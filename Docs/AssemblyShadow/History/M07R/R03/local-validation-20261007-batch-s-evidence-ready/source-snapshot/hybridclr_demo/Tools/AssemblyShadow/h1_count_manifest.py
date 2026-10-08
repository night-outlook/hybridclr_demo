"""Independent manifest binding for H1 parameter count fixtures.

The fixture writer's declared count is treated as input metadata.  This module
uses a separate canonical case table and the byte-shape decoder to prove the
actual method signature and Param rows.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from shadow_tools import VerificationError, require
from h1_count_fixture_audit import inspect_file


HERE = Path(__file__).resolve().parent
CORE_PATH = HERE / "h1_count_fixture_audit.py"
TOOL_PATH = HERE / "h1_count_manifest.py"
MAX_MANIFEST_BYTES = 16 * 1024 * 1024
SHA256 = re.compile(r"^[0-9a-f]{64}$")
TARGET_TYPE = "AssemblyShadow.H1Count.Target"
TARGET_METHOD = "Probe"


# This table is the independent parameter contract.  It intentionally does
# not import CASE_SPECS or any other generator declaration.
CANONICAL_CASES = (
    ("H1R-P01-a", 0, "base-0", "Accepted"),
    ("H1R-P01-b", 1, "base-1", "Accepted"),
    ("H1R-P01-c", 254, "base-254", "Accepted"),
    ("H1R-P01-d", 255, "base-255", "Accepted"),
    ("H1R-P02-a", 256, "base-256", "ControlledRejected"),
    ("H1R-P02-b", 65535, "base-65535", "ControlledRejected"),
    ("H1R-P03-a", 65536, "base-65536", "ControlledRejected"),
    ("H1R-P03-b", 65537, "base-65537", "ControlledRejected"),
    ("H1R-P04-return255", 255, "return255", "Accepted"),
    ("H1R-P04-partial-names", 255, "partial-names", "Accepted"),
    ("H1R-P04-instance", 255, "instance", "Accepted"),
    ("H1R-P04-mixed-kinds", 255, "mixed-kinds", "Accepted"),
)
CANONICAL_BY_ID = {case[0]: case for case in CANONICAL_CASES}
CANONICAL_IDS = tuple(case[0] for case in CANONICAL_CASES)
EXPECTED_ARTIFACT_KEYS = frozenset((
    "fullName", "mvid", "name", "path", "sha256", "sizeBytes",
    "targetMethod", "targetType", "version"))
EXPECTED_CASE_KEYS = frozenset(("caseId", "count", "expected", "family",
                                "ordinary", "shadow", "variant"))
EXPECTED_TOP_KEYS = frozenset((
    "caseSet", "cases", "createdAtUtc", "family", "generator", "kind",
    "recipe", "schemaVersion", "seed", "targetMethod", "targetType"))


class ManifestError(VerificationError):
    """A malformed or unauthenticated fixture manifest."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _canonical_existing(path_value, label: str) -> Path:
    require(isinstance(path_value, (str, Path)) and str(path_value),
            f"{label} path is missing")
    path = Path(path_value)
    require(path.is_absolute() and path == path.resolve(),
            f"{label} path must be canonical absolute")
    require(path.is_file() and not path.is_symlink(),
            f"{label} path is missing or not a regular file")
    for parent in path.parents:
        require(not parent.is_symlink() and parent == parent.resolve(),
                f"{label} path has a symlinked/noncanonical parent")
    return path


def _canonical_new(path_value, label: str) -> Path:
    require(isinstance(path_value, (str, Path)) and str(path_value),
            f"{label} path is missing")
    path = Path(path_value)
    require(path.is_absolute() and path == path.resolve() and not path.exists() and
            not path.is_symlink(), f"{label} must be a new canonical absolute path")
    require(path.parent.is_dir() and not path.parent.is_symlink() and
            path.parent == path.parent.resolve(),
            f"{label} parent must be an existing canonical directory")
    return path


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(isinstance(key, str), "Manifest object key must be a string")
        require(key not in result, "Duplicate manifest JSON key: " + key)
        result[key] = value
    return result


def parse_manifest_bytes(data: bytes, label="H1 count manifest") -> dict:
    require(type(data) is bytes and 0 < len(data) <= MAX_MANIFEST_BYTES,
            f"{label}: invalid or oversized manifest")
    try:
        value = json.loads(data.decode("utf-8-sig"), object_pairs_hook=_unique_pairs)
    except (UnicodeError, ValueError) as error:
        raise ManifestError(f"{label}: invalid JSON: {error}") from error
    require(isinstance(value, dict), f"{label}: root must be an object")
    return value


