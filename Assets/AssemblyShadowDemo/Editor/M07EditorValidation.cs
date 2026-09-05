using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Rebuilds M07 patch policy into fresh scratch and reopens every recorded resource/native byte.</summary>
    public static class M07EditorValidation
    {
        public const string ComparisonPolicy = "compiler-linked-policy-resource-abi-unity-assets:1";

        public static void Validate()
        {
            string path = AssemblyShadowBuildCommands.Argument("-shadowM07Fixtures", "");
            Require(!string.IsNullOrEmpty(path), "Pass -shadowM07Fixtures for M07 replay.");
            string receipt = ValidateAndWriteReceipt(path, AssemblyShadowBuildCommands.Argument("-shadowValidationReceipt", ""));
            Debug.Log("[AssemblyShadow M07] Independent Editor replay passed: " + receipt);
        }

        public static string ValidateAndWriteReceipt(string manifestPath, string receiptPath = null)
        {
            manifestPath = Path.GetFullPath(manifestPath);
            receiptPath = Path.GetFullPath(string.IsNullOrEmpty(receiptPath)
                ? Path.Combine(Path.GetDirectoryName(manifestPath), "m07-editor-replay.json") : receiptPath);
            Require(!File.Exists(receiptPath) && !Directory.Exists(receiptPath), "M07 replay receipt is immutable: " + receiptPath);
            string manifestSha = ShadowHash.File(manifestPath);
            ReplayContext context = Replay(manifestPath);
            Require(ShadowHash.File(manifestPath) == manifestSha, "M07 fixture manifest changed during independent replay.");
            var manifest = context.Manifest;
            var player = context.Player;
            M04AssemblyIdentityProof.WriteNewJson(receiptPath, new ReplayReceipt {
                schemaVersion = 1, milestone = "M07", result = "Passed", comparisonPolicy = ComparisonPolicy,
                fixtureManifestPath = manifestPath, fixtureManifestSha256 = manifestSha,
                baselineManifestPath = manifest.baselineManifestPath, baselineManifestSha256 = manifest.baselineManifestSha256,
                playerBuildReceiptPath = manifest.playerBuildReceiptPath, playerBuildReceiptSha256 = manifest.playerBuildReceiptSha256,
                baselineInputSnapshotHash = manifest.baselineInputSnapshotHash, baselineBuildId = manifest.baselineBuildId,
                playerBuildGuid = player.buildGuid, nativeLibrarySha256 = player.nativeLibrarySha256,
                linkedPlayerReceiptHash = player.linkedPlayerReceiptHash, runtimeAbiHash = manifest.runtimeAbiHash,
                unityVersion = manifest.unityVersion, target = manifest.target, architecture = manifest.architecture,
                stableAotProvenanceHash = manifest.stableAotProvenanceHash,
                resourceBuildReceiptPath = context.ResourceReceiptPath,
                resourceBuildReceiptSha256 = ShadowHash.File(context.ResourceReceiptPath), resourceAbiHash = context.Baseline.resourceAbiHash,
                replayScratchPath = context.Scratch, validatorSourcePins = context.Pins,
                fixtures = manifest.fixtures.Select(row => new FixtureReplayEntry {
                    patchId = row.patchId, patchManifestSha256 = row.patchManifestSha256,
                    compileSnapshotHash = row.compileSnapshotHash, resourceAbiHash = row.resourceAbiHash,
                    dllOnly = row.dllOnly, changedRoots = row.changedRoots, closureLoadOrder = row.closureLoadOrder,
                    resourceBundlesRequired = row.resourceBundlesRequired,
                }).ToArray(),
                rejectedFixtures = manifest.rejectedFixtures.Select(row => new RejectedReplayEntry {
                    patchId = row.patchId, compileSnapshotHash = row.compileSnapshotHash,
                    errorCode = row.errorCode, errorMessage = row.errorMessage,
                }).ToArray(),
            });
            return receiptPath;
        }

        internal static void ValidateManifest(string path)
        {
            Replay(Path.GetFullPath(path));
        }

        private static ReplayContext Replay(string path)
        {
            Require(File.Exists(path), "M07 fixture manifest is missing.");
            M07Build.M07FixtureManifest manifest = JsonUtility.FromJson<M07Build.M07FixtureManifest>(File.ReadAllText(path));
            Require(manifest != null && manifest.schemaVersion == 1 && manifest.milestone == "M07" &&
                manifest.unityVersion == Application.unityVersion && manifest.target == EditorUserBuildSettings.activeBuildTarget.ToString() &&
                manifest.architecture == AssemblyShadowSettings.Instance.architecture, "M07 fixture schema/target differs from this Editor.");
            Require(manifest.candidateNames != null && manifest.candidateNames.SequenceEqual(M07Build.Candidates) &&
                manifest.bundleNames != null && manifest.bundleNames.SequenceEqual(M07Build.BundleNames) && manifest.stableAotNames != null &&
                manifest.stableAotNames.Length > 0 && manifest.stableAotProvenanceHash == ShadowHash.Text(M05Build.StableAotHashDomain + manifest.stableAotProvenance),
                "M07 candidate, stable-AOT, or seven-bundle inventory differs.");
            VerifyHash(manifest.baselineManifestPath, manifest.baselineManifestSha256);
            VerifyHash(manifest.playerBuildReceiptPath, manifest.playerBuildReceiptSha256);
            ShadowBaselineManifest baseline = M07Build.ReadBaseline(manifest.baselineManifestPath);
            Require(baseline.baselineBuildId == manifest.baselineBuildId && baseline.runtimeAbiHash == manifest.runtimeAbiHash &&
                baseline.playerInputSnapshotHash == manifest.baselineInputSnapshotHash && baseline.shadowCandidates.SequenceEqual(M07Build.Candidates) &&
                baseline.bundles.Select(item => item.name).SequenceEqual(M07Build.BundleNames), "M07 baseline identity differs from the fixture manifest.");
            AssemblySnapshotReceipt player = AssemblySnapshot.ReadAndVerify(manifest.baselineInputSnapshot, true);
            Require(player.snapshotHash == manifest.baselineInputSnapshotHash && player.snapshotHash == baseline.playerInputSnapshotHash &&
                player.buildId == baseline.baselineBuildId && player.buildGuid == baseline.playerBuildGuid &&
                player.nativeLibrarySha256 == baseline.nativeLibrarySha256, "M07 successful Player snapshot identity differs.");
            string frozenRoot = ShadowHash.SafeChild(Path.GetDirectoryName(manifest.baselineManifestPath), baseline.playerInputSnapshot);
            AssemblySnapshotReceipt frozen = AssemblySnapshot.ReadAndVerify(frozenRoot, true);
            Require(frozen.snapshotHash == player.snapshotHash && frozen.linkedPlayerReceiptHash == player.linkedPlayerReceiptHash,
                "M07 frozen Player proof differs from the successful build snapshot.");

            var pins = ShadowSourcePins.Read(AssemblyShadowSettings.Instance.sourcePinFile,
                EditorUserBuildSettings.activeBuildTarget, AssemblyShadowSettings.Instance.architecture);
            ShadowSourcePins.RequireSameBuildSources(pins, baseline.sourcePins);
            ShadowSourcePins.RequireSameBuildSources(player.sourcePins, baseline.sourcePins);
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(EditorUserBuildSettings.activeBuildTarget);
            var stable = M05Build.DeriveStableAotNames(manifest.baselineInputSnapshot, player, policy);
            Require(manifest.stableAotNames.SequenceEqual(stable.names) && manifest.stableAotProvenance == stable.provenance &&
                manifest.stableAotProvenanceHash == stable.provenanceHash, "M07 stable-AOT authorization is not derived from the linked Player.");
            string resourceRoot = ShadowHash.SafeChild(Path.GetDirectoryName(manifest.baselineManifestPath), baseline.resourceBaselinePath);
            VerifiedShadowResourceBaseline resources = ShadowResourceBaseline.ReadAndVerify(resourceRoot,
                EditorUserBuildSettings.activeBuildTarget, manifest.architecture);
            string resourceReceiptPath = Path.Combine(resourceRoot, ShadowResourceBaseline.ReceiptName);
            Require(ShadowHash.File(resourceReceiptPath) == baseline.resourceBuildReceiptHash && resources.Receipt.resourceAbiHash == baseline.resourceAbiHash &&
                resources.Receipt.resourceIndexHash == baseline.resourceIndexHash && resources.Receipt.bundles.Select(item => item.name).SequenceEqual(M07Build.BundleNames),
                "M07 baseline resource receipt differs from the baseline manifest.");
            ValidatePlayerReceipt(manifest.playerBuildReceiptPath, manifest, player, true, resourceReceiptPath, resources);

            Require(manifest.fixtures != null && manifest.fixtures.Select(item => item.patchId).OrderBy(value => value, StringComparer.Ordinal)
                .SequenceEqual(new[] { "P01", "P02", "P03", "P04", "P05" }), "M07 fixture set must contain P01-P05 exactly.");
            Require(manifest.rejectedFixtures != null && manifest.rejectedFixtures.Select(item => item.patchId).OrderBy(value => value, StringComparer.Ordinal)
                .SequenceEqual(new[] { "P05-DllOnly", "P14-ClassRename", "P15-SerializeReferenceRename" }), "M07 rejected fixture set differs.");
            string scratch = Path.GetFullPath("_temp/AssemblyShadow/M07Replay-" + Guid.NewGuid().ToString("N"));
            Require(!Directory.Exists(scratch) && !File.Exists(scratch), "M07 replay scratch must be new.");
            Directory.CreateDirectory(scratch);
            foreach (M07Build.M07Fixture fixture in manifest.fixtures)
                ReplayFixture(fixture, manifest, baseline, scratch, pins, policy);
            foreach (M07Build.M07RejectedFixture rejected in manifest.rejectedFixtures)
                ReplayRejected(rejected, manifest, scratch, pins, policy);
            return new ReplayContext { Manifest = manifest, Baseline = baseline, Player = player, Pins = pins,
                Scratch = scratch, ResourceReceiptPath = resourceReceiptPath };
        }

        private static void ValidatePlayerReceipt(string path, M07Build.M07FixtureManifest manifest, AssemblySnapshotReceipt actual, bool nativeEnabled,
            string baselineResourceReceiptPath, VerifiedShadowResourceBaseline baselineResources)
        {
            M07Build.M07PlayerBuildReceipt claimed = JsonUtility.FromJson<M07Build.M07PlayerBuildReceipt>(File.ReadAllText(path));
            string root = Path.GetFullPath(manifest.baselineInputSnapshot);
            Require(path == Path.Combine(root, "m07-player-build.json") && claimed != null && claimed.schemaVersion == 1 && claimed.milestone == "M07" &&
                claimed.variant == (nativeEnabled ? "NativeOn" : "NativeOff") && claimed.nativeArguments ==
                "--compiler-flags=\"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=" + (nativeEnabled ? "1" : "0") + "\"", "M07 Player receipt schema/path/native variant differs.");
            Require(claimed.baselineBuildId == actual.buildId && claimed.runtimeAbiHash == actual.sourcePins.RuntimeAbiHash() &&
                claimed.unityVersion == actual.unityVersion && claimed.target == actual.target && claimed.architecture == actual.architecture &&
                claimed.buildGuid == actual.buildGuid && claimed.playerOutput == actual.playerOutput && claimed.inputSnapshot == root &&
                claimed.inputSnapshotHash == actual.snapshotHash && claimed.nativeLibraryPath == actual.nativeLibraryPath &&
                claimed.nativeLibrarySha256 == actual.nativeLibrarySha256, "M07 Player receipt does not bind the actual build snapshot.");
            VerifyHash(claimed.nativeLibraryPath, claimed.nativeLibrarySha256);
            M04AssemblyIdentity[] linked = M04AssemblyIdentityProof.ReadLinked(root, actual);
            M04AssemblyIdentityProof.Verify(claimed.assemblyIdentities, linked);
            M04NativeMetadataProof.Capture metadata = M04NativeMetadataProof.ReadPlayer(actual.playerOutput, linked);
            Require(claimed.nativeMetadataPath == metadata.path && claimed.nativeMetadataSha256 == metadata.sha256 &&
                claimed.nativeMetadataVersion == metadata.version && claimed.nativeGeneratedAssemblyNames.SequenceEqual(metadata.generatedAssemblyNames),
                "M07 native metadata evidence differs from the executed Player.");
            M04NativeMetadataProof.VerifyIdentities(claimed.nativeAssemblyIdentities, metadata.assemblies);
            Require(claimed.placeholderManifestPath == Path.Combine(root, "m07-placeholder-AssemblyManifest.cpp"), "M07 placeholder snapshot path differs.");
            VerifyHash(claimed.placeholderManifestPath, claimed.placeholderManifestSha256);
            Require(M04PlaceholderManifestProof.Parse(File.ReadAllBytes(claimed.placeholderManifestPath)).SequenceEqual(claimed.placeholderAssemblyNames),
                "M07 placeholder name inventory differs from the captured generated source.");
            string claimedResourceRoot = Path.GetFullPath(claimed.resourceBaselinePath);
            string claimedResourceReceipt = ShadowHash.SafeChild(claimedResourceRoot, ShadowResourceBaseline.ReceiptName);
            Require(Path.GetFullPath(claimed.resourceBuildReceiptPath) == claimedResourceReceipt &&
                claimed.resourceAbiHash == manifest.fixtures[0].baselineResourceAbiHash && claimed.bundleNames.SequenceEqual(M07Build.BundleNames) &&
                claimed.resourceBuildReceiptSha256 == ShadowHash.File(claimedResourceReceipt) &&
                claimed.resourceBuildReceiptSha256 == ShadowHash.File(baselineResourceReceiptPath), "M07 Player resource receipt binding differs.");
            VerifiedShadowResourceBaseline claimedResources = ShadowResourceBaseline.ReadAndVerify(claimedResourceRoot,
                EditorUserBuildSettings.activeBuildTarget, manifest.architecture);
            Require(claimedResources.Receipt.resourceAbiHash == baselineResources.Receipt.resourceAbiHash &&
                claimedResources.Receipt.bundles.Select(item => item.name + ":" + item.sha256)
                    .SequenceEqual(baselineResources.Receipt.bundles.Select(item => item.name + ":" + item.sha256)),
                "M07 original and baseline-copied resource bytes differ.");
        }

        private static void ReplayFixture(M07Build.M07Fixture fixture, M07Build.M07FixtureManifest manifest, ShadowBaselineManifest baseline,
            string scratch, ShadowSourcePins pins, ShadowPolicyConfiguration policy)
        {
            Require(fixture != null, "M07 fixture is null.");
            string[] expectedDefines; string[] expectedRoots; bool expectedDllOnly;
            ExpectedFixture(fixture.patchId, out expectedDefines, out expectedRoots, out expectedDllOnly);
            RequireSet(fixture.defines, expectedDefines, fixture.patchId + " defines");
            RequireSet(fixture.changedRoots, expectedRoots, fixture.patchId + " changed roots");
            Require(fixture.dllOnly == expectedDllOnly && Path.GetFullPath(fixture.patchManifest) ==
                Path.Combine(Path.GetFullPath(fixture.patchDirectory), "patch-manifest.json"), "M07 fixture policy/path differs: " + fixture.patchId);
            VerifyHash(fixture.patchManifest, fixture.patchManifestSha256);
            AssemblySnapshotReceipt compiled = AssemblySnapshot.ReadAndVerify(fixture.compileSnapshot, false);
            Require(compiled.snapshotHash == fixture.compileSnapshotHash, "M07 compiler snapshot changed: " + fixture.patchId);
            RequireSet(ShadowReflectionBindingEvidence.UserDefines(compiled.extraScriptingDefines), expectedDefines, fixture.patchId + " captured defines");
            ShadowSourcePins.RequireSameBuildSources(compiled.sourcePins, baseline.sourcePins);
            M07Build.M07Fixture rebuilt = M07Build.BuildFixtureFromSnapshot(scratch, fixture.patchId, fixture.defines, fixture.changedRoots,
                fixture.dllOnly, EditorUserBuildSettings.activeBuildTarget, manifest.architecture, pins, policy, manifest.baselineManifestPath, fixture.compileSnapshot);
            M05EditorValidation.VerifyArtifactTree(fixture.patchDirectory, rebuilt.patchDirectory);
            Require(rebuilt.patchManifestSha256 == fixture.patchManifestSha256 && rebuilt.compileSnapshotHash == fixture.compileSnapshotHash &&
                rebuilt.resourceAbiHash == fixture.resourceAbiHash && rebuilt.baselineResourceAbiHash == fixture.baselineResourceAbiHash &&
                rebuilt.resourceChangeLevel == fixture.resourceChangeLevel && rebuilt.dllOnly == fixture.dllOnly &&
                rebuilt.closureLoadOrder.SequenceEqual(fixture.closureLoadOrder) && rebuilt.resourceBundlesRequired.SequenceEqual(fixture.resourceBundlesRequired),
                "M07 rebuilt patch policy differs: " + fixture.patchId);
            ShadowPatchManifest patch = JsonUtility.FromJson<ShadowPatchManifest>(File.ReadAllText(fixture.patchManifest));
            M04AssemblyIdentityProof.Verify(fixture.assemblyIdentities, M04AssemblyIdentityProof.ReadPatch(fixture.patchDirectory, patch));
            if (fixture.patchId == "P05")
            {
                Require(!fixture.dllOnly && fixture.resourceChangeLevel == ResourceAbiDiffLevel.ResourceRebuildRequired.ToString() &&
                    fixture.resourceBundlesRequired.Length > 0 && fixture.replacementBundleNames.SequenceEqual(M07Build.BundleNames),
                    "M07 P05 lacks an atomic structural resource replacement.");
                VerifyHash(fixture.replacementResourceReceiptPath, fixture.replacementResourceReceiptSha256);
                VerifiedShadowResourceBaseline replacement = ShadowResourceBaseline.ReadAndVerify(fixture.replacementResourcePath,
                    EditorUserBuildSettings.activeBuildTarget, manifest.architecture);
                Require(replacement.Receipt.resourceAbiHash == fixture.resourceAbiHash &&
                    fixture.resourceBundlesRequired.All(name => fixture.replacementBundleNames.Contains(name, StringComparer.Ordinal)),
                    "M07 P05 resource ABI or required bundles differ from its replacement catalog.");
            }
            else Require(fixture.dllOnly && fixture.resourceChangeLevel == ResourceAbiDiffLevel.CodeOnly.ToString() &&
                fixture.resourceAbiHash == fixture.baselineResourceAbiHash && fixture.resourceBundlesRequired.Length == 0 &&
                string.IsNullOrEmpty(fixture.replacementResourcePath), "M07 compatible patch unexpectedly requires resources: " + fixture.patchId);
        }

        private static void ReplayRejected(M07Build.M07RejectedFixture rejected, M07Build.M07FixtureManifest manifest,
            string scratch, ShadowSourcePins pins, ShadowPolicyConfiguration policy)
        {
            Require(rejected != null && rejected.errorCode == "ResourceRebuildRequired" && !string.IsNullOrEmpty(rejected.errorMessage),
                "M07 rejected fixture lacks a real structural error.");
            string[] defines; string[] roots; RejectedFixturePolicy(rejected.patchId, out defines, out roots);
            RequireSet(rejected.defines, defines, rejected.patchId + " defines");
            RequireSet(rejected.changedRoots, roots, rejected.patchId + " changed roots");
            AssemblySnapshotReceipt compiled = AssemblySnapshot.ReadAndVerify(rejected.compileSnapshot, false);
            Require(compiled.snapshotHash == rejected.compileSnapshotHash, "M07 rejected compiler snapshot changed: " + rejected.patchId);
            RequireSet(ShadowReflectionBindingEvidence.UserDefines(compiled.extraScriptingDefines), defines, rejected.patchId + " captured defines");
            string output = Path.Combine(scratch, rejected.patchId + "-must-not-exist");
            ShadowBuildException observed = null;
            try
            {
                ShadowPatchManifestBuilder.Build(new ShadowPatchBuildRequest {
                    baselineManifestPath = manifest.baselineManifestPath, currentCompileSnapshot = rejected.compileSnapshot,
                    outputDirectory = output, patchId = rejected.patchId, target = EditorUserBuildSettings.activeBuildTarget,
                    architecture = manifest.architecture, sourcePins = pins, policy = policy,
                    explicitChangedRoots = rejected.changedRoots, dllOnly = true, includePdb = true,
                });
            }
            catch (ShadowBuildException error) { observed = error; }
            Require(observed != null && observed.Code == rejected.errorCode && observed.Message == rejected.errorMessage &&
                !Directory.Exists(output) && !File.Exists(output), "M07 structural rejection replay differs: " + rejected.patchId);
        }

        private static void ExpectedFixture(string patchId, out string[] defines, out string[] roots, out bool dllOnly)
        {
            dllOnly = patchId != "P05";
            if (patchId == "P01") { defines = new[] { M07Build.P01Define }; roots = new[] { "AssemblyA.Implementation.Internal" }; }
            else if (patchId == "P02") { defines = new[] { M07Build.P02Define }; roots = new[] { "AssemblyA.Implementation.Extensibility" }; }
            else if (patchId == "P03") { defines = new[] { M07Build.P01Define, M07Build.P03Define }; roots = M07Build.Candidates; }
            else if (patchId == "P04") { defines = new[] { M07Build.P01Define, M07Build.P04Define }; roots = new[] { "AssemblyA.Implementation.Internal" }; }
            else if (patchId == "P05") { defines = new[] { M07Build.P05Define }; roots = new[] { "AssemblyA.Implementation.Internal" }; }
            else throw new BuildFailedException("Unknown M07 fixture: " + patchId);
        }

        private static void RejectedFixturePolicy(string patchId, out string[] defines, out string[] roots)
        {
            roots = new[] { "AssemblyA.Implementation.Internal" };
            if (patchId == "P05-DllOnly") defines = new[] { M07Build.P01Define, M07Build.P05Define };
            else if (patchId == "P14-ClassRename") defines = new[] { M07Build.P01Define, M07Build.P14Define };
            else if (patchId == "P15-SerializeReferenceRename") defines = new[] { M07Build.P01Define, M07Build.P15Define };
            else throw new BuildFailedException("Unknown M07 rejected fixture: " + patchId);
        }

        private static void RequireSet(IEnumerable<string> actual, IEnumerable<string> expected, string label)
        {
            string[] a = actual == null ? new string[0] : actual.ToArray();
            string[] b = expected == null ? new string[0] : expected.ToArray();
            Require(a.Distinct(StringComparer.Ordinal).Count() == a.Length && b.Distinct(StringComparer.Ordinal).Count() == b.Length &&
                new HashSet<string>(a, StringComparer.Ordinal).SetEquals(b), "M07 " + label + " differs.");
        }

        private static void VerifyHash(string path, string hash)
        {
            Require(Path.IsPathRooted(path) && File.Exists(path) && !string.IsNullOrEmpty(hash) && ShadowHash.File(path) == hash,
                "M07 artifact hash differs: " + path);
        }

        private static void Require(bool value, string message)
        {
            if (!value) throw new BuildFailedException(message);
        }

        private sealed class ReplayContext
        {
            public M07Build.M07FixtureManifest Manifest;
            public ShadowBaselineManifest Baseline;
            public AssemblySnapshotReceipt Player;
            public ShadowSourcePins Pins;
            public string Scratch, ResourceReceiptPath;
        }

        [Serializable] public sealed class ReplayReceipt
        {
            public int schemaVersion;
            public string milestone, result, comparisonPolicy;
            public string fixtureManifestPath, fixtureManifestSha256, baselineManifestPath, baselineManifestSha256;
            public string playerBuildReceiptPath, playerBuildReceiptSha256, baselineInputSnapshotHash, baselineBuildId;
            public string playerBuildGuid, nativeLibrarySha256, linkedPlayerReceiptHash, runtimeAbiHash, unityVersion, target, architecture;
            public string stableAotProvenanceHash, resourceBuildReceiptPath, resourceBuildReceiptSha256, resourceAbiHash, replayScratchPath;
            public ShadowSourcePins validatorSourcePins;
            public FixtureReplayEntry[] fixtures;
            public RejectedReplayEntry[] rejectedFixtures;
        }
        [Serializable] public sealed class FixtureReplayEntry
        {
            public string patchId, patchManifestSha256, compileSnapshotHash, resourceAbiHash;
            public bool dllOnly;
            public string[] changedRoots, closureLoadOrder, resourceBundlesRequired;
        }
        [Serializable] public sealed class RejectedReplayEntry
        {
            public string patchId, compileSnapshotHash, errorCode, errorMessage;
        }
    }
}
