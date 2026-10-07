"""Independent M05 literal raw-type admission proof; old binding domains stay strict.

No host framework lookup, generated type list, dynamic provider or broad method
waiver is admitted. Every operation is tied to actual compiler/linked DLL bytes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import unicodedata

from shadow_tools import VerificationError, require, unique_object
from m04_results import _fields, _absolute, _same, _rel, _obj, CANDIDATES, TYPE_NAMES
from m02_results import _reflection_full_identity, _reflection_provider, _reflection_snapshot
from m05_types import MethodProof, CliTables, Signature, IL_OPS
from m04_metadata import Reader, TABLES, CODED, _metadata, read_identity_bytes

POLICY="assembly-shadow-raw-type-admission:1"
POLICY_V2="assembly-shadow-raw-type-admission:2"
PREFIX="ASSEMBLY_SHADOW_RAW_TYPE_ADMISSION_"
SITE_FIELDS="id consumerAssembly declaringType methodSignature methodHash operationIndex operationSignature providerAssemblyIdentity typeName throwOnError ignoreCase reason"
SITE_FIELDS_V2="compilerVariants consumerAssembly declaringType id ignoreCase methodSignature operationSignature providerAssemblyIdentity reason throwOnError typeName"
VARIANT_FIELDS="compilerMode methodHash operationIndex"
COMPILER_MODES=("Development","Release")
OPERATIONS={
    "System.Type[] System.Reflection.Assembly::GetTypes()":"Assembly.GetTypes",
    "System.Collections.Generic.IEnumerable`1<System.Reflection.TypeInfo> System.Reflection.Assembly::get_DefinedTypes()":"Assembly.get_DefinedTypes",
    "System.Collections.Generic.IEnumerable`1<System.Type> System.Reflection.Assembly::get_ExportedTypes()":"Assembly.get_ExportedTypes",
    "System.Type[] System.Reflection.Module::GetTypes()":"Module.GetTypes",
    "System.Type System.Reflection.Module::GetType(System.String,System.Boolean,System.Boolean)":"Module.GetType",
}
HELPER_TYPE="AssemblyShadowDemo.M05BoundTypeQueries"
HELPER_METHODS=dict(zip(OPERATIONS,("GetTypes","GetDefinedTypes","GetExportedTypes","GetModuleTypes","GetModuleType")))


class BindingHash:
    def __init__(self,domain):self.data=bytearray();self.add(domain)
    def add(self,value):
        if value is None:self.data.extend((-1).to_bytes(4,"little",signed=True));return
        text="True" if value is True else "False" if value is False else str(value)
        raw=text.encode("utf-8",errors="strict")
        self.data.extend(len(raw).to_bytes(4,"little",signed=True));self.data.extend(raw)
    def finish(self):return hashlib.sha256(self.data).hexdigest()


def ordinal(value):return value.encode("utf-16-be",errors="strict")


def _text(value,path,empty=False):
    require(type(value) is str and (empty or value.strip()) and len(value.encode("utf-16-le"))//2<=16384 and
            all(unicodedata.category(c)!="Cc" for c in value),f"{path}: invalid bounded admission text")


def parse_configuration(raw,path="raw admission configuration"):
    require(type(raw) is bytes and 0<len(raw)<=8*1024*1024,f"{path}: invalid configuration byte length")
    try:
        value=json.loads(raw.decode("utf-8",errors="strict"),object_pairs_hook=unique_object)
        _fields(value,"schemaVersion policy sites",path)
        schema=value["schemaVersion"]
        require(type(schema) is int and ((schema==1 and value["policy"]==POLICY) or (schema==2 and value["policy"]==POLICY_V2)) and
                type(value["sites"]) is list and 0<len(value["sites"])<=4096,f"{path}: invalid raw admission domain/schema/site count")
        ids,operations,methods=set(),set(),{}
        for site in value["sites"]:
            _fields(site,SITE_FIELDS if schema==1 else SITE_FIELDS_V2,path)
            text_fields=("id","consumerAssembly","declaringType","methodSignature","operationSignature","providerAssemblyIdentity","typeName","reason")
            for key in text_fields:_text(site[key],path,key=="typeName")
            require(re.fullmatch(r"[A-Za-z0-9_.-]{1,128}",site["id"]) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*",site["consumerAssembly"]) and
                    not site["consumerAssembly"].lower().endswith(".dll"),f"{path}: invalid admission id/consumer")
            variants=[dict(compilerMode="Legacy",methodHash=site["methodHash"],operationIndex=site["operationIndex"])] if schema==1 else site["compilerVariants"]
            require(type(variants) is list and len(variants)==(1 if schema==1 else 2),f"{path}: invalid compiler variant count")
            modes=set()
            for variant in variants:
                if schema==2:_fields(variant,VARIANT_FIELDS,path)
                require(type(variant) is dict and type(variant["compilerMode"]) is str and variant["compilerMode"] not in modes and
                        re.fullmatch(r"[0-9a-f]{64}",variant["methodHash"]) and type(variant["operationIndex"]) is int and
                        0<=variant["operationIndex"]<1<<31,f"{path}: invalid actual compiler method hash/instruction index")
                modes.add(variant["compilerMode"])
            require(modes==({"Legacy"} if schema==1 else set(COMPILER_MODES)),f"{path}: incomplete/unknown compiler mode inventory")
            require(type(site["throwOnError"]) is bool and type(site["ignoreCase"]) is bool,f"{path}: missing Boolean admission flags")
            provider=_reflection_full_identity(site["providerAssemblyIdentity"],path)
            version=provider.split(", ")[1][8:].split(".")
            require(all(str(int(n))==n and 0<=int(n)<=65535 for n in version),f"{path}: noncanonical/unsupported AssemblyVersion")
            require(site["operationSignature"] in OPERATIONS,f"{path}: unsupported raw type operation")
            if OPERATIONS[site["operationSignature"]]=="Module.GetType":
                _reflection_provider(site["typeName"]+", "+provider,path)
                require(site["throwOnError"] and not site["ignoreCase"],f"{path}: unsupported Module.GetType flags")
            else:require(site["typeName"]=="" and not site["throwOnError"] and not site["ignoreCase"],f"{path}: enumeration cannot claim a type/filter")
            method=(site["consumerAssembly"].lower(),site["declaringType"],site["methodSignature"])
            profile=tuple(sorted(((variant["compilerMode"],variant["methodHash"]) for variant in variants),key=lambda row:ordinal(row[0])))
            require(site["id"] not in ids and (method not in methods or methods[method]==profile),f"{path}: duplicate/inconsistent raw admission identity")
            for variant in variants:
                operation=(*method,variant["compilerMode"],variant["operationIndex"])
                require(operation not in operations,f"{path}: duplicate raw admission operation")
                operations.add(operation)
            ids.add(site["id"]);methods[method]=profile
        require([site["id"] for site in value["sites"]]==sorted(ids,key=ordinal),f"{path}: raw admission sites must retain ordinal id order")
        canonical=BindingHash(value["policy"])
        for item in (schema,value["policy"],len(value["sites"])):canonical.add(item)
        for site in value["sites"]:
            for key in ("id","consumerAssembly","declaringType","methodSignature"):canonical.add(site[key])
            if schema==1:
                canonical.add(site["methodHash"]);canonical.add(site["operationIndex"])
            else:
                variants=sorted(site["compilerVariants"],key=lambda variant:ordinal(variant["compilerMode"]))
                canonical.add(len(variants))
                for variant in variants:
                    canonical.add(variant["compilerMode"]);canonical.add(variant["methodHash"]);canonical.add(variant["operationIndex"])
            for key in ("operationSignature","providerAssemblyIdentity","typeName","throwOnError","ignoreCase","reason"):canonical.add(site[key])
        return dict(configuration=value,configurationSha256=hashlib.sha256(raw).hexdigest(),configurationHash=canonical.finish())
    except (UnicodeError,ValueError,TypeError,KeyError) as error:
        raise VerificationError(f"{path}: invalid raw admission JSON/encoding: {error}") from error


def control_hash(defines,path):
    require(type(defines) is list and all(type(value) is str for value in defines) and len(defines)==len(set(defines)),f"{path}: invalid/duplicate compiler defines")
    controls=[value for value in defines if value.startswith(PREFIX)]
    require("UNITY_EDITOR" not in defines and len(controls)==1 and re.fullmatch(r"[0-9a-f]{64}",controls[0][len(PREFIX):]),
            f"{path}: exactly one byte-bound raw admission control is required")
    return controls[0][len(PREFIX):]


def type_inventory_hash(proof):
    """Package inventory fingerprint from independently read actual TypeDefs."""
    h=BindingHash("assembly-shadow-raw-type-inventory:1")
    h.add(proof.identity["fullName"]);h.add(len(proof.inventory["types"]))
    parents=dict(proof.tables.row(41,rid) for rid in range(1,proof.tables.counts[41]+1))
    arities={rid:row["genericArity"] for rid,row in enumerate(proof.inventory["types"],2)}
    for rid in sorted(range(2,proof.tables.counts[2]+1),key=lambda rid:ordinal(proof.type_names[rid])):
        flags,name,namespace,extends,_,_=proof.tables.row(2,rid)
        base=proof.type_identity(*proof.tables.coded(extends,"TypeDefOrRef"))[0] if extends else None
        for item in (proof.type_names[rid],proof.tables.string(namespace),proof.tables.string(name),
                     proof.type_names[parents[rid]] if rid in parents else None,arities[rid],flags,base):h.add(item)
    return h.finish()


class RawMethodProof(MethodProof):
    """Bounded independent implementation of reflection-method:1 for helpers.

    Supports finite static string-selection helpers, complete signatures,
    positional parameter metadata, no-argument attributes, locals and branch
    labels. Unsupported attributes/EH/native/generic helpers fail closed.
    """
    def core_identity(self):
        choices=[row for row in [self.identity,*self.identity["referenceIdentities"]] if row["name"] in ("mscorlib","netstandard")]
        require(len(choices)==1,f"{self.label}: ambiguous/missing actual corlib identity")
        return choices[0]["fullName"]

    def user_string(self,token):
        require(token>>24==0x70,f"{self.label}: invalid raw-helper user string token")
        raw=self.tables.blob(token&0xffffff,"#US")
        require(len(raw)%2==1 and raw[-1] in (0,1),f"{self.label}: invalid user string")
        # CLI strings are UTF-16 code-unit sequences, not necessarily Unicode
        # scalar sequences (e.g. regex ranges containing isolated surrogates).
        # Preserve their exact bytes; never replace/drop a unit before matching
        # a provider literal. Identifier #Strings decoding remains strict UTF-8.
        try:return raw[:-1].decode("utf-16-le",errors="surrogatepass")
        except UnicodeError as error:raise VerificationError(f"{self.label}: malformed user string") from error

    def body(self,rid):
        rva=self.tables.row(6,rid)[0];p=self.rva(rva,1);r=Reader(self.data,self.label)
        first=r.number(p,1);local_blob=None
        if first&3==2:start,size,init=p+1,first>>2,False
        else:
            flags=r.number(p,2)
            require(flags&3==3 and flags>>12==3 and not flags&8,f"{self.label}: unsupported raw-helper body header/EH")
            start,size,init=p+12,r.number(p+4,4),bool(flags&16)
            local_token=r.number(p+8,4)
            if local_token:
                require(local_token>>24==17,f"{self.label}: invalid local signature token")
                local_blob=self.tables.blob(self.tables.row(17,local_token&0xffffff)[0])
        require(0<size<=1_000_000,f"{self.label}: invalid raw-helper code length")
        self.rva(rva,start-p+size)
        code=Signature(r.block(start,size),self.label)
        vocabulary=dict(IL_OPS)
        vocabulary.update({0x0e:("ldarg.s","var1"),0x0f:("ldarga.s","var1"),0x10:("starg.s","var1"),
                           0x11:("ldloc.s","var1"),0x12:("ldloca.s","var1"),0x13:("stloc.s","var1"),
                           0xfe09:("ldarg","var2"),0xfe0a:("ldarga","var2"),0xfe0b:("starg","var2"),
                           0xfe0c:("ldloc","var2"),0xfe0d:("ldloca","var2"),0xfe0e:("stloc","var2")})
        rows,positions=[],{}
        while code.position<len(code.data):
            positions[code.position]=len(rows)
            op=code.byte()
            if op==0xfe:op=0xfe00|code.byte()
            require(op in vocabulary,f"{self.label}: unsupported raw-helper opcode 0x{op:x}")
            name,kind=vocabulary[op];value=None
            if kind=="token":value=int.from_bytes(code.take(4),"little")
            elif kind.startswith("branch"):
                width=int(kind[-1]);distance=int.from_bytes(code.take(width),"little",signed=True);value=[code.position+distance]
            elif kind=="switch":
                count=int.from_bytes(code.take(4),"little");require(count<=65536,f"{self.label}: oversized switch")
                values=[int.from_bytes(code.take(4),"little",signed=True) for _ in range(count)];value=[code.position+v for v in values]
            elif kind.startswith("int") or kind.startswith("var"):value=int.from_bytes(code.take(int(kind[-1])),"little",signed=kind.startswith("int"))
            else:require(not kind,f"{self.label}: unknown raw-helper operand")
            rows.append(dict(name=name,kind=kind,value=value))
        for row in rows:
            if row["kind"].startswith("branch") or row["kind"]=="switch":
                require(all(value in positions for value in row["value"]),f"{self.label}: branch outside instruction boundaries")
                row["value"]=[positions[value] for value in row["value"]]
        return dict(initLocals=init,localBlob=local_blob,instructions=rows)

    def hash_type_reference(self,h,table,rid,scope):
        if table==27:
            h.add("type-spec");sig=Signature(self.tables.blob(self.tables.row(27,rid)[0]),self.label)
            self.hash_type(h,sig,scope);require(sig.position==len(sig.data),f"{self.label}: trailing TypeSpec");return
        name,assembly=self.type_identity(table,rid)
        h.add("type");h.add(name);h.add(scope(name,assembly) if scope else assembly)

    def hash_type(self,h,sig,scope,depth=0):
        require(depth<128,f"{self.label}: recursive raw-helper signature")
        code=sig.byte();h.add(code)
        primitives={1:"Void",2:"Boolean",3:"Char",4:"SByte",5:"Byte",6:"Int16",7:"UInt16",8:"Int32",9:"UInt32",10:"Int64",11:"UInt64",12:"Single",13:"Double",14:"String",22:"TypedReference",24:"IntPtr",25:"UIntPtr",28:"Object"}
        if code in primitives:
            name="System."+primitives[code];assembly=self.core_identity()
            h.add("type");h.add(name);h.add(scope(name,assembly) if scope else assembly)
        elif code in (17,18):self.hash_type_reference(h,*self.tables.coded(sig.compressed(),"TypeDefOrRef"),scope)
        elif code in (15,16,29,69):self.hash_type(h,sig,scope,depth+1)
        elif code==21:
            self.hash_type(h,sig,scope,depth+1);count=sig.compressed();require(count<=256,f"{self.label}: oversized raw generic signature");h.add(count)
            for _ in range(count):self.hash_type(h,sig,scope,depth+1)
        elif code in (19,30):h.add(sig.compressed())
        else:raise VerificationError(f"{self.label}: unsupported raw-helper signature 0x{code:x}")

    def hash_signature(self,h,blob,scope):
        sig=Signature(blob,self.label);convention=sig.byte()
        require(convention&15==0 and not convention&0x50,f"{self.label}: unsupported raw method calling convention")
        count=sig.compressed();require(count<=1024,f"{self.label}: oversized raw method parameter list")
        h.add(convention);h.add(0);self.hash_type(h,sig,scope);h.add(count)
        for _ in range(count):self.hash_type(h,sig,scope)
        require(sig.position==len(sig.data),f"{self.label}: trailing raw method signature")
        h.add(-1)

    def hash_method_reference(self,h,token,scope):
        table,rid=token>>24,token&0xffffff
        if table==6:
            row=self.tables.row(6,rid);owner=(2,self.method_owners[rid]);name,blob=row[3:5]
        elif table==10:
            parent,name,blob=self.tables.row(10,rid);owner=self.tables.coded(parent,"MemberRefParent")
        else:raise VerificationError(f"{self.label}: raw-helper method token must be MethodDef/MemberRef")
        require(owner[0] in (1,2),f"{self.label}: unsupported raw method owner")
        h.add("method");self.hash_type_reference(h,*owner,scope);h.add(self.tables.string(name));self.hash_signature(h,self.tables.blob(blob),scope)

    def hash_attributes(self,h,table,rid,scope):
        rows=[]
        for index in range(1,self.tables.counts[12]+1):
            parent,constructor,blob=self.tables.row(12,index)
            if self.tables.coded(parent,"HasCustomAttribute")== (table,rid):rows.append((constructor,blob))
        h.add(len(rows))
        for constructor,blob in rows:
            # ECMA CustomAttributeType reserves tags0/1; its live tags are2/3.
            tag,target=constructor&7,constructor>>3
            require(tag in (2,3),f"{self.label}: invalid attribute constructor coded tag")
            owner=(6,10)[tag-2];self.tables.row(owner,target)
            raw=self.tables.blob(blob)
            require(raw==b"\x01\x00\x00\x00",f"{self.label}: unsupported nonempty raw-helper custom attribute")
            member=self.member(owner,target)
            require(member["name"]==".ctor" and member["parameters"]==[],f"{self.label}: attribute signature/blob mismatch")
            self.hash_method_reference(h,(owner<<24)|target,scope);h.add(0);h.add(0)

    @staticmethod
    def variable(row):
        name=row["name"]
        return int(name.rsplit(".",1)[1]) if name[-1:] in "0123" else row["value"]

    @staticmethod
    def constant(row):
        name=row["name"]
        return -1 if name=="ldc.i4.m1" else row["value"] if name in ("ldc.i4","ldc.i4.s") else int(name[-1])

    def method_hash(self,rid,scope=None):
        row=self.tables.row(6,rid);owner=self.method_owners[rid]
        require(row[0] and row[2]&0x10 and not row[2]&0x2000 and not row[1]&0x1003,f"{self.label}: unsupported native/nonstatic raw method")
        require(not any(self.tables.coded(self.tables.row(42,n)[2],"TypeOrMethodDef") in ((6,rid),(2,owner)) for n in range(1,self.tables.counts[42]+1)),
                f"{self.label}: generic raw helper is unsupported")
        require(not any(self.tables.coded(self.tables.row(14,n)[1],"HasDeclSecurity")== (6,rid) for n in range(1,self.tables.counts[14]+1)),f"{self.label}: security metadata on raw helper")
        require(not any(self.tables.coded(self.tables.row(25,n)[1],"MethodDefOrRef")== (6,rid) for n in range(1,self.tables.counts[25]+1)),f"{self.label}: override metadata on raw helper")
        h=BindingHash("assembly-shadow-reflection-method:1")
        for value in (self.type_names[owner],self.tables.string(row[3]),row[2],row[1]):h.add(value)
        self.hash_signature(h,self.tables.blob(row[4]),scope);self.hash_attributes(h,6,rid,scope);h.add(0)
        end=self.tables.row(6,rid+1)[5] if rid<self.tables.counts[6] else self.tables.counts[8]+1
        require(1<=row[5]<=end<=self.tables.counts[8]+1,f"{self.label}: invalid parameter range")
        parameters=sorted([(n,self.tables.row(8,n)) for n in range(row[5],end)],key=lambda item:item[1][1]);h.add(len(parameters))
        for index,(flags,sequence,name) in parameters:
            require(not flags&0x3000,f"{self.label}: marshal/default parameter metadata unsupported")
            for value in (sequence,flags,self.tables.string(name),False):h.add(value)
            self.hash_attributes(h,8,index,scope)
        body=self.body(rid);h.add(body["initLocals"])
        if body["localBlob"]:
            sig=Signature(body["localBlob"],self.label);require(sig.byte()==7,f"{self.label}: invalid local signature")
            count=sig.compressed();require(count<=1024,f"{self.label}: oversized local inventory");h.add(count)
            for _ in range(count):self.hash_type(h,sig,scope)
            require(sig.position==len(sig.data),f"{self.label}: trailing local signature")
        else:h.add(0)
        h.add(len(body["instructions"]))
        for instruction in body["instructions"]:
            name,kind,value=instruction["name"],instruction["kind"],instruction["value"]
            if name.startswith("ldc.i4"):
                h.add("Ldc_I4");h.add(self.constant(instruction));continue
            if name.startswith(("ldarg","starg","ldloc","stloc")):
                stem=name.split(".")[0];h.add(stem[0].upper()+stem[1:]);h.add(self.variable(instruction));continue
            enum="_".join(part[0].upper()+part[1:] for part in name.split("."))
            if kind=="branch1":enum=enum[:-2]
            h.add(enum)
            if value is None:h.add("none")
            elif name=="ldstr":h.add("string");h.add(self.user_string(value))
            elif kind.startswith("branch"):h.add("branch");h.add(value[0])
            elif kind=="switch":
                h.add("switch");h.add(len(value))
                for target in value:h.add(target)
            elif name in ("call","callvirt","newobj"):
                h.add("method");self.hash_method_reference(h,value,scope)
            else:raise VerificationError(f"{self.label}: unsupported raw-helper fingerprint operand: {name}")
        h.add(0) # No exception handlers: enforced by body header.
        return h.finish()


CORE_IDENTITIES={"mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089",
                 "netstandard, Version=2.1.0.0, Culture=neutral, PublicKeyToken=cc7b13ffcd2ddd51"}
LOAD_SIGNATURE="System.Reflection.Assembly System.Reflection.Assembly::Load(System.String)"
MODULE_SIGNATURE="System.Reflection.Module System.Reflection.Assembly::get_ManifestModule()"


def find_method(proof,declaring_type,signature):
    matches=[]
    for rid,owner in proof.method_owners.items():
        if proof.type_names[owner]==declaring_type and proof.member(6,rid)["fullName"]==signature:matches.append(rid)
    require(len(matches)==1,f"{proof.label}: missing/ambiguous exact raw helper method: {signature}")
    return matches[0]


def trusted_method(proof,token,load):
    table,rid=token>>24,token&0xffffff
    require(table in (6,10),f"{proof.label}: unsupported raw method reference")
    member=proof.member(table,rid);core_identity=proof.core_identity()
    require(member["kind"]=="method",f"{proof.label}: raw API operand is not a method")
    require(core_identity in CORE_IDENTITIES and member["assembly"]==core_identity,f"{proof.label}: raw API is not the captured corlib method")
    core=load(core_identity.split(", ")[0])
    require(core.identity["fullName"]==core_identity,f"{proof.label}: corlib actual identity differs")
    matches=[]
    for candidate,owner in core.method_owners.items():
        # Only decode the requested overload family. Unrelated core methods
        # can legitimately be generic, outside this bounded helper grammar.
        if (core.type_names[owner]==member["owner"] and
                core.tables.string(core.tables.row(6,candidate)[3])==member["name"] and
                core.member(6,candidate)["fullName"]==member["fullName"]):matches.append(candidate)
    require(len(matches)==1,f"{proof.label}: raw API missing/ambiguous in actual captured corlib")
    def actual_core_type(name,assembly):
        require(assembly==core_identity and list(core.type_names.values()).count(name)==1,
                f"{proof.label}: raw signature type has no unique actual captured corlib definition: {name}")
        return assembly
    expected,actual=BindingHash("raw-signature:1"),BindingHash("raw-signature:1")
    core.hash_method_reference(expected,(6<<24)|matches[0],actual_core_type)
    proof.hash_method_reference(actual,token,actual_core_type)
    require(expected.finish()==actual.finish(),f"{proof.label}: raw method signature/scope differs from actual corlib")
    return member


def verify_chains(proof,rid,sites,load):
    body=proof.body(rid);il=body["instructions"];covered=set();receivers={}
    method=proof.member(6,rid)
    require(not method["instance"] and len(method["parameters"])<=1 and (not method["parameters"] or method["parameters"]==["System.String"]),
            f"{proof.label}: raw helper requires static finite literal selector")
    signature=Signature(proof.tables.blob(proof.tables.row(6,rid)[4]),proof.label)
    require(signature.byte()==0,f"{proof.label}: unsupported raw helper calling convention")
    count=signature.compressed();return_hash=BindingHash("raw-local:1");proof.hash_type(return_hash,signature,None)
    require(count in (0,1) and (not count or signature.byte()==14) and signature.position==len(signature.data),
            f"{proof.label}: raw selector argument must be a primitive string")
    def previous(index):
        index-=1
        while index>=0 and il[index]["name"]=="nop":index-=1
        require(index>=0,f"{proof.label}: incomplete literal receiver chain")
        return index
    def call(index,opcode,signature):
        require(il[index]["name"]==opcode,f"{proof.label}: raw receiver opcode differs")
        member=trusted_method(proof,il[index]["value"],load)
        require(member["fullName"]==signature,f"{proof.label}: raw receiver method differs")
        return member
    for site in sites:
        end=site["operationIndex"]
        require(end<len(il),f"{proof.label}: raw operation index outside method")
        operation=call(end,"callvirt",site["operationSignature"])
        require(operation["instance"] and method["returnType"]==operation["returnType"],f"{proof.label}: raw result type changed")
        def result_hash(table,index):
            entry=proof.tables.row(table,index)
            blob=entry[4] if table==6 else entry[2]
            sig=Signature(proof.tables.blob(blob),proof.label);convention=sig.byte()
            require(not convention&16,f"{proof.label}: generic helper method unsupported")
            sig.compressed();h=BindingHash("raw-result:1");proof.hash_type(h,sig,None);return h.finish()
        token=il[end]["value"]
        require(result_hash(6,rid)==result_hash(token>>24,token&0xffffff),f"{proof.label}: raw result scope/shape changed")
        provider=load(site["providerAssemblyIdentity"].split(", ")[0])
        require(provider.identity["fullName"]==site["providerAssemblyIdentity"],f"{proof.label}: raw provider identity differs")
        require(not provider.tables.counts[38] and not provider.tables.counts[39] and not proof.tables.counts[38] and not proof.tables.counts[39],
                f"{proof.label}: multimodule/exported provider or consumer unsupported")
        kind=OPERATIONS[site["operationSignature"]];cursor=end
        if kind=="Module.GetType":
            ignore=previous(cursor);throws=previous(ignore);literal=previous(throws)
            require(il[ignore]["name"].startswith("ldc.i4") and proof.constant(il[ignore])==0 and
                    il[throws]["name"].startswith("ldc.i4") and proof.constant(il[throws])==1 and il[literal]["name"]=="ldstr" and
                    proof.user_string(il[literal]["value"])==site["typeName"],f"{proof.label}: Module.GetType is not exact literal/flags")
            require(list(provider.type_names.values()).count(site["typeName"].replace("+","/"))==1,f"{proof.label}: literal type absent/ambiguous in actual provider")
            cursor=literal
        if kind.startswith("Module."):
            cursor=previous(cursor);call(cursor,"callvirt",MODULE_SIGNATURE)
        receiver=previous(cursor);call(receiver,"call",LOAD_SIGNATURE)
        start=previous(receiver)
        require(il[start]["name"]=="ldstr" and proof.user_string(il[start]["value"])==provider.identity["name"],
                f"{proof.label}: receiver must be exact provider simple-name literal; no aliases")
        for instruction in il:
            if instruction["kind"].startswith("branch") or instruction["kind"]=="switch":
                require(all(target<=start or target>end for target in instruction["value"]),f"{proof.label}: branch bypasses literal receiver")
        chain=set(range(start,end+1));require(not covered&chain,f"{proof.label}: overlapping raw chains")
        covered|=chain;receivers[site["id"]]=receiver
    locals=[]
    if body["localBlob"]:
        sig=Signature(body["localBlob"],proof.label);require(sig.byte()==7,f"{proof.label}: local signature kind differs")
        count=sig.compressed()
        for _ in range(count):
            start=sig.position;h=BindingHash("raw-local:1");proof.hash_type(h,sig,None)
            require(sig.data[start] in (14,8,2) or h.finish()==return_hash.finish(),f"{proof.label}: raw helper has receiver alias/arbitrary scoped local")
            locals.append(True)
        require(sig.position==len(sig.data),f"{proof.label}: trailing local signature")
    allowed={"nop","ret","throw","ldstr","ldnull","br","br.s","brtrue","brtrue.s","brfalse","brfalse.s","beq","beq.s","bne.un","bne.un.s","ceq","switch"}
    exceptions={"System.Void System.ArgumentException::.ctor(System.String)","System.Void System.ArgumentException::.ctor(System.String,System.String)",
                "System.Void System.ArgumentOutOfRangeException::.ctor(System.String)"}
    comparisons={"System.Boolean System.String::op_Equality(System.String,System.String)","System.Boolean System.String::op_Inequality(System.String,System.String)"}
    for index,instruction in enumerate(il):
        if index in covered:continue
        name=instruction["name"];ok=name in allowed or name.startswith("ldc.i4")
        if name in ("ldarg","ldarg.s","ldarg.0"):ok=method["parameters"]==["System.String"] and proof.variable(instruction)==0
        if name.startswith(("ldloc","stloc")) and not name.startswith(("ldloca","stloca")):
            variable=proof.variable(instruction);ok=type(variable) is int and 0<=variable<len(locals)
        if name in ("call","newobj"):
            called=trusted_method(proof,instruction["value"],load)
            ok=called["fullName"] in (comparisons if name=="call" else exceptions)
        require(ok,f"{proof.label}: operation{index} outside finite raw-helper grammar: {name}")
    return receivers


PROOF_FIELDS="schemaVersion policy phase configurationSha256 configurationHash unityVersion target architecture buildGuid linkedPlayerReceiptHash profileHash sites"
PROOF_SITE_FIELDS="id consumerAssemblyIdentity consumerPath consumerSha256 providerAssemblyIdentity providerPath providerSha256 providerInventoryHash declaringType methodSignature operationIndex operationSignature kind typeName throwOnError ignoreCase compiledMethodHash linkedMethodHash compiledConsumerSha256"


class Catalog:
    def __init__(self,root,files):
        self.root,self.files,self.loaded=Path(root),{},{}
        for row in files:
            name=row["name"].casefold()
            require(name not in self.files,f"{root}: duplicate raw admission module")
            self.files[name]=row
    def __call__(self,name):
        key=name.casefold();require(key in self.files,f"{self.root}: raw admission module absent: {name}")
        if key not in self.loaded:
            row=self.files[key];path=_rel(self.root,row["path"],self.root,"raw module")
            raw=path.read_bytes();require(hashlib.sha256(raw).hexdigest()==row["sha256"],f"{path}: raw module bytes changed")
            proof=RawMethodProof(raw,path)
            require(proof.identity["name"].casefold()==key,f"{path}: raw module actual identity differs")
            self.loaded[key]=proof
        return self.loaded[key]


# This scanner only locates actual operands and branches. It does not enlarge
# the raw helper grammar above and does not claim whole-program IL validity.
# Widths are ECMA-335 III (also the pinned runtime metadata/Opcodes table).
def boundary_instructions(proof,rid):
    row=proof.tables.row(6,rid)
    if not row[0]:return []
    require(row[1]&3==0,f"{proof.label}: non-IL consumer body in provider boundary")
    offset=proof.rva(row[0],1);reader=Reader(proof.data,proof.label);first=reader.number(offset,1)
    if first&3==2:start,size=offset+1,first>>2
    else:
        flags=reader.number(offset,2)
        require(flags&3==3 and flags>>12==3,f"{proof.label}: unsupported provider-boundary method header")
        start,size=offset+12,reader.number(offset+4,4)
    require(0<size<=1_000_000,f"{proof.label}: invalid provider-boundary code size")
    proof.rva(row[0],start-offset+size);code=Signature(reader.block(start,size),proof.label)
    widths={n:0 for a,b in ((0,13),(20,30),(37,38),(70,110),(130,139),(144,162),(179,186),(209,220),(223,224)) for n in range(a,b+1)}
    widths.update({n:0 for n in (0x2a,0x76,0x7a,0x8e,0xc3)})
    widths.update({n:1 for n in [*range(0x0e,0x14),0x1f,*range(0x2b,0x38),0xde]})
    widths.update({n:4 for n in [0x20,0x22,*range(0x27,0x2a),*range(0x38,0x45),*range(0x6f,0x76),0x79,*range(0x7b,0x82),0x8c,0x8d,0x8f,0xa3,0xa4,0xa5,0xc2,0xc6,0xd0,0xdd]})
    widths.update({0x21:8,0x23:8})
    widths.update({0xfe00|n:0 for n in [*range(6),0x0f,0x11,0x13,0x14,0x17,0x18,0x1a,0x1d,0x1e]})
    widths.update({0xfe00|n:4 for n in (6,7,0x15,0x16,0x1c)})
    widths.update({0xfe00|n:2 for n in range(9,15)});widths.update({0xfe12:1,0xfe19:1})
    branches=set(range(0x2b,0x45))|{0xdd,0xde};rows=[];positions={}
    while code.position<len(code.data):
        positions[code.position]=len(rows);op=code.byte()
        if op==0xfe:op=0xfe00|code.byte()
        if op==0x45:
            count=int.from_bytes(code.take(4),"little");require(count<=65536,f"{proof.label}: oversized provider switch")
            distances=[int.from_bytes(code.take(4),"little",signed=True) for _ in range(count)];value=[code.position+d for d in distances]
        else:
            require(op in widths,f"{proof.label}: unsupported/reserved consumer opcode {op:#x}")
            width=widths[op];value=int.from_bytes(code.take(width),"little",signed=op in branches) if width else None
            if op in branches:value=[code.position+value]
        rows.append((op,value))
    for index,(op,value) in enumerate(rows):
        if op in branches or op==0x45:
            require(all(target in positions for target in value),f"{proof.label}: provider branch is not an actual instruction boundary")
            rows[index]=(op,[positions[target] for target in value])
    return rows


class ImportTables(CliTables):
    """External import inspection only; pointer tables are not TypeDef proof.

    Some actual unlinked runtime DLLs contain #- pointer tables. Their TypeRef,
    MemberRef and #US imports have ordinary bounded ECMA layouts. No field or
    method-owner inventory is inferred through those indirections here.
    """
    def __init__(self,data,label):
        self.data,self.label=bytes(data),str(label);self.streams=_metadata(self.data,label)
        self.reader=Reader(self.streams.get("#~",self.streams.get("#-")),label)
        heaps,valid=self.reader.number(6,1),self.reader.number(8,8)
        require(not valid>>len(TABLES),f"{label}: unsupported import tables")
        self.counts=[0]*len(TABLES);cursor=24
        for index in range(len(TABLES)):
            if valid&(1<<index):
                self.counts[index]=self.reader.number(cursor,4);cursor+=4
                require(self.counts[index]<=10_000_000,f"{label}: oversized import table")
        require(self.counts[0]==self.counts[32]==1,f"{label}: import module requires one assembly")
        def width(column):
            if isinstance(column,int):return 4 if self.counts[column]>=65536 else 2
            if column in ("u2","u4"):return int(column[1:])
            if column in ("s","b","g"):return 4 if heaps&{"s":1,"g":2,"b":4}[column] else 2
            bits,targets=CODED[column];return 4 if max(self.counts[t] for t in targets)>=1<<(16-bits) else 2
        self.offsets,self.widths=[],[]
        for table,schema in enumerate(TABLES):
            sizes=[width(column) for column in schema];self.offsets.append(cursor);self.widths.append(sizes)
            size=self.counts[table]*sum(sizes);self.reader.block(cursor,size);cursor+=size


class ImportModule(RawMethodProof):
    def __init__(self,data,label):
        self.data,self.label=bytes(data),label;self.tables=ImportTables(data,label)
        self.identity=read_identity_bytes(self.data,label);self.type_names={};parents={}
        for rid in range(1,self.tables.counts[41]+1):
            child,parent=self.tables.row(41,rid)
            require(child not in parents,f"{label}: duplicate import nested type");parents[child]=parent
        def name(rid,seen=()):
            require(rid not in seen and len(seen)<128,f"{label}: cyclic import type")
            row=self.tables.row(2,rid);leaf,ns=self.tables.string(row[1]),self.tables.string(row[2])
            return name(parents[rid],(*seen,rid))+"/"+leaf if rid in parents else (ns+"." if ns else "")+leaf
        for rid in range(1,self.tables.counts[2]+1):self.type_names[rid]=name(rid)


class ProviderBoundary:
    """M05 specialization: no recorded explanation admits external brokers.

    Proves direct metadata imports, exact reflection literals, selector-shaped
    same-consumer forwarding and explicit token/delegate/field escapes. It is
    intentionally not general package-policy parity, dynamic string analysis,
    arbitrary native analysis, or a whole-program dependency proof.
    """
    HANDLES=set("System.Type System.Reflection.TypeInfo System.Reflection.MemberInfo System.Reflection.MethodBase System.Reflection.MethodInfo System.Reflection.ConstructorInfo System.Reflection.FieldInfo System.Reflection.PropertyInfo System.Reflection.EventInfo System.Reflection.ParameterInfo System.Reflection.Assembly System.Reflection.Module System.RuntimeTypeHandle System.RuntimeMethodHandle System.RuntimeFieldHandle System.ModuleHandle System.Object System.Delegate System.MulticastDelegate System.Collections.IEnumerable System.Collections.IEnumerator".split())
    SCALARS=set("System.Void System.Boolean System.Char System.SByte System.Byte System.Int16 System.UInt16 System.Int32 System.UInt32 System.Int64 System.UInt64 System.Single System.Double System.Decimal System.String System.IntPtr System.UIntPtr".split())

    def __init__(self,catalog,sites,runtime_names):
        self.catalog,self.sites,self.runtime_names=catalog,sites,set(runtime_names)
        self.consumers={site["consumerAssembly"] for site in sites}
        self.shape_cache={};self.definitions={};self.method_cache={}

    def shape(self,proof,sig,depth=0):
        require(depth<128,f"{proof.label}: recursive selector signature")
        code=sig.byte()
        if code in (31,32):proof.tables.coded(sig.compressed(),"TypeDefOrRef");return self.shape(proof,sig,depth+1)
        if code in (15,16,29,69):return (code,self.shape(proof,sig,depth+1))
        if code in (17,18):return (code,self.type_ref(proof,*proof.tables.coded(sig.compressed(),"TypeDefOrRef"),depth+1))
        if code in (19,30):return (code,sig.compressed())
        if code==21:
            definition=self.shape(proof,sig,depth+1);count=sig.compressed();require(count<=1024,f"{proof.label}: oversized selector generic")
            return (code,definition,tuple(self.shape(proof,sig,depth+1) for _ in range(count)))
        if code==20:
            element=self.shape(proof,sig,depth+1);rank=sig.compressed();require(0<rank<=64,f"{proof.label}: invalid selector array rank")
            for _ in range(2):
                count=sig.compressed();require(count<=rank,f"{proof.label}: invalid selector array bounds")
                for _ in range(count):sig.compressed()
            return (code,element)
        if code==27:return (code,self.signature(proof,sig,depth+1))
        require(code in (*range(1,15),22,24,25,28),f"{proof.label}: unsupported selector signature element {code:#x}")
        return (code,)

    def type_ref(self,proof,table,rid,depth=0):
        require(depth<128,f"{proof.label}: recursive selector type reference")
        if table==27:
            sig=Signature(proof.tables.blob(proof.tables.row(27,rid)[0]),proof.label);shape=self.shape(proof,sig,depth+1)
            require(sig.position==len(sig.data),f"{proof.label}: trailing selector TypeSpec")
            if shape[0]==21:shape=shape[1]
            return shape[1] if shape[0] in (17,18) else ("","")
        name,assembly=proof.type_identity(table,rid)
        return assembly,name

    def type_components(self,proof,table,rid):
        """Exact token components, not only a generic container's definition."""
        if table!=27:return {self.type_ref(proof,table,rid)}
        sig=Signature(proof.tables.blob(proof.tables.row(27,rid)[0]),proof.label)
        shape=self.shape(proof,sig)
        require(sig.position==len(sig.data),f"{proof.label}: trailing selector type-token signature")
        def walk(item):
            if item[0] in (17,18):return {item[1]}
            if item[0] in (15,16,20,29,69):return walk(item[1])
            if item[0]==21:return walk(item[1]).union(*(walk(arg) for arg in item[2]))
            if item[0]==27:return walk(item[1][2]).union(*(walk(arg) for arg in item[1][3]))
            return set()
        return walk(shape)

    def signature(self,proof,sig,depth=0):
        convention=sig.byte();require(convention&15 in (0,5),f"{proof.label}: unsupported selector method signature")
        arity=sig.compressed() if convention&16 else 0;count=sig.compressed()
        require(count<=4096,f"{proof.label}: oversized selector parameter inventory")
        result=self.shape(proof,sig,depth+1);parameters=[]
        for _ in range(count):
            if sig.data[sig.position]==65:sig.byte()
            parameters.append(self.shape(proof,sig,depth+1))
        return convention,arity,result,tuple(parameters)

    def method(self,proof,token):
        key=(proof.identity["fullName"],token)
        if key in self.method_cache:return self.method_cache[key]
        table,rid=token>>24,token&0xffffff
        if table==43:
            target,blob=proof.tables.row(43,rid);kind,target=proof.tables.coded(target,"MethodDefOrRef")
            member=self.method(proof,(kind<<24)|target);sig=Signature(proof.tables.blob(blob),proof.label)
            require(sig.byte()==10,f"{proof.label}: invalid selector MethodSpec signature")
            count=sig.compressed();require(count==member[3][1],f"{proof.label}: selector MethodSpec arity differs")
            arguments=tuple(self.shape(proof,sig) for _ in range(count))
            require(sig.position==len(sig.data),f"{proof.label}: trailing selector MethodSpec signature")
            def substitute(shape):
                if shape[0]==30:
                    require(shape[1]<len(arguments),f"{proof.label}: MethodSpec variable outside arguments")
                    return arguments[shape[1]]
                if shape[0] in (15,16,20,29,69):return (shape[0],substitute(shape[1]))
                if shape[0]==21:return (21,substitute(shape[1]),tuple(substitute(item) for item in shape[2]))
                return shape
            convention,arity,returned,parameters=member[3]
            return (*member[:3],(convention,arity,substitute(returned),tuple(substitute(item) for item in parameters)))
        require(table in (6,10),f"{proof.label}: invalid provider method operand")
        if table==6:
            row=proof.tables.row(6,rid);owner=(2,proof.method_owners[rid]);name,blob=row[3:5]
        else:
            parent,name,blob=proof.tables.row(10,rid);owner=proof.tables.coded(parent,"MemberRefParent")
            if owner[0]==6:return self.method(proof,(6<<24)|owner[1])
        require(owner[0] in (1,2,27),f"{proof.label}: unresolved global provider method")
        assembly,declaring=self.type_ref(proof,*owner);sig=Signature(proof.tables.blob(blob),proof.label)
        parsed=self.signature(proof,sig);require(sig.position==len(sig.data),f"{proof.label}: trailing provider method signature")
        value=(assembly,declaring,proof.tables.string(name),parsed)
        self.method_cache[key]=value;return value

    def capable(self,shape,seen=frozenset()):
        code=shape[0]
        if code==28:return True
        # A closed MethodSpec can instantiate an unconstrained return/out
        # parameter with a handle. Do not silently treat that uncertainty as
        # an opaque primitive in a method already reached from an admission.
        if code in (19,30):return True
        if code in (15,16,20,29,69):return self.capable(shape[1],seen)
        if code==27:return True
        if code==21:return any(self.capable(item,seen) for item in shape[2]) or self.capable(shape[1],seen)
        if code not in (17,18):return False
        identity,name=shape[1]
        if identity in CORE_IDENTITIES and name in self.SCALARS:return False
        if identity in CORE_IDENTITIES and name in self.HANDLES:return True
        key=(identity,name)
        if key in seen:return False
        if key in self.shape_cache:return self.shape_cache[key]
        # Framework container internals (e.g. synchronization Object fields) do
        # not turn Action<int>/List<string> into provider selectors. Generic
        # arguments above are still traversed; custom captured fields follow.
        if identity in CORE_IDENTITIES or identity.split(", ")[0] in ("System","System.Core") or identity.split(", ")[0].startswith("UnityEngine."):return False
        simple=identity.split(", ")[0]
        if simple.casefold() not in self.catalog.files:return False
        proof=self.catalog(simple)
        require(proof.identity["fullName"]==identity,f"{proof.label}: selector field owner identity differs")
        rids=[rid for rid,value in proof.type_names.items() if value==name]
        require(len(rids)==1,f"{proof.label}: selector custom type is missing/ambiguous: {name}")
        extends=proof.tables.row(2,rids[0])[3]
        if extends and self.type_ref(proof,*proof.tables.coded(extends,"TypeDefOrRef"))[1] in ("System.Delegate","System.MulticastDelegate"):
            invokes=[rid for rid,owner in proof.method_owners.items() if owner==rids[0] and proof.tables.string(proof.tables.row(6,rid)[3])=="Invoke"]
            require(len(invokes)==1,f"{proof.label}: selector delegate lacks exact Invoke signature")
            signature=self.method(proof,(6<<24)|invokes[0])[3]
            return any(self.capable(item,seen|{key}) for item in (signature[2],*signature[3]))
        result=False
        for field,owner in proof.field_owners.items():
            if owner!=rids[0] or proof.tables.row(4,field)[0]&0x10:continue
            sig=Signature(proof.tables.blob(proof.tables.row(4,field)[2]),proof.label)
            require(sig.byte()==6,f"{proof.label}: invalid selector field signature")
            child=self.shape(proof,sig);require(sig.position==len(sig.data),f"{proof.label}: trailing selector field signature")
            result=result or self.capable(child,seen|{key})
        if not seen:self.shape_cache[key]=result
        return result

    def selector(self,signature):
        _,_,returned,parameters=signature
        if self.capable(returned):return True
        for shape in parameters:
            if shape[0]==16 and self.capable(shape[1]):return True
            if shape[0]==21 and shape[1][0] in (17,18):
                _,name=shape[1][1]
                if name.startswith(("System.Func`","System.Action`")) and self.capable(shape):return True
            if shape[0] in (17,18) and shape[1][1] in ("System.Delegate","System.MulticastDelegate"):return True
            if shape[0] in (17,18):
                identity,name=shape[1];simple=identity.split(", ")[0]
                if simple.casefold() in self.catalog.files and simple not in ("mscorlib","netstandard"):
                    proof=self.catalog(simple);rids=[rid for rid,value in proof.type_names.items() if value==name]
                    require(len(rids)==1,f"{proof.label}: callback type is missing/ambiguous")
                    extends=proof.tables.row(2,rids[0])[3]
                    if extends and self.type_ref(proof,*proof.tables.coded(extends,"TypeDefOrRef"))[1] in ("System.Delegate","System.MulticastDelegate") and self.capable(shape):return True
        return False

    def resolve_self(self,proof,token):
        if token>>24==43:
            # Validate the actual closed signature, but bind its definition
            # by the MethodDefOrRef operand rather than comparing it to an
            # unsubstituted generic definition signature.
            self.method(proof,token)
            target,_=proof.tables.row(43,token&0xffffff);kind,target=proof.tables.coded(target,"MethodDefOrRef")
            return self.resolve_self(proof,(kind<<24)|target)
        if token>>24==6:return token&0xffffff
        member=self.method(proof,token)
        if member[0]!=proof.identity["fullName"]:return None
        matches=[rid for rid,owner in proof.method_owners.items() if proof.type_names[owner]==member[1] and
                 proof.tables.string(proof.tables.row(6,rid)[3])==member[2] and self.method(proof,(6<<24)|rid)[3]==member[3]]
        require(len(matches)==1,f"{proof.label}: ambiguous/missing same-consumer selector target")
        return matches[0]

    @staticmethod
    def exact_type_literal(text,identity,names):
        for name in names:
            for spelling in (name,name.replace("/","+")):
                if text==spelling:return True
                if text.startswith(spelling+",") and text[len(spelling)+1:].strip() in (identity,identity.split(", ")[0]):return True
        return False

    def local_field(self,proof,token):
        table,rid=token>>24,token&0xffffff
        if table==4:proof.tables.row(4,rid);return rid
        require(table==10,f"{proof.label}: invalid selector field token")
        parent,name,_=proof.tables.row(10,rid);kind,target=proof.tables.coded(parent,"MemberRefParent")
        if kind not in (1,2,27):return None
        identity,owner=self.type_ref(proof,kind,target)
        if identity!=proof.identity["fullName"]:return None
        matches=[field for field,type_rid in proof.field_owners.items() if proof.type_names[type_rid]==owner and proof.tables.string(proof.tables.row(4,field)[1])==proof.tables.string(name)]
        require(len(matches)==1,f"{proof.label}: ambiguous selector field target")
        return matches[0]

    def verify_field_values(self,proof,bodies,selected):
        """Finite may-carry flow, seeded only by admitted/forwarded selectors.

        Ordinary Type inputs and unrelated method pointers begin opaque. This
        prevents a LINQ Func<TypeInfo,Type> cache in a method which also calls
        GetTypes from becoming a fabricated provider-selection field escape.
        Direct consumer calls pass the bit through arguments/locals. A newarr
        site also carries a finite allocation identity: local aliases and
        nested containers retain it, and selected contents propagate on reads.
        Only arrays which stay local may receive selected handles. Calls,
        returns, fields and indirect stores escape their allocation identities,
        including escapes preceding a later write. Unknown/caller-owned stores
        fail closed; this is not an interprocedural heap/alias proof.
        """
        # (selected value, local allocation sites, may be nonlocal/unknown).
        opaque=(False,frozenset(),True)
        def merge(left,right):return (left[0] or right[0],left[1]|right[1],left[2] or right[2])
        fields=set();arguments={rid:set() for rid in bodies};changed=True
        arrays={rid:(set(),set(),{}) for rid in bodies}
        while changed:
            changed=False
            for rid,il in bodies.items():
                if not il:continue
                contents,escaped,children=arrays[rid]
                def carry(item):return item[0] or bool(item[1]&contents)
                def close_arrays():
                    nonlocal changed
                    again=True
                    while again:
                        again=False
                        for owner,nested in children.items():
                            if nested&contents and owner not in contents:contents.add(owner);again=changed=True
                            if owner in escaped and nested-escaped:escaped.update(nested);again=changed=True
                    require(not contents&escaped,f"{proof.label}: selected handle container escapes local ownership (method {rid})")
                def escape(item):
                    nonlocal changed
                    if item[1]-escaped:escaped.update(item[1]);changed=True
                    close_arrays()
                close_arrays()
                states={0:((),{})};pending=[0]
                # Include unreachable/EH continuation blocks conservatively;
                # a discarded branch must not hide an explicit selector store.
                for index,(op,_) in enumerate(il[:-1]):
                    if op in (0x2a,0x7a,0xdc,0xdd,0xde,0x2b,0x38,0xfe1a):states[index+1]=((),{});pending.append(index+1)
                def join(target,stack,locals_):
                    if target>=len(il):return
                    old=states.get(target)
                    if old is None:new=(tuple(stack),dict(locals_))
                    else:
                        width=max(len(old[0]),len(stack));left=(opaque,)*(width-len(old[0]))+old[0];right=(opaque,)*(width-len(stack))+tuple(stack)
                        new=(tuple(merge(a,b) for a,b in zip(left,right)),{key:merge(old[1].get(key,opaque),locals_.get(key,opaque)) for key in old[1].keys()|locals_.keys()})
                    require(len(new[0])<=4096,f"{proof.label}: oversized selector-flow stack")
                    if old!=new:states[target]=new;pending.append(target)
                while pending:
                    index=pending.pop();stack=list(states[index][0]);locals_=dict(states[index][1]);op,value=il[index]
                    def pop(count=1):
                        taken=[stack.pop() if stack else opaque for _ in range(count)];return taken
                    def push(value_=opaque):stack.append(value_)
                    if 2<=op<=5:push((op-2 in arguments[rid],frozenset(),True))
                    elif 6<=op<=9:push(locals_.get(op-6,opaque))
                    elif 10<=op<=13:locals_[op-10]=pop()[0]
                    elif op in (0x0e,0x0f,0xfe09,0xfe0a):push((value in arguments[rid],frozenset(),True))
                    elif op in (0x10,0xfe0b):
                        item=pop()[0];escape(item)
                        if carry(item) and value not in arguments[rid]:arguments[rid].add(value);changed=True
                    elif op in (0x11,0xfe0c):push(locals_.get(value,opaque))
                    elif op in (0x12,0xfe0d):
                        # Taking an address is not proof that later indirect
                        # writes stay local; do not turn it into array ownership.
                        item=locals_.get(value,opaque);escape(item);push((carry(item),frozenset(),True))
                    elif op in (0x13,0xfe0e):locals_[value]=pop()[0]
                    elif op in (0x25,):push(stack[-1] if stack else opaque)
                    elif op==0x26:pop()
                    elif op in (0x28,0x6f,0x73):
                        member=self.method(proof,value);convention,_,returned,parameters=member[3]
                        count=len(parameters)+(1 if convention&32 and op!=0x73 else 0);taken=pop(count);args=list(reversed(taken))
                        for item in args:escape(item)
                        target=self.resolve_self(proof,value)
                        if target is not None:
                            values=([opaque]+args) if op==0x73 else args
                            new={i for i,item in enumerate(values) if carry(item)}-arguments[target]
                            if new:arguments[target]|=new;changed=True
                        selected_call=target in selected
                        if selected_call and any(shape[0]==16 and self.capable(shape[1]) for shape in parameters):
                            # An out/ref pointer can alias a local; no unproved
                            # selective alias claim is made by this M05 gate.
                            for key in locals_:locals_[key]=(True,locals_[key][1],locals_[key][2])
                        if op==0x73:push((any(map(carry,args)),frozenset(),True))
                        elif returned[0]!=1:push(((selected_call or any(map(carry,args))) and self.capable(returned),frozenset(),True))
                    elif op in (0x7b,0x7c,0x7e,0x7f):
                        field=self.local_field(proof,value);item=pop()[0] if op in (0x7b,0x7c) else opaque
                        if op in (0x7c,0x7f):escape(item)
                        push((field in fields or carry(item),frozenset(),True))
                    elif op in (0x7d,0x80):
                        item=pop()[0];escape(item);taint=carry(item)
                        if op==0x7d:pop()
                        field=self.local_field(proof,value)
                        if taint:
                            require(field is not None and proof.tables.row(4,field)[0]&7 in (0,1),f"{proof.label}: selected provider handle escapes through an external field (method {rid}, instruction {index}, field {field})")
                            if field not in fields:fields.add(field);changed=True
                    elif op in (*range(0x51,0x58),0x81,0xdf):
                        item=pop()[0];pop();escape(item)
                        require(not carry(item),f"{proof.label}: unproved selected handle indirect store")
                    elif op in (*range(0x9b,0xa3),0xa4):
                        item=pop()[0];pop();array=pop()[0]
                        owned=bool(array[1]) and not array[2]
                        if owned:
                            for owner in array[1]:
                                nested=children.setdefault(owner,set())
                                if item[1]-nested:nested.update(item[1]);changed=True
                            if carry(item) and array[1]-contents:contents.update(array[1]);changed=True
                            close_arrays()
                        else:
                            escape(item)
                            require(not carry(item),f"{proof.label}: unproved selected handle array store")
                    elif op in (0x2c,0x2d,0x39,0x3a,0x45):pop()
                    elif op in (*range(0x2e,0x38),*range(0x3b,0x45)):pop(2)
                    elif op in (*range(0x58,0x65),):
                        taken=pop(2)
                        for item in taken:escape(item)
                        push((any(map(carry,taken)),frozenset(),True))
                    elif op in (0xfe01,0xfe02,0xfe03,0xfe04,0xfe05):pop(2);push()
                    elif op in (*range(0x46,0x51),*range(0x65,0x6f),0x71,0x74,0x75,0x76,0x79,*range(0x82,0x8c),0x8c,0xa5,*range(0xb3,0xbb),0xc2,0xc3,0xc6,*range(0xd1,0xd6),0xe0):push(pop()[0])
                    elif op in (*range(0x90,0x9b),0xa3,0x8f):
                        pop();array=pop()[0]
                        if op==0x8f:escape(array)
                        # An element may itself alias a locally allocated
                        # nested array. Retain every possible child for escape
                        # checks, but no index-sensitive ownership is claimed.
                        nested=frozenset().union(*(children.get(owner,set()) for owner in array[1]))
                        push((carry(array),nested,True))
                    elif op==0x8d:pop();push((False,frozenset({index}),False))
                    elif op in (0x8e,0xfe0f):pop();push()
                    elif op in (0x70,0xfe17,0xfe18):
                        taken=pop(2 if op==0x70 else 3)
                        for item in taken:escape(item)
                        require(not any(map(carry,taken)),f"{proof.label}: unproved selected handle block copy")
                    elif op==0x2a:
                        for item in stack:escape(item)
                    elif op in (0x7a,0xfe11,0xfe15):pop()
                    elif op==0xfe07:pop();push()
                    elif op in (0x72,0xd0,0xfe06,0xfe00,0xfe1c) or 0x14<=op<=0x23:push()
                    elif op==0xfe1d:pop();push()
                    elif op==0x29:
                        for item in (*stack,*locals_.values()):escape(item)
                        require(not any(map(carry,stack)) and not any(map(carry,locals_.values())),f"{proof.label}: selected handle reaches an indirect call")
                        stack=[]
                    elif op in range(0xd6,0xdc):
                        taken=pop(2)
                        for item in taken:escape(item)
                        push((any(map(carry,taken)),frozenset(),True))
                    if op in (0xdd,0xde):stack=[]
                    if isinstance(value,list):
                        for target in value:join(target,stack,locals_)
                    if op not in (0x2a,0x27,0x7a,0xdc,0xdd,0xde,0x2b,0x38,0xfe11,0xfe1a):join(index+1,stack,locals_)
        return fields

    def verify(self):
        brokers={}
        for consumer in self.consumers:
            proof=self.catalog(consumer);sites=[site for site in self.sites if site["consumerAssembly"]==consumer]
            seeds={find_method(proof,site["declaringType"],site["methodSignature"]) for site in sites}
            owners={proof.method_owners[rid] for rid in seeds}
            for owner in owners:
                definition=proof.tables.row(2,owner);flags=definition[0]
                require(flags&0x180==0x180 and not flags&0x20,f"{proof.label}: admitted helper is not a static sealed type")
                base=self.type_ref(proof,*proof.tables.coded(definition[3],"TypeDefOrRef")) if definition[3] else ("","")
                require(base[0] in CORE_IDENTITIES and base[1]=="System.Object",f"{proof.label}: admitted helper is a delegate/custom-base selector")
                require(owner not in proof.field_owners.values() and not any(proof.tables.row(9,n)[0]==owner for n in range(1,proof.tables.counts[9]+1)) and
                        not any(proof.tables.row(25,n)[0]==owner for n in range(1,proof.tables.counts[25]+1)),f"{proof.label}: admitted helper exports a field/interface/override selector")
            bodies={rid:boundary_instructions(proof,rid) for rid in proof.method_owners}
            calls={rid:{target for op,token in il if op in (0x28,0x6f) for target in [self.resolve_self(proof,token)] if target is not None} for rid,il in bodies.items()}
            selected=set(seeds)
            while True:
                added={rid for rid,targets in calls.items() if targets&selected and self.selector(self.method(proof,(6<<24)|rid)[3])}-selected
                fields=self.verify_field_values(proof,bodies,selected)
                added|={rid for rid,il in bodies.items() if self.selector(self.method(proof,(6<<24)|rid)[3]) and
                        any(op in (0x7b,0x7c,0x7e,0x7f) and self.local_field(proof,token) in fields for op,token in il)}-selected
                if not added:break
                selected|=added
            names={proof.type_names[proof.method_owners[rid]] for rid in selected}
            for rid in selected:
                owner=proof.method_owners[rid];flags=proof.tables.row(6,rid)[2]
                external_interface=not flags&0x10 and any(proof.tables.row(9,n)[0]==owner and
                    self.type_ref(proof,*proof.tables.coded(proof.tables.row(9,n)[1],"TypeDefOrRef"))[0]!=proof.identity["fullName"] for n in range(1,proof.tables.counts[9]+1))
                require(not flags&0x40 and not external_interface and not any(proof.tables.coded(proof.tables.row(25,n)[1],"MethodDefOrRef")== (6,rid) for n in range(1,proof.tables.counts[25]+1)),
                        f"{proof.label}: selector-bearing virtual/interface implementation lacks external provider explanation")
            for rid,il in bodies.items():
                for op,token in il:
                    if op in (0xfe06,0xfe07,0x27):
                        require(self.resolve_self(proof,token) not in selected,f"{proof.label}: unproved selector delegate/function-pointer escape")
                    if op==0xd0:
                        table,index=token>>24,token&0xffffff
                        is_field=table==4 or table==10 and proof.tables.blob(proof.tables.row(10,index)[2])[:1]==b"\x06"
                        if is_field:require(self.local_field(proof,token) not in fields,f"{proof.label}: selector field token escape")
                        elif table in (6,10,43):require(self.resolve_self(proof,token) not in selected,f"{proof.label}: selector method token escape")
                        elif table in (1,2,27):
                            require(not any(identity==proof.identity["fullName"] and name in names for identity,name in self.type_components(proof,table,index)),f"{proof.label}: selector owner type token escape")
                    if op==0x72:
                        require(not self.exact_type_literal(proof.user_string(token),proof.identity["fullName"],names),f"{proof.label}: unproved literal reflection of a selector owner")
            symbols={(proof.type_names[proof.method_owners[rid]],proof.tables.string(proof.tables.row(6,rid)[3])) for rid in selected}
            symbols|={(proof.type_names[proof.field_owners[field]],proof.tables.string(proof.tables.row(4,field)[1])) for field in fields}
            brokers[proof.identity["fullName"]]=(names,symbols)
        # Linked receipts use canonical lowercase transport names while DLL
        # metadata retains its original spelling. Normalize only catalog/role
        # keys, exactly as Catalog does; full metadata identities stay exact.
        consumer_keys={name.casefold() for name in self.consumers}
        for name in self.runtime_names:
            if name.casefold() in consumer_keys:continue
            row=self.catalog.files[name.casefold()];path=_rel(self.catalog.root,row["path"],self.catalog.root,"import module")
            data=path.read_bytes();require(hashlib.sha256(data).hexdigest()==row["sha256"],f"{path}: import module bytes changed")
            proof=ImportModule(data,path)
            require(proof.identity["name"].casefold()==name.casefold(),f"{path}: import module identity differs")
            for rid in range(1,proof.tables.counts[1]+1):
                identity,declaring=self.type_ref(proof,1,rid)
                consumer_scope=next((key for key in brokers if key.split(", ")[0]==identity.split(", ")[0]),None)
                require(consumer_scope is None or declaring not in brokers[consumer_scope][0],f"{proof.label}: non-consumer imports a selector forwarder owner type without provider explanation")
            for rid in range(1,proof.tables.counts[10]+1):
                parent,name_index,_=proof.tables.row(10,rid);table,target=proof.tables.coded(parent,"MemberRefParent")
                if table not in (1,2,27):continue
                identity,declaring=self.type_ref(proof,table,target)
                consumer_scope=next((key for key in brokers if key.split(", ")[0]==identity.split(", ")[0]),None)
                require(consumer_scope is None or (declaring,proof.tables.string(name_index)) not in brokers[consumer_scope][1],
                        f"{proof.label}: non-consumer imports a selector forwarder without provider explanation")
            heap=proof.tables.streams.get("#US",b"");cursor=1
            while cursor<len(heap):
                entry=Signature(heap,proof.label,cursor);length=entry.compressed();entry.take(length)
                if length:
                    text=proof.user_string(0x70000000|cursor)
                    require(not any(self.exact_type_literal(text,identity,names) for identity,(names,_) in brokers.items()),
                            f"{proof.label}: non-consumer has an exact selector reflection literal without provider explanation")
                cursor=entry.position
        return brokers


