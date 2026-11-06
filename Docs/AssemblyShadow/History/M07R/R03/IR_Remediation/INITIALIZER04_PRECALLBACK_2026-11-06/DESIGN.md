# R03 initializer oneuse-04 — native first-failure recovery and pre-callback isolation

Date: 2026-11-06 UTC. Owner: Primary Implementation. Active branch:
`codex/assembly-shadow-r01b-h1`. Scope: resolve the diagnostic blind spot in
`IR-LOCAL-R03-INITIALIZER-03-PRECALLBACK-01`. **No change to product VM,
interpreter, HybridCLR Unity package, historical fixtures or stage acceptance.**

## Evidence-backed starting state

Real Local `oneuse-03` ran exactly once with demo
`7a3b6c31408d8fd8b9fb5f74d78be4fa65670915`; its evidence was
published at demo `ec753f2facb4b2645083ed969d40d541c9f03cf4`.
One actual Unity2022.3.62f2 macOS ARM64 ON/Release IL2CPP build,
ten real native host components, 41 initializer host tests,
original S archive/90 cells/59 process joins, strict native host
custody and real product evidence seal **Passed within scope**.
Both independently launched Players exited2 and the strict V1 raws
remained zero bytes. Both actual native journals authenticated
Commit19/state9, native read-1/prepared.state0 and Seal reason1,
**without phase299 or300 native callback entry**. The control's
Commit19 violates its expected healthy0/6; the failure's19/9
does **not** prove the intended post-preparation sentinel because
no native preparation callback ran. Neither record authenticates
a field3/positive mask15/callback1 witness.

Local correctly classified `oneuse-03` FAIL/ReturnRequired,
13/15 cells Passed, real Player semantic verifiers NotRun_CommandFailed.
Its source, command PID/request/nonces/build, raw bytes, complete native
journals, original S and product seal are immutable. `oneuse-01` stays
BLOCKED; `oneuse-02` stays FAIL including its original failed seal.
No attempt to retroactively rerun or promote those results is valid.

## Independently inspected implementation

`hybridclr/metadata/StagedAssembly.cpp`
`Assembly::RunStagedModuleInitializer` attempts the physical published
`<Module>` class initializer and catches
`Il2CppExceptionWrapper`, `std::exception` or unknown errors.
Its existing `ManagedExceptionDetail` directly walks the captured
exception and bounded inner-exception chain, without invoking
managed `ToString`. The caller
`il2cpp_plus/libil2cpp/vm/AssemblyShadow.cpp` on failed Commit
keeps the string through `Result(..., detail)` in the transaction's
`recoveryTerminalDetail` and marks `FailedAfterCommit`.
`AssemblyShadow::GetRecoveryInfoJson` is the existing native
reader that emits this original string as `reason`, the original
terminal error, state and disposition. **The preceding initializer
journal recorded only numeric error19, not this retained detail**.
Its omission prevented differentiating a delegate/generic/direct
body error, metadata exception, or interpreter `__Internal` PInvoke
resolution failure.

The HybridCLR interpreter's PInvoke compiler resolves dynamic
imports using `il2cpp::vm::PlatformInvoke::Resolve` in
`hybridclr/transform/TransformContext.cpp`. This path can throw,
but the original exported GameAssembly symbols alone cannot prove
the interpreter reached or resolved the import. The first recorded
VM recovery reason is needed before selecting any code repair.

## New test-only native recovery source

`PlayerProject/R03InitializerObservationWriter.cpp` now:
- Opens the existing strict `raw.json` and phase
  `raw.json.native-trace.jsonl` and an independent
  `raw.json.vm-recovery.json` using `O_EXCL|O_NOFOLLOW`, mode0600,
  regular-file/nlink guards **before** calling Configure/Begin.
- Provides test-only `R03_IRW_CaptureRecovery`, called by
  `R03InitializerObservationPlayer.cs` immediately after the
  *real* Commit/GetState and **before any attempted terminal AOT
  canary**. It calls only the existing native
  `AssemblyShadow::GetRecoveryInfoJson`, not a managed reflection
  API or exception formatter. Its bounded original JSON is
  persisted exactly once, with runId/caseId/stimulus/fixture SHA/OS
  PID, a native-return code, and explicitly false acceptance flags.
