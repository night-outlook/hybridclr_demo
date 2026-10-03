using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using dnlib.DotNet;
using dnlib.DotNet.Emit;
using HybridCLR.Editor.AssemblyShadow;

internal static class Program
{
    private static string root;
    private static readonly List<object> cases = new List<object>();
    private static int failures;
    private static int Main(string[] args)
    {
        if (args.Length != 2 || args[0] != "--output") return 2;
        root = Path.GetFullPath(args[1]);
        if (Directory.Exists(root) || File.Exists(root)) throw new IOException("Unused output required");
        Directory.CreateDirectory(root);
        Test("Q01-pure-reference", f => Candidate(f.Analyze()));
        Test("Q02-private-reference-stays-v1-rejected", f => {
            f.Change(t => t.Fields.Add(new FieldDefUser("added", new FieldSig(t.Module.CorLibTypes.Object), FieldAttributes.Private)));
            var r=f.Analyze(); Candidate(r); Need(r.types.Single().nativeV1Decision=="Rejected", "Eligibility cannot override V1"); });
        Test("Q03-value-representation", f => { f.Both(t=>t.BaseType=Ref(t.Module,"System","ValueType","mscorlib")); Excluded(f.Analyze(),"ValueRepresentation"); });
        Test("Q04-unity-native-binding", f => { f.Both(t=>t.BaseType=Ref(t.Module,"UnityEngine","MonoBehaviour","UnityEngine.CoreModule")); Excluded(f.Analyze(),"UnityNativeBinding"); });
        Test("Q05-resource-domain", f => { f.resources.types=new[]{new ResourceAbiTypeDescriptor{typeKey="pure:Fixture:Node",assembly="Pure",type="Node",@namespace="Fixture"}}; Excluded(f.Analyze(),"SerializedResourceType"); });
        Test("Q06-unresolved-parent", f => { f.Both(t=>t.BaseType=Ref(t.Module,"Absent","Base","mscorlib")); Excluded(f.Analyze(),"UnresolvedBase"); });
        Test("Q07-generic-definition", f => { f.Both(t=>t.GenericParameters.Add(new GenericParamUser(0,GenericParamAttributes.NonVariant,"T"))); Excluded(f.Analyze(),"GenericBoundary"); });
        Test("Q08-generic-field", f => { f.Both(t=>t.Fields.Add(new FieldDefUser("generic",new FieldSig(new GenericInstSig(new ClassSig(Ref(t.Module,"System.Collections.Generic","List`1","mscorlib")),t.Module.CorLibTypes.Object)),FieldAttributes.Private))); Excluded(f.Analyze(),"FieldGenericPointer"); });
        Test("Q09-byref-method", f => { f.Both(t=>t.Methods.Single(m=>m.Name=="Read").MethodSig.Params.Add(new ByRefSig(t.Module.CorLibTypes.Int32))); Excluded(f.Analyze(),"MethodGenericPointer"); });
        Test("Q10-pinvoke", f => { f.Both(t=> {var m=t.Methods.Single(x=>x.Name=="Read");m.ImplMap=new ImplMapUser(new ModuleRefUser(t.Module,"native"),"Read",PInvokeAttributes.CallConvCdecl);}); Excluded(f.Analyze(),"NativeCallableMethod"); });
        Test("Q11-sequential-layout", f => { f.Both(t=>t.IsSequentialLayout=true); Excluded(f.Analyze(),"ExplicitOrSequentialLayout"); });
        Test("Q12-unknown-resource", f => { f.resources.unknowns=new[]{"missing resource closure"}; Excluded(f.Analyze(),"ResourceUnknown"); });
        Test("Q13-reference-bytes-changed", f => f.Tamper("references/mscorlib.dll"));
        Test("Q14-baseline-bytes-changed", f => f.Tamper("baseline/Pure.dll"));
        Test("Q15-target-bytes-changed", f => f.Tamper("target/Pure.dll"));
        Test("Q16-fixed-aot-consumer", f => { f.Consumer(false,false); Code("NonShadowConsumer",()=>f.Analyze()); });
        Test("Q17-ordinary-consumer", f => { f.Consumer(true,false); Code("NonShadowConsumer",()=>f.Analyze()); });
        Test("Q18-fixed-generic-consumer", f => { f.Consumer(false,true); Code("NonShadowConsumer",()=>f.Analyze()); });
        Test("Q19-dynamic-consumer-unproved", f => { f.DynamicConsumer(); Excluded(f.Analyze(),"DynamicConcreteConsumer"); });
        Test("Q20-delegate-domain", f => { f.Both(t=>t.BaseType=Ref(t.Module,"System","MulticastDelegate","mscorlib")); Excluded(f.Analyze(),"DelegateAbi"); });
        Test("Q21-resource-input-required", f => { f.resources=null; Code("EligibilityResourceInput",()=>f.Analyze()); });
        Test("Q22-deterministic-source-binding", f => {var a=f.Analyze();var b=f.Analyze();Need(Json(a)==Json(b),"Deterministic unchanged input report");Need(a.inputBindings.Length==6,"Both input worlds and actual references");});
        Test("Q23-no-business-initialization", f => { f.Both(t=> {var m=new MethodDefUser(".cctor",MethodSig.CreateStatic(t.Module.CorLibTypes.Void),MethodImplAttributes.IL,MethodAttributes.Static|MethodAttributes.Private|MethodAttributes.SpecialName|MethodAttributes.RTSpecialName);m.Body=new CilBody();m.Body.Instructions.Add(Instruction.Create(OpCodes.Ldnull));m.Body.Instructions.Add(Instruction.Create(OpCodes.Throw));t.Methods.Add(m);});Candidate(f.Analyze()); });
        Test("Q24-resource-duplicate-key", f => {var t=new ResourceAbiTypeDescriptor{typeKey="pure:Fixture:Node"};f.resources.types=new[]{t,t};Code("EligibilityResourceInput",()=>f.Analyze());});
        Test("Q25-unknown-resource-flag", f => {f.resources.types=new[]{new ResourceAbiTypeDescriptor{typeKey="other:Fixture:X",hasUnknown=true}};Excluded(f.Analyze(),"ResourceUnknown");});
        Test("Q26-explicit-interop-field", f => {f.Both(t=>t.Fields.Add(new FieldDefUser("pointer",new FieldSig(new PtrSig(t.Module.CorLibTypes.Int32)),FieldAttributes.Private)));Excluded(f.Analyze(),"FieldGenericPointer");});
        Test("Q27-resource-hash-binds-field-shape", f => {var t=new ResourceAbiTypeDescriptor{typeKey="pure:Fixture:Node",fields=new[]{new ResourceAbiFieldDescriptor{name="x",type="int"}}};f.resources.types=new[]{t};var a=f.Analyze();t.fields[0].type="long";Need(a.resourceDescriptorHash!=f.Analyze().resourceDescriptorHash,"Resource shape hash");});
        Test("Q28-report-never-grants-capability", f => {var r=f.Analyze();Need(!r.expansionAuthorized&&!r.runtimeProofExecuted&&!r.qualificationApproved&&r.types.All(t=>!t.authorizesExpansion),"No permission from classification");Need(r.types.All(t=>t.requiredProofs.Contains("NoExistingBaselineObjectsOrUses")&&t.requiredProofs.Contains("ExplicitOwnerQualificationApproval")),"Qualification proof boundary");});
        Test("Q29-resource-referenced-type", f => {f.resources.types=new[]{new ResourceAbiTypeDescriptor{typeKey="other:Other:Container",referencedTypeKeys=new[]{"pure:Fixture:Node"}}};Excluded(f.Analyze(),"SerializedResourceType");});
        Test("Q30-loaded-metadata-mutation", f => f.TamperMetadata());
        var inventory=Directory.GetFiles(root,"*.dll",SearchOption.AllDirectories).OrderBy(x=>x,StringComparer.Ordinal).Select(p=>new{path=Path.GetRelativePath(root,p).Replace('\\','/'),sha256=ShadowHash.File(p),size=new FileInfo(p).Length}).ToArray();
        File.WriteAllText(Path.Combine(root,"results.json"),Json(new{kind="R03QualificationContracts",schemaVersion=1,result=failures==0?"Passed":"Failed",failures,cases,inventory,runtimeProofExecuted=false,expansionAuthorized=false})+"\n");
        return failures==0?0:1;
    }
    private static string Json(object value)=>JsonSerializer.Serialize(value,new JsonSerializerOptions{IncludeFields=true,WriteIndented=true});
    private static void Need(bool b,string message){if(!b)throw new Exception(message);}
    private static void Candidate(PureInterpreterEligibilityReport r){Need(r.types.Length==1&&r.types[0].decision=="StaticCandidateNeedsRuntimeAndReview",Json(r));Need(!r.expansionAuthorized,"No expansion");}
    private static void Excluded(PureInterpreterEligibilityReport r,string reason){Need(r.types.Any(t=>t.decision=="ExcludedOrNeedsProof"&&t.staticReasons.Any(s=>s.StartsWith(reason,StringComparison.Ordinal))),Json(r));Need(!r.expansionAuthorized,"No expansion");}
    private static void Code(string code,Action action){try{action();}catch(ShadowBuildException e){Need(e.Code==code,"Expected "+code+", got "+e);return;}throw new Exception("Expected "+code);}
    private static void Test(string name,Action<Fixture> action)
    {
        try{using(var f=new Fixture(Path.Combine(root,name))){action(f);}cases.Add(new{id=name,result="Passed"});Console.WriteLine(name+" Passed");}
        catch(Exception e){++failures;cases.Add(new{id=name,result="Failed",error=e.ToString()});Console.Error.WriteLine(name+" "+e);}
    }
    private static AssemblyRef AR(string name)=>new AssemblyRefUser(name,new Version(1,0,0,0),new PublicKeyToken()){HasPublicKey=false};
    private static ITypeDefOrRef Ref(ModuleDef m,string ns,string name,string assembly)=>new TypeRefUser(m,ns,name,AR(assembly));
    private static ModuleDefUser Module(string name)
    {
        var m=new ModuleDefUser(name+".dll"){Kind=ModuleKind.Dll,RuntimeVersion="v4.0.30319",Mvid=Guid.Parse("01020304-0506-0708-090a-0b0c0d0e0f01")};
        new AssemblyDefUser(name,new Version(1,0,0,0)).Modules.Add(m);
        var cor=m.CorLibTypes.AssemblyRef;cor.Version=new Version(1,0,0,0);cor.PublicKeyOrToken=new PublicKeyToken();cor.HasPublicKey=false;
        return m;
    }
    private sealed class Fixture:IDisposable
    {
        public ResourceAbiDescriptor resources=new ResourceAbiDescriptor();
        private readonly string path;
        private readonly ModuleDefUser baseline=Module("Pure"), target=Module("Pure");
        private readonly List<ModuleDefUser> extras=new List<ModuleDefUser>();
        private readonly List<AssemblyCapability> caps=new List<AssemblyCapability>{new AssemblyCapability{name="Pure",isShadowCapable=true,capabilityDeclared=true}};
        public Fixture(string root)
        {
            path=root;Directory.CreateDirectory(path);
            foreach(var pair in new[]{(baseline,41),(target,42)})
            {
                var t=new TypeDefUser("Fixture","Node",pair.Item1.CorLibTypes.Object.TypeDefOrRef){Attributes=TypeAttributes.Public|TypeAttributes.AutoLayout};pair.Item1.Types.Add(t);
                t.Fields.Add(new FieldDefUser("x",new FieldSig(pair.Item1.CorLibTypes.Int32),FieldAttributes.Private));
                var m=new MethodDefUser("Read",MethodSig.CreateInstance(pair.Item1.CorLibTypes.Int32),MethodImplAttributes.IL,MethodAttributes.Public){Body=new CilBody()};
                m.Body.Instructions.Add(Instruction.Create(OpCodes.Ldc_I4,pair.Item2));m.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));t.Methods.Add(m);
            }
            using(var core=Module("mscorlib"))
            {
                foreach(var name in new[]{"Object","ValueType","Enum","MulticastDelegate","Void","Int32","Int64","Boolean","String","Type"})core.Types.Add(new TypeDefUser("System",name,null){Attributes=TypeAttributes.Public});
                var list=new TypeDefUser("System.Collections.Generic","List`1",core.Types.Single(t=>t.Name=="Object")){Attributes=TypeAttributes.Public};list.GenericParameters.Add(new GenericParamUser(0,GenericParamAttributes.NonVariant,"T"));core.Types.Add(list);Save(core,"references/mscorlib.dll");
            }
            using(var engine=Module("UnityEngine.CoreModule"))
            {var o=new TypeDefUser("UnityEngine","Object",engine.CorLibTypes.Object.TypeDefOrRef){Attributes=TypeAttributes.Public};engine.Types.Add(o);engine.Types.Add(new TypeDefUser("UnityEngine","MonoBehaviour",o){Attributes=TypeAttributes.Public});Save(engine,"references/UnityEngine.CoreModule.dll");}
        }
        public void Change(Action<TypeDef> edit)=>edit(target.Types.Single(t=>t.Name=="Node"));
        public void Both(Action<TypeDef> edit){edit(baseline.Types.Single(t=>t.Name=="Node"));Change(edit);}
        public void Consumer(bool ordinary,bool generic)
        {
            var m=Module("Consumer");extras.Add(m);var t=new TypeDefUser("Fixture","Consumer",m.CorLibTypes.Object.TypeDefOrRef){Attributes=TypeAttributes.Public};m.Types.Add(t);
            TypeSig sig=new ClassSig(Ref(m,"Fixture","Node","Pure"));
            if(generic)sig=new GenericInstSig(new ClassSig(Ref(m,"System.Collections.Generic","List`1","mscorlib")),sig);
            t.Fields.Add(new FieldDefUser("value",new FieldSig(sig),FieldAttributes.Private));
            caps.Add(new AssemblyCapability{name="Consumer",classification=ordinary?AssemblyClassification.NormalHotUpdate:AssemblyClassification.Runtime});
        }
        public void DynamicConsumer()
        {
            var m=Module("Consumer");extras.Add(m);var t=new TypeDefUser("Fixture","Consumer",m.CorLibTypes.Object.TypeDefOrRef){Attributes=TypeAttributes.Public};m.Types.Add(t);
            var f=new MethodDefUser("Acquire",MethodSig.CreateStatic(m.CorLibTypes.Object),MethodImplAttributes.IL,MethodAttributes.Public|MethodAttributes.Static){Body=new CilBody()};
            f.Body.Instructions.Add(Instruction.Create(OpCodes.Ldstr,"Fixture.Node, Pure"));
            f.Body.Instructions.Add(Instruction.Create(OpCodes.Call,new MemberRefUser(m,"GetType",MethodSig.CreateStatic(m.CorLibTypes.Object,m.CorLibTypes.String),Ref(m,"System","Type","mscorlib"))));f.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));t.Methods.Add(f);caps.Add(new AssemblyCapability{name="Consumer"});
        }
        private void Save(ModuleDef module,string relative){string p=Path.Combine(path,relative);Directory.CreateDirectory(Path.GetDirectoryName(p));using(var s=new FileStream(p,FileMode.Create))module.Write(s);}
        private void Prepare(){Save(baseline,"baseline/Pure.dll");Save(target,"target/Pure.dll");foreach(var m in extras){Save(m,"baseline/"+m.Name);Save(m,"target/"+m.Name);}}
        public PureInterpreterEligibilityReport Analyze()
        {
            Prepare();using(var a=DnlibAssemblyLoader.Load(Path.Combine(path,"baseline"),new[]{Path.Combine(path,"references")},caps,false))
            using(var b=DnlibAssemblyLoader.Load(Path.Combine(path,"target"),new[]{Path.Combine(path,"references")},caps,false))
            {var result=PureInterpreterEligibility.Analyze(a,b,null,null,resources);File.WriteAllText(Path.Combine(path,"eligibility.json"),Json(result));return result;}
        }
        public void Tamper(string relative)
        {
            Prepare();using(var a=DnlibAssemblyLoader.Load(Path.Combine(path,"baseline"),new[]{Path.Combine(path,"references")},caps,false))
            using(var b=DnlibAssemblyLoader.Load(Path.Combine(path,"target"),new[]{Path.Combine(path,"references")},caps,false))
            {File.AppendAllText(Path.Combine(path,relative),"mutated");Code("EligibilityInputChanged",()=>PureInterpreterEligibility.Analyze(a,b,null,null,resources));}
        }
        public void TamperMetadata()
        {
            Prepare();using(var a=DnlibAssemblyLoader.Load(Path.Combine(path,"baseline"),new[]{Path.Combine(path,"references")},caps,false))
            using(var b=DnlibAssemblyLoader.Load(Path.Combine(path,"target"),new[]{Path.Combine(path,"references")},caps,false))
            {b.GetModule("Pure").Types.Single(t=>t.Name=="Node").Fields.Clear();Code("EligibilityInputChanged",()=>PureInterpreterEligibility.Analyze(a,b,null,null,resources));}
        }
        public void Dispose(){baseline.Dispose();target.Dispose();foreach(var m in extras)m.Dispose();}
    }
}
