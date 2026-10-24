from pathlib import Path
import hashlib,json,subprocess,datetime,os,concurrent.futures
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';P=B/'Preflight-R03-P1-ADMITTED-EXECUTION-20261023-b7e3';O=B/'R03-P1-ADMITTED-EXECUTION-20261023-b7e3';S=B/'Scratch-R03-P1-ADMITTED-EXECUTION-20261023-b7e3';A=B/'AuditOnly-R03-P1-ADMITTED-EXECUTION-20261024-f51d';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-audit-only-p1-20261024-f51d';CP=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-admitted-execution-20261023-b7e3';T=D/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/P1_HISTORICAL_AUDIT_HELPER_2026-10-24'
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1<<20),b''):h.update(x)
 return h.hexdigest()
load=lambda p:json.loads(p.read_text())
start=now();pins={'hybridclr_demo':'ea530e59eef38175738e517110c698ebd31bb07f','hybridclr':'4b2774b066cfc6afd77a8c8aded6bda7ea574f55','hybridclr_unity':'948c0e3b4f8891481301770115e8ba4945eea6de','il2cpp_plus':'e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb'}
assert load(B/'f51d-SOURCE_CI_GATE.json')['result']=='PassedSourceAndSourceMatchedCIReadiness'
for q in [A,C]:assert not q.exists() and not q.is_symlink() and q.resolve()==q
assert A not in C.parents and C not in A.parents
U=Path('/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity')
for root in [W/n for n in pins]+[P,O,S,U.parent.parent]:
 assert A!=root and A not in root.parents and root not in A.parents
reads=[D/'Docs/AssemblyShadow/README.md',D/'Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md',D/'Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md']+[CP/n for n in ['README.md','FINDING.json','LOCAL_RESULT.json','MANIFEST.sha256','preflight/audit.py','preflight/AUDITOR_COMMAND.json','batch/RESULT.json','batch/MANIFEST.json','preflight/INDEPENDENT_PRESERVATION_AFTER.json']]+[T/n for n in ['DESIGN.md','PLAN.md','PRIMARY_SOURCE_AUDIT.md','EVIDENCE.json']]+sorted(T.glob('*.py'))+[D/'Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md']
readbindings=[]
for q in reads:
 text=q.read_text();readbindings.append(dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q)));print('READ',q,flush=True)
source=(T/'audit_historical_helper_successor.py').read_bytes()
old=subprocess.check_output(['git','-C',str(D),'cat-file','blob','c451e0cb7794e624eabb9029db0a35ba28d14592'])
assert source==old.replace(b'verify_admitted_execution_receipt_and_fail_closed_mutations',b'verify_admitted_execution_receipt_and_negative_mutations')
OLD_C=D/'Docs/AssemblyShadow/History/M07R/R03/local-audit-only-p1-20261023-c42a'
OLD_A=B/'AuditOnly-R03-P1-ADMITTED-EXECUTION-20261023-c42a'
for root in [OLD_C,OLD_A]:
 assert root.is_dir() and root.resolve()==root and not root.is_symlink()
 assert A!=root and A not in root.parents and root not in A.parents
for line in (OLD_C/'MANIFEST.sha256').read_text().splitlines():
 h,rel=line.split('  ',1);q=OLD_C/rel;assert q.is_file() and not q.is_symlink() and sha(q)==h
assert len((OLD_C/'MANIFEST.sha256').read_text().splitlines())==197
assert sha(OLD_C/'MANIFEST.sha256')=='2e5d9ad234f0a2c6ec43ba9a2f8761d9b1079fb4db00a2d7591f46e730113f10'
old_snap={}
for label,root in [('c42aCheckpoint',OLD_C),('c42aExternal',OLD_A)]:
 rows=[]
 for q in sorted(root.rglob('*')):
  assert not q.is_symlink()
  if q.is_file():rows.append(dict(path=str(q.relative_to(root)),bytes=q.stat().st_size,sha256=sha(q)))
 old_snap[label]=dict(root=str(root),files=rows)
assert len(old_snap['c42aCheckpoint']['files'])==198
assert load(OLD_C/'LOCAL_RESULT.json')['result']=='FAIL'
for rel in ['audit.py','AUDIT_ONLY_RUN_RECEIPT.json','AUDIT_ONLY_AFTER.json']:
 assert sha(OLD_A/rel)==sha(OLD_C/'stage'/rel)
