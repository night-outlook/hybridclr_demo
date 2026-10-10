from pathlib import Path
import json,datetime
P=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261010E-native-receipt');B=P.parent/'R03IRLocal-20261010E-native-receipt';S=P.parent/'Storage-R03IRLocal-20261010E-native-receipt'
cells=[]
for f in sorted((B/'cells').glob('*.json')):
 v=json.loads(f.read_text());cells.append({k:v[k] for k in ['id','result','error','reason'] if k in v})
commands=sorted((B/'commands').glob('*'));last=commands[-1] if commands else None
row={'observedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':'ReadOnlyInProgressObservation','cells':cells,'commandDirectories':len(commands),'lastCommand':str(last) if last else None,'resultFileExists':(B/'LOCAL_BATCH_RESULT.json').exists(),'executionSidecarExists':S.exists()}
if last:
 for name in ['receipt.json','unity-completion.json']:
  if (last/name).is_file():row[name]=json.loads((last/name).read_text())
 for name in ['stdout.log','stderr.log']:
  f=last/name
  if f.is_file():
   with f.open('rb') as s:s.seek(max(0,f.stat().st_size-1600));row[name+'Tail']=s.read().decode(errors='replace')
with (P/'RUN_OBSERVATIONS.jsonl').open('a') as out:out.write(json.dumps(row)+'\n')
print(json.dumps(row))
