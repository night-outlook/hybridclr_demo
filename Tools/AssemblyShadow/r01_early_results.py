"""Strict evidence gate for the bounded R01 earliest-startup experiment.

The early receipt is produced before the normal M07 bootstrap runner.  This
module deliberately treats the launcher as provenance only: all capsule bytes,
managed byte inputs, operation order, native snapshots, and the follow-on M07
receipt are recomputed from the current source-pinned input graph.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

import m07_results as m07
import m04_results as m04
from m04_metadata import read_identity
import r01_early_capsule as capsule
from r00_player_inputs import verify_inputs
import r01_failure_results as failures
import r01_results
from shadow_tools import require, unique_object


MODES = tuple(capsule.MODES)
DEFAULT_MODES = MODES[:-1]
POSITIVE_MODES = frozenset(("Control", "OrdinaryFirst", "OrdinaryAfterReserve"))
REJECTION_MODES = frozenset(set(MODES) - set(POSITIVE_MODES) - {"Baseline"})
FAILURE_MODES = frozenset(("MetadataFailure", "InitializerFailure"))
DIAGNOSTIC_MODES = frozenset(MODES)
DEFAULT_M07_MODE = "T07-03-FullClosure-P03"
M07_MODE = DEFAULT_M07_MODE
EARLY_KIND = "R01EarlyStartupReceipt"
LAUNCH_KIND = "R01EarlyLaunches"
CAPSULE_KIND = "R01EarlyStartupCapsuleReceipt"
ORDINARY = "AssemblyShadowBaseline.HotUpdate"
INTERNAL = "AssemblyA.Implementation.Internal"
GUARD_MODES = frozenset(("Type", "Object", "Cctor", "NativeScript"))

ERROR_CODES = {
    "Success": 0,
    "InvalidState": 2,
    "ReferenceResolutionFailed": 13,
    "BaselineAlreadyUsed": 15,
    "AlreadyCommitted": 18,
    "ModuleInitializerFailed": 19,
}

RECEIPT_FIELDS = (
    "schemaVersion kind mode processId managedThreadId stopwatchFrequency elapsedTicks "
    "capsulePath capsuleSha256 resultPath baselineBuildId runtimeAbiHash patchId result error "
    "callbackReturnCode inputReadCount operations snapshots byteInputs observerJoined observerErrors "
    "observerSamples observerDroppedBefore observerDroppedAfter initializerEvents"
)
OPERATION_FIELDS = "phase code intCode startedTicks elapsedTicks"
SNAPSHOT_FIELDS = (
    "phase diagnosticsCode diagnosticsJson recoveryCode recoveryJson capacityCode capacityJson orderedSizes"
)
BYTE_FIELDS = "name path length sha256 kind"
LAUNCH_FIELDS = (
    "schemaVersion kind projectRoot fixtureManifestPath onBuildReceiptPath offBuildReceiptPath "
    "replayReceiptPath failureFixturesPath negativeInputPath sourcePins requestedModes fullModeInventory m07Mode "
    "completedModes processLaunches resultDirectory inputHashesBefore inputHashesAfter inputsUnchanged "
    "diagnosticOnly note"
)
PROCESS_FIELDS = (
    "mode command processId startedAtUnix durationSeconds exitCode timedOut passed "
    "capsulePath capsuleSha256 earlyResultPath earlyResultSha256 m07ResultPath m07ResultSha256 "
    "logPath logSha256 consolePath consoleSha256 inputHashesBefore inputHashesAfter inputsUnchanged error"
)


def read(path: Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)
    require(type(value) is dict, "Expected JSON object: " + str(path))
    return value


def exact(actual: Any, expected: Any, label: str) -> None:
    def same(left: Any, right: Any) -> bool:
        if type(left) is not type(right):
            return False
        if type(left) is dict:
            return left.keys() == right.keys() and all(same(left[key], right[key]) for key in left)
        if type(left) in (list, tuple):
            return len(left) == len(right) and all(same(a, b) for a, b in zip(left, right))
        return left == right
    if not same(actual, expected):
        require(False, f"{label}: expected {repr(expected)[:240]}, got {repr(actual)[:240]}")


def fields(value: dict[str, Any], expected: str, label: str) -> dict[str, Any]:
    require(type(value) is dict, label + ": expected object")
    for key in expected.split():
        require(key in value, label + ": missing field " + key)
    return value


def integer(value: Any, label: str, minimum: int = 0) -> int:
    require(type(value) is int and not isinstance(value, bool) and value >= minimum,
            label + ": expected integer")
    return value


def sha256(value: Any, label: str) -> str:
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
            label + ": invalid SHA-256")
    return value


def digest(path: Path) -> str:
    path = Path(path)
    require(path.is_absolute() and path == path.resolve(strict=True) and path.is_file() and not path.is_symlink(),
            "Expected canonical regular file: " + str(path))
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _padded_hash(path: Path, length: int) -> str:
    """Hash a source followed by zero bytes without materializing the pad."""
    path = Path(path)
    source_length = path.stat().st_size
    require(length >= source_length, "Derived padded input is shorter than its source")
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    zero = bytes(1024 * 1024)
    remaining = length - source_length
    while remaining:
        count = min(remaining, len(zero))
        value.update(zero[:count])
        remaining -= count
    return value.hexdigest()


def canonical(value: Any, base: Path, label: str, directory: bool = False) -> Path:
    path = Path(value)
    require(path.is_absolute(), label + ": path must be absolute")
    require(not path.is_symlink() and path == path.resolve(strict=True), label + ": noncanonical path")
    if directory:
        require(path.is_dir() and not path.is_symlink(), label + ": expected directory")
    else:
        require(path.is_file() and not path.is_symlink(), label + ": expected regular file")
    return path


def bound(value: Any, expected_hash: Any, base: Path, label: str, directory: bool = False) -> Path:
    path = canonical(value, base, label, directory)
    exact(digest(path) if not directory else None, expected_hash if not directory else None, label + ".sha256")
    return path


def _new_child(value: Path, parent: Path, label: str) -> Path:
    require(value.is_absolute() and value == value.resolve() and not value.exists() and not value.is_symlink(),
            label + " must be a new canonical absolute path")
    parent = parent.resolve(strict=True)
    require(not parent.is_symlink() and value.parent == parent, label + " must be a direct child of " + str(parent))
    return value


def _json(value: Any, label: str) -> dict[str, Any]:
    require(type(value) is str and value, label + ": missing JSON")
    parsed = json.loads(value, object_pairs_hook=unique_object)
    require(type(parsed) is dict, label + ": expected JSON object")
    return parsed


def _expected_operations(mode: str, closure: list[str]) -> list[tuple[str, str, int]]:
    stage = [("stage:" + name, "Success", 0) for name in closure]
    if mode == "Baseline":
        return []
    if mode == "OrdinaryFirst":
        return [("ordinary-before-configure", "Success", 0), ("configure", "Success", 0),
                ("begin", "Success", 0), ("reserve", "Success", 0)] + stage + [
                    ("validate", "Success", 0), ("commit", "Success", 0)]
    if mode == "OrdinaryAfterReserve":
        return [("configure", "Success", 0), ("begin", "Success", 0), ("reserve", "Success", 0),
                ("ordinary-after-reserve", "Success", 0)] + stage + [
                    ("validate", "Success", 0), ("commit", "Success", 0)]
    if mode in ("Type", "Object", "Cctor"):
        return [("preconfigure-" + mode.lower(), "Success", 0), ("configure", "Success", 0),
                ("begin", "Success", 0), ("reserve", "Success", 0)] + stage + [
                    ("validate", "BaselineAlreadyUsed", 15), ("abort", "Success", 0)]
    if mode == "NativeScript":
        return [("preconfigure-nativescript", "Success", 0), ("configure", "Success", 0),
                ("begin", "Success", 0), ("reserve", "Success", 0)] + stage + [
                    ("validate", "BaselineAlreadyUsed", 15), ("abort", "Success", 0)]
    if mode == "Oversize":
        return [("configure", "Success", 0), ("begin", "Success", 0),
                ("reserve", "MetadataCapacityExceeded", 23), ("abort", "Success", 0)]
    if mode == "Mismatch":
        return [("configure", "Success", 0), ("begin", "Success", 0), ("reserve", "Success", 0),
                ("stage:" + closure[0], "MetadataBudgetMismatch", 24), ("abort", "Success", 0)]
    if mode == "MetadataFailure":
        return [("configure", "Success", 0), ("begin", "Success", 0), ("reserve", "Success", 0)] + stage + [
            ("validate", "ReferenceResolutionFailed", 13), ("abort", "InvalidState", 2),
            ("begin-after-failure", "InvalidState", 2)]
    if mode == "InitializerFailure":
        return [("configure", "Success", 0), ("begin", "Success", 0), ("reserve", "Success", 0)] + stage + [
            ("validate", "Success", 0), ("commit", "ModuleInitializerFailed", 19),
            ("abort", "AlreadyCommitted", 18), ("begin-after-commit", "AlreadyCommitted", 18)]
    if mode == "Control":
        return [("configure", "Success", 0), ("begin", "Success", 0), ("reserve", "Success", 0)] + stage + [
            ("validate", "Success", 0), ("commit", "Success", 0)]
    raise ValueError("Unknown early mode: " + mode)


def _expected_snapshots(mode: str, closure: list[str]) -> list[str]:
    if mode == "Baseline":
        return ["before-startup-ops"]
    phases = ["before-startup-ops"]
    if mode == "OrdinaryFirst":
        phases += ["after-ordinary-before-configure"]
    if mode in ("Type", "Object", "Cctor"):
        phases += ["after-preconfigure-witness"]
    if mode == "NativeScript":
        phases += ["after-preconfigure-witness"]
    if mode == "Oversize":
        return phases + ["after-configure", "after-begin", "after-failed-reserve", "after-abort"]
    if mode == "Mismatch":
        return phases + ["after-configure", "after-begin", "after-reserve", "after-mismatch", "after-abort"]
    phases += ["after-configure", "after-begin", "after-reserve"]
    if mode == "OrdinaryAfterReserve":
        phases += ["after-ordinary-after-reserve"]
    phases += ["after-stage", "after-validate"]
    if mode in POSITIVE_MODES or mode == "InitializerFailure":
        phases += ["after-commit"]
    if mode in FAILURE_MODES:
        phases += ["after-rejected-operations"]
    elif mode in GUARD_MODES:
        phases += ["after-abort"]
    return phases


def _expected_bytes(capsule_data: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in capsule_data["inputs"]:
        rows.append({"name": item["name"], "path": item["dllPath"], "length": item["dllLength"],
                     "sha256": item["dllSha256"], "kind": "dll"})
        if item["pdbPath"]:
            rows.append({"name": item["name"], "path": item["pdbPath"], "length": item["pdbLength"],
                         "sha256": item["pdbSha256"], "kind": "pdb"})
    if capsule_data["ordinaryPath"]:
        rows.append({"name": ORDINARY, "path": capsule_data["ordinaryPath"], "length": None,
                     "sha256": capsule_data["ordinarySha256"], "kind": "ordinary"})
    rows += [{"name": "", "path": item["path"], "length": item["length"],
              "sha256": item["sha256"], "kind": "prerequisite"}
             for item in capsule_data["prerequisiteFiles"]]
    if capsule_data["mode"] == "Mismatch":
        first = capsule_data["inputs"][0]
        source = Path(first["dllPath"]).read_bytes()
        rows.append({"name": first["name"], "path": first["dllPath"], "length": len(source) + 1,
                     "sha256": hashlib.sha256(source + b"\0").hexdigest(), "kind": "mismatch-dll"})
    if capsule_data["mode"] == "Oversize":
        last = capsule_data["inputs"][-1]
        rows.append({"name": last["name"], "path": last["dllPath"], "length": 64 * 1024 * 1024,
                     "sha256": _padded_hash(Path(last["dllPath"]), 64 * 1024 * 1024),
                     "kind": "oversize-dll"})
    return rows


def _ordered_sizes(data: dict[str, Any], mode: str) -> list[int]:
    sizes = [item["dllLength"] for item in data["inputs"]]
    if mode == "Oversize":
        require(sizes, "Oversize capsule has no closure members")
        sizes[-1] = 64 * 1024 * 1024
    return sizes


def verify_byte_inputs(receipt: dict[str, Any], data: dict[str, Any], label: str) -> None:
    rows = receipt["byteInputs"]
    expected = _expected_bytes(data)
    exact(len(rows), len(expected), label + ".byteInputCount")
    for index, (actual, wanted) in enumerate(zip(rows, expected)):
        current = fields(actual, BYTE_FIELDS, f"{label}.byteInputs[{index}]")
        for key in ("name", "path", "sha256", "kind"):
            exact(current[key], wanted[key], f"{label}.byteInputs[{index}].{key}")
        path = canonical(current["path"], Path(receipt["resultPath"]), f"{label}.byteInputs[{index}].path")
        actual_size = path.stat().st_size
        expected_size = actual_size if wanted["length"] is None else wanted["length"]
        exact(current["length"], expected_size, f"{label}.byteInputs[{index}].length")
        if wanted["kind"] not in ("mismatch-dll", "oversize-dll"):
            exact(actual_size, expected_size, f"{label}.byteInputs[{index}].fileLength")
        exact(current["sha256"], wanted["sha256"], f"{label}.byteInputs[{index}].capsuleHash")
        actual_hash = (_padded_hash(path, wanted["length"]) if wanted["kind"] == "oversize-dll" else
                       hashlib.sha256(path.read_bytes() + b"\0").hexdigest() if wanted["kind"] == "mismatch-dll" else
                       digest(path))
        exact(actual_hash, current["sha256"], f"{label}.byteInputs[{index}].fileHash")
    read_count = sum(item["kind"] not in ("mismatch-dll", "oversize-dll") for item in expected)
    exact(receipt["inputReadCount"], read_count, label + ".inputReadCount")


def _verify_capacity(raw: dict[str, Any], sizes: list[int], label: str) -> None:
    required = ("schemaVersion enabled profileVersion indexBits kindBits cursors remainingSlots requiredImages "
                "acceptedImages firstFailingIndex firstFailingSize failureReason fits allocations finalCursors "
                "ordinaryAllocatedCount shadowAllocatedCount reservedImageCount")
    fields(raw, required, label)
    exact(raw["schemaVersion"], 1, label + ".schemaVersion")
    exact(raw["enabled"], True, label + ".enabled")
    for key, expected in (("profileVersion", 1), ("indexBits", 22), ("kindBits", 2)):
        exact(raw[key], expected, label + "." + key)
    r01_results._u32_array(raw["cursors"], label + ".cursors")
    # Reuse the independent budget oracle from the legacy strict verifier.  It
    # does not depend on the early runner or on a self-reported fit value.
    model = r01_results.evaluate_budget(raw["cursors"], sizes)
    remaining = r01_results.remaining_slots(raw["cursors"])
    for key, expected in model.items():
        exact(raw[key], expected, label + "." + key)
    exact(raw["remainingSlots"], remaining, label + ".remainingSlots")
    for key in ("ordinaryAllocatedCount", "shadowAllocatedCount", "reservedImageCount"):
        integer(raw[key], label + "." + key)


def _verify_snapshot(snapshot: dict[str, Any], sizes: list[int], candidates: list[str], label: str,
                     profile: int = 1) -> dict[str, Any]:
    fields(snapshot, SNAPSHOT_FIELDS, label)
    exact(snapshot["orderedSizes"], sizes, label + ".orderedSizes")
    for key in ("diagnosticsCode", "recoveryCode", "capacityCode"):
        exact(snapshot[key], "Success", label + "." + key)
    diagnostics = _json(snapshot["diagnosticsJson"], label + ".diagnosticsJson")
    recovery = _json(snapshot["recoveryJson"], label + ".recoveryJson")
    capacity = _json(snapshot["capacityJson"], label + ".capacityJson")
    if profile == 1:
        _verify_capacity(capacity, sizes, label + ".capacityJson")
    else:
        failures.verify_profile2_capacity(capacity, sizes, label + ".capacityJson")
    fields(diagnostics, m04.R01_DIAGNOSTIC_FIELDS, label + ".diagnosticsJson")
    m04._diagnostic(diagnostics, label + ".diagnosticsJson", expected_abi=profile)
    for key, expected in dict(enabled=True, startupCandidateSchemaVersion=1,
                             startupObservationMode="EarlyTracking", startupCandidateNames=candidates,
                             metadataBudgetCapabilityVersion=profile, recoveryCapabilityVersion=1).items():
        exact(diagnostics[key], expected, label + "." + key)
    fields(recovery, "schemaVersion enabled capabilityVersion state stateCode published abortAllowed disposition dispositionCode terminalFailureCode reason retainedBytes baselineEligibilityRequiresStartupValidation", label + ".recoveryJson")
    for key in ("enabled", "published", "abortAllowed", "baselineEligibilityRequiresStartupValidation"):
        r01_results.boolean(recovery[key], label + ".recovery." + key)
    for key in ("schemaVersion", "capabilityVersion", "stateCode", "dispositionCode", "terminalFailureCode", "retainedBytes"):
        integer(recovery[key], label + ".recovery." + key)
    require(type(recovery["reason"]) is str, label + ".recovery.reason")
    return {"diagnostics": diagnostics, "recovery": recovery, "capacity": capacity,
            "profileComplete": True}


def physical_stable_names(data: dict[str, Any], diagnostics: dict[str, Any], label: str) -> list[str]:
    """Resolve policy spelling without changing capsule or raw diagnostic bytes.

    Configure uses the existing case-insensitive physical AOT lookup and stores
    the assembly's actual identity. Preserve policy order and require uniqueness
    on both sides so normalization cannot hide missing or ambiguous identities.
    """
    policy = data["stableAotNames"]
    exact(len({name.casefold() for name in policy}), len(policy), label + ".uniqueStablePolicy")
    physical = [row["name"] for row in diagnostics["ordinaryAssemblies"] if not row["isInterpreter"]]
    resolved = []
    for name in policy:
        matches = [actual for actual in physical if actual.casefold() == name.casefold()]
        exact(len(matches), 1, label + ".physicalStableAot." + name)
        resolved.append(matches[0])
    return resolved


TERMINAL_MARKER = "[AssemblyShadowStartup] Terminating process before host continuation (exit=1)"
FAILURE_PREFIX = "[AssemblyShadowStartup] Failed: "
EXPECTED_REFUSAL = FAILURE_PREFIX + "Bootstrap explicitly refused startup"
# These are observed post-il2cpp_init host boundaries or managed M07 entrypoints.
# A terminal marker appended to a continued Player log cannot repair that run.
HOST_CONTINUATION_MARKERS = (
    "Player connection [", "Input System module state changed to: Initialized",
    "[PhysX] Initialized", "Initialize engine version:", "[Subsystems] Discovering",
    "GfxDevice:", "NullGfxDevice:", "MonoScript::", "M07BootstrapRunner", "M07Probe",
    "M07BaselineProbe", "UnityEngine.SetupCoroutine", "UnloadTime:",
)


def verify_startup_logs(mode: str, log_path: Path, console_path: Path) -> None:
    """Check both process-owned streams; hash binding is checked by verify_suite.

    The native marker plus exact exit status is bounded evidence of the gateway
    path. Nonreturn itself is independently established by native death tests.
    Streams may duplicate stderr, but every refusal-bearing stream must end in
    the complete adjacent refusal/termination pair, with no host continuation.
    """
    terminal_streams = 0
    for path in (log_path, console_path):
        lines = Path(path).read_text(encoding="utf-8-sig", errors="strict").splitlines()
        if mode not in REJECTION_MODES:
            require(not any(FAILURE_PREFIX in line or TERMINAL_MARKER in line for line in lines),
                    mode + ": unexpected startup refusal in " + str(path))
            continue
        require(not any(marker in line for line in lines for marker in HOST_CONTINUATION_MARKERS),
                mode + ": downstream host/M07 continuation in " + str(path))
        nonempty = [line for line in lines if line.strip()]
        refusals = [i for i, line in enumerate(nonempty) if line.startswith(FAILURE_PREFIX)]
        terminals = [i for i, line in enumerate(nonempty) if line == TERMINAL_MARKER]
        if refusals or terminals:
            exact(len(refusals), 1, mode + ".nativeRefusalCount")
            exact(len(terminals), 1, mode + ".nativeTerminalCount")
            exact(refusals[0], len(nonempty) - 2, mode + ".nativeRefusalPosition")
            exact(terminals[0], len(nonempty) - 1, mode + ".nativeTerminalPosition")
            exact(nonempty[refusals[0]], EXPECTED_REFUSAL, mode + ".nativeRefusalReason")
            terminal_streams += 1
    require(mode not in REJECTION_MODES or terminal_streams > 0,
            mode + ": missing native terminal refusal evidence")


BASELINE_USE_KINDS = frozenset((
    "AssemblyReflection", "TypeReflection", "ClassInit", "ObjectAllocation", "StaticField",
    "VTable", "MonoScript", "ModuleReflection", "MethodExecution",
))


def verify_first_use_history(current: list[dict[str, Any]], previous: list[dict[str, Any]],
                             data: dict[str, Any], label: str, *, witness: bool = False) -> None:
    """Retain the whole generated registry history, scoped to the selected closure.

    ResolvePrivate intentionally uses physical AOT for unchanged candidates.
    Those records remain observable and do not make a different selected member
    ineligible. This is the established M07 rule, with the R01 first-use sequence
    and immutable record contract checked as well.
    """
    candidates = data["candidates"]
    closure = {row["name"] for row in data["inputs"]}
    names, sequences, chronological = [], [], []
    for use in current:
        fields(use, "name kind detail type thread timestamp", label)
        name = use["name"]
        require(name in candidates and (witness or name not in closure),
                label + ": selected closure or non-candidate baseline use observed")
        require(use["kind"] in BASELINE_USE_KINDS, label + ".invalidKind")
        integer(use["thread"], label + ".thread", 1)
        integer(use["timestamp"], label + ".timestamp", 1)
        match = re.fullmatch(r"(.+) FirstUseSequence=([1-9][0-9]*)", use["detail"])
        require(match is not None, label + ".invalidFirstUseSequence")
        sequence = int(match.group(2))
        names.append(name); sequences.append(sequence)
        chronological.append((sequence, use["timestamp"]))
    # Native emits registry order, which need not be first-use sequence order.
    exact(names, [name for name in candidates if name in names], label + ".registryOrder")
    exact(sorted(sequences), list(range(1, len(current) + 1)), label + ".completeSequence")
    timestamps = [timestamp for _, timestamp in sorted(chronological)]
    exact(timestamps, sorted(timestamps), label + ".sequenceTimeOrder")
    by_name = {use["name"]: use for use in current}
    for use in previous:
        exact(by_name.get(use["name"]), use, label + ".immutableFirstUse." + use["name"])


def _verify_timeline(parsed: list[dict[str, Any]], phases: list[str], data: dict[str, Any]) -> None:
    """Synchronous main-thread snapshots of AssemblyShadow.cpp's exact operations.

    Recovery is classified independently from mutable lastError. Refused Abort
    and Begin overwrite lastError, while terminal recovery and retained owners
    remain unchanged. Capacity arithmetic reuses the independent R01 oracle.
    """
    mode = data["mode"]
    closure = [row["name"] for row in data["inputs"]]
    sizes = _ordered_sizes(data, mode)
    identities = {row["name"]: read_identity(Path(row["dllPath"]))["mvid"] for row in data["inputs"]}
    for row in data["inputs"]:
        exact(read_identity(Path(row["dllPath"]))["name"], row["name"], "early.inputIdentity")
    retained = sum(row["dllLength"] + row["pdbLength"] for row in data["inputs"])
    state, configured, begun, staged, metadata, published = "Disabled", False, False, False, False, False
    error, terminal = 0, 0
    cursors = list(r01_results.FRESH_CURSORS)
    ordinary_count = shadow_count = reserved_count = 0
    events: list[dict[str, Any]] = []
    commit_order: list[str] = []
    attempts: list[str] = []
    initial_physical = None
    witness_uses = None
    previous_uses = []
    validation_started = False
    terminal_recovery = None

    def event(kind: str, name: str = "", count: int | None = None) -> None:
        events.append(dict(sequence=len(events) + 1, kind=kind, name=name, generation=int(published),
                           stagedCount=(len(closure) if staged else 0) if count is None else count))

    for phase, snapshot in zip(phases, parsed):
        label = "early." + phase
        d, r, c = (snapshot[key] for key in ("diagnostics", "recovery", "capacity"))
        if phase == "after-configure":
            configured, state = True, "CandidatesRegistered"
            event("candidates-registered")
        elif phase == "after-begin":
            begun, state = True, "Staging"
            event("transaction-begun")
        elif phase == "after-reserve":
            budget = r01_results.evaluate_budget(cursors, sizes)
            exact(budget["fits"], True, label + ".reservationFits")
            cursors = budget["finalCursors"]
            reserved_count += len(sizes)
            event("metadata-budget-reserved")
        elif phase in ("after-ordinary-before-configure", "after-ordinary-after-reserve"):
            budget = r01_results.evaluate_budget(cursors, [Path(data["ordinaryPath"]).stat().st_size])
            exact(budget["fits"], True, label + ".ordinaryFits")
            cursors = budget["finalCursors"]
            ordinary_count += 1
        elif phase == "after-failed-reserve":
            error = 23
        elif phase == "after-mismatch":
            error = 24
        elif phase == "after-stage":
            staged, state = True, "Staged"
            shadow_count += len(closure)
            for index, name in enumerate(closure):
                event("skeleton-created", name, index + 1)
        elif phase == "after-validate":
            if mode in GUARD_MODES:
                error = 15
            elif mode == "MetadataFailure":
                state, error, terminal = "Failed", 13, 13
                event("metadata-begin", closure[0])
            else:
                metadata, state = True, "Validated"
                for name in closure:
                    event("metadata-begin", name)
                    event("metadata-ready", name)
                event("transaction-validated")
        elif phase == "after-commit":
            published = True
            event("active-published")
            attempts = closure[:closure.index(failures.INITIALIZER_TARGET) + 1] if mode == "InitializerFailure" else closure
            for name in attempts:
                event("initializer-begin", name)
                if mode == "InitializerFailure" and name == failures.INITIALIZER_TARGET:
                    event("initializer-failed", name)
                else:
                    commit_order.append(name)
                    event("initializer-complete", name)
            if mode == "InitializerFailure":
                state, error, terminal = "FailedAfterCommit", 19, 19
            else:
                state = "Committed"
                event("transaction-committed")
        elif phase == "after-rejected-operations":
            error = 2 if mode == "MetadataFailure" else 18
        elif phase == "after-abort":
            state, error = "Aborted", 0
            event("transaction-aborted")

        # No other managed operation in this capsule allocates interpreter images.
        for key, wanted in dict(cursors=cursors, ordinaryAllocatedCount=ordinary_count,
                                shadowAllocatedCount=shadow_count, reservedImageCount=reserved_count).items():
            exact(c[key], wanted, label + ".capacity." + key)
        if mode == "Oversize":
            exact(c["fits"], False, label + ".oversize.fits")
            exact(c["firstFailingIndex"], len(sizes) - 1, label + ".oversize.firstFailingIndex")
        for key, wanted in dict(state=state, stateCode=m04.STATE_CODES[state], lastError=error,
                                baselineBuildId=data["baselineBuildId"] if configured else "",
                                patchId=data["patchId"] if begun else "",
                                closureLoadOrder=closure if begun else [],
                                stableAotNames=physical_stable_names(data, d, label) if configured else [],
                                expected=len(closure) if begun else 0, staged=len(closure) if staged else 0,
                                retainedBytes=retained if staged else 0,
                                generation=int(published), enumerationGeneration=int(published),
                                classEnumerationGeneration=int(published), commitOrder=commit_order,
                                events=events).items():
            exact(d[key], wanted, label + ".diagnostics." + key)
        exact([row["name"] for row in d["assemblies"]], closure if begun else [], label + ".assemblies")
        for row in d["assemblies"]:
            for key, wanted in dict(mvid=identities[row["name"]] if staged else "", skeletonBuilt=staged,
                                    runtimeMetadataInitialized=metadata, published=published,
                                    moduleInitializerAttempted=row["name"] in attempts,
                                    moduleInitializerRan=row["name"] in commit_order).items():
                exact(row[key], wanted, label + ".assembly." + row["name"] + "." + key)
        physical = [row for row in d["ordinaryAssemblies"] if not row["isInterpreter"]]
        if initial_physical is None:
            initial_physical = physical
        exact(physical, initial_physical, label + ".physicalAotRetention")
        for name in data["candidates"] + physical_stable_names(data, d, label):
            exact(sum(row["name"] == name for row in physical), 1, label + ".physicalAot." + name)
        actual_interpreters = sorted(row["name"] for row in d["ordinaryAssemblies"] if row["isInterpreter"])
        exact(actual_interpreters, sorted((closure if published else []) + ([ORDINARY] if ordinary_count else [])),
              label + ".ordinaryInterpreterIsolation")
        for row in d["ordinaryClasses"]:
            if row["usesStagedMetadata"]:
                require(published, label + ".privateClassLeak")
            if row["isInterpreter"]:
                require(row["assemblyName"] in actual_interpreters, label + ".unpublishedInterpreterClass")

        uses = d["baselineUses"]
        if phase == "after-preconfigure-witness":
            require(any(row["name"] == INTERNAL for row in uses), label + ".missingCandidateWitness")
            witness_uses = uses
            for row in uses:
                require(row["name"] in data["candidates"] and row["thread"] > 0 and row["timestamp"] > 0,
                        label + ".invalidFirstUse")
                require(re.search(r" FirstUseSequence=[1-9][0-9]*$", row["detail"]) is not None,
                        label + ".missingFirstUseSequence")
            if mode == "NativeScript":
                exact(len(uses), 1, label + ".nativeInputWitnessCount")
                exact(uses[0]["kind"], "AssemblyReflection", label + ".nativeInputKind")
                exact(uses[0]["detail"], "Image::ClassFromName.input FirstUseSequence=1", label + ".nativeInputDetail")
        verify_first_use_history(uses, previous_uses, data, label + ".firstUseHistory", witness=mode in GUARD_MODES)
        if mode in GUARD_MODES:
            exact(uses, witness_uses or [], label + ".firstUseHistory")
        else:
            validation_started = validation_started or phase == "after-validate"
            if not validation_started:
                exact(uses, [], label + ".preValidationFirstUse")
        previous_uses = uses
        if terminal:
            disposition, disposition_code, abort_allowed = "RestartRequired", 0, False
        elif state in ("Disabled", "CandidatesRegistered"):
            disposition, disposition_code, abort_allowed = "BaselineUnselected", 5, False
        elif state == "Aborted":
            disposition, disposition_code, abort_allowed = "BaselineEligibleAfterAbort", 3, False
        elif published:
            disposition, disposition_code, abort_allowed = "ActiveShadow", 4, False
        elif error == 15:
            disposition, disposition_code, abort_allowed = "AbortRequired", 2, True
        else:
            disposition, disposition_code, abort_allowed = "CorrectInputOrAbort", 1, True
        for key, wanted in dict(schemaVersion=1, enabled=True, capabilityVersion=1,
                                state=state, stateCode=m04.STATE_CODES[state], published=published,
                                abortAllowed=abort_allowed, disposition=disposition, dispositionCode=disposition_code,
                                terminalFailureCode=terminal, retainedBytes=retained if staged else 0,
                                baselineEligibilityRequiresStartupValidation=disposition != "ActiveShadow").items():
            exact(r[key], wanted, label + ".recovery." + key)
        if terminal:
            reason = "Image::ReadType invalid type" if mode == "MetadataFailure" else failures.INITIALIZER_REASON
            require(reason in r["reason"], label + ".terminalReason")
            if terminal_recovery is None:
                terminal_recovery = r
                exact(d["detail"], r["reason"], label + ".originalFailureReason")
            exact(r, terminal_recovery, label + ".durableRecovery")
        else:
            exact(r["reason"], d["detail"], label + ".recoveryReason")
        if error == 13:
            require(d["detail"].startswith("AssemblyA.Contracts:"), label + ".Q04Provider")
        elif error == 15:
            expected_used = next(name for name in closure if any(use["name"] == name for use in uses))
            exact(d["detail"], expected_used, label + ".baselineRejectionReason")
        elif error == 23:
            exact(d["detail"], "Metadata capacity rejected before Stage: " + closure[-1], label + ".capacityReason")
        elif error == 24:
            exact(d["detail"], "DLL size differs from the reserved closure input.", label + ".mismatchReason")
        elif phase == "after-rejected-operations":
            exact(d["detail"], "Operation is not allowed in the current transaction state.", label + ".refusedReason")
        elif state == "Aborted":
            exact(d["detail"], "Private metadata retained; a second transaction is forbidden.", label + ".abortReason")
        elif not terminal:
            exact(d["detail"], "", label + ".unexpectedNativeDetail")


OBSERVER_MODES = frozenset(("Control", "MetadataFailure", "InitializerFailure"))


def _verify_observers(receipt: dict[str, Any], data: dict[str, Any], parsed: list[dict[str, Any]],
                      profile: int = 1) -> None:
    mode = data["mode"]
    samples, initializers = receipt["observerSamples"], receipt["initializerEvents"]
    require(type(samples) is list and type(initializers) is list, "early.observer arrays")
    exact(receipt["observerErrors"], [], "early.observerErrors")
    for key in ("observerDroppedBefore", "observerDroppedAfter"):
        integer(receipt[key], "early." + key)
    if mode not in OBSERVER_MODES:
        for key, wanted in dict(observerJoined=False, observerSamples=[], initializerEvents=[],
                                observerDroppedBefore=0, observerDroppedAfter=0).items():
            exact(receipt[key], wanted, "early." + key)
        return
    exact(receipt["observerJoined"], True, "early.observerJoined")
    require(2 <= len(samples) <= 32 and {row["phase"] for row in samples} == {"before", "after"},
            "early.observerSamples requires bounded before/after evidence")
    phases = [row["phase"] for row in samples]
    exact(phases, sorted(phases, key=lambda phase: phase == "after"), "early.observerPhaseOrder")
    for phase in ("before", "after"):
        count = phases.count(phase)
        require(1 <= count <= 16, "early.observer retained phase limit")
        if receipt["observerDropped" + phase.title()]:
            exact(count, 16, "early.observer dropped before retention full")
    thread_ids = {integer(row["threadId"], "early.observerThread", 1) for row in samples}
    require(len(thread_ids) == 1 and receipt["managedThreadId"] not in thread_ids,
            "early.observer requires a separate single thread")
    closure = [row["name"] for row in data["inputs"]]
    final = parsed[-1]["diagnostics"]
    source_identities = {row["name"]: read_identity(Path(row["dllPath"]))["mvid"] for row in data["inputs"]}
    previous = (0, 0, 0)
    previous_ticks = 0
    saw_private_transaction = False

    def raw(sample: dict[str, Any], label: str) -> dict[str, Any]:
        fields(sample, "phase rawJson code threadId ticks", label)
        exact(sample["code"], 0, label + ".code")
        integer(sample["threadId"], label + ".threadId", 1)
        integer(sample["ticks"], label + ".ticks", 1)
        d = _json(sample["rawJson"], label + ".rawJson")
        fields(d, m04.R01_DIAGNOSTIC_FIELDS, label)
        m04._diagnostic(d, label, expected_abi=profile)
        for key in ("schemaVersion", "enabled", "runtimeAbiVersion", "metadataBudgetCapabilityVersion",
                    "recoveryCapabilityVersion", "startupCandidateSchemaVersion", "startupObservationMode", "startupCandidateNames"):
            exact(d[key], final[key], label + "." + key)
        g, e, c = (d[key] for key in ("generation", "enumerationGeneration", "classEnumerationGeneration"))
        require(0 <= g <= e <= c <= 1, label + ".incoherentGenerations")
        if mode == "MetadataFailure":
            exact((g, e, c), (0, 0, 0), label + ".metadataFailurePublished")
        configured = d["state"] != "Disabled"
        begun = d["state"] not in ("Disabled", "CandidatesRegistered")
        exact(d["baselineBuildId"], data["baselineBuildId"] if configured else "", label + ".baselineBuildId")
        exact(d["stableAotNames"], physical_stable_names(data, d, label) if configured else [], label + ".stableAotNames")
        exact(d["patchId"], data["patchId"] if begun else "", label + ".patchId")
        exact(d["closureLoadOrder"], closure if begun else [], label + ".closureLoadOrder")
        exact(d["expected"], len(closure) if begun else 0, label + ".expected")
        exact([row["name"] for row in d["assemblies"]], closure if begun else [], label + ".assemblies")
        exact(d["staged"], sum(row["skeletonBuilt"] for row in d["assemblies"]), label + ".staged")
        exact(d["retainedBytes"], sum(row["dllLength"] + row["pdbLength"] for row in data["inputs"]
                                       if any(a["name"] == row["name"] and a["skeletonBuilt"] for a in d["assemblies"])),
              label + ".retainedBytes")
        require(d["state"] in ("Disabled", "CandidatesRegistered", "Staging", "Staged", "Validated", "Committing", "Committed", "Failed", "FailedAfterCommit"),
                label + ".unexpectedState")
        if g:
            require(d["state"] in ("Committing", "Committed", "FailedAfterCommit"), label + ".publishedState")
        if d["state"] in ("Committed", "FailedAfterCommit"):
            exact(g, 1, label + ".terminalPublication")
        allowed_states = {"Staging", "Staged", "Validated", "Committing"}
        allowed_states.add(final["state"])
        require(d["state"] in allowed_states, label + ".modeState")
        allowed_errors = {13, 2} if d["state"] == "Failed" else {19, 18} if d["state"] == "FailedAfterCommit" else {0}
        require(d["lastError"] in allowed_errors, label + ".modeError")
        ready_names = [event["name"] for event in d["events"] if event["kind"] == "metadata-ready"]
        metadata_ready = d["state"] in ("Validated", "Committing", "Committed", "FailedAfterCommit")
        # Validate holds the transaction mutex across metadata initialization.
        # These observer modes therefore expose either pre-Validate metadata,
        # the first-provider Q04 refusal, or the fully initialized closure.
        exact(ready_names, closure if metadata_ready else [], label + ".metadataReadyEvents")
        for row in d["assemblies"]:
            exact(row["mvid"], source_identities[row["name"]] if row["skeletonBuilt"] else "", label + ".mvid")
            exact(row["runtimeMetadataInitialized"], metadata_ready, label + ".privateMetadataReadiness")
            require(not row["runtimeMetadataInitialized"] or row["skeletonBuilt"],
                    label + ".metadataWithoutSkeleton")
            exact(row["published"], bool(g), label + ".atomicPublication")
            if g: require(row["runtimeMetadataInitialized"] and row["skeletonBuilt"], label + ".publicationReadiness")
            else: require(not row["moduleInitializerAttempted"] and not row["moduleInitializerRan"], label + ".privateInitializer")
        exact(d["commitOrder"], closure[:len(d["commitOrder"])], label + ".commitPrefix")
        exact(d["events"], final["events"][:len(d["events"])], label + ".eventPrefix")
        require(any(row["kind"] == "transaction-begun" for row in d["events"]),
                label + ".missingTransactionEvent")
        exact([row["name"] for row in d["events"] if row["kind"] == "skeleton-created"],
              [row["name"] for row in d["assemblies"] if row["skeletonBuilt"]], label + ".skeletonEvents")
        exact(d["commitOrder"], [row["name"] for row in d["events"] if row["kind"] == "initializer-complete"],
              label + ".completedInitializerEvents")
        verify_first_use_history(d["baselineUses"], [], data, label + ".firstUseHistory")
        final_uses = {use["name"]: use for use in final["baselineUses"]}
        for use in d["baselineUses"]:
            exact(use, final_uses.get(use["name"]), label + ".finalFirstUse." + use["name"])
        exact([row for row in d["ordinaryAssemblies"] if not row["isInterpreter"]],
              [row for row in final["ordinaryAssemblies"] if not row["isInterpreter"]], label + ".physicalAotRetention")
        exact(sorted(row["name"] for row in d["ordinaryAssemblies"] if row["isInterpreter"]),
              sorted(closure if e else []), label + ".ordinaryPublication")
        for row in d["ordinaryClasses"]:
            if row["usesStagedMetadata"]:
                require(c == 1, label + ".privateClassLeak")
            if row["isInterpreter"]:
                require(c == 1 and row["assemblyName"] in closure, label + ".unpublishedInterpreterClass")
        return d

    previous_uses = []
    for index, sample in enumerate(samples):
        d = raw(sample, "early.observer[" + str(index) + "]")
        # State and usage are copied under separate locks. A query that copied
        # Staging can acquire new nonclosure uses while Validate runs before its
        # usage copy. Only the handshake's first sample is certainly pre-Validate.
        verify_first_use_history(d["baselineUses"], previous_uses, data, "early.observer.firstUseHistory")
        previous_uses = d["baselineUses"]
        generation = tuple(d[key] for key in ("generation", "enumerationGeneration", "classEnumerationGeneration"))
        require(all(a <= b for a, b in zip(previous, generation)), "early.observer generation regressed")
        require(sample["ticks"] >= previous_ticks, "early.observer clock regressed")
        previous, previous_ticks = generation, sample["ticks"]
        if index == 0:
            exact(d["state"], "Staging", "early.observer.initialState")
            exact(d["baselineUses"], [], "early.observer.initialFirstUse")
            exact(generation, (0, 0, 0), "early.observer.initialGeneration")
        if sample["phase"] == "before" and d["closureLoadOrder"] and generation[0] == 0:
            saw_private_transaction = True
        if sample["phase"] == "after":
            # Lazy stable BCL class caches may grow between queries. All
            # transaction and publication facts must still match the main tail.
            for key in final:
                if key != "ordinaryClasses":
                    exact(d[key], final[key], "early.observer.afterMatchesTerminal." + key)
    require(saw_private_transaction, "early.observer missing retained private-transaction sample")
    # Ordinary M07 P01-P05 fixtures do not enable the M03 Console markers.
    # Native attempted/ran flags above still cover every committed member.
    # Only the dedicated throwing fixture enables captured M03-INIT lines.
    expected_initializers = closure[:closure.index(failures.INITIALIZER_TARGET) + 1] if mode == "InitializerFailure" else []
    exact([row["name"] for row in initializers], expected_initializers, "early.initializerOrder")
    previous_ticks = 0
    for index, row in enumerate(initializers):
        fields(row, "name diagnostics", "early.initializer")
        sample = row["diagnostics"]
        exact(sample["phase"], "initializer", "early.initializer.phase")
        exact(sample["threadId"], receipt["managedThreadId"], "early.initializer.thread")
        require(sample["ticks"] >= previous_ticks, "early.initializer clock regressed")
        previous_ticks = sample["ticks"]
        d = raw(sample, "early.initializer." + row["name"])
        exact(d["state"], "Committing", "early.initializer.state")
        exact(tuple(d[key] for key in ("generation", "enumerationGeneration", "classEnumerationGeneration")),
              (1, 1, 1), "early.initializer.fullPublication")
        exact(d["commitOrder"], closure[:index], "early.initializer.completedPrefix")
        exact([a["moduleInitializerAttempted"] for a in d["assemblies"]],
              [name in closure[:index + 1] for name in closure], "early.initializer.attemptedPrefix")
        exact([a["moduleInitializerRan"] for a in d["assemblies"]],
              [name in closure[:index] for name in closure], "early.initializer.ranPrefix")


def verify_early_receipt(path: Path, capsule_path: Path, expected_mode: str,
                         expected_pid: int | None = None, profile: int = 1) -> dict[str, Any]:
    path = canonical(path, path, "early receipt")
    receipt = fields(read(path), RECEIPT_FIELDS, str(path))
    capsule_path = canonical(capsule_path, path, "early capsule")
    data = capsule.decode(capsule_path.read_bytes())
    exact(data["mode"], expected_mode, "early.capsuleMode")
    cap_hash = digest(capsule_path)
    exact(receipt["schemaVersion"], 1, "early.schemaVersion")
    exact(receipt["kind"], EARLY_KIND, "early.kind")
    exact(receipt["mode"], expected_mode, "early.mode")
    expected_result = "Passed" if expected_mode in POSITIVE_MODES or expected_mode == "Baseline" else \
        "PassedExpectedFailure" if expected_mode in FAILURE_MODES else "PassedExpectedRejection"
    exact(receipt["result"], expected_result, "early.result")
    exact(receipt["error"], "", "early.error")
    exact(receipt["capsulePath"], str(capsule_path), "early.capsulePath")
    exact(receipt["capsuleSha256"], cap_hash, "early.capsuleSha256")
    exact(receipt["resultPath"], str(path), "early.resultPath")
    exact(receipt["baselineBuildId"], data["baselineBuildId"], "early.baselineBuildId")
    exact(receipt["runtimeAbiHash"], data["runtimeAbiHash"], "early.runtimeAbiHash")
    exact(receipt["patchId"], data["patchId"], "early.patchId")
    pid = integer(receipt["processId"], "early.processId", 1)
    if expected_pid is not None: exact(pid, expected_pid, "early.processId")
    integer(receipt["managedThreadId"], "early.managedThreadId", 1)
    integer(receipt["stopwatchFrequency"], "early.stopwatchFrequency", 1)
    integer(receipt["elapsedTicks"], "early.elapsedTicks")
    callback = integer(receipt["callbackReturnCode"], "early.callbackReturnCode")
    expected_callback = 0 if expected_mode in POSITIVE_MODES or expected_mode == "Baseline" else 1
    exact(callback, expected_callback, "early.callbackReturnCode")
    verify_byte_inputs(receipt, data, "early")
    operations = receipt["operations"]
    expected_operations = _expected_operations(expected_mode, [r["name"] for r in data["inputs"]])
    exact(len(operations), len(expected_operations), "early.operationCount")
    for index, (row, expected) in enumerate(zip(operations, expected_operations)):
        item = fields(row, OPERATION_FIELDS, f"early.operations[{index}]")
        exact((item["phase"], item["code"], item["intCode"]), expected, f"early.operations[{index}]")
        integer(item["intCode"], f"early.operations[{index}].intCode")
        integer(item["startedTicks"], f"early.operations[{index}].startedTicks")
        integer(item["elapsedTicks"], f"early.operations[{index}].elapsedTicks")
    for previous, current in zip(operations, operations[1:]):
        require(current["startedTicks"] >= previous["startedTicks"] + previous["elapsedTicks"],
                "early.operationTimeRegressed")
    require(sum(item["elapsedTicks"] for item in operations) <= receipt["elapsedTicks"], "early.operationDurationExceedsTotal")
    sizes = _ordered_sizes(data, expected_mode)
    snapshots = receipt["snapshots"]
    expected_phases = _expected_snapshots(expected_mode, [r["name"] for r in data["inputs"]])
    exact([row.get("phase") for row in snapshots], expected_phases, "early.snapshotPhases")
    require(profile in (1, 2), "early: unsupported metadata profile")
    parsed = [_verify_snapshot(row, sizes, data["candidates"], f"early.snapshots[{i}]", profile)
              for i, row in enumerate(snapshots)]
    _verify_timeline(parsed, expected_phases, data)
    _verify_observers(receipt, data, parsed, profile)
    complete = all(item["profileComplete"] for item in parsed)
    return {"receipt": receipt, "capsule": data, "pid": pid, "diagnosticProfileComplete": complete,
            "snapshots": parsed}


def _load_runner():
    import importlib.util
    path = Path(__file__).with_name("run-m07-players.py")
    spec = importlib.util.spec_from_file_location("m07_player_runner_r01_early", path)
    require(spec is not None and spec.loader is not None, "Cannot load M07 launcher helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _prepare(project: Path, fixture: Path, on: Path, off: Path, replay: Path,
             failure_path: Path | None, negative_path: Path | None, modes: list[str]) -> dict[str, Any]:
    context = verify_inputs(project, fixture, on, off, replay)
    profile = failures.metadata_profile(context, "R01 early")
    if profile == 1:
        r01_results.require_r01_inputs(context)
    runner = _load_runner()
    inventory = runner.collect_inputs(fixture, replay, (on, off))
    prepared_failures = None
    if set(modes) & FAILURE_MODES:
        require(failure_path is not None and negative_path is not None,
                "Failure modes require verified failure fixtures and Q04 negative input")
        prepared_failures = failures.prepare(project, fixture, on, off, replay, failure_path, negative_path)
        inventory |= prepared_failures["inventory"]
    # r00_player_inputs intentionally returns only the admitted context.  Keep
    # the independently verified baseline resource projection for the exact
    # M07 case verifier without changing that shared contract.
    _, _, _, _, resources = m07.verify_inputs(fixture)
    return {"context": context, "profile": profile, "runner": runner, "inventory": inventory,
            "failures": prepared_failures, "baselineResources": resources}


def _capsule_for(prepared: dict[str, Any], mode: str, fixture_path: Path, output: Path,
                 patch_id: str = "P03") -> dict[str, Any]:
    return capsule.write_capsule(output, expected_capsule(prepared, mode, fixture_path, patch_id))


def expected_capsule(prepared: dict[str, Any], mode: str, fixture_path: Path,
                     patch_id: str = "P03") -> dict[str, Any]:
    """Reconstruct admitted inputs; a capsule's self-hash is not admission."""
    context = prepared["context"]
    replacement = None
    if prepared["failures"] is not None:
        replacement = {"initializer": prepared["failures"]["failures"]["initializer"],
                       "negative": prepared["failures"]["negative"]}
    return capsule.from_context(context, mode, patch_id, fixture_path, replacement)


