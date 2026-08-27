"""Independently verify the M02 Editor report and its on-disk artifacts.

This verifier deliberately treats the Unity report as an index, not as proof.
Manifest, snapshot, bundle and native-library bytes are re-read and hashed from
their recorded paths.  It validates the Unity metadata contracts emitted by
the AssemblyShadow builders; it does not claim runtime IL or PE/MVID parsing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import uuid
import xml.etree.ElementTree as ET

from shadow_tools import VerificationError, read_json, require, safe_file


TARGET = "StandaloneOSX"
CANDIDATES = frozenset({
    "AssemblyA.Contracts",
    "AssemblyA.Implementation.Extensibility",
    "AssemblyA.Implementation.Internal",
    "AssemblyShadowDemo.ContractsConsumer",
    "AssemblyShadowDemo.ExtensibilityConsumer",
})
BOOTSTRAP = "AssemblyShadowDemo.Bootstrap"
INTERNAL = "AssemblyA.Implementation.Internal"
EXTENSIBILITY = "AssemblyA.Implementation.Extensibility"
CONTRACTS = "AssemblyA.Contracts"
M01_BUNDLES = frozenset({"business-scene.bundle", "versioned-prefab.bundle", "versioned-data.bundle"})
M01_ASSEMBLIES = frozenset({
    "AssemblyA.Contracts",
    "AssemblyA.Implementation.Extensibility",
    "AssemblyA.Implementation.Internal",
})
CASE_IDS = frozenset({
    "T02-01", "T02-02", "T02-03", "T02-04", "T02-05", "T02-06", "T02-07",
    "M02-Repeatability", "M02-SnapshotTamper",
})
PATCH_IDS = frozenset({"P01", "P02", "P03", "P05-requires-bundles", "P01-repeat"})
NUNIT_SUITES = ("MetadataTests", "PolicyTests", "GraphAndInputTests", "ResourceAbiTests", "SnapshotTests", "SignatureHashTests")
NUNIT_SUITES = NUNIT_SUITES + ("ResourceReceiptTests",)


def digest(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), f"Cannot hash missing or symlinked file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _need(condition, path, message):
    require(condition, f"{path}: {message}")


def _json(path: Path):
    try:
        return read_json(path)
    except VerificationError as error:
        raise VerificationError(f"{path}: {error}") from error


def _string(value, path, field):
    _need(isinstance(value, str) and value.strip(), path, f"{field} must be a non-empty string")
    return value


def _absolute_file(path_value, path, field):
    value = _string(path_value, path, field)
    result = Path(value)
    _need(result.is_absolute(), path, f"{field} must be an absolute path")
    _need(result.is_file() and not result.is_symlink(), path, f"{field} is missing or symlinked: {result}")
    return result


def _root(path: Path, label: str) -> Path:
    original = Path(path)
    _need(not original.is_symlink(), label, "directory is symlinked")
    path = original.resolve()
    _need(path.is_dir(), label, "directory is missing")
    return path


def _relative(root: Path, value, path, field):
    value = _string(value, path, field)
    _need(not Path(value).is_absolute() and "\\" not in value, path, f"{field} must be a relative POSIX path")
    try:
        return safe_file(root, value)
    except VerificationError as error:
        raise VerificationError(f"{path}.{field}: {error}") from error


def _relative_dir(root: Path, value, path, field) -> Path:
    value = _string(value, path, field)
    _need(not Path(value).is_absolute() and "\\" not in value, path, f"{field} must be a relative POSIX path")
    parts = value.split("/")
    _need(all(part not in ("", ".", "..") for part in parts), path, f"{field} escapes its root")
    result = root.joinpath(*parts)
    _need(result.is_dir() and not result.is_symlink(), path, f"{field} directory is missing: {result}")
    for part in (result, *result.parents):
        _need(not part.is_symlink(), path, f"{field} has symlinked component: {part}")
    return result


def _name(value, path, field):
    return _string(value, path, field).strip()


def _names(items, path, field):
    _need(isinstance(items, list), path, f"{field} must be an array")
    result = []
    for index, item in enumerate(items):
        item_path = f"{path}.{field}[{index}]"
        if isinstance(item, str):
            result.append(_name(item, item_path, "name"))
        else:
            _need(isinstance(item, dict), item_path, "entry must be a string or object")
            result.append(_name(item.get("name"), item_path, "name"))
    _need(len(result) == len(set(result)), path, f"{field} contains duplicate names")
    return result


def _normal(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _csharp_len(value):
    return len(value.encode("utf-16-le")) // 2


def _resource_abi_hash(descriptor):
    """Mirror ResourceAbiHasher v2's canonical UTF-8 input for independent checking."""
    text = ["resource-abi-schema:2\n"]

    def append(key, value):
        value = "" if value is None else str(value)
        text.append(f"{key}={_csharp_len(value)}:{value}\n")

    def append_many(key, values):
        values = {value for value in (values or []) if value is not None}
        for value in sorted(values):
            append(key, value)

    append("descriptor-schema", descriptor.get("schemaVersion", ""))
    types = [item for item in (descriptor.get("types") or []) if isinstance(item, dict)]
    for item in sorted(types, key=lambda value: value.get("typeKey") or ""):
        append("type", item.get("typeKey")); append("assembly", item.get("assembly")); append("namespace", item.get("namespace"))
        append("name", item.get("type")); append("base", item.get("baseChain"))
        append_many("interface", item.get("interfaces")); append("callback", "1" if item.get("serializationCallback") is True else "0")
        append("callback-semantics", item.get("callbackSemanticHash")); append_many("serialize-reference-candidate", item.get("serializeReferenceCandidates"))
        append_many("referenced-type", item.get("referencedTypeKeys")); append_many("type-unknown-reason", item.get("unknownReasons"))
        fields = [field for field in (item.get("fields") or []) if isinstance(field, dict)]
        for field in sorted(fields, key=lambda value: (value.get("declaringType") or "", value.get("name") or "")):
            append("field.declaring", field.get("declaringType")); append("field.name", field.get("name")); append("field.type", field.get("type"))
            append("field.shape", field.get("shape")); append("field.flags", field.get("flags")); append_many("field.former", field.get("formerNames"))
            append("field.managed-reference", field.get("managedReferenceMode")); append("field.unknown", "1" if field.get("unknown") is True else "0")
        append("type.unknown", "1" if item.get("hasUnknown") is True else "0")
    append_many("unknown", descriptor.get("unknowns"))
    return "sha256:" + hashlib.sha256("".join(text).encode("utf-8")).hexdigest()


def _resource_source_set_hash(sources):
    entries = []
    for source in sources:
        values = {
            "path": source.get("path", ""), "snapshotPath": source.get("snapshotPath", ""), "sha256": source.get("sha256", ""),
            "metaSnapshotPath": source.get("metaSnapshotPath", ""), "metaSha256": source.get("metaSha256", ""), "guid": source.get("guid", ""),
            "builtin": source.get("builtin", False), "dependencies": source.get("dependencies") or [],
        }
        entries.append(json.dumps(values, ensure_ascii=False, separators=(",", ":")))
    return hashlib.sha256(("resource-source-set:1\n" + "\n".join(sorted(entries))).encode("utf-8")).hexdigest()


def _runtime_abi_hash(pins, path):
    _need(isinstance(pins, dict), path, "sourcePins must be an object")
    values = [pins.get("unityVersion"), pins.get("target"), pins.get("architecture")]
    for repo in ("hybridclr", "il2cppPlus", "hybridclrUnity"):
        entry = pins.get(repo)
        _need(isinstance(entry, dict), path, f"sourcePins.{repo} is missing")
        values.append(entry.get("revision"))
    _need(all(isinstance(value, str) and value for value in values), path, "source pin identity is incomplete")
    return hashlib.sha256(("assembly-shadow-runtime-abi:1\n" + "\n".join(values)).encode("utf-8")).hexdigest()


def _canonical_assembly_name(value):
    """Mirror AssemblyIdentityUtil.CanonicalName for snapshot role hashing."""
    if not isinstance(value, str) or not value.strip():
        return ""
    name = value.strip().replace("\\", "/")
    name = name.rsplit("/", 1)[-1]
    if name.lower().endswith(".dll"):
        name = name[:-4]
    return name.strip().lower()


