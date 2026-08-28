using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    /// <summary>
    /// M05 type/reflection acceptance entrypoint.  Runtime behavior is added
    /// below the stable schema declarations; these DTOs are the byte-bound
    /// contract shared with the Editor and offline evidence gates.
    /// </summary>
    [Preserve]
    public static class M05TypeProbe
    {
        private const string Internal = "AssemblyA.Implementation.Internal";
        private const string Contracts = "AssemblyA.Contracts";
        private const string Extensibility = "AssemblyA.Implementation.Extensibility";
        private const string ContractsConsumer = "AssemblyShadowDemo.ContractsConsumer";
        private const string ExtensibilityConsumer = "AssemblyShadowDemo.ExtensibilityConsumer";
        private static readonly string[] Modes = {
            "T05-01-P01", "T05-01-P03", "T05-02-P01", "T05-02-P03",
            "T05-03-P01", "T05-03-P03", "T05-04-EarlyType", "T05-05-P01",
            "T05-05-P03", "T05-06-P01", "T05-07-P03", "T05-08-P01",
            "T05-08-P03", "T05-09-LayoutMismatch", "T05-10-P01", "T05-10-P03",
            "T05-11-FeatureOff", "T05-12-BenchmarkOn", "T05-13-BenchmarkOff"
        };

        private const int RuntimeAbiVersion = 1;
        private const string MvidPolicy = "unavailable-pinned-il2cpp-use-byte-bound-build-and-native-diagnostics";
        private static readonly string[] Candidates = { Contracts, Extensibility, Internal, ContractsConsumer, ExtensibilityConsumer };
        private static Result activeCoroutineResult;
        private static bool activeCoroutineInputsValidated;

        public static int RunAndWrite(string expectedBaselineBuildId, string expectedRuntimeAbiHash)
        {
            string mode = Argument("-shadowM05Mode", "T05-01-P01");
            var result = NewResult(mode, expectedBaselineBuildId, expectedRuntimeAbiHash);
            bool inputsValidated = false;
            try
            {
                Require(result.il2cpp, "M05 acceptance requires an actual IL2CPP Player.");
                Require(IsKnownMode(mode), "Unknown M05 mode: " + mode);
                Input input = ReadInputs(expectedBaselineBuildId, expectedRuntimeAbiHash);
                inputsValidated = true;
                result.fixtureManifestPath = input.manifestPath; result.fixtureManifestSha256 = HashFile(input.manifestPath);
                result.playerBuildReceiptPath = input.playerReceiptPath; result.playerBuildReceiptSha256 = HashFile(input.playerReceiptPath);
                result.typeProofPath = input.player.typeProofPath; result.typeProofSha256 = input.player.typeProofSha256;
                if (mode == "T05-13-BenchmarkOff") RunBenchmark(result, false, null);
                else if (mode == "T05-11-FeatureOff") RunFeatureOff(result, input);
                else if (mode == "T05-04-EarlyType") RunEarlyType(result, input);
                else if (mode == "T05-09-LayoutMismatch") RunLayoutMismatch(result, input);
                else RunCommitted(result, input, SelectFixture(input.manifest, mode));
                result.result = "Passed";
            }
            catch (Exception error)
            {
                result.error = error.ToString();
                UnityEngine.Debug.LogException(error);
                if (inputsValidated)
                    try { Capture(result, "failure"); } catch (Exception diagnosticError) { result.error += "\nFailure diagnostics: " + diagnosticError; }
            }
            try { WriteEvidence(result); return result.result == "Passed" ? 0 : 1; }
            catch (Exception error) { UnityEngine.Debug.LogException(error); return 2; }
        }

        public static bool IsResourceMode()
        {
            return Argument("-shadowM05Mode", "T05-01-P01").StartsWith("T05-08-", StringComparison.Ordinal);
        }

        /// <summary>Coroutine entrypoint used by the bootstrap runner for the asynchronous resource cases.</summary>
        public static IEnumerator RunAndWriteCoroutine(string expectedBaselineBuildId, string expectedRuntimeAbiHash, Action<int> completed)
        {
            string mode = Argument("-shadowM05Mode", "T05-01-P01");
            Result result = NewResult(mode, expectedBaselineBuildId, expectedRuntimeAbiHash);
            activeCoroutineResult = result;
            activeCoroutineInputsValidated = false;
            Require(result.il2cpp, "M05 acceptance requires an actual IL2CPP Player.");
            Require(IsKnownMode(mode), "Unknown M05 mode: " + mode);
            Input input = ReadInputs(expectedBaselineBuildId, expectedRuntimeAbiHash);
            activeCoroutineInputsValidated = true;
            result.fixtureManifestPath = input.manifestPath; result.fixtureManifestSha256 = HashFile(input.manifestPath);
            result.playerBuildReceiptPath = input.playerReceiptPath; result.playerBuildReceiptSha256 = HashFile(input.playerReceiptPath);
            result.typeProofPath = input.player.typeProofPath; result.typeProofSha256 = input.player.typeProofSha256;
            if (mode == "T05-13-BenchmarkOff") RunBenchmark(result, false, null);
            else if (mode == "T05-11-FeatureOff") RunFeatureOff(result, input);
            else if (mode == "T05-04-EarlyType") RunEarlyType(result, input);
            else if (mode == "T05-09-LayoutMismatch") RunLayoutMismatch(result, input);
            else
            {
                Fixture fixture = SelectFixture(input.manifest, mode);
                RunCommitted(result, input, fixture, !mode.StartsWith("T05-08-", StringComparison.Ordinal));
                if (mode.StartsWith("T05-08-", StringComparison.Ordinal))
                {
                    IEnumerator resource = M05ResourceProbe.Run(result);
                    while (true)
                    {
                        bool moved;
                        try { moved = resource.MoveNext(); }
                        catch (Exception error) { throw new InvalidOperationException("M05 resource coroutine failed while advancing.", error); }
                        if (!moved) break;
                        yield return resource.Current;
                    }
                    RequireState(result, AssemblyShadowState.Committed, "resource-complete");
                    Capture(result, "final-resource");
                }
            }
            result.result = "Passed";
            int exitCode;
            try { WriteEvidence(result); exitCode = result.result == "Passed" ? 0 : 1; }
            catch (Exception error) { UnityEngine.Debug.LogException(error); exitCode = 2; }
            if (completed != null) completed(exitCode);
        }

        public static int CompleteCoroutineFailure(Exception error)
        {
            Result result = activeCoroutineResult;
            if (result == null) return 2;
            result.error = error == null ? "M05 coroutine failed." : error.ToString();
            UnityEngine.Debug.LogException(error);
            if (activeCoroutineInputsValidated)
                try { Capture(result, "failure"); } catch (Exception diagnosticError) { result.error += "\nFailure diagnostics: " + diagnosticError; }
            try { WriteEvidence(result); return 1; } catch (Exception writeError) { UnityEngine.Debug.LogException(writeError); return 2; }
        }

        private static Result NewResult(string mode, string baseline, string abi)
        {
            return new Result {
                schemaVersion = 1, milestone = "M05", mode = mode, result = "Failed", error = "", il2cpp = IsIl2CppPlayer(),
                unityVersion = Application.unityVersion, platform = Application.platform.ToString(), buildGuid = Application.buildGUID,
                playerDataPath = Application.dataPath, processId = Process.GetCurrentProcess().Id, baselineBuildId = baseline, runtimeAbiHash = abi,
                moduleMvidObservationPolicy = MvidPolicy, businessMarker = "M05-TYPE-PROBE", stageOrder = new string[0],
                checks = new List<Check>(), snapshots = new List<Snapshot>(), actualLogicalAssemblies = new List<AssemblyObservation>(),
                assemblyObservations = new List<AssemblyObservation>(), typeObservations = new List<TypeObservation>(),
                typeResolutionObservations = new List<TypeResolutionObservation>(), typeEnumerations = new List<TypeEnumeration>(),
                memberObservations = new List<MemberObservation>(), identityObservations = new List<IdentityObservation>(),
                assignabilityObservations = new List<AssignabilityObservation>(), loadObservations = new List<LoadObservation>(),
                sceneObservations = new List<SceneObservation>(), stageResults = new List<StageResult>(), benchmark = new Benchmark()
            };
        }

        private static Input ReadInputs(string expectedBaseline, string expectedAbi)
        {
            string manifestPath = Path.GetFullPath(Argument("-shadowM05Fixtures", ""));
            string receiptPath = Path.GetFullPath(Argument("-shadowM05PlayerReceipt", ""));
            Require(File.Exists(manifestPath) && File.Exists(receiptPath), "M05 fixture manifest and Player receipt are required.");
            FixtureManifest manifest = JsonUtility.FromJson<FixtureManifest>(File.ReadAllText(manifestPath));
            PlayerBuildReceipt player = JsonUtility.FromJson<PlayerBuildReceipt>(File.ReadAllText(receiptPath));
            Require(manifest != null && manifest.schemaVersion == 1 && manifest.milestone == "M05", "M05 fixture manifest schema mismatch.");
            Require(player != null && player.schemaVersion == 1 && player.milestone == "M05", "M05 Player receipt schema mismatch.");
            Require(!string.IsNullOrEmpty(expectedBaseline) && IsHash(expectedAbi), "Embedded baseline/ABI identity is missing.");
            Require(manifest.baselineBuildId == expectedBaseline && manifest.runtimeAbiHash == expectedAbi, "M05 fixture identity mismatch.");
            Require(player.baselineBuildId == expectedBaseline && player.runtimeAbiHash == expectedAbi && player.buildGuid == Application.buildGUID, "M05 Player receipt identity mismatch.");
            Require(!string.IsNullOrEmpty(player.buildGuid) && manifest.unityVersion == Application.unityVersion && player.unityVersion == manifest.unityVersion &&
                manifest.target == "StandaloneOSX" && manifest.architecture == "arm64" && player.target == manifest.target && player.architecture == manifest.architecture,
                "M05 executed Player target identity mismatch.");
            Require(manifest.candidateNames != null && manifest.candidateNames.SequenceEqual(Candidates) && manifest.closureLoadOrder != null && manifest.closureLoadOrder.SequenceEqual(Candidates), "M05 candidate/provider order changed.");
            Require(manifest.stableAotNames != null && manifest.stableAotNames.Length > 0 && manifest.stableAotNames.All(name => !string.IsNullOrEmpty(name)) &&
                manifest.stableAotNames.Distinct(StringComparer.OrdinalIgnoreCase).Count() == manifest.stableAotNames.Length &&
                !manifest.stableAotNames.Intersect(Candidates, StringComparer.OrdinalIgnoreCase).Any() &&
                manifest.stableAotNames.SequenceEqual(manifest.stableAotNames.OrderBy(name => name, StringComparer.Ordinal)), "M05 stable AOT allowlist is invalid.");
            Require(!string.IsNullOrEmpty(manifest.stableAotProvenance) && manifest.stableAotProvenanceHash == Hash(Encoding.UTF8.GetBytes("m05-stable-aot:1\n" + manifest.stableAotProvenance)) &&
                manifest.stableAotProvenance.EndsWith("\nphysical=" + string.Join(",", manifest.stableAotNames), StringComparison.Ordinal), "M05 stable AOT provenance mismatch.");
            ValidateByteFile(manifest.baselineManifestPath, manifest.baselineManifestSha256);
            BaselineManifest baseline = ReadBaselineManifest(File.ReadAllText(manifest.baselineManifestPath), manifest, expectedBaseline, expectedAbi);
            SnapshotReceipt baselineInputs = ValidateSnapshot(manifest.baselineInputSnapshot, manifest.baselineInputSnapshotHash, manifest, true);
            SnapshotReceipt playerInputs = ValidateSnapshot(player.inputSnapshot, player.inputSnapshotHash, manifest, true);
            Require(playerInputs.rawAdmissionHash == baselineInputs.rawAdmissionHash, "M05 Player raw-type admission configuration differs from the frozen baseline.");
            Require(playerInputs.buildGuid == player.buildGuid && playerInputs.nativeLibrarySha256 == player.nativeLibrarySha256 &&
                Path.GetFullPath(playerInputs.nativeLibraryPath) == Path.GetFullPath(player.nativeLibraryPath), "M05 Player snapshot/native identity mismatch.");
            ValidateByteFile(player.nativeLibraryPath, player.nativeLibrarySha256);
            string[] nativeLibraries = Directory.GetFiles(Application.dataPath, "GameAssembly.dylib", SearchOption.AllDirectories).Select(Path.GetFullPath).ToArray();
            Require(nativeLibraries.Length == 1 && nativeLibraries[0] == Path.GetFullPath(player.nativeLibraryPath), "M05 native library is not the unique executed Player library.");
            Require(Path.GetFullPath(Application.dataPath).StartsWith(Path.GetFullPath(player.playerOutput).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar, StringComparison.Ordinal), "M05 receipt belongs to another Player output.");
            ValidateMetadata(player);
            Require(player.typeProofPath != null && Path.IsPathRooted(player.typeProofPath) && File.Exists(player.typeProofPath), "M05 type proof is missing.");
            Require(IsHash(player.typeProofSha256) && HashFile(player.typeProofPath) == player.typeProofSha256, "M05 type proof hash mismatch.");
            TypeProof proof = JsonUtility.FromJson<TypeProof>(File.ReadAllText(player.typeProofPath));
            Require(proof != null && proof.schemaVersion == 1 && proof.milestone == "M05" && proof.policy == "active-type-world:1" &&
                proof.buildGuid == Application.buildGUID && proof.compileSnapshotHash == player.inputSnapshotHash &&
                proof.nativeLibrarySha256 == player.nativeLibrarySha256 && !string.IsNullOrEmpty(proof.linkedPlayerReceiptHash) &&
                proof.assemblies != null && proof.assemblies.Length > 0 && proof.moduleMethods != null,
                "M05 type proof schema or identity is incomplete.");
            Require(manifest.fixtures != null && manifest.fixtures.Length == 2, "M05 requires P01 and P03 normal fixtures.");
            Require(manifest.fixtures.All(item => item != null) && manifest.fixtures.Select(item => item.patchId).OrderBy(id => id, StringComparer.Ordinal).SequenceEqual(new[] { "P01", "P03" }), "M05 fixture ids must be exactly P01/P03.");
            Require(manifest.rejectedFixtures != null && manifest.rejectedFixtures.Length == 1 && manifest.rejectedFixtures[0] != null && manifest.rejectedFixtures[0].fixtureId == "LayoutMismatch", "M05 requires exactly the rejected layout fixture.");
            Require(player.assemblyIdentities != null && player.assemblyIdentities.Length > 0, "M05 linked assembly identities are required.");
            M04ReferenceProbe.AssemblyIdentity mscorlib = player.assemblyIdentities.FirstOrDefault(item => item.name == "mscorlib");
            Require(mscorlib != null && File.Exists(mscorlib.path) && HashFile(mscorlib.path) == mscorlib.sha256, "M05 linked mscorlib identity is not byte-bound.");
            foreach (Fixture fixture in manifest.fixtures)
            {
                fixture.patchManifest = ConfinedChild(Path.GetDirectoryName(manifestPath), fixture.patchManifest); fixture.patchDirectory = ConfinedChild(Path.GetDirectoryName(manifestPath), fixture.patchDirectory);
                Require(Path.GetDirectoryName(fixture.patchManifest) == fixture.patchDirectory, "M05 patch manifest is outside its artifact directory.");
                Require(File.Exists(fixture.patchManifest) && HashFile(fixture.patchManifest) == fixture.patchManifestSha256, "M05 patch manifest hash mismatch: " + fixture.patchId);
                fixture.patchRoot = fixture.patchDirectory; fixture.patch = JsonUtility.FromJson<PatchManifest>(File.ReadAllText(fixture.patchManifest));
                Require(fixture.patch != null && fixture.patch.closure != null && fixture.patch.patchId == fixture.patchId, "M05 patch closure is incomplete: " + fixture.patchId);
                Require(fixture.typeInventories != null && fixture.typeInventories.Length == fixture.patch.closure.Length, "M05 type inventory is incomplete: " + fixture.patchId);
                ValidatePatch(fixture, manifest, baseline, baselineInputs.rawAdmissionHash);
            }
            foreach (NegativeRejectedFixture rejected in manifest.rejectedFixtures)
            {
                SnapshotReceipt snapshot = ValidateSnapshot(rejected.compileSnapshot, rejected.compileSnapshotHash, manifest, false);
                Require(snapshot.rawAdmissionHash == baselineInputs.rawAdmissionHash, "M05 rejected fixture raw-type admission differs from the frozen baseline.");
                Require(rejected.errorCode == "ResourceRebuildRequired" && !string.IsNullOrEmpty(rejected.errorMessage) && rejected.changedRoots != null && rejected.changedRoots.SequenceEqual(new[] { Internal }) &&
                    rejected.defines != null && rejected.defines.Contains("ASSEMBLY_SHADOW_M05_LAYOUT_MISMATCH"), "M05 rejected fixture is not the captured layout rejection.");
                ValidateDefines(snapshot.extraScriptingDefines, rejected.defines, baseline.reflectionBindingConfigurationSha256);
                SnapshotFile file = snapshot.assemblies.Single(item => item.name == Internal);
                ValidateByteFile(rejected.dllPath, rejected.dllSha256);
                Require(Path.GetFullPath(rejected.dllPath) == ConfinedChild(rejected.compileSnapshot, file.path) && rejected.dllSha256 == file.sha256 &&
                    rejected.assemblyIdentity != null && rejected.assemblyIdentity.name == Internal && rejected.assemblyIdentity.sha256 == file.sha256 &&
                    Path.GetFullPath(rejected.assemblyIdentity.path) == Path.GetFullPath(rejected.dllPath) && rejected.typeInventory != null && rejected.typeInventory.assemblyName == Internal && rejected.typeInventory.types != null,
                    "M05 rejected fixture bytes/identity/inventory differ.");
            }
            return new Input { manifestPath = manifestPath, playerReceiptPath = receiptPath, manifest = manifest, player = player, typeProof = proof, mscorlib = mscorlib };
        }

        private static BaselineManifest ReadBaselineManifest(string json, FixtureManifest manifest, string expectedBaseline, string expectedAbi)
        {
            BaselineManifest baseline = JsonUtility.FromJson<BaselineManifest>(json);
            Require(baseline != null && baseline.schemaVersion == 1 && baseline.semanticHashSchema == 1 && baseline.baselineBuildId == expectedBaseline && baseline.runtimeAbiHash == expectedAbi &&
                baseline.playerInputSnapshotHash == manifest.baselineInputSnapshotHash && baseline.unityVersion == manifest.unityVersion && baseline.target == manifest.target && baseline.architecture == manifest.architecture,
                "M05 frozen baseline identity mismatch.");
            Require(IsHash(baseline.bootstrapAbiHash), "M05 frozen Bootstrap ABI hash format mismatch.");
            Require(IsResourceAbiHash(baseline.resourceAbiHash), "M05 frozen resource ABI hash must use sha256:<64 lowercase hex>.");
            Require(baseline.shadowCandidates != null && baseline.shadowCandidates.SequenceEqual(Candidates.OrderBy(name => name, StringComparer.Ordinal)), "M05 frozen baseline candidate order mismatch.");
            return baseline;
        }

        private static void ValidateMetadata(PlayerBuildReceipt player)
        {
            Require(!string.IsNullOrEmpty(player.nativeMetadataPath) && Path.IsPathRooted(player.nativeMetadataPath), "Native metadata path must be absolute.");
            string metadataPath = Path.GetFullPath(player.nativeMetadataPath);
            Require(File.Exists(metadataPath) && Path.GetFileName(metadataPath) == "global-metadata.dat", "Native metadata file is missing.");
            Require(IsHash(player.nativeMetadataSha256) && HashFile(metadataPath) == player.nativeMetadataSha256, "Native metadata hash mismatch.");
            Require(player.nativeMetadataVersion == 31, "Unsupported native metadata version; expected v31.");
            ValidateMetadataHeader(metadataPath);
            string[] files = Directory.GetFiles(Application.dataPath, "global-metadata.dat", SearchOption.AllDirectories).Select(Path.GetFullPath).ToArray();
            Require(files.Length == 1 && files[0] == metadataPath, "Native metadata path is not the unique file under the executed Player data path.");
            Require(player.nativeAssemblyIdentities != null && player.nativeAssemblyIdentities.Length > 0, "Native assembly inventory is empty.");
            Require(player.nativeGeneratedAssemblyNames != null && player.nativeGeneratedAssemblyNames.Length > 0, "Native generated assembly inventory is empty.");
            Require(player.nativeAssemblyIdentities.All(item => item != null && item.assemblyIndex >= 0 && item.imageIndex >= 0 && !string.IsNullOrEmpty(item.name) && !string.IsNullOrEmpty(item.fullName) && !string.IsNullOrEmpty(item.imageName)) &&
                player.nativeAssemblyIdentities.Select(item => item.name).Distinct(StringComparer.Ordinal).Count() == player.nativeAssemblyIdentities.Length &&
                player.nativeGeneratedAssemblyNames.All(name => !string.IsNullOrEmpty(name)) && player.nativeGeneratedAssemblyNames.Distinct(StringComparer.Ordinal).Count() == player.nativeGeneratedAssemblyNames.Length,
                "M05 native assembly inventory is malformed.");
        }

        private static void ValidatePatch(Fixture fixture, FixtureManifest manifest, BaselineManifest baseline, string rawAdmissionHash)
        {
            PatchManifest patch = fixture.patch;
            Require(patch.schemaVersion == 1 && patch.semanticHashSchema == 1 && patch.baselineBuildId == manifest.baselineBuildId && patch.baselineManifestSha256 == manifest.baselineManifestSha256 && patch.runtimeAbiHash == manifest.runtimeAbiHash &&
                patch.unityVersion == manifest.unityVersion && patch.target == manifest.target && patch.architecture == manifest.architecture && patch.compileSnapshotHash == fixture.compileSnapshotHash && IsHash(patch.compileSnapshotHash), "M05 patch baseline/compiler identity mismatch: " + fixture.patchId);
            Require(patch.bootstrapAbiHash == baseline.bootstrapAbiHash && patch.baselineResourceAbiHash == baseline.resourceAbiHash && patch.resourceAbiHash == baseline.resourceAbiHash && patch.dllOnly && patch.unsigned && patch.signatureAlgorithm == "None", "M05 patch changed its fixed ABI/integrity contract.");
            string[] expected = fixture.patchId == "P01" ? new[] { Internal } : Candidates;
            Require(patch.loadOrder != null && patch.loadOrder.SequenceEqual(expected) && fixture.closureLoadOrder != null && patch.loadOrder.SequenceEqual(fixture.closureLoadOrder) &&
                patch.closure.Length == expected.Length && patch.closure.Select(item => item.name).OrderBy(name => name, StringComparer.Ordinal).SequenceEqual(expected.OrderBy(name => name, StringComparer.Ordinal)), "M05 closure order/set mismatch: " + fixture.patchId);
            Require(fixture.stableAotNames != null && fixture.stableAotNames.SequenceEqual(manifest.stableAotNames) && fixture.changedRoots != null && fixture.changedRoots.SequenceEqual(expected), "M05 fixture providers/changed roots mismatch.");
            SnapshotReceipt snapshot = ValidateSnapshot(fixture.compileSnapshot, fixture.compileSnapshotHash, manifest, false);
            Require(snapshot.rawAdmissionHash == rawAdmissionHash, "M05 patch raw-type admission differs from the frozen baseline.");
            ValidateDefines(snapshot.extraScriptingDefines, fixture.defines, baseline.reflectionBindingConfigurationSha256);
            Require(fixture.assemblyIdentities != null && fixture.assemblyIdentities.Length == expected.Length, "M05 patch identities are incomplete.");
            foreach (PatchAssembly assembly in fixture.patch.closure)
            {
                string dll = ConfinedChild(fixture.patchRoot, assembly.dll);
                ValidateByteFile(dll, assembly.sha256);
                Require(!string.IsNullOrEmpty(assembly.pdb), "M05 fixture requires captured PDB bytes: " + assembly.name);
                ValidateByteFile(ConfinedChild(fixture.patchRoot, assembly.pdb), assembly.pdbSha256);
                SnapshotFile compiled = snapshot.assemblies.Single(item => item.name == assembly.name);
                Require(compiled.sha256 == assembly.sha256 && compiled.pdbSha256 == assembly.pdbSha256, "M05 deployment bytes differ from captured compiler output.");
                M04ReferenceProbe.AssemblyIdentity identity = fixture.assemblyIdentities.Single(item => item.name == assembly.name);
                Require(identity.sha256 == assembly.sha256 && identity.mvid == assembly.mvid && Path.GetFullPath(identity.path) == dll && !string.IsNullOrEmpty(assembly.mvid) &&
                    baseline.assemblies != null && baseline.assemblies.Single(item => item.name == assembly.name).mvid == assembly.baselineMvid, "M05 patch identity mismatch: " + assembly.name);
                TypeInventory inventory = fixture.typeInventories.Single(item => item.assemblyName == assembly.name);
                Require(inventory.types != null, "M05 type inventory types missing: " + assembly.name);
            }
        }

        // Runtime integrity replay checks captured hashes/identities, not a second PE or semantic-manifest parser.
        private static SnapshotReceipt ValidateSnapshot(string root, string expectedHash, FixtureManifest manifest, bool player)
        {
            Require(!string.IsNullOrEmpty(root) && Path.IsPathRooted(root), "M05 snapshot root must be absolute.");
            SnapshotReceipt snapshot = JsonUtility.FromJson<SnapshotReceipt>(File.ReadAllText(Path.Combine(root, "assembly-snapshot.json")));
            Require(snapshot != null && snapshot.schemaVersion == 1 && IsHash(expectedHash) && snapshot.snapshotHash == expectedHash && snapshot.unityVersion == manifest.unityVersion && snapshot.target == manifest.target && snapshot.architecture == manifest.architecture &&
                snapshot.kind == (player ? "PlayerBuildInputs" : "CompilePlayerScripts") && (!player || (snapshot.playerBuildSucceeded && snapshot.playerBuildFilterCaptured && !string.IsNullOrEmpty(snapshot.buildGuid))) && snapshot.assemblies != null && snapshot.assemblies.Length > 0,
                "M05 captured snapshot identity mismatch.");
            SnapshotFile[] files = snapshot.assemblies.Concat(snapshot.references ?? new SnapshotFile[0]).Concat(snapshot.filteredAssemblies ?? new SnapshotFile[0]).ToArray();
            Require(files.All(file => file != null && !string.IsNullOrEmpty(file.name)) && files.Select(file => file.name).Distinct(StringComparer.OrdinalIgnoreCase).Count() == files.Length, "M05 snapshot assembly inventory is malformed.");
            foreach (SnapshotFile file in files)
            {
                ValidateByteFile(ConfinedChild(root, file.path), file.sha256);
                if (!string.IsNullOrEmpty(file.pdbPath)) ValidateByteFile(ConfinedChild(root, file.pdbPath), file.pdbSha256);
                else Require(string.IsNullOrEmpty(file.pdbSha256), "M05 snapshot has a PDB hash without a PDB path.");
            }
            snapshot.rawAdmissionHash = ValidateRawAdmission(root, snapshot.extraScriptingDefines);
            return snapshot;
        }

        private static string ConfinedChild(string root, string path)
        {
            Require(!string.IsNullOrEmpty(root) && !string.IsNullOrEmpty(path), "M05 artifact path is missing.");
            string prefix = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
            string full = Path.GetFullPath(Path.IsPathRooted(path) ? path : Path.Combine(root, path));
            Require(full.StartsWith(prefix, StringComparison.Ordinal), "M05 artifact path escapes its declared root.");
            return full;
        }

        private static void ValidateByteFile(string path, string expectedHash)
        {
            Require(!string.IsNullOrEmpty(path) && Path.IsPathRooted(path) && File.Exists(path) && IsHash(expectedHash) && HashFile(path) == expectedHash, "M05 artifact bytes/hash mismatch: " + path);
        }

        private static void ValidateDefines(string[] actual, string[] requested, string bindingHash)
        {
            const string prefix = "ASSEMBLY_SHADOW_REFLECTION_BINDINGS_";
            const string rawPrefix = "ASSEMBLY_SHADOW_RAW_TYPE_ADMISSION_";
            Require(actual != null && requested != null && requested.All(value => !string.IsNullOrEmpty(value) && !value.StartsWith(prefix, StringComparison.Ordinal) && !value.StartsWith(rawPrefix, StringComparison.Ordinal)), "M05 requested compiler defines are invalid.");
            string[] expected = IsHash(bindingHash) ? requested.Concat(new[] { prefix + bindingHash }).ToArray() : requested;
            // ValidateSnapshot already bound the raw admission control to actual captured configuration bytes.
            Require(actual.Where(value => value == null || !value.StartsWith(rawPrefix, StringComparison.Ordinal)).SequenceEqual(expected.OrderBy(value => value, StringComparer.Ordinal)), "M05 captured compiler defines/configuration differ from the frozen baseline.");
        }

        private static string ValidateRawAdmission(string root, string[] defines)
        {
            const string prefix = "ASSEMBLY_SHADOW_RAW_TYPE_ADMISSION_";
            string[] controls = (defines ?? new string[0]).Where(value => value != null && value.StartsWith(prefix, StringComparison.Ordinal)).ToArray();
            if (controls.Length == 0) return "";
            Require(controls.Length == 1, "M05 raw-type admission control must be unique.");
            string hash = controls[0].Substring(prefix.Length);
            ValidateByteFile(ConfinedChild(root, "RawTypeAdmissions/configuration.json"), hash);
            return hash;
        }

        private static void ValidateMetadataHeader(string path)
        {
            using (var stream = File.OpenRead(path))
            using (var reader = new BinaryReader(stream))
                Require(stream.Length >= 8 && reader.ReadUInt32() == 0xFAB11BAFU && reader.ReadInt32() == 31, "M05 actual native metadata header is not version 31.");
        }

        private static Fixture SelectFixture(FixtureManifest manifest, string mode)
        {
            string patchId = mode.EndsWith("P01", StringComparison.Ordinal) ? "P01" : "P03";
            return manifest.fixtures.Single(fixture => fixture.patchId == patchId);
        }

        private static void BindFixture(Result result, Fixture fixture)
        {
            result.patchId = fixture.patchId; result.patchManifestPath = Path.GetFullPath(fixture.patchManifest);
            result.patchManifestSha256 = fixture.patchManifestSha256; result.compileSnapshotHash = fixture.compileSnapshotHash;
        }

        private static void Stage(Result result, Fixture fixture, string name)
        {
            PatchAssembly assembly = fixture.patch.closure.Single(item => item.name == name);
            byte[] dll = File.ReadAllBytes(Path.GetFullPath(Path.Combine(fixture.patchRoot, assembly.dll)));
            byte[] pdb = string.IsNullOrEmpty(assembly.pdb) ? null : File.ReadAllBytes(Path.GetFullPath(Path.Combine(fixture.patchRoot, assembly.pdb)));
            string code = Expect(result, "stage-" + name, AssemblyShadowRuntime.StageAssembly(dll, pdb));
            result.stageResults.Add(new StageResult { name = name, code = code, dllSha256 = Hash(dll), pdbSha256 = pdb == null ? "" : Hash(pdb) });
        }

        private static string Capture(Result result, string phase)
        {
            string json; AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetDiagnosticsJson(out json);
            Require(code == AssemblyShadowErrorCode.Success && !string.IsNullOrEmpty(json), "M05 diagnostics query failed: " + code);
            AssemblyShadowDiagnostics diagnostics;
            Require(AssemblyShadowDiagnostics.TryParse(json, out diagnostics), "M05 diagnostics JSON is malformed.");
            result.nativeDiagnosticsJson = json; result.diagnosticsCode = code.ToString(); result.snapshots.Add(new Snapshot { phase = phase, diagnostics = diagnostics });
            return code.ToString();
        }

        private static void RequireState(Result result, AssemblyShadowState expected, string phase)
        {
            AssemblyShadowState actual; AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetState(out actual);
            result.stateCode = code.ToString(); result.state = actual.ToString();
            Require(code == AssemblyShadowErrorCode.Success && actual == expected, "M05 " + phase + " state mismatch: " + actual);
        }

        private static string Expect(Result result, string operation, AssemblyShadowErrorCode actual, AssemblyShadowErrorCode expected = AssemblyShadowErrorCode.Success)
        {
            result.checks.Add(new Check { name = operation, actual = actual.ToString(), expected = expected.ToString(), actualCode = (int)actual, expectedCode = (int)expected });
            Require(actual == expected, operation + " returned " + actual + ", expected " + expected);
            return actual.ToString();
        }

        private static void RunCommitted(Result result, Input input, Fixture fixture, bool captureFinal = true)
        {
            BindFixture(result, fixture);
            RequireState(result, AssemblyShadowState.Disabled, "initial"); Capture(result, "initial");
            CheckOnQueryArguments(result);
            result.configure = Expect(result, "configure", AssemblyShadowRuntime.ConfigureCandidates(input.manifest.baselineBuildId, input.manifest.candidateNames, input.manifest.stableAotNames));
            result.begin = Expect(result, "begin", AssemblyShadowRuntime.BeginTransaction(fixture.patchId, input.manifest.baselineBuildId, fixture.closureLoadOrder, RuntimeAbiVersion));
            RequireState(result, AssemblyShadowState.Staging, "staging");
            foreach (string name in fixture.closureLoadOrder) Stage(result, fixture, name);
            result.stageOrder = fixture.closureLoadOrder.ToArray(); Capture(result, "staged");
            result.validate = Expect(result, "validate", AssemblyShadowRuntime.ValidateTransaction()); Capture(result, "validated");
            result.commit = Expect(result, "commit", AssemblyShadowRuntime.CommitTransaction()); RequireState(result, AssemblyShadowState.Committed, "committed"); Capture(result, "committed");

            ObserveAssemblies(result, input, fixture);
            if (ModeHas(result.mode, "T05-01") || ModeHas(result.mode, "T05-05")) ObserveNameAndCompositeForms(result, fixture);
            if (ModeHas(result.mode, "T05-02")) ObserveEnumerations(result, fixture);
            if (ModeHas(result.mode, "T05-03") || ModeHas(result.mode, "T05-10")) ObserveReflectionCaches(result, fixture);
            if (ModeHas(result.mode, "T05-05")) ObserveComposites(result, fixture);
            if (result.mode == "T05-06-P01" || result.mode == "T05-07-P03") ObserveInterface(result, fixture);
            if (ModeHas(result.mode, "T05-12")) RunBenchmark(result, true, fixture);
            if (captureFinal) Capture(result, "final");
        }

        private static void RunEarlyType(Result result, Input input)
        {
            Fixture fixture = SelectFixture(input.manifest, "T05-04-EarlyType");
            BindFixture(result, fixture); RequireState(result, AssemblyShadowState.Disabled, "initial"); Capture(result, "initial");
            CheckOnQueryArguments(result);
            result.configure = Expect(result, "configure", AssemblyShadowRuntime.ConfigureCandidates(input.manifest.baselineBuildId, input.manifest.candidateNames, input.manifest.stableAotNames));
            result.begin = Expect(result, "begin", AssemblyShadowRuntime.BeginTransaction(fixture.patchId, input.manifest.baselineBuildId, fixture.closureLoadOrder, RuntimeAbiVersion));
            RequireState(result, AssemblyShadowState.Staging, "staging");
            foreach (string name in fixture.closureLoadOrder) Stage(result, fixture, name);
            result.stageOrder = fixture.closureLoadOrder.ToArray(); Capture(result, "staged");
            result.validate = Expect(result, "validate", AssemblyShadowRuntime.ValidateTransaction()); Capture(result, "validated");
            Type baselineType = Type.GetType("AssemblyA.Implementation.Internal.VersionedPrefabComponent, AssemblyA.Implementation.Internal", true);
            Type baselineTypeRepeat = Type.GetType("AssemblyA.Implementation.Internal.VersionedPrefabComponent, AssemblyA.Implementation.Internal", true);
            ObserveTypeResolution(result, "early-baseline-type", baselineType, System.Object.ReferenceEquals(baselineType, baselineTypeRepeat));
            result.checks.Add(new Check { name = "first-use-kind", actual = "baseline-Type.GetType", expected = "baseline-Type.GetType", actualCode = 0, expectedCode = 0 });
            result.loadObservations.Add(new LoadObservation { requested = "AssemblyA.Implementation.Internal.VersionedPrefabComponent, AssemblyA.Implementation.Internal", overload = "early-baseline", typeName = baselineType.FullName, assemblyName = baselineType.Assembly.GetName().Name, sameType = true });
            result.commit = Expect(result, "commit", AssemblyShadowRuntime.CommitTransaction(), AssemblyShadowErrorCode.BaselineAlreadyUsed);
            result.abort = Expect(result, "abort", AssemblyShadowRuntime.AbortTransaction()); RequireState(result, AssemblyShadowState.Aborted, "aborted"); Capture(result, "aborted");
        }

        private static void RunLayoutMismatch(Result result, Input input)
        {
            NegativeRejectedFixture rejected = input.manifest.rejectedFixtures.Single(item => item.fixtureId == "LayoutMismatch");
            result.patchId = rejected.fixtureId; result.patchManifestPath = ""; result.patchManifestSha256 = ""; result.compileSnapshotHash = rejected.compileSnapshotHash;
            RequireState(result, AssemblyShadowState.Disabled, "initial"); Capture(result, "initial");
            CheckOnQueryArguments(result);
            result.configure = Expect(result, "configure", AssemblyShadowRuntime.ConfigureCandidates(input.manifest.baselineBuildId, input.manifest.candidateNames, input.manifest.stableAotNames));
            result.begin = Expect(result, "begin", AssemblyShadowRuntime.BeginTransaction("LayoutMismatch", input.manifest.baselineBuildId, new[] { Internal }, RuntimeAbiVersion));
            RequireState(result, AssemblyShadowState.Staging, "staging");
            byte[] dll = File.ReadAllBytes(rejected.dllPath); result.stage = Expect(result, "stage-layout-mismatch", AssemblyShadowRuntime.StageAssembly(dll, null)); result.stageOrder = new[] { Internal }; Capture(result, "staged");
            result.validate = Expect(result, "validate", AssemblyShadowRuntime.ValidateTransaction()); Capture(result, "validated");
            result.commit = Expect(result, "commit", AssemblyShadowRuntime.CommitTransaction()); RequireState(result, AssemblyShadowState.Committed, "committed"); Capture(result, "committed");
            Type componentType = Type.GetType("AssemblyA.Implementation.Internal.VersionedPrefabComponent, AssemblyA.Implementation.Internal", true);
            object allocated = null; bool allocationThrew = false;
            try
            {
                allocated = Activator.CreateInstance(componentType);
            }
            catch (Exception allocationError)
            {
                allocationThrew = true;
                result.allocationException = allocationError.ToString();
            }
            Require(allocationThrew && allocated == null && !string.IsNullOrEmpty(result.allocationException), "M05 layout mismatch allocation did not throw without returning an object.");
            CheckObserved(result, "allocation-no-object", allocated == null);
            RequireState(result, AssemblyShadowState.FailedAfterCommit, "allocation-failure");
            Capture(result, "allocation-failure");
            AssemblyShadowDiagnostics diagnostics = result.snapshots.Last().diagnostics;
            result.checks.Add(new Check { name = "allocation-guard", actual = diagnostics.lastError.ToString(), expected = ((int)AssemblyShadowErrorCode.ResourceAbiMismatch).ToString(), actualCode = diagnostics.lastError, expectedCode = (int)AssemblyShadowErrorCode.ResourceAbiMismatch });
            Require(diagnostics.lastError == (int)AssemblyShadowErrorCode.ResourceAbiMismatch && diagnostics.detail != null && diagnostics.detail.Contains("ShadowLayoutMismatch"), "M05 layout mismatch diagnostic was not the native allocation guard.");
        }

        private static void RunFeatureOff(Result result, Input input)
        {
            AssemblyShadowState state; AssemblyExecutionMode mode; string json;
            result.configure = Expect(result, "configure", AssemblyShadowRuntime.ConfigureCandidates(null, null, null), AssemblyShadowErrorCode.FeatureDisabled);
            result.begin = Expect(result, "begin", AssemblyShadowRuntime.BeginTransaction(null, null, null, -1), AssemblyShadowErrorCode.FeatureDisabled);
            result.stage = Expect(result, "stage", AssemblyShadowRuntime.StageAssembly(null, null), AssemblyShadowErrorCode.FeatureDisabled);
            result.validate = Expect(result, "validate", AssemblyShadowRuntime.ValidateTransaction(), AssemblyShadowErrorCode.FeatureDisabled);
            result.commit = Expect(result, "commit", AssemblyShadowRuntime.CommitTransaction(), AssemblyShadowErrorCode.FeatureDisabled);
            result.abort = Expect(result, "abort", AssemblyShadowRuntime.AbortTransaction(), AssemblyShadowErrorCode.FeatureDisabled);
            result.stateCode = Expect(result, "state", AssemblyShadowRuntime.GetState(out state), AssemblyShadowErrorCode.FeatureDisabled); result.state = state.ToString();
            result.diagnosticsCode = Expect(result, "diagnostics", AssemblyShadowRuntime.GetDiagnosticsJson(out json), AssemblyShadowErrorCode.FeatureDisabled); result.nativeDiagnosticsJson = json;
            result.executionModeCode = Expect(result, "execution-mode", AssemblyShadowRuntime.GetAssemblyExecutionMode(null, out mode), AssemblyShadowErrorCode.FeatureDisabled); result.executionMode = mode.ToString();
            string typeJson = "must-be-cleared";
            Expect(result, "type-resolution", AssemblyShadowRuntime.GetTypeResolutionInfo(typeof(string), out typeJson), AssemblyShadowErrorCode.FeatureDisabled);
            CheckObserved(result, "type-resolution-valid-null-json", typeJson == null);
            typeJson = "must-be-cleared";
            Expect(result, "type-resolution-null-input", AssemblyShadowRuntime.GetTypeResolutionInfo(null, out typeJson), AssemblyShadowErrorCode.FeatureDisabled);
            CheckObserved(result, "type-resolution-invalid-null-json", typeJson == null);
            Require(state == AssemblyShadowState.Disabled && mode == AssemblyExecutionMode.AotBaseline, "M05 OFF out values changed.");
            Require(AssemblyShadowDiagnostics.TryParse(json, out AssemblyShadowDiagnostics diagnostics), "M05 OFF diagnostics malformed."); result.snapshots.Add(new Snapshot { phase = "disabled", diagnostics = diagnostics });
            result.ordinary = M04OrdinaryAssemblyProbe.Run(input.mscorlib.path, input.mscorlib.sha256, input.mscorlib.fullName, input.mscorlib.mvid);
        }

        private static void CheckOnQueryArguments(Result result)
        {
            AssemblyShadowState before, after;
            Expect(result, "type-resolution-state-before", AssemblyShadowRuntime.GetState(out before));
            string json = "must-be-cleared";
            Expect(result, "type-resolution-null-input", AssemblyShadowRuntime.GetTypeResolutionInfo(null, out json), AssemblyShadowErrorCode.InvalidArgument);
            CheckObserved(result, "type-resolution-invalid-null-json", json == null);
            Expect(result, "type-resolution-state-after", AssemblyShadowRuntime.GetState(out after));
            CheckObserved(result, "type-resolution-state-unchanged", before == after);
        }

        private static void CheckObserved(Result result, string name, bool actual)
        {
            result.checks.Add(new Check { name = name, actual = actual.ToString(), expected = true.ToString(), actualCode = actual ? 1 : 0, expectedCode = 1 });
            Require(actual, "M05 observation failed: " + name);
        }

        private static void ObserveAssemblies(Result result, Input input, Fixture fixture)
        {
            foreach (string name in Candidates)
            {
                Assembly assembly = LoadAssembly(name); AssemblyExecutionMode mode; AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetAssemblyExecutionMode(name, out mode);
                bool shadow = fixture.closureLoadOrder.Contains(name, StringComparer.Ordinal);
                Require(assembly.FullName == ExpectedFullName(input, fixture, name), "M05 assembly full identity mismatch: " + name);
                Require((code == AssemblyShadowErrorCode.Success && mode == (shadow ? AssemblyExecutionMode.InterpreterShadow : AssemblyExecutionMode.AotBaseline)) || (!shadow && code == AssemblyShadowErrorCode.CandidateNotRegistered && mode == AssemblyExecutionMode.AotBaseline), "M05 assembly execution mode mismatch: " + name);
                result.assemblyObservations.Add(new AssemblyObservation { name = name, fullName = assembly.FullName, mvid = "", mvidAvailable = false, executionCode = code.ToString(), executionMode = mode.ToString(), isInterpreter = shadow, logical = true });
            }
            foreach (Assembly assembly in AppDomain.CurrentDomain.GetAssemblies())
            {
                if (assembly == null) continue;
                AssemblyExecutionMode mode; AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetAssemblyExecutionMode(assembly.GetName().Name, out mode);
                string name = assembly.GetName().Name;
                bool logical = !Candidates.Contains(name, StringComparer.Ordinal);
                if (!logical)
                {
                    logical = System.Object.ReferenceEquals(assembly, LoadAssembly(name)) && System.Object.ReferenceEquals(assembly, WitnessOwner(name).Assembly);
                    CheckObserved(result, "appdomain-identity-" + name, logical);
                }
                result.actualLogicalAssemblies.Add(new AssemblyObservation { name = name, fullName = assembly.FullName, mvid = "", mvidAvailable = false, executionCode = code.ToString(), executionMode = mode.ToString(), isInterpreter = code == AssemblyShadowErrorCode.Success && mode == AssemblyExecutionMode.InterpreterShadow, logical = logical });
            }
        }

        private static void ObserveNameAndCompositeForms(Result result, Fixture fixture)
        {
            foreach (string name in fixture.closureLoadOrder)
            {
                Type[] forms = InvokeWitnessTypes(name, "GetM05TypeNameForms");
                Type[] repeated = InvokeWitnessTypes(name, "GetM05TypeNameForms");
                for (int index = 0; index < forms.Length; ++index)
                    ObserveType(result, "name-form", forms[index], true, System.Object.ReferenceEquals(forms[index], repeated[index]));
            }
        }

        private static void ObserveEnumerations(Result result, Fixture fixture)
        {
            foreach (string name in fixture.closureLoadOrder)
            {
                Type[] types = M05BoundTypeQueries.GetTypes(name);
                AddEnumeration(result, "Assembly.GetTypes", name, types);
                ValidateTypeInventory(fixture, name, types);
                AddEnumeration(result, "Assembly.DefinedTypes", name, M05BoundTypeQueries.GetDefinedTypes(name).Select(item => item.AsType()).ToArray());
                AddEnumeration(result, "Assembly.ExportedTypes", name, M05BoundTypeQueries.GetExportedTypes(name).ToArray());
                AddEnumeration(result, "Module.GetTypes", name, M05BoundTypeQueries.GetModuleTypes(name));
            }
        }

        private static void AddEnumeration(Result result, string operation, string assemblyName, Type[] types)
        {
            result.typeEnumerations.Add(new TypeEnumeration { operation = operation, assemblyName = assemblyName, typeNames = types.Select(item => item.FullName).ToArray() });
        }

        private static void ValidateTypeInventory(Fixture fixture, string assemblyName, Type[] actualTypes)
        {
            TypeInventory expected = fixture.typeInventories.Single(item => item.assemblyName == assemblyName);
            Require(expected.types != null && actualTypes != null && expected.types.Length == actualTypes.Length,
                "M05 type inventory count mismatch: " + assemblyName);
            Require(expected.types.All(type => type != null && !string.IsNullOrEmpty(type.fullName) &&
                type.namespaceName != null && type.nestingPath != null) && actualTypes.All(type => type != null) &&
                expected.types.Select(type => type.fullName).Distinct(StringComparer.Ordinal).Count() == expected.types.Length,
                "M05 type inventory contains missing or duplicate definitions: " + assemblyName);
            var definitions = expected.types.ToDictionary(type => type.fullName, StringComparer.Ordinal);
            for (int index = 0; index < actualTypes.Length; ++index)
            {
                Type actual = actualTypes[index]; TypeDefinition claim = expected.types[index];
                Type outermost = actual;
                while (outermost.DeclaringType != null) outermost = outermost.DeclaringType;
                TypeDefinition owner;
                Require(definitions.TryGetValue(outermost.FullName, out owner) && owner.nestingPath.Length == 0,
                    "M05 type inventory has no top-level declaring definition: " + assemblyName + " / " + actual.FullName);
                // The inventory preserves raw TypeDef.Namespace. Pinned IL2CPP
                // Type.Namespace projects the outermost declaring namespace.
                // A nested row's own nonempty namespace is not independently
                // observable on this path; do not silently normalize it away.
                Require(!actual.IsNested || claim.namespaceName.Length == 0,
                    "M05 nested TypeDef namespace is unsupported by the pinned reflection projection: " + claim.fullName);
                string reflectedNamespace = owner.namespaceName;
                Require(claim.fullName == actual.FullName && reflectedNamespace == (actual.Namespace ?? "") &&
                    claim.name == actual.Name && claim.genericArity == (actual.IsGenericType ? actual.GetGenericArguments().Length : 0) &&
                    claim.kind == TypeKind(actual) && claim.isExported == IsExported(actual) &&
                    claim.nestingPath.SequenceEqual(NestingPath(actual)),
                    "M05 type inventory mismatch: " + assemblyName + " index " + index + "; expected " + claim.fullName +
                    " namespace='" + reflectedNamespace + "'; observed " + actual.FullName + " namespace='" + (actual.Namespace ?? "") + "'");
            }
        }

        private static string TypeKind(Type type)
        {
            return type.IsEnum ? "enum" : type.IsInterface ? "interface" : type.IsValueType ? "valuetype" : "class";
        }

        private static bool IsExported(Type type)
        {
            if (type.IsNested)
                return type.IsNestedPublic && IsExported(type.DeclaringType);
            return type.IsPublic;
        }

        private static string[] NestingPath(Type type)
        {
            var path = new List<string>();
            for (Type parent = type.DeclaringType; parent != null; parent = parent.DeclaringType) path.Add(parent.Name);
            path.Reverse(); return path.ToArray();
        }

        private static void ObserveReflectionCaches(Result result, Fixture fixture)
        {
            foreach (string name in fixture.closureLoadOrder)
            {
                Assembly firstAssembly = LoadAssembly(name), secondAssembly = LoadAssembly(name);
                result.identityObservations.Add(new IdentityObservation { operation = "Assembly.Load", left = firstAssembly.FullName, right = secondAssembly.FullName, sameObject = System.Object.ReferenceEquals(firstAssembly, secondAssembly) });
                Type[] types = InvokeWitnessTypes(name, "GetM05Types");
                Require(types != null && types.Length > 0, "M05 reflection witness types are empty.");
                Type type = types[0]; Type[] repeatedTypes = InvokeWitnessTypes(name, "GetM05Types"); Type byName = WitnessOwner(name); Module module = firstAssembly.ManifestModule;
                bool sameModule = System.Object.ReferenceEquals(module, secondAssembly.ManifestModule);
                result.identityObservations.Add(new IdentityObservation { operation = "ManifestModule", left = firstAssembly.FullName, right = secondAssembly.FullName, sameObject = sameModule });
                CheckObserved(result, "module-identity-" + name, sameModule);
                Type moduleType = GetLiteralModuleType(name);
                    result.identityObservations.Add(new IdentityObservation { operation = "Type/Module.GetType", left = byName.FullName, right = moduleType.FullName, sameObject = System.Object.ReferenceEquals(byName, moduleType) });
                    ObserveTypeResolution(result, "GetTypeResolutionInfo", byName, System.Object.ReferenceEquals(byName, moduleType));
                result.identityObservations.Add(new IdentityObservation { operation = "PatchType/Assembly", left = type.Assembly.FullName, right = firstAssembly.FullName, sameObject = System.Object.ReferenceEquals(type.Assembly, firstAssembly) });
                result.identityObservations.Add(new IdentityObservation { operation = "PatchType witness repeat", left = type.FullName, right = repeatedTypes[0].FullName, sameObject = System.Object.ReferenceEquals(type, repeatedTypes[0]) });
                const BindingFlags memberFlags = BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly;
                MethodInfo method = type.GetMethod("Echo", memberFlags), repeatedMethod = type.GetMethod("Echo", memberFlags);
                FieldInfo field = type.GetField("Field", memberFlags), repeatedField = type.GetField("Field", memberFlags);
                PropertyInfo property = type.GetProperty("Property", memberFlags), repeatedProperty = type.GetProperty("Property", memberFlags);
                EventInfo eventInfo = type.GetEvent("Changed", memberFlags), repeatedEvent = type.GetEvent("Changed", memberFlags);
                Require(method != null && repeatedMethod != null && field != null && repeatedField != null && property != null && repeatedProperty != null && eventInfo != null && repeatedEvent != null,
                    "M05 requires all four declared payload member kinds: " + name);
                ObserveMember(result, firstAssembly, method, repeatedMethod, "method", method.ReturnType, null, method.GetParameters(), repeatedMethod.GetParameters());
                ObserveMember(result, firstAssembly, field, repeatedField, "field", null, field.FieldType, new ParameterInfo[0], new ParameterInfo[0]);
                ObserveMember(result, firstAssembly, property, repeatedProperty, "property", property.PropertyType, null, property.GetIndexParameters(), repeatedProperty.GetIndexParameters());
                ObserveMember(result, firstAssembly, eventInfo, repeatedEvent, "event", null, eventInfo.EventHandlerType, new ParameterInfo[0], new ParameterInfo[0]);
                result.identityObservations.Add(new IdentityObservation { operation = "ManifestModule.Assembly", left = firstAssembly.FullName, right = firstAssembly.ManifestModule.Assembly.FullName, sameObject = System.Object.ReferenceEquals(firstAssembly, firstAssembly.ManifestModule.Assembly) });
            }
        }

        private static void ObserveMember(Result result, Assembly assembly, MemberInfo member, MemberInfo repeated,
            string kind, Type returnType, Type fieldType, ParameterInfo[] parameters, ParameterInfo[] repeatedParameters)
        {
            bool same = System.Object.ReferenceEquals(member, repeated);
            Require(member.DeclaringType != null && member.ReflectedType != null, "M05 member owner is missing.");
            bool activeOwner = ObserveTypeResolution(result, "member-" + kind + "-declaring", member.DeclaringType, System.Object.ReferenceEquals(member.DeclaringType, repeated.DeclaringType)) &&
                ObserveTypeResolution(result, "member-" + kind + "-reflected", member.ReflectedType, System.Object.ReferenceEquals(member.ReflectedType, repeated.ReflectedType));
            activeOwner = activeOwner && System.Object.ReferenceEquals(member.DeclaringType.Assembly, assembly) && System.Object.ReferenceEquals(member.ReflectedType.Assembly, assembly) &&
                System.Object.ReferenceEquals(member.DeclaringType, repeated.DeclaringType) && System.Object.ReferenceEquals(member.ReflectedType, repeated.ReflectedType);
            CheckObserved(result, "member-" + kind + "-identity-" + assembly.GetName().Name, same && activeOwner);
            if (returnType != null)
            {
                Type repeatedType = repeated is MethodInfo ? ((MethodInfo)repeated).ReturnType : ((PropertyInfo)repeated).PropertyType;
                bool sameType = System.Object.ReferenceEquals(returnType, repeatedType);
                Require(sameType && ObserveTypeResolution(result, "member-" + kind + "-return", returnType, sameType), "Inactive or unstable member return type.");
            }
            if (fieldType != null)
            {
                Type repeatedType = repeated is FieldInfo ? ((FieldInfo)repeated).FieldType : ((EventInfo)repeated).EventHandlerType;
                bool sameType = System.Object.ReferenceEquals(fieldType, repeatedType);
                Require(sameType && ObserveTypeResolution(result, "member-" + kind + "-type", fieldType, sameType), "Inactive or unstable member field/event type.");
            }
            Require(parameters.Length == repeatedParameters.Length, "M05 parameter count changed across repeated member access.");
            for (int index = 0; index < parameters.Length; ++index)
            {
                bool sameParameter = System.Object.ReferenceEquals(parameters[index], repeatedParameters[index]);
                bool sameType = System.Object.ReferenceEquals(parameters[index].ParameterType, repeatedParameters[index].ParameterType);
                CheckObserved(result, "member-" + kind + "-parameter-identity-" + assembly.GetName().Name + "-" + index, sameParameter && sameType);
                Require(ObserveTypeResolution(result, "member-" + kind + "-parameter-" + index, parameters[index].ParameterType, sameType), "Inactive member parameter type.");
            }
            result.memberObservations.Add(new MemberObservation { declaringType = member.DeclaringType.FullName, reflectedType = member.ReflectedType.FullName,
                memberName = member.Name, memberKind = kind, returnType = returnType == null ? "" : returnType.FullName,
                fieldType = fieldType == null ? "" : fieldType.FullName, parameterTypes = parameters.Select(item => item.ParameterType.FullName).ToArray(), sameMember = same, activeOwner = activeOwner });
        }

        private static Type GetLiteralModuleType(string name)
        {
            return M05BoundTypeQueries.GetModuleType(name);
        }

        private static void ObserveComposites(Result result, Fixture fixture)
        {
            if (!fixture.closureLoadOrder.Contains(Internal, StringComparer.Ordinal)) return;
            Type[] types = InvokeWitnessTypes(Internal, "GetM05CompositeTypes");
            Type[] repeated = InvokeWitnessTypes(Internal, "GetM05CompositeTypes");
            Require(types != null && repeated != null && types.Length == 9 && repeated.Length == types.Length, "M05 requires all nine composite forms.");
            for (int index = 0; index < types.Length; ++index)
            {
                ObserveType(result, "composite", types[index], true, System.Object.ReferenceEquals(types[index], repeated[index]));
                Type fromHandle = Type.GetTypeFromHandle(types[index].TypeHandle);
                CheckObserved(result, "composite-handle-" + index, System.Object.ReferenceEquals(types[index], fromHandle));
                ObserveType(result, "composite-handle", fromHandle, true, System.Object.ReferenceEquals(fromHandle, Type.GetTypeFromHandle(repeated[index].TypeHandle)));
                if (types[index].HasElementType)
                    ObserveType(result, "composite-element", types[index].GetElementType(), true, System.Object.ReferenceEquals(types[index].GetElementType(), repeated[index].GetElementType()));
                if (types[index].IsGenericType)
                {
                    Type[] arguments = types[index].GetGenericArguments(), repeatedArguments = repeated[index].GetGenericArguments();
                    Require(arguments.Length == repeatedArguments.Length, "Composite generic argument count changed.");
                    for (int argument = 0; argument < arguments.Length; ++argument)
                        ObserveType(result, "composite-argument", arguments[argument], true, System.Object.ReferenceEquals(arguments[argument], repeatedArguments[argument]));
                }
            }
            Array[] arrays = InvokeWitnessObject(Internal, "GetM05CompositeArrays") as Array[];
            Require(arrays != null && arrays.Length == 2 && arrays[0] != null && arrays[1] != null, "Actual composite array witness is missing.");
            for (int index = 0; index < arrays.Length; ++index)
            {
                Type actual = arrays[index].GetType();
                CheckObserved(result, "composite-array-rank-" + (index + 1), arrays[index].Rank == index + 1 && arrays[index].Length == 2);
                bool same = System.Object.ReferenceEquals(actual, types[index + 5]);
                result.identityObservations.Add(new IdentityObservation { operation = "composite-array-runtime-type", left = actual.FullName, right = types[index + 5].FullName, sameObject = same });
                ObserveType(result, "composite-array-runtime-type", actual, true, same);
            }
        }

        private static void ObserveInterface(Result result, Fixture fixture)
        {
            if (!fixture.closureLoadOrder.Contains(Internal, StringComparer.Ordinal)) return;
            bool contractsShadow = fixture.closureLoadOrder.Contains(Contracts, StringComparer.Ordinal);
            const string contractName = "AssemblyA.Contracts.IVersionTextProvider";
            object payload = InvokeWitnessObject(Internal, "GetM05InterfacePayload");
            Type source = payload.GetType();
            Type contract = source.GetInterfaces().FirstOrDefault(item => item.FullName == contractName);
            Require(contract != null, "M05 interface payload does not expose the active Contracts interface.");
            bool assignable = contract.IsAssignableFrom(source), instance = contract.IsInstanceOfType(payload);
            string castMarker = InvokeWitnessObject(Internal, "GetM05InterfaceCastResult") as string;
            bool cast = castMarker == "M05-INTERNAL";
            result.assignabilityObservations.Add(new AssignabilityObservation { operation = "Contracts interface", sourceType = source.FullName, targetType = contract.FullName, isAssignable = assignable, isInstance = instance, castSucceeded = cast, castMarker = castMarker ?? "" });
            Require(assignable && instance && cast, "M05 interface cast/assignability failed.");
            ObserveExpectedMode(result, "interface-source", source, true);
            ObserveExpectedMode(result, "Contracts interface", contract, contractsShadow);
            if (contractsShadow)
            {
                string consumerDispatch = InvokeConsumerDispatch(ContractsConsumer, payload);
                CheckObserved(result, "contracts-consumer-interface-dispatch", consumerDispatch == "M05-INTERNAL|CONTRACTS-CONSUMER");
                ObserveExpectedMode(result, "contracts-consumer-owner", WitnessOwner(ContractsConsumer), true);
                object derived = InvokeWitnessObject(ExtensibilityConsumer, "GetM05Payload");
                Type derivedType = derived.GetType(), baseType = derivedType.BaseType;
                Type derivedContract = derivedType.GetInterfaces().Single(item => item.FullName == contractName);
                string derivedDispatch = InvokeConsumerDispatch(ExtensibilityConsumer, derived);
                bool derivedCast = derivedDispatch == "M05-EXT-CONSUMER|M05-SHADOW-CONTRACTS";
                bool baseAssignable = baseType != null && baseType.IsAssignableFrom(derivedType), baseInstance = baseType != null && baseType.IsInstanceOfType(derived);
                result.assignabilityObservations.Add(new AssignabilityObservation { operation = "Extensibility consumer inheritance", sourceType = derivedType.FullName,
                    targetType = baseType == null ? "" : baseType.FullName, isAssignable = baseAssignable, isInstance = baseInstance, castSucceeded = derivedCast, castMarker = derivedDispatch });
                Require(derivedCast && baseAssignable && baseInstance && System.Object.ReferenceEquals(contract, derivedContract), "P03 consumer dispatch/inheritance escaped the active Contracts world.");
                ObserveExpectedMode(result, "extensibility-consumer-source", derivedType, true);
                ObserveExpectedMode(result, "extensibility-consumer-base", baseType, true);
                ObserveExpectedMode(result, "extensibility-consumer-contract", derivedContract, true);
                ObserveExpectedMode(result, "extensibility-consumer-owner", WitnessOwner(ExtensibilityConsumer), true);
            }
        }

        private static void ObserveExpectedMode(Result result, string operation, Type type, bool shadow)
        {
            bool same = System.Object.ReferenceEquals(type, Type.GetTypeFromHandle(type.TypeHandle));
            Require(ObserveTypeResolution(result, operation, type, same) && same, "Inactive or unstable type: " + operation);
            AssemblyShadowTypeResolutionInfo info = result.typeResolutionObservations.Last().info;
            Require(info.executionModeCode == (int)(shadow ? AssemblyExecutionMode.InterpreterShadow : AssemblyExecutionMode.AotBaseline) &&
                info.physicalImageKind == (shadow ? "Interpreter" : "Aot"), "Unexpected actual type execution mode: " + operation);
        }

        private static string InvokeConsumerDispatch(string assemblyName, object payload)
        {
            Require(assemblyName == ContractsConsumer || assemblyName == ExtensibilityConsumer, "Unknown M05 consumer dispatch owner.");
            MethodInfo method = WitnessOwner(assemblyName).GetMethod("GetM05ConsumerDispatch", BindingFlags.Public | BindingFlags.Static);
            Require(method != null && method.ReturnType == typeof(object), "M05 consumer dispatch method is missing.");
            string marker = method.Invoke(null, new[] { payload }) as string;
            Require(marker != null, "M05 consumer dispatch did not return its actual marker.");
            return marker;
        }

        private static bool ObserveTypeResolution(Result result, string operation, Type type, bool sameType)
        {
            string json; AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetTypeResolutionInfo(type, out json);
            Require(code == AssemblyShadowErrorCode.Success && !string.IsNullOrEmpty(json), "M05 type-resolution query failed: " + code);
            AssemblyShadowTypeResolutionInfo info;
            Require(AssemblyShadowTypeResolutionInfo.TryParse(json, out info), "M05 type-resolution JSON is malformed.");
            result.typeResolutionObservations.Add(new TypeResolutionObservation { operation = operation, requested = type.FullName, rawJson = json, info = info, sameType = sameType });
            return info != null && info.isActive;
        }

        private static void ObserveType(Result result, string operation, Type type, bool requireActive, bool sameType)
        {
            Require(type != null, "M05 type observation returned null.");
            bool isActive = requireActive && ObserveTypeResolution(result, operation, type, sameType);
            Require(sameType && (!requireActive || isActive), "Inactive or unstable M05 type observation: " + type);
            TypeObservation row = new TypeObservation {
                requested = type.FullName, fullName = type.FullName, assemblyName = type.Assembly.GetName().Name,
                kind = type.IsEnum ? "enum" : type.IsInterface ? "interface" : type.IsValueType ? "valuetype" : "class",
                genericDefinition = type.IsGenericType ? (type.IsGenericTypeDefinition ? type.FullName : type.GetGenericTypeDefinition().FullName) : "",
                genericArguments = type.IsGenericType ? type.GetGenericArguments().Select(item => item.FullName).ToArray() : new string[0],
                elementShape = type.IsArray ? "array-rank-" + type.GetArrayRank() : type.IsByRef ? "byref" : type.IsPointer ? "pointer" : "",
                isActive = isActive, sameType = sameType, isAssignable = false, castSucceeded = false,
            };
            result.typeObservations.Add(row);
        }

        private static void RunBenchmark(Result result, bool enabled, Fixture fixture)
        {
            const int warmups = 1000, iterations = 100000;
            const string requestedName = "AssemblyA.Implementation.Internal.InternalEntry, AssemblyA.Implementation.Internal";
            Type first = Type.GetType(requestedName, true), last = first;
            Type benchmarkRepeat = Type.GetType(requestedName, true);
            if (enabled) ObserveTypeResolution(result, "benchmark-prewarm", first, System.Object.ReferenceEquals(first, benchmarkRepeat));
            for (int i = 0; i < warmups; ++i) last = Type.GetType(requestedName, true);
            long checksum = 0; Stopwatch timer = Stopwatch.StartNew();
            for (int i = 0; i < iterations; ++i)
            {
                last = Type.GetType(requestedName, true);
                if (last != null) checksum++;
            }
            timer.Stop();
            Require(last != null && checksum == iterations && System.Object.ReferenceEquals(first, last), "M05 benchmark type identity/checksum mismatch.");
            result.benchmark = new Benchmark { enabled = enabled, warmupCount = warmups, lookupCount = iterations, elapsedTicks = timer.ElapsedTicks, stopwatchFrequency = Stopwatch.Frequency, checksum = checksum, requestedName = requestedName, finalTypeName = last.FullName, finalAssemblyName = last.Assembly.GetName().Name, finalSameType = System.Object.ReferenceEquals(first, last) };
        }

        private static Type[] InvokeWitnessTypes(string assemblyName, string methodName)
        {
            Type type = WitnessOwner(assemblyName);
            switch (methodName)
            {
                case "GetM05Types": return InvokeTypeArray(type.GetMethod("GetM05Types", BindingFlags.Public | BindingFlags.Static), assemblyName, methodName);
                case "GetM05TypeNameForms": return InvokeTypeArray(type.GetMethod("GetM05TypeNameForms", BindingFlags.Public | BindingFlags.Static), assemblyName, methodName);
                case "GetM05CompositeTypes": return InvokeTypeArray(type.GetMethod("GetM05CompositeTypes", BindingFlags.Public | BindingFlags.Static), assemblyName, methodName);
                default: throw new ArgumentException("Unknown M05 type witness method: " + methodName);
            }
        }

        private static object InvokeWitnessObject(string assemblyName, string methodName)
        {
            Type type = WitnessOwner(assemblyName);
            switch (methodName)
            {
                case "GetM05InterfacePayload": return InvokeObject(type.GetMethod("GetM05InterfacePayload", BindingFlags.Public | BindingFlags.Static), assemblyName, methodName);
                case "GetM05InterfaceCastResult": return InvokeObject(type.GetMethod("GetM05InterfaceCastResult", BindingFlags.Public | BindingFlags.Static), assemblyName, methodName);
                case "GetM05Payload": return InvokeObject(type.GetMethod("GetM05Payload", BindingFlags.Public | BindingFlags.Static), assemblyName, methodName);
                case "GetM05CompositeArrays": return InvokeObject(type.GetMethod("GetM05CompositeArrays", BindingFlags.Public | BindingFlags.Static), assemblyName, methodName);
                default: throw new ArgumentException("Unknown M05 object witness method: " + methodName);
            }
        }

        private static Type[] InvokeTypeArray(MethodInfo method, string assemblyName, string methodName)
        {
            Require(method != null && method.ReturnType == typeof(Type[]), "M05 witness method missing: " + assemblyName + "." + methodName);
            return (Type[])method.Invoke(null, null);
        }

        private static object InvokeObject(MethodInfo method, string assemblyName, string methodName)
        {
            Require(method != null && method.ReturnType == typeof(object), "M05 object witness method missing: " + assemblyName + "." + methodName);
            return method.Invoke(null, null);
        }

        private static Type WitnessOwner(string assemblyName)
        {
            switch (assemblyName)
            {
                case Contracts: return Type.GetType("AssemblyA.Contracts.AssemblyAContractVersion, AssemblyA.Contracts", true);
                case Extensibility: return Type.GetType("AssemblyA.Implementation.Extensibility.VersionedComponentBase, AssemblyA.Implementation.Extensibility", true);
                case Internal: return Type.GetType("AssemblyA.Implementation.Internal.InternalEntry, AssemblyA.Implementation.Internal", true);
                case ContractsConsumer: return Type.GetType("AssemblyShadowDemo.Consumers.ContractsConsumer, AssemblyShadowDemo.ContractsConsumer", true);
                case ExtensibilityConsumer: return Type.GetType("AssemblyShadowDemo.Consumers.DerivedExternalComponent, AssemblyShadowDemo.ExtensibilityConsumer", true);
                default: throw new ArgumentException("Unknown M05 witness assembly: " + assemblyName);
            }
        }

        private static Assembly LoadAssembly(string name)
        {
            switch (name)
            {
                case Contracts: return Assembly.Load("AssemblyA.Contracts");
                case Extensibility: return Assembly.Load("AssemblyA.Implementation.Extensibility");
                case Internal: return Assembly.Load("AssemblyA.Implementation.Internal");
                case ContractsConsumer: return Assembly.Load("AssemblyShadowDemo.ContractsConsumer");
                case ExtensibilityConsumer: return Assembly.Load("AssemblyShadowDemo.ExtensibilityConsumer");
                default: throw new ArgumentException("Unknown M05 assembly: " + name);
            }
        }

        private static string ExpectedFullName(Input input, Fixture fixture, string name)
        {
            M04ReferenceProbe.AssemblyIdentity identity = fixture.assemblyIdentities.SingleOrDefault(item => item.name == name) ?? input.player.assemblyIdentities.Single(item => item.name == name);
            return identity.fullName;
        }

        private static void WriteEvidence(Result result)
        {
            string output = Path.GetFullPath(Argument("-shadowM05Result", Path.Combine(Application.persistentDataPath, "AssemblyShadowTests/m05-" + result.mode + ".json")));
            string directory = Path.GetDirectoryName(output); Directory.CreateDirectory(directory);
            if (!string.IsNullOrEmpty(result.nativeDiagnosticsJson))
            {
                string raw = Path.Combine(directory, Path.GetFileNameWithoutExtension(output) + "-native-diagnostics.json");
                using (var stream = new FileStream(raw, FileMode.CreateNew, FileAccess.Write, FileShare.None)) using (var writer = new StreamWriter(stream, new UTF8Encoding(false))) writer.Write(result.nativeDiagnosticsJson);
                result.rawDiagnosticsPath = raw; result.rawDiagnosticsSha256 = HashFile(raw);
            }
            using (var stream = new FileStream(output, FileMode.CreateNew, FileAccess.Write, FileShare.None)) using (var writer = new StreamWriter(stream, new UTF8Encoding(false))) writer.Write(JsonUtility.ToJson(result, true));
        }

        private static bool ModeHas(string mode, string prefix) { return mode.StartsWith(prefix, StringComparison.Ordinal); }
        private static bool IsKnownMode(string mode) { return Modes.Contains(mode, StringComparer.Ordinal); }
        private static string Argument(string name, string fallback) { string[] args = Environment.GetCommandLineArgs(); for (int i = 0; i + 1 < args.Length; ++i) if (args[i] == name) return args[i + 1]; return fallback; }
        private static bool IsIl2CppPlayer()
        {
#if ENABLE_IL2CPP && !UNITY_EDITOR
            return true;
#else
            return false;
#endif
        }
        private static bool IsHash(string value) { return value != null && value.Length == 64 && value.All(c => (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')); }
        private static bool IsResourceAbiHash(string value)
        {
            // ResourceAbiHasher emits a tagged semantic hash. Byte, Bootstrap
            // and runtime ABI hashes retain their separate bare-hex contract.
            const string prefix = "sha256:";
            return value != null && value.StartsWith(prefix, StringComparison.Ordinal) && IsHash(value.Substring(prefix.Length));
        }
        private static string HashFile(string path)
        {
            using (var sha = SHA256.Create())
            using (var stream = File.OpenRead(path))
                return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
        }
        private static string Hash(byte[] bytes) { using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant(); }
        private static bool ObjectEquals(object left, object right) { return System.Object.ReferenceEquals(left, right); }
        private static void Require(bool condition, string message) { if (!condition) throw new InvalidOperationException(message); }

        [Serializable, Preserve] private sealed class Input
        {
            [Preserve] public string manifestPath, playerReceiptPath;
            [Preserve] public FixtureManifest manifest;
            [Preserve] public PlayerBuildReceipt player;
            [Preserve] public TypeProof typeProof;
            [Preserve] public M04ReferenceProbe.AssemblyIdentity mscorlib;
        }
        [Serializable, Preserve] internal sealed class PatchManifest
        {
            [Preserve] public int schemaVersion, semanticHashSchema;
            [Preserve] public string patchId, baselineBuildId, baselineManifestSha256, runtimeAbiHash, compileSnapshotHash, unityVersion, target, architecture, bootstrapAbiHash, baselineResourceAbiHash, resourceAbiHash, signatureAlgorithm;
            [Preserve] public bool dllOnly, unsigned;
            [Preserve] public string[] loadOrder;
            [Preserve] public PatchAssembly[] closure;
        }
        [Serializable, Preserve] internal sealed class PatchAssembly
        {
            [Preserve] public string name, dll, sha256, pdb, pdbSha256, mvid, baselineMvid;
        }
        [Serializable, Preserve] private sealed class BaselineManifest
        {
            [Preserve] public int schemaVersion, semanticHashSchema;
            [Preserve] public string baselineBuildId, runtimeAbiHash, unityVersion, target, architecture, playerInputSnapshotHash, bootstrapAbiHash, resourceAbiHash, reflectionBindingConfigurationSha256;
            [Preserve] public string[] shadowCandidates;
            [Preserve] public BaselineAssembly[] assemblies;
        }
        [Serializable, Preserve] private sealed class BaselineAssembly { [Preserve] public string name, mvid; }
        [Serializable, Preserve] private sealed class SnapshotReceipt
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string kind, snapshotHash, unityVersion, target, architecture, buildGuid, nativeLibraryPath, nativeLibrarySha256;
            [Preserve] public bool playerBuildSucceeded, playerBuildFilterCaptured;
            [Preserve] public string[] extraScriptingDefines;
            [Preserve] public SnapshotFile[] assemblies, references, filteredAssemblies;
            [Preserve, NonSerialized] public string rawAdmissionHash;
        }
        [Serializable, Preserve] private sealed class SnapshotFile { [Preserve] public string name, path, sha256, pdbPath, pdbSha256; }

        [Serializable, Preserve] public sealed class Result
        {
            [Preserve] public int schemaVersion, processId;
            [Preserve] public string milestone, mode, result, error, unityVersion, platform, buildGuid, playerDataPath, baselineBuildId, runtimeAbiHash;
            [Preserve] public bool il2cpp;
            [Preserve] public string fixtureManifestPath, fixtureManifestSha256, playerBuildReceiptPath, playerBuildReceiptSha256, typeProofPath, typeProofSha256;
            [Preserve] public string patchId, patchManifestPath, patchManifestSha256, compileSnapshotHash, rawDiagnosticsPath, rawDiagnosticsSha256;
            [Preserve] public string moduleMvidObservationPolicy, businessMarker, configure, begin, stage, validate, commit, abort, stateCode, state, diagnosticsCode, executionModeCode, executionMode, allocationException, nativeDiagnosticsJson;
            [Preserve] public string[] stageOrder;
            [Preserve] public List<Check> checks;
            [Preserve] public List<Snapshot> snapshots;
            [Preserve] public List<AssemblyObservation> actualLogicalAssemblies, assemblyObservations;
            [Preserve] public List<TypeObservation> typeObservations;
            [Preserve] public List<TypeResolutionObservation> typeResolutionObservations;
            [Preserve] public List<TypeEnumeration> typeEnumerations;
            [Preserve] public List<MemberObservation> memberObservations;
            [Preserve] public List<IdentityObservation> identityObservations;
            [Preserve] public List<AssignabilityObservation> assignabilityObservations;
            [Preserve] public List<LoadObservation> loadObservations;
            [Preserve] public List<SceneObservation> sceneObservations;
            [Preserve] public List<StageResult> stageResults;
            [Preserve] public Benchmark benchmark;
            [Preserve] public M04OrdinaryAssemblyProbe.Result ordinary;
        }

        [Serializable, Preserve] public sealed class FixtureManifest
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string milestone, unityVersion, target, architecture, baselineManifestPath, baselineManifestSha256, baselineBuildId, runtimeAbiHash, baselineInputSnapshot, baselineInputSnapshotHash, stableAotProvenanceHash, stableAotProvenance;
            [Preserve] public string[] candidateNames, closureLoadOrder, stableAotNames;
            [Preserve] public Fixture[] fixtures;
            [Preserve] public NegativeRejectedFixture[] rejectedFixtures;
        }

        [Serializable, Preserve] public sealed class PlayerBuildReceipt
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string milestone, variant, baselineBuildId, runtimeAbiHash, unityVersion, target, architecture, buildGuid, playerOutput, inputSnapshot, inputSnapshotHash, nativeLibraryPath, nativeLibrarySha256, nativeArguments, placeholderManifestPath, placeholderManifestSha256, nativeMetadataPath, nativeMetadataSha256, typeProofPath, typeProofSha256;
            [Preserve] public int nativeMetadataVersion;
            [Preserve] public string[] placeholderAssemblyNames, nativeGeneratedAssemblyNames;
            [Preserve] public M04ReferenceProbe.AssemblyIdentity[] assemblyIdentities;
            [Preserve] public M04ReferenceProbe.NativeAssemblyIdentity[] nativeAssemblyIdentities;
        }

        [Serializable, Preserve] public sealed class Fixture
        {
            [Preserve] public string patchId, compileSnapshot, compileSnapshotHash, patchDirectory, patchManifest, patchManifestSha256;
            [Preserve] public string[] defines, changedRoots, closureLoadOrder, stableAotNames;
            [Preserve] public M04ReferenceProbe.AssemblyIdentity[] assemblyIdentities;
            [Preserve] public TypeInventory[] typeInventories;
            [Preserve, NonSerialized] internal string patchRoot;
            [Preserve, NonSerialized] internal PatchManifest patch;
        }

        [Serializable, Preserve] public sealed class TypeInventory
        {
            [Preserve] public string assemblyName;
            [Preserve] public TypeDefinition[] types;
        }

        [Serializable, Preserve] public sealed class TypeDefinition
        {
            [Preserve] public string fullName, namespaceName, name, kind;
            [Preserve] public string[] nestingPath;
            [Preserve] public int genericArity;
            [Preserve] public bool isExported;
        }

        [Serializable, Preserve] public sealed class NegativeRejectedFixture
        {
            [Preserve] public string fixtureId, compileSnapshot, compileSnapshotHash, errorCode, errorMessage, dllPath, dllSha256;
            [Preserve] public string[] defines, changedRoots;
            [Preserve] public M04ReferenceProbe.AssemblyIdentity assemblyIdentity;
            [Preserve] public TypeInventory typeInventory;
        }

        [Serializable, Preserve] public sealed class TypeProof
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string milestone, policy, compileSnapshotHash, linkedPlayerReceiptHash, nativeLibrarySha256, buildGuid;
            [Preserve] public bool developmentBuild;
            [Preserve] public TypeInventory[] assemblies;
            [Preserve] public MethodWitness[] moduleMethods;
        }
        [Serializable, Preserve] public sealed class MethodWitness
        {
            [Preserve] public string declaringType, name, signature;
            [Preserve] public bool hasBody;
            [Preserve] public int implementationFlags;
            [Preserve] public string[] instructions;
        }
        [Serializable, Preserve] public sealed class Check { [Preserve] public string name, actual, expected; [Preserve] public int actualCode, expectedCode; }
        [Serializable, Preserve] public sealed class Snapshot { [Preserve] public string phase; [Preserve] public AssemblyShadowDiagnostics diagnostics; }
        [Serializable, Preserve] public sealed class AssemblyObservation { [Preserve] public string name, fullName, mvid, executionCode, executionMode; [Preserve] public bool mvidAvailable, isInterpreter, logical; }
        [Serializable, Preserve] public sealed class TypeObservation { [Preserve] public string requested, fullName, assemblyName, kind, genericDefinition, elementShape; [Preserve] public string[] genericArguments; [Preserve] public bool isActive, sameType, isAssignable, castSucceeded; }
        [Serializable, Preserve] public sealed class TypeResolutionObservation { [Preserve] public string operation, requested, rawJson; [Preserve] public AssemblyShadowTypeResolutionInfo info; [Preserve] public bool sameType; }
        [Serializable, Preserve] public sealed class TypeEnumeration { [Preserve] public string operation, assemblyName; [Preserve] public string[] typeNames; }
        [Serializable, Preserve] public sealed class MemberObservation { [Preserve] public string declaringType, reflectedType, memberName, memberKind, returnType, fieldType; [Preserve] public string[] parameterTypes; [Preserve] public bool sameMember, activeOwner; }
        [Serializable, Preserve] public sealed class IdentityObservation { [Preserve] public string operation, left, right; [Preserve] public bool sameObject; }
        [Serializable, Preserve] public sealed class AssignabilityObservation { [Preserve] public string operation, sourceType, targetType, castMarker; [Preserve] public bool isAssignable, isInstance, castSucceeded; }
        [Serializable, Preserve] public sealed class LoadObservation { [Preserve] public string requested, overload, typeName, assemblyName; [Preserve] public bool sameAssembly, sameType; }
        [Serializable, Preserve] public sealed class SceneObservation { [Preserve] public string phase, bundleName, bundlePath, bundleSha256, scenePath, componentAssemblyName, componentType, businessMarker, error; [Preserve] public int serializedValue, baseSerializedValue, dataSerializedValue; [Preserve] public bool loaded, activeType, referenceIdentity; }
        [Serializable, Preserve] public sealed class StageResult { [Preserve] public string name, code, dllSha256, pdbSha256; }
        [Serializable, Preserve] public sealed class Benchmark { [Preserve] public bool enabled, finalSameType; [Preserve] public int warmupCount, lookupCount; [Preserve] public long elapsedTicks, stopwatchFrequency, checksum; [Preserve] public string requestedName, finalTypeName, finalAssemblyName; }
    }
}
