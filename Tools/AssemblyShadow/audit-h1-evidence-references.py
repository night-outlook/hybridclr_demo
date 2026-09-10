"""CLI entry point for the H1 exact reference-resolution audit."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from h1_evidence_references import REPORT_NAME, VerificationError, authenticate_references


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operation", required=True, choices=("references",))
    parser.add_argument("--input-map", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = authenticate_references(args.input_map, args.output_root)
    except (VerificationError, OSError, ValueError) as error:
        print(f"references audit failed: {error}", file=sys.stderr)
        return 1
    print(f"references audit {report['status']}: {Path(args.output_root).resolve() / REPORT_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
