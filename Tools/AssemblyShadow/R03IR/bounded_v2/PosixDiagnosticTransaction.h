#ifndef R03_POSIX_DIAGNOSTIC_TRANSACTION_H
#define R03_POSIX_DIAGNOSTIC_TRANSACTION_H
// Inactive POSIX file component. Single owner, healthy-time Prepare only.
// Does not collect VM state, parse the envelope, authorize a Player, or make
// two filesystem files atomically durable. An external authenticated successful
// receipt AND the exact envelope/artifact are mandatory for later consumption.
#include "BoundedDiagnosticsV2.h"
#include <cerrno>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

namespace r03_diag_v2 {
constexpr const char* kDiagnosticFile = "diagnostics.v2.bin";
constexpr const char* kEnvelopeFile = "envelope.v2.json";
constexpr size_t kPathBytes = 4096;
constexpr size_t kPathNodes = 64; // Includes '/'; all descriptors retained.
constexpr unsigned kInterruptedLimit = 16;

enum class FileError : uint8_t { None, State, Reentry, Path, Open, Identity,
    Resource, Write, Read, Content, Synchronize, Close };
enum class FileState : uint8_t { Fresh, Prepared, ArtifactDurable, Committed, Failed };
struct FileFailure { FileError error=FileError::None; const char* operation="none"; int systemError=0; };
struct FileIdentity { uint64_t device=0, inode=0, owner=0, mode=0, bytes=0; Digest sha256{}; };
struct TransactionReceipt {
    FileIdentity root{}, artifact{}, envelope{};
    bool complete=false;
    // This identifies the requested synchronization primitive, not power-loss
    // testing or a claim that the device honored the flush request.
    const char* syncPolicy=
#ifdef __APPLE__
        "F_FULLFSYNC-files+fsync-directory";
#else
        "fsync-files+fsync-directory";
#endif
};
struct PosixFileOps {
    static int OpenRoot() noexcept { return ::open("/", O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC); }
    static int OpenAt(int fd,const char* p,int flags,mode_t mode) noexcept { return ::openat(fd,p,flags,mode); }
    static int Stat(int fd,struct stat* s) noexcept { return ::fstat(fd,s); }
    static int StatAt(int fd,const char* p,struct stat* s) noexcept { return ::fstatat(fd,p,s,AT_SYMLINK_NOFOLLOW); }
    static ssize_t Write(int fd,const uint8_t* p,size_t n) noexcept { return ::write(fd,p,n); }
    static ssize_t ReadAt(int fd,uint8_t* p,size_t n,off_t off) noexcept { return ::pread(fd,p,n,off); }
    static int Sync(int fd,bool directory) noexcept {
#ifdef __APPLE__
        return directory ? ::fsync(fd) : ::fcntl(fd,F_FULLFSYNC,0);
#else
        (void)directory; return ::fsync(fd);
#endif
    }
    // No retry on close: the two target platforms may release the descriptor
    // on error. A repeated close could affect a reused, unrelated descriptor.
    static int Close(int fd) noexcept { return ::close(fd); }
};

template<class Ops=PosixFileOps>
class PosixDiagnosticTransaction {
    struct Node { int fd=-1; size_t name=0; struct stat original{}; };
    Node nodes_[kPathNodes]{}; size_t nodeCount_=0;
    char path_[kPathBytes]{};
    int artifact_=-1, envelope_=-1;
    struct stat artifactStat_{},envelopeStat_{};
    size_t artifactBytes_=0, envelopeBytes_=0;
    Sha256 artifactHash_{};
    FileFailure failure_{};
    FileState state_=FileState::Fresh;
    TransactionReceipt receipt_{};
    bool busy_=false;
    uint8_t readback_[4096]{};
    bool Fail(FileError error,const char* operation,int systemError=0) noexcept {
        if(failure_.error==FileError::None) failure_={error,operation,systemError};
        state_=FileState::Failed; receipt_.complete=false; return false;
    }
    struct Call {
        PosixDiagnosticTransaction& self; bool entered;
        explicit Call(PosixDiagnosticTransaction& x) noexcept : self(x),entered(!x.busy_) {
            if(entered) x.busy_=true; else x.Fail(FileError::Reentry,"reentry");
        }
        ~Call() { if(entered) self.busy_=false; }
    };
    static bool Same(const struct stat& a,const struct stat& b) noexcept {
        return a.st_dev==b.st_dev && a.st_ino==b.st_ino && a.st_uid==b.st_uid &&
            a.st_gid==b.st_gid && a.st_mode==b.st_mode;
    }
    static FileIdentity Identity(const struct stat& s,size_t bytes,Digest hash={}) noexcept {
        return {uint64_t(s.st_dev),uint64_t(s.st_ino),uint64_t(s.st_uid),
            uint64_t(s.st_mode & 07777),uint64_t(bytes),hash};
    }
    int Root() const noexcept { return nodes_[nodeCount_-1].fd; }
    bool Chain() noexcept {
        for(size_t i=0;i<nodeCount_;++i) {
            struct stat current{},named{};
            if(Ops::Stat(nodes_[i].fd,&current)) return Fail(FileError::Identity,"directory-fstat",errno);
            if(!Same(nodes_[i].original,current)||!S_ISDIR(current.st_mode)||current.st_nlink==0)
                return Fail(FileError::Identity,"directory-changed");
            if(i) {
                if(Ops::StatAt(nodes_[i-1].fd,path_+nodes_[i].name,&named))
                    return Fail(FileError::Identity,"ancestor-fstatat",errno);
                if(!Same(current,named)) return Fail(FileError::Identity,"ancestor-replaced");
            }
        }
        return failure_.error==FileError::None;
    }
    bool Named(const char* name,const struct stat& original,size_t bytes) noexcept {
        struct stat s{};
        if(Ops::StatAt(Root(),name,&s)) return Fail(FileError::Identity,"file-fstatat",errno);
        if(!Same(original,s)||!S_ISREG(s.st_mode)||s.st_nlink!=1||s.st_size<0||uint64_t(s.st_size)!=bytes)
            return Fail(FileError::Identity,"file-replaced-or-resized");
        return true;
    }
    bool Disk(int fd,const struct stat& original,size_t bytes,Digest expected) noexcept {
        struct stat before{},after{};
        if(Ops::Stat(fd,&before)) return Fail(FileError::Identity,"file-fstat",errno);
        if(!Same(original,before)||before.st_nlink!=1||before.st_size<0||uint64_t(before.st_size)!=bytes)
            return Fail(FileError::Identity,"open-file-changed");
        Sha256 hash; size_t offset=0; unsigned interrupted=0;
        while(offset<bytes) {
            const size_t n=bytes-offset<sizeof(readback_)?bytes-offset:sizeof(readback_);
            const ssize_t got=Ops::ReadAt(fd,readback_,n,static_cast<off_t>(offset));
            if(got<0 && errno==EINTR && interrupted++<kInterruptedLimit) continue;
            if(got<=0||static_cast<size_t>(got)>n) return Fail(FileError::Read,"readback",got<0?errno:0);
            if(failure_.error!=FileError::None) return false;
            interrupted=0; hash.Update(readback_,static_cast<size_t>(got)); offset+=static_cast<size_t>(got);
        }
        if(hash.Finish()!=expected) return Fail(FileError::Content,"readback-sha256");
        if(Ops::Stat(fd,&after)) return Fail(FileError::Identity,"file-fstat-after",errno);
        if(!Same(before,after)||after.st_nlink!=1||before.st_size!=after.st_size)
            return Fail(FileError::Identity,"file-changed-during-readback");
        return failure_.error==FileError::None;
    }
    bool WriteAll(int fd,const uint8_t* p,size_t n,size_t& count,Sha256& hash) noexcept {
        unsigned interrupted=0;
        while(n) {
            const ssize_t written=Ops::Write(fd,p,n);
            if(written<0 && errno==EINTR && interrupted++<kInterruptedLimit) continue;
            if(written<=0||static_cast<size_t>(written)>n) return Fail(FileError::Write,"write",written<0?errno:0);
            if(failure_.error!=FileError::None) return false;
            interrupted=0; const size_t done=static_cast<size_t>(written);
            hash.Update(p,done); count+=done; p+=done; n-=done;
        }
        return true;
    }
    bool Sync(int fd,bool dir,const char* operation) noexcept {
        // Interrupted or unsupported synchronization is Failed, no fallback.
        if(Ops::Sync(fd,dir)) return Fail(FileError::Synchronize,operation,errno);
        return failure_.error==FileError::None;
    }
    bool Close(int& fd) noexcept {
        const int owned=fd; fd=-1;
        if(owned>=0 && Ops::Close(owned)) return Fail(FileError::Close,"close-once",errno);
        return failure_.error==FileError::None;
    }
    bool NewFile(const char* name,int& fd,struct stat& identity) noexcept {
        fd=Ops::OpenAt(Root(),name,O_RDWR|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
        if(fd<0) return Fail(FileError::Open,"exclusive-file-open",errno);
        if(Ops::Stat(fd,&identity)) return Fail(FileError::Identity,"new-file-fstat",errno);
        if(!S_ISREG(identity.st_mode)||identity.st_nlink!=1||identity.st_size!=0||
            identity.st_uid!=::geteuid()||(identity.st_mode&07777)!=0600)
            return Fail(FileError::Identity,"new-file-mode-owner");
        return true;
    }
public:
    PosixDiagnosticTransaction() noexcept=default;
    PosixDiagnosticTransaction(const PosixDiagnosticTransaction&)=delete;
    PosixDiagnosticTransaction& operator=(const PosixDiagnosticTransaction&)=delete;
    ~PosixDiagnosticTransaction() {
        // Cleanup never unlinks or truncates outputs, and never retries closes.
        if(artifact_>=0) { const int fd=artifact_;artifact_=-1;Ops::Close(fd); }
        if(envelope_>=0) { const int fd=envelope_;envelope_=-1;Ops::Close(fd); }
        for(size_t i=nodeCount_;i>0;--i) if(nodes_[i-1].fd>=0) {
            const int fd=nodes_[i-1].fd;nodes_[i-1].fd=-1;Ops::Close(fd);
        }
    }
    FileFailure failure() const noexcept { return failure_; }
    FileState state() const noexcept { return state_; }
    TransactionReceipt receipt() const noexcept { return receipt_; }
    // Expected directory identity comes from independent healthy admission.
    // The component does not decide whether a root overlaps protected history.
    bool Prepare(const char* absolute,uint64_t expectedDevice,uint64_t expectedInode) noexcept {
        Call call(*this); if(!call.entered) return false;
        if(state_!=FileState::Fresh) return Fail(FileError::State,"prepare-once");
        if(!absolute) return Fail(FileError::Path,"null-path");
        size_t n=0;while(n<sizeof(path_) && absolute[n])++n;
        if(n<2||n==sizeof(path_)||absolute[0]!='/'||absolute[n-1]=='/') return Fail(FileError::Path,"canonical-path");
        std::memcpy(path_,absolute,n+1);
        // Validate all components before opening anything; never realpath away an alias.
        size_t starts[kPathNodes]{}; size_t parts=0,start=1;
        for(size_t i=1;i<=n;++i) if(path_[i]=='/'||!path_[i]) {
            const size_t size=i-start;
            if(!size||size>255||parts>=kPathNodes-1||(size==1&&path_[start]=='.')||
                (size==2&&path_[start]=='.'&&path_[start+1]=='.')) return Fail(FileError::Path,"path-component");
            starts[parts++]=start;path_[i]=0;start=i+1;
        }
        nodes_[0].fd=Ops::OpenRoot(); if(nodes_[0].fd<0) return Fail(FileError::Open,"root-open",errno);
        nodeCount_=1;
        if(Ops::Stat(nodes_[0].fd,&nodes_[0].original)) return Fail(FileError::Identity,"root-fstat",errno);
        for(size_t i=0;i<parts;++i) {
            Node& next=nodes_[nodeCount_];next.name=starts[i];
            next.fd=Ops::OpenAt(nodes_[nodeCount_-1].fd,path_+next.name,O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC,0);
            if(next.fd<0) return Fail(FileError::Open,"directory-open",errno);
            ++nodeCount_;
            if(Ops::Stat(next.fd,&next.original)) return Fail(FileError::Identity,"directory-fstat",errno);
        }
        const struct stat& root=nodes_[nodeCount_-1].original;
        if(!S_ISDIR(root.st_mode)||root.st_uid!=::geteuid()||(root.st_mode&07777)!=0700||
            uint64_t(root.st_dev)!=expectedDevice||uint64_t(root.st_ino)!=expectedInode)
            return Fail(FileError::Identity,"admitted-root");
        if(!Chain()||!NewFile(kDiagnosticFile,artifact_,artifactStat_)||!NewFile(kEnvelopeFile,envelope_,envelopeStat_)||
            !Chain()||!Sync(Root(),true,"prearm-directory-sync")) return false;
        receipt_.root=Identity(root,0);
        state_=FileState::Prepared;return true;
    }
    static bool ArtifactSink(void* context,const uint8_t* bytes,size_t n) noexcept {
        return context && static_cast<PosixDiagnosticTransaction*>(context)->AppendArtifact(bytes,n);
    }
    bool AppendArtifact(const uint8_t* bytes,size_t n) noexcept {
        Call call(*this); if(!call.entered) return false;
        if(state_!=FileState::Prepared) return Fail(FileError::State,"artifact-state");
        if((!bytes&&n)||n>kFrame||n>kArtifactMax-artifactBytes_) return Fail(FileError::Resource,"artifact-bound");
        return WriteAll(artifact_,bytes,n,artifactBytes_,artifactHash_);
    }
    bool FinishArtifact(const Receipt& expected) noexcept {
        Call call(*this); if(!call.entered) return false;
        if(state_!=FileState::Prepared) return Fail(FileError::State,"artifact-finish-state");
        if(!expected.complete||expected.bytes<192||expected.bytes!=artifactBytes_||expected.sha256!=artifactHash_.Finish())
            return Fail(FileError::Content,"encoder-receipt");
        if(!Chain()||!Named(kDiagnosticFile,artifactStat_,artifactBytes_)||
            !Disk(artifact_,artifactStat_,artifactBytes_,expected.sha256)||
            !Sync(artifact_,false,"artifact-sync")||!Close(artifact_)||
            !Named(kDiagnosticFile,artifactStat_,artifactBytes_)||!Sync(Root(),true,"artifact-directory-sync")) return false;
        receipt_.artifact=Identity(artifactStat_,artifactBytes_,expected.sha256);
        state_=FileState::ArtifactDurable;return true;
    }
    bool CommitEnvelope(const uint8_t* bytes,size_t n) noexcept {
        Call call(*this); if(!call.entered) return false;
        if(state_!=FileState::ArtifactDurable) return Fail(FileError::State,"envelope-order");
        if(!bytes||!n||n>kEnvelopeReserve) return Fail(FileError::Resource,"envelope-bound");
        if(!Chain()||!Named(kDiagnosticFile,artifactStat_,artifactBytes_)||!Named(kEnvelopeFile,envelopeStat_,0)) return false;
        Sha256 hash;
        if(!WriteAll(envelope_,bytes,n,envelopeBytes_,hash)||!Disk(envelope_,envelopeStat_,n,hash.Finish())||
            !Sync(envelope_,false,"envelope-sync")||!Close(envelope_)||
            !Sync(Root(),true,"commit-directory-sync")||!Chain()||
            !Named(kDiagnosticFile,artifactStat_,artifactBytes_)||!Named(kEnvelopeFile,envelopeStat_,n)) return false;
        receipt_.envelope=Identity(envelopeStat_,n,hash.Finish());
        // Checked close of every held directory is part of success.
        for(size_t i=nodeCount_;i>0;--i) if(!Close(nodes_[i-1].fd)) return false;
        state_=FileState::Committed;receipt_.complete=true;return true;
    }
};
} // namespace r03_diag_v2
#endif
