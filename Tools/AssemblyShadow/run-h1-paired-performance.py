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
import h1_graph_reuse as graph_reuse
import h1_formal_launch_authority as formal_authority


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
PILOT_VERIFICATION_KIND = "H1PilotVerificationReceipt"
PILOT_VERIFICATION_SCHEMA = 1
PILOT_VERIFIER_PATHS = tuple(
    Path(__file__).with_name(name).resolve()
    for name in (
        "run-h1-paired-performance.py",
        "seal-h1-pilot-verification.py",
        "h1_paired_performance.py",
        "h1_graph_reuse.py",
        "h1_formal_launch_authority.py",
        "r00_results.py",
        "r00_player_inputs.py",
        "run-r00-players.py",
        "run-m07-players.py",
        "m07_results.py",
        "r01_early_results.py",
        "r01_early_capsule.py",
        "shadow_tools.py",
    )
)


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


def _verify_prior_launch(value: Any, side: dict[str, Any], mode: str, label: str,
                         pairing_authority: dict[str, Any] | None = None) -> None:
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
    verified = _r00.verify_suite(launch_path, expected_mode=mode, pairing_authority=pairing_authority)
    require(verified.get("result") == "Passed" and verified.get("requestedModeIds") == [mode] and
            verified.get("executedModeIds") == [mode], label + " R00 verification failed")


def _json_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _pilot_attempts(attempts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in attempts if row.get("phase") == "pilot"]


def _pilot_attempt_digest(attempts: list[dict[str, Any]]) -> str:
    return _json_digest(_pilot_attempts(attempts))


def _selected_pilot_attempts(attempts: list[dict[str, Any]],
                             schedule: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = []
    for pair in [row for row in schedule if row.get("phase") == "pilot"]:
        rows = [row for row in attempts if row.get("pairId") == pair.get("pairId")]
        require(rows, "Missing pilot attempt: " + str(pair.get("pairId")))
        latest = max(rows, key=lambda row: row.get("attempt", 0))
        require(latest.get("status") == "Passed",
                "Latest retained pilot attempt is not Passed: " + str(pair.get("pairId")))
        require(latest.get("mode") == pair.get("mode") and latest.get("phase") == "pilot",
                "Pilot attempt schedule identity mismatch: " + str(pair.get("pairId")))
        for side in SIDES:
            require(type(latest.get(side)) is dict and latest[side].get("status") == "Passed" and
                    type(latest[side].get("launchReceipt")) is dict,
                    "Selected pilot side is not a passed launch: " + str(pair.get("pairId")) + "." + side)
        selected.append(latest)
    require(len(selected) == len(MODES) and {row.get("mode") for row in selected} == set(MODES),
            "Formal sampling requires exactly one latest passed pilot for every mode")
    return selected


def _verifier_bindings() -> list[dict[str, str]]:
    return [binding(path) for path in PILOT_VERIFIER_PATHS]


def _guarded_file(value: str | Path, label: str) -> Path:
    raw = Path(value)
    require(raw.is_absolute() and not raw.is_symlink(), label + " must be an absolute non-symlink file")
    path = raw.resolve(strict=True)
    require(path == raw and path.is_file() and not path.is_symlink(), label + " must be a canonical regular file")
    return path


def _stat_guard(path: Path) -> dict[str, int]:
    path = _guarded_file(path, "Pilot guarded input")
    stat = path.stat()
    return {
        "device": int(stat.st_dev),
        "inode": int(stat.st_ino),
        "mode": int(stat.st_mode),
        "size": int(stat.st_size),
        "mtimeNs": int(stat.st_mtime_ns),
        "ctimeNs": int(stat.st_ctime_ns),
    }


def _register_expected_file(files: dict[str, str], value: str | Path, sha256: Any, label: str) -> None:
    require(type(sha256) is str and len(sha256) == 64 and
            all(character in "0123456789abcdef" for character in sha256.lower()),
            label + " SHA-256 is invalid")
    path = _guarded_file(value, label)
    key = str(path)
    expected = sha256.lower()
    if key in files:
        require(files[key] == expected, label + " has inconsistent immutable hashes")
    else:
        files[key] = expected


def _pilot_expected_files(selected: list[dict[str, Any]]) -> dict[str, str]:
    files: dict[str, str] = {}
    for attempt in selected:
        pair_id = str(attempt.get("pairId"))
        for side in SIDES:
            launch_path, launch_binding = bound_file(
                attempt[side].get("launchReceipt"), "Pilot " + pair_id + "." + side + ".launchReceipt")
            _register_expected_file(files, launch_path, launch_binding["sha256"],
                                    "Pilot " + pair_id + "." + side + " launch receipt")
            launch = read_json(launch_path)
            before = launch.get("inputHashesBefore")
            after = launch.get("inputHashesAfter")
            require(type(before) is dict and before and before == after,
                    "Pilot " + pair_id + "." + side + " immutable input inventory is absent or changed")
            for file_path, sha256 in before.items():
                _register_expected_file(files, file_path, sha256,
                                        "Pilot " + pair_id + "." + side + " immutable input")
            launches = launch.get("processLaunches")
            require(type(launches) is list and launches,
                    "Pilot " + pair_id + "." + side + " process launch inventory is empty")
            for process in launches:
                require(type(process) is dict, "Pilot process launch row is invalid")
                for path_key, sha_key in (
                    ("resultPath", "resultSha256"),
                    ("earlyCapsulePath", "earlyCapsuleSha256"),
                    ("earlyResultPath", "earlyResultSha256"),
                ):
                    file_path = process.get(path_key)
                    sha256 = process.get(sha_key)
                    if file_path:
                        _register_expected_file(files, file_path, sha256,
                                                "Pilot " + pair_id + "." + side + " " + path_key)
    return files


def _selected_pilot_summary(selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "pairId": row["pairId"],
            "attempt": row["attempt"],
            "mode": row["mode"],
            "A": {"launchReceipt": row["A"]["launchReceipt"]},
            "B": {"launchReceipt": row["B"]["launchReceipt"]},
        }
        for row in selected
    ]


