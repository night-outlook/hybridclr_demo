from pathlib import Path
import json,hashlib,subprocess,datetime,os,sys
R=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-CapturedGeneric08');B=R.parent;W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';S=B/'OriginalS-20261026-fc55-oneuse';T=Path('/Users/ah/GitHub/hybridclr_cleanup_receipts/user-retire-runtime17-20261106');phase=sys.argv[1];assert phase in ['BEFORE','AFTER'];out=R/('PRESERVATION_'+phase+'.json');assert not out.exists();load=lambda p:json.loads(p.read_text());now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();start=now()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
H='26843412eda7034cd91c0754bdcde16d5517d814';scope=load(T/'APPROVED_SCOPE.json')
assert sha(T/'APPROVED_SCOPE.json')=='43fd0b63568c391eef04b23da01b756692043f83ee53783f328cf45f92fa7b5f'
assert len(scope['exactRoots'])==17 and len(scope['duplicateFiles'])==40
for item in scope['duplicateFiles']:
 q=Path(item if isinstance(item,str) else item['path'])
 assert any(q.is_relative_to(Path(root)) for root in scope['exactRoots']) and not q.exists() and not q.is_symlink()

for p in scope['exactRoots']:assert not Path(p).exists() and not Path(p).is_symlink()
remaining=load(T/'PROTECTED_AFTER.json');outside=[]; metadata=[]
for row in remaining['topLevelOutsideEntries']:
 p=Path(row['path']);s=p.lstat();assert s.st_ino==row['inode'] and s.st_mode==row['mode'] and s.st_size==row['bytes'],p
 if s.st_mtime_ns!=row['mtimeNs']:
  assert p==B/'initializer-05-PUBLICATION_RECEIPT.json' and sha(p)==row['sha256']=='8c186c8efd2c3df89874dce3ab23364736726ec9777c28dd5486b190b29d7fae',p
  metadata.append({'path':str(p),'originalMtimeNs':row['mtimeNs'],'observedMtimeNs':s.st_mtime_ns,'sha256':row['sha256'],'reason':'Documented byte-identical restoration in oneuse-05 PUBLICATION_NAMESPACE.json'})
 if row['kind']=='file':assert sha(p)==row['sha256']
 if row['kind']=='symlink':assert os.readlink(p)==row['linkTarget']
 outside.append(row['path'])
protected=load(B/'oneuse-C-PROTECTED_BEFORE.json')
for row in protected['rows']:
 p=S/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
history=[]
for row in remaining['publishedCheckpointsVerified']:
 p=Path(row['root']);manifest=p/'MANIFEST.sha256';assert sha(manifest)==row['manifestSha256'];count=0
 for line in manifest.read_text().splitlines():
  h,rel=line.split('  ',1);assert sha(p/rel)==h;count+=1
 history.append({'root':str(p),'manifestSha256':sha(manifest),'filesVerified':count})
p=D/'Docs/AssemblyShadow/History/M07R/R03/storage-retirement-20261106-runtime17';manifest=p/'MANIFEST.sha256';count=0
for line in manifest.read_text().splitlines():
 h,rel=line.split('  ',1);assert sha(p/rel)==h;count+=1
history.append({'root':str(p),'manifestSha256':sha(manifest),'filesVerified':count})
assert sha(manifest)=='8b129427ed6ade138dc862795c7ffa06fecf570efe5d9ebb1898d7100bf4f222'
prior=load(B/'initializer-05-runtime-PUBLICATION_RECEIPT.json')
q=Path(prior['checkpoint']);manifest=q/'MANIFEST.sha256';assert sha(manifest)==prior['checkpointManifestSha256']
count=0
for line in manifest.read_text().splitlines():
 h,rel=line.split('  ',1);assert sha(q/rel)==h;count+=1
history.append({'root':str(q),'manifestSha256':sha(manifest),'filesVerified':count})
priorRaw=[]
for label in ['RAW_MANIFEST.json','HOST_RAW_MANIFEST.json']:
 m=q/'local-evidence'/label
 inv=load(m); root=Path(inv['root'])
 for row in inv['files']:
  f=root/row['path'];assert f.is_file() and not f.is_symlink() and f.stat().st_size==row['bytes'] and sha(f)==row['sha256'],f
 for row in inv['symlinks']:
  f=root/row['path'];assert f.is_symlink() and os.readlink(f)==row['target'],f
 priorRaw.append({'root':str(root),'manifestSha256':sha(m),'files':len(inv['files']),'symlinks':len(inv['symlinks'])})
prior=load(B/'initializer-06-runtime-PUBLICATION_RECEIPT.json')
q=Path(prior['checkpoint']);manifest=q/'MANIFEST.sha256';assert sha(manifest)==prior['checkpointManifestSha256']
count=0
for line in manifest.read_text().splitlines():
 h,rel=line.split('  ',1);assert sha(q/rel)==h;count+=1
history.append({'root':str(q),'manifestSha256':sha(manifest),'filesVerified':count})

for label in ['RAW_MANIFEST.json','HOST_RAW_MANIFEST.json']:
 m=q/'local-evidence'/label
 inv=load(m); root=Path(inv['root'])
 for row in inv['files']:
  f=root/row['path'];assert f.is_file() and not f.is_symlink() and f.stat().st_size==row['bytes'] and sha(f)==row['sha256'],f
 for row in inv['symlinks']:
  f=root/row['path'];assert f.is_symlink() and os.readlink(f)==row['target'],f
 priorRaw.append({'root':str(root),'manifestSha256':sha(m),'files':len(inv['files']),'symlinks':len(inv['symlinks'])})
