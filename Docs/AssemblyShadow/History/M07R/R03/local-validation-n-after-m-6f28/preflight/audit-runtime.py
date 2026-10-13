from h_common import *
import tarfile,collections
start=now();R=B/'R03IRLocal-N-after-M-6f28';idx=load(R/'evidence-index.json');files={r['path']:r for r in idx['files']};assert len(files)==len(idx['files'])
def check_rows(root,rows):
 for r in rows:
  f=root/r['path'];assert f.is_file() and not f.is_symlink() and f.stat().st_size==r['size'] and sha(f)==r['sha256'],f
check_rows(R,idx['files']);members=[]
with tarfile.open(R/'evidence.tar.gz','r:gz') as t:
 for m in t:
  assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts;f=t.extractfile(m);h=hashlib.file_digest(f,'sha256').hexdigest()
  if m.name in files:assert m.size==files[m.name]['size'] and h==files[m.name]['sha256']
  else:assert m.name=='evidence-index.json' and h==sha(R/'evidence-index.json')
  members.append(m.name)
assert len(members)==len(set(members))==len(files)+1 and set(members)==set(files)|{'evidence-index.json'}
result=load(R/'LOCAL_BATCH_RESULT.json');ledger=load(R/'BATCH_EXECUTION.json');seal=load(R/'seal-receipt.json');assert result['cells']==ledger['cells'] and result['executionLedgerSha256']==sha(R/'BATCH_EXECUTION.json') and seal==result['seal'];assert result['sealStatus']=='Passed' and seal['archiveSha256']==sha(R/'evidence.tar.gz') and seal['indexSha256']==sha(R/'evidence-index.json');assert len(result['cells'])==18;states=collections.Counter(r['result'] for r in result['cells'])
commands=[]
for f in sorted((R/'commands').glob('*/command.json')):
 c=load(f)
 for n in ['stdout','stderr']:assert sha(f.parent/(n+'.log'))==c[n+'Sha256']
 assert not c['cleanupErrors'] and not c['remainingProcessGroup'] and not c['postCleanupGroupExists'];commands.append({'path':str(f),'sha256':sha(f),'pid':c['pid'],'pgid':c['pgid'],'startEpoch':c['startedUtcEpoch'],'endEpoch':c['endedUtcEpoch'],'exitCode':c['exitCode'],'timeout':c['timeout'],'interrupted':c['interrupted'],'command':c['command']})
builds=[]
for role in ['candidate-release','candidate-debug','candidate-off']:
 cell=next(c for c in result['cells'] if c['id']=='build-'+role);path=R/'builds'/role/'build-receipt.json';row={'role':role,'state':cell['result'],'receiptAvailable':path.is_file()}
 if path.is_file() and cell['result']=='Passed':
  r=load(path);native=Path(r['installedNativeRoot']);assert native.is_relative_to(R/'projects'/role) and native.resolve()==native;assert r['result']=='Passed' and r['errors']==0 and r['unityVersion']=='2022.3.62f2' and r['architecture']=='arm64' and sha(path)==cell['evidence']['sha256'];before={x['path']:x for x in r['installedBefore']};after={x['path']:x for x in r['installedAfter']};allowed={'hybridclr/generated/AssemblyManifest.cpp','hybridclr/generated/MethodBridge.cpp','hybridclr/generated/UnityVersion.h','vm/AssemblyShadowR03Probe.cpp'};assert {n for n in before.keys()|after.keys() if before.get(n)!=after.get(n)}<=allowed and r['nonGeneratedCorePreserved'];check_rows(native,r['installedAfter']);check_rows(Path(r['outputPath']),r['playerFiles']);assert sha(native/'assembly-shadow-install.json')==r['installReceiptSha256'] and cell['evidence']['nativeBinding']['repositories']==pins;row.update(receipt=str(path),receiptSha256=sha(path),installedNativeRoot=str(native),nativeFilesVerified=len(r['installedAfter']),installedFileInventory=r['installedAfter'],playerFilesVerified=len(r['playerFiles']),featureEnabled=r['featureEnabled'],cppConfiguration=r['cppConfiguration'])
 if path.is_file() and cell['result']!='Passed':
  failed=load(path);row.update(receipt=str(path),receiptSha256=sha(path),reportedResult=failed.get('result'),errors=failed.get('errors'),warnings=failed.get('warnings'),exception=failed.get('exception'),installedNativeRoot=failed.get('installedNativeRoot'),installedFileInventory=failed.get('installedAfter'),nativeFilesVerified=len(failed.get('installedAfter',[])));check_rows(Path(failed['installedNativeRoot']),failed.get('installedAfter',[]))
 builds.append(row)
