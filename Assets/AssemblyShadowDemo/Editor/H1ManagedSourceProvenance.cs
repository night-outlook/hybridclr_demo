using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEditor.Compilation;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>
    /// Captures the managed inputs which are visible to the Player compiler at
    /// the point immediately before an H1 diagnostic build.  This is a source
    /// witness only: the current Player input receipt has no source-to-DLL
    /// mapping, so BindPlayerSnapshot deliberately does not assert causality.
    /// </summary>
    public static class H1ManagedSourceProvenance
    {
        public const string ReceiptName = "managed-source-provenance.json";
        private const string SnapshotDirectory = "ManagedSource";
        private static readonly string[] ManagedExtensions = { ".cs", ".js", ".boo", ".asmdef", ".asmref" };

        [Serializable]
        public sealed class SourceFile
        {
            public string logicalPath;
            public string snapshotPath;
            public string sourcePath;
            public string sha256;
            public string metaSnapshotPath;
            public string metaSha256;
            public string kind;
        }

        [Serializable]
        public sealed class Assembly
        {
            public string name;
            public string asmdefPath;
            public string[] sourceFiles = new string[0];
            public string[] defines = new string[0];
            public string[] referenceAssemblyNames = new string[0];
        }

        [Serializable]
        public sealed class ProjectFile
        {
            public string logicalPath;
            public string snapshotPath;
            public string sourcePath;
            public string sha256;
        }

        [Serializable]
        public sealed class Capture
        {
            public int schemaVersion = 1;
            public string kind = "H1ManagedSourceProvenance";
            public string projectRoot;
            public string snapshotRoot;
            public string sourceBaseRevision;
            public string sourceHeadRevision;
            public string codeContentHash;
            public string configurationContentHash;
            public string contentSetHash;
            public SourceFile[] sourceFiles = new SourceFile[0];
            public ProjectFile[] projectFiles = new ProjectFile[0];
            public Assembly[] assemblies = new Assembly[0];
            public string[] allowedOverlayPaths = new string[0];
        }

        [Serializable]
        public sealed class BinaryInput
        {
            public string name;
            public string path;
            public string sha256;
            public string role;
            public string pdbPath;
            public string pdbSha256;
        }

        [Serializable]
        public sealed class PlayerSnapshotBinding
        {
            public int schemaVersion = 1;
            public string playerSnapshotRoot;
            public string playerSnapshotHash;
            public string buildGuid;
            public string nativeLibrarySha256;
            public string managedCodeContentHash;
            public string managedConfigurationContentHash;
            public BinaryInput[] matchedInputs = new BinaryInput[0];
            public BinaryInput[] rawCompilerInputs = new BinaryInput[0];
            public string[] unmatchedSourceAssemblies = new string[0];
            public bool sourceToBinaryCausalMappingProven;
            public string causalEvidenceRequirement;
        }

        public static Capture CaptureBeforeBuild(string projectRoot, string snapshotParent,
            string sourceBaseRevision, string sourceHeadRevision, IEnumerable<string> allowedOverlayPaths = null)
        {
            projectRoot = RequireProjectRoot(projectRoot);
            RequireRevision(sourceBaseRevision, "sourceBaseRevision");
            RequireRevision(sourceHeadRevision, "sourceHeadRevision");
            string[] overlays = NormalizeOverlayPaths(projectRoot, allowedOverlayPaths);
            string root = CreateSnapshotRoot(projectRoot, snapshotParent);
            var assemblies = new List<Assembly>();
            var sources = new List<SourceFile>();
            var logicalToPhysical = new Dictionary<string, string>(StringComparer.Ordinal);
            var physicalToLogical = new Dictionary<string, string>(StringComparer.Ordinal);

            foreach (var assembly in CompilationPipeline.GetAssemblies(AssembliesType.PlayerWithoutTestAssemblies)
                .OrderBy(a => a.name, StringComparer.Ordinal))
            {
                string asmdef = CompilationPipeline.GetAssemblyDefinitionFilePathFromAssemblyName(assembly.name);
                string asmdefLogical = string.IsNullOrEmpty(asmdef) ? "" : AddSource(projectRoot, root, overlays, asmdef,
                    "asmdef", assembly.name, sources, logicalToPhysical, physicalToLogical);
                var sourceNames = new List<string>();
                foreach (string source in (assembly.sourceFiles ?? new string[0]).OrderBy(p => p, StringComparer.Ordinal))
                    sourceNames.Add(AddSource(projectRoot, root, overlays, source, "source", assembly.name,
                        sources, logicalToPhysical, physicalToLogical));
                assemblies.Add(new Assembly {
                    name = RequireAssemblyName(assembly.name), asmdefPath = asmdefLogical,
                    sourceFiles = sourceNames.OrderBy(p => p, StringComparer.Ordinal).ToArray(),
                    defines = Sorted(assembly.defines),
                    referenceAssemblyNames = ReferenceNames(assembly),
                });
            }

            Require(assemblies.Count != 0, "ManagedSourceAssembliesMissing", "PlayerWithoutTestAssemblies returned no assemblies.");
            RejectUnexpectedManagedCode(projectRoot, overlays, logicalToPhysical);
            var projectFiles = CaptureProjectFiles(projectRoot, root);
            var capture = new Capture {
                projectRoot = projectRoot, snapshotRoot = root,
                sourceBaseRevision = sourceBaseRevision, sourceHeadRevision = sourceHeadRevision,
                sourceFiles = sources.OrderBy(f => f.logicalPath, StringComparer.Ordinal).ToArray(),
                projectFiles = projectFiles.OrderBy(f => f.logicalPath, StringComparer.Ordinal).ToArray(),
                assemblies = assemblies.OrderBy(a => a.name, StringComparer.Ordinal).ToArray(),
                allowedOverlayPaths = overlays,
            };
            capture.codeContentHash = ComputeCodeContentHash(capture);
            capture.configurationContentHash = ComputeConfigurationContentHash(capture);
            capture.contentSetHash = ShadowHash.Text("h1-managed-content-set:1\n" + capture.codeContentHash + "\n" + capture.configurationContentHash + "\n");
            WriteReceipt(capture);
            return capture;
        }

        public static void RequireUnchanged(Capture expected)
        {
            Require(expected != null && expected.schemaVersion == 1 && expected.kind == "H1ManagedSourceProvenance",
                "ManagedSourceReceiptSchema", "Managed source provenance receipt is missing or unsupported.");
            Require(expected.sourceFiles != null && expected.projectFiles != null && expected.assemblies != null,
                "ManagedSourceReceiptSchema", "Managed source provenance arrays are missing.");
            RequireRegularDirectory(expected.projectRoot, "Managed source project root");
            RequireRegularDirectory(expected.snapshotRoot, "Managed source snapshot root");
            VerifySnapshotInventory(expected);
            foreach (SourceFile file in expected.sourceFiles ?? new SourceFile[0]) VerifyLiveFile(expected, file);
            foreach (ProjectFile file in expected.projectFiles ?? new ProjectFile[0]) VerifyLiveProjectFile(expected, file);
            var current = CaptureBeforeBuild(expected.projectRoot, MakeTemporaryParent(expected.projectRoot),
                expected.sourceBaseRevision, expected.sourceHeadRevision, expected.allowedOverlayPaths);
            try
            {
                Require(expected.codeContentHash == current.codeContentHash,
                    "ManagedSourceChanged", "Managed source/asmdef content or assembly source mapping changed during the build.");
                Require(expected.configurationContentHash == current.configurationContentHash,
                    "ManagedBuildConfigurationChanged", "Defines, references, ProjectSettings, or package manifests changed during the build.");
                Require(expected.sourceFiles.Length == current.sourceFiles.Length &&
                    expected.sourceFiles.Select(f => f.logicalPath).SequenceEqual(current.sourceFiles.Select(f => f.logicalPath), StringComparer.Ordinal),
                    "ManagedSourceSetChanged", "The Player managed source set changed during the build.");
            }
            finally
            {
                DeleteTemporaryCapture(current);
            }
        }

        public static PlayerSnapshotBinding BindPlayerSnapshot(Capture source, string playerSnapshotRoot)
        {
            RequireUnchanged(source);
            AssemblySnapshotReceipt receipt = AssemblySnapshot.ReadAndVerify(Path.GetFullPath(playerSnapshotRoot), true);
            var playerFiles = AssemblySnapshot.AllFiles(receipt).OrderBy(f => f.name, StringComparer.Ordinal).ToArray();
            var byName = playerFiles.ToDictionary(f => AssemblyIdentityUtil.CanonicalName(f.name), StringComparer.Ordinal);
            var rawInputs = playerFiles.Select(file => new BinaryInput { name = file.name, path = file.path, sha256 = file.sha256,
                role = receipt.assemblies.Contains(file) ? "assembly" : receipt.filteredAssemblies.Contains(file) ? "filtered" : "reference",
                pdbPath = file.pdbPath, pdbSha256 = file.pdbSha256 }).ToArray();
            var matched = new List<BinaryInput>();
            var unmatched = new List<string>();
            foreach (Assembly assembly in source.assemblies.OrderBy(a => a.name, StringComparer.Ordinal))
            {
                SnapshotFile file;
                if (!byName.TryGetValue(AssemblyIdentityUtil.CanonicalName(assembly.name), out file))
                {
                    unmatched.Add(assembly.name);
                    continue;
                }
                matched.Add(new BinaryInput { name = file.name, path = file.path, sha256 = file.sha256,
                    role = "assembly",
                    pdbPath = file.pdbPath, pdbSha256 = file.pdbSha256 });
            }
            return new PlayerSnapshotBinding {
                playerSnapshotRoot = Path.GetFullPath(playerSnapshotRoot), playerSnapshotHash = receipt.snapshotHash,
                buildGuid = receipt.buildGuid, nativeLibrarySha256 = receipt.nativeLibrarySha256,
                managedCodeContentHash = source.codeContentHash, managedConfigurationContentHash = source.configurationContentHash,
                matchedInputs = matched.ToArray(), rawCompilerInputs = rawInputs, unmatchedSourceAssemblies = unmatched.ToArray(),
                sourceToBinaryCausalMappingProven = false,
                causalEvidenceRequirement = "AssemblySnapshotReceipt records emitted DLL identities and hashes but no source-file-set identity. Add a compiler/linker receipt that binds each emitted DLL hash to this exact assembly source-set hash before claiming source-to-binary causality.",
            };
        }

        public static string ComputeCodeContentHash(Capture capture)
        {
            var text = new StringBuilder("h1-managed-code-content:1\n");
            text.Append(capture.sourceBaseRevision).Append('\n').Append(capture.sourceHeadRevision).Append('\n');
            foreach (SourceFile file in (capture.sourceFiles ?? new SourceFile[0]).OrderBy(f => f.logicalPath, StringComparer.Ordinal))
                text.Append(file.kind).Append('\n').Append(file.logicalPath).Append('\n').Append(file.sha256).Append('\n').Append(file.metaSha256).Append('\n');
            foreach (Assembly assembly in (capture.assemblies ?? new Assembly[0]).OrderBy(a => a.name, StringComparer.Ordinal))
                text.Append("assembly:").Append(assembly.name).Append('\n').Append(assembly.asmdefPath).Append('\n')
                    .Append(string.Join(";", Sorted(assembly.sourceFiles))).Append('\n');
            return ShadowHash.Text(text.ToString());
        }

        public static string ComputeConfigurationContentHash(Capture capture)
        {
            var text = new StringBuilder("h1-managed-build-configuration:1\n");
            foreach (ProjectFile file in (capture.projectFiles ?? new ProjectFile[0]).OrderBy(f => f.logicalPath, StringComparer.Ordinal))
                text.Append(file.logicalPath).Append('\n').Append(file.sha256).Append('\n');
            foreach (Assembly assembly in (capture.assemblies ?? new Assembly[0]).OrderBy(a => a.name, StringComparer.Ordinal))
                text.Append("assembly:").Append(assembly.name).Append('\n').Append(string.Join(";", Sorted(assembly.defines))).Append('\n')
                    .Append(string.Join(";", Sorted(assembly.referenceAssemblyNames))).Append('\n');
            return ShadowHash.Text(text.ToString());
        }

        private static string AddSource(string projectRoot, string root, string[] overlays, string path, string kind, string assemblyName,
            List<SourceFile> result, Dictionary<string, string> logicalToPhysical, Dictionary<string, string> physicalToLogical)
        {
            string physical = ResolveSourceFile(projectRoot, path);
            RequireRegularFile(physical, "Managed source file");
            string logical = LogicalPath(projectRoot, overlays, path, physical);
            string prior;
            Require(!logicalToPhysical.TryGetValue(logical, out prior), "ManagedSourceDuplicateMapping",
                logical + " is mapped more than once (" + prior + " and " + physical + ").");
            Require(!physicalToLogical.TryGetValue(physical, out prior), "ManagedSourceDuplicateMapping",
                physical + " is mapped more than once (" + prior + " and " + logical + ").");
            logicalToPhysical.Add(logical, physical); physicalToLogical.Add(physical, logical);
            string snapshotPath = SnapshotDirectory + "/Sources/" + logical;
            CopyExact(physical, ShadowHash.SafeChild(root, snapshotPath), "Managed source");
            var file = new SourceFile { logicalPath = logical, snapshotPath = snapshotPath, sourcePath = physical,
                sha256 = ShadowHash.File(physical), kind = kind };
            string meta = physical + ".meta";
            if (File.Exists(meta))
            {
                RequireRegularFile(meta, "Managed source meta");
                file.metaSnapshotPath = snapshotPath + ".meta"; file.metaSha256 = ShadowHash.File(meta);
                CopyExact(meta, ShadowHash.SafeChild(root, file.metaSnapshotPath), "Managed source meta");
            }
            result.Add(file);
            return logical;
        }

        private static ProjectFile[] CaptureProjectFiles(string projectRoot, string root)
        {
            var paths = Directory.GetFiles(Path.Combine(projectRoot, "ProjectSettings"), "*", SearchOption.TopDirectoryOnly)
                .Select(p => Relative(projectRoot, p)).Concat(new[] { "Packages/manifest.json", "Packages/packages-lock.json" })
                .Distinct(StringComparer.Ordinal).OrderBy(p => p, StringComparer.Ordinal).ToArray();
            var result = new List<ProjectFile>();
            var seen = new HashSet<string>(StringComparer.Ordinal);
            foreach (string logical in paths)
            {
                string physical = Path.Combine(projectRoot, logical.Replace('/', Path.DirectorySeparatorChar));
                Require(seen.Add(logical), "ManagedProjectDuplicate", logical);
                RequireRegularFile(physical, "Managed project input");
                string snapshot = SnapshotDirectory + "/Project/" + logical;
                CopyExact(physical, ShadowHash.SafeChild(root, snapshot), "Managed project input");
                result.Add(new ProjectFile { logicalPath = logical, snapshotPath = snapshot, sourcePath = physical, sha256 = ShadowHash.File(physical) });
            }
            return result.ToArray();
        }

        private static void RejectUnexpectedManagedCode(string projectRoot, string[] overlays, Dictionary<string, string> tracked)
        {
            foreach (string root in new[] { Path.Combine(projectRoot, "Assets"), Path.Combine(projectRoot, "Packages") })
            {
                if (!Directory.Exists(root)) continue;
                foreach (string file in Directory.GetFiles(root, "*", SearchOption.AllDirectories).Where(IsManagedFile))
                {
                    if (IsIgnoredManagedPath(file) || IsUnderOverlay(file, overlays)) continue;
                    string logical = LogicalPath(projectRoot, overlays, file, file);
                    Require(tracked.ContainsKey(logical), "UnexpectedIgnoredManagedCode",
                        "Managed code is present but absent from PlayerWithoutTestAssemblies: " + logical);
                }
            }
        }

        private static bool IsIgnoredManagedPath(string path)
        {
            string[] parts = path.Replace('\\', '/').Split('/');
            return parts.Any(p => string.Equals(p, "Editor", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(p, "Tests", StringComparison.OrdinalIgnoreCase) || string.Equals(p, "Test", StringComparison.OrdinalIgnoreCase));
        }

        private static string[] ReferenceNames(UnityEditor.Compilation.Assembly assembly)
        {
            var names = new List<string>();
            if (assembly.assemblyReferences != null) names.AddRange(assembly.assemblyReferences.Where(a => a != null).Select(a => a.name));
            if (assembly.compiledAssemblyReferences != null) names.AddRange(assembly.compiledAssemblyReferences.Select(Path.GetFileNameWithoutExtension));
            return Sorted(names.Where(n => !string.IsNullOrWhiteSpace(n)).Select(AssemblyIdentityUtil.CanonicalName));
        }

        private static string ResolveSourceFile(string projectRoot, string path)
        {
            if (Path.IsPathRooted(path)) return Path.GetFullPath(path);
            if (path.StartsWith("Packages/", StringComparison.Ordinal))
            {
                var package = UnityEditor.PackageManager.PackageInfo.FindForAssetPath(path);
                if (package != null) return Path.GetFullPath(Path.Combine(package.resolvedPath, path.Substring(("Packages/" + package.name + "/").Length)));
            }
            return Path.GetFullPath(Path.Combine(projectRoot, path.Replace('/', Path.DirectorySeparatorChar)));
        }

        private static string LogicalPath(string projectRoot, string[] overlays, string original, string physical)
        {
            string relative;
            if (TryRelative(projectRoot, physical, out relative)) return relative;
            for (int i = 0; i < overlays.Length; ++i)
            {
                if (File.Exists(overlays[i]) && string.Equals(Path.GetFullPath(overlays[i]), Path.GetFullPath(physical), StringComparison.Ordinal))
                    return "Overlay/" + i.ToString() + "/" + Path.GetFileName(overlays[i]);
                if (TryRelative(overlays[i], physical, out relative)) return "Overlay/" + i.ToString() + "/" + relative;
            }
            foreach (var package in UnityEditor.PackageManager.PackageInfo.GetAllRegisteredPackages()
                .Where(p => p != null && !string.IsNullOrWhiteSpace(p.resolvedPath)).OrderBy(p => p.name, StringComparer.Ordinal))
            {
                if (TryRelative(package.resolvedPath, physical, out relative))
                    return "Packages/" + package.name + "/" + relative;
            }
            Require(false, "ManagedSourceOutsideAllowedRoots", "Managed source path is outside the project and explicit overlays: " + physical);
            return null;
        }

        private static string[] NormalizeOverlayPaths(string projectRoot, IEnumerable<string> paths)
        {
            return (paths ?? new string[0]).Select(Path.GetFullPath).Distinct(StringComparer.Ordinal)
                .OrderBy(p => p, StringComparer.Ordinal).Select(p => { Require(File.Exists(p) || Directory.Exists(p), "ManagedSourceOverlay", "Managed source overlay is missing: " + p);
                    if (Directory.Exists(p)) RequireRegularDirectory(p, "Managed source overlay"); else RequireRegularFile(p, "Managed source overlay");
                    Require(!IsSameOrUnder(projectRoot, p), "ManagedSourceOverlay", "An overlay must be outside the project root: " + p); return p; }).ToArray();
        }

        private static string CreateSnapshotRoot(string projectRoot, string parent)
        {
            string basePath = string.IsNullOrWhiteSpace(parent) ? Path.Combine(projectRoot, "_temp", "AssemblyShadow") : Path.GetFullPath(parent);
            RequireRegularDirectory(Path.GetDirectoryName(basePath) ?? projectRoot, "Managed source snapshot parent");
            Directory.CreateDirectory(basePath);
            for (int i = 0; i != 20; ++i)
            {
                string path = Path.Combine(basePath, "H1ManagedSource-" + Guid.NewGuid().ToString("N"));
                if (File.Exists(path) || Directory.Exists(path)) continue;
                Directory.CreateDirectory(path); Require(!IsSymlink(path), "ManagedSourceSnapshotPath", path); return path;
            }
            throw new ShadowBuildException("ManagedSourceSnapshotPath", "Could not allocate a fresh managed source snapshot root.");
        }

        private static string MakeTemporaryParent(string projectRoot)
        { return Path.Combine(projectRoot, "_temp", "AssemblyShadow", "H1ManagedSourceVerification-" + Guid.NewGuid().ToString("N")); }

        private static void DeleteTemporaryCapture(Capture capture)
        { if (capture != null && !string.IsNullOrEmpty(capture.snapshotRoot) && Directory.Exists(capture.snapshotRoot)) Directory.Delete(capture.snapshotRoot, true); }

        private static void WriteReceipt(Capture capture)
        { File.WriteAllText(Path.Combine(capture.snapshotRoot, ReceiptName), UnityEngine.JsonUtility.ToJson(capture, true), new UTF8Encoding(false)); }

        private static void VerifyLiveFile(Capture expected, SourceFile file)
        {
            Require(file != null && !string.IsNullOrWhiteSpace(file.sourcePath) && !string.IsNullOrWhiteSpace(file.snapshotPath), "ManagedSourceReceiptSchema", "Invalid managed source entry.");
            RequireRegularFile(file.sourcePath, "Managed source");
            Require(LogicalPath(expected.projectRoot, expected.allowedOverlayPaths ?? new string[0], file.logicalPath, file.sourcePath) == file.logicalPath,
                "ManagedSourcePathAmbiguous", file.logicalPath);
            Require(ShadowHash.File(file.sourcePath) == file.sha256, "ManagedSourceChanged", file.logicalPath);
            VerifySnapshotFile(expected.snapshotRoot, file.snapshotPath, file.sha256, "ManagedSourceSnapshotChanged");
            if (!string.IsNullOrEmpty(file.metaSnapshotPath))
            {
                RequireRegularFile(file.sourcePath + ".meta", "Managed source meta");
                Require(ShadowHash.File(file.sourcePath + ".meta") == file.metaSha256, "ManagedSourceChanged", file.logicalPath + ".meta");
                VerifySnapshotFile(expected.snapshotRoot, file.metaSnapshotPath, file.metaSha256, "ManagedSourceSnapshotChanged");
            }
        }

        private static void VerifyLiveProjectFile(Capture expected, ProjectFile file)
        {
            Require(Relative(expected.projectRoot, file.sourcePath) == file.logicalPath, "ManagedSourcePathAmbiguous", file.logicalPath);
            RequireRegularFile(file.sourcePath, "Managed project input");
            Require(ShadowHash.File(file.sourcePath) == file.sha256, "ManagedBuildConfigurationChanged", file.logicalPath);
            VerifySnapshotFile(expected.snapshotRoot, file.snapshotPath, file.sha256, "ManagedSourceSnapshotChanged");
        }

        private static void VerifySnapshotFile(string root, string relative, string hash, string code)
        { Require(File.Exists(ShadowHash.SafeChild(root, relative)) && ShadowHash.File(ShadowHash.SafeChild(root, relative)) == hash, code, relative); }

        private static void VerifySnapshotInventory(Capture expected)
        {
            var expectedFiles = (expected.sourceFiles ?? new SourceFile[0]).SelectMany(file =>
                string.IsNullOrEmpty(file.metaSnapshotPath) ? new[] { file.snapshotPath } : new[] { file.snapshotPath, file.metaSnapshotPath })
                .Concat((expected.projectFiles ?? new ProjectFile[0]).Select(file => file.snapshotPath))
                .Select(path => Path.GetFullPath(ShadowHash.SafeChild(expected.snapshotRoot, path)));
            string[] expectedArray = expectedFiles.ToArray();
            var expectedSet = new HashSet<string>(expectedArray, StringComparer.Ordinal);
            Require(expectedSet.Count == expectedArray.Length, "ManagedSourceSnapshotSetMismatch", "Managed source snapshot declares duplicate files.");
            string sourceRoot = Path.Combine(expected.snapshotRoot, SnapshotDirectory);
            Require(Directory.Exists(sourceRoot), "ManagedSourceSnapshotSetMismatch", sourceRoot);
            var actualFiles = Directory.GetFiles(sourceRoot, "*", SearchOption.AllDirectories).Select(Path.GetFullPath);
            var actualSet = new HashSet<string>(actualFiles, StringComparer.Ordinal);
            Require(expectedSet.SetEquals(actualSet), "ManagedSourceSnapshotSetMismatch",
                "Managed source snapshot contains undeclared or missing files.");
        }

        private static void CopyExact(string source, string destination, string label)
        { RequireRegularFile(source, label); Directory.CreateDirectory(Path.GetDirectoryName(destination)); File.Copy(source, destination, false); Require(ShadowHash.File(destination) == ShadowHash.File(source), "ManagedSourceSnapshotWrite", label + " changed while being snapshotted: " + source); }

        private static string RequireProjectRoot(string path)
        { string full = Path.GetFullPath(path); RequireRegularDirectory(full, "Managed source project root"); return full.TrimEnd(Path.DirectorySeparatorChar); }

        private static string Relative(string root, string path) { string result; Require(TryRelative(root, path, out result), "ManagedSourcePath", path); return result; }
        private static bool TryRelative(string root, string path, out string result)
        {
            string prefix = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
            string full = Path.GetFullPath(path);
            if (!full.StartsWith(prefix, StringComparison.Ordinal)) { result = null; return false; }
            result = full.Substring(prefix.Length).Replace(Path.DirectorySeparatorChar, '/'); return true;
        }
        private static bool IsUnder(string root, string path) { string ignored; return TryRelative(root, path, out ignored); }
        private static bool IsSameOrUnder(string root, string path)
        { return string.Equals(Path.GetFullPath(root), Path.GetFullPath(path), StringComparison.Ordinal) || IsUnder(root, path); }
        private static bool IsUnderOverlay(string path, string[] overlays) { return overlays.Any(root => (File.Exists(root) && string.Equals(Path.GetFullPath(root), Path.GetFullPath(path), StringComparison.Ordinal)) || IsUnder(root, path)); }
        private static bool IsManagedFile(string path) { return ManagedExtensions.Contains(Path.GetExtension(path), StringComparer.OrdinalIgnoreCase); }
        private static string[] Sorted(IEnumerable<string> values) { return (values ?? new string[0]).Where(v => !string.IsNullOrWhiteSpace(v)).Distinct(StringComparer.Ordinal).OrderBy(v => v, StringComparer.Ordinal).ToArray(); }
        private static string RequireAssemblyName(string name) { Require(!string.IsNullOrWhiteSpace(name), "ManagedAssemblyName", "Player assembly has no name."); return name; }
        private static void RequireRevision(string value, string name) { Require(!string.IsNullOrWhiteSpace(value), "ManagedSourceRevision", name + " is required caller-supplied evidence."); }
        private static void Require(bool condition, string code, string message) { ShadowHash.Require(condition, code, message); }
        private static void RequireRegularDirectory(string path, string label)
        {
            Require(!string.IsNullOrWhiteSpace(path) && Directory.Exists(path) && !IsSymlink(path), "ManagedSourcePath", label + " is missing or symlinked: " + path);
            RequireNoSymlinkAncestors(Path.GetFullPath(path), label);
        }
        private static void RequireRegularFile(string path, string label)
        {
            Require(!string.IsNullOrWhiteSpace(path) && File.Exists(path) && !IsSymlink(path), "ManagedSourcePath", label + " is missing or symlinked: " + path);
            RequireNoSymlinkAncestors(Path.GetDirectoryName(Path.GetFullPath(path)), label);
        }
        private static void RequireNoSymlinkAncestors(string path, string label)
        {
            for (string current = Path.GetFullPath(path); !string.IsNullOrEmpty(current); current = Path.GetDirectoryName(current))
            {
                Require(!IsSymlink(current), "ManagedSourcePath", label + " has a symlinked path component: " + current);
                string parent = Path.GetDirectoryName(current);
                if (parent == null || string.Equals(parent, current, StringComparison.Ordinal)) break;
            }
        }
        private static bool IsSymlink(string path) { try { return (File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0; } catch (FileNotFoundException) { return false; } }
    }
}
