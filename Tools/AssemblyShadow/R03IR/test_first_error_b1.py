#!/usr/bin/env python3
"""Adversarial host-only B1 parser tests; no Unity/VM execution."""
import copy
import json
import unittest
from verify_first_error_b1 import (
    B1ValidationError, EXPECT, decode, verify_record,
)

RUN = "cafe" * 8
SHA = "a" * 64
REQUEST = {"runId": RUN, "caseId": "IR-R03-02-captured-generic",
           "dllSha256": SHA}
GUARD = ("ShadowCapturedBaselineType Assembly=Assembly-CSharp "
         "CapturedArgumentAssembly=Methods Context=method_inst TypePath=/arg[0]")
INITIALIZER = "R03IR.InitializerFailure.AfterPublication.V1"

def sample(mode):
    state, code, origin = EXPECT[mode]
    request = dict(REQUEST)
    request["caseId"] = {
        "initializer-control": "IR-R03-02-initializer-control",
        "initializer-failure": "IR-R03-02-initializer-failure",
        "captured-generic": "IR-R03-02-captured-generic",
    }[mode]
    reason = None if mode == "initializer-control" else (
        INITIALIZER if mode == "initializer-failure" else GUARD)
    value = {
        "schemaVersion": 1, "kind": "R03NativeFirstErrorB1Player",
        "transport": "PreopenedNativeB1NotV2",
        "runId": request["runId"], "caseId": request["caseId"],
        "fixtureSha256": SHA, "processId": 711, "state": state,
        "code": code, "origin": origin, "reasonLength":
        len(reason.encode()) if reason is not None else 0,
        "expectedCode": code, "expectedOrigin": origin,
        "matchExpected": True, "reason": reason,
        "nativeV2TransportImplemented": False,
        "firstRecoveryAuthenticatedV2": False,
        "wholeVmEpoch": "NotProven",
        "runtimeAcceptance": False, "R03Accepted": False, "H2Passed": False,
    }
    return value, request, reason

class TestB1NativeReceipt(unittest.TestCase):
    def test_01_control(self):
        r,q,reason=sample("initializer-control")
        self.assertEqual(verify_record(r,q,"initializer-control",711,None)["firstCode"],0)

    def test_02_initializer(self):
        r,q,reason=sample("initializer-failure")
        self.assertEqual(verify_record(r,q,"initializer-failure",711,reason)["firstOrigin"],2)

    def test_03_captured(self):
        r,q,reason=sample("captured-generic")
        self.assertEqual(verify_record(r,q,"captured-generic",711,reason)["firstCode"],15)

    def test_04_json_roundtrip(self):
        r,q,reason=sample("captured-generic")
        self.assertEqual(verify_record(decode(json.dumps(r).encode()),q,
                                       "captured-generic",711,reason)["firstCode"],15)

    def test_05_duplicate_json_key_rejected(self):
        with self.assertRaises(B1ValidationError):
            decode(b'{"schemaVersion":1,"schemaVersion":1}')

    def test_06_nonfinite_rejected(self):
        with self.assertRaises(B1ValidationError):
            decode(b'{"test":NaN}')

    def test_07_invalid_utf8_rejected(self):
        with self.assertRaises(B1ValidationError):
            decode(b'\xff')

    def test_08_oversize_rejected(self):
        with self.assertRaises(B1ValidationError):
            decode(b'x' * 32769)

    def test_09_source_id_mutation_rejected(self):
        r,q,reason=sample("captured-generic");r["runId"]="other"
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"captured-generic",711,reason)

    def test_10_pid_swap_rejected(self):
        r,q,reason=sample("captured-generic")
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"captured-generic",999,reason)

    def test_11_fixture_replay_rejected(self):
        r,q,reason=sample("captured-generic");r["fixtureSha256"]="b"*64
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"captured-generic",711,reason)

    def test_12_first_code_swap_rejected(self):
        r,q,reason=sample("captured-generic");r["code"]=19
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"captured-generic",711,reason)

    def test_13_origin_swap_rejected(self):
        r,q,reason=sample("initializer-failure");r["origin"]=1
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"initializer-failure",711,reason)

    def test_14_mismatched_first_reason_rejected(self):
        r,q,reason=sample("captured-generic");r["reason"]=INITIALIZER
        r["reasonLength"]=len(INITIALIZER)
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"captured-generic",711,reason)

    def test_15_truncation_rejected(self):
        r,q,reason=sample("captured-generic");r["reasonLength"]-=1
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"captured-generic",711,reason)

    def test_16_no_later_first_fabricated_control(self):
        r,q,reason=sample("initializer-control");r["state"]=2
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"initializer-control",711,None)

    def test_17_invalid_first_not_accepted(self):
        r,q,reason=sample("initializer-failure");r["state"]=3
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"initializer-failure",711,reason)

    def test_18_false_acceptance_rejected(self):
        r,q,reason=sample("captured-generic");r["R03Accepted"]=True
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"captured-generic",711,reason)

    def test_19_false_v2_rejected(self):
        r,q,reason=sample("captured-generic");r["nativeV2TransportImplemented"]=True
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"captured-generic",711,reason)

    def test_20_wrong_epoch_rejected(self):
        r,q,reason=sample("captured-generic");r["wholeVmEpoch"]="Authenticated"
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"captured-generic",711,reason)

    def test_21_extra_field_rejected(self):
        r,q,reason=sample("captured-generic");r["injected"]="not part of schema"
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"captured-generic",711,reason)

    def test_22_bool_integer_confusion_rejected(self):
        r,q,reason=sample("captured-generic");r["code"]=True
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"captured-generic",711,reason)

    def test_23_match_expected_false(self):
        r,q,reason=sample("captured-generic");r["matchExpected"]=False
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"captured-generic",711,reason)

    def test_24_reason_identity_v1_mismatch(self):
        r,q,reason=sample("initializer-failure")
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"initializer-failure",711,reason+"!")

    def test_25_wrong_case(self):
        r,q,reason=sample("initializer-failure");q["caseId"]="another"
        with self.assertRaises(B1ValidationError):
            verify_record(r,q,"initializer-failure",711,reason)

if __name__ == "__main__":
    unittest.main()
