# R03 P1 — execution-class observation identity-only census (Primary staging)

**Status: implemented and source-bound HOST CI PASSED. Isolated staging branch only, not merged to active feature, no Local SDK/Editor/Player run.** This increment deliberately stops at checking the **observed execution-class registry structure**, without reading class metadata, claiming source provenance, formatting type keys or writing a diagnostic artifact.

## Source authority and repository isolation

Canonical active feature: `codex/assembly-shadow-r01b-h1`.

| Repository | Active published SHA |
| --- | --- |
| night-outlook/hybridclr_demo | `25d5986c5919ab70119364ce36e8b670329ad5b0` |
| night-outlook/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | `5667e3712f49e4b38c7dd7359e57f81e344626da` |

**Active Local Validation remains independently authorized for ONE 12-component / 75 native-syntax host+installed-SDK cycle at the above source tuple.** Its return is **NotPublished** at the start of this staging increment. Do not advance those active HEADs, substitute a staging revision, consume or rerun its one-shot roots, or infer any official SDK result from host CI.

New native code is exclusively on `night-outlook/il2cpp_plus@codex/p1-execution-scalars-20261018`, after the earlier bounded execution scalar/R02/classless stage `2cd731be7629d4bd0698176554720a609fcb3d10`. Staging documentation is on `night-outlook/hybridclr_demo@codex/p1-execution-scalars-20261018`. Both GitHub Connector read/write smoke tests passed on separate disposable branches; those tests change no active source.

## Engineering target

The original `AssemblyShadow.cpp` keeps a process-lifetime `std::array<Il2CppClass*,2048> s_executionClasses` table of up to `1024` distinct recorded class addresses. Its original `ObserveExecutionClass` writer uses an `ExecutionObservationLock` and a monotone `s_executionClassCount` to append identity entries, and increments `s_droppedClassObservations` on an over-capacity record. The original `GetExecutionDiagnosticsJson` separately copies pointers from this table and dereferences type metadata outside the observation lock, allocating type-key and text structures. That original behavior is unchanged here.

The narrow next P1 step is to **observe/count only that physical registry's entries** under its own original lock, not dereference or retain any `Il2CppClass` pointer or imagine that the stored pointer was originally allocated in the admitted metadata session. The output is an internal, bounded scalar count receipt, *not* one diagnostic class row or a type-name/metadata lifetime proof.

### Production implementation

1. `libil2cpp/vm/AssemblyShadowBoundedExecutionCensus.h` — a new fixed, caller-preallocated `Capture` with `sizeof(Capture)<=128`; one-shot Begin/Seal; errors for missing coverage, oversized class table, reported count/table occupancy mismatch and observed changes. A successful `Get(Result&)` exports only `distinctClasses` and `scannedSlots=2048` and explicit false `classPointerOriginProven`, `coherentVmEpochProven`, `classTypeKeyCaptured` and `runtimeAcceptance`. No class address or internal identity fingerprint is exposed by `Get`.
2. `libil2cpp/vm/AssemblyShadowBoundedExecutionCensusSource.inl` — actual **inactive** `AssemblyShadow::TryCaptureBoundedExecutionCensus` method; one initial metadata admission ticket; two independent scans of all table slots under **separate short ExecutionObservationLock scopes**. Each scan reads only pointer bits, never `klass->...`, and computes a slot-sensitive, noncryptographic internal fingerprint. It also samples the dropped-class counter, `ObservationCounters::DroppedThreads` and saturation after releasing the lock. This is an in-process change witness, *not* a stable hash, class authentication or address verification.
3. `AssemblyShadow.h` declares the inactive method and `AssemblyShadow.cpp` includes both new header and source body once in the same native VM TU. No original getter, existing registry writer, source/SDK build pin, Unity API, Player or R02 metric behavior is modified.
4. `tools/r03/diagnostic_stream/bounded_execution_census_fixture.cpp`, `run_bounded_execution_census.py` and `.github/workflows/r03-p1-execution-census-staging.yml` bind the **exact real included `.inl` method body**, actual `Capture` and actual metadata lifetime Gate. The test explicitly mocks only the VM registry and counter writers and does not dereference a synthetic class in the production method.

