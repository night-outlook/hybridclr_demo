#ifndef R03_POSIX_DIAGNOSTIC_TRANSACTION_H
#define R03_POSIX_DIAGNOSTIC_TRANSACTION_H
// Inactive integration component. Single owner; prearm before terminal state.
// Expected directory identity comes from independent healthy-time admission.
// Hashes and OS sync success do not assert semantic or hardware-power-loss proof.
#include "BoundedDiagnosticsV2.h"
#include <cerrno>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

namespace r03_diag_v2 {
struct PosixIO {
    int Open(const char* p,int flags) noexcept { return ::open(p,flags); }
    int OpenAt(int d,const char* p,int flags,mode_t mode) noexcept { return ::openat(d,p,flags,mode); }
    int Stat(int d,struct stat* s) noexcept { return ::fstat(d,s); }
    int StatAt(int d,const char* p,struct stat* s) noexcept { return ::fstatat(d,p,s,AT_SYMLINK_NOFOLLOW); }
    ssize_t Write(int d,const void* p,size_t n) noexcept { return ::write(d,p,n); }
    ssize_t ReadAt(int d,void* p,size_t n,off_t offset) noexcept { return ::pread(d,p,n,offset); }
    int SyncFile(int d) noexcept {
        if (::fsync(d)) return -1;
#if defined(__APPLE__)
        // No fallback: an unsupported full flush is a failed durability gate.
        return ::fcntl(d,F_FULLFSYNC);
#else
        return 0;
#endif
    }
    int SyncDirectory(int d) noexcept { return ::fsync(d); }
    int Close(int d) noexcept { return ::close(d); }
};
struct DirectoryIdentity { dev_t device; ino_t inode; uid_t owner; };
struct FileIdentity { dev_t device=0; ino_t inode=0; size_t bytes=0; Digest sha256{}; };
enum class TransactionError : uint8_t { None, State, Reentered, Path, DirectoryIdentity,
    Create, FileIdentity, Encode, Write, Readback, Sync, Close, Envelope, DirectorySync };
struct TransactionFailure { TransactionError error=TransactionError::None; int systemError=0; };
struct TransactionReceipt {
    bool complete=false;
    DirectoryIdentity directory{};
    FileIdentity artifact{},envelope{};
};

// Keeps original descriptors, rejects linked ancestors/entries and checks their
// identities before/after use. It cannot exclude a malicious same-UID writer:
// external command/source custody and re-authentication remain mandatory.
template<class IO=PosixIO> class PosixDiagnosticTransaction {
public:
    static constexpr const char* ArtifactName="diagnostics.r03v2";
    static constexpr const char* EnvelopeName="raw.json";
private:
    IO& io_;
    char root_[4096]{};
    DirectoryIdentity expected_{};
    FileIdentity artifact_{},envelope_{};
    int directory_=-1,artifactFd_=-1,envelopeFd_=-1;
    enum class State { Fresh, Armed, Writing, Complete, Failed } state_=State::Fresh;
    bool busy_=false;
    TransactionFailure failure_{};
    Sha256 artifactHash_,envelopeHash_;
    bool Fail(TransactionError code,int error=0) noexcept {
        if(failure_.error==TransactionError::None) failure_={code,error};
        state_=State::Failed;return false;
    }
    bool Close(int& descriptor) noexcept {
        if(descriptor<0)return true;
        const int d=descriptor;descriptor=-1; // Never retry close on an ambiguous error.
        if(io_.Close(d))return Fail(TransactionError::Close,errno);
        return true;
    }
    bool Owner(const struct stat& s) const noexcept {
        return S_ISDIR(s.st_mode)&&s.st_dev==expected_.device&&s.st_ino==expected_.inode&&
            s.st_uid==expected_.owner&&s.st_uid==::geteuid()&&s.st_nlink>0&&!(s.st_mode&0022);
    }
    int OpenRoot() noexcept {
        int d=io_.Open("/",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
        if(d<0){Fail(TransactionError::Path,errno);return -1;}
        size_t i=1;
        while(root_[i]) {
            char component[256]{};size_t n=0;
            while(root_[i]&&root_[i]!='/') {
                if(n==sizeof(component)-1){Fail(TransactionError::Path);Close(d);return -1;}
                component[n++]=root_[i++];
            }
            if(!n||(n==1&&component[0]=='.')||(n==2&&component[0]=='.'&&component[1]=='.')) {
                Fail(TransactionError::Path);Close(d);return -1;
            }
            if(root_[i]=='/'&&!root_[++i]){Fail(TransactionError::Path);Close(d);return -1;}
            const int next=io_.OpenAt(d,component,O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC,0);
            if(next<0){const int e=errno;Fail(TransactionError::Path,e);Close(d);return -1;}
            if(!Close(d)){int discard=next;Close(discard);return -1;} d=next;
        }
        struct stat s{};
        if(io_.Stat(d,&s)){const int e=errno;Fail(TransactionError::DirectoryIdentity,e);Close(d);return -1;}
        if(!Owner(s)){Fail(TransactionError::DirectoryIdentity);Close(d);return -1;}
        return d;
    }
    bool RootStillBound() noexcept {
        struct stat held{};
        if(io_.Stat(directory_,&held))return Fail(TransactionError::DirectoryIdentity,errno);
        if(!Owner(held))return Fail(TransactionError::DirectoryIdentity);
        int again=OpenRoot(); if(again<0)return false;
        return Close(again);
    }
    bool FileBound(int d,const char* name,const FileIdentity& expected,size_t bytes) noexcept {
        struct stat a{},b{};
        if(io_.StatAt(directory_,name,&b))return Fail(TransactionError::FileIdentity,errno);
        if(d>=0){if(io_.Stat(d,&a))return Fail(TransactionError::FileIdentity,errno);}
        else a=b;
        for(const struct stat* s:{&a,&b}) {
            if(!S_ISREG(s->st_mode)||s->st_dev!=expected.device||s->st_ino!=expected.inode||
               s->st_uid!=expected_.owner||s->st_nlink!=1||(s->st_mode&0777)!=0600||
               s->st_size<0||static_cast<uint64_t>(s->st_size)!=bytes)
                return Fail(TransactionError::FileIdentity);
        }
        return true;
    }
    bool Create(int& fd,const char* name,FileIdentity& identity) noexcept {
        fd=io_.OpenAt(directory_,name,O_RDWR|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
        if(fd<0)return Fail(TransactionError::Create,errno);
        struct stat s{};if(io_.Stat(fd,&s))return Fail(TransactionError::FileIdentity,errno);
        identity.device=s.st_dev;identity.inode=s.st_ino;
        return FileBound(fd,name,identity,0);
    }
    bool WriteAll(int fd,FileIdentity& file,Sha256& hash,const uint8_t* p,size_t n,size_t limit) noexcept {
        if(failure_.error!=TransactionError::None)return false;
        if((!p&&n)||file.bytes>limit||n>limit-file.bytes)return Fail(TransactionError::Write);
        while(n) {
            const ssize_t wrote=io_.Write(fd,p,n);
            if(wrote<=0||static_cast<size_t>(wrote)>n)return Fail(TransactionError::Write,wrote<0?errno:0);
            // A synchronous injected/reentrant operation may have invalidated us.
            if(failure_.error!=TransactionError::None)return false;
            hash.Update(p,static_cast<size_t>(wrote));file.bytes+=static_cast<size_t>(wrote);
            p+=wrote;n-=static_cast<size_t>(wrote);
        }
        return true;
    }
    static bool Sink(void* p,const uint8_t* bytes,size_t size) noexcept {
        auto& self=*static_cast<PosixDiagnosticTransaction*>(p);
        return self.WriteAll(self.artifactFd_,self.artifact_,self.artifactHash_,bytes,size,kArtifactMax);
    }
    bool Readback(int fd,const FileIdentity& file,uint8_t* scratch) noexcept {
        Sha256 hash;size_t offset=0;
        while(offset<file.bytes) {
            size_t n=file.bytes-offset;if(n>kFrame)n=kFrame;
            const ssize_t got=io_.ReadAt(fd,scratch,n,static_cast<off_t>(offset));
            if(got<=0||static_cast<size_t>(got)>n)return Fail(TransactionError::Readback,got<0?errno:0);
            hash.Update(scratch,static_cast<size_t>(got));offset+=static_cast<size_t>(got);
        }
        uint8_t extra=0;
        if(io_.ReadAt(fd,&extra,1,static_cast<off_t>(file.bytes))!=0)return Fail(TransactionError::Readback);
        return hash.Finish()==file.sha256||Fail(TransactionError::Readback);
    }
    bool Raw(const uint8_t* p,size_t n) noexcept {
        return WriteAll(envelopeFd_,envelope_,envelopeHash_,p,n,kEnvelopeReserve);
    }
    bool Literal(const char* p) noexcept {return Raw(reinterpret_cast<const uint8_t*>(p),std::strlen(p));}
    bool Hex(Digest digest) noexcept {
        static constexpr char hex[]="0123456789abcdef";uint8_t text[64]{};
        for(size_t i=0;i<32;++i){text[2*i]=uint8_t(hex[digest[i]>>4]);text[2*i+1]=uint8_t(hex[digest[i]&15]);}
        return Raw(text,sizeof(text));
    }
    bool Number(size_t n) noexcept {
        uint8_t text[32]{};size_t i=sizeof(text);
        do{text[--i]=uint8_t('0'+n%10);n/=10;}while(n);
        return Raw(text+i,sizeof(text)-i);
    }
public:
    explicit PosixDiagnosticTransaction(IO& io) noexcept:io_(io){}
    ~PosixDiagnosticTransaction(){Close(artifactFd_);Close(envelopeFd_);Close(directory_);}
    PosixDiagnosticTransaction(const PosixDiagnosticTransaction&)=delete;
    PosixDiagnosticTransaction& operator=(const PosixDiagnosticTransaction&)=delete;
    TransactionFailure failure() const noexcept {return failure_;}
    bool Arm(const char* absoluteRoot,DirectoryIdentity expected) noexcept {
        if(busy_)return Fail(TransactionError::Reentered);
        if(state_!=State::Fresh)return Fail(TransactionError::State);
        if(!absoluteRoot||absoluteRoot[0]!='/')return Fail(TransactionError::Path);
        size_t n=0;while(n<sizeof(root_)&&absoluteRoot[n])++n;
        if(n<2||n==sizeof(root_))return Fail(TransactionError::Path);
        std::memcpy(root_,absoluteRoot,n+1);expected_=expected;
        busy_=true;
        directory_=OpenRoot();
        bool ok=directory_>=0&&Create(artifactFd_,ArtifactName,artifact_)&&
            Create(envelopeFd_,EnvelopeName,envelope_)&&RootStillBound();
        if(ok&&io_.SyncDirectory(directory_))ok=Fail(TransactionError::DirectorySync,errno);
        busy_=false;if(ok&&failure_.error==TransactionError::None){state_=State::Armed;return true;}
        return false;
    }
    bool Commit(Digest binding,const uint8_t* inlineCanonical,size_t inlineBytes,
                const FieldView (&fields)[2],uint8_t* scratch,size_t scratchBytes,
                TransactionReceipt& receipt) noexcept {
        receipt=TransactionReceipt{};
        if(busy_)return Fail(TransactionError::Reentered);
        if(state_!=State::Armed)return Fail(TransactionError::State);
        if(!inlineCanonical||inlineBytes<2||inlineBytes>kInlineLimit||
            inlineCanonical[0]!='{'||inlineCanonical[inlineBytes-1]!='}'||
            !ValidUtf8(inlineCanonical,inlineBytes)||!scratch||scratchBytes<kFrame)
            return Fail(TransactionError::Envelope);
        // Caller-owned canonical envelope and field buffers must be immutable
        // and disjoint from scratch throughout encoding/readback/publication.
        const uintptr_t ib=reinterpret_cast<uintptr_t>(inlineCanonical),sb=reinterpret_cast<uintptr_t>(scratch);
        if(ib>UINTPTR_MAX-inlineBytes||sb>UINTPTR_MAX-kFrame||
            (ib<sb+kFrame&&sb<ib+inlineBytes))return Fail(TransactionError::Envelope);
        busy_=true;state_=State::Writing;
        const Digest inlineHash=Sha256::Of(inlineCanonical,inlineBytes);
        bool ok=RootStillBound()&&FileBound(artifactFd_,ArtifactName,artifact_,0)&&
            FileBound(envelopeFd_,EnvelopeName,envelope_,0);
        Encoder encoder;Receipt encoded;
        if(ok&&!encoder.Encode(binding,inlineHash,inlineBytes,fields,scratch,scratchBytes,&Sink,this,encoded))
            ok=Fail(TransactionError::Encode);
        artifact_.sha256=artifactHash_.Finish();
        if(ok&&(!encoded.complete||encoded.bytes!=artifact_.bytes||encoded.sha256!=artifact_.sha256))
            ok=Fail(TransactionError::Encode);
        if(ok)ok=Readback(artifactFd_,artifact_,scratch)&&FileBound(artifactFd_,ArtifactName,artifact_,artifact_.bytes);
        if(ok&&io_.SyncFile(artifactFd_))ok=Fail(TransactionError::Sync,errno);
        if(ok)ok=Close(artifactFd_);
        if(ok&&(Sha256::Of(inlineCanonical,inlineBytes)!=inlineHash))ok=Fail(TransactionError::Envelope);
        if(ok)ok=Raw(inlineCanonical,inlineBytes-1)&&
            (inlineBytes==2||Literal(","))&&Literal("\"diagnosticArtifact\":{\"kind\":\"R03BoundedDiagnosticsV2\",\"bytes\":")&&
            Number(artifact_.bytes)&&Literal(",\"sha256\":\"")&&Hex(artifact_.sha256)&&
            Literal("\",\"binding\":\"")&&Hex(binding)&&Literal("\",\"inlineSha256\":\"")&&Hex(inlineHash)&&Literal("\"}}");
        envelope_.sha256=envelopeHash_.Finish();
        if(ok)ok=Readback(envelopeFd_,envelope_,scratch)&&FileBound(envelopeFd_,EnvelopeName,envelope_,envelope_.bytes);
        if(ok&&io_.SyncFile(envelopeFd_))ok=Fail(TransactionError::Sync,errno);
        if(ok)ok=Close(envelopeFd_);
        if(ok)ok=RootStillBound()&&FileBound(-1,ArtifactName,artifact_,artifact_.bytes)&&
            FileBound(-1,EnvelopeName,envelope_,envelope_.bytes);
        if(ok&&io_.SyncDirectory(directory_))ok=Fail(TransactionError::DirectorySync,errno);
        if(ok)ok=Close(directory_);
        busy_=false;
        if(!ok||failure_.error!=TransactionError::None)return false;
        state_=State::Complete;receipt={true,expected_,artifact_,envelope_};return true;
    }
};
} // namespace r03_diag_v2
#endif
