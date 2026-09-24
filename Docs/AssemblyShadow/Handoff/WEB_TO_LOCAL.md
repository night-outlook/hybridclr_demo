# Primary Implementation → Local Validation

## Objective

Validate the split-checkout repair at analysis/test source anchor:

`d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece`

Then authenticate and reanalyze the immutable source-27df 40/40 formal series without rerunning Players.

Latest Local return:

`57d51ac4b1d09eb190a7e95235a7ec6ff5ed1357`

H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

**Do not begin R02.**

## Source targets

Machine authority:

`Docs/AssemblyShadow/Handoff/source-targets.json`

Required repository identities:

| Repository | Branch | Source/runtime identity |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | analysis/test anchor `d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece` |
| `night-outlook/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| `night-outlook/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| `night-outlook/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |

The final pushed demo checkout may be later than the source anchor only by paths classified as metadata under the unchanged `shadow_tools.metadata_only` policy.

Historical identities remain:

- completed execution source: `27df1a3d60811dc121f296ab561ae313a382b363`;
- historical checkout family: `f5e34235641c212c715aef3405925ddd4cf28ee6`;
- retained graph source: `69130bbb3a6df516916dddb5ad263799a7c6e5e3`;
- historical compatibility: `H1HistoricalPerformanceReanalysis-v2`, exact seven paths;
- retained graph compatibility: `H1V04RetainedGraphToolOnlySuccessor-v2`, exact 25 paths.

Latest blocked checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authorityd239-compatibility-project-blocked/`

