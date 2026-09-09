#!/usr/bin/env python3
"""Run the bounded R01B metadata range helper and InterpreterImage syntax check."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import re
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


def run(command: list[str], cwd: Path, receipt: dict, phase: str,
        environment: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                               errors="replace", check=False, env=environment)
    receipt["commands"].append({"phase": phase, "argv": [str(arg) for arg in command],
                                 "cwd": str(cwd), "exitCode": completed.returncode,
                                 "stdout": completed.stdout, "stderr": completed.stderr})
    require(completed.returncode == 0,
            f"{phase} failed ({completed.returncode}): {completed.stderr.strip()}")
    return completed


def production_contract(source: Path, helper: Path) -> None:
    image = source.read_text(encoding="utf-8")
    helper_text = helper.read_text(encoding="utf-8")
    require("#include \"InterpreterMetadataRange.h\"" in image,
            "InterpreterImage.cpp does not include the production range helper")
    require("InterpreterMetadataRange::DecodeRange" in image and
            "InterpreterMetadataRange::ResolveOffset" in image and
            "InterpreterMetadataRange::DecodeEndpoint" in image and
            "InterpreterMetadataRange::ValidateCustomAttributeLayout" in image,
            "production range helper calls are incomplete")
    require("CountRawRange" in helper_text,
            "range helper raw count validation is missing")
    require("cur.fieldStart - last.fieldStart" not in image and
            "cur.methodStart - last.methodStart" not in image and
            "def->fieldStart + i" not in image and
            "nextTypeRange.startOffset - curTypeRange.startOffset" not in image and
            "typeDefine->interfaceOffsetsStart + index" not in image,
            "encoded metadata arithmetic remains in InterpreterImage.cpp")


def execute(args: argparse.Namespace, receipt: dict) -> None:
    require(sys.platform == "darwin", "R01B index-range harness requires macOS clang++")
    demo = canonical_directory(args.demo_root, "Demo root")
    native = canonical_directory(args.native_root, "Active HybridCLR root")
    installed = canonical_directory(args.installed_root, "Accepted R01 generated installed root")
    source = canonical_file(native / "hybridclr/metadata/InterpreterImage.cpp", "InterpreterImage.cpp")
    helper = canonical_file(native / "hybridclr/metadata/InterpreterMetadataRange.h",
                            "InterpreterMetadataRange.h")
    codec = canonical_file(native / "hybridclr/metadata/InterpreterMetadataIndexCodec.h",
                           "InterpreterMetadataIndexCodec.h")
    test_source = canonical_file(demo / "Tools/AssemblyShadow/native-tests/r01b-index-range.cpp",
                                 "index-range adapter")
    runner = canonical_file(Path(__file__), "index-range runner")
    version_header = canonical_file(installed / "hybridclr/generated/UnityVersion.h", "generated UnityVersion.h")
    compiler_path = shutil.which(args.compiler)
    require(compiler_path is not None, f"Compiler not found: {args.compiler}")
    compiler = canonical_file(Path(compiler_path), "Compiler")
    production_contract(source, helper)

    defines = dict(re.findall(r"^#define\s+(HYBRIDCLR_UNITY_[A-Z0-9_]+)\s+(\d+)\s*$",
                              version_header.read_text(encoding="utf-8"), re.MULTILINE))
    external = canonical_directory(installed.parent / "external", "Installed external root")
    runtime = canonical_directory(args.runtime_root, "Active il2cpp_plus root")
    include_flags: list[str] = []
    for switch, directory in [
        ("-I", runtime / "libil2cpp"), ("-I", native), ("-I", native / "hybridclr"),
        ("-isystem", external / "baselib/Include"),
        ("-isystem", external / "baselib/Platforms/OSX/Include"),
        ("-iquote", installed / "utils"), ("-I", external / "google"),
        ("-I", external / "bdwgc/include"), ("-I", external / "bdwgc/libatomic_ops/src"),
        ("-I", external / "xxHash")]:
        include_flags += [switch, str(canonical_directory(directory, f"include root {directory}"))]
    flags = ["-std=c++11", "-O1", "-g", "-Wall", "-Wextra",
             "-DBASELIB_INLINE_NAMESPACE=il2cpp_baselib",
             "-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1", "-DIL2CPP_DEBUG=1"]
    flags += [f"-D{name}={value}" for name, value in sorted(defines.items())]
    input_paths = (source, helper, codec, test_source, runner, version_header, compiler)
    receipt.update({"platform": platform.platform(), "architecture": platform.machine(),
                    "roots": {"demo": str(demo), "native": str(native),
                               "runtime": str(runtime), "installed": str(installed)},
                    "inputs": {str(path): sha256(path) for path in input_paths},
                    "boundary": "The production range helper is exercised with the actual sparse-page codec; InterpreterImage.cpp is syntax-checked with active source roots. No Unity, Player, install, or full runtime acceptance is claimed."})

    with tempfile.TemporaryDirectory(prefix="assembly-shadow-r01b-index-range-") as temporary:
        executable = Path(temporary) / "r01b-index-range"
        run([str(compiler), "-std=c++11", "-O1", "-g", "-Wall", "-Wextra",
             "-fsanitize=address", "-fno-omit-frame-pointer", "-I", str(native / "hybridclr"),
             str(test_source), "-o", str(executable)], runtime, receipt, "compile-index-range")
        environment = os.environ.copy()
        environment["ASAN_OPTIONS"] = "halt_on_error=1:abort_on_error=1"
        result = run([str(executable)], runtime, receipt, "run-index-range", environment)
        match = re.search(r"^r01b_index_range_checks=(\d+) PASS$", result.stdout, re.MULTILINE)
        require(match is not None and int(match.group(1)) >= 20,
                "index-range adapter coverage marker is missing")
        receipt["checkCount"] = int(match.group(1))
        receipt["executableSha256"] = sha256(executable)
        run([str(compiler), *flags, *include_flags, "-fsyntax-only", str(source)], native,
            receipt, "syntax-interpreter-image")

    after = {str(path): sha256(path) for path in input_paths}
    require(after == receipt["inputs"], "owned inputs changed during validation")
    receipt.update(inputsUnchanged=True, productionContract="Passed", result="Passed", success=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-root", type=Path, required=True)
    parser.add_argument("--native-root", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--installed-root", type=Path, required=True)
    parser.add_argument("--compiler", default="clang++")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    require(not output.exists() and not output.is_symlink(), f"Receipt already exists: {output}")
    require(output.parent.is_dir(), f"Receipt parent does not exist: {output.parent}")
    receipt = {"schemaVersion": 1, "kind": "R01BIndexRangeNative", "success": False,
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
