using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>
    /// Proves installed Player compiler libraries for the stable-AOT allowlist.
    /// This is not framework identity-unification evidence: the framework
    /// verifier remains restricted to Unity's target system-reference directories.
    /// </summary>
    public static class M03CompilerLibraryVerifier
    {
        public static M03CompilerLibraryEvidence Verify(string root, AssemblySnapshotReceipt receipt,
            VerifiedTargetFrameworkReferences framework)
        {
            ShadowHash.Require(framework != null && receipt != null && framework.SnapshotHash == receipt.snapshotHash &&
                framework.UnityVersion == receipt.unityVersion && framework.Target == receipt.target &&
                framework.Architecture == receipt.architecture, "M03CompilerTargetMismatch",
                "Compiler-library evidence requires the same verified target-framework snapshot.");
            return VerifyAgainstCatalog(root, receipt, EditorApplication.applicationContentsPath,
                AssemblySnapshot.TargetCompilerReferences(), framework.ProvenanceHash);
        }

        // Only the production entry point supplies the installed Editor root and
        // the active Player compiler's actual reference list. Receipt sourcePath,
        // assembly-name prefixes and Bootstrap dependencies grant no authority.
        internal static M03CompilerLibraryEvidence VerifyAgainstCatalog(string root, AssemblySnapshotReceipt receipt,
            string editorContentsPath, IEnumerable<string> compilerReferences, string frameworkProvenanceHash)
        {
            ShadowHash.Require(receipt != null && receipt.schemaVersion == 1 && receipt.sourcePins != null &&
                receipt.snapshotHash == AssemblySnapshot.ComputeHash(receipt), "M03CompilerSnapshotMismatch",
                "Compiler-library evidence requires an unchanged captured snapshot.");
            ShadowHash.Require(!string.IsNullOrWhiteSpace(editorContentsPath) && Path.IsPathRooted(editorContentsPath) &&
                Directory.Exists(editorContentsPath) && compilerReferences != null &&
                frameworkProvenanceHash != null && frameworkProvenanceHash.Length == 64 &&
                frameworkProvenanceHash.All(c => c >= '0' && c <= '9' || c >= 'a' && c <= 'f'),
                "M03CompilerCatalogUnavailable", "Installed Editor, target compiler references and framework proof are required.");
            string contents = Path.GetFullPath(editorContentsPath).TrimEnd(Path.DirectorySeparatorChar);
            var catalog = new Dictionary<string, KeyValuePair<string, string>>(StringComparer.OrdinalIgnoreCase);
            foreach (string reference in compilerReferences.Distinct(StringComparer.Ordinal))
            {
                if (string.IsNullOrWhiteSpace(reference) || !Path.IsPathRooted(reference)) continue;
                string full = Path.GetFullPath(reference);
                if (!full.StartsWith(contents + Path.DirectorySeparatorChar, StringComparison.Ordinal)) continue;
                RequireInstalledPath(contents, full);
                byte[] bytes = File.ReadAllBytes(full);
                using (var module = ModuleDefMD.Load(bytes))
                {
                    ShadowHash.Require(module.Assembly != null, "M03CompilerCatalogInvalid", full);
                    string name = AssemblyIdentityUtil.CanonicalName(module.Assembly.Name);
                    var item = new KeyValuePair<string, string>(module.Assembly.FullName, ShadowHash.Bytes(bytes));
                    KeyValuePair<string, string> prior;
                    ShadowHash.Require(!catalog.TryGetValue(name, out prior) || prior.Key == item.Key && prior.Value == item.Value,
                        "M03CompilerCatalogAmbiguous", "Conflicting installed target compiler libraries: " + name);
                    catalog[name] = item;
                }
            }
            ShadowHash.Require(catalog.Count > 0, "M03CompilerCatalogUnavailable",
                "No actual Player compiler references belong to the installed Editor.");

            var providers = new Dictionary<string, string>(StringComparer.Ordinal);
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            // A library already captured as a Player input is not copied again
            // into References. Filtered inputs can never receive this proof.
            foreach (var section in new[] {
                new KeyValuePair<string, SnapshotFile[]>("Assemblies", receipt.assemblies ?? new SnapshotFile[0]),
                new KeyValuePair<string, SnapshotFile[]>("References", receipt.references ?? new SnapshotFile[0]),
            })
            foreach (SnapshotFile file in section.Value)
            {
                ShadowHash.Require(file != null && !string.IsNullOrWhiteSpace(file.name) &&
                    file.path == section.Key + "/" + file.name + ".dll" && seen.Add(AssemblyIdentityUtil.CanonicalName(file.name)),
                    "M03CompilerReferenceRoleMismatch", "Compiler libraries must be unique captured input/reference DLLs.");
                byte[] bytes = File.ReadAllBytes(ShadowHash.SafeChild(root, file.path));
                string hash = ShadowHash.Bytes(bytes);
                ShadowHash.Require(hash == file.sha256, "M03CompilerReferenceHashMismatch", file.path);
                using (var module = ModuleDefMD.Load(bytes))
                {
                    ShadowHash.Require(module.Assembly != null &&
                        AssemblyIdentityUtil.CanonicalName(module.Assembly.Name) == AssemblyIdentityUtil.CanonicalName(file.name),
                        "M03CompilerReferenceIdentityMismatch", file.path);
                    KeyValuePair<string, string> installed;
                    if (!catalog.TryGetValue(AssemblyIdentityUtil.CanonicalName(file.name), out installed)) continue;
                    ShadowHash.Require(installed.Key == module.Assembly.FullName && installed.Value == hash,
                        "M03CompilerReferenceMismatch", "Captured library is not the exact installed target compiler input: " + file.path);
                    providers.Add(installed.Key, installed.Value);
                }
            }
            return new M03CompilerLibraryEvidence(receipt.snapshotHash, frameworkProvenanceHash, providers);
        }

        private static void RequireInstalledPath(string contents, string path)
        {
            for (string current = path; current != null && current.Length >= contents.Length; current = Path.GetDirectoryName(current))
                ShadowHash.Require((File.GetAttributes(current) & System.IO.FileAttributes.ReparsePoint) == 0, "M03CompilerCatalogLink",
                    "Installed compiler provenance cannot traverse a filesystem link: " + current);
        }
    }

    public sealed class M03CompilerLibraryEvidence
    {
        internal M03CompilerLibraryEvidence(string snapshotHash, string frameworkProvenanceHash, IDictionary<string, string> providers)
        {
            Providers = Array.AsReadOnly(providers.OrderBy(p => p.Key, StringComparer.Ordinal)
                .Select(p => p.Key + " | sha256=" + p.Value).ToArray());
            ProvenanceHash = ShadowHash.Text("m03-target-compiler-libraries:1\n" + frameworkProvenanceHash + "\n" +
                snapshotHash + "\n" + string.Join("\n", Providers.ToArray()));
        }

        public IReadOnlyList<string> Providers { get; private set; }
        public string ProvenanceHash { get; private set; }
    }
}
