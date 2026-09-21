#!/usr/bin/env python3
"""Strictly preflight retained candidate ON pilots through bridge-aware R01EarlyStartup reconstruction.

This is a read-only diagnostic gate before the full 8-side pilot seal.  It
verifies the three retained candidate side-B ON pilot launches (NoPatch, P01,
P03) using the fully authenticated graph-reuse authority, so both Baseline and
Control early-capsule reconstruction are exercised before paying the full seal
cost.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from pathlib import Path

import h1_graph_reuse as graph_reuse
from shadow_tools import VerificationError, require


_driver_spec = importlib.util.spec_from_file_location(
    "h1_retained_early_preflight_driver",
    Path(__file__).with_name("run-h1-paired-performance.py"))
driver = importlib.util.module_from_spec(_driver_spec)
_driver_spec.loader.exec_module(driver)

ON_MODES = ("R00-ON-NoPatch", "R00-ON-P01", "R00-ON-P03")


def _write_new(path: Path, value: dict) -> None:
    require(path.is_absolute() and path == path.resolve() and
            not path.exists() and not path.is_symlink(),
            "Retained early preflight output must be a new canonical absolute path")
    require(path.parent.is_dir() and not path.parent.is_symlink(),
            "Retained early preflight output parent is unavailable")
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", required=True, type=driver._m07.canonical_file)
    parser.add_argument("--schedule", required=True, type=driver._m07.canonical_file)
    parser.add_argument("--build-map", required=True, type=driver._m07.canonical_file)
    parser.add_argument("--pilot-index", required=True, type=driver._m07.canonical_file)
    parser.add_argument("--graph-reuse-bridge", required=True, type=driver._m07.canonical_file)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)

    protocol = driver._validate_protocol(args.protocol)
    schedule = driver._validate_schedule(args.schedule, args.protocol, protocol)
    build = driver._validate_build(args.build_map, protocol)
    attempts = driver._load_prior(
        args.pilot_index, args.protocol, args.schedule, args.build_map, schedule, "pilot", build)
    selected = driver._selected_pilot_attempts(attempts, schedule)

    candidate = build["sides"]["B"]
    authority = graph_reuse.verify_bridge_full(
        args.graph_reuse_bridge, candidate["projectRoot"], args.build_map)

    by_mode = {row["mode"]: row for row in selected}
    require(all(mode in by_mode for mode in ON_MODES),
            "Retained pilot index does not contain all three candidate ON modes")

    rows = []
    started_all = time.time()
    for mode in ON_MODES:
        attempt = by_mode[mode]
        launch_path, launch_binding = driver.bound_file(
            attempt["B"]["launchReceipt"], "retained early preflight " + mode + ".B.launchReceipt")
        require(launch_path == Path(attempt["B"]["launchReceipt"]["path"]).resolve(strict=True),
                "Retained early preflight launch path changed")
        started = time.time()
        verified = driver._r00.verify_suite(
            launch_path, expected_mode=mode, pairing_authority=authority)
        ended = time.time()
        require(verified.get("result") == "Passed" and
                verified.get("requestedModeIds") == [mode] and
                verified.get("executedModeIds") == [mode],
                "Retained early preflight strict R00 verification failed: " + mode)
        rows.append({
            "mode": mode,
            "pairId": attempt["pairId"],
            "attempt": attempt["attempt"],
            "side": "B",
            "launchReceipt": launch_binding,
            "result": "Passed",
            "durationSeconds": ended - started,
            "sourcePins": verified.get("sourcePins"),
        })

    receipt = {
        "schemaVersion": 1,
        "kind": "H1RetainedEarlyReusePreflight",
        "result": "Passed",
        "scope": (
            "Read-only strict bridge-aware verification of retained candidate side-B ON pilots. "
            "Exercises R01EarlyStartup Baseline and Control capsule reconstruction before the full pilot seal."
        ),
        "protocol": driver.binding(args.protocol),
        "schedule": driver.binding(args.schedule),
        "buildMap": driver.binding(args.build_map),
        "pilotIndex": driver.binding(args.pilot_index),
        "graphReuseBridge": driver.binding(args.graph_reuse_bridge),
        "modes": rows,
        "modeCount": len(rows),
        "durationSeconds": time.time() - started_all,
    }
    _write_new(args.output, receipt)
    print("Passed: " + str(args.output), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (VerificationError, OSError, KeyError, TypeError, ValueError) as error:
        print("[FAIL] " + str(error), flush=True)
        raise SystemExit(1)
