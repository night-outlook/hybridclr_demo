// R03 D4: exact-source snapshot ownership, P5/P6, post-active native exits.
 // The D3 two-thread failure custody tests are retained as regressions.
//
// Exactly pinned native D2 registry scopes, D3 phase/lease callbacks,
// D1 phase/first-error/terminal headers, actual HybridCLR Runtime/Codec,
// and actual two intermediate publisher functions execute here.
// Only VM objects, native lock implementations, memory allocator, and the
// fault-injection adapter are test-owned. NOT a Unity Player or GC proof.
#include "AssemblyShadowTypes.h"
#include "AssemblyShadowTerminalExecution.h"
#include "AssemblyShadowFirstFailureV2.h"
#include "AssemblyShadowPublicationD3Decision.h"
#include "AssemblyShadowProcessSnapshotOwner.h"
#include "PinnedNativeDynamicArray.h"
#include "hybridclr/metadata/InterpreterMetadataIndexRuntime.h"
#include "hybridclr/metadata/AssemblyShadowBridge.h"

#include <atomic>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <memory>
#include <stdexcept>
#include <thread>
#include <vector>

using Runtime = hybridclr::metadata::InterpreterMetadataIndexRuntime;
using CodecError = Runtime::Error;
namespace phase = il2cpp::vm::assembly_shadow_publication;
namespace first = il2cpp::vm::assembly_shadow_first_failure_v2;

static std::atomic<unsigned> checks{0};
static void Check(bool accepted, const char* expression, int line)
{
    ++checks;
    if (!accepted)
    {
        std::fprintf(stderr, "IR-D3-01 HOST FAIL at %d: %s\n", line, expression);
        std::abort();
    }
}
#define CHECK(c) Check(bool(c), #c, __LINE__)

static void WaitFlag(const std::atomic<bool>& flag, const char* site)
{
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(5);
    while (!flag.load(std::memory_order_acquire))
    {
        if (std::chrono::steady_clock::now() > deadline)
        {
            std::fprintf(stderr, "IR-D3-01 barrier stalled at %s\n", site);
            std::abort();
        }
        std::this_thread::yield();
    }
}

static std::atomic<bool> gateEnabled(false);
static std::atomic<bool> beginHeld(false);
static std::atomic<bool> preChecked(false);
static std::atomic<bool> pausedInAssemblyUnlock(false);
static std::atomic<bool> contenderCompleted(false);
static std::atomic<bool> enteredBaseline(false);
static std::atomic<bool> deniedUnderUsage(false);
static std::atomic<bool> deniedAfterUsage(false);
static std::mutex* watchedAssemblyMutex = nullptr;

struct Il2CppAssembly { int token; };
struct MethodInfo {};  // The exact terminal method predicate never dereferences this in a healthy test.
namespace il2cpp { namespace os {
class FastAutoLock
{
public:
    explicit FastAutoLock(std::mutex* mutex) : mutex_(mutex) { mutex_->lock(); }
    ~FastAutoLock()
    {
        if (mutex_ == watchedAssemblyMutex &&
            gateEnabled.load(std::memory_order_acquire))
        {
            // The production s_assemblyLock is still held. The D2 physical
            // guard already called the exact ReleasePublicationUsage callback.
            // STOP T1 here, before the outer CommitTransaction classifier.
            pausedInAssemblyUnlock.store(true, std::memory_order_release);
            WaitFlag(contenderCompleted, "method contender before outer classification");
        }
        mutex_->unlock();
    }
    FastAutoLock(const FastAutoLock&)=delete;
    FastAutoLock& operator=(const FastAutoLock&)=delete;
private:
    std::mutex* mutex_;
};
}}

