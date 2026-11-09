#!/usr/bin/env python3
"""Oneuse-08 actual blocked snapshot + strict non-authorizing CI mutations.

Tests do not alter historical evidence, invoke GitHub/Unity/Player or grant
Local execution. A synthetic corrected status is NEVER a correction to GitHub.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from captured_ci_job_admission import (CIRecordRejected, REQUIRED, json_strict,
                                        validate, verify_file)

ROOT = Path(__file__).resolve().parents[3]
HIST = ROOT / ("Docs/AssemblyShadow/History/M07R/R03/"
               "local-validation-captured-generic-20261109-oneuse-08-prerequisite-blocked"
               "/preflight/CI.json")
CANDIDATE = "26843412eda7034cd91c0754bdcde16d5517d814"
ANOMALOUS = 128946622207


class ExactCIJobStatusContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not HIST.is_file():
            raise RuntimeError("Authenticated Git-published oneuse08 CI.json required")
        cls.original_bytes = HIST.read_bytes()
        cls.original = json_strict(cls.original_bytes)
        cls.anomaly = [
            job for slot in cls.original["jobs"].values()
            for job in slot["jobs"] if job.get("id") == ANOMALOUS]
        if len(cls.anomaly) != 1:
            raise RuntimeError("Exact original inconsistent job evidence missing")

    @classmethod
    def source_consistent_fixture(cls):
        # In-memory counterfactual ONLY: verifies that a fresh successful
        # completed job can be accepted, not that the historical job changed.
        source = copy.deepcopy(cls.original)
        job = [job for slot in source["jobs"].values()
               for job in slot["jobs"] if job.get("id") == ANOMALOUS][0]
        job["status"] = "completed"
        return source

    def assert_denied(self, modified, reason=None):
        with self.assertRaises(CIRecordRejected) as ctx:
            validate(modified, CANDIDATE)
        if reason:
            self.assertIn(reason, str(ctx.exception))

    def test_01_real_immutable_oneuse08_is_blocked_by_job_status(self):
        original = self.anomaly[0]
        self.assertEqual(original["status"], "in_progress")
        self.assertEqual(original["conclusion"], "success")
        self.assertEqual(original["run_id"], 42551093381)
        self.assertTrue(original["steps"])
        self.assertTrue(all(x["status"] == "completed" and
                            x["conclusion"] == "success" for x in original["steps"]))
        self.assert_denied(self.original, "Job-level status is NOT completed")
        with self.assertRaisesRegex(CIRecordRejected, "Job-level status is NOT completed"):
            verify_file(HIST, CANDIDATE)

    def test_02_only_synthetic_new_consistent_records_pass_parser(self):
        result = validate(self.source_consistent_fixture(), CANDIDATE)
        self.assertEqual(result["result"],
                         "PassedSevenWorkflowFourteenJobRecords_NoLocalAuthorization")
        self.assertEqual(result["workflowCount"], 7)
        self.assertEqual(result["jobCount"], 14)
        self.assertFalse(result["oldInconsistentJobWaived"])
        self.assertFalse(result["localRunnerAuthorizedByThisRecord"])
        self.assertFalse(result["ReadyForHumanReviewGate"])
        self.assertFalse(result["runtimeAcceptance"])

    def test_03_inprogress_success_with_timestamp_and_steps_cannot_pass(self):
        for status in ("in_progress", "queued", "pending", None, True):
            source = self.source_consistent_fixture()
            source["jobs"]["42551093381"]["jobs"][0]["status"] = status
            with self.subTest(status=status):
                self.assert_denied(source, "Job-level status is NOT completed")

    def test_04_no_weaker_parent_workflow_or_job_conclusion(self):
        source = self.source_consistent_fixture()
        for attr, bad in (("status", "in_progress"),
                          ("conclusion", "cancelled"),
                          ("run_attempt", 0),
                          ("head_sha", "0"*40),
                          ("head_branch", "main")):
            rows = copy.deepcopy(source)
            rows["runs"][0][attr] = bad
            with self.subTest(attr=attr):
                self.assert_denied(rows)

    def test_05_each_missing_workflow_job_pair_or_duplicate_blocked(self):
        source = self.source_consistent_fixture()
        self.assertEqual(len(REQUIRED), 7)
        # CI.json also records the optional source-only workflow. Removing
        # that optional run is valid; mutate each REQUIRED identity by name.
        for name in REQUIRED:
            rows = copy.deepcopy(source)
            path = ".github/workflows/" + name
            found = [run for run in rows["runs"] if run.get("path") == path]
            self.assertEqual(len(found), 1)
            erased = found[0]
            rows["runs"].remove(erased)
            rows["jobs"].pop(str(erased["id"]))
            with self.subTest(required=name):
                self.assert_denied(rows)
        rows = copy.deepcopy(source)
        rows["jobs"].pop("42551093381")
        self.assert_denied(rows, "Actual job list missing")
        rows = copy.deepcopy(source)
        jobs = rows["jobs"]["42551093381"]["jobs"]
        jobs.append(copy.deepcopy(jobs[0]))
        self.assert_denied(rows, "Exactly two")
        rows = copy.deepcopy(source)
        jobs = rows["jobs"]["42551093381"]["jobs"]
        jobs[1]["name"] = jobs[0]["name"]
        self.assert_denied(rows, "Duplicate OS")

    def test_06_mismatched_job_owner_or_bad_step_refused(self):
        source = self.source_consistent_fixture()
        for key, bad in (("id", True), ("run_id", 9),
                         ("conclusion", "success-but-not-real"),
                         ("name", "unknown")):
            rows = copy.deepcopy(source)
            rows["jobs"]["42551093381"]["jobs"][0][key] = bad
            with self.subTest(key=key):
                self.assert_denied(rows)
        for key, bad in (("status", "skipped"), ("conclusion", "failure")):
            rows = copy.deepcopy(source)
            rows["jobs"]["42551093381"]["jobs"][0]["steps"][0][key] = bad
            with self.subTest(step=key):
                self.assert_denied(rows, "Every real job step")

    def test_07_bad_casing_and_bool_integer_conversions_denied(self):
        source = self.source_consistent_fixture()
        rows = copy.deepcopy(source)
        rows["runs"][0]["id"] = True
        self.assert_denied(rows)
        rows = copy.deepcopy(source)
        rows["runs"][0]["status"] = "Completed"
        self.assert_denied(rows)
        rows = copy.deepcopy(source)
        rows["jobs"]["42551093381"]["jobs"][0]["conclusion"] = True
        self.assert_denied(rows)

    def test_08_wrong_expected_commit_and_malformed_document(self):
        with self.assertRaises(CIRecordRejected):
            validate(self.source_consistent_fixture(), "0"*40)
        with self.assertRaises(CIRecordRejected):
            validate(self.source_consistent_fixture(), "not-a-commit")
        with self.assertRaises(CIRecordRejected):
            json_strict(b'{"runs":[], "runs":[], "jobs":{}}')
        with self.assertRaises(CIRecordRejected):
            json_strict(b'{"value":NaN}')
        with self.assertRaises(CIRecordRejected):
            json_strict(b"")
        with self.assertRaises(CIRecordRejected):
            json_strict(b"x" * 2_000_001)

    def test_09_source_evidence_is_not_mutated(self):
        original = HIST.stat().st_mtime_ns, HIST.read_bytes()
        self.assert_denied(self.original)
        self.assertEqual((HIST.stat().st_mtime_ns, HIST.read_bytes()), original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
