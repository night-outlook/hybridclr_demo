#!/usr/bin/env python3
"""Exercise the production startup gateway with explicit native VM adapters.

No Unity, installed-tree mutation, or Player execution. Real gateway resolution
and method checks use actual VM structures; lookup/invocation are test adapters.
Failure scenarios execute the production non-returning terminator in child
processes, including its real exit code and suppression of atexit callbacks.
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

    def run(argv, expected_exit=0, **kwargs):
        result = subprocess.run([str(v) for v in argv], capture_output=True, text=True, timeout=180, **kwargs)
        receipt["commands"].append({"argv": [str(v) for v in argv], "exitCode": result.returncode,
                                    "stdout": result.stdout, "stderr": result.stderr})
        if result.returncode != expected_exit:
            raise RuntimeError(f"command exited {result.returncode}, expected {expected_exit}: {result.stderr[-3000:]}")
        return result

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
                     "managed-throw", "reentry", "refuse-13", "refuse-19"]
        successful = {"success", "global-namespace", "empty", "off"}
        unexpected = {"native-throw", "managed-throw", "reentry"}
        invoked = {"success", "global-namespace", "null-result", "wrong-result", "refuse",
                   "refuse-13", "refuse-19", *unexpected}
        no_lookup = {"empty", "schema", "partial", "namespace-only", "bad-name", "null-name",
                     "before-core", "core-failed", "wrong-thread", "off"}
        failure_reasons = {}
        for names, reason in (
            ("schema partial namespace-only bad-name null-name", "Invalid generated bootstrap configuration"),
            ("before-core", "Core runtime initialization is incomplete"),
            ("core-failed", "Core runtime initialization failed"),
            ("wrong-thread", "Bootstrap dispatch requires the attached main thread"),
            ("missing-assembly wrong-assembly candidate dynamic interpreter", "Bootstrap assembly is not an exact physical noncandidate AOT assembly"),
            ("missing-type nested generic-type wrong-type wrong-type-image", "Bootstrap type is not an exact nonnested nongeneric definition"),
            ("instance abstract generic-method inflated-method parameters wrong-return byref-return wrong-method wrong-owner uncallable duplicate-method",
             "Bootstrap requires one callable static nongeneric parameterless Int32 method"),
            ("null-result", "Bootstrap returned no boxed result"),
            ("wrong-result", "Bootstrap returned a non-Int32 result"),
            ("refuse refuse-13 refuse-19", "Bootstrap explicitly refused startup"),
            ("native-throw managed-throw", "Bootstrap raised an unexpected exception"),
            ("reentry", "Concurrent or recursive initialization during bootstrap"),
        ):
            failure_reasons.update({name: reason for name in names.split()})
        if set(scenarios) != (successful - {"off"}) | set(failure_reasons):
            raise RuntimeError("gateway scenarios do not have exact expected outcomes")
        receipt["compilerVersion"] = run([compiler, "--version"]).stdout
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
                    death = scenario not in successful
                    completed = run([binary, scenario], expected_exit=1 if death else 0, env=env)
                    text, errors = completed.stdout, completed.stderr
                    assertions = 0

                    def check(condition, message):
                        nonlocal assertions
                        assertions += 1
                        if not condition:
                            raise RuntimeError(f"{scenario}: {message}")

                    check("r01_gateway_check_failed=" not in errors, "native adapter assertion failed")
                    checkpoints = [int(value) for value in re.findall(r"^r01_gateway_check=(\d+) PASS$", errors, re.M)]
                    check(bool(checkpoints) and checkpoints == list(range(1, len(checkpoints) + 1)),
                          "native checks are missing or nonsequential")
                    events = re.findall(r"^r01_gateway_event=([a-z-]+) checks=\d+$", errors, re.M)
                    check(events.count("lookup") == (0 if scenario in no_lookup else 1), "physical lookup count differs")
                    check(events.count("invoke") == int(scenario in invoked), "callback invocation count differs")
                    check(events.count("seal") == int(scenario in unexpected), "unexpected-failure seal count differs")
                    termination = "[AssemblyShadowStartup] Terminating process before host continuation (exit=1)"
                    if death:
                        check(events.count("before-init") == 1, "failure did not enter the real initialization boundary")
                        check(not any(name in events for name in ("post-init", "post-recursive-init", "atexit")),
                              "startup failure continued or ran process-exit callbacks")
                        failure = "[AssemblyShadowStartup] Failed: " + failure_reasons[scenario]
                        lines = errors.splitlines()
                        check(lines.count(failure) == 1, "wrong or repeated failure classification")
                        check(lines[-2:] == [failure, termination] and lines.count(termination) == 1,
                              "missing exact final failure/termination lines")
                        check("r01_startup_gateway_checks=" not in text, "failed startup reached the success marker")
                    else:
                        match = re.search(r"^r01_startup_gateway_checks=(\d+) scenario=" + re.escape(scenario) + r" PASS$", text, re.M)
                        check(match is not None and int(match[1]) == len(checkpoints), "missing or inconsistent pass marker")
                        check("[AssemblyShadowStartup]" not in errors, "successful startup entered failure termination")
                        check(events.count("post-init") == int(bool(enabled)), "successful startup did not continue")
                        check(events.count("atexit") == int(bool(enabled)), "atexit sentinel was not functional")
                    receipts.append({"scenario": scenario, "enabled": bool(enabled), "deathTest": death,
                                     "exitCode": completed.returncode, "checks": len(checkpoints),
                                     "processAssertions": assertions})
                # These real translation units include the actual wrapper/core
                # integration, not just a source-text assertion.
                for unit in (vm / "il2cpp-api.cpp", vm / "vm/Runtime.cpp", vm / "vm/AssemblyShadowStartup.cpp",
                             native / "hybridclr/generated/AssemblyManifest.cpp"):
                    run([compiler, *flags, *mode, "-fsyntax-only", unit])
                if not enabled:
                    symbols = run(["nm", "-u", binary]).stdout
                    if "g_assemblyShadowStartupBootstrap" in symbols:
                        raise RuntimeError("OFF executable references generated bootstrap symbols")
        if hashes != {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}:
            raise RuntimeError("an input changed during verification")
        receipt.update(result="Passed", scenarios=receipts, checks=sum(v["checks"] for v in receipts),
                       processAssertions=sum(v["processAssertions"] for v in receipts),
                       deathTests=sum(v["deathTest"] for v in receipts),
                       inputsUnchanged=True, syntaxChecks=8,
                       boundary="Production gateway, real non-returning failure termination in child processes, and exact VM structures; explicit lookup/invocation/exception/sealing adapters. Death tests verify exit 1, failure reason, no host or recursive continuation and no atexit callbacks. Explicit callback codes 13/19 verify no unexpected-failure seal; actual recovery state remains a Player/state-machine boundary. Pure gate concurrency/reentry checks. No Unity, GC, full Runtime::Init, or Player execution.")
    except Exception as error:
        receipt["error"] = str(error)
    receipt["finishedUtc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with output.open("x") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    print(json.dumps({k: receipt[k] for k in ("result", "checks", "processAssertions", "deathTests", "syntaxChecks", "error") if k in receipt}))
    return 0 if receipt["result"] == "Passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