Immutable execution checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260923-authority27df-formal-analysis-blocked/`

## Implementation

### Returned Local result

At d239 Local passed:

- source authority and exact seven/25-path audits;
- bounded Primary **377/377**;
- full Python **1,033 Passed / 28 explicit Skipped / 0 Failed / 0 Error** across 1,061 leaves;
- source-27df manifest **92/92**;
- exact four fixed historical input hashes;
- complete sealed-live reauthentication: **33,792/33,792 files**, 1,606,993,133 bytes, zero unresolved mismatches.

No Player was rerun.

V04.AF failed because `authenticate_compatibility` treated the immutable historical bridge `projectRoot` as the current analysis-source checkout. That owner checkout still pinned `7aa6f619...`, while the designated validation checkout pinned `d239d9d0...`. The preflight therefore saw the older five-path source authority and reported the two v2 test paths missing.

### Repair — separate the two authorities

`h1_historical_reanalysis.py` now requires:

`--analysis-project <current-validation-checkout>`

Two roots are intentionally distinct:

1. **Current analysis project**
   - supplies current source authority;
   - must be a canonical Git root;
   - its source-pin file must equal committed HEAD;
   - must identify `night-outlook/hybridclr_demo` with `localPath=.`;
   - its complete non-metadata tree must equal its pinned source revision;
   - its copy of `h1_historical_reanalysis.py` must byte-match the running tool.

2. **Historical evidence project**
   - comes only from immutable historical receipts such as `bridge.projectRoot`;
   - continues to own historical build/fixture/launch paths;
   - its present-day source pin is **not** current analysis authority;
   - historical Git/source/tool identities continue to be reconstructed from fixed revisions and receipt hashes.

### Repair — strict historical R00 verification

Full V04.AG would otherwise still depend on the mutable historical candidate checkout through normal retained-graph input verification.

The historical reanalysis tool now provides a candidate-side historical-input verifier only during the strict historical callback. It rechecks:

- historical baseline source pins;
- NativeOn/NativeOff snapshot source pins;
- fixture resources;
- ON/OFF distinct build identities;
- managed input equivalence;
- manifest ON receipt path/hash;
- Editor replay source pins;
- original historical build/output paths.

It uses the immutable historical graph/source DTOs and bridge-installed verification evidence, not the historical checkout's current pin.

Normal shared source is unchanged:

- `r00_player_inputs.py`: unchanged;
- `r00_results.py`: unchanged;
- `r01_early_results.py`: unchanged.

The historical callback temporarily substitutes the candidate-side retained-input verifier for both normal R00 and nested early-startup reconstruction and restores both globals in `finally`.

### Regression coverage

Four new leaves were added inside the already-bounded `test_h1_graph_reuse` module:

1. **split-checkout process regression**  
   Creates a real detached historical worktree at the stale checkout commit reported by Local while using the current checkout as analysis authority. Historical bridge verification must accept that split and retain source-27df historical pins.

2. **wrong current pin rejection**  
   Creates a detached current worktree, commits an intentionally stale 7aa pin, and requires current source verification to fail closed.

3. **compatibility routing**  
   Locks `authenticate_compatibility` so current delta/source authority uses the designated analysis root while historical receipts use the historical root.

4. **strict verifier scope/restoration**  
   Requires candidate historical verification to install the historical-input override only inside the callback and restore both normal R00 and early-startup verifier functions afterward.

The split-checkout regression also mutates the historical build-map binding and requires fail-closed rejection.

### Source/policy scope

New source anchor:

`d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece`

Relative to d239, only these three already-allowed non-metadata paths changed:

- `Tools/AssemblyShadow/README.md`;
- `Tools/AssemblyShadow/h1_historical_reanalysis.py`;
- `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`.

Therefore the existing exact v2 policies are unchanged:

**Historical analysis/test seven-path set**

1. `Tools/AssemblyShadow/README.md`
2. `Tools/AssemblyShadow/h1_bee_primary_tests.py`
3. `Tools/AssemblyShadow/h1_graph_reuse.py`
4. `Tools/AssemblyShadow/h1_historical_reanalysis.py`
5. `Tools/AssemblyShadow/h1_paired_performance.py`
6. `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`
7. `Tools/AssemblyShadow/tests/test_h1_paired_performance.py`

**Retained graph policy**

`H1V04RetainedGraphToolOnlySuccessor-v2` remains the exact 25-path set already recorded in machine authority.

No execution runner, R00 shared verifier, measurement source, protocol, schedule, graph producer, Player/native/runtime source, or execution-authority source was added.

### Immutable historical evidence

Source-27df evidence is unchanged:

- 40/40 formal pairs Passed;
- 10 per mode;
- zero formal retries.

Fixed SHA-256:

- bridge: `c03665dbdba797f5024fa8f376e6ac6aa6edf165c76387ddbf01ee6d3611826c`;
- guard-v2 seal: `bdc4062acfc6d208a9be50a142b897a07e7359e5df14ad3d3d8f2805c5179631`;
- formal batch: `97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667`;
- final sample index: `a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021`.

No historical evidence file or receipt was rewritten.

### Primary validation status

No GitHub Actions run was available for the new source commits in this Primary environment.

Fresh Local requirements are therefore authoritative:

- bounded Primary: **381/381**;
- full Python discovery: **1,065** leaves;
- expected if the same environment skips remain: **1,037 Passed / 28 Skipped / 0 Failed / 0 Error**.

These counts are expectations until Local executes them.

## Local validation

Authoritative detailed plan:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`

Run the complete sequence in order.

### V00 — source authority

1. Pull final pushed `codex/assembly-shadow-r01b-h1`.
2. Require exact final pushed HEAD from the handoff prompt.
3. Require all four repository remote heads and branches.
4. Require demo source pin = `d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece`.
5. Require source anchor → final checkout HEAD has zero non-metadata paths.
6. Run committed handoff/source preflight and require `SourceTargetVerifiedNotBuildAccepted`.
7. Preserve explicit distinction between source authority and build acceptance.

### V01 — current source regression

Run bounded Primary and require:

- 381 tests;
- 381 Passed;
- zero Skip/Fail/Error.

Run complete Python discovery and require:

- 1,065 discovered/executed leaves unless an independently explained inventory change exists;
- zero Failed/Error;
- every skip explicit;
- all split-checkout regressions Passed.

Expected under the previous environment skip set:

- 1,037 Passed;
- 28 Skipped.

### V01A — exact source audits

Require source-27df → current anchor to equal exactly the existing seven-path v2 set.

Require retained 69130 → current anchor to equal exactly the existing 25-path v2 set.

Also record d239 → current anchor and require its non-metadata set to equal exactly:

- `Tools/AssemblyShadow/README.md`;
- `Tools/AssemblyShadow/h1_historical_reanalysis.py`;
- `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`.

