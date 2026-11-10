#!/usr/bin/env python3
"""Focused product-seal contract with B2's real descriptor-test output layout.

All data is synthetic host-only, but path names, negative alias type and the
real custody+product sealer implementations match the Local B2 runner. A
separate CI step executes the actual native B2 suite before sealing.
"""
from __future__ import annotations
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from initializer_host_custody import capture, verify_live
from batch_evidence import finalize


class B2CustodyAndProductSealContracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="r03-b2-host-seal-")
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name).resolve(strict=True)
        self.raw = base / "R03IR-NativeB1-oneuse-12-b2-host-raw"
        self.raw.mkdir()
        self.product = base / "product"
        self.product.mkdir()
        self.custody = self.product / "host" / "b2-raw-custody"
        self.custody.parent.mkdir(parents=True)
        (self.raw / "bounded-codec").mkdir()
        (self.raw / "bounded-codec" / "RESULT.json").write_text(
            json.dumps({"kind": "BoundedNativeV2Interop", "actualUnity": False}) + "\n")
        case = self.raw / "descriptor-transaction" / "sanitized" / "case-0160"
        target = case / "transaction"
        target.mkdir(parents=True)
        target.joinpath("marker").write_text("negative fixture remains untouched\n")
        (case / "alias").symlink_to(target, target_is_directory=True)
        (self.raw / "descriptor-transaction/RESULT.json").write_text(
            json.dumps({"kind": "InactiveNativeFileTransactionTests",
                        "productionTransportEnabled": False, "actualUnity": False}) + "\n")

    def capture(self):
        record = capture(self.raw, self.custody)
        self.assertEqual(record["result"], "PassedFullRegularBytesAndLiteralSymlinkTargets")
        self.assertEqual(record["symlinkCount"], 1)
        self.assertEqual(verify_live(self.raw, self.custody)["symlinkCount"], 1)
        return record

    def test_01_actual_negative_alias_layout_is_regular_only_in_product(self):
        self.capture()
        result = finalize(self.product, {
            "kind": "R03B2HostOnlyProductSeal",
            "result": "HostOnlyNotUnity",
            "R03Accepted": False, "runtimeAcceptance": False})
        self.assertEqual(result["sealStatus"], "Passed", result.get("sealError"))
        self.assertFalse(result["R03Accepted"])
        with tarfile.open(self.product / "evidence.tar.gz") as archive:
            names = archive.getnames()
        self.assertIn("host/b2-raw-custody/HOST_MANIFEST.json", names)
        self.assertIn("host/b2-raw-custody/HOST_REGULAR_BYTES.tar.gz", names)
        self.assertNotIn("host/b2-descriptor-transaction/sanitized/case-0160/alias", names)
        custody = json.loads((self.custody / "HOST_MANIFEST.json").read_text())
        aliases = [entry for entry in custody["entries"] if entry["kind"] == "symlink"]
        self.assertEqual(len(aliases), 1)
        self.assertEqual(aliases[0]["path"], "descriptor-transaction/sanitized/case-0160/alias")
        self.assertEqual(aliases[0]["target"],
                         str(self.raw / "descriptor-transaction/sanitized/case-0160/transaction"))

    def test_02_unexpected_product_symlink_remains_fail_closed(self):
        self.capture()
        (self.product / "host" / "unexpected-alias").symlink_to(
            self.raw, target_is_directory=True)
        result = finalize(self.product, {"result":"HostOnlyNotUnity", "R03Accepted":False})
        self.assertEqual(result["sealStatus"], "Failed")
        self.assertIn("Unexpected directory symlink", result["sealError"])
        self.assertFalse(result["R03Accepted"])

    def test_03_changed_literal_symlink_target_fails_live_custody(self):
        self.capture()
        alias = self.raw / "descriptor-transaction/sanitized/case-0160/alias"
        alias.unlink()
        alias.symlink_to(self.raw / "bounded-codec", target_is_directory=True)
        with self.assertRaises(ValueError):
            verify_live(self.raw, self.custody)

    def test_04_changed_host_regular_bytes_fail_live_custody(self):
        self.capture()
        with (self.raw / "bounded-codec/RESULT.json").open("a") as f:
            f.write("tamper")
        with self.assertRaises(ValueError):
            verify_live(self.raw, self.custody)

    def test_05_preexisting_custody_cannot_be_reused(self):
        self.capture()
        with self.assertRaises(ValueError):
            capture(self.raw, self.custody)


if __name__ == "__main__":
    unittest.main(verbosity=2)
