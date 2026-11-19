// R03 B2 D3 exact-source host. Actual Runtime.cpp + Codec.h and literal
// native PublishActive/phase callbacks; fake VM ownership and staging adapter.
// This DOES NOT test Unity/GC/Player or complete native translation units.
#include "hybridclr/metadata/InterpreterMetadataIndexRuntime.h"
#include "hybridclr/metadata/AssemblyShadowBridge.h"
#include "AssemblyShadowPublicationD3Decision.h"

#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <thread>
#include <vector>

namespace hybridclr { namespace metadata {
namespace {
std::atomic<bool> vmVisible{false};
uint32_t shadowIds[2] = {};
InterpreterImage* shadowImages[2] = {};
}
InterpreterImage* AssemblyShadowBridge::GetPrivateImage(uint32_t)
{
    return nullptr; // construction scope owns all private test associations
}
bool AssemblyShadowBridge::IsPublicImage(uint32_t imageId, InterpreterImage* image)
{
    if (!vmVisible.load(std::memory_order_acquire)) return false;
    for (unsigned i=0;i<2;++i)
        if (shadowIds[i]==imageId && shadowImages[i]==image) return true;
    return false;
}
}}
using Runtime=hybridclr::metadata::InterpreterMetadataIndexRuntime;
using Image=hybridclr::metadata::InterpreterImage;
using Error=Runtime::Error;
namespace phase=il2cpp::vm::assembly_shadow_publication;

static unsigned checks=0;
static void Check(bool b,const char* e,int line)
{
    ++checks;
    if (!b) {std::fprintf(stderr,"D3 HOST FAIL line %d: %s\n",line,e);std::abort();}
}
#define CHECK(b) Check(bool(b),#b,__LINE__)

// Only the types needed by exact extracted native function bodies are
// represented here. Actual Callback definitions are included below.
namespace il2cpp { namespace vm { namespace {
struct Candidate { struct {bool present=false;} firstUse; };
struct StagedAssembly {bool published=false;};
struct ClosureMember {Candidate* candidate;StagedAssembly* staged;};
struct Transaction {std::vector<ClosureMember> closure;};
struct ActiveSnapshot {unsigned id=42;};
std::atomic_flag s_usageLock=ATOMIC_FLAG_INIT;
std::atomic<const ActiveSnapshot*> s_active{nullptr};
bool poisonGroupCallback=false;
bool ObserveCodecAttempt(void*) noexcept;
bool ObserveRuntimeGroupPublished(void*) noexcept;
bool BeforeCodecThenSeal(void* opaque) noexcept;

struct InterpreterAssembly
{
    static bool PublishStagedImagesBatch(const std::vector<uint32_t>& ids,
        const Runtime::PublicationObserver* observer)
    {
        // Test shim for the source-verified StagedAssembly.cpp ->
        // InterpreterImage.cpp forwarding, not a compiled staged assembly TU.
        Runtime::PublicationObserver wrapped=*observer;
        if (poisonGroupCallback)
            wrapped.beforeCodec=BeforeCodecThenSeal;
        return !ids.empty() && Runtime::PublishBatch(
            ids.data(),ids.size(),&wrapped)==Error::None;
    }
};
}}}

#include "D3ExactNativeCallbacks.inc"

namespace il2cpp { namespace vm { namespace {
bool BeforeCodecThenSeal(void* opaque) noexcept
{
    if (!ObserveCodecAttempt(opaque)) return false;
    Publication& p=*static_cast<Publication*>(opaque);
    p.phaseReceipt->MarkTerminal(phase::Reason::NativePublicationFailure);
    return true; // Runtime must then observe afterGroup returning false.
}
}}}
using namespace il2cpp::vm;

static bool UsageHeld()
{
    bool wasHeld=s_usageLock.test_and_set(std::memory_order_acquire);
    if (!wasHeld) s_usageLock.clear(std::memory_order_release);
    return wasHeld;
}
struct Marker {uint32_t value;};
struct Fixture
{
    Marker markers[2]={{81},{82}};
    Image* images[2]={
        reinterpret_cast<Image*>(&markers[0]),
        reinterpret_cast<Image*>(&markers[1]),
    };
    std::vector<Runtime::Reservation> reservations;
    uint32_t ids[2]={};
    Candidate candidate;
    StagedAssembly staged;
    Transaction transaction;
    ActiveSnapshot snapshot;
    phase::PublicationPhaseReceipt receipt;
    Publication publication{};

