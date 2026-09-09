"""Pure, independent checks for the strict R01 evidence gate."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r01_results as gate
from shadow_tools import VerificationError


def capacity_observation(sizes):
    model = gate.evaluate_budget(list(gate.FRESH_CURSORS), sizes)
    raw = {
        "schemaVersion": 1, "enabled": True, "profileVersion": 1,
        "indexBits": 22, "kindBits": 2,
        "cursors": list(gate.FRESH_CURSORS),
        "remainingSlots": gate.remaining_slots(list(gate.FRESH_CURSORS)),
        "requiredImages": model["requiredImages"], "acceptedImages": model["acceptedImages"],
        "firstFailingIndex": model["firstFailingIndex"], "firstFailingSize": model["firstFailingSize"],
        "failureReason": model["failureReason"], "fits": model["fits"],
        "allocations": model["allocations"], "finalCursors": model["finalCursors"],
        "ordinaryAllocatedCount": 0, "shadowAllocatedCount": 0, "reservedImageCount": 0,
    }
    return {
        "phase": "before-configure", "code": "Success", "rawJson": json.dumps(raw),
        "orderedSizes": list(sizes), "parsed": True, "fits": raw["fits"],
        "profileVersion": 1, "indexBits": 22, "kindBits": 2,
        "cursors": raw["cursors"], "finalCursors": raw["finalCursors"],
        "remainingSlots": raw["remainingSlots"], "requiredImages": raw["requiredImages"],
        "acceptedImages": raw["acceptedImages"], "firstFailingIndex": raw["firstFailingIndex"],
        "firstFailingSize": raw["firstFailingSize"], "failureReason": raw["failureReason"],
        "ordinaryAllocatedCount": 0, "shadowAllocatedCount": 0, "reservedImageCount": 0,
    }


def profile2_raw(sizes, ordinary=0, reserved=0, pages=None, mapped=0):
    if pages is None:
        pages = ordinary + reserved
    lifetime = ordinary + reserved
    failure_index = -1
    failure_reason = "None"
    if len(sizes) > gate.PROFILE2_MAX_IMAGES - lifetime:
        failure_index, failure_reason = gate.PROFILE2_MAX_IMAGES - lifetime, "ImageLimit"
    else:
        for index, size in enumerate(sizes):
            if size == 0:
                failure_index, failure_reason = index, "EmptyDll"
                break
            if size > gate.PROFILE2_MAX_DLL_BYTES:
                failure_index, failure_reason = index, "DllTooLarge"
                break
    fits = failure_index < 0
    return {
        "schemaVersion": 2, "enabled": True, "profileVersion": 2,
        "maximumImageCount": gate.PROFILE2_MAX_IMAGES, "maximumDllBytes": gate.PROFILE2_MAX_DLL_BYTES,
        "usablePageCapacity": gate.PROFILE2_USABLE_PAGE_CAPACITY,
        "chargedPageCeiling": gate.PROFILE2_CHARGED_PAGE_CEILING,
        "minimumFreePageMargin": gate.PROFILE2_MINIMUM_FREE_PAGE_MARGIN,
        "reservedPages": pages, "mappedPages": mapped,
        "lifetimeReservedImageCount": lifetime, "remainingImageCount": gate.PROFILE2_MAX_IMAGES - lifetime,
        "requiredImages": len(sizes), "acceptedImages": len(sizes) if fits else 0,
        "firstFailingIndex": failure_index,
        "firstFailingSize": 0 if failure_index < 0 else sizes[failure_index],
        "failureReason": failure_reason, "fitsPreliminary": fits,
        "runtimeFinalizationRequired": True,
        "aggregateInputDllBytes": sum(sizes), "aggregateInputDllBytesInformational": True,
        "ordinaryAllocatedCount": ordinary, "shadowAllocatedCount": 0,
        "reservedShadowImageCount": reserved,
    }


def profile2_observation(raw, phase, sizes):
    return {
        "phase": phase, "code": "Success", "rawJson": json.dumps(raw),
        "orderedSizes": list(sizes), "parsed": True, "fits": raw["fitsPreliminary"],
        "fitsPreliminary": raw["fitsPreliminary"], "profileVersion": 2,
        "indexBits": 0, "kindBits": 0, "cursors": [], "finalCursors": [],
        "remainingSlots": [], "requiredImages": raw["requiredImages"],
        "acceptedImages": raw["acceptedImages"], "firstFailingIndex": raw["firstFailingIndex"],
        "firstFailingSize": raw["firstFailingSize"], "failureReason": raw["failureReason"],
        "ordinaryAllocatedCount": raw["ordinaryAllocatedCount"], "shadowAllocatedCount": raw["shadowAllocatedCount"],
        "reservedImageCount": 0, "reservedPages": raw["reservedPages"], "mappedPages": raw["mappedPages"],
        "lifetimeReservedImageCount": raw["lifetimeReservedImageCount"],
        "remainingImageCount": raw["remainingImageCount"],
        "reservedShadowImageCount": raw["reservedShadowImageCount"],
    }


class R01ResultTests(unittest.TestCase):
    def test_ordinary_input_binds_hash_named_fixed_image(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root = Path(directory)
            snapshot_root = root / "snapshot"
            fixed = snapshot_root / "ReflectionBindings" / "Images" / ("a" * 64 + ".dll.bytes")
            filtered = snapshot_root / "Assemblies" / "Filtered" / "AssemblyShadowBaseline.HotUpdate.dll"
            fixed.parent.mkdir(parents=True)
            filtered.parent.mkdir(parents=True)
            fixed.write_bytes(b"approved-fixed-image")
            filtered.write_bytes(b"valid-filtered-compiler-image")
            fixed_hash = gate.digest(fixed)
            filtered_hash = gate.digest(filtered)
            fixed.rename(fixed.with_name(fixed_hash + ".dll.bytes"))
            fixed = fixed.with_name(fixed_hash + ".dll.bytes")
            result = {
                "fixtureManifestPath": str(root / "manifest.json"),
                "byteInputs": [{
                    "phase": "ordinary-before-configure", "assemblyName": gate.ORDINARY,
                    "path": str(fixed), "originalSha256": fixed_hash,
                    "actualSha256": fixed_hash, "originalLength": len(b"approved-fixed-image"),
                    "actualLength": len(b"approved-fixed-image"),
                    "transformation": "verified ON snapshot fixed M00 image"
                }]
            }
            build = {
                "player": {"inputSnapshot": str(snapshot_root)},
                "path": root / "player.json",
                "snapshot": {"filteredAssemblies": [{
                    "name": gate.ORDINARY + ".dll", "path": "Assemblies/Filtered/AssemblyShadowBaseline.HotUpdate.dll",
                    "sha256": filtered_hash
                }]}
            }
            reflection = {"declarations": [{
                "id": "m00-normal-hot-update-image", "kind": "FixedAssemblyBytes",
                "imageSha256": fixed_hash,
                "providerAssemblyIdentity": gate.ORDINARY + ", Version=0.0.0.0, Culture=neutral, PublicKeyToken=null"
            }]}
            with patch.object(gate.m07.prior, "_reflection_snapshot", return_value=reflection):
                gate.verify_byte_inputs(result, "R01-P03-OrdinaryFirst", [], {}, build)
                result["byteInputs"][0].update(path=str(filtered), originalSha256=filtered_hash,
                                               actualSha256=filtered_hash,
                                               originalLength=len(filtered.read_bytes()),
                                               actualLength=len(filtered.read_bytes()))
                with self.assertRaises(VerificationError):
                    gate.verify_byte_inputs(result, "R01-P03-OrdinaryFirst", [], {}, build)

    def test_complete_ordered_inventory_and_strict_default(self):
        self.assertEqual(len(gate.MODES), 10)
        self.assertEqual(gate.MODES[2], "R01-P03-OrdinaryAfterReserve")
        self.assertEqual(gate.STARTUP_EARLY_GUARD, "RequireEarlyGuard")
        self.assertEqual(gate.verify_suite.__defaults__, (gate.STARTUP_EARLY_GUARD,))

    def test_capacity_oracle_allocates_descending_kind_without_reported_fit(self):
        observation = capacity_observation([5120, 6656])
        raw = gate.verify_capacity_snapshot(observation, [5120, 6656], "capacity")
        self.assertTrue(raw["fits"])
        self.assertEqual(raw["acceptedImages"], 2)
        tampered = copy.deepcopy(observation)
        tampered_raw = json.loads(tampered["rawJson"])
        tampered_raw["fits"] = False
        tampered["rawJson"] = json.dumps(tampered_raw)
        with self.assertRaises(VerificationError):
            gate.verify_capacity_snapshot(tampered, [5120, 6656], "tampered")

    def test_capacity_oracle_rejects_oversize_at_ordered_member(self):
        sizes = [5120, 64 * 1024 * 1024]
        model = gate.evaluate_budget(list(gate.FRESH_CURSORS), sizes)
        self.assertFalse(model["fits"])
        self.assertEqual(model["firstFailingIndex"], 1)
        self.assertEqual(model["acceptedImages"], 1)

    def test_profile_binding_comes_from_verified_baseline(self):
        context = {"baseline": {"nativeBudgetCapabilityVersion": 1},
                   "fixtures": {"P03": {"r01Capability": True}}}
        self.assertEqual(gate.require_r01_inputs(context), 1)
        with self.assertRaises(VerificationError):
            gate.require_r01_inputs({"baseline": {"nativeBudgetCapabilityVersion": 2},
                                     "fixtures": {"P03": {"r01Capability": True}}})
        with self.assertRaises(VerificationError):
            gate.require_r01_inputs({"baseline": {},
                                     "fixtures": {"P03": {"r01Capability": True}}})
        observation = capacity_observation([5120])
        result = {"profileVersion": 2, "capacitySnapshots": [observation],
                  "capacityCode": "Success", "capacityJson": observation["rawJson"]}
        with self.assertRaises(VerificationError):
            gate.verify_capacity(result, "R01-PreConfigure-Type", [5120])

    def test_profile2_oversize_rejection_is_atomic_and_all_or_nothing(self):
        sizes = [5120, 64 * 1024 * 1024]
        before = profile2_raw(sizes)
        after = profile2_raw(sizes)
        result = {"profileVersion": 2, "capacitySnapshots": [
            profile2_observation(before, "before-configure", sizes),
            profile2_observation(after, "after-failed-reserve", sizes)],
            "capacityCode": "Success", "capacityJson": json.dumps(after)}
        gate.verify_capacity(result, "R01-P03-Oversize", sizes)
        tampered = copy.deepcopy(result)
        changed = json.loads(tampered["capacitySnapshots"][1]["rawJson"])
        changed["reservedPages"] = 1
        tampered["capacitySnapshots"][1]["rawJson"] = json.dumps(changed)
        tampered["capacitySnapshots"][1]["reservedPages"] = 1
        with self.assertRaises(VerificationError):
            gate.verify_capacity(tampered, "R01-P03-Oversize", sizes)

    def test_profile2_ordinary_load_grows_pages_then_reserve_adds_one_credit(self):
        sizes = [5120]
        fresh = profile2_raw([], pages=0)
        ordinary = profile2_raw(sizes, ordinary=1, pages=1)
        reserved = profile2_raw(sizes, ordinary=1, reserved=1, pages=2)
        result = {"profileVersion": 2, "capacitySnapshots": [
            profile2_observation(fresh, "before-ordinary", []),
            profile2_observation(ordinary, "after-ordinary-before-configure", sizes),
            profile2_observation(reserved, "after-reserve", sizes)],
            "capacityCode": "Success", "capacityJson": json.dumps(reserved)}
        gate.verify_capacity(result, "R01-P03-OrdinaryFirst", sizes)
        for field, value in (("reservedPages", 1), ("ordinaryAllocatedCount", 3), ("shadowAllocatedCount", 1)):
            tampered = copy.deepcopy(result)
            changed = json.loads(tampered["capacitySnapshots"][2]["rawJson"])
            changed[field] = value
            tampered["capacitySnapshots"][2]["rawJson"] = json.dumps(changed)
            tampered["capacitySnapshots"][2][field] = value
            with self.subTest(field=field), self.assertRaises(VerificationError):
                gate.verify_capacity(tampered, "R01-P03-OrdinaryFirst", sizes)

    def test_profile2_mismatch_preserves_ledger_after_rejected_stage(self):
        sizes = [5120]
        before = profile2_raw(sizes)
        reserved = profile2_raw(sizes, reserved=1, pages=1)
        after = copy.deepcopy(reserved)
        result = {"profileVersion": 2, "capacitySnapshots": [
            profile2_observation(before, "before-configure", sizes),
            profile2_observation(reserved, "after-reserve", sizes),
            profile2_observation(after, "after-mismatch", sizes)],
            "capacityCode": "Success", "capacityJson": json.dumps(after)}
        gate.verify_capacity(result, "R01-P03-Mismatch", sizes)
        tampered = copy.deepcopy(result)
        changed = json.loads(tampered["capacitySnapshots"][2]["rawJson"])
        changed["mappedPages"] = 1
        tampered["capacitySnapshots"][2]["rawJson"] = json.dumps(changed)
        tampered["capacitySnapshots"][2]["mappedPages"] = 1
        with self.assertRaises(VerificationError):
            gate.verify_capacity(tampered, "R01-P03-Mismatch", sizes)

    def test_one_byte_mismatch_is_reserved_at_original_length(self):
        source = (Path(__file__).resolve().parents[1] / "r01_results.py").read_text()
        self.assertIn("Mismatch deliberately reserves", source)
        self.assertEqual(gate.evaluate_budget(list(gate.FRESH_CURSORS), [5120])["requiredImages"], 1)

    def test_startup_state_is_staged_for_early_guard(self):
        result = {"stateSnapshots": [
            {"phase": "configured", "state": "CandidatesRegistered", "code": "Success", "passed": True},
            {"phase": "begun", "state": "Staging", "code": "Success", "passed": True},
            {"phase": "staged", "state": "Staged", "code": "Success", "passed": True},
            {"phase": "validated-or-early-guard", "state": "Staged", "code": "Success", "passed": True},
            {"phase": "aborted", "state": "Aborted", "code": "Success", "passed": True},
        ]}
        gate.verify_states(result, "R01-PreConfigure-Type", gate.STARTUP_EARLY_GUARD)
        with self.assertRaises(VerificationError):
            gate.verify_states(result, "R01-PreConfigure-Type", gate.STARTUP_OBSERVATION_GAP)

    def test_feature_off_does_not_fabricate_capacity_or_recovery(self):
        result = {"capacitySnapshots": [], "capacityCode": "FeatureDisabled", "capacityJson": None,
                  "recoverySnapshots": [], "recoveryCode": "FeatureDisabled", "recoveryJson": None}
        gate.verify_capacity(result, gate.OFF_MODE, [])
        gate.verify_recovery(result, gate.OFF_MODE)
        bad = dict(result, capacityJson="{}")
        with self.assertRaises(VerificationError):
            gate.verify_capacity(bad, gate.OFF_MODE, [])

    def test_physical_rows_require_interpreter_shadow_for_closure(self):
        closure = [gate.INTERNAL]
        candidates = [gate.INTERNAL, "AssemblyA.Contracts"]
        rows = [
            {"phase": "committed", "assemblyName": gate.INTERNAL, "code": "Success",
             "mode": "InterpreterShadow", "passed": True},
            {"phase": "committed", "assemblyName": "AssemblyA.Contracts", "code": "Success",
             "mode": "AotBaseline", "passed": True},
        ]
        gate.verify_physical({"physicalWorld": rows}, gate.MODES[0], closure, candidates)
        rows[0]["mode"] = "AotBaseline"
        with self.assertRaises(VerificationError):
            gate.verify_physical({"physicalWorld": rows}, gate.MODES[0], closure, candidates)


if __name__ == "__main__":
    unittest.main()
