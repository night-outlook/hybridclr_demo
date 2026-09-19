#!/usr/bin/env python3
"""Run one preregistered A/B R00 pair and retain every attempt."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from shadow_tools import VerificationError, read_json, require
import h1_paired_performance as analysis


_m07_spec = importlib.util.spec_from_file_location(
    "h1_pair_m07_runner", Path(__file__).with_name("run-m07-players.py"))
_m07 = importlib.util.module_from_spec(_m07_spec)
_m07_spec.loader.exec_module(_m07)
_r00_spec = importlib.util.spec_from_file_location(
    "h1_pair_r00_results", Path(__file__).with_name("r00_results.py"))
_r00 = importlib.util.module_from_spec(_r00_spec)
_r00_spec.loader.exec_module(_r00)

MODES = tuple(analysis.MODES)
PHASES = ("pilot", "formal")
SIDES = ("A", "B")
RUNNER_PATH = Path(__file__).with_name("run-r00-players.py").resolve()
RUNNER_OVERHEAD_SECONDS = 30


class OwnedProcessGroupError(VerificationError):
    """The owned runner process group could not be proven gone."""


def digest(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "Expected regular file: " + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(path: Path) -> dict[str, str]:
    return {"path": str(path), "sha256": digest(path)}


def runner_binding() -> dict[str, str]:
    return binding(RUNNER_PATH)


def canonical_dir(value: str | Path, label: str) -> Path:
    path = Path(value)
    require(path.is_absolute() and path == path.resolve(strict=True) and path.is_dir() and not path.is_symlink(),
            label + " must be a canonical directory: " + str(value))
    return path


def bound_file(value: Any, label: str) -> tuple[Path, dict[str, str]]:
    require(type(value) is dict, label + " must be an object")
    path = _m07.canonical_file(value.get("path", ""))
    actual = digest(path)
    require(value.get("sha256") == actual, label + " hash mismatch")
    return path, {"path": str(path), "sha256": actual}


def _expected_config(evidence: dict[str, Any], feature: str, label: str) -> None:
    require(evidence.get("result") == "Passed", label + " controlled evidence is not Passed")
    require(evidence.get("provenanceComplete") is True, label + " provenance is incomplete")
    require(evidence.get("feature") == feature, label + " feature mode mismatch")
    effective = evidence.get("effectiveConfiguration")
    require(type(effective) is dict, label + " effective configuration is missing")
    expected = {
        "development": True,
        "scriptingBackend": "IL2CPP",
        "il2CppCompilerConfiguration": "Release",
        "managedStrippingLevel": "Low",
        "il2CppCodeGeneration": "OptimizeSpeed",
        "allowDebugging": False,
        "connectProfiler": False,
        "deepProfiling": False,
        "buildScriptsOnly": False,
    }
    for key, value in expected.items():
        require(effective.get(key) == value, label + " effective configuration mismatch: " + key)


def _validate_protocol(path: Path) -> dict[str, Any]:
    value = read_json(path)
    require(value.get("schemaVersion") == 1 and value.get("kind") == "H1ControlledPerformanceProtocolTemplate",
            "Invalid performance protocol")
    require(value.get("development") is True and value.get("nativeCompilerConfiguration") == "Release" and
            value.get("nativeAssertions") is False, "Protocol is not the Development C++ Release contract")
    require(value.get("unityVersion") == "2022.3.62f2" and value.get("target") == "StandaloneOSX" and
            value.get("architecture") == "arm64", "Protocol platform contract mismatch")
    require(value.get("modes") == list(MODES) and value.get("pilotPairsPerMode") == 1 and
            value.get("formalPairsPerMode") == 10, "Protocol pair inventory mismatch")
    require(value.get("invalidPairPolicy") == "RetainAllAttempts_RepeatWholePair_NoSelectiveOutlierDeletion" and
            value.get("sourceFreezeRequiredBeforeFormalSampling") is True,
            "Protocol retry/source-freeze policy mismatch")
    return value


def _validate_schedule(path: Path, protocol_path: Path, protocol: dict[str, Any]) -> list[dict[str, Any]]:
    value = read_json(path)
    require(value.get("schemaVersion") == 1 and value.get("kind") == "H1ControlledPairSchedule",
            "Invalid performance schedule")
    require(value.get("executionRequiresFrozenBuildMap") is True, "Schedule does not require a frozen build map")
    require(value.get("protocolPath") == str(protocol_path) and value.get("protocolSha256") == digest(protocol_path),
            "Schedule protocol binding mismatch")
    pairs = value.get("pairs")
    require(type(pairs) is list and len(pairs) == 44, "Schedule must contain exactly 44 pairs")
    ids: set[str] = set()
    for row in pairs:
        require(type(row) is dict, "Schedule pair must be an object")
        pair_id, mode, phase, order = row.get("pairId"), row.get("mode"), row.get("phase"), row.get("order")
        require(type(pair_id) is str and pair_id and pair_id not in ids, "Schedule pairId must be unique")
        require(mode in MODES and phase in PHASES and order in (["A", "B"], ["B", "A"]),
                "Schedule pair fields are invalid")
        require(row.get("includedInFormalStatistics") is (phase == "formal"),
                "Schedule formal inclusion differs from phase")
        ids.add(pair_id)
    for mode in MODES:
        rows = [row for row in pairs if row["mode"] == mode]
        require(sum(row["phase"] == "pilot" for row in rows) == 1 and
                sum(row["phase"] == "formal" for row in rows) == 10,
                mode + " schedule count mismatch")
        formal = [row for row in rows if row["phase"] == "formal"]
        require(sum(row["order"] == ["A", "B"] for row in formal) == 5 and
                sum(row["order"] == ["B", "A"] for row in formal) == 5,
                mode + " formal order is not balanced")
    require(protocol.get("modes") == list(MODES), "Protocol and schedule mode order mismatch")
    return pairs


def _validate_build(build_map_path: Path, protocol: dict[str, Any]) -> dict[str, Any]:
    value = read_json(build_map_path)
    require(value.get("schemaVersion") == 1 and value.get("kind") == "H1ControlledBuildMap" and
            value.get("status") == "Frozen", "Build map must be a frozen H1ControlledBuildMap")
    strict = analysis.validate_build_map(value)
    require(strict.get("status") == "ComparabilityPassed",
            "Build map failed strict authenticated comparability: " +
            "; ".join(strict.get("reasons", [])))
    require(value.get("protocolId") == protocol.get("protocolId"), "Build map protocol identity mismatch")
    require(value.get("target") == "StandaloneOSX" and value.get("architecture") == "arm64",
            "Build map platform mismatch")
    configuration = value.get("configuration")
    require(type(configuration) is dict and configuration.get("development") is True and
            configuration.get("nativeCompilerConfiguration") == "Release" and
            configuration.get("nativeAssertions") is False, "Build map configuration is not Development C++ Release")
    comparability = value.get("comparability")
    require(type(comparability) is dict, "Build map comparability is missing")
    for field in ("developmentCppRelease", "unity", "architecture", "strip", "codegen", "startup",
                  "commonMeasurementCoreSha256", "witnessSha256", "runtimeAbiHash", "sourcePins"):
        pair = comparability.get(field)
        require(type(pair) is dict and pair.get("A") not in (None, "") and pair.get("B") not in (None, ""),
                "Build map comparability field is incomplete: " + field)
    for field in ("developmentCppRelease", "unity", "architecture", "strip", "codegen", "startup",
                  "commonMeasurementCoreSha256", "witnessSha256"):
        require(comparability[field]["A"] == comparability[field]["B"],
                "Build map comparability field differs: " + field)
    for field in ("runtimeAbiHash", "sourcePins"):
        require(comparability[field]["A"] != comparability[field]["B"],
                "Build map must bind expected-different field: " + field)

    sides = value.get("sides")
    require(type(sides) is dict and set(sides) == set(SIDES), "Build map must contain exactly A and B sides")
    result: dict[str, Any] = {"map": value, "sides": {}}
    for side in SIDES:
        item = sides[side]
        require(type(item) is dict, "Build map side is invalid: " + side)
        project = canonical_dir(item.get("projectRoot", ""), side + ".projectRoot")
        require((project / "Assets/AssemblyShadowDemo").is_dir(), side + " is not an Assembly Shadow demo")
        manifest, manifest_binding = bound_file(item.get("fixtureManifest"), side + ".fixtureManifest")
        replay, replay_binding = bound_file(item.get("replayReceipt"), side + ".replayReceipt")
        builds = item.get("builds")
        require(type(builds) is dict and set(builds) == {"on", "off"}, side + " must bind ON and OFF builds")
        variants: dict[str, Any] = {}
        for flavor, expected_variant, expected_feature in (("on", "NativeOn", "on"), ("off", "NativeOff", "off")):
            build = builds[flavor]
            require(type(build) is dict, side + "." + flavor + " build is invalid")
            receipt_path, receipt_binding = bound_file(build.get("receipt"), side + "." + flavor + ".receipt")
            receipt = read_json(receipt_path)
            require(receipt.get("schemaVersion") == 1 and receipt.get("milestone") == "M07" and
                    receipt.get("variant") == expected_variant, side + "." + flavor + " M07 receipt mismatch")
            app = canonical_dir(receipt.get("playerOutput", ""), side + "." + flavor + ".playerOutput")
            _m07.executable_for(app)
            evidence_path, evidence_binding = bound_file(build.get("controlledEvidence"),
                                                         side + "." + flavor + ".controlledEvidence")
            evidence = read_json(evidence_path)
            _expected_config(evidence, expected_feature, side + "." + flavor)
            require(evidence.get("actualReceiptPath") == str(receipt_path) and
                    evidence.get("actualReceiptSha256") == digest(receipt_path),
                    side + "." + flavor + " controlled evidence receipt binding mismatch")
            require(evidence.get("buildGuid") == receipt.get("buildGuid") and
                    evidence.get("playerOutput") == receipt.get("playerOutput"),
                    side + "." + flavor + " controlled evidence identity mismatch")
            executable = _m07.executable_for(app)
            require(evidence.get("playerExecutable") == str(executable) and
                    evidence.get("playerExecutableSha256") == digest(executable),
                    side + "." + flavor + " controlled evidence executable binding mismatch")
            require(build.get("feature") == expected_feature and build.get("development") is True and
                    build.get("nativeCompilerConfiguration") == "Release", side + "." + flavor + " declared config mismatch")
            if "buildGuid" in build:
                require(build["buildGuid"] == receipt.get("buildGuid"), side + "." + flavor + " build GUID mismatch")
            if "playerOutput" in build:
                require(build["playerOutput"] == receipt.get("playerOutput"), side + "." + flavor + " output mismatch")
            variants[flavor] = {"receipt": receipt_path, "receiptBinding": receipt_binding,
                                "evidence": evidence_path, "evidenceBinding": evidence_binding,
                                "receiptObject": receipt, "feature": expected_feature}
        result["sides"][side] = {"projectRoot": project, "fixtureManifest": manifest,
                                  "fixtureBinding": manifest_binding, "replayReceipt": replay,
                                  "replayBinding": replay_binding, "builds": variants}
    return result


def _index_bindings(index: dict[str, Any], protocol_path: Path, schedule_path: Path, build_map_path: Path) -> None:
    for key, path in (("protocol", protocol_path), ("schedule", schedule_path), ("buildMap", build_map_path)):
        _, item = bound_file(index.get(key), "prior index " + key)
        require(item == binding(path), "Prior index " + key + " binding mismatch")


def _verify_prior_launch(value: Any, side: dict[str, Any], mode: str, label: str) -> None:
    launch_path, _ = bound_file(value, label + ".launchReceipt")
    launch = read_json(launch_path)
    expected_build = side["builds"]["off" if mode == "R00-OFF-NoPatch" else "on"]["receipt"]
    require(launch.get("projectRoot") == str(side["projectRoot"]) and
            launch.get("fixtureManifestPath") == str(side["fixtureManifest"]) and
            launch.get("nativeOnReceipt") == str(side["builds"]["on"]["receipt"]) and
            launch.get("nativeOffReceipt") == str(side["builds"]["off"]["receipt"]) and
            launch.get("editorReplayReceipt") == str(side["replayReceipt"]),
            label + " launch receipt is not bound to the frozen build map")
    require(expected_build.is_file(), label + " selected M07 receipt is missing")
    verified = _r00.verify_suite(launch_path, expected_mode=mode)
    require(verified.get("result") == "Passed" and verified.get("requestedModeIds") == [mode] and
            verified.get("executedModeIds") == [mode], label + " R00 verification failed")


def _successful_pilots(attempts: list[dict[str, Any]], schedule: list[dict[str, Any]], build: dict[str, Any]) -> set[str]:
    successful = set()
    scheduled = {row["pairId"]: row for row in schedule}
    for row in attempts:
        if row.get("phase") != "pilot" or row.get("status") != "Passed":
            continue
        pair = scheduled.get(row.get("pairId"))
        if pair is None:
            continue
        try:
            for side_name in SIDES:
                require(type(row.get(side_name)) is dict and row[side_name].get("status") == "Passed",
                        "Pilot side is not marked Passed")
                _verify_prior_launch(row[side_name].get("launchReceipt"), build["sides"][side_name],
                                     pair["mode"], "Pilot " + side_name)
            successful.add(row.get("pairId"))
        except (VerificationError, OSError, KeyError, TypeError, ValueError):
            continue
    return {row["pairId"] for row in schedule if row["phase"] == "pilot" and row["pairId"] in successful}


def _load_prior(path: Path | None, protocol_path: Path, schedule_path: Path, build_map_path: Path,
                schedule: list[dict[str, Any]], phase: str, build: dict[str, Any]) -> list[dict[str, Any]]:
    if path is None:
        require(phase == "pilot", "Formal pair requires --prior-index with completed pilots")
        return []
    value = read_json(path)
    require(value.get("schemaVersion") == 1 and value.get("kind") == "H1ControlledSamples",
            "Invalid prior sample index")
    _index_bindings(value, protocol_path, schedule_path, build_map_path)
    attempts = value.get("attempts")
    require(type(attempts) is list, "Prior sample index attempts must be an array")
    seen: set[tuple[str, int]] = set()
    scheduled = {row["pairId"]: row for row in schedule}
    formal_started = False
    for row in attempts:
        require(type(row) is dict and row.get("pairId") in scheduled and type(row.get("attempt")) is int and row["attempt"] > 0,
                "Prior attempt identity is invalid")
        key = (row["pairId"], row["attempt"])
        require(key not in seen, "Prior index contains duplicate attempt: " + str(key))
        seen.add(key)
        require(row.get("phase") == scheduled[row["pairId"]]["phase"] and row.get("mode") == scheduled[row["pairId"]]["mode"],
                "Prior attempt schedule binding mismatch")
        if row["phase"] == "formal":
            formal_started = True
        else:
            require(not formal_started, "Prior pilots must precede formal attempts")
        for side in SIDES:
            require(type(row.get(side)) is dict, "Prior attempt lacks " + side + " diagnostic")
            require(row[side].get("runner") == runner_binding(),
                    "Prior " + side + " diagnostic runner binding mismatch")
            launch_receipt = row[side].get("launchReceipt")
            if launch_receipt is not None:
                bound_file(launch_receipt, "Prior " + side + " launch receipt")
    if phase == "formal":
        pilot_ids = {row["pairId"] for row in schedule if row["phase"] == "pilot"}
        require(_successful_pilots(attempts, schedule, build) == pilot_ids,
                "Formal sampling requires all four completed pilot pair receipts")
    return attempts


def _select_pair(schedule: list[dict[str, Any]], phase: str, pair_id: str | None,
                 prior: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [row for row in schedule if row["phase"] == phase]
    require(rows, "No schedule rows for phase: " + phase)
    if pair_id is not None:
        matches = [row for row in rows if row["pairId"] == pair_id]
        require(len(matches) == 1, "pair-id is not a scheduled row in the selected phase")
        row = matches[0]
    else:
        attempted = {row.get("pairId") for row in prior}
        remaining = [row for row in rows if row["pairId"] not in attempted]
        require(remaining, "No unattempted pair remains in the selected phase")
        row = remaining[0]
    return row


def _safe_name(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_.-]+", "_", value)
    require(result and result not in (".", ".."), "Unsafe output name")
    return result


def build_command(project: Path, mode: str, side: dict[str, Any], output_root: Path, timeout: int) -> list[str]:
    canonical_dir(project, "project")
    script = _m07.canonical_file(RUNNER_PATH)
    on = side["builds"]["on"]["receipt"]
    off = side["builds"]["off"]["receipt"]
    return [sys.executable, str(script), "--project-root", str(project),
            "--fixture-manifest", str(side["fixtureManifest"]), "--on-build", str(on),
            "--off-build", str(off), "--replay-receipt", str(side["replayReceipt"]),
            "--output-root", str(output_root), "--early-startup-strategy", "R01EarlyStartup",
            "--mode", mode, "--timeout", str(timeout)]


def _write_failure_receipt(path: Path, mode: str, error: str) -> None:
    require(not path.exists() and not path.is_symlink(), "Failure receipt must be new")
    value = {"schemaVersion": 2, "milestone": "R00", "result": "Failed", "requestedModes": [mode],
             "processLaunches": [], "error": error, "driverFailure": True}
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def _group_exists(process_id: int) -> bool:
    try:
        os.killpg(process_id, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _wait_group_gone(process_id: int, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while _group_exists(process_id) and time.monotonic() < deadline:
        time.sleep(0.05)
    return not _group_exists(process_id)


def _terminate_owned_group(process_id: int) -> None:
    try:
        os.killpg(process_id, signal.SIGTERM)
    except ProcessLookupError:
        return
    except OSError as error:
        raise OwnedProcessGroupError("Could not terminate owned runner process group: " + str(error)) from error
    if _wait_group_gone(process_id, 15):
        return
    try:
        os.killpg(process_id, signal.SIGKILL)
    except ProcessLookupError:
        return
    except OSError as error:
        raise OwnedProcessGroupError("Could not kill owned runner process group: " + str(error)) from error
    if not _wait_group_gone(process_id, 15):
        raise OwnedProcessGroupError("Owned runner process group did not exit; refusing to launch the other side.")


def _run_side(side_name: str, side: dict[str, Any], mode: str, output_root: Path,
              project_output: Path, timeout: int) -> dict[str, Any]:
    output_root_parent = project_output / "_temp/AssemblyShadow"
    require(output_root_parent.is_dir() and not output_root_parent.is_symlink(),
            side_name + " project output parent is unavailable")
    command = build_command(side["projectRoot"], mode, side, output_root, timeout)
    console = output_root_parent / (output_root.name + "." + side_name + ".driver.console.log")
    started = time.time()
    process = None
    exit_code = -1
    timed_out = False
    error = ""
    cleanup_error = None
    had_launch_receipt = False
    try:
        with console.open("xb") as stream:
            process = subprocess.Popen(command, cwd=side["projectRoot"], stdin=subprocess.DEVNULL,
                                       stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                exit_code = process.wait(timeout=timeout + RUNNER_OVERHEAD_SECONDS)
            except subprocess.TimeoutExpired:
                timed_out = True
                try:
                    _terminate_owned_group(process.pid)
                except OwnedProcessGroupError as problem:
                    cleanup_error = problem
                try:
                    exit_code = process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    exit_code = process.poll()
            if cleanup_error is None and not timed_out and not _wait_group_gone(process.pid, 5):
                cleanup_error = OwnedProcessGroupError(
                    "Runner exited but its owned process group remains; refusing to launch the other side.")
    except (OSError, ValueError) as problem:
        error = str(problem)
    if cleanup_error is not None:
        error = str(cleanup_error)
    ended = time.time()
    duration = ended - started
    launch_path = output_root / "r00-player-launches.json"
    had_launch_receipt = launch_path.is_file()
    if not launch_path.is_file():
        output_root.mkdir(parents=True, exist_ok=True)
        _write_failure_receipt(launch_path, mode, error or ("Player timed out" if timed_out else "R00 runner produced no receipt"))
    launch = read_json(launch_path)
    rows = launch.get("processLaunches")
    row = rows[0] if type(rows) is list and len(rows) == 1 else {}
    passed = (not error and not timed_out and exit_code == 0 and launch.get("milestone") == "R00" and
              launch.get("inputsUnchanged") is True and row.get("mode") == mode and row.get("passed") is True)
    value = {"status": "Passed" if passed else "Failed", "command": command, "cwd": str(side["projectRoot"]),
            "outputRoot": str(output_root),
            "startedAtUnix": started, "finishedAtUnix": ended, "durationSeconds": duration, "exitCode": exit_code,
            "timedOut": timed_out, "launchReceipt": binding(launch_path) if had_launch_receipt else None,
            "consolePath": str(console), "error": error or row.get("error", ""),
            "runner": runner_binding()}
    if process is not None:
        value["processId"] = process.pid
    if cleanup_error is not None:
        value["stopBeforeNextSide"] = True
    return value


def _skipped_side(side_name: str, side: dict[str, Any], mode: str, output_root: Path,
                  error: str, timeout: int) -> dict[str, Any]:
    command = build_command(side["projectRoot"], mode, side, output_root, timeout)
    now = time.time()
    return {"status": "Failed", "command": command, "cwd": str(side["projectRoot"]),
            "outputRoot": str(output_root), "startedAtUnix": now, "finishedAtUnix": now,
            "durationSeconds": 0.0, "exitCode": -1, "timedOut": False,
            "launchReceipt": None, "consolePath": None, "error": error,
            "runner": runner_binding(), "skipped": True}


def _positive(value: str) -> int:
    number = int(value)
    require(number > 0, "attempt and timeout must be positive")
    return number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", required=True, type=_m07.canonical_file)
    parser.add_argument("--schedule", required=True, type=_m07.canonical_file)
    parser.add_argument("--build-map", required=True, type=_m07.canonical_file)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--phase", required=True, choices=PHASES)
    parser.add_argument("--pair-id")
    parser.add_argument("--attempt", required=True, type=_positive)
    parser.add_argument("--prior-index", type=_m07.canonical_file)
    parser.add_argument("--timeout", type=_positive, default=900)
    args = parser.parse_args(argv)
    protocol_path = args.protocol
    schedule_path = args.schedule
    build_map_path = args.build_map
    protocol = _validate_protocol(protocol_path)
    schedule = _validate_schedule(schedule_path, protocol_path, protocol)
    build = _validate_build(build_map_path, protocol)
    prior = _load_prior(args.prior_index, protocol_path, schedule_path, build_map_path, schedule, args.phase, build)
    row = _select_pair(schedule, args.phase, args.pair_id, prior)
    require(not any(item.get("pairId") == row["pairId"] and item.get("attempt") == args.attempt for item in prior),
            "The requested pair attempt already exists in the prior index")
    if args.attempt > 1:
        require(any(item.get("pairId") == row["pairId"] and item.get("attempt") == args.attempt - 1 for item in prior),
                "Retry attempt requires the immediately prior retained pair attempt")
    output_root = args.output_root
    require(output_root.is_absolute() and output_root == output_root.resolve() and not output_root.exists() and
            not output_root.is_symlink(), "Output root must be a new canonical absolute path")
    require(output_root.parent.is_dir() and not output_root.parent.is_symlink(), "Output root parent is unavailable")
    output_root.mkdir()
    run_id = _safe_name(output_root.name)
    attempts = list(prior)
    sides: dict[str, dict[str, Any]] = {}
    for side_name in row["order"]:
        side = build["sides"][side_name]
        project_output = side["projectRoot"] / "_temp/AssemblyShadow" / (
            "H1Pair-" + run_id + "-" + side_name + "-" + _safe_name(row["pairId"]) + "-" + str(args.attempt))
        require(not project_output.exists() and not project_output.is_symlink(),
                "Per-side output must be new: " + str(project_output))
        sides[side_name] = _run_side(side_name, side, row["mode"], project_output, side["projectRoot"], args.timeout)
        if sides[side_name].get("stopBeforeNextSide"):
            other = "B" if side_name == "A" else "A"
            if other not in sides:
                other_side = build["sides"][other]
                other_output = other_side["projectRoot"] / "_temp/AssemblyShadow" / (
                    "H1Pair-" + run_id + "-" + other + "-" + _safe_name(row["pairId"]) + "-" + str(args.attempt))
                require(not other_output.exists() and not other_output.is_symlink(),
                        "Skipped side output must be new: " + str(other_output))
                sides[other] = _skipped_side(
                    other, other_side, row["mode"], other_output,
                    "Skipped because the previous runner process group could not be proven gone.", args.timeout)
            break
    status = "Passed" if all(sides[side]["status"] == "Passed" for side in SIDES) else "Failed"
    record = {"pairId": row["pairId"], "attempt": args.attempt, "mode": row["mode"], "phase": row["phase"],
              "order": row["order"], "status": status, "retryOf": args.attempt - 1 if args.attempt > 1 else None,
              "A": sides["A"], "B": sides["B"]}
    attempts.append(record)
    sample = {"schemaVersion": 1, "kind": "H1ControlledSamples", "protocol": binding(protocol_path),
              "schedule": binding(schedule_path), "buildMap": binding(build_map_path), "attempts": attempts}
    output_path = output_root / "sample-index.json"
    with output_path.open("x", encoding="utf-8") as stream:
        json.dump(sample, stream, indent=2)
        stream.write("\n")
    print(("Passed" if status == "Passed" else "Failed") + ": " + str(output_path), flush=True)
    return 0 if status == "Passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
