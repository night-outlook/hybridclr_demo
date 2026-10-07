import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import managed
from evidence import EvidenceError, write


class Managed(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.csproj = self.root / 'ManagedTests.csproj'
        self.csproj.write_text('<Project/>')

    def result(self, **replace):
        row = dict(kind='R02ManagedHostTests', result='Passed', checks=102, marker=3000, unityPlayerRun=False)
        row.update(replace)
        path = self.root / 'stdout.log'
        path.write_text(json.dumps(row)+'\n')
        return path

    def test_build_has_no_reused_compiler_or_msbuild_server(self):
        command, dll = managed.build_plan('/dotnet', self.csproj, self.root, 'Baseline', '')
        self.assertEqual(command[1], 'build')
        for arg in ('--disable-build-servers', '--property:UseSharedCompilation=false', '-nodeReuse:false'):
            self.assertIn(arg, command)
        self.assertEqual(dll, self.root/'managed-bin-Baseline/ManagedTests.dll')
        self.assertNotIn('shutdown', command)

    def test_variants_have_separate_build_outputs(self):
        plans = [managed.build_plan('/dotnet', self.csproj, self.root, n, d) for n,d,_,_ in managed.VARIANTS]
        self.assertEqual(len({str(p[1]) for p in plans}),3)
        self.assertEqual(len({next(x for x in p[0] if x.startswith('--property:BaseIntermediateOutputPath=')) for p in plans}),3)

    def test_server_environment_is_explicit_and_does_not_mutate_input(self):
        original={'MSBUILDDISABLENODEREUSE':'0','DOTNET_CLI_USE_MSBUILD_SERVER':'1','OTHER':'kept'}
        result=managed.host_environment(original)
        self.assertEqual(result['MSBUILDDISABLENODEREUSE'],'1')
        self.assertEqual(result['DOTNET_CLI_USE_MSBUILD_SERVER'],'0')
        self.assertEqual(result['OTHER'],'kept')
        self.assertEqual(original['MSBUILDDISABLENODEREUSE'],'0')

    def test_assertion_record_exact(self):
        self.assertEqual(managed.verify_result(self.result(),3000,102)['checks'],102)

    def test_wrong_marker_rejected(self):
        with self.assertRaises(EvidenceError): managed.verify_result(self.result(marker=3001),3000,102)

    def test_short_coverage_rejected(self):
        with self.assertRaises(EvidenceError): managed.verify_result(self.result(checks=101),3000,102)

    def test_player_claim_rejected(self):
        with self.assertRaises(EvidenceError): managed.verify_result(self.result(unityPlayerRun=True),3000,102)

    def test_failed_assertions_rejected(self):
        with self.assertRaises(EvidenceError): managed.verify_result(self.result(result='Failed'),3000,102)

    def test_duplicate_result_rejected(self):
        path=self.result();path.write_text(path.read_text()*2)
        with self.assertRaises(EvidenceError): managed.verify_result(path,3000,102)

    def test_missing_result_rejected(self):
        path=self.root/'stdout.log';path.write_text('Passed\n')
        with self.assertRaises(EvidenceError): managed.verify_result(path,3000,102)

    def test_invalid_variant_rejected(self):
        with self.assertRaises(EvidenceError): managed.build_plan('/dotnet',self.csproj,self.root,'P01','')

    def test_build_failure_blocks_exec_and_preserves_all_variants(self):
        calls=[]
        def fake_run(command,project,output,timeout,env):
            calls.append(command)
            write(output/'command.json', {'result':'Failed','processGroupClean':False})
            return {'result':'Failed'}
        with patch.object(managed,'run',side_effect=fake_run):
            rows=managed.run_suite('/dotnet',self.csproj,self.root,self.root,{})
        self.assertEqual(len(calls),3)
        self.assertTrue(all(c[1]=='build' for c in calls))
        self.assertTrue(all(r['runResult']=='Blocked' and r['result']=='Failed' for r in rows))

    def test_build_and_run_are_distinct_owned_processes(self):
        calls=[]
        def fake_run(command,project,output,timeout,env):
            calls.append(command)
            write(output/'command.json', {'result':'Passed','processGroupClean':True})
            if command[1]=='build':
                directory=Path(command[command.index('--output')+1]);directory.mkdir()
                (directory/'ManagedTests.dll').write_bytes(b'host-only-fixture')
            else:
                self.assertEqual(command[1],'exec')
                marker,checks=next((m,c) for n,d,m,c in managed.VARIANTS if ('managed-bin-'+n) in command[2])
                (output/'stdout.log').write_text(json.dumps(dict(kind='R02ManagedHostTests',result='Passed',checks=checks,marker=marker,unityPlayerRun=False)))
            return {'result':'Passed'}
        with patch.object(managed,'run',side_effect=fake_run):
            rows=managed.run_suite('/dotnet',self.csproj,self.root,self.root,{})
        self.assertEqual([c[1] for c in calls],['build','exec']*3)
        self.assertTrue(all(r['result']=='Passed' for r in rows))

    def test_exit_zero_assertions_cannot_override_cleanup_failure(self):
        calls=[]
        def fake_run(command,project,output,timeout,env):
            calls.append(command)
            write(output/'command.json', {'result':'Passed' if command[1]=='build' else 'Failed'})
            if command[1]=='build':
                directory=Path(command[command.index('--output')+1]);directory.mkdir()
                (directory/'ManagedTests.dll').write_bytes(b'host-only-fixture')
                return {'result':'Passed'}
            (output/'stdout.log').write_text('{"kind":"R02ManagedHostTests","result":"Passed","checks":102,"marker":3000,"unityPlayerRun":false}\n')
            return {'result':'Failed','exitCode':0,'processGroupClean':False}
        with patch.object(managed,'run',side_effect=fake_run):
            rows=managed.run_suite('/dotnet',self.csproj,self.root,self.root,{})
        self.assertTrue(all(r['result']=='Failed' for r in rows))

if __name__=='__main__': unittest.main()
