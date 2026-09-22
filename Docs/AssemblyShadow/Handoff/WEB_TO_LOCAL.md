# Primary Implementation → Local Validation

## Objective

Validate the formal candidate side-B subprocess authority repair at candidate source/tool anchor:

`f1266a4d7f39a49523186b3dc63f9add9cc0e64c`

Then, if the fresh bridge/seal and first formal subprocess pass, continue in one Local batch through all 40 formal pairs, final strict analysis, checkpoint, V05, and independent M08 when eligible.

Latest Local return:

`d18a1fb15c43f918c9d3bba1ed641e87a58b32b0`

H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

**Do not begin R02.**

## Source targets

Machine authority:

`Docs/AssemblyShadow/Handoff/source-targets.json`

Candidate identities:

| Repository | Branch | Build/runtime identity |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | source/tool anchor `f1266a4d7f39a49523186b3dc63f9add9cc0e64c` |
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

The branch checkout HEAD may be a later metadata-only successor. Record checkout HEAD separately from source/tool anchor.

Evidence roots to retain:

- retained graph/pilots:
  `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/`;
- formal-admission cache blocker:
  `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority1a87-formal-blocked/`;
- nested early-authority blocker:
  `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6dd9-formal-blocked/`;
- latest formal subprocess blocker:
  `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authoritya964-formal-launch-blocked/`.

Authority-updated Primary source/tool validation:

- workflow `35673645036`;
- commit `5e88c18a2bd5ac937bec7380cf422875a20cc83e`;
- bounded Primary **358/358**;
- live handoff **11/11**;
- R01 early capsule **7/7**;
- R01 early launch **20/20**;
- R01 early results **20/20**;
- R01 failure pipeline **16/16**;
- M07 recovery-label binder Passed;
- M07 mutable-input recovery Passed;
- R01B lazy **10/10**;
- artifact `10672720137`;
- artifact SHA-256 `3d2c82e8972776945efe92dbee5efb70e451088ee37bbe11cfa087221d690a8f`.

This is Primary source/tool evidence only.

## Implementation

### Returned Local finding

At source `a964f79d...`, Local successfully completed all earlier retained-graph admission work:

- current/protected authority;
- exact source audits;
- retained evidence authentication;
- real graph-reuse bridge;
- 3-mode retained-ON early preflight;
- strict 8-side pilot seal;
- cached formal admission.

The nested early-authority defect is empirically closed.

Formal admission reached the first side launch in about 14.746 seconds.

The next boundary failed:

`R00 baseline: source pins differ from baseline provenance`

Pair `R00-OFF-NoPatch-formal-01` attempt 1:

- protected side A Passed;
- candidate side B exited before Player launch.

Local then performed the protocol-required whole-pair attempt 2 with the same bridge, seal, pair ID, order, and failed cumulative index.

Attempt 2 reproduced exactly:

- A Passed again;
- B failed again before Player launch;
- B console/failure receipts were byte-identical;
- no process remained.

Direct cause:

`run-h1-paired-performance.py` had authenticated bridge/seal authority in the parent process, but `build_command()` launched public `run-r00-players.py` without any retained side authority.

The child therefore called default current-pairing `verify_inputs` before Player launch.

### Repair 1 — H1FormalSideLaunchAuthority

New:

`Tools/AssemblyShadow/h1_formal_launch_authority.py`

For every bridge-bound **formal candidate side B** attempt, the paired driver creates one new:

`H1FormalSideLaunchAuthority`

The receipt binds:

- `side=B`;
- pairId;
- attempt;
- mode;
- AB/BA pair order;
- candidate project;
- exact per-side R00 runner output root;
- protocol;
- schedule;
- frozen build map;
- graph-reuse bridge;
- pilot verification seal;
- fixture manifest;
- Native ON receipt;
- Native OFF receipt;
- Editor replay receipt;
- current authority/paired-driver/R00-runner/R00-input/R00-results/early-verifier tool hashes.

The exact output-root binding prevents replaying one authority receipt into another subprocess output.

The authority cannot name an arbitrary historical revision.

### Repair 2 — child runner consumes only the bound H1 receipt

`run-r00-players.py` now has one H1-specific internal option:

`--h1-formal-launch-authority <receipt>`

It does **not** expose:

- raw historical revision;
- raw historical source-pin DTO;
- generic pairing override.

When the receipt is present, the child requires:

- explicit single R00 mode;
- `R01EarlyStartup`;
- exact project/mode/input/output receipt bindings.

