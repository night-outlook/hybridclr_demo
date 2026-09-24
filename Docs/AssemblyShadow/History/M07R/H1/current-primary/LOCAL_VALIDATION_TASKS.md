# Local Validation Tasks — Split-Checkout Historical Reanalysis Repair

Current analysis/test source anchor:

`d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece`

Latest Local return:

`57d51ac4b1d09eb190a7e95235a7ec6ff5ed1357`

Completed formal execution source:

`27df1a3d60811dc121f296ab561ae313a382b363`

Retained graph source:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3`

Previous blocked checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authorityd239-compatibility-project-blocked/`

H1 remains `InProgress`. Do not begin R02.

## Goal

Validate the split between current analysis authority and immutable historical evidence paths, then close as much of V04/V05/M08 as eligibility permits in one Local cycle.

Do not rerun Players.

## V00 — repository/source authority

1. Pull the final handoff branch and exact pushed commits.
2. Require clean tracked state before writing new evidence.
3. Record all four paths, branches, HEADs, remote HEADs, worktree registrations, remotes, pins, package reference, tool versions, and host.
4. Require:
   - demo source pin `d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece`;
   - hybridclr `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`;
   - hybridclr_unity `0ea633a2c5b936b5af69d944593c55bd2783fca9`;
   - il2cpp_plus `6be7f38bec2fa4677d24efc1a4a1294240789933`.
5. Require source anchor → final demo checkout HEAD has zero non-metadata paths under unchanged `shadow_tools.metadata_only`.
6. Run committed `h1_handoff_preflight.py`.
7. Require `SourceTargetVerifiedNotBuildAccepted`.

Stop on any source-authority mismatch.

## V01 — bounded Primary

Run current bounded Primary regression.

Require:

- `testCount=381`;
- 381 Passed;
- zero Skipped/Failed/Error.

Explicitly confirm the four new split-checkout leaves Passed:

- `test_split_checkout_process_regression_uses_designated_analysis_authority`;
- `test_analysis_source_authority_rejects_wrong_committed_pin`;
- `test_compatibility_routes_current_delta_to_designated_analysis_checkout`;
- `test_historical_verified_launch_scopes_and_restores_input_override`.

Also confirm the previously repaired paired-performance positive leaf Passed.

## V01B — complete Python discovery

Run the complete `test*.py` inventory through `h1_test_inventory.py`.

Require:

- discovered count = executed count;
- expected current leaf count = **1,065**, unless a separately explained source-inventory reason exists;
- zero Failed;
- zero Error;
- every skip explicit.

Expected if the same environment skip set remains:

- 1,037 Passed;
- 28 Skipped.

The inventory tool may return nonzero solely because explicit skips are represented as non-Pass; record that distinction exactly.

## V01A — exact source audits

### Historical execution → current source

Require:

`27df1a3d60811dc121f296ab561ae313a382b363 → d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece`

equals exactly these seven non-metadata paths:

1. `Tools/AssemblyShadow/README.md`
2. `Tools/AssemblyShadow/h1_bee_primary_tests.py`
3. `Tools/AssemblyShadow/h1_graph_reuse.py`
4. `Tools/AssemblyShadow/h1_historical_reanalysis.py`
5. `Tools/AssemblyShadow/h1_paired_performance.py`
6. `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`
7. `Tools/AssemblyShadow/tests/test_h1_paired_performance.py`

Policy ID must remain:

`H1HistoricalPerformanceReanalysis-v2`

### Retained graph → current source

