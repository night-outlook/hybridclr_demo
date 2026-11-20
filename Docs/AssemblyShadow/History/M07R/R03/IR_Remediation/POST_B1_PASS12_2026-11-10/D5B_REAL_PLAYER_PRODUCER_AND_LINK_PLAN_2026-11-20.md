# R03 B2 D5-B — real-Player producer and native link preparation plan

**Status: source/design preparation only. NO Unity/IL2CPP/Player execution.** Date: 2026-11-20 UTC. This record is an implementation plan following [independent D5-A `PassD5AForD5BPreparation`](D5A_INDEPENDENT_SOURCE_REVIEW_2026-11-20.md). It does not add native production code, actual Player fault producers, or Local execution authority. Work to implement it requires a separate scoped Primary task and independent test-harness review before a user-approved Local handoff.

## Objective and source authority

D5-A successfully established a 33-file, four-repository source-only inventory; it did **not** prove the 12 native `libil2cpp` inputs were installed or compiled, did not run a full translation unit or a Player, and left all 18 D5-Cxx Player scenarios at `NoCoverage`. The first D5-B preparation slice now provides source-only remote-ref and historical-root contracts. It does **not** change those empirical facts.

Branch `codex/assembly-shadow-r01b-h1`:
- `hybridclr_demo`: the D5-B source-only CI-tested commit is to be bound in the sibling [Primary report](D5B_SOURCE_CUSTODY_PRIMARY_REVIEW_2026-11-20.md); future Local will need its own independently reviewed latest pushed SHA.
- `hybridclr@c3c232023724cbad565b85e9b2c3beea8ce2789a`.
- `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`.
- `il2cpp_plus@3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699`.

The *historical* Player harness `Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs` restricts Unity 2022.3.62f2/macOS arm64, builds an isolated project and performs actual `BuildPipeline.BuildPlayer`. It must **not** be reused via the old B1 `run_captured_generic_local.py` with replaced pins. The new coordinator and its precise run/receipt contract must be separate and independently reviewed.

## 1. Source pin, installation and actual compilation proof

**Phase B1 — source-authenticated installation contract (Primary, source-only).**
- Freeze a complete D5-B source manifest at the reviewed head, including the original Unity package, HybridCLR Runtime/Codec, `AssemblyShadow.cpp`, both D2 registry publishers, D3 phase/lease code, D4 process-owned header, D1 receipt and original source roster.
- Preserve all original Git history and B1 `current_native_source_gate.CURRENT` / 14-file/46-VM contract unchanged. Use a distinct D5-B manifest; old oneuse-12 remains a read-only comparator.
- Define a reproducible native installation record for the **12 reviewed `libil2cpp` source files** with both SHA-1 Git object hashes and SHA-256 file hashes. `check_native_file_copy` presently validates only synthetic file copies; it is **not a Unity installation receipt**.
- Independently prove `NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp` and its global `operator new/delete` definitions are absent from native compile inputs and the linked GameAssembly. Do not rely solely on file location.

**Phase B2 — authentic build/Player evidence support (separate later Local authorization).**
- Capture exact installed `libil2cpp` bytes, generated `MethodBridge.cpp` and other HybridCLR outputs, Unity `BuildReport`, Bee DAG/compiler command lines, full translation unit compilation, native object and linked binary SHA-256/UUID/architecture, C++ flags, and Unity/SDK build environment.
- Require real separate ON/Release and OFF/Release Unity 2022.3.62f2 macOS arm64 IL2CPP builds, no reuse of previous output or test-host binaries.
- A source-only or synthetic copy receipt cannot set `actualUnityNativeCompilation=true` or `actualPlayerLinked=true`. Only externally authenticated Local evidence may set them.

## 2. Future real-Player fault-producer designs

Each row is a **planned** source/Player test, not an implemented producer or passed cell. Proposed fail points reference the reviewed [42-cell D5 matrix](D5_LOCAL_VALIDATION_MATRIX_2026-11-20.md). Preserve `NoCoverage` until the relevant probe is compiled and its linked test binary, case ID and PID are independently authenticated.

