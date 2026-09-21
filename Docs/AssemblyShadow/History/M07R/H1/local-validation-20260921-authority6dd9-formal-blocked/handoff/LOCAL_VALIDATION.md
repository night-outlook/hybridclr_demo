# Local Validation report

## Current run — 2026-09-21 authority `6dd964c0`

### Exit

**Local Validation → Primary Implementation: RETURN REQUIRED at bridge-bound strict pilot sealing**

Fresh V00 authenticated candidate checkout `1c6cdda260e2bf91e07e672aa261dcc38b3a5aa8` and exact source/tool anchor `6dd964c045034240ea53dd15ba7c0b33e9f2ad17`. Candidate authority returned `SourceTargetVerifiedNotBuildAccepted`; reproduction tooling, the exact protected profile-1 family, and both installed runtimes passed. The candidate installed-runtime receipt was refreshed once through `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability`, then passed strict Shadow-ON verification with complete demo-source authentication.

The exact non-metadata delta from both `1a87a393...` and retained graph anchor `69130bbb...` to `6dd964c0...` is the reviewed 14-path set. The retained V04 checkpoint and Player-artifact manifests, the prior blocked checkpoint, live protocol/schedule/map/pilot bindings, all eight selected launch receipts, and 33,784 unique bound files totaling 1,521,688,590 bytes reauthenticated.

The real `H1GraphReuseBridge` passed with side-B-only scope and SHA-256 `088a338632a9d2a9970c0bc61aaa9b218b4ca93e080a1734539b68317fa1a89e`. It binds the exact `69130bbb... → 6dd964c0...` transition, all 14 paths, both source-pin DTO identities, the frozen map, current verifier hashes, and the refreshed candidate installed-runtime receipt.

The one-time strict seal nevertheless failed after approximately 1104.2 seconds with `R00 baseline: source pins differ from baseline provenance`; no `H1PilotVerificationReceipt`, formal output root, or formal Player launch was produced. A focused read-only reproduction proved that bridge-aware outer R00 input verification succeeds. The nested early-startup capsule reconstruction then calls `r01_early_results._prepare()`, which calls default `r00_player_inputs.verify_inputs()` without the authenticated reuse authority and reproduces the same failure. The bridge is valid, but its authority is not propagated through the nested early-capsule reconstruction used by `r00_results.verify_suite`.

This is a Primary-side fail-closed authority-propagation defect, not a retained artifact mismatch, bridge corruption, or measurement failure. Local did not weaken verification, modify source/tool contracts, edit `WEB_TO_LOCAL.md`, rewrite retained receipts, move protected pins, or start R02.

### Results

| Cell | Result | Evidence / disposition |
| --- | --- | --- |
| V00 candidate authority | `Passed` | Checkout `1c6cdda...`; exact `SourceTargetVerifiedNotBuildAccepted` for `6dd964c0...` |
| V00 reproduction/protected refs | `Passed` | Reproduction tooling `ba8fee33...`; protected profile-1 demo/runtime family exact |
| V00 installed runtimes | `PassedAfterCandidateReceiptRefresh` | Candidate receipt `df751fe2...`; protected receipt `54bfe84c...`; both Shadow ON and demo source verified |
| V01 bounded Primary | `Passed` | 348/348 |
| V01 direct graph/paired/formal tests | `PassedWithPreservedInvocationFailure` | Graph 8/8; paired 12/12; formal 2/2 after supplying repository `PYTHONPATH`; initial literal formal-file invocation failed before tests and is retained |
| V01 direct R01/lazy | `Passed` | Capsule 7/7; early launch 20/20; early results 20/20; failure pipeline 16/16; lazy 10/10 |
| V01 PowerShell recovery | `Passed` | All four generated-input labels and exact success/failure restoration passed |
| V01 Python inventory | `CompletedWithExplainedEnvironmentSkips` | 1,033 total; 1,005 passed; 28 skipped; 0 failures/errors |
| V01 Unity EditMode | `Passed` | Fresh 1,076/1,076, zero skips |
| V01A source audits | `PassedExact14Paths` | Both `1a87... → 6dd9...` and `6913... → 6dd9...`; no subset/superset |
| V02 retained evidence | `Passed` | Both checkpoint manifests, Player artifacts, live controls, eight selected launches, and 1.52 GB bound files authenticate |
| V04.N graph-reuse bridge | `Passed` | `AuthenticatedToolOnlySuccessor`, side B, exact bridge/map/pins/verifier/install bindings |
| V04.O strict pilot seal | `FailedBeforeReceipt` | ~1104.2 s; nested early reconstruction lost bridge authority; exact source-pairing error recurred |
| V04.P formal pairs | `NotRun` | Seal prerequisite absent; 0/40 formal pairs started |
| V04.Q final analysis | `NotRun` | No formal index exists |
| V05 / independent M08 | `Ineligible / NotRun` | Seal, 40 formal pairs, and analysis are absent |

### Root cause and required Primary correction

`r00_results.verify_suite(..., pairing_authority=...)` correctly routes its outer graph validation through `verify_inputs_with_reuse`. For strict modern launches using `R01EarlyStartup`, it separately reconstructs early capsules by calling `r01_early_results._prepare(...)`. That function unconditionally calls default `verify_inputs`, which reasserts current source-pin DTO equality and rejects the retained candidate graph before capsule reconstruction.

Primary should propagate the already authenticated, side-scoped reuse authority through this nested reconstruction without changing default R00 pairing, without allowing authority on protected side A, and without weakening any source-pin comparison. Add a real retained-graph regression that exercises an ON pilot mode with early capsule reconstruction, not only the outer input gate. Local must then restart at fresh V00 and create a new bridge and seal; the failed seal attempt must remain historical.

### Retention checkpoint

The authenticated pre-cleanup checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6dd9-formal-blocked/`. It contains fresh V00/V01 receipts and inventories, the exact source/reuse audit, retained-evidence audit, the valid graph bridge, the failed seal receipt and focused root-cause diagnostic, a raw-evidence archive, prior checkpoint manifests, and a SHA-256 manifest. No cleanup was performed on the retained graphs, pilots, bridge, or this batch.

H1 remains `InProgress`; the last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.