def verify_provider_boundary(catalog,sites,runtime_names):
    return ProviderBoundary(catalog,sites,runtime_names).verify()


def captured_profile(root,snapshot,linked):
    """Rebuild actual ExportedType forwarding; never trust a recorded map alone."""
    _reflection_snapshot(root,snapshot,root,require_linked=True)
    path=root/"ReflectionBindings/LinkedRetargeting/evidence.json";receipt=_obj(path)
    facade_path=_rel(root,receipt["facadePath"],path,"captured facade")
    raw=facade_path.read_bytes();require(hashlib.sha256(raw).hexdigest()==receipt["facadeSha256"],f"{path}: captured facade changed")
    facade=RawMethodProof(raw,facade_path)
    require(facade.identity["fullName"]=="netstandard, Version=2.1.0.0, Culture=neutral, PublicKeyToken=cc7b13ffcd2ddd51",f"{path}: unsupported captured facade identity")
    def forward(rid,seen=()):
        require(rid not in seen and len(seen)<128,f"{path}: cyclic/nested exported type")
        flags,_,name,namespace,implementation=facade.tables.row(39,rid)
        name,namespace=facade.tables.string(name),facade.tables.string(namespace)
        require(name and "/" not in name,f"{path}: invalid exported metadata name")
        kind,target=facade.tables.coded(implementation,"Implementation")
        if kind==39:
            require(not namespace,f"{path}: nested export namespace differs")
            parent,destination=forward(target,(*seen,rid));return parent+"/"+name,destination
        require(kind==35 and flags&0x200000,f"{path}: top-level export is not an assembly forwarder")
        destination=facade.identity["referenceIdentities"][target-1]["fullName"]
        require(destination!=facade.identity["fullName"],f"{path}: self-forwarding facade")
        return (namespace+"." if namespace else "")+name,destination
    pairs=[forward(rid) for rid in range(1,facade.tables.counts[39]+1)]
    require(pairs and len({name for name,_ in pairs})==len(pairs),f"{path}: duplicate/empty facade forwarders")
    expected=[dict(typeFullName=name,destinationAssemblyIdentity=destination) for name,destination in sorted(pairs,key=lambda pair:ordinal(pair[0]))]
    require(_same(receipt["forwarders"],expected),f"{path}: retargeting map differs from actual facade ExportedType bytes")
    definitions={}
    for row in receipt["runtimeFrameworkModules"]:
        module=linked(row["assemblyIdentity"].split(", ")[0]);file=linked.files[module.identity["name"].casefold()]
        require(row["assemblyIdentity"]==module.identity["fullName"] and row["path"]==file["path"] and row["sha256"]==file["sha256"] and row["mvid"]==module.identity["mvid"],
                f"{path}: retargeting runtime module differs from actual linked bytes")
        require(module.identity["fullName"] not in definitions,f"{path}: duplicate runtime framework identity")
        definitions[module.identity["fullName"]]=set(module.type_names.values())
    mapping=dict(pairs)
    def scope(name,assembly):
        if assembly!=facade.identity["fullName"]:return assembly
        destination=mapping.get(name)
        require(destination in definitions and name in definitions[destination],f"{path}: facade reference lacks actual linked definition: {name}")
        return destination
    return receipt["profileHash"],scope


