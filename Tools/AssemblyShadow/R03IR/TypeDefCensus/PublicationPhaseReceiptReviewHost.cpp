// R03 B2 D1 adversarial contract review: exact inert native header only.
// No production publisher, Runtime, Unity/IL2CPP or Local Validation.
#include "vm/AssemblyShadowPublicationPhaseReceipt.h"
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <thread>
#include <type_traits>
#include <utility>

using namespace il2cpp::vm::assembly_shadow_publication;

static unsigned checks = 0, scenarios = 0;
static void Check(bool value, const char* expr, int line)
{
    ++checks;
    if (!value)
    {
        std::fprintf(stderr, "D1 independent-scope host FAIL line %d: %s\n", line, expr);
        std::abort();
    }
}
#define CHECK(x) Check(bool(x), #x, __LINE__)

static_assert(!std::is_copy_constructible<PublicationPhaseReceipt>::value,
              "receipt must be one-shot and non-copyable");
static_assert(!std::is_move_constructible<PublicationPhaseReceipt>::value,
              "receipt must not be moved across publication callbacks");
static_assert(std::is_trivially_destructible<PublicationPhaseReceipt>::value,
              "receipt must not acquire destructor-owned native state");
static_assert(noexcept(std::declval<const PublicationPhaseReceipt&>().IsLockFreeOnThisTarget()),
              "lock-free admission query must be noexcept");

static PreCodecCleanupProof Clean()
{
    const PreCodecCleanupProof value = {true,true,true,true};
    return value;
}

static void Complete(PublicationPhaseReceipt& r)
{
    CHECK(r.Advance(Phase::UsageAdmitted));
    CHECK(r.Advance(Phase::RegistriesAppended));
    CHECK(r.Advance(Phase::CodecAttempted));
    CHECK(r.Advance(Phase::RuntimeGroupPublished));
    CHECK(r.Advance(Phase::ActiveSnapshotPublished));
    CHECK(r.Advance(Phase::InitializersRunning));
    CHECK(r.Complete());
}

static void OneShotPreCodecRetryRequiresFreshInstance()
{
    ++scenarios;
    PublicationPhaseReceipt oldAttempt;
    CHECK(oldAttempt.Advance(Phase::UsageAdmitted));
    CHECK(oldAttempt.RejectBeforeCodec(Clean()));
    CHECK(oldAttempt.MayReturnValidated());
    CHECK(!oldAttempt.Advance(Phase::RegistriesAppended));
    CHECK(!oldAttempt.Complete());
    CHECK(oldAttempt.Read().outcome == Outcome::RejectedBeforeCodec);
    // New attempt, new object. This DOES NOT authenticate that the caller is
    // entitled to retry; it establishes necessary one-shot object lifetime.
    PublicationPhaseReceipt newAttempt;
    CHECK(newAttempt.Read().phase == Phase::Prepared);
    CHECK(newAttempt.Advance(Phase::UsageAdmitted));
    CHECK(newAttempt.Advance(Phase::RegistriesAppended));
    CHECK(newAttempt.Advance(Phase::CodecAttempted));
    newAttempt.MarkTerminal(Reason::CodecOutcomeUnknown);
    CHECK(newAttempt.RestartRequired());
    CHECK(!newAttempt.MayReturnValidated());
    CHECK(oldAttempt.Read().outcome == Outcome::RejectedBeforeCodec);
}

static void PostCompleteFailureNeedsSeparateGlobalGuard()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    Complete(r);
    const Snapshot done = r.Read();
    CHECK(done.outcome == Outcome::Complete);
    CHECK(done.reason == Reason::None);
    r.MarkTerminal(Reason::InitializerFailure);
    const Snapshot afterwards = r.Read();
    CHECK(afterwards.phase == done.phase);
    CHECK(afterwards.outcome == Outcome::Complete);
    CHECK(afterwards.reason == Reason::None);
    CHECK(!r.RestartRequired());
    // D3/D4 must not use this attempt receipt as its sole postcommit guard.
}

