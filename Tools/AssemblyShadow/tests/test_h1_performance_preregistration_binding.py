"""Regression for path-binding the preregistered H1 performance schedule."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

spec = importlib.util.spec_from_file_location(
    "h1_performance_preregistration_binder",
    TOOLS / "bind-h1-performance-preregistration.py")
binder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(binder)


class PerformancePreregistrationBindingTests(unittest.TestCase):
    def test_binds_only_protocol_path_and_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve() / "bound"
            receipt = binder.bind(root)
            self.assertEqual("Passed", receipt["result"])
            self.assertTrue(receipt["protocolBytesUnchanged"])
            self.assertTrue(receipt["scheduleSemanticFieldsUnchanged"])
            self.assertEqual(44, receipt["pairCount"])

            source = json.loads(binder.SOURCE_SCHEDULE.read_text())
            bound = json.loads(Path(receipt["boundSchedulePath"]).read_text())
            restored = dict(bound)
            restored["protocolPath"] = source["protocolPath"]
            restored["protocolSha256"] = source["protocolSha256"]
            self.assertEqual(source, restored)

    def test_output_root_must_be_fresh(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve() / "bound"
            binder.bind(root)
            with self.assertRaises(Exception):
                binder.bind(root)


if __name__ == "__main__":
    unittest.main()
