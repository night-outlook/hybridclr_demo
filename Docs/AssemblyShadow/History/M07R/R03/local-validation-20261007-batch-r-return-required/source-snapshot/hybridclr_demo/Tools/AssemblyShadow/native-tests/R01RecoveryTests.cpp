#include <stdint.h>

#include <cstdio>
#include <cstdlib>
#include <limits>

#include "AssemblyShadowRecovery.h"

namespace
{
using il2cpp::vm::assembly_shadow_recovery::AbortRequired;
using il2cpp::vm::assembly_shadow_recovery::ActiveShadow;
using il2cpp::vm::assembly_shadow_recovery::BaselineEligibleAfterAbort;
using il2cpp::vm::assembly_shadow_recovery::BaselineUnselected;
using il2cpp::vm::assembly_shadow_recovery::CorrectInputOrAbort;
using il2cpp::vm::assembly_shadow_recovery::ErrorBadImage;
using il2cpp::vm::assembly_shadow_recovery::ErrorAlreadyCommitted;
using il2cpp::vm::assembly_shadow_recovery::ErrorBaselineAlreadyUsed;
using il2cpp::vm::assembly_shadow_recovery::ErrorBudgetMismatch;
using il2cpp::vm::assembly_shadow_recovery::ErrorCapacityExceeded;
using il2cpp::vm::assembly_shadow_recovery::ErrorClosureMemberMissing;
using il2cpp::vm::assembly_shadow_recovery::ErrorDuplicateAssemblyName;
using il2cpp::vm::assembly_shadow_recovery::ErrorInvalidState;
using il2cpp::vm::assembly_shadow_recovery::ErrorInternal;
using il2cpp::vm::assembly_shadow_recovery::ErrorInvalidArgument;
using il2cpp::vm::assembly_shadow_recovery::ErrorCapabilityUnavailable;
using il2cpp::vm::assembly_shadow_recovery::ErrorReferenceEscapesClosure;
using il2cpp::vm::assembly_shadow_recovery::ErrorReferenceResolutionFailed;
using il2cpp::vm::assembly_shadow_recovery::ErrorSuccess;
using il2cpp::vm::assembly_shadow_recovery::ErrorUnexpectedClosureMember;
using il2cpp::vm::assembly_shadow_recovery::ErrorUnsupportedAssembly;
using il2cpp::vm::assembly_shadow_recovery::RecoveryDecision;
using il2cpp::vm::assembly_shadow_recovery::RecoveryInput;
using il2cpp::vm::assembly_shadow_recovery::RestartRequired;
using il2cpp::vm::assembly_shadow_recovery::Classify;

size_t checks = 0;

struct Expected
{
    int disposition;
    bool abortAllowed;
    bool requireStartupValidation;
};

RecoveryInput Input(int32_t state, bool published, bool terminalFailure,
                    bool poisoned, bool knownBaselineUseRejection, int32_t lastError)
{
    RecoveryInput input = { state, published, terminalFailure, poisoned,
                            knownBaselineUseRejection, lastError };
    return input;
}

void Check(bool condition, const char* message)
{
    ++checks;
    if (!condition)
    {
        std::fprintf(stderr, "R01 recovery check failed: %s\n", message);
        std::fflush(stderr);
        std::exit(1);
    }
}

void CheckDecision(const RecoveryInput& input, const Expected& expected, const char* label)
{
    const RecoveryDecision actual = Classify(input);
    Check(static_cast<int>(actual.disposition) == expected.disposition, label);
    Check(actual.abortAllowed == expected.abortAllowed, label);
    Check(actual.requireStartupValidation == expected.requireStartupValidation, label);
}

void TestStateTable()
{
    // This table is the contract oracle.  It is deliberately written as
    // expected values instead of calling any helper from the implementation.
    struct StateCase
    {
        int32_t state;
        bool published;
        Expected expected;
    } cases[] = {
        { 0, false, { BaselineUnselected, false, true } },
        { 1, false, { BaselineUnselected, false, true } },
        { 2, false, { CorrectInputOrAbort, true, true } },
        { 3, false, { CorrectInputOrAbort, true, true } },
        { 4, false, { CorrectInputOrAbort, true, true } },
        { 5, false, { RestartRequired, false, true } },
        { 6, true, { ActiveShadow, false, false } },
        { 7, false, { BaselineEligibleAfterAbort, false, true } },
        { 8, false, { RestartRequired, false, true } },
        { 9, false, { RestartRequired, false, true } },
        { -1, false, { RestartRequired, false, true } },
        { 10, false, { RestartRequired, false, true } },
        { std::numeric_limits<int32_t>::min(), false, { RestartRequired, false, true } },
        { std::numeric_limits<int32_t>::max(), false, { RestartRequired, false, true } },
    };

    for (size_t i = 0; i < sizeof(cases) / sizeof(cases[0]); ++i)
        CheckDecision(Input(cases[i].state, cases[i].published, false, false, false,
                            ErrorSuccess), cases[i].expected, "state table");
}

void TestErrorFamilies()
{
    // Every input error is checked independently against the recovery table.
    // A correctable error remains a description of the caller's choices; it
    // never elects baseline automatically.
    struct ErrorCase
    {
        int32_t error;
        Expected expected;
    } cases[] = {
        { ErrorSuccess, { CorrectInputOrAbort, true, true } },
        { ErrorInvalidArgument, { CorrectInputOrAbort, true, true } },
        { ErrorDuplicateAssemblyName, { CorrectInputOrAbort, true, true } },
        { ErrorBadImage, { CorrectInputOrAbort, true, true } },
        { ErrorUnsupportedAssembly, { CorrectInputOrAbort, true, true } },
        { ErrorClosureMemberMissing, { CorrectInputOrAbort, true, true } },
        { ErrorUnexpectedClosureMember, { CorrectInputOrAbort, true, true } },
        { ErrorReferenceResolutionFailed, { CorrectInputOrAbort, true, true } },
        { ErrorReferenceEscapesClosure, { CorrectInputOrAbort, true, true } },
        { ErrorCapacityExceeded, { CorrectInputOrAbort, true, true } },
        { ErrorBudgetMismatch, { CorrectInputOrAbort, true, true } },
        { ErrorCapabilityUnavailable, { CorrectInputOrAbort, true, true } },
        { ErrorBaselineAlreadyUsed, { AbortRequired, true, true } },
        { ErrorInvalidState, { RestartRequired, false, true } },
        { ErrorInternal, { RestartRequired, false, true } },
        { 25, { RestartRequired, false, true } },
        { std::numeric_limits<int32_t>::min(), { RestartRequired, false, true } },
        { std::numeric_limits<int32_t>::max(), { RestartRequired, false, true } },
    };

    for (size_t i = 0; i < sizeof(cases) / sizeof(cases[0]); ++i)
        CheckDecision(Input(2, false, false, false, false, cases[i].error),
                      cases[i].expected, "error family table");

    // The durable observation is independent from the mutable error slot.
    CheckDecision(Input(2, false, false, false, true, ErrorSuccess),
                  { AbortRequired, true, true }, "known baseline use fact");
    CheckDecision(Input(2, false, false, false, true, ErrorBadImage),
                  { AbortRequired, true, true }, "known baseline use dominates input error");
}

void TestErrorsAlwaysRestart()
{
    const int32_t states[] = { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, 10 };
    const int32_t errors[] = {
        ErrorInternal, 25, std::numeric_limits<int32_t>::min(),
        std::numeric_limits<int32_t>::max()
    };
    const Expected expected = { RestartRequired, false, true };

    for (size_t state = 0; state < sizeof(states) / sizeof(states[0]); ++state)
        for (size_t error = 0; error < sizeof(errors) / sizeof(errors[0]); ++error)
            CheckDecision(Input(states[state], false, false, false, false, errors[error]),
                          expected, "unknown/internal error always restarts");
}

void TestKnownErrorDomainAndMutableResults()
{
    // Every preserved 0..21 value and every R01 value is recognized.  The
    // classifier remains conservative during staging for errors without an
    // explicit corrective path, while a known mutable result cannot erase a
    // clean Aborted or healthy published Committed state.
    const int32_t knownErrors[] = {
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
        13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24
    };
    const Expected active = { ActiveShadow, false, false };
    const Expected baseline = { BaselineEligibleAfterAbort, false, true };
    for (size_t i = 0; i < sizeof(knownErrors) / sizeof(knownErrors[0]); ++i)
    {
        if (knownErrors[i] == ErrorInternal)
        {
            CheckDecision(Input(6, true, false, false, false, knownErrors[i]),
                          { RestartRequired, false, true },
                          "internal remains terminal in committed state");
            CheckDecision(Input(7, false, false, false, false, knownErrors[i]),
                          { RestartRequired, false, true },
                          "internal remains terminal in aborted state");
        }
        else
        {
            CheckDecision(Input(6, true, false, false, false, knownErrors[i]),
                          active, "known mutable result preserves active shadow");
            CheckDecision(Input(7, false, false, false, false, knownErrors[i]),
                          baseline, "known mutable result preserves clean abort");
        }
    }
    CheckDecision(Input(6, true, false, false, false, ErrorAlreadyCommitted),
                  active, "rejected Abort or Commit leaves active shadow");
    CheckDecision(Input(6, true, false, false, false, ErrorInvalidState),
                  active, "wrong-state result leaves active shadow");
}

void TestTerminalFailurePrecedence()
{
    // These rows model a durable failure retained after an incorrect
    // Abort/Commit/Success attempt overwrote the mutable last-error slot.
    struct TerminalCase
    {
        int32_t state;
        bool published;
        int32_t lastError;
    } cases[] = {
        { 2, false, ErrorSuccess },
        { 3, false, ErrorSuccess },
        { 4, false, ErrorSuccess },
        { 5, false, ErrorSuccess },
        { 6, true, ErrorSuccess },
        { 7, false, ErrorSuccess },
        { 8, false, ErrorSuccess },
        { 9, false, ErrorSuccess },
        { 2, false, ErrorInvalidArgument },
        { 6, true, ErrorSuccess },
    };
    const Expected expected = { RestartRequired, false, true };
    for (size_t i = 0; i < sizeof(cases) / sizeof(cases[0]); ++i)
        CheckDecision(Input(cases[i].state, cases[i].published, true, false, false,
                            cases[i].lastError), expected, "terminal failure dominates");

    // Poison is also fail-closed even when the publication tuple otherwise
    // describes a healthy committed shadow.
    CheckDecision(Input(6, true, false, true, false, ErrorSuccess),
                  expected, "poisoned committed state");
    CheckDecision(Input(7, false, false, true, false, ErrorSuccess),
                  expected, "poisoned aborted state");
}

void TestPublicationContradictions()
{
    const Expected expected = { RestartRequired, false, true };
    // Published is only coherent with Committed.
    const int32_t unpublishedStates[] = { 0, 1, 2, 3, 4, 5, 7, 8, 9, -1 };
    for (size_t i = 0; i < sizeof(unpublishedStates) / sizeof(unpublishedStates[0]); ++i)
        CheckDecision(Input(unpublishedStates[i], true, false, false, false, ErrorSuccess),
                      expected, "published non-committed contradiction");
    CheckDecision(Input(6, false, false, false, false, ErrorSuccess),
                  expected, "committed unpublished contradiction");
    CheckDecision(Input(6, true, false, false, true, ErrorSuccess),
                  expected, "published baseline-use contradiction");
    CheckDecision(Input(7, false, false, false, true, ErrorSuccess),
                  { BaselineEligibleAfterAbort, false, true },
                  "aborted baseline-use remains baseline eligible");

    // A stale mutable error cannot downgrade the state-derived recovery
    // decision after publication or a clean abort.
    CheckDecision(Input(6, true, false, false, false, ErrorBaselineAlreadyUsed),
                  { ActiveShadow, false, false }, "published stale baseline-use error");
    CheckDecision(Input(7, false, false, false, false, ErrorBadImage),
                  { BaselineEligibleAfterAbort, false, true }, "aborted stale input error");
}

void TestRecoverySequences()
{
    // Model the production call order: a pre-publication baseline-use guard
    // requests Abort, Abort reaches Aborted, and a later wrong-state call only
    // changes mutable lastError.  The clean Aborted decision survives it.
    RecoveryInput attempt = Input(2, false, false, false, true, ErrorBaselineAlreadyUsed);
    CheckDecision(attempt, { AbortRequired, true, true },
                  "sequence: pre-publication baseline use requires abort");
    attempt = Input(7, false, false, false, true, ErrorSuccess);
    CheckDecision(attempt, { BaselineEligibleAfterAbort, false, true },
                  "sequence: successful abort permits baseline validation");
    attempt = Input(7, false, false, false, true, ErrorInvalidState);
    CheckDecision(attempt, { BaselineEligibleAfterAbort, false, true },
                  "sequence: rejected post-abort call preserves eligibility");

    // After publication, a rejected Commit/Abort leaves the active world
    // healthy; only a durable terminal/poison flag can change this result.
    attempt = Input(6, true, false, false, false, ErrorAlreadyCommitted);
    CheckDecision(attempt, { ActiveShadow, false, false },
                  "sequence: rejected commit preserves active shadow");
    attempt = Input(6, true, true, false, false, ErrorSuccess);
    CheckDecision(attempt, { RestartRequired, false, true },
                  "sequence: terminal flag dominates later success");
}

} // namespace

int main()
{
    TestStateTable();
    TestErrorFamilies();
    TestErrorsAlwaysRestart();
    TestKnownErrorDomainAndMutableResults();
    TestTerminalFailurePrecedence();
    TestPublicationContradictions();
    TestRecoverySequences();
    std::printf("r01_recovery_checks=%zu PASS\n", checks);
    return 0;
}
