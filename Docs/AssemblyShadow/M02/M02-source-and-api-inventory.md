# M02 source and API inventory

This inventory covers the executable source boundary used by the acceptance
Player: demo `0939b0ed667abd2694e5e7dbab23b6f670a8642f` and package
`6d603459e52027cd31616c71f137d29aadaf4ea2`, compared with each repository's
`assembly-shadow-m01-poc` tag. Later pin and evidence closeout changes do not
alter these build inputs. Runtime and native source are unchanged from M01.

## New Editor API surface

These are tooling APIs, not a production native Shadow transaction contract.
Public receipt/model types describe the versioned inputs and outputs of these
operations; their fields are defined in the source files listed below.

| Responsibility | Public operations and types |
| --- | --- |
| Settings | `AssemblyShadowSettings.Instance/LoadOrCreate/Save`; `AssemblyShadowSettingsProvider`; `AssemblyShadowSettingsUtil.CreatePolicyConfiguration/ValidateSettings/ValidateSettingsOrThrow` |
| Metadata and identity | `DnlibAssemblyLoader.Load`; `CompiledAssemblySet`; `AssemblyDescriptor/TypeDescriptor`; `AssemblyIdentityUtil`; `VerifiedTargetFrameworkReferences` |
| Dependency closure | `AssemblyReferenceGraph`, `AssemblyDependencyEdge`; reverse closure, stable dependency-first order, explicit and frozen-edge validation |
| Hashing | `AssemblySemanticHasher.Compute`; `SemanticHashOptions`, `SemanticHashSchema`, `SemanticHashReport/SemanticHashSections`; `ShadowHash` |
| Policy | `ShadowAssemblyPolicyValidator.ValidateCompiled/ValidateDefinitions/ValidateBeforeCompile/ValidateBootstrapResources`; `AssemblyNamePolicy`; capability, dependency, whitelist, Bootstrap-entry and diagnostic models |
| Serialized ABI | `UnitySerializedTypeAnalyzer.Analyze`; `ResourceAbiHasher`; `ResourceAbiDiffComparer`; descriptor, field, type, difference-level and script-index models |
| Resource indexing | `AssetScriptReferenceIndexer`; `UnitySerializedReferenceParser`; `BundleImpactAnalyzer`; `IResourceAssetReader`, `FrozenResourceAssetReader`, `ResourceAssetReferences/ResourceTypeIdentity` |
| Target snapshots | `AssemblySnapshot`; `AssemblySnapshotReceipt/SnapshotFile`; `TargetFrameworkReferenceVerifier`; `ShadowFilteredInputPolicy`; `VerifiedLinkedRuntimeReferences` |
| Player provenance | `ShadowPlayerInputCapture.Begin/CompleteSuccessfulBuild/End`; before/after filter callbacks; `ShadowLinkedPlayerEvidence` and linked-file/receipt models |
| Resource provenance | `ShadowResourceBaseline.Build/ReadAndVerify/RequirePlayerAbi`; build request, verified baseline, source/script, builtin object/module and reconstruction-proof models |
| Manifest building | `ShadowBaselineManifestBuilder.Build`; `ShadowPatchManifestBuilder.Build`; baseline/patch requests, manifests, bundle map/artifact and patch-assembly models |
| Source/session binding | `ShadowSourcePins/ShadowRepositoryPin`; `ShadowBuildSession` |
| Generator adapter | `IRuntimeAssemblyInputProvider`, `ShadowRuntimeAssemblyInputProvider`, `RuntimeAssemblyInputKind` (Link, MethodBridge, AotGenericReference, ReversePInvoke, Diagnostics) |
| Reflection contracts | `ReflectionBindingConfiguration/Site/Defines/Exception`; `ReflectionBindingTransformer`; `ReflectionBindingFingerprint`; `ReflectionBindingsILPostProcessor`; transform and verified-binding records |
| Linked reflection proof | `CapturedReflectionRetargetingProfile`; module/forwarder records; `ShadowReflectionBindingEvidence.ValidateCompiled/Capture/ReadFixedImages`; `ShadowReflectionBindingLinkedEvidence` and linked-site/framework/receipt models |

