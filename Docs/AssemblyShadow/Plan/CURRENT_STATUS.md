# Current Status

- Candidate analysis/test source anchor: `d239d9d00784ea2df22133cb8c938ec25035f5a0`.
- Previous analysis source anchor: `7aa6f61994da354b04464e38ddfc8552cc5c3055`.
- Latest Local return: `144a26adf37bc0ecd5222499d328d1d1560910a0`.
- Latest authenticated Local checkpoint: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority7aa6-python-fixture-blocked/`.
- Completed formal execution source: `27df1a3d60811dc121f296ab561ae313a382b363`.
- Retained graph source: `69130bbb3a6df516916dddb5ad263799a7c6e5e3`.
- Gate: `H1 / InProgress / AwaitingTestFixtureSuccessorValidation`.
- Last independent M08: `FAIL` (historical; not rerun).
- Human gate passed: `false`.
- May enter R02: `false`.

## Latest Local result

The repaired 7aa source-authority handoff passed:

- V00.R source-authority audit;
- committed V00 preflight;
- bounded Primary 376/376;
- historical checkpoint manifest 92/92;
- all four fixed live evidence hashes.

Complete Python discovery then ran 1,061 leaves:

- 1,032 Passed;
- 28 explicit environment Skipped;
- 1 Failed.

The failed leaf was `test_h1_paired_performance.H1PairedPerformanceTests.test_analyze_sample_index_complete_positive`.

The positive fixture omitted raw top-level `buildGuid`, `baselineBuildId`, and `runtimeAbiHash`. Local's in-memory diagnostic added those producer-required fields and reached `ComparabilityPassed`. No production analyzer failure was demonstrated.

Historical compatibility/reanalysis was not run. No Player was rerun.

## Primary correction

The new source anchor `d239d9d0...` contains a reviewed test-only successor.

### Fixture

`Tools/AssemblyShadow/tests/test_h1_paired_performance.py::raw()` now emits the three authenticated top-level R00 build-identity fields while retaining nested receipt path/SHA/build-GUID and matching optional nested baseline/runtime copies.

### Bounded regression

`Tools/AssemblyShadow/h1_bee_primary_tests.py` explicitly loads the previously missed positive leaf.

Expected bounded suite size: **377**.

### Historical-analysis policy

Current policy:

`H1HistoricalPerformanceReanalysis-v2`

Exact source-27df → current non-metadata set: **7 paths**.

The two v2 additions relative to v1 are:

- `Tools/AssemblyShadow/h1_bee_primary_tests.py`;
- `Tools/AssemblyShadow/tests/test_h1_paired_performance.py`.

No execution/runtime/measurement source is added.

### Retained-graph policy

Current policy:

`H1V04RetainedGraphToolOnlySuccessor-v2`

Exact retained 69130 → current non-metadata set: **25 paths**.

The only v2-added unique path is:

`Tools/AssemblyShadow/tests/test_h1_paired_performance.py`

Historical source-27df v1 bridge/formal-authority evidence remains v1 and is authenticated as such.

## Immutable execution evidence

The source-27df series remains unchanged:

- 40/40 formal pairs Passed;
- 10 pairs per mode;
- zero formal retries.

Fixed hashes:

- bridge: `c03665dbdba797f5024fa8f376e6ac6aa6edf165c76387ddbf01ee6d3611826c`;
- seal: `bdc4062acfc6d208a9be50a142b897a07e7359e5df14ad3d3d8f2805c5179631`;
- formal batch: `97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667`;
- final sample: `a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021`.

## Primary validation status

No fresh GitHub Actions run was visible for `d239d9d0...`.

Therefore:

- prior 376/376 remains historical evidence for the previous source;
- current bounded 377/377 is **NotRun** in Primary;
- current full Python 1,061-leaf discovery is **NotRun** in Primary;
- Unity/IL2CPP/Players are **NotRun** and must remain unneeded for this analysis/test-only successor if compatibility passes.

## Required next action

Local must run, in order:

1. V00 source authority at the final pushed handoff HEAD;
2. bounded Primary, requiring 377/377;
3. complete Python discovery, requiring zero failures/errors;
4. exact 7-path historical-analysis audit;
5. exact 25-path retained-graph audit;
6. complete source-27df live evidence reauthentication;
7. `H1HistoricalPerformanceReanalysis-v2` preflight;
8. corrected historical analysis;
9. analysis-only checkpoint;
10. V05 and genuinely independent M08 if eligible.

Do not rerun Players as a workaround for an analysis/test defect.

H1 remains `InProgress`. Do not begin R02.
