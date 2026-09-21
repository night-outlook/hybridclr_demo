# Local Validation Tasks — Retained-Graph Bridge + Formal Closure after `9045d54e...`

Candidate build-input/tool source anchor:

`6dd964c045034240ea53dd15ba7c0b33e9f2ad17`

Latest Local return:

`9045d54e3a1c365ac8c15a3cb5ca791ad13d7501`

Retained graph/pilot checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/`

Latest Local checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority1a87-formal-blocked/`

H1 remains `InProgress`. Do not begin R02.

## Goal

Close the retained-graph source-pairing blocker without rebuilding already-authenticated Players:

fresh authority/tests → exact 14-path source/reuse audit → retained artifact reauthentication → one authenticated graph-reuse bridge → one strict pilot seal → all 40 formal pairs through the Primary batch runner → bridge-aware final strict analysis → authenticated checkpoint → V05/independent M08 if eligible.

Do not perform source/tool edits in Local. Any non-trivial correction returns to Primary.

## V00 — fresh current authority

1. Pull final pushed `codex/assembly-shadow-r01b-h1`.
2. Require clean tracked state and record checkout HEAD separately from source anchor `6dd964c045034240ea53dd15ba7c0b33e9f2ad17`.
3. Run current candidate handoff/source preflight; require `SourceTargetVerifiedNotBuildAccepted` at the exact source anchor.
4. Reauthenticate reproduction tooling and the exact protected profile-1 family.
5. Because the demo source pin advanced, run the sanctioned candidate:
   `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability`
   if the current installed-runtime receipt still binds the previous demo revision.
6. Verify candidate installed runtime with Shadow ON.
7. Verify protected installed runtime with Shadow ON.
8. Record receipt hashes before proceeding.

After the graph-reuse bridge is created, do **not** refresh/reinstall the candidate runtime again unless the bridge is deliberately discarded and recreated.

Hard-stop on source/runtime/protected-ref mismatch.

## V01 — current Primary/tool regression and prerequisite closure

Before creating the bridge or pilot seal, run:

- complete bounded Primary suite;
- committed live-handoff preflight;
- direct `test_h1_graph_reuse.py`;
- direct `test_h1_paired_driver.py`;
- direct `test_h1_formal_batch.py`;
- existing R01 early/failure/lazy suites;
- both M07 PowerShell recovery regressions.

Primary reference for the final source should have **348 bounded tests** before any metadata-only successor adjustment; the exact final committed handoff CI result in `source-targets.json` is authoritative.

### Python inventory

Run complete Python discovery again. The tooling changed materially in this cycle, so the prior Python result is not sufficient as current-source acceptance.

Expected external-environment skips remain explicit; no failure/error is acceptable.

### Unity EditMode

The source audit should show no Assets/Packages/C#/asmdef change from the previously passed Local cycle. Nevertheless, run broad Unity EditMode **before bridge creation** when possible so M08 receives fresh current-anchor evidence and no later Unity activity can touch sealed graph artifacts.

Require a fresh full pass or, only if an environmental constraint makes it genuinely impossible, retain an explicit `ReusedAuditedFrom9045` classification backed by the exact source-scope audit. Do not silently promote the prior 1076/1076 result to current-anchor Passed.

Do not run broad Unity/installation/setup work after the bridge+seal unless the bridge/seal is invalidated and recreated.

## V01A — exact source-scope and graph-reuse audit

Perform both audits independently.

### A. Previous Primary anchor → current anchor

Compare:

`1a87a393e7a0ee312f39647532d80bfc603c7b23`

to:

`6dd964c045034240ea53dd15ba7c0b33e9f2ad17`

Confirm every executable/tool change is expected and confined to retained-graph bridge/formal orchestration/testing/CI/tool documentation.

### B. Retained graph anchor → current anchor

