#!/usr/bin/env python3
"""Real POSIX two-file tests with the unchanged V2 decoder. No Unity execution."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parent
REFERENCE = 'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/reference/diagnostic_stream.py'
REF_BLOB = '0866b07f758a20284d2a5d5d933b2be577b20b50'
CODEC_BLOB = '174766c40235216d8c954107dd5e026116a510fa'
RECORDS = []
CASES = []
PROFILE = ''
BIN = None
OUT = None
REF = None
SEQ = 0

def sha(data): return hashlib.sha256(data).hexdigest()
def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def write_json(p,value): p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def need(ok,message):
    if not ok: raise RuntimeError(message)

def command(argv,base,env):
    start=time.monotonic();p=subprocess.run(argv,env=env,capture_output=True,timeout=90)
    base.with_suffix('.stdout').write_bytes(p.stdout);base.with_suffix('.stderr').write_bytes(p.stderr)
    r={'argv':argv,'exitCode':p.returncode,'stdoutSha256':sha(p.stdout),'stderrSha256':sha(p.stderr),
       'seconds':time.monotonic()-start}
    RECORDS.append(r);write_json(base.with_suffix('.receipt.json'),r)
    need(p.returncode==0,'compile failed: '+str(base));return p

# Expectations are file-layer outcomes, never semantic/Player acceptance.
GOOD = ['ok','unicode','null','empty','boundary','short-write','short-read',
        'eintr-write','eintr-read','repeat','empty-inline','failed-semantic']
FAULTS = {
    'commit-before-prepare':15,'prepare-reuse':1,'open-root':7,'open-dir':7,'open-artifact':7,'open-envelope':7,'stat':4,'stat-at':5,
    'write-artifact':8,'write-envelope':8,'zero-write':8,'invalid-write-count':8,
    'eintr-write-forever':9,'read-artifact':8,'read-envelope':8,'zero-read':8,
    'invalid-read-count':8,'eintr-read-forever':9,'sync-artifact':13,'sync-envelope':13,
    'full-artifact':13,'full-envelope':13,'sync-dir-first':13,'sync-dir-last':13,
    'close-artifact':14,'close-envelope':14,'close-dir':14,'close-eintr':14,
    'mutate-after-artifact-check':12,'mutate-before-final-check':12,
    'reenter':2,'process-changed':3,'artifact-replaced':6,'envelope-replaced':6,
    'artifact-hardlinked':6,'directory-permission':5,'directory-replaced':5,
    'ancestor-replaced':5,'wrong-root-identity':5,'invalid-utf8':11,'overflow':11,
    'relative':4,'trailing':4,'dot':4,'double-slash':4,'path-too-long':4,
    'alias-root':7,'alias-parent':7,'artifact-occupied':7,'envelope-occupied':7,
    'artifact-symlink':7,'envelope-symlink':7,'writable-root':5,'deep-root':4,
    'inline-too-large':3,'inline-invalid-utf8':3,'inline-not-object':3,
}

class FileTests(unittest.TestCase):
    def exercise(self,case,expected):
        global SEQ
        SEQ += 1
        folder=OUT/PROFILE/f'{SEQ:04d}-{case}';folder.mkdir(parents=True)
        parent=folder/'parent';parent.mkdir(mode=0o700)
        target=parent/'target';target.mkdir(mode=0o700)
        root=target
        untouched=b'original-owned-by-test\x00\xff'
        if case=='alias-root': root=parent/'alias';root.symlink_to(target,target_is_directory=True)
        if case=='alias-parent':
            alias=folder/'alias';alias.symlink_to(parent,target_is_directory=True);root=alias/'target'
        if case in ('artifact-occupied','envelope-occupied'):
            name='diagnostics.v2.bin' if case.startswith('artifact') else 'raw.v2.json'
            (target/name).write_bytes(untouched)
        if case in ('artifact-symlink','envelope-symlink'):
            (folder/'outside').write_bytes(untouched)
            name='diagnostics.v2.bin' if case.startswith('artifact') else 'raw.v2.json'
            (target/name).symlink_to(folder/'outside')
        if case=='writable-root':target.chmod(0o777)
        if case=='deep-root':
            for _ in range(70): root=root/'d';root.mkdir(mode=0o700)
        inline={'caseId':case,'reportTransport':'NativeBoundedSnapshotV2','result':'Failed','runId':'files-7a93'}
        inline_data=REF.canonical(inline)
        if case=='empty-inline':inline={};inline_data=b'{}'
        if case=='inline-too-large':inline_data=b'{'+b' '*REF.TEXT_LIMIT+b'}'
        if case=='inline-invalid-utf8':inline_data=b'{"bad":"\xff"}'
        if case=='inline-not-object':inline_data=b'[]'
        inp=folder/'inline.json';inp.write_bytes(inline_data)
        argv=[str(BIN),str(root),case,str(inp),'-']
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
        if PROFILE=='sanitized':
            env['ASAN_OPTIONS']='halt_on_error=1:detect_leaks='+('0' if sys.platform=='darwin' else '1')
            env['UBSAN_OPTIONS']='halt_on_error=1:print_stacktrace=1'
        start=time.monotonic();p=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(p.stdout,selectors.EVENT_READ)
                need(bool(selector.select(15)),'driver readiness timeout')
            ready=p.stdout.readline();pid=json.loads(ready)['readyPid'];self.assertEqual(pid,p.pid)
            identity={'runId':'files-7a93','caseId':case,'processId':pid,'requestSha256':sha(inline_data),
                      'buildSha256':sha(BIN.read_bytes()),'demoCommit':os.environ.get('GITHUB_SHA','0'*40),
                      'hybridclrCommit':'1'*40,'packageCommit':'2'*40,'nativeCommit':'3'*40}
            binding=REF.binding(identity).hex()
            stdout,stderr=p.communicate((binding+'\n').encode(),timeout=35)
        except BaseException:
            p.kill();p.communicate();raise
        (folder/'stdout.log').write_bytes(ready+stdout);(folder/'stderr.log').write_bytes(stderr)
        rec={'case':case,'argv':argv,'pid':pid,'exitCode':p.returncode,'identity':identity,
             'stdoutSha256':sha(ready+stdout),'stderrSha256':sha(stderr),'seconds':time.monotonic()-start,
             'syntheticIdentityAndFields':True,'realFilesystem':True,'actualUnity':False}
        RECORDS.append(rec);write_json(folder/'command.json',rec)
        self.assertEqual(p.returncode,0,stderr.decode(errors='replace'))
        self.assertNotIn(b'ERROR: AddressSanitizer',stderr);self.assertNotIn(b'runtime error:',stderr)
        result=json.loads(stdout);write_json(folder/'result.json',result);self.assertEqual(result['actualPid'],pid)
        self.assertEqual(result['openCount'],result['closeCount'],'descriptor cleanup count')
        self.assertEqual(result['newAtPrepare'],0);self.assertEqual(result['newAtCommit'],0)
        if expected==0:
            self.assertEqual(result['prepared'],1);self.assertEqual(result['committed'],1);self.assertEqual(result['complete'],1)
            artifact=(target/'diagnostics.v2.bin').read_bytes();envelope=(target/'raw.v2.json').read_bytes()
            self.assertEqual(result['artifactBytes'],len(artifact));self.assertEqual(result['envelopeBytes'],len(envelope))
            self.assertLessEqual(len(artifact),REF.MAX_STREAM);self.assertLessEqual(len(envelope),REF.RESERVE)
            self.assertLessEqual(len(artifact)+len(envelope),REF.TOTAL)
            self.assertEqual(result['artifactSha256'],sha(artifact));self.assertEqual(result['envelopeSha256'],sha(envelope))
            self.assertEqual(result['processId'],pid);self.assertEqual(result['binding'],binding)
            self.assertEqual(result['inlineSha256'],sha(inline_data))
            self.assertEqual(result['artifactInode'],(target/'diagnostics.v2.bin').stat().st_ino)
            self.assertEqual(result['envelopeInode'],(target/'raw.v2.json').stat().st_ino)
            self.assertEqual((target/'diagnostics.v2.bin').stat().st_mode&0o777,0o600)
            self.assertEqual((target/'raw.v2.json').stat().st_mode&0o777,0o600)
            self.assertLess(result['artifactSyncOrder'],result['envelopeFirstOrder'])
            self.assertLess(result['envelopeFirstOrder'],result['envelopeSyncOrder'])
            self.assertEqual(result['appleFullFileSync'],int(sys.platform=='darwin'))
            raw=REF.strict_json(envelope.decode());desc=raw['diagnosticArtifact']
            decoded=REF.decode(io.BytesIO(artifact),desc,identity,inline)
            a='{"data":"'+'a'*300000+'"}';b='{"data":"'+'b'*350000+'"}'
            if case=='unicode':a='{"data":"'+'😀'*100000+'"}'
            if case=='null':a=b=None
            if case=='empty':a=b=''
            if case=='boundary':
                self.assertEqual(len(artifact),REF.MAX_STREAM)
                size=len(decoded['finalExecutionDiagnostics']);b='{"data":"'+'b'*(size-11)+'"}'
            self.assertEqual(decoded,{'finalDiagnostics':a,'finalExecutionDiagnostics':b})
            if case not in ('empty','empty-inline'):
                hydrated=REF.hydrate(raw,artifact,desc,identity);self.assertEqual(hydrated['result'],'Failed')
            else:
                with self.assertRaises(REF.ContractError):REF.hydrate(raw,artifact,desc,identity)
            wrong=dict(identity,processId=pid+1)
            with self.assertRaises(REF.ContractError):REF.decode(io.BytesIO(artifact),desc,wrong,inline)
            if case=='repeat':
                self.assertEqual(result['secondOk'],0);self.assertEqual(result['secondComplete'],0);self.assertEqual(result['repeatError'],1)
            else:self.assertEqual(result['error'],0)
        else:
            self.assertEqual(result['committed'],0);self.assertEqual(result['complete'],0)
            self.assertEqual(result['error'],expected,result)
            self.assertEqual(result['artifactBytes'],0);self.assertEqual(result['envelopeBytes'],0)
            if case=='reenter':self.assertEqual(result['stage'],2)
            if case=='commit-before-prepare':self.assertEqual(result['openCount'],0)
            if case in ('close-artifact','close-envelope','close-dir','close-eintr'):
                self.assertEqual(result['stage'],10)
                self.assertGreater((target/'raw.v2.json').stat().st_size,0) # Bytes alone cannot prove commit success.
            if case in ('eintr-write-forever','eintr-read-forever'):
                self.assertLessEqual(result['writeCalls'] if case.startswith('eintr-write') else result['readCalls'],9)
            if case in ('artifact-occupied','envelope-occupied'):
                name='diagnostics.v2.bin' if case.startswith('artifact') else 'raw.v2.json'
                self.assertEqual((target/name).read_bytes(),untouched)
            if case in ('artifact-symlink','envelope-symlink'):self.assertEqual((folder/'outside').read_bytes(),untouched)
            if case in ('directory-replaced','ancestor-replaced'):
                self.assertEqual(list(target.iterdir()),[],'Replacement directory must receive no writes')
        CASES.append({'profile':PROFILE,'case':case,'expectedFileError':expected,'passed':True})

for name in GOOD:
    setattr(FileTests,'test_'+name.replace('-','_'),lambda self,n=name:self.exercise(n,0))
for name,error in FAULTS.items():
    setattr(FileTests,'test_'+name.replace('-','_'),lambda self,n=name,e=error:self.exercise(n,e))

def main():
    global BIN,OUT,REF,PROFILE
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--compiler',default=os.environ.get('CXX','clang++'));args=p.parse_args()
    need(__debug__,'Assertions must remain enabled')
    repo=args.repository.resolve(strict=True);OUT=args.output
    need(OUT.is_absolute() and OUT==OUT.resolve(strict=False) and OUT.parent.is_dir() and not OUT.exists(),'Unused canonical output required')
    need(repo not in OUT.parents and OUT not in repo.parents and repo!=OUT,'Output must be outside source')
    reference=repo/REFERENCE;need(blob(reference.read_bytes())==REF_BLOB,'Reference source mismatch')
    need(blob((ROOT/'BoundedDiagnosticsV2.h').read_bytes())==CODEC_BLOB,'Codec source mismatch')
    spec=importlib.util.spec_from_file_location('wire_reference',reference);REF=importlib.util.module_from_spec(spec);spec.loader.exec_module(REF)
    paths=[ROOT/'BoundedDiagnosticsV2.h',ROOT/'BoundedDiagnosticsFiles.h',ROOT/'file_driver.cpp',ROOT/'file_allocation_probe.cpp',Path(__file__),reference]
    sources=[{'path':str(f.relative_to(repo)),'blob':blob(f.read_bytes()),'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size} for f in paths]
    OUT.mkdir();summary={'kind':'InactiveV2FileTransactionHostTests','passed':False,'sources':sources,'actualUnity':False,
        'singleOwnerOnly':True,'actualVmCapture':False,'powerLossTested':False,'nativeSchedulerIntegrated':False,
        'untrustedInlineJsonParser':False,'originalV1VerifierChanged':False,'profiles':[]}
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    try:
        for PROFILE in ('strict','sanitized'):
            d=OUT/PROFILE;d.mkdir();BIN=d/'file-driver'
            flags=['-std=c++17','-Wall','-Wextra','-Werror','-pedantic','-O1','-g']
            if PROFILE=='sanitized':flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
            argv=[args.compiler,*flags,str(ROOT/'file_driver.cpp'),str(ROOT/'file_allocation_probe.cpp'),'-o',str(BIN)]
            command(argv,d/'compile',env)
            with (d/'tests.log').open('w') as stream:
                result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FileTests))
            summary['profiles'].append({'name':PROFILE,'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
               'leakSanitizer':'unavailable-on-Apple' if sys.platform=='darwin' else 'enabled-in-sanitized'})
            need(result.wasSuccessful() and not result.skipped,'Tests failed; preserve '+str(d/'tests.log'))
        summary['passed']=True
    finally:
        summary['caseContracts']=len(GOOD)+len(FAULTS);summary['compilerProcessRecords']=len(RECORDS)
        summary['sourceUnchanged']=all(sha((repo/r['path']).read_bytes())==r['sha256'] for r in sources)
        summary['records']=RECORDS;summary['cases']=CASES;write_json(OUT/'RESULT.json',summary)
        files=[]
        for f in sorted(OUT.rglob('*')):
            if f.is_symlink():
                link=os.readlink(f)
                files.append({'path':str(f.relative_to(OUT)),'kind':'symlink','target':link,'sha256':sha(os.fsencode(link))})
            elif f.is_file():
                files.append({'path':str(f.relative_to(OUT)),'kind':'file','bytes':f.stat().st_size,'sha256':sha(f.read_bytes())})
        write_json(OUT/'MANIFEST.json',{'files':files})
    print(json.dumps({k:summary[k] for k in ('passed','caseContracts','compilerProcessRecords','profiles','sourceUnchanged')},indent=2))
if __name__=='__main__':main()
