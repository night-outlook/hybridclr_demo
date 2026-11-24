#!/usr/bin/env python3
"""D5-specific Local entry point, currently DRY ADMISSION ONLY.

This module intentionally contains no Unity/IL2CPP/Player launch path.
The underlying admission remains closed until a separately reviewed
immutable approval envelope and explicit user authorization are committed.
Do not substitute any B1/current-native historical runner.
"""
from d5b_local_admission import main


if __name__ == "__main__":
    raise SystemExit(main())
