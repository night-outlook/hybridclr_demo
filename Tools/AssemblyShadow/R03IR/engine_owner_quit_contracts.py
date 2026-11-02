#!/usr/bin/env python3
"""Compile the genuine test-only terminal owner-quit callback under C++11.

Mocks native Unity icall and Il2CppException memory only; this neither
executes Unity nor proves an actual graceful shutdown. Does not change
terminal business guards, real completed report counters, or time bounds.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

SOURCE_PATH = "libil2cpp/vm/AssemblyShadowEngineReportingProbe.cpp"
HEADER_PATH = "libil2cpp/vm/AssemblyShadowTerminalReporting.h"


def extracted(native: Path) -> str:
    source = (native / SOURCE_PATH).read_text(encoding="utf-8")
    header = (native / HEADER_PATH).read_text(encoding="utf-8")
    start = source.index('extern "C" IL2CPP_EXPORT void R03_IR_OnNativeEngineReportCompleted(')
    end = source.index('extern "C" IL2CPP_EXPORT void R03_IR_EngineLoggerCalled()', start)
    hook = source[start:end]
    require = (
        'InternalCalls::Resolve(', '"UnityEngine.Application::Quit(System.Int32)"',
        "s_engineWitnessArmed.exchange(true", "s_ownerQuit = reinterpret_cast<OwnerQuit>",
        "s_ownerQuit(0);",
    )
    if not all(mark in source for mark in require):
        raise AssertionError("Missing genuine healthy binding or single native owner quit")
    if ("CompletedCounter().fetch_add(1" not in header or
        "::R03_IR_OnNativeEngineReportCompleted(" not in header or
        "if (count <= 32)" not in header):
        raise AssertionError("Native completed counter/native reporter provenance changed")
    if not ("s_ownerQuitRequested.exchange(true" in hook and
            "s_expectedSentinel" in hook and
            "message->chars[index]" in hook):
        raise AssertionError("Missing exact unhandled sentinel or once-only owner request")
    return hook


CPP_HEADER = r'''
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstdlib>
struct Il2CppString { int32_t length; uint16_t chars[128]; };
struct Il2CppException { Il2CppString* message; };
using OwnerQuit = void (*)(int32_t);
OwnerQuit s_ownerQuit = nullptr;
char s_expectedSentinel[64] = {};
std::atomic<bool> s_engineWitnessArmed{false};
std::atomic<bool> s_ownerQuitRequested{false};
std::atomic<int32_t> s_ownerQuitCalls{0};
std::atomic<int32_t> realOwnerCalls{0};
void owner(int32_t code)
{
    if (code != 0) std::abort();
    realOwnerCalls.fetch_add(1);
}
#define IL2CPP_EXPORT
'''

CPP_MAIN = r'''
int main()
{
    const char* sentinel = "R03_ENGINE_UNHANDLED_0123456789abcdef0123456789abcdef";
    std::strcpy(s_expectedSentinel, sentinel);
    s_ownerQuit = &owner;
    Il2CppString message{};
    for (int i = 0; sentinel[i]; ++i)
    {
        message.chars[i] = static_cast<unsigned char>(sentinel[i]);
        ++message.length;
    }
    Il2CppException error{&message};
    R03_IR_OnNativeEngineReportCompleted(&error);
    if (s_ownerQuitCalls.load() != 0) return 1; // Unarmed never requests quit.
    s_engineWitnessArmed.store(true);
    ++message.chars[0]; // Wrong sentinel cannot quit.
    R03_IR_OnNativeEngineReportCompleted(&error);
    --message.chars[0];
    R03_IR_OnNativeEngineReportCompleted(nullptr);
    if (s_ownerQuitCalls.load() != 0) return 2;
    R03_IR_OnNativeEngineReportCompleted(&error);
    if (s_ownerQuitCalls.load() != 1 || realOwnerCalls.load() != 1) return 3;
    for (int i = 0; i < 100; ++i)
        R03_IR_OnNativeEngineReportCompleted(&error);
    return (s_ownerQuitCalls.load() == 1 && realOwnerCalls.load() == 1) ? 0 : 4;
}
'''


class OwnerQuitHostContracts(unittest.TestCase):
    def test_actual_callback_cxx11_and_exact_sentinel(self):
        with tempfile.TemporaryDirectory(prefix="r03-owner-host-") as temp:
            src = Path(temp) / "witness.cpp"
            out = Path(temp) / "witness"
            src.write_text(CPP_HEADER + extracted(self.native) + CPP_MAIN, encoding="utf-8")
            compiler = shutil.which(os.environ.get("CXX", "clang++")) or shutil.which("g++")
            self.assertIsNotNone(compiler, "actual C++11 compiler required")
            p = subprocess.run([compiler, "-std=c++11", "-Wall", "-Wextra", "-Werror",
                                "-pedantic", "-pthread", str(src), "-o", str(out)],
                               capture_output=True, text=True, timeout=90)
            self.assertEqual(p.returncode, 0, p.stderr)
            r = subprocess.run([str(out)], capture_output=True, text=True, timeout=30)
            self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", required=True, type=Path)
    args = parser.parse_args()
    OwnerQuitHostContracts.native = args.native.resolve(strict=True)
    unittest.main(argv=[__file__], verbosity=2)
