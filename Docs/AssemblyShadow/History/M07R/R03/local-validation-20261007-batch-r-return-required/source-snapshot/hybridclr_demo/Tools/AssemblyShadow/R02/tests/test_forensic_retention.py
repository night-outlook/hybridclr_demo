import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from evidence import EvidenceError, binding, read, seal, check_binding
import test_m00_forensics as fixtures
import m00_forensics as f


class ForensicRetention(unittest.TestCase):
    setUp = fixtures.PeForensics.setUp
    receipts = fixtures.PeForensics.receipts
    # Reuse only setup/fixture generation, not the parent test inventory.
    def context(self, remove=True):
        raws, hashes, images = self.receipts()
        paths = [self.root/('old-'+role+'.dll') for role in ('candidate', 'control')]
        batch = self.root/'E'; batch.mkdir()
        result = seal(paths, batch/'seal')
        origin = dict(kind='R02LocalBatchELiveEvidenceBindings', result='AuthenticatedAtCheckpoint',
                      batchRoot=str(batch), files=[binding(batch/'seal/seal-index.json'), result['archive']])
        raw_origin = json.dumps(origin).encode()
        origin_blob = hashlib.sha1(b'blob '+str(len(raw_origin)).encode()+b'\0'+raw_origin).hexdigest()
        if remove:
            for path in paths: path.unlink()
        def git(args, **kwargs):
            if args[-1].endswith('LIVE_EVIDENCE_BINDINGS.json'): return raw_origin
            return raws['candidate' if 'candidate.json' in args[-1] else 'control']
        return hashes, images, origin_blob, git, result

    def analyze(self, context):
        hashes, images, origin_blob, git, _ = context
        with patch.object(f, 'E_BLOBS', hashes), patch.object(f, 'E_IMAGES', images), \
             patch.object(f, 'E_BINDINGS_BLOB', origin_blob), patch.object(f.subprocess, 'check_output', side_effect=git):
            return f.analyze_batch_e(self.root, self.root/'analysis')

    def test_absent_live_inputs_recovered_from_exact_archive_and_fully_sealable(self):
        context = self.context()
        report = self.analyze(context)
        self.assertTrue(report['inputsSnapshotted'])
        self.assertTrue(all(r['classification'] == 'AuthenticatedArchiveMemberSnapshot' for r in report['inputAcquisition'].values()))
        for row in report['retainedInputs']: check_binding(row)
        self.assertEqual(seal([Path(r['path']) for r in report['retainedInputs']], self.root/'final-seal')['result'], 'Passed')
        self.assertFalse((self.root/'old-candidate.dll').exists())

    def test_live_snapshots_survive_later_source_removal(self):
        context = self.context(remove=False)
        report = self.analyze(context)
        for role in ('candidate', 'control'): (self.root/('old-'+role+'.dll')).unlink()
        self.assertTrue(all(r['classification'] == 'AuthenticatedLiveSnapshot' for r in report['inputAcquisition'].values()))
        self.assertEqual(seal([Path(r['path']) for r in report['retainedInputs']], self.root/'final-seal')['result'], 'Passed')

    def test_archive_change_fails_without_reconstructing_original_path(self):
        context = self.context(); Path(context[-1]['archive']['path']).write_bytes(b'bad archive')
        with self.assertRaises(EvidenceError): self.analyze(context)
        self.assertFalse(read(self.root/'analysis/analysis.json')['inputsSnapshotted'])
        self.assertFalse((self.root/'old-candidate.dll').exists())

    def test_bad_existing_live_bytes_are_not_hidden_by_good_archive(self):
        context = self.context(remove=False); (self.root/'old-candidate.dll').write_bytes(b'corrupt')
        with self.assertRaises(EvidenceError): self.analyze(context)
        self.assertEqual((self.root/'old-candidate.dll').read_bytes(), b'corrupt')

    def test_matching_basename_cannot_replace_exact_index_locator(self):
        context = self.context()
        # Mutating the authenticated index is rejected before selecting bytes.
        index = self.root/'E/seal/seal-index.json'; raw = read(index)
        raw['files'][0]['path'] += '.other'
        index.write_text(json.dumps(raw))
        with self.assertRaises(EvidenceError): self.analyze(context)

if __name__ == '__main__': unittest.main()
