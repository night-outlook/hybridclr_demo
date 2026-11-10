#!/usr/bin/env python3
"""Host-only positive/negative cases for real Player-linked allocator exclusion."""
from pathlib import Path
import tempfile
import unittest

from native_b1_build_roster import inspect

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
