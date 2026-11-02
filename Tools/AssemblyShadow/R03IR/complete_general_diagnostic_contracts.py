#!/usr/bin/env python3
"""Adversarial host-only tests for the complete, untruncated R03 general JSON."""
from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest
import zlib

import complete_general_diagnostic as subject


def sample(ordinary_classes=()):
    return {"schemaVersion": 1, "enabled": True, "state": "FailedAfterCommit",
            "stateCode": 9, "generation": 4,
            "enumerationGeneration": 4, "classEnumerationGeneration": 4,
            "startupCandidateNames": [], "closureLoadOrder": [],
            "stableAotNames": [], "commitOrder": [],
            "assemblies": [], "events": [], "baselineUses": [],
            "ordinaryAssemblies": [], "ordinaryClasses": list(ordinary_classes)}


class CompleteGeneralDiagnosticContracts(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="r03-general-sidecar-")
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name).resolve()
        self.raw = self.dir / "raw.json"
        self.raw.write_text('{"kind":"R03IRPostPoisonEntryV1"}\n', encoding="utf-8")
        self.doc = sample()
        self.data = json.dumps(self.doc, sort_keys=True, separators=(",", ":")).encode()

    def make_sidecar(self, data=None):
        data = data if data is not None else self.data
        side = self.raw.with_name(self.raw.name + ".general.json")
        side.write_bytes(data)
        return f"{subject.PREFIX}{len(data)}:{zlib.crc32(data):08x}"

    def test_01_complete_inline_is_host_only(self):
        result = subject.verify(self.data.decode(), self.raw)
        self.assertEqual(result["transport"], "InlineWithin256KiB")
        self.assertIs(result["coherentVmEpochProven"], False)
        self.assertIs(result["runtimeAcceptance"], False)

    def test_02_real_size_sidecar_roundtrip(self):
        names = ("R03.Game.Namespace.Class" + str(i) + "X" * 48 for i in range(4000))
        self.doc["ordinaryClasses"] = [
            {"assemblyName": "UnityEngine.CoreModule", "typeName": name,
             "isInterpreter": False, "isConstructedGeneric": False,
             "usesStagedMetadata": False} for name in names]
        self.data = json.dumps(self.doc, sort_keys=True, separators=(",", ":")).encode()
        self.assertGreater(len(self.data), subject.TEXT_LIMIT)
        self.assertLess(len(self.data), subject.GENERAL_LIMIT)
        token = self.make_sidecar()
        actual = subject.verify(token, self.raw)
        self.assertEqual(actual["transport"], "FullPreopenedSidecar")
        self.assertEqual(actual["ordinaryClassCount"], 4000)
        self.assertEqual(actual["bytes"], len(self.data))

    def test_03_wrong_checksum(self):
        self.data = (self.data + b" " * subject.TEXT_LIMIT)[:subject.TEXT_LIMIT+40]
        desc = self.make_sidecar()
        with self.assertRaisesRegex(ValueError, "CRC"):
            subject.verify(desc[:-8] + "00000000", self.raw)

    def test_04_unclaimed_extra_sidecar_rejected(self):
        self.make_sidecar()
        with self.assertRaisesRegex(ValueError, "unclaimed sidecar"):
            subject.verify(json.dumps(self.doc), self.raw)

    def test_05_missing_canonical_raw_rejected(self):
        with self.assertRaisesRegex(ValueError, "actual canonical"):
            subject.verify(f"{subject.PREFIX}{subject.TEXT_LIMIT+1}:00000000", self.dir / "missing")

    def test_06_sidecar_size_disagreement(self):
        self.data = (self.data + b" " * subject.TEXT_LIMIT)[:subject.TEXT_LIMIT+50]
        token = self.make_sidecar()
        with self.assertRaisesRegex(ValueError, "wrong-sized"):
            subject.verify(token.replace(str(len(self.data)),str(len(self.data)+1)), self.raw)

    def test_07_sidecar_symlink_rejected(self):
        self.data = (self.data + b" " * subject.TEXT_LIMIT)[:subject.TEXT_LIMIT+50]
        token = self.make_sidecar()
        p = self.raw.with_name(self.raw.name + ".general.json")
        copy = self.dir / "copy"
        p.rename(copy)
        p.symlink_to(copy)
        with self.assertRaisesRegex(ValueError, "wrong-sized"):
            subject.verify(token, self.raw)

    def test_08_inline_oversize_rejected(self):
        with self.assertRaisesRegex(ValueError, "oversized"):
            subject.verify("X" * (subject.TEXT_LIMIT + 1), self.raw)

    def test_09_incomplete_json_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-object"):
            subject.verify('{"schemaVersion":1', self.raw)

    def test_10_terminal_state_required(self):
        self.doc["stateCode"] = 6
        with self.assertRaisesRegex(ValueError, "state"):
            subject.verify(json.dumps(self.doc), self.raw)

    def test_11_generation_disagreement_rejected(self):
        self.doc["classEnumerationGeneration"] = 5
        with self.assertRaisesRegex(ValueError, "generations"):
            subject.verify(json.dumps(self.doc), self.raw)

    def test_12_missing_array_rejected(self):
        del self.doc["ordinaryClasses"]
        with self.assertRaisesRegex(ValueError, "array"):
            subject.verify(json.dumps(self.doc), self.raw)

    def test_13_duplicate_json_field_rejected(self):
        source = json.dumps(self.doc)
        source = source[:-1] + ',"stateCode":9}'
        with self.assertRaisesRegex(ValueError, "duplicate"):
            subject.verify(source, self.raw)

    def test_14_descriptor_cannot_claim_oversized(self):
        with self.assertRaisesRegex(ValueError, "fixed bounds"):
            subject.verify(f"{subject.PREFIX}{subject.GENERAL_LIMIT + 1}:ffffffff", self.raw)

    def test_15_no_inferred_global_coherence(self):
        result = subject.verify(json.dumps(self.doc))
        self.assertEqual(result["result"],
                         "PassedCompleteByteBoundAndSchema_WithoutGlobalEpochProof")
        self.assertIs(result["R03Accepted"], False)

    def test_16_bad_sidecar_field_format(self):
        with self.assertRaisesRegex(ValueError, "descriptor"):
            subject.verify(f"{subject.PREFIX}{subject.TEXT_LIMIT+1}:NOTHEX!!", self.raw)


if __name__ == "__main__":
    unittest.main(verbosity=2)
