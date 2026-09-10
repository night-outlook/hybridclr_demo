#!/usr/bin/env python3
"""Launch one fresh H1 count diagnostic Player cell and retain provenance."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import plistlib
from pathlib import Path
import subprocess
import sys
import time
import uuid


HERE = Path(__file__).resolve().parent
MAX_PLAYER_BYTES = 512 * 1024 * 1024
MAX_TIMEOUT_SECONDS = 3600
AUDIT_KINDS = {
    "parameters": "H1CountFixtureShapeAudit",
    "nested": "H1NestedFixtureShapeAudit",
}


def require(condition: object, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "Expected regular file: " + str(path))
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def safe_digest(path: Path | str) -> tuple[str, str]:
    """Observe an input without allowing a bad path to suppress the receipt."""
    try:
        return digest(canonical_file(path, "observed input")), ""
    except Exception as error:
        return "", str(error)


def canonical_file(value: Path | str, label: str) -> Path:
    path = Path(value)
    require(path.is_absolute() and path == path.resolve() and path.is_file() and
            not path.is_symlink(), label + " must be an existing canonical file")
    for parent in path.parents:
        require(not parent.is_symlink() and parent == parent.resolve(),
                label + " has a symlinked or noncanonical parent")
    return path


def canonical_directory(value: Path | str, label: str) -> Path:
    path = Path(value)
    require(path.is_absolute() and path == path.resolve() and path.is_dir() and
            not path.is_symlink(), label + " must be a canonical directory")
    for parent in path.parents:
        require(not parent.is_symlink() and parent == parent.resolve(),
                label + " has a symlinked or noncanonical parent")
    return path


def canonical_new_output(value: Path | str, project: Path) -> Path:
    path = Path(value)
    root = project / "_temp/AssemblyShadow"
    require(path.is_absolute() and path == path.resolve() and not path.exists() and
            not path.is_symlink(), "output root must be a new canonical absolute path")
    require(root.is_dir() and not root.is_symlink() and root == root.resolve(),
            "project _temp/AssemblyShadow directory is unavailable")
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ValueError("output root must be under project/_temp/AssemblyShadow") from error
    require(path.parent.is_dir() and not path.parent.is_symlink() and
            path.parent == path.parent.resolve(),
            "output root parent must be an existing canonical directory")
    return path


def read_json_bytes_captured(path: Path, label: str) -> tuple[dict, bytes, str]:
    with path.open("rb") as stream:
        data = stream.read(MAX_PLAYER_BYTES + 1)
    require(0 < len(data) <= MAX_PLAYER_BYTES, label + " is empty or oversized")
    try:
        value = json.loads(data.decode("utf-8-sig"))
    except (UnicodeError, ValueError) as error:
        raise ValueError(label + " is not valid JSON: " + str(error)) from error
    require(type(value) is dict, label + " must contain a JSON object")
    return value, data, hashlib.sha256(data).hexdigest()


def read_json_captured(path: Path, label: str) -> tuple[dict, str]:
    value, _, captured_hash = read_json_bytes_captured(path, label)
    return value, captured_hash


def read_json(path: Path, label: str) -> dict:
    return read_json_captured(path, label)[0]


def collect_tree(root: Path, label: str) -> set[Path]:
    root = canonical_directory(root, label)
    files: set[Path] = set()
    for path in root.rglob("*"):
        require(not path.is_symlink(), "Symlink in " + label + ": " + str(path))
        if path.is_file():
            require(path.stat().st_size <= MAX_PLAYER_BYTES,
                    label + " contains an oversized file: " + str(path))
            files.add(path.resolve(strict=True))
    return files


def tree_sets(roots: dict[str, Path]) -> dict[str, set[Path]]:
    return {label: collect_tree(root, label) for label, root in roots.items()}


def tree_hashes(roots: dict[str, Path]) -> tuple[dict[str, str], list[str]]:
    hashes: dict[str, str] = {}
    errors: list[str] = []
    for label, root in roots.items():
        try:
            files = collect_tree(root, label)
        except Exception as error:
            errors.append(f"{label}: {error}")
            continue
        for path in sorted(files):
            value, observation_error = safe_digest(path)
            if observation_error:
                errors.append(observation_error)
            else:
                hashes[str(path)] = value
    return hashes, errors


def classify_exit(exit_code: int | None, launcher_initiated_termination: bool = False) -> dict[str, bool]:
    """A nonzero exit is a process failure; owned termination is not a crash."""
    failed = exit_code is not None and exit_code != 0
    signal = exit_code is not None and exit_code < 0
    return {"processFailed": failed, "signalTerminated": signal,
            "launcherInitiatedTermination": launcher_initiated_termination,
            "crashed": signal and not launcher_initiated_termination}


def compare_observations(before: dict[str, str], after: dict[str, str],
                         before_sets: dict[str, set[Path]],
                         after_sets: dict[str, set[Path]]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    for label in sorted(set(before_sets) | set(after_sets)):
        expected = before_sets.get(label, set())
        actual = after_sets.get(label, set())
        if expected != actual:
            added = sorted(str(path) for path in actual - expected)
            removed = sorted(str(path) for path in expected - actual)
            errors.append(f"{label} inventory changed: added={added}, removed={removed}")
    if before != after:
        errors.append("validated input hash set or value changed during launch")
    return not errors, errors


def require_expected_hashes(observed: dict[str, str], expected: dict[str, str]) -> None:
    for path, expected_hash in sorted(expected.items()):
        require(observed.get(path) == expected_hash,
                "validated input changed before launch: " + path)


def mode_for(family: str, path: str, feature_enabled: bool) -> str:
    require(family in ("parameters", "nested"), "family must be parameters or nested")
    require(path in ("ordinary", "shadow"), "path must be ordinary or shadow")
    require(path != "shadow" or feature_enabled,
            "shadow path requires an Assembly Shadow enabled diagnostic build")
    return path.capitalize() + ("On" if feature_enabled else "Off")


def build_player_command(executable: Path, family: str, path: str, case_id: str,
                        fixture: Path, fixture_sha256: str, result_path: Path,
                        early_result_path: Path | None = None, expected_outcome: str = "",
                        expected_count: int = 0, baseline_build_id: str = "",
                        runtime_abi_hash: str = "", log_path: Path | None = None) -> list[str]:
    # Keep the pre-receipt call shape available to focused launcher tests and
    # older tooling; production shadow launches always provide every binding.
    if log_path is None and expected_outcome == "" and expected_count == 0 and not baseline_build_id and not runtime_abi_hash:
        log_path, early_result_path = early_result_path, None
    require(log_path is not None, "Player log path is required")
    return [
        str(executable),
        "-batchmode", "-nographics",
        "-shadowH1Family", family,
        "-shadowH1Path", path,
        "-shadowH1Case", case_id,
        "-shadowH1Fixture", str(fixture),
        "-shadowH1FixtureSha256", fixture_sha256,
        "-shadowH1Result", str(result_path),
        *( [] if early_result_path is None else ["-shadowH1EarlyResult", str(early_result_path),
          "-shadowH1ExpectedOutcome", expected_outcome, "-shadowH1ExpectedCount", str(expected_count),
          "-shadowH1BaselineBuildId", baseline_build_id, "-shadowH1RuntimeAbiHash", runtime_abi_hash] ),
        "-logFile", str(log_path),
    ]


def load_manifest_tools(family: str):
    module_name = "h1_count_manifest" if family == "parameters" else "h1_nested_manifest"
    return importlib.import_module(module_name)


def validate_manifest_and_audit(manifest_path: Path, audit_path: Path, family: str,
                                case_id: str, path_name: str,
                                validated_hashes: dict[str, str] | None = None) -> tuple[dict, dict, dict, Path]:
    validated_hashes = validated_hashes if validated_hashes is not None else {}
    tool = load_manifest_tools(family)
    manifest, manifest_bytes, canonical_manifest = tool.load_manifest(manifest_path)
    bind_expected_hash(validated_hashes, str(canonical_manifest), hashlib.sha256(manifest_bytes).hexdigest())
    tool.validate_manifest_structure(manifest)
    require(manifest["family"] == family and manifest["caseSet"] == "all",
            "fixture manifest family/case set differs from the requested cell")
    cases = [case for case in manifest["cases"] if case.get("caseId") == case_id]
    require(len(cases) == 1, "fixture case is absent or duplicated in the manifest: " + case_id)
    case = cases[0]
    artifact = case[path_name]
    fixture = canonical_file(artifact["path"], "fixture DLL")
    require(fixture == canonical_manifest.parent / path_name / (case_id + ".dll"),
            "fixture DLL is outside the manifest's canonical flavor directory")
    fixture_sha256 = digest(fixture)
    require(fixture_sha256 == artifact["sha256"], "fixture DLL hash differs from manifest")

    audit, audit_hash = read_json_captured(audit_path, "fixture audit")
    bind_expected_hash(validated_hashes, str(audit_path), audit_hash)
    require(audit.get("schemaVersion") == 1 and
            audit.get("kind") == AUDIT_KINDS[family] and
            audit.get("result") == "Passed" and audit.get("family") == family and
            audit.get("caseSet") == "all", "fixture audit is not a passed family audit")
    require(case_id in audit.get("requestedCaseIds", []) and
            case_id in audit.get("executedCaseIds", []),
            "fixture audit does not cover the requested case")
    binding = audit.get("sourceBinding")
    require(type(binding) is dict, "fixture audit source binding is missing")
    require(binding.get("manifestPath") == str(canonical_manifest) and
            binding.get("manifestSha256") == hashlib.sha256(manifest_bytes).hexdigest(),
            "fixture audit is bound to a different fixture manifest")
    for path_key, hash_key in (
            ("coreAuditPath", "coreAuditSha256"),
            ("manifestToolPath", "manifestToolSha256"),
            ("sharedManifestPath", "sharedManifestSha256")):
        if path_key not in binding:
            require(family == "parameters" and path_key == "sharedManifestPath",
                    "fixture audit source binding is incomplete")
            continue
        source = canonical_file(binding[path_key], "fixture audit source")
        source_hash = digest(source)
        require(source_hash == binding.get(hash_key),
                "fixture audit source hash differs: " + str(source))
        bind_expected_hash(validated_hashes, str(source), source_hash)
    audit_case = next((item for item in audit.get("cases", [])
                       if item.get("caseId") == case_id), None)
    require(type(audit_case) is dict and type(audit_case.get("observed")) is dict,
            "fixture audit case observation is missing")
    observed = audit_case["observed"].get(path_name)
    require(type(observed) is dict and observed.get("assemblyName") == artifact["name"],
            "fixture audit observation does not match the selected DLL")
    bind_expected_hash(validated_hashes, str(fixture), fixture_sha256)
    for path_value, expected_hash in manifest.get("generator", {}).get("inputHashesBefore", {}).items():
        bind_expected_hash(validated_hashes, str(canonical_file(path_value, "fixture generator input")), expected_hash)
    return manifest, case, audit, fixture


def _sha(value: object, label: str) -> str:
    require(isinstance(value, str) and len(value) == 64 and
            all(character in "0123456789abcdefABCDEF" for character in value),
            label + " must be a SHA-256")
    return value.lower()


def _inventory_hash(entries: list[dict]) -> str:
    text = "\n".join(entry["path"] + "\0" + entry["source"] + "\0" + entry["sha256"]
                     for entry in sorted(entries, key=lambda item: item["path"]))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _native_inventory(root: Path, label: str, install_receipt: dict | None = None) -> tuple[list[dict], set[Path]]:
    files = collect_tree(root, label)
    relative = {str(path.relative_to(root)).replace("\\", "/"): path for path in files}
    entries: list[dict] = []
    if install_receipt is not None:
        expected: dict[str, str] = {}
        for item in install_receipt.get("sourceFileHashes", []):
            require(type(item) is dict and isinstance(item.get("path"), str) and
                    isinstance(item.get("source"), str),
                    "native install receipt has an invalid source entry")
            _sha(item.get("sha256"), "native install receipt source hash")
            require(item["path"] not in expected, "native install receipt has duplicate source paths")
            expected[item["path"]] = item["source"]
        generated_paths = (
            "hybridclr/generated/AssemblyManifest.cpp",
            "hybridclr/generated/MethodBridge.cpp",
            "hybridclr/generated/UnityVersion.h",
            "hybridclr/generated/libil2cpp-version.txt")
        exclusions = install_receipt.get("generatedFileExclusions")
        require(isinstance(exclusions, list) and len(exclusions) == len(generated_paths) and
                all(isinstance(path, str) for path in exclusions) and set(exclusions) == set(generated_paths),
                "native generated exclusions differ from the fixed four-file contract")
        for generated in generated_paths:
            expected[generated] = "generated"
        expected["assembly-shadow-install.json"] = "install-receipt"
        require(set(relative) == set(expected),
                "installed native inventory contains missing or unexpected paths")
        for path, source in expected.items():
            actual_hash = digest(relative[path])
            if source not in ("generated", "install-receipt"):
                claimed = next(item for item in install_receipt["sourceFileHashes"]
                               if item["path"] == path)
                require(actual_hash == claimed["sha256"],
                        "installed native source hash differs: " + path)
            entries.append({"path": path, "source": source, "sha256": actual_hash})
    else:
        for path in sorted(relative):
            entries.append({"path": path, "source": "external", "sha256": digest(relative[path])})
        require(entries, label + " inventory is empty")
    entries.sort(key=lambda item: item["path"])
    return entries, files


def validate_native_provenance(provenance: object, build: dict, project: Path,
                               validated_hashes: dict[str, str] | None = None) -> tuple[set[Path], dict[str, Path]]:
    require(type(provenance) is dict, "diagnostic native provenance is missing")
    validated_hashes = validated_hashes if validated_hashes is not None else {}
    paths: set[Path] = set()
    roots: dict[str, Path] = {}
    require(provenance.get("schemaVersion") == 2,
            "native provenance requires immutable snapshot schema 2")
    snapshot_root = canonical_directory(provenance.get("snapshotRoot"), "native provenance snapshot")
    require(snapshot_root.is_relative_to(project / "_temp/AssemblyShadow"),
            "native provenance snapshot is outside project evidence storage")
    snapshot_files = collect_tree(snapshot_root, "native provenance snapshot")
    snapshot_entries = sorted(({"path": path.relative_to(snapshot_root).as_posix(),
                                "source": "snapshot", "sha256": digest(path)}
                               for path in snapshot_files), key=lambda item: item["path"])
    require(snapshot_entries and provenance.get("snapshotFiles") == snapshot_entries and
            provenance.get("snapshotInventorySha256") == _inventory_hash(snapshot_entries),
            "native provenance snapshot inventory differs")
    for entry in snapshot_entries:
        bind_expected_hash(validated_hashes, str(snapshot_root / entry["path"]), entry["sha256"])
    paths.update(snapshot_files)
    roots["nativeProvenanceSnapshot"] = snapshot_root
    for field in ("sourcePinFile", "verificationToolPath", "verificationSupportToolPath",
                  "installReceiptPath", "pythonExecutable"):
        path = canonical_file(provenance.get(field), "native provenance " + field)
        if field != "pythonExecutable":
            require(path.is_relative_to(snapshot_root), "native provenance " + field + " is outside the snapshot")
        paths.add(path)
    require(provenance["sourcePinFile"] == build["sourcePinFile"],
            "native provenance source pin differs from the build receipt")
    require(digest(canonical_file(provenance["sourcePinFile"], "source pin")) ==
            build["sourcePinSha256"], "source pin hash differs from the build receipt")
    bind_expected_hash(validated_hashes, str(canonical_file(provenance["sourcePinFile"], "source pin")), build["sourcePinSha256"])
    for field, hash_field in (("verificationToolPath", "verificationToolSha256"),
                              ("verificationSupportToolPath", "verificationSupportToolSha256"),
                              ("installReceiptPath", "installReceiptSha256"),
                              ("pythonExecutable", "pythonExecutableSha256")):
        path = canonical_file(provenance[field], "native provenance " + field)
        expected_hash = provenance.get(hash_field)
        require(digest(path) == expected_hash,
                "native provenance hash differs for " + field)
        bind_expected_hash(validated_hashes, str(path), expected_hash)
        paths.add(path)
    require(provenance.get("verificationExitCode") == 0,
            "native provenance verification did not succeed")
    install_receipt_path = canonical_file(provenance["installReceiptPath"], "native install receipt")
    install_receipt, install_receipt_hash = read_json_captured(install_receipt_path, "native install receipt")
    bind_expected_hash(validated_hashes, str(install_receipt_path), install_receipt_hash)
    installed_root = canonical_directory(provenance.get("installedRoot"), "installed native root")
    external_root = canonical_directory(provenance.get("externalRoot"), "external native root")
    require(installed_root.is_relative_to(snapshot_root) and external_root.is_relative_to(snapshot_root),
            "native inventory roots are outside the immutable snapshot")
    require(provenance.get("sourcePinSha256") == build["sourcePinSha256"],
            "native snapshot source pin hash differs from the build")
    require(install_receipt_path == installed_root / "assembly-shadow-install.json",
            "native install receipt is outside the installed native root")
    roots["installedNative"] = installed_root
    roots["externalNative"] = external_root
    installed_entries, installed_files = _native_inventory(installed_root, "installed native", install_receipt)
    external_entries, external_files = _native_inventory(external_root, "external native")
    require(provenance.get("installedInventorySha256") == _inventory_hash(installed_entries) and
            provenance.get("externalInventorySha256") == _inventory_hash(external_entries),
            "native provenance inventory hash differs")
    for field, actual in (("installedFiles", installed_entries), ("externalFiles", external_entries)):
        claimed = provenance.get(field)
        require(isinstance(claimed, list), "native provenance " + field + " is missing")
        normalized = sorted(claimed, key=lambda item: item.get("path", "") if isinstance(item, dict) else "")
        require(normalized == actual, "native provenance " + field + " differs from actual inventory")
    paths.update(installed_files)
    paths.update(external_files)
    paths.update({installed_root / "assembly-shadow-install.json"})
    for entry, path in ((installed_entries, installed_root), (external_entries, external_root)):
        for item in entry:
            bind_expected_hash(validated_hashes, str(path / item["path"]), item["sha256"])
    return paths, roots


def bind_expected_hash(expected: dict[str, str], path: str, observed: str) -> None:
    """An overlapping observation must confirm, never replace, prior evidence."""
    require(path not in expected or expected[path] == observed,
            "validated input hash conflict: " + path)
    expected[path] = observed


def validate_snapshot(build: dict, project: Path,
                      validated_hashes: dict[str, str] | None = None) -> tuple[set[Path], Path]:
    validated_hashes = validated_hashes if validated_hashes is not None else {}
    root = canonical_directory(build["inputSnapshot"], "Player input snapshot")
    receipt_path = canonical_file(root / "assembly-snapshot.json", "Player input snapshot receipt")
    snapshot, snapshot_receipt_hash = read_json_captured(receipt_path, "Player input snapshot receipt")
    bind_expected_hash(validated_hashes, str(receipt_path), snapshot_receipt_hash)
    require(snapshot.get("kind") == "PlayerBuildInputs" and snapshot.get("snapshotHash") == build["inputSnapshotHash"],
            "builder inputSnapshotHash is not bound to the captured snapshot")
    require(snapshot.get("buildGuid") == build["buildGuid"] and
            snapshot.get("playerOutput") == build["playerOutput"] and
            snapshot.get("nativeLibraryPath") == build["nativeLibraryPath"] and
            snapshot.get("nativeLibrarySha256") == build["nativeLibrarySha256"],
            "builder snapshot identity differs from the build receipt")
    m03 = importlib.import_module("m03_results")
    try:
        actual_hash = m03._snapshot_hash(snapshot, root, receipt_path)
    except Exception as error:
        raise ValueError("builder input snapshot cannot be independently hashed: " + str(error)) from error
    require(actual_hash == build["inputSnapshotHash"],
            "builder inputSnapshotHash differs from the canonical snapshot hash")
    pin = canonical_file(build["sourcePinFile"], "source pin")
    require(pin.is_relative_to(project) and digest(pin) == build["sourcePinSha256"],
            "builder source pin is outside the project or has a stale hash")
    require(pin.read_text(encoding="utf-8") == build["sourcePinsJson"],
            "builder sourcePinsJson differs from source pin file")
    snapshot_files = collect_tree(root, "Player input snapshot")
    for path in snapshot_files:
        bind_expected_hash(validated_hashes, str(path), digest(path))
    return snapshot_files, root


def validate_player_layout(player_output: Path, executable: Path, native_library: Path,
                           native_metadata: Path) -> None:
    """Bind every launched binary to the actual macOS app bundle layout."""
    require(executable.is_relative_to(player_output), "Player executable is outside the Player app")
    info_path = canonical_file(player_output / "Contents/Info.plist", "Player Info.plist")
    try:
        info = plistlib.loads(info_path.read_bytes())
    except Exception as error:
        raise ValueError("Player Info.plist is unreadable: " + str(error)) from error
    require(isinstance(info.get("CFBundleExecutable"), str) and
            executable == player_output / "Contents/MacOS" / info["CFBundleExecutable"],
            "Player executable does not match the app bundle definition")
    require(native_library.is_relative_to(player_output) and native_metadata.is_relative_to(player_output),
            "native library and metadata must be inside the Player app")
    metadata_candidates = []
    for candidate in player_output.rglob("global-metadata.dat"):
        require(not candidate.is_symlink(), "Player metadata cannot be a symlink")
        if candidate.is_file():
            metadata_candidates.append(candidate.resolve(strict=True))
    require(len(metadata_candidates) == 1 and native_metadata == metadata_candidates[0],
            "native metadata path does not match the unique actual Player metadata file")


def validate_build_receipt(receipt_path: Path, project: Path, family: str, path_name: str,
                           validated_hashes: dict[str, str] | None = None) -> tuple[dict, set[Path], dict[str, Path]]:
    validated_hashes = validated_hashes if validated_hashes is not None else {}
    receipt, receipt_hash = read_json_captured(receipt_path, "diagnostic build receipt")
    bind_expected_hash(validated_hashes, str(receipt_path), receipt_hash)
    require(receipt.get("schemaVersion") == 1 and
            receipt.get("kind") == "H1CountDiagnosticPlayerBuild" and
            receipt.get("diagnosticOnly") is True,
            "diagnostic build receipt header differs")
    require(receipt.get("cppConfiguration") in ("Debug", "Release"),
            "diagnostic build receipt C++ configuration is invalid")
    feature_enabled = receipt.get("featureEnabled")
    require(type(feature_enabled) is bool, "diagnostic build featureEnabled must be boolean")
    mode_for(family, path_name, feature_enabled)
    require(receipt.get("target") == "StandaloneOSX" and receipt.get("architecture") == "arm64",
            "diagnostic build target is not the pinned StandaloneOSX arm64 Player")
    expected_feature_flag = "HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=" + ("1" if feature_enabled else "0")
    require(isinstance(receipt.get("nativeArguments"), str) and
            expected_feature_flag in receipt["nativeArguments"] and
            "-DHYBRIDCLR_H1_COUNT_DIAGNOSTICS=1" in receipt["nativeArguments"],
            "diagnostic native feature/diagnostic compiler flags are not explicit")
    require("ASSEMBLY_SHADOW_H1_COUNT_DIAGNOSTICS" in receipt.get("extraScriptingDefines", []) and
            "ASSEMBLY_SHADOW_R01B_DIAGNOSTICS" in receipt.get("extraScriptingDefines", []),
            "diagnostic scripting defines are incomplete")
    for field in ("baselineBuildId", "runtimeAbiHash", "buildGuid", "playerOutput",
                  "playerExecutable", "nativeLibraryPath", "nativeMetadataPath",
                  "inputSnapshot", "inputSnapshotHash", "sourcePinFile", "sourcePinSha256",
                  "sourcePinsJson"):
        require(isinstance(receipt.get(field), str) and receipt[field],
                "diagnostic build receipt field is missing: " + field)
    try:
        uuid.UUID(receipt["buildGuid"])
    except (ValueError, AttributeError) as error:
        raise ValueError("diagnostic build receipt buildGuid is not a UUID") from error
    player_output = canonical_directory(Path(receipt["playerOutput"]), "diagnostic Player output")
    require(player_output.suffix == ".app", "diagnostic Player output is not a macOS app")
    executable = canonical_file(receipt["playerExecutable"], "diagnostic Player executable")
    native_library = canonical_file(receipt["nativeLibraryPath"], "native library")
    native_metadata = canonical_file(receipt["nativeMetadataPath"], "native metadata")
    validate_player_layout(player_output, executable, native_library, native_metadata)
    for field in ("playerExecutableSha256", "nativeLibrarySha256", "nativeMetadataSha256",
                  "sourcePinSha256", "inputSnapshotHash"):
        _sha(receipt.get(field), "diagnostic build receipt " + field)
    require(digest(executable) == receipt.get("playerExecutableSha256"),
            "diagnostic executable hash differs from build receipt")
    require(digest(native_library) == receipt.get("nativeLibrarySha256"),
            "diagnostic native library hash differs from build receipt")
    require(digest(native_metadata) == receipt.get("nativeMetadataSha256"),
            "diagnostic native metadata hash differs from build receipt")
    require(receipt_path.is_absolute() and receipt_path == receipt_path.resolve(),
            "diagnostic build receipt path must be canonical")
    bind_expected_hash(validated_hashes, str(executable), receipt["playerExecutableSha256"])
    bind_expected_hash(validated_hashes, str(native_library), receipt["nativeLibrarySha256"])
    bind_expected_hash(validated_hashes, str(native_metadata), receipt["nativeMetadataSha256"])
    snapshot_inputs, snapshot_root = validate_snapshot(receipt, project, validated_hashes)
    provenance_inputs, provenance_roots = validate_native_provenance(
        receipt.get("nativeProvenance"), receipt, project, validated_hashes)
    inputs = {receipt_path, executable, native_library, native_metadata}
    player_files = collect_tree(player_output, "diagnostic Player output")
    for path in player_files:
        bind_expected_hash(validated_hashes, str(path), digest(path))
    inputs.update(player_files)
    inputs.update(snapshot_inputs)
    inputs.update(provenance_inputs)
    generated_inputs = receipt.get("generatedBuildInputs")
    expected_sources = {"Assets/AssemblyShadowR01BDiagnostics/Scenes/H1CountDiagnostic.unity",
                        "Assets/AssemblyShadowR01BDiagnostics/Scenes/H1CountDiagnostic.unity.meta"}
    require(isinstance(generated_inputs, list) and len(generated_inputs) == 2 and
            all(type(item) is dict for item in generated_inputs) and
            {item.get("sourcePath") for item in generated_inputs} == expected_sources,
            "generated build input inventory must contain the diagnostic scene and meta")
    for item in generated_inputs:
        require(item.get("path") == "GeneratedBuildInputs/" + Path(item["sourcePath"]).name,
                "generated build input path differs from the immutable build snapshot")
        generated_path = canonical_file(snapshot_root / item["path"], "generated build input")
        require(generated_path.is_relative_to(snapshot_root),
                "generated build input is outside the snapshot")
        expected_hash = _sha(item.get("sha256"), "generated build input hash")
        require(digest(generated_path) == expected_hash,
                "generated build input hash differs: " + str(generated_path))
        bind_expected_hash(validated_hashes, str(generated_path), expected_hash)
        inputs.add(generated_path)
    inventory_roots = {"playerOutput": player_output, "inputSnapshot": snapshot_root}
    inventory_roots.update(provenance_roots)
    return receipt, inputs, inventory_roots


def validate_result(result: dict, result_path: Path, process_id: int, build: dict,
                    family: str, path_name: str, case: dict, fixture: Path,
                    fixture_sha256: str) -> dict:
    expected = case["expected"]
    semantic = {
        "resultKind": result.get("kind") == "H1CountDiagnosticResult",
        "schemaVersion": result.get("schemaVersion") == 1,
        "resultPath": result.get("resultPath") == str(result_path),
        "processId": result.get("processId") == process_id,
        "buildGuid": result.get("buildGuid") == build["buildGuid"],
        "family": result.get("family") == family,
        "path": result.get("path") == path_name,
        "caseId": result.get("caseId") == case["caseId"],
        "expectedCount": result.get("expectedCount") == case["count"],
        "fixturePath": result.get("fixturePath") == str(fixture),
        "fixtureSha256": result.get("inputHashBefore") == fixture_sha256 and
                         result.get("inputHashAfter") == fixture_sha256 and
                         isinstance(result.get("fixtureSha256Expected"), str) and
                         result["fixtureSha256Expected"].lower() == fixture_sha256,
        "expectedOutcome": result.get("expectedOutcome") == expected,
        "featureEnabled": result.get("expectedFeatureEnabled") == build["featureEnabled"],
        "cppConfiguration": result.get("expectedCppConfiguration") == build["cppConfiguration"],
        "operationOutcome": (result.get("operationSucceeded") is True
                             if expected == "Accepted" else
                             result.get("observedControlledRejection") is True),
    }
    semantic["passed"] = all(semantic.values()) and result.get("result") == "Passed"
    return semantic


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--build-receipt", required=True, type=Path)
    parser.add_argument("--fixture-manifest", required=True, type=Path)
    parser.add_argument("--fixture-audit", required=True, type=Path)
    parser.add_argument("--family", required=True, choices=("parameters", "nested"))
    parser.add_argument("--path", required=True, choices=("ordinary", "shadow"))
    parser.add_argument("--case", dest="case_id", required=True)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)

    run_id = str(uuid.uuid4())
    project = canonical_directory(args.project_root, "project root")
    require((project / "Assets/AssemblyShadowDemo").is_dir(),
            "project root is not the Assembly Shadow demo")
    output_root = canonical_new_output(args.output_root, project)
    require(1 <= args.timeout <= MAX_TIMEOUT_SECONDS, "timeout must be in 1..3600 seconds")
    output_root.mkdir()
    result_path = output_root / "h1-count-diagnostic-result.json"
    early_result_path = output_root / "h1-count-early-result.json"
    unity_log = output_root / "h1-count-diagnostic.unity.log"
    console_log = output_root / "h1-count-diagnostic.console.log"
    receipt_path = output_root / "h1-count-player-launch.json"
    immutable: set[Path] = set()
    before: dict[str, str] = {}
    after: dict[str, str] = {}
    validated_hashes: dict[str, str] = {}
    before_sets: dict[str, set[Path]] = {}
    after_sets: dict[str, set[Path]] = {}
    observation_errors: list[str] = []
    inventory_roots: dict[str, Path] = {}
    build = None
    fixture = None
    case = None
    manifest_path = Path(args.fixture_manifest)
    audit_path = Path(args.fixture_audit)
    build_path = Path(args.build_receipt)
    process_id = None
    exit_code = None
    timed_out = False
    launcher_initiated_termination = False
    result = None
    early = None
    early_checks = {"passed": False, "error": "not started"}
    expected_startup_rejection = False
    identity_checks = {"passed": False, "error": "not started"}
    error = ""
    command: list[str] = []
    started_at = time.time()
    try:
        manifest_path = canonical_file(args.fixture_manifest, "fixture manifest")
        audit_path = canonical_file(args.fixture_audit, "fixture audit")
        build_path = canonical_file(args.build_receipt, "diagnostic build receipt")
        manifest, case, audit, fixture = validate_manifest_and_audit(
            manifest_path, audit_path, args.family, args.case_id, args.path, validated_hashes)
        build, build_inputs, inventory_roots = validate_build_receipt(
            build_path, project, args.family, args.path, validated_hashes)
        immutable.update({manifest_path, audit_path, build_path, fixture})
        binding = audit["sourceBinding"]
        for path_key in ("coreAuditPath", "manifestToolPath", "sharedManifestPath"):
            if path_key in binding:
                immutable.add(canonical_file(binding[path_key], "fixture audit source"))
        for path_value in manifest.get("generator", {}).get("inputHashesBefore", {}):
            immutable.add(canonical_file(path_value, "fixture generator input"))
        immutable.update(build_inputs)
        before_sets = tree_sets(inventory_roots)
        before = {str(path): digest(path) for path in sorted(immutable)}
        tree_before, tree_errors = tree_hashes(inventory_roots)
        observation_errors.extend(tree_errors)
        before.update(tree_before)
        require_expected_hashes(before, validated_hashes)
        if observation_errors:
            raise ValueError("input observation failed: " + "; ".join(observation_errors))
        fixture_sha256 = before[str(fixture)]
        command = build_player_command(Path(build["playerExecutable"]), args.family, args.path,
                                       args.case_id, fixture, fixture_sha256, result_path,
                                       early_result_path, case["expected"], case["count"],
                                       build["baselineBuildId"], build["runtimeAbiHash"], unity_log)
        with console_log.open("x", encoding="utf-8") as console:
            process = subprocess.Popen(command, cwd=project, stdin=subprocess.DEVNULL,
                                       stdout=console, stderr=subprocess.STDOUT)
            process_id = process.pid
            try:
                exit_code = process.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                launcher_initiated_termination = True
                process.terminate()
                try:
                    exit_code = process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    exit_code = process.wait(timeout=15)
        expected_startup_rejection = args.path == "shadow" and case["expected"] == "ControlledRejected"
        if early_result_path.is_file() and not early_result_path.is_symlink():
            early, early_bytes, _ = read_json_bytes_captured(early_result_path, "early startup receipt")
            sys.path.insert(0, str(HERE))
            from h1_count_results import verify_early_receipt_document
            early_checks = verify_early_receipt_document(
                early, early_bytes,
                {"family": args.family, "caseId": args.case_id,
                 "pathName": "Shadow-ON", "featureEnabled": build["featureEnabled"]},
                build=build, fixture=fixture, fixture_sha256=fixture_sha256,
                expected_result_path=early_result_path)
            if not expected_startup_rejection and args.path != "shadow":
                raise ValueError("ordinary launch unexpectedly produced an early startup receipt")
        elif args.path == "shadow":
            raise ValueError("shadow launch did not produce its authenticated early startup receipt")
        if result_path.is_file() and not result_path.is_symlink():
            result = read_json(result_path, "diagnostic result")
            if expected_startup_rejection:
                raise ValueError("rejected shadow startup unexpectedly reached the scene runner")
            identity_checks = validate_result(result, result_path, process_id, build, args.family,
                                              args.path, case, fixture, fixture_sha256)
        else:
            identity_checks = {"passed": expected_startup_rejection, "missingResult": True}
        if timed_out:
            error = "diagnostic Player timed out"
        elif expected_startup_rejection:
            if early_checks.get("accepted") is not False or early_checks.get("callbackReturnCode") != 1 or exit_code != 1:
                error = "expected startup rejection did not return its authenticated callback code"
        elif exit_code != 0:
            error = "diagnostic Player exited with code " + str(exit_code)
        elif not identity_checks.get("passed"):
            error = "diagnostic result identity checks failed"
    except Exception as problem:
        error = str(problem)
    finally:
        if inventory_roots:
            try:
                after_sets = tree_sets(inventory_roots)
            except Exception as problem:
                observation_errors.append(str(problem))
        after = {}
        paths_after = set(immutable)
        for files in after_sets.values():
            paths_after.update(files)
        for path in sorted(set(Path(path) for path in before) | paths_after):
            value, observation_error = safe_digest(path)
            if observation_error:
                observation_errors.append(observation_error)
            else:
                after[str(path)] = value
        if before_sets and after_sets:
            unchanged, comparison_errors = compare_observations(before, after, before_sets, after_sets)
            observation_errors.extend(comparison_errors)
        else:
            unchanged = False
        if observation_errors and not error:
            error = "input observation failed: " + "; ".join(dict.fromkeys(observation_errors))
        finished_at = time.time()
        exit_state = classify_exit(exit_code, launcher_initiated_termination)
        build_receipt_hash, build_hash_error = safe_digest(build_path)
        manifest_hash, manifest_hash_error = safe_digest(manifest_path)
        audit_hash, audit_hash_error = safe_digest(audit_path)
        result_hash, result_hash_error = safe_digest(result_path)
        early_hash, early_hash_error = safe_digest(early_result_path)
        observation_errors.extend(error for error in (build_hash_error, manifest_hash_error,
                                                       audit_hash_error) if error)
        if not expected_startup_rejection:
            observation_errors.extend(error for error in (result_hash_error,) if error)
        if args.path == "shadow":
            observation_errors.extend(error for error in (early_hash_error,) if error)
        if observation_errors and not error:
            error = "input observation failed: " + "; ".join(dict.fromkeys(observation_errors))
        receipt = {
            "schemaVersion": 1,
            "kind": "H1CountPlayerLaunchReceipt",
            "diagnosticOnly": True,
            "runId": run_id,
            "projectRoot": str(project),
            "buildReceiptPath": str(build_path),
            "buildReceiptSha256": build_receipt_hash,
            "fixtureManifestPath": str(manifest_path),
            "fixtureManifestSha256": manifest_hash,
            "fixtureAuditPath": str(audit_path),
            "fixtureAuditSha256": audit_hash,
            "family": args.family,
            "path": args.path,
            "caseId": args.case_id,
            "mode": mode_for(args.family, args.path, build["featureEnabled"]) if build else "",
            "featureEnabled": build.get("featureEnabled") if build else None,
            "cppConfiguration": build.get("cppConfiguration", "") if build else "",
            "expectedOutcome": case.get("expected") if case else "",
            "buildGuid": build.get("buildGuid", "") if build else "",
            "playerOutput": build.get("playerOutput", "") if build else "",
            "playerExecutable": build.get("playerExecutable", "") if build else "",
            "nativeLibraryPath": build.get("nativeLibraryPath", "") if build else "",
            "nativeMetadataPath": build.get("nativeMetadataPath", "") if build else "",
            "inputSnapshot": build.get("inputSnapshot", "") if build else "",
            "inputSnapshotHash": build.get("inputSnapshotHash", "") if build else "",
            "sourcePinFile": build.get("sourcePinFile", "") if build else "",
            "sourcePinSha256": build.get("sourcePinSha256", "") if build else "",
            "fixturePath": str(fixture) if fixture else "",
            "playerExecutableSha256": build.get("playerExecutableSha256", "") if build else "",
            "nativeLibrarySha256": build.get("nativeLibrarySha256", "") if build else "",
            "nativeMetadataSha256": build.get("nativeMetadataSha256", "") if build else "",
            "command": command,
            "processId": process_id,
            "startedAtUnix": started_at,
            "finishedAtUnix": finished_at,
            "durationSeconds": finished_at - started_at,
            "timeoutSeconds": args.timeout,
            "exitCode": exit_code,
            "timedOut": timed_out,
            "launcherInitiatedTermination": exit_state["launcherInitiatedTermination"],
            "processFailed": exit_state["processFailed"],
            "signalTerminated": exit_state["signalTerminated"],
            "crashed": exit_state["crashed"],
            "resultPath": str(result_path),
            "resultSha256": result_hash,
            "earlyResultPath": str(early_result_path),
            "earlyResultSha256": early_hash,
            "fixtureDllSha256": before.get(str(fixture), "") if fixture else "",
            "unityLogPath": str(unity_log),
            "consoleLogPath": str(console_log),
            "inputHashesBefore": before,
            "inputHashesAfter": after,
            "inputsUnchanged": bool(before) and before == after,
            "resultClaim": result.get("result") if result else "",
            "earlyResultClaim": early.get("result") if early else "",
            "earlyReceiptChecks": early_checks,
            "identityChecks": identity_checks,
            "expectedStartupRejection": expected_startup_rejection,
            "launchSucceeded": bool(not error and ((exit_code == 1 and expected_startup_rejection) or
                                                    (exit_code == 0 and not expected_startup_rejection)) and unchanged),
            "passed": bool(not error and ((exit_code == 1 and expected_startup_rejection and early_checks.get("passed", False)) or
                                           (exit_code == 0 and not expected_startup_rejection and identity_checks.get("passed"))) and unchanged),
            "error": error,
            "observationErrors": list(dict.fromkeys(observation_errors)),
            "note": "Identity checks do not constitute semantic acceptance; an independent verifier remains authoritative.",
        }
        with receipt_path.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write("\n")
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
