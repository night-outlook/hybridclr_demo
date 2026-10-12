using System;
using System.Collections.Generic;
using System.Collections;
using System.Reflection;
using System.Threading;
using System.IO;
using System.Linq;
using HybridCLR.Editor;
using HybridCLR.Editor.AssemblyShadow;
using HybridCLR.Editor.Commands;
using HybridCLR.Editor.Installer;
using HybridCLR.Editor.Settings;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace AssemblyShadow.R03.Editor
{
    [Serializable] public sealed class BuildConfig
    {
        public int schemaVersion;
        public string projectPath;
        public string outputPath;
        public string receiptPath;
        public string overlayPath;
        public string overlaySha256;
        public string sourceManifestSha256;
        public bool featureEnabled;
        public int diagnosticsLevel;
        public string cppConfiguration;
    }
    [Serializable] public sealed class FileHash { public string path; public string sha256; public long size; }
    [Serializable] public sealed class BuildReceipt
    {
        public int schemaVersion = 2;
        public string kind = "R03IsolatedPlayerBuild";
        public string result;
        public string unityVersion;
        public string target;
        public string architecture;
        public string cppConfiguration;
        public bool featureEnabled;
        public int diagnosticsLevel;
        public string nativeArguments;
        public string projectPath;
        public string outputPath;
        public string sourceManifestSha256;
        public string installReceiptSha256;
        public string installedNativeRoot;
        public string testOverlaySha256;
        public bool nonGeneratedCorePreserved;
        public int errors;
        public int warnings;
        public FileHash[] installedBefore;
        public FileHash[] installedAfter;
        public FileHash[] playerFiles;
        public FileHash[] linkedDlls;
        public string exception;
        public string beeObservationStatus, beeObservationPath, beeObservationSha256;
        public bool runtimeAcceptance = false;
    }

    public static class R03Build
    {
        private static readonly string[] Generated = {
            "hybridclr/generated/AssemblyManifest.cpp", "hybridclr/generated/MethodBridge.cpp",
            "hybridclr/generated/UnityVersion.h", "hybridclr/generated/libil2cpp-version.txt" };

        public static void Build()
        {
            string configPath = Argument("-r03Config");
            var config = JsonUtility.FromJson<BuildConfig>(File.ReadAllText(configPath));
            string project = Path.GetFullPath(SettingsUtil.ProjectDir);
            if (config == null || config.schemaVersion != 1 || Path.GetFullPath(config.projectPath) != project ||
                !File.Exists(Path.Combine(project, ".r03-isolated-project")))
                throw new BuildFailedException("Only the batch-created isolated R03 project may run this build.");
            if (Application.unityVersion != "2022.3.62f2" || EditorUserBuildSettings.activeBuildTarget != BuildTarget.StandaloneOSX)
                throw new BuildFailedException("This first R03 native batch is pinned to Unity 2022.3.62f2 macOS ARM64.");
            if (File.Exists(config.receiptPath) || Directory.Exists(config.outputPath) || File.Exists(config.outputPath))
                throw new BuildFailedException("Build output and receipt paths must be unused.");
            if (ShadowHash.File(Path.Combine(project, "source-inputs.json")) != config.sourceManifestSha256 ||
                ShadowHash.File(config.overlayPath) != config.overlaySha256)
                throw new BuildFailedException("Source manifest or additive diagnostic source changed.");
            var receipt = new BuildReceipt { unityVersion = Application.unityVersion, target = BuildTarget.StandaloneOSX.ToString(),
                architecture = "arm64", projectPath = project, outputPath = Path.GetFullPath(config.outputPath),
                sourceManifestSha256 = config.sourceManifestSha256, testOverlaySha256 = config.overlaySha256,
                featureEnabled = config.featureEnabled, diagnosticsLevel = config.diagnosticsLevel,
                cppConfiguration = config.cppConfiguration, result = "Failed" };
            R03BeeObservation observation = null;
            BuildReport actualReport = null;
            try
            {
                Configure(config);
                PinnedSourceInstaller.Install();
                string native = Path.GetFullPath(Path.Combine(SettingsUtil.LocalIl2CppDir, "libil2cpp"));
                receipt.installedNativeRoot = native;
                string installReceipt = Path.Combine(native, "assembly-shadow-install.json");
                receipt.installReceiptSha256 = ShadowHash.File(installReceipt);
                receipt.installedBefore = Inventory(native);
                string probe = Path.Combine(native, "vm", "AssemblyShadowR03Probe.cpp");
                if (File.Exists(probe)) throw new BuildFailedException("Unexpected pre-existing diagnostic source.");
                File.Copy(config.overlayPath, probe, false);
                // All fixture DLLs remain AOT Player inputs. The ordinary
                // hot-update filter stays empty: no role promotion is involved.
                // This suite adds no native signatures beyond those in the
                // preserved baseline and fixed diagnostic bootstrap.
                PrebuildCommand.GenerateAll();
                receipt.nativeArguments = PlayerSettings.GetAdditionalIl2CppArgs();
                observation = new R03BeeObservation(config, project);
                var report = actualReport = BuildPipeline.BuildPlayer(new BuildPlayerOptions
                {
                    scenes = new[] { "Assets/R03.unity" }, locationPathName = config.outputPath,
                    target = BuildTarget.StandaloneOSX, targetGroup = BuildTargetGroup.Standalone,
                    options = BuildOptions.Development | BuildOptions.DetailedBuildReport,
                });
                receipt.errors = report.summary.totalErrors; receipt.warnings = report.summary.totalWarnings;
                receipt.installedAfter = Inventory(native);
                VerifyCore(receipt.installedBefore, receipt.installedAfter);
                if (ShadowHash.File(installReceipt) != receipt.installReceiptSha256 || ShadowHash.File(probe) != config.overlaySha256)
                    throw new BuildFailedException("The source installation receipt or test overlay changed during build.");
                receipt.nonGeneratedCorePreserved = true;
                receipt.playerFiles = Inventory(config.outputPath);
                string linked = SettingsUtil.GetAssembliesPostIl2CppStripDir(BuildTarget.StandaloneOSX);
                receipt.linkedDlls = Directory.Exists(linked) ? Inventory(linked) : new FileHash[0];
                if (report.summary.result != BuildResult.Succeeded || report.summary.totalErrors != 0 || receipt.playerFiles.Length == 0)
                    throw new BuildFailedException("Actual IL2CPP Player build did not succeed.");
                receipt.result = "Passed";
            }
            catch (Exception error) { receipt.exception = error.ToString(); throw; }
            finally
            {
                if (observation != null)
                {
                    // This observes only. It never replaces/suppresses a result
                    // processor or changes BuildReport/error admission.
                    try
                    {
                        receipt.beeObservationPath = observation.Save(actualReport);
                        receipt.beeObservationSha256 = ShadowHash.File(receipt.beeObservationPath);
                        receipt.beeObservationStatus = "RecordedForAnalysis";
                    }
                    catch (Exception diagnosticError) { receipt.beeObservationStatus = "Unavailable:" + diagnosticError.GetType().FullName; }
                    finally { observation.Dispose(); }
                }
                Directory.CreateDirectory(Path.GetDirectoryName(config.receiptPath));
                using (var stream = new FileStream(config.receiptPath, FileMode.CreateNew))
                using (var writer = new StreamWriter(stream)) writer.Write(JsonUtility.ToJson(receipt, true) + "\n");
            }
        }

        private static void Configure(BuildConfig config)
        {
            Il2CppCompilerConfiguration cpp;
            if (!Enum.TryParse(config.cppConfiguration, out cpp) ||
                (cpp != Il2CppCompilerConfiguration.Debug && cpp != Il2CppCompilerConfiguration.Release))
                throw new BuildFailedException("Explicit C++ Debug or Release is required.");
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Standalone, ScriptingImplementation.IL2CPP);
            PlayerSettings.SetArchitecture(NamedBuildTarget.Standalone, 1);
#if UNITY_EDITOR_OSX
            UnityEditor.OSXStandalone.UserBuildSettings.architecture = OSArchitecture.ARM64;
#endif
            PlayerSettings.SetIl2CppCompilerConfiguration(NamedBuildTarget.Standalone, cpp);
            PlayerSettings.SetManagedStrippingLevel(NamedBuildTarget.Standalone, ManagedStrippingLevel.Low);
            PlayerSettings.SetApiCompatibilityLevel(NamedBuildTarget.Standalone, ApiCompatibilityLevel.NET_Standard);
            PlayerSettings.SetAdditionalIl2CppArgs("--compiler-flags=\"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=" +
                (config.featureEnabled ? "1" : "0") + " -DHYBRIDCLR_ASSEMBLY_SHADOW_DIAGNOSTICS_LEVEL=" + config.diagnosticsLevel + " -DHYBRIDCLR_R03_RUNTIME_PROBE=1\"");
            EditorUserBuildSettings.development = true;
            EditorUserBuildSettings.allowDebugging = false;
            EditorUserBuildSettings.connectProfiler = false;
            PlayerSettings.companyName = "AssemblyShadowLab"; PlayerSettings.productName = "R03Isolated";
            PlayerSettings.runInBackground = true;
            var settings = HybridCLRSettings.Instance;
            settings.enable = true; settings.useGlobalIl2cpp = false;
            settings.hotUpdateAssemblyDefinitions = Array.Empty<UnityEditorInternal.AssemblyDefinitionAsset>();
            settings.hotUpdateAssemblies = Array.Empty<string>();
            settings.preserveHotUpdateAssemblies = Array.Empty<string>();
            settings.patchAOTAssemblies = Array.Empty<string>();
            HybridCLRSettings.Save();
            // Use the existing direct-runtime fixture build model, not the
            // production deployment builder. Invalid patches are deliberate
            // inputs to the native admission tests, never deployable artifacts.
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            EditorSceneManager.SaveScene(scene, "Assets/R03.unity");
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene("Assets/R03.unity", true) };
            AssetDatabase.SaveAssets();
        }
        private static FileHash[] Inventory(string root)
        {
            root = Path.GetFullPath(root);
            return Directory.GetFiles(root, "*", SearchOption.AllDirectories).OrderBy(p => p, StringComparer.Ordinal)
                .Select(p => new FileHash { path = p.Substring(root.Length).TrimStart(Path.DirectorySeparatorChar).Replace('\\', '/'),
                    sha256 = ShadowHash.File(p), size = new FileInfo(p).Length }).ToArray();
        }
        private static void VerifyCore(FileHash[] before, FileHash[] after)
        {
            var old = before.ToDictionary(x => x.path, StringComparer.Ordinal);
            var current = after.ToDictionary(x => x.path, StringComparer.Ordinal);
            foreach (var pair in old)
            {
                if (Generated.Contains(pair.Key)) continue;
                FileHash value;
                if (!current.TryGetValue(pair.Key, out value) || value.sha256 != pair.Value.sha256)
                    throw new BuildFailedException("Non-generated installed source changed: " + pair.Key);
            }
            foreach (string path in current.Keys.Except(old.Keys))
                if (!Generated.Contains(path) && path != "vm/AssemblyShadowR03Probe.cpp")
                    throw new BuildFailedException("Unexplained installed source addition: " + path);
        }
        private static string Argument(string key)
        {
            var args = Environment.GetCommandLineArgs();
            for (int i = 0; i + 1 < args.Length; ++i) if (args[i] == key) return Path.GetFullPath(args[i + 1]);
            throw new ArgumentException("Missing " + key);
        }
    }

    // K observational instrumentation. No detours or result-processor replacement.
    internal sealed class R03BeeObservation : IDisposable
    {
        [Serializable] private sealed class Message { public string utc, text, stack; public int thread; }
        [Serializable] private sealed class Node
        { public string annotation, outputFile, outputDirectory, output; public int exitCode; }
        [Serializable] private sealed class Observation
        {
            public int schemaVersion = 1;
            public string kind = "R03BeeResultObservationV1", result = "Unavailable";
            public string project, sourceManifestSha256, utcStart, utcEnd, processorType, processorAssemblySha256, error;
            public bool sameProcessor, driverInitiallyAbsent, limitsExceeded, runtimeAcceptance = false;
            public int buildErrors = -1, buildWarnings = -1;
            public Message[] messages;
            public Node[] nodes;
        }
        private readonly BuildConfig config;
        private readonly Observation data = new Observation();
        private readonly List<Message> messages = new List<Message>();
        private readonly object sync = new object();
        private readonly object initialProcessor, initialDriver;
        private bool disposed, saved;

        public R03BeeObservation(BuildConfig config, string project)
        {
            this.config = config;
            data.project = project; data.sourceManifestSha256 = config.sourceManifestSha256;
            data.utcStart = DateTime.UtcNow.ToString("o");
            try { initialProcessor = Processor(); initialDriver = Read(initialProcessor, "BeeDriverResult"); }
            catch (Exception e) { data.error = "Before:" + e.GetType().FullName; }
            Application.logMessageReceivedThreaded += OnLog;
        }
        private void OnLog(string condition, string stack, LogType type)
        {
            if (condition == null || condition.IndexOf("failed to allocate space to load shared cache", StringComparison.Ordinal) < 0) return;
            lock (sync)
            {
                if (disposed) return;
                if (messages.Count >= 32 || condition.Length > 65536 || (stack != null && stack.Length > 65536))
                { data.limitsExceeded = true; return; }
                messages.Add(new Message { utc = DateTime.UtcNow.ToString("o"), text = condition,
                    stack = stack, thread = Thread.CurrentThread.ManagedThreadId });
            }
        }
        private static object Read(object target, string name)
        {
            if (target == null) return null;
            for (Type t = target.GetType(); t != null; t = t.BaseType)
            {
                const BindingFlags flags = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;
                FieldInfo f = t.GetField(name, flags); if (f != null) return f.GetValue(target);
                PropertyInfo p = t.GetProperty(name, flags); if (p != null && p.GetIndexParameters().Length == 0) return p.GetValue(target, null);
            }
            return null;
        }
        private static object Processor()
        {
            Type module = typeof(BuildPipeline).Assembly.GetType("UnityEditor.Modules.ModuleManager", true);
            MethodInfo method = module.GetMethod("GetBuildPostProcessor", BindingFlags.Static | BindingFlags.NonPublic,
                null, new[] { typeof(BuildTargetGroup), typeof(BuildTarget) }, null);
            if (method == null) throw new MissingMethodException("GetBuildPostProcessor");
            return method.Invoke(null, new object[] { BuildTargetGroup.Standalone, BuildTarget.StandaloneOSX });
        }
        public string Save(BuildReport report)
        {
            if (saved) throw new InvalidOperationException("Single-use Bee observation");
            saved = true;
            Dispose(); // Freeze callbacks before reading/serializing the snapshot.
            data.utcEnd = DateTime.UtcNow.ToString("o");
            if (report != null) { data.buildErrors = report.summary.totalErrors; data.buildWarnings = report.summary.totalWarnings; }
            var rows = new List<Node>(); long bytes = 0;
            try
            {
                object processor = Processor();
                data.sameProcessor = ReferenceEquals(initialProcessor, processor) && processor != null;
                data.driverInitiallyAbsent = initialDriver == null;
                data.processorType = processor == null ? null : processor.GetType().FullName;
                if (processor != null) data.processorAssemblySha256 = ShadowHash.File(processor.GetType().Assembly.Location);
                object driver = Read(processor, "BeeDriverResult");
                if (!data.sameProcessor || !data.driverInitiallyAbsent || driver == null)
                    throw new InvalidOperationException("Current build driver identity unavailable");
                var nodes = Read(driver, "NodeFinishedMessages") as IEnumerable;
                if (nodes == null) throw new InvalidOperationException("NodeFinishedMessages unavailable");
                foreach (object message in nodes)
                {
                    object node = Read(message, "Node");
                    string output = Read(message, "Output") as string;
                    bytes += output == null ? 0 : output.Length;
                    if (rows.Count >= 4096 || bytes > 16777216) { data.limitsExceeded = true; break; }
                    object code = Read(message, "ExitCode");
                    if (!(code is int)) throw new InvalidOperationException("Native result ExitCode unavailable");
                    rows.Add(new Node { annotation = Read(node, "Annotation") as string,
                        outputFile = Read(node, "OutputFile") as string,
                        outputDirectory = Read(node, "OutputDirectory") as string,
                        output = output, exitCode = (int)code });
                }
                if (rows.Count > 0 && !data.limitsExceeded) data.result = "CapturedForAnalysis";
            }
            catch (Exception e) { data.error = (data.error ?? "") + ";After:" + e.GetType().FullName + ":" + e.Message; }
            data.nodes = rows.ToArray(); lock (sync) data.messages = messages.ToArray();
            string path = Path.Combine(Path.GetDirectoryName(config.receiptPath), "bee-result-observation.json");
            using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(stream, new System.Text.UTF8Encoding(false)))
                writer.Write(JsonUtility.ToJson(data, true) + "\n");
            return path;
        }
        public void Dispose()
        {
            lock (sync)
            {
                if (disposed) return;
                Application.logMessageReceivedThreaded -= OnLog; disposed = true;
            }
        }
    }

}
