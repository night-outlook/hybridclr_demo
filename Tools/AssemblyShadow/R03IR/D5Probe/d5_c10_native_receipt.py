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
REQUIRED = tuple(range(1, 11))  # v2: slot 4 native guard entry; slot 5 method result
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


def parse_material(raw: bytes, *, externally_observed_pid: int | None = None,
                   externally_observed_exit_code: int | None = None) -> dict:
    """Fail closed without an independently supplied process PID and exit.

    This parser does not verify the external source of those arguments.
    Synthetic host tests explicitly label their fabricated process joins.
    A real Local validator must supply process-monitor evidence bound to the
    actual binary and argv, not merely copy the PID from this raw file.
    """
    need(len(raw) == RECEIPT_BYTES,
         "Truncated/overlong native evidence cannot be an observation")
    magic, version, pid, run_raw, request_raw, fixture_raw, reserved = HEADER.unpack_from(raw)
    need(magic == b"D5C10E1!" and version == 2 and pid > 0 and reserved == 0,
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
    decision = target[0] if target else 0  # native same-TLS method result
    method = ("AllowedGuard" if decision == 1 else
              "DeniedGuard" if decision == 2 else
              "RacedP6" if decision == 3 else "NotAttempted")

    # C10 wire schema v2 (still 4,652 bytes):
    # slot 4 (1,1,nativeStateBeforeTerminalPolicy,nativeFirstErrorAtEntry)
    # slot 5 (sameTLSGuardDecision,1,1,0)
    # slot 6 (-1,postCollectorState,observedNativeReleaseP5,armedCount)
    # Native ReleaseP5 is NOT a managed Join/completion fact. A terminal-denied
    # method need not return to managed code; native guard entry+result are enough
    # for a source-only candidate when the *entry* was healthy.
    entry = observed.get(4)
    entry_state = entry[2] if entry else None
    entry_first_error = entry[3] if entry else None
    guard_entry_precondition = (
        "HealthyP5CommittingFirstErrorEmpty" if
            entry_state == 5 and entry_first_error == 0 else
        "PreexistingTerminalOrFirstError" if
            entry_state in (8, 9) or entry_first_error in (1, 2, 3) else
        "MissingOrUnexpectedGuardEntry")
    release_value = observed[6][2] if 6 in observed else None
    release_observed = (release_value == 1) if release_value in (0, 1) else None

    required = all(slot in observed for slot in REQUIRED)
    joined = (required and observed[1][0] == 1 and
              observed[2][0] == 2 and observed[2][1] == 1 and
              observed[3][0] == 0 and observed[3][2] == 1 and
              observed[4][0] == 1 and observed[4][1] == 1 and
              guard_entry_precondition == "HealthyP5CommittingFirstErrorEmpty" and
              observed[5][1] == 1 and observed[5][2] == 1 and
              observed[6][0] == -1 and release_observed is not None and
              observed[6][3] == 1 and observed[7][0] == 1 and
              observed[8][0] == 1 and observed[8][2] == 0 and
              observed[10][0] == 1 and observed[10][1] == 1 and
              observed[10][2] == decision and observed[10][3] == 1 and
              bound == 1 and before == 0)
    process_joined = (type(externally_observed_pid) is int and
                      externally_observed_pid == pid and
                      type(externally_observed_exit_code) is int and
                      externally_observed_exit_code in (20, 42))
    permitted_guard = (joined and decision in (1, 2) and
                       guard[1] + guard[2] == 1 and guard[3] == 0 and
                       (decision != 1 or (guard[1] == 1 and release_observed)) and
                       (decision != 2 or guard[2] == 1))
    if permitted_guard and process_joined and (
            (decision == 1 and externally_observed_exit_code == 42) or
            (decision == 2 and body == "BodyExecuted" and
             externally_observed_exit_code == 20)):
        result = "UnsafeEarlyMethodAdmissionObserved_SourceMaterial"
    elif (permitted_guard and process_joined and
          externally_observed_exit_code == 20 and decision == 2 and
          observed[6][1] == 9 and status == 2 and
          body == "BodyNotExecuted"):
        result = "CandidateObservedDeniedInP5_RequiresIndependentBinaryProof"
    else:
        result = "NoCoverage"
    return {
        "schema": "R03D5C10NativeReceiptInspectionV2",
        "result": result,
        "processIdAsClaimed": pid,
        "runIdAsClaimed": run,
        "requestSha256AsClaimed": request,
        "fixtureSha256AsClaimed": fixture,
        "externallyObservedPidAsSupplied": externally_observed_pid,
        "externallyObservedExitCodeAsSupplied": externally_observed_exit_code,
        "externalProcessJoinMatched": process_joined,
        "externalProcessProvenanceIndependentlyVerified": False,
        "eventSlots": sorted(observed),
        "methodGuard": method,
        "guardEntryState": entry_state,
        "guardEntryFirstFailureStatus": entry_first_error,
        "guardEntryPrecondition": guard_entry_precondition,
        "nativeWorkerP5ReleaseObserved": release_observed,
        "managedWorkerCompletion": "Unknown_NotJoined",
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
        "schema": "R03D5C10NativeReceiptInspectionV2",
        "result": "SourceHostOnly_NoRealPlayerEvidence",
        "receiptBytes": RECEIPT_BYTES,
        "actualLinkedBinaryAndPidAuthenticated": False,
        "realPlayerC10Passed": False,
        "D5BLocalExecution": "NotAuthorized",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(preview(), sort_keys=True))