def compiler_mode(root,snapshot,configuration):
    if configuration["schemaVersion"]==1:return None
    if snapshot["kind"]=="PlayerBuildInputs":
        require(type(snapshot["playerBuildSucceeded"]) is bool and snapshot["playerBuildSucceeded"] and
                type(snapshot["playerBuildOptions"]) is int,f"{root}: schema-2 raw admission requires a completed Player receipt")
        return "Development" if snapshot["playerBuildOptions"]&1 else "Release"
    require(snapshot["kind"]=="CompilePlayerScripts",f"{root}: schema-2 raw admission has no compiler-mode provenance")
    path=root/"compiler-mode.json"
    receipt=_obj(path,"schemaVersion kind developmentBuild compilerOptions unityVersion target architecture snapshotHash snapshotReceiptSha256 extraScriptingDefines")
    require(receipt["schemaVersion"]==1 and receipt["kind"]=="CompilePlayerScriptsMode" and
            type(receipt["developmentBuild"]) is bool and receipt["compilerOptions"]==(1 if receipt["developmentBuild"] else 0) and
            receipt["unityVersion"]==snapshot["unityVersion"] and receipt["target"]==snapshot["target"] and
            receipt["architecture"]==snapshot["architecture"] and receipt["snapshotHash"]==snapshot["snapshotHash"] and
            receipt["snapshotReceiptSha256"]==hashlib.sha256((root/"assembly-snapshot.json").read_bytes()).hexdigest() and
            receipt["extraScriptingDefines"]==snapshot["extraScriptingDefines"],f"{path}: compiler mode is not bound to this exact snapshot")
    return "Development" if receipt["developmentBuild"] else "Release"


