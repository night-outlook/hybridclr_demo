#!/usr/bin/env python3
"""Run design-reference controls only. No Unity, repository mutation or live custody scan."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

SOURCES = ('diagnostic_stream.py','test_diagnostic_stream.py',
           'terminal_boundary.h','test_terminal_boundary.cpp','run_checks.py')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); here=Path(__file__).resolve().parent; out=a.output
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    if (not out.is_absolute() or out!=out.resolve(strict=False) or out.exists()
        or out.is_symlink() or not out.parent.is_dir() or here in out.parents
        or out in here.parents or out==here):raise RuntimeError('Unused external canonical output required')
    compiler=shutil.which('clang++') or shutil.which('c++')
    if not compiler:raise RuntimeError('C++17 compiler missing')
    before={name:hashlib.sha256((here/name).read_bytes()).hexdigest() for name in SOURCES}
    out.mkdir(); records=[]; passed=False
    def call(name,argv):
        start=dt.datetime.now(dt.timezone.utc).isoformat()
        result=subprocess.run(argv,cwd=here,capture_output=True,timeout=90,
            env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
        (out/(name+'.stdout')).write_bytes(result.stdout)
        (out/(name+'.stderr')).write_bytes(result.stderr)
        records.append(dict(name=name,argv=argv,cwd=str(here),startUtc=start,
            endUtc=dt.datetime.now(dt.timezone.utc).isoformat(),exit=result.returncode,
            stdoutSha256=hashlib.sha256(result.stdout).hexdigest(),
            stderrSha256=hashlib.sha256(result.stderr).hexdigest()))
        if result.returncode:raise RuntimeError(name+' failed; retain logs')
        return result
    try:
        result=call('codec',[sys.executable,'-B','-m','unittest','test_diagnostic_stream','-v'])
        if b'Ran 36 tests' not in result.stderr or b'\nOK\n' not in result.stderr:
            raise RuntimeError('Exact codec suite did not run')
        for profile,extra in [('strict',[]),('sanitized',['-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
            exe=out/('terminal-'+profile)
            call(profile+'-compile',[compiler,'-std=c++17','-Wall','-Wextra','-Werror','-pedantic',
                '-pthread',*extra,str(here/'test_terminal_boundary.cpp'),'-o',str(exe)])
            r=call(profile+'-run',[str(exe)])
            obj=json.loads(r.stdout)
            if obj!={'scenarios':21,'passed':True,'engineAdapterInstalled':False}:
                raise RuntimeError('Unexpected native contract result')
        passed=True
    finally:
        after={name:hashlib.sha256((here/name).read_bytes()).hexdigest() for name in SOURCES}
        report=dict(kind='SNAP01DesignContractChecks',result='PassedWithinReferenceScope' if passed and before==after else 'FailedOrIncomplete',
            pythonTests=36,nativeScenariosPerProfile=21,profiles=['strict','ASan/UBSan'],
            compiler=compiler,commands=records,sourceSha256=before,sourceUnchanged=before==after,
            actualUnity=False,actualNativeSchedulerAdapter=False,actualGC=False,
            productionTransportInstalled=False,semanticAcceptance=False,historicalCustodyChanged=False)
        (out/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
        files=[dict(path=str(x.relative_to(out)),bytes=x.stat().st_size,
            sha256=hashlib.sha256(x.read_bytes()).hexdigest()) for x in sorted(out.iterdir()) if x.is_file()]
        (out/'MANIFEST.json').write_text(json.dumps({'files':files},indent=2)+'\n')
    if not passed or before!=after:raise RuntimeError('Incomplete tests or source mutation')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
