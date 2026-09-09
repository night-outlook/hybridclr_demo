#!/usr/bin/env python3
"""Launch bounded R01 early-startup probes in fresh, provenance-bound Players.

The default matrix excludes Baseline because its post-startup handoff receipt is
still a separate integration milestone.  Use repeated ``--mode`` arguments for
an explicit diagnostic subset; the resulting receipt is never a full R01 claim.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

import r01_early_capsule as capsule
import r01_early_results as gate
from shadow_tools import require, VerificationError


def _canonical_project(value: Path) -> Path:
    require(value.is_absolute() and not value.is_symlink() and value == value.resolve(strict=True),
            "Project must be a canonical absolute path")
    path = value.resolve(strict=True)
    require(path.is_dir() and not path.is_symlink() and (path / "Assets/AssemblyShadowDemo").is_dir(),
            "Project is not the Assembly Shadow demo: " + str(path))
    return path


def _canonical_file(value: Path) -> Path:
    value = Path(value)
    require(value.is_absolute() and not value.is_symlink() and value == value.resolve(strict=True),
            "Input must be a canonical absolute path")
    path = value.resolve(strict=True)
    require(path.is_file() and not path.is_symlink(), "Expected canonical input file: " + str(value))
    return path


def _new_output(value: Path, project: Path) -> Path:
    root = value.resolve()
    parent = (project / "_temp/AssemblyShadow").resolve(strict=True)
    require(value.is_absolute() and root == value and not root.exists() and not value.is_symlink(),
            "Output root must be a new canonical absolute path")
    require(root.parent == parent and not parent.is_symlink(),
            "Output root must be a new direct child of " + str(parent))
    return root


def _run_one(command: list[str], project: Path, console: Path, timeout: int) -> dict:
    started = time.time()
    timed_out = False
    with console.open("xb") as stream:
        process = subprocess.Popen(command, cwd=project, stdin=subprocess.DEVNULL,
                                   stdout=stream, stderr=subprocess.STDOUT)
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
    return {"processId": process.pid, "startedAtUnix": started,
            "durationSeconds": time.time() - started, "exitCode": exit_code,
            "timedOut": timed_out}


def _read(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise ValueError(str(error)) from error
    require(type(value) is dict, "Expected JSON object: " + str(path))
    return value


def _verify_process_output(probe: dict, run: dict, m07_mode: str, profile: int) -> None:
    """A receipt written before a crash is not a successful startup refusal."""
    mode = probe["mode"]
    require(profile in (1, 2), mode + ": unsupported prepared metadata profile")
    require(run["timedOut"] is False, mode + ": Player timed out")
    gate.exact(run["exitCode"], 1 if mode in gate.REJECTION_MODES else 0, mode + ".exitCode")
    gate.verify_startup_logs(mode, probe["logPath"], probe["consolePath"])
    early = gate.verify_early_receipt(probe["earlyResultPath"], probe["capsulePath"], mode,
                                      run["processId"], profile)
    if mode in gate.POSITIVE_MODES:
        result = _read(probe["m07ResultPath"])
        gate.exact(result["processId"], run["processId"], mode + ".m07PID")
        gate.exact(result["mode"], m07_mode, mode + ".m07Mode")
        gate.exact(result["result"], "Passed", mode + ".m07Result")
        gate.verify_imported_snapshots(early, result)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--fixture-manifest", required=True, type=_canonical_file)
    parser.add_argument("--on-build", required=True, type=_canonical_file)
    parser.add_argument("--off-build", required=True, type=_canonical_file)
    parser.add_argument("--replay-receipt", required=True, type=_canonical_file)
    parser.add_argument("--failure-fixtures", type=_canonical_file)
    parser.add_argument("--negative-input", type=_canonical_file)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--m07-mode", choices=[mode for mode in gate.m07.MODES if mode != "T07-14-FeatureOff"],
                        default=gate.DEFAULT_M07_MODE,
                        help="Existing ON M07 mode for an explicit Control-only replay")
    parser.add_argument("--mode", action="append", choices=gate.MODES,
                        help="Explicit diagnostic subset; repeat to add modes")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)

    project = _canonical_project(args.project_root)
    fixture = _canonical_file(args.fixture_manifest)
    on = _canonical_file(args.on_build)
    off = _canonical_file(args.off_build)
    replay = _canonical_file(args.replay_receipt)
    failure_path = _canonical_file(args.failure_fixtures) if args.failure_fixtures else None
    negative_path = _canonical_file(args.negative_input) if args.negative_input else None
    modes = list(args.mode or gate.DEFAULT_MODES)
    require(modes == list(dict.fromkeys(modes)), "Duplicate R01 early modes are not allowed")
    if args.m07_mode != gate.DEFAULT_M07_MODE:
        require(modes == ["Control"], "--m07-mode alternatives are valid only for an explicit Control launch")
    require(1 <= args.timeout <= 3600, "Use a bounded 1-3600 second timeout per Player")
    prepared = gate._prepare(project, fixture, on, off, replay, failure_path, negative_path, modes)

    output = _new_output(args.output_root, project)
    output.mkdir()
    rows = []
    capsule_paths: list[Path] = []
    probes: list[dict] = []
    # Materialize every capsule before taking the immutable-input baseline so
    # each process row is checked against the same complete input graph.
    for mode in modes:
        mode_dir = output / mode
        mode_dir.mkdir()
        capsule_path = mode_dir / "r01-early.capsule"
        patch_id = gate.m07.MODE_PATCH[args.m07_mode] if mode == "Control" else "P03"
        gate._capsule_for(prepared, mode, fixture, capsule_path, patch_id)
        capsule_paths.append(capsule_path)
        early_result = mode_dir / "r01-early.json"
        m07_result = mode_dir / ("m07-" + args.m07_mode + ".json") if mode in gate.POSITIVE_MODES else None
        log_path = mode_dir / "unity.log"
        console_path = mode_dir / "console.log"
        command = gate.command_for(prepared, mode, fixture, on, capsule_path, early_result,
                                   m07_result or mode_dir / "unused-m07.json", log_path, args.m07_mode)
        probes.append(dict(mode=mode, capsulePath=capsule_path, earlyResultPath=early_result,
                           m07ResultPath=m07_result, logPath=log_path, consolePath=console_path,
                           command=command))

    immutable = set(prepared["inventory"]) | set(capsule_paths)
    matrix_before = {str(path): gate.digest(path) for path in sorted(immutable)}
    for probe in probes:
        mode = probe["mode"]
        capsule_path = probe["capsulePath"]
        early_result = probe["earlyResultPath"]
        m07_result = probe["m07ResultPath"]
        log_path = probe["logPath"]
        console_path = probe["consolePath"]
        command = probe["command"]
        before = {str(path): gate.digest(path) for path in sorted(immutable)}
        run = _run_one(command, project, console_path, args.timeout)
        after = {str(path): gate.digest(path) for path in sorted(immutable)}
        error = ""
        try:
            _verify_process_output(probe, run, args.m07_mode, prepared["profile"])
            require(before == after == matrix_before, mode + ": immutable inputs changed")
            producer_ok = True
        except (VerificationError, ValueError, OSError, KeyError, TypeError) as problem:
            error = str(problem)
            producer_ok = False
        rows.append({"mode": mode, "command": command, **run, "passed": producer_ok,
                     "capsulePath": str(capsule_path), "capsuleSha256": gate.digest(capsule_path),
                     "earlyResultPath": str(early_result),
                     "earlyResultSha256": gate.digest(early_result) if early_result.is_file() else "",
                     "m07ResultPath": str(m07_result) if m07_result is not None and m07_result.is_file() else "",
                     "m07ResultSha256": gate.digest(m07_result) if m07_result is not None and m07_result.is_file() else "",
                     "logPath": str(log_path), "logSha256": gate.digest(log_path) if log_path.is_file() else "",
                     "consolePath": str(console_path), "consoleSha256": gate.digest(console_path) if console_path.is_file() else "",
                     "inputHashesBefore": before, "inputHashesAfter": after,
                     "inputsUnchanged": before == after,
                     "error": error})
        print(f"{mode} {'Passed' if producer_ok else 'FAILED'} exit={run['exitCode']}", flush=True)

    before_all = matrix_before
    after_all = {str(path): gate.digest(path) for path in sorted(immutable)}
    launch = {
        "schemaVersion": 1, "kind": gate.LAUNCH_KIND,
        "projectRoot": str(project), "fixtureManifestPath": str(fixture),
        "onBuildReceiptPath": str(on), "offBuildReceiptPath": str(off),
        "replayReceiptPath": str(replay), "failureFixturesPath": str(failure_path or ""),
        "negativeInputPath": str(negative_path or ""), "sourcePins": prepared["context"]["sourcePins"],
        "m07Mode": args.m07_mode,
        "requestedModes": modes, "fullModeInventory": list(gate.MODES),
        "completedModes": len(rows), "processLaunches": rows,
        "resultDirectory": str(output), "inputHashesBefore": before_all,
        "inputHashesAfter": after_all, "inputsUnchanged": before_all == after_all,
        # Baseline's post-startup handoff is not part of this runner yet; even
        # the default bounded matrix is therefore explicitly diagnostic.
        "diagnosticOnly": True,
        "note": "Launch receipt is provenance; r01_early_results.py is the strict gate.",
    }
    launch_path = output / "r01-early-launches.json"
    with launch_path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(launch, stream, indent=2)
        stream.write("\n")
    return int(not all(row["passed"] and row["inputsUnchanged"] for row in rows) or not launch["inputsUnchanged"])


if __name__ == "__main__":
    raise SystemExit(main())
