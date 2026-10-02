import pathlib,json,hashlib,datetime,shutil,xml.etree.ElementTree as ET
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');R=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261002H-rejection');P=R.parent/'Preflight-R03LocalBatch-20261002H-rejection'
def load(p):return json.loads(p.read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
records=[];matrix=load(W/'hybridclr_demo/Tools/AssemblyShadow/R03/player-cases.json');selected=('C03-moved-slot','C04-old-AOT-guard','C05-direction-reversal','C07-private-primitive-append');main={c['id']:c for c in matrix['cases']};allcases=matrix['cases']+[dict(main[n],id='PC-'+n,producerControl=True) for n in selected];cases={c['id']:c for c in allcases};control_report=load(R/'producer-controls.json');control_rows={c['id']:c for c in control_report['cases']}
for case in allcases:
 root=R/'players'/case['id'];cell=control_rows[case['id']] if case.get('producerControl') else load(R/'cells'/(case['id']+'.json'));row={'case':case['id'],'role':case['role'],'cellState':cell['result'],'cellError':cell.get('error'),'evidencePresent':root.exists()}
 if (root/'raw.json').exists():
  raw=load(root/'raw.json');req=load(root/'request.json');diag=json.loads(raw['diagnostics']) if raw['diagnostics'] else {};recovery=json.loads(raw['recovery']) if raw['recovery'] else {};probe=json.loads(raw['runtimeProbe']) if raw['runtimeProbe'] else None
  row.update(raw=str(root/'raw.json'),rawSha256=sha(root/'raw.json'),requestSha256=sha(root/'request.json'),pid=raw['pid'],runId=raw['runId'],phase=raw['phase'],published=raw['published'],state=raw['finalState'],steps=raw['steps'],value=raw['invocationResult'],delegate=raw['delegateResult'],warmAllocations=raw['warmAllocationCount'],exception=raw['exception'],diagnostic={k:diag.get(k) for k in ['stateCode','lastError','detail','baselineBuildId','patchId','generation']},recovery=recovery,runtimeProbe=probe,nativeMethod=json.loads(raw['nativeMethod']) if raw['nativeMethod'] else None,inputDlls=req['dlls'])
  if raw['beforeWarm'] and raw['afterWarm']:
   before=json.loads(raw['beforeWarm']);after=json.loads(raw['afterWarm']);row.update(before=before,after=after,broadIntegerDeltas={k:after['r02'][k]-v for k,v in before['r02'].items() if type(v)==int and after['r02'][k]!=v})
  if probe and len(probe.get('samples',[]))==6:
   samples=probe['samples'];row['sampleLabels']=[s['label'] for s in samples];row['nativeSpans']=[]
   for a,b in zip(samples,samples[1:]):row['nativeSpans'].append({'from':a['label'],'to':b['label'],'deltas':{k:b['counters'][k]-v for k,v in a['counters'].items()},'events':probe['events'][a['eventEnd']:b['eventEnd']]})
  if (root/'verification.json').exists():row.update(verification=load(root/'verification.json'),verificationSha256=sha(root/'verification.json'))
 records.append(row)
executed=[r for r in records if r.get('rawSha256')];assert len({r['pid'] for r in executed})==len(executed) and len({r['runId'] for r in executed})==len(executed)
source=[]
for repo,rel in [('hybridclr_demo','Tools/AssemblyShadow/R03/runtime_contract.py'),('hybridclr_demo','Tools/AssemblyShadow/R03/rejection_contract.py'),('il2cpp_plus','libil2cpp/vm/AssemblyShadowRuntimeProbe.cpp'),('il2cpp_plus','libil2cpp/vm/AssemblyShadowProbeTypeSnapshot.h'),('hybridclr_demo','Tools/AssemblyShadow/R03/batch_contract.py'),('hybridclr_demo','Tools/AssemblyShadow/R03/run_local.py'),('hybridclr_demo','Tools/AssemblyShadow/R03/PlayerProject/R03Player.cs'),('hybridclr_demo','Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp'),('hybridclr','hybridclr/metadata/InterpreterImage.h'),('hybridclr','hybridclr/metadata/StagedAssembly.cpp'),('il2cpp_plus','libil2cpp/vm/AssemblyShadowTypeResolver.cpp'),('il2cpp_plus','libil2cpp/vm/AssemblyShadowRuntimeProbe.h'),('il2cpp_plus','libil2cpp/vm/AssemblyShadowAllocationProof.h'),('il2cpp_plus','libil2cpp/vm/AssemblyShadowProducerFence.h'),('il2cpp_plus','libil2cpp/vm/AssemblyShadowFinalizerProbe.h'),('il2cpp_plus','libil2cpp/gc/GarbageCollector.cpp'),('il2cpp_plus','libil2cpp/vm/AssemblyShadowObservationCounters.h'),('il2cpp_plus','libil2cpp/vm/Object.cpp')]:
 p=W/repo/rel;dest=P/'diagnostic-source-snapshot'/repo/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);source.append({'path':str(p),'size':p.stat().st_size,'sha256':sha(p),'snapshot':str(dest)})
result=load(R/'LOCAL_BATCH_RESULT.json');report={'kind':'ReadOnlyBatchHRuntimeObservations','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'executedRepositories':result['repositories'],'result':result['result'],'runtime':records,'requiredWarmCases':[c['id'] for c in matrix['cases'] if c.get('warmCertificate')],'failedCells':[c for c in result['cells'] if c['result']=='Failed'],'sourceEvidence':source,'editorAggregate':ET.parse(R/'editor-results.xml').getroot().attrib if (R/'editor-results.xml').exists() else None,'excludedCoverage':load(R/'editor-scope.json')['excluded'] if (R/'editor-scope.json').exists() else None,'producerControls':control_report,'historicalAttribution':'E/F producer identities remain as originally recorded; new H actor observations cannot establish historical finalizer/delegate attribution','limits':'No Local implementation, probe addition, retry, Player relaunch, counter relaxation, warm-up change or raw evidence rewrite'}
(P/'DIAGNOSTIC_FINDINGS.json').write_text(json.dumps(report,indent=2)+'\n')
print('Preserved',len(executed),'unique runtime observations; failed cells',len(report['failedCells']))

for row in records:
 if cases[row['case']].get('warmCertificate'):
  p=row.get('runtimeProbe') or {};print(row['case'],row['cellState'],row.get('cellError'),'events',len(p.get('events',[])), 'fence',p.get('producerFence'))
