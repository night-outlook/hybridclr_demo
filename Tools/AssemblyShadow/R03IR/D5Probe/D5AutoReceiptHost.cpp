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
    const bool unknownCanary = !std::strcmp(test,"allowed_canary_unknown");
    const bool allow = !std::strcmp(test,"allowed") || unknownCanary;
    const bool durableBefore = !std::strcmp(test,"entry_durable_before_error");
    const bool mixedEntry = !std::strcmp(test,"entry_policy_raced");
    const bool racedDenial = !std::strcmp(test,"terminal_policy_raced");
    const bool foreign = !std::strcmp(test,"foreign");
    const bool wrong = !std::strcmp(test,"wrongmethod");
    const bool race = !std::strcmp(test,"raced");
    const bool noattempt = !std::strcmp(test,"noattempt");
    const bool preterminal = !std::strcmp(test,"entry_preterminal");
    const bool priorerror = !std::strcmp(test,"entry_prior_error");
    const bool noentry = !std::strcmp(test,"entry_missing_guard");
    const bool ioPwrite = !std::strcmp(test,"io_pwrite");
    const bool ioFsync = !std::strcmp(test,"io_fsync");
    const bool ioClose = !std::strcmp(test,"io_close");
    const bool ioDir = !std::strcmp(test,"io_dirsync");
    const int32_t fault = ioPwrite ? 1 : ioFsync ? 2 : ioClose ? 3 : ioDir ? 4 : 0;
    const bool faulted = fault != 0;
    REQUIRE(deny||allow||foreign||wrong||race||noattempt||faulted||
            preterminal||priorerror||noentry||durableBefore||mixedEntry||racedDenial);
    REQUIRE(R03_D5_SourceHostAutoConfigure(5,0,noattempt ? 0 : 1,0,0)==1);
    if (!noattempt)
    {
        REQUIRE(probe.ArmTargetForCurrentThread(&probe));
        if (foreign)
        {
            std::atomic<bool> match{true};
            std::thread competitor([&] {
                probe.TargetGuardEntry(2,&probe,5,0,1); // wrong TLS must fail
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
            probe.TargetGuardEntry(2,&otherMethod,5,0,1);
            probe.MethodResult(2,probe.MatchesTargetOnCurrentThread(&otherMethod),false);
        }
        else if (race)
        {
            REQUIRE(probe.MatchesTargetOnCurrentThread(&probe));
            probe.TargetGuardEntry(2,&probe,5,0,1);
            probe.AtP6();
            probe.MethodResult(2,true,false);
        }
        else
        {
            REQUIRE(probe.MatchesTargetOnCurrentThread(&probe));
            if (!noentry)
                probe.TargetGuardEntry(2,&probe,
                    preterminal ? 9 : 5,
                    (preterminal || priorerror) ? 2 : 0,
                    mixedEntry ? 3 : (preterminal || priorerror || durableBefore) ? 2 : 1);
            probe.MethodResult(2,true,allow,
                (preterminal || durableBefore || mixedEntry || racedDenial) ? 1 : 0);
        }
    }
    if (race) REQUIRE(probe.TargetDecision()==3);
    // Every mock state is explicitly synthetic. The actual native VM branch
    // obtains state/first error independently from AssemblyShadow.
    const bool terminalNegative = deny || faulted || preterminal ||
        priorerror || noentry || durableBefore || mixedEntry || racedDenial;
    REQUIRE(R03_D5_SourceHostAutoConfigure(
        allow ? 6 : terminalNegative ? 9 : 5,
        unknownCanary ? -1 : allow ? 1 : 0, noattempt ? 0 : 1,
        terminalNegative ? 1 : 0, fault)==1);
    if (allow) REQUIRE(probe.ReleaseP5());
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
    REQUIRE(observedExit==((faulted||preterminal||priorerror||noentry||durableBefore||mixedEntry||racedDenial) ?
                           2 : allow ? 42 : deny ? 20 : 2));
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
    if (deny || preterminal || priorerror || noentry || durableBefore || mixedEntry || racedDenial)
        REQUIRE(guard.slot==5 && guard.a==2);
    if (allow) REQUIRE(guard.slot==5 && guard.a==1);
    if (racedDenial) REQUIRE(guard.d==1);
    if (unknownCanary) REQUIRE(end.b==0);
    if (race) REQUIRE(guard.slot==5 && guard.a==3);
    if (foreign || wrong || noattempt) REQUIRE(guard.magic==0 && guard.slot==0);
    if (faulted) REQUIRE(guard.slot==5 && guard.a==2);
    RawEvent entry{};
    REQUIRE(::pread(fd,&entry,sizeof entry,212+3*32)==
        static_cast<ssize_t>(sizeof entry));
    const bool actualEntry = !(foreign || wrong || noattempt || noentry);
    if (actualEntry)
    {
        REQUIRE(entry.slot==4 && entry.a==1 &&
            entry.b==(mixedEntry ? 3 : (preterminal || priorerror || durableBefore) ? 2 : 1));
        REQUIRE(entry.c==(preterminal ? 9 : 5));
        REQUIRE(entry.d==((preterminal || priorerror) ? 2 : 0));
    }
    else REQUIRE(entry.magic==0 && entry.slot==0);
    RawEvent release{};
    REQUIRE(::pread(fd,&release,sizeof release,212+5*32)==
        static_cast<ssize_t>(sizeof release));
    REQUIRE(release.slot==6);
    REQUIRE(release.c==(allow ? 1 : 0)); // native release only, never Join
    ::close(fd);
    std::printf("{\"result\":\"PassedD5NativeAutoCollectorHostOnly\",\"scenario\":\"%s\",\"expectedFailure\":%s,\"mockExitCode\":%d,\"realPlayerExecuted\":false,\"canaryFromRealVM\":false,\"firstErrorFromRealVM\":false}\n",test,faulted?"true":"false",observedExit);
    return 0;
}
