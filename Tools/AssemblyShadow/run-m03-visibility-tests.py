#!/usr/bin/env python3
"""ASan proof of actual private-visibility predicates, not IL2CPP Player acceptance."""
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
import subprocess
import sys
import tempfile

# Reuse read-only provenance helpers without creating Python cache files or
# changing the independent parser harness.
sys.dont_write_bytecode = True
HELPER = Path(__file__).with_name("run-m03-native-tests.py")
SPEC = importlib.util.spec_from_file_location("m03_native_helpers", HELPER)
helpers = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helpers)
require, required_path = helpers.require, helpers.required_path
run_command, sha256 = helpers.run_command, helpers.sha256


def function_body(source, signature):
    match = re.search(signature + r"\s*\{", source)
    require(match is not None, "Missing cached-enumeration function: " + signature)
    begin = match.end()
    depth = 1
    for end in range(begin, len(source)):
        depth += (source[end] == "{") - (source[end] == "}")
        if depth == 0:
            return source[begin:end]
    raise helpers.TestFailure("Unterminated cached-enumeration function")


def check_cached_enumeration_policy(compiler, flags, runtime, receipt, files):
    # This is a preprocessed source-policy check, not execution of VM cache reads.
    # In particular, ignore OFF-only materializing code when checking the ON API.
    preprocessed = []
    for source in files:
        output = run_command([compiler, *flags, "-E", "-P", source], runtime, receipt, "dependencies")
        receipt["commands"][-1]["phase"] = "preprocess-cached-enumeration-policy"
        preprocessed.append(output)
    report = function_body(preprocessed[0], r"void ReportIL2CppClasses\(ClassReportFunc callback, void\* context\)")
    cached = function_body(preprocessed[1], r"Il2CppClass\* il2cpp::vm::GlobalMetadata::GetInitializedTypeInfoFromAssembly\(const Il2CppImage\* image, AssemblyTypeIndex index\)")
    slot = function_body(preprocessed[1], r"Il2CppClass\* GetCachedTypeInfoFromTypeDefinitionRawIndex\(uint32_t index\) const")
    require("GlobalMetadata::GetInitializedTypeInfoFromAssembly(&image, i)" in report and "if (type)" in report,
            "Public class enumeration no longer uses the initialized cache-only accessor")
    for body in (report, cached, slot):
        require(not any(call in body for call in ("GetTypeInfoFromHandle(", "GetAssemblyTypeHandle(",
                    "GetIndexForTypeDefinitionInternal(", "MetadataModule::", "FromTypeDefinition(",
                    "Class::FromIl2CppType(", "Class::Init(", "Type::GetName(", "InitOnce(")),
                "Public cached-enumeration path contains a materializing or private-TLS lookup")
    require(all(token in cached for token in ("FastAutoLock", "g_MetadataLock", "s_TypeInfoDefinitionTable[typeIndex]",
                "InterpreterImage::GetImage(", "GetCachedTypeInfoFromTypeDefinitionRawIndex(",
                "klass && klass->initialized ? klass : nullptr")), "Cache lookup no longer reads initialized physical slots under the metadata lock")
    require("".join(slot.split()) == "returnindex<_classList.size()?_classList[index]:nullptr;",
            "Interpreter cached-slot accessor acquired side effects")
    require(all(call in report for call in ("WalkArrays(callback, context)", "WalkSZArrays(callback, context)",
                "WalkAllGenericClasses(callback, context)", "WalkPointerTypes(callback, context)")),
            "Public enumeration dropped an existing compound-cache walker")
    receipt["cachedEnumerationSourcePolicyChecks"] = 5


