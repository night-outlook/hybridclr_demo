#!/usr/bin/env python3
"""D5-B prospective read-only physical/local admission, NOT a Local handoff.

The only future executable action is a ONE-USE D5-B admission receipt after
separately reviewed immutable envelope bytes and explicit user approval.
There are NO Unity/IL2CPP/Player build/launch paths in this module.
Current APPROVED_EXECUTION_ENVELOPE_BLOB=None makes execution impossible.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import stat
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


class PathIdentityMismatch(Rejected):
    """The approved output pathname no longer names the open evidence root."""


class PartialOutput(Rejected):
    """A one-use root was created; do not retry or report outputCreated=false."""

    def __init__(self, root: Path, reason: str, files: list[dict], *,
                 commit_visible: bool = False,
                 commit_uncertain: bool = False,
                 path_identity_uncertain: bool = False,
                 cleanup_errors: tuple[str, ...] = ()):
        super().__init__(reason)
        self.root = root
        self.files = tuple(item["path"] for item in files)
        self.ledger = tuple(files)
        self.commit_visible = commit_visible
        self.commit_uncertain = commit_uncertain
        self.path_identity_uncertain = path_identity_uncertain
        self.cleanup_errors = cleanup_errors



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


def directory_identity(path: Path) -> dict:
    stat = path.stat()
    return {"device": stat.st_dev, "inode": stat.st_ino}


def check_custody(workspace: Path, historical: Mapping[str, Path],
                  evidence_parent: Path, oneuse_name: str, *,
                  expect_output_present: bool = False) -> dict:
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
    need(len(set(historical.values())) == len(HISTORY),
         "Distinct physical roots required for all six historical roles")
    base = historical["b1EvidenceBase"]
    for role in ("b1Oneuse12", "b1NativeHostRaw",
                 "b1B2HostRaw", "b1Preflight"):
        need(base in historical[role].parents and historical[role] != base,
             "Original B1 custody subtree mismatch: " + role)
    b1_children = [historical[role] for role in
                   ("b1Oneuse12", "b1NativeHostRaw",
                    "b1B2HostRaw", "b1Preflight")]
    need(all(separate(a, b) for i, a in enumerate(b1_children)
             for b in b1_children[i + 1:]),
         "Historical B1 child roles cannot overlap or alias")
    need(separate(workspace, historical["originalS"]),
         "Original S must be physically disjoint from active sources")
    canonical_dir(evidence_parent, "external evidence parent")
    need(type(oneuse_name) is str and NAME.fullmatch(oneuse_name) is not None,
         "Unique D5-B output ID is malformed")
    candidate = evidence_parent / oneuse_name
    if expect_output_present:
        canonical_dir(candidate, "existing one-use output")
    else:
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
        "evidenceParentIdentity": directory_identity(evidence_parent),
        "historicalRootIdentities": {
            role: directory_identity(historical[role]) for role in HISTORY},
        "sourceRootIdentities": {
            role: directory_identity(roots[role]) for role in ROLES},
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


def read_only_host_tool(argv: list[str], *, allow_empty: bool = False) -> str:
    """Query Xcode tooling without compiling, running Unity or creating files."""
    out = subprocess.run(argv, capture_output=True, text=True,
                         check=False, timeout=45)
    need(out.returncode == 0 and (allow_empty or bool(out.stdout.strip())),
         "Required macOS Xcode/SDK check failed: " + " ".join(argv) +
         " " + out.stderr[-180:])
    return out.stdout.strip()


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
    xcode = read_only_host_tool(["xcodebuild", "-version"])
    need(re.search(r"^Xcode [0-9]", xcode, re.MULTILINE) is not None,
         "Actual Xcode toolchain version is unavailable")
    sdk = Path(read_only_host_tool(
        ["xcrun", "--sdk", "macosx", "--show-sdk-path"]))
    # xcrun may return the standard MacOSX.sdk symlink. This is not a
    # historical evidence/source root: resolve the SDK and verify its target.
    need(sdk.is_absolute() and sdk.is_dir(),
         "Required macOS SDK directory does not exist")
    sdk_real = sdk.resolve(strict=True)
    canonical_dir(sdk_real, "resolved macOS SDK")
    clang = Path(read_only_host_tool(
        ["xcrun", "--sdk", "macosx", "--find", "clang"]))
    need(clang.is_file() and os.access(clang, os.X_OK),
         "Xcode macOS SDK clang compiler not installed")
    # A license probe is metadata admission, NOT Unity or native compilation.
    read_only_host_tool(["xcodebuild", "-license", "check"],
                        allow_empty=True)
    # Unity version and the IL2CPP module must be proved by a fresh Unity
    # BuildPipeline receipt, not inferred from a plausible executable path.
    return {
        "platform": "macOS", "architecture": platform.machine(),
        "unityExecutable": str(unity), "unitySha256": sha256(unity),
        "availableBytes": free, "minimumGiB": min_free_gib,
        "xcodeVersionOutput": xcode,
        "macosSdkPath": str(sdk_real), "macosClangPath": str(clang),
        "xcodeLicenseChecked": True,
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


def inspect(request: dict, *, expect_output_present: bool = False) -> dict:
    """Read-only admission, including optional existing output postflight."""
    plan = read_plan()
    need(type(request) is dict and set(request) == {
        "workspace", "historicalRoots", "evidenceParent",
        "oneuseName", "unity", "sourcePins",
    }, "D5-B inspection requires one complete structured request")
    need(all(type(request[k]) is str and request[k].startswith("/")
             for k in ("workspace", "evidenceParent", "unity")) and
         type(request["oneuseName"]) is str,
         "Canonical absolute paths and a string one-use ID are mandatory")
    pins = request["sourcePins"]
    need(type(pins) is dict and set(pins) == set(ROLES) and
         type(pins["hybridclr_demo"]) is str and
         HEX40.fullmatch(pins["hybridclr_demo"]) and
         all(pins.get(role) == source.PINS[role] for role in source.PINS),
         "Exact reviewed four-commit source tuple required")
    historic = request["historicalRoots"]
    need(type(historic) is dict and set(historic) == set(HISTORY),
         "Complete six historical evidence roles required")
    need(all(type(v) is str and v.startswith("/")
             for v in historic.values()),
         "Historical paths must be absolute strings")
    history_paths = {k: Path(v) for k, v in historic.items()}
    custody = check_custody(
        Path(request["workspace"]), history_paths,
        Path(request["evidenceParent"]), request["oneuseName"],
        expect_output_present=expect_output_present)
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
        "historicalRoots": {role: str(history_paths[role]) for role in HISTORY},
        "custodyIdentity": {
            "parent": custody["evidenceParentIdentity"],
            "history": custody["historicalRootIdentities"],
            "sources": custody["sourceRootIdentities"],
        },
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
            need(expected == admission["historicalRoots"] and
                 expected["originalS"] == admission["originalS"]["path"],
                 "Every approved historical root must match actual custody")
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


def _json_bytes(value: dict) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True,
                       ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def _write_locked(root_fd: int, name: str, value: dict) -> None:
    """Exclusive regular file in the already-open one-use directory.

    No child path is resolved through a mutable parent string. On-disk
    partial writes remain consumed evidence, never an accepted receipt.
    """
    need(re.fullmatch(r"[A-Z_]+\.json", name) is not None,
         "Only fixed one-use receipt filenames may be written")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    fd = os.open(name, flags, 0o600, dir_fd=root_fd)
    with os.fdopen(fd, "wb") as stream:
        stream.write(_json_bytes(value))
        stream.flush()
        os.fsync(stream.fileno())


def _locked_file_ledger(root_fd: int) -> list[dict]:
    """Read actual completed bytes, through the bound directory descriptor."""
    rows = []
    for name in sorted(os.listdir(root_fd)):
        entry_stat = os.stat(name, dir_fd=root_fd, follow_symlinks=False)
        need(name.endswith(".json") and entry_stat.st_size >= 0 and
             stat.S_ISREG(entry_stat.st_mode),
             "Unexpected one-use output entry")
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=root_fd)
        with os.fdopen(fd, "rb") as stream:
            raw = stream.read()
        rows.append({"path": name, "sha256": hashlib.sha256(raw).hexdigest(),
                     "bytes": len(raw)})
    return rows


def _assert_open_path(parent_fd: int, root_fd: int, root: Path,
                      expected_parent: dict) -> None:
    """Bind the string paths back to the previously opened physical inodes."""
    pstat = os.fstat(parent_fd)
    rstat = os.fstat(root_fd)
    need(not root.is_symlink() and root.is_dir() and
         directory_identity(root.parent) == expected_parent and
         pstat.st_dev == expected_parent["device"] and
         pstat.st_ino == expected_parent["inode"] and
         root.stat().st_dev == rstat.st_dev and
         root.stat().st_ino == rstat.st_ino,
         "Bound D5-B physical parent/root identity changed")


def _assert_final_path_identity(root_fd: int, root: Path,
                                expected_parent: dict) -> None:
    """Rebind the approved pathname to the open output inode after parent close.

    This is a point-in-time check, not a cross-process namespace lock.
    A final read-only check also runs after the last visibility-changing write.
    """
    try:
        canonical_dir(root.parent, "approved D5-B finalization parent")
        parent = os.stat(root.parent, follow_symlinks=False)
        named_root = os.stat(root, follow_symlinks=False)
        opened_root = os.fstat(root_fd)
        valid = (
            stat.S_ISDIR(parent.st_mode) and
            parent.st_dev == expected_parent["device"] and
            parent.st_ino == expected_parent["inode"] and
            stat.S_ISDIR(named_root.st_mode) and
            named_root.st_dev == opened_root.st_dev and
            named_root.st_ino == opened_root.st_ino
        )
    except (Rejected, OSError, RuntimeError) as error:
        raise PathIdentityMismatch(
            "Approved output path could not be rebound to its open directory"
        ) from error
    if not valid:
        raise PathIdentityMismatch(
            "Approved output path no longer names the bound evidence directory")


def _request_from_approval(approved: dict) -> dict:
    return {key: approved[key] for key in (
        "workspace", "historicalRoots", "evidenceParent",
        "oneuseName", "unity", "sourcePins")}


def _same_admission(before: dict, after: dict) -> None:
    """Compare stable physical/source facts, not free disk byte fluctuations."""
    for key in ("sourcePins", "source", "originalS", "workspace",
                "candidate", "historicalRootCount", "historicalRoots",
                "custodyIdentity"):
        need(after.get(key) == before.get(key),
             "D5-B custody or source changed: " + key)
    for key in ("unityExecutable", "unitySha256", "platform",
                "architecture", "xcodeVersionOutput", "macosSdkPath",
                "macosClangPath", "xcodeLicenseChecked"):
        need(after["host"].get(key) == before["host"].get(key),
             "Unity or macOS toolchain identity drifted: " + key)


def _read_locked(root_fd: int, name: str) -> bytes:
    need(re.fullmatch(r"[A-Z_]+\.json", name) is not None,
         "Fixed dry-receipt filename required")
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=root_fd)
    with os.fdopen(fd, "rb") as stream:
        return stream.read()


def _committed_receipt_structure(root_fd: int) -> dict:
    """Physical receipt evidence only. Never an approval or real Unity PASS.

    INCOMPLETE.json is a durable veto: its presence makes any complete-
    looking final receipt invalid, even if its hash matches MANIFEST.json.
    """
    ledger = _locked_file_ledger(root_fd)
    actual = {entry["path"]: entry for entry in ledger}
    required = {
        "ADMISSION.json", "CELLS.json", "POSTFLIGHT.json",
        "MANIFEST.json", "LOCAL_BATCH_RESULT.json",
    }
    need(set(actual) == required,
         "Dry receipt unsealed, incomplete, failed or contains extra files")
    manifest = parse_json(_read_locked(root_fd, "MANIFEST.json"))
    need(manifest.get("schemaVersion") == 1 and
         manifest.get("kind") == "R03D5BDryAdmissionLedgerV3" and
         manifest.get("finalReceiptIsExclusiveAndLast") is True and
         manifest.get("realPlayerEvidence") is False and
         manifest.get("R03Accepted") is False,
         "Wrong final dry-admission seal schema")
    files = manifest.get("files")
    need(type(files) is list and len(files) == 4 and
         all(type(x) is dict for x in files),
         "Unreviewed final dry-admission receipt roster")
    for item in files:
        name = item.get("path")
        need(name in required - {"MANIFEST.json"} and
             type(item.get("sha256")) is str and
             len(item["sha256"]) == 64 and
             type(item.get("bytes")) is int and
             name in actual and
             actual[name]["sha256"] == item["sha256"] and
             actual[name]["bytes"] == item["bytes"],
             "Dry-admission receipt hash, size or identity mismatch")
    need({x["path"] for x in files} == required - {"MANIFEST.json"},
         "Duplicate or missing sealed dry receipt entry")
    final = parse_json(_read_locked(root_fd, "LOCAL_BATCH_RESULT.json"))
    need(final.get("schemaVersion") == 1 and
         final.get("kind") == "R03D5BDryAdmissionReceiptV1" and
         final.get("result") == "DryAdmissionRecorded_NoUnityOrPlayer" and
         final.get("realUnityBuild") == "NotRun" and
         final.get("realPlayerCellsPassed") == 0 and
         final.get("realPlayerCellsNoCoverage") == 18 and
         final.get("R03Accepted") is False,
         "Final dry receipt cannot assert real Player or R03 acceptance")
    return {"result": "SealedDryReceiptStructureOnly_NotLocalAuthorization",
            "filesChecked": len(required),
            "manifestSha256": actual["MANIFEST.json"]["sha256"],
            "realPlayerCellsPassed": 0,
            "realPlayerCellsNoCoverage": 18,
            "R03Accepted": False}


def inspect_dry_receipt_structure(root: Path) -> dict:
    """Read-only structural verification, not an approved Local workflow."""
    canonical_dir(root, "sealed dry-admission candidate")
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        return _committed_receipt_structure(fd)
    finally:
        os.close(fd)


def seal_oneuse_dry_admission(approved_raw: bytes,
                              admission: dict) -> dict:
    """Future dry-only one-use writer; production approval is still None.

    The one-use product is NOT complete while INCOMPLETE.json exists. All
    preparatory files and the success-file staging bytes are fsynced before
    the atomic final rename. After the rename, fsync the directory while
    the durable incomplete marker still vetoes acceptance. The last
    visibility change is removing INCOMPLETE.json; if power fails before
    that unlink persists, the marker reappears and fails closed.
    """
    approved = approved_envelope(approved_raw)
    request = _request_from_approval(approved)
    need(type(admission) is dict and
         admission.get("result") ==
            "ReadOnlyLocalAdmissionInspected_ExecutionStillUnauthorized",
         "Actual previously inspected D5-B admission required")
    observed = inspect(request)
    _same_admission(admission, observed)
    result = oneuse_receipt(approved, observed)
    root = Path(observed["candidate"])
    parent = root.parent
    expected_parent = observed["custodyIdentity"]["parent"]
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    parent_fd = os.open(parent, flags)
    root_fd = None
    root_created = False
    committed = False
    final_unlink_attempted = False
    problem = None
    cleanup_errors = []
    ledger = []
    try:
        pstat = os.fstat(parent_fd)
        need(pstat.st_dev == expected_parent["device"] and
             pstat.st_ino == expected_parent["inode"] and
             directory_identity(parent) == expected_parent and
             not root.exists() and not root.is_symlink(),
             "D5-B output parent replaced or candidate consumed")
        os.mkdir(root.name, 0o700, dir_fd=parent_fd)
        root_created = True
        root_fd = os.open(root.name, flags, dir_fd=parent_fd)
        _assert_open_path(parent_fd, root_fd, root, expected_parent)
        _write_locked(root_fd, "INCOMPLETE.json", {
            "schemaVersion": 1,
            "kind": "R03D5BUncommittedDryAdmissionV1",
            "result": "NotCommitted", "retryAllowed": False,
            "R03Accepted": False})
        # Durably install the veto before generating any positive receipt.
        os.fsync(root_fd)
        _write_locked(root_fd, "ADMISSION.json", {
            "sourceAndHost": observed,
            "approvalEnvelopeGitBlob": git_blob(approved_raw),
            "result": "ReadOnlyAdmissionBeforeAnyBuild",
            "R03Accepted": False})
        _write_locked(root_fd, "CELLS.json", {
            "kind": "R03D5BInitialNoCoverageCellsV1",
            "cells": [
                {"id": "D5-C%02d" % i, "result": "NoCoverage",
                 "evidenceClass": "NotRun",
                 "reason": "No Unity/IL2CPP Player or case producer executed"}
                for i in range(1, 19)],
            "D5LocalValidation": "NotAuthorized"})
        postflight = inspect(request, expect_output_present=True)
        _same_admission(observed, postflight)
        _assert_open_path(parent_fd, root_fd, root, expected_parent)
        _write_locked(root_fd, "POSTFLIGHT.json", {
            "result": "ReadOnlyPostflightPassed_NotUnityValidation",
            "sourcePins": observed["sourcePins"],
            "candidate": str(root),
            "remoteHeads": postflight["source"]["remoteHeads"],
            "historicalRootCount": 6, "R03Accepted": False})
        _assert_open_path(parent_fd, root_fd, root, expected_parent)
        final_check = inspect(request, expect_output_present=True)
        _same_admission(observed, final_check)
        _assert_open_path(parent_fd, root_fd, root, expected_parent)
        existing = _locked_file_ledger(root_fd)
        need({entry["path"] for entry in existing} == {
             "INCOMPLETE.json", "ADMISSION.json", "CELLS.json",
             "POSTFLIGHT.json"}, "Unexpected precommit material")
        final_bytes = _json_bytes(result)
        files = [entry for entry in existing if entry["path"] != "INCOMPLETE.json"]
        files.append({"path": "LOCAL_BATCH_RESULT.json",
                      "sha256": hashlib.sha256(final_bytes).hexdigest(),
                      "bytes": len(final_bytes),
                      "expectedOnlyUntilAtomicCommit": True})
        _write_locked(root_fd, "MANIFEST.json", {
            "schemaVersion": 1,
            "kind": "R03D5BDryAdmissionLedgerV3",
            "files": files, "realPlayerEvidence": False,
            "R03Accepted": False, "finalReceiptIsExclusiveAndLast": True,
            "commitProtocol": "DurableIncompleteVeto_AtomicFinalRename"})
        _assert_open_path(parent_fd, root_fd, root, expected_parent)
        final_source = inspect(request, expect_output_present=True)
        _same_admission(observed, final_source)
        _assert_open_path(parent_fd, root_fd, root, expected_parent)

        # The only writer of positive bytes creates a non-accepting staging
        # filename. An fsync/close failure here cannot leave a final marker.
        _write_locked(root_fd, "LOCAL_BATCH_STAGING.json", result)
        staging = _read_locked(root_fd, "LOCAL_BATCH_STAGING.json")
        need(staging == final_bytes and
             hashlib.sha256(staging).hexdigest() == files[-1]["sha256"],
             "Staged final dry receipt does not match the reviewed bytes")
        # All preliminary writes and the stage become directory-durable.
        os.fsync(root_fd)
        _assert_open_path(parent_fd, root_fd, root, expected_parent)
        final_source = inspect(request, expect_output_present=True)
        _same_admission(observed, final_source)
        _assert_open_path(parent_fd, root_fd, root, expected_parent)

        # Finish all other descriptor closes BEFORE the final commit.
        closing_parent = parent_fd
        parent_fd = None  # Never double-close after an error.
        os.close(closing_parent)

        # Recheck the original path after closing the parent descriptor.
        # Descriptor-relative writes alone do not prove the approved pathname
        # still names this directory if another process moved the child.
        _assert_final_path_identity(root_fd, root, expected_parent)
        os.rename("LOCAL_BATCH_STAGING.json", "LOCAL_BATCH_RESULT.json",
                  src_dir_fd=root_fd, dst_dir_fd=root_fd)
        os.fsync(root_fd)
        _assert_final_path_identity(root_fd, root, expected_parent)

        # Unlink is the LAST visibility-changing operation. An error after
        # the unlink may mean it took effect; never claim a definite
        # precommit failure or attempt to write a FAILURE marker afterward.
        final_unlink_attempted = True
        os.unlink("INCOMPLETE.json", dir_fd=root_fd)
        committed = True
        # Read-only custody check after publication: any path drift must
        # become IndeterminateAfterCommit, not a success at the wrong path.
        _assert_final_path_identity(root_fd, root, expected_parent)
    except BaseException as error:
        problem = error

    # Cleanup is deliberately part of the same root-created accounting,
    # not a finally block that could override PartialOutput or claim no root.
    if (problem is not None and root_created and not committed
            and not final_unlink_attempted):
        try:
            if root_fd is not None:
                ledger = _locked_file_ledger(root_fd)
                if not any(x["path"] == "FAILURE.json" for x in ledger):
                    try:
                        _write_locked(root_fd, "FAILURE.json", {
                            "schemaVersion": 1,
                            "kind": "R03D5BPartialOutputFailureV1",
                            "result": "FailedAfterPartialOutput",
                            "candidate": str(root), "reason": repr(problem),
                            "observedFiles": ledger, "R03Accepted": False,
                            "retryAllowed": False})
                        ledger = _locked_file_ledger(root_fd)
                    except BaseException:
                        # Disk exhaustion may make the failure marker
                        # unavailable; the durable veto still rejects it.
                        pass
        except BaseException:
            pass
    if root_fd is not None:
        try:
            os.close(root_fd)
        except BaseException as error:
            cleanup_errors.append("rootFd: " + repr(error))
    if parent_fd is not None:
        try:
            os.close(parent_fd)
        except BaseException as error:
            cleanup_errors.append("parentFd: " + repr(error))
    if problem is not None or cleanup_errors:
        explanation = "; ".join(
            [repr(problem)] if problem is not None else [])
        if cleanup_errors:
            explanation += ("; " if explanation else "") + "; ".join(cleanup_errors)
        if root_created:
            # After the final veto unlink, close errors are indeterminate
            # cleanup outcomes, not evidence that the committed bytes failed.
            raise PartialOutput(root, explanation, ledger,
                                commit_visible=committed,
                                commit_uncertain=(final_unlink_attempted
                                                  and not committed),
                                path_identity_uncertain=isinstance(
                                    problem, PathIdentityMismatch),
                                cleanup_errors=tuple(cleanup_errors))
        raise Rejected(explanation) from problem
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
            approved_raw = args.approved_envelope.read_bytes()
            approved = approved_envelope(approved_raw)
            request = {
                "workspace": approved["workspace"],
                "historicalRoots": approved["historicalRoots"],
                "evidenceParent": approved["evidenceParent"],
                "oneuseName": approved["oneuseName"],
                "unity": approved["unity"],
                "sourcePins": approved["sourcePins"],
            }
            observation = inspect(request)
            result = seal_oneuse_dry_admission(approved_raw, observation)
        else:
            need(args.approved_envelope is None,
                 "Read-only preview must not accept approval-like inputs")
            need(args.request is not None and args.request.is_file() and
                 not args.request.is_symlink(),
                 "Read-only preview requires one external JSON request")
            result = inspect(parse_json(args.request.read_bytes()))
        print(json.dumps(result, sort_keys=True, allow_nan=False))
        return 0
    except PartialOutput as exc:
        print(json.dumps({
            "schemaVersion": 1,
            "kind": "R03D5BLocalAdmissionFailureV1",
            "result": ("IndeterminateAfterCommit"
                       if exc.commit_visible or exc.commit_uncertain
                       else "FailedAfterPartialOutput"),
            "reason": str(exc),
            "candidate": str(exc.root),
            "observedFiles": list(exc.files),
            "observedLedger": list(exc.ledger),
            "failureMarkerAvailable": "FAILURE.json" in exc.files,
            "commitVisible": exc.commit_visible,
            "commitOutcome": ("Visible" if exc.commit_visible else
                              "UnknownAfterFinalUnlink" if exc.commit_uncertain
                              else "NotCommitted"),
            "finalUnlinkOutcomeUncertain": exc.commit_uncertain,
            "outputPathIdentityUncertain": exc.path_identity_uncertain,
            "cleanupErrors": list(exc.cleanup_errors),
            "requiresPhysicalReconciliation": (
                exc.commit_visible or exc.commit_uncertain or
                exc.path_identity_uncertain or bool(exc.cleanup_errors)),
            "outputCreated": True,
            "retryAllowed": False,
            "WEB_TO_LOCAL": "CLOSED_NO_LOCAL_EXECUTION",
            "D5BLocalExecution": "NotAuthorized",
            "R03Accepted": False,
        }, sort_keys=True))
        return 2
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
