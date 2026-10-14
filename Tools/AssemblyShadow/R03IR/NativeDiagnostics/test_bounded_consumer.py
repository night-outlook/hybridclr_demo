"""Bounded V2 file/semantic admission. Actual files + codec; synthetic Player data.

Explicitly run with unittest -s NativeDiagnostics, never auto-enable V2 in Player.
"""
from __future__ import annotations
import ast
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
IR=HERE.parent
sys.path.insert(0,str(IR))
import bounded_snapshot as consumer
from NativeDiagnostics import diagnostic_wire as wire
import test_terminal_contract as original_tests
from batch_contract import ContractError
from run_terminal_local import verify_ir

PINS={'hybridclr_demo':'1'*40,'hybridclr':'2'*40,'hybridclr_unity':'3'*40,'il2cpp_plus':'4'*40}
ERRORS=(consumer.AdmissionError,wire.ContractError,ContractError,OSError)

class PairFixture(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve(strict=True)
        fixture=original_tests.TerminalReceiptContractTests()
        fixture.setUp()
        self.raw=copy.deepcopy(fixture.raw)
        self.request=copy.deepcopy(fixture.request)
        self.launch={**fixture.launch,'exitCode':0}
        self.build=fixture.build_sha
        self.serial=0

    def pair(self,fields=None,raw=None):
        self.serial+=1
        directory=self.root/str(self.serial);directory.mkdir(mode=0o700)
        text=json.dumps(self.request,indent=2)+'\n'
        r=copy.deepcopy(self.raw if raw is None else raw)
        r['reportTransport']='NativeBoundedSnapshotV2'
        r.setdefault('requestSha256',consumer.digest(text.encode('utf-8')))
        r.pop('finalDiagnostics',None);r.pop('finalExecutionDiagnostics',None)
        identity={'runId':self.request['runId'],'caseId':self.request['caseId'],
                  'processId':self.launch['pid'],'requestSha256':consumer.digest(text.encode()),
                  'buildSha256':self.build,'demoCommit':PINS['hybridclr_demo'],
                  'hybridclrCommit':PINS['hybridclr'],'packageCommit':PINS['hybridclr_unity'],
                  'nativeCommit':PINS['il2cpp_plus']}
        fields=fields or {'finalDiagnostics':'{"classes":[1,2,3]}','finalExecutionDiagnostics':'{}'}
        data,descriptor=wire.encode(identity,r,fields)
        envelope={**r,'diagnosticArtifact':descriptor}
        def put(name,b):
            fd=os.open(directory/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'wb') as out:out.write(b)
        put('raw.json',wire.canonical(envelope));put('diagnostics.v2',data)
        fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY)
        self.addCleanup(os.close,fd)
        def receipt(name):
            p=directory/name;return {'stat':consumer.stamp(p.stat()),'sha256':consumer.digest(p.read_bytes())}
        authority={'kind':'R03BoundedPairAuthorityV2','directory':consumer.stamp(os.fstat(fd),consumer.DIR_KEYS),
                   'raw':receipt('raw.json'),'artifact':receipt('diagnostics.v2')}
        return directory,fd,authority,text,envelope,fields

    def invoke(self,pair,**kwargs):
        d,fd,authority,text,_,_=pair
        return consumer.verify_v2_pair(fd,kwargs.get('authority',authority),kwargs.get('request_text',text),
            kwargs.get('launch',self.launch),kwargs.get('build',self.build),kwargs.get('pins',PINS))

    def refresh(self,pair,key):
        d,fd,a,txt,e,f=pair
        p=d/('raw.json' if key=='raw' else 'diagnostics.v2')
        a[key]={'stat':consumer.stamp(p.stat()),'sha256':consumer.digest(p.read_bytes())}

