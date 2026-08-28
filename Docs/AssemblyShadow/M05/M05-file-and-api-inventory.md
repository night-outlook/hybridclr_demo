# M05 file and API inventory

This catalogs the immutable implementation pairing below, not Player acceptance.
The complete per-file A/M/D status and line counts are in
[M05-source-inventory.json](M05-source-inventory.json). Later evidence-only
commits are deliberately outside these counts. All repositories use
`codex/assembly-shadow-m05` and the accepted M04 tag as the comparison base.

| Repository | M05 implementation commit | Added / modified / deleted files | Added / removed lines |
| --- | --- | --- | --- |
| hybridclr | `7f0da36e1a978abfd22c2c195ecb2741588a5d69` | 0 / 2 / 0 | 30 / 0 |
| il2cpp_plus | `8ceb7e40abe458dce5343bedaf250333ef9433a1` | 4 / 15 / 0 | 1200 / 34 |
| hybridclr_unity | `90852d8a59fa14b501cf1c6f1cc38e9d4655ee86` | 20 / 6 / 0 | 3282 / 8 |
| demo | `2b7635339795d80dc2c77c8d3903256abc1c0fd3` | 51 / 10 / 0 | 11152 / 15 |

There are no deleted source paths in these ranges. Added Unity source/scene
assets have paired meta files. No historical M00-M04 evidence is rewritten.

## Managed and native API boundary

The package adds exactly one public operation in
`Runtime/AssemblyShadow/AssemblyShadowRuntime.cs`:

```csharp
AssemblyShadowErrorCode GetTypeResolutionInfo(Type type, out string json)
```

The existing nine operations remain signature-compatible: ConfigureCandidates,
BeginTransaction, StageAssembly, ValidateTransaction, CommitTransaction,
AbortTransaction, GetState, GetAssemblyExecutionMode and GetDiagnosticsJson.
Existing error/state/execution enums and transaction-diagnostics schema remain
unchanged. Editor/Mono is not a simulation; OFF and invalid-input behavior are
specified in the [type contract](M05-type-contract.md).

Runtime changes are confined to `hybridclr/AssemblyShadowRuntimeApi.cpp/.h`.
The new managed signature is registered by the exact icall name
`HybridCLR.AssemblyShadowRuntime::GetTypeResolutionInfo(System.Type,System.String&)`.

`AssemblyShadowTypeResolutionInfo.cs` adds the separate, preserved 18-field DTO:

- Schema/identity: schemaVersion, logicalAssembly, typeKey.
- Execution/type: executionModeCode, executionMode, isActive,
  physicalImageKind, containsShadowTypes.
- Actual optional addresses: inputTypePointer, activeTypePointer,
  baselineTypePointer, pointerDetailsAvailable, baselinePointerAvailable.
- Unsigned counters: definitionCacheHits, definitionCacheMisses,
  compositeRebuilds, allocationRemaps, guardFailures.

The native additions are `AssemblyShadowTypeKey.cpp/.h` and
`AssemblyShadowTypeResolver.cpp/.h`. Main integration declarations are in
`vm/AssemblyShadow.h`; semantic entrypoints include ResolveClassDefinition,
ResolveClass, ResolveType, ResolveAllocationClass, RequireActiveClass,
RecordTypeUse, GetTypeResolutionInfo and IsResolvingTypeMetadata. Changed
callers cover Image/Class/Type, generic and array construction, object/array
allocation, field/member reflection and the pinned RuntimeAssembly module
surface. Definition keys use logical assembly/name/nesting/arity rather than
metadata tokens or transient addresses. Already-created objects are not
reinterpreted, and unsupported module MVID observations remain unavailable.

## Raw-query admission and evidence tooling

New package files cover RawTypeAdmissionConfiguration/Json/Verifier,
ShadowRawTypeAdmissionEvidence and RawTypeAdmissionPropagation, plus tests.
Existing snapshot, linked-evidence, reflection-binding and policy integration
consume the separate domain without changing historical M03/M04 schemas.

The declaration binds exactly five raw operations across five candidates:
Assembly.GetTypes, DefinedTypes, ExportedTypes, Module.GetTypes and the exact
Module.GetType(string,bool,bool) overload. The public demo helper
`M05BoundTypeQueries` returns actual raw API results; it never substitutes an
expected type array. Finite provider and callable-selector requirements remain
in the [raw-query contract](M05-raw-type-admission.md).

`M05RawTypeAdmissionBuild.Generate` preserves the exact returned compiler DLLs
and available PDBs outside Bee's producer directory, validates copy hashes and
then derives/verifies the declaration. Direct compiler outputs are distinct
from the broader precompiled inputs in a general snapshot. Python's `#US`
decoder preserves legal UTF-16 code units while retaining structural and exact
provider checks; strict identifier decoding is unchanged. Linked transport keys
are canonicalized without changing actual assembly identities, and type
inventory reflection names retain each nested TypeDef namespace/name segment.

New demo Editor proof surfaces are M05TypeInventoryProof,
M05TypeSchemaVerifier and M05EditorValidation. Offline proof is implemented in
m05_raw_type_admissions.py, m05_types.py and m05_results.py, with the strict
verify-m05-results.py entrypoint. The existing M03 facade-lookup test adapter
adds only the required identity-class seam and two assertions; production
native behavior is not emulated by that adapter.

## Build and runtime entrypoints

Within `AssemblyShadowDemo.Editor`:

- M05RawTypeAdmissionBuild.Generate.
- M05Build.Configure and ValidateCompilerInputs.
- M05Build.BuildPlayerBaseline, BuildFixtures and BuildFeatureDisabledPlayer.
- M05EditorValidation.Validate, ValidateAndWriteReceipt, ValidateFixtures and
  ValidatePlayerReceipt.

The shared pinned installer remains
`AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability`. M05 never
rebuilds the frozen M01 resource bundles. The isolated scene is
`Assets/AssemblyShadowDemo/Scenes/M05Bootstrap.unity`, using
`AssemblyShadowDemo.M05BootstrapRunner` and M05TypeProbe/M05ResourceProbe.

The CLI fields are `-shadowM05Mode`, `-shadowM05Fixtures`,
`-shadowM05PlayerReceipt` and `-shadowM05Result`. There are 19 fresh-process
modes: P01/P03 variants of T05-01/02/03/05/08/10, then T05-04-EarlyType,
T05-06-P01, T05-07-P03, T05-09-LayoutMismatch, T05-11-FeatureOff,
T05-12-BenchmarkOn and T05-13-BenchmarkOff. Only T05-11 and T05-13 use the
OFF binary. OFF regressions and benchmarks are explicitly required by the
declared type contract, not a separate feature expansion.

Five guarded M05TypeWitness files supply patch-only definitions and actual
reflection/interface observations. The sole old business-source edit adds
`partial` to VersionedPrefabComponent. Resource evidence must still come from
actual old prefab/scene/data bytes and runtime identities. The catalog, source
reviews, Editor tests and compiler snapshots alone do not accept M05 or open
M06.