namespace hybridclr { namespace metadata {
namespace {
bool vmVisible = false;
uint32_t shadowIds[2] = {};
InterpreterImage* shadowImages[2] = {};
}
InterpreterImage* AssemblyShadowBridge::GetPrivateImage(uint32_t) {return nullptr;}
bool AssemblyShadowBridge::IsPublicImage(uint32_t id, InterpreterImage* image)
{
    if (!vmVisible) return false;
    for (unsigned i=0;i<2;++i)
        if (shadowIds[i]==id && shadowImages[i]==image) return true;
    return false;
}
class InterpreterImage
{
public:
    static Runtime::Error RegisterImagesBatch(const uint32_t*,size_t,
        const Runtime::PublicationObserver*);
};
class Assembly
{
public:
    static bool PublishStagedImagesBatch(const std::vector<uint32_t>&,
        const Runtime::PublicationObserver*);
};
}}

// Native file-level and anonymous namespace stand-ins, not Unity VM code.
static il2cpp::utils::dynamic_array<Il2CppAssembly*> s_cliAssemblies;
namespace il2cpp { namespace vm {
using AssemblyVector = std::vector<const Il2CppAssembly*>;
static std::mutex g_MetadataLock;
static std::mutex s_assemblyLock;
static AssemblyVector s_Assemblies;
static uint64_t s_assemblyVersion = 0;
class Assembly
{
public:
    static bool PublishShadowBatch(const AssemblyVector&,
        bool (*)(void*), bool (*)(void*), void (*)(void*), void*);
};
class MetadataCache
{
public:
    static bool PublishInterpreterAssembliesBatch(const std::vector<Il2CppAssembly*>&,
        bool (*)(void*), bool (*)(void*), void (*)(void*), void*);
};
namespace {
struct Candidate { struct {bool present=false;} firstUse; };
struct StagedAssembly {bool published=false;};
struct ClosureMember {Candidate* candidate;StagedAssembly* staged;};
struct ActiveSnapshot {unsigned id=42;};
struct Transaction {
    std::vector<ClosureMember> closure;
    phase::ProcessSnapshotOwner<ActiveSnapshot> activeOwner;
};
struct TypeFailure {};
std::atomic_flag s_usageLock=ATOMIC_FLAG_INIT;
std::atomic<const ActiveSnapshot*> s_active{nullptr};
std::atomic<AssemblyShadowState> s_state{AssemblyShadowState::Committing};
std::atomic<bool> s_unexpectedFailure{false};
std::atomic<bool> s_lateBaselineUse{false};
std::atomic<bool> s_referenceViolation{false};
std::atomic<const TypeFailure*> s_typeFailure{nullptr};
first::FirstErrorV2 s_firstFailureV2;
thread_local bool s_constructingFixedDiagnosticException=false;
bool IsFixedDiagnosticConstructor(const MethodInfo*) noexcept {return false;}

enum class Injection {Normal,RuntimePrecheck,CodecValidation,PostGroupRejection,
                      ThrowBeforeCodec,ThrowAfterGroup,ThrowAfterActive};
Injection injection=Injection::Normal;
bool InjectCodecThenSeal(void*) noexcept;
struct InterpreterAssembly
{
    static bool PublishStagedImagesBatch(const std::vector<uint32_t>& ids,
        const Runtime::PublicationObserver* observer)
    {
        if (injection==Injection::ThrowBeforeCodec)
            throw std::runtime_error("test-owned before-codec throw");
        if (injection==Injection::PostGroupRejection)
        {
            Runtime::PublicationObserver wrapped=*observer;
            wrapped.beforeCodec=InjectCodecThenSeal;
            return !ids.empty() &&
                Runtime::PublishBatch(ids.data(),ids.size(),&wrapped)==CodecError::None;
        }
        // Exact two intermediate forwarding definitions execute here.
        const bool accepted=hybridclr::metadata::Assembly::PublishStagedImagesBatch(
            ids,observer);
        if (accepted && injection==Injection::ThrowAfterGroup)
            throw std::runtime_error("test-owned post-group callback throw");
        return accepted;
    }
};
}}
}
#include "D4ExactNativeSources.inc"

namespace il2cpp { namespace vm { namespace {
bool PublishAndThrowAfterActive(void* context)
{
    const bool ok = PublishActive(context);
    if (ok) throw std::runtime_error("synthetic native exit after active release-store");
    return ok;
}
}}}

