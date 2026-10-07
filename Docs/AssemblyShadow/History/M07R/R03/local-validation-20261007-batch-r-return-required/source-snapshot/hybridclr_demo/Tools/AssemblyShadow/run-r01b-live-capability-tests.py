#!/usr/bin/env python3
"""Actual native live capability getters and managed negotiation; no Unity launch."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
helper_path = Path(__file__).with_name("run-m03-native-tests.py")
spec = importlib.util.spec_from_file_location("native_helpers", helper_path)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def run(command, cwd, receipt, phase):
    completed = subprocess.run([str(x) for x in command], cwd=cwd, text=True,
                               capture_output=True, timeout=180, check=False,
                               env={**os.environ, "ASAN_OPTIONS": "halt_on_error=1:abort_on_error=1",
                                    "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=1"})
    receipt["commands"].append(dict(phase=phase, argv=[str(x) for x in command], cwd=str(cwd),
                                    exitCode=completed.returncode, stdout=completed.stdout,
                                    stderr=completed.stderr))
    if completed.returncode:
        raise RuntimeError(f"{phase} failed ({completed.returncode}): {completed.stderr}")
    return completed.stdout


def execute(args, receipt):
    demo, native, runtime, package, installed = [p.resolve(strict=True) for p in
        (args.demo_root, args.native_root, args.runtime_root, args.package_root, args.installed_root)]
    external = installed.parent / "external"
    version = installed / "hybridclr/generated/UnityVersion.h"
    installation = installed / "assembly-shadow-install.json"
    install = json.loads(installation.read_text(encoding="utf-8-sig"))
    mono_root = (args.mono_root or Path("/Applications/Unity/Hub/Editor") / install["unityVersion"] /
                 "Unity.app/Contents/MonoBleedingEdge").resolve(strict=True)
    compiler = Path(shutil.which("clang++")).resolve(strict=True)
    mono = mono_root / "bin/mono"
    mcs = mono_root / "lib/mono/4.5/mcs.exe"
    nunit = (args.nunit or demo / "Library/PackageCache/com.unity.ext.nunit@1.0.6/net35/unity-custom/nunit.framework.dll").resolve(strict=True)
    sources = [demo / "Tools/AssemblyShadow/native-tests/r01b-live-capability.cpp",
               native / "hybridclr/RuntimeApi.cpp", native / "hybridclr/RuntimeConfig.cpp",
               runtime / "libil2cpp/vm/AssemblyShadowDiagnostics.cpp"]
    managed = [*[package / "Runtime" / name for name in
                 ("RuntimeOptionId.cs", "RuntimeApi.cs", "LoadImageErrorCode.cs", "HomologousImageMode.cs")],
               *[package / "Runtime/AssemblyShadow" / name for name in
                 ("AssemblyShadowDiagnostics.cs", "AssemblyShadowCapabilityReader.cs", "AssemblyShadowRuntime.cs",
                  "AssemblyShadowErrorCode.cs", "AssemblyShadowState.cs")],
               package / "Tests/Editor/AssemblyShadow/R01EarlyCapabilityNegotiationTests.cs",
               demo / "Tools/AssemblyShadow/tests/R01BLiveCapabilityStandalone.cs"]
    flags = ["-std=c++11", "-O1", "-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
             "-ffunction-sections", "-fdata-sections", "-DBASELIB_INLINE_NAMESPACE=il2cpp_baselib",
             "-include", str(version), "-I", str(runtime / "libil2cpp"), "-I", str(native),
             "-I", str(native / "hybridclr"), "-iquote", str(installed / "utils"),
             "-I", str(external / "google"), "-isystem", str(external / "baselib/Include"),
             "-isystem", str(external / "baselib/Platforms/OSX/Include"), "-I", str(external / "bdwgc/include")]
    dependencies = set(sources + managed + [Path(__file__).resolve(), helper_path.resolve(),
                       version, installation, compiler, mono.resolve(), mcs.resolve(), nunit])
    for enabled in (1, 0):
        for source in sources:
            output = run([compiler, *flags, f"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW={enabled}",
                          "-M", "-MT", "capability", source], runtime, receipt, "dependencies")
            dependencies.update(helper.dependencies(output, runtime))
    before = {str(p): helper.sha256(p) for p in sorted(dependencies)}
    receipt.update(inputs=before, dependencyCount=len(before), sourceHeads={name:
        subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
        for name, root in (("native", native), ("runtime", runtime), ("package", package), ("demo", demo))},
        boundary="Actual native RuntimeApi/RuntimeConfig/serializer with a managed-exception adapter; actual package negotiation/strict parser/Editor tests and RuntimeApi/AssemblyShadowRuntime wrappers compiled under both Player/Editor defines. Mono executes negotiation and Editor mock, not Player-only internal calls; only unused Unity types/namespaces are adapted. Synthetic diagnostic inventory, not real assembly loading or Player acceptance.",
        installedHeaderProvenance=dict(root=str(installed), externalRoot=str(external),
                                       installationSha256=helper.sha256(installation)))
    with tempfile.TemporaryDirectory(prefix="r01b-live-capability-") as directory:
        temporary = Path(directory)
        summaries = []
        for enabled in (1, 0):
            executable = temporary / f"native-{enabled}"
            run([compiler, *flags, f"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW={enabled}", *sources,
                 "-Wl,-dead_strip", "-Wl,-undefined,dynamic_lookup", "-o", executable], runtime, receipt, "compile-native")
            fixture = temporary / f"diagnostics-{enabled}.json"
            output = run([executable, fixture], runtime, receipt, "test-native")
            marker = re.search(r"r01b_live_capability_checks=(\d+) feature=(\d+) diagnostic_bytes=(\d+) PASS", output)
            if not marker or int(marker[2]) != enabled:
                raise RuntimeError("native capability proof marker missing")
            summaries.append(dict(feature=enabled, checks=int(marker[1]), diagnosticBytes=int(marker[3]),
                                  executableSha256=helper.sha256(executable), fixtureSha256=helper.sha256(fixture)))
        # Also compile the production getter without an Assembly Shadow define.
        run([compiler, *flags, "-fsyntax-only", native / "hybridclr/RuntimeConfig.cpp"], runtime, receipt, "syntax-default-off")
        shutil.copy2(nunit, temporary / nunit.name)
        managed_summaries = []
        for defines in ("ENABLE_IL2CPP", "UNITY_EDITOR,ENABLE_IL2CPP"):
            executable = temporary / ("managed-" + defines.replace(",", "-") + ".exe")
            run([mono, mcs, "-langversion:latest", "-unsafe", "-define:" + defines, f"-r:{nunit}",
                 f"-out:{executable}", *managed], demo, receipt, "compile-managed")
            output = run([mono, executable, temporary / "diagnostics-1.json"], demo, receipt, "test-managed")
            marker = re.search(r"r01b_live_capability_managed_tests=(\d+).* PASS", output)
            if not marker:
                raise RuntimeError("managed capability proof marker missing")
            managed_summaries.append(dict(defines=defines, tests=int(marker[1]),
                                          executableSha256=helper.sha256(executable)))
        receipt.update(nativeTests=summaries, managedTests=managed_summaries)
    changed = [p for p, digest in before.items() if helper.sha256(Path(p)) != digest]
    if changed:
        raise RuntimeError("inputs changed: " + ", ".join(changed))
    receipt.update(success=True, inputsUnchanged=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("demo-root", "native-root", "runtime-root", "package-root", "installed-root", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--mono-root", type=Path)
    parser.add_argument("--nunit", type=Path)
    args = parser.parse_args()
    if args.output.exists() or not args.output.parent.is_dir():
        parser.error("Output must be new and its parent must exist")
    receipt = dict(schemaVersion=1, kind="R01BLiveCapabilityRegression", success=False, commands=[],
                   startedUtc=dt.datetime.now(dt.timezone.utc).isoformat())
    try:
        execute(args, receipt)
    except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as error:
        receipt["error"] = str(error)
    receipt["finishedUtc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    with args.output.open("x") as output:
        json.dump(receipt, output, indent=2)
        output.write("\n")
    print(json.dumps({k: receipt.get(k) for k in
                     ("success", "nativeTests", "managedTests", "inputsUnchanged", "dependencyCount", "error")}))
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
