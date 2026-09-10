"""Independent manifest binding for H1 nested-type count fixtures.

The fixture generator's counts are treated as input metadata.  This module
uses a separate, explicit case table and the byte-shape decoder to prove the
actual TypeDef and NestedClass identities, ownership, and order.
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
from h1_count_manifest import (
    _canonical_existing,
    _canonical_new,
    _sha256_bytes,
    _sha256_file,
    _unique_pairs,
)


HERE = Path(__file__).resolve().parent
CORE_PATH = HERE / "h1_count_fixture_audit.py"
TOOL_PATH = HERE / "h1_nested_manifest.py"
SHARED_TOOL_PATH = HERE / "h1_count_manifest.py"
MAX_MANIFEST_BYTES = 16 * 1024 * 1024
SHA256 = re.compile(r"^[0-9a-f]{64}$")
TARGET_TYPE = "AssemblyShadow.H1Nested.Target"
TARGET_METHOD = "Probe"
NAMESPACE = "AssemblyShadow.H1Nested"
FLAVORS = ("ordinary", "shadow")


# This table is the independent nested contract.  It intentionally does not
# import CASE_SPECS or any declaration from the fixture generator.
CANONICAL_CASES = (
    ("H1R-N01-a", 0, (0,), ("Target",), False, "nested-single", "Accepted"),
    ("H1R-N01-b", 1, (1,), ("Target",), False, "nested-single", "Accepted"),
    ("H1R-N01-c", 65534, (65534,), ("Target",), False, "nested-single", "Accepted"),
    ("H1R-N01-d", 65535, (65535,), ("Target",), False, "nested-single", "Accepted"),
    ("H1R-N02-a", 65536, (65536,), ("Target",), False, "nested-single", "ControlledRejected"),
    ("H1R-N02-b", 65537, (65537,), ("Target",), False, "nested-single", "ControlledRejected"),
    ("H1R-N03-interleaved", 4, (2, 2), ("Target", "SiblingB"), True,
     "nested-interleaved", "Accepted"),
    ("H1R-N04-adjacent-valid", 65536, (1, 65535), ("Target", "SiblingB"), False,
     "nested-adjacent-valid", "Accepted"),
    ("H1R-N04-adjacent-overflow", 65537, (1, 65536), ("Target", "SiblingB"), False,
     "nested-adjacent-overflow", "ControlledRejected"),
    ("H1R-N05-final-repeat", 65535, (65535,), ("Target",), False,
     "nested-final-repeat", "Accepted"),
)
CANONICAL_BY_ID = {case[0]: case for case in CANONICAL_CASES}
CANONICAL_IDS = tuple(case[0] for case in CANONICAL_CASES)
EXPECTED_ARTIFACT_KEYS = frozenset((
    "fullName", "mvid", "name", "path", "sha256", "sizeBytes",
    "targetMethod", "targetType", "version"))
EXPECTED_CASE_KEYS = frozenset((
    "caseId", "count", "declaringTypes", "expected", "family",
    "groupCounts", "interleaved", "ordinary", "shadow", "variant"))
EXPECTED_RECIPE_CASE_KEYS = frozenset((
    "caseId", "count", "declaringTypes", "expected", "family",
    "groupCounts", "interleaved", "variant"))
EXPECTED_TOP_KEYS = frozenset((
    "caseSet", "cases", "createdAtUtc", "family", "generator", "kind",
    "recipe", "schemaVersion", "seed", "targetMethod", "targetType"))


class ManifestError(VerificationError):
    """A malformed or unauthenticated nested fixture manifest."""


def parse_manifest_bytes(data: bytes, label="H1 nested manifest") -> dict:
    require(type(data) is bytes and 0 < len(data) <= MAX_MANIFEST_BYTES,
            f"{label}: invalid or oversized manifest")
    try:
        value = json.loads(data.decode("utf-8-sig"), object_pairs_hook=_unique_pairs)
    except (UnicodeError, ValueError, VerificationError) as error:
        raise ManifestError(f"{label}: invalid JSON: {error}") from error
    require(isinstance(value, dict), f"{label}: root must be an object")
    return value


def load_manifest(path: Path) -> tuple[dict, bytes, Path]:
    path = _canonical_existing(path, "manifest")
    data = path.read_bytes()
    return parse_manifest_bytes(data, str(path)), data, path


def _require_keys(value, expected, label):
    require(isinstance(value, dict) and set(value) == set(expected),
            f"{label}: unexpected or missing keys")


def _require_sha(value, label):
    require(isinstance(value, str) and SHA256.fullmatch(value) is not None,
            f"{label}: invalid SHA-256")


def _canonical_case_record(case, expected):
    _require_keys(case, EXPECTED_CASE_KEYS, "manifest case")
    case_id, count, groups, declaring, interleaved, variant, outcome = expected
    require(case["caseId"] == case_id and type(case["count"]) is int and
            case["count"] == count and case["groupCounts"] == list(groups) and
            case["declaringTypes"] == list(declaring) and
            type(case["interleaved"]) is bool and case["interleaved"] is interleaved and
            case["variant"] == variant and case["family"] == "nested" and
            case["expected"] == outcome,
            f"{case_id}: canonical nested case differs")
    require(sum(groups) == count, f"{case_id}: group counts do not sum to count")
    for flavor in FLAVORS:
        artifact = case[flavor]
        _require_keys(artifact, EXPECTED_ARTIFACT_KEYS, f"{case_id}/{flavor}")
        _require_sha(artifact["sha256"], f"{case_id}/{flavor} artifact")
        require(type(artifact["sizeBytes"]) is int and artifact["sizeBytes"] > 0,
                f"{case_id}/{flavor}: invalid artifact size")
        require(artifact["targetMethod"] is None and
                artifact["targetType"] == TARGET_TYPE,
                f"{case_id}/{flavor}: invalid target identity")
        require(all(isinstance(artifact[field], str) and artifact[field]
                    for field in ("name", "fullName", "version", "mvid")),
                f"{case_id}/{flavor}: invalid assembly identity fields")


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
    """Validate the immutable nested matrix and artifact declarations."""
    _require_keys(manifest, EXPECTED_TOP_KEYS, "manifest")
    require(manifest["schemaVersion"] == 1 and
            manifest["kind"] == "H1CountFixtureManifest" and
            manifest["family"] == "nested" and manifest["caseSet"] == "all" and
            manifest["targetType"] == TARGET_TYPE and
            manifest["targetMethod"] == TARGET_METHOD,
            "manifest is not the nested fixture contract")
    require(type(manifest["seed"]) is int and 0 <= manifest["seed"] <= 0x7fffffff,
            "manifest seed is invalid")
    cases = manifest["cases"]
    require(isinstance(cases, list) and len(cases) == len(CANONICAL_CASES) and
            [case.get("caseId") for case in cases] == list(CANONICAL_IDS),
            "manifest nested IDs are missing, duplicated, or out of order")
    for case, expected in zip(cases, CANONICAL_CASES):
        _canonical_case_record(case, expected)

    recipe = manifest["recipe"]
    _require_keys(recipe, ("caseSet", "cases", "family", "flavors", "seed"),
                  "manifest recipe")
    require(recipe["family"] == "nested" and recipe["caseSet"] == "all" and
            recipe["flavors"] == list(FLAVORS) and recipe["seed"] == manifest["seed"],
            "manifest recipe is not canonical")
    recipe_cases = recipe["cases"]
    require(isinstance(recipe_cases, list) and
            [item.get("caseId") for item in recipe_cases] == list(CANONICAL_IDS),
            "manifest recipe cases are missing, duplicated, or out of order")
    for item, expected in zip(recipe_cases, CANONICAL_CASES):
        _require_keys(item, EXPECTED_RECIPE_CASE_KEYS, "manifest recipe case")
        case_id, count, groups, declaring, interleaved, variant, outcome = expected
        require(item == {
            "caseId": case_id, "count": count, "declaringTypes": list(declaring),
            "expected": outcome, "family": "nested", "groupCounts": list(groups),
            "interleaved": interleaved, "variant": variant,
        }, f"{case_id}: recipe case differs")
    return manifest


def _children_hash(names):
    return _sha256_bytes("\n".join(names).encode("utf-8"))


def _relationship_hash(types):
    return _sha256_bytes("\n".join(
        f"{item['parentRid']}:{item['fullName']}" for item in types).encode("utf-8"))


def _expected_group(declaring, count):
    names = [f"{NAMESPACE}.{declaring}+{declaring}Child{index:05d}"
             for index in range(count)]
    return {
        "declaringType": f"{NAMESPACE}.{declaring}",
        "count": count,
        "first": names[0] if names else None,
        "last": names[-1] if names else None,
        "childrenSha256": _children_hash(names) if names else None,
        "children": names,
    }


def _expected_parent_sequence(declaring, groups, interleaved):
    if not interleaved:
        return [name for name, count in zip(declaring, groups) for _ in range(count)]
    sequence = []
    remaining = list(groups)
    while any(remaining):
        for index, name in enumerate(declaring):
            if remaining[index]:
                sequence.append(name)
                remaining[index] -= 1
    return sequence


def validate_observation(case: dict, flavor: str, actual: dict) -> dict:
    """Bind one independently decoded DLL shape to its manifest case."""
    require(flavor in FLAVORS, "invalid fixture flavor")
    expected = CANONICAL_BY_ID.get(case.get("caseId"))
    require(expected is not None, "unknown nested case")
    case_id, count, groups, declaring, interleaved, variant, outcome = expected
    artifact = case[flavor]
    require(actual.get("sha256") == artifact["sha256"] and
            actual.get("sizeBytes") == artifact["sizeBytes"],
            f"{case_id}/{flavor}: DLL bytes differ from manifest")
    identity = actual.get("identity")
    require(isinstance(identity, dict), f"{case_id}/{flavor}: missing decoded identity")
    for field in ("name", "fullName", "version", "mvid"):
        require(identity.get(field) == artifact[field],
                f"{case_id}/{flavor}: decoded identity {field} differs")

    types = actual.get("types")
    require(isinstance(types, list), f"{case_id}/{flavor}: missing decoded type identities")
    require(all(isinstance(item, dict) for item in types),
            f"{case_id}/{flavor}: malformed decoded type identity")
    targets = [item for item in types if item.get("fullName") == TARGET_TYPE]
    require(len(targets) == 1, f"{case_id}/{flavor}: target type is not unique")
    target = targets[0]
    require(target.get("parentRid") is None and target.get("name") == "Target" and
            target.get("namespace") == NAMESPACE and target.get("rid") != 1,
            f"{case_id}/{flavor}: target type relationship is invalid")

    expected_groups = [_expected_group(name, group_count)
                       for name, group_count in zip(declaring, groups) if group_count]
    parent_rids = {}
    actual_nested = []
    actual_group_summaries = actual.get("nestedGroups")
    require(isinstance(actual_group_summaries, list),
            f"{case_id}/{flavor}: missing decoded nested groups")
    for group_index, (declaring_name, group_count) in enumerate(zip(declaring, groups)):
        parent_name = f"{NAMESPACE}.{declaring_name}"
        parents = [item for item in types if item.get("fullName") == parent_name]
        require(len(parents) == 1, f"{case_id}/{flavor}: declaring type is not unique: {parent_name}")
        parent = parents[0]
        require(parent.get("parentRid") is None and parent.get("rid") != 1,
                f"{case_id}/{flavor}: declaring type relationship is invalid")
        parent_rid = parent.get("rid")
        require(type(parent_rid) is int and parent_rid not in parent_rids.values(),
                f"{case_id}/{flavor}: invalid declaring type RID")
        parent_rids[declaring_name] = parent_rid
        children = [item for item in types if item.get("parentRid") == parent_rid]
        expected_names = [f"{NAMESPACE}.{declaring_name}+{declaring_name}Child{index:05d}"
                          for index in range(group_count)]
        require([item.get("fullName") for item in children] == expected_names,
                f"{case_id}/{flavor}: child identities/order differ for {parent_name}")
        require(all(item.get("name") == f"{declaring_name}Child{index:05d}" and
                    item.get("namespace") == "" for index, item in enumerate(children)),
                f"{case_id}/{flavor}: child name/namespace differs for {parent_name}")
        actual_nested.extend(children)

        if group_count:
            require(group_index < len(actual_group_summaries),
                    f"{case_id}/{flavor}: missing nested group")
            summary = actual_group_summaries[group_index]
            require(summary.get("declaringType") == parent_name and
                    summary.get("parentRid") == parent_rid and
                    summary.get("count") == group_count and
                    summary.get("first") == expected_names[0] and
                    summary.get("last") == expected_names[-1] and
                    summary.get("childrenSha256") == _children_hash(expected_names),
                    f"{case_id}/{flavor}: nested group differs for {parent_name}")
    require(len(actual_group_summaries) == len(expected_groups),
            f"{case_id}/{flavor}: unexpected zero or extra nested group")

    nested_in_rid_order = [item for item in types if item.get("parentRid") is not None]
    require([item.get("fullName") for item in nested_in_rid_order] ==
            [item.get("fullName") for item in actual_nested] if not interleaved else
            len(nested_in_rid_order) == count,
            f"{case_id}/{flavor}: nested child ownership is incomplete")
    require(len(nested_in_rid_order) == count and
            actual.get("nestedClassTableCount") == count,
            f"{case_id}/{flavor}: NestedClass count differs")
    expected_type_count = 1 + len(declaring) + count
    require(actual.get("typeDefCount") == expected_type_count,
            f"{case_id}/{flavor}: TypeDef count differs")
    require(actual.get("methodDefCount") == 0 and actual.get("paramTableCount") == 0 and
            actual.get("methods") == [],
            f"{case_id}/{flavor}: nested fixture unexpectedly contains methods")
    require(actual.get("nestedClassSortedDeclared") is True,
            f"{case_id}/{flavor}: NestedClass sorted declaration missing")

    actual_parent_sequence = [
        item["fullName"].split("+", 1)[0].rsplit(".", 1)[-1]
        for item in nested_in_rid_order]
    expected_parent_sequence = _expected_parent_sequence(declaring, groups, interleaved)
    require(actual_parent_sequence == expected_parent_sequence,
            f"{case_id}/{flavor}: nested child interleaving differs")
    relationship_names = [
        f"{item.get('parentRid')}:{item.get('fullName')}" for item in nested_in_rid_order]
    return {
        "assemblyName": identity["name"],
        "assemblyFullName": identity["fullName"],
        "targetType": TARGET_TYPE,
        "targetTypeRid": target.get("rid"),
        "targetPresentWithZeroChildren": count == 0,
        "typeDefCount": actual["typeDefCount"],
        "nestedClassTableCount": actual["nestedClassTableCount"],
        "nestedClassSortedDeclared": actual["nestedClassSortedDeclared"],
        "nestedRowsSha256": actual.get("nestedRowsSha256"),
        "nestedParentSequenceSha256": _sha256_bytes("\n".join(actual_parent_sequence).encode()),
        "nestedRelationshipSha256": _sha256_bytes("\n".join(relationship_names).encode()),
        "groups": [
            {
                "declaringType": summary["declaringType"],
                "parentRid": summary["parentRid"],
                "count": summary["count"],
                "first": summary["first"],
                "last": summary["last"],
                "childrenSha256": summary["childrenSha256"],
            }
            for summary in actual_group_summaries
        ],
    }


def _source_snapshot(manifest_path: Path, manifest_bytes: bytes):
    return {
        "manifestPath": str(manifest_path),
        "manifestSha256": _sha256_bytes(manifest_bytes),
        "coreAuditPath": str(CORE_PATH),
        "coreAuditSha256": _sha256_file(CORE_PATH),
        "manifestToolPath": str(TOOL_PATH),
        "manifestToolSha256": _sha256_file(TOOL_PATH),
        "sharedManifestPath": str(SHARED_TOOL_PATH),
        "sharedManifestSha256": _sha256_file(SHARED_TOOL_PATH),
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
        for flavor in FLAVORS:
            artifact_path = _canonical_existing(case[flavor]["path"],
                                                f"{case_id}/{flavor} DLL")
            expected_path = manifest_path.parent / flavor / f"{case_id}.dll"
            require(artifact_path == expected_path,
                    f"{case_id}/{flavor}: DLL path is outside canonical flavor location")
            observations[flavor] = validate_observation(
                case, flavor, inspect_file(artifact_path))
        records.append({
            "caseId": case_id,
            "expected": {
                "count": case["count"], "groupCounts": case["groupCounts"],
                "declaringTypes": case["declaringTypes"],
                "interleaved": case["interleaved"], "variant": case["variant"],
                "expectedResult": case["expected"],
            },
            "observed": observations,
        })
        executed.append(case_id)

    require(_source_snapshot(manifest_path, manifest_path.read_bytes()) == source_before,
            "manifest, core, or manifest-tool source drifted during audit")
    _validate_generator_inputs(manifest)
    return {
        "schemaVersion": 1,
        "kind": "H1NestedFixtureShapeAudit",
        "result": "Passed",
        "family": "nested",
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
            "schemaVersion": 1, "kind": "H1NestedFixtureShapeAudit", "result": "Failed",
            "requestedCaseIds": list(CANONICAL_IDS), "executedCaseIds": [],
            "failure": str(error),
            "createdAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
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
                print(f"h1-nested manifest audit failed: {error}; failure receipt: {write_error}",
                      file=sys.stderr)
                return 1
        print(f"h1-nested manifest audit failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
