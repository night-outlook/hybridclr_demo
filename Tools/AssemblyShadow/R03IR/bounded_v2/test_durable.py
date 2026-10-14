#!/usr/bin/env python3
"""Actual general serializer -> fixed capture -> POSIX durable pair -> V2 reader.

Synthetic immutable metadata and execution JSON; no VM capture/Unity integration.
Owned fault-injection fixtures are archived losslessly before temp cleanup.
"""
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json, os, shutil, subprocess, sys, tarfile, tempfile, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=None; WORK=None; NATIVE=None; REPO=None; CODEC=None; RESOLVER=None; DRIVER=None
PROFILE=''; SEQ=0; COMMANDS=[]
IDENTITY=dict(runId='durable-v2',caseId='native-format',processId=1234,requestSha256='a'*64,buildSha256='b'*64,demoCommit='1'*40,hybridclrCommit='2'*40,packageCommit='3'*40,nativeCommit='4'*40)
INLINE=dict(reportTransport='NativeBoundedSnapshotV2',status='Failed',preReflection=42,preDelegate=42)

def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def need(ok,msg):
    if not ok:raise RuntimeError(msg)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj

def run(argv,label):
    p=OUT/PROFILE/label;p.parent.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',ASAN_OPTIONS='abort_on_error=1:detect_leaks='+('0' if sys.platform=='darwin' else '1'),UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    r=subprocess.run([str(x) for x in argv],cwd=OUT,capture_output=True,env=env,timeout=120)
    p.with_suffix('.stdout').write_bytes(r.stdout);p.with_suffix('.stderr').write_bytes(r.stderr)
    rec=dict(argv=[str(x) for x in argv],cwd=str(OUT),exitCode=r.returncode,stdoutSha256=sha(r.stdout),stderrSha256=sha(r.stderr),label=str(p.relative_to(OUT)),asan=env['ASAN_OPTIONS'],ubsan=env['UBSAN_OPTIONS'])
    p.with_suffix('.command.json').write_text(json.dumps(rec,indent=2)+'\n');COMMANDS.append(rec)
    need(r.returncode==0,'failed actual command: '+str(p))
    return r

def case(mode='ok',classes=2,inline=None,execution=None,prepare=None,fail=(-1,0)):
    global SEQ
    SEQ+=1;label=f'case-{SEQ:04d}'
    d=WORK/PROFILE/label;d.mkdir(parents=True);root=d/'owned';root.mkdir(mode=0o700)
    inline=INLINE if inline is None else inline
    execution='{"classes":[],"runtime":"synthetic execution input"}' if execution is None else execution
    (d/'inline.json').write_bytes(CODEC.canonical(inline));(d/'execution.json').write_text(execution)
    invoked=str(root)
    if prepare:invoked=prepare(root) or invoked
    result=json.loads(run([DRIVER,mode,invoked,d/'inline.json',d/'execution.json',CODEC.binding(IDENTITY).hex(),classes,*fail],label).stdout)
    need(result['formatNew']==0 and result['transactionNew']==0,'operator-new in prepared formatter/transaction')
    return root,result

def view(root,result,identity=None,receipt=None):
    return RESOLVER.read_transaction(str(root),result['receipt']['directory'],result['receipt'] if receipt is None else receipt,IDENTITY if identity is None else identity,CODEC)

