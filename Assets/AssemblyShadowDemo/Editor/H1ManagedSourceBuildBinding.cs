using System;
using System.IO;
using System.Linq;
using System.Text;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor.Build;
using UnityEditor.Compilation;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Build-scoped source-before-build ledger used by the H1 repro provenance wrapper.</summary>
    public static class H1ManagedSourceBuildBinding
    {
        [Serializable] public sealed class Context { public string projectRoot, evidenceRoot, beginSha256, buildId; }
        [Serializable] private sealed class AssemblySources { public string name; public string[] sourceFiles, defines, referenceFiles; }
        [Serializable] private sealed class BeginRequest { public string projectRoot, buildId, sourcePinFile; public AssemblySources[] assemblies; public string[] extraScriptingDefines; }
        [Serializable] private sealed class Input { public string name, sourcePath, retainedPath, sha256; }
        [Serializable] private sealed class EndRequest
        {
            public string buildId, buildGuid, inputSnapshotHash, nativeLibrarySha256, sourcePinSha256;
            public Input[] actualInputs;
        }
        private static readonly string[] Required = { "AssemblyShadowDemo.Bootstrap", "AssemblyShadow.R01BDiagnostics" };
        private const string Script = "Tools/AssemblyShadow/h1_managed_provenance.py";

        public static Context Begin(string projectRoot, string sourcePinFile, string buildId, string evidenceRoot, string[] extraScriptingDefines)
        {
            var assemblies = CompilationPipeline.GetAssemblies(AssembliesType.Player)
                .Where(assembly => Required.Contains(assembly.name, StringComparer.Ordinal))
                .Select(assembly => new AssemblySources { name = assembly.name,
                    sourceFiles = assembly.sourceFiles.OrderBy(p => p, StringComparer.Ordinal).ToArray(),
                    defines = assembly.defines.OrderBy(p => p, StringComparer.Ordinal).ToArray(),
                    referenceFiles = assembly.compiledAssemblyReferences.OrderBy(p => p, StringComparer.Ordinal).ToArray() })
                .OrderBy(assembly => assembly.name, StringComparer.Ordinal).ToArray();
            if (assemblies.Length != Required.Length || assemblies.Any(a => a.sourceFiles.Length == 0))
                throw new BuildFailedException("Prepare diagnostic defines in a fresh Editor process before source capture.");
            var request = new BeginRequest { projectRoot = Path.GetFullPath(projectRoot), buildId = buildId,
                sourcePinFile = sourcePinFile, assemblies = assemblies, extraScriptingDefines = extraScriptingDefines };
            string path = Path.GetFullPath(evidenceRoot) + ".begin-request.json";
            WriteNew(path, request);
            H1EvidenceProcess.RunPython(projectRoot, Script, "begin", "--request", path, "--evidence-root", Path.GetFullPath(evidenceRoot));
            return new Context { projectRoot = request.projectRoot, evidenceRoot = Path.GetFullPath(evidenceRoot),
                beginSha256 = ShadowHash.File(Path.Combine(evidenceRoot, "begin.json")), buildId = buildId };
        }

        public static string End(Context context, string inputSnapshot, AssemblySnapshotReceipt captured, string sourcePinSha256)
        {
            if (context == null || captured == null || captured.buildId != context.buildId ||
                ShadowHash.File(Path.Combine(context.evidenceRoot, "begin.json")) != context.beginSha256)
                throw new BuildFailedException("Managed-source capture does not belong to this build.");
            var inputs = captured.assemblies.Where(file => Required.Contains(
                    file.name.EndsWith(".dll", StringComparison.OrdinalIgnoreCase) ? file.name.Substring(0, file.name.Length - 4) : file.name,
                    StringComparer.Ordinal))
                .Select(file => new Input {
                    name = file.name.EndsWith(".dll", StringComparison.OrdinalIgnoreCase) ? file.name.Substring(0, file.name.Length - 4) : file.name,
                    sourcePath = Path.GetFullPath(file.sourcePath), retainedPath = Path.GetFullPath(Path.Combine(inputSnapshot, file.path)), sha256 = file.sha256
                }).ToArray();
            if (inputs.Length != Required.Length) throw new BuildFailedException("Actual Player input capture is missing an H1 managed assembly.");
            var request = new EndRequest { buildId = captured.buildId, buildGuid = captured.buildGuid,
                inputSnapshotHash = captured.snapshotHash, nativeLibrarySha256 = captured.nativeLibrarySha256,
                sourcePinSha256 = sourcePinSha256, actualInputs = inputs };
            string path = Path.Combine(context.evidenceRoot, "end-request.json");
            WriteNew(path, request);
            H1EvidenceProcess.RunPython(context.projectRoot, Script, "end", "--request", path, "--evidence-root", context.evidenceRoot);
            return Path.Combine(context.evidenceRoot, "h1-managed-source-capture.json");
        }

        private static void WriteNew(string path, object value)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            {
                byte[] bytes = new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(value, true));
                stream.Write(bytes, 0, bytes.Length); stream.Flush(true);
            }
        }
    }
}
