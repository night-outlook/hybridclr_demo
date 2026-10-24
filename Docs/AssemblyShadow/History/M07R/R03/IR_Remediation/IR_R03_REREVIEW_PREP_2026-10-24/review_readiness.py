#!/usr/bin/env python3
"""R03 IR-R03-01/02 source and original-S identity pre-review; no Player or builds.

Reads exact pinned source/checkpoint files and emits typed, negative scope.
Existing independent R03 FAIL, S 90/90 and f51d historical-only PASS are distinct.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

CURRENT = {
    "hybridclr": "4b2774b066cfc6afd77a8c8aded6bda7ea574f55",
    "hybridclr_unity": "948c0e3b4f8891481301770115e8ba4945eea6de",
    "il2cpp_plus": "e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb",
}
EXPECTED_BLOBS = {
    "libil2cpp/vm/AssemblyShadow.cpp": "57cf47f964a83973df8296955ccf856b105c595f",
    "libil2cpp/vm/AssemblyShadowTerminalExecution.h": "33258986c31b2e6ae3af17b8553030482a83aef7",
    "libil2cpp/vm/Runtime.cpp": "96b914fbeb31c69d649e4076a802de0b6418daa8",
    "hybridclr/interpreter/Interpreter_Execute.cpp": "2dbdb7527afee7f2546e45f20e6ef93e1bca237a",
    "Tools/AssemblyShadow/R03/source-pins.json": "9d72a237fb6ecd3efe3267ca89625aa49c61775d",
}
S_PREFIX = ("Docs/AssemblyShadow/History/M07R/R03/"
            "local-validation-20261007-batch-s-evidence-ready")
CORRECTIVE = ("Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/"
              "ORIGINAL_S_PROVENANCE_CORRECTION_2026-10-08.json")
OLD_EVIDENCE = "Docs/AssemblyShadow/History/M07R/R03/S_Reconciliation/EVIDENCE.json"
OLD_REVIEW = ("Docs/AssemblyShadow/History/M07R/R03/S_Reconciliation/"
              "INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md")
OWNER = ("Docs/AssemblyShadow/History/M07R/R03/S_Reconciliation/"
         "OWNER_DISPOSITION_2026-10-08.md")
PLAYER = "Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs"
RUNNER = "Tools/AssemblyShadow/R03IR/run_terminal_local.py"
C04 = S_PREFIX + "/batch/players/C04-old-AOT-guard/verification.json"


class ReviewReadinessError(ValueError):
    pass


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise ReviewReadinessError(msg)


def read(root: pathlib.Path, path: str) -> bytes:
    candidate = root / path
    require(candidate.is_file() and not candidate.is_symlink(),
            "Missing/aliased review input: " + path)
    return candidate.read_bytes()


def jread(root: pathlib.Path, path: str):
    def unique(pairs):
        obj = {}
        for name, value in pairs:
            if name in obj:
                raise ReviewReadinessError("Duplicate JSON member in " + path + ": " + name)
            obj[name] = value
        return obj
    return json.loads(read(root, path), object_pairs_hook=unique)


def blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def source_body(source: str, signature: str) -> str:
    """Return one named C++ function body. This is a source-contract check, not a compiler."""
    require(source.count(signature) == 1, "Missing/duplicate C++ symbol: " + signature)
    start = source.index(signature)
    left = source.find("{", start + len(signature))
    require(left > start and left - start < 380,
            "Missing C++ function body: " + signature)
    depth = 0
    for i in range(left, len(source)):
        char = source[i]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[left + 1:i]
    raise ReviewReadinessError("Unclosed C++ function: " + signature)


def check_terminal_source(core: str, policy: str, runtime: str, interpreter: str):
    function = source_body(core, "bool AssemblyShadow::AssertMethodIsActive(")
    first = function.index("if (TerminalMethodDenied(method)) return false;")
    owners = function.index("PhysicalMethodAssembly(method)")
    observe = function.index("ObserveExecutionClass(method->klass)")
    late = function.index("if (error == AssemblyShadowError::Success) return !TerminalMethodDenied(method);")
    require(first < owners < observe < late,
            "Native entry denial not both early and on success path")
    wrapper = source_body(core, "void AssemblyShadow::RequireActiveMethod(")
    require(wrapper.index("if (!AssertMethodIsActive(method, site))") <
            wrapper.index("if (TerminalMethodDenied(method))") <
            wrapper.index("RaiseTerminalExecutionRejected();") <
            wrapper.index("FailTypeResolution("),
            "Terminal rejection chain not fail-closed before original failure handling")
    terminal = source_body(core, "bool TerminalMethodDenied(")
    for anchor in ("s_state.load(std::memory_order_acquire)",
                   "s_typeFailure.load(std::memory_order_acquire)",
                   "s_unexpectedFailure.load(std::memory_order_acquire)",
                   "s_lateBaselineUse.load(std::memory_order_acquire)",
                   "s_referenceViolation.load(std::memory_order_acquire)",
                   "assembly_shadow_terminal::TerminalForBusiness",
                   "assembly_shadow_terminal::RejectMethod"):
        require(anchor in terminal, "Missing terminal predicate source: " + anchor)
    constructors = source_body(core, "bool IsFixedDiagnosticConstructor(")
    for label in ("Image::GetCorlib()", '"Object"', '"Exception"',
                  '"SystemException"', '"InvalidOperationException"'):
        require(label in constructors, "Missing exact diagnostic constructor constraint: " + label)
    require("s_constructingFixedDiagnosticException && IsFixedDiagnosticConstructor(method)"
            in terminal, "Diagnostic construction exception scope not bound")
    require("return state == kFailed || state == kFailedAfterCommit" in policy and
            "(state != kDisabled && durableFailure)" in policy and
            "!(constructingDiagnostic && verifiedFixedExceptionCtor)" in policy,
            "Terminal header changed scope/policy")
    invoke = source_body(runtime, "Il2CppObject* Runtime::Invoke(")
    require(invoke.index("assembly_shadow_reporting::TryHandle(") <
            invoke.index("AssemblyShadow::ResolveReflectionMethod(") <
            invoke.index('AssemblyShadow::RequireActiveMethod(method, "Runtime::Invoke")') <
            invoke.index("ClassInit(method->klass)") <
            invoke.index("return InvokeWithThrow(method, obj, params);"),
            "Invoke may enter method before guarded identity admission")
    invoke_throw = source_body(runtime, "Il2CppObject* Runtime::InvokeWithThrow(")
    require(invoke_throw.index('AssemblyShadow::RequireActiveMethod(method, "Runtime::InvokeWithThrow")') <
            invoke_throw.index("hybridclr::InitAndGetInterpreterDirectlyCallMethodPointer(method)"),
            "Direct managed invocation lacks pre-body guard")
    for s in ('REQUIRE_ACTIVE_METHOD(newMethodInfo, "Interpreter.entry")',
              'REQUIRE_ACTIVE_METHOD(newMethodInfo, "Interpreter.nestedCall")',
              'REQUIRE_ACTIVE_METHOD(method, "Interpreter.delegateTarget")',
              'REQUIRE_ACTIVE_METHOD(_actualMethod, "Interpreter.virtualTarget")'):
        require(s in interpreter, "Interpreter method boundary not guarded: " + s)
    require(interpreter.count("REQUIRE_ACTIVE_METHOD(") > 10 and
            "PREPARE_NEW_FRAME_FROM_NATIVE(methodInfo, args, ret)" in interpreter,
            "Interpreter requires detailed entry inspection")
    return {
        "staticGuards": "PassedPresentSourceContractsOnly",
        "terminalCheckBeforeMethodAndBeforeSuccess": True,
        "runtimeInvokeAndInvokeWithThrowGuarded": True,
        "interpreterEntryNestedDelegateVirtualSourceGuarded": True,
        "actualPostPoisonPlayerOnCurrentSource": "NotRun",
        "allDirectAotToAotEntryCovered": False,
        "userCodeAfterPoisonGloballyProven": False,
    }


def check_player_fixture(player: str, runner: str, source_pins: dict):
    snippets = [
        "report.preActiveReflection = (int)activeMethod.Invoke(instance, null);",
        "report.preActiveDelegate = activeDelegate();",
        "report.preShadowField = (int)stableField.GetValue(instance);",
        "report.activeReflectionAttempted = true;",
        "try { activeMethod.Invoke(instance, null); report.activeReflectionSucceeded = true; }",
        "report.activeDelegateAttempted = true;",
        "try { activeDelegate(); report.activeDelegateSucceeded = true; }",
        "report.aotReflectionAttempted = true;",
        "try { canary.Invoke(null, null); report.aotReflectionSucceeded = true; }",
        "report.shadowFieldReadable = R03_IR_ReadActiveField(out afterField) == 1;",
        "report.finalShadowField == report.preShadowField",
        "report.finalCanaryCount == report.preCanaryCount",
        "report.recoveryStable = report.firstRecovery == report.finalRecovery;",
    ]
    for anchor in snippets:
        require(anchor in player, "IR-02 Player witness disappeared: " + anchor)
    require('report.poisonedState = (int)state;' in player and
            player.index("report.activeReflectionAttempted = true;") >
            player.index("report.poisonedState = (int)state;"),
            "Post-poison active method attempt precedes recorded poison")
    require("original_s_fixtures" in runner and
            "R03TerminalPlayer.cs" in runner and
            "IR_TARGET_SHA256" in runner and
            "verify_ir(" in runner,
            "Source-bound focused Player runner missing")
    observed_pin = source_pins["il2cpp_plus"]
    return {
        "sourceFixtureContracts": "PassedPresentSourceContractsOnly",
        "sourceNativePin": observed_pin,
        "currentNativeHead": CURRENT["il2cpp_plus"],
        "nativePinMatchesCurrent": observed_pin == CURRENT["il2cpp_plus"],
        "freshPostPoisonPlayerExecution": "NotRun",
        "playerGate": "ReadyForSeparateLocalAdmission"
        if observed_pin == CURRENT["il2cpp_plus"]
        else "BlockedStaleRunnerNativePin",
        "genericCapturedAndInitializerPlayerCoverage": "NotProvenHere",
    }


def check_original_s(transport: dict, seal: dict, correction: dict,
                     stale: dict, review: str, disposition: str, c04: dict):
    require("Overall verdict: **FAIL**" in review or
            "Overall verdict: **FAIL**" in review.replace("  ", " "),
            "Existing independent FAIL review not retained")
    for name in ("IR-R03-01", "IR-R03-02"):
        require(name in review, "Original high-severity finding absent: " + name)
    require("D1=A" in disposition and "D2=A" in disposition,
            "Owner scoped D1/D2 not retained")
    require(correction["findingDisposition"]["IR-R03-01"] ==
            "PartiallyRemediatedNotIndependentlyClosed",
            "Original-S provenance was silently marked fully closed")
    require(correction["observedAudit"]["auditResult"] == "Passed" and
            correction["observedAudit"]["ledgerCellJoins"] == 90 and
            correction["observedAudit"]["independentReviewer"] is False,
            "S original archive audit source/authority not retained")
    for name in ("BATCH_EXECUTION.json", "LOCAL_BATCH_RESULT.json", "evidence.tar.gz"):
        matched = [x for x in transport["files"] if x["originalPath"].endswith("/" + name)]
        require(len(matched) == 1, "Original S transport identity missing/ambiguous: " + name)
        original = correction["originalArtifacts"][name]
        require(matched[0]["originalSha256"] == original["sha256"] and
                matched[0]["originalSize"] == original["bytes"] and
                len(matched[0]["parts"]) == original["transportParts"],
                "S original transport disagrees with corrective byte identity: " + name)
    require(seal["archiveSha256"] ==
            correction["originalArtifacts"]["evidence.tar.gz"]["sha256"] and
            seal["indexSha256"] ==
            correction["originalArtifacts"]["evidence-index.json"]["sha256"] and
            seal["members"] == 15713,
            "S original seal mismatches corrective transport")
    historical = stale["originalArtifacts"]["evidence.tar.gz"]
    require(historical != seal["archiveSha256"],
            "Historical S conflicting archive was silently substituted")
    require(correction["withdrawnHistoricalClaims"]["status"] == "NotAuthorityForOriginalS",
            "Contradictory older archive claim has not been withdrawn")
    require("newMethodInvocationAttempted" not in c04 and
            "newMethodInvocationSucceeded" not in c04,
            "C04 older evidence field coverage changed")
    return {
        "originalSArchiveCorrectiveBytes": "MatchedOriginalCommittedTransportAndSeal",
        "archiveSha256": seal["archiveSha256"],
        "archiveSize": correction["originalArtifacts"]["evidence.tar.gz"]["bytes"],
        "originalSCellsRecordedAndAuditCrosswalk": 90,
        "stalePrimaryArchiveIdentity": historical,
        "stalePrimaryArchiveWithdrawn": True,
        "priorIndependentFullStageResult": "FAIL",
        "IR_R03_01_Status": "PartiallyRemediatedAwaitingIndependentRereview",
        "independentArchiveSemanticReauthenticationByThisTool": False,
        "originalSExecutionReplayed": False,
    }


def verify(demo: pathlib.Path, native: pathlib.Path,
           hybridclr: pathlib.Path, package: pathlib.Path, check_git: bool = True):
    roots = {"hybridclr_demo": demo, "il2cpp_plus": native,
             "hybridclr": hybridclr, "hybridclr_unity": package}
    if check_git:
        for key, want in CURRENT.items():
            proc = subprocess.run(["git", "-C", str(roots[key]),
                                   "rev-parse", "HEAD"], capture_output=True, text=True)
            require(proc.returncode == 0 and proc.stdout.strip() == want,
                    "Source checkout HEAD mismatch: " + key)
    parts = {}
    sources = {
        "core": (native, "libil2cpp/vm/AssemblyShadow.cpp"),
        "terminal": (native, "libil2cpp/vm/AssemblyShadowTerminalExecution.h"),
        "runtime": (native, "libil2cpp/vm/Runtime.cpp"),
        "interpreter": (hybridclr, "hybridclr/interpreter/Interpreter_Execute.cpp"),
        "pins": (demo, "Tools/AssemblyShadow/R03/source-pins.json"),
    }
    for k, (root, path) in sources.items():
        raw = read(root, path)
        require(blob(raw) == EXPECTED_BLOBS[path],
                "Unexpected source Git blob: " + path)
        parts[k] = raw.decode("utf-8")
    guards = check_terminal_source(parts["core"], parts["terminal"],
                                   parts["runtime"], parts["interpreter"])
    pins = json.loads(parts["pins"])
    require(pins["hybridclr"] == CURRENT["hybridclr"] and
            pins["hybridclr_unity"] == CURRENT["hybridclr_unity"],
            "Original managed/package source pins changed")
    player = check_player_fixture(read(demo, PLAYER).decode(),
                                  read(demo, RUNNER).decode(), pins)
    source = check_original_s(
        jread(demo, S_PREFIX + "/FILE_TRANSPORT.json"),
        jread(demo, S_PREFIX + "/batch/seal-receipt.json"),
        jread(demo, CORRECTIVE), jread(demo, OLD_EVIDENCE),
        read(demo, OLD_REVIEW).decode(),
        read(demo, OWNER).decode(),
        jread(demo, C04))
    return {
        "kind": "R03IndependentRereviewSourceReadinessV1",
        "result": "PassedSourceOnlyPreflight_PendingRealPlayerAndIndependentReview",
        "sourcePins": CURRENT,
        "guards": guards, "focusedPlayerWitness": player, "originalSProvenance": source,
        "R03Accepted": False, "H2Passed": False,
        "ReadyForHumanReviewGate": False, "qualificationApproved": False,
        "PureInterpreterEnabled": False, "runtimeAcceptance": False,
        "newUnityOrPlayerOrSdkCompilation": False,
        "nextActions": [
            "Primary must repair/review stale R03 focused-runner native pin before any source-matched Player run",
            "IR-R03-02 needs actual protected post-poison business-entry Player evidence with original safety/side-effect negative controls",
            "IR-R03-01 needs independent acceptance of authenticated original-S archive and withdrawn contradictory older archive",
            "Independent complete R03 full-stage re-review remains required, followed by separately user-initiated H2 if exit conditions close"
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("demo", "native", "hybridclr", "package"):
        parser.add_argument("--" + name, type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    try:
        require(args.output.is_absolute() and not args.output.exists(),
                "Source-only output must be a new absolute path")
        report = verify(args.demo, args.native, args.hybridclr, args.package)
        # Output is intentionally a fresh CI-only report, not a substitute for original S/Player evidence.
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as f:
            json.dump(report, f, sort_keys=True, indent=2)
            f.write("\n")
        print("R03_REVIEW_READINESS=" + json.dumps({
            "result": report["result"],
            "terminalGuard": report["guards"]["staticGuards"],
            "playerGate": report["focusedPlayerWitness"]["playerGate"],
            "originalS": report["originalSProvenance"]["IR_R03_01_Status"],
            "runtimeAcceptance": report["runtimeAcceptance"],
            "H2Passed": report["H2Passed"]}, sort_keys=True))
        return 0
    except (ReviewReadinessError, ValueError, KeyError, OSError) as exc:
        print("REVIEW_PREFLIGHT_FAIL_CLOSED: " + repr(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
