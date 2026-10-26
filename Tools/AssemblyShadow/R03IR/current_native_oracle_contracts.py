#!/usr/bin/env python3
"""IR-R03-02 current-native strict Player oracle: SYNTHETIC HOST TESTS ONLY.

Executes existing verify_ir/verify_engine against typed fabricated receipts
to test FAIL-CLOSED rejection logic. It does NOT execute a Unity Player,
make compiler calls, use original runtime output as input, or certify IR-02.
Explicit filename avoids broad historical test_*.py autodiscovery.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from run_terminal_local import verify_ir, verify_engine
from batch_contract import ContractError

HERE = Path(__file__).resolve().parent
PINNED_ORACLE_BLOB = "70b1a27f2dbbcad93f67e8caddcf7282ff3afd73"
PINNED_PLAYER_BLOB = "598feeec3231707091699d99fbf4428d50b52024"
CASE_IDS = {
    "baseline-owner": "IR-R03-02-release-baseline",
    "type-resolution": "IR-R03-02-release-type",
    "off": "IR-R03-02-off",
    "engine-unhandled": "IR-R03-02-release-engine",
}
PINNED_SAMPLE_PID = 424242


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def request_for(stimulus: str) -> dict:
    return {"runId": "typed-host-only-id-9285", "caseId": CASE_IDS[stimulus],
            "stimulus": stimulus}


def strict_recovery(code: int) -> str:
    return json.dumps({"schemaVersion": 1, "published": True, "stateCode": 9,
                       "disposition": "RestartRequired",
                       "terminalFailureCode": code}, sort_keys=True)


def ir_raw(stimulus: str) -> dict:
    req = request_for(stimulus)
    raw = {"reportTransport": "NativePreopenedSnapshotV1",
           "schemaVersion": 1, "kind": "R03IRPostPoisonEntryV1",
           "acceptance": False, "result": "Passed", "error": "",
           "runId": req["runId"], "caseId": req["caseId"],
           "stimulus": stimulus, "processId": PINNED_SAMPLE_PID,
           "unityVersion": "2022.3.62f2", "platform": "OSXPlayer"}
    if stimulus == "off":
        raw.update({"initialState": 0, "finalState": 0, "prePositive": True,
                    "preCanaryCount": 1, "finalCanaryCount": 2,
                    "reserveGcProbeMask": 0, "terminalReportingProbeMask": 0,
                    "activeReflectionAttempted": False,
                    "activeDelegateAttempted": False,
                    "aotReflectionAttempted": False})
    else:
        code = 21 if stimulus == "baseline-owner" else 13
        first = strict_recovery(code)
        raw.update({"reserveGcProbeMask": 31, "initialState": 6,
                    "poisonedState": 9, "finalState": 9, "prePositive": True,
                    "preActiveReflection": 42, "preActiveDelegate": 42,
                    "preCanaryCount": 1, "finalCanaryCount": 1,
                    "preShadowField": 2, "finalShadowField": 2,
                    "shadowFieldReadable": True, "recoveryStable": True,
                    "fixedDiagnosticsReadable": True, "firstRecovery": first,
                    "finalRecovery": first, "terminalReportingProbeMask": 15,
                    "nativeStimulusReturn": 1})
        for entry in ("activeReflection", "activeDelegate", "aotReflection"):
            raw[entry + "Attempted"] = True
            raw[entry + "Succeeded"] = False
            raw[entry + "Exception"] = "ManagedExceptionCaught"
        if stimulus == "baseline-owner":
            raw["nativeGuardJson"] = json.dumps(
                {"available": True, "activeGuard": 1, "baselineGuard": 0,
                 "caughtOldGuard": 1, "stateCode": 9})
    return raw


def engine_raw():
    req = request_for("engine-unhandled")
    return {"schemaVersion": 1, "kind": "R03IREngineReportingV1",
            "runtimeAcceptance": False, "runId": req["runId"],
            "caseId": req["caseId"], "processId": PINNED_SAMPLE_PID,
            "result": "ObservedNotAccepted", "timedOut": False,
            "initialState": 6, "finalState": 9,
            "preManagedLoggerCalls": 1, "finalManagedLoggerCalls": 1,
            "completedReports": 1, "observationMilliseconds": 500,
            "recovery": {"published": True, "stateCode": 9,
                         "terminalFailureCode": 13,
                         "disposition": "RestartRequired"}}


def engine_log():
    run_id = request_for("engine-unhandled")["runId"]
    return (
        '[AssemblyShadowTerminalReport] sequence=1 state=9 message="'
        'R03_ENGINE_UNHANDLED_' + run_id +
        '" managedHandlerExecuted=false\n'
        '[R03ReserveGcProbe] mask=31 source=actual-test\n'
    )


class CurrentNativeOracleContracts(unittest.TestCase):
    """All fixtures in this suite are synthetic; no PASS is empirical Player evidence."""

    @classmethod
    def setUpClass(cls):
        cls.oracle_source = HERE / "run_terminal_local.py"
        cls.player_source = HERE / "PlayerProject/R03TerminalPlayer.cs"
        if git_blob(cls.oracle_source) != PINNED_ORACLE_BLOB:
            raise AssertionError("Existing oracle source changed; review test assumptions")
        if git_blob(cls.player_source) != PINNED_PLAYER_BLOB:
            raise AssertionError("Original Player witness source changed")

    def check_ir(self, stimulus, raw=None, req=None, pid=PINNED_SAMPLE_PID):
        return verify_ir(
            ir_raw(stimulus) if raw is None else raw,
            request_for(stimulus) if req is None else req,
            {"pid": pid}, "synthetic-build-receipt-digest")

    def check_engine(self, raw=None, log=None, req=None, pid=PINNED_SAMPLE_PID):
        return verify_engine(
            engine_raw() if raw is None else raw,
            request_for("engine-unhandled") if req is None else req,
            {"pid": pid}, engine_log() if log is None else log)

    def reject_ir(self, stimulus, mutate, message=""):
        raw = ir_raw(stimulus)
        mutate(raw)
        with self.assertRaises(ContractError, msg=message):
            self.check_ir(stimulus, raw)

    def reject_engine(self, mutate, message=""):
        raw = engine_raw()
        mutate(raw)
        with self.assertRaises(ContractError, msg=message):
            self.check_engine(raw)

    def test_01_actual_source_blobs_fixed(self):
        self.assertEqual(git_blob(self.oracle_source), PINNED_ORACLE_BLOB)
        self.assertEqual(git_blob(self.player_source), PINNED_PLAYER_BLOB)

    def test_02_positive_baseline_owner_oracle_is_nonacceptance(self):
        ret = self.check_ir("baseline-owner")
        self.assertEqual(ret["result"], "Passed")
        self.assertFalse(ret["runtimeAcceptance"])
        self.assertFalse(ret["R03Accepted"])
        self.assertFalse(ret["H2Passed"])

    def test_03_positive_type_resolution_oracle_is_nonacceptance(self):
        ret = self.check_ir("type-resolution")
        self.assertEqual(ret["result"], "Passed")
        self.assertFalse(ret["runtimeAcceptance"])

    def test_04_positive_feature_off_oracle_is_nonacceptance(self):
        ret = self.check_ir("off")
        self.assertEqual(ret["result"], "Passed")
        self.assertFalse(ret["runtimeAcceptance"])

    def test_05_positive_unhandled_engine_oracle_is_scoped(self):
        ret = self.check_engine()
        self.assertEqual(ret["result"], "Passed")
        self.assertFalse(ret["runtimeAcceptance"])

    def test_06_missing_or_false_postpoison_attempt_rejected(self):
        for field in ("activeReflectionAttempted", "activeDelegateAttempted",
                      "aotReflectionAttempted"):
            with self.subTest(field=field):
                self.reject_ir("baseline-owner", lambda r, f=field: r.__setitem__(f, False))
                self.reject_ir("baseline-owner", lambda r, f=field: r.pop(f))

    def test_07_successful_postpoison_body_attempt_rejected(self):
        for field in ("activeReflectionSucceeded", "activeDelegateSucceeded",
                      "aotReflectionSucceeded"):
            with self.subTest(field=field):
                self.reject_ir("baseline-owner", lambda r, f=field: r.__setitem__(f, True))

    def test_08_missing_exception_receipt_rejected(self):
        for field in ("activeReflectionException", "activeDelegateException",
                      "aotReflectionException"):
            for invalid in ("", None):
                with self.subTest(field=field, invalid=invalid):
                    self.reject_ir("baseline-owner",
                                   lambda r, f=field, v=invalid: r.__setitem__(f, v))

    def test_09_actual_method_field_side_effect_rejected(self):
        for after in (3, 0, True):
            with self.subTest(after=after):
                self.reject_ir("baseline-owner",
                               lambda r, v=after: r.__setitem__("finalShadowField", v))

    def test_10_false_native_observer_receipt_rejected(self):
        self.reject_ir("baseline-owner", lambda r: r.__setitem__("shadowFieldReadable", False))

    def test_11_aot_canary_body_side_effect_rejected(self):
        self.reject_ir("baseline-owner", lambda r: r.__setitem__("finalCanaryCount", 2))

    def test_12_first_failure_cause_must_remain_stable(self):
        self.reject_ir("baseline-owner",
                       lambda r: r.__setitem__("finalRecovery", strict_recovery(13)))
        self.reject_ir("baseline-owner",
                       lambda r: r.__setitem__("recoveryStable", False))

    def test_13_first_terminal_state_must_be_real(self):
        for field, invalid in (("initialState", 9), ("poisonedState", 6),
                               ("finalState", 6), ("terminalReportingProbeMask", 0),
                               ("reserveGcProbeMask", 0)):
            with self.subTest(field=field):
                self.reject_ir("baseline-owner",
                               lambda r, f=field, v=invalid: r.__setitem__(f, v))

    def test_14_native_baseline_guard_receipt_required(self):
        for field, invalid in (("available", False), ("activeGuard", 0),
                               ("baselineGuard", 1), ("caughtOldGuard", 0),
                               ("stateCode", 6)):
            with self.subTest(field=field):
                def mutate(raw):
                    guard = json.loads(raw["nativeGuardJson"])
                    guard[field] = invalid
                    raw["nativeGuardJson"] = json.dumps(guard)
                self.reject_ir("baseline-owner", mutate)

    def test_15_native_baseline_stimulus_success_required(self):
        self.reject_ir("baseline-owner",
                       lambda r: r.__setitem__("nativeStimulusReturn", 0))

    def test_16_type_resolution_failure_is_distinct_from_baseline_owner(self):
        self.reject_ir("type-resolution",
                       lambda r: r.__setitem__("firstRecovery", strict_recovery(21)))

    def test_17_off_must_allow_healthy_canary_without_poison(self):
        self.reject_ir("off", lambda r: r.__setitem__("finalCanaryCount", 1))
        self.reject_ir("off", lambda r: r.__setitem__("finalState", 9))
        self.reject_ir("off", lambda r: r.__setitem__("activeReflectionAttempted", True))

    def test_18_identity_and_pid_cannot_be_spoofed(self):
        self.reject_ir("baseline-owner", lambda r: r.__setitem__("runId", "wrong"))
        self.reject_ir("baseline-owner", lambda r: r.__setitem__("processId", 9000))
        self.reject_ir("baseline-owner", lambda r: r.__setitem__("caseId", "wrong"))

    def test_19_exact_platform_and_fresh_target_required(self):
        self.reject_ir("baseline-owner", lambda r: r.__setitem__("platform", "OSXEditor"))
        self.reject_ir("baseline-owner", lambda r: r.__setitem__("unityVersion", "2022.3.11f1"))

    def test_20_result_cannot_self_authorize(self):
        self.reject_ir("baseline-owner", lambda r: r.__setitem__("acceptance", True))
        self.reject_ir("baseline-owner", lambda r: r.__setitem__("result", "Failed"))
        self.reject_ir("baseline-owner", lambda r: r.__setitem__("error", "ignored"))

    def test_21_engine_must_have_true_unhandled_sentinel(self):
        with self.assertRaises(ContractError):
            self.check_engine(log='[AssemblyShadowTerminalReport] sequence=1 state=9 message="OTHER" managedHandlerExecuted=false\n')
        with self.assertRaises(ContractError):
            self.check_engine(log=engine_log().replace("managedHandlerExecuted=false", "managedHandlerExecuted=true"))

    def test_22_engine_only_generic_debug_log_rejected(self):
        with self.assertRaises(ContractError):
            self.check_engine(log="[R03ReserveGcProbe] mask=31 source=test\n")

    def test_23_engine_managed_logger_body_must_not_run_after_poison(self):
        self.reject_engine(lambda r: r.__setitem__("finalManagedLoggerCalls", 2))

    def test_24_engine_bounded_native_completion_required(self):
        for k, value in (("completedReports", 0), ("completedReports", 65),
                         ("observationMilliseconds", 0), ("timedOut", True)):
            with self.subTest(field=k, value=value):
                self.reject_engine(lambda r, key=k, v=value: r.__setitem__(key, v))

    def test_25_engine_terminal_source_and_recovery_still_matters(self):
        self.reject_engine(lambda r: r["recovery"].__setitem__("stateCode", 6))
        self.reject_engine(lambda r: r["recovery"].__setitem__("published", False))
        self.reject_engine(lambda r: r.__setitem__("runtimeAcceptance", True))
        with self.assertRaises(ContractError):
            self.check_engine(log=engine_log() + "fatal=unexpected\n")

    def test_26_player_fixture_proves_attempt_before_field_observation_in_source(self):
        source = self.player_source.read_text(encoding="utf-8")
        tokens = [
            'report.prePositive = report.preActiveReflection == 42',
            'report.activeReflectionAttempted = true;',
            'report.activeDelegateAttempted = true;',
            'report.aotReflectionAttempted = true;',
            'report.shadowFieldReadable = R03_IR_ReadActiveField(out afterField) == 1;',
            'report.finalShadowField = afterField;',
        ]
        indices = [source.find(s) for s in tokens]
        self.assertTrue(all(x >= 0 for x in indices), indices)
        self.assertEqual(indices, sorted(indices))
        self.assertIn('throw engineSentinel;', source)
        self.assertIn('R03_IR_Exit(exit);', source)

    def test_27_complete_case_ids_and_source_only_marker(self):
        self.assertEqual(len(CASE_IDS), 4)
        self.assertEqual(len(set(CASE_IDS.values())), 4)
        self.assertNotIn("UnityEngine", self.oracle_source.read_text())
        self.assertEqual(PINNED_SAMPLE_PID, 424242)


if __name__ == "__main__":
    unittest.main(verbosity=2)
