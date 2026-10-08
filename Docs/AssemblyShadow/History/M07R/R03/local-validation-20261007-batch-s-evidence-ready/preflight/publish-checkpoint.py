"""Preserve exact sealed S bytes and source snapshots; only Local-owned checkpoint writes."""
from pathlib import Path
import json,hashlib,subprocess,shutil,datetime
P=Path(__file__).resolve().parent;BASE=P.parent;B=BASE/'R03LocalBatch-20261007S-lr-recovery';W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';LIMIT=64*1024*1024

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def load(path):return json.loads(Path(path).read_text())
def save(path,value):
 with Path(path).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True,timeout=120).strip()
a=load(P/'POSTRUN_AUTHENTICATION.json');assert a['state']=='Passed';assert load(P/'storage-publication-check.json')['state']=='Passed';auth=load(P/'SOURCE_AUTHORITY.json');pins=auth['repositories'];assert not git(D,'status','--short') and git(D,'rev-parse','HEAD')==pins['hybridclr_demo'];result=load(B/'LOCAL_BATCH_RESULT.json');ready=result['result']=='EvidenceReadyForPrimaryReview' and result['sealStatus']=='Passed' and a['outerExitCode']==0 and a['storageSessionState']=='Passed' and a['counts']=={'Passed':90};name='local-validation-20261007-batch-s-'+('evidence-ready' if ready else 'return-required');C=D/'Docs/AssemblyShadow/History/M07R/R03'/name;assert not C.exists();C.mkdir();start=utc();copies=[];transports=[]
def transport(src,dest,force=False):
 src=Path(src);dest=Path(dest);before=sha(src);size=src.stat().st_size
 if not force and size<100*1024*1024:
  dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copy2(src,dest);assert sha(dest)==before==sha(src);copies.append({'sourcePath':str(src),'destination':str(dest.relative_to(C)),'size':size,'sha256':before});return
 folder=dest.with_name(dest.name+'.parts');folder.mkdir(parents=True);parts=[];whole=hashlib.sha256();total=0
 with src.open('rb') as stream:
  i=0
  while block:=stream.read(LIMIT):
   file=folder/('part-'+str(i).zfill(3)+'.part');file.write_bytes(block);digest=hashlib.sha256(block).hexdigest();assert sha(file)==digest;parts.append({'path':str(file.relative_to(C)),'size':len(block),'sha256':digest});whole.update(block);total+=len(block);i+=1
 assert whole.hexdigest()==before==sha(src) and total==size;transports.append({'originalPath':str(dest.relative_to(C)),'originalLivePath':str(src),'originalSize':size,'originalSha256':before,'parts':parts,'concatenationSha256Verified':True,'liveOriginalUnmodified':True})
index=load(B/'evidence-index.json');names={r['path'] for r in index['files']}|{'LOCAL_BATCH_RESULT.json','BATCH_EXECUTION.json','evidence-index.json','evidence.tar.gz','seal-receipt.json'}
for name in sorted(names):transport(B/name,C/'batch'/name,force=name=='evidence.tar.gz')
for root,label in [(P,'preflight'),(BASE/'RetainedR-R03LocalBatch-20261007S-lr-recovery-2','retained-r-audit'),(BASE/'Transport-R03LocalBatch-20261007S-lr-recovery-2','transport'),(BASE/'StorageCheck-R03LocalBatch-20261007S-lr-recovery-2','admitted-diagnostic'),(BASE/'Storage-R03LocalBatch-20261007S-lr-recovery-2','executing-storage')]:
 for src in sorted(root.rglob('*')):
  if src.is_file():assert not src.is_symlink();transport(src,C/label/src.relative_to(root))
