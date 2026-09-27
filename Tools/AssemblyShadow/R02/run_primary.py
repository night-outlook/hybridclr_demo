#!/usr/bin/env python3
"""Primary host checks; cannot confer Unity/IL2CPP Player acceptance."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
from evidence import run, write, binding
from managed import run_suite


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--il2cpp-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--dotnet", default="dotnet")
    p.add_argument("--skip-managed", action="store_true", help="Explicit unavailable host compiler, never a complete pass")
    args = p.parse_args(argv)
    project = Path(__file__).resolve().parents[3]
    native = args.il2cpp_root.resolve(strict=True)
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    commands = [
        ("source", [sys.executable, str(native / "tools/r02/finalize_sources.py"), "--verify", "--output", str(out / "source.json")], 300),
        ("native", [sys.executable, str(native / "tools/r02/run_tests.py"), "--output", str(out / "native"), "--sanitizers"], 900),
        ("revision", [sys.executable, str(native / "tools/r02/run_revision_tests.py"), "--output", str(out / "revision"), "--sanitizers"], 900),
        ("codec-storage", [sys.executable, str(Path(__file__).parent / "codec_memory.py"),
            "--hybridclr-root", str(native.parent / "hybridclr"), "--output", str(out / "codec-storage")], 300),
        ("python", [sys.executable, "-m", "unittest", "discover", "-s", str(Path(__file__).parent / "tests"), "-v"], 180),
    ]
    rows = []
    env = dict(os.environ); env["PYTHONPATH"] = str(Path(__file__).parent) + os.pathsep + str(Path(__file__).parent.parent)
    for label, command, timeout in commands:
        receipt = run(command, project, out / (label + "-command"), timeout, env)
        rows.append({"cell": label, "result": receipt["result"], "receipt": binding(out / (label + "-command/command.json"))})
    dotnet = shutil.which(args.dotnet)
    if args.skip_managed or not dotnet:
        rows.append({"cell": "managed", "result": "Unavailable", "reason": "Host .NET SDK not run", "unityPlayerRun": False})
    else:
        csproj = Path(__file__).parent / "ManagedTests/ManagedTests.csproj"
        rows.extend(run_suite(dotnet, csproj, project, out, env))
    success = all(row["result"] == "Passed" for row in rows)
    result = {"kind": "R02PrimaryValidation", "result": "Passed" if success else "IncompleteOrFailed", "cells": rows,
              "unityPlayerRun": False, "runtimeAcceptance": False}
    write(out / "results.json", result); print(json.dumps(result))
    return 0 if success else 1


if __name__ == "__main__": raise SystemExit(main())
