#!/usr/bin/env python3
"""Independent read-only cross-check of the Git-published oneuse-09 receipts.

Rechecks exact published raw bytes and selected semantic/identity joins. It
DOES NOT run Unity, rehash the original physical macOS Player, reassemble
the 509-member sealed archive, authenticate a native V2 snapshot, or grant R03.
The historical 08 prerequisite checkpoint is immutable and separate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from captured_ci_job_admission import validate as validate_ci
from verify_captured_generic_native import verify as validate_captured
from verify_initializer_observation import strict_load as initializer_load, verify as validate_initializer
from verify_initializer_trace import parse as parse_trace, summarize as summarize_trace

CHECKPOINT = (Path(__file__).resolve().parents[3] /
    "Docs/AssemblyShadow/History/M07R/R03/local-validation-captured-generic-20261109-oneuse-09")
PINS = {
    "hybridclr_demo": "bb5fce9c15450e68c6341d88270fbc30dd7b9738",
    "hybridclr": "4b2774b066cfc6afd77a8c8aded6bda7ea574f55",
    "hybridclr_unity": "948c0e3b4f8891481301770115e8ba4945eea6de",
    "il2cpp_plus": "41764ae1eeefb33b05966e7f7676e52aae39c340",
}
BRIDGE = "c6bbea6e179964b7296bff02ee4f434b188e8578a4e7086da1c283e79b82f3da"
BUILD = "671644a8b110684389fe07c00e6052559b5151d2ed876364824d1bb66ac3b345"
OVERLAY = "a83c776afab8b5befec4291a39c52d85d794633ec74ca977d7b54a7ae9e01ab2"
GAME = "1a7b6a25125c79478b6019a859498fbed6d412cd8d05bc03aed4d081e77882c4"
EXECUTABLE = "e8eacb584cb71d6f54d7a73d72ff11a1bc9c8790526228d444ef49b25268656c"
CAPTURED = "c7e4ddd3da14207ad680e9c0f60458f967661202a9cbf6a383ba06289ec11aab"
PIDS = {"initializer-control": 52095, "initializer-failure": 52113, "captured-generic": 52122}
FIXTURES = {
    "initializer-control": "d6e5b66f695498a9ba0806ea81930f03804d98f77382cb851d24c2b24f24202e",
    "initializer-failure": "6ad097153da2054579c13ec48d9f81a35d2551b08bf7a77398f13809ef9e5370",
    "captured-generic": CAPTURED,
}
COMMANDS = {"initializer-control": "0026", "initializer-failure": "0027", "captured-generic": "0028"}
CELLS = {
    "entry-authority", "initializer-host-contracts", "captured-host-contracts",
    "original-s-archive", "original-s-process-joins", "audit_s_generated_material",
    "audit_s_binary_linkage", "real-dll-fixtures", "ir-generator-build",
    "initializer-native-targets", "captured-generic-targets", "prepare-release",
    "prepare-initializer", "prepare-captured", "build-captured",
    "player-initializer-control", "player-initializer-failure",
    "player-captured-generic", "final-authority",
}
SENTINEL = "R03IR.InitializerFailure.AfterPublication.V1"
REASON = ("ShadowCapturedBaselineType Assembly=Assembly-CSharp "
          "Type=AssemblyShadow.R03.IR.R03CapturedGenericAotOwner Method=Touch "
          "Site=R03IR:PhysicalCapturedAotOwner CapturedArgumentAssembly=Methods "
          "Context=method_inst TypePath=/arg[0] Reason=CapturedBaselineType")


class PublishedAuditRejected(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise PublishedAuditRejected(reason)


def exact_int(value, expected):
    return type(value) is int and value == expected


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw):
    need(type(raw) is bytes and 0 < len(raw) <= 10_000_000, "Bounded original evidence bytes")
    def unique(items):
        result = {}
        for name, value in items:
            need(name not in result, "Duplicate original evidence JSON key " + name)
            result[name] = value
        return result
    return json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(PublishedAuditRejected("Non-finite original JSON")))


def no_acceptance(obj):
    need(type(obj) is dict and
         all(obj.get(name) is False for name in ("runtimeAcceptance", "R03Accepted", "H2Passed")),
         "Historical or runtime acceptance claim is forbidden")


def verify(root=CHECKPOINT, overrides=None):
    root = Path(root)
    need(root.is_absolute() and root.is_dir() and
         root.resolve(strict=True) == root and not root.is_symlink(),
         "Canonical Git-published checkpoint root required")
    overrides = dict(overrides or {})
    def read(relative):
        need(type(relative) is str and not Path(relative).is_absolute() and
             ".." not in Path(relative).parts, "Only bounded relative evidence paths")
        if relative in overrides:
            need(type(overrides[relative]) is bytes, "Override must be original raw bytes")
            return overrides[relative]
        p = root / relative
        need(p.is_file() and not p.is_symlink() and
             p.resolve(strict=True) == p, "Missing/aliased Git-published file " + relative)
        return p.read_bytes()
    def load(p):
        return strict_json(read(p))
    local = load("LOCAL_RESULT.json")
    findings = load("local-evidence/RUNTIME_FINDINGS.json")
    independent = load("local-evidence/FINAL_INDEPENDENT_AUDIT.json")
    ledger = load("batch/LOCAL_BATCH_RESULT.json")
    need(local.get("result") == "PASS" and
         local.get("producerResult") == "FocusedCapturedGenericAndInitializerEvidenceForIndependentReview" and
         local.get("sourcePins") == PINS and local.get("nextState") == "Primary Implementation" and
         findings.get("producerResult") == local["producerResult"] and
         findings.get("result") == "PASS" and findings.get("firstFailedCell") is None,
         "Exact Local oneuse09 and source tuple")
    no_acceptance(local)
    # The original RUNTIME_FINDINGS producer writes runtimeAcceptance only;
    # never invent R03/H2 fields missing from that historical JSON schema.
    need(findings.get("runtimeAcceptance") is False,
         "Original findings cannot claim runtime acceptance")
    no_acceptance(independent)
    no_acceptance(ledger)
    runner = local.get("runner", {})
    argv = runner.get("command", [])
    need(type(argv) is list and argv.count("--demo-commit") == 1 and
         argv[argv.index("--demo-commit")+1] == PINS["hybridclr_demo"] and
         exact_int(runner.get("runnerInvocations"), 1) and
         exact_int(runner.get("exitCode"), 0) and runner.get("retryPerformed") is False,
         "One exact original Local invocation, no replay")
    states = local.get("cellStates", {})
    need(type(states) is dict and set(states) == CELLS and
         all(status == "Passed" for status in states.values()) and
         local.get("cellCounts") == {"Passed": 19} and
         findings.get("cells") == {"Passed": 19} and
         independent.get("cellCounts") == {"Passed": 19} and
         independent.get("cellStates") == states and
         independent.get("runnerInvocations") == 1 and
         independent.get("result") == "PassedReceiptAndCustodyAudit_ProducerSemanticResultRetained" and
         independent.get("sourcePins") == PINS and
         independent.get("archiveMembers") == 509,
         "Original complete 19-cell independent scope")
    repository_record = ledger.get("repositories", {})
    need(ledger.get("kind") == "R03IRCapturedGenericOneUse09EvidenceBatchV1" and
         type(repository_record) is dict and
         all(repository_record.get(k) == v for k, v in PINS.items()) and
         repository_record.get("branch") == "codex/assembly-shadow-r01b-h1" and
         repository_record.get("runtimeAcceptance") is False and
         ledger.get("result") == "FocusedCapturedGenericAndInitializerEvidenceForIndependentReview" and
         exact_int(ledger.get("plannedFreshUnityBuilds"), 1) and
         exact_int(ledger.get("verifiedFreshUnityBuilds"), 1) and
         exact_int(ledger.get("plannedFreshPlayers"), 3) and
         exact_int(ledger.get("verifiedFreshPlayers"), 3) and
         ledger.get("nativeV2TransportImplemented") is False and
         ledger.get("firstRecoveryAuthenticatedV2") is False and
         ledger.get("fullOriginalSIndependentCompilerLinkPlayerJoin") is False and
         ledger.get("pureInterpreterExpansionEnabled") is False and
         ledger.get("originalRetiredEvidenceRegenerated") is False and
         ledger.get("wholeVmEpoch") == "NotProven",
         "No false nativeV2/wholeVM/originalS/R03 acceptance")
    seal = local.get("seal", {})
    custody = local.get("hostCustody", {})
    need(local.get("sealStatus") == "Passed" and
         seal == load("batch/seal-receipt.json") and
         seal.get("members") == 509 and seal.get("runtimeAcceptance") is False and
         sha(read("batch/evidence-index.json")) == seal.get("indexSha256") and
         custody.get("fileCount") == 3198 and custody.get("symlinkCount") == 4 and
         custody.get("result") == "PassedFullRegularBytesAndLiteralSymlinkTargets" and
         independent.get("sealStatus") == "Passed",
         "Bounded 509-member seal/index and external host custody declarations")

    receipt_bytes = read("batch/builds/candidate-release/build-receipt.json")
    build = strict_json(receipt_bytes)
    local_build = local.get("build", {})
    need(sha(receipt_bytes) == BUILD == local_build.get("sha256") and
         findings.get("build", {}).get("sha256") == BUILD and
         build.get("result") == "Passed" and build.get("buildPipelineResult") == "Succeeded" and
         exact_int(build.get("errors"), 0) and exact_int(build.get("warnings"), 1) and
         build.get("unityVersion") == "2022.3.62f2" and
         build.get("architecture") == "arm64" and
         build.get("initializerBridgeSignature") == "Bi4" and
         build.get("initializerBridgeGeneratedSha256") == BRIDGE and
         build.get("initializerBridgePostBuildSha256") == BRIDGE and
         build.get("initializerBridgeLinkedRuntimeObserved") is False and
         build.get("testOverlaySha256") == OVERLAY and
         build.get("runtimeAcceptance") is False and
         local_build.get("bridge", {}).get("gameAssemblySha256") == GAME and
         local_build.get("executableSha256") == EXECUTABLE and
         local_build.get("sourceManifestSha256") == build.get("sourceManifestSha256"),
         "Exact generated Bi4, native overlay, GameAssembly, Player and original BuildReceipt")
    need(type(local.get("players")) is list and len(local["players"]) == 2 and
         type(findings.get("players")) is list and len(findings["players"]) == 3 and
         len({x.get("case") for x in findings["players"]}) == 3,
         "Two initializer and one distinct captured Player")
    identities = {}
    results = {}

    def original_process(mode, request, verification, row):
        expected = PIDS[mode]
        prefix = "batch/players/IR-R03-02-" + mode + "/"
        args = load("batch/commands/" + COMMANDS[mode] + "/command.json")
        actual = args.get("command", [])
        flag = "-r03IrCapturedRunId" if mode == "captured-generic" else "-r03IrInitializerRunId"
        need(exact_int(row.get("commandPid"), expected) and
             exact_int(row.get("commandExit"), 0) and
             exact_int(args.get("pid"), expected) and
             exact_int(args.get("exitCode"), 0) and
             args.get("timeout") is False and args.get("remainingProcessGroup") is False and
             args.get("interrupted") is False and
             type(actual) is list and actual.count(flag) == 1 and
             actual[actual.index(flag)+1] == request.get("runId") and
             actual.count("-logFile") == 1 and
             actual[actual.index("-logFile")+1].endswith(
                 "/IR-R03-02-" + mode + "/Player.log"),
             "Original OS process/nonce/command source join")
        # Literal OS argv fields, not user-synthesized PIDs or host parser receipts.
        need(any(item.endswith("/IR-R03-02-" + mode + "/request.json") for item in actual) and
             any(item.endswith("/IR-R03-02-" + mode + "/raw.json") for item in actual) and
             verification.get("launchPid") == expected and
             verification.get("runId") == request.get("runId") and
             verification.get("buildReceiptSha256") == BUILD and
             verification.get("executableSha256") == EXECUTABLE and
             verification.get("nativeOverlaySha256") == OVERLAY and
             verification.get("sourceManifestSha256") == build["sourceManifestSha256"],
             "Original process-specific raw/output/source binding")
        identities[mode] = (expected, request.get("runId"))
        return args

    for mode, commit, state in (("initializer-control", 0, 6),
                                ("initializer-failure", 19, 9)):
        row = next((x for x in local["players"] if x.get("case") == mode), None)
        reported = next((x for x in findings["players"] if x.get("case") == mode), None)
        need(type(row) is dict and type(reported) is dict and
             row.get("state") == "Passed" and reported.get("state") == "Passed",
             "One passed original initializer result")
        prefix = "batch/players/IR-R03-02-" + mode + "/"
        request_bytes = read(prefix+"request.json")
        request = strict_json(request_bytes)
        raw_bytes = read(prefix+"raw.json")
        raw = initializer_load(raw_bytes)
        verification = load(prefix+"verification.json")
        need(request.get("stimulus") == mode and request.get("dllSha256") == FIXTURES[mode] and
             sha(request_bytes) == verification.get("requestSha256") and
             sha(raw_bytes) == row.get("rawSha256") == verification.get("rawSha256") and
             exact_int(row.get("rawBytes"), 752) and
             verification.get("result") == "PassedFocusedV1PlayerObservation_NotV2" and
             verification.get("firstRecoveryAuthenticated") is False and
             verification.get("nativeV2TransportImplemented") is False,
             "Original initializer request and strict 752-byte V1 raw identity")
        no_acceptance(raw)
        no_acceptance(verification)
        need(validate_initializer(raw, request, {"pid": PIDS[mode]}, FIXTURES[mode]).get("result") ==
             "SchemaConsistentNotRuntimeAuthenticated", "Original initializer strict V1 semantics")
        original_process(mode, request, verification, row)
        recovery_bytes = read(prefix+"raw.json.vm-recovery.json")
        recovery = strict_json(recovery_bytes)
        native = recovery.get("nativeRecovery", {})
        trace_bytes = read(prefix+"raw.json.native-trace.jsonl")
        trace = parse_trace(trace_bytes, request, PIDS[mode], FIXTURES[mode])
        summary = summarize_trace(trace, require_complete=True)
        by_phase = {}
        for event in trace:
            by_phase.setdefault(event["phase"], []).append(event)
        phases = (103, 190, 299, 300, 191, 201, 601, 620)
        need(all(len(by_phase.get(p, [])) == 1 for p in phases) and
             [by_phase[p][0]["seq"] for p in phases] ==
                 sorted(by_phase[p][0]["seq"] for p in phases) and
             tuple(by_phase[300][0][k] for k in ("a", "b", "c", "d")) == (1, 3, 15, 1) and
             summary.get("genuineLinkedBi4ProbeStatus") == [1] and
             recovery.get("processId") == PIDS[mode] and
             recovery.get("runId") == request["runId"] and
             recovery.get("fixtureSha256") == FIXTURES[mode] and
             native.get("stateCode") == state and native.get("terminalFailureCode") == commit and
             (native.get("reason", "").endswith(SENTINEL) if commit else native.get("reason") == "") and
             raw.get("commitReturn") == commit and raw.get("finalState") == state and
             raw.get("preparedField") == 3 and raw.get("positiveMask") == 15 and
             raw.get("initializerCallbackCalls") == 1 and
             raw.get("postAotSucceeded") is False and
             raw.get("postAotAttempted") is (commit == 19),
             "Bound real linked Bi4, physical callback, native first-recovery")
        results[mode] = {"pid": PIDS[mode], "commit": commit, "state": state,
                         "linkedBi4": 1, "callback": 1}

    row = local.get("capturedPlayer")
    reported = next((x for x in findings["players"] if x.get("case") == "captured-generic"), None)
    need(type(row) is dict and type(reported) is dict and
         row.get("state") == "Passed" and reported.get("state") == "Passed",
         "Exactly one published captured-generic result")
    prefix = "batch/players/IR-R03-02-captured-generic/"
    request_bytes = read(prefix+"request.json")
    raw_bytes = read(prefix+"raw.json")
    request, raw = strict_json(request_bytes), strict_json(raw_bytes)
    verification = load(prefix+"verification.json")
    need(request.get("stimulus") == "captured-generic" and
         request.get("dllSha256") == CAPTURED and
         sha(request_bytes) == verification.get("requestSha256") and
         sha(raw_bytes) == row.get("rawSha256") == verification.get("rawSha256") and
         exact_int(row.get("rawBytes"), 1273) and
         verification.get("result") == "PassedFocusedCapturedGenericV1PlayerObservation_NotV2" and
         verification.get("nativeV2TransportImplemented") is False and
         verification.get("semanticRecord", {}).get("nativeVMProofIndependent") is False,
         "Actual original captured-generic 1273-byte request/native V1")
    original_process("captured-generic", request, verification, row)
    no_acceptance(raw)
    no_acceptance(verification)
    observed = validate_captured(raw_bytes, request, expected_pid=PIDS["captured-generic"],
                                 expected_owner="Assembly-CSharp", expected_fixture_sha256=CAPTURED)
    need(observed.get("result") == "SchemaConsistentNotRuntimeAuthenticated" and
         raw.get("physicalTypeIndex") == 1 and
         raw.get("methodInflated") is True and
         raw.get("methodContextPhysical") is True and
         raw.get("ownerIndependentAot") is True and
         raw.get("guardAllowed") == 0 and
         exact_int(raw.get("beforeState"), 6) and exact_int(raw.get("afterState"), 9) and
         exact_int(raw.get("beforeCount"), 1) and exact_int(raw.get("afterCount"), 1) and
         raw.get("runtimeInvokeAttempted") is True and
         raw.get("runtimeInvokeSucceeded") is False and
         raw.get("runtimeInvokeThrew") is True and
         raw.get("nativeRecovery", {}).get("reason") == REASON and
         exact_int(raw.get("nativeRecovery", {}).get("terminalFailureCode"), 15),
         "Actual physical method-inst captured baseline and first error15")
    need(local.get("capturedTarget", {}).get("sha256") == CAPTURED and
         local["capturedTarget"].get("sameHostRepeatSha256") == CAPTURED and
         local["capturedTarget"].get("size") == 2560 and
         local["capturedTarget"].get("mvid") == "d8f7bafb-421a-2979-4e5a-1b290117a32a",
         "Actual independent same-host captured target MVID/size/digest")
    results["captured-generic"] = {"pid": PIDS["captured-generic"],
                                   "beforeState": 6, "afterState": 9,
                                   "firstError": 15, "methodInstPhysical": True,
                                   "postTerminalBodyCalls": 0}
    need(len(set(identities.values())) == 3 and len({x[0] for x in identities.values()}) == 3
         and len({x[1] for x in identities.values()}) == 3,
         "Three genuinely independent OS process and nonce identities")

    ci = load("local-evidence/captured-generic-09-prerequisite-CI.json")
    ci_verified = validate_ci(ci, PINS["hybridclr_demo"])
    summary = load("local-evidence/CI_VALIDATOR.json")
    need(ci_verified.get("result") == "PassedSevenWorkflowFourteenJobRecords_NoLocalAuthorization" and
         ci_verified.get("verifiedWorkflows") == summary.get("verifiedWorkflows") and
         exact_int(summary.get("workflowCount"), 7) and
         exact_int(summary.get("jobCount"), 14) and
         summary.get("sourceCommit") == PINS["hybridclr_demo"] and
         summary.get("oldInconsistentJobWaived") is False and
         summary.get("localRunnerAuthorizedByThisRecord") is False,
         "Original published seven completed-workflow / fourteen completed-job CI source join")
    return {
        "kind": "R03Captured09PublishedCrossCheckV1",
        "result": "PassedPublishedBoundedRawCrossCheck_NotUnityV2OrR03Acceptance",
        "sourcePins": PINS,
        "cells": 19, "players": results, "verifiedCIRuns": 7,
        "originalPhysicalGameAssemblyRehashed": False,
        "fullProductSealArchiveRehashed": False,
        "originalNativeV2ProducerPresent": False,
        "firstExceptionTypeIdentified": False,
        "wholeVmEpochAuthenticated": False,
        "runtimeAcceptance": False, "R03Accepted": False,
        "H2Passed": False, "ReadyForHumanReviewGate": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=CHECKPOINT)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.checkpoint), sort_keys=True))
        return 0
    except (ValueError, KeyError, TypeError, IndexError, OSError, UnicodeError) as error:
        print("R03_CAPTURED09_PUBLICATION_BLOCKED: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
