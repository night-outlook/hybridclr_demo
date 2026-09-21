# Local Validation report

## Current run — 2026-09-21 authority `1a87a393`

### Exit

**Local Validation → Primary Implementation: RETURN REQUIRED at strict pilot sealing**

Fresh V00 authenticated candidate checkout `3fd718784ed582100bb47a0b28b2204343af9cb8` and exact source anchor `1a87a393e7a0ee312f39647532d80bfc603c7b23`. Candidate authority returned `SourceTargetVerifiedNotBuildAccepted`; reproduction tooling, the exact protected profile-1 family, and both installed runtimes passed. The candidate installed-runtime receipt was refreshed once through `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability` after the source-pin advance, then verified with Shadow ON.

The declared executable/tool delta from `69130bbb3a6df516916dddb5ad263799a7c6e5e3` to `1a87a393...` is exactly the five expected CI/seal/driver/test paths. The prior checkpoint manifest and its live Player-artifact manifest both pass, and the live protocol, schedule, build map, and final pilot index byte-match their retained checkpoint copies.

The one-time real seal did not pass. After 390.81 seconds it failed closed with `R00 baseline: source pins differ from baseline provenance`; no `H1PilotVerificationReceipt`, formal output root, or Player launch was produced. The retained profile-2 graph binds demo revision `69130bbb...`, while the authoritative live `AssemblyShadowSourcePins.json` binds `1a87a393...`. `r00_player_inputs.require_current_pairing` requires those complete DTOs to match for the baseline, Native ON/OFF snapshots, and replay. The submitted cache implementation contains no authenticated metadata-only compatibility bridge, so the retained candidate graph cannot be strictly reconstructed under the current anchor.

Formal sampling and final analysis are therefore `NotRun`, not Failed and not Passed. V05 and independent M08 are ineligible.

### Results

| Cell | Result | Evidence / disposition |
| --- | --- | --- |
| V00 candidate authority | `Passed` | Checkout `3fd718...`; exact `SourceTargetVerifiedNotBuildAccepted` for `1a87a393...` |
| V00 reproduction/protected refs | `Passed` | Reproduction tooling `ba8fee33...`; protected profile-1 demo/runtime family exact |
| V00 installed runtimes | `PassedAfterCandidateReceiptRefresh` | Candidate receipt `3e3e16a8...`; protected receipt `54bfe84c...`; both Shadow ON with demo source verified |
| V01 bounded Primary | `Passed` | 336/336 |
| V01 paired-driver regression | `Passed` | 10/10; simulated strict seal uses 8 deep verifications, 40 formal admissions use 0 deep rescans, mutation and seal-switch classes reject |
| V01 direct handoff/R01/lazy | `Passed` | Handoff 11/11; capsule 7/7; early launch 20/20; early results 20/20; failure pipeline 16/16; lazy 10/10 |
| V01 PowerShell recovery | `Passed` | All four labels accepted; unknown label rejected; success/failure exact two-input restoration passed |
| V01A functional source audit | `PassedExpectedScope` | Exactly the five declared functional paths; no unexpected non-document delta |
| V02 retained checkpoint manifest | `Passed` | All 30 checkpoint entries verified |
| V02 live Player artifacts | `Passed` | All live graph/Player paths in `PLAYER_ARTIFACTS.sha256` verified |
| V04.J one-time strict pilot seal | `FailedBeforeReceipt` | 390.81 s; `R00 baseline: source pins differ from baseline provenance`; no receipt created |
| V04.K formal pairs | `NotRun` | Seal prerequisite absent; 0/40 formal pairs started |
| V04.L final analysis | `NotRun` | No formal index exists |
| V04.M complete Python inventory | `CompletedWithExplainedEnvironmentSkips` | After exact prerequisite recovery: 1,021 total, 993 passed, 28 skipped, 0 failed/errors |
| V04.M broad Unity EditMode | `PassedAfterExactPrerequisiteRecovery` | 1,076/1,076, 0 skipped |
| V05 / independent M08 | `Ineligible / NotRun` | Strict seal, 40 formal pairs, and final analysis are absent |

### Source/reuse boundary

The five functional paths are:

- `.github/workflows/h1-bee-primary.yml`;
- `Tools/AssemblyShadow/h1_bee_primary_tests.py`;
- `Tools/AssemblyShadow/run-h1-paired-performance.py`;
- `Tools/AssemblyShadow/seal-h1-pilot-verification.py`;
- `Tools/AssemblyShadow/tests/test_h1_paired_driver.py`.

No Player/runtime/Bootstrap C#, native runtime, Unity package, IL2CPP, R00 runner/results/input verifier, protocol, bound schedule, build-map freezer, preregistration binder, timing/statistics logic, or final analyzer changed.

The prior checkpoint manifest SHA-256 is `76b4af548142220411ce18c191d6326e1293256efb9bd59a06b22b19d7ad6bf8`; the live Player-artifact manifest SHA-256 is `2f4af85f10dab5a9790a81bf072dece34198c418aaccd2b17eb158b314ac12f5`. Protocol/schedule/map/pilot-index hashes remain `2c12ce68...`, `429b99a6...`, `169351cc...`, and `8f856abb...`. The complete retained pilot-attempt digest is `32e62a12...`, including the failed timeout and successful whole-pair retry.

Source-scope equality is necessary but not sufficient for strict graph reuse. The retained current-candidate baseline, Native ON/OFF snapshots, and replay all carry demo revision `69130bbb...`. The current source pin carries `1a87a393...`. The unmodified strict R00 verifier rejects this mismatch before the new seal can be emitted. Local did not weaken the verifier, rewrite graph receipts, move the source pin, or auto-reseal.

### Fresh inventory closure

The first Python inventory retained 987 passed, 28 skipped, 1 failed, and 5 errors because exact historical M01/M02 trees were absent. The exact immutable trees were recovered without overwrite from the prior H1 worktree; their embedded proofs were then reauthenticated by the tests. The final Python run has no failure or error. Its 28 skips are explicit: 27 require the separately supplied H1R coordination corpus, and one requires explicit real M05 compiler/configuration paths.

The first broad Unity run retained 1,071 passed and 5 failed, all due to the absent accepted `M05-Baseline-v6` linked input. After exact non-overwriting recovery of that immutable baseline, a fresh full rerun passed 1,076/1,076 with zero skips. Candidate installed-runtime verification passed again afterward, and the tracked worktree was clean before this report update.

### Preserved attempts

The batch retains the incorrect reproduction-preflight checkout attempt, two incorrect installed-runtime CLI argument-order attempts, the direct R01 import-path invocation failure, the first Python inventory, the first Unity inventory, and the failed seal. These are invocation or prerequisite failures and are not relabelled test passes. No formal attempt exists because strict sealing failed before admission.

### Retention checkpoint

The authenticated pre-cleanup checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority1a87-formal-blocked/`. It contains fresh V00/V01 receipts, source/reuse audit, exact generated-prerequisite recovery inventory, the seal failure with selected launch and control bindings, final Python/Unity inventories, a raw-evidence archive, explicit hashes back to the prior V04 checkpoint, and a SHA-256 manifest. No cleanup was performed on the prior live graphs, pilot outputs, or this batch.

H1 remains `InProgress`; the last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. `WEB_TO_LOCAL.md`, protected pins, strict source/runtime verification, and R02 were not modified.
