# Primary Implementation → Local Validation

## Objective

Validate the authenticated retained-graph reuse bridge at candidate build-input/tool source anchor:

`6dd964c045034240ea53dd15ba7c0b33e9f2ad17`

Then, if the bridge and strict pilot seal pass, complete in one Local cycle:

fresh authority/tests → exact source/reuse audit → retained evidence reauthentication → graph-reuse bridge → strict pilot seal → all 40 formal pairs through the sequential batch runner → bridge-aware final strict analysis → authenticated checkpoint → V05/M08 if eligible.

Latest Local return:

`9045d54e3a1c365ac8c15a3cb5ca791ad13d7501`

H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

**Do not begin R02.**

## Source targets

Machine authority:

`Docs/AssemblyShadow/Handoff/source-targets.json`

Candidate identities:

| Repository | Branch | Build/runtime identity |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | source anchor `6dd964c045034240ea53dd15ba7c0b33e9f2ad17` |
| `night-outlook/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| `night-outlook/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| `night-outlook/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |

Protected profile-1 family remains unchanged:

- demo HEAD `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c`;
- demo source anchor `f1c923cbaa814e1b63f3c5b9f8303c90616de726`;
- HybridCLR `b22fa3d92223645c32663e4a2157eaadf8ea495e`;
- HybridCLR Unity `b649c499385ea68490a0f652a98b732e060aeb89`;
- IL2CPP `7967b8c7043904fcae130b294defd5ce7aa897c4`.

Environment target:

`Unity 2022.3.62f2 / StandaloneOSX / arm64`

The branch checkout HEAD may be a later metadata-only successor. Record checkout HEAD separately from the source anchor.

Retained V04 graph/pilot checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/`

Latest blocked-formal checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority1a87-formal-blocked/`

Primary source/tool CI after source authority advance:

- workflow `35595508673`;
- commit `1273dea49f0e091888cbd0d5fd5267be8897008a`;
- bounded **348/348**;
- committed handoff **11/11**;
- R01 early capsule **7/7**;
- early launch **20/20**;
- early results **20/20**;
- failure pipeline **16/16**;
- both M07 PowerShell recovery regressions **Passed**;
- R01B lazy **10/10**;
- artifact `10636615987`, SHA-256 `6f3049b8d48994189abf83a3ac0dca131c71e2de7d244c7d90b4ecd4ac57fd83`.

This is Primary source/tool evidence only.

## Implementation

### Returned Local finding

The previous one-time strict pilot seal reached the unchanged R00 graph verifier and failed after 390.81 seconds with:

`R00 baseline: source pins differ from baseline provenance`

The retained current/profile-2 graph correctly records demo source revision:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3`

while current project authority had advanced to:

`1a87a393e7a0ee312f39647532d80bfc603c7b23`.

The default `r00_player_inputs.require_current_pairing` correctly rejected the complete source-pin DTO mismatch. No seal/formal Player was produced.

Local also independently closed the generated-prerequisite inventories:

- Python: 993 passed, 28 explicit environment skips, zero failure/error;
- Unity EditMode: 1076/1076 passed, zero skips.

### Repair 1 — authenticated retained-graph source-pairing bridge

Primary did **not** weaken the default R00 pairing gate.

New:

- `Tools/AssemblyShadow/h1_graph_reuse.py`;
- `Tools/AssemblyShadow/create-h1-graph-reuse-bridge.py`.

The only reusable profile-2 graph is the retained candidate graph at `69130bbb...`.

`H1GraphReuseBridge` requires:

1. current candidate source/runtime authority through the unchanged global verifier;
2. graph/current Unity version, target, and architecture equality;
3. exact equality of HybridCLR, HybridCLR Unity, and IL2CPP pins;
4. graph demo revision exactly `69130bbb...`;
5. `69130bbb...` is a Git ancestor of current source anchor;
6. after the repository's existing metadata-only classification, the complete graph→current delta is **exactly** this 14-path allowlist:

   - `.github/workflows/h1-bee-primary.yml`
   - `Tools/AssemblyShadow/README.md`
   - `Tools/AssemblyShadow/analyze-h1-paired-performance.py`
   - `Tools/AssemblyShadow/create-h1-graph-reuse-bridge.py`
   - `Tools/AssemblyShadow/h1_bee_primary_tests.py`
   - `Tools/AssemblyShadow/h1_graph_reuse.py`
   - `Tools/AssemblyShadow/r00_player_inputs.py`
   - `Tools/AssemblyShadow/r00_results.py`
   - `Tools/AssemblyShadow/run-h1-formal-batch.py`
   - `Tools/AssemblyShadow/run-h1-paired-performance.py`
   - `Tools/AssemblyShadow/seal-h1-pilot-verification.py`
   - `Tools/AssemblyShadow/tests/test_h1_formal_batch.py`
   - `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`
   - `Tools/AssemblyShadow/tests/test_h1_paired_driver.py`