class DurableTests(unittest.TestCase):
    def test_actual_general_serializer_full_roundtrip(self):
        text=json.dumps({'unicode':'中é🐦','records':[{'value':i} for i in range(25000)]},ensure_ascii=False,separators=(',',':'))
        root,r=case(classes=4096,execution=text);self.assertTrue(r['committed']);v=view(root,r)
        self.assertGreater(r['generalBytes'],262144);self.assertGreater(len(text.encode()),262144)
        self.assertEqual(sha(v['finalDiagnostics'].encode()),r['generalSha256']);self.assertEqual(v['finalExecutionDiagnostics'],text)
        self.assertEqual(len(json.loads(v['finalDiagnostics'])['ordinaryClasses']),4096)
        self.assertEqual(v['status'],'Failed');self.assertEqual(v['reportTransport'],'NativeBoundedSnapshotV2')
        self.assertLessEqual(sum(r['receipt'][k]['bytes'] for k in ('artifact','envelope')),4194304)
    def test_empty_general_inventory(self):
        root,r=case(classes=0);self.assertTrue(r['committed']);self.assertEqual(json.loads(view(root,r)['finalDiagnostics'])['ordinaryClasses'],[])
    def test_positive_short_writes(self):
        root,r=case('short-write');self.assertTrue(r['committed']);self.assertEqual(view(root,r)['status'],'Failed')
    def test_positive_short_reads(self):
        root,r=case('short-read');self.assertTrue(r['committed']);view(root,r)
    def test_all_os_failure_positions(self):
        _,good=case();self.assertTrue(good['committed']);count=0
        for op,total in enumerate(good['calls']):
            for ordinal in range(1,total+1):
                with self.subTest(op=op,ordinal=ordinal):
                    _,r=case(fail=(op,ordinal));self.assertTrue(r['faultTriggered']);self.assertFalse(r['committed']);self.assertFalse(r['receipt']['complete']);self.assertNotEqual(r['error'],0);count+=1
        self.assertGreater(count,50)
    def test_occupied_files_untouched(self):
        for name in ('raw.json','diagnostics.r03v2'):
            def prepare(root): (root/name).write_bytes(b'original retained bytes')
            root,r=case(prepare=prepare);self.assertFalse(r['armed']);self.assertEqual((root/name).read_bytes(),b'original retained bytes')
    def test_symlink_files_untouched(self):
        for name in ('raw.json','diagnostics.r03v2'):
            def prepare(root):
                (root.parent/'sentinel').write_bytes(b'original');(root/name).symlink_to(root.parent/'sentinel')
            root,r=case(prepare=prepare);self.assertFalse(r['armed']);self.assertEqual((root.parent/'sentinel').read_bytes(),b'original')
    def test_linked_root_and_ancestor(self):
        for tail in ('','/child'):
            def prepare(root):
                if tail:(root/'child').mkdir(mode=0o700)
                alias=root.parent/'alias';alias.symlink_to(root,target_is_directory=True);return str(alias)+tail
            _,r=case(prepare=prepare);self.assertFalse(r['armed']);self.assertEqual(r['error'],3)
    def test_noncanonical_spellings(self):
        for suffix in ('/','/.','/../owned'):
            _,r=case(prepare=lambda p:str(p)+suffix);self.assertFalse(r['armed']);self.assertEqual(r['error'],3)
    def test_wrong_directory_identity(self):
        root,r=case('wrong-root');self.assertFalse(r['armed']);self.assertEqual(r['error'],4);self.assertFalse(list(root.iterdir()))
    def test_unprotected_directory_mode(self):
        def prepare(p):p.chmod(0o770)
        root,r=case(prepare=prepare);self.assertFalse(r['armed']);self.assertEqual(r['error'],4);self.assertFalse(list(root.iterdir()))
    def test_rename_root_after_arm(self):
        root,r=case('rename-root');self.assertTrue(r['armed']);self.assertFalse(r['committed']);self.assertFalse(list(root.iterdir()));self.assertTrue(Path(str(root)+'.moved').is_dir())
    def test_file_replacement_after_arm(self):
        root,r=case('replace-artifact');self.assertFalse(r['committed']);self.assertEqual(r['error'],6);self.assertEqual((root/'diagnostics.r03v2').read_bytes(),b'do-not-touch');self.assertEqual((root/'original.r03v2').stat().st_size,0)
    def test_hardlink_after_arm(self):
        root,r=case('hardlink');self.assertFalse(r['committed']);self.assertEqual(r['error'],6);self.assertEqual((root/'diagnostics.r03v2').stat().st_size,0)
    def test_reentry_and_reuse(self):
        for mode in ('reenter','repeat'):
            _,r=case(mode);self.assertFalse(r['committed']);self.assertFalse(r['receipt']['complete']);self.assertNotEqual(r['error'],0)
    def test_aggregate_overflow_has_no_complete_envelope(self):
        root,r=case(execution='"'+'x'*3932160+'"');self.assertFalse(r['captured']);self.assertFalse(r['committed']);self.assertEqual((root/'raw.json').stat().st_size,0)
    def test_invalid_json_envelope_is_not_semantic_success(self):
        root,r=case(inline={'status':'Failed'});self.assertTrue(r['committed'])
        with self.assertRaises((ValueError,OSError)):view(root,r)
    def test_external_receipt_mandatory(self):
        root,r=case();bad=copy.deepcopy(r['receipt']);bad['complete']=False
        with self.assertRaises(ValueError):view(root,r,receipt=bad)
    def test_reader_inode_and_symlink_mismatch(self):
        root,r=case();os.rename(root/'raw.json',root/'original.json');(root/'raw.json').symlink_to(root/'original.json')
        with self.assertRaises((ValueError,OSError)):view(root,r)
    def test_reader_context_replay_rejected(self):
        root,r=case()
        for key,new in (('processId',1235),('requestSha256','f'*64),('nativeCommit','f'*40)):
            identity={**IDENTITY,key:new}
            with self.assertRaises(ValueError):view(root,r,identity=identity)
    def test_reader_corruption_partial_and_trailing(self):
        for op in ('change','short','trailing'):
            root,r=case();p=root/'diagnostics.r03v2';b=p.read_bytes()
            p.write_bytes((b[:-1]+bytes([b[-1]^1])) if op=='change' else b[:-1] if op=='short' else b+b'x')
            with self.assertRaises(ValueError):view(root,r)
    def test_reader_duplicate_json_keys(self):
        root,r=case();p=root/'raw.json';b=p.read_bytes();b=b[:-1]+b',"status":"Passed"}';p.write_bytes(b)
        # Even self-consistent malicious producer bytes do not bypass strict JSON.
        r['receipt']['envelope']['bytes']=len(b);r['receipt']['envelope']['sha256']=sha(b)
        with self.assertRaises(ValueError):view(root,r)
    def test_reader_resource_and_boolean_integer_negative(self):
        root,r=case()
        for key,value in (('bytes',5000000),('inode',True)):
            bad=copy.deepcopy(r['receipt']);bad['artifact'][key]=value
            with self.assertRaises(ValueError):view(root,r,receipt=bad)
    def test_reader_nonfinite_exponent(self):
        for text in ('1e999','-1e999','NaN','Infinity'):
            with self.assertRaises(ValueError):RESOLVER.strict_json('{"value":'+text+'}')
    def test_reader_rejects_directory_type_confusion(self):
        root,r=case();bad=copy.deepcopy(r['receipt']);bad['directory']['owner']=bool(bad['directory']['owner'])
        with self.assertRaises(ValueError):view(root,r,receipt=bad)
    def test_failed_sync_cannot_be_read_as_committed(self):
        root,r=case(fail=(7,2));self.assertFalse(r['committed']);self.assertGreater((root/'raw.json').stat().st_size,0)
        with self.assertRaises(ValueError):view(root,r)

