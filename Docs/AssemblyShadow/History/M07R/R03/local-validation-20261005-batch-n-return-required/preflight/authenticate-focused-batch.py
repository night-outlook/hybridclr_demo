import collections, datetime, hashlib, json, pathlib, shutil, subprocess, tarfile, sys, xml.etree.ElementTree as ET
R=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261005N-identity')
P=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261005N-identity')
import os
os.environ['GIT_SSH_COMMAND']=json.loads((P/'SSH_TRANSPORT.json').read_text())['command']
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
assert len(result['cells'])==len({c['id'] for c in result['cells']})==90
for c in result['cells']:assert load(R/'cells'/(c['id']+'.json'))==c
counts=dict(collections.Counter(c['result'] for c in result['cells']));assert sum(counts.values())==90
for flag in ['R03Accepted','H2Passed','fullLegacyRegressionAcceptance','pureInterpreterExpansionEnabled','qualificationApproved']:assert result[flag] is False
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

assert len(commands) >= 86
negative_ids={pathlib.Path(load(R/'consumer-unity-2022.3.62f2/results.json')['negative']['commandReceipt']).parent.name, pathlib.Path(next(c for c in load(R/'unity-lifecycle/results.json')['cases'] if c['id']=='invalid-key')['receipt']['outerReceipt']).parent.name}
negative_ids.update(pathlib.Path(c['receipt']['path']).parent.name for c in load(R/'build-api/results.json')['commands'] if c['expectedExit']==1)
assert negative_ids <= {d['id'] for d in commands if d['exitCode']==1}
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
 inner=load(p);outer=load(p.parent/'command.json');assert outer['exitCode']==(0 if inner['commandExitCode']==0 else 1) and inner['completion']['clean'] is True and 'error' not in inner and outer['remainingProcessGroup'] is False and outer['postCleanupGroupExists'] is False
 assert inner['result']==('Passed' if inner['commandExitCode']==0 else 'Failed')
 assert inner['policy']=='R02OwnedUnityRoslyn-v2'
 b=inner['compilerBinding'];assert sha(b['path'])==b['sha256']
 for action in inner['completion']['actions']:
  assert action['identity']['kernel']['birth'] and action['identity']['group']==inner['completion']['group'] and 'VBCSCompiler.dll' in action['identity']['command']
 unity.append({'command':p.parent.name,'originalInnerExit':inner['commandExitCode'],'outerExit':outer['exitCode'],'wrapperNormalizesNonzeroInnerToOne':True,'result':inner['result'],'clean':True,'supervisorPid':outer['pid'],'unityPid':inner.get('pid'), 'compilerRetirementActions':inner['completion']['actions']})
assert len(unity)>=7
for rel,n in [('host/baseline-graph/results.json',9),('host/candidate-graph/results.json',9),('host/admission/results.json',35)]:
 d=load(R/rel);assert len(d['cases'])==n and d['failures']==0 and all(c['result']=='Passed' for c in d['cases'])


api=load(R/'build-api/results.json');assert api['result']=='Passed' and api['referenceCoreSha256']=='e22a829a8022d30c6b2b11fe764d12a2383cf882b63a954641e3cd41ea56af6e' and len(api['commands'])==5 and len(api['inputs'])>=425 and len(api['defines'])==115
for f in api['inputs']:assert sha(f['path'])==f['sha256'] and pathlib.Path(f['path']).stat().st_size==f['size']
for c in api['commands']:
 for k in ['receipt','response']:
  f=c[k];assert sha(f['path'])==f['sha256']
 d=load(c['receipt']['path']);assert d['exitCode']==c['expectedExit'] and not d['remainingProcessGroup'] and '/noconfig' in d['command']
for a in api['packageAssemblies']:
 f=a['output'];assert sha(f['path'])==f['sha256']
