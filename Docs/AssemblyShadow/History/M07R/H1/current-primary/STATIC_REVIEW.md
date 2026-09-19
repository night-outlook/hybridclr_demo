# Static Review — V04 Closure Repairs after Local `f829db51...`

## Verdict

**PASS for Primary → Local Validation handoff**, subject to real Unity/IL2CPP validation.

Reviewed source anchor:

`925e84d7b653bc7434482e6f4fbde39a4d9fcd0e`

No claim is made here for V04 runtime completion, performance acceptance, V05, M08 PASS, or Human Review Gate approval.

## Q04 history review

The early Q04 terminal transaction remains unchanged.

The only semantic adjustment is to late observation:

- before terminal failure / in an eligible transaction: selected closure use remains forbidden;
- after Q04 has already sealed `Failed`: normal host baseline use of registered candidates is observable and may be appended;
- non-candidate identities are always invalid;
- existing first-use records cannot change;
- Control and initializer published worlds do not receive this exception.

This is consistent with the process-lifetime first-use registry: a late host observation after terminal pre-publication failure cannot retroactively make the already failed transaction invalid for a second reason.

## Dense runtime review

Generator and Player now agree exactly on:

- namespace `AssemblyShadow.Dense`;
- type-name formula;
- rows 4095/4096;
- return formula `fixtureId * 10000 + row`.

The Player still requires the manifest to pass the deterministic-v2 admission contract before loading either assembly.

## Performance review

### Previous gap

Comparability checked four controlled Player builds but did not authenticate the side fixture/replay graph against those exact baselines.

### New fail-closed boundary

The build-map validator now binds:

- graph baseline/runtime/platform;
- graph controlled NativeOn path/hash;
- replay graph identity;
- controlled ON/OFF receipts.

The runner calls the strict validator before sampling.

### New producer path

`-ControlledPerformanceBuilds` creates the controlled ON/OFF Players before fixture finalization, under one baseline ID, so M07's existing fixture/replay producer naturally binds the controlled NativeOn world.

No performance thresholds, sample schedule, outlier rule, operation inventory, memory semantics or expected A/B differences changed.

## Stale-test review

The two broad-suite failures reported by Local were stale ownership assumptions.

They are replaced with semantic/owner-aware tests rather than deleted or skipped.

## Source authority

Only `hybridclr_demo` changes.

HybridCLR, HybridCLR Unity and IL2CPP candidate pins remain unchanged.

Protected profile-1 pins remain unchanged.

No expansion of `metadata_only`, no weakening of `verify_demo`, runtime ABI/capacity/index rules, protected refs, or H1 gate conditions.

## Residual Local evidence

Local must still prove:

1. broad test suites are clean at the new source;
2. Q04 post-host strict verification passes while early terminal state stays unchanged;
3. dense fixtures execute all four boundary methods;
4. both controlled-performance M07 workflows produce self-consistent graph receipts;
5. the strict freezer passes only those graphs;
6. all pilots pass;
7. formal sampling/analysis completes;
8. checkpoint retention is complete;
9. V05 + independent M08 only after V04 closes.

## Gate

H1: `InProgress`.

Historical M08: `FAIL`.

`humanGatePassed=false`.

`mayEnterR02=false`.

Do not begin R02.

## Final Primary CI

Authority-consistent workflow `35449924454` passed 323/323 bounded tests plus 11/11 handoff, 7/7 early-capsule, 20/20 early-launch, 20/20 early-results, 16/16 failure-pipeline and 10/10 lazy-contract tests. Artifact `10586344220`; ZIP SHA-256 `a7f8d4f910057383d56635330e71db27107bd1314d218d32e80e6f08b133347e`.

## Final committed handoff verification

The exact live handoff commit `08f805da9ea8e479801f10d3a4fbb7af0a70a123` passed workflow `35450199014` with 323/323 bounded tests plus 11/11 handoff, 7/7 early-capsule, 20/20 early-launch, 20/20 early-results, 16/16 failure-pipeline and 10/10 lazy-contract tests. Artifact `10586482880`, ZIP SHA-256 `676152ab0de591d0012b2d7f6a96cbac16dce37b5cca0d894c5b482b12835e1d`.
