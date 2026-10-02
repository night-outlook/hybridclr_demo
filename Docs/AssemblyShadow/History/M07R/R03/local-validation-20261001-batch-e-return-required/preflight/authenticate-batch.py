import collections, datetime, hashlib, json, pathlib, shutil, subprocess, tarfile, sys, xml.etree.ElementTree as ET
R=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001E-provenance')
P=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261001E-provenance')
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
 ms=t.getmembers();assert len(ms)==len(expected)==len({m.name for m in ms})==len(idx['files'])+1
 for m in ms:
  assert m.isfile() and m.name in expected
  e=expected[m.name];assert m.size==e['size'] and hashlib.sha256(t.extractfile(m).read()).hexdigest()==e['sha256'],m.name
assert receipt==result['seal'] and sha(R/'evidence.tar.gz')==receipt['archiveSha256'] and sha(R/'evidence-index.json')==receipt['indexSha256']
assert sha(R/'BATCH_EXECUTION.json')==result['executionLedgerSha256'] and result['cells']==ledger['cells']
assert len(result['cells'])==len({c['id'] for c in result['cells']})==36
for c in result['cells']:assert load(R/'cells'/(c['id']+'.json'))==c
counts=dict(collections.Counter(c['result'] for c in result['cells']));assert sum(counts.values())==36
for flag in ['R03Accepted','H2Passed','fullLegacyRegressionAcceptance','pureInterpreterExpansionEnabled']:assert result[flag] is False
commands=[]
for q in sorted((R/'commands').glob('*/command.json')):
 d=load(q);assert sha(q.parent/'stdout.log')==d['stdoutSha256'];assert sha(q.parent/'stderr.log')==d['stderrSha256']
 if d['remainingProcessGroup']:assert load(q.parent/'process-group-before-cleanup.json')==d['processGroupBeforeCleanup']
 commands.append({'id':q.parent.name,'exitCode':d['exitCode'],'remainingProcessGroup':d['remainingProcessGroup'],'pid':d['pid'],'pgid':d['pgid'],'lifetimePolicy':d['lifetimePolicy']})
for d in commands:
 if '0005'<=d['id']<='0012':assert d['exitCode']==0 and d['remainingProcessGroup'] is False
 assert d['remainingProcessGroup'] is False
inventory=load(R/'host/player-fixtures/inventory.json');assert len(inventory['files'])==15
for f in inventory['files']:assert sha(R/'host/player-fixtures'/f['path'])==f['sha256']

assert 60 <= len(commands) <=79
assert {'0048','0050','0055'} <= {d['id'] for d in commands if d['exitCode']==1}
subchecks=[]
for rel,count in [('fixture-audit/results.json',33),('consumer-unity-2022.3.62f2/results.json',33),('unity-lifecycle/results.json',2)]:
 d=load(R/rel);assert d['result']=='Passed' and len(d['cases'])==count and len({c['id'] for c in d['cases']})==count
 subchecks.append({'path':rel,'sha256':sha(R/rel),'cases':count,'result':'Passed'})
a=load(R/'fixture-audit/results.json')
for c in a['cases']:
 assert sha(c['input'])==c['inputSha256'] and sha(c['source'])==c['sourceSha256']
 for peer in c['peers']:assert sha(peer['path'])==peer['sha256']
 for ref in c['references']:assert ref['flags']&1==0 and ref['keyBytes']==(8 if ref['name']=='mscorlib' else 0)
consumer=load(R/'consumer-unity-2022.3.62f2/results.json')
for c in consumer['cases']:
 b=c['consumer'];assert sha(b['path'])==b['sha256'] and pathlib.Path(b['path']).stat().st_size==b['size'] and c['result']=='Passed'
