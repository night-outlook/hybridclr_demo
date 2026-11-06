# Primary Implementation source review — oneuse-05 capacity admission

Date 2026-11-06 UTC. Scope: `IR-LOCAL-R03-INITIALIZER-04-CAPACITY-01` only.
This is Primary self-review, NOT independent R03 review, actual Mac
capacity clearance, Local validation or Human Review Gate.

## Empirical evidence inspected

Canonical `Handoff/RETURN_TO_WEB.md`, Local checkpoint
`History/M07R/R03/local-validation-initializer-20261106-oneuse-04/`,
and original `FINDING.json`, `LOCAL_RESULT.json`, the two original
statvfs sample receipts and before/after preservation:
- At actual source demo
  `e0f52c008b6b244e58be135e9bdba46192b76d04`,
  two same-device samples were `26,557,333,504` and
  `26,553,147,392` bytes available against required
  `26,843,545,600`. Both failed.
- The second shortfall is `290,398,208` bytes. The cause of
  occupied space and eligibility of any deletion are unknown.
- 15/15 cells NotRun; Unity/IL2CPP/Players/host/VM recovery all
  NotRun. Both reserved oneuse-04 roots absent, no product
  ledger or seal. No reclassification is authorized.
- Exact source/CI, SDK, historical S and 17 prior checkpoints
  were reported preserved. Earlier oneuse-03's separate
  real build, host custody and product seal remain valid
  only in their original scopes, with failed Players.

## Deliberate policy decision

No real owner/size/reclaimability data exists for a
non-protected deletion candidate. Primary refuses to
delegate `rm -rf`, generic cache purge, SDK/Unity tool
deletion, Git garbage collection, snapshot thinning,
historical run removal, evidence move, APFS alias,
alternate device or temporary-dir redirection.
The user may independently and explicitly authorize
a **specific outside-protected path** after a read-only
inventory and data-owner review; that decision has
not yet occurred. The user may also otherwise create
free space on the same actual APFS volume.
No remote Primary code can guarantee or cause free
bytes to increase on the user's Mac.

Maintain exact20GiB hard /25GiB two-sample mandatory /
40GiB advisory thresholds; optional >=32GiB headroom
is a nonbinding risk recommendation only. Never
substitute APFS purgeable-space counters, file logical
size, cached CI or reused earlier capacity samples.

## Source review

`Tools/AssemblyShadow/R03IR/capacity_readiness.py` is
a deliberately separate read-only program:
- One actual `os.statvfs(parent).f_bavail * f_frsize`
  physical observation per invocation with UTC
  timestamp and st_dev, comparable to Local's
  original measured quantity.
- Fixed no-overwrite absent oneuse05 product/raw-host
  roots, canonical existing output parent, original S,
  workspace and Unity file; rejects symlink aliases,
  same-tree source/evidence overlap, wrong sibling name
  or noncanonical candidate.
- No automatic candidate discovery. Only explicit
  outside-protected on-device candidates are inventoried,
  without following symlinks or emitting file contents.
  Additional explicitly named SDK/user roots are protected
  using `--protected-root`. System sensitive roots
  cannot be inspected as deletion candidates.
  Logical/allocated bytes are only estimates;
  APFS clones and snapshots invalidate a claim
  about safely reclaimable bytes.
- No write/delete/move/purge/mkdir operations or
  automated cleanup. The JSON always carries
  `eligibleForUnityRun=false`,
  `twoIndependentSamplesCompleted=false`,
  `runtimeAcceptance=false` and
  `R03Accepted=false`, even when one sample is >=25GiB.
  The script exit0 is a read-only diagnostic success,
  **never an execution GO**. The second real independent
  sample, full CI/source/SDK/preservation gates and
  original Mac admission remain mandatory.

`test_capacity_readiness.py` covers 14 host tests:
actual external-cwd CLI, original observed ~290MB
shortfall, byte-accurate 25GiB boundary, no implicit
double-sample admission, exact absent roots, safe
candidate link avoidance, source/original/Sdk/output
protection, reuse, wrong sibling name and missing
protected paths. The tests never touch the user's Mac
data. Initial host CI caught a missing protected path
returning FileNotFoundError; the code now rejects it
cleanly with CapacityReadinessError (without mutation).

## Actual CI and limits

Source code and regression workflow have been published.
At source commit
`12c4c426bb61be656a7fc90e28c51784a84b8040`,
[GitHub Actions capacity readiness run 42191174051](https://github.com/night-outlook/hybridclr_demo/actions/runs/42191174051)
completed SUCCESS on **macOS15 and Ubuntu24.04**,
including all14 tests, actual CLI from a separate cwd
and strict no-write guards. This is host-only; it
does NOT measure the user's macOS volume.

The final documentation/handoff commit must receive
its own successful exact-source capacity workflow
AND the two existing mandatory dual-OS initializer
and full native-host workflows. The dedicated
native writer and managed Player API source-blob
contracts remain required but have unchanged
implementation files. No Unity/native/Player source
or deterministic fixture was changed in this cycle.

## Remaining Local/human constraints

The on-device 25 GiB condition is **not currently
confirmed met**; status remains
`BlockedAwaitingExternalCapacityReadiness` until
new actual samples pass. A new oneuse-05 run is
conditionally authorized only after the user
reestablishes true same-volume capacity, independent
double measurement, exact final pushed heads and
CI/SDK/historical source/evidence preservation.
If readiness stays below25GiB, do not create either
oneuse05 root or perform any Unity/Player/host work.
A separate user-approved storage action is required
before Primary can honestly call real capacity clear.

Independent High `IR-R03-01`/`IR-R03-02` remain
open and oneuse-03's pre-callback exception is
still unknown. Native V2, captured-generic15,
original-S compiler/link/Player chain, whole-VM
epoch, GC/RSS/managed shutdown, RC/P/E and
qualifications remain NotRun/NotProven.
`R03Accepted=false; H2Passed=false;
ReadyForHumanReviewGate=false;
runtimeAcceptance=false;
qualificationApproved=false;
fullLegacyRegressionAcceptance=false`;
PureInterpreter disabled.
