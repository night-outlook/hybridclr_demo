"""Regression for the production H1 controlled performance build-map freezer."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import h1_paired_performance as analysis
import test_h1_paired_performance as fixtures

spec = importlib.util.spec_from_file_location(
    "h1_performance_build_map_freezer", TOOLS / "freeze-h1-performance-build-map.py")
freezer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(freezer)


class PerformanceBuildMapFreezerTests(unittest.TestCase):
    def setUp(self):
        self.helper = fixtures.H1PairedPerformanceTests(
            methodName="test_producer_schema_build_map_authenticates_actual_facts")
        self.root = self.helper.temp("h1-freezer-")
        self.source_map, self.refs = self.helper.build_map(self.root)

    def tearDown(self):
        self.helper.doCleanups()

    def side_from(self, name):
        source = self.source_map["sides"][name]
        return freezer.side(
            Path(source["projectRoot"]),
            Path(source["fixtureManifest"]["path"]),
            Path(source["replayReceipt"]["path"]),
            Path(source["builds"]["on"]["receipt"]["path"]),
            Path(source["builds"]["on"]["controlledEvidence"]["path"]),
            Path(source["builds"]["off"]["receipt"]["path"]),
            Path(source["builds"]["off"]["controlledEvidence"]["path"]),
        )

    def test_derives_comparability_from_authenticated_builds(self):
        value, receipt = freezer.freeze_map(self.side_from("A"), self.side_from("B"))
        self.assertEqual("Frozen", value["status"])
        self.assertEqual("ComparabilityPassed", analysis.validate_build_map(value)["status"])
        self.assertEqual("Passed", receipt["result"])
        self.assertFalse(receipt["acceptanceClaimed"])
        self.assertEqual(
            value["comparability"]["commonMeasurementCoreSha256"]["A"],
            value["comparability"]["commonMeasurementCoreSha256"]["B"])
        self.assertNotEqual(
            value["comparability"]["runtimeAbiHash"]["A"],
            value["comparability"]["runtimeAbiHash"]["B"])

    def test_tampered_controlled_evidence_is_not_freezable(self):
        evidence = Path(self.source_map["sides"]["B"]["builds"]["on"]["controlledEvidence"]["path"])
        evidence.write_text("{}")
        with self.assertRaises(Exception):
            freezer.freeze_map(self.side_from("A"), self.side_from("B"))


if __name__ == "__main__":
    unittest.main()
