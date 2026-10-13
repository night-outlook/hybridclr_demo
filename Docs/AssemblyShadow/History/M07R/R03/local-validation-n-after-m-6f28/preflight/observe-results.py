from h_common import *
R=B/'R03IRLocal-N-after-M-6f28';start=now();rows=[]
for role in ['candidate-release','candidate-debug','candidate-off']:
 root=R/'builds'/role;f=root/'bee-result-observation.json';row={'role':role,'observation':'Unavailable','analysis':'Unavailable'}
 if f.exists():
  j=load(f);row.update(path=str(f),sha256=sha(f),bytes=f.stat().st_size,rawResult=j.get('result'),sameProcessor=j.get('sameProcessor'),driverInitiallyAbsent=j.get('driverInitiallyAbsent'),limitsExceeded=j.get('limitsExceeded'),buildErrors=j.get('buildErrors'),nodeCount=len(j.get('nodes') or []),messages=j.get('messages'),sourceManifestSha256=j.get('sourceManifestSha256'),error=j.get('error'));row['observation']='Recorded raw; '+str(j.get('result'))
  cfg=load(root/'config.json');assert j['sourceManifestSha256']==cfg['sourceManifestSha256']
  if (root/'build-receipt.json').exists():
   br=load(root/'build-receipt.json');assert br.get('beeObservationSha256')==sha(f) and br.get('beeObservationStatus')==j.get('result');row['buildReportedResult']=br['result'];row['buildReceiptErrors']=br['errors'];row['buildReceiptWarnings']=br['warnings']
 if (root/'bee-result-analysis.json').exists():row['analysis']=load(root/'bee-result-analysis.json')
 if f.exists():
  row['factoryEvidence']={k:v for k,v in j.items() if any(t in k.lower() for t in ['factory','driver','processor','assembly','digest','identity','sequence','call','restor'])}
 rows.append(row)
save(P/'BEE_OBSERVATION_AUDIT.json',{'state':'FactualEvidenceRecorded','startUtc':start,'endUtc':now(),'roles':rows,'exactEmitter':'Unavailable unless actual source-bound messages establish it; no inference from task paths','buildAcceptanceChanged':False,'historicalIResult':'FAIL unchanged','runtimeAcceptance':False})
print(json.dumps([{'role':r['role'],'rawResult':r.get('rawResult'),'sameProcessor':r.get('sameProcessor'),'nodes':r.get('nodeCount')} for r in rows]),flush=True)
