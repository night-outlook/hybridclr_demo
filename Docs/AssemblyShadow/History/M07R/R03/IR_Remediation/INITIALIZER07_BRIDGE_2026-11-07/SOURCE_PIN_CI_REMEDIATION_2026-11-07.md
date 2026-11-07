# Primary remediation — stale R03Build source Git blob in mandatory current-native CI

Date: 2026-11-07 UTC. Scope: source-identity compatibility for the existing R03 initializer oneuse-07 preparation only. This document is **not** a runtime validation report or a replacement independent R03 review.

## Observation and raw CI authority

At demo source `b0469e46c4052ea986d4d92ad501ac020c032d5e`, Actions run `42336107614` (`r03-ir-current-native-local-cycle-host.yml`) failed on both Ubuntu 24.04 job `128293291949` and macOS 15 job `128293292129` at the read-only four-repository source admission step, before any native-host component. Both logs identified `CandidateSourceError: Source bytes/Git blob mismatch: hybridclr_demo/Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs`. The separate source-only run `42336107652` failed both OS jobs at two source-authentication cases for the same path. These failures are genuine and are not relabeled.

The two focused mandatory workflows, `r03-ir-initializer-bridge-host.yml` (run `42336107682`) and `r03-ir-initializer-local-contracts.yml` (run `42336107678`), completed successfully on both OS jobs at that **older** demo SHA. Their results are source/host-only and cannot be recycled as completed jobs at any later SHA.

## Root cause and change

The candidate-only `FILES` map in `Tools/AssemblyShadow/R03IR/current_native_source_gate.py` and the corresponding entry in `current_native_candidate.json` retained the historical pre-initializer Editor builder blob `b993703d918090733a659bd7c3ac883cd5d753e1`. However, the actual `R03Build.cs` Git blob is `71c685f419d157bf3774996f28f2d075246cf4e4`, as read independently from the exact feature-branch commit. It retains ordinary `PrebuildCommand.GenerateAll()` and conditionally calls `GenerateInitializerBridgeIfRequested` only for the explicitly configured isolated initializer. It verifies the generated MethodBridge source after the real Player build.

Update only this **current candidate** source pin from `b993703d918090733a659bd7c3ac883cd5d753e1` to `71c685f419d157bf3774996f28f2d075246cf4e4`. Add source tests asserting actual Git blob equality, the opt-in bridge/post-build source checks and a negative old-blob candidate-manifest case. **Do not modify** `Tools/AssemblyShadow/R03/source-pins.json`, the original native/interpreter/package pins, R03Build implementation, the two fixture DLL identities, any historical Local evidence, or the 15-cell initializer runner.

## Follow-up CI failure exposed by the first correction

The first correction committed as `bc3a3fe89b8035bb81cc8c79128115bac1b6363a` passed the current-native-source-only and focused initializer bridge and coordinator workflows on both operating systems. Full current-native-host run `42354711808` got past the original read-only preflight and ran the genuine ten native-host components on both operating systems. Its next `Actual fresh Python CLI startup without PYTHONPATH or Unity` step FAILED on both operating systems because independent `current_native_cli_contracts.py` held the same obsolete `R03Build.cs` git blob `b993703d918090733a659bd7c3ac883cd5d753e1`. Ubuntu raw job `128350141447` explicitly reported `AssertionError: '71c685f419d157bf3774996f28f2d075246cf4e4' != 'b993703d918090733a659bd7c3ac883cd5d753e1'` in `test_12_reviewed_current_source_files_are_pinned`. The macOS job `128350141740` failed the same named step. Do not reclassify these failures; previous current-host success is not an overall run pass.

Second focused Primary correction: align only that CLI contract's candidate `BLOB_PINS` builder entry to `71c685f419d157bf3774996f28f2d075246cf4e4` and assert current/legacy identities plus the actual conditional generator entry. Keep all original source and older historical pins untouched. The required final three-workflow two-OS CI gate remains unchanged.

## Verification and operational gate

Primary source sanity requires the pinned actual `R03Build.cs` Git blob to equal `71c685f419d157bf3774996f28f2d075246cf4e4`, the candidate JSON and source-gate FILES map to agree, and the unchanged twenty source contract tests to include positive current and negative stale Git-blob checks.

Before **one** Local `R03IR-Initializer-20261107-oneuse-07` attempt, verify on the **same final pushed demo SHA** successful, completed macOS 15 **and** Ubuntu 24.04 jobs for all three named mandatory workflows:
1. `r03-ir-initializer-bridge-host.yml`
2. `r03-ir-initializer-local-contracts.yml`
3. `r03-ir-current-native-local-cycle-host.yml`

Also check the source-only current-native workflow if run; any new failure must remain an explicit blocker or be remediated by Primary before handoff. Do not equate a workflow's overall success with a missing, skipped, cancelled or failed required OS job.

The Local batch is still conditioned on fresh macOS original-S/source/SDK/custody and two independent same-volume available-space readings at least 25 GiB, clean four-repository exact remote HEADs and unused output roots. All 15 original oneuse-07 cells (ten genuine native-host components, original-S archived audits, fixture preparation, one real IL2CPP build, two distinct real Players, independent evidence seals and postflight) remain fixed; this source-pin change neither adds an unauthorized Player run nor relaxes any guard.

**Acceptance:** `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; `runtimeAcceptance=false`; `qualificationApproved=false`; `fullLegacyRegressionAcceptance=false`. The prior independent High findings and 17 retired runtime roots/40 duplicate paths remain respectively open and Unavailable. Preserve all historical outcomes.
