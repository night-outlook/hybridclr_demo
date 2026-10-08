import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

import h1_local_batch as batch


class LocalBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def task(self,name='one',code='print("done")',requires=()):
        return {'id':name,'kind':'python','argv':[sys.executable,'-c',code],'cwd':str(self.root),'timeoutSec':5,'requires':list(requires)}
    def plan(self,*tasks):return {'schemaVersion':1,'kind':'H1LocalDiagnosticBatch','tasks':list(tasks)}
    def test_preview_does_not_create_output(self):
        output=self.root/'run';r=batch.run_plan(self.plan(self.task()),{},output);self.assertFalse(output.exists());self.assertFalse(r['executed'])
    def test_actual_command_execution(self):
        r=batch.run_plan(self.plan(self.task()),{},self.root/'run',True);self.assertEqual('DiagnosticsPassed',r['status']);self.assertFalse(r['wholeChainM08Pass'])
    def test_failed_dependency_blocks_but_unrelated_runs(self):
        r=batch.run_plan(self.plan(self.task('fail','raise SystemExit(3)'),self.task('child',requires=('fail',)),self.task('other')),{},self.root/'run',True)
        self.assertEqual(['Failed','Blocked','Passed'],[x['status'] for x in r['tasks']])
    def test_no_output_overwrite(self):
        with self.assertRaises(batch.BatchError):batch.run_plan(self.plan(self.task()),{},self.root)
    def test_duplicate_task_rejected(self):
        with self.assertRaises(batch.BatchError):batch.validate(self.plan(self.task(),self.task()))
    def test_forward_dependency_rejected(self):
        with self.assertRaises(batch.BatchError):batch.validate(self.plan(self.task('one',requires=('two',)),self.task('two')))
    def test_path_traversal_task_rejected(self):
        with self.assertRaises(batch.BatchError):batch.validate(self.plan(self.task('../one')))
    def test_unknown_variable_fails_before_execution(self):
        task=self.task();task['argv'].append('${MISSING}')
        with self.assertRaises(batch.BatchError):batch.run_plan(self.plan(task),{},self.root/'run',True)
        self.assertFalse((self.root/'run').exists())
    def test_timeout_recorded(self):
        task=self.task(code='import time; time.sleep(4)');task['timeoutSec']=0.05
        result=batch.run_plan(self.plan(task),{},self.root/'run',True);self.assertEqual('Timeout',result['tasks'][0]['status'])
    def test_nunit_no_cases_rejected(self):
        path=self.root/'tests.xml';path.write_text('<test-run result="Passed"/>')
        with self.assertRaises(batch.BatchError):batch.validate_nunit(path)
    def test_nunit_failed_child_not_hidden_by_root(self):
        path=self.root/'tests.xml';path.write_text('<test-run result="Passed"><test-case result="Failed"/></test-run>')
        self.assertFalse(batch.validate_nunit(path)['passed'])
    def test_nunit_passes_require_real_cases(self):
        path=self.root/'tests.xml';path.write_text('<test-run result="Passed"><test-case result="Passed"/></test-run>')
        self.assertTrue(batch.validate_nunit(path)['passed'])
    def test_unittest_zero_cases_not_pass(self):
        task=self.task(code='print("Ran 0 tests in 0.0s")');task['validator']='unittest'
        self.assertEqual('Failed',batch.run_plan(self.plan(task),{},self.root/'run',True)['tasks'][0]['status'])
    def test_unity_requires_exact_project_guard(self):
        task=self.task();task['kind']='unity'
        with self.assertRaises(batch.BatchError):batch.validate(self.plan(task))
    def test_json_duplicate_keys_rejected(self):
        path=self.root/'plan.json';path.write_text('{"a":1,"a":2}')
        with self.assertRaises(batch.BatchError):batch.read_json(path)
    def test_no_shell_interpolation(self):
        value='$(touch NEVER_CREATED); echo text'
        task=self.task(code='import sys; print(sys.argv[1])');task['argv'].append('${literal}')
        result=batch.run_plan(self.plan(task),{'literal':value},self.root/'run',True)
        self.assertEqual('Passed',result['tasks'][0]['status']);self.assertFalse((self.root/'NEVER_CREATED').exists())
        self.assertIn(value,(self.root/'run/one/process.log').read_text())


if __name__=='__main__':unittest.main()
