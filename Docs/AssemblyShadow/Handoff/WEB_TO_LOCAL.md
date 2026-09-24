# Primary Implementation → Local Validation

## Objective

Authenticate and reanalyze the already-completed source-27df 40/40 formal series under the corrected final-analysis contract at current analysis source:

`7aa6f61994da354b04464e38ddfc8552cc5c3055`

No Player, bridge, seal, pilot, or formal pair should be rerun if historical compatibility passes.

Latest Local return:

`c3fe9620f9f6b494184b8ff76cbb377757591585`

H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

**Do not begin R02.**

## Current Primary source-authority repair

Local V00 correctly rejected the prior pushed checkout because nine repository agent-configuration files had changed after analysis source anchor `7aa6f61994da354b04464e38ddfc8552cc5c3055`.

Primary resolved this by restoring those nine files to their exact `7aa6f619` Git blobs:

- `.agents/skills/agent-collaboration/SKILL.md`
- `.agents/skills/agent-collaboration/scripts/Get-GateReviewMode.ps1`
- `.agents/skills/agent-collaboration/tests/Test-AgentCollaborationGatePolicy.Tests.ps1`
- `.codex/agents/code-debugger.toml`
- `.codex/agents/code-explorer.toml`
- `.codex/agents/code-gate-reviewer.toml`
- `.codex/agents/code-general.toml`
- `.codex/agents/code-reviewer.toml`
- `.codex/agents/code-worker.toml`

No verifier policy was weakened:

- `shadow_tools.metadata_only` is unchanged;
- `.agents/` and `.codex/` are not broadly reclassified as metadata;
- analysis source anchor remains `7aa6f619...`;
- `H1HistoricalPerformanceReanalysis-v1` remains the exact five-file analysis-only successor;
- the source-27df formal evidence and fixed four evidence hashes remain untouched.

Connector transport readiness was also proven independently on disposable branch `codex/connector-smoke-primary-20260923-a` in all four repositories. Exact smoke commits are recorded in `source-targets.json`. The smoke branches remain only because the current Connector exposes no branch-delete operation; they are not product evidence or handoff authority.

Local must rerun V00 from the final pushed handoff HEAD. The checkout may be later than `7aa6f619` only by paths already classified as repository metadata. The complete non-metadata tree must equal the source anchor before historical compatibility or reanalysis may continue.

## Source targets

Machine authority:

`Docs/AssemblyShadow/Handoff/source-targets.json`

Candidate/current analysis identities:

| Repository | Branch | Identity |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | analysis source/tool anchor `7aa6f61994da354b04464e38ddfc8552cc5c3055` |
| `night-outlook/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| `night-outlook/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| `night-outlook/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |

Completed formal execution source:

`27df1a3d60811dc121f296ab561ae313a382b363`

Historical checkout finalizing that source family:

`f5e34235641c212c715aef3405925ddd4cf28ee6`

Retained graph source:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3`

