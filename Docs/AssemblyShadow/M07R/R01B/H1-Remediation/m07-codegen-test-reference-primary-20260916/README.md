# R01B H1 — M07 CodeGen Test Reference / Recovery Proof Review

## Status

Primary Implementation reviewed the Local Validation correction returned at:

`1d0be06d5dc61eb963a13a72061be82f8fd04bf4`

Final candidate source / implementation anchor:

`f59b0d8d171340951157b01b583df17e380d6f55`

The correction is retained. `AssemblyShadowDemo.EditorTests.asmdef` now has a direct reference to `Unity.HybridCLR.AssemblyShadow.CodeGen`, which is required because `M07FixedByteBootstrapPolicyTests.cs` imports `HybridCLR.AssemblyShadow.CodeGen` directly and Unity asmdef references are non-transitive.

## Scope

The asmdef change is bounded to the Editor test assembly:

- `includePlatforms` remains exactly `Editor`;
- `autoReferenced` remains false;
- `UNITY_INCLUDE_TESTS` remains required;
- the CodeGen reference occurs exactly once;
- no Player/runtime assembly dependency is added.

Local empirically demonstrated that this one-line dependency correction makes the real Unity 2022.3.62f2 candidate compile pass and `M07FixedByteBootstrapPolicyTests` pass 2/2. The old source authority then rejected the changed bytes, which was the expected fail-closed behavior.

## Controlled post-mutation restoration

Primary also closed the remaining V04 evidence gap. `Invoke-M07Build.ps1` now exposes the opt-in switch:

`-ControlledFailureAfterValidateCompilerInputs`

With exact installed candidate pins, this mode:

1. snapshots the three wrapper-owned scene/settings files;
2. verifies installed candidate pins;
3. executes real Unity `AssemblyShadowDemo.Editor.M07Build.ValidateCompilerInputs` with the requested fresh baseline ID;
4. verifies installed pins again;
5. deliberately fails before entering the normal core workflow;
6. runs the existing outer exact-byte restoration and rethrows.

The normal invocation without this switch still delegates to `Invoke-M07Build.Core.ps1` unchanged.

Local V04 must use a fresh baseline ID and prove actual pre-restore mutation. Merely receiving `workflow-inputs-restored.json` after a pre-Unity/no-op failure is not coverage.

## Primary bounded validation

Workflow: `35179309998`

- source anchor: `f59b0d8d171340951157b01b583df17e380d6f55`
- tests: **302/302 Passed**
- nonpasses: `0`
- authenticated Apple Bee graph SHA-256: `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181`
- artifact ID: `10478699390`
- artifact SHA-256: `28239edbda587ca61f9175ef42b334c588363a28226d955b25198a7219afd258`

This does not establish current-source Unity/Player/M07/runtime/performance acceptance, M08 PASS, or Human Review Gate readiness.

## Preserved identities

No protected identity moved:

- protected reproduction demo `352d7474dd7c2ffd9b9501d8fa42334a3b236e05`;
- unfixed behavior source `4e3d2035991ab5629265ac663e61bcb2ca62828b`;
- reproduction tooling `ba8fee33753a5ebc215b7a98739e343d8e05572e`;
- candidate native `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`;
- reproduction native `99cdb1b67e4ed07b70732a2148cb69e079ca41cf`;
- shared package `0ea633a2c5b936b5af69d944593c55bd2783fca9`;
- IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933`;
- performance reference `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c`.

All historical Local checkpoints remain evidence under their original identities and dispositions.
