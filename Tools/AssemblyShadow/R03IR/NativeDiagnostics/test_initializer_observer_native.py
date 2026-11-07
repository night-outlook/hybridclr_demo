#!/usr/bin/env python3
"""Compile exact additive initializer observer with C++11 VM-shaped test doubles."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parent.parent / "PlayerProject/R03InitializerPreparedProbe.cpp"
HEADERS = {
    "il2cpp-config.h": """#pragma once
#define IL2CPP_EXPORT
#define HYBRIDCLR_R03_RUNTIME_PROBE 1
#define HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW 1
""",
    "il2cpp-class-internals.h": """#pragma once
#include <cstdint>
struct Il2CppAssembly;
struct Il2CppClass;
struct Il2CppImage { Il2CppAssembly* assembly; };
struct Il2CppAssembly { Il2CppImage* image; };
struct Il2CppType { int type; int attrs; };
struct FieldInfo { const char* name; const Il2CppType* type; Il2CppClass* parent; int32_t offset; };
struct Il2CppClass { Il2CppImage* image; void* static_fields; uint32_t static_fields_size; uint32_t instance_size; };
#define FIELD_ATTRIBUTE_STATIC 0x10
#define IL2CPP_TYPE_I4 0x08
""",
    "il2cpp-object-internals.h": """#pragma once
#include "il2cpp-class-internals.h"
struct Il2CppObject { Il2CppClass* klass; };
""",
    "vm/AssemblyShadow.h": """#pragma once
#include "il2cpp-class-internals.h"
namespace il2cpp { namespace vm {
enum class AssemblyShadowState { Committing=5, Committed=6, FailedAfterCommit=9 };
enum class AssemblyShadowError { Success=0 };
struct AssemblyShadow {
 static AssemblyShadowError GetState(AssemblyShadowState&);
 static bool IsActiveShadow(const Il2CppAssembly*);
};
}}
""",
    "vm/Assembly.h": """#pragma once
#include "il2cpp-class-internals.h"
namespace il2cpp { namespace vm {
struct Assembly { static const Il2CppAssembly* GetLoadedAssembly(const char*); };
}}
""",
    "vm/Image.h": """#pragma once
#include "il2cpp-class-internals.h"
namespace il2cpp { namespace vm {
struct Image { static Il2CppClass* ClassFromName(Il2CppImage*,const char*,const char*); };
}}
""",
    "vm/Class.h": """#pragma once
#include "il2cpp-class-internals.h"
namespace il2cpp { namespace vm {
struct Class { static FieldInfo* GetFieldFromName(Il2CppClass*,const char*); };
}}
""",
    "gc/GCHandle.h": """#pragma once
#include "il2cpp-object-internals.h"
namespace il2cpp { namespace gc {
struct GCHandle {
 static uint32_t New(Il2CppObject*,bool);
 static Il2CppObject* GetTarget(uint32_t);
 static void Free(uint32_t);
};
}}
""",
    "hybridclr/interpreter/MethodBridge.h": """#pragma once
#include <cstdint>
namespace hybridclr { namespace interpreter {
struct Managed2NativeFunctionPointerCallData {
    const char* methodSig;
    void (*methodPointer)();
};
extern const Managed2NativeFunctionPointerCallData g_managed2NativeFunctionPointerCallStub[];
}}
""",
}
DRIVER = r"""
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <cstdio>
#include "il2cpp-config.h"
#include "il2cpp-class-internals.h"
#include "il2cpp-object-internals.h"
#include "vm/AssemblyShadow.h"
#include "vm/Assembly.h"
#include "vm/Image.h"
#include "vm/Class.h"
#include "gc/GCHandle.h"
static auto state=il2cpp::vm::AssemblyShadowState::Committing;
static Il2CppImage image{};
static Il2CppAssembly assembly{};
struct Node { Il2CppObject object; int32_t stable; };
struct Witness { Il2CppObject* instance; int32_t preField,ready,direct,delegated,generic; };
static Node node{};
static Witness values{};
static Il2CppClass nodeClass{}, witnessClass{};
static Il2CppType integer{IL2CPP_TYPE_I4,0};
static Il2CppType staticInteger{IL2CPP_TYPE_I4,FIELD_ATTRIBUTE_STATIC};
static Il2CppType staticReference{0,FIELD_ATTRIBUTE_STATIC};
static FieldInfo fields[7]{};
il2cpp::vm::AssemblyShadowError il2cpp::vm::AssemblyShadow::GetState(
    il2cpp::vm::AssemblyShadowState& out) { out=state; return AssemblyShadowError::Success; }
