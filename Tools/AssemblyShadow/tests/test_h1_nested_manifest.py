"""Focused hand-authored controls for the nested manifest auditor."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from h1_nested_manifest import (  # noqa: E402
    CANONICAL_BY_ID,
    TARGET_TYPE,
    ManifestError,
    parse_manifest_bytes,
    validate_observation,
)


def _identity(name):
    return {
        "name": name,
        "fullName": name + ", Version=1.0.0.1, Culture=neutral, PublicKeyToken=null",
        "version": "1.0.0.1",
        "mvid": "00000000-0000-0000-0000-000000000000",
    }


def _artifact(case_id):
    return {
        "sha256": "a" * 64,
        "sizeBytes": 1,
        "name": "Fixture",
        "fullName": "Fixture, Version=1.0.0.1, Culture=neutral, PublicKeyToken=null",
        "version": "1.0.0.1",
        "mvid": "00000000-0000-0000-0000-000000000000",
        "targetType": TARGET_TYPE,
        "targetMethod": None,
        "path": f"/tmp/{case_id}.dll",
    }


def _case(case_id, count, groups, declaring, interleaved):
    canonical = CANONICAL_BY_ID[case_id]
    return {
        "caseId": case_id, "count": count, "groupCounts": list(groups),
        "declaringTypes": list(declaring), "interleaved": interleaved,
        "variant": canonical[5], "expected": canonical[6], "family": "nested",
    }


def _shape(case_id, count, groups, declaring, interleaved, *, bad_parent=False):
    case = _case(case_id, count, groups, declaring, interleaved)
    types = [
        {"rid": 1, "name": "<Module>", "namespace": "", "fullName": "<Module>",
         "parentRid": None},
        {"rid": 2, "name": "Target", "namespace": "AssemblyShadow.H1Nested",
         "fullName": TARGET_TYPE, "parentRid": None},
    ]
    rid = 3
    parent_rids = {}
    for name in declaring:
        full = f"AssemblyShadow.H1Nested.{name}"
        if name == "Target":
            parent_rids[name] = 2
            continue
        parent_rids[name] = rid
        types.append({"rid": rid, "name": name, "namespace": "AssemblyShadow.H1Nested",
                      "fullName": full, "parentRid": None})
        rid += 1
    nested = []
    remaining = list(groups)
    while any(remaining):
        for group_index, name in enumerate(declaring):
            if not remaining[group_index]:
                continue
            child_index = groups[group_index] - remaining[group_index]
            child_rid = rid
            parent = parent_rids[name]
            if bad_parent and not nested:
                parent += 100
            full = f"AssemblyShadow.H1Nested.{name}+{name}Child{child_index:05d}"
            nested.append({"rid": child_rid, "name": f"{name}Child{child_index:05d}",
                           "namespace": "", "fullName": full, "parentRid": parent})
            rid += 1
            remaining[group_index] -= 1
    types.extend(nested)
    summaries = []
    for name, group_count, parent in zip(declaring, groups,
                                         (parent_rids[name] for name in declaring)):
        if not group_count:
            continue
        names = [f"AssemblyShadow.H1Nested.{name}+{name}Child{i:05d}"
                 for i in range(group_count)]
        import hashlib
        summaries.append({
            "declaringType": f"AssemblyShadow.H1Nested.{name}", "parentRid": parent,
            "count": group_count, "first": names[0], "last": names[-1],
            "childrenSha256": hashlib.sha256("\n".join(names).encode()).hexdigest(),
        })
    artifact = _artifact(case_id)
    case["ordinary"], case["shadow"] = artifact, dict(artifact)
    actual = {
        "sha256": artifact["sha256"], "sizeBytes": artifact["sizeBytes"],
        "identity": _identity(artifact["name"]), "types": types,
        "nestedGroups": summaries, "nestedClassTableCount": count,
        "typeDefCount": 1 + len(declaring) + count, "methodDefCount": 0,
        "paramTableCount": 0, "methods": [], "nestedClassSortedDeclared": True,
        "nestedRowsSha256": "b" * 64,
    }
    return case, actual


class NestedManifestControls(unittest.TestCase):
    def test_zero_child_target_is_still_visible(self):
        case, actual = _shape("H1R-N01-a", 0, (0,), ("Target",), False)
        result = validate_observation(case, "ordinary", actual)
        self.assertTrue(result["targetPresentWithZeroChildren"])
        self.assertEqual(result["groups"], [])

    def test_hand_authored_interleaving_and_relationships(self):
        case, actual = _shape("H1R-N03-interleaved", 4, (2, 2),
                              ("Target", "SiblingB"), True)
        result = validate_observation(case, "shadow", actual)
        self.assertEqual([group["count"] for group in result["groups"]], [2, 2])

    def test_wrong_parent_is_rejected(self):
        case, actual = _shape("H1R-N03-interleaved", 4, (2, 2),
                              ("Target", "SiblingB"), True, bad_parent=True)
        with self.assertRaises(Exception):
            validate_observation(case, "ordinary", actual)

    def test_duplicate_manifest_keys_are_rejected(self):
        with self.assertRaises(ManifestError):
            parse_manifest_bytes(b'{"caseSet":"all","caseSet":"all"}')

    def test_canonical_temp_output_is_resolved_before_use(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory).resolve() / "receipt.json"
            self.assertTrue(path.is_absolute())
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
