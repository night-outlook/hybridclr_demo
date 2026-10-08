"""Strict R01 Player evidence gate.

The launcher records process provenance; this module independently verifies the
fresh Player receipts, immutable input graph, exact R01 result schema, raw
capacity arithmetic, recovery disposition, and physical execution modes.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

import m07_results as m07
import m04_results as m04
from r00_player_inputs import verify_inputs
from shadow_tools import require


MODES = (
    "R01-P03-Control",
    "R01-P03-OrdinaryFirst",
    "R01-P03-OrdinaryAfterReserve",
    "R01-P03-Oversize",
    "R01-P03-Mismatch",
    "R01-PreConfigure-Type",
    "R01-PreConfigure-Object",
    "R01-PreConfigure-Cctor",
    "R01-PreConfigure-NativePrefab",
    "R01-FeatureOff",
)
OFF_MODE = "R01-FeatureOff"
STARTUP_OBSERVATION_GAP = "ObserveGap"
STARTUP_EARLY_GUARD = "RequireEarlyGuard"
STARTUP_EXPECTATIONS = (STARTUP_EARLY_GUARD, STARTUP_OBSERVATION_GAP)
INTERNAL = "AssemblyA.Implementation.Internal"
ORDINARY = "AssemblyShadowBaseline.HotUpdate"
PROFILE_VERSION = 1
PROFILE2_VERSION = 2
PROFILE2_MAX_IMAGES = 8192
PROFILE2_MAX_DLL_BYTES = 33554432
PROFILE2_USABLE_PAGE_CAPACITY = 524287
PROFILE2_CHARGED_PAGE_CEILING = 393215
PROFILE2_MINIMUM_FREE_PAGE_MARGIN = 131072
INDEX_BITS = 22
KIND_BITS = 2
SIZE_MULTIPLIER = 4
MAX_UINT64 = (1 << 64) - 1
KIND_MASKS = ((1 << 28) - 1, (1 << 26) - 1, (1 << 24) - 1, (1 << 22) - 1)
KIND_SHIFTS = (6, 4, 2, 0)
FRESH_CURSORS = (64, 0, 0, 0)
TERMINALS = (256, 256, 256, 255)
P03_MODES = frozenset(MODES[:-1])
COMMITTED_MODES = frozenset((
    "R01-P03-Control", "R01-P03-OrdinaryFirst", "R01-P03-OrdinaryAfterReserve"
))
ABORTED_MODES = frozenset(set(P03_MODES) - set(COMMITTED_MODES))
PRECONFIGURE_MODES = frozenset(mode for mode in MODES if mode.startswith("R01-PreConfigure-"))

RESULT_INTS = "schemaVersion processId profileVersion"
RESULT_STRINGS = "milestone mode result error startupExpectation unityVersion platform buildGuid playerDataPath baselineBuildId runtimeAbiHash target architecture resultPath fixtureManifestPath fixtureManifestSha256 playerBuildReceiptPath playerBuildReceiptSha256 baselineManifestPath baselineManifestSha256 patchId patchManifestPath patchManifestSha256 playerInputSnapshot playerInputSnapshotSha256 nativeLibraryPath nativeLibrarySha256 nativeMetadataPath nativeMetadataSha256 configureCode beginCode reserveCode stageCode validateCode commitCode abortCode stateCode state capacityCode capacityJson recoveryCode recoveryJson diagnosticsCode nativeDiagnosticsJson"
RESULT_ARRAYS = "candidateNames closureLoadOrder stageOrder checks stageResults capacitySnapshots stateSnapshots recoverySnapshots diagnosticSnapshots observations physicalWorld byteInputs"
RESULT_FIELDS = RESULT_INTS + " " + RESULT_STRINGS + " " + RESULT_ARRAYS + " il2cpp"


def read(path: Path) -> dict[str, Any]:
    value = m07.json_text(path.read_text(encoding="utf-8-sig"), str(path))
    require(type(value) is dict, f"{path}: expected JSON object")
    return value


def exact(actual: Any, expected: Any, label: str) -> None:
    m07.exact(actual, expected, label)


def integer(value: Any, label: str, minimum: int = 0) -> int:
    require(type(value) is int and not isinstance(value, bool) and value >= minimum,
            label + ": invalid integer")
    return value


def boolean(value: Any, label: str) -> bool:
    require(type(value) is bool, label + ": expected boolean")
    return value


def string(value: Any, label: str, nonempty: bool = True) -> str:
    require(type(value) is str and (not nonempty or bool(value)), label + ": invalid string")
    return value


def sha256(value: Any, label: str) -> str:
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
            label + ": invalid SHA-256")
    return value


def digest(path: Path) -> str:
    return m07.digest(path)


def canonical(value: Any, base: Path, label: str, directory: bool = False) -> Path:
    return m07.canonical(str(value), base, label, directory)


def bound(value: Any, expected_hash: Any, base: Path, label: str) -> Path:
    path = m07.bound(value, expected_hash, base, label)
    return path


def array(value: Any, label: str) -> list[Any]:
    require(type(value) is list, label + ": expected array")
    return value


def fields(value: Any, expected: str, label: str) -> dict[str, Any]:
    return m07.fields(value, expected, label)


def _load_m07_runner():
    path = Path(__file__).with_name("run-m07-players.py")
    spec = importlib.util.spec_from_file_location("m07_player_runner_r01", path)
    require(spec is not None and spec.loader is not None, "Cannot load M07 launcher helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_r01_inputs(context):
    profile = m07.diagnostic_abi(context["baseline"], "R01 baseline capability")
    declared = context["baseline"].get("nativeBudgetCapabilityVersion")
    require(type(declared) is int and declared in (PROFILE_VERSION, PROFILE2_VERSION),
            "R01 baseline profile must be explicitly declared as profile 1 or 2")
    exact(profile, declared, "R01 baseline profile")
    require(context["fixtures"], "R01 fixtures are missing")
    for patch_id, item in context["fixtures"].items():
        exact(item.get("r01Capability"), True, "R01 fixture capability: " + patch_id)
    return profile


def _known_mode(mode: str) -> None:
    require(mode in MODES, "Unknown R01 mode: " + mode)


def _u32_array(value: Any, label: str) -> list[int]:
    values = array(value, label)
    require(len(values) == 4, label + ": expected four values")
    return [integer(item, f"{label}[{index}]") for index, item in enumerate(values)]


def image_kind(size: int) -> int:
    require(type(size) is int and not isinstance(size, bool) and size >= 0,
            "image size must be a non-negative integer")
    if size == 0 or size > MAX_UINT64 // SIZE_MULTIPLIER:
        return -1
    scaled = size * SIZE_MULTIPLIER
    for kind in range(3, -1, -1):
        if scaled <= KIND_MASKS[kind]:
            return kind
    return -1


def _valid_budget_state(cursors: list[int]) -> bool:
    if len(cursors) != 4 or cursors[0] < FRESH_CURSORS[0]:
        return False
    return all(cursor <= TERMINALS[kind] and cursor % (1 << KIND_SHIFTS[kind]) == 0
               for kind, cursor in enumerate(cursors))


def evaluate_budget(initial: list[int], sizes: list[int]) -> dict[str, Any]:
    """Independent Python oracle for InterpreterImageBudget::Evaluate."""
    require(_valid_budget_state(initial), "invalid capacity cursor state")
    cursors = list(initial)
    allocations: list[dict[str, int]] = []
    first_failure_index = -1
    first_failure_size = 0
    failure = "None"
    for index, size in enumerate(sizes):
        reason = None
        if size == 0:
            reason = "InvalidSizeOrProfileState"
        elif size > MAX_UINT64 // SIZE_MULTIPLIER:
            reason = "InvalidSizeOrProfileState"
        elif size * SIZE_MULTIPLIER > KIND_MASKS[0] or image_kind(size) < 0:
            reason = "InvalidSizeOrProfileState"
        if reason is None:
            requested = image_kind(size)
            selected = -1
            for kind in range(requested, -1, -1):
                cursor = cursors[kind]
                stride = 1 << KIND_SHIFTS[kind]
                terminal = TERMINALS[kind]
                if cursor >= terminal or cursor + stride > terminal:
                    continue
                selected = kind
                image_index = cursor | (kind << 8)
                cursors[kind] += stride
                allocations.append({"imageIndex": image_index, "kind": kind, "dllSize": size})
                break
            if selected < 0:
                reason = "Exhausted"
        if reason is not None:
            first_failure_index = index
            first_failure_size = size
            failure = reason
            break
    fits = first_failure_index < 0
    return {
        "cursors": list(initial),
        "finalCursors": cursors,
        "allocations": allocations,
        "requiredImages": len(sizes),
        "acceptedImages": len(allocations),
        "firstFailingIndex": first_failure_index,
        "firstFailingSize": first_failure_size,
        "failureReason": failure,
        "fits": fits,
    }


def remaining_slots(cursors: list[int]) -> list[int]:
    return [(TERMINALS[kind] - cursors[kind]) // (1 << KIND_SHIFTS[kind])
            for kind in range(4)]


def verify_profile2_capacity(raw: dict[str, Any], sizes: list[int], label: str) -> dict[str, Any]:
    fields(raw, "schemaVersion enabled profileVersion maximumImageCount maximumDllBytes usablePageCapacity chargedPageCeiling minimumFreePageMargin reservedPages mappedPages lifetimeReservedImageCount remainingImageCount requiredImages acceptedImages firstFailingIndex firstFailingSize failureReason fitsPreliminary runtimeFinalizationRequired aggregateInputDllBytes aggregateInputDllBytesInformational ordinaryAllocatedCount shadowAllocatedCount reservedShadowImageCount", label)
    exact(raw["schemaVersion"], 2, label + ".schemaVersion")
    exact(raw["enabled"], True, label + ".enabled")
    exact(raw["profileVersion"], PROFILE2_VERSION, label + ".profileVersion")
    for key, expected in (("maximumImageCount", PROFILE2_MAX_IMAGES),
                          ("maximumDllBytes", PROFILE2_MAX_DLL_BYTES),
                          ("usablePageCapacity", PROFILE2_USABLE_PAGE_CAPACITY),
                          ("chargedPageCeiling", PROFILE2_CHARGED_PAGE_CEILING),
                          ("minimumFreePageMargin", PROFILE2_MINIMUM_FREE_PAGE_MARGIN)):
        exact(raw[key], expected, label + "." + key)
    require(type(sizes) is list and all(type(size) is int and not isinstance(size, bool) and size >= 0 for size in sizes),
            label + ".sizes: expected non-negative integers")
    for key in ("reservedPages", "mappedPages", "lifetimeReservedImageCount", "remainingImageCount",
                "requiredImages", "acceptedImages", "firstFailingSize", "aggregateInputDllBytes",
                "ordinaryAllocatedCount", "shadowAllocatedCount", "reservedShadowImageCount"):
        integer(raw[key], label + "." + key)
    boolean(raw["fitsPreliminary"], label + ".fitsPreliminary")
    boolean(raw["runtimeFinalizationRequired"], label + ".runtimeFinalizationRequired")
    boolean(raw["aggregateInputDllBytesInformational"], label + ".aggregateInputDllBytesInformational")
    exact(raw["requiredImages"], len(sizes), label + ".requiredImages")
    lifetime = raw["lifetimeReservedImageCount"]
    require(lifetime <= PROFILE2_MAX_IMAGES, label + ".lifetimeReservedImageCount")
    exact(lifetime, raw["ordinaryAllocatedCount"] + raw["reservedShadowImageCount"], label + ".lifetimeLedger")
    exact(raw["remainingImageCount"], PROFILE2_MAX_IMAGES - lifetime, label + ".remainingImageCount")
    require(raw["mappedPages"] <= raw["reservedPages"] <= PROFILE2_CHARGED_PAGE_CEILING,
            label + ".pageBounds")
    require(raw["lifetimeReservedImageCount"] <= raw["reservedPages"] and
            PROFILE2_USABLE_PAGE_CAPACITY - raw["reservedPages"] >= PROFILE2_MINIMUM_FREE_PAGE_MARGIN,
            label + ".pageAccounting")
    aggregate = 0
    for size in sizes:
        aggregate = min(MAX_UINT64, aggregate + size)
    exact(raw["aggregateInputDllBytes"], aggregate, label + ".aggregateInputDllBytes")
    exact(raw["runtimeFinalizationRequired"], True, label + ".runtimeFinalizationRequired")
    exact(raw["aggregateInputDllBytesInformational"], True, label + ".aggregateInputDllBytesInformational")
    failure_index = -1
    failure_reason = "None"
    if len(sizes) > PROFILE2_MAX_IMAGES - lifetime:
        failure_index, failure_reason = PROFILE2_MAX_IMAGES - lifetime, "ImageLimit"
    else:
        for index, size in enumerate(sizes):
            if size == 0:
                failure_index, failure_reason = index, "EmptyDll"
                break
            if size > PROFILE2_MAX_DLL_BYTES:
                failure_index, failure_reason = index, "DllTooLarge"
                break
    fits = failure_index == -1
    exact(raw["fitsPreliminary"], fits, label + ".fitsPreliminary")
    exact(raw["acceptedImages"], len(sizes) if fits else 0, label + ".acceptedImages")
    exact(raw["firstFailingIndex"], failure_index, label + ".firstFailingIndex")
    exact(raw["firstFailingSize"], 0 if failure_index < 0 else sizes[failure_index], label + ".firstFailingSize")
    exact(raw["failureReason"], failure_reason, label + ".failureReason")
    require(raw["reservedShadowImageCount"] <= lifetime and
            raw["shadowAllocatedCount"] <= raw["reservedShadowImageCount"],
            label + ".shadowLedger")
    return raw


def verify_capacity_snapshot(observation: dict[str, Any], sizes: list[int], label: str,
                             expected_profile: int | None = None) -> dict[str, Any]:
    require(type(observation) is dict, label + ": expected object")
    raw = m07.json_text(observation.get("rawJson"), label + ".rawJson")
    actual_profile = raw.get("profileVersion")
    require(actual_profile in (PROFILE_VERSION, PROFILE2_VERSION), label + ".profileVersion")
    if expected_profile is not None:
        exact(actual_profile, expected_profile, label + ".profileVersion")
    if actual_profile == PROFILE2_VERSION:
        fields(observation, "phase code rawJson orderedSizes parsed fits fitsPreliminary profileVersion indexBits kindBits cursors finalCursors remainingSlots requiredImages acceptedImages firstFailingIndex firstFailingSize failureReason ordinaryAllocatedCount shadowAllocatedCount reservedImageCount reservedPages mappedPages lifetimeReservedImageCount remainingImageCount reservedShadowImageCount", label)
        exact(observation["orderedSizes"], sizes, label + ".orderedSizes")
        exact(observation["code"], "Success", label + ".code")
        exact(observation["parsed"], True, label + ".parsed")
        parsed = verify_profile2_capacity(raw, sizes, label + ".rawJson")
        exact(observation["profileVersion"], 2, label + ".reported-profileVersion")
        exact(observation["fits"], parsed["fitsPreliminary"], label + ".reported-fits")
        exact(observation["fitsPreliminary"], parsed["fitsPreliminary"], label + ".reported-fitsPreliminary")
        for key in ("requiredImages", "acceptedImages", "firstFailingIndex", "firstFailingSize", "failureReason",
                    "ordinaryAllocatedCount", "shadowAllocatedCount", "reservedPages", "mappedPages",
                    "lifetimeReservedImageCount", "remainingImageCount", "reservedShadowImageCount"):
            exact(observation[key], parsed[key], label + ".reported-" + key)
        for key in ("indexBits", "kindBits", "reservedImageCount"):
            exact(observation[key], 0, label + ".profile2-empty-" + key)
        for key in ("cursors", "finalCursors", "remainingSlots"):
            exact(observation[key], [], label + ".profile2-empty-" + key)
        return parsed

    fields(observation, "phase code rawJson orderedSizes parsed fits profileVersion indexBits kindBits cursors finalCursors remainingSlots requiredImages acceptedImages firstFailingIndex firstFailingSize failureReason ordinaryAllocatedCount shadowAllocatedCount reservedImageCount", label)
    exact(observation["orderedSizes"], sizes, label + ".orderedSizes")
    exact(observation["code"], "Success", label + ".code")
    exact(observation["parsed"], True, label + ".parsed")
    fields(raw, "schemaVersion enabled profileVersion indexBits kindBits cursors remainingSlots requiredImages acceptedImages firstFailingIndex firstFailingSize failureReason fits allocations finalCursors ordinaryAllocatedCount shadowAllocatedCount reservedImageCount", label + ".rawJson")
    exact(raw["schemaVersion"], 1, label + ".schemaVersion")
    exact(raw["enabled"], True, label + ".enabled")
    exact(raw["profileVersion"], PROFILE_VERSION, label + ".profileVersion")
    exact(raw["indexBits"], INDEX_BITS, label + ".indexBits")
    exact(raw["kindBits"], KIND_BITS, label + ".kindBits")
    cursors = _u32_array(raw["cursors"], label + ".cursors")
    model = evaluate_budget(cursors, sizes)
    exact(_u32_array(raw["remainingSlots"], label + ".remainingSlots"), remaining_slots(cursors), label + ".remainingSlots")
    exact(raw["finalCursors"], model["finalCursors"], label + ".finalCursors")
    exact(raw["requiredImages"], model["requiredImages"], label + ".requiredImages")
    exact(raw["acceptedImages"], model["acceptedImages"], label + ".acceptedImages")
    exact(raw["firstFailingIndex"], model["firstFailingIndex"], label + ".firstFailingIndex")
    exact(raw["firstFailingSize"], model["firstFailingSize"], label + ".firstFailingSize")
    exact(raw["failureReason"], model["failureReason"], label + ".failureReason")
    exact(raw["fits"], model["fits"], label + ".fits")
    allocations = array(raw["allocations"], label + ".allocations")
    exact(allocations, model["allocations"], label + ".allocations")
    for key in ("ordinaryAllocatedCount", "shadowAllocatedCount", "reservedImageCount"):
        integer(raw[key], label + "." + key)
        exact(observation[key], raw[key], label + ".reported-" + key)
    for key in ("profileVersion", "indexBits", "kindBits", "firstFailingIndex", "firstFailingSize", "requiredImages", "acceptedImages"):
        exact(observation[key], raw[key], label + ".reported-" + key)
    exact(observation["fits"], raw["fits"], label + ".reported-fits")
    exact(observation["failureReason"], raw["failureReason"], label + ".reported-failureReason")
    exact(observation["cursors"], raw["cursors"], label + ".reported-cursors")
    exact(observation["finalCursors"], raw["finalCursors"], label + ".reported-finalCursors")
    exact(observation["remainingSlots"], raw["remainingSlots"], label + ".reported-remainingSlots")
    return raw


def _expected_closure(context: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    fixture = context["fixtures"]["P03"]
    return list(fixture["fixture"]["closureLoadOrder"]), fixture


def _expected_player(result: dict[str, Any], build: dict[str, Any], manifest: dict[str, Any], mode: str,
                     startup_expectation: str, expected_profile: int) -> None:
    for key, expected in (("schemaVersion", 1), ("milestone", "M07R-R01"), ("mode", mode),
                          ("result", "Passed"), ("error", ""), ("il2cpp", True),
                          ("unityVersion", manifest["unityVersion"]), ("target", manifest["target"]),
                          ("architecture", manifest["architecture"]), ("baselineBuildId", manifest["baselineBuildId"]),
                          ("runtimeAbiHash", manifest["runtimeAbiHash"]), ("buildGuid", build["player"]["buildGuid"]),
                          ("startupExpectation", startup_expectation)):
        exact(result.get(key), expected, mode + "." + key)
    exact(result["fixtureManifestPath"], manifest["_path"], mode + ".fixtureManifestPath")
    exact(result["fixtureManifestSha256"], digest(Path(manifest["_path"])), mode + ".fixtureManifestSha256")
    exact(result["playerBuildReceiptPath"], str(build["path"]), mode + ".playerBuildReceiptPath")
    exact(result["playerBuildReceiptSha256"], digest(build["path"]), mode + ".playerBuildReceiptSha256")
    exact(result["baselineManifestPath"], manifest["baselineManifestPath"], mode + ".baselineManifestPath")
    exact(result["baselineManifestSha256"], manifest["baselineManifestSha256"], mode + ".baselineManifestSha256")
    player = build["player"]
    for key, source in (("playerInputSnapshot", "inputSnapshot"), ("playerInputSnapshotSha256", "inputSnapshotHash"),
                        ("nativeLibraryPath", "nativeLibraryPath"), ("nativeLibrarySha256", "nativeLibrarySha256"),
                        ("nativeMetadataPath", "nativeMetadataPath"), ("nativeMetadataSha256", "nativeMetadataSha256")):
        exact(result[key], player[source], mode + "." + key)
    exact(result["platform"], "OSXPlayer", mode + ".platform")
    data_path = canonical(result["playerDataPath"], build["path"], mode + ".playerDataPath", True)
    require(data_path.is_relative_to(Path(player["playerOutput"])), mode + ": Player data escaped build output")
    exact(result["candidateNames"], manifest["candidateNames"], mode + ".candidateNames")
    exact(result["profileVersion"], expected_profile, mode + ".profileVersion")


def verify_byte_inputs(result: dict[str, Any], mode: str, closure: list[str], fixture: dict[str, Any], build: dict[str, Any]) -> list[int]:
    rows = array(result["byteInputs"], mode + ".byteInputs")
    if mode == OFF_MODE:
        exact(rows, [], mode + ".featureOffByteInputs")
        return []
    expected_count = len(closure) + (1 if mode in ("R01-P03-OrdinaryFirst", "R01-P03-OrdinaryAfterReserve") else 0)
    require(len(rows) == expected_count, mode + ".byteInputs: unexpected row count")
    expected_rows = []
    if mode == "R01-P03-OrdinaryFirst":
        expected_rows.append(("ordinary-before-configure" if mode.endswith("OrdinaryFirst") else "ordinary-after-reserve", ORDINARY, None))
    for name in closure:
        expected_rows.append(("closure", name, name))
    if mode == "R01-P03-OrdinaryAfterReserve":
        expected_rows.append(("ordinary-after-reserve", ORDINARY, None))
    sizes = []
    for index, (row, (phase, assembly, closure_name)) in enumerate(zip(rows, expected_rows)):
        label = f"{mode}.byteInputs[{index}]"
        fields(row, "phase assemblyName path originalSha256 actualSha256 originalLength actualLength transformation", label)
        exact(row["phase"], phase, label + ".phase")
        exact(row["assemblyName"], assembly, label + ".assemblyName")
        path = canonical(row["path"], Path(result["fixtureManifestPath"]), label + ".path")
        original = path.read_bytes()
        exact(row["originalLength"], len(original), label + ".originalLength")
        exact(row["originalSha256"], digest(path), label + ".originalSha256")
        actual = original
        transformation = row["transformation"]
        if closure_name is not None:
            expected_transformation = ("zero-padding-to-64MiB" if mode == "R01-P03-Oversize" and closure_name == closure[-1]
                                       else "one-byte zero-padding" if mode == "R01-P03-Mismatch" and closure_name == closure[0]
                                       else "verified closure bytes")
            exact(transformation, expected_transformation, label + ".transformation")
        if closure_name is not None:
            patch_fixture = fixture["fixture"]
            patch_row = next((item for item in fixture["patch"]["closure"]
                              if item["name"] == closure_name), None)
            require(patch_row is not None, label + ": closure member missing from verified patch")
            expected_path = canonical(patch_fixture["patchDirectory"], Path(result["fixtureManifestPath"]),
                                      label + ".patchDirectory", True) / patch_row["dll"]
            exact(path, expected_path.resolve(strict=True), label + ".verifiedInputPath")
            if "64MiB" in transformation:
                actual = original + b"\0" * (64 * 1024 * 1024 - len(original))
                exact(row["actualLength"], 64 * 1024 * 1024, label + ".actualLength")
            elif "one-byte" in transformation or "one-byte" in transformation.lower():
                actual = original + b"\0"
                exact(row["actualLength"], len(original) + 1, label + ".actualLength")
            else:
                exact(row["actualLength"], len(original), label + ".actualLength")
        else:
            snapshot_root = canonical(build["player"]["inputSnapshot"], build["path"], label + ".snapshotRoot", True)
            require(path.is_relative_to(snapshot_root), label + ": ordinary bytes escaped ON Player snapshot")
            # m07.verify_player has already verified the complete compiled,
            # linked, and fixed-image evidence. Reuse its reflection parser
            # here so R01 selects the exact M00 hash-named blob rather than a
            # valid-but-different filtered compiler DLL.
            reflection = m07.prior._reflection_snapshot(snapshot_root, build["snapshot"], build["path"], require_linked=True)
            require(reflection is not None, label + ": verified Player has no reflection binding configuration")
            sites = [declaration for declaration in reflection["declarations"]
                     if declaration.get("id") == "m00-normal-hot-update-image"]
            require(len(sites) == 1, label + ": M00 fixed-image site is missing or ambiguous")
            site = sites[0]
            require(site.get("kind") == "FixedAssemblyBytes" and site.get("imageSha256") and
                    site.get("providerAssemblyIdentity", "").split(",", 1)[0] == ORDINARY,
                    label + ": M00 fixed-image site identity differs from ordinary provider")
            provider_rows = [item for item in build["snapshot"].get("filteredAssemblies", [])
                             if item.get("name") in (ORDINARY, ORDINARY + ".dll")]
            require(len(provider_rows) == 1, label + ": ordinary provider identity is missing or ambiguous")
            provider_relative = Path(provider_rows[0]["path"])
            require(not provider_relative.is_absolute() and "\\" not in provider_rows[0]["path"],
                    label + ": ordinary provider path must be relative POSIX")
            provider_path = canonical(str((snapshot_root / provider_relative).resolve()), snapshot_root,
                                      label + ".providerPath")
            require(provider_path.is_file() and not provider_path.is_symlink() and
                    digest(provider_path) == provider_rows[0]["sha256"],
                    label + ": ordinary provider bytes differ from verified filtered identity")
            fixed_relative = Path("ReflectionBindings", "Images", site["imageSha256"] + ".dll.bytes")
            fixed_path = canonical(str((snapshot_root / fixed_relative).resolve()), snapshot_root,
                                   label + ".fixedImagePath")
            require(fixed_path.is_relative_to(snapshot_root), label + ": fixed image escaped ON Player snapshot")
            require(fixed_path.is_file() and not fixed_path.is_symlink(), label + ": fixed image blob is missing")
            exact(path, fixed_path, label + ".ordinaryInputPath")
            exact(row["originalSha256"], site["imageSha256"], label + ".ordinaryFixedImageHash")
            exact(row["actualLength"], len(original), label + ".ordinaryActualLength")
        actual_hash = __import__("hashlib").sha256(actual).hexdigest()
        exact(row["actualSha256"], actual_hash, label + ".actualSha256")
        # Mismatch deliberately reserves the verified/original lengths and
        # stages one padded byte.  All other closure rows reserve what they
        # actually stage.
        if closure_name is not None:
            sizes.append(len(original) if "one-byte" in transformation.lower() else len(actual))
    return sizes


def verify_capacity(result: dict[str, Any], mode: str, sizes: list[int]) -> None:
    snapshots = array(result["capacitySnapshots"], mode + ".capacitySnapshots")
    if mode == OFF_MODE:
        exact(snapshots, [], mode + ".featureOffCapacitySnapshots")
        exact(result.get("capacityCode"), "FeatureDisabled", mode + ".capacityCode")
        require(result.get("capacityJson") in (None, ""), mode + ": disabled capacity fabricated JSON")
        return
    expected_phases = {
        "R01-P03-Control": ["before-configure", "after-reserve"],
        "R01-P03-OrdinaryFirst": ["before-ordinary", "after-ordinary-before-configure", "after-reserve"],
        "R01-P03-OrdinaryAfterReserve": ["before-configure", "after-reserve", "after-ordinary-after-reserve"],
        "R01-P03-Oversize": ["before-configure", "after-failed-reserve"],
        "R01-P03-Mismatch": ["before-configure", "after-reserve", "after-mismatch"],
        "R01-PreConfigure-Type": ["after-preconfigure-observation"],
        "R01-PreConfigure-Object": ["after-preconfigure-observation"],
        "R01-PreConfigure-Cctor": ["after-preconfigure-observation"],
        "R01-PreConfigure-NativePrefab": ["after-preconfigure-observation"],
    }[mode]
    exact([row["phase"] for row in snapshots], expected_phases, mode + ".capacityPhases")
    raws = []
    phase_sizes = ([[]] + [sizes, sizes] if mode == "R01-P03-OrdinaryFirst" else
                   [sizes] * len(expected_phases))
    for index, row in enumerate(snapshots):
        raws.append(verify_capacity_snapshot(row, phase_sizes[index], f"{mode}.capacity[{index}]", result["profileVersion"]) )
    exact(result["capacityCode"], "Success", mode + ".capacityCode")
    exact(result["capacityJson"], snapshots[-1]["rawJson"], mode + ".capacityJson")
    if result["profileVersion"] == PROFILE2_VERSION:
        def ledger(row):
            return tuple(row[key] for key in ("reservedPages", "mappedPages", "lifetimeReservedImageCount",
                                               "remainingImageCount", "ordinaryAllocatedCount",
                                               "shadowAllocatedCount", "reservedShadowImageCount"))
        if mode == "R01-P03-Oversize":
            exact(raws[0]["fitsPreliminary"], False, mode + ".oversizeDryRun")
            exact(raws[0]["acceptedImages"], 0, mode + ".oversizeAtomicAccepted")
            exact(ledger(raws[1]), ledger(raws[0]), mode + ".failedReserveLedger")
            exact(raws[1]["acceptedImages"], raws[0]["acceptedImages"], mode + ".failedReserveAccepted")
        if mode == "R01-P03-Mismatch":
            before, after = raws[1], raws[2]
            exact(ledger(after), ledger(before), mode + ".mismatchLedger")
            for key in ("fitsPreliminary", "requiredImages", "acceptedImages", "firstFailingIndex", "firstFailingSize", "failureReason"):
                exact(after[key], before[key], mode + ".mismatch-" + key)
        if mode in COMMITTED_MODES or mode == "R01-P03-Mismatch":
            before, after = (raws[1], raws[2]) if mode == "R01-P03-OrdinaryFirst" else (raws[0], raws[1])
            added = len(sizes)
            exact(after["reservedShadowImageCount"], before["reservedShadowImageCount"] + added,
                  mode + ".reservationShadowCount")
            exact(after["lifetimeReservedImageCount"], after["ordinaryAllocatedCount"] + after["reservedShadowImageCount"],
                  mode + ".reservationLifetimeCount")
            exact(after["reservedPages"], before["reservedPages"] + added, mode + ".reservationPageCredit")
            exact(after["mappedPages"], before["mappedPages"], mode + ".reservationDoesNotMapPages")
            exact(after["ordinaryAllocatedCount"], before["ordinaryAllocatedCount"], mode + ".reservationOrdinaryCount")
            exact(after["shadowAllocatedCount"], before["shadowAllocatedCount"], mode + ".reservationShadowAllocations")
        if mode == "R01-P03-OrdinaryFirst":
            before, after = raws[0], raws[1]
            exact(after["ordinaryAllocatedCount"], before["ordinaryAllocatedCount"] + 1, mode + ".ordinaryFirstCount")
            exact(after["shadowAllocatedCount"], before["shadowAllocatedCount"], mode + ".ordinaryFirstShadowCount")
            exact(after["reservedShadowImageCount"], before["reservedShadowImageCount"], mode + ".ordinaryFirstShadowReservation")
            require(after["reservedPages"] >= before["reservedPages"] + 1, mode + ".ordinaryFirstPageCredit")
            require(after["mappedPages"] >= before["mappedPages"], mode + ".ordinaryFirstMappedMonotonic")
            exact(after["reservedShadowImageCount"], before["reservedShadowImageCount"], mode + ".ordinaryFirstShadowReservation")
        if mode == "R01-P03-OrdinaryAfterReserve":
            before, after = raws[1], raws[2]
            exact(after["ordinaryAllocatedCount"], before["ordinaryAllocatedCount"] + 1, mode + ".ordinaryCount")
            exact(after["shadowAllocatedCount"], before["shadowAllocatedCount"], mode + ".ordinaryShadowCount")
            require(after["reservedPages"] >= before["reservedPages"] + 1, mode + ".ordinaryPageCredit")
            require(after["mappedPages"] >= before["mappedPages"], mode + ".ordinaryMappedMonotonic")
            exact(after["reservedShadowImageCount"], before["reservedShadowImageCount"], mode + ".ordinaryShadowReservation")
    else:
        if mode in ("R01-P03-Oversize",):
            exact(raws[0]["fits"], False, mode + ".oversizeDryRun")
            exact(raws[1]["cursors"], raws[0]["cursors"], mode + ".failedReserveCursors")
            exact(raws[1]["finalCursors"], raws[0]["finalCursors"], mode + ".failedReserveFinalCursors")
            exact(raws[1]["reservedImageCount"], raws[0]["reservedImageCount"], mode + ".failedReserveReservedCount")
            exact(raws[1]["acceptedImages"], raws[0]["acceptedImages"], mode + ".failedReserveAccepted")
        if mode in COMMITTED_MODES or mode == "R01-P03-Mismatch":
            before, after = (raws[1], raws[2]) if mode == "R01-P03-OrdinaryFirst" else (raws[0], raws[1])
            exact(after["cursors"], before["finalCursors"], mode + ".reservationCursorAdvance")
            exact(after["reservedImageCount"], before["reservedImageCount"] + len(sizes), mode + ".reservationCount")
            exact(after["ordinaryAllocatedCount"], before["ordinaryAllocatedCount"], mode + ".reservationOrdinaryCount")
            exact(after["shadowAllocatedCount"], before["shadowAllocatedCount"], mode + ".reservationShadowCount")
        if mode == "R01-P03-OrdinaryFirst":
            require(raws[1]["ordinaryAllocatedCount"] > raws[0]["ordinaryAllocatedCount"], mode + ".ordinaryFirstCount")
            require(raws[1]["cursors"] != raws[0]["cursors"], mode + ".ordinaryFirstCursor")
        if mode == "R01-P03-Mismatch":
            exact(raws[2]["cursors"], raws[1]["cursors"], mode + ".mismatchNoCursorAdvance")
            exact(raws[2]["finalCursors"], raws[1]["finalCursors"], mode + ".mismatchFinalCursors")
        if mode == "R01-P03-OrdinaryAfterReserve":
            exact(raws[2]["shadowAllocatedCount"], raws[1]["shadowAllocatedCount"], mode + ".ordinaryShadowCount")
            exact(raws[2]["reservedImageCount"], raws[1]["reservedImageCount"], mode + ".ordinaryReservedCount")
            require(raws[2]["ordinaryAllocatedCount"] > raws[1]["ordinaryAllocatedCount"], mode + ".ordinaryCount")
            require(raws[2]["cursors"] != raws[1]["cursors"], mode + ".ordinaryCursorIsolation")


def verify_recovery(result: dict[str, Any], mode: str) -> None:
    snapshots = array(result["recoverySnapshots"], mode + ".recoverySnapshots")
    if mode == OFF_MODE:
        exact(snapshots, [], mode + ".featureOffRecoverySnapshots")
        exact(result.get("recoveryCode"), "FeatureDisabled", mode + ".recoveryCode")
        require(result.get("recoveryJson") in (None, ""), mode + ": disabled recovery fabricated JSON")
        return
    expected_state = "Committed" if mode in COMMITTED_MODES else "Aborted"
    expected_disposition = "ActiveShadow" if mode in COMMITTED_MODES else "BaselineEligibleAfterAbort"
    expected_code = 4 if mode in COMMITTED_MODES else 3
    exact([row["phase"] for row in snapshots], ["committed"] if mode in COMMITTED_MODES else ["aborted"], mode + ".recoveryPhases")
    for index, row in enumerate(snapshots):
        label = f"{mode}.recovery[{index}]"
        fields(row, "phase code rawJson parsed state disposition reason published abortAllowed baselineEligibilityRequiresStartupValidation stateCode dispositionCode terminalFailureCode retainedBytes", label)
        exact(row["code"], "Success", label + ".code")
        exact(row["parsed"], True, label + ".parsed")
        raw = m07.json_text(row["rawJson"], label + ".rawJson")
        fields(raw, "schemaVersion enabled capabilityVersion stateCode state published abortAllowed dispositionCode disposition terminalFailureCode reason retainedBytes baselineEligibilityRequiresStartupValidation", label + ".rawJson")
        exact(raw["schemaVersion"], 1, label + ".schemaVersion")
        exact(raw["enabled"], True, label + ".enabled")
        exact(raw["capabilityVersion"], 1, label + ".capabilityVersion")
        exact(raw["state"], expected_state, label + ".state")
        exact(raw["stateCode"], 6 if expected_state == "Committed" else 7, label + ".stateCode")
        exact(raw["published"], expected_state == "Committed", label + ".published")
        exact(raw["abortAllowed"], False, label + ".abortAllowed")
        exact(raw["disposition"], expected_disposition, label + ".disposition")
        exact(raw["dispositionCode"], expected_code, label + ".dispositionCode")
        exact(raw["terminalFailureCode"], 0, label + ".terminalFailureCode")
        exact(raw["baselineEligibilityRequiresStartupValidation"], expected_state == "Aborted", label + ".startupValidation")
        integer(raw["retainedBytes"], label + ".retainedBytes")
        for key in ("state", "stateCode", "published", "abortAllowed", "disposition", "dispositionCode",
                    "terminalFailureCode", "retainedBytes", "baselineEligibilityRequiresStartupValidation"):
            exact(row[key], raw[key], label + ".projection." + key)
    exact(result["recoveryCode"], "Success", mode + ".recoveryCode")
    exact(result["recoveryJson"], snapshots[-1]["rawJson"], mode + ".recoveryJson")


def verify_diagnostic_snapshots(result: dict[str, Any], mode: str, closure: list[str],
                                startup_expectation: str, expected_profile: int) -> None:
    snapshots = array(result["diagnosticSnapshots"], mode + ".diagnosticSnapshots")
    if mode == OFF_MODE:
        exact(snapshots, [], mode + ".featureOffDiagnosticSnapshots")
        return
    if mode in PRECONFIGURE_MODES:
        expected = ["before-preconfigure-observation"]
        if mode.endswith("NativePrefab"):
            expected += ["before-native-prefab-load", "after-native-prefab-load"]
        expected += ["after-preconfigure-observation", "before-configure", "configured", "aborted"]
    elif mode == "R01-P03-OrdinaryFirst":
        expected = ["ordinary-before-configure", "before-configure", "configured", "committed"]
    elif mode == "R01-P03-OrdinaryAfterReserve":
        expected = ["before-configure", "configured", "ordinary-after-reserve", "committed"]
    else:
        expected = ["before-configure", "configured", "aborted" if mode in ABORTED_MODES else "committed"]
    exact([row.get("phase") for row in snapshots], expected, mode + ".diagnosticPhases")
    expected_observation = "EarlyTracking" if startup_expectation == STARTUP_EARLY_GUARD else "ConfigureOnly"
    parsed = []
    for index, row in enumerate(snapshots):
        label = f"{mode}.diagnosticSnapshots[{index}]"
        fields(row, "phase code rawJson parsed", label)
        exact(row["code"], "Success", label + ".code")
        exact(row["parsed"], True, label + ".parsed")
        raw = m07.json_text(row["rawJson"], label + ".rawJson")
        fields(raw, m04.R01_DIAGNOSTIC_FIELDS, label + ".rawJson")
        m04._diagnostic(raw, label + ".rawJson", expected_abi=expected_profile)
        exact(raw["schemaVersion"], 1, label + ".schemaVersion")
        exact(raw["runtimeAbiVersion"], expected_profile, label + ".runtimeAbiVersion")
        exact(raw["enabled"], True, label + ".enabled")
        exact(raw["startupCandidateSchemaVersion"], 1, label + ".startupCandidateSchemaVersion")
        exact(raw["startupCandidateNames"], result["candidateNames"], label + ".startupCandidateNames")
        exact(raw["startupObservationMode"], expected_observation, label + ".startupObservationMode")
        exact(raw["metadataBudgetCapabilityVersion"], expected_profile, label + ".metadataBudgetCapabilityVersion")
        exact(raw["recoveryCapabilityVersion"], 1, label + ".recoveryCapabilityVersion")
        phase = row["phase"]
        wanted_state = ("CandidatesRegistered" if phase == "configured" else
                        "Committed" if phase == "committed" else "Aborted" if phase == "aborted" else
                        "Staging" if phase == "ordinary-after-reserve" else "Disabled")
        exact(raw["state"], wanted_state, label + ".state")
        parsed.append(raw)
    def use_names(raw: dict[str, Any]) -> list[str]:
        return [row["name"] for row in raw["baselineUses"]]
    if mode in PRECONFIGURE_MODES:
        after_observation = parsed[expected.index("after-preconfigure-observation")]
        if startup_expectation == STARTUP_EARLY_GUARD:
            require(set(use_names(after_observation)) & set(closure), mode + ": pre-Configure candidate use missing from raw diagnostics")
        else:
            exact(after_observation["baselineUses"], [], mode + ": ConfigureOnly must expose the observation gap")
        before_configure = parsed[expected.index("before-configure")]
        configured = parsed[expected.index("configured")]
        exact(configured["baselineUses"], before_configure["baselineUses"], mode + ": configure changed first-use history")
        if mode.endswith("NativePrefab") and startup_expectation == STARTUP_EARLY_GUARD:
            direct_after = parsed[expected.index("after-native-prefab-load")]
            require(set(use_names(direct_after)) & set(closure), mode + ": native prefab direct load did not precede candidate use")
    else:
        before_configure = parsed[expected.index("before-configure")]
        configured = parsed[expected.index("configured")]
        require(not (set(use_names(before_configure)) & set(closure)), mode + ": candidate used before Configure")
        exact(configured["baselineUses"], before_configure["baselineUses"], mode + ": Configure changed first-use history")


def verify_states(result: dict[str, Any], mode: str, startup_expectation: str) -> None:
    snapshots = array(result["stateSnapshots"], mode + ".stateSnapshots")
    if mode == OFF_MODE:
        exact(snapshots, [], mode + ".featureOffStateSnapshots")
        return
    expected = [("configured", "CandidatesRegistered"), ("begun", "Staging")]
    if mode in COMMITTED_MODES:
        expected += [("staged", "Staged"), ("validated", "Validated"), ("committed", "Committed")]
    elif mode == "R01-P03-Oversize" or mode == "R01-P03-Mismatch":
        expected += [("aborted", "Aborted")]
    else:
        expected += [("staged", "Staged")]
        # The early guard rejects Validate while the transaction is still in
        # Staged.  ObserveGap reaches Validated and records the gap honestly.
        expected += [("validated-or-early-guard",
                      "Staged" if startup_expectation == STARTUP_EARLY_GUARD else "Validated"),
                     ("aborted", "Aborted")]
    exact([(row["phase"], row["state"]) for row in snapshots], expected, mode + ".stateSnapshots")
    for row in snapshots:
        fields(row, "phase code state passed", mode + ".stateSnapshot")
    require(all(row["code"] == "Success" and row["passed"] is True for row in snapshots), mode + ".stateChecks")


def verify_physical(result: dict[str, Any], mode: str, closure: list[str], candidates: list[str]) -> None:
    rows = array(result["physicalWorld"], mode + ".physicalWorld")
    if mode in COMMITTED_MODES:
        exact([row["phase"] for row in rows], ["committed"] * len(candidates), mode + ".physicalPhases")
        exact([row["assemblyName"] for row in rows], candidates, mode + ".physicalNames")
        for row in rows:
            fields(row, "phase assemblyName code mode passed", mode + ".physicalRow")
            expected_shadow = row["assemblyName"] in closure
            exact(row["code"], "Success", mode + ".physicalCode")
            exact(row["mode"], "InterpreterShadow" if expected_shadow else "AotBaseline", mode + ".physicalMode")
            exact(row["passed"], True, mode + ".physicalPassed")
    else:
        exact(rows, [], mode + ".physicalWorld")


def verify_result(result_path: Path, mode: str, context: dict[str, Any], build: dict[str, Any],
                  startup_expectation: str, expected_profile: int | None = None) -> dict[str, Any]:
    result = fields(read(result_path), RESULT_FIELDS, str(result_path))
    for key in RESULT_INTS.split(): integer(result[key], str(result_path) + "." + key)
    integer(result["processId"], str(result_path) + ".processId", 1)
    for key in RESULT_STRINGS.split(): string(result[key], str(result_path) + "." + key, False)
    for key in RESULT_ARRAYS.split(): array(result[key], str(result_path) + "." + key)
    _known_mode(mode)
    exact(result["resultPath"], str(result_path), mode + ".resultPath")
    profile = require_r01_inputs(context)
    if expected_profile is not None:
        exact(expected_profile, profile, mode + ".expectedProfileBinding")
    manifest = context["manifest"]
    closure, fixture = _expected_closure(context)
    _expected_player(result, build, manifest, mode, startup_expectation, profile)
    if mode == OFF_MODE:
        exact(result["patchId"], "", mode + ".patchId")
        exact(result["patchManifestPath"], "", mode + ".patchManifestPath")
        exact(result["patchManifestSha256"], "", mode + ".patchManifestSha256")
        closure = []
    else:
        exact(result["patchId"], "P03", mode + ".patchId")
        exact(result["patchManifestPath"], fixture["fixture"]["patchManifest"], mode + ".patchManifestPath")
        exact(result["patchManifestSha256"], fixture["fixture"]["patchManifestSha256"], mode + ".patchManifestSha256")
    exact(result["closureLoadOrder"], closure, mode + ".closureLoadOrder")
    sizes = verify_byte_inputs(result, mode, closure, fixture, build)
    verify_capacity(result, mode, sizes)
    verify_diagnostic_snapshots(result, mode, closure, startup_expectation, profile)
    verify_states(result, mode, startup_expectation)
    verify_recovery(result, mode)
    verify_physical(result, mode, closure, list(manifest["candidateNames"]))
    checks = array(result["checks"], mode + ".checks")
    require(checks and len({row["name"] for row in checks}) == len(checks), mode + ".checks: missing or duplicate checks")
    for row in checks:
        fields(row, "name actual expected passed", mode + ".check")
        for key in ("name", "actual", "expected"):
            string(row[key], mode + ".check." + key, key == "name")
        exact(row["actual"], row["expected"], mode + ".check.outcome")
    require(all(row["passed"] is True for row in checks), mode + ".checks: reported failure")
    if mode != OFF_MODE:
        for key in ("configureCode", "beginCode"):
            exact(result[key], "Success", mode + "." + key)
        exact(result["diagnosticsCode"], "Success", mode + ".diagnosticsCode")
        exact(result["nativeDiagnosticsJson"], result["diagnosticSnapshots"][-1]["rawJson"], mode + ".nativeDiagnosticsJson")
    if mode in COMMITTED_MODES:
        for key in ("configureCode", "beginCode", "reserveCode", "validateCode", "commitCode"):
            exact(result[key], "Success", mode + "." + key)
        exact(result["abortCode"], "", mode + ".abortCode")
        stage_rows = array(result["stageResults"], mode + ".stageResults")
        exact([row["name"] for row in stage_rows], closure, mode + ".stageOrder")
        exact(result["stageOrder"], closure, mode + ".stageOrderField")
        byte_rows = [row for row in array(result["byteInputs"], mode + ".byteInputs")
                     if row["phase"] == "closure"]
        exact(len(stage_rows), len(byte_rows), mode + ".stageResultCount")
        for index, row in enumerate(stage_rows):
            label = f"{mode}.stageResults[{index}]"
            fields(row, "name code dllSha256 pdbSha256 actualLength", label)
            exact(row["code"], "Success", label + ".code")
            exact(row["dllSha256"], byte_rows[index]["actualSha256"], label + ".dllSha256")
            exact(row["actualLength"], byte_rows[index]["actualLength"], label + ".actualLength")
    elif mode == "R01-P03-Oversize":
        exact(result["reserveCode"], "MetadataCapacityExceeded", mode + ".reserveCode")
        exact(result["stageResults"], [], mode + ".stageResults")
        exact(result["abortCode"], "Success", mode + ".abortCode")
    elif mode == "R01-P03-Mismatch":
        exact(result["reserveCode"], "Success", mode + ".reserveCode")
        stage_rows = array(result["stageResults"], mode + ".stageResults")
        exact(len(stage_rows), 1, mode + ".mismatchStageCount")
        fields(stage_rows[0], "name code dllSha256 pdbSha256 actualLength", mode + ".mismatchStage")
        exact(stage_rows[0]["name"], closure[0], mode + ".mismatchName")
        exact(stage_rows[0]["code"], "MetadataBudgetMismatch", mode + ".mismatchCode")
        exact(stage_rows[0]["dllSha256"], result["byteInputs"][0]["actualSha256"], mode + ".mismatchHash")
        exact(stage_rows[0]["actualLength"], result["byteInputs"][0]["actualLength"], mode + ".mismatchLength")
        exact(result["abortCode"], "Success", mode + ".abortCode")
    elif mode in PRECONFIGURE_MODES:
        exact(result["reserveCode"], "Success", mode + ".reserveCode")
        exact(result["abortCode"], "Success", mode + ".abortCode")
        exact(result["stageOrder"], closure, mode + ".stageOrder")
        exact([row["name"] for row in result["stageResults"]], closure, mode + ".stageOrder")
        require(all(row["code"] == "Success" for row in result["stageResults"]), mode + ".stageResults")
    else:
        exact(result["reserveCode"], "FeatureDisabled", mode + ".reserveCode")
        for key in ("configureCode", "beginCode", "stageCode", "validateCode", "commitCode", "abortCode"):
            exact(result[key], "", mode + "." + key)
    expected_stages = [] if mode in (OFF_MODE, "R01-P03-Oversize") else closure[:1] if mode == "R01-P03-Mismatch" else closure
    stage_rows = result["stageResults"]
    exact([row.get("name") for row in stage_rows], expected_stages, mode + ".stageNames")
    byte_rows = {row["assemblyName"]: row for row in result["byteInputs"] if row["phase"] == "closure"}
    patch_rows = {row["name"]: row for row in fixture["patch"]["closure"]}
    for row in stage_rows:
        fields(row, "name code dllSha256 pdbSha256 actualLength", mode + ".stageResult")
        exact(row["dllSha256"], byte_rows[row["name"]]["actualSha256"], mode + ".stageHash")
        exact(row["actualLength"], byte_rows[row["name"]]["actualLength"], mode + ".stageLength")
        exact(row["pdbSha256"], patch_rows[row["name"]]["pdbSha256"] or "", mode + ".stagePdbHash")
    exact(result["stageCode"], stage_rows[-1]["code"] if stage_rows else "", mode + ".stageCode")
    if mode in (OFF_MODE, "R01-P03-Oversize", "R01-P03-Mismatch"):
        exact(result["stageOrder"], [], mode + ".unstagedOrder")
        exact(result["validateCode"], "", mode + ".unvalidatedCode")
    if mode not in COMMITTED_MODES:
        exact(result["commitCode"], "", mode + ".uncommittedCode")
    observations = array(result["observations"], mode + ".observations")
    for row in observations:
        fields(row, "phase kind detail path assemblyName passed", mode + ".observation")
        for key in ("phase", "kind", "detail", "path", "assemblyName"):
            string(row[key], mode + ".observation." + key, False)
        exact(row["passed"], True, mode + ".observation.passed")
    if mode in PRECONFIGURE_MODES:
        kind = mode.split("R01-PreConfigure-", 1)[1]
        mapped = {"Type": "type", "Object": "object", "Cctor": "cctor", "NativePrefab": "native-prefab-direct"}[kind]
        rows = [row for row in observations if row["phase"] == "before-configure"]
        require(len(rows) == 1 and rows[0]["kind"] == mapped and rows[0]["passed"] is True,
                mode + ": pre-Configure observation missing")
        expected_validate = ("BaselineAlreadyUsed" if startup_expectation == STARTUP_EARLY_GUARD
                             else "Success")
        result_row = [row for row in observations if row["phase"] == "preconfigure-result"]
        require(len(result_row) == 1 and result_row[0]["detail"] == expected_validate and
                result_row[0]["passed"] is True, mode + ": startup result mismatch")
        exact(result["validateCode"], expected_validate, mode + ".validateCode")
        if startup_expectation != STARTUP_EARLY_GUARD:
            require(all("EarlyGuard" not in str(row.get("detail", "")) for row in observations),
                    mode + ": early-guard claim is not accepted")
    if mode == "R01-P03-OrdinaryAfterReserve":
        require(any(row["kind"] == "reserved-slot-isolation" and row["passed"] is True for row in observations),
                mode + ": ordinary-after-reserve isolation observation missing")
    if mode in ("R01-P03-OrdinaryFirst", "R01-P03-OrdinaryAfterReserve"):
        require(any(row["kind"] in ("ordinary-interpreter-load", "reserved-slot-isolation") and row["passed"] is True for row in observations),
                mode + ": ordinary allocation observation missing")
    exact(result["state"], "Committed" if mode in COMMITTED_MODES else
          ("Disabled" if mode == OFF_MODE else "Aborted"), mode + ".finalState")
    exact(result["stateCode"], "FeatureDisabled" if mode == OFF_MODE else "Success",
          mode + ".finalStateCode")
    if mode == OFF_MODE:
        for key in ("configureCode", "beginCode", "stageCode", "validateCode", "commitCode", "abortCode", "diagnosticsCode", "nativeDiagnosticsJson"):
            require(result.get(key) in (None, ""), mode + "." + key + ": disabled mode fabricated operation")
    return {"mode": mode, "processId": result["processId"], "buildGuid": result["buildGuid"],
            "resultPath": str(result_path), "resultSha256": digest(result_path)}


def verify_suite(launch_path: Path, expected_startup: str = STARTUP_EARLY_GUARD) -> dict[str, Any]:
    require(expected_startup in STARTUP_EXPECTATIONS, "Unknown startup expectation: " + expected_startup)
    launch_path = canonical(str(launch_path), launch_path, "launch receipt")
    launch = fields(read(launch_path), "schemaVersion milestone diagnosticOnly startupExpectation fullModeInventory requestedModes completedModes processLaunches projectRoot fixtureManifestPath onBuildReceiptPath offBuildReceiptPath replayReceiptPath sourcePins resultDirectory inputHashesBefore inputHashesAfter inputsUnchanged note", str(launch_path))
    exact(launch["schemaVersion"], 1, "launch.schemaVersion")
    exact(launch["milestone"], "M07R-R01", "launch.milestone")
    exact(launch["diagnosticOnly"], expected_startup == STARTUP_OBSERVATION_GAP, "launch.diagnosticOnly")
    exact(launch["startupExpectation"], expected_startup, "launch.startupExpectation")
    exact(launch["fullModeInventory"], list(MODES), "launch.fullModeInventory")
    exact(launch["requestedModes"], list(MODES), "launch.requestedModes")
    exact(launch["completedModes"], len(MODES), "launch.completedModes")
    exact(launch["inputsUnchanged"], True, "launch.inputsUnchanged")
    exact(launch["inputHashesAfter"], launch["inputHashesBefore"], "launch.inputHashes")
    project = canonical(launch["projectRoot"], launch_path, "launch.projectRoot", True)
    fixture_path = canonical(launch["fixtureManifestPath"], launch_path, "launch.fixtureManifestPath", False)
    on_path = canonical(launch["onBuildReceiptPath"], launch_path, "launch.onBuildReceiptPath", False)
    off_path = canonical(launch["offBuildReceiptPath"], launch_path, "launch.offBuildReceiptPath", False)
    replay_path = canonical(launch["replayReceiptPath"], launch_path, "launch.replayReceiptPath", False)
    context = verify_inputs(project, fixture_path, on_path, off_path, replay_path)
    profile = require_r01_inputs(context)
    exact(launch["sourcePins"], context["sourcePins"], "launch.sourcePins")
    runner = _load_m07_runner()
    immutable = runner.collect_inputs(fixture_path, replay_path, (on_path, off_path))
    exact(launch["inputHashesBefore"], {str(path): digest(path) for path in sorted(immutable)},
          "launch.completeInputInventory")
    result_dir = canonical(launch["resultDirectory"], launch_path, "launch.resultDirectory", True)
    rows = array(launch["processLaunches"], "launch.processLaunches")
    exact([row["mode"] for row in rows], list(MODES), "launch.processModes")
    require(len({integer(row["processId"], "launch.pid", 1) for row in rows}) == len(MODES),
            "R01 modes must use distinct fresh processes")
    summary = []
    for row in rows:
        fields(row, "mode command processId startedAtUnix durationSeconds exitCode timedOut passed resultPath resultSha256 logPath consolePath error", "launch.process")
        mode = row["mode"]
        build = context["off"] if mode == OFF_MODE else context["on"]
        exact(row["exitCode"], 0, mode + ".exitCode")
        exact(row["timedOut"], False, mode + ".timedOut")
        exact(row["passed"], True, mode + ".launcherPassed")
        result_path = bound(row["resultPath"], row["resultSha256"], launch_path, mode + ".result")
        exact(result_path, result_dir / ("r01-" + mode + ".json"), mode + ".resultPath")
        exact(row["logPath"], str(launch_path.parent / (mode + ".unity.log")), mode + ".logPath")
        exact(row["consolePath"], str(launch_path.parent / (mode + ".console.log")), mode + ".consolePath")
        require(Path(row["logPath"]).is_file() and Path(row["consolePath"]).is_file(),
                mode + ": launcher logs are missing")
        expected_command = [str(runner.executable_for(build["output"])), "-batchmode", "-nographics",
                            "-shadowR01Mode", mode, "-shadowR01StartupExpectation", expected_startup,
                            "-shadowR01SnapshotReceiptSha256", digest(Path(build["player"]["inputSnapshot"]) / "assembly-snapshot.json"),
                            "-shadowM07Fixtures", str(fixture_path), "-shadowM07PlayerReceipt", str(build["path"]),
                            "-shadowR01Result", str(result_path), "-logFile", row["logPath"]]
        exact(row["command"], expected_command, mode + ".command")
        result = read(result_path)
        exact(result["processId"], row["processId"], mode + ".pid")
        exact(result["buildGuid"], build["player"]["buildGuid"], mode + ".buildGuid")
        data_path = canonical(result["playerDataPath"], result_path, mode + ".playerDataPath", True)
        require(data_path.is_relative_to(build["output"]), mode + ": Player data escaped executed app")
        summary.append(verify_result(result_path, mode, context, build, expected_startup, profile))
    return {"schemaVersion": 1, "milestone": "M07R-R01", "result": "Passed",
            "diagnosticOnly": expected_startup == STARTUP_OBSERVATION_GAP,
            "acceptance": ("DiagnosticOnly-ObserveGap" if expected_startup == STARTUP_OBSERVATION_GAP
                           else "Strict-RequireEarlyGuard"),
            "startupExpectation": expected_startup, "sourcePins": context["sourcePins"],
            "launchReceipt": str(launch_path), "launchReceiptSha256": digest(launch_path),
            "modes": summary,
            "scope": ("R01 native budget, reservation, recovery, physical identity, and startup guard evidence."
                      if expected_startup == STARTUP_EARLY_GUARD else
                      "R01 diagnostic evidence only; pre-Configure ObserveGap remains an explicit unclosed startup boundary.")}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--launch-receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--startup-expectation", choices=STARTUP_EXPECTATIONS,
                        default=STARTUP_EARLY_GUARD)
    args = parser.parse_args(argv)
    result = verify_suite(args.launch_receipt, args.startup_expectation)
    output = args.output.absolute()
    require(not output.exists() and not output.is_symlink() and output == output.resolve(),
            "R01 output must be a new canonical path")
    require(output.parent.is_dir() and not output.parent.is_symlink(), "R01 output parent must exist")
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print("R01 results Passed: " + str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
