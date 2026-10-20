# HybridCLR Assembly Shadow

## Current — P1 shared execution-registry publisher; next source/SDK Local cycle

**Latest consumed Local Validation:** `20261020-f09e` **PASS / PassedSourceHostAndSDKOnly**, 16/16 components, 75 command-failure tests, five official managed positive products plus the exact original expected-negative, and 90/90 Unity2022.3.62f2 Apple arm64 C++17 SDK syntax configurations. The corresponding Local-owned [LOCAL_VALIDATION.md](Handoff/LOCAL_VALIDATION.md), [RETURN_TO_WEB.md](Handoff/RETURN_TO_WEB.md) and [checkpoint](History/M07R/R03/local-validation-p1-registry-revision-20261020-f09e/README.md) preserve the original executed four-SHA tuple and raw source/SDK/evidence integrity. It was NOT Unity Editor, Player, native link, metadata teardown or full R03 acceptance.

### Latest Primary source

- Native `il2cpp_plus@699dec4698a529c66e201aca1802ee8f498d8334` extracts the original execution-class observation **insertion/witness/count/revision** sequence into `AssemblyShadowExecutionRegistryPublisher.h`. The real `ObserveExecutionClass` and exact native host fixture now use the same bounded publisher, under the original registry observation lock, without new locks, heap allocations, class pointer dereferences or changing the original getter bodies.
- A new record is refused **before any witness/slot publication** when the registry revision is saturated. Existing registrations preserve the original short-circuit and memo behavior. Typed full/collision/invalid/source-rejection outcomes preserve dropped-class accounting.
- Native [host CI 39382804881](https://github.com/night-outlook/il2cpp_plus/actions/runs/39382804881) PASS 3/3 on Mac Clang/Linux Clang/GCC, **34 cases per strict/sanitized profile**: original 25 opaque/witness tests plus nine tests of the *actual publisher*. The runner's source audit requires the production CPP call and unchanged original getter/guard Git blob.
- Demo source/test anchor `hybridclr_demo@22c935c3a3bcebd1fe08bb75ba18727eaabbc9d7` hashes the new helper header, includes it in controlled fake-source tests and the official SDK syntax probe. [Integrated 75 CI](https://github.com/night-outlook/hybridclr_demo/actions/runs/39382994571), [focused command CI](https://github.com/night-outlook/hybridclr_demo/actions/runs/39382994501), and [managed/aggregate CI](https://github.com/night-outlook/hybridclr_demo/actions/runs/39382994639) PASS on macOS/Linux within host/mocked scope.

**Strict limitation:** the registration witness only authenticates admission by this observer path; it is NOT physical class-pointer ownership, metadata lifetime, a coherent VM epoch, general ABA freedom, complete execution class rows or a safe Player getter. The new helper does not enable the inactive collector. Original C#/V1/V2 transport, original reporting predicates and real engine-owner scheduler remain untouched.

### Mandatory read and next scope

1. [Plan/CURRENT_STATUS.md](Plan/CURRENT_STATUS.md), Local-owned [LOCAL_VALIDATION.md](Handoff/LOCAL_VALIDATION.md), then [RETURN_TO_WEB.md](Handoff/RETURN_TO_WEB.md).
2. [Publisher design](History/M07R/R03/IR_Remediation/P1_REGISTRY_PUBLISHER_2026-10-20/DESIGN.md), [Primary Review](History/M07R/R03/IR_Remediation/P1_REGISTRY_PUBLISHER_2026-10-20/PRIMARY_REVIEW.md), [machine evidence](History/M07R/R03/IR_Remediation/P1_REGISTRY_PUBLISHER_2026-10-20/EVIDENCE.json).
3. **One** fresh four-source-pinned 16-component/75-failure-contract/**90 native Apple SDK syntax** Local cycle specified ONLY by the final published [WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md). The previous registration-witness handoff is superseded; do not infer that it was executed. Do not use any consumed root.
4. [Remaining P1/P2/E0/E1/P3 implementation plan](History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md).

**Acceptance unchanged:** P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete. Original SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, strict S custody Blocked and independent R03 full-stage FAIL/re-review NotRun preserved. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. **No Unity Editor, Player, linked runtime, engine-owner experiments, Human Review Gate or later milestone is authorized.**
