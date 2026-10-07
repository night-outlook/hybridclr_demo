"""Publish exact owned Local evidence; never delete or rewrite live evidence."""
from pathlib import Path
import hashlib,json,shutil,subprocess,datetime
P=Path(__file__).resolve().parent;B=P.parent/'R03LocalBatch-20261007R-lq-storage';W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';PIN='ba57a3391da9627e694ee33f8bfe3cb993e6c56a';BASE=P.parent;LIMIT=64*1024*1024

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,a):
 with p.open('x') as f:json.dump(a,f,indent=2);f.write('\n')
def copy_exact(src,dest):
 dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest);assert sha(dest)==sha(src)
def transport(src,dest,checkpoint,force=False):
 if not force and src.stat().st_size<100*1024*1024:copy_exact(src,dest);return None
 folder=dest.with_name(dest.name+'.parts');folder.mkdir(parents=True);parts=[];whole=hashlib.sha256();total=0
 with src.open('rb') as stream:
  seq=0
  while block:=stream.read(LIMIT):
   p=folder/('part-'+str(seq).zfill(3)+'.part');p.write_bytes(block);h=sha(p);assert h==hashlib.sha256(block).hexdigest();parts.append({'path':str(p.relative_to(checkpoint)),'size':len(block),'sha256':h});whole.update(block);total+=len(block);seq+=1
 assert whole.hexdigest()==sha(src) and total==src.stat().st_size
 return {'originalPath':str(dest.relative_to(checkpoint)),'originalLivePath':str(src),'originalSize':total,'originalSha256':whole.hexdigest(),'parts':parts,'concatenationSha256Verified':True,'liveOriginalUnmodified':True}

