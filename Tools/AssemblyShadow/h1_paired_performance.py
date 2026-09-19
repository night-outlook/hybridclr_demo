"""Strict analysis of preregistered paired R00 Development observations."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable

import r00_results
import r00_player_inputs
from shadow_tools import VerificationError, require


MODES = ("R00-OFF-NoPatch", "R00-ON-NoPatch", "R00-ON-P01", "R00-ON-P03")
OPERATIONS = ("allocation", "reflectionInvoke", "closedGeneric")
PHASES = ("first", "warmup", "repeat10", "repeat10000")
MEMORY_PHASES = ("before-benchmark", "after-benchmark")
MEMORY_MEASUREMENT = "DarwinMachTaskBasicInfoResidentAndLifetimePeakBytes"
MEMORY_SEMANTICS = "currentRssBytes=mach_task_self/task_info(MACH_TASK_BASIC_INFO).resident_size; managedBytes=GC.GetTotalMemory(false); lifetimePeakRssBytes=resident_size_max; noForcedGC"
MATCH_FIELDS = (
    "developmentCppRelease", "unity", "architecture", "strip", "codegen", "startup",
    "commonMeasurementCoreSha256", "witnessSha256",
)
EXPECTED_DIFFERENCES = ("runtimeAbiHash", "sourcePins")
PROTOCOL_ID = "H1R-Development-Paired-v1"
UNITY_VERSION = "2022.3.62f2"
TARGET = "StandaloneOSX"
ARCHITECTURE = "arm64"
STARTUP_STRATEGY = "R01EarlyStartup"
MEASUREMENT_CORE = "Assets/AssemblyShadowDemo/Bootstrap/M07R00PerformanceProbe.cs"
PROCESS_MEMORY = "Assets/AssemblyShadowDemo/Bootstrap/R00ProcessMemory.cs"
WITNESS = "Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/R00PerformanceWitness.cs"


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file() and not path.is_symlink(), "Missing or symlinked JSON: " + str(path))
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError, UnicodeError) as error:
        raise VerificationError("Invalid JSON " + str(path) + ": " + str(error)) from error
    require(type(value) is dict, "Expected JSON object: " + str(path))
    return value


def digest(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as error:
        raise VerificationError("Cannot hash " + str(path) + ": " + str(error)) from error


def _receipt_binding(value: Any, label: str) -> tuple[Path, str]:
    path, sha256 = _binding_shape(value, label)
    require(not path.is_symlink(), label + " must not bind a symlink")
    resolved = path.resolve(strict=True)
    require(not resolved.is_symlink() and resolved.is_file(), label + " must bind a regular file")
    require(digest(resolved) == sha256.lower(), label + " hash mismatch")
    return resolved, sha256.lower()


def _binding_shape(value: Any, label: str) -> tuple[Path, str]:
    require(type(value) is dict, label + " must be an object")
    path = value.get("path")
    sha256 = value.get("sha256")
    require(type(path) is str and path, label + ".path is required")
    require(type(sha256) is str and len(sha256) == 64 and all(c in "0123456789abcdef" for c in sha256.lower()),
            label + ".sha256 is invalid")
    return Path(path), sha256.lower()


def _load_preregistration(path: Path, kind: str, label: str) -> dict[str, Any]:
    value = read_json(path)
    require(value.get("schemaVersion") == 1, label + " schemaVersion must be 1")
    require(value.get("kind") == kind, label + " kind mismatch")
    return value


def _protocol_and_schedule(protocol_path: Path, schedule_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    protocol = _load_preregistration(protocol_path, "H1ControlledPerformanceProtocolTemplate", "protocol")
    schedule = _load_preregistration(schedule_path, "H1ControlledPairSchedule", "schedule")
    require(protocol.get("protocolId") == PROTOCOL_ID, "protocol identity mismatch")
    require(protocol.get("development") is True and protocol.get("nativeCompilerConfiguration") == "Release" and
            protocol.get("nativeAssertions") is False, "protocol must be Development C++ Release without native assertions")
    require(protocol.get("unityVersion") == UNITY_VERSION and protocol.get("target") == TARGET and
            protocol.get("architecture") == ARCHITECTURE, "protocol platform identity mismatch")
    require(protocol.get("modes") == list(MODES), "protocol mode order differs from R00")
    require(protocol.get("formalPairsPerMode") == 10, "protocol formal pair count must be 10")
    require(protocol.get("pilotPairsPerMode") == 1, "protocol pilot pair count must be 1")
    require(protocol.get("pilotExcludedByPredeclaredRule") is True, "pilot exclusion must be preregistered")
    require(protocol.get("formalOutlierPolicy") == "Retain all valid samples; no latency-based exclusions",
            "protocol outlier policy is not the preregistered retain-all policy")
    require(protocol.get("ratioResolutionRule") == "Suppress ratios when reference total ticks < 10; retain absolute ticks and paired differences",
            "protocol ratio rule differs from the preregistered rule")
    require(schedule.get("protocolPath") == str(protocol_path), "schedule protocol path is not bound")
    require(schedule.get("protocolSha256") == digest(protocol_path), "schedule protocol hash mismatch")
    require(schedule.get("algorithm"), "schedule algorithm is missing")
    pairs = schedule.get("pairs")
    require(type(pairs) is list, "schedule pairs must be an array")
    expected = []
    for row in pairs:
        require(type(row) is dict, "schedule pair must be an object")
        pair_id, mode, phase, order = row.get("pairId"), row.get("mode"), row.get("phase"), row.get("order")
        require(type(pair_id) is str and pair_id, "schedule pairId is required")
        require(mode in MODES, "schedule contains unknown mode")
        require(phase in ("pilot", "formal"), "schedule contains unknown phase")
        require(order in (["A", "B"], ["B", "A"]), "schedule order must be AB or BA")
        require(row.get("includedInFormalStatistics") is (phase == "formal"),
                "schedule formal inclusion flag differs from phase")
        expected.append(row)
    require(len(expected) == 44, "schedule must contain exactly 44 preregistered pairs")
    for mode in MODES:
        rows = [row for row in expected if row["mode"] == mode]
        require(len([row for row in rows if row["phase"] == "pilot"]) == 1, mode + " must have one pilot")
        formal = [row for row in rows if row["phase"] == "formal"]
        require(len(formal) == 10, mode + " must have ten formal pairs")
        require(sum(row["order"] == ["A", "B"] for row in formal) == 5, mode + " must have five AB formal pairs")
        require(sum(row["order"] == ["B", "A"] for row in formal) == 5, mode + " must have five BA formal pairs")
    return protocol, schedule


def _build_world_key(mode: str) -> str:
    return "OFF" if mode == MODES[0] else "ON"


def _canonical_directory(value: Any, label: str) -> Path:
    require(type(value) is str and value, label + " is required")
    path = Path(value)
    resolved = path.resolve(strict=True)
    require(path.is_absolute() and path == resolved and resolved.is_dir() and not resolved.is_symlink(),
            label + " must be a canonical directory")
    return resolved


def _bound_artifact(path_value: Any, sha_value: Any, label: str) -> Path:
    require(type(path_value) is str and path_value, label + " path is required")
    require(type(sha_value) is str and len(sha_value) == 64,
            label + " sha256 is invalid")
    raw_path = Path(path_value)
    require(not raw_path.is_symlink(), label + " must not bind a symlink")
    path = raw_path.resolve(strict=True)
    require(path.is_file() and not path.is_symlink(), label + " must be a regular file")
    require(digest(path) == sha_value.lower(), label + " hash mismatch")
    return path


def _inventory_hash(rows: list[dict[str, Any]]) -> str:
    text = "\n".join(row["path"] + "\0" + row["source"] + "\0" + row["sha256"]
                     for row in sorted(rows, key=lambda row: row["path"]))
    return hashlib.sha256(text.encode()).hexdigest()


def _validate_snapshot_inventory(provenance: dict[str, Any], label: str) -> Path:
    require(provenance.get("schemaVersion") == 2, label + " schemaVersion must be 2")
    root = _canonical_directory(provenance.get("snapshotRoot"), label + ".snapshotRoot")
    rows = provenance.get("snapshotFiles")
    require(type(rows) is list and rows, label + ".snapshotFiles is empty")
    actual_paths = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    claimed_paths: set[str] = set()
    for row in rows:
        require(type(row) is dict and type(row.get("path")) is str and row["path"] and
                row.get("source") == "snapshot" and
                type(row.get("sha256")) is str and len(row["sha256"]) == 64,
                label + " snapshot inventory row is invalid")
        relative = Path(row["path"])
        require(not relative.is_absolute() and ".." not in relative.parts and row["path"] not in claimed_paths,
                label + " snapshot inventory path is invalid or duplicate")
        raw_artifact = root / relative
        require(not raw_artifact.is_symlink(), label + " snapshot inventory path is symlinked: " + row["path"])
        artifact = raw_artifact.resolve(strict=True)
        require(artifact.is_relative_to(root) and artifact.is_file() and not artifact.is_symlink(),
                label + " snapshot inventory path escapes or is not a regular file")
        require(digest(artifact) == row["sha256"], label + " snapshot inventory file hash mismatch: " + row["path"])
        claimed_paths.add(row["path"])
    require(claimed_paths == actual_paths, label + " snapshot inventory paths differ from current files")
    require(_inventory_hash(rows) == provenance.get("snapshotInventorySha256"),
            label + " snapshot inventory aggregate hash mismatch")
    return root


def _expected_configuration(feature: str) -> dict[str, Any]:
    return {
        "development": True,
        "developmentOption": True,
        "scriptingBackend": "IL2CPP",
        "il2CppCompilerConfiguration": "Release",
        "managedStrippingLevel": "Low",
        "il2CppCodeGeneration": "OptimizeSpeed",
        "allowDebugging": False,
        "connectProfiler": False,
        "deepProfiling": False,
        "buildScriptsOnly": False,
        "nativeArguments": "--compiler-flags=\"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=" +
                           ("1" if feature == "on" else "0") + "\"",
    }


def _measurement_source_hashes(evidence: dict[str, Any], project: Path,
                               build_guid: str, label: str) -> dict[str, str]:
    root = _canonical_directory(evidence.get("measurementSourceSnapshotRoot"),
                                label + ".measurementSourceSnapshotRoot")
    require(evidence.get("measurementSourcesBuildGuid") == build_guid,
            label + " measurement source evidence is not tied to the M07 build GUID")
    require(evidence.get("measurementSourcesUnchanged") is True,
            label + " measurement source evidence was not sealed")
    rows = evidence.get("measurementSources")
    expected_paths = {MEASUREMENT_CORE, PROCESS_MEMORY, WITNESS}
    require(type(rows) is list and len(rows) == len(expected_paths),
            label + " measurement source evidence inventory is incomplete")
    result: dict[str, str] = {}
    for row in rows:
        require(type(row) is dict and row.get("relativePath") in expected_paths and
                row["relativePath"] not in result,
                label + " measurement source path is unrecognized or duplicate")
        relative = row["relativePath"]
        original = project / relative
        snapshot = root / relative
        require(row.get("originalSourcePath") == str(original) and row.get("snapshotPath") == str(snapshot),
                label + " measurement source paths do not match the recognized source")
        _bound_artifact(row.get("snapshotPath"), row.get("sha256"),
                        label + " measurement source " + relative)
        result[relative] = row["sha256"].lower()
    actual_paths = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_paths == expected_paths, label + " measurement source snapshot inventory differs")
    return result


def _validate_controlled_build(project: Path, side: str, flavor: str,
                               build: dict[str, Any]) -> dict[str, Any]:
    label = side + "." + flavor
    feature = flavor
    variant = "NativeOn" if flavor == "on" else "NativeOff"
    require(type(build) is dict, label + " build is invalid")
    require(build.get("feature") == feature and build.get("development") is True and
            build.get("nativeCompilerConfiguration") == "Release", label + " declared configuration mismatch")
    receipt_path, receipt_sha = _receipt_binding(build.get("receipt"), label + ".receipt")
    evidence_path, evidence_sha = _receipt_binding(build.get("controlledEvidence"), label + ".controlledEvidence")
    receipt = read_json(receipt_path)
    evidence = read_json(evidence_path)

    require(receipt.get("schemaVersion") == 1 and receipt.get("milestone") == "M07" and
            receipt.get("variant") == variant, label + " M07 receipt header mismatch")
    for field in ("baselineBuildId", "runtimeAbiHash", "buildGuid", "playerOutput",
                  "inputSnapshot", "inputSnapshotHash", "nativeLibraryPath", "nativeLibrarySha256",
                  "nativeMetadataPath", "nativeMetadataSha256"):
        require(type(receipt.get(field)) is str and receipt[field], label + " M07 receipt field is missing: " + field)
    require(receipt.get("unityVersion") == UNITY_VERSION and receipt.get("target") == TARGET and
            receipt.get("architecture") == ARCHITECTURE, label + " M07 platform identity mismatch")
    expected_config = _expected_configuration(feature)
    require(receipt.get("nativeArguments") == expected_config["nativeArguments"],
            label + " M07 native feature argument mismatch")

    require(evidence.get("schemaVersion") == 1 and evidence.get("kind") == "R00ControlledBuildEvidence" and
            evidence.get("result") == "Passed", label + " controlled evidence header mismatch")
    require(evidence.get("feature") == feature and evidence.get("provenanceComplete") is True and
            evidence.get("sourcePinsUnchanged") is True, label + " controlled evidence is not sealed")
    require(evidence.get("selectedBuildMethod") ==
            ("BuildPlayerBaseline" if feature == "on" else "BuildFeatureDisabledPlayer"),
            label + " selected build method mismatch")
    for config_name in ("requestedConfiguration", "effectiveConfiguration"):
        config = evidence.get(config_name)
        require(type(config) is dict, label + " " + config_name + " is missing")
        for key, expected in expected_config.items():
            require(config.get(key) == expected, label + " " + config_name + " mismatch: " + key)

    require(evidence.get("actualReceiptPath") == str(receipt_path) and
            evidence.get("actualReceiptSha256") == receipt_sha,
            label + " controlled evidence receipt binding mismatch")
    cross_fields = {
        "actualReceiptVariant": "variant", "buildGuid": "buildGuid",
        "baselineBuildId": "baselineBuildId", "runtimeAbiHash": "runtimeAbiHash",
        "playerOutput": "playerOutput", "nativeLibraryPath": "nativeLibraryPath",
        "nativeLibrarySha256": "nativeLibrarySha256", "nativeMetadataPath": "nativeMetadataPath",
        "nativeMetadataSha256": "nativeMetadataSha256", "inputSnapshotPath": "inputSnapshot",
        "inputSnapshotSha256": "inputSnapshotHash", "nativeArguments": "nativeArguments",
    }
    for evidence_field, receipt_field in cross_fields.items():
        require(evidence.get(evidence_field) == receipt.get(receipt_field),
                label + " controlled evidence differs from M07 receipt: " + evidence_field)
    measurement_sources = _measurement_source_hashes(evidence, project, receipt["buildGuid"], label)
    if "buildGuid" in build:
        require(build["buildGuid"] == receipt["buildGuid"], label + " build GUID mismatch")
    if "playerOutput" in build:
        require(build["playerOutput"] == receipt["playerOutput"], label + " Player output mismatch")

    player_output = _canonical_directory(receipt["playerOutput"], label + " Player output")
    native_library = _bound_artifact(receipt["nativeLibraryPath"], receipt["nativeLibrarySha256"], label + " native library")
    native_metadata = _bound_artifact(receipt["nativeMetadataPath"], receipt["nativeMetadataSha256"], label + " native metadata")
    executable = _bound_artifact(evidence.get("playerExecutable"), evidence.get("playerExecutableSha256"),
                                 label + " Player executable")
    require(all(path.is_relative_to(player_output) for path in (native_library, native_metadata, executable)),
            label + " Player artifact is outside the bound Player output")
    snapshot = _canonical_directory(receipt["inputSnapshot"], label + " input snapshot")
    require(snapshot == Path(receipt_path).parent, label + " M07 receipt is outside its input snapshot")

    source_pins = _bound_artifact(evidence.get("sourcePinsPath"), evidence.get("sourcePinsSha256Before"),
                                  label + " source pins")
    require(evidence.get("sourcePinsSha256After") == evidence.get("sourcePinsSha256Before"),
            label + " source pin before/after hashes differ")
    provenance = evidence.get("nativeProvenance")
    require(type(provenance) is dict and provenance.get("schemaVersion") == 2 and
            provenance.get("projectRoot") == str(project) and provenance.get("sourcePinFile") == str(source_pins) and
            provenance.get("sourcePinSha256") == digest(source_pins) and
            provenance.get("verificationExitCode") == 0,
            label + " native provenance does not bind the current project and source pins")
    snapshot_root = _validate_snapshot_inventory(provenance, label + ".nativeProvenance")
    require(source_pins.is_relative_to(snapshot_root), label + " source pins are outside the immutable snapshot")
    for path_field, hash_field in (
            ("verificationToolPath", "verificationToolSha256"),
            ("verificationSupportToolPath", "verificationSupportToolSha256"),
            ("installReceiptPath", "installReceiptSha256"),
            ("pythonExecutable", "pythonExecutableSha256")):
        artifact = _bound_artifact(provenance.get(path_field), provenance.get(hash_field),
                                   label + ".nativeProvenance." + path_field)
        if path_field != "pythonExecutable":
            require(artifact.is_relative_to(snapshot_root), label + " provenance artifact is outside the snapshot: " + path_field)
    return {"path": str(receipt_path), "sha256": receipt_sha, "receipt": receipt,
            "controlledEvidence": {"path": str(evidence_path), "sha256": evidence_sha},
            "sourcePinsSha256": digest(source_pins), "configuration": expected_config,
            "measurementSources": measurement_sources}


def _build_bindings(build_map: dict[str, Any]) -> tuple[dict[str, dict[str, dict[str, Any]]], dict[str, dict[str, Any]]]:
    sides = build_map.get("sides")
    require(type(sides) is dict and set(sides) == {"A", "B"},
            "frozen build map must contain exactly A and B sides")
    bindings: dict[str, dict[str, dict[str, Any]]] = {}
    facts: dict[str, dict[str, Any]] = {}
    all_guids: set[str] = set()
    all_receipts: set[str] = set()
    for side in ("A", "B"):
        item = sides[side]
        require(type(item) is dict, "frozen build map side is invalid: " + side)
        project = _canonical_directory(item.get("projectRoot"), side + ".projectRoot")
        builds = item.get("builds")
        require(type(builds) is dict and set(builds) == {"on", "off"},
                side + " must bind exactly on and off builds")
        bindings[side] = {
            "ON": _validate_controlled_build(project, side, "on", builds["on"]),
            "OFF": _validate_controlled_build(project, side, "off", builds["off"]),
        }
        on, off = bindings[side]["ON"], bindings[side]["OFF"]

        fixture_path, fixture_sha = _receipt_binding(
            item.get("fixtureManifest"), side + ".fixtureManifest")
        replay_path, replay_sha = _receipt_binding(
            item.get("replayReceipt"), side + ".replayReceipt")
        graph = r00_player_inputs.verify_inputs(
            project, fixture_path, Path(on["path"]), Path(off["path"]), replay_path)
        manifest = graph["manifest"]
        require(manifest.get("baselineBuildId") == on["receipt"]["baselineBuildId"] ==
                off["receipt"]["baselineBuildId"],
                side + " fixture/replay graph baseline differs from controlled Players")
        require(manifest.get("runtimeAbiHash") == on["receipt"]["runtimeAbiHash"] ==
                off["receipt"]["runtimeAbiHash"],
                side + " fixture/replay graph runtime ABI differs from controlled Players")
        bindings[side]["graph"] = {
            "fixtureManifest": {"path": str(fixture_path), "sha256": fixture_sha},
            "replayReceipt": {"path": str(replay_path), "sha256": replay_sha},
            "baselineBuildId": manifest["baselineBuildId"],
            "runtimeAbiHash": manifest["runtimeAbiHash"],
        }

        require(on["receipt"]["runtimeAbiHash"] == off["receipt"]["runtimeAbiHash"],
                side + " ON/OFF runtime ABI hashes differ")
        require(on["sourcePinsSha256"] == off["sourcePinsSha256"],
                side + " ON/OFF source pin hashes differ")
        require(on["measurementSources"] == off["measurementSources"],
                side + " ON/OFF build-time measurement source hashes differ")
        for row in (on, off):
            require(row["path"] not in all_receipts, "frozen build map reuses an M07 receipt")
            require(row["receipt"]["buildGuid"] not in all_guids, "frozen build map reuses a buildGuid")
            all_receipts.add(row["path"])
            all_guids.add(row["receipt"]["buildGuid"])
        facts[side] = {
            "developmentCppRelease": True,
            "unity": on["receipt"]["unityVersion"],
            "architecture": on["receipt"]["architecture"],
            "strip": on["configuration"]["managedStrippingLevel"],
            "codegen": on["configuration"]["il2CppCodeGeneration"],
            "startup": STARTUP_STRATEGY,
            "commonMeasurementCoreSha256": on["measurementSources"][MEASUREMENT_CORE],
            "witnessSha256": on["measurementSources"][WITNESS],
            "runtimeAbiHash": on["receipt"]["runtimeAbiHash"],
            "sourcePins": on["sourcePinsSha256"],
        }
    require(bindings["A"]["ON"]["measurementSources"][PROCESS_MEMORY] ==
            bindings["B"]["ON"]["measurementSources"][PROCESS_MEMORY],
            "authenticated build facts are unmatched: processMemorySha256")
    return bindings, facts


def validate_build_map(build_map: dict[str, Any]) -> dict[str, Any]:
    """Authenticate frozen build artifacts and derive their comparability facts."""
    require(type(build_map) is dict, "build map must be an object")
    require(build_map.get("schemaVersion") == 1 and build_map.get("kind") == "H1ControlledBuildMap",
            "unsupported frozen build map schema")
    status = build_map.get("status")
    comp = build_map.get("comparability")
    if status != "Frozen" or type(comp) is not dict:
        return {"status": "ComparabilityIncomplete", "reasons": ["frozen build map comparability is pending"]}
    try:
        require(build_map.get("protocolId") == PROTOCOL_ID, "frozen build map protocol identity mismatch")
        require(build_map.get("target") == TARGET and build_map.get("architecture") == ARCHITECTURE,
                "frozen build map platform identity mismatch")
        configuration = build_map.get("configuration")
        require(type(configuration) is dict and configuration.get("development") is True and
                configuration.get("nativeCompilerConfiguration") == "Release" and
                configuration.get("nativeAssertions") is False,
                "frozen build map top-level configuration mismatch")
        build_bindings, facts = _build_bindings(build_map)
        require(set(comp) == set(MATCH_FIELDS + EXPECTED_DIFFERENCES),
                "comparability fields differ from the authenticated schema")
        for field in MATCH_FIELDS + EXPECTED_DIFFERENCES:
            require(comp.get(field) == {"A": facts["A"][field], "B": facts["B"][field]},
                    "comparability claim differs from authenticated build facts: " + field)
        mismatched = [field for field in MATCH_FIELDS if facts["A"][field] != facts["B"][field]]
        require(not mismatched, "authenticated build facts are unmatched: " + ", ".join(mismatched))
        unexpected = [field for field in EXPECTED_DIFFERENCES if facts["A"][field] == facts["B"][field]]
        require(not unexpected, "authenticated ABI/source fields are not different: " + ", ".join(unexpected))
    except (VerificationError, OSError, KeyError, TypeError, ValueError) as error:
        return {"status": "ComparabilityFailed", "reasons": ["frozen build authentication failed: " + str(error)]}
    return {"status": "ComparabilityPassed", "reasons": [],
            "matchedFields": {field: facts["A"][field] for field in MATCH_FIELDS},
            "expectedDifferent": {field: {"A": facts["A"][field], "B": facts["B"][field]}
                                  for field in EXPECTED_DIFFERENCES},
            "buildBindings": build_bindings}


def _validate_diagnostic_side(value: dict[str, Any], label: str) -> None:
    for field in ("startedAt", "finishedAt", "startedAtUnix", "finishedAtUnix"):
        if field in value:
            require(type(value[field]) in (int, float) and not isinstance(value[field], bool), label + "." + field + " is invalid")
    start = value.get("startedAt", value.get("startedAtUnix"))
    finish = value.get("finishedAt", value.get("finishedAtUnix"))
    if start is not None or finish is not None:
        require(start is not None and finish is not None and finish >= start, label + " interval is invalid")
    if "processId" in value:
        require(type(value["processId"]) is int and value["processId"] > 0, label + ".processId is invalid")
    if "exitCode" in value:
        require(type(value["exitCode"]) is int, label + ".exitCode is invalid")
    if "timedOut" in value:
        require(type(value["timedOut"]) is bool, label + ".timedOut is invalid")


def validate_sample_index(index: dict[str, Any], protocol_path: Path, schedule_path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    require(set(index) == {"schemaVersion", "kind", "protocol", "schedule", "buildMap", "attempts"},
            "sample index fields differ")
    require(index.get("schemaVersion") == 1, "sample index schemaVersion must be 1")
    require(index.get("kind") == "H1ControlledSamples", "sample index kind mismatch")
    protocol_binding = index.get("protocol")
    schedule_binding = index.get("schedule")
    build_binding = index.get("buildMap")
    protocol, schedule = _protocol_and_schedule(protocol_path, schedule_path)
    bound_protocol, _ = _receipt_binding(protocol_binding, "sample index protocol")
    bound_schedule, _ = _receipt_binding(schedule_binding, "sample index schedule")
    require(bound_protocol == protocol_path.resolve(), "sample index protocol path mismatch")
    require(bound_schedule == schedule_path.resolve(), "sample index schedule path mismatch")
    build_path, _ = _receipt_binding(build_binding, "sample index build map")
    build_map = read_json(build_path)
    attempts = index.get("attempts")
    require(type(attempts) is list, "sample index attempts must be an array")
    scheduled = {row["pairId"]: row for row in schedule["pairs"]}
    seen: set[tuple[str, int]] = set()
    for attempt in attempts:
        require(type(attempt) is dict, "sample attempt must be an object")
        pair_id, number = attempt.get("pairId"), attempt.get("attempt")
        require(pair_id in scheduled, "sample index contains an unscheduled pairId")
        require(type(number) is int and not isinstance(number, bool) and number >= 1, "attempt must be a positive integer")
        key = (pair_id, number)
        require(key not in seen, "duplicate sample attempt: " + pair_id + ":" + str(number))
        seen.add(key)
        require(set(attempt) >= {"pairId", "attempt", "A", "B"}, "sample attempt must contain pairId, attempt, A and B")
        scheduled_row = scheduled[pair_id]
        if "mode" in attempt:
            require(attempt["mode"] == scheduled_row["mode"], pair_id + ": diagnostic mode differs from schedule")
        if "phase" in attempt:
            require(attempt["phase"] == scheduled_row["phase"], pair_id + ": diagnostic phase differs from schedule")
        if "order" in attempt:
            require(attempt["order"] == scheduled_row["order"], pair_id + ": diagnostic order differs from schedule")
        for side in ("A", "B"):
            value = attempt[side]
            require(type(value) is dict, pair_id + "." + side + " must be an object")
            receipt = value.get("launchReceipt")
            if receipt is not None:
                _binding_shape(receipt, pair_id + "." + side + ".launchReceipt")
            _validate_diagnostic_side(value, pair_id + "." + side)
    scheduled_keys = set(scheduled)
    require({pair_id for pair_id, _ in seen} == scheduled_keys, "sample index must retain every scheduled pair, including pilots")
    return protocol, schedule, build_map, validate_build_map(build_map)


def _process_row(launch: dict[str, Any], mode: str) -> dict[str, Any]:
    rows = launch.get("processLaunches")
    require(type(rows) is list and len(rows) == 1, "single R00 launch must contain exactly one process row")
    row = rows[0]
    require(row.get("mode") == mode, "single R00 launch mode differs from schedule")
    require(type(row.get("startedAtUnix")) in (int, float) and not isinstance(row["startedAtUnix"], bool),
            "R00 launch start time is missing")
    require(type(row.get("durationSeconds")) in (int, float) and row["durationSeconds"] >= 0,
            "R00 launch duration is invalid")
    return row


def _all_process_intervals(launch_path: Path) -> tuple[list[tuple[float, float]], bool]:
    """Recover every process interval even when R00 verification failed."""
    try:
        launch = read_json(launch_path)
        rows = launch.get("processLaunches")
        require(type(rows) is list and rows, "process interval is unresolved")
        intervals = []
        for row in rows:
            require(type(row) is dict, "process interval row is unresolved")
            start, duration = row.get("startedAtUnix"), row.get("durationSeconds")
            require(type(start) in (int, float) and not isinstance(start, bool), "process start is unresolved")
            require(type(duration) in (int, float) and not isinstance(duration, bool) and duration >= 0,
                    "process duration is unresolved")
            intervals.append((float(start), float(start + duration)))
        return intervals, True
    except (VerificationError, OSError, KeyError, TypeError, ValueError):
        return [], False


def _diagnostic_intervals(value: dict[str, Any]) -> tuple[list[tuple[float, float]], bool]:
    try:
        start = value.get("startedAt", value.get("startedAtUnix"))
        finish = value.get("finishedAt", value.get("finishedAtUnix"))
        require(type(start) in (int, float) and type(finish) in (int, float), "diagnostic process interval is unresolved")
        require(finish >= start, "diagnostic process interval is invalid")
        return [(float(start), float(finish))], True
    except (VerificationError, TypeError, ValueError):
        return [], False


def _raw_result(launch_row: dict[str, Any]) -> dict[str, Any]:
    path = Path(launch_row["resultPath"]).resolve(strict=True)
    require(not path.is_symlink(), "R00 raw result must not be a symlink")
    require(digest(path) == launch_row.get("resultSha256"), "R00 raw result hash mismatch")
    return read_json(path)


def _check_build_binding(raw: dict[str, Any], expected: dict[str, Any]) -> None:
    actual = raw.get("playerBuildReceipt")
    require(type(actual) is dict, "R00 raw build receipt is missing")
    require(actual.get("path") == expected["path"], "R00 raw build receipt path is not the frozen side build")
    require(actual.get("sha256") == expected["sha256"], "R00 raw build receipt hash is not the frozen side build")
    frozen = expected["receipt"]
    for field in ("buildGuid", "baselineBuildId", "runtimeAbiHash"):
        if field in frozen:
            require(actual.get(field) == frozen[field], "R00 raw build field differs: " + field)


def _verify_raw(raw: dict[str, Any], mode: str) -> dict[str, Any]:
    require(raw.get("mode") == mode and raw.get("result") == "Passed", "R00 raw result is not a passed selected mode")
    operations = raw.get("operations")
    require(type(operations) is list, "R00 operations are missing")
    expected = [(operation, phase) for operation in OPERATIONS for phase in PHASES]
    require([(row.get("operation"), row.get("phase")) for row in operations] == expected,
            "R00 raw operation inventory differs")
    for row in operations:
        require(type(row.get("elapsedTicks")) is int and row["elapsedTicks"] >= 0, "R00 elapsed ticks are invalid")
        require(type(row.get("stopwatchFrequency")) is int and row["stopwatchFrequency"] > 0, "R00 stopwatch frequency is invalid")
        require(type(row.get("requestedIterations")) is int and row["requestedIterations"] > 0, "R00 iteration count is invalid")
    readiness = raw.get("readiness")
    require(type(readiness) is dict and readiness.get("businessReady") is True and
            type(readiness.get("businessReadyUtcTicks")) is int and readiness["businessReadyUtcTicks"] > 0,
            "R00 readiness is missing")
    snapshots = raw.get("memorySnapshots")
    require(type(snapshots) is list and [row.get("phase") for row in snapshots] == list(MEMORY_PHASES),
            "R00 memory snapshots must contain matched before/after phases")
    for row in snapshots:
        require(row.get("measurement") == MEMORY_MEASUREMENT, "R00 memory measurement method differs")
        require(row.get("measurementSemantics") == MEMORY_SEMANTICS, "R00 memory measurement semantics differ")
        for field in ("currentRssBytes", "managedBytes", "lifetimePeakRssBytes"):
            require(type(row.get(field)) is int and row[field] > 0, "R00 memory value must be positive: " + field)
        require(row["lifetimePeakRssBytes"] >= row["currentRssBytes"], "R00 lifetime peak is below current RSS")
        require(type(row.get("measurement")) is str and row["measurement"], "R00 memory measurement is missing")
        require(type(row.get("measurementSemantics")) is str and row["measurementSemantics"], "R00 memory semantics are missing")
    return raw


def verify_launch(launch_path: Path, mode: str, verifier: Callable[..., dict[str, Any]] | None = None,
                  expected_build: dict[str, Any] | None = None) -> dict[str, Any]:
    """Verify one scheduled launch and return its raw R00 data plus timing."""
    verify = verifier or r00_results.verify_suite
    try:
        verified = verify(launch_path, expected_mode=mode)
        require(verified.get("requestedModeIds") == [mode], "R00 verifier requested mode IDs differ")
        require(verified.get("executedModeIds") == [mode], "R00 verifier executed mode IDs differ")
        observations = verified.get("modes")
        require(type(observations) is list and len(observations) == 1, "R00 verifier must return one selected observation")
        startup_ms = observations[0].get("launchToBusinessReadyMilliseconds")
        require(type(startup_ms) in (int, float) and not isinstance(startup_ms, bool) and startup_ms >= 0,
                "verified R00 startup timing is missing")
        launch = read_json(launch_path)
        row = _process_row(launch, mode)
        raw = _verify_raw(_raw_result(row), mode)
        if expected_build is not None:
            _check_build_binding(raw, expected_build)
        return {"valid": True, "verified": verified, "launch": launch, "process": row, "raw": raw,
                "verifiedStartupMilliseconds": startup_ms}
    except (VerificationError, OSError, KeyError, TypeError, ValueError) as error:
        return {"valid": False, "error": str(error), "launchReceipt": str(launch_path), "mode": mode}


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def stats(values: list[float]) -> dict[str, float | int]:
    require(values, "statistics require at least one value")
    return {"n": len(values), "median": _percentile(values, .5), "iqr": _percentile(values, .75) - _percentile(values, .25),
            "min": min(values), "max": max(values)}


def paired_stats(values_a: list[float], values_b: list[float], ticks_a: list[int]) -> dict[str, Any]:
    differences = [b - a for a, b in zip(values_a, values_b)]
    ratios = [b / a for a, b, ticks in zip(values_a, values_b, ticks_a) if ticks >= 10 and a != 0]
    result = {"n": len(values_a), "A": stats(values_a), "B": stats(values_b), "pairedBMinusA": stats(differences),
              "pairedBRatioOverA": {"n": len(ratios), "suppressed": len(values_a) - len(ratios)}}
    if ratios:
        result["pairedBRatioOverA"].update(stats(ratios))
    return result


def _attempt_metrics(valid_attempt: dict[str, Any], schedule_row: dict[str, Any]) -> dict[str, Any]:
    sides = {side: valid_attempt[side] for side in ("A", "B")}
    metrics = {"pairId": schedule_row["pairId"], "attempt": valid_attempt["attempt"], "mode": schedule_row["mode"],
               "order": schedule_row["order"], "phase": schedule_row["phase"], "sides": {}}
    for side, item in sides.items():
        raw = item["raw"]
        rows = raw["operations"]
        metrics["sides"][side] = {
            "startedAtUnix": item["process"]["startedAtUnix"],
            "readinessMilliseconds": item["verifiedStartupMilliseconds"],
            "operations": {
                operation + ":" + phase: row["elapsedTicks"] / row["stopwatchFrequency"] / row["requestedIterations"]
                for row in rows for operation, phase in ((row["operation"], row["phase"]),)
            },
            "operationTicks": {operation + ":" + phase: row["elapsedTicks"] for row in rows for operation, phase in ((row["operation"], row["phase"]),)},
            "memory": {row["phase"]: {field: row[field] for field in ("currentRssBytes", "managedBytes", "lifetimePeakRssBytes")}
                       for row in raw["memorySnapshots"]},
            "memoryMetadata": {row["phase"]: {"measurement": row["measurement"],
                                                 "measurementSemantics": row["measurementSemantics"]}
                               for row in raw["memorySnapshots"]},
        }
    return metrics


def _aggregate(valid_metrics: list[dict[str, Any]], modes: tuple[str, ...] = MODES) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for mode in modes:
        rows = [row for row in valid_metrics if row["mode"] == mode and row["phase"] == "formal"]
        mode_out: dict[str, Any] = {"formalPairCount": len(rows), "operations": {}, "memory": {}}
        for operation in OPERATIONS:
            mode_out["operations"][operation] = {}
            for phase in PHASES:
                key = operation + ":" + phase
                a = [row["sides"]["A"]["operations"][key] for row in rows]
                b = [row["sides"]["B"]["operations"][key] for row in rows]
                ticks = [row["sides"]["A"]["operationTicks"][key] for row in rows]
                mode_out["operations"][operation][phase] = paired_stats(a, b, ticks) if rows else {"n": 0}
        for side in ("A", "B"):
            mode_out["memory"][side] = {}
            for phase in MEMORY_PHASES:
                mode_out["memory"][side][phase] = {}
                for field in ("currentRssBytes", "managedBytes", "lifetimePeakRssBytes"):
                    values = [row["sides"][side]["memory"][phase][field] for row in rows]
                    mode_out["memory"][side][phase][field] = stats(values) if values else {"n": 0}
                metadata = [row["sides"][side]["memoryMetadata"][phase] for row in rows]
                mode_out["memory"][side][phase]["metadata"] = metadata
            mode_out["memory"]["metadataMatch"] = {
                phase: all(row["sides"]["A"]["memoryMetadata"][phase] == row["sides"]["B"]["memoryMetadata"][phase]
                           for row in rows)
                for phase in MEMORY_PHASES
            }
            readiness = [row["sides"][side]["readinessMilliseconds"] for row in rows
                         if type(row["sides"][side]["readinessMilliseconds"]) in (int, float) and
                         row["sides"][side]["readinessMilliseconds"] >= 0]
            mode_out.setdefault("readinessMilliseconds", {})[side] = stats(readiness) if readiness else {"n": 0}
        output[mode] = mode_out
    return output


def analyze_sample_index(sample_index_path: Path, protocol_path: Path | None = None, schedule_path: Path | None = None,
                         verifier: Callable[..., dict[str, Any]] | None = None) -> dict[str, Any]:
    index_path = Path(sample_index_path).resolve(strict=True)
    index = read_json(index_path)
    if protocol_path is None:
        protocol_path = Path(index["protocol"]["path"])
    if schedule_path is None:
        schedule_path = Path(index["schedule"]["path"])
    protocol_path = Path(protocol_path).resolve(strict=True)
    schedule_path = Path(schedule_path).resolve(strict=True)
    protocol, schedule, build_map, comparability = validate_sample_index(index, protocol_path, schedule_path)
    build_bindings = comparability.pop("buildBindings", {})
    scheduled = {row["pairId"]: row for row in schedule["pairs"]}
    attempts_out: list[dict[str, Any]] = []
    valid_metrics: list[dict[str, Any]] = []
    intervals: list[tuple[float, float, str, str]] = []
    unresolved_intervals = False
    attempt_timestamps: list[tuple[str, str, float, float, str]] = []
    for attempt in index["attempts"]:
        pair_id, number = attempt["pairId"], attempt["attempt"]
        row = scheduled[pair_id]
        sides: dict[str, dict[str, Any]] = {}
        for side in ("A", "B"):
            binding = attempt[side].get("launchReceipt")
            resolved_interval = False
            try:
                side_value = attempt[side]
                if binding is None:
                    side_intervals, resolved_interval = _diagnostic_intervals(side_value)
                else:
                    path, _ = _receipt_binding(binding, pair_id + "." + side + ".launchReceipt")
                    side_intervals, resolved_interval = _all_process_intervals(path)
                if not resolved_interval:
                    unresolved_intervals = True
                for start, end in side_intervals:
                    intervals.append((start, end, pair_id + "." + side, row["phase"]))
                if binding is None:
                    sides[side] = {"valid": False, "error": side_value.get("error", "launch receipt unavailable"),
                                   "launchReceipt": None}
                else:
                    expected_build = build_bindings.get(side, {}).get(_build_world_key(row["mode"]))
                    if build_map.get("status") == "Frozen" and expected_build is None:
                        raise VerificationError("frozen build map has no " + side + " " + _build_world_key(row["mode"]) + " launch binding")
                    sides[side] = verify_launch(path, row["mode"], verifier, expected_build)
            except (VerificationError, OSError, KeyError, TypeError, ValueError) as error:
                if not resolved_interval:
                    unresolved_intervals = True
                sides[side] = {"valid": False, "error": str(error),
                               "launchReceipt": binding.get("path", "") if type(binding) is dict else None}
        valid = all(item["valid"] for item in sides.values())
        errors = {side: item.get("error", "") for side, item in sides.items() if not item["valid"]}
        if valid:
            ordered = row["order"]
            first = sides[ordered[0]]["process"]["startedAtUnix"]
            second = sides[ordered[1]]["process"]["startedAtUnix"]
            if first >= second:
                valid = False
                errors["chronology"] = "launch order differs from schedule"
            else:
                attempt_timestamps.append((pair_id, row["phase"], first, second, row["order"][0]))
        record = {"pairId": pair_id, "attempt": number, "mode": row["mode"], "phase": row["phase"], "order": row["order"],
                  "valid": valid, "sides": {side: {"valid": item["valid"], "error": item.get("error", "")} for side, item in sides.items()}}
        if valid:
            record["metrics"] = _attempt_metrics({"attempt": number, **sides}, row)
            valid_metrics.append(record["metrics"])
        else:
            record["errors"] = errors
        attempts_out.append(record)
    ordered_intervals = sorted(intervals)
    nonoverlap = all(previous[1] <= current[0] for previous, current in zip(ordered_intervals, ordered_intervals[1:]))
    pilot_intervals = [item for item in intervals if item[3] == "pilot"]
    formal_intervals = [item for item in intervals if item[3] == "formal"]
    pilots_before_formal = bool(pilot_intervals and formal_intervals) and max(item[1] for item in pilot_intervals) <= min(item[0] for item in formal_intervals)
    valid_by_pair: dict[str, dict[str, Any]] = {}
    for record in valid_metrics:
        current = valid_by_pair.get(record["pairId"])
        if current is None or record["attempt"] > current["attempt"]:
            valid_by_pair[record["pairId"]] = record
    selected = list(valid_by_pair.values())
    formal_selected = [row for row in selected if row["phase"] == "formal"]
    pilot_selected = [row for row in selected if row["phase"] == "pilot"]
    counts = {mode: len([row for row in formal_selected if row["mode"] == mode]) for mode in MODES}
    pilot_counts = {mode: len([row for row in pilot_selected if row["mode"] == mode]) for mode in MODES}
    formal_ok = all(counts[mode] == 10 for mode in MODES)
    pilot_ok = all(pilot_counts[mode] == 1 for mode in MODES)
    startup_counts = {mode: len([row for row in formal_selected if row["mode"] == mode and
                                  all(type(row["sides"][side]["readinessMilliseconds"]) in (int, float)
                                      for side in ("A", "B"))]) for mode in MODES}
    startup_ok = all(startup_counts[mode] == 10 for mode in MODES)
    chronology_ok = nonoverlap and pilots_before_formal and not unresolved_intervals
    sampling_ok = formal_ok and pilot_ok and startup_ok and chronology_ok
    status = comparability["status"] if comparability["status"] != "ComparabilityPassed" else "ComparabilityPassed" if sampling_ok else "ComparabilityIncomplete"
    return {"schemaVersion": 1, "kind": "H1ControlledPairedPerformanceSummary", "result": "Passed" if status == "ComparabilityPassed" else "Incomplete",
            "status": status, "protocol": {"path": str(protocol_path), "sha256": digest(protocol_path)},
            "schedule": {"path": str(schedule_path), "sha256": digest(schedule_path)},
            "buildMap": {"path": str(Path(index["buildMap"]["path"]).resolve()), "sha256": digest(Path(index["buildMap"]["path"]).resolve())},
            "requirements": {"formalPairsPerMode": counts, "pilotPairsPerMode": pilot_counts,
                             "formalStartupObservationsPerMode": startup_counts,
                             "formalComplete": formal_ok, "pilotsComplete": pilot_ok,
                             "startupComplete": startup_ok, "chronologyComplete": chronology_ok,
                             "globalIntervalsResolved": not unresolved_intervals,
                             "globalIntervalsNonOverlapping": nonoverlap,
                             "pilotsBeforeFormalByTimestamp": pilots_before_formal},
            "comparability": comparability, "attempts": attempts_out, "statistics": _aggregate(selected)}


analyze = analyze_sample_index