namespace il2cpp { namespace vm { namespace {
bool InjectCodecThenSeal(void* opaque) noexcept
{
    if (!ObserveCodecAttempt(opaque)) return false;
    Publication& p=*static_cast<Publication*>(opaque);
    p.phaseReceipt->MarkTerminal(phase::Reason::NativePublicationFailure);
    return true;
}
}}}

using namespace il2cpp::vm;
struct Marker {unsigned tag;};
struct Fixture
{
    Marker markers[2]={{11},{12}};
    hybridclr::metadata::InterpreterImage* images[2]={
        reinterpret_cast<hybridclr::metadata::InterpreterImage*>(&markers[0]),
        reinterpret_cast<hybridclr::metadata::InterpreterImage*>(&markers[1])
    };
    Il2CppAssembly first{1},second{2};
    std::vector<Il2CppAssembly*> assemblies{&first,&second};
    std::vector<Runtime::Reservation> reservations;
    uint32_t ids[2]={};
    Candidate candidate;
    StagedAssembly staged;
    Transaction transaction;
    std::unique_ptr<ActiveSnapshot> pendingSnapshot{new ActiveSnapshot()};
    ActiveSnapshot* snapshot = pendingSnapshot.get();
    phase::PublicationPhaseReceipt receipt;
    Publication publication{};

    explicit Fixture(bool finalizeSecond=true)
    {
        CHECK(Runtime::ReserveImages(2,reservations)==CodecError::None);
        CHECK(reservations.size()==2);
        for(int index=0;index<2;++index)
        {
            ids[index]=reservations[index].imageId;
            {
                Runtime::ScopedConstruction construction(ids[index],images[index],true);
                if (index==0||finalizeSecond)
                    CHECK(Runtime::Finalize(ids[index],1)==CodecError::None);
            }
            hybridclr::metadata::shadowIds[index]=ids[index];
            hybridclr::metadata::shadowImages[index]=images[index];
        }
        transaction.closure.push_back({&candidate,&staged});
        publication.transaction=&transaction;
        publication.snapshot=snapshot;
        publication.pendingSnapshot=&pendingSnapshot;
        publication.phaseReceipt=&receipt;
        publication.imageIndices.assign(ids,ids+2);
        watchedAssemblyMutex=&s_assemblyLock;
        CHECK(s_Assemblies.empty() && s_cliAssemblies.empty());
        CHECK(s_active.load(std::memory_order_acquire)==nullptr);
    }
    bool Publish(bool synchronizeBegin)
    {
        return MetadataCache::PublishInterpreterAssembliesBatch(
            assemblies,synchronizeBegin ? BeginWithProbe : TryBeginPublication,
            injection==Injection::ThrowAfterActive
                ? PublishAndThrowAfterActive : PublishActive,
            ReleasePublicationUsage,&publication);
    }
    static bool BeginWithProbe(void* opaque)
    {
        const bool permitted=TryBeginPublication(opaque);
        if (permitted)
        {
            beginHeld.store(true,std::memory_order_release);
            WaitFlag(preChecked,"pre-release contender check");
        }
        return permitted;
    }
    void CheckNativeRelease(bool succeeded)
    {
        CHECK(!publication.usageHeld);
        CHECK(!UsageHeld());
        CHECK(s_cliAssemblies.size()==(succeeded?2u:0u));
        CHECK(s_Assemblies.size()==(succeeded?2u:0u));
        CHECK(s_assemblyVersion==(succeeded?1u:0u));
    }
    static bool UsageHeld()
    {
        bool was=s_usageLock.test_and_set(std::memory_order_acquire);
        if (!was)s_usageLock.clear(std::memory_order_release);
        return was;
    }
    void CheckTerminal(bool expected, first::Origin origin=first::Origin::TransactionTerminal)
    {
        CHECK(s_unexpectedFailure.load(std::memory_order_acquire)==expected);
        CHECK(s_state.load(std::memory_order_acquire)==
              (expected?AssemblyShadowState::Failed:AssemblyShadowState::Committing));
        if(expected)
        {
            CHECK(receipt.RestartRequired());
            CHECK(TerminalMethodDenied(nullptr));
            first::Snapshot record{};
            CHECK(s_firstFailureV2.Read(record));
            CHECK(record.origin==origin);
        }
        else
        {
            CHECK(!receipt.RestartRequired());
            CHECK(!TerminalMethodDenied(nullptr));
            CHECK(s_firstFailureV2.status()==first::State::Empty);
        }
    }
};

