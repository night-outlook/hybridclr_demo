"""Candidate preservation and native first-failure decoding. No Unity execution."""
from pathlib import Path
import hashlib
import re
import unittest
from classify_snapshot_failure import classify

H = Path(__file__).resolve().parent

class NativeFailureClassification(unittest.TestCase):
    def setUp(self):
        self.line = b'[R03SnapshotFailure] version=1 pid=321 operation=text field=15 reason=9 previousState=1 length=262145 limit=262144 errno=0 intMask=01ffffff textMask=00007fff\n'

    def read(self, data=None, pid=321):
        data = self.line if data is None else data
        return classify(data, pid, hashlib.sha256(data).hexdigest())

    def test_exact_prefix_not_claimed_full_length(self):
        r = self.read()
        self.assertEqual(r['firstFailure']['slot'], 15)
        self.assertFalse(r['firstFailure']['fullLengthKnown'])
        self.assertFalse(r['runtimeAcceptance'])

    def test_missing_failure_is_not_acceptance(self):
        r = self.read(b'[R03SnapshotSealed] version=1 pid=321 intMask=01ffffff textMask=0000ffff\n')
        self.assertIsNone(r['firstFailure'])
        self.assertEqual(r['semanticVerification'], 'SeparateOriginalRawVerifierRequired')
        self.assertFalse(r['runtimeAcceptance'])

    def test_pid_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, 'PID mismatch'): self.read(pid=322)

    def test_hash_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            classify(self.line, 321, '0' * 64)

    def test_multiple_first_failures_rejected(self):
        with self.assertRaisesRegex(ValueError, 'More than one'): self.read(self.line * 2)

    def test_malformed_line_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Malformed'): self.read(self.line.replace(b'field=15 ', b''))

    def test_changed_limit_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Changed scan bound'):
            self.read(self.line.replace(b'limit=262144', b'limit=524288'))

    def test_invalid_negative_slot_is_preserved_as_diagnostic(self):
        data = self.line.replace(b'field=15 reason=9', b'field=-2 reason=6')
        result = self.read(data)
        self.assertEqual(result['firstFailure']['slot'], -2)
        self.assertEqual(result['firstFailure']['reason'], 'InvalidSlotIndex')
        self.assertFalse(result['runtimeAcceptance'])

    def test_unknown_reason_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unknown'): self.read(self.line.replace(b'reason=9 ', b'reason=99 '))

    def test_out_of_schema_mask_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Out-of-schema'):
            self.read(self.line.replace(b'intMask=01ffffff', b'intMask=ffffffff'))

    def test_packed_integrity_failure_is_not_a_size_or_semantic_pass(self):
        data=self.line.replace(b'operation=text field=15 reason=9',b'operation=packed-text field=15 reason=17').replace(b'length=262145',b'length=0')
        r=self.read(data)
        self.assertEqual(r['firstFailure']['reason'], 'PackedTextIntegrityFailed')
        self.assertFalse(r['runtimeAcceptance'])

    def test_original_aggregate_budget_failure_remains_failure(self):
        data=self.line.replace(b'operation=text field=15 reason=9',b'operation=text-budget field=15 reason=18').replace(b'length=262145',b'length=4194305')
        r=self.read(data)
        self.assertEqual(r['firstFailure']['wholeUnescapedReportLimit'],4194304)
        self.assertFalse(r['firstFailure']['fullLengthKnown'])

if __name__=='__main__':unittest.main()
