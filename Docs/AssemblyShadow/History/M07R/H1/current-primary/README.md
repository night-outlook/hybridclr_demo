# R01B H1 — Current Primary Implementation

## Status

Latest Local return:

`ff3d352ee9a7c373e21bc06d714fff647354bb09`

Candidate source/tool anchor:

`7aa6f61994da354b04464e38ddfc8552cc5c3055`

Completed formal execution source:

`27df1a3d60811dc121f296ab561ae313a382b363`

H1 remains `InProgress`; `humanGatePassed=false`; `mayEnterR02=false`.

## Local result received

The source-27df formal run is complete:

- bridge: Passed;
- retained-pilot admission: Passed;
- guard-v2 8-side seal: Passed;
- formal batch: **40/40 Passed, zero retries**;
- build-map comparability: Passed;
- chronology: Passed.

Final analysis returned Incomplete because the analyzer required two duplicate identity fields in a nested summary that the R00 producer never emitted.

The raw top-level build identity is correct and already verified by R00.

## Primary design decision

Do not mutate the producer and do not rerun 40 Players.

Correct the analyzer to match the existing authenticated producer contract.

Then reanalyze the exact immutable 27df evidence only through a fixed historical-analysis compatibility policy.

## Corrected R00 build binding

Required against the frozen M07 receipt:

### Raw result top level

- `buildGuid`;
- `baselineBuildId`;
- `runtimeAbiHash`.

### Nested playerBuildReceipt

Required:

- path;
- SHA-256;
- build GUID.

Optional:

- baseline build ID;
- runtime ABI hash.

If optional nested copies exist, they must match.

## Historical reanalysis compatibility

New:

`Tools/AssemblyShadow/h1_historical_reanalysis.py`

Policy:

`H1HistoricalPerformanceReanalysis-v1`

It is fixed to:

- historical source `27df1a3d...`;
- historical checkout `f5e34235...`;
- retained graph `69130bbb...`;
- exact old bridge;
- exact old guard-v2 seal;
- exact 40/40 batch receipt;
- exact final cumulative index.

It authenticates all historical tool hashes from Git rather than accepting current-tool substitutions.

The exact current delta contains only five analysis files.

No execution authority is granted.

## Regression coverage

Tests now cover:

- the actual Local failure diagnosis;
- real producer-shaped raw build receipt;
- missing/wrong top-level build identity rejection;
- conflicting optional nested identity rejection;
- exact five-file Git analysis delta;
- historical bridge reconstruction from Git;
- exact historical seal verifier inventory;
- fixed checkpoint bridge/seal/batch/final-index SHA-256s;
- synthetic 4-pilot + 40-formal authority chain;
- retained-pilot vs current-formal runner split;
- formal batch 40/40 binding and unsuccessful-run rejection.

## Primary validation

Workflow `35942350651` passed bounded **376/376** and all live handoff/R01/M07 recovery/lazy suites.

## Next Local cycle

No Player execution.

Run:

1. current source/Python and exact analysis-only audit;
2. checkpoint/live evidence reauthentication;
3. `h1_historical_reanalysis.py --preflight-only`;
4. full `h1_historical_reanalysis.py`;
5. analysis-only checkpoint;
6. V05 / independent M08 if the result is Passed.

Expected final analysis:

- `result=Passed`;
- `status=ComparabilityPassed`;
- 10 formal pairs/mode;
- 1 valid pilot/mode;
- complete startup and chronology;
- one retained historical failed pilot attempt remains invalid and non-selected.

Do not rerun formal Players unless compatibility fails because of a genuine non-analysis source/evidence mismatch.

Do not begin R02.
