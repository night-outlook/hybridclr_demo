# R01B H1 — Current Primary Implementation

## Status

Latest Local return: `65f47f6bf62fe8889a3b71ed629f9fd06f3a489a`

Candidate source/tool anchor: `91ac4db31cec704551c7db05bd918c8d5695ce83`

H1 remains `InProgress`; `humanGatePassed=false`; `mayEnterR02=false`.

## Returned blocker

The source `24a0d3af...` Local cycle passed current authority, current Python regression, exact source audits, complete retained artifact authentication, and a new graph bridge.

The strict seal failed before deep reconstruction because retained pilot rows bind the historical runner that actually produced them, while `_load_prior` compared them against the current runner.

Historical retained runner:

`afc0b649579ebd497be493be9fd39fcfe19e3ba3074d6d6679e009975d21a07c`

Current runner at that Local cycle:

`a8de4dc1052306923f7aef529442d4c2012cc959c5dea58da6f15785caacd280`

Both identities are legitimate but serve different roles.

## Primary design

### Immutable historical runner provenance

The current graph bridge now binds `retainedPilotRunner`.

It is reconstructed from the Git blob at fixed retained graph revision `69130bbb...`; it is not supplied by Local or by a sample index.

Bridge creation records it and bridge verification recomputes it.

### Current runner remains mandatory for new work

The historical binding is accepted only for retained rows whose phase is `pilot`.

Every new formal attempt continues to require the current runner binding, including the H1 formal side-B subprocess-authority path from the previous repair.

### Seal ordering

The production seal entrypoint now performs full bridge authentication before retained-pilot loading.

Thus the exception cannot be reached from an unauthenticated pilot index.

### Formal resume

A new formal series starts from the retained pilot index.

During formal prior-index validation, compact bridge authentication supplies the exact historical pilot-runner provenance for pilot rows.

Any formal row still requires the current runner.

### Fast preflight

New `verify-h1-retained-pilot-admission.py` performs only bridge + pilot-history admission.

It selects the four latest Passed pilots and records their exact historical runner/launch bindings without rehashing/reconstructing the eight R00 graphs.

Run it before the expensive seal.

## Regression coverage

Primary added a real retained-style pilot fixture based on the Git-derived runner at `69130bbb...`.

Tests prove:

- the exact historical SHA is `afc0b649...`;
- it differs from the current runner;
- the actual seal entrypoint accepts it only with authenticated bridge authority;
- the actual seal reaches 8 deep verifications;
- no bridge rejects it;
- wrong hash rejects it;
- wrong path rejects it;
- bridge switching rejects it;
- the admission preflight accepts it without invoking deep R00 verification.

## Source scope

Previous Primary delta: exactly 9 non-metadata paths.

Full retained graph delta: exactly 22 non-metadata paths.

The two new retained paths relative to the last cycle are:

- `Tools/AssemblyShadow/tests/test_h1_retained_pilot_runner.py`;
- `Tools/AssemblyShadow/verify-h1-retained-pilot-admission.py`.

No Player/runtime/native/Unity asset/measurement/protocol/schedule/graph-production source changed.

## Primary validation

Workflow `35680306116` passed bounded **364/364** plus all live handoff, R01, M07 recovery, and lazy suites.

## Next Local cycle

Run:

1. fresh authority / current Python;
2. exact 9/22 path audits;
3. retained evidence audit;
4. new graph bridge;
5. **retained pilot admission preflight**;
6. new strict 8-side seal;
7. new formal series from retained pilot index;
8. all 40 formal pairs;
9. final strict analysis;
10. checkpoint / V05 / independent M08 if eligible.

Prior source bridges/seals/failed formal attempts remain historical only.

Do not begin R02.
