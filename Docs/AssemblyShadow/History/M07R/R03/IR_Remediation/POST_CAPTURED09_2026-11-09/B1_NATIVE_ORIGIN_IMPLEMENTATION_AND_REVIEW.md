# R03 Native V2 B1 — originating-first-error source, implementation and independent-boundary review

Date: 2026-11-09 UTC. Stage: **Primary Implementation source complete / real Unity Local Validation NOT RUN**. This is **B1 only** (with existing B2 inactive host contract coverage), not complete NativePreopenedSnapshotV2, R03 acceptance or a Human Review Gate.

## 1. Purpose and provenance

Follow [current design/plan](B_NATIVE_V2_FIRST_ERROR_DESIGN_AND_PLAN.md), [oneuse-09 focused reconciliation](PRIMARY_RECONCILIATION.md) and the [current conditional B1 handoff](../../../../../Handoff/WEB_TO_LOCAL.md). Source prior to B1: demo `061dcc59a22a837cdec348bb102f7883b3acb737`, native `41764ae1eeefb33b05966e7f7676e52aae39c340`. B1 native candidate is the separately pushed exact `a0209bf4285db3f0d0fc66d8817578235438cef4`; unchanged interpreter `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package `948c0e3b4f8891481301770115e8ba4945eea6de`. Final demo source revision is the current verified feature-branch HEAD at actual Local handoff, not the retired oneuse09 executed source SHA.

### Immutable historical boundaries

oneuse-07 initializer focused PASS (15/15) and oneuse-09 captured-generic A2 focused PASS (19/19) are **historical** and must not be replayed/reclassified. oneuse-08 PrerequisiteBlocked/NotRun remains unchanged. Original Oct independent full-stage R03 **FAIL**, High IR-R03-01/02 remain open; original S complete compiler/object/link/Player provenance and strict historical custody remain unaccepted. The 17 owner-retired roots / 40 duplicate paths are permanently Unavailable, never reconstructed or counted as preserved.

## 2. B1 source design and actual Primary-owned implementation

### Native production-facing core: `night-outlook/il2cpp_plus`

- `libil2cpp/vm/AssemblyShadowFirstFailureV2.h`: C++11 inline-only, process-lifetime fixed storage `FirstErrorV2` (`State=Empty/Writing/Frozen/Invalid`). One CAS winner, immutable code/origin/UTF-8 reason of at most 4096 bytes, no heap or managed API in capture/read, release/acquire snapshot. **Invalid original first event is permanently Invalid; later failures cannot replace it.**
- `libil2cpp/vm/AssemblyShadow.cpp`: captures when the **existing** first type-guard CAS succeeds, at original terminal transaction failure under its existing lock (including postpublication initializer code19), at late baseline physical use and reference-closure failure, and at unexpected native failure. The pre-existing V1 recovery policy, original error code and terminal guard behavior are not redefined. Later attempted native calls cannot replace a Frozen first record.
- `libil2cpp/vm/AssemblyShadow.h`: read-only B1 `FirstFailureV2Status` and `TryReadFirstFailureV2` APIs. These are not activated as a general managed API and do not acquire metadata.
- `libil2cpp/vm/AssemblyShadowFirstFailureV2Host.cpp` plus `.github/workflows/r03-native-b1-first-origin.yml`: C++11/17 source-compiled on macOS and Ubuntu, first winner/overwrite/invalid UTF-8/limits/concurrency/zero-allocation checks. [Native dual-OS run 42598105952](https://github.com/night-outlook/il2cpp_plus/actions/runs/42598105952) Passed at `a0209bf4285db3f0d0fc66d8817578235438cef4`. This is exact-header host proof; the entire VM and real Unity/SDK are **NotRun** here.

### Isolated test-only Player observation: `night-outlook/hybridclr_demo`

- `Tools/AssemblyShadow/R03IR/PlayerProject/R03FirstErrorB1Probe.cpp` adds exported `R03_IRB1_Open` and `R03_IRB1_Seal`: **before** Configure, `O_CREAT|O_EXCL|O_NOFOLLOW` with mode `0600`; post-event read actual B1 `State/Code/Origin/Reason` and write fixed bounded JSON with runId, caseId, fixture SHA, actual process PID and explicit false V2/acceptance flags, `fsync`, close. This output is intentionally **not** B2's descriptor-relative end-to-end transport.
- Existing `R03InitializerObservationPlayer.cs`: healthy control expects Empty/0/0; failure expects Frozen/code19/InterpreterInitializer(2). Strict old linked Bi4 and native V1 pre/postpublication witness is still mandatory.
- Existing `R03CapturedGenericPlayer.cs`: after true Commit and physical `method_inst` error15, expects Frozen/code15/Guard(1), including after denied `Runtime::Invoke`. Old AOT counter and native V1 receipt remain mandatory.
- `prepare_captured_generic_sources.py` adds the B1 native C++ file **only to the new isolated composite**, authenticates origin SHA, rejects existing B1 symbols, updates source manifest and never mutates older oneuse roots or original native source.
- `verify_first_error_b1.py` and `test_first_error_b1.py`: strict JSON schema, malformed/duplicate/extra field, type confusion, source/run/fixture/PID, exact UTF-8 byte length, unchanged original V1 reason, no false runtime acceptance. 25 focused tests.
- `NativeDiagnostics/test_first_error_b1_probe.py`: compiles **the real test-only probe source** with explicitly mocked VM read APIs using host C++11; C++11/GCC/Clang syntax plus emitted JSON, pre-existing file protection; cannot prove real VM producer integration.
- `run_captured_generic_local.py`: **new oneuse-10**, 19 fixed cells / exactly one actual Unity macOS arm64 IL2CPP ON/Release build / 3 distinct Players, strict actual B1-vs-V1 reason verification and original AOT/initializer/host/source/Original-S/provenance/seal gates. Two extra **existing inactive B2** host suites (strict and sanitized native codec; descriptor transaction) execute under the same one-use batch before Unity, but do **not** mark B2 transport integrated.
- `current_native_candidate.json`, `current_native_source_gate.py`, `current_native_vm_delta.json`, `current_native_vm_delta_contracts.py`, `current_native_source_contracts.py`: update **current candidate only** from original 11-source/45 VM delta at native `41764ae...` to 14 source files/47 VM paths at new native `a0209bf...`, crosschecked against GitHub compare: 174 ahead / 0 behind / 134 total changed paths (47 VM + 61 diagnostic tools + 26 workflows); original historical `R03/source-pins.json` and original Local evidence are NOT rewritten.
- `.github/workflows/r03-ir-native-b1-source-and-host.yml` and `r03-ir-native-b1-four-repo-source.yml` verify host and exact source on both `macos-15` and `ubuntu-24.04`. A green CI run never represents an actual Unity Player or full SDK compiler/link/VM proof.

## 3. Acceptance matrix for next one-use Local batch

| Verification | Current Primary evidence | Local required |
| --- | --- | --- |
| New native B1 header, first/invalid/concurrent rule | Dual-OS C++11/17 host PASS | Official Unity SDK production C++ compile and linked GameAssembly identity |
| Interpreter initializer native first reason | Source-integrated B1 with non-VM tests | One new initializer-failure Player: code19/origin2, exact old V1 reason |
| Healthy initializer | Source-integrated, no real build yet | One new control Player: Empty/0/0 plus real Bi4 control0/state6 |
| Physical captured generic first reason | Source-integrated test-only probe | One new Player: actual MethodInfo physical type, first code15/origin1, denied postterminal Invoke, AOT counter1→1, exact old V1 reason |
| B2 fixed codec / exclusive POSIX sink | Existing strict/sanitized host component programs | Host component receipts and source seals only; **VM producer/descriptor transport NotIntegrated** |
| Original S retained evidence | Historical read-only audits, partial provenance | Fresh source-S/custody/process/binary audits; never claim missing full compiled-object graph |
| Whole-VM epoch, B2 real V2 writer, GC/RSS, full RC/P/E | **NotImplemented/NotAccepted** | Not eligible for acceptance in this B1 batch; keep pending |

## 4. Defects/risks and review decisions

1. The B1 CAS is first among **participating producers**; it does **not** establish a total temporal order across existing V1 transaction, guard, external VM failure and managed shutdown origins. B3 whole-VM epoch remains a separate Primary-owned design and implementation obligation.
2. B1 does not reconstruct failure details by allocating a JSON string after terminality. It copies the existing originating native string into fixed storage. If that native string is malformed, empty, overlong or cannot be stored, the B1 record is Invalid; Local must report **Failed**, never silently truncate or substitute the later V1 report.
3. The B1 Player observation uses an early exclusive file under an independently admitted root; it does **not** implement B2's descriptor-relative full path, transaction envelopes, immutable writer/rename/manifest or complete per-VM diagnostics. These are not recast as Passed by the host-only B2 tests.
4. Generated `GameAssembly` must contain linked `_R03_IRB1_Open` and `_R03_IRB1_Seal` once each, alongside original `Bi4` and physical AOT probe exports. Static symbols alone do not prove the runtime path: three new real Player source/exe/PID/first-error/V1 joins are mandatory.
5. Historical original S compiled-object and executable join, 17 retired raw roots, strict historical custody and High IR-R03-01/02 remain unresolved; preserve original independent FAIL and require a separately initiated full-stage review at the documented gate.
6. Source audit / host stubs cannot prove C++17 official SDK, IL2CPP codegen, native first-producer ordering or real GC/shutdown. Local must run exactly the new oneuse10, not retry oneuse09, and return all failed evidence intact.

**Independent Primary static verdict**: Correctness evidence sufficient to issue a **conditional B1-focused Local Validation handoff** only if the final source-pinned dual-OS CI/admission requirements in `Handoff/WEB_TO_LOCAL.md` are satisfied. Full R03 release/runtime acceptance and Human Review Gate remain **false**; PureInterpreter stays disabled. No H2, M08A, X02, SNAP-01.