for b in consumer['toolchain']:assert sha(b['path'])==b['sha256']
negative=load(consumer['negative']['commandReceipt']);assert negative['exitCode']==1 and not negative['remainingProcessGroup']
negativeFolder=pathlib.Path(consumer['negative']['commandReceipt']).parent;output=(negativeFolder/'stdout.log').read_text()+(negativeFolder/'stderr.log').read_text();assert 'CS0009' in output and 'invalid public key' in output.lower()
assert not(R/'consumer-unity-2022.3.62f2/negative/Consumer.dll').exists() and not(R/'unity-lifecycle/invalid-key.marker').exists();assert (R/'unity-lifecycle/valid.marker').read_text()=='R03CompilerProbe-v1'
unity=[]
for p in sorted((R/'commands').glob('*/unity-completion.json')):
 inner=load(p);outer=load(p.parent/'command.json');assert inner['commandExitCode']==outer['exitCode'] and inner['completion']['clean'] is True and 'error' not in inner and outer['remainingProcessGroup'] is False and outer['postCleanupGroupExists'] is False
 assert inner['result']==('Passed' if inner['commandExitCode']==0 else 'Failed')
 assert inner['policy']=='R02OwnedUnityRoslyn-v2' and len(inner['completion']['actions'])==1
 b=inner['compilerBinding'];assert sha(b['path'])==b['sha256']
 action=inner['completion']['actions'][0];assert action['identity']['kernel']['birth'] and action['identity']['group']==inner['completion']['group'] and 'VBCSCompiler.dll' in action['identity']['command']
 unity.append({'command':p.parent.name,'originalInnerExit':inner['commandExitCode'],'result':inner['result'],'clean':True,'supervisorPid':outer['pid'],'unityPid':inner.get('pid'), 'compilerRetirementActions':inner['completion']['actions']})
assert len(unity)==7
for rel,n in [('host/baseline-graph/results.json',9),('host/candidate-graph/results.json',9),('host/admission/results.json',35)]:
 d=load(R/rel);assert len(d['cases'])==n and d['failures']==0 and all(c['result']=='Passed' for c in d['cases'])


api=load(R/'build-api/results.json');assert api['result']=='Passed' and api['referenceCoreSha256']=='e22a829a8022d30c6b2b11fe764d12a2383cf882b63a954641e3cd41ea56af6e' and len(api['commands'])==5 and len(api['inputs'])==425 and len(api['defines'])==115
for f in api['inputs']:assert sha(f['path'])==f['sha256'] and pathlib.Path(f['path']).stat().st_size==f['size']
for c in api['commands']:
 for k in ['receipt','response']:
  f=c[k];assert sha(f['path'])==f['sha256']
 d=load(c['receipt']['path']);assert d['exitCode']==c['expectedExit'] and not d['remainingProcessGroup'] and '/noconfig' in d['command']
for a in api['packageAssemblies']:
 f=a['output'];assert sha(f['path'])==f['sha256']
f=api['completeHelper'];assert sha(f['path'])==f['sha256'] and pathlib.Path(f['path']).stat().st_size==f['size']
oldLog=(R/'commands/0055/stdout.log').read_text()+(R/'commands/0055/stderr.log').read_text();assert oldLog.count('error CS0266:')==2 and not(R/'build-api/OriginalUnsignedCounts/OriginalUnsignedCounts.dll').exists()

sys.path.insert(0,'/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Tools/AssemblyShadow/R03')
from build_provenance import verify_installation,verify_inventory
from editor_scope import verify_editor
from batch_contract import verify_raw
builds=[]
for role in ['candidate-release','reference-release','candidate-debug','candidate-off']:
 root=R/'builds'/role;receipt=load(root/'build-receipt.json');project=R/'projects'/role;manifest=load(project/'source-inputs.json')
 assert receipt['schemaVersion']==2 and receipt['result']=='Passed' and receipt['nonGeneratedCorePreserved'] and receipt['errors']==0
 verify_inventory(pathlib.Path(receipt['outputPath']),receipt['playerFiles']);binding=verify_installation(receipt,project,R,manifest['repositories'])
 cell=load(R/'cells'/('build-'+role+'.json'));assert cell['result']=='Passed' and cell['evidence']['nativeBinding']==binding
 binary=list((pathlib.Path(receipt['outputPath'])/'Contents/MacOS').iterdir());assert len(binary)==1
 assert subprocess.check_output(['lipo','-archs',str(binary[0])],text=True).strip()=='arm64'
 builds.append({'role':role,'receiptSha256':sha(root/'build-receipt.json'),'schemaVersion':2,'binding':binding,'playerFiles':len(receipt['playerFiles']),'installedBefore':len(receipt['installedBefore']),'installedAfter':len(receipt['installedAfter']),'buildGuid':receipt.get('buildGuid')})