It then:

1. verifies the formal authority;
2. revalidates its schedule/map/bridge/seal/input/tool bindings;
3. reconstructs `H1AuthenticatedGraphReuseAuthority` from the same graph bridge;
4. uses `verify_inputs_with_reuse`;
5. for ON modes, passes that same authority into nested Baseline/Control early preparation.

Without the receipt, public runner behavior remains current-pairing-only.

### Repair 3 — protected side A remains isolated

Only bridge-bound **formal candidate side B** receives a formal launch authority.

Protected side A receives none.

Prior/formal sample validation and final analysis reject retained authority on protected A.

### Repair 4 — parent receipt echo

A real candidate runner launch writes these bindings into `r00-player-launches.json`:

- `formalLaunchAuthority`;
- `graphReuseBridge`;
- `pilotVerification`;
- `buildMap`.

The paired parent marks a real runner receipt Passed only when the child echoes the exact parent-issued formal authority binding.

If the child exits before creating a real R00 launch receipt:

- the original runner failure is preserved;
- the parent authority receipt remains retained/hash-bound;
- no fake launch receipt is created;
- the side cannot pass.

### Repair 5 — retry/resume authority chain

Every formal candidate side-B attempt that was actually prepared/launched retains a hash-bound `formalLaunchAuthority`.

Bridge-bound resumed formal chains require that authority evidence on every non-skipped candidate attempt.

A skipped B side with no runner invocation does not fabricate one.

Whole-pair retry semantics remain unchanged.

### Repair 6 — final analysis authority proof

Before statistics, final analysis now verifies each formal candidate side-B authority against:

- pairId;
- attempt;
- mode/order;
- candidate project;
- exact runner output root;
- fixture/on/off/replay;
- frozen map;
- bridge;
- pilot seal;
- current tool hashes.

It requires protected side A to have no retained authority.

For a successful candidate runner receipt, the launch receipt must echo the same formal authority.

For a failed candidate attempt that ended before an R00 launch receipt, final analysis still verifies and retains the authority receipt without inventing launch evidence.

The existing strict R00/raw/result verification remains mandatory.

### Primary regression coverage

New bounded regression crosses the exact returned process boundary:

1. actual `run-h1-paired-performance.build_command` builds the candidate child command;
2. its argv is passed into actual `run-r00-players.main`;
3. formal authority verification supplies the authenticated pairing;
4. default `verify_inputs` is forced to fail if touched;
5. `verify_inputs_with_reuse` must receive the exact authority;
6. only the actual Player process is mocked.

Additional tests prove:

- schedule/map/bridge/seal/input/tool binding;
- mode/input/tool tampering rejection;
- exact runner-output binding;
- direct runner remains current-pairing-only without H1 authority;
- parent authority echo requirement;
- resumed formal authority retention;
- final analysis successful-authority verification;
- failed pre-launch authority evidence retention;
- protected side A authority rejection.

All earlier bridge/preflight/seal/cache/formal-batch regressions remain active.

## Local validation

Detailed authoritative plan:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`

Run it in order.

### Fresh current admission

Before bridge creation:

1. fresh V00 source/handoff/reproduction/protected authority;
2. sanctioned candidate installed-runtime receipt refresh when required by the new source pin;
3. candidate/protected installed-runtime verification;
4. full current Primary/Python regression;
5. exact source audits;
6. retained evidence authentication.

### Unity evidence

The current source delta modifies no Unity C#/asmdef/resource/Assets/Packages input.

The fresh `1076/1076` result from Local commit `d18a1fb...` may be classified:

`ReusedAuditedFromD18`

only after the exact 11-path audit passes.

A new Unity run is optional before bridge creation.

### Exact source scopes

Previous Primary source:

`a964f79d6ceba866c5956741a4a32e38ff8a6b5f → f1266a4d7f39a49523186b3dc63f9add9cc0e64c`

must equal exactly **11** non-metadata paths.

Retained graph:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3 → f1266a4d7f39a49523186b3dc63f9add9cc0e64c`

must equal exactly **20** non-metadata paths.

Any subset or superset fails.

### Create new bridge and seal

The a964 bridge/seal are historical and invalid as current authorities.

Create a new bridge, then a new strict 8-side pilot seal.

A standalone new 3-mode early preflight is not mandatory this cycle because the current 11-path delta does not modify R00 results, early results, or the preflight tool; record the prior passing preflight only as `ReusedAuditedFromD18`.