static void CheckNoSnapshot()
{
    CHECK(s_active.load(std::memory_order_acquire)==nullptr);
}
static void LaunchContender()
{
    WaitFlag(beginHeld,"begin-held");
    const MethodInfo method{};
    // This first check intentionally runs while T1 still owns UsageLock.
    CHECK(!TerminalMethodDenied(&method));
    preChecked.store(true,std::memory_order_release);
    LockUsage(); // acquire only AFTER production callback clears the usage flag
    const bool denied=TerminalMethodDenied(&method);
    deniedUnderUsage.store(denied,std::memory_order_release);
    if (!denied && !s_active.load(std::memory_order_acquire))
        enteredBaseline.store(true,std::memory_order_release);
    UnlockUsage();
    deniedAfterUsage.store(TerminalMethodDenied(&method),std::memory_order_release);
    contenderCompleted.store(true,std::memory_order_release);
}

static void VerifyRaceWithNativeScope(Injection mode, bool finalizeSecond,
                                      bool expectGroupPublished, bool exceptional)
{
    Fixture f(finalizeSecond);
    injection=mode;
    if (mode==Injection::RuntimePrecheck)
        f.publication.imageIndices[1]=0; // real Runtime precheck refuses P2
    gateEnabled.store(true,std::memory_order_release);
    std::thread contender(LaunchContender);
    bool published=false,escaped=false;
    {
        try
        {
            // Literal native D2 exceptional guard from CommitTransaction,
            // not a reconstructed first-error implementation.
            ScopedUnexpectedPublicationExit exceptionalExit(f.receipt);
            published=f.Publish(true);
            exceptionalExit.returned=true;
        }
        catch(const std::runtime_error&)
        {
            escaped=true;
        }
    }
    contender.join();
    gateEnabled.store(false,std::memory_order_release);
    CHECK(pausedInAssemblyUnlock.load(std::memory_order_acquire));
    CHECK(contenderCompleted.load(std::memory_order_acquire));
    CHECK(deniedUnderUsage.load(std::memory_order_acquire));
    CHECK(deniedAfterUsage.load(std::memory_order_acquire));
    CHECK(!enteredBaseline.load(std::memory_order_acquire));
    CHECK(!published);
    CHECK(escaped==exceptional);
    f.CheckNativeRelease(false);
    f.CheckTerminal(true,exceptional?first::Origin::UnexpectedFailure
                                    :first::Origin::TransactionTerminal);
    CHECK(phase::ClassifyFailedNativeBatch(
        f.receipt,f.publication.used!=nullptr,f.publication.usageHeld,
        f.publication.runtimePublicationFailed)==phase::D3Disposition::TerminalRestartRequired);
    CHECK(f.receipt.RestartRequired());
    CheckNoSnapshot();
    if(expectGroupPublished)
    {
        // Real Codec + Runtime have committed, irrespective of mock VM gate.
        CHECK(Runtime::Abort(f.ids[0])==CodecError::InvalidState);
        CHECK(Runtime::Abort(f.ids[1])==CodecError::InvalidState);
    }
    else
    {
        CHECK(Runtime::GetPublishedImage(f.ids[0])==nullptr);
    }
}

