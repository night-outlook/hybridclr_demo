# Primary Implementation → Local Validation

## Objective

Validate the test-only historical-analysis successor at source anchor:

`d239d9d00784ea2df22133cb8c938ec25035f5a0`

Then, only if current source/Python validation passes, authenticate and reanalyze the already-completed source-27df 40/40 formal series without rerunning Players.

Latest Local return:

`144a26adf37bc0ecd5222499d328d1d1560910a0`

H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

**Do not begin R02.**

## Source targets

Machine authority:

`Docs/AssemblyShadow/Handoff/source-targets.json`

Candidate/current identities:

| Repository | Branch | Required source/runtime identity |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | analysis/test source anchor `d239d9d00784ea2df22133cb8c938ec25035f5a0` |
| `night-outlook/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| `night-outlook/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| `night-outlook/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |

The final pushed demo checkout HEAD may be later than `d239d9d0...` only by paths classified as metadata by the unchanged `shadow_tools.metadata_only` policy. Local must use the exact final pushed HEAD from the handoff prompt and must independently prove the non-metadata tree equals the source anchor.

Completed formal execution source:

`27df1a3d60811dc121f296ab561ae313a382b363`

Historical checkout finalizing that source family:

`f5e34235641c212c715aef3405925ddd4cf28ee6`

Retained graph source:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3`

Authenticated completed-series checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260923-authority27df-formal-analysis-blocked/`

Latest blocked Local checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority7aa6-python-fixture-blocked/`

## Implementation

### Returned failure

The repaired 7aa source-authority handoff passed V00.R and committed V00. Bounded Primary passed 376/376, but full Python discovery produced:

- 1,061 leaves;
- 1,032 Passed;
- 28 explicit environment Skipped;
- 1 Failed.

The failed leaf was:

`test_h1_paired_performance.H1PairedPerformanceTests.test_analyze_sample_index_complete_positive`

Its synthetic `raw()` fixture modeled the old receipt shape: build GUID, baseline ID, and runtime ABI existed only inside `playerBuildReceipt`. The corrected production analyzer intentionally requires those identities at raw-result top level.

Local proved in memory that adding the three top-level fields makes the focused positive case reach `ComparabilityPassed`.

### Fixture correction

`Tools/AssemblyShadow/tests/test_h1_paired_performance.py` now emits:

- top-level `buildGuid`;
- top-level `baselineBuildId`;
- top-level `runtimeAbiHash`;

while retaining the nested receipt:

- path;
- SHA-256;
- build GUID;
- matching optional baseline/runtime copies.

No production analyzer check was weakened.

### Mandatory bounded regression

`Tools/AssemblyShadow/h1_bee_primary_tests.py` now explicitly loads only:

`test_h1_paired_performance.H1PairedPerformanceTests.test_analyze_sample_index_complete_positive`

The expected bounded suite therefore grows from 376 to **377** leaves. A bounded PASS can no longer omit this positive analyzer contract.

### Historical-analysis compatibility successor

New policy:

`H1HistoricalPerformanceReanalysis-v2`

The exact source-27df → current-anchor non-metadata set is **seven paths**:

1. `Tools/AssemblyShadow/README.md`
2. `Tools/AssemblyShadow/h1_bee_primary_tests.py`
3. `Tools/AssemblyShadow/h1_graph_reuse.py`
4. `Tools/AssemblyShadow/h1_historical_reanalysis.py`
5. `Tools/AssemblyShadow/h1_paired_performance.py`
6. `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`
7. `Tools/AssemblyShadow/tests/test_h1_paired_performance.py`

Relative to v1, the only additional paths are the bounded regression runner and the synthetic paired-performance fixture. No Player runner, R00 verifier, runtime, measurement, protocol, schedule, graph producer, native source, or execution-authority source is added.

### Retained-graph compatibility successor

New current-source policy:

`H1V04RetainedGraphToolOnlySuccessor-v2`

The exact retained-graph `69130bbb... → d239d9d0...` non-metadata allowlist contains **25 paths**: the prior reviewed 24-path set plus:

`Tools/AssemblyShadow/tests/test_h1_paired_performance.py`

The historical source-27df bridge and formal authorities remain v1 evidence. `h1_historical_reanalysis.py` continues to authenticate those immutable historical v1 receipts explicitly; current v2 policy does not relabel them.

### Immutable evidence preserved

The source-27df execution series is unchanged:

- 40/40 formal pairs passed first attempt;
- 10 OFF-NoPatch;
- 10 ON-NoPatch;
- 10 ON-P01;
- 10 ON-P03;
- zero formal retries.

Fixed historical evidence SHA-256:

- graph bridge: `c03665dbdba797f5024fa8f376e6ac6aa6edf165c76387ddbf01ee6d3611826c`;
- guard-v2 seal: `bdc4062acfc6d208a9be50a142b897a07e7359e5df14ad3d3d8f2805c5179631`;
- formal batch: `97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667`;
- final sample index: `a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021`.

No historical receipt, bridge, seal, authority, sample, build, or Player result was modified.

### Primary-side evidence status

No new GitHub Actions run was available to this Primary environment for the new source anchor. Do not promote the earlier 376/376 run to current-source validation.

Fresh required expectations are:

- bounded Primary: 377/377;
- full Python discovery: 1,061 leaves;
- expected if unchanged environment skips: 1,033 Passed / 28 Skipped / 0 Failed / 0 Error.

The exact empirical counts remain Local Validation evidence, not Primary assumptions.

## Local validation

