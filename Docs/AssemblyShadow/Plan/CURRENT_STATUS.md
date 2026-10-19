# R03 staging status — P1 execution scalar + R02 owned source

## Latest isolated P1 increment — bounded execution identity census

Primary published an additional **inactive identity-only census** at `night-outlook/il2cpp_plus@dc9c7113d8a0373532e77938a2299d011ccf3433` on this *isolated staging branch*. It reads the existing execution-class observation table only inside two separately locked scans, under initial metadata lifetime admission. It counts up to 1024 observed entries across 2048 slots, compares count + an internal slot-sensitive pointer-bit witness, rejects source changes or dropped/saturated coverage, and exports just count and scope flags. It never dereferences an `Il2CppClass*`, retains no class pointer and produces **no** executable class rows/type keys.

[Source review](../History/M07R/R03/IR_Remediation/P1_EXECUTION_IDENTITY_CENSUS_2026-10-18/PRIMARY_STAGING_REVIEW.md) · [machine evidence](../History/M07R/R03/IR_Remediation/P1_EXECUTION_IDENTITY_CENSUS_2026-10-18/EVIDENCE.json). [Native host CI 39189008508](https://github.com/night-outlook/il2cpp_plus/actions/runs/39189008508) **PASSED 3/3**, strict and sanitizer, 12 groups/profile = 72 executions, three original ZIP digests and 54/54 original manifest files verified. No installed Unity SDK, real native linker, Player or runtime/GC/RSS work was executed on this increment. The actual original registry *writer* was mocked in host fixtures; no global VM snapshot guarantee is established.

**Important dependency:** Active `codex/assembly-shadow-r01b-h1` remote heads are still demo `25d5986c5919ab70119364ce36e8b670329ad5b0` and native `5667e3712f49e4b38c7dd7359e57f81e344626da` (other two repos unchanged). The **existing one 12/75 Local source/SDK-only assignment** has no published Local return. Do not alter active source or reuse Local roots to test staging. Staging's `WEB_TO_LOCAL.md` remains **NO EXECUTION**. Reconcile that active Local result before staging promotion.

## Earlier staging — scalar header, R02 metrics and classless execution JSON

**Owner: Primary Implementation (isolated staging only). Local Validation on this branch: PAUSED.** No real Unity Editor/Player or official installed SDK compilation has been executed for the staged execution scalar/R02/classless increments. Do not promote host source validation into P1, R03, Human Review Gate, or future milestone approval.

## Current staging source and host evidence

Native isolated working branch `night-outlook/il2cpp_plus@codex/p1-execution-scalars-20261018` currently carries **`2cd731be7629d4bd0698176554720a609fcb3d10`**, descended from the still-active feature native `5667e3712f49e4b38c7dd7359e57f81e344626da`. The initial execution-header implementation and host CI was validated at staged `39d4637b868726c92f50d1db92a5c269ff0bafe5`. Two additive increments since then retain the original scalar and live-general source body unchanged:

1. `AssemblyShadowBoundedR02Metrics.h` — 22 real R02 ObservationCounters/ObservationMemo fields in original serializer order, owned fixed storage, two separate acquisitions, fail-closed on mismatched values, dropped/saturated counters, dropped class observations and unavailable coverage; pure byte-exact `r02` legacy serializer. [CI 39106258581](https://github.com/night-outlook/il2cpp_plus/actions/runs/39106258581): **3/3 PASSED**, strict/sanitized Mac/Linux, **72 group executions**, 48/48 original artifact manifest files SHA256 checked.
2. `AssemblyShadowBoundedExecutionComposite.h` — combines completed scalar-header and R02 captures into one fixed 32 KiB classless JSON fixture using the original execution serializer and fixed output Writer, rejecting missing/unfinished sources, short/invalid budget and reentry. [CI 39106675107](https://github.com/night-outlook/il2cpp_plus/actions/runs/39106675107): **3/3 PASSED**, 72 group executions, 51/51 original artifact manifest files checked. Initial CI 39106598817 failed at test harness compilation for lack of `il2cpp-config.h`; corrected with a host-only stub. Original failure retained.

Across these **two separate** suites: 6/6 success jobs, 144 executed groups and 99 manifest file bindings verified. They exercise actual real R02 counters and serializers under host fixtures. They are **not** full class-bearing execution diagnostic proof, actual VM-wide atomic epoch, class-pointer lifetime, GC/RSS, native shutdown or linked Player validation.

[Primary review](../History/M07R/R03/IR_Remediation/P1_R02_CLASSLESS_EXECUTION_2026-10-18/PRIMARY_STAGING_REVIEW.md) · [machine evidence](../History/M07R/R03/IR_Remediation/P1_R02_CLASSLESS_EXECUTION_2026-10-18/EVIDENCE.json) · [earlier bounded execution scalar review](../History/M07R/R03/IR_Remediation/P1_EXECUTION_SCALARS_2026-10-18/PRIMARY_STAGING_REVIEW.md).

## Active source authority and dependency

**Do not modify or fast-forward the active branch while its one-shot Local assignment is pending.** The authoritative `codex/assembly-shadow-r01b-h1` tuple remains:

- demo `25d5986c5919ab70119364ce36e8b670329ad5b0`
- native `5667e3712f49e4b38c7dd7359e57f81e344626da`
- HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`
- Unity package `948c0e3b4f8891481301770115e8ba4945eea6de`

The active [WEB_TO_LOCAL.md](https://github.com/night-outlook/hybridclr_demo/blob/25d5986c5919ab70119364ce36e8b670329ad5b0/Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md) authorizes exactly **one 12-component/75-native-SDK-syntax batch**, with no Unity Editor/Player. As of this staging update, there is **no published Local return** for it. The staging branch [WEB_TO_LOCAL.md](../Handoff/WEB_TO_LOCAL.md) authorizes **nothing**. All old Local-owned evidence, previous 11/10/9 PASS/FAIL source-scoped receipts and historical `source-pins.json` remain immutable.

**Next gate:** receive the active Local 12/75 factual report; independently reconcile real compilation and source/evidence custody (even if FAIL/Blocked). Only then review and choose to merge the isolated staged code into active feature, update new source/test/SDK binding and authorize a **different** Local cycle. Never attribute current active SDK PASS to the newer staged sources.

## Engineering gates still open

**P1 Incomplete:** fully coherent bounded live general+execution+R02 VM capture, class rows and Type::GetName/type-key recursion budget, metadata pointer provenance, all-VM source epoch/ABA, real GC/RSS/lock/shutdown, original allocating getter integration. **P2 NotIntegrated:** authenticated native+C# V2 file sidecar/transaction/unchanged semantic verifier. **E0 Blocked/Unavailable:** legitimate StandaloneOSX owner-safe point. **E1 BlockedByE0:** real GC/finalizer maintenance, callback drain and restart. Full P3 linked-runtime/Player validation incomplete.

Historical SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, strict original S custody Blocked and independent R03 full review FAIL/rereview NotRun remain separate from recent scoped PASS. `R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