def _text(value):
    """StringBuilder.Append(object) renders null as an empty string in C#."""
    return "" if value is None else str(value)


def _verify_source_pins(pins, path, expected=None):
    """Validate the complete source-pin DTO, including demo provenance.

    RuntimeAbiHash intentionally excludes the demo revision, so checking only
    that derived value would allow a different demo source tree to masquerade
    as the same runtime ABI.  The manifest, Player receipt and resource receipt
    must therefore carry the same complete four-repository pin object.
    """
    _need(isinstance(pins, dict), path, "sourcePins must be an object")
    _need(pins.get("schemaVersion") == 1, path, "sourcePins schemaVersion must be 1")
    for field in ("unityVersion", "target", "architecture"):
        _string(pins.get(field), path, field)
    for repo in ("hybridclr", "hybridclrUnity", "il2cppPlus", "demo"):
        entry = pins.get(repo)
        entry_path = f"{path}.{repo}"
        _need(isinstance(entry, dict), entry_path, "repository pin is missing")
        _string(entry.get("url"), entry_path, "url")
        revision = _string(entry.get("revision"), entry_path, "revision")
        _need(re.fullmatch(r"[0-9a-f]{40}", revision) is not None, entry_path,
             "revision must be an exact forty-character commit SHA")
    if expected is not None:
        _need(_normal(pins) == _normal(expected), path, "source pins differ from baseline provenance")


def _snapshot_files(receipt, root: Path, path: Path, validate_sections=True):
    arrays = (("assemblies", receipt.get("assemblies")), ("filteredAssemblies", receipt.get("filteredAssemblies")),
              ("references", receipt.get("references")))
    by_name = {}
    all_files = []
    for section, entries in arrays:
        _need(isinstance(entries, list), path, f"{section} must be an array")
        for index, entry in enumerate(entries):
            entry_path = f"{path}.{section}[{index}]"
            _need(isinstance(entry, dict), entry_path, "snapshot entry must be an object")
            name = _name(entry.get("name"), entry_path, "name")
            _need("/" not in name and "\\" not in name, entry_path, "assembly name must not contain path separators")
            if validate_sections:
                section_path = {"assemblies": "Assemblies", "filteredAssemblies": "Assemblies/Filtered", "references": "References"}[section]
                _need(entry.get("path") == f"{section_path}/{name}.dll", entry_path,
                     "captured DLL cannot be renamed or moved between input/reference/filter roles")
                if entry.get("pdbPath"):
                    _need(entry.get("pdbPath") == f"{section_path}/{name}.pdb", entry_path,
                         "captured PDB cannot be renamed or moved between input/reference/filter roles")
            _need(name not in by_name, entry_path, f"duplicate snapshot assembly: {name}")
            by_name[name] = entry
            all_files.append(entry)
            dll = _relative(root, entry.get("path"), entry_path, "path")
            _need(digest(dll) == entry.get("sha256"), entry_path, "snapshot DLL SHA-256 differs from bytes")
            if entry.get("pdbPath"):
                pdb = _relative(root, entry["pdbPath"], entry_path, "pdbPath")
                _need(digest(pdb) == entry.get("pdbSha256"), entry_path, "snapshot PDB SHA-256 differs from bytes")
    expected = {str(path.resolve()) for entry in all_files for path in [root / entry["path"]]}
    actual = {str(path.resolve()) for path in root.rglob("*.dll")
             if "LinkedPlayer" not in path.relative_to(root).parts}
    _need(expected == actual, path, "snapshot DLL inventory contains undeclared or missing files")
    return by_name, all_files


def _snapshot_hash(receipt, root: Path, path):
    text = ["assembly-shadow-snapshot:1\n"]
    text.extend(_text(receipt.get(field, "")) + "\n" for field in ("kind", "unityVersion", "target", "architecture"))
    text.append(_runtime_abi_hash(receipt.get("sourcePins"), path) + "\n")
    text.append(("filtered-proof" if receipt.get("playerBuildFilterCaptured") is True else "compiler-output") + "\n")
    text.append(str(receipt.get("playerBuildOptions", 0)) + "\n")
    for name in sorted(receipt.get("normalHotUpdateAssemblies") or []): text.append("normal:" + name + "\n")
    roles = receipt.get("filteredAssemblyCapabilities") or []
    _need(isinstance(roles, list), path, "filteredAssemblyCapabilities must be an array")
    for role in sorted(roles, key=lambda item: item.get("name", "") if isinstance(item, dict) else ""):
        _need(isinstance(role, dict), path, "filtered capability must be an object")
        text.append("filtered-role:" + _canonical_assembly_name(_name(role.get("name"), path, "filteredAssemblyCapabilities.name")) + ":" +
                    _text(role.get("classification", 0)) + ":" + _text(role.get("isPrecompiled", False)) + ":" +
                    _text(role.get("isShadowCapable", False)) + ":" + _text(role.get("isBootstrap", False)) + ":" +
                    _text(role.get("capabilityDeclared", False)) + "\n")
    text.append("linked-player:" + _text(receipt.get("linkedPlayerReceiptHash")) + "\n")
    for name in sorted(receipt.get("linkerExcludedAssemblies") or []):
        text.append("linker-excluded:" + _text(name) + "\n")
    linker_roles = receipt.get("linkerExcludedAssemblyCapabilities") or []
    _need(isinstance(linker_roles, list), path, "linkerExcludedAssemblyCapabilities must be an array")
    for role in sorted(linker_roles, key=lambda item: item.get("name", "") if isinstance(item, dict) else ""):
        _need(isinstance(role, dict), path, "linker-excluded capability must be an object")
        text.append("linker-excluded-role:" + _canonical_assembly_name(_text(role.get("name"))) + ":" +
                    _text(role.get("classification", 0)) + ":" + _text(role.get("isPrecompiled", False)) + ":" +
                    _text(role.get("isShadowCapable", False)) + ":" + _text(role.get("isBootstrap", False)) + ":" +
                    _text(role.get("capabilityDeclared", False)) + "\n")
    for define in sorted(receipt.get("extraScriptingDefines") or []): text.append(_text(define) + "\n")
    _, all_files = _snapshot_files(receipt, root, path, validate_sections=False)
    for entry in sorted(all_files, key=lambda item: item.get("path", "")):
        for field in ("path", "sha256", "pdbPath", "pdbSha256"):
            text.append(str(entry.get(field, "")) + "\n")
    return hashlib.sha256("".join(text).encode("utf-8")).hexdigest()


def _hash64(value, path, field):
    _need(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
          path, f"{field} must be a lowercase SHA-256")
    return value


def _linked_claim_absent(receipt):
    """Mirror ShadowLinkedPlayerEvidence.IsAbsent after Unity JSON materialization."""
    if receipt.get("linkedPlayerReceiptHash") not in (None, ""):
        return False
    for field in ("linkerExcludedAssemblies", "linkerExcludedAssemblyCapabilities"):
        values = receipt.get(field)
        if values is not None and (not isinstance(values, list) or len(values) != 0):
            return False
    linked = receipt.get("linkedPlayerReceipt")
    if linked is None:
        return True
    # A raw `{}` also materializes as the DTO's constructor-default object in
    # Unity (schemaVersion 1); Python's missing key is the equivalent absence.
    if not isinstance(linked, dict) or linked.get("schemaVersion") not in (None, 0, 1):
        return False
    for field in ("buildGuid", "nativeLibrarySha256", "target", "architecture", "sourceDirectory"):
        if linked.get(field) not in (None, ""):
            return False
    for field in ("protectedAssemblies", "assemblies"):
        values = linked.get(field)
        if values is not None and (not isinstance(values, list) or len(values) != 0):
            return False
    return True


def _canonical_names(values, path, field):
    _need(isinstance(values, list), path, f"{field} must be an array")
    names = []
    for index, value in enumerate(values):
        item_path = f"{path}.{field}[{index}]"
        name = _name(value, item_path, "name")
        canonical = _canonical_assembly_name(name)
        _need(name == canonical, item_path, "assembly identity must be canonical lowercase")
        _need(canonical not in names, item_path, "duplicate assembly identity")
        names.append(canonical)
    return set(names)