def command_for(prepared: dict[str, Any], mode: str, fixture_path: Path, on_path: Path,
                capsule_path: Path, early_result: Path, m07_result: Path, log_path: Path,
                m07_mode: str = DEFAULT_M07_MODE) -> list[str]:
    build = prepared["context"]["on"]
    command = [str(prepared["runner"].executable_for(build["output"])), "-batchmode", "-nographics",
               "-shadowEarlyCapsule", str(capsule_path), "-shadowEarlyCapsuleSha256", digest(capsule_path),
               "-shadowEarlyResult", str(early_result)]
    if mode in POSITIVE_MODES:
        command += ["-shadowM07Mode", m07_mode, "-shadowM07Fixtures", str(fixture_path),
                    "-shadowM07PlayerReceipt", str(on_path), "-shadowM07Result", str(m07_result)]
    command += ["-logFile", str(log_path)]
    return command


def verify_imported_snapshots(early: dict[str, Any], m07_result: dict[str, Any]) -> None:
    """The handoff imports these exact snapshots; it does not recapture them."""
    rows = m07_result.get("snapshots")
    require(type(rows) is list, "early.handoff.snapshots")
    for source_phase, target_phase in (
        ("after-stage", "staged"),
        ("after-validate", "validated-resource-precheck-complete"),
    ):
        sources = [row for row in early["receipt"]["snapshots"] if row["phase"] == source_phase]
        targets = [row for row in rows if row.get("phase") == target_phase]
        exact(len(sources), 1, "early.handoff.sourceCount." + source_phase)
        exact(len(targets), 1, "early.handoff.targetCount." + target_phase)
        fields(targets[0], "phase diagnostics", "early.handoff." + target_phase)
        exact(targets[0]["diagnostics"], _json(sources[0]["diagnosticsJson"], "early.handoff.source"),
              "early.handoff.importedDiagnostics." + target_phase)


