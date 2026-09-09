#!/usr/bin/env python3
"""Run the bounded R01B generic-constraint adapter and production syntax checks."""
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


def run(command: list[str], cwd: Path, receipt: dict, phase: str) -> subprocess.CompletedProcess[str]:
    environment = None
    if phase == "run-adapter":
        environment = os.environ.copy()
        environment["ASAN_OPTIONS"] = "halt_on_error=1:abort_on_error=1"
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                               errors="replace", check=False, env=environment)
    receipt["commands"].append({"phase": phase, "argv": [str(arg) for arg in command],
                                 "cwd": str(cwd), "exitCode": completed.returncode,
                                 "stdout": completed.stdout, "stderr": completed.stderr})
    require(completed.returncode == 0,
            f"{phase} failed ({completed.returncode}): {completed.stderr.strip()}")
    return completed


def production_contract(header: Path, source: Path, global_metadata: Path) -> None:
    image = header.read_text(encoding="utf-8") + "\n" + source.read_text(encoding="utf-8")
    metadata = global_metadata.read_text(encoding="utf-8")
    require("std::vector<uint32_t> _genericConstraintStarts;" in image,
            "interpreter raw-start sidecar is missing")
    require("InterpreterGenericConstraintMap::Initialize(_genericConstraintStarts" in image,
            "sidecar sentinel initialization is missing")
    require("GetGenericParameterConstraintFromIndex(const Il2CppGenericParameter* genericParameter" in image,
            "interpreter handle-aware lookup is missing")
    require("InterpreterGenericConstraintMap::RecordRow" in image and
            "InterpreterGenericConstraintMap::ResolveRawIndex" in image,
            "production generic constraint map integration is missing")
    require("->GetGenericParameterConstraintFromIndex(genericParameter, index);" in metadata,
            "interpreter dispatch does not pass the parameter handle")
    dispatch = metadata.index("if (hybridclr::metadata::IsInterpreterIndex(genericParameter->ownerIndex))")
    addition = metadata.index("index = genericParameter->constraintsStart + index;")
    require(dispatch < addition, "AOT narrow addition occurs before interpreter dispatch")
    require("genericParam.constraintsStart = EncodeWithIndex" not in image,
            "interpreter path still narrows an encoded constraint start")


def execute(args: argparse.Namespace, receipt: dict) -> None:
    require(sys.platform == "darwin", "R01B constraint harness requires macOS clang++")
    demo = canonical_directory(args.demo_root, "Demo root")
    native = canonical_directory(args.native_root, "Active HybridCLR root")
    runtime = canonical_directory(args.runtime_root, "Active il2cpp_plus root")
    installed = canonical_directory(args.installed_root, "Accepted R01 generated installed root")
    source = canonical_file(native / "hybridclr/metadata/InterpreterImage.cpp", "InterpreterImage.cpp")
    header = canonical_file(native / "hybridclr/metadata/InterpreterImage.h", "InterpreterImage.h")
    global_metadata = canonical_file(runtime / "libil2cpp/vm/GlobalMetadata.cpp", "GlobalMetadata.cpp")
    helper = canonical_file(native / "hybridclr/metadata/InterpreterGenericConstraintMap.h",
                            "InterpreterGenericConstraintMap.h")
    test_source = canonical_file(demo / "Tools/AssemblyShadow/native-tests/r01b-constraint-adapter.cpp", "constraint adapter")
    runner = canonical_file(Path(__file__), "constraint runner")
    version_header = canonical_file(installed / "hybridclr/generated/UnityVersion.h", "generated UnityVersion.h")
    compiler_path = shutil.which(args.compiler)
    require(compiler_path is not None, f"Compiler not found: {args.compiler}")
    compiler = canonical_file(Path(compiler_path), "Compiler")
    production_contract(header, source, global_metadata)

    defines = dict(re.findall(r"^#define\s+(HYBRIDCLR_UNITY_[A-Z0-9_]+)\s+(\d+)\s*$",
                              version_header.read_text(encoding="utf-8"), re.MULTILINE))
    external = canonical_directory(installed.parent / "external", "Installed external root")
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
    input_paths = (source, header, helper, global_metadata, test_source, runner, version_header, compiler)
    receipt.update({"platform": platform.platform(), "architecture": platform.machine(),
                    "roots": {"demo": str(demo), "native": str(native), "runtime": str(runtime), "installed": str(installed)},
                    "inputs": {str(path): sha256(path) for path in input_paths},
                    "boundary": "Actual production translation units are syntax-checked; behavior uses a focused adapter with the production Il2CppGenericParameter layout. No Unity, Player, install, or runtime acceptance is claimed."})

    with tempfile.TemporaryDirectory(prefix="assembly-shadow-r01b-constraint-") as temporary:
        executable = Path(temporary) / "r01b-constraint-adapter"
        run([str(compiler), *flags, "-fsanitize=address", "-fno-omit-frame-pointer",
             *include_flags, str(test_source), "-o", str(executable)], runtime, receipt, "compile-adapter")
        result = run([str(executable)], runtime, receipt, "run-adapter")
        match = re.search(r"^r01b_constraint_checks=(\d+) PASS$", result.stdout, re.MULTILINE)
        require(match is not None and int(match.group(1)) >= 19, "constraint adapter coverage marker is missing")
        receipt["checkCount"] = int(match.group(1))
        receipt["executableSha256"] = sha256(executable)
        for production_source, label in ((source, "syntax-interpreter-image"), (global_metadata, "syntax-global-metadata")):
            run([str(compiler), *flags, *include_flags, "-fsyntax-only", str(production_source)], native, receipt, label)

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
    receipt = {"schemaVersion": 1, "kind": "R01BConstraintNative", "success": False,
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
