"""Adversarial independent raw-admission tests; not synthetic Player acceptance."""
import copy
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from shadow_tools import VerificationError
from m05_types import MethodProof
from test_m05_results import make_type_pe
from test_m04_results import make_pe
import m05_raw_type_admissions as v


def raw_pe(name, types, *, references=(), type_refs=(), member_refs=(), user_strings=(), core=False, version=None, public_token=None, exported=(),method_specs=(),type_specs=()):
    """Actual bounded CLI metadata/body fixture, not a mocked metadata reader."""
    strings,blobs,us=bytearray(b"\0"),bytearray(b"\0"),bytearray(b"\0")
    def string(text):p=len(strings);strings.extend(text.encode()+b"\0");return p
    def length(value):return bytes([value]) if value<128 else bytes([0x80|(value>>8),value&255])
    def blob(data):p=len(blobs);blobs.extend(length(len(data))+data);return p
    string_tokens={}
    for text in user_strings:
        data=text.encode("utf-16-le")+b"\0";string_tokens[text]=0x70000000|len(us);us.extend(length(len(data))+data)
    token=bytes.fromhex("b77a5c561934e089")
    version=version or ((4,0,0,0) if core else (1,0,0,0))
    own_token=token if core else b""
    if public_token is not None:own_token=public_token
    rows={0:[struct.pack("<HHHHH",0,string(name+".dll"),1,0,0)],
          1:[struct.pack("<HHH",entry[0] if len(entry)==3 else 6,string(entry[-1]),string(entry[-2])) for entry in type_refs],
          2:[struct.pack("<IHHHHH",0,string("<Module>"),0,0,1,1)],4:[],6:[],8:[],9:[],10:[],12:[],17:[],25:[],42:[],
          32:[struct.pack("<IHHHHIHHH",0x8004,*version,0,blob(own_token) if own_token else 0,string(name),0)],
          35:[struct.pack("<HHHHIHHHH",4 if ref=="mscorlib" else 1,0,0,0,0,blob(token) if ref=="mscorlib" else 0,string(ref),0,0) for ref in references],
          39:[struct.pack("<IIHHH",row.get("flags",0x200000),0,string(row["name"]),string(row.get("namespace","")),row["implementation"]) for row in exported],
          43:[struct.pack("<HH",target,blob(signature)) for target,signature in method_specs],
          27:[struct.pack("<H",blob(signature)) for signature in type_specs]}
    for owner,n,sig in member_refs:rows[10].append(struct.pack("<HHH",owner*8+1,string(n),blob(sig)))
    bodies=bytearray()
    for rid,t in enumerate(types,2):
        rows[2].append(struct.pack("<IHHHHH",t.get("flags",1),string(t["name"]),string(t.get("namespace","Example")),t.get("extends",0),len(rows[4])+1,len(rows[6])+1))
        for field in t.get("fields",[]):rows[4].append(struct.pack("<HHH",field.get("flags",0x16),string(field["name"]),blob(field["signature"])))
        for interface in t.get("interfaces",[]):rows[9].append(struct.pack("<HH",rid,interface))
        for body_method,declaration in t.get("overrides",[]):rows[25].append(struct.pack("<HHH",rid,body_method,declaration))
        for number in range(t.get("arity",0)):rows[42].append(struct.pack("<HHHH",number,0,rid*2,string("T")))
        for method in t.get("methods",[]):
            body=method.get("body");rva=0
            if callable(body):body=body(string_tokens)
            if body is not None:
                bodies.extend(bytes(-len(bodies)%4));rva=0x3000+len(bodies)
                if "locals" in method:
                    rows[17].append(struct.pack("<H",blob(method["locals"])));local_token=0x11000000|len(rows[17])
                else:local_token=0
                bodies.extend(struct.pack("<HHII",0x3013,8,len(body),local_token));bodies.extend(body)
            start=len(rows[8])+1
            for seq,param in enumerate(method.get("parameters",[]),1):rows[8].append(struct.pack("<HHH",0,seq,string(param)))
            rows[6].append(struct.pack("<IHHHHH",rva,method.get("impl",0),method.get("flags",0x16),string(method["name"]),blob(method["signature"]),start))
            for number in range(method.get("arity",0)):rows[42].append(struct.pack("<HHHH",number,0,len(rows[6])*2+1,string("T")))
            if method.get("attribute"):
                rows[12].append(struct.pack("<HHH",len(rows[6])*32,method["attribute"]*8+3,blob(b"\x01\0\0\0")))
    rows={table:items for table,items in rows.items() if items}
    table_data=struct.pack("<IBBBBQQ",0,2,0,0,1,sum(1<<t for t in rows),0)
    table_data+=b"".join(struct.pack("<I",len(rows[t])) for t in sorted(rows))+b"".join(b"".join(rows[t]) for t in sorted(rows))
    streams=[("#~",table_data),("#Strings",bytes(strings)),("#Blob",bytes(blobs)),("#GUID",bytes(range(16))),("#US",bytes(us))]
    root=struct.pack("<IHHII",0x424a5342,1,1,0,12)+b"v4.0.30319\0\0"+struct.pack("<HH",0,len(streams))
    offset=len(root)+sum(8+((len(n)+4)&~3) for n,_ in streams);headers,content=b"",b""
    for n,data in streams:
        encoded=n.encode()+b"\0";headers+=struct.pack("<II",offset,len(data))+encoded+bytes(-len(encoded)%4);content+=data;offset+=len(data)
    metadata=root+headers+content
    pe=bytearray(make_pe()[:1024]);pe.extend(metadata)
    assert len(pe)<4608
    pe.extend(bytes(4608-len(pe)));pe.extend(bodies)
    struct.pack_into("<I",pe,512+12,len(metadata));section=0x98+224
    struct.pack_into("<I",pe,section+8,len(pe)-512);struct.pack_into("<I",pe,section+16,len(pe)-512)
    return bytes(pe)


def raw_helper_fixture(body=None, locals=None, **changes):
    core_types=[dict(namespace="System",name=n) for n in ("Object","Void","String","Boolean","Int32","Type")]
    core_types += [dict(namespace="System.Reflection",name="Assembly",methods=[
        dict(name="Load",signature=b"\x00\x01\x12\x20\x0e"),
        dict(name="GetTypes",flags=6,signature=b"\x20\x00\x1d\x12\x1c")])]
    # Unrelated generic overload is deliberately present: lookup must first
    # identify the requested name, not reject unrelated core signatures.
    core_types[2]["methods"]=[dict(name="UnrelatedGeneric",signature=b"\x10\x01\x00\x01")]
    core=raw_pe("mscorlib",core_types,core=True)
    default=lambda tokens:b"\x72"+struct.pack("<I",tokens["Provider"])+b"\x28\x01\0\0\x0a\x6f\x02\0\0\x0a\x2a"
    method=dict(name="Run",signature=b"\x00\x00\x1d\x12\x09",body=body or default,**changes)
    if locals is not None:method["locals"]=locals
    helper=raw_pe("Bootstrap",[dict(name="Queries",namespace="",methods=[method])],references=["mscorlib"],
                  type_refs=[("System.Reflection","Assembly"),("System","Type")],
                  member_refs=[(1,"Load",b"\x00\x01\x12\x05\x0e"),(1,"GetTypes",b"\x20\x00\x1d\x12\x09")],user_strings=["Provider","Provider.dll"])
    provider=raw_pe("Provider",[dict(name="Payload")])
    modules={name:v.RawMethodProof(data,name) for name,data in (("mscorlib",core),("Bootstrap",helper),("Provider",provider))}
    site=configuration()["sites"][0];site["methodHash"]=modules["Bootstrap"].method_hash(1)
    return helper,modules,site


