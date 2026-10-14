#ifndef R03_BOUNDED_FILE_TRANSACTION_V2_H
#define R03_BOUNDED_FILE_TRANSACTION_V2_H
// Inactive POSIX component: no VM capture, Player dispatch or engine control.
// One owner; all input spans must remain immutable and disjoint from scratch.
// Directory identity and run context must be authenticated BEFORE Arm.
#include "BoundedDiagnosticsV2.h"
#include <cerrno>
#include <cstdio>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace r03_diag_v2 { namespace files {
constexpr const char* kArtifactName = "diagnostics.v2.bin";
constexpr const char* kEnvelopeName = "raw.json";
constexpr size_t kPathBytes = 1024;
enum class Target : uint8_t { Directory, Artifact, Envelope };
enum class Stage : uint8_t { Arm, Create, Encode, Write, Verify, Sync, Close, Publish };
enum class FileError : uint8_t { None, Reused, Reentered, Input, Path, Identity, Open, Encode, Io, Limit };
struct FileIdentity { uint64_t device=0, inode=0; uint32_t owner=0, mode=0; };
inline FileIdentity Identity(const struct stat& s) noexcept {
    return {uint64_t(s.st_dev),uint64_t(s.st_ino),uint32_t(s.st_uid),uint32_t(s.st_mode & 07777)};
}
inline bool Same(FileIdentity a, FileIdentity b) noexcept {
    return a.device==b.device && a.inode==b.inode && a.owner==b.owner && a.mode==b.mode;
}
struct FirstFailure {
    FileError error=FileError::None; Stage stage=Stage::Arm; Target target=Target::Directory;
    int systemError=0; size_t artifactWritten=0, envelopeWritten=0;
};
struct Publication {
    bool complete=false; // Successful checked syscalls, NOT semantic acceptance or a power-loss test.
    Receipt artifact{}, envelope{}; FileIdentity directory{}, artifactFile{}, envelopeFile{};
    Digest context{}, inlineHash{};
};
// Optional TEST seam. Returning false injects EIO; it never changes actual
// production syscall flags. The callback may not retain spans or mutate inputs.
using Gate = bool (*)(void*,Stage,Target) noexcept;
// Optional test syscall seam; production defaults to the real write syscall.
using WriteCall = ssize_t (*)(void*,int,const uint8_t*,size_t) noexcept;
class Transaction {
    char root_[kPathBytes]{};
    int dir_=-1, artifact_=-1, envelope_=-1;
    unsigned state_=0; // 0 new, 1 armed, 2 finished (success or failure).
    bool busy_=false;
    FileIdentity directoryId_{}, artifactId_{}, envelopeId_{};
    Digest context_{};
    FirstFailure first_{};
    Gate gate_=nullptr; void* gateContext_=nullptr;
    WriteCall writer_=nullptr; void* writerContext_=nullptr;
    size_t written_[2]{};
    bool Fail(FileError error,Stage stage,Target target,int systemError=0) noexcept {
        if(first_.error==FileError::None)
            first_={error,stage,target,systemError,written_[0],written_[1]};
        return false;
    }
    bool Allow(Stage stage,Target target) noexcept {
        if(first_.error!=FileError::None)return false;
        if(gate_ && !gate_(gateContext_,stage,target))return Fail(FileError::Io,stage,target,EIO);
        return first_.error==FileError::None;
    }
    static int Walk(const char* path) noexcept {
        if(!path || path[0]!='/' || !path[1]){errno=EINVAL;return -1;}
        const size_t bytes=strnlen(path,kPathBytes);
        if(bytes==kPathBytes || path[bytes-1]=='/'){errno=EINVAL;return -1;}
        int current=::open("/",O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW);
        if(current<0)return -1;
        size_t position=1;
        while(position<bytes){
            size_t end=position;while(end<bytes && path[end]!='/')++end;
            const size_t n=end-position;
            if(!n || n>255 || (n==1 && path[position]=='.') ||
               (n==2 && path[position]=='.' && path[position+1]=='.')){
                ::close(current);errno=EINVAL;return -1;
            }
            char part[256]{};std::memcpy(part,path+position,n);
            int next=::openat(current,part,O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW);
            const int openError=errno;
            const int closeResult=::close(current); // Never retry close on a reused descriptor.
            if(next<0){errno=openError;return -1;}
            if(closeResult!=0){const int saved=errno;::close(next);errno=saved;return -1;}
            current=next;position=end+1;
        }
        return current;
    }
    bool CheckRoot(Stage stage) noexcept {
        if(!Allow(stage,Target::Directory))return false;
        struct stat retained{}, named{};
        if(::fstat(dir_,&retained)!=0)return Fail(FileError::Io,stage,Target::Directory,errno);
        const int fd=Walk(root_);
        if(fd<0)return Fail(FileError::Path,stage,Target::Directory,errno);
        const int r=::fstat(fd,&named);const int e=errno;const int c=::close(fd);
        if(r!=0 || c!=0)return Fail(FileError::Io,stage,Target::Directory,r!=0?e:errno);
        if(!S_ISDIR(retained.st_mode) || !Same(Identity(retained),directoryId_) ||
           !Same(Identity(named),directoryId_))return Fail(FileError::Identity,stage,Target::Directory);
        return true;
    }
    bool CheckFile(int fd,const char* name,FileIdentity id,size_t expected,Target target) noexcept {
        if(!Allow(Stage::Verify,target))return false;
        struct stat held{},named{};
        if(::fstat(fd,&held)!=0 || ::fstatat(dir_,name,&named,AT_SYMLINK_NOFOLLOW)!=0)
            return Fail(FileError::Io,Stage::Verify,target,errno);
        if(!S_ISREG(held.st_mode) || !S_ISREG(named.st_mode) || held.st_nlink!=1 || named.st_nlink!=1 ||
           held.st_uid!=::geteuid() || (held.st_mode&07777)!=0600 ||
           !Same(Identity(held),id) || !Same(Identity(named),id) ||
           held.st_size<0 || uint64_t(held.st_size)!=expected || named.st_size!=held.st_size)
            return Fail(FileError::Identity,Stage::Verify,target);
        return true;
    }
    bool WriteAll(int fd,const uint8_t* p,size_t n,Target target) noexcept {
        const unsigned index=target==Target::Artifact?0:1;
        const size_t limit=index==0?kArtifactMax:kEnvelopeReserve;
        if(!p && n)return Fail(FileError::Input,Stage::Write,target);
        if(n>limit-written_[index])return Fail(FileError::Limit,Stage::Write,target);
        unsigned interrupted=0;
        while(n){
            if(!Allow(Stage::Write,target))return false;
            const ssize_t actual=writer_?writer_(writerContext_,fd,p,n) : ::write(fd,p,n);
            if(actual<0){if(errno==EINTR && ++interrupted<=8)continue;
                return Fail(FileError::Io,Stage::Write,target,errno);}
            if(actual==0)return Fail(FileError::Io,Stage::Write,target,EIO);
            const size_t consumed=static_cast<size_t>(actual);
            if(consumed>n)return Fail(FileError::Io,Stage::Write,target,EIO);
            written_[index]+=consumed;p+=consumed;n-=consumed;
            if(first_.error!=FileError::None)return false;
        }
        return first_.error==FileError::None;
    }
    static bool ArtifactSink(void* self,const uint8_t* p,size_t n) noexcept {
        auto& tx=*static_cast<Transaction*>(self);
        return tx.WriteAll(tx.artifact_,p,n,Target::Artifact);
    }
    bool Readback(int fd,size_t bytes,Digest expected,uint8_t* scratch,Target target) noexcept {
        if(!Allow(Stage::Verify,target))return false;
        Sha256 hash;size_t at=0;unsigned interrupted=0;
        while(at<bytes){
            const size_t want=(bytes-at>kFrame)?kFrame:bytes-at;
            const ssize_t n=::pread(fd,scratch,want,static_cast<off_t>(at));
            if(n<0){if(errno==EINTR && ++interrupted<=8)continue;
                return Fail(FileError::Io,Stage::Verify,target,errno);}
            if(n==0)return Fail(FileError::Io,Stage::Verify,target,EIO);
            hash.Update(scratch,static_cast<size_t>(n));at+=static_cast<size_t>(n);
        }
        if(hash.Finish()!=expected)return Fail(FileError::Identity,Stage::Verify,target);
        return true;
    }
    bool Sync(int fd,Target target) noexcept {
        if(!Allow(Stage::Sync,target))return false;
        int result;
#if defined(__APPLE__)
        // No silent fallback to weaker file synchronization on Apple.
        result=target==Target::Directory?::fsync(fd) : ::fcntl(fd,F_FULLFSYNC,0);
#else
        result=::fsync(fd);
#endif
        return result==0 || Fail(FileError::Io,Stage::Sync,target,errno);
    }
    bool Close(int& fd,Target target) noexcept {
        const bool allowed=Allow(Stage::Close,target);
        const int owned=fd;fd=-1;
        const int r=::close(owned); // Close ONCE even if a test injects a close error.
        if(r!=0)return Fail(FileError::Io,Stage::Close,target,errno);
        return allowed;
    }
    bool Create(int& fd,const char* name,FileIdentity& id,Target target) noexcept {
        if(!Allow(Stage::Create,target))return false;
        fd=::openat(dir_,name,O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC|O_RDWR,0600);
        if(fd<0)return Fail(FileError::Open,Stage::Create,target,errno);
        struct stat s{};
        if(::fstat(fd,&s)!=0)return Fail(FileError::Io,Stage::Create,target,errno);
        id=Identity(s);return CheckFile(fd,name,id,0,target);
    }
    static void Hex(Digest value,char (&out)[65]) noexcept {
        constexpr char h[]="0123456789abcdef";
        for(size_t i=0;i<32;++i){out[2*i]=h[value[i]>>4];out[2*i+1]=h[value[i]&15];}
        out[64]=0;
    }
public:
    explicit Transaction(Gate gate=nullptr,void* user=nullptr,WriteCall writer=nullptr,void* writerUser=nullptr) noexcept
        : gate_(gate),gateContext_(user),writer_(writer),writerContext_(writerUser) {}
    Transaction(const Transaction&)=delete;Transaction& operator=(const Transaction&)=delete;
    ~Transaction(){if(artifact_>=0)::close(artifact_);if(envelope_>=0)::close(envelope_);if(dir_>=0)::close(dir_);}
    FirstFailure failure() const noexcept {return first_;}
    bool Arm(const char* canonicalRoot,FileIdentity expectedDirectory,Digest authenticatedContext) noexcept {
        if(busy_)return Fail(FileError::Reentered,Stage::Arm,Target::Directory);
        if(state_!=0 || first_.error!=FileError::None)return Fail(FileError::Reused,Stage::Arm,Target::Directory);
        state_=2;busy_=true;
        const size_t n=canonicalRoot?strnlen(canonicalRoot,kPathBytes):kPathBytes;
        if(n==kPathBytes){busy_=false;return Fail(FileError::Input,Stage::Arm,Target::Directory);}
        std::memcpy(root_,canonicalRoot,n+1);context_=authenticatedContext;directoryId_=expectedDirectory;
        dir_=Walk(root_);
        if(dir_<0){busy_=false;return Fail(FileError::Path,Stage::Arm,Target::Directory,errno);}
        struct stat d{};const int r=::fstat(dir_,&d);
        bool ok=r==0;
        if(!ok)Fail(FileError::Io,Stage::Arm,Target::Directory,errno);
        else if(!S_ISDIR(d.st_mode) || d.st_uid!=::geteuid() || (d.st_mode&0022) || !Same(Identity(d),directoryId_))
            ok=Fail(FileError::Identity,Stage::Arm,Target::Directory);
        if(ok)ok=CheckRoot(Stage::Arm) && Create(artifact_,kArtifactName,artifactId_,Target::Artifact) &&
                  Create(envelope_,kEnvelopeName,envelopeId_,Target::Envelope) && CheckRoot(Stage::Arm);
        busy_=false;if(ok)state_=1;return ok;
    }
    bool Seal(const uint8_t* inlineJson,size_t inlineBytes,const FieldView (&fields)[2],
              uint8_t* scratch,size_t scratchBytes,Publication& out) noexcept {
        out=Publication{};
        if(busy_)return Fail(FileError::Reentered,Stage::Publish,Target::Envelope);
        if(state_!=1 || first_.error!=FileError::None)return Fail(FileError::Reused,Stage::Publish,Target::Envelope);
        state_=2;busy_=true;
        bool ok=inlineJson && inlineBytes>=2 && inlineBytes<=kInlineLimit &&
            inlineJson[0]=='{' && inlineJson[inlineBytes-1]=='}' &&
            scratch && scratchBytes>=kFrame && ValidUtf8(inlineJson,inlineBytes);
        const uintptr_t p=reinterpret_cast<uintptr_t>(inlineJson),s=reinterpret_cast<uintptr_t>(scratch);
        ok=ok && p<=UINTPTR_MAX-inlineBytes && s<=UINTPTR_MAX-kFrame &&
           !(p<s+kFrame && s<p+inlineBytes);
        if(!ok){busy_=false;return Fail(FileError::Input,Stage::Encode,Target::Envelope);}
        const Digest inlineHash=Sha256::Of(inlineJson,inlineBytes);
        Receipt artifact;Encoder encoder;
        ok=CheckRoot(Stage::Verify) && CheckFile(artifact_,kArtifactName,artifactId_,0,Target::Artifact) &&
            CheckFile(envelope_,kEnvelopeName,envelopeId_,0,Target::Envelope) && Allow(Stage::Encode,Target::Artifact);
        if(ok){ok=encoder.Encode(context_,inlineHash,inlineBytes,fields,scratch,scratchBytes,ArtifactSink,this,artifact);
            if(!ok)Fail(FileError::Encode,Stage::Encode,Target::Artifact);}
        if(ok)ok=CheckFile(artifact_,kArtifactName,artifactId_,artifact.bytes,Target::Artifact) &&
                  Readback(artifact_,artifact.bytes,artifact.sha256,scratch,Target::Artifact) &&
                  Sync(artifact_,Target::Artifact) && Close(artifact_,Target::Artifact) && Sync(dir_,Target::Directory);
        char hash[65]{},context[65]{},ih[65]{};Hex(artifact.sha256,hash);Hex(context_,context);Hex(inlineHash,ih);
        char prefix[512]{};
        const int n=std::snprintf(prefix,sizeof prefix,
            "{\"diagnosticArtifact\":{\"kind\":\"R03BoundedDiagnosticsV2\",\"bytes\":%zu,\"sha256\":\"%s\",\"binding\":\"%s\",\"inlineSha256\":\"%s\"}%s",
            artifact.bytes,hash,context,ih,inlineBytes==2?"":",");
        const size_t tail=inlineBytes-1;
        if(ok && (n<=0 || size_t(n)>=sizeof prefix || size_t(n)+tail>kEnvelopeReserve))
            ok=Fail(FileError::Limit,Stage::Write,Target::Envelope);
        Sha256 envelopeHash;
        if(ok && Sha256::Of(inlineJson,inlineBytes)!=inlineHash)ok=Fail(FileError::Identity,Stage::Write,Target::Envelope);
        if(ok){envelopeHash.Update(reinterpret_cast<const uint8_t*>(prefix),size_t(n));
            envelopeHash.Update(inlineJson+1,tail);
            ok=CheckRoot(Stage::Verify) && CheckFile(envelope_,kEnvelopeName,envelopeId_,0,Target::Envelope) &&
                WriteAll(envelope_,reinterpret_cast<const uint8_t*>(prefix),size_t(n),Target::Envelope) &&
                WriteAll(envelope_,inlineJson+1,tail,Target::Envelope);}
        const size_t envelopeBytes=written_[1];
        if(ok)ok=CheckFile(envelope_,kEnvelopeName,envelopeId_,envelopeBytes,Target::Envelope) &&
                  Readback(envelope_,envelopeBytes,envelopeHash.Finish(),scratch,Target::Envelope) &&
                  Sync(envelope_,Target::Envelope) && Close(envelope_,Target::Envelope) && Sync(dir_,Target::Directory) &&
                  CheckRoot(Stage::Publish);
        // After closing data FDs, verify their original named identities/sizes
        // once more through the retained directory; never reopen for writing.
        if(ok){struct stat a{},e{};
            if(::fstatat(dir_,kArtifactName,&a,AT_SYMLINK_NOFOLLOW)!=0 ||
               ::fstatat(dir_,kEnvelopeName,&e,AT_SYMLINK_NOFOLLOW)!=0)
                ok=Fail(FileError::Io,Stage::Publish,Target::Directory,errno);
            else if(!Same(Identity(a),artifactId_) || !Same(Identity(e),envelopeId_) ||
                    a.st_nlink!=1 || e.st_nlink!=1 || uint64_t(a.st_size)!=artifact.bytes ||
                    uint64_t(e.st_size)!=envelopeBytes || !S_ISREG(a.st_mode) || !S_ISREG(e.st_mode))
                ok=Fail(FileError::Identity,Stage::Publish,Target::Directory);
        }
        if(ok)ok=Close(dir_,Target::Directory);
        busy_=false;
        if(!ok || first_.error!=FileError::None)return false;
        out.complete=true;out.artifact=artifact;out.envelope={envelopeBytes,envelopeHash.Finish(),true};
        out.context=context_;out.inlineHash=inlineHash;out.directory=directoryId_;
        out.artifactFile=artifactId_;out.envelopeFile=envelopeId_;return true;
    }
};
}} // r03_diag_v2::files
#endif
