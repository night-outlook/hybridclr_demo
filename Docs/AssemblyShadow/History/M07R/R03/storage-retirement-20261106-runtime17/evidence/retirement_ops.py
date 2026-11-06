from pathlib import Path
import json,datetime,hashlib,gzip,stat,os,sys,subprocess,shutil
R=Path('/Users/ah/GitHub/hybridclr_cleanup_receipts/user-retire-runtime17-20261106');B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';S=B/'OriginalS-20261026-fc55-oneuse'
scope=json.loads((R/'APPROVED_SCOPE.json').read_text());roots=[Path(p) for p in scope['exactRoots']];now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();load=lambda p:json.loads(p.read_text())
def write(name,x):
 with (R/name).open('x') as f:json.dump(x,f,indent=2,ensure_ascii=False);f.write('\n')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def free():
 x=os.statvfs(B);return x.f_bavail*x.f_frsize
def guards(require_present=True):
 assert sha(R/'APPROVED_SCOPE.json')=='43fd0b63568c391eef04b23da01b756692043f83ee53783f328cf45f92fa7b5f';assert len(roots)==17 and len(set(roots))==17 and load(R/'SCOPE_REVIEW.json')['result']=='PASS'
 for p in roots:
  assert p.parent==B and p.resolve()==p and not p.is_symlink() and p!=S
  if require_present:assert p.is_dir() and p.stat().st_dev==B.stat().st_dev and not os.path.ismount(p)
 ps=subprocess.check_output(['ps','-axo','pid=,comm='],text=True);writers=[]
 for line in ps.splitlines():
  bits=line.strip().split(maxsplit=1)
  if len(bits)==2 and Path(bits[1]).name in ('Unity','bee_backend','il2cpp','dotnet','R03Isolated','R03Initializer'):writers.append(line)
 assert not writers,writers
 return {'scopeHashVerified':True,'roots':17,'noConflictingBuildOrPlayerProcesses':True,'device':B.stat().st_dev}
def walk(root):
 yield root
 for cur,dirs,files in os.walk(root,followlinks=False):
  dirs.sort();files.sort()
  for name in dirs+files:yield Path(cur)/name
def meta(p,root):
 s=p.lstat();assert s.st_dev==B.stat().st_dev
 kind='file' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'symlink' if stat.S_ISLNK(s.st_mode) else 'fifo' if stat.S_ISFIFO(s.st_mode) else 'socket' if stat.S_ISSOCK(s.st_mode) else 'other'
 assert kind!='other',(p,s.st_mode)
 return {'path':str(p.relative_to(root)),'kind':kind,'device':s.st_dev,'inode':s.st_ino,'mode':s.st_mode,'uid':s.st_uid,'gid':s.st_gid,'mtimeNs':s.st_mtime_ns,'bytes':s.st_size if kind=='file' else None,'allocatedBytes':s.st_blocks*512 if kind=='file' else None,'linkTarget':os.readlink(p) if kind=='symlink' else None}
def inventory():
 start=now();g=guards();assert not (R/'TARGET_INVENTORY.jsonl.gz').exists();summaries=[];duplicates={x['path']:x for x in scope['duplicateFiles']};matched=0
 with (R/'TARGET_INVENTORY.jsonl.gz').open('xb') as raw:
  with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as z:
   for root in roots:
    fingerprint=hashlib.sha256();counts={};total=allocated=0
    for p in walk(root):
     row=meta(p,root);fingerprint.update(json.dumps(row,sort_keys=True,separators=(',',':')).encode()+b'\n');counts[row['kind']]=counts.get(row['kind'],0)+1
     if row['kind']=='file':
      digest=sha(p);total+=row['bytes'];allocated+=row['allocatedBytes'];row['sha256']=digest
      if str(p) in duplicates:
       assert digest==duplicates[str(p)]['sha256'] and row['bytes']==duplicates[str(p)]['bytes'];matched+=1
     row['root']=str(root);z.write((json.dumps(row,sort_keys=True,separators=(',',':'))+'\n').encode())
    summaries.append({'root':str(root),'counts':counts,'logicalFileBytes':total,'allocatedFileBytesEstimate':allocated,'metadataFingerprint':fingerprint.hexdigest()});print('inventoried',root.name,counts.get('file',0),'files',round(total/1024**3,3),'GiB',flush=True)
 assert matched==40
 x={'kind':'MetadataOnlyInventoryForApprovedPermanentRetirement','startUtc':start,'endUtc':now(),'result':'PassedAllSelectedPayloadHashesAndBoundaries','guard':g,'roots':summaries,'fileCount':sum(r['counts'].get('file',0) for r in summaries),'symlinkCount':sum(r['counts'].get('symlink',0) for r in summaries),'logicalFileBytes':sum(r['logicalFileBytes'] for r in summaries),'allocatedFileBytesEstimate':sum(r['allocatedFileBytesEstimate'] for r in summaries),'inventory':str(R/'TARGET_INVENTORY.jsonl.gz'),'inventorySha256':sha(R/'TARGET_INVENTORY.jsonl.gz'),'fortyDuplicateFilesHashVerified':40,'recoveryPayloadArchiveCreated':False,'userExplicitlyForfeitsThese40CopiesAndSelectedUniqueRawEvidence':True};write('TARGET_INVENTORY_RESULT.json',x)
