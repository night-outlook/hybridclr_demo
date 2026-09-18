# Local Validation Tasks — H1 Failure/Publication Early Admission

Candidate build-input source anchor:

`50c79913096961636a776ee8254b6631002cdfe5`

The goal of this cycle is to obtain as much fresh H1 evidence as safely possible in one batch. A source/provenance/build-identity failure stops the batch. After those foundations pass, an isolated functional failure in one fresh-process downstream test does **not** automatically prevent running other independent downstream tests; preserve the failure and continue where the same authenticated inputs remain valid. V05 still requires all mandatory acceptance prerequisites.

## V00 — authority

1. Pull the final handoff branch and record checkout HEAD separately from source anchor `50c79913096961636a776ee8254b6631002cdfe5`.
2. Run candidate `h1_handoff_preflight.py`; require `SourceTargetVerifiedNotBuildAccepted` and exact `codeCommit=50c79913...`.
3. Run reproduction-tooling preflight at exact `ba8fee33753a5ebc215b7a98739e343d8e05572e`.
4. Verify protected reproduction/native/package/IL2CPP/performance refs remain exact.
5. Confirm `ProjectSettings/AssemblyShadowSourcePins.json` and `source-targets.json` both identify `50c79913...`.
6. Require clean tracked state before builds.

Stop on any V00 failure. Do not change source authority or metadata-only rules locally.

## V01 — source/tests/Unity compilation

Run the complete H1 Python inventory and affected focused source/tool tests.

At minimum confirm the Primary repair suites:

- `test_r01_early_capsule.py`;
- `test_r01_early_results.py`;
- `test_r01_failure_pipeline.py`;
- source-authority/preflight regressions.

Primary CI reference at the exact source anchor is workflow `35330989089`: 311/311 + 7/7 + 19/19 + 16/16.

Compile the candidate and reproduction-tooling Unity projects with Unity 2022.3.62f2 as required by the existing H1 matrix. Retain logs and NUnit XML. Primary CI is not a substitute for real Unity compilation.

## V02 — fresh candidate provenance

Produce a fresh candidate ON/Debug provenance proof under source anchor `50c79913...`.

Require the existing strict native compiler/PCH/store/managed-source/current-Player bindings and exact restoration. Do not relabel `8b1298d...` build receipts as current.

## V03 — fresh build set

Produce the current required candidate ON/OFF × Debug/Release and reproduction ON Debug/Release set with exact tooling/source bindings.

Preserve every accepted build receipt and associated compiler/managed provenance artifacts.

## V04.A — controlled M07 authority/recovery

Run a new controlled M07 baseline.

Require:

- full pre-mutation source/runtime authority;
- real `ValidateCompilerInputs`;
- post-mutation exact M07 authority;
- the exact expected controlled failure only after that authority passes;
- three-file exact restoration;
- post-recovery candidate preflight.

Stop and return to Primary if a new tracked build input needs mutation or if authority/provenance differs.

## V04.B — fresh normal M07

Use a distinct new baseline and run normal `Invoke-M07Build.ps1`.

Require:

- baseline resources;
- Native-ON Player;
- Native-OFF Player;
- generated-link exact restoration;
- structural prepare/compile/restore;
- fixture finalization;
- Editor replay;
- successful `m07-build-workflow.json`.

Keep the generated fixture/build/replay set live for all following tests.

## V04.C — startup and M07 matrix

Using those exact current-anchor receipts:

1. generate current control capsules;
2. run startup11 and strict startup verification;
3. run the complete M07 14-mode Player matrix with the matching early-capsule root.

Require the existing strict acceptance or record the exact isolated failure.

## V04.D — repaired failure/publication matrix

Generate the current failure-fixture and Q04 negative-input receipts from the same fresh M07 chain, then run:

~~~text
python3 Tools/AssemblyShadow/run-r01-failure-players.py   --project-root <candidate-root>   --fixture-manifest <m07-fixtures.json>   --on-build <native-on-m07-player-build.json>   --off-build <native-off-m07-player-build.json>   --replay-receipt <m07-editor-replay.json>   --failure-fixtures <r01-failure-fixtures.json>   --negative-input <q04-negative-input.json>   --output-root <new-direct-child-of-_temp/AssemblyShadow>
~~~

Then run the public verifier directly:

~~~text
python3 Tools/AssemblyShadow/verify-r01-failure-results.py   --launch-receipt <failure-output>/r01-failure-launches.json   --output <new-strict-verification.json>
~~~

Require all three fresh processes:

- `R01-Failure-P03-Control`;
- `R01-Failure-Q04-Metadata`;
- `R01-Failure-InitializerThrow`.

For every mode require:

- a distinct `R01FailureEarlyAdmissionBinding`;
- distinct Baseline admission capsule;
- early receipt `Passed`, callbackReturnCode=0, same PID and exact capsule hash;
- exact immutable input before/after hashes;
- exact late failure/publication result from the same PID;
- strict verification result `Passed`.

The Baseline early capsule is intentionally admission-only and must not consume a Shadow transaction.

On failure preserve binding, capsule, early receipt, late result, command, PID/start, console and Unity logs. Do not disable the early callback or substitute an early Control/failure capsule.

## V04.E — maximize independent downstream coverage

If V00–V04.B provenance remains valid, continue independent fresh-process validations even if one V04.C/D functional test fails, unless that failure indicates corrupted shared inputs or unsafe global source state.

Run all still-required independent cells, including:

- 8192/8193 capacity and mixed boundary;
- lazy/dense;
- generic/array/reflection/FieldRVA;
- immutable old-Player rejection;
- retained M03–M07 native/runtime coverage;
- controlled Development performance against protected reference `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c`.

Keep `Passed`, `Failed`, `Blocked`, `Unavailable`, `NotRun`, and `NoCoverage` distinct.

## Retention checkpoint — before cleanup

Before deleting, moving, consolidating, or regenerating any relevant `_temp`, `Builds`, Player, resource, fixture, capsule, replay, failure, or performance directories, create and authenticate the Local checkpoint.

Retain or hash-bind the complete current-anchor graph, including:

- V00 authority outputs;
- current source pins;
- V02/V03 build/provenance receipts;
- controlled M07 mutation/restoration evidence;
- normal `m07-build-workflow.json`;
- `m07-fixtures.json`;
- Native-ON/OFF `m07-player-build.json`;
- `m07-editor-replay.json`;
- control capsules/startup11 artifacts;
- M07 14-mode launch/results;
- failure-fixture and Q04 negative-input receipts;
- three failure-mode admission bindings/capsules/early receipts/late results/logs;
- capacity/lazy/dense/retained coverage/performance outputs.

A missing required artifact is `Unavailable`; do not reconstruct acceptance from summaries.

## V05 — successor + independent whole-chain M08

Only after mandatory V04 requirements are complete:

1. build and authenticate the successor evidence package;
2. preserve all historical evidence under original identities;
3. commission a genuinely independent design → source → builds → raw-evidence whole-chain M08 review.

Only genuine independent whole-chain **M08 PASS** may make H1 Ready for Human Review Gate.

Then stop for explicit human approval. Do not begin R02.
