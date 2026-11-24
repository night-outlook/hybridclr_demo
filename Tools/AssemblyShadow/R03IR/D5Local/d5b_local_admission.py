#!/usr/bin/env python3
"""D5-B prospective read-only physical/local admission, NOT a Local handoff.

The only future executable action is a ONE-USE D5-B admission receipt after
separately reviewed immutable envelope bytes and explicit user approval.
There are NO Unity/IL2CPP/Player build/launch paths in this module.
Current APPROVED_EXECUTION_ENVELOPE_BLOB=None makes execution impossible.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
from typing import Mapping

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "D5Admission"))
import d5b_rr5_source_preflight as source

BRANCH = source.BRANCH
ROLES = source.ROLES
PLAN = HERE / "d5b_local_admission_plan_v1.json"
PLAN_BLOB = "5c0ab7a6d788ebd5adf57f1fddc567ba700632e9"
R2_REVIEW = ("Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/"
             "POST_B1_PASS12_2026-11-10/"
             "D5B_RR5_R2_INDEPENDENT_REREVIEW_2026-11-24.md")
R2_REVIEW_BLOB = "5a1e3690de6f44494bc718284315b8d9d9ced12a"
REVIEWED_SOURCE_CODE = "54780df40bddfc9d050b87f64fcd259475d99ba4"
ORIGINAL_S = "fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b"
HISTORY = ("originalS", "b1EvidenceBase", "b1Oneuse12",
           "b1NativeHostRaw", "b1B2HostRaw", "b1Preflight")
NAME = re.compile(r"^R03-B2-D5-[A-Za-z0-9][A-Za-z0-9-]{5,63}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

# The production form is deliberately CLOSED. This constant cannot be set
# by CLI, environment or user-provided JSON. It can change only in a future
# separately reviewed and committed version with explicit user approval.
APPROVED_EXECUTION_ENVELOPE_BLOB = None


class Rejected(ValueError):
    """Admission failure. No local execution permission was granted."""


def need(ok: bool, why: str) -> None:
    if not ok:
        raise Rejected(why)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") +
                        b"\0" + raw).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_json(raw: bytes) -> dict:
    try:
        return source.read_object(raw)
    except (source.Rejected, ValueError) as err:
        raise Rejected(str(err)) from err


def read_plan(*, verify_blob: bool = True) -> dict:
    need(PLAN.is_file() and not PLAN.is_symlink(),
         "Missing or symlinked D5-B plan")
    raw = PLAN.read_bytes()
    if verify_blob:
        need(git_blob(raw) == PLAN_BLOB,
             "Unreviewed D5-B local plan bytes")
    plan = parse_json(raw)
    need(plan.get("schemaVersion") == 1 and
         plan.get("kind") == "R03B2D5BLocalDryAdmissionPlanV1" and
         plan.get("branch") == BRANCH,
         "D5-B plan schema or branch changed")
    authority = plan.get("sourceAuthority")
    need(authority == {
        "sourcePreflightIndependentReview": "PassSourcePreflightOnly",
        "sourcePreflightCodeCommit": REVIEWED_SOURCE_CODE,
        "sourcePreflightProposalGitBlob": source.PROFILE_BLOB,
        "sourcePreflightReviewGitBlob": R2_REVIEW_BLOB,
        "c10PinsetGitBlob": source.MANIFEST_BLOB,
        "hybridclr_demo": "LATEST_PUSHED_HEAD_IN_SEPARATELY_APPROVED_ENVELOPE",
        **source.PINS,
    }, "D5-B independently reviewed source pins changed")
    need(plan.get("target") == {
        "platform": "macOS", "architecture": "arm64",
        "unity": "2022.3.62f2", "scriptingBackend": "IL2CPP",
        "cppConfiguration": "Release", "featureOn": True,
        "featureOffControl": True, "diagnosticsLevel": 2,
        "managedStripping": "Low", "developerPlayerMode": True,
        "minFreeGiB": 20, "actualUnityVersionObserved": "NotRun",
    }, "D5-B macOS IL2CPP target was altered")
    need(plan.get("custody") == {
        "workspaceLayout": "four-sibling-repositories",
        "originalSCommit": ORIGINAL_S,
        "historicalRootRoles": list(HISTORY),
        "historicalDataUse": "ReadOnlyComparator",
        "evidenceNamePattern": "R03-B2-D5-<unique-oneuse-id>",
        "requireAbsentExternalCanonicalOutput": True,
        "requireSourceClean": True, "requireLiveRemoteBranchExactHeads": True,
        "forbidSourceAndHistoricalOverlap": True,
        "outputCreationBeforeAdmission": False,
        "oldB1SourceCount": 14, "oldB1VmDeltaCount": 46,
    }, "D5-B history, output and source custody changed")
    producer = plan.get("producerScope")
    need(type(producer) is dict and producer == {
        "c10": "SourceProducerCandidate_NotLinkedPlayer",
        "nativeBuildAndLink": "NotRun", "c10RealPlayer": "NoCoverage",
        "originalS": "HistoricalComparatorOnly",
        "d5PlayerCells": ["D5-C%02d" % i for i in range(1, 19)],
        "d5PlayerCellsPassed": 0, "d5PlayerCellsNoCoverage": 18,
    }, "Unperformed real Player coverage reclassified")
    need(plan.get("authorization") == {
        "approvedEnvelopeGitBlob": None,
        "independentlyReviewedExecutableAdmission": "Pending",
        "explicitUserLocalApproval": "NotAuthorized",
        "WEB_TO_LOCAL": "CLOSED_NO_LOCAL_EXECUTION",
        "D5BLocalExecution": "NotAuthorized",
        "D5LocalValidation": "NotAuthorized",
        "R03Accepted": False, "H2Passed": False,
        "ReadyForHumanReviewGate": False,
        "allowNativeBuild": False, "allowPlayerLaunch": False,
    } and
    plan.get("mode") ==
        "PrimarySourceOnly_ExecutableLocalAdmissionNotAuthorized",
    "Current D5-B dry admission has no execution authority")
    return plan


def canonical_dir(path: Path, label: str) -> Path:
    need(isinstance(path, Path) and path.is_absolute() and
         ".." not in path.parts and path.is_dir() and
         not path.is_symlink() and path.resolve(strict=True) == path,
         "Exact canonical directory required: " + label)
    return path


def canonical_file(path: Path, label: str) -> Path:
    need(isinstance(path, Path) and path.is_absolute() and
         ".." not in path.parts and path.is_file() and
         not path.is_symlink() and path.resolve(strict=True) == path,
         "Exact canonical regular file required: " + label)
    return path


def separate(a: Path, b: Path) -> bool:
    return a != b and a not in b.parents and b not in a.parents


def check_custody(workspace: Path, historical: Mapping[str, Path],
                  evidence_parent: Path, oneuse_name: str) -> dict:
    workspace = canonical_dir(workspace, "four-repo workspace")
    need(type(historical) is dict and set(historical) == set(HISTORY),
         "Exactly six named historical roots are mandatory")
    roots = {role: workspace / role for role in ROLES}
    for role, root in roots.items():
        canonical_dir(root, "owning Git root " + role)
        need(root.parent == workspace,
             "All four repositories must be workspace siblings")
    need(len(set(roots.values())) == 4, "Duplicate source checkout")
    for role, root in historical.items():
        canonical_dir(root, "historical " + role)
    base = historical["b1EvidenceBase"]
    for role in ("b1Oneuse12", "b1NativeHostRaw",
                 "b1B2HostRaw", "b1Preflight"):
        need(base in historical[role].parents and historical[role] != base,
             "Original B1 custody subtree mismatch: " + role)
    need(separate(workspace, historical["originalS"]),
         "Original S must be physically disjoint from active sources")
    canonical_dir(evidence_parent, "external evidence parent")
    need(type(oneuse_name) is str and NAME.fullmatch(oneuse_name) is not None,
         "Unique D5-B output ID is malformed")
    candidate = evidence_parent / oneuse_name
    need(not candidate.exists() and not candidate.is_symlink() and
         candidate.resolve(strict=False) == candidate,
         "D5-B one-use output must be fresh, absent and canonical")
    protected = [workspace, *roots.values(), *historical.values()]
    need(all(separate(evidence_parent, p) and separate(candidate, p)
             for p in protected),
         "Output parent/root intersects a repository or historical evidence")
    return {
        "workspace": str(workspace), "roots": roots,
        "candidate": candidate, "historical": historical,
        "result": "ReadOnlyRootCustodyChecked_NoOutputCreated",
        "historicalRootsChecked": len(historical),
    }


def git(root: Path, *args: str) -> str:
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0")
    cmd = subprocess.run(["git", "-C", str(root), *args],
                         capture_output=True, text=True, timeout=60,
                         env=env, check=False)
    need(cmd.returncode == 0,
         "Git checkout/remote verification failed: " +
         " ".join(args) + ": " + cmd.stderr[-200:])
    return cmd.stdout.strip()


def exact_remote_head(raw: str, expected: str) -> str:
    need(type(expected) is str and HEX40.fullmatch(expected),
         "Exact source review SHA required")
    parts = raw.splitlines()
    need(len(parts) == 1 and "\t" in parts[0],
         "Require a single exact live remote ref")
    sha, name = parts[0].split("\t", 1)
    need(name == "refs/heads/" + BRANCH and
         HEX40.fullmatch(sha) and sha == expected,
         "Live remote source ref does not match reviewed commit")
    return sha


def inspect_original_s(original: Path) -> dict:
    canonical_dir(original, "original S physical repository")
    need(git(original, "rev-parse", "--show-toplevel") == str(original) and
         git(original, "rev-parse", "HEAD") == ORIGINAL_S and
         not git(original, "status", "--porcelain=v1",
                 "--untracked-files=all") and
         source.canonical_origin("hybridclr_demo",
                                 git(original, "remote", "get-url", "origin")),
         "Original S source identity, clean state or provenance mismatch")
    return {"role": "HistoricalComparatorOnly",
            "repository": "night-outlook/hybridclr_demo",
            "commit": ORIGINAL_S, "path": str(original),
            "actualPlayerProof": False}


def inspect_machine(unity: Path, evidence_parent: Path, *,
                    min_free_gib: int = 20) -> dict:
    need(sys.platform == "darwin" and
         platform.machine().lower() in ("arm64", "aarch64"),
         "D5-B Local admission requires actual macOS arm64")
    canonical_file(unity, "Unity executable")
    need(os.access(unity, os.X_OK), "Unity executable has no execute permission")
    need(shutil.which("xcodebuild") is not None and
         shutil.which("xcrun") is not None,
         "macOS Xcode build/SDK commands unavailable")
    free = shutil.disk_usage(evidence_parent).free
    need(free >= min_free_gib * (1024 ** 3),
         "Insufficient available disk space for fresh D5 native builds")
    # Merely checking the executable identity is NOT proof of Unity version,
    # installed IL2CPP, SDK license or BuildPipeline success.
    return {
        "platform": "macOS", "architecture": platform.machine(),
        "unityExecutable": str(unity), "unitySha256": sha256(unity),
        "availableBytes": free, "minimumGiB": min_free_gib,
        "xcodeExecutableFound": True, "xcrunExecutableFound": True,
        "actualUnityVersionVerified": "NotRun",
        "actualIl2CppBuildVerified": False,
    }


def inspect_source_and_remote(roots: Mapping[str, Path],
                              demo_head: str) -> dict:
    need(set(roots) == set(ROLES), "Exactly four Git roots required")
    need(type(demo_head) is str and HEX40.fullmatch(demo_head),
         "Source head must be exact 40-digit Git SHA")
    r = source.inspect(dict(roots), demo_head)
    need(r.get("result") == "RR5PinnedGitSourceVerified_NoLocalExecution" and
         r.get("checkedNativeAndOverlayFiles") == 16 and
         r.get("checkedEvidenceProducerFiles") == 14 and
         r.get("checkedHistoricalComparators") == 5 and
         r.get("receiptProducerBlobsMatched") is True and
         r.get("linkSourceBlobsMatched") is True,
         "The independently reviewed RR5 R2 source preflight did not pass")
    source.checked_source_blob(roots["hybridclr_demo"],
                               R2_REVIEW, R2_REVIEW_BLOB)
    # Source preflight explicitly does not authenticate current remote ref.
    # D5-B must compare the exact LIVE ref to its frozen source tuple.
    remote = {}
    for role in ROLES:
        head = demo_head if role == "hybridclr_demo" else source.PINS[role]
        raw = git(roots[role], "ls-remote", "--exit-code", "origin",
                  "refs/heads/" + BRANCH)
        remote[role] = exact_remote_head(raw, head)
    need(git(roots["hybridclr_demo"], "merge-base", "--is-ancestor",
             REVIEWED_SOURCE_CODE, demo_head) == "",
         "Reviewed R2 preflight code must be an ancestor of frozen demo HEAD")
    return {
        "result": "LocalExactGitAndLiveRemoteSourceOnly",
        "source": r, "remoteHeads": remote, "reviewedR2CodeAncestor": True,
        "actualBeeOrPlayerProven": False,
    }


def inspect(request: dict) -> dict:
    """Read-only prospective admission. No mkdir, file write or Unity launch."""
    plan = read_plan()
    need(type(request) is dict and set(request) == {
        "workspace", "historicalRoots", "evidenceParent",
        "oneuseName", "unity", "sourcePins",
    }, "D5-B inspection requires one complete structured request")
    pins = request["sourcePins"]
    need(type(pins) is dict and set(pins) == set(ROLES) and
         type(pins["hybridclr_demo"]) is str and
         HEX40.fullmatch(pins["hybridclr_demo"]) and
         all(pins.get(role) == source.PINS[role] for role in source.PINS),
         "Exact reviewed four-commit source tuple required")
    historic = request["historicalRoots"]
    need(type(historic) is dict and set(historic) == set(HISTORY),
         "Complete six historical evidence roles required")
    history_paths = {k: Path(v) for k, v in historic.items()}
    custody = check_custody(
        Path(request["workspace"]), history_paths,
        Path(request["evidenceParent"]), request["oneuseName"])
    original = inspect_original_s(history_paths["originalS"])
    sources = inspect_source_and_remote(custody["roots"],
                                        pins["hybridclr_demo"])
    machine = inspect_machine(Path(request["unity"]),
                              Path(request["evidenceParent"]),
                              min_free_gib=plan["target"]["minFreeGiB"])
    return {
        "schemaVersion": 1, "kind": "R03D5BLocalAdmissionInspectionV1",
        "result": "ReadOnlyLocalAdmissionInspected_ExecutionStillUnauthorized",
        "sourcePins": pins,
        "source": sources, "originalS": original,
        "workspace": custody["workspace"],
        "candidate": str(custody["candidate"]),
        "historicalRootCount": custody["historicalRootsChecked"],
        "host": machine,
        "outputCreated": False, "UnityOrPlayerExecuted": False,
        "approvedEnvelopeGitBlob": None,
        "D5BLocalExecution": "NotAuthorized",
        "WEB_TO_LOCAL": "CLOSED_NO_LOCAL_EXECUTION",
        "R03Accepted": False,
        "D5PlayerCellsNoCoverage": 18,
    }


def approved_envelope(raw: bytes) -> dict:
    """An immutable, separately published approval is mandatory.

    There is NO API argument or environment-variable override for this pin.
    Only a new, independently reviewed, user-approved source revision may
    replace None with the actual Git blob of the committed envelope.
    """
    need(APPROVED_EXECUTION_ENVELOPE_BLOB is not None,
         "No independently reviewed and user-approved D5-B Local envelope")
    need(type(raw) is bytes and
         git_blob(raw) == APPROVED_EXECUTION_ENVELOPE_BLOB,
         "D5-B approval envelope Git blob mismatch")
    e = parse_json(raw)
    need(e.get("schemaVersion") == 1 and
         e.get("kind") == "R03D5BApprovedDryAdmissionEnvelopeV1" and
         e.get("branch") == BRANCH and
         e.get("independentExecutableAdmissionReview") ==
            "PassedForD5BLocalDryAdmissionOnly" and
         e.get("userLocalExecutionApproval") == "ExplicitlyApproved" and
         e.get("WEB_TO_LOCAL") == "OPEN_FOR_EXACT_D5B_DRY_ADMISSION_ONLY" and
         e.get("scope") == "NoUnityOrPlayerLaunch" and
         e.get("R03Accepted") is False,
         "Reviewed source/local/user approval gates are not satisfied")
    p = e.get("sourcePins")
    need(type(p) is dict and set(p) == set(ROLES) and
         type(p["hybridclr_demo"]) is str and
         HEX40.fullmatch(p["hybridclr_demo"]) and
         all(p.get(r) == source.PINS[r] for r in source.PINS),
         "Incomplete source authority in approved envelope")
    need(type(e.get("historicalRoots")) is dict and
         set(e["historicalRoots"]) == set(HISTORY) and
         all(type(x) is str and x.startswith("/")
             for x in e["historicalRoots"].values()),
         "Approved envelope omitted historical custody roots")
    need(all(type(e.get(k)) is str and e[k].startswith("/")
             for k in ("workspace", "evidenceParent", "unity")) and
         type(e.get("oneuseName")) is str,
         "Approved envelope did not freeze physical paths and one-use ID")
    need(type(e.get("unitySha256")) is str and
         HEX64.fullmatch(e["unitySha256"]),
         "Approved envelope did not pin Unity executable bytes")
    return e


def oneuse_receipt(approved: dict, admission: dict) -> dict:
    """Pure, no-I/O future dry-admission material."""
    need(approved.get("sourcePins") == admission.get("sourcePins") and
         approved.get("oneuseName") == Path(admission["candidate"]).name and
         approved.get("workspace") == admission["workspace"] and
         approved.get("unitySha256") == admission["host"]["unitySha256"],
         "Approved envelope and actual physical admission differ")
    for key in ("historicalRoots", "evidenceParent", "unity"):
        if key == "historicalRoots":
            expected = approved[key]
            need(expected["originalS"] == admission["originalS"]["path"],
                 "Approved Original S root mismatch")
        elif key == "evidenceParent":
            need(str(Path(admission["candidate"]).parent) == approved[key],
                 "Approved external evidence parent mismatch")
        elif key == "unity":
            need(admission["host"]["unityExecutable"] == approved[key],
                 "Approved Unity executable path mismatch")
    return {
        "schemaVersion": 1, "kind": "R03D5BDryAdmissionReceiptV1",
        "result": "DryAdmissionRecorded_NoUnityOrPlayer",
        "sourcePins": admission["sourcePins"],
        "candidate": admission["candidate"],
        "unitySha256": admission["host"]["unitySha256"],
        "historicalRootCount": 6,
        "realUnityBuild": "NotRun",
        "realPlayerCellsPassed": 0,
        "realPlayerCellsNoCoverage": 18,
        "WEB_TO_LOCAL": "CLOSED_AFTER_SINGLE_DRY_ADMISSION",
        "R03Accepted": False, "ReadyForHumanReviewGate": False,
    }


def write_exclusive(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8") as output:
        json.dump(value, output, indent=2, sort_keys=True,
                  ensure_ascii=True, allow_nan=False)
        output.write("\n")


def seal_oneuse_dry_admission(approved: dict, admission: dict) -> dict:
    """Future executable D5-B scope: records only an admission, no Unity.

    Caller must have obtained approved_envelope() BEFORE inspecting sources.
    This function never calls Unity, dotnet, a Player, or a native compiler.
    """
    result = oneuse_receipt(approved, admission)
    root = Path(admission["candidate"])
    need(not root.exists() and not root.is_symlink(),
         "Approved one-use destination was already consumed")
    root.mkdir(mode=0o700, exist_ok=False)
    write_exclusive(root / "ADMISSION.json", {
        "sourceAndHost": admission, "approvalEnvelopeGitBlob":
            APPROVED_EXECUTION_ENVELOPE_BLOB,
        "result": "RecordedReadOnlyBeforeAnyBuild",
        "R03Accepted": False})
    write_exclusive(root / "CELLS.json", {
        "kind": "R03D5BInitialNoCoverageCellsV1",
        "cells": [
            {"id": "D5-C%02d" % i, "result": "NoCoverage",
             "evidenceClass": "NotRun",
             "reason": "No real Unity/IL2CPP Player or case producer executed"}
            for i in range(1, 19)],
        "D5LocalValidation": "NotAuthorized",
    })
    write_exclusive(root / "LOCAL_BATCH_RESULT.json", result)
    hashes = []
    for name in ("ADMISSION.json", "CELLS.json", "LOCAL_BATCH_RESULT.json"):
        p = root / name
        hashes.append({"path": name, "sha256": sha256(p),
                       "bytes": p.stat().st_size})
    write_exclusive(root / "MANIFEST.json", {
        "schemaVersion": 1, "kind": "R03D5BDryAdmissionLedgerV1",
        "files": hashes, "realPlayerEvidence": False,
        "R03Accepted": False})
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=("preview", "execute"))
    parser.add_argument("--request", type=Path)
    parser.add_argument("--approved-envelope", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.mode == "execute":
            # Stop BEFORE reading user paths or performing any read-only Git
            # operations. No current source build can pass this hard gate.
            need(APPROVED_EXECUTION_ENVELOPE_BLOB is not None,
                 "D5-B Local execution is not authorized")
            need(args.approved_envelope is not None,
                 "Separately approved immutable envelope required")
            approved = approved_envelope(args.approved_envelope.read_bytes())
            request = {
                "workspace": approved["workspace"],
                "historicalRoots": approved["historicalRoots"],
                "evidenceParent": approved["evidenceParent"],
                "oneuseName": approved["oneuseName"],
                "unity": approved["unity"],
                "sourcePins": approved["sourcePins"],
            }
            observation = inspect(request)
            result = seal_oneuse_dry_admission(approved, observation)
        else:
            need(args.approved_envelope is None,
                 "Read-only preview must not accept approval-like inputs")
            need(args.request is not None and args.request.is_file() and
                 not args.request.is_symlink(),
                 "Read-only preview requires one external JSON request")
            result = inspect(parse_json(args.request.read_bytes()))
        print(json.dumps(result, sort_keys=True, allow_nan=False))
        return 0
    except (Rejected, source.Rejected, OSError, ValueError,
            subprocess.TimeoutExpired) as exc:
        print(json.dumps({
            "schemaVersion": 1, "kind": "R03D5BLocalAdmissionFailureV1",
            "result": "NotAuthorized" if args.mode == "execute" else "BlockedBeforeBuild",
            "reason": str(exc),
            "outputCreated": False,
            "WEB_TO_LOCAL": "CLOSED_NO_LOCAL_EXECUTION",
            "D5BLocalExecution": "NotAuthorized",
            "R03Accepted": False,
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
