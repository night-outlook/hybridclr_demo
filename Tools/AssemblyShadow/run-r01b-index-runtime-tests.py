#!/usr/bin/env python3
"""Run the actual unwired R01B metadata-index runtime adapter tests."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True


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
    record = {"phase": phase, "argv": [str(arg) for arg in command],
              "cwd": str(cwd), "exitCode": completed.returncode}
    if phase == "dependencies":
        record["stdoutSha256"] = hashlib.sha256(completed.stdout.encode()).hexdigest()
    else:
        record["stdout"] = completed.stdout
    record["stderr"] = completed.stderr
    receipt["commands"].append(record)
    require(completed.returncode == 0,
            f"{phase} failed ({completed.returncode}): {completed.stderr.strip()}")
    return completed


def dependency_paths(output: str, cwd: Path) -> set[Path]:
    flattened = output.replace("\\\n", " ")
    require(": " in flattened, "compiler dependency output is malformed")
    paths = set()
    for value in shlex.split(flattened.split(": ", 1)[1]):
        path = Path(value)
        if not path.is_absolute():
            path = cwd / path
        path = path.resolve(strict=True)
        require(path.is_file(), f"dependency is not a file: {path}")
        paths.add(path)
    return paths


def production_contract(test_source: Path, runtime_source: Path, kernel: Path) -> None:
    test = test_source.read_text(encoding="utf-8")
    runtime = runtime_source.read_text(encoding="utf-8")
    require('#include "metadata/InterpreterMetadataIndexRuntime.h"' in test,
            "adapter does not include the runtime production API")
    require("AssemblyShadowBridge::GetPrivateImage" in test,
            "adapter does not provide controlled TLS membership")
    require("ReserveImages" in runtime and "CurrentOwner" in runtime and
            "GetPublishedImage" in runtime,
            "runtime production implementation is incomplete")
    require("class InterpreterMetadataIndexCodec" in kernel.read_text(encoding="utf-8"),
            "actual codec kernel dependency is missing")


def execute(args: argparse.Namespace, receipt: dict) -> None:
    require(sys.platform == "darwin", "R01B index-runtime harness requires macOS clang++")
    demo = canonical_directory(args.demo_root, "Demo root")
    native = canonical_directory(args.native_root, "Active HybridCLR root")
    runtime_root = canonical_directory(args.runtime_root, "Active il2cpp_plus root")
    test_source = canonical_file(demo / "Tools/AssemblyShadow/native-tests/r01b-index-runtime.cpp",
                                 "index-runtime adapter")
    runtime_source = canonical_file(native / "hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp",
                                    "InterpreterMetadataIndexRuntime.cpp")
    runtime_header = canonical_file(native / "hybridclr/metadata/InterpreterMetadataIndexRuntime.h",
                                    "InterpreterMetadataIndexRuntime.h")
    kernel = canonical_file(native / "hybridclr/metadata/InterpreterMetadataIndexCodec.h",
                            "InterpreterMetadataIndexCodec.h")
    runner = canonical_file(Path(__file__), "index-runtime runner")
    compiler_path = shutil.which(args.compiler)
    require(compiler_path is not None, f"Compiler not found: {args.compiler}")
    compiler = canonical_file(Path(compiler_path), "Compiler")
    production_contract(test_source, runtime_source, kernel)

    flags = ["-std=c++11", "-O1", "-g", "-Wall", "-Wextra",
             "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-pthread",
             "-DBASELIB_INLINE_NAMESPACE=il2cpp_baselib",
             "-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1"]
    include_flags = ["-I", str(runtime_root / "libil2cpp"),
                     "-I", str(native), "-I", str(native / "hybridclr")]
    receipt.update({"platform": platform.platform(), "architecture": platform.machine(),
                    "roots": {"demo": str(demo), "native": str(native), "runtime": str(runtime_root)},
                    "boundary": "Actual InterpreterMetadataIndexRuntime.cpp and InterpreterMetadataIndexCodec.h are exercised with fake opaque InterpreterImage pointers and a controlled AssemblyShadowBridge TLS-membership stub. No full InterpreterImage construction, transaction wiring, Unity, install, or Player semantics are claimed."})

    with tempfile.TemporaryDirectory(prefix="assembly-shadow-r01b-index-runtime-") as temporary_name:
        temporary = Path(temporary_name)
        dependencies = {test_source, runtime_source, runtime_header, kernel, runner, compiler}
        for source in (test_source, runtime_source):
            dependency_output = run([str(compiler), *flags, *include_flags,
                                     "-M", "-MT", "r01b-index-runtime", str(source)],
                                    runtime_root, receipt, "dependencies")
            dependencies.update(dependency_paths(dependency_output.stdout, runtime_root))
        before = {path: sha256(path) for path in sorted(dependencies)}
        receipt.update({"inputs": {str(path): digest for path, digest in before.items()},
                        "dependencyCount": len(before)})

        executable = temporary / "r01b-index-runtime"
        run([str(compiler), *flags, *include_flags, str(test_source), str(runtime_source),
             "-o", str(executable)], runtime_root, receipt, "compile-index-runtime")
        environment = os.environ.copy()
        environment["ASAN_OPTIONS"] = "halt_on_error=1:abort_on_error=1"
        environment["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
        result = run([str(executable)], runtime_root, receipt, "run-index-runtime", environment)
        marker = "r01b_index_runtime_checks="
        require(marker in result.stdout and result.stdout.rstrip().endswith(" PASS"),
                "index-runtime coverage marker is missing")
        receipt["checkCount"] = int(result.stdout.split(marker, 1)[1].split()[0])
        receipt["executableSha256"] = sha256(executable)

    after = {path: sha256(path) for path in before}
    changed = [str(path) for path in before if before[path] != after[path]]
    require(not changed, "production/test inputs changed during validation: " + ", ".join(changed))
    receipt.update(inputsUnchanged=True, productionContract="Passed", result="Passed", success=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-root", type=Path, required=True)
    parser.add_argument("--native-root", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--compiler", default="clang++")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    require(not output.exists() and not output.is_symlink(), f"Receipt already exists: {output}")
    require(output.parent.is_dir(), f"Receipt parent does not exist: {output.parent}")
    receipt = {"schemaVersion": 1, "kind": "R01BIndexRuntimeNative", "success": False,
               "result": "Failed", "startedUtc": dt.datetime.now(dt.timezone.utc).isoformat(), "commands": []}
    try:
        execute(args, receipt)
    except (TestFailure, OSError, subprocess.SubprocessError, ValueError) as error:
        receipt["error"] = str(error)
    receipt["finishedUtc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: receipt.get(key) for key in ("success", "result", "checkCount", "dependencyCount", "inputsUnchanged", "error")} |
                     {"receipt": str(output)}))
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
