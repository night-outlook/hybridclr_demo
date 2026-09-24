# Local Validation Tasks — Authenticated Historical Final Reanalysis

Candidate analysis source/tool anchor:

`7aa6f61994da354b04464e38ddfc8552cc5c3055`

Latest Local return:

`ff3d352ee9a7c373e21bc06d714fff647354bb09`

Completed formal-execution source:

`27df1a3d60811dc121f296ab561ae313a382b363`

Historical checkout that finalized that source family:

`f5e34235641c212c715aef3405925ddd4cf28ee6`

Authenticated blocked checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260923-authority27df-formal-analysis-blocked/`

H1 remains `InProgress`. Do not begin R02.

## Goal

Close the final analyzer-only contract defect without rerunning Players:

fresh current source/Python → exact analysis-only source audit → reauthenticate the completed 27df checkpoint/live evidence → historical compatibility preflight → corrected historical analysis → analysis-only checkpoint → V05 / genuinely independent M08 if eligible.

The completed 40/40 formal series is immutable execution evidence. Do not create a new bridge, seal, Player, pilot, formal pair, or retry unless the compatibility proof fails because of a genuine non-analysis evidence problem and the task returns to Primary.

## V00.R — source-authority repair prerequisite

Before the existing V00 sequence, authenticate the final pushed checkout after Primary's source-authority repair:

1. require branch `codex/assembly-shadow-r01b-h1` and the final handoff HEAD;
2. verify these nine paths are byte-identical to `7aa6f61994da354b04464e38ddfc8552cc5c3055`:
   - `.agents/skills/agent-collaboration/SKILL.md`
   - `.agents/skills/agent-collaboration/scripts/Get-GateReviewMode.ps1`
   - `.agents/skills/agent-collaboration/tests/Test-AgentCollaborationGatePolicy.Tests.ps1`
   - `.codex/agents/code-debugger.toml`
   - `.codex/agents/code-explorer.toml`
   - `.codex/agents/code-gate-reviewer.toml`
   - `.codex/agents/code-general.toml`
   - `.codex/agents/code-reviewer.toml`
   - `.codex/agents/code-worker.toml`
3. require the complete `7aa6f619... → HEAD` non-metadata delta, under the unchanged `shadow_tools.metadata_only` policy, to be empty;
4. require the complete `27df1a3d... → HEAD` non-metadata delta to remain exactly the existing five analysis-only paths;
5. do not alter metadata classification, source pins, or the historical-analysis allowlist locally.

Then run the committed `h1_handoff_preflight.py` V00 step. If any of the above fails, stop and return to Primary before bounded tests or historical evidence work.

## V00 — current analysis authority

1. Pull final pushed `codex/assembly-shadow-r01b-h1`.
2. Require clean tracked state.
3. Record checkout HEAD separately from analysis source anchor `7aa6f61994da354b04464e38ddfc8552cc5c3055`.
4. Run current committed handoff/source preflight and require `SourceTargetVerifiedNotBuildAccepted`.
5. Run complete current bounded Primary regression.
6. Run complete Python discovery.

Require:

- zero Python failures/errors;
- environment skips explicit;
- full logs retained.

### No runtime rebuild / Unity execution

Do **not** run:

- candidate install-repeatability refresh;
- Player builds;
- Unity Play/Player validation;
- formal sampling;
- bridge/seal creation.

Reason: the successor is analysis-only and historical compatibility must not mutate the completed execution evidence.

Classify prior runtime/Unity evidence only after the source audit:

- candidate/protected runtime evidence: `ReusedAuditedFromFF3D`;
- Unity EditMode 1076/1076: `ReusedAuditedFromD18`;
- completed source-27df formal execution: `HistoricalExecutionAuthenticatedFromFF3D`.

Do not label any of these as fresh execution at the new analyzer source.

## V01 — exact source audits

### A. Historical execution source → current analysis source

Compare:

`27df1a3d60811dc121f296ab561ae313a382b363`

to:

`7aa6f61994da354b04464e38ddfc8552cc5c3055`

After repository metadata-only classification, the exact non-metadata set must equal **five paths**:

1. `Tools/AssemblyShadow/README.md`
2. `Tools/AssemblyShadow/h1_graph_reuse.py`
3. `Tools/AssemblyShadow/h1_historical_reanalysis.py`
4. `Tools/AssemblyShadow/h1_paired_performance.py`
5. `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`

Require **no** delta in:

- `run-r00-players.py`;
- `r00_results.py`;
- `r00_player_inputs.py`;
- `r01_early_results.py`;
- paired/formal execution runner;
- pilot sealer;
- measurement source;
- protocol/schedule;
- build-map/graph producer;
- Unity/runtime/native/Player source.

A subset or superset fails historical compatibility.

### B. Retained graph anchor → current analysis source

Compare:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3`

