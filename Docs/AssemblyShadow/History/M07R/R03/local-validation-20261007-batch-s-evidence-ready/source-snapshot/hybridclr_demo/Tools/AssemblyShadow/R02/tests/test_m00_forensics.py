import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from evidence import EvidenceError, binding, read
import m00_forensics as f
import ordinary_input as ordinary
from shadow_tools import VerificationError
from test_ordinary_input import setup_project


class PeForensics(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = setup_project(Path(self.tmp.name).resolve() / 'candidate')
        self.data = ordinary.fixture(self.root)[0]

    def test_frozen_image_exposes_historical_pdb_path(self):
        described = f.describe(self.data, 'frozen')
        cv = [r for r in described['parsedProvenance'] if r['kind'] == 'codeview']
        self.assertEqual(len(cv), 1)
        self.assertIn('/hybridclr_demo_shadow/Library/Bee/', cv[0]['pdbPath'])
        self.assertFalse(described['runtimeAcceptance'])

    def test_exact_bytes_diagnostic_never_grants_acceptance(self):
        report = f.compare(self.data, self.data, 'a', 'b')
        self.assertEqual(report['classification'], 'ExactBytes')
        self.assertFalse(report['runtimeAcceptance'])
        self.assertTrue(report['admissionPolicyUnchanged'])
        self.assertEqual(report['differingSpans'], [])

    def test_mvid_provenance_difference_is_diagnostic_only(self):
        data = bytearray(self.data)
        masks = f.describe(data, 'base')['maskRanges']
        offset = next(offset for offset, _, kind in masks if kind == 'module-mvid')
        data[offset] ^= 1
        report = f.compare(self.data, bytes(data), 'frozen', 'synthetic')
        self.assertTrue(report['mvidDiffers'])
        self.assertTrue(report['equalOutsideExistingPeProvenanceMask'])
        self.assertEqual(report['classification'], 'OnlyExistingPeProvenanceRangesDiffer')
        self.assertFalse(report['exactBytesEqual'])
        self.assertFalse(report['runtimeAcceptance'])

    def test_other_bytes_cannot_be_hidden_by_provenance_mask(self):
        data = bytearray(self.data); data[-1] ^= 1
        report = f.compare(self.data, bytes(data), 'a', 'mutated')
        self.assertFalse(report['equalOutsideExistingPeProvenanceMask'])
        self.assertEqual(report['classification'], 'OtherBytesOrLayoutAlsoDiffer')

    def test_same_length_pdb_path_difference_is_reported(self):
        data = bytearray(self.data)
        offset, _, _ = next(row for row in f.describe(data, 'base')['maskRanges'] if row[2] == 'codeview')
        data[offset+25] = ord('X')
        report = f.compare(self.data, bytes(data), 'a', 'synthetic')
        self.assertTrue(report['pdbPathsDiffer'])
        self.assertFalse(report['runtimeAcceptance'])

    def test_malformed_pe_rejected(self):
        for data in (b'', b'not PE', self.data[:40]):
            with self.subTest(size=len(data)):
                with self.assertRaises((ValueError, VerificationError)): f.describe(data, 'broken')

    def receipts(self):
        raws = {}; hashes = {}; image_hashes = {}
        for index, role in enumerate(('candidate', 'control')):
            image = self.root / ('old-'+role+'.dll')
            data = bytearray(self.data); data[-1] = index+1; image.write_bytes(data)
            row = dict(result='Failed', compiled=binding(image), expectedSha256=ordinary.IMAGE_SHA256,
                       sourcePinsSha256=str(index)*64, sources=[{'path':'labelled synthetic source'}])
            raw = json.dumps(row).encode(); raws[role] = raw
            hashes[role] = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            image_hashes[role] = row['compiled']['sha256']
        return raws, hashes, image_hashes

    def test_authenticated_read_only_analysis_of_three_pairs(self):
        raws, hashes, images = self.receipts()
        def git(args, **kwargs):
            return raws['candidate' if 'candidate.json' in args[-1] else 'control']
        output = self.root/'analysis'
        with patch.object(f, 'E_BLOBS', hashes), patch.object(f, 'E_IMAGES', images), \
             patch.object(f.subprocess, 'check_output', side_effect=git):
            report = f.analyze_batch_e(self.root, output)
        self.assertEqual(report['result'], 'AnalyzedNotRuntimeAccepted')
        self.assertEqual(len(report['comparisons']), 3)
        self.assertEqual(len(report['retainedInputs']), 6)
        self.assertTrue(report['inputsSnapshotted'])
        self.assertFalse((self.root/ordinary.IMAGE_PATH).exists())
        self.assertFalse(report['runtimeAcceptance'])

    def test_modified_checkpoint_blob_is_rejected_with_failure_receipt(self):
        output = self.root/'analysis'
        with patch.object(f.subprocess, 'check_output', return_value=b'{}'):
            with self.assertRaises(EvidenceError): f.analyze_batch_e(self.root, output)
        report = read(output/'analysis.json')
        self.assertEqual(report['result'], 'Failed')
        self.assertIn('Git blob changed', report['error'])

    def test_missing_retained_image_keeps_exact_error_and_bindings(self):
        raws, hashes, images = self.receipts()
        (self.root/'old-control.dll').unlink()
        def git(args, **kwargs):
            return raws['candidate' if 'candidate.json' in args[-1] else 'control']
        output = self.root/'analysis'
        with patch.object(f, 'E_BLOBS', hashes), patch.object(f, 'E_IMAGES', images), \
             patch.object(f.subprocess, 'check_output', side_effect=git):
            with self.assertRaises(EvidenceError): f.analyze_batch_e(self.root, output)
        report = read(output/'analysis.json')
        self.assertEqual(report['result'], 'Failed')
        self.assertEqual(len(report['retainedInputs']), 5)
        self.assertIn('old-control.dll', report['inputAcquisition']['control']['original']['path'])
        self.assertFalse(report['inputsSnapshotted'])

    def test_reused_output_refused(self):
        output=self.root/'analysis';output.mkdir()
        with self.assertRaises(EvidenceError): f.analyze_batch_e(self.root, output)


if __name__ == '__main__': unittest.main()
