#!/usr/bin/env python3
"""Source-bound, non-authorizing native VM recovery detail observation.

The VM itself captured the initializer exception before Commit returned 19.
This parses the *unmodified* AssemblyShadow::GetRecoveryInfoJson output,
written once via a preopened native file, with independent request/PID joins.
Never promote this detail to a V1, V2, or runtime acceptance result.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

MAX_BYTES = 20000
KIN = "R03IRNativeInitializerRecoveryV1"
HEX = re.compile(r"[0-9a-f]{64}\Z")
IDENT = re.compile(r"[A-Za-z0-9_.-]{1,95}\Z")
EXPECTED = frozenset(("schemaVersion", "kind", "runId", "caseId", "stimulus",
                      "fixtureSha256", "processId", "nativeReturn",
                      "nativeRecovery", "runtimeAcceptance", "R03Accepted",
                      "H2Passed"))
CORE = frozenset(("schemaVersion", "enabled", "capabilityVersion", "stateCode",
                  "state", "published", "abortAllowed", "dispositionCode",
                  "disposition", "terminalFailureCode", "reason", "retainedBytes",
                  "baselineEligibilityRequiresStartupValidation"))


class RecoveryRejected(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise RecoveryRejected(reason)


def unique(rows):
    obj = {}
    for key, val in rows:
        need(key not in obj, "Duplicate native recovery key: " + key)
        obj[key] = val
    return obj


def no_constant(value):
    raise RecoveryRejected("Nonfinite native recovery value: " + value)


def inspect(path, request, launch_pid, fixture_sha256):
    path = Path(path)
    need(path.is_file() and not path.is_symlink(), "Missing actual native recovery file")
    raw = path.read_bytes()
    need(0 < len(raw) <= MAX_BYTES and raw.endswith(b"\n") and
         raw.count(b"\n") == 1, "Bounded complete native recovery file required")
    try:
        value = json.loads(raw.decode("utf-8", "strict"),
                           object_pairs_hook=unique, parse_constant=no_constant)
    except (UnicodeError, ValueError) as error:
        raise RecoveryRejected("Invalid native recovery JSON") from error
    need(type(value) is dict and set(value) == EXPECTED and
         value["kind"] == KIN and type(value["schemaVersion"]) is int and
         value["schemaVersion"] == 1 and
         value["runId"] == request.get("runId") and
         value["caseId"] == request.get("caseId") and
         value["stimulus"] == request.get("stimulus") and
         type(value["processId"]) is int and
         value["processId"] == launch_pid and type(launch_pid) is int and
         launch_pid > 0 and type(fixture_sha256) is str and
         HEX.fullmatch(fixture_sha256) is not None and
         value["fixtureSha256"] == request.get("dllSha256") == fixture_sha256 and
         type(value["nativeReturn"]) is int and
         value["nativeReturn"] == 0 and
         all(value[key] is False for key in
             ("runtimeAcceptance", "R03Accepted", "H2Passed")),
         "Native recovery provenance, exact source and false acceptance required")
    got = value["nativeRecovery"]
    need(type(got) is dict and set(got) == CORE and
         type(got["schemaVersion"]) is int and got["schemaVersion"] == 1 and
         got["enabled"] is True and
         type(got["capabilityVersion"]) is int and got["capabilityVersion"] == 1 and
         type(got["stateCode"]) is int and got["stateCode"] in (6, 9) and
         type(got["state"]) is str and
         got["published"] is True and
         type(got["abortAllowed"]) is bool and
         type(got["dispositionCode"]) is int and
         type(got["disposition"]) is str and
         type(got["terminalFailureCode"]) is int and
         type(got["reason"]) is str and len(got["reason"]) <= 4096 and
         type(got["retainedBytes"]) is int and got["retainedBytes"] >= 0 and
         type(got["baselineEligibilityRequiresStartupValidation"]) is bool,
         "Exact existing native VM recovery schema and type identity")
    if got["stateCode"] == 9:
        need(got["disposition"] == "RestartRequired" and
             got["terminalFailureCode"] != 0 and
             bool(got["reason"]),
             "Terminal state must contain a real native reason")
    else:
        need(got["terminalFailureCode"] == 0,
             "Committed state cannot claim an initializer terminal failure")
    return {
        "kind": "R03IRInitializerRecoverySourceOnlyDiagnosticV1",
        "result": "ParsedNativeVMFirstFailure_NotRuntimeAuthenticated",
        "rawSha256": hashlib.sha256(raw).hexdigest(),
        "rawBytes": len(raw),
        "nativeGetterResult": value["nativeReturn"],
        "stateCode": got["stateCode"],
        "terminalFailureCode": got["terminalFailureCode"],
        "vmReason": got["reason"],
        "disposition": got["disposition"],
        "runtimeAcceptance": False, "R03Accepted": False, "H2Passed": False,
        "completeDiagnosticsAuthenticated": False,
        "nativeV2TransportImplemented": False,
    }
