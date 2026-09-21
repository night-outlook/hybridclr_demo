# Local Validation Tasks — Nested Early Authority Closure + Formal Sampling

Candidate build-input/tool source anchor:

`a964f79d6ceba866c5956741a4a32e38ff8a6b5f`

Latest Local return:

`21caaecc315623ec10c779af04d563ed7badeac2`

Latest blocked checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6dd9-formal-blocked/`

Retained graph/pilot checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/`

H1 remains `InProgress`. Do not begin R02.

## Goal

Close the exact nested `R01EarlyStartup` authority-propagation defect returned by Local and, if it passes, continue in one batch through:

fresh authority/tests → exact 9-path Primary delta audit → exact 17-path retained-graph audit → retained evidence reauthentication → new graph-reuse bridge → 3-mode retained-ON early preflight → new 8-side strict pilot seal → all 40 formal pairs → bridge-aware final analysis → checkpoint → V05 / independent M08 if eligible.

The failed seal retained at authority `6dd964c0...` remains historical evidence. Do not overwrite, reuse, or relabel it.

## V00 — fresh current authority

1. Pull the final pushed `codex/assembly-shadow-r01b-h1`.
2. Require clean tracked state.
3. Record checkout HEAD separately from source/tool anchor `a964f79d6ceba866c5956741a4a32e38ff8a6b5f`.
4. Run live handoff/source preflight and require `SourceTargetVerifiedNotBuildAccepted` at the exact source anchor.
5. Reauthenticate reproduction tooling and exact protected profile-1 family.
6. Because the demo source pin changed, refresh the candidate installed-runtime receipt through the sanctioned:
   `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability`
   when the current receipt still binds the prior demo revision.
7. Verify candidate installed runtime with Shadow ON and complete demo-source verification.
8. Verify protected installed runtime with Shadow ON.
9. Retain the exact receipt hashes.

Do not create the graph bridge until V00/V01/V01A/V02 are complete.

After bridge creation, do not reinstall/refresh the candidate runtime unless the bridge is discarded and recreated.

## V01 — current Primary regressions

Run the complete current bounded Primary suite and live handoff preflight.

The final Primary source introduces:

- bridge-aware nested early authority propagation;
- explicit rejection outside `Baseline` / `Control`;
- a retained-ON early preflight tool and regression.

Expected focused direct suites:

- `test_h1_graph_reuse.py`: **11/11**;
- `test_h1_retained_early_preflight.py`: **2/2**;
- `test_h1_paired_driver.py`: **12/12**;
- `test_h1_formal_batch.py`: **2/2**;
- R01 early capsule: existing full pass;
- R01 early launch: existing full pass;
- R01 early results: existing full pass;
- failure pipeline: existing full pass;
- R01B lazy: existing full pass;
- both M07 PowerShell recovery regressions: Passed.

The final committed Primary CI count recorded in `source-targets.json` is authoritative if metadata-only successors change the checkout HEAD.

### Full Python inventory

Run complete Python discovery after all exact prerequisites recovered in the previous Local cycle are present.

Requirements:

- zero failure/error;
- every skip explicit and environment-bound;
- do not convert prior 28 environment skips into passes or ignore them silently;
- retain the complete test inventory/log.

### Broad Unity EditMode

Run the full broad Unity EditMode suite **before bridge creation**.

No Assets/Packages/C#/asmdef changed from the prior 1076/1076 Local run, but current source-pin/install authority did change. A fresh pass is preferred and should be retained for M08.

Require 1076/1076 or the current exact discovered count with zero unexplained failure/skip.

Do not run broad Unity/setup/build work after the bridge+seal unless both are deliberately invalidated and recreated.

## V01A — exact source audits

### A. Previous Primary source → current source

Compare:

`6dd964c045034240ea53dd15ba7c0b33e9f2ad17`

to:

`a964f79d6ceba866c5956741a4a32e38ff8a6b5f`

After applying repository metadata-only classification, the exact non-metadata delta must be these **9 paths**:

1. `.github/workflows/h1-bee-primary.yml`
2. `Tools/AssemblyShadow/README.md`
3. `Tools/AssemblyShadow/h1_bee_primary_tests.py`
4. `Tools/AssemblyShadow/h1_graph_reuse.py`
5. `Tools/AssemblyShadow/r00_results.py`
6. `Tools/AssemblyShadow/r01_early_results.py`
7. `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`
8. `Tools/AssemblyShadow/tests/test_h1_retained_early_preflight.py`
9. `Tools/AssemblyShadow/verify-h1-retained-early-reuse.py`