bool il2cpp::vm::AssemblyShadow::IsActiveShadow(const Il2CppAssembly* a) { return a==&assembly; }
const Il2CppAssembly* il2cpp::vm::Assembly::GetLoadedAssembly(const char* name) {
    return strcmp(name,"Methods")==0?&assembly:nullptr;
}
Il2CppClass* il2cpp::vm::Image::ClassFromName(Il2CppImage* i,const char* ns,const char* name) {
    if(i!=&image || strcmp(ns,"R03")!=0) return nullptr;
    return strcmp(name,"Node")==0?&nodeClass:
           strcmp(name,"TerminalWitness")==0?&witnessClass:nullptr;
}
FieldInfo* il2cpp::vm::Class::GetFieldFromName(Il2CppClass* k,const char* name) {
    for(auto& f:fields) if(f.parent==k && strcmp(f.name,name)==0) return &f;
    return nullptr;
}
uint32_t il2cpp::gc::GCHandle::New(Il2CppObject* o,bool pin) { return pin && o==&node.object?1:0; }
Il2CppObject* il2cpp::gc::GCHandle::GetTarget(uint32_t h) { return h==1?&node.object:nullptr; }
void il2cpp::gc::GCHandle::Free(uint32_t) {}
// Exact native table stub, with one negative no-Bi4 linked program.
namespace hybridclr { namespace interpreter {
#if !defined(R03_TEST_NO_LINKED_BI4)
static void FakeBi4() {}
#endif
extern const Managed2NativeFunctionPointerCallData g_managed2NativeFunctionPointerCallStub[] = {
#if defined(R03_TEST_NO_LINKED_BI4)
    {nullptr, nullptr},
#else
    {"Bi4", FakeBi4},
    {nullptr, nullptr},
#endif
};
}}
extern "C" int32_t R03_IRW_BridgeStatus();
// Stub for the real writer's preopened diagnostic, host-only.
extern "C" int32_t R03_IRW_Trace(int32_t phase,int32_t a,int32_t,int32_t,int32_t) {
    return phase>0 && a>=-9 ? 1 : -1;
}
extern "C" int32_t R03_IRW_OnPrepared();
extern "C" int32_t R03_IRW_ReadPrepared(int32_t*,int32_t*,int32_t*,int32_t*,int32_t*);
int main() {
#if defined(R03_TEST_NO_LINKED_BI4)
    assert(R03_IRW_BridgeStatus()==-2);
#else
    assert(R03_IRW_BridgeStatus()==1);
#endif
    image.assembly=&assembly;assembly.image=&image;
    nodeClass.image=&image;nodeClass.instance_size=sizeof(Node);
    witnessClass.image=&image;witnessClass.static_fields=&values;
    witnessClass.static_fields_size=sizeof(Witness);
    node.object.klass=&nodeClass;node.stable=3;
    values.instance=&node.object;values.preField=3;values.ready=1;
    values.direct=42;values.delegated=42;values.generic=42;
    fields[0]={"stable",&integer,&nodeClass,static_cast<int32_t>(offsetof(Node,stable))};
    fields[1]={"Instance",&staticReference,&witnessClass,static_cast<int32_t>(offsetof(Witness,instance))};
    fields[2]={"PreField",&staticInteger,&witnessClass,static_cast<int32_t>(offsetof(Witness,preField))};
    fields[3]={"Ready",&staticInteger,&witnessClass,static_cast<int32_t>(offsetof(Witness,ready))};
    fields[4]={"PreDirectReturn",&staticInteger,&witnessClass,static_cast<int32_t>(offsetof(Witness,direct))};
    fields[5]={"PreDelegateReturn",&staticInteger,&witnessClass,static_cast<int32_t>(offsetof(Witness,delegated))};
    fields[6]={"PreGenericReturn",&staticInteger,&witnessClass,static_cast<int32_t>(offsetof(Witness,generic))};
    assert(R03_IRW_OnPrepared()==1);
    state=il2cpp::vm::AssemblyShadowState::FailedAfterCommit;
    int32_t after=-1,before=-1,ready=-1,mask=-1,calls=-1;
    assert(R03_IRW_ReadPrepared(&after,&before,&ready,&mask,&calls)==1);
    assert(after==3 && before==3 && ready==1 && mask==15 && calls==1);
    node.stable=4;
    assert(R03_IRW_ReadPrepared(&after,&before,&ready,&mask,&calls)==1 && after==4);
    assert(R03_IRW_OnPrepared()!=1);
    assert(R03_IRW_ReadPrepared(&after,&before,&ready,&mask,&calls)==1 && calls==2);
    puts("C++11 HOST OBSERVER PASSED; REAL UNITY NOT EXECUTED");
}
"""


class ObserverHostTests(unittest.TestCase):
    def test_actual_committed_source_under_clang_and_gcc(self):
        self.assertTrue(SOURCE.is_file())
        source_bytes = SOURCE.read_bytes()
        self.assertIn(b'R03_IRW_OnPrepared', source_bytes)
        self.assertIn(b'AssemblyShadowState::Committing', source_bytes)
        with tempfile.TemporaryDirectory(prefix='r03-host-observer-') as temp:
            root = Path(temp)
            for name, body in HEADERS.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(body, encoding='utf-8')
            driver = root / 'driver.cpp'
            driver.write_text(DRIVER, encoding='utf-8')
            compilers = [cc for cc in ('clang++', 'g++') if shutil.which(cc)]
            self.assertTrue(compilers, 'C++ compiler required')
            for compiler in compilers:
                for negative in (False, True):
                    with self.subTest(compiler=compiler, negative=negative):
                        app = root / (compiler.replace('+','p') + ('-noBi4' if negative else '-Bi4'))
                        args = [compiler, '-std=c++11','-Wall','-Wextra','-Werror',
                                '-I',str(root)]
                        if negative: args.append('-DR03_TEST_NO_LINKED_BI4=1')
                        subprocess.run(args + [str(SOURCE),str(driver),'-o',str(app)],
                                       capture_output=True, text=True, check=True, timeout=80)
                        done=subprocess.run([str(app)],capture_output=True,text=True,timeout=20)
                        self.assertEqual(done.returncode,0,done.stderr)
                        self.assertIn('HOST OBSERVER PASSED',done.stdout)
            self.assertEqual(hashlib.sha256(source_bytes).hexdigest(),
                             hashlib.sha256(SOURCE.read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main(verbosity=2)
