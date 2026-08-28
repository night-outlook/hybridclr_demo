"""Independent acceptance checks for the M03 transaction evidence.

The Player JSON is an observation index, never a source of truth.  This module
re-reads every manifest, compiler snapshot, DLL/PDB and native diagnostic file
and then checks the state-machine invariants for every required real process.
M03 is intentionally unsigned; authenticity remains a later milestone.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import uuid

from shadow_tools import VerificationError, read_json, require, safe_file
from m02_results import (_runtime_abi_hash, _snapshot_hash, _snapshot_linked_hash,
                         _verify_source_pins, _linked_claim_absent)


CANDIDATES = (
    "AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility",
    "AssemblyA.Implementation.Internal", "AssemblyShadowDemo.ContractsConsumer",
    "AssemblyShadowDemo.ExtensibilityConsumer",
)
INTERNAL = CANDIDATES[2]
PROVIDER_ORDER = list(CANDIDATES)
ON_MODES = frozenset(f"T03-{n:02d}" for n in range(1, 16) if n != 9)
REQUIRED_MODES = ON_MODES | {"T03-08-Fallback", "T03-09"}
FULL_PATCHES = frozenset({"P03", "P03-InitializerThrow"})
ERROR_CODES = {
    "Success": 0, "FeatureDisabled": 1, "InvalidState": 2,
    "InvalidArgument": 3, "CandidateNotRegistered": 4,
    "DuplicateAssemblyName": 5, "BaselineAssemblyNotFound": 6,
    "BaselineBuildMismatch": 7, "AssemblyNameMismatch": 8,
    "BadImage": 9, "UnsupportedAssembly": 10,
    "ClosureMemberMissing": 11, "UnexpectedClosureMember": 12,
    "ReferenceResolutionFailed": 13, "ReferenceEscapesClosure": 14,
    "BaselineAlreadyUsed": 15, "ResourceAbiMismatch": 16,
    "RuntimeAbiMismatch": 17, "AlreadyCommitted": 18,
    "ModuleInitializerFailed": 19, "InternalError": 20,
}
STATE_CODES = {
    "Disabled": 0, "CandidatesRegistered": 1, "Staging": 2,
    "Staged": 3, "Validated": 4, "Committing": 5,
    "Committed": 6, "Aborted": 7, "Failed": 8,
    "FailedAfterCommit": 9,
}
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
GUID_RE = re.compile(r"[0-9a-f]{32}\Z")
SUCCESS_MODES = {"T03-01", "T03-02", "T03-07", "T03-12", "T03-13", "T03-14"}
ABORT_MODES = {"T03-03", "T03-04", "T03-05", "T03-10", "T03-11", "T03-15"}
SHUFFLED_MODES = {"T03-02", "T03-07", "T03-12"}


def digest(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), f"Cannot hash missing or symlinked file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _obj(path):
    value = read_json(path)
    require(isinstance(value, dict), f"{path}: JSON root must be an object")
    return value


def _s(value, path, field):
    require(isinstance(value, str) and value.strip(), f"{path}: {field} must be a non-empty string")
    return value


def _hash(value, path, field):
    require(isinstance(value, str) and HASH_RE.fullmatch(value) is not None,
            f"{path}: {field} must be a lowercase SHA-256")
    return value


def _guid(value, path, field):
    value = _s(value, path, field).replace("-", "").lower()
    require(GUID_RE.fullmatch(value) is not None, f"{path}: {field} must be a 32-hex build GUID")
    return value


def _absolute(value, path, field, directory=False):
    result = Path(_s(value, path, field))
    require(result.is_absolute(), f"{path}: {field} must be absolute")
    require(not result.is_symlink(), f"{path}: {field} is symlinked")
    require(result.is_dir() if directory else result.is_file(), f"{path}: {field} is missing: {result}")
    for parent in (result, *result.parents):
        require(not parent.is_symlink(), f"{path}: {field} has symlinked component: {parent}")
    return result


def _rel(root: Path, value, path, field):
    value = _s(value, path, field)
    require(not Path(value).is_absolute() and "\\" not in value, f"{path}: {field} must be relative POSIX")
    try:
        result = safe_file(root, value)
    except VerificationError as error:
        raise VerificationError(f"{path}.{field}: {error}") from error
    require(result.is_file() and not result.is_symlink(), f"{path}: missing {field}: {result}")
    return result


def _same(a, b):
    return json.dumps(a, sort_keys=True, ensure_ascii=False, separators=(",", ":")) == json.dumps(
        b, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _names(values, path, field):
    require(isinstance(values, list), f"{path}: {field} must be an array")
    result = []
    for index, value in enumerate(values):
        item_path = f"{path}.{field}[{index}]"
        _s(value, item_path, "name")
        result.append(value)
    require(len(result) == len({name.casefold() for name in result}), f"{path}: duplicate names in {field}")
    return result


def _exact(actual, expected, path, field):
    require(isinstance(actual, (list, tuple)) and list(actual) == list(expected),
            f"{path}: {field} differs; expected {expected!r}, got {actual!r}")


def _fold(values):
    return [value.casefold() for value in values]


def _name_order(actual, expected, path, field):
    require(_fold(_names(actual, path, field)) == _fold(expected), f"{path}: {field} differs from provider order")


def _name_set(actual, expected, path, field):
    require(set(_fold(_names(actual, path, field))) == set(_fold(expected)), f"{path}: {field} exact set differs")


def _integer(value, path, field, minimum=0):
    require(type(value) is int and value >= minimum, f"{path}: {field} must be an integer >= {minimum}")
    return value


def _verify_snapshot(root: Path, expected_build_id: str, expected_abi: str, baseline: dict, path: Path,
                     bind_baseline: bool = True):
    receipt_path = root / "assembly-snapshot.json"
    receipt = _obj(receipt_path)
    _guid(receipt.get("buildGuid"), receipt_path, "buildGuid")
    require(receipt.get("schemaVersion") == 1 and receipt.get("kind") == "PlayerBuildInputs",
            f"{receipt_path}: M03 baseline needs a real PlayerBuildInputs snapshot")
    require(receipt.get("buildId") == expected_build_id and receipt.get("unityVersion") == baseline.get("unityVersion") and
            receipt.get("target") == baseline.get("target") == "StandaloneOSX" and
            receipt.get("architecture") == baseline.get("architecture"),
            f"{receipt_path}: Player identity differs from M03 baseline")
    require(receipt.get("playerBuildSucceeded") is True and receipt.get("playerBuildFilterCaptured") is True,
            f"{receipt_path}: snapshot is not a successful filtered Player capture")
    _verify_source_pins(receipt.get("sourcePins"), receipt_path, baseline.get("sourcePins"))
    require(_runtime_abi_hash(receipt["sourcePins"], receipt_path) == expected_abi,
            f"{receipt_path}: source pins do not reproduce runtimeAbiHash")
    _hash(receipt.get("nativeLibrarySha256"), receipt_path, "nativeLibrarySha256")
    native = _absolute(receipt.get("nativeLibraryPath"), receipt_path, "nativeLibraryPath")
    require(digest(native) == receipt["nativeLibrarySha256"], f"{native}: native Player hash differs")
    require(receipt.get("snapshotHash") == _snapshot_hash(receipt, root, receipt_path),
            f"{receipt_path}: snapshotHash is stale or self-reported")
    # linked-player evidence is the actual native/managed load boundary.
    linked_path = root / "LinkedPlayer" / "linked-player-receipt.json"
    linked = _obj(linked_path)
    require(_same(receipt.get("linkedPlayerReceipt"), linked),
            f"{receipt_path}: embedded linked Player receipt differs from on-disk receipt")
    require(linked.get("buildGuid") == receipt.get("buildGuid") and
            linked.get("nativeLibrarySha256") == receipt.get("nativeLibrarySha256") and
            linked.get("target") == receipt.get("target") and linked.get("architecture") == receipt.get("architecture"),
            f"{linked_path}: linked Player identity differs")
    _hash(linked.get("nativeLibrarySha256"), linked_path, "nativeLibrarySha256")
    require(receipt.get("linkedPlayerReceiptHash") == _snapshot_linked_hash(linked),
            f"{linked_path}: linkedPlayerReceiptHash is stale")
    require(isinstance(linked.get("assemblies"), list) and linked["assemblies"], f"{linked_path}: linked assemblies missing")
    linked_names = {str(item.get("name", "")).lower() for item in linked["assemblies"] if isinstance(item, dict)}
    require(len(linked_names) == len(linked["assemblies"]), f"{linked_path}: duplicate linked assembly identities")
    require({name.lower() for name in CANDIDATES}.issubset(linked_names),
            f"{linked_path}: linked Player omitted an M03 candidate assembly")
    for index, entry in enumerate(linked["assemblies"]):
        item_path = f"{linked_path}.assemblies[{index}]"
        require(isinstance(entry, dict), f"{item_path}: entry must be object")
        name = _s(entry.get("name"), item_path, "name")
        require(entry.get("path") == f"Assemblies/{name}.dll", f"{item_path}: noncanonical linked path")
        _hash(entry.get("sha256"), item_path, "sha256")
        dll = _rel(root / "LinkedPlayer", entry["path"], item_path, "path")
        require(digest(dll) == entry["sha256"], f"{item_path}: linked DLL hash differs")
    if bind_baseline:
        _hash(baseline.get("playerInputSnapshotHash"), path, "playerInputSnapshotHash")
        require(baseline.get("playerInputSnapshotHash") == receipt.get("snapshotHash"),
                f"{path}: baseline input snapshot hash differs from actual receipt")
        require(baseline.get("nativeLibrarySha256") == receipt.get("nativeLibrarySha256"),
                f"{path}: baseline native hash differs from actual Player")
    return receipt


def _verify_inputs(manifest_path: Path, baseline_manifest_path: Path | None, baseline_snapshot_path: Path | None):
    manifest = _obj(manifest_path)
    require(manifest.get("schemaVersion") == 1 and manifest.get("milestone") == "M03",
            f"{manifest_path}: M03FixtureManifest schema/milestone mismatch")
    _s(manifest.get("baselineBuildId"), manifest_path, "baselineBuildId")
    require(manifest["baselineBuildId"].startswith("M03-Baseline-"),
            f"{manifest_path}: M03 must use a new M03 baseline, not an M02/M01 baseline")
    abi = _hash(manifest.get("runtimeAbiHash"), manifest_path, "runtimeAbiHash")
    require(manifest.get("target") == "StandaloneOSX" and manifest.get("architecture") == "arm64",
            f"{manifest_path}: M03 acceptance is pinned to StandaloneOSX arm64")
    _name_order(manifest.get("candidateNames"), CANDIDATES, manifest_path, "candidateNames")
    _name_order(manifest.get("closureLoadOrder"), PROVIDER_ORDER, manifest_path, "closureLoadOrder")
    stable = _names(manifest.get("stableAotNames"), manifest_path, "stableAotNames")
    require(stable and stable == sorted(stable) and not set(_fold(stable)) & set(_fold(CANDIDATES)),
            f"{manifest_path}: stableAotNames must be sorted, non-empty and exclude candidates")
    _hash(manifest.get("stableAotProvenanceHash"), manifest_path, "stableAotProvenanceHash")
    provenance = _s(manifest.get("stableAotProvenance"), manifest_path, "stableAotProvenance")
    require(manifest["stableAotProvenanceHash"] == hashlib.sha256(("m03-stable-aot:1\n" + provenance).encode()).hexdigest(),
            f"{manifest_path}: stable AOT provenance hash is stale")
    baseline_path = baseline_manifest_path or _absolute(manifest.get("baselineManifestPath"), manifest_path, "baselineManifestPath")
    baseline_path = _absolute(str(baseline_path), manifest_path, "baselineManifestPath")
    require(digest(baseline_path) == manifest.get("baselineManifestSha256"), f"{baseline_path}: baseline manifest hash differs")
    baseline = _obj(baseline_path)
    require(baseline.get("schemaVersion") == 1 and baseline.get("semanticHashSchema") == 1,
            f"{baseline_path}: baseline manifest schema mismatch")
    for field in ("baselineBuildId", "runtimeAbiHash", "unityVersion", "target", "architecture"):
        require(baseline.get(field) == manifest.get(field), f"{baseline_path}: {field} differs from fixture manifest")
    _verify_source_pins(baseline.get("sourcePins"), baseline_path)
    _name_set(baseline.get("shadowCandidates"), CANDIDATES, baseline_path, "shadowCandidates")
    for field in ("bootstrapAbiHash", "resourceAbiHash"):
        _hash(baseline.get(field), baseline_path, field)
    require(_runtime_abi_hash(baseline["sourcePins"], baseline_path) == abi, f"{baseline_path}: runtime ABI mismatch")
    snapshot_value = baseline_snapshot_path or manifest.get("baselineInputSnapshot")
    snapshot_root = _absolute(str(snapshot_value), manifest_path, "baselineInputSnapshot", directory=True)
    require(manifest.get("baselineInputSnapshotHash") == baseline.get("playerInputSnapshotHash"),
            f"{manifest_path}: baseline snapshot hash binding differs")
    receipt = _verify_snapshot(snapshot_root, manifest["baselineBuildId"], abi, baseline, manifest_path)
    require(receipt.get("buildGuid") == baseline.get("playerBuildGuid"), f"{snapshot_root}: buildGuid differs")
    linked_names = {a["name"].casefold() for a in receipt["linkedPlayerReceipt"]["assemblies"]}
    require(set(_fold(stable)) <= linked_names, f"{manifest_path}: stable AOT allowlist contains an unlinked assembly")
    provenance_lines = provenance.split("\n")
    require(len(provenance_lines) == 4 and provenance_lines[0].startswith("framework=") and
            HASH_RE.fullmatch(provenance_lines[0][10:]) and
            provenance_lines[1] == "linked-player=" + receipt["linkedPlayerReceiptHash"] and
            provenance_lines[2] == "bootstrap-policy=" + ",".join(sorted(_fold(_names(baseline.get("bootstrapAssemblies"), baseline_path, "bootstrapAssemblies")))) and
            provenance_lines[3] == "physical=" + ",".join(stable),
            f"{manifest_path}: stable AOT provenance does not bind linked Player/bootstrap/names")
    require(isinstance(manifest.get("fixtures"), list) and len(manifest["fixtures"]) == 3,
            f"{manifest_path}: M03 manifest must contain exactly three fixtures")
    fixture_by_id = {}
    for index, fixture in enumerate(manifest["fixtures"]):
        fp = f"{manifest_path}.fixtures[{index}]"
        require(isinstance(fixture, dict), f"{fp}: fixture must be object")
        patch_id = _s(fixture.get("patchId"), fp, "patchId")
        require(patch_id in {"P01", "P03", "P03-InitializerThrow"} and patch_id not in fixture_by_id,
                f"{fp}: duplicate or unknown patchId")
        patch_root = _absolute(fixture.get("patchDirectory"), fp, "patchDirectory", directory=True)
        patch_path = _absolute(fixture.get("patchManifest"), fp, "patchManifest")
        require(patch_path.parent == patch_root, f"{fp}: patch manifest is outside patchDirectory")
        require(digest(patch_path) == fixture.get("patchManifestSha256"), f"{patch_path}: manifest hash differs")
        compile_root = _absolute(fixture.get("compileSnapshot"), fp, "compileSnapshot", directory=True)
        compile_receipt_path = compile_root / "assembly-snapshot.json"
        compile_receipt = _obj(compile_receipt_path)
        require(compile_receipt.get("schemaVersion") == 1 and compile_receipt.get("kind") == "CompilePlayerScripts" and compile_receipt.get("snapshotHash") == fixture.get("compileSnapshotHash"),
                f"{compile_receipt_path}: compiler snapshot identity differs")
        require(_linked_claim_absent(compile_receipt) and not (compile_root / "LinkedPlayer").exists(),
                f"{compile_receipt_path}: compiler snapshot must not claim linked Player evidence")
        _verify_source_pins(compile_receipt.get("sourcePins"), compile_receipt_path, baseline.get("sourcePins"))
        require(compile_receipt.get("unityVersion") == manifest.get("unityVersion") and compile_receipt.get("target") == manifest.get("target") and
                compile_receipt.get("architecture") == manifest.get("architecture"), f"{compile_receipt_path}: target identity differs")
        require(compile_receipt.get("snapshotHash") == _snapshot_hash(compile_receipt, compile_root, compile_receipt_path),
                f"{compile_receipt_path}: snapshotHash is stale")
        expected_defines = {"ASSEMBLY_SHADOW_M03_INITIALIZERS", "ASSEMBLY_SHADOW_P01"}
        if patch_id != "P01":
            expected_defines.update({"ASSEMBLY_SHADOW_M03_P03", "ASSEMBLY_SHADOW_P03"})
        if patch_id == "P03-InitializerThrow":
            expected_defines.add("ASSEMBLY_SHADOW_M03_INITIALIZER_THROW")
        declared = _names(fixture.get("defines"), fp, "defines")
        compiled = _names(compile_receipt.get("extraScriptingDefines"), compile_receipt_path, "extraScriptingDefines")
        require(set(declared) == expected_defines and {d for d in compiled if not d.startswith("ASSEMBLY_SHADOW_REFLECTION_BINDINGS_")} == expected_defines,
                f"{compile_receipt_path}: actual compiler initializer/marker defines differ")
        fixture_by_id[patch_id] = (fixture, patch_root, patch_path, compile_root, compile_receipt)
    require(set(fixture_by_id) == {"P01", "P03", "P03-InitializerThrow"}, f"{manifest_path}: fixture set is incomplete")
    manifest["_path"] = str(manifest_path)
    manifest["_snapshot"] = receipt
    return manifest, baseline, snapshot_root, fixture_by_id


def _verify_player_build_receipt(path: Path, manifest: dict, baseline: dict, variant: str):
    """Verify the build-side binding, including the exact native compiler switch."""
    path = _absolute(str(path), path, "playerBuildReceipt")
    receipt = _obj(path)
    require(receipt.get("schemaVersion") == 1 and receipt.get("milestone") == "M03" and
            receipt.get("variant") == variant, f"{path}: M03 Player build receipt schema/variant mismatch")
    for field in ("baselineBuildId", "runtimeAbiHash", "unityVersion", "target", "architecture", "buildGuid",
                  "playerOutput", "inputSnapshot", "inputSnapshotHash", "nativeLibraryPath", "nativeLibrarySha256", "nativeArguments"):
        _s(receipt.get(field), path, field)
    require(receipt.get("baselineBuildId") == manifest["baselineBuildId"] and receipt.get("runtimeAbiHash") == manifest["runtimeAbiHash"] and
            receipt.get("unityVersion") == manifest["unityVersion"] and receipt.get("target") == manifest["target"] and
            receipt.get("architecture") == manifest["architecture"], f"{path}: Player build identity differs from fixture manifest")
    expected_arg = '--compiler-flags="-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=' + ("1" if variant == "NativeOn" else "0") + '"'
    require(receipt.get("nativeArguments") == expected_arg, f"{path}: native compiler feature switch differs from receipt variant")
    snapshot_root = _absolute(receipt["inputSnapshot"], path, "inputSnapshot", directory=True)
    require(snapshot_root.resolve() == path.parent.resolve(), f"{path}: inputSnapshot must be the receipt directory")
    require(receipt.get("inputSnapshotHash") == baseline.get("playerInputSnapshotHash") if variant == "NativeOn" else
            isinstance(receipt.get("inputSnapshotHash"), str), f"{path}: inputSnapshotHash binding is invalid")
    native = _absolute(receipt["nativeLibraryPath"], path, "nativeLibraryPath")
    _hash(receipt.get("nativeLibrarySha256"), path, "nativeLibrarySha256")
    _guid(receipt.get("buildGuid"), path, "buildGuid")
    require(digest(native) == receipt["nativeLibrarySha256"], f"{path}: actual native library hash differs")
    receipt_snapshot = _verify_snapshot(snapshot_root, manifest["baselineBuildId"], manifest["runtimeAbiHash"], baseline, path,
                                        bind_baseline=variant == "NativeOn")
    require(receipt_snapshot.get("snapshotHash") == receipt.get("inputSnapshotHash"), f"{path}: inputSnapshotHash differs from assembly snapshot")
    require(receipt_snapshot.get("nativeLibrarySha256") == receipt.get("nativeLibrarySha256"), f"{path}: native hash differs from assembly snapshot")
    require(_guid(receipt.get("buildGuid"), path, "buildGuid") == _guid(receipt_snapshot.get("buildGuid"), path, "snapshot.buildGuid"),
            f"{path}: buildGuid differs from actual assembly snapshot")
    require(receipt["nativeLibraryPath"] == receipt_snapshot.get("nativeLibraryPath") and receipt["playerOutput"] == receipt_snapshot.get("playerOutput"),
            f"{path}: Player/native paths differ from actual assembly snapshot")
    _absolute(receipt["playerOutput"], path, "playerOutput", directory=True)
    return receipt


def _verify_patch(patch_id, item, manifest, baseline):
    fixture, patch_root, patch_path, compile_root, compile = item
    patch = _obj(patch_path)
    sidecar = patch_root / "manifest.sha256"
    require(sidecar.is_file() and not sidecar.is_symlink() and sidecar.read_text(encoding="utf-8").strip() == digest(patch_path),
            f"{sidecar}: patch manifest SHA sidecar is missing or stale")
    require(patch.get("schemaVersion") == 1 and patch.get("semanticHashSchema") == 1 and patch.get("patchId") == patch_id,
            f"{patch_path}: patch schema or identity mismatch")
    for field in ("baselineBuildId", "baselineManifestSha256", "runtimeAbiHash", "unityVersion", "target", "architecture"):
        require(patch.get(field) == manifest.get(field),
                f"{patch_path}: {field} differs from M03 input binding")
    require(patch.get("compileSnapshotHash") == compile.get("snapshotHash") == fixture.get("compileSnapshotHash"),
            f"{patch_path}: compiler snapshot binding differs")
    _verify_source_pins(patch.get("sourcePins"), patch_path, baseline.get("sourcePins"))
    require(_runtime_abi_hash(patch["sourcePins"], patch_path) == manifest.get("runtimeAbiHash"),
            f"{patch_path}: patch source pins do not reproduce runtime ABI")
    require(patch.get("dllOnly") is True and patch.get("unsigned") is True and patch.get("signatureAlgorithm") == "None",
            f"{patch_path}: M03 patch must be unsigned DLL-only")
    expected = [INTERNAL] if patch_id == "P01" else PROVIDER_ORDER
    _name_set(patch.get("changedRoots"), fixture.get("changedRoots", []), patch_path, "changedRoots")
    _name_order(patch.get("loadOrder"), expected, patch_path, "loadOrder")
    closure = patch.get("closure")
    require(isinstance(closure, list) and all(isinstance(x, dict) for x in closure), f"{patch_path}: closure must be an object array")
    _name_set([x.get("name") for x in closure], expected, patch_path, "closure")
    _name_order(fixture.get("closureLoadOrder"), expected, patch_path, "fixture closureLoadOrder")
    _name_order(fixture.get("stableAotNames"), manifest.get("stableAotNames"), patch_path, "fixture stableAotNames")
    by_compile = {x["name"].casefold(): x for x in compile.get("assemblies", []) if isinstance(x, dict)}
    baseline_by_name = {x["name"].casefold(): x for x in baseline.get("assemblies", []) if isinstance(x, dict)}
    for index, entry in enumerate(closure):
        ep = f"{patch_path}.closure[{index}]"
        require(isinstance(entry, dict) and entry.get("name", "").casefold() in _fold(expected), f"{ep}: invalid closure entry")
        name = entry["name"]
        source = by_compile.get(name.casefold())
        require(source is not None, f"{ep}: assembly absent from compiler snapshot")
        dll = _rel(patch_root, entry.get("dll"), ep, "dll")
        _hash(entry.get("sha256"), ep, "sha256")
        require(digest(dll) == entry["sha256"] == source.get("sha256"), f"{ep}: DLL hash differs from bytes/snapshot")
        try:
            parsed_mvid = uuid.UUID(_s(entry.get("mvid"), ep, "mvid"))
            parsed_baseline_mvid = uuid.UUID(_s(entry.get("baselineMvid"), ep, "baselineMvid"))
        except (ValueError, AttributeError) as error:
            raise VerificationError(f"{ep}: invalid assembly MVID evidence") from error
        require(parsed_mvid.int != 0 and parsed_baseline_mvid.int != 0 and
                baseline_by_name.get(name.casefold(), {}).get("mvid") == entry.get("baselineMvid"),
                f"{ep}: MVID baseline identity is missing or stale")
        pdb = entry.get("pdb")
        require(pdb and source.get("pdbPath"), f"{ep}: M03 requires compiler PDB evidence")
        pdb_file = _rel(patch_root, pdb, ep, "pdb")
        source_pdb = _rel(compile_root, source["pdbPath"], ep, "compilePdbPath")
        _hash(entry.get("pdbSha256"), ep, "pdbSha256")
        require(digest(pdb_file) == entry["pdbSha256"] == source.get("pdbSha256") == digest(source_pdb),
                f"{ep}: PDB hash differs from bytes/snapshot")
    for field, baseline_field in (("bootstrapAbiHash", "bootstrapAbiHash"), ("resourceAbiHash", "resourceAbiHash"), ("baselineResourceAbiHash", "resourceAbiHash")):
        require(_hash(patch.get(field), patch_path, field) == baseline.get(baseline_field), f"{patch_path}: {field} changed")
    expected_dlls = {(patch_root / entry["dll"]).resolve() for entry in closure}
    require(expected_dlls == {p.resolve() for p in patch_root.rglob("*.dll")}, f"{patch_path}: undeclared or missing patch DLL")
    return patch


def _diag(value, path):
    require(isinstance(value, dict), f"{path}: diagnostics must be object")
    require(value.get("schemaVersion") == 1 and value.get("runtimeAbiVersion") == 1,
            f"{path}: native diagnostics schema mismatch")
    require(isinstance(value.get("assemblies"), list) and isinstance(value.get("events"), list) and
            isinstance(value.get("ordinaryAssemblies"), list) and isinstance(value.get("ordinaryClasses"), list) and
            isinstance(value.get("baselineUses"), list), f"{path}: diagnostics arrays are incomplete")
    state = value.get("state")
    require(state in STATE_CODES and type(value.get("stateCode")) is int and value.get("stateCode") == STATE_CODES[state], f"{path}: state enum/code mismatch")
    return value


def _verify_diag_invariants(diagnostics, expected, stable, path, final=False, patch=None):
    d = _diag(diagnostics, path)
    require(d.get("enabled") is True, f"{path}: native ON diagnostic is disabled")
    require(type(d.get("lastError")) is int and 0 <= d["lastError"] <= 20, f"{path}: native lastError code is invalid")
    _name_order(d.get("closureLoadOrder"), expected, path, "diagnostic closureLoadOrder")
    _name_order(d.get("stableAotNames"), stable, path, "diagnostic stableAotNames")
    require(_integer(d.get("expected"), path, "expected") == len(expected), f"{path}: diagnostic expected count is not actual")
    require(all(isinstance(a, dict) for a in d["assemblies"]), f"{path}: assembly diagnostic must be an object")
    _name_order([a.get("name") for a in d["assemblies"]], expected, path, "diagnostic assemblies")
    for assembly in d["assemblies"]:
        for field in ("skeletonBuilt", "runtimeMetadataInitialized", "published", "moduleInitializerAttempted", "moduleInitializerRan"):
            require(type(assembly.get(field)) is bool, f"{path}: assembly {field} is not a Boolean")
        if assembly["skeletonBuilt"] and patch is not None:
            entry = next(a for a in patch["closure"] if a["name"].casefold() == assembly["name"].casefold())
            require(_guid(assembly.get("mvid"), path, "diagnostic assembly mvid") == _guid(entry["mvid"], path, "patch mvid"),
                    f"{path}: diagnostic assembly MVID differs from patch")
        if not assembly["skeletonBuilt"]:
            require(not any(assembly[field] for field in ("runtimeMetadataInitialized", "published", "moduleInitializerAttempted", "moduleInitializerRan")),
                    f"{path}: absent skeleton has initialized metadata")
        require(not assembly["published"] or assembly["runtimeMetadataInitialized"], f"{path}: published assembly lacks initialized metadata")
        require(not assembly["moduleInitializerRan"] or assembly["moduleInitializerAttempted"], f"{path}: initializer ran without attempt")
    staged = _integer(d.get("staged"), path, "staged")
    require(staged == sum(a["skeletonBuilt"] for a in d["assemblies"]), f"{path}: staged count is not actual")
    retained = _integer(d.get("retainedBytes"), path, "retainedBytes")
    require((retained > 0) == (staged > 0), f"{path}: retained bytes disagree with staged images")
    if any(a.get("runtimeMetadataInitialized") for a in d["assemblies"]):
        require(len(d["assemblies"]) == len(expected) and all(a.get("skeletonBuilt") for a in d["assemblies"]),
                f"{path}: metadata initialized before complete skeleton closure")
    for field in ("generation", "enumerationGeneration", "classEnumerationGeneration"):
        require(_integer(d.get(field), path, field) in (0, 1), f"{path}: {field} must be generation zero or one")
    require(d["generation"] <= d["enumerationGeneration"] <= d["classEnumerationGeneration"], f"{path}: enumeration generation is incoherent")
    if d["state"] in {"Disabled", "CandidatesRegistered", "Staging", "Staged", "Validated", "Aborted", "Failed"}:
        require(d["generation"] == 0, f"{path}: prepublication state has active generation")
    elif d["state"] in {"Committing", "Committed", "FailedAfterCommit"}:
        require(d["generation"] == 1 and staged == len(expected) and expected, f"{path}: publication state lacks complete active closure")
    published = any(a.get("published") for a in d["assemblies"])
    if d["generation"] == 0:
        require(not published and not any(a.get("moduleInitializerAttempted") or a.get("moduleInitializerRan") for a in d["assemblies"]),
                f"{path}: private generation contains publication or initializer")
    if d["generation"] == 1:
        require(published and d.get("enumerationGeneration") == 1,
                f"{path}: publication must be one atomic generation")
        require(all(a.get("published") for a in d["assemblies"]), f"{path}: partial publication")
    order = _names(d.get("commitOrder"), path, "commitOrder")
    require(_fold(order) == _fold(expected[:len(order)]), f"{path}: commitOrder is not a provider-order prefix")
    require(not order or d["generation"] == 1, f"{path}: private generation has completed initializers")
    for name in order:
        require(next(a for a in d["assemblies"] if a["name"].casefold() == name.casefold())["moduleInitializerRan"],
                f"{path}: commitOrder claims an initializer that did not run")
    if d["state"] in {"Committing", "FailedAfterCommit"}:
        require(not any(a["moduleInitializerAttempted"] or a["moduleInitializerRan"] for a in d["assemblies"][len(order) + 1:]),
                f"{path}: initializer flags skipped beyond the current provider-order member")
    if d["state"] == "Committed":
        require(len(order) == len(expected) and all(a["moduleInitializerRan"] for a in d["assemblies"]), f"{path}: Committed state has incomplete initializer order")
    for index, klass in enumerate(d["ordinaryClasses"]):
        require(isinstance(klass, dict), f"{path}.ordinaryClasses[{index}]: invalid class row")
        for field in ("assemblyName", "typeName"):
            _s(klass.get(field), path, "ordinaryClasses." + field)
        for field in ("isInterpreter", "isConstructedGeneric", "usesStagedMetadata"):
            require(type(klass.get(field)) is bool, f"{path}.ordinaryClasses[{index}]: {field} evidence is missing")
    if d.get("classEnumerationGeneration") == 0:
        require(not any(c["usesStagedMetadata"] for c in d["ordinaryClasses"]), f"{path}: private staged class leaked")
    if final:
        require(d.get("classEnumerationGeneration") == 1, f"{path}: committed class registry did not publish generation 1")
        require(any(c.get("isConstructedGeneric") is True and c.get("usesStagedMetadata") is True and
                    "M03Pair" in str(c.get("typeName", "")) for c in d["ordinaryClasses"]),
                f"{path}: constructed M03Pair class is absent from committed enumeration")
        require(any(c.get("isConstructedGeneric") is True and c.get("usesStagedMetadata") is True and
                    "Nullable`1" in str(c.get("typeName", "")) and c.get("isInterpreter") is False
                    for c in d["ordinaryClasses"]),
                f"{path}: constructed AOT Nullable class is absent from committed enumeration")
    ordinary = d["ordinaryAssemblies"]
    require(all(isinstance(a, dict) and isinstance(a.get("name"), str) and type(a.get("isInterpreter")) is bool for a in ordinary), f"{path}: malformed ordinary assembly row")
    for name in CANDIDATES:
        rows = [x for x in ordinary if x["name"].casefold() == name.casefold()]
        require(sum(not x.get("isInterpreter") for x in rows) == 1, f"{path}: physical ordinary row missing/duplicated: {name}")
        shadow = 1 if d.get("enumerationGeneration") == 1 and name.casefold() in _fold(expected) else 0
        require(sum(bool(x.get("isInterpreter")) for x in rows) == shadow, f"{path}: partial ordinary publication: {name}")
    for event in d["events"]:
        require(isinstance(event, dict), f"{path}: invalid diagnostic event")
        _integer(event.get("sequence"), path, "event.sequence", 1)
        _integer(event.get("stagedCount"), path, "event.stagedCount")
        require(type(event.get("generation")) is int and event["generation"] in (0, 1) and event["generation"] <= d["generation"], f"{path}: diagnostic event generation invalid")
        if event.get("kind") == "metadata-begin":
            require(event.get("stagedCount") == len(expected), f"{path}: metadata began before complete skeleton closure")
    sequences = [event.get("sequence") for event in d["events"]]
    require(sequences == sorted(sequences) and len(sequences) == len(set(sequences)), f"{path}: diagnostic event sequence regressed/duplicated")
    return d


def _checks(result, expected_codes, path):
    checks = result.get("checks")
    require(isinstance(checks, list) and checks, f"{path}: checks are missing")
    seen = set()
    for index, check in enumerate(checks):
        cp = f"{path}.checks[{index}]"
        require(isinstance(check, dict), f"{cp}: check must be object")
        operation = _s(check.get("operation"), cp, "operation")
        require(operation not in seen, f"{cp}: duplicate operation")
        require(operation in expected_codes, f"{cp}: unknown operation for mode: {operation}")
        seen.add(operation)
        require(check.get("actual") == check.get("expected") and check.get("actualCode") == check.get("expectedCode"),
                f"{cp}: self-reported check is not green")
        require(type(check.get("actualCode")) is int and type(check.get("expectedCode")) is int, f"{cp}: error codes must be integers")
        require(check.get("actual") in ERROR_CODES and check.get("actualCode") == ERROR_CODES[check["actual"]] and
                check.get("expected") in ERROR_CODES and check.get("expectedCode") == ERROR_CODES[check["expected"]],
                f"{cp}: check code/name is not the AssemblyShadow ABI")
        if operation in expected_codes:
            code = expected_codes[operation]
            require(check.get("actual") == code and check.get("actualCode") == ERROR_CODES[code],
                    f"{cp}: {operation} reports wrong native code")
    for operation in expected_codes:
        require(operation in seen, f"{path}: required check is absent: {operation}")


def _load_diagnostics(result, path):
    native_path = _absolute(result.get("nativeDiagnosticsPath"), path, "nativeDiagnosticsPath")
    native_hash = _hash(result.get("nativeDiagnosticsSha256"), path, "nativeDiagnosticsSha256")
    require(digest(native_path) == native_hash, f"{native_path}: diagnostics SHA differs")
    inline = result.get("nativeDiagnosticsJson")
    require(isinstance(inline, str) and inline.strip(), f"{path}: nativeDiagnosticsJson is missing")
    try:
        inline_obj = json.loads(inline)
    except ValueError as error:
        raise VerificationError(f"{path}: invalid nativeDiagnosticsJson: {error}") from error
    disk_obj = _obj(native_path)
    require(_same(inline_obj, disk_obj), f"{path}: inline/native diagnostics differ")
    return _diag(disk_obj, native_path)


def _mode_contract(mode, stages):
    """Exact observations emitted by the C# probe, not self-reported pass flags."""
    points, states, codes = [], [], {}

    def state(point, value):
        states.append((point, value))
        codes["state-" + point] = "Success"

    def snapshot(point):
        points.append(point)
        codes["diagnostics-" + point] = "Success"

    def code(operation, value="Success"):
        codes[operation] = value

    if mode == "T03-08-Fallback":
        state("fallback-initial", "Disabled")
        snapshot("fallback-before-business")
        code("fallback-unregistered-mode", "CandidateNotRegistered")
        state("fallback-after-business", "Disabled")
        snapshot("fallback-after-business")
        return points, states, codes
    state("initial", "Disabled")
    snapshot("initial")
    if mode == "T03-14":
        for op in ("stage-disabled", "validate-disabled", "commit-disabled", "abort-disabled"):
            code(op, "InvalidState")
        code("configure-null", "InvalidArgument")
        state("invalid-configure-unchanged", "Disabled")
    code("configure")
    state("configured", "CandidatesRegistered")
    if mode == "T03-14":
        for op, error in (("configure-again", "InvalidState"), ("abi-mismatch", "RuntimeAbiMismatch"),
                          ("duplicate-closure", "DuplicateAssemblyName"), ("unknown-candidate", "CandidateNotRegistered"),
                          ("empty-closure", "InvalidArgument"), ("null-mode", "InvalidArgument"),
                          ("unknown-mode", "CandidateNotRegistered")):
            code(op, error)
        state("begin-errors-unchanged", "CandidatesRegistered")
        snapshot("begin-errors-no-images")
    code("begin", "BaselineBuildMismatch" if mode == "T03-06" else "Success")
    if mode == "T03-06":
        state("wrong-baseline", "CandidatesRegistered")
        snapshot("wrong-baseline")
        return points, states, codes
    state("begun", "Staging")
    snapshot("begun")

    def abort():
        code("abort")
        state("aborted", "Aborted")
        snapshot("aborted")
        for op in ("begin-after-abort", "commit-after-abort", "abort-again"):
            code(op, "InvalidState")
        state("aborted-frozen", "Aborted")

    if mode == "T03-04":
        code("extra-candidate", "UnexpectedClosureMember")
        snapshot("extra-rejected")
        abort()
        return points, states, codes
    if mode == "T03-13":
        code("bad-pdb", "BadImage")
        snapshot("bad-pdb-rejected")
        state("bad-pdb-retryable", "Staging")
    if mode == "T03-14":
        for op, error in (("commit-before-validate", "InvalidState"), ("null-dll", "InvalidArgument"), ("bad-dll", "BadImage")):
            code(op, error)
        snapshot("invalid-inputs-no-images")
    for name in stages:
        code("stage-" + name)
        snapshot("staged-" + name)
    state("after-stage", "Staging" if mode == "T03-03" else "Staged")
    if mode == "T03-05":
        snapshot("before-duplicate")
        code("duplicate", "DuplicateAssemblyName")
        snapshot("after-duplicate")
        abort()
        return points, states, codes
    code("validate", "ClosureMemberMissing" if mode == "T03-03" else
         "BaselineAlreadyUsed" if mode in {"T03-10", "T03-11"} else "Success")
    snapshot("after-validate")
    if mode in {"T03-03", "T03-10", "T03-11"}:
        abort()
        return points, states, codes
    state("validated", "Validated")
    if mode == "T03-15":
        abort()
        return points, states, codes
    code("commit", "ModuleInitializerFailed" if mode == "T03-08" else "Success")
    snapshot("after-commit")
    if mode == "T03-08":
        state("initializer-failure", "FailedAfterCommit")
        code("abort-after-failure", "AlreadyCommitted")
        code("commit-after-failure", "AlreadyCommitted")
        state("still-failed-after-commit", "FailedAfterCommit")
    else:
        state("committed", "Committed")
        code("active-execution-mode")
        code("commit-again", "AlreadyCommitted")
        code("abort-after-commit", "AlreadyCommitted")
        state("committed-frozen", "Committed")
    return points, states, codes


