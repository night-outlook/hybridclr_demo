#!/usr/bin/env python3
"""Test R01B native count boundaries using exact production method bodies.

Signature/override resolution is adapted; count-bearing methods and native
layouts are production code. Both full production units are syntax checked.
No Unity, installation, Player, or whole loader acceptance is claimed.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract(source, signature):
    start = source.index(signature)
    opening = source.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        if source[end] == "{":
            depth += 1
        elif source[end] == "}":
            depth -= 1
        end += 1
    return source[start:end]


def run(argv, root, receipt, phase):
    env = os.environ.copy()
    env.update(ASAN_OPTIONS="halt_on_error=1:abort_on_error=1", UBSAN_OPTIONS="halt_on_error=1")
    result = subprocess.run(list(map(str, argv)), cwd=root, capture_output=True, text=True, env=env)
    receipt["commands"].append(dict(phase=phase, argv=list(map(str, argv)), exitCode=result.returncode,
                                    stdout=result.stdout, stderr=result.stderr))
    if result.returncode:
        raise RuntimeError(phase + " failed: " + result.stderr[-5000:])
    return result.stdout


def execute(args, receipt):
    demo, native, runtime, installed = [p.resolve(strict=True) for p in
                                       (args.demo_root, args.native_root, args.runtime_root, args.installed_root)]
    compiler = Path(shutil.which(args.compiler)).resolve(strict=True)
    metadata = native / "hybridclr/metadata"
    image, vtable = metadata / "InterpreterImage.cpp", metadata / "VTableSetup.cpp"
    helper, header = metadata / "InterpreterMetadataCounts.h", metadata / "VTableSetup.h"
    test = demo / "Tools/AssemblyShadow/r01b-native-counts.cpp"
    version = installed / "hybridclr/generated/UnityVersion.h"
    external = installed.parent / "external"
    inputs = [image, vtable, helper, header, test, version, compiler, Path(__file__).resolve()]
    receipt["inputsBefore"] = {str(p): sha(p) for p in inputs}
    source = vtable.read_text()
    signatures = ["bool FindType(", "void VTableSetUp::InitInterfaceVTable(",
                  "void VTableSetUp::ComputeOverrideParentVirtualMethod(",
                  "void VTableSetUp::ComputeInterpTypeVtables("]
    bodies = "namespace hybridclr { namespace metadata {\n" + "\n\n".join(extract(source, s) for s in signatures) + "\n}}\n"
    receipt["extractedProductionMethods"] = signatures
    receipt["extractedSourceSha256"] = hashlib.sha256(bodies.encode()).hexdigest()
    image_source = image.read_text()
    for method, count_marker in (("InitProperties", "TryListRange"), ("InitEvents", "TryListRange"),
                                 ("InitInterfaces", "CanAppend"), ("ComputeVTable", "CanAppend")):
        if "InterpreterMetadataCounts::" + count_marker not in extract(image_source, "void InterpreterImage::" + method + "("):
            raise RuntimeError("missing production count guard in " + method)
    includes = []
    for switch, path in [
        ("-I", runtime / "libil2cpp"), ("-I", native), ("-I", native / "hybridclr"),
        ("-isystem", external / "baselib/Include"), ("-isystem", external / "baselib/Platforms/OSX/Include"),
        ("-iquote", installed / "utils"), ("-I", external / "google"),
        ("-I", external / "bdwgc/include"), ("-I", external / "bdwgc/libatomic_ops/src"),
        ("-I", external / "xxHash")]:
        includes.extend([switch, str(path.resolve(strict=True))])
    defines = ["-D%s=%s" % pair for pair in re.findall(r"^#define\s+(HYBRIDCLR_UNITY_[A-Z0-9_]+)\s+(\d+)\s*$", version.read_text(), re.M)]
    common = [compiler, "-std=c++11", "-Wall", "-Wextra", "-Wno-unused-parameter",
              "-DBASELIB_INLINE_NAMESPACE=il2cpp_baselib", "-DIL2CPP_DEBUG=0", "-DIL2CPP_ENABLE_ASSERTIONS=0", *defines, *includes]
    runtime_sources = [runtime / "libil2cpp" / name for name in
                       ("utils/Memory.cpp", "os/Posix/Memory.cpp", "os/Generic/Assert.cpp")]
    inputs += runtime_sources
    receipt["inputsBefore"].update({str(p): sha(p) for p in runtime_sources})
    with tempfile.TemporaryDirectory(prefix="r01b-native-counts-") as temporary:
        root = Path(temporary)
        (root / "r01b-native-counts-production.inc").write_text(bodies)
        for label, options in (("release", ["-O2", "-DNDEBUG"]),
                               ("asan-ubsan", ["-O1", "-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer"])):
            executable = root / label
            run([*common, "-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1", *options, "-I", root,
                 test, *runtime_sources, "-o", executable], native, receipt, "compile-" + label)
            result = run([executable], native, receipt, "run-" + label)
            match = re.search(r"r01b_native_count_checks=(\d+) PASS", result)
            if not match or int(match[1]) < 30:
                raise RuntimeError("missing native count coverage")
            receipt[label + "Checks"] = int(match[1])
        for shadow in (0, 1):
            for production in (image, vtable):
                run([*common, "-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=" + str(shadow), "-fsyntax-only", production],
                    native, receipt, "syntax-" + production.name + "-shadow-" + str(shadow))
    receipt["inputsAfter"] = {str(p): sha(p) for p in inputs}
    receipt["inputsUnchanged"] = receipt["inputsAfter"] == receipt["inputsBefore"]
    if not receipt["inputsUnchanged"]:
        raise RuntimeError("production inputs changed during test")
    receipt["success"] = True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("demo-root", "native-root", "runtime-root", "installed-root", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--compiler", default="clang++")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.parent.is_dir():
        raise RuntimeError("receipt must be fresh and parent must exist")
    receipt = dict(schemaVersion=1, kind="R01BNativeCounts", success=False, commands=[],
                   startedUtc=dt.datetime.now(dt.timezone.utc).isoformat(),
                   boundary="Production count helper and extracted verbatim VTableSetUp count-bearing methods with native layouts; pointer identity, signature/override resolution and managed exceptions adapted. Full production InterpreterImage.cpp and VTableSetup.cpp syntax checked ON/OFF. No Unity, Player or whole-loader runtime acceptance.")
    try:
        execute(args, receipt)
    except Exception as error:
        receipt["error"] = str(error)
    receipt["finishedUtc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({key: receipt.get(key) for key in ("success", "releaseChecks", "asan-ubsanChecks", "error")} | {"receipt": str(output)}))
    return 0 if receipt["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
