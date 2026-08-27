#!/usr/bin/env python3
import sys
from shadow_tools import main

if __name__ == "__main__":
    raise SystemExit(main(["verify", *sys.argv[1:]]))