def selected_site(site,schema,mode,actual_hash,path):
    variants=[dict(compilerMode="Legacy",methodHash=site["methodHash"],operationIndex=site["operationIndex"])] if schema==1 else site["compilerVariants"]
    matches=[variant for variant in variants if variant["compilerMode"]==(mode or "Legacy")]
    require(len(matches)==1 and matches[0]["methodHash"]==actual_hash,
            f"{path}: configured {mode or 'Legacy'} raw method hash differs from actual compiler IL")
    result=dict(site);result["methodHash"]=matches[0]["methodHash"];result["operationIndex"]=matches[0]["operationIndex"]
    return result


def verify_snapshot(root,snapshot,require_linked=False):
    """Exact M05 raw proof over snapshot bytes; caller also verifies old policy."""
    root=_absolute(str(root),root,"raw snapshot",directory=True)
    require(str(root)==str(root.resolve()),f"{root}: aliased raw snapshot root")
    expected_hash=control_hash(snapshot["extraScriptingDefines"],root)
    directory=root/"RawTypeAdmissions"
    names={"configuration.json","compiled-evidence.json"}|({"linked-evidence.json"} if require_linked else set())
    require(directory.is_dir() and not directory.is_symlink(),f"{root}: raw admission evidence directory missing")
    entries=list(directory.rglob("*"))
    require(not any(path.is_symlink() for path in entries) and {path.relative_to(directory).as_posix() for path in entries if path.is_file()}==names,
            f"{root}: missing/extra/symlinked raw admission proof files")
    parsed=parse_configuration((directory/"configuration.json").read_bytes(),directory)
    require(parsed["configurationSha256"]==expected_hash,f"{root}: raw admission control differs from actual config bytes")
    sites=parsed["configuration"]["sites"]
    schema=parsed["configuration"]["schemaVersion"]
    mode=compiler_mode(root,snapshot,parsed["configuration"])
    compiled=Catalog(root,[row for section in ("assemblies","filteredAssemblies","references") for row in snapshot[section]])
    # Finite M05 admission, not the package's broader reusable configuration API.
    consumers={site["consumerAssembly"] for site in sites};declaring={site["declaringType"] for site in sites}
    require(consumers=={"AssemblyShadowDemo.Bootstrap"} and declaring=={HELPER_TYPE} and len(sites)==25,
            f"{root}: M05 requires exactly five raw operations for five candidate providers")
    expected={(name,operation) for name in CANDIDATES for operation in OPERATIONS}
    actual={(site["providerAssemblyIdentity"].split(", ")[0],site["operationSignature"]) for site in sites}
    require(actual==expected and len(actual)==len(sites),f"{root}: M05 raw provider/operation coverage differs")
    role_names={row["name"] for row in snapshot["assemblies"]}
    require((set(CANDIDATES)|consumers)<=role_names,f"{root}: raw provider/consumer is not actual compiled runtime input")
    for site in sites:
        name=site["providerAssemblyIdentity"].split(", ")[0]
        require(site["typeName"]==(TYPE_NAMES[name] if OPERATIONS[site["operationSignature"]]=="Module.GetType" else ""),f"{root}: raw Module literal is not the fixed M05 owner")
        operation=site["operationSignature"]
        signature=operation.split(" System.Reflection.")[0]+" "+HELPER_TYPE+"::"+HELPER_METHODS[operation]+"(System.String)"
        require(site["methodSignature"]==signature,f"{root}: raw operation is outside the exact five M05 helper methods")
    phases=[("Compiled",compiled,None,"")]
    if require_linked:
        linked=Catalog(root,[dict(row,path="LinkedPlayer/"+row["path"]) for row in snapshot["linkedPlayerReceipt"]["assemblies"]])
        profile_hash,scope=captured_profile(root,snapshot,linked)
        phases.append(("Linked",linked,scope,profile_hash))
    compiled_hashes={};selected_sites={}
    for phase,catalog,scope,profile_hash in phases:
        grouped={}
        for site in sites:grouped.setdefault((site["consumerAssembly"],site["declaringType"],site["methodSignature"]),[]).append(site)
        hashes={}
        for (consumer,declaring,signature),group in grouped.items():
            module=catalog(consumer);rid=find_method(module,declaring,signature)
            actual_hash=module.method_hash(rid)
            if phase=="Compiled":
                group=[selected_site(site,schema,mode,actual_hash,root) for site in group]
                selected_sites.update((site["id"],site) for site in group)
                compiled_hashes[(consumer,signature)]=(module,rid)
            else:
                group=[selected_sites[site["id"]] for site in group]
                original,source_rid=compiled_hashes[(consumer,signature)]
                require(original.identity["fullName"]==module.identity["fullName"] and original.method_hash(source_rid,scope)==actual_hash,
                        f"{root}: linked raw method differs beyond captured per-type retargeting")
            verify_chains(module,rid,group,catalog)
            hashes[(consumer,signature)]=actual_hash
        runtime_names=[row["name"] for section in ("assemblies","filteredAssemblies") for row in snapshot[section]] if phase=="Compiled" else [row["name"] for row in snapshot["linkedPlayerReceipt"]["assemblies"]]
        verify_provider_boundary(catalog,sites,runtime_names)
        rows=[]
        for site in sites:
            selected=selected_sites[site["id"]]
            consumer=catalog(site["consumerAssembly"]);provider=catalog(site["providerAssemblyIdentity"].split(", ")[0])
            cf=catalog.files[consumer.identity["name"].casefold()];pf=catalog.files[provider.identity["name"].casefold()]
            row=dict(id=site["id"],consumerAssemblyIdentity=consumer.identity["fullName"],consumerPath=cf["path"],consumerSha256=cf["sha256"],
                     providerAssemblyIdentity=provider.identity["fullName"],providerPath=pf["path"],providerSha256=pf["sha256"],providerInventoryHash=type_inventory_hash(provider),
                     declaringType=site["declaringType"],methodSignature=site["methodSignature"],operationIndex=selected["operationIndex"],
                     operationSignature=site["operationSignature"],kind=OPERATIONS[site["operationSignature"]],typeName=site["typeName"],
                     throwOnError=site["throwOnError"],ignoreCase=site["ignoreCase"],compiledMethodHash=selected["methodHash"],
                     linkedMethodHash=hashes[(site["consumerAssembly"],site["methodSignature"])] if phase=="Linked" else "",
                     compiledConsumerSha256=compiled.files[site["consumerAssembly"].casefold()]["sha256"])
            rows.append(row)
        expected=dict(schemaVersion=1,policy=parsed["configuration"]["policy"],phase=phase,configurationSha256=parsed["configurationSha256"],configurationHash=parsed["configurationHash"],
                      unityVersion=snapshot["unityVersion"],target=snapshot["target"],architecture=snapshot["architecture"],
                      buildGuid=snapshot["buildGuid"] if phase=="Linked" else "",linkedPlayerReceiptHash=snapshot["linkedPlayerReceiptHash"] if phase=="Linked" else "",
                      profileHash=profile_hash,sites=rows)
        path=directory/(phase.lower()+"-evidence.json");claimed=_obj(path,PROOF_FIELDS)
        require(type(claimed["sites"]) is list,f"{path}: raw proof sites must be an array")
        for row in claimed["sites"]:_fields(row,PROOF_SITE_FIELDS,path)
        require(_same(claimed,expected),f"{path}: raw receipt differs from independently derived metadata/IL/retarget proof")
        # JsonUtility's declared order/4-space pretty form, no newline, for this
        # string/int/bool-only DTO. Unknown and duplicate members already fail.
        require(path.read_bytes()==json.dumps(expected,ensure_ascii=False,indent=4).encode("utf-8"),f"{path}: raw derived receipt bytes are noncanonical")
    return parsed
