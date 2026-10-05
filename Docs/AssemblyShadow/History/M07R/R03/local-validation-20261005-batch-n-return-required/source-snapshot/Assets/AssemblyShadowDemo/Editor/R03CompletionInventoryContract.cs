using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using HybridCLR.Editor.AssemblyShadow;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.Compilation;
using UnityEngine;
using CompilerAssembly = UnityEditor.Compilation.Assembly;

namespace AssemblyShadowDemo.Editor
{
    // Actual target inventory/production policy contract; no substitute inventory
    // is used for the positive case. Negative inventories/settings are named copies.
    public static class R03CompletionInventoryContract
    {
        private static readonly Dictionary<string, string> Packages = new Dictionary<string, string> {
            {"com.unity.burst","1.8.21"}, {"com.unity.mathematics","1.2.6"}, {"com.unity.ext.nunit","1.0.6"},
            {"com.unity.nuget.newtonsoft-json","3.2.1"}, {"com.unity.render-pipelines.core","14.0.12"},
            {"com.unity.render-pipelines.universal","14.0.12"}, {"com.unity.render-pipelines.universal-config","14.0.10"},
            {"com.unity.searcher","4.9.2"}, {"com.unity.shadergraph","14.0.12"},
            {"com.unity.test-framework","1.1.33"}, {"com.unity.ugui","1.0.0"} };
        internal static void ValidatePackages(string project)
        {
            var manifest = (JObject)JObject.Parse(File.ReadAllText(Path.Combine(project,"Packages/manifest.json")))["dependencies"];
            var locked = (JObject)JObject.Parse(File.ReadAllText(Path.Combine(project,"Packages/packages-lock.json")))["dependencies"];
            Require(manifest != null && locked != null, "Complete package manifest and lock required.");
            string[] names = manifest.Properties().Select(p => p.Name).OrderBy(n => n, StringComparer.Ordinal).ToArray();
            Require(names.SequenceEqual(locked.Properties().Select(p => p.Name).OrderBy(n => n, StringComparer.Ordinal)), "Resolved package set differs from reviewed scope.");
            Require(names.Where(n => !n.StartsWith("com.unity.modules.", StringComparison.Ordinal)).SequenceEqual(
                Packages.Keys.Concat(new[] {"com.code-philosophy.hybridclr"}).OrderBy(n => n, StringComparer.Ordinal)), "Unreviewed package added or removed.");
            foreach (string name in names)
            {
                string expected = name.StartsWith("com.unity.modules.", StringComparison.Ordinal) ? "1.0.0" :
                    name == "com.code-philosophy.hybridclr" ? (string)manifest[name] : Packages[name];
                Require((string)manifest[name] == expected && (string)locked[name]["version"] == expected, "Package version drift: " + name);
            }
        }
        [Serializable] private sealed class Input { public string path, sha256; }
        [Serializable] private sealed class FileInput { public string path, sha256; public long size; }
        [Serializable] private sealed class CompilerRow
        { public string mode, name, outputPath, flags; public string[] sourceFiles, assemblyReferences, compiledReferences; }
        [Serializable] private sealed class Cap
        {
            public string name, classification;
            public bool isPrecompiled, isShadowCapable, isBootstrap, capabilityDeclared;
        }
        [Serializable] private sealed class Declaration { public string name; public bool included, present, isShadowCapable; }
        [Serializable] private sealed class Case { public string id, path, sha256, expectedCode, observedCode, result; }
        [Serializable] private sealed class Control { public string settingsJson; public AssemblyCapability[] inventory; public string[] normalHotUpdates; }
        [Serializable] private sealed class Report
        {
            public int schemaVersion = 1;
            public string kind = "R03ActualTargetCapabilityContract", result = "Failed", profile = R03ResourceCapabilityProfile.Id;
            public string consumer = "AssemblyShadowSettingsUtil.CreatePolicyConfiguration/BuildCompilerInventory/BuildCapabilities";
            public string projectPath, baselineId, unityVersion, target, architecture, error, policyJson;
            public bool unityEditorRun = true, configurationOccurred, snapshotCompilationRun, expansionAuthorized, R03Accepted, H2Passed;
            public Input[] before, after, sourceFiles;
            public CompilerRow[] compilerAssemblies;
            public FileInput[] referenceFiles;
            public Cap[] inventory;
            public Declaration[] declarations;
            public List<Case> cases = new List<Case>();
        }
        private static readonly string[] Inputs = {"Packages/manifest.json", "Packages/packages-lock.json",
            "ProjectSettings/AssemblyShadowSettings.asset", "ProjectSettings/ProjectSettings.asset",
            "ProjectSettings/AssemblyShadowSourcePins.json", ".r03-completion-project"};
        private static Input[] Capture(string project, IEnumerable<string> paths) => paths.Select(p => new Input {path=p, sha256=ShadowHash.File(Path.Combine(project,p))}).ToArray();
        private static Cap Row(AssemblyCapability c) => new Cap { name=c.name,classification=c.classification.ToString(),
            isPrecompiled=c.isPrecompiled,isShadowCapable=c.isShadowCapable,isBootstrap=c.isBootstrap,capabilityDeclared=c.capabilityDeclared };
        private static MethodInfo Core(string name, params Type[] types)
        {
            var method=typeof(AssemblyShadowSettingsUtil).GetMethod(name,BindingFlags.Static|BindingFlags.NonPublic,null,types,null);
            Require(method != null, "Exact production core signature changed: " + name); return method;
        }
        private static T Invoke<T>(MethodInfo method, params object[] values)
        {
            try { return (T)method.Invoke(null,values); }
            catch (TargetInvocationException error) { if (error.InnerException != null) throw error.InnerException; throw; }
        }
        public static void Verify()
        {
            using (R03CompletionBuild.BeginCapabilityScope()) Run();
        }
        private static void Run()
        {
            string project=Path.GetFullPath(Path.Combine(Application.dataPath,".."));
            var marker=JObject.Parse(File.ReadAllText(Path.Combine(project,".r03-completion-project")));
            string root=(string)marker["receiptRoot"], destination=Path.Combine(root,"capability-contract.json");
            string controls=Path.Combine(root,"capability-inputs");
            Require(!File.Exists(destination) && !Directory.Exists(controls), "New capability output required.");
            Directory.CreateDirectory(controls);
            var report=new Report {projectPath=project,baselineId=(string)marker["baselineId"],unityVersion=Application.unityVersion,
                target=EditorUserBuildSettings.activeBuildTarget.ToString(),architecture="arm64"};
            try
            {
                ValidatePackages(project);
                M07Build.Configure(); // Named, permitted configuration; not hidden as a read-only operation.
                report.configurationOccurred=true; report.before=Capture(project,Inputs);
                report.sourceFiles=Capture(Path.Combine(project,"Assets/AssemblyShadowDemo/Editor"), new[] {"R03ResourceCapabilityProfile.cs","R03CompletionInventoryContract.cs","M02Build.cs"});
                var player=CompilationPipeline.GetAssemblies(AssembliesType.Player);
                var production=CompilationPipeline.GetAssemblies(AssembliesType.PlayerWithoutTestAssemblies);
                Require(player != null && production != null, "Both actual active-target compiler inventories required.");
                report.compilerAssemblies=CaptureAssemblies(player,"Player").Concat(CaptureAssemblies(production,"PlayerWithoutTestAssemblies")).ToArray();
                report.referenceFiles=report.compilerAssemblies.SelectMany(a=>a.compiledReferences).Distinct(StringComparer.Ordinal).OrderBy(p=>p,StringComparer.Ordinal)
                    .Select(p=>new FileInput {path=p,sha256=ShadowHash.File(p),size=new FileInfo(p).Length}).ToArray();
                string unityRoot=Path.GetFullPath(EditorApplication.applicationContentsPath).TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar;
                Func<string,bool> framework=p=>Path.GetFullPath(p).StartsWith(unityRoot,StringComparison.Ordinal);
                var inventory=Invoke<AssemblyCapability[]>(Core("BuildCompilerInventory",typeof(CompilerAssembly[]),typeof(CompilerAssembly[]),typeof(Func<string,bool>)),player,production,framework);
                report.inventory=inventory.Select(Row).ToArray();
                report.declarations=M02Build.InheritedPrecompiledCapabilities().Select(c=>new Declaration {name=c.name,
                    included=R03ResourceCapabilityProfile.Included.Contains(c.name),present=inventory.Any(i=>i.name==c.name),isShadowCapable=c.isShadowCapable}).ToArray();
                Require(report.declarations.Length==5 && report.declarations.All(d=>d.included==d.present && !d.isShadowCapable), "All inherited declaration dispositions must match actual inventory.");
                var settings=AssemblyShadowSettings.Instance;
                Require(settings.precompiledAssemblyCapabilities.Select(c=>c.name).SequenceEqual(R03ResourceCapabilityProfile.Included), "Exact scoped declarations required.");
                Require(settings.precompiledAssemblyNames.Length==0 && settings.rejectUnknownReflectionDependencies && settings.enforceResourceAbi, "No extra capability or policy bypass.");
                var policy=AssemblyShadowSettingsUtil.CreatePolicyConfiguration(EditorUserBuildSettings.activeBuildTarget);
                ShadowAssemblyPolicyValidator.ValidateBeforeCompile(policy,EditorUserBuildSettings.activeBuildTarget).ThrowIfInvalid();
                report.policyJson=JsonUtility.ToJson(policy,true);
                foreach(string name in R03ResourceCapabilityProfile.Included)
                {
                    var cap=policy.assemblies.Single(c=>c.name==name);
                    Require(cap.isPrecompiled && cap.capabilityDeclared && !cap.isShadowCapable && !cap.isBootstrap && cap.classification==AssemblyClassification.Runtime, "Required fixed plugin classification: "+name);
                }
                string[] normal=policy.assemblies.Where(c=>c.classification==AssemblyClassification.NormalHotUpdate).Select(c=>c.name).ToArray();
                var core=Core("BuildCapabilities",typeof(AssemblyShadowSettings),typeof(IEnumerable<AssemblyCapability>),typeof(IEnumerable<string>));
                Check(report,controls,core,"scoped-policy","Success",settings,inventory,normal,settings.precompiledAssemblyCapabilities);
                Check(report,controls,core,"original-inherited","UnknownPrecompiledCapability",settings,inventory,normal,M02Build.InheritedPrecompiledCapabilities());
                Check(report,controls,core,"excluded-collections","UnknownPrecompiledCapability",settings,inventory,normal,Plus(settings,"Unity.Collections.LowLevel.ILSupport"));
                Check(report,controls,core,"excluded-antlr","UnknownPrecompiledCapability",settings,inventory,normal,Plus(settings,"Unity.VisualScripting.Antlr3.Runtime"));
                Check(report,controls,core,"unknown-plugin","UnknownPrecompiledCapability",settings,inventory,normal,Plus(settings,"R03.Absent.Control"));
                Check(report,controls,core,"source-as-plugin","InvalidPrecompiledCapability",settings,inventory,normal,Plus(settings,"AssemblyA.Contracts"));
                string reference=inventory.First(c=>c.classification==AssemblyClassification.Reference && !c.isPrecompiled).name;
                Check(report,controls,core,"framework-as-plugin","InvalidPrecompiledCapability",settings,inventory,normal,Plus(settings,reference));
                var altered=inventory.Select(c=>new AssemblyCapability {name=c.name,classification=c.name=="Newtonsoft.Json"?AssemblyClassification.EditorOnly:c.classification,isPrecompiled=c.isPrecompiled}).ToArray();
                Check(report,controls,core,"nonruntime-plugin","InvalidCapabilityClassification",settings,altered,normal,settings.precompiledAssemblyCapabilities);
                string[] ordinary=normal.Concat(new[]{"Newtonsoft.Json"}).Distinct(StringComparer.Ordinal).ToArray();
                Check(report,controls,core,"ordinary-fixed-plugin","Success",settings,inventory,ordinary,settings.precompiledAssemblyCapabilities);
                var shadow=settings.precompiledAssemblyCapabilities.Select(c=>new AssemblyCapability{name=c.name,isShadowCapable=c.name=="Newtonsoft.Json"}).ToArray();
                Check(report,controls,core,"ordinary-shadow-plugin","InvalidCapabilityClassification",settings,inventory,ordinary,shadow);
                report.after=Capture(project,Inputs);
                Require(report.before.Select(i=>i.sha256).SequenceEqual(report.after.Select(i=>i.sha256)), "Policy controls mutated configured inputs.");
                report.result="Passed";
            }
            catch(Exception error) {report.error=error.ToString();throw;}
            finally {report.after=Capture(project,Inputs);M04AssemblyIdentityProof.WriteNewJson(destination,report);}
        }
        private static AssemblyCapability[] Plus(AssemblyShadowSettings settings,string name) => settings.precompiledAssemblyCapabilities.Concat(new[]{new AssemblyCapability{name=name}}).ToArray();
        private static CompilerRow[] CaptureAssemblies(CompilerAssembly[] assemblies,string mode) => assemblies.OrderBy(a=>a.name,StringComparer.Ordinal).Select(a=>new CompilerRow {
            mode=mode,name=a.name,outputPath=Path.GetFullPath(a.outputPath),flags=a.flags.ToString(),
            sourceFiles=(a.sourceFiles??new string[0]).Select(Path.GetFullPath).OrderBy(p=>p,StringComparer.Ordinal).ToArray(),
            assemblyReferences=(a.assemblyReferences??new CompilerAssembly[0]).Select(r=>r.name).OrderBy(n=>n,StringComparer.Ordinal).ToArray(),
            compiledReferences=(a.compiledAssemblyReferences??new string[0]).Select(Path.GetFullPath).OrderBy(p=>p,StringComparer.Ordinal).ToArray() }).ToArray();
        private static void Check(Report report,string root,MethodInfo core,string id,string expected,AssemblyShadowSettings settings,
            AssemblyCapability[] inventory,string[] normal,AssemblyCapability[] declarations)
        {
            var clone=ScriptableObject.CreateInstance<AssemblyShadowSettings>();
            try
            {
                JsonUtility.FromJsonOverwrite(JsonUtility.ToJson(settings),clone);clone.precompiledAssemblyCapabilities=declarations;
                string path=Path.Combine(root,id+".json");
                M04AssemblyIdentityProof.WriteNewJson(path,new Control {settingsJson=JsonUtility.ToJson(clone),inventory=inventory,normalHotUpdates=normal});
                var row=new Case {id=id,path=path,sha256=ShadowHash.File(path),expectedCode=expected,observedCode="Success",result="Failed"};report.cases.Add(row);
                try {Invoke<AssemblyCapability[]>(core,clone,inventory,normal);}
                catch(ShadowBuildException error) {row.observedCode=error.Code;}
                Require(row.observedCode==expected,id+": expected "+expected+", got "+row.observedCode);row.result="Passed";
            }
            finally {UnityEngine.Object.DestroyImmediate(clone);}
        }
        private static void Require(bool condition,string message) {ShadowHash.Require(condition,"R03ResourceCapabilityContract",message);}
    }
}
