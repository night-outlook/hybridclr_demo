from pathlib import Path
import json,hashlib,datetime,os,subprocess,concurrent.futures,ast
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');ad=json.loads((B/'c42a-ADMISSION_BEFORE.json').read_text());W=Path(ad['workspace']);D=W/'hybridclr_demo';P=Path(ad['originalPreflight']);O=Path(ad['raw']);S=Path(ad['scratch']);A=Path(ad['stage']);CP=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-admitted-execution-20261023-b7e3';T=D/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/P1_B7E3_AUDIT_ONLY_2026-10-23'
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1<<20),b''):h.update(x)
 return h.hexdigest()
load=lambda p:json.loads(p.read_text())
def save(n,r):
 p=A/n;assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
start=now();run=load(A/'AUDIT_ONLY_RUN_RECEIPT.json');stage=load(A/'AUDIT_ONLY_STAGE.json');provided=load(A/'AUDIT_ONLY_AFTER.json');assert run['exit']==1 and run['unknownCommandLifetime'] is False and run['timedOut'] is False and provided['result']=='Preserved' and not (A/'EVIDENCE_AUDIT.json').exists()
assert run['sourceGitBlob']=='c451e0cb7794e624eabb9029db0a35ba28d14592' and (A/'audit.py').read_bytes()==subprocess.check_output(['git','-C',str(D),'cat-file','blob',run['sourceGitBlob']])
assert sha(A/'audit-only.stdout.bin')==run['stdoutSha256'] and sha(A/'audit-only.stderr.bin')==run['stderrSha256']
stderr=(A/'audit-only.stderr.bin').read_text();assert 'line 1031' in stderr and 'StopIteration' in stderr
source=D/'Tools/AssemblyShadow/R03IR/test_p1_command_failures.py';data=source.read_bytes();assert data==subprocess.check_output(['git','-C',str(D),'show','49c6b62d38d7668be10004ac1e5a030d74894f09:Tools/AssemblyShadow/R03IR/test_p1_command_failures.py'])
tree=ast.parse(data);wanted='verify_admitted_execution_receipt_and_fail_closed_mutations';actual='verify_admitted_execution_receipt_and_negative_mutations';matches=[n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==actual];assert len(matches)==1 and not any(isinstance(n,ast.FunctionDef) and n.name==wanted for n in ast.walk(tree));node=matches[0];sourceText=data.decode()
assert 'OwnedBindingInventoryContract().'+actual+'()' in sourceText
finding=dict(id='IR-LOCAL-P1-HISTORICAL-AUDIT-HELPER-01',status='ReproducedHistoricalAuditorStopIteration',scope='One new isolated historical audit-only attempt; original b7e3 Local FAIL and raw PASS unchanged',currentAuditPins=ad['currentPins'],historicalExecutionPins=ad['executedHistoricalPins'],failedCommand=run['argv'],pid=run['pid'],start=run['start'],end=run['end'],exit=run['exit'],timedOut=False,unknownLifetime=False,auditorPath=str(A/'audit.py'),auditorGitBlob=run['sourceGitBlob'],auditorSha256=sha(A/'audit.py'),firstFailureLine=1031,exception='StopIteration',stderrPath=str(A/'audit-only.stderr.bin'),stderrSha256=run['stderrSha256'],expectedHelper=wanted,actualHelper=actual,actualHelperLine=node.lineno,actualHelperSourcePath=str(source),actualHelperSourceSha256=sha(source),actualHelperByteIdenticalToHistoricalB7E3Source=True,actualHelperSource=ast.get_source_segment(sourceText,node),actualHelperCalledByExisting85TestLeaf=True,nextUnreachedAssertLine=1032,rootCause='The inherited auditor AST lookup uses a nonexistent helper name. The exact recorded original test source defines and calls the negative_mutations helper. Both AST lookup and following required-call-string check reference the wrong fail_closed_mutations spelling.',affectedScope='Historical independent evidence auditor and its remaining final admitted-contract/historical-authority/report checks; no native, SDK compiler, fixture-byte or product failure demonstrated.',recommendedDirection='Bind the successor audit lookup AND its following call-site assertion to verify_admitted_execution_receipt_and_negative_mutations in the original source. Add source-bound regressions that resolve exactly one actual method and its existing call, and fail clearly on absent/duplicate/wrong identities. Keep all negative-mutation checks, original85 IDs, strict signatures and historical-only authority scope. Do not rename original test source to match the auditor or edit consumed artifacts.',remainingUncertainty='All statements after the failing lookup were not executed, including admitted verification output, final captured GIT_BEFORE authority join and EVIDENCE_AUDIT.json; later defects remain possible.',validationRequired='A separately authorized source-pinned historical-only audit successor with before/after preservation; no original core/SDK/Player rerun implied.',originalB7E3LocalResult='FAIL',originalRawResult='PassedSourceHostAndSDKOnly',newAuditResult='FailedOrIncomplete',auditRetried=False,sourceAssertionsChangedLocally=False,coreSdkUnityPlayerInvoked=False,productAcceptance=False)
save('C42A_FINDING.json',finding)
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
def current(n):
 path=W/n;rows=[]
 for args in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--short'],['remote','-v'],['worktree','list','--porcelain'],['submodule','status','--recursive'],['ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1']]:
  t=now();argv=['git','-C',str(path),*args];r=subprocess.run(argv,capture_output=True,text=True,timeout=90);rows.append(dict(argv=argv,start=t,end=now(),exit=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0
 assert rows[0]['stdout'].strip()==str(path) and rows[1]['stdout'].strip()=='codex/assembly-shadow-r01b-h1' and rows[2]['stdout'].strip()==ad['currentPins'][n] and not rows[3]['stdout'] and rows[-1]['stdout'].split()[0]==ad['currentPins'][n];return n,rows
repos=dict(concurrent.futures.ThreadPoolExecutor(4).map(current,ad['currentPins']))
save('C42A_INDEPENDENT_AFTER.json',dict(result='Preserved',start=start,end=now(),currentPins=ad['currentPins'],historicalPins=ad['executedHistoricalPins'],rawFiles=4269,sdkFiles=2405,sdkScratchFiles=1925,originalPreflightFiles=len(ad['originalPreflightFiles']),b7e3CheckpointFiles=len(ad['b7e3CheckpointFiles']),consumedP1Sets=len(ret['consumed']),originalCheckpointSets=24,historicalNegativeSymlinks=links,blockedHistoriesUnchanged=True,currentGit= repos,originalLocalResultUnchanged='FAIL',rawPassedResultUnchanged=True,compilerSdkCoreInvoked=False,providedAfterReceipt='AUDIT_ONLY_AFTER.json'))
save('C42A_LOCAL_RESULT.json',dict(kind='IsolatedHistoricalAuditOnlyLocalOutcome',result='FAIL',scopedAuditResult='FailedOrIncomplete',sourceOnlyTests=23,sourceOnlyTestsResult='Passed',staging='PassedStagedNotExecuted',auditorExit=1,auditorError='StopIteration_Line1031',auditReport='Unavailable_NotProduced',providedAfter='Preserved',independentAfter='Preserved',firstFinding=finding['id'],currentPins=ad['currentPins'],historicalPins=ad['executedHistoricalPins'],originalB7E3LocalResult='FAIL',originalB7E3Raw='PassedSourceHostAndSDKOnly',historicalAuthorityFinalJoin='NotRun_AfterFirstFailure',laterChecks='NotRun',coreAndSdkCompilerRerun=False,unityOrPlayerRun=False,retries=0,R03Accepted=False,H2Passed=False,qualificationApproved=False,ReadyForHumanReviewGate=False,runtimeAcceptance=False,fullLegacyRegressionAcceptance=False,nextState='Primary Implementation'))
print('c42a FAIL; original evidence preservation Passed; no retry')
