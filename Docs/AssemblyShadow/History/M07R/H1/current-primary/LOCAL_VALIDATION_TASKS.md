# Local Validation Tasks — Retained Pilot Runner Admission Closure

Candidate source/tool anchor:

`91ac4db31cec704551c7db05bd918c8d5695ce83`

Latest Local return:

`65f47f6bf62fe8889a3b71ed629f9fd06f3a489a`

Latest blocked checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority24a0-pilot-seal-blocked/`

Retained graph/pilot checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/`

H1 remains `InProgress`. Do not begin R02.

## Goal

Close the retained historical pilot-runner admission defect before paying the full seal cost, then continue the complete H1 performance chain in one Local cycle if every gate passes:

fresh authority/tests → exact 9-path Primary delta audit → exact 22-path retained-graph audit → retained evidence reauthentication → new graph bridge → retained-pilot admission preflight → new 8-side strict seal → new formal series from retained pilot index → all 40 formal pairs → final strict analysis → checkpoint → V05 / independent M08 if eligible.

All prior bridges, seals, failed formal attempts, and blocked checkpoints remain historical evidence only.

## V00 — fresh current authority

1. Pull final pushed `codex/assembly-shadow-r01b-h1`.
2. Require clean tracked state.
3. Record checkout HEAD separately from source/tool anchor `91ac4db31cec704551c7db05bd918c8d5695ce83`.
4. Run live handoff/source preflight and require `SourceTargetVerifiedNotBuildAccepted`.
5. Reauthenticate reproduction tooling and exact protected profile-1 family.
6. If the candidate installed-runtime receipt still binds the previous demo revision, refresh it through:
   `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability`.
7. Verify candidate installed runtime with Shadow ON and full demo-source authority.
8. Verify protected installed runtime with Shadow ON.
9. Retain exact receipt hashes.

Do not create the graph bridge until V00/V01/V01A/V02 are complete.

After bridge creation, do not reinstall or regenerate source/runtime inputs unless the bridge and any later seal are discarded and recreated.

## V01 — current Primary regressions

Run:

- complete bounded Primary suite;
- committed live-handoff preflight;
- direct `test_h1_retained_pilot_runner.py`;
- direct graph-reuse/paired-driver/formal-authority/formal-batch suites;
- existing R01 early/failure/lazy suites;
- both M07 PowerShell recovery regressions.

The final committed Primary result in `source-targets.json` is authoritative.

### Full Python inventory

Run complete Python discovery because Python tooling changed.

Require:

- zero failure/error;
- every skip explicit and environment-bound;
- full inventory/log retained.

Prior environment skips are not Passed evidence.

### Unity EditMode

The current source delta changes no Assets/Packages/C#/asmdef/resource input.

The historical 1076/1076 result from the D18 cycle may be retained only as:

`ReusedAuditedFromD18`

after the exact 9-path audit passes.

A fresh broad Unity run is optional before bridge creation.

Do not call reused evidence fresh current-source execution.

## V01A — exact source audits

### A. Previous Primary source → current source

Compare:

`24a0d3af7d5b5b664d063a75d85deb4f11aa2915`

to:

`91ac4db31cec704551c7db05bd918c8d5695ce83`

After metadata-only classification, the exact non-metadata set must equal these **9 paths**:

1. `.github/workflows/h1-bee-primary.yml`
2. `Tools/AssemblyShadow/README.md`
3. `Tools/AssemblyShadow/h1_bee_primary_tests.py`
4. `Tools/AssemblyShadow/h1_graph_reuse.py`
5. `Tools/AssemblyShadow/run-h1-paired-performance.py`
6. `Tools/AssemblyShadow/seal-h1-pilot-verification.py`
7. `Tools/AssemblyShadow/tests/test_h1_paired_driver.py`
8. `Tools/AssemblyShadow/tests/test_h1_retained_pilot_runner.py`
9. `Tools/AssemblyShadow/verify-h1-retained-pilot-admission.py`

### B. Retained graph anchor → current source

