#!/usr/bin/env python3
"""Read D5 C10 *untrusted* fixed native receipt materials.

This is a source-host schema validator, NOT an attestation of a live Unity,
Bee, GameAssembly, PID or actual method body. No CLI promotes input to Player
acceptance. A future independent Local reviewer must join this raw file to
source/linked binary, process/argv and native first-error custody.
"""
from __future__ import annotations
import re
import struct

MAGIC = 0xC105D5E1
HEADER = struct.Struct("<8sii64s64s64si")
EVENT = struct.Struct("<IiiiiiII")
FIRST_ERROR = struct.Struct("<Iiiii4097s3x")
RECEIPT_BYTES = HEADER.size + EVENT.size * 10 + FIRST_ERROR.size
assert HEADER.size == 212 and EVENT.size == 32 and FIRST_ERROR.size == 4120
REQUIRED = tuple(range(1, 11))  # slot 5: native same-worker guard completion
HEX = re.compile("^[0-9a-f]{64}$")
IDENT = re.compile("^[A-Za-z0-9_-]{1,63}$")


class InvalidReceipt(ValueError):
    pass


def need(condition: bool, reason: str) -> None:
    if not condition:
        raise InvalidReceipt(reason)


def extract_text(raw: bytes) -> str:
    end = raw.find(b"\0")
    if end < 0:
        end = len(raw)
    need(raw[end:] == b"\0" * (len(raw) - end), "Invalid field padding")
    return raw[:end].decode("ascii", errors="strict")


def parse_material(raw: bytes) -> dict:
    need(len(raw) == RECEIPT_BYTES,
         "Truncated/overlong native evidence cannot be an observation")
    magic, version, pid, run_raw, request_raw, fixture_raw, reserved = HEADER.unpack_from(raw)
    need(magic == b"D5C10E1!" and version == 1 and pid > 0 and reserved == 0,
         "Invalid native evidence header")
    run = extract_text(run_raw)
    request = request_raw.decode("ascii", errors="strict")
    fixture = fixture_raw.decode("ascii", errors="strict")
    need(bool(IDENT.fullmatch(run)) and HEX.fullmatch(request) and
         HEX.fullmatch(fixture), "Invalid receipt identity")
    observed = {}
    for slot in range(1, 11):
        start = HEADER.size + (slot - 1) * EVENT.size
        cell = raw[start:start+EVENT.size]
        if not any(cell):
            continue
        marker, actual_slot, a, b, c, d, check, size = EVENT.unpack(cell)
        need(marker == MAGIC and actual_slot == slot and size == 32 and
             check == (MAGIC ^ slot ^ (a & 0xffffffff) ^
                       (b & 0xffffffff) ^ (c & 0xffffffff) ^ (d & 0xffffffff)),
             "Corrupt/noncanonical native event slot")
        observed[slot] = (a, b, c, d)
    at = HEADER.size + 10 * EVENT.size
    first_magic, status, error_code, origin, length, reason = FIRST_ERROR.unpack_from(raw, at)
    need(first_magic == MAGIC and status in (0, 1, 2, 3),
         "First-error header/state missing")
    if status == 2:
        need(error_code > 0 and 1 <= origin <= 6 and 0 < length <= 4096 and
             reason[length:] == b"\0" * (4097 - length),
             "Frozen first-error corrupted")
        first_reason = reason[:length].decode("utf-8", errors="strict")
    else:
        need(error_code == 0 and origin == 0 and length == 0 and
             reason == b"\0" * 4097,
             "Unfrozen first-error claimed data")
        first_reason = None
    canary = observed.get(9)
    before, after, bound = (canary[0], canary[1], canary[2]) if canary else (-1, -1, 0)
    body = ("BodyExecuted" if bound == 1 and before == 0 and after != 0 else
            "BodyNotExecuted" if bound == 1 and before == 0 and after == 0 else "Unknown")
    guard = observed.get(7)
    target = observed.get(5)
    decision = target[0] if target else 0  # native single TLS worker token
    method = ("AllowedGuard" if decision == 1 else
              "DeniedGuard" if decision == 2 else
              "RacedP6" if decision == 3 else "NotAttempted")
    required = all(slot in observed for slot in REQUIRED)
    # Every slot has a concrete producer: 1=healthy arm, 2=P5 native,
    # 3=native pinned instance, 4=native TLS attempt, 5=native method
    # guard completion, 6=native collector state, 7=guard counters,
    # 8=window, 9=pinned raw field after, 10=native fsynced seal.
    # Slot 5 is never inferred from a managed exception or an unrelated Keep.
    joined = (required and observed[1][0] == 1 and
              observed[2][0] == 2 and observed[2][1] == 1 and
              observed[3][0] == 0 and observed[3][2] == 1 and
              observed[4][0] == 1 and observed[4][1] == 1 and
              observed[5][1] == 1 and observed[5][2] == 1 and
              observed[6][0] == -1 and observed[6][2] == 1 and
              observed[6][3] == 1 and observed[7][0] == 1 and
              observed[8][0] == 1 and observed[8][2] == 0 and
              observed[10][0] == 1 and observed[10][1] == 1 and
              observed[10][2] == decision and observed[10][3] == 1 and
              bound == 1 and before == 0)
    permitted_guard = (joined and decision in (1, 2) and
                       guard[1] + guard[2] == 1 and guard[3] == 0 and
                       (decision != 1 or guard[1] == 1) and
                       (decision != 2 or guard[2] == 1))
    if permitted_guard and (body == "BodyExecuted" or decision == 1):
        result = "UnsafeEarlyMethodAdmissionObserved_SourceMaterial"
    elif (permitted_guard and decision == 2 and
          observed[6][1] == 9 and status == 2 and
          body == "BodyNotExecuted"):
        result = "CandidateObservedDeniedInP5_RequiresIndependentBinaryProof"
    else:
        result = "NoCoverage"
    return {
        "schema": "R03D5C10NativeReceiptInspectionV1",
        "result": result,
        "processIdAsClaimed": pid,
        "runIdAsClaimed": run,
        "requestSha256AsClaimed": request,
        "fixtureSha256AsClaimed": fixture,
        "eventSlots": sorted(observed),
        "methodGuard": method,
        "methodBodySideEffect": body,
        "firstErrorStatus": status,
        "firstErrorCode": error_code,
        "firstErrorOrigin": origin,
        "firstErrorReason": first_reason,
        "actualLinkedBinaryAndPidAuthenticated": False,
        "realPlayerC10Passed": False,
        "R03Accepted": False,
        "D5BLocalExecution": "NotAuthorized",
        "WEB_TO_LOCAL": "CLOSED_NO_LOCAL_EXECUTION",
    }


def preview() -> dict:
    return {
        "schema": "R03D5C10NativeReceiptInspectionV1",
        "result": "SourceHostOnly_NoRealPlayerEvidence",
        "receiptBytes": RECEIPT_BYTES,
        "actualLinkedBinaryAndPidAuthenticated": False,
        "realPlayerC10Passed": False,
        "D5BLocalExecution": "NotAuthorized",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(preview(), sort_keys=True))
