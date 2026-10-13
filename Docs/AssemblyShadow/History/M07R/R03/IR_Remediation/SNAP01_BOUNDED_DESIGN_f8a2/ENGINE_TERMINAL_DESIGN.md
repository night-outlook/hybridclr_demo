# SNAP-01 follow-up: native engine terminal and restart boundary

Status: **architecture proposal and native executable contract only; no Unity scheduler adapter is installed.** Current owner remains Primary Implementation. This document does not claim the51500-class report cascade is repaired; the exact SNAP-01 count is **51213**. No full runtime successor is authorized by this proposal.

## 1. Evidence and the actual missing ownership boundary

SNAP-01 engine PID67384 reached state6→9/code13 and logged its true uncaught sentinel, logger1→1 and500ms, but completed **51213 uncapped native reports**, exiting71. All24 bounded denial samples entered Runtime::Invoke, across input/rendering/update/Canvas/NavMesh plus one Gen2 finalizer. A sampled method is not a frequency histogram and does not establish a dominant producer. The original reporter handles each rejection but does not stop Unity from scheduling another forbidden callback. The guard is doing its job; repeated handled reports are not engine quiescence.

Immutable authority: `../../local-validation-snap01-82bd/preflight/DIAGNOSTIC_COLLECTION.json`, `FAILURE_DIAGNOSIS.json`, `SNAP01_TERMINAL_SITE_ANALYSIS.json`, original engine request/raw/log and `Handoff/RETURN_TO_WEB.md` at demo64da7e51d740d4816907a63864b9c006a9db4b85. No prior N/M/K/I/E result changes.

The required division is:

- **IL2CPP owns admission and first-failure/recovery:** it must continue to reject prohibited bodies and preserve the exact first cause.
- **The native engine owner owns scheduling:** it must stop creating new managed callback work at a real scheduler safe point, drain or cancel owned in-flight native work according to supported semantics, and maintain required native services.
- **The native lifecycle owner owns teardown/restart:** it must retain complete evidence and perform a real native disposition; the failing managed runtime must not be used as its own recovery controller.

Changing Runtime::Invoke to return default values for named Unity callbacks, suppressing native report increments, parking a callback thread, disabling finalizers, catching-and-continuing forever, or exiting early to avoid the full observation window does not implement these responsibilities.

## 2. Public API constraints and platform decision

Primary-source references checked for Unity2022.3:

1. [PlayerLoopSystem](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/LowLevel.PlayerLoopSystem.html) describes native update/condition values as copied from GetDefaultPlayerLoop; native system parameters should not be modified. It does not document arbitrary C function pointers as a supported extension ABI.
2. [Application.Unload](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/Application.Unload.html) lists iOS, Android and UWP support, and triggers an unloading event. This does not provide the present **StandaloneOSX** candidate with a supported unload/restart boundary, nor does it prove callbacks after terminal state are safe.
3. [Unity as a Library](https://docs.unity3d.com/2022.3/Documentation/Manual/UnityasaLibrary.html) lists Android/iOS/Windows/UWP integration and warns that native/managed plugins may require adaptation. Do not assume a UnityFramework API for a macOS standalone executable or use an iOS same-process unload claim to establish fresh-process recovery.

Accordingly, the selected architecture is a **source- or vendor-supported native scheduler adapter**, with a pinned implementation and explicitly reviewed safe-point, thread, callback-drain, maintenance and lifecycle contract. No such concrete adapter has been established by this cycle. Its identity, declarations and ownership are a hard integration dependency, not a detail Local should invent.

Alternatives assessed:

| Approach | Disposition |
| --- | --- |
| Verified native engine-owner gate at scheduling safe point | Selected design; requires real supported integration and evidence |
| Managed SetPlayerLoop/quit callback after poison | Not accepted: managed entry can itself be denied and native callbacks outside the chosen loop/finalizers remain; no safe-point proof |
| Invented native PlayerLoop pointer/private symbol interception | Rejected without supported ABI, ownership and review; symbol availability is not enough |
| Supervisor terminates process immediately | Possible separate operational failure-containment policy, **not a passing1..64/500ms experiment**, not authorized here |
| Counter cap/coalescing/sleeps/default return/managed-name exemptions | Rejected: conceal the failure or change guard semantics |

If supported native scheduler control is unavailable for this exact standalone target, admission to the *repaired-engine experiment* remains Blocked. Do not claim impossibility in principle, but do not substitute an unverified pointer call or fictitious acknowledgement. Primary must obtain a reviewed engine-owner integration or return an explicit platform/design decision; Local is not asked to implement it.

## 3. Versioned native ownership contract

Prepare one process-lifetime coordinator while healthy, before publishing it to callback threads. Bind ABI version, exact Unity engine/platform build hash, native adapter module hash and instance, owner thread/executor, run/request/nonce/PID, native state generation and evidence descriptors. Function pointers must come from a typed, authenticated registration by the actual owner—not string lookup or a managed delegate created after failure. A SHA-256 digest alone is not proof that an arbitrary pointer is trustworthy.

Prototype: `reference/terminal_boundary.h`. It deliberately contains **no Unity call, adapter installation, thread suspension, process exit, callback sleep, counter increment suppression or method guard override**. It models the ordering and evidence obligations below. All methods except Request, State/MayScheduleManaged and the atomic late-dispatch signal are owner-thread operations; Prepare runs before concurrent publication. The implementation and tests do not certify concurrent arbitrary owner method calls.

States:

`Unbound → Prepared → Publishing → Requested → Acknowledged → ReadyForRestart`

Any invalid bound acknowledgement, time/counter regression, unexpected managed dispatch, incomplete maintenance/evidence or failed full-window bound leads to `Failed`. There is no recovery to Prepared in the same instance. Publishing prevents consumers reading partially initialized first-failure metadata; concurrent Request losers cannot overwrite the first cause/generation/time. Unsupported/unbound state cannot admit a repaired runtime launch.

### A. Healthy preparation

Keep the original Player loop and guards unchanged until a supported owner registration has been authenticated. Prepare complete capture buffers/output descriptors and preserve old source/app/SDK identity. Record the uncapped native reporting counter **before the genuine trigger**. No managed helper becomes an implicit post-terminal allowlist.

### B. Terminal request on the rejection/report path

After the actual native terminal state and first recovery are published, latch a single fixed-size request with cause, generation and monotonic origin time. This path performs only bounded lock-free publication; it must not acquire engine/metadata/GC locks, allocate, call Unity, format managed data or wait for another thread. Wakeup must use an already prepared native signaling mechanism whose safety on this callback thread is documented. Report and return/unwind according to the unchanged guard/report behavior.

The observation starts at the original genuine failure/report event; it does **not** restart after quiescence acknowledgement to hide the transition's report burst. Counters are read from the original CompletedCounter; no derived or saturated counter replaces it.

### C. Scheduler safe-point ownership transfer

At the owner-controlled scheduling boundary, stop **admission of new managed callback work**, not the execution guard itself. Existing stack frames must unwind through their original ABI; do not longjmp across engine/C++ destructors or fabricate results for already-dispatched methods. Complete/cancel in-flight native jobs according to the actual scheduler contract. Drain render/input/physics/async callbacks through supported cancellation mechanisms. Verify all participating queues and active managed-dispatch counts, including non-main-thread producers.

Only the authentic owner can publish acknowledgement for the exact run/generation/epoch after no new managed dispatch is being admitted and all prescribed in-flight work is resolved. A bool in the plugin is not evidence that the engine obeyed it. Required receipt: adapter build/instance, owner thread, safe-point epoch, queue disposition, in-flight counts, generation, monotonic clock, actual counter, and preserved first recovery.

`MayScheduleManaged` in the prototype is an interface obligation for that scheduler. It is **not** added to Runtime::Invoke as a mechanism for returning benign values after a method was already requested.

### D. Native maintenance during the complete500ms observation

Run the owner's supported native maintenance path. It must keep OS event/control responsiveness, native diagnostic I/O, required GC cooperation and shutdown synchronization functioning without running arbitrary managed business/logger bodies. Maintain original finalizer and class/method guards; do not disable the finalizer worker. If necessary maintenance unavoidably requires forbidden managed work under this runtime policy, mark the integration Unsupported/Failed and redesign it rather than exempt a method name.

The prototype requires an authenticated epoch, monotonic sequential maintenance pulses, no post-request managed admission, no report counter rewind, a durable complete snapshot, and the full500ms interval. Its maintenance bitmask is **only a model input**; real integration must independently observe the services rather than set mask0x0f to make a test pass. Likewise its timestamps are synthetic test inputs, not proof of wall-clock progress.

At window completion read the original uncapped CompletedCounter and require the unchanged **1..64** delta, exact sentinel and logger1→1, healthy GC31, first state6→9/code13 and recovery. Counts65 or51213 remain failure. A missing ack, dead native pump, early exit, callback sleep or native-fatal cannot become success. The transition itself must meet the bound; do not ignore pre-ack reports.

### E. Evidence commit and restart

Durably finish the complete raw envelope/diagnostic stream and external command/process receipts. `ReadyForRestart` requires those exact hashes and fsync success; it is a bounded coordinator state, not full R03 acceptance or proof of clean teardown. The selected standalone deployment should transfer restart intent to an authenticated native supervisor and create a **fresh process/runtime generation** only after the old instance's lifecycle disposition is independently recorded. Never reload a poisoned managed runtime and call it a new process. Preserve original source manifest and freshly bound app/PID/nonce; startup dependency validation must run again.

The prototype's BindRestart only rejects same PID/run identities. It does not spawn, tear down, prove address-space replacement, authorize new business logic or certify normal finalizer cleanup. The real supervisor/engine handshake and fresh-process proof remain Primary implementation work. On a lifecycle error preserve Failed/ReturnRequired; operational emergency termination is not a passing acceptance result.

## 4. Interactions with diagnostic transport and original assertions

Lossless diagnostic generation must capture a complete coherent final state without depending on newly denied managed formatting, reflection or file operations. Use the proposed native stream design only after its producer/sink/consumer review. An authenticated summary or prefix is not enough. Pre-poison42/42, stable0→2/readable2, baseline code21/type13, actual reflection/delegate/AOT rejections, unchanged canary and first/final recovery, physical reporting mask15/OFF0 and complete JSON/verifier remain mandatory.

The caught baseline/type cases and the engine-uncaught case must remain distinct. Caught diagnostic probes must not inadvertently activate a platform restart while the test still needs final field/recovery observations. Activation therefore needs a prearmed **experiment/deployment policy** with a source-bound route and exact terminal ownership classification, not arbitrary inspection of method names or exception strings. Production must eventually define whether all terminal causes mandate immediate ownership transfer; current diagnostic fixtures cannot silently stand in for that policy.

No additional sixth Player, new engine stimulus, smaller observation window or changed semantic threshold is authorized here. A future integration handoff must review any needed scope change explicitly.

## 5. Executable model coverage and missing platform proof

The native21-scenario suite tests unbound rejection, exactly-once first cause, wrong owner/generation/epoch, in-flight managed work, incomplete maintenance, missing safe-point ack, early-window Pending, time/counter regression, report counts0/65/51213, inclusive64, missing durable evidence, late managed dispatch, and distinct restart identity. Sixteen concurrent request threads verify one winning publisher. It passed strict C++17 and ASan/UBSan here; these results are **synthetic contract tests**, not a real engine loop, scheduler memory model, lock-free ABI, GC or platform lifecycle test. No TSan proof is claimed.

Primary integration gates before runtime:

1. Obtain and review the actual native scheduler/lifecycle declarations and implementation for exact Unity2022.3.62f2/StandaloneOSX. Record who owns the scheduler, safe point and threads. Verify legitimate ABI access and licensing/provenance. Do not ask Local to invent an interface from binary symbols.
2. Implement one adapter, native wakeup and supervisor protocol in the owning source, with bounded memory, lock/thread ordering and unsupported-platform handling. Add build inclusion/export tests and actual interface conformance. Keep the adapter unbound when unsupported; no runtime experiment admission.
3. Integrate the reviewed lossless transport and original semantic predicates. Add failures for unavailable scheduler, invalid ticket, stale generation, reentrant request, uncommitted output, late callback, pending native job, continued finalizer-produced reporting and failed restart handshake. No fake acknowledgements.
4. Source-bound official managed/native compilation, paired OFF/no-request controls, actual scheduler/GC/finalizer instrumentation, and independent static review of every call on the terminal path.
5. Only then authorize a fresh Local runtime attempt with original historical custody/storage/SDK/source and five-case acceptance gates. Observe actual quiescence and native service liveness for500ms, count all real reports and record restart separately. No reuse of SNAP-01 or N outputs.

## 6. Immediate next action

This cycle delivers the requested architecture, bounded representation and executable contracts. It intentionally does **not** repeat the known-failing five-Player run or issue a fictional repaired-runtime handoff. Current owner remains Primary Implementation until native producer integration and the actual engine-owner dependency are resolved. A read-only external design review may assess these contracts, but no agent/human acceptance is inferred from the tests.

All acceptance flags remain false. Historical SNAP-01/N/M/K/I/E failures and strict S custody Blocked remain immutable. Independent full-stage R03 FAIL/re-review NotRun; no H2/X02/M08A/PureInterpreter expansion or Human Review Gate approval.
