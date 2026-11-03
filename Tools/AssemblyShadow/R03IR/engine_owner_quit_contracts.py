#!/usr/bin/env python3
"""C++11 source-bound owner-exit and feature-OFF contracts for the R03 probe.

Compiles the ENTIRE genuine native translation unit with narrow fake SDK
headers: the mock does not prove Unity/IL2CPP ABI, Player exit, or shutdown.
Unlike the previous extracted-callback fixture, no other mock header may
provide complete Il2CppException/Il2CppString types in feature-OFF mode.
Positive mock atexit and negative watchdog runs are separate processes.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SOURCE_PATH = "libil2cpp/vm/AssemblyShadowEngineReportingProbe.cpp"
HEADER_PATH = "libil2cpp/vm/AssemblyShadowTerminalReporting.h"

SDK_HEADERS = {
    "il2cpp-config.h": r"""
#pragma once
#define IL2CPP_EXPORT
struct Il2CppException;
struct Il2CppString;
""",
    "il2cpp-object-internals.h": r"""
#pragma once
#include <cstdint>
// Sole provider of the complete layout in this SDK-like fixture. This is not
// a replacement for the actual Unity SDK header in Local Validation.
struct Il2CppString { int32_t length; uint16_t chars[128]; };
struct Il2CppException { Il2CppString* message; };
""",
    "vm/AssemblyShadow.h": r"""
#pragma once
#include <atomic>
#include <cstdint>
#include <string>
namespace il2cpp { namespace vm {
enum class AssemblyShadowState : int32_t { Committed = 6, FailedAfterCommit = 9 };
enum class AssemblyShadowError : int32_t { Success = 0 };
inline std::atomic<int>& MockState() { static std::atomic<int> value{6}; return value; }
struct AssemblyShadow {
    static AssemblyShadowError GetState(AssemblyShadowState& out) {
        out = static_cast<AssemblyShadowState>(MockState().load());
        return AssemblyShadowError::Success;
    }
    static AssemblyShadowError GetRecoveryInfoJson(std::string& out) {
        out = "{\"published\":true,\"stateCode\":9,\"terminalFailureCode\":13,"
              "\"disposition\":\"RestartRequired\"}";
        return AssemblyShadowError::Success;
    }
};
}}
""",
    "vm/AssemblyShadowTerminalReporting.h": r"""
#pragma once
#include <atomic>
#include <cstdint>
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
namespace il2cpp { namespace vm { namespace assembly_shadow_reporting {
inline std::atomic<uint64_t>& CompletedCounter() {
    static std::atomic<uint64_t> count{0};
    return count;
}
}}}
#endif // HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
""",
    "vm/InternalCalls.h": r"""
#pragma once
#include <cstdint>
extern "C" void R03MockUnityQuit(int32_t);
namespace il2cpp { namespace vm {
struct InternalCalls {
    static void* Resolve(const char*) {
        return reinterpret_cast<void*>(&R03MockUnityQuit);
    }
};
}}
""",
}

HARNESS = r"""
#include "il2cpp-config.h"
#include "il2cpp-object-internals.h"
#include "vm/AssemblyShadow.h"
#include "vm/AssemblyShadowTerminalReporting.h"
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <thread>

extern "C" int32_t R03_IR_ArmEngineWitness(
    const char*, const char*, const char*, const char*);
extern "C" void R03_IR_EngineLoggerCalled();
extern "C" void R03_IR_OnNativeEngineReportCompleted(const Il2CppException*);

static bool s_naturalQuit = false;
extern "C" void R03MockUnityQuit(int32_t code)
{
    if (code != 0) std::_Exit(80);
    if (s_naturalQuit) std::exit(0); // C runtime atexit, not watchdog.
}