def seal_pilot_verification(attempts: list[dict[str, Any]], schedule: list[dict[str, Any]],
                            build: dict[str, Any], protocol_path: Path, schedule_path: Path,
                            build_map_path: Path, source_index_path: Path,
                            graph_reuse_authority: dict[str, Any] | None = None,
                            graph_reuse_bridge_path: Path | None = None) -> dict[str, Any]:
    selected = _selected_pilot_attempts(attempts, schedule)
    expected = _pilot_expected_files(selected)
    before = {path: _stat_guard(Path(path)) for path in sorted(expected)}
    deep_verifications = 0
    for attempt in selected:
        pair = next(row for row in schedule if row.get("pairId") == attempt.get("pairId"))
        for side in SIDES:
            side_authority = graph_reuse.authority_for_project(
                graph_reuse_authority, build["sides"][side]["projectRoot"])
            _verify_prior_launch(
                attempt[side].get("launchReceipt"), build["sides"][side], pair["mode"],
                "Pilot " + str(pair["pairId"]) + "." + side, side_authority)
            deep_verifications += 1
    after = {path: _stat_guard(Path(path)) for path in sorted(expected)}
    require(before == after, "Pilot immutable file identity changed during strict verification; refusing to seal cache")
    files = [
        {"path": path, "sha256": expected[path], "guard": after[path]}
        for path in sorted(expected)
    ]
    return {
        "schemaVersion": PILOT_VERIFICATION_SCHEMA,
        "kind": PILOT_VERIFICATION_KIND,
        "status": "PassedStrictReconstructionAndStatGuardSealed",
        "protocol": binding(protocol_path),
        "schedule": binding(schedule_path),
        "buildMap": binding(build_map_path),
        "sourcePilotIndex": binding(source_index_path),
        "graphReuseBridge": binding(graph_reuse_bridge_path) if graph_reuse_bridge_path is not None else None,
        "verifierBindings": _verifier_bindings(),
        "pilotAttemptsSha256": _pilot_attempt_digest(attempts),
        "selectedPilots": _selected_pilot_summary(selected),
        "deepLaunchVerificationCount": deep_verifications,
        "fileCount": len(files),
        "totalBytes": sum(row["guard"]["size"] for row in files),
        "fileInventorySha256": _json_digest(
            [{"path": row["path"], "sha256": row["sha256"]} for row in files]),
        "guardInventorySha256": _json_digest(files),
        "guardSemantics": (
            "Strict R00 reconstruction hashes the complete graph once while file identity is stable. "
            "Formal admission re-hashes control receipts/tools and requires unchanged canonical path, "
            "device, inode, mode, size, mtimeNs, and ctimeNs for every sealed immutable file. "
            "Any guard change fails closed and requires a new strict seal."
        ),
        "files": files,
    }


