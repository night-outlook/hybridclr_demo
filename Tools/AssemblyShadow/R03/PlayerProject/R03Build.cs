using System;
using System.Collections.Generic;
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
        public string diagnosticStatus, diagnosticReceiptSha256;
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
            R03BuildCapture capture = null;
            BuildReport actualReport = null;
            try
            {
                capture = new R03BuildCapture(Path.GetDirectoryName(config.receiptPath));
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
                var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
                {
                    scenes = new[] { "Assets/R03.unity" }, locationPathName = config.outputPath,
                    target = BuildTarget.StandaloneOSX, targetGroup = BuildTargetGroup.Standalone,
                    options = BuildOptions.Development | BuildOptions.DetailedBuildReport,
                });
                actualReport = report;
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
                if (capture != null)
                {
                    try
                    {
                        string diagnostic = capture.Finish(actualReport);
                        receipt.diagnosticReceiptSha256 = ShadowHash.File(diagnostic);
                        receipt.diagnosticStatus = "Recorded";
                    }
                    catch (Exception diagnosticError)
                    {
                        // Do not replace a real BuildReport failure or hide it.
                        receipt.diagnosticStatus = "Failed: " + diagnosticError.GetType().FullName;
                    }
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
}

namespace AssemblyShadow.R03.Editor
{
    // Observation only. Never replace processors, alter their output or change
    // BuildReport acceptance. Each build keeps an independent, bounded record.
    internal sealed class R03BuildCapture
    {
        [Serializable] private sealed class EventRow
        {
            public string utc, type, message, stack;
            public int managedThread;
            public long sequence;
        }
        [Serializable] private sealed class StepRow
        { public int index, depth; public string name; public EventRow[] messages; }
        [Serializable] private sealed class NodeRow
        {
            public string annotation, outputFile, outputDirectory, output;
            public int exitCode;
        }
        [Serializable] private sealed class Snapshot
        {
            public string kind = "R03BuildResultCaptureV1", state, unityVersion, eventSha256, error;
            public string editorAssembly, editorAssemblySha256, editorAssemblyMvid;
            public string liveBeeState = "Unavailable", liveBeeReason;
            public bool runtimeAcceptance = false, eventOverflow, reportReturned;
            public int events, droppedEvents;
            public StepRow[] steps;
            public NodeRow[] liveBeeNodes;
        }
        private readonly object sync = new object();
        private readonly string root, eventPath;
        private StreamWriter writer;
        private bool active = true;
        private int events, dropped;
        private long eventCharacters;
        private string captureError;
        private const int MaxEvents = 8192, MaxCharacters = 16 * 1024 * 1024;
        public R03BuildCapture(string root)
        {
            this.root = Path.GetFullPath(root);
            eventPath = Path.Combine(this.root, "build-events.jsonl");
            writer = new StreamWriter(new FileStream(eventPath, FileMode.CreateNew, FileAccess.Write, FileShare.Read),
                new System.Text.UTF8Encoding(false));
            writer.AutoFlush = true;
            Application.logMessageReceivedThreaded += OnLog;
        }
        private static string Quote(string value)
        {
            if (value == null) return "null";
            var b = new System.Text.StringBuilder(value.Length + 8); b.Append('"');
            foreach (char c in value)
            {
                if (c == '"' || c == '\\') { b.Append('\\'); b.Append(c); }
                else if (c < 32 || char.IsSurrogate(c)) b.Append("\\u" + ((int)c).ToString("x4"));
                else b.Append(c);
            }
            return b.Append('"').ToString();
        }
        private void OnLog(string message, string stack, LogType type)
        {
            if (type == LogType.Log) return;
            lock (sync)
            {
                if (!active) return;
                try
                {
                    long chars = (message == null ? 0 : message.Length) + (stack == null ? 0 : stack.Length);
                    if (events >= MaxEvents || chars > 1024 * 1024 || eventCharacters + chars > MaxCharacters)
                    { ++dropped; return; }
                    ++events; eventCharacters += chars;
                    // Do not call Unity logging or JsonUtility from its log callback.
                    writer.WriteLine("{\"utc\":" + Quote(DateTime.UtcNow.ToString("O")) +
                        ",\"sequence\":" + events + ",\"managedThread\":" +
                        System.Threading.Thread.CurrentThread.ManagedThreadId + ",\"type\":" + Quote(type.ToString()) +
                        ",\"message\":" + Quote(message) + ",\"stack\":" + Quote(stack) + "}");
                }
                catch (Exception e) { captureError = e.GetType().FullName; }
            }
        }
        private static object ReadMember(object obj, string name)
        {
            if (obj == null) return null;
            var flags = System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public |
                System.Reflection.BindingFlags.NonPublic;
            for (Type type = obj.GetType(); type != null; type = type.BaseType)
            {
                var field = type.GetField(name, flags | System.Reflection.BindingFlags.DeclaredOnly);
                if (field != null) return field.GetValue(obj);
                var property = type.GetProperty(name, flags | System.Reflection.BindingFlags.DeclaredOnly);
                if (property != null && property.GetIndexParameters().Length == 0) return property.GetValue(obj, null);
            }
            return null;
        }
        private static string TextMember(object obj, string name)
        { return ReadMember(obj, name) as string; }
        private static object FindRetainedBeeResult()
        {
            // Inspect only already registered modules and their immediate fields.
            // Never call CreateBuildPostprocessor (which could make a new instance).
            var manager = typeof(UnityEditor.Editor).Assembly.GetType("UnityEditor.Modules.ModuleManager");
            var field = manager == null ? null : manager.GetField("s_PlatformModules",
                System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic);
            var modules = field == null ? null : field.GetValue(null) as System.Collections.IDictionary;
            if (modules == null) return null;
            int visited = 0;
            foreach (object module in modules.Values)
            {
                if (module == null) continue;
                for (Type type = module.GetType(); type != null; type = type.BaseType)
                    foreach (var f in type.GetFields(System.Reflection.BindingFlags.Instance |
                        System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic |
                        System.Reflection.BindingFlags.DeclaredOnly))
                    {
                        if (++visited > 512) return null;
                        object candidate = f.GetValue(module);
                        if (candidate == null) continue;
                        bool isProcessor = false;
                        for (Type t = candidate.GetType(); t != null; t = t.BaseType)
                            if (t.FullName == "UnityEditor.Modules.BeeBuildPostprocessor") isProcessor = true;
                        if (isProcessor)
                        {
                            object result = ReadMember(candidate, "BeeDriverResult");
                            if (result != null) return result;
                        }
                    }
            }
            return null;
        }
        public string Finish(BuildReport report)
        {
            Application.logMessageReceivedThreaded -= OnLog;
            lock (sync) { active = false; writer.Flush(); writer.Dispose(); writer = null; }
            var snapshot = new Snapshot { unityVersion = Application.unityVersion,
                state = captureError == null && dropped == 0 ? "Recorded" : "Incomplete",
                error = captureError, events = events, droppedEvents = dropped, eventOverflow = dropped != 0,
                eventSha256 = ShadowHash.File(eventPath), reportReturned = report != null };
            var editor = typeof(UnityEditor.Editor).Assembly;
            snapshot.editorAssembly = editor.Location;
            snapshot.editorAssemblyMvid = editor.ManifestModule.ModuleVersionId.ToString();
            snapshot.editorAssemblySha256 = ShadowHash.File(editor.Location);
            var steps = new List<StepRow>();
            int messageCount = 0;
            if (report != null)
                foreach (var step in report.steps)
                {
                    if (steps.Count >= 4096) throw new InvalidOperationException("Build step capture bound");
                    var messages = new List<EventRow>();
                    foreach (var message in step.messages)
                    {
                        if (++messageCount > 32768) throw new InvalidOperationException("Build message capture bound");
                        messages.Add(new EventRow { type = message.type.ToString(), message = message.content });
                    }
                    steps.Add(new StepRow { index = steps.Count, depth = step.depth, name = step.name,
                        messages = messages.ToArray() });
                }
            snapshot.steps = steps.ToArray();
            var nodes = new List<NodeRow>();
            try
            {
                object bee = FindRetainedBeeResult();
                var source = ReadMember(bee, "NodeFinishedMessages") as System.Collections.IEnumerable;
                if (source == null) snapshot.liveBeeReason = "No retained processor/result instance; do not infer node output from disk logs";
                else
                {
                    long chars = 0;
                    foreach (object node in source)
                    {
                        string output = TextMember(node, "Output"); chars += output == null ? 0 : output.Length;
                        if (nodes.Count >= 4096 || chars > MaxCharacters) throw new InvalidOperationException("Live node capture bound");
                        object descriptor = ReadMember(node, "Node");
                        nodes.Add(new NodeRow { output = output, exitCode = Convert.ToInt32(ReadMember(node, "ExitCode")),
                            annotation = TextMember(descriptor, "Annotation"), outputFile = TextMember(descriptor, "OutputFile"),
                            outputDirectory = TextMember(descriptor, "OutputDirectory") });
                    }
                    snapshot.liveBeeState = "CapturedCurrentProcess";
                }
            }
            catch (Exception e) { snapshot.liveBeeState = "Unavailable"; snapshot.liveBeeReason = e.GetType().FullName; }
            snapshot.liveBeeNodes = nodes.ToArray();
            string path = Path.Combine(root, "build-result-capture.json");
            using (var f = new FileStream(path, FileMode.CreateNew))
            using (var w = new StreamWriter(f, new System.Text.UTF8Encoding(false)))
                w.Write(JsonUtility.ToJson(snapshot, true) + "\n");
            return path;
        }
    }
}