if __name__=='__main__':
 assert (P/'runner-exit.json').exists() and (P/'POSTRUN_AUDIT_DISPATCH.json').exists();budget=json.loads((P/'storage-publication-check.json').read_text());assert budget['state']=='Passed'
 assert subprocess.check_output(['git','-C',str(D),'status','--short']).decode()=='';assert subprocess.check_output(['git','-C',str(D),'rev-parse','HEAD']).decode().strip()==PIN
 result=json.loads((B/'LOCAL_BATCH_RESULT.json').read_text());session=json.loads((BASE/'Storage-R03LocalBatch-20261007R-lq-storage/session.json').read_text());ready=result['result']=='EvidenceReadyForPrimaryReview' and session['state']=='Passed';C=D/('Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-r-'+('evidence-ready' if ready else 'return-required'));assert not C.exists();C.mkdir();start=utc();transports=[]
 index=json.loads((B/'evidence-index.json').read_text());files=set(row['path'] for row in index['files'])|{'LOCAL_BATCH_RESULT.json','BATCH_EXECUTION.json','evidence-index.json','seal-receipt.json','evidence.tar.gz'}
 for name in sorted(files):
  r=transport(B/name,C/'batch'/name,C,force=name=='evidence.tar.gz')
  if r:transports.append(r)
 for src in sorted(P.rglob('*')):
  if src.is_file():
   r=transport(src,C/'preflight'/src.relative_to(P),C)
   if r:transports.append(r)
 for name,label in [('StorageCheck-R03LocalBatch-20261007R-lq-storage','original-blocked-diagnostic'),('StorageCheck-R03LocalBatch-20261007R-lq-storage-2','admitted-diagnostic'),('Storage-R03LocalBatch-20261007R-lq-storage','executing-storage')]:
  root=BASE/name
  for src in sorted(root.rglob('*')):
   if src.is_file():copy_exact(src,C/label/src.relative_to(root))
 save(C/'FILE_TRANSPORT.json',{'kind':'BytePreservingLocalEvidenceTransport','startUtc':start,'endUtc':utc(),'partSizeLimit':LIMIT,'files':transports,'liveOriginalsUnchanged':True,'reason':'Sealed archive always split; files exceeding Git publication size are represented by exact ordered parts. No new seal/runtime result.'})
 save(P/'CHECKPOINT_LOCATION.json',{'path':str(C),'sourceCommit':PIN,'result':result['result'],'storageSession':session['state'],'checkpointIsLocalEvidenceOnly':True})
 print('Exact raw checkpoint copied',str(C),'transported files',len(transports),flush=True)
 # Authenticate executed source files independently of raw outputs.
 bindings=[]
 for repo in ['hybridclr_demo','hybridclr_unity','hybridclr','il2cpp_plus']:
  source=json.loads((P/'SOURCE_AUTHORITY.json').read_text())['repositories'][repo]
  if repo=='hybridclr_demo':
   names=subprocess.check_output(['git','-C',str(W/repo),'ls-files','Tools/AssemblyShadow','Assets/AssemblyShadowDemo/Editor','Assets/AssemblyShadowDemo/Bootstrap','Packages/manifest.json','Packages/packages-lock.json','ProjectSettings/AssemblyShadowSourcePins.json','.github/workflows/r03-storage.yml']).decode().splitlines()
  elif repo=='hybridclr_unity':names=subprocess.check_output(['git','-C',str(W/repo),'ls-files','Editor/AssemblyShadow','Tests/Editor/AssemblyShadow']).decode().splitlines()
  elif repo=='hybridclr':names=subprocess.check_output(['git','-C',str(W/repo),'ls-files','*AssemblyShadow*']).decode().splitlines()
  else:names=subprocess.check_output(['git','-C',str(W/repo),'ls-files','*AssemblyShadow*','libil2cpp/vm/MetadataCache.cpp','libil2cpp/utils/MemoryPool.cpp','libil2cpp/gc/BoehmGC.cpp','libil2cpp/vm/Delegate.cpp','libil2cpp/vm/ThreadPool.cpp']).decode().splitlines()
  for name in names:
   raw=subprocess.check_output(['git','-C',str(W/repo),'show',source+':'+name])
   assert raw==(W/repo/name).read_bytes();dest=C/'source-snapshot'/repo/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);bindings.append({'repositoryPath':str(W/repo),'commit':source,'path':name,'snapshot':str(dest.relative_to(C)),'sha256':sha(dest)})
 save(C/'SOURCE_BINDINGS.json',{'kind':'ExactExecutedGitSourceSnapshots','sourceRepositories':json.loads((P/'SOURCE_AUTHORITY.json').read_text())['repositories'],'files':bindings,'installedNativeInventoriesRemainAuthoritativeInBuildReceipts':True,'authorizedAgentConfigurationException':json.loads((P/'USER_SOURCE_AUTHORIZATION.json').read_text())})
 helper='''"""Reconstruct exact transported evidence into an absolute unused directory."""
from pathlib import Path
import json,hashlib,sys
root=Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit('Usage: python3 REASSEMBLE_EVIDENCE.py /absolute/unused/directory')
out=Path(sys.argv[1]);assert out.is_absolute() and not out.exists();out.mkdir(parents=True)
for row in json.loads((root/'FILE_TRANSPORT.json').read_text())['files']:
 rel=Path(row['originalPath']);assert not rel.is_absolute() and '..' not in rel.parts;target=out/rel;target.parent.mkdir(parents=True,exist_ok=True);whole=hashlib.sha256();total=0
 with target.open('xb') as dst:
  for item in row['parts']:
   rel=Path(item['path']);assert not rel.is_absolute() and '..' not in rel.parts;part=root/rel;h=hashlib.sha256();size=0
   with part.open('rb') as src:
    for block in iter(lambda:src.read(1048576),b''):h.update(block);whole.update(block);size+=len(block);total+=len(block);dst.write(block)
   assert h.hexdigest()==item['sha256'] and size==item['size']
 assert whole.hexdigest()==row['originalSha256'] and total==row['originalSize'];print(row['originalPath'],whole.hexdigest(),total)
'''
 compile(helper,'REASSEMBLE_EVIDENCE.py','exec');(C/'REASSEMBLE_EVIDENCE.py').write_text(helper)