def verify_suite(launch_path: Path) -> dict[str, Any]:
    launch_path = canonical(launch_path, launch_path, "early launch receipt")
    launch = fields(read(launch_path), LAUNCH_FIELDS, str(launch_path))
    exact(launch["schemaVersion"], 1, "launch.schemaVersion")
    exact(launch["kind"], LAUNCH_KIND, "launch.kind")
    m07_mode = launch["m07Mode"]
    require(m07_mode in m07.MODES and m07_mode != "T07-14-FeatureOff", "launch.m07Mode is not an ON M07 mode")
    requested = launch["requestedModes"]
    require(type(requested) is list and requested and all(mode in MODES for mode in requested), "launch.requestedModes")
    require(requested == list(dict.fromkeys(requested)), "launch.requestedModes contains duplicates")
    if m07_mode != DEFAULT_M07_MODE:
        exact(requested, ["Control"], "launch.m07Mode diagnostic scope")
    exact(launch["fullModeInventory"], list(MODES), "launch.fullModeInventory")
    exact(launch["diagnosticOnly"], True, "launch.diagnosticOnly")
    exact(launch["completedModes"], len(requested), "launch.completedModes")
    exact(launch["inputsUnchanged"], True, "launch.inputsUnchanged")
    project = canonical(launch["projectRoot"], launch_path, "launch.projectRoot", True)
    fixture = canonical(launch["fixtureManifestPath"], launch_path, "launch.fixtureManifestPath")
    on = canonical(launch["onBuildReceiptPath"], launch_path, "launch.onBuildReceiptPath")
    off = canonical(launch["offBuildReceiptPath"], launch_path, "launch.offBuildReceiptPath")
    replay = canonical(launch["replayReceiptPath"], launch_path, "launch.replayReceiptPath")
    failure_path = Path(launch["failureFixturesPath"]) if launch["failureFixturesPath"] else None
    negative_path = Path(launch["negativeInputPath"]) if launch["negativeInputPath"] else None
    if failure_path is not None: failure_path = canonical(failure_path, launch_path, "launch.failureFixturesPath")
    if negative_path is not None: negative_path = canonical(negative_path, launch_path, "launch.negativeInputPath")
    prepared = _prepare(project, fixture, on, off, replay, failure_path, negative_path, requested)
    exact(launch["sourcePins"], prepared["context"]["sourcePins"], "launch.sourcePins")
    rows = launch["processLaunches"]
    require(type(rows) is list and len(rows) == len(requested), "launch.processLaunches")
    capsule_inputs = set()
    for row in rows:
        capsule_input = Path(row.get("capsulePath", ""))
        require(capsule_input.is_absolute() and capsule_input.is_file() and not capsule_input.is_symlink(),
                "launch capsule input is missing")
        capsule_inputs.add(capsule_input.resolve(strict=True))
    inventory = {str(path): digest(path) for path in sorted(set(prepared["inventory"]) | capsule_inputs)}
    exact(launch["inputHashesBefore"], inventory, "launch.inputHashesBefore")
    exact(launch["inputHashesAfter"], inventory, "launch.inputHashesAfter")
    result_dir = canonical(launch["resultDirectory"], launch_path, "launch.resultDirectory", True)
    exact([row.get("mode") for row in rows], requested, "launch.processModes")
    summaries = []
    pids = set()
    # Bounded profile success never establishes whole-milestone acceptance.
    complete = True
    for index, row in enumerate(rows):
        fields(row, PROCESS_FIELDS, f"launch.process[{index}]")
        mode = requested[index]
        exact(row["mode"], mode, mode + ".mode")
        pid = integer(row["processId"], mode + ".processId", 1)
        require(pid not in pids, mode + ": reused process ID")
        pids.add(pid)
        for key in ("startedAtUnix", "durationSeconds"):
            require(type(row[key]) in (int, float) and math.isfinite(row[key]) and row[key] > 0,
                    mode + "." + key)
        exact(row["passed"], True, mode + ".passed")
        exact(row["error"], "", mode + ".error")
        require(row["timedOut"] is False, mode + ": timed out process")
        capsule_path = canonical(row["capsulePath"], launch_path, mode + ".capsule")
        exact(row["capsuleSha256"], digest(capsule_path), mode + ".capsuleSha256")
        patch_id = m07.MODE_PATCH[m07_mode] if mode == "Control" else "P03"
        admitted_capsule = expected_capsule(prepared, mode, fixture, patch_id)
        exact(capsule.decode(capsule_path.read_bytes()), admitted_capsule, mode + ".admittedCapsule")
        early_path = bound(row["earlyResultPath"], row["earlyResultSha256"], launch_path, mode + ".earlyResult")
        expected_dir = result_dir / mode
        exact(capsule_path.parent, expected_dir, mode + ".capsuleDirectory")
        exact(early_path, expected_dir / "r01-early.json", mode + ".earlyResultPath")
        expected_m07 = expected_dir / ("m07-" + m07_mode + ".json")
        expected_command = command_for(prepared, mode, fixture, on, capsule_path, early_path,
                                       expected_m07, expected_dir / "unity.log", m07_mode)
        exact(row["command"], expected_command, mode + ".command")
        exact(row["logPath"], str(expected_dir / "unity.log"), mode + ".logPath")
        exact(row["consolePath"], str(expected_dir / "console.log"), mode + ".consolePath")
        log_path = bound(row["logPath"], row["logSha256"], launch_path, mode + ".log")
        console_path = bound(row["consolePath"], row["consoleSha256"], launch_path, mode + ".console")
        verify_startup_logs(mode, log_path, console_path)
        exact(row["inputHashesBefore"], inventory, mode + ".inputHashesBefore")
        exact(row["inputHashesAfter"], inventory, mode + ".inputHashesAfter")
        early = verify_early_receipt(early_path, capsule_path, mode, row["processId"], prepared["profile"])
        exact(early["receipt"]["patchId"], admitted_capsule["patchId"], mode + ".patchId")
        if mode in POSITIVE_MODES:
            exact(row["exitCode"], 0, mode + ".exitCode")
            m07_path = bound(row["m07ResultPath"], row["m07ResultSha256"], launch_path, mode + ".m07Result")
            exact(m07_path, expected_m07, mode + ".m07ResultPath")
            exact(read(m07_path)["processId"], row["processId"], mode + ".m07PID")
            exact(read(m07_path)["mode"], m07_mode, mode + ".m07Mode")
            verify_imported_snapshots(early, read(m07_path))
            m07.verify_case(m07_path, prepared["context"]["manifest"], prepared["context"]["baseline"],
                            prepared["context"]["fixtures"], prepared["baselineResources"],
                            prepared["context"]["on"], prepared["context"]["off"])
        elif mode in REJECTION_MODES:
            exact(row["exitCode"], 1, mode + ".explicitRejectionExit")
            exact(row["m07ResultPath"], "", mode + ".m07ResultPath")
            exact(row["m07ResultSha256"], "", mode + ".m07ResultSha256")
            require(not expected_m07.exists(), mode + ": rejected startup produced an M07 handoff")
        else:
            complete = False
            exact(row["exitCode"], 0, mode + ".baselineExit")
            exact(row["m07ResultPath"], "", mode + ".m07ResultPath")
            exact(row["m07ResultSha256"], "", mode + ".m07ResultSha256")
        exact(row["inputHashesBefore"], row["inputHashesAfter"], mode + ".inputHashes")
        exact(row["inputsUnchanged"], True, mode + ".inputsUnchanged")
        complete = complete and early["diagnosticProfileComplete"]
        summaries.append({"mode": mode, "processId": early["pid"],
                          "diagnosticProfileComplete": early["diagnosticProfileComplete"],
                          "earlyReceipt": str(early_path),
                          "m07Receipt": str(expected_m07) if mode in POSITIVE_MODES else ""})
    exact(launch["inputHashesAfter"], launch["inputHashesBefore"], "launch.inputHashesAfter")
    status = "PassedBoundedProfile" if complete else "DiagnosticIncomplete"
    return {"schemaVersion": 1, "kind": "R01EarlyVerification", "result": status,
            "acceptance": "R01-Early-BoundedProfile" if complete else "R01-Early-Diagnostic-Incomplete",
            "milestoneAccepted": False,
            "requestedModes": requested, "fullModeInventory": list(MODES),
            "diagnosticOnly": True,
            "observerPolicy": "At most 16 retained raw samples per phase; discarded queries are counted, not semantically verified.", "sourcePins": prepared["context"]["sourcePins"],
            "launchReceipt": str(launch_path), "launchReceiptSha256": digest(launch_path),
            "modes": summaries,
            "scope": "Requested early modes only. Full R01 acceptance, Baseline handoff, native stack evidence and remaining M07 matrices require separate evidence."}



def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--launch-receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    result = verify_suite(args.launch_receipt)
    output = args.output.absolute()
    require(not output.exists() and not output.is_symlink() and output == output.resolve(), "R01 output must be new")
    require(output.parent.is_dir() and not output.parent.is_symlink(), "R01 output parent must exist")
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print("R01 early results " + result["result"] + ": " + str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