static void UsedBeforeAppend()
{
    Fixture f;
    f.candidate.firstUse.present=true;
    CHECK(!f.Publish(false));
    f.CheckNativeRelease(false);
    f.CheckTerminal(false);
    CHECK(f.publication.leaseExit==PublicationLeaseExit::UsedBeforeAppend);
    CHECK(f.publication.used==&f.candidate);
    CHECK(f.receipt.Read().phase==phase::Phase::Prepared);
    CHECK(phase::ClassifyFailedNativeBatch(
        f.receipt,true,false,false)==phase::D3Disposition::ProvenUsedRejection);
    CHECK(f.receipt.MayReturnValidated());
    CHECK(!s_unexpectedFailure.load(std::memory_order_acquire));
    CheckNoSnapshot();
}

static void NormalSuccess()
{
    Fixture f;
    CHECK(f.Publish(false));
    f.CheckNativeRelease(true);
    f.CheckTerminal(false);
    CHECK(f.publication.leaseExit==PublicationLeaseExit::ActivePublished);
    CHECK(f.staged.published);
    CHECK(s_active.load(std::memory_order_acquire)==f.snapshot);
    CHECK(f.transaction.activeOwner.get()==f.snapshot);
    CHECK(!f.pendingSnapshot);
    CHECK(f.receipt.Read().phase==phase::Phase::ActiveSnapshotPublished);
    // The actual Runtime is group-published, but the VM predicate remains
    // mocked. This never claims a native snapshot lifetime proof.
    CHECK(Runtime::GetPublishedImage(f.ids[0])==nullptr);
    hybridclr::metadata::vmVisible=true;
    CHECK(Runtime::GetPublishedImage(f.ids[0])==f.images[0]);
    CHECK(Runtime::GetPublishedImage(f.ids[1])==f.images[1]);
}

static void PreserveEarlierFirstError()
{
    Fixture f(false);
    static const char firstReason[]="preexisting first native error";
    CHECK(s_firstFailureV2.TryFreeze(
        static_cast<int32_t>(AssemblyShadowError::InternalError),
        first::Origin::Guard,firstReason,sizeof(firstReason)-1));
    injection=Injection::CodecValidation;
    CHECK(!f.Publish(false));
    f.CheckNativeRelease(false);
    CHECK(f.receipt.RestartRequired());
    CHECK(s_unexpectedFailure.load(std::memory_order_acquire));
    first::Snapshot after{};
    CHECK(s_firstFailureV2.Read(after));
    CHECK(after.origin==first::Origin::Guard);
    CHECK(std::strcmp(after.reason,firstReason)==0);
}

// A D4 native exception AFTER the active release-store cannot destroy the
// public pointer: the transaction already owns it, and the outer D2 guard
// seals terminal state despite rolling back its physical/CLI memberships.
static void ThrowAfterActiveStore()
{
    Fixture f;
    injection=Injection::ThrowAfterActive;
    bool escaped=false;
    try
    {
        ScopedUnexpectedPublicationExit unexpected(f.receipt);
        (void)f.Publish(false);
        unexpected.returned=true;
    }
    catch(const std::runtime_error&) { escaped=true; }
    CHECK(escaped);
    f.CheckNativeRelease(false);
    CHECK(f.receipt.Read().phase==phase::Phase::ActiveSnapshotPublished);
    CHECK(f.receipt.RestartRequired());
    CHECK(f.transaction.activeOwner.get()==f.snapshot);
    CHECK(!f.pendingSnapshot);
    CHECK(s_active.load(std::memory_order_acquire)==f.snapshot);
    CHECK(s_unexpectedFailure.load(std::memory_order_acquire));
    CHECK(s_state.load(std::memory_order_acquire)==AssemblyShadowState::FailedAfterCommit);
    CHECK(TerminalMethodDenied(nullptr));
}

