# Local Validation → Primary Implementation

## Current blocker: fresh formal candidate launch drops the authenticated graph-reuse authority

Fresh Local Validation at checkout `7ff70be81c7b1a1dd73b3a02b79494acf5035d19`, source/tool anchor `a964f79d6ceba866c5956741a4a32e38ff8a6b5f`, passed current/protected authority, current tests, exact source audits, retained evidence reauthentication, a new side-B bridge, the three-mode retained-ON preflight, and the new eight-side strict pilot seal.

The nested `R01EarlyStartup` defect returned in the previous cycle is closed. ON-NoPatch, ON-P01, and ON-P03 all passed strict retained side-B reconstruction. The strict seal then completed `deepLaunchVerificationCount=8` and sealed 33,792 immutable files. Bridge SHA-256 is `b6e97f573938757d712c632a765fb58b8cb82ff9e360733158de998f980a25e0`; seal SHA-256 is `5dc313824e9b034475a4d6f105b5d29801ef796f1553881d8b3b3699f9f65935`.

The first formal pair exposed the next subprocess boundary:

`R00 baseline: source pins differ from baseline provenance`

Pair `R00-OFF-NoPatch-formal-01` attempt 1 retained a passing protected side A and a candidate side B that failed before Player launch. Per protocol, Local explicitly repeated the entire A→B pair as attempt 2 using the identical bridge, seal, controls, order, and failed cumulative index. A passed again; B reproduced the byte-identical traceback and failure receipt. Neither attempt timed out or left a residual process.

### Direct cause

`run-h1-paired-performance.py` authenticates the bridge during admission and binds it into the attempt, but `build_command()` launches `run-r00-players.py` without any authenticated side authority. The launched tool has no bridge-aware internal input and immediately calls default `r00_player_inputs.verify_inputs()`. That current-pairing-only call rejects the retained `69130bbb...` candidate graph before output preparation or Player launch.

This is distinct from the repaired seal path:

- bridge creation: passed;
- retained ON early preflight: passed 3/3;
- strict pilot seal: passed 8/8;
- cached formal admission: passed and reached first side launch in about 14.746 seconds;
- protected formal side A: passed twice;
- candidate formal side B fresh preparation: failed twice before Player launch.

### Required correction

Add a fail-closed fresh formal side-B launch path that passes only the already authenticated same-bridge authority across the subprocess boundary. Preserve:

- default/direct `run-r00-players.py` current-pairing behavior;
- protected side A current pairing;
- no generic historical-pairing CLI override;
- exact bridge/seal binding per formal attempt;
- the same authority through nested Baseline/Control early preparation for ON modes;
- immutable graph/Player inputs and existing final-analyzer strict reconstruction.

Add a regression that executes the real formal command boundary (`build_command → run-r00-players → verify_inputs`) for retained candidate side B. Current unit tests proved admission and recording but did not execute this subprocess input-verification path.

After Primary publishes the correction, Local must restart fresh, create a new bridge/seal, and create a new formal batch. Preserve both failed pair attempts as historical evidence; do not relabel them.

## Independent closure completed

- V00 authority and both installed runtimes passed after the sanctioned candidate receipt refresh.
- Bounded Primary passed 353/353; all focused suites passed at expected counts.
- Full Python inventory recorded 1,010 passed and 28 explicit environment skips with no failures/errors.
- Broad Unity EditMode passed 1,076/1,076.
- Exact 9-path and 17-path source audits passed.
- Retained manifests, eight selected launches, and 33,792 bound files reauthenticated.
- New retained early preflight passed 3/3 in 1763.650 seconds.
- New strict seal passed 8/8 with stable guards.
- Formal pair 1 attempt 1 and explicit attempt 2 are both retained; A passed twice, B failed identically twice.

Evidence is retained at `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authoritya964-formal-launch-blocked/`.

Remaining formal pairs, final analysis, V05, and independent M08 were not run. H1 remains `InProgress`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. Do not begin R02.
