"""Synthetic verifier regressions, not actual Unity execution evidence."""
import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'R03'))
from batch_contract import ContractError, sha
from batch_evidence import write
import fixture_project
import fixture_contracts
import source_pin_contract as contract


class SourcePinTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.project = self.root / 'batch/projects/resource-complete'; self.project.mkdir(parents=True)
        self.batch = SimpleNamespace(workspace=self.root / 'workspace', pins={repo: str(i + 1) * 40 for i, repo in enumerate(contract.REPOSITORIES.values())},
                                     resource_config={'baselineId': 'unit-baseline'})
        self.pins = fixture_project.source_pins(self.batch, self.project)

    def verify(self, value=None):
        return contract.validate_document(self.pins if value is None else value, self.batch, self.project)

    def test_generated_architecture_matches_independent_platform_contract(self):
        self.assertEqual(self.verify()['architecture'], 'arm64')
        self.assertEqual({k: self.pins[k] for k in contract.PLATFORM}, contract.PLATFORM)

    def test_missing_architecture_is_rejected(self):
        del self.pins['architecture']
        with self.assertRaises(ContractError): self.verify()

    def test_wrong_null_or_blank_architecture_is_rejected(self):
        for value in ('x64', '', None, 64):
            with self.subTest(value=value):
                self.pins['architecture'] = value
                with self.assertRaises(ContractError): self.verify()

    def test_wrong_unity_target_or_schema_is_rejected(self):
        for key, value in (('unityVersion', 'wrong'), ('target', 'StandaloneWindows64'), ('schemaVersion', 2), ('schemaVersion', True)):
            with self.subTest(key=key, value=value):
                pins = copy.deepcopy(self.pins); pins[key] = value
                with self.assertRaises(ContractError): self.verify(pins)

    def test_extra_or_missing_platform_field_is_rejected(self):
        for mutation in ('extra', 'missing'):
            pins = copy.deepcopy(self.pins)
            if mutation == 'extra': pins['cpu'] = 'arm64'
            else: del pins['target']
            with self.assertRaises(ContractError): self.verify(pins)

    def test_each_wrong_repository_revision_is_rejected(self):
        for field in contract.REPOSITORIES:
            pins = copy.deepcopy(self.pins); pins[field]['revision'] = 'f' * 40
            with self.assertRaises(ContractError): self.verify(pins)

    def test_each_wrong_repository_owner_is_rejected(self):
        for field in contract.REPOSITORIES:
            pins = copy.deepcopy(self.pins); pins[field]['url'] = 'https://github.com/other/repo.git'
            with self.assertRaises(ContractError): self.verify(pins)

    def test_each_missing_repository_or_local_owner_is_rejected(self):
        for field in contract.REPOSITORIES:
            pins = copy.deepcopy(self.pins); pins[field] = None
            with self.assertRaises(ContractError): self.verify(pins)
            pins = copy.deepcopy(self.pins); pins[field]['localPath'] = '/another/root'
            with self.assertRaises(ContractError): self.verify(pins)

    def report(self):
        for name in contract.INPUTS:
            p = self.project / name; p.parent.mkdir(parents=True, exist_ok=True)
            if name == contract.INPUTS[0]: write(p, self.pins)
            else: p.write_text('synthetic unit input\n')
        folder = self.project / '_temp/contracts'; folder.mkdir(parents=True)
        rows = []
        for id, code in contract.CODES.items():
            path = self.project / contract.INPUTS[0] if id == 'generated' else folder / 'source-pin-contract-inputs' / (id + '.json')
            if id != 'generated': write(path, {'unitOnly': id})
            rows.append({'id': id, 'path': str(path), 'sha256': sha(path), 'expectedCode': code, 'observedCode': code, 'result': 'Passed'})
        inputs = [{'path': p, 'sha256': sha(self.project / p)} for p in contract.INPUTS]
        value = {'kind': 'R03ProductionSourcePinContract', 'schemaVersion': 1, 'result': 'Passed',
                 'projectPath': str(self.project), 'baselineId': 'unit-baseline', **contract.PLATFORM,
                 'consumer': 'HybridCLR.Editor.AssemblyShadow.ShadowSourcePins.Read', 'serialization': 'UnityEngine.JsonUtility',
                 'unityEditorRun': True, 'nativeInstallationRun': False, 'R03Accepted': False, 'H2Passed': False,
                 'expansionAuthorized': False, 'cases': rows, 'before': inputs, 'after': copy.deepcopy(inputs), 'runtimeAbiHash': 'a' * 64}
        return folder / 'source-pin-contract.json', value

    def verify_report(self, path, value):
        path.write_text(json.dumps(value)); return contract.verify_report(path, self.batch, self.project)

    def test_receipt_validator_accepts_exact_synthetic_contract(self):
        self.assertEqual(self.verify_report(*self.report())['cases'], 10)

    def test_receipt_rejects_wrong_negative_code(self):
        path, value = self.report(); value['cases'][2]['observedCode'] = 'Success'
        with self.assertRaises(ContractError): self.verify_report(path, value)

    def test_receipt_rejects_missing_or_duplicate_case(self):
        path, value = self.report(); value['cases'][1] = value['cases'][0]
        with self.assertRaises(ContractError): self.verify_report(path, value)

    def test_receipt_rejects_changed_consumed_bytes(self):
        path, value = self.report(); Path(value['cases'][1]['path']).write_text('changed')
        with self.assertRaises(ContractError): self.verify_report(path, value)

    def test_receipt_rejects_changed_settings(self):
        path, value = self.report(); (self.project / contract.INPUTS[1]).write_text('changed')
        with self.assertRaises(ContractError): self.verify_report(path, value)

    def test_receipt_rejects_fake_consumer_or_authority(self):
        path, value = self.report()
        for key, bad in (('consumer', 'FakeReader'), ('serialization', 'FakeJson'), ('unityEditorRun', False),
                         ('nativeInstallationRun', True), ('expansionAuthorized', True), ('R03Accepted', True)):
            changed = copy.deepcopy(value); changed[key] = bad
            with self.assertRaises(ContractError): self.verify_report(path, changed)

    def test_receipt_rejects_outside_or_symlink_input(self):
        path, value = self.report(); original = Path(value['cases'][1]['path']); outside = self.root / 'other.json'
        outside.write_bytes(original.read_bytes()); original.unlink(); original.symlink_to(outside)
        with self.assertRaises(ContractError): self.verify_report(path, value)

    def test_actual_I_generator_output_remains_rejected(self):
        # Immutable fixture evidence is only read; no old record is repaired.
        checkpoint = HERE.parents[2] / 'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261003-batch-i-return-required'
        candidates = list((checkpoint / 'preflight/issue-resource-snapshot').rglob('AssemblyShadowSourcePins.json'))
        self.assertEqual(len(candidates), 1)
        legacy = json.loads(candidates[0].read_text()); self.assertNotIn('architecture', legacy)
        with self.assertRaises(ContractError): self.verify(legacy)

    def test_real_production_read_guards_unchanged_in_source(self):
        package = HERE.parents[3] / 'hybridclr_unity'
        text = (package / 'Editor/AssemblyShadow/Build/ShadowSourcePins.cs').read_text()
        self.assertIn('public string architecture;', text)
        self.assertIn('pins.architecture == architecture', text)
        self.assertIn('JsonUtility.FromJson<ShadowSourcePins>', text)
        self.assertIn('"SourcePinTarget"', text)

    def test_adapter_reads_before_configure_and_native_install(self):
        demo = HERE.parents[2]
        pipeline = (HERE / 'resource_pipeline.py').read_text()
        self.assertLess(pipeline.index("proof = unity_command(batch, command(batch, 'source-pin-preflight')"),
                        pipeline.index("receipt = unity_command(batch, command(batch, name)"))
        consumer = (demo / 'Assets/AssemblyShadowDemo/Editor/R03CompletionSourcePinContract.cs').read_text()
        self.assertIn('ShadowSourcePins.Read(path, BuildTarget.StandaloneOSX, "arm64")', consumer)
        self.assertIn('ShadowSourcePins.RequireSameBuildSources(baseline, value)', consumer)
        self.assertNotIn('PinnedSourceInstaller.Install', consumer)
        self.assertNotIn('M07Build.Configure', consumer)
        self.assertNotIn('JsonConvert.', consumer)


