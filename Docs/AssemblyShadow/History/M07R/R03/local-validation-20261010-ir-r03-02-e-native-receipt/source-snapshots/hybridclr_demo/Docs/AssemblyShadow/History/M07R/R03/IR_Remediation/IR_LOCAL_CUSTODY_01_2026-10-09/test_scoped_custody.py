"""Synthetic negative controls for the exact-loss, read-only custody verifier."""
from pathlib import Path
import tempfile
import unittest
from verify_scoped_custody import (
    AdmissionError, C_BLOBS, C_RECEIPT_GIT_BLOBS, EXPECTED_FILES,
    EXPECTED_MISSING, audit_exact, authenticated_c_receipt,
    authenticated_json, error_pairs, load_frozen_c, require,
    verify_pinned_receipt_constants,
)


class ScopedCustodyUnitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.good = self.root / 'good.txt'
        self.other = self.root / 'other.txt'
        self.absent = self.root / 'missing.bin'
        self.good.write_bytes(b'good')
        self.other.write_bytes(b'other')
        import hashlib
        self.orig = {str(self.good): hashlib.sha256(self.good.read_bytes()).hexdigest(),
                     str(self.other): hashlib.sha256(self.other.read_bytes()).hexdigest(),
                     str(self.absent): '0'*64}
        self.frozen = {str(self.absent): '0'*64}

    def test_unchanged_historical_loss_is_scoped_only(self):
        r = audit_exact(self.orig, self.frozen)
        self.assertEqual(r['result'], 'ScopedHistoricalLossStable')
        self.assertEqual(r['originalStrictCustody'], 'Blocked')
        self.assertEqual((r['presentVerified'], r['historicalStillMissing']), (2, 1))
        self.assertTrue(r['completeScan'])

    def test_changed_survivor_blocks(self):
        self.good.write_bytes(b'changed')
        self.assertEqual(audit_exact(self.orig, self.frozen)['result'], 'Blocked')

    def test_additional_missing_blocks(self):
        self.other.unlink()
        r = audit_exact(self.orig, self.frozen)
        self.assertEqual(r['result'], 'Blocked')
        self.assertEqual(r['problems'][0]['kind'], 'NewMissing')

    def test_restoring_originally_missing_requires_primary_review(self):
        self.absent.write_bytes(b'restored')
        r = audit_exact(self.orig, self.frozen)
        self.assertEqual(r['result'], 'Blocked')
        self.assertEqual(r['problems'][0]['kind'], 'UnexpectedRestorationNeedsPrimaryReview')

    def test_symlink_replacement_blocks(self):
        self.good.unlink()
        self.good.symlink_to(self.other)
        self.assertEqual(audit_exact(self.orig, self.frozen)['result'], 'Blocked')

    def test_parent_symlink_blocks(self):
        d = self.root / 'real'
        d.mkdir()
        f = d / 'file'
        f.write_bytes(b'abc')
        link = self.root / 'alias'
        link.symlink_to(d, target_is_directory=True)
        import hashlib
        r = audit_exact({str(link / 'file'): hashlib.sha256(b'abc').hexdigest()}, {})
        self.assertEqual(r['result'], 'Blocked')

    def test_bad_error_schema_blocks(self):
        with self.assertRaises(AdmissionError):
            error_pairs({'errors': [{'path': str(self.absent)}]})

    def test_duplicate_error_blocks(self):
        row = {'path': str(self.absent), 'expectedSha256': '0'*64,
               'error': "[Errno 2] No such file or directory: '" + str(self.absent) + "'"}
        with self.assertRaises(AdmissionError):
            error_pairs({'errors': [row, row]})

    def test_unchanged_error_rows(self):
        row = {'path': str(self.absent), 'expectedSha256': '0'*64,
               'error': "[Errno 2] No such file or directory: '" + str(self.absent) + "'"}
        self.assertEqual(error_pairs({'errors': [row]}), self.frozen)

    def test_require_is_fail_closed(self):
        with self.assertRaises(AdmissionError):
            require(False, 'test')


class RealImmutableCBindingTests(unittest.TestCase):
    """Unlike synthetic controls, these tests read original C Git-published bytes.

    C's published receipt objects and four map parts are checked in under R03.
    These tests deliberately do NOT read or repair the unavailable S live roots.
    """

    @classmethod
    def setUpClass(cls):
        cls.checkpoint = (
            Path(__file__).resolve().parents[2] /
            'local-validation-20261009-ir-r03-02-c-custody-blocked'
        )
        cls.pre = cls.checkpoint / 'preflight'

    def test_all_c_sha_and_git_blob_pins_are_complete(self):
        verify_pinned_receipt_constants()
        self.assertEqual(len(C_BLOBS), 5)
        self.assertEqual(set(C_BLOBS), set(C_RECEIPT_GIT_BLOBS))

    def test_original_c_five_real_receipts_match_both_digests(self):
        for name in sorted(C_BLOBS):
            with self.subTest(original_c_file=name):
                obj = authenticated_c_receipt(self.pre, name)
                self.assertIsInstance(obj, dict)

    def test_truncated_native_limit_sha_is_rejected(self):
        name = 'NATIVE_LIVE_CUSTODY_LIMIT.json'
        with self.assertRaisesRegex(AdmissionError, 'Invalid pinned SHA-256'):
            authenticated_json(self.pre / name, C_BLOBS[name][:-11],
                               C_RECEIPT_GIT_BLOBS[name])

    def test_same_sha_but_wrong_original_git_blob_is_rejected(self):
        name = 'NATIVE_LIVE_CUSTODY_LIMIT.json'
        with self.assertRaisesRegex(AdmissionError, 'Immutable C Git blob mismatch'):
            authenticated_json(self.pre / name, C_BLOBS[name], '0' * 40)

    def test_full_original_c_roster_parses_without_live_s_access(self):
        original, missing = load_frozen_c(self.checkpoint)
        self.assertEqual(len(original), EXPECTED_FILES)
        self.assertEqual(len(missing), EXPECTED_MISSING)
        self.assertEqual(len(original) - len(missing), 339367)
        self.assertEqual(original.get(next(iter(missing))), missing[next(iter(missing))])



if __name__ == '__main__':
    unittest.main()
