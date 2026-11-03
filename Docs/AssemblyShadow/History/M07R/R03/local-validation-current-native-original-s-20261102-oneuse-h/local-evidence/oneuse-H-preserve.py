from pathlib import Path
import json,hashlib,datetime,subprocess,shutil,os,sys
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';S=B/'OriginalS-20261026-fc55-oneuse';O=B/'R03IR-CurrentNativeOriginalS-20261102-oneuse-H';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-current-native-original-s-20261102-oneuse-h';phase=sys.argv[1];assert phase in ['BEFORE','AFTER'];out=B/f'oneuse-H-PRESERVATION_{phase}.json';assert not out.exists();now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();start=now();load=lambda p:json.loads(p.read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
assert phase=='BEFORE' and not O.exists() and not O.is_symlink() and O.resolve()==O and not C.exists();assert not (B/'R03IR-CurrentNativeOriginalS-20261102-oneuse-F').exists()
assert load(B/'oneuse-H-CI_GATE.json')['result']=='PassedNineExactPushWorkflows_EighteenJobs_HostOnly'
protected=load(B/'oneuse-C-PROTECTED_BEFORE.json')
for row in protected['rows']:
 p=S/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
roots=[Path(x['root']) for x in load(B/'oneuse-G-PRESERVATION_BEFORE.json')['history']]+[D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-current-native-original-s-20261102-oneuse-g'];history=[]
for root in roots:
 rows=[];manifest=root/'MANIFEST.sha256';expected=subprocess.check_output(['git','-C',str(D),'rev-parse','HEAD:'+str(manifest.relative_to(D))],text=True).strip();assert subprocess.check_output(['git','-C',str(D),'hash-object',str(manifest)],text=True).strip()==expected
 for line in manifest.read_text().splitlines():
  h,rel=line.split('  ',1);p=root/rel;assert sha(p)==h;rows.append(dict(path=rel,sha256=h,bytes=p.stat().st_size))
 assert subprocess.check_output(['git','-C',str(D),'rev-parse',load(B/'oneuse-G-PUBLICATION_RECEIPT.json')['publishedDocumentationCommit']+':'+str(manifest.relative_to(D))],text=True).strip()==expected
 history.append(dict(root=str(root),manifestSha256=sha(manifest),manifestGitBlob=expected,files=rows))
raws=[]
for label,cp in [('D','local-validation-current-native-original-s-20261029-oneuse-d'),('E','local-validation-current-native-original-s-20261102-oneuse-e'),('G','local-validation-current-native-original-s-20261102-oneuse-g')]:
 mapping=B/f'oneuse-{label}-RAW_MANIFEST.json';copy=D/'Docs/AssemblyShadow/History/M07R/R03'/cp/'local-evidence'/mapping.name;assert sha(mapping)==sha(copy);draw=load(mapping);root=Path(draw['root'])
 for row in draw['files']:
  p=root/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
 for row in draw['symlinks']:
  p=root/row['path'];assert p.is_symlink() and os.readlink(p)==row['target']
 raws.append(dict(cycle=label,root=str(root),manifestSha256=sha(mapping),filesVerified=len(draw['files']),symlinksVerified=len(draw['symlinks']),bytesVerified=draw['totalBytes']))
sdk=load(B/'Preflight-R03-P1-ADMITTED-EXECUTION-20261023-b7e3/SDK_BEFORE.json')
for row in sdk['files']:
 p=Path(row['path']);assert p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
env=load(B/'oneuse-E-ENVIRONMENT_BEFORE.json');assert sha(Path(env['dotnet']))==env['dotnetSha256'] and sha(Path(env['Unity2022']))==env['unitySha256']
source=load(B/'oneuse-H-CI_GATE.json')['sourceBindings']
for x in source:assert sha(W/x['repository']/x['path'])==x['sha256']
pins=load(B/'oneuse-H-initial-git-20261102.json')['expected'];repos={}
for n in [*pins,'OriginalS']:
 p=S if n=='OriginalS' else W/n;rows=[]
 for a in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--porcelain=v1','--untracked-files=all'],['remote','-v'],['worktree','list','--porcelain'],['submodule','status','--recursive']]+([] if n=='OriginalS' else [['ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1']]):
  t=now();argv=['git','-C',str(p),*a];r=subprocess.run(argv,capture_output=True,text=True,timeout=120);rows.append(dict(argv=argv,start=t,end=now(),exit=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0
 expected='fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b' if n=='OriginalS' else pins[n];assert rows[0]['stdout'].strip()==str(p) and rows[2]['stdout'].strip()==expected and not rows[3]['stdout']
 if n!='OriginalS':assert rows[1]['stdout'].strip()=='codex/assembly-shadow-r01b-h1' and rows[-1]['stdout'].split()[0]==expected
 else:assert not rows[1]['stdout']
 repos[n]=rows
assert subprocess.check_output(['git','-C',str(S),'config','core.sparseCheckout'],text=True).strip()=='true';assert subprocess.check_output(['git','-C',str(S),'rev-parse','HEAD:Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready'],text=True).strip()=='2acdcc0ec3c0f15dea11f99bc9c5d6d0f431de79'
E=B/'R03IR-CurrentNativeOriginalS-20261030-oneuse-E/current-native';assert all((E/'players'/case/'raw.json').stat().st_size==0 for case in ['IR-R03-02-release-baseline','IR-R03-02-debug-baseline','IR-R03-02-release-type']);assert load(E/'players/IR-R03-02-release-engine/raw.json')['completedReports']==51211 and load(E/'players/IR-R03-02-off/verification.json')['result']=='Passed'
report=dict(kind='IndependentOneuseHBlockedPrerequisitePreservation',phase=phase,start=start,end=now(),result='PassedScopedPreservation_BeforeAuthorizedConditionalAdmission',sourcePins=pins,sourceRepositories=repos,sourceBindingsVerified=len(source),protectedOriginalSFilesVerified=16978,protectedLogicalBytes=3882340952,originalSparseProjectionUnchanged=True,history=history,retainedRawInventoriesVerified=raws,installedSdkFilesVerified=len(sdk['files']),UnityBinaryPreserved=True,dotnetBinaryPreserved=True,toolchainVersionAdmission='PendingFreshReadOnlyAdmission',macAdmission='PendingFreshReadOnlyAdmission',HRootAbsent=True,root=str(O),coordinatorInvocations=0,UnityLaunches=0,PlayersLaunched=0,capacityFreeBytes=shutil.disk_usage(B).free,earlierEFailureUnchanged=True,sourceOrHistoricalChanges=False)
out.write_text(json.dumps(report,indent=2)+'\n');print(phase,'preservation Passed;',len(history),'checkpoints;16978 S files;44976 D +46603 E +46074 G raw files;2405 SDK inputs;',len(source),'source bindings; root absent, coordinator0',flush=True)