Authoritative detailed plan:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`

Run in order.

### V00 — source authority

1. Pull final pushed `codex/assembly-shadow-r01b-h1`.
2. Require the final pushed repository HEAD from the handoff prompt.
3. Require clean tracked state before evidence output.
4. Require `ProjectSettings/AssemblyShadowSourcePins.json` demo revision = `d239d9d0...`.
5. Require `d239d9d0... → checkout HEAD` has zero non-metadata paths under unchanged `shadow_tools.metadata_only`.
6. Run committed `h1_handoff_preflight.py` and require `SourceTargetVerifiedNotBuildAccepted`.
7. Reconfirm the other three runtime/package/native pins exactly match the table above.

Do not mark build acceptance from this preflight.

### V01 — current source/Python

Run the bounded Primary regression and require:

- 377 tests;
- 377 Passed;
- zero skips/failures/errors.

Run complete Python discovery and require:

- zero failures/errors;
- every skip explicit;
- the corrected positive paired-performance test Passed.

Retain full inventories and logs.

### V01A — exact source audits

Require:

`27df1a3d60811dc121f296ab561ae313a382b363 → d239d9d00784ea2df22133cb8c938ec25035f5a0`

to equal exactly the seven-path `H1HistoricalPerformanceReanalysis-v2` set above.

Require:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3 → d239d9d00784ea2df22133cb8c938ec25035f5a0`

to equal exactly the 25-path `H1V04RetainedGraphToolOnlySuccessor-v2` set in machine authority.

Any subset or superset fails.

### V02 — completed evidence authentication

Authenticate the source-27df checkpoint manifest and all referenced live evidence.

Require the exact four fixed hashes above and complete live binding availability.

Use original live paths recorded by historical receipts. Do not substitute checkpoint-copy paths.

### V04.AF — historical compatibility preflight

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
- `policyId=H1HistoricalPerformanceReanalysis-v2`;
- current source revision = `d239d9d0...`;
- exact seven-path historical analysis/test delta;
- exact historical v1 bridge/seal/formal-authority proof;
- formal batch = 40/40 Passed;
- historical sample = 45 attempts / 40 formal;
- exact four evidence hashes.

This command must not launch Players.

If it fails, stop and return to Primary. Do not rerun formal evidence.

### V04.AG — corrected historical analysis

Only after V04.AF passes, run the same tool without `--preflight-only`.

Require:

- `kind=H1ControlledPairedPerformanceSummary`;
- `result=Passed`;
- `status=ComparabilityPassed`;
- embedded compatibility status `AuthenticatedAnalysisOnlySuccessor`;
- 10 formal pairs per mode;
- 1 selected valid pilot per mode;
- 10 formal startup observations per mode;
- chronology/non-overlap complete;
- 45 retained attempts:
  - 44 valid/analyzable;
  - 1 preserved invalid historical ON-NoPatch pilot attempt;
- no formal attempt invalid;
- `formalPairCount=10` for every mode.

Retain measured results even if unfavorable.

### V04.AH / V05 / independent M08

After V04.AG passes:

1. authenticate a new analysis-only checkpoint referencing the immutable source-27df execution checkpoint;
2. prepare V05 successor evidence;
3. prepare and execute a genuinely independent M08 review when an established independent mechanism exists;
4. otherwise return `ReadyForIndependentM08`, not a self-approved PASS.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**.

## Failure evidence

On current-source/Python failure retain:

- final checkout HEAD and source anchor;
- bounded and full Python inventories/logs;
- first failing test and traceback;
- exact 7-path and 25-path source audits.

On compatibility failure retain:

- exact current/historical source identities;
- exact four historical input hashes;
- first failing bridge/seal/batch/sample/formal-authority binding;
- stdout/stderr;
- proof no Player was launched.

On analysis failure retain:

- compatibility preflight;
- complete analysis output;
- first invalid attempt/side/raw field;
- corresponding raw result and frozen build binding.

## Alternatives

Do not:

- classify the paired-performance test fixture as metadata;
- remove or weaken top-level `buildGuid`, `baselineBuildId`, or `runtimeAbiHash` checks;
- retrofit or rewrite historical source-27df receipts;
- rerun the 40 formal Players to work around an analysis/test defect;
- regenerate historical bridge/seal/formal authorities;
- accept a source delta other than the exact seven-path v2 set;
- accept a retained-graph delta other than the exact 25-path v2 set;
- substitute copied evidence paths for authenticated live paths;
- delete or relabel the preserved failed pilot;
- alter protocol/schedule/map/statistics;
- begin R02.

## Risks

- Original live evidence paths must remain present and hash-identical.
- The historical compatibility mechanism is intentionally fixed to the source-27df series.
- The two v2 additions are test-only; any execution/runtime/measurement delta invalidates historical reanalysis.
- Another analyzer/test defect may still block V04 and must return to Primary rather than trigger resampling.
- Independent M08 remains mandatory after analysis passes.

## Local correction boundary

Local may adjust only:

- absolute paths to already authenticated live historical evidence;
- new evidence/checkpoint output roots;
- permissions/PYTHONPATH;
- bounded invocation syntax.

Local must not modify:

- production analyzer semantics;
- source pins or compatibility allowlists;
- historical receipts/evidence;
- fixed SHA/source constants;
- protocol/schedule/map;
- execution/runtime tools;
- M08 independence rules.

Any non-trivial source/tool correction returns to Primary.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress** until corrected historical analysis and genuinely independent M08 close.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**. Human approval must then be explicit.

**Do not begin R02.**