class FixtureRosterTests(unittest.TestCase):
    def tree(self):
        names = fixture_contracts.roster()
        tree = ET.Element('test-run', result='Passed', total='18', passed='18', failed='0', skipped='0', inconclusive='0')
        for name in names: ET.SubElement(tree, 'test-case', fullname=name, result='Passed')
        return tree, names

    def test_exact_editor_subset_is_additional_not_a_full_roster_replacement(self):
        self.assertFalse(fixture_contracts.verify_editor(*self.tree())['fullEditorRosterReplaced'])

    def test_any_failed_skipped_or_labelled_fixture_is_rejected(self):
        for key, value in (('result', 'Failed'), ('result', 'Skipped'), ('label', 'Ignored')):
            tree, names = self.tree(); tree[0].set(key, value)
            with self.assertRaises(ContractError): fixture_contracts.verify_editor(tree, names)

    def test_missing_duplicate_substituted_fixture_is_rejected(self):
        for mode in ('missing', 'duplicate', 'other'):
            tree, names = self.tree()
            if mode == 'missing': tree.remove(tree[0])
            else: tree[0].set('fullname', tree[1].get('fullname') if mode == 'duplicate' else 'Other.Test')
            with self.assertRaises(ContractError): fixture_contracts.verify_editor(tree, names)

    def test_editor_aggregate_must_match_all_eighteen(self):
        tree, names = self.tree(); tree.set('total', '754')
        with self.assertRaises(ContractError): fixture_contracts.verify_editor(tree, names)

    def test_original_failed_I_names_are_preserved_exactly(self):
        xml = HERE.parents[2] / 'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261003-batch-i-return-required/batch/focused-editor/results.xml'
        names = sorted(c.get('fullname') for c in ET.parse(xml).iter('test-case') if c.get('result') == 'Failed')
        self.assertEqual(names, fixture_contracts.roster())

    def test_single_checked_reflection_boundary_for_package_fixtures(self):
        package = HERE.parents[3] / 'hybridclr_unity'
        paths = list((package / 'Tests/Editor/AssemblyShadow').rglob('*.cs'))
        users = [p for p in paths if 'typeof(CompiledAssemblySet)' in p.read_text()]
        self.assertEqual([p.name for p in users], ['SyntheticCompiledAssemblySet.cs'])
        text = users[0].read_text()
        self.assertIn('typeof(IEnumerable<CompiledAssemblySource>)', text)
        self.assertIn('Array.Empty<CompiledAssemblySource>()', text)
        self.assertNotIn('GetConstructors(', text)


if __name__ == '__main__': unittest.main()
