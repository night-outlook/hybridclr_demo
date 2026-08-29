#!/usr/bin/env python3
"""Focused M06 actual-core ASan matrix and ON/OFF syntax; no install or Unity launch."""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
HELPER = Path(__file__).with_name("run-m03-native-tests.py")
SPEC = importlib.util.spec_from_file_location("m03_native_helpers", HELPER)
helpers = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helpers)
require, path, run = helpers.require, helpers.required_path, helpers.run_command

SCENARIOS = ("baseline", "inflated", "prior", "reference", "null", "overflow", "concurrent",
             "args-class", "args-method", "args-composite", "args-declaring", "args-null",
             "args-empty", "args-null-vector", "args-open", "args-recursive", "args-array", "args-generic")
COUNTERS = {"methodChecks", "shadowMethodChecks", "rejectedBaselineMethods", "baselineClassCctorStarted",
            "shadowClassCctorStarted", "interpreterTransformations", "shadowInterpreterTransformations",
            "droppedClassObservations"}
ROOT_FIELDS = COUNTERS | {"schemaVersion", "enabled", "stateCode", "state", "generation", "classes"}
CLASS_FIELDS = {"logicalAssembly", "typeKey", "executionModeCode", "executionMode", "physicalImageKind",
                "isActive", "cctorStarted", "cctorFinished", "hasInitializationException", "staticStoragePointer",
                "pointerDetailsAvailable", "staticStorageAvailable"}
STATES = ("Disabled", "CandidatesRegistered", "Staging", "Staged", "Validated", "Committing", "Committed",
          "Aborted", "Failed", "FailedAfterCommit")


def validate_execution(value, debug):
    require(set(value) == ROOT_FIELDS and value["schemaVersion"] == 1 and value["enabled"] is True,
            "Execution root differs from declared schema 1")
    require(type(value["stateCode"]) is int and 0 <= value["stateCode"] < len(STATES) and
            value["state"] == STATES[value["stateCode"]], "Invalid execution state pair")
    for field in COUNTERS | {"generation"}:
        require(type(value[field]) is int and 0 <= value[field] <= (1 << 64) - 1, "Invalid uint64: " + field)
    require(value["shadowMethodChecks"] <= value["methodChecks"] and
            value["rejectedBaselineMethods"] <= value["methodChecks"] and
            value["shadowInterpreterTransformations"] <= value["interpreterTransformations"],
            "Execution subset exceeds total")
    require(type(value["classes"]) is list and 0 < len(value["classes"]) <= 1024,
            "Class observation bound violated")
    for row in value["classes"]:
        require(set(row) == CLASS_FIELDS, "Execution class schema changed")
        for field in ("logicalAssembly", "typeKey", "executionMode", "physicalImageKind", "staticStoragePointer"):
            require(type(row[field]) is str, "Invalid string: " + field)
        for field in ("isActive", "cctorStarted", "cctorFinished", "hasInitializationException",
                      "pointerDetailsAvailable", "staticStorageAvailable"):
            require(type(row[field]) is bool, "Invalid boolean: " + field)
        require(type(row["executionModeCode"]) is int and
                (row["executionModeCode"], row["executionMode"]) in ((0, "AotBaseline"), (1, "InterpreterShadow")),
                "Invalid execution mode pair")
        require(row["logicalAssembly"] and row["typeKey"] and row["physicalImageKind"] in ("Aot", "Interpreter"),
                "Incomplete physical class identity")
        require(row["pointerDetailsAvailable"] is bool(debug), "IL2CPP_DEBUG address gating changed")
        pointer = row["staticStoragePointer"]
        available = bool(debug) and row["staticStorageAvailable"]
        require(bool(re.fullmatch(r"0x[0-9a-f]{1,16}", pointer)) and int(pointer, 16) != 0 if available else pointer == "",
                "Invalid storage pointer/availability")


