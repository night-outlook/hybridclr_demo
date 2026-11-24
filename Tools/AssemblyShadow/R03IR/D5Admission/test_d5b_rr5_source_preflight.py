#!/usr/bin/env python3
"""Adversarial RR5 source-only custody tests; cannot authorize a Local run."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
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

    # All Git fixtures below are TEMPORARY synthetic repositories, not an
    # authenticated real checkout or a Local Validation product.
    def _git_fixture(self, files: dict[str, bytes]):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name).resolve(strict=True) / "repo"
        root.mkdir()
        for name, raw in files.items():
            p = root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
        subprocess.run(["git", "init", "-q", str(root)],
                       check=True, capture_output=True, text=True)
        subprocess.run(["git", "-C", str(root), "add", "."],
                       check=True, capture_output=True, text=True)
        subprocess.run(["git", "-C", str(root),
                        "-c", "user.name=RR5 Source Host",
                        "-c", "user.email=rr5-host@example.invalid",
                        "commit", "-q", "-m", "synthetic Git source fixture"],
                       check=True, capture_output=True, text=True)
        return root

    def _all_pinned_git_fixtures(self):
        # This copies reviewed CI checkout bytes into isolated temporary Git
        # repositories, then exercises the REAL checked_source_blob and
        # HEAD:path Git-blob join. Only pinned HEAD/remote admission is mocked.
        demo = gate.ROOT.parents[3]
        native_env = os.environ.get("R03_D5B_RR5_NATIVE_ROOT")
        if not native_env:
            raise RuntimeError("Set R03_D5B_RR5_NATIVE_ROOT to a reviewed source checkout")
        native = Path(native_env).resolve(strict=True)
        wanted = {role: {} for role in gate.ROLES}
        for path, blob in self.c10["nativeInstalledSources"].items():
            rel = "libil2cpp/" + path
            wanted["il2cpp_plus"][rel] = (native / rel, blob)
        for path, blob in self.c10["isolatedOverlaySource"].items():
            wanted["hybridclr_demo"][path] = (demo / path, blob)
        for path, blob in gate.EVIDENCE_PRODUCER_BLOBS.items():
            wanted["hybridclr_demo"][path] = (demo / path, blob)
        for path, blob in gate.HIST.items():
            wanted["hybridclr_demo"][path] = (demo / path, blob)
        for path, blob in (
                ("Tools/AssemblyShadow/R03IR/D5Admission/" + gate.PROFILE.name,
                 gate.PROFILE_BLOB),
                (self.proposal["exactSourceManifests"]["c10Path"],
                 gate.MANIFEST_BLOB)):
            wanted["hybridclr_demo"][path] = (demo / path, blob)
        roots = {}
        for role in gate.ROLES:
            material = {}
            for path, (src, blob) in wanted[role].items():
                raw = src.read_bytes()
                self.assertEqual(gate.git_blob(raw), blob,
                                 "Wrong source fixture blob: " + role + "/" + path)
                material[path] = raw
            # Empty hybridclr/package fixtures are deliberate: these test
            # source-file authentication, not real remote admission.
            if material:
                roots[role] = self._git_fixture(material)
            else:
                temp = tempfile.TemporaryDirectory()
                self.addCleanup(temp.cleanup)
                roots[role] = Path(temp.name).resolve(strict=True)
        return roots

    def test_28_real_git_blob_positive(self):
        content = b"rr5 exact source bytes\n"
        root = self._git_fixture({"source/probe.txt": content})
        actual = gate.git_blob(content)
        self.assertEqual(gate.checked_source_blob(
            root, "source/probe.txt", actual), actual)

    def test_29_real_git_blob_dirty_worktree_rejected(self):
        content = b"pinned source\n"
        root = self._git_fixture({"source/probe.txt": content})
        (root / "source/probe.txt").write_bytes(content + b"mutated\n")
        with self.assertRaises(gate.Rejected):
            gate.checked_source_blob(
                root, "source/probe.txt", gate.git_blob(content))

    def test_30_real_git_head_blob_mismatch_rejected(self):
        original = b"recorded HEAD source\n"
        changed = b"different working tree source\n"
        root = self._git_fixture({"source/probe.txt": original})
        (root / "source/probe.txt").write_bytes(changed)
        with self.assertRaises(gate.Rejected):
            # The worktree matches this caller's hash but HEAD:path does not.
            gate.checked_source_blob(
                root, "source/probe.txt", gate.git_blob(changed))

    def test_31_real_git_symlink_and_path_escape_rejected(self):
        content = b"exact bytes\n"
        root = self._git_fixture({"source/probe.txt": content})
        (root / "source/link.txt").symlink_to(
            root / "source/probe.txt")
        for path in ("source/link.txt", "../probe.txt",
                     str(root / "source/probe.txt")):
            with self.subTest(path=path):
                with self.assertRaises(gate.Rejected):
                    gate.checked_source_blob(root, path, gate.git_blob(content))

    def test_32_full_inspect_positive_then_native_mutation_rejected(self):
        roots = self._all_pinned_git_fixtures()
        # Deliberately bypass only remote/canonical checkout identity:
        # these temporary repos have test SHAs, never source acceptance.
        with mock.patch.object(gate, "checked_checkout"):
            result = gate.inspect(roots, "a" * 40)
            self.assertEqual(result["checkedNativeAndOverlayFiles"], 16)
            self.assertEqual(result["checkedEvidenceProducerFiles"], 14)
            self.assertTrue(result["linkSourceBlobsMatched"])
            self.assertTrue(result["receiptProducerBlobsMatched"])
            self.assertEqual(result["D5BLocalExecution"], "NotAuthorized")
            source = roots["il2cpp_plus"] / "libil2cpp/vm/AssemblyShadow.cpp"
            source.write_bytes(source.read_bytes() + b"\n// mutated native source\n")
            with self.assertRaises(gate.Rejected):
                gate.inspect(roots, "a" * 40)

    def test_33_full_inspect_parser_drift_rejected(self):
        roots = self._all_pinned_git_fixtures()
        with mock.patch.object(gate, "checked_checkout"):
            self.assertEqual(gate.inspect(
                roots, "a" * 40)["checkedEvidenceProducerFiles"], 14)
            parser = roots["hybridclr_demo"] / (
                "Tools/AssemblyShadow/R03IR/D5Probe/d5_c10_native_receipt.py")
            parser.write_bytes(parser.read_bytes() + b"\n# changed receipt logic\n")
            with self.assertRaises(gate.Rejected):
                gate.inspect(roots, "a" * 40)

    def test_34_full_inspect_host_workflow_drift_rejected(self):
        roots = self._all_pinned_git_fixtures()
        with mock.patch.object(gate, "checked_checkout"):
            self.assertTrue(gate.inspect(
                roots, "a" * 40)["receiptProducerBlobsMatched"])
            workflow = roots["hybridclr_demo"] / (
                ".github/workflows/r03-b2-d5-c10-window-source-host.yml")
            workflow.write_bytes(workflow.read_bytes() + b"\n# changed producer\n")
            with self.assertRaises(gate.Rejected):
                gate.inspect(roots, "a" * 40)

    def test_35_verifier_noop_does_not_fake_a_full_inspect(self):
        roots = self._all_pinned_git_fixtures()
        with mock.patch.object(gate, "checked_checkout"), mock.patch.object(
                gate, "checked_source_blob", return_value=None):
            with self.assertRaises(gate.Rejected):
                gate.inspect(roots, "a" * 40)

    def test_36_mutant_source_verifier_kills_negative_test(self):
        # Mutation testing: the *test runner* must observe a FAILURE when
        # checked_source_blob is artificially disabled, not a success count.
        mutant = RR5SourcePreflight(
            "test_29_real_git_blob_dirty_worktree_rejected")
        result = unittest.TestResult()
        with mock.patch.object(gate, "checked_source_blob", return_value=None):
            mutant.run(result)
        self.assertFalse(result.wasSuccessful())
        self.assertEqual(len(result.failures), 1)
        self.assertFalse(result.errors)


if __name__ == "__main__":
    unittest.main()
