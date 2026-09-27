import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import authority
import run_local
from evidence import EvidenceError


class Local(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def test_formal_clears_every_inherited_sidecar_control(self):
        with patch.dict(os.environ, dict(zip(run_local.ENV_KEYS, ('bad', 'bad', 'bad')))):
            self.assertTrue(all(k not in run_local.environment() for k in run_local.ENV_KEYS))

    def test_sidecar_environment_is_exact(self):
        env = run_local.environment('candidate', self.root/'raw.json', 'a'*32)
        self.assertEqual([env[k] for k in run_local.ENV_KEYS], [str(self.root/'raw.json'), 'a'*32, 'candidate'])

    def test_partial_environment_rejected(self):
        with self.assertRaises(EvidenceError): run_local.environment('candidate')

    def test_wrong_role_rejected(self):
        with self.assertRaises(EvidenceError): run_local.environment('other', self.root/'a', 'a'*32)

    def test_graph_args_keep_four_roles(self):
        graph = dict(fixtureManifest='fixtures', nativeOnReceipt='on', nativeOffReceipt='off', editorReplayReceipt='replay')
        self.assertEqual(run_local.graph_args(graph), ['--fixture-manifest','fixtures','--on-build','on','--off-build','off','--replay-receipt','replay'])

    def workflow(self, folder='a', baseline='new', status='Passed', controlled=True):
        path = self.root/'_temp/AssemblyShadow'/folder/'m07-build-workflow.json'; path.parent.mkdir(parents=True)
        path.write_text(json.dumps(dict(baselineBuildId=baseline, projectPath=str(self.root), result=status, controlledPerformanceBuilds=controlled)))
        return path

    def test_workflow_does_not_select_old_baseline(self):
        self.workflow('old','old'); path = self.workflow()
        self.assertEqual(run_local.select_workflow(self.root, 'new', set())[0], path)

    def test_workflow_does_not_select_preexisting_result(self):
        old = self.workflow()
        with self.assertRaises(EvidenceError): run_local.select_workflow(self.root,'new',{old})

    def test_duplicate_workflow_rejected(self):
        self.workflow(); self.workflow('duplicate')
        with self.assertRaises(EvidenceError): run_local.select_workflow(self.root,'new',set())

    def test_failed_workflow_rejected(self):
        self.workflow(status='Failed')
        with self.assertRaises(EvidenceError): run_local.select_workflow(self.root,'new',set())

    def test_uncontrolled_build_rejected(self):
        self.workflow(controlled=False)
        with self.assertRaises(EvidenceError): run_local.select_workflow(self.root,'new',set())

    def test_dependency_failure_blocks_only_dependents(self):
        batch = object.__new__(run_local.Batch); batch.out=self.root; batch.rows={};batch.values={}
        def failure(): raise ValueError('retained cause')
        called=[]
        with contextlib.redirect_stdout(io.StringIO()):
            batch.cell('a', [], failure)
            batch.cell('b', ['a'], lambda: called.append('b'))
            batch.cell('c', [], lambda: called.append('c'))
        self.assertEqual(called,['c'])
        self.assertEqual([batch.rows[k]['result'] for k in 'abc'], ['Failed','Blocked','Passed'])
        self.assertIn('retained cause', batch.rows['a']['error'])

    def test_source_commit_requires_full_lowercase(self):
        self.assertEqual(authority.commit('a'*40), 'a'*40)
        for value in ('a'*39,'A'*40,'z'*40,None):
            with self.assertRaises(EvidenceError): authority.commit(value)

    def test_no_execute_default_creates_no_artifacts(self):
        args=['--candidate',str(self.root/'c'),'--candidate-head','a'*40,'--control',str(self.root/'b'),
              '--control-head','b'*40,'--unity','/missing-unity','--pwsh','/missing-pwsh','--output',str(self.root/'out')]
        with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(run_local.main(args),0)
        self.assertFalse((self.root/'out').exists())

    def test_common_source_rejects_executable_difference(self):
        with patch.object(authority.shadow_tools,'tree',side_effect=[{'Assets/a.cs':'a'},{'Assets/a.cs':'b'}]):
            with self.assertRaises(EvidenceError): authority.common_sources(self.root,self.root)

    def test_common_source_allows_only_existing_metadata_policy(self):
        with patch.object(authority.shadow_tools,'tree',side_effect=[{'Assets/a.cs':'a',authority.shadow_tools.PINS:'a'},
                                                                {'Assets/a.cs':'a',authority.shadow_tools.PINS:'b'}]):
            self.assertEqual(authority.common_sources(self.root,self.root)['blobCount'],1)


if __name__=='__main__': unittest.main()

class CellAuthority(unittest.TestCase):
    def test_dirty_workspace_blocks_cell_before_action(self):
        with tempfile.TemporaryDirectory() as root:
            batch=object.__new__(run_local.Batch);batch.out=Path(root).resolve();batch.rows={};batch.values={}
            batch.roots={'candidate':batch.out};batch.heads={'candidate':'a'*40};batch.targets={}
            calls=[]
            with patch.object(authority,'inspect',side_effect=EvidenceError('dirty after prior failed build')):
                with contextlib.redirect_stdout(io.StringIO()):
                    batch.cell('diagnostic',[],lambda:calls.append('run'),roles=('candidate',))
            self.assertEqual(calls,[]);self.assertEqual(batch.rows['diagnostic']['result'],'Blocked')
            self.assertIn('dirty',batch.rows['diagnostic']['sourceAuthorityError'])

    def test_clean_workspace_runs_cell_with_receipt(self):
        with tempfile.TemporaryDirectory() as root:
            batch=object.__new__(run_local.Batch);batch.out=Path(root).resolve();batch.rows={};batch.values={}
            batch.roots={'candidate':batch.out};batch.heads={'candidate':'a'*40};batch.targets={}
            with patch.object(authority,'inspect',return_value={'result':'SourceVerifiedNotBuildAccepted'}):
                with contextlib.redirect_stdout(io.StringIO()):batch.cell('check',[],lambda:42,roles=('candidate',))
            self.assertEqual(batch.values['check'],42);self.assertEqual(len(batch.rows['check']['inputAuthorities']),1)
