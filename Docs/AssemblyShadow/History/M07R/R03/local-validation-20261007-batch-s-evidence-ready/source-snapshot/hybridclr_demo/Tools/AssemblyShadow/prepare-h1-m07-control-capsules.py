#!/usr/bin/env python3
"""Generate mode-specific R01 Control capsules from immutable M07 build evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import m07_results as m07
import r01_early_capsule as capsule
import runpy


def require(value: object, message: str) -> None:
    if not value:
        raise ValueError(message)


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical_file(value: Path) -> Path:
    require(value.is_absolute() and value == value.resolve(strict=True) and value.is_file() and not value.is_symlink(),
            "Expected canonical regular file: " + str(value))
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-manifest", required=True, type=Path)
    parser.add_argument("--on-build", required=True, type=Path)
    parser.add_argument("--off-build", required=True, type=Path)
    parser.add_argument("--replay-receipt", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    fixture, on_path, off_path, replay = map(canonical_file,
        (args.fixture_manifest, args.on_build, args.off_build, args.replay_receipt))
    output = args.output_root
    require(output.is_absolute() and output == output.resolve() and not output.exists() and output.parent.is_dir(),
            "Output root must be a new canonical path")

    manifest, baseline, fixtures, rejected, resources = m07.verify_inputs(fixture)
    m07.prepare_fixture_resources(manifest, baseline, fixtures, resources)
    on = m07.verify_player(on_path, manifest, baseline, resources, "NativeOn")
    off = m07.verify_player(off_path, manifest, baseline, resources, "NativeOff")
    m07.verify_replay(replay, manifest, baseline, fixtures, rejected, on, resources)
    context = {"manifest": manifest, "baseline": baseline, "fixtures": fixtures, "on": on, "off": off}

    output.mkdir()
    rows = []
    modes = tuple(mode for mode in m07.MODES if mode != "T07-14-FeatureOff")
    for mode in modes:
        path = output / (mode + ".capsule")
        data = capsule.from_context(context, "Control", m07.MODE_PATCH[mode], fixture)
        receipt = capsule.write_capsule(path, data)
        rows.append({"mode": mode, "patchId": data["patchId"], "path": str(path),
                     "sha256": receipt["sha256"], "length": receipt["length"]})
    report = {"schemaVersion": 1, "kind": "H1M07BuildBoundControlCapsules", "status": "Passed",
              "diagnosticOnly": True, "buildBound": True, "workingCopySourceAdmission": False,
              "fixtureManifestPath": str(fixture), "fixtureManifestSha256": digest(fixture),
              "onBuildPath": str(on_path), "onBuildSha256": digest(on_path),
              "offBuildPath": str(off_path), "offBuildSha256": digest(off_path),
              "replayReceiptPath": str(replay), "replayReceiptSha256": digest(replay),
              "capsules": rows,
              "note": "Capsules are admitted against immutable M07 build evidence; no current-working-tree source equivalence is claimed."}
    (output / "capsules.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": "Passed", "capsuleCount": len(rows), "output": str(output)}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print("Failed: " + str(error), file=__import__("sys").stderr)
        raise SystemExit(1)