f=api['completeHelper'];assert sha(f['path'])==f['sha256'] and pathlib.Path(f['path']).stat().st_size==f['size']
oldReceipt=pathlib.Path(next(c for c in api['commands'] if c['expectedExit']==1)['receipt']['path']);oldLog=(oldReceipt.parent/'stdout.log').read_text()+(oldReceipt.parent/'stderr.log').read_text();assert oldLog.count('error CS0266:')==2 and not(R/'build-api/OriginalUnsignedCounts/OriginalUnsignedCounts.dll').exists()

sys.path.insert(0,'/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Tools/AssemblyShadow/R03')
from build_provenance import verify_installation,verify_inventory
sys.path.insert(0,"/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Tools/AssemblyShadow/R03Completion")
from editor_contract import verify as verify_editor
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
if (R/'focused-editor/results.xml').exists():
 editor=load(R/'focused-editor/verification.json');scope=load(R/'focused-editor/scope.json');tree=ET.parse(R/'focused-editor/results.xml').getroot()
 import editor_scope
 mapped=editor_scope.case_map(tree);assert set(mapped)==set(scope['expectedNames']) and len(mapped)==scope['expectedCount']==754
 try:fresh=verify_editor(tree,scope)
 except Exception as error:
  assert editor['result']==load(R/'cells/editor-tests.json')['result']=='Failed'
  fresh={'result':'Failed','cases':len(mapped),'counts':{k:int(tree.get(k)) for k in ['total','passed','failed','skipped','inconclusive']},'readOnlyVerifierError':str(error),'failedCases':[{'name':k,'result':c.get('result'),'message':c.findtext('failure/message'),'stack':c.findtext('failure/stack-trace')} for k,c in mapped.items() if c.get('result')!='Passed'],'xmlSha256':sha(R/'focused-editor/results.xml'),'scopeSha256':sha(R/'focused-editor/scope.json')}
 else:
  assert editor['result']=='Passed' and fresh['cases']==754 and fresh['skipped']==0 and editor['xmlSha256']==sha(R/'focused-editor/results.xml') and editor['scopeSha256']==sha(R/'focused-editor/scope.json')
else:
 cell=load(R/'cells/editor-tests.json');assert cell['result']=='Failed' and cell['error']=='Review any additional package change before selecting Editor tests' and not(R/'focused-editor').exists()
 fresh={'result':'Failed','execution':'NotRun','cases':0,'scope':'Unavailable','xml':'Unavailable','originalCell':cell,'reason':'Source scope rejected before folder creation and Unity Test Runner launch'}
players=[];matrix=load('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Tools/AssemblyShadow/R03/player-cases.json')
control_report=load(R/'producer-controls.json');control_cell=load(R/'cells/producer-controls.json');control_rows={c['id']:c for c in control_report['cases']};selected=('C03-moved-slot','C04-old-AOT-guard','C05-direction-reversal','C07-private-primitive-append');main={c['id']:c for c in matrix['cases']};cases=matrix['cases']+[dict(main[n],id='PC-'+n,producerControl=True) for n in selected]
assert set(control_rows)=={'PC-'+n for n in selected}
assert control_report['result']==control_cell['result'] and control_report['runtimeAcceptance'] is False
if control_cell['result']=='Passed':assert control_cell['evidence']==control_report
for case in cases:
 root=R/'players'/case['id'];cell=control_rows[case['id']] if case.get('producerControl') else load(R/'cells'/(case['id']+'.json'));row={'id':case['id'],'state':cell['result'],'role':case['role'],'evidenceExists':root.exists()}
 if root.exists():
  request=load(root/'request.json');rawpath=root/'raw.json';row['requestSha256']=sha(root/'request.json');row['runId']=request['runId'];matches=[q for q in (R/'commands').glob('*/command.json') if str(root/'request.json') in load(q)['command']];assert len(matches)==1
  cmd=load(matches[0]);row.update(command=matches[0].parent.name,pid=cmd['pid'],exitCode=cmd['exitCode'],rawAvailable=rawpath.exists())
  if rawpath.exists():
   raw=load(rawpath);row.update(rawSha256=sha(rawpath),rawPid=raw['pid'],phase=raw['phase'],finalState=raw['finalState'],invocationResult=raw['invocationResult'],exception=raw['exception']);assert raw['pid']==cmd['pid'] and raw['runId']==request['runId'] and raw['requestSha256']==row['requestSha256']
   verified=load(root/'verification.json');assert verified['rawSha256']==sha(rawpath) and verified['requestSha256']==row['requestSha256'] and verified['launchPid']==cmd['pid'] and verified['runId']==request['runId'] and verified['buildReceiptSha256']==sha(R/'builds'/case['role']/'build-receipt.json')
   try: verdict=verify_raw(request,raw,case,row['requestSha256'],cmd['pid'])
   except Exception as exc:
    row['readOnlyVerifier']='Failed';row['readOnlyError']=str(exc);assert cell['result']==verified['result']=='Failed' and verified['error']==cell['error']==str(exc)
   else:
    row['readOnlyVerifier']='Passed';assert cell['result']==verified['result']=='Passed' and verified==cell['evidence'];assert all(verified[k]==v for k,v in verdict.items())
   row.update(verificationSha256=sha(root/'verification.json'),verificationResult=verified['result'],runtimeProbeAvailable=bool(raw['runtimeProbe']))

 players.append(row)