def _verify_marker(result, result_path, manifest, patch, fallback):
    path = _absolute(result.get("fallbackMarkerPath"), result_path, "fallbackMarkerPath")
    require(digest(path) == _hash(result.get("fallbackMarkerSha256"), result_path, "fallbackMarkerSha256"),
            f"{path}: fallback marker SHA differs")
    marker = _obj(path)
    bindings = {
        "schemaVersion": 1, "baselineBuildId": manifest["baselineBuildId"], "runtimeAbiHash": manifest["runtimeAbiHash"],
        "baselineManifestSha256": manifest["baselineManifestSha256"], "patchId": "P03-InitializerThrow",
        "patchManifestSha256": result["patchManifestSha256"], "compileSnapshotHash": patch["compileSnapshotHash"],
        "failure": "ModuleInitializerFailed", "state": "FailedAfterCommit", "generation": 1, "businessStarted": False,
    }
    for field, expected in bindings.items():
        require(marker.get(field) == expected, f"{path}: fallback marker {field} binding differs")
    pid = _integer(marker.get("processId"), path, "processId", 1)
    require((pid != result["processId"]) if fallback else (pid == result["processId"]),
            f"{result_path}: fallback marker process identity does not prove the required process boundary")
    return marker


def _verify_snapshots(result, path, manifest, patch, expected, stages, mode):
    points, states, codes = _mode_contract(mode, stages)
    snapshots = result.get("snapshots")
    require(isinstance(snapshots, list) and all(isinstance(s, dict) for s in snapshots), f"{path}: diagnostic snapshots missing")
    require([s.get("point") for s in snapshots] == points, f"{path}: diagnostic snapshot points/order differ from actual mode")
    require(result.get("states") == [f"{point}:{STATE_CODES[state]}:{state}" for point, state in states],
            f"{path}: recorded state transition sequence differs")
    require(result.get("state") == states[-1][1] and result.get("stateCode") == "Success",
            f"{path}: final state/query code differs")
    _checks(result, codes, path)
    by_point, staged_count = {}, 0
    for index, snapshot in enumerate(snapshots):
        point = snapshot["point"]
        dp = f"{path}.snapshots[{index}]({point})"
        initial = point == "initial" or point.startswith("fallback-")
        prebegin = initial or point in {"begin-errors-no-images", "wrong-baseline"}
        d = _verify_diag_invariants(snapshot.get("diagnostics"), [] if prebegin else expected,
                                    [] if initial else manifest["stableAotNames"], dp, patch=patch)
        require(d.get("baselineBuildId") == ("" if initial else manifest["baselineBuildId"]) and
                d.get("patchId") == ("" if prebegin else patch["patchId"]), f"{dp}: diagnostic transaction identity differs")
        if point.startswith("staged-"):
            staged_count += 1
        require(d["staged"] == staged_count, f"{dp}: staged count does not follow accepted Stage calls")
        desired = "Disabled" if initial else "CandidatesRegistered" if prebegin else "Staging"
        if point.startswith("staged-") or point in {"before-duplicate", "after-duplicate"}:
            desired = "Staged" if staged_count == len(expected) else "Staging"
        if point == "after-validate":
            desired = "Staging" if mode == "T03-03" else "Staged" if mode in {"T03-10", "T03-11"} else "Validated"
        if point == "aborted":
            desired = "Aborted"
        if point == "after-commit":
            desired = "FailedAfterCommit" if mode == "T03-08" else "Committed"
        require(d["state"] == desired, f"{dp}: native state differs from mode phase")
        if point != "after-commit":
            require(d["generation"] == d["enumerationGeneration"] == d["classEnumerationGeneration"] == 0,
                    f"{dp}: synchronous private phase observed publication")
        if point == "after-validate" and mode not in {"T03-03", "T03-10", "T03-11"}:
            require(all(a["runtimeMetadataInitialized"] for a in d["assemblies"]), f"{dp}: Validate did not initialize full metadata")
            metadata_names = [e.get("name") for e in d["events"] if e.get("kind") == "metadata-begin"]
            _name_order(metadata_names, expected, dp, "metadata-begin events")
        if point == "after-validate" and mode == "T03-03":
            require(not any(a["runtimeMetadataInitialized"] for a in d["assemblies"]), f"{dp}: incomplete closure initialized metadata")
        by_point[point] = d
    if mode == "T03-05":
        before, after = by_point["before-duplicate"], by_point["after-duplicate"]
        require(before["staged"] == after["staged"] and before["retainedBytes"] == after["retainedBytes"] and
                _same(before["assemblies"], after["assemblies"]), f"{path}: duplicate Stage allocated another image")
    if mode in {"T03-10", "T03-11"}:
        uses = by_point["after-validate"]["baselineUses"]
        require(any(isinstance(u, dict) and str(u.get("name", "")).casefold() == INTERNAL.casefold() and
                    isinstance(u.get("kind"), str) and u["kind"] for u in uses), f"{path}: baseline rejection has no actual use record")
    for point, error in (("wrong-baseline", "BaselineBuildMismatch"), ("extra-rejected", "UnexpectedClosureMember"),
                         ("after-duplicate", "DuplicateAssemblyName"), ("bad-pdb-rejected", "BadImage")):
        if point in by_point:
            require(by_point[point]["lastError"] == ERROR_CODES[error], f"{path}: {point} exact native error differs")
    if "after-validate" in by_point:
        require(by_point["after-validate"]["lastError"] == ERROR_CODES[codes["validate"]], f"{path}: validation exact native error differs")
    diag = _load_diagnostics(result, path)
    require(_same(diag, snapshots[-1]["diagnostics"]), f"{path}: native diagnostics do not match final captured snapshot")
    return diag


