#!/usr/bin/env python3
"""Host-only contracts for the new one-use initializer Local runner.

Synthetic native records are deliberately NOT Player execution or acceptance.
"""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import run_initializer_local as cycle
from test_initializer_observation import fixture as raw_fixture
from verify_initializer_observation import Rejected
from test_initializer_trace import fixture as native_trace_fixture, encode as native_trace_encode
from test_initializer_recovery import fixture as native_recovery_fixture


class FakeInitializerBatch:
    def __init__(self, root: Path, mode: str, corrupt=None):
        self.root, self.mode, self.corrupt = root, mode, corrupt
        self.pid, self.call_count = 3187, 0
        self.command_count = 0
        (root / "target").mkdir()
        (root / "build").mkdir()
        (root / "project").mkdir()
        self.dll = root / "target/Methods.dll"
        self.dll.write_bytes(b"isolated-host-synthetic-target-not-real-methods")
        self.initializer_targets = {mode: self.dll}
        self.initializer_target_report = root / "target/fixture.json"
        self.initializer_target_report.write_text('{"source":"synthetic"}\n')
        self.target_receipt_sha = cycle.sha(self.initializer_target_report)
        executable = root / "build/Player"
        executable.write_bytes(b"host fake only")
        (root / "build/build-receipt.json").write_text('{"kind":"fake"}\n')
        (root / "project/source-inputs.json").write_text('{"kind":"fake"}\n')
        self.builds = {"candidate-release": {
            "executable": executable, "root": root / "build",
            "project": root / "project",
            "config": {"overlaySha256": "c" * 64}
        }}

    def verify_build(self, role):
        if role != "candidate-release":
            raise ValueError("Wrong role")

    def command(self, argv, timeout):
        self.call_count += 1
        self.command_count += 1
        request = json.loads(Path(argv[argv.index("-r03IrInitializerRequest") + 1]).read_text())
        raw, _, _, _ = raw_fixture(self.mode)
        raw["runId"] = request["runId"]
        raw["caseId"] = request["caseId"]
        raw["fixtureSha256"] = request["dllSha256"]
        raw["processId"] = self.pid
        if self.corrupt == "pid":
            raw["processId"] += 1
        if self.corrupt == "postAot":
            raw["postAotSucceeded"] = True
        if self.corrupt == "canary":
            raw["finalField"] = 4
        out = Path(argv[argv.index("-r03IrInitializerOutput") + 1])
        traces, _ = native_trace_fixture(self.mode)
        for row in traces:
            row["runId"] = request["runId"]
            row["caseId"] = request["caseId"]
            row["fixtureSha256"] = request["dllSha256"]
            row["pid"] = self.pid
        if self.corrupt == "trace-pid":
            traces[2]["pid"] = self.pid + 1
        if self.corrupt == "recovery-wrong-reason":
            raw["postAotSucceeded"] = False
        if self.corrupt == "exit":
            # Synthetic reproduction of a real native seal failure. The
            # command returns nonzero, raw remains exactly empty, but a
            # preopened diagnostic journal can still be authenticated.
            traces = traces[:4]
            traces[-1]["a"] = -7
            traces.append(dict(traces[-1], seq=5, phase=900, a=190))
            traces.append(dict(traces[-1], seq=6, phase=610, a=-2, b=3))
            out.write_bytes(b"")
            receipt = self.root / "commands" / ("%04d" % self.command_count)
            receipt.mkdir(parents=True)
            (receipt / "command.json").write_text(json.dumps({
                "pid": self.pid, "exitCode": 2}) + "\n")
        else:
            out.write_text(json.dumps(raw, separators=(",", ":")) + "\n")
        if self.corrupt != "trace-missing":
            (Path(str(out) + ".native-trace.jsonl")).write_bytes(
                native_trace_encode(traces))
        if self.corrupt != "recovery-missing":
            recovery, _ = native_recovery_fixture(self.mode)
            recovery["runId"] = request["runId"]
            recovery["caseId"] = request["caseId"]
            recovery["fixtureSha256"] = request["dllSha256"]
            recovery["processId"] = self.pid + (1 if self.corrupt == "recovery-pid" else 0)
            if self.corrupt == "recovery-wrong-reason":
                recovery["nativeRecovery"]["reason"] = "Methods: unrelated initializer exception"
            Path(str(out) + ".vm-recovery.json").write_bytes(
                (json.dumps(recovery, sort_keys=True) + "\n").encode())
        if self.corrupt == "exit":
            raise RuntimeError("Synthetic nonzero native Player exit")
        return {"pid": self.pid}


