# R01B H1 — Current Primary Implementation

## Status

Latest Local return:

`21caaecc315623ec10c779af04d563ed7badeac2`

Candidate build-input/tool source anchor:

`a964f79d6ceba866c5956741a4a32e38ff8a6b5f`

H1 remains `InProgress`; `humanGatePassed=false`; `mayEnterR02=false`.

## Returned Local blocker

The real graph-reuse bridge passed and authenticated the retained candidate graph correctly.

The strict seal still failed before a seal receipt because bridge authority was lost after the outer R00 input check. A retained candidate ON launch with `R01EarlyStartup` entered `r01_early_results._prepare`, which called default current-pairing `verify_inputs` and reproduced:

`R00 baseline: source pins differ from baseline provenance`

Local's focused diagnostic proved outer reuse verification passed first.

No formal Player or performance observation exists from that attempt.

## Primary correction

### Nested early authority

`r01_early_results._prepare` now has one optional keyword-only internal authority parameter.

When absent, behavior is unchanged.

When present, it delegates graph admission to the existing `verify_inputs_with_reuse` authority-aware path.

`r00_results.verify_suite` threads the exact already-authenticated authority through nested early preparation.

This is not a new bridge creation point and not a new CLI option.

### Restricted scope

Retained authority at the nested early boundary is valid only for:

- `Baseline`;
- `Control`.

Those are exactly the early modes used by the retained performance ON observations.

`OrdinaryFirst`, failures, and guard modes fail closed if a retained authority is supplied.

Direct `r01_early_results.verify_suite` remains current-pairing-only.

### Bridge binding

`r01_early_results.py` is now in both:

- the exact retained-graph source-transition allowlist;
- `H1GraphReuseBridge.verifierBindings`.

The new retained-graph allowlist contains exactly 17 non-metadata paths.

### Read-only early preflight

Primary added `verify-h1-retained-early-reuse.py`.

It full-verifies the current bridge then strictly reconstructs candidate side B for all three ON pilot modes:

1. `R00-ON-NoPatch` — early `Baseline`;
2. `R00-ON-P01` — early `Control`;
3. `R00-ON-P03` — early `Control`.

This is an early diagnostic gate before paying the full 8-side seal cost.

It does not replace or weaken the pilot seal.

## Source scope

Previous Primary source `6dd964c0... → a964f79d...` has exactly 9 non-metadata paths:

- `.github/workflows/h1-bee-primary.yml`;
- `Tools/AssemblyShadow/README.md`;
- `Tools/AssemblyShadow/h1_bee_primary_tests.py`;
- `Tools/AssemblyShadow/h1_graph_reuse.py`;
- `Tools/AssemblyShadow/r00_results.py`;
- `Tools/AssemblyShadow/r01_early_results.py`;
- `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`;
- `Tools/AssemblyShadow/tests/test_h1_retained_early_preflight.py`;
- `Tools/AssemblyShadow/verify-h1-retained-early-reuse.py`.

The full retained graph transition `69130bbb... → a964f79d...` has exactly 17 paths defined by machine authority and bridge code.

No Player/runtime/measurement/protocol/schedule/build-map source changed.

## Validation support

Bounded Primary: **353/353**.

New tests prove:

- real source-transition authority;
- nested actual `_prepare` retained path;
- no fallback to current pairing in that path;
- explicit-keyword propagation from R00;
- direct early verifier remains strict current;
- negative mode restrictions;
- exact three-mode retained-ON preflight;
- all previous seal-cache/formal-batch/final-analysis contracts.

## Next Local cycle

Fresh authority and inventories happen before bridge creation.

Then:

1. new bridge;
2. 3-mode retained-ON early preflight;
3. new 8-side pilot seal;
4. 40 formal pairs via batch runner;
5. final bridge-aware strict analysis;
6. checkpoint / V05 / independent M08 if eligible.

Do not begin R02.
