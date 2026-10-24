#!/usr/bin/env python3
"""Source-only/fully synthetic custody and one-shot tests; no Local audit or SDK."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
R03 = HERE.parents[1]
OLD_DIR = R03 / "IR_Remediation/P1_B7E3_AUDIT_ONLY_2026-10-23"
C42A = R03 / "local-audit-only-p1-20261023-c42a"
STAGER = HERE / "stage_helper_successor.py"
RUNNER = HERE / "run_helper_audit_once.py"
NEW_AUDIT = HERE / "audit_historical_helper_successor.py"
OLD_STAGER = OLD_DIR / "stage_local_audit_only.py"
OLD_RUNNER = OLD_DIR / "run_local_audit_once.py"
AUDIT_BLOB = "220aa2831458b37a81f66555f27d95349ec7013f"
C42A_MANIFEST_BLOB = "091d57e6234331ee1f5a8e1e3d5f1d9d229cf60b"


def loader(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class HelperStageAuditOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = loader(STAGER, "successor_helper_stager")
        cls.runner = loader(RUNNER, "successor_helper_one_shot")
        cls.new_source = NEW_AUDIT.read_bytes()

    def create_c42a_fixture(self, tempdir: Path):
        workspace = tempdir / "work"
        checkpoint = workspace / "hybridclr_demo/checkpoint"
        checkpoint.mkdir(parents=True)
        stage = tempdir / "consumed-original-c42a-stage"
        stage.mkdir()
        evidence = {
            "LOCAL_RESULT.json": {
                "result": "FAIL", "firstFinding": "IR-LOCAL-P1-HISTORICAL-AUDIT-HELPER-01"},
            "FINDING.json": {
                "id": "IR-LOCAL-P1-HISTORICAL-AUDIT-HELPER-01",
                "firstFailureLine": 1031},
            "stage/AUDIT_ONLY_RUN_RECEIPT.json": {
                "result": "FailedOrIncomplete", "exit": 1,
                "sourceGitBlob": "c451e0cb7794e624eabb9029db0a35ba28d14592",
                "originalB7E3LocalResult": "FAIL"},
            "stage/AUDIT_ONLY_AFTER.json": {
                "result": "Preserved", "preflightCount": 104,
                "rawFiles": 4269, "sdkFiles": 2405, "sdkScratchFiles": 1925},
            "stage/audit.py": "immutable old audit source\n",
        }
        for i in range(192):
            evidence[f"extra/evidence-{i:03d}.txt"] = f"immutable-{i}\n"
        self.assertEqual(len(evidence), 197)
        rows = []
        for name, value in sorted(evidence.items()):
            raw = ((json.dumps(value, indent=2) + "\n").encode()
                   if isinstance(value, dict) else value.encode())
            p = checkpoint / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
            rows.append(f"{sha(raw)}  {name}")
            if name.startswith("stage/") and name.split("/")[-1] in (
                    "audit.py", "AUDIT_ONLY_RUN_RECEIPT.json", "AUDIT_ONLY_AFTER.json"):
                (stage / Path(name).name).write_bytes(raw)
        manifest = ("\n".join(rows) + "\n").encode()
        (checkpoint / "MANIFEST.sha256").write_bytes(manifest)
        return workspace, stage, checkpoint, self.stage.blob_id(manifest)

    def test_01_successor_source_blob_and_exact_runner_pin(self):
        self.assertEqual(self.stage.blob_id(self.new_source), AUDIT_BLOB)
        old = OLD_RUNNER.read_text()
        new = RUNNER.read_text()
        self.assertEqual(new, old.replace(
            'SOURCE_BLOB = "c451e0cb7794e624eabb9029db0a35ba28d14592"',
            f'SOURCE_BLOB = "{AUDIT_BLOB}"'))
        self.assertIn('with marker.open("x"', new)
        self.assertIn('"originalB7E3LocalResult": "FAIL"', new)

    def test_02_stager_preserves_all_prior_input_guards(self):
        old = OLD_STAGER.read_text()
        new = STAGER.read_text()
        for phrase in (
            "def raw_manifest_hashes(", "def sdk_source_hashes(",
            "def sdk_scratch_hashes(", "def original_source_bindings(",
            "def consumed_input_hashes(", "def require_absent(",
            "def path_beneath(", 'result": "Preserved"',
        ):
            self.assertIn(phrase, old)
            self.assertIn(phrase, new)
        self.assertIn("c42a_immutable_history(workspace)", new)
        self.assertIn('HISTORICAL_AUDITOR_BLOB = "' + AUDIT_BLOB + '"', new)
        self.assertIn('source = HERE / "audit_historical_helper_successor.py"', new)
        self.assertNotIn('source = HERE / "audit_historical_only.py"', new)
        ast.parse(new)

    def test_03_real_published_c42a_checkpoint_manifest_all_files(self):
        manifest = C42A / "MANIFEST.sha256"
        self.assertEqual(self.stage.blob_id(manifest.read_bytes()), C42A_MANIFEST_BLOB)
        entries = {}
        for line in manifest.read_text().splitlines():
            expected, sep, rel = line.partition("  ")
            self.assertEqual(sep, "  ")
            self.assertNotIn(rel, entries)
            path = self.stage.path_beneath(C42A, rel)
            self.assertTrue(path.is_file())
            self.assertEqual(self.stage.digest(path), expected)
            entries[rel] = expected
        self.assertEqual(len(entries), 197)
        self.assertEqual(json.loads((C42A/"LOCAL_RESULT.json").read_text())["result"], "FAIL")

    def test_04_original_c42a_auditor_rejected_old_helper(self):
        finding = json.loads((C42A / "FINDING.json").read_text())
        self.assertEqual(finding["expectedHelper"], "verify_admitted_execution_receipt_and_fail_closed_mutations")
        self.assertEqual(finding["actualHelper"], "verify_admitted_execution_receipt_and_negative_mutations")
        self.assertEqual(finding["firstFailureLine"], 1031)
        local = json.loads((C42A / "LOCAL_RESULT.json").read_text())
        self.assertEqual(local["auditReport"], "Unavailable_NotProduced")
        self.assertEqual(local["result"], "FAIL")
        self.assertFalse(local["coreAndSdkCompilerRerun"])

    def test_05_synthetic_c42a_custody_passes_and_retains_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace, original, checkpoint, blob = self.create_c42a_fixture(Path(directory).resolve())
            with patch.object(self.stage, "C42A_CHECKPOINT", "checkpoint"), \
                 patch.object(self.stage, "C42A_MANIFEST_BLOB", blob), \
                 patch.object(self.stage, "C42A_ORIGINAL_STAGE", original):
                report = self.stage.c42a_immutable_history(workspace)
                self.assertEqual(report["publishedFilesVerified"], 197)
                self.assertEqual(report["originalLocalResult"], "FAIL")
                self.assertEqual(report["originalExternalStageFileBindings"], 3)

    def test_06_synthetic_c42a_checkpoint_tamper_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace, original, checkpoint, blob = self.create_c42a_fixture(Path(directory).resolve())
            (checkpoint / "extra/evidence-001.txt").write_text("malicious changed text")
            with patch.object(self.stage, "C42A_CHECKPOINT", "checkpoint"), \
                 patch.object(self.stage, "C42A_MANIFEST_BLOB", blob), \
                 patch.object(self.stage, "C42A_ORIGINAL_STAGE", original):
                with self.assertRaises(ValueError):
                    self.stage.c42a_immutable_history(workspace)

    def test_07_synthetic_c42a_original_audit_tamper_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace, original, checkpoint, blob = self.create_c42a_fixture(Path(directory).resolve())
            (original / "audit.py").write_text("changed original consumed audit")
            with patch.object(self.stage, "C42A_CHECKPOINT", "checkpoint"), \
                 patch.object(self.stage, "C42A_MANIFEST_BLOB", blob), \
                 patch.object(self.stage, "C42A_ORIGINAL_STAGE", original):
                with self.assertRaises(ValueError):
                    self.stage.c42a_immutable_history(workspace)

    def test_08_synthetic_c42a_forged_success_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace, original, checkpoint, blob = self.create_c42a_fixture(Path(directory).resolve())
            p = checkpoint / "LOCAL_RESULT.json"
            p.write_text(json.dumps({"result":"PASS",
                                     "firstFinding":"IR-LOCAL-P1-HISTORICAL-AUDIT-HELPER-01"}))
            with patch.object(self.stage, "C42A_CHECKPOINT", "checkpoint"), \
                 patch.object(self.stage, "C42A_MANIFEST_BLOB", blob), \
                 patch.object(self.stage, "C42A_ORIGINAL_STAGE", original):
                with self.assertRaises(ValueError):
                    self.stage.c42a_immutable_history(workspace)

    def test_09_wrong_c42a_root_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            stage = Path(directory).resolve()
            with self.assertRaises(ValueError):
                self.stage.require_absent(stage)
            with self.assertRaises(ValueError):
                self.stage.require_absent(stage / "../same")
            self.stage.require_absent(stage / "unused")

    def test_10_corrected_auditor_changes_no_component_or_git_pins(self):
        source = self.new_source.decode()
        self.assertIn("r['componentCount']==r['attemptedComponentCount']==25", source)
        self.assertIn("GIT_HISTORICAL_AUTHORITY_AFTER.json", source)
        self.assertIn("originalB7E3LocalResult='FAIL'", source)
        self.assertIn("liveRemoteHeadCheck='NotRun_TimeVariant'", source)
        self.assertNotIn("verify_admitted_execution_receipt_and_fail_closed_mutations", source)

    def test_11_no_original_source_milestone_acceptance(self):
        with tempfile.TemporaryDirectory() as directory:
            stage = Path(directory).resolve() / "successor-stage"
            stage.mkdir()
            (stage / "audit.py").write_bytes(self.new_source)
            self.assertEqual(self.runner.blob(stage/"audit.py"), AUDIT_BLOB)
            self.assertFalse((stage/"AUDIT_ONLY_INVOCATION.json").exists())


if __name__ == "__main__":
    unittest.main()
