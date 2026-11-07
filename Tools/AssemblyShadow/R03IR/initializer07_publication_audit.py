#!/usr/bin/env python3
"""Read-only oneuse-07 published-record cross-check; NOT R03 acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from verify_initializer_observation import strict_load, verify as verify_v1
from verify_initializer_trace import parse as parse_trace, summarize as summarize_trace

CHECKPOINT = (Path(__file__).resolve().parents[3] /
              "Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261107-oneuse-07")
PINS = {
    "hybridclr_demo": "6e1dc7b4349a386dc35c5ed46fca4225db273b18",
    "hybridclr": "4b2774b066cfc6afd77a8c8aded6bda7ea574f55",
    "hybridclr_unity": "948c0e3b4f8891481301770115e8ba4945eea6de",
    "il2cpp_plus": "41764ae1eeefb33b05966e7f7676e52aae39c340",
}
SHA_BUILD = "553af2f5cd35a08da543e2b6b2d68ac89a5a7e98d63b7fb840ce2e64dfd60a05"
SHA_BRIDGE = "c6bbea6e179964b7296bff02ee4f434b188e8578a4e7086da1c283e79b82f3da"
MODES = {
    "initializer-control": ("d6e5b66f695498a9ba0806ea81930f03804d98f77382cb851d24c2b24f24202e", 0, 6, 35820, "0018"),
    "initializer-failure": ("6ad097153da2054579c13ec48d9f81a35d2551b08bf7a77398f13809ef9e5370", 19, 9, 35842, "0019"),
}
CELLS = {
    "entry-authority", "initializer-host-contracts", "original-s-archive",
    "original-s-process-joins", "audit_s_generated_material", "audit_s_binary_linkage",
    "real-dll-fixtures", "ir-generator-build", "initializer-native-targets",
    "prepare-release", "prepare-initializer", "build-initializer",
    "player-initializer-control", "player-initializer-failure", "final-authority",
}
SENTINEL = "R03IR.InitializerFailure.AfterPublication.V1"


class AuditRejected(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise AuditRejected(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw):
    def unique(items):
        obj = {}
        for key, value in items:
            need(key not in obj, "Duplicate JSON key")
            obj[key] = value
        return obj
    return json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(AuditRejected("Non-finite JSON")))


def no_acceptance(obj):
    need(type(obj) is dict and all(obj.get(k) is False for k in
         ("runtimeAcceptance", "R03Accepted", "H2Passed")), "Acceptance flag drift")


def verify(root=CHECKPOINT, overrides=None):
    root = Path(root)
    need(root.is_absolute() and root.is_dir() and root.resolve(strict=True) == root
         and not root.is_symlink(), "Canonical published checkpoint directory")
    overrides = dict(overrides or {})

    def read(p):
        need(not Path(p).is_absolute() and ".." not in Path(p).parts, "Relative evidence only")
        if p in overrides:
            need(type(overrides[p]) is bytes, "Raw override bytes only")
            return overrides[p]
        f = root / p
        need(f.is_file() and not f.is_symlink() and f.resolve(strict=True) == f,
             "Missing/linked published file: " + p)
        return f.read_bytes()

    def load(p):
        return strict_json(read(p))

    local = load("LOCAL_RESULT.json")
    findings = load("local-evidence/RUNTIME_FINDINGS.json")
    independent = load("local-evidence/FINAL_INDEPENDENT_AUDIT.json")
    need(local.get("result") == "PASS" and local.get("sourcePins") == PINS and
         local.get("producerResult") == "FocusedInitializerEvidenceReadyForIndependentReview",
         "Pinned Local result")
    runner = local.get("runner", {})
    argv = runner.get("command", [])
    need(type(runner.get("runnerInvocations")) is int and
         runner["runnerInvocations"] == 1 and runner.get("retryPerformed") is False and
         runner.get("exitCode") == 0 and type(runner.get("exitCode")) is int and
         type(argv) is list and argv.count("--demo-commit") == 1 and
         argv[argv.index("--demo-commit") + 1] == PINS["hybridclr_demo"],
         "Single real committed Local invocation")
    cells = local.get("cellStates", {})
    need(type(cells) is dict and set(cells) == CELLS and
         all(v == "Passed" for v in cells.values()) and
         local.get("cellCounts") == {"Passed": 15} and
         independent.get("cellCounts") == local["cellCounts"] and
         independent.get("cellStates") == cells and
         independent.get("sourcePins") == PINS and
         independent.get("result") ==
             "PassedReceiptAndCustodyAudit_ProducerSemanticResultRetained" and
         independent.get("archiveMembers") == 456 and
         type(independent.get("archiveMembers")) is int, "15-cell scope and independent audit")
    no_acceptance(independent)
    need(findings.get("producerResult") == local["producerResult"] and
         findings.get("cells") == {"Passed": 15} and
         local.get("seal", {}).get("members") == 456 and
         local.get("hostCustody", {}).get("fileCount") == 3198 and
         local.get("hostCustody", {}).get("symlinkCount") == 4, "Host/product scope")
    build_bytes = read("batch/builds/candidate-release/build-receipt.json")
    build = strict_json(build_bytes)
    need(sha(build_bytes) == SHA_BUILD == local.get("build", {}).get("sha256") and
         findings.get("build", {}).get("sha256") == SHA_BUILD and
         build.get("result") == "Passed" and build.get("buildPipelineResult") == "Succeeded" and
         type(build.get("errors")) is int and build["errors"] == 0 and
         type(build.get("warnings")) is int and build["warnings"] == 1 and
         build.get("initializerBridgeSignature") == "Bi4" and
         build.get("initializerBridgeGeneratedSha256") == SHA_BRIDGE and
         build.get("initializerBridgePostBuildSha256") == SHA_BRIDGE and
         build.get("initializerBridgeLinkedRuntimeObserved") is False, "Published BuildReceipt")
    # BuildReceipt schema carries runtimeAcceptance only; R03/H2 fields
    # belong to Local result/Player records and must not be fabricated.
    need(build.get("runtimeAcceptance") is False,
         "Original BuildReceipt cannot claim runtime acceptance")
    need(type(local.get("players")) is list and len(local["players"]) == 2 and
         type(findings.get("players")) is list and len(findings["players"]) == 2,
         "Two original distinct Players")
    result_players = {}
    for mode, (fixture, commit, state, pid, command_id) in MODES.items():
        l = [x for x in local["players"] if x.get("case") == mode]
        fs = [x for x in findings["players"] if x.get("mode") == mode]
        need(len(l) == len(fs) == 1, "Unique mode-specific published result")
        row, f = l[0], fs[0]
        prefix = "batch/players/IR-R03-02-" + mode + "/"
        request_bytes = read(prefix + "request.json")
        request = strict_json(request_bytes)
        raw_bytes = read(prefix + "raw.json")
        raw = strict_load(raw_bytes)
        verification = load(prefix + "verification.json")
        need(type(pid) is int and row.get("commandPid") == pid == f.get("pid") and
             row.get("commandExit") == 0 and f.get("exit") == 0 and
             request.get("stimulus") == mode and request.get("dllSha256") == fixture and
             sha(request_bytes) == verification.get("requestSha256") and
             sha(raw_bytes) == row.get("rawSha256") == f.get("strictSha256") ==
                 verification.get("rawSha256") and
             verification.get("launchPid") == pid and
             verification.get("buildReceiptSha256") == SHA_BUILD and
             verification.get("result") == "PassedFocusedV1PlayerObservation_NotV2",
             "Pinned request/raw/fixture/PID/verification")
        no_acceptance(raw)
        no_acceptance(verification)
        need(verify_v1(raw, request, {"pid": pid}, fixture).get("result") ==
             "SchemaConsistentNotRuntimeAuthenticated", "Original strict V1 schema")
        trace_bytes = read(prefix + "raw.json.native-trace.jsonl")
        trace = parse_trace(trace_bytes, request, pid, fixture)
        summary = summarize_trace(trace, require_complete=True)
        need(summary.get("genuineLinkedBi4ProbeStatus") == [1] and
             sha(trace_bytes) == f.get("traceSha256"), "Bound native trace/linked Bi4")
        by_phase = {}
        for event in trace:
            by_phase.setdefault(event["phase"], []).append(event)
        phases = (103, 190, 299, 300, 191, 201, 601, 620)
        need(all(len(by_phase.get(p, [])) == 1 for p in phases) and
             [by_phase[p][0]["seq"] for p in phases] ==
                 sorted(by_phase[p][0]["seq"] for p in phases) and
             tuple(by_phase[300][0][k] for k in ("a", "b", "c", "d")) == (1, 3, 15, 1),
             "Pre-Commit native callback/field/mask phase order")
        recovery_bytes = read(prefix + "raw.json.vm-recovery.json")
        recovery = strict_json(recovery_bytes)
        native = recovery.get("nativeRecovery", {})
        need(sha(recovery_bytes) == f.get("recoverySha256") and
             recovery.get("processId") == pid and recovery.get("runId") == request.get("runId") and
             recovery.get("fixtureSha256") == fixture and
             raw.get("commitReturn") == f.get("commit") == commit and
             raw.get("finalState") == f.get("stateCode") == state and
             native.get("stateCode") == state and native.get("terminalFailureCode") == commit and
             (native.get("reason", "").endswith(SENTINEL) if commit == 19
              else native.get("reason") == "") and
             raw.get("postAotAttempted") is (commit == 19) and
             raw.get("postAotSucceeded") is False and
             by_phase[191][0]["a"] == commit and by_phase[201][0]["b"] == state,
             "Real native first recovery and bounded terminal status")
        command = load("batch/commands/" + command_id + "/command.json")
        args = command.get("command", [])
        need(command.get("pid") == pid and command.get("exitCode") == 0 and
             command.get("timeout") is False and
             command.get("remainingProcessGroup") is False and
             args == verification.get("argv") and args.count("-r03IrInitializerRunId") == 1 and
             args[args.index("-r03IrInitializerRunId") + 1] == request.get("runId"),
             "Original OS process/nonce and stable executable argv")
        result_players[mode] = {"pid": pid, "exit": 0, "commit": commit, "state": state,
                                "Bi4Phase103": 1, "nativeCallback": 1}
    need(result_players["initializer-control"]["pid"] !=
         result_players["initializer-failure"]["pid"], "Two distinct PIDs")
    return {
        "kind": "R03Initializer07PublishedRecordCrossCheckV1",
        "result": "PassedPublishedRecordCrossCheck_NotRuntimeOrV2Acceptance",
        "executionDemo": PINS["hybridclr_demo"], "sourcePins": PINS, "cells": 15,
        "players": result_players, "publishedBuildReceiptSha256": sha(build_bytes),
        "physicalGameAssemblyRehashed": False, "fullProductArchiveRehashed": False,
        "capturedGeneric15Executed": False, "nativeV2TransportAuthenticated": False,
        "runtimeAcceptance": False, "R03Accepted": False, "H2Passed": False,
        "ReadyForHumanReviewGate": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checkpoint", type=Path, default=CHECKPOINT)
    try:
        print(json.dumps(verify(p.parse_args().checkpoint), sort_keys=True))
        return 0
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        print("ONEUSE07_PUBLICATION_BLOCKED: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
