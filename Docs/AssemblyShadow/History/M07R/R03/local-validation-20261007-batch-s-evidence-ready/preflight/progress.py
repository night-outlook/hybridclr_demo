"""Read-only point-in-time progress; never acceptance or phase dispatch."""
from pathlib import Path
import json,datetime,collections,os
P=Path(__file__).resolve().parent;B=P.parent/'R03LocalBatch-20261007S-lr-recovery';S=P.parent/'Storage-R03LocalBatch-20261007S-lr-recovery-2'
rows=[]
if (B/'cells').is_dir():
 for f in (B/'cells').glob('*.json'):
  try:rows.append(json.loads(f.read_text()))
  except (json.JSONDecodeError,FileNotFoundError):pass
commands=sorted((B/'commands').glob('*')) if (B/'commands').is_dir() else [];last={'directory':str(commands[-1])} if commands else None
if last:
 f=commands[-1]/'command.json'
 if f.is_file():
  try:
   c=json.loads(f.read_text());last.update(exitCode=c.get('exitCode'),executable=c.get('command',[''])[0])
  except (json.JSONDecodeError,FileNotFoundError):pass
rows.sort(key=lambda r:(B/'cells'/(r['id']+'.json')).stat().st_mtime_ns);capacity=None
if (S/'capacity.jsonl').exists():
 lines=(S/'capacity.jsonl').read_text().splitlines()
 if lines:
  try:capacity=json.loads(lines[-1])
  except json.JSONDecodeError:pass
record={'recordedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'coreRootExists':B.exists(),'cellsRecorded':len(rows),'counts':dict(collections.Counter(r['result'] for r in rows)),'failed':[{'id':r['id'],'error':r.get('error')} for r in rows if r['result']=='Failed'],'lastCell':rows[-1]['id'] if rows else None,'commandFolders':len(commands),'lastCommand':last,'availableBytes':os.statvfs(P).f_bavail*os.statvfs(P).f_frsize,'resultFileExists':(B/'LOCAL_BATCH_RESULT.json').exists(),'capacityPhase':capacity.get('phase') if capacity else None,'observationOnly':True}
with (P/'PROGRESS_OBSERVATIONS.jsonl').open('a') as out:out.write(json.dumps(record)+'\n')
print(json.dumps(record))
