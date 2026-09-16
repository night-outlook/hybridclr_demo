# Static Review — M07 Fixed-Byte Bootstrap Repair

## Verdict

**Primary bounded review: PASS for Local Validation handoff.** This is not Unity/M07 runtime acceptance, M08, or Human Review Gate acceptance.

## Reviewed invariants

- Candidate source anchor is `29261690798059077e5263de71526867a32bce30`.
- Protected reproduction demo remains `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` with unfixed behavior source `4e3d2035991ab5629265ac663e61bcb2ca62828b`.
- Reproduction tooling remains `ba8fee33753a5ebc215b7a98739e343d8e05572e`.
- Candidate/reproduction native pins remain `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` / `99cdb1b67e4ed07b70732a2148cb69e079ca41cf`.
- Shared package and IL2CPP pins remain `0ea633a2c5b936b5af69d944593c55bd2783fca9` / `6be7f38bec2fa4677d24efc1a4a1294240789933`.
- Performance reference remains `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c`.

## Policy boundary

- Global `BootstrapIsolationRule` is not changed or bypassed.
- Exactly one callsite is reconciled: `AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness`.
- Exactly two target-qualified forms are admitted because real policy scanning produces two authenticated representations of the same fixed-byte acquisition: source/precompile evidence token and compiled image SHA.
- No targetless, provider-wide, type-wide, or method-only bootstrap exemption is introduced.
- The existing schema-4 `FixedAssemblyBytes` binding remains authoritative for method hashes, operation index, provider identity/variants, image path, and image SHA.
- Unity integration regression requires the real policy to validate and separately proves another image target remains rejected.

## Failure recovery boundary

The initial recovery draft was rejected during Primary review because it did not match Local's real mutation set. Final `Invoke-M07Build.ps1` is an outer failure guard around `Invoke-M07Build.Core.ps1`.

Before the first core Unity operation it snapshots exact bytes for:

1. `Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity`;
2. `ProjectSettings/AssemblyShadowSettings.asset`;
3. `ProjectSettings/EditorBuildSettings.asset`.

On failure only, after owned Unity processes exit, it preserves current bytes, restores the originals exactly, writes `workflow-inputs-restored.json`, then rethrows the original workflow failure. A restoration failure is surfaced explicitly instead of hiding the original failure. Successful workflow behavior is not rolled back.

## Regression evidence

Primary workflow `35135969629` at `29261690798059077e5263de71526867a32bce30` passed **300/300** bounded tests, zero nonpasses.

Artifact `10463420165`, SHA-256 `2f1b9707ed745e47461b2f5baa3e8672b4b3d2ecd4ce5380fb085cc125d299e2`.

The bounded suite covers the exact dependency/binding bridge and exact wrapper/core recovery layout. The Unity test source additionally exercises the actual project policy API, but Primary CI does not execute Unity; Local V01 must execute that NUnit test in Unity and V04 must rerun the real M07 workflow.

## Residual risk

Fresh Local validation must prove:

- the real Unity policy scanner emits only the reviewed source/image target forms;
- `ValidateCompilerInputs` passes under the current source anchor;
- a deliberately or naturally failing M07 invocation restores the scene/settings exact bytes and emits the restoration receipt;
- the normal successful M07 chain continues through startup/capacity/performance evidence.

Any need for a third bootstrap target or broader entrypoint rule returns to Primary.
