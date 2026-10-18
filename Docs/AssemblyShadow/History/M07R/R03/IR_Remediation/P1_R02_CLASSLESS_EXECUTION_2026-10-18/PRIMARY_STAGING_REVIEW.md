# P1 execution continuation — bounded R02 metrics and classless execution JSON (isolated staging)

**Disposition: Two bounded native source increments implemented and host-validated on staging only. NOT merged, no new Local Validation assignment, no Unity SDK/Player runtime or Human Review Gate.**

## Source and ownership

The canonical active branch `codex/assembly-shadow-r01b-h1` remains at demo `25d5986c5919ab70119364ce36e8b670329ad5b0`, native `5667e3712f49e4b38c7dd7359e57f81e344626da`, HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, and Unity package `948c0e3b4f8891481301770115e8ba4945eea6de`. Its existing **ONE** 12-component/75-native-syntax host/official SDK Local cycle is **awaiting a factual return**. This staging work never updates those source pins, active source/tooling, Local-owned reports or `WEB_TO_LOCAL.md`.

Staging native `night-outlook/il2cpp_plus@codex/p1-execution-scalars-20261018` has source-verified HEAD `2cd731be7629d4bd0698176554720a609fcb3d10`; earlier bounded execution header source base for this increment `39d4637b868726c92f50d1db92a5c269ff0bafe5`. The native diff from that earlier commit contains **eight additive R02/composition source, tests, runners and CI paths**; it does not change the already staged execution-header `.h`, `.inl`, the existing general bridge, original getters, C# source, historical pins or Unity build integration.

All staging documentation belongs to `night-outlook/hybridclr_demo` on the **same isolated staging branch**, not the canonical active feature branch. See the previous [execution scalar source review](../P1_EXECUTION_SCALARS_2026-10-18/PRIMARY_STAGING_REVIEW.md) and [machine evidence](../P1_EXECUTION_SCALARS_2026-10-18/EVIDENCE.json).

## Increment A — 22 original R02 metric fields in owned fixed storage

New `libil2cpp/vm/AssemblyShadowBoundedR02Metrics.h` reads the **real production** `ObservationCounters::Read` and `ObservationMemo::TlsBytesPerThread`; this is NOT a mock R02 counter implementation. The `kFields` field-name/Metric mapping is intentionally derived in the **exact original order** from `AssemblyShadowR02Diagnostics.h::AppendDiagnostics`. Runtime `Sample()` visits all 22 source metrics and then samples dropped-class count, dropped threads, saturation and static storage/capacity metadata. A second independent `Sample()` is compared field-by-field before a caller-owned capture can Seal.

**Fail closed:** the new complete-coverage capture refuses disabled or partial diagnostics profiles, dropped/overflowed counter-thread coverage, dropped observed classes, saturated R02 counters, changed metrics/metadata, and any second use of an already sealed object. That is deliberately *stricter* than the legacy serializer, which continues to truthfully print `Disabled/Truncated/Saturated` coverage states: the new API cannot turn them into successful full-diagnostic evidence. No legacy diagnostics or counters were modified. The 512-byte maximum object size is a **source storage bound**, not total process RSS, TLS storage/GC or an atomic cross-thread read.

Successful, stable, Level 2 `Capture::Append` reproduces the complete original comma-prefixed `"r02"` JSON object **byte-for-byte** with no new counter reads while formatting. Both the original `std::ostream` serializer and the production fixed-sink `Writer` are exercised. The data is owned and copied, not a borrowed live-counter view; it is **not** guaranteed to represent one concurrent timepoint.

Source/test/CI changes:
- New `libil2cpp/vm/AssemblyShadowBoundedR02Metrics.h`.
- New `tools/r03/diagnostic_stream/bounded_r02_metrics_fixture.cpp` and `run_bounded_r02_metrics.py`, binding the exact original 22 ordered name/metric pairs and real production counters, testing 12 groups/profile with strict + ASan/UBSan.
- New `.github/workflows/r03-p1-bounded-r02-metrics-staging.yml`.