static void BadPendingOwner(bool mismatch)
{
    Fixture f;
    ActiveSnapshot decoy;
    if (mismatch) f.publication.snapshot=&decoy;
    else f.publication.pendingSnapshot=nullptr;
    CHECK(!f.Publish(false)); // actual Codec + Runtime published first
    f.CheckNativeRelease(false);
    CHECK(f.receipt.RestartRequired());
    CHECK(f.receipt.Read().phase==phase::Phase::RuntimeGroupPublished);
    CHECK(s_unexpectedFailure.load(std::memory_order_acquire));
    CHECK(s_state.load(std::memory_order_acquire)==AssemblyShadowState::Failed);
    CHECK(!f.transaction.activeOwner.get());
    CHECK(f.pendingSnapshot.get()==f.snapshot);
    CHECK(!s_active.load(std::memory_order_acquire));
    CHECK(Runtime::Abort(f.ids[0])==CodecError::InvalidState);
}

static void PostActiveException(bool afterP6, bool preservePrior)
{
    Fixture f;
    CHECK(f.Publish(false));
    CHECK(!f.pendingSnapshot && f.transaction.activeOwner.get()==f.snapshot);
    if (preservePrior)
    {
        static const char reason[]="first failure is retained";
        CHECK(s_firstFailureV2.TryFreeze(
            static_cast<int32_t>(AssemblyShadowError::InternalError),
            first::Origin::Guard,reason,sizeof(reason)-1));
    }
    bool escaped=false;
    try
    {
        ScopedPostActiveExit guard(f.receipt);
        if (afterP6)
            CHECK(f.receipt.Advance(phase::Phase::InitializersRunning));
        throw std::runtime_error("synthetic post-active diagnostic or initializer exception");
    }
    catch(const std::runtime_error&) {escaped=true;}
    CHECK(escaped);
    CHECK(f.transaction.activeOwner.get()==f.snapshot);
    CHECK(s_active.load(std::memory_order_acquire)==f.snapshot);
    CHECK(f.receipt.RestartRequired());
    CHECK(f.receipt.Read().reason == (afterP6
        ? phase::Reason::InitializerFailure : phase::Reason::NativePublicationFailure));
    CHECK(s_unexpectedFailure.load(std::memory_order_acquire));
    CHECK(s_state.load(std::memory_order_acquire)==AssemblyShadowState::FailedAfterCommit);
    CHECK(TerminalMethodDenied(nullptr));
    first::Snapshot firstEvent{};
    CHECK(s_firstFailureV2.Read(firstEvent));
    CHECK(firstEvent.origin==(preservePrior ? first::Origin::Guard
                                           : first::Origin::UnexpectedFailure));
}

static void PostActiveHandledFailure()
{
    Fixture f;
    CHECK(f.Publish(false));
    {
        ScopedPostActiveExit guard(f.receipt);
        CHECK(f.receipt.Advance(phase::Phase::InitializersRunning));
        s_state.store(AssemblyShadowState::FailedAfterCommit,std::memory_order_release);
        f.receipt.MarkTerminal(phase::Reason::InitializerFailure);
        static const char reason[]="real initializer failure simulated by host";
        CHECK(s_firstFailureV2.TryFreeze(
            static_cast<int32_t>(AssemblyShadowError::ModuleInitializerFailed),
            first::Origin::InterpreterInitializer,reason,sizeof(reason)-1));
        guard.handled=true;
    }
    CHECK(!s_unexpectedFailure.load(std::memory_order_acquire));
    CHECK(f.receipt.RestartRequired());
    CHECK(f.receipt.Read().reason==phase::Reason::InitializerFailure);
    CHECK(s_state.load(std::memory_order_acquire)==AssemblyShadowState::FailedAfterCommit);
    CHECK(s_active.load(std::memory_order_acquire)==f.snapshot);
    CHECK(f.transaction.activeOwner.get()==f.snapshot);
    first::Snapshot firstEvent{};
    CHECK(s_firstFailureV2.Read(firstEvent));
    CHECK(firstEvent.origin==first::Origin::InterpreterInitializer);
}

