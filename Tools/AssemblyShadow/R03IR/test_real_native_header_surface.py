#!/usr/bin/env python3
"""Adversarial actual-fork source declaration tests. NO official Unity SDK."""
import os
from pathlib import Path
import unittest

from real_native_header_surface import FILES, PROBE, SourceRejected, inspect, read


class RealNativeHeaderSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ["R03_FORK_ROOT"])
        cls.probe = Path(os.environ["R03_CAPTURED_PROBE"])
        cls.inputs = {name: (cls.root / "libil2cpp" / name).read_bytes() for name in FILES}
        cls.body = cls.probe.read_bytes()

    def test_01_actual_public_fork_api_source_roster(self):
        result = read(self.root, self.probe)
        self.assertEqual(result["result"], "PassedForkAPISourceDeclarations_NoSDKCompile")
        self.assertEqual(len(result["realNativeFilesChecked"]), len(FILES))
        for key in ("nativeApiMocksUsed", "translationUnitCompiledAgainstUnitySdk",
                    "realIl2cppGenericContextObserved", "realNativeCapturedFailure15",
                    "runtimeAcceptance", "R03Accepted", "H2Passed"):
            self.assertIs(result[key], False)

    def test_02_each_actual_declaration_drift_rejected(self):
        count = 0
        for path, anchors in FILES.items():
            for anchor in anchors:
                needle = anchor.encode()
                raw = self.inputs[path]
                self.assertIn(needle, raw, (path, anchor))
                changed = dict(self.inputs)
                changed[path] = raw.replace(needle, b"__R03_DECLARATION_DRIFT__", 1)
                with self.subTest(file=path, anchor=anchor), self.assertRaises(SourceRejected):
                    inspect(changed, self.body)
                count += 1
        self.assertGreaterEqual(count, 25)

    def test_03_missing_or_extra_native_file_rejected(self):
        first = next(iter(FILES))
        altered = dict(self.inputs)
        altered.pop(first)
        with self.assertRaises(SourceRejected):
            inspect(altered, self.body)
        altered = dict(self.inputs)
        altered["invented-fork.cpp"] = b"mock"
        with self.assertRaises(SourceRejected):
            inspect(altered, self.body)

    def test_04_exact_native_probe_path_and_guard_source_required(self):
        for anchor in PROBE:
            needle = anchor.encode()
            self.assertIn(needle, self.body)
            with self.subTest(anchor=anchor), self.assertRaises(SourceRejected):
                inspect(self.inputs, self.body.replace(needle, b"__MISSING__", 1))

    def test_05_forged_physical_class_materialization_refused(self):
        with self.assertRaisesRegex(SourceRejected, "cannot be materialized"):
            inspect(self.inputs, self.body + b"\nClass::FromIl2CppType(arg);\n")

    def test_06_unavailable_sdk_is_never_labelled_compiled(self):
        report = inspect(self.inputs, self.body)
        self.assertFalse(report["UnitySdkBaselibPresent"])
        self.assertFalse(report["translationUnitCompiledAgainstUnitySdk"])
        self.assertFalse(report["realNativeCapturedFailure15"])

    def test_07_canonical_file_inputs_only(self):
        with self.assertRaises(SourceRejected):
            read(Path("relative-repo"), self.probe)
        with self.assertRaises(SourceRejected):
            read(self.root, Path("relative.cpp"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
