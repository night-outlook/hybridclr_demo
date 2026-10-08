#!/usr/bin/env python3
"""Focused negative tests for the R01B strict capacity-report reader."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "tests"))
import r01_early_capsule as early_capsule
import r01_early_results as early_results
from r01b_capacity_inputs import validate_mixed_workload
from shadow_tools import VerificationError
from test_r01_early_results import emit_receipt, make_capsule


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


def as_profile2(receipt: dict, data: dict) -> dict:
    """Project the existing synthetic early receipt onto the profile-2 wire schema."""
    value = json.loads(json.dumps(receipt))
    pages = mapped = 0
    for snapshot in value["snapshots"]:
        legacy = json.loads(snapshot["capacityJson"])
        phase = snapshot["phase"]
        sizes = snapshot["orderedSizes"]
        ordinary = legacy["ordinaryAllocatedCount"]
        shadow = legacy["shadowAllocatedCount"]
        reserved = legacy["reservedImageCount"]
        if phase == "after-reserve":
            pages += len(sizes)
        elif phase in ("after-ordinary-before-configure", "after-ordinary-after-reserve"):
            pages += 3
            mapped += 2
        elif phase == "after-stage":
            mapped += len(sizes)
        elif phase == "after-validate" and data["mode"] not in early_results.GUARD_MODES:
            pages += len(sizes) * 3
            mapped += len(sizes)
        elif phase == "after-commit":
            mapped += 1
        oversized = data["mode"] == "Oversize"
        profile2 = dict(
            schemaVersion=2, enabled=True, profileVersion=2, maximumImageCount=8192,
            maximumDllBytes=33554432, usablePageCapacity=524287, chargedPageCeiling=393215,
            minimumFreePageMargin=131072, reservedPages=pages, mappedPages=mapped,
            lifetimeReservedImageCount=ordinary + reserved, remainingImageCount=8192 - ordinary - reserved,
            requiredImages=len(sizes), acceptedImages=0 if oversized else len(sizes),
            firstFailingIndex=len(sizes) - 1 if oversized else -1,
            firstFailingSize=sizes[-1] if oversized else 0,
            failureReason="DllTooLarge" if oversized else "None", fitsPreliminary=not oversized,
            runtimeFinalizationRequired=True, aggregateInputDllBytes=sum(sizes),
            aggregateInputDllBytesInformational=True, ordinaryAllocatedCount=ordinary,
            shadowAllocatedCount=shadow, reservedShadowImageCount=reserved)
        snapshot["capacityJson"] = json.dumps(profile2)
        diagnostics = json.loads(snapshot["diagnosticsJson"])
        diagnostics.update(runtimeAbiVersion=2, metadataBudgetCapabilityVersion=2)
        snapshot["diagnosticsJson"] = json.dumps(diagnostics)
    for observer in value["observerSamples"] + [row["diagnostics"] for row in value["initializerEvents"]]:
        diagnostics = json.loads(observer["rawJson"])
        diagnostics.update(runtimeAbiVersion=2, metadataBudgetCapabilityVersion=2)
        observer["rawJson"] = json.dumps(diagnostics)
    return value


def startup_evidence(root: Path, mode: str) -> tuple[Path, Path, int]:
    """Create authenticated bounded evidence from the shared synthetic fixture emitter."""
    data = make_capsule(root, mode)
    capsule_path = root / (mode + ".capsule")
    early_capsule.write_capsule(capsule_path, data)
    receipt_path = root / (mode + ".json")
    receipt = as_profile2(emit_receipt(data, capsule_path, receipt_path), data)
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    return capsule_path, receipt_path, receipt["processId"]


def startup_launch(root: Path, capsule_path: Path, receipt_path: Path) -> dict:
    return {"capsulePath": str(capsule_path), "capsuleSha256": VERIFIER.digest(capsule_path),
            "earlyResultPath": str(receipt_path), "earlyResultSha256": VERIFIER.digest(receipt_path)}


class CapacityReaderTests(unittest.TestCase):
    def test_accepts_ordinary_baseline_startup_contract(self) -> None:
        with tempfile.TemporaryDirectory(prefix="r01b-baseline-startup-") as temporary:
            root = Path(temporary).resolve()
            capsule_path, receipt_path, process_id = startup_evidence(root, "Baseline")
            launch = startup_launch(root, capsule_path, receipt_path)
            mode, bound_capsule, bound_receipt = VERIFIER.startup_binding(launch, root / "launch.json", False)
            VERIFIER.verify_startup_receipt(bound_receipt, bound_capsule, mode, process_id)
            self.assertEqual(mode, "Baseline")

    def test_rejects_control_capsule_in_ordinary_startup(self) -> None:
        with tempfile.TemporaryDirectory(prefix="r01b-control-ordinary-") as temporary:
            root = Path(temporary).resolve()
            capsule_path, receipt_path, _ = startup_evidence(root, "Control")
            with self.assertRaises(VerificationError):
                VERIFIER.startup_binding(startup_launch(root, capsule_path, receipt_path), root / "launch.json", False)

    def test_preserves_control_startup_contract_for_mixed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="r01b-mixed-startup-") as temporary:
            root = Path(temporary).resolve()
            capsule_path, receipt_path, process_id = startup_evidence(root, "Control")
            launch = startup_launch(root, capsule_path, receipt_path)
            mode, bound_capsule, bound_receipt = VERIFIER.startup_binding(launch, root / "launch.json", True)
            VERIFIER.validate_startup_receipt_contract(bound_receipt, bound_capsule, mode, process_id)
            self.assertEqual(mode, "Control")

    def test_rejects_missing_startup_capsule(self) -> None:
        with tempfile.TemporaryDirectory(prefix="r01b-missing-startup-") as temporary:
            root = Path(temporary).resolve()
            capsule_path, receipt_path, _ = startup_evidence(root, "Baseline")
            launch = startup_launch(root, capsule_path, receipt_path)
            launch["capsulePath"] = ""
            with self.assertRaises(VerificationError):
                VERIFIER.startup_binding(launch, root / "launch.json", False)

    def test_rejects_forged_startup_process_id(self) -> None:
        with tempfile.TemporaryDirectory(prefix="r01b-forged-startup-") as temporary:
            root = Path(temporary).resolve()
            capsule_path, receipt_path, process_id = startup_evidence(root, "Baseline")
            mode, bound_capsule, bound_receipt = VERIFIER.startup_binding(
                startup_launch(root, capsule_path, receipt_path), root / "launch.json", False)
            with self.assertRaises(VerificationError):
                VERIFIER.validate_startup_receipt_contract(bound_receipt, bound_capsule, mode, process_id + 1)

    def test_rejects_operations_in_baseline_startup_receipt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="r01b-baseline-ops-") as temporary:
            root = Path(temporary).resolve()
            capsule_path, receipt_path, process_id = startup_evidence(root, "Baseline")
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["operations"] = [dict(phase="configure", code="Success", intCode=0,
                                           startedTicks=1, elapsedTicks=0)]
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            launch = startup_launch(root, capsule_path, receipt_path)
            mode, bound_capsule, bound_receipt = VERIFIER.startup_binding(launch, root / "launch.json", False)
            with self.assertRaises(VerificationError):
                VERIFIER.validate_startup_receipt_contract(bound_receipt, bound_capsule, mode, process_id)

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
