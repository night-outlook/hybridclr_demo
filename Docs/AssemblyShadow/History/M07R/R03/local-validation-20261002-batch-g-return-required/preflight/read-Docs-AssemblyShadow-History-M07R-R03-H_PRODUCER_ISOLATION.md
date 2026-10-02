# R03 H — concurrent producer attribution and bounded witness isolation

Primary Implementation design, source review and validation record, 2026-10-02 UTC. **Not independent stage review, integrated runtime acceptance, or Human Review Gate approval.**

## 1. Received evidence and exact authority

Read the unchanged `Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md` and `History/M07R/R03/local-validation-20261002-batch-f-return-required/` under `Docs/AssemblyShadow`. Local publication is `7f27633d9fc761faa93733b07e1787831babe73e`; executed demo was `8f86dda1aa0582a5b2d55aa650ea321f710cb49a`.

F remains **ReturnRequired: 32 Passed / 4 Failed / 0 Blocked**, focused seal Passed. Four native builds and all 754 selected Editor cases passed. All nineteen fresh-process Players ran, fifteen Passed and four Failed. C03/C04/C05/C07 each recorded a cold mscorlib Enumerator admission on probe thread 2 inside labels 1→2, while owner thread 1 completed 10,000 hits and mandatory baseline checks. Debug D02/D03 passed the same zero-work requirement. No historical class/site/thread observation is reclassified.

C07's separate physical-layout subcheck passed: baseline size 24, active size 32, retained offset 16 and private Int64 tail at 24–32, completed staging readiness, no baseline business initialization. **Its full cell remains Failed** because of the warm witness. That successful physical subcheck does not establish LF-001 closure or full R03 acceptance.

Local authenticated 1,871 indexed files, 1,872 archive members and 5,027 earlier custody bindings. Primary has read published evidence, not accessed the retained macOS live root. F's result/index/archive hashes remain `29e5796cb95571416ad8f7b6e6f9fcbf18bf5638e25295ae0ed5ecc1ff2b6946`, `a5b84340e83c96cd1a38f185926e58b341eced53f7132b1b8c2f27fd1e6d208c`, and `f0c259e6ba4a479d3765477962b4d971b902c83ce84bdfa635d519d13fa9bdeb`. No Local-owned report, previous checkpoint, app or archive is changed.

Final tested source tuple, all on `codex/assembly-shadow-r01b-h1`:

| Repository | Tested source |
| --- | --- |
| night-outlook/hybridclr_demo | `53e6e559165344cb98405a7261a988871157a864` |
| night-outlook/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` — unchanged |
| night-outlook/hybridclr_unity | `120bb01be680cec0375002a0823552d66d34b84c` — unchanged |
| night-outlook/il2cpp_plus | `9ab7a0000f02251e280901c6e23f6a7772344ca6` |

The final demo handoff is a documentation-only descendant of that tested anchor. The exact latest pushed transport SHA is supplied in the final prompt and resolved from the latest commit touching WEB_TO_LOCAL.md; it must equal local and remote HEAD before Local execution.

## 2. Identify a concrete producer without inventing historical attribution

F's simple name `Enumerator`, empty nested namespace and non-owner probe thread do not identify its declaring generic type or caller. Primary inspected actual pinned Unity 2022.3.62f2 ARM64 BCL metadata, not an assumed current .NET implementation. `H_BCL_PRODUCER.json` binds the mscorlib bytes, tokens, selected IL and original metadata artifact. The file SHA-256 is `d89d5124cafb873b34c2eac68d2ece41d14fec10999baf0e4620276dff54ab83`.

Among thirteen simple-name Enumerator types in that BCL, the ConditionalWeakTable nested Enumerator is the reference-class variant. Actual IL supplies this candidate chain:

`TlsOverPerCoreLockedStacksArrayPool<T>.Return` → registration of `Gen2GcCallbackFunc` → `System.Gen2GcCallback.Finalize` invoking its `_callback` delegate → `TlsOverPerCoreLockedStacksArrayPool<T>.Trim` → high-memory branch enumerating `ConditionalWeakTable<T[][], object>`.

The pinned `GetTrimBuffers()` returns the literal true; there is no configuration switch in that method to disable trimming. The source also has another ConditionalWeakTable caller, `TaskScheduler.GetTaskSchedulersForDebugger`. Therefore neither a simple name nor source-chain plausibility proves F's actual producer. **The ArrayPool path is a source-supported hypothesis; its new runtime identity must be verified, and F's original actor remains unproven.** No claim is made about why Release and Debug scheduling differ.

The metadata workflow extracts the official changeset `7670c08855a9` ARM64 installer without installing or launching Unity. Installer SHA-256 is `5d2575c1b10a2a9f1f89bf40631a6b9bec3628fe16ca5f2203720af7943a3f05`. Source capture and metadata analysis are not Player runs or runtime evidence.

## 3. Native attribution and narrowly scoped isolation candidate

The added GC adapter is compiled only when both Assembly Shadow and `HYBRIDCLR_R03_RUNTIME_PROBE` are enabled. That probe is already off by default in ordinary Players. Runtime cache behavior, the admission key, counter increments, physical-layout comparison and mutable per-allocation baseline guards are not relaxed.

At `GarbageCollector::RunFinalizer`, a metadata-only adapter recognizes an already initialized `mscorlib/System.Gen2GcCallback` object. It checks the unique nonstatic generic `_callback` field and its offset/bounds, then inspects the actual delegate's MethodInfo. The qualifying callback must be static `Gen2GcCallbackFunc`, with a closed generic `System.Buffers.TlsOverPerCoreLockedStacksArrayPool`1` owner, one parameter and Boolean return. Unknown or incomplete metadata does not qualify for isolation.

An RAII thread-local producer context records the real finalizer class, qualifying delegate MethodInfo and the native runtime's thread identifier. Each cold admission event retains that context. The report includes full type keys, including nested and closed-generic identity, formatted after the probe is sealed; it does not resolve names or invoke managed code while incrementing counters. Probe thread identities and the added native thread identifiers remain distinct fields.

`ProducerFence` is a one-use, owner-bound diagnostic lease with a hard **5,000 ms** maximum. It is acquired outside metadata/probe locks before Begin, waits for existing matching callbacks to finish, and defers new matching callbacks until the observer interval ends. It neither initializes an Enumerator nor triggers a collection or extra warm-up. Mark(3) releases it; exceptional managed paths also release it during final evidence retrieval. Deferred callbacks must complete under a separate bounded drain. Expiry opens the gate for runtime progress but invalidates the witness; a timeout cannot become a successful isolation result.

**Scope and side effects:** GC remains enabled, finalizers are not discarded, and unknown callbacks are not themselves selected by the gate. However, Unity's finalizer thread is serial: a deferred matching callback can indirectly delay later queued finalizers. This bounded scheduling intervention belongs only to the isolated diagnostic profile. It is not proposed as a production GC policy, memory optimization, concurrent-service SLA or performance acceptance technique. No claim that all unrelated finalizers are unaffected is made.

The six original warm witnesses continue requiring zero all-thread cold admission/proof/entry/retained-byte/unready work and zero layout/field/interface workspace work inside the exact 10,000-allocation loop. Required hits and baseline checks remain at least 10,000. Preparation remains eight allocations. All original broad counters and six native boundaries remain visible and reconciled; no +1 allowance, thread subtraction, counter reset, warm-until-pass loop or forced GC is introduced.

## 4. Natural controls prevent the candidate from hiding the producer