Compare:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3`

to:

`91ac4db31cec704551c7db05bd918c8d5695ce83`

After metadata-only classification, the complete set must equal exactly these **22 paths**:

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
20. `Tools/AssemblyShadow/tests/test_h1_retained_pilot_runner.py`
21. `Tools/AssemblyShadow/verify-h1-retained-early-reuse.py`
22. `Tools/AssemblyShadow/verify-h1-retained-pilot-admission.py`

Require no changed path under:

- `Assets/`;
- `Packages/`;
- Unity C#/asmdef/resource/measurement source;
- HybridCLR native;
- HybridCLR Unity;
- IL2CPP;
- protocol/schedule JSON;
- graph/build-map producer;
- preregistration producer;
- Player binary source.

A subset or superset fails. Do not edit the allowlist locally.

## V02 — retained evidence reauthentication

Before bridge creation, verify:

- retained V04 `MANIFEST.sha256`;
- `PLAYER_ARTIFACTS.sha256`;
- latest `authority24a0-pilot-seal-blocked` checkpoint manifest;
- all earlier blocked-checkpoint links/hashes;
- protected/current controlled graph receipts/evidence;
- frozen build map + freeze receipt;
- preregistration binding;
- bound protocol and schedule;
- complete retained pilot attempt history;
- all eight selected pilot launch receipts;
- complete bound-file inventory.

The retained pilot index must remain byte-identical to authenticated historical evidence.

Historical runner provenance expected from that index:

- path: canonical current candidate path to `Tools/AssemblyShadow/run-r00-players.py`;
- SHA-256: `afc0b649579ebd497be493be9fd39fcfe19e3ba3074d6d6679e009975d21a07c`.

Do not edit that historical binding to the current runner hash.

## V04.V — create new graph bridge

Create a **new** current-source bridge:

~~~text
python3 Tools/AssemblyShadow/create-h1-graph-reuse-bridge.py \
  --project <candidate> \
  --build-map <retained-live-frozen-build-map.json> \
  --output <new-graph-reuse-bridge.json>
~~~

Require:

- `kind=H1GraphReuseBridge`;
- `status=AuthenticatedToolOnlySuccessor`;
- `side=B`;
- retained graph revision exactly `69130bbb...`;
- current demo revision exactly `91ac4db31cec704551c7db05bd918c8d5695ce83`;
- exact 22-path transition;
- current installed-runtime binding;
- exact frozen-map/current-verifier bindings;
- `retainedPilotRunner.path` equals the canonical candidate `Tools/AssemblyShadow/run-r00-players.py`;
- `retainedPilotRunner.sha256` equals:
  `afc0b649579ebd497be493be9fd39fcfe19e3ba3074d6d6679e009975d21a07c`.

Independently confirm the current runner hash differs and is bound through current verifier/formal execution contracts.

If the bridge lacks or mismatches retained pilot runner provenance, stop and return to Primary.

## V04.W — retained pilot admission preflight

Run **before** the expensive seal:

~~~text
python3 Tools/AssemblyShadow/verify-h1-retained-pilot-admission.py \
  --protocol <bound-protocol> \
  --schedule <bound-schedule> \
  --build-map <retained-live-frozen-build-map.json> \
  --pilot-index <retained-live-pilot-index.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --output <new-retained-pilot-admission.json>
~~~

Require:

- `schemaVersion=1`;
- `kind=H1RetainedPilotAdmissionPreflight`;
- `result=Passed`;
- exact protocol/schedule/map/pilot/bridge bindings;
- `retainedPilotRunner` equals the bridge's Git-derived historical runner;
- `pilotAttemptCount=5` for the retained authoritative pilot history;
- `selectedPilotCount=4`;
- exactly one latest Passed selected pilot for every R00 mode;
- both A and B runner bindings in every selected pilot equal the same historical retained runner;
- all selected launch receipt bindings remain exact;
- no deep R00 verification or graph reconstruction is performed;
- no retained file is modified.

This is the direct empirical closure of the returned `Prior A diagnostic runner binding mismatch`.

If V04.W fails, **do not run the seal**. Preserve the receipt/failure and return to Primary.

## V04.X — create new strict 8-side pilot seal

Only after V04.W passes:

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

- `kind=H1PilotVerificationReceipt`;
- `status=PassedStrictReconstructionAndStatGuardSealed`;
- exact new bridge binding;
- `deepLaunchVerificationCount=8`;
- full five-attempt pilot digest;
- four selected Passed pilots;
- stable complete immutable file/stat inventory;
- candidate side B uses bridge-aware retained graph authority;
- protected side A remains graph-default/current-pairing for graph verification;
- historical runner provenance is accepted only as the pilot diagnostic runner binding;
- no formal execution has started.

The seal must supersede, not overwrite, every historical seal/failure.

### Retained-ON early preflight

The D18 3-mode retained-ON preflight may remain `ReusedAuditedFromD18` because the current 9-path delta does not change `r00_results.py`, `r01_early_results.py`, or `verify-h1-retained-early-reuse.py`.

The new 8-side seal is nevertheless mandatory and freshly re-verifies those retained launches.

## V04.Y — start a new formal series

Only after V04.X passes.

Do **not** use any historical formal index from a964 or later blocked cycles.

Start from the retained pilot index:

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

### First pair focused gate

For `R00-OFF-NoPatch-formal-01` attempt 1:

Protected A:

- no `formalLaunchAuthority`;
- current runner;
- default current-pairing path;
- normal Passed launch when otherwise valid.

Candidate B:

- current runner binding, **not** historical pilot runner;
- new `H1FormalSideLaunchAuthority`;
- exact pair/attempt/mode/order/project/output binding;
- exact bridge/seal/map/input/tool binding;
- child consumes `--h1-formal-launch-authority`;
- child enters `verify_inputs_with_reuse`;
- candidate Player actually launches;
- real R00 launch receipt is emitted;
- receipt echoes the exact formal authority, bridge, seal, and map.

The historical pilot runner exception must not leak into new formal runner identity.

If pair 1 fails before candidate Player launch, stop and return to Primary with the full authority/child diagnostic.

### Complete all 40 formal pairs

If pair 1 passes, continue the same batch.

Require:

- `PassedAllFormalPairs`;
- 40/40 formal pairs Passed;
- every actual candidate formal attempt uses current runner + unique valid formal authority;
- protected A never carries retained authority;
- current bridge/seal remain unchanged;
- preregistered ordering and retry policy remain unchanged.

### Retry

On whole-pair failure, preserve the failed attempt and its authority.

Retry exactly the same pair only when the preregistered policy permits it; increment attempt number and retain both attempts.

No side-only retry, skip, auto-retry, or sample deletion.

## V04.Z — final strict analysis

After 40 selected valid formal pairs:

~~~text
python3 Tools/AssemblyShadow/analyze-h1-paired-performance.py \
  --sample-index <final-sample-index.json> \
  --pilot-verification-receipt <new-pilot-verification.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --output <new-performance-analysis.json>
~~~

Require:

- full bridge reauthentication;
- formal authority verification for every candidate formal attempt;
- current runner/formal authority for new formal execution;
- historical runner accepted only in retained pilot provenance;
- protected A authority-free;
- original strict raw/launch/evidence verification;
- 10 selected formal pairs per mode;
- failed/retried attempts retained;
- complete result retained regardless of performance direction.

## Checkpoint / V05 / M08

Before cleanup, authenticate a new checkpoint containing:

- V00 current/protected authority;
- fresh Python inventory;
- Unity reuse/fresh classification;
- exact 9/22 source audits;
- retained evidence audit;
- new graph bridge including retained runner provenance;
- retained pilot admission preflight;
- new strict pilot seal;
- all formal batches/authorities/retries;
- final sample index;
- final analysis;
- hashes/links for every historical blocked cycle.

Proceed to V05 / independent M08 only after mandatory V04 is complete and consistent.

M08 must explicitly review:

- historical pilot runner provenance derivation;
- bridge-before-loader ordering;
- pilot-vs-formal runner identity isolation;
- admission preflight;
- strict seal;
- formal subprocess authority chain;
- final analysis.

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

- fixed retained runner revision/path/hash policy;
- graph-reuse 22-path allowlist;
- bridge/preflight/seal schema;
- loader pilot/formal runner distinction;
- source/runtime/protected pins;
- default R00 current-pairing behavior;
- formal authority semantics;
- graph/map/protocol/schedule identities;
- pair ordering/retry/statistics;
- final analyzer logic.

Any non-trivial source/tool correction returns to Primary.
