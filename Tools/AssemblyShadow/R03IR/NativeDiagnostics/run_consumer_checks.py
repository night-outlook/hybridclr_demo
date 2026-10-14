#!/usr/bin/env python3
"""Source-bound host consumer tests, including actual native codec to verifier.
No Unity/IL2CPP process, production producer, scheduler or protected files used.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
IR=HERE.parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(IR))
import bounded_snapshot as consumer
from NativeDiagnostics import diagnostic_wire as wire
import test_terminal_contract as prior
from test_bounded_consumer import PINS


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output
    if not __debug__:raise RuntimeError('Assertions must not be disabled')
    if not out.is_absolute() or out!=out.resolve(strict=False) or out.exists() or not out.parent.is_dir():
        raise RuntimeError('Fresh canonical external output required')
    if out==ROOT or ROOT in out.parents or out in ROOT.parents:raise RuntimeError('External output required')
    compiler=shutil.which(os.environ.get('CXX','clang++'))
    if not compiler:raise RuntimeError('Clang or explicit CXX required')
    files=[IR/'bounded_snapshot.py',IR/'run_terminal_local.py',IR/'test_terminal_contract.py',
           HERE/'diagnostic_wire.py',HERE/'test_bounded_consumer.py',Path(__file__).resolve(),
           HERE/'native_codec_driver.cpp',HERE/'BoundedDiagnosticsV2.h']
    before={str(p.relative_to(ROOT)):consumer.digest(p.read_bytes()) for p in files}
    out.mkdir();(out/'commands').mkdir();(out/'cases').mkdir()
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1',
         'ASAN_OPTIONS':f'detect_leaks={int(sys.platform!="darwin")}:abort_on_error=1',
         'UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'}
    records=[];observations=[];status='FailedOrIncomplete'
    suites={k:{'result':'NotRun','requiredCount':n,'passedCount':None} for k,n in
            (('consumer',56),('originalIR',93),('originalR03',203))}
    def run(argv,expected=0,stdin=None,fds=()):
        start=time.monotonic()
        try:
            r=subprocess.run([str(a) for a in argv],cwd=ROOT,env=env,
                input=stdin,pass_fds=fds,capture_output=True,timeout=180)
        except subprocess.TimeoutExpired as exc:
            row={'argv':[str(a) for a in argv],'cwd':str(ROOT),'exit':None,
                 'expectedExit':expected,'timedOut':True,'seconds':time.monotonic()-start}
            for name,data in [('stdout',exc.stdout or b''),('stderr',exc.stderr or b'')]:
                dest=out/'commands'/f'{len(records):03d}.{name}';dest.write_bytes(data)
                row[name]={'path':str(dest.relative_to(out)),'bytes':len(data),'sha256':consumer.digest(data)}
            records.append(row)
            raise RuntimeError(f'Command {len(records)-1} timed out; original output retained') from exc
        row={'argv':[str(a) for a in argv],'cwd':str(ROOT),'exit':r.returncode,
             'expectedExit':expected,'seconds':time.monotonic()-start}
        for name,data in [('stdout',r.stdout),('stderr',r.stderr)]:
            dest=out/'commands'/f'{len(records):03d}.{name}';dest.write_bytes(data)
            row[name]={'path':str(dest.relative_to(out)),'bytes':len(data),'sha256':consumer.digest(data)}
        records.append(row)
        if r.returncode!=expected:raise RuntimeError(f'Command {len(records)-1}: {r.returncode} != {expected}; see preserved logs')
        return r
    try:
        suites['consumer']['result']='RunningOrFailed'
        result=run([sys.executable,'-B',HERE/'test_bounded_consumer.py'])
        if b'Ran 56 tests' not in result.stderr or b'\nOK\n' not in result.stderr:
            raise RuntimeError('56 complete consumer regressions required')
        suites['consumer'].update(result='Passed',passedCount=56)
        suites['originalIR']['result']='RunningOrFailed'
        result=run([sys.executable,'-B','-m','unittest','discover','-s',IR,'-p','test_*.py','-v'])
        if b'Ran 93 tests' not in result.stderr or b'\nOK\n' not in result.stderr:
            raise RuntimeError('93 original IR regressions required')
        suites['originalIR'].update(result='Passed',passedCount=93)
        suites['originalR03']['result']='RunningOrFailed'
        result=run([sys.executable,'-B','-m','unittest','discover','-s',IR.parent/'R03','-p','test_*.py','-v'])
        if b'Ran 203 tests' not in result.stderr or b'\nOK\n' not in result.stderr:
            raise RuntimeError('203 original R03 regressions required')
        suites['originalR03'].update(result='Passed',passedCount=203)
        for profile in ('strict','sanitized'):
            flags=['-O2'] if profile=='strict' else ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
            binary=out/('codec-'+profile)
            run([compiler,'-std=c++17','-Wall','-Wextra','-Werror','-pedantic',*flags,HERE/'native_codec_driver.cpp','-o',binary])
            for scenario in ('baseline','type','off','large','unicode','failed-semantic'):
                p=out/'cases'/f'{profile}-{scenario}';p.mkdir(mode=0o700)
                fixture=prior.TerminalReceiptContractTests();fixture.setUp()
                raw=copy.deepcopy(fixture.raw);request=copy.deepcopy(fixture.request)
                launch={**fixture.launch,'exitCode':0};build=fixture.build_sha
                if scenario=='type':
                    request['stimulus']=raw['stimulus']='type-resolution'
                    request['caseId']=raw['caseId']='IR-R03-02-release-type'
                    raw['firstRecovery']=raw['finalRecovery']=json.dumps({'published':True,'stateCode':9,
                        'terminalFailureCode':13,'disposition':'RestartRequired'})
                if scenario=='off':
                    request['stimulus']=raw['stimulus']='off';request['caseId']=raw['caseId']='IR-R03-02-off'
                    raw.update(initialState=0,finalState=0,prePositive=True,preCanaryCount=1,finalCanaryCount=2,
                        activeReflectionAttempted=False,activeDelegateAttempted=False,aotReflectionAttempted=False,
                        terminalReportingProbeMask=0,reserveGcProbeMask=0)
                if scenario=='failed-semantic':raw['result']='Failed'
                raw['reportTransport']='NativeBoundedSnapshotV2'
                request_text=json.dumps(request,indent=2)+'\n'
                identity={'runId':request['runId'],'caseId':request['caseId'],'processId':launch['pid'],
                    'requestSha256':consumer.digest(request_text.encode()),'buildSha256':build,
                    'demoCommit':PINS['hybridclr_demo'],'hybridclrCommit':PINS['hybridclr'],
                    'packageCommit':PINS['hybridclr_unity'],'nativeCommit':PINS['il2cpp_plus']}
                raw['requestSha256']=identity['requestSha256']
                fields={'finalDiagnostics':'{"allClasses":[]}','finalExecutionDiagnostics':'{}'}
                if scenario=='large':fields={k:json.dumps({'content':'x'*600000}) for k in wire.FIELDS}
                if scenario=='unicode':fields['finalDiagnostics']='{"text":"'+'z'*65524+'😀漢字€'+'b'*70000+'"}'
                expected,desc=wire.encode(identity,raw,fields)
                field_paths=[]
                for i,field in enumerate(wire.FIELDS):
                    name=p/f'input-{i}.utf8';name.write_bytes(fields[field].encode());field_paths.append(name)
                meta=json.loads(run([binary,'encode',wire.binding(identity).hex(),consumer.digest(wire.inline_bytes(raw)),
                    len(wire.inline_bytes(raw)),*field_paths,p/'diagnostics.v2',4093]).stdout)
                data=(p/'diagnostics.v2').read_bytes()
                if data!=expected or meta['sha256']!=desc['sha256'] or meta['maxWrite']>wire.CHUNK:
                    raise RuntimeError('Actual native codec/reference mismatch')
                os.chmod(p/'diagnostics.v2',0o600)
                raw['diagnosticArtifact']=desc
                (p/'raw.json').write_bytes(wire.canonical(raw));os.chmod(p/'raw.json',0o600)
                fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY)
                try:
                    authority={'kind':'R03BoundedPairAuthorityV2','directory':consumer.stamp(os.fstat(fd),consumer.DIR_KEYS)}
                    for key,name in [('raw','raw.json'),('artifact','diagnostics.v2')]:
                        f=p/name;authority[key]={'stat':consumer.stamp(f.stat()),'sha256':consumer.digest(f.read_bytes())}
                    body=wire.canonical({'authority':authority,'requestText':request_text,'launch':launch,'buildSha256':build,'pins':PINS})
                    response=run([sys.executable,'-I','-B',IR/'bounded_snapshot.py','--worker',fd],
                                 2 if scenario=='failed-semantic' else 0,stdin=body,fds=(fd,))
                    if scenario!='failed-semantic':
                        accepted=json.loads(response.stdout)
                        if accepted['transport']!='NativeBoundedSnapshotV2' or accepted['runtimeAcceptance'] is not False:
                            raise RuntimeError('Tagged semantic receipt contract')
                        for key,val in fields.items():
                            if accepted['fields'][key]['sha256']!=consumer.digest(val.encode()):raise RuntimeError('Full bytes not retained')
                    observations.append({'profile':profile,'scenario':scenario,'nativeBytes':len(data),
                        'nativeSha256':consumer.digest(data),'workerExit':response.returncode,
                        'completeSyntheticSemanticResult':scenario!='failed-semantic','runtimeAcceptance':False})
                finally:os.close(fd)
        if any(consumer.digest((ROOT/k).read_bytes())!=v for k,v in before.items()):raise RuntimeError('Source changed')
        status='PassedWithinHostConsumerScope'
    finally:
        unchanged=all((ROOT/k).is_file() and consumer.digest((ROOT/k).read_bytes())==v for k,v in before.items())
        if not unchanged:status='FailedOrIncomplete'
        for suite in suites.values():
            if suite['result']=='RunningOrFailed':suite['result']='FailedOrIncomplete'
        result={'kind':'R03BoundedConsumerSourceCheck','result':status,'suites':suites,
                'sourceUnchanged':unchanged,'nativeIntegrationScenarios':observations,'commands':records,
                'sourceSha256':before,'artifactBytesBound':wire.MAX_STREAM,'envelopeBytesBound':wire.RESERVE,
                'frameBytesBound':wire.CHUNK,'pooledBytesBound':wire.TOTAL,'notUnity':True,
                'actualProducerIntegrated':False,'engineAdapterImplemented':False,'runtimeAcceptance':False,
                'darwinLeakDetection':'Unavailable in Apple ASan' if sys.platform=='darwin' else 'Enabled',
                'sanitizerEnvironment':{k:env[k] for k in ('ASAN_OPTIONS','UBSAN_OPTIONS')}}
        (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
        inventory=[{'path':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':consumer.digest(p.read_bytes())}
                   for p in sorted(out.rglob('*')) if p.is_file() and not p.is_symlink()]
        (out/'MANIFEST.json').write_text(json.dumps({'files':inventory},indent=2)+'\n')
    print(json.dumps({'result':status,'commands':len(records),'nativeScenarios':len(observations)}))

if __name__=='__main__':main()
