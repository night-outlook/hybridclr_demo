from pathlib import Path
import json,hashlib,subprocess,datetime,re
D=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');BASE=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');P=BASE/'Preflight-R03IRLocal-20261009C-capacity-retry';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-c-custody-blocked';head='e6f918bf6c756251982eef47f255eaa71b11e1d4';start=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(f):
 with Path(f).open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
rows=[]
for line in (C/'MANIFEST.sha256').read_text().splitlines():
 h,n=line.split('  ',1);assert sha(C/n)==h;rows.append(n)
actual={str(f.relative_to(C)) for f in C.rglob('*') if f.is_file()};assert actual==set(rows)|{'MANIFEST.sha256'}
copies=json.loads((C/'COPY_BINDINGS.json').read_text());chunks=0
for row in copies:
 assert sha(row['originalPath'])==row['sha256']
 if row['transport']=='exactCopy':assert sha(C/row['checkpointPath'])==row['sha256']
 else:
  h=hashlib.sha256();total=0
  for part in row['parts']:
   data=(C/part['path']).read_bytes();assert len(data)==part['bytes'] and hashlib.sha256(data).hexdigest()==part['sha256'];h.update(data);total+=len(data);chunks+=1
  assert h.hexdigest()==row['sha256'] and total==row['bytes']
for row in json.loads((C/'SOURCE_BINDINGS.json').read_text()):
 assert sha(C/row['snapshot'])==row['sha256'];raw=subprocess.check_output(['git','-C',row['repository'],'show',row['commit']+':'+row['path']]);assert hashlib.sha256(raw).hexdigest()==row['sha256']
jsons=0
for f in C.rglob('*.json'):json.loads(f.read_text());jsons+=1
for f in C.rglob('*.jsonl'):
 for line in f.read_text().splitlines():json.loads(line)
links=0
for n in ['LOCAL_VALIDATION.md','RETURN_TO_WEB.md']:
 f=D/'Docs/AssemblyShadow/Handoff'/n;old=subprocess.check_output(['git','-C',str(D),'show',head+':'+str(f.relative_to(D))]).decode();body=old.split('\n\n',1)[1].replace('## Current ','## Historical ',1);new=f.read_text();assert new.endswith(body);section=new[:-len(body)]
 for target in re.findall(r'\]\(([^)]+)\)',section):
  assert not target.startswith('http');assert (f.parent/target).exists(),target;links+=1
for f in C.rglob('*'):
 assert not f.is_symlink()
 if f.is_file():assert f.stat().st_size<50*1024**2
assert not (BASE/'R03IRLocal-20261009C-capacity-retry').exists() and not (BASE/'Storage-R03IRLocal-20261009C-capacity-retry').exists()
subprocess.run(['git','-C',str(D),'diff','--check'],check=True)
owned=['Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md','Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md',str(C.relative_to(D))]
status=subprocess.check_output(['git','-C',str(D),'status','--porcelain'],text=True);assert all(any(line[3:].rstrip('/')==x or line[3:].startswith(x+'/') for x in owned) for line in status.splitlines())
subprocess.run(['git','-C',str(D),'add','--',*owned[:2]],check=True)
# Exact Local-owned checkpoint includes deliberate raw logs and csproj snapshots ignored globally.
subprocess.run(['git','-C',str(D),'add','--force','--',owned[2]],check=True)
subprocess.run(['git','-C',str(D),'diff','--cached','--check'],check=True)
staged=subprocess.check_output(['git','-C',str(D),'diff','--cached','--name-only','-z']).decode().split('\0')[:-1];assert len(staged)==len(actual)+2
assert all(any(n==x or n.startswith(x+'/') for x in owned) for n in staged)
# Stream each index blob and compare bytes without creating any runtime output.
proc=subprocess.Popen(['git','-C',str(D),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
for n in staged:
 proc.stdin.write((':'+n+'\n').encode());proc.stdin.flush();header=proc.stdout.readline().decode().split();assert header[1]=='blob';count=int(header[2]);h=hashlib.sha256();left=count
 while left:
  data=proc.stdout.read(min(left,1024**2));assert data;h.update(data);left-=len(data)
 assert proc.stdout.read(1)==b'\n';assert h.hexdigest()==sha(D/n)
proc.stdin.close();assert proc.wait(timeout=60)==0
record={'state':'Passed','startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifestSha256':sha(C/'MANIFEST.sha256'),'manifestFiles':len(rows),'sourceBindings':'Passed','copiedFiles':len(copies),'largeMapParts':chunks,'orderedReassembly':'Passed','jsonFiles':jsons,'newReportLinks':links,'historicalReportTailPreserved':True,'stagedByteEquality':'Passed','stagedFiles':len(staged),'stagedScope':owned,'gitDiffCheck':'Passed','allFourSourceAuthority':'preflight/FINAL_PREFLIGHT_SOURCE_AUTHORITY.json','runtimeBatch':'NotRun','coreSeal':'Unavailable'}
with (P/'PUBLICATION_VALIDATION.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps(record))