def _verify_linked_player(snapshot: Path, receipt: dict, descriptors: dict, path: Path):
    linked_root = snapshot / "LinkedPlayer"
    linked_path = linked_root / "linked-player-receipt.json"
    linked = _json(linked_path)
    _need(linked.get("schemaVersion") == 1, linked_path, "linked player receipt schemaVersion must be 1")
    for field in ("buildGuid", "nativeLibrarySha256", "target", "architecture", "sourceDirectory"):
        _string(linked.get(field), linked_path, field)
    _need(Path(linked["sourceDirectory"]).is_absolute(), linked_path, "sourceDirectory must be absolute")
    _need(linked.get("buildGuid") == receipt.get("buildGuid") and
          linked.get("nativeLibrarySha256") == receipt.get("nativeLibrarySha256") and
          linked.get("target") == receipt.get("target") and linked.get("architecture") == receipt.get("architecture"),
          linked_path, "linked Player evidence identity differs from the Player receipt")
    _hash64(linked["nativeLibrarySha256"], linked_path, "nativeLibrarySha256")
    _need(receipt.get("linkedPlayerReceiptHash") == _hash64(receipt.get("linkedPlayerReceiptHash"), path, "linkedPlayerReceiptHash"),
          path, "linkedPlayerReceiptHash is missing")
    _need(_snapshot_linked_hash(linked) == receipt["linkedPlayerReceiptHash"], linked_path,
          "linkedPlayerReceiptHash differs from receipt")
    protected = _canonical_names(linked.get("protectedAssemblies"), linked_path, "protectedAssemblies")
    _need(protected == {_canonical_assembly_name(name) for name in CANDIDATES | {BOOTSTRAP}}, linked_path,
          "linked protectedAssemblies must contain exactly the five candidates and Bootstrap")
    files = linked.get("assemblies")
    _need(isinstance(files, list) and files, linked_path, "linked assemblies are missing")
    linked_names = set()
    expected_files = {linked_path.resolve()}
    for index, item in enumerate(files):
        item_path = f"{linked_path}.assemblies[{index}]"
        _need(isinstance(item, dict), item_path, "linked assembly entry must be an object")
        name = _name(item.get("name"), item_path, "name")
        canonical = _canonical_assembly_name(name)
        _need(name == canonical and name not in linked_names, item_path, "linked assembly name must be unique canonical lowercase")
        _need(item.get("path") == f"Assemblies/{name}.dll", item_path, "linked assembly path is not canonical")
        _hash64(item.get("sha256"), item_path, "sha256")
        try:
            parsed = uuid.UUID(_string(item.get("mvid"), item_path, "mvid"))
        except (ValueError, AttributeError) as error:
            raise VerificationError(f"{item_path}.mvid: invalid GUID") from error
        _need(parsed.int != 0, item_path, "mvid must not be empty")
        dll = _relative(linked_root, item["path"], item_path, "path")
        _need(digest(dll) == item["sha256"], item_path, "linked DLL SHA-256 differs from bytes")
        expected_files.add(dll.resolve())
        pdb_path = item.get("pdbPath")
        pdb_sha = item.get("pdbSha256")
        if pdb_path or pdb_sha:
            _need(pdb_path == f"Assemblies/{name}.pdb", item_path, "linked PDB path is not canonical")
            _hash64(pdb_sha, item_path, "pdbSha256")
            pdb = _relative(linked_root, pdb_path, item_path, "pdbPath")
            _need(digest(pdb) == pdb_sha, item_path, "linked PDB SHA-256 differs from bytes")
            expected_files.add(pdb.resolve())
        linked_names.add(name)
    for item in linked_root.rglob("*"):
        _need(not item.is_symlink(), item, "linked Player proof contains a symlink")
    actual_files = {item.resolve() for item in linked_root.rglob("*") if item.is_file()}
    _need(actual_files == expected_files, linked_root, "linked Player proof contains undeclared or missing files")
    player_names = {_canonical_assembly_name(entry["name"]) for entry in receipt.get("assemblies", [])}
    excluded = _canonical_names(receipt.get("linkerExcludedAssemblies"), path, "linkerExcludedAssemblies")
    _need(excluded == player_names - linked_names, path,
          "linkerExcludedAssemblies must equal Player inputs absent from linked output")
    _need(not (excluded & protected), path, "linker exclusions cannot contain protected candidates or Bootstrap")
    roles = receipt.get("linkerExcludedAssemblyCapabilities")
    _need(isinstance(roles, list), path, "linkerExcludedAssemblyCapabilities must be an array")
    role_names = set()
    for index, role in enumerate(roles):
        role_path = f"{path}.linkerExcludedAssemblyCapabilities[{index}]"
        _need(isinstance(role, dict), role_path, "linker-excluded capability must be an object")
        name = _name(role.get("name"), role_path, "name")
        _need(name == _canonical_assembly_name(name), role_path, "linker-excluded capability name must be canonical lowercase")
        _need(name in excluded and name not in role_names, role_path, "linker-excluded capability does not match exclusions")
        _need(role.get("classification") in (0, 1, 2, 3, 4), role_path,
             "linker-excluded capability cannot claim BuildFiltered")
        _need(role.get("isShadowCapable") is not True and role.get("isBootstrap") is not True, role_path,
             "linker-excluded capability cannot be a candidate or Bootstrap")
        role_names.add(name)
        for desc_name, descriptor in descriptors.items():
            if _canonical_assembly_name(desc_name) == name:
                for field in ("classification", "isPrecompiled", "isShadowCapable", "isBootstrap", "capabilityDeclared"):
                    _need(descriptor.get(field, 0 if field == "classification" else False) == role.get(field, 0 if field == "classification" else False),
                          role_path, f"linker-excluded role {field} differs from baseline descriptor")
    _need(role_names == excluded, path, "linker-excluded capability inventory is incomplete")
    _need(protected <= linked_names and protected <= player_names, linked_path,
          "all protected candidates and Bootstrap must be present in linked output")
    return linked, linked_names


def _snapshot_linked_hash(linked):
    text = ["assembly-shadow-linked-player:1\n"]
    text.extend(_text(linked.get(field)) + "\n" for field in ("schemaVersion", "buildGuid", "nativeLibrarySha256", "target", "architecture", "sourceDirectory"))
    for name in sorted(linked.get("protectedAssemblies") or []):
        text.append("protected:" + _text(name) + "\n")
    for item in sorted(linked.get("assemblies") or [], key=lambda value: value.get("path", "") if isinstance(value, dict) else ""):
        _need(isinstance(item, dict), "linkedPlayerReceipt", "linked assembly entry must be an object")
        for field in ("name", "path", "sha256", "mvid", "pdbPath", "pdbSha256"):
            text.append(_text(item.get(field)) + "\n")
    return hashlib.sha256("".join(text).encode("utf-8")).hexdigest()


def _verify_editor_report(path: Path):
    report = _json(path)
    _need(isinstance(report, dict), path, "report must be an object")
    _need(report.get("schemaVersion") == 1, path, "schemaVersion must be 1")
    _need(report.get("result") == "Passed", path, "result must be Passed")
    _string(report.get("runDirectory"), path, "runDirectory")
    run = _root(Path(report["runDirectory"]), f"{path}.runDirectory")
    cases = report.get("cases")
    _need(isinstance(cases, list), path, "cases must be an array")
    observed = []
    for index, case in enumerate(cases):
        case_path = f"{path}.cases[{index}]"
        _need(isinstance(case, dict), case_path, "case must be an object")
        observed.append(_name(case.get("id"), case_path, "id"))
        _need(case.get("passed") is True, case_path, "passed must be true")
    _need(set(observed) == CASE_IDS and len(observed) == len(CASE_IDS), path,
         "cases must contain exactly T02-01..T02-07, M02-Repeatability and M02-SnapshotTamper")
    _need(isinstance(report.get("artifacts"), list), path, "artifacts must be an array")
    artifacts = {}
    for index, artifact in enumerate(report["artifacts"]):
        artifact_path = f"{path}.artifacts[{index}]"
        _need(isinstance(artifact, dict), artifact_path, "artifact must be an object")
        artifact_id = _name(artifact.get("id"), artifact_path, "id")
        _need(artifact_id not in artifacts, artifact_path, f"duplicate artifact id: {artifact_id}")
        artifact_file = _absolute_file(artifact.get("path"), artifact_path, "path")
        _need(isinstance(artifact.get("sha256"), str) and artifact["sha256"], artifact_path,
             "sha256 must be present")
        _need(digest(artifact_file) == artifact["sha256"], artifact_path, "artifact SHA-256 differs from bytes")
        _need(artifact_file.name == "patch-manifest.json", artifact_path, "artifact must be patch-manifest.json")
        _need(artifact_file.parent.resolve().is_relative_to(run), artifact_path,
             "patch artifact root must be below report.runDirectory")
        artifacts[artifact_id] = artifact_file
    _need(set(artifacts) == PATCH_IDS, path, "artifacts must contain P01, P02, P03, P05-requires-bundles and P01-repeat exactly")
    baseline_path = _absolute_file(report.get("baselineManifestPath"), path, "baselineManifestPath")
    _need(report.get("baselineManifestSha256") == digest(baseline_path), path,
         "baselineManifestSha256 differs from actual baseline-manifest.json")
    _need(baseline_path.name == "baseline-manifest.json", path, "baselineManifestPath must name baseline-manifest.json")
    return report, run, baseline_path, artifacts


