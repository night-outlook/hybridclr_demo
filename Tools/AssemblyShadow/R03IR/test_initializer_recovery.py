#!/usr/bin/env python3
"""Native VM recovery document contracts; no Unity or HybridCLR VM invocation."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from verify_initializer_recovery import inspect, RecoveryRejected


def fixture(mode="initializer-failure"):
    request = {"runId": "HostInitializerEvidenceRun000001", "caseId": "HOST-INIT",
               "stimulus": mode, "dllSha256": "a" * 64}
    failed = mode == "initializer-failure"
    result = {
        "schemaVersion": 1, "kind": "R03IRNativeInitializerRecoveryV1",
        "runId": request["runId"], "caseId": request["caseId"],
        "stimulus": mode, "fixtureSha256": request["dllSha256"],
        "processId": 987, "nativeReturn": 0,
        "nativeRecovery": {
            "schemaVersion": 1, "enabled": True, "capabilityVersion": 1,
            "stateCode": 9 if failed else 6,
            "state": "FailedAfterCommit" if failed else "Committed",
            "published": True, "abortAllowed": False,
            "dispositionCode": 0 if failed else 4,
            "disposition": "RestartRequired" if failed else "ActiveShadow",
            "terminalFailureCode": 19 if failed else 0,
            "reason": "Methods: actual module initializer exception R03IR.InitializerFailure.AfterPublication.V1" if failed else "",
            "retainedBytes": 2048,
            "baselineEligibilityRequiresStartupValidation": False,
        },
        "runtimeAcceptance": False, "R03Accepted": False, "H2Passed": False,
    }
    return result, request


class NativeRecoveryContractTests(unittest.TestCase):
    def verify(self, changed=None, mode="initializer-failure", payload=None):
        data, request = fixture(mode)
        if changed is not None:
            data = copy.deepcopy(data)
            changed(data)
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "raw.json.vm-recovery.json"
            file.write_bytes(payload if payload is not None else
                             (json.dumps(data, sort_keys=True) + "\n").encode("utf-8"))
            return inspect(file, request, 987, "a" * 64)

    def test_01_actual_schema_shape_both_control_and_failure(self):
        for mode, code, state in (("initializer-control", 0, 6),
                                  ("initializer-failure", 19, 9)):
            with self.subTest(mode=mode):
                report = self.verify(mode=mode)
                self.assertEqual(report["terminalFailureCode"], code)
                self.assertEqual(report["stateCode"], state)
                self.assertIs(report["R03Accepted"], False)
                self.assertEqual(report["result"],
                                 "ParsedNativeVMFirstFailure_NotRuntimeAuthenticated")

    def test_02_identity_fields_and_status_flags_fail_closed(self):
        for key, value in (("kind","V2"), ("runId","wrong"), ("caseId","bad"),
                           ("stimulus","initializer-control"), ("fixtureSha256","b"*64),
                           ("processId", 111), ("nativeReturn", 19),
                           ("runtimeAcceptance", True), ("R03Accepted", True),
                           ("H2Passed", True), ("schemaVersion", True)):
            with self.subTest(key=key), self.assertRaises(RecoveryRejected):
                self.verify(changed=lambda d,k=key,v=value: d.__setitem__(k,v))

    def test_03_recovery_body_mutations_rejected(self):
        for key, value in (("enabled",False), ("published",False),
                           ("stateCode",True), ("terminalFailureCode",0),
                           ("reason",""), ("disposition","ActiveShadow"),
                           ("retainedBytes",-1),
                           ("baselineEligibilityRequiresStartupValidation",0)):
            with self.subTest(key=key), self.assertRaises(RecoveryRejected):
                self.verify(changed=lambda d,k=key,v=value:
                            d["nativeRecovery"].__setitem__(k,v))

    def test_04_missing_extra_duplicate_and_truncated_rejected(self):
        data, _ = fixture()
        correct = (json.dumps(data) + "\n").encode()
        cases = [
            correct[:-1], correct + b"{}\n", correct + b" " * 25000,
            correct.replace(b'"reason":', b'"reason":null,"reason":', 1),
            correct.replace(b'"schemaVersion": 1', b'"schemaVersion": NaN', 1),
        ]
        for raw in cases:
            with self.subTest(size=len(raw)), self.assertRaises((RecoveryRejected, ValueError)):
                self.verify(payload=raw)
        with self.assertRaises(RecoveryRejected):
            self.verify(changed=lambda d: d["nativeRecovery"].update(extra="x"))

    def test_05_real_reason_is_recoverable_without_managed_formatter(self):
        report = self.verify()
        self.assertIn("module initializer exception", report["vmReason"])
        self.assertIs(report["nativeV2TransportImplemented"], False)
        self.assertIs(report["completeDiagnosticsAuthenticated"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
