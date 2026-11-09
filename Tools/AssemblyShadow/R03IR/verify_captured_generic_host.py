#!/usr/bin/env python3
"""Strict host-only structural receipt for R03 captured-generic prerequisite.

This validates a real CLR MethodInfo whose owner differs from physical Methods.
It does NOT simulate native IL2CPP type indices, method entry or error 15.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

KIND = "R03CapturedGenericOwnerHostV1"
RESULT = "PassedCLRPhysicalOwnerStructureAndBodies_NotUnity"
OWNER = "R03CapturedGenericHost"
METHOD = "AssemblyShadow.R03.IR.R03CapturedGenericAotOwner.Touch<T>"
SHA = re.compile(r"[0-9a-f]{64}\Z")
MVID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z")

FIELDS = frozenset((
    "schemaVersion", "kind", "result", "ownerAssembly", "ownerMethod",
    "capturedArgumentAssembly", "capturedArgumentType",
    "ownerHasStaticMethodsDependency", "ownerDifferentFromArgument",
    "openGenericDefinition", "closedGenericMethod", "genericArity",
    "referenceTypeConstraint", "methodsSha256", "methodsMvid", "methodsSize",
    "clrModuleMvidMatches", "prewarmedReturn", "reflectiveReturn",
    "delegatedReturn", "callCountAfterWarm", "callCountAfterReflection",
    "callCountAfterDelegate", "wrongOwnerRejectedByWitnessContract",
    "invalidValueTypeRejectedByCLR", "il2cppMethodContextObserved",
    "nativeGuardExecuted", "capturedBaselineFailure15Observed",
    "unityOrPlayerExecuted", "originalSReusedAsNewInput",
    "runtimeAcceptance", "R03Accepted", "H2Passed"
))


class HostRejected(ValueError):
    pass


def need(condition, reason):
    if not condition:
        raise HostRejected(reason)


def loads(raw: bytes):
    need(type(raw) is bytes and 0 < len(raw) <= 8192, "Bounded host receipt bytes")
    def unique(items):
        out = {}
        for key, value in items:
            need(key not in out, "Duplicate host receipt JSON key: " + key)
            out[key] = value
        return out
    return json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=unique,
                      parse_constant=lambda s: (_ for _ in ()).throw(HostRejected("Nonfinite JSON: " + s)))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify(receipt_bytes: bytes, methods: bytes, owner_source: bytes, native_source: bytes):
    record = loads(receipt_bytes)
    need(type(record) is dict and set(record) == FIELDS, "Exact typed host receipt schema")
    need(type(record["schemaVersion"]) is int and record["schemaVersion"] == 1 and
         record["kind"] == KIND and record["result"] == RESULT and
         record["ownerAssembly"] == OWNER and record["ownerMethod"] == METHOD and
         record["capturedArgumentAssembly"] == "Methods" and
         record["capturedArgumentType"] == "R03.Node", "Physical source/CLR type owner distinction")
    for field in ("ownerDifferentFromArgument", "openGenericDefinition",
                  "closedGenericMethod", "referenceTypeConstraint", "clrModuleMvidMatches",
                  "wrongOwnerRejectedByWitnessContract", "invalidValueTypeRejectedByCLR"):
        need(record[field] is True, "Required positive CLR structural field: " + field)
    for field in ("ownerHasStaticMethodsDependency", "il2cppMethodContextObserved",
                  "nativeGuardExecuted", "capturedBaselineFailure15Observed",
                  "unityOrPlayerExecuted", "originalSReusedAsNewInput",
                  "runtimeAcceptance", "R03Accepted", "H2Passed"):
        need(record[field] is False, "No invented Unity/native evidence: " + field)
    for field, expected in {
        "genericArity": 1,
        "prewarmedReturn": 42, "reflectiveReturn": 42, "delegatedReturn": 42,
        "callCountAfterWarm": 1, "callCountAfterReflection": 2,
        "callCountAfterDelegate": 3,
    }.items():
        need(type(record[field]) is int and record[field] == expected,
             "Exact real CLR call/side-effect field: " + field)
    need(type(methods) is bytes and len(methods) > 0 and
         type(record["methodsSize"]) is int and record["methodsSize"] == len(methods) and
         type(record["methodsSha256"]) is str and SHA.fullmatch(record["methodsSha256"]) and
         record["methodsSha256"] == sha(methods) and
         type(record["methodsMvid"]) is str and
         MVID.fullmatch(record["methodsMvid"]), "Published physical Methods input SHA/MVID/size")
    need(type(owner_source) is bytes and type(native_source) is bytes,
         "Actual source bytes required")
    owner = owner_source.decode("utf-8", "strict")
    native = native_source.decode("utf-8", "strict")
    # Fail closed if a future editor edits the AOT-source semantics without
    # explicitly updating this exact bounded test-only witness contract.
    for anchor in ("public static class R03CapturedGenericAotOwner",
                   "public static int Touch<T>() where T : class",
                   "where T : class", "Interlocked.Increment(ref s_calls)",
                   "return Touch<object>();", "MethodImplOptions.NoInlining"):
        need(anchor in owner, "AOT owner source witness missing: " + anchor)
    active_lines = "\n".join(line for line in owner.splitlines()
                             if not line.lstrip().startswith("//"))
    need("using Methods" not in active_lines and
         "typeof(Methods." not in active_lines and
         "Methods.R03.Node" not in active_lines and
         "typeof(T)" not in active_lines,
         "No static Methods reference or eager generic argument reflection")
    for anchor in ("struct CapturedArgumentVisitor",
                   'Fail("CapturedBaselineType", candidate)',
                   'visitor.Context(method->genericMethod->context',
                   'AssemblyShadow::AssertMethodIsActive',
                   'PhysicalMethodAssembly(method)',
                   'RecordFirstGuardFailure(error, detail)'):
        need(anchor in native, "Pinned native source guard missing: " + anchor)
    return {
        "kind": "R03CapturedGenericOwnerHostContractV1",
        "result": "PassedHostStructuralContextAndBodies_NotUnityOrNative",
        "methodsSha256": record["methodsSha256"],
        "physicalOwner": record["ownerAssembly"],
        "capturedArgumentAssembly": record["capturedArgumentAssembly"],
        "prePositiveCalls": record["callCountAfterDelegate"],
        "sourceGuardAnchorsVerified": True,
        "actualIl2cppMethodContextObserved": False,
        "actualNativeCapturedFailure15": False,
        "runtimeAcceptance": False, "R03Accepted": False, "H2Passed": False,
        "ReadyForHumanReviewGate": False,
    }


def read_regular(path: Path):
    need(path.is_file() and not path.is_symlink(), "Real regular host/source input required")
    return path.read_bytes()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for item in ("receipt", "methods", "owner-source", "native-source"):
        parser.add_argument("--" + item, required=True, type=Path)
    args = parser.parse_args()
    try:
        result = verify(read_regular(args.receipt), read_regular(args.methods),
                        read_regular(args.owner_source), read_regular(args.native_source))
        print(json.dumps(result, sort_keys=True))
        return 0
    except (HostRejected, ValueError, OSError, UnicodeError) as error:
        print("R03_CAPTURED_HOST_REJECTED: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
