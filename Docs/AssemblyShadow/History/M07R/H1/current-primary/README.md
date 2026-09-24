# R01B H1 — Current Primary Implementation

## Status

Latest Local return:

`57d51ac4b1d09eb190a7e95235a7ec6ff5ed1357`

Current analysis/test source anchor:

`d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece`

Completed formal execution source:

`27df1a3d60811dc121f296ab561ae313a382b363`

H1 remains `InProgress`; historical M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

## Returned Local result

The d239 cycle passed source authority, bounded 377/377, full Python with zero failures/errors, exact seven/25-path audits, the source-27df manifest, all four fixed hashes, and complete read-only sealed-live authentication.

V04.AF failed because current source authority was read from the historical bridge checkout instead of the designated validation checkout.

No Player was rerun.

## Primary design decision

Historical evidence location and current analysis source authority are independent concepts.

Do not move or rewrite historical evidence and do not update the historical owner checkout merely to satisfy current source verification.

Current authority must come from an explicitly designated current validation checkout.

## Implementation

`h1_historical_reanalysis.py` now requires:

`--analysis-project <current-validation-checkout>`

It independently authenticates that checkout and uses it for the v2 source delta.

Historical bridge/seal/batch/sample/formal-authority verification continues to use the original historical paths.

For strict candidate-side R00 reanalysis, the tool supplies a historical-input adapter that reconstructs the immutable historical M07/R00 input graph without consulting the historical checkout's current source pin. Shared runtime verification modules are not changed and their normal functions are restored after the callback.

## Policies

Unchanged:

- `H1HistoricalPerformanceReanalysis-v2`: exact 7 paths;
- `H1V04RetainedGraphToolOnlySuccessor-v2`: exact 25 paths.

Relative to d239, only three already-allowed paths changed:

- `Tools/AssemblyShadow/README.md`;
- `Tools/AssemblyShadow/h1_historical_reanalysis.py`;
- `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`.

## Regression coverage

Four new leaves cover:

- real split checkout with stale historical worktree + current analysis checkout;
- wrong committed current source pin rejection;
- compatibility root-routing contract;
- strict candidate-side historical verifier override scope/restoration.

The split-checkout test also mutates historical build-map binding and requires rejection.

Expected counts:

- bounded: **381**;
- full Python: **1,065**;
- expected under unchanged environment skips: **1,037 Passed / 28 Skipped / 0 Failed/Error**.

Fresh Local evidence is required.

## Next Local cycle

Run the complete chain in one cycle:

1. V00 source authority;
2. bounded 381;
3. full Python 1,065;
4. exact source audits;
5. complete live historical reauthentication;
6. V04.AF with explicit `--analysis-project`;
7. V04.AG with the same analysis checkout;
8. analysis-only checkpoint;
9. V05;
10. genuinely independent M08 if eligible.

Do not rerun Players as a workaround.

Do not begin R02.
