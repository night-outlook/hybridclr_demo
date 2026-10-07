import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "create-h1-count-fixtures.py"
WRITER = ROOT / "h1-count-fixture-writer.cs"


def load_launcher():
    spec = importlib.util.spec_from_file_location("h1_count_fixture_launcher", LAUNCHER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load fixture launcher")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class H1CountFixtureGeneratorTests(unittest.TestCase):
    def test_case_matrix_contains_base_and_p04_variants(self):
        launcher = load_launcher()
        cases = launcher.CASE_SPECS
        self.assertEqual(12, len(cases))
        self.assertEqual([0, 1, 254, 255, 256, 65535, 65536, 65537],
                         [case["count"] for case in cases[:8]])
        self.assertEqual({"return255", "partial-names", "instance", "mixed-kinds"},
                         {case["variant"] for case in cases[8:]})
        self.assertEqual(12, len({case["caseId"] for case in cases}))
        self.assertEqual({"Accepted", "ControlledRejected"},
                         {case["expected"] for case in cases})

    def test_names_and_manifest_contract_are_distinct_per_flavor(self):
        launcher = load_launcher()
        self.assertEqual("AssemblyShadow.H1Count.Target", launcher.TARGET_TYPE)
        ordinary = [launcher.assembly_name(str(case["caseId"]), False) for case in launcher.CASE_SPECS]
        self.assertEqual(len(ordinary), len(set(ordinary)))
        self.assertTrue(all(name.startswith("AssemblyShadow.H1Count.Ordinary.") for name in ordinary))
        ordinary_types = [launcher.target_type(str(case["caseId"]), False) for case in launcher.CASE_SPECS]
        self.assertEqual(len(ordinary_types), len(set(ordinary_types)))
        self.assertTrue(all(name.startswith("AssemblyShadow.H1Count.Ordinary_") for name in ordinary_types))
        self.assertEqual(launcher.TARGET_TYPE, launcher.target_type("H1R-P01-a", True))
        self.assertTrue(all(case["family"] == "parameters" for case in launcher.CASE_SPECS))

    def test_cli_rejects_unsupported_case_set(self):
        for option, value in (("--case-set", "future"),):
            result = subprocess.run([sys.executable, str(LAUNCHER), option, value,
                                     "--seed", "1", "--output-root", "/tmp/unused-h1-count-output"],
                                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertNotEqual(0, result.returncode)

    def test_nested_family_is_a_supported_cli_family(self):
        launcher = load_launcher()
        self.assertEqual(10, len(launcher.NESTED_CASE_SPECS))
        self.assertEqual("nested", launcher.NESTED_CASE_SPECS[0]["family"])

    def test_writer_contains_bounded_large_signature_and_no_padding(self):
        source = WRITER.read_text(encoding="utf-8")
        self.assertIn("MaximumCount = 65537", source)
        self.assertIn("method.Parameters.Add", source)
        self.assertIn("ParameterAttributes.None", source)
        self.assertIn("DeterministicMvid", source)
        self.assertNotIn("SetLength", source)


if __name__ == "__main__":
    unittest.main()