def _verify_sidecar_manifest(root: Path, manifest: dict, path: Path):
    _need(manifest.get("schemaVersion") == 1 and manifest.get("semanticHashSchema") == 1,
         path, "manifest schemaVersion and semanticHashSchema must be 1")
    manifest_sidecar = root / "manifest.sha256"
    _need(manifest_sidecar.is_file() and not manifest_sidecar.is_symlink(), manifest_sidecar,
         "manifest SHA sidecar is missing")
    _need(manifest_sidecar.read_text().strip() == digest(path), manifest_sidecar,
         "manifest SHA sidecar differs from baseline-manifest.json")
    for field in ("baselineBuildId", "unityVersion", "target", "architecture", "runtimeAbiHash",
                  "bootstrapAbiHash", "resourceAbiHash", "resourceIndexHash", "playerInputSnapshotHash",
                  "playerBuildGuid", "nativeLibrarySha256", "resourceBaselinePath", "resourceBuildReceiptHash"):
        _string(manifest.get(field), path, field)
    _need(manifest["target"] == TARGET, path, "target must be StandaloneOSX")
    sidecars = {
        "resource-abi.json": root / "resource-abi.json",
        "resource-script-index.json": root / "resource-script-index.json",
        "source-pins.json": root / "source-pins.json",
        "policy.json": root / "policy.json",
    }
    for name, sidecar in sidecars.items():
        _need(sidecar.is_file() and not sidecar.is_symlink(), f"{path.parent}/{name}", "required baseline sidecar is missing")
    abi = _json(sidecars["resource-abi.json"])
    index = _json(sidecars["resource-script-index.json"])
    _need(abi.get("schemaVersion") == 2, sidecars["resource-abi.json"], "resource ABI schemaVersion must be 2")
    _need(index.get("schemaVersion") == 2, sidecars["resource-script-index.json"], "resource script index schemaVersion must be 2")
    _need(abi.get("unknowns") in (None, []), sidecars["resource-abi.json"], "baseline resource ABI contains unknown entries")
    _need(index.get("hasUnknown") in (None, False) and index.get("unknowns") in (None, []),
         sidecars["resource-script-index.json"], "baseline resource index contains unknown entries")
    _need(_resource_abi_hash(abi) == manifest.get("resourceAbiHash"), sidecars["resource-abi.json"],
         "resourceAbiHash does not match resource-abi.json")
    source_pins = _json(sidecars["source-pins.json"])
    _verify_source_pins(source_pins, sidecars["source-pins.json"], manifest.get("sourcePins"))
    _need(_normal(source_pins) == _normal(manifest.get("sourcePins")), sidecars["source-pins.json"],
         "source-pins.json differs from baseline manifest")
    _need(manifest.get("resourceBaselinePath") == "ResourceInputs", path,
         "resourceBaselinePath must be the fixed ResourceInputs evidence directory")
    _need(digest(sidecars["policy.json"]) == manifest.get("policyHash"), sidecars["policy.json"],
         "policyHash does not match policy.json")
    _need(digest(sidecars["resource-script-index.json"]) == manifest["resourceIndexHash"], path,
         "resourceIndexHash does not match resource-script-index.json")
    _need(isinstance(manifest.get("shadowCandidates"), list) and set(manifest["shadowCandidates"]) == CANDIDATES and
         len(manifest["shadowCandidates"]) == len(CANDIDATES), path, "shadowCandidates must contain exactly five M02 candidates")
    _need(isinstance(manifest.get("bootstrapAssemblies"), list) and manifest["bootstrapAssemblies"] == [BOOTSTRAP],
         path, "bootstrapAssemblies must contain the fixed Bootstrap exactly")
    _need(isinstance(manifest.get("assemblies"), list) and manifest["assemblies"], path, "assemblies are missing")
    descriptors = {}
    for index, descriptor in enumerate(manifest["assemblies"]):
        descriptor_path = f"{path}.assemblies[{index}]"
        _need(isinstance(descriptor, dict), descriptor_path, "assembly descriptor must be an object")
        name = _name(descriptor.get("name"), descriptor_path, "name")
        _need("/" not in name and "\\" not in name, descriptor_path, "assembly name must not contain path separators")
        _need(name not in descriptors, descriptor_path, f"duplicate assembly descriptor: {name}")
        descriptors[name] = descriptor
        file_path = _relative(root, descriptor.get("filePath"), descriptor_path, "filePath")
        _need(digest(file_path) == descriptor.get("sha256"), descriptor_path, "assembly SHA-256 differs from manifest")
        sidecar = _relative(root, f"assemblies/{name}.json", descriptor_path, "sidecar")
        _need(sidecar.is_file() and not sidecar.is_symlink(), descriptor_path, "assembly sidecar is missing")
        side = _json(sidecar)
        for field in ("name", "mvid", "sha256", "semanticHash"):
            _need(side.get(field) == descriptor.get(field), sidecar, f"sidecar {field} differs from manifest descriptor")
    _need(BOOTSTRAP in descriptors, path, "fixed Bootstrap descriptor is missing")
    _need({name for name, descriptor in descriptors.items() if descriptor.get("isShadowCapable") is True} == CANDIDATES,
         path, "manifest must mark exactly the five M02 candidates as shadow-capable")
    _need({name for name, descriptor in descriptors.items() if descriptor.get("isBootstrap") is True} == {BOOTSTRAP},
         path, "manifest must mark exactly the fixed Bootstrap as bootstrap")
    bootstrap = descriptors[BOOTSTRAP]
    _need(bootstrap.get("isBootstrap") is True and bootstrap.get("isShadowCapable") is False,
         path, "Bootstrap metadata is not fixed/non-shadow")
    _need(not (set(bootstrap.get("references") or ()) & CANDIDATES), path,
         "Bootstrap metadata references a shadow candidate")
    return descriptors


