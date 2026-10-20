# HybridCLR Assembly Shadow

## Current — P1 bounded execution registry revision; next scoped Local SDK syntax validation

**Most recent completed Local Validation**: `20261019-d548`, **PASS / PassedSourceHostAndSDKOnly**, 16/16 components, 75 command-failure tests, five actual managed positive products plus the exact original expected-negative, 90/90 official Unity2022.3.62f2 native arm64 SDK syntax configurations. Immutable source/SDK/history evidence, exact executed four-SHA tuple and original failures reside in [LOCAL_VALIDATION.md](Handoff/LOCAL_VALIDATION.md), [RETURN_TO_WEB.md](Handoff/RETURN_TO_WEB.md), and [the retained checkpoint](History/M07R/R03/local-validation-p1-opaque-lifetime-20261019-d548/README.md). This was **not** Editor/Player, linked VM, Shutdown or overall R03 acceptance.

### New inactive P1 source increment
- **Native `il2cpp_plus@f09edc0499fa8baf964b80256a71ce9f4d2bd522`** adds a small saturating revision to the existing execution-class observation registry. Every successful new opaque class insertion increments it under the original short registry lock. The inactive bounded opaque collector copies the revision with each full 2,048-slot sample, rejects observed revision changes despite identical slots, rejects version saturation and returns only numeric/boolean receipts after scrubbing pointer-value scratch.
- **Demo source `hybridclr_demo@05077e54a4b350c7cce7c3efce5161a975c7719d`** binds that native revision header in source custody and the existing SDK type probe. All original 16 component scripts, **75** controlled Python contract tests and **90** native SDK syntax commands are retained.
- Native [opaque host CI](https://github.com/night-outlook/il2cpp_plus/actions/runs/39360310335) **passed 3/3** Mac/Linux Clang/GCC jobs: **21 host test cases per strict/sanitized profile**, including revision-change with unchanged slots, positive nonzero-version samples and saturation refusal. Demo [integrated 75-test CI](https://github.com/night-outlook/hybridclr_demo/actions/runs/39360193616), [command failure CI](https://github.com/night-outlook/hybridclr_demo/actions/runs/39360193811), [managed/aggregate CI](https://github.com/night-outlook/hybridclr_demo/actions/runs/39360193768) passed. Host CI is **not** proof of official installed Unity SDK or native Player execution at the new source pins.

**Strict scope:** registry-only revision is not an atomic VM epoch or general ABA-free guarantee. No class pointer metadata is dereferenced/authenticated; no nonempty execution JSON rows, type-key construction, active getter integration, process allocation/GC/RSS or real Shutdown safety follow. Original getters, R02, C# and V2 transport are unchanged.

### Required reading order
1. [CURRENT_STATUS](Plan/CURRENT_STATUS.md), Local-owned [LOCAL_VALIDATION](Handoff/LOCAL_VALIDATION.md), then [RETURN_TO_WEB](Handoff/RETURN_TO_WEB.md).
2. [New design](History/M07R/R03/IR_Remediation/P1_REGISTRY_REVISION_2026-10-20/DESIGN.md), [Primary review](History/M07R/R03/IR_Remediation/P1_REGISTRY_REVISION_2026-10-20/PRIMARY_REVIEW.md), [machine evidence](History/M07R/R03/IR_Remediation/P1_REGISTRY_REVISION_2026-10-20/EVIDENCE.json).
3. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) for the exact **one** unused root set, published four-source pins, 16/75/90 validation and stop policy.
4. [Remaining implementation plan](History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md).

### Explicit non-acceptance
P1 Incomplete, P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 Incomplete. All historical SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, original S custody Blocked, independent R03 full-stage FAIL/re-review NotRun remain factual. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. The next Local batch is **source/host/official SDK syntax only**; Unity Editor, Test Runner, Player, runtime/engine-owner experiments, Human Review Gate or later milestone remain unauthorized.
