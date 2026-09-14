using System;
using System.IO;
using System.Linq;
using System.Text;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Fresh native build evidence; interpretation is shared with the independent Python checker.</summary>
    public static class H1CompilerProvenance
    {
        [Serializable] public sealed class GraphInventory { public Entry[] entries; }
        [Serializable] public sealed class Entry { public string path, sha256; }
        [Serializable] public sealed class ResponseFile { public string sourcePath, retainedPath, sha256; public long bytes; }
        [Serializable] public sealed class Capture
        {
            public int schemaVersion;
            public string buildId, buildGuid, inputSnapshotHash;
            public string nativeLibraryPath, nativeLibrarySha256, sourcePinSha256;
            public string beeActionGraphPath, beeActionGraphSha256, beeLinkOutputPath;
            public int compileActionCount, linkActionCount;
            public string compilerPath, compilerSha256, compilerVersion;
            public string sdkPath, sdkVersion, sdkSettingsPath, sdkSettingsSha256;
            public string il2cppConfigPath, il2cppConfigSha256;
            public string il2cppDebug, ndebug, il2cppDevelopment, macroEvidence;
            public ResponseFile[] responseFiles;
        }
        [Serializable] private sealed class Request
        {
            public string projectRoot, output, buildId, buildGuid, inputSnapshotHash;
            public string nativeLibraryPath, nativeLibrarySha256, sourcePinSha256;
            public string il2cppConfigPath, cppConfiguration;
            public GraphInventory before;
            public bool featureEnabled;
        }

        public static GraphInventory Begin(string projectRoot)
        {
            string root = Path.Combine(projectRoot, "Library", "Bee");
            return new GraphInventory { entries = Directory.Exists(root)
                ? Directory.GetFiles(root, "Player*.dag.json", SearchOption.TopDirectoryOnly)
                    .Where(path => (File.GetAttributes(path) & FileAttributes.ReparsePoint) == 0)
                    .Select(path => new Entry { path = Path.GetFullPath(path), sha256 = ShadowHash.File(path) })
                    .OrderBy(row => row.path, StringComparer.Ordinal).ToArray()
                : new Entry[0] };
        }

        public static Capture CaptureAfterBuild(string projectRoot, string output, string buildId,
            string buildGuid, string inputSnapshotHash, string nativeLibraryPath, string nativeLibrarySha256,
            string sourcePinSha256, GraphInventory before, string evidenceRoot,
            out string evidencePath, out string evidenceSha256)
        {
            if (before == null || before.entries == null || File.Exists(evidenceRoot) || Directory.Exists(evidenceRoot))
                throw new BuildFailedException("A pre-build graph inventory and new provenance directory are required.");
            var request = new Request
            {
                projectRoot = Path.GetFullPath(projectRoot), output = Path.GetFullPath(output),
                buildId = buildId, buildGuid = buildGuid, inputSnapshotHash = inputSnapshotHash,
                nativeLibraryPath = Path.GetFullPath(nativeLibraryPath), nativeLibrarySha256 = nativeLibrarySha256,
                sourcePinSha256 = sourcePinSha256, before = before,
                featureEnabled = buildId.StartsWith("H1Count-On-", StringComparison.Ordinal),
                il2cppConfigPath = Path.GetFullPath(Path.Combine(HybridCLR.Editor.SettingsUtil.LocalIl2CppDir, "libil2cpp/il2cpp-config.h")),
                cppConfiguration = PlayerSettings.GetIl2CppCompilerConfiguration(NamedBuildTarget.Standalone).ToString(),
            };
            string requestPath = Path.GetFullPath(evidenceRoot) + ".request-" + Guid.NewGuid().ToString("N") + ".json";
            Directory.CreateDirectory(Path.GetDirectoryName(requestPath));
            using (var stream = new FileStream(requestPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            {
                byte[] bytes = new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(request, true));
                stream.Write(bytes, 0, bytes.Length); stream.Flush(true);
            }
            string requestHash = ShadowHash.File(requestPath);
            const string script = "Tools/AssemblyShadow/h1_native_capture.py";
            const string parser = "Tools/AssemblyShadow/h1_compiler_actions.py";
            string scriptHash = ShadowHash.File(Path.Combine(projectRoot, script));
            string parserHash = ShadowHash.File(Path.Combine(projectRoot, parser));
            H1EvidenceProcess.RunPython(projectRoot, script, "--request", requestPath,
                "--evidence-root", Path.GetFullPath(evidenceRoot));
            if (requestHash != ShadowHash.File(requestPath) || scriptHash != ShadowHash.File(Path.Combine(projectRoot, script)) ||
                parserHash != ShadowHash.File(Path.Combine(projectRoot, parser)))
                throw new BuildFailedException("Provenance inputs changed during capture.");
            evidencePath = Path.Combine(Path.GetFullPath(evidenceRoot), "h1-compiler-provenance.json");
            evidenceSha256 = ShadowHash.File(evidencePath);
            var result = JsonUtility.FromJson<Capture>(File.ReadAllText(evidencePath));
            if (result == null || result.schemaVersion != 1 || result.buildGuid != buildGuid ||
                result.buildId != buildId || result.inputSnapshotHash != inputSnapshotHash ||
                result.nativeLibrarySha256 != nativeLibrarySha256 || result.sourcePinSha256 != sourcePinSha256)
                throw new BuildFailedException("Returned compiler provenance does not bind this build.");
            return result;
        }
    }
}
