# Primary source review — R03 oneuse-04 pre-callback initializer detail

Date: 2026-11-06 UTC. Reviewer role: **Primary Implementation**.
Not an independent R03 full-stage review, Local Unity execution,
or Human Review Gate approval.

## 1. Fixed evidence and source confirmation

Read the canonical `Docs/AssemblyShadow/README.md`, Local-owned
`Handoff/RETURN_TO_WEB.md`, and actual oneuse03 checkpoint
`Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261106-oneuse-03/`.
The Local's exact executed demo was
`7a3b6c31408d8fd8b9fb5f74d78be4fa65670915`, later published
as `ec753f2facb4b2645083ed969d40d541c9f03cf4`.
Two independently launched Players (PIDs12510/12525) returned2,
strict raw V1=0 bytes; authenticated 22/24-event native
journals recorded Commit19/state9, no native phases299/300,
uninitialized prepared.state0 and Seal reason1.
The real oneuse03 build, ten host components, historical S audit,
host custody and full product evidence seal were separately
Passed within their bounded scopes. No failure is rewritten.

Independently inspected:
- `hybridclr/metadata/StagedAssembly.cpp:544–562`:
  RunStagedModuleInitializer catches the real exception and
  captures bounded direct messages + nested exception details
  through `ManagedExceptionDetail`.
- `il2cpp_plus/libil2cpp/vm/AssemblyShadow.cpp:1229–1238`:
  Commit persists this detail through `Result` in the transaction;
  `GetRecoveryInfoJson` emits the retained `reason` and terminal
  state/error/disposition without running user code.
- `hybridclr/transform/TransformContext.cpp:2440–2470,
  3232–3241`: interpreter dynamic PInvoke import resolution
  can raise a managed runtime exception. A defined native
  GameAssembly symbol does not prove this path succeeded.
- Existing test-only native writer, prepared probe, managed Player,
  deterministic fixture generator and Local verifier/runner.

**Diagnosis**: the precise original initializer exception detail
was already captured but omitted from the preopened observer output.
Both traces alone cannot choose between a failing preparation body,
metadata/delegate/generic transform or a failing
`__Internal` import. Choosing a native/fixture change without the
retained reason would be speculative. The implemented correction
is to read the actual native reason; no production fix is falsely
claimed before new real Local evidence.

## 2. Source changes and fail-closed behavior

- `PlayerProject/R03InitializerObservationWriter.cpp`:
  new exclusive regular `raw.json.vm-recovery.json`, opened while
  healthy and recorded once by `R03_IRW_CaptureRecovery` directly
  from the existing native `GetRecoveryInfoJson`. Bounded source
  size, exact run/case/stimulus/fixture/PID envelope, fsync,
  numeric phase230 failures. Existing strict V1 output and
  native OnPrepared/ReadPrepared/Seal predicates unchanged.
- `PlayerProject/R03InitializerObservationPlayer.cs`:
  actual recovery getter call immediately after Commit/GetState,
  before terminal AOT attempt, records phase231; no managed
  exception string formatting or debug logging after terminal.
- `verify_initializer_recovery.py` and
  `verify_initializer_trace.py`:
  strict versioned JSON schema, exactly typed flags, no dup
  fields/nonfinite/partial/wrong PID/fixture; phases230/231.
  No JSON read grants V2, full recovery authentication or
  R03 runtime acceptance.
- `run_initializer_local.py`:
  verifies the new source files, invokes actual host negative
  regressions, parses the independent native recovery under the
  owned command PID even if raw strict V1 is empty, and keeps
  `NotRun_CommandFailed` on real nonzero exit.
  On a successful focused V1 it ALSO requires full phase,
  coherent VM recovery Commit state, exact
  `R03IR.InitializerFailure.AfterPublication.V1` first-failure
  sentinel for the failure case, and no such unexpected failure
  for control. Wrong code19 from an earlier failing body will
  never pass as the expected post-preparation sentinel.
- `NativeDiagnostics/InitializerHostInclude/vm/AssemblyShadow.h`,
  writer driver/tests and Python host contracts:
  genuine C++11 compilation under a VM-shaped stub, actual
  exclusive file/read round-trip and negative inputs,
  correct original native recovery schema, reuse rejection,
  authenticated PID/source, malformed/forged record negatives.
  This host VM is explicitly synthetic, not Unity.

No method/fixture ABI or deterministic Methods.dll SHA/MVID
changed. Existing exact NativeOn/Off build/host/provenance
checks, strict product evidence seal and K/historical sources
are preserved.

## 3. Host and CI outcomes

Primary published focused source commits and ran GitHub Actions.
Initial exact-source new-CI attempts exposed test-only stub
schema and reused-output fixture errors, corrected without
loosening the native recovery parser or production guards.
The reviewed code-side source commit was
`4a13c8b4482748550196470799e12b5a3684774a`.
The initializer combined workflow
[run 42178163665](https://github.com/night-outlook/hybridclr_demo/actions/runs/42178163665)
and writer host
[run 42178163651](https://github.com/night-outlook/hybridclr_demo/actions/runs/42178163651)
completed success on Linux and macOS at that commit.
The source-bound managed Player C# API compile earlier succeeded
[run 42177702825](https://github.com/night-outlook/hybridclr_demo/actions/runs/42177702825)
on the same current managed Player source blob
(identical in the reviewed code commit).
Each of these is host/source testing only.

**The final Local handoff requires new completed success jobs for
both mandated workflows on BOTH OSes at the exact final published
documentation SHA**. Successful historical runs alone do not
satisfy that gate. The secondary managed/independent writer jobs
can be accepted only with exact unchanged source blob identity
or exact-final-SHA outcomes.

## 4. Remaining uncertainty and Local instruction

The source cannot prove whether the actual Unity exception was
an interpreter PInvoke binding failure, failed direct/delegate/
generic prepare call, metadata/field problem, or another managed
initializer failure. The new native recovery file should
distinguish those cases in a single new real build plus two
separate Players; if native recovery remains unavailable its
absence and trace phase230 are first-class FAIL evidence.
Local shall not choose one unverified hypothesis and change VM
or emitted Methods.dll. Any nontrivial correction returns
to Primary with actual original VM reason and native trace.

Original oneuse01 BLOCKED and oneuse02/03 FAIL remain immutable;
oneuse03 sealed host custody is a bounded PASS, not a Player PASS.
Independent High IR-R03-01/02 remain open, as do complete
native V2/first-failure/general diagnostics, captured generic
error15, original S compiled-object/link/Player chain,
managed shutdown/whole VM epoch/GC/RSS, RC and P/E/performance.
`R03Accepted=false`, `H2Passed=false`,
`ReadyForHumanReviewGate=false`,
`runtimeAcceptance=false`, `qualificationApproved=false`,
PureInterpreter disabled.
