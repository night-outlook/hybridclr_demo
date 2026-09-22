# Current Status

- Candidate build-input/tool source anchor: `91ac4db31cec704551c7db05bd918c8d5695ce83`.
- Latest Local return: `65f47f6bf62fe8889a3b71ed629f9fd06f3a489a`.
- Latest authenticated Local checkpoint: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority24a0-pilot-seal-blocked/`.
- Reusable retained graph/pilot checkpoint: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/`.
- Gate: `H1 / InProgress / AwaitingRetainedPilotAdmissionEmpiricalClosure`.
- Last independent M08: `FAIL` (historical; not rerun).
- Human gate passed: `false`.
- May enter R02: `false`.

## Latest Local result

At source `24a0d3af...`, Local completed fresh authority, current Python validation, exact source audits, retained evidence authentication, and creation of a new current graph-reuse bridge.

Key results:

- bounded Primary: 359/359;
- Python inventory: 1016 passed / 28 explicit environment skips / 0 failures-errors;
- Unity 1076/1076: `ReusedAuditedFromD18`;
- retained-ON 3/3 preflight: `ReusedAuditedFromD18`;
- exact previous-source delta: 11 paths;
- exact retained-graph delta: 20 paths;
- retained V04 / Player / latest checkpoint manifests: authenticated;
- 33,792 retained files / 1,606,993,133 bytes: zero mismatches;
- new graph bridge: Passed.

The mandatory new strict pilot seal then failed **before any deep verification**:

`Prior A diagnostic runner binding mismatch`

The retained pilot index correctly records the runner that produced those pilots:

`run-r00-players.py SHA-256 afc0b649579ebd497be493be9fd39fcfe19e3ba3074d6d6679e009975d21a07c`

That hash is the exact runner at retained graph anchor `69130bbb...` and at previous source `a964f79d...`.

The current formal-subprocess repair intentionally changed the runner implementation. `_load_prior` incorrectly required historical pilot provenance to equal the current runner before using the already supplied graph bridge.

No seal receipt was produced and `deepLaunchVerificationCount=0`. No new formal series started.

## Current Primary repair

Source anchor `91ac4db31cec704551c7db05bd918c8d5695ce83` separates historical pilot provenance from current execution identity.

### Bridge-bound retained pilot runner

`H1GraphReuseBridge` now contains:

`retainedPilotRunner`

Its value is not caller-supplied.

Primary derives it directly from:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3:Tools/AssemblyShadow/run-r00-players.py`

using Git bytes and SHA-256.

Bridge verification recomputes that value and requires exact equality.

The fixed retained runner SHA-256 is:

`afc0b649579ebd497be493be9fd39fcfe19e3ba3074d6d6679e009975d21a07c`.

### Seal admission ordering

`seal-h1-pilot-verification.py` now:

1. validates protocol/schedule/build map;
2. fully authenticates the supplied graph bridge;
3. only then loads retained pilot history using that authenticated authority;
4. performs the existing strict 8-side reconstruction.

Therefore historical runner provenance is never accepted before bridge authentication.

### Loader semantics

`_load_prior` now distinguishes row phase:

- retained **pilot** row + authenticated graph authority → runner must equal bridge-derived `retainedPilotRunner`;
- new **formal** row → runner must equal current `runner_binding()`;
- pilot row without authenticated retained authority → current runner remains required;
- arbitrary historical runner path/hash is rejected.

For formal resume, compact bridge authentication supplies only the retained pilot provenance needed to validate pilot rows. Formal rows remain current-runner-only.

### Fast admission preflight

New:

`Tools/AssemblyShadow/verify-h1-retained-pilot-admission.py`

Before the 1.6 GB seal it:

- full-authenticates the current bridge;
- loads the complete retained pilot history under bridge-derived runner provenance;
- verifies exact protocol/schedule/map/pilot bindings;
- selects the four latest Passed pilot pairs;
- performs **zero deep R00 reconstructions**;
- writes `H1RetainedPilotAdmissionPreflight`.

It is diagnostic only and does not replace the strict seal.

### Regression coverage

Primary uses the **real Git-derived retained runner hash**, not a synthetic historical hash.

The actual seal entrypoint regression:

- invokes `seal-h1-pilot-verification.py`;
- loads a retained-style pilot index whose A/B diagnostics bind the Git-derived historical runner;
- uses an authenticated bridge authority;
- reaches exactly 8 deep side verifications;
- produces a Passed strict seal.

Negative tests reject:

- missing authenticated bridge authority;
- wrong retained runner SHA-256;
- wrong retained runner path;
- bridge switching.

The admission-preflight entrypoint is also executed and asserted to perform no deep R00 verification.

## Source scope

Previous Primary source `24a0d3af... → 91ac4db3...`: exactly **9 non-metadata paths**.

Retained graph `69130bbb... → 91ac4db3...`: exactly **22 non-metadata paths**.

No Unity Assets/Packages/C#/asmdef, native runtime, measurement source, protocol/schedule/map producer, graph/Player binary source, or preregistration source changed.

## Primary validation

Authority-updated workflow `35680306116` at commit `4732dc82...` passed:

- bounded Primary: **364/364**;
- live handoff: **11/11**;
- R01 early capsule: **7/7**;
- R01 early launch: **20/20**;
- R01 early results: **20/20**;
- failure pipeline: **16/16**;
- both M07 PowerShell recovery regressions: Passed;
- R01B lazy: **10/10**.

Authority-updated artifact `10675141839`, SHA-256 `726abdb0692a25cad6c9942321fc3e5eb3e48bb4f191d00629816560f32328ce`. Exact live handoff workflow `35680823080` at `6d27e9bf...` subsequently passed the same **364/364** bounded result plus all auxiliary suites; artifact `10674618336`, SHA-256 `3ee6730b7a92e185bf9f3f990ba2c1266780ddccfa305e984f463d86803dd6c0`.

## Required next action

Local must restart fresh V00 and create a **new** bridge because source/verifier hashes changed.

Then run the new retained-pilot admission preflight. Only if it passes, run a new strict 8-side seal.

If the seal passes, start a new formal series from the retained pilot index and empirically close the already implemented formal subprocess authority boundary.

All prior bridges, seals, blocked attempts, and checkpoints remain historical evidence.

H1 remains `InProgress`. Do not begin R02.