A subset or superset fails.

The bridge binds:

- retained graph source-pin DTO;
- current source-pin bytes/DTO;
- every changed Git blob;
- frozen build map;
- bridge/verifier implementation;
- current installed-runtime verification.

### Strict R00 contract remains default

`r00_player_inputs.require_current_pairing` retains the original strict complete-DTO comparison.

Default `verify_inputs` remains current-pairing-only.

A separate `verify_inputs_with_reuse` requires an explicit `H1AuthenticatedGraphReuseAuthority`.

Only bridge-authenticated seal/final-analysis paths may provide that authority, and only exact candidate side B receives it. Protected side A and ordinary R00 verification remain on the default path.

No arbitrary historical source-pin CLI override exists.

### Repair 2 — bridge-bound seal and formal chain

The pilot seal accepts:

`--graph-reuse-bridge <bridge>`

and fully reauthenticates the bridge before deep verification.

During the 8 side-graph seal checks:

- candidate side B uses the authenticated retained graph pairing;
- protected side A uses default strict current pairing.

`H1PilotVerificationReceipt` binds the bridge.

Every formal attempt binds both:

- `pilotVerification`;
- `graphReuseBridge`.

A cumulative formal chain cannot switch either authority.

Cached formal admission still performs zero repeated 8-graph deep rescans and fails closed on any bridge/seal/file/tool mismatch.

Fresh current-pairing graphs remain supported without a bridge.

### Repair 3 — bridge-aware final strict analyzer

`analyze-h1-paired-performance.py` now explicitly requires:

- final sample index;
- pilot verification receipt;
- graph-reuse bridge.

It full-reauthenticates the bridge, requires every formal attempt to bind the same bridge+seal, and then runs the existing strict launch/raw/evidence analyzer.

Historical pairing authority is applied only to retained candidate side B. Protected side A remains default-current.

The bridge and pilot seal do **not** replace final strict evidence verification.

### Repair 4 — Primary-owned sequential formal batch runner

New:

`Tools/AssemblyShadow/run-h1-formal-batch.py`

It removes forty-step manual chaining from Local Validation.

The batch:

- validates the same protocol/schedule/map/bridge/seal/prior index;
- selects each next unattempted formal pair in preregistered order;
- invokes the existing single-pair driver;
- chains each produced sample index into the next pair;
- writes `H1FormalBatchRun`;
- never retries automatically;
- stops on the first failed whole pair;
- refuses to resume while an unresolved failed pair exists.

A protocol-valid retry must be performed explicitly with the single-pair driver. A new batch may then resume from the successful retry sample index.

### Primary regression coverage

The bounded suite now includes real repository and orchestration coverage:

- real `69130bbb... → current` Git transition must equal the exact allowlist;
- changed runtime pin rejected;
- wrong retained graph revision rejected;
- default R00 pairing remains current-only;
- untrusted reuse authority rejected;
- bridge authority applied only to candidate side B;
- bridge bound into strict pilot seal;
- formal bridge/seal switching rejected;
- final analyzer bridge/seal binding enforced;
- one strict seal = 8 deep verifications;
- forty cached formal admissions = zero deep pilot rescans;
- sequential batch chains forty formal pair indexes;
- batch stops on first failed whole pair and never auto-retries/skips it.

## Local validation

