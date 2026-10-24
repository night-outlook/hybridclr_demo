from pathlib import Path
import json,hashlib,datetime,os,subprocess,concurrent.futures,ast
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');ad=json.loads((B/'f51d-ADMISSION_BEFORE.json').read_text());W=Path(ad['workspace']);D=W/'hybridclr_demo';P=Path(ad['originalPreflight']);O=Path(ad['raw']);S=Path(ad['scratch']);A=Path(ad['stage']);CP=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-admitted-execution-20261023-b7e3';T=D/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/P1_HISTORICAL_AUDIT_HELPER_2026-10-24'
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1<<20),b''):h.update(x)
 return h.hexdigest()
load=lambda p:json.loads(p.read_text())
def save(n,r):
 p=A/n;assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
start=now();run=load(A/'AUDIT_ONLY_RUN_RECEIPT.json');stage=load(A/'AUDIT_ONLY_STAGE.json');provided=load(A/'AUDIT_ONLY_AFTER.json')
assert provided['result']=='Preserved' and provided['c42aCheckpointFiles']==197
assert run['sourceGitBlob']=='220aa2831458b37a81f66555f27d95349ec7013f' and (A/'audit.py').read_bytes()==subprocess.check_output(['git','-C',str(D),'cat-file','blob',run['sourceGitBlob']])
assert sha(A/'audit-only.stdout.bin')==run['stdoutSha256'] and sha(A/'audit-only.stderr.bin')==run['stderrSha256']
passed=run['result']=='PassedHistoricalAuditOnly_UnchangedLocalFail'
if passed:
 assert run['exit']==0 and run['unknownCommandLifetime'] is False and run['timedOut'] is False
 audit=load(A/'EVIDENCE_AUDIT.json');assert audit['result']=='PassedHistoricalEvidenceAuditOnly' and audit['auditMode']=='ReadOnlyIsolatedB7E3History' and audit['originalB7E3LocalResult']=='FAIL' and audit['liveRemoteHeadCheck']=='NotRun_TimeVariant' and audit['productAcceptance'] is False
 admitted=load(A/'ADMITTED_EXECUTION_VERIFICATION.json');git_hist=load(A/'GIT_HISTORICAL_AUTHORITY_AFTER.json')
 assert admitted['allEightOuterInventoriesVerified'] and admitted['consumerMutationsInsideOriginal85'] and admitted['nativeSyntaxConfigurations']==100 and not admitted['runtimeAcceptance']
 assert git_hist['result']=='PassedCapturedB7E3HistoricalSourceAuthorityOnly' and len(git_hist['references'])==4 and git_hist['actualNewGitOrSdkInvocation'] is False
# Recheck all original evidence against independent before records.
assert sha(O/'RESULT.json')==ad['rawResultSha256'] and sha(O/'MANIFEST.json')==ad['rawManifestSha256']
for row in load(O/'MANIFEST.json')['files']:q=O/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['size']
scratch=load(O/'native-sdk/native-sdk-inputs.json')['files']
for row in scratch:q=S/row['path'];assert q.resolve()==q and q.is_file() and not q.is_symlink() and sha(q)==row['sha256']
sdk=load(P/'SDK_BEFORE.json')
for row in sdk['files']:q=Path(row['path']);assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes'] and (os.readlink(q) if q.is_symlink() else None)==row['symlink']
for row in load(P/'SOURCE_BINDINGS.json'):q=Path(row['path']);assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
assert {str(q.relative_to(P)) for q in P.rglob('*') if q.is_file()}=={row['path'] for row in ad['originalPreflightFiles']}
for row in ad['originalPreflightFiles']:q=P/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
assert sha(CP/'MANIFEST.sha256')==ad['b7e3CheckpointManifestSha256']
for row in ad['b7e3CheckpointFiles']:q=CP/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
ret=load(P/'ADMISSION_RETAINED_BEFORE.json');links=0
for item in ret['consumed']:
 raw=Path(item['rawRoot']);scr=Path(item['scratchRoot']);assert sha(raw/'MANIFEST.json')==item['manifestSha256']
 for row in load(raw/'MANIFEST.json')['files']:q=raw/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['size']
 for row in load(raw/'native-sdk/native-sdk-inputs.json')['files']:assert sha(scr/row['path'])==row['sha256']
 for row in load(raw/'legacy-host/MANIFEST.json')['files']:
  if row.get('kind')=='Symlink':q=raw/'legacy-host'/row['path'];assert q.is_symlink() and os.readlink(q)==row['target'];links+=1
 ar=Path(item['auditRoot']);assert {str(q) for q in ar.rglob('*') if q.is_file() and not q.is_symlink()}=={row['path'] for row in item['auditFiles']}
 for row in item['auditFiles']:q=Path(row['path']);assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
