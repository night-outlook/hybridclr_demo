#!/usr/bin/env python3
"""Fail-closed M07 workflow authority for intentionally mutable demo inputs.

Exactly three workflow-owned files may differ from the pinned demo source after
M07 Configure/ValidateCompilerInputs. Their saved pre-workflow originals must
authenticate to the source-anchor Git blobs, while every other demo build input
remains byte-identical to the source anchor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from shadow_tools import (
    PINS,
    VerificationError,
    git,
    metadata_only,
    read_json,
    require,
    safe_file,
    tree,
    verify_blob,
)

MUTABLE = {
    "Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity": "m07-bootstrap-scene.original",
    "ProjectSettings/AssemblyShadowSettings.asset": "assembly-shadow-settings.original",
    "ProjectSettings/EditorBuildSettings.asset": "editor-build-settings.original",
}
BASELINE_BOUND = frozenset((
    "Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity",
    "ProjectSettings/AssemblyShadowSettings.asset",
))
BASELINE_RE = re.compile(r"^M07-Baseline-[A-Za-z0-9._-]+$")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _regular_file(root: Path, relative: str) -> Path:
    path = safe_file(root, relative)
    require(path.is_file() and not path.is_symlink(), f"Missing or linked M07 authority file: {path}")
    return path


def _demo_entry(project: Path) -> dict:
    pins = read_json(project / PINS)
    entries = pins.get("repositories", pins)
    entry = entries.get("demo")
    require(isinstance(entry, dict), "Missing demo source pin")
    revision = str(entry.get("revision", ""))
    require(re.fullmatch(r"[0-9a-fA-F]{40}", revision) is not None, "Demo source pin must be an exact SHA")
    return entry


def _context(project: Path, recovery_root: Path):
    project = project.resolve()
    recovery_root = recovery_root.resolve()
    require(project.is_dir() and not project.is_symlink(), "M07 project root is missing or linked")
    require(recovery_root.is_dir() and not recovery_root.is_symlink(), "M07 recovery root is missing or linked")
    actual_root = Path(git(project, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    require(actual_root == project, "M07 project must be its Git root")

    entry = _demo_entry(project)
    revision = entry["revision"].lower()
    git(project, "merge-base", "--is-ancestor", revision, "HEAD")
    pinned = {path: oid for path, oid in tree(project, revision).items() if not metadata_only(path)}
    current = {path: oid for path, oid in tree(project, "HEAD").items() if not metadata_only(path)}
    require(pinned == current, "Demo HEAD contains build-input changes after the source pin")
    require(set(MUTABLE).issubset(pinned), "Pinned demo source is missing an exact M07 mutable input")

    head_pins = tree(project, "HEAD").get(PINS)
    require(head_pins is not None, "Final HEAD does not contain AssemblyShadowSourcePins.json")
    verify_blob(_regular_file(project, PINS), head_pins)
    return project, recovery_root, revision, pinned


def authenticate_originals(project: Path, recovery_root: Path) -> dict:
    project, recovery_root, revision, pinned = _context(project, recovery_root)
    rows = []
    for relative, backup_name in MUTABLE.items():
        backup_path = _regular_file(recovery_root, backup_name)
        original_sha = verify_blob(backup_path, pinned[relative])
        current_path = _regular_file(project, relative)
        current_sha = sha256(current_path.read_bytes())
        rows.append({
            "path": relative,
            "backup": backup_name,
            "originalSha256": original_sha,
            "currentSha256": current_sha,
            "changed": current_sha != original_sha,
        })
    return {
        "project": project,
        "recoveryRoot": recovery_root,
        "sourceRevision": revision,
        "pinned": pinned,
        "mutablePaths": rows,
        "requiredMutationObserved": any(row["changed"] and row["path"] in BASELINE_BOUND for row in rows),
    }


def verify(project: Path, recovery_root: Path, baseline_id: str) -> dict:
    require(BASELINE_RE.fullmatch(baseline_id) is not None, "Unsafe M07 baseline identity")
    context = authenticate_originals(project, recovery_root)
    project = context["project"]
    recovery_root = context["recoveryRoot"]
    revision = context["sourceRevision"]
    pinned = context["pinned"]

    immutable_count = 0
    for path, oid in pinned.items():
        if path in MUTABLE:
            continue
        verify_blob(_regular_file(project, path), oid)
        immutable_count += 1

    untracked = git(project, "ls-files", "--others", "--exclude-standard", "-z").decode().split("\0")
    require(not any(path and not metadata_only(path) for path in untracked), "Demo has untracked build inputs")
    for directory in ("Assets", "Packages"):
        for suffix in ("*.cs", "*.asmdef"):
            base = project / directory
            if not base.exists():
                continue
            for path in base.rglob(suffix):
                relative = path.relative_to(project).as_posix()
                require(relative in pinned, f"Unpinned Unity code input: {path}")

    mutable_rows = []
    changed_required = set()
    baseline_bytes = baseline_id.encode("utf-8")
    originals = {row["path"]: row for row in context["mutablePaths"]}
    for relative, backup_name in MUTABLE.items():
        current_path = _regular_file(project, relative)
        current_bytes = current_path.read_bytes()
        current_sha = sha256(current_bytes)
        original_sha = originals[relative]["originalSha256"]
        changed = current_sha != original_sha
        if relative in BASELINE_BOUND:
            require(changed, f"Required M07 workflow mutation did not occur: {relative}")
            require(baseline_bytes in current_bytes, f"M07 workflow mutation is not bound to baseline {baseline_id}: {relative}")
            changed_required.add(relative)
        mutable_rows.append({
            "path": relative,
            "backup": backup_name,
            "originalSha256": original_sha,
            "currentSha256": current_sha,
            "currentBytes": len(current_bytes),
            "changed": changed,
            "baselineBound": relative in BASELINE_BOUND,
        })

    require(changed_required == set(BASELINE_BOUND), "Required M07 workflow mutations are incomplete")
    return {
        "schemaVersion": 1,
        "kind": "H1M07PostValidationAuthority",
        "status": "M07PostValidationAuthorityVerifiedNotBuildAccepted",
        "project": str(project),
        "recoveryRoot": str(recovery_root),
        "baselineBuildId": baseline_id,
        "sourceRevision": revision,
        "immutableBuildInputCount": immutable_count,
        "mutablePaths": mutable_rows,
        "mutablePathPolicy": sorted(MUTABLE),
        "candidateAcceptance": False,
        "humanGatePassed": False,
        "mayEnterR02": False,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--recovery-root", type=Path, required=True)
    parser.add_argument("--baseline-id", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = verify(args.project, args.recovery_root, args.baseline_id)
        print(json.dumps(result, indent=2 if args.json else None, sort_keys=bool(args.json)))
        return 0
    except (VerificationError, OSError, ValueError, KeyError, TypeError) as error:
        print("[FAIL] " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
