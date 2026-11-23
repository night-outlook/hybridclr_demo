# R03 B2 D5-B C10 — Primary remediation of independent ReturnRequired

**Primary status: SourceHostComplete_PendingIndependentRereview (2026-11-23 UTC).** This is not independent approval, not Local Validation and not a real Unity/IL2CPP Player result. Read [the original independent ReturnRequired](D5B_C10_PRODUCER_INDEPENDENT_REVIEW_2026-11-22.md) and the [new rereview request](D5B_C10_PRIMARY_REMEDIATION_INDEPENDENT_REREVIEW_REQUEST_2026-11-23.md).

**Authority remains:** `D5BC10IndependentReview=ReturnRequired`; `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. All 18 real D5 Player cases, including C10, remain `NoCoverage`. No D6/H2/M08A/X02/SNAP-01 or Human Review Gate.

## 1. Exact source tuple and scope

All repositories use `codex/assembly-shadow-r01b-h1`.

| Repository | Exact source revision | Scope |
|---|---|---|
| night-outlook/hybridclr_demo | **`063de11e2459fa6530dee0bd0da9176f14b15c7f`** | CI-tested source, 13 D5Probe/workflow paths changed since previous review `acd6bc55b9e5e48edf52c61083a291c42239a8fa` |
| night-outlook/il2cpp_plus | **`84f9435628b8ff4cc675409f6b4d76dd2753d8a8`** | Two native files since `8eeb3cc53a451a6925b490d623c81753822cb1d4` |
| night-outlook/hybridclr | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Unchanged |
| night-outlook/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` | Unchanged |

Native files: `libil2cpp/vm/AssemblyShadow.cpp` and `AssemblyShadowD5WindowProbe.h` only. Demo files: `D5Probe/R03D5P5WindowPlayer.cs`, `R03D5WindowOverlay.cpp`, `R03D5Build.cs`, `D5NativeReceiptHost.cpp`, `D5WindowFeatureOffHost.cpp`, `d5_c10_native_receipt.py`, `test_d5_c10_native_receipt.py`, `d5_window_source_contract.py`, `test_d5_window_source_contract.py`, `d5_link_materials.py`, `test_d5_link_materials.py`, `d5c10_link_source_pinset_v1.json`, and `.github/workflows/r03-b2-d5-c10-window-source-host.yml`. None of the legacy B1 runners, oneuse-12 outputs, D5-A/custody source, or Local-owned handoff documents were edited. GitHub Connector compares independently confirmed precisely these two native and 13 demo paths.

The manifest authenticates intent for exactly **13 native Git source/header blobs**, **5 native translation units**, and now **8 C exports**. Previous oneuse-12 evidence is historical, not this C10 result.

## 2. IR-D5BC10-01 — Target identity and constructor-denial separation

Under the test-only `HYBRIDCLR_R03_D5_WINDOW_PROBE` guard, `AssemblyShadow::AssertMethodIsActive` now records only a real active-shadow `MethodInfo` with exact physical assembly `Methods`, declaring type `R03.Node` and method `Keep`. Constructor and unrelated Methods assembly calls cannot increment the C10 target counters. The original execution-guard boolean and normal feature-OFF implementation are unchanged.

The managed worker identifies the zero-parameter integer `Keep` method, constructs its instance, verifies a native canary bind, and only then sets `keepAttempted` immediately before `method.Invoke`. Constructor failure or metadata lookup before this point is explicitly `NoCoverage`, not a Keep denial. Synthetic receipt tests reject constructor-denial snapshots lacking the target-attempt event. No real constructor/MethodInfo was executed in CI.

## 3. IR-D5BC10-02 — Native body side-effect witness

In the isolated Player-only VM branch, the overlay binds the genuine active-shadow `R03.Node` instance using a managed `GCHandle` token, validates `Methods/R03.Node` identity and the nonstatic private `int stable` field bounds, and retains its own pinned native GC root. The native observer reads `stable` by its validated offset before `Keep` and again after the worker has joined, without managed field reflection after a possible terminal event. The original Methods fixture starts at `stable=0`; `Keep` returns 42 and increments it.

The existing eleven-int32 P5 window fields now count **Keep-specific** allowed, denied and raced guard decisions. A new fail-closed synthetic receipt reader distinguishes `BodyExecuted`, `BodyNotExecuted`, `Unknown`, `AllowedGuard`, `DeniedGuard`, `RacedP6`, and `NotAttempted`. A denied *candidate material* requires explicit Keep attempt, matching native canary before/after=0, exactly one real-target denied guard count, P5 observation/no timeout, worker completion, state 9 and an immutable first error. Any missing, conflicting or unbound evidence is `NoCoverage`, never Passed. Body mutation or allowed guard during P5 is flagged `UnsafeEarlyMethodAdmissionObserved_SourceMaterial`, not promoted to a real Player outcome.

**Limit:** the Unity native `GCHandle`, class/field metadata, first-error binder and entire production `AssemblyShadow.cpp` translation unit **have not been compiled or executed** by this host CI. These are only source-reviewed intent and synthetic model cases until a separately approved Unity build.

