"""Fail-closed authentication for reusing the retained 69130bbb H1 performance graph.

This module does not weaken normal R00 source-pairing verification.  It creates a
narrow authority object only after proving that the graph's demo source revision
is the retained V04 anchor and that every non-metadata successor change is in the
reviewed performance-admission tooling/test/CI set.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import shadow_tools
from shadow_tools import PINS, VerificationError, metadata_only, read_json, require

GRAPH_SOURCE_REVISION = "69130bbb3a6df516916dddb5ad263799a7c6e5e3"
POLICY_ID = "H1V04RetainedGraphToolOnlySuccessor-v1"
RECEIPT_KIND = "H1GraphReuseBridge"
AUTHORITY_KIND = "H1AuthenticatedGraphReuseAuthority"

# Exact non-metadata delta permitted between the retained profile-2 graph source
# and the current source anchor.  No Assets/, Packages/, runtime/native source,
# performance protocol/schedule/map producer, Player runner, or measurement
# source is in this set.
ALLOWED_NON_METADATA_PATHS = frozenset({
    ".github/workflows/h1-bee-primary.yml",
    "Tools/AssemblyShadow/README.md",
    "Tools/AssemblyShadow/analyze-h1-paired-performance.py",
    "Tools/AssemblyShadow/create-h1-graph-reuse-bridge.py",
    "Tools/AssemblyShadow/h1_bee_primary_tests.py",
    "Tools/AssemblyShadow/h1_graph_reuse.py",
    "Tools/AssemblyShadow/h1_formal_launch_authority.py",
    "Tools/AssemblyShadow/r00_player_inputs.py",
    "Tools/AssemblyShadow/r00_results.py",
    "Tools/AssemblyShadow/r01_early_results.py",
    "Tools/AssemblyShadow/run-h1-formal-batch.py",
    "Tools/AssemblyShadow/run-h1-paired-performance.py",
    "Tools/AssemblyShadow/run-r00-players.py",
    "Tools/AssemblyShadow/seal-h1-pilot-verification.py",
    "Tools/AssemblyShadow/tests/test_h1_formal_batch.py",
    "Tools/AssemblyShadow/tests/test_h1_formal_launch_authority.py",
    "Tools/AssemblyShadow/tests/test_h1_graph_reuse.py",
    "Tools/AssemblyShadow/tests/test_h1_paired_driver.py",
    "Tools/AssemblyShadow/tests/test_h1_retained_early_preflight.py",
    "Tools/AssemblyShadow/verify-h1-retained-early-reuse.py",
})

VERIFIER_PATHS = (
    "Tools/AssemblyShadow/h1_graph_reuse.py",
    "Tools/AssemblyShadow/h1_formal_launch_authority.py",
    "Tools/AssemblyShadow/run-r00-players.py",
    "Tools/AssemblyShadow/r00_player_inputs.py",
    "Tools/AssemblyShadow/r00_results.py",
    "Tools/AssemblyShadow/r01_early_results.py",
    "Tools/AssemblyShadow/m07_results.py",
    "Tools/AssemblyShadow/shadow_tools.py",
)


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
    require(path == raw and path.is_file() and not path.is_symlink(), label + " must be a canonical regular file")
    return path


def canonical_dir(value: str | Path, label: str) -> Path:
    raw = Path(value)
    require(raw.is_absolute() and not raw.is_symlink(), label + " must be an absolute non-symlink path")
    path = raw.resolve(strict=True)
    require(path == raw and path.is_dir() and not path.is_symlink(), label + " must be a canonical directory")
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


def retained_graph_pins(current_pins: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct the exact expected retained-graph DTO from current runtime/platform pins."""
    graph = copy.deepcopy(current_pins)
    entries = _entries(graph)
    entries["demo"]["revision"] = GRAPH_SOURCE_REVISION
    return graph


def _git_json(project: Path, revision: str, relative: str) -> dict[str, Any]:
    raw = shadow_tools.git(project, "show", revision + ":" + relative)
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=shadow_tools.unique_object)
    except (UnicodeError, ValueError) as error:
        raise VerificationError("Invalid pinned JSON " + revision + ":" + relative + ": " + str(error)) from error
    require(type(value) is dict, "Pinned source pins must be an object")
    return value


def _tool_bindings(project: Path) -> list[dict[str, str]]:
    result = []
    for relative in VERIFIER_PATHS:
        path = (project / relative).resolve(strict=True)
        require(path.is_relative_to(project) and path.is_file() and not path.is_symlink(),
                "Bridge verifier file is missing or unsafe: " + relative)
        result.append({"path": relative, "sha256": digest(path)})
    return result