to:

`7aa6f61994da354b04464e38ddfc8552cc5c3055`

Require equality to the exact **24-path** retained-graph tooling allowlist in:

`Docs/AssemblyShadow/Handoff/source-targets.json`

Do not edit either allowlist locally.

## V02 — reauthenticate the completed 27df evidence

Authenticate the checkpoint:

`local-validation-20260923-authority27df-formal-analysis-blocked`

Require its `MANIFEST.sha256` to pass.

The following exact evidence identities are mandatory:

- graph bridge:
  `c03665dbdba797f5024fa8f376e6ac6aa6edf165c76387ddbf01ee6d3611826c`;
- guard-v2 pilot seal:
  `bdc4062acfc6d208a9be50a142b897a07e7359e5df14ad3d3d8f2805c5179631`;
- formal batch:
  `97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667`;
- final cumulative sample index:
  `a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021`.

Also require:

- formal batch status `PassedAllFormalPairs`;
- 40/40 formal pairs;
- zero formal retries;
- all referenced live launch/raw/result/authority/build evidence remains available and hash-identical.

Use the **original live paths recorded in the historical receipts** for compatibility/reanalysis. Do not substitute checkpoint-copy paths whose filenames differ from the authenticated bindings.

If required live evidence is missing, do not manually rewrite receipts or relocate paths. Retain the failure and return to Primary.

## V04.AF — historical compatibility preflight

Run:

~~~text
python3 Tools/AssemblyShadow/h1_historical_reanalysis.py \
  --sample-index <27df-live-final-sample-index.json> \
  --pilot-verification-receipt <27df-live-pilot-verification.json> \
  --graph-reuse-bridge <27df-live-graph-reuse-bridge.json> \
  --formal-batch <27df-live-formal-batch.json> \
  --output <new-historical-analysis-compatibility.json> \
  --preflight-only
~~~

Require:

- `schemaVersion=1`;
- `kind=H1HistoricalAnalysisCompatibility`;
- `status=AuthenticatedAnalysisOnlySuccessor`;
- `policyId=H1HistoricalPerformanceReanalysis-v1`.

### Fixed evidence identities

Require `authenticatedEvidenceSha256` exactly:

- bridge: `c03665db...`;
- seal: `bdc4062a...`;
- final sample: `a8e519c3...`;
- formal batch: `97ddb6c8...`.

### Analysis delta

Require:

- historical source = `27df1a3d...`;
- historical checkout = `f5e34235...`;
- current source = `7aa6f61994da354b04464e38ddfc8552cc5c3055`;
- exact five-path analysis-only delta.

### Historical bridge/seal

Require:

- retained graph = `69130bbb...`;
- historical bridge transition 69130 → 27df authenticates from Git;
- historical bridge verifier hashes match Git 27df;
- historical guard-v2 seal verifier inventory matches Git 27df;
- guard-v2 seal still records 8 deep launch verifications;
- retained pilot runner provenance remains exact.

### Completed formal batch/sample

Require:

- historical formal batch = 40/40 Passed;
- final sample binding equals the fixed final index;
- bridge/seal/protocol/schedule/map bindings exact;
- historical sample attempt count = **45**;
- historical formal attempt count = **40**;
- pilot rows use retained historical runner;
- formal rows use source-27df current runner;
- all candidate-B formal authorities bind exact pair/attempt/mode/order/project/input/bridge/seal/tool identity;
- protected A carries no retained authority.

The compatibility preflight must not launch Players or mutate historical evidence.

If this fails, **do not rerun Players**. Return the exact incompatibility to Primary.

## V04.AG — corrected historical strict analysis

Only after V04.AF passes:

~~~text
python3 Tools/AssemblyShadow/h1_historical_reanalysis.py \
  --sample-index <27df-live-final-sample-index.json> \
  --pilot-verification-receipt <27df-live-pilot-verification.json> \
  --graph-reuse-bridge <27df-live-graph-reuse-bridge.json> \
  --formal-batch <27df-live-formal-batch.json> \
  --output <new-historical-performance-analysis.json>
