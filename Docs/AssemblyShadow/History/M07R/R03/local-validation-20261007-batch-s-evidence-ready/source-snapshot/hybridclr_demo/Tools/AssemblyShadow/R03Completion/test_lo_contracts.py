"""LO regressions through real consumers; mutated copies never alter O evidence."""
import ast
import copy
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock
import sys
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent), str(HERE.parent / 'R03')]
import execution_contract as execution
import lo_regressions as corpus
import m03_results
import m07_results
import native_codec_source as codec
from batch_contract import ContractError, loads, sha
from shadow_tools import VerificationError


def inputs():
    return corpus.checkpoint(HERE.parents[2], os.environ.get('R03_LO_CHECKPOINT'))[0]


class SelectedImageContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = inputs()
        cls.base = corpus.measurement_context(cls.root)
        _, _, cls.request, cls.raw, cls.extra = next(row for row in corpus.measurement_cases(cls.root) if row[:2] == ('R00-ON-P01', 0))

    def setUp(self):
        self.context = copy.deepcopy(self.base)

    def row(self, mode='R00-ON-P01'):
        if mode.endswith('NoPatch'):
            rows = self.context['off' if mode.startswith('R00-OFF') else 'on']['snapshot']['linkedPlayerReceipt']['assemblies']
        else:
            rows = self.context['fixtures'][mode[-3:]]['patch']['closure']
        return rows, next(row for row in rows if row['name'].casefold() == execution.m06.INTERNAL.casefold())

    def test_canonical_linked_name_preserves_physical_identity(self):
        _, row = self.row('R00-ON-NoPatch')
        self.assertEqual(row['name'], 'assemblya.implementation.internal')
        image = execution.selected_image(self.context, 'R00-ON-NoPatch')
        self.assertEqual(image['identity']['name'], execution.m06.INTERNAL)
        self.assertIn('Version=', image['identity']['fullName'])
        self.assertFalse(image['pdbAvailable'])
        self.assertTrue(image['methods'])

    def test_patch_record_has_actual_methods_and_symbols(self):
        image = execution.selected_image(self.context, 'R00-ON-P01')
        self.assertEqual(set(image), {'identity', 'methods', 'pdbAvailable'})
        self.assertTrue(image['pdbAvailable'])
        self.assertTrue(any(method['sequencePoints'] for method in image['methods']))

    def test_patch_transport_casing_is_not_metadata_casing(self):
        _, row = self.row(); row['name'] = row['name'].swapcase()
        self.assertEqual(execution.selected_image(self.context, 'R00-ON-P01')['identity']['name'], execution.m06.INTERNAL)

    def test_duplicate_linked_canonical_key_rejected(self):
        rows, row = self.row('R00-ON-NoPatch'); rows.append(dict(row, name=row['name'].upper()))
        with self.assertRaisesRegex(VerificationError, 'colliding'): execution.selected_image(self.context, 'R00-ON-NoPatch')

    def test_duplicate_patch_canonical_key_rejected(self):
        rows, row = self.row(); rows.append(dict(row, name=row['name'].lower()))
        with self.assertRaisesRegex(VerificationError, 'colliding'): execution.selected_image(self.context, 'R00-ON-P01')

    def test_unknown_mode_rejected(self):
        with self.assertRaisesRegex(ContractError, 'Unknown'): execution.selected_image(self.context, 'R00-ON-Other')

    def test_missing_linked_identity_rejected(self):
        rows, row = self.row('R00-ON-NoPatch'); rows.remove(row)
        with self.assertRaises(VerificationError): execution.selected_image(self.context, 'R00-ON-NoPatch')

    def test_foreign_patch_hash_rejected(self):
        _, row = self.row(); row['sha256'] = 'f' * 64
        with self.assertRaisesRegex(ContractError, 'bytes'): execution.selected_image(self.context, 'R00-ON-P01')

    def test_foreign_linked_mvid_rejected(self):
        _, row = self.row('R00-ON-NoPatch'); row['mvid'] = '00000000-0000-0000-0000-000000000000'
        with self.assertRaisesRegex(ContractError, 'MVID'): execution.selected_image(self.context, 'R00-ON-NoPatch')

    def test_foreign_patch_mvid_rejected(self):
        _, row = self.row(); row['mvid'] = '00000000-0000-0000-0000-000000000000'
        with self.assertRaisesRegex(ContractError, 'MVID'): execution.selected_image(self.context, 'R00-ON-P01')

    def test_missing_pdb_rejected(self):
        _, row = self.row(); row['pdb'] = 'DLLs/missing.pdb'
        with self.assertRaises((VerificationError, FileNotFoundError)): execution.selected_image(self.context, 'R00-ON-P01')

    def test_changed_pdb_hash_rejected(self):
        _, row = self.row(); row['pdbSha256'] = 'f' * 64
        with self.assertRaisesRegex(ContractError, 'symbols'): execution.selected_image(self.context, 'R00-ON-P01')

    def test_path_escape_rejected(self):
        _, row = self.row(); row['dll'] = '../escape.dll'
        with self.assertRaises(VerificationError): execution.selected_image(self.context, 'R00-ON-P01')

    def test_actual_dll_change_during_read_rejected(self):
        original = execution.metadata.read_methods
        with tempfile.TemporaryDirectory() as temp:
            import shutil
            folder = Path(temp) / 'patch'; shutil.copytree(self.context['fixtures']['P01']['root'] / 'DLLs', folder / 'DLLs')
            self.context['fixtures']['P01']['root'] = folder
            def mutate(dll, pdb):
                methods = original(dll, pdb)
                with Path(dll).open('ab') as output: output.write(b'changed-after-parse')
                return methods
            with mock.patch.object(execution.metadata, 'read_methods', side_effect=mutate):
                with self.assertRaisesRegex(ContractError, 'while reading'): execution.selected_image(self.context, 'R00-ON-P01')

    def reject_observation(self, phase, key, value):
        extra = loads(self.extra.read_text())
        values = next(row['values'] for row in extra['observations'] if row['phase'] == phase and row['repetition'] == 0)
        index = next(index for index, item in enumerate(values) if item.startswith(key + '='))
        values[index] = key + '=' + value
        with self.assertRaises(VerificationError):
            execution.verify(loads(self.request.read_text()), extra, loads(self.raw.read_text()),
                sha(self.request), sha(self.raw), extra['processId'], self.context)

    def test_real_statics_consumer_rejects_counter_mutation(self): self.reject_observation('statics', 'cctor', '2')
    def test_real_delegate_consumer_rejects_result_mutation(self): self.reject_observation('delegates', 'instance', 'foreign')
    def test_real_exception_consumer_rejects_token_mutation(self): self.reject_observation('exceptions', 'method.token', '1')
    def test_real_exception_consumer_rejects_pdb_line_mutation(self): self.reject_observation('exceptions', 'frame.0.line', '999999')


