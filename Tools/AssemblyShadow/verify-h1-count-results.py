#!/usr/bin/env python3
"""CLI entry point for the independent H1 count result verifier."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from h1_count_results import main


if __name__ == "__main__":
    raise SystemExit(main())
