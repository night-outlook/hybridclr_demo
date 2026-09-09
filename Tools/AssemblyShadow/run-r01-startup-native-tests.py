#!/usr/bin/env python3
"""Build and run the R01 native startup observation boundary executable.

Each scenario is a fresh process.  The executable includes the production
AssemblyShadow state machine and staging parser; VM assembly enumeration,
physical lookup, exception, and image-constructor registries are explicit
native adapters.  Unity is never launched and no installed tree is modified.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time


class TestFailure(RuntimeError):
    pass


def require(value, message):
    if not value:
        raise TestFailure(message)


def canonical_file(value, label):
    path = Path(value).expanduser().resolve(strict=True)
    require(path.is_file() and not path.is_symlink(), f"{label} must be a regular file: {path}")
    return path


def canonical_dir(value, label):
    path = Path(value).expanduser().resolve(strict=True)
    require(path.is_dir() and not path.is_symlink(), f"{label} must be a regular directory: {path}")
    return path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, cwd, receipt, phase, timeout):
    started = time.monotonic()
    completed = subprocess.run([str(item) for item in command], cwd=cwd,
                               capture_output=True, text=True, errors="replace",
                               timeout=timeout, check=False,
                               env={**__import__("os").environ,
                                    "ASAN_OPTIONS": "halt_on_error=1:abort_on_error=1"}
                               if phase == "tests" else None)
    entry = {"phase": phase, "argv": [str(item) for item in command], "cwd": str(cwd),
             "exitCode": completed.returncode,
             "durationSeconds": round(time.monotonic() - started, 3),
             "stdout": completed.stdout, "stderr": completed.stderr}
    receipt["commands"].append(entry)
    require(completed.returncode == 0,
            f"{phase} failed ({completed.returncode}): {completed.stderr.strip()}")
    return completed.stdout


def dependency_paths(output, cwd):
    text = output.replace("\\\n", " ")
    require(": " in text, "compiler dependency output is malformed")
    values = shlex.split(text.split(": ", 1)[1])
    result = set()
    for value in values:
        path = Path(value)
        if not path.is_absolute():
            path = cwd / path
        path = path.resolve()
        if path.is_file():
            result.add(path)
    return result


def repository(root, configured_pin):
    completed = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                               capture_output=True, text=True, check=False)
    return {"root": str(root), "head": completed.stdout.strip(),
            "configuredPin": configured_pin,
            "headMatchesPin": completed.returncode == 0 and completed.stdout.strip() == configured_pin}


def execute(args, receipt):
    require(sys.platform == "darwin", "R01 startup native tests require macOS clang++/baselib")
    demo = canonical_dir(args.demo_root, "demo root")
    native = canonical_dir(args.hybridclr_root, "HybridCLR root")
    pins_path = canonical_file(args.pins or demo / "ProjectSettings/AssemblyShadowSourcePins.json", "source pins")
    pins = json.loads(pins_path.read_text(encoding="utf-8-sig"))
    runtime = canonical_dir(args.runtime_root or demo / pins["il2cppPlus"]["localPath"], "il2cpp_plus root")
    installed_default = demo / "HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp"
    installed = canonical_dir(args.installed_root or installed_default, "installed il2cpp/libil2cpp")
    external = canonical_dir(installed.parent / "external", "installed external")
    header = canonical_file(installed / "hybridclr/generated/UnityVersion.h", "UnityVersion.h")
    install_path = canonical_file(installed / "assembly-shadow-install.json", "install provenance")
    install = json.loads(install_path.read_text(encoding="utf-8-sig"))
    require(install.get("installMode") == "PinnedLocal", "installed runtime is not pinned-local")
    compiler = canonical_file(Path(shutil.which(args.compiler) or ""), "clang++")
    baselib = canonical_file(args.baselib or Path("/Applications/Unity/Hub/Editor") /
                             pins["unityVersion"] / "Unity.app/Contents/PlaybackEngines/MacStandaloneSupport/baselib.a",
                             "baselib.a")
    fixture = canonical_file(args.dll or demo /
                             "HybridCLRData/AssemblyShadow/ResourceBaselines/StandaloneOSX/M02-Baseline-36ca3c767e2bc9c3/CompilerInputs/Assemblies/AssemblyA.Contracts.dll",
                             "DLL fixture")
    source = canonical_file(demo / "Tools/AssemblyShadow/native-tests/r01_startup.cpp", "R01 source")
    runner = canonical_file(Path(__file__).resolve(), "R01 runner")
    defines = dict(re.findall(r"^#define\s+(HYBRIDCLR_UNITY_[A-Z0-9_]+)\s+(\d+)\s*$",
                              header.read_text(encoding="utf-8"), re.MULTILINE))
    flags = ["-std=c++11", "-O1", "-g", "-fsanitize=address", "-fno-omit-frame-pointer",
             "-ffunction-sections", "-fdata-sections", "-DBASELIB_INLINE_NAMESPACE=il2cpp_baselib",
             "-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1", "-I", str(runtime / "libil2cpp"), "-I", str(native),
             "-isystem", str(external / "baselib/Include"), "-isystem", str(external / "baselib/Platforms/OSX/Include"),
             "-iquote", str(installed / "utils"), "-I", str(external / "google")]
    flags += [f"-D{name}={value}" for name, value in sorted(defines.items())]
    native_sources = [native / "hybridclr/metadata" / name for name in
                      ("InterpreterImage.cpp", "Image.cpp", "PDBImage.cpp", "RawImage.cpp",
                       "RawImageBase.cpp", "MetadataUtil.cpp", "AssemblyShadowBridge.cpp", "InterpreterMetadataIndexRuntime.cpp")]
    runtime_sources = [runtime / "libil2cpp" / name for name in
                       ("vm/AssemblyShadowDiagnostics.cpp", "vm/AssemblyShadowTypeKey.cpp", "vm/Runtime.cpp",
                        "vm/Assembly.cpp", "os/FastReaderReaderWriterLock.cpp", "vm-utils/VmStringUtils.cpp", "char-conversions.cpp", "utils/sha1.cpp")]
    sources = [source, *native_sources, *runtime_sources]
    compiler_version = run([compiler, "--version"], demo, receipt, "compiler-version", args.timeout)
    receipt.update({"platform": platform.platform(), "architecture": platform.machine(),
                    "sourcePins": pins,
                    "compiler": {"path": str(compiler), "sha256": digest(compiler),
                                  "version": compiler_version},
                    "demoRoot": str(demo), "hybridclrRoot": str(native), "runtimeRoot": str(runtime),
                    "installedHeaderProvenance": {"root": str(installed), "receipt": install,
                                                     "header": str(header), "fullInstalledRuntimeVerification": False},
                    "repositories": {"hybridclr": repository(native, pins["hybridclr"]["revision"]),
                                     "il2cppPlus": repository(runtime, pins["il2cppPlus"]["revision"])},
                    "fixture": {"path": str(fixture), "sha256": digest(fixture)},
                    "boundary": "Production AssemblyShadow startup registration, Configure, observation, transaction APIs and recovery serializer. Physical assembly/type-handle lookup and constructor enumeration use explicit native adapters. Heap and metadata lookup failures are injected. Concurrent observation is synchronized inside Configure physical stable lookup. Generated startup schema and names are explicit fixture values. This runner does not execute MetadataCache initialization, full Runtime startup, Unity, GC or Player behavior.",
                    "sourceFiles": [str(path) for path in sources]})

    all_inputs = {pins_path, install_path, header, compiler, baselib, source, runner, fixture}
    for path in sources:
        dependency_output = run([compiler, *flags, "-M", "-MT", "r01", path], native, receipt, "dependencies", args.timeout)
        all_inputs.update(dependency_paths(dependency_output, native))
    before = {path: digest(path) for path in sorted(all_inputs)}
    receipt["sourceFileHashes"] = [{"path": str(path), "sha256": value} for path, value in before.items()]
    build_parent = demo / "_temp/AssemblyShadow/R01"
    build_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="startup-native-build-", dir=build_parent) as temp_name:
        temp = Path(temp_name)
        objects = []
        for index, path in enumerate(sources):
            obj = temp / f"source-{index}.o"
            run([compiler, *flags, "-c", path, "-o", obj], native, receipt, "compile", args.timeout)
            objects.append(obj)
        executable = temp / "r01-startup"
        run([compiler, "-fsanitize=address", "-Wl,-dead_strip", "-Wl,-undefined,dynamic_lookup",
             *objects, baselib, "-o", executable], native, receipt, "link", args.timeout)
        scenarios = []
        for scenario in ("tracking", "empty", "retry", "failed-retry", "missing", "duplicate", "bad-name", "missing-handle", "duplicate-handle", "allocation", "unknown", "heap-allocation", "validate", "published-retry", "schema"):
            output = run((["/usr/bin/env", "R01_BAD_SCHEMA=1"] if scenario == "schema" else []) + [executable, scenario, fixture], native, receipt, "tests", args.timeout)
            marker = re.search(r"^r01_startup_checks=(\d+) scenario=" + re.escape(scenario) + r" PASS$",
                               output, re.MULTILINE)
            require(marker is not None, f"{scenario}: native pass marker missing")
            scenarios.append({"scenario": scenario, "checks": int(marker[1]),
                              "outputSha256": hashlib.sha256(output.encode()).hexdigest()})
            if scenario == "published-retry":
                require("r01_initializer_failure=pass" in output and "syntheticPublication=1" in output,
                        "post-publication retry boundary marker missing")
        after = {path: digest(path) for path in before}
        require(after == before, "read-only input changed during native checks")
        receipt.update({"scenarios": scenarios, "checks": sum(item["checks"] for item in scenarios),
                        "executableSha256": digest(executable), "inputsUnchanged": True,
                        "temporaryBuildOutputsRemovedOnExit": True, "success": True, "result": "Passed"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hybridclr-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--demo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--installed-root", type=Path)
    parser.add_argument("--pins", type=Path)
    parser.add_argument("--baselib", type=Path)
    parser.add_argument("--dll", type=Path)
    parser.add_argument("--compiler", default="clang++")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    require(1 <= args.timeout <= 600, "timeout must be 1..600 seconds")
    output = args.output.expanduser().resolve()
    require(not output.exists() and not output.is_symlink(), f"output already exists: {output}")
    require(output.parent.is_dir(), f"output parent does not exist: {output.parent}")
    receipt = {"schemaVersion": 1, "kind": "R01AssemblyShadowStartupNative",
               "success": False, "result": "Failed",
               "startedUtc": dt.datetime.now(dt.timezone.utc).isoformat(), "commands": []}
    try:
        execute(args, receipt)
    except (TestFailure, OSError, subprocess.TimeoutExpired, ValueError, KeyError) as error:
        receipt["error"] = str(error)
    receipt["finishedUtc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: receipt.get(key) for key in
                      ("success", "result", "checks", "inputsUnchanged", "error")} |
                     {"receipt": str(output)}))
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
