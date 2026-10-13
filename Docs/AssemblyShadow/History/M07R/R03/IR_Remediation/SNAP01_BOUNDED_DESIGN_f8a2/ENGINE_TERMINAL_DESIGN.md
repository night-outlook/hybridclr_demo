# SNAP-01 follow-up: native engine terminal and restart boundary

Status: **architecture proposal and native executable contract only; no Unity scheduler adapter is installed.** Current owner remains Primary Implementation. SNAP-01's actual **51213 completed reports in500ms** remain a failure. This proposal authorizes no new runtime execution.

## 1. Evidence and ownership

Engine PID67384 reached state6→9/code13 and its true uncaught sentinel/logger1→1, but exited71 after51213 uncapped native completions. All24 bounded denial samples entered Runtime::Invoke across input/rendering/update/Canvas/NavMesh and one Gen2 finalizer. Sampling does not establish a dominant method frequency. Handling each rejection does not stop Unity from scheduling another prohibited callback.

Authority: immutable `../../local-validation-snap01-82bd/preflight/DIAGNOSTIC_COLLECTION.json`, `FAILURE_DIAGNOSIS.json`, `SNAP01_TERMINAL_SITE_ANALYSIS.json`, engine request/raw/log and Local-owned `Handoff/RETURN_TO_WEB.md` at demo64da7e51d740d4816907a63864b9c006a9db4b85. No historical result is changed.

The architecture separates three owners:

- IL2CPP preserves the exact first terminal cause/recovery and rejects prohibited managed bodies.
- The native engine owner stops new managed callback scheduling at an authenticated safe point, resolves in-flight work and maintains required native services.
- The native lifecycle owner preserves complete evidence and owns supported teardown/restart; poisoned managed code is not its recovery controller.

No default-value return in Runtime::Invoke, report coalescing, counter cap, callback parking/sleep, finalizer disabling or arbitrary managed-name exemption is a substitute.

## 2. Platform constraints and selected approach

Official Unity2022.3 references:

