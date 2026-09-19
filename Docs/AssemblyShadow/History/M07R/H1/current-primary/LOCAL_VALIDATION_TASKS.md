# Local Validation Tasks — Early-Owned Failure / Lazy-v2 / Protected M07 Batch

Candidate build-input source anchor:

`99ef65db13341f54cf610e18453dddf197ee86e4`

Latest Local checkpoint:

`7a627afc7d3615430772cd1f5e6978d5106f34c7`

Restart from fresh V00. Previous `4fff4df...` receipts remain historical and must not be relabelled.

The goal is one maximal batch. Hard-stop on authority/provenance/shared-input corruption. After foundations pass, preserve isolated functional failures and continue independent cells when common authenticated inputs remain valid.

## V00 — fresh authority

1. Pull final handoff HEAD.
2. Record checkout HEAD separately from source anchor `99ef65db...`.
3. Require clean tracked state.
4. Run candidate handoff preflight and require `SourceTargetVerifiedNotBuildAccepted`.
5. Require exact candidate source `99ef65db...`.
6. Run reproduction tooling preflight at `ba8fee33753a5ebc215b7a98739e343d8e05572e`.
7. Verify protected reproduction/runtime/package/IL2CPP/performance refs.

Stop on V00 failure.

## V01 — source tests + Unity compile

Run the complete H1 Python inventory and real Unity compilation/EditMode tests.

Focused expectations include:

- `R01EarlyStartupTests` accepts the two continuation-only capsule modes;
- failure pipeline tests cover early-owned transactions + late read-only handoff;
- lazy tests cover four-field deterministic-v2 generator commands;
- M07 workflow-authority tests prove the core uses the coordinator's current verifier.

Primary CI reference will be recorded in `CURRENT_STATUS.md` after final run.

## V02 / V03 — current candidate provenance/builds

Regenerate current-anchor candidate ON/OFF × Debug/Release and reproduction ON Debug/Release evidence.

Do not reuse `4fff4df...` build receipts as current acceptance.

## V04.A — current controlled + normal M07

Run a fresh controlled restoration case and a separate normal M07 baseline through the current candidate coordinator.

Retain:

- workflow receipt;
- fixtures;
- ON/OFF Player receipts;
- editor replay;
- failure fixtures/Q04 negative input;
- restoration receipts.

Keep this graph live through current-candidate V04.

## V04.B — startup11 + M07 14/14

Generate fresh control capsules from the current normal graph.

Run startup11 and M07 14/14 with the matching capsule root.

Require the existing strict gates.

## V04.C — failure/publication with earliest transaction ownership

Run:

~~~text
python3 Tools/AssemblyShadow/run-r01-failure-players.py \
  --project-root <candidate> \
  --fixture-manifest <current-m07-fixtures> \
  --on-build <current-on> \
  --off-build <current-off> \
  --replay-receipt <current-replay> \
  --failure-fixtures <current-failure-fixtures> \
  --negative-input <current-q04-negative-input> \
  --output-root <new-direct-child-of-candidate-_temp/AssemblyShadow>
~~~

Then:

~~~text
python3 Tools/AssemblyShadow/verify-r01-failure-results.py \
  --launch-receipt <failure-output>/r01-failure-launches.json \
  --output <new-strict-verification.json>
~~~

Expected launch schema: 3.

Expected ownership:

| Failure mode | Early mode | Early result | Callback |
| --- | --- | --- | ---: |
| P03 Control | `Control` | `Passed` | 0 |
| Q04 Metadata | `MetadataFailureContinue` | `PassedExpectedFailureContinued` | 0 |
| Initializer | `InitializerFailureContinue` | `PassedExpectedFailureContinued` | 0 |

The early receipt is the authoritative transaction evidence.

The late probe must:

- run in the same PID;
- bind exact early receipt/capsule/current patch bytes;
- perform **no** mutation operations;
- report post-host state:
  - Control → `Committed`;
  - Metadata → `Failed`;
  - Initializer → `FailedAfterCommit`;
- preserve the early final capacity and recovery classification;
- pass strict verifier with `transactionOwnership=EarliestStartup`.

Historical terminal modes `MetadataFailure` and `InitializerFailure` remain callback-1 native startup-termination tests and are not replaced.

If `BaselineAlreadyUsed` appears in the dedicated failure/publication late result, retain exact early receipt + late result/logs and return to Primary.

## V04.D — independent current matrix

Rerun required current-anchor cells, including:

- 8192/8193 capacity;
- exact 512 MiB mixed boundary;
- parser / FieldRVA / bounded reader / sanitizer;
- generic / array / reflection / index / cache / capability;
- retained M03-M07/R01 native/runtime.

Continue independent cells after isolated failures when shared provenance remains intact.

## V04.E — fresh deterministic-v2 lazy Player

Generate fresh dense-v2:

~~~text
python3 Tools/AssemblyShadow/create-r01b-dense-fixtures.py \
  --output-root <new-dense-v2-root>
~~~

Run native/parser dense validation against that exact manifest.

Generate fresh lazy fixture:

~~~text
python3 Tools/AssemblyShadow/create-r01b-lazy-fixture.py \
  --output-root <new-lazy-fixture-root>
~~~

Build a fresh current diagnostic Player through:

`AssemblyShadowDemo.Editor.R01BDiagnosticBuild.BuildDiagnosticPlayer`

with the current M07 fixture manifest and Native-ON receipt.

Then run the exact current CLI:

~~~text
python3 Tools/AssemblyShadow/run-r01b-lazy-player.py \
  --project-root <candidate> \
  --fixture-manifest <current-m07-fixtures> \
  --on-build <current-on> \
  --off-build <current-off> \
  --replay-receipt <current-replay> \
  --diagnostic-build <fresh-r01b-diagnostic-build-receipt> \
  --lazy-fixture-receipt <new-lazy-fixture-root>/r01b-lazy-fixture-receipt.json \
  --dense-manifest <new-dense-v2-root>/workload-v3-dense-adjunct-v2.json \
  --output-root <new-direct-child-of-candidate-_temp/AssemblyShadow>
~~~

Require the v2 producer command inventory to bind four fields per command:

`mono / generator exe / fixture id / output DLL`

in order 1/run1, 1/run2, 2/run1, 2/run2.

Then require real lazy Player success and unchanged input hashes.

Do not reconstruct sealed-v1 evidence.

## V04.F — authenticate protected profile-1 family

Use the exact isolated reference family:

- demo HEAD `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c`;
- demo source anchor `f1c923cbaa814e1b63f3c5b9f8303c90616de726`;
- HybridCLR `b22fa3d92223645c32663e4a2157eaadf8ea495e`;
- HybridCLR Unity `b649c499385ea68490a0f652a98b732e060aeb89`;
- IL2CPP `7967b8c7043904fcae130b294defd5ce7aa897c4`.

Run current candidate:

~~~text
python3 <candidate>/Tools/AssemblyShadow/verify-h1-protected-reference.py \
  --reference-demo <reference-demo> \
  --reference-hybridclr <reference-hybridclr> \
  --reference-hybridclr-unity <reference-hybridclr-unity> \
  --reference-il2cpp-plus <reference-il2cpp-plus> \
  --candidate-demo <candidate> \
  --output <new-reference-verification.json>
~~~

Require `ProtectedReferenceInputsVerifiedNotBuilt`.

Require the already-installed profile-1 runtime through the **current candidate verifier**:

~~~text
python3 <candidate>/Tools/AssemblyShadow/verify-installed-runtime.py \
  --project <reference-demo> --expect-shadow on --json
~~~

## V04.G — protected profile-1 M07 using current coordinator

Do **not** invoke the protected project's historical `Invoke-M07Build.ps1`.

Invoke the current candidate coordinator against the protected project:

~~~text
pwsh -NoProfile -File <candidate>/Tools/AssemblyShadow/Invoke-M07Build.ps1 \
  -ProjectPath <reference-demo> \
  -BaselineId M07-Baseline-H1-ProtectedProfile1-<unique-id> \
  -TimeoutSec 28800 \
  -BuildTarget StandaloneOSX
~~~

The coordinator must:

1. fully verify protected source/runtime before mutation;
2. snapshot the exact three workflow-owned tracked paths;
3. run protected `M07Build.ValidateCompilerInputs`;
4. after mutation use current split authority:
   - installed runtime/package/native verified;
   - `h1_m07_workflow_authority` verifies exact originals + requested baseline;
5. build reference resources / Native ON / Native OFF;
6. perform structural Prepare/Compile/Restore/Finalize;
7. restore exact tracked bytes on outer completion;
8. leave a fresh reference fixture/ON/OFF/replay graph;
9. finish with protected source/runtime verification passing again.

Retain outer recovery/authority receipts.

A failure from the protected project's **historical verifier** indicates the wrong coordinator was invoked.

## V04.H — old-Player rejection

Once the fresh protected profile-1 graph exists, run current:

~~~text
python3 Tools/AssemblyShadow/run-r01b-old-player-rejection.py \
  --project-root <candidate> \
  --fixture-manifest <current-fixtures> \
  --on-build <current-on> \
  --off-build <current-off> \
  --replay-receipt <current-replay> \
  --old-fixture-manifest <reference-fixtures> \
  --old-on-build <reference-on> \
  --old-off-build <reference-off> \
  --old-replay-receipt <reference-replay> \
  --output-root <new-old-player-output>
~~~

Require profile-1 Baseline early admission and expected pre-Configure identity refusal of profile-2 current inputs.

## V04.I — controlled Development A/B performance

Build fresh controlled ON/OFF Development Players in both projects through each project's own:

`AssemblyShadowDemo.Editor.R00ControlledBuild.BuildPlayer`

Use fresh outputs/evidence.

Freeze the strict A/B map using:

`Tools/AssemblyShadow/freeze-h1-performance-build-map.py`

Require `ComparabilityPassed`.

Bind the preregistration into a fresh evidence root using:

`Tools/AssemblyShadow/bind-h1-performance-preregistration.py`

Require:

- protocol bytes unchanged;
- schedule semantic fields unchanged;
- 44 pairs;
- only protocol path/hash transport fields changed.

Run pilot pairs first, then formal pairs only under existing source-freeze/pilot rules.

Retain all attempts and analyze with `analyze-h1-paired-performance.py`.

## Retention checkpoint

Before any cleanup, authenticate a new checkpoint containing/hash-binding:

- V00-V03 current evidence;
- current controlled/normal M07;
- startup11 / M07 14/14;
- three early failure transaction capsules/receipts + late handoff results/raw files;
- dense-v2/parser/lazy fixture/diagnostic Player/lazy result;
- protected family verification/install;
- protected outer recovery + fresh M07 graph;
- old-Player rejection;
- four controlled Development build receipts/evidence;
- frozen build map;
- preregistration binding;
- every performance attempt + analysis.

Missing evidence remains `Unavailable`; failed evidence remains `Failed`.

## V05 / M08

Proceed only if mandatory V04 prerequisites are complete.

Build/authenticate successor evidence and commission a genuine independent whole-chain M08.

Only genuine **M08 PASS** may make H1 Ready for Human Review Gate.

Then stop for explicit human approval.

Do not begin R02.
