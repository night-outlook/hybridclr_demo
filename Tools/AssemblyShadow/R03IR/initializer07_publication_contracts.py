#!/usr/bin/env python3
"""Read-only published oneuse-07 source/receipt test plus negative mutations."""
import json
from pathlib import Path
import unittest
from initializer07_publication_audit import CHECKPOINT, AuditRejected, verify


def bytes_json(v):
    return (json.dumps(v, sort_keys=True) + "\n").encode("utf-8")


class Oneuse07PublishedContracts(unittest.TestCase):
    def reject_mutated(self, relative, mutate):
        raw = json.loads((CHECKPOINT / relative).read_text(encoding="utf-8"))
        mutate(raw)
        with self.assertRaises((ValueError, KeyError, TypeError, IndexError, OSError)):
            verify(overrides={relative: bytes_json(raw)})

    def test_01_original_published_record(self):
        result = verify()
        self.assertEqual(result["result"],
                         "PassedPublishedRecordCrossCheck_NotRuntimeOrV2Acceptance")
        self.assertEqual(result["cells"], 15)
        self.assertEqual(result["players"]["initializer-control"]["commit"], 0)
        self.assertEqual(result["players"]["initializer-failure"]["commit"], 19)
        for k in ("physicalGameAssemblyRehashed", "fullProductArchiveRehashed",
                  "capturedGeneric15Executed", "nativeV2TransportAuthenticated",
                  "R03Accepted", "ReadyForHumanReviewGate"):
            self.assertIs(result[k], False)

    def test_02_bad_exact_source(self):
        self.reject_mutated("LOCAL_RESULT.json",
                            lambda v: v["sourcePins"].update(hybridclr_demo="0" * 40))

    def test_03_wrong_cell(self):
        self.reject_mutated("LOCAL_RESULT.json",
                            lambda v: v["cellStates"].update(fake="Passed"))

    def test_04_forged_cell_count(self):
        self.reject_mutated("LOCAL_RESULT.json",
                            lambda v: v["cellCounts"].update(Passed=14))

    def test_05_replay(self):
        self.reject_mutated("LOCAL_RESULT.json",
                            lambda v: v["runner"].update(runnerInvocations=2))

    def test_06_forged_audit_acceptance(self):
        self.reject_mutated("local-evidence/FINAL_INDEPENDENT_AUDIT.json",
                            lambda v: v.update(R03Accepted=True))

    def test_07_wrong_independent_members(self):
        self.reject_mutated("local-evidence/FINAL_INDEPENDENT_AUDIT.json",
                            lambda v: v.update(archiveMembers=457))

    def test_08_host_custody_change(self):
        self.reject_mutated("LOCAL_RESULT.json",
                            lambda v: v["hostCustody"].update(symlinkCount=3))

    def test_09_build_warning_changed(self):
        self.reject_mutated("batch/builds/candidate-release/build-receipt.json",
                            lambda v: v.update(warnings=0))

    def test_10_bridge_codegen_changed(self):
        self.reject_mutated("batch/builds/candidate-release/build-receipt.json",
                            lambda v: v.update(initializerBridgeGeneratedSha256="0" * 64))

    def test_11_fake_runtime_linked_claim(self):
        self.reject_mutated("batch/builds/candidate-release/build-receipt.json",
                            lambda v: v.update(initializerBridgeLinkedRuntimeObserved=True))

    def test_12_bad_control_commit(self):
        self.reject_mutated("batch/players/IR-R03-02-initializer-control/raw.json",
                            lambda v: v.update(commitReturn=19))

    def test_13_bad_failure_callback(self):
        self.reject_mutated("batch/players/IR-R03-02-initializer-failure/raw.json",
                            lambda v: v.update(initializerCallbackCalls=0))

    def test_14_wrong_fixture(self):
        self.reject_mutated("batch/players/IR-R03-02-initializer-failure/request.json",
                            lambda v: v.update(dllSha256="0" * 64))

    def test_15_wrong_terminal_reason(self):
        self.reject_mutated("batch/players/IR-R03-02-initializer-failure/raw.json.vm-recovery.json",
                            lambda v: v["nativeRecovery"].update(reason="incorrect reason"))

    def test_16_nonzero_process_exit(self):
        self.reject_mutated("batch/commands/0018/command.json",
                            lambda v: v.update(exitCode=2))

    def test_17_duplicate_os_pid(self):
        self.reject_mutated("batch/commands/0019/command.json",
                            lambda v: v.update(pid=35820))

    def test_18_duplicate_native_phase(self):
        p = "batch/players/IR-R03-02-initializer-control/raw.json.native-trace.jsonl"
        data = (CHECKPOINT / p).read_bytes()
        with self.assertRaises((ValueError, KeyError, TypeError, IndexError, OSError)):
            verify(overrides={p: data.splitlines(keepends=True)[0] + data})

    def test_19_failed_linked_Bi4(self):
        p = "batch/players/IR-R03-02-initializer-failure/raw.json.native-trace.jsonl"
        data = [json.loads(x) for x in (CHECKPOINT / p).read_bytes().splitlines()]
        for row in data:
            if row["phase"] == 103:
                row["a"] = 0
        with self.assertRaises((ValueError, KeyError, TypeError, IndexError, OSError)):
            verify(overrides={p: b"".join(bytes_json(row) for row in data)})

    def test_20_duplicate_json_key(self):
        p = "LOCAL_RESULT.json"
        data = (CHECKPOINT / p).read_bytes()
        corrupted = data.replace(b'"result": "PASS",',
                                 b'"result": "PASS", "result": "PASS",', 1)
        self.assertNotEqual(corrupted, data)
        with self.assertRaises((ValueError, KeyError, TypeError, IndexError, OSError)):
            verify(overrides={p: corrupted})

    def test_21_no_published_input_mutation(self):
        p = CHECKPOINT / "LOCAL_RESULT.json"
        before = (p.stat().st_mtime_ns, p.read_bytes())
        verify()
        self.assertEqual((p.stat().st_mtime_ns, p.read_bytes()), before)

    def test_22_relative_checkpoint_rejected(self):
        with self.assertRaises(AuditRejected):
            verify(Path("noncanonical-relative"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
