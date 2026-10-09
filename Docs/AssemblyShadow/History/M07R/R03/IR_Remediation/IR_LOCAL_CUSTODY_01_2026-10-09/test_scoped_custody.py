"""Synthetic negative controls for the exact-loss, read-only custody verifier."""
from pathlib import Path
import tempfile
import unittest
from verify_scoped_custody import audit_exact, error_pairs, require, AdmissionError


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


if __name__ == '__main__':
    unittest.main()
