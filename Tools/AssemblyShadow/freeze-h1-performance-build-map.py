#!/usr/bin/env python3
"""Freeze authenticated H1 A/B controlled Development builds into a strict build map."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import h1_paired_performance as analysis
from shadow_tools import require


def canonical_dir(value: Path, label: str) -> Path:
    require(value.is_absolute() and not value.is_symlink() and value == value.resolve(strict=True) and value.is_dir(),
            label + " must be a canonical directory")
    return value.resolve(strict=True)


def canonical_file(value: Path, label: str) -> Path:
    require(value.is_absolute() and not value.is_symlink() and value == value.resolve(strict=True) and value.is_file(),
            label + " must be a canonical regular file")
    return value.resolve(strict=True)


def binding(path: Path) -> dict[str, str]:
    return {"path": str(path), "sha256": analysis.digest(path)}


def build_entry(receipt_path: Path, evidence_path: Path, feature: str) -> dict:
    receipt_path = canonical_file(receipt_path, feature + " receipt")
    evidence_path = canonical_file(evidence_path, feature + " controlled evidence")
    receipt = analysis.read_json(receipt_path)
    expected_variant = "NativeOn" if feature == "on" else "NativeOff"
    require(receipt.get("schemaVersion") == 1 and receipt.get("milestone") == "M07" and
            receipt.get("variant") == expected_variant,
            feature + " M07 receipt header differs")
    return {
        "feature": feature,
        "development": True,
        "nativeCompilerConfiguration": "Release",
        "buildGuid": receipt.get("buildGuid"),
        "playerOutput": receipt.get("playerOutput"),
        "receipt": binding(receipt_path),
        "controlledEvidence": binding(evidence_path),
    }


def side(project: Path, fixture: Path, replay: Path,
         on_receipt: Path, on_evidence: Path,
         off_receipt: Path, off_evidence: Path) -> dict:
    project = canonical_dir(project, "side project")
    fixture = canonical_file(fixture, "side fixture manifest")
    replay = canonical_file(replay, "side replay receipt")
    return {
        "projectRoot": str(project),
        "fixtureManifest": binding(fixture),
        "replayReceipt": binding(replay),
        "builds": {
            "on": build_entry(on_receipt, on_evidence, "on"),
            "off": build_entry(off_receipt, off_evidence, "off"),
        },
    }


def freeze_map(side_a: dict, side_b: dict) -> tuple[dict, dict]:
    value = {
        "schemaVersion": 1,
        "kind": "H1ControlledBuildMap",
        "status": "Frozen",
        "protocolId": analysis.PROTOCOL_ID,
        "target": analysis.TARGET,
        "architecture": analysis.ARCHITECTURE,
        "configuration": {
            "development": True,
            "nativeCompilerConfiguration": "Release",
            "nativeAssertions": False,
        },
        "comparability": {},
        "sides": {"A": side_a, "B": side_b},
    }
    _bindings, facts = analysis._build_bindings(value)
    value["comparability"] = {
        field: {"A": facts["A"][field], "B": facts["B"][field]}
        for field in analysis.MATCH_FIELDS + analysis.EXPECTED_DIFFERENCES
    }
    result = analysis.validate_build_map(value)
    require(result.get("status") == "ComparabilityPassed",
            "controlled build map does not satisfy comparability: " + "; ".join(result.get("reasons", [])))
    receipt = {
        "schemaVersion": 1,
        "kind": "H1ControlledBuildMapFreezeReceipt",
        "result": "Passed",
        "protocolId": analysis.PROTOCOL_ID,
        "matchedFields": result["matchedFields"],
        "expectedDifferent": result["expectedDifferent"],
        "acceptanceClaimed": False,
        "scope": "Authenticated build comparability only; no performance samples or H1 acceptance.",
    }
    return value, receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for prefix in ("a", "b"):
        parser.add_argument(f"--side-{prefix}-project", required=True, type=Path)
        parser.add_argument(f"--side-{prefix}-fixture-manifest", required=True, type=Path)
        parser.add_argument(f"--side-{prefix}-replay-receipt", required=True, type=Path)
        parser.add_argument(f"--side-{prefix}-on-receipt", required=True, type=Path)
        parser.add_argument(f"--side-{prefix}-on-evidence", required=True, type=Path)
        parser.add_argument(f"--side-{prefix}-off-receipt", required=True, type=Path)
        parser.add_argument(f"--side-{prefix}-off-evidence", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    def make(prefix: str) -> dict:
        return side(
            getattr(args, f"side_{prefix}_project"),
            getattr(args, f"side_{prefix}_fixture_manifest"),
            getattr(args, f"side_{prefix}_replay_receipt"),
            getattr(args, f"side_{prefix}_on_receipt"),
            getattr(args, f"side_{prefix}_on_evidence"),
            getattr(args, f"side_{prefix}_off_receipt"),
            getattr(args, f"side_{prefix}_off_evidence"),
        )

    value, receipt = freeze_map(make("a"), make("b"))
    output = args.output
    require(output.is_absolute() and output == output.resolve() and not output.exists() and
            output.parent.is_dir() and not output.is_symlink(),
            "output must be a new canonical file in an existing directory")
    with output.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
    receipt.update(buildMapPath=str(output), buildMapSha256=analysis.digest(output))
    receipt_path = output.with_name(output.stem + "-freeze-receipt.json")
    require(not receipt_path.exists() and not receipt_path.is_symlink(),
            "freeze receipt output already exists")
    with receipt_path.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
