#!/usr/bin/env python3
"""Compile actual B1 Player probe with a VM-shaped host stub, not a real VM.

Catches C++11 probe ABI/source regressions and validates emitted JSON. Only a
real Unity IL2CPP Player and original V1/physical source receipts can establish
that the VM itself published error19/15.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "PlayerProject/R03FirstErrorB1Probe.cpp"

STUB = r'''
#pragma once
#include <cstdint>
#include "AssemblyShadowFirstFailureV2.h"
namespace il2cpp { namespace vm {
struct AssemblyShadow {
    static assembly_shadow_first_failure_v2::FirstErrorV2 record;
    static assembly_shadow_first_failure_v2::State FirstFailureV2Status() noexcept;
    static bool TryReadFirstFailureV2(
        assembly_shadow_first_failure_v2::Snapshot&) noexcept;
};
}}
'''
# Source-shaped header is test-only and intentionally not the shipping VM header.
# Verify the real header contract text via source gating in the native repository.
HEADER = r'''
#pragma once
#include <atomic>
#include <cstdint>
#include <cstddef>
#include <cstring>
namespace il2cpp { namespace vm { namespace assembly_shadow_first_failure_v2 {
static const std::size_t kReasonLimit=4096;
enum class State : unsigned char { Empty=0, Writing=1, Frozen=2, Invalid=3 };
enum class Origin : unsigned char {
    Guard=1, InterpreterInitializer=2, LateBaselineUse=3,
    ReferenceViolation=4, UnexpectedFailure=5, TransactionTerminal=6
};
struct Snapshot {
    int32_t code=0; Origin origin=Origin::Guard; size_t length=0;
    char reason[4097]={};
};
class FirstErrorV2 {
    State state_=State::Empty;
    Snapshot value_{};
public:
    State status() const noexcept { return state_; }
    bool TryFreeze(int32_t code, Origin origin, const char* p,size_t n) noexcept {
        if(state_!=State::Empty||!p||!n||n>4096)return false;
        value_.code=code;value_.origin=origin;value_.length=n;
        memcpy(value_.reason,p,n);state_=State::Frozen;return true;
    }
    bool Read(Snapshot& s) const noexcept {
        if(state_!=State::Frozen)return false;s=value_;return true;
    }
};
}}}
'''
DRIVER = r'''
#include "il2cpp-config.h"
#include "vm/AssemblyShadow.h"
#include <cassert>
#include <cstdint>
#include <cstring>
#include <string>
using namespace il2cpp::vm;
using namespace assembly_shadow_first_failure_v2;
FirstErrorV2 AssemblyShadow::record;
State AssemblyShadow::FirstFailureV2Status() noexcept { return record.status(); }
bool AssemblyShadow::TryReadFirstFailureV2(Snapshot& out) noexcept {
    return record.Read(out);
}
extern "C" int32_t R03_IRB1_Open(const char*,const char*,const char*,const char*);
extern "C" int32_t R03_IRB1_Seal(int32_t,int32_t);
int main(int argc,char** argv) {
    assert(argc==3);
    const std::string mode=argv[1];
    const char* run="cafe123456789012345678901234abcd";
    const char* caseId=mode=="captured-generic"
        ?"IR-R03-02-captured-generic":("IR-R03-02-"+mode).c_str();
    // This is test-only, but caseId must be stable during the call.
    const std::string caseOwned = "IR-R03-02-" + mode;
    const char* caseId=caseOwned.c_str();
    const char* fixture="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    if(mode=="preexisting") {
        assert(R03_IRB1_Open(argv[2],run,caseId,fixture)!=1);
        return 0;
    }
    assert(R03_IRB1_Open(argv[2],run,caseId,fixture)==1);
    assert(R03_IRB1_Open(argv[2],run,caseId,fixture)!=1);
    int code=0,origin=0;
    if(mode=="initializer-failure") {
        const char* reason="Methods: The type initializer for '<Module>' threw an exception. ---> R03IR.InitializerFailure.AfterPublication.V1";
        code=19;origin=2;
        assert(AssemblyShadow::record.TryFreeze(code,Origin::InterpreterInitializer,reason,strlen(reason)));
    } else if(mode=="captured-generic") {
        const char* reason="ShadowCapturedBaselineType Assembly=Assembly-CSharp CapturedArgumentAssembly=Methods Context=method_inst TypePath=/arg[0]";
        code=15;origin=1;
        assert(AssemblyShadow::record.TryFreeze(code,Origin::Guard,reason,strlen(reason)));
    }
    assert(R03_IRB1_Seal(code,origin)==1);
    assert(R03_IRB1_Seal(code,origin)!=1);
    return 0;
}
'''
# Avoid dangling pointer to a temporary string in host driver code.
DRIVER = DRIVER.replace(
    '    const char* caseId=mode=="captured-generic"\n'
    '        ?"IR-R03-02-captured-generic":("IR-R03-02-"+mode).c_str();\n'
    '    // This is test-only, but caseId must be stable during the call.\n',
    '')

class B1NativeSourceHostTests(unittest.TestCase):
    def test_01_real_b1_probe_compiles_and_emits_standalone_receipts(self):
        self.assertTrue(SOURCE.is_file())
        raw=SOURCE.read_text(encoding="utf-8")
        for required in ("R03_IRB1_Open(", "R03_IRB1_Seal(",
                         "AssemblyShadow::TryReadFirstFailureV2(snap)",
                         "O_CREAT|O_EXCL|O_NOFOLLOW", "fsync(fd)==0",
                         '"nativeV2TransportImplemented"'):
            # JSON source literals contain escaped double quotes.
            if required.startswith('"'):
                self.assertIn("nativeV2TransportImplemented",raw)
            else:
                self.assertIn(required,raw)
        compilers=[c for c in ("clang++","g++") if shutil.which(c)]
        self.assertTrue(compilers,"POSIX native compiler required for B1 host")
        with tempfile.TemporaryDirectory(prefix="r03-b1-native-") as d:
            root=Path(d).resolve()
            (root/"vm").mkdir()
            (root/"il2cpp-config.h").write_text(
                "#pragma once\n#define HYBRIDCLR_R03_RUNTIME_PROBE 1\n"
                "#define HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW 1\n#define IL2CPP_EXPORT\n")
            (root/"vm/AssemblyShadow.h").write_text(STUB)
            (root/"AssemblyShadowFirstFailureV2.h").write_text(HEADER)
            src=root/"driver.cpp";src.write_text(DRIVER)
            for compiler in compilers:
                out=root/("test-"+compiler.replace("+","p"))
                cc=subprocess.run([compiler,"-std=c++11","-Wall","-Wextra",
                    "-Werror","-pthread","-I",str(root),str(SOURCE),
                    str(src),"-o",str(out)],capture_output=True,text=True,timeout=120)
                self.assertEqual(cc.returncode,0,cc.stderr)
                for mode in ("initializer-control","initializer-failure",
                             "captured-generic"):
                    target=root/(compiler.replace("+","p")+mode+".json")
                    p=subprocess.run([str(out),mode,str(target)],
                                     capture_output=True,text=True,timeout=20)
                    self.assertEqual(p.returncode,0,p.stderr)
                    self.assertTrue(target.is_file())
                    text=target.read_text()
                    self.assertIn('"nativeV2TransportImplemented":false',text)
                    self.assertIn('"matchExpected":true',text)
                old=root/(compiler.replace("+","p")+".exists")
                old.write_text("ORIGINAL")
                p=subprocess.run([str(out),"preexisting",str(old)],
                                 capture_output=True,text=True,timeout=20)
                self.assertEqual(p.returncode,0,p.stderr)
                self.assertEqual(old.read_text(),"ORIGINAL")

if __name__ == "__main__":
    unittest.main(verbosity=2)
