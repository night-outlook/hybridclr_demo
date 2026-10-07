"""Synthetic orchestration controls, not execution of Unity/reference metadata."""
import json
from pathlib import Path
import re
import tempfile
import unittest
import reference_binding as replay
from batch_contract import ContractError


class ReferenceCaseCollectionContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'new-cases'
        self.inputs = {'basis': 'ReusedAuditedLocalNCompilerInputs'}
        self.called = []
    def tearDown(self):
        self.temp.cleanup()
    def producer(self, case, folder):
        self.called.append(case); folder.mkdir()
        row = {'id': case, 'result': 'Passed', 'elapsedMilliseconds': 1}
        data = {'kind': 'R03ReferenceBindingContracts', 'basis': self.inputs['basis'], 'selection': case,
                'result': 'Passed', 'failures': 0, 'cases': [row], **{key: False for key in replay.FLAGS}}
        (folder / 'results.json').write_text(json.dumps(data))
        (folder / 'case-result.json').write_text(json.dumps(row))
        if case == 'N-reference-context-diagnosis':
            (folder / 'reference-context-diagnosis.json').write_text('{"syntheticTestOnly":true}')
    def test_all_fifteen_execute_once_with_exact_receipts(self):
        result = replay.run_cases(self.root, self.inputs, self.producer)
        self.assertEqual(tuple(self.called), replay.CASE_IDS)
        self.assertEqual(len(self.called), 15)
        self.assertEqual(result['result'], 'Passed')
        self.assertEqual(len(result['caseReceipts']), 15)
        self.assertEqual(result['perCaseTimeoutSeconds'], 600)
        self.assertTrue(all(result[key] is False for key in replay.FLAGS))
    def test_failure_keeps_independent_cases_and_fails_aggregate(self):
        def run(case, folder):
            if case == replay.CASE_IDS[0]:
                self.called.append(case); raise RuntimeError('bounded command failed')
            self.producer(case, folder)
        with self.assertRaises(ContractError): replay.run_cases(self.root, self.inputs, run)
        result = json.loads((self.root / 'results.json').read_text())
        self.assertEqual(tuple(self.called), replay.CASE_IDS)
        self.assertEqual(result['result'], 'Failed')
        self.assertEqual(result['failures'], 1)
        self.assertEqual(result['cases'][0]['result'], 'Failed')
    def test_missing_final_case_result_cannot_pass(self):
        def run(case, folder):
            self.producer(case, folder)
            if case == replay.CASE_IDS[-1]: (folder / 'results.json').unlink()
        with self.assertRaises(ContractError): replay.run_cases(self.root, self.inputs, run)
    def test_wrong_case_selection_rejected(self):
        def run(case, folder):
            self.producer(case, folder)
            path = folder / 'results.json'; data = json.loads(path.read_text()); data['selection'] = 'foreign'; path.write_text(json.dumps(data))
        with self.assertRaises(ContractError): replay.run_cases(self.root, self.inputs, run)
        self.assertEqual(json.loads((self.root / 'results.json').read_text())['failures'], 15)
    def test_authority_promotion_rejected(self):
        def run(case, folder):
            self.producer(case, folder)
            path = folder / 'results.json'; data = json.loads(path.read_text()); data['qualificationApproved'] = True; path.write_text(json.dumps(data))
        with self.assertRaises(ContractError): replay.run_cases(self.root, self.inputs, run)
    def test_progress_disagreement_rejected(self):
        def run(case, folder):
            self.producer(case, folder); (folder / 'case-result.json').write_text('{}')
        with self.assertRaises(ContractError): replay.run_cases(self.root, self.inputs, run)
    def test_existing_root_is_never_reused(self):
        self.root.mkdir()
        with self.assertRaises(ContractError): replay.run_cases(self.root, self.inputs, self.producer)
        self.assertEqual(self.called, [])
    def test_known_case_argument_contract(self):
        for case in replay.CASE_IDS:
            self.assertEqual(replay.case_arguments('input', 'output', case), ['--input', 'input', '--output', 'output', '--case', case])
        with self.assertRaises(ContractError): replay.case_arguments('input', 'output', 'unknown')
    def test_exact_managed_case_inventory_preserved(self):
        text = (Path(replay.__file__).parent / 'ReferenceBindingTests/Program.cs').read_text()
        literal = set(re.findall(r'Test\("(N-[^"+]+)"', text))
        self.assertEqual(literal, set(replay.CASE_IDS[6:]))
        self.assertEqual(tuple('N-' + n + '-unchanged-closed-domain' for n in replay.KINDS), replay.CASE_IDS[:6])
        self.assertEqual(len(set(replay.CASE_IDS)), 15)


if __name__ == '__main__':
    unittest.main()