editor=load(R/'editor-verification.json');fresh=verify_editor(ET.parse(R/'editor-results.xml').getroot(),load(R/'editor-scope.json'));assert editor['result']==fresh['result']=='Passed' and fresh['cases']==754 and fresh['skipped']==0
assert editor['sha256']==sha(R/'editor-results.xml') and editor['scopeSha256']==sha(R/'editor-scope.json')
players=[];matrix=load('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Tools/AssemblyShadow/R03/player-cases.json')
for case in matrix['cases']:
 root=R/'players'/case['id'];cell=load(R/'cells'/(case['id']+'.json'));row={'id':case['id'],'state':cell['result'],'role':case['role'],'evidenceExists':root.exists()}
 if root.exists():
  request=load(root/'request.json');rawpath=root/'raw.json';row['requestSha256']=sha(root/'request.json');row['runId']=request['runId'];matches=[q for q in (R/'commands').glob('*/command.json') if str(root/'request.json') in load(q)['command']];assert len(matches)==1
  cmd=load(matches[0]);row.update(command=matches[0].parent.name,pid=cmd['pid'],exitCode=cmd['exitCode'],rawAvailable=rawpath.exists())
  if rawpath.exists():
   raw=load(rawpath);row.update(rawSha256=sha(rawpath),rawPid=raw['pid'],phase=raw['phase'],finalState=raw['finalState'],invocationResult=raw['invocationResult'],exception=raw['exception']);assert raw['pid']==cmd['pid'] and raw['runId']==request['runId'] and raw['requestSha256']==row['requestSha256']
   try:
    verdict=verify_raw(request,raw,case,row['requestSha256'],cmd['pid']);row['readOnlyVerifier']='Passed';assert cell['result']=='Passed';sealed=load(root/'verification.json');assert sealed['rawSha256']==sha(rawpath) and sealed['requestSha256']==row['requestSha256']
   except Exception as exc:
    row['readOnlyVerifier']='Failed';row['readOnlyError']=str(exc);assert cell['result']=='Failed'
 players.append(row)
assert len(players)==19
(P/'INTEGRATED_OBSERVATIONS.json').write_text(json.dumps({'kind':'ReadOnlyIntegratedEvidenceAudit','builds':builds,'editor':fresh,'players':players},indent=2)+'\n')
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
audit={'kind':'ReadOnlyPostrunAuthentication','startUtc':started,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'Passed','indexedLiveFiles':len(idx['files']),'archiveMembers':len(expected),'cells':36,'counts':counts,'commands':commands,'fixtureDlls':15,'inputSubchecks':subchecks,'supervisedUnityCommands':unity,'expectedNegativeCommandIds':['0048','0050','0055'],'failedProductUnityCommandIds':[],'failedValidationCellIds':[c['id'] for c in result['cells'] if c['result']=='Failed'],'priorCustodyFilesUnchanged':len(prior),'repositories':source,'laterObservedOwnedGroupMembers':survivors,'laterProcessObservationScope':'read-only ps; original cleanup flags are retained unchanged','topLevelHashes':{n:sha(R/n) for n in ['LOCAL_BATCH_RESULT.json','BATCH_EXECUTION.json','evidence-index.json','evidence.tar.gz','seal-receipt.json']}}
(P/'POSTRUN_AUTHENTICATION.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k not in ['repositories','commands']},indent=2))
