#!/usr/bin/env python3
"""Source-only adversarial contracts for test-only native physical witness V1.

All source records in this file are synthetic; a PASS proves parser behavior
only. Real VM error15 requires independent fresh Player evidence.
"""
import copy
import json
import unittest
from verify_captured_generic_native import NativeReceiptRejected, verify

RUN = "a123456789abcdef123456789abcdef"
SHA = "a" * 64
PID = 12345
OWNER = "Assembly-CSharp"
REQUEST = {"runId": RUN, "caseId": "IR-R03-02-captured-generic",
           "stimulus": "captured-generic", "dllSha256": SHA}


def fixture():
    return {
        "schemaVersion": 1, "kind": "R03IRCapturedGenericPhysicalNativeV1",
        "result": "ObservedNotAccepted", "processId": PID, "runId": RUN,
        "caseId": REQUEST["caseId"], "fixtureSha256": SHA,
        "ownerAssembly": OWNER, "capturedArgumentAssembly": "Methods",
        "capturedType": "R03.Node", "physicalTypeIndex": 2,
        "methodInflated": True, "methodContextPhysical": True,
        "ownerIndependentAot": True, "guardAllowed": 0,
        "beforeState": 6, "afterState": 9,
        "beforeCount": 1, "afterCount": 1,
        "runtimeInvokeAttempted": True, "runtimeInvokeSucceeded": False,
        "runtimeInvokeThrew": True,
        "nativeRecovery": {
            "schemaVersion": 1, "enabled": True, "capabilityVersion": 1,
            "stateCode": 9, "state": "FailedAfterCommit", "published": True,
            "abortAllowed": False, "dispositionCode": 0,
            "disposition": "RestartRequired", "terminalFailureCode": 15,
            "reason": "ShadowCapturedBaselineType Assembly=Assembly-CSharp "
                      "CapturedArgumentAssembly=Methods Context=method_inst "
                      "TypePath=/arg[0] Reason=CapturedBaselineType",
            "retainedBytes": 2048,
            "baselineEligibilityRequiresStartupValidation": True,
        },
        "runtimeAcceptance": False, "R03Accepted": False, "H2Passed": False,
    }


def encode(value):
    return (json.dumps(value, separators=(",", ":"), sort_keys=True) + "\n").encode()


