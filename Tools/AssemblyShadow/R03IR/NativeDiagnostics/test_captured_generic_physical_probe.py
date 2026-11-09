#!/usr/bin/env python3
"""Compile the EXACT A2 native probe with VM-shaped C++11 test doubles.

This is a mock of IL2CPP metadata/runtime APIs, NEVER an actual Unity Player
or native error15 proof. Positive and negative host evidence is explicitly
separated from the Source/Player acquisition obligation.
"""
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from verify_captured_generic_native import verify as verify_native_receipt
NATIVE = HERE.parent / "PlayerProject/R03CapturedGenericPhysicalProbe.cpp"
HEADERS = {
    "il2cpp-config.h": """
#pragma once
#define HYBRIDCLR_R03_RUNTIME_PROBE 1
#define HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW 1
#define IL2CPP_EXPORT
""",
    "il2cpp-class-internals.h": """
#pragma once
#include <cstdint>
#define IL2CPP_TYPE_I4 8
#define IL2CPP_TYPE_CLASS 18
#define FIELD_ATTRIBUTE_STATIC 16
#define METHOD_ATTRIBUTE_STATIC 16
typedef const void* Il2CppMetadataTypeHandle;
struct Il2CppAssembly;
struct Il2CppImage { Il2CppAssembly* assembly; uint32_t typeCount; };
struct Il2CppAssemblyName { const char* name; };
struct Il2CppAssembly { Il2CppImage* image; Il2CppAssemblyName aname; };
struct Il2CppType {
    union { void* dummy; Il2CppMetadataTypeHandle typeHandle; } data;
    uint32_t attrs;
    uint32_t type;
};
struct Il2CppClass { Il2CppImage* image; void* static_fields; uint32_t static_fields_size; };
struct FieldInfo { const char* name; const Il2CppType* type; Il2CppClass* parent; int32_t offset; };
struct Il2CppGenericInst { uint32_t type_argc; const Il2CppType** type_argv; };
struct Il2CppGenericContext { const Il2CppGenericInst* class_inst; const Il2CppGenericInst* method_inst; };
struct MethodInfo;
struct Il2CppGenericMethod { const MethodInfo* methodDefinition; Il2CppGenericContext context; };
struct MethodInfo {
    const char* name;
    Il2CppClass* klass;
    const Il2CppGenericMethod* genericMethod;
    uint16_t flags;
    bool is_generic;
    bool is_inflated;
};
""",
    "il2cpp-object-internals.h": """
#pragma once
#include "il2cpp-class-internals.h"
#include <exception>
struct Il2CppObject { void* klass; };
struct Il2CppException {};
struct Il2CppExceptionWrapper : std::exception {};
""",
    "vm/AssemblyShadow.h": """
#pragma once
#include <cstdint>
#include <string>
#include "il2cpp-class-internals.h"
namespace il2cpp { namespace vm {
enum class AssemblyShadowState { Disabled=0, Committed=6, FailedAfterCommit=9 };
enum class AssemblyShadowError { Success=0, BaselineAlreadyUsed=15 };
struct AssemblyShadow {
    static uint64_t ActiveGeneration();
    static bool IsCandidate(const Il2CppAssembly*);
    static bool IsShadowedBaseline(const Il2CppAssembly*);
    static bool IsActiveShadow(const Il2CppAssembly*);
    static AssemblyShadowError GetState(AssemblyShadowState&);
    static bool AssertMethodIsActive(const MethodInfo*,const char*) noexcept;
    static AssemblyShadowError GetRecoveryInfoJson(std::string&);
};
}}
""",
    "vm/Assembly.h": "#pragma once\n#include \"il2cpp-class-internals.h\"\n",
    "vm/MetadataCache.h": """
#pragma once
#include <utility>
#include "il2cpp-class-internals.h"
namespace il2cpp { namespace vm {
struct MetadataCache {
    static const Il2CppAssembly* GetAotAssemblyByNamePhysical(const char*);
    static Il2CppMetadataTypeHandle GetAssemblyTypeHandle(const Il2CppImage*,uint32_t);
    static std::pair<const char*,const char*> GetTypeNamespaceAndName(Il2CppMetadataTypeHandle);
    static const MethodInfo* GetGenericInstanceMethod(const MethodInfo*,const Il2CppType**,uint32_t);
};
}}
""",
    "vm/Image.h": """
#pragma once
#include "il2cpp-class-internals.h"
namespace il2cpp { namespace vm { struct Image {
    static Il2CppClass* ClassFromName(Il2CppImage*,const char*,const char*);
}; }}
""",
    "vm/Class.h": """
#pragma once
#include "il2cpp-class-internals.h"
namespace il2cpp { namespace vm { struct Class {
    static const MethodInfo* GetMethodFromName(Il2CppClass*,const char*,int);
    static const FieldInfo* GetFieldFromName(Il2CppClass*,const char*);
}; }}
""",
    "vm/Runtime.h": """
#pragma once
#include "il2cpp-object-internals.h"
namespace il2cpp { namespace vm { struct Runtime {
    static Il2CppObject* Invoke(const MethodInfo*,void*,void**,Il2CppException**);
}; }}
""",
}
DRIVER = r"""
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iterator>
#include <string>
#include "il2cpp-config.h"
#include "il2cpp-class-internals.h"
#include "il2cpp-object-internals.h"
#include "vm/AssemblyShadow.h"
#include "vm/MetadataCache.h"
#include "vm/Image.h"
#include "vm/Class.h"
#include "vm/Runtime.h"
using namespace il2cpp::vm;

static AssemblyShadowState state=AssemblyShadowState::Disabled;
static int32_t bodyCalls=1, guardCalls=0, invokeCalls=0;
static int32_t mode=0; // 0=valid,1=bad owner,2=bad generic,3=wrong physical name,4=body escaped,5=silent-null
static Il2CppImage ownerImage{}, baselineImage{};
static Il2CppAssembly ownerAssembly{}, baselineAssembly{};
static Il2CppClass ownerClass{};
static Il2CppType counterType{};
static FieldInfo counterField{};
static MethodInfo definition{}, inflated{};
static Il2CppGenericMethod gmethod{};
static Il2CppGenericInst genericInst{};
static const Il2CppType* arguments[1]={};
static int baselineOtherHandle=1, baselineNodeHandle=2;
static Il2CppObject resultBox{};
static Il2CppException exception{};

uint64_t AssemblyShadow::ActiveGeneration() { return state==AssemblyShadowState::Disabled?0:1; }
bool AssemblyShadow::IsCandidate(const Il2CppAssembly* a) {
    return mode==1 && a==&ownerAssembly;
}
bool AssemblyShadow::IsShadowedBaseline(const Il2CppAssembly* a) {
    return a==&baselineAssembly && state!=AssemblyShadowState::Disabled;
}
bool AssemblyShadow::IsActiveShadow(const Il2CppAssembly*) { return false; }
AssemblyShadowError AssemblyShadow::GetState(AssemblyShadowState& out) {
    out=state;return AssemblyShadowError::Success;
}
bool AssemblyShadow::AssertMethodIsActive(const MethodInfo* method,const char* site) noexcept {
    ++guardCalls;
    assert(method==&inflated && site && strstr(site,"PhysicalCaptured"));
    state=AssemblyShadowState::FailedAfterCommit;
    return false; // HOST FAKE only, actual native guard is NOT executed
}
AssemblyShadowError AssemblyShadow::GetRecoveryInfoJson(std::string& out) {
    out="{\"schemaVersion\":1,\"enabled\":true,\"capabilityVersion\":1,"
        "\"stateCode\":9,\"state\":\"FailedAfterCommit\","
        "\"published\":true,\"abortAllowed\":false,\"dispositionCode\":0,"
        "\"disposition\":\"RestartRequired\",\"terminalFailureCode\":15,"
        "\"reason\":\"ShadowCapturedBaselineType Assembly=Assembly-CSharp"
        " CapturedArgumentAssembly=Methods TypePath=/arg[0] Reason=CapturedBaselineType\","
        "\"retainedBytes\":2048,\"baselineEligibilityRequiresStartupValidation\":true}";
    return AssemblyShadowError::Success;
}
const Il2CppAssembly* MetadataCache::GetAotAssemblyByNamePhysical(const char* name) {
    return strcmp(name,"Assembly-CSharp")==0?&ownerAssembly:
           strcmp(name,"Methods")==0?&baselineAssembly:nullptr;
}
Il2CppMetadataTypeHandle MetadataCache::GetAssemblyTypeHandle(const Il2CppImage* image,uint32_t index) {
    return image==&baselineImage ? (index==0?&baselineOtherHandle:&baselineNodeHandle):nullptr;
}
std::pair<const char*,const char*> MetadataCache::GetTypeNamespaceAndName(Il2CppMetadataTypeHandle handle) {
    if(handle==&baselineOtherHandle) return {"R03","Other"};
    if(handle==&baselineNodeHandle) return {"R03",mode==3?"NotNode":"Node"};
    return {"",""};
}
const MethodInfo* MetadataCache::GetGenericInstanceMethod(
    const MethodInfo* method,const Il2CppType** input,uint32_t count) {
    assert(method==&definition && count==1);
    arguments[0]=input[0]; genericInst.type_argc=1;genericInst.type_argv=arguments;
    gmethod.methodDefinition=method;gmethod.context.method_inst=&genericInst;
    inflated=definition;
    inflated.is_generic=false;inflated.is_inflated=mode!=2;
    inflated.genericMethod=&gmethod;
    return &inflated;
}
Il2CppClass* Image::ClassFromName(Il2CppImage* image,const char* ns,const char* type) {
    if(image!=&ownerImage || strcmp(ns,"AssemblyShadow.R03.IR")!=0 ||
       strcmp(type,"R03CapturedGenericAotOwner")!=0)return nullptr;
    return &ownerClass;
}
const MethodInfo* Class::GetMethodFromName(Il2CppClass* cl,const char* name,int argc) {
    return cl==&ownerClass && argc==0 && strcmp(name,"Touch")==0?&definition:nullptr;
}
const FieldInfo* Class::GetFieldFromName(Il2CppClass* cl,const char* name) {
    return cl==&ownerClass && strcmp(name,"s_calls")==0?&counterField:nullptr;
}
Il2CppObject* Runtime::Invoke(const MethodInfo* method,void*,void**,Il2CppException** ex) {
    assert(method==&inflated);++invokeCalls;
    if(mode==4) {++bodyCalls; *ex=nullptr;return &resultBox;}
    if(mode==5) {*ex=nullptr;return nullptr;}
    *ex=&exception;return nullptr;
}
extern "C" int32_t R03_IRG_Open(const char*,const char*,const char*,const char*,const char*);
extern "C" int32_t R03_IRG_Probe();
extern "C" int32_t R03_IRG_AttemptRuntimeInvoke();
extern "C" int32_t R03_IRG_Seal();

int main(int argc,char** argv) {
    if(argc!=3)return 99;
    const std::string kind=argv[1];
    if(kind=="bad-owner") mode=1;
    else if(kind=="bad-generic") mode=2;
    else if(kind=="wrong-physical") mode=3;
    else if(kind=="escaped-body") mode=4;
    else if(kind=="silent-null") mode=5;
    ownerImage.assembly=&ownerAssembly;
    ownerAssembly.image=&ownerImage;ownerAssembly.aname.name="Assembly-CSharp";
    baselineImage.assembly=&baselineAssembly;baselineImage.typeCount=2;
    baselineAssembly.image=&baselineImage;baselineAssembly.aname.name="Methods";
    ownerClass.image=&ownerImage;ownerClass.static_fields=&bodyCalls;
    ownerClass.static_fields_size=sizeof(bodyCalls);
    counterType.type=IL2CPP_TYPE_I4;counterType.attrs=FIELD_ATTRIBUTE_STATIC;
    counterField={"s_calls",&counterType,&ownerClass,0};
    definition.name="Touch";definition.klass=&ownerClass;
    definition.flags=METHOD_ATTRIBUTE_STATIC;definition.is_generic=true;
    definition.is_inflated=false;
    const char* nonce="a123456789abcdef123456789abcdef";
    const char* fixture="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    if(kind=="preexisting") {
        std::ofstream pre(argv[2]);pre<<"DO_NOT_OVERWRITE";pre.close();
        assert(R03_IRG_Open(argv[2],nonce,"IR-R03-02-captured-generic",
                           fixture,"Assembly-CSharp")!=1);
        std::ifstream test(argv[2]);std::string existing;
        std::getline(test,existing);
        assert(existing=="DO_NOT_OVERWRITE");
        return 0;
    }
    const int open=R03_IRG_Open(argv[2],nonce,"IR-R03-02-captured-generic",
                                fixture,"Assembly-CSharp");
    if(kind=="bad-owner") {
        assert(open!=1);
        std::ifstream none(argv[2]);assert(!none.good());
        return 0;
    }
    assert(open==1);
    assert(R03_IRG_Open(argv[2],nonce,"IR-R03-02-captured-generic",
                        fixture,"Assembly-CSharp")!=1);
    if(kind=="premature") {
        assert(R03_IRG_Probe()!=1);
        std::ifstream empty(argv[2]);empty.seekg(0,std::ios::end);
        assert(empty.tellg()==0);
        return 0;
    }
    state=AssemblyShadowState::Committed;
    const int probe=R03_IRG_Probe();
    if(kind=="bad-generic"||kind=="wrong-physical") {
        assert(probe!=1);
        assert(guardCalls==0);
        std::ifstream empty(argv[2]);empty.seekg(0,std::ios::end);
        assert(empty.tellg()==0);
        return 0;
    }
    assert(probe==1);
    assert(guardCalls==1 && state==AssemblyShadowState::FailedAfterCommit);
    const int attempt=R03_IRG_AttemptRuntimeInvoke();
    if(kind=="escaped-body" || kind=="silent-null") {
        assert(attempt!=1);
        assert(bodyCalls==(kind=="escaped-body"?2:1));
        assert(R03_IRG_Seal()!=1);
        return 0;
    }
    assert(attempt==1 && bodyCalls==1 && invokeCalls==1);
    assert(R03_IRG_Seal()==1);
    assert(R03_IRG_Seal()!=1);
    std::ifstream input(argv[2]);
    const std::string raw((std::istreambuf_iterator<char>(input)),
                          std::istreambuf_iterator<char>());
    assert(raw.find("\"methodContextPhysical\":true")!=std::string::npos);
    assert(raw.find("\"ownerIndependentAot\":true")!=std::string::npos);
    assert(raw.find("\"terminalFailureCode\":15")!=std::string::npos);
    assert(raw.find("\"runtimeAcceptance\":false")!=std::string::npos);
    assert(raw.find("\"beforeCount\":1,\"afterCount\":1")!=std::string::npos);
    assert(raw.find("\"runtimeInvokeAttempted\":true")!=std::string::npos);
    return 0;
}
"""