def add_measurement(mode, repetition):
    def test(self):
        row = next(row for row in corpus.measurement_cases(self.root) if row[:2] == (mode, repetition))
        verdict = corpus.verify_measurement(self.context, *row[2:])
        self.assertEqual(verdict['result'], 'Passed')
        self.assertEqual(verdict['phases'], 6)
        self.assertFalse(verdict['R03Accepted'])
    setattr(SelectedImageContracts, 'test_original_' + mode.replace('-', '_') + '_' + str(repetition), test)
for _mode in ('R00-ON-NoPatch', 'R00-ON-P01', 'R00-ON-P03', 'R00-OFF-NoPatch'):
    for _repetition in range(3): add_measurement(_mode, _repetition)


class SharedCodecBridgeContracts(unittest.TestCase):
    """Real nested transaction verifier with a synthetic, authenticated Git pin.

    The synthetic pin/header isolate context transport; exact unmodified O pins
    are additionally checked by lo_regressions.py against the pinned native repo.
    """
    @classmethod
    def setUpClass(cls): cls.root = inputs()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root_dir = Path(self.temp.name).resolve()
        self.repo = self.root_dir / 'owner/hybridclr'; self.repo.mkdir(parents=True)
        self.project = self.root_dir / 'run/projects/resource-complete'; self.project.mkdir(parents=True)
        def git(*args): return subprocess.check_output(['git', '-C', str(self.repo), *args], stderr=subprocess.PIPE, text=True).strip()
        self.git = git
        git('init', '-q'); git('config', 'user.name', 'Regression Fixture'); git('config', 'user.email', 'fixture@example.invalid')
        git('remote', 'add', 'origin', 'https://github.com/night-outlook/hybridclr.git')
        header = self.repo / codec.HEADER; header.parent.mkdir(parents=True); header.write_bytes(b'// synthetic codec authority fixture, not runtime evidence\n')
        git('add', '.'); git('commit', '-qm', 'synthetic context fixture')
        revision = git('rev-parse', 'HEAD')
        self.path, self.raw, self.manifest, self.patch = copy.deepcopy(next(corpus.transaction_cases(self.root)))
        profile = self.patch['patch']['metadataEncodingProfile2']
        profile.update(nativeSourceRevision=revision, nativeCodecHeaderSha256=sha(header))
        pin = self.patch['patch']['sourcePins']['hybridclr']
        pin.update(revision=revision, localPath=os.path.relpath(self.repo, self.project))
        self.context = codec.CodecSourceContext(self.project, self.repo, revision)

    def verify(self, context='default'):
        return m07_results.verify_transaction(self.raw, self.path, self.manifest, self.patch,
            source_context=self.context if context == 'default' else context)

    def test_entire_transaction_nested_bridge_outside_project_cwd(self):
        old = Path.cwd()
        try:
            os.chdir('/')
            self.assertEqual(self.verify()['state'], 'Committed')
        finally: os.chdir(old)

    def test_every_snapshot_reauthenticates_same_context(self):
        original = codec.read_codec
        with mock.patch.object(codec, 'read_codec', wraps=original) as observed:
            self.verify()
        self.assertEqual(observed.call_count, 5)  # Entry plus all four snapshots.
        self.assertTrue(all(call.args[3] is self.context for call in observed.call_args_list))

    def test_missing_context_fails(self):
        with self.assertRaisesRegex(VerificationError, 'explicit authenticated'): self.verify(None)

    def test_wrong_owner_fails(self):
        wrong = self.root_dir / 'foreign'; wrong.mkdir()
        with self.assertRaisesRegex(VerificationError, 'foreign'):
            self.verify(codec.CodecSourceContext(self.project, wrong, self.context.revision))

    def test_wrong_revision_fails(self):
        with self.assertRaisesRegex(VerificationError, 'context'):
            self.verify(codec.CodecSourceContext(self.project, self.repo, 'f' * 40))

    def test_changed_codec_hash_fails(self):
        self.patch['patch']['metadataEncodingProfile2']['nativeCodecHeaderSha256'] = 'f' * 64
        with self.assertRaisesRegex(VerificationError, 'header hash'): self.verify()

    def test_real_diagnostic_guard_not_waived(self):
        self.raw['snapshots'][0]['diagnostics']['expected'] += 1
        with self.assertRaises(VerificationError): self.verify()

    def test_legacy_default_abi_does_not_require_context(self):
        patch = {'nativeBudgetCapabilityVersion': 0}
        self.assertEqual(m07_results.diagnostic_abi(patch, 'legacy'), 1)


class CompilerDomainCallContract(unittest.TestCase):
    def test_fresh_compile_uses_pristine_source_not_player_policy(self):
        source = (HERE.parents[2] / 'Assets/AssemblyShadowDemo/Editor/R03CompletionBuild.cs').read_text()
        begin = source.index('private static void VerifyProductionEntriesCore()')
        body = source[begin:source.index('private static void Write(', begin)]
        self.assertIn('var sourcePolicy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration', body)
        self.assertIn('var policy = ShadowFilteredInputPolicy.ApplyPatch(sourcePolicy, baselineReceipt', body)
        self.assertIn('JsonUtility.ToJson(sourcePolicy) == sourcePolicyJson', body)
        compile_call = body[body.index('string restored = AssemblySnapshot.CompileWithOptions'):]
        compile_call = compile_call[:compile_call.index(';')]
        self.assertIn('), sourcePolicy, new string[0], true)', compile_call)
        self.assertNotIn('), policy,', compile_call)
        self.assertIn('ShadowFixtureProof.Load(restored, currentReceipt, policy)', body)
        self.assertIn('roots.Length == 0', body)
        self.assertIn('plan.Closure.Count == 0', body)
