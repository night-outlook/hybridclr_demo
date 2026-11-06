#!/usr/bin/env python3
"""Host-only full bytes/symlink custody and real product-seal integration tests."""
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

import initializer_host_custody as custody
from batch_evidence import finalize


class HostCustodySealTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="r03-init-host-custody-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve(strict=True)
        self.raw = self.root / "raw-native-host"
        self.raw.mkdir()
        (self.raw / "historical-eight" / "evidence").mkdir(parents=True)
        (self.raw / "RESULT.json").write_text('{"result":"PassedHostOnlyTenComponents"}\n')
        (self.raw / "historical-eight/evidence" / "transaction").mkdir()
        (self.raw / "historical-eight/evidence/transaction" / "native.dat").write_bytes(b"\x00\x80actual-bytes")
        (self.raw / "historical-eight/evidence" / "alias").symlink_to("transaction",
                                                                    target_is_directory=True)
        (self.raw / "orphan").symlink_to("../../private-unused",
                                         target_is_directory=True)
        self.product = self.root / "batch"
        self.product.mkdir()
        (self.product / "ADMISSION.json").write_text('{"host":"test-only"}\n')
        self.captured = self.product / "host-custody"

    def test_01_real_symlink_metadata_and_all_bytes_pass_through_generic_seal(self):
        receipt = custody.capture(self.raw, self.captured)
        self.assertEqual(receipt["symlinkCount"], 2)
        self.assertTrue(receipt["rawHostPreservedOutsideProductSeal"])
        with tarfile.open(self.captured / "HOST_REGULAR_BYTES.tar.gz", "r:gz") as tf:
            names = tf.getnames()
            self.assertEqual(set(names), {
                "RESULT.json", "historical-eight/evidence/transaction/native.dat",
                "HOST_MANIFEST.json"})
            self.assertTrue(all(m.isfile() for m in tf.getmembers()))
        manifest = json.loads((self.captured / "HOST_MANIFEST.json").read_bytes())
        self.assertEqual({row["path"]: row["target"] for row in manifest["entries"]
                          if row["kind"] == "symlink"}, {
            "historical-eight/evidence/alias": "transaction",
            "orphan": "../../private-unused"})
        self.assertEqual(custody.verify_live(self.raw, self.captured)["symlinkCount"], 2)
        result = finalize(self.product, {
            "kind": "HostCustodySyntheticIntegration_NotUnity",
            "result": "ReturnRequired", "R03Accepted": False, "runtimeAcceptance": False})
        self.assertEqual(result["sealStatus"], "Passed", result.get("sealError"))
        with tarfile.open(self.product / "evidence.tar.gz", "r:gz") as tf:
            names = tf.getnames()
            self.assertIn("host-custody/HOST_REGULAR_BYTES.tar.gz", names)
            self.assertIn("host-custody/HOST_MANIFEST.json", names)
            self.assertIn("host-custody/HOST_CUSTODY_RESULT.json", names)
            self.assertNotIn("historical-eight/evidence/alias", names)
        self.assertTrue((self.raw / "historical-eight/evidence/alias").is_symlink())
        self.assertIs(result["R03Accepted"], False)
        self.assertEqual(result["result"], "ReturnRequired")

    def test_02_host_symlink_target_mutation_fails_even_if_file_bytes_same(self):
        custody.capture(self.raw, self.captured)
        link = self.raw / "historical-eight/evidence/alias"
        link.unlink()
        link.symlink_to("unapproved-new-target", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "link identities drifted"):
            custody.verify_live(self.raw, self.captured)

    def test_03_host_regular_file_mutation_fails(self):
        custody.capture(self.raw, self.captured)
        (self.raw / "RESULT.json").write_text('{"result":"Changed"}\n')
        with self.assertRaisesRegex(ValueError, "link identities drifted"):
            custody.verify_live(self.raw, self.captured)

    def test_04_archive_tamper_cannot_be_relabelled_pass(self):
        custody.capture(self.raw, self.captured)
        archive = self.captured / "HOST_REGULAR_BYTES.tar.gz"
        with archive.open("ab") as file:
            file.write(b"\x00unverified-content")
        with self.assertRaisesRegex(ValueError, "Immutable source-bound"):
            custody.verify_live(self.raw, self.captured)

    def test_05_bad_external_roots_and_reuse_rejected(self):
        with self.assertRaisesRegex(ValueError, "Fresh external-to-host"):
            custody.capture(self.raw, self.raw / "not-outside")
        custody.capture(self.raw, self.captured)
        with self.assertRaisesRegex(ValueError, "Fresh external-to-host"):
            custody.capture(self.raw, self.captured)

    def test_06_generic_seal_rejects_direct_raw_symlink_host_tree(self):
        # Demonstrates exactly the failure fixed by the new placement.
        from batch_evidence import selected_files
        with self.assertRaisesRegex(Exception, "Unexpected directory symlink"):
            list(selected_files(self.raw))
        self.assertTrue((self.raw / "historical-eight/evidence/alias").is_symlink())


if __name__ == "__main__":
    unittest.main(verbosity=2)
