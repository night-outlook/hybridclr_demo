#!/usr/bin/env python3
"""Strict non-authorizing A2 real-native probe V1 receipt consumer.

The producer MUST be an independently source-verified linked Unity Player
with independently authenticated method-owner/fixture/build/PID authority.
Parsing host mock bytes alone cannot prove IL2CPP native error15.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

SCHEMA = 1
KIND = "R03IRCapturedGenericPhysicalNativeV1"
RECOVERY = frozenset((
    "schemaVersion", "enabled", "capabilityVersion", "stateCode", "state",
    "published", "abortAllowed", "dispositionCode", "disposition",
    "terminalFailureCode", "reason", "retainedBytes",
    "baselineEligibilityRequiresStartupValidation",
))
FIELDS = frozenset((
    "schemaVersion", "kind", "result", "processId", "runId", "caseId",
    "fixtureSha256", "ownerAssembly", "capturedArgumentAssembly",
    "capturedType", "physicalTypeIndex", "methodInflated",
    "methodContextPhysical", "ownerIndependentAot", "guardAllowed",
    "beforeState", "afterState", "beforeCount", "afterCount",
    "runtimeInvokeAttempted", "runtimeInvokeSucceeded", "runtimeInvokeThrew",
    "nativeRecovery", "runtimeAcceptance", "R03Accepted", "H2Passed",
))
SHA = re.compile(r"[0-9a-f]{64}\Z")
RUN = re.compile(r"[0-9a-fA-F]{24,64}\Z")
CASE = "IR-R03-02-captured-generic"
SENTINEL = "ShadowCapturedBaselineType"


class NativeReceiptRejected(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise NativeReceiptRejected(reason)


def strict_load(raw: bytes):
    need(type(raw) is bytes and 0 < len(raw) <= 16384 and
         raw.endswith(b"\n") and raw.count(b"\n") == 1 and b"\r" not in raw,
         "Complete bounded single physical native receipt")
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            need(key not in obj, "Duplicate native receipt key: " + key)
            obj[key] = value
        return obj
    try:
        return json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=unique,
                          parse_constant=lambda val: (_ for _ in ()).throw(
                              NativeReceiptRejected("Nonfinite JSON: " + val)))
    except (ValueError, UnicodeError) as err:
        raise NativeReceiptRejected("Invalid UTF8/native JSON") from err


def exact_int(value, expected):
    return type(value) is int and value == expected


def exact_bool(value, expected):
    return type(value) is bool and value is expected


def verify(raw_bytes: bytes, request: dict, *, expected_pid: int,
           expected_owner: str, expected_fixture_sha256: str):
    """Validate schema and external request/PID/digest *without* runtime promotion."""
    raw = strict_load(raw_bytes)
    need(type(raw) is dict and set(raw) == FIELDS and
         exact_int(raw.get("schemaVersion"), SCHEMA) and
         raw["kind"] == KIND and raw["result"] == "ObservedNotAccepted",
         "Exact physical native V1 identity/schema")
    need(type(request) is dict and type(request.get("runId")) is str and
         RUN.fullmatch(request["runId"]) is not None and
         request.get("caseId") == CASE and request.get("stimulus") == "captured-generic" and
         request.get("dllSha256") == expected_fixture_sha256 and
         type(expected_fixture_sha256) is str and SHA.fullmatch(expected_fixture_sha256) is not None and
         type(expected_owner) is str and 1 <= len(expected_owner) <= 100 and
         exact_int(raw.get("processId"), expected_pid) and expected_pid > 0 and
         raw.get("runId") == request["runId"] and
         raw.get("caseId") == request["caseId"] and
         raw.get("fixtureSha256") == expected_fixture_sha256 and
         raw.get("ownerAssembly") == expected_owner and
         raw.get("capturedArgumentAssembly") == "Methods" and
         raw.get("capturedType") == "R03.Node",
         "Independently bound physical source, mode, owner, fixture and actual OS PID")
    need(exact_int(raw.get("beforeState"), 6) and
         exact_int(raw.get("afterState"), 9) and
         exact_int(raw.get("beforeCount"), 1) and
         exact_int(raw.get("afterCount"), 1) and
         exact_int(raw.get("guardAllowed"), 0) and
         type(raw.get("physicalTypeIndex")) is int and
         raw["physicalTypeIndex"] >= 0 and
         exact_bool(raw.get("methodInflated"), True) and
         exact_bool(raw.get("methodContextPhysical"), True) and
         exact_bool(raw.get("ownerIndependentAot"), True) and
         exact_bool(raw.get("runtimeInvokeAttempted"), True) and
         exact_bool(raw.get("runtimeInvokeSucceeded"), False) and
         type(raw.get("runtimeInvokeThrew")) is bool and
         all(exact_bool(raw.get(k), False) for k in
             ("runtimeAcceptance", "R03Accepted", "H2Passed")),
         "Actual contained generic method guard and postterminal no-side-effects contract")
    recover = raw.get("nativeRecovery")
    need(type(recover) is dict and set(recover) == RECOVERY and
         exact_int(recover.get("schemaVersion"), 1) and
         exact_int(recover.get("capabilityVersion"), 1) and
         exact_bool(recover.get("enabled"), True) and
         exact_int(recover.get("stateCode"), 9) and
         recover.get("state") == "FailedAfterCommit" and
         exact_bool(recover.get("published"), True) and
         exact_bool(recover.get("abortAllowed"), False) and
         recover.get("disposition") == "RestartRequired" and
         exact_int(recover.get("terminalFailureCode"), 15) and
         type(recover.get("dispositionCode")) is int and
         type(recover.get("retainedBytes")) is int and recover["retainedBytes"] >= 0 and
         type(recover.get("baselineEligibilityRequiresStartupValidation")) is bool,
         "Unmodified actual VM recovery state/error15 structural schema")
    reason = recover.get("reason")
    need(type(reason) is str and 0 < len(reason) <= 4096 and
         SENTINEL in reason and "CapturedArgumentAssembly=Methods" in reason and
         "Reason=CapturedBaselineType" in reason and
         "/arg[0]" in reason,
         "Actual captured physical type, not fabricated 13/21 failure reason")
    return {
        "schemaVersion": 1, "kind": "R03CapturedGenericNativeSourceConsumerV1",
        "result": "SchemaConsistentNotRuntimeAuthenticated",
        "capturedNativeError15Field": 15, "ownerAssembly": expected_owner,
        "processId": expected_pid,
        "runtimeAcceptance": False, "R03Accepted": False,
        "H2Passed": False, "firstRecoveryAuthenticatedV2": False,
        "nativeVMProofIndependent": False,
    }


def inspect(path: Path, request: dict, *, expected_pid: int,
            expected_owner: str, expected_fixture_sha256: str):
    path = Path(path)
    need(path.is_file() and not path.is_symlink(), "Real native output regular file")
    return verify(path.read_bytes(), request, expected_pid=expected_pid,
                  expected_owner=expected_owner,
                  expected_fixture_sha256=expected_fixture_sha256)
