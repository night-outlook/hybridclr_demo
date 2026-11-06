// Host-only test stub; not real Unity/IL2CPP or HybridCLR execution.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iterator>
#include <string>
#include "vm/AssemblyShadow.h"
extern "C" int R03_IRW_Open(const char*,const char*,const char*,const char*,const char*);
extern "C" int R03_IRW_Seal(int,int,int,int,int,int);
extern "C" int R03_IRW_CaptureRecovery();
extern "C" int R03_IRW_Trace(int,int,int,int,int);

static const char* mode=nullptr;
il2cpp::vm::AssemblyShadowError il2cpp::vm::AssemblyShadow::GetRecoveryInfoJson(std::string& json) {
    const bool control=std::strcmp(mode,"control")==0;
    json = control
        ? R"({"schemaVersion":1,"enabled":true,"capabilityVersion":1,"stateCode":6,"state":"Committed","published":true,"abortAllowed":false,"dispositionCode":4,"disposition":"ActiveShadow","terminalFailureCode":0,"reason":"","retainedBytes":2048,"baselineEligibilityRequiresStartupValidation":false})"
        : R"({"schemaVersion":1,"enabled":true,"capabilityVersion":1,"stateCode":9,"state":"FailedAfterCommit","published":true,"abortAllowed":false,"dispositionCode":0,"disposition":"RestartRequired","terminalFailureCode":19,"reason":"Methods: controlled host initializer failure","retainedBytes":2048,"baselineEligibilityRequiresStartupValidation":false})";
    return AssemblyShadowError::Success;
}

extern "C" int R03_IRW_ReadPrepared(int* field,int* before,int* ready,int* mask,int* calls)
{
    if(std::strcmp(mode,"observer-reject")==0) {
        R03_IRW_Trace(400,-1,0,0,0); return -1;
    }
    *field=std::strcmp(mode,"field-mutated")==0?4:3;
    *before=3; *ready=1; *mask=15; *calls=1;
    R03_IRW_Trace(400,1,9,*field,*calls);
    R03_IRW_Trace(401,*before,*ready,*mask,0);
    return 1;
}
int main(int argc,char** argv)
{
    if(argc!=3) return 2;
    mode=argv[1];
    const char* const nonce="HostInitializerEvidenceRun000001";
    const char* const sha="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    const bool badId=std::strcmp(mode,"bad-run")==0;
    const int opened=R03_IRW_Open(argv[2],badId?"short":nonce,"HOST-INIT",
        std::strcmp(mode,"control")==0?"initializer-control":"initializer-failure",sha);
    if(std::strcmp(mode,"preexisting")==0 || badId) return opened==1?10:0;
    if(opened!=1) return 11;
    const int second=R03_IRW_Open(argv[2],nonce,"HOST-INIT","initializer-failure",sha);
    if(second==1) return 12;
    const bool control=std::strcmp(mode,"control")==0;
    const int nativeCommit=control?0:19;
    const int nativeState=control?6:9;
    // Synthetic observer and managed phases, only for C++11 writer tests.
    // NOT a Unity callback or an actual Shadow Commit.
    R03_IRW_Trace(299,1,0,0,0);
    R03_IRW_Trace(300,1,3,15,1);
    R03_IRW_Trace(190,1,0,0,0);
    R03_IRW_Trace(191,nativeCommit,0,0,0);
    R03_IRW_Trace(201,0,nativeState,nativeCommit,0);
    R03_IRW_Trace(205,!control,nativeCommit,nativeState,0);
    if (R03_IRW_CaptureRecovery()!=1) return 17;
    R03_IRW_Trace(231,1,nativeCommit,nativeState,0);
    const int result=R03_IRW_Seal(control?0:19,
       std::strcmp(mode,"wrong-state")==0?6:(control?6:9),
       1,1,control?0:1,std::strcmp(mode,"canary-executed")==0?1:0);
    const bool expectedFailure=std::strcmp(mode,"wrong-state")==0 ||
       std::strcmp(mode,"field-mutated")==0 ||
       std::strcmp(mode,"observer-reject")==0 ||
       std::strcmp(mode,"canary-executed")==0;
    if(expectedFailure) return result==1?13:0;
    if(result!=1) return 14;
    std::ifstream in(argv[2]);
    if(!in.good()) return 15;
    const std::string payload((std::istreambuf_iterator<char>(in)),
        std::istreambuf_iterator<char>());
    if(payload.find("\"runtimeAcceptance\":false")==std::string::npos ||
       payload.find("\"preparedField\":3")==std::string::npos ||
       payload.find(control?"\"commitReturn\":0":"\"commitReturn\":19")==std::string::npos)
       return 16;
    return 0;
}
