from pathlib import Path
import json,hashlib,datetime,re
P=Path(__file__).resolve().parent;C=Path(json.loads((P/'CHECKPOINT_LOCATION.json').read_text())['path']);D=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
copy=json.loads((C/'COPY_BINDINGS.json').read_text());count=0
for r in copy['files']:
 dst=C/r['destination'];assert dst.stat().st_size==r['size'] and sha(dst)==sha(r['sourcePath'])==r['sha256'];count+=1
transport=json.loads((C/'FILE_TRANSPORT.json').read_text())
for r in transport['files']:
 whole=hashlib.sha256();total=0
 for part in r['parts']:
  f=C/part['path'];assert f.stat().st_size==part['size'] and sha(f)==part['sha256']
  with f.open('rb') as src:
   for block in iter(lambda:src.read(1048576),b''):whole.update(block);total+=len(block)
 assert whole.hexdigest()==sha(r['originalLivePath'])==r['originalSha256'] and total==r['originalSize']
for r in json.loads((C/'SOURCE_BINDINGS.json').read_text())['files']:assert sha(C/r['snapshot'])==r['sha256']
links=[]
for f in [D/'Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md',D/'Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md']:
 text=f.read_text().split('## Historical',1)[0]
 for target in re.findall(r'\]\(([^)]+)\)',text):
  if '://' in target:continue
  dest=(f.parent/target.split('#')[0]).resolve();assert dest.exists(),(str(f),target);links.append({'source':str(f),'target':str(dest)})
(C/'.gitattributes').write_text('batch/** -whitespace\npreflight/** -whitespace\nretained-r-audit/** -whitespace\ntransport/** -whitespace\nadmitted-diagnostic/** -whitespace\nexecuting-storage/** -whitespace\nsource-snapshot/** -whitespace\n')
record={'kind':'LocalCheckpointVerification','recordedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'Passed','exactCopies':count,'orderedTransportFiles':len(transport['files']),'authoredLocalLinks':links,'rawCaptureWhitespaceScope':'Only byte-preserved evidence/source snapshots; authored reports and metadata retain default checks','jsonPolicy':'Authored JSON parsed; intentionally invalid compiler/control fixtures preserved as input evidence'}
with (C/'CHECKPOINT_VERIFICATION.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
files=sorted(f for f in C.rglob('*') if f.is_file());assert not any(f.is_symlink() for f in files)
with (C/'MANIFEST.sha256').open('x') as out:
 for f in files:out.write(sha(f)+'  '+str(f.relative_to(C))+'\n')
print('Checkpoint verified',count,'copies',len(transport['files']),'ordered transports',len(files),'manifest files',flush=True)
