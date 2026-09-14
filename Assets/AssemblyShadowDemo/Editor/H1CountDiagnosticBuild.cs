using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using AssemblyShadowBaseline.Editor;
using HybridCLR.Editor.AssemblyShadow;
using HybridCLR.Editor.Commands;
using UnityEditor;
using UnityEditorInternal;
using UnityEditor.Build;
using UnityEditor.Compilation;
using UnityEditor.SceneManagement;
using UnityEngine;
using HybridCLR.Editor.Settings;

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
        private const string PreparationArgument = "-shadowH1PreparationRoot";
        private const string PreparationStateName = "h1-count-diagnostic-define-state.json";
        private const string PreparationRestoreName = "h1-count-diagnostic-defines-restored.json";
        private const string GeneratedInputsDirectory = "GeneratedBuildInputs";
        private static readonly string[] Candidates = {
            "AssemblyShadow.H1Count.Target",
            "AssemblyShadow.H1Nested.Target",
        };
        private static readonly string[] DiagnosticAssemblies = Candidates.Concat(new[] { DiagnosticsAssemblyName }).ToArray();
        private static readonly string[] RequiredInternalEditorAssemblies = {
            "AssemblyShadowDemo.Editor",
            "AssemblyShadowDemo.EditorTests",
        };

        /// <summary>Stages diagnostic asmdef defines for the next fresh Unity process.</summary>
        public static void PrepareDiagnosticBuild()
        {
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            Require(target == BuildTarget.StandaloneOSX, "H1 count diagnostic Player is pinned to StandaloneOSX.");
            RequireQuiescentEditor();
            string projectRoot = ProjectRoot();
            string run = PreparationRoot(projectRoot);
            string statePath = Path.Combine(run, PreparationStateName);
            string restorePath = Path.Combine(run, PreparationRestoreName);
            Require(!File.Exists(statePath) && !File.Exists(restorePath),
                "H1 diagnostic preparation state already exists; use a new H1CountBuild-<guid> directory.");
            string original = CurrentScriptingDefines();
            var state = new DiagnosticPreparationState {
                runDirectory = run,
                projectDirectory = projectRoot,
                unityVersion = Application.unityVersion,
                target = target.ToString(),
                defineTarget = NamedBuildTarget.Standalone.TargetName,
                originalDefines = original,
                stagedDefines = StagedScriptingDefines(original),
                prepareProcessId = System.Diagnostics.Process.GetCurrentProcess().Id,
                projectSettingsSha256 = ShadowHash.File(ProjectSettingsPath(projectRoot)),
            };
            state.stateHash = PreparationStateHash(state);
            WriteNewJson(statePath, state);
            Require(CurrentScriptingDefines() == state.originalDefines,
                "Standalone scripting defines changed before H1 diagnostic staging.");
            SetScriptingDefines(state.stagedDefines);
            Debug.Log("[AssemblyShadow H1] Diagnostic defines staged; start a fresh Unity process for the build: " + run);
        }

        /// <summary>Restores the exact recorded Standalone define string after success or failure.</summary>
        public static void RestoreDiagnosticBuild()
        {
            string projectRoot = ProjectRoot();
            string run = PreparationRoot(projectRoot);
            string statePath = Path.Combine(run, PreparationStateName);
            if (!File.Exists(statePath))
            {
                Debug.Log("[AssemblyShadow H1] No recorded diagnostic define mutation; restoration leaves settings untouched: " + run);
                return;
            }
            RequireQuiescentEditor();
            string stateSha256;
            DiagnosticPreparationState state = ReadPreparationState(run, out stateSha256);
            RequireCurrentPreparationContext(state);
            Require(System.Diagnostics.Process.GetCurrentProcess().Id != state.prepareProcessId,
                "H1 diagnostic defines must be restored from a fresh Unity process.");
            string current = CurrentScriptingDefines();
            Require(current == state.originalDefines || current == state.stagedDefines,
                "Standalone scripting defines changed concurrently; refusing to overwrite them during H1 recovery.");
            if (current == state.stagedDefines) SetScriptingDefines(state.originalDefines);
            Require(CurrentScriptingDefines() == state.originalDefines,
                "H1 diagnostic restoration did not recover the exact original Standalone define string.");
            string restorePath = Path.Combine(run, PreparationRestoreName);
            if (File.Exists(restorePath))
            {
                var receipt = JsonUtility.FromJson<DiagnosticPreparationRestore>(ReadRegularText(restorePath));
                Require(receipt != null && receipt.schemaVersion == 1 && receipt.stateSha256 == stateSha256 &&
                    receipt.originalDefines == state.originalDefines,
                    "Existing H1 diagnostic restoration receipt does not match this preparation state.");
            }
            else
            {
                WriteNewJson(restorePath, new DiagnosticPreparationRestore {
                    stateSha256 = stateSha256,
                    originalDefines = state.originalDefines,
                });
            }
            Debug.Log("[AssemblyShadow H1] Exact original diagnostic defines restored: " + run);
        }

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
            string preparationStateSha256;
            DiagnosticPreparationState preparation = RequireStagedPreparation(out preparationStateSha256);
            Directory.CreateDirectory(Path.GetDirectoryName(output));

            string projectRoot = ProjectRoot();
            var settings = AssemblyShadowSettings.Instance;
            string settingsJson = JsonUtility.ToJson(settings);
            string hybridClrSettingsJson = JsonUtility.ToJson(HybridCLRSettings.Instance);
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
            H1CompilerProvenance.GraphInventory beeGraphBefore = null;
            H1CompilerProvenance.Capture compilerProvenance = null;
            string compilerProvenancePath = null;
            string compilerProvenanceSha256 = null;
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
                generatedBuildInputs = StageGeneratedBuildInputs(projectRoot, preparation.runDirectory);
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
                    projectRoot, settings.sourcePinFile, featureEnabled, preparation.runDirectory);

                ShadowSourcePins pinsForCapture = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
                string[] defines = ShadowReflectionBindingEvidence.CompilationDefines(new[] { DiagnosticDefine, R01BDiagnosticsDefine });
                snapshot = Path.GetFullPath("_temp/AssemblyShadow/H1/H1CountDiagnosticPlayerInputs-" + Guid.NewGuid().ToString("N"));
                Directory.CreateDirectory(Path.GetDirectoryName(snapshot));
                ShadowPlayerInputCapture.Begin(snapshot, baselineId, target, settings.architecture, pinsForCapture, Candidates, defines, true);
                captureStarted = true;
                beeGraphBefore = H1CompilerProvenance.Begin(projectRoot);
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
                RetainGeneratedBuildInputs(snapshot, preparation.runDirectory, generatedBuildInputs);

                AssemblySnapshotReceipt captured = AssemblySnapshot.ReadAndVerify(snapshot, true);
                compilerProvenance = H1CompilerProvenance.CaptureAfterBuild(
                    projectRoot, output, baselineId, captured.buildGuid, captured.snapshotHash,
                    captured.nativeLibraryPath, captured.nativeLibrarySha256, sourcePinsHashBefore,
                    beeGraphBefore, Path.Combine(preparation.runDirectory, "CompilerProvenance"),
                    out compilerProvenancePath, out compilerProvenanceSha256);
                M04AssemblyIdentity[] linked = M04AssemblyIdentityProof.ReadLinked(snapshot, captured);
                Require(linked.Any(item => string.Equals(item.name, DiagnosticsAssemblyName, StringComparison.Ordinal)),
                    "The diagnostics runtime assembly was not retained in the linked Player input.");
                Require(linked.Any(item => string.Equals(item.name, "AssemblyShadowDemo.Bootstrap", StringComparison.Ordinal)),
                    "The H1 early startup assembly was not retained in the linked Player input.");
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
                    startupBootstrapAssembly = settings.startupBootstrapAssembly,
                    startupBootstrapNamespace = settings.startupBootstrapNamespace,
                    startupBootstrapType = settings.startupBootstrapType,
                    startupBootstrapMethod = settings.startupBootstrapMethod,
                    unityVersion = Application.unityVersion,
                    target = target.ToString(),
                    architecture = settings.architecture,
                    buildGuid = captured.buildGuid,
                    playerOutput = captured.playerOutput,
                    playerExecutable = executable,
                    playerExecutableSha256 = ShadowHash.File(executable),
                    inputSnapshot = snapshot,
                    inputSnapshotHash = captured.snapshotHash,
                    sourcePinFile = nativeProvenance.sourcePinFile,
                    sourcePinSha256 = sourcePinsHash,
                    sourcePinsJson = sourcePinsJson,
                    nativeLibraryPath = captured.nativeLibraryPath,
                    nativeLibrarySha256 = captured.nativeLibrarySha256,
                    nativeArguments = nativeArgumentsUsed,
                    compilerProvenance = compilerProvenance,
                    compilerProvenancePath = compilerProvenancePath,
                    compilerProvenanceSha256 = compilerProvenanceSha256,
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
                    preparationStatePath = Path.Combine(preparation.runDirectory, PreparationStateName),
                    preparationStateSha256 = preparationStateSha256,
                    originalScriptingDefines = preparation.originalDefines,
                    stagedScriptingDefines = preparation.stagedDefines,
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
                    // Policy/generation can reload the singleton; restore the instance Save actually persists.
                    JsonUtility.FromJsonOverwrite(settingsJson, AssemblyShadowSettings.Instance);
                    AssemblyShadowSettings.Save();
                    Require(JsonUtility.ToJson(AssemblyShadowSettings.Instance) == settingsJson,
                        "Assembly Shadow settings did not restore after the diagnostic build.");
                    JsonUtility.FromJsonOverwrite(hybridClrSettingsJson, HybridCLRSettings.Instance);
                    HybridCLRSettings.Save();
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

        private static GeneratedBuildInput[] StageGeneratedBuildInputs(string projectRoot, string preparationRoot)
        {
            string[] paths = { DiagnosticScene, DiagnosticScene + ".meta" };
            string staging = Path.Combine(preparationRoot, GeneratedInputsDirectory);
            Require(!Directory.Exists(staging) && !File.Exists(staging),
                "H1 generated-input staging already exists; preparation state is single-use.");
            Directory.CreateDirectory(staging);
            return paths.Select(relative => {
                string absolute = Path.Combine(projectRoot, relative.Replace('/', Path.DirectorySeparatorChar));
                Require(File.Exists(absolute) && !IsSymlink(absolute), "Generated H1 diagnostic input is missing or symlinked: " + relative);
                string snapshotRelative = GeneratedInputsDirectory + "/" + Path.GetFileName(relative);
                string staged = Path.Combine(preparationRoot, snapshotRelative.Replace('/', Path.DirectorySeparatorChar));
                using (var source = new FileStream(absolute, FileMode.Open, FileAccess.Read, FileShare.Read))
                using (var destination = new FileStream(staged, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                { source.CopyTo(destination); destination.Flush(true); }
                string sha256 = ShadowHash.File(absolute);
                Require(ShadowHash.File(staged) == sha256, "Generated H1 diagnostic input changed while it was staged: " + relative);
                return new GeneratedBuildInput { sourcePath = relative, path = snapshotRelative, sha256 = sha256 };
            }).ToArray();
        }

        private static void RequireGeneratedBuildInputsUnchanged(string projectRoot, GeneratedBuildInput[] expected)
        {
            Require(expected != null && expected.Length == 2, "Generated H1 diagnostic input inventory is incomplete.");
            foreach (GeneratedBuildInput item in expected)
            {
                string live = Path.Combine(projectRoot, item.sourcePath.Replace('/', Path.DirectorySeparatorChar));
                Require(File.Exists(live) && !IsSymlink(live) && ShadowHash.File(live) == item.sha256,
                    "Generated H1 diagnostic scene or meta bytes changed during the Player build: " + item.sourcePath);
            }
        }

        private static void RetainGeneratedBuildInputs(string snapshot, string preparationRoot, GeneratedBuildInput[] expected)
        {
            string staged = Path.Combine(preparationRoot, GeneratedInputsDirectory);
            string retained = Path.Combine(snapshot, GeneratedInputsDirectory);
            Require(Directory.Exists(snapshot) && Directory.Exists(staged) && !Directory.Exists(retained),
                "H1 generated inputs require a new retained directory in the completed Player input snapshot.");
            Directory.Move(staged, retained);
            foreach (GeneratedBuildInput item in expected)
            {
                string path = Path.Combine(snapshot, item.path.Replace('/', Path.DirectorySeparatorChar));
                Require(File.Exists(path) && !IsSymlink(path) && ShadowHash.File(path) == item.sha256,
                    "Retained H1 diagnostic input differs from its pre-build bytes: " + item.path);
            }
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
            settings.bootstrapAssemblyNames = new[] { "AssemblyShadowDemo.Bootstrap" };
            settings.startupBootstrapAssembly = "AssemblyShadowDemo.Bootstrap";
            settings.startupBootstrapNamespace = "AssemblyShadowDemo";
            settings.startupBootstrapType = "H1CountEarlyStartup";
            settings.startupBootstrapMethod = "Run";
            Require(RequiredInternalEditorAssemblies.All(required =>
                (settings.allowedInternalEditorAssemblies ?? new string[0]).Any(actual =>
                    string.Equals(actual, required, StringComparison.OrdinalIgnoreCase))),
                "H1 diagnostic policy requires the project's existing Editor and EditorTests internal-dependency allowances.");
            settings.explicitDependencyConfig = new TextAsset("{\"schemaVersion\":2,\"runtimeDependencies\":[],\"resourceDependencies\":[],\"serializeReferenceDependencies\":[],\"bootstrapEntrypoints\":[]}");
            settings.architecture = BaselineBuild.TargetArchitecture();
            settings.buildId = baselineId;
            settings.playerInputSnapshot = "";
            settings.baselineManifestPath = "";
            HybridCLRSettings hybridClr = HybridCLRSettings.Instance;
            hybridClr.enable = true;
            hybridClr.hotUpdateAssemblyDefinitions = new AssemblyDefinitionAsset[0];
            hybridClr.hotUpdateAssemblies = new string[0];
            hybridClr.preserveHotUpdateAssemblies = new string[0];
            hybridClr.patchAOTAssemblies = new string[0];
            hybridClr.externalHotUpdateAssembliyDirs = new string[0];
            AssemblyShadowSettings.Save();
            HybridCLRSettings.Save();
            AssemblyShadowSettingsUtil.ValidateSettingsOrThrow(settings);
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            ShadowAssemblyPolicyValidator.ValidateBeforeCompile(policy, target).ThrowIfInvalid();
        }

        private static DiagnosticPreparationState RequireStagedPreparation(out string stateSha256)
        {
            RequireQuiescentEditor();
            string run = PreparationRoot(ProjectRoot());
            DiagnosticPreparationState state = ReadPreparationState(run, out stateSha256);
            RequireCurrentPreparationContext(state);
            Require(!File.Exists(Path.Combine(run, PreparationRestoreName)),
                "H1 diagnostic preparation was already restored and cannot be reused.");
            Require(System.Diagnostics.Process.GetCurrentProcess().Id != state.prepareProcessId,
                "BuildDiagnosticPlayer requires a fresh Unity process after PrepareDiagnosticBuild.");
            Require(CurrentScriptingDefines() == state.stagedDefines,
                "Standalone scripting defines do not match the exact staged H1 diagnostic state.");
            var player = new HashSet<string>(CompilationPipeline.GetAssemblies(AssembliesType.Player)
                .Select(item => item.name), StringComparer.OrdinalIgnoreCase);
            var production = new HashSet<string>(CompilationPipeline.GetAssemblies(AssembliesType.PlayerWithoutTestAssemblies)
                .Select(item => item.name), StringComparer.OrdinalIgnoreCase);
            Require(DiagnosticAssemblies.All(name => player.Contains(name) && production.Contains(name)),
                "Fresh Unity Player compiler inventory does not include every dedicated H1 candidate and diagnostics assembly.");
            return state;
        }

        private static DiagnosticPreparationState ReadPreparationState(string run, out string stateSha256)
        {
            string path = Path.Combine(run, PreparationStateName);
            string json = ReadRegularText(path);
            stateSha256 = ShadowHash.File(path);
            var state = JsonUtility.FromJson<DiagnosticPreparationState>(json);
            Require(state != null && state.schemaVersion == 1 && state.runDirectory == run &&
                state.projectDirectory == ProjectRoot() && state.defineTarget == NamedBuildTarget.Standalone.TargetName &&
                state.stateHash == PreparationStateHash(state) && state.stagedDefines == StagedScriptingDefines(state.originalDefines),
                "H1 diagnostic preparation state is incomplete, changed, or belongs to another project.");
            return state;
        }

        private static void RequireCurrentPreparationContext(DiagnosticPreparationState state)
        {
            Require(state.projectDirectory == ProjectRoot() && state.unityVersion == Application.unityVersion &&
                state.target == EditorUserBuildSettings.activeBuildTarget.ToString() &&
                state.defineTarget == NamedBuildTarget.Standalone.TargetName,
                "H1 diagnostic target, Unity version, or project changed between preparation processes.");
        }

        private static string StagedScriptingDefines(string original)
        {
            Require(original != null, "Unity returned no Standalone scripting define string.");
            string[] values = original.Length == 0 ? new string[0] : original.Split(';');
            Require(values.All(value => Regex.IsMatch(value, "^[A-Za-z_][A-Za-z_0-9]*$")) &&
                values.Distinct(StringComparer.Ordinal).Count() == values.Length,
                "Existing Standalone scripting defines must be canonical; H1 staging will not normalize user settings.");
            Require(!values.Intersect(new[] { DiagnosticDefine, R01BDiagnosticsDefine }, StringComparer.Ordinal).Any(),
                "Dedicated H1 diagnostic defines are already present; remove them explicitly before preparing a diagnostic build.");
            return string.Join(";", values.Concat(new[] { DiagnosticDefine, R01BDiagnosticsDefine }).ToArray());
        }

        private static string PreparationStateHash(DiagnosticPreparationState state)
        {
            return ShadowHash.Text("h1-count-diagnostic-preparation:1\n" + state.runDirectory + "\n" + state.projectDirectory + "\n" +
                state.unityVersion + "\n" + state.target + "\n" + state.defineTarget + "\n" + state.originalDefines + "\n" +
                state.stagedDefines + "\n" + state.prepareProcessId + "\n" + state.projectSettingsSha256);
        }

        private static string PreparationRoot(string projectRoot)
        {
            string[] arguments = Environment.GetCommandLineArgs();
            int[] positions = arguments.Select((value, index) => new { value, index })
                .Where(item => item.value == PreparationArgument).Select(item => item.index).ToArray();
            Require(positions.Length == 1 && positions[0] + 1 < arguments.Length,
                "Exactly one -shadowH1PreparationRoot argument is required.");
            string value = arguments[positions[0] + 1];
            Require(!string.IsNullOrWhiteSpace(value) && Path.IsPathRooted(value),
                "H1 diagnostic preparation root must be absolute.");
            string run = Path.GetFullPath(value).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            string parent = Path.Combine(projectRoot, "_temp", "AssemblyShadow");
            Require(Path.GetDirectoryName(run) == parent && Regex.IsMatch(Path.GetFileName(run), "^H1CountBuild-[0-9a-f]{32}$") &&
                Directory.Exists(run) && !IsSymlink(run) && !IsSymlink(parent) && !IsSymlink(Path.GetDirectoryName(parent)),
                "H1 diagnostic preparation root must be an existing regular _temp/AssemblyShadow/H1CountBuild-<guid> directory.");
            return run;
        }

        private static string ProjectRoot() { return Path.GetFullPath(Path.Combine(Application.dataPath, "..")); }
        private static string ProjectSettingsPath(string projectRoot) { return Path.Combine(projectRoot, "ProjectSettings", "ProjectSettings.asset"); }
        private static string CurrentScriptingDefines() { return PlayerSettings.GetScriptingDefineSymbols(NamedBuildTarget.Standalone); }
        private static void SetScriptingDefines(string defines)
        {
            PlayerSettings.SetScriptingDefineSymbols(NamedBuildTarget.Standalone, defines);
            AssetDatabase.SaveAssets();
            Require(CurrentScriptingDefines() == defines, "Unity did not retain the exact requested Standalone scripting define string.");
        }
        private static void RequireQuiescentEditor()
        { Require(!EditorApplication.isCompiling && !EditorApplication.isUpdating, "Unity compilation/import must be idle for H1 diagnostic preparation."); }
        private static string ReadRegularText(string path)
        {
            Require(File.Exists(path) && !IsSymlink(path), "H1 diagnostic preparation evidence is missing or symlinked: " + path);
            return File.ReadAllText(path);
        }
        private static void WriteNewJson(string path, object value)
        {
            byte[] bytes = new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(value, true));
            using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            { stream.Write(bytes, 0, bytes.Length); stream.Flush(true); }
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
            public string sourcePath, path, sha256;
        }

        [Serializable]
        private sealed class DiagnosticPreparationState
        {
            public int schemaVersion = 1;
            public string runDirectory, projectDirectory, unityVersion, target, defineTarget;
            public string originalDefines, stagedDefines, projectSettingsSha256, stateHash;
            public int prepareProcessId;
        }

        [Serializable]
        private sealed class DiagnosticPreparationRestore
        {
            public int schemaVersion = 1;
            public string stateSha256, originalDefines;
        }

        [Serializable]
        public sealed class DiagnosticBuildReceipt
        {
            public int schemaVersion, nativeMetadataVersion;
            public bool diagnosticOnly, featureEnabled;
            public string kind, cppConfiguration, baselineBuildId, runtimeAbiHash, unityVersion, target, architecture, buildGuid;
            public string startupBootstrapAssembly, startupBootstrapNamespace, startupBootstrapType, startupBootstrapMethod;
            public string playerOutput, playerExecutable, playerExecutableSha256, inputSnapshot, inputSnapshotHash;
            public string sourcePinFile, sourcePinSha256, sourcePinsJson, nativeLibraryPath, nativeLibrarySha256, nativeArguments;
            public string compilerProvenancePath, compilerProvenanceSha256;
            public string preparationStatePath, preparationStateSha256, originalScriptingDefines, stagedScriptingDefines;
            public string[] extraScriptingDefines, candidates, scenes, linkedInputNames, linkedInputSha256;
            public M04AssemblyIdentity[] assemblyIdentities;
            public string nativeMetadataPath, nativeMetadataSha256;
            public M04NativeAssemblyIdentity[] nativeAssemblyIdentities;
            public string[] nativeGeneratedAssemblyNames;
            public H1BuildInputProvenance.Capture nativeProvenance;
            public H1CompilerProvenance.Capture compilerProvenance;
            public GeneratedBuildInput[] generatedBuildInputs;
            public string note;
        }
    }
}
