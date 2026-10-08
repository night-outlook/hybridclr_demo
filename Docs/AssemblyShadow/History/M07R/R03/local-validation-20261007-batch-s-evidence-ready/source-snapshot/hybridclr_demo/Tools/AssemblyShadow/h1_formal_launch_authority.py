"""Fail-closed authority receipt for retained candidate formal R00 subprocess launches.

The public R00 runner remains current-pairing-only unless it receives this exact
H1 formal side-B authority receipt.  The receipt does not name an arbitrary
historical revision: it binds the already authenticated H1GraphReuseBridge,
pilot seal, frozen build map, formal schedule row, exact candidate graph inputs,
and current verifier/runner implementations.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import h1_graph_reuse as graph_reuse
from shadow_tools import VerificationError, read_json, require

KIND = "H1FormalSideLaunchAuthority"
STATUS = "AuthenticatedRetainedCandidateFormalLaunch"
SIDE = "B"

TOOL_PATHS = (
    "Tools/AssemblyShadow/h1_formal_launch_authority.py",
    "Tools/AssemblyShadow/h1_graph_reuse.py",
    "Tools/AssemblyShadow/run-h1-paired-performance.py",
    "Tools/AssemblyShadow/run-r00-players.py",
    "Tools/AssemblyShadow/r00_player_inputs.py",
    "Tools/AssemblyShadow/r00_results.py",
    "Tools/AssemblyShadow/r01_early_results.py",
)


def digest(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "Expected regular file: " + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def binding(path: Path) -> dict[str, str]:
    path = canonical_file(path, "bound file")
    return {"path": str(path), "sha256": digest(path)}


def _bound(value: Any, label: str) -> Path:
    require(type(value) is dict and set(value) == {"path", "sha256"}, label + " binding must contain path/sha256")
    path = canonical_file(value.get("path", ""), label)
    require(value.get("sha256") == digest(path), label + " binding hash mismatch")
    return path


def _output_root(value: str | Path, project: Path, *, require_new: bool) -> Path:
    raw = Path(value)
    parent = (project / "_temp/AssemblyShadow").resolve(strict=True)
    require(raw.is_absolute() and not raw.is_symlink() and raw.parent == parent,
            "Formal launch output root must be a direct child of candidate _temp/AssemblyShadow")
    resolved = raw.resolve(strict=False)
    require(resolved == raw, "Formal launch output root must be canonical")
    if require_new:
        require(not raw.exists() and not raw.is_symlink(),
                "Formal launch output root must be new when authority is created")
    elif raw.exists():
        require(raw.is_dir() and not raw.is_symlink(),
                "Formal launch output root must remain a non-symlink directory")
    return raw


def _tool_bindings(project: Path) -> list[dict[str, str]]:
    rows = []
    for relative in TOOL_PATHS:
        path = (project / relative).resolve(strict=True)
        require(path.is_relative_to(project) and path.is_file() and not path.is_symlink(),
                "Formal launch authority tool is missing or unsafe: " + relative)
        rows.append({"path": relative, "sha256": digest(path)})
    return rows


def _map_side_b(build_map_path: Path, project: Path,
                fixture: Path, on: Path, off: Path, replay: Path) -> None:
    value = read_json(build_map_path)
    require(value.get("schemaVersion") == 1 and value.get("kind") == "H1ControlledBuildMap" and
            value.get("status") == "Frozen", "Formal launch authority requires a frozen H1ControlledBuildMap")
    sides = value.get("sides")
    require(type(sides) is dict and type(sides.get(SIDE)) is dict,
            "Formal launch authority build map lacks side B")
    item = sides[SIDE]
    require(canonical_dir(item.get("projectRoot", ""), "formal side-B project") == project,
            "Formal launch authority project differs from frozen side B")
    require(_bound(item.get("fixtureManifest"), "formal side-B fixture") == fixture,
            "Formal launch authority fixture differs from frozen side B")
    require(_bound(item.get("replayReceipt"), "formal side-B replay") == replay,
            "Formal launch authority replay differs from frozen side B")
    builds = item.get("builds")
    require(type(builds) is dict and type(builds.get("on")) is dict and type(builds.get("off")) is dict,
            "Formal launch authority build map side B lacks ON/OFF builds")
    require(_bound(builds["on"].get("receipt"), "formal side-B ON receipt") == on,
            "Formal launch authority ON receipt differs from frozen side B")
    require(_bound(builds["off"].get("receipt"), "formal side-B OFF receipt") == off,
            "Formal launch authority OFF receipt differs from frozen side B")


def _schedule_row(schedule_path: Path, pair_id: str, mode: str, order: list[str]) -> None:
    value = read_json(schedule_path)
    require(value.get("schemaVersion") == 1 and value.get("kind") == "H1ControlledPairSchedule",
            "Formal launch authority schedule schema mismatch")
    pairs = value.get("pairs")
    require(type(pairs) is list, "Formal launch authority schedule pairs are missing")
    rows = [row for row in pairs if type(row) is dict and row.get("pairId") == pair_id]
    require(len(rows) == 1, "Formal launch authority pairId is not unique in the schedule")
    row = rows[0]
    require(row.get("phase") == "formal" and row.get("mode") == mode and row.get("order") == order and
            row.get("includedInFormalStatistics") is True,
            "Formal launch authority pair identity differs from preregistered schedule")


def _verify_seal(seal_path: Path, protocol_path: Path, schedule_path: Path,
                 build_map_path: Path, bridge_path: Path) -> None:
    value = read_json(seal_path)
    require(value.get("schemaVersion") == 1 and value.get("kind") == "H1PilotVerificationReceipt" and
            value.get("status") == "PassedStrictReconstructionAndStatGuardSealed",
            "Formal launch authority requires a passed pilot verification seal")
    for key, path in (("protocol", protocol_path), ("schedule", schedule_path), ("buildMap", build_map_path),
                      ("graphReuseBridge", bridge_path)):
        require(value.get(key) == binding(path), "Formal launch authority seal binding mismatch: " + key)


def create_receipt(project: Path, pair_id: str, attempt: int, mode: str, order: list[str],
                   protocol_path: Path, schedule_path: Path, build_map_path: Path,
                   bridge_path: Path, seal_path: Path, fixture: Path,
                   on: Path, off: Path, replay: Path, output_root: Path) -> dict[str, Any]:
    project = canonical_dir(project, "formal candidate project")
    require(type(pair_id) is str and pair_id, "Formal launch pairId is required")
    require(type(attempt) is int and not isinstance(attempt, bool) and attempt > 0,
            "Formal launch attempt must be positive")
    require(type(mode) is str and mode, "Formal launch mode is required")
    require(order in (["A", "B"], ["B", "A"]), "Formal launch order must be AB or BA")

    protocol_path = canonical_file(protocol_path, "formal protocol")
    schedule_path = canonical_file(schedule_path, "formal schedule")
    build_map_path = canonical_file(build_map_path, "formal build map")
    bridge_path = canonical_file(bridge_path, "formal graph bridge")
    seal_path = canonical_file(seal_path, "formal pilot seal")
    fixture = canonical_file(fixture, "formal fixture")
    on = canonical_file(on, "formal ON receipt")
    off = canonical_file(off, "formal OFF receipt")
    replay = canonical_file(replay, "formal replay")
    output_root = _output_root(output_root, project, require_new=True)

    _schedule_row(schedule_path, pair_id, mode, order)
    _map_side_b(build_map_path, project, fixture, on, off, replay)
    _verify_seal(seal_path, protocol_path, schedule_path, build_map_path, bridge_path)
    pairing = graph_reuse.verify_bridge_compact(bridge_path, project, build_map_path)

    return {
        "schemaVersion": 1,
        "kind": KIND,
        "status": STATUS,
        "side": SIDE,
        "pairId": pair_id,
        "attempt": attempt,
        "mode": mode,
        "pairOrder": order,
        "projectRoot": str(project),
        "runnerOutputRoot": str(output_root),
        "protocol": binding(protocol_path),
        "schedule": binding(schedule_path),
        "buildMap": binding(build_map_path),
        "graphReuseBridge": binding(bridge_path),
        "pilotVerification": binding(seal_path),
        "fixtureManifest": binding(fixture),
        "nativeOnReceipt": binding(on),
        "nativeOffReceipt": binding(off),
        "editorReplayReceipt": binding(replay),
        "toolBindings": _tool_bindings(project),
        "pairingPolicyId": pairing.get("policyId"),
        "graphSourcePins": pairing.get("graphSourcePins"),
        "currentSourcePins": pairing.get("currentSourcePins"),
        "scope": (
            "Retained H1 candidate formal side-B subprocess only. This receipt does not authorize "
            "protected side A, pilot execution, arbitrary historical pins, or non-formal R00 CLI use."
        ),
    }


def verify_receipt(receipt_path: Path, project: Path, mode: str,
                   fixture: Path, on: Path, off: Path, replay: Path, output_root: Path,
                   *, expected_pair_id: str | None = None,
                   expected_attempt: int | None = None) -> dict[str, Any]:
    receipt_path = canonical_file(receipt_path, "formal launch authority")
    project = canonical_dir(project, "formal candidate project")
    fixture = canonical_file(fixture, "formal fixture")
    on = canonical_file(on, "formal ON receipt")
    off = canonical_file(off, "formal OFF receipt")
    replay = canonical_file(replay, "formal replay")

    value = read_json(receipt_path)
    require(value.get("schemaVersion") == 1 and value.get("kind") == KIND and
            value.get("status") == STATUS and value.get("side") == SIDE,
            "Invalid H1 formal side launch authority")
    require(value.get("projectRoot") == str(project), "Formal launch authority project mismatch")
    output_root = _output_root(output_root, project, require_new=False)
    require(value.get("runnerOutputRoot") == str(output_root),
            "Formal launch authority output root mismatch")
    require(value.get("mode") == mode, "Formal launch authority mode mismatch")
    require(type(value.get("pairId")) is str and value["pairId"], "Formal launch authority pairId is missing")
    require(type(value.get("attempt")) is int and not isinstance(value["attempt"], bool) and value["attempt"] > 0,
            "Formal launch authority attempt is invalid")
    require(value.get("pairOrder") in (["A", "B"], ["B", "A"]), "Formal launch authority order is invalid")
    if expected_pair_id is not None:
        require(value.get("pairId") == expected_pair_id, "Formal launch authority pairId mismatch")
    if expected_attempt is not None:
        require(value.get("attempt") == expected_attempt, "Formal launch authority attempt mismatch")

    protocol_path = _bound(value.get("protocol"), "formal authority protocol")
    schedule_path = _bound(value.get("schedule"), "formal authority schedule")
    build_map_path = _bound(value.get("buildMap"), "formal authority build map")
    bridge_path = _bound(value.get("graphReuseBridge"), "formal authority graph bridge")
    seal_path = _bound(value.get("pilotVerification"), "formal authority pilot seal")
    require(_bound(value.get("fixtureManifest"), "formal authority fixture") == fixture,
            "Formal launch authority fixture mismatch")
    require(_bound(value.get("nativeOnReceipt"), "formal authority ON receipt") == on,
            "Formal launch authority ON receipt mismatch")
    require(_bound(value.get("nativeOffReceipt"), "formal authority OFF receipt") == off,
            "Formal launch authority OFF receipt mismatch")
    require(_bound(value.get("editorReplayReceipt"), "formal authority replay") == replay,
            "Formal launch authority replay mismatch")

    _schedule_row(schedule_path, value["pairId"], mode, value["pairOrder"])
    _map_side_b(build_map_path, project, fixture, on, off, replay)
    _verify_seal(seal_path, protocol_path, schedule_path, build_map_path, bridge_path)
    require(value.get("toolBindings") == _tool_bindings(project),
            "Formal launch authority verifier/runner implementation changed")

    pairing = graph_reuse.verify_bridge_compact(bridge_path, project, build_map_path)
    require(value.get("pairingPolicyId") == pairing.get("policyId") and
            value.get("graphSourcePins") == pairing.get("graphSourcePins") and
            value.get("currentSourcePins") == pairing.get("currentSourcePins"),
            "Formal launch authority pairing proof no longer matches bridge authority")

    return {
        "receipt": binding(receipt_path),
        "pairId": value["pairId"],
        "attempt": value["attempt"],
        "mode": mode,
        "pairOrder": value["pairOrder"],
        "runnerOutputRoot": str(output_root),
        "buildMap": binding(build_map_path),
        "graphReuseBridge": binding(bridge_path),
        "pilotVerification": binding(seal_path),
        "pairingAuthority": pairing,
    }
