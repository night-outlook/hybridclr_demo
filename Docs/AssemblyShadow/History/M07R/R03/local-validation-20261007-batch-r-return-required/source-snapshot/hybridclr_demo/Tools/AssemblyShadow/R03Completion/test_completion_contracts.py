"""Synthetic policy/negative tests, never fabricated Unity or Player evidence."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fixture_project as fixture
import fixture_authority as authority
import resource_pipeline as pipeline
import editor_contract as editor
import execution_contract as execution
import legacy_runtime as legacy
import run_completion as runner
from batch_contract import ContractError, loads, sha
from batch_evidence import write


def digest(data):
    return hashlib.sha256(data).hexdigest()


class SourceFixtureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.workspace = self.root / 'workspace'
        self.demo = self.workspace / 'hybridclr_demo'
        self.real = HERE.parents[2]
        self.rows = []
        # Actual committed-source-shaped bytes, but a synthetic Git response.
        # This is a copy-policy test, not real source authority or a Player run.
        candidates = {self.real / name for name in fixture.SETTINGS}
        for relative in fixture.ROOTS:
            candidates.add(self.real / (relative + '.meta'))
            candidates.update((self.real / relative).rglob('*'))
        candidates.update({self.real / 'Assets/HybridCLRGenerate/link.xml', self.real / 'Assets/HybridCLRGenerate/link.xml.meta'})
        for source in sorted(candidates):
            if not source.is_file() or not fixture.select(source.relative_to(self.real).as_posix()):
                continue
            relative = source.relative_to(self.real).as_posix()
            target = self.demo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
            self.rows.append('100644 blob ' + fixture.blob(source.read_bytes()) + '\t' + relative)
        # SourcePins is tracked in Git but deliberately regenerated, not copied.
        pin_source = self.real / 'ProjectSettings/AssemblyShadowSourcePins.json'
        self.rows.append('100644 blob ' + fixture.blob(pin_source.read_bytes()) + '\tProjectSettings/AssemblyShadowSourcePins.json')
        (self.demo / 'Packages').mkdir(parents=True)
        shutil.copyfile(self.real / 'Packages/manifest.json', self.demo / 'Packages/manifest.json')
        shutil.copyfile(self.real / 'Packages/packages-lock.json', self.demo / 'Packages/packages-lock.json')
        self.commit = '1' * 40
        def synthetic_git(root, *args):
            if args == ('rev-parse', 'HEAD'): return self.commit
            if args == ('ls-tree', '-r', '--full-tree', 'HEAD'): return '\n'.join(self.rows)
            raise AssertionError('Unexpected synthetic Git command: ' + repr(args))
        self.fakegit = mock.patch.object(fixture, 'git', side_effect=synthetic_git)
        self.fakegit.start(); self.addCleanup(self.fakegit.stop)
        pins = {name: self.commit for name in fixture.REPOS}
        pins.update(branch='codex/assembly-shadow-r01b-h1')
        self.batch = SimpleNamespace(workspace=self.workspace, root=self.root / 'batch', pins=pins)

    def test_original_frozen_asset_copy_and_pin_binding(self):
        project, config = fixture.provision(self.batch)
        result = fixture.verify_sources(project, config)
        self.assertEqual(result['frozenM01Files'], 6)
        self.assertFalse(config['expansionAuthorized'])
        self.assertEqual(set(fixture.source_pins(self.batch, project)),
                         {'schemaVersion', 'unityVersion', 'target', 'architecture', 'demo', 'hybridclr', 'hybridclrUnity', 'il2cppPlus'})
        self.assertEqual(fixture.source_pins(self.batch, project)['architecture'], 'arm64')

    def test_wrong_source_commit_rejected(self):
        with self.assertRaisesRegex(ContractError, 'commit changed'):
            fixture.source_catalog(self.demo, '2' * 40)

    def test_changed_frozen_bytes_rejected_before_copy(self):
        (self.demo / next(iter(fixture.FROZEN))).write_text('changed')
        with self.assertRaisesRegex(ContractError, 'Source differs'):
            fixture.provision(self.batch)

    def test_changed_frozen_metadata_rejected_after_copy(self):
        project, config = fixture.provision(self.batch)
        (project / 'Assets/AssemblyShadowDemo/Scenes/Business.unity.meta').write_text('guid: wrong')
        with self.assertRaises(ContractError): fixture.verify_sources(project, config, configured=True)

    def test_used_project_root_not_deleted_or_overwritten(self):
        project = self.batch.root / 'projects/resource-complete'
        project.mkdir(parents=True); (project / 'sentinel').write_text('retain')
        with self.assertRaises(ContractError): fixture.provision(self.batch)
        self.assertEqual((project / 'sentinel').read_text(), 'retain')

    def test_symlink_source_rejected(self):
        path = self.demo / next(iter(fixture.FROZEN)); path.unlink()
        target = self.root / 'other'; target.write_text('outside')
        path.symlink_to(target)
        with self.assertRaisesRegex(ContractError, 'regular source'):
            fixture.provision(self.batch)

    def test_configuration_changes_require_explicit_phase(self):
        project, config = fixture.provision(self.batch)
        path = project / 'ProjectSettings/ProjectSettings.asset'
        path.write_text(path.read_text() + '\n# configured\n')
        with self.assertRaises(ContractError): fixture.verify_sources(project, config)
        result = fixture.verify_sources(project, config, configured=True)
        self.assertEqual(len(result['allowedConfigurationChanges']), 1)

    def test_business_source_not_mutable_configuration(self):
        project, config = fixture.provision(self.batch)
        path = next(project.glob('Assets/AssemblyShadowDemo/**/*.cs'))
        path.write_text(path.read_text() + '\n// unexpected\n')
        with self.assertRaises(ContractError): fixture.verify_sources(project, config, configured=True)

    def test_manifest_or_source_pin_mutation_is_rejected(self):
        project, config = fixture.provision(self.batch)
        for relative in ('Packages/manifest.json', 'ProjectSettings/AssemblyShadowSourcePins.json'):
            path = project / relative; original = path.read_bytes()
            path.write_bytes(original + b' ')
            with self.assertRaises(ContractError): fixture.verify_sources(project, config, configured=True)
            path.write_bytes(original)

    def test_unsupported_git_entry_mode_fails(self):
        self.rows[0] = self.rows[0].replace('100644', '120000', 1)
        with self.assertRaises(ContractError): fixture.source_catalog(self.demo)

    def test_urp_dependency_is_not_substituted(self):
        path = self.demo / 'Packages/manifest.json'; value = loads(path.read_text())
        value['dependencies']['com.unity.render-pipelines.universal'] = 'latest'
        path.write_text(json.dumps(value))
        with self.assertRaises(ContractError): fixture.dependencies(self.demo, self.workspace / 'hybridclr_unity')

    def test_extra_executable_source_cannot_evade_copy_authority(self):
        project, config = fixture.provision(self.batch)
        injected = project / 'Assets/Injected.cs'; injected.write_text('class Injected {}')
        def fake_owner_git(repo, *args):
            if args == ('rev-parse', '--show-toplevel'): return str(repo)
            if args == ('rev-parse', 'HEAD'): return self.commit
            if args == ('branch', '--show-current'): return self.batch.pins['branch']
            if args[:1] == ('status',): return ''
            if args == ('config', '--get', 'remote.origin.url'): return 'git@github.com:night-outlook/' + repo.name + '.git'
            if args[:1] == ('ls-remote',): return self.commit + '\trefs/heads/' + self.batch.pins['branch']
            raise AssertionError(args)
        with mock.patch.object(authority, 'git', side_effect=fake_owner_git):
            with self.assertRaisesRegex(ContractError, 'Unbound source'):
                authority.authenticate_copy(self.batch, config)


class EditorSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.demo = HERE.parents[2]
        cls.catalog = ET.parse(cls.demo / editor.prior.REFERENCE).getroot()
        cls.ids = sorted(node.get('fullname').split('("')[1].split('")')[0]
                         for node in cls.catalog.iter('test-case') if node.get('fullname', '').startswith(editor.prior.PREFIX + '('))
        if len(cls.ids) != 35: raise AssertionError('Real immutable R03 catalog')

    def scope(self, complete=True):
        def git(_, *args):
            return '2' * 40 if args[:1] == ('rev-parse',) else '\n'.join(sorted(editor.REVIEWED_PACKAGE_FILES))
        with mock.patch.object(editor, 'git', side_effect=git):
            return editor.source_scope(self.demo, Path('/unit/package'), '2' * 40, self.ids, resource_complete=complete)

    def xml(self, scope):
        # Unit XML only, explicitly not produced as fresh runtime evidence.
        count = len(scope['expectedNames'])
        root = ET.Element('test-run', result='Passed', total=str(count), passed=str(count), failed='0', skipped='0', inconclusive='0')
        for name in scope['expectedNames']: ET.SubElement(root, 'test-case', fullname=name, result='Passed')
        return root

    def test_full_m01_identity_is_required(self):
        scope = self.scope(); result = editor.verify(self.xml(scope), scope)
        self.assertEqual(result['cases'], 755)
        self.assertEqual(result['m01Case'], editor.prior.EXCLUDED)
        self.assertEqual(scope['excluded'], [])
        self.assertFalse(result['R03Accepted'])

    def test_original_focused_scope_retains_explicit_no_coverage(self):
        scope = self.scope(False); result = editor.verify(self.xml(scope), scope)
        self.assertEqual(result['cases'], 754)
        self.assertEqual(result['excludedCoverage'][0]['coverage'], 'NoCoverage')

    def test_missing_m01_case_fails(self):
        scope = self.scope(); xml = self.xml(scope)
        xml.remove(next(c for c in xml if c.get('fullname') == editor.prior.EXCLUDED))
        with self.assertRaises(ContractError): editor.verify(xml, scope)

    def test_ignored_m01_case_fails(self):
        scope = self.scope(); xml = self.xml(scope)
        node = next(c for c in xml if c.get('fullname') == editor.prior.EXCLUDED)
        node.set('result', 'Skipped'); node.set('label', 'Ignored')
        with self.assertRaises(ContractError): editor.verify(xml, scope)

    def test_count_or_aggregate_mutation_fails(self):
        scope = self.scope()
        for field, value in (('passed', '754'), ('skipped', '1'), ('result', 'Failed'), ('label', 'Ignored')):
            xml = self.xml(scope); xml.set(field, value)
            with self.assertRaises(ContractError): editor.verify(xml, scope)

    def test_duplicate_or_substituted_name_fails(self):
        scope = self.scope()
        for name in (scope['expectedNames'][1], 'UnexpectedCase'):
            xml = self.xml(scope); xml[0].set('fullname', name)
            with self.assertRaises(ContractError): editor.verify(xml, scope)

    def test_additional_package_source_change_requires_review(self):
        def git(_, *args):
            return '2' * 40 if args[:1] == ('rev-parse',) else '\n'.join([*editor.REVIEWED_PACKAGE_FILES, 'Tests/Weakened.cs'])
        with mock.patch.object(editor, 'git', side_effect=git):
            with self.assertRaisesRegex(ContractError, 'additional package change'):
                editor.source_scope(self.demo, '/unit/package', '2' * 40, self.ids, resource_complete=True)


class StructuralRestoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name).resolve() / 'project'
        self.run = self.project / '_temp/AssemblyShadow/M02Validation-unit'
        self.run.mkdir(parents=True)
        (self.project / 'ProjectSettings').mkdir()
        self.settings = self.project / 'ProjectSettings/ProjectSettings.asset'
        self.settings.write_bytes(b'unity reserialized')
        (self.run / 'p05-project-settings.original').write_bytes(b'original settings')
        state = {'schemaVersion': 2, 'projectDirectory': str(self.project), 'runDirectory': str(self.run),
                 'originalDefines': 'ORIGINAL', 'originalSettingsSha256': digest(b'original settings')}
        write(self.run / 'p05-define-state.json', state)
        receipt = {'schemaVersion': 2, 'stateSha256': sha(self.run / 'p05-define-state.json'), 'originalDefines': 'ORIGINAL',
                   'originalSettingsSha256': digest(b'original settings'), 'restoredSettingsSha256': sha(self.settings)}
        write(self.run / 'p05-restored.json', receipt)

    def test_original_bytes_restored_without_rewriting_receipt(self):
        before = (self.run / 'p05-restored.json').read_bytes()
        result = pipeline.restore_bytes(self.project, self.run)
        self.assertEqual(self.settings.read_bytes(), b'original settings')
        self.assertEqual((self.run / 'p05-unity-restored.bytes').read_bytes(), b'unity reserialized')
        self.assertEqual((self.run / 'p05-restored.json').read_bytes(), before)
        self.assertEqual(result['result'], 'ExactOriginalBytesRestored')
        wrapper = loads((self.run / 'p05-settings-restored.json').read_text())
        self.assertEqual(wrapper['restoredSettingsSha256'], digest(b'unity reserialized'))

    def test_concurrent_settings_edit_is_not_overwritten(self):
        self.settings.write_bytes(b'unrelated edit')
        with self.assertRaisesRegex(ContractError, 'Concurrent settings edit'):
            pipeline.restore_bytes(self.project, self.run)
        self.assertEqual(self.settings.read_bytes(), b'unrelated edit')

    def test_changed_backup_is_not_restored(self):
        (self.run / 'p05-project-settings.original').write_bytes(b'wrong original')
        with self.assertRaises(ContractError): pipeline.restore_bytes(self.project, self.run)
        self.assertEqual(self.settings.read_bytes(), b'unity reserialized')

    def test_wrong_state_receipt_hash_fails(self):
        state = self.run / 'p05-define-state.json'; state.write_bytes(state.read_bytes() + b' ')
        with self.assertRaises(ContractError): pipeline.restore_bytes(self.project, self.run)

    def test_repeated_restore_fails(self):
        pipeline.restore_bytes(self.project, self.run)
        with self.assertRaises(ContractError): pipeline.restore_bytes(self.project, self.run)

    def test_escape_run_fails(self):
        with self.assertRaises(ContractError): pipeline.restore_bytes(self.project, self.run.parent.parent)

    def test_exact_production_cli_flag_is_used(self):
        b = SimpleNamespace(unity='/unit/Unity', root=self.run.parent, resource_config={
            'projectPath': str(self.project), 'baselineId': 'M07-Baseline-Unit', 'runPath': str(self.run)})
        args = pipeline.command(b, 'compile')
        self.assertEqual(args[args.index('-shadowValidationRoot') + 1], str(self.run))
        self.assertNotIn('-shadowM02RunDir', args)


class CommandLifetimeTests(unittest.TestCase):
    def invoke(self, code, expected, **mutations):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); folder = root / 'player'; folder.mkdir()
            class Batch:
                command_count = 0
                def command(self, args, timeout):
                    self.command_count += 1
                    path = root / 'commands/0001'; path.mkdir(parents=True)
                    (path / 'stdout.log').write_bytes(b'stdout'); (path / 'stderr.log').write_bytes(b'stderr')
                    value = {'schemaVersion': 2, 'lifetimePolicy': 'R03OwnedCommandV1', 'exitCode': code,
                        'timeout': False, 'remainingProcessGroup': False, 'postCleanupGroupExists': False,
                        'interrupted': False, 'startError': None, 'cleanupErrors': [], 'command': [str(x) for x in args],
                        'stdoutSha256': sha(path / 'stdout.log'), 'stderrSha256': sha(path / 'stderr.log'), 'pid': 123}
                    value.update(mutations); write(path / 'command.json', value)
                    if code or mutations: raise RuntimeError('Synthetic command failure')
                    return value
            batch = Batch(); batch.root = root
            return legacy.launch(batch, ['/unit/app', '-mode', 'test'], folder, expected)

    def test_exact_expected_early_rejection_exit_preserved(self):
        row, binding = self.invoke(1, 1)
        self.assertEqual(row['exitCode'], 1)
        self.assertTrue(binding['commandSha256'])

    def test_success_is_not_an_expected_rejection(self):
        with self.assertRaises(ContractError): self.invoke(0, 1)

    def test_unexpected_failure_is_not_swallowed(self):
        with self.assertRaises(RuntimeError): self.invoke(1, 0)

    def test_survivor_cleanup_cannot_override_rejection(self):
        for fields in ({'remainingProcessGroup': True}, {'postCleanupGroupExists': True}, {'timeout': True},
                       {'cleanupErrors': ['failure']}, {'interrupted': True}, {'startError': 'missing'}):
            with self.assertRaises(ContractError): self.invoke(1, 1, **fields)

    def test_expectation_must_be_explicit_integer(self):
        with self.assertRaises(ContractError): self.invoke(0, True)

    def test_command_and_stream_binding_are_not_optional(self):
        for change in ({'command': ['/different']}, {'stdoutSha256': '0' * 64}):
            with self.assertRaises(ContractError): self.invoke(1, 1, **change)


class OrchestrationTests(unittest.TestCase):
    def test_ninety_unique_cells_preserve_original_matrix(self):
        matrix = loads((HERE.parent / 'R03/player-cases.json').read_text())
        names = runner.cell_plan(matrix)
        self.assertEqual(len(names), 90)
        self.assertEqual(len(set(names)), 90)
        self.assertEqual(len(legacy.m07.MODES), 14)
        self.assertEqual(len(legacy.r00.MODES) * 3, 12)
        self.assertEqual(len(legacy.EARLY_CASES), 10)
        self.assertTrue({'producer-controls', 'resource-p05-restore', 'production-entry-integration'} <= set(names))
        self.assertTrue({row['id'] for row in matrix['cases']} <= set(names))

    def test_duplicate_matrix_cannot_change_count(self):
        matrix = loads((HERE.parent / 'R03/player-cases.json').read_text())
        matrix['cases'][0] = matrix['cases'][1]
        with self.assertRaises(ContractError): runner.cell_plan(matrix)

    def test_resource_pipeline_does_not_depend_on_static_qualification(self):
        source = (HERE / 'run_completion.py').read_text()
        self.assertIn("self.cell('resource-prepare', lambda: resources.prepare(self), ('entry-authority', 'completion-tool-contracts'))", source)
        self.assertNotIn("self.cell('resource-prepare', lambda: resources.prepare(self), ('entry-authority', 'completion-tool-contracts', 'qualification'))", source)

    def test_resource_restore_and_editor_continue_after_compile_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            batch = object.__new__(runner.CompletionBatch)
            batch.root = Path(directory); batch.workspace = Path('/unit/workspace')
            batch.pins = {}; batch.references = {}; batch.cells = []; batch.outputs = {}; batch.failed = False
            batch.matrix = loads((HERE.parent / 'R03/player-cases.json').read_text()); batch.planned = runner.cell_plan(batch.matrix)
            batch.authority = lambda: {}; batch.completion_tests = lambda: {}; batch.python_tests = lambda: {}
            batch.reference_worktrees = lambda: batch.references.update(hybridclr_unity=Path('/unit/reference')) or {}
            batch.managed = lambda *a, **k: {}; batch.prepare_project = lambda *a, **k: {}; batch.build = lambda *a, **k: {}
            batch.player = lambda *a, **k: {}; batch.producer_controls = lambda: {}
            observed = []
            def phase(_, name):
                observed.append(name)
                if name == 'compile': raise RuntimeError('Synthetic failed compiler')
                return {}
            with contextlib.ExitStack() as stack:
                stack.enter_context(mock.patch.object(runner, 'qualification', return_value={}))
                stack.enter_context(mock.patch.object(runner, 'validate_inputs', return_value={}))
                stack.enter_context(mock.patch.object(runner, 'sha', return_value='0' * 64))
                stack.enter_context(mock.patch.object(runner, 'finalize', side_effect=lambda root, report: dict(report, sealStatus='Passed')))
                for name in ('prepare', 'integration', 'graph'):
                    stack.enter_context(mock.patch.object(runner.resources, name, return_value={}))
                stack.enter_context(mock.patch.object(runner.resources, 'phase', side_effect=phase))
                stack.enter_context(mock.patch.object(runner.resources, 'restore', side_effect=lambda _: observed.append('restore') or {}))
                stack.enter_context(mock.patch.object(runner.resources, 'editor', side_effect=lambda _, complete: observed.append('editor-complete' if complete else 'editor-focused') or {}))
                for name in ('m07_case', 'm07_summary', 'r00_case', 'measurements', 'early_case'):
                    stack.enter_context(mock.patch.object(runner.legacy, name, return_value={}))
                with contextlib.redirect_stdout(io.StringIO()): code = batch.execute()
            states = {row['id']: row['result'] for row in batch.cells}
            self.assertEqual(code, 1)
            self.assertEqual(states['resource-p05-compile'], 'Failed')
            self.assertEqual(states['resource-p05-restore'], 'Passed')
            self.assertEqual(states['resource-editor'], 'Passed')
            self.assertEqual(states['resource-p05-finalize'], 'Blocked')
            self.assertEqual(states['C07-private-primitive-append'], 'Passed')
            self.assertEqual(observed.count('compile'), 1)
            self.assertEqual(observed.count('restore'), 1)
            self.assertEqual(len(states), 90)


class NativeProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve(); self.installed = self.root / 'libil2cpp'; self.installed.mkdir()
        self.paths = {name: self.root / name for name in authority.PIN_NAMES}
        self.paths['hybridclrUnity'].mkdir()
        write(self.paths['hybridclrUnity'] / 'package.json', {'name': authority.original.PACKAGE, 'version': '8.14.1'})
        self.pins = {'unityVersion': '2022.3.62f2', 'target': 'StandaloneOSX'}
        self.pins.update({key: {'url': 'https://github.com/night-outlook/' + name + '.git', 'revision': '1' * 40, 'localPath': '../' + name}
                          for key, name in zip(authority.PIN_NAMES, authority.DIR_NAMES)})
        headers = {'AssemblyShadowConfig.h': '#ifndef HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW\n#define HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW 0\n#endif\n',
                   'il2cpp-config.h': '#include "AssemblyShadowConfig.h"\n'}
        self.expected = {}
        for name in sorted(set(headers) | authority.original.GENERATED):
            path = self.installed / name; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(headers.get(name, 'original generated input'))
            self.expected[name] = {'source': 'il2cppPlus', 'sha256': sha(path)}
        self.receipt = {'schemaVersion': 1, 'installMode': 'PinnedLocal', 'unityVersion': '2022.3.62f2',
            'target': 'StandaloneOSX', 'repositories': {key: self.pins[key] for key in authority.PIN_NAMES},
            'packageRevision': '1' * 40, 'packageVersion': '8.14.1', 'generatedFileExclusions': sorted(authority.original.GENERATED),
            'sourceFileHashes': [dict(path=name, **row) for name, row in sorted(self.expected.items())],
            'defaultShadowMacro': 0, 'defaultShadowMacroSource': 'AssemblyShadowConfig.h'}
        self.save()
        self.patch = mock.patch.object(authority.original, 'source_inventory', return_value=self.expected)
        self.patch.start(); self.addCleanup(self.patch.stop)

    def save(self):
        # Deliberate synthetic tamper input for a negative unit case.
        (self.installed / authority.original.RECEIPT).write_text(json.dumps(self.receipt))

    def verify(self):
        return authority.verify_native_inventory(self.installed, self.pins, self.paths)

    def test_exact_inventory_and_only_generated_changes(self):
        for name in authority.original.GENERATED: (self.installed / name).write_text('fresh generated output')
        result = self.verify()
        self.assertEqual(result['installedFiles'], len(self.expected) + 1)
        self.assertFalse(result['probeEnabled'])

    def test_unbound_file_cannot_join_installed_source(self):
        (self.installed / 'Injected.cpp').write_text('untracked native change')
        with self.assertRaises(ContractError): self.verify()

    def test_changed_non_generated_bytes_fail(self):
        (self.installed / 'il2cpp-config.h').write_text('different')
        with self.assertRaises(ContractError): self.verify()

    def test_duplicate_receipt_entry_fails(self):
        self.receipt['sourceFileHashes'].append(self.receipt['sourceFileHashes'][0]); self.save()
        with self.assertRaises(ContractError): self.verify()

    def test_generated_exclusion_cannot_expand(self):
        self.receipt['generatedFileExclusions'].append('il2cpp-config.h'); self.save()
        with self.assertRaises(ContractError): self.verify()

    def test_installation_source_tuple_cannot_change(self):
        self.receipt['repositories'] = copy.deepcopy(self.receipt['repositories'])
        self.receipt['repositories']['il2cppPlus']['revision'] = '2' * 40; self.save()
        with self.assertRaises(ContractError): self.verify()

    def test_default_on_is_not_admitted_as_normal_source(self):
        self.receipt['defaultShadowMacro'] = 1; self.save()
        with self.assertRaises(ContractError): self.verify()

    def test_installed_symlink_is_not_resolved_away(self):
        path = self.installed / 'il2cpp-config.h'; path.unlink()
        other = self.root / 'elsewhere'; other.write_text('#include "AssemblyShadowConfig.h"\n'); path.symlink_to(other)
        with self.assertRaises(RuntimeError): self.verify()


class SupplementTests(unittest.TestCase):
    def example(self):
        req = {'schemaVersion': 1, 'kind': 'R03ExecutionSupplement', 'runId': '1' * 32, 'mode': 'R00-ON-P03'}
        original = {'mode': req['mode'], 'processId': 123, 'buildGuid': 'guid', 'featureEnabled': True, 'transactionCommitted': True}
        extra = {'schemaVersion': 1, 'kind': req['kind'], 'runId': req['runId'], 'mode': req['mode'],
                 'requestSha256': '2' * 64, 'r00Sha256': '3' * 64, 'processId': 123, 'buildGuid': 'guid', 'il2cpp': True,
                 'R03Accepted': False, 'H2Passed': False, 'result': 'Observed', 'error': '', 'featureEnabled': True,
                 'transactionCommitted': True, 'typeName': execution.m06.witness(execution.m06.INTERNAL),
                 'diagnosticsCode': 'Success', 'diagnostics': json.dumps({'isActive': True, 'logicalAssembly': execution.m06.INTERNAL,
                                                                         'executionMode': 'InterpreterShadow'}),
                 'observations': [{'phase': p, 'repetition': r, 'values': ['unit']} for p in ('statics', 'delegates', 'exceptions') for r in range(2)]}
        return req, extra, original

    def verify(self, req, extra, original):
        with mock.patch.object(execution, 'selected_image', return_value={'identity': 'selected-unit-dll', 'pdbAvailable': True}), \
             mock.patch.object(execution.m06, 'verify_business') as business, mock.patch.object(execution.m06, 'verify_exception') as exception:
            result = execution.verify(req, extra, original, '2' * 64, '3' * 64, 123, {})
            self.assertEqual(business.call_count, 4); self.assertEqual(exception.call_count, 2)
            # The exception verifier must require the actual patched DLL/PDB.
            self.assertTrue(all(call.args[-2:] == (True, True) for call in exception.call_args_list))
            self.assertFalse(result['measuredIntervalIncludesSupplement'])
            return result

    def test_original_business_and_exception_rules_invoked(self):
        self.assertEqual(self.verify(*self.example())['phases'], 6)

    def test_supplement_process_or_source_mutation_rejected(self):
        for key, value in (('processId', 999), ('requestSha256', '0' * 64), ('r00Sha256', '0' * 64),
                           ('transactionCommitted', False), ('R03Accepted', True), ('error', 'failure')):
            req, extra, original = self.example(); extra[key] = value
            with self.assertRaises(ContractError): self.verify(req, extra, original)

    def test_incomplete_or_reordered_phases_rejected(self):
        for reorder in (False, True):
            req, extra, original = self.example()
            extra['observations'] = list(reversed(extra['observations'])) if reorder else extra['observations'][:-1]
            with self.assertRaises(ContractError): self.verify(req, extra, original)

    def test_failure_inside_original_verifier_is_not_suppressed(self):
        req, extra, original = self.example()
        with mock.patch.object(execution, 'selected_image', return_value={}), \
             mock.patch.object(execution.m06, 'verify_business', side_effect=ValueError('real rule failed')):
            with self.assertRaisesRegex(ValueError, 'real rule failed'):
                execution.verify(req, extra, original, '2' * 64, '3' * 64, 123, {})

    def test_source_hook_does_not_change_original_benchmark_or_force_gc(self):
        source = (HERE.parents[2] / 'Assets/AssemblyShadowDemo/Bootstrap/R03CompletionExecution.cs').read_text()
        self.assertIn('Application.wantsToQuit += OnQuit', source)
        self.assertIn('File.Exists(originalPath)', source)
        self.assertIn('FileMode.CreateNew', source)
        for forbidden in ('GC.Collect(', 'GC.WaitForPendingFinalizers(', 'R03_BeginWarmProbe', 'ProducerFence', 'Application.Quit('):
            self.assertNotIn(forbidden, source)
        self.assertEqual(source.count('Application.wantsToQuit -= OnQuit'), 1)


if __name__ == '__main__':
    unittest.main()