def write_raw_snapshot(root,extra_types=(),extra_refs=(),extra_members=(),method_specs=(),helper_changes=None,type_specs=(),extra_assemblies=()):
    """Complete 25-site compiler artifact with actual independent CLI tables."""
    core_names=[("System",n) for n in ("Object","Void","String","Boolean","Int32","Type")]
    core_names += [("System.Reflection","Assembly"),("System.Reflection","Module"),("System.Reflection","TypeInfo"),("System.Collections.Generic","IEnumerable`1")]
    def signatures(core):
        def t(index):return b"\x12"+bytes([(index+1)*4 if core else index*4+1])
        array=b"\x1d"+t(6);defined=b"\x15"+t(10)+b"\x01"+t(9);exported=b"\x15"+t(10)+b"\x01"+t(6)
        return [b"\x00\x01"+t(7)+b"\x0e",b"\x20\x00"+t(8),b"\x20\x00"+array,
                b"\x20\x00"+defined,b"\x20\x00"+exported,b"\x20\x00"+array,b"\x20\x03"+t(6)+b"\x0e\x02\x02"]
    core_sigs,ref_sigs=signatures(True),signatures(False)
    method_names=["Load","get_ManifestModule","GetTypes","get_DefinedTypes","get_ExportedTypes","GetTypes","GetType"]
    core_types=[dict(namespace=ns,name=name,arity=1 if name.endswith("`1") else 0) for ns,name in core_names]
    core_types[6]["methods"]=[dict(name=method_names[n],signature=core_sigs[n],flags=0x16 if n==0 else 6) for n in range(5)]
    core_types[7]["methods"]=[dict(name=method_names[n],signature=core_sigs[n],flags=6) for n in (5,6)]
    core=raw_pe("mscorlib",core_types,core=True)
    methods,sites=[],[];declaring="AssemblyShadowDemo.M05BoundTypeQueries"
    for operation_index,operation in enumerate(v.OPERATIONS):
        member_index=operation_index+3;kind=v.OPERATIONS[operation]
        name=["GetTypes","GetDefinedTypes","GetExportedTypes","GetModuleTypes","GetModuleType"][operation_index]
        returned=ref_sigs[member_index-1][2:-3] if kind=="Module.GetType" else ref_sigs[member_index-1][2:]
        method_signature=operation.split(" System.Reflection.")[0]+" "+declaring+"::"+name+"(System.String)"
        chains=[];position=0
        for provider in v.CANDIDATES:
            chain=[("ldstr",provider),("call",1)]
            if kind.startswith("Module."):chain.append(("callvirt",2))
            if kind=="Module.GetType":chain.extend([("ldstr",v.TYPE_NAMES[provider]),("one",None),("zero",None)])
            site=configuration()["sites"][0]
            site.update(id=name+"-"+provider,consumerAssembly="AssemblyShadowDemo.Bootstrap",declaringType=declaring,
                        methodSignature=method_signature,operationIndex=position+len(chain),operationSignature=operation,
                        providerAssemblyIdentity=provider+", Version=1.0.0.0, Culture=neutral, PublicKeyToken=null",
                        typeName=v.TYPE_NAMES[provider] if kind=="Module.GetType" else "",throwOnError=kind=="Module.GetType")
            sites.append(site);chain.extend([("callvirt",member_index),("ret",None)]);position+=len(chain);chains.extend(chain)
        def body(tokens,chains=chains):
            data=bytearray()
            for opcode,operand in chains:
                if opcode=="ldstr":data.extend(b"\x72"+struct.pack("<I",tokens[operand]))
                elif opcode in ("call","callvirt"):data.extend(bytes([0x28 if opcode=="call" else 0x6f])+struct.pack("<I",0x0a000000|operand))
                else:data.append({"one":0x17,"zero":0x16,"ret":0x2a}[opcode])
            return bytes(data)
        methods.append(dict(name=name,signature=b"\x00\x01"+returned+b"\x0e",parameters=["assemblyName"],body=body))
    helper_type=dict(name="M05BoundTypeQueries",namespace="AssemblyShadowDemo",flags=0x181,extends=5,methods=methods)
    helper_type.update(helper_changes or {})
    helper=raw_pe("AssemblyShadowDemo.Bootstrap",[helper_type,*extra_types],references=["mscorlib",*extra_assemblies],type_refs=[*core_names,*extra_refs],
                  member_refs=[(7 if n<5 else 8,method_names[n],ref_sigs[n]) for n in range(7)]+list(extra_members),
                  user_strings=[*v.CANDIDATES,*v.TYPE_NAMES.values()],method_specs=method_specs,type_specs=type_specs)
    proof=v.RawMethodProof(helper,"helper")
    for site in sites:site["methodHash"]=proof.method_hash(v.find_method(proof,declaring,site["methodSignature"]))
    sites.sort(key=lambda site:v.ordinal(site["id"]));config=dict(schemaVersion=1,policy=v.POLICY,sites=sites)
    snapshot=dict(unityVersion="2022.3.62f2",target="StandaloneOSX",architecture="arm64",assemblies=[],filteredAssemblies=[],references=[])
    (root/"Assemblies").mkdir();(root/"References").mkdir();(root/"RawTypeAdmissions").mkdir()
    module_bytes={"AssemblyShadowDemo.Bootstrap":helper,"mscorlib":core}
    for name in v.CANDIDATES:
        ns,leaf=v.TYPE_NAMES[name].rsplit(".",1);module_bytes[name]=raw_pe(name,[dict(name=leaf,namespace=ns)])
    for name,data in module_bytes.items():
        section="references" if name=="mscorlib" else "assemblies";relative=("References/" if section=="references" else "Assemblies/")+name+".dll"
        (root/relative).write_bytes(data);snapshot[section].append(dict(name=name,path=relative,sha256=hashlib.sha256(data).hexdigest()))
    raw=json.dumps(config,indent=4).encode();parsed=v.parse_configuration(raw);(root/"RawTypeAdmissions/configuration.json").write_bytes(raw)
    snapshot["extraScriptingDefines"]=[v.PREFIX+parsed["configurationSha256"]]
    modules={name:v.RawMethodProof(data,name) for name,data in module_bytes.items()};files={row["name"]:row for section in ("assemblies","references") for row in snapshot[section]}
    rows=[]
    for site in sites:
        consumer=site["consumerAssembly"];provider=site["providerAssemblyIdentity"].split(", ")[0];cf,pf=files[consumer],files[provider]
        rows.append(dict(id=site["id"],consumerAssemblyIdentity=modules[consumer].identity["fullName"],consumerPath=cf["path"],consumerSha256=cf["sha256"],
                         providerAssemblyIdentity=modules[provider].identity["fullName"],providerPath=pf["path"],providerSha256=pf["sha256"],providerInventoryHash=v.type_inventory_hash(modules[provider]),
                         declaringType=site["declaringType"],methodSignature=site["methodSignature"],operationIndex=site["operationIndex"],operationSignature=site["operationSignature"],
                         kind=v.OPERATIONS[site["operationSignature"]],typeName=site["typeName"],throwOnError=site["throwOnError"],ignoreCase=False,
                         compiledMethodHash=site["methodHash"],linkedMethodHash="",compiledConsumerSha256=cf["sha256"]))
    receipt=dict(schemaVersion=1,policy=v.POLICY,phase="Compiled",configurationSha256=parsed["configurationSha256"],configurationHash=parsed["configurationHash"],
                 unityVersion=snapshot["unityVersion"],target=snapshot["target"],architecture=snapshot["architecture"],buildGuid="",linkedPlayerReceiptHash="",profileHash="",sites=rows)
    (root/"RawTypeAdmissions/compiled-evidence.json").write_bytes(json.dumps(receipt,indent=4).encode())
    return snapshot,config,receipt


