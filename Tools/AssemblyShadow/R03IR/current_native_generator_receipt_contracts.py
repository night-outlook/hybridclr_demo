#!/usr/bin/env python3
"""Host-only adversarial receipt checks. Synthetic bytes never stand for a real DLL."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import current_native_generator_receipt as subject


class GeneratorReceiptContracts(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="r03-ir-generator-contracts-")
        self.addCleanup(temp.cleanup)
        root = Path(temp.name).resolve()
        self.original = root / "original.json"
        self.first = root / "first"
        self.repeat = root / "repeat"
        self.data = b"synthetic-not-the-real-Methods-dll"
        self.digest = hashlib.sha256(self.data).hexdigest()
        for key, value in (("PINNED_IR_SHA256", self.digest),
                           ("PINNED_IR_MVID", "00000000-0000-0000-0000-000000000001")):
            patcher = mock.patch.object(subject, key, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        paths = [{"path": "virtual-slot/Methods.dll", "sha256": "f" * 64}]
        paths += [{"path": f"synthetic/fixture-{i}.dll", "sha256": "e" * 64}
                  for i in range(14)]
        self.write(self.original, {"files": paths})
        for folder in (self.first, self.repeat):
            folder.mkdir()
            (folder / "Methods.dll").write_bytes(self.data)
            self.write(folder / "ir-target.json", {
                "schemaVersion": 1, "kind": "R03IRSideEffectFixture",
                "result": "GeneratedNotRuntimeValidated", "assembly": "Methods",
                "mvid": subject.PINNED_IR_MVID, "sha256": self.digest,
                "size": len(self.data), "instanceField": "R03.Node.stable",
                "method": "R03.Node.Keep", "layoutEditorAdmission": "Passed",
                "sourceMode": "SupplementaryIR", "expectedReturn": 42,
                "expectedIncrementPerCall": 1, "sideEffectInstructionsVerified": True,
                "originalSFixtureUnchanged": True, "runtimeAcceptance": False,
            })

    @staticmethod
    def write(path: Path, obj: dict):
        path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def mutate(self, key, value, root=None):
        path = (root or self.first) / "ir-target.json"
        record = subject.load(path)
        record[key] = value
        self.write(path, record)

    def verify(self):
        return subject.verify(self.original, self.first, self.repeat)

    def test_01_synthetic_positive_is_not_runtime_evidence(self):
        report = self.verify()
        self.assertEqual(report["result"], "PassedPinnedFreshGeneratorBytesAndRepeatability_HostOnly")
        self.assertIs(report["R03Accepted"], False)
        self.assertIs(report["net8CompilationProvenByCaller"], False)

    def test_02_actual_binary_mutation_rejected(self):
        (self.first / "Methods.dll").write_bytes(b"X" + self.data[1:])
        with self.assertRaisesRegex(ValueError, "binary bytes"):
            self.verify()

    def test_03_forged_digest_rejected(self):
        self.mutate("sha256", "0" * 64)
        with self.assertRaisesRegex(ValueError, "Wrong IR field"):
            self.verify()

    def test_04_wrong_mvid_rejected(self):
        self.mutate("mvid", "ffffffff-ffff-ffff-ffff-ffffffffffff")
        with self.assertRaisesRegex(ValueError, "Wrong IR field"):
            self.verify()

    def test_05_bool_in_integer_slot_rejected(self):
        self.mutate("expectedIncrementPerCall", True)
        with self.assertRaisesRegex(ValueError, "Wrong IR integer"):
            self.verify()

    def test_06_fake_acceptance_rejected(self):
        self.mutate("runtimeAcceptance", True)
        with self.assertRaisesRegex(ValueError, "Wrong IR boolean"):
            self.verify()

    def test_07_missing_side_effect_rejected(self):
        self.mutate("sideEffectInstructionsVerified", False)
        with self.assertRaisesRegex(ValueError, "Wrong IR boolean"):
            self.verify()

    def test_08_repeat_mutation_rejected(self):
        self.mutate("expectedReturn", 43, self.repeat)
        with self.assertRaisesRegex(ValueError, "Wrong IR integer"):
            self.verify()

    def test_09_duplicate_json_keys_rejected(self):
        (self.first / "ir-target.json").write_text('{"kind":"valid","kind":"forged"}')
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            self.verify()

    def test_10_original_equals_ir_rejected(self):
        record = subject.load(self.original)
        record["files"][0]["sha256"] = self.digest
        self.write(self.original, record)
        with self.assertRaisesRegex(ValueError, "equals original"):
            self.verify()

    def test_11_duplicate_original_target_rejected(self):
        record = subject.load(self.original)
        record["files"][1]["path"] = "virtual-slot/Methods.dll"
        self.write(self.original, record)
        with self.assertRaisesRegex(ValueError, "Duplicated original"):
            self.verify()

    def test_12_symlink_target_rejected(self):
        path = self.first / "Methods.dll"
        path.unlink()
        path.symlink_to(self.repeat / "Methods.dll")
        with self.assertRaisesRegex(ValueError, "symlink fixture"):
            self.verify()

    def test_13_missing_repeat_rejected(self):
        (self.repeat / "Methods.dll").unlink()
        with self.assertRaisesRegex(ValueError, "Missing/symlink fixture"):
            self.verify()

    def test_14_missing_original_inventory_rejected(self):
        self.original.unlink()
        with self.assertRaisesRegex(ValueError, "Missing/symlink evidence"):
            self.verify()

    def test_15_same_roots_rejected(self):
        with self.assertRaisesRegex(ValueError, "distinct"):
            subject.verify(self.original, self.first, self.first)

    def test_16_wrong_reported_size_rejected(self):
        self.mutate("size", len(self.data) + 1)
        with self.assertRaisesRegex(ValueError, "Wrong IR integer"):
            self.verify()


if __name__ == "__main__":
    unittest.main(verbosity=2)
