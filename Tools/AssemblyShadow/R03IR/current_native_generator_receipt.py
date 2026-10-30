#!/usr/bin/env python3
"""Source/host-only check of a freshly compiled R03 IR fixture generator.

Fresh net8.0 outputs are distinct from historical S and Unity Player evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

PINNED_IR_SHA256 = "8d0b28cbca4d889801883ad436c51c215b913f1645055590980f902f1e80fffd"
PINNED_IR_MVID = "597eb18e-e0e7-6f8b-7e4a-6cdaabf9d1ff"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    record = {}
    for key, value in pairs:
        require(key not in record, "Duplicate JSON key: " + key)
        record[key] = value
    return record


def load(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink(), "Missing/symlink evidence file: " + str(path))
    result = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    require(type(result) is dict, "JSON evidence must be one object")
    return result


def file_hash(path: Path) -> tuple[str, int]:
    require(path.is_file() and not path.is_symlink(), "Missing/symlink fixture: " + str(path))
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest(), len(data)


def original_target(inventory: dict) -> str:
    files = inventory.get("files")
    require(type(files) is list and len(files) == 15, "Exactly 15 newly generated original fixtures")
    require(all(type(row) is dict and type(row.get("path")) is str
                and type(row.get("sha256")) is str and HEX64.fullmatch(row["sha256"])
                for row in files), "Malformed original fixture inventory entry")
    names = [row["path"] for row in files]
    require(len(set(names)) == 15, "Duplicated original fixture inventory path")
    matches = [row for row in files if row["path"] == "virtual-slot/Methods.dll"]
    require(len(matches) == 1, "Exactly one new original virtual-slot target")
    return matches[0]["sha256"]


def inspect_ir(root: Path, original_sha: str) -> dict:
    require(root.is_dir() and not root.is_symlink(), "Missing/symlink IR output root")
    receipt = load(root / "ir-target.json")
    actual, size = file_hash(root / "Methods.dll")
    expected = {
        "kind": "R03IRSideEffectFixture", "result": "GeneratedNotRuntimeValidated",
        "assembly": "Methods", "mvid": PINNED_IR_MVID,
        "sha256": PINNED_IR_SHA256, "instanceField": "R03.Node.stable",
        "method": "R03.Node.Keep", "layoutEditorAdmission": "Passed",
        "sourceMode": "SupplementaryIR",
    }
    require(type(receipt.get("schemaVersion")) is int and receipt["schemaVersion"] == 1,
            "Wrong IR receipt version")
    for key, value in expected.items():
        require(type(receipt.get(key)) is str and receipt[key] == value,
                "Wrong IR field: " + key)
    for key, value in (("expectedReturn", 42),
                       ("expectedIncrementPerCall", 1), ("size", size)):
        require(type(receipt.get(key)) is int and receipt[key] == value,
                "Wrong IR integer: " + key)
    for key, value in (("sideEffectInstructionsVerified", True),
                       ("originalSFixtureUnchanged", True),
                       ("runtimeAcceptance", False)):
        require(receipt.get(key) is value, "Wrong IR boolean: " + key)
    require(actual == PINNED_IR_SHA256 == receipt["sha256"],
            "Real IR binary bytes do not equal the pinned target")
    require(actual != original_sha, "IR target equals original virtual-slot fixture")
    return {"sha256": actual, "mvid": receipt["mvid"], "bytes": size,
            "receiptSha256": file_hash(root / "ir-target.json")[0]}


def verify(original_inventory_path: Path, first: Path, repeat: Path) -> dict:
    require(first != repeat and first.resolve(strict=False) != repeat.resolve(strict=False),
            "Two distinct fresh IR generation roots required")
    original = original_target(load(original_inventory_path))
    a = inspect_ir(first, original)
    b = inspect_ir(repeat, original)
    require(a["sha256"] == b["sha256"] and a["mvid"] == b["mvid"] and
            a["bytes"] == b["bytes"] and a["receiptSha256"] == b["receiptSha256"],
            "Independent fresh IR generations differ")
    return {"schemaVersion": 1, "kind": "R03IRGeneratorPreLocalHostProof",
            "result": "PassedPinnedFreshGeneratorBytesAndRepeatability_HostOnly",
            "originalRegeneratedFixtureCount": 15,
            "originalVirtualSlotSha256": original, "first": a, "repeat": b,
            "net8CompilationProvenByCaller": False,
            "historicalOriginalSIndependentlyAccepted": False,
            "unityOrPlayerExecuted": False, "R03Accepted": False,
            "ReadyForHumanReviewGate": False, "runtimeAcceptance": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", required=True, type=Path)
    parser.add_argument("--first", required=True, type=Path)
    parser.add_argument("--repeat", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.original, args.first, args.repeat), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
