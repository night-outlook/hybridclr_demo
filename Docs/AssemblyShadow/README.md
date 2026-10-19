# HybridCLR Assembly Shadow — isolated P1 execution staging

## Current staging increment — execution identity-only census, host CI Passed

**The latest P1 staging source is an inactive execution-class observation census**, published at native `il2cpp_plus@dc9c7113d8a0373532e77938a2299d011ccf3433` on `codex/p1-execution-scalars-20261018`. It samples the real, pre-existing 2048-slot execution-class pointer table under its original observation lock, checks that its occupied count agrees with the original maximum-1024 monotone count, rejects observable concurrent identity changes and incomplete R02 coverage, then exports **only a bounded class count**. It does NOT dereference class metadata, export raw addresses, prove class-pointer source lifetime/epoch, or produce JSON class/type-key rows.

[Actual-source review](History/M07R/R03/IR_Remediation/P1_EXECUTION_IDENTITY_CENSUS_2026-10-18/PRIMARY_STAGING_REVIEW.md) · [machine evidence](History/M07R/R03/IR_Remediation/P1_EXECUTION_IDENTITY_CENSUS_2026-10-18/EVIDENCE.json). [CI 39189008508](https://github.com/night-outlook/il2cpp_plus/actions/runs/39189008508) **PASSED 3/3 Mac/Linux jobs**, strict+ASan/UBSan, 12 groups/profile, **72 total group executions**, and three ZIP digests plus **54/54 original manifest files independently verified**. All tests are host source fixtures with mocked registry writers, NOT installed Unity SDK/Player execution. No R03 acceptance flags changed.

**Active Local remains independent:** canonical `codex/assembly-shadow-r01b-h1` source pins are untouched; its previously authorized **one 12-component/75-native-syntax installed-SDK-only Local cycle has not returned a published report**. Staging `WEB_TO_LOCAL.md` issues no Local commands. Do not merge staging into active before reconciling the active Local result.

## Prior staging increments — execution scalar header, real R02 and classless JSON

## Current — real R02 metrics and classless execution composition host-tested

**Staging only. Primary Implementation owns this work; no Local Validation command is authorized by this branch.** The active canonical `codex/assembly-shadow-r01b-h1` one-shot 12-component/75-native-syntax SDK-only handoff remains unchanged and has no published Local result. Do not merge or cherry-pick the staging source until its factual Local return is reconciled.

**Native staging source:** `night-outlook/il2cpp_plus@codex/p1-execution-scalars-20261018`, host-tested `2cd731be7629d4bd0698176554720a609fcb3d10`. The execution-header scalar source was previously tested at `39d4637b868726c92f50d1db92a5c269ff0bafe5`. This continuation adds a fixed real R02 metric capture and a fixed-buffer **classless** execution JSON composition, *without modifying the original execution getter or active branch*.

[Bounded R02 host CI 39106258581](https://github.com/night-outlook/il2cpp_plus/actions/runs/39106258581) passed **3/3 jobs** using actual `ObservationCounters` and original `AppendDiagnostics` with exact 22-field order, byte parity, zero watched new allocations after warmup and failure on missing/incomplete coverage. [Classless execution CI 39106675107](https://github.com/night-outlook/il2cpp_plus/actions/runs/39106675107) passed **3/3 jobs** using actual owned execution-header and R02 structures with exact original **classless** execution JSON bytes, bounded `32 KiB` output and fail-closed missing/partial/short writes. Both ran strict and ASan/UBSan on macOS Clang, Linux Clang/GCC, **144 total case-group executions** across the two suites. Original ZIPs and **99/99 manifest files** were independently checked. The first classless test run failed due to a missing host-only `il2cpp-config.h`; it remains a separate failed CI record.

**These tests do NOT prove actual class-bearing execution diagnostics, original Player getter integration, atomic VM epoch, R02 consistency across threads, real metadata type-key memory/GC/RSS or native teardown.** The new classless composition is a test fixture only and must not be supplied to the original semantic verifier or V2 runtime.

[New Primary staging review](History/M07R/R03/IR_Remediation/P1_R02_CLASSLESS_EXECUTION_2026-10-18/PRIMARY_STAGING_REVIEW.md) · [New machine evidence](History/M07R/R03/IR_Remediation/P1_R02_CLASSLESS_EXECUTION_2026-10-18/EVIDENCE.json) · [Prior execution scalar staging review](History/M07R/R03/IR_Remediation/P1_EXECUTION_SCALARS_2026-10-18/PRIMARY_STAGING_REVIEW.md).

## Active Local source pins — unchanged

The only active Local source+SDK assignment is [the canonical WEB_TO_LOCAL.md at demo commit 25d5986](https://github.com/night-outlook/hybridclr_demo/blob/25d5986c5919ab70119364ce36e8b670329ad5b0/Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md) on `codex/assembly-shadow-r01b-h1`:

| Repository | Active verified source SHA |
| --- | --- |
| night-outlook/hybridclr_demo | `25d5986c5919ab70119364ce36e8b670329ad5b0` |
| night-outlook/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | `5667e3712f49e4b38c7dd7359e57f81e344626da` |

**The staging branch's [WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md) is PAUSED and contains no executable Local assignment.** Preserve all historical original Local PASS/FAIL outcomes and source-pins.json. No Unity Editor/Player, Test Runner, next milestone or Human Review Gate is authorized.

## Remaining stages

**P1 Incomplete:** full coherent general/execution/R02 class and type-key capture, VM-wide epoch, class pointer provenance, GC/RSS and Shutdown drain safety, original getter integration. **P2 NotIntegrated** native/C# authenticated V2 file transaction and unchanged semantic verifier. **E0 Blocked/Unavailable**, legitimate Unity2022.3.62f2 StandaloneOSX native engine-owner safe point; **E1 BlockedByE0**, real maintenance/drain/restart. **P3 Incomplete**.

`R03Accepted=false`, `ReadyForHumanReviewGate=false`, `H2Passed=false`, `qualificationApproved=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. Historical SNAP-01/N/M/K/I/E/R02 FAIL, strict S Blocked, independent R03 FAIL/rereview NotRun and all consumed Local results remain unchanged.
