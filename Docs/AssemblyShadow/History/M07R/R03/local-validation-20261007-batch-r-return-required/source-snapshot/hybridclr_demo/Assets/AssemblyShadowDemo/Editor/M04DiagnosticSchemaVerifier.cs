using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Exact prelink/postlink field parity, including false/zero-valued fields and nested native diagnostics.</summary>
    public static class M04DiagnosticSchemaVerifier
    {
        internal static readonly string[] BootstrapRoots = {
            "AssemblyShadowDemo.M04ReferenceProbe/Result",
            "AssemblyShadowDemo.M04ReferenceProbe/FixtureManifest",
            "AssemblyShadowDemo.M04ReferenceProbe/PlayerBuildReceipt",
            "AssemblyShadowDemo.M04ReferenceProbe/PatchManifest",
            "AssemblyShadowDemo.M04ReferenceProbe/BaselineManifest",
            "AssemblyShadowDemo.M04OrdinaryAssemblyProbe/Result",
            "AssemblyShadowDemo.M04OrdinaryAssemblyProbe/Configuration",
            "AssemblyShadowDemo.M04OrdinaryAssemblyProbe/Site",
        };

        public static void Verify(string root, AssemblySnapshotReceipt receipt)
        {
            ShadowHash.Require(receipt != null && receipt.kind == "PlayerBuildInputs" && receipt.sourcePins != null &&
                receipt.snapshotHash == AssemblySnapshot.ComputeHash(receipt), "M04DiagnosticSnapshotMismatch",
                "M04 JSON schema proof requires a verified Player input snapshot.");
            ShadowLinkedPlayerEvidence.ReadAndVerify(root, receipt);
            // Preserve the accepted native diagnostics contract as well as M04 Bootstrap DTOs.
            M03DiagnosticSchemaVerifier.Verify(root, receipt);
            var inputs = new Dictionary<string, ModuleDef>(StringComparer.OrdinalIgnoreCase);
            var linked = new Dictionary<string, ModuleDef>(StringComparer.OrdinalIgnoreCase);
            try
            {
                foreach (string name in new[] { "AssemblyShadowDemo.Bootstrap", "HybridCLR.Runtime" })
                {
                    inputs.Add(name, ReadModule(root, receipt, name, false));
                    linked.Add(name, ReadModule(root, receipt, name, true));
                }
                VerifyModules(inputs["AssemblyShadowDemo.Bootstrap"], linked["AssemblyShadowDemo.Bootstrap"], inputs, linked);
            }
            finally
            {
                foreach (var module in inputs.Values.Concat(linked.Values)) module.Dispose();
            }
        }

        internal static void VerifyModules(ModuleDef input, ModuleDef linked, IDictionary<string, ModuleDef> inputs = null,
            IDictionary<string, ModuleDef> linkedModules = null)
        {
            ShadowHash.Require(input != null && linked != null && input.Assembly != null && linked.Assembly != null &&
                input.Assembly.Name == "AssemblyShadowDemo.Bootstrap" && input.Assembly.FullName == linked.Assembly.FullName,
                "M04DiagnosticRuntimeIdentity", "M04 DTOs must identify the captured Bootstrap assembly.");
            ShadowDiagnosticSchemaProof.Verify(input, linked, BootstrapRoots, "M04Diagnostic", inputs, linkedModules, allowCoreLibraryLists: true);
        }

        private static ModuleDefMD ReadModule(string root, AssemblySnapshotReceipt receipt, string name, bool linked)
        {
            var files = linked ? receipt.linkedPlayerReceipt.assemblies.Select(file => new { file.name, file.path, file.sha256 })
                : receipt.assemblies.Select(file => new { file.name, file.path, file.sha256 });
            var matches = files.Where(file => AssemblyIdentityUtil.CanonicalName(file.name) == AssemblyIdentityUtil.CanonicalName(name)).ToArray();
            ShadowHash.Require(matches.Length == 1, "M04DiagnosticAssemblyMissing", "Exactly one captured diagnostic assembly is required: " + name);
            var file = matches[0];
            string path = ShadowHash.SafeChild(root, (linked ? ShadowLinkedPlayerEvidence.DirectoryName + "/" : "") + file.path);
            byte[] bytes = File.ReadAllBytes(path);
            ShadowHash.Require(ShadowHash.Bytes(bytes) == file.sha256, "M04DiagnosticInputChanged", "Diagnostic DLL changed: " + path);
            var module = ModuleDefMD.Load(bytes);
            if (module.Assembly != null && AssemblyIdentityUtil.CanonicalName(module.Assembly.Name) == AssemblyIdentityUtil.CanonicalName(name)) return module;
            module.Dispose();
            throw new InvalidOperationException("M04 diagnostic DLL name mismatch: " + path);
        }
    }
}
