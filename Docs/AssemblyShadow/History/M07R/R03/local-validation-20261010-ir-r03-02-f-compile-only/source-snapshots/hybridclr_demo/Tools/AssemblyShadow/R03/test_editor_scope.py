"""Synthetic NUnit selection contracts. No new Editor execution is inferred."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from batch_contract import ContractError
from editor_scope import (catalog, load_scope, verify_editor, verify_scope_project, mandatory_names,
                          EXCLUDED, REASON, PREFIX, CYCLE, TEST_FILTER, REFERENCE, PACKAGE, MISSING_ASSETS)
from run_local import Batch

IDS = ['L%02d-synthetic' % i for i in range(1, 21)] + ['M%02d-synthetic' % i for i in range(1, 16)]


def reference():
    tree = ET.Element('test-run', result='Skipped:Ignored', total='755', passed='754', failed='0', skipped='1', inconclusive='0')
    names = mandatory_names(IDS) + ['Synthetic.Package.Other%03d' % i for i in range(718)]
    for name in names: ET.SubElement(tree, 'test-case', fullname=name, result='Passed')
    excluded = ET.SubElement(tree, 'test-case', fullname=EXCLUDED, result='Skipped', label='Ignored')
    ET.SubElement(ET.SubElement(excluded, 'reason'), 'message').text = REASON
    return tree


def filtered(scope):
    tree = ET.Element('test-run', result='Passed', total='754', passed='754', failed='0', skipped='0', inconclusive='0')
    for name in scope['expectedNames']: ET.SubElement(tree, 'test-case', fullname=name, result='Passed')
    return tree


class EditorScopeContracts(unittest.TestCase):
    def setUp(self):
        self.scope = catalog(reference(), IDS)
        self.xml = filtered(self.scope)

    def test_all_selected_cases_pass_and_asset_coverage_stays_absent(self):
        result = verify_editor(self.xml, self.scope)
        self.assertEqual(result['passed'], 754)
        self.assertEqual(result['excludedCoverage'][0]['coverage'], 'NoCoverage')
        self.assertFalse(result['fullLegacyRegressionAcceptance'])

    def test_original_unfiltered_ignored_result_is_still_rejected(self):
        with self.assertRaises(ContractError): verify_editor(reference(), self.scope)

    def test_exact_single_exclusion_not_category_wide(self):
        self.assertEqual(TEST_FILTER, '!^' + __import__('re').escape(EXCLUDED) + '$')
        self.assertNotIn('-testCategory', TEST_FILTER)

    def test_same_count_wrong_identity_rejected(self):
        self.xml[0].set('fullname', 'Unexpected.Test')
        with self.assertRaises(ContractError): verify_editor(self.xml, self.scope)

    def test_duplicate_identity_rejected(self):
        self.xml[0].set('fullname', self.xml[1].get('fullname'))
        with self.assertRaises(ContractError): verify_editor(self.xml, self.scope)

    def test_missing_mandatory_case_rejected(self):
        case = next(c for c in self.xml if c.get('fullname') == CYCLE); self.xml.remove(case)
        with self.assertRaises(ContractError): verify_editor(self.xml, self.scope)

    def test_required_skip_rejected_even_if_aggregate_claims_pass(self):
        next(c for c in self.xml if c.get('fullname') == CYCLE).set('result', 'Skipped')
        with self.assertRaises(ContractError): verify_editor(self.xml, self.scope)

    def test_nonmandatory_skip_also_rejected(self):
        next(c for c in self.xml if c.get('fullname').startswith('Synthetic')).set('result', 'Skipped')
        with self.assertRaises(ContractError): verify_editor(self.xml, self.scope)

    def test_failed_case_rejected(self):
        self.xml[0].set('result', 'Failed')
        with self.assertRaises(ContractError): verify_editor(self.xml, self.scope)

    def test_ignored_aggregate_never_accepted(self):
        self.xml.set('result', 'Skipped:Ignored')
        with self.assertRaises(ContractError): verify_editor(self.xml, self.scope)

    def test_false_aggregate_counts_rejected(self):
        for field, value in (('passed', '755'), ('total', '0'), ('skipped', '1'), ('inconclusive', '1'), ('failed', '1')):
            with self.subTest(field=field):
                tree = copy.deepcopy(self.xml); tree.set(field, value)
                with self.assertRaises(ContractError): verify_editor(tree, self.scope)

    def test_case_label_ignored_rejected(self):
        self.xml[0].set('label', 'Ignored')
        with self.assertRaises(ContractError): verify_editor(self.xml, self.scope)

    def test_empty_xml_rejected(self):
        with self.assertRaises(ContractError): verify_editor(ET.Element('test-run'), self.scope)

    def test_foreign_namespace_cannot_satisfy_required_case(self):
        case = next(c for c in self.xml if c.get('fullname') == CYCLE)
        case.set('fullname', 'Foreign.' + CYCLE)
        with self.assertRaises(ContractError): verify_editor(self.xml, self.scope)

    def test_bad_required_id_list_rejected(self):
        for ids in (IDS[:-1], IDS[:-1] + [IDS[0]], IDS[:-1] + ['.*']):
            with self.subTest(ids=ids[-1:]), self.assertRaises(ContractError): mandatory_names(ids)

    def test_catalog_cannot_silently_drop_another_test(self):
        xml = reference(); xml[0].set('result', 'Skipped')
        with self.assertRaises(ContractError): catalog(xml, IDS)

    def test_catalog_reason_must_match_missing_fixture(self):
        xml = reference(); xml[-1].find('reason/message').text = 'other unavailable condition'
        with self.assertRaises(ContractError): catalog(xml, IDS)

    def test_pinned_catalog_hash_enforced(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / REFERENCE; path.parent.mkdir(parents=True); path.write_bytes(ET.tostring(reference()))
            with self.assertRaises(ContractError): load_scope(d, PACKAGE, IDS)
            data = path.read_bytes(); blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            with patch('editor_scope.REFERENCE_BLOB', blob):
                self.assertEqual(load_scope(d, PACKAGE, IDS)['expectedCount'], 754)

    def test_different_package_requires_new_scope(self):
        with self.assertRaises(ContractError): load_scope('/unused', 'f' * 40, IDS)

    def test_fixture_scope_rejects_newly_present_m01_asset(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(verify_scope_project(d)['coverage'], 'NoCoverage')
            path = Path(d) / MISSING_ASSETS[0]; path.parent.mkdir(parents=True); path.write_text('not a real asset')
            with self.assertRaises(ContractError): verify_scope_project(d)

    def test_actual_batch_editor_call_is_filtered_and_writes_verdict(self):
        with tempfile.TemporaryDirectory() as d:
            batch = object.__new__(Batch); batch.root = Path(d); batch.workspace = Path(d) / 'workspace'
            batch.pins = {'hybridclr_unity': PACKAGE}; batch.unity = '/not-executed/Unity'
            batch.builds = {'candidate-release': {'project': Path(d) / 'projects/candidate-release'}}
            path = Path(d) / 'host/admission/results.json'; path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'cases': [{'id': i} for i in IDS]}))
            def invocation(receiver, command, timeout):
                self.assertEqual(command[command.index('-testFilter') + 1], TEST_FILTER)
                self.assertEqual(timeout, 3600)
                ET.ElementTree(self.xml).write(Path(d) / 'editor-results.xml')
            with patch('run_local.load_scope', return_value=copy.deepcopy(self.scope)), patch('run_local.unity_command', side_effect=invocation):
                self.assertEqual(batch.editor_tests()['passed'], 754)
            self.assertEqual(json.loads((Path(d) / 'editor-verification.json').read_text())['skipped'], 0)

    def test_filtered_failed_invocation_cannot_be_promoted(self):
        with tempfile.TemporaryDirectory() as d:
            batch = object.__new__(Batch); batch.root = Path(d); batch.workspace = Path(d)
            batch.pins = {'hybridclr_unity': PACKAGE}; batch.unity = '/not-executed/Unity'
            batch.builds = {'candidate-release': {'project': Path(d) / 'projects/candidate-release'}}
            path = Path(d) / 'host/admission/results.json'; path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'cases': [{'id': i} for i in IDS]}))
            with patch('run_local.load_scope', return_value=copy.deepcopy(self.scope)), patch('run_local.unity_command', side_effect=RuntimeError('compiler failed')):
                with self.assertRaises(RuntimeError): batch.editor_tests()
            result = json.loads((Path(d) / 'editor-verification.json').read_text())
            self.assertEqual(result['result'], 'Failed')
            self.assertEqual(result['excludedCoverage'][0]['coverage'], 'NoCoverage')


if __name__ == '__main__': unittest.main()