def verify_pilot_verification(receipt_path: Path, attempts: list[dict[str, Any]],
                              schedule: list[dict[str, Any]], protocol_path: Path,
                              schedule_path: Path, build_map_path: Path,
                              graph_reuse_bridge_path: Path | None = None) -> dict[str, str]:
    receipt_path = _m07.canonical_file(receipt_path)
    value = read_json(receipt_path)
    require(value.get("schemaVersion") == PILOT_VERIFICATION_SCHEMA and
            value.get("kind") == PILOT_VERIFICATION_KIND and
            value.get("status") == "PassedStrictReconstructionAndStatGuardSealed",
            "Invalid pilot verification receipt")
    for key, path in (("protocol", protocol_path), ("schedule", schedule_path), ("buildMap", build_map_path)):
        require(value.get(key) == binding(path), "Pilot verification " + key + " binding mismatch")
    require(value.get("verifierBindings") == _verifier_bindings(),
            "Pilot verification implementation changed; strict reseal is required")
    expected_bridge = binding(graph_reuse_bridge_path) if graph_reuse_bridge_path is not None else None
    require(value.get("graphReuseBridge") == expected_bridge,
            "Pilot verification graph reuse bridge binding mismatch")
    if graph_reuse_bridge_path is not None:
        bridge = read_json(graph_reuse_bridge_path)
        project = canonical_dir(bridge.get("projectRoot", ""), "graph reuse bridge project")
        graph_reuse.verify_bridge_compact(graph_reuse_bridge_path, project, build_map_path)
    require(value.get("pilotAttemptsSha256") == _pilot_attempt_digest(attempts),
            "Pilot attempt history changed after strict sealing")
    selected = _selected_pilot_attempts(attempts, schedule)
    require(value.get("selectedPilots") == _selected_pilot_summary(selected),
            "Selected pilot launch receipts changed after strict sealing")

    expected = _pilot_expected_files(selected)
    rows = value.get("files")
    require(type(rows) is list and len(rows) == value.get("fileCount") == len(expected),
            "Pilot verification file inventory count mismatch")
    cached_pairs = [{"path": row.get("path"), "sha256": row.get("sha256")} for row in rows
                    if type(row) is dict]
    require(len(cached_pairs) == len(rows) and value.get("fileInventorySha256") == _json_digest(cached_pairs),
            "Pilot verification file inventory digest mismatch")
    require(value.get("guardInventorySha256") == _json_digest(rows),
            "Pilot verification guard inventory digest mismatch")
    require(cached_pairs == [{"path": path, "sha256": expected[path]} for path in sorted(expected)],
            "Pilot verification immutable path/hash inventory differs from current pilot receipts")
    for row in rows:
        path = _guarded_file(row["path"], "Pilot verification cached file")
        require(row.get("guard") == _stat_guard(path),
                "Pilot verification cache invalidated by changed file identity: " + str(path))
    return binding(receipt_path)


def _load_prior(path: Path | None, protocol_path: Path, schedule_path: Path, build_map_path: Path,
                schedule: list[dict[str, Any]], phase: str, build: dict[str, Any],
                pilot_verification_path: Path | None = None,
                graph_reuse_bridge_path: Path | None = None) -> list[dict[str, Any]]:
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
        if row["phase"] == "formal":
            require(row["A"].get("formalLaunchAuthority") is None,
                    "Prior protected formal side A must not carry retained launch authority")
            b_authority = row["B"].get("formalLaunchAuthority")
            b_launch = row["B"].get("launchReceipt")
            if row["B"].get("skipped") is True and b_launch is None:
                require(b_authority is None,
                        "Skipped prior formal side B must not fabricate retained launch authority")
            elif b_authority is not None:
                bound_file(b_authority, "Prior formal side B launch authority")
    if phase == "formal":
        require(pilot_verification_path is not None,
                "Formal sampling requires --pilot-verification-receipt sealed by strict pilot reconstruction")
        cache_binding = verify_pilot_verification(
            pilot_verification_path, attempts, schedule, protocol_path, schedule_path, build_map_path,
            graph_reuse_bridge_path)
        bridge_binding = binding(graph_reuse_bridge_path) if graph_reuse_bridge_path is not None else None
        for prior_attempt in attempts:
            if prior_attempt.get("phase") == "formal":
                require(prior_attempt.get("pilotVerification") == cache_binding,
                        "Prior formal attempt pilot verification binding mismatch")
                require(prior_attempt.get("graphReuseBridge") == bridge_binding,
                        "Prior formal attempt graph reuse bridge binding mismatch")
                b = prior_attempt["B"]
                if bridge_binding is not None and not (
                        b.get("skipped") is True and b.get("launchReceipt") is None):
                    require(type(b.get("formalLaunchAuthority")) is dict,
                            "Prior retained formal side B is missing launch authority")
                    bound_file(b["formalLaunchAuthority"],
                               "Prior retained formal side B launch authority")
    else:
        require(pilot_verification_path is None, "Pilot sampling must not consume a formal pilot verification receipt")
        require(graph_reuse_bridge_path is None, "Pilot sampling must not consume a graph reuse bridge")
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


