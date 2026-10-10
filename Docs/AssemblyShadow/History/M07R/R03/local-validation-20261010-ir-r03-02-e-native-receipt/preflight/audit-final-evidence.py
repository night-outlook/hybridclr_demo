from pathlib import Path
import json,hashlib,tarfile,datetime,concurrent.futures,subprocess
P=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261010E-native-receipt');B=P.parent/'R03IRLocal-20261010E-native-receipt';W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');pins=json.loads((P/'SOURCE_ENVIRONMENT.json').read_text())['pins'];branch='codex/assembly-shadow-r01b-h1'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(f):
 with Path(f).open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def load(f):return json.loads(Path(f).read_text())
def checkrows(root,rows):
 for r in rows:
  f=root/r['path'];assert f.is_file() and not f.is_symlink() and f.stat().st_size==r['size'] and sha(f)==r['sha256'],str(f)
start=now();index=load(B/'evidence-index.json');checkrows(B,index['files']);expected={r['path']:r for r in index['files']};archiveRows=[]
with tarfile.open(B/'evidence.tar.gz','r:gz') as t:
 for m in t:
  assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
  f=t.extractfile(m);h=hashlib.file_digest(f,'sha256').hexdigest()
  if m.name in expected:assert m.size==expected[m.name]['size'] and h==expected[m.name]['sha256']
  else:assert m.name=='evidence-index.json' and h==sha(B/'evidence-index.json')
  archiveRows.append(m.name)
assert len(archiveRows)==len(set(archiveRows))==1000 and set(archiveRows)==set(expected)|{'evidence-index.json'}
result=load(B/'LOCAL_BATCH_RESULT.json');ledger=load(B/'BATCH_EXECUTION.json');seal=load(B/'seal-receipt.json');assert result['cells']==ledger['cells'] and result['executionLedgerSha256']==sha(B/'BATCH_EXECUTION.json');assert result['sealStatus']=='Passed' and result['result']=='ReturnRequired';assert seal==result['seal'];assert seal['archiveSha256']==sha(B/'evidence.tar.gz') and seal['indexSha256']==sha(B/'evidence-index.json')
assert len(result['cells'])==14 and sum(x['result']=='Passed' for x in result['cells'])==11 and sum(x['result']=='Failed' for x in result['cells'])==3
builds=[]
for role in ['candidate-release','candidate-debug','candidate-off']:
 cell=next(c for c in result['cells'] if c['id']=='build-'+role);r=load(B/'builds'/role/'build-receipt.json');native=Path(r['installedNativeRoot']);assert native.is_relative_to(B/'projects'/role) and native.resolve()==native
 assert r['result']=='Passed' and r['errors']==0 and r['unityVersion']=='2022.3.62f2' and r['architecture']=='arm64';assert sha(B/'builds'/role/'build-receipt.json')==cell['evidence']['sha256'];before={x['path']:x for x in r['installedBefore']};after={x['path']:x for x in r['installedAfter']};allowed={'hybridclr/generated/AssemblyManifest.cpp','hybridclr/generated/MethodBridge.cpp','hybridclr/generated/UnityVersion.h','vm/AssemblyShadowR03Probe.cpp'};assert {n for n in before.keys()|after.keys() if before.get(n)!=after.get(n)}<=allowed;assert r['nonGeneratedCorePreserved'];checkrows(native,r['installedAfter']);checkrows(Path(r['outputPath']),r['playerFiles']);assert len(r['installedAfter'])==972 and sha(native/'assembly-shadow-install.json')==r['installReceiptSha256'];assert cell['evidence']['nativeBinding']['repositories']==pins
 builds.append({'role':role,'state':'Passed','receipt':str(B/'builds'/role/'build-receipt.json'),'receiptSha256':cell['evidence']['sha256'],'installedNativeRoot':str(native),'verifiedNativeFiles':972,'playerFilesVerified':len(r['playerFiles']),'installedFileInventory':r['installedAfter'],'featureEnabled':r['featureEnabled'],'cppConfiguration':r['cppConfiguration'],'linkedDllInventoryBoundByReceipt':True,'provenance':'Fresh E build; retained live native root required independently of bounded core archive'})
players=[]
for n,num in [('release-baseline','0006'),('debug-baseline','0007'),('release-type','0008'),('off','0009')]:
 case='IR-R03-02-'+n;root=B/'players'/case;c=load(B/'commands'/num/'command.json');request=load(root/'request.json');assert c['pid']==c['pgid'] and not c['timeout'] and not c['interrupted'] and not c['remainingProcessGroup'] and not c['postCleanupGroupExists'] and not c['cleanupErrors'];assert c['command'][c['command'].index('-r03IrRunId')+1]==request['runId'];assert c['command'][c['command'].index('-r03IrRequest')+1]==str(root/'request.json')
 row={'caseId':case,'pid':c['pid'],'runId':request['runId'],'commandReceipt':str(B/'commands'/num/'command.json'),'commandReceiptSha256':sha(B/'commands'/num/'command.json'),'requestSha256':sha(root/'request.json'),'logSha256':sha(root/'Player.log'),'startUtc':datetime.datetime.fromtimestamp(c['startedUtcEpoch'],datetime.timezone.utc).isoformat(),'endUtc':datetime.datetime.fromtimestamp(c['endedUtcEpoch'],datetime.timezone.utc).isoformat(),'exitCode':c['exitCode'],'timeout':False,'ownedLifetimeCleanup':'Passed','rawState':'Passed' if n=='off' else 'Unavailable','verificationState':'Passed' if n=='off' else 'Unavailable'}
 if n=='off':
  raw=load(root/'raw.json');v=load(root/'verification.json');assert c['exitCode']==0 and raw['result']==v['result']=='Passed' and raw['processId']==v['launchPid']==c['pid'] and raw['runId']==request['runId'] and v['rawSha256']==sha(root/'raw.json') and v['requestSha256']==sha(root/'request.json') and raw['preCanaryCount']==1 and raw['finalCanaryCount']==2
  row.update({'state':'Passed','rawSha256':sha(root/'raw.json'),'verificationSha256':sha(root/'verification.json'),'canary':'1 -> 2'})
 else:
  assert c['exitCode']==-11 and not (root/'raw.json').exists() and not (root/'verification.json').exists();row.update({'state':'Failed','signal':'SIGSEGV','preAndPostPoisonSideEffectProof':'Unavailable','firstTerminalCause':'Unavailable'})
 players.append(row)