def verify_case(result_path: Path, fixture_manifest, baseline: dict | None = None, fixtures: dict | None = None,
                stable: list[str] | None = None, mode: str | None = None,
                baseline_manifest_path: Path | None = None, baseline_snapshot_path: Path | None = None):
    """Verify a case's artifact and runtime observations; full suite adds build/replay binding."""
    if isinstance(fixture_manifest, (str, Path)):
        fixture_manifest, baseline, _, fixtures = _verify_inputs(Path(fixture_manifest), baseline_manifest_path, baseline_snapshot_path)
        stable = fixture_manifest["stableAotNames"]
    require(isinstance(fixture_manifest, dict) and isinstance(baseline, dict) and isinstance(fixtures, dict),
            "verify_case requires explicit loaded fixture/baseline inputs or a fixture manifest path")
    result_path = _absolute(str(result_path), result_path, "result")
    result = _obj(result_path)
    mode = mode or result.get("mode")
    require(mode in REQUIRED_MODES and result.get("mode") == mode, f"{result_path}: unknown M03 mode")
    require(result.get("schemaVersion") == 2 and result.get("milestone") == "M03" and result.get("result") == "Passed" and result.get("error") in (None, ""),
            f"{result_path}: result must be a completed schema-2 M03 observation")
    require(result.get("il2cpp") is True and result.get("platform") == "OSXPlayer", f"{result_path}: result is not the pinned real IL2CPP platform")
    for field in ("baselineBuildId", "runtimeAbiHash", "unityVersion"):
        require(result.get(field) == fixture_manifest.get(field), f"{result_path}: Player {field} differs from fixture manifest")
    _integer(result.get("processId"), result_path, "processId", 1)
    _guid(result.get("playerBuildGuid"), result_path, "playerBuildGuid")
    _s(result.get("playerDataPath"), result_path, "playerDataPath")
    build = fixture_manifest.get("_offBuild" if mode == "T03-09" else "_onBuild")
    if build is not None:
        require(_guid(result["playerBuildGuid"], result_path, "playerBuildGuid") == _guid(build["buildGuid"], result_path, "buildGuid"),
                f"{result_path}: result playerBuildGuid differs from actual build receipt")
        require(Path(result["playerDataPath"]) == Path(build["playerOutput"]) / "Contents", f"{result_path}: Player data path differs from actual app")
    if mode == "T03-09":
        require(result.get("patchId") in (None, "") and result.get("state") == "Disabled" and result.get("stateCode") == "FeatureDisabled" and
                result.get("executionModeCode") == "FeatureDisabled" and result.get("executionMode") == "AotBaseline",
                f"{result_path}: native-OFF result must retain Disabled/AotBaseline query outputs")
        diag = _load_diagnostics(result, result_path)
        require(diag.get("enabled") is False and diag.get("lastError") == ERROR_CODES["FeatureDisabled"] and diag.get("state") == "Disabled" and
                diag.get("stateCode") == 0 and all(diag.get(f) == 0 for f in ("generation", "enumerationGeneration", "classEnumerationGeneration", "staged", "retainedBytes", "expected")),
                f"{result_path}: native-OFF diagnostics differ from FeatureDisabled contract")
        require(all(diag.get(f) == [] for f in ("assemblies", "events", "baselineUses", "closureLoadOrder", "stableAotNames", "commitOrder")),
                f"{result_path}: native-OFF transaction residue")
        _checks(result, {op: "FeatureDisabled" for op in ("configure-null", "begin-null-invalid-abi", "stage-null", "validate", "commit", "abort",
                                                        "state", "mode-null", "diagnostics", "configure-valid-off", "stage-empty-off")}, result_path)
        require(result.get("businessStarted") is False and not result.get("stageResults") and not result.get("initializerEvents"),
                f"{result_path}: native-OFF unexpectedly staged or ran business")
        return {"mode": mode, "patchId": None, "nativeEnabled": False}
    manifest_path = Path(fixture_manifest["_path"])
    require(result.get("baselineManifestSha256") == fixture_manifest["baselineManifestSha256"] and result.get("fixtureManifestPath") == str(manifest_path) and
            result.get("fixtureManifestSha256") == digest(manifest_path), f"{result_path}: result baseline/fixture binding is invalid")
    require(result.get("integrityOnlyUnsigned") is True, f"{result_path}: integrity-only declaration missing")
    _name_order(result.get("stableAotNames"), fixture_manifest["stableAotNames"], result_path, "stableAotNames")
    require(result.get("stableAotProvenanceHash") == fixture_manifest["stableAotProvenanceHash"], f"{result_path}: stable AOT provenance binding differs")
    patch_id = "P03-InitializerThrow" if mode in {"T03-08", "T03-08-Fallback"} else "P03" if mode in {"T03-02", "T03-03", "T03-07", "T03-12", "T03-15"} else "P01"
    patch = _verify_patch(patch_id, fixtures[patch_id], fixture_manifest, baseline)
    require(result.get("patchId") == patch_id and result.get("patchManifestPath") == str(fixtures[patch_id][2]) and
            result.get("patchManifestSha256") == digest(fixtures[patch_id][2]) and result.get("compileSnapshotHash") == patch["compileSnapshotHash"],
            f"{result_path}: patch/result identity differs")
    expected = list(CANDIDATES[:3]) if mode == "T03-03" else list(patch["loadOrder"])
    if mode == "T03-08-Fallback":
        _verify_marker(result, result_path, fixture_manifest, patch, True)
        diag = _verify_snapshots(result, result_path, fixture_manifest, patch, [], [], mode)
        require(result.get("fallbackObserved") is True and result.get("businessStarted") is True and result.get("businessMarker") == "BASELINE-INTERNAL" and
                result.get("executionModeCode") == "CandidateNotRegistered" and result.get("executionMode") == "AotBaseline",
                f"{result_path}: fallback lacks actual unregistered baseline business execution")
        require(result.get("stageResults") == [] and result.get("initializerEvents") == [], f"{result_path}: fallback performed a transaction")
        return {"mode": mode, "patchId": patch_id, "nativeEnabled": True}
    _name_order(result.get("expectedClosure"), expected, result_path, "expectedClosure")
    stage_results = result.get("stageResults")
    require(isinstance(stage_results, list) and all(isinstance(s, dict) for s in stage_results), f"{result_path}: stageResults missing")
    stages = _names([s.get("name") for s in stage_results], result_path, "stageResults names")
    wanted_stages = list(CANDIDATES[:2]) if mode == "T03-03" else [] if mode in {"T03-04", "T03-06"} else expected
    _name_set(stages, wanted_stages, result_path, "accepted Stage set")
    if mode in SHUFFLED_MODES:
        require(result.get("stageOrder") == stages and _fold(stages) != _fold(expected) and type(result.get("stageSeed")) is int,
                f"{result_path}: shuffled Stage order is absent or provider-ordered")
    else:
        _name_order(stages, wanted_stages, result_path, "Stage sequence")
    by_name = {a["name"].casefold(): a for a in patch["closure"]}
    for stage in stage_results:
        entry = by_name[stage["name"].casefold()]
        require(stage.get("code") == "Success" and stage.get("dllSha256") == entry["sha256"] and stage.get("pdbSha256") == entry["pdbSha256"],
                f"{result_path}: accepted Stage bytes/hash differ from verified patch")
    diag = _verify_snapshots(result, result_path, fixture_manifest, patch, expected, stages, mode)
    for field in ("initializersAfterStage", "initializersAfterValidate"):
        require(result.get(field) == 0, f"{result_path}: actual initializer ran before publication")
    initializers = result.get("initializerEvents")
    require(isinstance(initializers, list) and all(isinstance(e, dict) for e in initializers), f"{result_path}: initializer events missing")
    init_names = expected if mode in SUCCESS_MODES else expected[:3] if mode == "T03-08" else []
    _name_order([e.get("name") for e in initializers], init_names, result_path, "actual initializer order")
    require(result.get("reentrantQueries") == len(initializers), f"{result_path}: initializer reentrant query count differs")
    require(all(e.get("state") == "Committing" and e.get("generation") == 1 and e.get("stateCode") == e.get("diagnosticsCode") == "Success" for e in initializers),
            f"{result_path}: initializer reentrant state/generation/query error differs")
    if mode in SUCCESS_MODES:
        require(result.get("businessStarted") is True and result.get("businessMarker") == "PATCH-P01-INTERNAL" and
                result.get("stateAfterCommit") == "Committed" and result.get("stateAtValidate") == "Validated" and
                result.get("executionModeCode") == "Success" and result.get("executionMode") == "InterpreterShadow" and diag["lastError"] == 0,
                f"{result_path}: success lacks actual committed shadow business marker/mode")
        if patch_id == "P03":
            _verify_diag_invariants(diag, expected, fixture_manifest["stableAotNames"], result_path, final=True, patch=patch)
    elif mode == "T03-08":
        require(result.get("businessStarted") is False and result.get("businessMarker") in (None, "") and diag["state"] == "FailedAfterCommit" and
                diag["lastError"] == ERROR_CODES["ModuleInitializerFailed"], f"{result_path}: initializer failure was hidden or business executed")
        failed = next(a for a in diag["assemblies"] if a["name"].casefold() == INTERNAL.casefold())
        require(failed["moduleInitializerAttempted"] and not failed["moduleInitializerRan"], f"{result_path}: throwing initializer marked successful")
        _name_order(diag["commitOrder"], expected[:2], result_path, "failed commitOrder")
        _verify_marker(result, result_path, fixture_manifest, patch, False)
    else:
        require(result.get("businessStarted") is False and result.get("businessMarker") in (None, "") and diag["generation"] == 0,
                f"{result_path}: negative mode executed business or published")
    if mode == "T03-10":
        _s(result.get("baselineUseAssemblyLoad"), result_path, "baselineUseAssemblyLoad")
    if mode == "T03-11":
        rows = result.get("managedEnumeration")
        require(isinstance(rows, list) and all(isinstance(a, dict) and type(a.get("isInterpreter")) is bool for a in rows),
                f"{result_path}: actual managed enumeration missing")
        require(any(str(a.get("name", "")).casefold() == INTERNAL.casefold() and not a["isInterpreter"] for a in rows) and
                not any(str(a.get("name", "")).casefold() in _fold(expected) and a["isInterpreter"] for a in rows),
                f"{result_path}: managed enumeration leaked shadow or omitted baseline")
    if mode == "T03-12":
        before = _integer(result.get("stressBefore"), result_path, "stressBefore", 1)
        after = _integer(result.get("stressAfter"), result_path, "stressAfter", 1)
        require(result.get("stressStarted") is True and result.get("stressJoined") is True and result.get("stressErrors") == [] and
                result.get("stressIterations") == before + after, f"{result_path}: bounded stress completion/counts invalid")
        samples = result.get("stressSamples")
        require(isinstance(samples, list) and 2 <= len(samples) <= 32 and all(isinstance(s, dict) for s in samples), f"{result_path}: stress samples missing/unbounded")
        tx, generations = [], []
        for sample in samples:
            generation, enumeration = sample.get("generation"), sample.get("enumerationGeneration")
            require(type(generation) is int and type(enumeration) is int and 0 <= generation <= enumeration <= 1 and
                    sample.get("shadowCount") == (len(expected) if enumeration else 0), f"{result_path}: stress sample proves partial publication")
            tx.append(generation); generations.append(enumeration)
        require(tx == sorted(tx) and generations == sorted(generations) and set(generations) == {0, 1}, f"{result_path}: stress observations do not span monotonic publication")
    return {"mode": mode, "patchId": patch_id, "nativeEnabled": True, "generation": diag["generation"]}


