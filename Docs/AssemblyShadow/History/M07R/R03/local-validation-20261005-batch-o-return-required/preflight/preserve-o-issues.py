"""Preserve actionable Primary issues from original O and read-only exact reproductions."""
import pathlib,json,hashlib,datetime,subprocess
P=pathlib.Path(__file__).resolve().parent;R=P.parent/'R03LocalBatch-20261005O-ln-closure';W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo'
load=lambda p:json.loads(pathlib.Path(p).read_text())
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r=load(R/'LOCAL_BATCH_RESULT.json');assert r['result']=='ReturnRequired' and r['sealStatus']=='Passed';failed=[c for c in r['cells'] if c['result']=='Failed'];replayed=load(P/'FAILED_CONTRACT_REPRODUCTION.json');assert set(replayed['allRuntimeFailedCellsCovered'])=={c['id'] for c in failed if c['id']!='production-entry-integration'}
items=load(P/'ISSUE_DESCRIPTIONS.json');groups=[lambda c:c['id']=='production-entry-integration',lambda c:'Relative codec pin requires explicit authenticated project/owner context' in c['error'],lambda c:c['error']=='Actual linked baseline DLL',lambda c:c['error']=='list indices must be integers or slices, not str'];assert [sum(fn(c) for c in failed) for fn in groups]==[1,17,6,6]
def evidence(p):
 p=pathlib.Path(p);assert p.is_file();return {'path':str(p),'sha256':sha(p),'size':p.stat().st_size}
sourceGroups=[[(D,'Assets/AssemblyShadowDemo/Editor/R03CompletionBuild.cs'),(W/'hybridclr_unity','Editor/AssemblyShadow/Build/ShadowFilteredInputPolicy.cs'),(W/'hybridclr_unity','Editor/AssemblyShadow/Build/AssemblySnapshot.cs'),(W/'hybridclr_unity','Editor/AssemblyShadow/Validation/ShadowAssemblyPolicyValidator.cs')],[(D,'Tools/AssemblyShadow/R03Completion/legacy_runtime.py'),(D,'Tools/AssemblyShadow/m07_results.py'),(D,'Tools/AssemblyShadow/m04_results.py'),(D,'Tools/AssemblyShadow/m03_results.py'),(D,'Tools/AssemblyShadow/native_codec_source.py')],[(D,'Tools/AssemblyShadow/R03Completion/execution_contract.py'),(D,'Tools/AssemblyShadow/m06_results.py')],[(D,'Tools/AssemblyShadow/R03Completion/execution_contract.py'),(D,'Tools/AssemblyShadow/m06_execution_metadata.py'),(D,'Tools/AssemblyShadow/m06_results.py')]]
allSources=[]
for item,fn,sources in zip(items,groups,sourceGroups):
 selected=[c for c in failed if fn(c)];item['affectedCells']=[c['id'] for c in selected];ev=[evidence(R/'cells'/(c['id']+'.json')) for c in selected]
 for repo,name in sources:
  f=repo/name;commit=r['repositories'][repo.name];blob=subprocess.check_output(['git','-C',str(repo),'show',commit+':'+name]);assert blob==f.read_bytes();ev.append(evidence(f));allSources.append({'repository':str(repo),'commit':commit,'path':name,'sha256':sha(f)})
 if selected[0]['id']=='production-entry-integration':
  ev += [evidence(R/'commands/0126/command.json'),evidence(R/'commands/0126/unity-completion.json'),evidence(R/'resource-logs/integration.log')]
  item['reproduction']=['Use the four exact executed repository commits recorded in LOCAL_VALIDATION; the source-bound prescribed batch O command is retained in '+str(P/'runner-exit.json')+'. It has already been executed once; do not retry this root.', 'The runner built six fresh apps, finalized/restored P05, and invoked the exact Unity argv in '+str(R/'commands/0126/command.json')+' using Unity2022.3.62f2.','VerifyProductionEntries emits all five integration/*/eligibility.json files, then calls CompileWithOptions on receiptRoot/return-baseline. ValidateBeforeCompile throws the four policy errors; Unity exits1 without timeout/survivors and no integration.json is emitted.']
  cfg=load(R/'resource-project.json');folder=pathlib.Path(cfg['receiptRoot'])/'integration'
  for f in sorted(folder.glob('*/eligibility.json')):ev.append(evidence(f))
 else:
  cases=[c for c in replayed['cases'] if c['cell'] in item['affectedCells']];assert len(cases)==len(selected)
  ev.append(evidence(P/'FAILED_CONTRACT_REPRODUCTION.json'))
  for c in cases:
   ev += [evidence(c['rawPath']),evidence(c['commandReceipt'])]
   raw=pathlib.Path(c['rawPath']);folder=raw.parent
   if c['cell'].startswith('resource-'):folder=R/'resource-players'/load(raw)['mode']
   for n in ['verification.json','request.json','execution.json','early.json','early.capsule']:
    if (folder/n).exists():ev.append(evidence(folder/n))
  representative=cases[0];item['reproduction']=['Execute only the already-performed original batch O source tuple and command retained in '+str(P/'runner-exit.json')+'; no retry of O or its apps is authorized.', 'The runner launches a fresh process with the exact argv retained in '+representative['commandReceipt']+'; raw output is '+representative['rawPath']+'. All affected cells and exact receipts are listed in this issue.', 'Read-only original verifier replay against the same immutable context/input bytes reproduces every affected error exactly. Tracebacks, PID/hash bindings and separately passing prerequisite checks are in '+str(P/'FAILED_CONTRACT_REPRODUCTION.json')+'. No guard bypass or product reexecution was used.']
  item['representativeTraceback']=representative['traceback'];item['relevantExcerpt']+='\n\n```text\n'+representative['traceback'].strip()+'\n```'
 item['evidence']=list({e['path']:e for e in ev}.values())
covered=[c for item in items for c in item['affectedCells']];assert len(covered)==len(set(covered))==len(failed) and set(covered)=={c['id'] for c in failed}
(P/'PRIMARY_ISSUES.json').write_text(json.dumps({'kind':'R03OPrimaryImplementationIssues','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'issues':items,'allFailedCellsCovered':sorted(covered),'scope':'Only four non-trivial current-source failures requiring Primary; no Local source fix','R03Accepted':False,'H2Passed':False,'qualificationApproved':False},indent=2)+'\n')
(P/'ROOT_CAUSE_SOURCE_BINDINGS.json').write_text(json.dumps({'kind':'ExactGitBlobSourceBindings','sources':list({(v['repository'],v['path']):v for v in allSources}.values()),'noSourceChanges':True},indent=2)+'\n')
print('Preserved four actionable issues covering every original Failed cell:',len(covered))