### Package Editor menu commands

Under `HybridCLR/Assembly Shadow`:

- `Build Baseline Resources`
- `Build Baseline Manifest`
- `Compile Patch Snapshot`
- `Build Patch`

Their batchmode entrypoints are public static methods on
`HybridCLR.Editor.AssemblyShadow.AssemblyShadowBuildCommands`.
`Argument` handles the documented command-line input overrides.

### Demo entrypoints

All are under `AssemblyShadowDemo.Editor`:

- `M02Build.Configure`, `ValidateConfiguration`, `BuildPlayerBaseline`,
  `ValidateCompilerInputs`.
- `M02EditorValidation.Validate` (normally invoked through the guarded wrapper).
- `M02FrozenResources.Import`.
- `M02ReflectionBindingValidation.ValidateProjectAssets`,
  `ValidateEditorBehavior`, `StageConfiguration`.
- `M02StructuralPatchCompilation.Prepare`, `Compile`, `Restore`,
  `GetValidationRunDirectory`, `ReadPreparedSnapshot`.

The Bootstrap adds the `M02ReflectionBindings` Player mode. It is a test probe,
not an approval to reflect on or activate arbitrary business assemblies.

### Command-line tools

- `Tools/AssemblyShadow/Invoke-ShadowEditorTests.ps1`: guarded NUnit execution.
- `Tools/AssemblyShadow/Invoke-M02EditorValidation.ps1`: isolated P05 Editor
  domain, verified restoration, then baseline-domain T02 validation.
- `Tools/AssemblyShadow/verify-m02-results.py`: read-only artifact verification
  with optional generated JSON output.

## Exact source-boundary changed paths

Status letters are Git `--name-status` output. Unity meta files are included.
The report, this inventory, review record and archived evidence are milestone
documentation; the final reviewed commit records the complete closeout diff.

### Demo (40 paths)

```text
M	Assets/AssemblyShadowDemo/AssemblyA/Contracts/AssemblyAContractVersion.cs
M	Assets/AssemblyShadowDemo/AssemblyA/Implementation/Extensibility/VersionedComponentBase.cs
M	Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/VersionedPrefabComponent.cs
M	Assets/AssemblyShadowDemo/Bootstrap/AssemblyShadowDemo.Bootstrap.asmdef
A	Assets/AssemblyShadowDemo/Bootstrap/M02ReflectionBindingProbe.cs
A	Assets/AssemblyShadowDemo/Bootstrap/M02ReflectionBindingProbe.cs.meta
M	Assets/AssemblyShadowDemo/Bootstrap/ShadowBootstrap.cs
A	Assets/AssemblyShadowDemo/Bootstrap/link.xml
A	Assets/AssemblyShadowDemo/Bootstrap/link.xml.meta
A	Assets/AssemblyShadowDemo/Editor/M02Build.cs
A	Assets/AssemblyShadowDemo/Editor/M02Build.cs.meta
A	Assets/AssemblyShadowDemo/Editor/M02EditorValidation.cs
A	Assets/AssemblyShadowDemo/Editor/M02EditorValidation.cs.meta
A	Assets/AssemblyShadowDemo/Editor/M02FrozenResources.cs
A	Assets/AssemblyShadowDemo/Editor/M02FrozenResources.cs.meta
A	Assets/AssemblyShadowDemo/Editor/M02ReflectionBindingValidation.cs
A	Assets/AssemblyShadowDemo/Editor/M02ReflectionBindingValidation.cs.meta
A	Assets/AssemblyShadowDemo/Editor/M02StructuralPatchCompilation.cs
A	Assets/AssemblyShadowDemo/Editor/M02StructuralPatchCompilation.cs.meta
M	Assets/AssemblyShadowDemo/Tests/Editor/AssemblyShadowDemo.EditorTests.asmdef
A	Assets/AssemblyShadowDemo/Tests/Editor/M02DependencyFixtureTests.cs
A	Assets/AssemblyShadowDemo/Tests/Editor/M02DependencyFixtureTests.cs.meta
A	Assets/AssemblyShadowDemo/Tests/Editor/M02ReflectionBindingValidationTests.cs
A	Assets/AssemblyShadowDemo/Tests/Editor/M02ReflectionBindingValidationTests.cs.meta
A	Assets/AssemblyShadowDemo/Tests/Editor/M02StructuralPatchCompilationTests.cs
A	Assets/AssemblyShadowDemo/Tests/Editor/M02StructuralPatchCompilationTests.cs.meta
A	Docs/AssemblyShadow/M02/M02-report.md
M	Packages/manifest.json
A	ProjectSettings/AssemblyShadowDependencies.json
A	ProjectSettings/AssemblyShadowExtensibilityWhitelist.json
A	ProjectSettings/AssemblyShadowReflectionBindings.json
A	ProjectSettings/AssemblyShadowResources.json
A	ProjectSettings/AssemblyShadowSettings.asset
M	ProjectSettings/AssemblyShadowSourcePins.json
A	Tools/AssemblyShadow/Invoke-M02EditorValidation.ps1
A	Tools/AssemblyShadow/Invoke-ShadowEditorTests.ps1
M	Tools/AssemblyShadow/README.md
A	Tools/AssemblyShadow/m02_results.py
A	Tools/AssemblyShadow/tests/test_m02_results.py
A	Tools/AssemblyShadow/verify-m02-results.py
```

