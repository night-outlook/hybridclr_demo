#!/usr/bin/env python3
"""Build and run the bounded production custom-attribute writer/batch test.

Each invocation writes to a fresh R01B run directory and records immutable input,
compiler, dependency, build, and execution evidence.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


class TestFailure(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise TestFailure(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, cwd, log_path, env=None):
    result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, env=env, check=False)
    log_path.write_bytes(result.stdout)
    return result.returncode


def claim_run_dir(root):
    root.mkdir(parents=True, exist_ok=True)
    serial = 1
    while True:
        candidate = root / "attribute-batch-run-{}".format(serial)
        try:
            candidate.mkdir()
            return candidate
        except FileExistsError:
            serial += 1


def dependency_paths(path):
    if not path.exists():
        return []
    tokens = path.read_text(encoding="utf-8", errors="replace").replace("\\\n", " ").split()
    result = []
    for token in tokens[1:]:
        candidate = Path(token)
        if candidate.exists() and candidate not in result:
            result.append(candidate)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo-root", type=Path, required=True)
    parser.add_argument("--native-root", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--installed-root", type=Path, required=True)
    parser.add_argument("--compiler", default="clang++")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    demo = args.demo_root.resolve(strict=True)
    native = args.native_root.resolve(strict=True)
    runtime = args.runtime_root.resolve(strict=True)
    installed = args.installed_root.resolve(strict=True)
    source = demo / "Tools/AssemblyShadow/native-tests/r01b-attribute-batch.cpp"
    writer = native / "hybridclr/metadata/CustomAttributeDataWriter.h"
    batch = native / "hybridclr/metadata/CustomAttributeTypeIndexBatch.h"
    memory_read = runtime / "libil2cpp/utils/MemoryRead.cpp"
    memory = runtime / "libil2cpp/utils/Memory.cpp"
    platform_memory = runtime / "libil2cpp/os/Posix/Memory.cpp"
    assertion = runtime / "libil2cpp/os/Generic/Assert.cpp"
    compiler = Path(shutil.which(args.compiler) or "").resolve()
    require(source.is_file() and writer.is_file() and batch.is_file(), "owned inputs are missing")
    require(memory_read.is_file() and memory.is_file() and platform_memory.is_file() and assertion.is_file() and compiler.is_file(),
            "runtime MemoryRead/Memory/Assert or compiler is missing")
    output = args.output.resolve()
    require(not output.exists() and output.parent.is_dir(), "receipt already exists or parent is missing")
    runner = Path(__file__).resolve()

    run_dir = claim_run_dir(demo / "_temp/AssemblyShadow/R01B")
    release = run_dir / "attribute-batch-release"
    sanitizer = run_dir / "attribute-batch-asan-ubsan"
    release_log = run_dir / "attribute-batch-release.log"
    sanitizer_log = run_dir / "attribute-batch-asan-ubsan.log"
    release_build_log = run_dir / "attribute-batch-release-build.log"
    sanitizer_build_log = run_dir / "attribute-batch-asan-ubsan-build.log"
    dependency_file = run_dir / "attribute-batch-dependencies.d"

    external = installed.parent / "external"
    include_flags = [
        "-I", str(runtime / "libil2cpp"), "-I", str(native),
        "-I", str(native / "hybridclr"),
        "-isystem", str(external / "baselib/Include"),
        "-isystem", str(external / "baselib/Platforms/OSX/Include"),
        "-iquote", str(installed / "utils"), "-I", str(external / "google"),
        "-I", str(external / "bdwgc/include"),
        "-I", str(external / "bdwgc/libatomic_ops/src"),
        "-I", str(external / "xxHash"),
    ]
    version_header = installed / "hybridclr/generated/UnityVersion.h"
    require(version_header.is_file(), "installed UnityVersion.h is missing")
    defines = []
    for match in re.finditer(r"^#define\s+(HYBRIDCLR_UNITY_[A-Z0-9_]+)\s+(\d+)\s*$",
                             version_header.read_text(encoding="utf-8"), re.MULTILINE):
        defines.append("-D{}={}".format(match.group(1), match.group(2)))
    common = [str(compiler), "-std=c++11", "-Wall", "-Wextra", "-Wno-unused-parameter",
              "-DBASELIB_INLINE_NAMESPACE=il2cpp_baselib", "-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1",
              "-DIL2CPP_DEBUG=0", "-DIL2CPP_ENABLE_ASSERTIONS=0"] + defines + include_flags
    runtime_sources = (memory_read, memory, platform_memory, assertion)
    release_command = common + ["-O2", "-DNDEBUG", str(source), *map(str, runtime_sources), "-o", str(release)]
    sanitizer_command = common + ["-O1", "-g", "-fno-omit-frame-pointer", "-fsanitize=address,undefined",
                                  str(source), *map(str, runtime_sources), "-o", str(sanitizer)]
    dependency_command = common + ["-M", str(source), *map(str, runtime_sources)]

    input_paths = (source, writer, batch, *runtime_sources, version_header, compiler, runner)
    inputs = {str(path): sha256(path) for path in input_paths}
    compiler_version = subprocess.run([str(compiler), "--version"], stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, check=False).stdout.decode("utf-8", "replace").strip()
    receipt = {"schemaVersion": 1, "kind": "R01BCustomAttributeBatchNative",
               "success": False, "runDirectory": str(run_dir), "inputsBefore": inputs,
               "compiler": {"path": str(compiler), "sha256": inputs[str(compiler)], "version": compiler_version},
               "runner": {"path": str(runner), "sha256": inputs[str(runner)]}, "commands": []}
    dependency_exit = run(dependency_command, runtime, dependency_file)
    require(dependency_exit == 0, "dependency discovery failed before compilation")
    dependency_before = {str(path): sha256(path) for path in dependency_paths(dependency_file)}
    release_build_exit = run(release_command, runtime, release_build_log)
    sanitizer_build_exit = run(sanitizer_command, runtime, sanitizer_build_log)
    release_exit = run([str(release)], runtime, release_log) if release.exists() else 127
    sanitizer_env = os.environ.copy()
    sanitizer_env["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1:abort_on_error=1"
    sanitizer_env["UBSAN_OPTIONS"] = "halt_on_error=1"
    sanitizer_exit = run([str(sanitizer)], runtime, sanitizer_log, sanitizer_env) if sanitizer.exists() else 127

    def checks(path):
        match = re.search(r"r01b_attribute_batch_checks=(\d+) PASS", path.read_text(encoding="utf-8", errors="replace")) if path.exists() else None
        return int(match.group(1)) if match else None

    release_checks = checks(release_log)
    sanitizer_checks = checks(sanitizer_log)
    failures = []
    for name, code in (("release_build", release_build_exit), ("asan_ubsan_build", sanitizer_build_exit),
                       ("dependency_scan", dependency_exit), ("release_run", release_exit),
                       ("asan_ubsan_run", sanitizer_exit)):
        if code != 0:
            failures.append("{} exit {}".format(name, code))
    if release_checks is None or sanitizer_checks is None:
        failures.append("missing PASS marker")
    elif release_checks < 19 or sanitizer_checks < 19:
        failures.append("insufficient checks")
    dependency_after = {path: sha256(Path(path)) for path in dependency_before}
    if dependency_after != dependency_before:
        failures.append("transitive dependency changed during run")
    after = {str(path): sha256(path) for path in input_paths}
    if after != inputs:
        failures.append("input changed during run")
    receipt.update({"finishedUtc": dt.datetime.now(dt.timezone.utc).isoformat(), "failureReasons": failures,
                    "inputsAfter": after, "inputsUnchanged": after == inputs,
                    "dependencyHashesBefore": dependency_before, "dependencyHashesAfter": dependency_after,
                    "dependenciesUnchanged": dependency_before == dependency_after,
                    "controlledAdapters": ["Exception Raise and OutOfMemory throw adapters", "Runtime Memory callbacks inject null malloc/calloc"],
                    "limits": ["Private abandonment/retry tests do not execute InterpreterImage or cai publication", "No Player or whole-runtime concurrency claim"],
                    "releaseChecks": release_checks, "asanUbsanChecks": sanitizer_checks,
                    "status": "passed; production writer and batch only; no Player claim" if not failures else "failed; evidence retained",
                    "success": not failures,
                    "artifacts": {str(path.name): {"path": str(path), "sha256": sha256(path) if path.exists() else None}
                                  for path in (release, sanitizer, dependency_file, release_log, sanitizer_log,
                                               release_build_log, sanitizer_build_log)},
                    "dependencies": [{"path": str(path), "sha256": sha256(path)} for path in dependency_paths(dependency_file)],
                    "commands": [{"phase": "release-build", "argv": release_command, "exit": release_build_exit},
                                 {"phase": "asan-ubsan-build", "argv": sanitizer_command, "exit": sanitizer_build_exit},
                                 {"phase": "dependency-scan", "argv": dependency_command, "exit": dependency_exit},
                                 {"phase": "release-run", "exit": release_exit}, {"phase": "asan-ubsan-run", "exit": sanitizer_exit}]})
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(output), "success": receipt["success"],
                      "releaseChecks": release_checks, "asanUbsanChecks": sanitizer_checks}))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
