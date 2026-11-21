# R03 B2 D5-B — Primary Implementation: P5→P6 real-Player probe **candidate**, native source-host and link-material review

**D5-B C10 Primary source/host disposition: `CompleteForIndependentSourceReview`.** Report date: 2026-11-21 UTC (CI timestamps). This is **not** Local Validation, a finished Unity/IL2CPP build, a linked/observed Player, or independent review. D5-B Local execution requires **separate explicit user approval and a newly authenticated, independently reviewed `WEB_TO_LOCAL`**. Current `D5BLocalExecution=NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`.

Predecessors:
- [Independent D4 `PassD4ForNextGate`](D4_ACTIVE_SNAPSHOT_OWNERSHIP_INDEPENDENT_REVIEW_2026-11-20.md), source-host only;
- [Independent D5-A `PassD5AForD5BPreparation`](D5A_INDEPENDENT_SOURCE_REVIEW_2026-11-20.md);
- [Independent D5-B custody `PassD5BCustodyForProducerPreparation`](D5B_SOURCE_CUSTODY_INDEPENDENT_REVIEW_2026-11-20.md); and
- [D5-B real-Player producer/link plan](D5B_REAL_PLAYER_PRODUCER_AND_LINK_PLAN_2026-11-20.md).

## 1. Exact fixed source/test authority

All four repos on `codex/assembly-shadow-r01b-h1`:

| Repository | Actual source authority | D5-C10 change |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | **CI-tested code `a833d22487352135a88d6b245eea7f2d103af48b`** (later documentation-only HEAD listed in readback) | New separate D5 probe/Player candidate/Unity build entry, host code, synthetic link-material verifier/tests and source-host workflow |
| `night-outlook/il2cpp_plus` | **`8eeb3cc53a451a6925b490d623c81753822cb1d4`** | **Only** `libil2cpp/vm/AssemblyShadow.cpp` (blob `8db5fed1ee2e6bf6b95597707a2fa9cdf43807a1`) and added `libil2cpp/vm/AssemblyShadowD5WindowProbe.h` (blob `bb958c44ae11f47160cd306cadc0c3edf56501f9`) |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | No changes; real Codec and Runtime phase observers remain pinned |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | No changes; existing `PinnedSourceInstaller` is invoked by the isolated D5 builder |

Compared native base `il2cpp_plus@3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699` → `8eeb3cc53a451a6925b490d623c81753822cb1d4`: **two commits, exactly two paths**, preserving D2 physical/CLI rollback, D3 terminal-before-UsageUnlock, D4 process owner and source ABI for the default macro-OFF path. Compared demo base `ea230ebdd6833a99d3177c54fa67ef5b684c700b` → CI-tested `a833d22487352135a88d6b245eea7f2d103af48b`: **13 new D5Probe/workflow paths**, **zero edits** to old B1 `current_native_candidate.json`, `current_native_source_gate.py`, `run_current_native_validation_cycle.py`, `run_captured_generic_local.py`, historical oneuse-12 or prior D5-A/D5-B custody sources.

**Connector safety/readback:** both affected repos passed disposable branch write/readback smoke tests:
- Demo branch `codex/smoke-d5b-window-20261120-hybridclr_demo-b01`, smoke commit `191d466f08e9d17407683b1e5c3d5f6aca27a91c`.
- Native branch `codex/smoke-d5b-window-20261120-il2cpp_plus-b01`, smoke commit `fa79bb78780b3c59ff110f226bcbe0a8a7f210d5`.
These remain disposable and outside production/review branch; connector branch deletion unavailable.

## 2. Actual implemented source modules and their limits

### Native C10 window witness and actual method-guard instrumentation

`libil2cpp/vm/AssemblyShadowD5WindowProbe.h` defines a process-lifetime C++11 `WindowProbe` with lock-free-style atomic counters (no claim of target lock-free ABI), no VM/GC/managed callbacks, logging, dynamic allocation or mutex inside the witness, one-shot Arm and max **20–2000 ms** bounded P5 hold. Its `WindowSnapshot` is eleven fixed `int32_t` fields with phases `Idle→Armed→AtP5→AtP6→Complete`, P5/P6 and release counts, timeout count, active-shadow method attempts allowed/denied and cross-P6 race count.

