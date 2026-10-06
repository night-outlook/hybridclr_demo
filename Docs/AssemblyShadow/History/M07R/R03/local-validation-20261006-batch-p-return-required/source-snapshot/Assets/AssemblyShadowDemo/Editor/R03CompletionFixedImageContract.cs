using System;
using System.IO;
using System.Linq;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    // Executes the original image reader and shared guard checks in real Unity.
    // Neither controls nor observation are permitted to edit the live inputs.
    public static class R03CompletionFixedImageContract
    {
        [Serializable] private sealed class Authority
        {
            public int schemaVersion;
            public string kind, projectPath, baselineId, receiptRoot, fixedImageProfile;
            public bool expansionAuthorized, R03Accepted, H2Passed;
        }
        [Serializable] private sealed class Input { public string path, sha256; }
        [Serializable] private sealed class Report
        {
            public int schemaVersion = 1;
            public string kind = "R03ActualFixedImageContract", result = "Failed", projectPath, baselineId;
            public string unityVersion, target, architecture = "arm64", error;
            public bool unityEditorRun = true, actualProjectImageValidator, snapshotCompilationRun;
            public bool runtimeAcceptance, expansionAuthorized, R03Accepted, H2Passed;
            public Input[] before, after, sources;
            public R03FixedImageChecks.Observation observation;
        }
        private static readonly string[] Inputs = {
            "ProjectSettings/AssemblyShadowReflectionBindings.json", R03FixedImageChecks.ImagePath,
            "ProjectSettings/AssemblyShadowSourcePins.json", ".r03-completion-project",
            "_temp/AssemblyShadow/R03CompletionFixedImage/preparation.json",
            "Tools/AssemblyShadow/R02/fixtures/m00-frozen.dll.zlib.base64.txt",
            "Tools/AssemblyShadow/R02/fixtures/m00-origin.json" };
        private static readonly string[] Sources = {
            "Assets/AssemblyShadowDemo/Editor/R03FixedImageChecks.cs",
            "Assets/AssemblyShadowDemo/Editor/R03CompletionFixedImageContract.cs" };
        private static Input[] Capture(string project, string[] paths)
        { return paths.Select(path => new Input {path=path,sha256=ShadowHash.File(Path.Combine(project,path))}).ToArray(); }
        public static void Verify()
        {
            string project=Path.GetFullPath(Path.Combine(Application.dataPath,".."));
            var authority=JsonUtility.FromJson<Authority>(File.ReadAllText(Path.Combine(project,".r03-completion-project")));
            Require(authority!=null && authority.schemaVersion==1 && authority.kind=="R03ResourceCompleteFixtureV1" &&
                authority.projectPath==project && authority.fixedImageProfile==R03FixedImageChecks.Profile &&
                !authority.expansionAuthorized && !authority.R03Accepted && !authority.H2Passed, "Invalid exact project authority.");
            Require(Application.unityVersion=="2022.3.62f2" && EditorUserBuildSettings.activeBuildTarget==BuildTarget.StandaloneOSX &&
                AssemblyShadowBuildCommands.Argument("-shadowBaselineId","")==authority.baselineId && Path.GetFullPath(".")==project,
                "Exact Unity/target/baseline/working directory required.");
            string root=Path.Combine(project,"_temp/AssemblyShadow/R03CompletionArtifacts");
            Require(authority.receiptRoot==root, "Exact owned output root required.");
            Directory.CreateDirectory(root);
            string destination=Path.Combine(root,"fixed-image-contract.json");
            Require(!File.Exists(destination), "Unused fixed-image receipt required.");
            var report=new Report {projectPath=project,baselineId=authority.baselineId,unityVersion=Application.unityVersion,
                target=EditorUserBuildSettings.activeBuildTarget.ToString()};
            try
            {
                report.before=Capture(project,Inputs); report.sources=Capture(project,Sources);
                ShadowReflectionBindingEvidence.ValidateProjectImages(); report.actualProjectImageValidator=true;
                report.observation=R03FixedImageChecks.Run(project,Path.Combine(root,"fixed-image-controls"));
                R03FixedImageChecks.RequirePinnedSemantics(report.observation);
                report.after=Capture(project,Inputs);
                Require(report.before.Select(v=>v.sha256).SequenceEqual(report.after.Select(v=>v.sha256)), "Fixed input mutation.");
                report.result="Passed";
            }
            catch (Exception error) { report.error=error.ToString(); throw; }
            finally
            {
                report.after=Capture(project,Inputs);
                M04AssemblyIdentityProof.WriteNewJson(destination,report);
            }
        }
        private static void Require(bool value,string message)
        { if(!value)throw new InvalidOperationException("R03FixedImageContract: "+message); }
    }
}
