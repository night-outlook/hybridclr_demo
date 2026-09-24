# Local Validation Tasks — H1 Test-Only Historical Reanalysis Successor

Current analysis/test source anchor:

`d239d9d00784ea2df22133cb8c938ec25035f5a0`

Previous analysis source anchor:

`7aa6f61994da354b04464e38ddfc8552cc5c3055`

Latest Local return:

`144a26adf37bc0ecd5222499d328d1d1560910a0`

Completed formal execution source:

`27df1a3d60811dc121f296ab561ae313a382b363`

Retained graph source:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3`

Latest blocked checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority7aa6-python-fixture-blocked/`

H1 remains `InProgress`. Do not begin R02.

## Goal

Validate the corrected synthetic R00 fixture and the exact test-only source successor, then authenticate and reanalyze the immutable source-27df 40/40 series without rerunning Players.

Sequence:

current source authority → bounded 377 → full Python → exact 7-path/25-path audits → complete live historical reauthentication → historical compatibility v2 → corrected analysis → analysis-only checkpoint → V05 → genuinely independent M08 if eligible.

## V00 — repository and source authority

1. Pull final pushed `codex/assembly-shadow-r01b-h1`.
2. Use the exact final demo HEAD from the handoff prompt.
3. Require all four worktrees on the expected branch and matching remote heads.
4. Require runtime/package/native pins:
   - hybridclr `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`
   - hybridclr_unity `0ea633a2c5b936b5af69d944593c55bd2783fca9`
   - il2cpp_plus `6be7f38bec2fa4677d24efc1a4a1294240789933`
5. Require demo source pin = `d239d9d00784ea2df22133cb8c938ec25035f5a0`.
6. Require `d239d9d0... → checkout HEAD` to contain zero non-metadata paths under unchanged `shadow_tools.metadata_only`.
7. Run committed handoff/source preflight and require `SourceTargetVerifiedNotBuildAccepted`.

Record exact commands, UTC timing, versions, branch/commit/remotes, source pins, and package file reference.

Do not infer build acceptance from V00.

## V01 — bounded Primary regression

Run the current bounded Primary suite.

Require:

- `testCount=377`;
- 377 Passed;
- zero Skipped;
- zero Failed/Error.

Explicitly require the inventory contains and passes:

`test_h1_paired_performance.H1PairedPerformanceTests.test_analyze_sample_index_complete_positive`

If the bounded count remains 376, fail the cycle.

## V01B — complete Python discovery

Run:

~~~text
python3 Tools/AssemblyShadow/h1_test_inventory.py python \
  --tests <project>/Tools/AssemblyShadow/tests \
  --pattern 'test*.py' \
  --log <new-python-log> \
  --output <new-python-inventory>
~~~

Require:

- discovered/executed leaves = 1,061 unless environment-independent test inventory changed unexpectedly;
- zero Failed;
- zero Error;
- every skip explicit and justified;
- the paired-performance positive leaf Passed.

Expected from the previous environment if skip conditions are unchanged:

- 1,033 Passed;
- 28 Skipped;
- 0 Failed;
- 0 Error.

Treat those counts as expectations, not as a substitute for the fresh inventory.

## V01A — exact source audits

### A. Completed execution source → current analysis/test source

Compare:

`27df1a3d60811dc121f296ab561ae313a382b363`

to:

`d239d9d00784ea2df22133cb8c938ec25035f5a0`

After metadata classification, require exactly these **seven** non-metadata paths:

1. `Tools/AssemblyShadow/README.md`
2. `Tools/AssemblyShadow/h1_bee_primary_tests.py`
3. `Tools/AssemblyShadow/h1_graph_reuse.py`
4. `Tools/AssemblyShadow/h1_historical_reanalysis.py`
5. `Tools/AssemblyShadow/h1_paired_performance.py`
6. `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`
7. `Tools/AssemblyShadow/tests/test_h1_paired_performance.py`

Require policy:

`H1HistoricalPerformanceReanalysis-v2`

Any subset or superset fails.

### B. Previous analysis source → current source

Compare:

`7aa6f61994da354b04464e38ddfc8552cc5c3055`

to:

`d239d9d00784ea2df22133cb8c938ec25035f5a0`

Require exactly six non-metadata paths:

- `Tools/AssemblyShadow/README.md`
- `Tools/AssemblyShadow/h1_bee_primary_tests.py`
- `Tools/AssemblyShadow/h1_graph_reuse.py`
- `Tools/AssemblyShadow/h1_historical_reanalysis.py`
- `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`
- `Tools/AssemblyShadow/tests/test_h1_paired_performance.py`

Of those, only `test_h1_paired_performance.py` is a new unique path relative to the already-authenticated retained-graph 24-path set.

### C. Retained graph → current source