def execute(args, receipt):
    require(sys.platform == "darwin", "This ASan/linker harness supports macOS only")
    demo = required_path(args.demo_root, directory=True)
    pins_path = required_path(demo / "ProjectSettings/AssemblyShadowSourcePins.json")
    pins = json.loads(pins_path.read_text(encoding="utf-8-sig"))
    require(pins.get("schemaVersion") == 1 and pins.get("target") == "StandaloneOSX", "Unsupported source pins")
    entries = pins.get("repositories", pins)
    native = required_path(args.native_root or demo / entries["hybridclr"]["localPath"], directory=True)
    runtime = required_path(args.runtime_root or demo / entries["il2cppPlus"]["localPath"], directory=True)
    require(len({demo, native, runtime}) == 3, "Demo/native/runtime roots must be distinct")
    require(pins.get("architecture") == "arm64", "This harness requires pinned arm64 headers")
    generated = required_path(args.generated_root or demo / "HybridCLRData/StrippedAOTDllsTempProj/StandaloneOSX/Il2CppOutputProject/IL2CPP", directory=True)
    version = required_path(generated / "libil2cpp/hybridclr/generated/UnityVersion.h")
    installation = required_path(generated / "libil2cpp/assembly-shadow-install.json")
    installed = json.loads(installation.read_text(encoding="utf-8-sig"))
    require(installed.get("installMode") == "PinnedLocal" and installed.get("unityVersion") == pins.get("unityVersion"),
            "Generated headers need a matching PinnedLocal installation receipt")
    require(installed.get("target") == pins["target"], "Generated target differs from source pins")
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)[A-Za-z]\d+", pins.get("unityVersion", ""))
    require(match is not None, "Invalid pinned Unity version")
    defines = dict(re.findall(r"^#define\s+(HYBRIDCLR_UNITY_[A-Z0-9_]+)\s+(\d+)\s*$", version.read_text(), re.M))
    require(int(defines.get("HYBRIDCLR_UNITY_VERSION", "0")) == int(match[1]) * 10000 + int(match[2]) * 100 + int(match[3]),
            "Generated Unity version differs from pins")
    require(defines.get("HYBRIDCLR_UNITY_2022") == "1", "Harness requires the Unity 2022 native ABI")
    compiler_name = shutil.which(args.compiler)
    require(compiler_name is not None, "Compiler not found: " + args.compiler)
    compiler = required_path(compiler_name)
    compiler_version = run_command([compiler, "--version"], demo, receipt, "compiler-version")
    require("clang" in compiler_version.lower(), "ASan harness requires clang++")
    external = generated / "external"
    flags = ["-std=gnu++14", "-arch", "arm64", "-O1", "-g", "-fsanitize=address", "-fno-omit-frame-pointer",
             "-ffunction-sections", "-fdata-sections", "-DDEBUG=1", "-DBASELIB_INLINE_NAMESPACE=il2cpp_baselib",
             "-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1", "-include", str(version)]
    for switch, directory in [("-I", runtime / "libil2cpp"), ("-I", native),
                              ("-iquote", generated / "libil2cpp/utils"), ("-I", external / "google"),
                              ("-isystem", external / "baselib/Include"),
                              ("-isystem", external / "baselib/Platforms/OSX/Include"),
                              ("-I", external / "bdwgc/include")]:
        flags += [switch, str(required_path(directory, directory=True))]
    sources = [required_path(demo / "Tools/AssemblyShadow/native-tests/m03_private_visibility.cpp"),
               required_path(runtime / "libil2cpp/vm/AssemblyShadowVisibility.cpp"),
               required_path(native / "hybridclr/metadata/MetadataUtil.cpp")]
    policy_files = [required_path(runtime / "libil2cpp/vm" / name) for name in
                    ("MemoryInformation.cpp", "GlobalMetadata.cpp")]
    receipt.update(platform=platform.platform(), architecture="arm64", sourcePins=pins,
                   compiler={"path": str(compiler), "sha256": sha256(compiler), "version": compiler_version},
                   toolchainEnvironment={key: os.environ.get(key) for key in
                       ("DEVELOPER_DIR", "SDKROOT", "MACOSX_DEPLOYMENT_TARGET", "CPATH", "CPLUS_INCLUDE_PATH")},
                   repositories={key: helpers.repository_info(root, entries[key]["revision"]) for key, root in
                       (("demo", demo), ("hybridclr", native), ("il2cppPlus", runtime))},
                   generatedHeaderProvenance={"root": str(generated), "installation": str(installation),
                       "installationSha256": sha256(installation), "versionHeader": str(version),
                       "versionHeaderSha256": sha256(version), "fullInstalledRuntimeVerification": False},
                   linkBoundary="Real visibility predicates and metadata index decoder; synthetic native metadata; only ActiveGeneration/IsActiveShadow substituted; unused VM paths dead-stripped with dynamic_lookup",
                   playerAcceptance=False)
    with tempfile.TemporaryDirectory(prefix="assembly-shadow-m03-visibility-") as temporary_name:
        temporary = Path(temporary_name)
        dependencies = {pins_path, version, installation, compiler, Path(__file__).resolve(), HELPER.resolve()}
        for source in sources + policy_files:
            output = run_command([compiler, *flags, "-M", "-MT", "m03", source], runtime, receipt, "dependencies")
            dependencies.update(helpers.dependencies(output, runtime))
        before = {path: sha256(path) for path in sorted(dependencies)}
        check_cached_enumeration_policy(compiler, flags, runtime, receipt, policy_files)
        objects = []
        for index, source in enumerate(sources):
            obj = temporary / f"source-{index}.o"
            run_command([compiler, *flags, "-c", source, "-o", obj], runtime, receipt, "compile")
            objects.append(obj)
        executable = temporary / "m03-visibility-tests"
        run_command([compiler, "-arch", "arm64", "-fsanitize=address", "-Wl,-dead_strip", "-Wl,-undefined,dynamic_lookup",
                     *objects, "-o", executable], runtime, receipt, "link")
        scenarios = {}
        for mode in ("abort", "commit"):
            output = run_command([executable, mode], runtime, receipt, "tests")
            marker = re.search(r"^visibility_checks=(\d+) mode=" + mode + r" PASS$", output, re.M)
            require(marker is not None and int(marker[1]) > 1000, "Missing or incomplete visibility checks: " + mode)
            scenarios[mode] = int(marker[1])
        require(all(sha256(path) == digest for path, digest in before.items()), "Inputs changed during validation")
        receipt.update(scenarios=scenarios, visibilityChecks=sum(scenarios.values()), inputsUnchanged=True,
                       executableSha256=sha256(executable), dependencyCount=len(before),
                       sourceFileHashes=[{"path": str(path), "sha256": digest} for path, digest in before.items()],
                       temporaryBuildOutputsRemovedOnExit=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--native-root", type=Path, help="HybridCLR source repository")
    parser.add_argument("--runtime-root", type=Path, help="il2cpp_plus source repository")
    parser.add_argument("--generated-root", type=Path, help="Read-only generated IL2CPP tree for pinned external headers")
    parser.add_argument("--compiler", default="clang++")
    parser.add_argument("--output", type=Path, help="New immutable JSON receipt; existing files are refused")
    args = parser.parse_args()
    receipt = {"schemaVersion": 1, "kind": "M03NativeVisibilityPredicateRegression", "success": False,
               "startedUtc": dt.datetime.now(dt.timezone.utc).isoformat(), "commands": []}
    try:
        if args.output:
            require(not args.output.exists() and not args.output.is_symlink(), "Output receipt already exists")
            require(args.output.parent.is_dir(), "Output receipt parent directory must exist")
        execute(args, receipt)
        receipt["success"] = True
    except (helpers.TestFailure, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        receipt["error"] = str(error)
    receipt["finishedUtc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    encoded = json.dumps(receipt, indent=2) + "\n"
    if args.output and not args.output.exists() and not args.output.is_symlink() and args.output.parent.is_dir():
        try:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(encoded)
            print(json.dumps({key: receipt.get(key) for key in ("success", "visibilityChecks", "scenarios", "dependencyCount", "error")}
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
