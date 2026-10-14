#ifndef R03_BOUNDED_DIAGNOSTICS_FILES_H
#define R03_BOUNDED_DIAGNOSTICS_FILES_H
// POSIX two-file transaction over the existing V2 encoder. Inactive until the
// Player integration supplies a coherent capture and authenticated identity.
// Single owner; Prepare runs while healthy; Commit must run outside VM locks.
// Successful bytes/durability are NOT JSON semantic or producer acceptance.
#include "BoundedDiagnosticsV2.h"
#include <cerrno>
#include <cstdio>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace r03_diag_v2 {
constexpr size_t kPathBytes = 4096;
constexpr size_t kDirectoryDepth = 64;
constexpr unsigned kInterruptLimit = 8;
constexpr const char* kArtifactName = "diagnostics.v2.bin";
constexpr const char* kEnvelopeName = "raw.v2.json";

struct FileIdentity {
    uint64_t device=0, inode=0, owner=0, group=0;
    uint32_t mode=0;
    static FileIdentity From(const struct stat& st) noexcept {
        return {uint64_t(st.st_dev),uint64_t(st.st_ino),uint64_t(st.st_uid),
                uint64_t(st.st_gid),uint32_t(st.st_mode)};
    }
    bool Equals(const struct stat& st) const noexcept {
        return device==uint64_t(st.st_dev)&&inode==uint64_t(st.st_ino)&&
            owner==uint64_t(st.st_uid)&&group==uint64_t(st.st_gid)&&mode==uint32_t(st.st_mode);
    }
};
enum class FileStage : uint8_t { None, Prepare, ArtifactWrite, ArtifactCheck,
    ArtifactSync, DirectorySync, EnvelopeWrite, EnvelopeCheck, EnvelopeSync,
    FinalCheck, Close };
enum class FileError : uint8_t { None, Reused, Reentered, InvalidInput, Path,
    DirectoryChanged, FileChanged, Open, Io, Interrupted, ResourceLimit,
    Codec, ReceiptMismatch, Sync, Close, Incomplete };
struct FileFailure {
    FileError error=FileError::None;
    FileStage stage=FileStage::None;
    int systemError=0;
    size_t artifactBytes=0, envelopeBytes=0; // Known successful syscall bytes only.
};
struct FileReceipt {
    bool complete=false; // Only after both files and the directory were synced/closed.
    size_t artifactBytes=0, envelopeBytes=0;
    Digest artifactSha256{}, envelopeSha256{}, binding{}, inlineSha256{};
    FileIdentity directory{}, artifact{}, envelope{};
    int64_t processId=0;
    bool appleFullFileSync=false;
};

struct PosixFileOps {
    static int OpenRoot() noexcept { return ::open("/",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC); }
    static int OpenAt(int fd,const char* name,int flags,mode_t mode) noexcept { return ::openat(fd,name,flags,mode); }
    static int Stat(int fd,struct stat* out) noexcept { return ::fstat(fd,out); }
    static int StatAt(int fd,const char* name,struct stat* out) noexcept { return ::fstatat(fd,name,out,AT_SYMLINK_NOFOLLOW); }
    static ssize_t Write(int fd,const uint8_t* p,size_t n) noexcept { return ::write(fd,p,n); }
    static ssize_t ReadAt(int fd,uint8_t* p,size_t n,off_t at) noexcept { return ::pread(fd,p,n,at); }
    static int Sync(int fd) noexcept { return ::fsync(fd); }
    static int FullSync(int fd) noexcept {
#if defined(__APPLE__)
        return ::fcntl(fd,F_FULLFSYNC);
#else
        (void)fd; return 0;
#endif
    }
    static int Close(int fd) noexcept { return ::close(fd); }
    static uid_t Owner() noexcept { return ::geteuid(); }
    static pid_t Process() noexcept { return ::getpid(); }
};

// Trusted canonicalInline must be the complete canonical JSON object used by
// the V2 reference (excluding diagnosticArtifact). The upstream serializer and
// host verifier validate its JSON/schema. This component only bounds, hashes,
// copies and durably binds those bytes; it is not a JSON parser.
// The directory identity/binding must come from independently admitted inputs,
// not from an untrusted file header. No filenames are accepted from diagnostics.
template<class Ops=PosixFileOps>
class FileTransaction {
    struct Directory { int fd=-1; size_t nameOffset=0; FileIdentity identity{}; };
    Directory dirs_[kDirectoryDepth+1]{};
    size_t depth_=0;
    char path_[kPathBytes]{};
    int files_[2]={-1,-1};
    FileIdentity identities_[2]{};
    size_t sizes_[2]{};
    bool attempted_=false, prepared_=false, committed_=false, busy_=false;
    Digest binding_{};
    pid_t ownerProcess_=0;
    FileFailure first_{};
    FileStage stage_=FileStage::None;

