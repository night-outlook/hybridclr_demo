from pathlib import Path
import json,subprocess,datetime,hashlib,shutil
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';P=B/'Preflight-R03-P1-ADMITTED-EXECUTION-20261023-6c72';O=B/'R03-P1-ADMITTED-EXECUTION-20261023-6c72';S=B/'Scratch-R03-P1-ADMITTED-EXECUTION-20261023-6c72';K='Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-admitted-execution-20261023-6c72'
pin='7a098e45b41b98ee024ed0205b353aa2f132aae9';U='/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity';records=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def run(name,argv,directory):
 out=directory/(name+'.stdout.bin');err=directory/(name+'.stderr.bin');start=now()
 with out.open('xb') as a,err.open('xb') as b:
  child=subprocess.Popen(argv,cwd=D,stdout=a,stderr=b);pid=child.pid;code=child.wait()
 r=dict(argv=argv,cwd=str(D),start=start,end=now(),pid=pid,exit=code,stdout=str(out),stdoutSha256=sha(out),stderr=str(err),stderrSha256=sha(err))
 records.append(r);(B/'Dispatch-R03-P1-ADMITTED-EXECUTION-20261023-6c72.json').write_text(json.dumps(dict(commands=records),indent=2)+'\n')
 print(name,code,flush=True);return code
ad=json.loads((B/'Admission-R03-P1-ADMITTED-EXECUTION-20261023-6c72.json').read_text());assert ad['EXPECTED.json']['pins']['hybridclr_demo']==pin
for q in [P,O,S,D/K]:assert not q.exists() and not q.is_symlink()
tests=D/'Docs/AssemblyShadow/Handoff/Tools/test_prepare_p1_admitted_local.py';prep=D/'Docs/AssemblyShadow/Handoff/Tools/prepare_p1_admitted_local.py'
code=run('6c72-preparer-tests',['python3','-B',str(tests)],B);assert code==0
code=run('6c72-preparation',['python3','-B',str(prep),'--workspace',str(W),'--demo-sha',pin,'--unity',U,'--preflight',str(P),'--output',str(O),'--scratch',str(S),'--checkpoint',K],B);assert code==0
assert {q.name for q in P.iterdir()}=={'EXPECTED.json','PREPARATION.json','run-once.py','audit.py'}
rec=json.loads((P/'PREPARATION.json').read_text());assert rec['result']=='PreparedNotExecuted' and rec['coreInvoked'] is False and rec['pins']==ad['EXPECTED.json']['pins'] and sha(P/'run-once.py')==rec['correctedCollectorSha256'] and sha(P/'audit.py')==rec['independentAuditSha256']
assert json.loads((P/'EXPECTED.json').read_text())==ad['EXPECTED.json']
for n,v in ad.items():
 if n=='EXPECTED.json':continue
 assert not (P/n).exists();(P/n).write_text(json.dumps(v,indent=2)+'\n')
for name in ['6c72-preparer-tests.stdout.bin','6c72-preparer-tests.stderr.bin','6c72-preparation.stdout.bin','6c72-preparation.stderr.bin']:
 shutil.copyfile(B/name,P/name)
(P/'PREPARER_COMMANDS.json').write_text(json.dumps(records,indent=2)+'\n')
# The shipped, hash-bound collector is invoked once only. Its own command receipt binds core PID/times.
with (P/'run-once.log').open('xb') as output:
 start=now();child=subprocess.Popen(['python3','-B',str(P/'run-once.py')],cwd=D,stdout=output,stderr=subprocess.STDOUT);pid=child.pid;code=child.wait()
(P/'COLLECTOR_RECEIPT.json').write_text(json.dumps(dict(argv=['python3','-B',str(P/'run-once.py')],cwd=str(D),start=start,end=now(),pid=pid,exit=code,combinedLog=str(P/'run-once.log'),combinedLogSha256=sha(P/'run-once.log'),preparedCollectorSha256=rec['correctedCollectorSha256'],coreRetried=False),indent=2)+'\n')
print('collector',code,flush=True)