def execute(args, receipt):
    require(sys.platform == "darwin", "This focused harness requires macOS clang/baselib")
    demo = path(args.demo_root, True)
    pins_path = path(demo / "ProjectSettings/AssemblyShadowSourcePins.json")
    pins = json.loads(pins_path.read_text(encoding="utf-8-sig"))
    entries = pins.get("repositories", pins)
    require(pins.get("schemaVersion") == 1 and pins.get("target") == "StandaloneOSX" and
            pins.get("architecture") == "arm64", "Expected pinned StandaloneOSX arm64 source configuration")
    native = path(args.native_root or demo / entries["hybridclr"]["localPath"], True)
    runtime = path(args.runtime_root or demo / entries["il2cppPlus"]["localPath"], True)
    require(len({demo, native, runtime}) == 3, "Demo/native/runtime roots must be distinct")
    installed = path(args.installed_root or demo / "HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp", True)
    external = path(installed.parent / "external", True)
    header = path(installed / "hybridclr/generated/UnityVersion.h")
    install_path = path(installed / "assembly-shadow-install.json")
    install = json.loads(install_path.read_text(encoding="utf-8-sig"))
    require(install.get("installMode") == "PinnedLocal" and install.get("unityVersion") == pins["unityVersion"] and
            install.get("target") == pins["target"], "Generated headers need matching pinned-local Unity/target provenance")
    defines = dict(re.findall(r"^#define\s+(HYBRIDCLR_UNITY_[A-Z0-9_]+)\s+(\d+)\s*$", header.read_text(), re.M))
    version = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)[A-Za-z]\d+", pins["unityVersion"])
    require(version is not None and defines.get("HYBRIDCLR_UNITY_2022") == "1" and
            int(defines["HYBRIDCLR_UNITY_VERSION"]) == int(version[1]) * 10000 + int(version[2]) * 100 + int(version[3]),
            "Generated Unity ABI differs from pins")
    compiler_name = shutil.which(args.compiler)
    require(compiler_name is not None, "Compiler not found: " + args.compiler)
    compiler = path(compiler_name)
    nm = path(shutil.which("nm"))
    baselib = path(Path("/Applications/Unity/Hub/Editor") / pins["unityVersion"] /
                   "Unity.app/Contents/PlaybackEngines/MacStandaloneSupport/baselib.a")
    flags = ["-std=c++11", "-O1", "-g", "-fsanitize=address", "-fno-omit-frame-pointer",
             "-ffunction-sections", "-fdata-sections", "-DBASELIB_INLINE_NAMESPACE=il2cpp_baselib"]
    flags += [f"-D{name}={value}" for name, value in sorted(defines.items())]
    # Current paired source roots always precede generated external headers.
    for switch, directory in (("-I", runtime / "libil2cpp"), ("-I", native),
                              ("-isystem", external / "baselib/Include"),
                              ("-isystem", external / "baselib/Platforms/OSX/Include"),
                              ("-iquote", installed / "utils"), ("-I", external / "google"),
                              ("-I", external / "bdwgc/include"), ("-I", external / "bdwgc/libatomic_ops/src"),
                              ("-I", external / "xxHash")):
        flags += [switch, str(path(directory, True))]
    fixture = path(demo / "Tools/AssemblyShadow/native-tests/m06_execution.cpp")
    core = [fixture] + [runtime / "libil2cpp" / name for name in
                      ("vm/AssemblyShadowTypeKey.cpp", "vm/AssemblyShadowTypeResolver.cpp", "vm/AssemblyShadowDiagnostics.cpp",
                       "vm-utils/VmStringUtils.cpp", "utils/StringUtils.cpp", "char-conversions.cpp")]
    core += [native / "hybridclr/metadata" / name for name in ("AssemblyShadowBridge.cpp", "Image.cpp")]
    syntax = [runtime / "libil2cpp" / name for name in
              ("vm/AssemblyShadow.cpp", "vm/AssemblyShadowTypeKey.cpp", "vm/AssemblyShadowDiagnostics.cpp",
               "vm/Runtime.cpp", "codegen/il2cpp-codegen.h")]
    syntax += [native / "hybridclr" / name for name in
               ("AssemblyShadowRuntimeApi.cpp", "interpreter/InterpreterModule.cpp", "interpreter/Interpreter_Execute.cpp")]
    syntax.append(fixture)
    compiler_version = run([compiler, "--version"], demo, receipt, "compiler-version")
    require("clang" in compiler_version.lower(), "ASan harness requires clang++")
    receipt.update(platform=platform.platform(), architecture=platform.machine(), sourcePins=pins,
                   compiler={"path": str(compiler), "sha256": helpers.sha256(compiler), "version": compiler_version},
                   toolchainEnvironment={key: os.environ.get(key) for key in
                       ("DEVELOPER_DIR", "SDKROOT", "MACOSX_DEPLOYMENT_TARGET", "CPATH", "CPLUS_INCLUDE_PATH")},
                   baselib={"path": str(baselib), "sha256": helpers.sha256(baselib)},
                   repositories={key: helpers.repository_info(root, entries[key]["revision"]) for key, root in
                       (("demo", demo), ("hybridclr", native), ("il2cppPlus", runtime))},
                   installedHeaderProvenance={"root": str(installed), "receipt": install, "header": str(header),
                                             "fullInstalledRuntimeVerification": False},
                   boundary="Actual AssemblyShadow core, TypeKey/resolver/serializer and TLS. M05 physical/interner/exception adapters; M06 raw TypeDef adapters and immutable publication fixture. No managed execution, class materialization or object reinterpretation. Cctor/transform hooks are manually driven; actual Runtime/interpreter/codegen are syntax-checked, not executed.",
                   playerAcceptance=False)
    with tempfile.TemporaryDirectory(prefix="assembly-shadow-m06-native-") as temporary_name:
        temporary = Path(temporary_name)
        dependencies = {Path(__file__).resolve(), HELPER.resolve(), pins_path, install_path, header, compiler, nm, baselib}
        for feature, debug in ((1, 1), (1, 0), (0, 0)):
            mode_flags = flags + [f"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW={feature}", f"-DIL2CPP_DEBUG={debug}"]
            for source in sorted(set(core + syntax)):
                output = run([compiler, *mode_flags, "-x", "c++", "-M", "-MT", "m06", source], native, receipt, "dependencies")
                dependencies.update(helpers.dependencies(output, native))
        require(not any(p.is_relative_to(installed) and p not in (header, install_path) for p in dependencies),
                "Installed production source/header shadowed current paired sources")
        before = {p: helpers.sha256(p) for p in sorted(dependencies)}
        receipt["sourceFileHashes"] = [{"path": str(p), "sha256": digest} for p, digest in before.items()]
        for feature in (1, 0):
            mode_flags = flags + [f"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW={feature}", "-DIL2CPP_DEBUG=1"]
            for source in syntax:
                run([compiler, *mode_flags, "-x", "c++", "-fsyntax-only", source], native, receipt, f"syntax-{feature}")
        summaries, total_checks = [], 0
        for feature, debug in ((1, 1), (1, 0), (0, 0)):
            mode_flags = flags + [f"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW={feature}", f"-DIL2CPP_DEBUG={debug}"]
            objects = []
            for index, source in enumerate(core):
                obj = temporary / f"core-{feature}-{debug}-{index}.o"
                run([compiler, *mode_flags, "-c", source, "-o", obj], native, receipt, "compile")
                objects.append(obj)
            executable = temporary / f"m06-core-{feature}-{debug}"
            run([compiler, "-fsanitize=address", "-Wl,-dead_strip", "-Wl,-undefined,dynamic_lookup",
                 *objects, baselib, "-o", executable], native, receipt, "link")
            undefined = run([nm, "-u", executable], native, receipt, "undefined-symbols")
            require(not any(name in undefined for name in
                    ("AssertMethodIsActive", "RequireActiveMethod", "GetExecutionDiagnosticsJson", "ObserveClassCctorStarted",
                     "ObserveInterpreterTransformation", "GetAssemblyTypeHandle", "GetTypeNamespaceAndName",
                     "GetGenericContainerFromIndex", "GetGenericContainerCount", "GetIl2CppTypeFromIndex")),
                    "M06 core/metadata adapter symbol remains undefined")
            for scenario in SCENARIOS if feature else ("disabled",):
                output = run([executable, scenario], native, receipt, "tests")
                summary = {"feature": feature, "debug": bool(debug), "scenario": scenario,
                           "executableSha256": helpers.sha256(executable)}
                if not feature:
                    require("m06_execution_disabled_checks=2 PASS" in output, "OFF checks missing")
                    checks = 2
                else:
                    match = re.search(r"^m06_execution_checks=(\d+) mode=([\w-]+) metadata_reads=(\d+) PASS$", output, re.M)
                    checks = 18 if scenario.startswith("args-") else 32 if scenario == "overflow" else 31 if scenario == "concurrent" else 30
                    require(match is not None and int(match[1]) == checks and match[2] == scenario and int(match[3]) == 0,
                            "Incomplete coverage or materializing metadata query")
                    if scenario.startswith("args-"):
                        require("m06_argument_failure=" in output and "TypePath=" in output,
                                "Captured argument diagnostic missing")
                    else:
                        execution = json.loads(re.search(r"^m06_execution_json=(.+)$", output, re.M)[1])
                        validate_execution(execution, debug)
                        require(execution["droppedClassObservations"] == 0, "Normal acceptance dropped observations")
                        guard = json.loads(re.search(r"^m06_guard_json=(.+)$", output, re.M)[1])
                        expected = 14 if scenario == "reference" else 16 if scenario == "prior" else 3 if scenario == "null" else 21
                        require(guard["lastError"] == expected and guard["state"] == "FailedAfterCommit",
                                "First guard failure did not remain sealed/inspectable")
                        summary.update(execution=execution, guard=guard)
                summary["checks"] = checks
                summaries.append(summary)
                total_checks += checks
        require(total_checks == 824 and len(summaries) == 37, "M06 matrix differs from declared focused coverage")
        require(all(helpers.sha256(p) == digest for p, digest in before.items()), "Input changed during validation")
        receipt.update(success=True, tests=summaries, checks=total_checks, syntaxChecks=2 * len(syntax),
                       dependencyCount=len(before), inputsUnchanged=True, sourceFirstIncludesVerified=True,
                       temporaryBuildOutputsRemovedOnExit=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--native-root", type=Path, help="Current HybridCLR source repository")
    parser.add_argument("--runtime-root", type=Path, help="Current il2cpp_plus source repository")
    parser.add_argument("--installed-root", type=Path, help="Read-only pinned Unity header provenance")
    parser.add_argument("--compiler", default="clang++")
    parser.add_argument("--output", type=Path, help="New immutable JSON receipt; existing files are refused")
    args = parser.parse_args()
    receipt = {"schemaVersion": 1, "kind": "M06NativeExecutionRegression", "success": False,
               "startedUtc": dt.datetime.now(dt.timezone.utc).isoformat(), "commands": []}
    try:
        if args.output:
            require(not args.output.exists() and not args.output.is_symlink(), "Output receipt already exists")
            require(args.output.parent.is_dir(), "Output receipt parent must exist")
        execute(args, receipt)
    except Exception as error:
        receipt["error"] = str(error)
    receipt["finishedUtc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    encoded = json.dumps(receipt, indent=2) + "\n"
    if args.output and not args.output.exists() and not args.output.is_symlink() and args.output.parent.is_dir():
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(encoded)
        print(json.dumps({key: receipt.get(key) for key in ("success", "checks", "syntaxChecks", "dependencyCount", "error")}
                         | {"receipt": str(args.output.resolve())}))
    else:
        print(encoded, end="")
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