    bool Fail(FileError error,int systemError=0) noexcept {
        if(first_.error==FileError::None)
            first_={error,stage_,systemError,sizes_[0],sizes_[1]};
        return false;
    }
    bool Ok() const noexcept { return first_.error==FileError::None; }
    struct Busy {
        bool& value;
        explicit Busy(bool& v) noexcept:value(v){value=true;}
        ~Busy(){value=false;}
    };
    bool CheckProcess() noexcept { return Ops::Process()==ownerProcess_ || Fail(FileError::InvalidInput); }
    bool CheckDirectories() noexcept {
        for(size_t i=0;i<=depth_;++i) {
            struct stat st{};
            if(dirs_[i].fd<0 || Ops::Stat(dirs_[i].fd,&st)!=0)
                return Fail(FileError::DirectoryChanged,errno);
            if(!dirs_[i].identity.Equals(st)||!S_ISDIR(st.st_mode)) return Fail(FileError::DirectoryChanged);
            if(i) {
                if(Ops::StatAt(dirs_[i-1].fd,path_+dirs_[i].nameOffset,&st)!=0)
                    return Fail(FileError::DirectoryChanged,errno);
                if(!dirs_[i].identity.Equals(st)||!S_ISDIR(st.st_mode)) return Fail(FileError::DirectoryChanged);
            }
            if(!Ok())return false;
        }
        return true;
    }
    bool CheckFile(unsigned index,size_t bytes) noexcept {
        struct stat st{},named{};
        if(files_[index]<0 || Ops::Stat(files_[index],&st)!=0)
            return Fail(FileError::FileChanged,errno);
        if(!identities_[index].Equals(st)||!S_ISREG(st.st_mode)||st.st_nlink!=1||
           st.st_size<0 || uint64_t(st.st_size)!=bytes) return Fail(FileError::FileChanged);
        if(Ops::StatAt(dirs_[depth_].fd,index?kEnvelopeName:kArtifactName,&named)!=0)
            return Fail(FileError::FileChanged,errno);
        if(!identities_[index].Equals(named)||!S_ISREG(named.st_mode)||named.st_nlink!=1||
           named.st_size!=st.st_size)return Fail(FileError::FileChanged);
        return Ok();
    }
    bool CheckAll() noexcept {
        return CheckProcess()&&CheckDirectories()&&CheckFile(0,sizes_[0])&&CheckFile(1,sizes_[1]);
    }
    bool WriteAll(unsigned index,const uint8_t* data,size_t bytes) noexcept {
        const size_t bound=index?kEnvelopeReserve:kArtifactMax;
        if(!Ok())return false;
        if((!data&&bytes)||sizes_[index]>bound||bytes>bound-sizes_[index])return Fail(FileError::ResourceLimit);
        unsigned interrupts=0;
        while(bytes) {
            const size_t request=bytes>kFrame?kFrame:bytes;
            const ssize_t actual=Ops::Write(files_[index],data,request);
            const int error=errno;
            if(!Ok())return false; // A test/adapter callback re-entered the transaction.
            if(actual<0) {
                if(error==EINTR && ++interrupts<=kInterruptLimit)continue;
                return Fail(error==EINTR?FileError::Interrupted:FileError::Io,error);
            }
            if(actual==0 || size_t(actual)>request)return Fail(FileError::Io);
            data+=actual;bytes-=size_t(actual);sizes_[index]+=size_t(actual);
        }
        return true;
    }
    static bool Sink(void* owner,const uint8_t* p,size_t n) noexcept {
        return static_cast<FileTransaction*>(owner)->WriteAll(0,p,n);
    }
    bool HashFile(unsigned index,const Digest& expected,uint8_t* scratch) noexcept {
        if(!CheckFile(index,sizes_[index]))return false;
        Sha256 hash;size_t offset=0;unsigned interrupts=0;
        while(offset<sizes_[index]) {
            size_t n=sizes_[index]-offset;if(n>kFrame)n=kFrame;
            const ssize_t actual=Ops::ReadAt(files_[index],scratch,n,off_t(offset));
            const int error=errno;
            if(!Ok())return false;
            if(actual<0) {
                if(error==EINTR && ++interrupts<=kInterruptLimit)continue;
                return Fail(error==EINTR?FileError::Interrupted:FileError::Io,error);
            }
            if(actual==0 || size_t(actual)>n)return Fail(FileError::Io);
            hash.Update(scratch,size_t(actual));offset+=size_t(actual);
        }
        if(hash.Finish()!=expected)return Fail(FileError::ReceiptMismatch);
        return CheckFile(index,sizes_[index]);
    }
    bool SyncFile(unsigned index) noexcept {
        if(Ops::Sync(files_[index])!=0)return Fail(FileError::Sync,errno);
        if(!Ok())return false;
        // On Apple, fsync alone does not request the device write-cache flush.
        // No fallback: unsupported F_FULLFSYNC means no durability success.
        if(Ops::FullSync(files_[index])!=0)return Fail(FileError::Sync,errno);
        return Ok();
    }
    bool SyncDirectory() noexcept {
        stage_=FileStage::DirectorySync;
        if(Ops::Sync(dirs_[depth_].fd)!=0)return Fail(FileError::Sync,errno);
        return Ok();
    }
    static void Hex(const Digest& d,char (&out)[65]) noexcept {
        static constexpr char hex[]="0123456789abcdef";
        for(size_t i=0;i<32;++i){out[2*i]=hex[d[i]>>4];out[2*i+1]=hex[d[i]&15];}
        out[64]=0;
    }
    void CloseAll() noexcept {
        stage_=FileStage::Close;
        // Never retry a failed close: EINTR descriptor state is platform-specific.
        for(unsigned i=0;i<2;++i)if(files_[i]>=0) {
            int fd=files_[i];files_[i]=-1;
            if(Ops::Close(fd)!=0)Fail(FileError::Close,errno);
        }
        for(size_t n=depth_+1;n;--n)if(dirs_[n-1].fd>=0) {
            int fd=dirs_[n-1].fd;dirs_[n-1].fd=-1;
            if(Ops::Close(fd)!=0)Fail(FileError::Close,errno);
        }
    }
public:
    FileTransaction() noexcept=default;
    FileTransaction(const FileTransaction&)=delete;
    FileTransaction& operator=(const FileTransaction&)=delete;
    ~FileTransaction(){CloseAll();} // Abandoned outputs are retained, never unlinked.
    FileFailure failure() const noexcept{return first_;}
    bool Prepare(const char* absoluteDirectory,FileIdentity expectedDirectory,Digest binding) noexcept {
        if(busy_)return Fail(FileError::Reentered);
        Busy scope(busy_);stage_=FileStage::Prepare;
        if(attempted_)return Fail(FileError::Reused);
        if(!Ok())return false;
        attempted_=true;
        if(!absoluteDirectory)return Fail(FileError::InvalidInput);
        const size_t n=::strnlen(absoluteDirectory,kPathBytes);
        if(n<2||n>=kPathBytes||absoluteDirectory[0]!='/'||absoluteDirectory[n-1]=='/')return Fail(FileError::Path);
        std::memcpy(path_,absoluteDirectory,n+1);
        ownerProcess_=Ops::Process();binding_=binding;
        dirs_[0].fd=Ops::OpenRoot();
        if(dirs_[0].fd<0)return Fail(FileError::Open,errno);
        struct stat st{};
        if(Ops::Stat(dirs_[0].fd,&st)!=0||!S_ISDIR(st.st_mode))return Fail(FileError::Path,errno);
        dirs_[0].identity=FileIdentity::From(st);
        size_t at=1;
        while(at<n) {
            const size_t first=at;
            while(at<n && path_[at]!='/')++at;
            const size_t bytes=at-first;
            if(!bytes||bytes>255||depth_==kDirectoryDepth||
               (bytes==1&&path_[first]=='.')||(bytes==2&&path_[first]=='.'&&path_[first+1]=='.'))return Fail(FileError::Path);
            path_[at]=0;
            int fd=Ops::OpenAt(dirs_[depth_].fd,path_+first,O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC,0);
            if(fd<0)return Fail(FileError::Open,errno);
            ++depth_;dirs_[depth_].fd=fd;dirs_[depth_].nameOffset=first;
            if(Ops::Stat(fd,&st)!=0||!S_ISDIR(st.st_mode))return Fail(FileError::Path,errno);
            dirs_[depth_].identity=FileIdentity::From(st);++at;
        }
        if(!expectedDirectory.Equals(st)||st.st_uid!=Ops::Owner()||(st.st_mode&0022)!=0)
            return Fail(FileError::DirectoryChanged);
        if(!CheckDirectories())return false;
        for(unsigned i=0;i<2;++i) {
            files_[i]=Ops::OpenAt(dirs_[depth_].fd,i?kEnvelopeName:kArtifactName,
                O_RDWR|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
            if(files_[i]<0)return Fail(FileError::Open,errno);
            if(Ops::Stat(files_[i],&st)!=0)return Fail(FileError::FileChanged,errno);
            if(!S_ISREG(st.st_mode)||st.st_nlink!=1||st.st_uid!=Ops::Owner()||
               (st.st_mode&0777)!=0600||st.st_size!=0)return Fail(FileError::FileChanged);
            identities_[i]=FileIdentity::From(st);
        }
        if(!CheckAll())return false;
        prepared_=true;return true;
    }
    bool Commit(const uint8_t* canonicalInline,size_t inlineBytes,const FieldView (&fields)[2],
                uint8_t* scratch,size_t scratchBytes,FileReceipt& receipt) noexcept {
        receipt=FileReceipt{};
        if(busy_)return Fail(FileError::Reentered);
        Busy scope(busy_);stage_=FileStage::ArtifactWrite;
        if(committed_)return Fail(FileError::Reused);
        committed_=true;
        if(!prepared_||!Ok())return Fail(FileError::Incomplete);
        prepared_=false;
        if(!canonicalInline||inlineBytes<2||inlineBytes>kInlineLimit||
           canonicalInline[0]!='{'||canonicalInline[inlineBytes-1]!='}'||
           !ValidUtf8(canonicalInline,inlineBytes)||!scratch||scratchBytes<kFrame)
            return Fail(FileError::InvalidInput);
        const uintptr_t ib=reinterpret_cast<uintptr_t>(canonicalInline),sb=reinterpret_cast<uintptr_t>(scratch);
        if(ib>UINTPTR_MAX-inlineBytes||sb>UINTPTR_MAX-kFrame||
           (ib<sb+kFrame && sb<ib+inlineBytes))return Fail(FileError::InvalidInput);
        if(!CheckAll())return false;
        const Digest inlineHash=Sha256::Of(canonicalInline,inlineBytes);
        Encoder codec;Receipt encoded;
        if(!codec.Encode(binding_,inlineHash,inlineBytes,fields,scratch,scratchBytes,Sink,this,encoded))
            return Fail(FileError::Codec);
        if(!encoded.complete||encoded.bytes!=sizes_[0])return Fail(FileError::ReceiptMismatch);
        stage_=FileStage::ArtifactCheck;
        if(!HashFile(0,encoded.sha256,scratch)||!CheckAll())return false;
        stage_=FileStage::ArtifactSync;
        if(!SyncFile(0)||!SyncDirectory()||!CheckAll())return false;
        if(Sha256::Of(canonicalInline,inlineBytes)!=inlineHash)return Fail(FileError::ReceiptMismatch);
        char context[65],ih[65],ah[65];Hex(binding_,context);Hex(inlineHash,ih);Hex(encoded.sha256,ah);
        char prefix[512];
        const int prefixBytes=std::snprintf(prefix,sizeof prefix,
            "{\"diagnosticArtifact\":{\"binding\":\"%s\",\"bytes\":%zu,\"inlineSha256\":\"%s\","
            "\"kind\":\"R03BoundedDiagnosticsV2\",\"sha256\":\"%s\"}%s",
            context,encoded.bytes,ih,ah,inlineBytes==2?"}":",");
        if(prefixBytes<=0||size_t(prefixBytes)>=sizeof prefix)return Fail(FileError::InvalidInput);
        const size_t tail=inlineBytes==2?0:inlineBytes-1;
        if(size_t(prefixBytes)+tail>kEnvelopeReserve||encoded.bytes+size_t(prefixBytes)+tail>kTotal)
            return Fail(FileError::ResourceLimit);
        Sha256 envelopeHash;envelopeHash.Update(reinterpret_cast<const uint8_t*>(prefix),size_t(prefixBytes));
        if(tail)envelopeHash.Update(canonicalInline+1,tail);
        stage_=FileStage::EnvelopeWrite;
        if(!WriteAll(1,reinterpret_cast<const uint8_t*>(prefix),size_t(prefixBytes))||
           (tail&&!WriteAll(1,canonicalInline+1,tail)))return false;
        stage_=FileStage::EnvelopeCheck;
        if(!HashFile(1,envelopeHash.Finish(),scratch))return false;
        stage_=FileStage::EnvelopeSync;
        if(!SyncFile(1)||!SyncDirectory())return false;
        stage_=FileStage::FinalCheck;
        if(!CheckAll()||!HashFile(0,encoded.sha256,scratch)||
           !HashFile(1,envelopeHash.Finish(),scratch)||
           Sha256::Of(canonicalInline,inlineBytes)!=inlineHash)return Fail(FileError::ReceiptMismatch);
        if(!CheckAll())return false;
        FileReceipt result;
        result.artifactBytes=sizes_[0];result.envelopeBytes=sizes_[1];
        result.artifactSha256=encoded.sha256;result.envelopeSha256=envelopeHash.Finish();
        result.binding=binding_;result.inlineSha256=inlineHash;
        result.directory=dirs_[depth_].identity;result.artifact=identities_[0];result.envelope=identities_[1];
        result.processId=int64_t(ownerProcess_);
#if defined(__APPLE__)
        result.appleFullFileSync=true;
#endif
        CloseAll();
        if(!Ok())return false;
        result.complete=true;receipt=result;return true;
    }
};
} // namespace r03_diag_v2
#endif
