#!/usr/bin/env python3
"""Actual-core M05 ASan tests plus ON/OFF production syntax; no install or Unity launch."""
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
             "-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1", "-DIL2CPP_DEBUG=1"]
    flags += [f"-D{name}={value}" for name, value in sorted(defines.items())]
    for switch, directory in [("-I", runtime / "libil2cpp"), ("-I", native),
                              ("-isystem", external / "baselib/Include"),
                              ("-isystem", external / "baselib/Platforms/OSX/Include"),
                              ("-iquote", installed / "utils"), ("-I", external / "google"),
                              ("-I", external / "bdwgc/include"), ("-I", external / "bdwgc/libatomic_ops/src"),
                              ("-I", external / "xxHash")]:
        flags += [switch, str(path(directory, True))]
    production = [runtime / "libil2cpp" / name for name in
                  ("il2cpp-api.cpp", "vm/AssemblyShadow.cpp", "vm/AssemblyShadowTypeKey.cpp", "vm/AssemblyShadowTypeResolver.cpp",
                   "vm/AssemblyShadowDiagnostics.cpp", "vm/Class.cpp", "vm/Image.cpp", "vm/Object.cpp",
                   "vm/Array.cpp", "vm/Runtime.cpp", "vm/Reflection.cpp", "vm/Type.cpp", "vm/Field.cpp",
                   "icalls/mscorlib/System.Reflection/RuntimeAssembly.cpp", "icalls/mscorlib/System/Object.cpp",
                   "icalls/mscorlib/System/RuntimeType.cpp")]
    production += [native / "hybridclr/AssemblyShadowRuntimeApi.cpp"]
    core = [demo / "Tools/AssemblyShadow/native-tests/m05_types.cpp"]
    core += [runtime / "libil2cpp" / name for name in
             ("vm/AssemblyShadowTypeKey.cpp", "vm/AssemblyShadowTypeResolver.cpp", "vm/AssemblyShadowDiagnostics.cpp",
              "vm-utils/VmStringUtils.cpp", "utils/StringUtils.cpp", "char-conversions.cpp")]
    core += [native / "hybridclr/metadata/AssemblyShadowBridge.cpp"]
    core += [native / "hybridclr/metadata/Image.cpp"]
    core += [native / "hybridclr/generated/AssemblyManifest.cpp"]
    reflection = [demo / "Tools/AssemblyShadow/native-tests/m05_reflection.cpp"]
    reflection += [runtime / "libil2cpp" / name for name in
                   ("icalls/mscorlib/System.Reflection/RuntimeAssembly.cpp", "icalls/mscorlib/System/Object.cpp",
                    "vm/Type.cpp", "os/FastReaderReaderWriterLock.cpp", "gc/WriteBarrier.cpp",
                    "metadata/Il2CppTypeHash.cpp", "metadata/Il2CppTypeCompare.cpp")]
    reflection += [native / "hybridclr/AssemblyShadowRuntimeApi.cpp"]
    image_identity = [demo / "Tools/AssemblyShadow/native-tests/m05_image_identity.cpp",
                      runtime / "libil2cpp/il2cpp-api.cpp"]
    receipt.update(sourcePins=pins, installedHeaderProvenance={"root": str(installed), "receipt": install,
                   "header": str(header), "fullInstalledRuntimeVerification": False},
                   repositories={"hybridclr": helper.repository_info(native, entries["hybridclr"]["revision"]),
                                 "il2cppPlus": helper.repository_info(runtime, entries["il2cppPlus"]["revision"])},
                   coreBoundary="Actual TypeKey/resolver/guard/transaction diagnostic/TLS code. Controlled physical metadata and upstream generic/array/pointer interner adapters, managed exception adapter, immutable active snapshot. No class initialization, object reinterpretation, Player or full transaction acceptance.",
                   reflectionBoundary="Actual Reflection.cpp cache/member code included once; actual RuntimeAssembly/System.Object/Type/runtime API adapter linked. Controlled core/GC/object/string and unrelated resource-lock adapters. Not full VM acceptance.",
                   imageIdentityBoundary="Actual exported C API and published-snapshot image mapping. Controlled physical VM getters and class rows; snapshot fixture, not transaction/Unity registry/Player acceptance.")
    run([compiler, "--version"], demo, receipt, "compiler-version")
    with tempfile.TemporaryDirectory(prefix="assembly-shadow-m05-native-") as temp:
        temporary = Path(temp)
        dependencies = {Path(__file__).resolve(), helper_path.resolve(), pins_path, install_path, header, compiler, baselib}
        for mode in (1, 0):
            mode_flags = [f.replace("HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1", f"HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW={mode}") for f in flags]
            for source in sorted(set(core + reflection + image_identity + production)):
                output = run([compiler, *mode_flags, "-M", "-MT", "m05", source], native, receipt, "dependencies")
                dependencies.update(helper.dependencies(output, native))
        before = {p: helper.sha256(p) for p in sorted(dependencies)}
        for mode in (1, 0):
            mode_flags = [f.replace("HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1", f"HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW={mode}") for f in flags]
            for source in production:
                run([compiler, *mode_flags, "-fsyntax-only", source], native, receipt, f"syntax-{mode}")
        summaries = []
        for mode, debug in ((1, 1), (1, 0), (0, 0)):
            mode_flags = [f.replace("HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1", f"HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW={mode}")
                          .replace("IL2CPP_DEBUG=1", f"IL2CPP_DEBUG={debug}") for f in flags]
            objects = []
            for index, source in enumerate(core):
                obj = temporary / f"core-{mode}-{debug}-{index}.o"
                run([compiler, *mode_flags, "-c", source, "-o", obj], native, receipt, "compile")
                objects.append(obj)
            executable = temporary / f"m05-core-{mode}-{debug}"
            run([compiler, "-fsanitize=address", "-Wl,-dead_strip", "-Wl,-undefined,dynamic_lookup",
                 *objects, baselib, "-o", executable], native, receipt, "link")
            for scenario in (("layout", "metadata", "staging", "reference") if mode else ("disabled",)):
                output = run([executable, scenario], native, receipt, "tests")
                if not mode:
                    require("m05_disabled_checks=2 PASS" in output, "OFF API checks missing")
                    continue
                match = re.search(r"^m05_type_checks=(\d+) mode=(\w+) metadata_reads=(\d+) inflation_calls=(\d+) PASS$", output, re.M)
                require(match is not None and int(match[1]) >= 60, "Type resolver coverage incomplete")
                guard = json.loads(re.search(r"^m05_guard_diagnostics=(.+)$", output, re.M)[1])
                require(guard["lastError"] == (14 if scenario == "reference" else 16 if scenario == "layout" else 15) and guard["state"] == "FailedAfterCommit", "Guard failure did not remain sealed/inspectable")
                infos = [json.loads(m) for m in re.findall(r"^m05_(?:active_)?type_info=(.+)$", output, re.M)]
                for info in infos:
                    require(len(info) == 18 and info["schemaVersion"] == 1, "Type-info schema differs from declaration")
                    require(info["pointerDetailsAvailable"] == bool(debug), "Address gating differs from IL2CPP_DEBUG")
                    for field in ("inputTypePointer", "activeTypePointer", "baselineTypePointer"):
                        available = bool(debug) and (field != "baselineTypePointer" or info["baselinePointerAvailable"])
                        require(bool(re.fullmatch(r"0x[0-9a-f]{1,16}", info[field])) and int(info[field], 16) != 0 if available else info[field] == "", "Invalid diagnostic pointer/availability contract")
                    require(bool(debug) or not info["baselinePointerAvailable"], "Release baseline address leaked")
                summaries.append({"mode": scenario, "debug": bool(debug), "checks": int(match[1]), "guard": guard, "typeInfo": infos,
                                  "executableSha256": helper.sha256(executable)})
        reflection_summaries = []
        for mode in (1, 0):
            mode_flags = [f.replace("HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1", f"HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW={mode}") for f in flags]
            objects = []
            for index, source in enumerate(reflection):
                obj = temporary / f"reflection-{mode}-{index}.o"
                run([compiler, *mode_flags, "-c", source, "-o", obj], native, receipt, "compile-reflection")
                objects.append(obj)
            executable = temporary / f"m05-reflection-{mode}"
            run([compiler, "-fsanitize=address", "-Wl,-dead_strip", "-Wl,-undefined,dynamic_lookup",
                 *objects, baselib, "-o", executable], native, receipt, "link-reflection")
            output = run([executable], native, receipt, "tests")
            match = re.search(r"^m05_reflection_checks=(\d+) feature=(\d) PASS$", output, re.M)
            require(match is not None and int(match[2]) == mode and int(match[1]) >= (31 if mode else 3), "Reflection coverage incomplete")
            reflection_summaries.append({"feature": mode, "checks": int(match[1]), "executableSha256": helper.sha256(executable)})
        image_identity_summaries = []
        for mode in (1, 0):
            mode_flags = [f.replace("HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1", f"HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW={mode}") for f in flags]
            objects = []
            for index, source in enumerate(image_identity):
                obj = temporary / f"image-identity-{mode}-{index}.o"
                run([compiler, *mode_flags, "-c", source, "-o", obj], native, receipt, "compile-image-identity")
                objects.append(obj)
            executable = temporary / f"m05-image-identity-{mode}"
            run([compiler, "-fsanitize=address", "-Wl,-dead_strip", "-Wl,-undefined,dynamic_lookup",
                 *objects, baselib, "-o", executable], native, receipt, "link-image-identity")
            output = run([executable], native, receipt, "tests")
            match = re.search(r"^m05_image_identity_checks=(\d+) feature=(\d) PASS$", output, re.M)
            require(match is not None and int(match[2]) == mode and int(match[1]) >= (150 if mode else 30),
                    "Public image identity coverage incomplete")
            image_identity_summaries.append({"feature": mode, "checks": int(match[1]),
                                             "executableSha256": helper.sha256(executable)})
        require(all(helper.sha256(p) == digest for p, digest in before.items()), "Input changed during checks")
        receipt.update(success=True, coreTests=summaries, reflectionTests=reflection_summaries,
                       imageIdentityTests=image_identity_summaries,
                       syntaxChecks=2 * len(production), inputsUnchanged=True,
                       sourceFileHashes=[{"path": str(p), "sha256": digest} for p, digest in before.items()])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--native-root", type=Path)
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--installed-root", type=Path)
    parser.add_argument("--compiler", default="clang++")
    parser.add_argument("--output", type=Path, help="New receipt path; existing files are never overwritten")
    args = parser.parse_args()
    receipt = {"schemaVersion": 1, "kind": "M05NativeTypeRegression", "success": False,
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
        print(json.dumps({k: receipt.get(k) for k in ("success", "syntaxChecks", "error")} | {"receipt": str(args.output)}))
    else:
        print(encoded, end="")
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