The fresh 8-side seal is mandatory.

### Start a new formal series

Do **not** use either failed a964 formal sample index as prior.

Start from the retained live pilot index using the new bridge and seal.

### First pair is the critical empirical closure

For new pair `R00-OFF-NoPatch-formal-01` attempt 1:

Protected A must:

- have no `formalLaunchAuthority`;
- remain default-current pairing;
- pass normally when otherwise valid.

Candidate B must:

- have a new `H1FormalSideLaunchAuthority`;
- bind exact pair/attempt/mode/order/project/output;
- bind exact current protocol/schedule/map/bridge/seal/fixture/on/off/replay/tool hashes;
- invoke child with `--h1-formal-launch-authority`;
- pass child authority validation;
- use retained `verify_inputs_with_reuse`;
- get past graph preparation;
- actually launch the candidate Player;
- produce a real R00 launch receipt;
- echo the exact same formal authority;
- echo the current graph bridge, pilot seal, and build map.

The previous source-pin error must not recur before Player launch.

If pair 1 fails before candidate Player launch, stop the new series and return to Primary.

### Continue formal batch

If pair 1 passes, continue all forty formal pairs under the unchanged batch/retry protocol.

Every actual candidate side-B formal attempt must carry a valid formal authority.

The batch still never auto-retries.

### Final analysis

Run bridge-aware final analysis after all formal pairs complete.

It must verify the complete formal authority chain before normal strict performance analysis.

Proceed to checkpoint/V05/M08 only if all mandatory evidence is complete.

## Failure evidence

### Formal authority creation/child validation failure

Retain:

- exact pair/attempt/mode/order;
- formal authority receipt;
- runner output root;
- command;
- parent/child logs;
- source/map/bridge/seal/input/tool binding diagnostic;
- proof no candidate Player launched if failure was pre-launch.

### Candidate Player/runtime failure

Retain:

- formal authority;
- real R00 launch receipt if created;
- Player PID/command/log/result;
- bridge/seal/map bindings;
- full pair evidence.

### Retry

Preserve the entire failed attempt and its unique authority.

Never overwrite it with the retry authority.

### Final analysis failure

Retain final sample index, all formal authorities, bridge/seal, analyzer failure receipt, and exact invalid authority/launch path.

Do not clean before checkpoint authentication.

## Alternatives

Do not:

- add a raw historical revision/source-pin option to `run-r00-players.py`;
- pass bridge authority directly on a generic CLI;
- give protected side A a formal retained authority;
- reuse an authority on a different pair/attempt/output root;
- reuse the a964 bridge or seal as current authority;
- chain the two a964 failed formal attempts into the new source series;
- weaken `verify_inputs` or `require_current_pairing`;
- skip parent echo validation;
- fabricate an R00 launch receipt for pre-launch failures;
- auto-retry or side-only retry;
- delete slow/failed samples;
- edit protocol/schedule/map/statistics after observing timings;
- begin R02.

If honest retained execution still cannot pass, return to Primary; fallback is a fresh current-pairing controlled graph, not verifier weakening.

## Risks

- Current source pin again requires a new installed-runtime receipt before bridge creation.
- New bridge/seal are required because formal runner/verifier tool hashes changed.
- The full 8-side seal remains expensive.
- Forty formal pairs remain long-running.
- Any source/tool change invalidates bridge/seal/formal authorities.
- Final analysis must validate all formal authorities and strict raw evidence.
- Prior 28 Python environment skips remain explicit, not Passed.

## Local correction boundary

Local may adjust only:

- absolute paths;
- new evidence/output roots;
- executable permissions / PYTHONPATH;
- bounded command syntax;
- explicit protocol-valid whole-pair retry number.

Local must not alter:

- formal authority schema/tool set/output binding;
- child internal authority semantics;
- graph-reuse 20-path policy;
- source/runtime/protected pins;
- default R00 current-pairing behavior;
- bridge/seal/map/protocol/schedule identities;
- pair ordering/retry/statistics;
- final analyzer logic.

Any non-trivial source/tool correction returns to Primary.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress**.

Still required:

- new bridge;
- new strict seal;
- empirical first-pair formal subprocess authority closure;
- all 40 formal pairs;
- final analysis;
- checkpoint;
- V05;
- genuinely independent M08.

M08 must explicitly review the parent→child formal authority receipt chain, protected-side isolation, replay protection, retry evidence, and final-analysis authority validation.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**. Human approval must then be explicit.

**Do not begin R02.**
