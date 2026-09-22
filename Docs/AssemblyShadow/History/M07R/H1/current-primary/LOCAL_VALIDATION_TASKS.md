# Local Validation Tasks — Cross-Remount Seal Guard v2 + Fresh Formal Series

Candidate source/tool anchor:

`27df1a3d60811dc121f296ab561ae313a382b363`

Latest Local return:

`421f221156f4e9a71aab3363fd4e49a91cbaba68`

Latest authenticated blocked checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260922-authority91ac-formal-seal-invalidated/`

Retained graph/pilot checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/`

H1 remains `InProgress`. Do not begin R02.

## Goal

Validate cross-remount-stable seal guard v2 and collision-resistant internal paired outputs, then complete a wholly new formal series in one Local cycle if every gate passes:

fresh authority/tests → exact 3-path Primary delta audit → exact 22-path retained-graph audit → retained evidence reauthentication → new graph bridge → retained-pilot admission preflight → new guard-v2 strict seal → new 40-pair formal batch → final strict analysis → checkpoint → V05 / independent M08 if eligible.

The prior 14/40 formal series is historical only. Do not reuse or chain any of its sample indexes.

## V00 — fresh current authority

1. Pull final pushed `codex/assembly-shadow-r01b-h1`.
2. Require clean tracked state.
3. Record checkout HEAD separately from source/tool anchor `27df1a3d60811dc121f296ab561ae313a382b363`.
4. Run candidate handoff/source preflight and require `SourceTargetVerifiedNotBuildAccepted`.
5. Reauthenticate reproduction tooling and protected profile-1 family.
6. Refresh candidate installed-runtime receipt through the sanctioned `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability` path if the current receipt still binds the previous demo revision.
7. Verify candidate installed runtime with Shadow ON and complete demo-source authentication.
8. Verify protected installed runtime with Shadow ON.
9. Retain exact receipt hashes.

Do not create the bridge until V00/V01/V01A/V02 are complete.

## V01 — current Primary regression

Run:

- complete bounded Primary suite;
- live handoff preflight;
- direct `test_h1_paired_driver.py`;
- retained-pilot runner/admission suites;
- graph reuse/formal authority/formal batch suites;
- R01 early/failure/lazy suites;
- both M07 PowerShell recovery regressions.

### Python inventory

Run complete Python discovery because the paired driver/guard implementation changed.

Require:

- zero failures/errors;
- all skips explicit/environment-bound;
- complete log retained.

### Unity EditMode

The current 3-path source delta changes no Unity C#/asmdef/Assets/Packages/resource input.

The historical 1076/1076 result may remain:

`ReusedAuditedFromD18`

only after the exact 3-path audit passes.

A fresh Unity run is optional before bridge creation.

## V01A — exact source audits

### Previous Primary source → current source

Compare:

`91ac4db31cec704551c7db05bd918c8d5695ce83`

to:

`27df1a3d60811dc121f296ab561ae313a382b363`

After metadata-only classification, the exact non-metadata set must equal **3 paths**:

1. `Tools/AssemblyShadow/README.md`
2. `Tools/AssemblyShadow/run-h1-paired-performance.py`
3. `Tools/AssemblyShadow/tests/test_h1_paired_driver.py`

### Retained graph source → current source

