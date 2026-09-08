#!/usr/bin/env python3
"""Exercise the production startup gateway with explicit native VM adapters.

No Unity, installed-tree mutation, or Player execution. Real gateway resolution
and method checks use actual VM structures; lookup/invocation are test adapters.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--runtime-root", required=True, type=Path)
    parser.add_argument("--hybridclr-root", required=True, type=Path)
    parser.add_argument("--installed-root", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.parent.is_dir():
        parser.error("output must be a new file in an existing directory")
    receipt = {"schemaVersion": 1, "kind": "R01StartupGatewayNative", "result": "Failed", "commands": []}
    receipt["startedUtc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def run(argv, **kwargs):
        result = subprocess.run([str(v) for v in argv], capture_output=True, text=True, timeout=180, **kwargs)
        receipt["commands"].append({"argv": [str(v) for v in argv], "exitCode": result.returncode,
                                    "stdout": result.stdout, "stderr": result.stderr})
        if result.returncode:
            raise RuntimeError(f"command failed ({result.returncode}): {result.stderr[-3000:]}")
        return result.stdout

    try:
        demo, runtime, native = args.demo_root.resolve(), args.runtime_root.resolve(), args.hybridclr_root.resolve()
        installed = (args.installed_root or demo / "HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp").resolve()
        external = installed.parent / "external"
        version = installed / "hybridclr/generated/UnityVersion.h"
        defines = re.findall(r"^#define\s+(HYBRIDCLR_UNITY_[A-Z0-9_]+)\s+(\d+)\s*$", version.read_text(), re.MULTILINE)
        compiler = shutil.which("clang++")
        if not compiler:
            raise RuntimeError("clang++ is required")
        source = demo / "Tools/AssemblyShadow/native-tests/r01_startup_gateway.cpp"
        vm = runtime / "libil2cpp"
        inputs = [Path(__file__).resolve(), source, version,
                  vm / "vm/AssemblyShadowStartup.h", vm / "vm/AssemblyShadowStartup.cpp",
                  vm / "vm/AssemblyShadowStartupGate.h", vm / "il2cpp-api.cpp", vm / "vm/Runtime.cpp",
                  native / "hybridclr/generated/AssemblyManifest.cpp"]
        hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
        receipt["inputHashes"] = hashes
        flags = ["-std=c++11", "-DBASELIB_INLINE_NAMESPACE=il2cpp_baselib",
                 "-I", vm, "-I", native, "-I", external / "google",
                 "-isystem", external / "baselib/Include",
                 "-isystem", external / "baselib/Platforms/OSX/Include",
                 "-iquote", installed / "utils"]
        flags += [f"-D{name}={value}" for name, value in defines]
        scenarios = ["success", "global-namespace", "empty", "schema", "partial", "namespace-only",
                     "bad-name", "null-name", "before-core", "core-failed", "wrong-thread",
                     "missing-assembly", "wrong-assembly", "candidate", "dynamic", "interpreter",
                     "missing-type", "nested", "generic-type", "wrong-type", "wrong-type-image",
                     "instance", "abstract", "generic-method", "inflated-method", "parameters",
                     "wrong-return", "byref-return", "wrong-method", "wrong-owner", "uncallable",
                     "duplicate-method", "null-result", "wrong-result", "refuse", "native-throw",
                     "managed-throw", "reentry"]
        receipt["compilerVersion"] = run([compiler, "--version"])
        receipts = []
        with tempfile.TemporaryDirectory(prefix="r01-startup-gateway-") as folder:
            for enabled in (1, 0):
                binary = Path(folder) / f"gateway-{enabled}"
                mode = [f"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW={enabled}"]
                run([compiler, *flags, *mode, "-O1", "-g", "-fsanitize=address", "-fno-omit-frame-pointer",
                     "-pthread", source, "-o", binary])
                for scenario in scenarios if enabled else ["off"]:
                    env = dict(os.environ, ASAN_OPTIONS="halt_on_error=1:abort_on_error=1")
                    env.pop("R01_GATEWAY_BAD_SCHEMA", None)
                    if scenario == "schema":
                        env["R01_GATEWAY_BAD_SCHEMA"] = "1"
                    text = run([binary, scenario], env=env)
                    match = re.search(r"^r01_startup_gateway_checks=(\d+) scenario=" + re.escape(scenario) + r" PASS$", text, re.M)
                    if not match:
                        raise RuntimeError(f"missing pass marker: {scenario}")
                    receipts.append({"scenario": scenario, "enabled": bool(enabled), "checks": int(match[1])})
                # These real translation units include the actual wrapper/core
                # integration, not just a source-text assertion.
                for unit in (vm / "il2cpp-api.cpp", vm / "vm/Runtime.cpp", vm / "vm/AssemblyShadowStartup.cpp",
                             native / "hybridclr/generated/AssemblyManifest.cpp"):
                    run([compiler, *flags, *mode, "-fsyntax-only", unit])
                if not enabled:
                    symbols = run(["nm", "-u", binary])
                    if "g_assemblyShadowStartupBootstrap" in symbols:
                        raise RuntimeError("OFF executable references generated bootstrap symbols")
        if hashes != {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}:
            raise RuntimeError("an input changed during verification")
        receipt.update(result="Passed", scenarios=receipts, checks=sum(v["checks"] for v in receipts),
                       inputsUnchanged=True, syntaxChecks=8,
                       boundary="Production gateway and exact VM structures; explicit lookup/invocation/exception adapters. Pure gate concurrency/reentry checks. No Unity, GC, full Runtime::Init, or Player execution.")
    except Exception as error:
        receipt["error"] = str(error)
    receipt["finishedUtc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with output.open("x") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    print(json.dumps({k: receipt[k] for k in ("result", "checks", "syntaxChecks", "error") if k in receipt}))
    return 0 if receipt["result"] == "Passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