class NativeCapturedV1Contracts(unittest.TestCase):
    def check(self, obj=None, request=None, pid=PID, owner=OWNER, sha=SHA):
        return verify(encode(fixture() if obj is None else obj),
                      REQUEST if request is None else request,
                      expected_pid=pid, expected_owner=owner,
                      expected_fixture_sha256=sha)

    def test_01_schema_positive_is_explicitly_not_native_authenticated(self):
        r = self.check()
        self.assertEqual(r["result"], "SchemaConsistentNotRuntimeAuthenticated")
        self.assertEqual(r["capturedNativeError15Field"], 15)
        for key in ("runtimeAcceptance", "R03Accepted", "H2Passed",
                    "firstRecoveryAuthenticatedV2", "nativeVMProofIndependent"):
            self.assertFalse(r[key])

    def test_02_reject_invalid_or_forged_fields(self):
        changes = [
            ("schemaVersion", True), ("schemaVersion", 2),
            ("kind", "R03IRInitializerCommitObservationV1"),
            ("result", "Passed"), ("processId", True), ("processId", 12346),
            ("runId", "other"), ("caseId", "initializer-failure"),
            ("fixtureSha256", "b"*64),
            ("ownerAssembly", "Methods"),
            ("capturedArgumentAssembly", "Assembly-CSharp"),
            ("capturedType", "Other.Node"),
            ("physicalTypeIndex", -1), ("physicalTypeIndex", True),
            ("methodInflated", False), ("methodContextPhysical", False),
            ("ownerIndependentAot", False),
            ("guardAllowed", True), ("guardAllowed", 1),
            ("beforeState", 9), ("afterState", 6),
            ("beforeCount", 0), ("afterCount", 2),
            ("runtimeInvokeAttempted", False),
            ("runtimeInvokeSucceeded", True), ("runtimeInvokeThrew", False),
            ("runtimeInvokeThrew", 1),
            ("runtimeAcceptance", True), ("R03Accepted", True),
            ("H2Passed", True)
        ]
        for field, value in changes:
            with self.subTest(field=field, value=value):
                original=fixture();original[field]=value
                with self.assertRaises((NativeReceiptRejected, KeyError, TypeError)):
                    self.check(original)
        self.assertGreaterEqual(len(changes), 28)

    def test_03_first_failure_and_source_reason_must_match(self):
        mutations = [
            ("stateCode", 6), ("state", "Committed"),
            ("terminalFailureCode", 13), ("terminalFailureCode", 19),
            ("terminalFailureCode", True),
            ("reason", "ShadowCapturedBaselineType"),
            ("reason", "ShadowBaselineMethodExecution"),
            ("reason", "ShadowCapturedBaselineType CapturedArgumentAssembly=Methods Reason=CapturedBaselineType"),
            ("reason", "ShadowCapturedBaselineType CapturedArgumentAssembly=Other TypePath=/arg[0] Reason=CapturedBaselineType"),
            ("published", False), ("abortAllowed", True),
            ("disposition", "ActiveShadow"), ("enabled", False),
            ("retainedBytes", -1), ("capabilityVersion", 2),
        ]
        for field, value in mutations:
            with self.subTest(field=field, value=value):
                original=fixture();original["nativeRecovery"][field]=value
                with self.assertRaises((NativeReceiptRejected, KeyError, TypeError)):
                    self.check(original)

    def test_04_external_request_pid_owner_hash_must_be_independent(self):
        wrong = dict(REQUEST, runId="b"*32)
        with self.assertRaises(NativeReceiptRejected): self.check(request=wrong)
        wrong = dict(REQUEST, stimulus="initializer-failure")
        with self.assertRaises(NativeReceiptRejected): self.check(request=wrong)
        wrong = dict(REQUEST, dllSha256="b"*64)
        with self.assertRaises(NativeReceiptRejected): self.check(request=wrong)
        for vals in [(True, OWNER, SHA), (PID+1, OWNER, SHA),
                     (PID, "OtherOwner", SHA), (PID, OWNER, "b"*64)]:
            with self.subTest(vals=vals), self.assertRaises(NativeReceiptRejected):
                self.check(pid=vals[0], owner=vals[1], sha=vals[2])

    def test_05_unknown_missing_duplicate_keys_are_rejected(self):
        original=fixture()
        for key in ("runId", "processId", "nativeRecovery", "R03Accepted"):
            wrong=copy.deepcopy(original);wrong.pop(key)
            with self.subTest(key=key), self.assertRaises(NativeReceiptRejected):
                self.check(wrong)
        wrong=dict(original, fakeNativeRuntimeAccepted=True)
        with self.assertRaises(NativeReceiptRejected): self.check(wrong)
        wrong=fixture();wrong["nativeRecovery"]["unknownExtra"]=1
        with self.assertRaises(NativeReceiptRejected): self.check(wrong)
        raw=encode(original)
        duplicate=raw.replace(b'"schemaVersion":1', b'"schemaVersion":1,"schemaVersion":1',1)
        self.assertNotEqual(duplicate,raw)
        with self.assertRaises(NativeReceiptRejected):
            verify(duplicate,REQUEST,expected_pid=PID,expected_owner=OWNER,
                   expected_fixture_sha256=SHA)

    def test_06_raw_truncation_bogus_lines_and_nonfinite_refused(self):
        valid=encode(fixture())
        for raw in (valid[:-1], valid+b'{}', b'', b'\xff',
                    valid.replace(b'"beforeCount":1', b'"beforeCount":NaN'),
                    b'a'*16385):
            with self.subTest(size=len(raw)), self.assertRaises(
                (NativeReceiptRejected, ValueError, UnicodeError)):
                verify(raw,REQUEST,expected_pid=PID,expected_owner=OWNER,
                       expected_fixture_sha256=SHA)

    def test_07_actual_rejection_requires_managed_exception_evidence(self):
        original=fixture()
        self.assertEqual(self.check(original)["result"],
                         "SchemaConsistentNotRuntimeAuthenticated")
        for value in (False, 0, 1, None):
            original["runtimeInvokeThrew"]=value
            with self.subTest(value=value), self.assertRaises(NativeReceiptRejected):
                self.check(original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
