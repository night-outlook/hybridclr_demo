# R01B H1 — Current Primary Implementation

## Status

Latest Local return: `9045d54e3a1c365ac8c15a3cb5ca791ad13d7501`.

Candidate build-input/tool source anchor: `6dd964c045034240ea53dd15ba7c0b33e9f2ad17`.

H1 remains `InProgress`; `humanGatePassed=false`; `mayEnterR02=false`.

## Local result received

The previous Primary pilot-cache optimization itself remained structurally valid, but its first real strict seal exposed a source-pairing contract gap: the retained candidate graph was built at demo revision `69130bbb...` while current authority had advanced to `1a87a393...`.

The unchanged R00 verifier correctly rejected the retained graph before the cache could be sealed. No formal Player launched. This is neither a performance failure nor a timeout.

The same Local batch also completed the broad prerequisite closure: Python has no failures/errors (28 explicit external-environment skips), and Unity EditMode passed 1076/1076.

## Primary design: authenticated graph-reuse bridge

Primary selected the explicit bridge path rather than rebuilding the already-authenticated controlled graph/map/preregistration/pilots.

The bridge is not a relaxation of normal source pairing. It is a new evidence object with a closed policy:

1. the only reusable candidate graph revision is `69130bbb3a6df516916dddb5ad263799a7c6e5e3`;
2. current source/runtime authority must pass the unchanged global verifier;
3. Unity/target/architecture and all three runtime repository pins must equal the retained graph pairing;
4. the old revision must be a Git ancestor of current authority;
5. after the existing metadata-only exclusions, the old→current tree delta must equal the exact reviewed 12-path CI/AssemblyShadow-tooling allowlist;
6. the bridge binds every changed Git blob, current source-pin bytes, frozen build map, verifier code, and installed-runtime verification.

`r00_player_inputs.require_current_pairing` remains byte-for-byte logically unchanged. A separate `verify_inputs_with_reuse` entry accepts only an `H1AuthenticatedGraphReuseAuthority`; default `verify_inputs` still uses the live project pins.

## Seal / formal / final-analysis integration

- `create-h1-graph-reuse-bridge.py` creates and self-verifies the bridge.
- `seal-h1-pilot-verification.py --graph-reuse-bridge ...` performs full bridge authentication before the expensive eight-side pilot reconstruction.
- During sealing, only candidate side B receives the retained graph pairing authority; protected side A remains strict-current.
- `H1PilotVerificationReceipt` binds the bridge.
- Every formal attempt binds the same bridge and same pilot seal; a cumulative chain cannot switch either.
- Formal cached admission performs compact bridge revalidation plus the existing sealed identity checks; it still performs zero repeated deep pilot rescans.
- `analyze-h1-paired-performance.py` now requires the same bridge and pilot seal, fully reauthenticates the bridge, and then performs the original strict evidence analysis with historical pairing authority only on candidate side B.

For a genuinely fresh current-pairing graph, the bridge remains optional and the original strict path remains valid.

## Primary regression coverage

The bounded suite now includes real-transition and wiring coverage:

- real Git transition from retained `69130bbb...` to current source must equal the exact allowlist;
- runtime pin changes or a different retained graph revision are rejected;
- default R00 pairing remains current-only;
- an untrusted reuse object cannot enter the retained path;
- bridge authority is injected only into candidate side B;
- the bridge is cryptographically bound into the pilot seal;
- formal admission rejects bridge replacement;
- the final analyzer requires the same seal/bridge and fully verifies the bridge;
- existing cache regression still proves 8 deep seal verifications and 40 cached formal admissions with 0 deep rescans.

## Source scope

The full retained-graph non-metadata delta `69130bbb... → current` is exactly the 14 paths encoded in `source-targets.json` and `h1_graph_reuse.py`. No Assets/Packages/runtime/native/measurement source/protocol/schedule/build-map producer changed.

## Formal batch orchestration

Primary additionally supplies `Tools/AssemblyShadow/run-h1-formal-batch.py`. It sequentially chains all unattempted formal pairs with the same bridge+seal, never auto-retries, stops on the first failed whole pair, and resumes only after an explicit protocol-valid same-pair retry.

## Next Local cycle

Authenticate current authority and retained evidence, create the bridge, seal once, then run all forty formal pairs and final analysis in one batch if each gate passes. Preserve every failed/retry attempt and bind all outputs into a new checkpoint.

Do not begin R02.
