"""Compile the actual N field/guard bridge with explicit mocked VM/GC dependencies.

This is host evidence only. It does not establish real Unity GCHandle layout,
runtime reflection semantics, a linked Player or any R03 acceptance result.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = ROOT / "R03/PlayerProject/AssemblyShadowR03Probe.cpp"
CS = ROOT / "R03IR/PlayerProject/R03TerminalPlayer.cs"

STUB = r"""
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <iostream>
#define IL2CPP_EXPORT
#define HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW 1
#define HYBRIDCLR_R03_RUNTIME_PROBE 1
#define FIELD_ATTRIBUTE_STATIC 0x10
#define IL2CPP_TYPE_I4 8
struct Il2CppAssemblyName { const char* name; };
struct Il2CppAssembly { Il2CppAssemblyName aname; };
struct Il2CppImage { Il2CppAssembly* assembly; };
struct Il2CppClass { Il2CppImage* image; const char* namespaze; const char* name; uint32_t instance_size; };
struct Il2CppObject { Il2CppClass* klass; };
struct Il2CppType { int type; unsigned attrs; };
struct FieldInfo { Il2CppClass* parent; const char* name; Il2CppType* type; uint32_t offset; };
struct Instance { Il2CppObject header; int32_t stable; };
Il2CppAssembly assembly{{"Methods"}};
Il2CppImage image{&assembly};
Il2CppClass klass{&image,"R03","Node",sizeof(Instance)};
Il2CppType fieldType{IL2CPP_TYPE_I4,0};
FieldInfo field{&klass,"stable",&fieldType,offsetof(Instance,stable)};
Instance obj{{&klass},2};
bool ownerAllowed=true, gcCalledTerminal=false;
int pinCreates=0, targetLookupsTerminal=0, pinsFreed=0;
int32_t current=6, guardWrites=0;
std::string nativeGuard;
namespace il2cpp { namespace gc {
struct GCHandle {
 static Il2CppObject* GetTarget(uint32_t h) {
   if(current==9) { gcCalledTerminal=true; ++targetLookupsTerminal; }
   return h==7 || h==19 ? &obj.header : nullptr;
 }
 static uint32_t New(Il2CppObject* p,bool pinned) {
   assert(current==6 && pinned && p==&obj.header);++pinCreates;return 19;
 }
 static void Free(uint32_t h) {assert(h==19);++pinsFreed;}
};
} namespace vm {
enum class AssemblyShadowState { Disabled=0, Committed=6, FailedAfterCommit=9 };
enum class AssemblyShadowError { Success=0 };
struct AssemblyShadow {
 static AssemblyShadowError GetState(AssemblyShadowState& s) {
   s=static_cast<AssemblyShadowState>(current);return AssemblyShadowError::Success;
 }
 static bool IsActiveShadow(Il2CppAssembly* p) {return p==&assembly && ownerAllowed;}
};
struct Class {
 static FieldInfo* GetFieldFromName(Il2CppClass* c,const char* n) {
   assert(current==6);return c==&klass && !std::strcmp(n,"stable")?&field:nullptr;
 }
};
}}
int32_t R03_ObserveMethod(const char*,const char*,const char*,const char*,int32_t mode,char* out,int32_t size) {
 assert(mode==3);
 const char* ok="{\"available\":true,\"activeGuard\":1,\"baselineGuard\":0,\"caughtOldGuard\":1,\"stateCode\":9}";
 const char* bad="{\"available\":true,\"activeGuard\":1,\"baselineGuard\":0,\"caughtOldGuard\":0,\"stateCode\":9}";
 const char* value=ownerAllowed?ok:bad;
 int n=static_cast<int>(std::strlen(value));assert(n+1<size);
 std::memcpy(out,value,n+1);current=9;return n;
}
int R03_IR_ReportText(int index,const char* text) {
 if(index!=8||++guardWrites!=1)return -1;
 nativeGuard=text?text:"";return 1;
}
"""

TEST = r"""
int main(int argc,char**argv) {
 assert(argc==2);
 std::string mode=argv[1];
 if(mode=="bad-type"){klass.name="Other";assert(R03_IR_BindActiveField(reinterpret_cast<void*>(7))==-5);return 0;}
 if(mode=="bad-assembly"){assembly.aname.name="Other";assert(R03_IR_BindActiveField(reinterpret_cast<void*>(7))==-5);return 0;}
 if(mode=="static"){fieldType.attrs=FIELD_ATTRIBUTE_STATIC;assert(R03_IR_BindActiveField(reinterpret_cast<void*>(7))==-6);return 0;}
 if(mode=="offset"){field.offset=0;assert(R03_IR_BindActiveField(reinterpret_cast<void*>(7))==-6);return 0;}
 if(mode=="missing-root"){assert(R03_IR_BindActiveField(reinterpret_cast<void*>(888))==-4);return 0;}
 if(mode=="after-poison"){current=9;assert(R03_IR_BindActiveField(reinterpret_cast<void*>(7))==-2);return 0;}
 assert(R03_IR_BindActiveField(reinterpret_cast<void*>(7))==1);
 assert(R03_IR_BindActiveField(reinterpret_cast<void*>(7))==-1);
 assert(pinCreates==1 && !gcCalledTerminal);
 int32_t result=0;
 assert(R03_IR_ReadActiveField(&result)==-2);
 if(mode=="bad-json")ownerAllowed=false;
 int status=R03_IR_ObserveOldGuardIntoSnapshot();
 if(mode=="bad-json"){assert(status==-2 && guardWrites==0);return 0;}
 assert(status==1 && guardWrites==1 && nativeGuard.find("\"caughtOldGuard\":1")!=std::string::npos);
 assert(R03_IR_ObserveOldGuardIntoSnapshot()==-3);
 assert(R03_IR_ReadActiveField(&result)==1 && result==2);
 if(mode=="mutate"){obj.stable=3;result=0;assert(R03_IR_ReadActiveField(&result)==1 && result==3);}
 assert(targetLookupsTerminal==0 && !gcCalledTerminal && pinCreates==1 && pinsFreed==0);
 std::cout<<"{\"result\":\"Passed\"}"<<std::endl;
}
"""

class GuardedReceipts(unittest.TestCase):
    def test_actual_native_receipt_and_field_helpers(self):
        source = CPP.read_text()
        fragment = source[source.index("// N: test-only native guard receipt"):]
        fragment = "\n".join(s for s in fragment.splitlines() if not s.startswith('#include "'))
        cc = shutil.which("clang++") or shutil.which("g++")
        self.assertIsNotNone(cc, "C++17 compiler required")
        flags = ["-std=c++17", "-Wall", "-Wextra", "-Werror", "-pedantic"]
        if os.getenv("R03_SANITIZERS") == "1":
            flags += ["-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve(strict=True)
            src, exe = root/"n.cpp", root/"n"
            src.write_text(STUB + fragment + TEST)
            compiled = subprocess.run([cc, *flags, str(src), "-o", str(exe)],
                                      capture_output=True, text=True, timeout=50)
            self.assertEqual(compiled.returncode, 0, compiled.stderr[-7000:])
            for mode in ("success", "mutate", "bad-json", "bad-type", "bad-assembly",
                         "static", "offset", "missing-root", "after-poison"):
                run = subprocess.run([str(exe), mode], capture_output=True,
                                     text=True, timeout=20)
                self.assertEqual(run.returncode, 0, (mode, run.stderr[-2000:]))
                if mode in ("success", "mutate"):
                    self.assertEqual(json.loads(run.stdout)["result"], "Passed")

    def test_csharp_handoffs_and_unchanged_semantic_verifier(self):
        source = CS.read_text()
        self.assertIn("R03_IR_BindActiveField(GCHandle.ToIntPtr(fieldHandle))", source)
        self.assertIn("R03_IR_ObserveOldGuardIntoSnapshot()", source)
        self.assertIn("R03_IR_ReadActiveField(out afterField)", source)
        self.assertIn("fieldHandle.Free();", source)
        self.assertIn('if (r.stimulus != "baseline-owner")', source)
        after = source[source.index("Phase(report, 170);"):]
        self.assertNotIn("Encoding.UTF8.GetString(buffer", after)
        self.assertNotIn("stableField.GetValue(instance)", after)
        self.assertNotIn("GuardFlag(", after)
        self.assertIn("report.finalShadowField == report.preShadowField", after)
        host = (ROOT/"R03IR/run_terminal_local.py").read_text()
        self.assertIn("native = loads(raw['nativeGuardJson'])", host)
        self.assertIn("raw.get('shadowFieldReadable') is True", host)
        self.assertIn("exact_int(raw.get('finalShadowField'), 2)", host)

if __name__ == "__main__":
    unittest.main()
