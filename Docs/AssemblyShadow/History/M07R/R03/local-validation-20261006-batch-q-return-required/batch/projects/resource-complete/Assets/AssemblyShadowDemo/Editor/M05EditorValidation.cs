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
    /// <summary>Replays from immutable bytes into fresh M05-only scratch; never repairs recorded evidence.</summary>
    public static class M05EditorValidation
    {
        public const string ComparisonPolicy = "compiler-linked-policy-resource-type-world:1";

        public static void Validate()
        {
            string path = AssemblyShadowBuildCommands.Argument("-shadowFixtureManifest", "");
            Require(!string.IsNullOrEmpty(path), "Pass -shadowFixtureManifest for M05 replay.");
            Debug.Log("[AssemblyShadow M05] Independent Editor replay: " + ValidateAndWriteReceipt(path,
                AssemblyShadowBuildCommands.Argument("-shadowValidationReceipt", "")));
        }

        public static string ValidateAndWriteReceipt(string manifestPath, string receiptPath = null)
        {
            manifestPath = Path.GetFullPath(manifestPath);
            receiptPath = Path.GetFullPath(string.IsNullOrEmpty(receiptPath) ? Path.Combine(Path.GetDirectoryName(manifestPath), "m05-editor-replay.json") : receiptPath);
            Require(!File.Exists(receiptPath) && !Directory.Exists(receiptPath), "M05 replay receipt already exists: " + receiptPath);
            string before = ShadowHash.File(manifestPath);
            var context = Replay(manifestPath);
            Require(ShadowHash.File(manifestPath) == before, "Fixture manifest changed during replay.");
            var manifest = context.Manifest; var player = context.Player;
            var pins = ShadowSourcePins.Read(AssemblyShadowSettings.Instance.sourcePinFile,
                EditorUserBuildSettings.activeBuildTarget, AssemblyShadowSettings.Instance.architecture);
            ShadowSourcePins.RequireSameBuildSources(pins, context.Baseline.sourcePins);
            Require(Application.unityVersion == manifest.unityVersion, "Replay Editor version differs from captured Player.");
            string playerReceipt = Path.Combine(manifest.baselineInputSnapshot, "m05-player-build.json");
            var receipt = new FixtureReplayReceipt {
                schemaVersion = 1, milestone = "M05", result = "Passed", comparisonPolicy = ComparisonPolicy,
                fixtureManifestPath = manifestPath, fixtureManifestSha256 = before,
                baselineManifestPath = manifest.baselineManifestPath, baselineManifestSha256 = manifest.baselineManifestSha256,
                playerBuildReceiptPath = playerReceipt, playerBuildReceiptSha256 = ShadowHash.File(playerReceipt),
                baselineInputSnapshotHash = player.snapshotHash, baselineBuildId = manifest.baselineBuildId,
                playerBuildGuid = player.buildGuid, nativeLibrarySha256 = player.nativeLibrarySha256,
                linkedPlayerReceiptHash = player.linkedPlayerReceiptHash, runtimeAbiHash = manifest.runtimeAbiHash,
                unityVersion = manifest.unityVersion, target = manifest.target, architecture = manifest.architecture,
                stableAotProvenanceHash = manifest.stableAotProvenanceHash, validatorSourcePins = pins,
                typeProofPath = context.PlayerReceipt.typeProofPath, typeProofSha256 = context.PlayerReceipt.typeProofSha256,
                replayScratchPath = context.Scratch,
                fixtures = manifest.fixtures.Select(fixture => new FixtureReplayEntry {
                    patchId = fixture.patchId, patchManifestSha256 = fixture.patchManifestSha256,
                    compileSnapshotHash = fixture.compileSnapshotHash, changedRoots = fixture.changedRoots, closureLoadOrder = fixture.closureLoadOrder,
                }).ToArray(),
                rejectedFixtures = manifest.rejectedFixtures.Select(fixture => new RejectedReplayEntry {
                    fixtureId = fixture.fixtureId, compileSnapshotHash = fixture.compileSnapshotHash, dllSha256 = fixture.dllSha256,
                    errorCode = fixture.errorCode, errorMessage = fixture.errorMessage,
                }).ToArray(),
            };
            M04AssemblyIdentityProof.WriteNewJson(receiptPath, receipt);
            return receiptPath;
        }

        public static void ValidateFixtures(string manifestPath) { Replay(Path.GetFullPath(manifestPath)); }

        private static ReplayContext Replay(string manifestPath)
        {
            Require(File.Exists(manifestPath), "M05 fixture manifest missing.");
            var manifest = M04JsonEvidence.Read<M05Build.M05FixtureManifest>(File.ReadAllText(manifestPath));
            Require(manifest.schemaVersion == 1 && manifest.milestone == "M05" && manifest.baselineBuildId.StartsWith("M05-Baseline-", StringComparison.Ordinal), "M05 manifest identity mismatch.");
            Require(manifest.candidateNames.SequenceEqual(M02Build.Candidates) && manifest.closureLoadOrder.SequenceEqual(M05Build.ProviderFirstOrder), "M05 candidate/provider order changed.");
            RequireSet(manifest.fixtures.Select(fixture => fixture.patchId), new[] { "P01", "P03" }, "Normal fixture set");
            Require(manifest.rejectedFixtures.Length == 1 && manifest.rejectedFixtures[0].fixtureId == M05Build.RejectedFixtureId, "Exactly one separate LayoutMismatch rejection is required.");
            VerifyHash(manifest.baselineManifestPath, manifest.baselineManifestSha256);
            var baseline = JsonUtility.FromJson<ShadowBaselineManifest>(File.ReadAllText(manifest.baselineManifestPath));
            Require(baseline != null && baseline.schemaVersion == 1 && baseline.semanticHashSchema == 1 &&
                baseline.baselineBuildId == manifest.baselineBuildId && baseline.runtimeAbiHash == manifest.runtimeAbiHash &&
                baseline.sourcePins.RuntimeAbiHash() == manifest.runtimeAbiHash && baseline.unityVersion == manifest.unityVersion &&
                baseline.target == manifest.target && baseline.architecture == manifest.architecture, "Baseline identity/ABI differs.");
            RequireSet(baseline.shadowCandidates, manifest.candidateNames, "Baseline candidates");
            var player = AssemblySnapshot.ReadAndVerify(manifest.baselineInputSnapshot, true);
            var playerReceipt = ValidatePlayerReceipt(Path.Combine(manifest.baselineInputSnapshot, "m05-player-build.json"), manifest.baselineInputSnapshot, true);
            Require(player.snapshotHash == manifest.baselineInputSnapshotHash && player.snapshotHash == baseline.playerInputSnapshotHash &&
                player.buildId == baseline.baselineBuildId && player.buildGuid == baseline.playerBuildGuid && player.nativeLibrarySha256 == baseline.nativeLibrarySha256,
                "Baseline does not bind the actual captured Player.");
            ShadowSourcePins.RequireSameBuildSources(player.sourcePins, baseline.sourcePins);
            string frozenRoot = ShadowHash.SafeChild(Path.GetDirectoryName(manifest.baselineManifestPath), baseline.playerInputSnapshot);
            var frozen = AssemblySnapshot.ReadAndVerify(frozenRoot, true);
            Require(frozen.snapshotHash == player.snapshotHash && frozen.linkedPlayerReceiptHash == player.linkedPlayerReceiptHash, "Frozen Player proof differs.");
            BuildTarget target;
            Require(Enum.TryParse(manifest.target, out target), "Unknown build target.");
            VerifyFrozenResources(manifest, baseline, player, target);
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            var stable = ShadowFixtureProof.DeriveStableAotNames(manifest.baselineInputSnapshot, player, policy, M05Build.StableAotHashDomain);
            Require(manifest.stableAotNames.SequenceEqual(stable.names) && manifest.stableAotProvenance == stable.provenance &&
                manifest.stableAotProvenanceHash == stable.provenanceHash, "Stable AOT authorization does not derive from actual compiler/linker evidence.");
            var baselinePolicy = ShadowFilteredInputPolicy.Apply(policy, player);
            using (var set = ShadowFixtureProof.Load(manifest.baselineInputSnapshot, player, baselinePolicy))
            {
                ShadowReflectionBindingEvidence.AddCompiledDependencies(baselinePolicy, set.Assemblies.Values);
                var references = VerifiedLinkedRuntimeReferences.Verify(manifest.baselineInputSnapshot, player, set, baselinePolicy);
                ShadowReflectionBindingEvidence.ValidateCompiled(set, baselinePolicy, manifest.baselineInputSnapshot, player, true, references).ThrowIfInvalid();
                Require(ShadowFixtureProof.BootstrapHash(set.Assemblies.Values) == baseline.bootstrapAbiHash, "Fixed Bootstrap semantic proof differs.");
            }
            string scratch = Path.GetFullPath("_temp/AssemblyShadow/M05Replay-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(scratch);
            foreach (var fixture in manifest.fixtures)
            {
                Require(fixture.patchManifest == Path.GetFullPath(Path.Combine(fixture.patchDirectory, "patch-manifest.json")), "Patch manifest must be inside its immutable fixture directory.");
                VerifyHash(fixture.patchManifest, fixture.patchManifestSha256);
                var compiled = VerifyCompile(fixture.compileSnapshot, fixture.compileSnapshotHash, fixture.defines, baseline);
                RequireSet(fixture.defines, M05Build.ExpectedDefines(fixture.patchId), "Exact normal compiler defines");
                RequireSet(fixture.changedRoots, M05Build.ExpectedChangedRoots(fixture.patchId), "Truthful changed roots");
                Require(fixture.stableAotNames.SequenceEqual(stable.names), "Fixture stable AOT names differ.");
                string output = Path.Combine(scratch, fixture.patchId);
                var replayed = ShadowPatchManifestBuilder.Build(Request(manifest, fixture.compileSnapshot, output, fixture.patchId, fixture.changedRoots, target, compiled.sourcePins, policy));
                // This reruns the complete canonical policy, reference graph, closure, Bootstrap and resource ABI builder.
                // No timestamp/path/unknown-field exclusions can turn different artifacts into equivalent evidence.
                VerifyArtifactTree(fixture.patchDirectory, output);
                Require(replayed.loadOrder.SequenceEqual(fixture.closureLoadOrder), "Provider-first load order differs from replay.");
                RequireSet(replayed.closure.Select(item => item.name), fixture.patchId == "P01" ? new[] { "AssemblyA.Implementation.Internal" } : manifest.candidateNames, "Mode-specific closure");
                var identities = M04AssemblyIdentityProof.ReadPatch(fixture.patchDirectory, replayed);
                M04AssemblyIdentityProof.Verify(fixture.assemblyIdentities, identities);
                M05TypeInventoryProof.Verify(fixture.typeInventories, M05TypeInventoryProof.ReadIdentities(identities));
                Require(AssemblySnapshot.ReadAndVerify(fixture.compileSnapshot, false).snapshotHash == compiled.snapshotHash, "Compiler snapshot changed during replay.");
            }
            VerifyRejected(manifest, baseline, target, policy, scratch);
            return new ReplayContext { Manifest = manifest, Baseline = baseline, Player = player, PlayerReceipt = playerReceipt, Scratch = scratch };
        }

        public static M05Build.M05PlayerBuildReceipt ValidatePlayerReceipt(string path, string root, bool nativeEnabled)
        {
            root = Path.GetFullPath(root);
            Require(path == Path.Combine(root, "m05-player-build.json"), "M05 Player receipt must be inside its captured input snapshot.");
            var claimed = M04JsonEvidence.Read<M05Build.M05PlayerBuildReceipt>(File.ReadAllText(path));
            var actual = AssemblySnapshot.ReadAndVerify(root, true);
            Require(claimed.schemaVersion == 1 && claimed.milestone == "M05" && claimed.variant == (nativeEnabled ? "NativeOn" : "NativeOff") &&
                claimed.baselineBuildId.StartsWith("M05-Baseline-", StringComparison.Ordinal) &&
                claimed.nativeArguments == "--compiler-flags=\"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=" + (nativeEnabled ? "1" : "0") + "\"", "M05 Player variant/schema differs.");
            Require(claimed.baselineBuildId == actual.buildId && claimed.runtimeAbiHash == actual.sourcePins.RuntimeAbiHash() &&
                claimed.unityVersion == actual.unityVersion && claimed.target == actual.target && claimed.architecture == actual.architecture &&
                claimed.buildGuid == actual.buildGuid && claimed.playerOutput == actual.playerOutput && claimed.inputSnapshot == root &&
                claimed.inputSnapshotHash == actual.snapshotHash && claimed.nativeLibraryPath == actual.nativeLibraryPath && claimed.nativeLibrarySha256 == actual.nativeLibrarySha256,
                "Player receipt does not bind actual input/native/build identity.");
            VerifyHash(actual.nativeLibraryPath, actual.nativeLibrarySha256);
            var linked = M04AssemblyIdentityProof.ReadLinked(root, actual);
            M04AssemblyIdentityProof.Verify(claimed.assemblyIdentities, linked);
            var metadata = M04NativeMetadataProof.ReadPlayer(actual.playerOutput, linked);
            Require(claimed.nativeMetadataPath == metadata.path && claimed.nativeMetadataSha256 == metadata.sha256 &&
                claimed.nativeMetadataVersion == metadata.version && claimed.nativeGeneratedAssemblyNames.SequenceEqual(metadata.generatedAssemblyNames), "Native metadata evidence differs.");
            M04NativeMetadataProof.VerifyIdentities(claimed.nativeAssemblyIdentities, metadata.assemblies);
            string placeholder = Path.Combine(root, M05Build.PlaceholderName);
            Require(claimed.placeholderManifestPath == placeholder, "Placeholder manifest must be the M05 snapshot copy.");
            VerifyHash(placeholder, claimed.placeholderManifestSha256);
            Require(M04PlaceholderManifestProof.Parse(File.ReadAllBytes(placeholder)).SequenceEqual(claimed.placeholderAssemblyNames), "Placeholder name evidence differs.");
            M05TypeSchemaVerifier.Verify(root, actual, claimed, linked);
            return claimed;
        }

        private static void VerifyRejected(M05Build.M05FixtureManifest manifest, ShadowBaselineManifest baseline, BuildTarget target, ShadowPolicyConfiguration policy, string scratch)
        {
            var rejected = manifest.rejectedFixtures[0];
            var receipt = VerifyCompile(rejected.compileSnapshot, rejected.compileSnapshotHash, rejected.defines, baseline);
            RequireSet(rejected.defines, M05Build.ExpectedDefines("P01").Concat(new[] { M05Build.LayoutDefine }), "Exact rejected defines");
            RequireSet(rejected.changedRoots, M05Build.ExpectedChangedRoots("P01"), "Rejected changed roots");
            var file = receipt.assemblies.Single(item => item.name == "AssemblyA.Implementation.Internal");
            Require(rejected.dllPath == ShadowHash.SafeChild(rejected.compileSnapshot, file.path) && rejected.dllSha256 == file.sha256, "Rejected DLL is not the actual captured compiler output.");
            var identity = M04AssemblyIdentityProof.ReadFile(rejected.dllPath, file.sha256, file.name);
            M04AssemblyIdentityProof.Verify(new[] { rejected.assemblyIdentity }, new[] { identity });
            M05TypeInventoryProof.Verify(new[] { rejected.typeInventory }, new[] { M05TypeInventoryProof.ReadFile(rejected.dllPath, file.sha256, file.name) });
            string output = Path.Combine(scratch, M05Build.RejectedFixtureId + "-must-not-be-admitted");
            var error = M05Build.RequireLayoutRejection(() => ShadowPatchManifestBuilder.Build(Request(manifest,
                rejected.compileSnapshot, output, rejected.fixtureId, rejected.changedRoots, target, receipt.sourcePins, policy)), output);
            Require(rejected.errorCode == error.Code && rejected.errorMessage == error.Message, "Actual resource ABI rejection differs from recorded evidence.");
        }

        private static AssemblySnapshotReceipt VerifyCompile(string root, string hash, string[] defines, ShadowBaselineManifest baseline)
        {
            Require(Path.IsPathRooted(root), "Compiler snapshot path must be absolute.");
            var receipt = AssemblySnapshot.ReadAndVerify(root, false);
            Require(receipt.snapshotHash == hash, "Compiler snapshot hash differs.");
            RequireSet(ShadowReflectionBindingEvidence.UserDefines(receipt.extraScriptingDefines), defines, "Captured compiler defines");
            ShadowSourcePins.RequireCompatible(baseline.sourcePins, receipt.sourcePins);
            return receipt;
        }

        private static ShadowPatchBuildRequest Request(M05Build.M05FixtureManifest manifest, string snapshot, string output, string patchId,
            string[] roots, BuildTarget target, ShadowSourcePins pins, ShadowPolicyConfiguration policy)
        {
            return new ShadowPatchBuildRequest { baselineManifestPath = manifest.baselineManifestPath, currentCompileSnapshot = snapshot,
                outputDirectory = output, patchId = patchId, target = target, architecture = manifest.architecture, sourcePins = pins,
                policy = policy, explicitChangedRoots = roots, dllOnly = true, includePdb = true };
        }

        internal static void VerifyArtifactTree(string recorded, string replayed)
        {
            Require(Path.IsPathRooted(recorded) && Path.IsPathRooted(replayed), "Artifact directories must be absolute.");
            var left = Directory.GetFiles(recorded, "*", SearchOption.AllDirectories).ToDictionary(path => path.Substring(recorded.TrimEnd(Path.DirectorySeparatorChar).Length + 1), ShadowHash.File, StringComparer.Ordinal);
            var right = Directory.GetFiles(replayed, "*", SearchOption.AllDirectories).ToDictionary(path => path.Substring(replayed.TrimEnd(Path.DirectorySeparatorChar).Length + 1), ShadowHash.File, StringComparer.Ordinal);
            Require(left.Count == right.Count && right.All(item => left.ContainsKey(item.Key) && left[item.Key] == item.Value), "Replayed artifact tree differs byte-for-byte from recorded patch artifacts.");
        }

        private static void VerifyFrozenResources(M05Build.M05FixtureManifest manifest, ShadowBaselineManifest baseline, AssemblySnapshotReceipt player, BuildTarget target)
        {
            string frozen = M01Paths.BaselineRoot(target);
            BuildBaselineBundles.VerifyExisting(frozen);
            foreach (string name in new[] { "AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility", "AssemblyA.Implementation.Internal" })
            {
                var input = player.assemblies.Single(item => item.name == name);
                CompilePatchDlls.VerifySemanticEquivalence(Path.Combine(frozen, "AssemblySnapshot/" + name + ".dll"), ShadowHash.SafeChild(manifest.baselineInputSnapshot, input.path));
            }
            string resourceRoot = ShadowHash.SafeChild(Path.GetDirectoryName(manifest.baselineManifestPath), baseline.resourceBaselinePath);
            var resource = ShadowResourceBaseline.ReadAndVerify(resourceRoot, target, manifest.architecture);
            Require(ShadowHash.File(Path.Combine(resourceRoot, ShadowResourceBaseline.ReceiptName)) == baseline.resourceBuildReceiptHash &&
                resource.Receipt.provenance == ShadowResourceBaseline.M01Provenance && resource.Receipt.resourceAbiHash == baseline.resourceAbiHash &&
                resource.Receipt.resourceIndexHash == baseline.resourceIndexHash && resource.Receipt.compilerSnapshotHash == player.snapshotHash,
                "Frozen M01 resources do not bind this M05 Player.");
        }

        private static void RequireSet(IEnumerable<string> actual, IEnumerable<string> expected, string description)
        {
            var a = actual.ToArray(); var b = expected.ToArray();
            Require(a.Distinct(StringComparer.Ordinal).Count() == a.Length && b.Distinct(StringComparer.Ordinal).Count() == b.Length &&
                new HashSet<string>(a, StringComparer.Ordinal).SetEquals(b), description + " differs.");
        }
        private static void VerifyHash(string path, string hash) { Require(Path.IsPathRooted(path) && !string.IsNullOrEmpty(hash) && File.Exists(path) && ShadowHash.File(path) == hash, "Artifact hash mismatch: " + path); }
        private static void Require(bool value, string message) { if (!value) throw new BuildFailedException(message); }
        private sealed class ReplayContext { public M05Build.M05FixtureManifest Manifest; public ShadowBaselineManifest Baseline; public AssemblySnapshotReceipt Player; public M05Build.M05PlayerBuildReceipt PlayerReceipt; public string Scratch; }

        [Serializable] public sealed class FixtureReplayReceipt
        {
            public int schemaVersion;
            public string milestone, result, comparisonPolicy;
            public string fixtureManifestPath, fixtureManifestSha256, baselineManifestPath, baselineManifestSha256, playerBuildReceiptPath, playerBuildReceiptSha256;
            public string baselineInputSnapshotHash, baselineBuildId, playerBuildGuid, nativeLibrarySha256, linkedPlayerReceiptHash;
            public string runtimeAbiHash, unityVersion, target, architecture, stableAotProvenanceHash, typeProofPath, typeProofSha256, replayScratchPath;
            public ShadowSourcePins validatorSourcePins;
            public FixtureReplayEntry[] fixtures;
            public RejectedReplayEntry[] rejectedFixtures;
        }
        [Serializable] public sealed class FixtureReplayEntry { public string patchId, patchManifestSha256, compileSnapshotHash; public string[] changedRoots, closureLoadOrder; }
        [Serializable] public sealed class RejectedReplayEntry { public string fixtureId, compileSnapshotHash, dllSha256, errorCode, errorMessage; }
    }
}