def _verify_player_snapshot(root: Path, manifest: dict, descriptors: dict, path: Path):
    snapshot = _relative_dir(root, manifest.get("playerInputSnapshot"), path, "playerInputSnapshot")
    receipt_path = snapshot / "assembly-snapshot.json"
    receipt = _json(receipt_path)
    _need(receipt.get("schemaVersion") == 1 and receipt.get("kind") == "PlayerBuildInputs", receipt_path,
         "not a PlayerBuildInputs receipt")
    _need(receipt.get("playerBuildSucceeded") is True and receipt.get("playerBuildFilterCaptured") is True and
          _string(receipt.get("buildGuid"), receipt_path, "buildGuid"),
         receipt_path, "successful Player build and non-empty buildGuid are required")
    _need(isinstance(receipt.get("playerBuildOptions"), int) and receipt["playerBuildOptions"] & 1,
         receipt_path, "Player build options must include Development")
    for field in ("unityVersion", "target", "architecture", "snapshotHash", "nativeLibrarySha256"):
        _string(receipt.get(field), receipt_path, field)
    for field in ("unityVersion", "target", "architecture"):
        _need(receipt[field] == manifest[field], receipt_path, f"{field} differs from baseline manifest")
    _verify_source_pins(receipt.get("sourcePins"), receipt_path, manifest.get("sourcePins"))
    native = _absolute_file(receipt.get("nativeLibraryPath"), receipt_path, "nativeLibraryPath")
    _need(digest(native) == receipt["nativeLibrarySha256"] == manifest["nativeLibrarySha256"], receipt_path,
         "native library SHA-256 does not match receipt and baseline manifest")
    _need(receipt["snapshotHash"] == manifest["playerInputSnapshotHash"], receipt_path,
         "snapshotHash differs from baseline manifest")
    linked, linked_names = _verify_linked_player(snapshot, receipt, descriptors, receipt_path)
    by_name, _ = _snapshot_files(receipt, snapshot, receipt_path)
    aot = {entry["name"] for entry in receipt.get("assemblies", [])}
    filtered = {entry["name"] for entry in receipt.get("filteredAssemblies", [])}
    _need(CANDIDATES <= aot and len(CANDIDATES & aot) == 5, receipt_path,
         "captured Player inputs do not contain exactly the five candidates")
    _need(not (CANDIDATES & filtered) and BOOTSTRAP not in filtered, receipt_path,
         "shadow candidate or Bootstrap was filtered out of AOT")
    normal = receipt.get("normalHotUpdateAssemblies") or []
    _need(isinstance(normal, list), receipt_path, "normalHotUpdateAssemblies must be an array")
    normal = [_name(name, receipt_path, "normalHotUpdateAssemblies.name") for name in normal]
    _need(len(normal) == len(set(normal)) and not (set(normal) & CANDIDATES), receipt_path,
         "normal hot-update role overlaps a shadow candidate")
    roles = receipt.get("filteredAssemblyCapabilities") or []
    role_map = {}
    for index, role in enumerate(roles):
        role_path = f"{receipt_path}.filteredAssemblyCapabilities[{index}]"
        _need(isinstance(role, dict), role_path, "filtered capability must be an object")
        name = _name(role.get("name"), role_path, "name")
        _need(name in filtered and name not in role_map, role_path, "filtered capability does not match a filtered DLL")
        _need(role.get("classification") in (4, 5), role_path, "filtered DLL role must be NormalHotUpdate or BuildFiltered")
        _need(role.get("isShadowCapable") is not True and role.get("isBootstrap") is not True, role_path,
             "filtered DLL cannot be a candidate or Bootstrap")
        if role["classification"] == 4:
            _need(name in normal, role_path, "NormalHotUpdate filtered DLL is absent from normalHotUpdateAssemblies")
        if name in descriptors:
            descriptor = descriptors[name]
            for field in ("classification", "isPrecompiled", "isShadowCapable", "isBootstrap", "capabilityDeclared"):
                _need(descriptor.get(field, 0 if field == "classification" else False) == role.get(field, 0 if field == "classification" else False),
                     role_path, f"filtered role {field} differs from baseline descriptor")
        role_map[name] = role
    _need(set(role_map) == filtered, receipt_path, "filtered DLL role inventory is incomplete")
    _need(set(descriptors) == aot | filtered, path,
         "baseline manifest descriptors must cover the AOT and filtered Player assemblies exactly")
    for name in aot:
        if name in descriptors and name in CANDIDATES:
            _need(descriptors[name].get("isShadowCapable") is True and descriptors[name].get("classification", 0) == 0,
                 path, f"candidate descriptor has an invalid filtered role: {name}")
    for name, role in role_map.items():
        if name in descriptors:
            _need(descriptors[name].get("classification") == role.get("classification") and
                 descriptors[name].get("isShadowCapable") is not True and descriptors[name].get("isBootstrap") is not True,
                 path, f"filtered descriptor role differs from receipt: {name}")
    _need(_snapshot_hash(receipt, snapshot, receipt_path) == receipt.get("snapshotHash"), receipt_path,
         "snapshotHash does not match the complete receipt proof")
    for candidate in CANDIDATES:
        entry = by_name[candidate]
        descriptor = descriptors.get(candidate)
        _need(descriptor is not None, path, f"candidate descriptor is missing: {candidate}")
        copied = _relative(root, descriptor.get("filePath"), path, f"assemblies[{candidate}].filePath")
        _need(digest(copied) == entry["sha256"] == descriptor.get("sha256"), path,
             f"candidate {candidate} bytes do not match captured Player input")
    for name, descriptor in descriptors.items():
        if name not in by_name:
            continue
        expected = _relative(root, descriptor.get("filePath"), path, f"assemblies[{name}].filePath")
        _need(digest(expected) == by_name[name].get("sha256") == descriptor.get("sha256"), path,
             f"manifest descriptor bytes differ from captured receipt: {name}")
    return receipt, snapshot, by_name


def _verify_bundles(m01_root: Path, manifest: dict, path: Path):
    m01_manifest_path = m01_root / "baseline-manifest.json"
    m01 = _json(m01_manifest_path)
    _need(isinstance(m01.get("bundles"), list), m01_manifest_path, "M01 bundles are missing")
    old = {}
    for index, bundle in enumerate(m01["bundles"]):
        bundle_path = f"{m01_manifest_path}.bundles[{index}]"
        _need(isinstance(bundle, dict), bundle_path, "bundle must be an object")
        name = _name(bundle.get("name"), bundle_path, "name")
        _need(name not in old, bundle_path, f"duplicate M01 bundle: {name}")
        physical = _relative(m01_root, bundle.get("path"), bundle_path, "path")
        _need(digest(physical) == bundle.get("sha256"), bundle_path, "frozen M01 bundle SHA-256 differs from bytes")
        old[name] = bundle["sha256"]
    _need(set(old) == M01_BUNDLES, m01_manifest_path, "M01 must contain exactly the original three bundles")
    bundles = manifest.get("bundles")
    _need(isinstance(bundles, list) and len(bundles) == 3, path, "M02 must contain exactly three baseline bundles")
    current = {}
    for index, bundle in enumerate(bundles):
        bundle_path = f"{path}.bundles[{index}]"
        _need(isinstance(bundle, dict), bundle_path, "bundle must be an object")
        name = _name(bundle.get("name"), bundle_path, "name")
        _need(name not in current, bundle_path, f"duplicate M02 bundle: {name}")
        current[name] = _string(bundle.get("sha256"), bundle_path, "sha256")
    _need(current == old, path, "M02 baseline bundle hashes differ from frozen M01 bundle files/manifest")


