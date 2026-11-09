#!/usr/bin/env python3
"""Fail-closed A2 CI-job admission from *fresh* exact-commit GitHub records.

The consumer verifies a source-bound snapshot supplied by Local Validation.
It does not retrieve GitHub data, correct a platform job status, run Unity,
grant a Local run, or modify a historical CI or Player record.

Expected input: the established preflight/CI.json-shaped JSON:
  {"runs": [GitHub workflow_run records], "jobs": {run_id: {"jobs": [...]}},
   "ancillary": [...]}
A job with status=in_progress and conclusion=success is BLOCKED even when
completed_at and all step records say completed/success.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

BRANCH = "codex/assembly-shadow-r01b-h1"
REQUIRED = (
    "r03-ir-captured-generic-owner-host.yml",
    "r03-ir-captured-generic-native-host.yml",
    "r03-ir-captured-generic-batch-host.yml",
    "r03-ir-captured-generic-real-headers.yml",
    "r03-ir-initializer-bridge-host.yml",
    "r03-ir-initializer-local-contracts.yml",
    "r03-ir-current-native-local-cycle-host.yml",
)
PREFIX = ".github/workflows/"
OS = ("macos-15", "ubuntu-24.04")
SHA = re.compile(r"[0-9a-f]{40}\Z")
MAX_BYTES = 2_000_000


class CIRecordRejected(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise CIRecordRejected(message)


def exact_integer(value):
    return type(value) is int and value > 0


def json_strict(raw):
    need(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES,
         "Bounded nonempty authentic CI input bytes required")

    def unique(items):
        result = {}
        for key, value in items:
            need(key not in result, "Duplicate CI source JSON key: " + key)
            result[key] = value
        return result

    return json.loads(raw.decode("utf-8", "strict"),
                      object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          CIRecordRejected("Nonfinite CI number")))


def validate(snapshot, expected_sha):
    """Pure schema/identity/status consumer. No network, no waiver, no writes."""
    need(type(expected_sha) is str and SHA.fullmatch(expected_sha) is not None,
         "Exact expected execution SHA required")
    need(type(snapshot) is dict and
         type(snapshot.get("runs")) is list and
         type(snapshot.get("jobs")) is dict,
         "GitHub run/job source receipt shape")
    runs = snapshot["runs"]
    records = snapshot["jobs"]
    need(len(runs) >= len(REQUIRED), "Seven real mandatory workflow runs required")
    selected = []
    ids = set()
    for name in REQUIRED:
        path = PREFIX + name
        found = [row for row in runs if type(row) is dict and
                 row.get("path") == path and row.get("head_sha") == expected_sha]
        need(len(found) == 1,
             "Exactly one fresh exact-source run required: " + name)
        run = found[0]
        rid = run.get("id")
        need(exact_integer(rid) and rid not in ids,
             "Unique integer workflow run identity: " + name)
        ids.add(rid)
        need(run.get("head_branch") == BRANCH and
             exact_integer(run.get("run_attempt")) and
             run.get("status") == "completed" and
             run.get("conclusion") == "success",
             "Workflow must be actual completed/success: " + name)
        need(run.get("event") in ("push", "workflow_dispatch"),
             "Only explicit source-bound GitHub workflow event admitted")
        holder = records.get(str(rid))
        need(type(holder) is dict and type(holder.get("jobs")) is list,
             "Actual job list missing for workflow: " + name)
        jobs = holder["jobs"]
        need(len(jobs) == 2, "Exactly two genuine OS jobs: " + name)
        job_ids = set()
        os_rows = {}
        for job in jobs:
            need(type(job) is dict and
                 exact_integer(job.get("id")) and
                 job["id"] not in job_ids and
                 job["id"] not in {jid for entry in selected for jid in entry["jobIds"]} and
                 job.get("run_id") == rid and
                 type(job.get("name")) is str,
                 "Genuine unique job identity / owning run: " + name)
            job_ids.add(job["id"])
            matched_os = [os for os in OS if job["name"].endswith(" / " + os) or
                          job["name"].endswith(" (" + os + ")")]
            need(len(matched_os) == 1, "Exact OS job name required: " + name)
            os_name = matched_os[0]
            need(os_name not in os_rows, "Duplicate OS in mandatory job pair")
            # Deliberately do not infer completed from conclusion, timestamps,
            # successful steps, successful parent workflow, or check-run status.
            need(job.get("status") == "completed",
                 "Job-level status is NOT completed: " + name + " / " +
                 os_name + " (status=" + str(job.get("status")) +
                 ", conclusion=" + str(job.get("conclusion")) + ")")
            need(job.get("conclusion") == "success",
                 "Job-level conclusion is NOT success: " + name + " / " + os_name)
            steps = job.get("steps")
            need(type(steps) is list and steps and
                 all(type(step) is dict and step.get("status") == "completed" and
                     step.get("conclusion") == "success" for step in steps),
                 "Every real job step must be completed/success: " + name)
            os_rows[os_name] = {"jobId": job["id"], "steps": len(steps)}
        need(set(os_rows) == set(OS), "Missing mandatory OS")
        selected.append({"workflow": name, "runId": rid,
                         "runAttempt": run["run_attempt"],
                         "jobIds": sorted(job_ids), "osJobs": os_rows})
    # Records for a previous execution SHA or another branch are never
    # authoritative merely because their work is equivalent.
    return {
        "kind": "R03A2ExactSourceJobAdmissionV1",
        "result": "PassedSevenWorkflowFourteenJobRecords_NoLocalAuthorization",
        "sourceCommit": expected_sha,
        "verifiedWorkflows": selected,
        "workflowCount": len(selected), "jobCount": len(OS)*len(selected),
        "oldInconsistentJobWaived": False,
        "unityOrPlayerExecuted": False,
        "localRunnerAuthorizedByThisRecord": False,
        "runtimeAcceptance": False, "R03Accepted": False,
        "H2Passed": False, "ReadyForHumanReviewGate": False,
    }


def verify_file(path: Path, expected_sha: str):
    need(path.is_absolute() and path.is_file() and not path.is_symlink() and
         path.resolve(strict=True) == path,
         "Absolute canonical regular CI snapshot required")
    return validate(json_strict(path.read_bytes()), expected_sha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ci-json", required=True, type=Path)
    parser.add_argument("--demo-commit", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(verify_file(args.ci_json, args.demo_commit), sort_keys=True))
        return 0
    except (CIRecordRejected, OSError, ValueError, UnicodeError) as error:
        print("R03_A2_CI_ADMISSION_BLOCKED: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
