#!/usr/bin/env python3
"""Strict non-authorizing parser of the native preopened initializer trace V1.

The trace can diagnose a failed Player even with empty raw.json. It NEVER
replaces the strict native observation V1, source/build/PID provenance, or
native terminal V2 evidence.
"""
import json
from pathlib import Path
import re

KIND = "R03IRInitializerNativeTraceV1"
KEYS = frozenset(("kind", "runId", "caseId", "stimulus", "fixtureSha256",
                  "pid", "seq", "phase", "a", "b", "c", "d",
                  "runtimeAcceptance", "R03Accepted", "H2Passed"))
NONCE = re.compile(r"[A-Za-z0-9_.-]{24,95}\Z")
CASE = re.compile(r"[A-Za-z0-9_.-]{1,95}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
PHASES = frozenset((
    100, 101, 102, 110, 111, 120, 121, 130, 131, 140, 141,
    150, 151, 160, 161, 190, 191, 200, 201, 205, 210, 211,
    220, 299, 300, 301, 302, 400, 401, 600, 601, 602, 603,
    610, 620, 900, 901,
))
MAX_BYTES = 65536
MAX_EVENTS = 128


class TraceRejected(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise TraceRejected(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "Duplicate native trace JSON key")
        result[key] = value
    return result


def disallow_constant(value):
    raise TraceRejected("Non-finite native trace value: " + value)


def parse(raw, request, pid, expected_sha256):
    """Pure strict parser. Identity comes from an external request/process."""
    need(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES and
         raw.endswith(b"\n") and b"\r" not in raw, "Bounded complete native trace")
    need(type(request) is dict and type(pid) is int and pid > 0 and
         type(expected_sha256) is str and DIGEST.fullmatch(expected_sha256),
         "External request/PID/digest authority required")
    need(type(request.get("runId")) is str and NONCE.fullmatch(request["runId"]) and
         type(request.get("caseId")) is str and CASE.fullmatch(request["caseId"]) and
         request.get("stimulus") in ("initializer-control", "initializer-failure") and
         request.get("dllSha256") == expected_sha256,
         "Exact initializer request and fixture identity")
    records = []
    lines = raw.splitlines(keepends=True)
    need(1 <= len(lines) <= MAX_EVENTS, "Bounded native trace events")
    for number, line in enumerate(lines, 1):
        need(line.endswith(b"\n") and line.count(b"\n") == 1 and len(line) <= 512,
             "Complete single native journal event")
        try:
            event = json.loads(line[:-1].decode("utf-8", "strict"),
                               object_pairs_hook=unique,
                               parse_constant=disallow_constant)
        except (ValueError, UnicodeError) as error:
            raise TraceRejected("Invalid native trace JSON") from error
        need(type(event) is dict and set(event) == KEYS and
             event["kind"] == KIND and
             event["runId"] == request["runId"] and
             event["caseId"] == request["caseId"] and
             event["stimulus"] == request["stimulus"] and
             event["fixtureSha256"] == expected_sha256 and
             type(event["pid"]) is int and event["pid"] == pid and
             type(event["seq"]) is int and event["seq"] == number and
             type(event["phase"]) is int and event["phase"] in PHASES and
             all(type(event[k]) is int for k in ("a", "b", "c", "d")) and
             all(event[k] is False for k in ("runtimeAcceptance", "R03Accepted", "H2Passed")),
             "Native trace identity, types, sequence, phases and non-acceptance")
        records.append(event)
    need(records[0]["phase"] == 100 and records[0]["a"] == 1,
         "Native journal must start at actual preopened writer")
    return records


def summarize(records, *, require_complete=False):
    """Trace diagnostic only; never a native observation PASS verdict."""
    need(type(records) is list and records, "Parsed native trace required")
    steps = {phase: [row for row in records if row["phase"] == phase]
             for phase in PHASES}
    failed_observer = [event["a"] for event in steps[300] if event["a"] < 0]
    seals = [event for event in steps[610]]
    managed_failures = [event for event in steps[900]]
    summary = {
        "kind": "R03InitializerTraceHostInterpretationV1",
        "result": "BoundedTraceObserved_NotRuntimeAuthenticated",
        "events": len(records),
        "lastPhase": records[-1]["phase"],
        "preopenedWriter": True,
        "nativeCallbackObserved": bool(steps[299]),
        "nativeCallbackFailures": failed_observer,
        "nativeReadFailures": [e["a"] for e in steps[400] if e["a"] < 0],
        "nativeSealFailures": [{"return": e["a"], "reason": e["b"]} for e in seals],
        "managedCaughtPhase": [e["a"] for e in managed_failures],
        "commitStatusReported": [e["a"] for e in steps[191]],
        "nativeSealInput": [{"commit": e["a"], "state": e["b"],
                              "attempted": e["c"], "succeeded": e["d"]}
                             for e in steps[600]],
        "completeStrictObservationProven": False,
        "nativeV2TransportImplemented": False,
        "runtimeAcceptance": False, "R03Accepted": False, "H2Passed": False,
    }
    if require_complete:
        need(all(steps[k] for k in (100, 101, 190, 191, 201, 205,
                                    299, 300, 400, 401, 600, 601,
                                    602, 603, 620)) and
             not steps[610] and not steps[900] and
             len(steps[300]) == 1 and steps[300][0]["a"] == 1 and
             len(steps[400]) == 1 and steps[400][0]["a"] == 1 and
             len(steps[620]) == 1 and steps[620][0]["a"] == 1,
             "Native successful trace must have real callback/field/seal phases")
        summary["result"] = "CompletePhaseTrace_NotRuntimeAuthenticated"
    return summary


def inspect(path, request, pid, sha256, *, require_complete=False):
    """Fail closed on partial, forged, extra, or identity-mismatched raw bytes."""
    path = Path(path)
    need(path.is_file() and not path.is_symlink(),
         "Actual native trace must be a regular file")
    raw = path.read_bytes()
    steps = parse(raw, request, pid, sha256)
    report = summarize(steps, require_complete=require_complete)
    import hashlib
    report["rawSha256"] = hashlib.sha256(raw).hexdigest()
    report["rawBytes"] = len(raw)
    return report
