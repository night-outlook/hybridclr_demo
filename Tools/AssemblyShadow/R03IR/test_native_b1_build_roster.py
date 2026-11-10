#!/usr/bin/env python3
"""Host-only positive/negative cases for real Player-linked allocator exclusion."""
from pathlib import Path
import tempfile
import json
import unittest

from native_b1_build_roster import inspect, attest

GOOD = ("0000000000010000 T _R03_IRB1_Open\n"
        "0000000000020000 T _R03_IRG_Open\n"
        "0000000000030000 T _SomeNormalUnitySymbol\n")


class NativeB1BuildRosterContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r03-b1-linked-roster-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve(strict=True) / "libil2cpp"
        (self.root / "vm").mkdir(parents=True)

    def test_01_regular_production_sources_and_no_overrides(self):
        result = inspect(self.root, GOOD)
        self.assertEqual(result["linkedHostAllocatorOverrides"], 0)
        self.assertTrue(result["hostDriverAbsentFromInstalledVM"])
        self.assertFalse(result["actualUnityPlayerStarted"])

    def test_02_original_oneuse11_defined_allocators_are_rejected(self):
        for name in ("__Znwm", "__Znam", "__ZdlPv", "__ZdaPv",
                     "__ZdlPvm", "__ZdaPvm", "_Znwm", "_ZdlPv"):
            with self.subTest(symbol=name), self.assertRaisesRegex(
                    ValueError, "Global C\\+\\+ allocation override"):
                inspect(self.root, GOOD + "0000000000040000 T " + name + "\n")

    def test_03_undefined_imports_do_not_forge_own_allocators(self):
        self.assertEqual(inspect(
            self.root, GOOD + "                 U __Znwm\n")["linkedHostAllocatorOverrides"], 0)

    def test_04_standalone_source_in_installed_vm_is_forbidden(self):
        (self.root / "vm/AssemblyShadowFirstFailureV2Host.cpp").write_text("int main() { return 0; }")
        with self.assertRaisesRegex(ValueError, "installed in Unity"):
            inspect(self.root, GOOD)

    def test_05_symlink_alias_is_forbidden_even_when_target_missing(self):
        (self.root / "vm/AssemblyShadowFirstFailureV2Host.cpp").symlink_to(
            self.root / "unavailable-host.cpp")
        with self.assertRaisesRegex(ValueError, "installed in Unity"):
            inspect(self.root, GOOD)

    def test_06_unobserved_or_malformed_nm_output_fails(self):
        for bad in ("", "  U __Znwm\n", "not a native nm result"):
            with self.subTest(source=bad), self.assertRaises(ValueError):
                inspect(self.root, bad)

    def test_07_noncanonical_installed_root_fails(self):
        alias = self.root.parent / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Canonical installed"):
            inspect(alias, GOOD)


    def test_08_exact_real_shaped_nm_receipt_writes_once_and_rechecks(self):
        evidence = self.root.parent / "build-evidence"
        evidence.mkdir()
        assembly = self.root.parent / "GameAssembly.dylib"
        assembly.write_bytes(b"known-test-binary-not-Unity")
        received = attest(evidence, self.root, assembly, GOOD, "", 0)
        self.assertEqual(received["result"],
                         "PassedSourceAndLinkedDefinedExclusion_NotPlayerStartup")
        self.assertEqual(received["nmStdoutBytes"], len(GOOD.encode()))
        self.assertEqual(received["verifiedExclusion"]["linkedHostAllocatorOverrides"], 0)
        self.assertEqual((evidence/"native-b1-linked-symbols.nm").read_text(), GOOD)
        self.assertEqual(json.loads((evidence/"native-b1-linked-roster.json").read_text()),
                         received)
        self.assertEqual(attest(evidence, self.root, assembly, GOOD, "", 0),
                         received)

    def test_09_mutated_nm_recheck_rejected_without_overwriting_first_receipt(self):
        evidence = self.root.parent / "build-evidence"
        evidence.mkdir()
        assembly = self.root.parent / "GameAssembly.dylib"
        assembly.write_bytes(b"known-test-binary-not-Unity")
        attest(evidence, self.root, assembly, GOOD, "", 0)
        original = (evidence/"native-b1-linked-roster.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "Prior exclusive B1"):
            attest(evidence, self.root, assembly, GOOD+"another_defined_symbol T _x\\n", "", 0)
        self.assertEqual((evidence/"native-b1-linked-roster.json").read_bytes(),
                         original)

    def test_10_rejected_linked_allocation_persists_raw_failing_receipt(self):
        evidence = self.root.parent / "build-evidence"
        evidence.mkdir()
        assembly = self.root.parent / "GameAssembly.dylib"
        assembly.write_bytes(b"known-test-binary-not-Unity")
        bad_nm = GOOD+"0000000000040000 T __Znwm\\n"
        with self.assertRaisesRegex(ValueError, "Actual linked allocator roster refused"):
            attest(evidence, self.root, assembly, bad_nm, "", 0)
        receipt = json.loads((evidence/"native-b1-linked-roster.json").read_text())
        self.assertEqual(receipt["result"], "RejectedNativeLinkedRoster_NotPlayerRun")
        self.assertIn("__Znwm", (evidence/"native-b1-linked-symbols.nm").read_text())
        self.assertFalse(receipt["actualUnityPlayerStarted"])

    def test_11_failure_to_run_nm_is_persisted_without_claiming_pass(self):
        evidence = self.root.parent / "build-evidence"
        evidence.mkdir()
        assembly = self.root.parent / "GameAssembly.dylib"
        assembly.write_bytes(b"known-test-binary-not-Unity")
        with self.assertRaisesRegex(ValueError, "Actual linked allocator roster refused"):
            attest(evidence, self.root, assembly, "", "nm cannot read binary", 2)
        receipt = json.loads((evidence/"native-b1-linked-roster.json").read_text())
        self.assertEqual(receipt["nmExitCode"], 2)
        self.assertEqual(receipt["result"], "RejectedNativeLinkedRoster_NotPlayerRun")


if __name__ == "__main__":
    unittest.main(verbosity=2)