## 4. IR-D5BC10-03 — Fixed, exclusive native evidence

The previous post-Commit managed JSON/FileStream writer was removed. The test-only native overlay opens a new absolute evidence path while healthy using `O_EXCL | O_CLOEXEC | O_NOFOLLOW`, permission 0600, and never reopens a prior output. It writes a fixed **212-byte identity/PID/run/request header**, ten **32-byte** phase/method/canary/event slots, and a **4,120-byte** first-error block (total **4,652 bytes**) using `pwrite` and `fsync`. An atomic slot bitmap rejects duplicate writes. The native-VM branch can capture the existing immutable B1 native first-error code, origin and bounded raw UTF-8 reason through `AssemblyShadow::FirstFailureV2Status/TryReadFirstFailureV2`. Partial, corrupt, truncated, duplicate, unbound, contradictory or source-unknown results fail closed.

Host builds compile the actual new native overlay and exercise exclusive creation, duplicate event refusal, fixed-length native output, seal and feature-OFF. The Python inspection tests deliberately use synthetic native records and **never authenticate a linked binary/PID**. Their verdicts carry a source-material qualifier; they do not mark C10 Passed.

**Unresolved reachability risk for rereview:** `R03_D5_ReceiptSeal` is implemented with native primitives, but is still **invoked by managed finally** after `CommitTransaction` can make AOT business execution terminal. If that P/Invoke cannot run, the file remains incomplete and the source-only validator yields `NoCoverage`; complete terminal-state delivery is NOT proven. The independent reviewer must decide if this suffices for the bounded source/host preparation gate or requires an automatic native terminal completion path before any future Local authorization. Do not claim this risk closed by host tests.

## 5. IR-D5BC10-04 — Runtime admission hypothesis unchanged

At P5 the test-only witness still deliberately drops/reacquires the transaction lock after the metadata/assembly/usage publication locks have unwound, with a 20–2000 ms bounded window. The normal `Committing` business-admission policy, D2–D4 ownership/rollback/first-error state and feature-OFF source are unchanged. An early shadow business body remains an unproven **critical runtime hypothesis**, not an observed Player defect. Do not impose a naive global `Committing` denial that could block legitimate P6 initializers.

## 6. Fresh CI verified from raw GitHub logs

[GitHub Actions run **45122592338**](https://github.com/night-outlook/hybridclr_demo/actions/runs/45122592338), exact demo SHA `063de11e2459fa6530dee0bd0da9176f14b15c7f`, attempt 1 **completed/success, 4/4 successful jobs**:

| Runner | Job ID | Source tests | Link tests | Receipt tests | C++ host receipts | OFF |
|---|---|---:|---:|---:|---:|---:|
| macOS 15 C++11 | `137519551034` | 39 | 27 | 20 | 12 window + 2 native writer | 1 |
| Ubuntu 24.04 C++17 | `137519551260` | 39 | 27 | 20 | 12 window + 2 native writer | 1 |
| macOS 15 C++17 | `137519551297` | 39 | 27 | 20 | 12 window + 2 native writer | 1 |
| Ubuntu 24.04 C++11 | `137519551470` | 39 | 27 | 20 | 12 window + 2 native writer | 1 |
| **Total** | | **156** | **108** | **80** | **56** | **4** |

All four raw job logs were fetched and counted at this Primary checkpoint. Strict native compilation uses C++11/C++17 `-fno-exceptions -fno-rtti`; sanitized host jobs use ASan/UBSan and report no unexpected errors. **This CI does not compile Unity, the real IL2CPP VM, the C# scripts, a real Mach-O GameAssembly or a Player.** Synthetic `d5_link_materials.py` intentionally constructs fake compiler/object/link/nm/Mach-O material, correctly labeled `SyntheticSourceHost`.

Earlier failed intermediary runs retain failure: `45122188178` (invalid workflow, zero jobs), `45122301968` (old managed-source anchor), `45122380319` (extra pinset authority key), `45122474150` (unused VM-only variables in host compile). Only the final exact source run `45122592338` is 4/4 PASS.

## 7. Remaining gates and stop

**NotRun/NoCoverage:** Unity 2022.3.62f2 managed build, full native TU and IL2CPP conversion, Bee compile input DAG/object provenance, real binary/UUID/export and PID/argv joins, actual P5 business-body side effects, GC/shutdown, 32-bit ABI, strict VM V2 recovery and **18/18 real D5 Player cells**. The D5-B custody `APPROVED_LOCAL_HANDOFF_BLOB=None` remains binding; six historical roots have not been authenticated for new Local, no new one-use Local execution authority exists, and the user has not approved D5-B Local execution.

**Next permitted task:** independent **design/source/host C10 rereview** of these exact source commits and raw CI; independent reviewer selects `PassD5BC10ForNextPreparation`, `ReturnRequired` or `Blocked`. Even Pass is limited to preparation, and never authorizes Unity, Local Validation, R03 acceptance or a Human Review Gate. Primary must not approve its own work.
