#!/usr/bin/env python3
"""Focused negative tests for the R01B strict capacity-report reader."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from r01b_capacity_inputs import validate_mixed_workload
from shadow_tools import VerificationError


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("r01b_capacity_verifier", HERE / "verify-r01b-capacity-result.py")
VERIFIER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VERIFIER)


def valid_native() -> dict:
    return {
        "schemaVersion": 2, "enabled": True, "profileVersion": 2, "maximumImageCount": 8192,
        "maximumDllBytes": 33554432, "usablePageCapacity": 524287, "chargedPageCeiling": 393215,
        "minimumFreePageMargin": 131072, "reservedPages": 0, "mappedPages": 0,
        "lifetimeReservedImageCount": 0, "remainingImageCount": 8192, "requiredImages": 0,
        "acceptedImages": 0, "firstFailingIndex": -1, "firstFailingSize": 0, "failureReason": "None",
        "fitsPreliminary": True, "runtimeFinalizationRequired": True, "aggregateInputDllBytes": 0,
        "aggregateInputDllBytesInformational": True, "ordinaryAllocatedCount": 0,
        "shadowAllocatedCount": 0, "reservedShadowImageCount": 0,
    }


def captured(native: dict) -> dict:
    return {
        "rawJson": json.dumps(native, separators=(",", ":")),
        "failureReason": native["failureReason"], "fitsPreliminary": native["fitsPreliminary"],
        "firstFailingIndex": native["firstFailingIndex"], "requiredImages": native["requiredImages"],
        "acceptedImages": native["acceptedImages"], "reservedPages": native["reservedPages"],
        "mappedPages": native["mappedPages"], "lifetimeReservedImageCount": native["lifetimeReservedImageCount"],
        "remainingImageCount": native["remainingImageCount"], "ordinaryAllocatedCount": native["ordinaryAllocatedCount"],
        "shadowAllocatedCount": native["shadowAllocatedCount"],
        "reservedShadowImageCount": native["reservedShadowImageCount"],
        "freeUsablePages": 524287 - native["reservedPages"],
    }


class CapacityReaderTests(unittest.TestCase):
    def test_rejects_mixed_manifest_schema_before_corpus_access(self) -> None:
        with tempfile.TemporaryDirectory(prefix="r01b-mixed-schema-") as temporary:
            root = Path(temporary)
            manifest = root / "manifest.json"
            manifest.write_text("{}", encoding="utf-8")
            with self.assertRaises(VerificationError):
                validate_mixed_workload(manifest, root, deep=False)

    def test_accepts_coherent_success(self) -> None:
        VERIFIER.capacity(captured(valid_native()), "valid")

    def test_rejects_duplicate_native_key(self) -> None:
        value = captured(valid_native())
        value["rawJson"] = value["rawJson"].replace('{"schemaVersion":2', '{"schemaVersion":2,"schemaVersion":2', 1)
        with self.assertRaises(VerificationError):
            VERIFIER.capacity(value, "duplicate")

    def test_rejects_success_with_failure_markers(self) -> None:
        native = valid_native()
        native.update(requiredImages=1, acceptedImages=1, firstFailingIndex=0,
                      firstFailingSize=61440, failureReason="ImageLimit")
        value = captured(native)
        with self.assertRaises(VerificationError):
            VERIFIER.capacity(value, "inconsistent")

    def test_rejects_boolean_encoded_as_integer(self) -> None:
        native = valid_native()
        native["enabled"] = 1
        with self.assertRaises(VerificationError):
            VERIFIER.capacity(captured(native), "typed")

    def test_rejects_captured_native_mismatch(self) -> None:
        value = captured(valid_native())
        value["remainingImageCount"] = 8191
        with self.assertRaises(VerificationError):
            VERIFIER.capacity(value, "mismatch")

    def test_rejects_lifetime_ledger_accounting_mismatch(self) -> None:
        native = valid_native()
        native["ordinaryAllocatedCount"] = 1
        with self.assertRaises(VerificationError):
            VERIFIER.capacity(captured(native), "ledger")

    def test_rejects_shadow_reservation_accounting_mismatch(self) -> None:
        native = valid_native()
        native["shadowAllocatedCount"] = 1
        with self.assertRaises(VerificationError):
            VERIFIER.capacity(captured(native), "shadow-ledger")

    def test_accepts_coherent_image_limit_failure(self) -> None:
        native = valid_native()
        native.update(lifetimeReservedImageCount=8192, remainingImageCount=0, reservedPages=8192,
                      requiredImages=1, acceptedImages=0, firstFailingIndex=0, firstFailingSize=61440,
                      failureReason="ImageLimit", fitsPreliminary=False, aggregateInputDllBytes=61440,
                      ordinaryAllocatedCount=8192)
        value = captured(native)
        VERIFIER.capacity(value, "limit")


if __name__ == "__main__":
    unittest.main(verbosity=2)
