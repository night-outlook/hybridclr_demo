#!/usr/bin/env python3
"""Run each R00 observation in a fresh, hash-bound IL2CPP Player process."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import time

from r00_player_inputs import verify_inputs
from r00_results import MODES, OFF_MODE, validate_strategy_profile
import r01_early_results as early

_m07_path = Path(__file__).with_name("run-m07-players.py")
if not _m07_path.is_file():
    _m07_path = Path.cwd() / "Tools/AssemblyShadow/run-m07-players.py"
_spec = importlib.util.spec_from_file_location("m07_player_runner", _m07_path)
m07 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m07)


def output_paths(results: Path, mode: str) -> tuple[Path, Path, Path]:
    """Keep all per-mode outputs beneath the recorded result directory."""
    mode_dir = results / mode
    return results / (mode + ".json"), mode_dir, mode_dir / "r01-early.json"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    for name in ("fixture-manifest", "on-build", "off-build", "replay-receipt"):
        parser.add_argument("--" + name, required=True, type=m07.canonical_file)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--early-startup-strategy", choices=("R01EarlyStartup", "legacy-explicit-no-capsule"),
                        default="R01EarlyStartup",
                        help="Generate and bind R01 capsules, or explicitly preserve the historical no-capsule path.")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)
    project = args.project_root
    m07.require(project.is_absolute() and project == project.resolve(strict=True), "Canonical project required")
    output = m07.canonical_new_child(args.output_root, project / "_temp/AssemblyShadow", "R00 output")
    m07.require(1 <= args.timeout <= 3600, "Timeout must be 1-3600 seconds")
    context = verify_inputs(project, args.fixture_manifest, args.on_build, args.off_build, args.replay_receipt)
    inputs = m07.collect_inputs(args.fixture_manifest, args.replay_receipt, (args.on_build, args.off_build))
    legacy = args.early_startup_strategy == "legacy-explicit-no-capsule"
    before = {str(path): m07.digest(path) for path in sorted(inputs)}
    output.mkdir()
    results = output / "Results"
    results.mkdir()
    early_capsules = {}
    if not legacy:
        prepared = early._prepare(project, args.fixture_manifest, args.on_build, args.off_build,
                                  args.replay_receipt, None, None, ["Control", "Baseline"])
        for mode, early_mode, patch_id in (("R00-ON-P01", "Control", "P01"),
                                            ("R00-ON-P03", "Control", "P03"),
                                            ("R00-ON-NoPatch", "Baseline", "P03")):
            mode_dir = results / mode
            mode_dir.mkdir()
            capsule_path = mode_dir / "r01-early.capsule"
            early._capsule_for(prepared, early_mode, args.fixture_manifest, capsule_path, patch_id)
            early_capsules[mode] = capsule_path
        inputs.update(early_capsules.values())
        before = {str(path): m07.digest(path) for path in sorted(inputs)}
    else:
        prepared = early._prepare(project, args.fixture_manifest, args.on_build, args.off_build,
                                  args.replay_receipt, None, None, [])
        validate_strategy_profile(args.early_startup_strategy, prepared["profile"])
    launches = []
    for mode in MODES:
        build = context["off" if mode == OFF_MODE else "on"]["player"]
        receipt = args.off_build if mode == OFF_MODE else args.on_build
        executable = m07.executable_for(Path(build["playerOutput"]))
        result_path, mode_dir, early_result = output_paths(results, mode)
        if not mode_dir.exists():
            mode_dir.mkdir()
        early_capsule = early_capsules.get(mode)
        log = output / (mode + ".unity.log")
        console = output / (mode + ".console.log")
        command = [str(executable), "-batchmode", "-nographics", "-shadowR00Mode", mode,
                   "-shadowM07Fixtures", str(args.fixture_manifest), "-shadowM07PlayerReceipt", str(receipt),
                   "-shadowR00Result", str(result_path), "-logFile", str(log)]
        if early_capsule is not None:
            command.extend(["-shadowEarlyCapsule", str(early_capsule),
                            "-shadowEarlyCapsuleSha256", m07.digest(early_capsule),
                            "-shadowEarlyResult", str(early_result)])
        elif legacy:
            command.extend(["-shadowR00LegacyNoEarlyStartup", "1"])
        started = time.time()
        timed_out = False
        with console.open("xb") as stream:
            process = subprocess.Popen(command, cwd=project, stdin=subprocess.DEVNULL,
                                       stdout=stream, stderr=subprocess.STDOUT)
            print(f"{mode} started pid={process.pid}", flush=True)
            try:
                exit_code = process.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                process.terminate()
                try:
                    exit_code = process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    exit_code = process.wait(timeout=15)
        outcome = None
        error = ""
        if result_path.is_file():
            try:
                outcome = m07.read_object(result_path)
            except (OSError, ValueError) as problem:
                error = str(problem)
        passed = (not timed_out and exit_code == 0 and outcome is not None and
                  outcome.get("mode") == mode and outcome.get("result") == "Passed" and
                  outcome.get("processId") == process.pid and outcome.get("buildGuid") == build["buildGuid"])
        launches.append({"mode": mode, "command": command, "processId": process.pid,
                         "earlyStartupStrategy": args.early_startup_strategy,
                         "earlyCapsulePath": str(early_capsule) if early_capsule is not None else "",
                         "earlyCapsuleSha256": m07.digest(early_capsule) if early_capsule is not None else "",
                         "earlyResultPath": str(early_result) if early_capsule is not None else "",
                         "earlyResultSha256": m07.digest(early_result) if early_capsule is not None and early_result.is_file() else "",
                         "startedAtUnix": started, "durationSeconds": time.time() - started,
                         "exitCode": exit_code, "timedOut": timed_out, "passed": passed,
                         "resultPath": str(result_path), "resultSha256": m07.digest(result_path) if result_path.is_file() else "",
                         "logPath": str(log), "consolePath": str(console),
                         "error": error or (outcome or {}).get("error", "No result file")})
        print(f"{mode} {'Passed' if passed else 'FAILED'} exit={exit_code}", flush=True)
    after = {}
    for path in sorted(inputs):
        try:
            after[str(path)] = m07.digest(path)
        except (OSError, ValueError) as error:
            after[str(path)] = "UNAVAILABLE: " + str(error)
    receipt = {"schemaVersion": 2, "milestone": "R00", "diagnosticOnly": True,
               "projectRoot": str(project), "sourcePins": context["sourcePins"],
               "fixtureManifestPath": str(args.fixture_manifest), "nativeOnReceipt": str(args.on_build),
               "nativeOffReceipt": str(args.off_build), "editorReplayReceipt": str(args.replay_receipt),
               "requestedModes": list(MODES), "processLaunches": launches,
               "earlyStartupStrategy": args.early_startup_strategy,
               "inputHashesBefore": before, "inputHashesAfter": after, "inputsUnchanged": before == after,
               "resultDirectory": str(results)}
    with (output / "r00-player-launches.json").open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    return int(before != after or not all(row["passed"] for row in launches))


if __name__ == "__main__":
    raise SystemExit(main())
