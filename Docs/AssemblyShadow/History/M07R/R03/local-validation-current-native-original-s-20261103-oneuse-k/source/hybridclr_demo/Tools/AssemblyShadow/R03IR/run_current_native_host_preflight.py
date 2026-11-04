#!/usr/bin/env python3
"""Current R03 one-use native host batch: 8 historical + 2 new owner suites.

A source-pinned wrapper around the ORIGINAL eight-suite helper. This module
does not modify historical scripts, run Unity/IL2CPP or infer runtime
acceptance. It refuses a partial/faked ten-suite roster before the coordinator
may launch any Player. Every child command is run once and has an independent
process/stream receipt in the new evidence root.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

import current_native_source_gate as source
import run_primary_host_preflight as historical

HERE = Path(__file__).resolve().parent
BRANCH = source.BRANCH
LEGACY_HELPER = HERE / "run_primary_host_preflight.py"
LEGACY_HELPER_BLOB = "2d51be157b94a47ac19d1061d0066c1f98dbc177"
LEGACY_COMPONENTS = (
    "native-general-stream",
    "native-v2-codec",
    "native-v2-file-transaction",
    "native-v2-legacy-sink",
    "execution-serializer-strict",
    "execution-serializer-strict-run",
    "execution-serializer-sanitized",
    "execution-serializer-sanitized-run",
)
OWNER_SUITES = (
    ("native-owner-method-classifier", "native_owner_decision_contracts.py", 2),
    ("native-owner-full-tu", "engine_owner_quit_contracts.py", 3),
)
ALL_COMPONENTS = LEGACY_COMPONENTS + tuple(row[0] for row in OWNER_SUITES)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def read_strict(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink(),
            "Missing/aliased genuine native host result: " + str(path))
    data = json.loads(path.read_bytes(), object_pairs_hook=source.strict_object)
    require(type(data) is dict, "Native host report must be an object")
    return data


def expected_heads(demo_commit: str) -> dict[str, str]:
    source.expected_batch_repositories(demo_commit)
    return {"hybridclr_demo": demo_commit, **source.CURRENT}


def verify_legacy_report(receipt: dict, demo_commit: str) -> list[dict]:
    """Read the genuine historical helper result, not a self-reported count."""
    require(type(receipt) is dict and type(receipt.get("schemaVersion")) is int and
            receipt["schemaVersion"] == 1 and
            receipt.get("kind") == "R03PrimaryHostOnlyPreflight" and
            receipt.get("result") == "PassedHostOnly" and
            receipt.get("sourcePreserved") is True and
            receipt.get("actualUnityOrPlayerRun") is False and
            receipt.get("officialUnitySdkCompile") is False and
            receipt.get("runtimeAcceptance") is False and
            receipt.get("historicalEvidenceUpgraded") is False,
            "Historical eight-suite helper must pass its original scope")
    repos = receipt.get("repositories")
    heads = expected_heads(demo_commit)
    require(type(repos) is list and len(repos) == 4,
            "Historical helper must bind exactly four physical Git origins")
    seen = set()
    for item in repos:
        require(type(item) is dict and type(item.get("repository")) is str,
                "Malformed historical repository evidence")
        name = item["repository"].removeprefix("night-outlook/")
        require(item["repository"] == "night-outlook/" + name and
                name in heads and name not in seen and
                item.get("branch") == BRANCH and
                item.get("head") == heads[name] and
                item.get("remoteHead") == heads[name] and
                item.get("clean") is True,
                "Historical helper repository/head/remote evidence mismatch")
        seen.add(name)
    require(seen == set(heads), "Missing historical repository identity")
    rows = receipt.get("commands")
    require(type(rows) is list and len(rows) == len(LEGACY_COMPONENTS),
            "Historical helper must execute all eight commands")
    names = [r.get("name") for r in rows if type(r) is dict]
    require(len(names) == len(rows) and len(set(names)) == len(names) and
            set(names) == set(LEGACY_COMPONENTS) and
            all(row.get("status") == "Passed" for row in rows),
            "Historical command roster missing, duplicated, or failed")
    return [{"name": row["name"], "status": "Passed",
             "origin": "ImmutableHistoricalHelper"} for row in rows]


def verify_owner_run(row: dict, command_root: Path, name: str, tests: int) -> dict:
    """A zero exit without exact unittest execution is not a suite PASS."""
    require(type(row) is dict and row.get("name") == name and
            row.get("state") == "Passed" and
            type(row.get("exitCode")) is int and row["exitCode"] == 0 and
            type(row.get("processId")) is int and row["processId"] > 0 and
            row.get("timedOut") is False and
            row.get("mayHaveExternalOwnedChildren") is False,
            "Missing/failed fresh owner C++11 host invocation: " + name)
    stderr = command_root / "steps" / name / "stderr.log"
    require(stderr.is_file() and not stderr.is_symlink() and
            row.get("stderrSha256") == digest(stderr),
            "Native owner test stream hash mismatch: " + name)
    text = stderr.read_text(encoding="utf-8")
    require(re.search(r"(?m)^Ran " + str(tests) + r" tests? in ", text) is not None and
            re.search(r"(?m)^OK\s*$", text) is not None and
            "FAILED" not in text,
            "Actual compiled owner tests missing or incomplete: " + name)
    return {"name": name, "status": "Passed", "origin": "FreshLocalCurrentOwner",
            "processId": row["processId"], "exitCode": row["exitCode"],
            "stderrSha256": row["stderrSha256"], "stdoutSha256": row["stdoutSha256"],
            "unittestCases": tests}


def verify_current_host_report(result: dict, demo_commit: str,
                               native_commit: str) -> dict:
    """Authoritative current host roster contract reused by the coordinator."""
    require(type(result) is dict and
            type(result.get("schemaVersion")) is int and result["schemaVersion"] == 1 and
            result.get("kind") == "R03IRCurrentNativeTenHostComponents" and
            result.get("result") == "PassedHostOnlyTenComponents" and
            result.get("expectedDemo") == demo_commit and
            result.get("expectedNative") == native_commit == source.CURRENT["il2cpp_plus"] and
            result.get("sourcePreserved") is True and
            result.get("actualUnityOrPlayerRun") is False and
            result.get("officialUnitySdkCompile") is False and
            result.get("runtimeAcceptance") is False and
            result.get("R03Accepted") is False and
            type(result.get("expectedComponentCount")) is int and
            result["expectedComponentCount"] == 10,
            "Incomplete/forged current ten-component host report")
    components = result.get("components")
    require(type(components) is list and len(components) == len(ALL_COMPONENTS),
            "Exactly ten current host components required")
    names = [r.get("name") for r in components if type(r) is dict]
    require(len(names) == len(ALL_COMPONENTS) and
            len(set(names)) == len(names) and
            set(names) == set(ALL_COMPONENTS) and
            all(item.get("status") == "Passed" for item in components),
            "A missing/duplicate/failed current host component cannot pass")
    for row in components:
        require(row.get("origin") == (
            "FreshLocalCurrentOwner" if row["name"] in ALL_COMPONENTS[8:]
            else "ImmutableHistoricalHelper"),
            "Historical/Local component provenance must remain distinct")
        if row["name"] in ALL_COMPONENTS[8:]:
            require(type(row.get("processId")) is int and row["processId"] > 0 and
                    type(row.get("exitCode")) is int and row["exitCode"] == 0 and
                    type(row.get("unittestCases")) is int and row["unittestCases"] ==
                    next(x[2] for x in OWNER_SUITES if x[0] == row["name"]) and
                    type(row.get("stderrSha256")) is str and
                    re.fullmatch("[0-9a-f]{64}", row["stderrSha256"]) is not None,
                    "Fresh owner must have a real two/three-test process receipt")
    return {"result": "PassedVerifiedTenLocalNativeHostComponents",
            "historicalEight": 8, "freshCurrentOwnerSuites": 2,
            "runtimeAcceptance": False}


def inputs(workspace: Path, demo_commit: str, native_commit: str) -> dict:
    # Path(...) returns PosixPath/WindowsPath; exact type equality rejects every
    # genuine argparse(type=Path) input on macOS/Linux/Windows.
    require(isinstance(workspace, Path) and workspace.is_absolute() and
            workspace.is_dir() and not workspace.is_symlink() and
            workspace.resolve(strict=True) == workspace, "Canonical absolute workspace required")
    require(native_commit == source.CURRENT["il2cpp_plus"],
            "Current native commit does not match source gate")
    roots = {name: workspace / name for name in (
        "hybridclr_demo", "hybridclr", "hybridclr_unity", "il2cpp_plus")}
    report = source.verify_source_roots(roots, require_checkout_heads=True)
    require(report["verifiedSourceFiles"] == 11 and
            report["result"] == "PassedCoherentSourceOnly_NoPlayerOrRuntimeValidation",
            "Pinned eleven-source gate required before Local host")
    require(source.git_head(roots["hybridclr_demo"]) == demo_commit,
            "Current demo commit differs before Local host")
    # The outer coordinator already checks all four remotes, but the current
    # host wrapper must independently enforce the same gate BEFORE it creates
    # any output root. Keep the original historical validator intact.
    for name, expected in expected_heads(demo_commit).items():
        historical.verify_repo(workspace, name, expected)
    require(LEGACY_HELPER.is_file() and not LEGACY_HELPER.is_symlink() and
            LEGACY_HELPER.resolve(strict=True) == LEGACY_HELPER and
            source.git_blob(LEGACY_HELPER.read_bytes()) == LEGACY_HELPER_BLOB,
            "Historical eight-suite helper must remain byte-unchanged")
    for _, filename, _ in OWNER_SUITES:
        path = HERE / filename
        require(path.is_file() and not path.is_symlink(),
                "Missing current owner host suite: " + filename)
    return report


def source_fingerprints(workspace: Path) -> dict:
    files = (LEGACY_HELPER, HERE / "run_current_native_host_preflight.py",
             *(HERE / suite[1] for suite in OWNER_SUITES),
             workspace / "il2cpp_plus/libil2cpp/vm/Runtime.cpp",
             workspace / "il2cpp_plus/libil2cpp/vm/AssemblyShadowTerminalReporting.h",
             workspace / "il2cpp_plus/libil2cpp/vm/AssemblyShadowEngineReportingProbe.cpp")
    return {str(path): digest(path) for path in files}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--expected-demo", required=True)
    p.add_argument("--expected-native", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--read-only-admission", action="store_true",
                   help="Validate real source/CLI inputs and absent output only; no host commands, root or Unity")
    args = p.parse_args()
    if not __debug__:
        raise ValueError("Python -O is prohibited")
    report = inputs(args.workspace, args.expected_demo, args.expected_native)
    output = args.output
    require(output.is_absolute() and not output.exists() and
            not output.is_symlink() and output.resolve(strict=False) == output and
            output.parent.is_dir(), "New canonical host output root required")
    for name in ("hybridclr_demo", "hybridclr", "hybridclr_unity", "il2cpp_plus"):
        repo = args.workspace / name
        require(output not in repo.parents and repo not in output.parents and
                output != repo, "Host evidence cannot overlap any source repository")
    if args.read_only_admission:
        # Real fresh-process CLI path from CI and Local, not mock-level evidence
        # and never acceptance or an execution-authority replacement.
        print(json.dumps({
            "schemaVersion": 1,
            "kind": "R03IRCurrentNativeHostReadOnlyAdmission",
            "result": "PassedReadOnlyNativeHostInputs_NoComponentsOrUnity",
            "expectedDemo": args.expected_demo,
            "expectedNative": args.expected_native,
            "sourceGateVerified": report["result"],
            "nativeHostComponentsExecuted": 0,
            "UnityOrPlayerLaunched": False,
            "outputRootCreated": False,
            "runtimeAcceptance": False, "R03Accepted": False,
        }, sort_keys=True), flush=True)
        return 0
    original = source_fingerprints(args.workspace)
    # Existing historical helper independently verifies live branch/remotes
    # before writing its own legacy evidence; this wrapper owns only new state.
    output.mkdir(mode=0o700)
    components: list[dict] = []
    steps: list[dict] = []
    error = None
    from run_current_native_validation_cycle import run_step
    try:
        legacy = run_step(output, "historical-eight",
            [sys.executable, "-B", LEGACY_HELPER,
             "--workspace", args.workspace,
             "--expected-demo", args.expected_demo,
             "--expected-native", args.expected_native,
             "--output", output / "historical-eight"], 7200)
        steps.append(legacy)
        require(legacy["state"] == "Passed", "Historical eight-suite command failed")
        legacy_report = read_strict(output / "historical-eight" / "RESULT.json")
        components += verify_legacy_report(legacy_report, args.expected_demo)
        for name, script, test_count in OWNER_SUITES:
            row = run_step(output, name,
                [sys.executable, "-B", HERE / script,
                 "--native", args.workspace / "il2cpp_plus"], 1800)
            steps.append(row)
            require(row["state"] == "Passed", "Owner native suite failed: " + name)
            components.append(verify_owner_run(row, output, name, test_count))
    except BaseException as exc:
        error = repr(exc)
    preserved = original == source_fingerprints(args.workspace)
    result = {
        "schemaVersion": 1, "kind": "R03IRCurrentNativeTenHostComponents",
        "result": "PassedHostOnlyTenComponents" if error is None and preserved and
                  len(components) == 10 else "FailedOrIncomplete",
        "expectedDemo": args.expected_demo, "expectedNative": args.expected_native,
        "expectedComponentCount": 10, "components": components, "steps": steps,
        "sourceGateVerified": report["result"], "sourcePreserved": preserved,
        "originalSourceHashes": original,
        "finalSourceHashes": source_fingerprints(args.workspace),
        "historicalEightResultSha256": (
            digest(output / "historical-eight" / "RESULT.json")
            if (output / "historical-eight" / "RESULT.json").is_file() else None),
        "actualUnityOrPlayerRun": False, "officialUnitySdkCompile": False,
        "runtimeAcceptance": False, "R03Accepted": False,
        "error": error,
    }
    try:
        if result["result"] == "PassedHostOnlyTenComponents":
            verify_current_host_report(result, args.expected_demo, args.expected_native)
    except BaseException as exc:
        result["result"] = "FailedOrIncomplete"
        result["error"] = repr(exc)
    with (output / "RESULT.json").open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"result": result["result"], "componentCount": len(components),
                      "output": str(output), "runtimeAcceptance": False},
                     sort_keys=True), flush=True)
    return 0 if result["result"] == "PassedHostOnlyTenComponents" else 1


if __name__ == "__main__":
    raise SystemExit(main())
