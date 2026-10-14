#!/usr/bin/env python3
"""Host-only V2 disk transaction tests; real files/codec, synthetic VM inputs."""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent
REFERENCE = Path('Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/reference/diagnostic_stream.py')
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
OUT = None
BIN = None
REFERENCE_MODULE = None
READER = None
RECORDS = []
CASE_ID = 0
PROFILE = ''


def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(argv):
    step=OUT/'commands'/f'{len(RECORDS):04}'
    step.mkdir(parents=True)
    completed=subprocess.run([str(x) for x in argv],capture_output=True,env=ENV,timeout=45)
    (step/'stdout').write_bytes(completed.stdout)
    (step/'stderr').write_bytes(completed.stderr)
    receipt=dict(argv=[str(x) for x in argv],cwd=str(Path.cwd()),profile=PROFILE,exit=completed.returncode,
                 stdoutSha256=sha(completed.stdout),stderrSha256=sha(completed.stderr))
    (step/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    RECORDS.append(receipt)
    if completed.returncode:
        raise AssertionError(f'command failed {step}: {completed.stderr.decode(errors="replace")[-3000:]}')
    return completed.stdout


class FileTests(unittest.TestCase):
    def setUp(self):
        global CASE_ID
        self.area=OUT/'cases'/f'{PROFILE}-{CASE_ID:04}';CASE_ID+=1
        self.area.mkdir(parents=True)
        self.root=self.area/'output';self.root.mkdir(mode=0o700)
        self.identity=dict(runId='synthetic',caseId='type',processId=123,requestSha256='1'*64,buildSha256='2'*64,
            demoCommit='3'*40,hybridclrCommit='4'*40,packageCommit='5'*40,nativeCommit='6'*40)
        self.inline=dict(reportTransport='NativeBoundedSnapshotV2',result='Passed',phase=900,processId=123)
        self.fields=dict(finalDiagnostics='{"a":1}',finalExecutionDiagnostics='{"b":2}')

    def execute(self,mode='normal',fail=0,root=None,inline=None,fields=None):
        inline=self.inline if inline is None else inline
        fields=self.fields if fields is None else fields
        for name,data in [('inline',REFERENCE_MODULE.canonical(inline)),('a',fields['finalDiagnostics'].encode()),('b',fields['finalExecutionDiagnostics'].encode())]:
            (self.area/name).write_bytes(data)
        stdout=run([BIN,root or self.root,REFERENCE_MODULE.binding(self.identity).hex(),self.area/'inline',self.area/'a',self.area/'b',mode,str(fail)])
        result=json.loads(stdout)
        self.assertEqual(result['operatorNewCalls'],0)
        return result

    def decode(self,receipt):
        raw,artifact=READER.read_verified_files(self.root,receipt)
        envelope=REFERENCE_MODULE.strict_json(raw.decode())
        view=REFERENCE_MODULE.hydrate(envelope,artifact,envelope['diagnosticArtifact'],self.identity)
        self.assertEqual(sha(raw),receipt['envelope']['sha256'])
        self.assertEqual(sha(artifact),receipt['artifact']['sha256'])
        return view

    def test_complete_real_file_roundtrip(self):
        receipt=self.execute();self.assertTrue(receipt['complete'])
        view=self.decode(receipt)
        self.assertEqual(view['finalDiagnostics'],self.fields['finalDiagnostics'])
        self.assertEqual(view['finalExecutionDiagnostics'],self.fields['finalExecutionDiagnostics'])

    def test_both_fields_above_old_single_slot_limit(self):
        self.fields={name:json.dumps({'text':char*330000},ensure_ascii=False) for name,char in zip(self.fields,('a','b'))}
        receipt=self.execute();self.assertTrue(receipt['complete']);view=self.decode(receipt)
        self.assertTrue(all(view[k]==v for k,v in self.fields.items()))

    def test_unicode_across_chunks(self):
        self.fields['finalDiagnostics']=json.dumps({'text':'x'*65520+'🙂零'*30000},ensure_ascii=False)
        receipt=self.execute();self.assertTrue(receipt['complete'])
        self.assertEqual(self.decode(receipt)['finalDiagnostics'],self.fields['finalDiagnostics'])

    def test_null_fields_distinct(self):
        receipt=self.execute('null');self.assertTrue(receipt['complete']);view=self.decode(receipt)
        self.assertIsNone(view['finalDiagnostics']);self.assertIsNone(view['finalExecutionDiagnostics'])

    def test_failed_semantics_never_upgraded(self):
        self.inline['result']='Failed';receipt=self.execute();self.assertTrue(receipt['complete'])
        self.assertEqual(self.decode(receipt)['result'],'Failed');self.assertFalse(receipt['semanticAcceptance'])

    def test_raw_mode_and_single_link(self):
        receipt=self.execute();self.assertTrue(receipt['complete'])
        for name in READER.NAMES:
            info=(self.root/name).stat();self.assertEqual(stat.S_IMODE(info.st_mode),0o600);self.assertEqual(info.st_nlink,1)

    def test_occupied_artifact_preserved(self):
        path=self.root/READER.NAMES[0];path.write_bytes(b'original')
        receipt=self.execute();self.assertFalse(receipt['complete']);self.assertEqual(path.read_bytes(),b'original')
        self.assertFalse((self.root/'raw.json').exists())

    def test_occupied_raw_preserved_and_empty_artifact_retained(self):
        path=self.root/'raw.json';path.write_bytes(b'original')
        receipt=self.execute();self.assertFalse(receipt['complete']);self.assertEqual(path.read_bytes(),b'original')
        self.assertEqual((self.root/READER.NAMES[0]).read_bytes(),b'')

    def test_artifact_symlink_rejected(self):
        target=self.area/'original';target.write_bytes(b'keep');(self.root/READER.NAMES[0]).symlink_to(target)
        receipt=self.execute();self.assertFalse(receipt['complete']);self.assertEqual(target.read_bytes(),b'keep')

    def test_noncanonical_parent_rejected(self):
        alias=self.area/'alias';alias.symlink_to(self.area,target_is_directory=True)
        receipt=self.execute(root=alias/'output');self.assertFalse(receipt['complete']);self.assertEqual(list(self.root.iterdir()),[])

    def test_wrong_directory_identity_rejected(self):
        receipt=self.execute('wrong-root');self.assertFalse(receipt['complete']);self.assertEqual(list(self.root.iterdir()),[])

    def test_writable_directory_rejected(self):
        self.root.chmod(0o777);receipt=self.execute();self.assertFalse(receipt['complete'])

    def test_original_root_replaced_after_arm(self):
        receipt=self.execute('root-replace');self.assertTrue(receipt['faultActed']);self.assertFalse(receipt['complete'])
        self.assertEqual(list(self.root.iterdir()),[]);self.assertTrue(Path(str(self.root)+'.original').exists())

    def test_leaf_replaced_during_publication(self):
        receipt=self.execute('replace');self.assertTrue(receipt['faultActed']);self.assertFalse(receipt['complete'])
        self.assertTrue((self.root/'retained-original.bin').is_file())

    def test_extra_hardlink_rejected(self):
        receipt=self.execute('hardlink');self.assertTrue(receipt['faultActed']);self.assertFalse(receipt['complete'])

    def test_corruption_detected_by_descriptor_readback(self):
        receipt=self.execute('corrupt');self.assertTrue(receipt['faultActed']);self.assertFalse(receipt['complete'])
        self.assertEqual((self.root/'raw.json').read_bytes(),b'')

    def test_synchronous_reentry_rejected(self):
        receipt=self.execute('reentry');self.assertTrue(receipt['faultActed']);self.assertFalse(receipt['complete'])
        self.assertEqual(receipt['error'],3)

    def test_transaction_reuse_refused(self):
        receipt=self.execute('reuse');self.assertTrue(receipt['complete']);self.assertTrue(receipt['reuseRejected']);self.decode(receipt)

    def test_artifact_budget_overflow(self):
        self.fields['finalDiagnostics']='x'*(3932160+1)
        receipt=self.execute();self.assertFalse(receipt['complete']);self.assertEqual((self.root/'raw.json').read_bytes(),b'')

    def test_inline_budget_overflow(self):
        self.inline['value']='x'*258048
        receipt=self.execute();self.assertFalse(receipt['complete']);self.assertEqual((self.root/'raw.json').read_bytes(),b'')

    def test_every_gate_failure_prevents_receipt(self):
        receipt=self.execute();self.assertTrue(receipt['complete']);calls=receipt['gateCalls']
        self.assertGreater(calls,20)
        for at in range(1,calls+1):
            with self.subTest(event=at):
                root=self.area/f'failure-{at}';root.mkdir(mode=0o700)
                failure=self.execute(fail=at,root=root)
                self.assertFalse(failure['complete']);self.assertEqual(failure['error'],8);self.assertEqual(failure['errno'],5)

    def test_consumer_rejects_incomplete_receipt(self):
        receipt=self.execute();receipt['complete']=False
        with self.assertRaises(READER.FileContractError):self.decode(receipt)

    def test_consumer_rejects_wrong_pid_context(self):
        receipt=self.execute();self.identity['processId']+=1
        with self.assertRaises(REFERENCE_MODULE.ContractError):self.decode(receipt)

    def test_consumer_rejects_corrupt_artifact(self):
        receipt=self.execute();path=self.root/READER.NAMES[0];data=bytearray(path.read_bytes());data[-1]^=1;path.write_bytes(data)
        with self.assertRaises(READER.FileContractError):self.decode(receipt)

    def test_consumer_rejects_changed_inode(self):
        receipt=self.execute();path=self.root/READER.NAMES[0];data=path.read_bytes();path.rename(self.root/'original.bin');path.write_bytes(data);path.chmod(0o600)
        with self.assertRaises(READER.FileContractError):self.decode(receipt)

    def test_consumer_rejects_extra_hardlink(self):
        receipt=self.execute();os.link(self.root/'raw.json',self.root/'second.json')
        with self.assertRaises(READER.FileContractError):self.decode(receipt)

    def test_consumer_rejects_boolean_size(self):
        receipt=self.execute();receipt['envelope']['bytes']=True
        with self.assertRaises(READER.FileContractError):self.decode(receipt)

    def test_consumer_rejects_symlink_parent(self):
        receipt=self.execute();alias=self.area/'alias';alias.symlink_to(self.area,target_is_directory=True)
        with self.assertRaises(OSError):READER.read_verified_files(alias/'output',receipt)

    def test_invalid_json_is_not_semantic_snapshot(self):
        self.fields['finalDiagnostics']='invalid json'
        receipt=self.execute();self.assertTrue(receipt['complete'])
        with self.assertRaises(REFERENCE_MODULE.ContractError):self.decode(receipt)


def main():
    global OUT,BIN,REFERENCE_MODULE,READER,PROFILE
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();repo=args.repository.resolve(strict=True);OUT=args.output
    if not __debug__:raise RuntimeError('Assertions required')
    if not OUT.is_absolute() or OUT!=OUT.resolve() or OUT.exists() or not OUT.parent.is_dir() or repo in OUT.parents or OUT in repo.parents:
        raise RuntimeError('Unused canonical external output required')
    OUT.mkdir()
    REFERENCE_MODULE=load(repo/REFERENCE,'v2_reference')
    READER=load(ROOT/'read_verified_files.py','v2_files_reader')
    sources=[ROOT/'BoundedFileTransactionV2.h',ROOT/'BoundedDiagnosticsV2.h',ROOT/'file_transaction_driver.cpp',ROOT/'read_verified_files.py',Path(__file__).resolve(),repo/REFERENCE]
    snapshots=OUT/'sources';snapshots.mkdir()
    bindings=[]
    for path in sources:
        data=path.read_bytes();target=snapshots/path.name;target.write_bytes(data)
        bindings.append(dict(path=str(path.relative_to(repo)),bytes=len(data),sha256=sha(data),gitBlob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()))
    cxx=os.environ.get('CXX','clang++');results=[];ok=False
    try:
        for PROFILE in ('strict','sanitized'):
            BIN=OUT/('driver-'+PROFILE)
            flags=['-std=c++17','-Wall','-Wextra','-Werror','-pedantic','-O1','-g']
            if PROFILE=='sanitized':
                flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
                if sys.platform!='darwin':flags+=['-no-pie']
                ENV['ASAN_OPTIONS']='detect_leaks='+('0' if sys.platform=='darwin' else '1')+':abort_on_error=1'
                ENV['UBSAN_OPTIONS']='halt_on_error=1:print_stacktrace=1'
            run([cxx,*flags,ROOT/'file_transaction_driver.cpp','-o',BIN])
            with (OUT/(PROFILE+'.log')).open('w') as log:
                result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FileTests))
            results.append(dict(profile=PROFILE,tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped)))
            if not result.wasSuccessful() or result.skipped:raise RuntimeError(PROFILE+' failed; preserve logs')
        ok=True
    finally:
        unchanged=all(sha((repo/x['path']).read_bytes())==x['sha256'] for x in bindings)
        summary=dict(kind='InactiveV2FileTransactionHost',result='Passed' if ok and unchanged else 'FailedOrIncomplete',profiles=results,
            sources=bindings,commands=len(RECORDS),sourceUnchanged=unchanged,actualUnity=False,realVmCapture=False,engineAdapter=False,
            powerLossTested=False,semanticAcceptance=False,appleLeakSanitizer='Unavailable' if sys.platform=='darwin' else 'NotApplicable')
        (OUT/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n')
        files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in sorted(OUT.rglob('*')) if p.is_file() and not p.is_symlink()]
        links=[dict(path=str(p.relative_to(OUT)),target=os.readlink(p)) for p in sorted(OUT.rglob('*')) if p.is_symlink()]
        (OUT/'MANIFEST.json').write_text(json.dumps(dict(files=files,syntheticTestSymlinks=links),indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
