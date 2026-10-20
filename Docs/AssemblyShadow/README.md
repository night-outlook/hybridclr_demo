# HybridCLR Assembly Shadow

## Current — P1 inactive execution registration-source witnesses

**Latest consumed Local Validation:** 20261020-f09e PASS / PassedSourceHostAndSDKOnly. Exactly 16/16 components, 75 command-failure tests, five official managed positive products plus original exact expected-negative, and 90/90 actual Unity2022.3.62f2 Apple arm64 native C++17 syntax configurations. Source, SDK and historical evidence were preserved. This does NOT establish Unity Editor/Player execution, linked runtime, native metadata teardown or R03 acceptance. The original [LOCAL_VALIDATION.md](Handoff/LOCAL_VALIDATION.md), [RETURN_TO_WEB.md](Handoff/RETURN_TO_WEB.md) and [consumed checkpoint](History/M07R/R03/local-validation-p1-registry-revision-20261020-f09e/README.md) remain the factual authority.

### New Primary source increment

Native source commit **f0cb6f9f7a80c0601b5bc95c1a1cdda78a116e16** attaches an INACTIVE, write-once source witness to each successful native execution-class registry insertion. Every record stores only an opaque pointer value and Candidate/ActiveShadow registration role under the original observation lock. The inactive opaque collector now refuses nonempty slots without matching registered witnesses, mismatched identities and phantom witnesses in empty slots. It keeps the existing revision/slot comparison and returns only counts/booleans after scrubbing pointer scratch. Original C++ getters, C# APIs, V1/V2 semantic/transport paths remain unchanged.

**Registration-path witness is NOT actual physical class-pointer provenance.** The code never dereferences or returns these witnessed values during collection. It does not establish pointer lifetime, safe type-key acquisition, global VM epoch/ABA freedom, original getter integration, allocator/GC/RSS or Shutdown/lock safety.

Native [host CI 39366349420](https://github.com/night-outlook/il2cpp_plus/actions/runs/39366349420) PASSED 3/3 macOS Clang/Linux Clang/GCC, with **25 distinct strict and 25 ASan/UBSan groups per host**. The earlier source-audit label mismatch [CI 39366207558](https://github.com/night-outlook/il2cpp_plus/actions/runs/39366207558) remains historical FAIL; only the source-checker string was corrected. Demo source/test anchor **d7cbcc9deeb3d8f384887826bb8d65cec8324641** binds the new witness header to source custody and SDK syntax. [Integrated 75-test CI 39366390774](https://github.com/night-outlook/hybridclr_demo/actions/runs/39366390774), [focused command CI 39366390772](https://github.com/night-outlook/hybridclr_demo/actions/runs/39366390772) and [managed/aggregate CI 39366390737](https://github.com/night-outlook/hybridclr_demo/actions/runs/39366390737) PASSED within host/mock scope. These are NOT new official installed SDK or Player evidence.

**Next Local authority:** exactly ONE fresh source/host/installed SDK syntax-only cycle using the final pushed Docs-only [WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md) and exact four-repository pins: 16 independent components, 75 command-failure tests, opaque-inventory 2×25 groups, 90 official native SDK syntax configurations (18 translation units × five profiles), original five positive managed products + expected-negative. All prior PASS/FAIL/Blocked P1 results and evidence roots are consumed; do not rerun. No Unity Editor, Test Runner, Player, scheduler/engine-owner experiment, Human Review Gate or later milestone.

### Read order

1. [CURRENT_STATUS](Plan/CURRENT_STATUS.md), Local-owned [LOCAL_VALIDATION](Handoff/LOCAL_VALIDATION.md), then [RETURN_TO_WEB](Handoff/RETURN_TO_WEB.md).
2. [Focused design](History/M07R/R03/IR_Remediation/P1_REGISTRATION_WITNESS_2026-10-20/DESIGN.md), [Primary review](History/M07R/R03/IR_Remediation/P1_REGISTRATION_WITNESS_2026-10-20/PRIMARY_REVIEW.md), [source/CI evidence](History/M07R/R03/IR_Remediation/P1_REGISTRATION_WITNESS_2026-10-20/EVIDENCE.json).
3. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) for exactly one pinned source/SDK validation.
4. [Remaining P1/P2/E0/E1/P3 implementation plan](History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md).

**Acceptance unchanged:** P1 Incomplete, P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 Incomplete. Original SNAP-01/N/M/K/I/E/R02 immutable fingerprint FAIL, strict S custody Blocked and independent R03 full-stage FAIL/re-review NotRun preserved. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; PureInterpreter disabled.