def configuration():
    site=dict(id="raw-types",consumerAssembly="Bootstrap",declaringType="Queries",methodSignature="System.Type[] Queries::Run()",
              methodHash="a"*64,operationIndex=2,operationSignature=next(iter(v.OPERATIONS)),
              providerAssemblyIdentity="Provider, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null",typeName="",throwOnError=False,ignoreCase=False,reason="Finite literal raw query")
    return dict(schemaVersion=1,policy=v.POLICY,sites=[site])


class ConfigurationTests(unittest.TestCase):
    def test_raw_bytes_and_canonical_configuration_are_distinct_domains(self):
        raw=json.dumps(configuration()).encode();compact=json.dumps(configuration(),separators=(",",":")).encode()
        a,b=v.parse_configuration(raw),v.parse_configuration(compact)
        self.assertEqual(a["configurationHash"],b["configurationHash"])
        self.assertNotEqual(a["configurationSha256"],b["configurationSha256"])
        self.assertEqual(v.control_hash([v.PREFIX+a["configurationSha256"]],"defines"),a["configurationSha256"])
        for defines in ([],[v.PREFIX+"a"*64,v.PREFIX+"b"*64],[v.PREFIX+"a"*64]*2,["UNITY_EDITOR",v.PREFIX+"a"*64],[v.PREFIX+"A"*64]):
            with self.assertRaises(VerificationError):v.control_hash(defines,"bad control")

    def test_every_field_and_exact_literal_flags_required(self):
        original=configuration()
        mutations=[lambda x:x.update(schemaVersion=True),lambda x:x.update(policy="assembly-shadow-reflection-configuration:2"),
                   lambda x:x["sites"][0].update(operationIndex=True),lambda x:x["sites"][0].update(operationIndex=1<<31),
                   lambda x:x["sites"][0].update(ignoreCase=0),lambda x:x["sites"][0].update(typeName="Dynamic.Type"),
                   lambda x:x["sites"][0].update(operationSignature="System.Reflection.Assembly System.Reflection.Assembly::LoadFrom(System.String)"),
                   lambda x:x["sites"][0].update(providerAssemblyIdentity="Provider"),lambda x:x["sites"].append(copy.deepcopy(x["sites"][0]))]
        mutations += [lambda x,key=key:x["sites"][0].pop(key) for key in original["sites"][0]]
        for mutate in mutations:
            bad=copy.deepcopy(original);mutate(bad)
            with self.assertRaises(VerificationError):v.parse_configuration(json.dumps(bad).encode())
        raw=json.dumps(original)[:-1]+',"schemaVersion":1}'
        with self.assertRaises(VerificationError):v.parse_configuration(raw.encode())

    def test_module_type_is_concrete_case_sensitive_and_throwing(self):
        value=configuration();site=value["sites"][0]
        site.update(operationSignature=list(v.OPERATIONS)[-1],typeName="Example.Concrete",throwOnError=True)
        v.parse_configuration(json.dumps(value).encode())
        for update in (dict(typeName="T[]"),dict(typeName=""),dict(ignoreCase=True),dict(throwOnError=False)):
            bad=copy.deepcopy(value);bad["sites"][0].update(update)
            with self.assertRaises(VerificationError):v.parse_configuration(json.dumps(bad).encode())

    def test_inventory_hash_reads_actual_flags_nesting_arity_and_base(self):
        base=[dict(name="Owner",arity=1),dict(name="Inner",namespace="",flags=2,parent=2)]
        original=v.type_inventory_hash(MethodProof(make_type_pe(base),"inventory"))
        for update in (dict(flags=0),dict(arity=2),dict(name="Changed"),dict(extends=9)):
            changed=copy.deepcopy(base);changed[0].update(update)
            self.assertNotEqual(original,v.type_inventory_hash(MethodProof(make_type_pe(changed),"changed inventory")))


class RawByteProofTests(unittest.TestCase):
    def test_actual_metadata_signature_body_and_literal_chain(self):
        data,modules,site=raw_helper_fixture();proof=modules["Bootstrap"]
        self.assertEqual(proof.method_hash(1),"672d291d1c226c7cb55a235c17c86eb162bfd2789d547563f2dad7beb54dbe57")
        self.assertEqual(v.find_method(proof,"Queries",site["methodSignature"]),1)
        self.assertEqual(v.verify_chains(proof,1,[site],modules.__getitem__),{"raw-types":1})
        for change in (dict(operationIndex=1),dict(operationIndex=99),dict(providerAssemblyIdentity="Other, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null")):
            altered=dict(site,**change)
            with self.assertRaises((VerificationError,KeyError)):v.verify_chains(proof,1,[altered],modules.__getitem__)

    def test_rehashed_dll_cannot_replace_literal_receiver_with_suffix_or_alias(self):
        def suffix(tokens):return b"\x72"+struct.pack("<I",tokens["Provider.dll"])+b"\x28\x01\0\0\x0a\x6f\x02\0\0\x0a\x2a"
        _,modules,site=raw_helper_fixture(suffix)
        with self.assertRaisesRegex(VerificationError,"exact provider simple-name"):v.verify_chains(modules["Bootstrap"],1,[site],modules.__getitem__)
        def alias(tokens):return b"\x72"+struct.pack("<I",tokens["Provider"])+b"\x28\x01\0\0\x0a\x0a\x06\x6f\x02\0\0\x0a\x2a"
        _,modules,site=raw_helper_fixture(alias,locals=b"\x07\x01\x12\x05");site["operationIndex"]=4
        with self.assertRaises(VerificationError):v.verify_chains(modules["Bootstrap"],1,[site],modules.__getitem__)

    def test_branch_cannot_bypass_receiver_and_boundaries_are_actual(self):
        def bypass(tokens):return b"\x2b\x05\x72"+struct.pack("<I",tokens["Provider"])+b"\x28\x01\0\0\x0a\x6f\x02\0\0\x0a\x2a"
        _,modules,site=raw_helper_fixture(bypass);site["operationIndex"]=3
        with self.assertRaisesRegex(VerificationError,"branch bypasses"):v.verify_chains(modules["Bootstrap"],1,[site],modules.__getitem__)
        def misaligned(tokens):return b"\x2b\x01\x72"+struct.pack("<I",tokens["Provider"])+b"\x28\x01\0\0\x0a\x6f\x02\0\0\x0a\x2a"
        with self.assertRaisesRegex(VerificationError,"instruction boundaries"):raw_helper_fixture(misaligned)

    def test_strings_tokens_native_headers_and_synthetic_array_fail_closed(self):
        for body in (lambda _:b"\x72\xff\xff\xff\x70\x2a",lambda _:b"\x16\x8d\x02\0\0\x01\x2a",
                     lambda _:b"\x28\x01\0\0\x04\x2a"):
            with self.assertRaises(VerificationError):raw_helper_fixture(body)
        for changes in (dict(impl=4096),dict(flags=6),dict(impl=1)):
            with self.assertRaises(VerificationError):raw_helper_fixture(**changes)
        data,_,_=raw_helper_fixture();proof=v.RawMethodProof(data,"header");offset=proof.rva(proof.tables.row(6,1)[0],12)
        corrupt=bytearray(data);struct.pack_into("<H",corrupt,offset,0x301b)
        with self.assertRaisesRegex(VerificationError,"header/EH"):v.RawMethodProof(bytes(corrupt),"EH").method_hash(1)

    def test_parameters_attributes_and_locals_are_part_of_actual_hash(self):
        _,modules,_=raw_helper_fixture();original=modules["Bootstrap"].method_hash(1)
        _,modules,_=raw_helper_fixture(locals=b"\x07\x01\x08")
        self.assertNotEqual(original,modules["Bootstrap"].method_hash(1))
        _,modules,_=raw_helper_fixture(parameters=["actualArgument"])
        self.assertNotEqual(original,modules["Bootstrap"].method_hash(1))
        # A no-argument attribute constructor is actual metadata, not a
        # selected textual spelling. Signature/blob disagreement is rejected.
        with self.assertRaisesRegex(VerificationError,"attribute signature/blob mismatch"):raw_helper_fixture(attribute=1)

    def test_actual_corlib_definition_and_identity_required(self):
        _,modules,site=raw_helper_fixture();proof=modules["Bootstrap"]
        modules["mscorlib"]=v.RawMethodProof(raw_pe("mscorlib",[dict(name="Assembly",namespace="System.Reflection")],core=True),"missing core")
        with self.assertRaisesRegex(VerificationError,"missing/ambiguous"):v.verify_chains(proof,1,[site],modules.__getitem__)
        modules["mscorlib"]=v.RawMethodProof(raw_pe("Impostor",[dict(name="Assembly",namespace="System.Reflection")]),"fake core")
        with self.assertRaisesRegex(VerificationError,"identity differs"):v.verify_chains(proof,1,[site],modules.__getitem__)

    def test_catalog_hash_paths_and_duplicates_are_bound(self):
        data,_,_=raw_helper_fixture()
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory).resolve();(root/"helper.dll").write_bytes(data)
            row=dict(name="Bootstrap",path="helper.dll",sha256=hashlib.sha256(data).hexdigest())
            self.assertEqual(v.Catalog(root,[row])("Bootstrap").identity["name"],"Bootstrap")
            for changed in (dict(row,sha256="a"*64),dict(row,path="../helper.dll"),dict(row,path="./helper.dll"),dict(row,name="Wrong")):
                with self.assertRaises(VerificationError):v.Catalog(root,[changed])(changed["name"])
            with self.assertRaises(VerificationError):v.Catalog(root,[row,dict(row,name="BOOTSTRAP")])
            (root/"alias.dll").symlink_to(root/"helper.dll")
            with self.assertRaises(VerificationError):v.Catalog(root,[dict(row,path="alias.dll")])("Bootstrap")


class RawSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.snapshot,self.config,self.receipt=write_raw_snapshot(self.root)
        self.path=self.root/"RawTypeAdmissions/compiled-evidence.json"

    def test_full_25_site_compiler_proof_is_independently_rebuilt(self):
        actual=v.verify_snapshot(self.root,self.snapshot)
        self.assertEqual(actual["configuration"],self.config)
        self.assertEqual(len(actual["configuration"]["sites"]),25)

    def test_every_receipt_field_and_lossless_type_is_required(self):
        mutations=[lambda x:x.update(schemaVersion=True),lambda x:x.update(buildGuid="other-player"),lambda x:x.update(sites=None),
                   lambda x:x["sites"][0].update(operationIndex=True),lambda x:x["sites"][0].update(ignoreCase=0),
                   lambda x:x["sites"][0].update(providerInventoryHash="b"*64),lambda x:x["sites"][0].update(linkedMethodHash="b"*64),
                   lambda x:x["sites"].reverse(),lambda x:x["sites"].append(copy.deepcopy(x["sites"][0]))]
        mutations += [lambda x,k=k:x.pop(k) for k in self.receipt]
        mutations += [lambda x,k=k:x["sites"][0].pop(k) for k in self.receipt["sites"][0]]
        for mutate in mutations:
            altered=copy.deepcopy(self.receipt);mutate(altered);self.path.write_text(json.dumps(altered,indent=4))
            with self.subTest(mutation=mutate):
                with self.assertRaises(VerificationError):v.verify_snapshot(self.root,self.snapshot)

    def test_duplicate_json_unknown_fields_and_noncanonical_receipt_bytes_fail(self):
        raw=json.dumps(self.receipt,indent=4)
        for text in (raw+'\n',json.dumps(self.receipt),raw[:-1]+',"schemaVersion":1}',raw[:-1]+',"unknown":true}'):
            self.path.write_text(text)
            with self.assertRaises(VerificationError):v.verify_snapshot(self.root,self.snapshot)

    def test_exact_provider_operation_coverage_and_compiled_roles(self):
        bad=copy.deepcopy(self.config);bad["sites"].pop()
        raw=json.dumps(bad).encode();(self.root/"RawTypeAdmissions/configuration.json").write_bytes(raw)
        altered=copy.deepcopy(self.snapshot);altered["extraScriptingDefines"]=[v.PREFIX+hashlib.sha256(raw).hexdigest()]
        with self.assertRaisesRegex(VerificationError,"five raw operations"):v.verify_snapshot(self.root,altered)
        raw=json.dumps(self.config).encode();(self.root/"RawTypeAdmissions/configuration.json").write_bytes(raw)
        altered["extraScriptingDefines"]=[v.PREFIX+hashlib.sha256(raw).hexdigest()]
        altered["filteredAssemblies"].append(altered["assemblies"].pop())
        with self.assertRaisesRegex(VerificationError,"actual compiled runtime input"):v.verify_snapshot(self.root,altered)

    def test_rehashed_changed_helper_still_requires_actual_literal_receiver(self):
        entry=next(row for row in self.snapshot["assemblies"] if row["name"]=="AssemblyShadowDemo.Bootstrap")
        path=self.root/entry["path"];raw=path.read_bytes();old="AssemblyA.Contracts".encode("utf-16-le")
        self.assertGreaterEqual(raw.count(old),1)
        raw=raw.replace(old,"AssemblyB.Contracts".encode("utf-16-le"),1);path.write_bytes(raw);entry["sha256"]=hashlib.sha256(raw).hexdigest()
        proof=v.RawMethodProof(raw,path)
        for site in self.config["sites"]:site["methodHash"]=proof.method_hash(v.find_method(proof,site["declaringType"],site["methodSignature"]))
        raw=json.dumps(self.config).encode();(self.root/"RawTypeAdmissions/configuration.json").write_bytes(raw)
        self.snapshot["extraScriptingDefines"]=[v.PREFIX+hashlib.sha256(raw).hexdigest()]
        with self.assertRaisesRegex(VerificationError,"exact provider simple-name"):v.verify_snapshot(self.root,self.snapshot)

    def test_missing_linked_proof_extra_files_symlinks_and_aliases_fail(self):
        with self.assertRaisesRegex(VerificationError,"proof files"):v.verify_snapshot(self.root,self.snapshot,require_linked=True)
        extra=self.root/"RawTypeAdmissions/linked-evidence.json";extra.write_text('{}')
        with self.assertRaisesRegex(VerificationError,"proof files"):v.verify_snapshot(self.root,self.snapshot)
        extra.unlink();extra.symlink_to(self.path)
        with self.assertRaisesRegex(VerificationError,"proof files"):v.verify_snapshot(self.root,self.snapshot)
        extra.unlink()
        with self.assertRaises(VerificationError):v.verify_snapshot(self.root/".."/self.root.name,self.snapshot)

    def test_no_control_config_hash_replacement_or_raw_only_linked_fallback(self):
        for defines in ([],[v.PREFIX+"a"*64]):
            with self.assertRaises(VerificationError):v.verify_snapshot(self.root,dict(self.snapshot,extraScriptingDefines=defines))
        linked=dict(self.snapshot,linkedPlayerReceipt=dict(assemblies=[]),buildGuid="guid",linkedPlayerReceiptHash="a"*64)
        (self.root/"RawTypeAdmissions/linked-evidence.json").write_text('{}')
        with self.assertRaises(VerificationError):v.verify_snapshot(self.root,linked,require_linked=True)