assert len(players)==23 and len({r['pid'] for r in players})==23 and len({r['runId'] for r in players})==23
identified=sum(r.get('evidence',{}).get('warmWindow',{}).get('identifiedLoopAdmissions',0) for r in control_rows.values());assert identified==control_report['identifiedLoopAdmissions']
assert (control_report['result']=='Passed') == (all(r['result']=='Passed' for r in control_rows.values()) and identified>0)
for name in selected:
 mainreq=load(R/'players'/name/'request.json');controlreq=load(R/'players'/('PC-'+name)/'request.json');assert mainreq['producerControl'] is False and controlreq['producerControl'] is True
 assert mainreq['dlls']==controlreq['dlls'] and mainreq['runId']!=controlreq['runId'] and mainreq['invokeAssembly']==controlreq['invokeAssembly']
 mv=load(R/'players'/name/'verification.json');cv=load(R/'players'/('PC-'+name)/'verification.json');assert mv['buildReceiptSha256']==cv['buildReceiptSha256']
(P/'INTEGRATED_OBSERVATIONS.json').write_text(json.dumps({'kind':'ReadOnlyIntegratedEvidenceAudit','builds':builds,'editor':fresh,'players':players,'producerControls':control_report},indent=2)+'\n')
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
ps=subprocess.run(['ps','-axo','pid=,ppid=,pgid=,stat=,comm='],capture_output=True,text=True,check=True);groups={d['pgid'] for d in commands}; survivors=[]
for line in ps.stdout.splitlines():
 fields=line.split(None,4)
 if len(fields)==5 and int(fields[2]) in groups:survivors.append(line.strip())
audit={'kind':'ReadOnlyCompletionPostrunAuthentication','startUtc':started,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'Passed','indexedLiveFiles':len(idx['files']),'archiveMembers':len(expected),'cells':90,'counts':counts,'commands':commands,'fixtureDlls':15,'inputSubchecks':subchecks,'supervisedUnityCommands':unity,'expectedNegativeCommandIds':sorted(negative_ids),'failedProductUnityCommandIds':[d['command'] for d in unity if d['originalInnerExit']!=0 and d['command'] not in negative_ids],'failedValidationCellIds':[c['id'] for c in result['cells'] if c['result']=='Failed'],'priorCustodyFilesUnchanged':len(prior),'repositories':source,'laterObservedOwnedGroupMembers':survivors,'laterProcessObservationScope':'read-only ps; original cleanup flags are retained unchanged','topLevelHashes':{n:sha(R/n) for n in ['LOCAL_BATCH_RESULT.json','BATCH_EXECUTION.json','evidence-index.json','evidence.tar.gz','seal-receipt.json']}}
(P/'POSTRUN_AUTHENTICATION.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:audit[k] for k in ['status','indexedLiveFiles','archiveMembers','cells','counts','failedValidationCellIds','priorCustodyFilesUnchanged','topLevelHashes']},indent=2))
