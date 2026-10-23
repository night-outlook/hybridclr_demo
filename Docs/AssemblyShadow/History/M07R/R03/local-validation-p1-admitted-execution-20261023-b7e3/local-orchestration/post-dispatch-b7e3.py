from pathlib import Path
import json,subprocess,hashlib,datetime,os
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');P=B/'Preflight-R03-P1-ADMITTED-EXECUTION-20261023-b7e3';E=json.loads((P/'EXPECTED.json').read_text());D=Path(E['workspace'])/'hybridclr_demo';O=Path(E['output'])
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,argv,log):
 receipt=P/(name+'.json');assert not receipt.exists() and not log.exists()
 t=now()
 with log.open('xb') as f:
  c=subprocess.Popen(argv,cwd=D,stdout=f,stderr=subprocess.STDOUT);pid=c.pid;code=c.wait()
 receipt.write_text(json.dumps(dict(argv=argv,cwd=str(D),start=t,end=now(),pid=pid,exit=code,log=str(log),logSha256=sha(log),TMPDIR=os.environ.get('TMPDIR'),CXX=os.environ.get('CXX')),indent=2)+'\n')
 print(name,code,flush=True);return code
r=json.loads((O/'RESULT.json').read_text());m=json.loads((O/'MANIFEST.json').read_text());prep=json.loads((P/'PREPARATION.json').read_text())
assert sha(P/'run-once.py')==prep['correctedCollectorSha256'] and sha(P/'audit.py')==prep['independentAuditSha256']
known=r['result']=='PassedSourceHostAndSDKOnly' and len(r['commands'])==25 and all(c['status']=='Passed' and c['exit']==0 and c['commandLifetimeUnverified'] is False for c in r['commands']) and r['sourcePreserved'] is True and r['commandLifetimeUnverified'] is False and m['commandLifetimeUnverified'] is False and m['inventoryScope']=='CompletedBatchFiles' and r['postflightGitDiagnostics']['actualDirectCommandCount']==20 and r['postflightGitDiagnostics']['completedRepositoryCount']==4 and r['postflightGitDiagnostics']['timedOutCommands']==0
if known:
 for row in m['files']:p=O/row['path'];assert p.stat().st_size==row['size'] and sha(p)==row['sha256']
 acode=run('AUDITOR_COMMAND',['python3','-B',str(P/'audit.py')],P/'audit.log')
else:
 acode=None;(P/'AUDITOR_NOTRUN.json').write_text(json.dumps(dict(status='NotRun',reason='Raw aggregate/receipts not known-complete scoped PASS',rawResult=r['result']),indent=2)+'\n')
vcode=run('VERIFY_AFTER_COMMAND',['python3','-B',str(D/'Docs/AssemblyShadow/Handoff/Tools/prepare_p1_admitted_local.py'),'--verify-after','--workspace',E['workspace'],'--preflight',str(P)],P/'verify-after.log')
# Independent complete historical checks, separate from success-assuming audit and preparer verification.
if r['commandLifetimeUnverified'] is False:
 pcode=run('PRESERVATION_COMMAND',['python3','-B',str(B/'post-preservation-b7e3.py')],P/'independent-preservation.log')
else:
 pcode=None;(P/'PRESERVATION_NOTRUN.json').write_text(json.dumps(dict(reason='Unknown batch command lifetime; no subsequent independent subprocess started',status='NotRun'),indent=2)+'\n')
(P/'LOCAL_POSTPHASE_RESULT.json').write_text(json.dumps(dict(rawAggregate=r['result'],knownCompleteBeforeAudit=known,unchangedAuditExit=acode,preparerVerifyAfterExit=vcode,independentPreservationExit=pcode,sourceCollectorAndAuditNotEdited=True,coreRetried=False),indent=2)+'\n')
