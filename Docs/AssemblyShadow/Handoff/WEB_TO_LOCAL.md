# Primary Implementation → Local Validation

## Objective

Validate bridge-aware retained pilot runner provenance admission at source/tool anchor:

`91ac4db31cec704551c7db05bd918c8d5695ce83`

Then, if the new admission preflight and strict seal pass, continue in one Local cycle through a new formal series, all 40 formal pairs, final strict analysis, checkpoint, V05, and independent M08 when eligible.

Latest Local return:

`65f47f6bf62fe8889a3b71ed629f9fd06f3a489a`

H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

**Do not begin R02.**

## Source targets

Machine authority:

`Docs/AssemblyShadow/Handoff/source-targets.json`

Candidate identities:

| Repository | Branch | Build/runtime identity |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | source/tool anchor `91ac4db31cec704551c7db05bd918c8d5695ce83` |
| `night-outlook/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| `night-outlook/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| `night-outlook/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |

Protected profile-1 family remains unchanged.

Environment target:

`Unity 2022.3.62f2 / StandaloneOSX / arm64`

The branch checkout HEAD may be a later metadata-only successor. Record checkout HEAD separately from source/tool anchor.

Evidence roots to retain include:

- retained V04 graph/pilots:
  `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/`;
- latest blocked cycle:
  `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority24a0-pilot-seal-blocked/`;
- every earlier blocked checkpoint referenced from those manifests.

Authority-updated Primary validation:

- workflow `35680306116`;
- commit `4732dc8270b51fc5ef0fb880d3d86cd92327da17`;
- bounded Primary **364/364**;
- live handoff **11/11**;
- R01 early capsule **7/7**;
- R01 early launch **20/20**;
- R01 early results **20/20**;
- R01 failure pipeline **16/16**;
- both M07 PowerShell recovery regressions Passed;
- R01B lazy **10/10**;
- artifact `10675141839`;
- artifact SHA-256 `726abdb0692a25cad6c9942321fc3e5eb3e48bb4f191d00629816560f32328ce`.

This is Primary source/tool evidence only.

## Returned Local finding

At source `24a0d3af...`, Local passed:

- current/protected authority;
- current bounded/Python validation;
- exact 11-path and 20-path source audits;
- complete retained artifact/file authentication;
- a new current graph bridge.

The new strict seal then failed **before deep verification**:

`Prior A diagnostic runner binding mismatch`

The retained pilot index correctly binds the runner that created those pilot diagnostics:

`afc0b649579ebd497be493be9fd39fcfe19e3ba3074d6d6679e009975d21a07c`

That is the exact `run-r00-players.py` at retained graph anchor `69130bbb...`.

The current formal-subprocess repair intentionally changed the runner implementation.

The defect was that `_load_prior` treated historical pilot provenance as if it were new-execution current runner identity, and rejected it before bridge-aware reconstruction.

No seal was created; `deepLaunchVerificationCount=0`; no new formal series started.

## Implementation

### Bridge now authenticates historical pilot runner provenance

`H1GraphReuseBridge` now contains:

`retainedPilotRunner`

Primary derives it only from Git bytes at:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3:Tools/AssemblyShadow/run-r00-players.py`

Bridge verification recomputes and requires exact equality.

Expected retained runner SHA-256:

`afc0b649579ebd497be493be9fd39fcfe19e3ba3074d6d6679e009975d21a07c`

No caller can provide another historical runner hash/path.

### Seal authenticates bridge before loading pilots

Production seal ordering is now:

1. protocol/schedule/map validation;
2. **full graph bridge authentication**;
3. retained pilot-index loading using the authenticated bridge authority;
4. strict 8-side R00 reconstruction;
5. immutable stat/file seal.

The historical exception therefore cannot be used without a valid bridge.

### Pilot vs formal runner identity is explicit

In `_load_prior`:

- retained row with `phase=pilot` + authenticated retained authority:
  exact bridge-derived historical runner is required;
- pilot without retained authority:
  current runner is required;
- every row with `phase=formal`:
  current runner is required.

Thus the historical pilot exception cannot authorize an old runner for any new formal measurement.

For formal resume, compact bridge authentication supplies only the historical provenance needed to validate retained pilot rows. Formal rows remain current-runner-only.

### New fast retained-pilot admission preflight

New:

`Tools/AssemblyShadow/verify-h1-retained-pilot-admission.py`

It:

1. validates protocol/schedule/map;
2. full-authenticates the current graph bridge;
3. bridge-validates the complete retained pilot history;
4. checks historical A/B runner bindings;
5. selects the four latest Passed pilot pairs;
6. performs **zero deep R00 reconstruction**;
7. writes `H1RetainedPilotAdmissionPreflight`.

Run this before the expensive seal.

It does not replace the seal.

### Regression coverage

The tests use the real Git-derived historical runner, not a synthetic accepted hash.

The exact historical SHA is locked to:

`afc0b649579ebd497be493be9fd39fcfe19e3ba3074d6d6679e009975d21a07c`.

The actual production seal entrypoint test:

- receives a retained-style pilot index;
- fully authenticates a bridge authority;
- admits the historical runner;
- reaches all **8 deep side verifications**;
- creates a Passed strict seal.

Negative tests reject:

- no authenticated bridge authority;
- wrong historical runner SHA;
- wrong runner path;
- bridge switching.

The new admission-preflight entrypoint is separately executed and asserted to perform no deep R00 verification.

All previous formal subprocess, nested early, cache, batch, and final-analysis regressions remain active.

## Source scopes