def _verify_resource_baseline(root: Path, manifest: dict, path: Path, m01_root: Path):
    resource_root = _relative_dir(root, manifest.get("resourceBaselinePath"), path, "resourceBaselinePath")
    receipt_path = resource_root / "resource-build-receipt.json"
    _need(receipt_path.is_file() and not receipt_path.is_symlink(), receipt_path, "resource baseline receipt is missing")
    _need(digest(receipt_path) == manifest.get("resourceBuildReceiptHash"), receipt_path,
         "resourceBuildReceiptHash differs from resource-build-receipt.json")
    receipt_manifest_hash = resource_root / "manifest.sha256"
    _need(receipt_manifest_hash.is_file() and receipt_manifest_hash.read_text().strip() == digest(receipt_path), receipt_manifest_hash,
         "resource receipt manifest SHA sidecar is missing or stale")
    receipt = _json(receipt_path)
    _verify_source_pins(receipt.get("sourcePins", manifest.get("sourcePins")), receipt_path, manifest.get("sourcePins"))
    _need(receipt.get("schemaVersion") == 1 and receipt.get("provenance") in
          ("CompilePlayerScriptsAndBuildAssetBundles", "M01AuditedFrozenSourceReconstruction"), receipt_path,
         "resource baseline receipt schema/provenance is not recognized")
    for field in ("unityVersion", "target", "architecture", "compilerSnapshotHash", "resourceAbiHash", "resourceAbiFileSha256",
                  "resourceIndexHash", "sourceSetHash", "bundleDirectory", "compilerSnapshotPath", "metadataAssemblyDirectory"):
        _string(receipt.get(field), receipt_path, field)
    for field in ("unityVersion", "target", "architecture"):
        _need(receipt[field] == manifest[field], receipt_path, f"resource receipt {field} differs from baseline")
    candidate_names = receipt.get("candidateAssemblies")
    _need(isinstance(candidate_names, list) and set(candidate_names) == CANDIDATES and len(candidate_names) == 5,
         receipt_path, "resource receipt candidateAssemblies must contain exactly five candidates")
    abi_path = _relative(resource_root, receipt.get("resourceAbiPath"), receipt_path, "resourceAbiPath")
    index_path = _relative(resource_root, receipt.get("resourceIndexPath"), receipt_path, "resourceIndexPath")
    _need(digest(abi_path) == receipt["resourceAbiFileSha256"], receipt_path, "resource ABI file SHA differs from receipt")
    _need(digest(index_path) == receipt["resourceIndexHash"], receipt_path, "resource index SHA differs from receipt")
    abi = _json(abi_path); index = _json(index_path)
    _need(abi.get("schemaVersion") == 2 and _resource_abi_hash(abi) == receipt["resourceAbiHash"], abi_path,
         "resource ABI schema/hash is invalid")
    _need(index.get("schemaVersion") == 2 and index.get("hasUnknown") is False and index.get("unknowns") == [], index_path,
         "resource index is unproven or contains unknowns")
    _need(receipt["resourceAbiHash"] == manifest["resourceAbiHash"], receipt_path,
         "resource receipt ABI differs from baseline manifest")
    bundles = receipt.get("bundles")
    _need(isinstance(bundles, list) and len(bundles) == 3, receipt_path,
         "resource receipt must contain exactly three bundles")
    for index_number, bundle in enumerate(bundles):
        _need(isinstance(bundle, dict), f"{receipt_path}.bundles[{index_number}]", "bundle must be an object")
        _name(bundle.get("name"), f"{receipt_path}.bundles[{index_number}]", "name")
    _need({bundle["name"] for bundle in bundles} == M01_BUNDLES, receipt_path,
         "resource receipt must contain the original three bundles")
    build_map = receipt.get("buildMap")
    _need(isinstance(build_map, dict) and build_map.get("schemaVersion") == 1 and isinstance(build_map.get("bundles"), list),
         receipt_path, "resource build map is missing or invalid")
    map_by_name = {item.get("name"): item.get("assets") for item in build_map["bundles"] if isinstance(item, dict)}
    receipt_by_name = {item.get("name"): item.get("assets") for item in bundles}
    _need(map_by_name == receipt_by_name, receipt_path, "resource build map differs from captured bundle definitions")
    for index_number, bundle in enumerate(bundles):
        bundle_path = f"{receipt_path}.bundles[{index_number}]"
        physical = _relative(resource_root, receipt["bundleDirectory"] + "/" + _name(bundle.get("name"), bundle_path, "name"), bundle_path, "bundle")
        _need(digest(physical) == bundle.get("sha256"), bundle_path, "resource bundle SHA differs from bytes")
    sources = receipt.get("sources")
    _need(isinstance(sources, list) and sources, receipt_path, "resource source inventory is missing")
    _need(_resource_source_set_hash(sources) == receipt.get("sourceSetHash"), receipt_path,
         "resource source set hash does not match captured sources")
    for index_number, source in enumerate(sources):
        source_path = f"{receipt_path}.sources[{index_number}]"
        _need(isinstance(source, dict), source_path, "resource source must be an object")
        _relative(resource_root, source.get("snapshotPath"), source_path, "snapshotPath")
        _need(digest(_relative(resource_root, source["snapshotPath"], source_path, "snapshotPath")) == source.get("sha256"),
             source_path, "resource source SHA differs from snapshot bytes")
        if source.get("metaSnapshotPath"):
            meta = _relative(resource_root, source["metaSnapshotPath"], source_path, "metaSnapshotPath")
            _need(digest(meta) == source.get("metaSha256"), source_path, "resource meta SHA differs from snapshot bytes")
    compiler_root = _relative_dir(resource_root, receipt["compilerSnapshotPath"], receipt_path, "compilerSnapshotPath")
    compiler_receipt = _json(compiler_root / "assembly-snapshot.json")
    _need(compiler_receipt.get("snapshotHash") == receipt["compilerSnapshotHash"], receipt_path,
         "resource compiler snapshot hash differs from receipt")
    _need(_snapshot_hash(compiler_receipt, compiler_root, compiler_root / "assembly-snapshot.json") == compiler_receipt.get("snapshotHash"),
         compiler_root / "assembly-snapshot.json", "resource compiler snapshot proof hash is invalid")
    if receipt["provenance"] == "CompilePlayerScriptsAndBuildAssetBundles":
        _need(receipt.get("compilerSnapshotIsPlayer") is False and compiler_receipt.get("kind") == "CompilePlayerScripts" and
              compiler_receipt.get("extraScriptingDefines") == [], receipt_path,
             "fresh resource build must use an empty-define compile snapshot")
    else:
        _need(receipt.get("compilerSnapshotIsPlayer") is True, receipt_path, "M01 resource import must retain Player compiler proof")
    metadata = receipt.get("metadataAssemblies")
    _need(isinstance(metadata, list) and metadata, receipt_path, "resource metadata assembly proof is missing")
    _need(all(isinstance(item, dict) for item in metadata), receipt_path,
         "resource metadata proof contains a malformed entry")
    metadata_names = [_canonical_assembly_name(Path(item.get("path", "")).name) for item in metadata]
    _need(len(metadata_names) == len(set(metadata_names)) and set(metadata_names) ==
         {_canonical_assembly_name(name) for name in candidate_names}, receipt_path,
         "resource metadata proof must contain exactly the five candidate roots")
    _relative_dir(resource_root, receipt["metadataAssemblyDirectory"], receipt_path, "metadataAssemblyDirectory")
    compiler_aot = {_canonical_assembly_name(item.get("name")): item for item in compiler_receipt.get("assemblies", [])
                    if isinstance(item, dict)}
    if receipt["provenance"] == "CompilePlayerScriptsAndBuildAssetBundles":
        _need(receipt["metadataAssemblyDirectory"] == "ResourceAssemblies", receipt_path,
             "fresh resource metadata must use ResourceAssemblies")
        for index_number, item in enumerate(metadata):
            item_path = f"{receipt_path}.metadataAssemblies[{index_number}]"
            name = _canonical_assembly_name(Path(item.get("path", "")).name)
            compiled = compiler_aot.get(name)
            _need(compiled is not None and item.get("path") == "ResourceAssemblies/" + compiled.get("name") + ".dll" and
                  item.get("sha256") == compiled.get("sha256"), item_path,
                 "fresh resource metadata bytes differ from the same empty-define compiler input")
    for index_number, item in enumerate(metadata):
        item_path = f"{receipt_path}.metadataAssemblies[{index_number}]"
        physical = _relative(resource_root, item.get("path"), item_path, "path")
        _need(digest(physical) == item.get("sha256"), item_path, "metadata proof SHA differs from bytes")
    metadata_root = resource_root / receipt["metadataAssemblyDirectory"]
    expected_metadata = {(_relative(resource_root, item["path"], receipt_path, "metadataAssemblies.path")).resolve() for item in metadata}
    actual_metadata = {item.resolve() for item in metadata_root.rglob("*.dll")}
    _need(expected_metadata == actual_metadata, metadata_root,
         "resource metadata DLL set differs from the exact candidate proof")
    if receipt.get("provenance") == "M01AuditedFrozenSourceReconstruction":
        _need(receipt.get("originalManifestPath") and receipt.get("originalSourceAuditPath") and receipt.get("reconstructionProof"),
             receipt_path, "M01 resource import proof is incomplete")
        original_path = _relative(resource_root, receipt["originalManifestPath"], receipt_path, "originalManifestPath")
        audit_path = _relative(resource_root, receipt["originalSourceAuditPath"], receipt_path, "originalSourceAuditPath")
        _need(digest(original_path) == receipt.get("originalManifestSha256"), original_path, "original M01 manifest SHA mismatch")
        _need(digest(audit_path) == receipt.get("originalSourceAuditSha256"), audit_path, "original M01 audit SHA mismatch")
        original = _json(original_path); audit = _json(audit_path)
        original_assemblies = original.get("assemblies")
        _need(original.get("baselineBuildId") == "M01-Baseline-v1" and audit.get("verified") is True and
             isinstance(original_assemblies, list) and
             {item.get("name") for item in original_assemblies if isinstance(item, dict)} == M01_ASSEMBLIES and
             len(original_assemblies) == len(M01_ASSEMBLIES), receipt_path,
             "M01 resource import proof identity is invalid")
        _need({item.get("name"): item.get("sha256") for item in original.get("bundles", [])} ==
             {item.get("name"): item.get("sha256") for item in bundles}, receipt_path, "M01 imported bundle proof differs")
    pin_source = next((item for item in sources if item.get("path") == "ProjectSettings/AssemblyShadowSourcePins.json"), None)
    _need(pin_source is not None, receipt_path, "resource source inventory omits source pins")
    pins_file = _relative(resource_root, pin_source.get("snapshotPath"), receipt_path, "sourcePinsSnapshotPath")
    _need(_normal(_json(pins_file)) == _normal(manifest.get("sourcePins")), pins_file,
         "frozen resource source pins differ from baseline manifest")
    return receipt


