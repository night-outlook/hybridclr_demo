# Local Validation Tasks — Formal Side-B Subprocess Authority Closure

Candidate source/tool anchor:

`24a0d3af7d5b5b664d063a75d85deb4f11aa2915`

Latest Local return:

`d18a1fb15c43f918c9d3bba1ed641e87a58b32b0`

Latest authenticated Local checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authoritya964-formal-launch-blocked/`

Retained graph/pilot checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/`

H1 remains `InProgress`. Do not begin R02.

## Goal

Close the fresh formal candidate subprocess boundary returned by Local, then complete the remaining H1 performance chain in one batch when each gate passes:

fresh authority/tests → exact 11-path Primary delta audit → exact 20-path retained-graph audit → retained evidence reauthentication → new graph bridge → new 8-side strict pilot seal → new formal series from the retained pilot index → first-pair subprocess-authority proof → all 40 formal pairs → final strict analysis → checkpoint → V05 / independent M08 if eligible.

The two failed `a964f79d...` formal attempts are historical evidence only. Do not chain them into the new current-source sample series.

## V00 — fresh current authority

1. Pull final pushed `codex/assembly-shadow-r01b-h1`.
2. Require clean tracked state.
3. Record checkout HEAD separately from source/tool anchor `24a0d3af7d5b5b664d063a75d85deb4f11aa2915`.
4. Run committed candidate handoff/source preflight and require `SourceTargetVerifiedNotBuildAccepted`.
5. Reauthenticate reproduction tooling and the exact protected profile-1 family.
6. If candidate installed-runtime receipt still binds the prior demo revision, refresh it through:
   `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability`.
7. Verify candidate installed runtime with Shadow ON and full demo-source authority.
8. Verify protected installed runtime with Shadow ON.
9. Retain exact install/runtime receipt hashes.

Do not create the graph bridge until V00/V01/V01A/V02 are complete.

After bridge creation, do not reinstall or regenerate candidate source/runtime inputs unless the bridge and any later seal are discarded and recreated.

## V01 — current Primary regressions

Run the complete current bounded Primary suite and live handoff preflight.

Current focused source/tool areas include:

- `test_h1_formal_launch_authority.py`;
- `test_h1_graph_reuse.py`;
- `test_h1_paired_driver.py`;
- `test_h1_formal_batch.py`;
- `test_h1_retained_early_preflight.py`;
- all existing R01/lazy/M07 recovery regressions.

The final committed Primary validation result in `source-targets.json` is authoritative.

### Full Python inventory

Because Python execution tooling changed, run complete Python discovery again.

Require:

- zero failure/error;
- all skips explicit and environment-bound;
- preserve the full inventory/log.

The previously observed 28 environment skips are not Passed evidence.

### Unity EditMode

The source delta from `a964f79d...` changes no Assets/Packages/C#/asmdef/resource input.

Therefore the fresh 1076/1076 Unity result from Local commit `d18a1fb...` may be retained only as:

`ReusedAuditedFromD18`

after V01A proves the exact source scope.

A new full Unity run is optional before bridge creation. If run, retain it as fresh evidence.

Do not label the prior result as fresh current-source execution.

## V01A — exact source audits

### A. Previous Primary source → current source

Compare:

`a964f79d6ceba866c5956741a4a32e38ff8a6b5f`

to:

`24a0d3af7d5b5b664d063a75d85deb4f11aa2915`

After metadata-only classification, the exact non-metadata set must contain **11 paths**:

1. `.github/workflows/h1-bee-primary.yml`
2. `Tools/AssemblyShadow/README.md`
3. `Tools/AssemblyShadow/analyze-h1-paired-performance.py`
4. `Tools/AssemblyShadow/h1_bee_primary_tests.py`
5. `Tools/AssemblyShadow/h1_formal_launch_authority.py`
6. `Tools/AssemblyShadow/h1_graph_reuse.py`
7. `Tools/AssemblyShadow/run-h1-paired-performance.py`
8. `Tools/AssemblyShadow/run-r00-players.py`
9. `Tools/AssemblyShadow/tests/test_h1_formal_launch_authority.py`
10. `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`
11. `Tools/AssemblyShadow/tests/test_h1_paired_driver.py`

This audit is the basis for `ReusedAuditedFromD18` classification of the prior Unity result and prior retained-ON preflight semantics.

### B. Retained graph anchor → current source