The original 36 cells and nineteen case identities remain. One new `producer-controls` cell runs four additional, fixed, fresh-process controls paired with C03/C04/C05/C07: `PC-C03-moved-slot`, `PC-C04-old-AOT-guard`, `PC-C05-direction-reversal`, and `PC-C07-private-primitive-append`. Their source-bound request uses `producerControl=true`; the lease is not acquired. These are not retries of the main witnesses, and they execute independently even if another control fails.

Each natural control retains the full publication, reflection/delegate, old-AOT guard where applicable, and C07 physical proof checks. Every counter span still reconciles to events. Any in-loop cold event must identify a different physical/logical type, a non-owner probe thread, `Object::NewAllocSpecific`, the real Gen2 finalizer, the actual ArrayPool delegate and a full ConditionalWeakTable Enumerator type key. Unknown producers, target proof, rejection/unreadiness or repeated physical work fail the control.

A valid control with identified concurrent cold work records **`unisolatedWarmCertificate=Failed`** and `ExpectedContaminationObserved`. A valid control with no event records `NoContaminationObserved`; it is not claimed as positive actor attribution. At least one of the four must identify the producer, and all four controls must satisfy their diagnostic contracts. No attribution across all four makes the aggregate Failed/NoCoverage, not a waiver. A Passed diagnostic control is never promoted to a Passed unisolated warm certificate.

Total planned execution is **37 cells / four new builds / 754 selected Editor cases / 23 fresh Players**. All original nineteen Players still require their original semantic outcomes, with the six warm certificates additionally requiring a completed, nonexpired, drained lease. The frozen M01 asset test remains explicitly NoCoverage.

## 5. Tests, diagnostics and implementation inventory

IL2CPP changes: `libil2cpp/gc/GarbageCollector.cpp`, `libil2cpp/vm/AssemblyShadowRuntimeProbe.h`, new `AssemblyShadowFinalizerProbe.h`, new `AssemblyShadowProducerFence.h`, and new `tools/r03/producer_fence_tests.cpp`. The physical-readiness and allocation-cache policy implementations from F are unchanged.

Demo changes under `Tools/AssemblyShadow/R03/`: `PlayerProject/R03Player.cs`, `PlayerProject/AssemblyShadowR03Probe.cpp`, `batch_contract.py`, `runtime_contract.py`, `run_local.py`, `native_validation.py`, `source-pins.json`, `run_host_lifetime.py`, `test_runtime_contract.py`, `test_batch_contract.py`, `test_input_validation.py`, and new `test_producer_control.py`. New workflows are `.github/workflows/r03-producer-analysis.yml` and `r03-source-capture.yml`. Documentation adds this H record, H_HOST_EVIDENCE.json, H_BCL_PRODUCER.json and H_VALIDATION_MATRIX.md, and updates only canonical README/status/WEB_TO_LOCAL.

Nineteen new Python tests cover strict lease identity/bounds/draining, no-event NoCoverage, actual producer metadata requirements, preserved zero-work rejection, and independent four-control execution. Eleven native fence scenarios run in C++11 -O0, C++17 -O1 and sanitizer profiles: normal completion, deferred completion, unrelated callers, existing callbacks, expiry, abandonment, wrong-owner release, reuse, bounds, exceptions and nested TLS context. Native-header/synthetic contracts are not proof that the pinned GC adapter identified a real Player callback.

Primary's extra unoptimized C++11 link test exposed an ODR-use of the constexpr lease duration hidden by optimized tests. Native commit `9ab7a000...` fixes the chrono argument to a value. Final CI explicitly links and executes the unoptimized profile. The first native candidate `8e11a377...` and earlier demo compile checkpoints are not the final handoff tuple.

## 6. Completed validation and its limits

Final host workflow **36992865105** passed both Linux x86_64 and macOS 15.7.9 arm64 jobs at demo **53e6e559165344cb98405a7261a988871157a864**, SDK 8.0.318. Each passed 163 Python tests, reference/candidate graph 9/9 each, admission 35/35, fifteen fixture DLLs, 33 audits/consumers, actual managed Runtime API compilation, existing provenance/scope checks, compiler lifetime controls, **57 native header test processes** and the two existing R02 native suites with **60+60 passed processes**. Each has 123 fully owned command receipts, including two named expected-negative exits; all completed cleanly. Another 148 legacy receipts per host were stream-authenticated without claiming equivalent process-lifetime proof.