class CapturedForwarderTests(unittest.TestCase):
    def test_actual_exportedtype_rows_and_linked_definitions_are_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory).resolve();(root/"ReflectionBindings/LinkedRetargeting").mkdir(parents=True);(root/"LinkedPlayer").mkdir()
            core=raw_pe("mscorlib",[dict(name="Object",namespace="System"),dict(name="String",namespace="System")],core=True)
            path=root/"LinkedPlayer/mscorlib.dll";path.write_bytes(core);identity=v.RawMethodProof(core,path).identity
            row=dict(name="mscorlib",path="LinkedPlayer/mscorlib.dll",sha256=hashlib.sha256(core).hexdigest())
            facade=raw_pe("netstandard",[],references=["mscorlib"],version=(2,1,0,0),public_token=bytes.fromhex("cc7b13ffcd2ddd51"),
                          exported=[dict(name="Object",namespace="System",implementation=5),dict(name="String",namespace="System",implementation=5)])
            facade_path=root/"ReflectionBindings/LinkedRetargeting/netstandard.dll.bytes";facade_path.write_bytes(facade)
            receipt=dict(facadePath="ReflectionBindings/LinkedRetargeting/netstandard.dll.bytes",facadeSha256=hashlib.sha256(facade).hexdigest(),profileHash="a"*64,
                         forwarders=[dict(typeFullName="System."+name,destinationAssemblyIdentity=identity["fullName"]) for name in ("Object","String")],
                         runtimeFrameworkModules=[dict(assemblyIdentity=identity["fullName"],path=row["path"],sha256=row["sha256"],mvid=identity["mvid"])])
            receipt_path=root/"ReflectionBindings/LinkedRetargeting/evidence.json";receipt_path.write_text(json.dumps(receipt))
            # Unit boundary only: old full receipt proof is separately exercised
            # by the accepted suite. Here test the NEW actual facade/table proof.
            with patch.object(v,"_reflection_snapshot",return_value={}):
                _,scope=v.captured_profile(root,{},v.Catalog(root,[row]))
                self.assertEqual(scope("System.String","netstandard, Version=2.1.0.0, Culture=neutral, PublicKeyToken=cc7b13ffcd2ddd51"),identity["fullName"])
                with self.assertRaises(VerificationError):scope("System.Missing","netstandard, Version=2.1.0.0, Culture=neutral, PublicKeyToken=cc7b13ffcd2ddd51")
                receipt["forwarders"][0]["typeFullName"]="System.Fabricated";receipt_path.write_text(json.dumps(receipt))
                with self.assertRaisesRegex(VerificationError,"actual facade ExportedType"):v.captured_profile(root,{},v.Catalog(root,[row]))
                receipt["forwarders"][0]["typeFullName"]="System.Object"
                proof=v.RawMethodProof(facade,"facade");offset=facade.index(proof.tables.reader.data)+proof.tables.offsets[39]
                altered=bytearray(facade);struct.pack_into("<H",altered,offset+12,13)
                facade_path.write_bytes(altered);receipt["facadeSha256"]=hashlib.sha256(altered).hexdigest();receipt_path.write_text(json.dumps(receipt))
                with self.assertRaisesRegex(VerificationError,"Implementation coded index"):v.captured_profile(root,{},v.Catalog(root,[row]))

    def test_retarget_hash_requires_actual_scope_map_not_receipt_copy(self):
        _,modules,_=raw_helper_fixture();proof=modules["Bootstrap"]
        original=proof.method_hash(1)
        self.assertEqual(original,proof.method_hash(1,lambda name,assembly:assembly))
        self.assertNotEqual(original,proof.method_hash(1,lambda name,assembly:"Other, Version=4.0.0.0, Culture=neutral, PublicKeyToken=null"))


