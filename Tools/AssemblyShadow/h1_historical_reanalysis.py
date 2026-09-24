#!/usr/bin/env python3
"""Authenticate and reanalyze the immutable H1 27df formal series under an analysis-only successor.

This compatibility path is intentionally fixed to the completed Local series
produced at source 27df1a3d... / checkout f5e34235....  It does not authorize
historical execution, bridge reuse for new Players, or arbitrary source deltas.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import h1_paired_performance as paired
import r00_results
import shadow_tools
from shadow_tools import PINS, VerificationError, metadata_only, read_json, require

HISTORICAL_SOURCE_REVISION = "27df1a3d60811dc121f296ab561ae313a382b363"
HISTORICAL_CHECKOUT_REVISION = "f5e34235641c212c715aef3405925ddd4cf28ee6"
RETAINED_GRAPH_REVISION = "69130bbb3a6df516916dddb5ad263799a7c6e5e3"
POLICY_ID = "H1HistoricalPerformanceReanalysis-v2"
HISTORICAL_BRIDGE_SHA256 = "c03665dbdba797f5024fa8f376e6ac6aa6edf165c76387ddbf01ee6d3611826c"
HISTORICAL_SEAL_SHA256 = "bdc4062acfc6d208a9be50a142b897a07e7359e5df14ad3d3d8f2805c5179631"
HISTORICAL_FINAL_SAMPLE_SHA256 = "a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021"
HISTORICAL_FORMAL_BATCH_SHA256 = "97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667"
BRIDGE_KIND = "H1GraphReuseBridge"
SEAL_KIND = "H1PilotVerificationReceipt"
FORMAL_AUTHORITY_KIND = "H1FormalSideLaunchAuthority"
PAIRING_AUTHORITY_KIND = "H1AuthenticatedGraphReuseAuthority"

# Exact analysis/test-only successor scope from the completed 27df formal series.
# The two additional v2 paths are bounded-regression/test-fixture code only. No
# execution runner, measurement, graph, protocol, schedule, Player or native
# source may change under this compatibility policy.
ALLOWED_ANALYSIS_DELTA = frozenset({
    "Tools/AssemblyShadow/README.md",
    "Tools/AssemblyShadow/h1_bee_primary_tests.py",
    "Tools/AssemblyShadow/h1_graph_reuse.py",
    "Tools/AssemblyShadow/h1_historical_reanalysis.py",
    "Tools/AssemblyShadow/h1_paired_performance.py",
    "Tools/AssemblyShadow/tests/test_h1_graph_reuse.py",
    "Tools/AssemblyShadow/tests/test_h1_paired_performance.py",
})

HISTORICAL_BRIDGE_VERIFIER_PATHS = frozenset({
    "Tools/AssemblyShadow/h1_graph_reuse.py",
    "Tools/AssemblyShadow/h1_formal_launch_authority.py",
    "Tools/AssemblyShadow/run-r00-players.py",
    "Tools/AssemblyShadow/r00_player_inputs.py",
    "Tools/AssemblyShadow/r00_results.py",
    "Tools/AssemblyShadow/r01_early_results.py",
    "Tools/AssemblyShadow/m07_results.py",
    "Tools/AssemblyShadow/shadow_tools.py",
})

HISTORICAL_SEAL_VERIFIER_PATHS = frozenset({
    "Tools/AssemblyShadow/run-h1-paired-performance.py",
    "Tools/AssemblyShadow/seal-h1-pilot-verification.py",
    "Tools/AssemblyShadow/h1_paired_performance.py",
    "Tools/AssemblyShadow/h1_graph_reuse.py",
    "Tools/AssemblyShadow/h1_formal_launch_authority.py",
    "Tools/AssemblyShadow/r00_results.py",
    "Tools/AssemblyShadow/r00_player_inputs.py",
    "Tools/AssemblyShadow/run-r00-players.py",
    "Tools/AssemblyShadow/run-m07-players.py",
    "Tools/AssemblyShadow/m07_results.py",
    "Tools/AssemblyShadow/r01_early_results.py",
    "Tools/AssemblyShadow/r01_early_capsule.py",
    "Tools/AssemblyShadow/shadow_tools.py",
})

HISTORICAL_FORMAL_AUTHORITY_TOOL_PATHS = frozenset({
    "Tools/AssemblyShadow/h1_formal_launch_authority.py",
    "Tools/AssemblyShadow/h1_graph_reuse.py",
    "Tools/AssemblyShadow/run-h1-paired-performance.py",
    "Tools/AssemblyShadow/run-r00-players.py",
    "Tools/AssemblyShadow/r00_player_inputs.py",
    "Tools/AssemblyShadow/r00_results.py",
    "Tools/AssemblyShadow/r01_early_results.py",
})


def digest(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "Expected regular file: " + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(path: Path) -> dict[str, str]:
    path = canonical_file(path, "bound file")
    return {"path": str(path), "sha256": digest(path)}


def canonical_file(value: str | Path, label: str) -> Path:
    raw = Path(value)
    require(raw.is_absolute() and not raw.is_symlink(), label + " must be an absolute non-symlink path")
    path = raw.resolve(strict=True)
    require(path == raw and path.is_file() and not path.is_symlink(),
            label + " must be a canonical regular file")
    return path


def canonical_dir(value: str | Path, label: str) -> Path:
    raw = Path(value)
    require(raw.is_absolute() and not raw.is_symlink(), label + " must be an absolute non-symlink path")
    path = raw.resolve(strict=True)
    require(path == raw and path.is_dir() and not path.is_symlink(),
            label + " must be a canonical directory")
    return path


def json_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _entries(pins: dict[str, Any]) -> dict[str, Any]:
    require(type(pins) is dict and pins.get("schemaVersion") == 1, "Unsupported source pin schema")
    entries = pins.get("repositories", pins)
    require(type(entries) is dict, "Source pin repositories are missing")
    for name in shadow_tools.REPOSITORIES:
        require(type(entries.get(name)) is dict, "Missing source pin repository: " + name)
    return entries


def _git_bytes(project: Path, revision: str, relative: str) -> bytes:
    return shadow_tools.git(project, "show", revision + ":" + relative)


def _git_sha256(project: Path, revision: str, relative: str) -> str:
    return hashlib.sha256(_git_bytes(project, revision, relative)).hexdigest()


def _git_json(project: Path, revision: str, relative: str) -> dict[str, Any]:
    raw = _git_bytes(project, revision, relative)
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=shadow_tools.unique_object)
    except (UnicodeError, ValueError) as error:
        raise VerificationError(
            "Invalid historical JSON " + revision + ":" + relative + ": " + str(error)) from error
    require(type(value) is dict, "Historical JSON must be an object: " + relative)
    return value


def _tree_delta(project: Path, old_revision: str, new_revision: str) -> list[dict[str, Any]]:
    old_tree = shadow_tools.tree(project, old_revision)
    new_tree = shadow_tools.tree(project, new_revision)
    changed = sorted(
        path for path in set(old_tree) | set(new_tree)
        if old_tree.get(path) != new_tree.get(path) and not metadata_only(path)
    )
    return [
        {
            "path": path,
            "oldBlob": old_tree.get(path),
            "newBlob": new_tree.get(path),
            "status": "Added" if path not in old_tree else
                      "Deleted" if path not in new_tree else "Modified",
        }
        for path in changed
    ]


def authenticate_analysis_delta(project: Path, current_revision: str) -> dict[str, Any]:
    project = project.resolve(strict=True)
    require(type(current_revision) is str and len(current_revision) == 40,
            "Current analysis source revision is invalid")
    shadow_tools.git(project, "merge-base", "--is-ancestor",
                     HISTORICAL_SOURCE_REVISION, current_revision)
    rows = _tree_delta(project, HISTORICAL_SOURCE_REVISION, current_revision)
    changed = {row["path"] for row in rows}
    require(changed == set(ALLOWED_ANALYSIS_DELTA),
            "Historical analysis successor delta differs from the exact policy: " +
            json.dumps({
                "missing": sorted(ALLOWED_ANALYSIS_DELTA - changed),
                "extra": sorted(changed - ALLOWED_ANALYSIS_DELTA),
            }))
    return {
        "policyId": POLICY_ID,
        "historicalSourceRevision": HISTORICAL_SOURCE_REVISION,
        "historicalCheckoutRevision": HISTORICAL_CHECKOUT_REVISION,
        "currentSourceRevision": current_revision,
        "nonMetadataDelta": rows,
        "nonMetadataDeltaSha256": json_digest(rows),
    }


def _historical_current_pins(graph_pins: dict[str, Any]) -> dict[str, Any]:
    pins = copy.deepcopy(graph_pins)
    _entries(pins)["demo"]["revision"] = HISTORICAL_SOURCE_REVISION
    return pins


def _current_source_pins(project: Path) -> dict[str, Any]:
    pins_path = canonical_file(project / PINS, "current source pins")
    pins = read_json(pins_path)
    current = _entries(pins)["demo"].get("revision")
    require(type(current) is str and len(current) == 40,
            "Current demo source revision is invalid")
    return pins


def _historical_tool_binding(project: Path, relative: str) -> dict[str, str]:
    path = (project / relative).resolve(strict=True)
    require(path.is_relative_to(project) and path.is_file() and not path.is_symlink(),
            "Historical tool path is unavailable: " + relative)
    return {"path": relative, "sha256": _git_sha256(project, HISTORICAL_SOURCE_REVISION, relative)}


def _verify_historical_tool_rows(project: Path, rows: Any, label: str,
                                 *, exact_paths: set[str] | None = None,
                                 absolute_paths: bool = False) -> None:
    require(type(rows) is list and rows, label + " tool bindings are missing")
    actual_paths: set[str] = set()
    for row in rows:
        require(type(row) is dict and type(row.get("sha256")) is str,
                label + " tool binding is invalid")
        raw_path = row.get("path")
        require(type(raw_path) is str and raw_path, label + " tool path is missing")
        if absolute_paths:
            path = Path(raw_path).resolve(strict=True)
            require(path.is_relative_to(project), label + " tool escaped the demo project")
            relative = path.relative_to(project).as_posix()
        else:
            relative = raw_path
            path = (project / relative).resolve(strict=True)
            require(path.is_relative_to(project), label + " tool escaped the demo project")
        require(row["sha256"] == _git_sha256(project, HISTORICAL_SOURCE_REVISION, relative),
                label + " historical tool hash mismatch: " + relative)
        actual_paths.add(relative)
    if exact_paths is not None:
        require(actual_paths == exact_paths,
                label + " historical tool inventory differs from expected policy")


def verify_historical_bridge(bridge_path: Path, build_map_path: Path,
                             project: Path) -> dict[str, Any]:
    bridge_path = canonical_file(bridge_path, "historical graph bridge")
    build_map_path = canonical_file(build_map_path, "historical build map")
    project = canonical_dir(project, "candidate project")
    value = read_json(bridge_path)

    require(value.get("schemaVersion") == 1 and value.get("kind") == BRIDGE_KIND and
            value.get("status") == "AuthenticatedToolOnlySuccessor" and value.get("side") == "B",
            "Historical graph bridge header mismatch")
    require(value.get("projectRoot") == str(project), "Historical graph bridge project mismatch")
    require(value.get("buildMap") == binding(build_map_path),
            "Historical graph bridge build-map binding mismatch")

    graph_pins = value.get("graphSourcePins")
    require(type(graph_pins) is dict and
            _entries(graph_pins)["demo"].get("revision") == RETAINED_GRAPH_REVISION,
            "Historical bridge retained graph source mismatch")
    require(value.get("graphSourcePinsSha256") == json_digest(graph_pins),
            "Historical bridge graph source-pin digest mismatch")

    historical_pins = _historical_current_pins(graph_pins)
    source_pin_bytes = _git_bytes(project, HISTORICAL_CHECKOUT_REVISION, PINS)
    require(value.get("currentSourcePins") == {
                "path": str((project / PINS).resolve()),
                "sha256": hashlib.sha256(source_pin_bytes).hexdigest(),
            },
            "Historical bridge current source-pin file binding mismatch")
    require(value.get("currentSourcePinsObjectSha256") == json_digest(historical_pins),
            "Historical bridge current source-pin object mismatch")

    transition = value.get("transition")
    require(type(transition) is dict and
            transition.get("policyId") == "H1V04RetainedGraphToolOnlySuccessor-v1" and
            transition.get("graphDemoRevision") == RETAINED_GRAPH_REVISION and
            transition.get("currentDemoRevision") == HISTORICAL_SOURCE_REVISION,
            "Historical bridge transition header mismatch")
    require(transition.get("graphSourcePinsSha256") == json_digest(graph_pins) and
            transition.get("currentSourcePinsSha256") == json_digest(historical_pins),
            "Historical bridge transition source-pin digest mismatch")
    transition_rows = _tree_delta(project, RETAINED_GRAPH_REVISION, HISTORICAL_SOURCE_REVISION)
    require(transition.get("nonMetadataDelta") == transition_rows and
            transition.get("nonMetadataDeltaSha256") == json_digest(transition_rows),
            "Historical bridge transition Git proof mismatch")

    _verify_historical_tool_rows(
        project, value.get("verifierBindings"), "Historical bridge",
        exact_paths=set(HISTORICAL_BRIDGE_VERIFIER_PATHS))

    retained = value.get("retainedPilotRunner")
    require(type(retained) is dict and
            retained.get("path") == str((project / "Tools/AssemblyShadow/run-r00-players.py").resolve()) and
            retained.get("sha256") ==
                _git_sha256(project, RETAINED_GRAPH_REVISION,
                            "Tools/AssemblyShadow/run-r00-players.py"),
            "Historical bridge retained pilot runner mismatch")

    installed = value.get("installedRuntimeVerification")
    require(type(installed) is dict and installed.get("demoSourceVerified") is True and
            installed.get("configuredShadowMode") == "on" and
            installed.get("unityVersion") == graph_pins.get("unityVersion") and
            installed.get("target") == graph_pins.get("target") and
            type(installed.get("receiptSha256")) is str and len(installed["receiptSha256"]) == 64,
            "Historical bridge installed-runtime evidence is incomplete")

    current_pins = _current_source_pins(project)
    current_entries = _entries(current_pins)
    historical_entries = _entries(historical_pins)
    for key in ("unityVersion", "target", "architecture"):
        require(current_pins.get(key) == historical_pins.get(key),
                "Analysis successor changed platform source pins: " + key)
    for name in ("hybridclr", "hybridclrUnity", "il2cppPlus"):
        require(current_entries[name] == historical_entries[name],
                "Analysis successor changed runtime repository pin: " + name)

    return {
        "historicalBridge": binding(bridge_path),
        "graphSourcePins": graph_pins,
        "historicalCurrentSourcePins": historical_pins,
        "currentSourcePins": current_pins,
        "retainedPilotRunner": retained,
        "transitionSha256": transition["nonMetadataDeltaSha256"],
    }


def verify_historical_seal(seal_path: Path, bridge_path: Path,
                           sample_index: dict[str, Any], project: Path) -> dict[str, Any]:
    seal_path = canonical_file(seal_path, "historical pilot seal")
    bridge_path = canonical_file(bridge_path, "historical graph bridge")
    value = read_json(seal_path)
    require(value.get("schemaVersion") == 1 and value.get("kind") == SEAL_KIND and
            value.get("status") == "PassedStrictReconstructionAndStatGuardSealed",
            "Historical pilot seal header mismatch")
    for key in ("protocol", "schedule", "buildMap"):
        require(value.get(key) == sample_index.get(key),
                "Historical pilot seal binding mismatch: " + key)
    require(value.get("graphReuseBridge") == binding(bridge_path),
            "Historical pilot seal bridge binding mismatch")
    require(value.get("guardKind") == "CrossRemountStableStatGuard" and
            value.get("guardVersion") == 2 and
            value.get("guardFields") == ["inode", "mode", "size", "mtimeNs", "ctimeNs"],
            "Historical pilot seal guard-v2 contract mismatch")
    _verify_historical_tool_rows(
        project, value.get("verifierBindings"), "Historical pilot seal",
        exact_paths=set(HISTORICAL_SEAL_VERIFIER_PATHS), absolute_paths=True)
    source_pilot = value.get("sourcePilotIndex")
    require(type(source_pilot) is dict, "Historical seal source pilot index is missing")
    source_pilot_path = canonical_file(source_pilot.get("path", ""), "historical source pilot index")
    require(source_pilot == binding(source_pilot_path),
            "Historical seal source pilot index binding mismatch")
    require(value.get("deepLaunchVerificationCount") == 8 and
            type(value.get("selectedPilots")) is list and len(value["selectedPilots"]) == 4,
            "Historical pilot seal strict verification summary mismatch")
    return {
        "historicalSeal": binding(seal_path),
        "sourcePilotIndex": binding(source_pilot_path),
        "fileCount": value.get("fileCount"),
        "fileInventorySha256": value.get("fileInventorySha256"),
        "guardInventorySha256": value.get("guardInventorySha256"),
    }


def _bound(value: Any, label: str) -> Path:
    require(type(value) is dict and set(value) == {"path", "sha256"},
            label + " binding must contain path/sha256")
    path = canonical_file(value.get("path", ""), label)
    require(value.get("sha256") == digest(path), label + " binding hash mismatch")
    return path


def _verify_historical_formal_authority(authority_binding: dict[str, Any],
                                        attempt: dict[str, Any],
                                        protocol_binding: dict[str, Any],
                                        schedule_binding: dict[str, Any],
                                        build_map_binding: dict[str, Any],
                                        bridge_binding: dict[str, Any],
                                        seal_binding: dict[str, Any],
                                        project: Path,
                                        graph_pins: dict[str, Any],
                                        historical_pins: dict[str, Any]) -> None:
    path = _bound(authority_binding, "historical formal launch authority")
    value = read_json(path)
    require(value.get("schemaVersion") == 1 and
            value.get("kind") == FORMAL_AUTHORITY_KIND and
            value.get("status") == "AuthenticatedRetainedCandidateFormalLaunch" and
            value.get("side") == "B",
            "Historical formal authority header mismatch")
    require(value.get("pairId") == attempt.get("pairId") and
            value.get("attempt") == attempt.get("attempt") and
            value.get("mode") == attempt.get("mode") and
            value.get("pairOrder") == attempt.get("order"),
            "Historical formal authority pair identity mismatch")
    require(value.get("projectRoot") == str(project),
            "Historical formal authority project mismatch")
    for key, expected in (
        ("protocol", protocol_binding),
        ("schedule", schedule_binding),
        ("buildMap", build_map_binding),
        ("graphReuseBridge", bridge_binding),
        ("pilotVerification", seal_binding),
    ):
        require(value.get(key) == expected,
                "Historical formal authority binding mismatch: " + key)
    for key in ("fixtureManifest", "nativeOnReceipt", "nativeOffReceipt", "editorReplayReceipt"):
        _bound(value.get(key), "historical formal authority " + key)
    output_root = Path(value.get("runnerOutputRoot", ""))
    require(output_root.is_absolute(), "Historical formal authority output root is invalid")

    _verify_historical_tool_rows(
        project, value.get("toolBindings"), "Historical formal authority",
        exact_paths=set(HISTORICAL_FORMAL_AUTHORITY_TOOL_PATHS))
    require(value.get("pairingPolicyId") == "H1V04RetainedGraphToolOnlySuccessor-v1" and
            value.get("graphSourcePins") == graph_pins and
            value.get("currentSourcePins") == historical_pins,
            "Historical formal authority pairing identity mismatch")


def verify_historical_formal_batch(formal_batch_path: Path, sample_index_path: Path,
                                   seal_path: Path, bridge_path: Path,
                                   sample_index: dict[str, Any]) -> dict[str, Any]:
    formal_batch_path = canonical_file(formal_batch_path, "historical formal batch")
    require(digest(formal_batch_path) == HISTORICAL_FORMAL_BATCH_SHA256,
            "Historical reanalysis is limited to the authenticated 27df formal batch")
    value = read_json(formal_batch_path)
    require(value.get("schemaVersion") == 1 and value.get("kind") == "H1FormalBatchRun" and
            value.get("status") == "PassedAllFormalPairs",
            "Historical formal batch header mismatch")
    require(value.get("formalPairCount") == 40 and value.get("formalPairsPassed") == 40,
            "Historical formal batch is not the completed 40/40 series")
    require(value.get("finalSampleIndex") == binding(sample_index_path),
            "Historical formal batch final sample binding mismatch")
    require(value.get("graphReuseBridge") == binding(bridge_path) and
            value.get("pilotVerification") == binding(seal_path),
            "Historical formal batch switched bridge or seal")
    for key in ("protocol", "schedule", "buildMap"):
        require(value.get(key) == sample_index.get(key),
                "Historical formal batch binding mismatch: " + key)
    runs = value.get("runs")
    require(type(runs) is list and len(runs) == 40,
            "Historical formal batch must retain exactly 40 pair runs")
    require(all(type(row) is dict and row.get("exitCode") == 0 and
                type(row.get("sampleIndex")) is dict for row in runs),
            "Historical formal batch contains an unsuccessful or unbound run")
    return {
        "historicalFormalBatch": binding(formal_batch_path),
        "formalPairCount": 40,
        "formalPairsPassed": 40,
    }


def verify_historical_sample_chain(sample_index_path: Path, seal_path: Path,
                                   bridge_path: Path, project: Path,
                                   bridge_info: dict[str, Any]) -> dict[str, Any]:
    sample_index_path = canonical_file(sample_index_path, "historical final sample index")
    value = read_json(sample_index_path)
    require(value.get("schemaVersion") == 1 and value.get("kind") == "H1ControlledSamples",
            "Historical sample index schema mismatch")
    for key in ("protocol", "schedule", "buildMap"):
        _bound(value.get(key), "historical sample " + key)

    bridge_binding = binding(bridge_path)
    seal_binding = binding(seal_path)
    attempts = value.get("attempts")
    require(type(attempts) is list and attempts, "Historical sample attempts are missing")

    historical_runner = {
        "path": str((project / "Tools/AssemblyShadow/run-r00-players.py").resolve()),
        "sha256": _git_sha256(project, HISTORICAL_SOURCE_REVISION,
                              "Tools/AssemblyShadow/run-r00-players.py"),
    }
    retained_runner = bridge_info["retainedPilotRunner"]

    formal_count = 0
    for attempt in attempts:
        require(type(attempt) is dict and attempt.get("phase") in ("pilot", "formal"),
                "Historical sample attempt is invalid")
        for side in ("A", "B"):
            diagnostic = attempt.get(side)
            require(type(diagnostic) is dict, "Historical sample side diagnostic is missing")
            expected_runner = retained_runner if attempt["phase"] == "pilot" else historical_runner
            require(diagnostic.get("runner") == expected_runner,
                    "Historical sample runner provenance mismatch")
            launch_binding = diagnostic.get("launchReceipt")
            if launch_binding is not None:
                _bound(launch_binding, "historical sample launch receipt")

        if attempt["phase"] != "formal":
            continue
        formal_count += 1
        require(attempt.get("graphReuseBridge") == bridge_binding and
                attempt.get("pilotVerification") == seal_binding,
                "Historical formal attempt switched bridge or seal")
        require(attempt["A"].get("formalLaunchAuthority") is None,
                "Historical protected side A carried retained authority")
        b = attempt["B"]
        auth_binding = b.get("formalLaunchAuthority")
        require(type(auth_binding) is dict,
                "Historical candidate side B is missing formal launch authority")
        _verify_historical_formal_authority(
            auth_binding, attempt, value["protocol"], value["schedule"], value["buildMap"],
            bridge_binding, seal_binding, project,
            bridge_info["graphSourcePins"], bridge_info["historicalCurrentSourcePins"])
        launch_binding = b.get("launchReceipt")
        if launch_binding is not None:
            launch_path = _bound(launch_binding, "historical formal B launch receipt")
            launch = read_json(launch_path)
            require(launch.get("formalLaunchAuthority") == auth_binding and
                    launch.get("graphReuseBridge") == bridge_binding and
                    launch.get("pilotVerification") == seal_binding and
                    launch.get("buildMap") == value["buildMap"],
                    "Historical formal B launch receipt authority chain mismatch")

    require(formal_count == 40,
            "Historical completed series must contain exactly 40 formal attempts")
    return {
        "historicalSampleIndex": binding(sample_index_path),
        "attemptCount": len(attempts),
        "formalAttemptCount": formal_count,
    }


def authenticate_compatibility(sample_index_path: Path, seal_path: Path,
                               bridge_path: Path, formal_batch_path: Path) -> dict[str, Any]:
    sample_index_path = canonical_file(sample_index_path, "historical final sample index")
    seal_path = canonical_file(seal_path, "historical pilot seal")
    bridge_path = canonical_file(bridge_path, "historical graph bridge")
    formal_batch_path = canonical_file(formal_batch_path, "historical formal batch")
    require(digest(sample_index_path) == HISTORICAL_FINAL_SAMPLE_SHA256,
            "Historical reanalysis is limited to the authenticated 27df final sample index")
    require(digest(seal_path) == HISTORICAL_SEAL_SHA256,
            "Historical reanalysis is limited to the authenticated 27df pilot seal")
    require(digest(bridge_path) == HISTORICAL_BRIDGE_SHA256,
            "Historical reanalysis is limited to the authenticated 27df graph bridge")
    require(digest(formal_batch_path) == HISTORICAL_FORMAL_BATCH_SHA256,
            "Historical reanalysis is limited to the authenticated 27df formal batch")

    bridge_value = read_json(bridge_path)
    project = canonical_dir(bridge_value.get("projectRoot", ""), "candidate project")
    sample = read_json(sample_index_path)
    build_map_path = _bound(sample.get("buildMap"), "historical build map")

    current_pins = _current_source_pins(project)
    current_revision = _entries(current_pins)["demo"]["revision"]
    delta = authenticate_analysis_delta(project, current_revision)
    bridge_info = verify_historical_bridge(bridge_path, build_map_path, project)
    seal_info = verify_historical_seal(seal_path, bridge_path, sample, project)
    batch_info = verify_historical_formal_batch(
        formal_batch_path, sample_index_path, seal_path, bridge_path, sample)
    sample_info = verify_historical_sample_chain(
        sample_index_path, seal_path, bridge_path, project, bridge_info)

    pairing_authority = {
        "kind": PAIRING_AUTHORITY_KIND,
        "projectRoot": str(project),
        "graphSourcePins": bridge_info["graphSourcePins"],
        "currentSourcePins": current_pins,
        "bridgeReceipt": binding(bridge_path),
        "policyId": POLICY_ID,
    }
    return {
        "schemaVersion": 1,
        "kind": "H1HistoricalAnalysisCompatibility",
        "status": "AuthenticatedAnalysisOnlySuccessor",
        "policyId": POLICY_ID,
        "projectRoot": str(project),
        "analysisDelta": delta,
        "historicalBridge": bridge_info,
        "historicalSeal": seal_info,
        "historicalFormalBatch": batch_info,
        "historicalSeries": sample_info,
        "authenticatedEvidenceSha256": {
            "graphReuseBridge": HISTORICAL_BRIDGE_SHA256,
            "pilotVerification": HISTORICAL_SEAL_SHA256,
            "finalSampleIndex": HISTORICAL_FINAL_SAMPLE_SHA256,
            "formalBatch": HISTORICAL_FORMAL_BATCH_SHA256,
        },
        "pairingAuthority": pairing_authority,
    }


def _write_new(path: Path, value: dict[str, Any]) -> None:
    require(path.is_absolute() and path == path.resolve() and
            not path.exists() and not path.is_symlink(),
            "Historical reanalysis output must be a new canonical absolute path")
    require(path.parent.is_dir() and not path.parent.is_symlink(),
            "Historical reanalysis output parent is unavailable")
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def _historical_verified_launch(compatibility: dict[str, Any]):
    authority = compatibility["pairingAuthority"]
    candidate = Path(compatibility["projectRoot"]).resolve(strict=True)

    def verify(launch_path: Path, expected_mode: str | None = None) -> dict[str, Any]:
        launch = read_json(Path(launch_path))
        project = Path(launch["projectRoot"]).resolve(strict=True)
        pairing = authority if project == candidate else None
        return r00_results.verify_suite(
            launch_path, expected_mode=expected_mode, pairing_authority=pairing)

    return verify


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-index", required=True, type=Path)
    parser.add_argument("--pilot-verification-receipt", required=True, type=Path)
    parser.add_argument("--graph-reuse-bridge", required=True, type=Path)
    parser.add_argument("--formal-batch", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args(argv)

    output = args.output
    try:
        compatibility = authenticate_compatibility(
            args.sample_index, args.pilot_verification_receipt,
            args.graph_reuse_bridge, args.formal_batch)
        public_compatibility = copy.deepcopy(compatibility)
        public_compatibility.pop("pairingAuthority", None)
        if args.preflight_only:
            result = public_compatibility
        else:
            summary = paired.analyze_sample_index(
                args.sample_index, verifier=_historical_verified_launch(compatibility))
            summary["historicalAnalysisCompatibility"] = public_compatibility
            result = summary
    except Exception as error:
        result = {
            "schemaVersion": 1,
            "kind": "H1HistoricalPerformanceReanalysisFailure",
            "result": "Failed",
            "error": str(error),
            "sampleIndex": str(Path(args.sample_index).resolve()),
        }
        _write_new(output, result)
        print("Historical H1 reanalysis Failed: " + str(output), flush=True)
        return 1

    _write_new(output, result)
    status = result.get("result", result.get("status", "Passed"))
    print("Historical H1 reanalysis " + str(status) + ": " + str(output), flush=True)
    if args.preflight_only:
        return 0
    return 0 if result.get("result") == "Passed" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (VerificationError, OSError, KeyError, TypeError, ValueError) as error:
        print("[FAIL] " + str(error), flush=True)
        raise SystemExit(1)
