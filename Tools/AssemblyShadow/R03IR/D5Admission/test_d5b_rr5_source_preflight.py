#!/usr/bin/env python3
"""Adversarial RR5 source-only custody tests; cannot authorize a Local run."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import d5b_rr5_source_preflight as gate


class RR5SourcePreflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = gate.PROFILE.read_bytes()
        cls.proposal = gate.checked_profile(cls.raw)
        cls.c10_raw = (
            gate.ROOT.parent / "D5Probe" / "d5c10_link_source_pinset_v1.json"
        ).read_bytes()
        cls.c10 = gate.checked_c10_manifest(cls.c10_raw, cls.proposal)

    def reject_profile(self, mutate):
        p = copy.deepcopy(self.proposal)
        mutate(p)
        with self.assertRaises(gate.Rejected):
            gate.checked_profile(
                json.dumps(p, separators=(",", ":")).encode(),
                check_blob=False)

    def test_01_immutable_rr5_profile_blob(self):
        self.assertEqual(gate.git_blob(self.raw), gate.PROFILE_BLOB)
        self.assertEqual(self.proposal["reviewed"]["c10"],
                         "PassSourceProducerOnly")

    def test_02_immutable_rr5_c10_manifest(self):
        self.assertEqual(gate.git_blob(self.c10_raw), gate.MANIFEST_BLOB)
        self.assertEqual(self.c10["nativeWindowProtocolVersion"], 3)
        self.assertEqual(self.c10["receiptWireSchemaVersion"], 3)

    def test_03_exact_source_and_roster_counts(self):
        self.assertEqual(len(self.c10["nativeInstalledSources"]), 13)
        self.assertEqual(len(self.c10["isolatedOverlaySource"]), 3)
        self.assertEqual(len(gate.TUS), 5)
        self.assertEqual(len(gate.EXPORTS), 9)
        self.assertEqual(len(gate.HIST), 5)

    def test_04_profile_blob_any_byte_drift_rejected(self):
        with self.assertRaises(gate.Rejected):
            gate.checked_profile(self.raw + b" ")

    def test_05_missing_rr5_independent_pass_rejected(self):
        self.reject_profile(
            lambda p: p["reviewed"].__setitem__("c10", "Pending"))

    def test_06_stale_native_revision_rejected(self):
        for stale in ("3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699",
                      "8aa8d09319a89b55b2496bcc2c69ccc69cb57be9"):
            with self.subTest(stale=stale):
                self.reject_profile(lambda p:
                    p["reviewed"].__setitem__("il2cpp_plus", stale))

    def test_07_wrong_hybridclr_or_package_rejected(self):
        for role in ("hybridclr", "hybridclr_unity"):
            with self.subTest(role=role):
                self.reject_profile(lambda p:
                    p["reviewed"].__setitem__(role, "0" * 40))

    def test_08_self_reported_demo_latest_rejected(self):
        self.reject_profile(lambda p: p["reviewed"].__setitem__(
            "demoExecutionPolicy", "CallerSuppliedLatest"))

    def test_09_wrong_manifest_anchor_rejected(self):
        self.reject_profile(lambda p: p["exactSourceManifests"].__setitem__(
            "c10GitBlob", "0" * 40))

    def test_10_silent_host_allocator_inclusion_rejected(self):
        self.reject_profile(lambda p:
            p["nativeSourceRoster"]["translationUnits"].append(
                "NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp"))

    def test_11_extra_native_export_rejected(self):
        self.reject_profile(lambda p:
            p["nativeSourceRoster"]["cExports"].append("R03_D5_Fake"))

    def test_12_fake_native_compilation_rejected(self):
        self.reject_profile(lambda p:
            p["nativeSourceRoster"].__setitem__(
                "compiledTranslationUnitsObserved", 5))

    def test_13_fake_binary_link_rejected(self):
        self.reject_profile(lambda p:
            p["nativeSourceRoster"].__setitem__("linkedBinaryObserved", True))

    def test_14_fake_local_approval_rejected(self):
        for key, fake in (("approvedLocalHandoffGitBlob", "0" * 40),
                          ("d5bLocalExecution", "Authorized"),
                          ("WEB_TO_LOCAL", "OPEN"),
                          ("allowUnityOrPlayerExecution", True),
                          ("R03Accepted", True)):
            with self.subTest(key=key):
                self.reject_profile(lambda p:
                    p["authority"].__setitem__(key, fake))

    def test_15_player_evidence_fabrication_rejected(self):
        for key, fake in (("d5PlayerPassed", 1),
                          ("d5PlayerNoCoverage", 17),
                          ("actualUnityBuild", "Passed"),
                          ("actualIl2CppNativeLink", "Passed"),
                          ("realProcessPidAndExit", "Passed")):
            with self.subTest(key=key):
                self.reject_profile(lambda p:
                    p["evidence"].__setitem__(key, fake))

    def test_16_historical_b1_immutable_roster_rejected(self):
        self.reject_profile(lambda p:
            p["historicalBaseline"].__setitem__("oldB1SourceCount", 13))
        self.reject_profile(lambda p:
            p["historicalBaseline"].__setitem__("oldB1VmDeltaCount", 45))
        self.reject_profile(lambda p:
            p["historicalBaseline"].__setitem__(
                "historicalEvidenceAsComparatorOnly", False))

    def test_17_all_six_historical_roots_required(self):
        self.reject_profile(lambda p:
            p["requiredHistoricalRootRoles"].remove("b1Oneuse12"))

    def test_18_wrong_target_identity_rejected(self):
        self.reject_profile(lambda p:
            p["expectedLocalTarget"].__setitem__("unity", "2022.3.0f1"))
        self.reject_profile(lambda p:
            p["expectedLocalTarget"].__setitem__(
                "actualTargetToolchainVerified", True))

    def test_19_manifest_mutation_rejected(self):
        with self.assertRaises(gate.Rejected):
            gate.checked_c10_manifest(self.c10_raw + b"\n", self.proposal)

    def test_20_malformed_duplicate_json_rejected(self):
        with self.assertRaises(gate.Rejected):
            gate.read_object(b'{"duplicate":1,"duplicate":2}')

    def test_21_wrong_canonical_origin_rejected(self):
        self.assertFalse(gate.canonical_origin(
            "il2cpp_plus", "https://github.com/foreign/il2cpp_plus"))
        self.assertFalse(gate.canonical_origin(
            "hybridclr", "https://github.com/night-outlook/hybridclr_demo"))
        self.assertTrue(gate.canonical_origin(
            "hybridclr", "https://github.com/night-outlook/hybridclr.git"))

    def test_22_refuse_missing_demo_sha_before_git(self):
        with self.assertRaises(gate.Rejected):
            gate.inspect({}, "")

    def test_23_refuse_duplicated_source_checkout_roots(self):
        p = gate.ROOT
        roots = {r: p for r in gate.ROLES}
        with self.assertRaises(gate.Rejected):
            gate.inspect(roots, "a" * 40)

    def test_24_source_blob_is_content_addressed(self):
        a = b"original source"
        self.assertNotEqual(gate.git_blob(a), gate.git_blob(a + b"\n"))

    def test_25_checkout_wrong_revision_before_source_read(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d).resolve(strict=True)
            def git_check(root, *args):
                if args == ("rev-parse", "--show-toplevel"):
                    return str(root)
                if args == ("rev-parse", "HEAD"):
                    return "f" * 40
                raise AssertionError("Unexpected Git query: " + str(args))
            with mock.patch.object(gate, "git", side_effect=git_check):
                with self.assertRaises(gate.Rejected):
                    gate.checked_checkout(p, "il2cpp_plus",
                                          gate.PINS["il2cpp_plus"])

    def test_26_checkout_dirty_tree_is_not_admissible(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d).resolve(strict=True)
            def git_check(root, *args):
                record = {
                    ("rev-parse", "--show-toplevel"): str(root),
                    ("rev-parse", "HEAD"): gate.PINS["il2cpp_plus"],
                    ("remote", "get-url", "origin"):
                        "https://github.com/night-outlook/il2cpp_plus",
                    ("branch", "--show-current"): gate.BRANCH,
                    ("status", "--porcelain=v1", "--untracked-files=all"):
                        " M libil2cpp/vm/AssemblyShadow.cpp",
                }
                return record[args]
            with mock.patch.object(gate, "git", side_effect=git_check):
                with self.assertRaises(gate.Rejected):
                    gate.checked_checkout(p, "il2cpp_plus",
                                          gate.PINS["il2cpp_plus"])

    def test_27_report_does_not_forge_player_or_authority(self):
        self.assertEqual(self.proposal["evidence"]["d5PlayerNoCoverage"], 18)
        self.assertIsNone(
            self.proposal["authority"]["approvedLocalHandoffGitBlob"])
        self.assertFalse(
            self.proposal["authority"]["allowUnityOrPlayerExecution"])


if __name__ == "__main__":
    unittest.main()