class V2AdmissionTests(PairFixture):
    def test_complete_both_large_fields_are_losslessly_authenticated(self):
        fields={'finalDiagnostics':json.dumps({'a':'漢'*100000},ensure_ascii=False),
                'finalExecutionDiagnostics':json.dumps({'b':'B'*420000})}
        p=self.pair(fields);got=self.invoke(p)
        self.assertEqual(got['transport'],'NativeBoundedSnapshotV2')
        for name,data in fields.items():
            self.assertGreater(len(data.encode()),262144)
            self.assertEqual(got['fields'][name]['sha256'],consumer.digest(data.encode()))
            self.assertEqual(got['fields'][name]['utf8Bytes'],len(data.encode()))
        self.assertEqual(got['semantic']['result'],'Passed')
        self.assertIs(got['runtimeAcceptance'],False)

    def test_null_is_distinct_from_empty_and_empty_diagnostics_json_rejected(self):
        p=self.pair(dict.fromkeys(wire.FIELDS,None));got=self.invoke(p)
        self.assertTrue(got['fields']['finalDiagnostics']['isNull'])
        p=self.pair(dict.fromkeys(wire.FIELDS,''))
        with self.assertRaises(consumer.AdmissionError):self.invoke(p)

    def test_failed_semantic_report_is_not_promoted(self):
        p=self.pair(raw={**self.raw,'result':'Failed'})
        with self.assertRaises(ContractError):self.invoke(p)

    def test_field_side_effect_remains_rejected(self):
        p=self.pair(raw={**self.raw,'finalShadowField':3})
        with self.assertRaises(ContractError):self.invoke(p)

    def test_v1_entrypoint_still_rejects_direct_v2(self):
        with self.assertRaises(ContractError):
            verify_ir({**self.raw,'reportTransport':'NativeBoundedSnapshotV2'},self.request,self.launch,self.build)

    def test_unknown_transport_never_falls_back_to_v1(self):
        p=self.pair();p[4]['reportTransport']='NativePreopenedSnapshotV1'
        (p[0]/'raw.json').write_bytes(wire.canonical(p[4]));self.refresh(p,'raw')
        with self.assertRaises(consumer.AdmissionError):self.invoke(p)

    def test_external_raw_digest_required(self):
        p=self.pair();p[2]['raw']['sha256']='0'*64
        with self.assertRaises(consumer.AdmissionError):self.invoke(p)

    def test_external_sidecar_receipt_not_self_reported(self):
        p=self.pair();p[2]['artifact']['sha256']='0'*64
        with self.assertRaises(consumer.AdmissionError):self.invoke(p)

    def test_cross_process_replay(self):
        p=self.pair()
        with self.assertRaises(wire.ContractError):self.invoke(p,launch={'pid':12035,'exitCode':0})

    def test_exact_request_bytes_not_canonicalized_before_binding(self):
        p=self.pair()
        with self.assertRaisesRegex(consumer.AdmissionError,'raw/launch request digest'):
            self.invoke(p,request_text=json.dumps(self.request))

    def test_raw_request_digest_must_match_external_request(self):
        p=self.pair(raw={**self.raw,'requestSha256':'e'*64})
        with self.assertRaisesRegex(consumer.AdmissionError,'raw/launch request digest'):
            self.invoke(p)

    def test_missing_raw_request_digest_rejected(self):
        p=self.pair();del p[4]['requestSha256']
        (p[0]/'raw.json').write_bytes(wire.canonical(p[4]));self.refresh(p,'raw')
        with self.assertRaisesRegex(consumer.AdmissionError,'raw/launch request digest'):
            self.invoke(p)

    def test_build_or_source_replay(self):
        p=self.pair()
        with self.assertRaises(wire.ContractError):self.invoke(p,build='c'*64)
        with self.assertRaises(wire.ContractError):self.invoke(p,pins={**PINS,'il2cpp_plus':'c'*40})

    def test_nonzero_original_exit_fails_before_raw_is_considered(self):
        p=self.pair()
        with self.assertRaises(consumer.AdmissionError):self.invoke(p,launch={'pid':self.launch['pid'],'exitCode':2})

    def test_boolean_pid_and_exit_rejected(self):
        p=self.pair()
        for launch in ({'pid':True,'exitCode':0},{'pid':self.launch['pid'],'exitCode':False}):
            with self.assertRaises(consumer.AdmissionError):self.invoke(p,launch=launch)

    def test_engine_case_requires_original_engine_verifier(self):
        self.request['stimulus']='engine-unhandled';p=self.pair()
        with self.assertRaises(consumer.AdmissionError):self.invoke(p)

    def test_unowned_or_world_readable_directory_refused(self):
        p=self.pair();os.chmod(p[0],0o755)
        with self.assertRaises(consumer.AdmissionError):self.invoke(p)

    def test_wrong_recorded_directory_inode(self):
        p=self.pair();p[2]['directory']['st_ino']+=1
        with self.assertRaises(consumer.AdmissionError):self.invoke(p)

    def test_world_writable_file_refused_even_with_matching_hash(self):
        p=self.pair();os.chmod(p[0]/'raw.json',0o666);self.refresh(p,'raw')
        with self.assertRaises(consumer.AdmissionError):self.invoke(p)

    def test_symlink_refused_no_target_write(self):
        p=self.pair();d=p[0];target=d/'kept';target.write_bytes(b'keep')
        (d/'raw.json').unlink();(d/'raw.json').symlink_to(target)
        with self.assertRaises(ERRORS):self.invoke(p)
        self.assertEqual(target.read_bytes(),b'keep')

    def test_hardlink_refused(self):
        p=self.pair();os.link(p[0]/'raw.json',p[0]/'other');self.refresh(p,'raw')
        with self.assertRaises(consumer.AdmissionError):self.invoke(p)

    def test_missing_file_refused(self):
        p=self.pair();(p[0]/'diagnostics.v2').unlink()
        with self.assertRaises(FileNotFoundError):self.invoke(p)

    def test_fifo_does_not_block(self):
        p=self.pair();f=p[0]/'diagnostics.v2';f.unlink();os.mkfifo(f,0o600)
        with self.assertRaises(consumer.AdmissionError):self.invoke(p)

    def test_stale_inode_after_same_byte_replacement(self):
        p=self.pair();f=p[0]/'raw.json';b=f.read_bytes();other=p[0]/'new';other.write_bytes(b);os.chmod(other,0o600);other.replace(f)
        with self.assertRaises(consumer.AdmissionError):self.invoke(p)

    def test_same_size_mutation_cannot_pass_hash_or_stat(self):
        p=self.pair();f=p[0]/'diagnostics.v2';b=bytearray(f.read_bytes());b[150]^=1;f.write_bytes(b)
        with self.assertRaises(ERRORS):self.invoke(p)

    def test_mutation_after_decode_detected_before_predicates(self):
        p=self.pair();real=wire.decode
        def change(*args,**kw):
            result=real(*args,**kw);f=p[0]/'raw.json';f.write_bytes(f.read_bytes());return result
        with patch.object(wire,'decode',side_effect=change),patch('run_terminal_local._verify_ir_semantics') as sem:
            with self.assertRaises(consumer.AdmissionError):self.invoke(p)
            sem.assert_not_called()

    def test_corruption_rehashing_descriptor_is_not_enough(self):
        p=self.pair();f=p[0]/'diagnostics.v2';b=bytearray(f.read_bytes());b[154]^=1;f.write_bytes(b);self.refresh(p,'artifact')
        p[4]['diagnosticArtifact']['sha256']=consumer.digest(b)
        (p[0]/'raw.json').write_bytes(wire.canonical(p[4]));self.refresh(p,'raw')
        with self.assertRaises(wire.ContractError):self.invoke(p)

    def test_trailing_partial_and_swapped_sections_rejected(self):
        for mode in ('trailing','partial','slot'):
            p=self.pair();f=p[0]/'diagnostics.v2';b=bytearray(f.read_bytes())
            if mode=='trailing':b+=b'x'
            elif mode=='partial':b=b[:-1]
            else:b[72]=15
            f.write_bytes(b);self.refresh(p,'artifact')
            p[4]['diagnosticArtifact'].update(sha256=consumer.digest(b),bytes=len(b))
            (p[0]/'raw.json').write_bytes(wire.canonical(p[4]));self.refresh(p,'raw')
            with self.assertRaises(wire.ContractError):self.invoke(p)

    def test_missing_descriptor_and_inline_collision(self):
        for mode in ('missing','inline','path'):
            p=self.pair()
            if mode=='missing':del p[4]['diagnosticArtifact']
            elif mode=='inline':p[4]['finalDiagnostics']='{}'
            else:p[4]['diagnosticArtifact']['path']='../outside'
            (p[0]/'raw.json').write_bytes(wire.canonical(p[4]));self.refresh(p,'raw')
            with self.assertRaises(ERRORS):self.invoke(p)

    def test_oversized_envelope_or_artifact_rejected_before_read(self):
        p=self.pair()
        for key,size in (('raw',wire.RESERVE+1),('artifact',wire.MAX_STREAM+1)):
            authority=copy.deepcopy(p[2]);authority[key]['stat']['st_size']=size
            with self.assertRaises(consumer.AdmissionError):self.invoke(p,authority=authority)

    def test_duplicate_keys_in_raw_and_diagnostic_rejected(self):
        p=self.pair();f=p[0]/'raw.json';b=f.read_bytes();f.write_bytes(b'{"result":"Failed",'+b[1:]);self.refresh(p,'raw')
        with self.assertRaises(consumer.AdmissionError):self.invoke(p)
        p=self.pair({'finalDiagnostics':'{"x":1,"x":2}','finalExecutionDiagnostics':'{}'})
        with self.assertRaises(consumer.AdmissionError):self.invoke(p)

    def test_nonfinite_and_numeric_overflow_not_normalized(self):
        for n in ('NaN','Infinity','1e999','9'*129):
            p=self.pair({'finalDiagnostics':'{"x":'+n+'}','finalExecutionDiagnostics':'{}'})
            with self.assertRaises(consumer.AdmissionError):self.invoke(p)

    def test_unpaired_json_surrogates_rejected_without_normalization(self):
        value='{"bad":"'+chr(92)+'ud800"}'
        p=self.pair({'finalDiagnostics':value,'finalExecutionDiagnostics':'{}'})
        with self.assertRaises(consumer.AdmissionError):self.invoke(p)

    def test_json_depth_and_token_budgets(self):
        for value in ('['*65+'0'+']'*65,'['+','.join(['0']*(consumer.JSON_TOKENS+2))+']'):
            p=self.pair({'finalDiagnostics':value,'finalExecutionDiagnostics':'{}'})
            with self.assertRaises(consumer.AdmissionError):self.invoke(p)

    def test_original_recovery_duplicate_key_is_not_normalized(self):
        r={**self.raw,'firstRecovery':'{"published":false,"published":true}'}
        p=self.pair(raw=r)
        with self.assertRaises(consumer.AdmissionError):self.invoke(p)

    def test_unicode_cross_frame_roundtrip(self):
        value='{"text":"'+'a'*65524+'😀€漢字'+ 'b'*70000+'"}'
        p=self.pair({'finalDiagnostics':value,'finalExecutionDiagnostics':'{}'})
        self.assertEqual(self.invoke(p)['fields']['finalDiagnostics']['sha256'],consumer.digest(value.encode()))

    def test_no_input_or_process_resource_mutation(self):
        import resource
        before=resource.getrlimit(resource.RLIMIT_AS)
        p=self.pair();contents={x.name:x.read_bytes() for x in p[0].iterdir()}
        self.invoke(p)
        self.assertEqual(contents,{x.name:x.read_bytes() for x in p[0].iterdir()})
        self.assertEqual(before,resource.getrlimit(resource.RLIMIT_AS))

    def test_isolated_worker_passes_complete_report_and_preserves_parent_limits(self):
        import resource
        p=self.pair({'finalDiagnostics':json.dumps({'data':'x'*600000}),'finalExecutionDiagnostics':'{}'})
        before=resource.getrlimit(resource.RLIMIT_AS)
        result=consumer.verify_isolated(p[1],p[2],p[3],self.launch,self.build,PINS)
        self.assertEqual(result['result'],'Passed');self.assertFalse(result['runtimeAcceptance'])
        self.assertEqual(before,resource.getrlimit(resource.RLIMIT_AS))

    def test_isolated_worker_failed_semantics_cannot_pass(self):
        p=self.pair(raw={**self.raw,'result':'Failed'})
        with self.assertRaises(consumer.AdmissionError):consumer.verify_isolated(p[1],p[2],p[3],self.launch,self.build,PINS)

    def test_bad_worker_input_bounded(self):
        with self.assertRaises(consumer.AdmissionError):consumer.bounded_json('['*10000+'0'+']'*10000,65536)

    def test_reference_wire_and_original_semantic_predicates_preserved(self):
        root=IR.parents[2]
        ref=root/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/reference/diagnostic_stream.py'
        self.assertEqual(ref.read_bytes(),(HERE/'diagnostic_wire.py').read_bytes())
        # Baseline semantic AST is recorded by source hash in the companion run audit.
        current=ast.parse((IR/'run_terminal_local.py').read_text())
        functions={f.name:f for f in current.body if isinstance(f,ast.FunctionDef)}
        wrapper=functions['verify_ir'];body=functions['_verify_ir_semantics'].body
        self.assertEqual(len(wrapper.body),2)
        self.assertIn('NativePreopenedSnapshotV1',ast.unparse(wrapper.body[0]))
        # AST serialization differs across Python versions. Parse the exact
        # original function and candidate in THIS interpreter, after checking
        # the retained original byte hash; never accept a version-specific list.
        original=(HERE/'original_verify_ir.txt').read_bytes()
        self.assertEqual(consumer.digest(original),'77b47c0dda798ef6f9712a930b3a22fb5096ba86f05e988520072362c9add297')
        baseline=ast.parse(original).body[0]
        self.assertEqual(baseline.name,'verify_ir')
        self.assertEqual(ast.dump(ast.Module(body=body,type_ignores=[]),include_attributes=False),
                         ast.dump(ast.Module(body=baseline.body[1:],type_ignores=[]),include_attributes=False))

class OriginalSemanticNegativesV2(original_tests.TerminalReceiptContractTests, PairFixture):
    """Every inherited original semantic test now traverses the authenticated V2 path."""
    def setUp(self):
        PairFixture.setUp(self)
        self.build_sha=self.build
    def verify(self):
        return self.invoke(self.pair())['semantic']

if __name__=='__main__':
    unittest.main(verbosity=2)
