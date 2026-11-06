#!/usr/bin/env python3
"""Host-only capacity readiness safety contracts. NEVER a real Mac GO."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import capacity_readiness as cap


class ReadOnlyCapacityContracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="r03-oneuse05-capacity-",
                                               dir=Path.home().resolve(strict=True))
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve(strict=True)
        self.parent = self.root / "r03-local-validation"
        self.parent.mkdir()
        self.workspace = self.root / "assembly_shadow_h1r"
        self.workspace.mkdir()
        self.original = self.root / "OriginalS"
        self.original.mkdir()
        (self.original / "evidence.bin").write_bytes(b"do-not-change-original")
        self.unity = self.root / "Unity.app/Contents/MacOS/Unity"
        self.unity.parent.mkdir(parents=True)
        self.unity.write_bytes(b"host-unit-unity-not-real-executable")
        self.run = self.parent / "R03IR-Initializer-20261106-oneuse-05"
        self.host = self.parent / (self.run.name + "-native-host-raw")
        self.candidate = self.root / "explicit-unprotected-cache"
        self.candidate.mkdir()
        (self.candidate / "user-owned-disposable.dat").write_bytes(b"not-deletable-by-script")
        (self.candidate / "link-to-evidence").symlink_to(self.original, target_is_directory=True)

    def probe(self, **kw):
        args = dict(parent=self.parent, run_root=self.run, host_root=self.host,
                    workspace=self.workspace, original_s=self.original, unity=self.unity)
        args.update(kw)
        return cap.inspect(**args)

    def test_01_25gib_exact_floor_and_fixed_20_40(self):
        for free, passed in ((0, False), (24 * cap.GIB, False),
                             (25 * cap.GIB - 1, False),
                             (25 * cap.GIB, True),
                             (40 * cap.GIB, True)):
            with self.subTest(free=free):
                result = cap.capacity_state(free)
                self.assertEqual(result["state"] ==
                                 "ReadySingleSample_NotBatchAuthorized", passed)
                self.assertEqual(result["minimumBytes"], 26843545600)
                self.assertEqual((result["hardMinimumGiB"],
                                  result["minimumGiB"],
                                  result["advisoryGiB"]), (20, 25, 40))
                self.assertIs(result["thresholdLowered"], False)
                self.assertIs(result["twoIndependentSamplesCompleted"], False)
                self.assertIs(result["runtimeAcceptance"], False)

    def test_02_actual_samples_are_independent_and_no_go_claim(self):
        with patch.object(cap.os, "statvfs", return_value=type("S", (), {
            "f_bavail": (25 * cap.GIB) // 4096, "f_frsize": 4096})()):
            observed = self.probe()
        self.assertEqual(observed["result"], "ReadySingleSample_NotBatchAuthorized")
        self.assertIs(observed["eligibleForUnityRun"], False)
        self.assertIs(observed["requiresSecondIndependentSample"], True)
        self.assertEqual(observed["capacity"]["freeBytes"], 25 * cap.GIB)
        self.assertFalse(self.run.exists())
        self.assertFalse(self.host.exists())

    def test_03_latest_failed_local_sample_is_blocked(self):
        outcome = cap.capacity_state(26553147392)
        self.assertEqual(outcome["state"], "CapacityBlocked")
        self.assertEqual(outcome["bytesBelowMinimum"], 290398208)
        self.assertIs(outcome["thresholdLowered"], False)

    def test_04_explicit_outside_candidate_link_is_not_followed(self):
        old_bytes = (self.original / "evidence.bin").read_bytes()
        snapshot = sorted(str(p) for p in self.root.rglob("*"))
        report = self.probe(candidates=(self.candidate,))
        row = report["explicitCandidateInspectionOnly"][0]
        self.assertEqual(row["symlinksNotFollowed"], 1)
        self.assertEqual(row["regularFiles"], 1)
        self.assertEqual(row["classification"],
                         "ReadOnlyCandidateEstimate_NotDeletionApproval")
        self.assertIs(row["deletionApproved"], False)
        self.assertEqual(row["deleteOrModifyOperations"], 0)
        self.assertTrue((self.candidate / "link-to-evidence").is_symlink())
        self.assertEqual((self.original / "evidence.bin").read_bytes(), old_bytes)
        self.assertEqual(sorted(str(p) for p in self.root.rglob("*")), snapshot)
        self.assertFalse(self.run.exists())

    def test_05_protected_and_parent_candidates_rejected(self):
        for candidate in (self.original, self.workspace, self.parent,
                          self.root, self.unity.parent.parent.parent):
            with self.subTest(path=candidate), self.assertRaises(cap.CapacityReadinessError):
                self.probe(candidates=(candidate,))
        self.assertFalse(self.run.exists())

    def test_06_candidate_root_symlink_rejected(self):
        link = self.root / "external-alias"
        link.symlink_to(self.candidate, target_is_directory=True)
        with self.assertRaises(cap.CapacityReadinessError):
            self.probe(candidates=(link,))
        self.assertFalse(self.run.exists())

    def test_07_reused_product_or_host_root_is_rejected(self):
        self.run.mkdir()
        with self.assertRaises(cap.CapacityReadinessError):
            self.probe()
        self.run.rmdir()
        self.host.mkdir()
        with self.assertRaises(cap.CapacityReadinessError):
            self.probe()

    def test_08_wrong_sibling_name_and_noncanonical_parent_fail(self):
        with self.assertRaises(cap.CapacityReadinessError):
            self.probe(host_root=self.parent / "wrong-host")
        alias = self.root / "parent-alias"
        alias.symlink_to(self.parent, target_is_directory=True)
        with self.assertRaises(cap.CapacityReadinessError):
            self.probe(parent=alias)
        self.assertFalse(self.run.exists())

    def test_09_actual_foreign_python_single_probe_no_writes(self):
        script = Path(cap.__file__).resolve(strict=True)
        argv = [sys.executable, "-B", str(script),
                "--output-parent", str(self.parent),
                "--run-root", str(self.run),
                "--host-raw-root", str(self.host),
                "--workspace", str(self.workspace),
                "--original-s", str(self.original),
                "--unity", str(self.unity)]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1")
        env.pop("PYTHONPATH", None)
        proc = subprocess.run(argv, cwd=self.root, env=env, text=True,
                              capture_output=True, timeout=40)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = json.loads(proc.stdout)
        self.assertEqual(report["kind"],
                         "R03InitializerOneUse05ReadOnlyCapacitySampleV1")
        self.assertFalse(report["eligibleForUnityRun"])
        self.assertEqual(report["writesPerformed"], 0)
        self.assertFalse(self.run.exists())
        self.assertFalse(self.host.exists())

    def test_10_local_script_has_no_mutating_helpers(self):
        source = Path(cap.__file__).read_text(encoding="utf-8")
        for unsafe in (".unlink(", ".rmdir(", ".mkdir(", "shutil.rmtree(",
                       "os.remove(", "os.unlink(", "subprocess.run("):
            self.assertNotIn(unsafe, source)
        self.assertIn("statvfs", source)
        self.assertIn("followlinks=False", source)
        self.assertEqual(cap.MIN_GIB, 25)
        self.assertEqual(cap.HARD_GIB, 20)
        self.assertEqual(cap.ADVISORY_GIB, 40)

    def test_11_no_candidate_auto_discovery(self):
        report = self.probe()
        self.assertEqual(report["candidateCount"], 0)
        self.assertEqual(report["explicitCandidateInspectionOnly"], [])
        self.assertFalse(report["automaticCleanupEnabled"])

    def test_12_failing_25gib_does_not_suggest_lower_floor(self):
        with patch.object(cap.os, "statvfs", return_value=type("S", (), {
            "f_bavail": (25 * cap.GIB - 1) // 4096, "f_frsize": 4096})()):
            report = self.probe()
        self.assertEqual(report["result"], "CapacityBlocked")
        self.assertTrue(report["capacity"]["bytesBelowMinimum"] > 0)
        self.assertFalse(report["bothFreshRootsAbsent"] is False)
        self.assertFalse(report["eligibleForUnityRun"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
