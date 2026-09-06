#!/usr/bin/env python3
"""Fail-closed continuation for the immutable M06 v8 acceptance run."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


PROJECT = Path("/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow")
ROOT = PROJECT / "_temp" / "AssemblyShadow"
RUN_ROOT = ROOT / "M06V8Continuation"
STATE = ROOT / "m06-v8-continuation.json"
RESULT_ROOT = ROOT / "M06Results-final-v8"
STRICT = ROOT / "m06-final-verification-v8.json"
DEVELOPMENT_BASELINE = "M06-Baseline-v8"
RELEASE_BASELINE = "M06-Baseline-Release-v8"
DEVELOPMENT_GENERATION = ROOT / "M06Generation-121a2a74c5f844b2b09b0f3e49e24eef" / "m06-generation.json"
DEVELOPMENT_ON = ROOT / "M06PlayerInputs-c93706fc8db048a3b593539ea4c68477" / "m06-player-build.json"
PWSH = Path("/usr/local/microsoft/powershell/7/pwsh")


def require(value: object, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def digest(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "Missing/nonregular input: " + str(path))
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(type(value) is dict, "Expected JSON object: " + str(path))
    return value


def write_new(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def shadow_unity() -> list[str]:
    output = subprocess.check_output(["/bin/ps", "ax", "-o", "command="], text=True)
    return [line.strip() for line in output.splitlines()
            if line.strip().startswith("/Applications/Unity/") and "-projectPath " + str(PROJECT) in line]


def run(name: str, command: list[str], timeout: int, unity: bool = False) -> dict:
    require(not shadow_unity(), "Shadow-project Unity is already running before " + name)
    log = RUN_ROOT / (name + ".log")
    before_logs = set((PROJECT / "_temp").glob("UnityExec_*.log"))
    started = time.time()
    print(time.strftime("%Y-%m-%d %H:%M:%S") + " START " + name, flush=True)
    with log.open("xb") as stream:
        completed = subprocess.run(command, cwd=PROJECT, stdin=subprocess.DEVNULL,
                                   stdout=stream, stderr=subprocess.STDOUT, timeout=timeout)
    require(completed.returncode == 0, f"{name} failed with exit {completed.returncode}; log={log}")
    require(not shadow_unity(), name + " returned before its Unity process exited")
    new_logs = sorted(set((PROJECT / "_temp").glob("UnityExec_*.log")) - before_logs)
    require((len(new_logs) == 1) == unity, name + " emitted an unexpected Unity-log inventory: " + repr([str(p) for p in new_logs]))
    result = {
        "name": name,
        "command": command,
        "durationSeconds": time.time() - started,
        "logPath": str(log),
        "logSha256": digest(log),
        "unityLogPath": str(new_logs[0]) if new_logs else "",
        "unityLogSha256": digest(new_logs[0]) if new_logs else "",
    }
    print(time.strftime("%Y-%m-%d %H:%M:%S") + " PASS " + name, flush=True)
    return result


def json_inventory(pattern: str) -> set[Path]:
    return {path.resolve() for path in ROOT.glob(pattern) if path.is_file() and not path.is_symlink()}


def discover(before: set[Path], pattern: str, label: str, predicate) -> Path:
    created = sorted(json_inventory(pattern) - before)
    matches = [path for path in created if predicate(read(path))]
    require(len(matches) == 1, f"Expected one new {label}; created={created!r}, matches={matches!r}")
    return matches[0]


def validate_replay(manifest: Path, baseline: str, development: bool) -> Path:
    receipt = manifest.parent / "m06-editor-replay.json"
    require(receipt.is_file() and not receipt.is_symlink(), "Fixture build emitted no regular replay receipt: " + str(receipt))
    value = read(receipt)
    require(value.get("schemaVersion") == 1 and value.get("milestone") == "M06" and
            value.get("result") == "Passed" and value.get("comparisonPolicy") == "compiler-linked-resource-generation-warmup:1" and
            value.get("fixtureManifestPath") == str(manifest) and value.get("fixtureManifestSha256") == digest(manifest) and
            value.get("baselineBuildId") == baseline and value.get("developmentBuild") is development,
            "Fixture build replay receipt is not bound to this manifest/mode: " + str(receipt))
    manifest_value = read(manifest)
    require(value.get("generationProofPath") == manifest_value.get("generationProofPath") and
            value.get("generationProofSha256") == manifest_value.get("generationProofSha256") and
            len(value.get("fixtures", [])) == 4,
            "Fixture build replay does not cover the exact generation and four fixture variants")
    scratch = Path(value.get("replayScratchPath", ""))
    require(scratch.is_absolute() and scratch == scratch.resolve(strict=True) and scratch.is_dir() and
            not scratch.is_symlink() and scratch.is_relative_to(ROOT), "Replay scratch is missing, aliased or outside the evidence root")
    return receipt


def recover_development_command(manifest: Path, receipt: Path) -> dict:
    log = RUN_ROOT / "development-fixtures.log"
    unity_log = PROJECT / "_temp" / "UnityExec_20260905_155606.log"
    require(log.is_file() and not log.is_symlink() and unity_log.is_file() and not unity_log.is_symlink(),
            "Completed Development fixture logs are missing or aliased")
    wrapper_output = log.read_text(encoding="utf-8-sig")
    require("[SUCCESS] Unity method completed." in wrapper_output and
            "[INFO] Method: AssemblyShadowDemo.Editor.M06Build.BuildFixtures" in wrapper_output and
            "[INFO] Log: " + str(unity_log) in wrapper_output,
            "Development fixture wrapper log does not prove the expected successful Unity method")
    unity_output = unity_log.read_text(encoding="utf-8-sig")
    require("[AssemblyShadow M06] Fixtures: " + str(manifest) + "; replay: " + str(receipt) in unity_output and
            "Exiting batchmode successfully now!" in unity_output,
            "Development fixture Unity log does not bind the recovered manifest/replay success")
    command = [str(PWSH), "-NoLogo", "-NoProfile", "-NonInteractive", "-File",
               str(PROJECT / "_temp" / "Run-M06DevelopmentFixtures-v8.ps1")]
    stat = unity_log.stat()
    started = getattr(stat, "st_birthtime", stat.st_mtime)
    return {
        "name": "development-fixtures", "command": command,
        "durationSeconds": max(0.0, stat.st_mtime - started),
        "logPath": str(log), "logSha256": digest(log),
        "unityLogPath": str(unity_log), "unityLogSha256": digest(unity_log),
        "recoveredAfterOrchestratorPreflightFailure": True,
    }


def recover_unity_command(name: str, command: list[str], method: str) -> dict:
    log = RUN_ROOT / (name + ".log")
    require(log.is_file() and not log.is_symlink(), "Completed stage wrapper log is missing/aliased: " + str(log))
    wrapper_output = log.read_text(encoding="utf-8-sig")
    expected_log_prefix = "[INFO] Log: "
    unity_log_rows = [line[len(expected_log_prefix):].strip() for line in wrapper_output.splitlines()
                      if line.startswith(expected_log_prefix)]
    require("[SUCCESS] Unity method completed." in wrapper_output and
            "[INFO] Project: " + str(PROJECT) in wrapper_output and
            "[INFO] Method: " + method in wrapper_output and len(unity_log_rows) == 1,
            "Completed stage wrapper log does not prove the expected successful Unity method: " + str(log))
    unity_log = Path(unity_log_rows[0])
    require(unity_log.is_absolute() and unity_log == unity_log.resolve(strict=True) and
            unity_log.parent == PROJECT / "_temp" and unity_log.name.startswith("UnityExec_") and
            unity_log.is_file() and not unity_log.is_symlink(),
            "Completed stage Unity log is missing, aliased or outside the project temp root: " + str(unity_log))
    unity_output = unity_log.read_text(encoding="utf-8-sig")
    require("Exiting batchmode successfully now!" in unity_output,
            "Completed stage Unity log does not contain the batchmode success boundary: " + str(unity_log))
    stat = unity_log.stat()
    started = getattr(stat, "st_birthtime", stat.st_mtime)
    return {
        "name": name, "command": command,
        "durationSeconds": max(0.0, stat.st_mtime - started),
        "logPath": str(log), "logSha256": digest(log),
        "unityLogPath": str(unity_log), "unityLogSha256": digest(unity_log),
        "recoveredAfterOrchestratorInterruption": True,
    }


def recover_nonunity_command(name: str, command: list[str]) -> dict:
    log = RUN_ROOT / (name + ".log")
    require(log.is_file() and not log.is_symlink(), "Completed stage log is missing/aliased: " + str(log))
    stat = log.stat()
    started = getattr(stat, "st_birthtime", stat.st_mtime)
    return {
        "name": name, "command": command,
        "durationSeconds": max(0.0, stat.st_mtime - started),
        "logPath": str(log), "logSha256": digest(log),
        "unityLogPath": "", "unityLogSha256": "",
        "recoveredAfterOrchestratorInterruption": True,
    }


def one_existing(pattern: str, label: str, predicate) -> Path | None:
    matches = [path for path in sorted(json_inventory(pattern)) if predicate(read(path))]
    require(len(matches) <= 1, f"Expected at most one existing {label}; matches={matches!r}")
    return matches[0] if matches else None


def main() -> int:
    require(not STATE.exists(), "M06 v8 final continuation receipt already exists")
    for path in (DEVELOPMENT_GENERATION, DEVELOPMENT_ON, PWSH,
                 PROJECT / "_temp" / "Run-M06DevelopmentFixtures-v8.ps1",
                 PROJECT / "_temp" / "Run-M06ReleaseGeneration-v8.ps1",
                 PROJECT / "_temp" / "Run-M06ReleasePlayer-v8.ps1",
                 PROJECT / "_temp" / "Run-M06ReleaseFixtures-v8.ps1",
                 ROOT / "m06-capture-run-players.py",
                 PROJECT / "Tools" / "AssemblyShadow" / "verify-m06-results.py"):
        require(path.exists() and not path.is_symlink(), "Required continuation input is missing/aliased: " + str(path))
    require(read(DEVELOPMENT_GENERATION).get("baselineBuildId") == DEVELOPMENT_BASELINE, "Wrong Development generation")
    require(read(DEVELOPMENT_ON).get("variant") == "NativeOn", "Wrong Development native-ON receipt")
    commands: list[dict] = []
    fixed_logs = {
        "development-fixtures.log", "release-generation.log", "release-player.log",
        "release-fixtures.log", "player-capture.log",
    }
    if RUN_ROOT.exists():
        require(RUN_ROOT.is_dir() and not RUN_ROOT.is_symlink(), "M06 v8 continuation root is not a regular directory")
        inventory = {path.name for path in RUN_ROOT.iterdir()}
        require(all(name in fixed_logs or re.fullmatch(r"strict-verifier(?:-retry[1-9][0-9]*)?\.log",name)
                    for name in inventory) and
                all(path.is_file() and not path.is_symlink() for path in RUN_ROOT.iterdir()),
                "Unexpected M06 v8 continuation recovery inventory: " + repr(sorted(inventory)))
    else:
        RUN_ROOT.mkdir()

    development_fixture = one_existing("M06Fixtures-*/m06-fixtures.json", "v8 Development fixture manifest",
        lambda value: value.get("baselineBuildId") == DEVELOPMENT_BASELINE and value.get("developmentBuild") is True and
        value.get("generationProofPath") == str(DEVELOPMENT_GENERATION))
    if development_fixture is not None:
        development_replay = validate_replay(development_fixture, DEVELOPMENT_BASELINE, True)
        commands.append(recover_development_command(development_fixture, development_replay))
        print(time.strftime("%Y-%m-%d %H:%M:%S") + " RESUME after validated Development fixtures/replay", flush=True)
    else:
        require(not (RUN_ROOT / "development-fixtures.log").exists(),
                "Development fixture log exists without a completed exact fixture/replay output")
        before = json_inventory("M06Fixtures-*/m06-fixtures.json")
        commands.append(run("development-fixtures", [str(PWSH), "-NoLogo", "-NoProfile", "-NonInteractive", "-File",
            str(PROJECT / "_temp" / "Run-M06DevelopmentFixtures-v8.ps1")], 9 * 60 * 60, True))
        development_fixture = discover(before, "M06Fixtures-*/m06-fixtures.json", "Development fixture manifest",
            lambda value: value.get("baselineBuildId") == DEVELOPMENT_BASELINE and value.get("developmentBuild") is True and
            value.get("generationProofPath") == str(DEVELOPMENT_GENERATION))
        development_replay = validate_replay(development_fixture, DEVELOPMENT_BASELINE, True)

    release_generation_command = [str(PWSH), "-NoLogo", "-NoProfile", "-NonInteractive", "-File",
        str(PROJECT / "_temp" / "Run-M06ReleaseGeneration-v8.ps1")]
    release_generation = one_existing("M06Generation-*/m06-generation.json", "v8 Release generation proof",
        lambda value: value.get("baselineBuildId") == RELEASE_BASELINE and value.get("developmentBuild") is False and
        value.get("selectedPlanId") == "P03")
    if release_generation is not None:
        commands.append(recover_unity_command("release-generation", release_generation_command,
            "AssemblyShadowDemo.Editor.M06Build.PrepareGenerationInputs"))
        print(time.strftime("%Y-%m-%d %H:%M:%S") + " RESUME after validated Release generation", flush=True)
    else:
        require(not (RUN_ROOT / "release-generation.log").exists(),
                "Release generation log exists without a completed exact generation proof")
        before = json_inventory("M06Generation-*/m06-generation.json")
        commands.append(run("release-generation", release_generation_command, 9 * 60 * 60, True))
        release_generation = discover(before, "M06Generation-*/m06-generation.json", "Release generation proof",
            lambda value: value.get("baselineBuildId") == RELEASE_BASELINE and value.get("developmentBuild") is False and
            value.get("selectedPlanId") == "P03")

    release_player_command = [str(PWSH), "-NoLogo", "-NoProfile", "-NonInteractive", "-File",
        str(PROJECT / "_temp" / "Run-M06ReleasePlayer-v8.ps1"), "-Generation", str(release_generation)]
    release_player = one_existing("M06PlayerInputs-*/m06-player-build.json", "v8 Release Player receipt",
        lambda value: value.get("baselineBuildId") == RELEASE_BASELINE and value.get("variant") == "NativeOn" and
        value.get("developmentBuild") is False and value.get("generationProofPath") == str(release_generation))
    if release_player is not None:
        commands.append(recover_unity_command("release-player", release_player_command,
            "AssemblyShadowDemo.Editor.M06Build.BuildReleasePlayerBaseline"))
        print(time.strftime("%Y-%m-%d %H:%M:%S") + " RESUME after validated Release Player", flush=True)
    else:
        require(not (RUN_ROOT / "release-player.log").exists(),
                "Release Player log exists without a completed exact Player receipt")
        before = json_inventory("M06PlayerInputs-*/m06-player-build.json")
        commands.append(run("release-player", release_player_command, 9 * 60 * 60, True))
        release_player = discover(before, "M06PlayerInputs-*/m06-player-build.json", "Release Player receipt",
            lambda value: value.get("baselineBuildId") == RELEASE_BASELINE and value.get("variant") == "NativeOn" and
            value.get("developmentBuild") is False and value.get("generationProofPath") == str(release_generation))

    release_fixture_command = [str(PWSH), "-NoLogo", "-NoProfile", "-NonInteractive", "-File",
        str(PROJECT / "_temp" / "Run-M06ReleaseFixtures-v8.ps1"), "-Generation", str(release_generation)]
    release_fixture = one_existing("M06Fixtures-*/m06-fixtures.json", "v8 Release fixture manifest",
        lambda value: value.get("baselineBuildId") == RELEASE_BASELINE and value.get("developmentBuild") is False and
        value.get("generationProofPath") == str(release_generation))
    if release_fixture is not None:
        release_replay = validate_replay(release_fixture, RELEASE_BASELINE, False)
        commands.append(recover_unity_command("release-fixtures", release_fixture_command,
            "AssemblyShadowDemo.Editor.M06Build.BuildFixtures"))
        print(time.strftime("%Y-%m-%d %H:%M:%S") + " RESUME after validated Release fixtures/replay", flush=True)
    else:
        require(not (RUN_ROOT / "release-fixtures.log").exists(),
                "Release fixture log exists without a completed exact fixture/replay output")
        before = json_inventory("M06Fixtures-*/m06-fixtures.json")
        commands.append(run("release-fixtures", release_fixture_command, 9 * 60 * 60, True))
        release_fixture = discover(before, "M06Fixtures-*/m06-fixtures.json", "Release fixture manifest",
            lambda value: value.get("baselineBuildId") == RELEASE_BASELINE and value.get("developmentBuild") is False and
            value.get("generationProofPath") == str(release_generation))
        release_replay = validate_replay(release_fixture, RELEASE_BASELINE, False)

    native_off_candidates = [path for path in json_inventory("M06PlayerInputs-*/m06-player-build.json")
        if read(path).get("baselineBuildId") == DEVELOPMENT_BASELINE and read(path).get("variant") == "NativeOff" and
        read(path).get("developmentBuild") is True and read(path).get("generationProofPath") == str(DEVELOPMENT_GENERATION)]
    require(len(native_off_candidates) == 1, "Expected exactly one M06 v8 Development native-OFF receipt")
    development_off = native_off_candidates[0]

    player_capture_command = [sys.executable, str(ROOT / "m06-capture-run-players.py"),
        "--fixture-manifest", str(development_fixture), "--on-build", str(DEVELOPMENT_ON),
        "--off-build", str(development_off), "--release-fixture-manifest", str(release_fixture),
        "--release-build", str(release_player), "--output-root", str(RESULT_ROOT), "--timeout", "1800"]
    if RESULT_ROOT.exists():
        require(RESULT_ROOT.is_dir() and not RESULT_ROOT.is_symlink(), "M06 result root is not a regular directory")
        launches = read(RESULT_ROOT / "player-launches.json")
        require(launches.get("completedModes") == 28 and launches.get("inputsUnchanged") is True and
                all(row.get("passed") is True for row in launches.get("processLaunches", [])),
                "Existing M06 28-process capture is incomplete or failed")
        commands.append(recover_nonunity_command("player-capture", player_capture_command))
        print(time.strftime("%Y-%m-%d %H:%M:%S") + " RESUME after validated 28-process Player capture", flush=True)
    else:
        require(not (RUN_ROOT / "player-capture.log").exists(),
                "Player capture log exists without a completed exact result root")
        commands.append(run("player-capture", player_capture_command, 16 * 60 * 60))
        launches = read(RESULT_ROOT / "player-launches.json")
    require(launches.get("completedModes") == 28 and launches.get("inputsUnchanged") is True and
            all(row.get("passed") is True for row in launches.get("processLaunches", [])), "M06 28-process capture failed")

    strict_command = [sys.executable, str(PROJECT / "Tools" / "AssemblyShadow" / "verify-m06-results.py"),
        "--fixture-manifest", str(development_fixture), "--on-build", str(DEVELOPMENT_ON),
        "--off-build", str(development_off), "--release-fixture-manifest", str(release_fixture),
        "--release-build", str(release_player), "--results", str(RESULT_ROOT / "Results"),
        "--m01-baseline-root", str(PROJECT / "BaselineArtifacts" / "StandaloneOSX" / "M01-Baseline-v1"),
        "--output", str(STRICT)]
    strict_logs = []
    for path in RUN_ROOT.glob("strict-verifier*.log"):
        match = re.fullmatch(r"strict-verifier(?:-retry([1-9][0-9]*))?\.log",path.name)
        require(match is not None,"Unexpected strict-verifier log: " + str(path))
        strict_logs.append((int(match.group(1)) if match.group(1) else 0,path))
    strict_logs.sort()
    require([number for number,_ in strict_logs]==list(range(len(strict_logs))),
            "Strict-verifier retry logs are not contiguous")
    if STRICT.exists():
        strict = read(STRICT)
        require(strict.get("result") == "Passed" and strict.get("caseCount") == 28,
                "Existing M06 strict verifier receipt did not pass 28 cases")
        require(strict_logs,"Strict verifier receipt exists without its command log")
        commands.append(recover_nonunity_command(strict_logs[-1][1].stem, strict_command))
        print(time.strftime("%Y-%m-%d %H:%M:%S") + " RESUME after validated strict verifier", flush=True)
    else:
        attempt=len(strict_logs)
        strict_name="strict-verifier" if attempt==0 else "strict-verifier-retry"+str(attempt)
        commands.append(run(strict_name, strict_command, 5 * 60 * 60))
        strict = read(STRICT)
    require(strict.get("result") == "Passed" and strict.get("caseCount") == 28, "M06 strict verifier did not pass 28 cases")

    value = {
        "schemaVersion": 1, "milestone": "M06", "result": "Passed",
        "developmentGeneration": str(DEVELOPMENT_GENERATION), "developmentGenerationSha256": digest(DEVELOPMENT_GENERATION),
        "developmentOn": str(DEVELOPMENT_ON), "developmentOnSha256": digest(DEVELOPMENT_ON),
        "developmentOff": str(development_off), "developmentOffSha256": digest(development_off),
        "developmentFixtureManifest": str(development_fixture), "developmentFixtureManifestSha256": digest(development_fixture),
        "developmentReplay": str(development_replay), "developmentReplaySha256": digest(development_replay),
        "releaseGeneration": str(release_generation), "releaseGenerationSha256": digest(release_generation),
        "releasePlayer": str(release_player), "releasePlayerSha256": digest(release_player),
        "releaseFixtureManifest": str(release_fixture), "releaseFixtureManifestSha256": digest(release_fixture),
        "releaseReplay": str(release_replay), "releaseReplaySha256": digest(release_replay),
        "resultRoot": str(RESULT_ROOT), "launchReceiptSha256": digest(RESULT_ROOT / "player-launches.json"),
        "strictReceipt": str(STRICT), "strictReceiptSha256": digest(STRICT), "commands": commands,
    }
    write_new(STATE, value)
    print(json.dumps({"result": "Passed", "state": str(STATE), "strict": str(STRICT)}, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print("M06 v8 continuation FAILED: " + repr(error), file=sys.stderr, flush=True)
        raise
