import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from h1_capture_attempt import Attempt, RetentionError


class CaptureAttemptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
    def tearDown(self): self.temp.cleanup()
    def make(self, **kwargs): return Attempt(self.root / 'attempt', 'unit-test', **kwargs)
    def state(self): return json.loads((self.root / 'attempt/attempt-state.json').read_text())
    def test_root_created_before_guarded_validation(self):
        a = self.make(); self.assertTrue(a.root.is_dir())
        with self.assertRaisesRegex(ValueError, 'bad plan'):
            with a.guard():
                a.stage('planning', planning='Started'); raise ValueError('bad plan')
        s = self.state(); self.assertEqual('FailedNotAccepted', s['status']); self.assertEqual('planning', s['stage'])
        self.assertEqual('NotRun', s['pchReplay']); self.assertEqual('NotRun', s['macroProbes'])
    def test_existing_directory_untouched(self):
        a = self.make(); before = (a.root / 'attempt-state.json').read_bytes()
        with self.assertRaises(RetentionError): self.make()
        self.assertEqual(before, (a.root / 'attempt-state.json').read_bytes())
    def test_existing_file_untouched(self):
        (self.root / 'attempt').write_bytes(b'historical')
        with self.assertRaises(RetentionError): self.make()
        self.assertEqual(b'historical', (self.root / 'attempt').read_bytes())
    def test_relative_root_rejected(self):
        with self.assertRaises(RetentionError): Attempt(Path('relative'), 'unit-test')
    def test_symlink_ancestor_rejected(self):
        target = self.root / 'target'; target.mkdir(); link = self.root / 'link'; link.symlink_to(target)
        with self.assertRaises(RetentionError): Attempt(link / 'new', 'unit-test')
        self.assertFalse((target / 'new').exists())
    def test_original_bytes_survive_source_replacement(self):
        src = self.root / 'raw.json'; src.write_bytes(b'{ "x" : 1 }\n')
        a = self.make(); a.read_file(src, 'graph'); src.write_bytes(b'new')
        self.assertEqual(b'{ "x" : 1 }\n', Path(a.rows[0]['retainedPath']).read_bytes())
    def test_same_source_observed_changed_rejected(self):
        a = self.make(); a.keep_bytes('/a', b'a', 'graph')
        with self.assertRaisesRegex(RetentionError, 'changed'): a.keep_bytes('/a', b'b', 'graph')
    def test_content_deduplicates_without_losing_locators(self):
        a = self.make(); a.keep_bytes('/a', b'abc', 'graph'); a.keep_bytes('/b', b'abc', 'graph')
        self.assertEqual(2, len(a.rows)); self.assertEqual(3, a.used_bytes)
        self.assertEqual(1, len(list(a.inputs.iterdir())))
    def test_binary_pch_retained_without_decoding(self):
        raw = b'\x80\xff\x00CPCH'; a = self.make(); r = a.keep_bytes('/x.pch', raw, 'pch')
        self.assertEqual(raw, Path(r['retainedPath']).read_bytes())
    def test_missing_optional_input_explicit(self):
        a = self.make(); self.assertIsNone(a.read_file(self.root / 'missing', 'header', required=False))
        self.assertEqual('UnavailableToRetention', a.rows[-1]['status'])
    def test_missing_required_input_raises_and_retains_failure(self):
        a = self.make()
        with self.assertRaises(FileNotFoundError):
            with a.guard(): a.read_file(self.root / 'missing', 'request')
        self.assertTrue((a.root / 'attempt-failure.json').is_file())
    def test_oversized_file_not_read(self):
        src = self.root / 'x'; src.write_bytes(b'12345'); a = self.make(max_file_bytes=4)
        with self.assertRaises(RetentionError): a.read_file(src, 'header')
        self.assertEqual(0, a.used_bytes)
    def test_total_budget_is_fatal_even_for_optional_input(self):
        a = self.make(max_total_bytes=3); a.keep_bytes('/a', b'aa', 'a')
        src = self.root / 'b'; src.write_bytes(b'bb')
        with self.assertRaisesRegex(RetentionError, 'byte bound'): a.read_file(src, 'b', required=False)
    def test_inventory_bound(self):
        a = self.make(max_files=1); a.keep_bytes('/a', b'a', 'a')
        with self.assertRaises(RetentionError): a.keep_bytes('/b', b'b', 'b')
    def test_invalid_bounds_rejected_before_creating_root(self):
        with self.assertRaises(RetentionError): self.make(max_files=True)
        self.assertFalse((self.root / 'attempt').exists())
    def test_symlink_input_rejected(self):
        src = self.root / 'real.h'; src.write_bytes(b'h'); link = self.root / 'link.h'; link.symlink_to(src)
        a = self.make()
        with self.assertRaises(RetentionError): a.read_file(link, 'header')
    def test_metadata_inventory_hash_and_traceback(self):
        a = self.make()
        with self.assertRaises(KeyError):
            with a.guard():
                a.keep_bytes('/bad.json', b'invalid', 'request'); raise KeyError('bad')
        failure = json.loads((a.root / 'attempt-failure.json').read_text())
        self.assertIn('KeyError', failure['traceback'])
        self.assertEqual(hashlib.sha256(a.inventory.read_bytes()).hexdigest(), failure['inputInventorySha256'])
    def test_original_error_not_masked_by_journal_failure(self):
        a = self.make(); error = ValueError('original')
        with patch.object(a, 'fail', side_effect=OSError('disk full')):
            with self.assertRaises(ValueError) as caught:
                with a.guard(): raise error
        self.assertIs(error, caught.exception)
    def test_keyboard_interrupt_recorded_and_propagated(self):
        a = self.make()
        with self.assertRaises(KeyboardInterrupt):
            with a.guard(): raise KeyboardInterrupt()
        self.assertEqual('KeyboardInterrupt', self.state()['errorType'])
    def test_declared_pch_and_header_retained_without_execution(self):
        h = self.root / 'x.h'; h.write_bytes(b'header'); p = self.root / 'x.pch'; p.write_bytes(b'pch')
        graph = {'Nodes': [{'Annotation': 'C_Mac_arm64Pch', 'Inputs': [str(h)], 'Outputs': [str(p)]}]}
        a = self.make(); a.retain_declared_inputs(graph, self.root)
        self.assertEqual({str(h), str(p)}, {r['sourcePath'] for r in a.rows})
        self.assertEqual('NotDiscoveredBeforePchInspection', a.state['transitivePchHeaders'])
    def test_success_diagnostic_is_not_acceptance(self):
        a = self.make(); a.finish('CapturedNotRuntimeAccepted')
        s = self.state(); self.assertFalse(s['candidateAcceptance']); self.assertFalse(s['humanGatePassed'])
        self.assertFalse(s['mayEnterR02']); self.assertFalse((a.root / 'h1-compiler-provenance.json').exists())
