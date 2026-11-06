from pathlib import Path
import hashlib,json,os,datetime
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');O=B/'R03IR-Initializer-20261106-oneuse-05';out=B/'Preflight-Initializer05-Resume-20261106-after-retirement/RAW_MANIFEST.json';assert not out.exists() and (B/'Preflight-Initializer05-Resume-20261106-after-retirement/FINAL_INDEPENDENT_AUDIT.json').exists()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for v in iter(lambda:f.read(1048576),b''):h.update(v)
 return h.hexdigest()
start=datetime.datetime.now(datetime.timezone.utc).isoformat();files=[];links=[]
for root,dirs,names in os.walk(O,followlinks=False):
 for n in sorted(dirs+names):
  p=Path(root)/n
  if p.is_symlink():links.append(dict(path=str(p.relative_to(O)),target=os.readlink(p)))
  elif p.is_file():files.append(dict(path=str(p.relative_to(O)),bytes=p.stat().st_size,sha256=sha(p)))
report=dict(kind='IndependentInitializer05CompleteRetainedLiveInventory',root=str(O),start=start,end=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=files,symlinks=links,totalBytes=sum(x['bytes'] for x in files),scope='Complete retained live root; original semantic result unchanged; no acceptance')
with out.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print(len(files),'files',len(links),'symlinks',report['totalBytes'],'bytes')
