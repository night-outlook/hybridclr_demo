#!/usr/bin/env python3
"""Run actual-code M04 resolver checks and ON/OFF syntax checks; never install or launch Unity."""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
sys.dont_write_bytecode = True


def execute(args, receipt):
    helper_path = Path(__file__).with_name("run-m03-native-tests.py")
    spec = importlib.util.spec_from_file_location("m03_native_helpers", helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    require, path, run = helper.require, helper.required_path, helper.run_command
    require(sys.platform == "darwin", "Focused harness requires macOS clang/baselib")
    demo = path(args.demo_root, True)
    pins_path = path(demo / "ProjectSettings/AssemblyShadowSourcePins.json")
    pins = json.loads(pins_path.read_text(encoding="utf-8-sig"))
    entries = pins.get("repositories", pins)
    native = path(args.native_root or demo / entries["hybridclr"]["localPath"], True)
    runtime = path(args.runtime_root or demo / entries["il2cppPlus"]["localPath"], True)
    installed = path(args.installed_root or demo / "HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp", True)
    external = path(installed.parent / "external", True)
    header = path(installed / "hybridclr/generated/UnityVersion.h")
    install_path = path(installed / "assembly-shadow-install.json")
    install = json.loads(install_path.read_text(encoding="utf-8-sig"))
    require(install.get("installMode") == "PinnedLocal" and install.get("unityVersion") == pins["unityVersion"],
            "Expected matching pinned-local generated header provenance")
    require(install.get("target") == pins.get("target") == "StandaloneOSX", "Expected StandaloneOSX")
    defines = dict(re.findall(r"^#define\s+(HYBRIDCLR_UNITY_[A-Z0-9_]+)\s+(\d+)\s*$", header.read_text(), re.M))
    version = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)[A-Za-z]\d+", pins["unityVersion"])
    require(version is not None and defines.get("HYBRIDCLR_UNITY_2022") == "1" and
            int(defines["HYBRIDCLR_UNITY_VERSION"]) == int(version[1]) * 10000 + int(version[2]) * 100 + int(version[3]),
            "Generated Unity ABI differs from pinned version")
    compiler = path(shutil.which(args.compiler))
    baselib = path(Path("/Applications/Unity/Hub/Editor") / pins["unityVersion"] /
                   "Unity.app/Contents/PlaybackEngines/MacStandaloneSupport/baselib.a")
    flags = ["-std=c++11", "-O1", "-g", "-fsanitize=address", "-fno-omit-frame-pointer",
             "-ffunction-sections", "-fdata-sections", "-DBASELIB_INLINE_NAMESPACE=il2cpp_baselib",
             "-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1"]
    flags += [f"-D{name}={value}" for name, value in sorted(defines.items())]
    for switch, directory in [("-I", runtime / "libil2cpp"), ("-I", native),
                              ("-isystem", external / "baselib/Include"),
                              ("-isystem", external / "baselib/Platforms/OSX/Include"),
                              ("-iquote", installed / "utils"), ("-I", external / "google")]:
        flags += [switch, str(path(directory, True))]
    runtime_sources = [runtime / "libil2cpp" / name for name in
                       ("vm/Assembly.cpp", "vm/AssemblyShadow.cpp", "vm/MetadataCache.cpp", "vm/GlobalMetadata.cpp",
                        "vm/Reflection.cpp", "icalls/mscorlib/System.Reflection/Assembly.cpp", "icalls/mscorlib/System/AppDomain.cpp")]
    native_sources = [native / "hybridclr/metadata" / name for name in
                      ("Image.cpp", "InterpreterImage.cpp", "AssemblyShadowBridge.cpp", "Assembly.cpp")]
    fixture = path(args.dll or demo / "HybridCLRData/HotUpdateDlls/StandaloneOSX/AssemblyA.Implementation.Internal.dll")
    sources = [demo / "Tools/AssemblyShadow/native-tests/m04_resolution.cpp",
               demo / "Tools/AssemblyShadow/native-tests/m04_reference_identity.cpp", runtime_sources[0], native_sources[0], native_sources[2]]
    sources += [native / "hybridclr/metadata" / name for name in ("RawImage.cpp", "RawImageBase.cpp", "MetadataUtil.cpp")]
    sources += [native / "hybridclr/generated/AssemblyManifest.cpp"]
    sources += [runtime / "libil2cpp" / name for name in
                ("vm/AssemblyShadowDiagnostics.cpp", "vm-utils/VmStringUtils.cpp", "char-conversions.cpp", "utils/sha1.cpp")]
    receipt.update(sourcePins=pins, installedHeaderProvenance={"root": str(installed), "receipt": install,
                   "header": str(header), "fullInstalledRuntimeVerification": False},
                   repositories={"hybridclr": helper.repository_info(native, entries["hybridclr"]["revision"]),
                                 "il2cppPlus": helper.repository_info(runtime, entries["il2cppPlus"]["revision"])},
                   boundary="Actual resolver/core, Assembly enumeration/publication, TLS, physical-AOT closure scan and serializer. Controlled physical metadata-table, exception and class-enumeration adapters; immutable active snapshot fixture. Not full transaction, managed reflection or Player acceptance.")
    run([compiler, "--version"], demo, receipt, "compiler-version")
    with tempfile.TemporaryDirectory(prefix="assembly-shadow-m04-native-") as temp:
        temporary = Path(temp)
        dependencies = {Path(__file__).resolve(), helper_path.resolve(), pins_path, install_path, header, compiler, baselib, fixture}
        for source in sorted(set(sources + runtime_sources + native_sources)):
            output = run([compiler, *flags, "-M", "-MT", "m04", source], native, receipt, "dependencies")
            dependencies.update(helper.dependencies(output, native))
        before = {p: helper.sha256(p) for p in sorted(dependencies)}
        for mode in (1, 0):
            mode_flags = [f.replace("HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1", f"HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW={mode}") for f in flags]
            for source in runtime_sources + native_sources:
                run([compiler, *mode_flags, "-fsyntax-only", source], native, receipt, f"syntax-{mode}")
        objects = []
        for index, source in enumerate(sources):
            obj = temporary / f"source-{index}.o"
            run([compiler, *flags, "-c", source, "-o", obj], native, receipt, "compile")
            objects.append(obj)
        executable = temporary / "m04-resolution"
        run([compiler, "-fsanitize=address", "-Wl,-dead_strip", "-Wl,-undefined,dynamic_lookup",
             *objects, baselib, "-o", executable], native, receipt, "link")
        output = run([executable, fixture], native, receipt, "tests")
        match = re.search(r"^m04_resolution_checks=(\d+) lookup_count=(\d+) lookup_allocations=(\d+) lookup_microseconds=(\d+) PASS$", output, re.M)
        require(match is not None and int(match[1]) >= 45 and int(match[2]) == 1000000 and int(match[3]) == 0, "Resolver coverage/benchmark marker incomplete")
        reference_match = re.search(r"^m04_reference_identity_checks=(\d+) PASS$", output, re.M)
        require(reference_match is not None and int(reference_match[1]) >= 15, "Declared AssemblyRef identity checks missing")
        diagnostic = re.search(r"^m04_guard_diagnostics=(.+)$", output, re.M)
        require(diagnostic is not None, "Runtime guard diagnostics missing")
        snapshot = json.loads(diagnostic[1])
        require(snapshot["lastError"] == 14 and snapshot["state"] == "FailedAfterCommit", "Runtime violation did not remain inspectable")
        require(all(helper.sha256(p) == digest for p, digest in before.items()), "Input changed during checks")
        receipt.update(success=True, checks=int(match[1]), lookupCount=int(match[2]), lookupAllocations=int(match[3]),
                       lookupMicroseconds=int(match[4]), guardDiagnostics=snapshot, syntaxChecks=22,
                       referenceIdentityChecks=int(reference_match[1]), fixture={"path": str(fixture), "sha256": before[fixture]},
                       executableSha256=helper.sha256(executable), inputsUnchanged=True,
                       sourceFileHashes=[{"path": str(p), "sha256": digest} for p, digest in before.items()])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--native-root", type=Path)
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--installed-root", type=Path)
    parser.add_argument("--compiler", default="clang++")
    parser.add_argument("--dll", type=Path, help="Read-only fixture containing netstandard AssemblyRef")
    parser.add_argument("--output", type=Path, help="New receipt path; existing files are never overwritten")
    args = parser.parse_args()
    receipt = {"schemaVersion": 1, "kind": "M04NativeResolutionRegression", "success": False,
               "startedUtc": dt.datetime.now(dt.timezone.utc).isoformat(), "commands": []}
    try:
        if args.output and (args.output.exists() or args.output.is_symlink()):
            raise RuntimeError("Receipt path already exists")
        execute(args, receipt)
    except Exception as error:
        receipt["error"] = str(error)
    receipt["finishedUtc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    encoded = json.dumps(receipt, indent=2) + "\n"
    if args.output and not args.output.exists() and not args.output.is_symlink():
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(encoded)
        print(json.dumps({k: receipt.get(k) for k in ("success", "checks", "syntaxChecks", "lookupCount", "lookupAllocations", "error")} | {"receipt": str(args.output)}))
    else:
        print(encoded, end="")
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