Compare:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3`

to:

`6dd964c045034240ea53dd15ba7c0b33e9f2ad17`

Apply the repository's existing metadata-only classification. The **complete non-metadata set must equal exactly these 14 paths**:

1. `.github/workflows/h1-bee-primary.yml`
2. `Tools/AssemblyShadow/README.md`
3. `Tools/AssemblyShadow/analyze-h1-paired-performance.py`
4. `Tools/AssemblyShadow/create-h1-graph-reuse-bridge.py`
5. `Tools/AssemblyShadow/h1_bee_primary_tests.py`
6. `Tools/AssemblyShadow/h1_graph_reuse.py`
7. `Tools/AssemblyShadow/r00_player_inputs.py`
8. `Tools/AssemblyShadow/r00_results.py`
9. `Tools/AssemblyShadow/run-h1-formal-batch.py`
10. `Tools/AssemblyShadow/run-h1-paired-performance.py`
11. `Tools/AssemblyShadow/seal-h1-pilot-verification.py`
12. `Tools/AssemblyShadow/tests/test_h1_formal_batch.py`
13. `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`
14. `Tools/AssemblyShadow/tests/test_h1_paired_driver.py`

Require no changed path under:

- `Assets/`;
- `Packages/`;
- Player/runtime/Bootstrap source;
- measurement source;
- HybridCLR native;
- HybridCLR Unity;
- IL2CPP;
- protocol/schedule JSON;
- build-map producer;
- preregistration producer;
- `run-r00-players.py`;
- M07 graph producer/runtime evidence paths.

A subset or superset of the 14-path set is a hard failure. Do not edit the allowlist locally.

## V02 — retained evidence reauthentication

Before bridge creation, verify the retained V04 checkpoint again:

- checkpoint `MANIFEST.sha256`;
- `PLAYER_ARTIFACTS.sha256`;
- current/profile-2 controlled graph receipts and evidence;
- protected/profile-1 controlled graph receipts and evidence;
- frozen build map + freeze receipt;
- preregistration binding;
- bound protocol and schedule;
- full retained pilot sample index, including failed timeout + whole-pair retry;
- every selected pilot launch receipt and live artifact hash.

Also verify the latest `authority1a87-formal-blocked` checkpoint manifest so the failed 390.81-second seal attempt remains preserved as historical evidence.

Do not modify or copy-over live graph/pilot files after these checks.

## V04.N — create one authenticated graph-reuse bridge

Use the live candidate project and retained live frozen build map:

~~~text
python3 Tools/AssemblyShadow/create-h1-graph-reuse-bridge.py \
  --project <absolute-candidate-project> \
  --build-map <retained-live-frozen-build-map.json> \
  --output <new-graph-reuse-bridge.json>
~~~

Require:

- `schemaVersion=1`;
- `kind=H1GraphReuseBridge`;
- `status=AuthenticatedToolOnlySuccessor`;
- `side=B`;
- `transition.policyId=H1V04RetainedGraphToolOnlySuccessor-v1`;
- `transition.graphDemoRevision=69130bbb3a6df516916dddb5ad263799a7c6e5e3`;
- `transition.currentDemoRevision=6dd964c045034240ea53dd15ba7c0b33e9f2ad17`;
- exact 14-path non-metadata delta;
- current source-pin binding and graph-source DTO binding;
- exact frozen build-map binding;
- current verifier/tool bindings;
- current installed-runtime verification bound to the already-refreshed candidate receipt.

Independently inspect that graph/current Unity/target/architecture and HybridCLR/HybridCLR-Unity/IL2CPP pins are identical except the permitted demo revision transition.

The bridge must not mutate the project, source pins, retained graph, build map, or Players.

If bridge creation fails, return to Primary. Do not fall back to scope-audit-only reuse.

## V04.O — strict pilot seal using the bridge

Only after V04.N passes:

~~~text
python3 Tools/AssemblyShadow/seal-h1-pilot-verification.py \
  --protocol <bound-protocol> \
  --schedule <bound-schedule> \
  --build-map <retained-live-frozen-build-map.json> \
  --pilot-index <retained-live-pilot-sample-index.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --output <new-pilot-verification.json>
~~~

Require:

- `kind=H1PilotVerificationReceipt`;
- `status=PassedStrictReconstructionAndStatGuardSealed`;
- exact `graphReuseBridge` binding;
- `deepLaunchVerificationCount=8`;
- exactly four latest successful pilot pairs selected;
- all retained pilot attempts included in the attempt digest;
- candidate side B deep verification succeeds against bridge-authenticated graph pins;
- protected side A remains on the default strict current-pairing path;
- complete immutable file inventory/guard digests exist;
- no file identity changes during sealing.

Record wall-clock duration, file count, total bytes, and bridge/seal hashes.

This is the direct regression of the previous real failure. The old
`R00 baseline: source pins differ from baseline provenance`
failure must not recur when the bridge is valid.

After sealing, do not run setup/build/test operations that can alter sealed graph/pilot files.

## V04.P — complete formal sampling with the Primary batch runner

Start a new output root:

~~~text
python3 Tools/AssemblyShadow/run-h1-formal-batch.py \
  --protocol <bound-protocol> \
  --schedule <bound-schedule> \
  --build-map <retained-live-frozen-build-map.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --pilot-verification-receipt <new-pilot-verification.json> \
  --prior-index <retained-live-pilot-sample-index.json> \
  --output-root <new-formal-batch-root> \
  --timeout 900
~~~

Normal successful exit requires:

- `kind=H1FormalBatchRun`;
- `status=PassedAllFormalPairs`;
- `formalPairCount=40`;
- `formalPairsPassed=40`;
- cumulative final sample index contains all four pilots plus all 40 formal pair IDs;
- every formal attempt binds the exact same bridge and seal;
- all formal pairs respect preregistered AB/BA order;
- no repeated eight-graph pilot reconstruction occurs before each pair.

Record the first formal pair's admission-to-first-side-launch latency. The previous 47:39 pre-launch behavior must not recur.

### If the batch stops on a failed whole pair

The batch intentionally does **not** retry.

1. Preserve `formal-batch.json`, the failed pair output, logs, and failed cumulative index.
2. Diagnose and prove no owned Player/runner process remains.
3. Determine whether the existing preregistered whole-pair retry policy permits retry.
4. If yes, rerun exactly the same pair explicitly:

~~~text
python3 Tools/AssemblyShadow/run-h1-paired-performance.py \
  --protocol <bound-protocol> \
  --schedule <bound-schedule> \
  --build-map <retained-live-frozen-build-map.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --pilot-verification-receipt <new-pilot-verification.json> \
  --prior-index <failed-pair-sample-index.json> \
  --output-root <new-retry-root> \
  --phase formal \
  --pair-id <same-pair-id> \
  --attempt <next-attempt-number> \
  --timeout 900
~~~

5. Preserve the failed attempt.
6. If retry passes, start **a new batch output root** using the retry sample index as `--prior-index`.
7. If retry is not permitted or exposes a source/tool defect, return to Primary.

Never:

- retry only A or B;
- skip an unresolved failed pair;
- auto-repeat a pair;
- delete a slow sample;
- edit the schedule/protocol/map/bridge/seal after observing timings.

## V04.Q — final bridge-aware strict analysis

After all 40 formal pairs have a selected valid attempt:

~~~text
python3 Tools/AssemblyShadow/analyze-h1-paired-performance.py \
  --sample-index <final-sample-index.json> \
  --pilot-verification-receipt <new-pilot-verification.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --output <new-performance-analysis.json>
~~~

The analyzer must:

- full-reauthenticate the bridge;
- require every formal attempt to bind the same bridge/seal;
- use historical pairing authority only for candidate side B;
- use default pairing for protected side A;
- perform the existing full strict launch/raw/evidence verification;
- report the preregistered 10 formal pairs per mode;
- retain all valid samples and all failed/retried attempts;
- emit the full comparability/measurement result even if unfavorable.

Do not use the bridge or pilot seal as a substitute for final evidence reconstruction.

## V05 / independent M08

Proceed only if:

1. V00/V01 current authority passes;
2. exact 14-path source/reuse audit passes;
3. retained evidence reauthentication passes;
4. bridge creation passes;
5. strict pilot seal passes;
6. all 40 formal pairs complete under the unchanged preregistered contract;
7. final analysis completes;
8. Python inventory has no unexplained failures/errors;
9. Unity inventory is freshly Passed or explicitly audited/reused with adequate justification;
10. no fresh evidence contradicts retained H1 evidence.

Then:

- prepare V05 successor evidence;
- authenticate a new pre-cleanup checkpoint;
- commission a genuinely independent whole-chain M08 review;
- require M08 to review the graph-reuse bridge proof, seal/cache proof, formal-batch chain, final analysis, and any reused Unity evidence.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**.

Stop for explicit human approval.

**Do not begin R02.**

## Failure retention

On any failure retain at minimum:

- exact checkout/source/runtime identities;
- bridge/seal/batch command and stdout/stderr;
- graph bridge receipt or failure;
- exact Git delta/allowlist diagnostic;
- source-pin/build-map/verifier bindings;
- pilot seal or seal failure;
- first invalid path/hash/guard when applicable;
- cumulative sample index before and after each formal attempt;
- whole-pair logs and cleanup evidence;
- final analysis failure receipt if analysis is reached.

Do not clean the retained V04 graph/pilot artifacts or new formal evidence before the new checkpoint is authenticated.
