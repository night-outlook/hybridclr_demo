using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    /// <summary>Hash-bound transaction and evidence boundary for M07.</summary>
    [Preserve]
    public static partial class M07Probe
    {
        internal const int RuntimeAbiVersion = 1;
        internal static readonly string[] Candidates = {
            "AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility", "AssemblyA.Implementation.Internal",
            "AssemblyShadowDemo.ContractsConsumer", "AssemblyShadowDemo.ExtensibilityConsumer"
        };
        internal static readonly string[] BundleNames = {
            "additive-scene.bundle", "business-scene.bundle", "mixed-assets.bundle", "nested-prefab.bundle",
            "scriptable-object.bundle", "serialize-reference.bundle", "versioned-prefab.bundle"
        };
        private static readonly string[] Modes = {
            "T07-01-Prefab-P01", "T07-02-Nested-P02", "T07-03-FullClosure-P03", "T07-04-UnityApis-P01",
            "T07-05-Scriptable-P03", "T07-06-SceneSingle-P01", "T07-07-SceneAdditive-P03",
            "T07-08-SerializeReference-P03", "T07-09-Messages-P01", "T07-10-Cache-P03",
            "T07-11-DelayedCatalog-P03", "T07-12-P04-NonSerialized", "T07-13-P05-Rebuilt", "T07-14-FeatureOff"
        };

        private static Result s_active;
        private static bool s_inputsReady;

        public static IEnumerator RunAndWriteCoroutine(string expectedBaselineBuildId, string expectedRuntimeAbiHash, Action<int> completed)
        {
            string mode = Argument("-shadowM07Mode", Modes[0]);
            Result result = NewResult(mode, expectedBaselineBuildId, expectedRuntimeAbiHash);
            s_active = result;
            s_inputsReady = false;
            Require(IsIl2CppPlayer(), "M07 acceptance requires an actual IL2CPP Player.");
            Require(Modes.Contains(mode, StringComparer.Ordinal), "Unknown M07 mode: " + mode);
            Input input = ReadInputs(expectedBaselineBuildId, expectedRuntimeAbiHash, mode);
            s_inputsReady = true;
            result.fixtureManifestPath = input.manifestPath;
            result.fixtureManifestSha256 = HashFile(input.manifestPath);
            result.playerBuildReceiptPath = input.playerReceiptPath;
            result.playerBuildReceiptSha256 = HashFile(input.playerReceiptPath);
            result.baselineManifestPath = input.manifest.baselineManifestPath;
            result.baselineManifestSha256 = input.manifest.baselineManifestSha256;
            result.resourceReceiptPath = input.resourceReceiptPath;
            result.resourceReceiptSha256 = HashFile(input.resourceReceiptPath);
            result.baselineResourceAbiHash = input.baseline.resourceAbiHash;
            result.selectedResourceAbiHash = input.resources.resourceAbiHash;
            result.patchId = input.fixture == null ? "" : input.fixture.patchId;
            result.patchManifestPath = input.fixture == null ? "" : input.fixture.patchManifest;
            result.patchManifestSha256 = input.fixture == null ? "" : input.fixture.patchManifestSha256;
            result.resourcePrecheckPassed = true;
            result.resourcePrecheckPhase = "before-commit-before-business-resource-load";

            if (mode == "T07-14-FeatureOff") RunFeatureOff(result);
            else RunTransaction(result, input);

            IEnumerator resource = M07ResourceProbe.Run(result, input);
            try
            {
                while (true)
                {
                    bool moved;
                    try { moved = resource.MoveNext(); }
                    catch (Exception error) { throw new InvalidOperationException("M07 resource coroutine failed while advancing.", error); }
                    if (!moved) break;
                    yield return resource.Current;
                }
            }
            finally
            {
                var disposable = resource as IDisposable;
                if (disposable != null) disposable.Dispose();
            }
            if (mode != "T07-14-FeatureOff")
            {
                RequireState(result, AssemblyShadowState.Committed, "resource-complete");
                Capture(result, "final-resource");
                AssemblyShadowDiagnostics final = result.snapshots.Last().diagnostics;
                result.baselineUseCount = final.baselineUses == null ? -1 : final.baselineUses.Count(use =>
                    result.stageOrder.Contains(use.name, StringComparer.Ordinal));
                result.nativeEventCount = final.events == null ? -1 : final.events.Length;
                result.transactionGeneration = final.generation;
                Require(result.baselineUseCount == 0 && result.nativeEventCount > 0 && result.transactionGeneration > 0,
                    "M07 native resolver evidence is incomplete or the selected shadow closure used its AOT baseline.");
            }
            result.result = "Passed";
            int exitCode;
            try { WriteEvidence(result); exitCode = 0; }
            catch (Exception error) { UnityEngine.Debug.LogException(error); exitCode = 2; }
            if (completed != null) completed(exitCode);
        }

        public static int CompleteCoroutineFailure(Exception error)
        {
            Result result = s_active;
            if (result == null) return 2;
            result.error = error == null ? "M07 coroutine failed." : error.ToString();
            UnityEngine.Debug.LogException(error);
            if (s_inputsReady && result.mode != "T07-14-FeatureOff")
                try { Capture(result, "failure"); } catch (Exception diagnosticError) { result.error += "\nFailure diagnostics: " + diagnosticError; }
            try { WriteEvidence(result); return 1; }
            catch (Exception writeError) { UnityEngine.Debug.LogException(writeError); return 2; }
        }

        private static void RunTransaction(Result result, Input input)
        {
            Fixture fixture = input.fixture;
            Require(fixture != null, "M07 committed mode has no fixture.");
            result.configureCode = Expect(result, "configure", AssemblyShadowRuntime.ConfigureCandidates(
                input.manifest.baselineBuildId, input.manifest.candidateNames, input.manifest.stableAotNames));
            result.beginCode = Expect(result, "begin", AssemblyShadowRuntime.BeginTransaction(
                fixture.patchId, input.manifest.baselineBuildId, fixture.closureLoadOrder, RuntimeAbiVersion));
            RequireState(result, AssemblyShadowState.Staging, "staging");
            result.reserveMetadataBudget = ReserveMetadataBudget(result, input, fixture);
            foreach (string name in fixture.closureLoadOrder)
            {
                PatchAssembly assembly = input.patch.closure.Single(item => item.name == name);
                byte[] dll = File.ReadAllBytes(Confined(fixture.patchDirectory, assembly.dll));
                byte[] pdb = string.IsNullOrEmpty(assembly.pdb) ? null : File.ReadAllBytes(Confined(fixture.patchDirectory, assembly.pdb));
                string code = Expect(result, "stage-" + name, AssemblyShadowRuntime.StageAssembly(dll, pdb));
                result.stageResults.Add(new StageResult { name = name, code = code, dllSha256 = Hash(dll), pdbSha256 = pdb == null ? "" : Hash(pdb) });
            }
            result.stageOrder = fixture.closureLoadOrder.ToArray();
            Capture(result, "staged");
            result.validateCode = Expect(result, "validate", AssemblyShadowRuntime.ValidateTransaction());
            Capture(result, "validated-resource-precheck-complete");
            Require(result.resourcePrecheckPassed && !result.businessResourceLoadStarted, "M07 resource ABI precheck did not precede Commit and resource loading.");
            result.commitCode = Expect(result, "commit", AssemblyShadowRuntime.CommitTransaction());
            RequireState(result, AssemblyShadowState.Committed, "committed");
            CaptureAssemblyModes(result, false);
            result.commitCompletedBeforeResourceLoad = !result.businessResourceLoadStarted;
            Require(result.commitCompletedBeforeResourceLoad, "M07 business resource loading began before Commit.");
            Capture(result, "committed-before-resources");
        }

        private static void RunFeatureOff(Result result)
        {
            AssemblyShadowState state; AssemblyExecutionMode executionMode; string diagnostics; string typeInfo; string executionDiagnostics;
            result.configureCode = Expect(result, "configure", AssemblyShadowRuntime.ConfigureCandidates(null, null, null), AssemblyShadowErrorCode.FeatureDisabled);
            result.beginCode = Expect(result, "begin", AssemblyShadowRuntime.BeginTransaction(null, null, null, -1), AssemblyShadowErrorCode.FeatureDisabled);
            result.stageProbeCode = Expect(result, "stage", AssemblyShadowRuntime.StageAssembly(null, null), AssemblyShadowErrorCode.FeatureDisabled);
            result.validateCode = Expect(result, "validate", AssemblyShadowRuntime.ValidateTransaction(), AssemblyShadowErrorCode.FeatureDisabled);
            result.commitCode = Expect(result, "commit", AssemblyShadowRuntime.CommitTransaction(), AssemblyShadowErrorCode.FeatureDisabled);
            result.abortCode = Expect(result, "abort", AssemblyShadowRuntime.AbortTransaction(), AssemblyShadowErrorCode.FeatureDisabled);
            string code = Expect(result, "state", AssemblyShadowRuntime.GetState(out state), AssemblyShadowErrorCode.FeatureDisabled);
            result.stateCode = code;
            result.state = state.ToString();
            result.executionModeCode = Expect(result, "execution-mode", AssemblyShadowRuntime.GetAssemblyExecutionMode(null, out executionMode), AssemblyShadowErrorCode.FeatureDisabled);
            result.diagnosticsCode = Expect(result, "diagnostics", AssemblyShadowRuntime.GetDiagnosticsJson(out diagnostics), AssemblyShadowErrorCode.FeatureDisabled);
            result.typeResolutionCode = Expect(result, "type-resolution", AssemblyShadowRuntime.GetTypeResolutionInfo(null, out typeInfo), AssemblyShadowErrorCode.FeatureDisabled);
            result.executionDiagnosticsCode = Expect(result, "execution-diagnostics", AssemblyShadowRuntime.GetExecutionDiagnosticsJson(out executionDiagnostics), AssemblyShadowErrorCode.FeatureDisabled);
            AssemblyShadowDiagnostics disabled = null;
            Require(state == AssemblyShadowState.Disabled && executionMode == AssemblyExecutionMode.AotBaseline &&
                AssemblyShadowDiagnostics.TryParse(diagnostics, out disabled) && disabled != null && !disabled.enabled && disabled.state == "Disabled" &&
                string.IsNullOrEmpty(typeInfo) && string.IsNullOrEmpty(executionDiagnostics), "M07 feature-OFF outputs changed.");
            result.nativeDiagnosticsJson = diagnostics;
            result.snapshots.Add(new Snapshot { phase = "disabled", diagnostics = disabled });
            CaptureAssemblyModes(result, true);
            result.commitCompletedBeforeResourceLoad = true;
        }

        private static void CaptureAssemblyModes(Result result, bool featureOff)
        {
            foreach (string name in Candidates)
            {
                AssemblyExecutionMode mode;
                AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetAssemblyExecutionMode(name, out mode);
                bool expectedShadow = !featureOff && result.stageOrder.Contains(name, StringComparer.Ordinal);
                AssemblyShadowErrorCode expectedCode = featureOff ? AssemblyShadowErrorCode.FeatureDisabled : AssemblyShadowErrorCode.Success;
                AssemblyExecutionMode expectedMode = expectedShadow ? AssemblyExecutionMode.InterpreterShadow : AssemblyExecutionMode.AotBaseline;
                bool validCode = code == expectedCode || !featureOff && !expectedShadow && code == AssemblyShadowErrorCode.CandidateNotRegistered;
                Verify(result, "assembly-mode-" + name, validCode && mode == expectedMode, code + ":" + mode,
                    (featureOff ? "FeatureDisabled" : expectedShadow ? "Success" : "Success|CandidateNotRegistered") + ":" + expectedMode);
                result.assemblyModes.Add(new AssemblyModeObservation { name = name, code = code.ToString(), mode = mode.ToString(), expectedShadow = expectedShadow });
            }
        }

        private static Input ReadInputs(string expectedBaseline, string expectedAbi, string mode)
        {
            string manifestPath = Path.GetFullPath(Argument("-shadowM07Fixtures", ""));
            string playerPath = Path.GetFullPath(Argument("-shadowM07PlayerReceipt", ""));
            Require(File.Exists(manifestPath) && File.Exists(playerPath), "M07 fixture manifest and Player receipt are required.");
            FixtureManifest manifest = JsonUtility.FromJson<FixtureManifest>(File.ReadAllText(manifestPath));
            PlayerBuildReceipt player = JsonUtility.FromJson<PlayerBuildReceipt>(File.ReadAllText(playerPath));
            Require(manifest != null && manifest.schemaVersion == 1 && manifest.milestone == "M07" && player != null && player.schemaVersion == 1 && player.milestone == "M07",
                "M07 fixture or Player receipt schema differs.");
            Require(!string.IsNullOrEmpty(expectedBaseline) && IsHash(expectedAbi) && manifest.baselineBuildId == expectedBaseline && manifest.runtimeAbiHash == expectedAbi &&
                player.baselineBuildId == expectedBaseline && player.runtimeAbiHash == expectedAbi, "M07 embedded baseline/runtime ABI identity differs.");
            Require(manifest.unityVersion == Application.unityVersion && player.unityVersion == Application.unityVersion && manifest.target == player.target &&
                manifest.architecture == player.architecture && player.buildGuid == Application.buildGUID,
                "M07 executed Player Unity/target/build GUID differs from its receipt.");
            Require(manifest.candidateNames != null && manifest.candidateNames.SequenceEqual(Candidates) && manifest.bundleNames != null && manifest.bundleNames.SequenceEqual(BundleNames) &&
                manifest.stableAotNames != null && manifest.stableAotNames.Length > 0 && manifest.stableAotNames.SequenceEqual(manifest.stableAotNames.OrderBy(value => value, StringComparer.Ordinal)) &&
                !manifest.stableAotNames.Intersect(Candidates, StringComparer.OrdinalIgnoreCase).Any(), "M07 candidate/stable-AOT/bundle inventory differs.");
            ValidateFile(manifest.baselineManifestPath, manifest.baselineManifestSha256);
            BaselineManifest baseline = JsonUtility.FromJson<BaselineManifest>(File.ReadAllText(manifest.baselineManifestPath));
            Require(baseline != null && baseline.schemaVersion == 1 && baseline.semanticHashSchema == 1 && baseline.baselineBuildId == expectedBaseline &&
                baseline.runtimeAbiHash == expectedAbi && baseline.playerInputSnapshotHash == manifest.baselineInputSnapshotHash &&
                baseline.shadowCandidates.SequenceEqual(Candidates) && baseline.bundles.Select(item => item.name).SequenceEqual(BundleNames), "M07 baseline manifest identity differs.");
            ValidatePlayer(player, mode == "T07-14-FeatureOff" ? "NativeOff" : "NativeOn");
            if (mode != "T07-14-FeatureOff")
            {
                Require(playerPath == Path.GetFullPath(manifest.playerBuildReceiptPath) && HashFile(playerPath) == manifest.playerBuildReceiptSha256,
                    "M07 native-ON Player receipt differs from the fixture manifest.");
            }
            string baselineRoot = Path.GetDirectoryName(manifest.baselineManifestPath);
            string baselineResourceRoot = Confined(baselineRoot, baseline.resourceBaselinePath);
            string baselineResourceReceipt = Confined(baselineResourceRoot, "resource-build-receipt.json");
            Require(HashFile(baselineResourceReceipt) == baseline.resourceBuildReceiptHash, "M07 baseline resource receipt changed.");
            ResourceReceipt resources = ValidateResourceReceipt(baselineResourceRoot, baselineResourceReceipt, baseline.resourceAbiHash, manifest);
            string playerResourceRoot = Path.GetFullPath(player.resourceBaselinePath);
            string playerResourceReceipt = Confined(playerResourceRoot, "resource-build-receipt.json");
            Require(Path.GetFullPath(player.resourceBuildReceiptPath) == playerResourceReceipt &&
                player.resourceBuildReceiptSha256 == baseline.resourceBuildReceiptHash &&
                HashFile(playerResourceReceipt) == player.resourceBuildReceiptSha256 && player.resourceAbiHash == baseline.resourceAbiHash,
                "M07 Player receipt is not byte-bound to the selected baseline resource catalog.");
            ResourceReceipt playerResources = ValidateResourceReceipt(playerResourceRoot, playerResourceReceipt, player.resourceAbiHash, manifest);
            Require(playerResources.bundles.Select(item => item.name + ":" + item.sha256)
                .SequenceEqual(resources.bundles.Select(item => item.name + ":" + item.sha256)),
                "M07 frozen and baseline-copied resource bundle bytes differ.");
            Fixture fixture = mode == "T07-14-FeatureOff" ? null : SelectFixture(manifest, mode);
            PatchManifest patch = null;
            string resourceRoot = baselineResourceRoot;
            string resourceReceipt = baselineResourceReceipt;
            if (fixture != null)
            {
                ValidateFile(fixture.patchManifest, fixture.patchManifestSha256);
                patch = JsonUtility.FromJson<PatchManifest>(File.ReadAllText(fixture.patchManifest));
                Require(patch != null && patch.schemaVersion == 1 && patch.semanticHashSchema == 1 && patch.patchId == fixture.patchId &&
                    patch.baselineBuildId == expectedBaseline && patch.baselineManifestSha256 == manifest.baselineManifestSha256 && patch.runtimeAbiHash == expectedAbi &&
                    patch.compileSnapshotHash == fixture.compileSnapshotHash && patch.loadOrder.SequenceEqual(fixture.closureLoadOrder) && patch.closure.Length == fixture.closureLoadOrder.Length &&
                    fixture.assemblyIdentities != null && fixture.assemblyIdentities.Length == patch.closure.Length && baseline.assemblies != null &&
                    patch.baselineResourceAbiHash == baseline.resourceAbiHash && patch.resourceAbiHash == fixture.resourceAbiHash && patch.dllOnly == fixture.dllOnly,
                    "M07 selected patch identity differs: " + fixture.patchId);
                foreach (PatchAssembly assembly in patch.closure)
                {
                    ValidateFile(Confined(fixture.patchDirectory, assembly.dll), assembly.sha256);
                    if (!string.IsNullOrEmpty(assembly.pdb)) ValidateFile(Confined(fixture.patchDirectory, assembly.pdb), assembly.pdbSha256);
                    AssemblyIdentity identity = fixture.assemblyIdentities.Single(item => item.name == assembly.name);
                    BaselineAssembly baselineAssembly = baseline.assemblies.Single(item => item.name == assembly.name);
                    Require(identity.sha256 == assembly.sha256 && identity.mvid == assembly.mvid && assembly.baselineMvid == baselineAssembly.mvid,
                        "M07 patch assembly identity is not byte/prelink-bound: " + assembly.name);
                }
                if (fixture.patchId == "P05")
                {
                    Require(!patch.dllOnly && patch.resourceAbiHash != patch.baselineResourceAbiHash && patch.resourceBundlesRequired.Length > 0,
                        "M07 P05 is not a structural resource replacement.");
                    string fixtureRoot = Path.GetFullPath(Path.GetDirectoryName(fixture.patchDirectory));
                    resourceRoot = Path.GetFullPath(fixture.replacementResourcePath);
                    Require(IsChild(fixtureRoot, resourceRoot), "M07 P05 replacement resources escape the fixture root.");
                    resourceReceipt = Path.GetFullPath(fixture.replacementResourceReceiptPath);
                    ValidateFile(resourceReceipt, fixture.replacementResourceReceiptSha256);
                    resources = ValidateResourceReceipt(resourceRoot, resourceReceipt, patch.resourceAbiHash, manifest);
                    Require(patch.resourceBundlesRequired.All(name => resources.bundles.Any(item => item.name == name)),
                        "M07 P05 replacement catalog omits a required bundle.");
                }
                else Require(patch.dllOnly && patch.resourceAbiHash == baseline.resourceAbiHash && patch.resourceBundlesRequired.Length == 0,
                    "M07 DLL-only patch changed resource ABI.");
            }
            return new Input { manifestPath = manifestPath, playerReceiptPath = playerPath, manifest = manifest, player = player,
                baseline = baseline, fixture = fixture, patch = patch, resourceRoot = resourceRoot, resourceReceiptPath = resourceReceipt, resources = resources };
        }

        private static Fixture SelectFixture(FixtureManifest manifest, string mode)
        {
            string patchId = mode.Contains("P05") ? "P05" : mode.Contains("P04") ? "P04" : mode.EndsWith("P02", StringComparison.Ordinal) ? "P02" :
                mode.EndsWith("P03", StringComparison.Ordinal) ? "P03" : "P01";
            return manifest.fixtures.Single(item => item.patchId == patchId);
        }

        private static void ValidatePlayer(PlayerBuildReceipt player, string variant)
        {
            Require(player.variant == variant && player.inputSnapshotHash != null && IsHash(player.inputSnapshotHash) &&
                File.Exists(player.nativeLibraryPath) && HashFile(player.nativeLibraryPath) == player.nativeLibrarySha256 &&
                File.Exists(player.nativeMetadataPath) && HashFile(player.nativeMetadataPath) == player.nativeMetadataSha256 && player.nativeMetadataVersion == 31 &&
                player.nativeArguments == "--compiler-flags=\"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=" + (variant == "NativeOn" ? "1" : "0") + "\"" &&
                player.bundleNames != null && player.bundleNames.SequenceEqual(BundleNames), "M07 executed Player artifact identity differs.");
            Require(PlayerOwnsDataPath(player.playerOutput, Application.dataPath), "M07 receipt is not for the executed Player path.");
            Require(Path.IsPathRooted(player.inputSnapshot) && Directory.Exists(player.inputSnapshot), "M07 Player input snapshot is unavailable.");
            ValidateFile(player.placeholderManifestPath, player.placeholderManifestSha256);
            Require(player.placeholderAssemblyNames != null && player.placeholderAssemblyNames.Length > 0 &&
                player.placeholderAssemblyNames.All(name => !string.IsNullOrEmpty(name)), "M07 placeholder assembly inventory is empty.");
            Require(player.assemblyIdentities != null && player.assemblyIdentities.Length > 0 &&
                player.assemblyIdentities.Select(item => item.name).Distinct(StringComparer.OrdinalIgnoreCase).Count() == player.assemblyIdentities.Length,
                "M07 linked Player assembly inventory is empty or ambiguous.");
            foreach (AssemblyIdentity identity in player.assemblyIdentities)
                Require(identity != null && !string.IsNullOrEmpty(identity.name) && Path.IsPathRooted(identity.path) && IsHash(identity.sha256) &&
                    File.Exists(identity.path) && HashFile(identity.path) == identity.sha256, "M07 linked Player identity is not byte-bound.");
            ValidateNativeMetadataReceipt(player);
        }

        private static void ValidateNativeMetadataReceipt(PlayerBuildReceipt player)
        {
            string metadataPath = Path.GetFullPath(player.nativeMetadataPath);
            Require(Path.IsPathRooted(player.nativeMetadataPath) && Path.GetFileName(metadataPath) == "global-metadata.dat" &&
                Directory.GetFiles(Application.dataPath, "global-metadata.dat", SearchOption.AllDirectories).Select(Path.GetFullPath)
                    .SequenceEqual(new[] { metadataPath }), "M07 native metadata is not the unique executed-Player metadata file.");
            Require(player.nativeAssemblyIdentities != null && player.nativeAssemblyIdentities.Length > 0 &&
                player.nativeGeneratedAssemblyNames != null && player.nativeGeneratedAssemblyNames.Length > 0 &&
                player.nativeGeneratedAssemblyNames.All(name => !string.IsNullOrEmpty(name)), "M07 native metadata inventories are empty.");
            foreach (NativeAssemblyIdentity identity in player.nativeAssemblyIdentities)
                Require(identity != null && identity.assemblyIndex >= 0 && identity.imageIndex >= 0 && !string.IsNullOrEmpty(identity.imageName) &&
                    !string.IsNullOrEmpty(identity.name) && !string.IsNullOrEmpty(identity.fullName), "M07 native metadata identity is incomplete.");
        }

        private static bool PlayerOwnsDataPath(string playerOutput, string dataPath)
        {
            string output = Path.GetFullPath(playerOutput).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            string data = Path.GetFullPath(dataPath).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            if (Directory.Exists(output) || output.EndsWith(".app", StringComparison.OrdinalIgnoreCase))
                return IsChild(output, data);
            string directory = Path.GetDirectoryName(output);
            string expected = Path.Combine(directory, Path.GetFileNameWithoutExtension(output) + "_Data");
            return string.Equals(Path.GetFullPath(expected), data, StringComparison.Ordinal);
        }

        private static bool IsChild(string root, string path)
        {
            string prefix = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar;
            return Path.GetFullPath(path).StartsWith(prefix, StringComparison.Ordinal);
        }

        private static ResourceReceipt ValidateResourceReceipt(string root, string path, string expectedAbi, FixtureManifest manifest)
        {
            Require(Path.GetFullPath(path) == Confined(root, "resource-build-receipt.json"), "M07 resource receipt escapes its root.");
            ResourceReceipt receipt = JsonUtility.FromJson<ResourceReceipt>(File.ReadAllText(path));
            Require(receipt != null && receipt.schemaVersion == 1 && receipt.unityVersion == manifest.unityVersion && receipt.target == manifest.target &&
                receipt.architecture == manifest.architecture && receipt.resourceAbiHash == expectedAbi && receipt.bundleDirectory == "Bundles" &&
                receipt.bundles != null && receipt.bundles.Select(item => item.name).SequenceEqual(BundleNames), "M07 resource receipt identity/bundle set differs.");
            foreach (ResourceBundle bundle in receipt.bundles) ValidateFile(Confined(root, receipt.bundleDirectory + "/" + bundle.name), bundle.sha256);
            return receipt;
        }

        private static string Capture(Result result, string phase)
        {
            string json;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetDiagnosticsJson(out json);
            Require(code == AssemblyShadowErrorCode.Success && !string.IsNullOrEmpty(json), "M07 diagnostics query failed: " + code);
            AssemblyShadowDiagnostics diagnostics;
            Require(AssemblyShadowDiagnostics.TryParse(json, out diagnostics), "M07 diagnostics JSON is malformed.");
            result.nativeDiagnosticsJson = json;
            result.snapshots.Add(new Snapshot { phase = phase, diagnostics = diagnostics });
            return code.ToString();
        }

        private static void RequireState(Result result, AssemblyShadowState expected, string phase)
        {
            AssemblyShadowState state;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetState(out state);
            result.stateCode = code.ToString();
            result.state = state.ToString();
            Require(code == AssemblyShadowErrorCode.Success && state == expected, "M07 " + phase + " state differs: " + state);
        }

        internal static string Expect(Result result, string name, AssemblyShadowErrorCode actual, AssemblyShadowErrorCode expected = AssemblyShadowErrorCode.Success)
        {
            result.checks.Add(new Check { name = name, actual = actual.ToString(), expected = expected.ToString(), passed = actual == expected });
            Require(actual == expected, "M07 " + name + " returned " + actual + ", expected " + expected);
            return actual.ToString();
        }

        internal static void Verify(Result result, string name, bool passed, string actual, string expected)
        {
            result.checks.Add(new Check { name = name, actual = actual, expected = expected, passed = passed });
            Require(passed, "M07 check failed: " + name + "; actual=" + actual + "; expected=" + expected);
        }

        private static Result NewResult(string mode, string baseline, string runtimeAbi)
        {
            return new Result {
                schemaVersion = 1, milestone = "M07", mode = mode, result = "Failed", error = "", il2cpp = IsIl2CppPlayer(),
                unityVersion = Application.unityVersion, platform = Application.platform.ToString(), buildGuid = Application.buildGUID,
                playerDataPath = Application.dataPath, processId = Process.GetCurrentProcess().Id, baselineBuildId = baseline, runtimeAbiHash = runtimeAbi,
                stageOrder = new string[0], checks = new List<Check>(), stageResults = new List<StageResult>(), snapshots = new List<Snapshot>(),
                bundles = new List<BundleObservation>(), assets = new List<AssetObservation>(), scenes = new List<SceneObservation>(),
                typeResolutions = new List<TypeResolutionObservation>(), cacheEvents = new List<CacheObservation>(), assemblyModes = new List<AssemblyModeObservation>(),
            };
        }

        private static void WriteEvidence(Result result)
        {
            string output = Path.GetFullPath(Argument("-shadowM07Result", Path.Combine(Application.persistentDataPath, "AssemblyShadowTests/m07-" + result.mode + ".json")));
            string directory = Path.GetDirectoryName(output);
            Directory.CreateDirectory(directory);
            if (!string.IsNullOrEmpty(result.nativeDiagnosticsJson))
            {
                string raw = Path.Combine(directory, Path.GetFileNameWithoutExtension(output) + "-diagnostics.json");
                using (var stream = new FileStream(raw, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                using (var writer = new StreamWriter(stream, new UTF8Encoding(false))) writer.Write(result.nativeDiagnosticsJson);
                result.rawDiagnosticsPath = raw;
                result.rawDiagnosticsSha256 = HashFile(raw);
            }
            using (var stream = new FileStream(output, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(stream, new UTF8Encoding(false))) writer.Write(JsonUtility.ToJson(result, true));
        }

        internal static string Confined(string root, string relative)
        {
            Require(!string.IsNullOrEmpty(root) && !string.IsNullOrEmpty(relative), "M07 confined path is missing.");
            string prefix = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
            string full = Path.GetFullPath(Path.IsPathRooted(relative) ? relative : Path.Combine(root, relative));
            Require(full.StartsWith(prefix, StringComparison.Ordinal), "M07 path escapes its declared root: " + relative);
            return full;
        }

        private static string ReserveMetadataBudget(Result result, Input input, Fixture fixture)
        {
            AssemblyShadowErrorCode code;
            bool declared = ShadowPatchMetadataReservation.ReserveIfDeclared(
                input.patch.nativeBudgetCapabilityVersion, input.patch.metadataEncodingProfile, input.patch.metadataCapacityReport,
                input.patch.loadOrder, input.patch.closure.Select(item => new ShadowPatchMetadataAssembly { name = item.name, dllSize = item.dllSize }).ToArray(),
                name => ReadVerifiedDll(input.patch, fixture, name), out code);
            return declared ? Expect(result, "reserve-metadata-budget", code) : null;
        }

        private static byte[] ReadVerifiedDll(PatchManifest patch, Fixture fixture, string name)
        {
            PatchAssembly assembly = patch.closure.Single(item => item.name == name);
            byte[] dll = File.ReadAllBytes(Confined(fixture.patchDirectory, assembly.dll));
            Require(Hash(dll) == assembly.sha256, "M07 patch DLL hash mismatch: " + name);
            return dll;
        }

        internal static void ValidateFile(string path, string expectedHash)
        {
            Require(File.Exists(path) && IsHash(expectedHash) && HashFile(path) == expectedHash, "M07 artifact hash differs: " + path);
        }

        internal static string HashFile(string path) { return Hash(File.ReadAllBytes(path)); }
        internal static string Hash(byte[] bytes) { using (var algorithm = SHA256.Create()) return BitConverter.ToString(algorithm.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant(); }
        internal static bool IsHash(string value) { return value != null && value.Length == 64 && value.All(c => c >= '0' && c <= '9' || c >= 'a' && c <= 'f'); }
        internal static string Argument(string name, string fallback) { string[] args = Environment.GetCommandLineArgs(); for (int i = 0; i + 1 < args.Length; ++i) if (args[i] == name) return args[i + 1]; return fallback; }
        internal static void Require(bool value, string message) { if (!value) throw new InvalidOperationException(message); }

        private static bool IsIl2CppPlayer()
        {
#if ENABLE_IL2CPP && !UNITY_EDITOR
            return true;
#else
            return false;
#endif
        }

        internal sealed class Input
        {
            public string manifestPath, playerReceiptPath, resourceRoot, resourceReceiptPath;
            public FixtureManifest manifest;
            public PlayerBuildReceipt player;
            public BaselineManifest baseline;
            public Fixture fixture;
            public PatchManifest patch;
            public ResourceReceipt resources;
        }

        [Serializable, Preserve] public sealed class Result
        {
            [Preserve] public int schemaVersion, processId;
            [Preserve] public string milestone, mode, result, error, unityVersion, platform, buildGuid, playerDataPath, baselineBuildId, runtimeAbiHash;
            [Preserve] public string fixtureManifestPath, fixtureManifestSha256, playerBuildReceiptPath, playerBuildReceiptSha256;
            [Preserve] public string baselineManifestPath, baselineManifestSha256, patchId, patchManifestPath, patchManifestSha256;
            [Preserve] public string resourceReceiptPath, resourceReceiptSha256, baselineResourceAbiHash, selectedResourceAbiHash, resourcePrecheckPhase;
            [Preserve] public bool il2cpp, resourcePrecheckPassed, commitCompletedBeforeResourceLoad, businessResourceLoadStarted;
            [Preserve] public string configureCode, beginCode, reserveMetadataBudget, stageProbeCode, validateCode, commitCode, abortCode, stateCode, state;
            [Preserve] public string executionModeCode, diagnosticsCode, typeResolutionCode, executionDiagnosticsCode, nativeDiagnosticsJson;
            [Preserve] public string rawDiagnosticsPath, rawDiagnosticsSha256, unityPathJson, monoScriptClass, monoScriptAssembly, graphType, graphDescription;
            [Preserve] public string serializedState, lifecycleBefore, lifecycleAfter, sceneLifecycleAfter;
            [Preserve] public int graphSum, p04RuntimeValue, p05SerializedValue, baselineUseCount, nativeEventCount;
            [Preserve] public ulong transactionGeneration;
            [Preserve] public string[] stageOrder;
            [Preserve] public List<Check> checks;
            [Preserve] public List<StageResult> stageResults;
            [Preserve] public List<Snapshot> snapshots;
            [Preserve] public List<BundleObservation> bundles;
            [Preserve] public List<AssetObservation> assets;
            [Preserve] public List<SceneObservation> scenes;
            [Preserve] public List<TypeResolutionObservation> typeResolutions;
            [Preserve] public List<CacheObservation> cacheEvents;
            [Preserve] public List<AssemblyModeObservation> assemblyModes;
        }
        [Serializable, Preserve] public sealed class Check { [Preserve] public string name, actual, expected; [Preserve] public bool passed; }
        [Serializable, Preserve] public sealed class StageResult { [Preserve] public string name, code, dllSha256, pdbSha256; }
        [Serializable, Preserve] public sealed class Snapshot { [Preserve] public string phase; [Preserve] public AssemblyShadowDiagnostics diagnostics; }
        [Serializable, Preserve] public sealed class BundleObservation { [Preserve] public string name, path, sha256; [Preserve] public int assetCount, sceneCount; [Preserve] public bool loaded, unloaded; }
        [Serializable, Preserve] public sealed class AssetObservation { [Preserve] public string phase, bundle, assetName, typeName, assemblyName, marker, serializedState; [Preserve] public bool active, instantiated; }
        [Serializable, Preserve] public sealed class SceneObservation { [Preserve] public string phase, bundle, scenePath, componentType, marker, serializedState, lifecycle; [Preserve] public bool loaded, additive, activationDelayed, unloaded; }
        [Serializable, Preserve] public sealed class TypeResolutionObservation { [Preserve] public string phase, typeName, assemblyName, code, executionMode, rawJson; [Preserve] public bool sameType, active; }
        [Serializable, Preserve] public sealed class CacheObservation { [Preserve] public string operation, typeName, marker; [Preserve] public bool active, distinctInstance; }
        [Serializable, Preserve] public sealed class AssemblyModeObservation { [Preserve] public string name, code, mode; [Preserve] public bool expectedShadow; }

        [Serializable, Preserve] internal sealed class FixtureManifest
        {
            public int schemaVersion; public string milestone, unityVersion, target, architecture, baselineBuildId, runtimeAbiHash;
            public string baselineManifestPath, baselineManifestSha256, baselineInputSnapshot, baselineInputSnapshotHash;
            public string playerBuildReceiptPath, playerBuildReceiptSha256; public string[] candidateNames, bundleNames, stableAotNames;
            public string stableAotProvenance, stableAotProvenanceHash; public Fixture[] fixtures; public RejectedFixture[] rejectedFixtures;
        }
        [Serializable, Preserve] internal sealed class Fixture
        {
            public string patchId; public string[] defines, changedRoots; public string compileSnapshot, compileSnapshotHash, patchDirectory, patchManifest, patchManifestSha256;
            public string[] closureLoadOrder; public string baselineResourceAbiHash, resourceAbiHash, resourceChangeLevel; public bool dllOnly;
            public string[] resourceBundlesRequired; public string replacementResourcePath, replacementResourceReceiptPath, replacementResourceReceiptSha256; public string[] replacementBundleNames;
            public AssemblyIdentity[] assemblyIdentities;
        }
        [Serializable, Preserve] internal sealed class RejectedFixture { public string patchId, compileSnapshot, compileSnapshotHash, errorCode, errorMessage; public string[] defines, changedRoots; }
        [Serializable, Preserve] internal sealed class PlayerBuildReceipt
        {
            public int schemaVersion; public string milestone, variant, baselineBuildId, runtimeAbiHash, unityVersion, target, architecture, buildGuid, playerOutput;
            public string inputSnapshot, inputSnapshotHash, nativeLibraryPath, nativeLibrarySha256, nativeArguments, nativeMetadataPath, nativeMetadataSha256;
            public int nativeMetadataVersion; public string placeholderManifestPath, placeholderManifestSha256; public string[] placeholderAssemblyNames;
            public AssemblyIdentity[] assemblyIdentities; public NativeAssemblyIdentity[] nativeAssemblyIdentities; public string[] nativeGeneratedAssemblyNames;
            public string resourceBaselinePath, resourceBuildReceiptPath, resourceBuildReceiptSha256, resourceAbiHash; public string[] bundleNames;
        }
        [Serializable, Preserve] internal sealed class BaselineManifest
        {
            public int schemaVersion, semanticHashSchema; public string baselineBuildId, unityVersion, target, architecture, runtimeAbiHash, resourceAbiHash;
            public string resourceBaselinePath, resourceBuildReceiptHash, playerInputSnapshotHash; public string[] shadowCandidates; public ResourceBundle[] bundles;
            public BaselineAssembly[] assemblies;
        }
        [Serializable, Preserve] internal sealed class BaselineAssembly { public string name, mvid; }
        [Serializable, Preserve] internal sealed class PatchManifest
        {
            [Preserve] public int schemaVersion, semanticHashSchema, nativeBudgetCapabilityVersion; [Preserve] public string patchId, baselineBuildId, baselineManifestSha256, runtimeAbiHash, compileSnapshotHash;
            [Preserve] public string baselineResourceAbiHash, resourceAbiHash, resourceChangeLevel; [Preserve] public bool dllOnly; [Preserve] public string[] resourceBundlesRequired, changedRoots, loadOrder; [Preserve] public PatchAssembly[] closure;
            [Preserve] public ShadowPatchMetadataEncodingProfile metadataEncodingProfile; [Preserve] public ShadowPatchMetadataCapacityReport metadataCapacityReport;
        }
        [Serializable, Preserve] internal sealed class PatchAssembly { [Preserve] public string name, dll, sha256, pdb, pdbSha256, mvid, baselineMvid; [Preserve] public ulong dllSize; }
        [Serializable, Preserve] internal sealed class ResourceReceipt
        {
            public int schemaVersion; public string provenance, unityVersion, target, architecture, resourceAbiHash, bundleDirectory; public ResourceBundle[] bundles;
        }
        [Serializable, Preserve] internal sealed class ResourceBundle { public string name, sha256; public string[] assets; }
        [Serializable, Preserve] internal sealed class AssemblyIdentity
        {
            public string name, fullName, version, culture, publicKeyToken, mvid, path, sha256;
            public ReferenceIdentity[] referenceIdentities;
        }
        [Serializable, Preserve] internal sealed class ReferenceIdentity
        {
            public int referenceIndex; public string name, fullName, version, culture, publicKeyToken;
        }
        [Serializable, Preserve] internal sealed class NativeAssemblyIdentity
        {
            public int assemblyIndex, imageIndex; public uint token; public string imageName, name, fullName, version, culture, publicKeyToken;
        }
    }
}
