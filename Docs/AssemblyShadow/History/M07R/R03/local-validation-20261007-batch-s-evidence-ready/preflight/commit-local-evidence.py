from pathlib import Path
import json,subprocess,datetime,hashlib,os
P=Path(__file__).resolve().parent;D=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');C=Path(json.loads((P/'CHECKPOINT_LOCATION.json').read_text())['path']);auth=json.loads((P/'SOURCE_AUTHORITY.json').read_text());pin=auth['repositories']['hybridclr_demo'];branch=auth['branch'];owned=['Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md','Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md',str(C.relative_to(D))];records=[]
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(*args):
 start=utc();r=subprocess.run(['git','-C',str(D),*args],capture_output=True,text=True,timeout=180);records.append({'argv':['git','-C',str(D),*args],'startUtc':start,'endUtc':utc(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0,r.stderr;return r.stdout
assert git('rev-parse','HEAD').strip()==pin and git('branch','--show-current').strip()==branch;assert not git('diff','--cached','--name-only').strip()
raw=git('status','--porcelain','-z','--untracked-files=all')
for entry in raw.split('\0'):
 if not entry:continue
 assert entry[3:] in owned[:2] or entry[3:].startswith(owned[2]+'/'),entry
manifest=C/'MANIFEST.sha256';expected={}
for line in manifest.read_text().splitlines():
 h,name=line.split('  ',1);f=C/name
 with f.open('rb') as src:actual=hashlib.file_digest(src,'sha256').hexdigest()
 assert actual==h;expected[name]=h
assert set(expected)=={str(f.relative_to(C)) for f in C.rglob('*') if f.is_file() and f!=manifest}
git('add','-f','--',*owned)
staged=git('diff','--cached','--name-only','-z').split('\0');staged=[x for x in staged if x];assert len(staged)==len(expected)+3
for name in staged:assert name in owned[:2] or name.startswith(owned[2]+'/'),name
# Git's clean-filter output must preserve each intended evidence byte.
for name in staged:
 indexed=subprocess.check_output(['git','-C',str(D),'show',':'+name]);assert indexed==(D/name).read_bytes(),name
git('diff','--check');git('diff','--cached','--check');before=utc();out=git('commit','-m','Preserve source-bound R03 batch S Local validation and custody evidence');head=git('rev-parse','HEAD').strip();assert len(head)==40;assert not git('status','--short').strip()
with (P/'LOCAL_COMMIT_RECEIPT.json').open('x') as f:json.dump({'kind':'ScopedLocalEvidenceCommit','commit':head,'sourceCommit':pin,'branch':branch,'ownedPaths':owned,'stagedFiles':len(staged),'startUtc':before,'endUtc':utc(),'records':records},f,indent=2);f.write('\n')
print('Committed only Local evidence/docs',head,'files',len(staged),flush=True)