The reader fails closed on class-count >1024, count mismatching nonempty slots, diagnostics level other than full level 2, dropped class or thread observations, saturated counters, changed registry occupancy/identity, double invocation and missing/closed metadata admission. It **does not** prove a global coherent VM epoch. Equal hash/count samples cannot prevent an unobserved update between scans or a digest collision, and cannot prove the lifetime of previously registered `Il2CppClass*` instances. No pointer data is retained in the Capture, but its internal fingerprint is derived from pointer bits and must never be serialized as a public identity.

### Real-source CI and independent evidence

[Native CI run 39189008508](https://github.com/night-outlook/il2cpp_plus/actions/runs/39189008508) **PASSED 3/3 jobs**: macOS 15 Clang, Linux Ubuntu 24.04 Clang and GCC. Each job compiled and ran the real production method via an explicit source-bound host fixture in **strict + ASan/UBSan** profiles, with **12 distinct passing groups per profile** (72 successful group executions total), and **4/4 successful compile/run subprocess receipts per job**.

The tests cover two ordinary observed entries in a 2,048-slot table, zero C++ `operator new` calls during the prewarmed tested capture, an empty registry, invalid declared count, >1,024 capacity, concurrent new identity insertion, same-count source-pointer rebinding, late dropped observations, dropped-thread/saturated metric coverage, partial diagnostics level, immutable rejection on repeated use, and metadata admission closed before reads.

Primary independently downloaded all three original GitHub Actions artifacts, confirmed **their entire ZIP SHA-256 equals GitHub's digest**, and verified **54/54 manifest-declared file bytes/sizes/hash digests**, not merely the workflow result. Every original result reports `PassedWithinInactiveHostScope`, two profiles, 12 case groups each, four command exits 0, and the identical exact production method SHA256 `53741797f26464881ab3b9b687fd1c3d7089b4a77f013fe793d87a842a2b2c47`. Exact source Git blobs in those receipts: method `ae57d7884943a679158eed95650b6f99bf86b56d`, header `64fe8b95e51465959f31485f5a51cc3f61b6a8cf`, owning `AssemblyShadow.cpp` `11602c22ec098209dd7dac55096719343222bb36`.

The original class registration/writer is **not** compiled in this unit; its table/lock behavior is modeled and source inspected. Therefore these tests do **not** validate all interactions with the live VM, true writer synchronization, late metadata pointer lifetime, actual IL2CPP allocations, process RSS/GC, real concurrency or shutdown deadlock freedom. The full native `AssemblyShadow.cpp` under the installed Unity2022.3.62f2 SDK remains **NotRun** at the new staging revision. No Editor/Player has run.

[Machine evidence](EVIDENCE.json) contains the scope distinctions and exact commit/artifact identities.

## Acceptance and next dependency

This increment is appropriate **only as inactive, source-bounded P1 scaffolding**. It is not an authenticated execution-class list; complete class records still require a reviewed safe origin/epoch/lifetime scheme, bounded metadata-type-key formatting, GC/RSS/lock and shutdown proof, a coherent general/R02/execution VM capture, and original getter/semantic integration. Do not feed its scalar Result into the original semantic verifier as if it contained full class evidence.

**Next:** the active 12/75 Local run must return a factual report before Primary merges or cherry-picks isolated staging. Review the returned raw evidence and preserve all consumed source PASS/FAIL. Thereafter independently review the complete staging delta, add the new identity-census child to a separately source-pinned SDK preflight if justified, and authorize only new fresh roots with exact four-repository HEADs. The staging `WEB_TO_LOCAL.md` remains **PAUSED**; there is no new Local execution command here.

P1 coherent live capture **Incomplete**; P2 native+C# authenticated V2 semantic integration **NotIntegrated**; E0 supported StandaloneOSX native engine owner **Blocked/Unavailable**; E1 genuine native maintenance/GC/finalizer/callback drain/restart **BlockedByE0**; full P3 Player qualification **Incomplete**. Prior `20261016-3dc9` PASS (11/11), `f598` PASS (10/10), `0620` PASS (10/10) and `0a0b` FAIL (9/10) remain separate and immutable. SNAP-01/N/M/K/I/E, old R02 fingerprint and full independent R03 review FAIL, strict S custody Blocked, rereview NotRun remain unchanged.

`R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. No Player, Human Review Gate or next milestone authorized by this staging source.
