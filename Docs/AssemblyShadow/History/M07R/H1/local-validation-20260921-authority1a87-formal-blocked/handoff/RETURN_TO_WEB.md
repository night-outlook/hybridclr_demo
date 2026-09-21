# Local Validation → Primary Implementation

## Current blocker: retained candidate graph cannot pass current-anchor strict sealing

Fresh Local Validation at checkout `3fd718784ed582100bb47a0b28b2204343af9cb8`, source anchor `1a87a393e7a0ee312f39647532d80bfc603c7b23`, completed V00 authority and independently confirmed the expected five-path functional delta. The prior V04 checkpoint and all live Player artifacts authenticate successfully.

The one-time strict pilot seal failed after 390.81 seconds with:

`R00 baseline: source pins differ from baseline provenance`

No seal receipt, formal output root, Player launch, or residual owned process exists.

### Root cause

The retained profile-2 baseline, Native ON/OFF snapshots, Editor replay, and pilot launches bind the complete source-pin DTO whose demo revision is `69130bbb3a6df516916dddb5ad263799a7c6e5e3`. The current authoritative source pin is `1a87a393e7a0ee312f39647532d80bfc603c7b23`.

`Tools/AssemblyShadow/r00_player_inputs.py` intentionally calls `require_current_pairing` for the baseline, both Player snapshots, and replay. This verifies complete DTO equality, including the demo revision. The submitted seal implementation still calls the same strict `r00_results.verify_suite` path and contains no authenticated bridge from the old graph pin to the audited metadata-only successor. Therefore the real seal fails even though the executable/tool delta is within the declared reuse scope.

This is an admission-contract mismatch, not a Player measurement failure and not an operational timeout.

### Required correction

Primary must choose and implement one honest path:

1. add a fail-closed, explicitly authenticated graph-reuse bridge that proves the full `69130bbb...` → `1a87a393...` delta is limited to the reviewed formal-admission tooling/tests/CI and binds that proof into the seal; or
2. require fresh profile-2 controlled graph/map/preregistration/pilots at `1a87a393...`, then seal those current-pairing pilots.

Do not weaken `r00_player_inputs.require_current_pairing`, rewrite retained receipts, move protected pins, treat the scope audit alone as a strict R00 pass, or auto-reseal after mismatch.

Add a regression using a real old-graph/new-metadata-anchor fixture so Primary proves the intended reuse behavior at the same boundary that failed locally. The existing synthetic cache regression passed 10/10 but did not cover this source-pin transition.

## Independent closure completed

- V00 candidate/reproduction/protected authority passed.
- Candidate and protected installed runtimes passed; candidate receipt was refreshed through the sanctioned Unity method.
- Bounded Primary passed 336/336.
- Direct handoff/R01/lazy and PowerShell recovery suites passed.
- Complete Python inventory has 993 passed and 28 explicit environment skips, with no failures/errors after exact historical prerequisite recovery.
- Broad Unity EditMode passed 1,076/1,076 after exact M05 baseline recovery.

Evidence is retained at `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority1a87-formal-blocked/`.

Formal pairs and final analysis were not started. V05/M08 remain ineligible. H1 remains `InProgress`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. Do not begin R02.
