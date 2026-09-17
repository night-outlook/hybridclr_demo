# Local Validation Tasks — M07 CodeGen Test Reference / Recovery Proof

## V00 — authority

1. Pull candidate `codex/assembly-shadow-r01b-h1` at the final published handoff HEAD.
2. Record checkout HEAD and authoritative source anchor `f59b0d8d171340951157b01b583df17e380d6f55` separately.
3. Require candidate `h1_handoff_preflight.py` → `SourceTargetVerifiedNotBuildAccepted`.
4. Require split reproduction-tooling preflight at exact `ba8fee33753a5ebc215b7a98739e343d8e05572e`.
5. Verify every protected demo/native/package/IL2CPP/performance identity remains exact.

Stop on V00 failure.

## V01 — compile / policy integration

Run the full H1 Python inventory and bounded Primary suite, then real Unity 2022.3.62f2 compilation for candidate and reproduction tooling.

For candidate, require:

- `AssemblyShadowDemo.EditorTests.asmdef` has direct `Unity.HybridCLR.AssemblyShadow.CodeGen` reference;
- compile has zero errors;
- `M07FixedByteBootstrapPolicyTests` passes **2/2** using the real policy construction/validator;
- no target, binding, or bootstrap-policy broadening.

## V02 — fresh candidate provenance

Run fresh candidate ON/Debug normal-cache provenance under source anchor `f59b0d8d...`.

Require strict native compiler/PCH/store proof, schema-3 managed proof, exact fresh Player binding, and exact restoration. Do not clear Bee cache or substitute legacy `--reuse-proof`.

## V03 — fresh six-build set

Use candidate-owned `h1_count_build_batch_tooling.py` to produce:

- candidate ON/OFF × Debug/Release;
- reproduction ON Debug/Release.

Require strict current native/managed provenance, reproduction-tooling binding, and exact restoration for every accepted build.

## V04 — count + deterministic mutation/recovery + full M07/runtime/performance

Re-run the candidate 132-cell matrix and all eight unfixed reproduction observations under the current anchor. Preserve prior Local count evidence as historical comparison only.

### Controlled post-mutation recovery

After fresh V03 has installed the exact candidate runtime, choose a **new** M07 baseline ID and run:

```powershell
pwsh -NoProfile -File Tools/AssemblyShadow/Invoke-M07Build.ps1 `
  -ProjectPath /ABS/CANDIDATE `
  -BaselineId M07-Baseline-H1-<NEW-ID> `
  -TimeoutSec 28800 `
  -ControlledFailureAfterValidateCompilerInputs
```

Require:

1. the real Unity `M07Build.ValidateCompilerInputs` succeeds before the deliberate failure;
2. the error is the explicit controlled post-validation failure, not a pin/preflight/Unity-policy failure;
3. `workflow-inputs-restored.json` reports `ExactBytesRestored`;
4. pre-restore evidence proves **actual mutation**: `M07Bootstrap.unity` and `ProjectSettings/AssemblyShadowSettings.asset` hashes must differ from their original hashes; `EditorBuildSettings.asset` may or may not change but must be restored exactly;
5. all three restored hashes equal originals;
6. post-recovery candidate source preflight passes.

A failure before real `ValidateCompilerInputs`, or a receipt with no scene/settings mutation, is `NoCoverage` for this requirement.

### Successful chain

Then use another fresh baseline ID and invoke normal `Invoke-M07Build.ps1` **without** the controlled switch. Complete:

- successful compiler policy validation;
- baseline resources;
- native ON/OFF Players;
- fixtures and Editor replay;
- startup11;
- 8192/8193 capacity boundary;
- required lazy/dense/generic/array/reflection/FieldRVA/old-Player and M03–M07 coverage;
- controlled Development performance against protected reference `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` on common supported workloads.

Do not broaden bootstrap or fixed-byte policy locally.

## V05 — successor + independent M08

Build the successor package only from fresh current-anchor evidence. Include V00 authority outputs, V01 compile/policy tests, six-build provenance, count results, controlled mutation/restoration evidence, successful M07/runtime/startup/capacity/performance evidence, and historical checkpoints under original identities.

Authenticate archive/index bytes and semantic membership, then run a genuine independent whole-chain design → source → build → raw-evidence M08 review.

Only genuine independent whole-chain **M08 PASS** may make H1 Ready for Human Review Gate. Stop for explicit human approval. Do not begin R02.
