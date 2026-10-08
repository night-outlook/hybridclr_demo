import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from m06_execution_metadata import ExecutionMetadata, LinkedSchemaResolver, PortableSymbols, Shape, read_methods, schema_fields
from shadow_tools import VerificationError


class ExecutionMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="m06-execution-metadata-")
        cls.root = Path(cls.temp.name)
        base = Path(os.environ.get("UNITY_MONO_ROOT", "/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MonoBleedingEdge"))
        if not (base / "bin/mono").is_file():
            raise unittest.SkipTest("Pinned Unity Mono compiler is unavailable")
        cls.source = cls.root / "Fixture.cs"
        cls.source.write_text('''using System; using System.Threading.Tasks;
public class Fixture<T> {
 public int Value;
 public Fixture(int value) { Value=value; }
 public static U Echo<U>(U value) { return value; }
 public static int Run(int value) { int result=0; try { if(value<0) throw new InvalidOperationException("actual-fixture"); result=value+3; } catch(InvalidOperationException error) when(error.Message.Length>0) { result=-1; } finally { result++; } return result; }
 public static async Task<int> Work(int value) { await Task.Yield(); return value+2; }
 public static string Generic() { return Echo<string>("hello"); }
}''', encoding="utf-8")
        cls.dll = cls.root / "Fixture.dll"; cls.pdb = cls.root / "Fixture.pdb"
        run = subprocess.run([str(base / "bin/mono"), str(base / "lib/mono/4.5/csc.exe"), "-nologo", "-target:library", "-debug:portable", "-optimize-", "-out:"+str(cls.dll), str(cls.source)], capture_output=True, text=True)
        if run.returncode: raise RuntimeError(run.stdout + run.stderr)
        cls.module = ExecutionMetadata(cls.dll.read_bytes(), cls.dll)
        cls.base = base
        cls.facade_dll=cls.root/'NetStandardFixture.dll';cls.facade_pdb=cls.root/'NetStandardFixture.pdb'
        run=subprocess.run([str(base/'bin/mono'),str(base/'lib/mono/4.5/csc.exe'),'-nologo','-target:library','-nostdlib','-debug:portable','-out:'+str(cls.facade_dll),'-r:'+str(base.parent/'NetStandard/ref/2.1.0/netstandard.dll'),str(cls.source)],capture_output=True,text=True)
        if run.returncode:raise RuntimeError(run.stdout+run.stderr)
        schema_source=cls.root/'Schema.cs';schema_source.write_text('using System; using System.Collections.Generic; [Serializable] public class Child { public string text; } [Serializable] public class Fields { public int count; public Child[] children; public List<Child> items; }')
        cls.schema={}
        for side in ('input','linked'):
            directory=cls.root/side;directory.mkdir();dll=directory/'Schema.dll'
            args=['-nostdlib','-r:'+str(base.parent/'NetStandard/ref/2.1.0/netstandard.dll')] if side=='input' else []
            run=subprocess.run([str(base/'bin/mono'),str(base/'lib/mono/4.5/csc.exe'),'-nologo','-target:library','-out:'+str(dll)]+args+[str(schema_source)],capture_output=True,text=True)
            if run.returncode:raise RuntimeError(run.stdout+run.stderr)
            cls.schema[side]=ExecutionMetadata(dll.read_bytes(),dll)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_actual_generic_tokens_flags_and_il(self):
        rows=read_methods(self.dll)
        self.assertEqual(len(rows),self.module.tables.counts[6])
        echo=next(row for row in rows if row["name"]=="Echo")
        self.assertEqual(echo["genericArity"],1)
        self.assertEqual(echo["genericParameterNames"],["U"])
        self.assertEqual(echo["returnType"],dict(assembly="",type="U"))
        self.assertTrue(echo["isStatic"])
        self.assertEqual(echo["metadataToken"]>>24,6)
        self.assertTrue(any("method:" in line and "Echo" in line for row in rows for line in row["instructions"]))

    def test_actual_filter_finally_and_branch_boundaries(self):
        run=next(row for row in read_methods(self.dll) if row["name"]=="Run")
        self.assertEqual([row["handlerType"] for row in run["exceptionHandlers"]],["Filter","Finally"])
        for handler in run["exceptionHandlers"]:
            self.assertLess(handler["tryStart"],handler["tryEnd"])
            self.assertLessEqual(handler["handlerEnd"],len(run["instructions"]))
        self.assertTrue(any("branch:" in line for line in run["instructions"]))

    def test_actual_portable_symbols_bind_document_lines_and_il(self):
        rows=read_methods(self.dll,self.pdb)
        points=[p for row in rows for p in row["sequencePoints"]]
        self.assertTrue(points)
        visible=[p for p in points if p["startLine"]!=0xFEEFEE]
        self.assertTrue(all(p["document"]==str(self.source) for p in visible))
        self.assertTrue(all(p["checksum"] for p in visible))
        self.assertTrue(any(p["startLine"]==6 for p in visible))

    def test_full_actual_editor_method_proof_parity(self):
        project=Path(__file__).resolve().parents[3]
        source=(project / "Assets/AssemblyShadowDemo/Editor/M06ExecutionSchemaVerifier.cs").read_text()
        dtos=source[source.index("[Serializable] public sealed class M06ExecutionMethod"):source.index("    /// <summary>")]
        methods=source[source.index("        internal static M06ExecutionMethod ReadMethod"):source.index("        private static void VerifyHash")]
        program='''using System; using System.IO; using System.Linq; using System.Collections.Generic; using System.Globalization; using System.Text; using dnlib.DotNet; using dnlib.DotNet.Emit;
''' + dtos + '''public static class Proof {
static void Require(bool value,string code,string message) { if(!value)throw new Exception(code+message); }
''' + methods.replace('throw new ShadowBuildException(', 'throw new Exception(').replace('"M06ExecutionIlOperand", ', '') + '''
public static void Main(string[] args) { using(var module=ModuleDefMD.Load(File.ReadAllBytes(args[0]),new ModuleCreationOptions {TryToLoadPdbFromDisk=false,PdbFileOrData=File.ReadAllBytes(args[1])})) { var rows=module.GetTypes().SelectMany(type=>type.Methods).OrderBy(method=>method.MDToken.Raw).Select(ReadMethod).ToArray();new System.Runtime.Serialization.Json.DataContractJsonSerializer(typeof(M06ExecutionMethod[])).WriteObject(Console.OpenStandardOutput(),rows); } }
}'''
        helper=self.root/'Proof.cs'; helper.write_text(program)
        dnlib=project.parent/'hybridclr_unity/Plugins/dnlib.dll'
        run=subprocess.run([str(self.base/'bin/mono'),str(self.base/'lib/mono/4.5/csc.exe'),'-nologo','-target:exe','-out:'+str(self.root/'Proof.exe'),'-r:'+str(dnlib),'-r:'+str(self.base/'lib/mono/4.5/System.Runtime.Serialization.dll'),str(helper)],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        env=dict(os.environ,MONO_PATH=str(dnlib.parent))
        self.maxDiff=None
        for dll,pdb in ((self.dll,self.pdb),(self.facade_dll,self.facade_pdb)):
            run=subprocess.run([str(self.base/'bin/mono'),str(self.root/'Proof.exe'),str(dll),str(pdb)],capture_output=True,text=True,env=env)
            self.assertEqual(run.returncode,0,run.stderr)
            expected=json.loads(run.stdout);actual=read_methods(dll,pdb);self.assertEqual(len(actual),len(expected))
            for actual,wanted in zip(actual,expected):self.assertEqual(actual,wanted,wanted['name'])

    def test_tampered_pdb_identity_is_rejected(self):
        data=bytearray(self.pdb.read_bytes())
        identifier=PortableSymbols(bytes(data),self.module,self.pdb).streams["#Pdb"][:20]
        offset=data.index(identifier); data[offset]^=1
        with self.assertRaisesRegex(VerificationError,"CodeView"):
            PortableSymbols(bytes(data),self.module,"tampered")

    def test_actual_data_contract_canonical_transport_and_hash(self):
        import m06_results as gate
        source=self.root/'Canonical.cs'
        source.write_text('''using System; using System.Runtime.Serialization.Json;
public class Receipt { public string planHash; public string path; public int schemaVersion; public bool enabled; public string[] images; }
public static class Canonical { public static void Main() { new DataContractJsonSerializer(typeof(Receipt)).WriteObject(Console.OpenStandardOutput(),new Receipt {schemaVersion=1,enabled=false,path="C:/actual/é/文",images=new[]{"one","two"}}); } }''')
        run=subprocess.run([str(self.base/'bin/mono'),str(self.base/'lib/mono/4.5/csc.exe'),'-nologo','-target:exe','-out:'+str(self.root/'Canonical.exe'),'-r:'+str(self.base/'lib/mono/4.5/System.Runtime.Serialization.dll'),str(source)],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        run=subprocess.run([str(self.base/'bin/mono'),str(self.root/'Canonical.exe')],capture_output=True)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertEqual(run.stdout,gate.datacontract_bytes(json.loads(run.stdout)))

    def schema_resolver(self):
        linked=self.schema['linked'];core=self.base/'lib/mono/4.5/mscorlib.dll'
        return LinkedSchemaResolver({linked.identity['fullName']:linked.label,linked.core:core})

    def test_declared_facade_and_actual_linked_resolved_field_types_are_distinct(self):
        resolver=self.schema_resolver()
        before=schema_fields(self.schema['input'],'Fields',resolver);after=schema_fields(self.schema['linked'],'Fields',resolver)
        self.assertEqual([r['resolvedType'] for r in before],[r['resolvedType'] for r in after])
        count=next(r for r in before if r['name']=='count')
        self.assertIn(', netstandard, Version=2.1.0.0',count['type'])
        self.assertIn(', mscorlib, Version=4.0.0.0',count['resolvedType'])
        items=next(r for r in before if r['name']=='items')
        self.assertIn('System.Collections.Generic.List`1[[Child, Schema,',items['resolvedType'])
        child=next(r for r in before if r['name']=='children')
        self.assertEqual(child['type'],child['resolvedType'])
        resolver.verify_unchanged()

    def test_resolved_field_types_match_actual_linked_reflection(self):
        source=self.root/'Fields.cs';source.write_text('''using System; using System.Reflection; public static class ReadFields { public static void Main(string[] args) { foreach(var f in Assembly.LoadFrom(args[0]).GetType("Fields").GetFields())Console.WriteLine(f.Name+"|"+f.FieldType.AssemblyQualifiedName); } }''')
        run=subprocess.run([str(self.base/'bin/mono'),str(self.base/'lib/mono/4.5/csc.exe'),'-nologo','-target:exe','-out:'+str(self.root/'Fields.exe'),str(source)],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        run=subprocess.run([str(self.base/'bin/mono'),str(self.root/'Fields.exe'),str(self.schema['linked'].label)],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr)
        actual=dict(line.split('|',1) for line in run.stdout.splitlines())
        rows=schema_fields(self.schema['input'],'Fields',self.schema_resolver())
        self.assertEqual(actual,{r['name']:r['resolvedType'] for r in rows})

    def test_resolved_leaf_does_not_search_other_assemblies(self):
        resolver=self.schema_resolver()
        with self.assertRaises(VerificationError):resolver.resolve(Shape('System.Int32','System.Int32',self.schema['linked'].identity['fullName']))
        with self.assertRaises(VerificationError):resolver.resolve(Shape('System.Int32','System.Int32',self.schema['input'].core))
        with self.assertRaises(VerificationError):schema_fields(self.schema['input'],'MissingOwner',resolver)
        with self.assertRaises(VerificationError):resolver.resolve(Shape('Missing','Missing',self.schema['linked'].core))

    def test_actual_exported_type_forwarding_requires_exact_target(self):
        target=self.root/'Target.cs';target.write_text('namespace Forwarded { public class Leaf {} }')
        facade=self.root/'Facade.cs';facade.write_text('using System.Runtime.CompilerServices; [assembly:TypeForwardedTo(typeof(Forwarded.Leaf))]')
        for name,source,args in (('Target',target,[]),('Facade',facade,['-r:'+str(self.root/'Target.dll')])):
            run=subprocess.run([str(self.base/'bin/mono'),str(self.base/'lib/mono/4.5/csc.exe'),'-nologo','-target:library','-out:'+str(self.root/(name+'.dll'))]+args+[str(source)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        source=ExecutionMetadata((self.root/'Facade.dll').read_bytes(),'facade');target=ExecutionMetadata((self.root/'Target.dll').read_bytes(),'target')
        resolver=LinkedSchemaResolver({source.identity['fullName']:self.root/'Facade.dll',target.identity['fullName']:self.root/'Target.dll'})
        shape=Shape('Forwarded.Leaf','Forwarded.Leaf',source.identity['fullName'])
        self.assertEqual(resolver.resolve(shape).assembly,target.identity['fullName'])
        with self.assertRaises(VerificationError):LinkedSchemaResolver({source.identity['fullName']:self.root/'Facade.dll'}).resolve(shape)
        with self.assertRaises(VerificationError):LinkedSchemaResolver({source.identity['fullName']:self.root/'Target.dll'}).resolve(shape)
        data=(self.root/'Facade.dll').read_bytes();self.assertEqual(data.count(b'Target\0'),1)
        cycle=self.root/'Cycle.dll';cycle.write_bytes(data.replace(b'Target\0',b'Facade\0'))
        with self.assertRaisesRegex(VerificationError,'cyclic'):LinkedSchemaResolver({source.identity['fullName']:cycle}).resolve(shape)

    def test_actual_linked_counterpart_shape_or_flags_change_rejects(self):
        for variant,field in (('shape','public long count;'),('flags','private int count;')):
            directory=self.root/variant;directory.mkdir();source=directory/'Schema.cs';source.write_text('using System; using System.Collections.Generic; [Serializable] public class Child { public string text; } [Serializable] public class Fields { '+field+' public Child[] children; public List<Child> items; }')
            dll=directory/'Schema.dll'
            run=subprocess.run([str(self.base/'bin/mono'),str(self.base/'lib/mono/4.5/csc.exe'),'-nologo','-target:library','-out:'+str(dll),str(source)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            resolver=self.schema_resolver();resolver.paths[self.schema['linked'].identity['fullName']]=dll
            with self.assertRaises(VerificationError):schema_fields(self.schema['input'],'Fields',resolver)

    def test_truncated_dll_and_pdb_fail_closed(self):
        for size in (0,1,63,256):
            with self.assertRaises(VerificationError): ExecutionMetadata(self.dll.read_bytes()[:size],"short")
            with self.assertRaises(VerificationError): PortableSymbols(self.pdb.read_bytes()[:size],self.module,"short")


if __name__=="__main__": unittest.main()
