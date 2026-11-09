# R03 IR-R03-02 — A2 captured-generic Primary source and host review

Date: 2026-11-09 UTC. Owner: **Primary Implementation**. Scope **A2 only**, on `codex/assembly-shadow-r01b-h1`. This is **not** an independent full-stage R03 review or a real Unity/IL2CPP Player result.

## 1. Input authority and key design

The consumed initializer oneuse-07 is a **focused PASS**, not R03 acceptance. Its original S/K/initializer assets, local evidence, source SHA and historical 17 user-retired roots/40 duplicates remain unchanged. The pinned native, interpreter and package branches remain:
- `night-outlook/il2cpp_plus` `41764ae1eeefb33b05966e7f7676e52aae39c340`.
- `night-outlook/hybridclr` `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`.
- `night-outlook/hybridclr_unity` `948c0e3b4f8891481301770115e8ba4945eea6de`.

The A2 sources were already committed when this Primary continuation began at demo `cca0920afb566b5f02d3a87d9f3fe6b0a2431dee` (22 commits after A1). We reviewed actual source rather than assuming A2 was still absent:

1. `PlayerProject/R03CapturedGenericAotOwner.cs` is a test-only, class-constrained `Touch<T>()` in the AOT `Assembly-CSharp`, with prewarmed `Touch<object>` and an observable static counter. It contains no static `Methods` assembly reference.
2. `R03CapturedGenericPlayer.cs` is inert without a distinct captured request; it warms only the shared AOT owner, starts the original five-candidate transaction, stages the actual independently produced `Methods` target, and requires Commit0/state6 *before* the new native physical probe.
3. `R03CapturedGenericPhysicalProbe.cpp` uses `MetadataCache::GetAotAssemblyByNamePhysical` and physical TypeDef handles *after* publication; it does **not** ask managed reflection to resolve `Methods.R03.Node`, or materialize the physical class via `Class::FromIl2CppType`. It invokes real `MetadataCache::GetGenericInstanceMethod` to obtain an inflated `MethodInfo` whose *owner* is stable AOT and whose `method_inst` refers to the physical baseline node. It then executes the actual `AssemblyShadow::AssertMethodIsActive`, requiring FailedAfterCommit9, failure15 first-recovery, and unchanged counter. A secondary `Runtime::Invoke` is attempted only after terminal failure, and must not invoke the AOT body.
4. `prepare_captured_generic_sources.py` only extends a **new** unbuilt initializer copy with a source-bound native extension and two new managed files. `run_captured_generic_local.py` reuses the original initializer source checks, original S archival checks, real 8+2 native hosts, the two identical initializer controls and adds the separate captured generic test case. This is a fixed **19-cell, one-build, three-Player** single-use plan, not permission to reuse oneuse-07.
5. `verify_captured_generic_native.py` and adversarial tests admit only strict native V1 expected schema with exact external request/fixture/PID/owner, terminal15/state9, a real physical context, and explicit non-acceptance flags. They cannot authenticate a native producer or promote a host mock to a Player PASS.

## 2. Source-review findings and corrections delivered

**A2-SRC-01 — premature generic `typeof(T)`.** The AOT `Touch<T>` originally performed `typeof(T).IsClass`. That redundant reflection could evaluate the captured physical type/RGCTX before the intended method-entry guard. Primary removed it; the `where T : class` constraint and the real CLR host fixture already establish reference-type eligibility. A host source regression rejects reintroduction of `typeof(T)`. This reduces but cannot prove elimination of all runtime-generated generic inflation effects.

**A2-SRC-02 — silent null misclassified as denied AOT entry.** The native `Runtime::Invoke` result check previously accepted a null return with a null exception. That may represent an unresolved generic body, not the required terminal guard. Primary now records the actual out exception (or an `Il2CppExceptionWrapper`) and requires a reported exception **and** unchanged counter in the probe and seal. The strict raw consumer requires `runtimeInvokeThrew=true`. VM-shaped host native `silent-null` and `escaped-body` negatives now fail closed.

**A2-SRC-03 — inflation poison incorrectly attributed to method guard.** Real `MetadataCache::GetGenericInstanceMethod` calls `GlobalMetadata` / `metadata::GenericMethod` and can perform RGCTX inflation, metadata registration or other operations. Primary added a second, explicit `Committed=6` check **after inflation and before `AssertMethodIsActive`**. A VM-shaped host mode `inflation-poison` forces state9 inside inflation and must fail without calling the method guard or sealing any PASS evidence. Actual IL2CPP behavior is still NotRun.

