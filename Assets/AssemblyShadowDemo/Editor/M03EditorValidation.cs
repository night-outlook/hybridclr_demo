using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Replays compiler/linker proof without recompiling or rewriting any artifact.</summary>
    public static class M03EditorValidation
    {
        public const string ComparisonPolicy = "compiler-linked-policy-graph-resource-abi:2";

        /// <summary>Batchmode entry point; replay is read-only apart from a new evidence receipt.</summary>
        public static void Validate()
        {
            string manifest = AssemblyShadowBuildCommands.Argument("-shadowFixtureManifest", "");
            Require(!string.IsNullOrEmpty(manifest), "Pass -shadowFixtureManifest to replay M03 fixture evidence.");
            string receipt = AssemblyShadowBuildCommands.Argument("-shadowValidationReceipt", "");
            Debug.Log("[AssemblyShadow M03] Independent Editor replay: " + ValidateAndWriteReceipt(manifest, receipt));
        }

        public static string ValidateAndWriteReceipt(string manifestPath, string receiptPath = null)
        {
            manifestPath = Path.GetFullPath(manifestPath);
            receiptPath = Path.GetFullPath(string.IsNullOrEmpty(receiptPath)
                ? Path.Combine(Path.GetDirectoryName(manifestPath), "m03-editor-replay.json") : receiptPath);
            Require(!File.Exists(receiptPath) && !Directory.Exists(receiptPath), "M03 replay receipt already exists: " + receiptPath);
            Require(File.Exists(manifestPath), "M03 fixture manifest is missing: " + manifestPath);
            string before = ShadowHash.File(manifestPath);
            ValidateFixtures(manifestPath);
            Require(ShadowHash.File(manifestPath) == before, "M03 fixture manifest changed during replay.");
            var manifest = JsonUtility.FromJson<M03Build.M03FixtureManifest>(File.ReadAllText(manifestPath));
            var baseline = JsonUtility.FromJson<ShadowBaselineManifest>(File.ReadAllText(manifest.baselineManifestPath));
            var player = AssemblySnapshot.ReadAndVerify(manifest.baselineInputSnapshot, true);
            var pins = ShadowSourcePins.Read(AssemblyShadowSettings.Instance.sourcePinFile,
                EditorUserBuildSettings.activeBuildTarget, AssemblyShadowSettings.Instance.architecture);
            ShadowSourcePins.RequireSameBuildSources(pins, baseline.sourcePins);
            Require(Application.unityVersion == manifest.unityVersion, "Editor replay Unity version differs from the captured Player.");
            var receipt = new FixtureReplayReceipt {
                schemaVersion = 1, milestone = "M03", result = "Passed", comparisonPolicy = ComparisonPolicy,
                fixtureManifestPath = manifestPath, fixtureManifestSha256 = before,
                baselineManifestPath = Path.GetFullPath(manifest.baselineManifestPath), baselineManifestSha256 = manifest.baselineManifestSha256,
                baselineInputSnapshotHash = player.snapshotHash, baselineBuildId = baseline.baselineBuildId,
                playerBuildGuid = player.buildGuid, nativeLibrarySha256 = player.nativeLibrarySha256,
                linkedPlayerReceiptHash = player.linkedPlayerReceiptHash, runtimeAbiHash = manifest.runtimeAbiHash,
                unityVersion = manifest.unityVersion, target = manifest.target, architecture = manifest.architecture,
                stableAotProvenanceHash = manifest.stableAotProvenanceHash, validatorSourcePins = pins,
                fixtures = manifest.fixtures.Select(fixture => new FixtureReplayEntry {
                    patchId = fixture.patchId, patchManifestSha256 = fixture.patchManifestSha256,
                    compileSnapshotHash = fixture.compileSnapshotHash, changedRoots = fixture.changedRoots,
                    closureLoadOrder = fixture.closureLoadOrder,
                }).ToArray(),
            };
            string json = JsonUtility.ToJson(receipt, true);
            // CreateNew refuses a concurrent writer too. A truncated write can
            // never become valid evidence because consumers parse and bind it.
            using (var stream = new FileStream(receiptPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(stream, new UTF8Encoding(false))) writer.Write(json);
            return receiptPath;
        }

        public static void ValidateFixtures(string manifestPath)
        {
            Require(File.Exists(manifestPath), "M03 fixture manifest is missing: " + manifestPath);
            var manifest = JsonUtility.FromJson<M03Build.M03FixtureManifest>(File.ReadAllText(manifestPath));
            Require(manifest != null && manifest.schemaVersion == 1 && manifest.milestone == "M03", "M03 fixture manifest schema mismatch.");
            Require(manifest.candidateNames != null && manifest.candidateNames.SequenceEqual(M02Build.Candidates), "M03 candidate identity drifted from M02.");
            Require(manifest.closureLoadOrder != null && manifest.closureLoadOrder.SequenceEqual(M03Build.ProviderFirstOrder), "M03 closure order is not provider-first.");
            Require(manifest.stableAotNames != null && manifest.stableAotNames.Length > 0 && manifest.stableAotNames.SequenceEqual(manifest.stableAotNames.OrderBy(item => item, StringComparer.Ordinal)),
                "Stable AOT names must be non-empty and deterministic.");
            Require(manifest.stableAotProvenanceHash == ShadowHash.Text("m03-stable-aot:2\n" + manifest.stableAotProvenance), "Stable AOT provenance hash mismatch.");
            Require(manifest.fixtures != null && manifest.fixtures.Length == 3, "M03 requires P01, P03, and initializer-throw fixtures.");
            RequireSet(manifest.fixtures.Select(f => f.patchId), new[] { "P01", "P03", "P03-InitializerThrow" }, "Fixture identities");
            VerifyHash(manifest.baselineManifestPath, manifest.baselineManifestSha256);
            var baseline = JsonUtility.FromJson<ShadowBaselineManifest>(File.ReadAllText(manifest.baselineManifestPath));
            Require(baseline != null && baseline.schemaVersion == 1 && baseline.semanticHashSchema == 1 && baseline.baselineBuildId == manifest.baselineBuildId && baseline.runtimeAbiHash == manifest.runtimeAbiHash, "Fixture/baseline identity mismatch.");
            RequireSet(baseline.shadowCandidates, manifest.candidateNames, "Baseline candidates");
            Require(baseline.sourcePins.RuntimeAbiHash() == manifest.runtimeAbiHash && baseline.unityVersion == manifest.unityVersion && baseline.target == manifest.target && baseline.architecture == manifest.architecture, "Baseline source/target ABI mismatch.");
            var player = AssemblySnapshot.ReadAndVerify(manifest.baselineInputSnapshot, true);
            M03DiagnosticSchemaVerifier.Verify(manifest.baselineInputSnapshot, player);
            Require(player.snapshotHash == manifest.baselineInputSnapshotHash && player.snapshotHash == baseline.playerInputSnapshotHash && player.buildId == baseline.baselineBuildId && player.buildGuid == baseline.playerBuildGuid && player.nativeLibrarySha256 == baseline.nativeLibrarySha256, "Captured Player identity mismatch.");
            ShadowSourcePins.RequireSameBuildSources(player.sourcePins, baseline.sourcePins);
            VerifyHash(player.nativeLibraryPath, player.nativeLibrarySha256);
            string frozenPlayerRoot = ShadowHash.SafeChild(Path.GetDirectoryName(manifest.baselineManifestPath), baseline.playerInputSnapshot);
            var frozenPlayer = AssemblySnapshot.ReadAndVerify(frozenPlayerRoot, true);
            Require(frozenPlayer.snapshotHash == player.snapshotHash && frozenPlayer.linkedPlayerReceiptHash == player.linkedPlayerReceiptHash, "Frozen and original linked Player proof differ.");
            BuildTarget target;
            Require(Enum.TryParse(manifest.target, out target), "Unknown fixture build target.");
            var sourcePolicy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            VerifyStableAot(manifest, player, sourcePolicy);
            var baselinePolicy = ShadowFilteredInputPolicy.Apply(sourcePolicy, player);
            using (var baselineSet = Load(manifest.baselineInputSnapshot, player, baselinePolicy))
            {
                ShadowReflectionBindingEvidence.AddCompiledDependencies(baselinePolicy, baselineSet.Assemblies.Values);
                var linked = VerifiedLinkedRuntimeReferences.Verify(manifest.baselineInputSnapshot, player, baselineSet, baselinePolicy);
                ShadowReflectionBindingEvidence.ValidateCompiled(baselineSet, baselinePolicy, manifest.baselineInputSnapshot, player, true, linked).ThrowIfInvalid();
                Require(BootstrapHash(baselineSet.Assemblies.Values) == baseline.bootstrapAbiHash, "Baseline Bootstrap semantic proof changed.");
            }
            foreach (M03Build.M03Fixture fixture in manifest.fixtures)
            {
                VerifyHash(fixture.patchManifest, fixture.patchManifestSha256);
                Require(Directory.Exists(fixture.compileSnapshot), "Fixture compiler snapshot is missing: " + fixture.patchId);
                AssemblySnapshotReceipt receipt = AssemblySnapshot.ReadAndVerify(fixture.compileSnapshot, false);
                Require(receipt.snapshotHash == fixture.compileSnapshotHash, "Fixture compiler snapshot changed: " + fixture.patchId);
                Require(fixture.stableAotNames.SequenceEqual(manifest.stableAotNames), "Fixture stable AOT provenance differs from manifest.");
                RequireSet(ShadowReflectionBindingEvidence.UserDefines(receipt.extraScriptingDefines), fixture.defines, "Compiler define evidence");
                Require(fixture.defines.Contains(M03Build.InitializerDefine) && fixture.defines.Contains("ASSEMBLY_SHADOW_P01"), "Fixture must compile actual initializers and patched business marker.");
                Require(fixture.defines.Contains(M03Build.InitializerThrowDefine) == (fixture.patchId == "P03-InitializerThrow"), "Throw define is not isolated to the failure fixture.");
                Require(fixture.defines.Contains(M03Build.P03InitializerDefine) == (fixture.patchId != "P01"), "Five-assembly initializer define mismatch.");
                ShadowSourcePins.RequireCompatible(baseline.sourcePins, receipt.sourcePins);
                var patch = JsonUtility.FromJson<ShadowPatchManifest>(File.ReadAllText(fixture.patchManifest));
                Require(patch != null && patch.schemaVersion == 1 && patch.semanticHashSchema == 1 && patch.patchId == fixture.patchId && patch.baselineBuildId == baseline.baselineBuildId && patch.baselineManifestSha256 == manifest.baselineManifestSha256 && patch.runtimeAbiHash == baseline.runtimeAbiHash, "Patch/baseline binding mismatch.");
                Require(patch.compileSnapshotHash == receipt.snapshotHash && patch.unityVersion == receipt.unityVersion && patch.target == receipt.target && patch.architecture == receipt.architecture && patch.unityVersion == baseline.unityVersion && patch.target == baseline.target && patch.architecture == baseline.architecture, "Patch compile/target mismatch.");
                ShadowSourcePins.RequireCompatible(patch.sourcePins, receipt.sourcePins);
                var policy = ShadowFilteredInputPolicy.ApplyPatch(sourcePolicy, player, baseline.shadowCandidates, baseline.bootstrapAssemblies);
                using (var set = Load(fixture.compileSnapshot, receipt, policy))
                {
                    ShadowReflectionBindingEvidence.AddCompiledDependencies(policy, set.Assemblies.Values);
                    var linked = VerifiedLinkedRuntimeReferences.Verify(frozenPlayerRoot, frozenPlayer, set, policy);
                    ShadowReflectionBindingEvidence.ValidateCompiled(set, policy, fixture.compileSnapshot, receipt, false, linked).ThrowIfInvalid();
                    Require(BootstrapHash(set.Assemblies.Values) == baseline.bootstrapAbiHash && patch.bootstrapAbiHash == baseline.bootstrapAbiHash, "Patch changed fixed Bootstrap metadata/IL.");
                    string[] roots = AssemblyReferenceGraph.DetectChangedRoots(baseline.assemblies, set.Assemblies.Values, fixture.changedRoots);
                    var graph = new AssemblyReferenceGraph(set.Assemblies.Values, policy.dependencies, baseline.dependencyGraph);
                    string[] closure = graph.ReverseClosure(roots);
                    RequireSet(roots, patch.changedRoots, "Replayed changed roots");
                    RequireSet(closure, patch.closure.Select(a => a.name), "Replayed reverse closure");
                    RequireSet(closure, fixture.patchId == "P01" ? new[] { "AssemblyA.Implementation.Internal" } : manifest.candidateNames, "Mode-specific closure");
                    Require(graph.LoadOrder(closure).SequenceEqual(patch.loadOrder) && patch.loadOrder.SequenceEqual(fixture.closureLoadOrder), "Replayed provider-before-consumer order mismatch.");
                    Require(JsonUtility.ToJson(new EdgeList { edges = graph.Edges }) == JsonUtility.ToJson(new EdgeList { edges = patch.dependencyGraph }), "Replayed graph differs from patch manifest.");
                    var resourceAbi = UnitySerializedTypeAnalyzer.Analyze(set, baseline.shadowCandidates);
                    Require(ResourceAbiHasher.Compute(resourceAbi) == baseline.resourceAbiHash && patch.baselineResourceAbiHash == baseline.resourceAbiHash && patch.resourceAbiHash == baseline.resourceAbiHash && patch.dllOnly, "Patch resource ABI is not DLL-only compatible.");
                    var artifactDlls = new HashSet<string>(StringComparer.Ordinal);
                    foreach (ShadowPatchAssembly assembly in patch.closure)
                    {
                        var descriptor = set.Get(assembly.name);
                        var file = receipt.assemblies.Single(a => a.name == assembly.name);
                        string dll = ShadowHash.SafeChild(fixture.patchDirectory, assembly.dll);
                        VerifyHash(dll, assembly.sha256);
                        artifactDlls.Add(Path.GetFullPath(dll));
                        Require(assembly.sha256 == file.sha256 && assembly.sha256 == descriptor.sha256 && assembly.semanticHash == descriptor.semanticHash && assembly.mvid == descriptor.mvid && assembly.baselineMvid == baseline.assemblies.Single(a => a.name == assembly.name).mvid, "Patch identity differs from actual compiler bytes: " + assembly.name);
                        RequireSet(assembly.references, descriptor.references, "Actual AssemblyRefs: " + assembly.name);
                        Require(!string.IsNullOrEmpty(assembly.pdb) && !string.IsNullOrEmpty(file.pdbPath), "M03 symbol retry fixture requires compiler PDBs.");
                        VerifyHash(ShadowHash.SafeChild(fixture.patchDirectory, assembly.pdb), assembly.pdbSha256);
                        Require(assembly.pdbSha256 == file.pdbSha256, "Patch PDB differs from compiler output.");
                    }
                    Require(artifactDlls.SetEquals(Directory.GetFiles(fixture.patchDirectory, "*.dll", SearchOption.AllDirectories).Select(Path.GetFullPath)), "Undeclared DLL in patch artifacts.");
                }
            }
        }

        private static CompiledAssemblySet Load(string root, AssemblySnapshotReceipt receipt, ShadowPolicyConfiguration policy)
        {
            ShadowReflectionBindingEvidence.RequirePolicy(policy, root, receipt, receipt.kind == "PlayerBuildInputs");
            var framework = TargetFrameworkReferenceVerifier.Verify(root, receipt);
            return DnlibAssemblyLoader.Load(Path.Combine(root, "Assemblies"), new[] { Path.Combine(root, "References") }, policy.assemblies, targetFrameworkReferences: framework);
        }

        private static void VerifyStableAot(M03Build.M03FixtureManifest manifest, AssemblySnapshotReceipt player, ShadowPolicyConfiguration policy)
        {
            var framework = TargetFrameworkReferenceVerifier.Verify(manifest.baselineInputSnapshot, player);
            var libraries = M03CompilerLibraryVerifier.Verify(manifest.baselineInputSnapshot, player, framework);
            var physical = player.linkedPlayerReceipt.assemblies.ToDictionary(a => AssemblyIdentityUtil.CanonicalName(a.name), a => a.name, StringComparer.OrdinalIgnoreCase);
            var candidates = new HashSet<string>(manifest.candidateNames.Select(AssemblyIdentityUtil.CanonicalName), StringComparer.OrdinalIgnoreCase);
            var expected = new HashSet<string>(StringComparer.Ordinal);
            foreach (string provider in framework.Providers.Concat(libraries.Providers))
            {
                string identity = provider.Split(new[] { " | " }, StringSplitOptions.None)[0];
                string name = AssemblyIdentityUtil.CanonicalName(new System.Reflection.AssemblyName(identity).Name);
                string actual;
                if (!candidates.Contains(name) && physical.TryGetValue(name, out actual)) expected.Add(actual);
            }
            var bootstrap = policy.assemblies.Where(a => a.isBootstrap).Select(a => AssemblyIdentityUtil.CanonicalName(a.name)).OrderBy(n => n, StringComparer.Ordinal).ToArray();
            Require(bootstrap.Length > 0, "Fixed Bootstrap provenance is absent.");
            foreach (string name in bootstrap)
            {
                string actual;
                Require(!candidates.Contains(name) && physical.TryGetValue(name, out actual), "Fixed Bootstrap lacks linked physical AOT proof: " + name);
                expected.Add(physical[name]);
            }
            RequireSet(manifest.stableAotNames, expected, "Replayed stable physical AOT allowlist");
            string provenance = "framework=" + framework.ProvenanceHash + "\ncompiler-libraries=" + libraries.ProvenanceHash +
                "\nlinked-player=" + player.linkedPlayerReceiptHash + "\nbootstrap-policy=" + string.Join(",", bootstrap) + "\nphysical=" + string.Join(",", expected.OrderBy(n => n, StringComparer.Ordinal));
            Require(manifest.stableAotProvenance == provenance && manifest.stableAotProvenanceHash == ShadowHash.Text("m03-stable-aot:2\n" + provenance), "Stable AOT provenance does not replay from compiler/linker bytes.");
        }

        private static string BootstrapHash(IEnumerable<AssemblyDescriptor> descriptors)
        {
            return ShadowHash.Text("bootstrap-abi:1\n" + string.Join("\n", descriptors.Where(a => a.isBootstrap).OrderBy(a => a.name, StringComparer.Ordinal).Select(a => AssemblyIdentityUtil.CanonicalName(a.name) + ":" + a.semanticHash)));
        }

        private static void RequireSet(IEnumerable<string> actual, IEnumerable<string> expected, string description)
        {
            Require(actual != null && expected != null, description + " is absent.");
            string[] values = actual.ToArray(), required = expected.ToArray();
            Require(values.Length == values.Distinct(StringComparer.Ordinal).Count() && required.Length == required.Distinct(StringComparer.Ordinal).Count() && new HashSet<string>(values, StringComparer.Ordinal).SetEquals(required), description + " differs.");
        }

        private static void VerifyHash(string path, string expected)
        {
            Require(!string.IsNullOrEmpty(expected) && File.Exists(path) && ShadowHash.File(path) == expected, "Artifact hash mismatch: " + path);
        }

        [Serializable] private sealed class EdgeList { public AssemblyDependencyEdge[] edges; }

        [Serializable] public sealed class FixtureReplayReceipt
        {
            public int schemaVersion;
            public string milestone, result, comparisonPolicy;
            public string fixtureManifestPath, fixtureManifestSha256, baselineManifestPath, baselineManifestSha256;
            public string baselineInputSnapshotHash, baselineBuildId, playerBuildGuid, nativeLibrarySha256, linkedPlayerReceiptHash;
            public string runtimeAbiHash, unityVersion, target, architecture, stableAotProvenanceHash;
            public ShadowSourcePins validatorSourcePins;
            public FixtureReplayEntry[] fixtures;
        }

        [Serializable] public sealed class FixtureReplayEntry
        {
            public string patchId, patchManifestSha256, compileSnapshotHash;
            public string[] changedRoots, closureLoadOrder;
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new BuildFailedException(message);
        }
    }
}