### Package (153 paths)

```text
A	Editor/AssemblyShadow.CodeGen.meta
A	Editor/AssemblyShadow.CodeGen/CapturedReflectionRetargetingProfile.cs
A	Editor/AssemblyShadow.CodeGen/CapturedReflectionRetargetingProfile.cs.meta
A	Editor/AssemblyShadow.CodeGen/HybridCLR.AssemblyShadow.CodeGen.asmdef
A	Editor/AssemblyShadow.CodeGen/HybridCLR.AssemblyShadow.CodeGen.asmdef.meta
A	Editor/AssemblyShadow.CodeGen/ReflectionAcquisitionGuards.cs
A	Editor/AssemblyShadow.CodeGen/ReflectionAcquisitionGuards.cs.meta
A	Editor/AssemblyShadow.CodeGen/ReflectionBindingConfiguration.cs
A	Editor/AssemblyShadow.CodeGen/ReflectionBindingConfiguration.cs.meta
A	Editor/AssemblyShadow.CodeGen/ReflectionBindingFingerprint.cs
A	Editor/AssemblyShadow.CodeGen/ReflectionBindingFingerprint.cs.meta
A	Editor/AssemblyShadow.CodeGen/ReflectionBindingLinkedVerifier.cs
A	Editor/AssemblyShadow.CodeGen/ReflectionBindingLinkedVerifier.cs.meta
A	Editor/AssemblyShadow.CodeGen/ReflectionBindingTransformer.cs
A	Editor/AssemblyShadow.CodeGen/ReflectionBindingTransformer.cs.meta
A	Editor/AssemblyShadow.CodeGen/ReflectionBindingsILPostProcessor.cs
A	Editor/AssemblyShadow.CodeGen/ReflectionBindingsILPostProcessor.cs.meta
A	Editor/AssemblyShadow.meta
A	Editor/AssemblyShadow/Build.meta
A	Editor/AssemblyShadow/Build/AssemblyShadowBuildCommands.cs
A	Editor/AssemblyShadow/Build/AssemblyShadowBuildCommands.cs.meta
A	Editor/AssemblyShadow/Build/AssemblySnapshot.cs
A	Editor/AssemblyShadow/Build/AssemblySnapshot.cs.meta
A	Editor/AssemblyShadow/Build/ShadowArtifactWriter.cs
A	Editor/AssemblyShadow/Build/ShadowArtifactWriter.cs.meta
A	Editor/AssemblyShadow/Build/ShadowBaselineManifestBuilder.cs
A	Editor/AssemblyShadow/Build/ShadowBaselineManifestBuilder.cs.meta
A	Editor/AssemblyShadow/Build/ShadowBuildSession.cs
A	Editor/AssemblyShadow/Build/ShadowBuildSession.cs.meta
A	Editor/AssemblyShadow/Build/ShadowFilteredInputPolicy.cs
A	Editor/AssemblyShadow/Build/ShadowFilteredInputPolicy.cs.meta
A	Editor/AssemblyShadow/Build/ShadowLinkedPlayerEvidence.cs
A	Editor/AssemblyShadow/Build/ShadowLinkedPlayerEvidence.cs.meta
A	Editor/AssemblyShadow/Build/ShadowManifests.cs
A	Editor/AssemblyShadow/Build/ShadowManifests.cs.meta
A	Editor/AssemblyShadow/Build/ShadowPatchManifestBuilder.cs
A	Editor/AssemblyShadow/Build/ShadowPatchManifestBuilder.cs.meta
A	Editor/AssemblyShadow/Build/ShadowPlayerInputCapture.cs
A	Editor/AssemblyShadow/Build/ShadowPlayerInputCapture.cs.meta
A	Editor/AssemblyShadow/Build/ShadowReflectionBindingEvidence.cs
A	Editor/AssemblyShadow/Build/ShadowReflectionBindingEvidence.cs.meta
A	Editor/AssemblyShadow/Build/ShadowReflectionBindingLinkedEvidence.cs
A	Editor/AssemblyShadow/Build/ShadowReflectionBindingLinkedEvidence.cs.meta
A	Editor/AssemblyShadow/Build/ShadowResourceBaseline.cs
A	Editor/AssemblyShadow/Build/ShadowResourceBaseline.cs.meta
A	Editor/AssemblyShadow/Build/ShadowSourcePins.cs
A	Editor/AssemblyShadow/Build/ShadowSourcePins.cs.meta
A	Editor/AssemblyShadow/Build/TargetFrameworkReferenceVerifier.cs
A	Editor/AssemblyShadow/Build/TargetFrameworkReferenceVerifier.cs.meta
A	Editor/AssemblyShadow/Build/VerifiedLinkedRuntimeReferences.cs
A	Editor/AssemblyShadow/Build/VerifiedLinkedRuntimeReferences.cs.meta
A	Editor/AssemblyShadow/Generation.meta
A	Editor/AssemblyShadow/Generation/RuntimeAssemblyInputProvider.cs
A	Editor/AssemblyShadow/Generation/RuntimeAssemblyInputProvider.cs.meta
A	Editor/AssemblyShadow/Hashing.meta
A	Editor/AssemblyShadow/Hashing/AssemblySemanticHasher.cs
A	Editor/AssemblyShadow/Hashing/AssemblySemanticHasher.cs.meta
A	Editor/AssemblyShadow/Hashing/CanonicalSignatureWriter.cs
A	Editor/AssemblyShadow/Hashing/CanonicalSignatureWriter.cs.meta
A	Editor/AssemblyShadow/Hashing/SemanticHashReport.cs
A	Editor/AssemblyShadow/Hashing/SemanticHashReport.cs.meta
A	Editor/AssemblyShadow/Hashing/SemanticHashSchema.cs
A	Editor/AssemblyShadow/Hashing/SemanticHashSchema.cs.meta
A	Editor/AssemblyShadow/Metadata.meta
A	Editor/AssemblyShadow/Metadata/AssemblyDescriptor.cs
A	Editor/AssemblyShadow/Metadata/AssemblyDescriptor.cs.meta
A	Editor/AssemblyShadow/Metadata/AssemblyIdentityUtil.cs
A	Editor/AssemblyShadow/Metadata/AssemblyIdentityUtil.cs.meta
A	Editor/AssemblyShadow/Metadata/AssemblyReferenceGraph.cs
A	Editor/AssemblyShadow/Metadata/AssemblyReferenceGraph.cs.meta
A	Editor/AssemblyShadow/Metadata/CompiledAssemblySet.cs
A	Editor/AssemblyShadow/Metadata/CompiledAssemblySet.cs.meta
A	Editor/AssemblyShadow/Metadata/DnlibAssemblyLoader.cs
A	Editor/AssemblyShadow/Metadata/DnlibAssemblyLoader.cs.meta
A	Editor/AssemblyShadow/Metadata/VerifiedTargetFrameworkReferences.cs
A	Editor/AssemblyShadow/Metadata/VerifiedTargetFrameworkReferences.cs.meta
A	Editor/AssemblyShadow/Model.meta
A	Editor/AssemblyShadow/Model/ShadowConfiguration.cs
A	Editor/AssemblyShadow/Model/ShadowConfiguration.cs.meta
A	Editor/AssemblyShadow/Serialization.meta
A	Editor/AssemblyShadow/Serialization/AssetScriptReferenceIndexer.cs
A	Editor/AssemblyShadow/Serialization/AssetScriptReferenceIndexer.cs.meta
A	Editor/AssemblyShadow/Serialization/BundleImpactAnalyzer.cs
A	Editor/AssemblyShadow/Serialization/BundleImpactAnalyzer.cs.meta
A	Editor/AssemblyShadow/Serialization/ResourceAbiDescriptor.cs
A	Editor/AssemblyShadow/Serialization/ResourceAbiDescriptor.cs.meta
A	Editor/AssemblyShadow/Serialization/ResourceAbiDiff.cs
A	Editor/AssemblyShadow/Serialization/ResourceAbiDiff.cs.meta
A	Editor/AssemblyShadow/Serialization/ResourceAbiHasher.cs
A	Editor/AssemblyShadow/Serialization/ResourceAbiHasher.cs.meta
A	Editor/AssemblyShadow/Serialization/UnitySerializedTypeAnalyzer.cs
A	Editor/AssemblyShadow/Serialization/UnitySerializedTypeAnalyzer.cs.meta
A	Editor/AssemblyShadow/Settings.meta
A	Editor/AssemblyShadow/Settings/AssemblyShadowSettings.asset.template
A	Editor/AssemblyShadow/Settings/AssemblyShadowSettings.asset.template.meta
A	Editor/AssemblyShadow/Settings/AssemblyShadowSettings.cs
A	Editor/AssemblyShadow/Settings/AssemblyShadowSettings.cs.meta
A	Editor/AssemblyShadow/Settings/AssemblyShadowSettingsProvider.cs
A	Editor/AssemblyShadow/Settings/AssemblyShadowSettingsProvider.cs.meta
A	Editor/AssemblyShadow/Settings/AssemblyShadowSettingsUtil.cs
A	Editor/AssemblyShadow/Settings/AssemblyShadowSettingsUtil.cs.meta
A	Editor/AssemblyShadow/Validation.meta
A	Editor/AssemblyShadow/Validation/AssemblyNamePolicy.cs
A	Editor/AssemblyShadow/Validation/AssemblyNamePolicy.cs.meta
A	Editor/AssemblyShadow/Validation/BootstrapIsolationRule.cs
A	Editor/AssemblyShadow/Validation/BootstrapIsolationRule.cs.meta
A	Editor/AssemblyShadow/Validation/ExtensibilityWhitelistRule.cs
A	Editor/AssemblyShadow/Validation/ExtensibilityWhitelistRule.cs.meta
A	Editor/AssemblyShadow/Validation/InternalDependencyRule.cs
A	Editor/AssemblyShadow/Validation/InternalDependencyRule.cs.meta
A	Editor/AssemblyShadow/Validation/ReflectionDependencyScanner.cs
A	Editor/AssemblyShadow/Validation/ReflectionDependencyScanner.cs.meta
A	Editor/AssemblyShadow/Validation/ShadowAssemblyPolicyValidator.cs
A	Editor/AssemblyShadow/Validation/ShadowAssemblyPolicyValidator.cs.meta
M	Editor/HybridCLR.Editor.asmdef
A	Tests.meta
A	Tests/Editor.meta
A	Tests/Editor/AssemblyShadow.meta
A	Tests/Editor/AssemblyShadow/AssemblyIdentityTests.cs
A	Tests/Editor/AssemblyShadow/AssemblyIdentityTests.cs.meta
A	Tests/Editor/AssemblyShadow/CodeGen.meta
A	Tests/Editor/AssemblyShadow/CodeGen/ReflectionAcquisitionCodeGenTests.cs
A	Tests/Editor/AssemblyShadow/CodeGen/ReflectionAcquisitionCodeGenTests.cs.meta
A	Tests/Editor/AssemblyShadow/CodeGen/ReflectionBindingCodeGenTests.cs
A	Tests/Editor/AssemblyShadow/CodeGen/ReflectionBindingCodeGenTests.cs.meta
A	Tests/Editor/AssemblyShadow/CodeGen/Unity.HybridCLR.AssemblyShadow.CodeGen.Tests.asmdef
A	Tests/Editor/AssemblyShadow/CodeGen/Unity.HybridCLR.AssemblyShadow.CodeGen.Tests.asmdef.meta
A	Tests/Editor/AssemblyShadow/GraphAndInputTests.cs
A	Tests/Editor/AssemblyShadow/GraphAndInputTests.cs.meta
A	Tests/Editor/AssemblyShadow/LinkedRuntimeReferenceTests.cs
A	Tests/Editor/AssemblyShadow/LinkedRuntimeReferenceTests.cs.meta
A	Tests/Editor/AssemblyShadow/ManagedAcquisitionPolicyTests.cs
A	Tests/Editor/AssemblyShadow/ManagedAcquisitionPolicyTests.cs.meta
A	Tests/Editor/AssemblyShadow/MetadataTests.cs
A	Tests/Editor/AssemblyShadow/MetadataTests.cs.meta
A	Tests/Editor/AssemblyShadow/PlayerCaptureLifecycleTests.cs
A	Tests/Editor/AssemblyShadow/PlayerCaptureLifecycleTests.cs.meta
A	Tests/Editor/AssemblyShadow/PolicySourceTests.cs
A	Tests/Editor/AssemblyShadow/PolicySourceTests.cs.meta
A	Tests/Editor/AssemblyShadow/PolicyTests.cs
A	Tests/Editor/AssemblyShadow/PolicyTests.cs.meta
A	Tests/Editor/AssemblyShadow/ReflectionBindingEvidenceTests.cs
A	Tests/Editor/AssemblyShadow/ReflectionBindingEvidenceTests.cs.meta
A	Tests/Editor/AssemblyShadow/ResourceAbiTests.cs
A	Tests/Editor/AssemblyShadow/ResourceAbiTests.cs.meta
A	Tests/Editor/AssemblyShadow/ResourceReceiptTests.cs
A	Tests/Editor/AssemblyShadow/ResourceReceiptTests.cs.meta
A	Tests/Editor/AssemblyShadow/SignatureHashTests.cs
A	Tests/Editor/AssemblyShadow/SignatureHashTests.cs.meta
A	Tests/Editor/AssemblyShadow/SnapshotTests.cs
A	Tests/Editor/AssemblyShadow/SnapshotTests.cs.meta
A	Tests/Editor/HybridCLR.AssemblyShadow.Editor.Tests.asmdef
A	Tests/Editor/HybridCLR.AssemblyShadow.Editor.Tests.asmdef.meta
```

### Runtime and native

No M02 source changes. The M01 revisions remain pinned:
`hybridclr` at `1bc69c3acc2434804e71560418df8c728a63360e`,
`il2cpp_plus` at `03a450c73b5c5db2ed6f87dc4f194788fd204567`.