**A2-SRC-04 — incomplete Git input list.** The new runner's `EXTRA_SOURCE_PATHS` originally omitted several CSharp managed API host, helper and test inputs. It now authenticates those plus the real-native fork API audit source/tests to the actual current Git HEAD before the run and again at the end. `test_captured_batch_source.py` requires them. This does not substitute for independent Mac source-tree/Unity/SDK validation.

## 3. Evidence from real host actions (NOT Unity)

- Actual `.NET8` AOT-owner CLR host CI (macOS 15 and Ubuntu 24.04) passed previously. The same owner source compiles against the A2 managed API test host. It is not a compiled Unity IL2CPP binary.
- Native exact A2 probe compiles as C++11 against **VM-shaped test headers** with adversarial data. [Native host run 42549775786](https://github.com/night-outlook/hybridclr_demo/actions/runs/42549775786) finished successfully on both platforms after the inflation-poison negative control. The simulated guard is explicitly not the production native guard.
- [Real-fork declaration/implementation source audit run 42549775765](https://github.com/night-outlook/hybridclr_demo/actions/runs/42549775765) succeeded on both hosts. It reads the exact `il2cpp_plus` source at fixed SHA and checks actual `MetadataCache`, `Class`, `Image`, `Runtime`, `GenericMethod`, native method structs, `AssemblyShadow` state/Error15, the captured visitor, and method-entry guard connection. Adversarial tests mutate every required source anchor and require failure.
- [One-build/three-Player coordinator/managed-host run 42549992287](https://github.com/night-outlook/hybridclr_demo/actions/runs/42549992287) succeeded on both hosts at the source after expanding exact Git input inventory. These are **host/source tests**: no new Unity Player.
- The first attempts to compile A2 against headers from the public `il2cpp_plus` fork (runs `42547856676` and `42548066788`) remain **FAILED**: public source omitted separately supplied third-party `sparsehash`, and after a temporary CI dependency was supplied, lacked the official Unity SDK `Baselib.h`. Replacing that impossible *public-fork-only* compilation with an explicitly named, read-only API-source audit is **not** claiming successful C++ compilation against the official SDK. The required real SDK compile is still assigned to genuine Local Validation.

**No A2 Unity native translation unit, IL2CPP Player, physical AOT owner or genuine error15 was compiled/executed in this environment.** Any claimed source/host PASS is separate from the unknown real SDK/native outcome. Other repositories' production native source and flags were not modified.

## 4. Independent technical risk boundaries

The native `MetadataCache::GetGenericInstanceMethod` **does not guarantee** the requested specialization exists in IL2CPP AOT output; a missing invoker or early class materialization can still prevent the probe. Primary's state check and exception requirement now **fail closed** instead of manufacturing a result. The first native error must really be `CapturedBaselineType` with `CapturedArgumentAssembly=Methods`, `Context=method_inst`, `TypePath=/arg[0]`, terminal code15/state9, and before/after stable AOT counter1→1. No fallback to an arbitrary error13, 19, 21, or host-synthetic receipt may pass.

A native first-error V1 envelope and a bounded once-only file are **not** complete native V2 diagnostics, whole-VM epoch or shutdown evidence. Failure of `Runtime::Invoke` alone does **not** establish every direct AOT-to-AOT business-entry denial. Existing independent `IR-R03-01/02` High findings remain unclosed; the original S compiler/object/link/Player chain and 17 retired roots cannot be made whole by new Player evidence.

## 5. Local-batch sequencing decision

Primary may dispatch a single **scoped A2 oneuse-08** (one real Unity2022.3.62f2 macOS ARM64 ON/diagnostics2/Release IL2CPP build, two initializer regression Players plus one genuine captured-generic Player, fixed 19 cells) *after* all mandatory exact-final-demo-SHA dual-OS host gates and a fully explicit `WEB_TO_LOCAL.md` are published. This staged scope keeps V2/whole-VM work separately blocked: a captured-generic focused PASS is evidence for the method-guard path only, not a full `IR-R03-02` closure. This narrow experiment precedes the larger native-V2 batch to avoid coupling an unverified generic inflation path to new VM-wide instrumentation in the same first compile.

The independent R03 full-stage review remains FAIL. `R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false`; PureInterpreter disabled; no automatic Human Review Gate/H2/M08A/X02/SNAP-01.
