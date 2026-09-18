# Static Review — H1 Committed Handoff Section Contract Repair

## Verdict

**PASS for Primary → fresh Local V00 handoff.**

This review does not establish V00 Local PASS, Unity/Player/runtime/performance acceptance, M08 PASS, or Human Review Gate readiness.

## Returned finding

Local at `f8a2766d4ff8de3c6bb4d0900780ef0eccb48bbf` found that the authoritative handoff did not satisfy its own verifier contract.

The verifier requires exact substrings:

- `## Objective`
- `## Source targets`
- `## Implementation`
- `## Local validation`
- `## Failure evidence`
- `## Alternatives`
- `## Risks`
- `## Local correction boundary`
- `## Human review gate`

The prior handoff used editorial variants such as `## Primary implementation` and `## Human Review Gate`, and lacked exact `Risks` and `Local correction boundary` sections.

## Repair invariant

`h1_handoff_preflight.py` was not changed.

No verifier relaxation, case-folding, heading alias, metadata-only expansion, source-path exception, or source-authority bypass was introduced.

The repair changes the document to match the verifier, not the verifier to match the document.

## Live regression

The previous unit suite only proved a synthetic handoff built from `REQUIRED_SECTIONS`.

The new regression resolves the actual repository root from the committed test file and runs:

`h1_handoff_preflight.verify(root, 'candidate')`

This requires, in one test:

- actual committed WEB_TO_LOCAL bytes equal HEAD;
- actual committed source-target bytes equal HEAD;
- all required headings are present;
- actual branch/origin are correct;
- actual source target and source pin agree;
- runtime pins agree;
- `verify_demo` confirms every non-metadata build input matches the declared source anchor.

The CI workflow uses `fetch-depth: 0` because `verify_demo` must resolve the source-anchor commit beneath metadata-only successors.

## CI trigger coverage

The Primary workflow now runs when any of these authorities change:

- `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`;
- `Docs/AssemblyShadow/Handoff/source-targets.json`;
- `ProjectSettings/AssemblyShadowSourcePins.json`;
- the existing source/test/workflow paths.

This closes the specific gap that allowed a committed handoff edit to bypass the synthetic-only regression.

## Source authority

The live regression test and workflow trigger are build-input changes, so the candidate source anchor advances to:

`af56b841e9ae80be0b1748e546338f9b68da2717`

The underlying failure/publication runtime implementation from `50c79913...` is unchanged.

The reproduction-tool candidate source anchor advances consistently; its declared tool blobs remain unchanged.

## Blocked-attempt preservation

The Local attempt at `f8a2766d...` remains Blocked at V00. V01–V05 were NotRun. M08 was not rerun.

No evidence state was upgraded by this repair.

## Final committed-live-handoff CI

The exact live handoff version at commit `4338cc989bd01918e012e43b8ecbae983e4862c8` passed GitHub Actions workflow `35333505896`.

Results:

- bounded Primary suite: **312/312 Passed**;
- committed live handoff preflight suite: **11/11 Passed**;
- R01 early-capsule suite: **7/7 Passed**;
- R01 early-results suite: **19/19 Passed**;
- R01 failure-pipeline suite: **16/16 Passed**.

CI artifact:

- ID: `10542063317`
- ZIP SHA-256: `63027964602b3e44f34aed7eb77b1ce228b781c2dcf08ed21eaa743e5bd8928b`

The 11-test handoff suite includes the regression that executes `h1_handoff_preflight.verify()` against the actual committed checkout. The exact `WEB_TO_LOCAL.md`, `source-targets.json`, and source-pin relationship therefore passed the same source preflight used by Local.

## Gate

H1 remains `InProgress`; historical M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

Do not begin R02.
