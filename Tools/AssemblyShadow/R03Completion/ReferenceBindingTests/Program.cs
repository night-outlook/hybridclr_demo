using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;
#if HOST_REFERENCE
using System.Text.Json;
#else
using Newtonsoft.Json;
#endif

// Uses actual loader, hasher and eligibility code. Captured reference catalog
// below is a DIAGNOSTIC replay policy, never a minted live Unity authority.
internal static class Program
{
    [Serializable] public sealed class FileRow { public string path, sha256, name; public long size; public bool referenceOnly, framework; }
    [Serializable] public sealed class World { public string name, root, receiptSha256; public FileRow[] files; }
    [Serializable] public sealed class Inputs { public string kind, basis; public World[] worlds; }
    [Serializable] public sealed class Case { public string id, result, error; }
    [Serializable] public sealed class Report {
        public string kind="R03ReferenceBindingContracts",result="Failed",basis="ReusedAuditedLocalNCompilerInputs";
        public int schemaVersion=1,failures; public List<Case> cases=new List<Case>();
        public bool runtimeAcceptance,qualificationApproved,expansionAuthorized,unityEditorRun,playerRun;
    }
    static string output; static Report report=new Report();
    static void Need(bool ok,string text) { if(!ok) throw new InvalidOperationException(text); }
    static string Json(object value) {
#if HOST_REFERENCE
        return JsonSerializer.Serialize(value,new JsonSerializerOptions{IncludeFields=true,WriteIndented=true});
#else
        return JsonConvert.SerializeObject(value,Formatting.Indented);
#endif
    }
    static T Read<T>(string path) {
#if HOST_REFERENCE
        return JsonSerializer.Deserialize<T>(File.ReadAllText(path),new JsonSerializerOptions{IncludeFields=true});
#else
        return JsonConvert.DeserializeObject<T>(File.ReadAllText(path));
#endif
    }
    static void Save(string path,object value) { File.WriteAllText(Path.Combine(output,path),Json(value)+"\n"); }
    static void Test(string id,Action action) {try{action();report.cases.Add(new Case{id=id,result="Passed"});}catch(Exception e){report.failures++;report.cases.Add(new Case{id=id,result="Failed",error=e.ToString()});Console.Error.WriteLine(id+" "+e);}}
    static void Reject(Action action) {try{action();}catch(ShadowBuildException e){Need(e.Code=="EligibilityInputChanged",e.ToString());return;}throw new Exception("Mutation was accepted");}
    static void Authenticate(World w) {
        Need(w.files.Length>100 && w.files.Select(f=>f.name.ToLowerInvariant()).Distinct().Count()==w.files.Length,"Exact complete domain");
        foreach(var f in w.files) Need(File.Exists(f.path)&&new FileInfo(f.path).Length==f.size&&ShadowHash.File(f.path)==f.sha256,"Changed captured file: "+f.path);
    }
    static VerifiedTargetFrameworkReferences Policy(World w) {
        var providers=new Dictionary<string,string>(StringComparer.Ordinal);
        foreach(var f in w.files.Where(f=>f.framework)) using(var m=ModuleDefMD.Load(File.ReadAllBytes(f.path))) providers.Add(m.Assembly.FullName,f.sha256);
        Need(providers.Count>0,"Captured diagnostic framework context is explicit");
        var ctor=typeof(VerifiedTargetFrameworkReferences).GetConstructors(BindingFlags.NonPublic|BindingFlags.Instance).Single();
        return (VerifiedTargetFrameworkReferences)ctor.Invoke(new object[]{"2022.3.62f2","StandaloneOSX","arm64","NET_Standard_2_0",w.receiptSha256,providers});
    }
    static CompiledAssemblySet Load(World w) { Authenticate(w);return DnlibAssemblyLoader.Load(Path.Combine(w.root,"Assemblies"),new[]{Path.Combine(w.root,"References")},new AssemblyCapability[0],false,Policy(w)); }
    static PureInterpreterEligibilityReport Analyze(CompiledAssemblySet s) {return PureInterpreterEligibility.Analyze(s,s,null,null,new ResourceAbiDescriptor());}
    static string[] Sections(SemanticHashReport a,SemanticHashReport b) {return new[]{"identity","types","methods","attributes","resources"}.Where(n=>(string)a.sections.GetType().GetField(n).GetValue(a.sections)!=(string)b.sections.GetType().GetField(n).GetValue(b.sections)).ToArray();}
    static object Differences(ModuleDef isolated,ModuleDef closed,string[] sections) {
        var rows=new List<object>();
        foreach(var name in sections) {
            string method="Write"+char.ToUpperInvariant(name[0])+name.Substring(1);
            var m=typeof(AssemblySemanticHasher).GetMethod(method,BindingFlags.NonPublic|BindingFlags.Static);
            object[] Args(ModuleDef x) { return m.GetParameters().Length==1?new object[]{x}:new object[]{x,new SemanticHashOptions()}; }
            string a=(string)m.Invoke(null,Args(isolated)),b=(string)m.Invoke(null,Args(closed));int i=0;
            while(i<Math.Min(a.Length,b.Length)&&a[i]==b[i])i++;
            rows.Add(new{section=name,firstDifferentCharacter=i,isolatedLength=a.Length,closedLength=b.Length,
                isolatedExcerpt=a.Substring(Math.Max(0,i-120),Math.Min(a.Length-Math.Max(0,i-120),1200)),
                closedExcerpt=b.Substring(Math.Max(0,i-120),Math.Min(b.Length-Math.Max(0,i-120),1200))});
        }return rows;
    }
    static int Main(string[] args) {
        Need(args.Length==4&&args[0]=="--input"&&args[2]=="--output","Explicit input and new output");
        output=Path.GetFullPath(args[3]);Need(!Directory.Exists(output)&&!File.Exists(output),"Unused output");Directory.CreateDirectory(output);
        var inputs=Read<Inputs>(args[1]);Need(inputs.kind=="R03NReferenceInputs"&&inputs.basis=="ReusedAuditedLocalNCompilerInputs"&&inputs.worlds.Length==6,"Exact six captured input worlds");
        foreach(var w in inputs.worlds) Test("N-"+w.name+"-unchanged-closed-domain",()=>{using(var s=Load(w)){var a=Analyze(s);var b=Analyze(s);Need(Json(a)==Json(b)&&!a.qualificationApproved&&!a.expansionAuthorized,"Identical closed replay without authority");Save(w.name+"-unchanged.json",a);}Authenticate(w);});
        var first=inputs.worlds[0];
        Test("N-reference-context-diagnosis",()=>{using(var set=Load(first)) {
            var row=first.files.Single(f=>f.name.Equals("UnityEngine.AnimationModule",StringComparison.OrdinalIgnoreCase));
            var closed=set.GetModule(row.name);using(var isolated=ModuleDefMD.Load(File.ReadAllBytes(row.path))) {
                var a=AssemblySemanticHasher.Compute(isolated);var b=AssemblySemanticHasher.Compute(closed);var sections=Sections(a,b);
                Need(a.semanticHash!=b.semanticHash&&sections.Length>0,"The recorded context-dependent mismatch must reproduce");
                Save("reference-context-diagnosis.json",new{source=row,isolated=a,closed=b,differences=Differences(isolated,closed,sections),
                    oldUncontextualizedComparison="Rejected",repairedClosedComparison="Passed",runtimeAcceptance=false});
            }
        }});
        Test("N-reference-type-mutation",()=>{using(var s=Load(first)){s.GetModule("UnityEngine.AnimationModule").Types.First(t=>!t.IsGlobalModuleType).Name+="Changed";Reject(()=>Analyze(s));}});
        Test("N-reference-method-mutation",()=>{using(var s=Load(first)){var m=s.GetModule("UnityEngine.AnimationModule").GetTypes().SelectMany(t=>t.Methods).First();m.Name+="Changed";Reject(()=>Analyze(s));}});
        Test("N-reference-attribute-mutation",()=>{using(var s=Load(first)){var m=s.GetModule("UnityEngine.AnimationModule");Need(m.Assembly.CustomAttributes.Count>0,"Attribute witness");m.Assembly.CustomAttributes.Clear();Reject(()=>Analyze(s));}});
        Test("N-primary-and-descriptor-mutation",()=>{using(var s=Load(first)){var d=s.Assemblies.Values.First();var m=s.GetModule(d.name);m.Types.First(t=>!t.IsGlobalModuleType).Name+="Changed";d.semanticHash=AssemblySemanticHasher.Compute(m).semanticHash;Reject(()=>Analyze(s));}});
        Test("N-reference-assembly-identity-mutation",()=>{using(var s=Load(first)){s.GetModule("UnityEngine.AnimationModule").Assembly.Version=new Version(9,9,9,9);Reject(()=>Analyze(s));}});
        Test("N-disposed-domain",()=>{var s=Load(first);s.Dispose();try{Analyze(s);}catch(ObjectDisposedException){return;}throw new Exception("Disposed set accepted");});
        // Disk mutation occurs only in a fresh test-owned copy. Original N never changes.
        string copy=Path.Combine(output,"disk-control");Directory.CreateDirectory(copy);
        var files=first.files.Select(f=>{string rel=Path.GetFullPath(f.path).Substring(Path.GetFullPath(first.root).Length+1);string p=Path.Combine(copy,rel);Directory.CreateDirectory(Path.GetDirectoryName(p));File.Copy(f.path,p);return new FileRow{path=p,name=f.name,sha256=f.sha256,size=f.size,referenceOnly=f.referenceOnly,framework=f.framework};}).ToArray();
        var copied=new World{name="owned-negative",root=copy,receiptSha256=first.receiptSha256,files=files};
        Test("N-reference-disk-mutation",()=>{using(var s=Load(copied)){var f=files.Single(f=>f.name.Equals("UnityEngine.AnimationModule",StringComparison.OrdinalIgnoreCase));var original=File.ReadAllBytes(f.path);try{var changed=(byte[])original.Clone();changed[changed.Length-1]^=1;File.WriteAllBytes(f.path,changed);Reject(()=>Analyze(s));}finally{File.WriteAllBytes(f.path,original);}}});
        Test("N-reference-disappeared",()=>{using(var s=Load(copied)){var f=files.Single(f=>f.name.Equals("UnityEngine.AnimationModule",StringComparison.OrdinalIgnoreCase));var original=File.ReadAllBytes(f.path);try{File.Delete(f.path);try{Analyze(s);}catch(IOException){return;}throw new Exception("Missing reference accepted");}finally{File.WriteAllBytes(f.path,original);}}});
        Authenticate(first);Authenticate(copied);
        report.result=report.failures==0?"Passed":"Failed";Save("results.json",report);return report.failures==0?0:1;
    }
}
