import collections, datetime, hashlib, json, pathlib, shutil, subprocess, tarfile
R=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930B-lifetime')
P=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20260930B-lifetime')
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(pathlib.Path(p).read_text())
def git(path,*args):return subprocess.check_output(['git','-C',str(path),*args],text=True).strip()
started=datetime.datetime.now(datetime.timezone.utc).isoformat();idx=load(R/'evidence-index.json'); result=load(R/'LOCAL_BATCH_RESULT.json');ledger=load(R/'BATCH_EXECUTION.json'); receipt=load(R/'seal-receipt.json')
for f in idx['files']:
 p=R/f['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==f['size'] and sha(p)==f['sha256'],p
expected={f['path']:f for f in idx['files']};expected['evidence-index.json']={'size':(R/'evidence-index.json').stat().st_size,'sha256':sha(R/'evidence-index.json')}
with tarfile.open(R/'evidence.tar.gz','r:gz') as t:
 ms=t.getmembers();assert len(ms)==len(expected)==len({m.name for m in ms})==408
 for m in ms:
  assert m.isfile() and m.name in expected
  e=expected[m.name];assert m.size==e['size'] and hashlib.sha256(t.extractfile(m).read()).hexdigest()==e['sha256'],m.name
assert receipt==result['seal'] and sha(R/'evidence.tar.gz')==receipt['archiveSha256'] and sha(R/'evidence-index.json')==receipt['indexSha256']
assert sha(R/'BATCH_EXECUTION.json')==result['executionLedgerSha256'] and result['cells']==ledger['cells']
assert len(result['cells'])==len({c['id'] for c in result['cells']})==36
for c in result['cells']:assert load(R/'cells'/(c['id']+'.json'))==c
counts=dict(collections.Counter(c['result'] for c in result['cells']));assert counts=={'Passed':12,'Failed':5,'Blocked':19}
for flag in ['R03Accepted','H2Passed','fullLegacyRegressionAcceptance','pureInterpreterExpansionEnabled']:assert result[flag] is False
commands=[]
for q in sorted((R/'commands').glob('*/command.json')):
 d=load(q);assert sha(q.parent/'stdout.log')==d['stdoutSha256'];assert sha(q.parent/'stderr.log')==d['stderrSha256']
 if d['remainingProcessGroup']:assert load(q.parent/'process-group-before-cleanup.json')==d['processGroupBeforeCleanup']
 commands.append({'id':q.parent.name,'exitCode':d['exitCode'],'remainingProcessGroup':d['remainingProcessGroup'],'pid':d['pid'],'pgid':d['pgid'],'lifetimePolicy':d['lifetimePolicy']})
for d in commands:
 if '0005'<=d['id']<='0012':assert d['exitCode']==0 and d['remainingProcessGroup'] is False
 if '0013'<=d['id']<='0017':assert d['exitCode']==1 and d['remainingProcessGroup'] is True
inventory=load(R/'host/player-fixtures/inventory.json');assert len(inventory['files'])==15
for f in inventory['files']:assert sha(R/'host/player-fixtures'/f['path'])==f['sha256']
prior=load(P/'prior-evidence-custody.json')
for p,h in prior.items():assert sha(p)==h,(p,h)
source=[]
for name,h in result['repositories'].items():
 if name not in ('hybridclr_demo','hybridclr','hybridclr_unity','il2cpp_plus'):continue
 path=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r')/name
 row={'path':str(path),'toplevel':git(path,'rev-parse','--show-toplevel'),'branch':git(path,'branch','--show-current'),'commit':git(path,'rev-parse','HEAD'),'status':git(path,'status','--short'),'remotes':git(path,'remote','-v'),'worktrees':git(path,'worktree','list','--porcelain'),'remoteHead':git(path,'ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1')}
 assert row['toplevel']==str(path) and row['commit']==h and row['status']=='' and row['branch']=='codex/assembly-shadow-r01b-h1' and row['remoteHead'].split()[0]==h;source.append(row)
retained={'batchRoot':str(R),'referenceWorktrees':[],'compiledFiles':[],'isolatedProjects':[]}
for name,path in result['retainedReferenceWorktrees'].items():
 row={'path':path,'commit':git(path,'rev-parse','HEAD'),'branch':git(path,'branch','--show-current'),'status':git(path,'status','--short')};assert row['status']=='' and row['branch']=='';retained['referenceWorktrees'].append(row)
for directory in ['bin','obj']:
 for p in sorted((R/directory).rglob('*')):
  if p.is_file():retained['compiledFiles'].append({'path':str(p),'size':p.stat().st_size,'sha256':sha(p)})
for project in sorted((R/'projects').iterdir()):
 row={'path':str(project),'exists':project.is_dir(),'excludedCaches':[],'compilerInputs':[]}
 for name in ['Library','Temp','Logs','HybridCLRData','obj']:
  p=project/name
  if p.exists():row['excludedCaches'].append({'path':str(p),'fileCount':sum(1 for x in p.rglob('*') if x.is_file())})
 for p in sorted((project/'Library/Bee').rglob('*.rsp')):
  if 'UnityEngine.UI' in p.name:
   dest=P/'compiler-inputs'/project.name/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);row['compilerInputs'].append({'path':str(p),'sha256':sha(p),'readOnlyCopy':str(dest)})
 row['missingBuildReceipt']=not(R/'builds'/project.name/'build-receipt.json').exists();retained['isolatedProjects'].append(row)
(P/'RETAINED_LIVE_ROOTS.json').write_text(json.dumps(retained,indent=2)+'\n')
ps=subprocess.run(['ps','-axo','pid=,ppid=,pgid=,stat=,comm='],capture_output=True,text=True,check=True);groups={d['pgid'] for d in commands if d['remainingProcessGroup']}; survivors=[]
for line in ps.stdout.splitlines():
 fields=line.split(None,4)
 if len(fields)==5 and int(fields[2]) in groups:survivors.append(line.strip())
audit={'kind':'ReadOnlyPostrunAuthentication','startUtc':started,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'Passed','indexedLiveFiles':len(idx['files']),'archiveMembers':len(expected),'cells':36,'counts':counts,'commands':commands,'fixtureDlls':15,'priorCustodyFilesUnchanged':len(prior),'repositories':source,'laterObservedOwnedGroupMembers':survivors,'laterProcessObservationScope':'read-only ps; original cleanup flags are retained unchanged','topLevelHashes':{n:sha(R/n) for n in ['LOCAL_BATCH_RESULT.json','BATCH_EXECUTION.json','evidence-index.json','evidence.tar.gz','seal-receipt.json']}}
(P/'POSTRUN_AUTHENTICATION.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k not in ['repositories','commands']},indent=2))
