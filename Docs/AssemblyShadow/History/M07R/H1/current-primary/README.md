# R01B H1 — Current Primary Implementation

## Status

Local Validation returned at:

`476925a44613f09774de78f93c017e1a078838b0`

Current reviewed candidate build-input source anchor:

`8b1298d6a5979928bdfa30446e2d674d63999b76`

The source authority was advanced from `68df00fe31a199491b313cc17f25575663b7452b` after Local independently validated the MethodPtr and deterministic dense-v2 changes. The global `shadow_tools.verify_demo()` contract, metadata-only classification, M07 three-path workflow authority, and protected reproduction/runtime/performance pins were not weakened.

## Closed focused findings

Local Validation established:

- focused M05 Python inventory: 113 passed, one explicit environment-path skip;
- retained real Unity 2022.3.62f2 Bootstrap: `#-`, 469 TypeDef, 1,675 MethodPtr and 1,675 MethodDef rows;
- all MethodPtr rows form a complete one-to-one permutation and the five raw method witnesses resolve correctly;
- deterministic dense-v2 generation produces two byte-reproducible exact 1 MiB fixtures;
- native parser: full corpus 8,192, dense 2/2, bounded reader 13/13, sanitizer clean, provenance stable.

Historical dense-v1 bytes remain `UnavailableDoNotRelabel`. Focused success does not establish V04/V05, M08, H1 approval, or permission to start R02.

Evidence remains under:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260917-methodptr-dense/`

## Source authority advance

`ProjectSettings/AssemblyShadowSourcePins.json` and `Docs/AssemblyShadow/Handoff/source-targets.json` now bind candidate demo source to `8b1298d...`.

All commits after that anchor through the authority update are metadata-only under the existing verifier: live handoff/source-target files, ProjectSettings source pins, plan/status files, and preserved evidence under `Docs/AssemblyShadow/`.

The reproduction-tool source anchor was also advanced to `8b1298d...`. Every declared reproduction-tool blob remains byte-identical at that anchor, and the two authenticated deletion paths remain absent.

No source-verifier exception was added.

## Remaining blocker

The prior successful M07 fixture/build/replay receipts were removed during workspace consolidation. They must not be reconstructed from summaries.

The next Local cycle must regenerate a fresh provenance-bound normal M07 chain under source anchor `8b1298d...`, then immediately continue capsule/startup11 and the blocked V04 downstream chain while those exact inputs still exist.

Before any cleanup or handback, retain one complete evidence set containing at minimum:

- normal `m07-build-workflow.json`;
- `m07-fixtures.json`;
- Native-ON and Native-OFF `m07-player-build.json` receipts;
- `m07-editor-replay.json`;
- rejected/failure-fixture and negative-input receipts referenced by the fixture manifest;
- generated control capsules and `capsules.json`;
- startup11 launch receipt, results, console logs and Unity logs;
- exact hashes/paths for all referenced Player/resource/fixture inputs;
- post-run source-authority/preflight result.

The Local checkpoint archive must be created before deleting or consolidating `_temp`, `Builds`, or launch-output directories.

## Gate

H1 remains `InProgress`. Last independent whole-chain M08 remains `FAIL`. `humanGatePassed=false`; `mayEnterR02=false`.

Do not begin R02.
