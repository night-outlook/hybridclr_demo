// Source/host only: real native ExecutionSerializer + new bounded owned rows.
// No IL2CPP Player, VM metadata reader, end-to-end V2 source or epoch proof.
#include "BoundedOwnedExecutionSerializerBridge.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <new>
#include <sstream>
#include <string>

static bool guard=false;
static unsigned allocations=0,assertions=0;
void* operator new(std::size_t n){
    if(guard){++allocations;std::abort();}
    if(void* p=std::malloc(n?n:1))return p;
    throw std::bad_alloc();
}
void* operator new[](std::size_t n){return ::operator new(n);}
void operator delete(void* p) noexcept{std::free(p);}
void operator delete[](void* p) noexcept{std::free(p);}
void operator delete(void* p,std::size_t) noexcept{std::free(p);}
void operator delete[](void* p,std::size_t) noexcept{std::free(p);}

using namespace r03_b2_owned_definition_key;
namespace rows=r03_b2_owned_execution_rows;
namespace bridge=r03_b2_owned_execution_bridge;
namespace diag=il2cpp::vm::assembly_shadow_diagnostic;
namespace exec=il2cpp::vm::assembly_shadow_execution_diagnostic;
static void Need(bool c){++assertions;if(!c)std::abort();}
static ByteView V(const char* s){return ByteView{s,std::strlen(s)};}
struct Buffer { char* bytes=nullptr;size_t capacity=0,used=0;};
static bool Sink(void* ctx,const char* text,size_t n) noexcept {
    auto& b=*static_cast<Buffer*>(ctx);
    if(n>b.capacity-b.used)return false;
    if(n)std::memcpy(b.bytes+b.used,text,n);
    b.used+=n;
    return true;
}
static void Seed(Capture& key,const char* name){
    Need(key.Begin(V("Assembly-CSharp"),true,false,false));
    Need(key.AddDeclaration(V("Demo"),V(name),0));
    Need(key.Seal());
}
static void Run(){
    Capture monster,hero;Seed(monster,"Monster");Seed(hero,"Hero");
    rows::Rows input;
    rows::Flags monsterFlags{},heroFlags{};
    monsterFlags.interpreterShadow=true;
    monsterFlags.physicalInterpreter=true;
    monsterFlags.cctorStarted=true;
    monsterFlags.cctorFinished=true;
    monsterFlags.hasInitializationException=false;
    monsterFlags.staticStorageAvailable=true;
    heroFlags.isActive=true;heroFlags.pointerDetailsAvailable=true;
    Need(input.Begin(2));
    Need(input.Add(420,rows::Source::ActiveShadow,V("Methods"),monster,V(""),monsterFlags));
    Need(input.Add(8,rows::Source::Candidate,V("Assembly-CSharp"),hero,V("0xabc"),heroFlags));
    Need(input.Seal());
    Need(!monster.Revoke()&&!hero.Revoke()); // source strings no longer exist

    exec::Header h{};
    h.stateCode=6;h.state="Committed";h.generation=4;
    h.methodChecks=17;h.shadowMethodChecks=7;h.rejectedBaselineMethods=2;
    h.baselineClassCctorStarted=3;h.shadowClassCctorStarted=1;
    h.interpreterTransformations=5;h.shadowInterpreterTransformations=2;
    h.droppedClassObservations=0;
    std::ostringstream legacy;
    exec::Begin(legacy,h);
    Need(bridge::AppendClassRows(legacy,input));
    exec::EndClasses(legacy);
    const std::string expected=legacy.str();
    Need(expected.find("type(15:assembly-csharp/4:Demo/4:Hero@0)")!=std::string::npos);
    Need(expected.find("type(15:assembly-csharp/4:Demo/7:Monster@0)")!=std::string::npos);
    Need(expected.find("\"staticStoragePointer\":\"0xabc\"")!=std::string::npos);
    Need(expected.find("\"shadowMethodChecks\":7")!=std::string::npos);
    const auto first=expected.find("\"logicalAssembly\":\"Assembly-CSharp\"");
    const auto second=expected.find("\"logicalAssembly\":\"Methods\"");
    Need(first!=std::string::npos && second!=std::string::npos && first<second);

    char owned[32768]{};
    Buffer b{};b.bytes=owned;b.capacity=sizeof owned;
    diag::Writer fixed(diag::Sink{&b,Sink},sizeof owned);
    guard=true;
    exec::Begin(fixed,h);
    const bool rowsOK=bridge::AppendClassRows(fixed,input);
    exec::EndClasses(fixed);
    const auto receipt=fixed.Finish();
    guard=false;
    Need(rowsOK && receipt.complete);
    Need(receipt.bytesAccepted==b.used && b.used==expected.size());
    Need(std::memcmp(owned,expected.data(),expected.size())==0);

    char tiny[15]{};
    Buffer tooShort{};tooShort.bytes=tiny;tooShort.capacity=sizeof tiny;
    diag::Writer blocked(diag::Sink{&tooShort,Sink},sizeof tiny);
    exec::Begin(blocked,h);
    Need(bridge::AppendClassRows(blocked,input));
    exec::EndClasses(blocked);
    Need(!blocked.Finish().complete); // no successful truncated output

    rows::Rows unsealed;
    diag::Writer failedSource(diag::Sink{&b,Sink},sizeof owned);
    const size_t before=b.used;
    Need(!bridge::AppendClassRows(failedSource,unsealed));
    Need(before==b.used);
}
int main(){
    Run();
    Need(allocations==0);
    std::printf("{\"kind\":\"R03B2RealNativeExecutionSerializerHost\","
        "\"result\":\"PassedOwnedRowsToNativeSerializerOnly\","
        "\"assertions\":%u,\"protectedAllocations\":%u,"
        "\"sourceBytesFromRealVm\":false,"
        "\"completeNonemptyExecutionDiagnostics\":false,"
        "\"runtimeAcceptance\":false,\"nativeV2TransportImplemented\":false}\n",
        assertions,allocations);
}
