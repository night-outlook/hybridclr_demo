using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Globalization;
using System.Text;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    public static partial class M06ExecutionProbe
    {
        private static Input ReadInputs(string expectedBaselineBuildId, string expectedRuntimeAbiHash)
        {
            string manifestPath = Absolute(Argument("-shadowM06Fixtures", ""));
            string receiptPath = Absolute(Argument("-shadowM06PlayerReceipt", ""));
            Require(!string.IsNullOrEmpty(manifestPath) && File.Exists(manifestPath), "M06 fixture manifest is missing.");
            Require(!string.IsNullOrEmpty(receiptPath) && File.Exists(receiptPath), "M06 Player receipt is missing.");
            FixtureManifest manifest = ReadJson<FixtureManifest>(File.ReadAllText(manifestPath));
            PlayerBuildReceipt player = ReadJson<PlayerBuildReceipt>(File.ReadAllText(receiptPath));
            Require(manifest != null && player != null, "M06 input JSON root is malformed.");
            ValidateManifest(manifest, expectedBaselineBuildId, expectedRuntimeAbiHash);
            ValidatePlayer(player, expectedBaselineBuildId, expectedRuntimeAbiHash);
            Require(manifest.developmentBuild == player.developmentBuild, "M06 manifest/Player development mode differs.");
            string baselinePath = Absolute(manifest.baselineManifestPath);
            VerifyBytes(baselinePath, manifest.baselineManifestSha256, "baseline manifest");
            BaselineManifest baseline = JsonUtility.FromJson<BaselineManifest>(File.ReadAllText(baselinePath));
            Require(baseline != null && baseline.baselineBuildId == expectedBaselineBuildId && baseline.assemblies != null && baseline.assemblies.Length > 0, "M06 baseline manifest identity evidence is incomplete.");
            foreach (Fixture fixture in manifest.fixtures ?? new Fixture[0]) LoadPatchManifest(fixture, manifest.baselineManifestSha256, expectedBaselineBuildId, expectedRuntimeAbiHash);
            LoadPatchManifest(manifest.initializerFailureFixture, manifest.baselineManifestSha256, expectedBaselineBuildId, expectedRuntimeAbiHash);
            ValidateBaselineLinks(manifest, baseline);
            var input = new Input { manifestPath = manifestPath, playerReceiptPath = receiptPath, manifest = manifest, player = player, baseline = baseline };
            ValidateProofGraph(input);
            return input;
        }

        private static void ValidateBaselineLinks(FixtureManifest manifest, BaselineManifest baseline)
        {
            foreach (Fixture fixture in (manifest.fixtures ?? new Fixture[0]).Concat(new[] { manifest.initializerFailureFixture }))
                foreach (PatchAssembly patch in fixture.patch.closure)
                {
                    BaselineAssembly row = baseline.assemblies.SingleOrDefault(candidate => candidate.name == patch.name);
                    Require(row != null && !string.IsNullOrEmpty(row.mvid) && patch.baselineMvid == row.mvid, "M06 patch baseline MVID provenance mismatch: " + patch.name);
                }
        }

        private static void ValidateManifest(FixtureManifest manifest, string expectedBaselineBuildId, string expectedRuntimeAbiHash)
        {
            Require(manifest.schemaVersion == 1 && manifest.milestone == "M06", "M06 fixture manifest schema/milestone mismatch.");
            Require(manifest.baselineBuildId == expectedBaselineBuildId && manifest.runtimeAbiHash == expectedRuntimeAbiHash, "M06 fixture baseline/ABI binding mismatch.");
            Require(!string.IsNullOrEmpty(manifest.baselineManifestPath) && IsHash(manifest.baselineManifestSha256) && IsHash(manifest.baselineInputSnapshotHash) && IsHash(manifest.stableAotProvenanceHash), "M06 manifest hash binding is incomplete.");
            Require(manifest.candidateNames != null && manifest.candidateNames.SequenceEqual(Candidates), "M06 candidate order differs from the fixed candidate inventory.");
            Require(manifest.closureLoadOrder != null && manifest.stableAotNames != null, "M06 manifest closure/stable arrays are missing.");
            Require(manifest.fixtures != null && manifest.fixtures.Length == 3, "M06 manifest must contain exactly P01/P02/P03 fixtures.");
            Require(manifest.fixtures.Select(fixture => fixture.patchId).OrderBy(value => value, StringComparer.Ordinal).SequenceEqual(new[] { "P01", "P02", "P03" }), "M06 fixture IDs are not exactly P01/P02/P03.");
            ValidateProofFile(manifest.generationProofPath, manifest.generationProofSha256, "generation proof");
            foreach (Fixture fixture in manifest.fixtures) ValidateFixture(fixture, expectedBaselineBuildId, expectedRuntimeAbiHash);
            Require(manifest.initializerFailureFixture != null && manifest.initializerFailureFixture.patchId == "InitializerFailure", "M06 initializer-failure fixture is missing.");
            ValidateFixture(manifest.initializerFailureFixture, expectedBaselineBuildId, expectedRuntimeAbiHash);
        }

        private static void ValidateFixture(Fixture fixture, string expectedBaselineBuildId, string expectedRuntimeAbiHash)
        {
            Require(fixture != null && fixture.patchId != null && fixture.defines != null && fixture.changedRoots != null && fixture.closureLoadOrder != null,
                "M06 fixture root/closure fields are missing.");
            Require(fixture.compileSnapshot != null && IsHash(fixture.compileSnapshotHash) && fixture.patchDirectory != null, "M06 fixture compile binding is incomplete.");
            Require(fixture.patchManifest != null && IsHash(fixture.patchManifestSha256), "M06 fixture patch manifest binding is incomplete.");
            Require(fixture.stableAotNames != null && fixture.requiredAotMetadataNames != null && fixture.assemblyIdentities != null && fixture.typeInventories != null, "M06 fixture identity/type fields are missing.");
            Require(fixture.variant != null && fixture.generationPlanPath != null && IsHash(fixture.generationPlanSha256), "M06 fixture generation binding is incomplete.");
            Require(fixture.closureLoadOrder.Length > 0 && fixture.closureLoadOrder.All(name => Candidates.Contains(name, StringComparer.Ordinal)), "M06 fixture closure contains an unknown candidate.");
            Require(fixture.requiredAotMetadataNames.All(name => !fixture.closureLoadOrder.Contains(name, StringComparer.Ordinal) &&
                (fixture.stableAotNames.Contains(name, StringComparer.Ordinal) || Candidates.Contains(name, StringComparer.Ordinal))),
                "M06 required AOT metadata escapes the selected closure/candidate/stable policy.");
            Require(fixture.patchId == "InitializerFailure" ? fixture.closureLoadOrder.SequenceEqual(new[] { Internal }) : fixture.closureLoadOrder.SequenceEqual(ExpectedClosure(fixture.patchId)), "M06 fixture closure order mismatch.");
            ValidateProofFile(fixture.generationPlanPath, fixture.generationPlanSha256, "fixture generation plan");
            foreach (M04ReferenceProbe.AssemblyIdentity identity in fixture.assemblyIdentities)
            {
                Require(identity != null && Candidates.Contains(identity.name, StringComparer.Ordinal) && IsHash(identity.sha256) && !string.IsNullOrEmpty(identity.path), "M06 fixture identity is incomplete.");
                VerifyBytes(identity.path, identity.sha256, "fixture " + identity.name);
            }
        }

        private static string[] ExpectedClosure(string patchId)
        {
            switch (patchId)
            {
                case "P01": return new[] { Internal };
                case "P02": return new[] { Extensibility, Internal, ExtensibilityConsumer };
                case "P03": return Candidates.ToArray();
                default: throw new ArgumentException("Unknown M06 fixture: " + patchId);
            }
        }

        private static void ValidatePlayer(PlayerBuildReceipt player, string expectedBaselineBuildId, string expectedRuntimeAbiHash)
        {
            Require(player.schemaVersion == 1 && player.milestone == "M06" && player.baselineBuildId == expectedBaselineBuildId && player.runtimeAbiHash == expectedRuntimeAbiHash,
                "M06 Player receipt schema/baseline binding mismatch.");
            Require(player.variant == "NativeOn" || player.variant == "NativeOff", "M06 Player native variant is unknown.");
            string requestedMode = Argument("-shadowM06Mode", "T06-01-New-P01");
            Require(player.variant == (requestedMode == "T06-11-FeatureOff" ? "NativeOff" : "NativeOn") &&
                player.developmentBuild == (requestedMode != "T06-13-ReleaseNoPdb"), "M06 mode requires its genuine native/development Player build.");
            Require(player.buildGuid == Application.buildGUID && !string.IsNullOrEmpty(player.buildGuid), "M06 Player build GUID mismatch.");
            // Pinned Unity 2022.3 BuildOptions.DetailedBuildReport = 1 << 29; Development = 1.
            Require(player.buildOptions == (536870912 | (player.developmentBuild ? 1 : 0)), "M06 actual Player build options differ from the declared build workflow.");
            Require(Debug.isDebugBuild == player.developmentBuild, "M06 Player debug-build flag differs from the captured build mode.");
            Require(IsHash(player.nativeLibrarySha256) && IsHash(player.nativeMetadataSha256), "M06 native Player hashes are incomplete.");
            VerifyBytes(player.nativeLibraryPath, player.nativeLibrarySha256, "native library");
            string[] nativeLibraries = Directory.GetFiles(Application.dataPath, "GameAssembly.dylib", SearchOption.AllDirectories).Select(Absolute).ToArray();
            Require(player.unityVersion == Application.unityVersion && player.target == "StandaloneOSX" && player.architecture == "arm64" &&
                nativeLibraries.Length == 1 && nativeLibraries[0] == Absolute(player.nativeLibraryPath) &&
                Absolute(Application.dataPath).StartsWith(Absolute(player.playerOutput).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar, StringComparison.Ordinal),
                "M06 native library/target is not this executed pinned Player.");
            Require(player.nativeMetadataVersion == 31, "M06 requires global-metadata.dat version 31.");
            string metadata = Absolute(player.nativeMetadataPath);
            VerifyBytes(metadata, player.nativeMetadataSha256, "global metadata");
            byte[] metadataBytes = File.ReadAllBytes(metadata);
            Require(metadataBytes.Length >= 8 && BitConverter.ToUInt32(metadataBytes, 0) == 0xFAB11BAFu && BitConverter.ToInt32(metadataBytes, 4) == 31,
                "M06 global-metadata.dat header/version is not the executed Unity metadata format.");
            string[] metadataFiles = Directory.GetFiles(Application.dataPath, "global-metadata.dat", SearchOption.AllDirectories).Select(Absolute).Distinct(StringComparer.Ordinal).ToArray();
            Require(metadataFiles.Length == 1 && metadataFiles[0] == metadata, "M06 metadata path is not the unique executed Player global-metadata.dat.");
            Require(!string.IsNullOrEmpty(player.inputSnapshot) && Directory.Exists(Absolute(player.inputSnapshot)) && IsHash(player.inputSnapshotHash),
                "M06 Player input snapshot binding is incomplete.");
            ValidatePlayerSnapshot(player);
            ValidateProofFile(player.typeProofPath, player.typeProofSha256, "type proof");
            ValidateProofFile(player.generationProofPath, player.generationProofSha256, "Player generation proof");
            ValidateProofFile(player.executionProofPath, player.executionProofSha256, "execution proof");
            Require(player.nativeAssemblyIdentities != null && player.nativeAssemblyIdentities.Length > 0 && player.nativeGeneratedAssemblyNames != null,
                "M06 native assembly inventory is missing.");
            Require(player.assemblyIdentities != null && player.assemblyIdentities.Length > 0, "M06 linked assembly inventory is missing.");
            foreach (M04ReferenceProbe.AssemblyIdentity identity in player.assemblyIdentities)
            {
                Require(identity != null && !string.IsNullOrEmpty(identity.name) && !string.IsNullOrEmpty(identity.fullName) &&
                    IsHash(identity.sha256) && !string.IsNullOrEmpty(identity.path), "M06 linked assembly identity is incomplete.");
                VerifyBytes(identity.path, identity.sha256, "linked assembly " + identity.name);
            }
            if (player.supplementaryMetadataInputs != null)
                foreach (SupplementaryMetadataInput input in player.supplementaryMetadataInputs)
                {
                    Require(input != null && !string.IsNullOrEmpty(input.assemblyName) && IsHash(input.sha256) && input.identity != null, "M06 supplementary metadata input is incomplete.");
                    VerifyBytes(input.path, input.sha256, "supplementary metadata " + input.assemblyName);
                    M04ReferenceProbe.AssemblyIdentity linked = player.assemblyIdentities.SingleOrDefault(identity => identity != null && identity.name == input.assemblyName);
                    Require(linked != null && input.identity.name == linked.name && input.identity.fullName == linked.fullName && input.identity.mvid == linked.mvid &&
                        input.identity.sha256 == linked.sha256 && Absolute(input.identity.path) == Absolute(input.path) && input.sha256 == linked.sha256,
                        "M06 supplementary metadata input is not the same verified linked Player identity: " + input.assemblyName);
                }
        }

        private static void LoadPatchManifest(Fixture fixture, string baselineManifestSha256, string expectedBaselineBuildId, string expectedRuntimeAbiHash)
        {
            if (fixture == null) return;
            string path = Absolute(fixture.patchManifest);
            Require(HashFile(path) == fixture.patchManifestSha256, "M06 patch manifest hash mismatch: " + fixture.patchId);
            string json = File.ReadAllText(path);
            PatchManifestVersion version = JsonUtility.FromJson<PatchManifestVersion>(json);
            Require(version != null && (version.schemaVersion == 1 || version.schemaVersion == 2), "M06 patch manifest schema version is not explicit: " + fixture.patchId);
            if (version.schemaVersion == 2)
            {
                var objectFields = new ProofJsonReader(json).Read() as Dictionary<string, object>;
                Require(objectFields != null && objectFields.Count == 3 && objectFields.ContainsKey("schemaVersion") && objectFields.ContainsKey("patch") && objectFields.ContainsKey("warmup"),
                    "M06 warmup envelope field schema differs.");
                ValidateJsonShape(objectFields["warmup"], typeof(WarmupPlan), "warmup");
                PatchManifestEnvelope envelope = JsonUtility.FromJson<PatchManifestEnvelope>(json);
                Require(envelope != null && envelope.schemaVersion == 2 && envelope.patch != null && envelope.warmup != null,
                    "M06 schema-2 patch manifest envelope is incomplete: " + fixture.patchId);
                Require(envelope.warmup.types != null && envelope.warmup.methods != null, "M06 schema-2 warmup envelope is incomplete: " + fixture.patchId);
                fixture.patch = envelope.patch;
                fixture.warmup = envelope.warmup;
            }
            else { fixture.patch = JsonUtility.FromJson<PatchManifest>(json); fixture.warmup = null; }
            Require(fixture.patch != null && fixture.patch.patchId == fixture.patchId && fixture.patch.closure != null && fixture.patch.loadOrder != null,
                "M06 patch manifest root mismatch: " + fixture.patchId);
            Require(fixture.patch.schemaVersion == 1 && fixture.patch.semanticHashSchema == 1 && fixture.patch.baselineBuildId == expectedBaselineBuildId &&
                fixture.patch.baselineManifestSha256 == baselineManifestSha256 && fixture.patch.runtimeAbiHash == expectedRuntimeAbiHash &&
                fixture.patch.compileSnapshotHash == fixture.compileSnapshotHash, "M06 patch baseline/compiler identity is missing: " + fixture.patchId);
            Require(fixture.patch.loadOrder.SequenceEqual(fixture.closureLoadOrder), "M06 patch manifest order differs from fixture order: " + fixture.patchId);
            RequireSet(fixture.patch.closure.Select(row => row.name), fixture.closureLoadOrder, "patch closure");
            foreach (PatchAssembly assembly in fixture.patch.closure)
            {
                Require(assembly != null && fixture.closureLoadOrder.Contains(assembly.name, StringComparer.Ordinal) && IsHash(assembly.sha256), "M06 patch closure identity is incomplete.");
                assembly.dll = ConfinedPatchPath(path, assembly.dll);
                VerifyBytes(assembly.dll, assembly.sha256, "patch " + assembly.name);
                M04ReferenceProbe.AssemblyIdentity identity = fixture.assemblyIdentities.SingleOrDefault(candidate => candidate != null && candidate.name == assembly.name);
                Require(identity != null && identity.sha256 == assembly.sha256 && identity.mvid == assembly.mvid && Absolute(identity.path) == assembly.dll,
                    "M06 patch DLL identity differs from the fixture's verified linked bytes: " + assembly.name);
                if (!string.IsNullOrEmpty(assembly.pdb)) { Require(IsHash(assembly.pdbSha256), "M06 patch PDB hash missing: " + assembly.name); assembly.pdb = ConfinedPatchPath(path, assembly.pdb); VerifyBytes(assembly.pdb, assembly.pdbSha256, "patch PDB " + assembly.name); }
                else Require(string.IsNullOrEmpty(assembly.pdbSha256), "M06 unbound patch PDB hash.");
            }
        }

        private static string ConfinedPatchPath(string manifestPath, string relativePath)
        {
            Require(!string.IsNullOrEmpty(relativePath) && !Path.IsPathRooted(relativePath), "M06 patch paths must be relative to their verified manifest.");
            string root = Path.GetFullPath(Path.GetDirectoryName(manifestPath));
            string path = Path.GetFullPath(Path.Combine(root, relativePath));
            string prefix = root.EndsWith(Path.DirectorySeparatorChar.ToString(), StringComparison.Ordinal) ? root : root + Path.DirectorySeparatorChar;
            Require(path.StartsWith(prefix, StringComparison.Ordinal), "M06 patch path escapes its verified manifest directory: " + relativePath);
            return path;
        }

        private static void ValidateProofFile(string path, string sha256, string label)
        {
            Require(!string.IsNullOrEmpty(path) && IsHash(sha256), "M06 " + label + " path/hash is missing.");
            VerifyBytes(path, sha256, label);
        }

        private static void ValidateProofGraph(Input input)
        {
            var manifest = input.manifest; var player = input.player;
            Require(manifest.unityVersion == player.unityVersion && manifest.target == player.target && manifest.architecture == player.architecture &&
                manifest.baselineInputSnapshotHash == player.inputSnapshotHash && Absolute(manifest.baselineInputSnapshot) == Absolute(player.inputSnapshot) &&
                Absolute(manifest.generationProofPath) == Absolute(player.generationProofPath) && manifest.generationProofSha256 == player.generationProofSha256,
                "M06 fixture/Player source-generation binding differs.");
            SnapshotReceipt snapshot = JsonUtility.FromJson<SnapshotReceipt>(File.ReadAllText(Path.Combine(player.inputSnapshot, "assembly-snapshot.json")));
            LinkedPlayerReceipt linked = ReadJson<LinkedPlayerReceipt>(File.ReadAllText(Path.Combine(player.inputSnapshot, "LinkedPlayer/linked-player-receipt.json")));
            Require(snapshot.linkedPlayerReceipt != null && IsHash(snapshot.linkedPlayerReceiptHash) && LinkedReceiptHash(linked) == snapshot.linkedPlayerReceiptHash &&
                LinkedReceiptHash(snapshot.linkedPlayerReceipt) == snapshot.linkedPlayerReceiptHash && linked.buildGuid == player.buildGuid &&
                linked.nativeLibrarySha256 == player.nativeLibrarySha256 && linked.target == player.target && linked.architecture == player.architecture,
                "M06 linked receipt is not bound to this exact native Player.");
            RequireCanonicalSet(player.assemblyIdentities.Select(row => row.name), linked.assemblies.Select(row => row.name), "linked identities");
            RequireCanonicalSet(player.nativeAssemblyIdentities.Select(row => row.name), player.nativeAssemblyIdentities.Select(row => row.name).Distinct(), "native identity uniqueness");
            foreach (var row in linked.assemblies)
            {
                var identity = LinkedIdentity(player, row);
                Require(identity.sha256 == row.sha256 && identity.mvid == row.mvid &&
                    Absolute(identity.path) == ConfinedSnapshotPath(Path.Combine(player.inputSnapshot, "LinkedPlayer"), row.path), "M06 linked file identity differs: " + row.name);
                VerifyBytes(identity.path, identity.sha256, "same-build linked DLL");
            }
            RequireSet(manifest.closureLoadOrder, Candidates, "manifest closure");
            Require(manifest.stableAotNames != null && manifest.stableAotNames.Length > 0 &&
                manifest.stableAotNames.SequenceEqual(manifest.stableAotNames.OrderBy(name => name, StringComparer.Ordinal)) &&
                !manifest.stableAotNames.Intersect(Candidates).Any() && manifest.stableAotNames.All(name => linked.assemblies.Any(row => CanonicalName(row.name) == CanonicalName(name))),
                "M06 stable AOT names are not actual same-build linked providers.");
            RequireSet(manifest.stableAotNames, manifest.stableAotNames.Distinct(), "stable AOT uniqueness");
            Require(manifest.stableAotProvenanceHash == Hash(Encoding.UTF8.GetBytes("m06-stable-aot:1\n" + manifest.stableAotProvenance)) &&
                manifest.stableAotProvenance.Contains("\nlinked-player=" + snapshot.linkedPlayerReceiptHash + "\n") &&
                manifest.stableAotProvenance.EndsWith("\nphysical=" + string.Join(",", manifest.stableAotNames), StringComparison.Ordinal), "M06 stable AOT provenance differs.");
            TypeProof typeProof = ReadJson<TypeProof>(File.ReadAllText(player.typeProofPath));
            Require(typeProof.schemaVersion == 1 && typeProof.milestone == "M06" && typeProof.policy == "active-execution-types:1" &&
                typeProof.compileSnapshotHash == player.inputSnapshotHash && typeProof.linkedPlayerReceiptHash == snapshot.linkedPlayerReceiptHash &&
                typeProof.nativeLibrarySha256 == player.nativeLibrarySha256 && typeProof.buildGuid == player.buildGuid &&
                typeProof.developmentBuild == player.developmentBuild && typeProof.moduleMethods != null && typeProof.moduleMethods.Length > 0, "M06 type proof binding differs.");
            RequireCanonicalSet(typeProof.assemblies.Select(row => row.assemblyName), linked.assemblies.Select(row => row.name), "type proof assembly inventory");
            Require(typeProof.assemblies.All(row => row.types != null) && Candidates.All(name => typeProof.assemblies.Single(row => row.assemblyName == name).types.Any(type => type.fullName == WitnessName(name))), "M06 candidate type inventories are incomplete.");
            input.executionProof = ReadJson<ExecutionProof>(File.ReadAllText(player.executionProofPath));
            var execution = input.executionProof;
            Require(execution.schemaVersion == 1 && execution.milestone == "M06" && execution.policy == "execution-world:1" &&
                execution.compileSnapshotHash == player.inputSnapshotHash && execution.linkedPlayerReceiptHash == snapshot.linkedPlayerReceiptHash &&
                execution.nativeLibrarySha256 == player.nativeLibrarySha256 && execution.buildGuid == player.buildGuid &&
                execution.developmentBuild == player.developmentBuild && Absolute(execution.generationProofPath) == Absolute(player.generationProofPath) &&
                execution.generationProofSha256 == player.generationProofSha256 && Absolute(execution.typeProofPath) == Absolute(player.typeProofPath) &&
                execution.typeProofSha256 == player.typeProofSha256, "M06 execution proof identity differs.");
            ValidateExecutionSchema(execution);
            input.generationProof = ReadJson<GenerationProof>(File.ReadAllText(player.generationProofPath));
            var generation = input.generationProof;
            Require(generation.schemaVersion == 1 && generation.milestone == "M06" && generation.policy == "compile-only-generator-provenance:1" &&
                generation.baselineBuildId == manifest.baselineBuildId && generation.unityVersion == player.unityVersion && generation.target == player.target &&
                generation.architecture == player.architecture && generation.developmentBuild == player.developmentBuild && generation.selectedPlanId == "P03" && generation.sourcePins != null &&
                JsonUtility.ToJson(generation.sourcePins) == JsonUtility.ToJson(snapshot.sourcePins), "M06 generation context/source pins differ.");
            Require(generation.sourcePins.schemaVersion == 1 && generation.sourcePins.unityVersion == player.unityVersion &&
                generation.sourcePins.target == player.target && generation.sourcePins.architecture == player.architecture, "M06 source-pin context differs.");
            foreach (var pin in new[] { generation.sourcePins.hybridclr, generation.sourcePins.hybridclrUnity, generation.sourcePins.il2cppPlus, generation.sourcePins.demo })
                Require(pin != null && !string.IsNullOrEmpty(pin.url) && !string.IsNullOrEmpty(pin.localPath) && pin.revision != null && pin.revision.Length == 40 &&
                    pin.revision.All(character => character >= '0' && character <= '9' || character >= 'a' && character <= 'f'), "M06 source revision is not an exact captured commit.");
            RequireSet(generation.plans.Select(row => row.planId), new[] { "Ordinary", "P01", "P02", "P03", "InitializerFailure" }, "generation plans");
            var expectedImages = new HashSet<string>(StringComparer.Ordinal);
            foreach (string role in new[] { "PlayerInput", "LinkedPlayer" })
                foreach (string name in Candidates)
                {
                    var image = execution.images.Single(row => row.role == role && row.identity.name == name);
                    expectedImages.Add(role + "|" + "|" + name);
                    Require(image.planId == "" && image.planHash == "" && image.compileSnapshotHash == player.inputSnapshotHash, "M06 Player execution image has a generation role.");
                    if (role == "LinkedPlayer")
                    {
                        var identity = player.assemblyIdentities.Single(row => row.name == name);
                        RequireSameIdentity(image.identity, identity);
                    }
                    else
                    {
                        var file = snapshot.assemblies.Single(row => row.name == name);
                        Require(image.identity.sha256 == file.sha256 && Absolute(image.identity.path) == ConfinedSnapshotPath(player.inputSnapshot, file.path), "M06 compiler execution image differs.");
                    }
                    ValidateExecutionImage(image);
                }
            var bridgeOutputs = new Dictionary<string, GenerationOutput>(StringComparer.Ordinal);
            foreach (var row in generation.plans)
            {
                VerifyBytes(row.planPath, row.planSha256, "generation plan");
                VerifyBytes(row.compilerModePath, row.compilerModeSha256, "compiler mode");
                VerifyBytes(row.executionPolicyPath, row.executionPolicySha256, "execution startup policy");
                var plan = ReadJson<GenerationPlan>(File.ReadAllText(row.planPath));
                var mode = ReadJson<CompilerModeProof>(File.ReadAllText(row.compilerModePath));
                ValidateStartupProof(ReadJson<ExecutionPolicyProof>(File.ReadAllText(row.executionPolicyPath)), row);
                string root = Path.GetDirectoryName(Absolute(row.planPath));
                var compile = JsonUtility.FromJson<SnapshotReceipt>(File.ReadAllText(Path.Combine(row.compileSnapshot, "assembly-snapshot.json")));
                Require(plan.schemaVersion == 1 && plan.kind == "CompileOnlyGeneration" && plan.purpose == "NotDeployable" && plan.planHash == row.planHash &&
                    plan.snapshotHash == row.compileSnapshotHash && compile.snapshotHash == row.compileSnapshotHash && compile.kind == "CompilePlayerScripts" &&
                    plan.target == player.target && plan.architecture == player.architecture && plan.unityVersion == player.unityVersion &&
                    JsonUtility.ToJson(plan.sourcePins) == JsonUtility.ToJson(generation.sourcePins) && JsonUtility.ToJson(compile.sourcePins) == JsonUtility.ToJson(generation.sourcePins),
                    "M06 generation plan/compiler binding differs: " + row.planId);
                VerifyBytes(Path.Combine(row.compileSnapshot, "assembly-snapshot.json"), plan.snapshotReceiptSha256, "original compiler snapshot receipt");
                VerifyBytes(Path.Combine(root, "Snapshot/assembly-snapshot.json"), plan.snapshotReceiptSha256, "plan copied snapshot receipt");
                VerifyBytes(Path.Combine(root, "policy.json"), plan.policySha256, "generation policy");
                Require(mode.schemaVersion == 1 && mode.kind == "CompilePlayerScriptsMode" && mode.developmentBuild == player.developmentBuild &&
                    mode.compilerOptions == (player.developmentBuild ? 1 : 0) && mode.snapshotHash == row.compileSnapshotHash &&
                    mode.snapshotReceiptSha256 == plan.snapshotReceiptSha256 && mode.unityVersion == player.unityVersion && mode.target == player.target && mode.architecture == player.architecture &&
                    mode.extraScriptingDefines.SequenceEqual(compile.extraScriptingDefines), "M06 actual compiler invocation mode differs.");
                VerifyBytes(Path.Combine(root, "Snapshot/compiler-mode.json"), row.compilerModeSha256, "copied compiler mode");
                RequireSet(row.defines, ExpectedDefines(row.planId), "generation defines");
                RequireSet(compile.extraScriptingDefines.Where(value => !value.StartsWith("ASSEMBLY_SHADOW_REFLECTION_BINDINGS_", StringComparison.Ordinal) &&
                    !value.StartsWith("ASSEMBLY_SHADOW_RAW_TYPE_ADMISSION_", StringComparison.Ordinal)), row.defines, "actual compiler defines");
                string[] closure = row.planId == "Ordinary" ? new string[0] : row.planId == "InitializerFailure" ? new[] { Internal } : ExpectedClosure(row.planId);
                Require(row.closureLoadOrder.SequenceEqual(closure) && plan.loadOrder.Select(CanonicalName).SequenceEqual(closure.Select(CanonicalName)), "M06 generation order differs.");
                RequireSet(plan.closure.Select(CanonicalName), closure.Select(CanonicalName), "plan closure");
                RequireSet(plan.explicitRoots.Select(CanonicalName), row.changedRoots.Select(CanonicalName), "plan roots");
                RequireSet(row.changedRoots, closure, "fixed generation changed roots");
                RequireSet(plan.catalog.Select(image => image.name), compile.assemblies.Concat(compile.references).Concat(compile.filteredAssemblies ?? new SnapshotFile[0]).Select(file => file.name), "compiler catalog");
                foreach (var image in plan.catalog) VerifyGenerationImage(root, image);
                foreach (var file in compile.assemblies.Concat(compile.references).Concat(compile.filteredAssemblies ?? new SnapshotFile[0]))
                {
                    VerifyBytes(ConfinedSnapshotPath(row.compileSnapshot, file.path), file.sha256, "original compiler DLL");
                    if (!string.IsNullOrEmpty(file.pdbPath)) VerifyBytes(ConfinedSnapshotPath(row.compileSnapshot, file.pdbPath), file.pdbSha256, "original compiler PDB");
                    var catalog = plan.catalog.Single(image => image.name == file.name);
                    Require(catalog.sha256 == file.sha256 && (catalog.pdbSha256 ?? "") == (file.pdbSha256 ?? ""), "M06 plan catalog differs from current compiler bytes.");
                }
                RequireSet(plan.images.Select(image => CanonicalName(image.name)), closure.Concat(plan.ordinaryAssemblies).Select(CanonicalName), "selected generation inputs");
                foreach (var image in plan.images)
                {
                    VerifyGenerationImage(root, image);
                    var catalog = plan.catalog.Single(file => file.name == image.name);
                    Require(image.sha256 == catalog.sha256 && image.mvid == catalog.mvid && image.assemblyIdentity == catalog.assemblyIdentity &&
                        image.path == catalog.path && image.pdbSha256 == catalog.pdbSha256, "M06 selected image differs from its compiler catalog.");
                }
                var fixture = row.planId == "Ordinary" ? null : row.planId == "InitializerFailure" ? manifest.initializerFailureFixture : manifest.fixtures.Single(item => item.patchId == row.planId);
                if (fixture != null)
                {
                    Require(fixture.developmentBuild == player.developmentBuild && fixture.compileSnapshotHash == row.compileSnapshotHash &&
                        Absolute(fixture.compileSnapshot) == Absolute(row.compileSnapshot) && Absolute(fixture.generationPlanPath) == Absolute(row.planPath) &&
                        fixture.generationPlanSha256 == row.planSha256 && fixture.closureLoadOrder.SequenceEqual(row.closureLoadOrder) &&
                        fixture.defines.SequenceEqual(row.defines) && fixture.changedRoots.SequenceEqual(row.changedRoots) &&
                        fixture.stableAotNames.SequenceEqual(manifest.stableAotNames) && fixture.requiredAotMetadataNames.SequenceEqual(row.requiredAotMetadataNames), "M06 fixture differs from its generation plan.");
                    RequireSet(fixture.assemblyIdentities.Select(identity => identity.name), closure, "fixture identity inventory");
                    foreach (string name in closure)
                    {
                        var image = execution.images.Single(item => item.role == "GenerationPlan" && item.planId == row.planId && item.identity.name == name);
                        expectedImages.Add("GenerationPlan|" + row.planId + "|" + name);
                        var compiled = plan.images.Single(item => item.name == name);
                        var patch = fixture.patch.closure.Single(item => item.name == name);
                        Require(image.compileSnapshotHash == row.compileSnapshotHash && image.planHash == row.planHash && image.identity.sha256 == compiled.sha256 &&
                            image.identity.mvid == compiled.mvid && image.identity.fullName == compiled.assemblyIdentity && patch.sha256 == compiled.sha256 && patch.mvid == compiled.mvid &&
                            Absolute(image.identity.path) == ConfinedSnapshotPath(root, compiled.path) &&
                            (player.developmentBuild ? patch.pdbSha256 == image.pdbSha256 && image.pdbSha256 == compiled.pdbSha256 : string.IsNullOrEmpty(patch.pdb)),
                            "M06 execution/deployed patch/plan bytes differ: " + name);
                        ValidateExecutionImage(image);
                    }
                    ValidateWarmupPlan(fixture);
                }
                VerifyBytes(row.aotInputPath, row.aotInputSha256, "generator AOT input");
                var aot = ReadJson<AotInputProof>(File.ReadAllText(row.aotInputPath));
                Require(aot.schemaVersion == 1 && aot.kind == "GeneratorStripInputs" && aot.planHash == plan.planHash && aot.inventoryHash == row.aotInventoryHash &&
                    aot.target == player.target && aot.architecture == player.architecture && aot.images.Length > 0, "M06 AOT input binding differs.");
                foreach (var image in aot.images) VerifyGenerationImage(Path.GetDirectoryName(row.aotInputPath), image);
                Require(row.stripBuildOptions == (536870912 | 128 | (player.developmentBuild ? 1 : 0)) && !string.IsNullOrEmpty(row.stripBuildGuid), "M06 strip build options/provenance differ.");
                ReadGenerationOutput(row.linkReceiptPath, row.linkReceiptSha256, "Link", plan, row, player);
                var bridge = ReadGenerationOutput(row.bridgeReceiptPath, row.bridgeReceiptSha256, "MethodBridge", plan, row, player);
                var generic = ReadGenerationOutput(row.aotReceiptPath, row.aotReceiptSha256, "AotGenericReference", plan, row, player);
                bridgeOutputs.Add(row.planId, bridge);
                if (row.planId == generation.selectedPlanId)
                    foreach (var output in new[] { ReadGenerationOutput(row.linkReceiptPath, row.linkReceiptSha256, "Link", plan, row, player), bridge, generic })
                    {
                        var installed = generation.installedOutputs.Single(item => item.role == output.stage);
                        string receiptPath = output.stage == "Link" ? row.linkReceiptPath : output.stage == "MethodBridge" ? row.bridgeReceiptPath : row.aotReceiptPath;
                        Require(installed.sha256 == output.outputSha256 && Absolute(installed.sourcePath) == ConfinedSnapshotPath(Path.GetDirectoryName(receiptPath), output.outputPath),
                            "M06 selected generated output is not the installed receipt's exact bytes.");
                    }
                RequireSet(generic.emittedAssemblyNames.Select(WithoutDll).Where(name => !closure.Contains(name)), row.requiredAotMetadataNames, "actual supplementary metadata collector names");
            }
            RequireSet(execution.images.Select(image => image.role + "|" + image.planId + "|" + image.identity.name), expectedImages, "execution image inventory");
            var ordinary = generation.plans.Single(row => row.planId == "Ordinary");
            Require(generation.baselineCompileSnapshotHash == ordinary.compileSnapshotHash && Absolute(generation.baselineCompileSnapshot) == Absolute(ordinary.compileSnapshot), "M06 ordinary/baseline generation differs.");
            RequireSet(generation.installedOutputs.Select(row => row.role), new[] { "Link", "MethodBridge", "AotGenericReference", "AssemblyManifest", "UnityVersion" }, "generated output roles");
            foreach (var output in generation.installedOutputs) VerifyBytes(output.sourcePath, output.sha256, "captured installed generated output");
            var placeholder = generation.installedOutputs.Single(item => item.role == "AssemblyManifest");
            Require(placeholder.sha256 == player.placeholderManifestSha256, "M06 native placeholder manifest is not the selected generation output.");
            VerifyBytes(player.placeholderManifestPath, player.placeholderManifestSha256, "native placeholder manifest");
            foreach (var required in bridgeOutputs.Values) RequireBridgeCoverage(bridgeOutputs["P03"], required);
        }

        private static void ValidateStartupProof(ExecutionPolicyProof proof, GenerationPlanProof plan)
        {
            Require(proof != null && proof.schemaVersion == 1 && proof.milestone == "M06" && proof.compileSnapshotHash == plan.compileSnapshotHash &&
                proof.bootstrapAssemblyIdentity == typeof(M06BootstrapRunner).Assembly.FullName && proof.bootstrapTypeName == typeof(M06BootstrapRunner).FullName &&
                proof.bootstrapExecutionOrder == -32000 && proof.diagnostics != null && proof.diagnostics.Length == 0 &&
                proof.files != null && proof.files.Length >= 2 && proof.scripts != null && proof.scripts.Length > 0 && proof.preloadedAssets != null,
                "M06 startup policy is incomplete or belongs to another compiler/Bootstrap.");
            RequireSet(proof.files.Select(file => file.sourcePath), proof.files.Select(file => file.sourcePath).Distinct(), "startup source uniqueness");
            RequireSet(proof.files.Select(file => file.path), proof.files.Select(file => file.path).Distinct(), "startup capture uniqueness");
            foreach (var file in proof.files) VerifyBytes(file.path, file.sha256, "captured startup input");
            Action<string, string, string> bind = (source, captured, sha) => {
                var file = proof.files.SingleOrDefault(item => item.sourcePath == source);
                Require(file != null && Absolute(file.path) == Absolute(captured) && file.sha256 == sha, "M06 startup file does not bind its captured bytes.");
            };
            bind(proof.startupSceneSourcePath, proof.startupScenePath, proof.startupSceneSha256);
            bind(proof.bootstrapScriptSourcePath, proof.bootstrapScriptPath, proof.bootstrapScriptSha256);
            foreach (var script in proof.scripts)
            {
                bind(script.assetSourcePath, script.assetPath, script.assetSha256);
                bind(script.scriptSourcePath, script.scriptPath, script.scriptSha256);
                Require(!script.isCandidate && !Candidates.Contains(new AssemblyName(script.assemblyIdentity).Name) && script.callbacks != null && script.dependencyEvidence != null &&
                    (script.phase == "StartupScene" || script.phase == "PreloadedAsset"), "M06 candidate/unknown startup script cannot execute before publication.");
                Require(script.isBootstrapRunner == (script.assemblyIdentity == proof.bootstrapAssemblyIdentity && script.typeName == proof.bootstrapTypeName), "M06 startup Bootstrap role differs from its actual identity.");
                if (script.isBootstrapRunner)
                    Require(script.phase == "StartupScene" && script.assetSourcePath == proof.startupSceneSourcePath && script.scriptSourcePath == proof.bootstrapScriptSourcePath &&
                        script.executionOrder == proof.bootstrapExecutionOrder && script.callbacks.Contains("Awake"), "M06 Bootstrap is not the captured initial scene gate.");
                else if (script.callbacks.Length > 0 && (script.phase == "PreloadedAsset" || script.executionOrder <= proof.bootstrapExecutionOrder))
                    Require(script.dependencyProved && !script.isCandidateDependent, "M06 early startup callback is not independently proved candidate-free.");
            }
            Require(proof.scripts.Any(script => script.isBootstrapRunner), "M06 startup scene has no actual Bootstrap gate.");
            foreach (var asset in proof.preloadedAssets)
            {
                bind(asset.sourcePath, asset.assetPath, asset.sha256);
                Require(!asset.isCandidate && !Candidates.Contains(new AssemblyName(asset.assemblyIdentity).Name) && !string.IsNullOrEmpty(asset.typeName), "M06 preloaded asset has a candidate identity.");
            }
        }

        private static string LinkedReceiptHash(LinkedPlayerReceipt receipt)
        {
            Require(receipt != null && (receipt.schemaVersion == 1 || receipt.schemaVersion == 2), "M06 linked receipt schema differs.");
            var text = new StringBuilder("assembly-shadow-linked-player:" + receipt.schemaVersion + "\n");
            text.Append(receipt.schemaVersion).Append('\n').Append(receipt.buildGuid).Append('\n').Append(receipt.nativeLibrarySha256).Append('\n')
                .Append(receipt.target).Append('\n').Append(receipt.architecture).Append('\n').Append(receipt.sourceDirectory).Append('\n');
            if (receipt.schemaVersion == 2) text.Append("reflection-bindings:").Append(receipt.reflectionBindingEvidenceHash).Append('\n');
            foreach (string name in receipt.protectedAssemblies.OrderBy(name => name, StringComparer.Ordinal)) text.Append("protected:").Append(name).Append('\n');
            foreach (var file in receipt.assemblies.OrderBy(file => file.path, StringComparer.Ordinal))
                text.Append(file.name).Append('\n').Append(file.path).Append('\n').Append(file.sha256).Append('\n').Append(file.mvid).Append('\n').Append(file.pdbPath).Append('\n').Append(file.pdbSha256).Append('\n');
            return Hash(Encoding.UTF8.GetBytes(text.ToString()));
        }

        private static void RequireSet(IEnumerable<string> actual, IEnumerable<string> expected, string label)
        {
            Require(actual != null && expected != null, "M06 missing " + label);
            var a = actual.ToArray(); var e = expected.ToArray();
            Require(a.All(value => !string.IsNullOrEmpty(value)) && a.Distinct(StringComparer.Ordinal).Count() == a.Length &&
                e.Distinct(StringComparer.Ordinal).Count() == e.Length && a.OrderBy(value => value, StringComparer.Ordinal).SequenceEqual(e.OrderBy(value => value, StringComparer.Ordinal)),
                "M06 exact " + label + " differs.");
        }
        private static void RequireCanonicalSet(IEnumerable<string> actual, IEnumerable<string> expected, string label)
        {
            Require(actual != null && expected != null, "M06 missing " + label);
            RequireSet(actual.Select(AssemblyTransportKey), expected.Select(AssemblyTransportKey), label);
        }
        private static string AssemblyTransportKey(string name)
        {
            Require(!string.IsNullOrWhiteSpace(name) && name == name.Trim() && name.IndexOfAny(new[] { '/', '\\', ',' }) < 0,
                "M06 invalid assembly transport name.");
            return CanonicalName(name);
        }
        private static M04ReferenceProbe.AssemblyIdentity LinkedIdentity(PlayerBuildReceipt player, LinkedPlayerFile file)
        {
            string key = AssemblyTransportKey(file.name);
            var identities = player.assemblyIdentities.Where(item => AssemblyTransportKey(item.name) == key).ToArray();
            var native = player.nativeAssemblyIdentities.Where(item => AssemblyTransportKey(item.name) == key).ToArray();
            Require(identities.Length == 1 && native.Length == 1, "M06 linked/native assembly transport identity is absent or ambiguous: " + file.name);
            var identity = identities[0];
            Require(new AssemblyName(identity.fullName).Name == identity.name && native[0].name == identity.name &&
                native[0].fullName == identity.fullName && native[0].imageName == identity.name + ".dll", "M06 native metadata identity differs: " + file.name);
            return identity;
        }
        private static string CanonicalName(string value) { return WithoutDll(value).ToLowerInvariant(); }
        private static string WithoutDll(string value) { return value.EndsWith(".dll", StringComparison.OrdinalIgnoreCase) ? value.Substring(0, value.Length - 4) : value; }
        private static string[] ExpectedDefines(string id)
        {
            if (id == "Ordinary") return new string[0];
            var result = new List<string> { "ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_M06" };
            if (id == "P02") result.AddRange(new[] { "ASSEMBLY_SHADOW_P02", "ASSEMBLY_SHADOW_M06_P02" });
            if (id == "P03") result.AddRange(new[] { "ASSEMBLY_SHADOW_P03", "ASSEMBLY_SHADOW_M06_P03" });
            if (id == "InitializerFailure") result.Add("ASSEMBLY_SHADOW_M06_INITIALIZER_THROW");
            return result.ToArray();
        }
        private static void RequireSameIdentity(M04ReferenceProbe.AssemblyIdentity a, M04ReferenceProbe.AssemblyIdentity b)
        { Require(a.name == b.name && a.fullName == b.fullName && a.mvid == b.mvid && a.sha256 == b.sha256 && Absolute(a.path) == Absolute(b.path), "M06 physical image identity differs."); }
        private static void VerifyGenerationImage(string root, GenerationImage image)
        {
            Require(image != null && !string.IsNullOrEmpty(image.name) && !string.IsNullOrEmpty(image.assemblyIdentity) && !string.IsNullOrEmpty(image.mvid), "M06 generation image identity missing.");
            VerifyBytes(ConfinedSnapshotPath(root, image.path), image.sha256, "generation image " + image.name);
            if (!string.IsNullOrEmpty(image.pdbPath)) VerifyBytes(ConfinedSnapshotPath(root, image.pdbPath), image.pdbSha256, "generation PDB");
            else Require(string.IsNullOrEmpty(image.pdbSha256), "M06 orphan generation PDB hash.");
        }

        private static void ValidateExecutionSchema(ExecutionProof proof)
        {
            string[] api = typeof(AssemblyShadowRuntime).GetMethods(BindingFlags.Public | BindingFlags.Static | BindingFlags.DeclaredOnly)
                .Select(method => method.ReturnType.FullName + " " + typeof(AssemblyShadowRuntime).FullName + "::" + method.Name + "(" +
                    string.Join(",", method.GetParameters().Select(parameter => parameter.ParameterType.FullName)) + ")").ToArray();
            Require(api.Length == 11, "M06 runtime API inventory changed."); RequireSet(proof.apiSignatures, api, "execution API signatures");
            string[] errors = Enum.GetNames(typeof(AssemblyShadowErrorCode));
            Require(errors.Length == 22 && proof.errorCodes != null && proof.errorCodes.Length == 22, "M06 error-code inventory changed.");
            RequireSet(proof.errorCodes.Select(row => row.name), errors, "error-code names");
            foreach (var row in proof.errorCodes) Require(row.value == (int)Enum.Parse(typeof(AssemblyShadowErrorCode), row.name), "M06 error-code number changed.");
            Require(proof.schemaTypes != null && proof.schemaTypes.Length > 0, "M06 preserved DTO schema evidence missing.");
            RequireSet(proof.schemaTypes.Select(row => row.side + "|" + row.typeName), proof.schemaTypes.Select(row => row.side + "|" + row.typeName).Distinct(), "DTO schema uniqueness");
            foreach (var before in proof.schemaTypes.Where(row => row.side == "PlayerInput"))
            {
                var after = proof.schemaTypes.Single(row => row.side == "LinkedPlayer" && row.typeName == before.typeName);
                ValidateSchemaPair(before, after);
            }
            Require(proof.schemaTypes.Count(row => row.side == "PlayerInput") * 2 == proof.schemaTypes.Length, "M06 unknown/unpaired DTO schema roles.");
            var pending = new Queue<Type>(new[] { typeof(Result), typeof(FixtureManifest), typeof(PlayerBuildReceipt), typeof(TypeProof), typeof(ExecutionProof),
                typeof(GenerationProof), typeof(GenerationPlan), typeof(CompilerModeProof), typeof(GenerationOutput), typeof(AotInputProof), typeof(LinkedPlayerReceipt), typeof(ExecutionPolicyProof) });
            var inspected = new HashSet<Type>();
            while (pending.Count > 0)
            {
                Type type = pending.Dequeue();
                if (type.IsArray) { pending.Enqueue(type.GetElementType()); continue; }
                if (type.IsGenericType && type.GetGenericTypeDefinition() == typeof(List<>)) { pending.Enqueue(type.GetGenericArguments()[0]); continue; }
                if (type.IsPrimitive || type == typeof(string) || !inspected.Add(type)) continue;
                FieldInfo[] fields = type.GetFields(BindingFlags.Public | BindingFlags.Instance).Where(field => !field.IsNotSerialized).ToArray();
                foreach (string side in new[] { "PlayerInput", "LinkedPlayer" })
                {
                    var row = proof.schemaTypes.Single(item => item.side == side && item.typeName == type.FullName.Replace('+', '/'));
                    Require(row.assemblyIdentity == type.Assembly.FullName, "M06 loaded fixed DTO assembly differs from captured schema.");
                    ValidateSchemaFields(row, type);
                }
                foreach (FieldInfo field in fields) pending.Enqueue(field.FieldType);
            }
            foreach (Type type in new[] { typeof(AssemblyShadowExecutionDiagnostics), typeof(AssemblyShadowExecutionClassInfo) })
                foreach (string side in new[] { "PlayerInput", "LinkedPlayer" })
                {
                    var row = proof.schemaTypes.Single(item => item.side == side && item.typeName == type.FullName);
                    ValidateSchemaFields(row, type);
                    Require(row.fields.Length == (type == typeof(AssemblyShadowExecutionDiagnostics) ? 14 : 12), "M06 execution diagnostic schema count differs.");
                }
        }

        private static void ValidateSchemaFields(SchemaType row, Type type)
        {
            // Each side retains its declared AQN as byte-bound evidence above.
            // The producer resolves it through the captured target runtime catalog;
            // reflection exposes that definition identity, not a compiler facade.
            Require(row.fields != null && row.fields.All(field => field != null && !string.IsNullOrEmpty(field.type) && !string.IsNullOrEmpty(field.resolvedType)),
                "M06 declared/resolved field identity is missing.");
            RequireSet(row.fields.Select(field => field.name + "|" + field.resolvedType), type.GetFields(BindingFlags.Public | BindingFlags.Instance)
                .Where(field => !field.IsNotSerialized).Select(field => field.Name + "|" + field.FieldType.AssemblyQualifiedName), "assembly-qualified DTO field graph");
        }

        private static void ValidateSchemaPair(SchemaType before, SchemaType after)
        {
            Require(before != null && after != null && before.isSerializable && after.isSerializable && before.assemblyIdentity == after.assemblyIdentity &&
                before.fields != null && before.fields.Length > 0 && after.fields != null &&
                before.fields.Concat(after.fields).All(field => field != null && !string.IsNullOrEmpty(field.type) && !string.IsNullOrEmpty(field.resolvedType)) &&
                before.fields.Select(field => field.name + "|" + field.resolvedType + "|" + field.attributes).OrderBy(value => value, StringComparer.Ordinal)
                    .SequenceEqual(after.fields.Select(field => field.name + "|" + field.resolvedType + "|" + field.attributes).OrderBy(value => value, StringComparer.Ordinal)),
                "M06 linked DTO resolved field preservation differs.");
        }

        private static void ValidateExecutionImage(ExecutionImage image)
        {
            Require(image != null && image.identity != null && Candidates.Contains(image.identity.name) && image.methods != null && image.methods.Length > 0,
                "M06 execution method/image inventory missing.");
            VerifyBytes(image.identity.path, image.identity.sha256, "execution image");
            Require(!string.IsNullOrEmpty(image.identity.fullName) && !string.IsNullOrEmpty(image.identity.mvid) &&
                image.methods.Select(method => method.metadataToken).Distinct().Count() == image.methods.Length, "M06 execution identity/method token is ambiguous.");
            Require(image.pdbAvailable == !string.IsNullOrEmpty(image.pdbPath), "M06 execution symbol availability differs.");
            if (image.pdbAvailable) VerifyBytes(image.pdbPath, image.pdbSha256, "execution PDB"); else Require(string.IsNullOrEmpty(image.pdbSha256), "M06 orphan execution symbol hash.");
            foreach (var method in image.methods)
            {
                Require(method != null && (method.metadataToken & unchecked((int)0xff000000)) == 0x06000000 && (method.metadataToken & 0xffffff) != 0 &&
                    !string.IsNullOrEmpty(method.declaringType) && !string.IsNullOrEmpty(method.signature) && !string.IsNullOrEmpty(method.name) &&
                    method.returnType != null && !string.IsNullOrEmpty(method.returnType.type) && method.parameterTypes != null && method.genericParameterNames != null &&
                    method.genericParameterNames.Length == method.genericArity && method.locals != null && method.instructions != null && method.exceptionHandlers != null && method.sequencePoints != null &&
                    method.hasBody == (method.instructions.Length > 0) && method.isStatic == ((method.methodFlags & 0x10) != 0), "M06 malformed actual method definition.");
                foreach (var point in method.sequencePoints) Require(image.pdbAvailable && point.instructionIndex >= 0 && point.instructionIndex < method.instructions.Length &&
                    point.ilOffset >= 0 && !string.IsNullOrEmpty(point.document) && point.startLine > 0, "M06 malformed method PDB evidence.");
            }
            string witness = WitnessName(image.identity.name);
            foreach (string name in new[] { "Run", "GetModuleEvidence", "RunAsync", "RunCoroutine", "WarmupValue", "WarmupEcho", "ThrowForEvidence" })
                Require(image.methods.Count(method => method.declaringType == witness && method.name == name && method.isStatic && method.hasBody) == 1, "M06 finite witness selector missing/ambiguous: " + name);
        }

        private static GenerationOutput ReadGenerationOutput(string path, string sha, string stage, GenerationPlan plan, GenerationPlanProof row, PlayerBuildReceipt player)
        {
            VerifyBytes(path, sha, "generation output receipt");
            var output = ReadJson<GenerationOutput>(File.ReadAllText(path));
            Require(output.schemaVersion == 1 && output.kind == "GenerationOutput" && output.stage == stage && output.planHash == plan.planHash &&
                output.target == player.target && output.architecture == player.architecture && IsHash(output.outputHash) &&
                (stage == "Link" ? string.IsNullOrEmpty(output.aotInventoryHash) && output.maxIterations == 0 : output.aotInventoryHash == row.aotInventoryHash && output.maxIterations > 0 && output.maxIterations <= 20) &&
                (stage != "MethodBridge" || output.development == player.developmentBuild), "M06 generator output binding differs.");
            VerifyBytes(ConfinedSnapshotPath(Path.GetDirectoryName(path), output.outputPath), output.outputSha256, "actual generated bytes");
            Require(output.resolverCatalog != null && output.resolverCatalog.Length > 0 && output.collectorRoots != null && output.collectorTypes != null && output.collectorMethods != null &&
                output.reverseMethods != null && output.nativeCallSignatures != null && output.aotTypes != null && output.aotMethods != null && output.emittedAssemblyNames != null &&
                output.managedToNative != null && output.nativeToManaged != null && output.adjustThunks != null && output.reversePInvoke != null && output.calli != null && output.structMappings != null,
                "M06 generator inventories are missing.");
            foreach (var image in output.resolverCatalog) VerifyGenerationImage(image.role == "StrippedAot" ? Path.GetDirectoryName(row.aotInputPath) : Path.GetDirectoryName(row.planPath), image);
            return output;
        }

        private static void RequireBridgeCoverage(GenerationOutput selected, GenerationOutput required)
        {
            Require(selected.development == required.development && selected.target == required.target && selected.architecture == required.architecture &&
                selected.templateSha256 == required.templateSha256 && selected.nativePointerDispatchHasMethodInfo == required.nativePointerDispatchHasMethodInfo &&
                selected.reversePInvokeGuardPolicy == required.reversePInvokeGuardPolicy, "M06 bridge ABI policy/context differs across plans.");
            var selectedGroups = new[] { selected.managedToNative, selected.nativeToManaged, selected.adjustThunks, selected.reversePInvoke, selected.calli };
            var requiredGroups = new[] { required.managedToNative, required.nativeToManaged, required.adjustThunks, required.reversePInvoke, required.calli };
            for (int index = 0; index < selectedGroups.Length; ++index)
                foreach (var entry in requiredGroups[index]) Require(entry.capacity > 0 && selectedGroups[index].Any(candidate => candidate.abi == entry.abi && candidate.capacity >= entry.capacity), "M06 selected P03 generator output misses an actual ABI/capacity.");
            foreach (var entry in required.structMappings) Require(selected.structMappings.Any(candidate => candidate.key == entry.key && candidate.abi == entry.abi), "M06 selected generator output misses a runtime struct mapping.");
        }

        private static string WitnessName(string assembly)
        {
            switch (assembly)
            {
                case Contracts: case Extensibility: case Internal: return assembly + ".M06ExecutionWitness";
                case ContractsConsumer: return "AssemblyShadowDemo.Consumers.ContractsM06ExecutionWitness";
                case ExtensibilityConsumer: return "AssemblyShadowDemo.Consumers.ExtensibilityM06ExecutionWitness";
                default: throw new InvalidOperationException("M06 unknown literal witness name.");
            }
        }

        private static void ValidateWarmupPlan(Fixture fixture)
        {
            if (fixture.warmup == null) { Require(!ModeIsWarmup(Argument("-shadowM06Mode", "")), "M06 warmup requires an explicit schema-2 manifest."); return; }
            Require(fixture.warmup.types.Select(row => row.assembly).SequenceEqual(fixture.closureLoadOrder) && fixture.warmup.methods.Length == fixture.closureLoadOrder.Length * 4,
                "M06 warmup envelope does not cover its exact closure.");
            foreach (var type in fixture.warmup.types)
            {
                Require(type.type == WitnessName(type.assembly), "M06 warmup type is not the finite witness.");
                var owner = fixture.assemblyIdentities.Single(identity => identity != null && identity.name == type.assembly);
                var methods = fixture.warmup.methods.Where(row => row.assembly == type.assembly).ToArray();
                RequireSet(methods.Select(row => row.name + "|" + row.returnType.type), new[] { "WarmupValue|System.Int32", "WarmupEcho|System.Int32", "WarmupEcho|System.String", "Run|System.String[]" }, "warmup literal methods");
                foreach (var method in methods)
                {
                    Require(method.declaringType == type.type && method.isStatic && method.genericArity == (method.name == "WarmupEcho" ? 1 : 0) &&
                        method.genericArguments != null && method.genericArguments.Length == method.genericArity && method.parameterTypes != null && method.parameterTypes.Length == 1 &&
                        method.parameterTypes[0].assembly == method.returnType.assembly && method.parameterTypes[0].type == (method.name == "Run" ? "System.String" : method.returnType.type) &&
                        (method.genericArity == 0 || method.genericArguments[0].assembly == method.returnType.assembly && method.genericArguments[0].type == method.returnType.type), "M06 warmup structured signature differs.");
                    RequireWarmupCompilerIdentity(owner, method.returnType);
                    RequireWarmupCompilerIdentity(owner, method.parameterTypes[0]);
                    foreach (var argument in method.genericArguments) RequireWarmupCompilerIdentity(owner, argument);
                }
            }
        }

        private static void RequireWarmupCompilerIdentity(M04ReferenceProbe.AssemblyIdentity owner, WarmupTypeIdentity identity)
        {
            Require(owner != null && owner.referenceIdentities != null && identity != null && !string.IsNullOrEmpty(identity.assembly) &&
                (identity.type == "System.Int32" || identity.type == "System.String" || identity.type == "System.String[]") &&
                owner.referenceIdentities.Any(reference => reference != null && reference.fullName == identity.assembly),
                "M06 warmup signature identity is not an exact compiler reference of its captured owner.");
        }

        private static void VerifyBytes(string path, string expectedHash, string label)
        {
            string absolute = Absolute(path);
            Require(File.Exists(absolute) && HashFile(absolute) == expectedHash, "M06 " + label + " bytes/hash mismatch.");
        }

        private static void ValidatePlayerSnapshot(PlayerBuildReceipt player)
        {
            string root = Absolute(player.inputSnapshot);
            string receiptPath = Path.Combine(root, "assembly-snapshot.json");
            Require(File.Exists(receiptPath), "M06 Player assembly snapshot receipt is missing.");
            SnapshotReceipt snapshot = JsonUtility.FromJson<SnapshotReceipt>(File.ReadAllText(receiptPath));
            Require(snapshot != null && snapshot.schemaVersion == 1 && snapshot.kind == "PlayerBuildInputs" && snapshot.snapshotHash == player.inputSnapshotHash &&
                snapshot.playerBuildSucceeded && snapshot.playerBuildFilterCaptured && snapshot.buildGuid == player.buildGuid &&
                snapshot.playerBuildOptions == player.buildOptions && Path.GetFullPath(snapshot.nativeLibraryPath) == Path.GetFullPath(player.nativeLibraryPath) &&
                snapshot.nativeLibrarySha256 == player.nativeLibrarySha256 && snapshot.assemblies != null && snapshot.assemblies.Length > 0,
                "M06 Player assembly snapshot identity is incomplete.");
            foreach (SnapshotFile file in (snapshot.assemblies ?? new SnapshotFile[0]).Concat(snapshot.references ?? new SnapshotFile[0]).Concat(snapshot.filteredAssemblies ?? new SnapshotFile[0]))
            {
                Require(file != null && !string.IsNullOrEmpty(file.name) && IsHash(file.sha256), "M06 Player assembly snapshot file identity is incomplete.");
                VerifyBytes(ConfinedSnapshotPath(root, file.path), file.sha256, "Player snapshot " + file.name);
                if (!string.IsNullOrEmpty(file.pdbPath))
                {
                    Require(IsHash(file.pdbSha256), "M06 Player snapshot PDB hash is missing: " + file.name);
                    VerifyBytes(ConfinedSnapshotPath(root, file.pdbPath), file.pdbSha256, "Player snapshot PDB " + file.name);
                }
                else Require(string.IsNullOrEmpty(file.pdbSha256), "M06 Player snapshot has an unbound PDB hash: " + file.name);
            }
            ValidateSnapshotControl(root, snapshot.extraScriptingDefines, "ASSEMBLY_SHADOW_REFLECTION_BINDINGS_", "ReflectionBindings/configuration.json");
            ValidateSnapshotControl(root, snapshot.extraScriptingDefines, "ASSEMBLY_SHADOW_RAW_TYPE_ADMISSION_", "RawTypeAdmissions/configuration.json");
        }

        private static void ValidateSnapshotControl(string root, string[] defines, string prefix, string relativePath)
        {
            string[] controls = (defines ?? new string[0]).Where(value => value != null && value.StartsWith(prefix, StringComparison.Ordinal)).ToArray();
            Require(controls.Length == 1 && IsHash(controls[0].Substring(prefix.Length)), "M06 Player snapshot control is missing or ambiguous: " + prefix);
            VerifyBytes(ConfinedSnapshotPath(root, relativePath), controls[0].Substring(prefix.Length), "Player snapshot control " + prefix);
        }

        private static string ConfinedSnapshotPath(string root, string relativePath)
        {
            Require(!string.IsNullOrEmpty(relativePath) && !Path.IsPathRooted(relativePath), "M06 snapshot paths must be relative to the verified snapshot root.");
            string normalizedRoot = Path.GetFullPath(root);
            string path = Path.GetFullPath(Path.Combine(normalizedRoot, relativePath));
            string prefix = normalizedRoot.EndsWith(Path.DirectorySeparatorChar.ToString(), StringComparison.Ordinal) ? normalizedRoot : normalizedRoot + Path.DirectorySeparatorChar;
            Require(path.StartsWith(prefix, StringComparison.Ordinal), "M06 snapshot path escapes its verified root: " + relativePath);
            return path;
        }

        [Serializable, Preserve] public sealed class GenerationProof
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string milestone, policy;
            [Preserve] public string baselineBuildId, unityVersion, target, architecture, baselineCompileSnapshot, baselineCompileSnapshotHash, selectedPlanId;
            [Preserve] public bool developmentBuild;
            [Preserve] public SourcePins sourcePins;
            [Preserve] public GenerationPlanProof[] plans;
            [Preserve] public InstalledOutput[] installedOutputs;
        }

        [Serializable, Preserve] public sealed class GenerationPlanProof
        {
            [Preserve] public string planId, compileSnapshot, compileSnapshotHash, planPath, planSha256, planHash;
            [Preserve] public string compilerModePath, compilerModeSha256;
            [Preserve] public string executionPolicyPath, executionPolicySha256, aotInputPath, aotInputSha256, aotInventoryHash;
            [Preserve] public string stripBuildGuid, stripOutput, stripSourceDirectory;
            [Preserve] public int stripBuildOptions;
            [Preserve] public string linkReceiptPath, linkReceiptSha256, bridgeReceiptPath, bridgeReceiptSha256, aotReceiptPath, aotReceiptSha256;
            [Preserve] public string[] defines, changedRoots, closureLoadOrder, requiredAotMetadataNames;
        }

        [Serializable, Preserve] public sealed class InstalledOutput
        {
            [Preserve] public string role, sourcePath, destinationPath, sha256;
        }

        [Serializable, Preserve] public sealed class ExecutionPolicyProof
        {
            [Preserve] public int schemaVersion, bootstrapExecutionOrder;
            [Preserve] public string milestone, compileSnapshotHash, startupScenePath, startupSceneSha256;
            [Preserve] public string bootstrapScriptPath, bootstrapScriptSha256, bootstrapAssemblyIdentity, bootstrapTypeName;
            [Preserve] public string startupSceneSourcePath, bootstrapScriptSourcePath;
            [Preserve] public StartupFile[] files;
            [Preserve] public StartupScript[] scripts;
            [Preserve] public PreloadedAsset[] preloadedAssets;
            [Preserve] public string[] diagnostics;
        }
        [Serializable, Preserve] public sealed class StartupFile
        { [Preserve] public string sourcePath, path, sha256; }
        [Serializable, Preserve] public sealed class StartupScript
        {
            [Preserve] public string rootAssetPath, assetPath, scriptPath, assemblyIdentity, typeName, phase, assetSha256, scriptSha256;
            [Preserve] public string assetSourcePath, scriptSourcePath;
            [Preserve] public int executionOrder;
            [Preserve] public bool isCandidate, isBootstrapRunner, isCandidateDependent, dependencyProved;
            [Preserve] public string[] callbacks, dependencyEvidence;
        }
        [Serializable, Preserve] public sealed class PreloadedAsset
        { [Preserve] public string assetPath, sourcePath, typeName, assemblyIdentity, sha256; [Preserve] public bool isCandidate; }

        [Serializable, Preserve] public sealed class SourcePins
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string unityVersion;
            [Preserve] public string target;
            [Preserve] public string architecture;
            [Preserve] public RepositoryPin hybridclr;
            [Preserve] public RepositoryPin hybridclrUnity;
            [Preserve] public RepositoryPin il2cppPlus;
            [Preserve] public RepositoryPin demo;
        }

        [Serializable, Preserve] public sealed class RepositoryPin
        {
            [Preserve] public string url;
            [Preserve] public string revision;
            [Preserve] public string localPath;
        }

        [Serializable, Preserve] public sealed class GenerationPlan
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string kind;
            [Preserve] public string purpose;
            [Preserve] public string target, architecture, unityVersion, snapshotHash, snapshotReceiptSha256, policySha256, planHash;
            [Preserve] public SourcePins sourcePins;
            [Preserve] public string[] explicitRoots, closure, loadOrder, ordinaryAssemblies;
            [Preserve] public GenerationImage[] images, catalog;
        }

        [Serializable, Preserve] public sealed class GenerationImage
        {
            [Preserve] public string name, assemblyIdentity, mvid, path, sha256, pdbPath, pdbSha256, sourcePath, role;
        }

        [Serializable, Preserve] public sealed class GenerationOutput
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string kind;
            [Preserve] public string planHash, aotInventoryHash, stage, target, architecture, templateSha256, outputPath, outputSha256, outputHash;
            [Preserve] public bool development;
            [Preserve] public int maxIterations;
            [Preserve] public bool nativePointerDispatchHasMethodInfo;
            [Preserve] public string reversePInvokeGuardPolicy;
            [Preserve] public string[] collectorRoots, collectorTypes, collectorMethods, reverseMethods, nativeCallSignatures, aotTypes, aotMethods, emittedAssemblyNames;
            [Preserve] public GenerationImage[] resolverCatalog;
            [Preserve] public GenerationAbiEntry[] managedToNative, nativeToManaged, adjustThunks, reversePInvoke, calli, structMappings;
        }

        [Serializable, Preserve] public sealed class GenerationAbiEntry
        {
            [Preserve] public string key, abi;
            [Preserve] public int capacity;
        }

        [Serializable, Preserve] public sealed class AotInputProof
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string kind;
            [Preserve] public string planHash, target, architecture, sourceDirectory, inventoryHash;
            [Preserve] public string[] excludedSelectedNames;
            [Preserve] public GenerationImage[] images;
        }

        [Serializable, Preserve] public sealed class CompilerModeProof
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string kind;
            [Preserve] public bool developmentBuild;
            [Preserve] public int compilerOptions;
            [Preserve] public string unityVersion, target, architecture, snapshotHash, snapshotReceiptSha256;
            [Preserve] public string[] extraScriptingDefines;
        }

        [Serializable, Preserve] public sealed class LinkedPlayerReceipt
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string buildGuid, nativeLibrarySha256, target, architecture, sourceDirectory;
            [Preserve] public string reflectionBindingEvidenceHash;
            [Preserve] public string[] protectedAssemblies;
            [Preserve] public LinkedPlayerFile[] assemblies;
        }

        [Serializable, Preserve] public sealed class LinkedPlayerFile
        {
            [Preserve] public string name, path, sha256, mvid, pdbPath, pdbSha256;
        }

        private static T ReadJson<T>(string json)
        {
            Type root = typeof(T);
            Require(new[] { typeof(FixtureManifest), typeof(PlayerBuildReceipt), typeof(TypeProof), typeof(ExecutionProof), typeof(GenerationProof),
                typeof(GenerationPlan), typeof(CompilerModeProof), typeof(GenerationOutput), typeof(AotInputProof), typeof(LinkedPlayerReceipt), typeof(ExecutionPolicyProof), typeof(Result) }.Contains(root),
                "M06 JSON root is not in the finite preserved input inventory.");
            object value = new ProofJsonReader(json).Read();
            ValidateJsonShape(value, root, root.Name);
            return JsonUtility.FromJson<T>(json);
        }

        private static void ValidateJsonShape(object value, Type type, string path)
        {
            if (value == null) { Require(!type.IsValueType, "M06 null scalar: " + path); return; }
            if (type == typeof(string)) { Require(value is string, "M06 expected string: " + path); return; }
            if (type == typeof(bool)) { Require(value is bool, "M06 expected Boolean: " + path); return; }
            if (type == typeof(int) || type == typeof(uint) || type == typeof(long) || type == typeof(ulong))
            {
                var number = value as ProofNumber; long signed; ulong unsigned; int integer; uint unsignedInteger;
                Require(number != null && (type == typeof(int) ? int.TryParse(number.text, NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out integer) :
                    type == typeof(uint) ? uint.TryParse(number.text, NumberStyles.None, CultureInfo.InvariantCulture, out unsignedInteger) : type == typeof(long) ? long.TryParse(number.text, NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out signed) :
                    ulong.TryParse(number.text, NumberStyles.None, CultureInfo.InvariantCulture, out unsigned)), "M06 exact integer token required: " + path);
                return;
            }
            if (type.IsArray || (type.IsGenericType && type.GetGenericTypeDefinition() == typeof(List<>)))
            {
                var array = value as List<object>; Require(array != null, "M06 expected array: " + path);
                Type element = type.IsArray ? type.GetElementType() : type.GetGenericArguments()[0];
                foreach (object item in array) ValidateJsonShape(item, element, path + "[]");
                return;
            }
            var fields = type.GetFields(BindingFlags.Public | BindingFlags.Instance).Where(field => !field.IsNotSerialized).ToArray();
            var row = value as Dictionary<string, object>;
            Require(row != null && row.Count == fields.Length && fields.All(field => row.ContainsKey(field.Name)), "M06 missing/unknown JSON fields: " + path);
            foreach (FieldInfo field in fields) ValidateJsonShape(row[field.Name], field.FieldType, path + "." + field.Name);
        }

        private sealed class ProofNumber { internal string text; }
        private sealed class ProofJsonReader
        {
            private readonly string json; private int position;
            internal ProofJsonReader(string json) { Require(json != null && json.Length > 0 && json.Length <= 128 * 1024 * 1024, "M06 JSON size invalid."); this.json = json; }
            internal object Read() { object value = Value(0); White(); Require(position == json.Length, "M06 trailing JSON."); return value; }
            private object Value(int depth)
            {
                Require(depth < 64, "M06 JSON nesting limit exceeded."); White(); Require(position < json.Length, "M06 truncated JSON.");
                if (json[position] == '"') return String();
                if (Take('{'))
                {
                    var row = new Dictionary<string, object>(StringComparer.Ordinal);
                    if (!Take('}')) { do { string key = String(); Require(!row.ContainsKey(key), "M06 duplicate JSON field: " + key); Expect(':'); row.Add(key, Value(depth + 1)); } while (Take(',')); Expect('}'); }
                    return row;
                }
                if (Take('['))
                {
                    var array = new List<object>(); if (!Take(']')) { do { array.Add(Value(depth + 1)); } while (Take(',')); Expect(']'); } return array;
                }
                if (Literal("true")) return true; if (Literal("false")) return false; if (Literal("null")) return null;
                int start = position;
                if (position < json.Length && json[position] == '-') ++position;
                Require(position < json.Length && char.IsDigit(json[position]) && json[position] <= '9', "M06 invalid JSON token.");
                bool zero = json[position] == '0'; ++position;
                while (position < json.Length && json[position] >= '0' && json[position] <= '9') { Require(!zero, "M06 JSON integer has leading zero."); ++position; }
                // All admitted DTO numbers are exact integers; reject floating point/exponent coercions.
                return new ProofNumber { text = json.Substring(start, position - start) };
            }
            private string String()
            {
                Expect('"'); var text = new StringBuilder();
                while (position < json.Length)
                {
                    char c = json[position++]; if (c == '"')
                    {
                        string result = text.ToString();
                        for (int i = 0; i < result.Length; ++i) if (char.IsHighSurrogate(result[i])) { Require(++i < result.Length && char.IsLowSurrogate(result[i]), "M06 invalid surrogate."); } else Require(!char.IsLowSurrogate(result[i]), "M06 invalid surrogate.");
                        return result;
                    }
                    Require(c >= ' ', "M06 unescaped JSON control character.");
                    if (c != '\\') { text.Append(c); continue; }
                    Require(position < json.Length, "M06 truncated JSON escape."); c = json[position++];
                    switch (c)
                    {
                        case '"': case '\\': case '/': text.Append(c); break;
                        case 'b': text.Append('\b'); break; case 'f': text.Append('\f'); break; case 'n': text.Append('\n'); break; case 'r': text.Append('\r'); break; case 't': text.Append('\t'); break;
                        case 'u':
                            Require(position + 4 <= json.Length, "M06 truncated Unicode escape."); int code;
                            Require(int.TryParse(json.Substring(position, 4), NumberStyles.AllowHexSpecifier, CultureInfo.InvariantCulture, out code), "M06 invalid Unicode escape.");
                            text.Append((char)code); position += 4; break;
                        default: throw new InvalidOperationException("M06 invalid JSON escape.");
                    }
                }
                throw new InvalidOperationException("M06 unterminated JSON string.");
            }
            private bool Literal(string value) { White(); if (position + value.Length > json.Length || string.CompareOrdinal(json, position, value, 0, value.Length) != 0) return false; position += value.Length; return true; }
            private void White() { while (position < json.Length && (json[position] == ' ' || json[position] == '\r' || json[position] == '\n' || json[position] == '\t')) ++position; }
            private bool Take(char c) { White(); if (position == json.Length || json[position] != c) return false; ++position; return true; }
            private void Expect(char c) { Require(Take(c), "M06 expected JSON punctuation: " + c); }
        }

        private static string Absolute(string path) { return string.IsNullOrEmpty(path) ? "" : Path.GetFullPath(path); }
        private static bool IsHash(string value) { return value != null && value.Length == 64 && value.All(character => character >= '0' && character <= '9' || character >= 'a' && character <= 'f'); }

        [Serializable, Preserve] private sealed class SnapshotReceipt
        {
            [Preserve] public int schemaVersion, playerBuildOptions;
            [Preserve] public string kind, snapshotHash, unityVersion, target, architecture, buildGuid, nativeLibraryPath, nativeLibrarySha256;
            [Preserve] public bool playerBuildSucceeded, playerBuildFilterCaptured;
            [Preserve] public string[] extraScriptingDefines;
            [Preserve] public SnapshotFile[] assemblies, references, filteredAssemblies;
            [Preserve] public string linkedPlayerReceiptHash;
            [Preserve] public LinkedPlayerReceipt linkedPlayerReceipt;
            [Preserve] public SourcePins sourcePins;
        }
        [Serializable, Preserve] private sealed class SnapshotFile
        {
            [Preserve] public string name, path, sha256, pdbPath, pdbSha256;
        }
    }
}
