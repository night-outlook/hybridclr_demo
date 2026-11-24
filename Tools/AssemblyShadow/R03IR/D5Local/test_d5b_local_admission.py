#!/usr/bin/env python3
"""Prospective D5-B admission tests. No real Unity, Player, Local handoff."""
from __future__ import annotations

import copy
import io
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock

import d5b_local_admission as gate


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


if __name__ == "__main__":
    unittest.main()
