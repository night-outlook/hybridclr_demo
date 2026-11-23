// Test-only native asynchronous receipt writer test: never a VM/Player result.
// Compiled only with HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO=1. It executes the same
// prestarted writer and fixed 4652-byte record path as the real-VM branch.
#include "vm/AssemblyShadowD5WindowProbe.h"
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <sys/stat.h>
#include <thread>
#include <unistd.h>

using il2cpp::vm::assembly_shadow_d5::WindowProbe;
extern "C" int32_t R03_D5_ReceiptOpen(const char*,const char*,const char*,const char*);
extern "C" int32_t R03_D5_ReceiptEvent(int32_t,int32_t,int32_t,int32_t,int32_t);
extern "C" int32_t R03_D5_SourceHostAutoConfigure(int32_t,int32_t,int32_t,int32_t,int32_t);
extern "C" int32_t R03_D5_SourceHostAutoSealStatus();
extern "C" int32_t R03_D5_SourceHostAutoExitCode();
extern "C" int32_t R03_D5_SourceHostAutoDone();

#define REQUIRE(x) do { if (!(x)) { \
    std::fprintf(stderr,"D5 native autocollector source host FAIL %d %s\n",__LINE__,#x); \
    return 1; } } while (0)

struct RawEvent { uint32_t magic;int32_t slot,a,b,c,d;uint32_t checksum,size; };
static_assert(sizeof(RawEvent)==32,"D5 C10 raw event wire size");

int main(int argc,char** argv)
{
    if (argc != 3) return 2;
    const char* test = argv[1];
    const char* file = argv[2];
    static const char hash1[] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    static const char hash2[] = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
    REQUIRE(R03_D5_ReceiptOpen(file,"synthetic-auto",hash1,hash2)==1);
    REQUIRE(R03_D5_ReceiptEvent(1,1,0,0,0)==1);

    WindowProbe& probe = WindowProbe::Instance();
    REQUIRE(probe.Arm(200));
    probe.AtP5();
    const bool deny = !std::strcmp(test,"denied");
    const bool allow = !std::strcmp(test,"allowed");
    const bool foreign = !std::strcmp(test,"foreign");
    const bool wrong = !std::strcmp(test,"wrongmethod");
    const bool race = !std::strcmp(test,"raced");
    const bool noattempt = !std::strcmp(test,"noattempt");
    const bool ioPwrite = !std::strcmp(test,"io_pwrite");
    const bool ioFsync = !std::strcmp(test,"io_fsync");
    const bool ioClose = !std::strcmp(test,"io_close");
    const bool ioDir = !std::strcmp(test,"io_dirsync");
    const int32_t fault = ioPwrite ? 1 : ioFsync ? 2 : ioClose ? 3 : ioDir ? 4 : 0;
    const bool faulted = fault != 0;
    REQUIRE(deny||allow||foreign||wrong||race||noattempt||faulted);
    if (!noattempt)
    {
        REQUIRE(probe.ArmTargetForCurrentThread(&probe));
        if (foreign)
        {
            std::atomic<bool> match{true};
            std::thread competitor([&] {
                bool found=probe.MatchesTargetOnCurrentThread(&probe);
                match.store(found,std::memory_order_release);
                probe.MethodResult(2,found,false);
            });
            competitor.join();
            REQUIRE(!match.load(std::memory_order_acquire));
        }
        else if (wrong)
        {
            int otherMethod=0;
            REQUIRE(!probe.MatchesTargetOnCurrentThread(&otherMethod));
            probe.MethodResult(2,probe.MatchesTargetOnCurrentThread(&otherMethod),false);
        }
        else if (race)
        {
            REQUIRE(probe.MatchesTargetOnCurrentThread(&probe));
            probe.AtP6();
            probe.MethodResult(2,true,false);
        }
        else
        {
            REQUIRE(probe.MatchesTargetOnCurrentThread(&probe));
            probe.MethodResult(2,true,allow);
        }
    }
    if (allow) REQUIRE(probe.ReleaseP5());
    if (race) REQUIRE(probe.TargetDecision()==3);
    // Every mock state is explicitly synthetic. The actual native VM branch
    // obtains state/first error independently from AssemblyShadow.
    REQUIRE(R03_D5_SourceHostAutoConfigure(
        allow ? 6 : (deny||faulted) ? 9 : 5,
        allow ? 1 : 0, noattempt ? 0 : 1,
        deny||faulted ? 1 : 0, fault)==1);
    bool done=false;
    for (int t=0;t<4000;++t)
    {
        if (R03_D5_SourceHostAutoDone()==1) { done=true; break; }
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    REQUIRE(done); // no managed work is required to finish an autonomous file
    const int32_t seal=R03_D5_SourceHostAutoSealStatus();
    const int32_t observedExit=R03_D5_SourceHostAutoExitCode();
    REQUIRE((seal==1)==!faulted);
    REQUIRE(observedExit==(faulted ? 2 : allow ? 42 : deny ? 20 : 2));
    struct stat info{};
    // The final path exists ONLY after a successful sync and close.
    if (faulted && !ioDir)
    {
        REQUIRE(::stat(file,&info)!=0);
        std::printf("{\"result\":\"PassedD5NativeAutoCollectorHostOnly\",\"scenario\":\"%s\",\"expectedFailure\":true,\"mockExitCode\":%d,\"realPlayerExecuted\":false}\n",test,observedExit);
        return 0;
    }
    REQUIRE(::stat(file,&info)==0 && info.st_size==4652);
    const int fd=::open(file,O_RDONLY);
    REQUIRE(fd>=0);
    char header[8]={};
    REQUIRE(::pread(fd,header,sizeof header,0)==8);
    REQUIRE(std::memcmp(header,"D5C10E1!",8)==0);
    RawEvent end{};
    REQUIRE(::pread(fd,&end,sizeof end,212+9*32)==
        static_cast<ssize_t>(sizeof end));
    REQUIRE(end.magic==0xC105D5E1u && end.slot==10 && end.a==1 &&
        end.d==1 && end.size==32);
    RawEvent guard{};
    REQUIRE(::pread(fd,&guard,sizeof guard,212+4*32)==
        static_cast<ssize_t>(sizeof guard));
    if (deny) REQUIRE(guard.slot==5 && guard.a==2);
    if (allow) REQUIRE(guard.slot==5 && guard.a==1);
    if (race) REQUIRE(guard.slot==5 && guard.a==3);
    if (foreign || wrong || noattempt) REQUIRE(guard.magic==0 && guard.slot==0);
    if (faulted) REQUIRE(guard.slot==5 && guard.a==2);
    ::close(fd);
    std::printf("{\"result\":\"PassedD5NativeAutoCollectorHostOnly\",\"scenario\":\"%s\",\"expectedFailure\":%s,\"mockExitCode\":%d,\"realPlayerExecuted\":false,\"canaryFromRealVM\":false,\"firstErrorFromRealVM\":false}\n",test,faulted?"true":"false",observedExit);
    return 0;
}