~~~

Require top-level result:

- `kind=H1ControlledPairedPerformanceSummary`;
- `result=Passed`;
- `status=ComparabilityPassed`.

Require embedded:

`historicalAnalysisCompatibility.status=AuthenticatedAnalysisOnlySuccessor`

with the exact same fixed evidence hashes and five-path delta as preflight.

### Sampling requirements

Require:

- formal pairs per mode:
  - OFF-NoPatch = 10;
  - ON-NoPatch = 10;
  - ON-P01 = 10;
  - ON-P03 = 10;
- pilot pairs per mode = 1 each;
- formal startup observations per mode = 10 each;
- `formalComplete=true`;
- `pilotsComplete=true`;
- `startupComplete=true`;
- `chronologyComplete=true`;
- `globalIntervalsResolved=true`;
- `globalIntervalsNonOverlapping=true`;
- `pilotsBeforeFormalByTimestamp=true`.

### Attempt retention

Require exactly 45 attempt records:

- 44 valid selected/analyzable attempts;
- 1 invalid historical pilot attempt:
  `R00-ON-NoPatch-pilot-01` attempt 1;
- later Passed pilot attempt is the selected pilot for that mode;
- no formal attempt becomes invalid.

Do not delete or relabel the historical failed pilot.

### Build binding

For every selected raw R00 result require:

- top-level build GUID/baseline/runtime ABI equals frozen build;
- nested `playerBuildReceipt` path/SHA/build GUID equals frozen build;
- absent nested baseline/runtime is accepted;
- any present nested duplicate must agree.

### Statistics

Require every mode summary to report `formalPairCount=10`.

Retain all paired operation/memory/startup statistics exactly as produced. Do not interpret or suppress an unfavorable measured result.

If analysis is not Passed, retain the entire output and return to Primary. Do **not** rerun formal Players to work around another analyzer/tool defect.

## V04.AH — analysis-only checkpoint

After V04.AG passes, create/authenticate a new checkpoint that includes:

- current source/Python validation;
- exact five-path and 24-path audits;
- original source-27df checkpoint manifest reference;
- compatibility preflight;
- corrected historical analysis;
- exact four historical evidence SHA-256s;
- explicit classification that no new Player execution occurred;
- all prior failure/blocked checkpoint references.

Authenticate the checkpoint manifest before any cleanup.

The source-27df execution checkpoint remains immutable historical evidence; the new checkpoint adds analysis closure rather than replacing it.

## V05 / independent M08

If and only if V04 historical reanalysis is Passed/ComparabilityPassed:

1. prepare the existing V05 successor evidence using the completed V04 execution + analysis closure;
2. prepare a fresh independent-M08 review package;
3. if the Local environment has an established genuinely independent reviewer mechanism, execute it in a separate context/agent;
4. otherwise return `ReadyForIndependentM08` with the package rather than self-declaring an independent PASS.

M08 must explicitly review:

- real R00 producer vs analyzer field contract;
- fixed-source historical compatibility policy;
- exact evidence hashes;
- five-file analysis-only delta;
- historical bridge/seal/formal-authority Git verification;
- one failed pilot retained/non-selected;
- 40/40 formal execution and corrected statistical result;
- no Player rerun after analyzer fix.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**.

Stop for explicit human approval.

**Do not begin R02.**

## Failure evidence

On compatibility failure retain:

- current source/checkout;
- exact Git delta;
- fixed historical input hashes;
- first failing bridge/seal/batch/sample/formal-authority binding;
- stdout/stderr;
- proof no Player process launched.

On analysis failure retain:

- compatibility preflight;
- corrected analysis output;
- first invalid attempt/side/raw field;
- relevant raw result and frozen build receipt bindings.

## Local correction boundary

Local may adjust only:

- absolute paths to the already authenticated live historical evidence;
- new output/checkpoint roots;
- permissions/PYTHONPATH;
- bounded invocation syntax.

Local must not:

- rewrite historical receipts;
- substitute copied paths for bound live paths;
- broaden the five-file compatibility delta;
- change fixed historical hashes/source revisions;
- rerun Players/bridges/seals/formal pairs;
- alter analyzer semantics;
- modify protocol/schedule/map/statistics;
- claim independent M08 without an independent mechanism.

Any non-trivial source/tool correction returns to Primary.
