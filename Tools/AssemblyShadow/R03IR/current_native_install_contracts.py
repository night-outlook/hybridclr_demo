#!/usr/bin/env python3
"""Host-only adversarial native-installed-source parity tests; no Unity build."""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import current_native_install_audit as audit


class InstalledNativeAuditContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r03-install-parity-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve(strict=True)
        self.source = self.root / "checkout"
        self.install = self.root / "installed"
        (self.source / "libil2cpp/vm").mkdir(parents=True)
        (self.install / "vm").mkdir(parents=True)
        self.rel = "libil2cpp/vm/Example.cpp"
        self.source_file = self.source / self.rel
        self.install_file = self.install / "vm/Example.cpp"
        self.data = b"// synthetic source bytes\x0aextern int k;\x0a"
        self.source_file.write_bytes(self.data)
        self.install_file.write_bytes(self.data)
        self.source_sha = hashlib.sha256(self.data).hexdigest()
        self.row = {"path": self.rel,
                    "gitBlob": audit.delta.git_blob(self.data)}
        self.inventory = {"vm/Example.cpp": {"sha256": self.source_sha,
                                               "size": len(self.data), "path": "vm/Example.cpp"}}

    def test_01_parity_recognizes_actual_file_bytes(self):
        rows = audit.vm_installed_parity(
            self.source, self.install, [self.row],
            self.inventory, self.inventory)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["sha256"], self.source_sha)
        self.assertEqual(rows[0]["sourceGitBlob"], self.row["gitBlob"])

    def test_02_installed_byte_mutation_is_rejected(self):
        self.install_file.write_bytes(self.data + b"//changed")
        with self.assertRaises(ValueError):
            audit.vm_installed_parity(
                self.source, self.install, [self.row],
                self.inventory, self.inventory)

    def test_03_source_manifest_forgery_is_rejected(self):
        bad = dict(self.row, gitBlob="0"*40)
        with self.assertRaises(ValueError):
            audit.vm_installed_parity(
                self.source, self.install, [bad],
                self.inventory, self.inventory)

    def test_04_before_inventory_missing_source_is_rejected(self):
        with self.assertRaises(ValueError):
            audit.vm_installed_parity(self.source, self.install, [self.row],
                                      {}, self.inventory)

    def test_05_after_inventory_missing_source_is_rejected(self):
        with self.assertRaises(ValueError):
            audit.vm_installed_parity(self.source, self.install, [self.row],
                                      self.inventory, {})

    def test_06_before_hash_mutation_is_rejected(self):
        bad = copy.deepcopy(self.inventory)
        bad["vm/Example.cpp"]["sha256"] = "f"*64
        with self.assertRaises(ValueError):
            audit.vm_installed_parity(self.source, self.install, [self.row],
                                      bad, self.inventory)

    def test_07_after_size_mutation_is_rejected(self):
        bad = copy.deepcopy(self.inventory)
        bad["vm/Example.cpp"]["size"] += 1
        with self.assertRaises(ValueError):
            audit.vm_installed_parity(self.source, self.install, [self.row],
                                      self.inventory, bad)

    def test_08_duplicate_source_name_is_rejected(self):
        with self.assertRaises(ValueError):
            audit.vm_installed_parity(self.source, self.install,
                                      [self.row, self.row],
                                      self.inventory, self.inventory)

    def test_09_path_traversal_is_rejected(self):
        bad = dict(self.row, path="libil2cpp/vm/../Example.cpp")
        with self.assertRaises(Exception):
            audit.vm_installed_parity(self.source, self.install, [bad],
                                      self.inventory, self.inventory)

    def test_10_installed_symlink_is_rejected(self):
        self.install_file.unlink()
        self.install_file.symlink_to(self.source_file)
        with self.assertRaises(Exception):
            audit.vm_installed_parity(self.source, self.install, [self.row],
                                      self.inventory, self.inventory)

    def test_11_source_symlink_is_rejected(self):
        other = self.root / "outside.cpp"
        other.write_bytes(self.data)
        self.source_file.unlink()
        self.source_file.symlink_to(other)
        with self.assertRaises(Exception):
            audit.vm_installed_parity(self.source, self.install, [self.row],
                                      self.inventory, self.inventory)

    def test_12_extra_source_file_without_manifest_not_auto_accepted(self):
        (self.source / "libil2cpp/vm/Unlisted.cpp").write_text("//extra\n")
        (self.install / "vm/Unlisted.cpp").write_text("//extra\n")
        rows = audit.vm_installed_parity(
            self.source, self.install, [self.row],
            self.inventory, self.inventory)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source"], "libil2cpp/vm/Example.cpp")

    def test_13_run_references_real_builder_not_test_double(self):
        text = Path(audit.__file__).read_text()
        self.assertIn("build-receipt.json", text)
        self.assertIn("installedNativeRoot", text)
        self.assertIn("candidate-release", text)
        self.assertIn("candidate-debug", text)
        self.assertIn("candidate-off", text)
        self.assertIn("NotProvenBySourceParity", text)
        self.assertNotIn("return {'R03Accepted': True}", text)

    def test_14_requires_exact_role_roster(self):
        self.assertEqual(tuple(audit.ROLES), (
            "candidate-release", "candidate-debug", "candidate-off"))
        self.assertIs(audit.ROLES["candidate-off"][1], False)
        self.assertIs(audit.ROLES["candidate-debug"][1], True)

    def test_15_current_source_identity_is_versioned(self):
        self.assertEqual(audit.delta.CURRENT_NATIVE,
                         "6510aed7cab67e9fc70b13ae22a115ad9819193b")
        self.assertEqual(len(audit.delta.EXPECTED_VM_NAMES), 43)
        self.assertEqual(audit.delta.LEGACY_NATIVE,
                         "74dbdbea80d83923863303bd2b2c0a87f36541b1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
