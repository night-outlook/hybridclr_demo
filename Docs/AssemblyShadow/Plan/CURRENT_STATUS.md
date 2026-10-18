# R03 P1 current status — inactive live general-source bridge host-tested; next Local SDK preflight

## Current bounded assignment

Primary has authored and published a native `AssemblyShadow::TryCaptureBoundedGeneralLive` method that **combines actual separately implemented source readers** and feeds the previously reviewed byte-exact owned-general composer under one MetadataLifetimeGate.Reader admission, then rejects **observed** before/after source changes. The implementation remains **inactive**, is not called from original general/execution getters, and is not a live Player diagnostic replacement. No coherent global VM epoch, physical class source/lifetime, metadata teardown safety or process GC/RSS bound is established.

**Source/host testing status: PASS within mocks only.** [Native CI 39085622437](https://github.com/night-outlook/il2cpp_plus/actions/runs/39085622437) passed 3/3 (Mac Clang, Linux Clang/GCC), strict and ASan/UBSan with 13 distinct groups/profile, exact native source body extracted/included against actual Capture and serializer types; 57/57 original manifest files verified. [Demo CI 39085881448](https://github.com/night-outlook/hybridclr_demo/actions/runs/39085881448) passed 2/2 OS jobs (5 CLI +14 managed receipt/aggregate tests/OS), 10/10 original manifest files verified. CI hosts mock all installed SDK/VM inputs; a host success is not official installed SDK evidence.

**Next authorized Local Validation is only ONE fresh, separately committed and source-pinned host/SDK syntax-only cycle**, with **12 independently receipted components** (the previous 11 plus `live-general`) and **75 actual C++17 macOS arm64 native syntax configurations** (15 units × 5 profiles), plus five official managed product outputs and the unchanged expected-negative control. The full source preflight script and exact new roots live in [WEB_TO_LOCAL.md](../Handoff/WEB_TO_LOCAL.md). No Unity Editor/Player Test Runner, runtime seven-root batch, source/engine adapter experiment, H2/X02/M08A or Human Review Gate may run. Local only validates and records factual evidence; all substantive design/changes remain Primary-owned.

## Exact source pins and source of truth

All four canonical `night-outlook/<repo>` remotes use branch `codex/assembly-shadow-r01b-h1`. The source/CI tested native implementation is `il2cpp_plus@5667e3712f49e4b38c7dd7359e57f81e344626da`, the demo CLI/producer integration CI anchor is `hybridclr_demo@d7b923e9d97b89d67149d6f659d61546a966de6f`, the HybridCLR fork remains `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` and Unity package remains `948c0e3b4f8891481301770115e8ba4945eea6de`.

Later demo `Docs/` publications do not alter the tested source. The precise authoritative demo Local-execution pin will be the **final remote handoff-containing commit** and must be matched against checkout HEAD and the Primary Local-agent prompt. No prior Local execution SHA may be replaced by a later transport commit; historical `Tools/AssemblyShadow/R03/source-pins.json` remains unchanged at its previous factual native pin.

### Published native files

- `libil2cpp/vm/AssemblyShadowBoundedGeneralLive.h` — preallocated startup-name scratch, source pointers, fail-closed receipt, noncoherence flags.
- `libil2cpp/vm/AssemblyShadowBoundedGeneralLiveSource.inl` — actual inactive source collector included once by `AssemblyShadow.cpp`, `AssemblyShadow.h` declares it only inside the existing feature flag.
- `tools/r03/diagnostic_stream/bounded_general_live_fixture.cpp`, `run_bounded_general_live.py`, and `.github/workflows/r03-p1-bounded-general-live-source.yml` — actual method under mocks, positive/negative source/epoch/admission/control tests and executable retained evidence.
- Demo `run_p1_metadata_local_preflight.py`, its two regression files and `.github/workflows/r03-p1-metadata-preflight-contract.yml` — scoped 12th source child, source SHA custody and 12-child failure semantics. Existing managed consumer, full native SDK translator list and runtime probes remain functionally unchanged.

[Primary review](../History/M07R/R03/IR_Remediation/P1_INACTIVE_LIVE_GENERAL_2026-10-17/PRIMARY_REVIEW.md) · [machine evidence](../History/M07R/R03/IR_Remediation/P1_INACTIVE_LIVE_GENERAL_2026-10-17/EVIDENCE.json).

## Immutable consumed empirical Local evidence

| Local cycle | Recorded original result | Authority |
| --- | --- | --- |
| `20261016-3dc9` | `PassedSourceHostAndSDKOnly` **11/11**, 75 SDK syntax | Consumed, actual native `3dc9b848...` |
| `20261016-f598` | `PassedSourceHostAndSDKOnly` **10/10**, 70 SDK syntax | Consumed |
| `20261016-0620` | `PassedSourceHostAndSDKOnly` **10/10**, 70 SDK syntax | Consumed |
| `20261016-0a0b` | `FailedOrIncomplete` **9/10**, original aggregate SDK flag FALSE | Consumed, never reclassified |
| SNAP-01 | **FAIL / ReturnRequired, 14/18** | Historical |
| N/M/K/I/E, historical R02 immutable whole-file fingerprint | **FAIL** | Historical |
| Original strict S custody | **Blocked** | Historical |
| R03 independent full-stage review / rereview | **FAIL / NotRun** | Historical |

The original V1 slot14 >262144, scanned prefix262145 (exact full bytes Unavailable) and the engine 51,213 uncapped reports/500ms, exit71 remain previous FAIL. Original logger, GC, canary, recovery, sidecar and native reporting limits/predicates are unchanged. No current source/host result upgrades these.

## Remaining gates

**P1 incomplete:** the new source collector uses one outer metadata lifetime ticket and rejects witnessed concurrent source changes, but does **not** prove global atomic VM epoch/ABA freedom, live class pointer origin, class iterator/type-key allocation, GC/RSS and shutdown/drain/lock safety. Original `GetDiagnosticsJson` and `GetExecutionDiagnosticsJson` still run their old allocating implementations, and no R02+execution complete live capture is integrated.

**P2 NotIntegrated:** actual native/C# authenticated V2 artifact/envelope/file transaction and original semantic verifier. **E0 Blocked/Unavailable:** Unity2022.3.62f2 StandaloneOSX native/vendor-supported engine owner-safe point. **E1 BlockedByE0:** callback drain, genuine GC/finalizer native maintenance and restart. **Full P3 Incomplete:** native `-fsyntax-only` compilation is neither linking nor Player runtime/teardown acceptance.

All acceptance flags remain false: `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. No automatic Human Review Gate or milestone transition.

[Local-owned factual validation](../Handoff/LOCAL_VALIDATION.md), [RETURN_TO_WEB](../Handoff/RETURN_TO_WEB.md) and [last consumed Primary reconciliation](../History/M07R/R03/IR_Remediation/P1_OWNED_GENERAL_LOCAL_PASS_2026-10-16/PRIMARY_RECONCILIATION.md) remain immutable evidence. The [remaining implementation plan](../History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md) governs later Primary work.
