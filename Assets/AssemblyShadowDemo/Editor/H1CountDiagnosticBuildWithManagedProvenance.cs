using System;
using System.IO;
using System.Text;
using HybridCLR.Editor.AssemblyShadow;
using HybridCLR.Editor.Commands;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>
    /// Bounded wrapper around the existing H1 diagnostic build. It freezes the
    /// managed source/configuration set before BuildPlayer and binds the actual
    /// captured Player DLLs afterwards without changing the existing build receipt.
    /// </summary>
    public static class H1CountDiagnosticBuildWithManagedProvenance
    {
        [Serializable]
        private sealed class ManagedLink
        {
            public int schemaVersion = 1;
            public string kind = "H1ManagedSourceProvenanceLink";
            public string buildReceiptPath, buildReceiptSha256;
            public string capturePath, captureSha256;
            public string buildGuid, inputSnapshotHash, nativeLibrarySha256, sourcePinSha256;
            public bool humanGatePassed = false, mayEnterR02 = false;
        }

        public static void BuildDiagnosticPlayer()
        {
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            bool featureEnabled = ParseFeature(AssemblyShadowBuildCommands.Argument("-shadowH1Feature", ""));
            string cpp = AssemblyShadowBuildCommands.Argument("-shadowH1Cpp", "");
            Require(cpp == "Debug" || cpp == "Release", "-shadowH1Cpp must be Debug or Release.");
            string baselineId = "H1Count-" + (featureEnabled ? "On" : "Off") + "-" + cpp;
            string receiptArg = AssemblyShadowBuildCommands.Argument("-shadowH1BuildReceipt", "");
            Require(!string.IsNullOrWhiteSpace(receiptArg) && Path.IsPathRooted(receiptArg),
                "The provenance wrapper requires an explicit absolute -shadowH1BuildReceipt.");
            string receiptPath = Path.GetFullPath(receiptArg);
            string preparation = RequiredArgument("-shadowH1PreparationRoot");
            string evidenceRoot = Path.Combine(Path.GetFullPath(preparation), "ManagedSourceProvenance");
            var settings = AssemblyShadowSettings.Instance;
            string[] defines = ShadowReflectionBindingEvidence.CompilationDefines(new[] {
                H1CountDiagnosticBuild.DiagnosticDefine, H1CountDiagnosticBuild.R01BDiagnosticsDefine });
            H1ManagedSourceProvenance.Context context = H1ManagedSourceProvenance.Begin(
                projectRoot, settings.sourcePinFile, baselineId, evidenceRoot, defines);

            H1CountDiagnosticBuild.BuildDiagnosticPlayer();

            Require(File.Exists(receiptPath), "The wrapped diagnostic build did not create its requested receipt.");
            string receiptSha = ShadowHash.File(receiptPath);
            var receipt = JsonUtility.FromJson<H1CountDiagnosticBuild.DiagnosticBuildReceipt>(File.ReadAllText(receiptPath));
            Require(receipt != null && receipt.baselineBuildId == baselineId && !string.IsNullOrWhiteSpace(receipt.inputSnapshot) &&
                !string.IsNullOrWhiteSpace(receipt.sourcePinSha256), "The wrapped build receipt is incomplete or belongs to another build.");
            AssemblySnapshotReceipt captured = AssemblySnapshot.ReadAndVerify(receipt.inputSnapshot, true);
            Require(captured.buildGuid == receipt.buildGuid && captured.snapshotHash == receipt.inputSnapshotHash &&
                captured.nativeLibrarySha256 == receipt.nativeLibrarySha256,
                "The wrapped build receipt and Player input snapshot differ.");
            string capturePath = H1ManagedSourceProvenance.End(context, receipt.inputSnapshot, captured, receipt.sourcePinSha256);
            string linkPath = Path.Combine(evidenceRoot, "managed-source-link.json");
            var link = new ManagedLink {
                buildReceiptPath = receiptPath, buildReceiptSha256 = receiptSha,
                capturePath = capturePath, captureSha256 = ShadowHash.File(capturePath),
                buildGuid = receipt.buildGuid, inputSnapshotHash = receipt.inputSnapshotHash,
                nativeLibrarySha256 = receipt.nativeLibrarySha256, sourcePinSha256 = receipt.sourcePinSha256,
            };
            WriteNew(linkPath, JsonUtility.ToJson(link, true));
            Debug.Log("[AssemblyShadow H1] Managed source provenance captured: " + capturePath);
        }

        private static bool ParseFeature(string value)
        {
            if (string.Equals(value, "on", StringComparison.OrdinalIgnoreCase)) return true;
            if (string.Equals(value, "off", StringComparison.OrdinalIgnoreCase)) return false;
            throw new InvalidOperationException("-shadowH1Feature must be on or off.");
        }

        private static string RequiredArgument(string name)
        {
            string[] args = Environment.GetCommandLineArgs();
            string result = null;
            for (int i = 0; i < args.Length; ++i)
                if (args[i] == name)
                {
                    Require(result == null && i + 1 < args.Length && !string.IsNullOrWhiteSpace(args[i + 1]),
                        "Missing or duplicate argument: " + name);
                    result = args[++i];
                }
            Require(result != null && Path.IsPathRooted(result), "Missing absolute argument: " + name);
            return result;
        }

        private static void WriteNew(string path, string text)
        {
            byte[] bytes = new UTF8Encoding(false).GetBytes(text);
            using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            { stream.Write(bytes, 0, bytes.Length); stream.Flush(true); }
        }

        private static void Require(bool condition, string message)
        { if (!condition) throw new InvalidOperationException(message); }
    }
}
