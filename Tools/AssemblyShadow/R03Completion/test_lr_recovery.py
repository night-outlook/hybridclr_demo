"""Cleanup ownership and acceptance ordering; external Unity execution is isolated."""
import contextlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
import run_completion as runner
import resource_pipeline as pipeline
import fixture_authority as authority
from batch_contract import ContractError, sha


class CleanupAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.project=self.root/'batch/projects/resource-complete';self.project.mkdir(parents=True)
        (self.project/'ProjectSettings').mkdir();(self.project/'Assets').mkdir()
        self.pins={n:'a'*40 for n in authority.DIR_NAMES};self.pins['branch']='codex/assembly-shadow-r01b-h1'
        self.batch=SimpleNamespace(root=self.root/'batch',workspace=self.root/'owners',pins=self.pins)
        self.config={'projectPath':str(self.project),'kind':authority.POLICY,'schemaVersion':1,
                     'owningDemoCommit':'a'*40,'files':[],'expansionAuthorized':False,'R03Accepted':False,'H2Passed':False}
        (self.project/'.r03-completion-project').write_text(json.dumps(self.config))
        (self.project/authority.original.PINS).write_text('{}')
        self.commands=[];self.fault=None

    def git(self,repo,*args):
        self.commands.append(args)
        if self.fault and self.fault[0]==args:return self.fault[1]
        if args==('rev-parse','--show-toplevel'):return str(repo)
        if args==('rev-parse','HEAD'):return 'a'*40
        if args==('branch','--show-current'):return self.pins['branch']
        if args[0]=='status':return ''
        if args[0]=='config':return 'https://github.com/night-outlook/'+repo.name+'.git'
        if args[0]=='ls-remote':raise RuntimeError('controlled remote unavailable')
        raise AssertionError(args)

    def verify(self,cleanup=True):
        with patch.object(authority,'git',side_effect=self.git),patch.object(authority,'source_catalog',return_value=[]),\
             patch.object(authority,'source_pins',return_value={}),patch.object(authority,'verify_sources',return_value={}):
            return (authority.authenticate_cleanup_copy if cleanup else authority.authenticate_copy)(self.batch,self.config)

    def test_cleanup_checks_four_local_owners_without_remote(self):
        self.assertEqual(self.verify()[0],self.project)
        self.assertEqual(sum(args==('rev-parse','HEAD') for args in self.commands),4)
        self.assertFalse(any(a[0]=='ls-remote' for a in self.commands))

    def test_normal_verifier_still_requires_network(self):
        with self.assertRaisesRegex(RuntimeError,'remote unavailable'):self.verify(False)

    def test_dirty_owner_rejected_without_remote(self):
        self.fault=(('status','--porcelain=v1','--untracked-files=all'),' M source.cs')
        with self.assertRaisesRegex(ContractError,'dirty'):self.verify()

    def test_wrong_local_head_rejected(self):
        self.fault=(('rev-parse','HEAD'),'b'*40)
        with self.assertRaisesRegex(ContractError,'HEAD/branch'):self.verify()

    def test_noncanonical_origin_rejected(self):
        self.fault=(('config','--get','remote.origin.url'),'https://foreign.invalid/repo')
        with self.assertRaisesRegex(ContractError,'Canonical origin'):self.verify()

    def test_changed_marker_rejected(self):
        (self.project/'.r03-completion-project').write_text('{}')
        with self.assertRaisesRegex(ContractError,'marker changed'):self.verify()

    def test_unbound_executable_still_rejected(self):
        (self.project/'Assets/foreign.cs').write_text('class Foreign {}')
        with self.assertRaisesRegex(ContractError,'Unbound source'):self.verify()

    def test_wrong_remote_ref_name_even_matching_sha_rejected(self):
        self.fault=(('ls-remote','origin','refs/heads/'+self.pins['branch']),'a'*40+'\trefs/heads/other')
        with self.assertRaisesRegex(ContractError,'reply malformed'):self.verify(False)

    def test_empty_remote_reply_rejected_clearly(self):
        self.fault=(('ls-remote','origin','refs/heads/'+self.pins['branch']),'')
        with self.assertRaisesRegex(ContractError,'reply malformed'):self.verify(False)


class RecoveryOrderingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name).resolve();unity=root/'Unity';unity.write_text('constructor fixture only')
        self.batch=runner.CompletionBatch(runner.HERE.parents[3],root/'batch',unity,'a'*40)
        self.project=self.batch.root/'projects/resource-complete';self.project.mkdir(parents=True)
        (self.project/'ProjectSettings').mkdir();(self.project/'.r03-completion-project').write_text('{}')
        self.run=self.project/'_temp/AssemblyShadow/M02Validation-test';self.run.mkdir(parents=True)
        self.settings=self.project/'ProjectSettings/ProjectSettings.asset';self.settings.write_bytes(b'staged settings')
        self.original=self.run/'p05-project-settings.original';self.original.write_bytes(b'original settings')
        self.state={'schemaVersion':2,'projectDirectory':str(self.project),'runDirectory':str(self.run),
                    'originalSettingsSha256':sha(self.original),'originalDefines':''}
        (self.run/'p05-define-state.json').write_text(json.dumps(self.state))
        self.batch.resource_config={'projectPath':str(self.project),'runPath':str(self.run)}
        self.calls=[]

    def phase(self,batch,name,project,pins):
        self.assertEqual(name,'restore');self.calls.append('UnityRestore')
        # Model only external Unity's guarded producer. The production Python
        # byte-restorer and scheduler execute unmodified around this fixture.
        self.settings.write_bytes(b'original defines; Unity reserialized settings')
        (self.run/'p05-restored.json').write_text(json.dumps({'schemaVersion':2,
            'stateSha256':sha(self.run/'p05-define-state.json'),'originalDefines':'',
            'originalSettingsSha256':sha(self.original),'restoredSettingsSha256':sha(self.settings)}))
        return {}

    def exercise(self,remote_error=None,local_error=None,phase_error=None):
        def local(*args):
            self.calls.append('LocalPinnedAuthentication')
            if local_error:raise local_error
            return self.project,{}
        def remote(*args):
            self.calls.append('FreshRemoteAuthentication')
            if (self.run/'p05-define-state.json').exists():self.assertEqual(self.settings.read_bytes(),b'original settings')
            if remote_error:raise remote_error
            return self.project,{}
        with patch.object(pipeline,'authenticate_cleanup_copy',side_effect=local),\
             patch.object(pipeline,'authenticate_copy',side_effect=remote),\
             patch.object(pipeline,'_verified_phase',side_effect=phase_error or self.phase),\
             patch.object(pipeline,'verify_sources',return_value={}):
            with contextlib.redirect_stdout(io.StringIO()):
                self.batch.cell('resource-p05-restore',lambda:pipeline.restore(self.batch))
                self.batch.cell('resource-p05-finalize',lambda:self.calls.append('Finalize'),('resource-p05-restore',))
        report=json.loads((self.batch.root/'transaction-recovery/verification.json').read_text())
        return report

    def test_remote_failure_happens_after_exact_cleanup_but_blocks_finalize(self):
        report=self.exercise(remote_error=RuntimeError('remote offline'))
        self.assertEqual(self.calls,['LocalPinnedAuthentication','UnityRestore','FreshRemoteAuthentication'])
        self.assertEqual(self.settings.read_bytes(),b'original settings')
        self.assertEqual(report['cleanupResult'],'ExactOriginalBytesRestored');self.assertEqual(report['remoteAuthority'],'Failed')
        self.assertEqual([r['result'] for r in self.batch.cells],['Failed','Blocked'])
        self.assertFalse(report['runtimeAcceptance'])
        self.assertEqual((self.batch.root/'transaction-recovery/settings-before.bytes').read_bytes(),b'staged settings')

    def test_success_requires_local_cleanup_and_fresh_remote(self):
        report=self.exercise();self.assertEqual(report['remoteAuthority'],'Passed')
        self.assertEqual(self.calls,['LocalPinnedAuthentication','UnityRestore','FreshRemoteAuthentication','Finalize'])
        self.assertEqual([r['result'] for r in self.batch.cells],['Passed','Passed'])

    def test_changed_remote_tip_does_not_undo_cleanup_or_allow_acceptance(self):
        report=self.exercise(remote_error=ContractError('remote tip changed'))
        self.assertEqual(report['cleanupResult'],'ExactOriginalBytesRestored')
        self.assertEqual(self.batch.cells[0]['result'],'Failed')

    def test_local_identity_failure_never_launches_or_overwrites(self):
        report=self.exercise(local_error=ContractError('wrong source'))
        self.assertEqual(self.calls,['LocalPinnedAuthentication']);self.assertEqual(self.settings.read_bytes(),b'staged settings')
        self.assertEqual(report['cleanupResult'],'Failed');self.assertEqual(report['stage'],'LocalAuthentication')

    def test_backup_mutation_denies_restore(self):
        self.original.write_bytes(b'foreign')
        report=self.exercise();self.assertEqual(self.calls,['LocalPinnedAuthentication'])
        self.assertEqual(report['cleanupResult'],'Failed')

    def test_wrong_transaction_owner_denies_restore(self):
        self.state['projectDirectory']+='-other';(self.run/'p05-define-state.json').write_text(json.dumps(self.state))
        self.exercise();self.assertEqual(self.calls,['LocalPinnedAuthentication'])
        self.assertEqual(self.settings.read_bytes(),b'staged settings')

    def test_restore_process_failure_is_not_claimed_as_cleanup(self):
        report=self.exercise(phase_error=RuntimeError('Unity process failed'))
        self.assertEqual(report['cleanupResult'],'Failed');self.assertEqual(report['stage'],'ProductionRestore')
        self.assertEqual(report['remoteAuthority'],'NotRun')

    def test_no_state_means_no_write_but_still_remote_acceptance(self):
        (self.run/'p05-define-state.json').unlink()
        report=self.exercise();self.assertEqual(report['cleanupResult'],'NoRecordedMutation')
        self.assertEqual(self.calls,['LocalPinnedAuthentication','FreshRemoteAuthentication','Finalize'])
        self.assertEqual(self.settings.read_bytes(),b'staged settings')

    def test_symlink_backup_rejected(self):
        data=self.original.read_bytes();self.original.unlink();outside=self.batch.root/'other';outside.write_bytes(data);self.original.symlink_to(outside)
        self.exercise();self.assertEqual(self.calls,['LocalPinnedAuthentication'])
        self.assertEqual(self.settings.read_bytes(),b'staged settings')

    def test_duplicate_invocation_cannot_restore_twice(self):
        self.exercise()
        with self.assertRaises(FileExistsError):pipeline.restore(self.batch)


if __name__=='__main__':unittest.main()
