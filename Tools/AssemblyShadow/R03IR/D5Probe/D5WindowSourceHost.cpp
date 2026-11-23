// D5-B source-host test of exact native window header and test-only overlay.
// This is NOT Unity/IL2CPP Player, MethodInfo execution, or GC/ABI proof.
#include "vm/AssemblyShadowD5WindowProbe.h"
#include <atomic>
#include <cstdlib>
#include <cassert>
#include <cstdio>
#include <cstring>
#include <thread>
#include <chrono>
#include <cstdint>
using il2cpp::vm::assembly_shadow_d5::WindowProbe;
using il2cpp::vm::assembly_shadow_d5::WindowPhase;
extern "C" void* D5ProbeOtherTU();
extern "C" int32_t R03_D5_WindowProtocolVersion();
extern "C" int32_t R03_D5_ArmP5Window(int32_t);
extern "C" int32_t R03_D5_ReleaseP5Window();
extern "C" int32_t R03_D5_ReadP5Window(int32_t*,int32_t);

static unsigned assertions=0;
#define REQUIRE(x) do {++assertions;if(!(x)){std::fprintf(stderr,"D5WindowHost FAIL line %d %s\n",__LINE__,#x);return 1;}}while(0)
int main(int argc,char**argv)
{
    if(argc!=2)return 2;
    const char* c=argv[1];
    auto& w=WindowProbe::Instance();
    REQUIRE(D5ProbeOtherTU()==&w);
    int32_t raw[11]={};
    REQUIRE(R03_D5_ReadP5Window(nullptr,11)==-2);
    REQUIRE(R03_D5_ReadP5Window(raw,10)==-2);
    REQUIRE(R03_D5_ReadP5Window(raw,11)==1);
    REQUIRE(raw[0]==1&&raw[1]==0);
    REQUIRE(R03_D5_WindowProtocolVersion()==1);

    if(!std::strcmp(c,"unarmed"))
    {
        w.AtP5();
        w.HoldP5Bounded();
        w.AtP6();
        w.Complete();
        REQUIRE(R03_D5_ReadP5Window(raw,11)==1);
        REQUIRE(raw[1]==0&&raw[3]==0&&raw[4]==0);
        REQUIRE(w.MethodBegin()==0);
        REQUIRE(R03_D5_ReleaseP5Window()==-1);
    }
    else if(!std::strcmp(c,"denied") || !std::strcmp(c,"allowed"))
    {
        const bool allow=!std::strcmp(c,"allowed");
        REQUIRE(R03_D5_ArmP5Window(900)==1);
        REQUIRE(R03_D5_ArmP5Window(500)==-1);
        std::atomic<bool> workerDone{false};
        std::thread t([&]{
            int32_t stage=0;
            while((stage=w.MethodBegin())!=2)
                std::this_thread::yield();
            const bool armed=w.ArmTargetForCurrentThread(&w);
            const bool matched=w.MatchesTargetOnCurrentThread(&w);
            if(!armed || !matched)std::abort();
            w.MethodResult(stage,matched,allow);
            workerDone.store(true,std::memory_order_release);
            R03_D5_ReleaseP5Window();
        });
        w.AtP5();
        w.HoldP5Bounded();
        REQUIRE(workerDone.load(std::memory_order_acquire));
        w.AtP6();
        w.Complete();
        t.join();
        REQUIRE(R03_D5_ReadP5Window(raw,11)==1);
        REQUIRE(raw[1]==4&&raw[2]==1&&raw[3]==1&&raw[4]==1);
        REQUIRE(raw[5]==1&&raw[6]==0&&raw[7]==1);
        REQUIRE(raw[8]==(allow?1:0)&&raw[9]==(allow?0:1)&&raw[10]==0);
    }
    else if(!std::strcmp(c,"timeout"))
    {
        REQUIRE(R03_D5_ArmP5Window(20)==1);
        w.AtP5();
        w.HoldP5Bounded();
        REQUIRE(R03_D5_ReadP5Window(raw,11)==1);
        REQUIRE(raw[6]==1&&raw[1]==2);
        w.AtP6();
        w.Complete();
        REQUIRE(raw[5]==0);
    }
    else if(!std::strcmp(c,"raced"))
    {
        REQUIRE(R03_D5_ArmP5Window(100)==1);
        w.AtP5();
        const int32_t started=w.MethodBegin();
        REQUIRE(w.ArmTargetForCurrentThread(&w));
        const bool matched=w.MatchesTargetOnCurrentThread(&w);
        w.AtP6();
        w.MethodResult(started,matched,true);
        REQUIRE(R03_D5_ReadP5Window(raw,11)==1);
        REQUIRE(raw[7]==0&&raw[8]==0&&raw[10]==1);
    }
    else if(!std::strcmp(c,"foreign"))
    {
        REQUIRE(w.Arm(100)==true);
        w.AtP5();
        REQUIRE(w.ArmTargetForCurrentThread(&w));
        std::atomic<bool> otherMatched{true};
        std::thread other([&] {
            const bool match=w.MatchesTargetOnCurrentThread(&w);
            otherMatched.store(match,std::memory_order_release);
            w.MethodResult(2,match,false);
        });
        other.join();
        REQUIRE(!otherMatched.load(std::memory_order_acquire));
        REQUIRE(w.Read().shadowMethodAttemptsInP5==0);
        const bool match=w.MatchesTargetOnCurrentThread(&w);
        REQUIRE(match);
        w.MethodResult(2,match,true);
        REQUIRE(w.Read().shadowMethodAttemptsInP5==1);
        REQUIRE(w.TargetDecision()==1);
    }
    else if(!std::strcmp(c,"wrongmethod"))
    {
        REQUIRE(w.Arm(100)==true);
        w.AtP5();
        int otherMethod=0;
        REQUIRE(w.ArmTargetForCurrentThread(&w));
        REQUIRE(!w.MatchesTargetOnCurrentThread(&otherMethod));
        w.MethodResult(2,w.MatchesTargetOnCurrentThread(&otherMethod),true);
        REQUIRE(w.Read().shadowMethodAttemptsInP5==0);
        REQUIRE(w.MatchesTargetOnCurrentThread(&w));
        w.MethodResult(2,true,false);
        REQUIRE(w.TargetDecision()==2);
        REQUIRE(w.Read().shadowMethodDeniedInP5==1);
    }
    else if(!std::strcmp(c,"duplicate"))
    {
        REQUIRE(w.Arm(100)==true);
        w.AtP5();
        REQUIRE(w.ArmTargetForCurrentThread(&w));
        REQUIRE(!w.ArmTargetForCurrentThread(&w));
        REQUIRE(w.MatchesTargetOnCurrentThread(&w));
        w.MethodResult(2,true,false);
        REQUIRE(!w.MatchesTargetOnCurrentThread(&w));
        w.MethodResult(2,true,true);
        REQUIRE(w.TargetArmCount()==1);
        REQUIRE(w.Read().shadowMethodAttemptsInP5==1);
    }
    else if(!std::strcmp(c,"early_terminal"))
    {
        REQUIRE(w.Arm(200));
        w.AtP5();
        const int32_t begun=w.MethodBegin();
        REQUIRE(w.ArmTargetForCurrentThread(&w));
        // Same test-only sequence as AssemblyShadow.cpp's early-return
        // branch; no metadata/VM allocation is performed here.
        w.MethodResult(begun,w.MatchesTargetOnCurrentThread(&w),false);
        REQUIRE(w.TargetDecision()==2);
        REQUIRE(w.Read().shadowMethodDeniedInP5==1);
        REQUIRE(!w.MatchesTargetOnCurrentThread(&w));
        // A second/baseline attempt cannot create a second denied event.
        w.MethodResult(begun,w.MatchesTargetOnCurrentThread(&w),false);
        REQUIRE(w.Read().shadowMethodAttemptsInP5==1);
    }
    else if(!std::strcmp(c,"canary_happens_before"))
    {
        REQUIRE(w.Arm(200));
        w.AtP5();
        REQUIRE(!w.HasWorkerCompletedP5Acquire());
        int32_t stable=0;
        std::thread writer([&] {
            stable=42;
            // A release CAS publishes the ordinary field write.
            if(!w.ReleaseP5()) std::abort();
        });
        while(!w.HasWorkerCompletedP5Acquire())
            std::this_thread::yield();
        REQUIRE(stable==42); // acquire synchronizes with writer
        writer.join();
        REQUIRE(w.Read().releaseCount==1);
    }
    else if(!std::strcmp(c,"invalid"))
    {
        REQUIRE(R03_D5_ArmP5Window(0)==-1);
        REQUIRE(R03_D5_ArmP5Window(2001)==-1);
        REQUIRE(R03_D5_ArmP5Window(20)==1);
        REQUIRE(R03_D5_ArmP5Window(20)==-1);
        REQUIRE(R03_D5_ReadP5Window(raw,11)==1&&raw[1]==1);
    }
    else return 2;
    std::printf("{\"schema\":\"R03D5WindowSourceHostV1\",\"case\":\"%s\",\"result\":\"PassedExactNativeWindowHeaderAndOverlayHostOnly\",\"assertions\":%u,\"actualProductionMethodInfoExercised\":false,\"unityOrPlayerExecuted\":false,\"C10RealPlayerPassed\":false}\n",c,assertions);
    return 0;
}
