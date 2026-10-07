#!/usr/bin/env python3
"""Build and run R01B contention scenarios against production allocator/lock code."""
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


def require(condition, message):
    if not condition:
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


def repository_state(path):
    head = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=False)
    status = subprocess.run(["git", "-C", str(path), "status", "--short",
                             "--untracked-files=all"], capture_output=True,
                            text=True, check=False)
    lines = status.stdout.splitlines()
    return {"head": head.stdout.strip() if head.returncode == 0 else "",
            "dirty": bool(lines), "status": lines}


def run(command, cwd, receipt, phase, timeout, env=None):
    started = time.monotonic()
    completed = subprocess.run([str(item) for item in command], cwd=cwd,
                               capture_output=True, text=True, errors="replace",
                               timeout=timeout, check=False, env=env)
    receipt["commands"].append({
        "phase": phase,
        "argv": [str(item) for item in command],
        "cwd": str(cwd),
        "exitCode": completed.returncode,
        "durationSeconds": round(time.monotonic() - started, 3),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    })
    require(completed.returncode == 0,
            f"{phase} failed ({completed.returncode}): {completed.stderr.strip()}")
    return completed.stdout


def dependency_paths(output, cwd):
    text = output.replace("\\\n", " ")
    require(": " in text, "compiler dependency output is malformed")
    values = shlex.split(text.split(": ", 1)[1])
    paths = set()
    for value in values:
        path = Path(value)
        if not path.is_absolute():
            path = cwd / path
        path = path.resolve()
        if path.is_file():
            paths.add(path)
    return paths


