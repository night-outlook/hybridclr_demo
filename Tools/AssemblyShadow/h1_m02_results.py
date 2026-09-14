#!/usr/bin/env python3
"""Compatibility entry point. H1 parsing is owned by m02_results itself."""
import m02_results as m02


def install() -> None:
    """Deprecated no-op retained for callers of the former wrapper."""


def _current_parse(path, raw):
    return m02._reflection_parse(path, raw)


def main(argv=None):
    return m02.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
