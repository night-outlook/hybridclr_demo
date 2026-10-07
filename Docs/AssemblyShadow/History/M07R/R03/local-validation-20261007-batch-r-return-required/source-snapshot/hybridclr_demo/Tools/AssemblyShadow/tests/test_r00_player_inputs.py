import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from r00_player_inputs import require_current_pairing
from shadow_tools import read_json, VerificationError


class R00PairingTests(unittest.TestCase):
    def setUp(self):
        self.pins = read_json(Path(__file__).resolve().parents[3] / "ProjectSettings/AssemblyShadowSourcePins.json")

    def test_exact_captured_pairing_passes(self):
        require_current_pairing(self.pins, copy.deepcopy(self.pins), "test")

    def test_demo_drift_rejects_even_when_runtime_abi_is_identical(self):
        captured = copy.deepcopy(self.pins)
        captured["demo"]["revision"] = "9f322a948981341321f0eeb40cc5aa006a094bae"
        with self.assertRaises(VerificationError):
            require_current_pairing(self.pins, captured, "historical Player")

    def test_package_and_install_path_drift_reject(self):
        for repository, key, value in (("hybridclrUnity", "revision", "8c94f178646e71c9020dc8b66cf3c38632e9cc6d"),
                                       ("hybridclr", "localPath", "../other-checkout")):
            with self.subTest(repository=repository, key=key):
                captured = copy.deepcopy(self.pins)
                captured[repository][key] = value
                with self.assertRaises(VerificationError):
                    require_current_pairing(self.pins, captured, "captured")


if __name__ == "__main__":
    unittest.main()