Previous Primary source:

`24a0d3af... → 91ac4db3...`

must equal exactly **9** non-metadata paths.

Retained graph:

`69130bbb... → 91ac4db3...`

must equal exactly **22** non-metadata paths.

The detailed exact sets are in:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`

No Unity C#/asmdef/Assets/Packages, native runtime, measurement source, protocol, schedule, graph/build-map producer, or Player binary source changed.

## Local validation

Run the detailed plan in order.

### Before bridge creation

1. fresh source/handoff/reproduction/protected authority;
2. sanctioned candidate installed-runtime receipt refresh if required by the new source pin;
3. candidate/protected installed-runtime verification;
4. current bounded and full Python regression;
5. exact 9/22 source audits;
6. retained evidence authentication.

The historical Unity 1076/1076 result may remain `ReusedAuditedFromD18` only after the 9-path audit passes.

### Create a new bridge

Do not reuse the 24a bridge.

Create a new bridge and require:

- current source `91ac4db31cec704551c7db05bd918c8d5695ce83`;
- exact 22-path transition;
- current runtime/map/verifier bindings;
- exact `retainedPilotRunner` path;
- exact retained runner SHA `afc0b649...`.

### Run retained-pilot admission preflight

Before sealing:

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

- `H1RetainedPilotAdmissionPreflight / Passed`;
- retained runner matches `afc0b649...`;
- complete five-attempt historical pilot inventory;
- four selected Passed pilots;
- all selected A/B diagnostic runner bindings equal the same historical runner;
- exact launch bindings;
- zero deep R00 reconstruction.

If this fails, **stop before seal** and return to Primary.

### Create a new strict seal

Only after the admission preflight passes, run the normal bridge-bound 8-side seal.

Require `deepLaunchVerificationCount=8`, stable file guards, and the complete retained attempt digest.

Historical runner is pilot provenance only.

### Start a new formal series

Start from the retained pilot index.

Do not chain any historical failed formal index.

For first formal pair:

- protected A uses current runner and no retained authority;
- candidate B uses **current runner**, not the historical pilot runner;
- candidate B gets its unique `H1FormalSideLaunchAuthority`;
- child passes retained graph preparation and actually launches the Player;
- real R00 receipt echoes the formal authority/bridge/seal/map.

If pair 1 fails before candidate Player launch, stop and return to Primary.

If it passes, continue all 40 formal pairs with the existing batch/retry protocol.

### Final analysis

Run the existing bridge-aware strict analyzer after all 40 pairs complete.

It must preserve the historical-pilot/current-formal runner distinction while verifying all formal authorities and raw performance evidence.

Proceed to checkpoint/V05/M08 only if mandatory V04 is complete.

## Failure evidence

### Admission preflight failure

Retain:

- bridge;
- retained-pilot admission output/failure;
- recorded vs expected runner binding;
- pilot pair/side;
- exact protocol/schedule/map/pilot bindings;
- proof no deep seal ran.

### Seal failure

Retain:

- passed admission preflight;
- bridge;
- exact side/mode;
- runner binding;
- strict R00 error;
- seal stdout/stderr and duration.

### Formal failure

Retain:

- current runner binding;
- formal launch authority;
- child command/log/receipt;
- bridge/seal/map bindings;
- process cleanup evidence;
- any whole-pair retry.

Do not clean before authenticating the new checkpoint.

## Alternatives

Do not:

- edit the retained pilot index to the current runner;
- accept a caller-supplied historical runner hash;
- broaden historical runner use to formal rows;
- weaken current formal runner validation;
- reuse an old bridge/seal as current authority;
- skip the admission preflight;
- treat the admission preflight as a substitute for the strict seal;
- chain historical failed formal attempts into the new series;
- weaken graph/source pairing;
- auto-retry or side-only retry formal pairs;
- edit protocol/schedule/map/statistics after timings;
- begin R02.

If the fixed historical provenance cannot authenticate honestly, return to Primary; the fallback remains rebuilding a fresh current-pairing graph, not rewriting provenance.

## Risks

- Current source pin changes require a fresh candidate installed-runtime receipt before bridge creation.
- The retained-pilot admission preflight is cheap relative to the seal but does not replace deep graph verification.
- The strict 8-side seal remains intentionally expensive and must run after the admission preflight.
- Historical pilot runner provenance is valid only for retained pilot diagnostics; any leakage into new formal rows is a hard failure.
- New formal attempts must use the current runner and current per-attempt formal authority.
- Any source/tool/verifier change invalidates the current bridge and any seal/formal authorities derived from it.
- Forty formal A/B pairs and final strict analysis remain intrinsically long-running.
- Reused Unity/retained-ON evidence must remain explicitly classified as reused, not fresh current-source execution.
- Environment-bound Python skips remain non-Passed evidence.

## Local correction boundary

Local may adjust only paths/output roots, permissions/PYTHONPATH, bounded command syntax, and protocol-valid whole-pair retry numbers.

Local must not alter retained runner policy, 22-path allowlist, bridge/admission/seal semantics, source/runtime pins, current formal runner rules, pairing verification, graph/map/protocol/schedule identities, or analyzer logic.

Any non-trivial source/tool correction returns to Primary.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress**.

Still required:

- new bridge;
- retained-pilot admission preflight;
- strict seal;
- first formal current-runner closure;
- 40 formal pairs;
- final analysis;
- checkpoint;
- V05;
- independent M08.

M08 must explicitly review historical pilot provenance vs current formal runner identity.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**.

**Do not begin R02.**
