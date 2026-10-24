#!/usr/bin/env python3
"""Host-only source-bound audit staging/provenance regressions. No Local commands."""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
R03 = HERE.parents[1]
CHECKPOINT = R03 / "local-validation-p1-admitted-execution-20261023-b7e3"
ORIGINAL = R03 / "IR_Remediation/P1_AUDIT_ROSTER_2026-10-23/audit_successor.py"
HISTORICAL = HERE / "audit_historical_only.py"
EXPECTED_SOURCE_BLOB = "c451e0cb7794e624eabb9029db0a35ba28d14592"


def import_stager():
    spec = importlib.util.spec_from_file_location(
        "b7e3_audit_stage_source_only", HERE / "stage_local_audit_only.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AuditOnlySourceContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stager = import_stager()
        cls.original = ORIGINAL.read_bytes()
        cls.historical = HISTORICAL.read_bytes()
        cls.original_tree = ast.parse(cls.original)
        cls.historical_tree = ast.parse(cls.historical)
        cls.initial = json.loads((CHECKPOINT / "preflight/EXPECTED.json").read_text())
        cls.before = json.loads((CHECKPOINT / "preflight/GIT_BEFORE.json").read_text())
        cls.raw = json.loads((CHECKPOINT / "batch/RESULT.json").read_text())
        cls.authority = next(n for n in cls.historical_tree.body
                             if isinstance(n, ast.FunctionDef) and n.name == "authority")
        namespace = {"E": cls.initial, "W": Path(cls.initial["workspace"]),
                     "P": CHECKPOINT / "preflight", "r": cls.raw,
                     "load": lambda path: json.loads(path.read_bytes()),
                     "dict": dict}
        exec(compile(ast.Module(body=[cls.authority], type_ignores=[]),
                     "<isolated-historical-authority-only>", "exec"), namespace)
        cls.authority_fn = staticmethod(namespace["authority"])

    def test_01_exact_full_historical_audit_source_blob(self):
        self.assertEqual(self.stager.blob_id(self.historical), EXPECTED_SOURCE_BLOB)

    def test_02_all_auditor_checks_preceding_final_authority_unchanged(self):
        token = b"def authority(n):\n"
        original_prefix = self.original.split(token, 1)[0]
        historical_prefix = self.historical.split(token, 1)[0]
        audit_only_comment = (
            b"# AUDIT-ONLY successor: historical provenance, never claim a live remote HEAD\n"
            b"# still equals a past execution SHA. The original twenty direct b7e3 Git\n"
            b"# receipts were already independently joined and checked above.\n"
        )
        self.assertEqual(historical_prefix, original_prefix + audit_only_comment)

    def test_03_only_historical_authority_and_explicit_scope_result_modified(self):
        old_tail = self.original.split(b"audit=dict(", 1)[1]
        new_tail = self.historical.split(b"audit=dict(", 1)[1]
        old_prefix = b"result='PassedFactualEvidenceAudit',"
        new_prefix = (b"result='PassedHistoricalEvidenceAuditOnly',"
                      b"auditMode='ReadOnlyIsolatedB7E3History',"
                      b"originalB7E3LocalResult='FAIL',"
                      b"liveRemoteHeadCheck='NotRun_TimeVariant',"
                      b"productAcceptance=False,")
        self.assertTrue(old_tail.startswith(old_prefix))
        self.assertTrue(new_tail.startswith(new_prefix))
        self.assertEqual(old_tail[len(old_prefix):], new_tail[len(new_prefix):])
        self.assertNotIn(b"PassedFactualEvidenceAudit", self.historical)

    def test_04_full_source_parses_and_output_labeled_nonacceptance(self):
        self.assertGreater(len(self.historical_tree.body), len(self.original_tree.body))
        self.assertIn(b"originalLocalAcceptancePromoted=False", self.historical)
        self.assertIn(b"liveRemoteRechecked=False", self.historical)

    def test_05_four_exact_event_time_head_receipts_pass(self):
        for repo, pin in self.stager.EXECUTION_PINS.items():
            with self.subTest(repo=repo):
                row = self.authority_fn(repo)
                self.assertEqual(row[0], repo)
                self.assertEqual(row[1]["pinnedHead"], pin)
                self.assertFalse(row[1]["liveRemoteRechecked"])
                self.assertEqual(row[1]["rawFinalDirectCommands"], 5)

    def test_06_mutated_historical_head_fails_closed(self):
        namespace = self.authority_fn.__globals__
        old = namespace["load"]
        def altered(path):
            value = copy.deepcopy(old(path))
            if Path(path).name == "GIT_BEFORE.json":
                value["hybridclr_demo"][2]["stdout"] = ("0" * 40 + "\n")
            return value
        namespace["load"] = altered
        try:
            with self.assertRaises(AssertionError):
                self.authority_fn("hybridclr_demo")
        finally:
            namespace["load"] = old

    def test_07_mutated_final_raw_authority_fails_closed(self):
        namespace = self.authority_fn.__globals__
        original_raw = namespace["r"]
        changed = copy.deepcopy(original_raw)
        changed["fourRepositoriesAfter"][0]["remoteHead"] = "0" * 40
        namespace["r"] = changed
        try:
            with self.assertRaises(AssertionError):
                self.authority_fn("hybridclr_demo")
        finally:
            namespace["r"] = original_raw

    def test_08_path_traversal_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp).resolve()
            for rel in ("../x", "/tmp/x", "a/../x", "a\\b"):
                with self.subTest(rel=rel):
                    with self.assertRaises(ValueError):
                        self.stager.path_beneath(p, rel)

    def test_09_real_stage_root_guard_keeps_alias_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp).resolve()
            self.stager.require_absent(parent / "absent")
            with self.assertRaises(ValueError):
                self.stager.require_absent(parent)
            physical = parent / "physical"
            physical.mkdir()
            alias = parent / "alias"
            alias.symlink_to(physical, target_is_directory=True)
            with self.assertRaises(ValueError):
                self.stager.require_absent(alias / "absent")

    def test_10_original_execution_pin_table_has_four_immutable_refs(self):
        self.assertEqual(self.stager.EXECUTION_PINS, self.initial["pins"])
        self.assertEqual(self.raw["componentCount"], 25)
        self.assertEqual(self.raw["result"], "PassedSourceHostAndSDKOnly")

    def test_11_stager_does_not_launch_an_auditor_or_compiler(self):
        code = (HERE / "stage_local_audit_only.py").read_text()
        parsed = ast.parse(code)
        imports = [n for n in ast.walk(parsed) if isinstance(n, ast.Import)]
        self.assertFalse(any(alias.name == "subprocess" for n in imports for alias in n.names))
        self.assertNotIn("Popen(", code)
        self.assertNotIn("os.system(", code)
        self.assertNotIn("subprocess.run(", code)

    def test_12_runner_is_one_shot_and_marks_local_failure_immutable(self):
        code = (HERE / "run_local_audit_once.py").read_text()
        ast.parse(code)
        self.assertIn('with marker.open("x"', code)
        self.assertIn("AUDIT_ONLY_RUN_RECEIPT.json", code)
        self.assertIn('originalB7E3LocalResult": "FAIL"', code)
        self.assertIn('"originalRawCoreRetried": False', code)
        self.assertIn("start_new_session=True", code)

    def test_13_original_required_auditor_still_failed(self):
        report = json.loads((CHECKPOINT / "LOCAL_RESULT.json").read_text())
        self.assertEqual(report["result"], "FAIL")
        self.assertEqual(report["firstFinding"], "IR-LOCAL-P1-ADMITTED-AUDIT-ROSTER-01")


    def make_encoded_preflight_fixture(self, parent):
        """Test the actual b7e3 lossless-run-once-log source-binding mode."""
        checkpoint = parent / "checkpoint"
        historical = parent / "original-preflight"
        historical.mkdir()
        checkpoint.mkdir()
        lines = []
        for i in range(70):
            name = f"item-{i:02d}.json"
            content = f"immutable-{i:02d}\n".encode()
            (historical / name).write_bytes(content)
            clone = checkpoint / "preflight" / name
            clone.parent.mkdir(exist_ok=True)
            clone.write_bytes(content)
            lines.append(f"{hashlib.sha256(content).hexdigest()}  preflight/{name}")
        raw = b"Original logged argv, stdout and warnings.\n"
        (historical / "run-once.log").write_bytes(raw)
        encoded = {
            "kind": "ExactUtf8TextEvidenceEncoding",
            "sourcePath": str(historical / "run-once.log"),
            "sourceSha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "encoding": "UTF-8",
            "text": raw.decode("utf-8"),
        }
        wrapped = (json.dumps(encoded, indent=2) + "\n").encode()
        wrapper = checkpoint / "preflight" / "run-once.log.utf8.json"
        wrapper.write_bytes(wrapped)
        lines.append(f"{hashlib.sha256(wrapped).hexdigest()}  preflight/run-once.log.utf8.json")
        bindings = {"encodedTextEvidence": [{
            "source": str(historical / "run-once.log"),
            "checkpoint": "preflight/run-once.log.utf8.json",
            "decodedBytes": len(raw), "decodedSha256": hashlib.sha256(raw).hexdigest()
        }]}
        (checkpoint / "COPY_BINDINGS.json").write_text(json.dumps(bindings))
        (checkpoint / "MANIFEST.sha256").write_text("\n".join(lines) + "\n")
        return checkpoint, historical, wrapper

    def test_14_source_bound_utf8_log_and_70_regular_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            checkpoint, historical, wrapper = self.make_encoded_preflight_fixture(Path(temp).resolve())
            verified = self.stager.consumed_input_hashes(checkpoint, historical)
            self.assertEqual(len(verified), 71)
            self.assertIn("run-once.log", verified)
            self.assertNotIn("run-once.log.utf8.json", verified)
            self.assertEqual(verified["run-once.log"],
                             hashlib.sha256((historical / "run-once.log").read_bytes()).hexdigest())

    def test_15_mutated_original_decoded_log_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            checkpoint, historical, wrapper = self.make_encoded_preflight_fixture(Path(temp).resolve())
            (historical / "run-once.log").write_text("different raw bytes")
            with self.assertRaises(ValueError):
                self.stager.consumed_input_hashes(checkpoint, historical)

    def test_16_mutated_published_utf8_wrapper_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            checkpoint, historical, wrapper = self.make_encoded_preflight_fixture(Path(temp).resolve())
            wrapper.write_text(wrapper.read_text() + " ")
            with self.assertRaises(ValueError):
                self.stager.consumed_input_hashes(checkpoint, historical)


    def sdk_scratch_fixture(self, base):
        raw = base / "raw"
        scratch = base / "scratch"
        (raw / "native-sdk").mkdir(parents=True)
        scratch.mkdir()
        paths = ("external/baselib/Include/Baselib.h",
                 "libil2cpp/vm/AssemblyShadow.cpp",
                 "libil2cpp/vm/AssemblyShadow.h")
        entries = []
        for i, path in enumerate(paths, 1):
            file = scratch / path
            file.parent.mkdir(parents=True, exist_ok=True)
            data = f"immutable scratch {i}\n".encode()
            file.write_bytes(data)
            entries.append({"path": path, "sha256": hashlib.sha256(data).hexdigest()})
        (raw / "native-sdk/native-sdk-inputs.json").write_text(
            json.dumps({"files": entries, "vendorFilesUploaded": False}))
        return raw, scratch

    def test_17_source_pinned_sdk_scratch_fixture_passes(self):
        with tempfile.TemporaryDirectory() as d:
            raw, scratch = self.sdk_scratch_fixture(Path(d).resolve())
            result = self.stager.sdk_scratch_hashes(raw, scratch, expected_count=3)
            self.assertEqual(result["checkedScratchFiles"], 3)
            self.assertFalse(result["sourceSdkOrCompilerReinvoked"])
            self.assertEqual(result["checkedSource"],
                             "b7e3/native-sdk/native-sdk-inputs.json")

    def test_18_changed_sdk_scratch_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            raw, scratch = self.sdk_scratch_fixture(Path(d).resolve())
            (scratch / "libil2cpp/vm/AssemblyShadow.h").write_text("tampered")
            with self.assertRaises(ValueError):
                self.stager.sdk_scratch_hashes(raw, scratch, expected_count=3)

    def test_19_duplicate_traversal_and_symlink_scratch_inputs_refused(self):
        with tempfile.TemporaryDirectory() as d:
            raw, scratch = self.sdk_scratch_fixture(Path(d).resolve())
            receipt = raw / "native-sdk/native-sdk-inputs.json"
            original = json.loads(receipt.read_text())
            duplicates = {"files": original["files"] + [original["files"][0]]}
            receipt.write_text(json.dumps(duplicates))
            with self.assertRaises(ValueError):
                self.stager.sdk_scratch_hashes(raw, scratch, expected_count=4)
            traversal = {"files": [*original["files"][:2],
                                   {**original["files"][2], "path": "../escape"}]}
            receipt.write_text(json.dumps(traversal))
            with self.assertRaises(ValueError):
                self.stager.sdk_scratch_hashes(raw, scratch, expected_count=3)
            receipt.write_text(json.dumps(original))
            real = scratch / "libil2cpp/vm/AssemblyShadow.cpp"
            real.unlink()
            real.symlink_to(scratch / "libil2cpp/vm/AssemblyShadow.h")
            with self.assertRaises(ValueError):
                self.stager.sdk_scratch_hashes(raw, scratch, expected_count=3)


if __name__ == "__main__":
    unittest.main()
