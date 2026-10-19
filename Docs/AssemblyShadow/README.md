# HybridCLR Assembly Shadow

## Current — opaque-inventory receipt fail-stop correction; new Local source/SDK-only cycle

**Latest completed Local Validation**: 20261019-48ee **PASS / PassedSourceHostAndSDKOnly**, 15/15 independently receipted host/SDK components, **70** source-bound command-failure tests, five positive managed compilation products plus the original exact expected-negative, **85/85** installed Unity2022.3.62f2 arm64 native syntax checks; sources, SDK and historical evidence preserved. This completed cycle is consumed. It did **not** launch Unity Editor/Player or establish VM-wide coherence, pointer provenance, shutdown, linking or full R03 acceptance. Read the Local-owned [LOCAL_VALIDATION.md](Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB.md](Handoff/RETURN_TO_WEB.md) as the factual authority.

### Reconciled newer native source

The separately published inactive native opaque inventory at `night-outlook/il2cpp_plus@5e2326a45bd6070aa25830ca8c0236e1915bde13` copies and checks zero or nonzero observed class **pointer identities only** from the 2,048-slot native registry. It never dereferences or returns class pointers and has no original getter/Player caller. Its exact production header/source under VM mocks passed [native CI 39244090056](https://github.com/night-outlook/il2cpp_plus/actions/runs/39244090056) on macOS Clang/Linux Clang/GCC, 18 distinct groups per strict/sanitized profile. The original handoff at demo d4daea59682ffd14a8ff8b282c280733bcecb3d8 covered 16 host/SDK components and 90 planned native SDK syntax checks but has **no corresponding newer Local result recorded** in the current published Local-owned report. Do not claim that batch ran or that it passed.

### Primary finding and corrective source

Independent review identified a fail-stop parity gap: the newer `opaque-inventory` producer includes `commandLifetimeUnverified` in its `RESULT.json`, but the outer aggregate consumer required a typed marker only for `empty-live`. On a completed opaque child with a missing/unparseable summary, the outer logic could continue unrelated children despite uncertainty about native compiler descendants. This is a **source-path defect and controlled regression**, not an observed failure in any consumed Local PASS.

Demo source/test/CI anchor **`d548799cc026b2ca78b40b7289fed404a3e8ec96`** now requires an explicit boolean lifetime marker for **both** `empty-live` and `opaque-inventory`, converts missing/malformed receipts into an uncertain-lifetime stop and `NotRun` later cells, and retains ordinary known nonzero behavior. Five new source-bound negative tests (nested uncertainty, absent marker, malformed string, null marker, missing result) increase the integrated inventory from **70 to 75 = 5 + 14 + 34 + 10 + 12**. [Focused CI 39256679075](https://github.com/night-outlook/hybridclr_demo/actions/runs/39256679075), [integrated 75-test CI 39256679128](https://github.com/night-outlook/hybridclr_demo/actions/runs/39256679128) and [managed/aggregate CI 39256679215](https://github.com/night-outlook/hybridclr_demo/actions/runs/39256679215) passed on macOS and Linux. These runs are host/mocked tests; they do not supersede official installed SDK syntax or Player evidence.

**Next action: one NEW 16-component, 75-contract and 90-native-syntax source/host/installed SDK Local cycle** is permitted solely by the final Docs-only [WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md) and its verified four-repository pins. The former opaque source handoff is superseded by the code change; no result from it may be inferred. Do not rerun the completed 15/15 cycle or reuse any consumed root. No Unity Editor/Player, runtime seven-root, scheduler/engine-owner experiment, Human Review Gate or later milestone.

### Read order

1. [Plan/CURRENT_STATUS.md](Plan/CURRENT_STATUS.md), Local-owned [LOCAL_VALIDATION.md](Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB.md](Handoff/RETURN_TO_WEB.md).
2. [New defect/design](History/M07R/R03/IR_Remediation/P1_OPAQUE_LIFETIME_2026-10-19/DESIGN.md), [Primary review](History/M07R/R03/IR_Remediation/P1_OPAQUE_LIFETIME_2026-10-19/PRIMARY_REVIEW.md), [CI/source evidence](History/M07R/R03/IR_Remediation/P1_OPAQUE_LIFETIME_2026-10-19/EVIDENCE.json).
3. Full [WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md) for precise batch, root admission, source pins and stop policy.
4. [Original remaining P1/P2/E0/E1/P3 plan](History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md).

**No change in acceptance:** P1 Incomplete (class metadata origin/lifetime, all-VM epoch/ABA, type keys, getter integration, GC/RSS, locks/Shutdown), P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 Incomplete. Historical SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, original strict S custody Blocked and R03 independent full-stage FAIL/re-review NotRun are preserved. `R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled.