def _edges(items, path):
    _need(isinstance(items, list), path, "dependencyGraph must be an array")
    result = []
    seen_pairs = set()
    for index, edge in enumerate(items):
        edge_path = f"{path}[{index}]"
        _need(isinstance(edge, dict), edge_path, "dependency edge must be an object")
        consumer = _name(edge.get("consumer"), edge_path, "consumer")
        provider = _name(edge.get("provider"), edge_path, "provider")
        _need(consumer != provider, edge_path, "self-dependency is forbidden")
        _need(_name(edge.get("kind"), edge_path, "kind"), edge_path, "edge kind is required")
        _need((consumer, provider) not in seen_pairs, edge_path, f"duplicate dependency edge: {consumer} -> {provider}")
        seen_pairs.add((consumer, provider))
        result.append((consumer, provider, edge.get("kind"), edge.get("evidence")))
    return result


def _closure(edges, roots, known, path):
    reverse = {name: set() for name in known}
    for consumer, provider, _, _ in edges:
        _need(consumer in known and provider in known, path, f"dependency edge names unknown assembly: {consumer} -> {provider}")
        reverse[provider].add(consumer)
    seen = set(roots)
    queue = list(sorted(roots))
    while queue:
        provider = queue.pop(0)
        for consumer in sorted(reverse[provider]):
            if consumer not in seen:
                seen.add(consumer)
                queue.append(consumer)
    return seen


def _verify_topological(order, closure, edges, path):
    _need(isinstance(order, list), path, "loadOrder must be an array")
    _need(len(order) == len(set(order)) and set(order) == closure, path, "loadOrder must contain closure exactly once")
    positions = {name: index for index, name in enumerate(order)}
    for consumer, provider, _, _ in edges:
        if consumer in closure and provider in closure:
            _need(positions[provider] < positions[consumer], path,
                 f"loadOrder is not dependency-first: {provider} must precede {consumer}")


def _pins(manifest, receipt, path):
    _need(manifest.get("sourcePins") is not None and receipt.get("sourcePins") is not None, path,
         "source pins are required")
    _verify_source_pins(manifest["sourcePins"], path)
    _verify_source_pins(receipt["sourcePins"], path, manifest["sourcePins"])
    _need(_normal(manifest["sourcePins"]) == _normal(receipt["sourcePins"]), path,
         "compile/Player source pins differ from baseline")
    _need(_runtime_abi_hash(receipt["sourcePins"], path) == manifest.get("runtimeAbiHash"), path,
         "runtimeAbiHash does not match source pins")


def _verify_compile_snapshot(run: Path, patch_root: Path, patch: dict, baseline: dict, patch_path: Path,
                             patch_id: str):
    source_root = run / f"{patch_id}-compile" / "Snapshot"
    _need(source_root.is_dir() and not source_root.is_symlink(), patch_path,
         f"compile snapshot source is missing: {source_root}")
    source_receipt_path = source_root / "assembly-snapshot.json"
    sidecar_path = patch_root / "compile-snapshot-receipt.json"
    _need(sidecar_path.is_file() and not sidecar_path.is_symlink(), patch_path,
         "compile-snapshot-receipt.json sidecar is missing")
    source_receipt = _json(source_receipt_path)
    sidecar = _json(sidecar_path)
    _need(_normal(source_receipt) == _normal(sidecar), sidecar_path,
         "compile snapshot sidecar differs from the single original receipt")
    _need(source_receipt.get("schemaVersion") == 1 and source_receipt.get("kind") == "CompilePlayerScripts",
         source_receipt_path, "not a CompilePlayerScripts receipt")
    _need(_linked_claim_absent(source_receipt) and
          not (source_root / "LinkedPlayer").exists() and not (source_root / "LinkedPlayer").is_symlink(),
          source_receipt_path, "compiler snapshot cannot claim linked Player evidence")
    _need(patch.get("compileSnapshotHash") == source_receipt.get("snapshotHash"), patch_path,
         "compileSnapshotHash differs from receipt snapshotHash")
    for field in ("unityVersion", "target", "architecture"):
        _need(source_receipt.get(field) == baseline.get(field) and
             (field != "target" or source_receipt.get(field) == TARGET),
             source_receipt_path, f"compile snapshot {field} differs from baseline")
    _pins(baseline, source_receipt, source_receipt_path)
    by_name, _ = _snapshot_files(source_receipt, source_root, source_receipt_path)
    _need(_snapshot_hash(source_receipt, source_root, source_receipt_path) == source_receipt.get("snapshotHash"),
         source_receipt_path, "snapshotHash does not match the complete compile receipt")
    return {entry["name"]: entry for entry in source_receipt.get("assemblies", [])}


def _verify_patch(patch_path: Path, run: Path, baseline: dict, descriptors: dict, baseline_edges, expected_root,
                  expected_closure, expected_bundles=None):
    patch_root = patch_path.parent
    patch = _json(patch_path)
    manifest_sidecar = patch_root / "manifest.sha256"
    _need(manifest_sidecar.is_file() and not manifest_sidecar.is_symlink(), manifest_sidecar,
         "manifest SHA sidecar is missing")
    _need(manifest_sidecar.read_text().strip() == digest(patch_path), manifest_sidecar,
         "manifest SHA sidecar differs from patch-manifest.json")
    _need(patch.get("schemaVersion") == 1 and patch.get("semanticHashSchema") == 1, patch_path,
         "patch manifest schemaVersion and semanticHashSchema must be 1")
    patch_id = _name(patch.get("patchId"), patch_path, "patchId")
    _need(patch_id in {"P01", "P02", "P03", "P05"}, patch_path, "unexpected patchId")
    for field in ("baselineBuildId", "baselineManifestSha256", "unityVersion", "target", "architecture",
                  "runtimeAbiHash", "compileSnapshotHash", "bootstrapAbiHash", "baselineResourceAbiHash",
                  "resourceAbiHash", "resourceChangeLevel"):
        _string(patch.get(field), patch_path, field)
        if field == "baselineBuildId":
            _need(patch[field] == baseline.get(field), patch_path, "baselineBuildId differs from baseline")
        elif field in baseline and field not in ("resourceAbiHash",):
            _need(patch[field] == baseline[field], patch_path, f"{field} differs from baseline")
    _need(patch["baselineManifestSha256"] == baseline.get("_actualSha256"), patch_path,
         "baselineManifestSha256 does not identify the actual baseline manifest")
    _need(patch.get("unsigned") is True and patch.get("signatureAlgorithm") == "None", patch_path,
         "patch must explicitly declare unsigned/None signature")
    _need(patch.get("sourcePins") is not None and _normal(patch["sourcePins"]) == _normal(baseline.get("sourcePins")),
         patch_path, "patch source pins differ from baseline")
    resource_sidecar = patch_root / "resource-abi.json"
    _need(resource_sidecar.is_file() and not resource_sidecar.is_symlink(), resource_sidecar,
         "patch resource-abi.json sidecar is missing")
    patch_abi = _json(resource_sidecar)
    _need(patch_abi.get("schemaVersion") == 2 and _resource_abi_hash(patch_abi) == patch.get("resourceAbiHash"), resource_sidecar,
         "resourceAbiHash does not match patch resource-abi.json")
    _need(patch.get("changedRoots") == [expected_root], patch_path, "changedRoots differs from expected M02 case")
    closure_names = _names(patch.get("closure"), patch_path, "closure")
    _need(set(closure_names) == expected_closure and len(closure_names) == len(expected_closure), patch_path,
         "closure does not equal independently computed reverse dependency closure")
    current_edges = _edges(patch.get("dependencyGraph"), f"{patch_path}.dependencyGraph")
    all_edges = baseline_edges + current_edges
    _need(_closure(all_edges, {expected_root}, set(descriptors), patch_path) == expected_closure, patch_path,
         "reverse closure from current+baseline dependency edges differs from patch closure")
    _verify_topological(patch.get("loadOrder"), expected_closure, all_edges, patch_path)
    receipt_entries = _verify_compile_snapshot(run, patch_root, patch, baseline, patch_path, patch_id)
    closure = patch.get("closure")
    for index, entry in enumerate(closure):
        entry_path = f"{patch_path}.closure[{index}]"
        _need(isinstance(entry, dict), entry_path, "closure entry must be an object")
        name = _name(entry.get("name"), entry_path, "name")
        _need(name in expected_closure, entry_path, f"unexpected closure assembly: {name}")
        input_entry = receipt_entries.get(name)
        _need(input_entry is not None, entry_path, f"assembly is absent from the single compile snapshot receipt: {name}")
        dll = _relative(patch_root, entry.get("dll"), entry_path, "dll")
        _need(digest(dll) == entry.get("sha256") == input_entry.get("sha256"), entry_path,
             "closure DLL SHA-256 differs from manifest or compile snapshot")
        if entry.get("pdb"):
            _need(input_entry.get("pdbPath"), entry_path, "closure PDB is not present in compile snapshot receipt")
            pdb = _relative(patch_root, entry["pdb"], entry_path, "pdb")
            source_pdb = _relative(run / f"{patch_id}-compile" / "Snapshot", input_entry["pdbPath"], entry_path, "receipt.pdbPath")
            _need(digest(pdb) == entry.get("pdbSha256") == input_entry.get("pdbSha256") == digest(source_pdb), entry_path,
                 "closure PDB SHA-256 differs from manifest or compile snapshot")
        else:
            _need(not input_entry.get("pdbPath"), entry_path, "closure must include the compile snapshot PDB")
    if patch_id in ("P01", "P02", "P03"):
        _need(patch.get("dllOnly") is True and patch["resourceAbiHash"] == patch["baselineResourceAbiHash"], patch_path,
             "P01/P02/P03 must be DLL-only with unchanged resource ABI")
        _need(patch.get("resourceBundlesRequired") == [], patch_path, "code-only patches must require no bundles")
    else:
        _need(patch.get("dllOnly") is False and patch.get("resourceChangeLevel") == "ResourceRebuildRequired", patch_path,
             "P05 must require a resource rebuild and must not be DLL-only")
        _need(set(patch.get("resourceBundlesRequired") or ()) == {"business-scene.bundle", "versioned-prefab.bundle"} and
             len(patch.get("resourceBundlesRequired") or ()) == 2 and "versioned-data.bundle" not in patch["resourceBundlesRequired"],
             patch_path, "P05 must require exactly business-scene.bundle and versioned-prefab.bundle")
    return patch