def main():
    global OUT,WORK,NATIVE,REPO,CODEC,RESOLVER,DRIVER,PROFILE
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,required=True);p.add_argument('--native',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    need(__debug__,'Assertions must remain enabled');REPO=a.repository.resolve(strict=True);NATIVE=a.native.resolve(strict=True);OUT=a.output
    need(OUT.is_absolute() and OUT==OUT.resolve(strict=False) and OUT.parent.is_dir() and not OUT.exists(),'Fresh external canonical output required')
    need(all(OUT!=x and x not in OUT.parents and OUT not in x.parents for x in (REPO,NATIVE)),'Output outside source')
    ref=REPO/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/reference/diagnostic_stream.py'
    need(blob(ref.read_bytes())=='0866b07f758a20284d2a5d5d933b2be577b20b50','Original codec reference changed')
    need(blob((HERE/'BoundedDiagnosticsV2.h').read_bytes())=='174766c40235216d8c954107dd5e026116a510fa','Original native codec changed')
    CODEC=load('immutable_codec',ref);RESOLVER=load('durable_reader',HERE/'read_transaction.py')
    paths=[ref,*[HERE/n for n in ('BoundedDiagnosticsV2.h','PosixDiagnosticTransaction.h','durable_driver.cpp','read_transaction.py','test_durable.py')],*[NATIVE/'libil2cpp/vm'/n for n in ('AssemblyShadowDiagnostics.cpp','AssemblyShadowDiagnostics.h','AssemblyShadowDiagnosticWriter.h','AssemblyShadowTypes.h')],NATIVE/'tools/r03/diagnostic_stream/allocation_probe.cpp']
    sources={str(x):dict(gitBlob=blob(x.read_bytes()),sha256=sha(x.read_bytes()),bytes=x.stat().st_size) for x in paths}
    OUT.mkdir();(OUT/'stubs').mkdir();(OUT/'stubs/il2cpp-config.h').write_text('#pragma once\n// Explicit host configuration stub; not installed SDK.\n')
    profiles=[];verified=False
    try:
        for name,flags in [('strict',[]),('sanitized',['-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
            PROFILE=name;folder=OUT/name;folder.mkdir();DRIVER=folder/'durable'
            compiler=shutil.which(os.environ.get('CXX','clang++'));need(compiler,'Compiler unavailable')
            run([compiler,'-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-pedantic',*flags,'-I'+str(HERE),'-I'+str(NATIVE/'libil2cpp/vm'),'-I'+str(OUT/'stubs'),HERE/'durable_driver.cpp',NATIVE/'libil2cpp/vm/AssemblyShadowDiagnostics.cpp',NATIVE/'tools/r03/diagnostic_stream/allocation_probe.cpp','-o',DRIVER],'compile')
            with tempfile.TemporaryDirectory(prefix='owned-fixtures-',dir=OUT) as temporary:
                WORK=Path(temporary).resolve(strict=True)
                try:
                    with (folder/'tests.log').open('w') as stream:r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(DurableTests))
                finally:
                    with tarfile.open(folder/'owned-fixtures.tar.gz','w:gz',dereference=False) as t:t.add(WORK,arcname='owned-fixtures')
            profiles.append(dict(name=name,tests=r.testsRun,failures=len(r.failures),errors=len(r.errors),skipped=len(r.skipped)))
            need(r.wasSuccessful() and not r.skipped,'Tests failed; retain '+str(folder/'tests.log'))
        verified=True
    finally:
        unchanged=sources=={str(x):dict(gitBlob=blob(x.read_bytes()),sha256=sha(x.read_bytes()),bytes=x.stat().st_size) for x in paths}
        result=dict(kind='NativeV2DurableFileHostIntegration',result='PassedWithinHostScope' if verified and unchanged else 'FailedOrIncomplete',profiles=profiles,sources=sources,sourceUnchanged=unchanged,commands=COMMANDS,actualGeneralSerializer=True,syntheticVmCapture=True,executionDiagnosticIsFixture=True,realPosixIO=True,operatorNewDuringPreparedCode=0 if verified else None,physicalPowerLossProven=False,actualUnity=False,playerTransportEnabled=False,engineContainmentImplemented=False)
        (OUT/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    need(verified and unchanged,'Validation incomplete')
    print(json.dumps({'result':result['result'],'profiles':profiles,'commands':len(COMMANDS)},indent=2))
if __name__=='__main__':main()
