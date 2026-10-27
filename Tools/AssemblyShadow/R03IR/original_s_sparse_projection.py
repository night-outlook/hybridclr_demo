#!/usr/bin/env python3
"""Guarded one-use sparse projection of the retained original-S fc55 worktree.

This is a bounded environment remediation, not a historical audit or Player.
--inspect only reads; --apply de-materializes unrelated CLEAN TRACKED checkout
files without deleting Git objects, altering the fc55 commit, or modifying the
protected original-S checkpoint subtree. It never prunes worktrees/caches.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone

import current_native_environment_admission as admission
import run_current_native_validation_cycle as cycle

FC55 = "fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b"
RETAINED_PATH = Path("/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse")
CHECKPOINT = "Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready"
CHECKPOINT_TREE = "2acdcc0ec3c0f15dea11f99bc9c5d6d0f431de79"
CHECKPOINT_FILES = 16978
CHECKPOINT_LOGICAL_BYTES = 3882340952
SAMPLE_MIN_GIB = 20
GIT_TIMEOUT_SECONDS = 3600


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def git(repo: Path, *args: str, allow_failure: bool = False,
        timeout: int = 240) -> subprocess.CompletedProcess:
    result = subprocess.run(["git", "-C", str(repo), *args],
                            capture_output=True, timeout=timeout, check=False)
    if not allow_failure:
        require(result.returncode == 0,
                "Git operation failed: " + repr(args) + " " +
                result.stderr.decode("utf-8", errors="replace")[-350:])
    return result


def canonical_relative(value: str) -> str:
    require(isinstance(value, str) and value and "\\" not in value and
            "\x00" not in value and "\n" not in value and
            "\t" not in value, "Malformed projected source path")
    p = PurePosixPath(value)
    require(not p.is_absolute() and ".." not in p.parts and str(p) == value,
            "Noncanonical relative source path")
    return value


def require_clean(repo: Path) -> None:
    status = git(repo, "status", "--porcelain=v1", "--untracked-files=all").stdout
    require(status == b"", "Original-S source must be absolutely clean")
    submodules = git(repo, "submodule", "status", "--recursive").stdout
    require(not submodules.strip(),
            "Submodule checkout requires separate custody review; sparse apply refused")



def require_unhidden_index(repo: Path) -> int:
    """Refuse assume-unchanged/skip-worktree flags before de-materialization."""
    raw = git(repo, "ls-files", "-v", "-z", timeout=600).stdout
    count = 0
    for entry in raw.split(b"\x00"):
        if not entry:
            continue
        require(entry.startswith(b"H "),
                "Hidden or abnormal tracked index entry would risk unobserved data: " +
                entry[:160].decode("utf-8", errors="replace"))
        count += 1
    require(count >= CHECKPOINT_FILES,
            "Original worktree full index is implausibly small for fc55")
    return count


def sparse_enabled(repo: Path) -> bool:
    result = git(repo, "config", "--bool", "core.sparseCheckout", allow_failure=True)
    require(result.returncode in (0, 1), "Cannot read worktree sparse configuration")
    return result.returncode == 0 and result.stdout.strip().lower() == b"true"


def checkpoint_rows(repo: Path, relative: str) -> list[dict]:
    canonical_relative(relative)
    data = git(repo, "ls-tree", "-rlz", "HEAD", "--", relative, timeout=600).stdout
    rows = []
    for record in data.split(b"\x00"):
        if not record:
            continue
        attributes, rawpath = record.split(b"\t", 1)
        # ls-tree -l pads size with spaces; tokenize arbitrary ASCII whitespace.
        parts = attributes.decode("ascii").split()
        require(len(parts) == 4, "Malformed Git tree entry")
        mode, kind, oid, size = parts
        path = canonical_relative(rawpath.decode("utf-8"))
        require(mode in ("100644", "100755") and kind == "blob" and
                re.fullmatch(r"[0-9a-f]{40}", oid) is not None and
                size.isdecimal() and
                (path == relative or path.startswith(relative + "/")),
                "Only canonical regular committed checkpoint files allowed")
        rows.append({"path": path, "gitBlob": oid, "size": int(size)})
    require(bool(rows) and len({r["path"] for r in rows}) == len(rows),
            "Exact checkpoint tree roster not available")
    return rows


def actual_git_blob(path: Path, length: int) -> str:
    require(path.is_file() and not path.is_symlink() and path.resolve() == path,
            "Checkpoint file missing or aliased: " + str(path))
    s = path.stat()
    require(stat.S_ISREG(s.st_mode) and s.st_size == length,
            "Checkpoint size or file mode differs: " + str(path))
    h = hashlib.sha1()
    h.update(b"blob " + str(length).encode("ascii") + b"\x00")
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_materialized(repo: Path, rows: list[dict]) -> dict:
    verified = 0
    total = 0
    for row in rows:
        path = repo / row["path"]
        require(actual_git_blob(path, row["size"]) == row["gitBlob"],
                "Protected checkpoint differs from pinned Git bytes: " + row["path"])
        verified += 1
        total += row["size"]
    return {"kind": "R03OriginalSProtectedCheckpointByteVerification",
            "result": "PassedPhysicalFileVsPinnedGitBlobs",
            "files": verified, "logicalBytes": total,
            "materializedEvidenceRewritten": False,
            "R03Accepted": False}


def checkpoint_identity(repo: Path) -> list[dict]:
    sha = git(repo, "rev-parse", "HEAD:" + CHECKPOINT).stdout.decode().strip()
    require(sha == CHECKPOINT_TREE, "Original S checkpoint Git tree changed")
    rows = checkpoint_rows(repo, CHECKPOINT)
    require(len(rows) == CHECKPOINT_FILES and
            sum(row["size"] for row in rows) == CHECKPOINT_LOGICAL_BYTES,
            "Original S full checkpoint cardinality or byte roster changed")
    return rows


def inspect(workspace: Path, original: Path, demo_commit: str,
            *, check_bytes: bool) -> tuple[dict, list[dict]]:
    require(original == RETAINED_PATH and original.is_absolute() and
            original.resolve(strict=True) == original and
            not original.is_symlink(), "Exactly the retained canonical fc55 worktree is allowed")
    admission.registered_original(workspace, original)
    current = cycle.validate_sources(workspace, demo_commit)
    require(current["result"] == "PassedReadOnlySourceAdmission_NotBuildOrRuntime",
            "Current four-source authority mismatch")
    require_clean(original)
    enabled = sparse_enabled(original)
    # A clean status alone can miss deliberately hidden assume-unchanged files.
    # Reject those before any clean tracked file outside the projection disappears.
    full_index_files = require_unhidden_index(original) if not enabled else None
    rows = checkpoint_identity(original)
    physical = verify_materialized(original, rows) if check_bytes else {
        "result": "NotRun_InspectOnlyNoFullRehash"}
    free = shutil.disk_usage(original.parent).free
    return {
        "kind": "R03OriginalSRetainedSparseProjectionAdmission",
        "result": "PassedReadOnlyInspect_NotAnExecution",
        "repo": str(original), "commit": FC55, "checkpoint": CHECKPOINT,
        "checkpointTree": CHECKPOINT_TREE, "checkpointFiles": len(rows),
        "checkpointLogicalBytes": sum(x["size"] for x in rows),
        "originalWorktreeSparseEnabled": enabled,
        "preProjectionUnhiddenIndexFiles": full_index_files,
        "beforeCapacityBytes": free,
        "beforeCapacityGiB": round(free / 1024**3, 3),
        "physicalCheckpoint": physical, "currentSources": current["repositories"],
        "gitObjectHistoryDeleted": False, "originalArchiveExecuted": False,
        "coordinatorInvoked": False, "R03Accepted": False,
    }, rows


def write_new(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")


def sparse_command(repo: Path, checkpoint: str, *, timeout=GIT_TIMEOUT_SECONDS) -> dict:
    """One real Git sparse-checkout invocation, no retry, no cleanup."""
    canonical_relative(checkpoint)
    args = ["sparse-checkout", "set", "--cone", "--no-sparse-index", checkpoint]
    try:
        result = git(repo, *args, allow_failure=True, timeout=timeout)
        return {"argv": ["git", "-C", str(repo), *args],
                "exitCode": result.returncode,
                "stdout": result.stdout.decode("utf-8", errors="replace"),
                "stderr": result.stderr.decode("utf-8", errors="replace"),
                "timedOut": False, "attemptCount": 1}
    except subprocess.TimeoutExpired as e:
        return {"argv": ["git", "-C", str(repo), *args],
                "exitCode": None, "timedOut": True, "attemptCount": 1,
                "stdout": (e.stdout or b"").decode("utf-8", errors="replace"),
                "stderr": (e.stderr or b"").decode("utf-8", errors="replace")}


def apply(workspace: Path, original: Path, demo_commit: str,
          evidence: Path) -> dict:
    # No source or checkout mutation until all evidence/custody prerequisites pass.
    cycle.validate_destination(workspace, original, evidence)
    require(not evidence.exists() and evidence.parent.is_dir(),
            "Exactly one absent external remediation evidence root required")
    pre, rows = inspect(workspace, original, demo_commit, check_bytes=True)
    require(pre["originalWorktreeSparseEnabled"] is False,
            "Worktree is already sparse; never repeat a sparse conversion")
    evidence.mkdir(mode=0o700)
    write_new(evidence / "INTENT.json", {
        "kind": "R03OriginalSOnceOnlySparseProjection",
        "source": pre, "scope": "Only projected clean tracked files",
        "commandAuthorized": True, "commandInvocationsPlanned": 1,
        "trackedFilesOutsideCheckpointDeMaterialized": True,
        "gitCommitOrObjectHistoryDeleted": False, "retriesAllowed": False,
        "historicalEvidenceDeletedFromGit": False,
        "reversalMayRequireOriginalFullDiskCapacity": True,
        "coordinatorInvoked": False, "runtimeAcceptance": False})
    report = {
        "kind": "R03OriginalSOnceOnlySparseProjection",
        "result": "FailedOrIncomplete_RetainRawForPrimary",
        "startedUtc": utc(), "source": pre,
        "oneUseEvidenceRoot": str(evidence), "attemptCount": 0,
        "originalGitCommitChanged": None, "checkpointBytesPreserved": None,
        "coordinatorInvoked": False, "R03Accepted": False,
        "ReadyForHumanReviewGate": False, "runtimeAcceptance": False}
    try:
        command = sparse_command(original, CHECKPOINT)
        report["attemptCount"] = 1
        write_new(evidence / "GIT_COMMAND.json", command)
        require(command["exitCode"] == 0 and not command["timedOut"],
                "Sparse conversion failed or timed out; do not retry")
        require(sparse_enabled(original), "Sparse configuration was not activated")
        included = git(original, "sparse-checkout", "list").stdout.decode().splitlines()
        require(included == [CHECKPOINT], "Actual sparse paths differ from contract")
        admission.registered_original(workspace, original)
        post_sources = cycle.validate_sources(workspace, demo_commit)
        require(post_sources["result"] == "PassedReadOnlySourceAdmission_NotBuildOrRuntime",
                "Four authoritative source checkouts changed during sparse projection")
        require_clean(original)
        after_rows = checkpoint_identity(original)
        require(after_rows == rows, "Original S checkpoint metadata changed")
        physical = verify_materialized(original, rows)
        after = shutil.disk_usage(original.parent).free
        report.update({
            "result": "PassedBoundedSourceProjection_RequiresFreshCapacityAdmission",
            "checkpointBytesPreserved": physical["result"] ==
                "PassedPhysicalFileVsPinnedGitBlobs",
            "originalGitCommitChanged": False,
            "worktreeStillRegisteredAndClean": True,
            "sourcePostflight": post_sources["result"],
            "activeSparsePaths": included, "checkpointFiles": len(rows),
            "checkpointLogicalBytes": CHECKPOINT_LOGICAL_BYTES,
            "beforeFreeBytes": pre["beforeCapacityBytes"],
            "afterFreeBytes": after,
            "observedFreeDeltaBytes": after - pre["beforeCapacityBytes"],
            "afterFreeGiB": round(after / 1024**3, 3),
            "fixed20GiBCurrentlyAvailable": after >= SAMPLE_MIN_GIB * 1024**3,
            "advisory40GiBAvailable": after >= 40 * 1024**3,
            "actualFuturePlayerDiskUseProven": False,
            "gitCommitOrObjectHistoryDeleted": False,
            "sourceCheckoutChangesTracked": False})
    except BaseException as error:
        report["failure"] = type(error).__name__ + ": " + str(error)
        try:
            report["postFailureHEAD"] = git(original, "rev-parse", "HEAD").stdout.decode().strip()
            report["postFailureSparseEnabled"] = sparse_enabled(original)
            report["postFailureClean"] = (git(
                original, "status", "--porcelain=v1", "--untracked-files=all").stdout == b"")
        except Exception as e:
            report["postFailureInspectionError"] = repr(e)
    finally:
        report["finishedUtc"] = utc()
        write_new(evidence / "RESULT.json", report)
    return report


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--inspect", action="store_true")
    mode.add_argument("--apply", action="store_true")
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--original-s", type=Path, required=True)
    p.add_argument("--demo-commit", required=True)
    p.add_argument("--evidence", type=Path,
                   help="Fresh external remediation evidence root (required for --apply)")
    o = p.parse_args()
    require(__debug__, "Optimized Python mode refused")
    try:
        if o.inspect:
            require(o.evidence is None, "Inspection is strictly no-write")
            info, _ = inspect(o.workspace, o.original_s, o.demo_commit,
                              check_bytes=False)
            print(json.dumps(info, indent=2, sort_keys=True))
            return 0
        require(o.evidence is not None, "--apply needs fresh external evidence root")
        report = apply(o.workspace, o.original_s, o.demo_commit, o.evidence)
        print(json.dumps({k: report.get(k) for k in (
              "result", "oneUseEvidenceRoot", "attemptCount", "checkpointBytesPreserved",
              "beforeFreeBytes", "afterFreeBytes", "fixed20GiBCurrentlyAvailable",
              "advisory40GiBAvailable", "failure", "coordinatorInvoked")},
              indent=2, sort_keys=True))
        return 0 if report["result"] == (
            "PassedBoundedSourceProjection_RequiresFreshCapacityAdmission") else 2
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({"kind": "R03OriginalSRetainedSparseProjection",
                          "result": "BlockedBeforeProjection",
                          "reason": str(error), "coordinatorInvoked": False,
                          "sourceMutationAuthorized": False,
                          "R03Accepted": False}, indent=2, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