The actual native `AssemblyShadow.cpp` changes are all gated by `#if defined(HYBRIDCLR_R03_D5_WINDOW_PROBE) && HYBRIDCLR_R03_D5_WINDOW_PROBE`. During the test-only successful `CommitTransaction` after D4 `PublishActive`, the witness captures P5; it temporarily **unlocks the transaction lock**, executes bounded P5 hold *after* metadata/assembly/usage release, then relocks and validates `s_state==Committing` before advancing real P6. The same test flag samples the actual `AssertMethodIsActive` active-shadow `MethodInfo` outcome and records whether the execution-guard call was **admitted while both entry and exit were still at P5**. It does not substitute a synthetic MethodInfo or intentionally change the return value. The compiled default (flag undefined/0) removes the probe code and leaves the original D2/D3/D4 behavior intact.

**Critical scope limitation:** the test flag changes actual scheduling/lock scope by widening P5→P6, so successful/failed behavior under probe **is not proof of normal production timing**. A real Player result is required before claiming an actual concurrent Shadow body ran/was denied, and even a denied test case does **not** independently prove whole-VM epoch coherence. Probe-induced lock order, unexpected exceptions, diagnostics and bounds need independent source review before any Local run.

### Isolated native overlay, managed Player candidate and Unity build entry

- `Tools/AssemblyShadow/R03IR/D5Probe/R03D5WindowOverlay.cpp` provides four `IL2CPP_EXPORT` P/Invoke functions (`WindowProtocolVersion`, `ArmP5Window`, `ReleaseP5Window`, `ReadP5Window`), using an 11-int32 fixed wire format and inert feature-OFF returns, **without** any host global `operator new/delete`.
- `.../R03D5P5WindowPlayer.cs` is a *test-only* C10 Unity 2022.3.62f2 macOS `BeforeSceneLoad` candidate: an exact hashed `Methods` DLL is staged by real `AssemblyShadowRuntime` managed APIs, native window is armed, a worker observes P5 and attempts `R03.Node.Keep` on an actual active-shadow method during the window, native counters are fetched and JSON written with `FileMode.CreateNew`. A positive early admission is reported `UnsafeEarlyMethodAdmissionObserved` (critical finding), not a successful qualification. Any apparent P5 denial is labeled `CandidateObservedDeniedInP5_RequiresIndependentBinaryProof`, **not** an accepted real Player pass. `actualLinkAndBinaryIdentityExternallyAuthenticated=false`, `R03Accepted=false`.
- `.../R03D5Build.cs` adds **a distinct Unity Editor entry** `AssemblyShadow.R03.D5.Editor.R03D5Build.Build` with a fresh project marker, exact Unity 2022.3.62f2/StandaloneOSX guard, pinned native source SHA, manifest/overlay/managed SHA checks, `PinnedSourceInstaller.Install()`, isolated copy of the D5 overlay into `libil2cpp/vm`, ordinary `PrebuildCommand.GenerateAll()`, feature-ON or feature-OFF `HYBRIDCLR_R03_D5_WINDOW_PROBE` compiler flag, and actual `BuildPipeline.BuildPlayer` code plus an exclusive receipt. **This C# builder has not been compiled or invoked by Unity.** Its BuildReport source contract would only report build status; `independentLinkedBinaryProof=false`, `actualD5PlayerRun=false`. No `run_d5_local.py` or approved `WEB_TO_LOCAL` exists.

### Native install/source→compiler/object/link *materials* verifier

`d5c10_link_source_pinset_v1.json` (Git blob `c709a15e27b6b3b7fa0091d36ef3fc514df4a4ba`) names **13** actual pinned `libil2cpp` source/header files including new D5 header, the two native modified files, three demo isolated overlay/Player/build sources, five expected translation units and four test-only exports. **Every 13 native Git blob** was independently re-fetched and matched the actual native source at `8eeb3cc53a451a6925b490d623c81753822cb1d4`. All three demo isolated source blobs also matched.

`d5_link_materials.py` accepts only `evidenceClass=SyntheticSourceHost` before Local authorization. It checks *supplied* installed file byte equality, Git source identities, overlay copy identity, self-described `BuildReceipt`, five compiled source/object hashes and command text, link command inputs, a Mach-O magic/digest and supplied `nm` symbols. On synthetic success it explicitly returns **`SyntheticMaterialCoherent_NotIndependentUnityBuild`**, `actualUnityOrIL2CPPExecutionVerified=false`, `actualBeeCompilerCommandExecutionVerified=false`, `realPlayerC10Passed=false`. **The synthetic tests deliberately construct fake object, Mach-O and symbol files. This is an integrity schema/test harness only**, not independent proof a real linker produced those bytes. Later Local validation must derive source→installed files→actual Bee compiler commands→real objects→linked Mach-O/export map→binary SHA→PID evidence independently, not accept a synthetic bundle or its self-reported BuildReport as real.

## 3. Exact completed CI evidence

