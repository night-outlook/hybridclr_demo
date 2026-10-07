#!/usr/bin/env python3
"""Run focused R01B type-cache insertion fault and concurrency checks."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile


class TestFailure(RuntimeError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise TestFailure(detail)


def canonical_file(value: Path, label: str) -> Path:
    path = value.expanduser().resolve(strict=True)
    require(path.is_file(), f"{label} must be a file: {path}")
    return path


def canonical_directory(value: Path, label: str) -> Path:
    path = value.expanduser().resolve(strict=True)
    require(path.is_dir(), f"{label} must be a directory: {path}")
    return path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], cwd: Path, receipt: dict, phase: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy() if phase == "run-type-cache" else None
    if environment is not None:
        environment["ASAN_OPTIONS"] = "halt_on_error=1:abort_on_error=1"
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                               errors="replace", check=False, env=environment)
    receipt["commands"].append({"phase": phase, "argv": [str(arg) for arg in command],
                                 "cwd": str(cwd), "exitCode": completed.returncode,
                                 "stdout": completed.stdout, "stderr": completed.stderr})
    require(completed.returncode == 0,
            f"{phase} failed ({completed.returncode}): {completed.stderr.strip()}")
    return completed


def production_contract(test_source: Path, helper: Path) -> None:
    test = test_source.read_text(encoding="utf-8")
    implementation = helper.read_text(encoding="utf-8")
    require('#include "metadata/InterpreterTypeCacheInsertion.h"' in test,
            "adapter does not include the production type-cache helper")
    require("GetOrInsert" in implementation,
            "production type-cache helper is missing")
    require("types.reserve" in implementation and "indices.insert" in implementation,
            "production helper preparation path is incomplete")


def execute(args: argparse.Namespace, receipt: dict) -> None:
    require(sys.platform == "darwin", "R01B type-cache harness requires macOS clang++")
    demo = canonical_directory(args.demo_root, "Demo root")
    native = canonical_directory(args.native_root, "Active HybridCLR root")
    helper = canonical_file(native / "hybridclr/metadata/InterpreterTypeCacheInsertion.h",
                            "InterpreterTypeCacheInsertion.h")
    kernel = canonical_file(native / "hybridclr/metadata/InterpreterMetadataIndexCodec.h",
                            "InterpreterMetadataIndexCodec.h")
    test_source = canonical_file(demo / "Tools/AssemblyShadow/native-tests/r01b-type-cache.cpp",
                                 "type-cache adapter")
    runner = canonical_file(Path(__file__), "type-cache runner")
    compiler_path = shutil.which(args.compiler)
    require(compiler_path is not None, f"Compiler not found: {args.compiler}")
    compiler = canonical_file(Path(compiler_path), "Compiler")
    production_contract(test_source, helper)
    input_paths = (helper, kernel, test_source, runner, compiler)
    receipt.update({"platform": platform.platform(), "architecture": platform.machine(),
                    "roots": {"demo": str(demo), "native": str(native)},
                    "inputs": {str(path): sha256(path) for path in input_paths},
                    "boundary": "The actual production InterpreterTypeCacheInsertion helper is exercised with controlled allocation and map failures, retries, deduplication, amortized growth, and externally serialized concurrent writers. No production translation-unit or Unity/Player acceptance is claimed."})

    with tempfile.TemporaryDirectory(prefix="assembly-shadow-r01b-type-cache-") as temporary:
        executable = Path(temporary) / "r01b-type-cache"
        run([str(compiler), "-std=c++11", "-O1", "-g", "-Wall", "-Wextra",
             "-fsanitize=address", "-fno-omit-frame-pointer", "-I", str(native / "hybridclr"),
             str(test_source), "-o", str(executable)], native, receipt, "compile-type-cache")
        result = run([str(executable)], native, receipt, "run-type-cache")
        marker = "r01b_type_cache_checks="
        require(marker in result.stdout and result.stdout.rstrip().endswith(" PASS"),
                "type-cache adapter coverage marker is missing")
        receipt["checkCount"] = int(result.stdout.split(marker, 1)[1].split()[0])
        receipt["executableSha256"] = sha256(executable)

    after = {str(path): sha256(path) for path in input_paths}
    require(after == receipt["inputs"], "owned inputs changed during validation")
    receipt.update(inputsUnchanged=True, productionContract="Passed", result="Passed", success=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-root", type=Path, required=True)
    parser.add_argument("--native-root", type=Path, required=True)
    parser.add_argument("--compiler", default="clang++")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    require(not output.exists() and not output.is_symlink(), f"Receipt already exists: {output}")
    require(output.parent.is_dir(), f"Receipt parent does not exist: {output.parent}")
    receipt = {"schemaVersion": 1, "kind": "R01BTypeCacheNative", "success": False,
               "result": "Failed", "startedUtc": dt.datetime.now(dt.timezone.utc).isoformat(), "commands": []}
    try:
        execute(args, receipt)
    except (TestFailure, OSError, subprocess.SubprocessError, ValueError) as error:
        receipt["error"] = str(error)
    receipt["finishedUtc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: receipt.get(key) for key in ("success", "result", "checkCount", "inputsUnchanged", "error")} |
                     {"receipt": str(output)}))
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