class NativePhysicalCapturedProbeTests(unittest.TestCase):
    def test_actual_native_source_compiles_and_negative_host_controls(self):
        self.assertTrue(NATIVE.is_file())
        original = NATIVE.read_bytes()
        for symbol in (b"MetadataCache::GetAssemblyTypeHandle",
                       b"MetadataCache::GetGenericInstanceMethod",
                       b"AssemblyShadow::AssertMethodIsActive",
                       b"Runtime::Invoke", b"GetRecoveryInfoJson",
                       b"O_NOFOLLOW", b"O_EXCL"):
            self.assertIn(symbol, original)
        compilers = [x for x in ("clang++", "g++") if shutil.which(x)]
        self.assertTrue(compilers)
        with tempfile.TemporaryDirectory(prefix="r03-irg-native-host-") as temporary:
            root = Path(temporary).resolve()
            for rel, value in HEADERS.items():
                file = root / rel
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text(value, encoding="utf-8")
            driver = root / "driver.cpp"
            driver.write_text(DRIVER, encoding="utf-8")
            for compiler in compilers:
                binary = root / compiler.replace("+", "p")
                with self.subTest(compiler=compiler):
                    result = subprocess.run([
                        compiler, "-std=c++11", "-Wall", "-Wextra", "-Werror",
                        "-I", str(root), str(NATIVE), str(driver),
                        "-o", str(binary)],
                        capture_output=True, text=True, timeout=120)
                    self.assertEqual(result.returncode, 0, result.stderr)
                for kind in ("valid", "bad-owner", "bad-generic", "wrong-physical",
                             "premature", "escaped-body", "silent-null", "preexisting"):
                    out = root / (compiler.replace("+", "p") + "-" + kind + ".json")
                    process = subprocess.Popen([str(binary), kind, str(out)],
                                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               text=True)
                    stdout, stderr = process.communicate(timeout=15)
                    with self.subTest(compiler=compiler, kind=kind):
                        self.assertEqual(process.returncode, 0, stdout + stderr)
                        if kind == "valid":
                            receipt = verify_native_receipt(
                                out.read_bytes(), {
                                    "runId": "a123456789abcdef123456789abcdef",
                                    "caseId": "IR-R03-02-captured-generic",
                                    "stimulus": "captured-generic",
                                    "dllSha256": "a"*64,
                                }, expected_pid=process.pid,
                                expected_owner="Assembly-CSharp",
                                expected_fixture_sha256="a"*64)
                            self.assertEqual(receipt["result"],
                                "SchemaConsistentNotRuntimeAuthenticated")
                            self.assertFalse(receipt["nativeVMProofIndependent"])
                        elif kind in ("bad-owner", "preexisting"):
                            self.assertFalse(kind == "bad-owner" and out.exists())
                        else:
                            self.assertFalse(out.is_file() and
                                             b'"runtimeAcceptance":false' in out.read_bytes())
        self.assertEqual(hashlib.sha256(NATIVE.read_bytes()).digest(),
                         hashlib.sha256(original).digest())


if __name__ == "__main__":
    unittest.main(verbosity=2)