    explicit Fixture(bool finalizeSecond=true)
    {
        CHECK(Runtime::ReserveImages(2,reservations)==Error::None);
        CHECK(reservations.size()==2);
        for(int i=0;i<2;++i)
        {
            ids[i]=reservations[i].imageId;
            {
                Runtime::ScopedConstruction construction(ids[i],images[i],true);
                if (i==0||finalizeSecond)
                    CHECK(Runtime::Finalize(ids[i],1)==Error::None);
            }
            hybridclr::metadata::shadowIds[i]=ids[i];
            hybridclr::metadata::shadowImages[i]=images[i];
        }
        transaction.closure.push_back({&candidate,&staged});
        publication.transaction=&transaction;
        publication.snapshot=&snapshot;
        publication.phaseReceipt=&receipt;
        publication.imageIndices.assign(ids,ids+2);
        CHECK(Runtime::GetPublishedImage(ids[0])==nullptr);
        CHECK(Runtime::GetPublishedImage(ids[1])==nullptr);
    }
    bool Begin(){return TryBeginPublication(&publication);}
    bool Publish(){return PublishActive(&publication);}
    void CheckNativeClean()
    {
        CHECK(!UsageHeld());
        CHECK(!publication.usageHeld);
    }
    void CheckNoVMActive()
    {
        CHECK(s_active.load(std::memory_order_acquire)==nullptr);
        CHECK(!staged.published);
        CHECK(Runtime::GetPublishedImage(ids[0])==nullptr);
    }
    void SetMockVmVisible()
    {
        hybridclr::metadata::vmVisible.store(true,std::memory_order_release);
    }
};

