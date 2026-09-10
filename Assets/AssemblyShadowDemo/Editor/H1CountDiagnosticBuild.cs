using System;
using System.IO;
using System.Linq;
using AssemblyShadowBaseline.Editor;
using HybridCLR.Editor.AssemblyShadow;
using HybridCLR.Editor.Commands;
using UnityEditor;
using UnityEditorInternal;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Builds a fresh H1 count diagnostic Player in either native feature mode.</summary>
    public static class H1CountDiagnosticBuild
    {
        public const string DiagnosticScene = "Assets/AssemblyShadowR01BDiagnostics/Scenes/H1CountDiagnostic.unity";
        public const string DiagnosticDefine = "ASSEMBLY_SHADOW_H1_COUNT_DIAGNOSTICS";
        public const string NativeDiagnosticDefine = "HYBRIDCLR_H1_COUNT_DIAGNOSTICS";
        public const string R01BDiagnosticsDefine = "ASSEMBLY_SHADOW_R01B_DIAGNOSTICS";
        public const string DiagnosticsAssemblyName = "AssemblyShadow.R01BDiagnostics";
        private const string RunnerTypeName = "AssemblyShadowDemo.H1CountDiagnosticRunner";
        private const string ReceiptDefault = "_temp/AssemblyShadow/H1/H1CountDiagnosticPlayerBuild.json";
        private static readonly string[] Candidates = {
            "AssemblyShadow.H1Count.Target",
            "AssemblyShadow.H1Nested.Target",
        };

        public static void BuildDiagnosticPlayer()
        {
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            Require(target == BuildTarget.StandaloneOSX,
                "H1 count diagnostic Player is pinned to StandaloneOSX.");
#if UNITY_EDITOR_OSX
            OSArchitecture previousOsxArchitecture = UnityEditor.OSXStandalone.UserBuildSettings.architecture;
#else
            throw new BuildFailedException("H1 count diagnostic Player requires a macOS Unity Editor.");
#endif
            bool featureEnabled = ParseFeature(AssemblyShadowBuildCommands.Argument("-shadowH1Feature", ""));
            Il2CppCompilerConfiguration cppConfiguration = ParseCppConfiguration(
                AssemblyShadowBuildCommands.Argument("-shadowH1Cpp", ""));
            string outputArgument = AssemblyShadowBuildCommands.Argument("-shadowH1PlayerOutput", "");
            Require(!string.IsNullOrWhiteSpace(outputArgument), "-shadowH1PlayerOutput is required.");
            string output = Path.GetFullPath(outputArgument);
            string receiptPath = Path.GetFullPath(AssemblyShadowBuildCommands.Argument("-shadowH1BuildReceipt", ReceiptDefault));
            Require(!File.Exists(output) && !Directory.Exists(output), "H1 diagnostic Player output must be new: " + output);
            Require(!File.Exists(receiptPath) && !Directory.Exists(receiptPath), "H1 diagnostic receipt must be new: " + receiptPath);
            Directory.CreateDirectory(Path.GetDirectoryName(output));

            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            var settings = AssemblyShadowSettings.Instance;
            string settingsJson = JsonUtility.ToJson(settings);
            EditorBuildSettingsScene[] scenesBefore = EditorBuildSettings.scenes;
            string nativeArgumentsBefore = PlayerSettings.GetAdditionalIl2CppArgs();
            Il2CppCompilerConfiguration cppBefore = PlayerSettings.GetIl2CppCompilerConfiguration(NamedBuildTarget.Standalone);
            bool developmentBefore = EditorUserBuildSettings.development;
            bool allowDebuggingBefore = EditorUserBuildSettings.allowDebugging;
            bool connectProfilerBefore = EditorUserBuildSettings.connectProfiler;
            bool buildScriptsOnlyBefore = EditorUserBuildSettings.buildScriptsOnly;
            ScriptingImplementation scriptingBackendBefore = PlayerSettings.GetScriptingBackend(NamedBuildTarget.Standalone);
            string snapshot = null;
            bool captureStarted = false;
            string nativeArgumentsUsed = null;
            H1BuildInputProvenance.Capture nativeProvenance = null;
            GeneratedBuildInput[] generatedBuildInputs = null;
            DiagnosticBuildReceipt completedReceipt = null;
            string sourcePinsHashBefore = null;
            string sourcePinsJsonBefore = null;
            string baselineId = "H1Count-" + (featureEnabled ? "On" : "Off") + "-" + cppConfiguration;
            try
            {
#if UNITY_EDITOR_OSX
                UnityEditor.OSXStandalone.UserBuildSettings.architecture = OSArchitecture.ARM64;
#endif
                ConfigureSettings(settings, target, featureEnabled, baselineId);
                ShadowSourcePins pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
                string sourcePinsPathBefore = Path.Combine(projectRoot, settings.sourcePinFile);
                sourcePinsHashBefore = ShadowHash.File(sourcePinsPathBefore);
                sourcePinsJsonBefore = File.ReadAllText(sourcePinsPathBefore);
                EnsureScene(baselineId, pins.RuntimeAbiHash(), featureEnabled, cppConfiguration);
                generatedBuildInputs = CaptureGeneratedBuildInputs(projectRoot);
                EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(DiagnosticScene, true) };
                PlayerSettings.SetScriptingBackend(NamedBuildTarget.Standalone, ScriptingImplementation.IL2CPP);
                PlayerSettings.SetIl2CppCompilerConfiguration(NamedBuildTarget.Standalone, cppConfiguration);
                EditorUserBuildSettings.development = true;
                EditorUserBuildSettings.allowDebugging = false;
                EditorUserBuildSettings.connectProfiler = false;
                EditorUserBuildSettings.buildScriptsOnly = false;
                BaselineBuild.SetNativeFeature(featureEnabled);
                nativeArgumentsUsed = string.Format("--compiler-flags=\"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW={0} -D{1}=1\"",
                    featureEnabled ? 1 : 0, NativeDiagnosticDefine);
                PlayerSettings.SetAdditionalIl2CppArgs(nativeArgumentsUsed);
                Require(PlayerSettings.GetAdditionalIl2CppArgs() == nativeArgumentsUsed,
                    "H1 native diagnostic compiler arguments were not applied exactly.");
                AssemblyShadowSettings.Save();
                AssetDatabase.SaveAssets();
                PrebuildCommand.GenerateAll();
                nativeProvenance = H1BuildInputProvenance.CaptureAfterGenerate(
                    projectRoot, settings.sourcePinFile, featureEnabled);

                ShadowSourcePins pinsForCapture = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
                string[] defines = ShadowReflectionBindingEvidence.CompilationDefines(new[] { DiagnosticDefine, R01BDiagnosticsDefine });
                snapshot = Path.GetFullPath("_temp/AssemblyShadow/H1/H1CountDiagnosticPlayerInputs-" + Guid.NewGuid().ToString("N"));
                Directory.CreateDirectory(Path.GetDirectoryName(snapshot));
                ShadowPlayerInputCapture.Begin(snapshot, baselineId, target, settings.architecture, pinsForCapture, Candidates, defines, true);
                captureStarted = true;
                M07Build.WithPlayerBuildSettings(target, () =>
                {
                    var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                        scenes = new[] { DiagnosticScene },
                        locationPathName = output,
                        target = target,
                        targetGroup = BuildTargetGroup.Standalone,
                        options = BuildOptions.Development | BuildOptions.DetailedBuildReport | BuildOptions.CleanBuildCache,
                        extraScriptingDefines = defines,
                    });
                    ShadowPlayerInputCapture.CompleteSuccessfulBuild(report);
                });
                ShadowPlayerInputCapture.End();
                captureStarted = false;
                H1BuildInputProvenance.RequireUnchanged(nativeProvenance);
                RequireGeneratedBuildInputsUnchanged(projectRoot, generatedBuildInputs);

                AssemblySnapshotReceipt captured = AssemblySnapshot.ReadAndVerify(snapshot, true);
                M04AssemblyIdentity[] linked = M04AssemblyIdentityProof.ReadLinked(snapshot, captured);
                Require(linked.Any(item => string.Equals(item.name, DiagnosticsAssemblyName, StringComparison.Ordinal)),
                    "The diagnostics runtime assembly was not retained in the linked Player input.");
                M04NativeMetadataProof.Capture nativeMetadata = M04NativeMetadataProof.ReadPlayer(output, linked);
                string executable = PlayerExecutable(output);
                string sourcePinsPathForReceipt = Path.Combine(projectRoot, settings.sourcePinFile);
                string sourcePinsJson = File.ReadAllText(sourcePinsPathForReceipt);
                string sourcePinsHash = ShadowHash.File(sourcePinsPathForReceipt);
                Require(sourcePinsHash == sourcePinsHashBefore && sourcePinsJson == sourcePinsJsonBefore,
                    "Source pins changed during H1 diagnostic Player build.");
                Require(captured.buildId == baselineId, "Captured input snapshot build identity differs from the requested diagnostic identity.");
                completedReceipt = new DiagnosticBuildReceipt {
                    schemaVersion = 1,
                    kind = "H1CountDiagnosticPlayerBuild",
                    diagnosticOnly = true,
                    featureEnabled = featureEnabled,
                    cppConfiguration = cppConfiguration.ToString(),
                    baselineBuildId = baselineId,
                    runtimeAbiHash = pinsForCapture.RuntimeAbiHash(),
                    unityVersion = Application.unityVersion,
                    target = target.ToString(),
                    architecture = settings.architecture,
                    buildGuid = captured.buildGuid,
                    playerOutput = captured.playerOutput,
                    playerExecutable = executable,
                    playerExecutableSha256 = ShadowHash.File(executable),
                    inputSnapshot = snapshot,
                    inputSnapshotHash = captured.snapshotHash,
                    sourcePinFile = sourcePinsPathForReceipt,
                    sourcePinSha256 = sourcePinsHash,
                    sourcePinsJson = sourcePinsJson,
                    nativeLibraryPath = captured.nativeLibraryPath,
                    nativeLibrarySha256 = captured.nativeLibrarySha256,
                    nativeArguments = nativeArgumentsUsed,
                    extraScriptingDefines = defines,
                    candidates = Candidates,
                    scenes = new[] { DiagnosticScene },
                    linkedInputNames = linked.OrderBy(item => item.name, StringComparer.Ordinal).Select(item => item.name).ToArray(),
                    linkedInputSha256 = linked.OrderBy(item => item.name, StringComparer.Ordinal).Select(item => item.sha256).ToArray(),
                    assemblyIdentities = linked,
                    nativeMetadataPath = nativeMetadata.path,
                    nativeMetadataSha256 = nativeMetadata.sha256,
                    nativeMetadataVersion = nativeMetadata.version,
                    nativeAssemblyIdentities = nativeMetadata.assemblies,
                    nativeGeneratedAssemblyNames = nativeMetadata.generatedAssemblyNames,
                    nativeProvenance = nativeProvenance,
                    generatedBuildInputs = generatedBuildInputs,
                    note = "Diagnostic-only artifact; the two target assemblies are build candidates and are never a production manifest or runtime fixture.",
                };
            }
            finally
            {
                try
                {
                    if (captureStarted) ShadowPlayerInputCapture.End();
                    PlayerSettings.SetAdditionalIl2CppArgs(nativeArgumentsBefore);
                    PlayerSettings.SetScriptingBackend(NamedBuildTarget.Standalone, scriptingBackendBefore);
                    PlayerSettings.SetIl2CppCompilerConfiguration(NamedBuildTarget.Standalone, cppBefore);
                    EditorUserBuildSettings.development = developmentBefore;
                    EditorUserBuildSettings.allowDebugging = allowDebuggingBefore;
                    EditorUserBuildSettings.connectProfiler = connectProfilerBefore;
                    EditorUserBuildSettings.buildScriptsOnly = buildScriptsOnlyBefore;
                    EditorBuildSettings.scenes = scenesBefore;
                    JsonUtility.FromJsonOverwrite(settingsJson, settings);
                    AssemblyShadowSettings.Save();
                    AssetDatabase.SaveAssets();
                }
                finally
                {
#if UNITY_EDITOR_OSX
                    UnityEditor.OSXStandalone.UserBuildSettings.architecture = previousOsxArchitecture;
#endif
                }
            }
            Require(completedReceipt != null, "H1 diagnostic build did not produce a completed receipt after settings restoration.");
            Directory.CreateDirectory(Path.GetDirectoryName(receiptPath));
            M04AssemblyIdentityProof.WriteNewJson(receiptPath, completedReceipt);
            Debug.Log("[AssemblyShadow H1] Diagnostic Player captured: " + receiptPath);
        }

        private static GeneratedBuildInput[] CaptureGeneratedBuildInputs(string projectRoot)
        {
            string[] paths = { DiagnosticScene, DiagnosticScene + ".meta" };
            return paths.Select(relative => {
                string absolute = Path.Combine(projectRoot, relative.Replace('/', Path.DirectorySeparatorChar));
                Require(File.Exists(absolute) && !IsSymlink(absolute), "Generated H1 diagnostic input is missing or symlinked: " + relative);
                return new GeneratedBuildInput { path = relative, sha256 = ShadowHash.File(absolute) };
            }).ToArray();
        }

        private static void RequireGeneratedBuildInputsUnchanged(string projectRoot, GeneratedBuildInput[] expected)
        {
            Require(expected != null && expected.Length == 2, "Generated H1 diagnostic input inventory is incomplete.");
            GeneratedBuildInput[] actual = CaptureGeneratedBuildInputs(projectRoot);
            Require(actual.Length == expected.Length && actual.Zip(expected,
                (left, right) => left.path == right.path && left.sha256 == right.sha256).All(value => value),
                "Generated H1 diagnostic scene or meta bytes changed during the Player build.");
        }

        private static bool IsSymlink(string path)
        {
            try { return (File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0; }
            catch (FileNotFoundException) { return false; }
        }

        private static void ConfigureSettings(AssemblyShadowSettings settings, BuildTarget target, bool featureEnabled, string baselineId)
        {
            settings.enableAssemblyShadow = featureEnabled;
            settings.shadowAssemblyDefinitions = new AssemblyDefinitionAsset[0];
            settings.shadowAssemblyNames = Candidates.ToArray();
            settings.bootstrapAssemblyDefinitions = new AssemblyDefinitionAsset[0];
            settings.bootstrapAssemblyNames = new[] { DiagnosticsAssemblyName };
            settings.architecture = BaselineBuild.TargetArchitecture();
            settings.buildId = baselineId;
            settings.playerInputSnapshot = "";
            settings.baselineManifestPath = "";
            AssemblyShadowSettings.Save();
            AssemblyShadowSettingsUtil.ValidateSettingsOrThrow(settings);
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            ShadowAssemblyPolicyValidator.ValidateBeforeCompile(policy, target).ThrowIfInvalid();
        }

        private static void EnsureScene(string baselineId, string runtimeAbiHash, bool featureEnabled, Il2CppCompilerConfiguration cppConfiguration)
        {
            Require(!string.IsNullOrWhiteSpace(baselineId) && !string.IsNullOrWhiteSpace(runtimeAbiHash),
                "H1 diagnostic scene requires baseline identity and runtime ABI hash.");
            string directory = Path.GetDirectoryName(DiagnosticScene);
            if (!Directory.Exists(directory)) Directory.CreateDirectory(directory);
            SceneAsset existing = AssetDatabase.LoadAssetAtPath<SceneAsset>(DiagnosticScene);
            var scene = existing != null ? EditorSceneManager.OpenScene(DiagnosticScene, OpenSceneMode.Single) :
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Type runnerType = FindRunnerType();
            var runners = scene.GetRootGameObjects().SelectMany(root => root.GetComponentsInChildren<MonoBehaviour>(true))
                .Where(component => component != null && component.GetType() == runnerType).ToArray();
            Require(runners.Length <= 1, "H1 diagnostic scene contains duplicate runners.");
            MonoBehaviour runner = runners.Length == 1 ? runners[0] :
                (MonoBehaviour)new GameObject("AssemblyShadow H1 Count Diagnostic Runner").AddComponent(runnerType);
            SetString(runner, "expectedBaselineBuildId", baselineId);
            SetString(runner, "expectedRuntimeAbiHash", runtimeAbiHash);
            SetBool(runner, "expectedFeatureEnabled", featureEnabled);
            SetString(runner, "expectedCppConfiguration", cppConfiguration.ToString());
            Require(EditorSceneManager.SaveScene(scene, DiagnosticScene), "Could not save H1 diagnostic scene.");
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        }

        private static Type FindRunnerType()
        {
            foreach (var assembly in AppDomain.CurrentDomain.GetAssemblies())
            {
                Type type = assembly.GetType(RunnerTypeName, false);
                if (type != null && typeof(MonoBehaviour).IsAssignableFrom(type)) return type;
            }
            throw new BuildFailedException("H1 diagnostic runner type is unavailable; the diagnostics runtime assembly must provide " + RunnerTypeName + ".");
        }

        private static void SetString(MonoBehaviour runner, string name, string value)
        {
            var serialized = new SerializedObject(runner);
            SerializedProperty property = serialized.FindProperty(name);
            Require(property != null && property.propertyType == SerializedPropertyType.String, "Runner field is missing or not a string: " + name);
            property.stringValue = value;
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void SetBool(MonoBehaviour runner, string name, bool value)
        {
            var serialized = new SerializedObject(runner);
            SerializedProperty property = serialized.FindProperty(name);
            Require(property != null && property.propertyType == SerializedPropertyType.Boolean, "Runner field is missing or not a bool: " + name);
            property.boolValue = value;
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static bool ParseFeature(string value)
        {
            if (string.Equals(value, "on", StringComparison.OrdinalIgnoreCase)) return true;
            if (string.Equals(value, "off", StringComparison.OrdinalIgnoreCase)) return false;
            throw new BuildFailedException("-shadowH1Feature must be on or off.");
        }

        private static Il2CppCompilerConfiguration ParseCppConfiguration(string value)
        {
            if (string.Equals(value, "Debug", StringComparison.OrdinalIgnoreCase)) return Il2CppCompilerConfiguration.Debug;
            if (string.Equals(value, "Release", StringComparison.OrdinalIgnoreCase)) return Il2CppCompilerConfiguration.Release;
            throw new BuildFailedException("-shadowH1Cpp must be Debug or Release.");
        }

        private static string PlayerExecutable(string output)
        {
            string macos = Path.Combine(output, "Contents/MacOS");
            Require(Directory.Exists(macos), "H1 diagnostic OSX Player executable directory is missing: " + macos);
            string[] files = Directory.GetFiles(macos, "*", SearchOption.TopDirectoryOnly)
                .Where(path => !path.EndsWith(".dSYM", StringComparison.OrdinalIgnoreCase)).ToArray();
            Require(files.Length == 1, "H1 diagnostic OSX Player must contain exactly one executable.");
            return Path.GetFullPath(files[0]);
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new BuildFailedException(message);
        }

        [Serializable]
        public sealed class GeneratedBuildInput
        {
            public string path, sha256;
        }

        [Serializable]
        public sealed class DiagnosticBuildReceipt
        {
            public int schemaVersion, nativeMetadataVersion;
            public bool diagnosticOnly, featureEnabled;
            public string kind, cppConfiguration, baselineBuildId, runtimeAbiHash, unityVersion, target, architecture, buildGuid;
            public string playerOutput, playerExecutable, playerExecutableSha256, inputSnapshot, inputSnapshotHash;
            public string sourcePinFile, sourcePinSha256, sourcePinsJson, nativeLibraryPath, nativeLibrarySha256, nativeArguments;
            public string[] extraScriptingDefines, candidates, scenes, linkedInputNames, linkedInputSha256;
            public M04AssemblyIdentity[] assemblyIdentities;
            public string nativeMetadataPath, nativeMetadataSha256;
            public M04NativeAssemblyIdentity[] nativeAssemblyIdentities;
            public string[] nativeGeneratedAssemblyNames;
            public H1BuildInputProvenance.Capture nativeProvenance;
            public GeneratedBuildInput[] generatedBuildInputs;
            public string note;
        }
    }
}
