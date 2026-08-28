#!/usr/bin/env python3
"""Build/run the real M03 parser under ASan without modifying installed trees."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
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


def require(condition, detail):
    if not condition:
        raise TestFailure(detail)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def required_path(value, directory=False):
    path = Path(value).expanduser()
    # SDK headers legitimately use symlinks. All inputs are read-only; resolve
    # to and hash the actual target rather than rejecting Apple's SDK layout.
    path = path.resolve(strict=True)
    require(path.is_dir() if directory else path.is_file(), f"Invalid input path: {path}")
    return path


def run_command(argv, cwd, receipt, phase, timeout=60):
    started = time.monotonic()
    record = {"phase": phase, "argv": [str(arg) for arg in argv], "cwd": str(cwd)}
    receipt["commands"].append(record)
    environment = None
    if phase == "tests":
        environment = os.environ.copy()
        environment["ASAN_OPTIONS"] = "halt_on_error=1:abort_on_error=1"
        record["environmentOverrides"] = {"ASAN_OPTIONS": environment["ASAN_OPTIONS"]}
    try:
        result = subprocess.run(record["argv"], cwd=cwd, capture_output=True, text=True,
                                errors="replace", timeout=timeout, check=False, env=environment)
        record.update(exitCode=result.returncode, durationSeconds=round(time.monotonic() - started, 3),
                      stderr=result.stderr)
        if phase == "dependencies":
            record["stdoutSha256"] = hashlib.sha256(result.stdout.encode()).hexdigest()
        else:
            record["stdout"] = result.stdout
        require(result.returncode == 0, f"{phase} failed ({result.returncode}): {result.stderr.strip()}")
        return result.stdout
    except subprocess.TimeoutExpired as error:
        record.update(exitCode=None, timedOut=True, durationSeconds=round(time.monotonic() - started, 3))
        raise TestFailure(f"{phase} exceeded {timeout} seconds") from error


def repository_info(root, pin):
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel", "HEAD"],
                            capture_output=True, text=True, timeout=15, check=False)
    require(result.returncode == 0, f"Cannot inspect repository: {root}")
    lines = result.stdout.splitlines()
    require(len(lines) == 2 and Path(lines[0]).resolve() == root, f"Path is not a Git root: {root}")
    return {"root": str(root), "head": lines[1], "configuredPin": pin,
            "headMatchesPin": lines[1] == pin}


def dependencies(output, cwd):
    flattened = output.replace("\\\n", " ")
    require(": " in flattened, "Compiler did not return a Make dependency rule")
    return {required_path(cwd / value) for value in shlex.split(flattened.split(": ", 1)[1])}


def execute(args, receipt):
    require(sys.platform == "darwin", "This focused ASan/linker harness currently supports macOS only")
    demo = required_path(args.demo_root, directory=True)
    pins_path = required_path(args.pins or demo / "ProjectSettings/AssemblyShadowSourcePins.json")
    pins = json.loads(pins_path.read_text(encoding="utf-8-sig"))
    require(pins.get("schemaVersion") == 1, "Unsupported source-pins schema")
    entries = pins.get("repositories", pins)
    native = required_path(args.native_root or demo / entries["hybridclr"]["localPath"], directory=True)
    runtime = required_path(args.runtime_root or demo / entries["il2cppPlus"]["localPath"], directory=True)
    require(len({demo, native, runtime}) == 3, "Demo/native/runtime roots must be distinct")
    installed = required_path(args.installed_root or demo / "HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp", directory=True)
    external = required_path(installed.parent / "external", directory=True)
    version_header = required_path(installed / "hybridclr/generated/UnityVersion.h")
    install_receipt_path = required_path(installed / "assembly-shadow-install.json")
    install_receipt = json.loads(install_receipt_path.read_text(encoding="utf-8-sig"))
    require(install_receipt.get("installMode") == "PinnedLocal", "External headers require a PinnedLocal install receipt")
    require(install_receipt.get("unityVersion") == pins.get("unityVersion"), "Installed Unity version differs from source pins")
    require(install_receipt.get("target") == pins.get("target") == "StandaloneOSX", "Only pinned StandaloneOSX headers are supported")
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)[A-Za-z]\d+", pins.get("unityVersion", ""))
    require(match is not None, "Invalid pinned Unity version")
    expected_version = int(match[1]) * 10000 + int(match[2]) * 100 + int(match[3])
    defines = dict(re.findall(r"^#define\s+(HYBRIDCLR_UNITY_[A-Z0-9_]+)\s+(\d+)\s*$",
                              version_header.read_text(), re.M))
    require(int(defines.get("HYBRIDCLR_UNITY_VERSION", "0")) == expected_version, "Generated Unity header differs from source pins")
    require(defines.get("HYBRIDCLR_UNITY_2022") == "1", "This harness currently verifies the Unity 2022 native ABI")
    compiler_name = shutil.which(args.compiler)
    require(compiler_name is not None, f"Compiler not found: {args.compiler}")
    compiler = required_path(compiler_name)
    compiler_version = run_command([compiler, "--version"], demo, receipt, "compiler-version")
    require("clang" in compiler_version.lower(), "ASan harness requires clang++")
    receipt.update(platform=platform.platform(), architecture=platform.machine(), sourcePins=pins,
                   toolchainEnvironment={name: os.environ.get(name) for name in
                                         ("DEVELOPER_DIR", "SDKROOT", "MACOSX_DEPLOYMENT_TARGET", "CPATH", "CPLUS_INCLUDE_PATH")},
                   compiler={"path": str(compiler), "sha256": sha256(compiler), "version": compiler_version},
                   repositories={"demo": repository_info(demo, entries["demo"]["revision"]),
                                 "hybridclr": repository_info(native, entries["hybridclr"]["revision"]),
                                 "il2cppPlus": repository_info(runtime, entries["il2cppPlus"]["revision"])},
                   installedHeaderProvenance={"root": str(installed), "externalRoot": str(external),
                       "installReceipt": str(install_receipt_path), "installReceiptSha256": sha256(install_receipt_path),
                       "installRepositories": install_receipt.get("repositories"),
                       "unityVersionHeader": str(version_header), "unityVersionHeaderSha256": sha256(version_header),
                       "unityDefines": defines, "fullInstalledRuntimeVerification": False})
    harness = required_path(demo / "Tools/AssemblyShadow/native-tests/m03_staging_identity.cpp")
    sources = [harness] + [required_path(native / "hybridclr/metadata" / name) for name in
                          ("RawImage.cpp", "RawImageBase.cpp", "PDBImage.cpp", "MetadataUtil.cpp")]
    sources += [required_path(runtime / "libil2cpp" / name) for name in
                ("vm-utils/VmStringUtils.cpp", "char-conversions.cpp")]
    fixtures = [required_path(value) for value in args.dll] if args.dll else [
        required_path(demo / "HybridCLRData/HotUpdateDlls/StandaloneOSX" / (name + ".dll"))
        for name in ("AssemblyA.Contracts", "AssemblyA.Implementation.Internal", "AssemblyA.Implementation.Extensibility")]
    require(all(64 <= path.stat().st_size <= 256 * 1024 * 1024 for path in fixtures), "Fixture DLL size is invalid")
    include_directories = [runtime / "libil2cpp", native, external / "baselib/Include",
                           external / "baselib/Platforms/OSX/Include", installed / "utils", external / "google"]
    for directory in include_directories:
        required_path(directory, directory=True)
    flags = ["-std=c++11", "-O1", "-g", "-fsanitize=address", "-fno-omit-frame-pointer",
             "-ffunction-sections", "-fdata-sections", "-DBASELIB_INLINE_NAMESPACE=il2cpp_baselib",
             "-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1"]
    flags += [f"-D{name}={value}" for name, value in sorted(defines.items())]
    for switch, directory in zip(("-I", "-I", "-isystem", "-isystem", "-iquote", "-I"), include_directories):
        flags += [switch, str(directory)]
    receipt["linkBoundary"] = "Real parser/VM folding; only Memory::Free allocator adapter; unused VM paths dead-stripped with dynamic_lookup; no transaction/runtime execution"
    with tempfile.TemporaryDirectory(prefix="assembly-shadow-m03-native-") as temp:
        temporary = Path(temp)
        all_dependencies = {pins_path, install_receipt_path, version_header, compiler, Path(__file__).resolve(), *fixtures}
        for source in sources:
            output = run_command([compiler, *flags, "-M", "-MT", "m03", source], native, receipt, "dependencies")
            all_dependencies.update(dependencies(output, native))
        # Hash the actual transitive dependency set, including SDK/system
        # headers. This covers installed external headers even with -isystem.
        before = {path: sha256(path) for path in sorted(all_dependencies)}
        objects = []
        for index, source in enumerate(sources):
            obj = temporary / f"source-{index}.o"
            run_command([compiler, *flags, "-c", source, "-o", obj], native, receipt, "compile")
            objects.append(obj)
        executable = temporary / "m03-native-tests"
        run_command([compiler, "-fsanitize=address", "-Wl,-dead_strip", "-Wl,-undefined,dynamic_lookup",
                     *objects, "-o", executable], native, receipt, "link")
        output = run_command([executable, *fixtures], native, receipt, "tests")
        summary = re.search(r"^native_identity_checks=(\d+) name_checks=(\d+) PASS$", output, re.M)
        require(summary is not None, "Native test success/count marker is missing")
        require(int(summary[1]) > 6000 and int(summary[2]) >= 30, "Native test coverage is incomplete")
        after = {path: sha256(path) for path in before}
        changed = [str(path) for path in before if before[path] != after[path]]
        require(not changed, "Inputs changed during validation: " + ", ".join(changed))
        receipt.update(identityChecks=int(summary[1]), nameChecks=int(summary[2]),
                       executableSha256=sha256(executable), dependencyCount=len(before),
                       sourceFileHashes=[{"path": str(path), "sha256": digest} for path, digest in before.items()],
                       fixtureFiles=[{"path": str(path), "sha256": before[path]} for path in fixtures],
                       inputsUnchanged=True, temporaryBuildOutputsRemovedOnExit=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--native-root", type=Path, help="HybridCLR native repository root; defaults to hybridclr.localPath pin")
    parser.add_argument("--runtime-root", type=Path, help="il2cpp_plus repository root; defaults to il2cppPlus.localPath pin")
    parser.add_argument("--installed-root", type=Path, help="Pinned installed il2cpp/libil2cpp directory (read-only)")
    parser.add_argument("--pins", type=Path, help="Source-pins JSON; defaults to demo ProjectSettings")
    parser.add_argument("--compiler", default="clang++")
    parser.add_argument("--dll", action="append", type=Path, help="Real DLL fixture; repeat to override three default fixtures")
    parser.add_argument("--output", type=Path, help="Write a new JSON receipt; existing files are never overwritten")
    args = parser.parse_args()
    receipt = {"schemaVersion": 1, "kind": "M03NativeParserRegression", "success": False,
               "startedUtc": dt.datetime.now(dt.timezone.utc).isoformat(), "commands": []}
    try:
        if args.output:
            require(not args.output.exists() and not args.output.is_symlink(), "Output receipt already exists")
            require(args.output.parent.is_dir(), "Output receipt parent directory must exist")
        execute(args, receipt)
        receipt["success"] = True
    except (TestFailure, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        receipt["error"] = str(error)
    receipt["finishedUtc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    encoded = json.dumps(receipt, indent=2) + "\n"
    if args.output and not args.output.exists() and not args.output.is_symlink() and args.output.parent.is_dir():
        try:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(encoded)
            print(json.dumps({key: receipt.get(key) for key in ("success", "identityChecks", "nameChecks", "dependencyCount", "error")}
                             | {"receipt": str(args.output.resolve())}))
        except OSError as error:
            print(encoded, end="")
            print(f"Cannot save receipt: {error}", file=sys.stderr)
            return 1
    else:
        print(encoded, end="")
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
