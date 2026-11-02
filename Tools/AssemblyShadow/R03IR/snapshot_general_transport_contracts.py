#!/usr/bin/env python3
"""Compile the ACTUAL R03 native report writer at C++11 and test complete bytes.

Host-only extracted implementation; never represents Unity SDK compilation,
post-terminal lifetime coherence, actual Player entry, or engine containment.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import sys

from complete_general_diagnostic import verify, TEXT_LIMIT, GENERAL_LIMIT

OVERLAY = Path(__file__).resolve().parents[1] / "R03/PlayerProject/AssemblyShadowR03Probe.cpp"


def extract_source() -> str:
    source = OVERLAY.read_text(encoding="utf-8")
    begin = source.index("namespace r03_ir_snapshot {")
    end = source.index('extern "C" IL2CPP_EXPORT void R03_IR_Exit', begin)
    result = source[begin:end]
    for symbol in ("WriteCompleteGeneral", "GeneralLimit = 3932160",
                   "TextLimit = 262144", "R03_IR_ReportSeal", "R03_IR_ReportOpen",
                   "R03_IR_ReportText"):
        assert symbol in result, "Actual native source missing: " + symbol
    return result


HEADER = """#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <limits.h>
#include <string>
#define IL2CPP_EXPORT
"""

MAIN = r'''
int main(int argc, char** argv)
{
    if (argc != 3) return 90;
    if (R03_IR_ReportOpen(argv[1]) != 1) return 91;
    std::string full = "{\"schemaVersion\":1,\"enabled\":true,"
        "\"state\":\"FailedAfterCommit\",\"stateCode\":9,\"generation\":2,"
        "\"enumerationGeneration\":2,\"classEnumerationGeneration\":2,"
        "\"startupCandidateNames\":[],\"closureLoadOrder\":[],"
        "\"stableAotNames\":[],\"commitOrder\":[],\"assemblies\":[],"
        "\"events\":[],\"baselineUses\":[],\"ordinaryAssemblies\":[],"
        "\"ordinaryClasses\":[";
    const std::string ending = "]}";
    if (!std::strcmp(argv[2], "oversize"))
    {
        full.resize(r03_ir_snapshot::GeneralLimit + 100, 'x');
        full.back() = '}';
        const int status = R03_IR_ReportText(14, full.c_str());
        return status < 0 ? 0 : 92;
    }
    if (!std::strcmp(argv[2], "large"))
    {
        for (int i = 0; i < 3500; ++i)
        {
            if (i) full += ',';
            full += "{\"assemblyName\":\"UnityEngine.CoreModule\",\"typeName\":"
                "\"R03.VeryLongOrdinaryClassNameForNativeFixture_";
            full += std::to_string(i);
            full += "\",\"isInterpreter\":false,\"isConstructedGeneric\":false,"
                    "\"usesStagedMetadata\":false}";
        }
    }
    full += ending;
    for (int i = 0; i < r03_ir_snapshot::IntCount; ++i)
    {
        const int value = i < r03_ir_snapshot::FirstBool ? i : 0;
        if (R03_IR_ReportInt(i, value) != 1) return 93;
    }
    for (int i = 0; i < r03_ir_snapshot::TextCount; ++i)
    {
        if (R03_IR_ReportText(i, i == 14 ? full.c_str() : "sample") != 1) return 94;
    }
    return R03_IR_ReportSeal() == 1 ? 0 : 95;
}
'''


class ActualNativeGeneralTransportContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="r03-actual-native-writer-")
        cls.root = Path(cls.temp.name).resolve()
        source = cls.root / "writer.cpp"
        source.write_text(HEADER + extract_source() + MAIN, encoding="utf-8")
        cls.exe = cls.root / "writer"
        compiler = shutil.which(os.environ.get("CXX", "clang++")) or shutil.which("g++")
        if not compiler:
            raise RuntimeError("Required compiler unavailable; cannot pass without actual C++11")
        cls.compile_argv = [compiler, "-std=c++11", "-Wall", "-Wextra", "-Werror",
                            "-pedantic", "-pthread", str(source), "-o", str(cls.exe)]
        result = subprocess.run(cls.compile_argv, capture_output=True, text=True, timeout=120)
        if result.returncode:
            raise AssertionError("Actual C++11 report writer compiler failed\n" + result.stderr[-4000:])

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_actual(self, mode: str):
        root = self.root / mode
        root.mkdir()
        raw = root / "raw.json"
        proc = subprocess.run([str(self.exe), str(raw), mode],
                              capture_output=True, text=True, timeout=90)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return raw, proc

    def test_01_large_original_bytes_preopened_and_complete(self):
        raw, proc = self.run_actual("large")
        record = json.loads(raw.read_text(encoding="utf-8"))
        self.assertEqual(record["reportTransport"], "NativePreopenedSnapshotV1")
        self.assertTrue(record["finalDiagnostics"].startswith("R03FullGeneralSidecarV1:"))
        proof = verify(record["finalDiagnostics"], raw)
        self.assertEqual(proof["result"], "PassedCompleteByteBoundAndSchema_WithoutGlobalEpochProof")
        self.assertGreater(proof["bytes"], TEXT_LIMIT)
        self.assertLess(proof["bytes"], GENERAL_LIMIT)
        self.assertEqual(proof["ordinaryClassCount"], 3500)
        self.assertIn("R03FullGeneralSidecar", proc.stderr)
        self.assertIs(proof["runtimeAcceptance"], False)

    def test_02_short_general_still_inline_no_sidecar(self):
        raw, _ = self.run_actual("small")
        record = json.loads(raw.read_text(encoding="utf-8"))
        self.assertFalse(record["finalDiagnostics"].startswith("R03FullGeneralSidecarV1:"))
        proof = verify(record["finalDiagnostics"], raw)
        self.assertEqual(proof["transport"], "InlineWithin256KiB")
        self.assertFalse((raw.parent / "raw.json.general.json").exists())

    def test_03_above_general_cap_rejected_no_complete_receipt(self):
        raw, proc = self.run_actual("oversize")
        self.assertTrue(raw.exists())
        self.assertEqual(raw.stat().st_size, 0)
        self.assertIn("R03SnapshotFailure", proc.stderr)
        self.assertIn("general-over-limit", proc.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
