#!/usr/bin/env python3
"""Validate the immutable successor evidence chain used by H1 packaging.

The v11 package was able to select an older matrix and older count Players
because each packaging stage carried its own path constants.  This module is
the single binding contract for the v12 successor chain.  Callers must pass
the binding file explicitly; all paths, bytes, statuses, and source pins are
checked before any delivery output is created.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


CHAIN_ID = "H1MatrixProvenanceFinal-20260911-v4"
SCHEMA_VERSION = 1
KIND = "H1RemediationSuccessorChainBinding"


class SuccessorChainError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SuccessorChainError(message)


def _unique_json_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"),
                          object_pairs_hook=_unique_json_pairs)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SuccessorChainError("Cannot read successor binding: " + str(path)) from error


def _canonical_file(value, label: str) -> Path:
    require(type(value) is str and value, label + " path is required")
    path = Path(value)
    require(path.is_absolute() and not path.is_symlink(), label + " must be absolute and not symlinked")
    resolved = path.resolve(strict=True)
    require(path == resolved and resolved.is_file() and not resolved.is_symlink(),
            label + " must be a canonical regular file")
    parent = resolved.parent
    while parent != parent.parent:
        require(not parent.is_symlink(), label + " has a symlinked parent")
        parent = parent.parent
    return resolved


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_hash(value, label: str) -> str:
    require(type(value) is str and len(value) == 64 and
            all(character in "0123456789abcdef" for character in value.lower()),
            label + " SHA-256 is invalid")
    return value.lower()


def _field(value, path: str):
    current = value
    for part in path.split("."):
        require(isinstance(current, dict) and part in current,
                "Missing required field " + path)
        current = current[part]
    return current


def _validate_artifact(row, label: str) -> dict:
    require(type(row) is dict, label + " must be an object")
    path = _canonical_file(row.get("path"), label)
    expected_path = str(path)
    expected_hash = _validate_hash(row.get("sha256"), label)
    expected_size = row.get("sizeBytes")
    require(type(expected_size) is int and not isinstance(expected_size, bool) and expected_size >= 0,
            label + " sizeBytes is invalid")
    require(_sha256(path) == expected_hash, label + " bytes differ from binding")
    require(path.stat().st_size == expected_size, label + " size differs from binding")
    json_checks = row.get("jsonChecks", {})
    require(type(json_checks) is dict, label + " jsonChecks must be an object")
    text_contains = row.get("textContains", [])
    require(type(text_contains) is list and all(type(item) is str and item for item in text_contains),
            label + " textContains is invalid")
    if json_checks:
        try:
            value = _read_json(path)
        except SuccessorChainError:
            raise SuccessorChainError(label + " is not valid JSON for jsonChecks")
        require(type(value) is dict, label + " JSON must be an object")
        for field_path, expected in json_checks.items():
            require(_field(value, field_path) == expected,
                    label + " field differs: " + field_path)
    if text_contains:
        text = path.read_text(encoding="utf-8-sig")
        for marker in text_contains:
            require(marker in text, label + " is missing required text: " + marker)
    return {
        "path": expected_path,
        "sha256": expected_hash,
        "sizeBytes": expected_size,
        **({"jsonChecks": json_checks} if json_checks else {}),
        **({"textContains": text_contains} if text_contains else {}),
    }


def _validate_semantics(artifacts: dict, source_chain: dict) -> None:
    matrix = artifacts["count-matrix"]
    matrix_value = _read_json(Path(matrix["path"]))
    result_index = matrix_value["inputs"]["resultIndex"]
    require(result_index["path"].endswith("H1MatrixProvenanceFinal-20260911-v4/result-index.json"),
            "count matrix result index is not the v4 successor")

    compiler = _read_json(Path(artifacts["compiler-provenance"]["path"]))
    rows = compiler.get("rows")
    require(type(rows) is list and {row.get("mode") for row in rows} ==
            {"Off/Debug", "Off/Release", "On/Debug", "On/Release"},
            "compiler provenance mode set is not the four successor builds")
    expected_builds = {
        "Off/Debug": "H1CountBuild-d0f847a745a742e681119a84008f82a9",
        "Off/Release": "H1CountBuild-d5ccf93bdb6946aaa85d6ea4b17c50d8",
        "On/Debug": "H1CountBuild-39b0dd2a8e9c49ca92a3c61dd2ba097e",
        "On/Release": "H1CountBuild-467fba57c2204074a42d151625fceca5",
    }
    for row in rows:
        mode = row["mode"]
        require(Path(row["receiptPath"]).parent.name == expected_builds[mode],
                "compiler provenance selects stale count build for " + mode)
        build_id = mode.lower().replace("/", "-")
        require(row["receiptSha256"] == _sha256(Path(row["receiptPath"])),
                "compiler receipt hash is not current for " + mode)

    m06 = _read_json(Path(artifacts["m06-successor-aggregate"]["path"]))
    require(m06["requiredMembership"]["m07Modes"] and
            len(m06["requiredMembership"]["m07Modes"]) == 14 and
            len(m06["requiredMembership"]["r00Modes"]) == 4 and
            len(m06["requiredMembership"]["startupModes"]) == 11,
            "M06 successor membership is incomplete")
    input_rows = {row.get("label"): row for row in m06.get("inputArtifacts", []) if isinstance(row, dict)}
    for label, artifact_id in (("startup11", "startup11"), ("broad-python", "m06-python")):
        row = input_rows.get(label)
        require(row is not None and row.get("path") == artifacts[artifact_id]["path"] and
                row.get("sha256") == artifacts[artifact_id]["sha256"],
                "M06 successor input is not bound to " + artifact_id)

    m07 = artifacts["m07-full"]
    m07_text = Path(m07["path"]).read_text(encoding="utf-8-sig")
    require('"baselineBuildId": "M07-Baseline-H1-Candidate-9c6b812-v2"' in m07_text and
            '"resultPassed": true' in m07_text and '"missingModes": []' in m07_text,
            "M07 successor evidence is not the current complete chain")

    receipt = _read_json(Path(artifacts["performance-receipt"]["path"]))
    analysis_ref = receipt["analysis"]
    require(analysis_ref["path"] == artifacts["performance-analysis"]["path"] and
            analysis_ref["sha256"] == artifacts["performance-analysis"]["sha256"],
            "performance receipt is not bound to the selected analysis")

    source = _read_json(Path(artifacts["source-state"]["path"]))
    selected = source["builtSourceSelection"]
    for field in ("demo", "hybridclr", "hybridclrUnity", "il2cppPlus"):
        require(selected[field] == source_chain[field], "source chain differs for " + field)
    require(source["repositories"]["hybridclrActive"]["head"] == source_chain["hybridclrActive"],
            "active HybridCLR source chain differs")
    require(selected["sourcePinFile"]["sha256"] == source_chain["sourcePinSha256"],
            "source pin hash differs from source chain")
    require(source["allActiveNativeBytesEqualFrozenCommit"] is True,
            "active native bytes are not paired to the frozen source")


def load(path: Path, *, expected_binding_sha256: str | None = None) -> dict:
    """Load and validate a binding, returning a normalized immutable record."""
    binding_path = _canonical_file(str(path), "successor binding")
    binding_hash = _sha256(binding_path)
    if expected_binding_sha256 is not None:
        require(binding_hash == _validate_hash(expected_binding_sha256, "successor binding"),
                "successor binding bytes differ from manifest")
    value = _read_json(binding_path)
    require(value.get("schemaVersion") == SCHEMA_VERSION and value.get("kind") == KIND,
            "Unsupported successor binding")
    require(value.get("chainId") == CHAIN_ID,
            "Successor chain is not " + CHAIN_ID)
    source_chain = value.get("sourceChain")
    require(type(source_chain) is dict, "sourceChain is required")
    expected_source_keys = {"demo", "hybridclr", "hybridclrActive", "hybridclrUnity", "il2cppPlus", "sourcePinSha256"}
    require(set(source_chain) == expected_source_keys, "sourceChain keys are not explicit")
    for key in expected_source_keys:
        if key.endswith("Sha256"):
            _validate_hash(source_chain[key], "sourceChain." + key)
        else:
            require(type(source_chain[key]) is str and source_chain[key],
                    "sourceChain." + key + " is required")
    rows = value.get("artifacts")
    require(type(rows) is list and rows, "successor artifacts are required")
    expected_ids = {
        "count-matrix", "compiler-provenance", "m06-successor-aggregate",
        "m06-successor-native-impact", "startup11", "m07-full", "m06-python",
        "performance-analysis", "performance-receipt", "toolchain", "historical-gaps",
        "source-state", "source-h1-startup", "source-h1-runner", "source-h1-verifier",
        "source-h1-build-adapter", "source-pin",
    }
    actual_ids = [row.get("id") if isinstance(row, dict) else None for row in rows]
    require(set(actual_ids) == expected_ids and len(actual_ids) == len(expected_ids),
            "successor artifact membership differs")
    artifacts = {}
    for row in rows:
        artifact_id = row["id"]
        artifacts[artifact_id] = _validate_artifact(row, "artifact " + artifact_id)
    require(artifacts["source-pin"]["sha256"] == source_chain["sourcePinSha256"],
            "source-pin artifact differs from source chain")
    _validate_semantics(artifacts, source_chain)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "kind": KIND,
        "chainId": CHAIN_ID,
        "bindingPath": str(binding_path),
        "bindingSha256": binding_hash,
        "bindingSizeBytes": binding_path.stat().st_size,
        "sourceChain": source_chain,
        "artifacts": artifacts,
    }


def validate_manifest_record(record: dict) -> dict:
    """Validate the chain record copied into a package manifest."""
    require(type(record) is dict, "successorChain manifest record is required")
    path = record.get("bindingPath")
    require(type(path) is str and path, "successorChain.bindingPath is required")
    loaded = load(Path(path), expected_binding_sha256=record.get("bindingSha256"))
    comparable = {key: record.get(key) for key in ("chainId", "sourceChain", "artifacts")}
    expected = {key: loaded[key] for key in comparable}
    require(comparable == expected, "manifest successorChain differs from its binding")
    return loaded


def digest(path: Path) -> str:
    return _sha256(path)
