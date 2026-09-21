# Local Validation report

## Current run — 2026-09-21 authority `a964f79d`

### Exit

**Local Validation → Primary Implementation: RETURN REQUIRED at fresh formal side-B launch authority**

Fresh V00 authenticated candidate checkout `7ff70be81c7b1a1dd73b3a02b79494acf5035d19` and exact source/tool anchor `a964f79d6ceba866c5956741a4a32e38ff8a6b5f`. Candidate authority returned `SourceTargetVerifiedNotBuildAccepted`; reproduction tooling, the exact protected profile-1 family, and both installed runtimes passed. The candidate installed-runtime receipt was refreshed once through `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability`, then passed strict Shadow-ON verification with complete demo-source authentication.

Both reviewed source audits passed exactly. The non-metadata delta `6dd964c0... → a964f79d...` is the required 9 paths, and `69130bbb... → a964f79d...` is the required 17 paths. No runtime, Unity asset, native, protocol, schedule, measurement, or graph-producer path changed. The retained V04 and Player-artifact manifests, latest blocked checkpoint, live protocol/schedule/map/pilot bindings, all eight selected pilot launch receipts, and 33,792 bound files totaling 1,606,993,133 bytes reauthenticated with zero mismatches.

The new `H1GraphReuseBridge` passed with side-B-only scope and SHA-256 `b6e97f573938757d712c632a765fb58b8cb82ff9e360733158de998f980a25e0`. The repaired retained-ON preflight then passed all three required modes in exact order: ON-NoPatch, ON-P01, ON-P03. Its durations were 586.443, 588.563, and 588.616 seconds, total 1763.650 seconds. This empirically closes the returned nested `R01EarlyStartup` Baseline/Control authority-propagation defect.

The new strict pilot seal also passed. `H1PilotVerificationReceipt` SHA-256 is `5dc313824e9b034475a4d6f105b5d29801ef796f1553881d8b3b3699f9f65935`; status is `PassedStrictReconstructionAndStatGuardSealed`; `deepLaunchVerificationCount=8`; all four selected pilots and the complete five-attempt pilot digest are bound; 33,792 immutable files totaling 1,606,993,133 bytes have stable stat guards. Formal admission reached the first side launch in approximately 14.746 seconds, so the prior repeated deep pre-launch scan did not recur.

Formal pair `R00-OFF-NoPatch-formal-01` attempt 1 then exposed a distinct Primary tool-boundary defect. Protected side A passed. Candidate side B exited before Player launch because `run-r00-players.py` called default `r00_player_inputs.verify_inputs()` and rejected the retained graph with `R00 baseline: source pins differ from baseline provenance`. The batch correctly retained the failed whole pair and stopped. An explicit protocol-required whole-pair attempt 2 used the same bridge, seal, protocol, schedule, map, pair ID, order, and failed cumulative index; side A passed again and side B reproduced the exact error. The two side-B console logs and synthetic failure receipts are byte-identical. No process remained after either attempt.

This is not the repaired nested seal path, bridge corruption, retained artifact drift, timeout, cleanup failure, or a Player measurement failure. `run-h1-paired-performance.py` authenticates the bridge during admission and records it in each attempt, but `build_command()` launches the public current-pairing-only `run-r00-players.py` without a side-scoped authenticated authority. `run-r00-players.py` exposes no retained-authority input and calls default `verify_inputs` before it can launch the candidate Player. The failure therefore occurs at fresh formal side-B input preparation.

Local did not modify source/tool contracts, weaken verification, edit `WEB_TO_LOCAL.md`, move protected pins, rewrite retained evidence, or begin R02.

### Results

