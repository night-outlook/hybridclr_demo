# R03 initializer oneuse-03 — Primary source and evidence review

Date 2026-11-06 UTC. Review role: **Primary Implementation**,
not independent full-stage R03 review, Local empirical result or
Human Review Gate.

## Inputs independently inspected

- Exact Local `oneuse-02` source demo
  `7da27a486b529cdebf73100b5ce4c332a1bb7e86`,
  publication `61bf436d65e5909767206d385ecba865e4c7a5ac`.
  Read `Handoff/RETURN_TO_WEB.md` first, then
  `History/M07R/R03/local-validation-initializer-20261105-oneuse-02/`
  `RUNTIME_FINDINGS.json`, factual Local result,
  `batch/BATCH_EXECUTION.json`, `batch/SEAL_FAILED.json`,
  original 0014/0015 native raw/Player/owned commands and
  independent raw manifest. No original results were modified.
- Actual source of `run_initializer_local.py`,
  `R03InitializerObservationWriter.cpp`,
  `R03InitializerPreparedProbe.cpp`,
  `R03InitializerObservationPlayer.cs`,
  `verify_initializer_observation.py`, the native host suite
  and shared `R03/batch_evidence.py`.
- Original S/K/oneuse-01 and R03 acceptance conditions.

## Finding disposition and source design

**PLAYER-01: corrected diagnostic observability; runtime root cause
not yet established.** Both actual Players exited2, strict native
raw=0, no semantic verifier. The built GameAssembly exported
the four original symbols, which only proves their presence.
The old managed catch discarded where failure occurred; native
Open/OnPrepared/ReadPrepared/Seal each had unreported failing branches.
New native preopened `*.native-trace.jsonl` logs exact phase/return
numbers even when strict V1 remains zero bytes. The strict V1
predicate logic is unchanged. Both control and failure still require
real source-bound build/PID/fixture, native callback and postterminal
primitive evidence; no diagnostic trace alone counts as Passed.
Any future actual returned native branch code can support a precise
Primary fix, not a guessed VM change.

**SEAL-02: source-corrected custody architecture, Local revalidation
required.** Oneuse-02 failed on a deliberately retained directory
symlink inside included `native-host-diagnostics`. It was a *real
negative test*, not accidental source corruption. The new runner
places raw host output in an unused sibling, creates an exact manifest
of regular file SHA256 and four symlink literal targets, archives all
regular bytes + manifest without following links and copies this
bound evidence into the ordinary strict product seal.
The original shared `batch_evidence.py` remains byte-for-byte
unchanged. Product seal may now succeed even with failed Players;
that would be a PASS **for seal only**, not 15-cell or runtime PASS.

## Primary review of contracts and risks

- Native journal uses finite fixed input identity, monotonic sequence
  and bounded events, exclusive regular native fd, immediate fsync.
  Failure logging does not call managed reflection, type init,
  managed error formatting or Unity logging after poison. One
  remaining risk is an actual native abnormal termination before
  Open/trace creation; that correctly returns Unavailable.
- New `verify_initializer_trace.py` rejects duplicate keys, partial
  lines, forged PID/nonce/stimulus/fixture, mixed integer/boolean,
  oversize, missing callback/read/Seal and false-to-true acceptance.
  A failed Player keeps `NotRun_CommandFailed` even if the diagnostic
  journal is independently valid.
- New `initializer_host_custody.py` rejects raw symlink traversal,
  enforces node kinds and full regular-byte digest/size capture,
  verifies tar membership and file digests by rereading, preserves
  literal link targets and compares the live raw tree at final
  postflight. The four raw negative links are retained unchanged.
- The Python runner checks **both** newly absent output roots
  before batch creation, source HEAD pins, complete actual build
  receipt, each request/command PID, and source/custody postflight.
  No non-trivial change is delegated to Local.
- Scope risks: real IL2CPP native layout/initializer callback
  semantics are unproven until a fresh Unity Player; one C++11
  host compilation cannot substitute its actual generated C++/VM
  integration. External host-root archive consumes extra disk.
  A failed postflight must remain a distinct failure, not silently
  approve a stale archive.

## Host CI evidence and pre-handoff gate

Source implementation stages were published through GitHub Connector,
then tested on exact source SHAs. The shared current-native host
workflow `r03-ir-current-native-local-cycle-host.yml` includes an
**actual complete ten-component host CLI** on Ubuntu and macOS
followed by literal-link/regular-byte custody and a complete
`batch_evidence.finalize` on an authenticated copy.
Synthetic negative tests independently cover source/trace, actual
native writer/observer host compilation, request/PID failure
classification and host archive tampering. The managed Player API
compile has a separate source-bound workflow.

Prior failed/cancelled CI attempts are preserved and do not prove
success. The final handoff must use **completed/success, two OS jobs
at the exact final pushed demo SHA** for both the initializer and
shared current-native host workflows. Source-only CI never proves a
new Unity Player. The final response must identify exact run IDs
and the remote SHA after publication; if any required gate is not
green, mark this cycle NOT dispatched.

## R03 status

Original oneuse-02 remains 13/15 Passed, two failed real Players,
failed product seal. Oneuse-01 BLOCKED remains immutable.
Both independent IR-R03-01 and IR-R03-02 remain High/NeedsEvidence,
and original-S compiler/object/link/Player chain, captured generic,
NativeV2/first failure/general diagnostics, managed shutdown, GC/RSS,
whole-VM epoch, performance, RC1–RC6, P1/P2/E0/E1/P3 and full legacy
regression are not accepted.
`R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false;
qualificationApproved=false; runtimeAcceptance=false;
fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
No H2/M08A/X02/SNAP-01 or Human Review Gate self-approval.
