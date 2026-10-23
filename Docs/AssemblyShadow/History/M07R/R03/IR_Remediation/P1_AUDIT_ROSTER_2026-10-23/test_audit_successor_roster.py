#!/usr/bin/env python3
"""Source-only 25-component auditor roster regressions; no SDK/Unity/core execution."""
from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parents[1] / "local-validation-p1-admitted-execution-20261023-b7e3"
SOURCE = ARCHIVE / "preflight/audit.py"
RESULT = ARCHIVE / "batch/RESULT.json"
FINDING = ARCHIVE / "FINDING.json"
SUCCESSOR = HERE / "audit_successor.py"
ORIGINAL_SHA256 = "2b43453f00fd74c1692d55d3c10b7351df45a0a82d08cf551deb0282862848a0"
RAW_SHA256 = "f762d292d9601e620a83ecd79cc5e3c5ab85b0ea0a3813fbf472bd716eb1c7e6"
INSERT_BEFORE = "'vm-shape-json','bounded-status'"
INSERT_AFTER = "'vm-shape-json','admitted-execution','bounded-status'"
ROSTER = (
    "command-failures", "legacy-host", "metadata-gate", "bounded-class",
    "bounded-physical", "bounded-first-use", "owned-general", "live-general",
    "owned-execution", "empty-live", "opaque-inventory", "physical-membership",
    "owned-physical-names", "owned-physical-json", "live-owned-physical-json",
    "observed-type-shape", "live-type-shape-census", "observed-type-shape-json",
    "vm-shape-json", "admitted-execution", "bounded-status", "bounded-inventory",
    "frozen-v2", "managed-sdk", "native-sdk",
)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def exact_successor(original: bytes, original_line: str) -> bytes:
    """Produce precisely the reviewed one-line change from immutable bytes."""
    if sha256(original) != ORIGINAL_SHA256:
        raise ValueError("Original archived independent auditor bytes changed")
    text = original.decode("utf-8")
    if original_line.count(INSERT_BEFORE) != 1 or text.count(original_line) != 1:
        raise ValueError("Original auditor 24-roster anchor is missing or duplicated")
    if INSERT_AFTER in original_line:
        raise ValueError("Already-corrected roster is not a valid original")
    corrected = original_line.replace(INSERT_BEFORE, INSERT_AFTER)
    generated = text.replace(original_line, corrected)
    ast.parse(generated, filename="source-bound-25-auditor.py")
    if len(generated) != len(text) + len(INSERT_AFTER) - len(INSERT_BEFORE):
        raise ValueError("Unexpected source delta")
    return generated.encode("utf-8")


class AuditRosterSuccessorContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = SOURCE.read_bytes()
        cls.successor = SUCCESSOR.read_bytes()
        cls.raw_bytes = RESULT.read_bytes()
        cls.finding = json.loads(FINDING.read_bytes())
        cls.raw = json.loads(cls.raw_bytes)
        cls.old_line = cls.finding["sourceExpression"]
        cls.new_line = cls.old_line.replace(INSERT_BEFORE, INSERT_AFTER)
        cls.old_ast = ast.parse(cls.original, filename=str(SOURCE))
        cls.new_ast = ast.parse(cls.successor, filename=str(SUCCESSOR))
        cls.roster_assert = next(
            node for node in cls.new_ast.body
            if isinstance(node, ast.Assert) and node.lineno == 190
        )
        cls.execution_contract = compile(
            cls.successor.decode("utf-8").splitlines()[188] + "\n" +
            cls.successor.decode("utf-8").splitlines()[189] + "\n",
            "bounded-component-contract-only", "exec")

    def assert_roster_contract(self, raw):
        exec(self.execution_contract, {"r": raw})

    def test_01_original_source_sha_and_failure_identity_are_pinned(self):
        self.assertEqual(sha256(self.original), ORIGINAL_SHA256)
        self.assertEqual(self.finding["id"], "IR-LOCAL-P1-ADMITTED-AUDIT-ROSTER-01")
        self.assertEqual(self.finding["expectedCount"], 24)
        self.assertEqual(self.finding["actualCount"], 25)
        self.assertEqual(self.original.decode().splitlines()[189], self.old_line)

    def test_02_successor_is_exactly_one_source_line(self):
        self.assertEqual(self.successor, exact_successor(self.original, self.old_line))
        changed = [(i + 1, a, b) for i, (a, b) in enumerate(
            zip(self.original.decode().splitlines(),
                self.successor.decode().splitlines())) if a != b]
        self.assertEqual(changed, [(190, self.old_line, self.new_line)])
        self.assertEqual(len(self.successor), len(self.original) + 21)

    def test_03_syntax_and_25_component_guard_preserved(self):
        self.assertEqual(len(self.old_ast.body), len(self.new_ast.body))
        self.assertEqual(self.new_ast.body[0].lineno, self.old_ast.body[0].lineno)
        self.assertEqual(self.successor.decode().splitlines()[188],
                         self.original.decode().splitlines()[188])
        self.assertIn("r['componentCount']==r['attemptedComponentCount']==25",
                      self.successor.decode().splitlines()[188])
        self.assertEqual(self.new_line, self.successor.decode().splitlines()[189])

    def test_04_exact_roster_is_literal_25_ordered_names(self):
        names = ast.literal_eval(self.roster_assert.test.comparators[0])
        self.assertEqual(tuple(names), ROSTER)
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(ROSTER.index("admitted-execution"), 19)
        self.assertEqual(ROSTER[18:21],
                         ("vm-shape-json", "admitted-execution", "bounded-status"))

    def test_05_immutable_raw_record_has_original_success_without_promotion(self):
        self.assertEqual(sha256(self.raw_bytes), RAW_SHA256)
        self.assertEqual(self.raw["result"], "PassedSourceHostAndSDKOnly")
        self.assertEqual(self.raw["componentCount"], 25)
        self.assertEqual(self.raw["attemptedComponentCount"], 25)
        self.assertTrue(self.raw["sourcePreserved"])
        self.assertFalse(self.raw["commandLifetimeUnverified"])
        self.assertEqual([c["status"] for c in self.raw["commands"]], ["Passed"] * 25)

    def test_06_published_raw_names_match_local_finding_and_roster(self):
        names = [c["name"] for c in self.raw["commands"]]
        self.assertEqual(names, list(ROSTER))
        self.assertEqual(names, self.finding["actualNames"])
        self.assertEqual(
            self.finding["expectedNames"],
            [name for name in ROSTER if name != "admitted-execution"])

    def test_07_actual_raw_passes_exact_original_count_and_corrected_roster(self):
        self.assert_roster_contract(self.raw)

    def test_08_archived_24_roster_is_rejected(self):
        changed = copy.deepcopy(self.raw)
        changed["commands"] = [c for c in changed["commands"]
                               if c["name"] != "admitted-execution"]
        changed["componentCount"] = changed["attemptedComponentCount"] = 24
        with self.assertRaises(AssertionError):
            self.assert_roster_contract(changed)

    def test_09_absent_admitted_with_still_25_counter_rejected(self):
        changed = copy.deepcopy(self.raw)
        changed["commands"] = [c for c in changed["commands"]
                               if c["name"] != "admitted-execution"]
        with self.assertRaises(AssertionError):
            self.assert_roster_contract(changed)

    def test_10_extra_component_rejected(self):
        changed = copy.deepcopy(self.raw)
        changed["commands"].append(dict(changed["commands"][-1], name="unexpected"))
        with self.assertRaises(AssertionError):
            self.assert_roster_contract(changed)

    def test_11_duplicate_admitted_component_rejected(self):
        changed = copy.deepcopy(self.raw)
        changed["commands"][20] = dict(changed["commands"][19])
        with self.assertRaises(AssertionError):
            self.assert_roster_contract(changed)

    def test_12_wrong_slot_rejected(self):
        changed = copy.deepcopy(self.raw)
        item = changed["commands"].pop(19)
        changed["commands"].append(item)
        with self.assertRaises(AssertionError):
            self.assert_roster_contract(changed)

    def test_13_neighbor_swap_rejected(self):
        changed = copy.deepcopy(self.raw)
        changed["commands"][18], changed["commands"][19] = (
            changed["commands"][19], changed["commands"][18])
        with self.assertRaises(AssertionError):
            self.assert_roster_contract(changed)

    def test_14_count_mismatch_rejected(self):
        changed = copy.deepcopy(self.raw)
        changed["componentCount"] = 24
        with self.assertRaises(AssertionError):
            self.assert_roster_contract(changed)

    def test_15_mutated_source_or_duplicate_anchor_refused(self):
        with self.assertRaises(ValueError):
            exact_successor(self.original + b"# changed\n", self.old_line)
        with self.assertRaises(ValueError):
            exact_successor(self.original, self.old_line.replace(
                INSERT_BEFORE, INSERT_AFTER))
        with self.assertRaises(ValueError):
            exact_successor(self.original, "a missing roster line")

    def test_16_remaining_auditor_source_contracts_not_removed(self):
        src = self.successor.decode()
        for mandatory in (
            "ADMITTED_EXECUTION_VERIFICATION.json",
            "GIT_POSTFLIGHT_VERIFICATION.json",
            "CHECKPOINTS_AFTER.json",
            "SDK_AFTER.json",
            "MANIFEST.json",
            "PassedFactualEvidenceAudit",
            "admittedExecutionMetadataCaseInventoryVerified",
        ):
            self.assertIn(mandatory, src)
        # These later gates have NOT been executed by this host-only test.
        self.assertEqual(self.original.splitlines()[190:],
                         self.successor.splitlines()[190:])


if __name__ == "__main__":
    unittest.main()
