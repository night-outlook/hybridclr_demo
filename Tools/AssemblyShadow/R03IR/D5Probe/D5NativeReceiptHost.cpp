// Host-only positive/negative tests of the exact C10 native receipt writer.
// NO real MethodInfo, Unity/IL2CPP, VM canary or Player first-error is exercised.
#include "vm/AssemblyShadowD5WindowProbe.h"
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

extern "C" int32_t R03_D5_ReceiptOpen(const char*,const char*,const char*,const char*);
extern "C" int32_t R03_D5_ReceiptEvent(int32_t,int32_t,int32_t,int32_t,int32_t);
extern "C" int32_t R03_D5_BindKeepCanary(void*);
extern "C" int32_t R03_D5_ReceiptSeal(int32_t,int32_t,int32_t,int32_t);

#define REQUIRE(x) do { if(!(x)){std::fprintf(stderr,"D5 receipt host assertion failed: %s (%d)\n",#x,__LINE__);return 1;}}while(0)
struct Event { uint32_t magic;int32_t slot,a,b,c,d;uint32_t checksum,size; };
static_assert(sizeof(Event)==32,"C10 host event schema");
int main(int argc,char**argv)
{
    if(argc!=2)return 2;
    static const char sha[]="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    static const char fixture[]="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
    REQUIRE(R03_D5_ReceiptOpen(argv[1],"sourcehost-1",sha,fixture)==1);
    REQUIRE(R03_D5_ReceiptOpen(argv[1],"sourcehost-2",sha,fixture)==-1);
    REQUIRE(R03_D5_ReceiptEvent(0,0,0,0,0)==-1);
    REQUIRE(R03_D5_ReceiptEvent(1,1,0,0,0)==1);
    REQUIRE(R03_D5_ReceiptEvent(1,1,0,0,0)==-2);
    REQUIRE(R03_D5_ReceiptEvent(2,2,1,0,0)==1);
    REQUIRE(R03_D5_BindKeepCanary(nullptr)==0); // NO VM on host
    REQUIRE(R03_D5_ReceiptEvent(4,1,0,0,0)==1);
    REQUIRE(R03_D5_ReceiptEvent(5,1,42,0,0)==1);
    auto& probe=il2cpp::vm::assembly_shadow_d5::WindowProbe::Instance();
    REQUIRE(probe.Arm(100));
    probe.AtP5();
    probe.MethodResult(2,true,true); // synthetic guard input only
    REQUIRE(probe.ReleaseP5());
    probe.AtP6();
    probe.Complete();
    REQUIRE(R03_D5_ReceiptSeal(0,6,1,1)==1);
    REQUIRE(R03_D5_ReceiptEvent(5,1,42,0,0)==-1);
    struct stat st{};
    REQUIRE(::stat(argv[1],&st)==0 && st.st_size==4652);
    int fd=::open(argv[1],O_RDONLY);
    REQUIRE(fd>=0);
    char magic[8]={};
    REQUIRE(::pread(fd,magic,8,0)==8);
    REQUIRE(std::memcmp(magic,"D5C10E1!",8)==0);
    Event e{};
    REQUIRE(::pread(fd,&e,sizeof e,212+9*32)==static_cast<ssize_t>(sizeof e));
    REQUIRE(e.magic==0xC105D5E1u && e.slot==10 && e.a==1 && e.size==32);
    ::close(fd);
    std::puts("{\"result\":\"PassedD5NativeEvidenceWriterHostOnly\",\"realPlayerExecuted\":false,\"canaryFromRealVM\":false,\"firstErrorFromRealVM\":false}");
    return 0;
}