| Cell | Required real source boundary and instrumentation concept | Observable requirements |
| --- | --- | --- |
| C01/03 | Actual native `CommitTransaction` P0→P6→Complete and source-witnessed preappend used-closure refusal | No false terminal on P0; actual initializer success and stable active owner |
| C04/05 | D2 `MetadataCache::PublishInterpreterAssembliesBatch` and physical/CLI registry scopes under existing metadata→assembly→usage lock order | Capture registration sizes and release order; no false Codec rollback claim |
| C06/07 | Actual `InterpreterMetadataIndexRuntime::PublishBatch` immediately before `Codec::PublishBatch`; separate test-only partial publication scenario inside Codec *only if independently designed and reviewed* | Distinguish pre-Codec input refusal from P3 partial/unknown outcome; terminal-first error and no in-process retry |
| C08 | Runtime group's real `groups[group].active.store(1, release)` followed by test-only refusal before native `s_active` publication | Process terminal, no `Validated`, real P4 observable, Codec lifecycle not reversed |
| C09 | Native `ProcessSnapshotOwner::TryPublish` ownership move and `s_active.store(release)` before P5 | Prove native owner retained through post-store terminal path; no dangling pointer or implicit cleanup |
| C10 | Deterministic real independent method caller at **P5 after UsageLock release and before P6**, using the actual `AssemblyShadow::AssertMethodIsActive` method-entry gate | Measure denial/admission and side-effect canary; if Shadow business execution occurs before approved initializer policy, **Critical ReturnRequired**, not a host-only pass |
| C11/12 | Actual linked staged module initializer (healthy and deliberate managed exception) | Real C# and native V1/B1 first-error origin/provenance; FailedAfterCommit on failure |
| C13/14 | `ScopedPostActiveExit` across actual diagnostic/initializer exceptional exits, with first-error record already populated in a separate negative control | terminal, first error immutable, owner never deleted; do not rely on host C++ exception semantics under `-fno-exceptions` |
| C15/16 | Actual guarded method entry after terminal and new-process restart as a separate Player | AOT canary unchanged and no in-process restart or replay of old Codec state |
| C17 | Real GC/shutdown plus concurrent read-only native snapshot consumers | No after-free/read, no background callback after native/VM shutdown; include process log and signal evidence |
| C18 | Independent ON/OFF feature builds and historical oneuse-12 comparison, as **fresh** Players | Baseline/PureInterpreter unchanged; no old PID or prior Player hash substituted |

**Test-only instrumentation safety:** The first candidate should be additive and strictly confined to a separately reviewed isolated Player test configuration. Every fault switch must be one-shot, source-pinned and record its **real** firing site. Do not allocate managed objects, execute callbacks or block while holding metadata/usage locks unless the exact lock graph has been reviewed; for C10 install a deterministic, time-bounded barrier *outside critical locks*. No permanent runtime behavior switch, post-P3 rollback or automatic restart. Actual source changes in `il2cpp_plus`, `hybridclr` or `hybridclr_unity` require updated four-repo pins, source-host tests, and an independent design/source review before any Local Player run.

## 3. Native integration first, negative fault campaigns second

Recommended execution sequence once separately authorized:

1. Primary designs/reviews the D5-B source install manifest and isolated test project; commits new test-only sources and source-host tests. An initial **real native build/launch smoke test** may be authorized separately before enabling any P3+ fault producer.
2. Publish and independently review an exact `WEB_TO_LOCAL` with the user-approved immutable four-repository source tuple, complete historical root bindings, valid one-use output, actual Local commands and evidence budget.
3. Local performs read-only admission and then **one** fresh ON/Release and OFF/Release build under the approved scope. Stop immediately on actual full TU C++/IL2CPP compile failure, source-roster mismatch, global allocator override collision or mismatched native binary.
4. Only once native installation/Player controls are proven, run fresh isolated processes for P0→P6 failures, C10 concurrency and GC. If an exact real fault producer is missing, mark the case `NoCoverage` and stop for Primary, not `Passed`.
5. Local publishes immutable source→build→binary→PID/first-error/phase evidence. Independent review may then decide `Pass`, `ReturnRequired` or `Blocked` for that authorized Local scope. D6 Human Review Gate remains a separate explicit human decision.

## 4. Mandatory review boundaries and stop

The source-only custody primitives in `d5b_custody_authority.py` are **not** a complete local runner:
- `check_proposed_custody` requires all six history roles and rejects nested old roots, but the actual local bindings of those absolute paths are still **NotRun**.
- `verify_live_source_heads` refuses to operate while `APPROVED_LOCAL_HANDOFF_BLOB=None`. A later independent review must pin an actual approved handoff Git blob and verify it *matches the file bytes*, then use actual `git ls-remote` for each repository. Synthetic mock tests are not live remote evidence.
- `check_native_file_copy` compares exact source bytes in a **synthetic** 12-file copy; it does **not** prove Unity installation, compiling or linkage.
- All 18 Player cases remain `NoCoverage`; V2 first-recovery and 32-bit target ABI remain unproven.

**Current authority:** `D5BPreparation=SourceCustodyOnly`, `D5BIndependentReview=Pending`, `D5BLocalExecution=NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`. No Unity/SDK/Player, D6, H2/M08A/X02/SNAP-01 or Human Review Gate.
