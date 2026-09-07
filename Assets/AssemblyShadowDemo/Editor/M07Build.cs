using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using AssemblyShadowBaseline.Editor;
using HybridCLR.Editor.AssemblyShadow;
using HybridCLR.Editor.Commands;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Builds the M07 Player, seven-bundle baseline, and patch fixtures.</summary>
    public static class M07Build
    {
        public const string BootstrapScene = "Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity";
        public const string ResourceMapPath = "ProjectSettings/AssemblyShadowResourcesM07.json";
        public const string DefaultBaselineId = "M07-Baseline-v1";
        public const string P01Define = "ASSEMBLY_SHADOW_P01";
        public const string P02Define = "ASSEMBLY_SHADOW_P02";
        public const string P03Define = "ASSEMBLY_SHADOW_P03";
        public const string P04Define = "ASSEMBLY_SHADOW_M07_P04";
        public const string P05Define = "ASSEMBLY_SHADOW_P05";
        public const string P14Define = "ASSEMBLY_SHADOW_M07_P14";
        public const string P15Define = "ASSEMBLY_SHADOW_M07_P15";

        public static readonly string[] Candidates = M02Build.Candidates.ToArray();
        public static readonly string[] ProviderFirstOrder = M03Build.ProviderFirstOrder.ToArray();
        public static readonly string[] BundleNames = {
            "additive-scene.bundle", "business-scene.bundle", "mixed-assets.bundle", "nested-prefab.bundle",
            "scriptable-object.bundle", "serialize-reference.bundle", "versioned-prefab.bundle"
        };

        public static void Configure()
        {
            string previous = AssemblyShadowSettings.Instance.buildId;
            string buildId = AssemblyShadowBuildCommands.Argument("-shadowBaselineId",
                !string.IsNullOrEmpty(previous) && previous.StartsWith("M07-Baseline-", StringComparison.Ordinal) ? previous : DefaultBaselineId);
            Require(buildId.StartsWith("M07-Baseline-", StringComparison.Ordinal) && Path.GetFileName(buildId) == buildId &&
                buildId.IndexOfAny(Path.GetInvalidFileNameChars()) < 0, "M07 requires a safe M07-Baseline-* identity.");
            M02Build.Configure();
            var settings = AssemblyShadowSettings.Instance;
            settings.buildId = buildId;
            settings.playerInputSnapshot = "";
            settings.baselineManifestPath = "";
            settings.resourceBaselinePath = "";
            settings.resourceBuildMapPath = ResourceMapPath;
            AssemblyShadowSettings.Save();
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, EditorUserBuildSettings.activeBuildTarget, settings.architecture);
            EnsureBootstrapScene(buildId, pins.RuntimeAbiHash());
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(BootstrapScene, true) };
            AssemblyShadowSettings.Save();
            AssetDatabase.SaveAssets();
            Debug.Log("[AssemblyShadow M07] Configured " + buildId + " with a business-free bootstrap scene.");
        }

        public static void BuildBaselineResources()
        {
            Configure();
            var settings = AssemblyShadowSettings.Instance;
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            ShadowResourceBuildMap map = M07SourceAssets.Ensure(false);
            Require(MapIdentity(map) == MapIdentity(ReadConfiguredMap()), "Generated M07 baseline resource map differs from ProjectSettings.");
            EnsureBootstrapScene(settings.buildId, ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture).RuntimeAbiHash());
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(BootstrapScene, true) };
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            ShadowAssemblyPolicyValidator.ValidateBeforeCompile(policy, target).ThrowIfInvalid();
            string output = Path.GetFullPath(AssemblyShadowBuildCommands.Argument("-shadowM07ResourceOutput",
                "_temp/AssemblyShadow/M07ResourceBaseline-" + settings.buildId + "-" + Guid.NewGuid().ToString("N")));
            Require(!Directory.Exists(output) && !File.Exists(output), "M07 resource baseline output must be new: " + output);
            string frozen = ShadowResourceBaseline.Build(new ShadowResourceBuildRequest {
                outputDirectory = output, target = target, architecture = settings.architecture,
                sourcePins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture),
                policy = policy, resources = map, extraScriptingDefines = new string[0],
                captureCompilerMode = true, developmentBuild = true,
            });
            VerifiedShadowResourceBaseline verified = ShadowResourceBaseline.ReadAndVerify(frozen, target, settings.architecture);
            Require(verified.Receipt.bundles.Select(item => item.name).SequenceEqual(BundleNames), "M07 baseline must contain exactly the seven canonical bundles.");
            var session = ShadowBuildSession.Load();
            session.resourceBaselinePath = frozen;
            session.Save();
            Debug.Log("[AssemblyShadow M07] Frozen seven-bundle resource baseline: " + frozen);
        }

        public static void ValidateCompilerInputs()
        {
            Configure();
            var settings = AssemblyShadowSettings.Instance;
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
            string snapshot = AssemblySnapshot.CompileWithOptions(Path.GetFullPath("_temp/AssemblyShadow/M07CompilerPreflight-" + Guid.NewGuid().ToString("N")),
                target, settings.architecture, pins, policy, new string[0], true);
            AssemblySnapshotReceipt receipt = AssemblySnapshot.ReadAndVerify(snapshot, false);
            TargetFrameworkReferenceVerifier.Verify(snapshot, receipt);
            using (CompiledAssemblySet set = ShadowFixtureProof.Load(snapshot, receipt, policy))
                ShadowReflectionBindingEvidence.ValidateCompilerSnapshot(set, policy, snapshot, receipt).ThrowIfInvalid();
            Debug.Log("[AssemblyShadow M07] Fresh baseline-domain target compiler snapshot and connected policy graph verified: " + snapshot);
        }

        public static void BuildPlayerBaseline()
        {
            Configure();
            var settings = AssemblyShadowSettings.Instance;
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            ShadowAssemblyPolicyValidator.ValidateBeforeCompile(policy, target).ThrowIfInvalid();
            var session = ShadowBuildSession.Load();
            Require(Directory.Exists(session.resourceBaselinePath), "Run M07Build.BuildBaselineResources before building the Player.");
            VerifiedShadowResourceBaseline resources = ShadowResourceBaseline.ReadAndVerify(session.resourceBaselinePath, target, settings.architecture);
            Require(resources.Receipt.bundles.Select(item => item.name).SequenceEqual(BundleNames), "M07 Player resource baseline bundle inventory differs.");
            string baselineRoot = Path.Combine(settings.baselineOutputRoot, target.ToString(), settings.buildId);
            Require(!Directory.Exists(baselineRoot), "M07 baseline is immutable; choose a new -shadowBaselineId.");
            M02ReflectionBindingValidation.StageConfiguration();
            BaselineBuild.SetNativeFeature(true);
            AssetDatabase.SaveAssets();
            PrebuildCommand.GenerateAll();
            string output = ResolvePlayerOutput("Builds/AssemblyShadow/M07/" + settings.buildId + ".app");
            string snapshot = CapturePlayerInputs(output, true, resources);
            session = ShadowBuildSession.Load();
            session.playerInputSnapshot = snapshot;
            session.resourceBaselinePath = resources.Root;
            session.Save();
            AssemblyShadowBuildCommands.BuildBaselineManifest();
            Debug.Log("[AssemblyShadow M07] Native-ON Player and baseline manifest completed: " + baselineRoot);
        }

        public static void BuildFeatureDisabledPlayer()
        {
            Configure();
            var settings = AssemblyShadowSettings.Instance;
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            var session = ShadowBuildSession.Load();
            Require(Directory.Exists(session.resourceBaselinePath), "M07 native-OFF Player requires the frozen resource baseline.");
            var resources = ShadowResourceBaseline.ReadAndVerify(session.resourceBaselinePath, target, settings.architecture);
            string output = ResolvePlayerOutput("Builds/AssemblyShadow/M07/" + settings.buildId + "-NativeOff.app");
            M02ReflectionBindingValidation.StageConfiguration();
            try
            {
                BaselineBuild.SetNativeFeature(false);
                AssetDatabase.SaveAssets();
                PrebuildCommand.GenerateAll();
                string snapshot = CapturePlayerInputs(output, false, resources);
                Debug.Log("[AssemblyShadow M07] Native-OFF Player receipt: " + Path.Combine(snapshot, "m07-player-build.json"));
            }
            finally
            {
                BaselineBuild.SetNativeFeature(true);
                AssetDatabase.SaveAssets();
            }
        }

        internal static M07Fixture BuildFixture(string root, string patchId, string[] defines, string[] explicitRoots, bool dllOnly,
            BuildTarget target, string architecture, ShadowSourcePins pins, ShadowPolicyConfiguration policy, string baselineManifest)
        {
            string snapshot = AssemblySnapshot.CompileWithOptions(Path.Combine(root, patchId + "-compile"), target, architecture, pins, policy, defines, true);
            return BuildFixtureFromSnapshot(root, patchId, defines, explicitRoots, dllOnly, target, architecture, pins, policy, baselineManifest, snapshot);
        }

        internal static M07Fixture BuildFixtureFromSnapshot(string root, string patchId, string[] defines, string[] explicitRoots, bool dllOnly,
            BuildTarget target, string architecture, ShadowSourcePins pins, ShadowPolicyConfiguration policy, string baselineManifest, string snapshot)
        {
            AssemblySnapshotReceipt snapshotReceipt = AssemblySnapshot.ReadAndVerify(snapshot, false);
            Require(ShadowReflectionBindingEvidence.UserDefines(snapshotReceipt.extraScriptingDefines).SequenceEqual(defines.OrderBy(value => value, StringComparer.Ordinal)),
                "M07 fixture snapshot does not contain its exact declared user defines: " + patchId);
            string output = Path.Combine(root, patchId + "-patch");
            ShadowPatchManifest patch = ShadowPatchManifestBuilder.Build(new ShadowPatchBuildRequest {
                baselineManifestPath = baselineManifest, currentCompileSnapshot = snapshot, outputDirectory = output,
                patchId = patchId, target = target, architecture = architecture, sourcePins = pins, policy = policy,
                explicitChangedRoots = explicitRoots, dllOnly = dllOnly, includePdb = true,
            });
            return new M07Fixture {
                patchId = patchId, defines = defines, changedRoots = patch.changedRoots, compileSnapshot = snapshot,
                compileSnapshotHash = snapshotReceipt.snapshotHash,
                patchDirectory = output, patchManifest = Path.Combine(output, "patch-manifest.json"),
                patchManifestSha256 = ShadowHash.File(Path.Combine(output, "patch-manifest.json")), closureLoadOrder = patch.loadOrder,
                baselineResourceAbiHash = patch.baselineResourceAbiHash, resourceAbiHash = patch.resourceAbiHash,
                resourceChangeLevel = patch.resourceChangeLevel, dllOnly = patch.dllOnly,
                resourceBundlesRequired = patch.resourceBundlesRequired, assemblyIdentities = M04AssemblyIdentityProof.ReadPatch(output, patch),
            };
        }

        internal static M07RejectedFixture BuildRejected(string root, string patchId, string[] defines, string[] roots,
            BuildTarget target, string architecture, ShadowSourcePins pins, ShadowPolicyConfiguration policy, string baselineManifest)
        {
            string snapshot = AssemblySnapshot.CompileWithOptions(Path.Combine(root, patchId + "-compile"), target, architecture, pins, policy, defines, true);
            string output = Path.Combine(root, patchId + "-must-not-exist");
            ShadowBuildException rejection = null;
            try
            {
                ShadowPatchManifestBuilder.Build(new ShadowPatchBuildRequest {
                    baselineManifestPath = baselineManifest, currentCompileSnapshot = snapshot, outputDirectory = output,
                    patchId = patchId, target = target, architecture = architecture, sourcePins = pins, policy = policy,
                    explicitChangedRoots = roots, dllOnly = true, includePdb = true,
                });
            }
            catch (ShadowBuildException error)
            {
                if (error.Code != "ResourceRebuildRequired") throw;
                rejection = error;
            }
            Require(rejection != null && !Directory.Exists(output) && !File.Exists(output), patchId + " was not atomically rejected for DLL-only deployment.");
            return new M07RejectedFixture {
                patchId = patchId, defines = defines, changedRoots = roots, compileSnapshot = snapshot,
                compileSnapshotHash = AssemblySnapshot.ReadAndVerify(snapshot, false).snapshotHash,
                errorCode = rejection.Code, errorMessage = rejection.Message,
            };
        }

        internal static M07FixtureManifest BuildFixtureManifest(string root, M07Fixture structural)
        {
            Configure();
            var settings = AssemblyShadowSettings.Instance;
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            var session = ShadowBuildSession.Load();
            Require(File.Exists(session.baselineManifestPath) && Directory.Exists(session.playerInputSnapshot), "M07 fixtures require the current successful Player baseline.");
            ShadowBaselineManifest baseline = ReadBaseline(session.baselineManifestPath);
            Require(baseline.baselineBuildId == settings.buildId, "M07 fixture baseline identity differs from current settings.");
            Directory.CreateDirectory(root);
            var fixtures = new List<M07Fixture> {
                BuildFixture(root, "P01", new[] { P01Define }, new[] { "AssemblyA.Implementation.Internal" }, true, target, settings.architecture, pins, policy, session.baselineManifestPath),
                BuildFixture(root, "P02", new[] { P02Define }, new[] { "AssemblyA.Implementation.Extensibility" }, true, target, settings.architecture, pins, policy, session.baselineManifestPath),
                BuildFixture(root, "P03", new[] { P01Define, P03Define }, Candidates, true, target, settings.architecture, pins, policy, session.baselineManifestPath),
                BuildFixture(root, "P04", new[] { P01Define, P04Define }, new[] { "AssemblyA.Implementation.Internal" }, true, target, settings.architecture, pins, policy, session.baselineManifestPath),
            };
            Require(structural != null && structural.patchId == "P05" && !structural.dllOnly, "M07 structural P05 fixture is missing.");
            fixtures.Add(structural);
            var rejected = new[] {
                BuildRejected(root, "P05-DllOnly", new[] { P01Define, P05Define }, new[] { "AssemblyA.Implementation.Internal" }, target, settings.architecture, pins, policy, session.baselineManifestPath),
                BuildRejected(root, "P14-ClassRename", new[] { P01Define, P14Define }, new[] { "AssemblyA.Implementation.Internal" }, target, settings.architecture, pins, policy, session.baselineManifestPath),
                BuildRejected(root, "P15-SerializeReferenceRename", new[] { P01Define, P15Define }, new[] { "AssemblyA.Implementation.Internal" }, target, settings.architecture, pins, policy, session.baselineManifestPath),
            };
            var playerSnapshot = AssemblySnapshot.ReadAndVerify(session.playerInputSnapshot, true);
            var stable = M05Build.DeriveStableAotNames(session.playerInputSnapshot, playerSnapshot, policy);
            var manifest = new M07FixtureManifest {
                schemaVersion = 1, milestone = "M07", unityVersion = Application.unityVersion, target = target.ToString(), architecture = settings.architecture,
                baselineBuildId = baseline.baselineBuildId, runtimeAbiHash = baseline.runtimeAbiHash,
                baselineManifestPath = Path.GetFullPath(session.baselineManifestPath), baselineManifestSha256 = ShadowHash.File(session.baselineManifestPath),
                baselineInputSnapshot = Path.GetFullPath(session.playerInputSnapshot), baselineInputSnapshotHash = playerSnapshot.snapshotHash,
                playerBuildReceiptPath = Path.Combine(Path.GetFullPath(session.playerInputSnapshot), "m07-player-build.json"),
                candidateNames = Candidates, bundleNames = BundleNames, stableAotNames = stable.names,
                stableAotProvenance = stable.provenance, stableAotProvenanceHash = stable.provenanceHash,
                fixtures = fixtures.ToArray(), rejectedFixtures = rejected,
            };
            manifest.playerBuildReceiptSha256 = ShadowHash.File(manifest.playerBuildReceiptPath);
            return manifest;
        }

        internal static string WriteFixtureManifest(string root, M07FixtureManifest manifest)
        {
            string path = Path.Combine(root, "m07-fixtures.json");
            M04AssemblyIdentityProof.WriteNewJson(path, manifest);
            return path;
        }

        internal static ShadowBaselineManifest ReadBaseline(string path)
        {
            var baseline = JsonUtility.FromJson<ShadowBaselineManifest>(File.ReadAllText(path));
            Require(baseline != null && baseline.schemaVersion == 1 && baseline.semanticHashSchema == 1, "M07 baseline manifest is malformed.");
            return baseline;
        }

        internal static ShadowResourceBuildMap ReadConfiguredMap()
        {
            return JsonUtility.FromJson<ShadowResourceBuildMap>(File.ReadAllText(ResourceMapPath));
        }

        internal static string MapIdentity(ShadowResourceBuildMap map)
        {
            return string.Join("\n", ShadowResourceBaseline.ValidateMap(map).Select(item => item.assetBundleName + ":" + string.Join("|", item.assetNames)).ToArray());
        }

        private static string CapturePlayerInputs(string output, bool nativeEnabled, VerifiedShadowResourceBaseline resources)
        {
            var settings = AssemblyShadowSettings.Instance;
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
            string nativeArguments = PlayerSettings.GetAdditionalIl2CppArgs();
            Require(nativeArguments == "--compiler-flags=\"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=" + (nativeEnabled ? "1" : "0") + "\"",
                "M07 native compiler feature mode differs from the requested variant.");
            string snapshot = Path.GetFullPath("_temp/AssemblyShadow/M07PlayerInputs-" + Guid.NewGuid().ToString("N"));
            string[] defines = ShadowReflectionBindingEvidence.CompilationDefines(new string[0]);
            var placeholders = M04PlaceholderManifestProof.CaptureBeforeBuild();
            ShadowPlayerInputCapture.Begin(snapshot, settings.buildId, target, settings.architecture, pins, Candidates, defines);
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(output));
                var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                    scenes = new[] { BootstrapScene }, locationPathName = output, target = target, targetGroup = BuildTargetGroup.Standalone,
                    options = BuildOptions.Development | BuildOptions.DetailedBuildReport | BuildOptions.CleanBuildCache,
                    extraScriptingDefines = defines,
                });
                ShadowPlayerInputCapture.CompleteSuccessfulBuild(report);
            }
            finally { ShadowPlayerInputCapture.End(); }
            AssemblySnapshotReceipt captured = AssemblySnapshot.ReadAndVerify(snapshot, true);
            M04AssemblyIdentity[] linked = M04AssemblyIdentityProof.ReadLinked(snapshot, captured);
            var nativeMetadata = M04NativeMetadataProof.ReadPlayer(captured.playerOutput, linked);
            string placeholderPath = Path.Combine(snapshot, "m07-placeholder-AssemblyManifest.cpp");
            Require(ShadowHash.File(placeholders.sourcePath) == placeholders.sha256, "M07 generated placeholder changed during Player build.");
            using (var file = new FileStream(placeholderPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                file.Write(placeholders.bytes, 0, placeholders.bytes.Length);
            string receiptPath = Path.Combine(snapshot, "m07-player-build.json");
            M04AssemblyIdentityProof.WriteNewJson(receiptPath, new M07PlayerBuildReceipt {
                schemaVersion = 1, milestone = "M07", variant = nativeEnabled ? "NativeOn" : "NativeOff",
                baselineBuildId = settings.buildId, runtimeAbiHash = pins.RuntimeAbiHash(), unityVersion = Application.unityVersion,
                target = target.ToString(), architecture = settings.architecture, buildGuid = captured.buildGuid, playerOutput = captured.playerOutput,
                inputSnapshot = snapshot, inputSnapshotHash = captured.snapshotHash, nativeLibraryPath = captured.nativeLibraryPath,
                nativeLibrarySha256 = captured.nativeLibrarySha256, nativeArguments = nativeArguments, assemblyIdentities = linked,
                placeholderManifestPath = placeholderPath, placeholderManifestSha256 = placeholders.sha256, placeholderAssemblyNames = placeholders.names,
                nativeMetadataPath = nativeMetadata.path, nativeMetadataSha256 = nativeMetadata.sha256, nativeMetadataVersion = nativeMetadata.version,
                nativeAssemblyIdentities = nativeMetadata.assemblies, nativeGeneratedAssemblyNames = nativeMetadata.generatedAssemblyNames,
                resourceBaselinePath = resources.Root, resourceBuildReceiptPath = Path.Combine(resources.Root, ShadowResourceBaseline.ReceiptName),
                resourceBuildReceiptSha256 = ShadowHash.File(Path.Combine(resources.Root, ShadowResourceBaseline.ReceiptName)),
                resourceAbiHash = resources.Receipt.resourceAbiHash, bundleNames = resources.Receipt.bundles.Select(item => item.name).ToArray(),
            });
            return snapshot;
        }

        private static string ResolvePlayerOutput(string fallback)
        {
            string output = AssemblyShadowBuildCommands.Argument("-shadowBuildOutput", fallback);
            if (EditorUserBuildSettings.activeBuildTarget == BuildTarget.StandaloneWindows64 && output.EndsWith(".app", StringComparison.Ordinal))
                output = output.Substring(0, output.Length - 4) + ".exe";
            output = Path.GetFullPath(output);
            Require(!Directory.Exists(output) && !File.Exists(output), "M07 Player output already exists: " + output);
            return output;
        }

        private static void EnsureBootstrapScene(string baselineBuildId, string runtimeAbiHash)
        {
            Type runnerType = M01BuildSupport.FindType("AssemblyShadowDemo.Bootstrap", "AssemblyShadowDemo.M07BootstrapRunner");
            Require(runnerType != null && typeof(MonoBehaviour).IsAssignableFrom(runnerType), "Compile M07BootstrapRunner before configuring M07.");
            var scene = File.Exists(BootstrapScene) ? EditorSceneManager.OpenScene(BootstrapScene, OpenSceneMode.Single) :
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Component[] runners = scene.GetRootGameObjects().SelectMany(root => root.GetComponentsInChildren(runnerType, true)).ToArray();
            Require(runners.Length <= 1, "M07 bootstrap scene contains duplicate runners.");
            Component runner = runners.Length == 1 ? runners[0] : new GameObject("AssemblyShadow M07 Bootstrap").AddComponent(runnerType);
            var serialized = new SerializedObject(runner);
            serialized.FindProperty("expectedBaselineBuildId").stringValue = baselineBuildId;
            serialized.FindProperty("expectedRuntimeAbiHash").stringValue = runtimeAbiHash;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            Require(EditorSceneManager.SaveScene(scene, BootstrapScene), "M07 bootstrap scene could not be saved.");
        }

        private static void Require(bool value, string message)
        {
            if (!value) throw new BuildFailedException(message);
        }

        [Serializable]
        public sealed class M07PlayerBuildReceipt
        {
            public int schemaVersion;
            public string milestone, variant, baselineBuildId, runtimeAbiHash, unityVersion, target, architecture, buildGuid, playerOutput;
            public string inputSnapshot, inputSnapshotHash, nativeLibraryPath, nativeLibrarySha256, nativeArguments;
            public M04AssemblyIdentity[] assemblyIdentities;
            public string placeholderManifestPath, placeholderManifestSha256;
            public string[] placeholderAssemblyNames;
            public string nativeMetadataPath, nativeMetadataSha256;
            public int nativeMetadataVersion;
            public M04NativeAssemblyIdentity[] nativeAssemblyIdentities;
            public string[] nativeGeneratedAssemblyNames;
            public string resourceBaselinePath, resourceBuildReceiptPath, resourceBuildReceiptSha256, resourceAbiHash;
            public string[] bundleNames;
        }

        [Serializable]
        public sealed class M07Fixture
        {
            public string patchId;
            public string[] defines, changedRoots;
            public string compileSnapshot, compileSnapshotHash, patchDirectory, patchManifest, patchManifestSha256;
            public string[] closureLoadOrder;
            public string baselineResourceAbiHash, resourceAbiHash, resourceChangeLevel;
            public bool dllOnly;
            public string[] resourceBundlesRequired;
            public M04AssemblyIdentity[] assemblyIdentities;
            public string replacementResourcePath, replacementResourceReceiptPath, replacementResourceReceiptSha256;
            public string[] replacementBundleNames;
        }

        [Serializable]
        public sealed class M07RejectedFixture
        {
            public string patchId;
            public string[] defines, changedRoots;
            public string compileSnapshot, compileSnapshotHash, errorCode, errorMessage;
        }

        [Serializable]
        public sealed class M07FixtureManifest
        {
            public int schemaVersion;
            public string milestone, unityVersion, target, architecture, baselineBuildId, runtimeAbiHash;
            public string baselineManifestPath, baselineManifestSha256, baselineInputSnapshot, baselineInputSnapshotHash;
            public string playerBuildReceiptPath, playerBuildReceiptSha256;
            public string[] candidateNames, bundleNames, stableAotNames;
            public string stableAotProvenance, stableAotProvenanceHash;
            public M07Fixture[] fixtures;
            public M07RejectedFixture[] rejectedFixtures;
        }
    }
}
