// D5-C10 isolated Unity 2022.3.62f2 macOS arm64 IL2CPP build ENTRY.
// SOURCE ONLY until a separately authorized Local Validation Agent executes
// Unity. This is NOT the old R03/B1 build entry, and does not update it.
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using HybridCLR.Editor.Commands;
using HybridCLR.Editor.Installer;
using HybridCLR.Editor.Settings;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace AssemblyShadow.R03.D5.Editor
{
    [Serializable]
    public sealed class D5BuildConfig
    {
        public int schemaVersion;
        public string projectPath, outputPath, receiptPath;
        public string overlayPath, overlaySha256;
        public string managedFixtureSha256;
        public string sourcePinsSha256;
        public string expectedNativeCommit;
        public string expectedDemoCommit;
        public bool featureEnabled;
        public string cppConfiguration;
        public int diagnosticsLevel;
    }

    [Serializable]
    public sealed class D5NativeFile
    {
        public string path, sha256;
    }

    [Serializable]
    public sealed class D5BuildReceipt
    {
        public int schemaVersion = 1;
        public string kind = "R03D5C10IsolatedUnityBuildV1";
        public string result = "NotRun";
        public string unityVersion, platform, architecture, projectPath, outputPath;
        public string cppConfiguration, compilerFlags, sourcePinsSha256;
        public string nativeCommit, demoCommit;
        public string overlaySourceSha256, overlayInstalledSha256, managedFixtureSha256;
        public bool featureEnabled;
        public int buildErrors = -1, buildWarnings = -1;
        public string buildPipelineResult, exceptionType;
        public D5NativeFile[] requiredNativeFileHashes;
        public bool actualUnityBuildPipelineInvoked;
        public bool actualUnityBuildReportSucceeded;
        public bool independentLinkedBinaryProof = false;
        public bool actualD5PlayerRun = false;
        public bool R03Accepted = false;
    }

    public static class R03D5Build
    {
        private static readonly string[] RequiredNativeFiles =
        {
            "vm/AssemblyShadow.cpp",
            "vm/AssemblyShadow.h",
            "vm/AssemblyShadowD5WindowProbe.h",
            "vm/AssemblyShadowProcessSnapshotOwner.h",
            "vm/AssemblyShadowPublicationPhaseReceipt.h",
            "vm/AssemblyShadowPublicationD3Decision.h",
            "vm/AssemblyShadowFirstFailureV2.h",
            "vm/AssemblyShadowTerminalExecution.h",
            "vm/AssemblyShadowTypes.h",
            "vm/Assembly.cpp",
            "vm/MetadataCache.cpp",
            "vm/Runtime.cpp",
            "utils/dynamic_array.h"
        };

        public static void Build()
        {
            string configPath = Arg("-r03D5BuildConfig");
            if (string.IsNullOrEmpty(configPath) || !File.Exists(configPath))
                throw new BuildFailedException("D5 isolated config missing");
            var config = JsonUtility.FromJson<D5BuildConfig>(
                File.ReadAllText(configPath, Encoding.UTF8));
            string project = Path.GetFullPath(SettingsUtil.ProjectDir);
            if (config == null || config.schemaVersion != 1 ||
                project != Path.GetFullPath(config.projectPath) ||
                !File.Exists(Path.Combine(project, ".r03-d5-isolated-project")))
                throw new BuildFailedException("Only a new isolated D5 project may build");
            if (Application.unityVersion != "2022.3.62f2" ||
                EditorUserBuildSettings.activeBuildTarget != BuildTarget.StandaloneOSX)
                throw new BuildFailedException("D5 must use Unity 2022.3.62f2 StandaloneOSX");
            // This build entry is source-pinned to its reviewed D5 C10
            // native candidate. The demo head is additionally bound by the
            // future independent Local handoff, not by this self-reported field.
            if (config.expectedNativeCommit !=
                    "84f9435628b8ff4cc675409f6b4d76dd2753d8a8" ||
                string.IsNullOrEmpty(config.expectedDemoCommit) ||
                config.expectedDemoCommit.Length != 40)
                throw new BuildFailedException("D5 source revision is not the reviewed candidate");
            if (config.diagnosticsLevel != 2 ||
                (config.cppConfiguration != "Release" && config.cppConfiguration != "Debug") ||
                !File.Exists(config.overlayPath) || File.Exists(config.receiptPath) ||
                File.Exists(config.outputPath) || Directory.Exists(config.outputPath))
                throw new BuildFailedException("D5 build parameters or exclusive outputs invalid");
            string manifestPath = Path.Combine(project, "ProjectSettings", "AssemblyShadowSourcePins.json");
            string managedSource = Path.Combine(project, "Assets", "R03D5P5WindowPlayer.cs");
            if (!File.Exists(manifestPath) || !File.Exists(managedSource) ||
                !string.Equals(Sha(manifestPath), config.sourcePinsSha256,
                    StringComparison.OrdinalIgnoreCase) ||
                !string.Equals(Sha(managedSource), config.managedFixtureSha256,
                    StringComparison.OrdinalIgnoreCase) ||
                !string.Equals(Sha(config.overlayPath), config.overlaySha256,
                    StringComparison.OrdinalIgnoreCase))
                throw new BuildFailedException("D5 source manifest/fixture digest mismatch");

            var receipt = new D5BuildReceipt
            {
                unityVersion = Application.unityVersion,
                platform = "StandaloneOSX", architecture = "arm64",
                projectPath = project, outputPath = Path.GetFullPath(config.outputPath),
                cppConfiguration = config.cppConfiguration,
                featureEnabled = config.featureEnabled,
                sourcePinsSha256 = config.sourcePinsSha256,
                managedFixtureSha256 = config.managedFixtureSha256,
                overlaySourceSha256 = config.overlaySha256,
                nativeCommit = config.expectedNativeCommit,
                demoCommit = config.expectedDemoCommit
            };
            try
            {
                Configure(config);
                // Versioned upstream installation: cloned source commits are
                // verified by PinnedSourceInstaller and the future D5-B gate.
                PinnedSourceInstaller.Install();
                string native = Path.Combine(SettingsUtil.LocalIl2CppDir, "libil2cpp");
                string overlayDestination = Path.Combine(native, "vm", "AssemblyShadowD5WindowOverlay.cpp");
                if (File.Exists(overlayDestination))
                    throw new BuildFailedException("Unexpected previous D5 native probe");
                File.Copy(config.overlayPath, overlayDestination, false);
                receipt.overlayInstalledSha256 = Sha(overlayDestination);
                if (!string.Equals(receipt.overlayInstalledSha256,config.overlaySha256,
                    StringComparison.OrdinalIgnoreCase))
                    throw new BuildFailedException("D5 probe install bytes changed");

                var files = new List<D5NativeFile>();
                foreach (string name in RequiredNativeFiles)
                {
                    string installed = Path.Combine(native, name.Replace('/', Path.DirectorySeparatorChar));
                    if (!File.Exists(installed))
                        throw new BuildFailedException("Missing native D5 source " + name);
                    files.Add(new D5NativeFile { path = name, sha256 = Sha(installed) });
                }
                receipt.requiredNativeFileHashes = files.ToArray();
                // Copy/reviewed source is NOT proof that Bee actually compiled
                // the native core. CI and an independent linker audit are later.
                PrebuildCommand.GenerateAll();
                receipt.compilerFlags = PlayerSettings.GetAdditionalIl2CppArgs();
                receipt.actualUnityBuildPipelineInvoked = true;
                BuildReport report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
                {
                    scenes = new[] { "Assets/R03D5.unity" },
                    locationPathName = config.outputPath,
                    target = BuildTarget.StandaloneOSX,
                    targetGroup = BuildTargetGroup.Standalone,
                    options = BuildOptions.Development | BuildOptions.DetailedBuildReport
                });
                receipt.buildPipelineResult = report.summary.result.ToString();
                receipt.buildErrors = report.summary.totalErrors;
                receipt.buildWarnings = report.summary.totalWarnings;
                receipt.actualUnityBuildReportSucceeded =
                    report.summary.result == BuildResult.Succeeded &&
                    report.summary.totalErrors == 0;
                receipt.result = receipt.actualUnityBuildReportSucceeded ?
                    "BuildPipelineSucceeded_NotYetBinaryVerified" :
                    "BuildPipelineFailed";
                if (!receipt.actualUnityBuildReportSucceeded)
                    throw new BuildFailedException("D5 native Unity BuildPipeline failed");
            }
            catch (Exception error)
            {
                receipt.exceptionType = error.GetType().FullName;
                if (receipt.result == "NotRun") receipt.result = "FailedDuringUnityBuildPreparation";
                throw;
            }
            finally
            {
                // Exclusive receipt (never overwrite a prior evidence attempt).
                using (var stream = new FileStream(config.receiptPath,
                    FileMode.CreateNew, FileAccess.Write, FileShare.None))
                using (var writer = new StreamWriter(stream, new UTF8Encoding(false)))
                    writer.Write(JsonUtility.ToJson(receipt, true));
            }
        }

        private static void Configure(D5BuildConfig config)
        {
            var target = UnityEditor.Build.NamedBuildTarget.Standalone;
            PlayerSettings.SetScriptingBackend(target, ScriptingImplementation.IL2CPP);
            PlayerSettings.SetArchitecture(target, 1);
#if UNITY_EDITOR_OSX
            UnityEditor.OSXStandalone.UserBuildSettings.architecture = OSArchitecture.ARM64;
#endif
            PlayerSettings.SetIl2CppCompilerConfiguration(target,
                config.cppConfiguration == "Debug" ?
                    Il2CppCompilerConfiguration.Debug : Il2CppCompilerConfiguration.Release);
            PlayerSettings.SetManagedStrippingLevel(target, ManagedStrippingLevel.Low);
            PlayerSettings.SetApiCompatibilityLevel(target, ApiCompatibilityLevel.NET_Standard);
            var args = "--compiler-flags=\"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=" +
                (config.featureEnabled ? "1" : "0") +
                " -DHYBRIDCLR_ASSEMBLY_SHADOW_DIAGNOSTICS_LEVEL=2" +
                " -DHYBRIDCLR_R03_RUNTIME_PROBE=1" +
                " -DHYBRIDCLR_R03_D5_WINDOW_PROBE=" + (config.featureEnabled ? "1" : "0") +
                " -DHYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE=" + (config.featureEnabled ? "1" : "0") + "\"";
            PlayerSettings.SetAdditionalIl2CppArgs(args);
            EditorUserBuildSettings.development = true;
            EditorUserBuildSettings.allowDebugging = false;
            EditorUserBuildSettings.connectProfiler = false;
            PlayerSettings.companyName = "AssemblyShadowD5";
            PlayerSettings.productName = "R03D5Isolated";
            PlayerSettings.runInBackground = true;
            var settings = HybridCLRSettings.Instance;
            settings.enable = true;
            settings.useGlobalIl2cpp = false;
            settings.hotUpdateAssemblyDefinitions =
                Array.Empty<UnityEditorInternal.AssemblyDefinitionAsset>();
            settings.hotUpdateAssemblies = Array.Empty<string>();
            settings.preserveHotUpdateAssemblies = Array.Empty<string>();
            settings.patchAOTAssemblies = Array.Empty<string>();
            HybridCLRSettings.Save();
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            EditorSceneManager.SaveScene(scene, "Assets/R03D5.unity");
            EditorBuildSettings.scenes = new[] {
                new EditorBuildSettingsScene("Assets/R03D5.unity", true)
            };
            AssetDatabase.SaveAssets();
        }

        private static string Arg(string key)
        {
            var args = Environment.GetCommandLineArgs();
            for (int i = 0; i + 1 < args.Length; ++i)
                if (args[i] == key) return args[i+1];
            return null;
        }

        private static string Sha(string path)
        {
            using (var hash = SHA256.Create())
            using (var stream = File.OpenRead(path))
                return BitConverter.ToString(hash.ComputeHash(stream)).
                    Replace("-", "").ToLowerInvariant();
        }
    }
}
