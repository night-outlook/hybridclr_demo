# Static Review — Nested Early Retained-Authority Propagation

## Verdict

**PASS for Primary → Local Validation handoff**, subject to real bridge/preflight/seal/formal execution.

Reviewed source/tool anchor:

`a964f79d6ceba866c5956741a4a32e38ff8a6b5f`

## Finding

The previous bridge implementation correctly authenticated retained graph reuse and correctly supplied its authority to outer `r00_results.verify_suite`.

However, strict modern ON verification has a second graph-admission boundary: `r01_early_results._prepare` reconstructs the exact early capsule.

That function used default `verify_inputs`, so the retained authority was dropped and current-pairing equality was reapplied.

The real Local failure and focused reproduction identify this boundary directly.

## Review of correction

The correction is deliberately narrow.

### Default semantics preserved

`r00_player_inputs.require_current_pairing` is unchanged.

`r00_player_inputs.verify_inputs` remains default current-pairing admission.

Direct `r01_early_results.verify_suite` remains current-pairing-only.

No CLI can specify a historical source pairing.

### Internal propagation only

`r01_early_results._prepare` accepts a keyword-only `pairing_authority`.

The only production retained-performance caller is the already bridge-aware `r00_results.verify_suite`, which passes its same authority object into nested preparation.

No second bridge lookup or authority construction occurs below that boundary.

### Scope restriction

When authority is non-null, `_prepare` requires the requested modes to be a subset of:

- `Baseline`;
- `Control`.

This matches the R00 performance early-capsule path.

Any ordinary/failure/guard early mode rejects the retained authority before graph verification.

### Bridge invalidation

Because the early verifier now participates in retained historical pairing, `r01_early_results.py` is added to both the bridge verifier binding and exact source-transition allowlist.

Therefore a future change cannot silently reuse an old bridge.

## Regression review

Primary includes a real-transition test that:

1. authenticates the actual `69130bbb...` retained transition;
2. constructs the corresponding bridge-style authority;
3. executes the actual nested `r01_early_results._prepare` with the performance `Baseline` mode;
4. forces default `verify_inputs` to raise if called;
5. proves `verify_inputs_with_reuse` receives the exact authority.

Additional source-contract checks require R00 to pass authority by explicit keyword and require direct early verification to expose no historical authority parameter.

Negative tests reject `OrdinaryFirst`, `MetadataFailure`, and `Type`.

## Diagnostic improvement

The new read-only retained-ON preflight full-reauthenticates the real bridge and strict-verifies candidate side B for NoPatch/P01/P03.

This empirically crosses both `Baseline` and `Control` nested early paths before the expensive full seal.

Its regression ensures:

- exactly those three ON modes;
- side B only;
- one common authority;
- missing ON inventory fails before strict verification.

## Scope audit

The previous source-anchor delta is exactly 9 non-metadata tooling/test/CI paths.

The full retained-graph transition is exactly 17 non-metadata paths, still confined to CI and `Tools/AssemblyShadow`.

No Unity C#/asmdef, Player/runtime/native code, measurement source, protocol, schedule, map producer, preregistration producer, or R00 Player runner changed.

## Primary validation

Workflow `35614424960` at authority successor `76577900...` passed:

- bounded Primary: **353/353**;
- live committed handoff: **11/11**;
- R01 early capsule: **7/7**;
- early launch: **20/20**;
- early results: **20/20**;
- failure pipeline: **16/16**;
- M07 recovery-label binder: Passed;
- M07 mutable-input recovery: Passed;
- R01B lazy: **10/10**.

## Residual empirical requirements

Local must prove the new path against the retained real evidence:

- new current installed-runtime authority;
- exact source audits;
- new graph bridge;
- 3-mode retained-ON preflight;
- new 8-side strict pilot seal;
- 40 formal pairs;
- final strict paired analysis;
- authenticated checkpoint;
- V05 and genuinely independent M08.

H1 remains `InProgress`.

Do not begin R02.
