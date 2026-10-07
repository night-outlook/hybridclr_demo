from pathlib import Path
import subprocess,os,json,datetime,time,hashlib
P=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261007R-lq-storage-2');W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';BASE=P.parent;B=BASE/'R03LocalBatch-20261007R-lq-storage';CHECK=BASE/'StorageCheck-R03LocalBatch-20261007R-lq-storage-2';STORAGE=BASE/'Storage-R03LocalBatch-20261007R-lq-storage';PIN='ba57a3391da9627e694ee33f8bfe3cb993e6c56a';authority=json.loads((P/'SOURCE_AUTHORITY.json').read_text());SDK='/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk';env={**os.environ,'EXPECTED_DEMO_COMMIT':PIN,'GIT_SSH_COMMAND':authority['sshCommand'],'DOTNET_ROOT':SDK,'DOTNET_ROOT_ARM64':SDK,'PATH':SDK+':'+os.environ['PATH'],'DOTNET_MULTILEVEL_LOOKUP':'0','TMPDIR':'/private/tmp','PYTHONDONTWRITEBYTECODE':'1'}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert not B.exists() and not STORAGE.exists() and not (P/'runner-invocation.json').exists();assert json.loads((CHECK/'admission.json').read_text())['state']=='Admitted';assert json.loads((CHECK/'session.json').read_text())['state']=='Passed';assert len(json.loads((CHECK/'admission.json').read_text())['probes'])==10
pre=[]
for name,pin in authority['repositories'].items():
 repo=W/name;head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD']).decode().strip();status=subprocess.check_output(['git','-C',str(repo),'status','--porcelain=v1','--untracked-files=all']).decode();r=subprocess.run(['git','-C',str(repo),'ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1'],env=env,capture_output=True,text=True,check=True);assert head==pin and not status and r.stdout.split()==[pin,'refs/heads/codex/assembly-shadow-r01b-h1'];pre.append({'path':str(repo),'head':head,'status':status,'remoteHead':pin,'remoteVerified':True})
argv=['/Library/Frameworks/Python.framework/Versions/3.14/bin/python3','-B',str(D/'Tools/AssemblyShadow/R03Storage/run_storage_checked.py'),'--workspace',str(W),'--output',str(B),'--unity','/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity','--demo-commit',PIN,'--retained-q',str(BASE/'R03LocalBatch-20261006Q-lp-repair'),'--storage-evidence',str(STORAGE),'--execute']
receipt={'argv':argv,'cwd':str(D),'startedUtc':utc(),'startedEpoch':time.time(),'environment':{k:env[k] for k in ['PATH','EXPECTED_DEMO_COMMIT','DOTNET_ROOT','DOTNET_ROOT_ARM64','DOTNET_MULTILEVEL_LOOKUP','TMPDIR','PYTHONDONTWRITEBYTECODE']},'repositories':pre,'executingInvocations':1,'diagnosticSidecar':str(CHECK),'diagnosticAdmissionSha256':digest(CHECK/'admission.json'),'diagnosticSessionSha256':digest(CHECK/'session.json'),'newExecutingSidecar':str(STORAGE),'newBatchRoot':str(B),'coreInvokedDirectly':False,'sourceExceptionAuthorizationPath':str(P/'USER_SOURCE_AUTHORIZATION.json')}
with (P/'runner-stdout.log').open('xb') as out,(P/'runner-stderr.log').open('xb') as err:
 process=subprocess.Popen(argv,cwd=D,env=env,stdout=out,stderr=err);receipt['pid']=process.pid
 with (P/'runner-invocation.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
 print('Executing wrapper started',process.pid,receipt['startedUtc'],flush=True);code=process.wait()
receipt.update({'exitCode':code,'endedUtc':utc(),'endedEpoch':time.time(),'stdoutSha256':digest(P/'runner-stdout.log'),'stderrSha256':digest(P/'runner-stderr.log')})
with (P/'runner-exit.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print('Executing wrapper exited',code,receipt['endedUtc'],flush=True)
