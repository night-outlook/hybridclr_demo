#!/usr/bin/env python3
"""Read-only re-admission for the retained original-S fc55 worktree and R03 run.

No Unity, dotnet build, source mutation, archive reconstruction, output root or
new worktree is created. This is a prerequisite check, not runtime evidence.
A pass does not authorize a previously consumed Local cycle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

import current_native_source_gate as source
import run_current_native_validation_cycle as cycle

# Current initializer input: the single reviewed csproj change adds
# InitializerNativeTargetFixtures.cs. Historical blob 249c47... is NOT
# accepted for this new cycle; keep exact fingerprinting, do not whitelist
# arbitrary project revisions.
REQUIRED_CSPROJ_BLOB = "1c5c8628ead41d67d94bb1846dd5bf9764620c68"
REQUIRED_INITIALIZER_SOURCE_BLOB = "73e1c79c593b46cd2d8232ca6ccaae62d5dff4f0"
REQUIRED_PROGRAM_SOURCE_BLOB = "c8de453c03321a5b91635da7c6ed795664bcb975"
ADVISORY_HEADROOM_GIB = 40


def require(ok: bool, why: str):
    if not ok:
        raise ValueError(why)


def run_read_only(argv, *, timeout=90) -> str:
    proc = subprocess.run([str(x) for x in argv], capture_output=True,
                          text=True, timeout=timeout, check=False,
                          env=dict(os.environ, DOTNET_CLI_TELEMETRY_OPTOUT="1",
                                   DOTNET_SKIP_FIRST_TIME_EXPERIENCE="1"))
    require(proc.returncode == 0,
            "Read-only command failed: " + str(argv[0]) +
            " exit=" + str(proc.returncode) +
            " stderr=" + proc.stderr[-500:])
    return proc.stdout.strip()


def registered_original(workspace: Path, original: Path) -> dict:
    """Require exactly the retained, registered fc55 worktree; don't recreate it."""
    raw = run_read_only(["git", "-C", str(workspace / "hybridclr_demo"),
                         "worktree", "list", "--porcelain"])
    records = []
    for block in raw.split("\n\n"):
        if not block.strip():
            continue
        lines = block.splitlines()
        require(lines[0].startswith("worktree "), "Malformed Git worktree roster")
        fields = {"worktree": lines[0][len("worktree "):]}
        for line in lines[1:]:
            if line.startswith("HEAD "):
                fields["head"] = line[len("HEAD "):]
            elif line == "detached":
                fields["detached"] = True
        records.append(fields)
    matches = [r for r in records if r["worktree"] == str(original)]
    require(len(matches) == 1 and matches[0].get("head") == cycle.S_PUBLICATION
            and matches[0].get("detached") is True,
            "The retained clean original-S fc55 Git worktree is not singly registered")
    evidence = cycle.validate_original(original)
    return {"result": "PassedRegisteredRetainedWorktreeReadOnly",
            "registration": matches[0], "authority": evidence,
            "worktreeCreatedOrReplaced": False,
            "historicalExecutionRetried": False}