def _tree_delta(project: Path, old_revision: str, current_revision: str) -> list[dict[str, Any]]:
    old_tree = shadow_tools.tree(project, old_revision)
    current_tree = shadow_tools.tree(project, current_revision)
    changed = sorted(
        path for path in set(old_tree) | set(current_tree)
        if old_tree.get(path) != current_tree.get(path) and not metadata_only(path)
    )
    require(set(changed) == set(ALLOWED_NON_METADATA_PATHS),
            "Graph reuse non-metadata delta differs from the reviewed exact allowlist: " +
            json.dumps({"missing": sorted(ALLOWED_NON_METADATA_PATHS - set(changed)),
                        "extra": sorted(set(changed) - ALLOWED_NON_METADATA_PATHS)}))
    require(all(path.startswith(".github/") or path.startswith("Tools/AssemblyShadow/") for path in changed),
            "Graph reuse delta escaped CI/AssemblyShadow tooling scope")
    return [
        {"path": path, "oldBlob": old_tree.get(path), "newBlob": current_tree.get(path),
         "status": "Added" if path not in old_tree else "Deleted" if path not in current_tree else "Modified"}
        for path in changed
    ]


def authenticate_transition(project: Path, graph_pins: dict[str, Any],
                            current_pins: dict[str, Any]) -> dict[str, Any]:
    project = project.resolve(strict=True)
    graph_entries = _entries(graph_pins)
    current_entries = _entries(current_pins)
    graph_demo = graph_entries["demo"]
    current_demo = current_entries["demo"]
    require(graph_demo.get("revision") == GRAPH_SOURCE_REVISION,
            "Graph reuse supports only the retained 69130bbb profile-2 graph")
    require(type(current_demo.get("revision")) is str and len(current_demo["revision"]) == 40 and
            current_demo["revision"] != GRAPH_SOURCE_REVISION,
            "Current demo source revision is invalid or has not advanced")
    for key in ("unityVersion", "target", "architecture"):
        require(graph_pins.get(key) == current_pins.get(key),
                "Graph/current platform source pin differs: " + key)
    for name in ("hybridclr", "hybridclrUnity", "il2cppPlus"):
        require(graph_entries[name] == current_entries[name],
                "Graph/current runtime repository pin differs: " + name)
    for key in ("url", "localPath"):
        require(graph_demo.get(key) == current_demo.get(key),
                "Graph/current demo repository identity differs: " + key)

    current_revision = current_demo["revision"].lower()
    require(shadow_tools.git(project, "rev-parse", "HEAD").decode().strip() != "",
            "Demo repository HEAD is unavailable")
    shadow_tools.git(project, "merge-base", "--is-ancestor", GRAPH_SOURCE_REVISION, current_revision)
    rows = _tree_delta(project, GRAPH_SOURCE_REVISION, current_revision)
    return {
        "policyId": POLICY_ID,
        "graphDemoRevision": GRAPH_SOURCE_REVISION,
        "currentDemoRevision": current_revision,
        "graphSourcePinsSha256": json_digest(graph_pins),
        "currentSourcePinsSha256": json_digest(current_pins),
        "nonMetadataDelta": rows,
        "nonMetadataDeltaSha256": json_digest(rows),
    }


def _build_map_side_project(build_map: dict[str, Any], side: str) -> Path:
    require(build_map.get("schemaVersion") == 1 and build_map.get("kind") == "H1ControlledBuildMap" and
            build_map.get("status") == "Frozen", "Bridge requires a frozen H1ControlledBuildMap")
    sides = build_map.get("sides")
    require(type(sides) is dict and type(sides.get(side)) is dict, "Bridge build-map side is missing: " + side)
    return canonical_dir(sides[side].get("projectRoot", ""), "bridge build-map project")


