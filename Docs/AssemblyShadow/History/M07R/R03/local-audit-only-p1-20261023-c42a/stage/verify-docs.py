from pathlib import Path
import json,hashlib,subprocess,re,datetime,urllib.parse
P=Path(__file__).resolve().parent;E=json.loads((P/'EXPECTED.json').read_text());D=Path(E['workspace'])/'hybridclr_demo';O=Path(E['output']);plan=json.loads((P/'PUBLICATION_PLAN.json').read_text());C=Path(plan['checkpoint']);base=E['pins']['hybridclr_demo']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['git','-C',str(D),'rev-parse','HEAD'],text=True).strip()==base
rows=[]
for line in (C/'MANIFEST.sha256').read_text().splitlines():
 h,rel=line.split('  ',1);p=C/rel;assert p.is_file() and not p.is_symlink() and sha(p)==h;rows.append(rel)
assert set(rows)=={str(p.relative_to(C)) for p in C.rglob('*') if p.is_file()}-{'MANIFEST.sha256'}
for row in json.loads((C/'COPY_BINDINGS.json').read_text())['copied']:
 p=C/row['checkpoint'];assert sha(p)==row['sha256']==sha(Path(row['source']))
for row in json.loads((C/'COPY_BINDINGS.json').read_text()).get('encodedTextEvidence',[]):
 record=json.loads((C/row['checkpoint']).read_text());decoded=record['text'].encode('utf-8');assert decoded==Path(row['source']).read_bytes() and len(decoded)==row['decodedBytes'] and hashlib.sha256(decoded).hexdigest()==row['decodedSha256']==record['sourceSha256']
for f in C.rglob('*.json'):json.loads(f.read_text())
for p in C.rglob('*'):
 assert not p.is_symlink()
 if p.is_file():assert p.stat().st_size<20*1024*1024
history={}
for name in ['LOCAL_VALIDATION.md','RETURN_TO_WEB.md']:
 f=D/'Docs/AssemblyShadow/Handoff'/name;old=subprocess.check_output(['git','-C',str(D),'show',base+':'+str(f.relative_to(D))],text=True);prior=old.partition('\n\n')[2].replace('## Current ','## Historical ',1);assert f.read_text().endswith(prior);history[name]=True
for f in [*C.rglob('*.md'),D/'Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md',D/'Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md']:
 for target in re.findall(r'\]\(([^)]+)\)',f.read_text().split('## Historical ',1)[0]):
  target=urllib.parse.unquote(target.split('#')[0]);
  if target and not re.match(r'^[a-z]+:',target):assert (f.parent/target).exists(),(f,target)
status=subprocess.check_output(['git','-C',str(D),'status','--short','--untracked-files=all'],text=True);(P/'STATUS_BEFORE_COMMIT.txt').write_text(status)
for line in status.splitlines():
 rel=line[3:];assert rel in plan['ownedReports'] or rel.startswith(str(C.relative_to(D))+'/'),line
subprocess.run(['git','-C',str(D),'add','--',*plan['ownedReports']],check=True)
subprocess.run(['git','-C',str(D),'add','-f','--',str(C.relative_to(D))],check=True)
subprocess.run(['git','-C',str(D),'diff','--check'],check=True)
subprocess.run(['git','-C',str(D),'diff','--cached','--check'],check=True)
staged=subprocess.check_output(['git','-C',str(D),'diff','--cached','--name-only','-z']).split(b'\0');staged=[x.decode() for x in staged if x];assert len(staged)==len(rows)+3
# Verify actual staged blobs exactly match all intended owned bytes in one Git process.
proc=subprocess.Popen(['git','-C',str(D),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
for rel in staged:
 proc.stdin.write((':'+rel+'\n').encode());proc.stdin.flush();header=proc.stdout.readline().decode().split();n=int(header[2]);data=proc.stdout.read(n);assert proc.stdout.read(1)==b'\n';assert data==(D/rel).read_bytes(),rel
proc.stdin.close();assert proc.wait()==0
receipt=dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),result='PassedPublicationChecks',checkpointFiles=len(rows)+1,stagedFiles=len(staged),manifestSha256=sha(C/'MANIFEST.sha256'),allCopyHashesVerified=True,allJsonValid=True,allEncodedTextEvidenceRoundTripsVerified=True,currentLinksExist=True,historicalReportBodiesPreserved=history,onlyOwnedFactualDocumentationStaged=True,diffCheck='Passed',stagedBytesVerified=True)
(P/'PUBLICATION_VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
