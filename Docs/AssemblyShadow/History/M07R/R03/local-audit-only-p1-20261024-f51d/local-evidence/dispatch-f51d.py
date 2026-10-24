from pathlib import Path
import subprocess,json,hashlib,datetime,os
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');ad=json.loads((B/'f51d-ADMISSION_BEFORE.json').read_text());W=Path(ad['workspace']);D=W/'hybridclr_demo';T=D/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/P1_HISTORICAL_AUDIT_HELPER_2026-10-24';P=Path(ad['originalPreflight']);O=Path(ad['raw']);A=Path(ad['stage']);records=[]
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,argv):
 so=B/('f51d-'+name+'.stdout.bin');se=B/('f51d-'+name+'.stderr.bin');start=now()
 with so.open('xb') as f,se.open('xb') as g:
  child=subprocess.Popen(argv,cwd=D,stdout=f,stderr=g);pid=child.pid;code=child.wait()
 r=dict(name=name,argv=argv,cwd=str(D),start=start,end=now(),pid=pid,exit=code,TMPDIR=os.environ.get('TMPDIR'),CXX=os.environ.get('CXX'),stdout=str(so),stdoutSha256=sha(so),stderr=str(se),stderrSha256=sha(se))
 records.append(r);(B/'f51d-DISPATCH.json').write_text(json.dumps(dict(commands=records),indent=2)+'\n');print(name,code,flush=True);return code
assert not A.exists() and not Path(ad['checkpoint']).exists()
tests=[]
for label,path,count in [('identity-tests',T/'test_historical_helper_identity.py',17),('staging-tests',T/'test_helper_audit_staging.py',11),('retained-tests',D/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/P1_B7E3_AUDIT_ONLY_2026-10-23/test_audit_only_source.py',23)]:
 code=run(label,['python3','-B',str(path)]);tests.append(code);assert code==0
 stderr=(B/('f51d-'+label+'.stderr.bin')).read_text();assert ('Ran '+str(count)+' tests') in stderr and stderr.rstrip().endswith('OK')
test=0
stage=run('stage',['python3','-B',str(T/'stage_helper_successor.py'),'--workspace',str(W),'--preflight',str(P),'--raw',str(O),'--stage',str(A)]);assert stage==0
s=json.loads((A/'AUDIT_ONLY_STAGE.json').read_text());printed=json.loads((B/'f51d-stage.stdout.bin').read_text())
assert s['initialSnapshot']['consumedC42A']['publishedFilesVerified']==197 and s['status']=='StagedNotExecuted' and s['initialSnapshot']['sdkScratch']['checkedScratchFiles']==printed['sdkScratchFiles']==1925 and s['initialSnapshot']['raw']['regularFiles']==4269 and s['initialSnapshot']['sdk']['files']==2405
code=run('historical-audit',['python3','-B',str(T/'run_helper_audit_once.py'),'--stage',str(A),'--timeout-seconds','1800'])
# No retry; preserve known failure too. Unknown lifetime is recorded by shipped runner.
after=run('verify-after',['python3','-B',str(T/'stage_helper_successor.py'),'--verify-after','--workspace',str(W),'--preflight',str(P),'--raw',str(O),'--stage',str(A)])
(B/'f51d-DISPATCH_RESULT.json').write_text(json.dumps(dict(sourceTestsExit=test,stageExit=stage,auditRunnerExit=code,verifyAfterExit=after,coreOrCompilersInvoked=False,retried=False),indent=2)+'\n')
print('Single audit-only dispatch finished',flush=True)
