#!/usr/bin/env python3
"""Test the REAL native Unity quit matcher and dispatch under C++11.

Extracts source functions from the pinned libil2cpp header and compiles them
against strict minimal MethodInfo/assembly/owner-state mocks. This tests exact
AOT identity, signatures, active terminal owner token and negative cases.
It does not execute Unity or authorize full shutdown/runtime acceptance.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

HEADER = "libil2cpp/vm/AssemblyShadowTerminalReporting.h"
RUNTIME = "libil2cpp/vm/Runtime.cpp"
ENGINE = "libil2cpp/vm/AssemblyShadowEngineReportingProbe.cpp"

MOCK = r'''
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>

#define IL2CPP_TYPE_BOOLEAN 2
#define IL2CPP_TYPE_VOID 1
#define METHOD_ATTRIBUTE_STATIC 0x0010

struct Il2CppImage;
struct Il2CppAssembly { Il2CppImage* image; };
struct Il2CppImage { Il2CppAssembly* assembly; };
struct Il2CppClass {
    const char* name;
    const char* namespaze;
    Il2CppImage* image;
    void* generic_class;
};
struct Il2CppType { uint8_t type; bool byref; bool valuetype; };
struct MethodInfo {
    const char* name;
    Il2CppClass* klass;
    const Il2CppType* return_type;
    uint16_t flags;
    uint8_t parameters_count;
    bool is_inflated;
    bool is_generic;
};
struct Il2CppObject { int marker; };
static Il2CppImage g_image{};
static Il2CppAssembly g_physical{&g_image};
static bool g_candidate = false;
static bool g_shadowed = false;
static bool g_activeShadow = false;
static bool g_ownerPending = false;
static int g_state = 9;
static int g_approve = 0;
static int g_notify = 0;
static Il2CppObject g_pinnedTrue{1};

extern "C" int32_t R03_IR_NativeOwnerDecisionPending() noexcept
{ return g_ownerPending ? 1 : 0; }
extern "C" void R03_IR_NativeOwnerDecisionObserved(int32_t kind) noexcept
{ if (kind == 1) ++g_approve; else if (kind == 2) ++g_notify; }

namespace il2cpp { namespace vm {
enum class AssemblyShadowError : int32_t { Success = 0 };
enum class AssemblyShadowState : int32_t { Committed = 6, FailedAfterCommit = 9 };
struct MetadataCache {
    static const Il2CppAssembly* GetAotAssemblyByNamePhysical(const char* name)
    {
        return name && !std::strcmp(name, "UnityEngine.CoreModule") ? &g_physical : nullptr;
    }
};
struct AssemblyShadow {
    static bool IsCandidate(const Il2CppAssembly*) { return g_candidate; }
    static bool IsShadowedBaseline(const Il2CppAssembly*) { return g_shadowed; }
    static bool IsActiveShadow(const Il2CppAssembly*) { return g_activeShadow; }
    static AssemblyShadowError GetState(AssemblyShadowState& state) {
        state = static_cast<AssemblyShadowState>(g_state);
        return AssemblyShadowError::Success;
    }
};
namespace assembly_shadow_reporting {
inline Il2CppObject* FixedHandledResult() noexcept { return &g_pinnedTrue; }
'''

TESTS = r'''
}}} // il2cpp::vm::assembly_shadow_reporting
#define REQUIRE(x) do { if (!(x)) { \
    std::fprintf(stderr, "assertion:%d: %s\n", __LINE__, #x); return __LINE__ % 200 + 1; \
} } while (0)

int main()
{
    g_image.assembly = &g_physical;
    Il2CppType booleanType{IL2CPP_TYPE_BOOLEAN, false, true};
    Il2CppType voidType{IL2CPP_TYPE_VOID, false, false};
    Il2CppClass owner{"Application", "UnityEngine", &g_image, nullptr};
    MethodInfo wants{"Internal_ApplicationWantsToQuit", &owner, &booleanType,
                     METHOD_ATTRIBUTE_STATIC, 0, false, false};
    MethodInfo quit{"Internal_ApplicationQuit", &owner, &voidType,
                    METHOD_ATTRIBUTE_STATIC, 0, false, false};
    using namespace il2cpp::vm::assembly_shadow_reporting;
    Il2CppObject* result = nullptr;
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 1);
    REQUIRE(ClassifyNativeOwnerDecision(&quit, nullptr) == 2);
    REQUIRE(!TryHandleNativeOwnerDecision(&wants, nullptr, result));
    REQUIRE(g_approve == 0 && g_notify == 0);
    g_ownerPending = true;
    g_state = 6;
    REQUIRE(!TryHandleNativeOwnerDecision(&wants, nullptr, result));
    g_state = 9;
    REQUIRE(TryHandleNativeOwnerDecision(&wants, nullptr, result));
    REQUIRE(result == &g_pinnedTrue && g_approve == 1 && g_notify == 0);
    result = &g_pinnedTrue;
    REQUIRE(TryHandleNativeOwnerDecision(&quit, nullptr, result));
    REQUIRE(result == nullptr && g_approve == 1 && g_notify == 1);
    g_ownerPending = false;
    REQUIRE(!TryHandleNativeOwnerDecision(&quit, nullptr, result));
    g_ownerPending = true;
    Il2CppObject fake{};
    REQUIRE(!TryHandleNativeOwnerDecision(&wants, &fake, result));
    const int beforeApproval = g_approve, beforeNotification = g_notify;
    wants.name = "Internal_ApplicationQuit";
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 0); // wrong bool signature
    wants.name = "Internal_ApplicationWantsToQuit";
    wants.return_type = &voidType;
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 0);
    wants.return_type = &booleanType;
    wants.flags = 0;
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 0);
    wants.flags = METHOD_ATTRIBUTE_STATIC;
    wants.parameters_count = 1;
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 0);
    wants.parameters_count = 0;
    wants.is_inflated = true;
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 0);
    wants.is_inflated = false;
    wants.is_generic = true;
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 0);
    wants.is_generic = false;
    owner.generic_class = &owner;
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 0);
    owner.generic_class = nullptr;
    owner.name = "Debug";
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 0);
    owner.name = "Application";
    owner.namespaze = "WrongNamespace";
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 0);
    owner.namespaze = "UnityEngine";
    Il2CppImage other{};
    owner.image = &other;
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 0);
    owner.image = &g_image;
    g_candidate = true;
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 0);
    g_candidate = false;
    g_shadowed = true;
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 0);
    g_shadowed = false;
    g_activeShadow = true;
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 0);
    g_activeShadow = false;
    booleanType.byref = true;
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 0);
    booleanType.byref = false;
    booleanType.valuetype = false;
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 0);
    booleanType.valuetype = true;
    wants.name = "InvokeOnBeforeRender";
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 0);
    wants.name = "Internal_ApplicationWantsToQuit";
    quit.name = "Internal_ApplicationUnload";
    REQUIRE(ClassifyNativeOwnerDecision(&quit, nullptr) == 0);
    REQUIRE(g_approve == beforeApproval && g_notify == beforeNotification);
    REQUIRE(ClassifyNativeOwnerDecision(&wants, nullptr) == 1);
    REQUIRE(ClassifyNativeOwnerDecision(&quit, nullptr) == 0);
    return 0;
}
'''


def extract(header: str) -> str:
    start = header.index("inline int32_t ClassifyNativeOwnerDecision(")
    end = header.index("#endif // HYBRIDCLR_R03_RUNTIME_PROBE", start)
    piece = header[start:end]
    for token in ("GetAotAssemblyByNamePhysical", "IsShadowedBaseline",
                  "IsActiveShadow", "R03_IR_NativeOwnerDecisionPending() != 1",
                  "AssemblyShadowState::FailedAfterCommit", "FixedHandledResult()",
                  "R03_IR_NativeOwnerDecisionObserved(kind)"):
        if token not in piece:
            raise AssertionError("Native owner classifier/decision contract missing: " + token)
    if "Class::Init(" in piece or "invoker_method(" in piece or "Runtime::Invoke(" in piece:
        raise AssertionError("Native owner decision must not enter managed code")
    return piece


class NativeOwnerDecisionContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not hasattr(cls, "native"):
            raise AssertionError("Explicit --native path required")
        cls.header = (cls.native / HEADER).read_text(encoding="utf-8")
        cls.runtime = (cls.native / RUNTIME).read_text(encoding="utf-8")
        cls.engine = (cls.native / ENGINE).read_text(encoding="utf-8")
        cls.compiler = shutil.which(os.environ.get("CXX", "clang++")) or shutil.which("g++")
        if not cls.compiler:
            raise AssertionError("Actual C++11 compiler required")

    def test_native_dispatch_remains_before_general_guard_and_probe_only(self):
        entry = self.runtime.index("Il2CppObject* Runtime::Invoke(")
        segment = self.runtime[entry:self.runtime.index("Runtime::InvokeWithThrow(", entry)]
        self.assertIn("#if HYBRIDCLR_R03_RUNTIME_PROBE", segment)
        self.assertLess(segment.index("TryHandleNativeOwnerDecision("),
                        segment.index("TryHandle(method, obj, params, terminalReport)"))
        self.assertLess(segment.index("TryHandleNativeOwnerDecision("),
                        segment.index('RequireActiveMethod(method, "Runtime::Invoke")'))
        self.assertIn("s_ownerQuitRequested.load(", self.engine)
        self.assertIn("s_recoveryReady.load(", self.engine)
        self.assertIn("s_ownerQuitCalls.load(", self.engine)
        self.assertIn("s_reportWriter.load(", self.engine)
        self.assertIn("return 0;", self.engine)
        self.assertIn("s_ownerWantsToQuitNativeResponses.fetch_add(1", self.engine)
        self.assertIn("s_ownerApplicationQuitNativeNotifications.fetch_add(1", self.engine)
        self.assertNotIn("std::_Exit(0);", "\n".join(
            line.split("//", 1)[0] for line in self.engine.splitlines()))

    def test_actual_classifier_cxx11_negative_matrix(self):
        with tempfile.TemporaryDirectory(prefix="r03-owner-policy-") as temporary:
            root = Path(temporary)
            src = root / "native-owner.cpp"
            exe = root / "native-owner"
            src.write_text(MOCK + extract(self.header) + TESTS, encoding="utf-8")
            proc = subprocess.run(
                [self.compiler, "-std=c++11", "-Wall", "-Wextra", "-Werror",
                 "-pedantic", str(src), "-o", str(exe)],
                capture_output=True, text=True, timeout=90)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = subprocess.run([str(exe)], capture_output=True, text=True, timeout=30)
            self.assertEqual(out.returncode, 0, out.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", required=True, type=Path)
    options = parser.parse_args()
    NativeOwnerDecisionContracts.native = options.native.resolve(strict=True)
    unittest.main(argv=[__file__], verbosity=2)