def protected(phase):
 assert phase in ('BEFORE','AFTER');start=now();outside=[]
 for p in sorted(B.iterdir()):
  if p in roots:continue
  s=p.lstat();row={'path':str(p),'kind':'symlink' if p.is_symlink() else 'directory' if p.is_dir() else 'file','inode':s.st_ino,'mode':s.st_mode,'mtimeNs':s.st_mtime_ns,'bytes':s.st_size,'linkTarget':os.readlink(p) if p.is_symlink() else None}
  if row['kind']=='file':row['sha256']=sha(p)
  outside.append(row)
 original=load(B/'oneuse-C-PROTECTED_BEFORE.json')
 for row in original['rows']:
  p=S/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
 history=[]
 for row in load(B/'initializer-05-PRESERVATION_POST_CLEANUP.json')['history']:
  root=Path(row['root']);manifest=root/'MANIFEST.sha256';assert sha(manifest)==row['manifestSha256'];n=0
  for line in manifest.read_text().splitlines():
   h,rel=line.split('  ',1);assert sha(root/rel)==h;n+=1
  history.append({'root':str(root),'manifestSha256':sha(manifest),'filesVerified':n})
 latest=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261106-oneuse-05-capacity-readiness';n=0
 for line in (latest/'MANIFEST.sha256').read_text().splitlines():
  h,rel=line.split('  ',1);assert sha(latest/rel)==h;n+=1
 history.append({'root':str(latest),'manifestSha256':sha(latest/'MANIFEST.sha256'),'filesVerified':n})
 sdk=load(B/'Preflight-R03-P1-ADMITTED-EXECUTION-20261023-b7e3/SDK_BEFORE.json')
 for row in sdk['files']:
  p=Path(row['path']);assert p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
 repos={}
 for name in ['hybridclr_demo','hybridclr','hybridclr_unity','il2cpp_plus','OriginalS']:
  p=S if name=='OriginalS' else W/name;rows=[]
  for args in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--short','--untracked-files=all'],['remote','-v'],['worktree','list','--porcelain']]:
   a=['git','-C',str(p),*args];r=subprocess.run(a,capture_output=True,text=True,timeout=120);assert r.returncode==0;rows.append({'command':a,'stdout':r.stdout,'stderr':r.stderr,'exitCode':r.returncode})
  assert rows[0]['stdout'].strip()==str(p) and not rows[3]['stdout'];repos[name]=rows
 assert repos['OriginalS'][2]['stdout'].strip()=='fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b'
 gzipTransition=load(B/'backup-compression-20261106-RESULT.json')
 assert sha(Path(gzipTransition['originalManifest']))==gzipTransition['originalManifestSha256']
 for row in gzipTransition['rows']:assert sha(Path(row['compressedPath']))==row['compressedSha256']
 recovery=B/'Initializer05-CapacityAnalysis-20261106/StrippedAOTDllsTempProj.recovery.tar.gz';assert sha(recovery)=='4b5e3b8eb84646bd5025f755f0f23436adf359cbaf9ff850983a2837fe16a727'
 x={'startUtc':start,'endUtc':now(),'phase':phase,'result':'PassedProtectionChecksWithinDeclaredScope','topLevelOutsideEntries':outside,'outsideDirectoryCheck':'Top-level identity/metadata; selected immutable S/SDK/published checkpoints additionally fully hashed. Not a full byte audit of every unselected raw tree.','originalSFilesVerified':len(original['rows']),'publishedCheckpointsVerified':history,'installedSdkFilesVerified':len(sdk['files']),'sourceRepositories':repos,'retainedRecoveryArchiveSha256':sha(recovery),'gzipTransitionStillVerified':True}
 if phase=='AFTER':
  before=load(R/'PROTECTED_BEFORE.json');assert before['topLevelOutsideEntries']==outside and before['publishedCheckpointsVerified']==history
  for name in repos:assert before['sourceRepositories'][name][2]['stdout']==repos[name][2]['stdout']
  x['independentBeforeAfterComparison']='Passed'
 write('PROTECTED_'+phase+'.json',x);print('Protected',phase,'Passed:',len(outside),'outside entries;16978 S files;19 checkpoints;2405 SDK inputs',flush=True)
