#!/usr/bin/env python3
"""Compile and run the standalone R01 recovery-classifier contract."""
from __future__ import annotations

import argparse
import datetime as datetime_module
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time


class TestFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TestFailure(message)


def canonical_directory(value: Path, label: str) -> Path:
    path = value.expanduser().resolve(strict=True)
    require(path.is_dir() and not path.is_symlink(),
            f"{label} must be a canonical directory: {path}")
    return path


def canonical_file(value: Path, label: str) -> Path:
    path = value.expanduser().resolve(strict=True)
    require(path.is_file() and not path.is_symlink(),
            f"{label} must be a canonical file: {path}")
    return path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_command(command: list[str], cwd: Path, receipt: dict, phase: str,
                timeout: int) -> subprocess.CompletedProcess[str]:
    started = time.monotonic()
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                               errors="replace", timeout=timeout, check=False)
    receipt["commands"].append({
        "phase": phase,
        "argv": command,
        "cwd": str(cwd),
        "exitCode": completed.returncode,
        "durationSeconds": round(time.monotonic() - started, 3),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    })
    require(completed.returncode == 0,
            f"{phase} failed ({completed.returncode}): {completed.stderr.strip()}")
    return completed


def execute(args: argparse.Namespace, receipt: dict) -> None:
    require(sys.platform == "darwin", "R01 recovery harness requires macOS clang++")
    demo_root = canonical_directory(args.demo_root, "Demo root")
    il2cpp_root = canonical_directory(args.il2cpp_root, "il2cpp_plus root")
    source = canonical_file(
        demo_root / "Tools/AssemblyShadow/native-tests/R01RecoveryTests.cpp",
        "R01 recovery test source")
    header = canonical_file(
        il2cpp_root / "libil2cpp/vm/AssemblyShadowRecovery.h",
        "R01 recovery header")
    compiler_path = shutil.which(args.compiler)
    require(compiler_path is not None, f"Compiler not found: {args.compiler}")
    compiler = canonical_file(Path(compiler_path), "Compiler")

    input_hashes = {
        "testSource": sha256(source),
        "recoveryHeader": sha256(header),
        "runner": sha256(Path(__file__).resolve()),
    }
    receipt.update({
        "demoRoot": str(demo_root),
        "il2cppRoot": str(il2cpp_root),
        "sourceHash": input_hashes,
        "compiler": {"path": str(compiler)},
        "boundary": (
            "C++11 native executable includes the production recovery header "
            "directly; no IL2CPP runtime, Unity, or Python model is used."
        ),
    })

    with tempfile.TemporaryDirectory(prefix="assembly-shadow-r01-recovery-") as temporary:
        executable = Path(temporary) / "r01-recovery-tests"
        command = [str(compiler), "-std=c++11", "-O1", "-g", "-Wall", "-Wextra",
                   "-Werror", "-pedantic", "-fsanitize=address",
                   "-fno-omit-frame-pointer", "-I", str(header.parent), str(source),
                   "-o", str(executable)]
        run_command(command, il2cpp_root, receipt, "compile", args.timeout)
        completed = run_command([str(executable)], il2cpp_root, receipt,
                                "tests", args.timeout)
        match = re.search(r"^r01_recovery_checks=(\d+) PASS$", completed.stdout,
                          re.MULTILINE)
        require(match is not None, "Native test count marker is missing")
        check_count = int(match.group(1))
        require(check_count >= 300,
                f"Native coverage count is unexpectedly low: {check_count}")
        receipt.update({
            "checkCount": check_count,
            "executableSha256": sha256(executable),
        })

    after_hashes = {
        "testSource": sha256(source),
        "recoveryHeader": sha256(header),
        "runner": sha256(Path(__file__).resolve()),
    }
    require(after_hashes == input_hashes, "Owned inputs changed during native validation")
    receipt["inputsUnchanged"] = True
    receipt["result"] = "Passed"
    receipt["success"] = True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--il2cpp-root", required=True, type=Path,
                        help="il2cpp_plus checkout containing libil2cpp/vm")
    parser.add_argument("--output", required=True, type=Path,
                        help="New JSON receipt path; existing files are refused")
    parser.add_argument("--demo-root", type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument("--compiler", default="clang++")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    require(1 <= args.timeout <= 600, "Timeout must be between 1 and 600 seconds")
    output = args.output.expanduser().resolve()
    require(not output.exists() and not output.is_symlink(),
            f"Output receipt already exists: {output}")
    require(output.parent.is_dir(),
            f"Output parent directory does not exist: {output.parent}")

    receipt = {
        "schemaVersion": 1,
        "kind": "R01AssemblyShadowRecoveryNative",
        "success": False,
        "result": "Failed",
        "startedUtc": datetime_module.datetime.now(
            datetime_module.timezone.utc).isoformat(),
        "commands": [],
    }
    try:
        execute(args, receipt)
    except (TestFailure, OSError, subprocess.TimeoutExpired, ValueError) as error:
        receipt["error"] = str(error)
    receipt["finishedUtc"] = datetime_module.datetime.now(
        datetime_module.timezone.utc).isoformat()
    encoded = json.dumps(receipt, indent=2) + "\n"
    try:
        with output.open("x", encoding="utf-8") as stream:
            stream.write(encoded)
    except OSError as error:
        print(encoded, end="")
        print(f"Cannot save receipt: {error}", file=sys.stderr)
        return 1
    print(json.dumps({key: receipt.get(key) for key in
                      ("success", "result", "checkCount", "inputsUnchanged", "error")} |
                     {"receipt": str(output)}))
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