- fsyncs/closes the recovery artifact, emits phase230
  (actual native getter/result or error/byte count) and managed
  phase231 (call result/Commit/final state) into the preopened
  phase journal. Getter/file problems fail closed and are recorded
  numerically. No retry, fallback synthetic message, mutable
  transaction state, acceptance promotion or native VM source edit.
- Maintains the original strict native V1 Seal predicates: healthy
  control0/6, failure19/9, **one** genuine
  `R03_IRW_OnPrepared` entry, field3, four-bit positive mask15,
  and protected canary1→1.

`verify_initializer_recovery.py` accepts only the exact native
recovery JSON object and the actual VM's original versioned recovery
fields/types; it independently joins the request, fixture digest and
owned OS PID. It rejects duplicate keys, nonfinite values, missing,
partial/oversize or forged source, wrong state/error/terminal
disposition and any true acceptance marker. The narrow
`run_initializer_local.py` binds the result to
`verification.json/nativeDiagnostic.vmRecovery` in both ordinary
and failed Player commands. The original `NotRun_CommandFailed`
classification remains on nonzero exit, regardless of the parsed
exception. For a **successful** focused result it further requires
full phase-journal integrity, VM recovery state/error matching
Commit and, crucially, an exact original
`R03IR.InitializerFailure.AfterPublication.V1` substring for a
real post-preparation failure, versus an empty first-failure reason
for the control case. A random pre-callback error19 can never pass
as the intended sentinel.

**No new method/fixture ABI or DLL mode** was introduced: the
original two independently pinned deterministic Methods DLL SHA256
and MVID remain unchanged. The existing native prepared callback
and managed positive body checks are NOT relaxed.

## Regression design

The actual additive writer and VM-shaped C++11 native stub are built
on Ubuntu and macOS, now exercising real file creation/close,
typed original VM recovery schema, positive/negative V1 records
and failure branches with no invented recovery artifact on Open
rejection. Python contracts run actual file/parser round-trip,
genuine process IDs and request binding, missing/mutated PID/nonce,
duplicate/nonfinite JSON, recovery truncation and source mismatch;
synthetic successes never grant Unity/Player acceptance.
The full 15-cell orchestration remains unchanged apart from the
new host verifier and required native recovery record. Managed
Player API compilation checks the actual C# DllImport signature;
real Unity/IL2CPP native link and interpreter PInvoke resolution
remain **Local Validation only**. Prior C++11 host success
proves test source compilation, **not** actual VM behavior.

## Explicit hypotheses / next decision boundary

- **A: pre-callback interpreter execution failure.** Native
  recovery `reason` identifies a direct/delegate/generic/body
  exception or invalid metadata. Primary owns the next IL/metadata
  correction, with actual new source-pinned fixtures and tests.
- **B: test callback PInvoke resolution failure.** The native
  recovery explicitly reports DLL/entry-point resolution or
  PInvoke transformation. Primary will review the exact
  `PlatformInvoke::Resolve` path and the module name/signature
  before altering the fixture or native linkage; an existing
  defined Mach-O export is not proof of resolution.
- **C: unexpected poisoned state/exception.** If recovery reports
  a different terminal code, guard, or no valid reason, retain
  the raw/generator/trace and return without relabeling.
- **D: expected control0/6 and failure19/9 after actual callback.**
  Require strict V1, full native phase journal, VM first-failure
  reason/sentinel, source/build/Player/provenance and the existing
  host custody/product seal. This would be scoped initializer
  evidence for independent review, **not R03 acceptance**.

One new fresh distinct Local cycle
`R03IR-Initializer-20261106-oneuse-04` (plus its
`-native-host-raw` sibling) can answer A/B/C/D without guessing
or delegating nontrivial changes to the Local Agent.
Original S, K and oneuse-01/02/03 evidence stay immutable.
No Human Review Gate, H2/M08A/X02 or additional milestone is
authorized.

## Acceptance boundary

Independent High `IR-R03-01`/`IR-R03-02` remain open, and native
V2/complete general diagnostics, captured-generic failure15,
original S source/object/link/Player closure, whole-VM epoch,
managed shutdown, GC/RSS, RC1–RC6, P1/P2/E0/E1/P3 and performance
remain NotProven/NotRun. `R03Accepted=false`;
`H2Passed=false`; `ReadyForHumanReviewGate=false`;
`runtimeAcceptance=false`; `qualificationApproved=false`;
`fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
