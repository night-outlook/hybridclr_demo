from pathlib import Path
import json,hashlib,subprocess,datetime,tarfile,os,stat
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');D=B.parent/'assembly_shadow_h1r/hybridclr_demo';target=D/'HybridCLRData/StrippedAOTDllsTempProj';out=B/'Initializer05-CapacityAnalysis-20261106';assert not out.exists()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();start=now()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
assert target.resolve()==target and target.is_dir() and not target.is_symlink()
assert subprocess.check_output(['git','-C',str(D),'rev-parse','HEAD'],text=True).strip()=='85fb825ccd70291afa3eaa279cc6280703ed58f7'
assert not subprocess.check_output(['git','-C',str(D),'ls-files','--',str(target.relative_to(D))],text=True)
assert not subprocess.check_output(['git','-C',str(D),'status','--porcelain=v1','--untracked-files=all'],text=True)
ps=subprocess.check_output(['ps','-axo','comm='],text=True);assert not [p for p in ps.splitlines() if Path(p.strip()).name in ('Unity','bee_backend','il2cpp','dotnet')]
def inventory():
 rows=[]
 for p in [target,*sorted(target.rglob('*'))]:
  s=p.lstat();assert not p.is_symlink() and (p.is_file() or p.is_dir());rows.append({'path':str(p.relative_to(target.parent)),'kind':'file' if p.is_file() else 'directory','bytes':s.st_size if p.is_file() else None,'mode':stat.S_IMODE(s.st_mode),'mtimeNs':s.st_mtime_ns,'sha256':sha(p) if p.is_file() else None})
 return rows
before=inventory();assert len([x for x in before if x['kind']=='file'])==2664
free=lambda:int(os.statvfs(B).f_bavail)*int(os.statvfs(B).f_frsize)
freeBefore=free();out.mkdir();archive=out/'StrippedAOTDllsTempProj.recovery.tar.gz';args=['/usr/bin/tar','-czf',str(archive),'-C',str(target.parent),target.name];r=subprocess.run(args,capture_output=True,text=True,timeout=180)
(out/'ARCHIVE_COMMAND.json').write_text(json.dumps({'command':args,'startUtc':start,'endUtc':now(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');assert r.returncode==0
expected={x['path']:x for x in before if x['kind']=='file'};seen=set();macMetadata=[]
with tarfile.open(archive,'r:gz') as tar:
 for member in tar:
  p=Path(member.name);assert not p.is_absolute() and '..' not in p.parts
  if member.isfile():
   stream=tar.extractfile(member);h=hashlib.sha256();n=0
   for block in iter(lambda:stream.read(1024*1024),b''):h.update(block);n+=len(block)
   if p.name.startswith('._'):
    macMetadata.append({'path':member.name,'bytes':n,'sha256':h.hexdigest()});continue
   assert member.name in expected and member.name not in seen;row=expected[member.name];assert n==row['bytes'] and h.hexdigest()==row['sha256'];seen.add(member.name)
  else:assert member.isdir()
assert set(expected)==seen;after=inventory();assert before==after
(out/'INVENTORY_BEFORE.json').write_text(json.dumps({'root':str(target),'rows':before},indent=2)+'\n');(out/'INVENTORY_AFTER.json').write_text(json.dumps({'root':str(target),'rows':after},indent=2)+'\n')
receipt={'kind':'PreparedRecoverableCapacityOption_NotDeletionApproval','result':'BackupAndSourcePreservationVerified','startUtc':start,'endUtc':now(),'target':str(target),'archive':str(archive),'archiveBytes':archive.stat().st_size,'archiveSha256':sha(archive),'regularFilesVerified':len(seen),'logicalBytesVerified':sum(r['bytes'] for r in expected.values()),'nativeTarMacMetadata':macMetadata,'sourceBytesAndMetadataUnchanged':True,'sourceTrackedFiles':0,'freeBytesBefore':freeBefore,'freeBytesAfterBackup':free(),'device':target.stat().st_dev,'sourceWorkspaceDefaultProtection':'RequiresExplicitUserScopedDispositionBeforeAnyDeletion','reclaimableBytes':'Unknown_APFSSharingSnapshots','deletionApproved':False,'deletionOperations':0,'movedExistingData':False,'UnityOrPlayerLaunched':False,'runtimeRunnerInvocations':0,'proposedAction':'Only after explicit user approval, remove exactly target following final unchanged-inventory and backup checks; preserve all siblings, sources, SDK, evidence and recovery archive; measure actual capacity again.'}
(out/'BACKUP_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');(B/'initializer-05-CLEANUP_OPTION_BACKUP.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
