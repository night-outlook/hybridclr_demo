#!/usr/bin/env python3
"""Host-only real Python command-failure evidence, with no Unity/Player invoked."""
from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest

from run_terminal_local import player, sha


class FakeFailedBatch:
    def __init__(self, root: Path, add_raw: bool):
        self.root = root
        (root / "players").mkdir(parents=True)
        fixture = root / "target.dll"
        receipt = root / "target-receipt.json"
        fixture.write_bytes(b"host-only-not-an-assembly")
        receipt.write_text('{"result":"GeneratedNotRuntimeValidated"}')
        self.ir_target = {
            "path": fixture, "sha256": sha(fixture),
            "receipt": receipt, "receiptSha256": sha(receipt),
        }
        self.builds = {"candidate-release": {"executable": root / "fake-executable"}}
        self.add_raw = add_raw
        self.invocations = 0

    def verify_build(self, role):
        assert role == "candidate-release"

    def command(self, argv, timeout):
        self.invocations += 1
        assert timeout == 180
        assert "-r03IrOutput" in argv
        raw = Path(argv[argv.index("-r03IrOutput") + 1])
        if self.add_raw:
            raw.write_bytes(b"")
            raw.with_name(raw.name + ".general.json").write_bytes(b'{"incomplete":true}')
        raise RuntimeError("Real command simulated nonzero; verifier must remain NotRun")


class FailedPlayerReceiptContracts(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory(prefix="r03-failed-player-receipt-")
        self.addCleanup(t.cleanup)
        self.root = Path(t.name).resolve()

    def check(self, with_partial=False):
        batch = FakeFailedBatch(self.root, with_partial)
        case = {"id": "IR-R03-02-release-baseline", "role": "candidate-release",
                "stimulus": "baseline-owner"}
        with self.assertRaisesRegex(RuntimeError, "simulated nonzero"):
            player(batch, case)
        self.assertEqual(batch.invocations, 1)
        path = batch.root / "players" / case["id"] / "verification.json"
        self.assertTrue(path.is_file())
        report = json.loads(path.read_text())
        self.assertEqual(report["result"], "Failed")
        self.assertEqual(report["semanticVerifierStatus"], "NotRun_CommandFailed")
        self.assertIs(report["R03Accepted"], False)
        self.assertIs(report["runtimeAcceptance"], False)
        self.assertEqual(report["caseId"], case["id"])
        self.assertEqual(report["stimulus"], case["stimulus"])
        self.assertEqual(len(report["requestSha256"]), 64)
        return report

    def test_01_no_raw_is_factual_failure_not_semantic_pass(self):
        result = self.check()
        self.assertIs(result["rawExists"], False)
        self.assertIsNone(result["rawSha256"])
        self.assertIs(result["fullGeneralSidecarExists"], False)

    def test_02_empty_raw_and_unverified_sidecar_are_preserved(self):
        result = self.check(with_partial=True)
        self.assertIs(result["rawExists"], True)
        self.assertEqual(result["rawBytes"], 0)
        self.assertIs(result["fullGeneralSidecarExists"], True)
        self.assertEqual(result["fullGeneralSidecarBytes"], len(b'{"incomplete":true}'))
        self.assertNotIn("completeGeneralDiagnostic", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
