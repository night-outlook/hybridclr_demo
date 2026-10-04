using System;
using System.IO;
using System.Linq;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    // Called only with the exact new snapshot returned by the original M07 gate.
    // Never scans for an older successful snapshot or repairs terminal evidence.
    public static class R03CompletionCompilerPolicyContract
    {
        [Serializable] private sealed class Report
        {
            public int schemaVersion = 1;
            public string kind = "R03ActualCompilerPolicyContract", result = "Failed", error;
            public string projectPath, baselineId, unityVersion, target, architecture, snapshot, snapshotSha256, compiledProofSha256;
            public R03CompilerPolicyChecks.Input[] before, after;
            public R03CompilerPolicyChecks.Observation observation;
            public bool unityEditorRun = true, originalCompilerPolicyPassed = true, capturedRawProofVerified;
            public bool linkedProofExecuted, runtimeAcceptance, expansionAuthorized, R03Accepted, H2Passed;
        }
        // All immutable policy JSON inputs, including explicit resource descriptors.
        private static readonly string[] Inputs = { R03CompilerPolicyChecks.RawPath, R03CompilerPolicyChecks.DependencyPath,
            "ProjectSettings/AssemblyShadowExtensibilityWhitelist.json", "ProjectSettings/AssemblyShadowReflectionBindings.json",
            "ProjectSettings/AssemblyShadowResources.json", "ProjectSettings/AssemblyShadowResourcesM07.json",
            "ProjectSettings/AssemblyShadowSourcePins.json", ".r03-completion-project" };
        private static R03CompilerPolicyChecks.Input[] Capture(string root) => Inputs.Select(p => new R03CompilerPolicyChecks.Input { path = p, sha256 = ShadowHash.File(Path.Combine(root,p)) }).ToArray();
        public static void Verify(string snapshot)
        {
            string project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            var marker = Newtonsoft.Json.Linq.JObject.Parse(File.ReadAllText(Path.Combine(project, ".r03-completion-project")));
            string root = (string)marker["receiptRoot"];
            R03CompilerPolicyChecks.Require((string)marker["projectPath"] == project && (string)marker["kind"] == "R03ResourceCompleteFixtureV1" &&
                !(bool)marker["expansionAuthorized"] && !(bool)marker["R03Accepted"] && !(bool)marker["H2Passed"], "Explicit non-authorizing project required.");
            R03CompilerPolicyChecks.Require(Path.GetFullPath(root).StartsWith(project + Path.DirectorySeparatorChar, StringComparison.Ordinal) &&
                Path.GetFullPath(snapshot).StartsWith(Path.Combine(project,"_temp","AssemblyShadow","M07CompilerPreflight-"),StringComparison.Ordinal), "Owned new compiler snapshot required.");
            var report = new Report { projectPath = project, baselineId = (string)marker["baselineId"], unityVersion = Application.unityVersion,
                target = EditorUserBuildSettings.activeBuildTarget.ToString(), architecture = AssemblyShadowSettings.Instance.architecture, snapshot = snapshot };
            try
            {
                report.before = Capture(project);
                var receipt = AssemblySnapshot.ReadAndVerify(snapshot, false);
                ShadowCompilerModeEvidence.ReadAndVerify(snapshot, true);
                var raw = ShadowRawTypeAdmissionEvidence.ReadAndVerify(snapshot, receipt, false);
                R03CompilerPolicyChecks.Require(raw != null && raw.sites.Length == 25 &&
                    ShadowHash.File(Path.Combine(snapshot,ShadowRawTypeAdmissionEvidence.ConfigurationPath)) == R03CompilerPolicyChecks.RawSha, "All 25 captured raw sites required.");
                report.capturedRawProofVerified = true;
                report.snapshotSha256 = ShadowHash.File(Path.Combine(snapshot,AssemblySnapshot.ReceiptName));
                report.compiledProofSha256 = ShadowHash.File(Path.Combine(snapshot,ShadowRawTypeAdmissionEvidence.CompiledProofPath));
                report.observation = R03CompilerPolicyChecks.Run(project, snapshot, Path.Combine(root,"compiler-policy-controls"), "Development");
                report.after = Capture(project);
                R03CompilerPolicyChecks.Require(report.before.Select(p=>p.sha256).SequenceEqual(report.after.Select(p=>p.sha256)), "Input mutation during controls.");
                report.result = "Passed";
            }
            catch (Exception error) { report.error = error.ToString(); throw; }
            finally { R03CompilerPolicyChecks.Write(Path.Combine(root,"compiler-policy-contract.json"), Newtonsoft.Json.JsonConvert.SerializeObject(report, Newtonsoft.Json.Formatting.Indented)); }
        }
    }
}