Compare:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3`

to:

`24a0d3af7d5b5b664d063a75d85deb4f11aa2915`

After metadata-only classification, the complete set must equal exactly these **20 paths**:

1. `.github/workflows/h1-bee-primary.yml`
2. `Tools/AssemblyShadow/README.md`
3. `Tools/AssemblyShadow/analyze-h1-paired-performance.py`
4. `Tools/AssemblyShadow/create-h1-graph-reuse-bridge.py`
5. `Tools/AssemblyShadow/h1_bee_primary_tests.py`
6. `Tools/AssemblyShadow/h1_formal_launch_authority.py`
7. `Tools/AssemblyShadow/h1_graph_reuse.py`
8. `Tools/AssemblyShadow/r00_player_inputs.py`
9. `Tools/AssemblyShadow/r00_results.py`
10. `Tools/AssemblyShadow/r01_early_results.py`
11. `Tools/AssemblyShadow/run-h1-formal-batch.py`
12. `Tools/AssemblyShadow/run-h1-paired-performance.py`
13. `Tools/AssemblyShadow/run-r00-players.py`
14. `Tools/AssemblyShadow/seal-h1-pilot-verification.py`
15. `Tools/AssemblyShadow/tests/test_h1_formal_batch.py`
16. `Tools/AssemblyShadow/tests/test_h1_formal_launch_authority.py`
17. `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`
18. `Tools/AssemblyShadow/tests/test_h1_paired_driver.py`
19. `Tools/AssemblyShadow/tests/test_h1_retained_early_preflight.py`
20. `Tools/AssemblyShadow/verify-h1-retained-early-reuse.py`

Require no changed path under:

- `Assets/`;
- `Packages/`;
- Unity C#/asmdef/resource/measurement source;
- HybridCLR native;
- HybridCLR Unity;
- IL2CPP;
- protocol or schedule JSON;
- graph/build-map producer;
- preregistration producer;
- Player binary source.

A subset or superset fails. Do not edit the allowlist locally.

## V02 — retained evidence reauthentication

Before bridge creation, verify:

- retained V04 `MANIFEST.sha256`;
- `PLAYER_ARTIFACTS.sha256`;
- latest `authoritya964-formal-launch-blocked` checkpoint manifest;
- protected/current controlled graph receipts and evidence;
- frozen build map + freeze receipt;
- preregistration binding;
- bound protocol and schedule;
- complete retained pilot index, including retained pilot failure/retry;
- all eight selected pilot launch receipts;
- complete bound-file inventory.

Historical evidence to retain but **not reuse as current authority**:

- a964 bridge SHA `b6e97f573938757d712c632a765fb58b8cb82ff9e360733158de998f980a25e0`;
- a964 seal SHA `5dc313824e9b034475a4d6f105b5d29801ef796f1553881d8b3b3699f9f65935`;
- formal pair `R00-OFF-NoPatch-formal-01` attempts 1 and 2 from the a964 series.

Those attempts must never be copied into the new source series.

## V04.R — create new current-source graph bridge

Create a **new** bridge:

~~~text
python3 Tools/AssemblyShadow/create-h1-graph-reuse-bridge.py \
  --project <candidate> \
  --build-map <retained-live-frozen-build-map.json> \
  --output <new-graph-reuse-bridge.json>
~~~

Require:

- `kind=H1GraphReuseBridge`;
- `status=AuthenticatedToolOnlySuccessor`;
- side B only;
- retained graph revision exactly `69130bbb...`;
- current demo revision exactly `24a0d3af7d5b5b664d063a75d85deb4f11aa2915`;
- exact 20-path transition;
- current installed-runtime binding;
- exact map/source/verifier bindings;
- verifier bindings include the formal authority module and `run-r00-players.py`.

If bridge creation fails, return to Primary.

## V04.S — create new strict pilot seal

Create a **new** seal using the new bridge:

~~~text
python3 Tools/AssemblyShadow/seal-h1-pilot-verification.py \
  --protocol <bound-protocol> \
  --schedule <bound-schedule> \
  --build-map <retained-live-frozen-build-map.json> \
  --pilot-index <retained-live-pilot-index.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --output <new-pilot-verification.json>
~~~

Require:

- `PassedStrictReconstructionAndStatGuardSealed`;
- `deepLaunchVerificationCount=8`;
- exact new bridge binding;
- stable immutable file guards;
- all four latest successful pilots;
- retained complete pilot-attempt digest.

### Retained-ON preflight classification

The a964 3-mode retained-ON preflight already passed after the nested-authority fix.

The current 11-path delta does not change:

- `r00_results.py`;
- `r01_early_results.py`;
- `verify-h1-retained-early-reuse.py`.

A standalone new 3-mode preflight is therefore **not mandatory** this cycle.

Record the prior result only as:

`ReusedAuditedFromD18`

after V01A passes.

The fresh 8-side seal is mandatory and provides new current-bridge strict reconstruction evidence.

If the seal fails, preserve it and return to Primary. Do not start formal sampling.

## V04.T — start a new formal series from the retained pilot index

Do **not** use either a964 failed formal sample index as `--prior-index`.

Start the new source series from the retained live pilot index:

~~~text
python3 Tools/AssemblyShadow/run-h1-formal-batch.py \
  --protocol <bound-protocol> \
  --schedule <bound-schedule> \
  --build-map <retained-live-frozen-build-map.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --pilot-verification-receipt <new-pilot-verification.json> \
  --prior-index <retained-live-pilot-index.json> \
  --output-root <new-formal-batch-root> \
  --timeout 900
~~~

### First new formal pair is a mandatory focused gate

Inspect pair `R00-OFF-NoPatch-formal-01` attempt 1 before treating batch continuation as accepted evidence.

Protected side A must:

- have `formalLaunchAuthority = null`;
- use default current-pairing execution;
- produce a passed R00 launch when otherwise valid.

Candidate side B must have a parent-issued authority receipt with:

- `kind=H1FormalSideLaunchAuthority`;
- `status=AuthenticatedRetainedCandidateFormalLaunch`;
- `side=B`;
- pairId exactly `R00-OFF-NoPatch-formal-01`;
- attempt `1`;
- exact mode and pair order;
- exact candidate project;
- exact runner output root;
- exact protocol/schedule/map bindings;
- exact new bridge and seal bindings;
- exact fixture/on/off/replay bindings;
- current tool bindings.

The child must:

- consume `--h1-formal-launch-authority`;
- revalidate that receipt;
- enter `verify_inputs_with_reuse`, not default `verify_inputs`;
- pass retained graph preparation;
- actually launch the candidate Player;
- produce a real `r00-player-launches.json`;
- echo the exact same formal authority binding;
- echo the same graph bridge, pilot seal, and build map;
- retain source pins for the retained graph;
- complete the selected mode normally.

The prior error:

`R00 baseline: source pins differ from baseline provenance`

must not recur at candidate side-B preparation.

If candidate B again fails before Player launch, stop the new series and return to Primary with the authority receipt, child console, command, and source-pairing traceback.

### Continue all formal pairs

If pair 1 passes, allow the same batch to continue.

Full success requires:

- `status=PassedAllFormalPairs`;
- `formalPairCount=40`;
- `formalPairsPassed=40`;
- all formal attempts bind the same current bridge and seal;
- every actual candidate side-B formal attempt carries a hash-valid formal launch authority;
- every passed candidate R00 receipt echoes that authority;
- protected side A never carries one;
- preregistered pair order remains unchanged.

### Whole-pair failure/retry

The batch stops on the first failed whole pair.

Retain:

- failed batch receipt;
- failed cumulative sample index;
- side A/B diagnostics;
- side-B formal authority receipt, even if no R00 receipt exists;
- process cleanup evidence.

Only if the unchanged protocol permits retry:

1. retry exactly the same pair;
2. use failed cumulative index as prior;
3. increment attempt number;
4. use same current bridge/seal;
5. retain the failed attempt;
6. resume with a new batch root only after the retry passes.

No side-only retry, skip, auto-retry, or sample deletion.

## V04.U — final strict analysis

After all 40 formal pairs have a selected valid attempt:

~~~text
python3 Tools/AssemblyShadow/analyze-h1-paired-performance.py \
  --sample-index <final-sample-index.json> \
  --pilot-verification-receipt <new-pilot-verification.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --output <new-performance-analysis.json>
~~~

Require final analysis to:

- full-reauthenticate the bridge;
- reverify all formal side-B authority receipts;
- bind each authority to its pairId/attempt/mode/order/output/input/map/bridge/seal/tool identity;
- require side A to have no retained authority;
- accept failed pre-launch side-B authority evidence without fabricating launch evidence;
- require successful candidate launch receipts to echo the same authority;
- perform original strict launch/raw/result verification;
- retain all valid and failed/retried attempts;
- report 10 formal pairs/mode.

Retain the complete result even if performance/comparability is unfavorable.

## Checkpoint / V05 / M08

Before cleanup, authenticate a new checkpoint containing:

- V00 authority;
- current Python inventory;
- Unity fresh result or `ReusedAuditedFromD18` classification;
- exact 11/20 source audits;
- retained evidence audit;
- new bridge;
- new seal;
- formal side authority receipts;
- every batch / retry;
- final cumulative sample index;
- final analysis;
- links/hashes to all historical failed cycles.

Only after mandatory V04 is complete and internally consistent may Local prepare V05 and commission a genuinely independent M08 review.

M08 must explicitly review:

- the formal subprocess authority design;
- side-B-only authority isolation;
- output-root replay protection;
- first-pair empirical subprocess proof;
- retry authority retention;
- final analyzer authority verification;
- all prior bridge/seal/cache evidence.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**.

Stop for explicit human approval.

**Do not begin R02.**

## Local correction boundary

Local may adjust only:

- absolute paths;
- new evidence/output roots;
- executable permissions / PYTHONPATH;
- bounded command syntax;
- explicit protocol-valid whole-pair retry number.

Local must not modify:

- formal authority schema or tool binding set;
- internal child authority flag semantics;
- graph-reuse policy/20-path allowlist;
- source/runtime/protected pins;
- default R00 current-pairing behavior;
- bridge/seal/map/protocol/schedule identities;
- pair ordering/retry/statistics;
- final analyzer logic.

Any non-trivial source/tool correction returns to Primary.
