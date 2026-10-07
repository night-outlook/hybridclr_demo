"""Static contract checks for the protected profile-1 H1 reference verifier."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parents[1]
sys.path.insert(0, str(TOOLS))

import h1_paired_performance as performance

spec = importlib.util.spec_from_file_location(
    "h1_protected_reference_verifier", TOOLS / "verify-h1-protected-reference.py")
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)


class ProtectedReferenceContractTests(unittest.TestCase):
    def test_protected_reference_identity_matches_live_authority(self):
        targets = json.loads((ROOT / "Docs/AssemblyShadow/Handoff/source-targets.json").read_text())
        self.assertEqual(
            targets["performanceReference"]["commit"],
            reference.REFERENCE_DEMO_HEAD)
        self.assertEqual(
            {
                performance.MEASUREMENT_CORE,
                performance.PROCESS_MEMORY,
                performance.WITNESS,
            },
            set(reference.MEASUREMENT_SOURCES))
        self.assertEqual("f1c923cbaa814e1b63f3c5b9f8303c90616de726",
                         reference.REFERENCE_SOURCE_ANCHOR)

    def test_reference_runtime_revisions_are_explicit_and_distinct_from_candidate(self):
        targets = json.loads((ROOT / "Docs/AssemblyShadow/Handoff/source-targets.json").read_text())
        candidate = targets["demoTargets"]["candidate"]["runtimePins"]
        self.assertEqual(40, len(reference.REFERENCE_REVISIONS["hybridclr"]))
        self.assertEqual(40, len(reference.REFERENCE_REVISIONS["hybridclrUnity"]))
        self.assertEqual(40, len(reference.REFERENCE_REVISIONS["il2cppPlus"]))
        self.assertNotEqual(candidate["hybridclr"]["revision"],
                            reference.REFERENCE_REVISIONS["hybridclr"])
        self.assertNotEqual(candidate["hybridclrUnity"]["revision"],
                            reference.REFERENCE_REVISIONS["hybridclrUnity"])
        self.assertNotEqual(candidate["il2cppPlus"]["revision"],
                            reference.REFERENCE_REVISIONS["il2cppPlus"])


if __name__ == "__main__":
    unittest.main()
