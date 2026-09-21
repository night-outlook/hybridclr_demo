# R01B H1 — Current Primary Implementation

## Status

Latest Local return: `8788d123ca7769396cf14c707f8df13ac764223b`.

Candidate build-input source anchor: `69130bbb3a6df516916dddb5ad263799a7c6e5e3`.

H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

## Returned V04 blockers

The 2026-09-20 Local cycle proved the prior controlled-label repair in real Unity: protected profile-1 completed Native ON. Two later boundaries then failed.

1. **Exact settings restoration:** `R00ControlledBuild.RestoreSettings` restored the semantic IL2CPP code-generation value, but Unity serialized `ProjectSettings/ProjectSettings.asset` differently (`il2cppCodeGeneration: {}` became an explicit `Standalone: 0`). The next exact source guard correctly rejected the byte drift.
2. **Nested provenance authority:** current profile-2 entered `H1BuildInputProvenance.CaptureAfterGenerate`, whose native-only verifier passes `--skip-demo-source`. The child inherited the outer M07 authority environment, so the verifier correctly rejected that unsupported combination.

## Primary implementation

### Controlled Player mutable-input transaction

`Invoke-M07PlayerMethodWithGeneratedInputRecovery` now owns two tracked inputs for every Native ON/OFF Player stage:

- `Assets/HybridCLRGenerate/link.xml`;
- `ProjectSettings/ProjectSettings.asset`.

For each input it:

1. requires the project to be closed;
2. captures original bytes and SHA-256;
3. writes an immutable per-stage backup;
4. invokes the owned Unity Player build;
5. retains post-build bytes;
6. exact-byte restores the original in the finally path;
7. verifies the restored SHA-256;
8. emits a per-input restoration receipt.

Recovery runs on both success and failure. A restore failure takes precedence; otherwise the original stage failure is preserved. The source-authority guard remains unchanged and runs only after the transaction returns.

Existing `link.xml` receipt kind remains `M07GeneratedPlayerInputRestoration`. Project settings uses `M07ControlledPlayerSettingsRestoration`.

### Nested native-only provenance scope

`H1BuildInputProvenance` still invokes the verifier with `--skip-demo-source`, because this subprocess is only proving the installed native/runtime graph.

Immediately before starting that child process, its `ProcessStartInfo.EnvironmentVariables` removes:

- `H1_M07_WORKFLOW_AUTHORITY_ROOT`;
- `H1_M07_WORKFLOW_BASELINE_ID`.

Only the child is scoped this way. The Unity process and outer coordinator keep the M07 authority environment, and the unchanged outer pinned-input check still performs fail-closed demo-source/workflow authority after each controlled Player stage.

The provenance capture records `verificationEnvironmentScope=NativeOnlyWithoutOuterM07WorkflowAuthority`.

## Regression coverage

Primary added/updated:

- `Tools/AssemblyShadow/tests/test_m07_player_input_recovery.ps1`: extracts the production PowerShell helper and verifies exact restoration of both inputs on success and on a simulated stage failure, including receipts and original failure preservation; no Unity required.
- `Tools/AssemblyShadow/tests/test_m07_generated_input_recovery_labels.ps1`: retains direct real-binder coverage for all four stage labels.
- `Tools/AssemblyShadow/tests/test_h1_m07_workflow_authority.py`: locks both repaired contracts and confirms the global verifier still rejects caller `--skip-demo-source` under M07 authority.
- `Assets/AssemblyShadowDemo/Tests/Editor/M07BuildTests.cs`: asserts the controlled settings transaction is present in the Unity-visible workflow source.
- `.github/workflows/h1-bee-primary.yml`: runs both direct PowerShell regressions and triggers on `H1BuildInputProvenance.cs`.

No HybridCLR native, HybridCLR Unity, IL2CPP, runtime transaction, capacity/index, dense metadata, performance protocol, schedule, or analyzer code changed.

## Local validation objective

Restart fresh V00. Then validate both complete `-ControlledPerformanceBuilds` workflows in one batch.

For each controlled label require **both** restoration receipts:

- `<label>-link-xml-restored.json`;
- `<label>-project-settings-restored.json`.

Both receipts must report `ExactBytesRestored`, with original and restored hashes equal. Candidate controlled evidence must also show the native provenance capture succeeded with the new nested verification scope.

Only after both profile graphs complete may Local continue to current-anchor old-Player rejection, build-map freeze, preregistration, pilots, formal samples, analysis, V05, and independent M08.

## Gate

H1 remains `InProgress`. Do not begin R02.
