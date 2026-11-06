#!/usr/bin/env python3
"""Exact-current initializer readmission regression, host-only.

This checks the real committed csproj/producer/entry source, the actual fresh
Python CLI startup, and fail-closed mutations. Every artificial external
requirement is labelled as a mock; no Unity, Player, archive or Local root runs.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import current_native_environment_admission as gate

HERE = Path(__file__).resolve().parent
DEMO = HERE.parents[2]
WORKSPACE = DEMO.parent
FIXTURE = DEMO / "Tools/AssemblyShadow/R03/PlayerFixtures"
FILES = ("PlayerFixtures.csproj", "InitializerNativeTargetFixtures.cs", "Program.cs")
RUNNER = HERE / "run_initializer_local.py"


class InitializerAdmissionContracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="r03-init02-admission-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve(strict=True)
        self.external = self.root / "new-absent-local-root"
        self.isolated = self.root / "work" / "hybridclr_demo/Tools/AssemblyShadow/R03/PlayerFixtures"
        self.isolated.mkdir(parents=True)
        for name in FILES:
            shutil.copyfile(FIXTURE / name, self.isolated / name)

    def inspected(self):
        return gate.fixture_net8_source(self.root / "work")

    def test_01_real_current_sources_pass_without_relabeling_old_blob(self):
        record = gate.fixture_net8_source(WORKSPACE)
        self.assertEqual(record["gitBlob"], "1c5c8628ead41d67d94bb1846dd5bf9764620c68")
        self.assertEqual(record["initializerSourceGitBlob"],
                         "da4bf2ece4999d2765ca51d4bdeecf2bc0617fd2")
        self.assertEqual(record["programSourceGitBlob"],
                         "c8de453c03321a5b91635da7c6ed795664bcb975")
        self.assertIs(record["initializerCompileIncludedExactlyOnce"], True)
        self.assertEqual(record["targetFramework"], "net8.0")
        self.assertNotEqual(record["gitBlob"], "249c47c1b453fc0cd3520173122599ca03cbe78c")

    def test_02_exact_copy_passes_and_no_output_created(self):
        self.assertEqual(self.inspected()["gitBlob"], gate.REQUIRED_CSPROJ_BLOB)
        self.assertFalse(self.external.exists())

    def test_03_preinitializer_project_without_new_compile_is_rejected(self):
        path = self.isolated / "PlayerFixtures.csproj"
        text = path.read_text(encoding="utf-8")
        self.assertIn('<Compile Include="InitializerNativeTargetFixtures.cs"/>', text)
        path.write_text(text.replace('<Compile Include="InitializerNativeTargetFixtures.cs"/>', ''))
        with self.assertRaisesRegex(ValueError, "fixture project source identity"):
            self.inspected()
        self.assertFalse(self.external.exists())

    def test_04_duplicate_or_extra_compile_is_rejected(self):
        path = self.isolated / "PlayerFixtures.csproj"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace(
            '<Compile Include="InitializerNativeTargetFixtures.cs"/>',
            '<Compile Include="InitializerNativeTargetFixtures.cs"/>' * 2))
        with self.assertRaisesRegex(ValueError, "fixture project source identity"):
            self.inspected()
        self.assertFalse(self.external.exists())

    def test_05_net8_change_and_whitespace_tamper_are_rejected(self):
        path = self.isolated / "PlayerFixtures.csproj"
        original = path.read_bytes()
        for change in (original.replace(b'net8.0', b'net10.0'), original + b'\n'):
            with self.subTest(change=change[-15:]):
                path.write_bytes(change)
                with self.assertRaisesRegex(ValueError, "fixture project source identity"):
                    self.inspected()
        self.assertFalse(self.external.exists())

    def test_06_changed_and_missing_native_fixture_producer_fail(self):
        path = self.isolated / "InitializerNativeTargetFixtures.cs"
        old = path.read_bytes()
        path.write_bytes(old + b'\n// changed\n')
        with self.assertRaisesRegex(ValueError, "initializer fixture producer source identity"):
            self.inspected()
        path.unlink()
        with self.assertRaisesRegex(ValueError, "initializer fixture producer source identity"):
            self.inspected()
        self.assertFalse(self.external.exists())

    def test_07_program_producer_entry_change_fails(self):
        path = self.isolated / "Program.cs"
        text = path.read_text(encoding="utf-8")
        self.assertIn("--ir-terminal-native-targets", text)
        path.write_text(text.replace("--ir-terminal-native-targets", "--unreviewed-mode"))
        with self.assertRaisesRegex(ValueError, "fixture generator entry source identity"):
            self.inspected()

    def test_08_linked_project_file_does_not_pass(self):
        path = self.isolated / "PlayerFixtures.csproj"
        old = self.root / "saved.csproj"
        old.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(old)
        with self.assertRaisesRegex(ValueError, "fixture project source identity"):
            self.inspected()
        self.assertFalse(self.external.exists())

    def test_09_real_initializer_cli_starts_in_fresh_foreign_process(self):
        clean = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1")
        for key in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP"):
            clean.pop(key, None)
        completed = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--help"],
            cwd=self.root, env=clean, text=True, capture_output=True, timeout=45)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--demo-commit", completed.stdout)
        self.assertIn("--original-s", completed.stdout)
        self.assertIn("--workspace", completed.stdout)
        self.assertIn("--output", completed.stdout)
        self.assertNotIn("ModuleNotFoundError", completed.stderr)
        self.assertFalse(self.external.exists())

    def test_10_actual_readmission_chain_with_real_fixture_and_cli(self):
        """External Mac/Git/SDK remain mocked; real source and CLI are not."""
        with mock.patch.object(gate.cycle, "validate_destination"), \
             mock.patch.object(gate, "registered_original", return_value={"result": "MockedOriginalOnly"}), \
             mock.patch.object(gate.cycle, "validate_sources", return_value={"result": "MockedGitOnly"}), \
             mock.patch.object(gate.cycle, "validate_machine", return_value={"result": "MockedMacOnly"}), \
             mock.patch.object(gate, "verify_toolchain",
                 side_effect=lambda workspace: {"fixture": gate.fixture_net8_source(workspace),
                                                "hostTools": "MockedExternalSDKOnly"}), \
             mock.patch.object(gate, "sample_capacity", return_value={"result": "MockedCapacityOnly"}):
            receipt = gate.inspect(
                WORKSPACE, self.root / "original-not-inspected",
                self.root / "Unity-not-launched", self.external, "a" * 40)
        self.assertEqual(receipt["result"],
                         "PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun")
        self.assertEqual(receipt["toolchain"]["fixture"]["gitBlob"],
                         gate.REQUIRED_CSPROJ_BLOB)
        self.assertEqual(receipt["standaloneCurrentNativeCli"]["result"],
                         "PassedFreshPythonProcessHelp_NoUnityOrRuntime")
        self.assertIs(receipt["coordinatorInvoked"], False)
        self.assertFalse(self.external.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