static void RejectedReceiptCannotBeOverwritten()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    CHECK(r.RejectBeforeCodec(Clean()));
    r.MarkTerminal(Reason::NativePublicationFailure);
    CHECK(r.Read().outcome == Outcome::RejectedBeforeCodec);
    CHECK(r.Read().reason == Reason::ProvenPreCodecRejection);
    CHECK(!r.RestartRequired());
    CHECK(r.MayReturnValidated());
}

static void TerminalAttemptCannotBeReused()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    CHECK(r.Advance(Phase::UsageAdmitted));
    CHECK(r.Advance(Phase::RegistriesAppended));
    CHECK(r.Advance(Phase::CodecAttempted));
    r.MarkTerminal(Reason::CodecOutcomeUnknown);
    CHECK(r.RestartRequired());
    CHECK(!r.MayReturnValidated());
    CHECK(!r.RejectBeforeCodec(Clean()));
    CHECK(!r.Advance(Phase::RuntimeGroupPublished));
    CHECK(!r.Complete());
    const Snapshot after = r.Read();
    CHECK(after.phase == Phase::CodecAttempted);
    CHECK(after.outcome == Outcome::TerminalRestartRequired);
    CHECK(after.reason == Reason::CodecOutcomeUnknown);
}

static void AtomicTriplesUnderConcurrentTerminalRead()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    CHECK(r.Advance(Phase::UsageAdmitted));
    CHECK(r.Advance(Phase::RegistriesAppended));
    CHECK(r.Advance(Phase::CodecAttempted));
    std::atomic<bool> go(false), bad(false);
    const unsigned count = 3;
    std::thread readers[count];
    for (unsigned k = 0; k < count; ++k)
    {
        readers[k] = std::thread([&]()
        {
            while (!go.load(std::memory_order_acquire)) std::this_thread::yield();
            for (unsigned i=0; i<120000; ++i)
            {
                const Snapshot s = r.Read();
                const bool before = s.phase == Phase::CodecAttempted &&
                    s.outcome == Outcome::InProgress && s.reason == Reason::None;
                const bool after = s.phase == Phase::CodecAttempted &&
                    s.outcome == Outcome::TerminalRestartRequired &&
                    s.reason == Reason::CodecOutcomeUnknown;
                if (!before && !after) bad.store(true, std::memory_order_release);
            }
        });
    }
    go.store(true, std::memory_order_release);
    r.MarkTerminal(Reason::CodecOutcomeUnknown);
    for (unsigned k=0; k<count; ++k) readers[k].join();
    CHECK(!bad.load(std::memory_order_acquire));
    CHECK(r.RestartRequired());
    CHECK(r.Read().reason == Reason::CodecOutcomeUnknown);
}

static void LockFreeHostObservationOnly()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    CHECK(r.IsLockFreeOnThisTarget());
    CHECK(sizeof(PublicationPhaseReceipt) <= 16u);
    CHECK(alignof(PublicationPhaseReceipt) <= 16u);
    // 64-bit macOS and Ubuntu hosts do NOT prove 32-bit mobile ABI.
}

int main()
{
    OneShotPreCodecRetryRequiresFreshInstance();
    PostCompleteFailureNeedsSeparateGlobalGuard();
    RejectedReceiptCannotBeOverwritten();
    TerminalAttemptCannotBeReused();
    AtomicTriplesUnderConcurrentTerminalRead();
    LockFreeHostObservationOnly();
    std::printf("{\"schema\":\"R03B2D1AdversarialReviewHostV1\","
                "\"result\":\"PassedBoundedReceiptAdversarialTestsOnly\","
                "\"scenarios\":%u,\"checks\":%u,"
                "\"freshReceiptPerAttemptRequired\":true,"
                "\"postCompleteNeedsSeparateTerminalGuard\":true,"
                "\"lockFreeOnTheseHostsOnly\":true,"
                "\"allNativeTargetsLockFreeProven\":false,"
                "\"cleanupProofVerifiedByNative\":false,"
                "\"productionPublisherIntegrated\":false,"
                "\"realUnity\":false,\"R03Accepted\":false,"
                "\"H2Passed\":false,\"ReadyForHumanReviewGate\":false}\n",
                scenarios, checks);
    return 0;
}
