from pathlib import Path
import json,datetime,hashlib,stat,os,subprocess,tarfile,shutil
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');D=B.parent/'assembly_shadow_h1r/hybridclr_demo';target=D/'HybridCLRData/StrippedAOTDllsTempProj';backup=B/'Initializer05-CapacityAnalysis-20261106';result=B/'initializer-05-APPROVED_CLEANUP_RESULT.json';assert not result.exists()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();start=now();load=lambda p:json.loads(p.read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def free():
 s=os.statvfs(B);return int(s.f_bavail)*int(s.f_frsize)
approval=load(B/'initializer-05-APPROVED_CLEANUP_SOURCE_PREFLIGHT.json');assert approval['result']=='PassedExactCleanSourceAndRemoteHeads' and approval['userApproval']['answer']=='批准，仅清理这个目录' and approval['userApproval']['scope']==str(target)
assert target.resolve()==target and target.is_dir() and not target.is_symlink() and target.stat().st_dev==B.stat().st_dev
assert shutil.rmtree.avoids_symlink_attacks
assert not subprocess.check_output(['git','-C',str(D),'ls-files','--',str(target.relative_to(D))],text=True)
assert not subprocess.check_output(['git','-C',str(D),'status','--porcelain=v1','--untracked-files=all'],text=True)
ps=subprocess.check_output(['ps','-axo','comm='],text=True);assert not [p for p in ps.splitlines() if Path(p.strip()).name in ('Unity','bee_backend','il2cpp','dotnet')]
receipt=load(backup/'BACKUP_RECEIPT.json');archive=Path(receipt['archive']);assert archive==backup/'StrippedAOTDllsTempProj.recovery.tar.gz' and sha(archive)==receipt['archiveSha256']=='4b5e3b8eb84646bd5025f755f0f23436adf359cbaf9ff850983a2837fe16a727' and archive.stat().st_size==112759682
expected=load(backup/'INVENTORY_BEFORE.json')['rows'];rows=[]
for p in [target,*sorted(target.rglob('*'))]:
 s=p.lstat();assert not p.is_symlink() and (p.is_file() or p.is_dir());rows.append({'path':str(p.relative_to(target.parent)),'kind':'file' if p.is_file() else 'directory','bytes':s.st_size if p.is_file() else None,'mode':stat.S_IMODE(s.st_mode),'mtimeNs':s.st_mtime_ns,'sha256':sha(p) if p.is_file() else None})
assert rows==expected and len([r for r in rows if r['kind']=='file'])==2664
files={r['path']:r for r in expected if r['kind']=='file'};seen=set()
with tarfile.open(archive,'r:gz') as tar:
 for m in tar:
  p=Path(m.name);assert not p.is_absolute() and '..' not in p.parts
  if m.isfile() and not p.name.startswith('._'):
   assert m.name in files and m.name not in seen;h=hashlib.sha256();n=0;stream=tar.extractfile(m)
   for block in iter(lambda:stream.read(1024*1024),b''):h.update(block);n+=len(block)
   assert n==files[m.name]['bytes'] and h.hexdigest()==files[m.name]['sha256'];seen.add(m.name)
assert set(files)==seen
def siblings():
 values=[]
 for root in sorted(target.parent.iterdir()):
  if root==target:continue
  for p in [root,*sorted(root.rglob('*'))] if root.is_dir() and not root.is_symlink() else [root]:
   s=p.lstat();kind='symlink' if p.is_symlink() else 'file' if p.is_file() else 'directory';values.append({'path':str(p.relative_to(target.parent)),'kind':kind,'mode':stat.S_IMODE(s.st_mode),'bytes':s.st_size if kind=='file' else None,'mtimeNs':s.st_mtime_ns,'sha256':sha(p) if kind=='file' else None,'linkTarget':os.readlink(p) if kind=='symlink' else None})
 return values
adjacentBefore=siblings();beforePath=B/'initializer-05-APPROVED_CLEANUP_SIBLINGS_BEFORE.json';assert not beforePath.exists();beforePath.write_text(json.dumps({'root':str(target.parent),'excludedOnlyApprovedTarget':str(target),'rows':adjacentBefore},indent=2)+'\n')
intent=B/'initializer-05-APPROVED_CLEANUP_INTENT.json';assert not intent.exists();freeBefore=free();intent.write_text(json.dumps({'timeUtc':now(),'approval':approval['userApproval'],'exactTarget':str(target),'verifiedRecoveryArchive':str(archive),'archiveSha256':sha(archive),'originalRegularFilesVerified':2664,'siblingsInventorySha256':sha(beforePath),'freeBytesBefore':freeBefore,'action':'shutil.rmtree of this one exact canonical ignored generated directory only','noOtherPathsAuthorized':True},indent=2)+'\n')
shutil.rmtree(target)
assert not target.exists() and not target.is_symlink();adjacentAfter=siblings();assert adjacentBefore==adjacentAfter
afterPath=B/'initializer-05-APPROVED_CLEANUP_SIBLINGS_AFTER.json';afterPath.write_text(json.dumps({'root':str(target.parent),'excludedOnlyApprovedTarget':str(target),'rows':adjacentAfter},indent=2)+'\n')
assert sha(archive)==receipt['archiveSha256'];assert not subprocess.check_output(['git','-C',str(D),'status','--porcelain=v1','--untracked-files=all'],text=True)
freeAfter=free();x={'kind':'ExplicitUserApprovedSingleDirectoryCapacityAction','result':'PassedExactScopedRemovalAndPreservation','startUtc':start,'endUtc':now(),'approval':approval['userApproval'],'deletedExactDirectory':str(target),'regularFilesRemoved':2664,'logicalBytesRemoved':526680638,'recoveryArchive':str(archive),'archiveBytes':archive.stat().st_size,'archiveSha256':sha(archive),'archiveRetainedAndAllRegularPayloadsVerified':True,'siblingsRowsVerifiedBeforeAndAfter':len(adjacentBefore),'siblingsBefore':str(beforePath),'siblingsAfter':str(afterPath),'siblingsUnchanged':True,'trackedSourceChanges':0,'deletedOtherPaths':0,'device':B.stat().st_dev,'freeBytesBefore':freeBefore,'freeBytesAfter':freeAfter,'actualAvailableBytesIncrease':freeAfter-freeBefore,'isRuntimeAdmission':False,'requiresTwoFreshCapacitySamplesAndAllRemainingGates':True,'runnerInvocations':0,'UnityLaunches':0,'Players':0};result.write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(x,indent=2))