class ProviderExportBoundaryTests(unittest.TestCase):
    TYPE_ARRAY=b"\x1d\x12\x19"
    def fixture(self,**kwargs):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        root=Path(temporary.name).resolve();snapshot,config,receipt=write_raw_snapshot(root,**kwargs)
        return root,snapshot,config

    def verify(self,root,snapshot,config):
        files=[row for section in ("assemblies","filteredAssemblies","references") for row in snapshot[section]]
        names=[row["name"] for section in ("assemblies","filteredAssemblies") for row in snapshot[section]]
        return v.verify_provider_boundary(v.Catalog(root,files),config["sites"],names)

    def external(self,root,snapshot,owner=v.HELPER_TYPE,member=None,literal=None,section="assemblies"):
        namespace,name=owner.rsplit(".",1)
        data=raw_pe("Unexplained.Consumer",[dict(name="Use")],references=["AssemblyShadowDemo.Bootstrap","mscorlib"],
                    type_refs=[(6,namespace,name),(10,"System","Type")] if member or literal is None else [],
                    member_refs=[(1,member,b"\x00\x01\x1d\x12\x09\x0e")] if member else [],user_strings=[literal] if literal else [])
        path=root/"Assemblies/Unexplained.Consumer.dll";path.write_bytes(data)
        snapshot[section].append(dict(name="Unexplained.Consumer",path="Assemblies/Unexplained.Consumer.dll",sha256=hashlib.sha256(data).hexdigest()))

    def test_actual_external_helper_typeref_and_exact_reflection_literal_fail(self):
        for literal in (None,v.HELPER_TYPE,v.HELPER_TYPE+", AssemblyShadowDemo.Bootstrap",
                        v.HELPER_TYPE+", AssemblyShadowDemo.Bootstrap, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null"):
            root,snapshot,config=self.fixture();self.external(root,snapshot,literal=literal)
            with self.assertRaisesRegex(VerificationError,"non-consumer"):self.verify(root,snapshot,config)

    def test_filtered_runtime_and_linked_phase_inventory_get_the_same_gate(self):
        root,snapshot,config=self.fixture();self.external(root,snapshot,section="filteredAssemblies")
        with self.assertRaisesRegex(VerificationError,"non-consumer"):v.verify_snapshot(root,snapshot)
        files=[dict(row,path=row["path"]) for section in ("assemblies","filteredAssemblies","references") for row in snapshot[section]]
        # A linked catalog's phase is not an escape hatch: actual linked module
        # imports are checked with the same byte-bound boundary function.
        with self.assertRaisesRegex(VerificationError,"non-consumer"):
            v.verify_provider_boundary(v.Catalog(root,files),config["sites"],[row["name"] for row in files])

    def test_private_selector_forwarder_survives_but_external_import_does_not(self):
        method=dict(name="Select",flags=0x11,signature=b"\x00\x01"+self.TYPE_ARRAY+b"\x0e",body=b"\x02\x28\x01\0\0\x06\x2a")
        root,snapshot,config=self.fixture(extra_types=[dict(name="ProviderBridge",namespace="AssemblyShadowDemo",methods=[method])])
        result=self.verify(root,snapshot,config)
        self.assertIn(("AssemblyShadowDemo.ProviderBridge","Select"),next(iter(result.values()))[1])
        self.external(root,snapshot,owner="AssemblyShadowDemo.ProviderBridge",member="Select")
        with self.assertRaisesRegex(VerificationError,"selector forwarder"):self.verify(root,snapshot,config)

    def test_generic_methodspec_forwarder_is_exact_and_not_a_bypass(self):
        methods=[dict(name="GenericSelect",arity=1,signature=b"\x10\x01\x01"+self.TYPE_ARRAY+b"\x0e",body=b"\x02\x28\x01\0\0\x06\x2a"),
                 dict(name="Select",signature=b"\x00\x01"+self.TYPE_ARRAY+b"\x0e",body=b"\x02\x28\x01\0\0\x2b\x2a")]
        root,snapshot,config=self.fixture(extra_types=[dict(name="ProviderBridge",namespace="AssemblyShadowDemo",methods=methods)],method_specs=[(12,b"\x0a\x01\x08")])
        symbols=next(iter(self.verify(root,snapshot,config).values()))[1]
        self.assertIn(("AssemblyShadowDemo.ProviderBridge","Select"),symbols)
        self.external(root,snapshot,owner="AssemblyShadowDemo.ProviderBridge",member="Select")
        with self.assertRaises(VerificationError):self.verify(root,snapshot,config)
        root,snapshot,config=self.fixture(extra_types=[dict(name="ProviderBridge",namespace="AssemblyShadowDemo",methods=methods)],method_specs=[(12,b"\x0a\x00")])
        with self.assertRaisesRegex(VerificationError,"MethodSpec arity"):self.verify(root,snapshot,config)

    def test_methodspec_substitutes_actual_return_type_without_linq_false_taint(self):
        method=dict(name="Identity",arity=1,signature=b"\x10\x01\x01\x1e\x00\x1e\x00",body=b"\x02\x2a")
        root,snapshot,config=self.fixture(extra_types=[dict(name="Opaque",methods=[method])],
                                           method_specs=[(12,b"\x0a\x01\x0e"),(12,b"\x0a\x01"+self.TYPE_ARRAY)])
        files=[row for section in ("assemblies","references") for row in snapshot[section]]
        catalog=v.Catalog(root,files);boundary=v.ProviderBoundary(catalog,config["sites"],[]);proof=catalog("AssemblyShadowDemo.Bootstrap")
        self.assertFalse(boundary.capable(boundary.method(proof,0x2b000001)[3][2]))
        self.assertTrue(boundary.capable(boundary.method(proof,0x2b000002)[3][2]))
        self.verify(root,snapshot,config)

    def test_custom_callback_selector_and_action_int_are_not_conflated(self):
        factory=dict(name="Factory",namespace="AssemblyShadowDemo",extends=45,methods=[dict(name="Invoke",flags=0x46,impl=4096,signature=b"\x20\x00"+self.TYPE_ARRAY)])
        observer=dict(name="IntegerAction",namespace="AssemblyShadowDemo",extends=45,methods=[dict(name="Invoke",flags=0x46,impl=4096,signature=b"\x20\x01\x01\x08")])
        methods=[dict(name="SelectorCallback",signature=b"\x00\x01\x01\x12\x0c",body=b"\x14\x28\x01\0\0\x06\x26\x2a"),
                 dict(name="IntegerCallback",signature=b"\x00\x01\x01\x12\x10",body=b"\x14\x28\x01\0\0\x06\x26\x2a")]
        root,snapshot,config=self.fixture(extra_types=[factory,observer,dict(name="ProviderBridge",namespace="AssemblyShadowDemo",methods=methods)],extra_refs=[("System","MulticastDelegate")])
        symbols=next(iter(self.verify(root,snapshot,config).values()))[1]
        self.assertIn(("AssemblyShadowDemo.ProviderBridge","SelectorCallback"),symbols)
        self.assertNotIn(("AssemblyShadowDemo.ProviderBridge","IntegerCallback"),symbols)

    def test_rehashed_wrong_version_reference_does_not_hide_helper_import(self):
        root,snapshot,config=self.fixture();self.external(root,snapshot)
        entry=snapshot["assemblies"][-1];path=root/entry["path"];raw=path.read_bytes();proof=v.ImportModule(raw,path)
        offset=raw.index(proof.tables.reader.data)+proof.tables.offsets[35]
        changed=bytearray(raw);struct.pack_into("<H",changed,offset,9);path.write_bytes(changed);entry["sha256"]=hashlib.sha256(changed).hexdigest()
        with self.assertRaisesRegex(VerificationError,"non-consumer imports"):self.verify(root,snapshot,config)

    def test_broker_method_type_tokens_and_delegate_targets_fail(self):
        for body in (b"\xfe\x06\x01\0\0\x06\x26\x2a",b"\x14\xfe\x07\x01\0\0\x06\x26\x2a",
                     b"\xd0\x01\0\0\x06\x26\x2a",b"\xd0\x02\0\0\x02\x26\x2a"):
            root,snapshot,config=self.fixture(extra_types=[dict(name="Escape",methods=[dict(name="Leak",signature=b"\x00\x00\x01",body=body)])])
            with self.assertRaisesRegex(VerificationError,"escape"):self.verify(root,snapshot,config)

    def test_static_helper_shape_and_external_virtual_selector_fail(self):
        for changes in (dict(flags=1),dict(interfaces=[5]),dict(fields=[dict(name="Broker",signature=b"\x06\x1c")])):
            root,snapshot,config=self.fixture(helper_changes=changes)
            with self.assertRaisesRegex(VerificationError,"admitted helper"):self.verify(root,snapshot,config)
        method=dict(name="Select",flags=0x46,signature=b"\x20\x01"+self.TYPE_ARRAY+b"\x0e",body=b"\x03\x28\x01\0\0\x06\x2a")
        root,snapshot,config=self.fixture(extra_types=[dict(name="InterfaceBroker",interfaces=[5],methods=[method])])
        with self.assertRaisesRegex(VerificationError,"virtual/interface"):self.verify(root,snapshot,config)

    def test_selected_value_field_store_rejects_but_unselected_cache_does_not(self):
        field=dict(name="Export",signature=b"\x06"+self.TYPE_ARRAY)
        leak=dict(name="Store",signature=b"\x00\x01\x01\x0e",body=b"\x02\x28\x01\0\0\x06\x80\x01\0\0\x04\x2a")
        root,snapshot,config=self.fixture(extra_types=[dict(name="FieldBroker",fields=[field],methods=[leak])])
        with self.assertRaisesRegex(VerificationError,"external field"):self.verify(root,snapshot,config)
        # Same method calls a selector, discards its result, then stores an
        # unrelated value: method-level 'has selector' taint must not reject.
        safe=dict(leak,body=b"\x02\x28\x01\0\0\x06\x26\x14\x80\x01\0\0\x04\x2a")
        root,snapshot,config=self.fixture(extra_types=[dict(name="OpaqueCache",fields=[field],methods=[safe])])
        self.verify(root,snapshot,config)

    def test_field_value_flows_through_locals_calls_and_private_getter(self):
        field=dict(name="Cache",flags=0x11,signature=b"\x06"+self.TYPE_ARRAY)
        methods=[dict(name="Store",signature=b"\x00\x01\x01\x0e",locals=b"\x07\x01"+self.TYPE_ARRAY,
                      body=b"\x02\x28\x01\0\0\x06\x0a\x06\x28\x07\0\0\x06\x2a"),
                 dict(name="Set",signature=b"\x00\x01\x01"+self.TYPE_ARRAY,body=b"\x02\x80\x01\0\0\x04\x2a"),
                 dict(name="Read",signature=b"\x00\x00"+self.TYPE_ARRAY,body=b"\x7e\x01\0\0\x04\x2a")]
        root,snapshot,config=self.fixture(extra_types=[dict(name="ProviderBridge",namespace="AssemblyShadowDemo",fields=[field],methods=methods)])
        symbols=next(iter(self.verify(root,snapshot,config).values()))[1]
        self.assertIn(("AssemblyShadowDemo.ProviderBridge","Read"),symbols)
        self.external(root,snapshot,owner="AssemblyShadowDemo.ProviderBridge",member="Read")
        with self.assertRaisesRegex(VerificationError,"selector forwarder"):self.verify(root,snapshot,config)

    def test_void_bool_string_int_diagnostics_and_opaque_type_array_do_not_propagate(self):
        methods=[]
        for name,result,tail in (("Observe",b"\x01",b""),("MoveNext",b"\x02",b"\x16"),("Count",b"\x08",b"\x16"),("Name",b"\x0e",b"\x14")):
            methods.append(dict(name=name,signature=b"\x00\x01"+result+b"\x0e",body=b"\x02\x28\x01\0\0\x06\x26"+tail+b"\x2a"))
        methods.append(dict(name="Opaque",signature=b"\x00\x01"+self.TYPE_ARRAY+self.TYPE_ARRAY,body=b"\x02\x2a"))
        root,snapshot,config=self.fixture(extra_types=[dict(name="Diagnostics",namespace="AssemblyShadowDemo",methods=methods)])
        symbols=next(iter(self.verify(root,snapshot,config).values()))[1]
        self.assertFalse(any(owner=="AssemblyShadowDemo.Diagnostics" for owner,_ in symbols))
        self.external(root,snapshot,owner="AssemblyShadowDemo.Diagnostics",member="Opaque")
        self.verify(root,snapshot,config)

    def test_void_selected_write_to_caller_array_is_not_an_opaque_diagnostic(self):
        # Actual SelectInto(string name, object[] sink) IL: a void signature
        # cannot hide sink[0] = admitted GetTypes(name).
        for store in (b"\xa2",b"\xa4\x01\0\0\x01"):
            method=dict(name="SelectInto",signature=b"\x00\x02\x01\x0e\x1d\x1c",
                        body=b"\x03\x16\x02\x28\x01\0\0\x06"+store+b"\x2a")
            root,snapshot,config=self.fixture(extra_types=[dict(name="ProviderBridge",namespace="AssemblyShadowDemo",methods=[method])])
            # Include the exact outside MemberRef with a truthful void/sink
            # signature; the consumer effect fails even before import scans.
            data=raw_pe("Outside",[dict(name="Use",methods=[dict(name="Run",signature=b"\x00\x00\x01",
                body=b"\x14\x17\x8d\x02\0\0\x01\x25\x0a\x28\x01\0\0\x0a\x06\x16\x9a\x26\x2a",locals=b"\x07\x01\x1d\x1c")])],
                references=["AssemblyShadowDemo.Bootstrap","mscorlib"],type_refs=[(6,"AssemblyShadowDemo","ProviderBridge"),(10,"System","Object")],
                member_refs=[(1,"SelectInto",b"\x00\x02\x01\x0e\x1d\x1c")])
            path=root/"Assemblies/Outside.dll";path.write_bytes(data)
            snapshot["assemblies"].append(dict(name="Outside",path="Assemblies/Outside.dll",sha256=hashlib.sha256(data).hexdigest()))
            with self.assertRaisesRegex(VerificationError,"selected handle array store"):self.verify(root,snapshot,config)

    def test_void_selected_indirect_outputs_fail(self):
        for store in (b"\x51",b"\x81\x01\0\0\x01"):
            method=dict(name="SelectOut",signature=b"\x00\x02\x01\x0e\x10\x1c",
                        body=b"\x03\x02\x28\x01\0\0\x06"+store+b"\x2a")
            root,snapshot,config=self.fixture(extra_types=[dict(name="Output",methods=[method])])
            with self.assertRaisesRegex(VerificationError,"selected handle indirect store"):self.verify(root,snapshot,config)

    def test_selected_local_array_materialization_and_alias_reads_survive(self):
        method=dict(name="LocalMaterialize",signature=b"\x00\x01\x01\x0e",locals=b"\x07\x02\x1d\x1c\x1d\x1c",
                    body=b"\x17\x8d\x01\0\0\x01\x25\x0a\x0b\x07\x16\x02\x28\x01\0\0\x06\xa2\x06\x16\x9a\x26\x2a")
        root,snapshot,config=self.fixture(extra_types=[dict(name="LocalMaterialization",methods=[method])])
        self.verify(root,snapshot,config)

    def test_local_materialized_selected_read_cannot_escape_through_field(self):
        method=dict(name="MaterializeThenExport",signature=b"\x00\x01\x01\x0e",locals=b"\x07\x01\x1d\x1c",
                    body=b"\x17\x8d\x01\0\0\x01\x0a\x06\x16\x02\x28\x01\0\0\x06\xa2\x06\x16\x9a\x80\x01\0\0\x04\x2a")
        root,snapshot,config=self.fixture(extra_types=[dict(name="LocalLeak",methods=[method],fields=[dict(name="Export",signature=b"\x06\x1c")])])
        with self.assertRaisesRegex(VerificationError,"external field"):self.verify(root,snapshot,config)

    def test_local_array_escape_before_or_after_selected_write_fails(self):
        allocate=b"\x17\x8d\x01\0\0\x01\x0a"
        store=b"\x06\x16\x02\x28\x01\0\0\x06\xa2"
        for escape in (b"\x06\x80\x01\0\0\x04",b"\x03\x16\x06\xa2",b"\x06\x28\x07\0\0\x06"):
            for before in (True,False):
                method=dict(name="Leak",signature=b"\x00\x02\x01\x0e\x1d\x1c",locals=b"\x07\x01\x1d\x1c",
                            body=allocate+(escape+store if before else store+escape)+b"\x2a")
                opaque=dict(name="OpaqueSink",signature=b"\x00\x01\x01\x1d\x1c",body=b"\x2a")
                root,snapshot,config=self.fixture(extra_types=[dict(name="LocalLeak",methods=[method,opaque],fields=[dict(name="Export",signature=b"\x06\x1d\x1c")])])
                with self.assertRaisesRegex(VerificationError,"container escapes local ownership"):self.verify(root,snapshot,config)

    def test_nested_local_container_ownership_is_transitive(self):
        allocate=b"\x17\x8d\x01\0\0\x01\x0a\x17\x8d\x01\0\0\x01\x0b"
        nest=b"\x07\x16\x06\xa2"
        store=b"\x06\x16\x02\x28\x01\0\0\x06\xa2"
        for escape in (b"",b"\x07\x80\x01\0\0\x04"):
            method=dict(name="Nested",signature=b"\x00\x01\x01\x0e",locals=b"\x07\x02\x1d\x1c\x1d\x1c",body=allocate+nest+escape+store+b"\x2a")
            root,snapshot,config=self.fixture(extra_types=[dict(name="Local",methods=[method],fields=[dict(name="Export",signature=b"\x06\x1d\x1c")])])
            if escape:
                with self.assertRaisesRegex(VerificationError,"container escapes local ownership"):self.verify(root,snapshot,config)
            else:self.verify(root,snapshot,config)

    def test_nested_array_read_keeps_alias_before_later_selected_mutation(self):
        # Store the inner array in a local outer array, then pass an element
        # read to an unknown sink before filling the original inner alias.
        method=dict(name="NestedLeak",signature=b"\x00\x01\x01\x0e",locals=b"\x07\x02\x1d\x1c\x1d\x1c",
                    body=b"\x17\x8d\x01\0\0\x01\x0a\x17\x8d\x01\0\0\x01\x0b\x07\x16\x06\xa2"
                         b"\x07\x16\x9a\x28\x07\0\0\x06\x06\x16\x02\x28\x01\0\0\x06\xa2\x2a")
        sink=dict(name="Sink",signature=b"\x00\x01\x01\x1c",body=b"\x2a")
        root,snapshot,config=self.fixture(extra_types=[dict(name="Nested",methods=[method,sink])])
        with self.assertRaisesRegex(VerificationError,"container escapes local ownership"):self.verify(root,snapshot,config)

    def test_branch_merge_cannot_turn_caller_array_into_proven_local_ownership(self):
        # if (flag) local = new object[1]; else local = callerSink;
        # local[0] = selected. The merge must preserve nonlocal possibility.
        method=dict(name="Merge",signature=b"\x00\x03\x01\x0e\x1d\x1c\x02",locals=b"\x07\x01\x1d\x1c",
                    body=b"\x04\x2c\x09\x17\x8d\x01\0\0\x01\x0a\x2b\x02\x03\x0a"
                         b"\x06\x16\x02\x28\x01\0\0\x06\xa2\x2a")
        root,snapshot,config=self.fixture(extra_types=[dict(name="Merge",methods=[method])])
        with self.assertRaisesRegex(VerificationError,"selected handle array store"):self.verify(root,snapshot,config)

    def test_external_custom_callback_actual_invoke_signature_carries_output(self):
        for selected in (True,False):
            parameter=self.TYPE_ARRAY if selected else b"\x08"
            body=b"\x03\x02\x28\x01\0\0\x06"+(b"" if selected else b"\x26\x16")+b"\x6f\x08\0\0\x0a\x2a"
            method=dict(name="SelectWithCallback",signature=b"\x00\x02\x01\x0e\x12\x2d",body=body)
            root,snapshot,config=self.fixture(extra_types=[dict(name="ProviderBridge",namespace="AssemblyShadowDemo",methods=[method])],
                extra_assemblies=["Outside"],extra_refs=[(10,"External","SelectedCallback")],extra_members=[(11,"Invoke",b"\x20\x01\x01"+parameter)])
            invoke_parameter=b"\x1d\x12\x09" if selected else b"\x08"
            data=raw_pe("Outside",[dict(name="SelectedCallback",namespace="External",extends=5,
                methods=[dict(name="Invoke",flags=0x46,impl=4096,signature=b"\x20\x01\x01"+invoke_parameter)]),
                dict(name="Use",methods=[dict(name="Run",signature=b"\x00\x00\x01",body=b"\x14\x14\x28\x01\0\0\x0a\x2a")])],
                references=["mscorlib","AssemblyShadowDemo.Bootstrap"],
                type_refs=[(6,"System","MulticastDelegate"),(6,"System","Type"),(10,"AssemblyShadowDemo","ProviderBridge")],
                member_refs=[(3,"SelectWithCallback",b"\x00\x02\x01\x0e\x12\x08")])
            path=root/"Assemblies/Outside.dll";path.write_bytes(data)
            snapshot["assemblies"].append(dict(name="Outside",path="Assemblies/Outside.dll",sha256=hashlib.sha256(data).hexdigest()))
            if selected:
                with self.assertRaisesRegex(VerificationError,"non-consumer imports a selector"):self.verify(root,snapshot,config)
            else:self.verify(root,snapshot,config)

    def test_broker_owner_nested_generic_and_array_tokens_are_not_definition_only(self):
        # TypeDef 3 is the forwarder owner. Both List<owner> and owner[]
        # expose the exact broker even though the outer type is not a broker.
        forward=dict(name="Select",signature=b"\x00\x01"+self.TYPE_ARRAY+b"\x0e",body=b"\x02\x28\x01\0\0\x06\x2a")
        token_method=dict(name="Token",signature=b"\x00\x00\x01",body=b"\xd0\x01\0\0\x1b\x26\x2a")
        for spec in (b"\x15\x12\x2d\x01\x12\x0c",b"\x1d\x12\x0c"):
            root,snapshot,config=self.fixture(extra_types=[dict(name="ProviderBridge",namespace="AssemblyShadowDemo",methods=[forward]),dict(name="Use",methods=[token_method])],
                                              extra_refs=[("System.Collections.Generic","List`1")],type_specs=[spec])
            with self.assertRaisesRegex(VerificationError,"owner type token escape"):self.verify(root,snapshot,config)
        # The same compound token around an ordinary nonbroker stays opaque.
        root,snapshot,config=self.fixture(extra_types=[dict(name="Ordinary"),dict(name="Use",methods=[token_method])],
                                          extra_refs=[("System.Collections.Generic","List`1")],type_specs=[b"\x15\x12\x2d\x01\x12\x0c"])
        self.verify(root,snapshot,config)

    def test_external_nested_broker_owner_typeref_fails_without_memberref(self):
        forward=dict(name="Select",signature=b"\x00\x01"+self.TYPE_ARRAY+b"\x0e",body=b"\x02\x28\x01\0\0\x06\x2a")
        for spec in (b"\x15\x12\x09\x01\x12\x05",b"\x1d\x12\x05"):
            root,snapshot,config=self.fixture(extra_types=[dict(name="ProviderBridge",namespace="AssemblyShadowDemo",methods=[forward])])
            data=raw_pe("Outside",[dict(name="Use",methods=[dict(name="Token",signature=b"\x00\x00\x01",body=b"\xd0\x01\0\0\x1b\x26\x2a")])],
                references=["AssemblyShadowDemo.Bootstrap","mscorlib"],type_refs=[(6,"AssemblyShadowDemo","ProviderBridge"),(10,"System.Collections.Generic","List`1")],type_specs=[spec])
            path=root/"Assemblies/Outside.dll";path.write_bytes(data)
            snapshot["assemblies"].append(dict(name="Outside",path="Assemblies/Outside.dll",sha256=hashlib.sha256(data).hexdigest()))
            with self.assertRaisesRegex(VerificationError,"non-consumer imports a selector"):self.verify(root,snapshot,config)

    @unittest.skipUnless(os.environ.get("M05_REAL_COMPILER_ROOT") and os.environ.get("M05_RAW_CONFIGURATION"),"explicit real compiler/config paths not supplied")
    def test_explicit_current_compiler_and_real_linq_cache_paths(self):
        root=Path(os.environ["M05_REAL_COMPILER_ROOT"]).resolve();config=v.parse_configuration(Path(os.environ["M05_RAW_CONFIGURATION"]).read_bytes())["configuration"]
        files=[dict(name=path.stem,path=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in root.glob("*.dll")]
        brokers=v.verify_provider_boundary(v.Catalog(root,files),config["sites"],[row["name"] for row in files])
        symbols=next(iter(brokers.values()))[1]
        self.assertEqual(len(symbols),6)
        self.assertIn(("AssemblyShadowDemo.M05TypeProbe","GetLiteralModuleType"),symbols)


if __name__=="__main__":unittest.main()