players=[]
for case in ['IR-R03-02-release-baseline','IR-R03-02-debug-baseline','IR-R03-02-release-type','IR-R03-02-off','IR-R03-02-release-engine']:
 root=R/'players'/case;cell=next(c for c in result['cells'] if c['id']==case);row={'caseId':case,'state':cell['result'],'request':'NotRun','raw':'Unavailable','verification':'Unavailable'}
 if (root/'request.json').exists():
  request=load(root/'request.json');launch=[c for c in commands if '-r03IrRequest' in c['command'] and c['command'][c['command'].index('-r03IrRequest')+1]==str(root/'request.json')];assert len(launch)==1;c=launch[0];assert c['command'][c['command'].index('-r03IrRunId')+1]==request['runId'];row.update(request='Recorded',requestSha256=sha(root/'request.json'),pid=c['pid'],runId=request['runId'],commandReceipt=c['path'],commandSha256=c['sha256'],exitCode=c['exitCode'],timeout=c['timeout'],startEpoch=c['startEpoch'],endEpoch=c['endEpoch'],logSha256=sha(root/'Player.log') if (root/'Player.log').exists() else None)
  if (root/'raw.json').exists() and (root/'raw.json').stat().st_size==0:row.update(raw='Recorded zero-byte file; semantic JSON Unavailable',rawSha256=sha(root/'raw.json'),rawBytes=0)
  if (root/'raw.json').exists() and (root/'raw.json').stat().st_size>0:
   raw=load(root/'raw.json');assert raw['runId']==request['runId'] and raw['processId']==c['pid'] and raw['requestSha256']==sha(root/'request.json');row.update(raw='Recorded',rawSha256=sha(root/'raw.json'),rawResult=raw.get('result'),rawError=raw.get('error'),semantics={k:v for k,v in raw.items() if k in ['initialState','poisonedState','finalState','prePositive','preActiveReflection','preActiveDelegate','preShadowField','shadowFieldReadable','finalShadowField','preCanaryCount','finalCanaryCount','recoveryStable','fixedDiagnosticsReadable','terminalReportingProbeMask','activeReflectionAttempted','activeReflectionSucceeded','activeDelegateAttempted','activeDelegateSucceeded','aotReflectionAttempted','aotReflectionSucceeded','firstRecovery','finalRecovery','nativeStimulusReturn','reserveGcProbeMask','completedReports','preManagedLoggerCalls','finalManagedLoggerCalls','timedOut','observationMilliseconds','recovery','reportTransport']})
  if (root/'verification.json').exists():
   v=load(root/'verification.json');assert v['runId']==request['runId'] and v['launchPid']==c['pid'] and v['requestSha256']==sha(root/'request.json') and v['rawSha256']==sha(root/'raw.json');row.update(verification=v['result'],verificationSha256=sha(root/'verification.json'),verifierError=v.get('error'))
 players.append(row)
storage=[]
for label,root in [('diagnostic',B/'StorageCheck-R03IRLocal-N-after-M-6f28'),('execution',B/'Storage-R03IRLocal-N-after-M-6f28')]:
 a=load(root/'admission.json');s=load(root/'session.json');d=load(root/'dispatch.json');assert a['state']=='Admitted' and d['sessionSha256']==sha(root/'session.json') and s['telemetrySha256']==sha(root/'capacity.jsonl');assert d['batchStarted']==(label=='execution')
 if label=='execution':assert d['coreResultSha256']==sha(R/'LOCAL_BATCH_RESULT.json')
 storage.append({'role':label,'admission':a['state'],'sessionState':s['state'],'batchStarted':d['batchStarted'],'batchExitCode':d['batchExitCode'],'thresholdBytes':a['requiredAvailableBytesEachLocation'],'minimumSampledAvailableBytes':s['minimumSampledAvailableBytes'],'samples':s['samples'],'latchedProblem':s['latchedProblem'],'capacityReserved':False})
rec={'state':'EvidenceAuthenticationPassed','startUtc':start,'endUtc':now(),'runtimeCoreResult':result['result'],'sources':pins,'cells':[{k:c[k] for k in ['id','result']} for c in result['cells']],'cellCounts':dict(states),'builds':builds,'players':players,'commands':commands,'storage':storage,'topArtifacts':[{'path':str(R/n),'bytes':(R/n).stat().st_size,'sha256':sha(R/n)} for n in ['LOCAL_BATCH_RESULT.json','BATCH_EXECUTION.json','evidence-index.json','evidence.tar.gz','seal-receipt.json']],'indexedFiles':len(files),'archiveMembers':len(members),'excludedLiveRoots':idx['excludedLiveRoots'],'sealStatus':result['sealStatus'],'boundedEvidenceOnly':True,'runtimeAcceptance':False,'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'ReadyForHumanReviewGate':False};save(P/'FINAL_EVIDENCE_AUDIT.json',rec);print(json.dumps({'state':rec['state'],'runtimeResult':result['result'],'cells':dict(states),'builds':[r['state'] for r in builds],'players':[r['state'] for r in players],'indexedFiles':len(files)}),flush=True)
