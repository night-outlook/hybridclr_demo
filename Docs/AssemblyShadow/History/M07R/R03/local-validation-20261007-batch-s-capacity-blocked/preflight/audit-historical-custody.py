"""Read-only full historical custody plus new retained-R cache snapshot; no recovery."""
from pathlib import Path
import subprocess,json,hashlib,datetime,concurrent.futures,os,time
P=Path(__file__).resolve().parent;BASE=P.parent;D=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-r-return-required';R=BASE/'R03LocalBatch-20261007R-lq-storage';PUB='1fb504b2732c72dd1c403060396276af69d6251a'
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(n,value):
 with (P/n).open('x') as f:json.dump(value,f,separators=(',',':'));f.write('\n')
start=utc();expected={};groups={}
def bind(p,h,group):
 p=str(p);assert len(h)==64
 if p in expected:assert expected[p]==h,(p,'Conflicting historical authority')
 expected[p]=h;groups.setdefault(group,set()).add(p)
m=C/'MANIFEST.sha256';blob=subprocess.check_output(['git','-C',str(D),'show',PUB+':'+str(m.relative_to(D))]);assert m.read_bytes()==blob;bind(m,hashlib.sha256(blob).hexdigest(),'rCheckpoint')
for line in blob.decode().splitlines():
 h,rel=line.split('  ',1);path=C/rel;assert path.resolve().is_relative_to(C.resolve());bind(path,h,'rCheckpoint')
prior=C/'preflight/prior-evidence-custody.json';assert sha(prior)==expected[str(prior)];old=json.loads(prior.read_text());
for p,h in old.items():bind(p,h,'priorFullCustody')
post=json.loads((C/'preflight/POSTRUN_AUTHENTICATION.json').read_text())
for n,h in post['topLevelHashes'].items():bind(R/n,h,'rTopLevel')
index=json.loads((R/'evidence-index.json').read_text());assert sha(R/'evidence-index.json')==post['topLevelHashes']['evidence-index.json']
for row in index['files']:
 path=R/row['path'];assert path.resolve().is_relative_to(R.resolve());assert path.stat().st_size==row['size'];bind(path,row['sha256'],'rIndexedLive')
for p in (C/'executing-storage').rglob('*'):
 if p.is_file():bind(BASE/'Storage-R03LocalBatch-20261007R-lq-storage'/p.relative_to(C/'executing-storage'),expected[str(p)],'rExecutingSidecar')
# Untabled retained Library/build/cache files are a current before/after snapshot, never runtime acceptance.
new=[];symlinks={}
for root,dirs,files in os.walk(R,followlinks=False):
 for name in [*dirs,*files]:
  f=Path(root)/name
  if f.is_symlink():symlinks[str(f)]=os.readlink(f)
 for name in files:
  f=Path(root)/name
  if not f.is_symlink() and str(f) not in expected:new.append(f)
print('Historical known paths',len(expected),'additional current retained-R files',len(new),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for p,h in pool.map(lambda p:(p,sha(p)),new,buffersize=48):bind(p,h,'rCurrentCacheSnapshotOnly')
save('prior-evidence-custody.json',expected);save('RETAINED_R_SYMLINKS.json',symlinks);save('HISTORICAL_CUSTODY_AUTHORITY.json',{'sourcePublication':PUB,'checkpointManifestSha256':sha(m),'priorMapPath':str(prior),'priorMapSha256':sha(prior),'newMapSha256':sha(P/'prior-evidence-custody.json'),'groups':{g:len(v) for g,v in groups.items()},'currentRCacheSnapshotIsNotHistoricalAcceptance':True,'retainedRSymlinks':len(symlinks),'recordedUtc':utc()})
errors=[];done=0;last=time.monotonic()
def verify(row):
 p,h=row
 try:
  actual=sha(p);return None if actual==h else {'path':p,'expectedSha256':h,'actualSha256':actual}
 except Exception as e:return {'path':p,'expectedSha256':h,'error':repr(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for error in pool.map(verify,expected.items(),buffersize=48):
  done+=1
  if error:errors.append(error)
  if time.monotonic()-last>20:print('Custody checked',done,'/',len(expected),'errors',len(errors),flush=True);last=time.monotonic()
record={'kind':'SReadOnlyHistoricalCustodyPrerequisite','startUtc':start,'endUtc':utc(),'state':'Passed' if not errors else 'Failed','uniqueFiles':len(expected),'groups':{g:len(v) for g,v in groups.items()},'errors':errors,'expectedMapSha256':sha(P/'prior-evidence-custody.json'),'retainedRModified':False,'historicalClassificationChanged':False,'currentCacheSnapshotIsNotAcceptance':True};save('HISTORICAL_CUSTODY_BEFORE.json',record);assert not errors,errors[:5];print('Full custody prerequisite Passed',len(expected),'files',flush=True)