Any unexpected path fails.

### V02 — complete historical evidence authentication

Repeat complete read-only source-27df evidence authentication:

- checkpoint manifest;
- four fixed input hashes;
- all sealed live files;
- direct binding semantics.

Preserve any generic-vs-semantic binding distinction exactly as in the previous Local checkpoint.

Do not rewrite evidence.

### V04.AF — split-checkout historical compatibility

Run from the designated validation checkout:

~~~text
python3 Tools/AssemblyShadow/h1_historical_reanalysis.py \
  --analysis-project /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
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
- `analysisProjectRoot` = designated validation checkout;
- `historicalProjectRoot` = original bridge project root;
- the two roots differ in this reproduced split-checkout case;
- current source revision = `d61bd9df...`;
- exact seven-path current analysis delta;
- historical bridge/seal/formal authority retain original v1 identities;
- exact four fixed evidence hashes;
- formal batch = 40/40;
- historical sample = 45 attempts / 40 formal.

No Player may launch.

If V04.AF fails, retain full output and return to Primary; do not run V04.AG.

### V04.AG — corrected strict historical analysis

Only after V04.AF passes:

~~~text
python3 Tools/AssemblyShadow/h1_historical_reanalysis.py \
  --analysis-project /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
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
- embedded compatibility = `AuthenticatedAnalysisOnlySuccessor`;
- 10 formal pairs/mode;
- one selected valid pilot/mode;
- 10 formal startup observations/mode;
- complete chronology and non-overlap;
- 45 retained attempts;
- 44 valid/analyzable;
- one preserved invalid historical ON-NoPatch pilot attempt;
- no formal attempt invalid;
- each mode `formalPairCount=10`.

Retain measured statistics even if unfavorable.

### V04.AH / V05 / M08

If and only if V04.AG passes:

1. create/authenticate an analysis-only closure checkpoint;
2. prepare V05;
3. prepare a fresh genuinely independent M08 package;
4. execute M08 only through an established independent mechanism;
5. otherwise return `ReadyForIndependentM08`, never a self-approved PASS.

Only genuine M08 PASS may make H1 Ready for Human Review Gate.

## Failure evidence

For source/test failure retain exact checkout/source identities, bounded/full inventories, logs, traceback, and exact source audits.

For V04.AF failure retain:

- `analysisProjectRoot`;
- `historicalProjectRoot`;
- both pin DTOs;
- exact seven/25-path audits;
- four fixed hashes;
- first failed historical binding;
- stdout/stderr;
- proof no Player launched.

For V04.AG failure retain compatibility receipt, complete analysis output, first invalid attempt/side/raw field, and corresponding historical evidence.

## Alternatives

Do not:

- move or rewrite the historical bridge project;
- update the historical owner checkout merely to make compatibility pass;
- derive current analysis authority from a historical receipt path;
- weaken v2 seven-path or 25-path policies;
- change `r00_player_inputs.py`, `r00_results.py`, or `r01_early_results.py` for this repair;
- remove top-level build-identity checks;
- rerun the 40 formal Players as a workaround;
- regenerate historical bridge/seal/formal authorities;
- delete/relabel the preserved failed pilot;
- begin R02.

## Risks

- Historical absolute evidence paths must remain present and hash-identical.
- Strict historical analysis now explicitly depends on two independently authenticated roots; mixing their authority roles must fail closed.
- Protected side A still uses its normal preserved validation path; only historical candidate side B receives the historical-input adapter.
- Another evidence/analysis defect may still block V04 and must return to Primary rather than trigger resampling.
- Independent M08 remains mandatory.

## Local correction boundary

Local may adjust only:

- absolute path spelling for the already designated validation checkout and authenticated historical evidence;
- new output/checkpoint roots;
- permissions/PYTHONPATH;
- bounded command syntax.

Local must not modify source, pins, compatibility policies, historical receipts/evidence, protocol/schedule/map/statistics, or M08 independence rules.

Any non-trivial correction returns to Primary.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress** until V04 closure and genuinely independent M08 pass.

Only genuine M08 PASS may make H1 **Ready for Human Review Gate**. Human approval must then be explicit.

**Do not begin R02.**