Compare:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3`

to:

`d239d9d00784ea2df22133cb8c938ec25035f5a0`

Require equality to the exact **25-path** `H1V04RetainedGraphToolOnlySuccessor-v2` allowlist in `source-targets.json` and `h1_graph_reuse.ALLOWED_NON_METADATA_PATHS`.

The v2-added unique path must be exactly:

`Tools/AssemblyShadow/tests/test_h1_paired_performance.py`

Do not edit any allowlist locally.

## V02 — completed source-27df evidence

Authenticate:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260923-authority27df-formal-analysis-blocked/`

Require its manifest to pass completely.

Require exact live SHA-256 identities:

- bridge: `c03665dbdba797f5024fa8f376e6ac6aa6edf165c76387ddbf01ee6d3611826c`
- seal: `bdc4062acfc6d208a9be50a142b897a07e7359e5df14ad3d3d8f2805c5179631`
- formal batch: `97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667`
- final sample: `a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021`

Then perform the complete live evidence reauthentication required by the existing H1 plan, not merely four hash spot checks.

Use original live paths from historical receipts.

Do not rewrite, copy-substitute, or relocate authenticated evidence bindings.

## V04.AF — historical compatibility v2

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
- `policyId=H1HistoricalPerformanceReanalysis-v2`;
- historical source = `27df1a3d...`;
- historical checkout = `f5e34235...`;
- current source = `d239d9d0...`;
- exact seven-path analysis/test delta;
- exact four fixed evidence hashes;
- formal batch 40/40 Passed;
- sample = 45 attempts / 40 formal;
- historical bridge/formal authorities authenticate their original v1 policy and tool hashes;
- retained pilot provenance and protected-A authority isolation remain exact.

The preflight must not launch Players.

If it fails, stop and return to Primary.

## V04.AG — historical strict analysis

Only after V04.AF passes, run the same tool without `--preflight-only`.

Require:

- `kind=H1ControlledPairedPerformanceSummary`;
- `result=Passed`;
- `status=ComparabilityPassed`;
- embedded compatibility = `AuthenticatedAnalysisOnlySuccessor`;
- formal pairs per mode = 10 each;
- selected valid pilot per mode = 1 each;
- formal startup observations per mode = 10 each;
- chronology complete;
- global intervals resolved and non-overlapping;
- pilots precede formals;
- exactly 45 attempt records:
  - 44 valid/analyzable;
  - 1 preserved invalid ON-NoPatch pilot attempt 1;
- no formal attempt invalid;
- each mode `formalPairCount=10`.

For selected raw R00 results require:

- top-level build GUID/baseline/runtime ABI equals frozen build;
- nested receipt path/SHA/build GUID equals frozen build;
- absent nested baseline/runtime remains acceptable;
- present nested duplicates must agree.

Retain measured statistics without suppressing an unfavorable result.

If analysis fails, return to Primary. Do not rerun Players as a workaround.

## V04.AH — analysis-only checkpoint

After V04.AG passes, create and authenticate a new checkpoint containing:

- V00 source authority;
- bounded 377 evidence;
- complete Python inventory;
- exact 7/6/25-path source audits;
- complete source-27df live evidence authentication;
- compatibility v2 preflight;
- corrected historical analysis;
- exact four fixed evidence hashes;
- explicit statement that no new Player execution occurred;
- links/references to all prior blocked checkpoints.

Authenticate the new manifest.

## V05 / independent M08

If and only if V04 historical analysis is Passed/ComparabilityPassed:

1. prepare V05 successor evidence;
2. prepare a fresh independent-M08 package;
3. use an established genuinely independent reviewer mechanism;
4. otherwise return `ReadyForIndependentM08` rather than self-approving.

M08 must review at minimum:

- real producer vs analyzer build-identity contract;
- corrected positive fixture;
- bounded regression coverage;
- v2 seven-path historical policy;
- v2 25-path retained-graph policy;
- immutable historical bridge/seal/formal authority provenance;
- one failed pilot retained/non-selected;
- 40/40 formal series;
- no Player rerun after analysis/test corrections.

Only genuine M08 PASS may make H1 Ready for Human Review Gate.

Stop for explicit human approval.

**Do not begin R02.**

## Failure evidence

For source/Python failure retain exact checkout/source revisions, source audits, inventories, logs, first failure, and traceback.

For compatibility failure retain exact historical/current revisions, four fixed hashes, first mismatching binding, output/stdout/stderr, and proof no Player launched.

For analysis failure retain compatibility preflight, complete analysis, first invalid attempt/side/raw field, and relevant build/raw evidence.

## Local correction boundary

Local may adjust only:

- absolute paths to already-authenticated live historical files;
- new output/checkpoint roots;
- permissions/PYTHONPATH;
- bounded invocation syntax.

Local must not:

- change the fixture or production analyzer;
- modify source pins or v2 allowlists;
- rewrite historical receipts;
- change fixed hashes/revisions;
- rerun Players/bridges/seals/formal pairs;
- alter protocol/schedule/map/statistics;
- claim independent M08 without genuine independence.

Any non-trivial source/tool correction returns to Primary.
