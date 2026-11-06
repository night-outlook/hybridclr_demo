#!/usr/bin/env python3
"""R03 initializer oneuse-05: read-only, single-sample capacity readiness.

This script does not create, delete, move, purge or edit ANY filesystem item.
It does not authorize a Local batch on its own: two fresh independent samples
and all existing source/CI/SDK/custody gates must pass separately.

Explicit candidate paths are INSPECTION ONLY, never permission to delete.
Neither historical evidence nor source/Unity/SDK may be reclaimed by inference.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import stat

MIN_GIB = 25
HARD_GIB = 20
ADVISORY_GIB = 40
GIB = 1024 ** 3
MAX_ENTRIES = 50000
SYSTEM_EXCLUSIONS = ("/Applications", "/Library", "/System", "/usr",
                     "/opt", "/private", "/Volumes", "/bin", "/sbin")


class CapacityReadinessError(ValueError):
    pass


def need(test, message):
    if not test:
        raise CapacityReadinessError(message)


def is_overlapping(a: Path, b: Path) -> bool:
    return a == b or a in b.parents or b in a.parents


def exact_existing(path: Path, label: str, *, directory: bool = True) -> Path:
    need(path.exists() and path.is_absolute() and ".." not in path.parts
         and not path.is_symlink() and path.resolve(strict=False) == path,
         "Noncanonical or symlink " + label)
    need(path.is_dir() if directory else path.is_file(),
         "Missing regular " + label)
    return path


def fresh_child(path: Path, parent: Path, label: str):
    need(path.is_absolute() and ".." not in path.parts and
         path.parent == parent and
         path.resolve(strict=False) == path and
         not path.exists() and not path.is_symlink(),
         "Fresh absent canonical " + label + " required")


def capacity_state(free_bytes: int) -> dict:
    need(type(free_bytes) is int and free_bytes >= 0,
         "Actual nonnegative available bytes required")
    minimum = MIN_GIB * GIB
    return {
        "state": ("ReadySingleSample_NotBatchAuthorized"
                  if free_bytes >= minimum else "CapacityBlocked"),
        "freeBytes": free_bytes, "freeGiB": free_bytes / GIB,
        "minimumBytes": minimum, "minimumGiB": MIN_GIB,
        "hardMinimumGiB": HARD_GIB, "advisoryGiB": ADVISORY_GIB,
        "bytesBelowMinimum": max(minimum - free_bytes, 0),
        "bytesAboveMinimum": max(free_bytes - minimum, 0),
        "belowAdvisory": free_bytes < ADVISORY_GIB * GIB,
        "thresholdLowered": False,
        "twoIndependentSamplesCompleted": False,
        "unityOrPlayerExecuted": False, "runtimeAcceptance": False,
        "R03Accepted": False, "H2Passed": False,
    }


def candidate_inventory(candidate: Path, *, parent: Path,
                        protected: tuple[Path, ...]) -> dict:
    """Inspect user-specified path only. Never follow links or assume reclaim."""
    candidate = exact_existing(candidate, "candidate directory")
    need(candidate != parent and candidate != parent.parent and
         all(not is_overlapping(candidate, p) for p in protected),
         "Candidate overlaps protected source, original S, SDK or evidence")
    need(all(not is_overlapping(candidate, Path(prefix))
             for prefix in SYSTEM_EXCLUSIONS),
         "Candidate overlaps system/SDK-sensitive tree")
    need(os.stat(candidate).st_dev == os.stat(parent).st_dev,
         "Candidate is not on the actual output-parent device")
    seen = 0
    total_allocated = 0
    total_size = 0
    symlinks = 0
    dirs = 0
    regular = 0
    truncated = False
    # Do not walk a symlink. os.walk(..., followlinks=False) is not enough
    # by itself: also inspect lstat nodes before descending.
    for current, directory_names, file_names in os.walk(candidate, followlinks=False):
        directory_names.sort()
        file_names.sort()
        kept = []
        for name in directory_names:
            node = Path(current) / name
            mode = os.lstat(node).st_mode
            seen += 1
            if stat.S_ISLNK(mode):
                symlinks += 1
            else:
                need(stat.S_ISDIR(mode), "Unexpected non-directory candidate node")
                kept.append(name)
                dirs += 1
            if seen >= MAX_ENTRIES:
                truncated = True
                break
        directory_names[:] = kept if not truncated else []
        if truncated:
            break
        for name in file_names:
            node = Path(current) / name
            info = os.lstat(node)
            seen += 1
            if stat.S_ISLNK(info.st_mode):
                symlinks += 1
            else:
                need(stat.S_ISREG(info.st_mode),
                     "Unexpected non-regular candidate node")
                total_allocated += int(info.st_blocks) * 512
                total_size += info.st_size
                regular += 1
            if seen >= MAX_ENTRIES:
                truncated = True
                break
        if truncated:
            break
    return {
        "path": str(candidate),
        "classification": "ReadOnlyCandidateEstimate_NotDeletionApproval",
        "entriesInspected": seen, "entryLimit": MAX_ENTRIES,
        "truncated": truncated, "sizeMayBeUnderestimate": truncated,
        "regularFiles": regular, "directories": dirs,
        "symlinksNotFollowed": symlinks,
        "regularLogicalBytesObserved": total_size,
        "regularAllocatedBytesObserved": total_allocated,
        "bytesReclaimable": "Unknown_APFSClonesSnapshotsAndCaches",
        "deletionApproved": False, "deleteOrModifyOperations": 0,
    }


def inspect(*, parent: Path, run_root: Path, host_root: Path,
            workspace: Path, original_s: Path, unity: Path,
            candidates: tuple[Path, ...] = (),
            additional_protected: tuple[Path, ...] = ()) -> dict:
    parent = exact_existing(parent, "output parent")
    workspace = exact_existing(workspace, "workspace root")
    original_s = exact_existing(original_s, "historical original S")
    unity = exact_existing(unity, "Unity executable", directory=False)
    fresh_child(run_root, parent, "oneuse run root")
    fresh_child(host_root, parent, "oneuse raw host root")
    need(run_root != host_root and
         host_root.name == run_root.name + "-native-host-raw",
         "New product/host roots must have one exact distinct naming contract")
    extra = tuple(exact_existing(p, "additional protected root") for p in
                  additional_protected)
    protect = (workspace, original_s, parent, unity,
               run_root, host_root, *extra)
    need(all(not is_overlapping(run_root, root) and
             not is_overlapping(host_root, root)
             for root in (workspace, original_s, unity)),
         "Output may not overlap any source or Unity root")
    # Exactly the same measurement definition as the failed oneuse-04
    # independent Local evidence: f_bavail * f_frsize.
    info = os.statvfs(parent)
    free_bytes = int(info.f_bavail) * int(info.f_frsize)
    state = capacity_state(free_bytes)
    samples = [candidate_inventory(p, parent=parent, protected=protect)
               for p in candidates]
    return {
        "schemaVersion": 1,
        "kind": "R03InitializerOneUse05ReadOnlyCapacitySampleV1",
        "result": state["state"],
        "timeUtc": datetime.now(timezone.utc).isoformat(),
        "outputParent": str(parent),
        "device": os.stat(parent).st_dev,
        "runRoot": str(run_root), "hostRawRoot": str(host_root),
        "bothFreshRootsAbsent": True,
        "capacity": state,
        "explicitCandidateInspectionOnly": samples,
        "candidateCount": len(samples),
        "additionalProtectedRootCount": len(extra),
        "readOnly": True, "writesPerformed": 0, "deletionsPerformed": 0,
        "automaticCleanupEnabled": False,
        "futureUnityDiskUseGuaranteed": False,
        "freshSampleNumber": "SingleIndependentInvocationOnly",
        "eligibleForUnityRun": False,
        "requiresSecondIndependentSample": True,
        "requiresFreshStandardMacAdmission": True,
        "requiresExactGitCIAndHistoricalPreservation": True,
        "runtimeAcceptance": False, "R03Accepted": False,
        "ReadyForHumanReviewGate": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("output-parent", "run-root", "host-raw-root",
                "workspace", "original-s", "unity"):
        parser.add_argument("--" + arg, required=True, type=Path)
    parser.add_argument("--candidate", action="append", default=[], type=Path,
                        help="EXPLICIT read-only candidate inspection; never deletion authorization")
    parser.add_argument("--protected-root", action="append", default=[], type=Path,
                        help="Additional known SDK, archive or user-owned root to exclude")
    args = parser.parse_args()
    report = inspect(parent=args.output_parent, run_root=args.run_root,
                     host_root=args.host_raw_root, workspace=args.workspace,
                     original_s=args.original_s, unity=args.unity,
                     candidates=tuple(args.candidate),
                     additional_protected=tuple(args.protected_root))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
