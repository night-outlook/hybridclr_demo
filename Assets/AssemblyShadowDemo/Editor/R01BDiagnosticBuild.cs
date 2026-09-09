using System;
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
    /// <summary>Builds an explicitly diagnostic-only R01B Player artifact.</summary>
    public static class R01BDiagnosticBuild
    {
        public const string DiagnosticScene = "Assets/AssemblyShadowR01BDiagnostics/Scenes/R01BDiagnostic.unity";
        public const string DiagnosticDefine = "ASSEMBLY_SHADOW_R01B_DIAGNOSTICS";
        private const string ReceiptDefault = "_temp/AssemblyShadow/R01B/r01b-diagnostic-player-build.json";

        public static void AuthorScene() { AuthorDiagnosticScene(); }

        public static void AuthorDiagnosticScene()
        {
            var settings = AssemblyShadowSettings.Instance;
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            ShadowSourcePins pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
            EnsureScene(settings.buildId, pins.RuntimeAbiHash());
            Debug.Log("[AssemblyShadow R01B] Authored diagnostic scene for " + settings.buildId + ".");
        }

        public static void BuildDiagnosticPlayer()
        {
            var settings = AssemblyShadowSettings.Instance;
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            string architecture = settings.architecture;
            ShadowSourcePins pins = ShadowSourcePins.Read(settings.sourcePinFile, target, architecture);
            string baselineId = settings.buildId;
            string runtimeAbiHash = pins.RuntimeAbiHash();
            Require(target == BuildTarget.StandaloneOSX && architecture == "arm64", "R01B diagnostic Player is pinned to StandaloneOSX arm64.");
            string sourcePinsPath = Path.GetFullPath(settings.sourcePinFile);
            string sourcePinsHash = ShadowHash.File(sourcePinsPath);
            string sourcePinsJson = File.ReadAllText(sourcePinsPath);
            string fixtures = Path.GetFullPath(Argument("-shadowM07Fixtures", ""));
            string playerReceipt = Path.GetFullPath(Argument("-shadowM07PlayerReceipt", ""));
            Require(File.Exists(fixtures) && File.Exists(playerReceipt), "Diagnostic build requires the regular M07 fixture and ON Player receipt arguments.");
            string fixtureHash = ShadowHash.File(fixtures);
            string playerReceiptHash = ShadowHash.File(playerReceipt);
            EnsureScene(baselineId, runtimeAbiHash);

            string output = Path.GetFullPath(Argument("-shadowR01BDiagnosticOutput",
                "Builds/AssemblyShadow/R01B/r01b-diagnostic-" + baselineId + ".app"));
            string receiptPath = Path.GetFullPath(Argument("-shadowR01BDiagnosticBuildReceipt", ReceiptDefault));
            Require(!File.Exists(output) && !Directory.Exists(output), "Diagnostic Player output must be new: " + output);
            Require(!File.Exists(receiptPath) && !Directory.Exists(receiptPath), "Diagnostic build receipt must be new: " + receiptPath);

            string nativeArgumentsBefore = PlayerSettings.GetAdditionalIl2CppArgs();
            string nativeArgumentsUsed = "";
            string snapshot = Path.GetFullPath("_temp/AssemblyShadow/R01B/R01BDiagnosticPlayerInputs-" + Guid.NewGuid().ToString("N"));
            string[] defines = ShadowReflectionBindingEvidence.CompilationDefines(new[] { DiagnosticDefine });
            bool captureStarted = false;
            try
            {
                BaselineBuild.SetNativeFeature(true);
                nativeArgumentsUsed = PlayerSettings.GetAdditionalIl2CppArgs();
                AssetDatabase.SaveAssets();
                PrebuildCommand.GenerateAll();
                ShadowPlayerInputCapture.Begin(snapshot, baselineId, target, architecture, pins, M02Build.Candidates, defines);
                captureStarted = true;
                M07Build.WithPlayerBuildSettings(target, () => {
                    var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                        scenes = new[] { DiagnosticScene, M07Build.BootstrapScene },
                        locationPathName = output,
                        target = target,
                        targetGroup = BuildTargetGroup.Standalone,
                        options = BuildOptions.Development | BuildOptions.DetailedBuildReport | BuildOptions.CleanBuildCache,
                        extraScriptingDefines = defines,
                    });
                    ShadowPlayerInputCapture.CompleteSuccessfulBuild(report);
                });
            }
            finally
            {
                if (captureStarted) ShadowPlayerInputCapture.End();
                PlayerSettings.SetAdditionalIl2CppArgs(nativeArgumentsBefore);
                AssetDatabase.SaveAssets();
            }

            AssemblySnapshotReceipt captured = AssemblySnapshot.ReadAndVerify(snapshot, true);
            M04AssemblyIdentity[] linked = M04AssemblyIdentityProof.ReadLinked(snapshot, captured);
            M04NativeMetadataProof.Capture nativeMetadata = M04NativeMetadataProof.ReadPlayer(output, linked);
            string executable = PlayerExecutable(output, target);
            Require(ShadowHash.File(sourcePinsPath) == sourcePinsHash && File.ReadAllText(sourcePinsPath) == sourcePinsJson,
                "Source pins changed during diagnostic Player build.");
            Require(ShadowHash.File(fixtures) == fixtureHash && ShadowHash.File(playerReceipt) == playerReceiptHash,
                "Regular M07 fixture or ON Player receipt changed during diagnostic Player build.");
            string[] linkedNames = linked.Select(item => item.name).OrderBy(item => item, StringComparer.Ordinal).ToArray();
            string[] linkedHashes = linked.OrderBy(item => item.name, StringComparer.Ordinal).Select(item => item.sha256).ToArray();
            string path = Path.GetFullPath(receiptPath);
            M04AssemblyIdentityProof.WriteNewJson(path, new DiagnosticBuildReceipt {
                schemaVersion = 1,
                kind = "R01BDiagnosticPlayerBuild",
                milestone = "R01B",
                diagnosticOnly = true,
                productionPolicyAdmission = false,
                uniqueGuid = Guid.NewGuid().ToString("N"),
                baselineBuildId = baselineId,
                runtimeAbiHash = runtimeAbiHash,
                unityVersion = Application.unityVersion,
                target = target.ToString(),
                architecture = architecture,
                buildGuid = captured.buildGuid,
                playerOutput = captured.playerOutput,
                playerExecutable = executable,
                playerExecutableSha256 = ShadowHash.File(executable),
                inputSnapshot = snapshot,
                inputSnapshotHash = captured.snapshotHash,
                sourcePinFile = sourcePinsPath,
                sourcePinSha256 = sourcePinsHash,
                sourcePinsJson = sourcePinsJson,
                nativeLibraryPath = captured.nativeLibraryPath,
                nativeLibrarySha256 = captured.nativeLibrarySha256,
                nativeArguments = nativeArgumentsUsed,
                extraScriptingDefines = defines,
                linkedInputNames = linkedNames,
                linkedInputSha256 = linkedHashes,
                assemblyIdentities = linked,
                nativeMetadataPath = nativeMetadata.path,
                nativeMetadataSha256 = nativeMetadata.sha256,
                nativeMetadataVersion = nativeMetadata.version,
                nativeAssemblyIdentities = nativeMetadata.assemblies,
                nativeGeneratedAssemblyNames = nativeMetadata.generatedAssemblyNames,
                diagnosticAssemblyName = "AssemblyShadow.R01BDiagnostics",
                regularFixtureManifestPath = Path.GetFullPath(fixtures),
                regularFixtureManifestSha256 = fixtureHash,
                regularPlayerReceiptPath = Path.GetFullPath(playerReceipt),
                regularPlayerReceiptSha256 = playerReceiptHash,
                scenes = new[] { DiagnosticScene, M07Build.BootstrapScene },
                note = "Diagnostic-only artifact; it does not publish a production Shadow baseline manifest or claim production policy admission.",
            });
            Debug.Log("[AssemblyShadow R01B] Diagnostic Player captured: " + path);
        }

        private static void EnsureScene(string baselineId, string runtimeAbiHash)
        {
            Require(!string.IsNullOrWhiteSpace(baselineId) && !string.IsNullOrWhiteSpace(runtimeAbiHash), "Diagnostic scene requires baseline identity and runtime ABI hash.");
            string directory = Path.GetDirectoryName(DiagnosticScene);
            if (!Directory.Exists(directory)) Directory.CreateDirectory(directory);
            SceneAsset existing = AssetDatabase.LoadAssetAtPath<SceneAsset>(DiagnosticScene);
            var scene = existing != null ? EditorSceneManager.OpenScene(DiagnosticScene, OpenSceneMode.Single) :
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var runners = scene.GetRootGameObjects().SelectMany(root => root.GetComponentsInChildren<AssemblyShadowDemo.R01BDiagnosticRunner>(true)).ToArray();
            Require(runners.Length <= 1, "Diagnostic scene contains duplicate runners.");
            var runner = runners.Length == 1 ? runners[0] : new GameObject("AssemblyShadow R01B Diagnostic Runner").AddComponent<AssemblyShadowDemo.R01BDiagnosticRunner>();
            var serialized = new SerializedObject(runner);
            serialized.FindProperty("expectedBaselineBuildId").stringValue = baselineId;
            serialized.FindProperty("expectedRuntimeAbiHash").stringValue = runtimeAbiHash;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            Require(EditorSceneManager.SaveScene(scene, DiagnosticScene), "Could not save diagnostic scene.");
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        }

        private static string Argument(string name, string fallback)
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int index = 0; index + 1 < args.Length; ++index)
                if (args[index] == name) return args[index + 1];
            return fallback;
        }

        private static string PlayerExecutable(string output, BuildTarget target)
        {
            if (target == BuildTarget.StandaloneOSX)
            {
                string macos = Path.Combine(output, "Contents/MacOS");
                string[] files = Directory.GetFiles(macos, "*", SearchOption.TopDirectoryOnly)
                    .Where(path => !path.EndsWith(".dSYM", StringComparison.OrdinalIgnoreCase)).ToArray();
                Require(files.Length == 1, "Diagnostic OSX Player must contain exactly one executable.");
                return Path.GetFullPath(files[0]);
            }
            Require(File.Exists(output), "Diagnostic Player executable is missing: " + output);
            return Path.GetFullPath(output);
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new BuildFailedException(message);
        }

        [Serializable]
        public sealed class DiagnosticBuildReceipt
        {
            public int schemaVersion, nativeMetadataVersion;
            public bool diagnosticOnly, productionPolicyAdmission;
            public string kind, milestone, uniqueGuid, baselineBuildId, runtimeAbiHash, unityVersion, target, architecture, buildGuid;
            public string playerOutput, playerExecutable, playerExecutableSha256, inputSnapshot, inputSnapshotHash;
            public string sourcePinFile, sourcePinSha256, sourcePinsJson, nativeLibraryPath, nativeLibrarySha256, nativeArguments;
            public string[] extraScriptingDefines, linkedInputNames, linkedInputSha256;
            public M04AssemblyIdentity[] assemblyIdentities;
            public string nativeMetadataPath, nativeMetadataSha256, diagnosticAssemblyName;
            public M04NativeAssemblyIdentity[] nativeAssemblyIdentities;
            public string[] nativeGeneratedAssemblyNames, scenes;
            public string regularFixtureManifestPath, regularFixtureManifestSha256, regularPlayerReceiptPath, regularPlayerReceiptSha256, note;
        }
    }
}