| Cell | Result | Evidence / disposition |
| --- | --- | --- |
| V00 candidate authority | `Passed` | Checkout `7ff70be8...`; exact `SourceTargetVerifiedNotBuildAccepted` for `a964f79d...` |
| V00 reproduction/protected refs | `Passed` | Reproduction tooling `ba8fee33...`; protected profile-1 family exact |
| V00 installed runtimes | `PassedAfterCandidateReceiptRefresh` | Candidate receipt `d65b6328...`; protected receipt `54bfe84c...`; both Shadow ON and demo source verified |
| V01 bounded Primary | `Passed` | 353/353 |
| V01 focused graph/retained/paired/formal | `Passed` | 11/11, 2/2, 12/12, 2/2 |
| V01 R01/failure/lazy | `Passed` | Capsule 7/7; launch 20/20; results 20/20; failure 16/16; lazy 10/10 |
| V01 PowerShell recovery | `Passed` | Generated-input labels and mutable-input success/failure restoration passed |
| V01 Python inventory | `CompletedWithExplainedEnvironmentSkips` | 1,038 total; 1,010 passed; 28 explicit environment skips; 0 failures/errors |
| V01 Unity EditMode | `Passed` | Fresh 1,076/1,076, zero skips |
| V01A source audits | `PassedExactSets` | Exact 9-path and 17-path non-metadata sets |
| V02 retained evidence | `Passed` | Checkpoint/Player manifests, controls, pilot history, 8 selected launches, and 1.607 GB bound files authenticate |
| V04.N bridge | `Passed` | New side-B `AuthenticatedToolOnlySuccessor`; SHA `b6e97f57...` |
| V04.N1 retained early preflight | `Passed` | 3/3 required ON modes; total 1763.650 s |
| V04.O strict pilot seal | `Passed` | 8/8 deep sides; stable 33,792-file guards; SHA `5dc31382...` |
| V04.P formal pair 1 attempt 1 | `FailedBeforeCandidatePlayerLaunch` | A passed; B current-pairing verifier rejected retained graph; batch stopped |
| V04.P explicit pair 1 attempt 2 | `FailedReproduced` | A passed; B reproduced byte-identical source-pairing rejection; no residual process |
| V04.P remaining pairs | `Blocked / NotRun` | 0/40 formal pairs accepted; unresolved pair 1 blocks resumption |
| V04.Q final analysis | `NotRun` | Complete formal index absent |
| V05 / independent M08 | `Ineligible / NotRun` | Mandatory formal and analysis evidence absent |

### Root cause and required Primary correction

The bridge-aware admission and strict verification paths are now correct. The missing boundary is fresh formal execution:

1. `run-h1-formal-batch.py` passes the bridge and seal to `run-h1-paired-performance.py`.
2. Formal admission authenticates both and completes quickly.
3. `run-h1-paired-performance.py::build_command()` constructs a command for `run-r00-players.py` using only project/fixture/build/replay/output/mode/timeout arguments.
4. `run-r00-players.py` calls default `r00_player_inputs.verify_inputs()` before creating output or launching the Player.
5. Candidate side B therefore reasserts current source-pin equality against retained graph anchor `69130bbb...` and fails.

Primary must provide a fail-closed fresh-launch path that consumes only the already authenticated, same-bridge, side-B authority. Preserve default/direct `run-r00-players.py` current-pairing behavior, keep protected side A current-only, prevent arbitrary historical pairing at the CLI, and thread the same authority into nested Baseline/Control early preparation for ON modes. Add a real formal driver regression crossing `build_command → run-r00-players → verify_inputs` for retained side B; existing seal and synthetic batch regressions did not exercise this subprocess boundary.

After Primary publishes the correction, Local must restart at fresh V00, re-audit the source delta, create a new bridge and seal, and start a new formal batch. These two failed whole-pair attempts remain historical and must not be deleted or relabelled.

### Retention checkpoint

The authenticated pre-cleanup checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authoritya964-formal-launch-blocked/`. It contains all fresh authority/test/audit receipts, the passing bridge/preflight/seal, the stopped batch, both whole-pair attempts with side logs/receipts, prior authenticated manifests, raw evidence, and a SHA-256 manifest. No cleanup was performed on retained graphs, pilots, bridge, seal, or formal attempts.

H1 remains `InProgress`; the last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.
