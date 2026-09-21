# Static Review — Authenticated Retained-Graph Reuse Bridge

## Verdict

**PASS for Primary → Local Validation handoff**, subject to real bridge creation, strict pilot sealing, formal Player sampling, and final analysis.

Reviewed build-input/tool source anchor: `48b44fff297d229cef5d9f8642900e974a201040`.

## Returned finding

The retained candidate graph is internally authentic but records demo source revision `69130bbb...`. Current project authority had advanced. The strict R00 gate therefore rejected the baseline/source provenance before pilot sealing.

Local explicitly prohibited weakening `require_current_pairing`, rewriting receipts, moving pins, or relying on a scope audit alone. The Primary repair follows that boundary.

## Review of the bridge

The implementation separates three authorities:

1. **current project authority** — unchanged global source/runtime verifier;
2. **retained graph authority** — exact historical complete source-pin DTO, reconstructed only with demo revision `69130bbb...` and otherwise identical current platform/runtime pins;
3. **reuse proof** — exact Git/tree/verifier/build-map evidence proving the graph→current transition is limited to the reviewed admission-tooling scope.

The bridge must satisfy all three before it emits `H1AuthenticatedGraphReuseAuthority`.

The exact non-metadata path allowlist is closed and includes only CI and `Tools/AssemblyShadow` Python/tool documentation. It contains no Unity C#/asmdef, Assets/Packages payload, native runtime, measurement source, protocol/schedule JSON, build-map producer, or Player runner.

## Strict verifier preservation

`r00_player_inputs.require_current_pairing` is unchanged and contains no reuse/override branch.

`verify_inputs` remains the default current-pairing path.

`verify_inputs_with_reuse` is a separate function requiring an authenticated authority bound to the candidate project/current pins/bridge receipt. `r00_results.verify_suite` takes no historical pairing unless its caller explicitly supplies that authority.

Only the sealer and final analyzer obtain that authority from bridge verification. This prevents a normal R00 CLI caller from declaring an arbitrary historical pin.

## Seal/formal/analyzer chain

- full bridge authentication occurs before the eight deep pilot-side seal verifications;
- only retained candidate side B receives the old pairing during deep verification;
- bridge hash is part of the seal;
- formal cached admission revalidates the bridge compactly and requires every formal attempt to retain the same bridge/seal bindings;
- final analyzer full-verifies the bridge again and performs the original strict per-launch evidence reconstruction;
- bridge/cache do not change pair ordering, whole-pair retry, measurement timing, statistics, or final evidence semantics.

## Regression review

Primary tests cover the real old-source/current-successor Git boundary rather than only synthetic data, plus negative runtime-pin/revision cases, current-only default R00 behavior, side-B-only authority injection, seal binding, formal bridge-switch rejection, and final-analysis bridge binding.

Primary CI at the authority successor passed 346/346 bounded tests and all existing H1 contract suites.

## Residual empirical requirements

- sanctioned current installed-runtime receipt refresh if required by the new source pin;
- independent Local source/allowlist audit;
- creation of a real `H1GraphReuseBridge` over the retained build map;
- successful real strict pilot seal (8 side graphs);
- all 40 formal pairs and any retained whole-pair retries;
- final bridge-aware strict analysis;
- authenticated checkpoint and V05;
- genuinely independent M08 review.

H1 remains `InProgress`. Do not begin R02.
