# R01B H1 — Current Primary Implementation

## Status

Latest Local return:

`144a26adf37bc0ecd5222499d328d1d1560910a0`

Current analysis/test source anchor:

`d239d9d00784ea2df22133cb8c938ec25035f5a0`

Previous analysis source anchor:

`7aa6f61994da354b04464e38ddfc8552cc5c3055`

Completed formal execution source:

`27df1a3d60811dc121f296ab561ae313a382b363`

H1 remains `InProgress`; `humanGatePassed=false`; `mayEnterR02=false`.

## Returned Local failure

V00.R and committed V00 passed on the repaired 7aa handoff. Bounded Primary passed 376/376.

Full Python discovery then ran 1,061 leaves and produced:

- 1,032 Passed;
- 28 environment-bound Skipped;
- 1 Failed.

The failed leaf was:

`test_h1_paired_performance.H1PairedPerformanceTests.test_analyze_sample_index_complete_positive`

Its synthetic raw-result fixture omitted top-level build GUID, baseline build ID, and runtime ABI hash. The corrected production analyzer correctly rejected that stale fixture.

Local demonstrated in memory that adding those three fields makes the positive case pass.

## Primary correction

### Synthetic fixture

`Tools/AssemblyShadow/tests/test_h1_paired_performance.py::raw()` now emits the authenticated top-level R00 build identity while retaining the nested receipt binding.

Production analyzer behavior is unchanged and remains fail-closed.

### Bounded suite

`Tools/AssemblyShadow/h1_bee_primary_tests.py` now explicitly loads the previously missed positive leaf.

Expected bounded leaf count: **377**.

### Historical successor v2

`H1HistoricalPerformanceReanalysis-v2` authenticates an exact seven-path source-27df → current analysis/test-only delta.

Relative to v1, the only added paths are:

- `Tools/AssemblyShadow/h1_bee_primary_tests.py`;
- `Tools/AssemblyShadow/tests/test_h1_paired_performance.py`.

No execution/runtime/measurement source is added.

### Retained graph v2

`H1V04RetainedGraphToolOnlySuccessor-v2` requires the exact prior 24-path retained-graph set plus the paired-performance test fixture, for **25 paths** total.

Historical v1 bridge/seal/formal-authority evidence is not relabelled.

## Source authority

The source anchor is frozen at:

`d239d9d00784ea2df22133cb8c938ec25035f5a0`

All later Primary commits in this cycle are metadata/handoff only.

`ProjectSettings/AssemblyShadowSourcePins.json` and `Docs/AssemblyShadow/Handoff/source-targets.json` point to this anchor.

## Primary evidence

No fresh GitHub Actions execution was visible for the new anchor.

Do not reuse old 376/376 as current validation.

Required Local empirical validation:

- bounded 377/377;
- full Python 1,061 leaves with zero failures/errors;
- exact 7-path and 25-path audits;
- completed source-27df live evidence reauthentication;
- historical compatibility v2;
- corrected historical analysis.

No Player rerun is required when those checks pass.

## Next Local cycle

Run:

1. final source preflight;
2. bounded 377;
3. full Python discovery;
4. exact source audits;
5. completed evidence reauthentication;
6. historical compatibility preflight v2;
7. historical strict analysis;
8. analysis-only checkpoint;
9. V05 / genuinely independent M08 if eligible.

Only genuine M08 PASS may make H1 Ready for Human Review Gate.

Do not begin R02.