custody=[]
for phase in ['before','after']:
 r=load(P/('scoped-custody-'+phase+'.json'));assert r['result']=='ScopedHistoricalLossStable' and r['completeScan'] and r['originalExpectedFiles']==416844 and r['presentVerified']==339367 and r['historicalStillMissing']==77477 and not r['problems'] and r['originalStrictCustody']=='Blocked' and not r['strictFullHistoricalCustodyAccepted'];custody.append({'phase':phase,'path':str(P/('scoped-custody-'+phase+'.json')),'sha256':sha(P/('scoped-custody-'+phase+'.json')),'result':r['result'],'startUtc':r['startedUtc'],'endUtc':r['completedUtc'],'presentVerified':339367,'historicalStillMissing':77477,'strictHistoricalCustody':'Blocked'})
storage=[]
for label,root in [('diagnostic',P.parent/'StorageCheck-R03IRLocal-20261010E-native-receipt'),('execution',P.parent/'Storage-R03IRLocal-20261010E-native-receipt')]:
 a=load(root/'admission.json');s=load(root/'session.json');d=load(root/'dispatch.json');assert a['state']=='Admitted' and s['state']==d['storageState']=='Passed' and s['latchedProblem'] is None and d['sessionSha256']==sha(root/'session.json') and s['telemetrySha256']==sha(root/'capacity.jsonl');assert d['batchStarted']==(label=='execution')
 if label=='execution':assert d['batchExitCode']==1 and d['coreResultSha256']==sha(B/'LOCAL_BATCH_RESULT.json')
 storage.append({'role':label,'root':str(root),'admission':'Admitted','storageSession':'Passed','batchStarted':d['batchStarted'],'batchExitCode':d['batchExitCode'],'requiredAvailableBytes':a['requiredAvailableBytesEachLocation'],'minimumSampledAvailableBytes':s['minimumSampledAvailableBytes'],'samples':s['samples'],'sampledMinimumNotActualHighWater':True,'capacityReserved':False,'failureDiagnostics':[p.name for p in root.glob('failure-*.json')]})
def authority(n):
 repo=W/n;rows=[]
 for args in [('rev-parse','--show-toplevel'),('branch','--show-current'),('rev-parse','HEAD'),('status','--short'),('remote','-v'),('worktree','list','--porcelain'),('submodule','status','--recursive'),('ls-remote','origin','refs/heads/'+branch)]:
  t=now();r=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True,timeout=180);assert r.returncode==0;rows.append({'argv':['git','-C',str(repo),*args],'startUtc':t,'endUtc':now(),'exitCode':0,'stdout':r.stdout,'stderr':r.stderr})
 assert rows[0]['stdout'].strip()==str(repo) and rows[1]['stdout'].strip()==branch and rows[2]['stdout'].strip()==pins[n] and not rows[3]['stdout'].strip() and rows[-1]['stdout'].split()[0]==pins[n]
 return {'path':str(repo),'branch':branch,'commit':pins[n],'state':'Passed','commands':rows}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:owners=list(pool.map(authority,pins))
with (P/'FINAL_EXECUTION_SOURCE_AUTHORITY.json').open('x') as f:json.dump({'state':'Passed','repositories':owners},f,indent=2);f.write('\n')
record={'state':'EvidenceAuthenticationPassed','runtimeResult':'FAIL / ReturnRequired','startUtc':start,'endUtc':now(),'batchRoot':str(B),'sources':pins,'topArtifacts':[{ 'path':str(B/n),'bytes':(B/n).stat().st_size,'sha256':sha(B/n)} for n in ['LOCAL_BATCH_RESULT.json','BATCH_EXECUTION.json','evidence-index.json','evidence.tar.gz','seal-receipt.json']],'indexedFiles':999,'archiveMembers':1000,'sealStatus':'Passed','boundedEvidenceOnly':True,'excludedLiveRoots':index['excludedLiveRoots'],'cells':[{k:c[k] for k in ['id','result']} for c in result['cells']],'builds':builds,'players':players,'custody':custody,'storage':storage,'capturedGenericFailure':'NotRun','initializerFailure':'NotRun','boundedFixes':[],'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'ReadyForHumanReviewGate':False,'pureInterpreterExpansionEnabled':False,'exitState':'Local Validation -> Primary Implementation'}
with (P/'FINAL_EVIDENCE_AUDIT.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps({'state':record['state'],'runtimeResult':record['runtimeResult'],'indexedFiles':999,'archiveMembers':1000,'buildsPassed':3,'playersPassed':1,'playersFailed':3,'custody':'Before/after ScopedHistoricalLossStable; strict historical Blocked'}))
