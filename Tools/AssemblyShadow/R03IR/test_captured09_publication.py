#!/usr/bin/env python3
"""Real oneuse09 published checkpoint and adversarial no-write source mutations.

No Unity/Player execution, no restoration of retired roots, no V2 or stage
approval; mutation inputs are memory-only and never overwrite evidence files.
"""
from __future__ import annotations
import copy
import json
from pathlib import Path
import unittest

from captured09_publication_audit import (
    CHECKPOINT, PINS, PIDS, PublishedAuditRejected, verify,
)


def encoded(value):
    return (json.dumps(value, separators=(",", ":"), sort_keys=True) + "\n").encode()


class Captured09PublicationContracts(unittest.TestCase):
    def reject(self, relative, mutate):
        original = json.loads((CHECKPOINT / relative).read_bytes())
        altered = copy.deepcopy(original)
        mutate(altered)
        with self.assertRaises((ValueError, KeyError, TypeError, IndexError, OSError)):
            verify(overrides={relative: encoded(altered)})

    def test_01_actual_original_raw_crosscheck(self):
        result = verify()
        self.assertEqual(result["result"],
             "PassedPublishedBoundedRawCrossCheck_NotUnityV2OrR03Acceptance")
        self.assertEqual(result["cells"], 19)
        self.assertEqual(result["sourcePins"], PINS)
        self.assertEqual(result["verifiedCIRuns"], 7)
        self.assertEqual(result["players"]["captured-generic"]["firstError"], 15)
        self.assertEqual(result["players"]["initializer-control"]["commit"], 0)
        self.assertEqual(result["players"]["initializer-failure"]["commit"], 19)
        for key in ("originalPhysicalGameAssemblyRehashed",
                    "fullProductSealArchiveRehashed",
                    "originalNativeV2ProducerPresent",
                    "firstExceptionTypeIdentified", "wholeVmEpochAuthenticated",
                    "runtimeAcceptance", "R03Accepted", "H2Passed",
                    "ReadyForHumanReviewGate"):
            self.assertIs(result[key], False)

    def test_02_source_provenance_drift(self):
        self.reject("LOCAL_RESULT.json", lambda j: j["sourcePins"].update(hybridclr_demo="0"*40))

    def test_03_original_cell_scope_cannot_gain_or_lose(self):
        self.reject("LOCAL_RESULT.json", lambda j: j["cellStates"].update(fake="Passed"))
        self.reject("LOCAL_RESULT.json", lambda j: j["cellStates"].update({"player-captured-generic":"NotRun"}))
        self.reject("LOCAL_RESULT.json", lambda j: j["cellCounts"].update(Passed=18))

    def test_04_original_runner_exactly_once(self):
        self.reject("LOCAL_RESULT.json", lambda j: j["runner"].update(runnerInvocations=2))
        self.reject("LOCAL_RESULT.json", lambda j: j["runner"].update(retryPerformed=True))

    def test_05_no_false_audit_acceptance(self):
        self.reject("local-evidence/FINAL_INDEPENDENT_AUDIT.json", lambda j: j.update(R03Accepted=True))
        self.reject("batch/LOCAL_BATCH_RESULT.json", lambda j: j.update(nativeV2TransportImplemented=True))
        self.reject("batch/LOCAL_BATCH_RESULT.json", lambda j: j.update(wholeVmEpoch="Proven"))

    def test_06_original_product_members_and_custody(self):
        self.reject("LOCAL_RESULT.json", lambda j: j["seal"].update(members=508))
        self.reject("batch/seal-receipt.json", lambda j: j.update(indexSha256="0"*64))
        self.reject("LOCAL_RESULT.json", lambda j: j["hostCustody"].update(symlinkCount=3))

    def test_07_original_build_receipt_digest_warning_and_bridge(self):
        p = "batch/builds/candidate-release/build-receipt.json"
        self.reject(p, lambda j: j.update(warnings=0))
        self.reject(p, lambda j: j.update(initializerBridgeGeneratedSha256="0"*64))
        self.reject(p, lambda j: j.update(initializerBridgeLinkedRuntimeObserved=True))

    def test_08_initializer_control_not_relabeled_failure(self):
        p = "batch/players/IR-R03-02-initializer-control/raw.json"
        self.reject(p, lambda j: j.update(commitReturn=19))
        self.reject(p, lambda j: j.update(initializerCallbackCalls=0))

    def test_09_initializer_failure_not_relabeled_control(self):
        p = "batch/players/IR-R03-02-initializer-failure/raw.json"
        self.reject(p, lambda j: j.update(finalState=6))
        self.reject(p, lambda j: j.update(positiveMask=0))

    def test_10_initializer_original_callback_phase_order(self):
        p = "batch/players/IR-R03-02-initializer-control/raw.json.native-trace.jsonl"
        raw = (CHECKPOINT / p).read_bytes()
        with self.assertRaises((ValueError, KeyError, TypeError, IndexError, OSError)):
            verify(overrides={p: raw.splitlines(keepends=True)[0] + raw})

    def test_11_initializer_linked_bi4_signal_is_required(self):
        p = "batch/players/IR-R03-02-initializer-failure/raw.json.native-trace.jsonl"
        entries = [json.loads(row) for row in (CHECKPOINT / p).read_bytes().splitlines()]
        changed = 0
        for row in entries:
            if row.get("phase") == 103:
                row["a"] = 0
                changed += 1
        self.assertEqual(changed, 1)
        with self.assertRaises((ValueError, KeyError, TypeError, IndexError, OSError)):
            verify(overrides={p: b"".join(encoded(r) for r in entries)})

    def test_12_initializer_native_first_recovery_not_fabricated(self):
        p = "batch/players/IR-R03-02-initializer-failure/raw.json.vm-recovery.json"
        self.reject(p, lambda j: j["nativeRecovery"].update(reason="wrong sentinel"))
        self.reject(p, lambda j: j["nativeRecovery"].update(terminalFailureCode=15))

    def test_13_captured_guard_reason_not_error13_or21(self):
        p = "batch/players/IR-R03-02-captured-generic/raw.json"
        self.reject(p, lambda j: j["nativeRecovery"].update(terminalFailureCode=13))
        self.reject(p, lambda j: j["nativeRecovery"].update(terminalFailureCode=21))
        self.reject(p, lambda j: j["nativeRecovery"].update(reason="BaselineMethodExecution"))

    def test_14_captured_physical_context_is_mandatory(self):
        p = "batch/players/IR-R03-02-captured-generic/raw.json"
        self.reject(p, lambda j: j.update(methodContextPhysical=False))
        self.reject(p, lambda j: j.update(methodInflated=False))
        self.reject(p, lambda j: j.update(ownerAssembly="Methods"))
        self.reject(p, lambda j: j.update(physicalTypeIndex=True))

    def test_15_postterminal_must_observe_real_exception_and_no_body(self):
        p = "batch/players/IR-R03-02-captured-generic/raw.json"
        self.reject(p, lambda j: j.update(runtimeInvokeThrew=False))
        self.reject(p, lambda j: j.update(runtimeInvokeSucceeded=True))
        self.reject(p, lambda j: j.update(afterCount=2))

    def test_16_failure_pid_and_nonce_crossjoin(self):
        p = "batch/players/IR-R03-02-captured-generic/request.json"
        self.reject(p, lambda j: j.update(runId="0"*32))
        self.reject(p, lambda j: j.update(dllSha256="0"*64))

    def test_17_actual_os_command_failure_is_not_success(self):
        self.reject("batch/commands/0028/command.json", lambda j: j.update(exitCode=2))
        self.reject("batch/commands/0028/command.json", lambda j: j.update(pid=PIDS["initializer-control"]))
        self.reject("batch/commands/0028/command.json", lambda j: j.update(timeout=True))

    def test_18_false_captured_sha_or_mvid(self):
        self.reject("LOCAL_RESULT.json", lambda j: j["capturedTarget"].update(sha256="0"*64))
        self.reject("LOCAL_RESULT.json", lambda j: j["capturedTarget"].update(size=2048))

    def test_19_old_inconsistent_CI_status_never_waived(self):
        self.reject("local-evidence/CI_VALIDATOR.json",
                    lambda j: j.update(oldInconsistentJobWaived=True))
        p = "local-evidence/captured-generic-09-prerequisite-CI.json"
        original = json.loads((CHECKPOINT / p).read_bytes())
        row = original["jobs"]["42556202588"]["jobs"][0]
        self.assertIn("ubuntu-24.04", row["name"])
        row["status"] = "in_progress"
        with self.assertRaises((ValueError, KeyError, TypeError, IndexError, OSError)):
            verify(overrides={p: encoded(original)})

    def test_20_duplicate_json_key_in_actual_evidence_is_rejected(self):
        p = "batch/players/IR-R03-02-captured-generic/raw.json"
        data = (CHECKPOINT / p).read_bytes()
        altered = data.replace(b'"schemaVersion":1,',
                               b'"schemaVersion":1,"schemaVersion":1,', 1)
        self.assertNotEqual(data, altered)
        with self.assertRaises((ValueError, KeyError, TypeError, IndexError, OSError)):
            verify(overrides={p: altered})

    def test_21_original_published_bytes_and_mtime_unchanged(self):
        p = CHECKPOINT / "batch/players/IR-R03-02-captured-generic/raw.json"
        before = p.read_bytes(), p.stat().st_mtime_ns
        verify()
        self.assertEqual((p.read_bytes(), p.stat().st_mtime_ns), before)

    def test_22_relative_or_missing_evidence_root_is_rejected(self):
        with self.assertRaises(PublishedAuditRejected):
            verify(Path("not-a-canonical-published-root"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
