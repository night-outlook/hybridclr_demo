#!/usr/bin/env python3
"""Real subprocess contracts for R03 current-native CLI import bootstrap.

Every positive test launches a fresh interpreter from a foreign cwd, without
PYTHONPATH, with no Unity/IL2CPP/SDK, no Local output root and no Player.
Historical runner, fixture and source pins must stay byte-identical.
The test file is explicitly run, not picked up by old test_*.py discovery.
"""
from __future__ import annotations

import ast
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import current_native_environment_admission as admission

HERE = Path(__file__).resolve().parent
RUNNER = HERE / "run_terminal_current.py"
DEMO = HERE.parents[2]
R03 = HERE.parent / "R03"
BLOB_PINS = {
    "Tools/AssemblyShadow/R03/run_local.py": "9aef8093f98fb7f9b5dd395ba4e5c2ed0220276e",
    "Tools/AssemblyShadow/R03IR/run_terminal_local.py": "70b1a27f2dbbcad93f67e8caddcf7282ff3afd73",
    "Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs":
        "598feeec3231707091699d99fbf4428d50b52024",
    "Tools/AssemblyShadow/R03/source-pins.json": "9d72a237fb6ecd3efe3267ca89625aa49c61775d",
    "Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs":
        "b993703d918090733a659bd7c3ac883cd5d753e1",
    "Tools/AssemblyShadow/R03IR/run_current_native_validation_cycle.py":
        "d03f0e754213bd7219028ccb0aad534b87e89b61",
}
HEX40 = "0" * 40


def blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(payload)).encode("ascii") + b"\x00" + payload
    ).hexdigest()


class StandaloneCliBootstrapContracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="r03-cli-external-")
        self.addCleanup(self.tmp.cleanup)
        self.outside = Path(self.tmp.name).resolve(strict=True)
        self._clean_env = dict(os.environ)
        for name in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP"):
            self._clean_env.pop(name, None)
        self._clean_env["PYTHONDONTWRITEBYTECODE"] = "1"
        self._clean_env["PYTHONNOUSERSITE"] = "1"

    def subprocess(self, *argv, env=None, cwd=None):
        result = subprocess.run(
            [sys.executable, "-B", str(RUNNER), *[str(x) for x in argv]],
            cwd=cwd or self.outside,
            env=env or self._clean_env,
            text=True, capture_output=True, timeout=30, check=False,
        )
        return result

    def test_01_exact_script_paths_are_owning_repository(self):
        self.assertTrue(RUNNER.is_file())
        self.assertTrue((R03 / "run_local.py").is_file())
        self.assertEqual(RUNNER.parent, HERE)
        self.assertEqual(R03, HERE.parent / "R03")

    def test_02_actual_fresh_interpreter_help_from_external_cwd(self):
        proc = self.subprocess("--help")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("--demo-commit", proc.stdout)
        self.assertIn("--workspace", proc.stdout)
        self.assertIn("--output", proc.stdout)
        self.assertEqual(proc.stderr, "")

    def test_03_help_is_independent_of_unity_installed(self):
        self.assertEqual(self.subprocess("--help").returncode, 0)
        self.assertFalse((self.outside / "Unity").exists())

    def test_04_help_needs_no_pythonpath(self):
        self.assertNotIn("PYTHONPATH", self._clean_env)
        p = self.subprocess("--help")
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_05_cwd_cannot_supply_fake_run_local(self):
        (self.outside / "run_local.py").write_text(
            "raise RuntimeError('never import from current working directory')\n")
        p = self.subprocess("--help")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertNotIn("never import", p.stderr)

    def test_06_no_assisted_pythonpath_even_when_poisoned(self):
        fake = self.outside / "poison"
        fake.mkdir()
        (fake / "run_local.py").write_text(
            "raise RuntimeError('unsafe PYTHONPATH resolved instead of owning R03')\n")
        env = dict(self._clean_env, PYTHONPATH=str(fake))
        p = self.subprocess("--help", env=env)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertNotIn("unsafe PYTHONPATH", p.stderr)

    def test_07_missing_arguments_fail_in_argparse(self):
        p = self.subprocess()
        self.assertEqual(p.returncode, 2)
        self.assertIn("required", p.stderr)
        self.assertNotIn("ModuleNotFoundError", p.stderr)

    def test_08_legacy_source_sha_invalid_refused_before_output(self):
        target = self.outside / "not-created"
        p = self.subprocess("--workspace", self.outside,
                            "--output", target,
                            "--unity", self.outside / "not-unity",
                            "--demo-commit", "HEAD")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("Exact committed demo HEAD required", p.stderr)
        self.assertFalse(target.exists())

    def test_09_relative_workspace_rejected_without_output(self):
        p = self.subprocess("--workspace", "relative-workspace",
                            "--output", self.outside / "absent",
                            "--unity", self.outside / "none",
                            "--demo-commit", HEX40)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("Canonical absolute workspace/output paths required", p.stderr)
        self.assertFalse((self.outside / "absent").exists())

    def test_10_relative_output_rejected_without_output(self):
        p = self.subprocess("--workspace", self.outside,
                            "--output", "relative-output",
                            "--unity", self.outside / "none",
                            "--demo-commit", HEX40)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("Canonical absolute workspace/output paths required", p.stderr)
        self.assertFalse((self.outside / "relative-output").exists())

    def test_11_foreign_absolute_workspace_rejected_before_batch(self):
        output = self.outside / "never-created"
        p = self.subprocess("--workspace", self.outside,
                            "--output", output,
                            "--unity", self.outside / "none",
                            "--demo-commit", HEX40)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("Execute from the owning exact demo checkout", p.stderr)
        self.assertNotIn("ModuleNotFoundError", p.stderr)
        self.assertFalse(output.exists())

    def test_12_old_source_files_are_pinned_without_edit(self):
        for relative, pin in BLOB_PINS.items():
            with self.subTest(relative=relative):
                path = DEMO / relative
                self.assertEqual(blob_sha(path), pin, relative)

    def test_13_import_bootstrap_precedes_first_run_local_import(self):
        tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
        imports = [(i, n) for i, n in enumerate(tree.body)
                   if isinstance(n, ast.ImportFrom) and n.module == "run_local"]
        self.assertEqual(len(imports), 1)
        import_idx = imports[0][0]
        bootstrap = [(i, n) for i, n in enumerate(tree.body)
                     if isinstance(n, ast.Expr)
                     and isinstance(n.value, ast.Call)
                     and isinstance(n.value.func, ast.Attribute)
                     and n.value.func.attr == "insert"
                     and isinstance(n.value.func.value, ast.Attribute)
                     and n.value.func.value.attr == "path"]
        self.assertTrue(bootstrap)
        self.assertLess(bootstrap[0][0], import_idx)

    def test_14_existing_focused_runner_is_still_injected(self):
        content = RUNNER.read_text(encoding="utf-8")
        self.assertIn("batch_type=CurrentNativeBatch", content)
        self.assertIn("run_existing_focused_batch(", content)
        self.assertIn("require_checkout_heads=True", content)
        self.assertIn("self.pins = candidate_pins(", content)

    def test_15_wrapper_does_not_add_a_fake_dry_run(self):
        proc = self.subprocess("--help")
        self.assertNotIn("--dry-run", proc.stdout)
        self.assertNotIn("--skip", proc.stdout)
        self.assertFalse((self.outside / "BATCH_EXECUTION.json").exists())

    def test_16_source_only_cli_help_creates_no_local_evidence(self):
        before = set(self.outside.iterdir())
        proc = self.subprocess("--help")
        after = set(self.outside.iterdir())
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(after, before)

    def test_17_fresh_process_module_import_also_bootstraps_r03(self):
        # -c has no script directory on sys.path; only the R03IR package
        # directory is supplied, never its sibling R03 infrastructure.
        cmd = [
            sys.executable, "-B", "-c",
            "import sys; sys.path.insert(0, " + repr(str(HERE)) +
            "); import run_terminal_current as module; " +
            "print(module.CurrentNativeBatch.__name__)"
        ]
        proc = subprocess.run(
            cmd, cwd=self.outside, env=self._clean_env,
            text=True, capture_output=True, timeout=30, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "CurrentNativeBatch")
        self.assertEqual(proc.stderr, "")

    def test_18_old_terminal_runner_bootstrap_remains_unchanged(self):
        legacy = (HERE / "run_terminal_local.py").read_text(encoding="utf-8")
        self.assertIn("sys.path.insert(0, str(R03))", legacy)
        self.assertIn("from run_local import Batch, ROOT, REPOS", legacy)

    def test_19_no_unity_or_compiler_in_wrapper_cli(self):
        wrapper = RUNNER.read_text(encoding="utf-8")
        self.assertNotIn("subprocess.Popen(", wrapper)
        self.assertNotIn("-executeMethod", wrapper)
        self.assertNotIn("dotnet build", wrapper)
        self.assertFalse((self.outside / "current-native").exists())


    def test_20_real_readonly_admission_runs_same_fresh_cli(self):
        output = self.outside / "new-batch-never-created"
        report = admission.verify_standalone_current_cli(DEMO.parent, output)
        self.assertEqual(report["result"],
                         "PassedFreshPythonProcessHelp_NoUnityOrRuntime")
        self.assertFalse(report["pythonPathProvided"])
        self.assertFalse(report["unityOrPlayerLaunched"])
        self.assertFalse(report["runtimeAcceptance"])
        self.assertFalse(output.exists())

    def test_21_readonly_probe_cannot_accept_missing_runner(self):
        foreign_workspace = self.outside / "foreign-workspace"
        foreign_workspace.mkdir()
        output = self.outside / "still-not-created"
        with self.assertRaisesRegex(ValueError, "unavailable"):
            admission.verify_standalone_current_cli(foreign_workspace, output)
        self.assertFalse(output.exists())

    def test_22_readonly_probe_rejects_forged_import_failure(self):
        with mock.patch.object(
                admission.subprocess, "run",
                return_value=subprocess.CompletedProcess(
                    args=[], returncode=1, stdout="",
                    stderr="ModuleNotFoundError: No module named 'run_local'")
        ):
            with self.assertRaisesRegex(ValueError, "Standalone current-native"):
                admission.verify_standalone_current_cli(
                    DEMO.parent, self.outside / "output")
        self.assertFalse((self.outside / "output").exists())

    def test_23_readonly_probe_strips_assisting_pythonpath(self):
        help_message = ("usage: current\n --demo-commit commit\n"
                        "--workspace workspace\n--output output\n")
        with mock.patch.dict(os.environ, {"PYTHONPATH": "/poison/path",
                                           "PYTHONHOME": "/poison/home"}), \
             mock.patch.object(
                 admission.subprocess, "run",
                 return_value=subprocess.CompletedProcess(
                     args=[], returncode=0, stdout=help_message, stderr="")
             ) as run:
            report = admission.verify_standalone_current_cli(
                DEMO.parent, self.outside / "output")
        self.assertEqual(report["result"],
                         "PassedFreshPythonProcessHelp_NoUnityOrRuntime")
        kwargs = run.call_args.kwargs
        self.assertNotIn("PYTHONPATH", kwargs["env"])
        self.assertNotIn("PYTHONHOME", kwargs["env"])
        self.assertEqual(kwargs["cwd"], str(self.outside))
        self.assertEqual(run.call_args.args[0][-1], "--help")


if __name__ == "__main__":
    unittest.main(verbosity=2)
