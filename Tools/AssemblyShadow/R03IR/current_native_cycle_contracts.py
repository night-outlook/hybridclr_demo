#!/usr/bin/env python3
"""Host-only adversarial contracts for the one-use R03 Local coordinator.

Deliberately no Unity/SDK/Player, original S archive, network or previous Local
root execution. The actual coordinator is exercised on isolated tiny controls.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import run_current_native_validation_cycle as cycle


class CurrentNativeCycleContracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="r03-ir-cycle-")
        self.addCleanup(self.tmp.cleanup)
        # macOS /var is an alias for /private/var; tests use real paths.
        self.base = Path(self.tmp.name).resolve(strict=True)
        self.workspace = self.base / "sources"
        self.workspace.mkdir()
        for name in cycle.REPOS:
            (self.workspace / name).mkdir()
        self.original = self.base / "original-S"
        self.original.mkdir()
        self.output = self.base / "evidence" / "one-use"
        self.output.parent.mkdir()

    def fake_result(self) -> dict:
        cells = [{"id": ident, "result": "Passed"}
                 for ident in cycle.EXPECTED_CHILD_CELLS]
        return {"schemaVersion": 1, "kind": "R03IRFocusedTerminalLocalBatch",
                "repositories": cycle.source.expected_batch_repositories("a" * 40),
                "result": "FocusedEvidenceReadyForPrimaryReview",
                "sealStatus": "Passed", "plannedFreshBuilds": 3,
                "verifiedFreshBuilds": 3, "plannedFreshPlayers": 5,
                "verifiedFreshPlayers": 5, "recordedFreshPlayerRawFiles": 5,
                "originalSFixtureAuthority": "AuthenticatedOriginalCommit",
                "originalSFixtureAuthoritySha256": "b" * 64,
                "R03Accepted": False, "H2Passed": False,
                "fullLegacyRegressionAcceptance": False,
                "qualificationApproved": False, "pureInterpreterExpansionEnabled": False,
                "cells": cells}

    def read_batch(self, data: dict, demo_commit="a" * 40):
        receipt = self.base / "test-batch.json"
        receipt.write_text(json.dumps(data), encoding="utf-8")
        try:
            return cycle.verify_current_batch(receipt, demo_commit)
        finally:
            receipt.unlink()

    def all_passed(self):
        return {k: {"state": "Passed"} for k in (
            "source-contracts", "oracle-contracts", "vm-delta-contracts",
            "original-s-host-contracts", "original-s-audit",
            "original-s-process-joins", "native-host-diagnostics",
            "current-native-players", "installed-source-host-contracts",
            "native-installed-source-audit")}

    def test_01_constituent_source_pins_are_explicit(self):
        self.assertEqual(cycle.NATIVE, "8aa8d09319a89b55b2496bcc2c69ccc69cb57be9")
        self.assertEqual(cycle.S_PUBLICATION,
                         "fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b")
        self.assertEqual(len(cycle.EXPECTED_BUILD_ROLES), 3)
        self.assertEqual(len(set(cycle.EXPECTED_PLAYERS)), 5)
        self.assertEqual(cycle.BRANCH, "codex/assembly-shadow-r01b-h1")

    def test_02_new_external_destination_passes_without_creation(self):
        cycle.validate_destination(self.workspace, self.original, self.output)
        self.assertFalse(self.output.exists())

    def test_03_existing_or_in_repository_destination_refused(self):
        for path in (self.workspace / "hybridclr_demo" / "not-allowed",
                     self.original / "not-allowed",
                     self.workspace / "not-allowed"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                cycle.validate_destination(self.workspace, self.original, path)
        self.output.mkdir()
        with self.assertRaises(ValueError):
            cycle.validate_destination(self.workspace, self.original, self.output)

    def test_04_relative_parent_or_symlink_path_refused(self):
        with self.assertRaises(ValueError):
            cycle.validate_destination(self.workspace, self.original, Path("relative/path"))
        link = self.base / "link-to-evidence"
        link.symlink_to(self.output.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            cycle.validate_destination(self.workspace, self.original, link / "batch")

    def test_05_same_source_as_original_refused(self):
        with self.assertRaises(ValueError):
            cycle.validate_destination(self.workspace, self.workspace / "hybridclr_demo", self.output)

    def test_06_source_tuple_must_be_40_digit_sha(self):
        with self.assertRaises(ValueError):
            cycle.validate_sources(self.workspace, "HEAD")

    def test_07_original_checkout_wrong_head_refused(self):
        with mock.patch.object(cycle, "git", side_effect=[
            str(self.original), "0"*40, ""]):
            with self.assertRaises(ValueError):
                cycle.validate_original(self.original)

    def test_08_source_gate_fails_before_output(self):
        with mock.patch.object(cycle, "identity", return_value={"remoteHeadVerified": True}), \
             mock.patch.object(cycle.source, "verify_source_roots",
                 return_value={"result": "Failed", "verifiedSourceFiles": 9}):
            with self.assertRaises(ValueError):
                cycle.validate_sources(self.workspace, "a" * 40)
        self.assertFalse(self.output.exists())

    def test_09_47_vm_files_required_before_output(self):
        with mock.patch.object(cycle, "identity", return_value={"remoteHeadVerified": True}), \
             mock.patch.object(cycle.source, "verify_source_roots", return_value={
                 "result": "PassedCoherentSourceOnly_NoPlayerOrRuntimeValidation",
                 "verifiedSourceFiles": 14,
                 "currentCandidatePins": dict(cycle.source.CURRENT)}), \
             mock.patch.object(cycle.delta, "validate", return_value={
                 "result": "PassedCurrentNativeVmSourceDeltaOnly",
                 "changedVmFileCount": 45,
                 "currentNativeCommit": cycle.source.CURRENT["il2cpp_plus"]}):
            with self.assertRaises(ValueError):
                cycle.validate_sources(self.workspace, "a" * 40)
        self.assertFalse(self.output.exists())

    def test_10_positive_source_contract_is_non_runtime(self):
        with mock.patch.object(cycle, "identity", return_value={"remoteHeadVerified": True}), \
             mock.patch.object(cycle.source, "verify_source_roots", return_value={
                 "result": "PassedCoherentSourceOnly_NoPlayerOrRuntimeValidation",
                 "verifiedSourceFiles": 14,
                 "currentCandidatePins": dict(cycle.source.CURRENT)}), \
             mock.patch.object(cycle.delta, "validate", return_value={
                 "result": "PassedCurrentNativeVmSourceDeltaOnly",
                 "changedVmFileCount": 46,
                 "currentNativeCommit": cycle.source.CURRENT["il2cpp_plus"]}):
            result = cycle.validate_sources(self.workspace, "a"*40)
        self.assertEqual(result["result"], "PassedReadOnlySourceAdmission_NotBuildOrRuntime")
        self.assertIs(result["R03Accepted"], False)


    def test_27_shared_admission_rejects_candidate_pin_and_count_drift(self):
        """The composed Mac/runner gate must not accept a merely green label."""
        valid = {
            "result": "PassedCoherentSourceOnly_NoPlayerOrRuntimeValidation",
            "verifiedSourceFiles": 14,
            "currentCandidatePins": dict(cycle.source.CURRENT),
        }
        delta_ok = {
            "result": "PassedCurrentNativeVmSourceDeltaOnly",
            "changedVmFileCount": 46,
            "currentNativeCommit": cycle.source.CURRENT["il2cpp_plus"],
        }
        for variant in ("old-source-count", "new-unknown-source-count",
                        "native-pin", "missing-pin"):
            record = copy.deepcopy(valid)
            if variant == "old-source-count": record["verifiedSourceFiles"] = 11
            elif variant == "new-unknown-source-count": record["verifiedSourceFiles"] = 15
            elif variant == "native-pin":
                record["currentCandidatePins"]["il2cpp_plus"] = "0"*40
            else:
                del record["currentCandidatePins"]["il2cpp_plus"]
            with self.subTest(variant=variant), \
                 mock.patch.object(cycle, "identity", return_value={"remoteHeadVerified":True}), \
                 mock.patch.object(cycle.source, "verify_source_roots", return_value=record), \
                 mock.patch.object(cycle.delta, "validate", return_value=delta_ok):
                with self.assertRaisesRegex(ValueError,"Fourteen-file B1"):
                    cycle.validate_sources(self.workspace,"a"*40)

        for variant in ("old-vm-count", "unreviewed-vm-count",
                        "wrong-native-head", "missing-native-head"):
            record = copy.deepcopy(delta_ok)
            if variant == "old-vm-count": record["changedVmFileCount"] = 45
            elif variant == "unreviewed-vm-count": record["changedVmFileCount"] = 48
            elif variant == "wrong-native-head": record["currentNativeCommit"] = "0"*40
            else: del record["currentNativeCommit"]
            with self.subTest(variant=variant), \
                 mock.patch.object(cycle, "identity", return_value={"remoteHeadVerified":True}), \
                 mock.patch.object(cycle.source, "verify_source_roots", return_value=valid), \
                 mock.patch.object(cycle.delta, "validate", return_value=record):
                with self.assertRaisesRegex(ValueError,"Forty-six-file B1"):
                    cycle.validate_sources(self.workspace,"a"*40)
        self.assertFalse(self.output.exists())

    def test_11_new_subprocess_log_receipt_and_hashes(self):
        self.output.mkdir()
        row = cycle.run_step(self.output, "tiny-pass",
                             [sys.executable, "-B", "-c", "print('probe OK')"], 30)
        self.assertEqual(row["state"], "Passed")
        self.assertEqual(row["exitCode"], 0)
        self.assertEqual(cycle.digest(self.output / "steps/tiny-pass/stdout.log"),
                         row["stdoutSha256"])
        self.assertIn("probe OK", (self.output / "steps/tiny-pass/stdout.log").read_text())
        self.assertFalse(row["mayHaveExternalOwnedChildren"])

    def test_12_failed_child_is_retained_not_retried(self):
        self.output.mkdir()
        row = cycle.run_step(self.output, "tiny-failure",
                             [sys.executable, "-B", "-c",
                              "import sys; print('bad'); sys.exit(7)"], 30)
        self.assertEqual(row["exitCode"], 7)
        self.assertEqual(row["state"], "Failed")
        with self.assertRaises(FileExistsError):
            cycle.run_step(self.output, "tiny-failure", [sys.executable, "-B", "-c", "pass"], 30)
        self.assertTrue((self.output / "steps/tiny-failure/INVOCATION.json").is_file())
        # Even exit-zero group leaders are rejected if owned children remain.
        with mock.patch.object(cycle, "group_exists", side_effect=[True, False]), \
             mock.patch.object(cycle, "group_snapshot", return_value={"owned": True}), \
             mock.patch.object(cycle.os, "killpg") as kill:
            surviving = cycle.run_step(self.output, "simulated-survivor",
                 [sys.executable, "-B", "-c", "pass"], 30)
        self.assertEqual(surviving["exitCode"], 0)
        self.assertEqual(surviving["state"], "Failed")
        self.assertTrue(surviving["mayHaveExternalOwnedChildren"])
        self.assertTrue(surviving["processGroupRemainedAtExit"])
        self.assertFalse(surviving["postCleanupGroupExists"])
        kill.assert_called_once()
        with mock.patch.object(cycle, "group_exists", side_effect=[True, False]), \
             mock.patch.object(cycle, "group_snapshot",
                               side_effect=RuntimeError("diagnostic failed")), \
             mock.patch.object(cycle.os, "killpg") as second_kill:
            diagnostic_failure = cycle.run_step(
                self.output, "diagnostic-should-not-prevent-cleanup",
                [sys.executable, "-B", "-c", "pass"], 30)
        self.assertEqual(diagnostic_failure["state"], "Failed")
        self.assertTrue(diagnostic_failure["mayHaveExternalOwnedChildren"])
        self.assertIn("diagnostic failed", diagnostic_failure["processDiagnosticError"])
        second_kill.assert_called_once()

    def test_13_valid_synthetic_batch_receipt_remains_non_acceptance(self):
        result = self.read_batch(self.fake_result())
        self.assertEqual(result["result"], "PassedFiveFocusedCurrentNativePlayersOnly")
        self.assertIs(result["IRR0301IndependentlyClosed"], False)

    def test_14_missing_or_forged_batch_role_refused(self):
        for key, value in (
            ("verifiedFreshBuilds", 2), ("verifiedFreshPlayers", 4),
            ("recordedFreshPlayerRawFiles", 4), ("sealStatus", "Failed"),
            ("originalSFixtureAuthority", "NotRun"), ("R03Accepted", True),
            ("pureInterpreterExpansionEnabled", True),
            ("result", "Failed"),
        ):
            with self.subTest(key=key):
                rec = self.fake_result()
                rec[key] = value
                with self.assertRaises(ValueError):
                    self.read_batch(rec)

    def test_15_fake_cases_and_wrong_native_sha_refused(self):
        for scenario in ("missing-case", "wrong-native", "failed-build", "no-fixture-hash"):
            with self.subTest(scenario=scenario):
                rec = self.fake_result()
                if scenario == "missing-case":
                    rec["cells"] = rec["cells"][:-1]
                if scenario == "wrong-native":
                    rec["repositories"]["il2cpp_plus"] = "0" * 40
                if scenario == "failed-build":
                    rec["cells"][0]["result"] = "Failed"
                if scenario == "no-fixture-hash":
                    rec["originalSFixtureAuthoritySha256"] = ""
                with self.assertRaises(ValueError):
                    self.read_batch(rec)

    def test_16_coordinator_summary_requires_all_ten_stages(self):
        stages = self.all_passed()
        native = {"result": "PassedFiveFocusedCurrentNativePlayersOnly"}
        after = {"result": "PassedReadOnlySourceAdmission_NotBuildOrRuntime"}
        summary = cycle.assess_summary(stages, native, after)
        self.assertEqual(summary["result"], "FocusedEvidenceReadyForIndependentReview")
        self.assertIs(summary["R03Accepted"], False)
        self.assertEqual(summary["independentR03FullStageReview"], "NotRun")
        self.assertIs(summary["IRR0302IndependentlyClosed"], False)

    def test_17_no_hidden_success_on_partial_or_forged_results(self):
        stages = self.all_passed()
        native = {"result": "PassedFiveFocusedCurrentNativePlayersOnly"}
        after = {"result": "PassedReadOnlySourceAdmission_NotBuildOrRuntime"}
        for key in stages:
            bad = copy.deepcopy(stages)
            bad[key]["state"] = "Blocked"
            with self.subTest(key=key):
                self.assertEqual(cycle.assess_summary(bad, native, after)["result"],
                                 "ReturnRequired")
        self.assertEqual(cycle.assess_summary(stages, None, after)["result"], "ReturnRequired")
        self.assertEqual(cycle.assess_summary(stages, native, None)["result"], "ReturnRequired")
        bad = copy.deepcopy(stages)
        bad["unexpected-error"] = {"state": "Failed"}
        self.assertEqual(cycle.assess_summary(bad, native, after)["result"], "ReturnRequired")

    def test_18_manifest_is_receipt_only_not_original_archive_claim(self):
        script = Path(cycle.__file__).read_text(encoding="utf-8")
        self.assertIn("externalChildEvidenceSealedHere", script)
        self.assertIn("independentR03FullStageReview", script)
        self.assertNotIn("def accept_r03(", script)
        self.assertIn("run_terminal_current.py", script)
        self.assertIn("audit_s_process_joins.py", script)
        self.assertNotIn("worktree remove --force", script)

    def test_19_machine_gate_requires_real_arm_mac_without_exceptions(self):
        with self.assertRaises(ValueError):
            cycle.validate_machine(self.base / "fake-unity", self.output)
        self.assertEqual(cycle.MIN_FREE_GIB, 20)

    def test_20_explicit_script_does_not_touch_original_test_discovery(self):
        self.assertFalse(Path(cycle.__file__).name.startswith("test_"))
        self.assertFalse(Path(__file__).name.startswith("test_"))
        self.assertEqual(cycle.S_PUBLICATION, cycle.S_PUBLICATION.lower())

    def test_21_installed_parity_independent_of_failed_player_semantics(self):
        source_text = Path(cycle.__file__).read_text(encoding="utf-8")
        self.assertIn("installed.admit_sealed_three_builds(batch_receipt, args.demo_commit)",
                      source_text)
        self.assertIn('"Exact sealed three successful native builds absent"', source_text)
        self.assertIn('"siblingPlayerSemanticsAccepted"', source_text)
        self.assertIn('stages["current-native-players"]["state"] = "Failed"',
                      source_text)
        self.assertIn("verify_current_batch(", source_text)
        self.assertLess(source_text.index("installed.admit_sealed_three_builds("),
                        source_text.index('stages["native-installed-source-audit"] = run_step('))
        stages = self.all_passed()
        stages["current-native-players"] = {"state": "Failed"}
        self.assertEqual(cycle.assess_summary(stages, None,
            {"result": "PassedReadOnlySourceAdmission_NotBuildOrRuntime"})["result"],
            "ReturnRequired")


    def test_22_actual_retained_oneuse_i_positive_child_receipt(self):
        # Exact original published I child bytes copied to the current-source
        # test tree. Its real child passed, but I's *outer* result stays FAIL.
        archive = Path(__file__).resolve().parent / (
            "fixtures/retained_oneuse_i_LOCAL_BATCH_RESULT.json")
        raw = archive.read_bytes()
        self.assertEqual(cycle.source.git_blob(raw),
                         "d7209e369f481bb91df3bd697046ae9447f5b255")
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "a2a4fc891f26151ff1e0822214e0625fe409a7be3cf7c95b1e941838f3363224")
        original_demo = "c707141204265a8111f1f5928515fc8cf28abfee"
        historical = json.loads(raw)
        # The I child was source-accurate under 41764..., not the current
        # a020... native. Preserve the original scoped child/outer FAIL;
        # never silently rebind it to a later B1 checkout or label it Passed.
        self.assertEqual(historical["repositories"]["il2cpp_plus"],
                         "41764ae1eeefb33b05966e7f7676e52aae39c340")
        self.assertIs(historical["R03Accepted"], False)
        with self.assertRaises(cycle.source.CandidateSourceError):
            cycle.verify_current_batch(archive, original_demo)

    def test_23_complete_repo_metadata_is_required_and_typed(self):
        fields = (
            ("schemaVersion", True), ("schemaVersion", "1"),
            ("schemaVersion", 2), ("branch", "main"), ("phase", "runtime"),
            ("runtimeAcceptance", 0), ("runtimeAcceptance", True),
            ("hybridclr_demo", "b" * 40),
            ("il2cpp_plus", "0" * 40),
        )
        for field, value in fields:
            with self.subTest(field=field, value=value):
                receipt = self.fake_result()
                receipt["repositories"][field] = value
                with self.assertRaises(ValueError):
                    self.read_batch(receipt)
        for key in ("schemaVersion", "branch", "phase", "runtimeAcceptance"):
            with self.subTest(missing=key):
                receipt = self.fake_result()
                del receipt["repositories"][key]
                with self.assertRaises(ValueError):
                    self.read_batch(receipt)
        receipt = self.fake_result()
        receipt["repositories"]["extra"] = "unreviewed"
        with self.assertRaises(ValueError):
            self.read_batch(receipt)

    def test_24_retained_i_source_is_not_rebound_or_promoted(self):
        fixture = Path(__file__).resolve().parent / (
            "fixtures/retained_oneuse_i_LOCAL_BATCH_RESULT.json")
        old = json.loads(fixture.read_bytes())
        self.assertEqual(old["repositories"]["il2cpp_plus"],
                         "41764ae1eeefb33b05966e7f7676e52aae39c340")
        with self.assertRaises(cycle.source.CandidateSourceError):
            self.read_batch(old, "c707141204265a8111f1f5928515fc8cf28abfee")
        current_synthetic = self.fake_result()
        current_synthetic["repositories"]["branch"] = "different-branch"
        with self.assertRaises(cycle.source.CandidateSourceError):
            self.read_batch(current_synthetic)

    def test_25_duplicate_or_failed_child_and_boolean_counts_rejected(self):
        for scenario in ("duplicate", "missing", "failed-prepare",
                         "boolean-build-count", "false-fixture-hash"):
            with self.subTest(scenario=scenario):
                rec = self.fake_result()
                if scenario == "duplicate":
                    rec["cells"][0]["id"] = rec["cells"][1]["id"]
                if scenario == "missing":
                    rec["cells"].pop(0)
                if scenario == "failed-prepare":
                    rec["cells"][4]["result"] = "Blocked"
                if scenario == "boolean-build-count":
                    rec["verifiedFreshBuilds"] = True
                if scenario == "false-fixture-hash":
                    rec["originalSFixtureAuthoritySha256"] = "not-sha256"
                with self.assertRaises(ValueError):
                    self.read_batch(rec)

    def test_26_duplicate_json_keys_cannot_mask_source_identity(self):
        rec = self.fake_result()
        text = json.dumps(rec)
        self.assertIn('"repositories": {', text)
        text = text.replace('"repositories": {', '"repositories": {"branch": "main",', 1)
        p = self.base / "duplicate.json"
        p.write_text(text, encoding="utf-8")
        with self.assertRaises(ValueError):
            cycle.verify_current_batch(p, "a" * 40)



if __name__ == "__main__":
    unittest.main(verbosity=2)
