import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "create-h1-count-fixtures.py"
WRITER = ROOT / "h1-count-fixture-writer.cs"


def load_launcher():
    spec = importlib.util.spec_from_file_location("h1_nested_fixture_launcher", LAUNCHER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load fixture launcher")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class H1NestedFixtureGeneratorTests(unittest.TestCase):
    def test_n01_and_n02_are_the_six_direct_sibling_boundaries(self):
        launcher = load_launcher()
        cases = launcher.NESTED_CASE_SPECS[:6]
        self.assertEqual(
            ["H1R-N01-a", "H1R-N01-b", "H1R-N01-c", "H1R-N01-d",
             "H1R-N02-a", "H1R-N02-b"],
            [case["caseId"] for case in cases])
        self.assertEqual([0, 1, 65534, 65535, 65536, 65537],
                         [case["groupCounts"][0] for case in cases])
        self.assertEqual(["Accepted"] * 4 + ["ControlledRejected"] * 2,
                         [case["expected"] for case in cases])
        self.assertTrue(all(case["family"] == "nested" for case in cases))

    def test_n03_n04_n05_recipes_keep_shape_inputs_explicit(self):
        launcher = load_launcher()
        cases = {case["caseId"]: case for case in launcher.NESTED_CASE_SPECS}
        self.assertEqual([2, 2], cases["H1R-N03-interleaved"]["groupCounts"])
        self.assertTrue(cases["H1R-N03-interleaved"]["interleaved"])
        self.assertEqual([1, 65535], cases["H1R-N04-adjacent-valid"]["groupCounts"])
        self.assertEqual("Accepted", cases["H1R-N04-adjacent-valid"]["expected"])
        self.assertEqual([1, 65536], cases["H1R-N04-adjacent-overflow"]["groupCounts"])
        self.assertEqual("ControlledRejected", cases["H1R-N04-adjacent-overflow"]["expected"])
        self.assertEqual([65535], cases["H1R-N05-final-repeat"]["groupCounts"])
        self.assertEqual("Accepted", cases["H1R-N05-final-repeat"]["expected"])

    def test_synthetic_interleaving_preserves_each_group_order(self):
        launcher = load_launcher()
        rows = launcher.interleave_nested_rows([
            [b"A1", b"A2", b"A3"],
            [b"B1", b"B2"],
        ])
        self.assertEqual([b"A1", b"B1", b"A2", b"B2", b"A3"], rows)

    def test_nested_identity_and_writer_contract_are_distinct_from_parameters(self):
        launcher = load_launcher()
        self.assertEqual("AssemblyShadow.H1Nested.Target", launcher.NESTED_TARGET_TYPE)
        self.assertEqual("AssemblyShadow.H1Nested.Target",
                         launcher.assembly_name("H1R-N01-b", True, "nested"))
        self.assertNotEqual(launcher.assembly_name("H1R-N01-b", False, "nested"),
                            launcher.assembly_name("H1R-N01-b", True, "nested"))
        source = WRITER.read_text(encoding="utf-8")
        self.assertIn("MaximumNestedCount = 131071", source)
        self.assertIn("TypeAttributes.NestedPublic", source)
        self.assertIn("NestedTypes.Add", source)
        self.assertIn("DeterministicMvid", source)
        self.assertNotIn("SetLength", source)

    def test_generation_command_binds_identity_and_family_for_each_flavor(self):
        launcher = load_launcher()
        binary = Path("/tmp/h1-writer.exe")
        output = Path("/tmp/H1R-case.dll")
        for family, variant in (("parameters", "base-1"), ("nested", "nested-single")):
            for shadow in (False, True):
                command = launcher.generation_command(binary, output, "H1R-case", 1,
                                                      variant, 20260910, shadow, family)
                self.assertEqual(launcher.assembly_name("H1R-case", shadow, family), command[3])
                if family == "nested":
                    self.assertEqual(9, len(command))
                    self.assertEqual("nested", command[-1])
                else:
                    self.assertEqual(8, len(command))
                    self.assertEqual("20260910", command[-1])


if __name__ == "__main__":
    unittest.main()