int main(int argc, char** argv)
{
    if (argc != 3) return 81;
    s_naturalQuit = std::strcmp(argv[1], "normal") == 0;
    const char* run = "0123456789abcdef0123456789abcdef";
    const char* sentinel =
        "R03_ENGINE_UNHANDLED_0123456789abcdef0123456789abcdef";
    const char* sha =
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    R03_IR_EngineLoggerCalled();
    if (R03_IR_ArmEngineWitness(argv[2], run,
            "IR-R03-02-release-engine", sha) != 1) return 82;
    Il2CppString message{};
    message.length = static_cast<int32_t>(std::strlen(sentinel));
    for (int32_t i = 0; i < message.length; ++i)
        message.chars[i] = static_cast<unsigned char>(sentinel[i]);
    Il2CppException exception{&message};
    il2cpp::vm::MockState().store(9);
    il2cpp::vm::assembly_shadow_reporting::CompletedCounter().fetch_add(1);
    R03_IR_OnNativeEngineReportCompleted(&exception);
    // Wrong subsequent message must not cause another native owner request.
    message.chars[0] += 1;
    R03_IR_OnNativeEngineReportCompleted(&exception);
    if (s_naturalQuit) return 83; // Quit must have used atexit directly.
    std::this_thread::sleep_for(std::chrono::seconds(2));
    return 84; // Watchdog should have exited failure-only first.
}
"""


class OwnerQuitHostContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not hasattr(cls, "native"):
            raise AssertionError("Explicit native checkout is required")
        cls.native_source = cls.native / SOURCE_PATH
        cls.terminal_header = cls.native / HEADER_PATH
        cls.source = cls.native_source.read_text(encoding="utf-8")
        cls.header = cls.terminal_header.read_text(encoding="utf-8")
        cls.compiler = shutil.which(os.environ.get("CXX", "clang++")) or shutil.which("g++")
        if not cls.compiler:
            raise AssertionError("Actual C++11 host compiler required")
        for token in (
            '#include "il2cpp-object-internals.h"',
            'std::atexit(NormalExitReport)', 'WriteReport(false)',
            'std::_Exit(71)', 's_ownerQuit(0);',
            '"UnityEngine.Application::Quit(System.Int32)"',
            's_ownerQuitRequested.exchange(true',
            's_ownerQuitReturned.store(true',
            'normalExitHookObserved',
            's_firstSentinelNs.store(NowNs()',
        ):
            if token not in cls.source:
                raise AssertionError("Required real native owner source missing: " + token)
        active = "\n".join(line.split("//", 1)[0] for line in cls.source.splitlines())
        if "std::_Exit(0)" in active or "std::_Exit(valid" in active:
            raise AssertionError("Native watchdog must never synthesize success")
        for token in ("CompletedCounter().fetch_add(1", "::R03_IR_OnNativeEngineReportCompleted("):
            if token not in cls.header:
                raise AssertionError("Real terminal counter/reporting callback lost: " + token)

    def fixture(self, root: Path):
        for path, contents in SDK_HEADERS.items():
            dest = root / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(contents, encoding="utf-8")

    def compile(self, root: Path, source: Path, *, enabled: bool,
                harness: Path | None = None) -> subprocess.CompletedProcess:
        out = root / ("on-runner" if enabled else "off.o")
        argv = [self.compiler, "-std=c++11", "-Wall", "-Wextra", "-Werror",
                "-Wno-unused-function", "-Wno-unused-variable", "-pedantic", "-pthread",
                "-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=" + ("1" if enabled else "0"),
                "-DHYBRIDCLR_R03_RUNTIME_PROBE=1", "-I", str(root),
                str(source)]
        if harness is not None:
            argv.append(str(harness))
        else:
            argv += ["-c"]
        argv += ["-o", str(out)]
        return subprocess.run(argv, capture_output=True, text=True, timeout=90)

    def test_off_translation_unit_requires_its_own_complete_type_include(self):
        with tempfile.TemporaryDirectory(prefix="r03-native-off-") as temp:
            root = Path(temp)
            self.fixture(root)
            passed = self.compile(root, self.native_source, enabled=False)
            self.assertEqual(passed.returncode, 0, passed.stderr)
            # A source copy without this include must reproduce the precise
            # incomplete-type class of failure that actual oneuse-G exposed.
            old = self.source
            replaced = old.replace('#include "il2cpp-object-internals.h"', "", 1)
            self.assertNotEqual(old, replaced)
            changed = root / "removed-object-layout-include.cpp"
            changed.write_text(replaced, encoding="utf-8")
            failed = self.compile(root, changed, enabled=False)
            self.assertNotEqual(failed.returncode, 0, "OFF regression sensitivity lost")
            self.assertTrue("incomplete" in failed.stderr or "undefined" in failed.stderr,
                            failed.stderr)

    def test_normal_exit_is_not_watchdog_synthetic_success(self):
        with tempfile.TemporaryDirectory(prefix="r03-native-normal-") as temp:
            root = Path(temp)
            self.fixture(root)
            harness = root / "main.cpp"
            harness.write_text(HARNESS, encoding="utf-8")
            compiled = self.compile(root, self.native_source, enabled=True, harness=harness)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            raw = root / "normal.json"
            run = subprocess.run([str(root / "on-runner"), "normal", str(raw)],
                                 capture_output=True, text=True, timeout=30)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("[R03EngineOwnerQuit]", run.stderr)
            self.assertIn("[R03EngineOwnerExit] nativeAtexit=true rawFlushed=true", run.stderr)
            receipt = json.loads(raw.read_text(encoding="utf-8"))
            self.assertEqual(receipt["schemaVersion"], 2)
            self.assertEqual(receipt["kind"], "R03IREngineReportingV2")
            self.assertEqual(receipt["witnessExitMode"], "NativeAtexit")
            self.assertTrue(receipt["normalExitHookObserved"])
            self.assertFalse(receipt["timedOut"])
            self.assertEqual(receipt["completedReports"], 1)
            self.assertEqual(receipt["ownerQuitNativeCalls"], 1)
            self.assertLessEqual(receipt["observationElapsedMilliseconds"], 500)
            self.assertEqual(receipt["finalState"], 9)
            self.assertEqual(receipt["recovery"]["terminalFailureCode"], 13)

    def test_watchdog_can_only_emit_failure_and_preserves_raw(self):
        with tempfile.TemporaryDirectory(prefix="r03-native-watchdog-") as temp:
            root = Path(temp)
            self.fixture(root)
            harness = root / "main.cpp"
            harness.write_text(HARNESS, encoding="utf-8")
            compiled = self.compile(root, self.native_source, enabled=True, harness=harness)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            raw = root / "watchdog.json"
            run = subprocess.run([str(root / "on-runner"), "watchdog", str(raw)],
                                 capture_output=True, text=True, timeout=30)
            self.assertEqual(run.returncode, 71, run.stderr)
            receipt = json.loads(raw.read_text(encoding="utf-8"))
            self.assertFalse(receipt["normalExitHookObserved"])
            self.assertEqual(receipt["witnessExitMode"], "WatchdogForcedExit")
            self.assertTrue(receipt["timedOut"])
            self.assertEqual(receipt["completedReports"], 1)
            self.assertEqual(receipt["ownerQuitNativeCalls"], 1)
            self.assertNotIn("[R03EngineOwnerExit]", run.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", required=True, type=Path)
    options = parser.parse_args()
    OwnerQuitHostContracts.native = options.native.resolve(strict=True)
    unittest.main(argv=[__file__], verbosity=2)