def load_manifest(path: Path) -> tuple[dict, bytes, Path]:
    path = _canonical_existing(path, "manifest")
    data = path.read_bytes()
    require(len(data) <= MAX_MANIFEST_BYTES, "manifest is oversized")
    return parse_manifest_bytes(data, str(path)), data, path


def _require_keys(value, expected, label):
    require(isinstance(value, dict) and set(value) == set(expected),
            f"{label}: unexpected or missing keys")


def _require_sha(value, label):
    require(isinstance(value, str) and SHA256.fullmatch(value) is not None,
            f"{label}: invalid SHA-256")


def _canonical_case_record(case, expected):
    _require_keys(case, EXPECTED_CASE_KEYS, "manifest case")
    case_id, count, variant, outcome = expected
    require(case["caseId"] == case_id and type(case["count"]) is int and
            case["count"] == count and case["variant"] == variant and
            case["family"] == "parameters" and case["expected"] == outcome,
            f"{case_id}: canonical parameter case differs")
    for flavor in ("ordinary", "shadow"):
        artifact = case[flavor]
        _require_keys(artifact, EXPECTED_ARTIFACT_KEYS, f"{case_id}/{flavor}")
        _require_sha(artifact["sha256"], f"{case_id}/{flavor} artifact")
        require(type(artifact["sizeBytes"]) is int and artifact["sizeBytes"] > 0,
                f"{case_id}/{flavor}: invalid artifact size")
        require(artifact["targetMethod"] == TARGET_METHOD and
                isinstance(artifact["targetType"], str) and artifact["targetType"],
                f"{case_id}/{flavor}: invalid target identity")
        require(isinstance(artifact["name"], str) and isinstance(artifact["fullName"], str) and
                isinstance(artifact["version"], str) and isinstance(artifact["mvid"], str),
                f"{case_id}/{flavor}: invalid assembly identity fields")
    return case


def _validate_generator_inputs(manifest):
    generator = manifest["generator"]
    require(isinstance(generator, dict), "manifest generator must be an object")
    before, after = generator.get("inputHashesBefore"), generator.get("inputHashesAfter")
    require(isinstance(before, dict) and isinstance(after, dict) and before == after and
            generator.get("inputsUnchanged") is True,
            "generator input hash receipt is incomplete or drifted")
    require(before, "generator input hash receipt is empty")
    for path_value, expected_hash in before.items():
        _require_sha(expected_hash, "generator input")
        path = _canonical_existing(path_value, "generator input")
        require(_sha256_file(path) == expected_hash,
                f"generator input hash differs: {path}")


def validate_manifest_structure(manifest: dict) -> dict:
    """Validate the immutable matrix and artifact declarations."""
    _require_keys(manifest, EXPECTED_TOP_KEYS, "manifest")
    require(manifest["schemaVersion"] == 1 and manifest["kind"] == "H1CountFixtureManifest" and
            manifest["family"] == "parameters" and manifest["caseSet"] == "all" and
            manifest["targetType"] == TARGET_TYPE and manifest["targetMethod"] == TARGET_METHOD,
            "manifest is not the parameter fixture contract")
    require(type(manifest["seed"]) is int and 0 <= manifest["seed"] <= 0x7fffffff,
            "manifest seed is invalid")
    cases = manifest["cases"]
    require(isinstance(cases, list) and len(cases) == len(CANONICAL_CASES),
            "manifest must contain exactly the canonical parameter cases")
    require([case.get("caseId") for case in cases] == list(CANONICAL_IDS),
            "manifest parameter IDs are missing, duplicated, or out of order")
    for case, expected in zip(cases, CANONICAL_CASES):
        _canonical_case_record(case, expected)

    recipe = manifest["recipe"]
    require(isinstance(recipe, dict) and recipe.get("family") == "parameters" and
            recipe.get("caseSet") == "all" and recipe.get("flavors") == ["ordinary", "shadow"] and
            recipe.get("seed") == manifest["seed"], "manifest recipe is not canonical")
    recipe_cases = recipe.get("cases")
    require(isinstance(recipe_cases, list) and
            [item.get("caseId") for item in recipe_cases] == list(CANONICAL_IDS),
            "manifest recipe cases are missing, duplicated, or out of order")
    for item, expected in zip(recipe_cases, CANONICAL_CASES):
        require(isinstance(item, dict) and item.get("caseId") == expected[0] and
                item.get("family") == "parameters" and item.get("count") == expected[1] and
                item.get("variant") == expected[2] and item.get("expected") == expected[3],
                f"{expected[0]}: recipe case differs")
    return manifest


