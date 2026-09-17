# Local Validation → Primary Implementation

## Current blocker: post-validation pin guard rejects expected M07 workflow mutations

### Symptom

At handoff `12cf9b25b71bb6fe819b09958a97ab55fb633d7a` and source anchor `f59b0d8d171340951157b01b583df17e380d6f55`, V00–V03 pass and V04 candidate count passes 132/132. The new controlled path successfully invokes real Unity `AssemblyShadowDemo.Editor.M07Build.ValidateCompilerInputs` and mutates both required workflow-owned files. Instead of reaching the explicit controlled failure, it exits at the following post-validation check:

```text
[FAIL] Working bytes do not match pinned Git blob: .../Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity
Controlled M07 validation source or installation differs from the pinned build inputs.
```

A separate normal `Invoke-M07Build.ps1` run fails identically at `Invoke-M07Build.Core.ps1:181`, before baseline resources or Players are built.

### Reproduction

After installing the exact candidate runtime, run either documented command with a new baseline ID. The controlled command is:

```sh
pwsh -NoProfile -File Tools/AssemblyShadow/Invoke-M07Build.ps1 \
  -ProjectPath /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
  -BaselineId M07-Baseline-H1-12cf9b2-Controlled-20260917T0001 \
  -TimeoutSec 28800 \
  -ControlledFailureAfterValidateCompilerInputs
```

The normal command omits the switch and uses a distinct baseline ID. Both exit 1 only after the Unity validation process exits successfully.

### Evidence

Portable evidence is in [local-validation-20260917-12cf9b2](../History/M07R/H1/latest-local/README.md).

- `v04/controlled-recovery/stdout.log`: real Unity `ValidateCompilerInputs` invocation completes successfully.
- `v04/controlled-recovery/stderr.log`: post-validation pinned-scene rejection; the explicit controlled failure text is absent.
- `v04/controlled-recovery-root.tar.gz`: originals, pre-restore bytes, and `workflow-inputs-restored.json` proving scene/settings mutation and exact three-file restoration.
- `v04/controlled-recovery/post-recovery-preflight.json`: authority passes after restoration.
- `v04/normal-m07/stdout.log` and `stderr.log`: the separate normal workflow reaches the same post-validation failure.
- `v04/normal-m07-recovery-root.tar.gz`: second independent exact restoration receipt and bytes.
- `failure-analysis.json`: machine-readable root cause, impact, and recommended direction.

### Root cause

`ValidateCompilerInputs` intentionally writes `Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity` and `ProjectSettings/AssemblyShadowSettings.asset`. The outer wrapper correctly captures their original bytes before Unity starts.

Immediately afterward, both workflows call the full installed-runtime verifier again. The controlled path does so through `Assert-M07ControlledPinnedInputs`; the normal path does so through `Assert-M07PinnedInputs` at core line 181. That verifier treats the intentionally changed scene as unauthorized source drift because it still requires the working file to equal the pinned Git blob. The post-validation guard therefore conflicts with the mutation that validation is required to perform.

The design allowed this because the new controlled-path tests did not prove that the explicit post-validation throw is reachable after real Unity mutation, while the normal workflow retained the same unscoped guard between validation and resource generation.

### Impact

The required controlled-failure condition has no coverage even though actual mutation and exact restoration are proven. The normal workflow cannot produce baseline resources, native ON/OFF Players, fixtures, or Editor replay. Startup11, 8192/8193, remaining M03–M07 coverage, controlled performance, V05 successor packaging, and independent M08 are blocked. Human Review Gate is not ready and R02 remains closed.

### Recommended direction

Keep the outer three-file snapshot/restoration contract. Change post-validation authority checks so they continue authenticating immutable compiler/runtime/source inputs while binding the expected workflow-owned mutations to their captured originals and validation outputs. Add a real integration regression that reaches the explicit controlled throw and a separate normal end-to-end M07 workflow regression. Do not broaden bootstrap/fixed-byte policy or allowlists.

### Uncertainty

This run proves that real validation succeeds, required files mutate, and exact restoration works twice. It does not establish baseline resource generation or any downstream runtime/performance behavior because both workflows stop at the immediate post-validation guard.

Historical returns are indexed by `../Evidence/evidence-catalog.json` at predecessor commit `7cb710fa38464b1977a69619fea2b5fc93f79966`.