reads += [OLD_C/n for n in ['README.md','FINDING.json','LOCAL_RESULT.json','MANIFEST.sha256','stage/AUDIT_ONLY_RUN_RECEIPT.json','stage/AUDIT_ONLY_AFTER.json','stage/audit.py']]
for q in reads[-7:]:q.read_bytes();readbindings.append(dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q)))
for args in [['log','-1','--format=%H','--','Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md'],['diff','--exit-code','117cc6b1c2be8050cd2f433ef17db8b3c5138f93',pins['hybridclr_demo'],'--','.',':(exclude)Docs/**',':(exclude).github/workflows/**']]:
 r=subprocess.run(['git','-C',str(D),*args],capture_output=True,text=True);assert r.returncode==0
 if args[0]=='log':assert r.stdout.strip()==pins['hybridclr_demo']
sdk=load(P/'SDK_BEFORE.json')
for row in sdk['files']:
 q=Path(row['path']);assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes'] and (os.readlink(q) if q.is_symlink() else None)==row['symlink']
sdk_paths={Path(sdk['anchor']),Path(sdk['anchor']).parent.parent/'Info.plist'}
for root in sdk['roots']:sdk_paths.update(p for p in Path(root).rglob('*') if p.is_file())
assert sdk_paths=={Path(row['path']) for row in sdk['files']} and len(sdk_paths)==2405
for row in load(O/'MANIFEST.json')['files']:
 q=O/row['path'];assert q.is_file() and not q.is_symlink() and sha(q)==row['sha256'] and q.stat().st_size==row['size']
assert len(load(O/'MANIFEST.json')['files'])==4269
assert sha(O/'RESULT.json')=='f762d292d9601e620a83ecd79cc5e3c5ab85b0ea0a3813fbf472bd716eb1c7e6' and sha(O/'MANIFEST.json')=='4b286c29a7ef36ec4377642b6009804ad532b0ae3166c186866fe74f4246130e'
scratch=load(O/'native-sdk/native-sdk-inputs.json')['files'];assert len(scratch)==1925 and len({row['path'] for row in scratch})==1925
for row in scratch:q=S/row['path'];assert q.is_file() and not q.is_symlink() and q.resolve()==q and sha(q)==row['sha256']
for row in load(P/'SOURCE_BINDINGS.json'):
 q=Path(row['path']);assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes'] and q.read_bytes()==subprocess.check_output(['git','-C',str(W/row['repository']),'cat-file','blob',row['gitBlob']])
cprows=[]
for line in (CP/'MANIFEST.sha256').read_text().splitlines():
 h,rel=line.split('  ',1);q=CP/rel;assert q.is_file() and not q.is_symlink() and sha(q)==h;cprows.append(dict(path=rel,bytes=q.stat().st_size,sha256=h))
assert len(cprows)==2506 and {str(q.relative_to(CP)) for q in CP.rglob('*') if q.is_file()}=={row['path'] for row in cprows}|{'MANIFEST.sha256'}
assert load(CP/'LOCAL_RESULT.json')['result']=='FAIL' and sha(P/'audit.py')=='2b43453f00fd74c1692d55d3c10b7351df45a0a82d08cf551deb0282862848a0'
preflight=[dict(path=str(q.relative_to(P)),bytes=q.stat().st_size,sha256=sha(q)) for q in sorted(P.rglob('*')) if q.is_file() and not q.is_symlink()]
# Bind all original 22 P1 sets and original24 checkpoints plus the earlier two blocked histories.
ret=load(P/'ADMISSION_RETAINED_BEFORE.json');links=0
for item in ret['consumed']:
 raw=Path(item['rawRoot']);scratchroot=Path(item['scratchRoot']);assert sha(raw/'MANIFEST.json')==item['manifestSha256']
 for row in load(raw/'MANIFEST.json')['files']:
  q=raw/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['size']
 for row in load(raw/'native-sdk/native-sdk-inputs.json')['files']:assert sha(scratchroot/row['path'])==row['sha256']
 for row in load(raw/'legacy-host/MANIFEST.json')['files']:
  if row.get('kind')=='Symlink':q=raw/'legacy-host'/row['path'];assert q.is_symlink() and os.readlink(q)==row['target'];links+=1
 ar=Path(item['auditRoot']);assert {str(p) for p in ar.rglob('*') if p.is_file() and not p.is_symlink()}=={row['path'] for row in item['auditFiles']}
 for row in item['auditFiles']:q=Path(row['path']);assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
