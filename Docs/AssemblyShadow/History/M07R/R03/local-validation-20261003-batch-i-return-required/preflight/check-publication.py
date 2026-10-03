import datetime,hashlib,json,pathlib,re,subprocess,urllib.parse
D=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');P=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261003I-completion');R=P.parent/'R03LocalBatch-20261003I-completion';C=D/('Docs/AssemblyShadow/History/M07R/R03/local-validation-20261003-batch-i-'+('evidence-ready' if json.loads((R/'LOCAL_BATCH_RESULT.json').read_text())['result']=='EvidenceReadyForPrimaryReview' else 'return-required'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(D),*args],text=True)
projectChecks=[]
for project in sorted((R/'projects').iterdir()):
 if project.name not in ['candidate-release','candidate-debug','candidate-off','reference-release']:continue
 source=json.loads((project/'source-inputs.json').read_text()); config=json.loads((R/'builds'/project.name/'config.json').read_text()); pins=json.loads((project/'ProjectSettings/AssemblyShadowSourcePins.json').read_text());manifest=json.loads((project/'Packages/manifest.json').read_text())
 for f in source['files']:assert sha(project/f['path'])==f['sha256']
 assert source['demoCommit']=='c579e75eadef58ca484b35ffee03e435a925d781' and sha(project/'source-inputs.json')==config['sourceManifestSha256']
 assert manifest['dependencies']['com.code-philosophy.hybridclr']=='file:/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity'
 projectChecks.append({'path':str(project),'sourceFilesAuthenticated':len(source['files']),'sourceInputsSha256':sha(project/'source-inputs.json'),'installPins':pins,'config':config})
for name in ['LOCAL_VALIDATION.md','RETURN_TO_WEB.md']:
 q=D/'Docs/AssemblyShadow/Handoff'/name;old=git('show','HEAD:Docs/AssemblyShadow/Handoff/'+name)
 first,oldtail=old.split('\n',1);oldtail=oldtail.lstrip('\n').replace('## Current','## Historical',1)
 assert q.read_text().endswith(oldtail),'Historical content altered '+name
 preservation=json.loads((C/'REPORT_HISTORY_PRESERVATION.json').read_text());preservation[name]['newSha256']=sha(q);(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps(preservation,indent=2)+'\n')
links=[]
for q in [C/'README.md',D/'Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md',D/'Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md']:
 txt=q.read_text().split('## Historical',1)[0]
 for target in re.findall(r'\]\(([^)]+)\)',txt):
  if '://' in target or target.startswith('#'):continue
  p=q.parent/urllib.parse.unquote(target.split('#')[0]);assert p.exists(),(q,target);links.append({'file':str(q),'target':target})
jsonCount=0
for p in C.rglob('*.json'):json.loads(p.read_text());jsonCount+=1
idx=json.loads((R/'evidence-index.json').read_text())
for f in idx['files']:assert sha(C/'batch'/f['path'])==f['sha256']
for n in ['LOCAL_BATCH_RESULT.json','evidence-index.json','seal-receipt.json']:assert sha(C/'batch'/n)==sha(R/n)
transport=json.loads((C/'ARCHIVE_TRANSPORT.json').read_text());combined=hashlib.sha256();total=0
for part in transport['parts']:
 p=C/part['path'];assert sha(p)==part['sha256'] and p.stat().st_size==part['size'];total+=part['size']
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):combined.update(b)
assert combined.hexdigest()==transport['originalSha256']==sha(R/'evidence.tar.gz') and total==transport['originalSize']
assert max(p.stat().st_size for p in C.rglob('*') if p.is_file())<100*1024*1024
record={'kind':'PreCommitEvidenceScopeCheck','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'Passed','projectProvenanceChecks':projectChecks,'parsedCheckpointJsonFilesBeforeThisReceipt':jsonCount,'newMarkdownLinks':links,'historyPreserved':'Previous report body unchanged except Current-to-Historical H heading','classification':'Two owned Local reports and new I checkpoint only; no code/runtime/pin/earlier-evidence changes','reusedEvidence':'None promoted; source snapshot and earlier hashes are historical/read-only bindings','rawWhitespaceAudit':'Captured generated IL2CPP/native raw files preserve every sealed byte. The two exact path-specific source/settings exceptions are independently authenticated against a pinned Git blob or post-execution live generated settings/issue receipt in SOURCE_SNAPSHOT_WHITESPACE.json; owned prose and other snapshots retain whitespace checks'}
(C/'PUBLICATION_CHECKS.json').write_text(json.dumps(record,indent=2)+'\n')
# Complete the checkpoint manifest before staging; no commit SHA circularity.
files=sorted(p for p in C.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256');(C/'MANIFEST.sha256').write_text(''.join(sha(p)+'  '+str(p.relative_to(C))+'\n' for p in files))
owned=['Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md','Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md',str(C.relative_to(D))]
subprocess.run(['git','-C',str(D),'add','--',*owned],check=True)
# Respect repository ignores except for explicitly manifest-owned raw evidence.
staged=set(git('diff','--cached','--name-only','-z').split('\0'));missing=[str(p.relative_to(D)) for p in C.rglob('*') if p.is_file() and str(p.relative_to(D)) not in staged]
if missing:subprocess.run(['git','-C',str(D),'add','-f','--',*missing],check=True)
changes=[p for p in git('diff','--cached','--name-only','-z').split('\0') if p]
assert set(changes)==set(owned[:2]+[str(p.relative_to(D)) for p in C.rglob('*') if p.is_file()])
for line in (C/'MANIFEST.sha256').read_text().splitlines():
 h,n=line.split('  ',1);p=C/n;assert sha(p)==h
 b=subprocess.check_output(['git','-C',str(D),'show',':'+str(p.relative_to(D))]);assert hashlib.sha256(b).hexdigest()==h,n
for name in owned[:2]:assert subprocess.check_output(['git','-C',str(D),'show',':'+name])==(D/name).read_bytes()
subprocess.run(['git','-C',str(D),'diff','--check'],capture_output=True,check=True);subprocess.run(['git','-C',str(D),'diff','--cached','--check'],capture_output=True,check=True)
print(json.dumps({'stagedFiles':len(changes),'manifestFiles':len(files),'explicitlyForceAddedOwnedEvidence':len(missing),'jsonValidated':jsonCount,'newLinksChecked':len(links),'projectProvenance':len(projectChecks),'status':'Passed'}))