class InitializerLocalOrchestrationTests(unittest.TestCase):
    def run_case(self, mode, corrupt=None):
        with tempfile.TemporaryDirectory(prefix="r03-init-local-contract-") as temp:
            batch = FakeInitializerBatch(Path(temp), mode, corrupt)
            with patch.dict(cycle.MODE_SHA, {mode: (cycle.sha(batch.dll), "not-a-real-mvid")}):
                if corrupt is None:
                    result = cycle.init_player(batch, mode)
                    self.assertEqual(result["result"],
                                     "PassedFocusedV1PlayerObservation_NotV2")
                    self.assertIs(result["R03Accepted"], False)
                    self.assertIs(result["runtimeAcceptance"], False)
                    self.assertIs(result["H2Passed"], False)
                    self.assertEqual(result["launchPid"], batch.pid)
                    self.assertEqual(result["targetGeneratorReceiptSha256"],
                                     batch.target_receipt_sha)
                    self.assertEqual(batch.call_count, 1)
                    self.assertEqual(result["nativeDiagnostic"]["result"],
                                     "CompletePhaseTrace_NotRuntimeAuthenticated")
                    self.assertEqual(result["nativeDiagnostic"]["vmRecovery"]["result"],
                                     "ParsedNativeVMFirstFailure_NotRuntimeAuthenticated")
                else:
                    with self.assertRaises((Rejected, ValueError, RuntimeError)):
                        cycle.init_player(batch, mode)
                    evidence = batch.root / "players" / ("IR-R03-02-" + mode)
                    result = json.loads((evidence / "verification.json").read_text())
                    self.assertEqual(result["result"], "Failed")
                    self.assertIs(result["R03Accepted"], False)
                    self.assertEqual(batch.call_count, 1)
                    self.assertTrue((evidence / "request.json").exists())
                    if corrupt == "exit":
                        self.assertEqual(result["semanticVerifierStatus"],
                                         "NotRun_CommandFailed")
                        self.assertEqual(result["nativeDiagnostic"]["result"],
                                         "BoundedTraceObserved_NotRuntimeAuthenticated")
                        self.assertEqual(result["nativeDiagnostic"]["nativeCallbackFailures"], [-7])
                        self.assertEqual((evidence / "raw.json").stat().st_size, 0)
                        self.assertEqual(result["launchPidFromOwnedReceipt"], batch.pid)
                        self.assertIn("nativeDiagnostic", result)
                        self.assertEqual(result["nativeDiagnostic"]["vmRecovery"]["stateCode"],
                                         6 if mode == "initializer-control" else 9)
                    else:
                        self.assertTrue((evidence / "raw.json").exists())

    def test_two_distinct_real_run_contracts_have_synthetic_positive(self):
        for mode in cycle.MODE_SHA:
            with self.subTest(mode=mode):
                self.run_case(mode)

    def test_pid_and_native_state_mutations_fail_closed(self):
        for mode in cycle.MODE_SHA:
            for corrupt in ("pid", "postAot", "canary", "exit",
                            "trace-missing", "trace-pid", "recovery-missing", "recovery-pid",
                            "recovery-wrong-reason"):
                with self.subTest(mode=mode, corrupt=corrupt):
                    self.run_case(mode, corrupt)

    def test_explicit_oneuse_scope_excludes_unsupported_claims(self):
        source = Path(cycle.__file__).read_text(encoding="utf-8")
        for explicit in (
            '"capturedGenericFailure": "NotRun"',
            '"completeNativeSnapshotV2": "NotImplemented_NotRun"',
            '"wholeVmEpoch": "NotProven"',
            '"managedShutdown": "NotProven"',
        ):
            self.assertIn(explicit, source)
        self.assertEqual(set(cycle.MODE_SHA),
                         {"initializer-control", "initializer-failure"})
        self.assertIn("R03InitializerCompositeOverlay.cpp", source)

    def test_new_runner_does_not_relabel_historical_k(self):
        source = Path(cycle.__file__).read_text(encoding="utf-8")
        self.assertNotIn('def execute_current_native', source)
        self.assertNotIn('R03IRPostPoisonEntryV1', source)
        self.assertIn('validate_sources(workspace, demo_commit)', source)
        self.assertIn('batch.cell("final-authority"', source)
        self.assertIn('R03IRInitializerOneUseEvidenceBatchV1', source)
        self.assertIn('verify_current_host_report(', source)
        self.assertIn('"tenCurrentNativeHostResultSha256"', source)
        self.assertIn('capture_host(output, batch.root / "host-custody")', source)
        self.assertIn('"nativeDiagnostic"', source)
        self.assertIn('Passed59ArchivedProcessJoinsOnly', source)
        self.assertIn('Exact new non-replayed 15-cell roster', source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