Require:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3 → d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece`

equals the exact existing 25-path:

`H1V04RetainedGraphToolOnlySuccessor-v2`

allowlist in machine authority and `h1_graph_reuse.ALLOWED_NON_METADATA_PATHS`.

### Previous current source → repair

Require:

`d239d9d00784ea2df22133cb8c938ec25035f5a0 → d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece`

contains exactly:

- `Tools/AssemblyShadow/README.md`;
- `Tools/AssemblyShadow/h1_historical_reanalysis.py`;
- `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`.

Any additional non-metadata path fails.

## V02 — repeat complete historical evidence authentication

Use the immutable source-27df checkpoint and original live paths.

Repeat and retain:

1. checkpoint `MANIFEST.sha256` verification;
2. exact four fixed input SHA-256s;
3. complete 33,792-file sealed-live inventory/content/stable-stat authentication;
4. direct live binding audit;
5. semantic resolution of any generic binding rows that are Git-source identities rather than live-path identity.

Expected fixed hashes:

- bridge: `c03665dbdba797f5024fa8f376e6ac6aa6edf165c76387ddbf01ee6d3611826c`;
- seal: `bdc4062acfc6d208a9be50a142b897a07e7359e5df14d3d8f2805c5179631`;
- formal batch: `97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667`;
- final sample: `a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021`.

Do not rewrite or relocate historical evidence.

## V04.AF — split-checkout compatibility preflight

Use the designated current validation checkout explicitly:

~~~text
python3 Tools/AssemblyShadow/h1_historical_reanalysis.py \
  --analysis-project /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
  --sample-index <original-live-final-sample-index> \
  --pilot-verification-receipt <original-live-pilot-seal> \
  --graph-reuse-bridge <original-live-graph-bridge> \
  --formal-batch <original-live-formal-batch> \
  --output <new-v04af-output> \
  --preflight-only
~~~

Require:

- `kind=H1HistoricalAnalysisCompatibility`;
- `status=AuthenticatedAnalysisOnlySuccessor`;
- `policyId=H1HistoricalPerformanceReanalysis-v2`;
- `analysisProjectRoot=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`;
- `historicalProjectRoot` equals the immutable bridge's original project root;
- the two roots are distinct in this reproduced case;
- `analysisSourceAuthority.sourceRevision=d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece`;
- exact seven-path analysis delta;
- historical bridge transition remains original v1;
- historical formal authorities remain original v1;
- exact four fixed input hashes;
- 40 formal attempts;
- 45 total retained attempts.

Also retain a receipt proving no Player process was launched.

If V04.AF fails, stop V04 and return exact evidence to Primary.

## V04.AG — strict historical analysis

Only after V04.AF passes, run the same command without `--preflight-only` to a new output.

Require:

- `kind=H1ControlledPairedPerformanceSummary`;
- `result=Passed`;
- `status=ComparabilityPassed`;
- embedded v2 compatibility = `AuthenticatedAnalysisOnlySuccessor`.

Sampling requirements:

- OFF-NoPatch formal pairs = 10;
- ON-NoPatch formal pairs = 10;
- ON-P01 formal pairs = 10;
- ON-P03 formal pairs = 10;
- valid selected pilots = 1/mode;
- formal startup observations = 10/mode;
- formal complete;
- pilots complete;
- startup complete;
- chronology complete;
- intervals resolved;
- intervals non-overlapping;
- pilots before formals.

Attempt retention:

- total attempts = 45;
- valid/analyzable = 44;
- invalid = exactly the preserved historical ON-NoPatch pilot attempt 1;
- no formal attempt invalid.

Build binding:

- required raw top-level build GUID/baseline/runtime ABI exact;
- nested receipt path/SHA/build GUID exact;
- absent nested baseline/runtime allowed;
- present nested duplicates must agree.

Retain all measured statistics, including unfavorable values.

If strict analysis fails for any reason, preserve complete evidence and return to Primary. Do not rerun Players.

## V04.AH — closure checkpoint

After V04.AG passes, create a new authenticated checkpoint containing at least:

- exact repository/source preflight;
- bounded 381 evidence;
- complete Python inventory;
- exact 7/25/3-path audits;
- repeated complete V02 authentication;
- V04.AF compatibility;
- V04.AG analysis;
- no-Player proof;
- references to all previous blocked checkpoints;
- final Local handoff snapshots;
- manifest.

Verify the new checkpoint manifest before continuing.

## V05

If V04 closes, execute the existing documented V05 successor-evidence requirements.

Do not reinterpret historical evidence status while preparing V05.

## Independent M08

If V05 is eligible:

1. prepare a fresh review package;
2. use an established genuinely independent reviewer mechanism/context;
3. require review of:
   - split analysis-vs-historical root design;
   - v2 7/25-path policies;
   - historical candidate input adapter;
   - callback scope/restoration;
   - immutable source-27df evidence;
   - 40/40 execution and corrected strict analysis;
   - preserved failed pilot;
   - no Player rerun.

If independence is unavailable, return `ReadyForIndependentM08`.

Only a genuine independent M08 PASS may make H1 Ready for Human Review Gate.

Stop for explicit human approval.

**Do not begin R02.**

## Failure evidence

For V00/V01 failure retain exact repos, source pins, branch/HEAD/remotes, source audit, test inventory/log, first traceback, and environment.

For V02 failure retain first missing/mismatched live item, expected/actual hash or stable-stat fields, and prior checkpoint reference.

For V04.AF failure retain both project roots, both relevant pin DTOs, source authority receipt, exact source deltas, four input hashes, first failed semantic binding, stdout/stderr, and no-Player proof.

For V04.AG failure retain V04.AF receipt, entire analysis output, first invalid attempt/side/raw field, relevant historical raw/launch/build evidence, and verifier traceback.

## Local correction boundary

Local may change only:

- absolute spelling of the already-designated analysis project path if it resolves to the same canonical checkout;
- original historical live-path arguments when selecting among paths already recorded by the immutable receipts;
- new output/checkpoint roots;
- permissions/PYTHONPATH;
- bounded invocation syntax.

Local must not change:

- source;
- pins;
- v2 allowlists;
- historical receipts;
- fixed revisions/hashes;
- protocol/schedule/map/statistics;
- shared runtime/input verifier behavior;
- M08 independence rules.

Any non-trivial correction returns to Primary.
