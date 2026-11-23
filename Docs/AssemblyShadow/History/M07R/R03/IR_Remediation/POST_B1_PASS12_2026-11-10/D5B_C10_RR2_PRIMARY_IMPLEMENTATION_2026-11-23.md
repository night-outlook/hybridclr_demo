# R03 B2 D5-B C10 — Primary Implementation: RR2 native autonomous receipt + worker identity + required slot 5

**Primary status: `SourceHostComplete_PendingIndependentRereview` (2026-11-23 UTC).** This deliverable implements focused corrections to independent [D5-B C10 RR1/RR2 `ReturnRequired`](D5B_C10_PRIMARY_REMEDIATION_INDEPENDENT_REREVIEW_2026-11-23.md). It is **not independent source approval**, not Unity Editor or IL2CPP compilation, not a native VM/GC measurement, not linked binary evidence, not Player testing and not Local execution authorization. The only next gate is an independently initiated **C10 source/design/host rereview**.

**Gates remain closed:** `D5BC10IndependentReview=ReturnRequired`; `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. All 18 real D5 Player cells remain `NoCoverage`. Historical B1 oneuse-12 is not new C10 evidence; no D6/H2/M08A/X02/SNAP-01/Human Review Gate or Local agent prompt is issued.

## 1. Exact source state

All four repos use `codex/assembly-shadow-r01b-h1`.

| Repo | Exact tested source commit | Changed scope |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | **`38b166eea238ff7e734178175bfeaa33889a022d`** | 14 changed D5Probe/workflow paths since previous independent review `d0b381809a5273c3dc82a0885c2e4277b6b330bb` |
| `night-outlook/il2cpp_plus` | **`87a34bbea39930dab96cf4703756d8da79d54684`** | Only `libil2cpp/vm/AssemblyShadow.cpp` and `AssemblyShadowD5WindowProbe.h` since prior native `84f9435628b8ff4cc675409f6b4d76dd2753d8a8` |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Unchanged |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | Unchanged |

GitHub Connector readbacks verified all four exact branches and read/write permissions. Native compare = one commit, exactly two native files; demo compare = five commits, exactly 14 C10 sources/tests/workflow, no old B1 runner, oneuse-12, D5-B custody or Local-owned doc mutation. The exact [final source-host CI](https://github.com/night-outlook/hybridclr_demo/actions/runs/45132702353) attaches to demo `38b166ee...`. Future documentation-only HEAD must **not** be reclassified as the CI-tested implementation.

**Actual Git blobs validated independently:** `AssemblyShadow.cpp=a5e7e654a2b1ede83ae18b8f15fcb4ee51f96490`; `AssemblyShadowD5WindowProbe.h=d89d457ba73685b9505185f1d788f0bbf6a6d216`; `R03D5WindowOverlay.cpp=30ca8ed1b60b7fa05ed41960111c5f9b91229b06`; `R03D5P5WindowPlayer.cs=b54d4df59e498a5eb5fb6ac59d3a17ac47505110`; `R03D5Build.cs=31ca04858aa00c5d1db1678d784a804ed076e159`. The actual 13 native Git source/header blobs in `d5c10_link_source_pinset_v1.json` all matched remote native source at the reviewed SHA. Intent roster remains **13 pinned native source/header blobs, five compiled TUs, nine C10 test-only exports**, with feature-OFF controls and explicit exclusion of host global-allocator source. Actual native installation/linkage remains NotRun.

## 2. IR-D5BC10-RR-01: independently prestarted native writer / terminal completion

The isolated `R03D5WindowOverlay.cpp` opens a fresh, absolute output path while managed runtime is healthy using `O_EXCL | O_CLOEXEC | O_NOFOLLOW` and file mode 0600. After an exclusive header write it starts one **POSIX pthread native collector** before Configure/Stage/Commit, and has no dependency on any post-Commit managed `finally`, `Thread.Join`, `GetState`, JSON serialization or `ReceiptSeal` P/Invoke. The managed fixture now **never invokes `ReceiptSeal`** after Commit. A separate source-host manual seal export remains for historical unit-compatibility; in the actual test-enabled native-VM configuration a managed manual seal returns a rejection code and the collector is the sole native owner of completion.

The prestarted collector asynchronously observes the real atomic P5/guard witness without taking transaction, metadata or usage locks. It writes event slots 2–5 with `pwrite/fsync` from its **separate thread**, not inside the `AssertMethodIsActive` guard or P5 managed worker. The collector reads `AssemblyShadow::GetState` (the source implementation is a direct atomic state load), actual `FirstFailureV2Status/TryReadFirstFailureV2` and a **pre-pinned raw primitive field**. There is no `GCHandle::GetTarget` call or new VM metadata/GC lookup after the possible terminal boundary. Pinned object, field offset and real method identity are bound ahead of the guarded attempt; a release/acquire `canaryReady` token publishes their immutable values to the reader.

The collector's runtime result predicate waits for a terminal-denied guard, an admitted method's release/finish, a P6 race or a bounded deadline. It has a **pre-arm max 60 seconds** (healthy staging/configuration) and a **post-arm max 8 seconds**; host-only synthetic runs use a separate 500-ms deadline. It independently writes and seals the complete fixed record, then uses **test-only native `_exit`** to avoid post-terminal managed/Unity teardown dependencies. All native probe outcomes exit **nonzero**: `20`=denied source-material candidate, `42`=potential early admission, `2`=incomplete/unavailable. **Exit status alone never establishes Player acceptance.** A failed writer or absent native guard is `NoCoverage`, not an implicit safe denial.

The native format is unchanged at **4,652 bytes**: 212-byte versioned run/request/fixture/PID header, ten 32-byte source-defined fixed event slots, one 4,120-byte first-native-error block. One-shot slot reservations reject duplicates. The native collector writes guarded canary snapshot/first-error outside critical locks and closes/fsyncs its source-material file; it never creates actual Unity/IL2CPP/linked-binary proof.

**Limit:** the actual `HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE=1` collector branch has **not been compiled against real Unity/IL2CPP**. Its VM/GC interactions and process-exit timing are still source candidates. Full Unity Player and real VM first-error/field capture remain NotRun; only the pure native same-code host collector loop and synthetic adapters were compiled.

## 3. IR-D5BC10-RR-02: unique one-shot worker/method correlation

In `AssemblyShadowD5WindowProbe.h`, `WindowProbe::ArmTargetForCurrentThread(const void* methodIdentity)` is a **single-use** atomic/TLS registration that can only arm in P5. The TLS token contains exact pointer identity, owner witness and an active bit; the native `MethodResult` consumes it exactly once. Calls from another thread, different `MethodInfo*`, or after a previous target guard cannot increment the worker's result. Native `AssemblyShadow::AssertMethodIsActive` still applies exact physical `Methods`, `R03.Node`, `Keep` filters, then calls `MatchesTargetOnCurrentThread(method)`; the boolean return of production method admission is unchanged. The TLS/atomic check performs no VM metadata lookups, allocation, disk I/O or lock acquisition inside the actual method guard.

The isolated overlay's `R03_D5_BindKeepCanary` resolves and binds the real `Class::GetMethodFromName(object->klass,"Keep",0)` pointer against the same owned, pinned `R03.Node` object while the test worker is still in the P5 window. The C# worker releases its temporary **managed** `GCHandle` *before* the potentially terminal `Keep` call; the independent native pinned root stays alive for its process. `R03_D5_BeginKeepAttempt()` arms the one-shot TLS token immediately before `method.Invoke(instance,null)`. No native file I/O or exception formatting occurs in that P5 worker path. A managed constructor/metadata failure does not arm the token and cannot be classified as a denied `Keep`.

Native witness counters now require both the exact physical `MethodInfo` and the **same thread-bound token**. Positive and negative source-host simulations exercise `foreign`, `wrongmethod`, `duplicate`, `raced`, `denied` and `allowed` cases. They **do not demonstrate** that real Unity reflection invokes the identical native `MethodInfo*` pointer; a mismatch correctly results in `NoCoverage` until verified by a separately reviewed Player.

## 4. IR-D5BC10-RR-03: mandatory native method-completion slot 5 and fail-closed parser

The autonomous collector owns all event slots after the healthy arm event. **Slot 4** records the one-shot worker token; **slot 5** records the native `MethodResult` outcome for precisely that token (1=admitted, 2=denied, 3=raced). It is deliberately **not** a managed `Invoke` return event: a terminal rejection may prevent managed code from reaching a catch/finally, so treating its absence as missing proof would recreate RR-01. The actual native guard result and independent field side-effect are the authoritative evidence sources.

`d5_c10_native_receipt.py` now requires **all ten event slots**, including 5, and validates the slot-4 token, slot-5 decision, method-specific counters, native auto-seal markers, P5 observation, no timeout, bound instance before=0, pinned before/after field, terminal state and frozen B1 first-error before reporting a **synthetic denied candidate**. Missing, contradictory, raced, unauthorized-thread, mismatched-method, duplicated or corrupted material returns `NoCoverage` or rejects the record. An observed admitted target guard or actual field mutation is marked `UnsafeEarlyMethodAdmissionObserved_SourceMaterial`, **never real Player execution proof**. Native `_exit(20/42/2)` is not used as an acceptance predicate. Every source-only result retains `realPlayerC10Passed=false`, `actualLinkedBinaryAndPidAuthenticated=false`, `R03Accepted=false` and `D5BLocalExecution=NotAuthorized`.

Host-only synthetic auto receipts are parsed as **source-host materials**, with six independent scenarios (`denied`, `allowed`, `foreign`, `wrongmethod`, `raced`, `noattempt`), separately for strict and ASan/UBSan host executables. The host mock state, field and first-error adapter is compiled **only** under `HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO=1`, not into a real Player.

## 5. Native and managed timing / limitations

The 20–2000-ms P5 barrier still intentionally widens the P5→P6 window by dropping/reacquiring the transaction lock **after** the publisher's nested metadata/assembly/usage locks unwind. This is a **test-only scheduling perturbation**, not proof of normal production timing or coherent VM epoch. The remaining P5 managed work includes `Type.GetType`, method reflection, `Activator.CreateInstance`, a temporary GCHandle and native canary/MethodInfo binding. It may still be too slow or inadmissible at P5 on a real IL2CPP Player; such outcomes must stay `NoCoverage` with source/first-error provenance, never automatically Passed. Source-host CI cannot prove healthy real `R03.Node.Keep` positive control or actual GC lifecycle.

The native collector's first-error read uses the real immutable B1 source; it is not V2 whole-VM epoch transport. The _exit path is appropriate only for isolated, fresh C10 test processes; ordinary Unity shutdown/GC safety is a separate D5-C17 requirement. 32-bit ABI, Android/iOS/Windows targets, native Bee/IL2CPP compiler, source→object→binary→PID joins and actual module initializers remain NotRun.

## 6. Exact completed source-host CI

**[GitHub Actions run 45132702353](https://github.com/night-outlook/hybridclr_demo/actions/runs/45132702353)**, push SHA **`38b166eea238ff7e734178175bfeaa33889a022d`**, attempt 1 **completed/success, four of four jobs**. All four raw job logs were fetched and audited at this Primary checkpoint. They show 50/50 source-contract tests, 27/27 synthetic-link tests, 28/28 synthetic receipt-parser tests, 18 strict/sanitized window host cases, 2 strict/sanitized manual writer host cases, 12 strict/sanitized **autonomous collector** host cases, and one feature-OFF control **per job**. Each host job additionally parses twelve auto-collector output files (six strict plus six sanitized), with source-host labels and no real Player claims. No unexpected ASan/UBSan errors in the final jobs.

| OS and C++ | Raw CI job ID | Source Python | Link Python | Receipt Python | Native strict/sanitized host | OFF |
|---|---|---:|---:|---:|---:|---:|
| Ubuntu 24.04 C++17 | `137551628821` | 50 | 27 | 28 | 18 window + 2 manual + 12 auto | 1 |
| macOS 15 C++11 | `137551629012` | 50 | 27 | 28 | 18 window + 2 manual + 12 auto | 1 |
| macOS 15 C++17 | `137551629033` | 50 | 27 | 28 | 18 window + 2 manual + 12 auto | 1 |
| Ubuntu 24.04 C++11 | `137551629043` | 50 | 27 | 28 | 18 window + 2 manual + 12 auto | 1 |
| **Total** | | **200** | **108** | **112** | **128** | **4** |

**Total 420 Python unit/source/synthetic tests, 128 strict/sanitized C++ host cases, four OFF controls, 48 synthetic host-receipt parser checks**. Source host uses actual updated C++11 header and overlay, but no full native `AssemblyShadow.cpp` production TU or VM-branch compilation. Intermediate failed attempts were **not** promoted: `45131940702` (stale test mutation pin), `45132088295` (workflow quoted compiler array), `45132164417` (missing C++ semicolon); previous green source-host run `45132338562` predates the final bounded timing and nonzero native exit change. Only `45132702353` is final exact-source success.

## 7. Source-identity handoff and next independent checkpoint

The current `d5c10_link_source_pinset_v1.json` has Git blob `fe531a9ab5a585a4b2e0217a1db236fb9ae0b4a0`. It maps 13 actual Git-pinned `libil2cpp` files (including the two changed native Git blobs), the three isolated demo overlay/managed/builder source blobs, 5 intended TUs and 9 expected exports. Synthetic `d5_link_materials.py` intentionally permits fake Mach-O/object/nm artifacts only as `SyntheticSourceHost`. It cannot attest a real Unity compiler/link invocation, linked symbol or native process. `APPROVED_LOCAL_HANDOFF_BLOB=None` in `D5Admission/d5b_custody_authority.py` remains binding, and all six historical root roles remain mandatory. No new actual one-use Local output or approved WEB_TO_LOCAL exists.

**Next permitted activity:** an **independent C10 design/source/host rereview** of exact four source pins, actual updated native and demo files, raw CI run `45132702353`, lock/TLS method identity, autonomous native writer and fail-closed parser. Reviewer chooses `PassD5BC10ForNextPreparation`, `ReturnRequired` or `Blocked` for **source/test-producer preparation only**. Primary does not self-approve. Even an independent Pass will **not** grant Local Unity/IL2CPP execution, C10 real-Player completion, R03 acceptance or Human Review Gate. A separately explicit user Local execution decision and authenticated immutable source→Bee→binary→PID/evidence handoff are required later.
