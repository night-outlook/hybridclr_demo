// Test driver only: file loading/arena allocation happen before the allocation ban.
#include "../source/NativeArtifactTransaction.h"
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <string>
#include <vector>
#include <new>
#include <stdexcept>
#include <algorithm>
using namespace r03::bounded_v2;
static bool forbidNew=false;
static unsigned newCalls=0;
void* operator new(std::size_t n){if(forbidNew){::write(2,"UNEXPECTED_NATIVE_NEW\n",22);::_exit(90);}++newCalls;if(void* p=std::malloc(n?n:1))return p;throw std::bad_alloc();}
void* operator new[](std::size_t n){return ::operator new(n);}
void operator delete(void* p)noexcept{std::free(p);}
void operator delete[](void* p)noexcept{std::free(p);}
#if defined(__cpp_sized_deallocation)
void operator delete(void* p,std::size_t)noexcept{std::free(p);}
void operator delete[](void* p,std::size_t)noexcept{std::free(p);}
#endif
static std::vector<std::uint8_t> Read(const char* name){
    if(std::strcmp(name,"-")==0)return {};
    std::ifstream f(name,std::ios::binary);if(!f)throw std::runtime_error("fixture not readable");
    std::vector<std::uint8_t> b((std::istreambuf_iterator<char>(f)),{});
    if(b.size()>kTotal+1024)throw std::runtime_error("fixture too large");return b;
}
struct TestIo:PosixIo {
    static inline const char* mode="";static inline unsigned writes=0,syncs=0,closes=0;
    static inline std::size_t largest=0;static inline char events[2048]{};static inline unsigned eventCount=0;
    static inline std::uint8_t* mutation=nullptr;
    static inline std::uint8_t* inlineMutation=nullptr;
    static void Event(char c)noexcept{if(eventCount<2047)events[eventCount++]=c;}
    static ssize_t Write(int fd,const void* p,std::size_t n)noexcept{
        ++writes;largest=std::max(largest,n);Event('W');
        if(std::strcmp(mode,"write_fail")==0&&writes==4){errno=ENOSPC;return -1;}
        if(std::strcmp(mode,"raw_write_fail")==0&&closes==1){errno=ENOSPC;return -1;}
        if(std::strcmp(mode,"write_zero")==0&&writes==2)return 0;
        if(std::strcmp(mode,"write_eintr")==0&&writes==1){errno=EINTR;return -1;}
        if(std::strcmp(mode,"persistent_eintr")==0){errno=EINTR;return -1;}
        if(std::strcmp(mode,"mutate_during")==0&&writes==4&&mutation)*mutation^=1;
        if(std::strcmp(mode,"mutate_inline")==0&&writes==4&&inlineMutation)*inlineMutation^=1;
        if(std::strcmp(mode,"short_write")==0&&n>1)n=(n+1)/2;
        return PosixIo::Write(fd,p,n);
    }
    static int Sync(int fd)noexcept{
        ++syncs;Event('S');
        if((std::strcmp(mode,"sync_artifact")==0&&syncs==1)||
           (std::strcmp(mode,"sync_directory_first")==0&&syncs==2)||
           (std::strcmp(mode,"sync_raw")==0&&syncs==3)||
           (std::strcmp(mode,"sync_directory_final")==0&&syncs==4)){errno=EIO;return -1;}
        return PosixIo::Sync(fd);
    }
    static int Close(int fd)noexcept{
        ++closes;Event('C');int code=PosixIo::Close(fd);
        if((std::strcmp(mode,"close_artifact")==0&&closes==1)||
           (std::strcmp(mode,"close_raw")==0&&closes==2)){errno=EIO;return -1;}
        return code;
    }
};
int main(int argc,char**argv){
    try{
        if(argc==3&&std::strcmp(argv[1],"hash")==0){auto b=Read(argv[2]);Sha256 h;
            for(std::size_t i=0;i<b.size();){auto n=std::min<std::size_t>(17,b.size()-i);h.Update(b.data()+i,n);i+=n;}
            char out[65];Hex(h.Finish(),out);std::puts(out);return 0;}
        if(argc!=7)return 64;
        TestIo::mode=argv[1];auto a=Read(argv[3]),b=Read(argv[4]),in=Read(argv[5]);
        Digest context{};if(std::strlen(argv[6])!=64)return 65;
        auto val=[](char c){if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;return -1;};
        for(unsigned i=0;i<32;++i){int x=val(argv[6][2*i]),y=val(argv[6][2*i+1]);if(x<0||y<0)return 65;context[i]=static_cast<std::uint8_t>(x*16+y);}
        std::vector<std::uint8_t> arena(kMaxStream);
        std::string held=std::string(argv[2])+".held",artifact=std::string(argv[2])+"/"+kArtifactName,
                    sentinel=std::string(argv[2])+"/sentinel",extra=std::string(argv[2])+"/second-link";
        TestIo::mutation=arena.data();TestIo::inlineMutation=in.data();Capture capture(arena.data(),arena.size());Transaction<TestIo> tx;
        Descriptor d{};bool ok=tx.Arm(argv[2]);unsigned beforeNew=newCalls;
        forbidNew=true;
        if(ok){
            if(std::strcmp(argv[1],"wrong_order")==0)ok=capture.Begin(15,true);
            else{
                ok=capture.Begin(14,std::strcmp(argv[3],"-")!=0);
                for(std::size_t pos=0;ok&&pos<a.size();){auto n=std::min<std::size_t>(7919,a.size()-pos);ok=capture.Append(a.data()+pos,n);pos+=n;}
                if(ok)ok=capture.End();
                if(ok&&std::strcmp(argv[1],"missing_section")!=0){
                    ok=capture.Begin(15,std::strcmp(argv[4],"-")!=0);
                    for(std::size_t pos=0;ok&&pos<b.size();){auto n=std::min<std::size_t>(37,b.size()-pos);ok=capture.Append(b.data()+pos,n);pos+=n;}
                    if(ok)ok=capture.End();
                }
                if(ok)ok=capture.Freeze();
            }
        }
        if(ok&&std::strcmp(argv[1],"late_append")==0)ok=capture.Append("x",1);
        if(ok&&std::strcmp(argv[1],"mutate_before")==0&&!a.empty())arena[0]^=1;
        if(ok&&std::strcmp(argv[1],"rename_directory")==0){if(::rename(argv[2],held.c_str())!=0||::mkdir(argv[2],0700)!=0)return 66;}
        if(ok&&std::strcmp(argv[1],"replace_artifact")==0){
            int f=::open(sentinel.c_str(),O_WRONLY|O_CREAT|O_EXCL,0600);if(f<0)return 66;
            if(::write(f,"preserve",8)!=8)return 66;::close(f);
            if(::unlink(artifact.c_str())!=0||::symlink("sentinel",artifact.c_str())!=0)return 66;
        }
        if(ok&&std::strcmp(argv[1],"hardlink_artifact")==0&&::link(artifact.c_str(),extra.c_str())!=0)return 66;
        if(ok&&std::strcmp(argv[1],"change_owner_mode")==0&&::chmod(argv[2],0755)!=0)return 66;
        if(ok)ok=tx.Commit(capture,context,in.data(),in.size(),d);
        Failure f=capture.GetFailure().code==Error::None?tx.GetFailure():capture.GetFailure();
        if(!ok){ // Failed state stays latched even if a caller attempts another operation.
            if(capture.GetFailure().code!=Error::None){(void)capture.Begin(14,true);if(capture.GetFailure().code!=f.code)return 67;}
            else {(void)tx.Commit(capture,context,in.data(),in.size(),d);if(tx.GetFailure().code!=f.code)return 67;}
        }
        if(ok&&std::strcmp(argv[1],"repeat_commit")==0){ok=tx.Commit(capture,context,in.data(),in.size(),d);f=tx.GetFailure();}
        forbidNew=false;
        const auto&r=tx.Receipt();char rawHash[65],artHash[65];Hex(r.envelopeHash,rawHash);Hex(r.artifactHash,artHash);
        std::printf("{\"ok\":%s,\"error\":%u,\"slot\":%u,\"observed\":%zu,\"errno\":%d,\"newCallsInComponent\":%u,\"largestWrite\":%zu,\"events\":\"%s\",\"receipt\":{\"committed\":%s,\"directoryDevice\":%llu,\"directoryInode\":%llu,\"artifactDevice\":%llu,\"artifactInode\":%llu,\"envelopeDevice\":%llu,\"envelopeInode\":%llu,\"artifactBytes\":%zu,\"envelopeBytes\":%zu,\"artifactHash\":\"%s\",\"envelopeHash\":\"%s\"}}\n",
          ok?"true":"false",static_cast<unsigned>(f.code),f.slot,f.observed,f.osError,newCalls-beforeNew,TestIo::largest,TestIo::events,
          r.committed?"true":"false",static_cast<unsigned long long>(r.directoryDevice),static_cast<unsigned long long>(r.directoryInode),
          static_cast<unsigned long long>(r.artifactDevice),static_cast<unsigned long long>(r.artifactInode),
          static_cast<unsigned long long>(r.envelopeDevice),static_cast<unsigned long long>(r.envelopeInode),
          r.artifactBytes,r.envelopeBytes,artHash,rawHash);
        return ok?0:3;
    }catch(const std::exception& e){std::fprintf(stderr,"harness exception: %s\n",e.what());return 68;}
}
