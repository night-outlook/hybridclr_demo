# Primary reconciliation — I failure, reserved Boolean response, Debug investigation

Owner: Primary Implementation. Task basis: Local I publication `3a3d8f384bd6f02e7a685f2e3aae5758e850d72a`, original native `c386cdd1e8942561f1d1e1fada52d21ca524f174`. Scope: a source/host-tested native reporting correction and bounded read-only Debug investigation. **No new Player result or full runtime acceptance is claimed.**

## 1. Immutable I facts and evidence

[Original I checkpoint](../../local-validation-i-post-h-custody-7f36/README.md), [read-only failure diagnosis](../../local-validation-i-post-h-custody-7f36/preflight/FAILURE_DIAGNOSIS.json), and Local-owned Handoff/LOCAL_VALIDATION.md / RETURN_TO_WEB.md remain authoritative and untouched. I used demo `036e329691f06dd9a9ed80bc3e2e0ca77a824884` and native c386. All prerequisites and both storage admissions passed; scoped custody/preservation and bounded seal passed. Actual matrix: **14 cells: 10 Passed / 3 Failed / 1 Blocked**. Release and OFF builds Passed; Debug build Failed; two ON release Players terminated SIGABRT; OFF Passed; Debug Player Blocked/NotRun. Neither unavailable ON semantic JSON nor a failed Debug receipt becomes Passed because preceding stages succeeded.

The release baseline process (PID32291/run2ea84debb23345888ffacab742dd3936) captured first failure code21 `ShadowBaselineMethodExecution`; release type process (PID32303/run1aaa4d85f2aa4b0e9d359026277a6727) captured code13 from the prescribed test-only stimulus. Both reached native reporting then `fatal=FixedBooleanAllocationFailed`. These are current-I first-failure observations, **not reconstruction of E's missing historical first failure**. Phase logs are not replacements for the unproduced ON field/counter/recovery semantic records.

Source and permitted I diagnostic text were obtained through a source-pinned, read-only Connector CI export: run38201485545, workflow commit63dd5035205569e5ccde90b254a35af60d951dde, artifact11726195352. The archive was authenticated by ZIP SHA-256 `3d3eefbf36c8bff7789d996addce0bfb9ee1e9533ccfe52efe1f6c92d0be09d7` and all **1,785** exported path/size/SHA256/Git-blob bindings against original demo3a3d/nativec386. This is source/diagnostic transport, not independent execution or an audit of every I checkpoint file.

## 2. Source-confirmed reporting defect; exact abort sub-cause remains unknown

Old `AssemblyShadowTerminalReporting.h::FixedHandledResult` performs metadata readiness checks and calls private `Object::NewPtrFree`. The actual `Object.cpp::NewPtrFree` calls `AssemblyShadow::RequireActiveClass(... ObjectAllocation ...)`. After terminal failure, ordinary object allocation is denied. Therefore the fixed diagnostic response still depended on a guarded post-terminal allocation, despite earlier mock tests presenting NewPtrFree as an unguarded primitive allocator.

The old catch-all message does **not** identify whether I first failed a Boolean readiness/cctor check, the guarded allocation, or another allocation condition. Do not label it an observed out-of-memory error or claim the allocator guard is the uniquely proven first throw. The published Boolean generated source also has a static constructor, so assuming cctor readiness without arranging it was not justified. The correction removes both post-terminal preparation and allocation dependencies.

## 3. Implemented candidate and lifetime contract

Native commit **`0fa7b4fef94062e54f186fda938dd8a3d2304b7e`** adds `vm/AssemblyShadowFixedBoolean.h` and makes two lifecycle calls in Runtime.cpp:

1. At the complete Runtime initialization tail, under the existing initialization lock and **before `AssemblyShadowStartup::MarkCoreReady()`**, require Shadow Disabled. Validate the physical corlib System.Boolean identity, allocate a boxed true through ordinary guarded `Object::Box`, complete its normal readiness/cctor path, and create a **strong pinned GCHandle**. Publish its pointer with release ordering only after identity, payload and pin checks succeed. Healthy bootstrap may use ordinary runtime allocation/cctor machinery; no terminal exemption is introduced.
2. After terminal failure, return the preallocated pinned object using an acquire load and fixed primitive identity/payload checks. **No allocation, Class::Init, cctor, GCHandle operation or allocation-profiler callback occurs in this response path.** The object is held for the runtime lifetime. A missing or corrupted reserve remains an explicit native failure, not a managed reporting exception.
3. During shutdown, clear/release the reserve after managed threads and finalizers stop, before metadata/GC teardown. Host tests cover reserve creation, use, shutdown and reinitialization; actual GC/lifecycle behavior still requires Unity validation.

The old special Object.h friendship was removed: NewPtrFree remains private to ordinary and reporting callers. `Object.cpp`, `AssemblyShadow.cpp`, the normal method/class/allocation guards, exact physical reporting callback classifier, first-error retention and business execution denial are unchanged. Feature-OFF does not initialize the reserve. Ordinary post-terminal allocation remains rejected. This design costs one pinned Boolean object/GC handle per enabled runtime and moves work to healthy startup; no steady-state business allocation allowance is added.

Stage-specific fixed native diagnostics distinguish bootstrap state/identity/boxing/readiness/root errors and reserve unavailable/identity/value faults. They print only bounded native text and primitive metadata. Native failure is never a successful Player result.

## 4. Verification actually completed