def _verify_replay(path, manifest, baseline, fixtures):
    path = _absolute(str(path), path, "editorReplayReceipt")
    replay = _obj(path)
    require(replay.get("schemaVersion") == 1 and replay.get("milestone") == "M03" and replay.get("result") == "Passed" and
            replay.get("comparisonPolicy") == "compiler-linked-policy-graph-resource-abi:1", f"{path}: Editor replay schema/policy/result differs")
    bindings = {field: manifest[field] for field in ("baselineManifestPath", "baselineManifestSha256", "baselineInputSnapshotHash", "baselineBuildId",
                                                    "runtimeAbiHash", "unityVersion", "target", "architecture", "stableAotProvenanceHash")}
    bindings.update(fixtureManifestPath=manifest["_path"], fixtureManifestSha256=digest(Path(manifest["_path"])),
                    playerBuildGuid=baseline["playerBuildGuid"], nativeLibrarySha256=baseline["nativeLibrarySha256"],
                    linkedPlayerReceiptHash=manifest["_snapshot"]["linkedPlayerReceiptHash"])
    for field, expected in bindings.items():
        require(replay.get(field) == expected, f"{path}: Editor replay {field} binding differs")
    _verify_source_pins(replay.get("validatorSourcePins"), path, baseline["sourcePins"])
    rows = replay.get("fixtures")
    require(isinstance(rows, list) and all(isinstance(f, dict) for f in rows), f"{path}: Editor replay fixtures missing")
    require(len(rows) == 3 and {f.get("patchId") for f in rows} == set(fixtures), f"{path}: Editor replay fixture identities differ")
    for row in rows:
        fixture, _, patch_path, _, _ = fixtures[row["patchId"]]
        patch = _obj(patch_path)
        require(row.get("patchManifestSha256") == digest(patch_path) and row.get("compileSnapshotHash") == fixture["compileSnapshotHash"],
                f"{path}: Editor replay patch/compiler hashes differ")
        _name_set(row.get("changedRoots"), patch["changedRoots"], path, "Editor replay changedRoots")
        _name_set(fixture.get("changedRoots"), patch["changedRoots"], path, "fixture changedRoots")
        _name_order(row.get("closureLoadOrder"), patch["loadOrder"], path, "Editor replay closureLoadOrder")
    return replay


