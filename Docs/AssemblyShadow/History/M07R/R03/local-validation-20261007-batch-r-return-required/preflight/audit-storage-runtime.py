"""Authenticate separate storage receipts without changing batch verdicts."""
from pathlib import Path
import json,hashlib,datetime,collections
P=Path(__file__).resolve().parent;BASE=P.parent;B=BASE/'R03LocalBatch-20261007R-lq-storage';S=BASE/'Storage-R03LocalBatch-20261007R-lq-storage'
def load(p):return json.loads(Path(p).read_text())
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
start=utc();session=load(S/'session.json');dispatch=load(S/'dispatch.json');run=load(P/'runner-exit.json');rows=[json.loads(x) for x in (S/'capacity.jsonl').read_text().splitlines()];assert [r['sequence'] for r in rows]==list(range(len(rows)));assert len(rows)==session['samples']==720;assert all(a['monotonicNs']<b['monotonicNs'] for a,b in zip(rows,rows[1:]));assert sha(S/'capacity.jsonl')==session['telemetrySha256'];assert sha(S/'session.json')==dispatch['storageSessionSha256'];assert sha(B/'LOCAL_BATCH_RESULT.json')==dispatch['coreResultSha256'];assert dispatch['batchExitCode']==session['batchExitCode']==run['exitCode']==1 and dispatch['batchStarted'] and session['batchStarted'];assert session['state']=='Passed' and session['latchedProblem'] is None
mins={}
for row in rows:
 for v in row['volumes']:
  assert v['device']==v['fsid']==16777230 and not v['readOnly'];mins[v['role']]=min(mins.get(v['role'],2**63),v['availableBytes']);assert v['availableBytes']>=20*1024**3
assert mins==session['minimumSampledAvailableBytes'];admissions=[]
for root in [BASE/'StorageCheck-R03LocalBatch-20261007R-lq-storage-2',S]:
 a=load(root/'admission.json');assert a['state']=='Admitted' and a['requiredAvailableBytesEachLocation']==max(64*1024**3,2*a['retainedQSize']['planningBytes']+20*1024**3);assert len(a['probes'])==10 and all(r['result']=='Passed' and not r['cleanupErrors'] and r['allocatedBytes']>=r['bytes']==1048576 for r in a['probes']);admissions.append({'path':str(root/'admission.json'),'sha256':sha(root/'admission.json'),'state':a['state'],'probesPassed':10,'requiredBytes':a['requiredAvailableBytesEachLocation'],'historicalCapacityPromotion':False})
for event in ['admission-before-probes','admission-after-probes','immediately-before-constructor']:
 r=next(r for r in rows if r['event']==event);assert min(v['availableBytes'] for v in r['volumes'])>=68719476736
intent=load(S/'launch-intent.json');assert intent['pid']==run['pid'] and intent['demoCommit']=='ba57a3391da9627e694ee33f8bfe3cb993e6c56a' and intent['expectedCells']==90 and intent['expectedPlayers']==59 and intent['expectedFreshBuilds']==6
assert not(S/'integration-allocation-probe.json').exists();assert load(B/'cells/production-entry-integration.json')['result']=='Blocked'
failures=[]
for p in sorted(S.glob('failure-*.json')):
 x=load(p);failures.append({'path':str(p),'sha256':sha(p),'phase':x['phase'],'error':x['error']['message'],'errno':x['error']['errno'],'interpretation':'Remote-authority failure' if x['phase']=='resource-p05-restore' else 'Expected-negative fixture/compiler control captured by wrapper; cell player-fixtures remains Passed'})
assert len(failures)==4 and all(r['errno'] is None for r in failures)
record={'kind':'ReadOnlyRStorageRuntimeAudit','startUtc':start,'endUtc':utc(),'authentication':'Passed','originalStorageSession':'Passed','originalCoreResult':'ReturnRequired','admissions':admissions,'samples':len(rows),'events':dict(collections.Counter(r['event'] for r in rows)),'minimumAvailableBytes':mins,'minimumGiB':min(mins.values())/1024**3,'operatingFloorGiB':20,'capacityReserved':False,'sampledMinimumIsNotActualHighWater':True,'samePoolNotSummed':True,'integrationAllocationProbe':'NotRun: dependent production integration Blocked','failures':failures,'sessionSha256':sha(S/'session.json'),'dispatchSha256':sha(S/'dispatch.json'),'telemetrySha256':sha(S/'capacity.jsonl'),'noRerunOrRawMutation':True}
with (P/'STORAGE_RUNTIME_AUDIT.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print('Storage audit Passed; core ReturnRequired unchanged; integration probe NotRun')
