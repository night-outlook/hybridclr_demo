// D1 source-host fault matrix. The "registries", "usage flag", Codec and
// snapshot are test-owned counters only. NOT a native publication integration.
// Each scenario is a separate process; no actual Unity/IL2CPP callbacks.
#include "vm/AssemblyShadowPublicationPhaseReceipt.h"
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <stdexcept>

using namespace il2cpp::vm::assembly_shadow_publication;
static unsigned checks = 0;
static void Check(bool ok, const char* expr, int line)
{
    ++checks;
    if (!ok) { std::fprintf(stderr, "D1 fault host FAIL %d: %s\n", line, expr); std::abort(); }
}
#define CHECK(x) Check(bool(x), #x, __LINE__)

struct MockNativePublication
{
    PublicationPhaseReceipt receipt;
    bool usageHeld = false;
    bool physicalAppended = false;
    bool cliAppended = false;
    bool codecAttempted = false;
    bool codecReturnedSuccess = false;
    bool nativeActive = false;

    void Usage()
    {
        CHECK(receipt.Advance(Phase::UsageAdmitted));
        usageHeld = true;
    }
    void Registries()
    {
        CHECK(usageHeld);
        CHECK(receipt.Advance(Phase::RegistriesAppended));
        physicalAppended = true;
        cliAppended = true;
    }
    void AttemptCodec()
    {
        CHECK(physicalAppended && cliAppended && usageHeld);
        // Marker is written BEFORE the hypothetical Codec invocation.
        CHECK(receipt.Advance(Phase::CodecAttempted));
        codecAttempted = true;
    }
    void PublishGroup()
    {
        CHECK(codecAttempted);
        CHECK(receipt.Advance(Phase::RuntimeGroupPublished));
        codecReturnedSuccess = true;
    }
    void Activate()
    {
        CHECK(codecReturnedSuccess);
        CHECK(receipt.Advance(Phase::ActiveSnapshotPublished));
        nativeActive = true;
        usageHeld = false;
    }
    void Initializers()
    {
        CHECK(nativeActive);
        CHECK(receipt.Advance(Phase::InitializersRunning));
    }

    // A simplified owned cleanup for pre-codec source-host cases only.
    // Does not attest to actual native source, metadata lifetimes or readers.
    PreCodecCleanupProof TestCleanupBeforeCodec(bool omitPhysical = false)
    {
        CHECK(!codecAttempted);
        if (!omitPhysical) physicalAppended = false;
        cliAppended = false;
        usageHeld = false;
        const PreCodecCleanupProof proof = {
            !codecAttempted, !physicalAppended, !cliAppended, !usageHeld
        };
        return proof;
    }
    void TerminalOnUnknown(Reason reason)
    {
        receipt.MarkTerminal(reason);
    }
};

static void EndCase(const char* caseName, MockNativePublication& m,
                    Phase phase, Outcome outcome, Reason reason,
                    bool validated, bool terminal)
{
    const Snapshot snap = m.receipt.Read();
    CHECK(snap.phase == phase);
    CHECK(snap.outcome == outcome);
    CHECK(snap.reason == reason);
    CHECK(m.receipt.MayReturnValidated() == validated);
    CHECK(m.receipt.RestartRequired() == terminal);
    if (terminal)
    {
        CHECK(!m.receipt.RejectBeforeCodec({true, true, true, true}));
        CHECK(!m.receipt.Complete());
    }
    std::printf("{\"schema\":\"R03B2D1PublicationPhaseFaultHostV1\","
        "\"result\":\"PassedInertFaultScenarioOnly\","
        "\"case\":\"%s\",\"phase\":%u,\"outcome\":%u,\"reason\":%u,"
        "\"checks\":%u,\"canReturnValidated\":%s,\"terminal\":%s,"
        "\"simulatedNativeStateOnly\":true,"
        "\"actualCodecAttempted\":false,\"nativeIntegration\":false,"
        "\"realUnity\":false,\"R03Accepted\":false,"
        "\"H2Passed\":false,\"ReadyForHumanReviewGate\":false}\n",
        caseName, unsigned(static_cast<uint8_t>(snap.phase)),
        unsigned(static_cast<uint8_t>(snap.outcome)),
        unsigned(static_cast<uint8_t>(snap.reason)), checks,
        validated ? "true" : "false", terminal ? "true" : "false");
}

