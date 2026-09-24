# Current Status

- Candidate analysis/test source anchor: `d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece`.
- Previous analysis/test source anchor: `d239d9d00784ea2df22133cb8c938ec25035f5a0`.
- Latest Local return: `57d51ac4b1d09eb190a7e95235a7ec6ff5ed1357`.
- Latest authenticated Local checkpoint: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authorityd239-compatibility-project-blocked/`.
- Completed formal execution source: `27df1a3d60811dc121f296ab561ae313a382b363`.
- Retained graph source: `69130bbb3a6df516916dddb5ad263799a7c6e5e3`.
- Historical compatibility policy: `H1HistoricalPerformanceReanalysis-v2` / exact 7 paths.
- Retained-graph policy: `H1V04RetainedGraphToolOnlySuccessor-v2` / exact 25 paths.
- Gate: `H1 / InProgress / AwaitingSplitCheckoutCompatibilityValidation`.
- Last independent M08: `FAIL` (historical; not rerun).
- Human gate passed: `false`.
- May enter R02: `false`.

## Latest Local result

The d239 v2 cycle passed every prerequisite before V04.AF:

- V00 source authority and exact seven/25-path audits;
- bounded Primary **377/377**;
- full Python discovery **1,033 Passed / 28 explicit Skipped / 0 Failed / 0 Error** across 1,061 leaves;
- source-27df checkpoint manifest **92/92**;
- all four fixed historical input SHA-256s;
- complete read-only reauthentication of **33,792/33,792 sealed live files**, 1,606,993,133 bytes, with zero unresolved content/stable-stat mismatches.

No Player was rerun.

V04.AF then failed before semantic bridge/seal/formal-authority analysis because the compatibility tool read current source pins from the historical bridge checkout. That checkout still pins `7aa6f619...`; the designated validation checkout pins `d239d9d0...`. The tool therefore saw the older five-path authority and reported the two v2 test paths missing.

This is a checkout-selection defect, not an evidence hash failure.

## Primary correction

The new source anchor is:

`d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece`

Only three existing v2 paths changed relative to d239:

- `Tools/AssemblyShadow/README.md`;
- `Tools/AssemblyShadow/h1_historical_reanalysis.py`;
- `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`.

Therefore the exact source-27df seven-path policy and retained-graph 25-path policy remain unchanged.

### Split source authority

`h1_historical_reanalysis.py` now requires:

`--analysis-project <current-validation-checkout>`

The designated analysis checkout is authenticated independently:

- canonical Git root;
- committed `ProjectSettings/AssemblyShadowSourcePins.json`;
- expected `night-outlook/hybridclr_demo` repository identity;
- demo `localPath=.`;
- complete non-metadata tree equals the pinned revision;
- running historical-reanalysis tool bytes equal the designated checkout's tool bytes.

The historical bridge's `projectRoot` remains historical evidence authority only.

### Strict historical analysis

Candidate-side historical R00 verification no longer treats the mutable historical evidence checkout as today's source authority.

The historical reanalysis tool locally reconstructs the immutable M07/R00 input graph using:

- historical graph source pins;
- historical source-27df pin DTO;
- original fixture/build/replay paths;
- immutable bridge-installed verification receipt.

Normal `r00_player_inputs.py`, `r00_results.py`, and `r01_early_results.py` are unchanged. The temporary historical-input callback is scoped to one candidate-side verification and is restored in `finally`.

### Regression coverage added

Four new bounded/full-Python leaves cover:

1. real split-checkout bridge verification using a detached stale historical worktree and the designated current analysis checkout;
2. rejection of a wrong committed current source pin;
3. direct routing of current source delta vs historical evidence roots through `authenticate_compatibility`;
4. candidate-side historical verifier override scope and restoration.

The split-checkout test also mutates historical build-map binding and requires fail-closed rejection.

Expected current counts:

- bounded Primary: **381**;
- complete Python: **1,065** leaves;
- if the same environment skip set remains: **1,037 Passed / 28 Skipped / 0 Failed / 0 Error**.

These are expectations only; fresh Local evidence is required.

## Immutable execution evidence

The source-27df execution evidence remains unchanged:

- 40/40 formal pairs Passed;
- 10 pairs per mode;
- zero formal retries.

Fixed hashes remain:

- bridge: `c03665dbdba797f5024fa8f376e6ac6aa6edf165c76387ddbf01ee6d3611826c`;
- seal: `bdc4062acfc6d208a9be50a142b897a07e7359e5df14ad3d3d8f2805c5179631`;
- formal batch: `97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667`;
- final sample index: `a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021`.

## Primary validation status

No GitHub Actions run was available for the new source commits in this Primary environment.

Current fresh empirical status is therefore:

- bounded 381: `NotRun`;
- full Python 1,065: `NotRun`;
- V04.AF split-checkout compatibility: `NotRun`;
- V04.AG strict analysis: `NotRun`;
- Unity/IL2CPP/Players: `NotRun` and should remain unnecessary if historical compatibility succeeds.

## Required next action

Local must run the complete repaired sequence in one cycle:

1. V00 source authority at the final pushed handoff HEAD;
2. bounded Primary 381/381;
3. complete Python discovery with zero failures/errors;
4. exact seven-path and 25-path audits;
5. complete source-27df live evidence reauthentication;
6. V04.AF using explicit `--analysis-project`;
7. V04.AG using the same explicit analysis checkout;
8. analysis-only checkpoint authentication;
9. V05;
10. genuinely independent M08 if eligible.

Do not rerun Players as a workaround.

H1 remains `InProgress`. Do not begin R02.