def _row_hash(rows):
    value = [{"flags": row["flags"], "sequence": row["sequence"], "name": row["name"]}
             for row in rows]
    return _sha256_bytes(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def _sequence_name_hash(rows, field):
    return _sha256_bytes(json.dumps([row[field] for row in rows],
                                    ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def _parameter_types(expected, count):
    variant = expected[2]
    if variant == "mixed-kinds":
        pattern = ("System.Int32", "System.String", "System.Object", "System.Int32&", "System.String[]")
        return [pattern[index % len(pattern)] for index in range(count)]
    return ["System.Int32"] * count


def _expected_shape(expected):
    case_id, count, variant, outcome = expected
    names, sequences = [], []
    if variant == "partial-names":
        sequences = [sequence for sequence in range(1, count + 1)
                     if (sequence - 1) % 17 == 0]
        names = [f"p{sequence:04d}" for sequence in sequences]
    elif variant == "return255":
        sequences, names = [0], ["result"]
    return {
        "caseId": case_id, "count": count, "variant": variant,
        "expectedResult": outcome, "returnType": "System.Int32",
        "instance": variant == "instance", "parameterTypes": _parameter_types(expected, count),
        "parameterSequences": sequences, "parameterNames": names,
    }


def validate_observation(case: dict, flavor: str, actual: dict) -> dict:
    """Bind one independently decoded DLL shape to its manifest case."""
    require(flavor in ("ordinary", "shadow"), "invalid fixture flavor")
    expected = CANONICAL_BY_ID.get(case.get("caseId"))
    require(expected is not None, "unknown parameter case")
    artifact = case[flavor]
    require(actual.get("sha256") == artifact["sha256"] and
            actual.get("sizeBytes") == artifact["sizeBytes"],
            f"{expected[0]}/{flavor}: DLL bytes differ from manifest")
    identity = actual.get("identity")
    require(isinstance(identity, dict), f"{expected[0]}/{flavor}: missing decoded identity")
    for field in ("name", "fullName", "version", "mvid"):
        require(identity.get(field) == artifact[field],
                f"{expected[0]}/{flavor}: decoded identity {field} differs")

    target_type = artifact["targetType"]
    types = actual.get("types")
    require(isinstance(types, list), f"{expected[0]}/{flavor}: missing decoded type identities")
    target_types = [item for item in types if item.get("fullName") == target_type]
    require(len(target_types) == 1, f"{expected[0]}/{flavor}: target type is not unique")
    methods = actual.get("methods")
    require(isinstance(methods, list), f"{expected[0]}/{flavor}: missing decoded methods")
    target_methods = [item for item in methods
                      if item.get("declaringType") == target_type and
                      item.get("name") == artifact["targetMethod"]]
    require(len(target_methods) == 1, f"{expected[0]}/{flavor}: target method is not unique")

    shape = _expected_shape(expected)
    method = target_methods[0]
    signature = method.get("signature")
    require(isinstance(signature, dict) and signature.get("count") == shape["count"] and
            signature.get("returnType") == shape["returnType"] and
            signature.get("instance") is shape["instance"] and
            signature.get("parameterTypes") == shape["parameterTypes"],
            f"{expected[0]}/{flavor}: decoded method signature differs")
    rows = method.get("paramRows")
    require(isinstance(rows, list) and
            [row.get("sequence") for row in rows] == shape["parameterSequences"] and
            [row.get("name") for row in rows] == shape["parameterNames"],
            f"{expected[0]}/{flavor}: decoded Param rows differ")
    if expected[2] == "return255":
        require(rows[0].get("sequence") == 0 and rows[0].get("name") == "result",
                f"{expected[0]}/{flavor}: return Param row 0 was not retained")

    return {
        "assemblyName": identity["name"], "assemblyFullName": identity["fullName"],
        "targetType": target_type, "targetTypeRid": target_types[0].get("rid"),
        "targetMethod": artifact["targetMethod"], "targetMethodRid": method.get("rid"),
        "signatureCount": signature["count"], "returnType": signature["returnType"],
        "instance": signature["instance"],
        "parameterTypesSha256": _sha256_bytes("\n".join(signature["parameterTypes"]).encode()),
        "paramRowCount": len(rows), "paramRowsSha256": _row_hash(rows),
        "parameterSequencesSha256": _sequence_name_hash(rows, "sequence"),
        "parameterNamesSha256": _sequence_name_hash(rows, "name"),
        "returnParamRow0Retained": any(row.get("sequence") == 0 for row in rows),
    }


def _source_snapshot(manifest_path: Path, manifest_bytes: bytes):
    return {
        "manifestPath": str(manifest_path),
        "manifestSha256": _sha256_bytes(manifest_bytes),
        "coreAuditPath": str(CORE_PATH),
        "coreAuditSha256": _sha256_file(CORE_PATH),
        "manifestToolPath": str(TOOL_PATH),
        "manifestToolSha256": _sha256_file(TOOL_PATH),
    }


def audit_manifest(manifest_path: Path) -> dict:
    manifest, manifest_bytes, manifest_path = load_manifest(Path(manifest_path))
    source_before = _source_snapshot(manifest_path, manifest_bytes)
    validate_manifest_structure(manifest)
    _validate_generator_inputs(manifest)

    executed = []
    records = []
    for case in manifest["cases"]:
        case_id = case["caseId"]
        observations = {}
        for flavor in ("ordinary", "shadow"):
            artifact_path = _canonical_existing(case[flavor]["path"], f"{case_id}/{flavor} DLL")
            expected_path = manifest_path.parent / flavor / f"{case_id}.dll"
            require(artifact_path == expected_path,
                    f"{case_id}/{flavor}: DLL path is outside its canonical flavor location")
            observations[flavor] = validate_observation(
                case, flavor, inspect_file(artifact_path))
        expected = _expected_shape(CANONICAL_BY_ID[case_id])
        expected_summary = {key: value for key, value in expected.items()
                            if key not in ("parameterTypes", "parameterSequences", "parameterNames")}
        expected_summary.update({
            "parameterTypesSha256": _sha256_bytes("\n".join(expected["parameterTypes"]).encode()),
            "parameterSequencesSha256": _sha256_bytes(json.dumps(
                expected["parameterSequences"], separators=(",", ":")).encode()),
            "parameterNamesSha256": _sha256_bytes(json.dumps(
                expected["parameterNames"], separators=(",", ":")).encode()),
            "paramRowCount": len(expected["parameterSequences"]),
            "returnParamRow0Retained": 0 in expected["parameterSequences"],
        })
        records.append({"caseId": case_id, "expected": expected_summary,
                        "observed": observations})
        executed.append(case_id)

    require(_source_snapshot(manifest_path, manifest_path.read_bytes()) == source_before,
            "manifest, core, or manifest-tool source drifted during audit")
    _validate_generator_inputs(manifest)
    return {
        "schemaVersion": 1,
        "kind": "H1CountFixtureShapeAudit",
        "result": "Passed",
        "family": "parameters",
        "caseSet": "all",
        "requestedCaseIds": list(CANONICAL_IDS),
        "executedCaseIds": executed,
        "sourceBinding": source_before,
        "generatorInputHashes": manifest["generator"]["inputHashesBefore"],
        "cases": records,
        "createdAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def _write_new(path: Path, value: dict):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, sort_keys=True)
        stream.write("\n")


def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    output = None
    try:
        manifest_path = _canonical_existing(args.manifest, "manifest")
        output = _canonical_new(args.output, "audit output")
        result = audit_manifest(manifest_path)
        _write_new(output, result)
        print(json.dumps({"result": result["result"], "output": str(output),
                          "requestedCaseIds": result["requestedCaseIds"],
                          "executedCaseIds": result["executedCaseIds"]}, sort_keys=True))
        return 0
    except Exception as error:
        failure = {
            "schemaVersion": 1, "kind": "H1CountFixtureShapeAudit", "result": "Failed",
            "requestedCaseIds": list(CANONICAL_IDS), "executedCaseIds": [],
            "failure": str(error), "createdAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        if output is None:
            try:
                output = _canonical_new(args.output, "audit output")
            except Exception:
                output = None
        if output is not None:
            try:
                _write_new(output, failure)
            except Exception as write_error:
                print(f"h1-count manifest audit failed: {error}; failure receipt: {write_error}", file=sys.stderr)
                return 1
        print(f"h1-count manifest audit failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
