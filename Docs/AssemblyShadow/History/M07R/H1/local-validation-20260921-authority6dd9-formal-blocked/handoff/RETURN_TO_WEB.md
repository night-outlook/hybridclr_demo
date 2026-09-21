# Local Validation → Primary Implementation

## Current blocker: nested early-capsule verification drops the authenticated graph-reuse authority

Fresh Local Validation at checkout `1c6cdda260e2bf91e07e672aa261dcc38b3a5aa8`, source/tool anchor `6dd964c045034240ea53dd15ba7c0b33e9f2ad17`, passed current and protected authority, the exact 14-path source audit, retained artifact reauthentication, and creation of the real side-B `H1GraphReuseBridge`.

The bridge-bound strict pilot seal then failed after approximately 1104.2 seconds with:

`R00 baseline: source pins differ from baseline provenance`

No `H1PilotVerificationReceipt`, formal output root, formal Player launch, or residual formal attempt exists.

### Direct and root cause

The direct failure occurs during strict R00 reconstruction of a retained candidate ON pilot that uses `R01EarlyStartup`. The graph bridge and retained inputs are valid.

The root cause is an incomplete authority propagation path:

1. `run-h1-paired-performance.py` selects the bridge authority only for candidate side B.
2. `_verify_prior_launch` passes it to `r00_results.verify_suite`.
3. `r00_results.verify_suite` correctly uses `verify_inputs_with_reuse` for its outer graph validation.
4. The same verifier then calls `r01_early_results._prepare` to reconstruct the early capsule.
5. `_prepare` unconditionally calls default `r00_player_inputs.verify_inputs`, dropping the authenticated reuse authority and reapplying current-pairing equality to the retained `69130bbb...` graph.

A focused read-only reproduction recorded `outerReuseVerification=Passed` followed by `nestedEarlyPrepare=FailedAsObserved` with the exact seal error. This is an admission-path defect, not bridge corruption, artifact drift, a Player result failure, or an operational timeout.

### Required correction

Propagate the already authenticated, side-scoped pairing authority through strict early-startup preparation and capsule reconstruction. Preserve these invariants:

- default `r00_player_inputs.require_current_pairing` remains unchanged and fail-closed;
- authority remains optional and bridge-authenticated;
- retained authority applies only to candidate side B;
- protected side A remains on default current pairing;
- capsule inputs, baseline/Native ON/OFF/replay pins, bridge, seal, and final analyzer remain independently bound;
- no caller can introduce a different authority below the bridge/seal boundary.

Add a regression using the real `69130bbb... → 6dd964c0...` transition and an ON pilot launch with `R01EarlyStartup`, so it crosses the nested `_prepare` boundary that failed locally. The existing outer bridge regression is insufficient.

After Primary publishes the correction, Local must restart from fresh V00, independently re-audit the new source delta, create a new bridge, and create a new strict seal. Do not reuse or relabel this failed seal attempt.

## Independent closure completed

- V00 candidate/reproduction/protected authority passed; candidate installed receipt was refreshed and reverified.
- Bounded Primary passed 348/348.
- Direct graph, paired-driver, formal-batch, R01, lazy, and PowerShell recovery suites passed, with the initial direct formal import failure retained separately.
- Complete Python inventory recorded 1,005 passed and 28 explicit environment skips, with no failures/errors.
- Broad Unity EditMode passed 1,076/1,076.
- Both exact 14-path source audits passed.
- Retained checkpoint, Player artifacts, controls, pilot history, eight selected launches, and 33,784 bound files reauthenticated.
- The real bridge passed and is retained with SHA-256 `088a338632a9d2a9970c0bc61aaa9b218b4ca93e080a1734539b68317fa1a89e`.

Evidence is retained at `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6dd9-formal-blocked/`.

Formal pairs and final analysis were not started. V05/M08 remain ineligible. H1 remains `InProgress`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. Do not begin R02.
