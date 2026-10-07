using System;
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    // A real Unity JsonUtility -> production Read contract, executed before
    // Configure/Install. Negative inputs are new files; never mutate live pins.
    public static class R03CompletionSourcePinContract
    {
        [Serializable] private sealed class Revisions { public string hybridclr, hybridclr_unity, il2cpp_plus, hybridclr_demo; }
        [Serializable] private sealed class Authority
        {
            public int schemaVersion;
            public string kind, projectPath, baselineId, receiptRoot;
            public bool expansionAuthorized, R03Accepted, H2Passed;
            public Revisions repositories;
        }
        public static void Verify()
        {
            string project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            var value = JsonUtility.FromJson<Authority>(File.ReadAllText(Path.Combine(project, ".r03-completion-project")));
            ShadowHash.Require(value != null && value.schemaVersion == 1 && value.kind == "R03ResourceCompleteFixtureV1" &&
                value.projectPath == project && !value.expansionAuthorized && !value.R03Accepted && !value.H2Passed,
                "SourcePinPreflightAuthority", "Exact isolated project required.");
            ShadowHash.Require(Application.unityVersion == "2022.3.62f2" && EditorUserBuildSettings.activeBuildTarget == BuildTarget.StandaloneOSX &&
                AssemblyShadowBuildCommands.Argument("-shadowBaselineId", "") == value.baselineId,
                "SourcePinPreflightAuthority", "Pinned platform/baseline required.");
            string prefix = Path.Combine(project, "_temp", "AssemblyShadow") + Path.DirectorySeparatorChar;
            ShadowHash.Require(Path.GetFullPath(value.receiptRoot).StartsWith(prefix, StringComparison.Ordinal),
                "SourcePinPreflightAuthority", "Receipt directory escaped isolated fixture.");
            Run(project, value.baselineId, value.receiptRoot);
        }
        [Serializable] private sealed class Input { public string path, sha256; }
        [Serializable] private sealed class Case { public string id, path, sha256, expectedCode, observedCode, result; }
        [Serializable] private sealed class Report
        {
            public int schemaVersion = 1;
            public string kind = "R03ProductionSourcePinContract", result = "Failed", projectPath, baselineId;
            public string unityVersion, target, architecture, runtimeAbiHash, error;
            public string consumer = "HybridCLR.Editor.AssemblyShadow.ShadowSourcePins.Read", serialization = "UnityEngine.JsonUtility";
            public bool unityEditorRun = true, nativeInstallationRun, expansionAuthorized, R03Accepted, H2Passed;
            public Input[] before, after;
            public List<Case> cases = new List<Case>();
        }
        private static readonly string[] Inputs = { "ProjectSettings/AssemblyShadowSourcePins.json", "ProjectSettings/AssemblyShadowSettings.asset",
            "ProjectSettings/ProjectSettings.asset", ".r03-completion-project" };
        private static Input[] Capture(string project)
        {
            var list = new List<Input>();
            foreach (string path in Inputs) list.Add(new Input { path = path, sha256 = ShadowHash.File(Path.Combine(project, path)) });
            return list.ToArray();
        }
        internal static void Run(string project, string baseline, string receiptRoot)
        {
            string destination = Path.Combine(receiptRoot, "source-pin-contract.json");
            string controls = Path.Combine(receiptRoot, "source-pin-contract-inputs");
            ShadowHash.Require(!File.Exists(destination) && !Directory.Exists(controls), "SourcePinPreflightReuse", "New contract output required.");
            Directory.CreateDirectory(controls);
            var report = new Report { projectPath = project, baselineId = baseline, unityVersion = Application.unityVersion,
                target = EditorUserBuildSettings.activeBuildTarget.ToString(), architecture = "arm64", before = Capture(project) };
            try
            {
                string path = Path.Combine(project, Inputs[0]);
                var actual = ReadCase(report, "generated", path, "Success");
                var expected = JsonUtility.FromJson<Authority>(File.ReadAllText(Path.Combine(project, ".r03-completion-project")));
                ShadowHash.Require(expected != null && expected.repositories != null, "SourcePinPreflightAuthority", "Owning source tuple required.");
                RequirePin(actual.demo, "hybridclr_demo", expected.repositories.hybridclr_demo);
                RequirePin(actual.hybridclr, "hybridclr", expected.repositories.hybridclr);
                RequirePin(actual.hybridclrUnity, "hybridclr_unity", expected.repositories.hybridclr_unity);
                RequirePin(actual.il2cppPlus, "il2cpp_plus", expected.repositories.il2cpp_plus);
                report.runtimeAbiHash = actual.RuntimeAbiHash();
                string valid = JsonUtility.ToJson(actual, false);
                WriteCase(report, controls, "roundtrip", valid, "Success", actual);
                var regex = new Regex("\\\"architecture\\\":\\\"arm64\\\",");
                ShadowHash.Require(regex.Matches(valid).Count == 1, "SourcePinPreflightShape", "Unambiguous architecture control required.");
                WriteCase(report, controls, "missing-architecture", regex.Replace(valid, "", 1), "SourcePinTarget");
                Mutate(report, controls, valid, "wrong-architecture", p => p.architecture = "x64", "SourcePinTarget");
                Mutate(report, controls, valid, "wrong-target", p => p.target = "StandaloneWindows64", "SourcePinTarget");
                Mutate(report, controls, valid, "wrong-unity", p => p.unityVersion = "wrong", "SourcePinTarget");
                Mutate(report, controls, valid, "wrong-schema", p => p.schemaVersion = 2, "SourcePinSchema");
                Mutate(report, controls, valid, "bad-revision", p => p.demo.revision = "bad", "InvalidSourcePin");
                Mutate(report, controls, valid, "missing-repository", p => p.hybridclr = null, "InvalidSourcePin");
                var changed = JsonUtility.FromJson<ShadowSourcePins>(valid);
                changed.demo.revision = actual.demo.revision == new string('0', 40) ? new string('1', 40) : new string('0', 40);
                WriteCase(report, controls, "wrong-build-source", JsonUtility.ToJson(changed), "BuildSourceProvenanceMismatch", actual);
                report.after = Capture(project);
                for (int i = 0; i < report.before.Length; i++)
                    ShadowHash.Require(report.before[i].sha256 == report.after[i].sha256, "SourcePinPreflightMutation", report.before[i].path);
                report.result = "Passed";
            }
            catch (Exception ex) { report.error = ex.ToString(); throw; }
            finally
            {
                report.after = Capture(project);
                M04AssemblyIdentityProof.WriteNewJson(destination, report);
            }
        }
        private static void RequirePin(ShadowRepositoryPin pin, string repository, string revision)
        {
            ShadowHash.Require(pin != null && pin.revision == revision && pin.url == "https://github.com/night-outlook/" + repository + ".git" &&
                !string.IsNullOrWhiteSpace(pin.localPath), "SourcePinPreflightAuthority", "Exact owning source " + repository);
        }
        private static ShadowSourcePins ReadCase(Report report, string id, string path, string code, ShadowSourcePins baseline = null)
        {
            var row = new Case { id = id, path = path, sha256 = ShadowHash.File(path), expectedCode = code, observedCode = "Success", result = "Failed" };
            report.cases.Add(row);
            ShadowSourcePins value = null;
            try { value = ShadowSourcePins.Read(path, BuildTarget.StandaloneOSX, "arm64"); if (baseline != null) ShadowSourcePins.RequireSameBuildSources(baseline, value); }
            catch (ShadowBuildException ex) { row.observedCode = ex.Code; }
            ShadowHash.Require(row.observedCode == code, "SourcePinPreflightContract", id + ": expected " + code + ", got " + row.observedCode);
            row.result = "Passed";
            return value;
        }
        private static void WriteCase(Report report, string root, string id, string json, string code, ShadowSourcePins baseline = null)
        {
            string path = Path.Combine(root, id + ".json");
            using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(stream)) writer.Write(json);
            ReadCase(report, id, path, code, baseline);
        }
        private static void Mutate(Report report, string root, string valid, string id, Action<ShadowSourcePins> mutation, string code)
        {
            var value = JsonUtility.FromJson<ShadowSourcePins>(valid); mutation(value);
            WriteCase(report, root, id, JsonUtility.ToJson(value, false), code);
        }
    }
}
