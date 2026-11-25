#!/usr/bin/env python3
"""Prospective D5-B admission tests. No real Unity, Player, Local handoff."""
from __future__ import annotations

import copy
import hashlib
import inspect as source_inspect
import io
import json
import os
import stat
import sys
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock

import d5b_local_admission as gate


class _R5DeliveryFaultStream(io.StringIO):
    """Synthetic response sink; filesystem writes still use the real writer."""

    def __init__(self, *, write_fault=None, flush_fault=False):
        super().__init__()
        self.write_fault = write_fault
        self.flush_fault = flush_fault
        self.write_attempts = 0
        self.flush_attempts = 0

    def write(self, value):
        self.write_attempts += 1
        if (self.write_fault == "always" or
                self.write_fault == "first" and self.write_attempts == 1):
            raise OSError(5, "synthetic response write failure")
        return super().write(value)

    def flush(self):
        self.flush_attempts += 1
        if self.flush_fault:
            raise OSError(5, "synthetic response flush failure after bytes")
        return super().flush()


class D5BLocalSourceOnly(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.parent = Path(self.tmp.name).resolve(strict=True)
        self.workspace = self.parent / "workspace"
        self.workspace.mkdir()
        self.roots = {}
        for role in gate.ROLES:
            p = self.workspace / role
            p.mkdir()
            self.roots[role] = p
        self.historical = {
            "originalS": self.parent / "original-S",
            "b1EvidenceBase": self.workspace / "old-evidence",
        }
        self.historical["originalS"].mkdir()
        self.historical["b1EvidenceBase"].mkdir()
        for role, name in (
            ("b1Oneuse12", "oneuse-12"),
            ("b1NativeHostRaw", "oneuse-12-native-host-raw"),
            ("b1B2HostRaw", "oneuse-12-b2-host-raw"),
            ("b1Preflight", "Preflight-NativeB1-12"),
        ):
            p = self.historical["b1EvidenceBase"] / name
            p.mkdir()
            self.historical[role] = p
        self.evidence = self.parent / "external-results"
        self.evidence.mkdir()
        self.oneuse = "R03-B2-D5-source-only-001"
        self.plan = gate.read_plan()
        self.pins = {"hybridclr_demo": "a" * 40, **gate.source.PINS}
        self.unity = self.parent / "Unity"
        self.unity.write_bytes(b"synthetic test-only Unity executable")
        self.unity.chmod(0o755)
        self.sdk = self.parent / "MacOSX.sdk"
        self.sdk.mkdir()
        self.clang = self.parent / "clang"
        self.clang.write_bytes(b"synthetic clang executable")
        self.clang.chmod(0o755)

    def request(self, **changes):
        data = {
            "workspace": str(self.workspace),
            "historicalRoots": {k: str(v) for k, v in self.historical.items()},
            "evidenceParent": str(self.evidence),
            "oneuseName": self.oneuse,
            "unity": str(self.unity),
            "sourcePins": dict(self.pins),
        }
        data.update(changes)
        return data

    def fake_admission(self):
        return {
            "schemaVersion": 1,
            "kind": "R03D5BLocalAdmissionInspectionV1",
            "result": "ReadOnlyLocalAdmissionInspected_ExecutionStillUnauthorized",
            "sourcePins": dict(self.pins),
            "candidate": str(self.evidence / self.oneuse),
            "workspace": str(self.workspace),
            "source": {"remoteHeads": dict(self.pins), "result":
                       "LocalExactGitAndLiveRemoteSourceOnly"},
            "host": {"unitySha256": gate.sha256(self.unity),
                     "unityExecutable": str(self.unity),
                     "platform": "macOS", "architecture": "arm64",
                     "xcodeVersionOutput": "Xcode 15.4",
                     "macosSdkPath": str(self.sdk),
                     "macosClangPath": str(self.clang),
                     "xcodeLicenseChecked": True},
            "originalS": {"path": str(self.historical["originalS"])},
            "historicalRootCount": 6,
            "historicalRoots": {k: str(v) for k, v in self.historical.items()},
            "custodyIdentity": {
                "parent": gate.directory_identity(self.evidence),
                "history": {k: gate.directory_identity(v)
                            for k, v in self.historical.items()},
                "sources": {k: gate.directory_identity(v)
                            for k, v in self.roots.items()},
            },
        }

    def fake_approval(self):
        return {
            **self.request(),
            "unitySha256": gate.sha256(self.unity),
        }

    def test_01_exact_plan_git_blob(self):
        self.assertEqual(
            gate.git_blob(gate.PLAN.read_bytes()), gate.PLAN_BLOB)

    def test_02_plan_source_provenance_and_r2_gate(self):
        a = self.plan["sourceAuthority"]
        self.assertEqual(a["sourcePreflightIndependentReview"],
                         "PassSourcePreflightOnly")
        self.assertEqual(a["sourcePreflightCodeCommit"],
                         gate.REVIEWED_SOURCE_CODE)
        self.assertEqual(a["sourcePreflightProposalGitBlob"],
                         gate.source.PROFILE_BLOB)
        self.assertEqual(a["sourcePreflightReviewGitBlob"],
                         gate.R2_REVIEW_BLOB)

    def test_03_all_18_real_player_cases_no_coverage(self):
        self.assertEqual(self.plan["producerScope"]["d5PlayerCells"],
                         ["D5-C%02d" % i for i in range(1, 19)])
        self.assertEqual(self.plan["producerScope"]["d5PlayerCellsPassed"], 0)
        self.assertEqual(self.plan["producerScope"]["d5PlayerCellsNoCoverage"], 18)

    def test_04_no_approval_authority_in_any_plan_or_code(self):
        self.assertIsNone(gate.APPROVED_EXECUTION_ENVELOPE_BLOB)
        self.assertIsNone(
            self.plan["authorization"]["approvedEnvelopeGitBlob"])
        self.assertFalse(self.plan["authorization"]["allowNativeBuild"])
        self.assertFalse(self.plan["authorization"]["allowPlayerLaunch"])

    def test_05_duplicate_plan_json_key_rejected(self):
        with self.assertRaises(gate.Rejected):
            gate.parse_json(b'{"x":1,"x":2}')

    def test_06_valid_proposed_root_custody_read_only(self):
        r = gate.check_custody(
            self.workspace, self.historical, self.evidence, self.oneuse)
        self.assertEqual(r["historicalRootsChecked"], 6)
        self.assertEqual(r["candidate"], self.evidence / self.oneuse)
        self.assertFalse(r["candidate"].exists())

    def test_07_missing_history_role_rejected(self):
        wrong = dict(self.historical)
        wrong.pop("b1Preflight")
        with self.assertRaises(gate.Rejected):
            gate.check_custody(self.workspace, wrong,
                               self.evidence, self.oneuse)

    def test_08_historical_base_relationship_rejected(self):
        wrong = dict(self.historical)
        p = self.parent / "outside-b1"
        p.mkdir()
        wrong["b1Oneuse12"] = p
        with self.assertRaises(gate.Rejected):
            gate.check_custody(self.workspace, wrong,
                               self.evidence, self.oneuse)

    def test_09_duplicate_historical_role_rejected(self):
        wrong = dict(self.historical)
        wrong["b1Preflight"] = wrong["b1Oneuse12"]
        with self.assertRaises(gate.Rejected):
            gate.check_custody(self.workspace, wrong,
                               self.evidence, self.oneuse)

    def test_10_workspace_symlink_alias_rejected(self):
        alias = self.parent / "workspace-alias"
        alias.symlink_to(self.workspace, target_is_directory=True)
        with self.assertRaises(gate.Rejected):
            gate.check_custody(alias, self.historical, self.evidence,
                               self.oneuse)

    def test_11_evidence_parent_under_old_b1_rejected(self):
        p = self.historical["b1EvidenceBase"] / "future-evidence"
        p.mkdir()
        with self.assertRaises(gate.Rejected):
            gate.check_custody(self.workspace, self.historical, p,
                               self.oneuse)

    def test_12_evidence_parent_under_source_rejected(self):
        p = self.workspace / "unexpected-output-parent"
        p.mkdir()
        with self.assertRaises(gate.Rejected):
            gate.check_custody(self.workspace, self.historical, p,
                               self.oneuse)

    def test_13_existing_oneuse_output_rejected(self):
        (self.evidence / self.oneuse).mkdir()
        with self.assertRaises(gate.Rejected):
            gate.check_custody(self.workspace, self.historical,
                               self.evidence, self.oneuse)

    def test_14_symlink_oneuse_output_rejected(self):
        (self.evidence / self.oneuse).symlink_to(
            self.historical["b1Oneuse12"], target_is_directory=True)
        with self.assertRaises(gate.Rejected):
            gate.check_custody(self.workspace, self.historical,
                               self.evidence, self.oneuse)

    def test_15_noncanonical_output_name_rejected(self):
        for name in ("../R03-B2-D5-other", "R03-B2-D5-",
                     "R03-B2-D5-123/other"):
            with self.subTest(name=name):
                with self.assertRaises(gate.Rejected):
                    gate.check_custody(self.workspace, self.historical,
                                       self.evidence, name)

    def test_16_original_s_must_be_outside_active_checkout(self):
        wrong = dict(self.historical)
        wrong["originalS"] = self.roots["hybridclr_demo"]
        with self.assertRaises(gate.Rejected):
            gate.check_custody(self.workspace, wrong,
                               self.evidence, self.oneuse)

    def test_17_parse_exact_single_remote_ref(self):
        sha = "a" * 40
        self.assertEqual(gate.exact_remote_head(
            sha + "\trefs/heads/" + gate.BRANCH, sha), sha)

    def test_18_stale_remote_ref_rejected(self):
        with self.assertRaises(gate.Rejected):
            gate.exact_remote_head(
                "b" * 40 + "\trefs/heads/" + gate.BRANCH, "a" * 40)

    def test_19_wrong_remote_branch_rejected(self):
        with self.assertRaises(gate.Rejected):
            gate.exact_remote_head("a" * 40 + "\trefs/heads/main",
                                   "a" * 40)

    def test_20_ambiguous_remote_ref_lines_rejected(self):
        line = "a" * 40 + "\trefs/heads/" + gate.BRANCH
        with self.assertRaises(gate.Rejected):
            gate.exact_remote_head(line + "\n" + line, "a" * 40)

    def test_21_malformed_remote_sha_rejected(self):
        with self.assertRaises(gate.Rejected):
            gate.exact_remote_head("abc\trefs/heads/" + gate.BRANCH,
                                   "a" * 40)

    def test_22_original_s_clean_source_record(self):
        def git_call(root, *args):
            table = {
                ("rev-parse", "--show-toplevel"): str(root),
                ("rev-parse", "HEAD"): gate.ORIGINAL_S,
                ("status", "--porcelain=v1", "--untracked-files=all"): "",
                ("remote", "get-url", "origin"):
                    "https://github.com/night-outlook/hybridclr_demo.git",
            }
            return table[args]
        with mock.patch.object(gate, "git", side_effect=git_call):
            x = gate.inspect_original_s(self.historical["originalS"])
        self.assertEqual(x["commit"], gate.ORIGINAL_S)
        self.assertFalse(x["actualPlayerProof"])

    def test_23_original_s_wrong_sha_rejected(self):
        with mock.patch.object(gate, "git", return_value="f" * 40):
            with self.assertRaises(gate.Rejected):
                gate.inspect_original_s(self.historical["originalS"])

    def test_24_host_must_be_macos_arm64(self):
        with mock.patch.object(gate.sys, "platform", "linux"):
            with self.assertRaises(gate.Rejected):
                gate.inspect_machine(self.unity, self.evidence, min_free_gib=0)

    def _fake_xcode_read(self, argv, *, allow_empty=False):
        if argv == ["xcodebuild", "-version"]:
            return "Xcode 15.4\nBuild version 15F31d"
        if argv[-1] == "--show-sdk-path":
            return str(self.sdk)
        if argv[-1] == "clang":
            return str(self.clang)
        if argv == ["xcodebuild", "-license", "check"]:
            return "Xcode license accepted"
        raise AssertionError("Unexpected Xcode read-only query: " + str(argv))

    def test_25_machine_preview_does_not_launch_unity(self):
        with mock.patch.object(gate.sys, "platform", "darwin"), \
             mock.patch.object(gate.platform, "machine", return_value="arm64"), \
             mock.patch.object(gate.shutil, "which", return_value="/usr/bin/tool"), \
             mock.patch.object(gate.shutil, "disk_usage",
                               return_value=SimpleNamespace(free=25 * 1024**3)), \
             mock.patch.object(gate, "read_only_host_tool",
                               side_effect=self._fake_xcode_read), \
             mock.patch.object(gate.subprocess, "Popen",
                               side_effect=AssertionError("Unity must not launch")):
            report = gate.inspect_machine(
                self.unity, self.evidence, min_free_gib=20)
        self.assertEqual(report["unitySha256"], gate.sha256(self.unity))
        self.assertEqual(report["actualUnityVersionVerified"], "NotRun")
        self.assertEqual(report["macosSdkPath"], str(self.sdk))
        self.assertTrue(report["xcodeLicenseChecked"])

    def test_26_machine_disk_threshold_rejected(self):
        with mock.patch.object(gate.sys, "platform", "darwin"), \
             mock.patch.object(gate.platform, "machine", return_value="arm64"), \
             mock.patch.object(gate.shutil, "which", return_value="/usr/bin/tool"), \
             mock.patch.object(gate.shutil, "disk_usage",
                               return_value=SimpleNamespace(free=1 * 1024**3)):
            with self.assertRaises(gate.Rejected):
                gate.inspect_machine(self.unity, self.evidence,
                                     min_free_gib=20)

    def test_27_live_source_join_uses_four_exact_refs(self):
        expected = {
            "result": "RR5PinnedGitSourceVerified_NoLocalExecution",
            "checkedNativeAndOverlayFiles": 16,
            "checkedEvidenceProducerFiles": 14,
            "checkedHistoricalComparators": 5,
            "receiptProducerBlobsMatched": True,
            "linkSourceBlobsMatched": True,
        }
        calls = []
        def git_read(root, *args):
            role = root.name
            calls.append((role, args))
            if args[0] == "ls-remote":
                return ((self.pins[role]) + "\trefs/heads/" + gate.BRANCH)
            if args[0] == "merge-base":
                return ""
            raise AssertionError("Unexpected Git argument")
        with mock.patch.object(gate.source, "inspect", return_value=expected), \
             mock.patch.object(gate.source, "checked_source_blob",
                               return_value=gate.R2_REVIEW_BLOB), \
             mock.patch.object(gate, "git", side_effect=git_read):
            result = gate.inspect_source_and_remote(
                self.roots, self.pins["hybridclr_demo"])
        self.assertEqual(result["remoteHeads"], self.pins)
        self.assertEqual(sum(args[0] == "ls-remote" for _, args in calls), 4)
        self.assertTrue(any(args[0] == "merge-base" for _, args in calls))
        self.assertFalse(result["actualBeeOrPlayerProven"])

    def test_28_live_remote_sha_drift_rejected(self):
        positive = {
            "result": "RR5PinnedGitSourceVerified_NoLocalExecution",
            "checkedNativeAndOverlayFiles": 16,
            "checkedEvidenceProducerFiles": 14,
            "checkedHistoricalComparators": 5,
            "receiptProducerBlobsMatched": True,
            "linkSourceBlobsMatched": True,
        }
        with mock.patch.object(gate.source, "inspect", return_value=positive), \
             mock.patch.object(gate.source, "checked_source_blob",
                               return_value=gate.R2_REVIEW_BLOB), \
             mock.patch.object(gate, "git", return_value=
                               "b"*40+"\trefs/heads/"+gate.BRANCH):
            with self.assertRaises(gate.Rejected):
                gate.inspect_source_and_remote(
                    self.roots, self.pins["hybridclr_demo"])

    def test_29_reject_source_gate_missing_receipt_producer(self):
        incomplete = {
            "result": "RR5PinnedGitSourceVerified_NoLocalExecution",
            "checkedNativeAndOverlayFiles": 16,
            "checkedEvidenceProducerFiles": 0,
            "checkedHistoricalComparators": 5,
            "receiptProducerBlobsMatched": False,
            "linkSourceBlobsMatched": True,
        }
        with mock.patch.object(gate.source, "inspect", return_value=incomplete):
            with self.assertRaises(gate.Rejected):
                gate.inspect_source_and_remote(
                    self.roots, self.pins["hybridclr_demo"])

    def test_30_approval_requires_immutable_compile_time_blob(self):
        self.assertIsNone(gate.APPROVED_EXECUTION_ENVELOPE_BLOB)
        with self.assertRaises(gate.Rejected):
            gate.approved_envelope(json.dumps({
                "userLocalExecutionApproval": "ExplicitlyApproved"
            }).encode("utf-8"))

    def test_31_approved_envelope_fake_status_cannot_open(self):
        data = {
            "schemaVersion": 1,
            "kind": "R03D5BApprovedDryAdmissionEnvelopeV1",
            "sourcePins": self.pins,
            "userLocalExecutionApproval": "ExplicitlyApproved",
            "WEB_TO_LOCAL": "OPEN_FOR_EXACT_D5B_DRY_ADMISSION_ONLY",
        }
        with self.assertRaises(gate.Rejected):
            gate.approved_envelope(json.dumps(data).encode())

    def test_32_oneuse_receipt_binds_exact_paths_and_unity(self):
        receipt = gate.oneuse_receipt(
            self.fake_approval(), self.fake_admission())
        self.assertEqual(receipt["result"],
                         "DryAdmissionRecorded_NoUnityOrPlayer")
        self.assertEqual(receipt["realPlayerCellsNoCoverage"], 18)

    def test_33_oneuse_receipt_wrong_unity_hash_rejected(self):
        approved = self.fake_approval()
        approved["unitySha256"] = "0" * 64
        with self.assertRaises(gate.Rejected):
            gate.oneuse_receipt(approved, self.fake_admission())

    def test_34_oneuse_receipt_wrong_historical_s_rejected(self):
        approved = self.fake_approval()
        approved["historicalRoots"]["originalS"] = "/wrong/path"
        with self.assertRaises(gate.Rejected):
            gate.oneuse_receipt(approved, self.fake_admission())

    def test_35_oneuse_output_exclusivity_and_no_player(self):
        raw = self._synthetic_approved_bytes()
        observed = self.fake_admission()
        root = self.evidence / self.oneuse
        self.assertFalse(root.exists())
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)), \
             mock.patch.object(gate, "inspect", return_value=observed) as check:
            receipt = gate.seal_oneuse_dry_admission(raw, observed)
            with self.assertRaises(gate.Rejected):
                gate.seal_oneuse_dry_admission(raw, observed)
        self.assertIsNone(gate.APPROVED_EXECUTION_ENVELOPE_BLOB)
        self.assertGreaterEqual(check.call_count, 3)
        self.assertEqual(receipt["realPlayerCellsPassed"], 0)
        self.assertEqual(receipt["realPlayerCellsNoCoverage"], 18)
        cells = json.loads((root / "CELLS.json").read_text())
        self.assertEqual(len(cells["cells"]), 18)
        self.assertTrue(all(x["result"] == "NoCoverage" for x in cells["cells"]))
        manifest = json.loads((root / "MANIFEST.json").read_text())
        self.assertEqual(len(manifest["files"]), 4)
        self.assertEqual(
            {x["path"] for x in manifest["files"]},
            {"ADMISSION.json", "CELLS.json", "POSTFLIGHT.json",
             "LOCAL_BATCH_RESULT.json"})
        self.assertFalse((root / "FAILURE.json").exists())
        self.assertTrue((root / "LOCAL_BATCH_RESULT.json").exists())
        self.assertFalse((root / "LOCAL_BATCH_STAGING.json").exists())
        self.assertFalse((root / "INCOMPLETE.json").exists())
        self.assertEqual(gate.inspect_dry_receipt_structure(root)["filesChecked"], 5)

    def test_36_execute_cli_denied_before_envelope_or_filesystem(self):
        missing = self.parent / "missing-envelope.json"
        root = self.evidence / self.oneuse
        with mock.patch.object(gate, "approved_envelope",
                               side_effect=AssertionError("Must not read")), \
             mock.patch.object(gate, "inspect",
                               side_effect=AssertionError("Must not inspect")):
            code = gate.main([
                "--mode", "execute", "--approved-envelope", str(missing)])
        self.assertEqual(code, 2)
        self.assertFalse(root.exists())

    def test_37_preview_rejects_spurious_approval_envelope(self):
        code = gate.main(["--mode", "preview", "--approved-envelope",
                          str(self.parent / "fake.json")])
        self.assertEqual(code, 2)

    def test_38_preview_requires_complete_request(self):
        with mock.patch.object(gate, "check_custody",
                               side_effect=AssertionError("Do not inspect")):
            with self.assertRaises(gate.Rejected):
                gate.inspect({"workspace": str(self.workspace)})

    def test_39_read_only_inspect_preview_no_output(self):
        sample = self.request()
        custody = {
            "workspace": str(self.workspace),
            "roots": self.roots,
            "candidate": self.evidence / self.oneuse,
            "historicalRootsChecked": 6,
            "evidenceParentIdentity": gate.directory_identity(self.evidence),
            "historicalRootIdentities": {
                k: gate.directory_identity(p) for k, p in self.historical.items()},
            "sourceRootIdentities": {
                k: gate.directory_identity(p) for k, p in self.roots.items()},
        }
        with mock.patch.object(gate, "check_custody", return_value=custody), \
             mock.patch.object(gate, "inspect_original_s",
                               return_value={"path": str(self.historical["originalS"])}), \
             mock.patch.object(gate, "inspect_source_and_remote",
                               return_value={"result": "LocalExactGitAndLiveRemoteSourceOnly"}), \
             mock.patch.object(gate, "inspect_machine",
                               return_value={"unitySha256":gate.sha256(self.unity)}):
            r = gate.inspect(sample)
        self.assertEqual(r["result"],
                         "ReadOnlyLocalAdmissionInspected_ExecutionStillUnauthorized")
        self.assertFalse((self.evidence / self.oneuse).exists())
        self.assertEqual(r["D5BLocalExecution"], "NotAuthorized")

    def test_40_extra_source_pin_or_wrong_hybridclr_rejected(self):
        sample = self.request()
        sample["sourcePins"]["hybridclr"] = "0"*40
        with self.assertRaises(gate.Rejected):
            gate.inspect(sample)

    def test_41_wrong_second_historical_root_blocks_receipt(self):
        approved = self.fake_approval()
        approved["historicalRoots"]["b1NativeHostRaw"] = "/different/root"
        with self.assertRaises(gate.Rejected):
            gate.oneuse_receipt(approved, self.fake_admission())

    def test_42_unparseable_xcode_version_rejected(self):
        with mock.patch.object(gate.sys, "platform", "darwin"), \
             mock.patch.object(gate.platform, "machine", return_value="arm64"), \
             mock.patch.object(gate.shutil, "which", return_value="/usr/bin/tool"), \
             mock.patch.object(gate.shutil, "disk_usage",
                               return_value=SimpleNamespace(free=25 * 1024**3)), \
             mock.patch.object(gate, "read_only_host_tool",
                               return_value="not a real Xcode version"):
            with self.assertRaises(gate.Rejected):
                gate.inspect_machine(self.unity, self.evidence, min_free_gib=20)

    def test_43_xcode_license_rejection_fails_closed(self):
        def no_license(argv, *, allow_empty=False):
            if argv == ["xcodebuild", "-license", "check"]:
                raise gate.Rejected("License not accepted")
            return self._fake_xcode_read(argv)
        with mock.patch.object(gate.sys, "platform", "darwin"), \
             mock.patch.object(gate.platform, "machine", return_value="arm64"), \
             mock.patch.object(gate.shutil, "which", return_value="/usr/bin/tool"), \
             mock.patch.object(gate.shutil, "disk_usage",
                               return_value=SimpleNamespace(free=25 * 1024**3)), \
             mock.patch.object(gate, "read_only_host_tool", side_effect=no_license):
            with self.assertRaises(gate.Rejected):
                gate.inspect_machine(self.unity, self.evidence, min_free_gib=20)

    def test_44_non_string_historical_path_rejected_before_custody(self):
        data = self.request()
        data["historicalRoots"]["b1NativeHostRaw"] = 17
        with mock.patch.object(gate, "check_custody",
                               side_effect=AssertionError("Must not inspect")):
            with self.assertRaises(gate.Rejected):
                gate.inspect(data)

    def test_45_non_string_workspace_rejected_before_custody(self):
        data = self.request(workspace=1234)
        with mock.patch.object(gate, "check_custody",
                               side_effect=AssertionError("Must not inspect")):
            with self.assertRaises(gate.Rejected):
                gate.inspect(data)

    def test_46_standard_sdk_symlink_is_resolved_not_rejected(self):
        link = self.parent / "MacOSX-current.sdk"
        link.symlink_to(self.sdk, target_is_directory=True)
        def xcode(argv, *, allow_empty=False):
            if argv[-1] == "--show-sdk-path":
                return str(link)
            return self._fake_xcode_read(argv, allow_empty=allow_empty)
        with mock.patch.object(gate.sys, "platform", "darwin"), \
             mock.patch.object(gate.platform, "machine", return_value="arm64"), \
             mock.patch.object(gate.shutil, "which", return_value="/usr/bin/tool"), \
             mock.patch.object(gate.shutil, "disk_usage",
                               return_value=SimpleNamespace(free=25 * 1024**3)), \
             mock.patch.object(gate, "read_only_host_tool", side_effect=xcode):
            result = gate.inspect_machine(
                self.unity, self.evidence, min_free_gib=20)
        self.assertEqual(result["macosSdkPath"], str(self.sdk))
        self.assertTrue(result["xcodeLicenseChecked"])

    def _synthetic_approved_bytes(self, mutate=None):
        # These are temporary, mocked independent-review inputs for tests.
        # Current production APPROVED_EXECUTION_ENVELOPE_BLOB remains None.
        e = {
            **self.fake_approval(),
            "schemaVersion": 1,
            "kind": "R03D5BApprovedDryAdmissionEnvelopeV1",
            "branch": gate.BRANCH,
            "independentExecutableAdmissionReview":
                "PassedForD5BLocalDryAdmissionOnly",
            "userLocalExecutionApproval": "ExplicitlyApproved",
            "WEB_TO_LOCAL": "OPEN_FOR_EXACT_D5B_DRY_ADMISSION_ONLY",
            "scope": "NoUnityOrPlayerLaunch",
            "R03Accepted": False,
        }
        if mutate:
            mutate(e)
        return json.dumps(e, sort_keys=True).encode("utf-8")

    def test_47_test_only_frozen_envelope_semantics(self):
        raw = self._synthetic_approved_bytes()
        with mock.patch.object(
                gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                gate.git_blob(raw)):
            parsed = gate.approved_envelope(raw)
        self.assertEqual(parsed["sourcePins"], self.pins)
        self.assertIsNone(gate.APPROVED_EXECUTION_ENVELOPE_BLOB)

    def test_48_approved_envelope_one_byte_drift_rejected(self):
        raw = self._synthetic_approved_bytes()
        with mock.patch.object(
                gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                gate.git_blob(raw)):
            with self.assertRaises(gate.Rejected):
                gate.approved_envelope(raw + b" ")

    def test_49_test_only_approval_cannot_skip_user_review(self):
        raw = self._synthetic_approved_bytes(
            lambda e: e.__setitem__("userLocalExecutionApproval", "Pending"))
        with mock.patch.object(
                gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                gate.git_blob(raw)):
            with self.assertRaises(gate.Rejected):
                gate.approved_envelope(raw)

    def test_50_test_only_approval_cannot_change_native_pin(self):
        raw = self._synthetic_approved_bytes(
            lambda e: e["sourcePins"].__setitem__("il2cpp_plus", "0" * 40))
        with mock.patch.object(
                gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                gate.git_blob(raw)):
            with self.assertRaises(gate.Rejected):
                gate.approved_envelope(raw)

    def test_51_test_only_approval_cannot_omit_historical_root(self):
        raw = self._synthetic_approved_bytes(
            lambda e: e["historicalRoots"].pop("b1Preflight"))
        with mock.patch.object(
                gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                gate.git_blob(raw)):
            with self.assertRaises(gate.Rejected):
                gate.approved_envelope(raw)

    def test_52_test_only_approval_cannot_claim_player_scope(self):
        raw = self._synthetic_approved_bytes(
            lambda e: e.__setitem__("scope", "BuildAndRunUnityPlayer"))
        with mock.patch.object(
                gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                gate.git_blob(raw)):
            with self.assertRaises(gate.Rejected):
                gate.approved_envelope(raw)

    def test_53_direct_seal_helper_denied_without_reviewed_envelope(self):
        self.assertIsNone(gate.APPROVED_EXECUTION_ENVELOPE_BLOB)
        root = self.evidence / self.oneuse
        with self.assertRaises(gate.Rejected):
            gate.seal_oneuse_dry_admission(
                self.fake_approval(), self.fake_admission())
        self.assertFalse(root.exists())

    # R3 independent dry-admission review findings: test the actual inner
    # receipt boundary, not merely the current public null-approval guard.
    def test_54_inner_seal_rejects_different_approval_dict(self):
        raw = self._synthetic_approved_bytes()
        fake = self.fake_admission()
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)):
            with self.assertRaises(gate.Rejected):
                gate.seal_oneuse_dry_admission(self.fake_approval(), fake)
        self.assertFalse((self.evidence / self.oneuse).exists())

    def test_55_inner_seal_rejects_tampered_envelope_bytes(self):
        raw = self._synthetic_approved_bytes()
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)):
            with self.assertRaises(gate.Rejected):
                gate.seal_oneuse_dry_admission(raw + b" ", self.fake_admission())
        self.assertFalse((self.evidence / self.oneuse).exists())

    def test_56_prewrite_source_drift_refuses_output(self):
        raw = self._synthetic_approved_bytes()
        prior = self.fake_admission()
        changed = copy.deepcopy(prior)
        changed["source"]["remoteHeads"]["hybridclr_demo"] = "f" * 40
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)), \
             mock.patch.object(gate, "inspect", return_value=changed):
            with self.assertRaises(gate.Rejected):
                gate.seal_oneuse_dry_admission(raw, prior)
        self.assertFalse((self.evidence / self.oneuse).exists())

    def test_57_postflight_remote_drift_consumes_root_no_success(self):
        raw, before = self._synthetic_approved_bytes(), self.fake_admission()
        def inspect(request, *, expect_output_present=False):
            if expect_output_present:
                raise gate.Rejected("synthetic remote HEAD changed")
            return copy.deepcopy(before)
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)), \
             mock.patch.object(gate, "inspect", side_effect=inspect):
            with self.assertRaises(gate.PartialOutput) as cm:
                gate.seal_oneuse_dry_admission(raw, before)
        root = self.evidence / self.oneuse
        self.assertTrue(root.exists())
        self.assertTrue(cm.exception.files)
        self.assertIn("ADMISSION.json", cm.exception.files)
        self.assertFalse((root / "LOCAL_BATCH_RESULT.json").exists())
        self.assertEqual(json.loads((root / "FAILURE.json").read_text())[
            "result"], "FailedAfterPartialOutput")

    def test_58_final_source_drift_has_no_positive_receipt(self):
        raw, before = self._synthetic_approved_bytes(), self.fake_admission()
        count = []
        def inspect(request, *, expect_output_present=False):
            count.append(expect_output_present)
            if len(count) == 3:
                raise gate.Rejected("synthetic last-moment Git worktree drift")
            return copy.deepcopy(before)
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)), \
             mock.patch.object(gate, "inspect", side_effect=inspect):
            with self.assertRaises(gate.PartialOutput):
                gate.seal_oneuse_dry_admission(raw, before)
        root = self.evidence / self.oneuse
        self.assertEqual(count, [False, True, True])
        self.assertTrue((root / "FAILURE.json").is_file())
        self.assertFalse((root / "LOCAL_BATCH_RESULT.json").exists())

    def test_59_parent_alias_swap_cannot_write_to_history(self):
        raw, before = self._synthetic_approved_bytes(), self.fake_admission()
        real = gate._write_locked
        moved = self.parent / "moved-external-results"
        swapped = [False]
        def swap_parent(root_fd, name, value):
            if name == "ADMISSION.json" and not swapped[0]:
                swapped[0] = True
                os.rename(self.evidence, moved)
                self.evidence.symlink_to(
                    self.historical["b1Oneuse12"], target_is_directory=True)
            return real(root_fd, name, value)
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)), \
             mock.patch.object(gate, "inspect", return_value=before), \
             mock.patch.object(gate, "_write_locked", side_effect=swap_parent):
            with self.assertRaises(gate.PartialOutput):
                gate.seal_oneuse_dry_admission(raw, before)
        self.assertTrue(swapped[0])
        self.assertTrue((moved / self.oneuse / "ADMISSION.json").exists())
        self.assertTrue((moved / self.oneuse / "FAILURE.json").exists())
        self.assertFalse((self.historical["b1Oneuse12"] / self.oneuse).exists())

    def test_60_faults_at_each_exclusive_receipt_are_partial(self):
        targets = ("ADMISSION.json", "CELLS.json", "POSTFLIGHT.json",
                   "MANIFEST.json", "LOCAL_BATCH_STAGING.json")
        real = gate._write_locked
        for target in targets:
            with self.subTest(target=target):
                self.oneuse = ("R03-B2-D5-failure-" +
                               target.split(".")[0].replace("_", "-"))
                raw, before = self._synthetic_approved_bytes(), self.fake_admission()
                def failing(root_fd, name, data):
                    if name == target:
                        raise OSError("Synthetic ENOSPC at " + target)
                    return real(root_fd, name, data)
                with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                                       gate.git_blob(raw)), \
                     mock.patch.object(gate, "inspect", return_value=before), \
                     mock.patch.object(gate, "_write_locked", side_effect=failing):
                    with self.assertRaises(gate.PartialOutput) as raised:
                        gate.seal_oneuse_dry_admission(raw, before)
                root = self.evidence / self.oneuse
                self.assertTrue(root.exists())
                self.assertFalse((root / "LOCAL_BATCH_RESULT.json").exists())
                self.assertIn("Synthetic ENOSPC", str(raised.exception))
                self.assertTrue((root / "FAILURE.json").is_file())
                self.assertFalse(raised.exception.files == ())
                self.assertIn("FAILURE.json", raised.exception.files)
                self.assertTrue((root / "INCOMPLETE.json").is_file())
                with self.assertRaises(gate.Rejected):
                    gate.inspect_dry_receipt_structure(root)

    def test_61_public_cli_reports_partial_root_truthfully(self):
        raw, prior = self._synthetic_approved_bytes(), self.fake_admission()
        file = self.parent / "reviewed-synthetic-envelope.json"
        file.write_bytes(raw)
        real = gate._write_locked
        def fault(root_fd, name, data):
            if name == "CELLS.json":
                raise OSError("Simulated mid-admission disk failure")
            return real(root_fd, name, data)
        stream = io.StringIO()
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)), \
             mock.patch.object(gate, "inspect", return_value=prior), \
             mock.patch.object(gate, "_write_locked", side_effect=fault), \
             mock.patch("sys.stdout", stream):
            code = gate.main(["--mode", "execute",
                              "--approved-envelope", str(file)])
        self.assertEqual(code, 2)
        message = json.loads(stream.getvalue())
        self.assertEqual(message["result"], "FailedAfterPartialOutput")
        self.assertTrue(message["outputCreated"])
        self.assertFalse(message["retryAllowed"])
        self.assertTrue(message["failureMarkerAvailable"])
        self.assertTrue((self.evidence / self.oneuse).exists())
        root = self.evidence / self.oneuse
        self.assertEqual(
            set(message["observedFiles"]),
            {x["path"] for x in message["observedLedger"]})
        for row in message["observedLedger"]:
            file = root / row["path"]
            self.assertEqual(file.stat().st_size, row["bytes"])
            self.assertEqual(
                hashlib.sha256(file.read_bytes()).hexdigest(),
                row["sha256"])
        self.assertFalse((self.evidence / self.oneuse /
                          "LOCAL_BATCH_RESULT.json").exists())

    def test_62_source_history_identity_drift_after_mkdir(self):
        raw, before = self._synthetic_approved_bytes(), self.fake_admission()
        changes = []
        def inspect(request, *, expect_output_present=False):
            changes.append(expect_output_present)
            got = copy.deepcopy(before)
            if expect_output_present:
                got["custodyIdentity"]["history"]["b1NativeHostRaw"]["inode"] += 1
            return got
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)), \
             mock.patch.object(gate, "inspect", side_effect=inspect):
            with self.assertRaises(gate.PartialOutput):
                gate.seal_oneuse_dry_admission(raw, before)
        self.assertEqual(changes, [False, True])
        self.assertTrue((self.evidence / self.oneuse / "FAILURE.json").exists())
        self.assertFalse((self.evidence / self.oneuse /
                          "LOCAL_BATCH_RESULT.json").exists())

    def test_63_final_commit_marker_refuses_last_minute_source_drift(self):
        raw, before = self._synthetic_approved_bytes(), self.fake_admission()
        calls = []
        def inspect(request, *, expect_output_present=False):
            calls.append(expect_output_present)
            if len(calls) == 4:
                raise gate.Rejected("Synthetic post-manifest source drift")
            return copy.deepcopy(before)
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)), \
             mock.patch.object(gate, "inspect", side_effect=inspect):
            with self.assertRaises(gate.PartialOutput):
                gate.seal_oneuse_dry_admission(raw, before)
        root = self.evidence / self.oneuse
        self.assertEqual(calls, [False, True, True, True])
        self.assertTrue((root / "MANIFEST.json").is_file())
        self.assertTrue((root / "FAILURE.json").is_file())
        self.assertFalse((root / "LOCAL_BATCH_RESULT.json").exists())

    def test_64_precreation_parent_symlink_race_is_blocked(self):
        raw, before = self._synthetic_approved_bytes(), self.fake_admission()
        moved = self.parent / "renamed-parent-before-mkdir"
        def altered(request, *, expect_output_present=False):
            os.rename(self.evidence, moved)
            self.evidence.symlink_to(
                self.historical["b1Oneuse12"], target_is_directory=True)
            return copy.deepcopy(before)
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)), \
             mock.patch.object(gate, "inspect", side_effect=altered):
            with self.assertRaises(OSError):
                gate.seal_oneuse_dry_admission(raw, before)
        self.assertFalse((moved / self.oneuse).exists())
        self.assertFalse((self.historical["b1Oneuse12"] /
                          self.oneuse).exists())

    def test_65_failed_failure_marker_still_reports_created_root(self):
        raw, before = self._synthetic_approved_bytes(), self.fake_admission()
        saved = gate._write_locked
        def no_space(root_fd, name, data):
            if name in ("ADMISSION.json", "FAILURE.json"):
                raise OSError("Simulated disk full even for failure marker")
            return saved(root_fd, name, data)
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)), \
             mock.patch.object(gate, "inspect", return_value=before), \
             mock.patch.object(gate, "_write_locked", side_effect=no_space):
            with self.assertRaises(gate.PartialOutput) as raised:
                gate.seal_oneuse_dry_admission(raw, before)
        self.assertTrue((self.evidence / self.oneuse).is_dir())
        self.assertFalse((self.evidence / self.oneuse /
                          "LOCAL_BATCH_RESULT.json").exists())
        self.assertNotIn("FAILURE.json", raised.exception.files)

    def _seal_for_r3(self, *, write_side_effect=None, fsync_side_effect=None,
                     rename_side_effect=None, unlink_side_effect=None,
                     close_side_effect=None):
        """Isolated, test-only approval anchor; never a live Local handoff."""
        raw, prior = self._synthetic_approved_bytes(), self.fake_admission()
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)), \
             mock.patch.object(gate, "inspect", return_value=prior):
            from contextlib import ExitStack
            with ExitStack() as stack:
                if write_side_effect is not None:
                    stack.enter_context(mock.patch.object(
                        gate, "_write_locked", side_effect=write_side_effect))
                if fsync_side_effect is not None:
                    stack.enter_context(mock.patch.object(
                        gate.os, "fsync", side_effect=fsync_side_effect))
                if rename_side_effect is not None:
                    stack.enter_context(mock.patch.object(
                        gate.os, "rename", side_effect=rename_side_effect))
                if unlink_side_effect is not None:
                    stack.enter_context(mock.patch.object(
                        gate.os, "unlink", side_effect=unlink_side_effect))
                if close_side_effect is not None:
                    stack.enter_context(mock.patch.object(
                        gate.os, "close", side_effect=close_side_effect))
                return gate.seal_oneuse_dry_admission(raw, prior)

    def test_66_structurally_sealed_receipt_has_no_veto_or_stage(self):
        result = self._seal_for_r3()
        root = self.evidence / self.oneuse
        self.assertEqual(result["result"], "DryAdmissionRecorded_NoUnityOrPlayer")
        self.assertEqual(
            set(x.name for x in root.iterdir()),
            {"ADMISSION.json", "CELLS.json", "POSTFLIGHT.json",
             "MANIFEST.json", "LOCAL_BATCH_RESULT.json"})
        evidence = gate.inspect_dry_receipt_structure(root)
        self.assertEqual(evidence["filesChecked"], 5)
        self.assertEqual(evidence["realPlayerCellsNoCoverage"], 18)
        self.assertFalse(evidence["R03Accepted"])

    def test_67_after_flush_stage_fsync_error_never_publishes_final(self):
        real_write, real_fsync = gate._write_locked, gate.os.fsync
        failed = [False]
        def write_staging(fd, name, value):
            if name == "LOCAL_BATCH_STAGING.json":
                def bad_fsync(file_fd):
                    info = os.fstat(file_fd)
                    if stat.S_ISREG(info.st_mode) and not failed[0]:
                        failed[0] = True
                        raise OSError(28, "after-flush staged receipt fsync failed")
                    return real_fsync(file_fd)
                with mock.patch.object(gate.os, "fsync",
                                       side_effect=bad_fsync):
                    return real_write(fd, name, value)
            return real_write(fd, name, value)
        with self.assertRaises(gate.PartialOutput) as raised:
            self._seal_for_r3(write_side_effect=write_staging)
        root = self.evidence / self.oneuse
        self.assertTrue(failed[0])
        self.assertFalse(raised.exception.commit_visible)
        self.assertTrue((root / "LOCAL_BATCH_STAGING.json").is_file())
        self.assertEqual(json.loads(
            (root / "LOCAL_BATCH_STAGING.json").read_text())["result"],
            "DryAdmissionRecorded_NoUnityOrPlayer")
        self.assertTrue((root / "INCOMPLETE.json").is_file())
        self.assertFalse((root / "LOCAL_BATCH_RESULT.json").exists())
        with self.assertRaises(gate.Rejected):
            gate.inspect_dry_receipt_structure(root)

    def test_68_post_rename_directory_fsync_error_keeps_durable_veto(self):
        real_fsync, real_write = gate.os.fsync, gate._write_locked
        dirs = [0]
        def fsync_with_postrename_failure(fd):
            info = os.fstat(fd)
            if stat.S_ISDIR(info.st_mode):
                dirs[0] += 1
                if dirs[0] == 3:
                    raise OSError(5, "final directory fsync failed")
            return real_fsync(fd)
        def disallow_failure_marker(fd, name, value):
            if name == "FAILURE.json":
                raise OSError(28, "failure marker disk full")
            return real_write(fd, name, value)
        with self.assertRaises(gate.PartialOutput) as raised:
            self._seal_for_r3(fsync_side_effect=fsync_with_postrename_failure,
                              write_side_effect=disallow_failure_marker)
        root = self.evidence / self.oneuse
        self.assertEqual(dirs[0], 3)
        self.assertFalse(raised.exception.commit_visible)
        self.assertTrue((root / "LOCAL_BATCH_RESULT.json").exists())
        self.assertEqual(json.loads((root / "LOCAL_BATCH_RESULT.json").read_text())[
            "result"], "DryAdmissionRecorded_NoUnityOrPlayer")
        self.assertTrue((root / "INCOMPLETE.json").exists())
        self.assertFalse((root / "FAILURE.json").exists())
        # The on-disk final bytes and manifest MAY match, but the durable
        # incomplete veto makes this an invalid physical product.
        with self.assertRaises(gate.Rejected):
            gate.inspect_dry_receipt_structure(root)

    def test_69_atomic_rename_failure_does_not_publish_final(self):
        def denied(*args, **kwargs):
            raise OSError(5, "atomic final rename failed")
        with self.assertRaises(gate.PartialOutput):
            self._seal_for_r3(rename_side_effect=denied)
        root = self.evidence / self.oneuse
        self.assertTrue((root / "LOCAL_BATCH_STAGING.json").exists())
        self.assertTrue((root / "INCOMPLETE.json").exists())
        self.assertFalse((root / "LOCAL_BATCH_RESULT.json").exists())
        with self.assertRaises(gate.Rejected):
            gate.inspect_dry_receipt_structure(root)

    def test_70_final_veto_unlink_failure_never_seals_product(self):
        def fail_unlink(name, **kwargs):
            if name == "INCOMPLETE.json":
                raise OSError(5, "atomic final veto unlink failed")
            raise AssertionError("Unexpected unlink")
        with self.assertRaises(gate.PartialOutput) as raised:
            self._seal_for_r3(unlink_side_effect=fail_unlink)
        root = self.evidence / self.oneuse
        self.assertFalse(raised.exception.commit_visible)
        self.assertTrue((root / "LOCAL_BATCH_RESULT.json").exists())
        self.assertTrue((root / "INCOMPLETE.json").exists())
        with self.assertRaises(gate.Rejected):
            gate.inspect_dry_receipt_structure(root)

    def test_71_parent_close_failure_is_partial_before_commit(self):
        real_close = gate.os.close
        handled = [False]
        def fail_parent(fd):
            fdinfo = os.fstat(fd)
            if (stat.S_ISDIR(fdinfo.st_mode) and
                fdinfo.st_ino == self.evidence.stat().st_ino and
                not handled[0]):
                handled[0] = True
                real_close(fd)
                raise OSError(5, "parent descriptor close failed")
            return real_close(fd)
        with self.assertRaises(gate.PartialOutput) as raised:
            self._seal_for_r3(close_side_effect=fail_parent)
        root = self.evidence / self.oneuse
        self.assertTrue(handled[0])
        self.assertTrue(root.exists())
        self.assertFalse(raised.exception.commit_visible)
        self.assertTrue((root / "INCOMPLETE.json").exists())
        self.assertFalse((root / "LOCAL_BATCH_RESULT.json").exists())
        with self.assertRaises(gate.Rejected):
            gate.inspect_dry_receipt_structure(root)

    def test_72_root_close_failure_is_indeterminate_after_commit(self):
        real_close = gate.os.close
        handled = [False]
        def fail_root(fd):
            fdinfo = os.fstat(fd)
            root = self.evidence / self.oneuse
            if (root.is_dir() and stat.S_ISDIR(fdinfo.st_mode) and
                fdinfo.st_ino == root.stat().st_ino and not handled[0]):
                handled[0] = True
                real_close(fd)
                raise OSError(5, "root descriptor close failed")
            return real_close(fd)
        with self.assertRaises(gate.PartialOutput) as raised:
            self._seal_for_r3(close_side_effect=fail_root)
        root = self.evidence / self.oneuse
        self.assertTrue(handled[0])
        self.assertTrue(raised.exception.commit_visible)
        self.assertTrue(raised.exception.cleanup_errors)
        self.assertTrue(root.is_dir())
        self.assertFalse((root / "INCOMPLETE.json").exists())
        self.assertEqual(gate.inspect_dry_receipt_structure(root)[
            "result"], "SealedDryReceiptStructureOnly_NotLocalAuthorization")

    def test_73_cli_reports_root_close_error_as_indeterminate(self):
        raw, prior = self._synthetic_approved_bytes(), self.fake_admission()
        file = self.parent / "test-only-reviewed-envelope.json"
        file.write_bytes(raw)
        real_close = gate.os.close
        def fail_root(fd):
            root = self.evidence / self.oneuse
            if root.is_dir():
                info = os.fstat(fd)
                if stat.S_ISDIR(info.st_mode) and (
                        info.st_ino == root.stat().st_ino):
                    real_close(fd)
                    raise OSError(5, "post-commit root descriptor close failed")
            return real_close(fd)
        stream = io.StringIO()
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)), \
             mock.patch.object(gate, "inspect", return_value=prior), \
             mock.patch.object(gate.os, "close", side_effect=fail_root), \
             mock.patch("sys.stdout", stream):
            code = gate.main([
                "--mode", "execute", "--approved-envelope", str(file)])
        self.assertEqual(code, 2)
        response = json.loads(stream.getvalue())
        self.assertEqual(response["result"], "IndeterminateAfterCommit")
        self.assertTrue(response["outputCreated"])
        self.assertFalse(response["retryAllowed"])
        self.assertTrue(response["requiresPhysicalReconciliation"])
        self.assertTrue(response["commitVisible"])
        self.assertTrue(response["cleanupErrors"])
        self.assertFalse(response["R03Accepted"])

    def test_74_committed_receipt_with_incomplete_marker_is_rejected(self):
        self._seal_for_r3()
        root = self.evidence / self.oneuse
        self.assertEqual(gate.inspect_dry_receipt_structure(root)["filesChecked"], 5)
        (root / "INCOMPLETE.json").write_text(
            '{"result":"NotCommitted"}\n', encoding="utf-8")
        with self.assertRaises(gate.Rejected):
            gate.inspect_dry_receipt_structure(root)

    def test_75_manifest_only_or_missing_final_receipt_is_rejected(self):
        self._seal_for_r3()
        root = self.evidence / self.oneuse
        (root / "LOCAL_BATCH_RESULT.json").unlink()
        with self.assertRaises(gate.Rejected):
            gate.inspect_dry_receipt_structure(root)

    def test_76_failure_marker_vetoes_otherwise_matching_receipts(self):
        self._seal_for_r3()
        root = self.evidence / self.oneuse
        (root / "FAILURE.json").write_text(
            '{"result":"FailedAfterPartialOutput"}\n', encoding="utf-8")
        with self.assertRaises(gate.Rejected):
            gate.inspect_dry_receipt_structure(root)


    def test_77_after_effect_veto_unlink_error_requires_reconciliation(self):
        real_unlink, real_write = gate.os.unlink, gate._write_locked
        failure_writes = []
        def after_unlink(name, **kwargs):
            real_unlink(name, **kwargs)
            raise OSError(5, "synthetic error after veto was removed")
        def no_failure(fd, name, value):
            if name == "FAILURE.json":
                failure_writes.append(name)
                raise OSError(28, "no space for failure marker")
            return real_write(fd, name, value)
        with self.assertRaises(gate.PartialOutput) as raised:
            self._seal_for_r3(unlink_side_effect=after_unlink,
                              write_side_effect=no_failure)
        root = self.evidence / self.oneuse
        self.assertFalse(raised.exception.commit_visible)
        self.assertTrue(raised.exception.commit_uncertain)
        self.assertFalse(raised.exception.path_identity_uncertain)
        self.assertEqual(failure_writes, [])
        self.assertFalse((root / "FAILURE.json").exists())
        self.assertFalse((root / "INCOMPLETE.json").exists())
        # Physical structure can be positive even though command outcome is
        # ambiguous. Structural inspection alone never authorizes Local.
        self.assertEqual(gate.inspect_dry_receipt_structure(root)["result"],
                         "SealedDryReceiptStructureOnly_NotLocalAuthorization")

    def test_78_cli_after_effect_unlink_error_never_claims_precommit(self):
        raw, prior = self._synthetic_approved_bytes(), self.fake_admission()
        envelope = self.parent / "synthetic-unlink-envelope.json"
        envelope.write_bytes(raw)
        real_unlink = gate.os.unlink
        def after_unlink(name, **kwargs):
            real_unlink(name, **kwargs)
            raise OSError(5, "synthetic post-effect unlink error")
        stream = io.StringIO()
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)), \
             mock.patch.object(gate, "inspect", return_value=prior), \
             mock.patch.object(gate.os, "unlink", side_effect=after_unlink), \
             mock.patch("sys.stdout", stream):
            code = gate.main(["--mode", "execute",
                              "--approved-envelope", str(envelope)])
        self.assertEqual(code, 2)
        response = json.loads(stream.getvalue())
        self.assertEqual(response["result"], "IndeterminateAfterCommit")
        self.assertFalse(response["commitVisible"])
        self.assertTrue(response["finalUnlinkOutcomeUncertain"])
        self.assertEqual(response["commitOutcome"],
                         "UnknownAfterFinalUnlink")
        self.assertTrue(response["requiresPhysicalReconciliation"])
        self.assertTrue(response["outputCreated"])
        self.assertFalse(response["retryAllowed"])
        self.assertFalse(response["R03Accepted"])

    def test_79_root_relocated_after_parent_close_is_not_success(self):
        real_close = gate.os.close
        moved = self.evidence / (self.oneuse + "-moved")
        swapped = [False]
        def close_then_move(fd):
            info = os.fstat(fd)
            if (not swapped[0] and stat.S_ISDIR(info.st_mode) and
                    info.st_ino == self.evidence.stat().st_ino):
                swapped[0] = True
                real_close(fd)
                (self.evidence / self.oneuse).rename(moved)
                (self.evidence / self.oneuse).mkdir()
                return
            return real_close(fd)
        with self.assertRaises(gate.PartialOutput) as raised:
            self._seal_for_r3(close_side_effect=close_then_move)
        self.assertTrue(swapped[0])
        self.assertTrue(raised.exception.path_identity_uncertain)
        self.assertFalse(raised.exception.commit_visible)
        self.assertFalse(raised.exception.commit_uncertain)
        self.assertTrue((moved / "INCOMPLETE.json").exists())
        self.assertFalse((moved / "LOCAL_BATCH_RESULT.json").exists())
        self.assertEqual(list((self.evidence / self.oneuse).iterdir()), [])
        with self.assertRaises(gate.Rejected):
            gate.inspect_dry_receipt_structure(moved)

    def test_80_root_relocated_after_final_unlink_is_indeterminate(self):
        real_unlink = gate.os.unlink
        moved = self.evidence / (self.oneuse + "-after-commit")
        swapped = [False]
        def unlink_then_move(name, **kwargs):
            real_unlink(name, **kwargs)
            if name == "INCOMPLETE.json":
                swapped[0] = True
                (self.evidence / self.oneuse).rename(moved)
                (self.evidence / self.oneuse).mkdir()
        with self.assertRaises(gate.PartialOutput) as raised:
            self._seal_for_r3(unlink_side_effect=unlink_then_move)
        self.assertTrue(swapped[0])
        self.assertTrue(raised.exception.commit_visible)
        self.assertFalse(raised.exception.commit_uncertain)
        self.assertTrue(raised.exception.path_identity_uncertain)
        self.assertEqual(list((self.evidence / self.oneuse).iterdir()), [])
        self.assertEqual(gate.inspect_dry_receipt_structure(moved)["result"],
                         "SealedDryReceiptStructureOnly_NotLocalAuthorization")



    def test_81_cli_relocated_parent_closed_root_requires_reconciliation(self):
        raw, prior = self._synthetic_approved_bytes(), self.fake_admission()
        envelope = self.parent / "synthetic-path-identity-envelope.json"
        envelope.write_bytes(raw)
        real_close = gate.os.close
        moved = self.evidence / (self.oneuse + "-cli-relocated")
        changed = [False]
        def close_then_relocate(fd):
            info = os.fstat(fd)
            if (not changed[0] and stat.S_ISDIR(info.st_mode) and
                    info.st_ino == self.evidence.stat().st_ino):
                changed[0] = True
                real_close(fd)
                (self.evidence / self.oneuse).rename(moved)
                (self.evidence / self.oneuse).mkdir()
                return
            return real_close(fd)
        stream = io.StringIO()
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)), \
             mock.patch.object(gate, "inspect", return_value=prior), \
             mock.patch.object(gate.os, "close", side_effect=close_then_relocate), \
             mock.patch("sys.stdout", stream):
            code = gate.main(["--mode", "execute",
                              "--approved-envelope", str(envelope)])
        response = json.loads(stream.getvalue())
        self.assertTrue(changed[0])
        self.assertEqual(code, 2)
        self.assertEqual(response["result"], "FailedAfterPartialOutput")
        self.assertEqual(response["commitOutcome"], "NotCommitted")
        self.assertTrue(response["outputPathIdentityUncertain"])
        self.assertTrue(response["requiresPhysicalReconciliation"])
        self.assertTrue(response["outputCreated"])
        self.assertFalse(response["retryAllowed"])
        self.assertFalse(response["R03Accepted"])
        self.assertTrue((moved / "INCOMPLETE.json").exists())
        self.assertFalse((moved / "LOCAL_BATCH_RESULT.json").exists())



    # R5 regressions for R4-IR-01/02. All approvals and host observations
    # below are synthetic process-local fixtures, never Local validation.
    def _r5_cli_fixture(self, suffix):
        self.oneuse = "R03-B2-D5-r5-" + suffix
        raw, prior = self._synthetic_approved_bytes(), self.fake_admission()
        envelope = self.parent / (suffix + "-synthetic-envelope.json")
        envelope.write_bytes(raw)
        return raw, prior, envelope, self.evidence / self.oneuse

    def _r5_execute(self, raw, prior, envelope, stdout, stderr):
        with mock.patch.object(gate, "APPROVED_EXECUTION_ENVELOPE_BLOB",
                               gate.git_blob(raw)), \
             mock.patch.object(gate, "inspect", return_value=prior), \
             mock.patch("sys.stdout", stdout), \
             mock.patch("sys.stderr", stderr):
            code = gate.main(["--mode", "execute",
                              "--approved-envelope", str(envelope)])
        self.assertIsNone(gate.APPROVED_EXECUTION_ENVELOPE_BLOB)
        return code

    def _r5_assert_closed(self, response):
        self.assertEqual(response["WEB_TO_LOCAL"], "CLOSED_NO_LOCAL_EXECUTION")
        self.assertEqual(response["D5BLocalExecution"], "NotAuthorized")
        self.assertIs(response["R03Accepted"], False)

    def _r5_assert_sealed_structure(self, root):
        self.assertEqual({p.name for p in root.iterdir()}, {
            "ADMISSION.json", "CELLS.json", "POSTFLIGHT.json",
            "MANIFEST.json", "LOCAL_BATCH_RESULT.json"})
        structure = gate.inspect_dry_receipt_structure(root)
        self.assertEqual(structure["result"],
                         "SealedDryReceiptStructureOnly_NotLocalAuthorization")
        self.assertEqual(structure["filesChecked"], 5)
        self.assertEqual(structure["realPlayerCellsPassed"], 0)
        self.assertEqual(structure["realPlayerCellsNoCoverage"], 18)
        self.assertIs(structure["R03Accepted"], False)

    def _r5_assert_committed_delivery_failure(self, response, root):
        self._r5_assert_closed(response)
        self.assertEqual(response["result"], "IndeterminateAfterCommit")
        self.assertEqual(response["candidate"], str(root))
        self.assertIs(response["outputCreated"], True)
        self.assertIs(response["commitVisible"], True)
        self.assertEqual(response["commitOutcome"], "Visible")
        self.assertIs(response["retryAllowed"], False)
        self.assertIs(response["requiresPhysicalReconciliation"], True)
        self.assertEqual(response["responseDelivery"], "Failed")
        self._r5_assert_sealed_structure(root)

    def _r5_assert_unknown_creation(self, response, root,
                                    outcome="UnknownAfterMkdirAttempt"):
        self._r5_assert_closed(response)
        self.assertEqual(response["result"], "IndeterminateOutputCreation")
        self.assertEqual(response["candidate"], str(root))
        self.assertIsNone(response["outputCreated"])
        self.assertEqual(response["creationOutcome"], outcome)
        self.assertEqual(response["candidateOwnership"], "Unproven")
        self.assertEqual(response["commitOutcome"], "NotCommitted")
        self.assertIs(response["retryAllowed"], False)
        self.assertIs(response["requiresPhysicalReconciliation"], True)

    def _r5_writer_line(self, statement):
        lines, start = source_inspect.getsourcelines(
            gate.seal_oneuse_dry_admission)
        matches = [start + offset for offset, line in enumerate(lines)
                   if line.strip().startswith(statement)]
        self.assertEqual(len(matches), 1,
                         "Expected one writer boundary: " + statement)
        return matches[0]

    def test_82_cli_completed_seal_first_stdout_write_failure_preserves_commit(self):
        raw, prior, envelope, root = self._r5_cli_fixture("first-write")
        stdout = _R5DeliveryFaultStream(write_fault="first")
        stderr = io.StringIO()
        code = self._r5_execute(raw, prior, envelope, stdout, stderr)
        self.assertEqual(code, 2)
        self.assertEqual(stdout.write_attempts, 1)
        self.assertEqual(stdout.getvalue(), "")
        self._r5_assert_committed_delivery_failure(
            json.loads(stderr.getvalue()), root)

    def test_83_cli_completed_seal_stdout_flush_failure_preserves_commit(self):
        raw, prior, envelope, root = self._r5_cli_fixture("flush")
        stdout = _R5DeliveryFaultStream(flush_fault=True)
        stderr = io.StringIO()
        code = self._r5_execute(raw, prior, envelope, stdout, stderr)
        self.assertEqual(code, 2)
        self.assertEqual(stdout.flush_attempts, 1)
        # Bytes may have escaped before flush failed. They are not a
        # successful terminal command outcome and must not trigger a retry.
        self.assertEqual(json.loads(stdout.getvalue())["result"],
                         "DryAdmissionRecorded_NoUnityOrPlayer")
        self._r5_assert_committed_delivery_failure(
            json.loads(stderr.getvalue()), root)

    def test_84_cli_completed_seal_both_failed_streams_returns_two(self):
        raw, prior, envelope, root = self._r5_cli_fixture("both-streams")
        stdout = _R5DeliveryFaultStream(write_fault="always", flush_fault=True)
        stderr = _R5DeliveryFaultStream(write_fault="always", flush_fault=True)
        code = self._r5_execute(raw, prior, envelope, stdout, stderr)
        self.assertEqual(code, 2)
        self.assertEqual(stdout.write_attempts, 1)
        self.assertEqual(stderr.write_attempts, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")
        self._r5_assert_sealed_structure(root)


    def test_85_cli_after_effect_mkdir_faults_report_unknown_creation(self):
        real_mkdir = gate.os.mkdir
        for error_type in (OSError, KeyboardInterrupt):
            with self.subTest(error=error_type.__name__):
                raw, prior, envelope, root = self._r5_cli_fixture(
                    "mkdir-after-" + error_type.__name__)
                stdout, stderr = io.StringIO(), io.StringIO()
                created = []
                def create_then_interrupt(name, mode=0o777, **kwargs):
                    real_mkdir(name, mode, **kwargs)
                    created.append(gate.directory_identity(root))
                    raise error_type("synthetic failure after real mkdir")
                with mock.patch.object(gate.os, "mkdir",
                                       side_effect=create_then_interrupt) as mkdir, \
                     mock.patch.object(gate, "_write_locked") as write:
                    code = self._r5_execute(
                        raw, prior, envelope, stdout, stderr)
                self.assertEqual(code, 2)
                mkdir.assert_called_once()
                write.assert_not_called()
                self.assertEqual(created, [gate.directory_identity(root)])
                self.assertEqual(list(root.iterdir()), [])
                self.assertEqual(stderr.getvalue(), "")
                self._r5_assert_unknown_creation(
                    json.loads(stdout.getvalue()), root)
        self.assertIs(gate.os.mkdir, real_mkdir)

    def test_86_cli_real_mkdir_trace_interruption_reports_unknown_creation(self):
        raw, prior, envelope, root = self._r5_cli_fixture("trace-after-mkdir")
        writer_code = gate.seal_oneuse_dry_admission.__code__
        boundary = self._r5_writer_line("root_created = True")
        real_mkdir, previous_trace = gate.os.mkdir, sys.gettrace()
        seen = []
        def interrupt_before_recorded_creation(frame, event, arg):
            if (event == "line" and frame.f_code is writer_code and
                    frame.f_lineno == boundary):
                seen.append({
                    "rootCreated": frame.f_locals["root_created"],
                    "creationAttempted": frame.f_locals["creation_attempted"],
                    "candidateExists": root.is_dir(),
                    "mkdirUnmodified": gate.os.mkdir is real_mkdir,
                })
                raise KeyboardInterrupt("after real mkdir, before assignment")
            return interrupt_before_recorded_creation
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(gate, "_write_locked") as write:
            try:
                sys.settrace(interrupt_before_recorded_creation)
                code = self._r5_execute(raw, prior, envelope, stdout, stderr)
            finally:
                sys.settrace(previous_trace)
        self.assertEqual(code, 2)
        self.assertEqual(seen, [{"rootCreated": False, "creationAttempted": True,
                                 "candidateExists": True,
                                 "mkdirUnmodified": True}])
        self.assertIs(sys.gettrace(), previous_trace)
        self.assertIs(gate.os.mkdir, real_mkdir)
        write.assert_not_called()
        self.assertEqual(list(root.iterdir()), [])
        self._r5_assert_unknown_creation(json.loads(stdout.getvalue()), root)

    def test_87_cli_preexisting_candidate_preserves_unrelated_sentinel(self):
        raw, prior, envelope, root = self._r5_cli_fixture("preexisting")
        root.mkdir()
        sentinel = root / "UNRELATED.txt"
        sentinel.write_bytes(b"pre-existing data must survive admission denial")
        identity = gate.directory_identity(root)
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(gate.os, "mkdir") as mkdir, \
             mock.patch.object(gate, "_write_locked") as write:
            code = self._r5_execute(raw, prior, envelope, stdout, stderr)
        self.assertEqual(code, 2)
        mkdir.assert_not_called()
        write.assert_not_called()
        response = json.loads(stdout.getvalue())
        self._r5_assert_closed(response)
        self.assertIs(response["outputCreated"], False)
        self.assertEqual(response["creationOutcome"], "PreexistingCandidate")
        self.assertEqual(gate.directory_identity(root), identity)
        self.assertEqual(list(root.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_bytes(),
                         b"pre-existing data must survive admission denial")

    def test_88_cli_raced_mkdir_collision_preserves_unrelated_sentinel(self):
        raw, prior, envelope, root = self._r5_cli_fixture("raced-collision")
        real_mkdir = gate.os.mkdir
        sentinel = root / "UNRELATED.txt"
        identity = []
        def race_then_collide(name, mode=0o777, **kwargs):
            # The first creation represents another actor consuming the
            # candidate. The writer's actual call then raises FileExistsError.
            real_mkdir(name, mode, **kwargs)
            sentinel.write_bytes(b"unrelated racing owner")
            identity.append(gate.directory_identity(root))
            return real_mkdir(name, mode, **kwargs)
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(gate.os, "mkdir",
                               side_effect=race_then_collide) as mkdir, \
             mock.patch.object(gate, "_write_locked") as write:
            code = self._r5_execute(raw, prior, envelope, stdout, stderr)
        self.assertEqual(code, 2)
        mkdir.assert_called_once()
        write.assert_not_called()
        self._r5_assert_unknown_creation(json.loads(stdout.getvalue()), root,
                                         "CollisionReported")
        self.assertEqual(identity, [gate.directory_identity(root)])
        self.assertEqual(list(root.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_bytes(), b"unrelated racing owner")

    def test_89_cli_mkdir_pre_effect_error_does_not_claim_proven_absence(self):
        raw, prior, envelope, root = self._r5_cli_fixture("mkdir-before-effect")
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(gate.os, "mkdir", side_effect=OSError(
                5, "synthetic error before mkdir has any effect")) as mkdir, \
             mock.patch.object(gate, "_write_locked") as write:
            code = self._r5_execute(raw, prior, envelope, stdout, stderr)
        self.assertEqual(code, 2)
        mkdir.assert_called_once()
        write.assert_not_called()
        self.assertFalse(root.exists())
        self._r5_assert_unknown_creation(json.loads(stdout.getvalue()), root)

    def test_90_cli_sealer_return_boundary_fault_requires_reconciliation(self):
        real_sealer = gate.seal_oneuse_dry_admission
        for error_type in (OSError, RuntimeError, KeyboardInterrupt):
            with self.subTest(error=error_type.__name__):
                raw, prior, envelope, root = self._r5_cli_fixture(
                    "writer-return-" + error_type.__name__)
                completed = []
                def seal_then_interrupt(approved_raw, observation):
                    result = real_sealer(approved_raw, observation)
                    completed.append(result["result"])
                    raise error_type("real sealer returned before wrapper fault")
                stdout, stderr = io.StringIO(), io.StringIO()
                with mock.patch.object(gate, "seal_oneuse_dry_admission",
                                       side_effect=seal_then_interrupt):
                    code = self._r5_execute(
                        raw, prior, envelope, stdout, stderr)
                self.assertEqual(code, 2)
                self.assertEqual(completed,
                                 ["DryAdmissionRecorded_NoUnityOrPlayer"])
                response = json.loads(stdout.getvalue())
                self._r5_assert_closed(response)
                self.assertEqual(response["candidate"], str(root))
                self.assertIsNone(response["outputCreated"])
                self.assertEqual(response["result"], "IndeterminateWriterOutcome")
                self.assertEqual(response["commitOutcome"],
                                 "UnknownAfterWriterInvocation")
                self.assertIs(response["retryAllowed"], False)
                self.assertIs(response["requiresPhysicalReconciliation"], True)
                self._r5_assert_sealed_structure(root)
        self.assertIs(gate.seal_oneuse_dry_admission, real_sealer)


    def test_91_cli_partial_output_delivery_failure_retains_partial_accounting(self):
        real_write = gate._write_locked
        for fault in ("first-write", "flush", "both-streams"):
            with self.subTest(fault=fault):
                raw, prior, envelope, root = self._r5_cli_fixture(
                    "partial-report-" + fault)
                def fail_cells(fd, name, value):
                    if name == "CELLS.json":
                        raise OSError(28, "synthetic partial-output failure")
                    return real_write(fd, name, value)
                stdout = _R5DeliveryFaultStream(
                    write_fault=None if fault == "flush" else "always",
                    flush_fault=fault == "flush")
                stderr = (_R5DeliveryFaultStream(write_fault="always")
                          if fault == "both-streams" else io.StringIO())
                with mock.patch.object(gate, "_write_locked",
                                       side_effect=fail_cells):
                    code = self._r5_execute(
                        raw, prior, envelope, stdout, stderr)
                self.assertEqual(code, 2)
                self.assertTrue((root / "INCOMPLETE.json").is_file())
                self.assertTrue((root / "FAILURE.json").is_file())
                self.assertFalse((root / "LOCAL_BATCH_RESULT.json").exists())
                with self.assertRaises(gate.Rejected):
                    gate.inspect_dry_receipt_structure(root)
                if fault == "both-streams":
                    self.assertEqual(stdout.write_attempts, 1)
                    self.assertEqual(stderr.write_attempts, 1)
                else:
                    response = json.loads(stderr.getvalue())
                    self._r5_assert_closed(response)
                    self.assertEqual(response["result"], "FailedAfterPartialOutput")
                    self.assertIs(response["outputCreated"], True)
                    self.assertEqual(response["commitOutcome"], "NotCommitted")
                    self.assertIs(response["retryAllowed"], False)
                    self.assertIs(response["failureMarkerAvailable"], True)
                    self.assertEqual(response["responseDelivery"], "Failed")
                    self.assertIn("FAILURE.json", response["observedFiles"])
                if fault == "flush":
                    self.assertEqual(stdout.flush_attempts, 1)
                    self.assertEqual(json.loads(stdout.getvalue())["result"],
                                     "FailedAfterPartialOutput")
                else:
                    self.assertEqual(stdout.write_attempts, 1)
                    self.assertEqual(stdout.getvalue(), "")

    def test_92_cli_null_approval_delivery_failure_remains_prewrite_denial(self):
        self.assertIsNone(gate.APPROVED_EXECUTION_ENVELOPE_BLOB)
        for fault in ("first-write", "flush", "both-streams"):
            with self.subTest(fault=fault):
                root = self.evidence / ("R03-B2-D5-r5-denied-" + fault)
                envelope = self.parent / (fault + "-missing-envelope.json")
                stdout = _R5DeliveryFaultStream(
                    write_fault=None if fault == "flush" else "always",
                    flush_fault=fault == "flush")
                stderr = (_R5DeliveryFaultStream(write_fault="always")
                          if fault == "both-streams" else io.StringIO())
                with mock.patch.object(Path, "read_bytes") as read, \
                     mock.patch.object(gate, "approved_envelope") as approve, \
                     mock.patch.object(gate, "inspect") as inspect, \
                     mock.patch.object(gate, "seal_oneuse_dry_admission") as seal, \
                     mock.patch.object(gate.os, "mkdir") as mkdir, \
                     mock.patch("sys.stdout", stdout), \
                     mock.patch("sys.stderr", stderr):
                    code = gate.main(["--mode", "execute",
                                      "--approved-envelope", str(envelope)])
                self.assertEqual(code, 2)
                for operation in (read, approve, inspect, seal, mkdir):
                    operation.assert_not_called()
                self.assertFalse(root.exists())
                self.assertFalse(envelope.exists())
                if fault == "both-streams":
                    self.assertEqual(stderr.write_attempts, 1)
                else:
                    response = json.loads(stderr.getvalue())
                    self._r5_assert_closed(response)
                    self.assertEqual(response["result"], "NotAuthorized")
                    self.assertIs(response["outputCreated"], False)
                    self.assertEqual(response["responseDelivery"], "Failed")
                if fault == "flush":
                    self.assertEqual(stdout.flush_attempts, 1)
                    self.assertEqual(json.loads(stdout.getvalue())["result"],
                                     "NotAuthorized")
                else:
                    self.assertEqual(stdout.write_attempts, 1)
                    self.assertEqual(stdout.getvalue(), "")
        self.assertIsNone(gate.APPROVED_EXECUTION_ENVELOPE_BLOB)

    def test_93_cli_trace_before_mkdir_retains_attempt_uncertainty(self):
        raw, prior, envelope, root = self._r5_cli_fixture("trace-before-mkdir")
        writer_code = gate.seal_oneuse_dry_admission.__code__
        boundary = self._r5_writer_line("os.mkdir(")
        real_mkdir, previous_trace = gate.os.mkdir, sys.gettrace()
        seen = []
        def interrupt_before_mkdir(frame, event, arg):
            if (event == "line" and frame.f_code is writer_code and
                    frame.f_lineno == boundary):
                seen.append({
                    "rootCreated": frame.f_locals["root_created"],
                    "creationAttempted": frame.f_locals["creation_attempted"],
                    "candidateExists": root.exists(),
                    "mkdirUnmodified": gate.os.mkdir is real_mkdir,
                })
                raise KeyboardInterrupt("attempt recorded before real mkdir")
            return interrupt_before_mkdir
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(gate, "_write_locked") as write:
            try:
                sys.settrace(interrupt_before_mkdir)
                code = self._r5_execute(raw, prior, envelope, stdout, stderr)
            finally:
                sys.settrace(previous_trace)
        self.assertEqual(code, 2)
        self.assertEqual(seen, [{"rootCreated": False, "creationAttempted": True,
                                 "candidateExists": False,
                                 "mkdirUnmodified": True}])
        self.assertIs(sys.gettrace(), previous_trace)
        self.assertIs(gate.os.mkdir, real_mkdir)
        write.assert_not_called()
        self.assertFalse(root.exists())
        self._r5_assert_unknown_creation(json.loads(stdout.getvalue()), root)

    def test_94_cli_after_mkdir_replacement_preserves_both_unowned_roots(self):
        raw, prior, envelope, root = self._r5_cli_fixture("mkdir-replacement")
        real_mkdir = gate.os.mkdir
        moved = self.evidence / (self.oneuse + "-relocated")
        sentinel = root / "UNRELATED.txt"
        identities = []
        def create_move_replace_then_interrupt(name, mode=0o777, **kwargs):
            real_mkdir(name, mode, **kwargs)
            root.rename(moved)
            real_mkdir(name, mode, **kwargs)
            sentinel.write_bytes(b"replacement owner must not be adopted")
            identities.append((gate.directory_identity(moved),
                               gate.directory_identity(root)))
            raise OSError(5, "synthetic fault after unrecorded root replacement")
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(gate.os, "mkdir",
                               side_effect=create_move_replace_then_interrupt), \
             mock.patch.object(gate, "_write_locked") as write:
            code = self._r5_execute(raw, prior, envelope, stdout, stderr)
        self.assertEqual(code, 2)
        write.assert_not_called()
        self._r5_assert_unknown_creation(json.loads(stdout.getvalue()), root)
        self.assertEqual(identities, [(gate.directory_identity(moved),
                                       gate.directory_identity(root))])
        self.assertNotEqual(moved.stat().st_ino, root.stat().st_ino)
        self.assertEqual(list(moved.iterdir()), [])
        self.assertEqual(list(root.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_bytes(),
                         b"replacement owner must not be adopted")


if __name__ == "__main__":
    unittest.main()