static void UsedBeforeAppend()
{
    Fixture f;
    f.candidate.firstUse.present=true;
    CHECK(!f.Begin());
    f.CheckNativeClean();
    CHECK(f.publication.used==&f.candidate);
    CHECK(phase::ClassifyFailedNativeBatch(f.receipt,true,false,false)==
          phase::D3Disposition::ProvenUsedRejection);
    CHECK(f.receipt.Read().phase==phase::Phase::Prepared);
    CHECK(f.receipt.Read().outcome==phase::Outcome::RejectedBeforeCodec);
    CHECK(!f.receipt.RestartRequired());
    f.CheckNoVMActive();
}
static void RuntimePrecheckFailure()
{
    Fixture f;
    CHECK(f.Begin());
    f.publication.imageIndices[1]=0; // rejected before actual Codec
    CHECK(!f.Publish());
    f.CheckNativeClean();
    CHECK(f.publication.runtimePublicationFailed);
    CHECK(f.receipt.Read().phase==phase::Phase::RegistriesAppended);
    CHECK(phase::ClassifyFailedNativeBatch(f.receipt,false,false,true)==
          phase::D3Disposition::TerminalRestartRequired);
    CHECK(f.receipt.Read().reason==phase::Reason::MissingCleanupProof);
    CHECK(f.receipt.RestartRequired());
    f.CheckNoVMActive();
}
static void CodecValidationError()
{
    Fixture f(false); // real Codec validation refuses unfinalized member
    CHECK(f.Begin());
    CHECK(!f.Publish());
    f.CheckNativeClean();
    CHECK(f.publication.runtimePublicationFailed);
    CHECK(f.receipt.Read().phase==phase::Phase::CodecAttempted);
    CHECK(phase::ClassifyFailedNativeBatch(f.receipt,false,false,true)==
          phase::D3Disposition::TerminalRestartRequired);
    CHECK(f.receipt.Read().reason==phase::Reason::CodecOutcomeUnknown);
    CHECK(f.receipt.RestartRequired());
    f.CheckNoVMActive();
}
static void RealRuntimeSuccess()
{
    Fixture f;
    CHECK(f.Begin());
    CHECK(f.Publish());
    f.CheckNativeClean();
    CHECK(f.receipt.Read().phase==phase::Phase::RuntimeGroupPublished);
    CHECK(f.receipt.Read().outcome==phase::Outcome::InProgress);
    CHECK(f.staged.published);
    CHECK(s_active.load(std::memory_order_acquire)==&f.snapshot);
    // Codec and Runtime group are real; VM visibility bridge is test-owned.
    CHECK(Runtime::GetPublishedImage(f.ids[0])==nullptr);
    f.SetMockVmVisible();
    CHECK(Runtime::GetPublishedImage(f.ids[0])==f.images[0]);
    CHECK(Runtime::GetPublishedImage(f.ids[1])==f.images[1]);
}
static void GroupPublishedButCallbackFails()
{
    Fixture f;
    CHECK(f.Begin());
    poisonGroupCallback=true;
    CHECK(!f.Publish()); // group ACTIVE, but native snapshot NOT published
    f.CheckNativeClean();
    CHECK(f.publication.runtimePublicationFailed);
    CHECK(f.receipt.Read().phase==phase::Phase::CodecAttempted);
    CHECK(f.receipt.RestartRequired());
    CHECK(f.receipt.Read().reason==phase::Reason::NativePublicationFailure);
    CHECK(phase::ClassifyFailedNativeBatch(f.receipt,false,false,true)==
          phase::D3Disposition::TerminalRestartRequired);
    f.CheckNoVMActive();
    f.SetMockVmVisible();
    // Codec + real group are ALREADY published; returning false cannot undo.
    CHECK(Runtime::GetPublishedImage(f.ids[0])==f.images[0]);
    CHECK(Runtime::Abort(f.ids[0])==Error::InvalidState);
}
static void CodecAttemptCannotBeUsedDenial()
{
    Fixture f(false);
    CHECK(f.Begin());
    CHECK(!f.Publish());
    f.CheckNativeClean();
    CHECK(phase::ClassifyFailedNativeBatch(f.receipt,true,false,false)==
          phase::D3Disposition::TerminalRestartRequired);
    CHECK(f.receipt.RestartRequired());
    CHECK(f.receipt.Read().reason==phase::Reason::CodecOutcomeUnknown);
}
static void BadObserverFailsBeforeCodec()
{
    Fixture f;
    Runtime::PublicationObserver incomplete={nullptr,ObserveRuntimeGroupPublished,
                                               &f.publication};
    CHECK(Runtime::PublishBatch(f.ids,2,&incomplete)==Error::InvalidArgument);
    CHECK(f.receipt.Read().phase==phase::Phase::Prepared);
    CHECK(Runtime::GetPublishedImage(f.ids[0])==nullptr);
}
int main(int argc,char** argv)
{
    if(argc!=2){std::fprintf(stderr,"Provide exact D3 scenario\n");return 2;}
    const char* name=argv[1];
    if(!std::strcmp(name,"used-precodec"))UsedBeforeAppend();
    else if(!std::strcmp(name,"runtime-precheck"))RuntimePrecheckFailure();
    else if(!std::strcmp(name,"codec-validation"))CodecValidationError();
    else if(!std::strcmp(name,"runtime-success"))RealRuntimeSuccess();
    else if(!std::strcmp(name,"post-group-rejection"))GroupPublishedButCallbackFails();
    else if(!std::strcmp(name,"attempt-not-used"))CodecAttemptCannotBeUsedDenial();
    else if(!std::strcmp(name,"bad-observer"))BadObserverFailsBeforeCodec();
    else{std::fprintf(stderr,"Unknown D3 scenario\n");return 2;}
    std::printf("{\"schema\":\"R03B2D3ActualRuntimeHostV1\",\"result\":\"PassedExactRuntimeAndNativeCallbacksHostOnly\","
        "\"scenario\":\"%s\",\"checks\":%u,\"actualRuntimeCodec\":true,\"nativeCallbacksExtracted\":true,"
        "\"vmAndStagedAdapterMock\":true,\"postCodecRollbackProven\":false,"
        "\"unityPlayerExecuted\":false,\"R03Accepted\":false,\"D4Complete\":false}\n",
        name,checks);
    return 0;
}
