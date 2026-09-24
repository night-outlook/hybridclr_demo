# Static Review — H1 Test-Only Historical Reanalysis Successor

## Verdict

**PASS for Primary → Local Validation handoff, with fresh empirical Local validation required.**

Reviewed source anchor:

`d239d9d00784ea2df22133cb8c938ec25035f5a0`

## Finding

Local's one full-discovery failure is a stale synthetic positive fixture, not evidence of a production analyzer defect or Player failure.

The real analyzer contract requires raw top-level:

- `buildGuid`;
- `baselineBuildId`;
- `runtimeAbiHash`.

The fixture had those values only in its nested `playerBuildReceipt`.

Local's in-memory diagnostic added the top-level fields and reached `ComparabilityPassed`.

## Fixture correction review

The committed fixture now mirrors the authenticated producer shape:

- required top-level build identity exists;
- nested receipt path/SHA/build GUID remains bound;
- optional nested baseline/runtime copies remain matching.

The production analyzer was not relaxed.

Missing or incorrect top-level identity still fails closed.

## Bounded-regression review

The bounded Primary runner now explicitly loads only:

`test_h1_paired_performance.H1PairedPerformanceTests.test_analyze_sample_index_complete_positive`

This directly closes the coverage gap that allowed 376/376 while full discovery failed.

Expected bounded count is 377.

## Historical compatibility review

The v1 five-path policy cannot honestly authorize the new test change.

Primary therefore published:

`H1HistoricalPerformanceReanalysis-v2`

with an exact **seven-path** source-27df → current delta.

The two additions are test/regression-only:

1. `Tools/AssemblyShadow/h1_bee_primary_tests.py`
2. `Tools/AssemblyShadow/tests/test_h1_paired_performance.py`

The other five paths are the already-reviewed v1 analysis paths.

No execution runner, R00 verifier, measurement source, protocol, schedule, graph producer, Player/native/runtime source, or execution-authority source is added.

## Retained-graph policy review

The current retained-graph source transition is versioned to:

`H1V04RetainedGraphToolOnlySuccessor-v2`

It contains exactly **25 non-metadata paths**: the prior reviewed 24 plus the paired-performance test fixture.

Changing the existing runner `h1_bee_primary_tests.py` does not add a new unique retained-graph path because that path was already in the 24-path set.

Historical source-27df bridge/formal authorities continue to bind v1. The historical authenticator explicitly validates their original v1 policy IDs and hashes.

## Source-anchor review

The implementation/source anchor is:

`d239d9d00784ea2df22133cb8c938ec25035f5a0`

A direct source-27df comparison at that anchor contains exactly the seven reviewed non-metadata paths.

All later commits in this Primary cycle are metadata/handoff only.

No `.agents/` or `.codex/` metadata exemption was introduced.

## Historical evidence integrity

Primary did not modify:

- source-27df raw results;
- historical build receipts;
- graph bridge;
- guard-v2 seal;
- formal authorities;
- formal batch;
- sample indexes;
- protocol/schedule/map;
- Player artifacts.

The fixed four historical SHA-256 identities remain unchanged.

## Validation boundary

No fresh GitHub Actions run was visible for the new source anchor.

Therefore this review does **not** claim:

- bounded 377/377;
- full Python PASS;
- live historical compatibility PASS;
- historical analysis PASS;
- V05 PASS;
- independent M08 PASS;
- Human Review Gate readiness.

Local must provide those empirical results in order.

## Stop condition

If source authority, bounded/full Python validation, exact source audits, historical compatibility, or strict analysis fails, return to Primary.

Do not rerun Players merely to work around analysis/test defects.

H1 remains `InProgress`. Do not begin R02.
