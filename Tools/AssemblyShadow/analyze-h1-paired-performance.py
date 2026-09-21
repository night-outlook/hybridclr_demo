#!/usr/bin/env python3
"""Analyze a preregistered H1 paired R00 sample index with authenticated graph reuse."""

import argparse
import hashlib
import json
from pathlib import Path

import h1_graph_reuse as graph_reuse
import r00_results
from h1_paired_performance import analyze_sample_index
from shadow_tools import VerificationError, read_json, require


def _digest(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "analysis binding file is missing: " + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _binding(path: Path) -> dict[str, str]:
    path = path.resolve(strict=True)
    require(path.is_file() and not path.is_symlink(), "analysis binding is not a regular file: " + str(path))
    return {"path": str(path), "sha256": _digest(path)}


def _write_new(path: Path, value: dict) -> None:
    if path.exists() or path.is_symlink():
        raise VerificationError("analysis output must be new: " + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def _prepare_reuse(sample_index: Path, pilot_verification: Path,
                   bridge_path: Path) -> dict:
    sample_index = sample_index.resolve(strict=True)
    pilot_verification = pilot_verification.resolve(strict=True)
    bridge_path = bridge_path.resolve(strict=True)
    index = read_json(sample_index)
    build_binding = index.get("buildMap")
    require(type(build_binding) is dict, "sample index build-map binding is missing")
    build_map = Path(build_binding.get("path", "")).resolve(strict=True)
    require(build_binding == _binding(build_map), "sample index build-map binding changed")

    pilot_binding = _binding(pilot_verification)
    bridge_binding = _binding(bridge_path)
    seal = read_json(pilot_verification)
    require(seal.get("kind") == "H1PilotVerificationReceipt" and
            seal.get("status") == "PassedStrictReconstructionAndStatGuardSealed",
            "final analysis requires a passed pilot verification seal")
    require(seal.get("graphReuseBridge") == bridge_binding,
            "pilot verification seal graph reuse bridge binding mismatch")

    attempts = index.get("attempts")
    require(type(attempts) is list, "sample index attempts are missing")
    formal = [row for row in attempts if type(row) is dict and row.get("phase") == "formal"]
    require(formal, "final analysis requires formal attempts")
    for row in formal:
        require(row.get("pilotVerification") == pilot_binding,
                "formal attempt switched pilot verification seal")
        require(row.get("graphReuseBridge") == bridge_binding,
                "formal attempt switched graph reuse bridge")

    bridge = read_json(bridge_path)
    project = Path(bridge.get("projectRoot", "")).resolve(strict=True)
    authority = graph_reuse.verify_bridge_full(bridge_path, project, build_map)
    return {
        "authority": authority,
        "pilotVerification": pilot_binding,
        "graphReuseBridge": bridge_binding,
        "buildMap": build_map,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-index", required=True, type=Path)
    parser.add_argument("--pilot-verification-receipt", required=True, type=Path)
    parser.add_argument("--graph-reuse-bridge", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("analysis output must be new: " + str(args.output))
    try:
        reuse = _prepare_reuse(
            args.sample_index, args.pilot_verification_receipt, args.graph_reuse_bridge)

        def verified_launch(launch_path, expected_mode=None):
            launch = read_json(Path(launch_path))
            project = Path(launch["projectRoot"]).resolve(strict=True)
            authority = graph_reuse.authority_for_project(reuse["authority"], project)
            return r00_results.verify_suite(
                launch_path, expected_mode=expected_mode, pairing_authority=authority)

        result = analyze_sample_index(args.sample_index, verifier=verified_launch)
        result["pilotVerification"] = reuse["pilotVerification"]
        result["graphReuseBridge"] = reuse["graphReuseBridge"]
    except Exception as error:
        result = {"schemaVersion": 1, "kind": "H1ControlledPairedPerformanceFailure", "result": "Failed",
                  "error": str(error), "sampleIndex": str(args.sample_index.resolve())}
        _write_new(args.output, result)
        print("H1 paired analysis Failed: " + str(args.output))
        return 1
    _write_new(args.output, result)
    print("H1 paired analysis " + result["result"] + ": " + str(args.output))
    return 0 if result["result"] == "Passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