Compare:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3`

to:

`27df1a3d60811dc121f296ab561ae313a382b363`

After metadata-only classification, the complete set must remain exactly the **22-path** allowlist in `source-targets.json`.

No changed path is permitted under Unity gameplay/runtime source, Assets/Packages, native HybridCLR/IL2CPP, protocol/schedule/build-map producers, measurement source, or Player binary source.

A subset or superset fails.

## V02 — retained evidence reauthentication

Before bridge creation verify:

- retained V04 manifest;
- Player-artifact manifest;
- latest `authority91ac-formal-seal-invalidated` checkpoint manifest;
- protocol/schedule/build map/preregistration;
- retained pilot index and all five pilot attempts;
- four selected pilots / eight selected launch receipts;
- complete bound-file inventory.

Also retain the prior 14/40 formal series and seal-invalidation receipt as historical evidence. Do not incorporate those attempts into the new cumulative series.

## V04.AA — create a new current graph bridge

Create a new bridge:

~~~text
python3 Tools/AssemblyShadow/create-h1-graph-reuse-bridge.py \
  --project <candidate> \
  --build-map <retained-live-frozen-build-map.json> \
  --output <new-graph-reuse-bridge.json>
~~~

Require:

- `AuthenticatedToolOnlySuccessor`;
- current demo revision exactly `27df1a3d60811dc121f296ab561ae313a382b363`;
- exact 22-path transition;
- exact current runtime/map/verifier bindings;
- fixed retained pilot runner provenance from `69130bbb...`.

Do not reuse the previous bridge.

## V04.AB — retained-pilot admission preflight

Run before the expensive seal:

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

- Passed;
- five retained attempts;
- four selected pilots;
- exact historical runner provenance;
- zero deep R00 verification.

If this fails, stop before seal and return to Primary.

## V04.AC — create guard-v2 strict pilot seal

Run:

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

- `status=PassedStrictReconstructionAndStatGuardSealed`;
- `deepLaunchVerificationCount=8`;
- `guardKind=CrossRemountStableStatGuard`;
- `guardVersion=2`;
- `guardFields=[inode, mode, size, mtimeNs, ctimeNs]`;
- no `device` field in any per-file acceptance guard;
- exact new bridge binding;
- stable file/stat inventory during sealing.

The old device-bound seal is incompatible and must not be reused.

### Explicit guard-v2 sanity

From the new seal, choose at least one protected Player native binary and independently record:

- canonical path;
- SHA-256;
- inode;
- mode;
- size;
- mtimeNs;
- ctimeNs;
- current `st_dev` as **diagnostic only**.

If the filesystem remounts later and only `st_dev` changes, formal admission must continue to pass.

If any acceptance field changes, it must fail closed.

Do not intentionally mutate files merely to test this.

## V04.AD — start a wholly new formal series

Start from the retained pilot index only:

~~~text
python3 Tools/AssemblyShadow/run-h1-formal-batch.py \
  --protocol <bound-protocol> \
  --schedule <bound-schedule> \
  --build-map <retained-live-frozen-build-map.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --pilot-verification-receipt <new-pilot-verification.json> \
  --prior-index <retained-live-pilot-index.json> \
  --output-root <new-unique-formal-batch-root> \
  --timeout 900
~~~

Do not use any sample index from the prior 14/40 series.

### Output-collision acceptance

Do not manually switch to a direct pair because of preserved historical project-local outputs.

The batch/paired driver must automatically derive collision-resistant per-project output names from the full canonical requested output path.

For formal pair 1 verify:

- project-local A/B output names include the new 12-hex path-hash suffix;
- they differ from preserved historical side-output paths;
- no `Per-side output must be new` collision occurs;
- parent formal authority output-root bindings match those new project-local paths.

If a collision still occurs, stop and return to Primary.

### Formal authority/current-runner acceptance

All prior current-formal requirements remain:

- protected A has no retained authority;
- candidate B uses the current runner;
- candidate B receives unique `H1FormalSideLaunchAuthority`;
- child uses `verify_inputs_with_reuse`;
- successful R00 receipt echoes authority/bridge/seal/map;
- historical runner is pilot provenance only.

### Complete all 40 pairs

Full success requires:

- `PassedAllFormalPairs`;
- 40/40 selected formal pairs;
- unchanged preregistered order;
- valid current formal authority for every actual candidate B attempt;
- no seal cache invalidation caused solely by `st_dev` drift.

### Whole-pair retry

If a protocol-valid pair fails:

- retain the failed attempt;
- retain its formal authority;
- prove process cleanup;
- retry exactly the same pair with incremented attempt;
- resume from the successful retry index in a new batch root.

No side-only retry, auto-retry, pair skip, or sample deletion.

## V04.AE — final strict analysis

After all 40 pairs complete:

~~~text
python3 Tools/AssemblyShadow/analyze-h1-paired-performance.py \
  --sample-index <final-sample-index.json> \
  --pilot-verification-receipt <new-pilot-verification.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --output <new-performance-analysis.json>
~~~

Require:

- full bridge/seal/formal-authority verification;
- 10 selected formal pairs per mode;
- all failed/retried attempts retained;
- complete comparability/performance result retained regardless of direction.

## Checkpoint / V05 / M08

Before cleanup authenticate a new checkpoint containing:

- V00 authority;
- current Python result;
- Unity reuse/fresh classification;
- exact 3/22 source audits;
- retained evidence audit;
- new bridge;
- admission preflight;
- guard-v2 seal;
- formal batch/retries/authorities;
- final sample index;
- final analysis;
- references to the historical 14/40 series and its device-drift invalidation.

Proceed to V05 and genuinely independent M08 only when mandatory V04 is complete and consistent.

M08 must explicitly review:

- the decision to exclude `st_dev`;
- guard-v2 acceptance fields and old-seal invalidation;
- collision-resistant project-output namespace;
- historical 14/40 evidence classification;
- full new 40-pair series and final analysis.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**.

Stop for explicit human approval.

**Do not begin R02.**

## Local correction boundary

Local may adjust only:

- absolute paths;
- new evidence/output roots;
- permissions/PYTHONPATH;
- bounded command syntax;
- protocol-valid whole-pair retry number.

Local must not alter:

- guard-v2 field set/version;
- device exclusion policy;
- path-hash output namespace;
- graph-reuse allowlist;
- bridge/seal/formal authority semantics;
- source/runtime pins;
- graph/map/protocol/schedule identities;
- pair order/retry/statistics;
- final analyzer logic.

Any non-trivial source/tool correction returns to Primary.