def fixture_net8_source(workspace: Path) -> dict:
    """Authenticate the *current* initializer fixture project and its producer.

    This is deliberately not a blanket 'accept HEAD' check: every source is
    pinned to a reviewed Git blob, and all three files must be regular files.
    The earlier pre-initializer csproj remains historical input, not a new
    Local validation authority.
    """
    root = workspace / "hybridclr_demo/Tools/AssemblyShadow/R03/PlayerFixtures"
    path = root / "PlayerFixtures.csproj"
    producer = root / "InitializerNativeTargetFixtures.cs"
    program = root / "Program.cs"
    for target, expected, label in (
        (path, REQUIRED_CSPROJ_BLOB, "net8.0 fixture project"),
        (producer, REQUIRED_INITIALIZER_SOURCE_BLOB, "initializer fixture producer"),
        (program, REQUIRED_PROGRAM_SOURCE_BLOB, "fixture generator entry"),
    ):
        require(target.is_file() and not target.is_symlink() and
                source.git_blob(target.read_bytes()) == expected,
                "Current R03 " + label + " source identity changed")
    project = ET.fromstring(path.read_text(encoding="utf-8"))
    frameworks = [e.text for e in project.iter("TargetFramework")]
    require(frameworks == ["net8.0"], "Expected unique real net8.0 fixture target")
    compile_items = [e.get("Include") for e in project.iter("Compile")]
    require(len(compile_items) == len(set(compile_items)) and
            all(compile_items.count(name) == 1 for name in (
                "Program.cs", "TerminalProducerFixtures.cs",
                "InitializerNativeTargetFixtures.cs")) and
            [e.text for e in project.iter("EnableDefaultCompileItems")] == ["false"],
            "Exactly one explicit initializer and legacy generator source required")
    producer_text = producer.read_text(encoding="utf-8")
    require('InterpreterImportModule = "__InternalDynamic"' in producer_text and
            'new ModuleRefUser(module, InterpreterImportModule)' in producer_text and
            'R03IR/InitializerNative/v2/' in producer_text,
            "Reviewed dynamic interpreted import and v2 identity required")
    require("--ir-terminal-native-targets" in program.read_text(encoding="utf-8"),
            "Initializer fixture entry point missing from pinned generator")
    return {"path": str(path), "gitBlob": REQUIRED_CSPROJ_BLOB,
            "targetFramework": "net8.0",
            "initializerSourceGitBlob": REQUIRED_INITIALIZER_SOURCE_BLOB,
            "programSourceGitBlob": REQUIRED_PROGRAM_SOURCE_BLOB,
            "initializerCompileIncludedExactlyOnce": True,
            "defaultCompileItemsDisabled": True}


def verify_sdk_output(sdks: str, runtimes: str) -> dict:
    versions = []
    for line in sdks.splitlines():
        match = re.fullmatch(r"\s*(\d+)\.(\d+)\.(\d+)[^\s]*\s+\[[^\]]+\]\s*", line)
        if match:
            versions.append((int(match[1]), int(match[2]), int(match[3])))
    require(any(version[0] >= 8 for version in versions),
            "dotnet SDK >=8 required to build R03 net8.0 project")
    runtimes8 = [line.strip() for line in runtimes.splitlines()
                 if re.match(r"^Microsoft\.NETCore\.App 8\.\d+\.\d+ ", line)]
    require(bool(runtimes8),
            "Microsoft.NETCore.App 8.x runtime required to execute net8.0 fixtures")
    return {"sdkVersions": [".".join(map(str, v)) for v in versions],
            "net8RuntimeLines": runtimes8,
            "net8ToolchainAvailable": True}


def resolved_command(name: str) -> Path:
    location = shutil.which(name)
    require(location is not None, "Required command not on PATH: " + name)
    path = Path(location).resolve(strict=True)
    require(path.is_file() and os.access(path, os.X_OK),
            "Required executable unavailable: " + name)
    return path


def verify_toolchain(workspace: Path) -> dict:
    """Check exact fixture runtime/tooling without compiling any project."""
    fixture = fixture_net8_source(workspace)
    dotnet = resolved_command("dotnet")
    compiler = resolved_command(os.environ.get("CXX", "clang++"))
    lipo = resolved_command("lipo")
    sdk_info = verify_sdk_output(
        run_read_only([dotnet, "--list-sdks"]),
        run_read_only([dotnet, "--list-runtimes"]))
    dotnet_info = run_read_only([dotnet, "--info"])
    sdk_info["dotnetRidArm64Reported"] = ("osx-arm64" in dotnet_info)
    # A non-arm64 external dotnet may be runnable via Rosetta; retain the RID
    # observation rather than silently claiming architecture equivalence.
    return {"fixture": fixture, "dotnet": str(dotnet),
            "compiler": str(compiler), "lipo": str(lipo),
            "compilerVersion": run_read_only([compiler, "--version"]).splitlines()[0],
            "dotnetSdk": sdk_info,
            "officialUnityOrSdkCompile": "NotRun",
            "runtimeAcceptance": False}


