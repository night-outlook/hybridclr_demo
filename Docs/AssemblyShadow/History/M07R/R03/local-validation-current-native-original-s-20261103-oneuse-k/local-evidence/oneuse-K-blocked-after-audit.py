from pathlib import Path
import json,hashlib,subprocess,datetime,os,shutil,tarfile
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';S=B/'OriginalS-20261026-fc55-oneuse';O=B/'R03IR-CurrentNativeOriginalS-20261103-oneuse-K';now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();start=now();load=lambda p:json.loads(p.read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
r=load(O/'RESULT.json');assert r['result']=='ReturnRequired' and r['stages']['native-host-diagnostics']['state']=='Failed' and r['stages']['current-native-players']['state']==r['stages']['native-installed-source-audit']['state']=='Blocked'
assert not (O/'current-native').exists()  and not (O/'installed-native-vm-parity.json').exists()
outer=load(O/'COORDINATOR_MANIFEST.json');assert outer['kind']=='R03IRCoordinatorReceiptsOnly' and outer['externalChildEvidenceSealedHere'] is False
for row in outer['files']:p=O/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
steps=[]
for p in sorted((O/'steps').glob('*/RESULT.json')):
 x=load(p);assert sha(p.parent/'stdout.log')==x['stdoutSha256'] and sha(p.parent/'stderr.log')==x['stderrSha256'] and not x['timedOut'] and not x['mayHaveExternalOwnedChildren'] and not x['processGroupRemainedAtExit'] and not x['postCleanupGroupExists'];steps.append(dict(name=p.parent.name,state=x['state'],pid=x['processId'],exit=x['exitCode'],start=x['startedUtc'],end=x['finishedUtc'],receiptSha256=sha(p)))
assert len(steps)==8
assert load(O/'original-s-audit/audit.json')['archiveMembers']==15713 and load(O/'original-s-audit/audit.json')['cells']==90 and load(O/'original-s-audit/audit.json')['result']=='Passed'
assert load(O/'original-s-process-joins/process-joins.json')['result']=='Passed' and load(O/'original-s-process-joins/process-joins.json')['totalPlayerReceipts']==59
for line in (O/'original-s-audit/MANIFEST.sha256').read_text().splitlines():
 h,rel=line.split('  ',1);assert sha(S/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready'/rel)==h
protected=load(B/'oneuse-C-PROTECTED_BEFORE.json')
for row in protected['rows']:
 p=S/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
before=load(B/'oneuse-K-PRESERVATION_BEFORE.json')
for item in before['history']:
 root=Path(item['root']);assert sha(root/'MANIFEST.sha256')==item['manifestSha256']
 for row in item['files']:assert sha(root/row['path'])==row['sha256']
raws=[]
for label in ['D','E','G','H','I','J']:
 m=load(B/f'oneuse-{label}-RAW_MANIFEST.json');root=Path(m['root'])
 for row in m['files']:
  p=root/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
 for row in m['symlinks']:assert (root/row['path']).is_symlink() and os.readlink(root/row['path'])==row['target']
 raws.append(dict(cycle=label,filesVerified=len(m['files']),symlinksVerified=len(m['symlinks']),bytesVerified=m['totalBytes']))
sdk=load(B/'Preflight-R03-P1-ADMITTED-EXECUTION-20261023-b7e3/SDK_BEFORE.json')
for row in sdk['files']:
 p=Path(row['path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
env=load(B/'oneuse-K-ENVIRONMENT_BEFORE.json');assert sha(Path(env['dotnet']))==env['dotnetSha256'] and sha(Path(env['Unity2022']))==env['unitySha256']
source=load(B/'oneuse-K-CI_GATE.json')['sourceBindings']
for row in source:assert sha(W/row['repository']/row['path'])==row['sha256']
pins=before['sourcePins'];repos={}
for n in [*pins,'OriginalS']:
 p=S if n=='OriginalS' else W/n;rows=[]
 for a in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--porcelain=v1','--untracked-files=all'],['remote','-v'],['worktree','list','--porcelain'],['submodule','status','--recursive']]+([] if n=='OriginalS' else [['ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1']]):
  t=now();v=subprocess.run(['git','-C',str(p),*a],capture_output=True,text=True,timeout=120);rows.append(dict(argv=v.args,start=t,end=now(),exit=v.returncode,stdout=v.stdout,stderr=v.stderr));assert v.returncode==0
 expected='fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b' if n=='OriginalS' else pins[n];assert rows[0]['stdout'].strip()==str(p) and rows[2]['stdout'].strip()==expected and not rows[3]['stdout']
 if n!='OriginalS':assert rows[1]['stdout'].strip()=='codex/assembly-shadow-r01b-h1' and rows[-1]['stdout'].split()[0]==expected
 else:assert not rows[1]['stdout']
 repos[n]=rows
assert subprocess.check_output(['git','-C',str(S),'config','core.sparseCheckout'],text=True).strip()=='true'
assert not (B/'R03IR-CurrentNativeOriginalS-20261102-oneuse-F').exists()
survivors=[]
for l in subprocess.check_output(['/bin/ps','-axo','pid=,ppid=,pgid=,command='],text=True).splitlines():
 f=l.strip().split(None,3)
 if len(f)==4 and str(O) in f[3] and any(k in f[3].split(' ',1)[0] for k in ['Unity','dotnet','clang','python']):survivors.append(l)
assert not survivors
counts={}
for s in r['stages'].values():counts[s['state']]=counts.get(s['state'],0)+1
report=dict(kind='IndependentOneuseKFailedHostGateAndPreservationAudit',result='PassedPreservationAndReceiptAudit_OriginalFailureRetained',start=start,end=now(),sourcePins=pins,coordinatorResult=r['result'],stageCounts=counts,coordinatorManifestFilesVerified=len(outer['files']),stageStreamsAndLifetimesVerified=steps,protectedOriginalSFilesVerified=16978,protectedLogicalBytes=3882340952,priorCheckpointsVerified=len(before['history']),retainedRawInventoriesVerified=raws,installedUnity2022SdkInputsVerified=len(sdk['files']),sourceBindingsVerified=len(source),UnityBinaryPreserved=True,dotnetBinaryPreserved=True,originalSSparseProjectionPreserved=True,copiedOriginalSManifestVerifiedAtOriginalCheckpoint=True,originalSArchiveAudit='PassedHistoricalOnly_15713Members90Cells',originalSArchivedProcessesVerified=59,nativeHostWrapper='Failed',nativeHostComponents=(load(O/'native-host-diagnostics/RESULT.json')['components'] if (O/'native-host-diagnostics/RESULT.json').exists() else []),freshBuilds='Blocked_NotRun',freshPlayers='Blocked_NotRun',installedNativeParity='Blocked_NotRun',nativeCurrentBatchConstructed=False,currentNativeSeal='Unavailable_NoChildConstructed_NoSyntheticSeal',sourcePostflight=repos,ownedSurvivorsObserved=survivors,availableBytes=shutil.disk_usage(B).free,sourceChangesByLocal=False,batchRetry=False)
p=B/'oneuse-K-FINAL_INDEPENDENT_AUDIT.json';assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n');print('After preservation Passed; actual host failure retained; Unity0/Players0; no child seal manufactured')
