#pragma once
// Optional POSIX sidecar sink. Accepts an already authenticated directory FD.
// This does not walk/authorize an arbitrary path or commit the V2 envelope.
#include "BoundedDiagnosticsV2.h"
#include <cerrno>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

namespace r03::diagnostics_v2 {
struct PosixCalls {
    ssize_t (*write)(int,const void*,std::size_t)=::write;
    int (*sync)(int)=::fsync;
    int (*close)(int)=::close;
};
class PosixDiagnosticFile final {
    int dir_=-1,fd_=-1;
    struct stat identity_{};
    std::size_t written_=0;
    bool attempted_=false,done_=false;
    int error_=0;
    PosixCalls calls_{};
    static constexpr const char* Name="diagnostics.v2";
    bool Fail(int e) noexcept { if(!error_)error_=e?e:EIO; return false; }
    bool Check() noexcept {
        struct stat a{},b{};
        if(::fstat(fd_,&a)<0 || ::fstatat(dir_,Name,&b,AT_SYMLINK_NOFOLLOW)<0)return Fail(errno);
        for(const auto* s:{&a,&b}) {
            if(!S_ISREG(s->st_mode) || (s->st_mode&0777)!=0600 || s->st_nlink!=1 ||
               s->st_dev!=identity_.st_dev || s->st_ino!=identity_.st_ino ||
               s->st_uid!=identity_.st_uid || s->st_size<0 ||
               static_cast<std::uintmax_t>(s->st_size)!=written_)return Fail(ESTALE);
        }
        return true;
    }
    bool Sync(int fd) noexcept {
        for(unsigned i=0;i<8;++i){if(calls_.sync(fd)==0)return true;if(errno!=EINTR)return Fail(errno);}
        return Fail(EINTR);
    }
    static bool Write(void* self,const std::uint8_t* p,std::size_t n,int& err) noexcept {
        auto& s=*static_cast<PosixDiagnosticFile*>(self);
        if(s.error_ || s.done_ || s.fd_<0 || n>FrameLimit || n>ArtifactBudget-s.written_ || (n&&!p)) {
            s.Fail(EINVAL);err=s.error_;return false;
        }
        if(!s.Check()){err=s.error_;return false;}
        unsigned interruptions=0;
        while(n) {
            const auto k=s.calls_.write(s.fd_,p,n);
            if(k<0){if(errno==EINTR && ++interruptions<=8)continue;s.Fail(errno);err=s.error_;return false;}
            if(k==0 || static_cast<std::size_t>(k)>n){s.Fail(EIO);err=s.error_;return false;}
            const auto count=static_cast<std::size_t>(k);s.written_+=count;p+=count;n-=count;
        }
        return true;
    }
    static bool Finish(void* self,int& err) noexcept {
        auto& s=*static_cast<PosixDiagnosticFile*>(self);
        if(s.error_ || s.done_ || s.fd_<0){s.Fail(EINVAL);err=s.error_;return false;}
        if(!s.Check() || !s.Sync(s.fd_)){err=s.error_;return false;}
        const int old=s.fd_;s.fd_=-1;
        // Never retry close(EINTR): the descriptor may already have been closed.
        if(s.calls_.close(old)<0){s.Fail(errno);err=s.error_;return false;}
        if(!s.Sync(s.dir_)){err=s.error_;return false;}
        // Verify the retained name still identifies the created inode after sync.
        struct stat after{};
        if(::fstatat(s.dir_,Name,&after,AT_SYMLINK_NOFOLLOW)<0){s.Fail(errno);err=s.error_;return false;}
        if(!S_ISREG(after.st_mode) || after.st_dev!=s.identity_.st_dev ||
           after.st_ino!=s.identity_.st_ino || after.st_nlink!=1 ||
           after.st_uid!=s.identity_.st_uid || (after.st_mode&0777)!=0600 ||
           after.st_size<0 || static_cast<std::uintmax_t>(after.st_size)!=s.written_){
            s.Fail(ESTALE);err=s.error_;return false;
        }
        s.done_=true;return true;
    }
public:
    explicit PosixDiagnosticFile(PosixCalls calls={}) noexcept : calls_(calls) {}
    PosixDiagnosticFile(const PosixDiagnosticFile&)=delete;
    PosixDiagnosticFile& operator=(const PosixDiagnosticFile&)=delete;
    ~PosixDiagnosticFile(){if(fd_>=0)::close(fd_);if(dir_>=0)::close(dir_);}
    bool Prepare(int approvedDirectory) noexcept {
        if(attempted_)return Fail(EALREADY);
        attempted_=true;
        if(!calls_.write || !calls_.sync || !calls_.close)return Fail(EINVAL);
        struct stat directory{};
        if(::fstat(approvedDirectory,&directory)<0)return Fail(errno);
        if(!S_ISDIR(directory.st_mode) || directory.st_uid!=::geteuid() ||
           (directory.st_mode&0777)!=0700)return Fail(EPERM);
        dir_=::fcntl(approvedDirectory,F_DUPFD_CLOEXEC,0);if(dir_<0)return Fail(errno);
        fd_=::openat(dir_,Name,O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
        if(fd_<0)return Fail(errno);
        if(::fstat(fd_,&identity_)<0)return Fail(errno);
        return Check();
    }
    Sink AsSink() noexcept { return {this,Write,Finish}; }
    int FirstError() const noexcept { return error_; }
    std::size_t BytesWritten() const noexcept { return written_; }
    bool DurableSidecar() const noexcept { return done_; }
};
// Reserve accounts for codec state plus this FD sink, not external metadata.
static_assert(sizeof(Capture)+sizeof(PosixDiagnosticFile)+InlineLimit+2048<=TotalBudget,"codec/sink budget");
} // namespace r03::diagnostics_v2
