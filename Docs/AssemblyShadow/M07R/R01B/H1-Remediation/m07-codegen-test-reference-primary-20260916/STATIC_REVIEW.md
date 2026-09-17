# Static Review — M07 CodeGen Test Reference / Recovery Proof

## Verdict

**PASS for Primary → Local Validation handoff.**

This is a bounded source/tool review only. It is not current-source Unity acceptance, M08, or Human Review Gate approval.

## Findings

### F1 — Local asmdef correction is necessary and bounded

`M07FixedByteBootstrapPolicyTests.cs` directly imports `HybridCLR.AssemblyShadow.CodeGen`. The test asmdef previously relied on `HybridCLR.Editor`, but Unity asmdef references are non-transitive. The direct `Unity.HybridCLR.AssemblyShadow.CodeGen` reference is therefore required for this test assembly to compile.

The retained change does not expand production/runtime dependencies:

- only `AssemblyShadowDemo.EditorTests.asmdef` changes;
- platform remains Editor-only;
- `UNITY_INCLUDE_TESTS` remains required;
- `autoReferenced=false` remains unchanged.

Local's real Unity compile PASS and 2/2 M07 policy-test PASS are valid correction evidence. The previous source-authority failure after the edit is expected and demonstrates fail-closed source identity.

### F2 — Primary regression locks the dependency boundary

`test_h1_m07_policy_bridge.py` now requires exactly one direct CodeGen reference and preserves the Editor/test-only constraints. Removal, duplication, platform broadening, or loss of `UNITY_INCLUDE_TESTS` fails bounded Primary validation.

### F3 — post-mutation failure restoration is now deterministic

The prior Local controlled failure occurred before actual M07 configuration mutation and was correctly classified `NoCoverage` for mutation-restoration.

`Invoke-M07Build.ps1` now adds only the opt-in `ControlledFailureAfterValidateCompilerInputs` validation path. It verifies installed pins, executes the real Unity `M07Build.ValidateCompilerInputs`, verifies pins again, then intentionally fails so the existing outer recovery restores:

- `Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity`;
- `ProjectSettings/AssemblyShadowSettings.asset`;
- `ProjectSettings/EditorBuildSettings.asset`.

Default successful behavior remains delegated to `Invoke-M07Build.Core.ps1`.

V04 must prove that at least the scene and `AssemblyShadowSettings.asset` actually differed before restoration when a fresh baseline ID is used. A restoration receipt without actual mutation is not acceptance evidence.

### F4 — M07 policy acceptance remains narrow

No bootstrap rule, fixed-byte binding, target allowlist, runtime pin, ABI, count behavior, or performance methodology was broadened in this repair.

The existing exact two-target fixed-byte/bootstrap contract remains unchanged and must pass fresh Unity validation again under the final source anchor.

## Validation receipt

Final executable source anchor:

`f59b0d8d171340951157b01b583df17e380d6f55`

Bounded Primary CI:

- workflow `35179309998`
- **302/302 Passed**
- zero nonpasses
- artifact `10478699390`
- artifact SHA-256 `28239edbda587ca61f9175ef42b334c588363a28226d955b25198a7219afd258`

## Gate disposition

H1 remains `InProgress / BlockedPendingFreshV00ToV05`.

Last independent whole-chain M08 remains `FAIL`.

`humanGatePassed=false`; `mayEnterR02=false`.