Detailed executable plan:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`

Run it in order.

### Before bridge creation

Complete all setup/authority activity first:

1. fresh V00 candidate/reproduction/protected authority;
2. sanctioned candidate installed-runtime receipt refresh if the new source pin requires it;
3. candidate/protected installed-runtime verification;
4. current Primary/Python regressions;
5. preferably fresh broad Unity EditMode;
6. exact source audit;
7. retained checkpoint/Player/map/protocol/schedule/pilot hash verification.

After bridge+seal creation, do not run setup/build/test activity that can rewrite sealed graph/pilot inputs.

### Create the graph-reuse bridge

~~~text
python3 Tools/AssemblyShadow/create-h1-graph-reuse-bridge.py \
  --project <candidate> \
  --build-map <retained-live-frozen-build-map.json> \
  --output <new-graph-reuse-bridge.json>
~~~

Require the exact old/current source identities, exact 14-path delta, current installed-runtime proof, and frozen-map binding.

### Seal pilots using the bridge

~~~text
python3 Tools/AssemblyShadow/seal-h1-pilot-verification.py \
  --protocol <bound-protocol> \
  --schedule <bound-schedule> \
  --build-map <retained-live-frozen-build-map.json> \
  --pilot-index <retained-live-pilot-index.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --output <new-pilot-verification.json>
~~~

Require `deepLaunchVerificationCount=8`, exact bridge binding, and complete stat/file guard sealing.

This must close the previous real source-pin mismatch.

### Run formal sampling as one batch

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

A full pass must report `PassedAllFormalPairs / 40 of 40`.

If it stops on a failed whole pair, preserve the failure. Retry that exact pair manually only when the unchanged preregistered policy permits it, then resume with a new batch root from the retry index.

No automatic retry, side-only retry, pair skipping, sample deletion, or schedule/protocol/map/bridge/seal modification is allowed.

### Final strict analysis

~~~text
python3 Tools/AssemblyShadow/analyze-h1-paired-performance.py \
  --sample-index <final-sample-index.json> \
  --pilot-verification-receipt <new-pilot-verification.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --output <new-performance-analysis.json>
~~~

Retain the complete result even if performance/comparability is unfavorable.

Proceed to V05/independent M08 only when the entire mandatory chain is complete.

## Failure evidence

On bridge failure retain:

- exact old/current source-pin DTOs;
- exact Git delta/allowlist diagnostic;
- current installed-runtime verification;
- frozen build-map binding;
- verifier bindings;
- bridge command/stdout/stderr.

On seal failure retain:

- bridge receipt;
- selected pilot bindings;
- exact failing side/mode;
- strict R00 error;
- file/hash/guard diagnostic;
- seal stdout/stderr and elapsed time.

On formal failure retain:

- formal-batch receipt;
- failed cumulative sample index;
- both side logs/output;
- bridge/seal binding;
- owned-process cleanup evidence;
- any explicit retry and its separate sample index.

On analysis failure retain the analyzer failure receipt plus final sample/bridge/seal bindings.

Do not clean retained V04 graph/pilot data or new formal data before the new checkpoint is authenticated.

## Alternatives

Do not:

- weaken or edit `r00_player_inputs.require_current_pairing`;
- add a general historical source-pin override;
- rewrite retained graph/Player/replay receipts;
- move current or protected source pins backward;
- accept a scope audit without a bridge receipt;
- broaden the 14-path allowlist locally;
- inject retained pairing authority into protected side A;
- auto-reseal after bridge/guard mismatch;
- silently rebuild the bridge mid-formal-chain;
- auto-retry a failed formal pair;
- retry only one side;
- delete slow/failed samples;
- modify protocol, schedule, build map, thresholds, or final statistics after observing performance;
- begin R02.

If the bridge cannot authenticate honestly, the fallback is a fresh profile-2 controlled graph/map/preregistration/pilot rebuild at the current source anchor—not verifier weakening.

## Risks

- Bridge creation performs full current source/runtime and Git transition authentication and may require a sanctioned installed-runtime receipt refresh first.
- The initial strict pilot seal remains expensive because it deliberately reconstructs all eight pilot side graphs once.
- Forty formal A/B pairs are intrinsically long-running Player work even after admission optimization.
- Any mutation of sealed graph/pilot files invalidates the seal.
- Any current source-pin/tool change invalidates the bridge.
- Final analysis remains intentionally expensive because it re-verifies all selected evidence strictly.
- The 28 Python skips from the previous Local cycle are environment-bound and must remain explicit; they are not passes.

## Local correction boundary

Local may adjust only:

- absolute local paths;
- new bridge/seal/batch/analysis evidence roots;
- executable permissions;
- bounded invocation syntax;
- explicit same-pair retry attempt number when the unchanged protocol permits retry.

Local must not alter:

- bridge policy/allowlist;
- retained graph source revision;
- source/runtime pins;
- default R00 pairing semantics;
- bridge/seal schema or verification rules;
- frozen graph/map/protocol/schedule/preregistration identities;
- pair ordering/retry/statistics;
- final analyzer semantics.

Any non-trivial source/tool correction returns to Primary.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress**.

The authenticated bridge, strict pilot seal, all 40 formal pairs, final analysis, V05, and a genuinely independent whole-chain M08 remain required.

M08 must explicitly review:

- retained-graph bridge proof and exact source allowlist;
- default strict R00 pairing preservation;
- pilot seal/cache proof;
- formal batch/retry chain;
- final performance analysis;
- any reused versus fresh Python/Unity evidence.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**. Human approval must then be explicit.

**Do not begin R02.**