1. [PlayerLoopSystem](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/LowLevel.PlayerLoopSystem.html) documents native update/condition values copied from GetDefaultPlayerLoop and says native parameters should not be modified. This is not a supported arbitrary-function-pointer extension ABI.
2. [Application.Unload](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/Application.Unload.html) lists iOS/Android/UWP support and triggers unloading callbacks. It does not establish a **StandaloneOSX** terminal-control solution or safe callbacks in the poisoned runtime.
3. [Unity as a Library](https://docs.unity3d.com/2022.3/Documentation/Manual/UnityasaLibrary.html) lists Android/iOS/Windows/UWP integration and platform limitations. Do not assume an iOS UnityFramework method for the macOS standalone executable or equate same-process unload with fresh runtime provenance.

**Selected architecture:** a source- or vendor-supported native scheduler adapter with pinned engine/module identity, typed registration, reviewed safe point, owner thread, queue-drain and maintenance semantics. This concrete dependency has **not** been established in this cycle. Native symbols or nonzero function pointers alone are insufficient. The current four repositories have not supplied a reviewed engine-owner interface that meets these obligations.

Alternatives:

| Route | Disposition |
| --- | --- |
| Verified native owner scheduling boundary | Selected design; actual integration still required |
| Managed SetPlayerLoop/quit after poison | Not accepted: managed entry can be denied and no complete native/finalizer ownership is proved |
| Invented PlayerLoop pointer or private ABI call | Rejected without supported declarations and ownership review |
| Immediate external process termination | Possible separate operational failure containment; **not a passing1..64/500ms experiment**, not authorized here |
| Counter suppression, delay, benign callback return | Rejected because it changes or conceals the required behavior |

If this exact platform lacks the required supported integration, repaired-engine admission stays Blocked. Primary must obtain a reviewed adapter or return a platform/design decision. Do not delegate ABI guessing, scheduler design or unreviewed binary alteration to Local.

## 3. Native contract and state machine

Prepare a process-lifetime coordinator while healthy. Bind ABI version, engine/platform build, adapter module and instance, owner executor, run/request/PID/nonce, generation and preopened evidence descriptors. Registration must come from the actual typed native owner. A digest alone does not authorize arbitrary native code.

Prototype: `reference/terminal_boundary.h`. It contains **no Unity calls, adapter installation, OS thread suspension, process exit, managed callback, callback sleep, reporting suppression or guard override**. All operations except Request, State/MayScheduleManaged and the atomic late-dispatch signal are serialized owner-thread operations; Prepare runs before concurrent publication. It is not safe to assume arbitrary concurrent owner-method calls.

States: `Unbound → Prepared → Publishing → Requested → Acknowledged → ReadyForRestart`; invalid authenticated transition/evidence leads to `Failed`. No return to Prepared in the same instance. Publishing keeps readers away from incomplete first-failure metadata; concurrent Request losers cannot overwrite cause/generation/time. Unbound cannot admit a repaired runtime experiment.

### A. Healthy preparation

Authenticate the actual owner and preserve the original loop/guards. Preallocate bounded capture/output/hash state and establish existing precise pinned objects. Bind the source/app/SDK and original uncapped reporting counter **before the genuine trigger**. No new managed terminal allowlist.

### B. Request from the rejection/reporting path

After publishing the genuine native terminal state and first recovery, latch one fixed-size request. No engine/metadata/GC lock, allocation, Unity call or wait on this path. A native wakeup may use only a previously prepared mechanism documented safe for the calling thread. Unwind existing frames normally; do not longjmp through C++ destructors or fabricate already-dispatched method results.

The500ms window starts at the original failure/report event, **not at acknowledgement**. Do not discard the transition's burst. Counts come from the original CompletedCounter.

### C. Real scheduler acknowledgement

At an owner-controlled safe point, close admission of new managed callback work. Resolve already-admitted work according to documented scheduler semantics; account for main-thread and worker queues, render/input/physics/async producers and in-flight callbacks. No variable in a plugin is proof that Unity stopped scheduling.

Only the verified owner acknowledges the exact run/generation/epoch after in-flight managed dispatch is resolved. Receipt includes adapter source/module/instance, thread, safe-point epoch, queue disposition, in-flight counts, time/counter and first recovery. `MayScheduleManaged` is a scheduler interface obligation, **not a Runtime::Invoke default-return implementation**.

### D. Full observation with native maintenance

Maintain OS/control responsiveness, native diagnostic I/O, required GC cooperation and lifecycle synchronization without executing arbitrary managed business/logger bodies. Preserve the finalizer worker and its original guards. If native maintenance unavoidably requires prohibited managed execution, classify the adapter Unsupported/Failed and redesign; do not exempt a finalizer by name.

Require authenticated epoch and sequential monotonic maintenance pulses, no late managed admission, nondecreasing original report counts, complete durable diagnostics and the full500ms. The model's mask0x0f and timestamps are **synthetic inputs**, not independent proof of real maintenance. A concrete adapter must observe and authenticate those services; merely setting the mask is not acceptance.

At the end require unchanged1..64 actual completed reports, exact sentinel/logger1→1/GC31/state6→9/code13/recovery, and all original ON/OFF assertions. Counts65 or51213 remain failure. Missing acknowledgement, native-pump stall, early exit, sleeps or native-fatal cannot pass. The transition's reports count too.

### E. Evidence commit and restart

Durably finish the complete envelope/diagnostic artifact and source/PID-bound command records. ReadyForRestart requires exact hashes and fsync completion but **is not proof of clean teardown**. Transfer restart to an authenticated native supervisor only after the old instance's native disposition is recorded. Prefer a fresh process/runtime generation for the standalone candidate; do not label a poisoned same-process reload fresh. Revalidate source manifest and new app/PID/nonce on startup.

The prototype's BindRestart only rejects same PID/run identities. It neither spawns nor tears down, proves address-space replacement, approves normal finalizer cleanup or starts new business logic. Real supervisor/lifecycle implementation remains Primary work. Emergency termination remains a failure-containment record, not acceptance.

## 4. Interaction with diagnostics and test activation

Use the lossless native stream only after producer/capture/filesystem/verifier integration review. No summary/prefix substitutes for complete slot14/15 data. Retain original25 integers, control fields, guard slot8,42/42, stable0→2/readable2, causes21/13, actual reflection/delegate/AOT denial/no side effects, stable canary/recovery, GC31 and mask15/OFF0.

Caught baseline/type probes and the engine-uncaught case have distinct observation lifetimes. A platform restart must not destroy required caught-case field/recovery evidence. Activation needs a **prearmed, source-bound experiment/deployment policy** and exact ownership classification—not exception text or arbitrary method-name inspection. Eventual production policy for every terminal cause remains separately reviewed; diagnostic fixtures do not define production recovery by accident.

No sixth Player, additional stimulus, shorter observation or relaxed semantic threshold is authorized by this design.

## 5. Model tests and integration gates

The21 native scenarios cover unbound rejection, single immutable first cause, wrong owner/generation/epoch, in-flight work, missing maintenance/ack, early Pending, clock/counter regression, actual0/65/51213 failure, inclusive64, missing durable output, late managed dispatch and distinct restart identities. Sixteen competing request threads have one winning publisher. Strict C++17 and ASan/UBSan passed. These are **simulated contracts**, not real Unity scheduling, GC, finalization or lifecycle proof; no TSan claim.

Before a runtime successor, Primary must:

1. Obtain/review exact supported native engine-owner declarations and implementation for Unity2022.3.62f2/StandaloneOSX, including safe point, thread/lock context, queues, finalizer/GC maintenance and lifecycle. Record legitimate ABI/source provenance.
2. Implement the adapter, prearmed signal, coordinator and native supervisor; provide source-backed receipt identities and unavailable-capability behavior. Keep unsupported integration unbound.
3. Integrate complete bounded diagnostics and unchanged semantic predicates. Add real failure cases for stale tickets, continued scheduling, incomplete queue drain, finalizer-produced report overflow, partial evidence and failed restart.
4. Complete source-bound official native/managed compilation and independent terminal-path review. Host mocks do not certify an engine interface.
5. Separately authorize fresh Local original custody/SDK/host/compiler/storage gates and five-case runtime. Observe real500ms maintenance and uncapped counts; record restart separately. No SNAP-01/N reuse.

Current owner stays Primary Implementation until these gates are met. All acceptance flags false; SNAP-01/N/M/K/I/E failures and strict historical S custody Blocked remain immutable. Independent full-stage R03 FAIL/re-review NotRun; no H2/X02/M08A/PureInterpreter expansion or Human Review Gate advancement.
