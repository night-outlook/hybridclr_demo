using System;
using HybridCLR.Editor.AssemblyShadow;

namespace AssemblyShadowDemo.Editor
{
    // Editor wire mirrors: no reference to the fixed Bootstrap assembly.
    [Serializable] public sealed class M06PlayerBuildReceipt
    {
        public int schemaVersion, nativeMetadataVersion, buildOptions;
        public string milestone, variant, baselineBuildId, runtimeAbiHash, unityVersion, target, architecture, buildGuid, playerOutput;
        public string inputSnapshot, inputSnapshotHash, nativeLibraryPath, nativeLibrarySha256, nativeArguments;
        public string placeholderManifestPath, placeholderManifestSha256, nativeMetadataPath, nativeMetadataSha256;
        public string typeProofPath, typeProofSha256, executionProofPath, executionProofSha256, generationProofPath, generationProofSha256;
        public bool developmentBuild;
        public string[] placeholderAssemblyNames, nativeGeneratedAssemblyNames;
        public M04AssemblyIdentity[] assemblyIdentities;
        public M04NativeAssemblyIdentity[] nativeAssemblyIdentities;
        public M06SupplementaryMetadataInput[] supplementaryMetadataInputs;
    }
    [Serializable] public sealed class M06SupplementaryMetadataInput
    { public string assemblyName, path, sha256; public M04AssemblyIdentity identity; }
    [Serializable] public sealed class M06BaselineSelection
    {
        public int schemaVersion = 1;
        public string milestone = "M06", baselineBuildId, baselineManifestPath, baselineManifestSha256, playerInputSnapshot, playerBuildReceiptSha256;
        public string resourceBaselinePath, generationProofPath, generationProofSha256;
        public bool developmentBuild;
    }
    [Serializable] public sealed class M06FixtureManifest
    {
        public int schemaVersion;
        public string milestone, unityVersion, target, architecture, baselineManifestPath, baselineManifestSha256, baselineBuildId, runtimeAbiHash;
        public string baselineInputSnapshot, baselineInputSnapshotHash, stableAotProvenanceHash, stableAotProvenance, generationProofPath, generationProofSha256;
        public bool developmentBuild;
        public string[] candidateNames, closureLoadOrder, stableAotNames;
        public M06Fixture[] fixtures;
        public M06Fixture initializerFailureFixture;
    }
    [Serializable] public sealed class M06Fixture
    {
        public string patchId, compileSnapshot, compileSnapshotHash, patchDirectory, patchManifest, patchManifestSha256;
        public string variant, generationPlanPath, generationPlanSha256;
        public bool developmentBuild;
        public string[] defines, changedRoots, closureLoadOrder, stableAotNames, requiredAotMetadataNames;
        public M04AssemblyIdentity[] assemblyIdentities;
        public M05TypeInventory[] typeInventories;
    }
    [Serializable] public sealed class M06GenerationProof
    {
        public int schemaVersion = 1;
        public string milestone = "M06", policy = "compile-only-generator-provenance:1";
        public string baselineBuildId, unityVersion, target, architecture, baselineCompileSnapshot, baselineCompileSnapshotHash, selectedPlanId;
        public bool developmentBuild;
        public ShadowSourcePins sourcePins;
        public M06GenerationPlanProof[] plans;
        public M06InstalledOutput[] installedOutputs;
    }
    [Serializable] public sealed class M06GenerationPlanProof
    {
        public string planId, compileSnapshot, compileSnapshotHash, planPath, planSha256, planHash;
        public string compilerModePath, compilerModeSha256;
        public string executionPolicyPath, executionPolicySha256, aotInputPath, aotInputSha256, aotInventoryHash;
        public string stripBuildGuid, stripOutput, stripSourceDirectory;
        public int stripBuildOptions;
        public string linkReceiptPath, linkReceiptSha256, bridgeReceiptPath, bridgeReceiptSha256, aotReceiptPath, aotReceiptSha256;
        public string[] defines, changedRoots, closureLoadOrder, requiredAotMetadataNames;
    }
    [Serializable] public sealed class M06InstalledOutput
    { public string role, sourcePath, destinationPath, sha256; }
    [Serializable] public sealed class M06ExecutionPolicyProof
    {
        public int schemaVersion = 1, bootstrapExecutionOrder;
        public string milestone = "M06", compileSnapshotHash, startupScenePath, startupSceneSha256;
        public string bootstrapScriptPath, bootstrapScriptSha256, bootstrapAssemblyIdentity, bootstrapTypeName;
        public string startupSceneSourcePath, bootstrapScriptSourcePath;
        public M06StartupFile[] files;
        public M06StartupScript[] scripts;
        public M06PreloadedAsset[] preloadedAssets;
        public string[] diagnostics;
    }
    [Serializable] public sealed class M06StartupScript
    {
        public string rootAssetPath, assetPath, scriptPath, assemblyIdentity, typeName, phase, assetSha256, scriptSha256;
        public string assetSourcePath, scriptSourcePath;
        public int executionOrder;
        public bool isCandidate, isBootstrapRunner, isCandidateDependent, dependencyProved;
        public string[] callbacks, dependencyEvidence;
    }
    [Serializable] public sealed class M06PreloadedAsset
    { public string assetPath, sourcePath, typeName, assemblyIdentity, sha256; public bool isCandidate; }
    [Serializable] public sealed class M06StartupFile
    { public string sourcePath, path, sha256; }
    [Serializable] public sealed class M06EditorReplayReceipt
    {
        public int schemaVersion = 1;
        public string milestone = "M06", result = "Passed", comparisonPolicy = "compiler-linked-resource-generation-warmup:1";
        public string fixtureManifestPath, fixtureManifestSha256, baselineManifestPath, baselineManifestSha256;
        public string playerBuildReceiptPath, playerBuildReceiptSha256, generationProofPath, generationProofSha256;
        public string baselineInputSnapshotHash, baselineBuildId, playerBuildGuid, nativeLibrarySha256, linkedPlayerReceiptHash, replayScratchPath;
        public bool developmentBuild;
        public ShadowSourcePins validatorSourcePins;
        public M06FixtureReplayEntry[] fixtures;
    }
    [Serializable] public sealed class M06FixtureReplayEntry
    { public string patchId, patchManifestSha256, compileSnapshotHash, generationPlanSha256; public string[] changedRoots, closureLoadOrder; }
}