def execute(args, receipt):
    require(sys.platform == "darwin", "R01B native contention tests require macOS baselib")
    demo = canonical_dir(args.demo_root, "demo root")
    native = canonical_dir(args.hybridclr_root, "HybridCLR root")
    runtime = canonical_dir(args.runtime_root, "il2cpp_plus root")
    installed = canonical_dir(args.installed_root, "installed il2cpp/libil2cpp")
    pins_path = canonical_file(demo / "ProjectSettings/AssemblyShadowSourcePins.json",
                               "source pins")
    pins = json.loads(pins_path.read_text(encoding="utf-8-sig"))
    external = canonical_dir(installed.parent / "external", "installed external")
    source = canonical_file(args.source or demo / "Tools/AssemblyShadow/native-tests/r01_budget_contention.cpp",
                            "R01 budget contention source")
    header = canonical_file(native / "hybridclr/metadata/InterpreterImageAdmission.h",
                            "budget header")
    interpreter = canonical_file(native / "hybridclr/metadata/InterpreterImage.cpp",
                                 "production InterpreterImage.cpp")
    lock_header = canonical_file(runtime / "libil2cpp/vm/MetadataLock.h",
                                 "production metadata lock header")
    runtime_source = canonical_file(runtime / "libil2cpp/vm/Runtime.cpp",
                                    "production Runtime.cpp")
    compiler = canonical_file(Path(shutil.which(args.compiler) or ""), "clang++")
    nm = canonical_file(Path(shutil.which("nm") or ""), "nm")
    baselib_path = args.baselib
    if baselib_path is None:
        baselib_path = (Path("/Applications/Unity/Hub/Editor") /
                        pins["unityVersion"] /
                        "Unity.app/Contents/PlaybackEngines/MacStandaloneSupport/baselib.a")
    baselib = canonical_file(baselib_path, "baselib.a")
    unity_header = canonical_file(installed / "hybridclr/generated/UnityVersion.h",
                                  "installed UnityVersion.h")
    install_receipt = canonical_file(installed / "assembly-shadow-install.json",
                                     "installed provenance")
    manifest = canonical_file(native / "hybridclr/generated/AssemblyManifest.cpp",
                              "generated AssemblyManifest.cpp")

    defines = dict(re.findall(r"^#define\s+(HYBRIDCLR_UNITY_[A-Z0-9_]+)\s+(\d+)\s*$",
                              unity_header.read_text(encoding="utf-8"), re.MULTILINE))
    flags = [
        "-std=c++11", "-O1", "-g", "-fsanitize=address", "-fno-omit-frame-pointer",
        "-ffunction-sections", "-fdata-sections", "-DBASELIB_INLINE_NAMESPACE=il2cpp_baselib",
        "-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1", "-I", str(runtime / "libil2cpp"),
        "-I", str(native), "-isystem", str(external / "baselib/Include"),
        "-isystem", str(external / "baselib/Platforms/OSX/Include"),
        "-iquote", str(installed / "utils"), "-I", str(external / "google"),
    ]
    flags += [f"-D{name}={value}" for name, value in sorted(defines.items())]
    native_sources = [native / "hybridclr/metadata" / name for name in
                      ("InterpreterImage.cpp", "InterpreterMetadataIndexRuntime.cpp", "Image.cpp", "PDBImage.cpp", "RawImage.cpp",
                       "RawImageBase.cpp", "MetadataUtil.cpp", "AssemblyShadowBridge.cpp")]
    runtime_sources = [runtime / "libil2cpp" / name for name in
                       ("vm/AssemblyShadowDiagnostics.cpp", "vm/AssemblyShadowTypeKey.cpp",
                        "vm/Runtime.cpp", "vm/Assembly.cpp", "vm-utils/VmStringUtils.cpp",
                        "char-conversions.cpp", "utils/sha1.cpp")]
    sources = [source, manifest, *native_sources, *runtime_sources]

    receipt.update({
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "compiler": {"path": str(compiler), "sha256": digest(compiler)},
        "demoRoot": str(demo),
        "hybridclrRoot": str(native),
        "runtimeRoot": str(runtime),
        "sourcePins": pins,
        "repositories": {"hybridclr": repository_state(native),
                          "il2cppPlus": repository_state(runtime)},
        "installedHeaderProvenance": {
            "root": str(installed),
            "receipt": json.loads(install_receipt.read_text(encoding="utf-8-sig")),
            "fullInstalledRuntimeVerification": False,
        },
        "boundary": (
            "Current profile-2 InterpreterImage.cpp admission/allocation, InterpreterMetadataIndexRuntime.cpp, and production il2cpp g_MetadataLock are linked; "
            "this does not exercise Assembly::Create, Unity GC, or Player publication. "
            "Worker alignment uses atomics only; no std::mutex substitutes allocator locking. "
            "Unity Player and managed publication are outside this standalone test."
        ),
        "sourceFiles": [str(path) for path in sources],
    })
    all_inputs = {source, Path(__file__).resolve(), pins_path, header, interpreter, lock_header,
                  runtime_source, compiler, nm, baselib, unity_header, install_receipt, manifest}
    for path in sources:
        dependencies = run([compiler, *flags, "-M", "-MT", "q05", path], native,
                           receipt, "dependencies", args.timeout)
        all_inputs.update(dependency_paths(dependencies, native))
    before = {path: digest(path) for path in sorted(all_inputs)}
    receipt["sourceFileHashes"] = [{"path": str(path), "sha256": value}
                                   for path, value in before.items()]

    with tempfile.TemporaryDirectory(prefix="r01b-contention-build-", dir=args.output.parent) as temp_name:
        temp = Path(temp_name)
        objects = []
        for index, path in enumerate(sources):
            obj = temp / f"source-{index}.o"
            run([compiler, *flags, "-c", path, "-o", obj], native, receipt,
                "compile", args.timeout)
            objects.append(obj)
        executable = temp / "r01b-interpreter-image-contention"
        run([compiler, "-fsanitize=address", "-pthread", "-Wl,-dead_strip",
             "-Wl,-undefined,dynamic_lookup", *objects, baselib, "-o", executable],
            native, receipt, "link", args.timeout)
        defined = run([nm, "-gU", executable], native, receipt, "defined-symbols", args.timeout)
        required_symbols = ("g_MetadataLock", "AllocImageIndex", "ReserveImageBudget", "ReserveImages")
        require(all(symbol in defined for symbol in required_symbols),
                "executable is missing a defined production allocator/lock symbol")
        receipt["definedProductionSymbols"] = [line for line in defined.splitlines()
                                              if any(symbol in line for symbol in required_symbols)]
        scenarios = []
        test_env = {**__import__("os").environ,
                    "ASAN_OPTIONS": "halt_on_error=1:abort_on_error=1"}
        scenario_names = ["serial-reserve-first", "serial-ordinary-first", "serial-reject"]
        scenario_names += [name for _ in range(args.race_repetitions)
                           for name in ("contention-accept", "contention-reject")]
        for ordinal, scenario in enumerate(scenario_names):
            output = run([executable, scenario], native, receipt, "tests", args.timeout,
                         env=test_env)
            marker = re.search(r"^r01b_concurrency_checks=(\d+) scenario=" +
                               re.escape(scenario) + r" PASS$", output, re.MULTILINE)
            require(marker is not None, f"{scenario}: native pass marker missing")
            if scenario == "contention-accept":
                require("oracle=shared-id-atomic-intervals" in output,
                        "contention acceptance serializability marker missing")
            scenarios.append({"scenario": scenario, "ordinal": ordinal, "checks": int(marker.group(1)),
                              "outputSha256": hashlib.sha256(output.encode()).hexdigest()})
        after = {path: digest(path) for path in before}
        require(after == before, "read-only production inputs changed during native checks")
        receipt.update({"scenarios": scenarios,
                        "checks": sum(item["checks"] for item in scenarios),
                        "executableSha256": digest(executable),
                        "inputsUnchanged": True,
                        "temporaryBuildOutputsRemovedOnExit": True,
                        "success": True,
                        "result": "Passed"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    demo_default = Path(__file__).resolve().parents[2]
    parser.add_argument("--hybridclr-root", type=Path,
                        default=demo_default.parent / "hybridclr")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--demo-root", type=Path, default=demo_default)
    parser.add_argument("--runtime-root", type=Path,
                        default=demo_default.parent / "il2cpp_plus")
    parser.add_argument("--installed-root", type=Path,
                        default=demo_default / "HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp")
    parser.add_argument("--source", type=Path, help="Optional prepared fixture; default is the checked-in contention fixture")
    parser.add_argument("--race-repetitions", type=int, default=3)
    parser.add_argument("--baselib", type=Path)
    parser.add_argument("--compiler", default="clang++")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    require(1 <= args.timeout <= 600, "timeout must be 1..600 seconds")
    require(1 <= args.race_repetitions <= 20, "race repetitions must be 1..20")
    output = args.output.expanduser().resolve()
    require(not output.exists() and not output.is_symlink(), f"output already exists: {output}")
    require(output.parent.is_dir(), f"output parent does not exist: {output.parent}")
    receipt = {"schemaVersion": 1, "kind": "R01BInterpreterImageContentionNative",
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
