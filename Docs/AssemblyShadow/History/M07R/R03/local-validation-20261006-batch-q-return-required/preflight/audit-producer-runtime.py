import datetime,pathlib,json,hashlib,sys
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261006Q-lp-repair';R=P.parent/'R03LocalBatch-20261006Q-lp-repair'
sys.path.insert(0,str(D/'Tools/AssemblyShadow/R03'))
from runtime_contract import analyze_window,verify_warm,verify_producer_control,verify_primitive_layout,COLD,COUNTERS
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
start=datetime.datetime.now(datetime.timezone.utc).isoformat();matrix=load(D/'Tools/AssemblyShadow/R03/player-cases.json');warm=[c for c in matrix['cases'] if c.get('warmCertificate')];selected=('C03-moved-slot','C04-old-AOT-guard','C05-direction-reversal','C07-private-primitive-append');main={c['id']:c for c in matrix['cases']};cases=warm+[dict(main[n],id='PC-'+n,producerControl=True) for n in selected];rows=[];bindings=[]
for c in cases:
 root=R/'players'/c['id'];rawpath=root/'raw.json';row={'case':c['id'],'kind':'NaturalControl' if c.get('producerControl') else 'StrictIsolatedMain','originalCellOrDiagnosticResult':load(root/'verification.json')['result'],'rawPath':str(rawpath),'rawSha256':sha(rawpath),'verificationSha256':sha(root/'verification.json'),'checks':{}}
 raw=load(rawpath);request=load(root/'request.json');probe=json.loads(raw['runtimeProbe']);row.update(runId=raw['runId'],pid=raw['pid'],requestSha256=sha(root/'request.json'),target=probe.get('target'),ownerThread=probe.get('ownerThread'),producerFence=probe.get('producerFence'),allEvents=probe.get('events'))
 before=json.loads(raw['beforeWarm'])['r02'];after=json.loads(raw['afterWarm'])['r02']
 def check(name,fn):
  try:record=fn()
  except Exception as e:row['checks'][name]={'status':'Failed','error':str(e)}
  else:row['checks'][name]={'status':'Passed','evidence':record}
 def window():
  p,a,b=analyze_window(raw['runtimeProbe'],before,after,request['invokeAssembly']);spans=[]
  for left,right in zip(p['samples'],p['samples'][1:]):
   events=p['events'][left['eventEnd']:right['eventEnd']]
   for k in COLD:assert right['counters'][k]-left['counters'][k]==sum(e['amount'] for e in events if e['metric']==k)
   spans.append({'from':left['label'],'to':right['label'],'events':events,'delta':{k:right['counters'][k]-left['counters'][k] for k in COUNTERS}})
  return {'sampleLabels':[s['label'] for s in p['samples']],'spans':spans,'exactLoopDelta':{k:b[k]-a[k] for k in COUNTERS}}
 check('completeWindowAndReconciliation',window)
 if c.get('producerControl'):check('naturalProducerDiagnostic',lambda:verify_producer_control(raw['runtimeProbe'],before,after,request['invokeAssembly']))
 else:check('strictIsolatedWarmCertificate',lambda:verify_warm(raw['runtimeProbe'],before,after,request['invokeAssembly']))
 if c['id'].endswith('C07-private-primitive-append'):check('positivePhysicalLayoutSubcheck',lambda:verify_primitive_layout(raw['runtimeProbe']))
 rows.append(row)
for n in selected:
 m=load(R/'players'/n/'request.json');c=load(R/'players'/('PC-'+n)/'request.json');mv=load(R/'players'/n/'verification.json');cv=load(R/'players'/('PC-'+n)/'verification.json')
 assert m['dlls']==c['dlls'] and m['runId']!=c['runId'] and mv['buildReceiptSha256']==cv['buildReceiptSha256']
 bindings.append({'main':n,'control':'PC-'+n,'sameFixtureDllHashes':True,'buildReceiptSha256':mv['buildReceiptSha256'],'mainRequestSha256':sha(R/'players'/n/'request.json'),'controlRequestSha256':sha(R/'players'/('PC-'+n)/'request.json'),'differentProcessAndNonce':True,'physicalPointersNotComparedAcrossProcesses':True})
controls=load(R/'producer-controls.json');report={'kind':'ReadOnlyQFocusedProducerRuntimeAudit','startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceCommit':load(R/'LOCAL_BATCH_RESULT.json')['repositories']['hybridclr_demo'],'verifierSha256':sha(D/'Tools/AssemblyShadow/R03/runtime_contract.py'),'rows':rows,'pairBindings':bindings,'originalAggregate':controls,'producerAttributionCoverage':'Observed' if controls['identifiedLoopAdmissions']>0 else 'NoCoverage','limits':'Existing sealed raw only; diagnostic control success never promotes contaminated unisolatedWarmCertificate; no historical F actor attribution, retries, source edits, counter subtraction or acceptance promotion','R03Accepted':False,'H2Passed':False}
(P/'PRODUCER_RUNTIME_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
for row in rows:
 print(row['case'],row['originalCellOrDiagnosticResult'],{k:v['status'] for k,v in row['checks'].items()})
print('Natural aggregate',controls['result'],'identified admissions',controls['identifiedLoopAdmissions'],'coverage',report['producerAttributionCoverage'])