int main(int argc, char** argv)
{
    if (argc != 2) { std::fputs("expected one fault case\n", stderr); return 2; }
    const char* name = argv[1];
    MockNativePublication m;
    if (std::strcmp(name, "preflight-clean") == 0)
    {
        CHECK(m.receipt.RejectBeforeCodec(m.TestCleanupBeforeCodec()));
        EndCase(name, m, Phase::Prepared, Outcome::RejectedBeforeCodec,
                Reason::ProvenPreCodecRejection, true, false);
    }
    else if (std::strcmp(name, "usage-clean") == 0)
    {
        m.Usage();
        CHECK(m.receipt.RejectBeforeCodec(m.TestCleanupBeforeCodec()));
        EndCase(name, m, Phase::UsageAdmitted, Outcome::RejectedBeforeCodec,
                Reason::ProvenPreCodecRejection, true, false);
    }
    else if (std::strcmp(name, "registries-clean") == 0)
    {
        m.Usage(); m.Registries();
        CHECK(m.receipt.RejectBeforeCodec(m.TestCleanupBeforeCodec()));
        EndCase(name, m, Phase::RegistriesAppended, Outcome::RejectedBeforeCodec,
                Reason::ProvenPreCodecRejection, true, false);
    }
    else if (std::strcmp(name, "registry-cleanup-unverified") == 0)
    {
        m.Usage(); m.Registries();
        CHECK(!m.receipt.RejectBeforeCodec(m.TestCleanupBeforeCodec(true)));
        EndCase(name, m, Phase::RegistriesAppended, Outcome::TerminalRestartRequired,
                Reason::MissingCleanupProof, false, true);
    }
    else if (std::strcmp(name, "codec-unknown-throw") == 0)
    {
        m.Usage(); m.Registries(); m.AttemptCodec();
        bool caught = false;
        try { throw std::runtime_error("injected Codec exception"); }
        catch (const std::runtime_error&) { caught = true; m.TerminalOnUnknown(Reason::CodecOutcomeUnknown); }
        CHECK(caught);
        EndCase(name, m, Phase::CodecAttempted, Outcome::TerminalRestartRequired,
                Reason::CodecOutcomeUnknown, false, true);
    }
    else if (std::strcmp(name, "post-group-throw") == 0)
    {
        m.Usage(); m.Registries(); m.AttemptCodec(); m.PublishGroup();
        bool caught = false;
        try { throw std::runtime_error("injected Runtime group exception"); }
        catch (const std::runtime_error&) { caught = true; m.TerminalOnUnknown(Reason::NativePublicationFailure); }
        CHECK(caught);
        CHECK(!m.nativeActive && m.codecReturnedSuccess);
        EndCase(name, m, Phase::RuntimeGroupPublished, Outcome::TerminalRestartRequired,
                Reason::NativePublicationFailure, false, true);
    }
    else if (std::strcmp(name, "post-active-throw") == 0)
    {
        m.Usage(); m.Registries(); m.AttemptCodec(); m.PublishGroup(); m.Activate();
        bool caught = false;
        try { throw std::runtime_error("injected after VM activation exception"); }
        catch (const std::runtime_error&) { caught = true; m.TerminalOnUnknown(Reason::SnapshotOwnershipUnverified); }
        CHECK(caught && m.nativeActive);
        EndCase(name, m, Phase::ActiveSnapshotPublished, Outcome::TerminalRestartRequired,
                Reason::SnapshotOwnershipUnverified, false, true);
    }
    else if (std::strcmp(name, "initializer-throw") == 0)
    {
        m.Usage(); m.Registries(); m.AttemptCodec(); m.PublishGroup(); m.Activate(); m.Initializers();
        bool caught = false;
        try { throw std::runtime_error("injected initializer exception"); }
        catch (const std::runtime_error&) { caught = true; m.TerminalOnUnknown(Reason::InitializerFailure); }
        CHECK(caught);
        EndCase(name, m, Phase::InitializersRunning, Outcome::TerminalRestartRequired,
                Reason::InitializerFailure, false, true);
    }
    else if (std::strcmp(name, "completed") == 0)
    {
        m.Usage(); m.Registries(); m.AttemptCodec(); m.PublishGroup(); m.Activate(); m.Initializers();
        CHECK(m.receipt.Complete());
        EndCase(name, m, Phase::InitializersRunning, Outcome::Complete,
                Reason::None, false, false);
    }
    else { std::fputs("unknown fault scenario\n", stderr); return 2; }
    return 0;
}