def create_receipt(project: Path, build_map_path: Path, side: str = "B") -> dict[str, Any]:
    project = project.resolve(strict=True)
    require(side == "B", "This H1 bridge is intentionally limited to retained candidate side B")
    build_map_path = canonical_file(build_map_path, "build map")
    build_map = read_json(build_map_path)
    require(_build_map_side_project(build_map, side) == project,
            "Bridge build-map side does not identify the candidate project")

    # Authenticate the current world through the unchanged global verifier.
    installed = shadow_tools.verify(project, expected_shadow="on")
    current_pins_path = canonical_file(project / PINS, "current source pins")
    current_pins = read_json(current_pins_path)
    graph_pins = retained_graph_pins(current_pins)
    transition = authenticate_transition(project, graph_pins, current_pins)

    return {
        "schemaVersion": 1,
        "kind": RECEIPT_KIND,
        "status": "AuthenticatedToolOnlySuccessor",
        "side": side,
        "projectRoot": str(project),
        "buildMap": binding(build_map_path),
        "graphSourcePins": graph_pins,
        "graphSourcePinsSha256": json_digest(graph_pins),
        "currentSourcePins": binding(current_pins_path),
        "currentSourcePinsObjectSha256": json_digest(current_pins),
        "transition": transition,
        "verifierBindings": _tool_bindings(project),
        "installedRuntimeVerification": installed,
        "scope": (
            "Permits strict verification of the retained 69130bbb candidate performance graph under its "
            "original complete source-pin DTO only after authenticating the reviewed tool-only successor. "
            "Does not alter normal R00 current-pairing verification, Player bytes, protocol, schedule, map, "
            "measurements, or protected profile-1 side A."
        ),
    }


def _verify_common(receipt_path: Path, project: Path, build_map_path: Path,
                   full: bool) -> dict[str, Any]:
    receipt_path = canonical_file(receipt_path, "graph reuse bridge")
    project = project.resolve(strict=True)
    build_map_path = canonical_file(build_map_path, "build map")
    value = read_json(receipt_path)
    require(value.get("schemaVersion") == 1 and value.get("kind") == RECEIPT_KIND and
            value.get("status") == "AuthenticatedToolOnlySuccessor" and value.get("side") == "B",
            "Invalid graph reuse bridge receipt")
    require(value.get("projectRoot") == str(project), "Graph reuse bridge project mismatch")
    require(value.get("buildMap") == binding(build_map_path), "Graph reuse bridge build-map binding mismatch")
    require(value.get("verifierBindings") == _tool_bindings(project),
            "Graph reuse bridge verifier implementation changed")

    current_pins_path = canonical_file(project / PINS, "current source pins")
    current_pins = read_json(current_pins_path)
    require(value.get("currentSourcePins") == binding(current_pins_path) and
            value.get("currentSourcePinsObjectSha256") == json_digest(current_pins),
            "Graph reuse bridge current source pins changed")
    graph_pins = value.get("graphSourcePins")
    require(type(graph_pins) is dict and value.get("graphSourcePinsSha256") == json_digest(graph_pins),
            "Graph reuse bridge graph source pins changed")
    transition = value.get("transition")
    require(type(transition) is dict and transition.get("policyId") == POLICY_ID and
            transition.get("graphDemoRevision") == GRAPH_SOURCE_REVISION,
            "Graph reuse transition header mismatch")
    current_revision = _entries(current_pins)["demo"].get("revision")
    require(transition.get("currentDemoRevision") == current_revision,
            "Graph reuse bridge current revision differs from source pins")

    build_map = read_json(build_map_path)
    require(_build_map_side_project(build_map, "B") == project,
            "Graph reuse bridge build-map project changed")

    if full:
        installed = shadow_tools.verify(project, expected_shadow="on")
        require(value.get("installedRuntimeVerification") == installed,
                "Graph reuse installed-runtime verification changed after bridge creation")
        actual = authenticate_transition(project, graph_pins, current_pins)
        require(transition == actual, "Graph reuse transition proof no longer matches current Git/source state")

    return {
        "kind": AUTHORITY_KIND,
        "projectRoot": str(project),
        "graphSourcePins": graph_pins,
        "currentSourcePins": current_pins,
        "bridgeReceipt": binding(receipt_path),
        "policyId": POLICY_ID,
    }


def verify_bridge_full(receipt_path: Path, project: Path, build_map_path: Path) -> dict[str, Any]:
    return _verify_common(receipt_path, project, build_map_path, True)


def verify_bridge_compact(receipt_path: Path, project: Path, build_map_path: Path) -> dict[str, Any]:
    return _verify_common(receipt_path, project, build_map_path, False)


def authority_for_project(authority: dict[str, Any] | None, project: Path) -> dict[str, Any] | None:
    if authority is None:
        return None
    require(authority.get("kind") == AUTHORITY_KIND, "Invalid graph reuse authority")
    return authority if authority.get("projectRoot") == str(project.resolve(strict=True)) else None
