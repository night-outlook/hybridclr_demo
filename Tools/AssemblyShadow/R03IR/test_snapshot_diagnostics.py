"""Actual bounded native writer/emitter and diagnostic integrity; not Unity evidence."""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from snapshot_diagnostics import classify
from snapshot_transport_harness import run_tests

ROOT = Path(__file__).resolve().parents[1]


class SnapshotDiagnosticContracts(unittest.TestCase):
    def setUp(self):
        self.line = b'[R03SnapshotFailure] version=1 pid=321 operation=text field=15 reason=9 previousState=1 length=262145 limit=262144 errno=0 intMask=01ffffff textMask=00007fff\n'

    def classify(self, data=None, pid=321):
        data = self.line if data is None else data
        return classify(data, pid, hashlib.sha256(data).hexdigest())

    def test_oversize_is_prefix_not_full_length(self):
        result = self.classify()
        self.assertEqual(result['firstFailure']['slot'], 15)
        self.assertEqual(result['firstFailure']['lengthMeaning'], 'ScannedPrefixOnly')
        self.assertFalse(result['firstFailure']['fullLengthKnown'])
        self.assertFalse(result['runtimeAcceptance'])

    def test_unmeasured_length_is_not_claimed(self):
        result = self.classify(self.line.replace(b'reason=9', b'reason=7').replace(b'length=262145', b'length=0'))
        self.assertFalse(result['firstFailure']['fullLengthKnown'])
        self.assertEqual(result['firstFailure']['lengthMeaning'], 'NotMeasured')

    def test_no_failure_is_not_a_semantic_pass(self):
        result = self.classify(b'[R03SnapshotSealed] version=1 pid=321 intMask=01ffffff textMask=0000ffff\n')
        self.assertIsNone(result['firstFailure'])
        self.assertFalse(result['runtimeAcceptance'])
        self.assertEqual(result['semanticVerification'], 'SeparateOriginalRawVerifierRequired')

    def test_pid_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'PID mismatch'):
            self.classify(pid=999)

    def test_log_hash_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            classify(self.line, 321, '0' * 64)

    def test_duplicate_first_failure_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'More than one'):
            self.classify(self.line * 2)

    def test_malformed_failure_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Malformed'):
            self.classify(self.line.replace(b'field=15 ', b''))

    def test_changed_bound_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Changed scan bound'):
            self.classify(self.line.replace(b'limit=262144', b'limit=524288'))

    def test_invalid_slot_is_diagnostic_not_accepted(self):
        result = self.classify(self.line.replace(b'field=15 reason=9', b'field=-2 reason=6'))
        self.assertEqual(result['firstFailure']['slot'], -2)
        self.assertFalse(result['runtimeAcceptance'])

    def test_unknown_reason_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            self.classify(self.line.replace(b'reason=9', b'reason=99'))

    def test_outside_schema_mask_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Out-of-schema'):
            self.classify(self.line.replace(b'intMask=01ffffff', b'intMask=ffffffff'))

    def test_original_managed_witness_except_seal_sequence_is_unchanged(self):
        data = (ROOT/'R03IR/PlayerProject/R03TerminalPlayer.cs').read_text()
        new = '''            // Call Seal even after a rejected store, so native failure state is
            // observed. It must never seal a failed/missing/duplicate field set.
            int seal = R03_IR_ReportSeal();
            return ok && seal == 1;'''
        old = '            return ok && R03_IR_ReportSeal() == 1;'
        self.assertEqual(data.count(new), 1)
        self.assertEqual(hashlib.sha256(data.replace(new, old).encode()).hexdigest(),
                         'e06face7827175c759de30b6c2de1424308a46e45ef1e1525f26b5084f47d94f')

    def test_native_non_writer_functions_are_unchanged(self):
        data = (ROOT/'R03/PlayerProject/AssemblyShadowR03Probe.cpp').read_text()
        before = data[:data.index('namespace r03_ir_snapshot {')].replace('#include <cerrno>\n', '')
        after = data[data.index('extern "C" IL2CPP_EXPORT void R03_IR_Exit'):]
        self.assertEqual(hashlib.sha256(before.encode()).hexdigest(),
                         '950e53edf5d23f2c6f01c019a3f5d8a5fd0938654aeab86e0bf0ca5b48478afb')
        self.assertEqual(hashlib.sha256(after.encode()).hexdigest(),
                         '3fa2c5894f79600f6354951c527238a669c05c99e0d5b2c1d67dca82a0eae068')

    def test_actual_writer_and_complete_native_emitter(self):
        self.assertTrue(__debug__, 'Tests must not run under Python -O')
        flags = ['-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if os.environ.get('R03_SANITIZERS') == '1' else []
        label = 'sanitized' if flags else 'strict'
        output = os.environ.get('R03_SNAPSHOT_TEST_EVIDENCE')
        if output:
            result = run_tests(Path(output), [(label, flags)])
        else:
            with tempfile.TemporaryDirectory() as temporary:
                result = run_tests(Path(temporary).resolve(strict=True)/'evidence', [(label, flags)])
        self.assertEqual(result['scenarioCountPerProfile'], 26)
        self.assertEqual(result['compilerProcessRecords'], 27)
        self.assertFalse(result['NRootCauseProven'])
        self.assertEqual(result['boundsUnchanged'], {'textPerSlot':262144,'intFields':25,'textFields':16})


if __name__ == '__main__':
    unittest.main()
