#!/usr/bin/env python3
"""Strict, read-only validator for a real R03 native B1 Player-origin receipt.

This is NOT a V2 transport validator. It requires a separately authenticated
original V1 recovery reason, real Player PID, request identity and fresh file.
Never infer acceptance from a plausible standalone JSON record.
"""
from __future__ import annotations
import json
from pathlib import Path

FIELDS = {
    "schemaVersion", "kind", "transport", "runId", "caseId",
    "fixtureSha256", "processId", "state", "code", "origin",
    "reasonLength", "expectedCode", "expectedOrigin", "matchExpected",
    "reason", "nativeV2TransportImplemented", "firstRecoveryAuthenticatedV2",
    "wholeVmEpoch", "runtimeAcceptance", "R03Accepted", "H2Passed"
}
EXPECT = {
    "initializer-control": (0, 0, 0),
    "initializer-failure": (2, 19, 2),
    "captured-generic": (2, 15, 1),
}
class B1ValidationError(ValueError):
    pass

def need(ok, message):
    if not ok:
        raise B1ValidationError(message)

def strict_pairs(pairs):
    output = {}
    for key, value in pairs:
        need(key not in output, "Duplicate JSON key: " + key)
        output[key] = value
    return output

def decode(raw: bytes) -> dict:
    need(type(raw) is bytes and 0 < len(raw) <= 32768,
         "Exact bounded native B1 file bytes required")
    try:
        value = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=strict_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(
                               B1ValidationError("Non-finite JSON number")))
    except (UnicodeError, json.JSONDecodeError) as err:
        raise B1ValidationError("Malformed UTF-8/JSON B1 file") from err
    need(type(value) is dict, "Single object required")
    return value

def verify_record(record: dict, request: dict, mode: str, expected_pid: int,
                  v1_reason: str | None) -> dict:
    need(mode in EXPECT, "Unknown Player mode")
    state, code, origin = EXPECT[mode]
    need(type(record) is dict and set(record) == FIELDS, "Complete exact B1 schema required")
    need(type(request) is dict and
         all(type(request.get(k)) is str and request[k] for k in (
             "runId", "caseId", "dllSha256")), "Authentic request required")
    need(type(expected_pid) is int and expected_pid > 1, "Real positive PID required")
    need(record["schemaVersion"] == 1 and type(record["schemaVersion"]) is int and
         record["kind"] == "R03NativeFirstErrorB1Player" and
         record["transport"] == "PreopenedNativeB1NotV2",
         "Test-only B1 source identity required")
    for key, val in (("runId", request["runId"]), ("caseId", request["caseId"]),
                     ("fixtureSha256", request["dllSha256"]),
                     ("processId", expected_pid), ("state", state),
                     ("code", code), ("origin", origin),
                     ("expectedCode", code), ("expectedOrigin", origin)):
        need(type(record.get(key)) is type(val) and record[key] == val,
             "B1 source/VM identity mismatch: " + key)
    need(record["matchExpected"] is True, "Native B1 did not match expected origin")
    need(record["wholeVmEpoch"] == "NotProven" and
         all(record.get(k) is False for k in (
            "nativeV2TransportImplemented", "firstRecoveryAuthenticatedV2",
            "runtimeAcceptance", "R03Accepted", "H2Passed")),
         "B1 must not claim V2 or acceptance")
    reason = record.get("reason")
    bytes_count = record.get("reasonLength")
    need(type(bytes_count) is int and 0 <= bytes_count <= 4096,
         "Exact bounded reason length required")
    if mode == "initializer-control":
        need(reason is None and bytes_count == 0 and v1_reason in (None, ""),
             "Healthy control must not fabricate first terminal failure")
    else:
        need(type(reason) is str and reason != "" and
             bytes_count == len(reason.encode("utf-8")) and "\0" not in reason,
             "Exact nontruncated UTF-8 first reason required")
        need(type(v1_reason) is str and v1_reason == reason,
             "Native B1 source must equal authenticated V1 FIRST reason")
        if mode == "initializer-failure":
            need(reason.endswith("R03IR.InitializerFailure.AfterPublication.V1"),
                 "Original first initializer sentinel lost")
        else:
            need(reason.startswith("ShadowCapturedBaselineType") and
                 "CapturedArgumentAssembly=Methods" in reason and
                 "Context=method_inst" in reason and "TypePath=/arg[0]" in reason,
                 "Physical captured-generic owner/path lost")
    return {
        "kind": "R03NativeFirstErrorB1ReadOnlyCrosscheck",
        "result": "PassedExactB1OriginVsV1_NotV2OrRuntimeAcceptance",
        "mode": mode, "firstCode": code, "firstOrigin": origin,
        "firstReasonBytes": bytes_count, "processId": expected_pid,
        "nativeV2TransportImplemented": False, "runtimeAcceptance": False,
    }

def inspect(path: Path, request: dict, mode: str, expected_pid: int,
            v1_reason: str | None) -> dict:
    path = Path(path)
    need(path.is_file() and not path.is_symlink(), "B1 file absent or symlinked")
    return verify_record(decode(path.read_bytes()), request, mode, expected_pid, v1_reason)