Authenticated completed-series checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260923-authority27df-formal-analysis-blocked/`

Authority-updated Primary validation:

- workflow `35942350651`;
- commit `4c368bdb01cf8e56573daaa15a828da25abea6b3`;
- bounded Primary **376/376**;
- live handoff **11/11**;
- R01 early capsule **7/7**;
- R01 early launch **20/20**;
- R01 early results **20/20**;
- R01 failure pipeline **16/16**;
- both M07 PowerShell recovery regressions Passed;
- R01B lazy **10/10**;
- artifact `10784819521`;
- artifact SHA-256 `9df947a5443d24f8f4d1a8cc71b1f440f3894f357a84824aa47ea65023c7f51b`.

This is Primary source/tool evidence only.

## Implementation

### Returned Local result

The source-27df V04 runtime/performance execution is complete.

Local passed:

- current/protected authority;
- exact source audits;
- retained evidence authentication;
- graph bridge;
- retained-pilot admission;
- guard-v2 strict seal;
- formal side-B authority/current runner;
- collision-resistant batch execution;
- **all 40 formal pairs on first attempt**.

Formal counts:

- OFF-NoPatch: 10/10;
- ON-NoPatch: 10/10;
- ON-P01: 10/10;
- ON-P03: 10/10;
- retries: 0.

Fixed historical evidence:

- graph bridge SHA-256:
  `c03665dbdba797f5024fa8f376e6ac6aa6edf165c76387ddbf01ee6d3611826c`;
- guard-v2 seal SHA-256:
  `bdc4062acfc6d208a9be50a142b897a07e7359e5df14ad3d3d8f2805c5179631`;
- formal batch SHA-256:
  `97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667`;
- final sample index SHA-256:
  `a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021`.

Final analysis alone returned `Incomplete / ComparabilityIncomplete`.

### Root cause

The R00 producer emits authenticated build identity at raw-result top level:

- `buildGuid`;
- `baselineBuildId`;
- `runtimeAbiHash`.

The nested `playerBuildReceipt` binds:

- frozen receipt path;
- receipt SHA-256;
- build GUID.

It does not require duplicate nested baseline/runtime fields.

The analyzer incorrectly required those two duplicate nested fields.

This affected 44 otherwise analyzable attempts identically.

The remaining invalid attempt is the historical failed ON-NoPatch pilot attempt 1; its later Passed retry remains the valid selected pilot.

### Corrected analyzer contract

`h1_paired_performance._check_build_binding` now:

1. binds nested receipt path/SHA to the frozen build;
2. requires top-level build GUID/baseline/runtime ABI to match the frozen build;
3. requires nested build GUID to match;
4. accepts absent nested baseline/runtime duplicates;
5. rejects conflicting optional nested duplicates.

Missing/wrong top-level identity remains fail-closed.

### Decision — do not rerun 40 Players

The immutable 40/40 series is eligible for historical reanalysis.

Normal current bridge/seal/formal-authority verification is not weakened.

Instead, new fixed policy:

`H1HistoricalPerformanceReanalysis-v1`

authenticates the historical evidence under its original source/tool identities before corrected analysis.

### Fixed-source compatibility

New:

`Tools/AssemblyShadow/h1_historical_reanalysis.py`

It is fixed to:

- historical source `27df1a3d...`;
- historical checkout `f5e34235...`;
- retained graph `69130bbb...`;
- the exact four historical evidence hashes above.

It verifies historical bridge/seal/formal-authority tool hashes from Git.

It also requires the current successor delta from 27df to contain exactly **five non-metadata analysis paths**:

1. `Tools/AssemblyShadow/README.md`
2. `Tools/AssemblyShadow/h1_graph_reuse.py`
3. `Tools/AssemblyShadow/h1_historical_reanalysis.py`
4. `Tools/AssemblyShadow/h1_paired_performance.py`
5. `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`

Any runner, R00 input/results verifier, measurement, protocol, schedule, graph, Player, native, or runtime source change rejects compatibility.

### Historical proof scope

Compatibility authenticates:

- exact bridge/seal/batch/final-index SHA-256s;
- historical bridge source pins and 69130→27df Git transition;
- exact historical bridge verifier inventory;
- exact historical guard-v2 seal verifier inventory;
- historical retained pilot runner;
- source-27df current formal runner;
- every candidate-B formal authority;
- protected A authority isolation;
- successful candidate launch authority/bridge/seal/map echoes;
- 40/40 formal-batch status and final-index binding;
- exact five-file analysis-only successor.

It grants analysis only.

It cannot authorize historical Player execution, a new historical bridge/seal, or an arbitrary source override.

### Primary regression coverage

New tests cover:

- the exact Local analyzer failure diagnosis;
- actual producer-shaped R00 raw build binding;
- wrong/missing top-level identity rejection;
- conflicting optional nested identity rejection;
- exact five-file real Git delta;
- historical bridge reconstruction from historical Git;
- exact historical seal verifier inventory;
- checkpoint MANIFEST SHA constants;
- 40/40 formal-batch binding;
- synthetic 4-pilot + 40-formal authority chain;
- retained-pilot/source-27df-formal runner isolation.

## Local validation

Authoritative detailed plan:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`

Run it in order.

### Current source/tool validation

Before any bounded or historical-analysis work, rerun the committed V00 preflight against the final pushed checkout and require it to pass. Independently confirm that the nine restored agent-configuration paths are byte-identical to `7aa6f619...` and that `7aa6f619... → HEAD` contains metadata-only paths under the unchanged verifier policy.


Run:

- committed handoff/source preflight;
- bounded Primary;
- complete Python discovery;
- exact source audits.

Do **not** refresh installed runtime, run Unity, build Players, reseal, or resample performance.

The current source is analysis-only.

Prior runtime/Unity evidence is reused only after the exact five-file audit and must be explicitly labelled reused.

### Exact source audit

Require:

`27df1a3d... → 7aa6f619...`

equals exactly the five analysis-only paths listed above.

Also require:

`69130bbb... → 7aa6f619...`

equals the exact 24-path retained-graph tooling allowlist in machine authority.

### Reauthenticate completed evidence

Verify the source-27df checkpoint manifest and exact four evidence hashes.

Use the original live paths recorded by the historical receipts.

Do not replace them with checkpoint-copy paths.

### Historical compatibility preflight

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

- `kind=H1HistoricalAnalysisCompatibility`;
- `status=AuthenticatedAnalysisOnlySuccessor`;
- correct policy ID;
- exact four fixed evidence hashes;
- exact historical/current source identities;
- exact five-file delta;
- historical formal batch 40/40;
- historical sample = 45 attempts / 40 formal;
- exact historical bridge/seal/formal authority proof.

The command must not launch a Player.

If preflight fails, stop and return to Primary. Do not rerun formal evidence.

### Corrected historical analysis

Only after preflight passes:

~~~text
python3 Tools/AssemblyShadow/h1_historical_reanalysis.py \
  --sample-index <27df-live-final-sample-index.json> \
  --pilot-verification-receipt <27df-live-pilot-verification.json> \
  --graph-reuse-bridge <27df-live-graph-reuse-bridge.json> \
  --formal-batch <27df-live-formal-batch.json> \
  --output <new-historical-performance-analysis.json>
~~~

Require:

- `kind=H1ControlledPairedPerformanceSummary`;
- `result=Passed`;
- `status=ComparabilityPassed`;
- embedded compatibility status Passed;
- 10 formal pairs per mode;
- 1 valid selected pilot per mode;
- 10 startup observations per mode;
- complete chronology/non-overlap;
- 45 retained attempts:
  - 44 valid;
  - 1 invalid preserved historical failed pilot attempt;
- no formal attempt invalid;
- each mode statistics `formalPairCount=10`.

Retain the measured result even if performance is unfavorable.

If this analysis fails for another contract/tool reason, return to Primary. Do not rerun Players as a workaround.

### Checkpoint / V05 / M08

After analysis Passed:

1. authenticate a new analysis-only checkpoint referencing the immutable source-27df execution checkpoint;
2. prepare V05 successor evidence under the existing project plan;
3. prepare a fresh independent-M08 package;
4. use only an established genuinely independent reviewer mechanism for M08;
5. if such a mechanism is unavailable, return `ReadyForIndependentM08` rather than self-approving.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**.

Stop for explicit human approval.

## Failure evidence

On compatibility failure retain:

- current source/checkout;
- five-file Git delta;
- exact four historical input hashes;
- first mismatching historical Git/receipt/tool/authority binding;
- stdout/stderr;
- proof no Player was launched.

On analysis failure retain:

- compatibility preflight;
- complete corrected analysis output;
- first invalid attempt/side/raw build binding;
- corresponding frozen build receipt and raw result.

## Alternatives

Do not:

- change the R00 producer to retrofit nested duplicate fields;
- rerun the 40 formal Players to work around this analyzer bug;
- regenerate the historical bridge/seal/formal authorities;
- broaden the five-file compatibility delta;
- substitute checkpoint-copy paths for bound live paths;
- ignore wrong/missing top-level build identity;
- remove build GUID/path/SHA checks;
- delete the historical failed pilot attempt;
- alter protocol/schedule/map/statistics;
- begin R02.

If compatibility cannot honestly authenticate the fixed source-27df series, return to Primary.

## Risks

- Historical reanalysis depends on the original live evidence paths still being available and hash-identical.
- The compatibility policy is intentionally fixed to one completed source-27df series; it is not a general historical execution mechanism.
- Any execution/runtime/measurement source change would invalidate compatibility.
- A further analyzer defect can still block V04 closure, but must be fixed in Primary rather than by resampling.
- Independent M08 remains mandatory even after analysis Passed.

## Local correction boundary

Local may adjust only:

- absolute paths to the already authenticated live historical files;
- new analysis/checkpoint output roots;
- permissions/PYTHONPATH;
- bounded command syntax.

Local must not modify:

- historical receipts/evidence;
- fixed SHA/source constants;
- five-file compatibility allowlist;
- analyzer semantics;
- protocol/schedule/map;
- execution/runtime tools;
- M08 independence rules.

Any non-trivial source/tool correction returns to Primary.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress** until corrected historical analysis and genuine independent M08 close.

No Player rerun is required when compatibility and corrected analysis pass.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**. Human approval must then be explicit.

**Do not begin R02.**
