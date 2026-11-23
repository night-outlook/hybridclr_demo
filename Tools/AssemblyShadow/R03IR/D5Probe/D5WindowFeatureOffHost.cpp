#include <cstdint>
#include <cstdio>
extern "C" int32_t R03_D5_WindowProtocolVersion();
extern "C" int32_t R03_D5_ArmP5Window(int32_t);
extern "C" int32_t R03_D5_ReleaseP5Window();
extern "C" int32_t R03_D5_ReadP5Window(int32_t*,int32_t);
extern "C" int32_t R03_D5_ReceiptOpen(const char*,const char*,const char*,const char*);
extern "C" int32_t R03_D5_ReceiptEvent(int32_t,int32_t,int32_t,int32_t,int32_t);
extern "C" int32_t R03_D5_BindKeepCanary(void*);
extern "C" int32_t R03_D5_BeginKeepAttempt();
extern "C" int32_t R03_D5_ReceiptSeal(int32_t,int32_t,int32_t,int32_t);
int main()
{
    int32_t fields[11]={};
    if(R03_D5_WindowProtocolVersion()!=0 ||
       R03_D5_ArmP5Window(50)!=0 ||
       R03_D5_ReleaseP5Window()!=0 ||
       R03_D5_ReadP5Window(fields,11)!=0 ||
       R03_D5_ReceiptOpen(nullptr,nullptr,nullptr,nullptr)!=0 ||
       R03_D5_ReceiptEvent(1,0,0,0,0)!=0 ||
       R03_D5_BindKeepCanary(nullptr)!=0 ||
       R03_D5_BeginKeepAttempt()!=0 ||
       R03_D5_ReceiptSeal(0,0,0,0)!=0) return 1;
    for(int32_t x:fields)if(x!=0)return 2;
    std::puts("{\"schema\":\"R03D5WindowOffHostV1\",\"result\":\"PassedNoTestProbeInFeatureOffSourceHostOnly\",\"unityOrPlayerExecuted\":false}");
    return 0;
}
