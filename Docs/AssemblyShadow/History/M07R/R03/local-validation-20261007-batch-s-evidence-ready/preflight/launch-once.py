"""Single fresh storage-checked S invocation; prerequisites must already be Passed."""
from pathlib import Path
import subprocess,os,json,datetime,hashlib
P=Path(__file__).resolve().parent;BASE=P.parent;W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';B=BASE/'R03LocalBatch-20261007S-lr-recovery';S=BASE/'Storage-R03LocalBatch-20261007S-lr-recovery-2';PY='/Library/Frameworks/Python.framework/Versions/3.14/bin/python3';SDK=Path('/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk');UNITY='/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity';auth=json.loads((P/'SOURCE_AUTHORITY.json').read_text());PIN=auth['repositories']['hybridclr_demo'];env={**os.environ,'EXPECTED_DEMO_COMMIT':PIN,'DOTNET_ROOT':str(SDK),'DOTNET_ROOT_ARM64':str(SDK),'DOTNET_MULTILEVEL_LOOKUP':'0','PATH':str(SDK)+os.pathsep+os.environ['PATH'],'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':'/private/tmp','GIT_SSH_COMMAND':auth['sshCommand'],'GIT_TERMINAL_PROMPT':'0'}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert json.loads((P/'PREREQUISITE_SEQUENCE.json').read_text())['state']=='PrerequisitesReady';assert json.loads((P/'HISTORICAL_CUSTODY_BEFORE.json').read_text())['state']=='Passed';assert not B.exists() and not B.is_symlink() and not S.exists() and not S.is_symlink();ps=subprocess.check_output(['ps','-axo','args='],text=True);assert not any(UNITY in line and '-projectPath' in line and (str(W) in line or str(B) in line or 'R03LocalBatch-20261007R-lq-storage' in line) for line in ps.splitlines())
argv=[PY,'-B',str(D/'Tools/AssemblyShadow/R03Storage/run_storage_checked.py'),'--workspace',str(W),'--output',str(B),'--unity',UNITY,'--demo-commit',PIN,'--retained-q',str(BASE/'R03LocalBatch-20261006Q-lp-repair'),'--storage-evidence',str(S),'--execute'];folder=P/'operations/storage-executing';folder.mkdir(parents=True);start=utc()
with (P/'SINGLE_EXECUTION_INTENT.json').open('x') as f:json.dump({'kind':'SingleAuthorizedFreshSInvocation','startUtc':start,'argv':argv,'demoCommit':PIN,'batchRootInitiallyAbsent':True,'sidecarInitiallyAbsent':True,'maximumInvocations':1,'noPhaseRetry':True,'productionTimeoutsUnchanged':True,'oldSBlockedEvidencePreserved':True},f,indent=2);f.write('\n')
print('Launching one storage-checked S invocation',start,flush=True)
with (folder/'stdout.log').open('xb') as out,(folder/'stderr.log').open('xb') as err:r=subprocess.run(argv,cwd=D,env=env,stdout=out,stderr=err)
row={'kind':'SingleStorageCheckedSCommand','argv':argv,'cwd':str(D),'startUtc':start,'endUtc':utc(),'exitCode':r.returncode,'stdoutSha256':sha(folder/'stdout.log'),'stderrSha256':sha(folder/'stderr.log'),'batchRootExists':B.exists(),'sidecarExists':S.exists(),'runtimeAcceptance':False}
with (folder/'receipt.json').open('x') as f:json.dump(row,f,indent=2);f.write('\n')
print('S invocation finished exit',r.returncode,'batchRootExists',B.exists(),flush=True)
raise SystemExit(r.returncode)
