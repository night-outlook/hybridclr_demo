# R01B H1 — M07 Fixed-Byte Bootstrap Policy Repair

## Status

Primary Implementation completed for the Local Validation blocker returned at `d8349b3facaa5d420ec41a484854a9bba9e6c1a4`.

Authoritative candidate source / implementation anchor:

`29261690798059077e5263de71526867a32bce30`

The previous Local run proved V00–V03, candidate count 132/132, and all eight unfixed reproduction cells, then real Unity M07 policy validation rejected `AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness` under the global bootstrap rule even though the acquisition site already had a schema-4 `FixedAssemblyBytes` contract.

## Policy repair

The shared `BootstrapIsolationRule` and package pin remain unchanged. The project dependency policy now declares exactly two **target-qualified** bootstrap entries for the one reviewed callsite:

- source/precompile evidence target `image:d60cad840ff603dcfd5d0816196469ecce9576306e5bef2901427a13759d8de4`;
- compiled fixed-image SHA-256 `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`.

The existing `FixedAssemblyBytes` site `h1-count-ordinary-witness-image` remains the byte-acquisition authority. It still binds the exact consumer/type/method signature, original and additional method hashes, operation index 25, provider identity/semantic variants, image path and image SHA. No targetless or method-only H1 bootstrap exemption was added.

`M07FixedByteBootstrapPolicyTests` exercises the real Unity policy construction and `ShadowAssemblyPolicyValidator.ValidateBeforeCompile`, binds the two dependency entries back to the exact fixed-byte site, and verifies that another image target is rejected with `BootstrapReflection`.

## Failure restoration

Review of the first unpublished recovery draft found that it tracked the wrong settings path and did not cover the actual scene mutation observed by Local Validation. The final design therefore separates the proven historical workflow from a narrow outer recovery wrapper:

- `Tools/AssemblyShadow/Invoke-M07Build.Core.ps1` is the proven pre-repair M07 workflow;
- `Tools/AssemblyShadow/Invoke-M07Build.ps1` snapshots workflow-owned inputs before delegating to the core;
- on **failure only**, before rethrowing, it restores exact original bytes for:
  - `Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity`;
  - `ProjectSettings/AssemblyShadowSettings.asset`;
  - `ProjectSettings/EditorBuildSettings.asset`;
- each pre-restore byte set is retained and `workflow-inputs-restored.json` records the exact restoration hashes;
- successful workflow semantics are unchanged by the outer wrapper.

This addresses the exact mutation pair observed by Local while also preserving Editor build settings changed by scene registration.

## Primary validation

Workflow `35135969629` at source anchor `29261690798059077e5263de71526867a32bce30` passed **300/300** bounded tests, zero nonpasses.

- authenticated Apple Bee fixture SHA-256: `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181`
- artifact ID: `10463420165`
- artifact SHA-256: `2f1b9707ed745e47461b2f5baa3e8672b4b3d2ecd4ce5380fb085cc125d299e2`

This is bounded Primary/tool evidence. It is **not** a claim that real Unity M07 now passes. Fresh Local V00–V05 and independent whole-chain M08 remain required.

## Preservation

Protected reproduction behavior/runtime pins, tooling revision `ba8fee33753a5ebc215b7a98739e343d8e05572e`, performance reference `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c`, and all historical Local evidence remain unchanged.

H1 remains `InProgress`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.