[Native CI 38203284632](https://github.com/night-outlook/il2cpp_plus/actions/runs/38203284632) on exact native0fa7 Passed **Ubuntu24.04 and macOS14**. Both normal and AddressSanitizer/UndefinedBehaviorSanitizer configurations passed. The revised harness compiles the actual Runtime::Invoke body, reporting headers **and the actual guarded Object::NewPtrFree body**, while GC, metadata and allocator internals remain mocks.

Coverage: initially unprepared Boolean; healthy initialization and pinning; ordinary post-terminal allocation rejection; eight concurrent readers totalling20,000 reporting iterations per ON configuration; no additional post-terminal allocation/metadata/GCHandle calls; 18 identity negatives; four message controls;18 expected native-fatal modes; shutdown/reinitialization. The repeat count is stress iterations, **not20,000 independent tests**. Real Object.h access tests passed five controls; native observer passed four cases in each normal/sanitized profile using mocked VM state; unchanged native policy passed69 assertions. No Unity process was run by these tests.

Both native artifacts were downloaded through the Connector, ZIP digests verified, and all11 source bindings and7 artifact-member hashes verified against the published source and local candidate. Six text logs are identical across OS artifacts and retained once in `ci/native/`; per-OS artifact identities remain in EVIDENCE.json. Artifact binaries are not published here.

The separate historical R02 workflow **38203284615 remains Failed** at its frozen source verification for AssemblyShadowTypeResolver.cpp/AssemblyShadow.cpp; its later header step was skipped. Those files were not changed in this correction. No R02 rebaseline or claim that all workflows passed is made.

**Still outstanding:** official Unity2022.3.62f2 native translation compilation for the new reserve header/lifecycle source, actual native linking/Player startup, actual GC lifetime/exception transport, complete ON raw semantic evidence and real engine-originated unhandled reporting. G's native syntax evidence belongs to c386 and cannot prove the new native source. Managed Player/API source remains unchanged and its G compilation can be reused only after exact input verification. The current Player's post-terminal managed serialization/reporting remains a separate integration risk; this Boolean change alone does not prove it will emit JSON.

## 5. Debug shared-cache investigation: not dismissed or repaired speculatively

The original Debug Editor.log (Git blob `ff88312ae6a01a3b9fd402f8f290c1b68bc028da`, 7,047,937 bytes) contains two occurrences of `failed to allocate space to load shared cache file at %s`, attributed through BeeBuildPostprocessor result processing to:

- `Library/Bee/artifacts/MacStandalonePlayerBuildProgram/obiza/ubsqkyqrmlqi.o`
- `Library/Bee/artifacts/MacStandalonePlayerBuildProgram/ManagedStripped`

They appear after Tundra success text, but the actual BuildReport has two errors/Failed. Successful native link text does not override that receipt. Storage admissions passed; no retained evidence establishes ENOSPC or authorizes cache deletion.

Apple's published [dyld dsc_extractor.cpp](https://github.com/apple-oss-distributions/dyld/blob/main/other-tools/dsc_extractor.cpp) has matching diagnostic text on a failed `vm_allocate` call. This is **a source-based lead toward shared-cache virtual-memory allocation**, not proof of the actual I emitting binary, invocation, resource pressure or underlying OS error. The literal `%s` and the missing child-task attribution require deeper retained Bee records; do not assume ordinary Unity disk-cache exhaustion or that the error is harmless.

`collect_i_debug_cache.py` now authenticates three original I Git/live anchors, then copies only bounded selected diagnostic extensions from the existing Debug Library/Bee into a **fresh external** directory. It never runs a compiler, Bee command, cache utility or Player. It records file hashes before/after collection, context offsets and exclusions, rejects aliases/occupied destinations/oversize or changing inputs, and labels previously unindexed files **current preserved diagnostic bytes**, not retroactively authenticated build provenance. Missing Bee data returns Unavailable/Failed evidence; no reconstruction or I rebuild is allowed.

Collector tests:14 synthetic controls Passed locally and in [CI38204087861](https://github.com/night-outlook/hybridclr_demo/actions/runs/38204087861) on both macOS/Ubuntu. Original artifact/source/log hashes were verified. They do not prove availability or contents of Local I Bee files. Next Local work must return those retained bytes and command attribution before Primary can close the Debug cause or select a bounded remedy. No warning suppression, global environment change, dyld-cache reset, protected cleanup or report reclassification is proposed.

## 6. Next state and separate permission boundary

The new [J compile-and-diagnostic procedure](J_COMPILE_DIAGNOSTIC_PROCEDURE.md), canonical WEB_TO_LOCAL and final exact four-SHA message permit **one fresh official native SDK syntax compilation and one read-only retained Debug diagnostic collection** after source/custody/root/host gates. They do **not** authorize Unity Editor launch, Player build, Player execution, the14-cell scheduler or an I retry. After return, Primary must review source-matched compilation and Debug diagnosis, then issue any runtime assignment separately.

Preserve original I FAIL (10 Passed/3 Failed/1 Blocked), E FAIL, F/H prerequisite failures, G compile-only Passed and all S/R/Q/P/O/N/A/B/C/D history. Strict historical custody remains Blocked:416,844 original entries,339,367 survivors,77,477 original missing identities/four historical S native roots Missing. Scoped preservation is not restored provenance. Full independent R03 review remains FAIL/re-review NotRun; all acceptance flags false; PureInterpreter expansion disabled. No H2/X02/M08A or Human Review Gate advancement.

Connector smoke commits on `codex/connector-smoke-i-response-6f02` passed exact readback in demo/native; the demo branch also carries only the source-export workflow. These disposable branches remain because branch deletion is unavailable, and are not execution-source assignments.
