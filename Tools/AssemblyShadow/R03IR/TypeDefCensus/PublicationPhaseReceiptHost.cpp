// R03 B2 D1: compile the exact inert native header, NOT Unity/IL2CPP.
// No native publisher is wired to this receipt. Proof flags are test-owned.
#include "vm/AssemblyShadowPublicationPhaseReceipt.h"

#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <thread>
#include <type_traits>
#include <utility>

using namespace il2cpp::vm::assembly_shadow_publication;
static unsigned scenarios = 0;
static unsigned checks = 0;

static void Check(bool condition, const char* expression, int line)
{
    ++checks;
    if (!condition)
    {
        std::fprintf(stderr, "D1 host FAIL at %d: %s\n", line, expression);
        std::abort();
    }
}
#define CHECK(x) Check(bool(x), #x, __LINE__)

static_assert(std::is_nothrow_constructible<PublicationPhaseReceipt>::value,
              "D1 receipt constructor must not throw");
static_assert(noexcept(std::declval<PublicationPhaseReceipt&>().Advance(Phase::UsageAdmitted)),
              "D1 transition must not throw");
static_assert(noexcept(std::declval<PublicationPhaseReceipt&>().MarkTerminal(Reason::CodecOutcomeUnknown)),
              "D1 terminal latch must not throw");
static_assert(noexcept(std::declval<const PublicationPhaseReceipt&>().Read()),
              "D1 snapshot must not throw");
static_assert(noexcept(std::declval<PublicationPhaseReceipt&>().Complete()),
              "D1 success seal must not throw");
static_assert(sizeof(PublicationPhaseReceipt) <= 16u,
              "D1 receipt unexpectedly exceeds its bounded storage budget");

static PreCodecCleanupProof CompleteProof()
{
    PreCodecCleanupProof proof = {true, true, true, true};
    return proof;
}

static void Expect(const PublicationPhaseReceipt& receipt,
                   Phase phase, Outcome outcome, Reason reason)
{
    const Snapshot s = receipt.Read();
    CHECK(s.phase == phase);
    CHECK(s.outcome == outcome);
    CHECK(s.reason == reason);
}

static void Go( PublicationPhaseReceipt& r, Phase phase )
{
    CHECK(r.Advance(phase));
    Expect(r, phase, Outcome::InProgress, Reason::None);
}

static void ToCodecAttempted(PublicationPhaseReceipt& r)
{
    Go(r, Phase::UsageAdmitted);
    Go(r, Phase::RegistriesAppended);
    Go(r, Phase::CodecAttempted);
}
static void ToInitializer(PublicationPhaseReceipt& r)
{
    ToCodecAttempted(r);
    Go(r, Phase::RuntimeGroupPublished);
    Go(r, Phase::ActiveSnapshotPublished);
    Go(r, Phase::InitializersRunning);
}

static void Fresh()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    Expect(r, Phase::Prepared, Outcome::InProgress, Reason::None);
    CHECK(!r.MayReturnValidated());
    CHECK(!r.RestartRequired());
    CHECK(!r.IsComplete());
}

static void OrderedCompletion()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    ToInitializer(r);
    CHECK(r.Complete());
    Expect(r, Phase::InitializersRunning, Outcome::Complete, Reason::None);
    CHECK(r.IsComplete());
    CHECK(!r.RestartRequired());
    CHECK(!r.MayReturnValidated());
    CHECK(!r.Complete());
    CHECK(!r.Advance(Phase::InitializersRunning));
    r.MarkTerminal(Reason::InitializerFailure);
    Expect(r, Phase::InitializersRunning, Outcome::Complete, Reason::None);
}

static void InvalidSkip()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    CHECK(!r.Advance(Phase::RegistriesAppended));
    Expect(r, Phase::Prepared, Outcome::TerminalRestartRequired,
           Reason::InvalidPhaseTransition);
    CHECK(r.RestartRequired());
}

static void InvalidRepeat()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    Go(r, Phase::UsageAdmitted);
    CHECK(!r.Advance(Phase::UsageAdmitted));
    Expect(r, Phase::UsageAdmitted, Outcome::TerminalRestartRequired,
           Reason::InvalidPhaseTransition);
    CHECK(!r.Advance(Phase::RegistriesAppended));
}