def verify_suite(fixture_manifest_path: Path, result_dir: Path, baseline_manifest_path: Path | None = None,
                 baseline_snapshot_path: Path | None = None, native_off_result_path: Path | None = None,
                 on_build_path: Path | None = None, off_build_path: Path | None = None,
                 editor_replay_path: Path | None = None):
    manifest_path = _absolute(str(fixture_manifest_path), fixture_manifest_path, "fixtureManifest")
    manifest, baseline, snapshot_root, fixtures = _verify_inputs(manifest_path, baseline_manifest_path, baseline_snapshot_path)
    require(on_build_path is not None and off_build_path is not None,
            "M03 acceptance requires explicit NativeOn and NativeOff Player build receipts")
    if on_build_path is not None:
        on_receipt = _verify_player_build_receipt(on_build_path, manifest, baseline, "NativeOn")
        require(Path(on_receipt["inputSnapshot"]).resolve() == snapshot_root.resolve(),
                f"{on_build_path}: NativeOn build receipt does not identify the M03 baseline snapshot")
    if off_build_path is not None:
        off_receipt = _verify_player_build_receipt(off_build_path, manifest, baseline, "NativeOff")
        manifest["_offBuild"] = off_receipt
    if on_build_path is not None:
        manifest["_onBuild"] = on_receipt
    require(Path(on_receipt["inputSnapshot"]).resolve() != Path(off_receipt["inputSnapshot"]).resolve() and
            on_receipt["inputSnapshotHash"] != off_receipt["inputSnapshotHash"] and
            on_receipt["nativeLibrarySha256"] != off_receipt["nativeLibrarySha256"],
            "NativeOn and NativeOff must be distinct actual Player snapshots/libraries")
    for patch_id, item in fixtures.items():
        _verify_patch(patch_id, item, manifest, baseline)
    _verify_replay(editor_replay_path or manifest_path.with_name("m03-editor-replay.json"), manifest, baseline, fixtures)
    result_root = _absolute(str(result_dir), result_dir, "resultDir", directory=True)
    paths = {}
    for path in sorted(result_root.glob("m03-T03-*.json")):
        if path.name.endswith("-native-diagnostics.json"):
            continue
        obj = _obj(path)
        mode = obj.get("mode")
        require(isinstance(mode, str) and mode in REQUIRED_MODES and path.name == "m03-" + mode + ".json",
                f"{path}: unexpected result filename/mode")
        require(mode not in paths, f"{result_root}: duplicate result mode {mode}")
        paths[mode] = path
    if native_off_result_path is not None:
        off = _absolute(str(native_off_result_path), result_dir, "nativeOffResult")
        obj = _obj(off)
        require(obj.get("mode") == "T03-09", f"{off}: native-OFF result mode mismatch")
        require("T03-09" not in paths, f"{result_root}: duplicate T03-09 result")
        paths["T03-09"] = off
    require(set(paths) == REQUIRED_MODES, f"{result_root}: required M03 mode set differs; got {sorted(paths)}")
    results = [verify_case(path, manifest, baseline, fixtures, manifest["stableAotNames"], mode) for mode, path in sorted(paths.items())]
    failure, fallback = _obj(paths["T03-08"]), _obj(paths["T03-08-Fallback"])
    require(failure["fallbackMarkerSha256"] == fallback["fallbackMarkerSha256"] and failure["processId"] != fallback["processId"],
            f"{result_root}: initializer failure/fallback pair is not the same marker across processes")
    return {"milestone": "M03", "resultPassed": True, "baselineBuildId": manifest["baselineBuildId"],
            "runtimeAbiHash": manifest["runtimeAbiHash"], "modes": results,
            "evidence": "Player observations bound to linked snapshots, Editor replay and artifact SHA-256; no authenticity or PE parsing claim"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-manifest", type=Path, required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--baseline-manifest", type=Path)
    parser.add_argument("--baseline-snapshot", type=Path)
    parser.add_argument("--native-off-result", type=Path, help="Explicit T03-09 receipt if kept outside result-dir")
    parser.add_argument("--on-build", type=Path, required=True, help="M03 NativeOn m03-player-build.json receipt")
    parser.add_argument("--off-build", type=Path, required=True, help="M03 NativeOff m03-player-build.json receipt")
    parser.add_argument("--editor-replay", type=Path, help="Editor replay receipt; defaults to fixture sibling m03-editor-replay.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = verify_suite(args.fixture_manifest.resolve(), args.result_dir.resolve(),
                              args.baseline_manifest.resolve() if args.baseline_manifest else None,
                              args.baseline_snapshot.resolve() if args.baseline_snapshot else None,
                              args.native_off_result.resolve() if args.native_off_result else None,
                              args.on_build.resolve() if args.on_build else None,
                              args.off_build.resolve() if args.off_build else None,
                              args.editor_replay.resolve() if args.editor_replay else None)
        text = json.dumps(result, indent=2) + "\n"
        if args.output:
            require(not args.output.exists() and not args.output.is_symlink(), f"Refusing to overwrite {args.output}")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding="utf-8")
        print(text, end="")
        return 0
    except (VerificationError, OSError, ValueError, KeyError, TypeError) as error:
        print("[FAIL] " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
