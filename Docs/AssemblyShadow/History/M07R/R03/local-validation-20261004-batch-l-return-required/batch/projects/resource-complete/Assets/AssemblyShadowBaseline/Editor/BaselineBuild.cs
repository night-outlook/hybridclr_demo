using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using HybridCLR.Editor;
using HybridCLR.Editor.Commands;
using HybridCLR.Editor.Installer;
using HybridCLR.Editor.Settings;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace AssemblyShadowBaseline.Editor
{
    public static class BaselineBuild
    {
        public const string ScenePath = "Assets/AssemblyShadowBaseline/Scenes/Baseline.unity";
        private const string ResourceRoot = "Assets/AssemblyShadowBaseline/Resources/AssemblyShadowBaseline";
        private const string HotAssembly = "AssemblyShadowBaseline.HotUpdate";

        public static void Configure()
        {
            if (Application.unityVersion != "2022.3.62f2")
                throw new BuildFailedException("Assembly Shadow M00 pins Unity 2022.3.62f2.");
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            if (target != BuildTarget.StandaloneOSX && target != BuildTarget.StandaloneWindows64)
                throw new BuildFailedException("M00 currently supports macOS ARM64 or Windows x64.");
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Standalone, ScriptingImplementation.IL2CPP);
            if (target == BuildTarget.StandaloneOSX)
            {
                PlayerSettings.SetArchitecture(NamedBuildTarget.Standalone, 1);
#if UNITY_EDITOR_OSX
                UnityEditor.OSXStandalone.UserBuildSettings.architecture = OSArchitecture.ARM64;
#endif
            }
            PlayerSettings.SetIl2CppCompilerConfiguration(NamedBuildTarget.Standalone, Il2CppCompilerConfiguration.Debug);
            PlayerSettings.SetManagedStrippingLevel(NamedBuildTarget.Standalone, ManagedStrippingLevel.Low);
            PlayerSettings.SetApiCompatibilityLevel(NamedBuildTarget.Standalone, ApiCompatibilityLevel.NET_Standard);
            SetNativeFeature(false);
            PlayerSettings.companyName = "AssemblyShadowLab";
            PlayerSettings.productName = "AssemblyShadowBaseline";
            PlayerSettings.runInBackground = true;
            EditorUserBuildSettings.development = true;
            EditorUserBuildSettings.allowDebugging = false;
            EditorUserBuildSettings.connectProfiler = false;

            var settings = HybridCLRSettings.Instance;
            settings.enable = true;
            settings.useGlobalIl2cpp = false;
            settings.hotUpdateAssemblyDefinitions = Array.Empty<UnityEditorInternal.AssemblyDefinitionAsset>();
            settings.hotUpdateAssemblies = new[] { HotAssembly };
            settings.preserveHotUpdateAssemblies = Array.Empty<string>();
            settings.patchAOTAssemblies = Array.Empty<string>();
            HybridCLRSettings.Save();
            EnsureAssets();
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            AssetDatabase.SaveAssets();
            Debug.Log("[AssemblyShadow M00] Configured ordinary HybridCLR baseline, Shadow OFF.");
        }

        public static void Install()
        {
            PinnedSourceInstaller.Install();
        }

        public static void InstallRepeatability()
        {
            string root = Path.Combine(SettingsUtil.LocalIl2CppDir, "libil2cpp");
            string receipt = Path.Combine(root, "assembly-shadow-install.json");
            Install();
            byte[] first = File.ReadAllBytes(receipt);
            Install();
            byte[] second = File.ReadAllBytes(receipt);
            if (!first.SequenceEqual(second))
                throw new BuildFailedException("Repeated pinned installation produced different receipts.");
            string hash;
            using (var sha = SHA256.Create())
                hash = BitConverter.ToString(sha.ComputeHash(first)).Replace("-", "").ToLowerInvariant();
            Directory.CreateDirectory("_temp/AssemblyShadow");
            File.WriteAllBytes("_temp/AssemblyShadow/m00-install-receipt.json", second);
            File.WriteAllText("_temp/AssemblyShadow/m00-install-repeatability.json", JsonUtility.ToJson(
                new InstallEvidence { identical = true, receiptSha256 = hash,
                    installedFiles = Directory.GetFiles(root, "*", SearchOption.AllDirectories).Length }, true));
            Debug.Log("[AssemblyShadow M00] Repeated install receipts identical: " + hash);
        }

        public static void Build()
        {
            Configure();
            PrebuildCommand.GenerateAll();
            string dllSource = Path.Combine(SettingsUtil.GetHotUpdateDllsOutputDirByTarget(
                EditorUserBuildSettings.activeBuildTarget), HotAssembly + ".dll");
            string streamRoot = Path.Combine(Application.streamingAssetsPath, "AssemblyShadow/M00");
            Directory.CreateDirectory(streamRoot);
            File.Copy(dllSource, Path.Combine(streamRoot, HotAssembly + ".dll.bytes"), true);
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            BuildPlayer("M00", ScenePath, "Builds/AssemblyShadow/M00/Baseline.app");
        }

        public static void BuildPlayer(string milestone, string scenePath, string defaultOutput)
        {
            var target = EditorUserBuildSettings.activeBuildTarget;
            string output = Argument("-shadowBuildOutput", defaultOutput);
            if (target == BuildTarget.StandaloneWindows64 && output.EndsWith(".app", StringComparison.Ordinal))
                output = output.Substring(0, output.Length - 4) + ".exe";
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(output)));
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { scenePath },
                locationPathName = output,
                target = target,
                targetGroup = BuildTargetGroup.Standalone,
                options = BuildOptions.Development | BuildOptions.DetailedBuildReport,
            });
            var evidence = new BuildEvidence
            {
                milestone = milestone,
                unityVersion = Application.unityVersion,
                target = target.ToString(),
                architecture = TargetArchitecture(),
                scriptingBackend = PlayerSettings.GetScriptingBackend(NamedBuildTarget.Standalone).ToString(),
                nativeArguments = PlayerSettings.GetAdditionalIl2CppArgs(),
                result = report.summary.result.ToString(),
                totalErrors = report.summary.totalErrors,
                totalWarnings = report.summary.totalWarnings,
                durationSeconds = report.summary.totalTime.TotalSeconds,
                outputPath = Path.GetFullPath(output),
                nativeArtifacts = report.GetFiles().Select(file => file.path)
                    .Where(path => path.Contains("GameAssembly") || path.EndsWith(".dylib") || path.EndsWith(".dSYM")).ToArray(),
            };
            Directory.CreateDirectory("_temp/AssemblyShadow");
            File.WriteAllText("_temp/AssemblyShadow/" + milestone.ToLowerInvariant() + "-build.json",
                JsonUtility.ToJson(evidence, true));
            if (report.summary.result != BuildResult.Succeeded || report.summary.totalErrors != 0)
                throw new BuildFailedException(milestone + " IL2CPP Player build failed.");
            Debug.Log("[AssemblyShadow] Build evidence: " + JsonUtility.ToJson(evidence));
        }

        public static void SetNativeFeature(bool enabled)
        {
            // This goes to the native compiler, independently of managed scripting symbols.
            PlayerSettings.SetAdditionalIl2CppArgs(enabled
                ? "--compiler-flags=\"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1\""
                : "--compiler-flags=\"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=0\"");
        }

        public static string TargetArchitecture()
        {
#if UNITY_EDITOR_OSX
            if (EditorUserBuildSettings.activeBuildTarget == BuildTarget.StandaloneOSX)
                return UnityEditor.OSXStandalone.UserBuildSettings.architecture.ToString().ToLowerInvariant();
#endif
            return "x64";
        }

        public static string Argument(string name, string fallback)
        {
            var args = Environment.GetCommandLineArgs();
            for (int i = 0; i + 1 < args.Length; ++i)
                if (args[i] == name) return args[i + 1];
            return fallback;
        }

        private static void EnsureAssets()
        {
            Directory.CreateDirectory(ResourceRoot);
            Directory.CreateDirectory(Path.GetDirectoryName(ScenePath));
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            string prefabPath = ResourceRoot + "/BaselinePrefab.prefab";
            if (!File.Exists(prefabPath))
            {
                var prefab = new GameObject("M00 AOT Prefab");
                prefab.AddComponent<BaselineProbe>().number = 1234;
                PrefabUtility.SaveAsPrefabAsset(prefab, prefabPath);
                UnityEngine.Object.DestroyImmediate(prefab);
            }
            string dataPath = ResourceRoot + "/BaselineData.asset";
            if (!File.Exists(dataPath))
            {
                var data = ScriptableObject.CreateInstance<BaselineData>();
                data.number = 5678;
                AssetDatabase.CreateAsset(data, dataPath);
            }
            if (!File.Exists(ScenePath))
            {
                var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                var root = new GameObject("M00 Bootstrap");
                root.AddComponent<BaselineBootstrap>();
                root.AddComponent<BaselineProbe>();
                EditorSceneManager.SaveScene(scene, ScenePath);
            }
        }

        [Serializable]
        private sealed class InstallEvidence
        {
            public bool identical;
            public string receiptSha256;
            public int installedFiles;
        }

        [Serializable]
        private sealed class BuildEvidence
        {
            public string milestone;
            public string unityVersion;
            public string target;
            public string architecture;
            public string scriptingBackend;
            public string nativeArguments;
            public string result;
            public int totalErrors;
            public int totalWarnings;
            public double durationSeconds;
            public string outputPath;
            public string[] nativeArtifacts;
        }
    }
}
