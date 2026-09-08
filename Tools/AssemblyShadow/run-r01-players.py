#!/usr/bin/env python3
"""Launch the bounded R01 matrix in fresh, provenance-bound Player processes.

The launcher is diagnostic infrastructure.  ``verify-r01-results.py`` is the
strict gate and independently rechecks every immutable input and result.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import time
from pathlib import Path

from r01_results import MODES, OFF_MODE, STARTUP_EARLY_GUARD, STARTUP_EXPECTATIONS, require_r01_inputs
from r00_player_inputs import verify_inputs
from shadow_tools import require


def _load_m07_runner():
    path = Path(__file__).with_name("run-m07-players.py")
    spec = importlib.util.spec_from_file_location("m07_player_runner_r01_launch", path)
    require(spec is not None and spec.loader is not None, "Cannot load M07 launcher helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _canonical_file(value: str | Path) -> Path:
    path = Path(value)
    require(path.is_absolute() and path == path.resolve(strict=True) and path.is_file() and
            not path.is_symlink(), "Expected canonical input file: " + str(value))
    return path


def _canonical_project(value: Path) -> Path:
    path = value.resolve(strict=True)
    require(path.is_dir() and not path.is_symlink() and
            (path / "Assets/AssemblyShadowDemo").is_dir(),
            "Project is not the Assembly Shadow demo: " + str(path))
    return path


def _new_output(value: Path, project: Path) -> Path:
    root = value if value.is_absolute() else (Path.cwd() / value)
    root = root.resolve()
    parent = (project / "_temp/AssemblyShadow").resolve(strict=True)
    require(not (project / "_temp/AssemblyShadow").is_symlink() and value.is_absolute() and
            root.parent == parent and not root.exists() and not root.is_symlink(),
            "Output root must be a new direct child of " + str(parent))
    return root


def _read_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(type(value) is dict, "Expected JSON object: " + str(path))
    return value


def _run_one(command: list[str], cwd: Path, console_path: Path, timeout: int) -> dict:
    started = time.time()
    timed_out = False
    with console_path.open("xb") as console:
        process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL,
                                   stdout=console, stderr=subprocess.STDOUT)
        print(f"{command[command.index('-shadowR01Mode') + 1]} started pid={process.pid}", flush=True)
        try:
            exit_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.terminate()
            try:
                exit_code = process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                exit_code = process.wait(timeout=15)
    return {"process": process, "processId": process.pid, "exitCode": exit_code,
            "timedOut": timed_out, "startedAtUnix": started,
            "durationSeconds": time.time() - started}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--fixture-manifest", required=True, type=_canonical_file)
    parser.add_argument("--on-build", required=True, type=_canonical_file)
    parser.add_argument("--off-build", required=True, type=_canonical_file)
    parser.add_argument("--replay-receipt", required=True, type=_canonical_file)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--mode", action="append", choices=MODES)
    parser.add_argument("--startup-expectation", choices=STARTUP_EXPECTATIONS,
                        default=STARTUP_EARLY_GUARD)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)

    project = _canonical_project(args.project_root)
    output_root = _new_output(args.output_root, project)
    require(1 <= args.timeout <= 3600, "Use a bounded 1-3600 second timeout per Player")
    modes = list(args.mode or MODES)
    require(len(modes) == len(set(modes)), "Duplicate R01 modes are not allowed")
    require(modes == list(MODES), "Strict R01 launcher requires the complete ordered mode inventory")

    # This is the inherited R00/M07 input gate.  It checks source pairing,
    # managed-input identity, ON/OFF artifacts, replay, and all fixture hashes
    # before any Player process starts.
    context = verify_inputs(project, args.fixture_manifest, args.on_build,
                            args.off_build, args.replay_receipt)
    require_r01_inputs(context)
    m07 = _load_m07_runner()
    immutable = m07.collect_inputs(args.fixture_manifest, args.replay_receipt,
                                   (args.on_build, args.off_build))
    before = {str(path): m07.digest(path) for path in sorted(immutable)}

    output_root.mkdir()
    result_dir = output_root / "Results"
    result_dir.mkdir()
    launches: list[dict] = []
    for mode in modes:
        build = context["off"] if mode == OFF_MODE else context["on"]
        executable = m07.executable_for(build["output"])
        receipt_path = Path(build["path"])
        snapshot_receipt = Path(build["player"]["inputSnapshot"]) / "assembly-snapshot.json"
        result_path = result_dir / ("r01-" + mode + ".json")
        log_path = output_root / (mode + ".unity.log")
        console_path = output_root / (mode + ".console.log")
        command = [str(executable), "-batchmode", "-nographics",
                   "-shadowR01Mode", mode,
                   "-shadowR01StartupExpectation", args.startup_expectation,
                   "-shadowR01SnapshotReceiptSha256", m07.digest(snapshot_receipt),
                   "-shadowM07Fixtures", str(args.fixture_manifest),
                   "-shadowM07PlayerReceipt", str(receipt_path),
                   "-shadowR01Result", str(result_path), "-logFile", str(log_path)]
        run = _run_one(command, project, console_path, args.timeout)
        outcome = None
        error = ""
        if result_path.is_file():
            try:
                outcome = _read_object(result_path)
            except (OSError, ValueError, json.JSONDecodeError) as problem:
                error = str(problem)
        passed = (not run["timedOut"] and run["exitCode"] == 0 and outcome is not None and
                  outcome.get("mode") == mode and outcome.get("result") == "Passed" and
                  outcome.get("processId") == run["processId"] and
                  outcome.get("buildGuid") == build["player"]["buildGuid"] and
                  outcome.get("startupExpectation") == args.startup_expectation)
        launches.append({
            "mode": mode, "command": command, "processId": run["processId"],
            "startedAtUnix": run["startedAtUnix"], "durationSeconds": run["durationSeconds"],
            "exitCode": run["exitCode"], "timedOut": run["timedOut"], "passed": passed,
            "resultPath": str(result_path),
            "resultSha256": m07.digest(result_path) if result_path.is_file() else "",
            "logPath": str(log_path), "consolePath": str(console_path),
            "error": error or (outcome or {}).get("error", "No result file"),
        })
        print(f"{mode} {'Passed' if passed else 'FAILED'} exit={run['exitCode']}", flush=True)

    after = {str(path): m07.digest(path) for path in sorted(immutable)}
    launch_receipt = {
        "schemaVersion": 1, "milestone": "M07R-R01", "diagnosticOnly": args.startup_expectation != STARTUP_EARLY_GUARD,
        "startupExpectation": args.startup_expectation,
        "fullModeInventory": list(MODES), "requestedModes": modes,
        "completedModes": len(launches), "processLaunches": launches,
        "projectRoot": str(project), "fixtureManifestPath": str(args.fixture_manifest),
        "onBuildReceiptPath": str(args.on_build), "offBuildReceiptPath": str(args.off_build),
        "replayReceiptPath": str(args.replay_receipt), "sourcePins": context["sourcePins"],
        "resultDirectory": str(result_dir), "inputHashesBefore": before,
        "inputHashesAfter": after, "inputsUnchanged": before == after,
        "note": "Launch receipt is provenance; verify-r01-results.py is the strict gate.",
    }
    receipt = output_root / "r01-player-launches.json"
    with receipt.open("x", encoding="utf-8") as stream:
        json.dump(launch_receipt, stream, indent=2)
        stream.write("\n")
    return int(len(launches) != len(modes) or not all(row["passed"] for row in launches) or before != after)


if __name__ == "__main__":
    raise SystemExit(main())
