#!/usr/bin/env python3
"""Actual compiler+native execution contract for isolated source-derived Bi4.

Inputs MUST come from the real .NET8 fixture generator and the real C# source
bridge augmentation, checked out at authenticated exact Git source commits.
The C++ harness uses only tiny host ABI stubs: NOT Unity or an actual Player.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def inspect_cpp(path: Path):
    raw = path.read_bytes()
    data = raw.decode("utf-8", "strict")
    head = "// R03 initializer source-bound Bi4 bridge (test-only)"
    table = "const Managed2NativeFunctionPointerCallData hybridclr::interpreter::g_managed2NativeFunctionPointerCallStub[]"
    need(data.count(head) == 1 and data.count(table) == 1,
         "Exact isolated Bi4 wrapper and one table declaration")
    need(data.count('"Bi4"') == 1 and data.count('__M2NF_Bi4') == 2,
         "One Bi4 row and its actual native wrapper function")
    index = data.index(table)
    need(data.index(head) < index and
         re.search(r'\{"Bi4",\s*__M2NF_Bi4\},', data[index:]) and
         re.search(r'\{nullptr,\s*nullptr\}', data[index:]),
         "Native call table has exactly one bridge and a null sentinel")
    end = data.index("\n};", index) + 3
    fragment = data[data.index(head):end]
    need("typedef int32_t (CDECL *NativeMethod)();" in fragment and
         "*(int32_t*)ret = ((NativeMethod)(methodPointer))();" in fragment,
         "Generated int32 Cdecl native call body")
    return fragment, hashlib.sha256(raw).hexdigest()


PREFIX = r"""
#include <cassert>
#include <cstdint>
#include <cstring>
#define CDECL
using Il2CppMethodPointer = void (*)();
union StackObject { uint64_t value; };
using NativeFn = void (*)(Il2CppMethodPointer, uint16_t*, StackObject*, void*);
struct Managed2NativeFunctionPointerCallData
{
    const char* methodSig;
    NativeFn methodPointer;
};
namespace hybridclr { namespace interpreter {
extern const Managed2NativeFunctionPointerCallData g_managed2NativeFunctionPointerCallStub[];
}}
using namespace hybridclr::interpreter;
"""

SUFFIX = r"""
static int32_t HostNativeCdeclInt32NoArgs() { return 42; }
int main()
{
    int count=0;
    for (int i=0; i<4; ++i)
    {
        auto const& row = g_managed2NativeFunctionPointerCallStub[i];
        if (!row.methodSig) break;
        assert(std::strcmp(row.methodSig, "Bi4")==0);
        assert(row.methodPointer != nullptr);
        int32_t value=-1;
        row.methodPointer(reinterpret_cast<Il2CppMethodPointer>(&HostNativeCdeclInt32NoArgs),
                          nullptr, nullptr, &value);
        assert(value==42);
        ++count;
    }
    assert(count==1);
    return 0;
}
"""


def verify(bridge: Path):
    need(bridge.is_file() and not bridge.is_symlink(), "Actual augmented source file required")
    fragment, digest = inspect_cpp(bridge)
    compilers = [v for v in ("clang++", "g++") if shutil.which(v)]
    need(compilers, "An actual host compiler required")
    with tempfile.TemporaryDirectory(prefix="r03-bi4-compiled-host-") as folder:
        root = Path(folder)
        source = root / "bridge_host.cpp"
        source.write_text(PREFIX + fragment + SUFFIX, encoding="utf-8")
        for compiler in compilers:
            output = root / (compiler.replace("+", "p") + "-linked")
            result = subprocess.run([compiler, "-std=c++11", "-Wall", "-Wextra",
                                     "-Werror", str(source), "-o", str(output)],
                                    capture_output=True, text=True, timeout=90)
            need(result.returncode == 0,
                 "Actual Bi4 C++11 native host compile failed: " + result.stderr[-1400:])
            run = subprocess.run([str(output)], capture_output=True, text=True, timeout=20)
            need(run.returncode == 0, "Actual compiled Bi4 wrapper invocation failed")
    return {"result": "PassedRealCdeclBi4NativeHostOnly_NotUnity",
            "generatedSourceSha256": digest, "compilers": compilers,
            "realUnityPlayerExecuted": False, "R03Accepted": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge", type=Path, required=True)
    import json
    args = parser.parse_args()
    print(json.dumps(verify(args.bridge), sort_keys=True))
