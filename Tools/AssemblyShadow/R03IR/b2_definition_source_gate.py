"""Read-only exact-source proof for an INACTIVE restricted B2 native producer.

This is not a Unity build, complete V2 field15, an executable source admission,
an independent metadata lifetime proof, or authorization to run Local Validation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

MANIFEST="Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json"
FIXED_B1_DEMO="2d690bb2f7234ddcbee339f9da7125d687f5ed45"
FIXED_B1_NATIVE="8aa8d09319a89b55b2496bcc2c69ccc69cb57be9"
FIXED_HYBRIDCLR="4b2774b066cfc6afd77a8c8aded6bda7ea574f55"
FIXED_UNITY="948c0e3b4f8891481301770115e8ba4945eea6de"
NATIVE_REQUIRED={
    "libil2cpp/vm/AssemblyShadow.cpp",
    "libil2cpp/vm/GlobalMetadataFileInternals.h",
    "libil2cpp/vm/AssemblyShadow.h",
    "libil2cpp/vm/AssemblyShadowTypeKey.cpp",
    "libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLive.h",
    "libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl",
    "libil2cpp/vm/AssemblyShadowOwnedDefinitionTypeKey.h",
    "libil2cpp/vm/AssemblyShadowOwnedConstructedTypeKey.h",
    "libil2cpp/vm/AssemblyShadowOwnedExecutionRows.h",
    "NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp",
    "NativeHostTests/AssemblyShadowOwnedConstructedTypeKeyHost.cpp",
    ".github/workflows/r03-native-b2-definition-live-source-host.yml",
    ".github/workflows/r03-native-b2-constructed-typekey-host.yml",
    "NativeHostTests/README.md",
}
DEMO_REQUIRED={
    "Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOwnedDefinitionTypeKey.h",
    "Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOwnedConstructedTypeKey.h",
    "Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOwnedExecutionRows.h",
}
class Rejected(ValueError):
    pass

def require(value:bool,what:str):
    if not value:
        raise Rejected(what)

def git(root:Path,*args:str)->str:
    p=subprocess.run(["git","-C",str(root),*args],capture_output=True,
                     text=True,timeout=30)
    require(p.returncode==0,"git failed: "+" ".join(args))
    return p.stdout.strip()

def blob(raw:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()

def verify_file(root:Path,path:str,digest:str)->bytes:
    require(type(path) is str and path and not path.startswith("/") and
            ".." not in Path(path).parts and "\x00" not in path,
            "Untrusted source path")
    require(type(digest) is str and re.fullmatch("[0-9a-f]{40}",digest) is not None,
            "Untrusted Git blob ID")
    f=root/path
    require(f.is_file() and not f.is_symlink() and f.resolve()==f,
            "File missing or source alias: "+path)
    raw=f.read_bytes()
    require(blob(raw)==digest,"Unreviewed file bytes: "+path)
    require(git(root,"ls-tree","HEAD","--",path)==
            "100644 blob "+digest+"\t"+path,
            "Remote tree and file mismatch: "+path)
    return raw

def validate_contract(m:dict)->None:
    require(type(m) is dict and m.get("schemaVersion")==1 and
            m.get("kind")=="R03B2RestrictedPhysicalDefinitionSourceCandidate",
            "Manifest identity")
    require(m.get("branch")=="codex/assembly-shadow-r01b-h1",
            "Wrong branch")
    for key in ("candidateNative","originalB1Native","originalB1ExecutionDemo",
                "hybridclr","hybridclr_unity"):
        require(type(m.get(key)) is str and
                re.fullmatch("[0-9a-f]{40}",m[key]) is not None,
                "Invalid source pin: "+key)
    require(m["originalB1ExecutionDemo"]==FIXED_B1_DEMO and
            m["originalB1Native"]==FIXED_B1_NATIVE and
            m["hybridclr"]==FIXED_HYBRIDCLR and
            m["hybridclr_unity"]==FIXED_UNITY,
            "Previously accepted source tuple must remain immutable")
    c=m.get("nativeSourceCapabilities")
    require(type(c) is dict and
            c.get("sourceReadsAfterTerminal") is False and
            c.get("arbitraryGenericInstantiationTypeKeys") is False and
            c.get("coherentVmEpochProven") is False,
            "Cannot invent terminal/full-key/VM-epoch acceptance")
    for key,required in (("nativeSources",NATIVE_REQUIRED),
                         ("demoPureSources",DEMO_REQUIRED)):
        rows=m.get(key)
        require(type(rows) is list and len(rows)==len(required) and
                all(type(row) is dict and set(row)=={"path","gitBlob"} for row in rows),
                "Source roster format: "+key)
        require({row["path"] for row in rows}==required,
                "Exact source roster: "+key)
        for row in rows:
            require(type(row["gitBlob"]) is str and
                    re.fullmatch("[0-9a-f]{40}",row["gitBlob"]) is not None,
                    "Source blob ID: "+row["path"])
            require(type(row["path"]) is str and row["path"] and
                    ".." not in Path(row["path"]).parts and
                    not row["path"].startswith("/"),
                    "Noncanonical source entry")
    for key in ("readyForNativeV2FieldCapture","nativeV2TransportImplemented",
                "runtimeAcceptance","R03Accepted","H2Passed",
                "ReadyForHumanReviewGate"):
        require(m.get(key) is False,"Illegal product acceptance: "+key)
    require(m.get("handoffAuthority")=="CLOSED_NO_LOCAL_EXECUTION",
            "Cannot authorize Local from source audit")

def source_boundary(native:dict[str,bytes])->None:
    def must(path:str,*tokens:str):
        txt=native[path].decode("utf8","strict")
        for token in tokens:
            require(token in txt,"Native source drift: "+path+" : "+token)
    must("libil2cpp/vm/GlobalMetadataFileInternals.h",
         "typedef struct Il2CppTypeDefinition",
         "TypeIndex declaringTypeIndex",
         "GenericContainerIndex genericContainerIndex")
    must("libil2cpp/vm/AssemblyShadowTypeKey.cpp",
         "case IL2CPP_TYPE_GENERICINST:",
         'value = "generic(" + FormatType(generic->type',
         'Part(FormatType(generic->context.class_inst->type_argv[index]',
         "kMaximumTypeDepth = 128")
    must("libil2cpp/vm/AssemblyShadowOwnedConstructedTypeKey.h",
         'Put("generic(",8)', 'Decimal(argument.Bytes())',
         "kMaximumArguments=16",
         "AddArgument(")
    must("libil2cpp/vm/AssemblyShadow.cpp",
         '#include "AssemblyShadowBoundedDefinitionExecutionLive.h"',
         '#include "vm/GlobalMetadataFileInternals.h"',
         '#include "AssemblyShadowBoundedDefinitionExecutionLiveSource.inl"')
    must("libil2cpp/vm/AssemblyShadow.h",
         "TryCaptureBoundedDefinitionExecutionLive",
         "does NOT replace the original live execution diagnostics getter")
    must("libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl",
         "assembly_shadow_metadata_lifetime::Gate::Reader admission",
         "il2cpp_class_for_each",
         "metadataLock(&g_MetadataLock)",
         "TryObservedRegistrationBinding",
         "MetadataCache::GetAssemblyTypeHandle",
         "GlobalMetadata::GetTypeNamespaceAndName",
         "GlobalMetadata::GetIl2CppTypeFromIndex",
         "IL2CPP_TYPE_GENERICINST",
         "generic->context.class_inst",
         "definitionArity!=instance->type_argc",
         "constructed_key::Capture genericKey",
         "buildDefinition(arg->data.typeHandle",
         "kMaximumTotalMetadataLookups",
         "assembly_shadow_first_failure_v2::State::Empty",
         "s_executionRegistrationWitnesses",
         "rows.Seal()",
         "record.Freeze()",
         "r02::Snapshot::TryCaptureCurrent",
         "not an all-VM linearization")
    must("libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLive.h",
         "callbackPhysicalMembershipProven",
         "completeArbitraryTypeKeys=false",
         "completeExecutionDiagnostics=false",
         "coherentVmEpochProven=false",
         "nativeV2TransportImplemented=false",
         "runtimeAcceptance=false")
    must("NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp",
         '#include "vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl"',
         "Mode::StagedNestedIndex",
         "Mode::CyclicNested",
         "Mode::GenericDefinition",
         "Mode::GenericSameImage",
         "Mode::GenericNestedArgument",
         "Mode::GenericTooManyArguments",
         "Mode::NestedType",
         "Mode::CounterChanged",
         "NoMetadataAdmission")
    for name in (
        "libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl",
        "libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLive.h",
        "libil2cpp/vm/AssemblyShadowOwnedDefinitionTypeKey.h",
        "libil2cpp/vm/AssemblyShadowOwnedConstructedTypeKey.h",
        "libil2cpp/vm/AssemblyShadowOwnedExecutionRows.h",
    ):
        raw=native[name]
        require(b"operator new" not in raw and b"int main(" not in raw,
                "Standalone allocator/host driver leaked into production vm: "+name)

def inspect(demo:Path,native:Path,expected_demo:str,expected_native:str)->dict:
    demo=demo.resolve(strict=True)
    native=native.resolve(strict=True)
    require(demo!=native and demo not in native.parents and native not in demo.parents,
            "Separate repository roots")
    require(git(demo,"rev-parse","HEAD")==expected_demo,"Demo HEAD")
    require(git(native,"rev-parse","HEAD")==expected_native,"Native HEAD")
    require(not git(demo,"status","--porcelain","--untracked-files=no"),
            "Dirty demo tracked source")
    require(not git(native,"status","--porcelain","--untracked-files=no"),
            "Dirty native tracked source")
    mf=demo/MANIFEST
    require(mf.is_file() and not mf.is_symlink(),"No authenticated candidate manifest")
    m=json.loads(mf.read_text(encoding="utf8"))
    validate_contract(m)
    require(m["candidateNative"]==expected_native,"Candidate source pin drift")
    d={r["path"]:verify_file(demo,r["path"],r["gitBlob"])
       for r in m["demoPureSources"]}
    n={r["path"]:verify_file(native,r["path"],r["gitBlob"])
       for r in m["nativeSources"]}
    source_boundary(n)
    key=d["Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOwnedDefinitionTypeKey.h"]
    rows=d["Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOwnedExecutionRows.h"]
    require(n["libil2cpp/vm/AssemblyShadowOwnedDefinitionTypeKey.h"]==key,
            "Fork TypeKey diverged from independently tested pure original")
    composed=d["Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOwnedConstructedTypeKey.h"]
    require(n["libil2cpp/vm/AssemblyShadowOwnedConstructedTypeKey.h"].replace(
                b'"AssemblyShadowOwnedDefinitionTypeKey.h"',
                b'"BoundedOwnedDefinitionTypeKey.h"')==composed,
            "Fork generic composer diverged from independent pure source")
    require(n["libil2cpp/vm/AssemblyShadowOwnedExecutionRows.h"].replace(
                b'"AssemblyShadowOwnedDefinitionTypeKey.h"',
                b'"BoundedOwnedDefinitionTypeKey.h"').replace(
                b'"AssemblyShadowOwnedConstructedTypeKey.h"',
                b'"BoundedOwnedConstructedTypeKey.h"')==rows,
            "Fork owned-row source diverged beyond local include path")
    return {
        "kind":"R03B2RestrictedDefinitionExactSourceGate",
        "result":"PassedInactiveSourceOnly_NotFullV2",
        "verifiedNativeFiles":len(n),
        "verifiedDemoPureFiles":len(d),
        "pins":{"hybridclr_demo":expected_demo,"il2cpp_plus":expected_native,
                "hybridclr":m["hybridclr"],"hybridclr_unity":m["hybridclr_unity"]},
        "supportedSubset":"Physical AOT TypeDef definitions and same-image concrete GENERICINST TypeDef arguments only",
        "liveMetadataReadProvenByUnity":False,
        "readyForNativeV2FieldCapture":False,
        "nativeV2TransportImplemented":False,
        "runtimeAcceptance":False,
        "R03Accepted":False,
        "H2Passed":False,
        "ReadyForHumanReviewGate":False,
        "handoffAuthority":"CLOSED_NO_LOCAL_EXECUTION"
    }

def main()->int:
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--demo",type=Path,required=True)
    a.add_argument("--native",type=Path,required=True)
    a.add_argument("--expected-demo",required=True)
    a.add_argument("--expected-native",required=True)
    v=a.parse_args()
    try:
        result=inspect(v.demo,v.native,v.expected_demo,v.expected_native)
    except (Rejected,OSError,ValueError,UnicodeError) as e:
        print(json.dumps({"result":"Rejected","reason":str(e),
                          "readyForNativeV2FieldCapture":False},sort_keys=True))
        return 2
    print(json.dumps(result,sort_keys=True))
    return 0

if __name__=="__main__":
    sys.exit(main())
