#!/usr/bin/env python3
"""Immutable b7e3 helper-identity regression; no real historical auditor execution.

The original 85-test source is the authority. Rejected mutations are synthetic.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
R03 = HERE.parents[1]
REPO = HERE.parents[6]
PRIOR = R03 / "IR_Remediation/P1_B7E3_AUDIT_ONLY_2026-10-23/audit_historical_only.py"
SUCCESSOR = HERE / "audit_historical_helper_successor.py"
CONSUMER = REPO / "Tools/AssemblyShadow/R03IR/test_p1_command_failures.py"
FINDING = R03 / "local-audit-only-p1-20261023-c42a/FINDING.json"
LOCAL = R03 / "local-audit-only-p1-20261023-c42a/LOCAL_RESULT.json"
RAW = R03 / "local-validation-p1-admitted-execution-20261023-b7e3/batch/command-failures/RESULT.json"
ORIGINAL_AUDITOR_BLOB = "c451e0cb7794e624eabb9029db0a35ba28d14592"
SUCCESSOR_AUDITOR_BLOB = "220aa2831458b37a81f66555f27d95349ec7013f"
CONSUMER_SHA256 = "637915585936544f2c001d936917959b1d53adf62a8e4f7d6b923ad316ed02de"
OLD = "verify_admitted_execution_receipt_and_fail_closed_mutations"
REAL = "verify_admitted_execution_receipt_and_negative_mutations"
CALLER = "test_all_eighteen_components_have_independent_success"
NAMES = (
    "missing-group", "duplicate-group", "wrong-kind", "bool-schema",
    "fake-typekey", "fake-runtime", "pretend-execution-v1-safe",
    "metadata-gate-not-compiled", "original-getter-changed", "epoch-not-original",
    "wrong-predecessor", "missing-sanitized", "profile-failure",
    "source-not-preserved", "wrapper-called-old-zero", "wrapper-activated-getter",
    "not-compiled",
)


def git_blob(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode() + b"\0" + data)
    return h.hexdigest()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_original_identity(source: str) -> tuple[ast.FunctionDef, ast.FunctionDef, ast.Call]:
    """Fail closed on duplicate/missing helper, missing call, or wrong caller."""
    tree = ast.parse(source)
    methods = [n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name == REAL]
    if len(methods) != 1:
        raise ValueError("Expected exactly one original admitted negative-mutations definition")
    callers = [n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name == CALLER]
    if len(callers) != 1:
        raise ValueError("Expected exactly one original existing-85 caller leaf")
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == REAL]
    if len(calls) != 1:
        raise ValueError("Expected exactly one original admitted negative-mutations invocation")
    within = [n for n in ast.walk(callers[0]) if n is calls[0]]
    if len(within) != 1:
        raise ValueError("Admitted helper must be invoked by the original success leaf")
    if not isinstance(calls[0].func.value, ast.Call):
        raise ValueError("Admitted helper invocation receiver unexpectedly changed")
    receiver = calls[0].func.value.func
    if not isinstance(receiver, ast.Name) or receiver.id != "OwnedBindingInventoryContract":
        raise ValueError("Original inventory-contract test owner changed")
    return methods[0], callers[0], calls[0]


def source_assertions(text: str) -> str:
    """Execute ONLY the two source-identity lines, not the full auditor."""
    lines = text.splitlines()
    assert len(lines) >= 1032
    code = lines[1030] + "\n" + lines[1031] + "\n"
    assert "consumer_node=next(" in code
    assert "assert '" + REAL + "()' in consumer_fixture" in code
    return code


class HistoricalAdmittedHelperIdentity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = PRIOR.read_bytes()
        cls.successor = SUCCESSOR.read_bytes()
        cls.consumer = CONSUMER.read_bytes()
        cls.finding = json.loads(FINDING.read_bytes())
        cls.local = json.loads(LOCAL.read_bytes())
        cls.raw = json.loads(RAW.read_bytes())
        cls.original_text = cls.original.decode("utf-8")
        cls.successor_text = cls.successor.decode("utf-8")
        cls.consumer_text = cls.consumer.decode("utf-8")

    def test_01_pinned_original_auditor_source_blob(self):
        self.assertEqual(git_blob(self.original), ORIGINAL_AUDITOR_BLOB)
        self.assertEqual(self.original_text.count(OLD), 2)
        self.assertNotIn(REAL, self.original_text)

    def test_02_successor_pinned_blob_and_exact_two_name_edits(self):
        self.assertEqual(git_blob(self.successor), SUCCESSOR_AUDITOR_BLOB)
        self.assertEqual(self.successor, self.original.replace(OLD.encode(), REAL.encode()))
        changed = [(i + 1, a, b) for i, (a, b) in
                   enumerate(zip(self.original_text.splitlines(),
                                 self.successor_text.splitlines())) if a != b]
        self.assertEqual([line for line, _, _ in changed], [1031, 1032])
        self.assertEqual(self.successor_text.count(REAL), 2)
        self.assertNotIn(OLD, self.successor_text)

    def test_03_full_corrected_auditor_has_valid_python_ast(self):
        ast.parse(self.successor_text)
        compile(self.successor_text, str(SUCCESSOR), "exec")
        self.assertEqual(len(self.successor_text.splitlines()),
                         len(self.original_text.splitlines()))

    def test_04_original_b7e3_consumer_sha_and_source_identity(self):
        self.assertEqual(sha(self.consumer), CONSUMER_SHA256)
        self.assertEqual(self.finding["actualHelperSourceSha256"], CONSUMER_SHA256)
        self.assertTrue(self.finding["actualHelperByteIdenticalToHistoricalB7E3Source"])
        self.assertEqual(self.consumer_text.count(REAL), 2)
        self.assertNotIn(OLD, self.consumer_text)

    def test_05_real_helper_definition_exactly_once(self):
        method, caller, call = verify_original_identity(self.consumer_text)
        self.assertEqual(method.name, REAL)
        self.assertEqual(method.lineno, 504)
        self.assertTrue(ast.get_source_segment(self.consumer_text, method).startswith("def " + REAL))

    def test_06_caller_in_original_85_and_exact_one_call(self):
        method, caller, call = verify_original_identity(self.consumer_text)
        self.assertEqual(caller.name, CALLER)
        self.assertIn("p1_contract_suite_2.BatchFailureScheduling." + CALLER,
                      self.raw["testIds"])
        self.assertEqual(self.raw["testsRun"], 85)
        self.assertEqual(len(self.raw["testIds"]), len(set(self.raw["testIds"])))
        self.assertEqual(ast.get_source_segment(self.consumer_text, call),
                         "OwnedBindingInventoryContract()." + REAL + "()")

    def test_07_original_negative_mutation_case_inventory_unchanged(self):
        method, _, _ = verify_original_identity(self.consumer_text)
        literals = [n for n in ast.walk(method)
                    if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "cases"
                                                         for t in n.targets)]
        self.assertEqual(len(literals), 1)
        self.assertEqual(tuple(ast.literal_eval(literals[0].value)), NAMES)
        self.assertIn("assertRaisesRegex", ast.get_source_segment(self.consumer_text, method))

    def test_08_two_actual_source_assertions_execute_without_running_auditor(self):
        scope = {"ast": ast, "consumer_fixture": self.consumer_text}
        exec(compile(source_assertions(self.successor_text),
                     "<source-identity-only>", "exec"), scope)
        self.assertEqual(scope["consumer_node"].name, REAL)
        self.assertIn("bad[", scope["cs"])
        self.assertIn("assertRaisesRegex", scope["cs"])

    def test_09_wrong_legacy_name_fails_on_actual_consumer(self):
        # Run original bad lines without passing through the corrected-name helper.
        old_lines = self.original_text.splitlines()
        with self.assertRaises(StopIteration):
            exec(compile(old_lines[1030] + "\n" + old_lines[1031] + "\n",
                         "<old-source-identity-only>", "exec"),
                 {"ast": ast, "consumer_fixture": self.consumer_text})

    def test_10_missing_definition_rejected(self):
        source = self.consumer_text.replace("def " + REAL, "def missing_" + REAL, 1)
        with self.assertRaises(ValueError):
            verify_original_identity(source)

    def test_11_duplicate_definition_rejected(self):
        source = self.consumer_text + "\ndef " + REAL + "(self):\n    pass\n"
        with self.assertRaises(ValueError):
            verify_original_identity(source)

    def test_12_missing_call_rejected(self):
        source = self.consumer_text.replace("OwnedBindingInventoryContract()." + REAL + "()",
                                            "OwnedBindingInventoryContract().missing()")
        with self.assertRaises(ValueError):
            verify_original_identity(source)

    def test_13_duplicate_call_rejected(self):
        pattern = "        OwnedBindingInventoryContract()." + REAL + "()"
        self.assertIn(pattern, self.consumer_text)
        with self.assertRaises(ValueError):
            verify_original_identity(self.consumer_text.replace(pattern, pattern + "\n" + pattern))

    def test_14_wrong_call_receiver_rejected(self):
        source = self.consumer_text.replace("OwnedBindingInventoryContract()." + REAL + "()",
                                            "OtherInventoryContract()." + REAL + "()")
        with self.assertRaises(ValueError):
            verify_original_identity(source)

    def test_15_wrong_caller_rejected(self):
        source = self.consumer_text.replace("    def " + CALLER + "(self):",
                                            "    def renamed_" + CALLER + "(self):")
        with self.assertRaises(ValueError):
            verify_original_identity(source)

    def test_16_evidence_original_c42a_fail_preserved(self):
        self.assertEqual(self.finding["id"], "IR-LOCAL-P1-HISTORICAL-AUDIT-HELPER-01")
        self.assertEqual(self.finding["expectedHelper"], OLD)
        self.assertEqual(self.finding["actualHelper"], REAL)
        self.assertEqual(self.finding["firstFailureLine"], 1031)
        self.assertEqual(self.local["result"], "FAIL")
        self.assertEqual(self.local["scopedAuditResult"], "FailedOrIncomplete")
        self.assertEqual(self.local["auditReport"], "Unavailable_NotProduced")
        self.assertFalse(self.local["coreAndSdkCompilerRerun"])

    def test_17_remaining_auditor_preserved_including_exact25_and_historical_git(self):
        assert self.successor_text.splitlines()[:1030] == self.original_text.splitlines()[:1030]
        assert self.successor_text.splitlines()[1032:] == self.original_text.splitlines()[1032:]
        self.assertIn("assert r['kind']=='R03P1FailureAwareSourceSDKPreflight'", self.successor_text)
        self.assertIn("GIT_HISTORICAL_AUTHORITY_AFTER.json", self.successor_text)
        self.assertIn("liveRemoteHeadCheck='NotRun_TimeVariant'", self.successor_text)
        self.assertIn("originalB7E3LocalResult='FAIL'", self.successor_text)
        self.assertIn("consumerMutationHelperSha256=hashlib.sha256(cs.encode()).hexdigest()",
                      self.successor_text)


if __name__ == "__main__":
    unittest.main()