def apply():
 start=now();g=guards();assert shutil.rmtree.avoids_symlink_attacks;inv=load(R/'TARGET_INVENTORY_RESULT.json');assert inv['result']=='PassedAllSelectedPayloadHashesAndBoundaries' and sha(R/'TARGET_INVENTORY.jsonl.gz')==inv['inventorySha256'];assert load(R/'PROTECTED_BEFORE.json')['result']=='PassedProtectionChecksWithinDeclaredScope';assert not (R/'DELETE_INTENT.json').exists()
 # Rewalk all names and metadata immediately before removal. Payload hashes
 # are in the first inventory; any changed identity/type/size/time aborts.
 for expected,root in zip(inv['roots'],roots):
  h=hashlib.sha256()
  for p in walk(root):h.update(json.dumps(meta(p,root),sort_keys=True,separators=(',',':')).encode()+b'\n')
  assert h.hexdigest()==expected['metadataFingerprint'],root
 before=free();write('DELETE_INTENT.json',{'timeUtc':now(),'authorization':scope['authorization'],'exactRoots':[str(p) for p in roots],'guard':g,'inventorySha256':inv['inventorySha256'],'metadataRewalkMatchedEverySelectedEntry':True,'freeBytesBefore':before,'noRecoveryArchiveCreatedByExplicitUserDecision':True})
 removed=[]
 try:
  for root in roots:
   t=now();assert root.resolve()==root and root.parent==B and root.is_dir() and not root.is_symlink();shutil.rmtree(root);assert not root.exists() and not root.is_symlink();removed.append(str(root))
   with (R/'DELETIONS.jsonl').open('a') as f:json.dump({'path':str(root),'startUtc':t,'endUtc':now(),'result':'PermanentlyDeleted_UserAuthorized'},f);f.write('\n');f.flush();os.fsync(f.fileno())
   print('deleted',root.name,flush=True)
 except BaseException as e:
  write('DELETE_FAILURE.json',{'timeUtc':now(),'error':repr(e),'removedSoFar':removed,'noAutomaticScopeExpansion':True});raise
 after=free();x={'kind':'UserAuthorizedPermanentRuntimeEvidenceRetirement','startUtc':start,'endUtc':now(),'result':'CompletedExact17RootDeletion','authorization':scope['authorization'],'deletedRoots':removed,'rootCount':len(removed),'deletedRegularFiles':inv['fileCount'],'deletedSymlinks':inv['symlinkCount'],'logicalFileBytesRetired':inv['logicalFileBytes'],'fortyDuplicateCopiesDeleted':all(not Path(r['path']).exists() for r in scope['duplicateFiles']),'copiesPreservedElsewhereByThisAction':0,'recoveryArchiveCreated':False,'payloadsOfSelectedRootsNowUnavailable':True,'currentCustodyDisposition':'PermanentlyDeleted_UserAuthorized','historicalVerdicts':'Original Passed/Failed/Blocked/NotRun verdicts remain historical facts; selected live raw paths no longer provide current verification coverage.','freeBytesBefore':before,'freeBytesAfter':after,'actualAvailableBytesIncrease':after-before,'device':B.stat().st_dev,'owningSourceOrInstalledSdkChanges':False,'selectedBatchSdkAndBuildCopiesDeletedAsAuthorized':True,'UnityLaunches':0,'runtimeBatchInvocations':0};write('RESULT.json',x);print('actual freed GiB',(after-before)/1024**3,'free GiB',after/1024**3,flush=True)
if __name__=='__main__':
 command=sys.argv[1]
 if command=='inventory':inventory()
 elif command=='protect-before':protected('BEFORE')
 elif command=='apply':apply()
 elif command=='protect-after':protected('AFTER')
 else:raise ValueError(command)