def sample_capacity(output: Path, *, free_bytes: int | None = None) -> dict:
    """Never weaken the coordinator's fixed 20-GiB floor."""
    free = shutil.disk_usage(output.parent).free if free_bytes is None else free_bytes
    minimum = cycle.MIN_FREE_GIB * 1024**3
    require(free >= minimum, "Fresh destination capacity below fixed 20-GiB minimum")
    return {"result": "PassedCurrentFreeSample_NotSustainedCapacity",
            "outputParent": str(output.parent), "freeBytes": free,
            "freeGiB": round(free / 1024**3, 3),
            "hardMinimumGiB": cycle.MIN_FREE_GIB,
            "advisoryHeadroomGiB": ADVISORY_HEADROOM_GIB,
            "belowAdvisory": free < ADVISORY_HEADROOM_GIB * 1024**3,
            "thresholdLowered": False,
            "futureUnityDiskUseGuaranteed": False}


def verify_standalone_current_cli(workspace: Path, output: Path) -> dict:
    """Actual fresh interpreter, unassisted by PYTHONPATH; no batch or Unity."""
    runner = (workspace / "hybridclr_demo/Tools/AssemblyShadow/R03IR/"
              "run_terminal_current.py")
    if not runner.is_file() or runner.is_symlink() or runner.resolve() != runner:
        raise ValueError("Owning current-native standalone CLI file unavailable")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               PYTHONNOUSERSITE="1")
    for key in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP"):
        env.pop(key, None)
    argv = [sys.executable, "-B", str(runner), "--help"]
    # The deliberately different cwd exposes accidental ambient import behavior.
    proc = subprocess.run(
        argv, cwd=str(output.parent), env=env,
        capture_output=True, text=True, timeout=45, check=False)
    require(proc.returncode == 0 and "--demo-commit" in proc.stdout and
            "--workspace" in proc.stdout and "--output" in proc.stdout and
            not proc.stderr, "Standalone current-native CLI import preflight "
            "failed (no PYTHONPATH assistance), exit=" + str(proc.returncode) +
            ", stderr=" + proc.stderr[-1200:])
    return {"kind": "R03CurrentNativeStandaloneImportPreflight",
            "result": "PassedFreshPythonProcessHelp_NoUnityOrRuntime",
            "argv": argv, "cwd": str(output.parent), "exitCode": 0,
            "pythonPathProvided": False, "sourceDirectory": str(runner.parent),
            "stdoutSha256": hashlib.sha256(proc.stdout.encode()).hexdigest(),
            "stderrSha256": hashlib.sha256(proc.stderr.encode()).hexdigest(),
            "outputRootCreated": False, "unityOrPlayerLaunched": False,
            "runtimeAcceptance": False}


def inspect(workspace: Path, original: Path, unity: Path,
            output: Path, demo_commit: str) -> dict:
    # No directory, report, worktree or receipt is created.
    cycle.validate_destination(workspace, original, output)
    retained = registered_original(workspace, original)
    current = cycle.validate_sources(workspace, demo_commit)
    machine = cycle.validate_machine(unity, output)
    toolchain = verify_toolchain(workspace)
    standalone_cli = verify_standalone_current_cli(workspace, output)
    capacity = sample_capacity(output)
    return {"schemaVersion": 1, "kind": "R03RetainedOriginalSReadOnlyReadmission",
            "result": "PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun",
            "retainedOriginal": retained, "currentSource": current,
            "machine": machine, "toolchain": toolchain,
            "standaloneCurrentNativeCli": standalone_cli, "capacity": capacity,
            "runRootCreated": False, "coordinatorInvoked": False,
            "archiveOrPlayerExecuted": False, "R03Accepted": False,
            "ReadyForHumanReviewGate": False, "runtimeAcceptance": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("workspace", "original-s", "unity", "output"):
        parser.add_argument("--" + key, type=Path, required=True)
    parser.add_argument("--demo-commit", required=True)
    args = parser.parse_args()
    require(__debug__, "Python -O is not supported")
    try:
        result = inspect(args.workspace, args.original_s, args.unity,
                         args.output, args.demo_commit)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError, ET.ParseError) as error:
        print(json.dumps({"kind": "R03RetainedOriginalSReadOnlyReadmission",
              "result": "BlockedBeforeCoordinator", "reason": str(error),
              "coordinatorInvoked": False, "newBatchRootCreated": False,
              "runtimeAcceptance": False}, indent=2, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
