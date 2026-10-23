from pathlib import Path
import json,hashlib,os,datetime,subprocess,concurrent.futures
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');tag='R03-P1-ADMITTED-EXECUTION-20261023-b7e3';ad=json.loads((B/('Admission-'+tag+'.json')).read_text());E=ad['EXPECTED.json'];W=Path(E['workspace']);D=W/'hybridclr_demo';P=Path(E['preflight'])
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for q in iter(lambda:f.read(1<<20),b''):h.update(q)
 return h.hexdigest()
load=lambda p:json.loads(p.read_text())
def save(n,r):
 p=P/n;assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
start=now();r=load(Path(E['output'])/'RESULT.json');assert r['commandLifetimeUnverified'] is False
sdk=load(P/'SDK_BEFORE.json')
for b in sdk['files']:
 q=Path(b['path']);assert sha(q)==b['sha256'] and q.stat().st_size==b['bytes'] and (os.readlink(q) if q.is_symlink() else None)==b['symlink']
allpaths={Path(sdk['anchor']),Path(sdk['anchor']).parent.parent/'Info.plist'}
for root in sdk['roots']:allpaths.update(p for p in Path(root).rglob('*') if p.is_file())
assert allpaths=={Path(b['path']) for b in sdk['files']}
for b in load(P/'SOURCE_BINDINGS.json'):assert sha(Path(b['path']))==b['sha256']
ret=ad['ADMISSION_RETAINED_BEFORE.json'];links=0
for item in ret['consumed']:
 raw=Path(item['rawRoot']);scratch=Path(item['scratchRoot']);assert sha(raw/'MANIFEST.json')==item['manifestSha256']
 for b in load(raw/'MANIFEST.json')['files']:
  q=raw/b['path'];assert sha(q)==b['sha256'] and q.stat().st_size==b['size']
 for b in load(raw/'native-sdk/native-sdk-inputs.json')['files']:assert sha(scratch/b['path'])==b['sha256']
 for b in load(raw/'legacy-host/MANIFEST.json')['files']:
  if b.get('kind')=='Symlink':
   q=raw/'legacy-host'/b['path'];assert q.is_symlink() and os.readlink(q)==b['target'];links+=1
 audit=Path(item['auditRoot']);assert {str(p) for p in audit.rglob('*') if p.is_file() and not p.is_symlink()}=={b['path'] for b in item['auditFiles']}
 for b in item['auditFiles']:q=Path(b['path']);assert sha(q)==b['sha256'] and q.stat().st_size==b['bytes']
for item in ad['ADMISSION_CHECKPOINTS_BEFORE.json']['checkpoints']:
 root=Path(item['root']);assert sha(root/'MANIFEST.sha256')==item['manifestSha256']
 assert {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}=={b['path'] for b in item['files']}|{'MANIFEST.sha256'}
 for b in item['files']:q=root/b['path'];assert sha(q)==b['sha256'] and q.stat().st_size==b['bytes']
for name,key in [('e1e5','BLOCKED_ADMISSION_BEFORE.json'),('6c72','BLOCKED_6C72_BEFORE.json')]:
 before=ad[key];root=Path(before['checkpoint']);assert sha(root/'MANIFEST.sha256')==before['manifestSha256']
 assert {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}=={b['path'] for b in before['files']}|{'MANIFEST.sha256'}
 for b in before['files']:q=root/b['path'];assert sha(q)==b['sha256'] and q.stat().st_size==b['bytes']
 for b in before['externalFiles']:q=Path(b['path']);assert sha(q)==b['sha256'] and q.stat().st_size==b['bytes']
 if name=='e1e5':
  bp=Path(before['externalPreflight']);assert {str(p) for p in bp.rglob('*') if p.is_file() and not p.is_symlink()}=={b['path'] for b in before['externalFiles']}
 save('BLOCKED_'+name.upper()+'_INDEPENDENT_AFTER.json',dict(result='Preserved',originalState='PrerequisiteBlocked_0of25_CoreNotRun',checkpoint=str(root),checkpointFilesVerified=len(before['files']),externalFilesVerified=len(before['externalFiles']),manifestSha256=before['manifestSha256'],beforeReceiptSha256=sha(P/key),outcomesReclassified=False))
for stem in ['20261022-e1e5','20261023-6c72']:
 for prefix in ['Preflight-R03-P1-ADMITTED-EXECUTION-','R03-P1-ADMITTED-EXECUTION-','Scratch-R03-P1-ADMITTED-EXECUTION-']:
  if stem=='20261022-e1e5' and prefix.startswith('Preflight'):continue
  q=B/(prefix+stem);assert not q.exists() and not q.is_symlink()
def check(n):
 records=[];path=W/n
 for args in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--short'],['remote','-v'],['worktree','list','--porcelain'],['submodule','status','--recursive'],['ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1']]:
  t=now();argv=['git','-C',str(path),*args];c=subprocess.run(argv,capture_output=True,text=True,timeout=90);records.append(dict(argv=argv,start=t,end=now(),exit=c.returncode,stdout=c.stdout,stderr=c.stderr));assert c.returncode==0
 assert records[0]['stdout'].strip()==str(path) and records[1]['stdout'].strip()=='codex/assembly-shadow-r01b-h1' and records[2]['stdout'].strip()==E['pins'][n] and not records[3]['stdout'] and records[-1]['stdout'].split()[0]==E['pins'][n];return n,records
records=dict(concurrent.futures.ThreadPoolExecutor(4).map(check,E['pins']))
save('INDEPENDENT_PRESERVATION_AFTER.json',dict(result='Preserved',start=start,end=now(),sourcePins=E['pins'],sdkFiles=len(sdk['files']),sdkBytes=sum(b['bytes'] for b in sdk['files']),sourceBindingsPreserved=True,installedSdkUnchanged=True,consumedP1RawScratchAuditSets=len(ret['consumed']),originalCheckpointSets=ad['ADMISSION_CHECKPOINTS_BEFORE.json']['count'],negativeControlSymlinks=links,separateBlockedCheckpoints=['e1e5','6c72'],blockedPreparerOrCoreResumed=False,rawAggregateReclassified=False,rawAggregateResult=r['result'],fourGitRepositories=records,acceptanceFlagsRemainFalse=True))
print('Independent source/SDK/history preservation Passed')
