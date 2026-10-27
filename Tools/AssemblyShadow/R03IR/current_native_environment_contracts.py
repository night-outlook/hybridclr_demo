#!/usr/bin/env python3
"""Host-only adversarial tests for retained-fc55 and .NET/storage readmission.

No actual retained worktree, runtime/toolchain installation, Unity or build is
touched. Only temporary tiny fixtures and mocked read-only commands are used.
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import current_native_environment_admission as gate


SDK8 = "8.0.414 [/opt/dotnet/sdk]"
SDK10 = "10.0.101 [/opt/dotnet/sdk]"
RUNTIME8 = "Microsoft.NETCore.App 8.0.22 [/opt/dotnet/shared/Microsoft.NETCore.App]"
RUNTIME10 = "Microsoft.NETCore.App 10.0.1 [/opt/dotnet/shared/Microsoft.NETCore.App]"


class R03RetainedOriginalReadmissionContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r03-env-retained-")
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name).resolve(strict=True)
        self.workspace = root / "workspace"
        self.workspace.mkdir()
        for name in gate.cycle.REPOS:
            (self.workspace / name).mkdir()
        self.original = root / "original-fc55"
        self.original.mkdir()
        self.output = root / "evidence" / "fresh-oneuse-B"
        self.output.parent.mkdir()
        self.unity = root / "Unity"
        self.unity.write_bytes(b"test-unity-executable-only")
        self.commit = "a" * 40

    def test_01_sdk8_with_matching_runtime_passes(self):
        v = gate.verify_sdk_output(SDK8, RUNTIME8)
        self.assertTrue(v["net8ToolchainAvailable"])
        self.assertEqual(v["sdkVersions"], ["8.0.414"])

    def test_02_sdk10_with_net8_runtime_is_supported(self):
        v = gate.verify_sdk_output(SDK10, RUNTIME10 + "\n" + RUNTIME8)
        self.assertTrue(v["net8ToolchainAvailable"])
        self.assertEqual(len(v["net8RuntimeLines"]), 1)

    def test_03_dotnet_sdk_missing_is_blocked(self):
        with self.assertRaisesRegex(ValueError, "SDK >=8"):
            gate.verify_sdk_output("7.0.400 [/opt/dotnet/sdk]", RUNTIME8)

    def test_04_net8_runtime_missing_is_blocked(self):
        with self.assertRaisesRegex(ValueError, "8.x runtime"):
            gate.verify_sdk_output(SDK10, RUNTIME10)

    def test_05_empty_toolchain_lists_are_not_a_pass(self):
        with self.assertRaises(ValueError):
            gate.verify_sdk_output("", "")

    def test_06_invented_or_malformed_sdk_receipt_is_rejected(self):
        with self.assertRaises(ValueError):
            gate.verify_sdk_output("SDK 10 available", RUNTIME8)

    def test_07_exact_threshold_20gib_is_unchanged(self):
        free = 20 * 1024**3
        r = gate.sample_capacity(self.output, free_bytes=free)
        self.assertEqual(r["hardMinimumGiB"], 20)
        self.assertFalse(r["thresholdLowered"])
        self.assertTrue(r["belowAdvisory"])
        self.assertFalse(r["futureUnityDiskUseGuaranteed"])

    def test_08_original_19_63gib_sample_is_blocked(self):
        with self.assertRaisesRegex(ValueError, "20-GiB"):
            gate.sample_capacity(self.output, free_bytes=21074190336)

    def test_09_passive_20_29gib_is_only_a_current_sample(self):
        result = gate.sample_capacity(self.output, free_bytes=21783199744)
        self.assertEqual(result["result"], "PassedCurrentFreeSample_NotSustainedCapacity")
        self.assertTrue(result["belowAdvisory"])

    def test_10_ample_alternate_volume_is_recorded_without_claiming_acceptance(self):
        result = gate.sample_capacity(self.output, free_bytes=70 * 1024**3)
        self.assertFalse(result["belowAdvisory"])
        self.assertFalse(result["futureUnityDiskUseGuaranteed"])

    def test_11_same_failed_A_root_is_not_required_for_new_readmission(self):
        gate.cycle.validate_destination(self.workspace, self.original, self.output)
        self.assertFalse(self.output.exists())

    def test_12_an_existing_output_root_is_rejected(self):
        self.output.mkdir()
        with self.assertRaises(ValueError):
            gate.cycle.validate_destination(self.workspace, self.original, self.output)

    def test_13_symlinked_output_parent_is_rejected(self):
        alias = self.output.parent.parent / "alias"
        alias.symlink_to(self.output.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            gate.cycle.validate_destination(self.workspace, self.original, alias / "bad")

    def test_14_registered_original_fc55_is_accepted_without_creating_worktree(self):
        git_roster = ("worktree " + str(self.workspace / "hybridclr_demo") +
                      "\nHEAD " + self.commit + "\nbranch refs/heads/example\n\n"
                      "worktree " + str(self.original) + "\nHEAD " +
                      gate.cycle.S_PUBLICATION + "\ndetached")
        with mock.patch.object(gate, "run_read_only", return_value=git_roster), \
             mock.patch.object(gate.cycle, "validate_original",
                               return_value={"clean": True, "commit": gate.cycle.S_PUBLICATION}):
            result = gate.registered_original(self.workspace, self.original)
        self.assertEqual(result["result"], "PassedRegisteredRetainedWorktreeReadOnly")
        self.assertFalse(result["worktreeCreatedOrReplaced"])

    def test_15_unregistered_original_is_rejected(self):
        with mock.patch.object(gate, "run_read_only", return_value=(
            "worktree " + str(self.workspace / "hybridclr_demo") +
            "\nHEAD " + self.commit + "\nbranch refs/heads/example")):
            with self.assertRaisesRegex(ValueError, "not singly registered"):
                gate.registered_original(self.workspace, self.original)

    def test_16_original_registered_at_wrong_commit_is_rejected(self):
        with mock.patch.object(gate, "run_read_only", return_value=(
            "worktree " + str(self.original) + "\nHEAD " + self.commit + "\ndetached")):
            with self.assertRaises(ValueError):
                gate.registered_original(self.workspace, self.original)

    def test_17_original_registered_not_detached_is_rejected(self):
        with mock.patch.object(gate, "run_read_only", return_value=(
            "worktree " + str(self.original) + "\nHEAD " +
            gate.cycle.S_PUBLICATION + "\nbranch refs/heads/master")):
            with self.assertRaises(ValueError):
                gate.registered_original(self.workspace, self.original)

    def test_18_duplicate_worktree_registration_is_rejected(self):
        one = ("worktree " + str(self.original) + "\nHEAD " +
               gate.cycle.S_PUBLICATION + "\ndetached")
        with mock.patch.object(gate, "run_read_only", return_value=one + "\n\n" + one):
            with self.assertRaises(ValueError):
                gate.registered_original(self.workspace, self.original)

    def test_19_missing_dotnet_executable_is_blocked(self):
        with mock.patch.object(gate.shutil, "which", return_value=None):
            with self.assertRaisesRegex(ValueError, "dotnet"):
                gate.resolved_command("dotnet")

    def test_20_actual_project_source_is_pinned_to_net8(self):
        script = Path(gate.__file__).read_text(encoding="utf-8")
        self.assertIn("REQUIRED_CSPROJ_BLOB", script)
        self.assertIn('frameworks == ["net8.0"]', script)
        self.assertIn("Microsoft.NETCore.App 8.", script)

    def test_21_preflight_is_explicitly_non_execution(self):
        script = Path(gate.__file__).read_text(encoding="utf-8")
        self.assertNotIn("worktree add", script)
        self.assertNotIn("run_terminal_current.py", script)
        self.assertNotIn(".mkdir(", script)
        self.assertIn("runRootCreated", script)
        self.assertIn("coordinatorInvoked", script)

    def test_22_positive_simulated_check_never_creates_output(self):
        with mock.patch.object(gate.cycle, "validate_destination"), \
             mock.patch.object(gate, "registered_original", return_value={"result": "Passed"}), \
             mock.patch.object(gate.cycle, "validate_sources", return_value={"result": "Passed"}), \
             mock.patch.object(gate.cycle, "validate_machine", return_value={"result": "Passed"}), \
             mock.patch.object(gate, "verify_toolchain", return_value={"net8": True}), \
             mock.patch.object(gate, "sample_capacity", return_value={"result": "Passed"}):
            result = gate.inspect(self.workspace, self.original, self.unity,
                                  self.output, self.commit)
        self.assertEqual(result["result"], "PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun")
        self.assertFalse(result["coordinatorInvoked"])
        self.assertFalse(self.output.exists())

    def test_23_source_failure_does_not_create_a_batch(self):
        with mock.patch.object(gate.cycle, "validate_destination"), \
             mock.patch.object(gate, "registered_original", return_value={"result": "Passed"}), \
             mock.patch.object(gate.cycle, "validate_sources", side_effect=ValueError("source drift")):
            with self.assertRaisesRegex(ValueError, "source drift"):
                gate.inspect(self.workspace, self.original, self.unity, self.output, self.commit)
        self.assertFalse(self.output.exists())

    def test_24_missing_toolchain_does_not_create_a_batch(self):
        with mock.patch.object(gate.cycle, "validate_destination"), \
             mock.patch.object(gate, "registered_original", return_value={"result": "Passed"}), \
             mock.patch.object(gate.cycle, "validate_sources", return_value={"result": "Passed"}), \
             mock.patch.object(gate.cycle, "validate_machine", return_value={"result": "Passed"}), \
             mock.patch.object(gate, "verify_toolchain", side_effect=ValueError("dotnet missing")):
            with self.assertRaises(ValueError):
                gate.inspect(self.workspace, self.original, self.unity, self.output, self.commit)
        self.assertFalse(self.output.exists())


    def test_25_actual_net8_fixture_source_is_rechecked(self):
        current_demo = Path(gate.__file__).resolve().parents[3]
        result = gate.fixture_net8_source(current_demo.parent)
        self.assertEqual(result["targetFramework"], "net8.0")
        self.assertEqual(result["gitBlob"], gate.REQUIRED_CSPROJ_BLOB)


if __name__ == "__main__":
    unittest.main(verbosity=2)
