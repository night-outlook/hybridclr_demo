#!/usr/bin/env python3
"""Read-only re-admission for the retained original-S fc55 worktree and R03 run.

No Unity, dotnet build, source mutation, archive reconstruction, output root or
new worktree is created. This is a prerequisite check, not runtime evidence.
A pass does not authorize a previously consumed Local cycle.
"""
from __future__ import annotations

import argparse
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

REQUIRED_CSPROJ_BLOB = "6bd02a765a53d9fc1830d1026f2b02710172a092"
ADVISORY_HEADROOM_GIB = 30


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
    path = workspace / "hybridclr_demo/Tools/AssemblyShadow/R03/PlayerFixtures/PlayerFixtures.csproj"
    require(path.is_file() and not path.is_symlink() and
            source.git_blob(path.read_bytes()) == REQUIRED_CSPROJ_BLOB,
            "Current R03 net8.0 fixture project source identity changed")
    project = ET.fromstring(path.read_text(encoding="utf-8"))
    frameworks = [e.text for e in project.iter("TargetFramework")]
    require(frameworks == ["net8.0"], "Expected unique real net8.0 fixture target")
    return {"path": str(path), "gitBlob": REQUIRED_CSPROJ_BLOB,
            "targetFramework": "net8.0"}


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


def inspect(workspace: Path, original: Path, unity: Path,
            output: Path, demo_commit: str) -> dict:
    # No directory, report, worktree or receipt is created.
    cycle.validate_destination(workspace, original, output)
    retained = registered_original(workspace, original)
    current = cycle.validate_sources(workspace, demo_commit)
    machine = cycle.validate_machine(unity, output)
    toolchain = verify_toolchain(workspace)
    capacity = sample_capacity(output)
    return {"schemaVersion": 1, "kind": "R03RetainedOriginalSReadOnlyReadmission",
            "result": "PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun",
            "retainedOriginal": retained, "currentSource": current,
            "machine": machine, "toolchain": toolchain, "capacity": capacity,
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