static void InvalidBackwards()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    Go(r, Phase::UsageAdmitted);
    Go(r, Phase::RegistriesAppended);
    CHECK(!r.Advance(Phase::Prepared));
    Expect(r, Phase::RegistriesAppended, Outcome::TerminalRestartRequired,
           Reason::InvalidPhaseTransition);
}

static void RejectAtPrepared()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    CHECK(r.RejectBeforeCodec(CompleteProof()));
    Expect(r, Phase::Prepared, Outcome::RejectedBeforeCodec,
           Reason::ProvenPreCodecRejection);
    CHECK(r.MayReturnValidated());
    CHECK(!r.RestartRequired());
    CHECK(!r.Advance(Phase::UsageAdmitted));
}

static void RejectAfterUsage()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    Go(r, Phase::UsageAdmitted);
    CHECK(r.RejectBeforeCodec(CompleteProof()));
    Expect(r, Phase::UsageAdmitted, Outcome::RejectedBeforeCodec,
           Reason::ProvenPreCodecRejection);
    CHECK(r.MayReturnValidated());
    CHECK(!r.RejectBeforeCodec(CompleteProof()));
}

static void RejectAfterRegistries()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    Go(r, Phase::UsageAdmitted);
    Go(r, Phase::RegistriesAppended);
    CHECK(r.RejectBeforeCodec(CompleteProof()));
    Expect(r, Phase::RegistriesAppended, Outcome::RejectedBeforeCodec,
           Reason::ProvenPreCodecRejection);
    CHECK(r.MayReturnValidated());
}

static void MissingProofFailsClosed()
{
    ++scenarios;
    for (unsigned index = 0; index < 4; ++index)
    {
        PublicationPhaseReceipt r;
        Go(r, Phase::UsageAdmitted);
        Go(r, Phase::RegistriesAppended);
        PreCodecCleanupProof proof = CompleteProof();
        if (index == 0) proof.codecNotAttempted = false;
        if (index == 1) proof.physicalRegistryRestored = false;
        if (index == 2) proof.cliRegistryRestored = false;
        if (index == 3) proof.usageLockReleased = false;
        CHECK(!r.RejectBeforeCodec(proof));
        Expect(r, Phase::RegistriesAppended, Outcome::TerminalRestartRequired,
               Reason::MissingCleanupProof);
        CHECK(!r.MayReturnValidated());
        CHECK(r.RestartRequired());
        CHECK(!r.RejectBeforeCodec(CompleteProof()));
        Expect(r, Phase::RegistriesAppended, Outcome::TerminalRestartRequired,
               Reason::MissingCleanupProof);
    }
}

static void CodecAttemptNeverRetryable()
{
    ++scenarios;
    for (unsigned extra = 0; extra <= 3; ++extra)
    {
        PublicationPhaseReceipt r;
        ToCodecAttempted(r);
        Phase p = Phase::CodecAttempted;
        if (extra >= 1) { Go(r, Phase::RuntimeGroupPublished); p = Phase::RuntimeGroupPublished; }
        if (extra >= 2) { Go(r, Phase::ActiveSnapshotPublished); p = Phase::ActiveSnapshotPublished; }
        if (extra >= 3) { Go(r, Phase::InitializersRunning); p = Phase::InitializersRunning; }
        CHECK(!r.RejectBeforeCodec(CompleteProof()));
        Expect(r, p, Outcome::TerminalRestartRequired, Reason::CodecOutcomeUnknown);
        CHECK(r.RestartRequired());
        CHECK(!r.MayReturnValidated());
        CHECK(!r.Complete());
    }
}

static void UnknownOutcomeTerminal()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    ToCodecAttempted(r);
    r.MarkTerminal(Reason::CodecOutcomeUnknown);
    Expect(r, Phase::CodecAttempted, Outcome::TerminalRestartRequired,
           Reason::CodecOutcomeUnknown);
    CHECK(!r.RejectBeforeCodec(CompleteProof()));
    CHECK(!r.Advance(Phase::RuntimeGroupPublished));
}

