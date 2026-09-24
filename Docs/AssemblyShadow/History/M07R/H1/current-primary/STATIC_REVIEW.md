# Static Review — Split-Checkout Historical Reanalysis Repair

## Verdict

**PASS for Primary → Local Validation handoff. Fresh Local empirical validation remains mandatory.**

Reviewed source anchor:

`d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece`

## Returned defect

The v2 compatibility tool conflated:

- immutable historical evidence root; and
- current analysis-source authority.

The historical bridge's `projectRoot` points to the owner checkout that owns the original absolute evidence paths. Its present-day source pin is not authoritative for the separate current validation checkout.

This caused V04.AF to compare source-27df against 7aa rather than d239.

## Authority separation review

The repair introduces a required `--analysis-project`.

The current analysis checkout is fail-closed authenticated as:

- a canonical Git root;
- committed source-pin bytes;
- canonical repository URL/localPath;
- complete non-metadata source tree matching the pinned revision;
- reanalysis tool bytes matching the running tool.

The historical bridge project remains required to match the immutable bridge's absolute project root and historical path/hash bindings.

No current-source inference is taken from that historical root.

## Historical bridge review

`verify_historical_bridge` now receives the already-authenticated analysis pin DTO explicitly.

It still reconstructs and checks:

- retained graph source revision;
- source-27df historical pin DTO;
- original v1 graph transition;
- historical verifier tool hashes from Git;
- retained pilot runner identity;
- immutable installed-runtime verification summary.

It compares only platform/runtime repository pins between current analysis and historical source. The demo revision is intentionally different under the analysis/test-only successor.

## Strict-analysis review

A preflight-only fix would have left a downstream dependency: normal retained R00 verification reads the candidate project's present-day source pins and runs the generic source verifier.

That is invalid for immutable historical evidence whose owner checkout can advance independently.

The repair therefore adds `_verify_historical_r00_inputs` inside the historical reanalysis module. It mirrors the evidence-semantic portion of the existing R00 input gate:

- baseline source pin equality;
- fixture resources;
- NativeOn/NativeOff player receipt verification;
- snapshot source pin equality;
- distinct ON/OFF identities;
- managed input equality;
- manifest ON receipt path/hash;
- replay validation and source pins.

It deliberately does not treat the historical checkout's present-day source file as current authority.

During candidate-side strict verification only, the reanalysis callback temporarily substitutes this historical input verifier for:

- `r00_results.verify_inputs_with_reuse`;
- `r00_results.early.verify_inputs_with_reuse`.

Both are restored in `finally`.

No shared execution/runtime verifier source is modified.

Protected side A follows its normal preserved verification path.

## Policy-scope review

The new repair does not widen v2 source scope.

Source-27df → current anchor remains exactly seven non-metadata paths.

d239 → current anchor is exactly three already-allowed paths.

The retained-graph 25-path policy is unchanged.

No changes occurred in:

- `r00_player_inputs.py`;
- `r00_results.py`;
- `r01_early_results.py`;
- Player runners;
- measurement code;
- protocol/schedule;
- build-map/graph producer;
- native/runtime source.

## Regression review

New tests cover:

1. a real Git split-checkout case using the stale evidence-checkout commit from the Local diagnosis;
2. a committed wrong-current-pin negative;
3. changed historical bridge build-map binding rejection;
4. direct `authenticate_compatibility` routing between analysis and historical roots;
5. strict historical input override installation/restoration.

These tests remain within `test_h1_graph_reuse`, already part of the bounded Primary suite.

Expected bounded count rises from 377 to 381.

## Residual empirical requirements

This Primary environment has no fresh workflow run for the new source anchor.

Local must verify:

- 381/381 bounded;
- full Python zero failures/errors;
- exact seven/25-path policies;
- complete historical live evidence;
- real split-checkout V04.AF;
- strict V04.AG;
- analysis-only checkpoint;
- V05;
- genuinely independent M08.

No Player rerun is required if those checks pass.

## Gate

H1 remains `InProgress`.

Historical M08 remains `FAIL`.

Do not begin R02.
