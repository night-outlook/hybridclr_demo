# Static Review — Bridge-Aware Retained Pilot Runner Admission

## Verdict

**PASS for Primary → Local Validation handoff**, subject to real current bridge, admission preflight, strict seal, and subsequent formal execution.

Reviewed source/tool anchor:

`91ac4db31cec704551c7db05bd918c8d5695ce83`

## Finding

The retained pilot index is immutable historical evidence.

Its A/B diagnostic `runner` fields correctly identify the `run-r00-players.py` implementation that produced those pilots.

After the formal subprocess repair, the current runner changed. The old loader compared historical pilot provenance to the current runner before authenticating the supplied bridge.

That conflated provenance identity with current execution identity.

## Review of correction

### Fixed-anchor derivation

No API accepts a historical runner hash.

`h1_graph_reuse.retained_pilot_runner_binding(project)` derives the only accepted runner from Git:

- revision: `69130bbb3a6df516916dddb5ad263799a7c6e5e3`;
- path: `Tools/AssemblyShadow/run-r00-players.py`;
- expected SHA-256: `afc0b649579ebd497be493be9fd39fcfe19e3ba3074d6d6679e009975d21a07c`.

The path in the resulting binding remains the canonical current project path, matching retained receipt provenance.

### Bridge binding

`H1GraphReuseBridge` contains `retainedPilotRunner`.

Both full and compact bridge verification recompute it from Git and require equality.

Therefore a caller cannot make an arbitrary historical runner acceptable by editing the pilot index or bridge JSON.

### Loader phase isolation

For a row whose phase is `pilot`:

- authenticated retained authority present → exact `retainedPilotRunner` is required;
- authority absent → current `runner_binding()` is required.

For a row whose phase is `formal`:

- current `runner_binding()` is always required.

The historical exception therefore cannot authorize old runners for new measurements.

### Bridge-before-loader seal ordering

The sealer now full-authenticates the bridge before calling `_load_prior`.

This directly fixes the returned ordering defect.

Formal resume derives only compact bridge authority before validating retained pilot rows.

### Preflight

`verify-h1-retained-pilot-admission.py` provides a cheap fail-closed gate.

It verifies the current bridge and retained pilot history/selection but deliberately does not invoke `r00_results.verify_suite`.

The full 8-side strict seal remains mandatory.

## Regression review

The new regression locks the exact historical SHA from real Git.

The positive test executes the actual seal entrypoint and reaches 8 deep verification calls.

Negative coverage:

- no bridge authority;
- wrong historical SHA;
- wrong historical path;
- bridge switching.

A separate actual preflight test asserts four-pilot admission with zero deep calls.

Existing formal subprocess, bridge, nested early, cache, batch, and final-analysis regressions remain active.

## Scope

`24a0d3af... → 91ac4db3...`: exactly 9 non-metadata paths.

`69130bbb... → 91ac4db3...`: exactly 22 non-metadata paths.

No Unity/runtime/native/measurement/protocol/schedule/controlled-build source changed.

## Primary validation

Exact live handoff workflow `35680823080` at `6d27e9bf...` passed bounded **364/364**, live handoff **11/11**, R01 early capsule **7/7**, early launch **20/20**, early results **20/20**, failure pipeline **16/16**, both M07 recovery regressions, and lazy **10/10**.

Artifact `10674618336` has SHA-256 `3ee6730b7a92e185bf9f3f990ba2c1266780ddccfa305e984f463d86803dd6c0`.

## Residual empirical requirements

Local must prove the path on real retained evidence:

- refreshed current authority;
- exact 9/22 path audits;
- new graph bridge containing the Git-derived retained runner;
- new retained-pilot admission preflight;
- new strict 8-side seal;
- new formal series;
- first-pair formal subprocess authority closure;
- all 40 formal pairs;
- final analysis;
- checkpoint / V05 / independent M08.

H1 remains `InProgress`. Do not begin R02.
