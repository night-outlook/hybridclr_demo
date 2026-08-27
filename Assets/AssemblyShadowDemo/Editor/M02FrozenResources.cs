using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>One historical migration, anchored to the accepted M01 evidence. Never rebuilds or changes M01 bundles.</summary>
    public static class M02FrozenResources
    {
        private const string OriginalManifestSha = "e0125ed2b59177fb8577dab0498325a4a489404d3147b7bb857f442a9464928d";
        private const string OriginalAuditSha = "4fe92ddfb66134efbef3f34fbd695abe262611c326196627c8b743b32f4785cc";
        private const string AuditPath = "Docs/AssemblyShadow/M01/Evidence/m01-source-asset-audit.json";

        public static string Import(string frozenRoot, string playerInputSnapshot, string outputDirectory, BuildTarget target, string architecture, ShadowPolicyConfiguration policy)
        {
            string manifestPath = Path.Combine(frozenRoot, "baseline-manifest.json");
            Require(ShadowHash.File(manifestPath) == OriginalManifestSha && ShadowHash.File(AuditPath) == OriginalAuditSha,
                "Original accepted M01 manifest/source-audit anchor changed.");
            var original = JsonUtility.FromJson<OriginalManifest>(File.ReadAllText(manifestPath));
            var audit = JsonUtility.FromJson<SourceAudit>(File.ReadAllText(AuditPath));
            Require(original.schemaVersion == 1 && original.baselineBuildId == M01Paths.BaselineBuildId && original.unityVersion == Application.unityVersion &&
                original.target == target.ToString() && original.architecture == architecture && audit.verified, "M01 identity/source audit mismatch.");
            var player = AssemblySnapshot.ReadAndVerify(playerInputSnapshot, true);
            var framework = TargetFrameworkReferenceVerifier.Verify(playerInputSnapshot, player);
            Require(player.unityVersion == original.unityVersion && player.target == original.target && player.architecture == original.architecture, "Player target differs from original M01.");
            Require(!Directory.Exists(outputDirectory) && !File.Exists(outputDirectory), "Resource import destination is immutable: " + outputDirectory);
            string temporary = Path.GetFullPath(outputDirectory) + ".building-" + Guid.NewGuid().ToString("N");
            Directory.CreateDirectory(temporary);
            string sourceRoot = ShadowHash.SafeChild(frozenRoot, original.sourceSnapshotPath);
            var auditByPath = audit.comparedFiles.ToDictionary(f => f.path, StringComparer.Ordinal);
            foreach (var file in audit.comparedFiles)
                Require(file.matchesFrozen && ShadowHash.File(ShadowHash.SafeChild(sourceRoot, file.path)) == file.sha256, "Audited frozen source changed: " + file.path);
            var sources = new List<ShadowResourceSource>();
            foreach (var file in audit.comparedFiles.OrderBy(f => f.path, StringComparer.Ordinal))
            {
                if (file.path.EndsWith(".meta", StringComparison.Ordinal) && auditByPath.ContainsKey(file.path.Substring(0, file.path.Length - 5))) continue;
                var source = new ShadowResourceSource { path = file.path, snapshotPath = "Sources/" + file.path, sha256 = file.sha256 };
                Copy(ShadowHash.SafeChild(sourceRoot, file.path), temporary, source.snapshotPath, file.sha256);
                AuditFile meta;
                if (auditByPath.TryGetValue(file.path + ".meta", out meta))
                {
                    source.metaSnapshotPath = source.snapshotPath + ".meta"; source.metaSha256 = meta.sha256;
                    source.guid = ShadowResourceBaseline.MetaGuid(File.ReadAllText(ShadowHash.SafeChild(sourceRoot, meta.path)));
                    Copy(ShadowHash.SafeChild(sourceRoot, meta.path), temporary, source.metaSnapshotPath, meta.sha256);
                }
                sources.Add(source);
            }
            foreach (var asset in original.assets)
            {
                var source = sources.Single(s => s.path == asset.path);
                Require(source.guid == asset.assetGuid, "Original manifest GUID disagrees with audited asset meta: " + asset.path);
                // The AssetDatabase is permitted only to provide engine-owned builtin dependencies.
                // Authored resource identities always come from the frozen snapshot, never live files.
                Require(ShadowHash.File(asset.path) == source.sha256 && ShadowHash.File(asset.path + ".meta") == source.metaSha256,
                    "Import requires the exact original assets/metas: " + asset.path);
            }
            CopyCompilerInputs(playerInputSnapshot, temporary, player);
            string metadata = Path.Combine(temporary, "ResourceAssemblies");
            Directory.CreateDirectory(metadata);
            var metadataFiles = new List<ShadowResourceProofFile>();
            foreach (var assembly in original.assemblies)
            {
                string relative = "ResourceAssemblies/" + assembly.name + ".dll";
                Copy(ShadowHash.SafeChild(frozenRoot, assembly.path), temporary, relative, assembly.sha256);
                using (var module = ModuleDefMD.Load(Path.Combine(temporary, relative))) Require(module.Assembly.Name == assembly.name && module.Mvid.ToString() == assembly.mvid, "Original DLL identity changed: " + assembly.name);
                if (!string.IsNullOrEmpty(assembly.pdbPath)) Copy(ShadowHash.SafeChild(frozenRoot, assembly.pdbPath), temporary, "OriginalPdb/" + assembly.name + ".pdb", assembly.pdbSha256);
                metadataFiles.Add(new ShadowResourceProofFile { path = relative, sha256 = assembly.sha256 });
            }
            var reconstructed = CompileFrozenConsumers(temporary, player, sources, metadataFiles);
            string[] candidates = policy.assemblies.Where(a => a.isShadowCapable).Select(a => a.name).OrderBy(n => n, StringComparer.Ordinal).ToArray();
            Require(new HashSet<string>(metadataFiles.Select(f => Path.GetFileNameWithoutExtension(f.path)), StringComparer.Ordinal).SetEquals(candidates),
                "M01 importer only proves the five original business assemblies; new candidates require new resources.");
            ResourceAbiDescriptor abi;
            ShadowResourceScript[] scripts;
            using (var set = DnlibAssemblyLoader.Load(metadata, new[] { Path.Combine(temporary, "CompilerInputs/Assemblies"), Path.Combine(temporary, "CompilerInputs/References") }, policy.assemblies,
                targetFrameworkReferences: framework))
            {
                abi = UnitySerializedTypeAnalyzer.Analyze(set, candidates);
                scripts = ScriptIdentities(set, sources, temporary);
            }
            Require(abi.unknowns.Length == 0 && abi.types.All(t => !t.hasUnknown), "Frozen source ABI has unproven types.");
            CaptureDependencies(temporary, sources);
            var map = new ShadowResourceBuildMap { bundleDirectory = "Bundles", bundles = new[] {
                new ShadowBundleDefinition { name = "business-scene.bundle", assets = new[] { M01Paths.BusinessScene } },
                new ShadowBundleDefinition { name = "versioned-prefab.bundle", assets = new[] { M01Paths.Prefab } },
                new ShadowBundleDefinition { name = "versioned-data.bundle", assets = new[] { M01Paths.Data } },
            } };
            var index = AssetScriptReferenceIndexer.Build(ShadowResourceBaseline.ValidateMap(map), abi, policy.dependencies, new FrozenResourceAssetReader(temporary, sources, scripts));
            Require(!index.hasUnknown, "Frozen source index is unproven: " + string.Join("; ", index.unknowns));
            var bundles = original.bundles.Select(b => new ShadowBundleArtifact { name = b.name, sha256 = b.sha256, assets = map.bundles.Single(m => m.name == b.name).assets }).ToArray();
            foreach (var bundle in original.bundles) Copy(ShadowHash.SafeChild(frozenRoot, bundle.path), temporary, "Bundles/" + bundle.name, bundle.sha256);
            Copy(manifestPath, temporary, "Original/baseline-manifest.json", OriginalManifestSha);
            Copy(AuditPath, temporary, "Original/source-audit.json", OriginalAuditSha);
            Json(temporary, "resource-abi.json", abi); Json(temporary, "resource-script-index.json", index);
            var receipt = new ShadowResourceBaselineReceipt {
                provenance = ShadowResourceBaseline.M01Provenance, unityVersion = original.unityVersion, target = original.target, architecture = original.architecture,
                compilerSnapshotHash = player.snapshotHash, compilerSnapshotIsPlayer = true, metadataAssemblyDirectory = "ResourceAssemblies", metadataAssemblies = metadataFiles.ToArray(),
                candidateAssemblies = candidates, buildMap = map, bundles = bundles.OrderBy(b => b.name, StringComparer.Ordinal).ToArray(),
                sources = sources.OrderBy(s => s.path, StringComparer.Ordinal).ToArray(), scripts = scripts, dependencies = policy.dependencies,
                sourceSetHash = ShadowResourceBaseline.ComputeSourceSetHash(sources), resourceAbiHash = ResourceAbiHasher.Compute(abi), resourceAbiFileSha256 = ShadowHash.File(Path.Combine(temporary, "resource-abi.json")),
                resourceIndexHash = ShadowHash.File(Path.Combine(temporary, "resource-script-index.json")), originalManifestPath = "Original/baseline-manifest.json", originalManifestSha256 = OriginalManifestSha,
                originalSourceAuditPath = "Original/source-audit.json", originalSourceAuditSha256 = OriginalAuditSha, reconstructionProof = reconstructed,
            };
            Json(temporary, ShadowResourceBaseline.ReceiptName, receipt);
            File.WriteAllText(Path.Combine(temporary, "manifest.sha256"), ShadowHash.File(Path.Combine(temporary, ShadowResourceBaseline.ReceiptName)) + "\n", new UTF8Encoding(false));
            var verified = ShadowResourceBaseline.ReadAndVerify(temporary, target, architecture);
            using (var current = DnlibAssemblyLoader.Load(Path.Combine(playerInputSnapshot, "Assemblies"), new[] { Path.Combine(playerInputSnapshot, "References") }, policy.assemblies,
                targetFrameworkReferences: framework))
                ShadowResourceBaseline.RequirePlayerAbi(verified, UnitySerializedTypeAnalyzer.Analyze(current, candidates));
            // Re-check original anchors/assets after all compiler and index work, before publishing.
            Require(ShadowHash.File(manifestPath) == OriginalManifestSha && ShadowHash.File(AuditPath) == OriginalAuditSha, "Original proof changed during import.");
            foreach (var file in audit.comparedFiles) Require(ShadowHash.File(ShadowHash.SafeChild(sourceRoot, file.path)) == file.sha256, "Frozen source changed during import: " + file.path);
            Directory.Move(temporary, Path.GetFullPath(outputDirectory));
            ShadowResourceBaseline.ReadAndVerify(outputDirectory, target, architecture);
            return Path.GetFullPath(outputDirectory);
        }

        private static ShadowResourceProofFile[] CompileFrozenConsumers(string root, AssemblySnapshotReceipt player, List<ShadowResourceSource> sources, List<ShadowResourceProofFile> metadata)
        {
            string editor = EditorApplication.applicationContentsPath;
            string host = Path.Combine(editor, "NetCoreRuntime", Application.platform == RuntimePlatform.WindowsEditor ? "dotnet.exe" : "dotnet");
            string csc = Path.Combine(editor, "DotNetSdkRoslyn/csc.dll");
            Require(File.Exists(host) && File.Exists(csc), "Pinned Unity C# compiler is unavailable.");
            var proof = new List<ShadowResourceProofFile>();
            foreach (string name in new[] { "AssemblyShadowDemo.ContractsConsumer", "AssemblyShadowDemo.ExtensibilityConsumer" })
            {
                var asmdef = sources.Single(s => s.path.EndsWith("/" + name + ".asmdef", StringComparison.Ordinal));
                var definition = JsonUtility.FromJson<Definition>(File.ReadAllText(Path.Combine(root, asmdef.snapshotPath)));
                Require(definition.name == name && (definition.includePlatforms ?? new string[0]).Length == 0 && (definition.defineConstraints ?? new string[0]).Length == 0,
                    "Historical consumer compilation settings cannot be proven: " + name);
                string directory = Path.GetDirectoryName(asmdef.path).Replace('\\', '/') + "/";
                var inputs = sources.Where(s => s.path.StartsWith(directory, StringComparison.Ordinal) && s.path.EndsWith(".cs", StringComparison.Ordinal)).ToArray();
                Require(inputs.Length > 0 && inputs.All(s => !Regex.IsMatch(File.ReadAllText(Path.Combine(root, s.snapshotPath)), @"(?m)^\s*#")),
                    "Historical consumer has conditional sources; a full historical compiler receipt is required.");
                string dll = "ResourceAssemblies/" + name + ".dll";
                var references = AssemblySnapshot.AllFiles(player).Where(a => !M02Build.Candidates.Contains(a.name)).Select(a => Path.Combine(root, "CompilerInputs", a.path))
                    .Concat(metadata.Select(m => Path.Combine(root, m.path))).Distinct(StringComparer.Ordinal).OrderBy(p => p, StringComparer.Ordinal).ToArray();
                var arguments = new List<string> { "/nologo", "/noconfig", "/nostdlib+", "/target:library", "/deterministic+", "/langversion:9.0", "/debug:portable", "/out:" + Quote(Path.Combine(root, dll)) };
                arguments.AddRange(references.Select(r => "/reference:" + Quote(r)));
                arguments.AddRange(inputs.Select(s => Quote(Path.Combine(root, s.snapshotPath))));
                string response = "Reconstruction/" + name + ".rsp";
                string responsePath = Path.Combine(root, response); Directory.CreateDirectory(Path.GetDirectoryName(responsePath));
                File.WriteAllText(responsePath, string.Join("\n", arguments.ToArray()), new UTF8Encoding(false));
                var start = new ProcessStartInfo { FileName = host, Arguments = Quote(csc) + " @" + Quote(responsePath), UseShellExecute = false, CreateNoWindow = true, RedirectStandardOutput = true, RedirectStandardError = true };
                using (var process = Process.Start(start))
                {
                    Require(process != null, "Could not start pinned Unity compiler.");
                    var stdout = process.StandardOutput.ReadToEndAsync(); var stderr = process.StandardError.ReadToEndAsync();
                    if (!process.WaitForExit(60000)) { process.Kill(); throw new ShadowBuildException("FrozenSourceCompileFailed", "Timed out compiling frozen consumer " + name); }
                    string log = stdout.GetAwaiter().GetResult() + stderr.GetAwaiter().GetResult();
                    File.WriteAllText(Path.Combine(root, "Reconstruction/" + name + ".log"), log, new UTF8Encoding(false));
                    Require(process.ExitCode == 0 && File.Exists(Path.Combine(root, dll)), "Frozen consumer compile failed: " + log);
                }
                var output = new ShadowResourceProofFile { path = dll, sha256 = ShadowHash.File(Path.Combine(root, dll)) }; metadata.Add(output); proof.Add(output);
                proof.Add(new ShadowResourceProofFile { path = response, sha256 = ShadowHash.File(responsePath) });
                string description = "Reconstruction/" + name + ".json";
                Json(root, description, new Reconstruction { compilerPath = csc, compilerSha256 = ShadowHash.File(csc), hostPath = host, hostSha256 = ShadowHash.File(host),
                    output = output, sourcePaths = inputs.Select(s => s.snapshotPath).ToArray(), sourceSha256 = inputs.Select(s => s.sha256).ToArray(),
                    referencePaths = references.Select(p => p.Substring(root.Length + 1).Replace('\\', '/')).ToArray(), referenceSha256 = references.Select(ShadowHash.File).ToArray() });
                proof.Add(new ShadowResourceProofFile { path = description, sha256 = ShadowHash.File(Path.Combine(root, description)) });
            }
            return proof.ToArray();
        }

        private static ShadowResourceScript[] ScriptIdentities(CompiledAssemblySet set, IEnumerable<ShadowResourceSource> sources, string root)
        {
            var result = new List<ShadowResourceScript>();
            foreach (var source in sources.Where(s => s.path.EndsWith(".cs", StringComparison.Ordinal)))
            {
                string name = Path.GetFileNameWithoutExtension(source.path);
                var candidates = set.Modules.Values.Where(m => M02Build.Candidates.Contains(m.Assembly.Name.String)).SelectMany(m => m.GetTypes()).Where(t => t.Name == name).ToArray();
                Require(candidates.Length == 1, "Frozen source script type identity is ambiguous: " + source.path);
                var type = candidates[0];
                result.Add(new ShadowResourceScript { path = source.path, guid = source.guid, localId = 11500000, assembly = type.Module.Assembly.Name.String, @namespace = type.Namespace, type = type.Name });
            }
            return result.OrderBy(s => s.guid, StringComparer.Ordinal).ToArray();
        }

        private static void CaptureDependencies(string root, List<ShadowResourceSource> sources)
        {
            var byGuid = sources.Where(s => !string.IsNullOrEmpty(s.guid)).ToDictionary(s => s.guid, StringComparer.Ordinal);
            foreach (var source in sources.ToArray())
            {
                string text = File.ReadAllText(Path.Combine(root, source.snapshotPath));
                if (!text.StartsWith("%YAML", StringComparison.Ordinal)) continue;
                var dependencies = new HashSet<string>(StringComparer.Ordinal) { source.path };
                foreach (Match match in Regex.Matches(text, @"\bguid:\s*([0-9a-f]{32})\b"))
                {
                    string guid = match.Groups[1].Value; ShadowResourceSource dependency;
                    if (!byGuid.TryGetValue(guid, out dependency))
                    {
                        string path = AssetDatabase.GUIDToAssetPath(guid);
                        Require(!string.IsNullOrEmpty(path) && !File.Exists(path), "Unproven authored dependency outside frozen M01 source: " + guid);
                        dependency = ShadowResourceBaseline.CaptureBuiltinSource(path, root);
                        Require(dependency.guid == guid, "Builtin GUID disagrees with frozen resource: " + guid);
                        sources.Add(dependency); byGuid.Add(guid, dependency);
                    }
                    dependencies.Add(dependency.path);
                }
                source.dependencies = dependencies.OrderBy(p => p, StringComparer.Ordinal).ToArray();
            }
            var byPath = sources.ToDictionary(s => s.path, StringComparer.Ordinal);
            foreach (var source in sources)
            {
                var closure = new HashSet<string>(source.dependencies, StringComparer.Ordinal);
                var pending = new Queue<string>(closure);
                while (pending.Count > 0) foreach (string dependency in byPath[pending.Dequeue()].dependencies) if (closure.Add(dependency)) pending.Enqueue(dependency);
                source.dependencies = closure.OrderBy(p => p, StringComparer.Ordinal).ToArray();
            }
        }

        private static void CopyCompilerInputs(string source, string root, AssemblySnapshotReceipt receipt)
        {
            foreach (var file in AssemblySnapshot.AllFiles(receipt))
            {
                Copy(Path.Combine(source, file.path), root, "CompilerInputs/" + file.path, file.sha256);
                if (!string.IsNullOrEmpty(file.pdbPath)) Copy(Path.Combine(source, file.pdbPath), root, "CompilerInputs/" + file.pdbPath, file.pdbSha256);
            }
            Json(root, "CompilerInputs/" + AssemblySnapshot.ReceiptName, receipt);
            ShadowLinkedPlayerEvidence.Copy(source, Path.Combine(root, "CompilerInputs"), receipt);
            ShadowReflectionBindingEvidence.Copy(source, Path.Combine(root, "CompilerInputs"), receipt);
        }
        private static void Copy(string source, string root, string relative, string hash)
        { Require(ShadowHash.File(source) == hash, "Proof input hash mismatch: " + source); string path = ShadowHash.SafeChild(root, relative); Directory.CreateDirectory(Path.GetDirectoryName(path)); File.Copy(source, path, false); Require(ShadowHash.File(path) == hash, "Copied proof hash mismatch: " + relative); }
        private static void Json(string root, string relative, object value)
        { string path = ShadowHash.SafeChild(root, relative); Directory.CreateDirectory(Path.GetDirectoryName(path)); File.WriteAllText(path, JsonUtility.ToJson(value, true), new UTF8Encoding(false)); }
        private static string Quote(string value) { Require(!value.Contains("\"") && !value.Contains("\n") && !value.Contains("\r"), "Unsupported compiler path."); return "\"" + value + "\""; }
        private static void Require(bool condition, string message) { ShadowHash.Require(condition, "M01ResourceProvenance", message); }
        [Serializable] private sealed class OriginalManifest { public int schemaVersion; public string baselineBuildId, unityVersion, target, architecture, sourceSnapshotPath; public OriginalBundle[] bundles; public OriginalAssembly[] assemblies; public OriginalAsset[] assets; }
        [Serializable] private sealed class OriginalBundle { public string name, path, sha256; }
        [Serializable] private sealed class OriginalAssembly { public string name, path, sha256, mvid, pdbPath, pdbSha256; }
        [Serializable] private sealed class OriginalAsset { public string path, assetGuid; }
        [Serializable] private sealed class SourceAudit { public bool verified; public AuditFile[] comparedFiles; }
        [Serializable] private sealed class AuditFile { public string path, sha256; public bool matchesFrozen; }
        [Serializable] private sealed class Definition { public string name; public string[] includePlatforms, defineConstraints; }
        [Serializable] private sealed class Reconstruction { public string compilerPath, compilerSha256, hostPath, hostSha256; public ShadowResourceProofFile output; public string[] sourcePaths, sourceSha256, referencePaths, referenceSha256; }
    }
}
