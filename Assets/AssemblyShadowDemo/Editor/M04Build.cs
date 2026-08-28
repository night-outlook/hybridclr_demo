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
using StableAotProvenance = AssemblyShadowDemo.Editor.M03Build.StableAotProvenance;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>
    /// Produces immutable, target-compiler M04 fixtures. All outputs are placed
    /// below one fresh _temp directory; no fixture is silently staged into a
    /// Player or into the frozen M01 resources.
    /// </summary>
    public static class M04Build
    {
        public const string InitializerDefine = M03Build.InitializerDefine;
        public const string P03InitializerDefine = M03Build.P03InitializerDefine;
        public const string MilestoneDefine = "ASSEMBLY_SHADOW_M04";
        public const string MilestoneP03Define = "ASSEMBLY_SHADOW_M04_P03";
        public const string StableAotHashDomain = "m04-stable-aot:1\n";
        public const string P03Define = "ASSEMBLY_SHADOW_P03";
        public const string P01Define = "ASSEMBLY_SHADOW_P01";
        public const string BootstrapScene = "Assets/AssemblyShadowDemo/Scenes/M04Bootstrap.unity";
        public const string DefaultBaselineId = "M04-Baseline-v1";

        public static readonly string[] ProviderFirstOrder = M03Build.ProviderFirstOrder.ToArray();

        public static void Configure()
        {
            string previousId = AssemblyShadowSettings.Instance.buildId;
            string baselineId = AssemblyShadowBuildCommands.Argument("-shadowBaselineId",
                !string.IsNullOrEmpty(previousId) && previousId.StartsWith("M04-Baseline-", StringComparison.Ordinal) ? previousId : DefaultBaselineId);
            Require(baselineId.StartsWith("M04-Baseline-", StringComparison.Ordinal) && Path.GetFileName(baselineId) == baselineId &&
                baselineId.IndexOfAny(Path.GetInvalidFileNameChars()) < 0, "M04 needs an explicit, safe M04-Baseline-* identity.");
            // Reuse accepted candidate/filter policy, but build a distinct M04
            // bootstrap. M01 bundles and their immutable baseline are untouched.
            M02Build.Configure();
            var settings = AssemblyShadowSettings.Instance;
            settings.buildId = baselineId;
            settings.playerInputSnapshot = "";
            settings.baselineManifestPath = "";
            settings.resourceBaselinePath = "";
            // Scene/asset callbacks can reload the settings singleton. Persist
            // this identity before those callbacks can replace the local object.
            AssemblyShadowSettings.Save();
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, EditorUserBuildSettings.activeBuildTarget, settings.architecture);
            EnsureBootstrapScene(baselineId, pins.RuntimeAbiHash());
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(BootstrapScene, true) };
            AssemblyShadowSettings.Save();
            AssetDatabase.SaveAssets();
            Debug.Log("[AssemblyShadow M04] Configured " + baselineId + " with Player-embedded baseline/ABI identity.");
        }

        public static void ValidateCompilerInputs()
        {
            Configure();
            var settings = AssemblyShadowSettings.Instance;
            var target = EditorUserBuildSettings.activeBuildTarget;
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
            string snapshot = AssemblySnapshot.Compile(Path.GetFullPath("_temp/AssemblyShadow/M04CompilerPreflight-" + Guid.NewGuid().ToString("N")),
                target, settings.architecture, pins, policy, new string[0]);
            var receipt = AssemblySnapshot.ReadAndVerify(snapshot, false);
            TargetFrameworkReferenceVerifier.Verify(snapshot, receipt);
            // The compiler output includes NUnit/facade inputs that the actual
            // Player filter/linker may remove. Only that later captured evidence
            // can classify runtime membership; do not waive unresolved types or
            // substitute historical exclusions to turn preflight into acceptance.
            Debug.Log("[AssemblyShadow M04] Fresh target compiler snapshot verified (not runtime policy acceptance): " + snapshot);
        }

        public static void BuildPlayerBaseline()
        {
            Configure();
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            var settings = AssemblyShadowSettings.Instance;
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            ShadowAssemblyPolicyValidator.ValidateBeforeCompile(policy, target).ThrowIfInvalid();
            string buildId = settings.buildId;
            Require(!Directory.Exists(Path.Combine(settings.baselineOutputRoot, target.ToString(), buildId)),
                "This M04 baseline is immutable; select a new -shadowBaselineId for a new build.");
            string output = ResolvePlayerOutput("Builds/AssemblyShadow/M04/" + buildId + ".app");
            string frozen = M01Paths.BaselineRoot(target);
            BuildBaselineBundles.VerifyExisting(frozen);
            M01BuildSupport.StageBaselineArtifacts(frozen, Path.Combine(Application.streamingAssetsPath, "AssemblyShadow/M01"));
            M02ReflectionBindingValidation.StageConfiguration();
            PrebuildCommand.GenerateAll();
            string snapshot = CapturePlayerInputs(output, true);
            var captured = AssemblySnapshot.ReadAndVerify(snapshot, true);
            foreach (string name in new[] { "AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility", "AssemblyA.Implementation.Internal" })
            {
                var input = captured.assemblies.Single(item => item.name == name);
                CompilePatchDlls.VerifySemanticEquivalence(Path.Combine(frozen, "AssemblySnapshot/" + name + ".dll"), Path.Combine(snapshot, input.path));
            }
            var session = ShadowBuildSession.Load();
            session.playerInputSnapshot = snapshot;
            session.resourceBaselinePath = M02FrozenResources.Import(frozen, snapshot,
                Path.Combine("HybridCLRData/AssemblyShadow/ResourceBaselines", target.ToString(), buildId), target, settings.architecture, policy);
            session.Save();
            AssemblyShadowBuildCommands.BuildBaselineManifest();
            Debug.Log("[AssemblyShadow M04] New M04 Player baseline captured; frozen M01 DLL semantics and bundles verified unchanged.");
        }

        public static void BuildFeatureDisabledPlayer()
        {
            Configure();
            var target = EditorUserBuildSettings.activeBuildTarget;
            ShadowAssemblyPolicyValidator.ValidateBeforeCompile(AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target), target).ThrowIfInvalid();
            string output = ResolvePlayerOutput("Builds/AssemblyShadow/M04/" + AssemblyShadowSettings.Instance.buildId + "-NativeOff.app");
            M02ReflectionBindingValidation.StageConfiguration();
            try
            {
                BaselineBuild.SetNativeFeature(false);
                AssetDatabase.SaveAssets();
                PrebuildCommand.GenerateAll();
                string snapshot = CapturePlayerInputs(output, false);
                Debug.Log("[AssemblyShadow M04] Native-OFF Player receipt: " + Path.Combine(snapshot, "m04-player-build.json"));
            }
            finally
            {
                BaselineBuild.SetNativeFeature(true);
                AssetDatabase.SaveAssets();
            }
        }

        public static void BuildFixtures()
        {
            Configure();
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            var settings = AssemblyShadowSettings.Instance;
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            var session = ShadowBuildSession.Load();
            Require(File.Exists(session.baselineManifestPath), "M04 requires its verified Player baseline manifest.");
            Require(Directory.Exists(session.playerInputSnapshot), "M04 requires its verified Player input snapshot directory.");
            var baselineReceipt = AssemblySnapshot.ReadAndVerify(session.playerInputSnapshot, true);
            ShadowSourcePins.RequireCompatible(baselineReceipt.sourcePins, pins);
            var baseline = JsonUtility.FromJson<ShadowBaselineManifest>(File.ReadAllText(session.baselineManifestPath));
            Require(baseline != null && baseline.baselineBuildId == settings.buildId && baselineReceipt.buildId == settings.buildId,
                "M04 fixtures must match this Player's embedded baseline identity, not an older milestone.");
            StableAotProvenance stable = DeriveStableAotNames(session.playerInputSnapshot, baselineReceipt, policy);

            string root = Path.GetFullPath("_temp/AssemblyShadow/M04Fixtures-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(root);
            var fixtures = new List<M04Fixture>();
            fixtures.Add(BuildFixture(root, "P01", ExpectedDefines("P01"), ExpectedChangedRoots("P01"), target, settings.architecture, pins, policy, session.baselineManifestPath, stable));
            // Initializer observations deliberately change every member's IL.
            // Declare those changes truthfully; the M02 Contracts-only case
            // separately proves reverse closure from a single changed provider.
            fixtures.Add(BuildFixture(root, "P03", ExpectedDefines("P03"), ExpectedChangedRoots("P03"), target, settings.architecture, pins, policy, session.baselineManifestPath, stable));

            var manifest = new M04FixtureManifest {
                schemaVersion = 1,
                milestone = "M04",
                unityVersion = Application.unityVersion,
                target = target.ToString(),
                architecture = settings.architecture,
                baselineManifestPath = Path.GetFullPath(session.baselineManifestPath),
                baselineManifestSha256 = ShadowHash.File(session.baselineManifestPath),
                baselineInputSnapshot = Path.GetFullPath(session.playerInputSnapshot),
                baselineInputSnapshotHash = baselineReceipt.snapshotHash,
                baselineBuildId = baseline.baselineBuildId,
                runtimeAbiHash = pins.RuntimeAbiHash(),
                candidateNames = M02Build.Candidates.ToArray(),
                closureLoadOrder = ProviderFirstOrder.ToArray(),
                stableAotNames = stable.names,
                stableAotProvenanceHash = stable.provenanceHash,
                stableAotProvenance = stable.provenance,
                fixtures = fixtures.ToArray(),
            };
            string path = Path.Combine(root, "m04-fixtures.json");
            M04AssemblyIdentityProof.WriteNewJson(path, manifest);
            string replay = M04EditorValidation.ValidateAndWriteReceipt(path);
            Debug.Log("[AssemblyShadow M04] Fixtures: " + path + "; independent Editor replay: " + replay);
        }

        internal static StableAotProvenance DeriveStableAotNames(string snapshotRoot, AssemblySnapshotReceipt receipt, ShadowPolicyConfiguration policy)
        {
            return ShadowFixtureProof.DeriveStableAotNames(snapshotRoot, receipt, policy, StableAotHashDomain);
        }

        private static M04Fixture BuildFixture(string root, string patchId, string[] defines, string[] changedRoots, BuildTarget target,
            string architecture, ShadowSourcePins pins, ShadowPolicyConfiguration policy, string baselineManifest, StableAotProvenance stable)
        {
            string snapshotRoot = Path.Combine(root, patchId + "-compile");
            string snapshot = AssemblySnapshot.Compile(snapshotRoot, target, architecture, pins, policy, defines);
            string artifact = Path.Combine(root, patchId);
            var patch = ShadowPatchManifestBuilder.Build(new ShadowPatchBuildRequest {
                baselineManifestPath = baselineManifest,
                currentCompileSnapshot = snapshot,
                outputDirectory = artifact,
                patchId = patchId,
                target = target,
                architecture = architecture,
                sourcePins = pins,
                policy = policy,
                explicitChangedRoots = changedRoots,
                dllOnly = true,
                includePdb = true,
            });
            return new M04Fixture {
                patchId = patchId,
                defines = defines.ToArray(),
                changedRoots = changedRoots.ToArray(),
                compileSnapshot = snapshot,
                compileSnapshotHash = AssemblySnapshot.ReadAndVerify(snapshot, false).snapshotHash,
                patchDirectory = artifact,
                patchManifest = Path.Combine(artifact, "patch-manifest.json"),
                patchManifestSha256 = ShadowHash.File(Path.Combine(artifact, "patch-manifest.json")),
                closureLoadOrder = patch.loadOrder,
                stableAotNames = stable.names,
                assemblyIdentities = M04AssemblyIdentityProof.ReadPatch(artifact, patch),
            };
        }

        internal static string[] ExpectedDefines(string patchId)
        {
            Require(patchId == "P01" || patchId == "P03", "Unsupported M04 fixture identity.");
            return patchId == "P01"
                ? new[] { InitializerDefine, P01Define, MilestoneDefine }
                : new[] { InitializerDefine, P01Define, MilestoneDefine, P03InitializerDefine, P03Define, MilestoneP03Define };
        }

        internal static string[] ExpectedChangedRoots(string patchId)
        {
            Require(patchId == "P01" || patchId == "P03", "Unsupported M04 fixture identity.");
            return patchId == "P01" ? new[] { "AssemblyA.Implementation.Internal" } : ProviderFirstOrder.ToArray();
        }

        private static string ResolvePlayerOutput(string defaultOutput)
        {
            string output = AssemblyShadowBuildCommands.Argument("-shadowBuildOutput", defaultOutput);
            if (EditorUserBuildSettings.activeBuildTarget == BuildTarget.StandaloneWindows64 && output.EndsWith(".app", StringComparison.Ordinal))
                output = output.Substring(0, output.Length - 4) + ".exe";
            Require(!Directory.Exists(output) && !File.Exists(output), "M04 Player output already exists: " + output);
            return Path.GetFullPath(output);
        }

        private static string CapturePlayerInputs(string output, bool nativeEnabled)
        {
            var settings = AssemblyShadowSettings.Instance;
            var target = EditorUserBuildSettings.activeBuildTarget;
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
            string nativeArguments = PlayerSettings.GetAdditionalIl2CppArgs();
            Require(nativeArguments == "--compiler-flags=\"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=" + (nativeEnabled ? "1" : "0") + "\"",
                "Native compiler feature mode does not match the requested evidence variant.");
            string snapshot = Path.GetFullPath("_temp/AssemblyShadow/M04PlayerInputs-" + Guid.NewGuid().ToString("N"));
            string[] defines = ShadowReflectionBindingEvidence.CompilationDefines(new string[0]);
            var placeholders = M04PlaceholderManifestProof.CaptureBeforeBuild();
            ShadowPlayerInputCapture.Begin(snapshot, settings.buildId, target, settings.architecture, pins, M02Build.Candidates, defines);
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(output));
                var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                    scenes = new[] { BootstrapScene }, locationPathName = output,
                    target = target, targetGroup = BuildTargetGroup.Standalone,
                    options = BuildOptions.Development | BuildOptions.DetailedBuildReport, extraScriptingDefines = defines,
                });
                ShadowPlayerInputCapture.CompleteSuccessfulBuild(report);
            }
            finally { ShadowPlayerInputCapture.End(); }
            var captured = AssemblySnapshot.ReadAndVerify(snapshot, true);
            M04DiagnosticSchemaVerifier.Verify(snapshot, captured);
            string placeholderPath = M04PlaceholderManifestProof.WriteSnapshot(snapshot, placeholders);
            M04AssemblyIdentityProof.WriteNewJson(Path.Combine(snapshot, "m04-player-build.json"), new M04PlayerBuildReceipt {
                schemaVersion = 1, milestone = "M04", variant = nativeEnabled ? "NativeOn" : "NativeOff",
                baselineBuildId = settings.buildId, runtimeAbiHash = pins.RuntimeAbiHash(),
                unityVersion = Application.unityVersion, target = target.ToString(), architecture = settings.architecture,
                buildGuid = captured.buildGuid, playerOutput = captured.playerOutput,
                inputSnapshot = snapshot, inputSnapshotHash = captured.snapshotHash,
                nativeLibraryPath = captured.nativeLibraryPath, nativeLibrarySha256 = captured.nativeLibrarySha256,
                nativeArguments = nativeArguments,
                assemblyIdentities = M04AssemblyIdentityProof.ReadLinked(snapshot, captured),
                placeholderManifestPath = placeholderPath, placeholderManifestSha256 = placeholders.sha256,
                placeholderAssemblyNames = placeholders.names,
            });
            return snapshot;
        }

        private static void EnsureBootstrapScene(string baselineId, string runtimeAbiHash)
        {
            Type runnerType = M01BuildSupport.FindType("AssemblyShadowDemo.Bootstrap", "AssemblyShadowDemo.M04BootstrapRunner");
            Require(runnerType != null && typeof(MonoBehaviour).IsAssignableFrom(runnerType), "Compile M04BootstrapRunner before configuring the Player.");
            var scene = File.Exists(BootstrapScene) ? EditorSceneManager.OpenScene(BootstrapScene, OpenSceneMode.Single) :
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var runners = scene.GetRootGameObjects().SelectMany(root => root.GetComponentsInChildren(runnerType, true)).ToArray();
            Require(runners.Length <= 1, "M04 bootstrap scene contains duplicate runners.");
            Component runner = runners.Length == 1 ? runners[0] : new GameObject("AssemblyShadow M04 Bootstrap").AddComponent(runnerType);
            var serialized = new SerializedObject(runner);
            serialized.FindProperty("expectedBaselineBuildId").stringValue = baselineId;
            serialized.FindProperty("expectedRuntimeAbiHash").stringValue = runtimeAbiHash;
            bool changed = serialized.ApplyModifiedPropertiesWithoutUndo();
            if (changed || !File.Exists(BootstrapScene))
                Require(EditorSceneManager.SaveScene(scene, BootstrapScene), "M04 bootstrap scene could not be saved.");
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new BuildFailedException(message);
        }

        [Serializable] public sealed class M04PlayerBuildReceipt
        {
            public int schemaVersion;
            public string milestone, variant, baselineBuildId, runtimeAbiHash;
            public string unityVersion, target, architecture, buildGuid, playerOutput;
            public string inputSnapshot, inputSnapshotHash, nativeLibraryPath, nativeLibrarySha256, nativeArguments;
            public M04AssemblyIdentity[] assemblyIdentities;
            public string placeholderManifestPath, placeholderManifestSha256;
            public string[] placeholderAssemblyNames;
        }

        [Serializable] public sealed class M04Fixture
        {
            public string patchId;
            public string[] defines;
            public string[] changedRoots;
            public string compileSnapshot;
            public string compileSnapshotHash;
            public string patchDirectory;
            public string patchManifest;
            public string patchManifestSha256;
            public string[] closureLoadOrder;
            public string[] stableAotNames;
            public M04AssemblyIdentity[] assemblyIdentities;
        }

        [Serializable] public sealed class M04FixtureManifest
        {
            public int schemaVersion;
            public string milestone;
            public string unityVersion;
            public string target;
            public string architecture;
            public string baselineManifestPath;
            public string baselineManifestSha256;
            public string baselineBuildId;
            public string runtimeAbiHash;
            public string baselineInputSnapshot;
            public string baselineInputSnapshotHash;
            public string[] candidateNames;
            public string[] closureLoadOrder;
            public string[] stableAotNames;
            public string stableAotProvenanceHash;
            public string stableAotProvenance;
            public M04Fixture[] fixtures;
        }
    }
}
