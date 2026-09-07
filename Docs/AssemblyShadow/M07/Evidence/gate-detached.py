#!/usr/bin/env python3
"""M07 Gate B: independent clean detached-commit replay."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
from pathlib import Path

import gate_common as common


HISTORICAL_INPUTS = (
    "Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes",
    "BaselineArtifacts/StandaloneOSX/M01-Baseline-v1",
    "HybridCLRData/AssemblyShadow/Baselines/StandaloneOSX/M02-Baseline-36ca3c767e2bc9c3",
    "HybridCLRData/AssemblyShadow/ResourceBaselines/StandaloneOSX/M02-Baseline-36ca3c767e2bc9c3",
    "HybridCLRData/AssemblyShadow/Baselines/StandaloneOSX/M05-Baseline-v6",
)


def inventory(path: Path) -> list[dict]:
    paths = [path] if path.is_file() else sorted(item for item in path.rglob("*") if item.is_file())
    common.require(paths and all(not item.is_symlink() for item in paths), "Historical input is empty/symlinked")
    base = path.parent if path.is_file() else path
    return [{"name": item.relative_to(base).as_posix(), "size": item.stat().st_size, "sha256": common.sha256(item)} for item in paths]


def seed(review: Path) -> list[dict]:
    rows = []
    for relative in HISTORICAL_INPUTS:
        source = common.LIVE / relative
        destination = review / relative
        common.require((source.is_file() or source.is_dir()) and not source.is_symlink(), "Missing historical input: " + str(source))
        common.require(not destination.exists() and not destination.is_symlink(), "Historical destination already exists")
        before = inventory(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
        common.require(inventory(destination) == before, "Historical input copy differs: " + relative)
        rows.append({"relativePath": relative, "fileCount": len(before), "sourcePath": str(source), "destinationPath": str(destination)})
    return rows


def main(review: Path, output_root: Path, evidence_commit: str) -> None:
    review = review.resolve(strict=True)
    common.require(review != common.LIVE and review.parent == common.LIVE.parent, "Review must be a sibling checkout")
    common.require(output_root.is_absolute() and output_root.resolve() == output_root and not output_root.exists(), "New canonical output root required")
    common.require(output_root.is_relative_to(common.LIVE / "_temp/AssemblyShadow"), "Gate output must remain task-local")
    output_root.mkdir()
    evidence = review / "Docs/AssemblyShadow/M07/Evidence"
    git_tree = common.verify_git_tree(review, evidence_commit, True)
    source = common.verify_source_inventory(review, evidence_commit)
    index, retention = common.verify_retention(evidence)
    recorded = common.validate_recorded(evidence)
    historical = seed(review)
    python, strict = common.run_python_and_strict(review, output_root)
    installed = common.run_installed(review, output_root)
    common.require(not common.git(review, "status", "--short"), "Detached checkout changed during Gate B")
    receipt = {
        "schemaVersion": 1,
        "milestone": "M07",
        "gate": "B-detached-evidence-commit-tests-strict-install-and-retention",
        "result": "PASS",
        "reviewMode": "independent-deterministic-clean-detached-worktree-process",
        "checkedUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "evidenceCommit": evidence_commit,
        "reviewRoot": str(review),
        "liveArtifactRoot": str(common.LIVE),
        "gitTree": git_tree,
        "sourceInventory": source,
        "artifactIndexPath": str(evidence / "artifact-index-v6.json"),
        "artifactIndexSha256": common.sha256(evidence / "artifact-index-v6.json"),
        "retention": retention,
        "recordedSuites": recorded,
        "historicalTestInputs": historical,
        "python": python,
        "strictReplay": strict,
        "installedSourceVerification": installed,
        "status": [],
        "limitation": "Independent deterministic detached-worktree process gate, not an independent human or LLM review. It reruns all Python tests, strict Gate 3B and complete installed-source verification; Editor/native suites remain byte-bound recorded inputs checked through retained receipts and archives.",
    }
    path = output_root / "gate-b.json"
    common.write_json_new(path, receipt)
    print(json.dumps({"result": "PASS", "receipt": str(path), "sha256": common.sha256(path)}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--evidence-commit", required=True)
    args = parser.parse_args()
    main(args.review_root, args.output_root, args.evidence_commit)
