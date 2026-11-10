// Pure host integration: owned TypeKeys + rows + ACTUAL native FrozenExecutionRecord
// and R02 suffix. All metadata/counters are synthetic, never a VM-source proof.
#include "BoundedOwnedExecutionFrozenRecordBridge.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <new>
#include <sstream>
#include <string>

static bool protectedRegion=false;
static unsigned protectedAllocations=0,assertions=0;
void* operator new(std::size_t n){
    if(protectedRegion){++protectedAllocations;std::abort();}
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
namespace frozen=il2cpp::vm::assembly_shadow_frozen_execution_record;
namespace r02=il2cpp::vm::assembly_shadow_r02;
static void Check(bool ok){++assertions;if(!ok)std::abort();}
static ByteView V(const char* p){return ByteView{p,std::strlen(p)};}

struct MockCounters {
    int DiagnosticsLevel() const noexcept{return 2;}
    size_t ThreadCapacity() const noexcept{return r02::ObservationCounters::kThreadCapacity;}
    size_t MemoTlsBytesPerThread() const noexcept{return 512;}
    size_t RetainedBytes() const noexcept{return 4096;}
    uint64_t Read(r02::Metric metric,std::memory_order=std::memory_order_relaxed) const noexcept {
        switch(metric) {
            case r02::Metric::MethodChecks: return 25;
            case r02::Metric::ShadowMethodChecks: return 7;
            case r02::Metric::RejectedBaselineMethods: return 2;
            case r02::Metric::BaselineCctors: return 3;
            case r02::Metric::ShadowCctors: return 1;
            case r02::Metric::Transformations: return 5;
            case r02::Metric::ShadowTransformations: return 2;
            default: return 0;
        }
    }
    uint64_t DroppedThreads() const noexcept{return 0;}
    bool Saturated() const noexcept{return false;}
    const char* Coverage() const noexcept{return "BoundedComplete";}
};
struct Output {char* storage=nullptr;size_t cap=0,bytes=0;};
static bool Write(void* context,const char* data,size_t n) noexcept {
    auto& out=*static_cast<Output*>(context);
    if(n>out.cap-out.bytes)return false;
    if(n)std::memcpy(out.storage+out.bytes,data,n);
    out.bytes+=n;return true;
}

static void Seed(Capture& k,const char* name) {
    Check(k.Begin(V("Assembly-CSharp"),true,false,false));
    Check(k.AddDeclaration(V("Demo"),V(name),0));
    Check(k.Seal());
}
static void Populate(rows::Rows& input) {
    Capture a,b;
    Seed(a,"A");Seed(b,"B");
    rows::Flags fa{},fb{};
    fa.interpreterShadow=true;fa.physicalInterpreter=true;
    fa.isActive=true;fa.cctorStarted=true;fa.staticStorageAvailable=true;
    fb.cctorFinished=true;fb.hasInitializationException=true;
    Check(input.Begin(2));
    Check(input.Add(101,rows::Source::Candidate,V("Methods"),b,V(""),fb));
    Check(input.Add(5,rows::Source::ActiveShadow,V("Assembly-CSharp"),a,V("0x123"),fa));
    Check(input.Seal());
    Check(!a.Revoke()&&!b.Revoke());
}
static void Run() {
    r02::Snapshot snapshot{};r02::SnapshotReceipt sr{};
    Check(r02::Snapshot::TryCaptureFrom(MockCounters{},snapshot,sr));
    Check(snapshot.Complete() && sr.observedReadFenceStable);
    auto* input=new rows::Rows();
    Populate(*input);
    auto* record=new frozen::Record();
    frozen::Identity id{};
    id.stateCode=6;id.state=diag::Quoted("Committed");id.generation=9;

    // Reference is the actual versioned native shared serializer over the
    // same immutable rows and R02 value, but with an allocating ostream.
    exec::Header h{};
    h.stateCode=6;h.state="Committed";h.generation=9;
    h.methodChecks=snapshot.Read(r02::Metric::MethodChecks);
    h.shadowMethodChecks=snapshot.Read(r02::Metric::ShadowMethodChecks);
    h.rejectedBaselineMethods=snapshot.Read(r02::Metric::RejectedBaselineMethods);
    h.baselineClassCctorStarted=snapshot.Read(r02::Metric::BaselineCctors);
    h.shadowClassCctorStarted=snapshot.Read(r02::Metric::ShadowCctors);
    h.interpreterTransformations=snapshot.Read(r02::Metric::Transformations);
    h.shadowInterpreterTransformations=snapshot.Read(r02::Metric::ShadowTransformations);
    h.droppedClassObservations=snapshot.Read(r02::Metric::DroppedClasses);
    std::ostringstream reference;
    exec::Begin(reference,h);
    Check(bridge::AppendClassRows(reference,*input));
    exec::EndClasses(reference);
    Check(r02::AppendFrozenDiagnostics(reference,snapshot));
    reference<<'}';
    const std::string expected=reference.str();
    Check(expected.find("\"typeKey\":\"type(15:assembly-csharp/4:Demo/1:A@0)\"")!=std::string::npos);
    Check(expected.find("\"typeKey\":\"type(15:assembly-csharp/4:Demo/1:B@0)\"")!=std::string::npos);
    Check(expected.find("\"memoryAccountingAvailable\":true")!=std::string::npos);

    // Source/record storage was constructed while healthy. From Begin through
    // Freeze/Emit, exercise the pure native writer with new/delete forbidden.
    protectedRegion=true;
    const bool started=record->Begin(id,snapshot,input->Count());
    const bool added=started&&bridge::AppendToFrozenRecord(*record,*input);
    const bool sealed=added&&record->Freeze();
    protectedRegion=false;
    Check(started&&added&&sealed&&record->Complete());
    Check(record->Bytes()==expected.size());
    Check(std::memcmp(record->Data(),expected.data(),expected.size())==0);

    char received[32768]{};
    Output out{};out.storage=received;out.cap=sizeof received;
    protectedRegion=true;
    const auto emission=record->EmitTo(diag::Sink{&out,Write},sizeof received);
    protectedRegion=false;
    Check(emission.complete&&emission.bytesAccepted==out.bytes);
    Check(out.bytes==expected.size());
    Check(std::memcmp(received,expected.data(),out.bytes)==0);
    const auto shortEmit=record->EmitTo(diag::Sink{&out,Write},expected.size()-1);
    Check(!shortEmit.complete&&shortEmit.error==diag::WriteError::ByteLimit);

    // Unadmitted, unsealed owned rows are never converted to a source of
    // complete finalExecutionDiagnostics. Failures revoke frozen bytes.
    auto* rejected=new frozen::Record();
    rows::Rows unsealed;
    Check(rejected->Begin(id,snapshot,1));
    Check(!bridge::AppendToFrozenRecord(*rejected,unsealed));
    Check(!rejected->Complete()&&rejected->Data()==nullptr);
    delete rejected;

    auto* bad=new frozen::Record();
    r02::Snapshot missing{}; // not a valid independently captured R02 value
    Check(!bad->Begin(id,missing,0) && !bad->Complete());
    delete bad;
    delete record;
    delete input;
}
int main() {
    Run();
    Check(protectedAllocations==0);
    std::printf("{\"kind\":\"R03B2NativeFrozenExecutionRecordHost\","
        "\"result\":\"PassedOwnedRowsAndFrozenR02Only\","
        "\"assertions\":%u,\"protectedAllocations\":%u,"
        "\"realPhysicalClassProven\":false,"
        "\"completeFinalExecutionDiagnostics\":false,"
        "\"nativeV2TransportImplemented\":false,\"runtimeAcceptance\":false}\n",
        assertions,protectedAllocations);
}
