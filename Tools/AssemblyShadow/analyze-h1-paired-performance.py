#!/usr/bin/env python3
"""Analyze a preregistered H1 paired R00 sample index."""
import argparse
import json
from pathlib import Path

from h1_paired_performance import analyze_sample_index
from shadow_tools import VerificationError


def _write_new(path: Path, value: dict) -> None:
    if path.exists() or path.is_symlink():
        raise VerificationError("analysis output must be new: " + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-index", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("analysis output must be new: " + str(args.output))
    try:
        result = analyze_sample_index(args.sample_index)
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