static void PostActiveCommitted()
{
    Fixture f;
    CHECK(f.Publish(false));
    {
        ScopedPostActiveExit guard(f.receipt);
        CHECK(f.receipt.Read().phase==phase::Phase::ActiveSnapshotPublished);
        CHECK(f.receipt.Advance(phase::Phase::InitializersRunning));
        s_state.store(AssemblyShadowState::Committed,std::memory_order_release);
        CHECK(f.receipt.Complete());
        guard.handled=true;
    }
    CHECK(f.receipt.IsComplete());
    CHECK(f.receipt.Read().outcome==phase::Outcome::Complete);
    CHECK(!s_unexpectedFailure.load(std::memory_order_acquire));
    CHECK(s_state.load(std::memory_order_acquire)==AssemblyShadowState::Committed);
    CHECK(s_active.load(std::memory_order_acquire)==f.snapshot);
    CHECK(f.transaction.activeOwner.get()==f.snapshot);
}

int main(int argc,char**argv)
{
    if(argc!=2){std::fputs("Specify one IR-D3-01 race case\n",stderr);return 2;}
    const char* scenario=argv[1];
    if(!std::strcmp(scenario,"p0-used-denial"))UsedBeforeAppend();
    else if(!std::strcmp(scenario,"normal-success"))NormalSuccess();
    else if(!std::strcmp(scenario,"runtime-precheck-race"))
        VerifyRaceWithNativeScope(Injection::RuntimePrecheck,true,false,false);
    else if(!std::strcmp(scenario,"codec-validation-race"))
        VerifyRaceWithNativeScope(Injection::CodecValidation,false,false,false);
    else if(!std::strcmp(scenario,"postgroup-rejection-race"))
        VerifyRaceWithNativeScope(Injection::PostGroupRejection,true,true,false);
    else if(!std::strcmp(scenario,"exception-precodec-race"))
        VerifyRaceWithNativeScope(Injection::ThrowBeforeCodec,true,false,true);
    else if(!std::strcmp(scenario,"exception-postgroup-race"))
        VerifyRaceWithNativeScope(Injection::ThrowAfterGroup,true,true,true);
    else if(!std::strcmp(scenario,"prior-first-error"))
        PreserveEarlierFirstError();
    else if(!std::strcmp(scenario,"post-active-store-throw"))
        ThrowAfterActiveStore();
    else if(!std::strcmp(scenario,"pending-owner-null"))
        BadPendingOwner(false);
    else if(!std::strcmp(scenario,"pending-owner-mismatch"))
        BadPendingOwner(true);
    else if(!std::strcmp(scenario,"post-active-event-throw"))
        PostActiveException(false,false);
    else if(!std::strcmp(scenario,"post-active-initializer-throw"))
        PostActiveException(true,false);
    else if(!std::strcmp(scenario,"post-active-first-error"))
        PostActiveException(false,true);
    else if(!std::strcmp(scenario,"post-active-handled-failure"))
        PostActiveHandledFailure();
    else if(!std::strcmp(scenario,"post-active-committed"))
        PostActiveCommitted();
    else {std::fputs("Unknown D4 source-host case\n",stderr);return 2;}
    std::printf("{\"schema\":\"R03D4ProcessOwnedSnapshotHostV1\","
        "\"result\":\"PassedExactD4AndRuntimeHostOnly\","
        "\"case\":\"%s\",\"checks\":%u,"
        "\"actualD2RegistryScopes\":true,\"actualD3NativeCallbacks\":true,"
        "\"actualRuntimeCodec\":true,\"realCliDynamicArraySource\":true,"
        "\"exactD4OwnerHeader\":true,\"exactPostActiveGuard\":true,"
        "\"actualTerminalMethodPredicate\":true,\"deterministicTwoThreadBarrier\":%s,"
        "\"hostLockAndVmStandIns\":true,\"unityPlayerExecuted\":false,"
        "\"postCodecRollbackProven\":false,\"R03Accepted\":false,"
        "\"D4IndependentReviewPassed\":false,\"D5Started\":false}\n",
        scenario,checks.load(std::memory_order_relaxed),pausedInAssemblyUnlock.load()?"true":"false");
    return 0;
}
