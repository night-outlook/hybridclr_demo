#!/usr/bin/env python3
"""RR5 D5-B read-only source preflight. NEVER an executable Local handoff.

This verifies *Git source bytes and an exact proposed roster*, not Unity
installation, native translation units, Bee objects, or Player evidence.
Legacy D5-A/B and B1 contracts remain immutable comparison-only inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

BRANCH = "codex/assembly-shadow-r01b-h1"
ROOT = Path(__file__).resolve().parent
PROFILE = ROOT / "d5b_rr5_source_preflight_v1.json"
PROFILE_BLOB = "9956ea49656dc8337f9ab177c40faf29ea20c397"
MANIFEST_BLOB = "66b2e83f8cab4debb71af36d4bcd5eecd80b5629"
REVIEWED_DEMO_CODE = "a8f9cb31cd51aed97a65d84e555ec7f4d3f2e328"
PINS = {
    "hybridclr": "c3c232023724cbad565b85e9b2c3beea8ce2789a",
    "hybridclr_unity": "948c0e3b4f8891481301770115e8ba4945eea6de",
    "il2cpp_plus": "1268dd417ffe9090fcd9ea2d49542c97ed3cccb3",
}
ROLES = ("hybridclr_demo", "hybridclr", "hybridclr_unity", "il2cpp_plus")
SHA40 = re.compile(r"^[a-f0-9]{40}$")
TUS = ("vm/Assembly.cpp", "vm/AssemblyShadow.cpp", "vm/MetadataCache.cpp",
       "vm/Runtime.cpp", "vm/AssemblyShadowD5WindowOverlay.cpp")
EXPORTS = ("R03_D5_WindowProtocolVersion", "R03_D5_ArmP5Window",
           "R03_D5_ReleaseP5Window", "R03_D5_ReadP5Window",
           "R03_D5_ReceiptOpen", "R03_D5_ReceiptEvent",
           "R03_D5_BindKeepCanary", "R03_D5_ReceiptSeal",
           "R03_D5_BeginKeepAttempt")
EVIDENCE_PRODUCER_BLOBS = {
    ".github/workflows/r03-b2-d5-c10-window-source-host.yml": "f565018f908c43892ebfc00816088797310349aa",
    "Tools/AssemblyShadow/R03IR/D5Probe/d5_c10_native_receipt.py": "44094a2e6ddc5a16238d287c956eb483995dd847",
    "Tools/AssemblyShadow/R03IR/D5Probe/d5_link_materials.py": "7ac9195191b00cf5f8930282381f7b324be99891",
    "Tools/AssemblyShadow/R03IR/D5Probe/d5_window_source_contract.py": "c00ed0d81b343cb375f7105e1aafe4e09647dfe1",
    "Tools/AssemblyShadow/R03IR/D5Probe/D5AutoReceiptHost.cpp": "f0bdc640183cb0311e81d49255e74a30e1dff43e",
    "Tools/AssemblyShadow/R03IR/D5Probe/d5c10_link_source_pinset_v1.json": "66b2e83f8cab4debb71af36d4bcd5eecd80b5629",
    "Tools/AssemblyShadow/R03IR/D5Probe/D5NativeReceiptHost.cpp": "a710dd5243cd868ae3d5debcddf2caa1c27da661",
    "Tools/AssemblyShadow/R03IR/D5Probe/D5WindowFeatureOffHost.cpp": "8f8d7235329e2132aee5b746024daa3c9a42afe5",
    "Tools/AssemblyShadow/R03IR/D5Probe/D5WindowOtherTU.cpp": "16de160427dd7fcd6566492229621aac0551bcdb",
    "Tools/AssemblyShadow/R03IR/D5Probe/D5WindowSourceHost.cpp": "abb273264851ecdda1f756e257898e970d5ea56d",
    "Tools/AssemblyShadow/R03IR/D5Probe/NativeHostStubs/il2cpp-config.h": "1d078cf09fcc6a33182ce1fdfc8a88e778e766eb",
    "Tools/AssemblyShadow/R03IR/D5Probe/test_d5_c10_native_receipt.py": "9323650c60e693a3faafdf75f250cc2fdc185189",
    "Tools/AssemblyShadow/R03IR/D5Probe/test_d5_link_materials.py": "a09596892620a86c4b34f5e04bc6f61f61ab5121",
    "Tools/AssemblyShadow/R03IR/D5Probe/test_d5_window_source_contract.py": "f874e31a1e751d2d8427b3bdefb093458601014e"
}

OLD_B1 = {
    "Tools/AssemblyShadow/R03IR/current_native_candidate.json":
        "efc4f7fa45fad394f156ed8d115bad727771c8a6",
    "Tools/AssemblyShadow/R03IR/current_native_source_gate.py":
        "92aaa6f523eee026a83223595147f5a79882a12f",
    "Tools/AssemblyShadow/R03IR/run_current_native_validation_cycle.py":
        "80100158732267ff36e37b0fa5c3b2d5bbe96d56",
}
HIST = {
    "Tools/AssemblyShadow/R03IR/D5Admission/d5a_candidate_v1.json":
        "e15bdbff02de2dbb7adef42c39f363fe2d1f3b37",
    "Tools/AssemblyShadow/R03IR/D5Admission/d5b_preparation_v1.json":
        "202c7847e4ae741902162391a4e4bd7a66e33c2c",
    **OLD_B1,
}
HISTORY_ROLES = ("originalS", "b1EvidenceBase", "b1Oneuse12",
                 "b1NativeHostRaw", "b1B2HostRaw", "b1Preflight")


class Rejected(ValueError):
    """Expected fail-closed source-preflight outcome."""


def require(ok: bool, detail: str) -> None:
    if not ok:
        raise Rejected(detail)


def git_blob(data: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def strict_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def read_object(data: bytes) -> dict:
    obj = json.loads(data, object_pairs_hook=strict_pairs)
    require(type(obj) is dict, "Expected JSON object")
    return obj


def checked_profile(raw: bytes, *, check_blob: bool = True) -> dict:
    if check_blob:
        require(git_blob(raw) == PROFILE_BLOB,
                "Unreviewed RR5 proposal bytes")
    p = read_object(raw)
    require(p.get("schemaVersion") == 1 and
            p.get("kind") == "R03B2D5BRR5SourcePreflightV1" and
            p.get("branch") == BRANCH, "Wrong RR5 proposal schema/branch")
    reviewed = p.get("reviewed")
    require(type(reviewed) is dict and reviewed == {
        "d5a": "PassD5AForD5BPreparation",
        "c10": "PassSourceProducerOnly",
        "hybridclr_demo_reviewed_code": REVIEWED_DEMO_CODE,
        **PINS,
        "demoExecutionPolicy":
            "ExactCurrentBranchHeadPlusReviewedC10SourceBlobs",
    }, "RR5 source review and exact tuple changed")
    manifests = p.get("exactSourceManifests")
    require(type(manifests) is dict and manifests == {
        "c10Path":
            "Tools/AssemblyShadow/R03IR/D5Probe/d5c10_link_source_pinset_v1.json",
        "c10GitBlob": MANIFEST_BLOB,
        "nativeSources": 13, "isolatedDemoSources": 3,
        "d5aHistoricalPath":
            "Tools/AssemblyShadow/R03IR/D5Admission/d5a_candidate_v1.json",
        "d5aHistoricalGitBlob":
            HIST["Tools/AssemblyShadow/R03IR/D5Admission/d5a_candidate_v1.json"],
        "d5bHistoricalPath":
            "Tools/AssemblyShadow/R03IR/D5Admission/d5b_preparation_v1.json",
        "d5bHistoricalGitBlob":
            HIST["Tools/AssemblyShadow/R03IR/D5Admission/d5b_preparation_v1.json"],
        "b1HistoricalPath":
            "Tools/AssemblyShadow/R03IR/current_native_candidate.json",
        "b1HistoricalGitBlob":
            OLD_B1["Tools/AssemblyShadow/R03IR/current_native_candidate.json"],
    }, "Previously reviewed D5/B1 source identities changed")
    roster = p.get("nativeSourceRoster")
    require(type(roster) is dict and
            roster.get("translationUnits") == list(TUS) and
            roster.get("cExports") == list(EXPORTS) and
            roster.get("forbiddenNativeInputs") == [
                "NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp"
            ] and roster.get("compiledTranslationUnitsObserved") == 0 and
            roster.get("linkedBinaryObserved") is False,
            "Unreviewed build roster or false compilation evidence")
    require(p.get("historicalBaseline") == {
        "originalS": "fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b",
        "b1NativePin": "8aa8d09319a89b55b2496bcc2c69ccc69cb57be9",
        "d5aNativePin": "3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699",
        "oldB1SourceCount": 14, "oldB1VmDeltaCount": 46,
        "historicalEvidenceAsComparatorOnly": True,
        "allowAlterLegacyAdmission": False,
    }, "Legacy B1/D5-A comparator policy changed")
    require(p.get("expectedLocalTarget") == {
        "unity": "2022.3.62f2", "platform": "macOS", "architecture": "arm64",
        "scriptingBackend": "IL2CPP", "cppMode": "Release",
        "featureOn": True, "featureOffControl": True,
        "actualTargetToolchainVerified": False,
    }, "Unreviewed platform or toolchain claim")
    require(p.get("requiredHistoricalRootRoles") == list(HISTORY_ROLES),
            "Historical evidence-root custody roles changed")
    require(p.get("evidence") == {
        "d5PlayerCells": 18, "d5PlayerPassed": 0, "d5PlayerNoCoverage": 18,
        "actualUnityBuild": "NotRun", "actualIl2CppNativeLink": "NotRun",
        "realMethodAndGc": "NotRun", "realProcessPidAndExit": "NotRun",
        "originalOneuse12": "HistoricalComparatorOnly",
    }, "Unperformed Player work reclassified")
    authority = p.get("authority")
    require(type(authority) is dict and authority == {
        "stage": "PrimaryRR5SourcePreflightOnly",
        "approvedLocalHandoffGitBlob": None,
        "d5bLocalExecution": "NotAuthorized",
        "d5LocalValidation": "NotAuthorized",
        "WEB_TO_LOCAL": "CLOSED_NO_LOCAL_EXECUTION",
        "R03Accepted": False, "H2Passed": False,
        "ReadyForHumanReviewGate": False,
        "allowUnityOrPlayerExecution": False,
    }, "RR5 preflight cannot authorize Local or Player")
    require(p.get("evidenceProducerRole") ==
            "ReviewedC10ReceiptParserTestsHostAndWorkflow_GitSourceOnly" and
            p.get("evidenceProducerSourceBlobs") == EVIDENCE_PRODUCER_BLOBS,
            "Unreviewed C10 receipt/host evidence-producer bytes or roster")
    return p


def checked_c10_manifest(raw: bytes, proposal: dict) -> dict:
    require(git_blob(raw) == MANIFEST_BLOB,
            "Reviewed C10 pinset bytes changed")
    m = read_object(raw)
    require(m.get("kind") == "R03D5C10NativeLinkSourcePinsetV1" and
            m.get("schemaVersion") == 1 and m.get("branch") == BRANCH and
            m.get("sourcePins") == {
                "hybridclr_demo":
                    "DEMO_HEAD_FROM_GITHUB_ACTIONS_AND_FUTURE_APPROVED_HANDOFF",
                **PINS,
            }, "Wrong four-source pinset")
    native = m.get("nativeInstalledSources")
    demo = m.get("isolatedOverlaySource")
    require(type(native) is dict and len(native) == 13 and
            type(demo) is dict and len(demo) == 3 and
            all(type(x) is str and SHA40.fullmatch(x) for x in
                list(native.values()) + list(demo.values())),
            "Missing/invalid source Git blobs")
    require(m.get("compiledTranslationUnits") ==
            proposal["nativeSourceRoster"]["translationUnits"] and
            m.get("expectedExportSymbols") ==
            proposal["nativeSourceRoster"]["cExports"] and
            m.get("overlayInstallDestination") == TUS[-1] and
            m.get("excludedSource") ==
            proposal["nativeSourceRoster"]["forbiddenNativeInputs"],
            "Native TU/export/test allocator source roster drift")
    require(m.get("receiptWireSchemaVersion") == 3 and
            m.get("nativeWindowProtocolVersion") == 3,
            "C10 requires receipt + protocol v3")
    require(m.get("authority") == {
        "D5BLocalExecution": "NotAuthorized",
        "WEB_TO_LOCAL": "CLOSED_NO_LOCAL_EXECUTION",
        "R03Accepted": False, "H2Passed": False,
        "ReadyForHumanReviewGate": False,
    }, "C10 source pinset asserted new authority")
    return m


def git(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args],
                       capture_output=True, text=True, timeout=45,
                       check=False)
    require(p.returncode == 0, "Git source inspection failed: " +
            " ".join(args) + ": " + p.stderr[-180:])
    return p.stdout.strip()


def canonical_origin(role: str, url: str) -> bool:
    name = "night-outlook/" + role
    return url in (
        "https://github.com/" + name, "https://github.com/" + name + ".git",
        "git@github.com:" + name, "git@github.com:" + name + ".git",
        "ssh://git@github.com/" + name,
        "ssh://git@github.com/" + name + ".git",
    )


def checked_checkout(root: Path, role: str, expected_head: str) -> None:
    require(root.is_absolute() and root.is_dir() and not root.is_symlink() and
            root.resolve(strict=True) == root,
            "Physically canonical checkout required: " + role)
    require(git(root, "rev-parse", "--show-toplevel") == str(root),
            "Wrong Git checkout root: " + role)
    require(git(root, "rev-parse", "HEAD") == expected_head,
            "Wrong Git source HEAD: " + role)
    require(canonical_origin(role, git(root, "remote", "get-url", "origin")),
            "Wrong canonical remote: " + role)
    require(git(root, "branch", "--show-current") in ("", BRANCH),
            "Unexpected branch: " + role)
    require(not git(root, "status", "--porcelain=v1", "--untracked-files=all"),
            "Dirty source tree: " + role)


def checked_source_blob(root: Path, path: str, sha: str) -> str:
    require(type(path) is str and path and
            not path.startswith("/") and "\\" not in path and
            ".." not in Path(path).parts, "Invalid relative source path")
    source = root / path
    require(source.is_file() and not source.is_symlink() and
            source.resolve(strict=True) == source and
            root in source.parents,
            "Missing/symlinked source: " + path)
    actual = git_blob(source.read_bytes())
    require(actual == sha and git(root, "rev-parse", "HEAD:" + path) == sha,
            "Unreviewed source bytes: " + path)
    return actual  # a verified byte identity, never just a loop iteration


def verified_source_blob(root: Path, path: str, sha: str) -> str:
    # A disabled/no-op verifier must never let loop counters become custody proof.
    verified = checked_source_blob(root, path, sha)
    require(verified == sha, "Source verifier did not authenticate: " + path)
    return verified


def inspect(roots: dict[str, Path], demo_head: str) -> dict:
    require(type(demo_head) is str and SHA40.fullmatch(demo_head),
            "Exact current demo HEAD is required")
    require(type(roots) is dict and set(roots) == set(ROLES) and
            len(set(roots.values())) == 4,
            "Four distinct repository roots required")
    proposal_raw = PROFILE.read_bytes()
    proposal = checked_profile(proposal_raw)
    pinset_path = proposal["exactSourceManifests"]["c10Path"]
    pinset_raw = (roots["hybridclr_demo"] / pinset_path).read_bytes()
    c10 = checked_c10_manifest(pinset_raw, proposal)
    for role in ROLES:
        checked_checkout(roots[role], role,
                         demo_head if role == "hybridclr_demo" else PINS[role])
    verified_source_blob(roots["hybridclr_demo"], pinset_path, MANIFEST_BLOB)
    count = 0
    for path, sha in c10["nativeInstalledSources"].items():
        verified_source_blob(roots["il2cpp_plus"], "libil2cpp/" + path, sha)
        count += 1
    for path, sha in c10["isolatedOverlaySource"].items():
        verified_source_blob(roots["hybridclr_demo"], path, sha)
        count += 1
    producer_count = 0
    for path, sha in EVIDENCE_PRODUCER_BLOBS.items():
        verified_source_blob(roots["hybridclr_demo"], path, sha)
        producer_count += 1
    require(producer_count == 14 and count == 16,
            "Incomplete reviewed C10 link-source/evidence-producer inventory")
    for path, sha in HIST.items():
        verified_source_blob(roots["hybridclr_demo"], path, sha)
    verified_source_blob(roots["hybridclr_demo"],
                         "Tools/AssemblyShadow/R03IR/D5Admission/" + PROFILE.name,
                         PROFILE_BLOB)
    historical_b1 = read_object(
        (roots["hybridclr_demo"] /
         "Tools/AssemblyShadow/R03IR/current_native_candidate.json").read_bytes())
    require(historical_b1.get("candidateNativePin") ==
            proposal["historicalBaseline"]["b1NativePin"] and
            historical_b1.get("hybridclrPin") ==
            "4b2774b066cfc6afd77a8c8aded6bda7ea574f55",
            "Historical B1 source tuple unexpectedly changed")
    return {
        "schema": "R03D5BRR5SourcePreflightResultV1",
        "result": "RR5PinnedGitSourceVerified_NoLocalExecution",
        "branch": BRANCH,
        "currentDemoHead": demo_head,
        "reviewedC10CodeHead": REVIEWED_DEMO_CODE,
        "checkedNativeAndOverlayFiles": count,
        "linkSourceBlobsMatched": True,
        "checkedEvidenceProducerFiles": producer_count,
        "receiptProducerBlobsMatched": True,
        "checkedHistoricalComparators": len(HIST),
        "checkedSourceManifest": True,
        "compiledTranslationUnits": 0,
        "actualUnityBuild": "NotRun",
        "actualIl2CppNativeLink": "NotRun",
        "realPlayerCellsPassed": 0,
        "realPlayerCellsNoCoverage": 18,
        "remoteBranchAtReview": "NotAuthenticatedBySourceOnlyCLI",
        "APPROVED_LOCAL_HANDOFF_BLOB": None,
        "D5BLocalExecution": "NotAuthorized",
        "WEB_TO_LOCAL": "CLOSED_NO_LOCAL_EXECUTION",
        "R03Accepted": False,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    for role in ROLES:
        p.add_argument("--" + role.replace("_", "-") + "-root",
                       type=Path, required=True)
    p.add_argument("--expected-demo-head", required=True)
    args = p.parse_args(argv)
    roots = {role: getattr(args, role + "_root") for role in ROLES}
    try:
        result = inspect(roots, args.expected_demo_head)
    except (Rejected, OSError, json.JSONDecodeError,
            UnicodeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"result": "BlockedBeforeUnity",
                          "reason": str(error),
                          "D5BLocalExecution": "NotAuthorized"},
                         sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
