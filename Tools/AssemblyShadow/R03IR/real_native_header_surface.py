#!/usr/bin/env python3
"""Source-only compatibility of A2 against the exact public IL2CPP fork.

The public fork excludes official Unity SDK external/Baselib and generated
UnityVersion.h. This checks the real fork declarations/implementations only.
It explicitly DOES NOT compile the translation unit or prove runtime error15.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

NATIVE = "41764ae1eeefb33b05966e7f7676e52aae39c340"
FILES = {
    "vm/MetadataCache.h": (
        "GetGenericInstanceMethod(const MethodInfo* genericMethodDefinition, "
        "const Il2CppType** genericArgumentTypes, uint32_t genericArgumentCount)",
        "GetAssemblyTypeHandle(const Il2CppImage* image, AssemblyTypeIndex index)",
        "GetTypeNamespaceAndName(Il2CppMetadataTypeHandle handle)",
        "GetAotAssemblyByNamePhysical(const char* name)",
    ),
    "vm/Class.h": (
        "GetMethodFromName(Il2CppClass *klass, const char* name, int argsCount)",
        "GetFieldFromName(Il2CppClass *klass, const char* name)",
    ),
    "vm/Image.h": (
        "ClassFromName(const Il2CppImage* image, const char* namespaze, const char *name)",
    ),
    "vm/Runtime.h": (
        "Invoke(const MethodInfo *method, void *obj, void **params, Il2CppException **exc)",
    ),
    "vm/AssemblyShadow.h": (
        "GetState(AssemblyShadowState& state)",
        "AssertMethodIsActive(const MethodInfo* method, const char* site)",
        "GetRecoveryInfoJson(std::string& json)",
        "ActiveGeneration()",
    ),
    "vm/AssemblyShadowTypes.h": (
        "BaselineAlreadyUsed = 15", "FailedAfterCommit = 9",
    ),
    "il2cpp-class-internals.h": (
        "typedef struct FieldInfo", "typedef struct MethodInfo",
        "static_fields_size", "const Il2CppGenericMethod* genericMethod",
    ),
    "il2cpp-runtime-metadata.h": (
        "typedef struct Il2CppType", "Il2CppMetadataTypeHandle typeHandle",
        "const Il2CppGenericInst *method_inst",
    ),
    "vm/MetadataCache.cpp": (
        "MetadataCache::GetGenericInstanceMethod(",
        "GetGenericInst(genericArgumentTypes, genericArgumentCount)",
    ),
    "vm/GlobalMetadata.cpp": (
        "GlobalMetadata::GetGenericInstanceMethod(",
        "GenericMethod::GetMethod(method, classInst, methodInst)",
    ),
    "metadata/GenericMethod.cpp": (
        "GenericMetadata::InflateIfNeeded(",
        "MetadataCache::GetGenericMethodPointers(",
    ),
    "vm/AssemblyShadow.cpp": (
        "struct CapturedArgumentVisitor",
        'Fail("CapturedBaselineType", candidate)',
        'visitor.Context(method->genericMethod->context, "class_inst", "method_inst")',
        "RecordFirstGuardFailure(error, detail)",
    ),
}
PROBE = (
    "MetadataCache::GetAotAssemblyByNamePhysical(kBaseline)",
    "MetadataCache::GetAssemblyTypeHandle(baseline->image, index)",
    "MetadataCache::GetTypeNamespaceAndName(handle)",
    "MetadataCache::GetGenericInstanceMethod(",
    "AssemblyShadow::AssertMethodIsActive(",
    "Runtime::Invoke(witness.inflated, nullptr, nullptr, &exception)",
    "witness.invokeThrew = exception != nullptr ? 1 : 0;",
    "!witness.invokeThrew",
)


class SourceRejected(ValueError):
    pass


def need(ok, msg):
    if not ok:
        raise SourceRejected(msg)


def normalize(raw: bytes):
    need(type(raw) is bytes and 0 < len(raw) < 2000000, "Exact bounded native source bytes")
    return re.sub(r"\s+", " ", raw.decode("utf-8", "strict"))


def inspect(fork: dict, probe: bytes):
    need(type(fork) is dict and set(fork) == set(FILES),
         "Exact source file roster with no omitted or synthetic headers")
    hits = []
    for relative, anchors in FILES.items():
        raw = fork[relative]
        normalized = normalize(raw)
        for anchor in anchors:
            need(re.sub(r"\s+", " ", anchor) in normalized,
                 "Native fork ABI/behavior drift: " + relative + ": " + anchor)
        hits.append({"path": "libil2cpp/" + relative,
                     "sha256": hashlib.sha256(raw).hexdigest(),
                     "declarations": len(anchors)})
    value = normalize(probe)
    for anchor in PROBE:
        need(re.sub(r"\s+", " ", anchor) in value, "A2 source entry path missing: " + anchor)
    need("Class::FromIl2CppType(" not in value,
         "Physical baseline argument cannot be materialized in the test witness")
    return {
        "kind": "R03A2RealForkSourceSurfaceV1",
        "result": "PassedForkAPISourceDeclarations_NoSDKCompile",
        "nativeForkCommit": NATIVE,
        "realNativeFilesChecked": hits,
        "probeSha256": hashlib.sha256(probe).hexdigest(),
        "nativeApiMocksUsed": False,
        "UnitySdkBaselibPresent": False,
        "translationUnitCompiledAgainstUnitySdk": False,
        "realIl2cppGenericContextObserved": False,
        "realNativeCapturedFailure15": False,
        "R03Accepted": False, "H2Passed": False, "runtimeAcceptance": False,
    }


def read(fork_root: Path, probe_path: Path):
    need(fork_root.is_absolute() and fork_root.is_dir() and
         fork_root.resolve(strict=True) == fork_root and not fork_root.is_symlink(),
         "Canonical exact external native fork checkout")
    need(probe_path.is_absolute() and probe_path.is_file() and
         probe_path.resolve(strict=True) == probe_path and not probe_path.is_symlink(),
         "Canonical actual Primary A2 native probe")
    raw = {}
    for name in FILES:
        file = fork_root / "libil2cpp" / name
        need(file.is_file() and not file.is_symlink() and
             file.resolve(strict=True) == file,
             "Native fork source file missing/aliased: " + name)
        raw[name] = file.read_bytes()
    return inspect(raw, probe_path.read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fork", required=True, type=Path)
    parser.add_argument("--probe", required=True, type=Path)
    result = read(parser.parse_args().fork, parser.parse_args().probe)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (SourceRejected, OSError, ValueError, UnicodeError) as error:
        print("R03_A2_REAL_HEADER_SURFACE_BLOCKED: " + str(error), file=sys.stderr)
        raise SystemExit(1)
