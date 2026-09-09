"""Focused checks for R00 early-startup authentication and output layout."""
from pathlib import Path
import hashlib
import importlib.util
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r01_early_capsule as capsule
import r00_results as gate
from shadow_tools import VerificationError

_launcher_spec = importlib.util.spec_from_file_location("r00_startup_launcher", Path(__file__).resolve().parents[1] / "run-r00-players.py")
launcher = importlib.util.module_from_spec(_launcher_spec)
_launcher_spec.loader.exec_module(launcher)


def _capsule_data(path: Path, mode: str = "Baseline", patch_id: str = "P03"):
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    return {
        "mode": mode, "baselineBuildId": "B", "runtimeAbiHash": "a" * 64,
        "patchId": patch_id, "candidates": ["A"], "stableAotNames": ["S"],
        "inputs": [{"name": "A", "dllPath": str(path), "dllLength": len(payload), "dllSha256": digest,
                     "pdbPath": "", "pdbLength": 0, "pdbSha256": ""}],
        "ordinaryPath": "", "ordinarySha256": "", "prerequisiteFiles":
        [{"path": str(path), "length": len(payload), "sha256": digest}],
    }


def _receipt(data, pid=41, operations=None):
    return {"mode": data["mode"], "result": "Passed", "error": "", "callbackReturnCode": 0,
            "processId": pid, "operations": operations or []}


class R00StartupCorrectionTests(unittest.TestCase):
    def test_authenticated_baseline_and_control_operation_boundaries(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "A.dll"
            path.write_bytes(b"fixture")
            baseline = _capsule_data(path)
            gate.verify_early_receipt_contract(_receipt(baseline), baseline, "Baseline", 41)
            control = _capsule_data(path, "Control")
            phases = ["configure", "begin", "reserve", "stage:A", "validate", "commit"]
            operations = [{"phase": phase, "code": "Success", "intCode": 0} for phase in phases]
            gate.verify_early_receipt_contract(_receipt(control, operations=operations), control, "Control", 41)

    def test_wrong_capsule_pid_and_extra_operation_are_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "A.dll"
            path.write_bytes(b"fixture")
            expected = _capsule_data(path)
            alternate = _capsule_data(path, patch_id="P01")
            capsule_path = Path(root) / "r01-early.capsule"
            capsule_path.write_bytes(capsule.encode(alternate))
            with self.assertRaises(VerificationError):
                gate.verify_capsule_reconstruction(capsule_path, expected, "substitution")
            with self.assertRaises(VerificationError):
                gate.verify_early_receipt_contract(dict(_receipt(expected), processId=42), expected, "Baseline", 41)
            extra = dict(_receipt(expected), operations=[{"phase": "configure", "code": "Success", "intCode": 0}])
            with self.assertRaises(VerificationError):
                gate.verify_early_receipt_contract(extra, expected, "Baseline", 41)

    def test_launch_layout_places_early_receipt_under_result_directory(self):
        with tempfile.TemporaryDirectory() as root:
            results = Path(root) / "Results"
            result_path, mode_dir, early_result = launcher.output_paths(results, "R00-ON-P01")
            self.assertEqual(result_path.parent, results)
            self.assertEqual(mode_dir.parent, results)
            self.assertEqual(early_result.parent, mode_dir)
            self.assertTrue(early_result.is_relative_to(results))

    def test_legacy_boundary_remains_explicit(self):
        project = Path(__file__).resolve().parents[3]
        probe = (project / "Assets/AssemblyShadowDemo/Bootstrap/M07R00PerformanceProbe.cs").read_text(encoding="utf-8")
        source = (project / "Tools/AssemblyShadow/run-r00-players.py").read_text(encoding="utf-8")
        self.assertIn('"-shadowR00LegacyNoEarlyStartup"', probe)
        self.assertIn('"-shadowR00LegacyNoEarlyStartup", "1"', source)
        self.assertIn('"--early-startup-strategy"', source)

    def test_current_profile_cannot_downgrade_to_capsuleless_legacy(self):
        gate.validate_strategy_profile("legacy-explicit-no-capsule", 1)
        with self.assertRaises(VerificationError):
            gate.validate_strategy_profile("legacy-explicit-no-capsule", 2)

    def test_schema_one_current_profile_two_cannot_bypass_startup_gate(self):
        gate.validate_launch_profile(1, "legacy-historical", None)
        gate.validate_launch_profile(1, "legacy-historical", 1)
        with self.assertRaises(VerificationError):
            gate.validate_launch_profile(1, "legacy-historical", 2)
        gate.validate_launch_profile(2, "R01EarlyStartup", 2)
        with self.assertRaises(VerificationError):
            gate.validate_launch_profile(2, "legacy-explicit-no-capsule", 2)


if __name__ == "__main__":
    unittest.main()
