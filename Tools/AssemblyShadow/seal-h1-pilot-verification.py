#!/usr/bin/env python3
"""Strictly reconstruct all completed pilots once and seal a reusable formal-admission receipt."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from shadow_tools import VerificationError, require


_driver_spec = importlib.util.spec_from_file_location(
    "h1_pilot_seal_driver", Path(__file__).with_name("run-h1-paired-performance.py"))
driver = importlib.util.module_from_spec(_driver_spec)
_driver_spec.loader.exec_module(driver)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", required=True, type=driver._m07.canonical_file)
    parser.add_argument("--schedule", required=True, type=driver._m07.canonical_file)
    parser.add_argument("--build-map", required=True, type=driver._m07.canonical_file)
    parser.add_argument("--pilot-index", required=True, type=driver._m07.canonical_file)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)

    output = args.output
    require(output.is_absolute() and output == output.resolve() and not output.exists() and
            not output.is_symlink(), "Pilot verification output must be a new canonical absolute path")
    require(output.parent.is_dir() and not output.parent.is_symlink(),
            "Pilot verification output parent is unavailable")

    protocol = driver._validate_protocol(args.protocol)
    schedule = driver._validate_schedule(args.schedule, args.protocol, protocol)
    build = driver._validate_build(args.build_map, protocol)
    attempts = driver._load_prior(
        args.pilot_index, args.protocol, args.schedule, args.build_map, schedule, "pilot", build)

    receipt = driver.seal_pilot_verification(
        attempts, schedule, build, args.protocol, args.schedule, args.build_map, args.pilot_index)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")

    driver.verify_pilot_verification(
        output, attempts, schedule, args.protocol, args.schedule, args.build_map)
    print("Passed: " + str(output), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (VerificationError, OSError, KeyError, TypeError, ValueError) as error:
        print("[FAIL] " + str(error))
        raise SystemExit(1)