[**GitHub Actions run 44854825948**](https://github.com/night-outlook/hybridclr_demo/actions/runs/44854825948), pushed demo code `a833d22487352135a88d6b245eea7f2d103af48b`, **attempt 1 `completed/success`, all 4 jobs successful**. Raw logs for each job fetched and audited independently:

| CI host/config | Job ID | Source mutation tests | Synthetic link-material tests | Native C++ host receipts |
| --- | --- | --- | --- | --- |
| Ubuntu 24.04 C++11 | `136694455676` | 32/32 PASS | 25/25 PASS | 6 strict + 6 ASan/UBSan + 1 feature OFF |
| Ubuntu 24.04 C++17 | `136694455671` | 32/32 PASS | 25/25 PASS | 6 strict + 6 ASan/UBSan + 1 feature OFF |
| macOS 15 C++11 | `136694455484` | 32/32 PASS | 25/25 PASS | 6 strict + 6 ASan/UBSan + 1 feature OFF |
| macOS 15 C++17 | `136694455849` | 32/32 PASS | 25/25 PASS | 6 strict + 6 ASan/UBSan + 1 feature OFF |
| **Totals** | | **128 tests** | **100 tests** | **48 strict/sanitized host receipts + 4 OFF controls** |

Native host receipts cover six distinct test states `unarmed`, `denied`, `allowed`, `timeout`, `raced`, `invalid`, each strict and sanitized; C++11 strict `-fno-exceptions -fno-rtti` compiles the exact D5 native header and **real** test overlay in three source-host translation units. ASan/UBSan builds reported no unexpected sanitizer errors. None of these builds compiles full `AssemblyShadow.cpp` or runs a Unity Player. The workflow emits explicit `actualIL2CPPCompiled=false`, `realUnityPlayerExecuted=false`, `D5BLocalExecution=NotAuthorized` and `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`.

**Nonpassing intermediate CI attempts were not reclassified**: earlier attempts between baseline C10 host success `44853819179` and final `44854825948` failed while adding the Unity build-source mutations, restructuring the workflow and correcting a **39-character typo** in pinned `vm/Runtime.cpp` (correct real Git blob `1b176ee5fd3e2127a0237877e5c9c32bc53058b3`). The successful current result uses the corrected 40-character file SHA, corrected source checks and a complete valid three-step workflow. Their failed historical conclusions are retained in Actions.

## 4. Primary findings and unresolved risks

| ID | Status at current source-only checkpoint | Independent review/follow-up |
| --- | --- | --- |
| D5BC10-PI-01: compile-time isolated native P5→P6 and MethodInfo witness | PASS in exact-source host and source-contract tests | Independently examine test-time transaction unlock, concurrency, metadata lock graph, P5/P6 and no-test default build effect |
| D5BC10-PI-02: native overlay C++11/17 and OFF behavior | PASS in host C++ strict/sanitized + OFF | Does not prove native Unity build/link/export ABI |
| D5BC10-PI-03: managed Worker + exact DLL/PInvoke/build source | Source/negative tests PASS; C# **not compiled** | Unity Editor/Player compilation, test worker lifecycle and native source installation **NotRun** |
| D5BC10-PI-04: 13 native source pins, 5 TU/evidence schema | PASS in checked Git blobs/synthetic file tests | Synthetic fake Mach-O/nm output is **not actual Bee/link proof** |
| D5BC10-PI-05: all 18 planned D5 Player cells | **18/18 NoCoverage**, including C10 | No actual Player CID/PID; no green Local status is allowed |
| D5BC10-PI-06: exclusive Local oneuse root, six authentic historical paths, actual 4-remote admission, independent approved handoff | **NotRun/NotIntegrated** | Future Local runner and separate user authorization mandatory; `APPROVED_LOCAL_HANDOFF_BLOB=None` |
| D5BC10-PI-07: real post-Codec partial publication, P4 failure, post-active exception, GC, 32-bit ABI and first V2 readback | **NotImplemented / NotRun** | Additional test-only producers and independent source review necessary |

**Primary conclusion:** This is a **first C10 real-Player producer *candidate* and source→link provenance schema, fully source/host tested, but not actual Unity/IL2CPP qualified**. It is ready for a separate **independent D5-B C10 design/source/CI review**. Passing that review may authorize subsequent Primary preparation or a separately approved focused Local build *only if all remaining pre-Local constraints are resolved and user explicitly approves the Local scope*. It does **not** mean D5-B or R03 complete.

**Status at publication:** `D5B_C10Primary=SourceHostComplete`, `D5B_C10IndependentReview=Pending`, `D5BLocalExecution=NotAuthorized`, `D5LocalValidation=NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`.
