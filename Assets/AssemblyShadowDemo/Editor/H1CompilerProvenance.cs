using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor.Build;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>
    /// Captures the immutable native action graph emitted by Bee for one fresh
    /// H1 Player build.  Settings and Unity logs are intent evidence only; this
    /// class accepts a receipt only when the graph contains the actual compiler
    /// and linker actions producing the selected GameAssembly.
    /// </summary>
    public static class H1CompilerProvenance
    {
        private const int SchemaVersion = 1;
        private const string CompilerActionPrefix = "C_Mac_arm64";
        private const string LinkActionPrefix = "Link_Mac_arm64";
        private const string Il2CppConfigRelativePath =
            "HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp/il2cpp-config.h";

        [Serializable]
        public sealed class GraphInventory
        {
            public Entry[] entries;
        }

        [Serializable]
        public sealed class Entry
        {
            public string path, sha256;
        }

        [Serializable]
        public sealed class Capture
        {
            public int schemaVersion;
            public string buildId, buildGuid, inputSnapshotHash;
            public string nativeLibraryPath, nativeLibrarySha256, sourcePinSha256;
            public string beeActionGraphPath, beeActionGraphSha256;
            public string beeLinkOutputPath;
            public int compileActionCount, linkActionCount;
            public string compilerPath, compilerSha256, compilerVersion;
            public string sdkPath, sdkVersion, sdkSettingsPath, sdkSettingsSha256;
            public string il2cppConfigPath, il2cppConfigSha256;
            public string il2cppDebug, ndebug, il2cppDevelopment;
            public string macroEvidence;
            public ResponseFile[] responseFiles;
        }

        [Serializable]
        public sealed class ResponseFile
        {
            public string sourcePath, retainedPath, sha256;
            public long bytes;
        }

        [Serializable]
        private sealed class BeeGraph
        {
            public BeeNode[] Nodes;
        }

        [Serializable]
        private sealed class BeeNode
        {
            public string Annotation, Action;
            public string[] Inputs, Outputs;
        }

        private static readonly Regex MacroPattern = new Regex(
            @"(?:^|\s)-D(?<name>[A-Za-z_][A-Za-z0-9_]*)(?:=(?<value>[^\s]+))?",
            RegexOptions.Compiled);
        private static readonly Regex SysrootPattern = new Regex(
            @"(?:^|\s)-isysroot\s+(?:""(?<quoted>[^""]+)""|(?<plain>[^\s]+))",
            RegexOptions.Compiled);
        private static readonly Regex ResponsePattern = new Regex(
            @"(?<![A-Za-z0-9_])@(?:""(?<quoted>[^""]+)""|(?<plain>[^\s,]+))",
            RegexOptions.Compiled);

        public static GraphInventory Begin(string projectRoot)
        {
            string beeRoot = Path.Combine(projectRoot, "Library", "Bee");
            if (!Directory.Exists(beeRoot))
                return new GraphInventory { entries = new Entry[0] };
            return new GraphInventory
            {
                entries = Directory.GetFiles(beeRoot, "Player*.dag.json", SearchOption.TopDirectoryOnly)
                    .Where(path => !IsSymlink(path))
                    .Select(path => new Entry { path = Path.GetFullPath(path), sha256 = ShadowHash.File(path) })
                    .OrderBy(item => item.path, StringComparer.Ordinal)
                    .ToArray(),
            };
        }

        public static Capture CaptureAfterBuild(string projectRoot, string output, string buildId,
            string buildGuid, string inputSnapshotHash, string nativeLibraryPath, string nativeLibrarySha256,
            string sourcePinSha256, GraphInventory before, string evidenceRoot,
            out string evidencePath, out string evidenceSha256)
        {
            Require(Path.IsPathRooted(projectRoot) && Directory.Exists(projectRoot), "Project root is missing.");
            Require(Path.IsPathRooted(output) && (Directory.Exists(output) || File.Exists(output)), "Built output is missing.");
            Require(!string.IsNullOrWhiteSpace(buildId) && !string.IsNullOrWhiteSpace(buildGuid), "Build identity is missing.");
            Require(Guid.TryParseExact(buildGuid, "N", out _), "Build GUID is not canonical.");
            Require(!string.IsNullOrWhiteSpace(inputSnapshotHash) && !string.IsNullOrWhiteSpace(nativeLibrarySha256) &&
                !string.IsNullOrWhiteSpace(sourcePinSha256), "Build binding hashes are missing.");
            Require(Path.IsPathRooted(nativeLibraryPath) && File.Exists(nativeLibraryPath), "Native library is missing.");
            Require(ShadowHash.File(nativeLibraryPath) == nativeLibrarySha256, "Native library changed before provenance capture.");
            Require(before != null && before.entries != null, "Bee graph inventory was not captured before the build.");
            Require(Path.IsPathRooted(evidenceRoot) && !File.Exists(evidenceRoot) && !Directory.Exists(evidenceRoot),
                "Native provenance evidence root must be new.");

            string graphPath = SelectChangedGraph(projectRoot, nativeLibraryPath, before);
            byte[] graphBytes = File.ReadAllBytes(graphPath);
            string graphSha = ShadowHash.Bytes(graphBytes);
            var graph = JsonUtility.FromJson<BeeGraph>(new UTF8Encoding(false).GetString(graphBytes));
            Require(graph != null && graph.Nodes != null && graph.Nodes.Length > 0, "Bee action graph is not readable.");

            var compile = graph.Nodes.Where(node => node != null &&
                (node.Annotation ?? "").StartsWith(CompilerActionPrefix, StringComparison.Ordinal) &&
                !string.IsNullOrWhiteSpace(node.Action)).ToArray();
            var link = graph.Nodes.Where(node => node != null &&
                (node.Annotation ?? "").StartsWith(LinkActionPrefix, StringComparison.Ordinal) &&
                !string.IsNullOrWhiteSpace(node.Action)).ToArray();
            Require(compile.Length > 0 && link.Length == 1, "Bee graph does not contain a unique native compile/link action set.");
            Require(link[0].Outputs != null && link[0].Outputs.Any(item =>
                string.Equals(Path.GetFileName(item), "GameAssembly.dylib", StringComparison.Ordinal)),
                "Bee linker does not emit GameAssembly.dylib.");
            Require(GraphContainsNativeOutput(projectRoot, graphPath, nativeLibraryPath),
                "Bee action graph does not retain the selected native library output.");
            string linkOutput = link[0].Outputs.Single(item =>
                string.Equals(Path.GetFileName(item), "GameAssembly.dylib", StringComparison.Ordinal));

            string compilerPath = CompilerPath(compile[0].Action);
            Require(File.Exists(compilerPath), "Bee compiler executable is missing: " + compilerPath);
            string compilerSha = ShadowHash.File(compilerPath);
            Require(compile.All(node => CompilerPath(node.Action) == compilerPath) && CompilerPath(link[0].Action) == compilerPath,
                "Bee native actions use more than one compiler executable.");
            string compilerVersion = Run(compilerPath, "--version", projectRoot);

            string sdkPath = Sysroot(compile[0].Action);
            Require(!string.IsNullOrWhiteSpace(sdkPath) && Directory.Exists(sdkPath), "Bee compiler sysroot is missing: " + sdkPath);
            Require(compile.All(node => Sysroot(node.Action) == sdkPath) && Sysroot(link[0].Action) == sdkPath,
                "Bee native actions use more than one SDK sysroot.");
            string sdkSettings = Path.Combine(sdkPath, "SDKSettings.plist");
            Require(File.Exists(sdkSettings), "SDKSettings.plist is missing: " + sdkSettings);
            string sdkVersion = Run("xcrun", "--sdk macosx --show-sdk-version", projectRoot).Trim();
            Require(!string.IsNullOrWhiteSpace(sdkVersion), "xcrun returned no macOS SDK version.");

            string configPath = Path.Combine(projectRoot, Il2CppConfigRelativePath.Replace('/', Path.DirectorySeparatorChar));
            Require(File.Exists(configPath) && !IsSymlink(configPath), "IL2CPP configuration header is missing or symlinked.");
            string config = File.ReadAllText(configPath);
            string configDebug = HeaderDefault(config, "IL2CPP_DEBUG");
            string configDevelopment = HeaderDefault(config, "IL2CPP_DEVELOPMENT");

            var macroValues = new Dictionary<string, HashSet<string>>(StringComparer.Ordinal);
            foreach (string macro in new[] { "IL2CPP_DEBUG", "NDEBUG", "IL2CPP_DEVELOPMENT" })
                macroValues[macro] = new HashSet<string>(StringComparer.Ordinal);
            foreach (BeeNode node in compile)
                foreach (Match match in MacroPattern.Matches(node.Action))
                {
                    string name = match.Groups["name"].Value;
                    if (!macroValues.ContainsKey(name)) continue;
                    macroValues[name].Add(match.Groups["value"].Success ? match.Groups["value"].Value : "1");
                }
            Require(macroValues["IL2CPP_DEBUG"].Count <= 1 && macroValues["NDEBUG"].Count <= 1 && macroValues["IL2CPP_DEVELOPMENT"].Count <= 1,
                "Native actions disagree on effective IL2CPP diagnostic macros.");
            string il2cppDebug = Effective(macroValues["IL2CPP_DEBUG"], configDebug);
            string il2cppDevelopment = Effective(macroValues["IL2CPP_DEVELOPMENT"], configDevelopment);
            string ndebug = Effective(macroValues["NDEBUG"], "0");

            var responseSources = new HashSet<string>(StringComparer.Ordinal);
            foreach (BeeNode node in compile.Concat(link))
                foreach (Match match in ResponsePattern.Matches(node.Action))
                {
                    string path = match.Groups["quoted"].Success ? match.Groups["quoted"].Value : match.Groups["plain"].Value;
                    responseSources.Add(Resolve(projectRoot, path));
                }
            Directory.CreateDirectory(evidenceRoot);
            evidencePath = Path.Combine(evidenceRoot, "h1-compiler-provenance.json");
            string retainedGraph = Path.Combine(evidenceRoot, "bee-action-graph.json");
            WriteBytesNew(retainedGraph, graphBytes);
            Require(ShadowHash.File(retainedGraph) == graphSha, "Retained Bee action graph hash differs.");
            string responseRoot = Path.Combine(evidenceRoot, "response-files");
            var responses = new List<ResponseFile>();
            foreach (string source in responseSources.OrderBy(item => item, StringComparer.Ordinal))
            {
                Require(File.Exists(source) && !IsSymlink(source), "Referenced native response file is missing or symlinked: " + source);
                string hash = ShadowHash.File(source);
                string retained = Path.Combine(responseRoot, responses.Count.ToString("D4") + "-" + Path.GetFileName(source));
                Directory.CreateDirectory(responseRoot);
                File.Copy(source, retained, false);
                Require(ShadowHash.File(retained) == hash, "Retained response-file hash differs: " + source);
                responses.Add(new ResponseFile { sourcePath = source, retainedPath = retained, sha256 = hash, bytes = new FileInfo(source).Length });
            }

            var capture = new Capture
            {
                schemaVersion = SchemaVersion,
                buildId = buildId, buildGuid = buildGuid, inputSnapshotHash = inputSnapshotHash,
                nativeLibraryPath = Path.GetFullPath(nativeLibraryPath), nativeLibrarySha256 = nativeLibrarySha256,
                sourcePinSha256 = sourcePinSha256,
                beeActionGraphPath = retainedGraph, beeActionGraphSha256 = graphSha,
                beeLinkOutputPath = Resolve(projectRoot, linkOutput),
                compileActionCount = compile.Length, linkActionCount = link.Length,
                compilerPath = compilerPath, compilerSha256 = compilerSha, compilerVersion = compilerVersion,
                sdkPath = sdkPath, sdkVersion = sdkVersion, sdkSettingsPath = sdkSettings,
                sdkSettingsSha256 = ShadowHash.File(sdkSettings), il2cppConfigPath = configPath,
                il2cppConfigSha256 = ShadowHash.File(configPath), il2cppDebug = il2cppDebug,
                ndebug = ndebug, il2cppDevelopment = il2cppDevelopment,
                macroEvidence = "Native Bee Action arguments; absent IL2CPP_DEBUG/IL2CPP_DEVELOPMENT use the retained il2cpp-config.h defaults; NDEBUG absent means 0.",
                responseFiles = responses.ToArray(),
            };
            WriteJsonNew(evidencePath, capture);
            evidenceSha256 = ShadowHash.File(evidencePath);
            return capture;
        }

        private static string SelectChangedGraph(string projectRoot, string nativeLibraryPath, GraphInventory before)
        {
            var old = before.entries.ToDictionary(item => item.path, item => item.sha256, StringComparer.Ordinal);
            string[] candidates = Directory.Exists(Path.Combine(projectRoot, "Library", "Bee"))
                ? Directory.GetFiles(Path.Combine(projectRoot, "Library", "Bee"), "Player*.dag.json", SearchOption.TopDirectoryOnly)
                : new string[0];
            var matches = candidates.Where(path => !IsSymlink(path)).Select(path => Path.GetFullPath(path))
                .Where(path => !old.TryGetValue(path, out string prior) || prior != ShadowHash.File(path))
                .Where(path => GraphContainsNativeOutput(projectRoot, path, nativeLibraryPath)).ToArray();
            Require(matches.Length == 1, "Expected one changed Bee graph for the selected native output; found " + matches.Length + ".");
            return matches[0];
        }

        private static bool GraphContainsNativeOutput(string projectRoot, string path, string nativeLibraryPath)
        {
            try
            {
                var graph = JsonUtility.FromJson<BeeGraph>(new UTF8Encoding(false).GetString(File.ReadAllBytes(path)));
                return graph != null && graph.Nodes != null && graph.Nodes.Any(node => node != null && node.Outputs != null &&
                    node.Outputs.Any(item => SamePath(projectRoot, item, nativeLibraryPath)));
            }
            catch { return false; }
        }

        private static string CompilerPath(string action)
        {
            Match match = Regex.Match(action ?? "", @"^\s*(?:""(?<quoted>[^""]+)""|(?<plain>\S+))");
            Require(match.Success, "Native Bee action has no compiler executable.");
            return Path.GetFullPath(match.Groups["quoted"].Success ? match.Groups["quoted"].Value : match.Groups["plain"].Value);
        }

        private static string Sysroot(string action)
        {
            Match match = SysrootPattern.Match(action ?? "");
            Require(match.Success, "Native Bee action has no explicit SDK sysroot.");
            return Path.GetFullPath(match.Groups["quoted"].Success ? match.Groups["quoted"].Value : match.Groups["plain"].Value);
        }

        private static string HeaderDefault(string source, string name)
        {
            Match match = Regex.Match(source, @"#define\s+" + name + @"\s+([01])\b");
            Require(match.Success, "Retained IL2CPP config has no canonical default for " + name + ".");
            return match.Groups[1].Value;
        }

        private static string Effective(HashSet<string> values, string fallback)
        { return values.Count == 0 ? fallback : values.Single(); }

        private static bool SamePath(string projectRoot, string graphPath, string actual)
        { return string.Equals(Resolve(projectRoot, graphPath), Path.GetFullPath(actual), StringComparison.Ordinal); }

        private static string Resolve(string projectRoot, string path)
        { return Path.GetFullPath(Path.IsPathRooted(path) ? path : Path.Combine(projectRoot, path)); }

        private static string Run(string fileName, string arguments, string workingDirectory)
        {
            var info = new ProcessStartInfo { FileName = fileName, Arguments = arguments, WorkingDirectory = workingDirectory,
                UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true, CreateNoWindow = true };
            using (var process = Process.Start(info))
            {
                string stdout = process.StandardOutput.ReadToEnd();
                string stderr = process.StandardError.ReadToEnd();
                process.WaitForExit();
                Require(process.ExitCode == 0, "Provenance command failed: " + fileName + " " + arguments + "\n" + stderr);
                return stdout + (string.IsNullOrEmpty(stderr) ? "" : "\n" + stderr);
            }
        }

        private static void WriteBytesNew(string path, byte[] bytes)
        {
            using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            { stream.Write(bytes, 0, bytes.Length); stream.Flush(true); }
        }

        private static void WriteJsonNew(string path, object value)
        { WriteBytesNew(path, new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(value, true))); }

        private static bool IsSymlink(string path)
        { return (File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0; }

        private static void Require(bool value, string message)
        { if (!value) throw new BuildFailedException("H1 compiler provenance: " + message); }
    }
}