This proves the returned fix did not alter Player/runtime/measurement code.

### B. Retained graph anchor → current source

Compare:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3`

to:

`a964f79d6ceba866c5956741a4a32e38ff8a6b5f`

After metadata-only classification, the complete set must equal exactly these **17 paths**:

1. `.github/workflows/h1-bee-primary.yml`
2. `Tools/AssemblyShadow/README.md`
3. `Tools/AssemblyShadow/analyze-h1-paired-performance.py`
4. `Tools/AssemblyShadow/create-h1-graph-reuse-bridge.py`
5. `Tools/AssemblyShadow/h1_bee_primary_tests.py`
6. `Tools/AssemblyShadow/h1_graph_reuse.py`
7. `Tools/AssemblyShadow/r00_player_inputs.py`
8. `Tools/AssemblyShadow/r00_results.py`
9. `Tools/AssemblyShadow/r01_early_results.py`
10. `Tools/AssemblyShadow/run-h1-formal-batch.py`
11. `Tools/AssemblyShadow/run-h1-paired-performance.py`
12. `Tools/AssemblyShadow/seal-h1-pilot-verification.py`
13. `Tools/AssemblyShadow/tests/test_h1_formal_batch.py`
14. `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`
15. `Tools/AssemblyShadow/tests/test_h1_paired_driver.py`
16. `Tools/AssemblyShadow/tests/test_h1_retained_early_preflight.py`
17. `Tools/AssemblyShadow/verify-h1-retained-early-reuse.py`

Require no changed path under:

- `Assets/`;
- `Packages/`;
- Unity C#/asmdef/Bootstrap/measurement source;
- HybridCLR native;
- HybridCLR Unity;
- IL2CPP;
- protocol/schedule JSON;
- build-map producer;
- preregistration producer;
- `run-r00-players.py`;
- controlled graph/Player producer.

A subset or superset fails. Do not edit the allowlist locally.

## V02 — retained evidence reauthentication

Verify again before bridge creation:

- retained V04 checkpoint `MANIFEST.sha256`;
- `PLAYER_ARTIFACTS.sha256`;
- latest `authority6dd9-formal-blocked` checkpoint manifest;
- protected and candidate controlled graph receipts/evidence;
- frozen build map + freeze receipt;
- preregistration binding;
- bound protocol/schedule;
- complete pilot index including failed timeout + whole-pair retry;
- all 8 selected pilot launch receipts;
- the complete bound-file inventory.

The previous real bridge SHA-256
`088a338632a9d2a9970c0bc61aaa9b218b4ca93e080a1734539b68317fa1a89e`
is historical evidence only. It binds source/verifier authority `6dd964c0...` and must not be reused under the new source.

## V04.N — create a new graph-reuse bridge

Create a **new** bridge after current installed-runtime refresh and all audits:

~~~text
python3 Tools/AssemblyShadow/create-h1-graph-reuse-bridge.py \
  --project <absolute-candidate-project> \
  --build-map <retained-live-frozen-build-map.json> \
  --output <new-graph-reuse-bridge.json>
~~~

Require:

- `kind=H1GraphReuseBridge`;
- `status=AuthenticatedToolOnlySuccessor`;
- `side=B`;
- `transition.policyId=H1V04RetainedGraphToolOnlySuccessor-v1`;
- retained graph demo revision exactly `69130bbb...`;
- current demo revision exactly `a964f79d6ceba866c5956741a4a32e38ff8a6b5f`;
- exact 17-path transition;
- current source-pin binding;
- exact frozen build-map binding;
- current installed-runtime verification;
- verifier bindings include `r01_early_results.py`;
- no project/graph/Player mutation.

If bridge creation fails, return to Primary.

## V04.N1 — retained ON early preflight

Before the expensive 8-side seal, run:

~~~text
python3 Tools/AssemblyShadow/verify-h1-retained-early-reuse.py \
  --protocol <bound-protocol> \
  --schedule <bound-schedule> \
  --build-map <retained-live-frozen-build-map.json> \
  --pilot-index <retained-live-pilot-index.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --output <new-retained-early-preflight.json>
~~~

This is the direct empirical closure of the returned nested-authority defect.

Require:

- `kind=H1RetainedEarlyReusePreflight`;
- `result=Passed`;
- `modeCount=3`;
- exact modes, in order:
  - `R00-ON-NoPatch`;
  - `R00-ON-P01`;
  - `R00-ON-P03`;
- side B only;
- exact new bridge binding;
- each mode's strict R00 result Passed;
- no `source pins differ from baseline provenance` failure;
- Baseline and Control nested early-capsule reconstruction both succeed;
- output is read-only diagnostic evidence.

Record per-mode and total durations.

If this preflight fails, **do not run the full seal**. Preserve evidence and return to Primary.

The preflight does not replace the seal.

## V04.O — create a new strict 8-side pilot seal

Only after V04.N1 passes:

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
- all four pilot modes selected;
- all retained attempts in the attempt digest;
- candidate side B:
  - retained authority applies through outer R00 graph verification;
  - for ON modes it also applies through nested `R01EarlyStartup` preparation/capsule reconstruction;
- protected side A remains default current-pairing verification;
- immutable file/stat guards stable;
- no graph/pilot file mutation.

This must supersede, not overwrite, the failed `6dd964c0...` seal attempt.

After seal creation, do not run setup/build/test/install work that can alter sealed inputs.

## V04.P — all 40 formal pairs

Run the Primary-owned batch:

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

Full success requires:

- `kind=H1FormalBatchRun`;
- `status=PassedAllFormalPairs`;
- `formalPairCount=40`;
- `formalPairsPassed=40`;
- every formal attempt binds the exact same new bridge + seal;
- cumulative sample index contains all pilots and formal pair IDs;
- preregistered order is preserved;
- no repeated 8-graph pilot reconstruction before each pair.

Record first formal admission → first side-launch latency.

### Failed whole pair

The batch intentionally stops.

Retain the failed whole pair and batch receipt. Diagnose process cleanup.

Only if the unchanged preregistered retry policy permits it, explicitly retry the same pair with:

- same bridge;
- same seal;
- failed cumulative index as prior;
- exact same pair ID;
- incremented attempt number.

Then resume with a new batch root from the successful retry index.

Never auto-retry, retry one side, skip a failed pair, edit order, or delete a slow sample.

## V04.Q — final bridge-aware strict analysis

After 40 selected valid formal pairs:

~~~text
python3 Tools/AssemblyShadow/analyze-h1-paired-performance.py \
  --sample-index <final-sample-index.json> \
  --pilot-verification-receipt <new-pilot-verification.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --output <new-performance-analysis.json>
~~~

Require the analyzer to:

- full-reauthenticate the current bridge;
- require every formal attempt to bind the same bridge/seal;
- apply retained authority only to candidate side B;
- propagate that same authority through nested early reconstruction for retained ON observations;
- keep protected side A on default current pairing;
- perform full strict launch/raw/evidence verification;
- retain all valid and failed/retried attempts;
- report 10 formal pairs per mode;
- report the complete preregistered comparability/performance result regardless of whether it is favorable.

## Retention checkpoint

Before cleanup, authenticate a new checkpoint containing:

- V00 current/protected authority;
- V01 Primary/Python/Unity inventories;
- both source audits;
- retained evidence audit;
- new graph bridge;
- retained-ON early preflight;
- new strict pilot seal;
- every formal-batch receipt;
- every formal attempt/retry;
- final cumulative sample index;
- final analysis;
- explicit hashes/links to all earlier blocked attempts/checkpoints.

Do not clean until the checkpoint manifest verifies.

## V05 / independent M08

Proceed only when all mandatory V04 evidence above is complete and consistent.

M08 must explicitly review:

- exact 17-path retained-graph transition;
- bridge validity and verifier bindings;
- default R00 pairing preservation;
- internal/keyword-only nested early authority propagation;
- V04.N1 retained-ON preflight;
- 8-side pilot seal;
- cache identity guard;
- formal batch/retry chain;
- final strict performance analysis;
- fresh Python/Unity current-anchor evidence;
- all historical failed seal attempts retained without relabelling.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**.

Stop for explicit human approval.

**Do not begin R02.**

## Local correction boundary

Local may change only:

- absolute local paths;
- new evidence/output roots;
- executable permissions;
- bounded invocation syntax;
- explicit protocol-valid whole-pair retry attempt number.

Local must not change:

- graph-reuse allowlist/policy;
- source/runtime pins;
- `r00_player_inputs.require_current_pairing`;
- nested authority mode restriction;
- bridge/preflight/seal schema or verifier semantics;
- retained graph/map/protocol/schedule identities;
- pair ordering/retry/statistics;
- final analyzer logic.

Any non-trivial correction returns to Primary.
