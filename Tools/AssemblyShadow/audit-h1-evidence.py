"""CLI entry point for narrowly scoped H1 evidence audits."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from h1_evidence_members import REPORT_NAME, VerificationError, authenticate_members


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operation", required=True, choices=("members",))
    parser.add_argument("--input-map", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = authenticate_members(args.input_map, args.output_root)
    except (VerificationError, OSError, ValueError) as error:
        # authenticate_members retains a report for failures after output-root
        # creation. CLI errors before that point remain ordinary nonzero failures.
        print(f"members audit failed: {error}", file=sys.stderr)
        return 1
    print(f"members audit {report['status']}: {Path(args.output_root).resolve() / REPORT_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
