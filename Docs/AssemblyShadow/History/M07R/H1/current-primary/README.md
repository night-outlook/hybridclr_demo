# R01B H1 — Current Primary Implementation

## Status

Latest Local return:

`f8a2766d4ff8de3c6bb4d0900780ef0eccb48bbf`

Result: **BLOCKED at V00**.

Current reviewed candidate build-input source anchor:

`39c33e259d1ba893e23e3f1aa22529c87524534f`

H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

## V00 blocker

The Local candidate preflight failed with:

`Blocked: Incomplete handoff sections`

The verifier requires the exact committed headings declared by `h1_handoff_preflight.py.REQUIRED_SECTIONS`. The previous handoff had editorially renamed several headings and omitted two exact headings.

Local correctly refused to modify the authoritative Primary handoff.

## Correction

The verifier is unchanged.

`WEB_TO_LOCAL.md` now contains all required exact headings:

- `## Objective`
- `## Source targets`
- `## Implementation`
- `## Local validation`
- `## Failure evidence`
- `## Alternatives`
- `## Risks`
- `## Local correction boundary`
- `## Human review gate`

The semantic content from the prior handoff is preserved under those headings.

## Regression

`Tools/AssemblyShadow/tests/test_h1_handoff_preflight.py` now contains a live-repository regression that calls:

`h1_handoff_preflight.verify(<actual repo root>, 'candidate')`

against the real committed:

- `WEB_TO_LOCAL.md`;
- `source-targets.json`;
- `ProjectSettings/AssemblyShadowSourcePins.json`;
- Git branch/origin/source-anchor relationship.

This supplements the existing disposable synthetic repository tests.

The Primary workflow now:

- triggers when the live handoff, source targets, or source pins change;
- checks out full Git history so the declared build-input anchor can be inspected by `verify_demo`;
- explicitly runs the live handoff preflight regression.

These regression/workflow changes are why source authority advances from `50c79913...` to `39c33e25...`.

## Preserved prior implementation

The R01 failure/publication earliest-admission implementation at `50c79913096961636a776ee8254b6631002cdfe5` is unchanged and inherited by `39c33e25...`.

Its Primary executable evidence remains:

- bounded suite: 311/311;
- early capsule: 7/7;
- early results: 19/19;
- failure pipeline: 16/16;
- workflow `35330989089`;
- artifact `10540898558`;
- artifact ZIP SHA-256 `52861f7bca634fa007e4e5fba7cd3774ab8f9dfbf1b39de0c6ca80fba047d139`.

Real Player acceptance remains Local work.

## Blocked-attempt disposition

The `f8a2766d...` Local attempt is preserved exactly as:

- V00 candidate preflight: `Blocked`;
- reproduction-tooling preflight: `Passed`;
- protected refs: `Passed`;
- V01–V05: `NotRun`;
- M08: historical `FAIL`, not rerun.

Nothing from that attempt may be relabelled as fresh V00 acceptance.

Evidence remains under:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260918-authority50c-v00-blocked/`

## Next cycle

Local must restart from **fresh V00** on the final pushed handoff.

If V00 passes, continue the already documented one-batch validation plan through provenance/builds, controlled/normal M07, startup11, M07 14/14, repaired failure/publication, independent remaining V04 cells, retention, and V05/M08 when eligible.

Do not begin R02.
