import copy
import json
from pathlib import Path
import plistlib
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import h1_compiler_actions as actions
import h1_native_capture as native
import h1_pch_diagnose as diagnose

CONFIG = '#ifndef IL2CPP_DEBUG\n#define IL2CPP_DEBUG 0\n#endif\n#ifndef IL2CPP_DEVELOPMENT\n#define IL2CPP_DEVELOPMENT 0\n#endif\n'


class PlanFailureRetentionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name).resolve()
        (self.root/'Library/Bee').mkdir(parents=True)
        self.compiler=self.root/'clang';self.compiler.write_bytes(b'synthetic-not-executed')
        self.sdk=self.root/'sdk';self.sdk.mkdir();(self.sdk/'SDKSettings.plist').write_bytes(plistlib.dumps({'Version':'synthetic'}))
        self.binary=self.root/'Built/GameAssembly.dylib';self.binary.parent.mkdir();self.binary.write_bytes(b'synthetic-not-executed')
        self.config=self.root/'il2cpp-config.h';self.config.write_text(CONFIG)
        self.flags=f'{self.compiler} -isysroot {self.sdk} -DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1 -DHYBRIDCLR_H1_COUNT_DIAGNOSTICS=1'
        self.graph={'Nodes':[
            {'Annotation':'C_Mac_arm64','Action':self.flags+' -DIL2CPP_DEBUG=1 -c runtime.cpp -o runtime.o','Inputs':['runtime.cpp'],'Outputs':['runtime.o']},
            {'Annotation':'Link_Mac_arm64','Action':f'{self.compiler} -isysroot {self.sdk}','Inputs':['runtime.o'],'Outputs':['Library/GameAssembly.dylib']},
            {'Annotation':'Copy','Inputs':['Library/GameAssembly.dylib'],'Outputs':[str(self.binary)]}]}
        (self.root/'runtime.cpp').write_text('int runtime;')
        self.graph_path=self.root/'Library/Bee/Player-synthetic.dag.json';self.save_graph()
        self.req={'projectRoot':str(self.root),'before':{'entries':[]},'buildId':'H1Count-On-Debug','buildGuid':'a'*32,
            'inputSnapshotHash':'b'*64,'nativeLibraryPath':str(self.binary),'nativeLibrarySha256':native.digest(self.binary),
            'sourcePinSha256':'c'*64,'il2cppConfigPath':str(self.config),'cppConfiguration':'Debug','featureEnabled':True}
        self.request_path=self.root/'request.json';self.request_path.write_text(json.dumps(self.req,indent=4)+'\n')
        self.out=self.root/'attempt'
    def tearDown(self): self.temp.cleanup()
    def save_graph(self):self.graph_path.write_text(json.dumps(self.graph,indent=2)+'\n')
    def failure(self):return json.loads((self.out/'attempt-failure.json').read_text())
    def retained(self,role):
        rows=[json.loads(x) for x in (self.out/'attempt-inputs.jsonl').read_text().splitlines()]
        return [Path(x['retainedPath']).read_bytes() for x in rows if x.get('role')==role and x['status']=='Retained']
    def assert_not_executed(self):
        self.assertEqual('NotRun',self.failure()['pchReplay']);self.assertEqual('NotRun',self.failure()['macroProbes'])
        self.assertFalse((self.out/'h1-compiler-provenance.json').exists());self.assertFalse((self.out/'pch/pch-proof.json').exists())
    def test_synthetic_16_430_split_remains_rejected_and_retained(self):
        units=[]
        for i in range(446):
            units.append({'Annotation':'C_Mac_arm64','Action':self.flags+(' -DIL2CPP_DEBUG=1' if i>=16 else '')+f' -c unit{i}.cpp -o unit{i}.o',
                          'Inputs':[], 'Outputs':[f'unit{i}.o']})
        link=copy.deepcopy(self.graph['Nodes'][1]);link['Inputs']=[u['Outputs'][0] for u in units]
        self.graph['Nodes']=units+[link,self.graph['Nodes'][2]];self.save_graph();raw=self.graph_path.read_bytes()
        with patch.object(native.subprocess,'run') as execute:
            with self.assertRaisesRegex(ValueError,'Translation units disagree'):
                native.capture_request(self.request_path,self.out)
            execute.assert_not_called()
        self.assertIn(raw,self.retained('candidate-dag'));self.assertEqual('planning',self.failure()['stage'])
        census=json.loads((self.out/'macro-domain-census.json').read_text());self.assertEqual(446,census['compileActionCount'])
        self.assert_not_executed()
    def test_injected_pch_plan_error_preserves_declared_pch_header_and_graph(self):
        header=self.root/'prefix.h';header.write_bytes(b'header');pch=self.root/'prefix.pch';pch.write_bytes(b'\x80CPCH')
        self.graph['Nodes'][0]['Inputs'].append(str(header));self.graph['Nodes'][0]['Outputs'].append(str(pch));self.save_graph()
        error=actions.CompilerActionError('Injected unsupported PCH action')
        with patch.object(native.pch,'has_pch',return_value=True),patch.object(native.pch,'plan',side_effect=error),patch.object(native.pch,'capture') as execution:
            with self.assertRaises(actions.CompilerActionError) as caught:native.capture_request(self.request_path,self.out)
            self.assertIs(error,caught.exception);execution.assert_not_called()
        kept=self.retained('declared-native-input');self.assertIn(b'header',kept);self.assertIn(b'\x80CPCH',kept)
        self.assert_not_executed()
    def test_old_diagnostic_plan_failure_retains_original_bytes(self):
        request=self.request_path.read_bytes();graph=self.graph_path.read_bytes()
        with patch.object(diagnose.p,'plan',side_effect=actions.CompilerActionError('Injected macro mismatch')),patch.object(diagnose.p,'capture') as execution:
            with self.assertRaisesRegex(ValueError,'Injected macro mismatch'):
                diagnose.diagnose(self.request_path,self.graph_path,self.out)
            execution.assert_not_called()
        self.graph_path.write_text('Bee replaced this file')
        self.assertEqual(request,(self.out/'original-request.json').read_bytes());self.assertEqual(graph,(self.out/'original-graph.json').read_bytes())
        summary=json.loads((self.out/'diagnostic-result.json').read_text());self.assertFalse(summary['freshBuildClaim'])
        self.assertEqual('planning',summary['failedStage']);self.assert_not_executed()
    def test_bad_request_json_retained_before_parse(self):
        raw=b'{ invalid \xff request';self.request_path.write_bytes(raw)
        with self.assertRaises(ValueError):native.capture_request(self.request_path,self.out)
        self.assertEqual([raw],self.retained('original-request'));self.assert_not_executed()
    def test_duplicate_request_key_still_rejected(self):
        self.request_path.write_text('{"projectRoot":"a","projectRoot":"b"}')
        with self.assertRaisesRegex(ValueError,'Duplicate JSON key'):native.capture_request(self.request_path,self.out)
        self.assertTrue(self.retained('original-request'));self.assert_not_executed()
    def test_bad_graph_json_retained_before_selection(self):
        self.graph_path.write_bytes(b'{invalid graph')
        with self.assertRaises(ValueError):native.capture_request(self.request_path,self.out)
        self.assertEqual([b'{invalid graph'],self.retained('candidate-dag'));self.assert_not_executed()
    def test_non_utf8_response_retained_before_expansion_failure(self):
        rsp=self.root/'flags.rsp';rsp.write_bytes(b'\xff invalid response')
        self.graph['Nodes'][0]['Action']+=' @flags.rsp';self.save_graph()
        with self.assertRaises(ValueError):native.capture_request(self.request_path,self.out)
        self.assertIn(b'\xff invalid response',self.retained('response-file'));self.assertEqual('response-closure',self.failure()['stage'])
        self.assert_not_executed()
    def test_multiple_dags_both_retained_not_selected_by_recency(self):
        other=self.graph_path.with_name('Player-other.dag.json');other.write_bytes(self.graph_path.read_bytes())
        with self.assertRaisesRegex(ValueError,'one changed'):native.capture_request(self.request_path,self.out)
        self.assertEqual(2,len(self.retained('candidate-dag')));self.assert_not_executed()
    def test_existing_root_is_never_reused(self):
        self.out.mkdir();(self.out/'historical').write_bytes(b'keep')
        with self.assertRaises(ValueError):native.capture_request(self.request_path,self.out)
        self.assertEqual(['historical'],[p.name for p in self.out.iterdir()])
    def test_request_mutation_rejected_before_provenance_publication(self):
        def version(*args,**kwargs):
            self.request_path.write_text('changed');return SimpleNamespace(stdout='synthetic clang',stderr='')
        with patch.object(native.subprocess,'run',side_effect=version):
            with self.assertRaisesRegex(ValueError,'Capture request changed'):native.capture_request(self.request_path,self.out)
        self.assertFalse((self.out/'h1-compiler-provenance.json').exists())
    def test_successful_non_pch_capture_still_writes_original_schema(self):
        with patch.object(native.subprocess,'run',return_value=SimpleNamespace(stdout='synthetic clang',stderr='')):
            result=native.capture_request(self.request_path,self.out)
        self.assertEqual(1,result['schemaVersion']);self.assertEqual('',result['pchProofPath'])
        self.assertEqual(result,json.loads((self.out/'h1-compiler-provenance.json').read_text()))
        self.assertFalse((self.out/'attempt-failure.json').exists())
    def test_bad_diagnostic_graph_retained_with_failure_summary(self):
        self.graph_path.write_bytes(b'{ malformed')
        with self.assertRaises(ValueError):diagnose.diagnose(self.request_path,self.graph_path,self.out)
        self.assertEqual(b'{ malformed',(self.out/'original-graph.json').read_bytes())
        self.assertTrue((self.out/'diagnostic-result.json').is_file());self.assert_not_executed()