def build_command(project: Path, mode: str, side: dict[str, Any], output_root: Path, timeout: int,
                  formal_launch_authority: Path | None = None) -> list[str]:
    canonical_dir(project, "project")
    script = _m07.canonical_file(RUNNER_PATH)
    on = side["builds"]["on"]["receipt"]
    off = side["builds"]["off"]["receipt"]
    command = [sys.executable, str(script), "--project-root", str(project),
               "--fixture-manifest", str(side["fixtureManifest"]), "--on-build", str(on),
               "--off-build", str(off), "--replay-receipt", str(side["replayReceipt"]),
               "--output-root", str(output_root), "--early-startup-strategy", "R01EarlyStartup",
               "--mode", mode, "--timeout", str(timeout)]
    if formal_launch_authority is not None:
        authority = _m07.canonical_file(formal_launch_authority)
        command.extend(["--h1-formal-launch-authority", str(authority)])
    return command


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
              project_output: Path, timeout: int,
              formal_launch_authority: Path | None = None) -> dict[str, Any]:
    output_root_parent = project_output / "_temp/AssemblyShadow"
    require(output_root_parent.is_dir() and not output_root_parent.is_symlink(),
            side_name + " project output parent is unavailable")
    command = build_command(
        side["projectRoot"], mode, side, output_root, timeout, formal_launch_authority)
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
            "runner": runner_binding(),
            "formalLaunchAuthority": binding(formal_launch_authority)
                if formal_launch_authority is not None else None}
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
    parser.add_argument("--pilot-verification-receipt", type=_m07.canonical_file)
    parser.add_argument("--graph-reuse-bridge", type=_m07.canonical_file)
    parser.add_argument("--timeout", type=_positive, default=900)
    args = parser.parse_args(argv)
    protocol_path = args.protocol
    schedule_path = args.schedule
    build_map_path = args.build_map
    protocol = _validate_protocol(protocol_path)
    schedule = _validate_schedule(schedule_path, protocol_path, protocol)
    build = _validate_build(build_map_path, protocol)
    prior = _load_prior(
        args.prior_index, protocol_path, schedule_path, build_map_path, schedule, args.phase, build,
        args.pilot_verification_receipt, args.graph_reuse_bridge)
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
        launch_authority_path = None
        if (args.phase == "formal" and side_name == "B" and
                args.graph_reuse_bridge is not None and args.pilot_verification_receipt is not None):
            launch_authority_path = project_output.parent / (
                project_output.name + ".formal-launch-authority.json")
            require(launch_authority_path.is_absolute() and
                    launch_authority_path == launch_authority_path.resolve() and
                    not launch_authority_path.exists() and not launch_authority_path.is_symlink(),
                    "Formal side-B launch authority must be a new canonical path")
            launch_authority = formal_authority.create_receipt(
                side["projectRoot"], row["pairId"], args.attempt, row["mode"], row["order"],
                protocol_path, schedule_path, build_map_path, args.graph_reuse_bridge,
                args.pilot_verification_receipt, side["fixtureManifest"],
                side["builds"]["on"]["receipt"], side["builds"]["off"]["receipt"],
                side["replayReceipt"])
            with launch_authority_path.open("x", encoding="utf-8") as stream:
                json.dump(launch_authority, stream, indent=2)
                stream.write("\n")
            formal_authority.verify_receipt(
                launch_authority_path, side["projectRoot"], row["mode"],
                side["fixtureManifest"], side["builds"]["on"]["receipt"],
                side["builds"]["off"]["receipt"], side["replayReceipt"],
                expected_pair_id=row["pairId"], expected_attempt=args.attempt)
        sides[side_name] = _run_side(
            side_name, side, row["mode"], project_output, side["projectRoot"], args.timeout,
            launch_authority_path)
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
    if args.pilot_verification_receipt is not None:
        record["pilotVerification"] = binding(args.pilot_verification_receipt)
    if args.graph_reuse_bridge is not None:
        record["graphReuseBridge"] = binding(args.graph_reuse_bridge)
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
