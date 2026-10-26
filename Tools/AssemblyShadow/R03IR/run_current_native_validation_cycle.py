#!/usr/bin/env python3
"""One-use R03 evidence cycle: original-S read-only custody and current-native Player.

No historical command is rerun. No stage can grant R03 acceptance or Human Review
Gate approval. The canonical WEB_TO_LOCAL must authorize this *new* cycle.
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
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
# run_local.py belongs to the adjacent historical R03 infrastructure.
sys.path.insert(0, str(HERE.parent / "R03"))
import current_native_source_gate as source
import current_native_vm_delta_contracts as delta
from run_local import BRANCH, REPOS, identity
NATIVE = source.CURRENT["il2cpp_plus"]
S_PUBLICATION = "fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b"
MIN_FREE_GIB = 20
EXPECTED_BUILD_ROLES = ("candidate-release", "candidate-debug", "candidate-off")
EXPECTED_PLAYERS = (
    "IR-R03-02-release-baseline", "IR-R03-02-debug-baseline",
    "IR-R03-02-release-type", "IR-R03-02-off", "IR-R03-02-release-engine",
)


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for piece in iter(lambda: f.read(1048576), b""):
            h.update(piece)
    return h.hexdigest()


def written(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def git(path: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(path), *args], capture_output=True, text=True,
        check=False, timeout=90)
    require(p.returncode == 0, "Git authority failed: " + str(path) + " " +
            " ".join(args) + ": " + p.stderr[-350:])
    return p.stdout.strip()


def exact_path(value: Path, *, exists: bool = True) -> Path:
    require(value.is_absolute() and ".." not in value.parts and
            value.resolve(strict=False) == value and not value.is_symlink(),
            "Absolute, physically canonical path required: " + str(value))
    if exists:
        require(value.exists(), "Missing required path: " + str(value))
    return value


def validate_destination(workspace: Path, original: Path, output: Path) -> None:
    exact_path(workspace)
    exact_path(original)
    exact_path(output.parent)
    exact_path(output, exists=False)
    require(not output.exists() and output.parent.is_dir() and
            output not in workspace.parents and workspace not in output.parents,
            "New absent external output root outside the entire workspace required")
    sources = [workspace / name for name in REPOS] + [original]
    require(all(output != p and output not in p.parents and
                p not in output.parents for p in sources),
            "Output must be disjoint from every source checkout")
    require(original != workspace / "hybridclr_demo" and
            original not in (workspace / name for name in REPOS),
            "Original-S must be a distinct clean historical checkout")


def validate_original(original: Path) -> dict:
    require(original.is_dir() and not original.is_symlink() and
            git(original, "rev-parse", "--show-toplevel") == str(original),
            "Original-S checkout must own its Git root")
    require(git(original, "rev-parse", "HEAD") == S_PUBLICATION and
            not git(original, "status", "--porcelain=v1", "--untracked-files=all"),
            "Original S must be exactly fc55, detached or clean")
    remote = git(original, "remote", "get-url", "origin")
    require(remote in (
        "https://github.com/night-outlook/hybridclr_demo.git",
        "https://github.com/night-outlook/hybridclr_demo",
        "git@github.com:night-outlook/hybridclr_demo.git",
        "git@github.com:night-outlook/hybridclr_demo",
        "ssh://git@github.com/night-outlook/hybridclr_demo.git",
    ), "Historical worktree must retain canonical demo remote")
    return {"repository": "night-outlook/hybridclr_demo", "path": str(original),
            "commit": S_PUBLICATION, "clean": True,
            "role": "immutable-original-S-read-only"}


def validate_sources(workspace: Path, demo_commit: str) -> dict:
    require(re.fullmatch("[0-9a-f]{40}", demo_commit) is not None,
            "Exact 40-digit demo source commit required")
    roots = {name: workspace / name for name in REPOS}
    for p in roots.values():
        exact_path(p)
        require(p.is_dir(), "Repository root must be a directory")
    repositories = [identity(roots[name], demo_commit if name == "hybridclr_demo"
                             else source.CURRENT[name]) for name in REPOS]
    checked = source.verify_source_roots(roots, require_checkout_heads=True)
    require(checked["result"] == "PassedCoherentSourceOnly_NoPlayerOrRuntimeValidation" and
            checked["verifiedSourceFiles"] == 10, "Ten-file source proof not passed")
    config = json.loads(delta.MANIFEST.read_text(encoding="utf-8"))
    vm = delta.validate(config, roots["il2cpp_plus"], check_native_commit=True)
    require(vm["result"] == "PassedCurrentNativeVmSourceDeltaOnly" and
            vm["changedVmFileCount"] == 42, "Forty-two-file source inventory not passed")
    return {"result": "PassedReadOnlySourceAdmission_NotBuildOrRuntime",
            "repositories": repositories, "sourceGate": checked, "vmDelta": vm,
            "R03Accepted": False, "ReadyForHumanReviewGate": False}


def validate_machine(unity: Path, output: Path) -> dict:
    require(sys.platform == "darwin" and platform.machine().lower() in
            ("arm64", "aarch64"), "Actual Player cycle requires macOS Apple Silicon")
    exact_path(unity)
    require(unity.is_file() and os.access(unity, os.X_OK),
            "Unity executable must exist and be executable")
    free = shutil.disk_usage(output.parent).free
    require(free >= MIN_FREE_GIB * 1024**3,
            "Insufficient available space for original archive and three fresh Players")
    return {"host": platform.platform(), "architecture": platform.machine(),
            "unityExecutable": str(unity), "unityExecutableSha256": digest(unity),
            "freeBytesAtAdmission": free, "minimumFreeGiB": MIN_FREE_GIB,
            "unityVersionValidatedByBuild": "NotRunAtPreflight"}


def verify_current_batch(result_path: Path, demo_commit: str) -> dict:
    require(result_path.is_file() and not result_path.is_symlink(),
            "Missing actual native Local batch final receipt")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    expected = {"hybridclr_demo": demo_commit, **source.CURRENT}
    require(result.get("repositories") == expected,
            "Fresh Player batch source tuple mismatch")
    require(result.get("result") == "FocusedEvidenceReadyForPrimaryReview" and
            result.get("sealStatus") == "Passed", "Fresh Player batch or seal did not pass")
    require(result.get("plannedFreshBuilds") == 3 and
            result.get("verifiedFreshBuilds") == 3 and
            result.get("plannedFreshPlayers") == 5 and
            result.get("verifiedFreshPlayers") == 5 and
            result.get("recordedFreshPlayerRawFiles") == 5,
            "Three genuine build roles and five fresh Player cases required")
    ids = {c.get("id"): c.get("result") for c in result.get("cells", [])}
    require(all(ids.get("build-" + role) == "Passed" for role in EXPECTED_BUILD_ROLES) and
            all(ids.get(case) == "Passed" for case in EXPECTED_PLAYERS),
            "Exact per-role and per-Player case results required")
    require(result.get("originalSFixtureAuthority") == "AuthenticatedOriginalCommit" and
            bool(result.get("originalSFixtureAuthoritySha256")) and
            result.get("R03Accepted") is False and result.get("H2Passed") is False and
            result.get("fullLegacyRegressionAcceptance") is False and
            result.get("qualificationApproved") is False and
            result.get("pureInterpreterExpansionEnabled") is False,
            "No missing original fixture or simulated stage-acceptance claim")
    return {"result": "PassedFiveFocusedCurrentNativePlayersOnly",
            "builds": 3, "players": 5,
            "localBatchResultSha256": digest(result_path),
            "IRR0301IndependentlyClosed": False,
            "IRR0302IndependentlyClosed": False, "R03Accepted": False}


def run_step(root: Path, name: str, argv: list[str], timeout: int) -> dict:
    """Record before launch, use one fresh process group, never retry a command."""
    assert re.fullmatch(r"[a-z0-9-]+", name)
    step = root / "steps" / name
    step.mkdir(parents=True, exist_ok=False)
    written(step / "INVOCATION.json", {
        "name": name, "argv": [str(x) for x in argv],
        "timestampUtc": utc(), "timeoutSeconds": timeout,
        "singleInvocation": True, "retryAllowed": False})
    status = {"name": name, "state": "Failed", "exitCode": None,
              "timedOut": False, "startedUtc": utc(), "finishedUtc": None,
              "processId": None, "mayHaveExternalOwnedChildren": False}
    with (step / "stdout.log").open("xb") as out, (step / "stderr.log").open("xb") as err:
        process = None
        try:
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       GIT_TERMINAL_PROMPT="0", DOTNET_CLI_DO_NOT_USE_MSBUILD_SERVER="1")
            process = subprocess.Popen(
                [str(x) for x in argv], cwd=str(root), env=env,
                stdout=out, stderr=err, start_new_session=True)
            status["processId"] = process.pid
            try:
                status["exitCode"] = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                status["timedOut"] = True
                status["mayHaveExternalOwnedChildren"] = True
                os.killpg(process.pid, signal.SIGKILL)
                status["exitCode"] = process.wait(timeout=30)
        except KeyboardInterrupt:
            status["mayHaveExternalOwnedChildren"] = process is not None
            if process is not None and process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=30)
                except Exception:
                    pass
            raise
        except Exception as exc:
            status["exception"] = repr(exc)
            status["mayHaveExternalOwnedChildren"] = process is not None
            if process is not None and process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=30)
                except BaseException as cleanup_error:
                    status["cleanupError"] = repr(cleanup_error)
        finally:
            status["finishedUtc"] = utc()
    status["stdoutSha256"] = digest(step / "stdout.log")
    status["stderrSha256"] = digest(step / "stderr.log")
    status["state"] = "Passed" if (
        status["exitCode"] == 0 and not status["timedOut"] and
        not status.get("exception") and not status.get("cleanupError")) else "Failed"
    written(step / "RESULT.json", status)
    return status


def step_ok(row: dict) -> bool:
    return row.get("state") == "Passed"


def assess_summary(stages: dict, native: dict | None, after: dict | None) -> dict:
    required = (
        "source-contracts", "oracle-contracts", "vm-delta-contracts",
        "original-s-host-contracts", "original-s-audit", "original-s-process-joins",
        "native-host-diagnostics", "current-native-players",
        "installed-source-host-contracts", "native-installed-source-audit",
    )
    completed = all(step_ok(stages.get(key, {})) for key in required)
    completed = completed and all(step_ok(row) for row in stages.values())
    valid = completed and native is not None and (
        native.get("result") == "PassedFiveFocusedCurrentNativePlayersOnly")
    valid = valid and after is not None and after.get("result") == (
        "PassedReadOnlySourceAdmission_NotBuildOrRuntime")
    return {"schemaVersion": 1, "kind": "R03IRCurrentNativeOneUseLocalCycle",
            "result": "FocusedEvidenceReadyForIndependentReview" if valid else "ReturnRequired",
            "stages": stages, "nativeFocusedVerification": native,
            "postflightSourceAuthority": after,
            "R03Accepted": False, "H2Passed": False,
            "ReadyForHumanReviewGate": False, "runtimeAcceptance": False,
            "independentR03FullStageReview": "NotRun",
            "IRR0301IndependentlyClosed": False, "IRR0302IndependentlyClosed": False,
            "historicalSResultReclassified": False,
            "historicalB7e3AndC42aResultsChanged": False,
            "pureInterpreterEnabled": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--original-s", type=Path, required=True,
                        help="Separate clean demo worktree at original S fc55 publication")
    parser.add_argument("--unity", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--demo-commit", required=True)
    args = parser.parse_args()
    if not __debug__:
        raise ValueError("Python -O invalidates validation assertions")
    validate_destination(args.workspace, args.original_s, args.output)
    original = validate_original(args.original_s)
    before = validate_sources(args.workspace, args.demo_commit)
    host = validate_machine(args.unity, args.output)
    # All root and source admission occurs before the first write.
    args.output.mkdir(mode=0o700)
    root = args.output
    written(root / "ADMISSION.json", {"schemaVersion": 1,
            "kind": "R03IRCurrentNativeLocalAdmission", "timeUtc": utc(),
            "originalS": original, "source": before, "host": host,
            "runtimeAcceptance": False, "R03Accepted": False})
    demo = args.workspace / "hybridclr_demo"
    native = args.workspace / "il2cpp_plus"
    script = HERE
    tests = [
        ("source-contracts", [sys.executable, "-B", script / "current_native_source_contracts.py",
            "--demo", demo, "--native", native, "--hybridclr", args.workspace / "hybridclr",
            "--package", args.workspace / "hybridclr_unity"], 1800),
        ("oracle-contracts", [sys.executable, "-B", script / "current_native_oracle_contracts.py"], 1200),
        ("vm-delta-contracts", [sys.executable, "-B", script / "current_native_vm_delta_contracts.py",
            "--native", native], 1200),
        ("original-s-host-contracts", [sys.executable, "-B",
            script / "test_audit_s_provenance.py"], 1200),
        ("installed-source-host-contracts", [sys.executable, "-B",
            script / "current_native_install_contracts.py"], 1200),
    ]
    stages: dict[str, dict] = {}
    after = None
    native_verdict = None
    try:
        for name, argv, timeout in tests:
            stages[name] = run_step(root, name, argv, timeout)
        audit = root / "original-s-audit"
        stages["original-s-audit"] = run_step(
            root, "original-s-audit",
            [sys.executable, "-B", script / "audit_s_provenance.py",
             "--repo", args.original_s, "--output", audit], 10800)
        if step_ok(stages["original-s-audit"]):
            try:
                audit_result = json.loads((audit / "audit.json").read_text())
                require(audit_result.get("result") == "Passed" and
                        audit_result.get("archiveMembers") == 15713 and
                        audit_result.get("cells") == 90, "Original S archive semantic ledger")
            except Exception as error:
                stages["original-s-audit"]["state"] = "Failed"
                stages["original-s-audit"]["auditVerdictError"] = str(error)
        if step_ok(stages["original-s-audit"]):
            stages["original-s-process-joins"] = run_step(
                root, "original-s-process-joins",
                [sys.executable, "-B", script / "audit_s_process_joins.py",
                 "--original", args.original_s, "--audit", audit,
                 "--output", root / "original-s-process-joins"], 5400)
            if step_ok(stages["original-s-process-joins"]):
                p = root / "original-s-process-joins/process-joins.json"
                if not p.is_file() or json.loads(p.read_text()).get("result") != "Passed":
                    stages["original-s-process-joins"]["state"] = "Failed"
                    stages["original-s-process-joins"]["auditVerdictError"] = "Missing process joins PASS"
        else:
            stages["original-s-process-joins"] = {
                "state": "Blocked", "reason": "Authentic original S full archive must pass first"}
        stages["native-host-diagnostics"] = run_step(
            root, "native-host-diagnostics",
            [sys.executable, "-B", script / "run_primary_host_preflight.py",
             "--workspace", args.workspace, "--expected-demo", args.demo_commit,
             "--expected-native", NATIVE,
             "--output", root / "native-host-diagnostics"], 7200)
        if all(step_ok(stages[name]) for name, _, _ in tests):
            # Repeat source, branch, clean, live remote and 42 VM byte checks after
            # independent host/archive commands and immediately before actual Unity.
            validate_sources(args.workspace, args.demo_commit)
            stages["current-native-players"] = run_step(
                root, "current-native-players",
                [sys.executable, "-B", script / "run_terminal_current.py",
                 "--workspace", args.workspace, "--output", root / "current-native",
                 "--unity", args.unity, "--demo-commit", args.demo_commit], 25200)
            if step_ok(stages["current-native-players"]):
                native_verdict = verify_current_batch(
                    root / "current-native/LOCAL_BATCH_RESULT.json", args.demo_commit)
                parity_path = root / "installed-native-vm-parity.json"
                stages["native-installed-source-audit"] = run_step(
                    root, "native-installed-source-audit",
                    [sys.executable, "-B", script / "current_native_install_audit.py",
                     "--workspace", args.workspace,
                     "--batch", root / "current-native",
                     "--demo-commit", args.demo_commit,
                     "--output", parity_path], 7200)
                if step_ok(stages["native-installed-source-audit"]):
                    report = json.loads(parity_path.read_text(encoding="utf-8"))
                    if not (report.get("result") == "PassedInstalledSourceParityOnly" and
                            report.get("verifiedBuildRoles") == 3 and
                            report.get("installedVmSourcePairs") == 126 and
                            report.get("R03Accepted") is False):
                        stages["native-installed-source-audit"]["state"] = "Failed"
                        stages["native-installed-source-audit"]["auditVerdictError"] = (
                            "Three installed physical 42-file VM parity roles required")
            else:
                stages["native-installed-source-audit"] = {
                    "state": "Blocked", "reason": "Genuine sealed current-native Player must pass first"}
        else:
            stages["current-native-players"] = {
                "state": "Blocked", "reason": "At least one source/oracle/VM host contract failed"}
            stages["native-installed-source-audit"] = {
                "state": "Blocked", "reason": "No current Player source installation exists"}
    except BaseException as error:
        stages["coordinator-error"] = {"state": "Failed", "exception": repr(error)}
    finally:
        try:
            after = validate_sources(args.workspace, args.demo_commit)
            validate_original(args.original_s)
        except BaseException as error:
            stages["postflight-authority"] = {
                "state": "Failed", "error": repr(error)}
            after = None
        summary = assess_summary(stages, native_verdict, after)
        summary["originalS"] = original
        summary["sourceBefore"] = before
        summary["host"] = host
        summary["startAdmissionSha256"] = digest(root / "ADMISSION.json")
        summary["finishedUtc"] = utc()
        written(root / "RESULT.json", summary)
        # Binds coordinator receipts; child evidence has its own original/fresh
        # sealing contracts. A root SHA list is NOT a 15,713-member archive audit.
        rows = []
        for path in sorted((root / "steps").rglob("*")):
            if path.is_file() and not path.is_symlink():
                rows.append({"path": str(path.relative_to(root)), "sha256": digest(path),
                             "size": path.stat().st_size})
        for name in ("ADMISSION.json", "RESULT.json"):
            path = root / name
            rows.append({"path": name, "sha256": digest(path), "size": path.stat().st_size})
        written(root / "COORDINATOR_MANIFEST.json", {
            "kind": "R03IRCoordinatorReceiptsOnly", "files": rows,
            "externalChildEvidenceSealedHere": False,
            "productAcceptance": False})
    print(json.dumps({"result": summary["result"], "output": str(root),
          "stages": {k: v.get("state") for k, v in stages.items()},
          "runtimeAcceptance": False}, sort_keys=True), flush=True)
    return 0 if summary["result"] == "FocusedEvidenceReadyForIndependentReview" else 1


if __name__ == "__main__":
    raise SystemExit(main())