static void FirstFailureWins()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    ToCodecAttempted(r);
    Go(r, Phase::RuntimeGroupPublished);
    r.MarkTerminal(Reason::NativePublicationFailure);
    r.MarkTerminal(Reason::SnapshotOwnershipUnverified);
    r.MarkTerminal(Reason::InitializerFailure);
    Expect(r, Phase::RuntimeGroupPublished, Outcome::TerminalRestartRequired,
           Reason::NativePublicationFailure);
}

static void InvalidTerminalReason()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    r.MarkTerminal(Reason::None);
    Expect(r, Phase::Prepared, Outcome::TerminalRestartRequired,
           Reason::InvalidPhaseTransition);
    CHECK(!r.MayReturnValidated());
}

static void EarlyUnexpectedFailure()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    Go(r, Phase::UsageAdmitted);
    r.MarkTerminal(Reason::NativePublicationFailure);
    Expect(r, Phase::UsageAdmitted, Outcome::TerminalRestartRequired,
           Reason::NativePublicationFailure);
    CHECK(!r.RejectBeforeCodec(CompleteProof()));
}

static void CompletionBeforeInitializersFailsClosed()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    ToCodecAttempted(r);
    Go(r, Phase::RuntimeGroupPublished);
    CHECK(!r.Complete());
    Expect(r, Phase::RuntimeGroupPublished, Outcome::TerminalRestartRequired,
           Reason::InvalidPhaseTransition);
}

static void InitializerFailureIsTerminal()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    ToInitializer(r);
    r.MarkTerminal(Reason::InitializerFailure);
    Expect(r, Phase::InitializersRunning, Outcome::TerminalRestartRequired,
           Reason::InitializerFailure);
    CHECK(!r.IsComplete());
    CHECK(!r.Complete());
}

static void ConcurrentReadSnapshots()
{
    ++scenarios;
    PublicationPhaseReceipt r;
    std::atomic<bool> bad(false);
    std::thread reader([&]()
    {
        for (unsigned i = 0; i < 60000; ++i)
        {
            const Snapshot s = r.Read();
            if (static_cast<unsigned>(s.phase) > 6u ||
                (s.outcome != Outcome::InProgress &&
                 s.outcome != Outcome::Complete) ||
                s.reason != Reason::None ||
                (s.outcome == Outcome::Complete &&
                 s.phase != Phase::InitializersRunning))
                bad.store(true, std::memory_order_release);
        }
    });
    ToInitializer(r);
    CHECK(r.Complete());
    reader.join();
    CHECK(!bad.load(std::memory_order_acquire));
    Expect(r, Phase::InitializersRunning, Outcome::Complete, Reason::None);
}

int main()
{
    Fresh();
    OrderedCompletion();
    InvalidSkip();
    InvalidRepeat();
    InvalidBackwards();
    RejectAtPrepared();
    RejectAfterUsage();
    RejectAfterRegistries();
    MissingProofFailsClosed();
    CodecAttemptNeverRetryable();
    UnknownOutcomeTerminal();
    FirstFailureWins();
    InvalidTerminalReason();
    EarlyUnexpectedFailure();
    CompletionBeforeInitializersFailsClosed();
    InitializerFailureIsTerminal();
    ConcurrentReadSnapshots();
    std::printf("{\"schema\":\"R03B2D1PublicationPhaseReceiptHostV1\","
                "\"result\":\"PassedInertPhaseReceiptHostOnly\","
                "\"scenarios\":%u,\"checks\":%u,"
                "\"phaseReceiptNoexcept\":true,"
                "\"preCodecProofCallerSupplied\":true,"
                "\"singleAtomicWordSnapshot\":true,"
                "\"actualNativePublisherWired\":false,"
                "\"actualRuntimeBridgeWired\":false,"
                "\"nativeVmEpochProven\":false,"
                "\"fullExceptionCustodyProven\":false,"
                "\"realUnity\":false,\"R03Accepted\":false,"
                "\"H2Passed\":false,\"ReadyForHumanReviewGate\":false}\n",
                scenarios, checks);
    return 0;
}