prior=load(B/'initializer-07-runtime-PUBLICATION_RECEIPT.json')
q=Path(prior['checkpoint']);manifest=q/'MANIFEST.sha256';assert sha(manifest)==prior['checkpointManifestSha256']
count=0
for line in manifest.read_text().splitlines():
 h,rel=line.split('  ',1);assert sha(q/rel)==h;count+=1
history.append({'root':str(q),'manifestSha256':sha(manifest),'filesVerified':count})

for label in ['RAW_MANIFEST.json','HOST_RAW_MANIFEST.json']:
 m=q/'local-evidence'/label
 inv=load(m); root=Path(inv['root'])
 for row in inv['files']:
  f=root/row['path'];assert f.is_file() and not f.is_symlink() and f.stat().st_size==row['bytes'] and sha(f)==row['sha256'],f
 for row in inv['symlinks']:
  f=root/row['path'];assert f.is_symlink() and os.readlink(f)==row['target'],f
 priorRaw.append({'root':str(root),'manifestSha256':sha(m),'files':len(inv['files']),'symlinks':len(inv['symlinks'])})
sdk=load(B/'Preflight-R03-P1-ADMITTED-EXECUTION-20261023-b7e3/SDK_BEFORE.json')
for row in sdk['files']:
 p=Path(row['path']);assert p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
sources=load(B/'initializer-04-CI_GATE.json')['sourceBindings']
sourceTransitions=[]
for row in sources:
 q=W/row['repository']/row['path'];h=sha(q)
 if h!=row['sha256']:
  assert row['repository']=='hybridclr_demo',q
  old=subprocess.check_output(['git','-C',str(D),'show','eeeec3ba574047c06b5b853e58a5b594e80c37ae:'+row['path']])
  new=subprocess.check_output(['git','-C',str(D),'show',H+':'+row['path']])
  assert hashlib.sha256(old).hexdigest()==row['sha256'] and hashlib.sha256(new).hexdigest()==h,q
  sourceTransitions.append({'path':row['path'],'previousSha256':row['sha256'],'pinnedSha256':h})
recovery=B/'Initializer05-CapacityAnalysis-20261106/StrippedAOTDllsTempProj.recovery.tar.gz';assert sha(recovery)=='4b5e3b8eb84646bd5025f755f0f23436adf359cbaf9ff850983a2837fe16a727'
compression=load(B/'backup-compression-20261106-RESULT.json');assert sha(Path(compression['originalManifest']))==compression['originalManifestSha256']
for row in compression['rows']:assert sha(Path(row['compressedPath']))==row['compressedSha256']
expected={'hybridclr_demo':H,'hybridclr':'4b2774b066cfc6afd77a8c8aded6bda7ea574f55','hybridclr_unity':'948c0e3b4f8891481301770115e8ba4945eea6de','il2cpp_plus':'41764ae1eeefb33b05966e7f7676e52aae39c340'};repos={}
for name,h in expected.items():
 p=W/name;rows=[]
 for a in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--short','--untracked-files=all'],['remote','-v'],['worktree','list','--porcelain'],['submodule','status','--recursive'],['ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1']]:
  t=now();args=['git','-C',str(p),*a];r=subprocess.run(args,capture_output=True,text=True,timeout=120);rows.append({'command':args,'startUtc':t,'endUtc':now(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0
 assert rows[0]['stdout'].strip()==str(p) and rows[1]['stdout'].strip()=='codex/assembly-shadow-r01b-h1' and rows[2]['stdout'].strip()==h and not rows[3]['stdout'] and rows[-1]['stdout'].split()[0]==h
 repos[name]=rows
assert subprocess.check_output(['git','-C',str(S),'rev-parse','HEAD'],text=True).strip()=='fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b' and not subprocess.check_output(['git','-C',str(S),'status','--short'],text=True)
O=B/'R03IR-CapturedGeneric-20261109-oneuse-08';HR=O.with_name(O.name+'-native-host-raw')
if phase=='BEFORE':assert not O.exists() and not HR.exists()
x={'original05Raw':priorRaw,'authorizedSourceTransitions':sourceTransitions,'metadataDrift':metadata,'kind':'RemainingCustodyPreservationAfterExplicitOwnerRetirement','phase':phase,'startUtc':start,'endUtc':now(),'result':'PassedRemainingProtectedInputs_Exact17RetiredRemainUnavailable','sourcePins':expected,'sourceRepositories':repos,'remainingOutsideTopLevelEntriesVerified':len(outside),'outsideDirectoryInteriors':'Only frozen-C audit separately covers its original map; other outside raw directory metadata not represented as full new byte audit','originalSFilesVerified':len(protected['rows']),'history':history,'installedSdkFilesVerified':len(sdk['files']),'retainedSourceBindingsVerified':len(sources),'retiredExact17States':[{'path':p,'state':'Unavailable_UserAuthorizedRetirement'} for p in scope['exactRoots']],'noAdditionalDisappearanceExcused':True,'retainedRecoveryArchiveSha256':sha(recovery),'gzipTransitionStillVerified':True,'root':str(O),'hostRoot':str(HR),'runRootPresent':O.exists(),'hostRootPresent':HR.exists(),'R03Accepted':False,'runtimeAcceptance':False}
if phase=='AFTER':
 before=load(R/'PRESERVATION_BEFORE.json');assert before['original05Raw']==priorRaw and before['metadataDrift']==metadata and before['authorizedSourceTransitions']==sourceTransitions and before['history']==history and before['sourcePins']==expected and before['retiredExact17States']==x['retiredExact17States'];x['independentlyRepeatedBeforeAfterComparison']='Passed'
out.write_text(json.dumps(x,indent=2)+'\n');print('Preservation',phase,'Passed',len(history),'published checkpoints;16978 S;2405 SDK;1135 outside entries;17 intentionally unavailable',flush=True)
