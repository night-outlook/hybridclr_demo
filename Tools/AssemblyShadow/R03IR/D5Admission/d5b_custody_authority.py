#!/usr/bin/env python3
"""R03 D5-B Primary preparation: source/remote and one-use evidence custody.

READ ONLY. Does not run Unity/IL2CPP, admit a Local batch, make directories,
create an executable handoff, or accept a self-asserted approval flag.
The future Local gate must use a NEW independently reviewed approved envelope.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Mapping

BRANCH = "codex/assembly-shadow-r01b-h1"
PREP_FILE = Path(__file__).resolve().with_name("d5b_preparation_v1.json")
PREP_BLOB = "TO_BE_BOUND_TO_REMOTE_GIT_BLOB"
PINNED = {
    "hybridclr": "c3c232023724cbad565b85e9b2c3beea8ce2789a",
    "hybridclr_unity": "948c0e3b4f8891481301770115e8ba4945eea6de",
    "il2cpp_plus": "3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699",
}
ROLES = ("hybridclr_demo", "hybridclr", "hybridclr_unity", "il2cpp_plus")
HISTORY = (
    "originalS", "b1EvidenceBase", "b1Oneuse12",
    "b1NativeHostRaw", "b1B2HostRaw", "b1Preflight",
)
NATIVE = (
    "libil2cpp/utils/dynamic_array.h",
    "libil2cpp/vm/Assembly.cpp",
    "libil2cpp/vm/AssemblyShadow.cpp",
    "libil2cpp/vm/AssemblyShadow.h",
    "libil2cpp/vm/AssemblyShadowFirstFailureV2.h",
    "libil2cpp/vm/AssemblyShadowProcessSnapshotOwner.h",
    "libil2cpp/vm/AssemblyShadowPublicationD3Decision.h",
    "libil2cpp/vm/AssemblyShadowPublicationPhaseReceipt.h",
    "libil2cpp/vm/AssemblyShadowTerminalExecution.h",
    "libil2cpp/vm/AssemblyShadowTypes.h",
    "libil2cpp/vm/MetadataCache.cpp",
    "libil2cpp/vm/Runtime.cpp",
)
TRANSLATION_UNITS = (
    "libil2cpp/vm/AssemblyShadow.cpp",
    "libil2cpp/vm/Assembly.cpp",
    "libil2cpp/vm/MetadataCache.cpp",
    "libil2cpp/vm/Runtime.cpp",
)
BAD_HOST = "NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
NAME = re.compile(r"^R03-B2-D5-[A-Za-z0-9][A-Za-z0-9-]{5,63}$")


class Rejected(ValueError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise Rejected(message)


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") +
                        b"\0" + data).hexdigest()


def strict_object(items) -> dict:
    result = {}
    for k,v in items:
        require(k not in result, "Duplicate JSON key: " + k)
        result[k] = v
    return result


def read_json(raw: bytes) -> dict:
    obj = json.loads(raw, object_pairs_hook=strict_object)
    require(type(obj) is dict, "Expected JSON object")
    return obj


def require_proposal(obj: dict) -> dict:
    require(obj.get("schemaVersion") == 1 and
            obj.get("kind") == "R03B2D5BSourceCustodyPreparationV1" and
            obj.get("branch") == BRANCH, "Wrong D5-B preparation schema/branch")
    s = obj.get("sourceAuthority")
    require(type(s) is dict and
            s.get("d5AIndependentReview") == "PassD5AForD5BPreparation" and
            s.get("demoReviewedBaseline") ==
                "b9776f7dc87170ba08bfed9021c0ee8546bceccf" and
            all(s.get(k) == v for k,v in PINNED.items()) and
            s.get("sourceCommitPolicy") ==
                "reviewedImmutableTuplePlusExactRemoteBranchReadback_NotCallerSuppliedLatest" and
            s.get("demoBaselineRole") ==
                "ReviewBootstrapOnly_NotFutureLocalHandoff",
            "Proposal source tuple or immutable authority role changed")
    require(obj.get("historicalRootRoles") == list(HISTORY),
            "Historical root list must not be optional or incomplete")
    require(obj.get("requiredNativeInputs") == list(NATIVE) and
            obj.get("forbiddenNativeInputs") == [BAD_HOST] and
            obj.get("requiredCompiledTranslationUnits") == list(TRANSLATION_UNITS),
            "Native source-input and host allocator identity changed")
    require(obj.get("expectedLocalTarget") == {
        "unity":"2022.3.62f2", "os":"macOS", "architecture":"arm64",
        "scriptingBackend":"IL2CPP", "featureOnRelease":True,
        "featureOffRelease":True}, "Preview platform changed")
    handoff = obj.get("reviewedHandoff")
    require(handoff == {
        "status":"NotCreated", "expectedGitBlob":None,
        "approvedCommitTuple":None, "remoteAtReview":None,
        "version":"D5B-ExecutionApprovalV1",
        "userLocalApproval":"NotAuthorized"}, "Local approval/handoff falsely issued")
    require(obj.get("evidenceRoot") == {
        "status":"ProposalOnly", "requireAbsent":True,
        "requireCanonical":True, "requireNonSymlinkAncestors":True,
        "requireAllHistoricalRoles":True,
        "requireOutsideFullWorkspace":True, "createOrReserve":False},
        "Evidence-root admission cannot be relaxed in proposal")
    require(obj.get("testCoverage") == {
        "D5PlayerCases":18,"D5PlayerCasesCompleted":0,
        "D5PlayerCasesNoCoverage":18,
        "nativeBuildAndLink":"NotRun",
        "historicalS":"ComparatorOnly",
        "realConcurrency":"NotRun",
        "fullNativeInstall":"NotRun"}, "Unperformed Player tests misclassified")
    require(obj.get("authority") == {
        "D5BPreparation":"PrimaryScoped",
        "D5BLocalExecution":"NotAuthorized",
        "WEB_TO_LOCAL":"CLOSED_NO_LOCAL_EXECUTION",
        "R03Accepted":False,"H2Passed":False,
        "ReadyForHumanReviewGate":False,"allowUnityOrPlayer":False},
        "D5-B approval must be explicit and separate")
    require(obj.get("mode") == "sourceOnly_NotAPlayerOrLocalExecutionGate",
            "D5-B preparation must stay source-only")
    return obj


def checked_directory(path: Path, label: str) -> Path:
    require(isinstance(path, Path) and path.is_absolute() and
            ".." not in path.parts and path.is_dir() and
            not path.is_symlink() and path.resolve(strict=True) == path,
            "Physically canonical non-symlink directory required: " + label)
    return path


def separate(a: Path, b: Path) -> bool:
    return a != b and a not in b.parents and b not in a.parents


def check_proposed_custody(
        workspace: Path,
        roots: Mapping[str, Path],
        historical_roots: Mapping[str, Path],
        evidence_parent: Path,
        oneuse_name: str,
) -> dict:
    """Pure path inspection; mandatory complete history map and no mkdir/open."""
    workspace = checked_directory(workspace, "entire four-repo workspace")
    require(set(roots) == set(ROLES), "Exactly four checkout root roles required")
    require(set(historical_roots) == set(HISTORY),
            "All six reviewed historical-root roles are MANDATORY")
    for name, path in roots.items():
        checked_directory(path, "repository:" + name)
        require(path.parent == workspace, "Four Git roots must be workspace siblings")
    require(len(set(roots.values())) == 4, "Duplicate source checkout identity")
    for name, path in historical_roots.items():
        checked_directory(path, "historical:" + name)
    historical_base = historical_roots["b1EvidenceBase"]
    for role in ("b1Oneuse12","b1NativeHostRaw","b1B2HostRaw","b1Preflight"):
        p = historical_roots[role]
        require(p != historical_base and historical_base in p.parents,
                "Historical B1 evidence roles must belong to the B1 evidence base")
    checked_directory(evidence_parent, "new evidence parent")
    require(type(oneuse_name) is str and NAME.fullmatch(oneuse_name),
            "New evidence root name must have a unique D5 one-use ID")
    candidate = evidence_parent / oneuse_name
    require(not candidate.exists() and not candidate.is_symlink() and
            candidate.resolve(strict=False) == candidate,
            "New D5 output must be ABSENT and canonical")
    # Explicitly exclude the full workspace AND each historical source/evidence
    # subtree (including a new child of an old evidence root).
    protected = [workspace, *roots.values(), *historical_roots.values()]
    require(all(separate(evidence_parent, p) for p in protected) and
            all(separate(candidate, p) for p in protected),
            "Evidence parent or new output overlaps a protected historical/source root")
    require(historical_roots["originalS"] != workspace,
            "Original S checkout is distinct from the source workspace root")
    return {
        "result":"PreparedReadOnlyCustody_NotLocalAuthorization",
        "candidate":str(candidate),"historicalRootCount":len(historical_roots),
        "sourceRootCount":len(roots),
        "outputExists":False,"outputCreated":False,
        "UnityOrPlayerExecuted":False,"D5BLocalExecution":"NotAuthorized",
        "WEB_TO_LOCAL":"CLOSED_NO_LOCAL_EXECUTION",
    }


def parse_remote_ref(stdout: str, expected_sha: str, branch: str = BRANCH) -> str:
    require(type(expected_sha) is str and SHA40.fullmatch(expected_sha),
            "Expected immutable reviewed SHA required")
    ref = "refs/heads/" + branch
    rows = stdout.splitlines()
    require(len(rows) == 1 and "\t" in rows[0],
            "Require exactly one remote branch ref, not an ambiguous list")
    sha, observed = rows[0].split("\t", 1)
    require(observed == ref and SHA40.fullmatch(sha) and sha == expected_sha,
            "Remote branch HEAD does not equal separately reviewed source pin")
    return sha


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git","-C",str(root),*args],
        capture_output=True, text=True, timeout=45, check=False)
    require(result.returncode == 0,
            "Git source/remote query failed: " + " ".join(args) +
            ": " + result.stderr[-240:])
    return result.stdout.strip()


def canonical_remote(url: str, role: str) -> bool:
    require(role in ROLES, "Unknown source role")
    name = "night-outlook/" + role
    return url in (
        "https://github.com/" + name, "https://github.com/" + name + ".git",
        "git@github.com:" + name, "git@github.com:" + name + ".git",
        "ssh://git@github.com/" + name,
        "ssh://git@github.com/" + name + ".git",
    )


def verify_live_source_heads(
        roots: Mapping[str, Path],
        independent_reviewed_pins: Mapping[str, str],
) -> dict:
    """Remote readback is required, but this function NEVER grants Local rights.

    The pins must come from an independently reviewed immutable handoff record.
    Current *preparation* metadata does not supply such a record; callers may
    use this primitive in synthetic tests, not for D5-B execution.
    """
    require(set(roots) == set(ROLES) and
            set(independent_reviewed_pins) == set(ROLES),
            "Four independent approved pins and roots required")
    result = {}
    for role in ROLES:
        root = checked_directory(roots[role], role)
        reviewed = independent_reviewed_pins[role]
        require(type(reviewed) is str and SHA40.fullmatch(reviewed),
                "Independently reviewed full SHA required for " + role)
        require(role == "hybridclr_demo" or reviewed == PINNED[role],
                "Unreviewed native/HybridCLR source transition forbidden")
        require(run_git(root,"rev-parse","--show-toplevel") == str(root),
                "Exact Git root check failed for " + role)
        require(run_git(root,"rev-parse","HEAD") == reviewed,
                "Local HEAD is not the independently reviewed commit")
        url = run_git(root,"remote","get-url","origin")
        require(canonical_remote(url,role),
                "Noncanonical origin for " + role)
        require(not run_git(root,"status","--porcelain=v1",
                            "--untracked-files=all"),
                "Dirty source tree " + role)
        remote_head = run_git(
            root, "ls-remote", "--exit-code", "origin",
            "refs/heads/" + BRANCH)
        parse_remote_ref(remote_head,reviewed)
        result[role] = {
            "repository":"night-outlook/"+role,
            "reviewedCommit":reviewed,"remoteBranchMatched":True,
            "localHeadMatched":True,"sourceClean":True,
        }
    return result


def check_native_file_copy(
        original: Path, proposed_installed: Path,
        expected_blobs: Mapping[str, str],
) -> dict:
    """Authenticate bytes in an *uncompiled file-copy fixture*, never Bee/link."""
    checked_directory(original, "reviewed native source")
    checked_directory(proposed_installed,"synthetic install fixture")
    require(set(expected_blobs)==set(NATIVE),
            "All 12 reviewed native files must be accounted for")
    copy_hashes={}
    for name in NATIVE:
        ref=original/name
        dst=proposed_installed/name
        require(ref.is_file() and dst.is_file() and
                not ref.is_symlink() and not dst.is_symlink(),
                "Source or copy missing/symlinked: "+name)
        a,b=ref.read_bytes(),dst.read_bytes()
        require(git_blob(a)==expected_blobs[name] and a==b,
                "Synthetic native source copy did not preserve exact reviewed bytes: "+name)
        copy_hashes[name]=hashlib.sha256(b).hexdigest()
    require(not (proposed_installed/BAD_HOST).exists(),
            "Standalone global allocator host driver entered native copy")
    return {"result":"SyntheticNativeFileCopyOnly_NotUnityInstalled",
            "nativeFilesAuthenticated":len(copy_hashes),
            "nativeSourceSha256":copy_hashes,
            "actualBeeCompilerInvoked":False,"compiledTranslationUnits":0,
            "actualPlayerLinked":False,
            "WEB_TO_LOCAL":"CLOSED_NO_LOCAL_EXECUTION"}


def preview(path: Path) -> dict:
    require(path == PREP_FILE and path.is_file() and not path.is_symlink(),
            "Only the versioned D5-B source-preparation manifest may be inspected")
    raw=path.read_bytes()
    require(git_blob(raw)==PREP_BLOB,
            "D5-B preparation manifest Git identity drifted")
    obj=require_proposal(read_json(raw))
    return {"schema":"R03B2D5BPreparationV1",
            "result":"PreparedSourceOnly_NoLocalExecution",
            "remoteSourceVerification":"NotRun",
            "historicalRootAdmission":"NotRun",
            "nativeUnityInstallation":"NotRun",
            "realPlayerCellsPassed":0,
            "realPlayerCellsNoCoverage":obj["testCoverage"]["D5PlayerCasesNoCoverage"],
            "D5BLocalExecution":"NotAuthorized",
            "WEB_TO_LOCAL":"CLOSED_NO_LOCAL_EXECUTION",
            "R03Accepted":False,"H2Passed":False,
            "ReadyForHumanReviewGate":False}


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-preview-only",action="store_true",required=True)
    a=p.parse_args()
    try:
        if a.source_preview_only:
            print(json.dumps(preview(PREP_FILE),sort_keys=True))
            return 0
    except (Rejected,OSError,ValueError,subprocess.SubprocessError) as error:
        print(json.dumps({"result":"D5BSourcePreparationBlocked",
                          "reason":str(error),
                          "D5BLocalExecution":"NotAuthorized",
                          "WEB_TO_LOCAL":"CLOSED_NO_LOCAL_EXECUTION",
                          "UnityOrPlayerExecuted":False},sort_keys=True),file=sys.stderr)
        return 2
    return 2


if __name__=="__main__":
    raise SystemExit(main())
