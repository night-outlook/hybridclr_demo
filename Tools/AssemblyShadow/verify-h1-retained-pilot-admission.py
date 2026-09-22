#!/usr/bin/env python3
"""Preflight bridge-aware retained pilot history before the expensive strict seal."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import h1_graph_reuse as graph_reuse
from shadow_tools import VerificationError, require


_spec = importlib.util.spec_from_file_location(
    "h1_retained_pilot_admission_driver",
    Path(__file__).with_name("run-h1-paired-performance.py"))
driver = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(driver)


def _write_new(path: Path, value: dict) -> None:
    require(path.is_absolute() and path == path.resolve() and
            not path.exists() and not path.is_symlink(),
            "Retained pilot admission output must be a new canonical absolute path")
    require(path.parent.is_dir() and not path.parent.is_symlink(),
            "Retained pilot admission output parent is unavailable")
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
    candidate = build["sides"]["B"]["projectRoot"]
    authority = graph_reuse.verify_bridge_full(
        args.graph_reuse_bridge, candidate, args.build_map)

    attempts = driver._load_prior(
        args.pilot_index, args.protocol, args.schedule, args.build_map,
        schedule, "pilot", build,
        graph_reuse_bridge_path=args.graph_reuse_bridge,
        retained_pilot_authority=authority)
    selected = driver._selected_pilot_attempts(attempts, schedule)

    require(len(selected) == len(driver.MODES),
            "Retained pilot admission did not select exactly four modes")
    rows = []
    for attempt in selected:
        rows.append({
            "pairId": attempt["pairId"],
            "attempt": attempt["attempt"],
            "mode": attempt["mode"],
            "A": {
                "runner": attempt["A"]["runner"],
                "launchReceipt": attempt["A"]["launchReceipt"],
            },
            "B": {
                "runner": attempt["B"]["runner"],
                "launchReceipt": attempt["B"]["launchReceipt"],
            },
        })

    receipt = {
        "schemaVersion": 1,
        "kind": "H1RetainedPilotAdmissionPreflight",
        "result": "Passed",
        "scope": (
            "Bridge-authenticated retained pilot history admission only. "
            "Does not replace 8-side strict R00 reconstruction or the pilot seal."
        ),
        "protocol": driver.binding(args.protocol),
        "schedule": driver.binding(args.schedule),
        "buildMap": driver.binding(args.build_map),
        "pilotIndex": driver.binding(args.pilot_index),
        "graphReuseBridge": driver.binding(args.graph_reuse_bridge),
        "retainedPilotRunner": authority["retainedPilotRunner"],
        "pilotAttemptCount": len(driver._pilot_attempts(attempts)),
        "selectedPilotCount": len(selected),
        "selectedPilots": rows,
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
