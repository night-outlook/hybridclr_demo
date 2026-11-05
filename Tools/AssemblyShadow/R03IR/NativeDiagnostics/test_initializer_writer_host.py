#!/usr/bin/env python3
"""Compile actual additive native writer against a test-only observer stub."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "PlayerProject/R03InitializerObservationWriter.cpp"
DRIVER = HERE / "initializer_writer_driver.cpp"
INCLUDE = HERE / "InitializerHostInclude"


class InitializerWriterHostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="r03-irw-host-")
        cls.binary = Path(cls.temp.name) / "driver"
        compiler = shutil.which("clang++") or shutil.which("g++")
        if compiler is None:
            raise AssertionError("A genuine C++11 host compiler is required")
        subprocess.run([compiler, "-std=c++11", "-Wall", "-Wextra", "-Werror",
                        "-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1",
                        "-I", str(INCLUDE), str(SOURCE), str(DRIVER),
                        "-o", str(cls.binary)], check=True, timeout=90)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_mode(self, mode, preexisting=False):
        with tempfile.TemporaryDirectory(prefix="r03-irw-case-") as root:
            output = Path(root) / "report.json"
            if preexisting:
                output.write_text("preexisting\n", encoding="utf-8")
            result = subprocess.run([str(self.binary), mode, str(output)],
                                    capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, (mode, result.stderr))
            return output.read_bytes() if output.exists() else None

    def test_failure_is_real_unaccepted_native_schema(self):
        raw = json.loads(self.run_mode("failure"))
        self.assertEqual(raw["kind"], "R03IRInitializerCommitObservationV1")
        self.assertEqual(raw["reportTransport"], "NativePreopenedInitializerObservationV1")
        self.assertEqual((raw["commitReturn"], raw["finalState"]), (19, 9))
        self.assertEqual(raw["preparedField"], 3)
        self.assertEqual(raw["finalField"], 3)
        self.assertEqual(raw["positiveMask"], 15)
        self.assertEqual(raw["initializerCallbackCalls"], 1)
        self.assertIs(raw["postAotAttempted"], True)
        for flag in ("runtimeAcceptance", "R03Accepted", "H2Passed",
                     "nativeV2TransportImplemented", "firstRecoveryAuthenticated",
                     "completeDiagnosticsAuthenticated"):
            self.assertIs(raw[flag], False)

    def test_control_is_distinct_success_case(self):
        raw = json.loads(self.run_mode("control"))
        self.assertEqual((raw["commitReturn"], raw["finalState"]), (0, 6))
        self.assertIs(raw["postAotAttempted"], False)
        self.assertEqual(raw["initializerCallbackCalls"], 1)

    def test_mutations_and_observer_absence_are_not_sealed(self):
        for mode in ("wrong-state", "field-mutated",
                     "observer-reject", "canary-executed"):
            with self.subTest(mode=mode):
                self.assertEqual(self.run_mode(mode), b"")

    def test_bad_nonce_and_reused_output_rejected(self):
        self.assertIsNone(self.run_mode("bad-run"))
        self.assertEqual(self.run_mode("preexisting", preexisting=True),
                         b"preexisting\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