Pinned-Unity workflow **36992864925** passed complete-helper/package compilation and **30 native translation-unit/profile syntax checks**. Six units include the modified GC and diagnostic adapter, across candidate/Debug/probe-off/diagnostics-off/feature-off profiles. These checks do not link or execute a Player. The helper emitted no compiler diagnostics; 61 existing package CS0649 warnings remain recorded, and the unchanged C helper still yields exactly its two expected CS0266 errors. The exact API CoreModule remains `e22a829a8022d30c6b2b11fe764d12a2383cf882b63a954641e3cd41ea56af6e`.

| Final evidence | Workflow / artifact | ZIP SHA-256 | Membership |
| --- | --- | --- | --- |
| Linux host | 36992865105 / 11220331384 | `7e3698fd4b8e217aa5e9b91476656f3b5922c48d5b292eab8980bbd72c55ba08` | 1333 indexed / 1334 files |
| macOS host | 36992865105 / 11219899668 | `3602561c6197cea31b7195a85840a2137e4d4f9e987f14a537fbcd7101ec5588` | 1441 indexed / 1442 files |
| Pinned API/native syntax | 36992864925 / 11219934786 | `0176a7a9195d35459155b9564ec5e2c0a94c02142ca365aee56b58b99914a45d` | 124 indexed / 125 files |
| Pinned BCL metadata | 36988063609 / 11217714458 | `cdd0fd15b0635090c145606aca13a5c85b6aebd62059f47ace106336fdf77985` | 1 indexed / 2 files |

Primary downloaded and authenticated exact safe/nonduplicate membership, every indexed size/hash, source/result identities and retained streams. H_HOST_EVIDENCE.json records the detailed audit. Artifacts expire 2026-10-16. The container separately passed all 163 Python contracts; an optional full native container invocation reached the execution tool's 120-second limit after 71 completed command receipts and has no final results.json. That attempt remains Incomplete, not a full-suite PASS. Both final CI hosts completed the corresponding full suites.

## 7. Disposition, transport and next handoff

**R03-LF-001: source-supported producer candidate, native attribution, bounded isolation and paired controls implemented and host/compiler validated. Actual producer attribution and isolated Player success remain pending.** This self-review does not empirically close the issue. Missing or different runtime attribution must return to Primary, not be hidden by additional filters or adjusted counters.

All four refs were read through the Connector. Demo and IL2CPP writes each passed a disposable Connector commit/read-back smoke on `codex/connector-smoke-r03-lf-20261002`: demo `52f225d000956d6c7b284e397291fff4be449e55`, IL2CPP `1dff14f3d0d22838e71d344f9d0ffdc461de5d8a`. No delete-ref action is exposed, so both remain disposable and non-authoritative. HybridCLR/package are unchanged; their previous smoke evidence and fresh reads are not represented as new writes.

The next unused root is `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261002G-producer`. Local receives completed source and executable checks, not an implementation task. It must use the final exact source tuple, run once, preserve all main/control result distinctions, publish Local-owned evidence/reports and stop. No previous app, root or result may be reused or relabeled.

Rollback requires a new coherent Primary-controlled source/handoff revision. Never mix native pins or modify preserved F evidence. Full legacy/resource/P01–P05 and M01 coverage, broader generic/interface/delegate/stack-trace work, startup/capacity/performance/memory, gated PureInterpreter qualification and independent full-stage review remain Primary-owned and open. R03Accepted=false; H2Passed=false; expansion disabled; fullLegacyRegressionAcceptance=false. R02 deferred CPU and original H1 RSS risks remain visible.
