"""Scope, raw hash, source, history, JSON, link and staged-byte checks for blocked S."""
from pathlib import Path
import json,hashlib,subprocess,re,datetime,shutil
P=Path(__file__).resolve().parent;D=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');C=Path(json.loads((P/'CHECKPOINT_LOCATION.json').read_text())['path']);PIN='e8fda852684f584295fe37830340ab3c9f3fcc4f';rel=str(C.relative_to(D));docs=['Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md','Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md']
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(D),*args])
assert git('rev-parse','HEAD').decode().strip()==PIN and not git('diff','--cached','--name-only');assert set(git('diff','--name-only').decode().splitlines())==set(docs);assert all(l[3:] in docs or l[3:].startswith(rel+'/') for l in git('status','--short','--untracked-files=all').decode().splitlines())
for row in json.loads((C/'COPY_BINDINGS.json').read_text())['files']:assert sha(C/row['copy'])==row['sha256']==sha(row['source']) and (C/row['copy']).stat().st_size==row['size']
for row in json.loads((C/'SOURCE_BINDINGS.json').read_text())['files']:assert sha(C/row['snapshot'])==row['sha256']==hashlib.sha256(git('show',row['gitCommit']+':'+row['path'])).hexdigest()
for row in json.loads((C/'REPORT_HISTORY_PRESERVATION.json').read_text())['reports']:
 current=(D/row['file']).read_text();old='## Historical '+current.split('## Historical ',1)[1];assert hashlib.sha256(old.encode()).hexdigest()==row['historicalBodySha256'];assert sha(D/row['file'])==row['currentFileSha256']
links=[]
for f in [*[D/n for n in docs],C/'README.md']:
 text=f.read_text().split('## Historical ',1)[0]
 for t in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
  if '://' in t or t.startswith('#'):continue
  target=t.strip('<>').split('#')[0];assert (f.parent/target).exists(),(f,target);links.append({'file':str(f.relative_to(D)),'target':target})
attrs=['# Exact captured bytes; owned report prose remains whitespace checked.','storage-diagnostic/** -whitespace -text','transport/** -whitespace -text','retained-r-audit/** -whitespace -text','preflight/**/*.log -whitespace -text'];raw=[]
for f in sorted(C.rglob('*')):
 if not f.is_file():continue
 n=str(f.relative_to(C))
 if f.is_relative_to(C/'source-snapshot') or f.is_relative_to(C/'preflight'):
  try:text=f.read_text()
  except UnicodeDecodeError:attrs.append('"'+n+'" binary');continue
  if any(line.endswith((' ','\t')) for line in text.splitlines()) or text.endswith('\n\n'):
   raw.append({'path':n,'sha256':sha(f)});attrs.append('"'+n+'" -whitespace -text')
(C/'.gitattributes').write_text('\n'.join(attrs)+'\n');(C/'RAW_WHITESPACE_BINDINGS.json').write_text(json.dumps({'exactCapturedFiles':raw,'ownedProseChecked':True},indent=2)+'\n');count=0
for f in C.rglob('*.json'):json.loads(f.read_text());count+=1
assert all(f.stat().st_size<100*1024*1024 for f in C.rglob('*') if f.is_file());(C/'PUBLICATION_CHECKS.json').write_text(json.dumps({'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'Passed','jsonFiles':count,'localLinks':links,'rawCopiesAndLiveHashesMatch':True,'sourceSnapshotsMatchExactGit':True,'historicalReportBodiesPreserved':True,'sourceCommit':PIN,'onlyOwnedScope':docs+[rel],'noCoreBatchInvented':True},indent=2)+'\n');m=C/'MANIFEST.sha256';m.write_text('\n'.join(sha(f)+'  '+str(f.relative_to(C)) for f in sorted(C.rglob('*')) if f.is_file() and f!=m)+'\n');git('diff','--check');paths=docs+[str(f.relative_to(D)) for f in C.rglob('*') if f.is_file()];subprocess.run(['git','-C',str(D),'add','-f','--pathspec-from-file=-','--pathspec-file-nul'],input=b'\0'.join(n.encode() for n in paths)+b'\0',check=True);git('diff','--cached','--check');assert set(git('diff','--cached','--name-only').decode().splitlines())==set(paths)
for n in paths:assert git('show',':'+n)==(D/n).read_bytes()
(P/'STAGING_RECEIPT.json').write_text(json.dumps({'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'Passed','stagedFiles':len(paths),'manifestSha256':sha(m),'diffCheck':'Passed','stagedBytesMatch':True,'modificationScope':docs+[rel]},indent=2)+'\n');print('Owned blocker files staged and byte verified',len(paths),flush=True)
