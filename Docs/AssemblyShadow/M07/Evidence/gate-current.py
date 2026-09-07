#!/usr/bin/env python3
"""M07 Gate A: current clean evidence-commit replay."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

import gate_common as common


def main(project: Path, output_root: Path, evidence_commit: str) -> None:
    project = project.resolve(strict=True)
    common.require(project == common.LIVE, "Wrong live M07 project")
    common.require(output_root.is_absolute() and output_root.resolve() == output_root and not output_root.exists(), "New canonical output root required")
    common.require(output_root.is_relative_to(common.LIVE / "_temp/AssemblyShadow"), "Gate output must remain task-local")
    output_root.mkdir()
    evidence = project / "Docs/AssemblyShadow/M07/Evidence"
    git_tree = common.verify_git_tree(project, evidence_commit, False)
    source = common.verify_source_inventory(project, evidence_commit)
    index, retention = common.verify_retention(evidence)
    recorded = common.validate_recorded(evidence)
    python, strict = common.run_python_and_strict(project, output_root)
    installed = common.run_installed(project, output_root)
    common.require(not common.git(project, "status", "--short"), "Current checkout changed during Gate A")
    receipt = {
        "schemaVersion": 1,
        "milestone": "M07",
        "gate": "A-current-evidence-commit-tests-strict-install-and-retention",
        "result": "PASS",
        "reviewMode": "deterministic-current-clean-commit-process",
        "checkedUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "evidenceCommit": evidence_commit,
        "gitTree": git_tree,
        "sourceInventory": source,
        "artifactIndexPath": str(evidence / "artifact-index-v6.json"),
        "artifactIndexSha256": common.sha256(evidence / "artifact-index-v6.json"),
        "retention": retention,
        "recordedSuites": recorded,
        "python": python,
        "strictReplay": strict,
        "installedSourceVerification": installed,
        "status": [],
        "limitation": "Deterministic current-commit process gate, not an independent human or LLM review. Editor/native suites are immutable recorded receipts; Python, strict runtime verification and complete installed-source verification are rerun.",
    }
    path = output_root / "gate-a.json"
    common.write_json_new(path, receipt)
    print(json.dumps({"result": "PASS", "receipt": str(path), "sha256": common.sha256(path)}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--evidence-commit", required=True)
    args = parser.parse_args()
    main(args.project_root, args.output_root, args.evidence_commit)
