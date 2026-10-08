"""Synthetic host regressions; no Unity execution or historical-input mutation."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import audit_s_provenance as audit


class FinalizerContractTests(unittest.TestCase):
    def setUp(self):
        self.ledger = {'result': 'EvidenceReadyForPrimaryReview', 'R03Accepted': False,
                       'H2Passed': False, 'cells': [{'id': 'positive', 'count': 0}]}
        self.seal = {'archiveSha256': 'a' * 64, 'indexSha256': 'b' * 64,
                     'members': 2, 'runtimeAcceptance': False}
        self.sha = 'c' * 64
        self.result = dict(copy.deepcopy(self.ledger), seal=copy.deepcopy(self.seal),
                           sealStatus='Passed', executionLedgerSha256=self.sha)

    def verify(self):
        audit.verify_final_pair(self.ledger, self.result, self.seal, self.sha)

    def test_original_summary_flags_survive_comparison(self):
        self.verify()

    def test_inputs_are_not_normalized_or_mutated(self):
        before = copy.deepcopy((self.ledger, self.result, self.seal))
        self.verify()
        self.assertEqual(before, (self.ledger, self.result, self.seal))

    def test_each_missing_acceptance_flag_is_rejected(self):
        for name in ('ledger', 'result'):
            for flag in ('R03Accepted', 'H2Passed'):
                with self.subTest(record=name, flag=flag):
                    self.setUp()
                    del getattr(self, name)[flag]
                    with self.assertRaisesRegex(ValueError, 'Explicit false'):
                        self.verify()

    def test_truthy_null_and_numeric_acceptance_flags_are_rejected(self):
        for name in ('ledger', 'result'):
            for flag in ('R03Accepted', 'H2Passed'):
                for value in (True, None, 0, 1, '', 'false'):
                    with self.subTest(record=name, flag=flag, value=repr(value)):
                        self.setUp()
                        getattr(self, name)[flag] = value
                        with self.assertRaisesRegex(ValueError, 'Explicit false'):
                            self.verify()

    def test_seal_fields_must_not_already_exist_in_ledger(self):
        for name in ('seal', 'sealStatus', 'executionLedgerSha256'):
            with self.subTest(field=name):
                self.setUp()
                self.ledger[name] = self.result[name]
                with self.assertRaisesRegex(ValueError, 'must not pre-exist'):
                    self.verify()

    def test_wrong_archive_or_index_digest_is_rejected(self):
        for name in ('archiveSha256', 'indexSha256'):
            with self.subTest(field=name):
                self.setUp()
                self.result['seal'][name] = 'd' * 64
                with self.assertRaisesRegex(ValueError, 'semantic equality'):
                    self.verify()

    def test_wrong_ledger_digest_is_rejected(self):
        self.result['executionLedgerSha256'] = 'e' * 64
        with self.assertRaisesRegex(ValueError, 'semantic equality'):
            self.verify()

    def test_failed_seal_is_not_promoted(self):
        self.result['sealStatus'] = 'Failed'
        with self.assertRaisesRegex(ValueError, 'semantic equality'):
            self.verify()

    def test_extra_final_result_field_is_rejected(self):
        self.result['unexpected'] = 'not produced by finalizer'
        with self.assertRaisesRegex(ValueError, 'semantic equality'):
            self.verify()

    def test_changed_nested_cell_is_rejected(self):
        self.result['cells'][0]['count'] = 1
        with self.assertRaisesRegex(ValueError, 'semantic equality'):
            self.verify()

    def test_nested_false_does_not_match_numeric_zero(self):
        self.result['cells'][0]['count'] = False
        with self.assertRaisesRegex(ValueError, 'semantic equality'):
            self.verify()

    def test_nonobject_inputs_are_rejected(self):
        for ledger, result in (([], self.result), (self.ledger, [])):
            with self.subTest(ledger=type(ledger), result=type(result)):
                with self.assertRaisesRegex(ValueError, 'Object ledger'):
                    audit.verify_final_pair(ledger, result, self.seal, self.sha)


class EvidencePrimitiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def json_file(self, raw):
        path = self.root / 'data.json'
        path.write_text(raw, encoding='utf-8')
        return path

    def test_json_key_order_is_not_significant(self):
        self.assertTrue(audit.json_equal({'a': 1, 'b': False}, {'b': False, 'a': 1}))

    def test_json_boolean_and_number_are_different(self):
        self.assertFalse(audit.json_equal({'a': False}, {'a': 0}))
        self.assertFalse(audit.json_equal({'a': True}, {'a': 1}))

    def test_duplicate_json_keys_are_rejected(self):
        for raw in ('{"a":1,"a":2}', '{"outer":{"a":1,"a":1}}'):
            with self.subTest(raw=raw):
                with self.assertRaisesRegex(ValueError, 'Duplicate JSON key'):
                    audit.load(self.json_file(raw))

    def test_nonfinite_json_numbers_are_rejected(self):
        for raw in ('NaN', 'Infinity', '-Infinity', '{"a":NaN}'):
            with self.subTest(raw=raw):
                with self.assertRaisesRegex(ValueError, 'Non-finite'):
                    audit.load(self.json_file(raw))

    def test_utf8_json_is_preserved(self):
        self.assertEqual(audit.load(self.json_file('{"text":"\u8bc1\u636e"}')), {'text': '\u8bc1\u636e'})

    def test_noncanonical_paths_are_rejected(self):
        for value in ('', '.', './a', 'a//b', 'a/../b', 'a/', '/a', 'C:/a', 'a\\b', 'a\x00b', None, 1, True):
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError):
                    audit.relpath(value)

    def test_canonical_relative_path_is_preserved(self):
        self.assertEqual(str(audit.relpath('batch/cells/a.json')), 'batch/cells/a.json')

    def test_missing_and_directory_paths_are_rejected(self):
        (self.root / 'directory').mkdir()
        for name in ('missing', 'directory'):
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, 'Missing/nonregular'):
                    audit.file_under(self.root, name)

    def test_symlink_file_is_rejected(self):
        target = self.json_file('{}')
        (self.root / 'link.json').symlink_to(target)
        with self.assertRaisesRegex(ValueError, 'Missing/nonregular'):
            audit.file_under(self.root, 'link.json')

    def test_symlink_parent_cannot_escape_root(self):
        nested = self.root / 'nested'
        nested.mkdir()
        self.json_file('{}')
        (nested / 'escape').symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Missing/nonregular'):
            audit.file_under(nested, 'escape/data.json')

    def test_bound_json_matches_authenticated_bytes(self):
        path = self.json_file('{"id":1}\n')
        members = {'data.json': {'size': path.stat().st_size, 'sha256': audit.digest(path)}}
        self.assertEqual(audit.bound_json(self.root, members, 'data.json'), {'id': 1})

    def test_bound_json_rejects_missing_membership(self):
        self.json_file('{}')
        with self.assertRaisesRegex(ValueError, 'missing from authenticated archive'):
            audit.bound_json(self.root, {}, 'data.json')

    def test_bound_json_rejects_digest_or_size_change(self):
        path = self.json_file('{"id":1}\n')
        good = {'size': path.stat().st_size, 'sha256': audit.digest(path)}
        for bad in (dict(good, size=good['size'] + 1), dict(good, sha256='0' * 64)):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, 'Checkpoint/archive JSON mismatch'):
                    audit.bound_json(self.root, {'data.json': bad}, 'data.json')

    def test_recorded_null_false_and_absence_are_distinct(self):
        self.assertEqual(audit.field_observation({}, 'flag'), {'state': 'NotRecorded'})
        self.assertEqual(audit.field_observation({'flag': False}, 'flag'), {'state': 'Recorded', 'value': False})
        self.assertEqual(audit.field_observation({'flag': None}, 'flag'), {'state': 'Recorded', 'value': None})

    def test_late_failure_revokes_pass_without_erasing_completed_checks(self):
        report = {'result': 'Passed', 'checksCompleted': ['ArchiveBytes'], 'runtimeAcceptance': False}
        audit.record_failure(report, OSError('export failed'))
        self.assertEqual(report['result'], 'Failed')
        self.assertEqual(report['checksCompleted'], ['ArchiveBytes'])
        self.assertEqual(report['error'], 'export failed')
        self.assertIs(report['runtimeAcceptance'], False)

    def test_early_failure_remains_failed(self):
        report = {'result': 'Failed', 'historicalInputsModified': None}
        audit.record_failure(report, ValueError('archive mismatch'))
        self.assertEqual(report['result'], 'Failed')
        self.assertIsNone(report['historicalInputsModified'])

    def test_write_cannot_overwrite_existing_evidence(self):
        path = self.json_file('{"original":true}\n')
        before = path.read_bytes()
        with self.assertRaises(FileExistsError):
            audit.write(path, {'original': False})
        self.assertEqual(path.read_bytes(), before)

    def test_digest_uses_file_bytes(self):
        path = self.json_file('{"original":true}\n')
        self.assertEqual(audit.digest(path), hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
