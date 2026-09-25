#!/usr/bin/env python3
"""Independent retention audit for the source-038 count matrix."""

import argparse
import hashlib
import json
import uuid
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path, expected_hash=None):
    path = Path(path)
    require(path.is_absolute() and path.is_file() and not path.is_symlink()
            and path == path.resolve(), "missing or noncanonical file: " + str(path))
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if expected_hash is not None:
        require(actual == expected_hash, "SHA-256 differs: " + str(path))
    return json.loads(raw), actual


def inside(path, root):
    require(path.is_relative_to(root), "evidence escapes matrix root: " + str(path))
    return path


def audit(index_path, selected_path):
    index, index_hash = read(index_path)
    selected, selected_hash = read(selected_path)
    root = index_path.parent
    require(index.get("kind") == "H1CountResultIndex", "wrong result-index kind")
    require(selected.get("status") == "Passed", "candidate selection not passed")
    cells = index.get("cells")
    require(isinstance(cells, list) and len(cells) == 132, "matrix does not have 132 cells")
    builds = selected["builds"]
    require(set(builds) == {"on-Debug", "on-Release", "off-Debug", "off-Release"},
            "candidate tuple set differs")
    seen_cells, seen_runs, seen_pids, seen_reports, seen_launches, seen_raws = (
        set(), set(), set(), set(), set(), set())
    rows = []
    outcome_counts = {}
    for ordinal, cell in enumerate(cells, 1):
        cell_id = cell["cellId"]
        require(cell_id not in seen_cells, "duplicate cell ID: " + cell_id)
        seen_cells.add(cell_id)
        report_ref = cell["report"]
        report_path = inside(Path(report_ref["path"]), root)
        require(report_path.name == "verification.json" and report_path not in seen_reports,
                "missing or reused verification path: " + cell_id)
        seen_reports.add(report_path)
        report, report_hash = read(report_path, report_ref["sha256"])
        require(report.get("kind") == "H1CountResultVerification" and
                report.get("result") == report.get("status") == "Passed", "cell did not pass: " + cell_id)
        launch_ref = report.get("inputs", {}).get("launchReceipt", {})
        launch_path = inside(Path(launch_ref.get("path", "")), root)
        require(launch_path.name == "h1-count-player-launch.json" and
                launch_path.parent == report_path.parent and launch_path not in seen_launches,
                "missing or reused launch path: " + cell_id)
        seen_launches.add(launch_path)
        launch, launch_hash = read(launch_path, launch_ref.get("sha256"))
        require(launch.get("kind") == "H1CountPlayerLaunchReceipt" and
                launch.get("passed") is True and launch.get("launchSucceeded") is True and
                launch.get("inputsUnchanged") is True and
                launch.get("inputHashesBefore") == launch.get("inputHashesAfter"),
                "launch failed or changed inputs: " + cell_id)
        run_id = str(uuid.UUID(launch["runId"]))
        pid = launch.get("processId")
        require(run_id not in seen_runs, "duplicate run ID: " + cell_id)
        require(isinstance(pid, int) and pid > 0 and pid not in seen_pids,
                "missing or reused process ID: " + cell_id)
        seen_runs.add(run_id)
        seen_pids.add(pid)
        requested = report["requested"]
        executed = report["executed"]
        require(requested["family"] == launch["family"] and
                requested["caseId"] == launch["caseId"] and
                requested["cppConfiguration"] == launch["cppConfiguration"] and
                requested["pathName"] == launch["path"].capitalize() +
                ("-ON" if launch["featureEnabled"] else "-OFF") and
                executed["processId"] == pid and executed["buildGuid"] == launch["buildGuid"],
                "cell identity differs across verifier/launch: " + cell_id)
        tuple_key = ("on" if launch["featureEnabled"] else "off") + "-" + launch["cppConfiguration"]
        build = builds[tuple_key]
        require(launch["buildGuid"] == build["buildGuid"] and
                launch["buildReceiptPath"] == build["receiptPath"] and
                launch["buildReceiptSha256"] == build["receiptSha256"],
                "unexpected build identity: " + cell_id)
        read(build["receiptPath"], build["receiptSha256"])
        rejected = launch.get("expectedStartupRejection") is True
        raw_key = "earlyResultPath" if rejected else "resultPath"
        hash_key = "earlyResultSha256" if rejected else "resultSha256"
        raw_path = inside(Path(launch[raw_key]), root)
        require(raw_path.parent == report_path.parent and raw_path not in seen_raws,
                "missing or reused semantic raw path: " + cell_id)
        seen_raws.add(raw_path)
        raw, raw_hash = read(raw_path, launch[hash_key])
        require(raw.get("kind") == ("H1CountEarlyStartupResult" if rejected else
                "H1CountDiagnosticResult") and raw.get("processId") == pid and
                raw.get("family") == launch["family"] and raw.get("caseId") == launch["caseId"] and
                raw.get("path") == launch["path"], "raw/launch semantics differ: " + cell_id)
        if "buildGuid" in raw:
            require(raw["buildGuid"] == launch["buildGuid"], "raw build GUID differs: " + cell_id)
        if rejected:
            require(raw.get("result") == "ExpectedValidationRejection" and
                    executed.get("earlyResultPath") == str(raw_path) and
                    not Path(launch["resultPath"]).exists(), "rejection raw differs: " + cell_id)
        else:
            require(raw.get("result") == "Passed" and
                    executed.get("resultPath") == str(raw_path), "diagnostic raw differs: " + cell_id)
        supporting_early = None
        if not rejected and launch.get("earlyResultSha256"):
            early_path = inside(Path(launch["earlyResultPath"]), root)
            early, early_hash = read(early_path, launch["earlyResultSha256"])
            require(early.get("processId") == pid and early.get("caseId") == launch["caseId"],
                    "supporting early result differs: " + cell_id)
            supporting_early = {"path": str(early_path), "sha256": early_hash}
        outcome = raw["result"]
        outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
        rows.append({"ordinal": ordinal, "cellId": cell_id, "runId": run_id,
                     "processId": pid, "buildTuple": tuple_key, "buildGuid": launch["buildGuid"],
                     "verification": {"path": str(report_path), "sha256": report_hash},
                     "launch": {"path": str(launch_path), "sha256": launch_hash},
                     "semanticRaw": {"path": str(raw_path), "sha256": raw_hash,
                                     "kind": raw["kind"], "result": outcome},
                     "supportingEarlyRaw": supporting_early,
                     "inputsUnchanged": True})
    all_reports = set(root.rglob("verification.json"))
    all_launches = set(root.rglob("h1-count-player-launch.json"))
    require(all_reports == seen_reports and all_launches == seen_launches,
            "matrix contains extra or unindexed verification/launch receipts")
    require(len(seen_cells) == len(seen_runs) == len(seen_pids) ==
            len(seen_reports) == len(seen_launches) == len(seen_raws) == 132,
            "retention cardinality differs")
    return {"kind": "H1FreshCountLaunchRawAudit", "status": "Passed", "allPassed": True,
            "resultIndexPath": str(index_path), "resultIndexSha256": index_hash,
            "selectedBuildsPath": str(selected_path), "selectedBuildsSha256": selected_hash,
            "cells": 132, "verifications": 132, "launches": 132,
            "semanticRawOutcomes": 132, "uniqueRunIds": 132,
            "uniqueProcessIds": 132, "missingLaunch": 0, "missingRaw": 0,
            "duplicateCellIds": 0, "unexpectedBuildGuids": 0,
            "outcomeCounts": outcome_counts, "rows": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-index", required=True, type=Path)
    parser.add_argument("--selected-builds", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = audit(args.result_index, args.selected_builds)
    with args.output.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({k: report[k] for k in ("status", "cells", "launches",
                                         "semanticRawOutcomes", "uniqueRunIds", "outcomeCounts")},
                     indent=2))


if __name__ == "__main__":
    main()
