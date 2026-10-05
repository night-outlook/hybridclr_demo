using System;
using System.IO;
using System.Linq;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Rebuilds into fresh scratch; original evidence is only read.</summary>
    public static class M06EditorValidation
    {
        public static void Validate()
        {
            string path = AssemblyShadowBuildCommands.Argument("-shadowFixtureManifest", "");
            M06Build.Require(!string.IsNullOrEmpty(path), "Pass -shadowFixtureManifest for M06 replay.");
            Debug.Log("[AssemblyShadow M06] Independent replay: " + ValidateAndWriteReceipt(path, AssemblyShadowBuildCommands.Argument("-shadowValidationReceipt", "")));
        }
        public static string ValidateAndWriteReceipt(string manifestPath, string receiptPath = null)
        {
            manifestPath = Path.GetFullPath(manifestPath);
            receiptPath = Path.GetFullPath(string.IsNullOrEmpty(receiptPath) ? Path.Combine(Path.GetDirectoryName(manifestPath), "m06-editor-replay.json") : receiptPath);
            M06Build.Require(!File.Exists(receiptPath) && !Directory.Exists(receiptPath), "Replay receipt is immutable.");
            string before = ShadowHash.File(manifestPath);
            var manifest = M04JsonEvidence.Read<M06FixtureManifest>(File.ReadAllText(manifestPath));
            M06Build.Require(manifest.schemaVersion == 1 && manifest.milestone == "M06", "M06 fixture schema differs."); M06Build.RequireSafeId(manifest.baselineBuildId);
            M06Build.RequireSet(manifest.candidateNames, M02Build.Candidates, "Candidates");
            M06Build.Require(manifest.closureLoadOrder.SequenceEqual(M06Build.ProviderFirstOrder), "Provider order differs.");
            M06Build.RequireSet(manifest.fixtures.Select(row => row.patchId), new[] { "P01", "P02", "P03" }, "Normal fixture set");
            M06Build.Require(manifest.initializerFailureFixture != null && manifest.initializerFailureFixture.patchId == "InitializerFailure", "Separate real initializer-failure patch is required.");
            M06Build.VerifyHash(manifest.baselineManifestPath, manifest.baselineManifestSha256);
            M06Build.VerifyHash(manifest.generationProofPath, manifest.generationProofSha256);
            var generation = M06GenerationBuild.ReadAndVerify(manifest.generationProofPath);
            M06Build.Require(generation.baselineBuildId == manifest.baselineBuildId && generation.developmentBuild == manifest.developmentBuild &&
                generation.target == manifest.target && generation.architecture == manifest.architecture && generation.unityVersion == manifest.unityVersion, "Fixture/generation context differs.");
            var baseline = JsonUtility.FromJson<ShadowBaselineManifest>(File.ReadAllText(manifest.baselineManifestPath));
            M06Build.Require(baseline != null && baseline.schemaVersion == 1 && baseline.semanticHashSchema == 1 && baseline.baselineBuildId == manifest.baselineBuildId &&
                baseline.runtimeAbiHash == manifest.runtimeAbiHash && baseline.sourcePins.RuntimeAbiHash() == manifest.runtimeAbiHash &&
                baseline.target == manifest.target && baseline.architecture == manifest.architecture && baseline.unityVersion == manifest.unityVersion, "Baseline identity differs.");
            string playerPath = Path.Combine(manifest.baselineInputSnapshot, M06Build.PlayerReceiptName);
            var playerReceipt = ValidatePlayerReceipt(playerPath, manifest.baselineInputSnapshot, true);
            var player = AssemblySnapshot.ReadAndVerify(manifest.baselineInputSnapshot, true);
            M06Build.Require(player.snapshotHash == manifest.baselineInputSnapshotHash && player.snapshotHash == baseline.playerInputSnapshotHash &&
                player.buildGuid == baseline.playerBuildGuid && player.nativeLibrarySha256 == baseline.nativeLibrarySha256 &&
                playerReceipt.developmentBuild == manifest.developmentBuild && playerReceipt.generationProofPath == manifest.generationProofPath &&
                playerReceipt.generationProofSha256 == manifest.generationProofSha256, "Fixture does not bind the actual baseline Player.");
            var frozenPlayer = AssemblySnapshot.ReadAndVerify(ShadowHash.SafeChild(Path.GetDirectoryName(manifest.baselineManifestPath), baseline.playerInputSnapshot), true);
            M06Build.Require(frozenPlayer.snapshotHash == player.snapshotHash && frozenPlayer.linkedPlayerReceiptHash == player.linkedPlayerReceiptHash, "Frozen Player copy differs.");
            var target = (BuildTarget)Enum.Parse(typeof(BuildTarget), manifest.target);
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            var stable = ShadowFixtureProof.DeriveStableAotNames(manifest.baselineInputSnapshot, player, policy, M06Build.StableAotHashDomain);
            M06Build.Require(manifest.stableAotNames.SequenceEqual(stable.names) && manifest.stableAotProvenance == stable.provenance && manifest.stableAotProvenanceHash == stable.provenanceHash, "Stable AOT provenance differs.");
            var frozenResource = ShadowResourceBaseline.ReadAndVerify(ShadowHash.SafeChild(Path.GetDirectoryName(manifest.baselineManifestPath), baseline.resourceBaselinePath), target, manifest.architecture);
            M06Build.Require(frozenResource.Receipt.provenance == ShadowResourceBaseline.M01Provenance && frozenResource.Receipt.compilerSnapshotHash == player.snapshotHash &&
                frozenResource.Receipt.resourceAbiHash == baseline.resourceAbiHash && frozenResource.Receipt.resourceIndexHash == baseline.resourceIndexHash, "M01 resource proof differs.");
            BuildBaselineBundles.VerifyExisting(M01Paths.BaselineRoot(target));
            using (var current = ShadowFixtureProof.Load(manifest.baselineInputSnapshot, player, ShadowFilteredInputPolicy.Apply(policy, player)))
                ShadowResourceBaseline.RequirePlayerAbi(frozenResource, UnitySerializedTypeAnalyzer.Analyze(current, M02Build.Candidates));
            ShadowSourcePins.RequireSameBuildSources(generation.sourcePins, baseline.sourcePins);
            var pins = ShadowSourcePins.Read(AssemblyShadowSettings.Instance.sourcePinFile, target, manifest.architecture);
            ShadowSourcePins.RequireSameBuildSources(pins, baseline.sourcePins);
            string scratch = M06Build.NewRoot("M06Replay-");
            var fixtures = manifest.fixtures.Concat(new[] { manifest.initializerFailureFixture }).ToArray();
            foreach (var fixture in fixtures)
            {
                var row = generation.plans.Single(item => item.planId == fixture.patchId); var plan = M06GenerationBuild.ReadPlan(generation, fixture.patchId);
                M06Build.Require(fixture.developmentBuild == generation.developmentBuild && fixture.variant == (generation.developmentBuild ? "Development" : "ReleaseNoPdb") &&
                    fixture.compileSnapshot == row.compileSnapshot && fixture.compileSnapshotHash == row.compileSnapshotHash &&
                    fixture.generationPlanPath == row.planPath && fixture.generationPlanSha256 == row.planSha256, "Fixture does not use the preserved generation snapshot/mode.");
                M06Build.RequireSet(fixture.defines, M06Build.ExpectedDefines(fixture.patchId), "Fixture defines");
                M06Build.RequireSet(fixture.changedRoots, M06Build.ExpectedChangedRoots(fixture.patchId), "Truthful changed roots");
                M06Build.Require(fixture.stableAotNames.SequenceEqual(stable.names) && fixture.closureLoadOrder.SequenceEqual(plan.LoadOrder) &&
                    fixture.requiredAotMetadataNames.SequenceEqual(row.requiredAotMetadataNames), "Fixture closure/AOT metadata requirements differ.");
                M06Build.Require(fixture.patchManifest == Path.GetFullPath(Path.Combine(fixture.patchDirectory, "patch-manifest.json")), "Patch manifest path differs.");
                M06Build.VerifyHash(fixture.patchManifest, fixture.patchManifestSha256);
                var compiled = AssemblySnapshot.ReadAndVerify(fixture.compileSnapshot, false);
                ShadowCompilerModeEvidence.ReadAndVerify(fixture.compileSnapshot, generation.developmentBuild);
                using (var inputs = ShadowFixtureProof.Load(fixture.compileSnapshot, compiled, policy))
                {
                    var original = ShadowWarmupManifestReader.ReadAndVerify(fixture.patchManifest, inputs);
                    M06Build.Require(original.SchemaVersion == 2, "All M06 normal and failure patches require explicit verified schema-2 warmup.");
                    M06Build.RequirePatchPlan(original.BaseManifest, plan, fixture.patchDirectory, fixture.developmentBuild);
                    string output = Path.Combine(scratch, fixture.patchId);
                    var rebuilt = ShadowPatchManifestBuilder.BuildWithWarmup(M06Build.PatchRequest(manifest.baselineManifestPath, row, output, generation, policy), M06Build.Warmup(inputs, plan.LoadOrder));
                    // Exact byte comparison covers the complete manifest, every
                    // DLL/PDB, resource proof, and compiler/reflection receipts.
                    M05EditorValidation.VerifyArtifactTree(fixture.patchDirectory, output);
                    M06Build.RequirePatchPlan(rebuilt.patch, plan, output, fixture.developmentBuild);
                    var identities = M04AssemblyIdentityProof.ReadPatch(fixture.patchDirectory, original.BaseManifest);
                    M04AssemblyIdentityProof.Verify(fixture.assemblyIdentities, identities);
                    M05TypeInventoryProof.Verify(fixture.typeInventories, M05TypeInventoryProof.ReadIdentities(identities));
                }
            }
            M06Build.Require(ShadowHash.File(manifestPath) == before, "Fixture manifest changed during replay.");
            M04AssemblyIdentityProof.WriteNewJson(receiptPath, new M06EditorReplayReceipt {
                fixtureManifestPath = manifestPath, fixtureManifestSha256 = before, baselineManifestPath = manifest.baselineManifestPath, baselineManifestSha256 = manifest.baselineManifestSha256,
                playerBuildReceiptPath = playerPath, playerBuildReceiptSha256 = ShadowHash.File(playerPath), generationProofPath = manifest.generationProofPath, generationProofSha256 = manifest.generationProofSha256,
                baselineInputSnapshotHash = player.snapshotHash, baselineBuildId = baseline.baselineBuildId, playerBuildGuid = player.buildGuid, nativeLibrarySha256 = player.nativeLibrarySha256,
                linkedPlayerReceiptHash = player.linkedPlayerReceiptHash, replayScratchPath = scratch, developmentBuild = manifest.developmentBuild, validatorSourcePins = pins,
                fixtures = fixtures.Select(row => new M06FixtureReplayEntry { patchId = row.patchId, patchManifestSha256 = row.patchManifestSha256,
                    compileSnapshotHash = row.compileSnapshotHash, generationPlanSha256 = row.generationPlanSha256, changedRoots = row.changedRoots, closureLoadOrder = row.closureLoadOrder }).ToArray() });
            return receiptPath;
        }

        public static M06PlayerBuildReceipt ValidatePlayerReceipt(string path, string root, bool nativeEnabled)
        {
            root = Path.GetFullPath(root); M06Build.Require(path == Path.Combine(root, M06Build.PlayerReceiptName), "M06 Player receipt must be inside its input snapshot.");
            var claimed = M04JsonEvidence.Read<M06PlayerBuildReceipt>(File.ReadAllText(path)); var actual = AssemblySnapshot.ReadAndVerify(root, true);
            M06Build.Require(claimed.schemaVersion == 1 && claimed.milestone == "M06" && claimed.variant == (nativeEnabled ? "NativeOn" : "NativeOff") &&
                claimed.nativeArguments == M06Build.NativeArguments(nativeEnabled), "Player schema/native variant differs."); M06Build.RequireSafeId(claimed.baselineBuildId);
            M06Build.Require(claimed.baselineBuildId == actual.buildId && claimed.runtimeAbiHash == actual.sourcePins.RuntimeAbiHash() && claimed.unityVersion == actual.unityVersion &&
                claimed.target == actual.target && claimed.architecture == actual.architecture && claimed.buildGuid == actual.buildGuid && claimed.playerOutput == actual.playerOutput &&
                claimed.inputSnapshot == root && claimed.inputSnapshotHash == actual.snapshotHash && claimed.nativeLibraryPath == actual.nativeLibraryPath &&
                claimed.nativeLibrarySha256 == actual.nativeLibrarySha256 && claimed.buildOptions == actual.playerBuildOptions &&
                (((BuildOptions)actual.playerBuildOptions & BuildOptions.Development) != 0) == claimed.developmentBuild, "Player receipt does not bind actual build inputs/options.");
            M06Build.VerifyHash(actual.nativeLibraryPath, actual.nativeLibrarySha256);
            M06Build.VerifyHash(claimed.generationProofPath, claimed.generationProofSha256); var generation = M06GenerationBuild.ReadAndVerify(claimed.generationProofPath);
            M06Build.Require(generation.baselineBuildId == claimed.baselineBuildId && generation.developmentBuild == claimed.developmentBuild, "Player generation baseline/mode differs.");
            ShadowSourcePins.RequireSameBuildSources(generation.sourcePins, actual.sourcePins);
            M06Build.RequireBaselineCompilerMatches(generation, root, actual);
            var linked = M04AssemblyIdentityProof.ReadLinked(root, actual); M04AssemblyIdentityProof.Verify(claimed.assemblyIdentities, linked);
            var metadata = M04NativeMetadataProof.ReadPlayer(actual.playerOutput, linked);
            M06Build.Require(claimed.nativeMetadataPath == metadata.path && claimed.nativeMetadataSha256 == metadata.sha256 && claimed.nativeMetadataVersion == metadata.version &&
                claimed.nativeGeneratedAssemblyNames.SequenceEqual(metadata.generatedAssemblyNames), "Native metadata evidence differs.");
            M04NativeMetadataProof.VerifyIdentities(claimed.nativeAssemblyIdentities, metadata.assemblies);
            M06Build.Require(claimed.placeholderManifestPath == Path.Combine(root, M06Build.PlaceholderName), "Placeholder snapshot path differs.");
            M06Build.VerifyHash(claimed.placeholderManifestPath, claimed.placeholderManifestSha256);
            M06Build.Require(M04PlaceholderManifestProof.Parse(File.ReadAllBytes(claimed.placeholderManifestPath)).SequenceEqual(claimed.placeholderAssemblyNames), "Placeholder manifest inventory differs.");
            var expected = M06Build.MetadataInputs(generation, linked);
            M06Build.Require(claimed.supplementaryMetadataInputs.Length == expected.Length, "Supplementary metadata union differs.");
            for (int index = 0; index < expected.Length; ++index)
            {
                var row = claimed.supplementaryMetadataInputs[index]; var reference = expected[index];
                M06Build.Require(row.assemblyName == reference.assemblyName && row.path == reference.path && row.sha256 == reference.sha256, "Supplementary metadata is not the required actual Player DLL.");
                M04AssemblyIdentityProof.Verify(new[] { row.identity }, new[] { reference.identity });
            }
            M06ExecutionSchemaVerifier.VerifyProofs(root, actual, linked, claimed.generationProofPath, claimed.typeProofPath, claimed.typeProofSha256, claimed.executionProofPath, claimed.executionProofSha256);
            return claimed;
        }
    }
}