cps=load(P/'ADMISSION_CHECKPOINTS_BEFORE.json')
for item in cps['checkpoints']:
 root=Path(item['root']);assert sha(root/'MANIFEST.sha256')==item['manifestSha256']
 for row in item['files']:q=root/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
blocked=[]
for key in ['BLOCKED_ADMISSION_BEFORE.json','BLOCKED_6C72_BEFORE.json']:
 item=load(P/key);root=Path(item['checkpoint']);assert sha(root/'MANIFEST.sha256')==item['manifestSha256']
 for row in item['files']:q=root/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
 for row in item['externalFiles']:q=Path(row['path']);assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
 blocked.append(dict(receipt=key,sha256=sha(P/key),files=len(item['files']),externalFiles=len(item['externalFiles'])))
for row in load(O/'legacy-host/MANIFEST.json')['files']:
 if row.get('kind')=='Symlink':q=O/'legacy-host'/row['path'];assert q.is_symlink() and os.readlink(q)==row['target']
assert (W/'hybridclr_unity').resolve()==(D/'Packages/../../hybridclr_unity').resolve()
sp=load(D/'Tools/AssemblyShadow/R03/source-pins.json');assert sp['il2cpp_plus']=='74dbdbea80d83923863303bd2b2c0a87f36541b1'
assert sha(D/'Tools/AssemblyShadow/R03/source-pins.json')==hashlib.sha256(subprocess.check_output(['git','-C',str(D),'show','49c6b62d38d7668be10004ac1e5a030d74894f09:Tools/AssemblyShadow/R03/source-pins.json'])).hexdigest()
def gitcheck(n):
 path=W/n;rows=[]
 for args in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--short'],['remote','-v'],['worktree','list','--porcelain'],['submodule','status','--recursive'],['ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1']]:
  t=now();cmd=['git','-C',str(path),*args];r=subprocess.run(cmd,capture_output=True,text=True,timeout=90);rows.append(dict(argv=cmd,start=t,end=now(),exit=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0
 assert rows[0]['stdout'].strip()==str(path) and rows[1]['stdout'].strip()=='codex/assembly-shadow-r01b-h1' and rows[2]['stdout'].strip()==pins[n] and not rows[3]['stdout'] and rows[-1]['stdout'].split()[0]==pins[n];return n,rows
repos=dict(concurrent.futures.ThreadPoolExecutor(4).map(gitcheck,pins))
assert os.statvfs(B).f_bavail*os.statvfs(B).f_frsize>1024**3
for q in [A,C]:assert not q.exists() and not q.is_symlink()
record=dict(kind='IndependentF51DAuditOnlyAdmission',result='AdmittedBeforeAnyStageCreation',start=start,end=now(),currentPins=pins,executedHistoricalPins=load(P/'EXPECTED.json')['pins'],workspace=str(W),stage=str(A),checkpoint=str(C),originalPreflight=str(P),raw=str(O),scratch=str(S),sourceCIReceiptSha256=sha(B/'f51d-SOURCE_CI_GATE.json'),readBindings=readbindings,rawRegularFiles=4269,rawResultSha256=sha(O/'RESULT.json'),rawManifestSha256=sha(O/'MANIFEST.json'),sdkFiles=2405,sdkBytes=sum(row['bytes'] for row in sdk['files']),scratchFiles=1925,sourceBindings=len(load(P/'SOURCE_BINDINGS.json')),b7e3CheckpointManifestSha256=sha(CP/'MANIFEST.sha256'),b7e3CheckpointFiles=cprows,originalPreflightFiles=preflight,consumedP1Sets=len(ret['consumed']),originalCheckpointSets=cps['count'],historicalNegativeSymlinks=links,blockedHistories=blocked,git=repos,historicalAuditorOnlyTwoHelperEdits=True,consumedC42A=old_snap,originalC42ALocalResult='FAIL',availableBytes=os.statvfs(B).f_bavail*os.statvfs(B).f_frsize,newRootsInitiallyAbsent=True,originalB7E3LocalResult='FAIL',sourceAssertionsUnchanged=True,compilerCoreAndUnityInvoked=False)
q=B/'f51d-ADMISSION_BEFORE.json';assert not q.exists();q.write_text(json.dumps(record,indent=2)+'\n');print('ADMITTED',A,flush=True)
