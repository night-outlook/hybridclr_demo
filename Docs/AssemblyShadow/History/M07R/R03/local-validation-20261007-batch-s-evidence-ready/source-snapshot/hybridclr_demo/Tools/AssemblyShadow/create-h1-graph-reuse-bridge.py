#!/usr/bin/env python3
"""Create one fail-closed bridge for the retained 69130bbb candidate performance graph."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import h1_graph_reuse as reuse
from shadow_tools import VerificationError, require


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--build-map", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)

    project = args.project.resolve(strict=True)
    build_map = reuse.canonical_file(args.build_map.resolve(strict=True), "build map")
    output = args.output
    require(output.is_absolute() and output == output.resolve() and
            not output.exists() and not output.is_symlink(),
            "Graph reuse bridge output must be a new canonical absolute path")
    require(output.parent.is_dir() and not output.parent.is_symlink(),
            "Graph reuse bridge output parent is unavailable")

    receipt = reuse.create_receipt(project, build_map, "B")
    with output.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    reuse.verify_bridge_full(output, project, build_map)
    print("Passed: " + str(output), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (VerificationError, OSError, KeyError, TypeError, ValueError) as error:
        print("[FAIL] " + str(error))
        raise SystemExit(1)
