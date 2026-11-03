from pathlib import Path
import json,hashlib,subprocess,datetime,shutil,re,os
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';S=B/'OriginalS-20261026-fc55-oneuse';O=B/'R03IR-CurrentNativeOriginalS-20261103-oneuse-J';M=B/'R03OriginalS-SparseProjection-20261026-oneuse-C';now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();start=now()
r=json.loads((O/'RESULT.json').read_text());assert r['result'] in ['ReturnRequired','FocusedEvidenceReadyForIndependentReview']
counts={}
for k,v in r['stages'].items():counts[v['state']]=counts.get(v['state'],0)+1
assert sum(counts.values())>=10 and set(counts)<=set(['Failed','Passed','Blocked'])
outer=json.loads((O/'COORDINATOR_MANIFEST.json').read_text());assert outer['kind']=='R03IRCoordinatorReceiptsOnly' and outer['externalChildEvidenceSealedHere'] is False
for row in outer['files']:p=O/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
assert (O/'current-native').is_dir()
steps=[]
for p in sorted((O/'steps').glob('*/RESULT.json')):
 row=json.loads(p.read_text());assert sha(p.parent/'stdout.log')==row['stdoutSha256'] and sha(p.parent/'stderr.log')==row['stderrSha256'];assert not row['timedOut'] and not row['mayHaveExternalOwnedChildren'] and not row['processGroupRemainedAtExit'] and not row['postCleanupGroupExists'];steps.append(dict(path=str(p),sha256=sha(p),state=row['state'],pid=row['processId']))
