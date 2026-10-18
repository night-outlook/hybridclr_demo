# HybridCLR Assembly Shadow

## Current — P1 inactive live-source general V1 bridge published; local SDK-only validation pending

**Primary Implementation has published a new inactive native live-source collector and its bounded, single-owner source test.** The canonical branch is `codex/assembly-shadow-r01b-h1`. The latest source/host-tested native increment is `night-outlook/il2cpp_plus@5667e3712f49e4b38c7dd7359e57f81e344626da`; the demo source/CLI CI anchor is `night-outlook/hybridclr_demo@d7b923e9d97b89d67149d6f659d61546a966de6f`. [Primary source review](History/M07R/R03/IR_Remediation/P1_INACTIVE_LIVE_GENERAL_2026-10-17/PRIMARY_REVIEW.md) · [machine evidence](History/M07R/R03/IR_Remediation/P1_INACTIVE_LIVE_GENERAL_2026-10-17/EVIDENCE.json).

### Implemented and verified at source level

The new `AssemblyShadow::TryCaptureBoundedGeneralLive` is **inactive** and takes caller-prewarmed, preallocated owned capture objects, keeps the source metadata lifetime ticket active from initial sample through final composition, and runs the existing bounded transaction, first-use, physical assembly and ordinary-class readers **sequentially without nesting their source mutexes**. It rejects witnessed changes in active/candidate/configuration/failure/diagnostic/usage source publications **before collection, after collection, and after frozen general JSON output**. Source and startup-name corruption, closed admission, child error, output corruption or attempted reuse cannot be turned into partial success.

**A stable read fence is not a coherent all-VM epoch.** It cannot rule out ABA, untracked metadata or R02 counter changes, physical class pointer provenance, GC/RSS costs or Shutdown deadlock. The original `GetDiagnosticsJson` / `GetExecutionDiagnosticsJson` getters, C# Player APIs and all semantic/transport guards remain unchanged and do not call the new bridge.

[Native host CI 39085622437](https://github.com/night-outlook/il2cpp_plus/actions/runs/39085622437) **PASSED 3/3** on macOS Apple Clang and Linux Clang/GCC: strict and ASan/UBSan, **13 distinct tests/profile**, 78 total groups, actual source method compiled against real owned capture types and explicitly mocked VM source methods. Three ZIP digests and **57/57 original artifact files** were independently checked. [Demo aggregate/managed receipt CI 39085881448](https://github.com/night-outlook/hybridclr_demo/actions/runs/39085881448) **PASSED 2/2** Mac/Linux jobs (five original CLI + fourteen aggregate/receipt tests per OS); two ZIP digests and **10/10 original artifact files** were verified. The new fake-child regression refuses a complete batch when the live-general host component fails, even if both SDK compiler children pass.

**The next authorized Local step is limited to one new `12/12` host + installed Unity2022.3.62f2 official SDK syntax-only batch**, preserving the original five managed products/expected-negative and the existing **75 native syntax configurations** (15 units × 5 profiles). The actual `AssemblyShadow.cpp` now includes the source bridge so SDK syntax validates the full translation unit across those profiles. **No Unity Editor/Player execution, real runtime batch, Human Review Gate or next milestone is authorized.** See [WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md).

### Exact older empirical outcomes — consumed, never reclassified

| Local cycle | Factual result | State |
| --- | --- | --- |
| `20261016-3dc9` | PASS / `PassedSourceHostAndSDKOnly`, 11/11, 75 native syntax | Consumed |
| `20261016-f598` | PASS / `PassedSourceHostAndSDKOnly`, 10/10, 70 native syntax | Consumed |
| `20261016-0620` | PASS / `PassedSourceHostAndSDKOnly`, 10/10, 70 native syntax | Consumed |
| `20261016-0a0b` | FAIL / `FailedOrIncomplete`, 9/10, original false aggregate SDK flag | Consumed and unchanged |

All original SNAP-01/N/M/K/I/E failures, historical R02 whole-file source-fingerprint FAIL, strict original S custody Blocked and the independent full-stage R03 FAIL/re-review NotRun remain unchanged. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.

### Remaining engineering scope

**P1 Incomplete:** original live getter integration, source-pointer origin, one genuinely coherent VM-wide epoch, complete R02/execution capture, type-key/class iterator worst-case allocation/GC/RSS and true VM lock/shutdown safety. **P2 NotIntegrated** (actual authenticated native/C# V2 sidecar/transaction and unchanged semantic verifier). **E0 Blocked/Unavailable** (source-supported Unity2022.3.62f2 StandaloneOSX native engine-owner safe point). **E1 BlockedByE0** (native maintenance, callback drain and restart). **P3 Incomplete:** source/SDK syntax does not qualify a linked Player.

### Mandatory read order

1. [Plan/CURRENT_STATUS.md](Plan/CURRENT_STATUS.md), then Local-owned [LOCAL_VALIDATION.md](Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB.md](Handoff/RETURN_TO_WEB.md).
2. [Primary design/source review](History/M07R/R03/IR_Remediation/P1_INACTIVE_LIVE_GENERAL_2026-10-17/PRIMARY_REVIEW.md) and [evidence](History/M07R/R03/IR_Remediation/P1_INACTIVE_LIVE_GENERAL_2026-10-17/EVIDENCE.json).
3. [WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md) for the single source/SDK-only executable command and stop boundary.
4. [Remaining implementation plan](History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md).

[Previous full current-status and owned-general Local reconciliation](https://github.com/night-outlook/hybridclr_demo/blob/97c3563ba0c36303c19a4ecd00f1ad4004f50e85/Docs/AssemblyShadow/README.md) remains preserved in Git; superseded authorizations are not active.
