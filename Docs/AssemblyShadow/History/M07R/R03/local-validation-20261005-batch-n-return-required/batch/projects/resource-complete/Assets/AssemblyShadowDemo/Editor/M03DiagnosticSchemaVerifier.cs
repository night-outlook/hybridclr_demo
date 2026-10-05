using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Checks the actual linked JSON contract, not just Editor reflection.</summary>
    public static class M03DiagnosticSchemaVerifier
    {
        private const string RuntimeAssembly = "hybridclr.runtime";
        private const string RootType = "HybridCLR.AssemblyShadowDiagnostics";

        public static void Verify(string root, AssemblySnapshotReceipt receipt)
        {
            ShadowHash.Require(receipt != null && receipt.kind == "PlayerBuildInputs" &&
                receipt.sourcePins != null && receipt.snapshotHash == AssemblySnapshot.ComputeHash(receipt),
                "M03DiagnosticSnapshotMismatch", "Diagnostic schema needs a verified Player input snapshot.");
            ShadowLinkedPlayerEvidence.ReadAndVerify(root, receipt);
            var inputs = (receipt.assemblies ?? new SnapshotFile[0]).Where(file =>
                AssemblyIdentityUtil.CanonicalName(file.name) == RuntimeAssembly).ToArray();
            var linked = receipt.linkedPlayerReceipt.assemblies.Where(file =>
                AssemblyIdentityUtil.CanonicalName(file.name) == RuntimeAssembly).ToArray();
            ShadowHash.Require(inputs.Length == 1 && linked.Length == 1,
                "M03DiagnosticRuntimeMissing", "Exactly one prelink and linked HybridCLR.Runtime DLL is required.");
            string inputPath = ShadowHash.SafeChild(root, inputs[0].path);
            string linkedPath = ShadowHash.SafeChild(root, ShadowLinkedPlayerEvidence.DirectoryName + "/" + linked[0].path);
            byte[] inputBytes = File.ReadAllBytes(inputPath), linkedBytes = File.ReadAllBytes(linkedPath);
            ShadowHash.Require(ShadowHash.Bytes(inputBytes) == inputs[0].sha256 &&
                ShadowHash.Bytes(linkedBytes) == linked[0].sha256, "M03DiagnosticInputChanged",
                "Diagnostic comparison must use the captured prelink and linked bytes.");
            using (var inputModule = ModuleDefMD.Load(inputBytes))
            using (var linkedModule = ModuleDefMD.Load(linkedBytes)) VerifyModules(inputModule, linkedModule);
        }

        // Test seam compares real metadata, including mutations representing
        // stripping. Production callers must use the snapshot-bound entry above.
        internal static void VerifyModules(ModuleDef input, ModuleDef linked)
        {
            ShadowHash.Require(input != null && linked != null && input.Assembly != null && linked.Assembly != null &&
                AssemblyIdentityUtil.CanonicalName(input.Assembly.Name) == RuntimeAssembly &&
                input.Assembly.FullName == linked.Assembly.FullName, "M03DiagnosticRuntimeIdentity",
                "Diagnostic inputs must identify the same HybridCLR.Runtime assembly.");
            ShadowDiagnosticSchemaProof.Verify(input, linked, new[] { RootType }, "M03Diagnostic");
        }
    }
}
