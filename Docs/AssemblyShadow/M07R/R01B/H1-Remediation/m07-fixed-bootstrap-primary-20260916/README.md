# R01B H1 — M07 Fixed-Byte Bootstrap Policy Repair

## Status

Primary Implementation completed for the Local Validation blocker returned at `d8349b3facaa5d420ec41a484854a9bba9e6c1a4`.

Candidate source / implementation anchor:

`c8271753f489ba5a104875ee020f572b604c840e`

Protected reproduction/runtime/performance identities remain unchanged.

## Local empirical basis

The preceding Local cycle proved V00–V03, candidate count 132/132, and captured all eight unfixed reproduction cells. V04 then failed in real Unity before fresh M07 outputs because the global bootstrap rule rejected:

`AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness`

The same acquisition was already authenticated by the schema-4 `FixedAssemblyBytes` site `h1-count-ordinary-witness-image`. This was a policy-join gap, not authority to weaken bootstrap reflection checks.

The failed M07 workflow also left two tracked project-setting owners mutated until Local manually restored their exact HEAD bytes.

## Repair

### Exact fixed-byte/bootstrap join

The package/global validator is unchanged. The project dependency policy now contains exactly two target-qualified bootstrap entries for the one reviewed callsite:

1. source/precompile evidence target `image:d60cad840ff603dcfd5d0816196469ecce9576306e5bef2901427a13759d8de4`;
2. compiled fixed-image target `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`.

Both are limited to consumer `AssemblyShadowDemo.Bootstrap`, provider `AssemblyShadowBaseline.HotUpdate`, type `AssemblyShadowBaseline.HotUpdate.Entry`, and callsite `AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness`.

There is no targetless H1 entry and no generic method-name exemption.

`M07FixedByteBootstrapPolicyTests` binds those two entries back to the exact `FixedAssemblyBytes` site: method signature/hash variants, operation index 25, provider assembly identity, image path/hash, and configuration hash. It invokes the real `ShadowAssemblyPolicyValidator.ValidateBeforeCompile` and separately proves an altered image target remains rejected.

### Workflow exact-byte recovery

`Invoke-M07Build.ps1` now snapshots, before its first Unity M07 invocation:

- `ProjectSettings/AssemblyShadow/AssemblyShadowSettings.asset`
- `ProjectSettings/EditorBuildSettings.asset`

Its outer `finally` preserves the current pre-restore bytes as evidence, restores the original bytes on success or failure, verifies SHA-256 equality, emits `workflow-settings-restored.json`, and treats recovery failure as fatal. The existing P05-specific recovery protocol is retained.

## Primary bounded validation

Workflow `35112630161` at source anchor `c8271753f489ba5a104875ee020f572b604c840e` passed **300/300** bounded tests with zero nonpasses.

- authenticated Apple Bee fixture SHA-256: `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181`
- artifact ID: `10453272042`
- artifact ZIP SHA-256: `c7e01dccb9802d1ce87a0008c214b02301afb27db7c3612b73052014ff6075b5`

The temporary write-capable patch workflows used to apply/review the transform were removed before this source anchor was frozen and are absent from the anchor tree.

This is bounded Primary evidence only. It is not Unity/Apple Player, current-source M07 runtime, V04/V05, M08, or human acceptance.

## Evidence preservation

`local-validation-20260916-e96bc07` and all older checkpoints remain historical evidence under their original source identities. Its V00–V03, 132/132 candidate count result, and eight reproduction cells are preserved; none is relabeled as fresh acceptance for `c8271753...`.

H1 remains `InProgress`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.