[Real R02 source/host CI 39106258581](https://github.com/night-outlook/il2cpp_plus/actions/runs/39106258581) **PASSED 3/3 jobs** on macOS 15 Clang, Ubuntu 24.04 Clang and GCC. Each job ran strict and sanitized profiles with 12 ordered test groups per profile: **72 successful group executions** overall. The original three GitHub ZIP digests and **48/48 SHA256/size manifest-declared files** were independently checked. Relevant cases include original byte parity, real fixed Writer parity, watched zero C++ `new` calls after counter prewarm, all 22 modified-source fields refused, late coverage drops refused, dropped classes/threads, saturation, partial output and reentry.

## Increment B — bounded CLASSLESS execution-header + R02 composition

New `libil2cpp/vm/AssemblyShadowBoundedExecutionComposite.h` composes **two already completed owner snapshots**: prior `AssemblyShadowBoundedExecutionHeader::Capture` and new `AssemblyShadowBoundedR02Metrics::Capture`, using the same unmodified `AssemblyShadowExecutionSerializer::Begin/EndClasses` and the exact new owned R02 field bytes. One preallocated `32,768`-byte buffer owns the combined classless JSON text, using the unchanged fixed `assembly_shadow_diagnostic::Writer`. Short, invalid, incomplete or reentered composition fails closed: `Complete=false`, `Bytes=0` and `Data=nullptr`.

**Critical schema distinction:** this emits `"classes":[]` *as a deliberate classless test fixture*, not as a claim that the real Player has no execution classes. It **must not** be substituted for the complete `GetExecutionDiagnosticsJson` result, original V1 status predicates or authenticated V2 transport. No class list, type-key recursion, native metadata, cctor/static storage, complete R02 source epoch or Player is captured. A complete classless fixture is useful for serializer byte-parity and buffer-safety tests only.

Changes:
- New `libil2cpp/vm/AssemblyShadowBoundedExecutionComposite.h`.
- New `tools/r03/diagnostic_stream/bounded_execution_composite_fixture.cpp` and `run_bounded_execution_composite.py`: real R02 production source + actual bounded header Capture, exact legacy classless execution/R02 bytes, invalid/missing sources, short capacity, owned counters, reentry and no new C++ allocations during composition.
- New `.github/workflows/r03-p1-classless-execution-composite-staging.yml`.

[Classless composition source/host CI 39106675107](https://github.com/night-outlook/il2cpp_plus/actions/runs/39106675107) **PASSED 3/3 jobs**, strict + sanitized with 12 ordered groups/profile: **72 successful group executions**. The three original ZIP digests and **51/51 SHA256/size manifest-declared files** were independently checked. The original first composition run [39106598817](https://github.com/night-outlook/il2cpp_plus/actions/runs/39106598817) FAILED at compilation because the standalone host harness did not generate `il2cpp-config.h`. Primary added an explicit **host-only** stub to the test runner (no product code changed). The failed run remains a separate factual CI result; no old evidence is overwritten.

Combined new evidence: **two completed CI runs, 6/6 jobs Passed, 144 distinct case-group executions across strict/sanitized/three compilers, and 99/99 artifact-manifest files verified**. These are different suites and not a claim about SDK/link/runtime or integrated P1 capture. [Machine evidence](EVIDENCE.json) retains the original CI run and ZIP digests.

## Engineering review and limitations

- **No full native link or installed official Unity2022.3.62f2 SDK compilation for these new staging files.** The current active Local SDK batch compiles an older pinned source set and cannot validate these files by implication.
- No `AssemblyShadow.cpp` or `AssemblyShadow.h` change was added in this R02/classless increment. The new headers are not connected to active VM getters, scheduler, C# code, full R02/execution census or native V2 sidecar.
- The original R02 counter implementation has per-thread atomic slots. Two equal collections do not prove one **coherent all-VM epoch** or exclude ABA, thread-local generation changes or concurrent edits between reads.
- Zero watched `operator new` after prewarming in host tests is not zero `malloc`, IL2CPP metadata allocation, TLS construction, managed GC, peak RSS or complete shutdown safety.
- The standalone classless writer's 32,768-byte buffer is a **fixture-specific bound**, not sufficient to hold arbitrary real class-bearing execution diagnostics; existing 4 MiB V2 combined and legacy V1 limits are unchanged.
- The old execution header snapshot remains separately scoped. Future native integration requires an explicit owned class/type-key capture design, capacity tests, high-contention counter proof, healthy-time prewarming, actual SDK syntax and linked Player behavior—**all Primary-owned**.
- E0 legitimate StandaloneOSX engine-owner maintenance API and E1 callback drain/GC/finalizer/restart remain blocked/unavailable. Do not infer scheduler or lifecycle from these host tests.

## Required next state

Preserve the active 12/75 `WEB_TO_LOCAL.md` source tuple until the Local result is published. Upon receiving a factual return (PASS, FAIL, Blocked or other), independently reconcile its source pins and evidence **before merging or cherry-picking staging**. Review the complete isolated staging diff against the actual active source, update appropriate source/SDK regression and add a separately authorized exact-source Local cycle if justified. The staging `WEB_TO_LOCAL.md` stays **PAUSED** with no executable command.

Historical Local `20261016-3dc9` PASS 11/11, `f598` PASS 10/10, `0620` PASS 10/10 and `0a0b` FAIL 9/10 stay consumed and immutable. SNAP-01 FAIL/ReturnRequired 14/18, N/M/K/I/E FAIL, old R02 whole-file fingerprint FAIL, strict S custody Blocked and independent full R03 review FAIL/rereview NotRun stay unchanged.

`P1=Incomplete`, `P2=NotIntegrated`, `E0=Blocked/Unavailable`, `E1=BlockedByE0`, `P3=Incomplete`. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
