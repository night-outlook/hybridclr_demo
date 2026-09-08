#!/usr/bin/env python3
"""Launch three fresh R01 failure/publication Players after complete input admission."""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

import r01_failure_results as gate
from shadow_tools import require


def run_one(command, project, console_path, timeout):
    started = time.time(); timed_out = False
    with console_path.open("xb") as console:
        process = subprocess.Popen(command, cwd=project, stdin=subprocess.DEVNULL, stdout=console, stderr=subprocess.STDOUT)
        print(f"{command[command.index('-shadowR01FailureMode') + 1]} pid={process.pid}", flush=True)
        try:
            exit_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True; process.terminate()
            try: exit_code = process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill(); exit_code = process.wait(timeout=15)
    return dict(processId=process.pid, startedAtUnix=started, durationSeconds=time.time()-started,
                exitCode=exit_code, timedOut=timed_out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("project-root", "fixture-manifest", "on-build", "off-build", "replay-receipt", "failure-fixtures", "negative-input", "output-root"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)
    require(1 <= args.timeout <= 3600, "Use a bounded Player timeout")
    keys = ("projectRoot", "fixtureManifestPath", "onBuildReceiptPath", "offBuildReceiptPath", "replayReceiptPath", "failureFixturesPath", "negativeInputPath")
    values = (args.project_root, args.fixture_manifest, args.on_build, args.off_build, args.replay_receipt, args.failure_fixtures, args.negative_input)
    paths = {key: gate.canonical(str(value), value, key, key == "projectRoot") for key, value in zip(keys, values)}
    output = args.output_root
    require(output.is_absolute() and output == output.resolve() and not output.exists() and not output.is_symlink() and
            output.parent == paths["projectRoot"] / "_temp/AssemblyShadow", "Output must be a fresh direct child of project _temp/AssemblyShadow")
    prepared = gate.prepare(*(paths[key] for key in keys))
    before = {str(path): gate.digest(path) for path in sorted(prepared["inventory"])}
    output.mkdir(); result_dir = output / "Results"; result_dir.mkdir()
    launches = []
    for mode in gate.MODES:
        result_path = result_dir / (mode + ".json")
        log = output / (mode + ".unity.log"); console = output / (mode + ".console.log")
        command = gate.command_for(prepared, mode, paths, result_path, log)
        row = run_one(command, paths["projectRoot"], console, args.timeout)
        passed, error = False, ""
        try:
            outcome = gate.read(result_path)
            passed = (row["exitCode"] == 0 and not row["timedOut"] and outcome["result"] == "Passed" and
                outcome["mode"] == mode and outcome["processId"] == row["processId"] and outcome["buildGuid"] == prepared["context"]["on"]["player"]["buildGuid"])
            if not passed: error = outcome.get("error", "Player result mismatch")
        except (OSError, ValueError, KeyError) as problem: error = str(problem)
        launches.append(dict(row, mode=mode, command=command, passed=passed, error=error, resultPath=str(result_path),
            resultSha256=gate.digest(result_path) if result_path.is_file() else "", logPath=str(log), consolePath=str(console)))
    after = {str(path): gate.digest(path) for path in sorted(prepared["inventory"])}
    receipt = dict(schemaVersion=1, kind="R01FailureLaunches", **{key: str(value) for key, value in paths.items()},
        sourcePins=prepared["context"]["sourcePins"], modes=list(gate.MODES), processLaunches=launches, resultDirectory=str(result_dir),
        inputHashesBefore=before, inputHashesAfter=after, inputsUnchanged=before == after)
    (output / "r01-failure-launches.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return int(before != after or not all(row["passed"] for row in launches))


if __name__ == "__main__":
    raise SystemExit(main())
