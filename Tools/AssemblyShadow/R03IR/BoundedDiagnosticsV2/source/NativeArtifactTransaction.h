#pragma once
// POSIX transaction component for the reviewed V2 protocol; not a Unity adapter.
// Caller must prearm while healthy in an independently admitted private directory.
#include "BoundedDiagnosticsV2.h"
#include <cerrno>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

namespace r03::bounded_v2 {
class DirectoryLease final {
    struct Node { int fd=-1; char name[256]{}; struct stat identity{}; };
    std::array<Node,65> nodes_{}; std::size_t count_=0;
    static bool Same(const struct stat& a,const struct stat& b) noexcept {
        return a.st_dev==b.st_dev&&a.st_ino==b.st_ino&&a.st_uid==b.st_uid&&a.st_gid==b.st_gid&&a.st_mode==b.st_mode;
    }
public:
    DirectoryLease()=default;DirectoryLease(const DirectoryLease&)=delete;
    DirectoryLease& operator=(const DirectoryLease&)=delete;
    ~DirectoryLease(){for(std::size_t i=0;i<count_;++i)if(nodes_[i].fd>=0)::close(nodes_[i].fd);}
    bool Open(const char* path,Failure& f) noexcept {
        if(count_||!path||path[0]!='/')return f.Set(Error::Path);
        auto n=::strnlen(path,4097);
        if(n<2||n>4096||path[n-1]=='/')return f.Set(Error::Path);
        int root=::open("/",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
        if(root<0)return f.Set(Error::Path,0,0,errno);
        nodes_[0].fd=root;count_=1;
        if(::fstat(root,&nodes_[0].identity)!=0)return f.Set(Error::Path,0,0,errno);
        std::size_t begin=1;
        while(begin<n){
            auto end=begin;while(end<n&&path[end]!='/')++end;auto length=end-begin;
            if(length==0||length>255||count_==nodes_.size()||
               (length==1&&path[begin]=='.')||
               (length==2&&path[begin]=='.'&&path[begin+1]=='.'))return f.Set(Error::Path);
            Node& node=nodes_[count_];std::memcpy(node.name,path+begin,length);node.name[length]=0;
            node.fd=::openat(nodes_[count_-1].fd,node.name,O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
            if(node.fd<0)return f.Set(Error::Path,0,0,errno);
            ++count_;if(::fstat(node.fd,&node.identity)!=0)return f.Set(Error::Path,0,0,errno);
            begin=end+1;
        }
        const auto& st=nodes_[count_-1].identity;
        if(st.st_uid!=::geteuid()||(st.st_mode&07777)!=0700)return f.Set(Error::Owner);
        return Check(f);
    }
    int Fd() const noexcept{return count_?nodes_[count_-1].fd:-1;}
    const struct stat& Identity() const noexcept{return nodes_[count_-1].identity;}
    bool Check(Failure& f) const noexcept{
        if(f.code!=Error::None)return false;
        if(!count_)return f.Set(Error::State);
        for(std::size_t i=0;i<count_;++i){
            struct stat held{};if(::fstat(nodes_[i].fd,&held)!=0)return f.Set(Error::Changed,0,i,errno);
            if(!Same(held,nodes_[i].identity))return f.Set(Error::Changed,0,i);
            if(i){struct stat named{};
                if(::fstatat(nodes_[i-1].fd,nodes_[i].name,&named,AT_SYMLINK_NOFOLLOW)!=0)
                    return f.Set(Error::Changed,0,i,errno);
                if(!Same(named,held))return f.Set(Error::Changed,0,i);
            }
        }return true;
    }
};

// Injectable only for source tests; default operations are direct POSIX calls.
struct PosixIo {
    static ssize_t Write(int fd,const void* p,std::size_t n) noexcept{return ::write(fd,p,n);}
    static int Sync(int fd) noexcept{return ::fsync(fd);}
    static int Close(int fd) noexcept{return ::close(fd);}
};
struct CommitReceipt {
    bool committed=false;std::uint64_t directoryDevice=0,directoryInode=0;
    std::uint64_t artifactDevice=0,artifactInode=0,envelopeDevice=0,envelopeInode=0;
    std::size_t artifactBytes=0,envelopeBytes=0;Digest artifactHash{},envelopeHash{};
};

template<class Io=PosixIo> class Transaction final {
    DirectoryLease lease_;std::array<int,2> fd_{{-1,-1}};std::array<struct stat,2> id_{};
    std::array<std::size_t,2> written_{};Failure failure_{};unsigned state_=0;
    Sha256 envelopeHash_;CommitReceipt receipt_{};
    const char* Name(unsigned i) const noexcept{return i==0?kArtifactName:kEnvelopeName;}
    bool Match(unsigned i) noexcept{
        struct stat st{};if(::fstatat(lease_.Fd(),Name(i),&st,AT_SYMLINK_NOFOLLOW)!=0)
            return failure_.Set(Error::Changed,i,written_[i],errno);
        const auto& old=id_[i];
        if(!S_ISREG(st.st_mode)||st.st_uid!=::geteuid()||(st.st_mode&07777)!=0600||st.st_nlink!=1||
           st.st_dev!=old.st_dev||st.st_ino!=old.st_ino||st.st_gid!=old.st_gid||st.st_size<0||
           static_cast<std::uint64_t>(st.st_size)!=written_[i])return failure_.Set(Error::Changed,i,written_[i]);
        // A name match alone does not establish that the descriptor being
        // written still names that inode. Check both while the FD is held.
        if(fd_[i]>=0){
            struct stat held{};
            if(::fstat(fd_[i],&held)!=0)return failure_.Set(Error::Changed,i,written_[i],errno);
            if(held.st_dev!=st.st_dev||held.st_ino!=st.st_ino||held.st_mode!=st.st_mode||
               held.st_uid!=st.st_uid||held.st_gid!=st.st_gid||held.st_nlink!=st.st_nlink||
               held.st_size!=st.st_size)return failure_.Set(Error::Changed,i,written_[i]);
        }
        return true;
    }
    bool WriteAll(unsigned i,const void* p,std::size_t n) noexcept{
        if(failure_.code!=Error::None)return false;
        const std::size_t bound=i==0?kMaxStream:kEnvelopeReserve;
        if((!p&&n)||fd_[i]<0)return failure_.Set(Error::Input,i,written_[i]);
        if(written_[i]>bound||n>bound-written_[i])return failure_.Set(Error::Resource,i,written_[i]);
        const auto* bytes=static_cast<const std::uint8_t*>(p);unsigned interrupted=0;
        while(n){
            const auto request=n<kChunk?n:kChunk;
            auto r=Io::Write(fd_[i],bytes,request);
            if(r<0){if(errno==EINTR&&++interrupted<=8)continue;return failure_.Set(Error::Write,i,written_[i],errno);}
            if(r==0||static_cast<std::size_t>(r)>request)return failure_.Set(Error::Write,i,written_[i],EIO);
            auto size=static_cast<std::size_t>(r);if(i==1)envelopeHash_.Update(bytes,size);
            bytes+=size;n-=size;written_[i]+=size;interrupted=0;
        }return true;
    }
    bool Sync(int fd,unsigned location) noexcept{
        if(Io::Sync(fd)!=0)return failure_.Set(Error::Sync,location,0,errno);return true;
    }
    bool Close(unsigned i) noexcept{
        int fd=fd_[i];fd_[i]=-1; // Do not retry a close with ambiguous EINTR state.
        if(Io::Close(fd)!=0)return failure_.Set(Error::Close,i,written_[i],errno);return true;
    }
    struct ArtifactSink{Transaction& tx;bool Write(const void* p,std::size_t n) noexcept{return tx.WriteAll(0,p,n);}};
    static char* Copy(char* p,const char* s) noexcept{while(*s)*p++=*s++;return p;}
    static char* Number(char* p,std::size_t n) noexcept{
        char tmp[32];unsigned count=0;do{tmp[count++]=static_cast<char>('0'+n%10);n/=10;}while(n);
        while(count)*p++=tmp[--count];return p;
    }
public:
    Transaction()=default;Transaction(const Transaction&)=delete;Transaction& operator=(const Transaction&)=delete;
    ~Transaction(){for(auto fd:fd_)if(fd>=0)::close(fd);} // Close, never unlink retained partial files.
    const Failure& GetFailure()const noexcept{return failure_;}
    CommitReceipt Receipt()const noexcept{auto r=receipt_;r.committed=r.committed&&failure_.code==Error::None;return r;}
    bool Arm(const char* ownedDirectory) noexcept{
        if(failure_.code!=Error::None)return false;
        if(state_!=0)return failure_.Set(Error::State);state_=1;
        if(!lease_.Open(ownedDirectory,failure_))return false;
        for(unsigned i=0;i<2;++i){
            fd_[i]=::openat(lease_.Fd(),Name(i),O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
            if(fd_[i]<0)return failure_.Set(Error::File,i,0,errno);
            if(::fstat(fd_[i],&id_[i])!=0)return failure_.Set(Error::File,i,0,errno);
            if(!Match(i))return false;
        }state_=2;return lease_.Check(failure_);
    }
    bool Commit(const Capture& capture,Digest binding,const void* inlineData,
                std::size_t inlineSize,Descriptor& result) noexcept{
        result=Descriptor{}; // Never return a prior successful descriptor on failure.
        if(failure_.code!=Error::None)return false;
        if(state_!=2)return failure_.Set(Error::State);state_=3;
        const auto* text=static_cast<const char*>(inlineData);
        if(!text||inlineSize<2||inlineSize>kInlineLimit||text[0]!='{'||text[inlineSize-1]!='}')
            return failure_.Set(Error::Input);
        if(!lease_.Check(failure_)||!Match(0)||!Match(1))return false;
        ArtifactSink sink{*this};Descriptor d;
        if(!Encode(capture,binding,inlineData,inlineSize,sink,d,failure_))return false;
        if(!Match(0)||!Sync(fd_[0],0)||!Close(0)||!Sync(lease_.Fd(),2))return false;
        if(!lease_.Check(failure_)||!Match(0)||!Match(1))return false;
        if(Sha256::Of(inlineData,inlineSize)!=d.inlineSha)return failure_.Set(Error::Changed,1);
        // Metadata is bounded ASCII and the inline bytes are retained verbatim.
        char metadata[512],hash[65],context[65],inHash[65];Hex(d.sha,hash);Hex(d.binding,context);Hex(d.inlineSha,inHash);
        char* p=Copy(metadata,"{\"diagnosticArtifact\":{\"kind\":\"R03BoundedDiagnosticsV2\",\"bytes\":");
        p=Number(p,d.bytes);p=Copy(p,",\"sha256\":\"");p=Copy(p,hash);
        p=Copy(p,"\",\"binding\":\"");p=Copy(p,context);p=Copy(p,"\",\"inlineSha256\":\"");p=Copy(p,inHash);p=Copy(p,"\"}");
        if(inlineSize>2)*p++=',';
        if(!WriteAll(1,metadata,static_cast<std::size_t>(p-metadata))||!WriteAll(1,text+1,inlineSize-1))return false;
        if(!Match(1)||!Sync(fd_[1],1)||!Close(1)||!Sync(lease_.Fd(),3))return false;
        if(!lease_.Check(failure_)||!Match(0)||!Match(1))return false;
        if(Sha256::Of(inlineData,inlineSize)!=d.inlineSha)return failure_.Set(Error::Changed,1);
        receipt_.directoryDevice=lease_.Identity().st_dev;receipt_.directoryInode=lease_.Identity().st_ino;
        receipt_.artifactDevice=id_[0].st_dev;receipt_.artifactInode=id_[0].st_ino;
        receipt_.envelopeDevice=id_[1].st_dev;receipt_.envelopeInode=id_[1].st_ino;
        receipt_.artifactBytes=written_[0];receipt_.envelopeBytes=written_[1];
        receipt_.artifactHash=d.sha;receipt_.envelopeHash=envelopeHash_.Finish();
        receipt_.committed=true;result=d;state_=4;return true;
    }
};
} // namespace r03::bounded_v2