save(C/'COPY_BINDINGS.json',{'kind':'ExactLocalEvidenceCopies','files':copies,'originalsUnmodified':True});save(C/'FILE_TRANSPORT.json',{'kind':'BytePreservingLocalEvidenceTransport','startUtc':start,'endUtc':utc(),'partSizeLimit':LIMIT,'files':transports,'liveOriginalsUnchanged':True,'reason':'Sealed archive uses ordered exact chunks; large files preserve original bytes/hash without resealing.'})
bindings=[]
for repo,pin in pins.items():
 root=W/repo;assert not git(root,'status','--short') if repo!='hybridclr_demo' else True;assert git(root,'rev-parse','HEAD')==pin
 patterns={'hybridclr_demo':['Tools/AssemblyShadow','Assets/AssemblyShadowDemo/Editor','Assets/AssemblyShadowDemo/Bootstrap','Packages/manifest.json','Packages/packages-lock.json','ProjectSettings/AssemblyShadowSourcePins.json','ProjectSettings/ProjectVersion.txt','.github/workflows/r03-lr-contracts.yml','.github/workflows/r03-storage.yml'],'hybridclr_unity':['Editor/AssemblyShadow','Tests/Editor/AssemblyShadow'],'hybridclr':['*AssemblyShadow*'],'il2cpp_plus':['*AssemblyShadow*','libil2cpp/vm/MetadataCache.cpp','libil2cpp/utils/MemoryPool.cpp','libil2cpp/gc/BoehmGC.cpp','libil2cpp/vm/Delegate.cpp','libil2cpp/vm/ThreadPool.cpp']}[repo]
 for name in git(root,'ls-files',*patterns).splitlines():
  raw=subprocess.check_output(['git','-C',str(root),'show',pin+':'+name]);assert raw==(root/name).read_bytes();dest=C/'source-snapshot'/repo/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);bindings.append({'repositoryPath':str(root),'commit':pin,'path':name,'snapshot':str(dest.relative_to(C)),'sha256':sha(dest)})
save(C/'SOURCE_BINDINGS.json',{'kind':'ExactExecutedGitSourceSnapshots','repositories':pins,'files':bindings,'authorization':load(P/'EXECUTION_AUTHORIZATION.json'),'installedNativeInventoriesRemainAuthoritativeInBuildReceipts':True})
helper='''"""Reassemble exact transported evidence into an absolute unused directory."""
from pathlib import Path
import json,hashlib,sys
root=Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit('Usage: python3 REASSEMBLE_EVIDENCE.py /absolute/unused/directory')
out=Path(sys.argv[1]);assert out.is_absolute() and not out.exists();out.mkdir(parents=True)
for row in json.loads((root/'FILE_TRANSPORT.json').read_text())['files']:
 rel=Path(row['originalPath']);assert not rel.is_absolute() and '..' not in rel.parts;target=out/rel;target.parent.mkdir(parents=True,exist_ok=True);whole=hashlib.sha256();total=0
 with target.open('xb') as dst:
  for part in row['parts']:
   rel=Path(part['path']);assert not rel.is_absolute() and '..' not in rel.parts;file=root/rel;h=hashlib.sha256();size=0
   with file.open('rb') as src:
    for block in iter(lambda:src.read(1048576),b''):h.update(block);whole.update(block);size+=len(block);total+=len(block);dst.write(block)
   assert h.hexdigest()==part['sha256'] and size==part['size']
 assert whole.hexdigest()==row['originalSha256'] and total==row['originalSize'];print(row['originalPath'],whole.hexdigest(),total)
'''
compile(helper,'REASSEMBLE_EVIDENCE.py','exec');(C/'REASSEMBLE_EVIDENCE.py').write_text(helper);save(P/'CHECKPOINT_LOCATION.json',{'path':str(C),'executedDemoCommit':pins['hybridclr_demo'],'coreResult':result['result'],'localExit':'Primary Implementation','checkpointIsEvidenceOnly':True});print('Copied immutable S checkpoint',C,'copies',len(copies),'transported',len(transports),'sourceSnapshots',len(bindings),flush=True)
