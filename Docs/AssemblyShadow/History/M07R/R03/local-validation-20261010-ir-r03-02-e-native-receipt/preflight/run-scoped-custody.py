from pathlib import Path
import subprocess,json,datetime,hashlib,sys,os
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261010E-native-receipt');DOC=D/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-c-custody-blocked';phase=sys.argv[1]
assert phase in ['before','after'];root=P/'commands'/('scoped-custody-'+phase);root.mkdir(parents=True);args=['/Library/Frameworks/Python.framework/Versions/3.14/bin/python3','-B',str(DOC/'verify_scoped_custody.py'),'--checkpoint',str(C),'--phase',phase,'--receipt',str(P/('scoped-custody-'+phase+'.json'))]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(f):
 with Path(f).open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
start=now()
with (root/'stdout.log').open('xb') as out,(root/'stderr.log').open('xb') as err:v=subprocess.run(args,cwd=D,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),stdout=out,stderr=err,timeout=600)
r={'argv':args,'cwd':str(D),'sourceCommit':'baa9473200e453d1ba1017610e776e6c18c8d7f1','sourceSha256':sha(DOC/'verify_scoped_custody.py'),'startUtc':start,'endUtc':now(),'exitCode':v.returncode,'stdoutPath':str(root/'stdout.log'),'stdoutSha256':sha(root/'stdout.log'),'stderrPath':str(root/'stderr.log'),'stderrSha256':sha(root/'stderr.log'),'receiptPath':str(P/('scoped-custody-'+phase+'.json')),'receiptSha256':sha(P/('scoped-custody-'+phase+'.json')),'unityLaunched':False}
(root/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'command':r,'scopedResult':json.loads((P/('scoped-custody-'+phase+'.json')).read_text())}));sys.exit(v.returncode)
