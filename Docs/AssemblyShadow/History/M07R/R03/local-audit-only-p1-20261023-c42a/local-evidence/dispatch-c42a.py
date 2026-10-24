from pathlib import Path
import subprocess,json,hashlib,datetime,os
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');ad=json.loads((B/'c42a-ADMISSION_BEFORE.json').read_text());W=Path(ad['workspace']);D=W/'hybridclr_demo';T=D/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/P1_B7E3_AUDIT_ONLY_2026-10-23';P=Path(ad['originalPreflight']);O=Path(ad['raw']);A=Path(ad['stage']);records=[]
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,argv):
 so=B/('c42a-'+name+'.stdout.bin');se=B/('c42a-'+name+'.stderr.bin');start=now()
 with so.open('xb') as f,se.open('xb') as g:
  child=subprocess.Popen(argv,cwd=D,stdout=f,stderr=g);pid=child.pid;code=child.wait()
 r=dict(name=name,argv=argv,cwd=str(D),start=start,end=now(),pid=pid,exit=code,TMPDIR=os.environ.get('TMPDIR'),CXX=os.environ.get('CXX'),stdout=str(so),stdoutSha256=sha(so),stderr=str(se),stderrSha256=sha(se))
 records.append(r);(B/'c42a-DISPATCH.json').write_text(json.dumps(dict(commands=records),indent=2)+'\n');print(name,code,flush=True);return code
assert not A.exists() and not Path(ad['checkpoint']).exists()
test=run('source-tests',['python3','-B',str(T/'test_audit_only_source.py')]);assert test==0
stderr=(B/'c42a-source-tests.stderr.bin').read_text();assert 'Ran 23 tests' in stderr and stderr.rstrip().endswith('OK')
stage=run('stage',['python3','-B',str(T/'stage_local_audit_only.py'),'--workspace',str(W),'--preflight',str(P),'--raw',str(O),'--stage',str(A)]);assert stage==0
s=json.loads((A/'AUDIT_ONLY_STAGE.json').read_text());printed=json.loads((B/'c42a-stage.stdout.bin').read_text())
assert s['status']=='StagedNotExecuted' and s['initialSnapshot']['sdkScratch']['checkedScratchFiles']==printed['sdkScratchFiles']==1925 and s['initialSnapshot']['raw']['regularFiles']==4269 and s['initialSnapshot']['sdk']['files']==2405
code=run('historical-audit',['python3','-B',str(T/'run_local_audit_once.py'),'--stage',str(A),'--timeout-seconds','1800'])
# No retry; preserve known failure too. Unknown lifetime is recorded by shipped runner.
after=run('verify-after',['python3','-B',str(T/'stage_local_audit_only.py'),'--verify-after','--workspace',str(W),'--preflight',str(P),'--raw',str(O),'--stage',str(A)])
(B/'c42a-DISPATCH_RESULT.json').write_text(json.dumps(dict(sourceTestsExit=test,stageExit=stage,auditRunnerExit=code,verifyAfterExit=after,coreOrCompilersInvoked=False,retried=False),indent=2)+'\n')
print('Single audit-only dispatch finished',flush=True)