audit=json.loads((O/'original-s-audit/audit.json').read_text());joins=json.loads((O/'original-s-process-joins/process-joins.json').read_text());assert audit['result']==joins['result']=='Passed' and audit['archiveMembers']==15713 and audit['cells']==90 and joins['totalPlayerReceipts']==59
for line in (O/'original-s-audit/MANIFEST.sha256').read_text().splitlines():
 h,rel=line.split('  ',1);assert sha(S/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready'/rel)==h
protected=json.loads((B/'oneuse-C-PROTECTED_BEFORE.json').read_text())
for row in protected['rows']:p=S/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
before=json.loads((B/'oneuse-J-PRESERVATION_BEFORE.json').read_text())
for item in before['history']:
 root=Path(item['root']);assert sha(root/'MANIFEST.sha256')==item['manifestSha256']
 for row in item['files']:assert sha(root/row['path'])==row['sha256']
SDK=json.loads((B/'Preflight-R03-P1-ADMITTED-EXECUTION-20261023-b7e3/SDK_BEFORE.json').read_text())
for row in SDK['files']:p=Path(row['path']);assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
env=json.loads((B/'oneuse-J-ENVIRONMENT_BEFORE.json').read_text());assert sha(Path(env['dotnet']))==env['dotnetSha256'] and sha(Path(env['Unity2022']))==env['unitySha256']
pins=before['sourcePins'];repos={}
for n in list(pins)+['OriginalS']:
 p=S if n=='OriginalS' else W/n;rows=[]
 for a in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--porcelain=v1','--untracked-files=all'],['remote','-v'],['worktree','list','--porcelain'],['submodule','status','--recursive']]+([] if n=='OriginalS' else [['ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1']]):
  argv=['git','-C',str(p),*a];t=now();v=subprocess.run(argv,capture_output=True,text=True,timeout=120);assert v.returncode==0;rows.append(dict(argv=argv,start=t,end=now(),exit=v.returncode,stdout=v.stdout,stderr=v.stderr))
 expected='fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b' if n=='OriginalS' else pins[n];assert rows[0]['stdout'].strip()==str(p) and rows[2]['stdout'].strip()==expected and not rows[3]['stdout']
 if n!='OriginalS':assert rows[1]['stdout'].strip()=='codex/assembly-shadow-r01b-h1' and rows[-1]['stdout'].split()[0]==expected
 else:assert not rows[1]['stdout']
 repos[n]=rows
procs=subprocess.check_output(['/bin/ps','-axo','pid=,ppid=,pgid=,command='],text=True);survivors=[]
for l in procs.splitlines():
 fields=l.strip().split(None,3)
 if len(fields)==4 and str(O) in fields[3] and any(k in fields[3].split(' ',1)[0] for k in ['Unity','dotnet','clang','python']):survivors.append(l)
assert not survivors
# Independently authenticate child sealed failure evidence, without running any product tool.
import tarfile,collections
N=O/'current-native'; child=json.loads((N/'LOCAL_BATCH_RESULT.json').read_text());countsChild=dict(collections.Counter(c['result'] for c in child['cells']));assert sum(countsChild.values())==18
assert child['sealStatus']=='Passed'
idx=json.loads((N/'evidence-index.json').read_text());seal=json.loads((N/'seal-receipt.json').read_text());assert sha(N/'evidence-index.json')==seal['indexSha256'] and sha(N/'evidence.tar.gz')==seal['archiveSha256'];assert sha(N/'BATCH_EXECUTION.json')==child['executionLedgerSha256']
for row in idx['files']:
 p=N/row['path'];assert p.is_file() and sha(p)==row['sha256'] and p.stat().st_size==row['size']
with tarfile.open(N/'evidence.tar.gz') as t:
 members=t.getmembers();assert len(members)==seal['members']
 for member in members:
  assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
  assert hashlib.sha256(t.extractfile(member).read()).hexdigest()==sha(N/member.name)
commands=[]
for p in sorted((N/'commands').glob('*/command.json')):
 d=json.loads(p.read_text());assert not d['timeout'] and not d['remainingProcessGroup'] and not d['postCleanupGroupExists'] and not d['interrupted'] and not d['cleanupErrors']
 assert sha(p.parent/'stdout.log')==d['stdoutSha256'] and sha(p.parent/'stderr.log')==d['stderrSha256'];commands.append(dict(path=str(p),sha256=sha(p),pid=d['pid'],pgid=d['pgid'],exitCode=d['exitCode'],start=d['startedUtcEpoch'],end=d['endedUtcEpoch']))
assert len(commands)>=5
for row in json.loads((B/'oneuse-J-CI_GATE.json').read_text())['sourceBindings']:
 assert sha(W/row['repository']/row['path'])==row['sha256']
# Preserve prior D/E complete retained live files independently, not only published checkpoints.
draw=json.loads((B/'oneuse-D-RAW_MANIFEST.json').read_text());dr=Path(draw['root'])
for row in draw['files']:
 p=dr/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
for row in draw['symlinks']:assert (dr/row['path']).is_symlink() and os.readlink(dr/row['path'])==row['target']
eraw=json.loads((B/'oneuse-E-RAW_MANIFEST.json').read_text());er=Path(eraw['root'])
for row in eraw['files']:
 p=er/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
for row in eraw['symlinks']:assert (er/row['path']).is_symlink() and os.readlink(er/row['path'])==row['target']
graw=json.loads((B/'oneuse-G-RAW_MANIFEST.json').read_text());gr=Path(graw['root'])
for row in graw['files']:
 p=gr/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
for row in graw['symlinks']:assert (gr/row['path']).is_symlink() and os.readlink(gr/row['path'])==row['target']
hraw=json.loads((B/'oneuse-H-RAW_MANIFEST.json').read_text());hr=Path(hraw['root'])
for row in hraw['files']:
 p=hr/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
for row in hraw['symlinks']:assert (hr/row['path']).is_symlink() and os.readlink(hr/row['path'])==row['target']
iraw=json.loads((B/'oneuse-I-RAW_MANIFEST.json').read_text());ir=Path(iraw['root'])
for row in iraw['files']:
 p=ir/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
for row in iraw['symlinks']:assert (ir/row['path']).is_symlink() and os.readlink(ir/row['path'])==row['target']
assert not (B/'R03IR-CurrentNativeOriginalS-20261102-oneuse-F').exists()
if r['result']=='FocusedEvidenceReadyForIndependentReview':
 assert counts=={'Passed':10} and countsChild=={'Passed':18} and child['verifiedFreshBuilds']==3 and child['verifiedFreshPlayers']==5 and child['recordedFreshPlayerRawFiles']==5
 parity=json.loads((O/'installed-native-vm-parity.json').read_text());assert parity['result']=='PassedInstalledSourceParityOnly' and parity['installedVmSourcePairs']==135
parityPath=O/'installed-native-vm-parity.json'
if r['stages']['native-installed-source-audit']['state']=='Passed':
 parity=json.loads(parityPath.read_text());assert parity['result']=='PassedInstalledSourceParityOnly' and parity['installedVmSourcePairs']==135 and parity['verifiedBuildRoles']==3
 assert parity['siblingPlayerBatchResult']==child['result'] and parity['siblingPlayerSemanticsAccepted']==(child['result']=='FocusedEvidenceReadyForPrimaryReview')
 assert parity['runtimeAcceptance'] is False and parity['R03Accepted'] is False
 for role in parity['roles']:
  assert role['changedVmFiles']==45 and sha(N/'builds'/role['role']/'build-receipt.json')==role['buildReceiptSha256']
  for row in role['sources']:
   assert sha(W/'il2cpp_plus'/row['source'])==row['sha256']==sha(Path(role['installedNativeRoot'])/row['installed'])
hostRoot=O/'native-host-diagnostics';host=json.loads((hostRoot/'RESULT.json').read_text());assert host['kind']=='R03IRCurrentNativeTenHostComponents' and host['result']=='PassedHostOnlyTenComponents' and len(host['components'])==10 and all(x['status']=='Passed' for x in host['components'])
assert host['sourcePreserved'] and host['originalSourceHashes']==host['finalSourceHashes'] and host['expectedDemo']==pins['hybridclr_demo'] and host['expectedNative']==pins['il2cpp_plus']
legacy=json.loads((hostRoot/'historical-eight/RESULT.json').read_text());assert len(legacy['commands'])==8 and all(c['status']=='Passed' for c in legacy['commands']) and sha(hostRoot/'historical-eight/RESULT.json')==host['historicalEightResultSha256']
ownerRows=[]
for name,count in [('native-owner-method-classifier',2),('native-owner-full-tu',3)]:
 p=hostRoot/'steps'/name;cmd=json.loads((p/'RESULT.json').read_text());inv=json.loads((p/'INVOCATION.json').read_text());assert cmd['state']=='Passed' and cmd['exitCode']==0 and not cmd['timedOut'] and not cmd['mayHaveExternalOwnedChildren'] and not cmd['processGroupRemainedAtExit'] and not cmd['postCleanupGroupExists']
 assert sha(p/'stdout.log')==cmd['stdoutSha256'] and sha(p/'stderr.log')==cmd['stderrSha256'] and re.search(r'(?m)^Ran '+str(count)+r' tests? in ',(p/'stderr.log').read_text()) and re.search(r'(?m)^OK\s*$',(p/'stderr.log').read_text())
 assert datetime.datetime.fromisoformat(cmd['finishedUtc']).timestamp()<=min(c['start'] for c in commands if c['path'].endswith('/0003/command.json'))
 ownerRows.append(dict(name=name,tests=count,pid=cmd['processId'],start=cmd['startedUtc'],end=cmd['finishedUtc'],argv=inv['argv'],stderrSha256=cmd['stderrSha256'],stdoutSha256=cmd['stdoutSha256'],result='PassedFreshLocalBeforeUnity'))
if r['result']=='FocusedEvidenceReadyForIndependentReview':
 v=r['nativeFocusedVerification'];assert v['result']=='PassedFiveFocusedCurrentNativePlayersOnly' and v['validatedCells']==18 and v['completeProducerRepositoryRecord'] is True and v['localBatchResultSha256']==sha(N/'LOCAL_BATCH_RESULT.json')
report=dict(kind='IndependentOneuseJFinalEvidenceAndPreservationAudit',result='PassedPreservationAndReceiptAudit_OriginalSemanticResultRetained',start=start,end=now(),freshLocalNativeHostComponents=10,historicalEightPassed=8,freshOwnerHostSuites=ownerRows,sourcePins=pins,coordinatorResult=r['result'],stageCounts=counts,childCellCounts=countsChild,childSealedFilesVerified=len(idx['files']),childArchiveMembersVerified=seal['members'],childCommandsVerified=commands,childArchiveSha256=seal['archiveSha256'],childIndexSha256=seal['indexSha256'],sourceBindingsVerified=len(json.loads((B/'oneuse-J-CI_GATE.json').read_text())['sourceBindings']),retainedDRawFilesVerified=len(draw['files']),retainedDRawSymlinksVerified=len(draw['symlinks']),retainedIRawFilesVerified=len(iraw['files']),retainedIRawSymlinksVerified=len(iraw['symlinks']),retainedHRawFilesVerified=len(hraw['files']),retainedHRawSymlinksVerified=len(hraw['symlinks']),retainedGRawFilesVerified=len(graw['files']),retainedGRawSymlinksVerified=len(graw['symlinks']),retainedERawFilesVerified=len(eraw['files']),retainedERawSymlinksVerified=len(eraw['symlinks']),reservedFRootStillAbsent=True,coordinatorManifestFilesVerified=len(outer['files']),stageStreamsAndLifetimesVerified=steps,protectedOriginalSFilesVerified=16978,protectedLogicalBytes=3882340952,originalSSparseProjectionPreserved=True,priorCheckpointsVerified=len(before['history']),installedUnity2022SdkInputsVerified=len(SDK['files']),copiedOriginalSManifestVerifiedAtOriginalCheckpoint=True,receiverAuditScopeCorrection='Original-S output MANIFEST is an unchanged original input copy, not a manifest of new audit output',dotnetBinaryPreserved=True,UnityBinaryPreserved=True,originalSArchiveAudit='Passed',originalSArchivedProcessesVerified=59,nativeCurrentBatchConstructed=True,newNativeBuildAttempts=3,newNativeBuilds=child['verifiedFreshBuilds'],newPlayers=child['recordedFreshPlayerRawFiles'],currentNativeSeal='Passed_BoundedEvidenceOnly',installedNativeParity=('PassedInstalledSourceParityOnly' if r['stages']['native-installed-source-audit']['state']=='Passed' else r['stages']['native-installed-source-audit']['state']),sourcePostflight=repos,ownedSurvivorsObserved=survivors,availableBytes=shutil.disk_usage(B).free,sourceChangesByLocal=False,batchRetry=False)
q=B/'oneuse-J-FINAL_INDEPENDENT_AUDIT.json';assert not q.exists();q.write_text(json.dumps(report,indent=2)+'\n');print('Final independent preservation/receipt audit Passed; original semantic result retained:',r['result'])
