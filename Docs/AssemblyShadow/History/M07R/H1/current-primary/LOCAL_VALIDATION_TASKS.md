# Local Validation Tasks — V04 Closure Batch after `f829db51...`

Candidate build-input source anchor:

`925e84d7b653bc7434482e6f4fbde39a4d9fcd0e`

Latest Local checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260919-authority99ef/`

Restart from fresh V00. Prior `99ef65db...` evidence remains historical.

The goal is one maximal batch. Stop only for authority/provenance/shared-input corruption. After foundations pass, preserve isolated functional failures and continue independent cells when their authenticated inputs remain valid.

## V00 — fresh authority

1. Pull the final pushed handoff HEAD.
2. Record checkout HEAD separately from source anchor `925e84d...`.
3. Require clean tracked state.
4. Run candidate `h1_handoff_preflight.py`.
5. Require `SourceTargetVerifiedNotBuildAccepted` and exact source anchor.
6. Run reproduction-tooling and protected-ref checks.
7. Verify candidate + protected installed runtimes before build work.

Hard-stop on failure.

## V01 — broad source and Unity tests

Run the complete Python inventory, bounded Primary suite and broad Unity EditMode suite.

The two stale expectations from the prior cycle must now be clean:

- early default matrix excludes Baseline and the continuation-only failure modes by semantics;
- `M07BuildTests.WorkflowRestoresExactProjectSettingsBytesAcrossFreshEditors` validates outer-wrapper and core ownership separately.

Primary reference:

- bounded: **323/323**;
- committed handoff: **11/11**;
- early capsule: **7/7**;
- early launch: **20/20**;
- early results: **20/20**;
- failure pipeline: **16/16**;
- lazy contract: **10/10**.

## V02 / V03 — current provenance/builds

Regenerate the current candidate/reproduction evidence required by H1.

Do not reuse prior source-anchor build acceptance.

## V04.A — fresh current normal M07

Produce a fresh normal profile-2 M07 graph with the current coordinator.

Retain:

- workflow receipt;
- fixture manifest;
- Native ON/OFF receipts;
- Editor replay;
- failure fixtures/Q04 negative input;
- outer recovery/restoration receipts.

Run startup11 and M07 14/14 against this exact graph.

## V04.B — failure/publication strict rerun

Run the dedicated failure/publication launcher and strict verifier against the fresh current graph.

Expected transaction ownership remains `EarliestStartup`.

For Q04 specifically:

- the early transaction must still terminate `Failed` at the intended metadata oracle;
- early first-use history remains immutable;
- post-host first-use history may append **registered candidate** baseline uses because the transaction is already terminal and unpublished;
- unknown/non-candidate identities remain forbidden;
- diagnostics/recovery/capacity must remain the same terminal transaction;
- Control and initializer still require no late physical baseline use in their published worlds.

Require schema-v3 strict verification `Passed`.

A Q04 failure should retain the exact early and post-host baseline-use arrays.

## V04.C — dense-v2 real runtime boundary

Generate a new deterministic dense-v2 adjunct:

~~~text
python3 Tools/AssemblyShadow/create-r01b-dense-fixtures.py \
  --output-root <new-dense-v2-root>
~~~

Run the current parser/native dense validation first.

Build a fresh diagnostic Player and run `run-r01b-lazy-player.py` with the exact fresh v2 manifest.

The Player must resolve:

- `AssemblyShadow.Dense.DenseType_0001_4095_MetadataBoundary_0123456789abcdef0123456789abcdef`;
- `AssemblyShadow.Dense.DenseType_0001_4096_MetadataBoundary_0123456789abcdef0123456789abcdef`;
- corresponding fixture-2 names.

Expected `ReturnId`:

- 14095;
- 14096;
- 24095;
- 24096.

Require:

- `denseFixtures=2`;
- `denseBoundaryChecks=4`;
- all required lazy checks pass;
- capacity accounting remains monotonic;
- no unintended extra interpreter-image allocation beyond the established contract.

## V04.D — current independent retained matrix

Rerun required current-anchor capacity/parser/index/generic/cache/capability/native cells.

The previous passed results are historical comparison only.

## V04.E — graph-bound profile-1 controlled-performance M07

Authenticate the exact protected profile-1 family first.

Then use the **current candidate** coordinator:

~~~text
pwsh -NoProfile -File <candidate>/Tools/AssemblyShadow/Invoke-M07Build.ps1 \
  -ProjectPath <reference-demo> \
  -BaselineId M07-Baseline-H1-Perf-Reference-<unique-id> \
  -TimeoutSec 28800 \
  -BuildTarget StandaloneOSX \
  -ControlledPerformanceBuilds
~~~

Do not invoke the protected historical wrapper.

The workflow receipt must report:

- `controlledPerformanceBuilds=true`;
- fresh NativeOn receipt;
- fresh NativeOff receipt;
- NativeOn controlled evidence;
- NativeOff controlled evidence;
- fixture manifest;
- Editor replay receipt.

All six artifacts must share the same requested profile-1 baseline world.

Require exact outer restoration and post-workflow protected source/runtime verification.

## V04.F — graph-bound profile-2 controlled-performance M07

Run the same current coordinator against the candidate:

~~~text
pwsh -NoProfile -File <candidate>/Tools/AssemblyShadow/Invoke-M07Build.ps1 \
  -ProjectPath <candidate> \
  -BaselineId M07-Baseline-H1-Perf-Current-<unique-id> \
  -TimeoutSec 28800 \
  -BuildTarget StandaloneOSX \
  -ControlledPerformanceBuilds
~~~

Require the same workflow inventory and one internally consistent profile-2 baseline world.

These performance workflows are separate from the normal M07 graph.

## V04.G — old-Player current-anchor check

Use fresh profile-2 and profile-1 graphs to rerun the old-Player rejection contract.

Require the profile-1 Player to admit its own Baseline and reject the incompatible profile-2 input before Configure/Stage.

## V04.H — freeze graph-bound performance map

Use only the two `-ControlledPerformanceBuilds` workflow outputs.

For side A = profile-1 reference and side B = current candidate:

~~~text
python3 Tools/AssemblyShadow/freeze-h1-performance-build-map.py \
  --side-a-project <reference-demo> \
  --side-a-fixture-manifest <reference-workflow.fixtureManifest> \
  --side-a-replay-receipt <reference-workflow.editorReplayReceipt> \
  --side-a-on-receipt <reference-workflow.nativeOnReceipt> \
  --side-a-on-evidence <reference-workflow.nativeOnControlledEvidence> \
  --side-a-off-receipt <reference-workflow.nativeOffReceipt> \
  --side-a-off-evidence <reference-workflow.nativeOffControlledEvidence> \
  --side-b-project <candidate> \
  --side-b-fixture-manifest <candidate-workflow.fixtureManifest> \
  --side-b-replay-receipt <candidate-workflow.editorReplayReceipt> \
  --side-b-on-receipt <candidate-workflow.nativeOnReceipt> \
  --side-b-on-evidence <candidate-workflow.nativeOnControlledEvidence> \
  --side-b-off-receipt <candidate-workflow.nativeOffReceipt> \
  --side-b-off-evidence <candidate-workflow.nativeOffControlledEvidence> \
  --output <new-frozen-build-map.json>
~~~

The freezer must fail if a fixture/replay baseline differs from either controlled Player.

Require `ComparabilityPassed`.

## V04.I — preregistration + all pilots

Bind the preregistered protocol/schedule into a fresh evidence root:

~~~text
python3 Tools/AssemblyShadow/bind-h1-performance-preregistration.py \
  --output-root <new-preregistration-root>
~~~

Use:

- bound protocol;
- bound schedule;
- new frozen build map.

Run every pilot pair via `run-h1-paired-performance.py`.

For each pair use a new output root and increasing `--attempt`. Chain the returned sample index with `--prior-index` as required by the runner.

Do not proceed to formal sampling until all mandatory pilots pass under the unchanged build map/protocol/schedule.

Retain every failed/retried attempt.

## V04.J — formal paired performance

If all pilots pass, execute every formal pair in the preregistered schedule.

Then analyze:

~~~text
python3 Tools/AssemblyShadow/analyze-h1-paired-performance.py \
  --sample-index <final-sample-index.json> \
  --output <new-performance-analysis.json>
~~~

No latency-based deletion, selective retry, schedule edit, build-map edit or manual comparability edit is allowed.

## Retention checkpoint

Before cleanup, authenticate a new Local checkpoint containing or hash-binding:

- fresh V00-V03 evidence;
- normal current M07 + startup/M07 matrix;
- failure/publication early + post-host evidence;
- dense-v2 generator/parser/Player evidence;
- retained current independent matrix;
- both graph-bound controlled-performance workflow receipts;
- four controlled build/evidence pairs;
- old-Player result;
- frozen map + freeze receipt;
- preregistration binding;
- every pilot/formal attempt;
- final performance analysis.

Keep `Passed`, `Failed`, `Blocked`, `Unavailable`, `NotRun`, and historical evidence distinct.

## V05 / M08

Proceed only if mandatory V04 evidence is complete.

Build/authenticate successor evidence and commission a genuinely independent whole-chain M08 review.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**.

Stop for explicit human approval.

Do not begin R02.