def _verify_nunit(path: Path):
    _need(path.is_file() and not path.is_symlink() and path.stat().st_size > 0, path, "NUnit XML is missing or empty")
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as error:
        raise VerificationError(f"{path}: invalid NUnit XML: {error}") from error
    result = str(root.attrib.get("result", "")).lower()
    _need(result == "passed", path, "NUnit test-run result must be Passed")
    _need(str(root.attrib.get("failed", "0")) == "0", path, "NUnit test-run failed count must be zero")
    cases = list(root.iter())
    test_cases = [node for node in cases if node.tag.rsplit("}", 1)[-1].lower() == "test-case"]
    _need(test_cases, path, "NUnit XML contains no test cases")
    for node in test_cases:
        _need(str(node.attrib.get("result", "")).lower() == "passed", path,
             f"NUnit test case is not Passed: {node.attrib.get('fullname', node.attrib.get('name', '<unnamed>'))}")
    _need(not any(str(node.attrib.get("result", "")).lower() == "failed" for node in cases), path,
         "NUnit XML contains a failed suite or test")
    coverage = {suite: False for suite in NUNIT_SUITES}

    def visit(node, inherited_labels=()):
        labels = set(inherited_labels)
        values = " ".join(str(value) for value in node.attrib.values())
        labels.update(suite for suite in NUNIT_SUITES if suite in values)
        if node.tag.rsplit("}", 1)[-1].lower() == "test-case":
            for suite in labels:
                coverage[suite] = True
        for child in node:
            visit(child, labels)

    visit(root)
    for suite in NUNIT_SUITES:
        _need(coverage[suite], path, f"NUnit test cases do not cover {suite}")
    return {"testCases": len(test_cases), "suitesCovered": list(NUNIT_SUITES)}


def verify(editor_result: Path, nunit_results: Path, m01_baseline_root: Path):
    report, run, baseline_path, artifacts = _verify_editor_report(editor_result)
    baseline_root = _root(baseline_path.parent, "baseline artifact root")
    baseline = _json(baseline_path)
    descriptors = _verify_sidecar_manifest(baseline_root, baseline, baseline_path)
    baseline["_actualSha256"] = digest(baseline_path)
    receipt, _, _ = _verify_player_snapshot(baseline_root, baseline, descriptors, baseline_path)
    _pins(baseline, receipt, baseline_path)
    m01_root = _root(m01_baseline_root, "--m01-baseline-root")
    _verify_resource_baseline(baseline_root, baseline, baseline_path, m01_root)
    _verify_bundles(m01_root, baseline, baseline_path)
    baseline_edges = _edges(baseline.get("dependencyGraph"), f"{baseline_path}.dependencyGraph")
    for consumer, provider, _, _ in baseline_edges:
        _need(descriptors.get(consumer, {}).get("classification") != 5 and descriptors.get(provider, {}).get("classification") != 5,
             baseline_path, f"BuildFiltered assembly participates in runtime dependency graph: {consumer} -> {provider}")
    _need(report.get("unityVersion") == baseline["unityVersion"], editor_result,
         "editor report Unity version differs from baseline")
    _need(report.get("target") == baseline["target"] == TARGET, editor_result,
         "editor report target differs from baseline")
    expected = {
        "P01": (INTERNAL, {INTERNAL}),
        "P02": (EXTENSIBILITY, {EXTENSIBILITY, INTERNAL, "AssemblyShadowDemo.ExtensibilityConsumer"}),
        "P03": (CONTRACTS, set(CANDIDATES)),
        "P05": (INTERNAL, {INTERNAL}),
    }
    patches = {}
    for patch_id, (root, closure) in expected.items():
        patch_path = artifacts["P05-requires-bundles"] if patch_id == "P05" else artifacts[patch_id]
        patch = _verify_patch(patch_path, run, baseline, descriptors, baseline_edges, root, closure)
        patches[patch_id] = patch
    repeat = artifacts["P01-repeat"]
    repeat_sidecar = repeat.parent / "manifest.sha256"
    _need(repeat_sidecar.is_file() and repeat_sidecar.read_text().strip() == digest(repeat), repeat_sidecar,
         "P01 repeat manifest SHA sidecar is missing or stale")
    _need(repeat.read_bytes() == artifacts["P01"].read_bytes(), repeat,
         "P01 repeat patch manifest is not byte-identical")
    baseline_repeat = run / "baseline-repeat" / "baseline-manifest.json"
    _need(baseline_repeat.is_file() and not baseline_repeat.is_symlink(), baseline_repeat,
         "baseline-repeat manifest is missing from actual report runDirectory")
    _need(baseline_repeat.read_bytes() == baseline_path.read_bytes(), baseline_repeat,
         "baseline-repeat manifest is not byte-identical to the actual baseline manifest")
    nunit = _verify_nunit(nunit_results)
    return {
        "milestone": "M02",
        "resultPassed": True,
        "unityVersion": baseline["unityVersion"],
        "target": baseline["target"],
        "baselineManifestSha256": baseline["_actualSha256"],
        "patches": {name: {"changedRoots": patch["changedRoots"], "closure": patch["loadOrder"], "dllOnly": patch["dllOnly"]}
                    for name, patch in patches.items()},
        "nunit": nunit,
        "evidence": "SHA-256 bytes, Unity AssemblyShadow manifest/snapshot metadata, and NUnit test evidence",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--editor-result", type=Path, required=True)
    parser.add_argument("--nunit-results", type=Path, required=True)
    parser.add_argument("--m01-baseline-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = verify(args.editor_result.resolve(), args.nunit_results.resolve(), args.m01_baseline_root.resolve())
        output = json.dumps(result, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
        print(output, end="")
        return 0
    except (VerificationError, OSError, ValueError, KeyError, TypeError) as error:
        print("[FAIL] " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
