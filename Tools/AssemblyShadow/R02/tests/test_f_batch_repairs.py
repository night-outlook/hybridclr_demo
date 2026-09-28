import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from evidence import EvidenceError
import run_local
import restoration


class FBatchRepairs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.batch = object.__new__(run_local.Batch)
        self.batch.roots = {'candidate': self.root}
        self.batch.graphs = {'candidate': {'fixtureManifest': 'fixtures', 'nativeOnReceipt': 'on',
            'nativeOffReceipt': 'off', 'editorReplayReceipt': 'replay'}}
        self.batch.generated_roots = set(); self.batch.prefix = 'test'; self.batch.out = self.root / 'batch'
        (self.root / '_temp/AssemblyShadow').mkdir(parents=True)

    def test_m07_generates_control_capsules_before_launch(self):
        with patch.object(self.batch, 'tool') as call:
            self.batch.regression('m07')
        self.assertEqual([c.args[0] for c in call.call_args_list],
            ['prepare-h1-m07-control-capsules.py', 'run-m07-players.py', 'verify-m07-results.py'])
        prepare, launch = call.call_args_list[:2]
        target = prepare.args[1][-1]
        args = launch.args[1]
        self.assertEqual(args[args.index('--early-capsule-root') + 1], target)
        self.assertIn(target, self.batch.generated_roots)

    def test_failed_capsule_preparation_never_launches_player(self):
        with patch.object(self.batch, 'tool', side_effect=EvidenceError('capsule invalid')) as call:
            with self.assertRaises(EvidenceError): self.batch.regression('m07')
        self.assertEqual(call.call_count, 1)

    def test_counts_dispatch_both_families_to_exact_auditors(self):
        with patch.object(self.batch, 'tool') as call, patch.object(self.batch, 'count_one', return_value=self.root/'receipt'):
            self.batch.counts()
        audits = [c for c in call.call_args_list if c.args[0].startswith('audit-')]
        self.assertEqual([c.args[0] for c in audits], ['audit-h1-count-fixtures.py', 'audit-h1-nested-fixtures.py'])
        self.assertEqual([c.args[1][1].parent.name for c in audits], ['parameters', 'nested'])
        matrix = next(c for c in call.call_args_list if c.args[0] == 'run-h1-count-matrix-players.py')
        self.assertIn('--parameter-audit', matrix.args[1]); self.assertIn('--nested-audit', matrix.args[1])
        with self.assertRaises(EvidenceError): run_local.fixture_auditor('unknown')

    def test_missing_required_forensic_inputs_still_make_seal_fatal(self):
        folder = self.batch.out / 'm00-batch-e-forensics'; folder.mkdir(parents=True)
        (folder/'analysis.json').write_text(json.dumps({'inputsSnapshotted': False, 'result': 'Failed'}))
        with self.assertRaisesRegex(EvidenceError, 'acquisition incomplete'): self.batch.finish()
        self.assertFalse((self.batch.out/'LOCAL_BATCH_RESULT.json').exists())

    def generated(self, names=None):
        names = restoration.DIAGNOSTIC_LINK_TYPES if names is None else names
        return ('\ufeff<?xml version="1.0" encoding="utf-8"?>\n<linker><assembly fullname="netstandard">' +
                ''.join('<type fullname="'+n+'" preserve="all" />' for n in sorted(names)) + '</assembly></linker>').encode()

    def test_exact_observed_linker_expansion_is_restored_byte_exact(self):
        original = b'<linker></linker>\r\n'
        path = self.root / restoration.GENERATED_LINK; path.parent.mkdir(parents=True)
        path.write_bytes(self.generated())
        self.assertTrue(restoration.generated_link_allowed(original, path.read_bytes()))
        restoration.restore_files(self.root, {restoration.GENERATED_LINK: original},
            lambda _, old, new: restoration.generated_link_allowed(old, new), self.root/'capture')
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual((self.root/'capture/000.after').read_bytes(), self.generated())

    def test_arbitrary_linker_edits_are_not_a_restoration_permission(self):
        before = b'<linker />'
        after = self.generated()
        for invalid in (after.replace(b'netstandard', b'Other'), after.replace(b'preserve="all"', b'preserve="nothing"'),
                        after.replace(b'System.Array', b'System.Unknown'), self.generated([]),
                        after.replace(b'<linker>', b'<linker><!--hidden-->'),
                        after.replace(b'</assembly>', b'<type fullname="System.Array" preserve="all"/></assembly>')):
            self.assertFalse(restoration.generated_link_allowed(before, invalid))
        self.assertFalse(restoration.generated_link_allowed(b'<linker><assembly fullname="User"/></linker>', after))
        self.assertTrue(restoration.generated_link_allowed(after, after))

    def test_diagnostic_and_count_transactions_both_capture_linker(self):
        # Complements the real restoration tests: a new build path may not omit
        # link.xml from its transaction just because the XML helper is covered.
        import inspect
        for method in (run_local.Batch.diagnostic, run_local.Batch.count_one):
            source = inspect.getsource(method)
            self.assertIn('GENERATED_LINK', source)
            self.assertIn('generated_link_allowed', source)


if __name__ == '__main__': unittest.main()
