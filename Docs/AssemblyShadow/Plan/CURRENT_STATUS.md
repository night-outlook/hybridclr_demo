# Current Status

- Candidate build-input/tool source anchor: `7aa6f61994da354b04464e38ddfc8552cc5c3055`.
- Latest Local return: `ff3d352ee9a7c373e21bc06d714fff647354bb09`.
- Latest authenticated Local checkpoint: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260923-authority27df-formal-analysis-blocked/`.
- Completed formal execution source: `27df1a3d60811dc121f296ab561ae313a382b363`.
- Gate: `H1 / InProgress / AwaitingHistoricalFinalReanalysis`.
- Last independent M08: `FAIL` (historical; not rerun).
- Human gate passed: `false`.
- May enter R02: `false`.

## Latest Local result

The source-27df Local cycle completed the mandatory formal execution chain:

- current/protected authority and Python validation passed;
- exact 3-path / 22-path source audits passed;
- retained graph/pilot evidence reauthenticated;
- new graph bridge passed;
- retained-pilot admission passed;
- guard-v2 strict pilot seal passed 8/8;
- path-hash output namespace avoided preserved-output collisions;
- formal side-B current authority path passed;
- **all 40 formal pairs passed on first attempt**:
  - 10 OFF-NoPatch;
  - 10 ON-NoPatch;
  - 10 ON-P01;
  - 10 ON-P03;
  - zero formal retries.

Authenticated completed-series hashes:

- graph bridge: `c03665dbdba797f5024fa8f376e6ac6aa6edf165c76387ddbf01ee6d3611826c`;
- guard-v2 seal: `bdc4062acfc6d208a9be50a142b897a07e7359e5df14ad3d3d8f2805c5179631`;
- formal batch: `97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667`;
- final sample index: `a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021`.

Final analysis alone returned `Incomplete / ComparabilityIncomplete`.

44 otherwise analyzable pilot/formal attempts failed the same analyzer-only contract check:

`R00 raw build field differs: baselineBuildId`

The remaining invalid attempt is the intentionally retained historical pilot attempt whose A runner process group could not be proven gone and whose B side was skipped.

## Root cause

The real R00 producer contract is:

- raw top-level:
  - `buildGuid`;
  - `baselineBuildId`;
  - `runtimeAbiHash`;
- nested `playerBuildReceipt`:
  - receipt path;
  - receipt SHA-256;
  - build GUID;
  - other receipt summary fields;
  - no required duplicate baseline/runtime identities.

`r00_results.verify_result` already validates the top-level identities against the authenticated graph/build context.

The paired analyzer incorrectly required `baselineBuildId` and `runtimeAbiHash` again inside the nested receipt summary.

No Player/runtime measurement failed.

## Primary correction

### Correct analyzer contract

`h1_paired_performance._check_build_binding` now:

1. requires nested receipt path/SHA to bind the frozen M07 receipt;
2. requires raw top-level `buildGuid`, `baselineBuildId`, and `runtimeAbiHash` to equal the frozen receipt;
3. requires nested `buildGuid` to agree;
4. treats nested baseline/runtime as optional duplicates;
5. if those optional nested fields exist, requires them to agree.

Wrong or missing top-level build identity remains fail-closed.

### Decision — reuse the immutable 40/40 series

The completed source-27df series **does not need to be rerun**.

It may be reanalyzed only through fixed policy:

`H1HistoricalPerformanceReanalysis-v1`

The compatibility path is source- and evidence-specific:

- historical execution source:
  `27df1a3d60811dc121f296ab561ae313a382b363`;
- historical checkout:
  `f5e34235641c212c715aef3405925ddd4cf28ee6`;
- fixed bridge/seal/batch/final-index SHA-256s listed above;
- retained graph:
  `69130bbb3a6df516916dddb5ad263799a7c6e5e3`.

### Exact analysis-only successor

`27df1a3d... → 7aa6f619...` contains exactly five non-metadata paths:

1. `Tools/AssemblyShadow/README.md`
2. `Tools/AssemblyShadow/h1_graph_reuse.py`
3. `Tools/AssemblyShadow/h1_historical_reanalysis.py`
4. `Tools/AssemblyShadow/h1_paired_performance.py`
5. `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`

No runner, R00 input/results verifier, measurement source, protocol, schedule, graph/map producer, Player/native/runtime source changed.

The retained-graph allowlist now contains 24 paths.

### Historical compatibility proof

Before analysis, the new tool verifies:

- exact completed bridge/seal/batch/final-index hashes;
- historical source-pin bytes and bridge transition from Git;
- exact historical bridge verifier hashes;
- exact historical guard-v2 seal verifier inventory;
- all retained pilot runner bindings;
- all 40 formal current-runner and formal-authority bindings;
- protected A authority isolation;
- candidate B launch authority echoes;
- exact five-file current analysis-only Git delta.

The path grants analysis only. It cannot authorize historical Player execution or bridge reuse.

## Primary validation

Authority-updated workflow `35942350651` at `4c368bdb...` passed:

- bounded Primary: **376/376**;
- live handoff: **11/11**;
- R01 early capsule: **7/7**;
- R01 early launch: **20/20**;
- R01 early results: **20/20**;
- failure pipeline: **16/16**;
- both M07 PowerShell recovery regressions: Passed;
- R01B lazy: **10/10**.

Artifact `10784819521`, SHA-256 `9df947a5443d24f8f4d1a8cc71b1f440f3894f357a84824aa47ea65023c7f51b`.

## Required next action

Local should **not rerun Players**.

It must:

1. validate current source/Python and exact five-file analysis-only delta;
2. reauthenticate the completed source-27df checkpoint and live immutable evidence;
3. run historical compatibility preflight with the exact old bridge, seal, formal batch, and final sample index;
4. if preflight passes, run corrected historical reanalysis on the same 40/40 series;
5. require `Passed / ComparabilityPassed`, 10 formal pairs/mode, 1 valid pilot/mode, complete startup/chronology, while retaining the one old failed pilot attempt as invalid/non-selected;
6. checkpoint the analysis-only closure;
7. proceed directly to V05 / genuinely independent M08 if eligible.

H1 remains `InProgress`. Do not begin R02.
