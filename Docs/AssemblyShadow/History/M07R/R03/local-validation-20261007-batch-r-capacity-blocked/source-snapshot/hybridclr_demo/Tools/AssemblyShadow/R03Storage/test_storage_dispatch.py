"""Actual R03 scheduler/constructor, with expensive external work isolated."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

import run_storage_checked as entry
import run_completion as core
import test_lp_orchestration as retained_tests
import storage_guard as g
from test_storage_guard import observation


class SchedulerTests(unittest.TestCase):
    def exercise(self, fail_at=None, latch=False):
        session=mock.Mock()
        lost=False
        def before(phase,*,cleanup=False):
            nonlocal lost
            lost = lost or phase==fail_at
            if not cleanup and (phase==fail_at or latch and lost):
                raise g.StorageBlocked('synthetic storage prerequisite')
        session.before.side_effect=before
        def factory(*args,**kwargs):
            return entry.StorageCheckedBatch(*args,session=session,**kwargs)
        with mock.patch.object(core,'CompletionBatch',side_effect=factory):
            values=retained_tests.CompletionDataflowTests().exercise()
        return values,session

    def test_same_ninety_cells_all_original_actions_and_order(self):
        (code,cells,calls,count,players),session=self.exercise()
        self.assertEqual(code,0);self.assertEqual(len(cells),90)
        self.assertEqual(calls,['graph','layout','integration'])
        self.assertEqual(cells['production-entry-integration']['dependencies'],['resource-input-binding'])
        self.assertEqual(players['m07_case']+players['r00_case']+players['early_case'],36)
        self.assertEqual(len([r for r in cells if r.startswith('build-')]),4)
        self.assertTrue(all(r['result']=='Passed' for r in cells.values()))
        self.assertEqual(session.before.call_count,90)

    def test_guard_failure_does_not_invoke_integration_or_erase_ledger(self):
        (code,cells,calls,count,players),session=self.exercise('production-entry-integration')
        self.assertEqual(code,1);self.assertEqual(count,0)
        self.assertEqual(cells['production-entry-integration']['result'],'Failed')
        self.assertEqual(players['m07_case']+players['r00_case']+players['early_case'],36)
        self.assertEqual(len(cells),90);session.record_failure.assert_called()

    def test_latched_shortage_blocks_new_work_not_p05_cleanup(self):
        (code,cells,calls,count,players),session=self.exercise('resource-compiler',latch=True)
        self.assertEqual(code,1);self.assertEqual(count,0)
        self.assertEqual(cells['resource-p05-restore']['result'],'Passed')
        self.assertEqual(cells['final-authority']['result'],'Passed')
        self.assertEqual(cells['resource-input-binding']['result'],'Blocked')
        self.assertEqual(len(cells),90)
        session.before.assert_any_call('resource-p05-restore',cleanup=True)
        session.before.assert_any_call('final-authority',cleanup=True)

    def test_command_argv_timeout_and_original_result_are_unchanged(self):
        batch=object.__new__(entry.StorageCheckedBatch)
        batch.storage_session=mock.Mock();batch.storage_phase='build';batch.command_count=7
        args=['Unity','-projectPath','/fixture'];original={'retained':True}
        with mock.patch.object(core.CompletionBatch,'command',return_value=original) as run:
            result=batch.command(args,7200)
        self.assertIs(result,original);run.assert_called_once_with(args,7200)

    def test_command_failure_is_reraised_with_failure_observation(self):
        batch=object.__new__(entry.StorageCheckedBatch)
        batch.storage_session=mock.Mock();batch.storage_phase='integration';batch.command_count=1
        error=RuntimeError('original command failed')
        with mock.patch.object(core.CompletionBatch,'command',side_effect=error):
            with self.assertRaises(RuntimeError) as caught:batch.command(['fixture'],3600)
        self.assertIs(caught.exception,error)
        self.assertIs(batch.storage_session.record_failure.call_args.args[1],error)


class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve();self.work=self.root/'workspace';self.work.mkdir()
        self.q=self.root/'q';(self.q/'cells').mkdir(parents=True)
        self.qcell=self.q/'cells/production-entry-integration.json';self.qcell.write_text('unit Q')
        self.args=SimpleNamespace(workspace=str(self.work),output=str(self.root/'batch'),
              storage_evidence=str(self.root/'sidecar'),retained_q=str(self.q),unity='/fixture/Unity',
              demo_commit='a'*40,execute=False)

    def invoke(self,free=128*g.GIB,execute=False,fail=False):
        self.args.execute=execute
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(entry.sys,'platform','darwin'))
            stack.enter_context(mock.patch.object(entry,'source_authority',return_value={'files':[],'repositories':[]}))
            stack.enter_context(mock.patch.object(entry,'git',return_value='.git'))
            stack.enter_context(mock.patch.object(g,'Q_CELL_SHA',g.digest(self.qcell)))
            stack.enter_context(mock.patch.object(g,'diagnostics',return_value=[]))
            stack.enter_context(mock.patch.object(g,'sample',return_value=observation(free)))
            stack.enter_context(mock.patch.object(g,'allocation_probe',return_value={'result':'Passed'}))
            cls=stack.enter_context(mock.patch.object(entry,'StorageCheckedBatch'))
            cls.return_value.execute.return_value=0
            if fail:cls.return_value.execute.side_effect=RuntimeError('controlled batch failure')
            with contextlib.redirect_stdout(io.StringIO()):
                if fail:
                    with self.assertRaises(RuntimeError):entry.run(self.args)
                    return None,cls
                return entry.run(self.args),cls

    def test_preflight_block_creates_no_batch_and_never_constructs_runner(self):
        code,cls=self.invoke(22*g.GIB,execute=True)
        self.assertEqual(code,2);cls.assert_not_called();self.assertFalse((self.root/'batch').exists())
        admission=json.loads((self.root/'sidecar/admission.json').read_text())
        self.assertEqual(admission['state'],'Blocked');self.assertFalse(admission['batchStarted'])

    def test_diagnostic_mode_never_launches_even_when_admitted(self):
        code,cls=self.invoke();self.assertEqual(code,0);cls.assert_not_called()
        dispatch=json.loads((self.root/'sidecar/dispatch.json').read_text())
        self.assertFalse(dispatch['batchStarted']);self.assertFalse(dispatch['runtimeAcceptance'])

    def test_execute_constructs_exactly_once_after_admission(self):
        code,cls=self.invoke(execute=True);self.assertEqual(code,0)
        cls.assert_called_once();cls.return_value.execute.assert_called_once_with()
        dispatch=json.loads((self.root/'sidecar/dispatch.json').read_text())
        self.assertTrue(dispatch['batchStarted']);self.assertFalse(dispatch['R03Accepted'])
        self.assertFalse(dispatch['qualificationApproved'])

    def test_exception_has_separate_failed_dispatch_no_retry(self):
        _,cls=self.invoke(execute=True,fail=True);cls.assert_called_once()
        d=json.loads((self.root/'sidecar/dispatch.json').read_text())
        self.assertEqual(d['batchExitCode'],1)
        self.assertTrue(list((self.root/'sidecar').glob('failure-*.json')))

    def test_existing_batch_or_diagnostics_refused(self):
        for attribute in ('output','storage_evidence'):
            p=Path(getattr(self.args,attribute));p.mkdir()
            with self.assertRaises(g.StorageBlocked):
                entry.validate_locations(self.work,self.args.output,self.args.storage_evidence,self.q)
            p.rmdir()

    def test_overlap_with_history_or_source_refused(self):
        for output in (self.q/'new',self.work/'new',self.q,self.root):
            with self.assertRaises(g.StorageBlocked):
                entry.validate_locations(self.work,output,self.args.storage_evidence,self.q)

    def test_sidecar_cannot_enter_batch_seal(self):
        batch=self.root/'batch';batch.mkdir()
        with self.assertRaises(g.StorageBlocked):
            entry.validate_locations(self.work,batch,batch/'sidecar',self.q)

    def test_wrong_platform_does_not_start_or_create_outputs(self):
        with mock.patch.object(entry.sys,'platform','linux'):
            with self.assertRaises(g.StorageBlocked):entry.run(self.args)
        self.assertFalse((self.root/'sidecar').exists())


if __name__=='__main__':unittest.main()