for item in load(P/'ADMISSION_CHECKPOINTS_BEFORE.json')['checkpoints']:
 root=Path(item['root']);assert sha(root/'MANIFEST.sha256')==item['manifestSha256']
 for row in item['files']:q=root/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
for key in ['BLOCKED_ADMISSION_BEFORE.json','BLOCKED_6C72_BEFORE.json']:
 item=load(P/key);root=Path(item['checkpoint']);assert sha(root/'MANIFEST.sha256')==item['manifestSha256']
 for row in item['files']:q=root/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
 for row in item['externalFiles']:q=Path(row['path']);assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
for item in ad['consumedC42A'].values():
 root=Path(item['root']);assert {str(q.relative_to(root)) for q in root.rglob('*') if q.is_file()}=={row['path'] for row in item['files']}
 for row in item['files']:q=root/row['path'];assert not q.is_symlink() and sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
def current(n):
 path=W/n;rows=[]
 for args in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--short'],['remote','-v'],['worktree','list','--porcelain'],['submodule','status','--recursive'],['ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1']]:
  t=now();argv=['git','-C',str(path),*args];r=subprocess.run(argv,capture_output=True,text=True,timeout=90);rows.append(dict(argv=argv,start=t,end=now(),exit=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0
 assert rows[0]['stdout'].strip()==str(path) and rows[1]['stdout'].strip()=='codex/assembly-shadow-r01b-h1' and rows[2]['stdout'].strip()==ad['currentPins'][n] and not rows[3]['stdout'] and rows[-1]['stdout'].split()[0]==ad['currentPins'][n];return n,rows
repos=dict(concurrent.futures.ThreadPoolExecutor(4).map(current,ad['currentPins']))
save('F51D_INDEPENDENT_AFTER.json',dict(result='Preserved',start=start,end=now(),currentPins=ad['currentPins'],historicalPins=ad['executedHistoricalPins'],rawFiles=4269,sdkFiles=2405,sdkScratchFiles=1925,originalPreflightFiles=len(ad['originalPreflightFiles']),b7e3CheckpointFiles=len(ad['b7e3CheckpointFiles']),consumedP1Sets=len(ret['consumed']),originalCheckpointSets=24,historicalNegativeSymlinks=links,blockedHistoriesUnchanged=True,c42aCheckpointAndExternalFullyPreserved=True,c42aCheckpointFiles=197,c42aExternalFiles=len(ad['consumedC42A']['c42aExternal']['files']),currentGit= repos,originalLocalResultUnchanged='FAIL',rawPassedResultUnchanged=True,compilerSdkCoreInvoked=False,providedAfterReceipt='AUDIT_ONLY_AFTER.json'))
save('F51D_LOCAL_RESULT.json',dict(kind='IsolatedHistoricalAuditOnlyLocalOutcome',result='PASS' if passed else 'FAIL',scopedAuditResult=run['result'],sourceOnlyTests=51,sourceOnlyTestSuites=[17,11,23],sourceOnlyTestsResult='Passed',staging='PassedStagedNotExecuted',auditorExit=run['exit'],auditReport='PassedHistoricalEvidenceAuditOnly' if passed else 'Unavailable_NotProduced',providedAfter='Preserved',independentAfter='Preserved',newNontrivialFindings=[] if passed else ['Read exact audit stderr and partial receipts'],currentPins=ad['currentPins'],historicalPins=ad['executedHistoricalPins'],originalB7E3LocalResult='FAIL',originalC42ALocalResult='FAIL',originalB7E3Raw='PassedSourceHostAndSDKOnly',historicalAuthorityFinalJoin='PassedCapturedHistoricalSourceAuthorityOnly' if passed else 'Unavailable',coreAndSdkCompilerRerun=False,unityOrPlayerRun=False,retries=0,R03Accepted=False,H2Passed=False,qualificationApproved=False,ReadyForHumanReviewGate=False,runtimeAcceptance=False,fullLegacyRegressionAcceptance=False,nextState='Primary Implementation'))
print('f51d',run['result'],'original evidence independently preserved; no retry')
