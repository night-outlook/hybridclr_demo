from pathlib import Path
import json,subprocess,os,datetime,hashlib,sys,shlex
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261010E-native-receipt');B=P.parent/'R03IRLocal-20261010E-native-receipt';mode=sys.argv[1];assert mode in ['diagnostic','execute'];source='baa9473200e453d1ba1017610e776e6c18c8d7f1'
for n in ['LOCAL_HOST_PREFLIGHT.json','CI_EQUIVALENCE_VERIFICATION.json','CUSTODY_CI_EQUIVALENCE.json','ORIGINAL_INPUT_PREFLIGHT.json']:assert json.loads((P/n).read_text())['state']=='Passed'
before=json.loads((P/'scoped-custody-before.json').read_text());assert before['result']=='ScopedHistoricalLossStable' and before['originalStrictCustody']=='Blocked' and before['completeScan'] and not before['problems'] and before['presentVerified']==339367 and before['historicalStillMissing']==77477
assert not B.exists()
if mode=='execute':
 check=P.parent/'StorageCheck-R03IRLocal-20261010E-native-receipt';assert json.loads((P/'commands/storage-diagnostic/receipt.json').read_text())['exitCode']==0;assert json.loads((check/'admission.json').read_text())['state']=='Admitted';assert not json.loads((check/'dispatch.json').read_text())['batchStarted'];assert json.loads((check/'session.json').read_text())['state']=='Passed'
for line in subprocess.check_output(['ps','-axo','comm='],text=True).splitlines():assert not line.strip().endswith('/Unity'),'Existing Unity process blocks isolated execution'
S=P.parent/('Storage-R03IRLocal-20261010E-native-receipt' if mode=='execute' else 'StorageCheck-R03IRLocal-20261010E-native-receipt');assert not os.path.lexists(S)
sdk='/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk';env=dict(os.environ,DOTNET_ROOT=sdk,DOTNET_ROOT_ARM64=sdk,DOTNET_MULTILEVEL_LOOKUP='0',PYTHONDONTWRITEBYTECODE='1',TMPDIR='/private/tmp',PATH=sdk+os.pathsep+os.environ['PATH'],EXPECTED_DEMO_COMMIT=source)
args=['/Library/Frameworks/Python.framework/Versions/3.14/bin/python3','-B',str(D/'Tools/AssemblyShadow/R03IR/run_terminal_storage_checked.py'),'--workspace',str(W),'--output',str(B),'--unity','/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity','--demo-commit',source,'--retained-q',str(P.parent/'R03LocalBatch-20261006Q-lp-repair'),'--storage-evidence',str(S)]
if mode=='execute':args.append('--execute')
folder=P/'commands'/('storage-execute' if mode=='execute' else 'storage-diagnostic');folder.mkdir(parents=True);start=datetime.datetime.now(datetime.timezone.utc).isoformat()
(folder/'invocation.json').write_text(json.dumps({'argv':args,'cwd':str(D),'startUtc':start,'sourceCommit':source,'executeFlag':mode=='execute','noOuterTimeoutOverride':True},indent=2)+'\n');print(json.dumps({'started':mode,'sourceCommit':source,'sidecar':str(S),'startUtc':start}),flush=True)
with (folder/'stdout.log').open('xb') as out,(folder/'stderr.log').open('xb') as err:r=subprocess.run(args,cwd=D,env=env,stdout=out,stderr=err)
def sha(f):
 with Path(f).open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
receipt={'argv':args,'cwd':str(D),'sourceCommit':source,'startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':r.returncode,'stdoutPath':str(folder/'stdout.log'),'stdoutSha256':sha(folder/'stdout.log'),'stderrPath':str(folder/'stderr.log'),'stderrSha256':sha(folder/'stderr.log'),'executeFlag':mode=='execute','coreRootExists':B.exists()};(folder/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True);sys.exit(r.returncode)
