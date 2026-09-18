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
        process = subprocess.Popen(command, cwd=project, stdin=subprocess.DEVNULL,
                                   stdout=console, stderr=subprocess.STDOUT)
        print(f"{command[command.index('-shadowR01FailureMode') + 1]} pid={process.pid}", flush=True)
        try:
            exit_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True; process.terminate()
            try:
                exit_code = process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill(); exit_code = process.wait(timeout=15)
    return dict(processId=process.pid, startedAtUnix=started, durationSeconds=time.time()-started,
                exitCode=exit_code, timedOut=timed_out)


def _read_optional(path):
    if not path.is_file() or path.is_symlink():
        return None, "Missing result: " + str(path)
    try:
        value = gate.read(path)
        return value, ""
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        return None, str(error)


def _hash_optional(path):
    return gate.digest(path) if path.is_file() and not path.is_symlink() else ""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("project-root", "fixture-manifest", "on-build", "off-build", "replay-receipt",
                 "failure-fixtures", "negative-input", "output-root"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)
    require(1 <= args.timeout <= 3600, "Use a bounded Player timeout")

    keys = ("projectRoot", "fixtureManifestPath", "onBuildReceiptPath", "offBuildReceiptPath",
            "replayReceiptPath", "failureFixturesPath", "negativeInputPath")
    values = (args.project_root, args.fixture_manifest, args.on_build, args.off_build,
              args.replay_receipt, args.failure_fixtures, args.negative_input)
    paths = {key: gate.canonical(str(value), value, key, key == "projectRoot")
             for key, value in zip(keys, values)}

    output = args.output_root
    require(output.is_absolute() and output == output.resolve() and not output.exists() and
            not output.is_symlink() and output.parent == paths["projectRoot"] / "_temp/AssemblyShadow",
            "Output must be a fresh direct child of project _temp/AssemblyShadow")

    prepared = gate.prepare(*(paths[key] for key in keys))

    # The earliest-startup callback must authenticate the complete failure input
    # graph without consuming the failure transaction. A Baseline capsule is
    # therefore used as an admission-only transport; a deterministic per-mode
    # binding file makes the three capsules non-interchangeable.
    output.mkdir()
    result_dir = output / "Results"; result_dir.mkdir()
    admission_dir = output / "EarlyAdmission"; admission_dir.mkdir()
    admissions = gate.materialize_admission_inputs(prepared, paths, admission_dir)

    inventory = set(prepared["inventory"])
    for row in admissions.values():
        inventory.add(row["bindingPath"])
        inventory.add(row["capsulePath"])
    before = {str(path): gate.digest(path) for path in sorted(inventory)}

    launches = []
    for mode in gate.MODES:
        admission = admissions[mode]
        result_path = result_dir / (mode + ".json")
        early_result = result_dir / (mode + ".early.json")
        log = output / (mode + ".unity.log")
        console = output / (mode + ".console.log")
        command = gate.command_for(prepared, mode, paths, admission["capsulePath"],
                                   early_result, result_path, log)
        row = run_one(command, paths["projectRoot"], console, args.timeout)

        early_outcome, early_error = _read_optional(early_result)
        outcome, result_error = _read_optional(result_path)
        expected_guid = prepared["context"]["on"]["player"]["buildGuid"]
        early_passed = (
            early_outcome is not None and
            early_outcome.get("result") == "Passed" and
            early_outcome.get("mode") == gate.EARLY_ADMISSION_MODE and
            early_outcome.get("callbackReturnCode") == 0 and
            early_outcome.get("processId") == row["processId"] and
            early_outcome.get("capsulePath") == str(admission["capsulePath"]) and
            early_outcome.get("capsuleSha256") == admission["capsuleSha256"]
        )
        result_passed = (
            outcome is not None and
            outcome.get("result") == "Passed" and
            outcome.get("mode") == mode and
            outcome.get("processId") == row["processId"] and
            outcome.get("buildGuid") == expected_guid
        )
        passed = (row["exitCode"] == 0 and not row["timedOut"] and early_passed and result_passed)
        error = ""
        if not early_passed:
            error = early_error or (early_outcome or {}).get("error", "Early admission result mismatch")
        elif not result_passed:
            error = result_error or (outcome or {}).get("error", "Failure/publication result mismatch")

        launches.append(dict(
            row,
            mode=mode,
            command=command,
            passed=passed,
            earlyBindingPath=str(admission["bindingPath"]),
            earlyBindingSha256=admission["bindingSha256"],
            capsulePath=str(admission["capsulePath"]),
            capsuleSha256=admission["capsuleSha256"],
            earlyResultPath=str(early_result),
            earlyResultSha256=_hash_optional(early_result),
            resultPath=str(result_path),
            resultSha256=_hash_optional(result_path),
            logPath=str(log),
            logSha256=_hash_optional(log),
            consolePath=str(console),
            consoleSha256=_hash_optional(console),
            error=error,
        ))

    after = {str(path): gate.digest(path) for path in sorted(inventory)}
    receipt = dict(
        schemaVersion=2,
        kind="R01FailureLaunches",
        **{key: str(value) for key, value in paths.items()},
        sourcePins=prepared["context"]["sourcePins"],
        modes=list(gate.MODES),
        processLaunches=launches,
        resultDirectory=str(result_dir),
        capsuleDirectory=str(admission_dir),
        inputHashesBefore=before,
        inputHashesAfter=after,
        inputsUnchanged=before == after,
    )
    (output / "r01-failure-launches.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return int(before != after or not all(row["passed"] for row in launches))


if __name__ == "__main__":
    raise SystemExit(main())
