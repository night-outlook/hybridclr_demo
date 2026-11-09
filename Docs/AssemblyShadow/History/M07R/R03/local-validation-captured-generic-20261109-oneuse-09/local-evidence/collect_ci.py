from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

preflight = Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-CapturedGeneric09')
snapshot = preflight.parent / 'captured-generic-09-prerequisite-CI.json'
expected = 'bb5fce9c15450e68c6341d88270fbc30dd7b9738'
api = 'https://api.github.com/repos/night-outlook/hybridclr_demo'
workflow_names = {
    'captured-generic-owner-host', 'captured-generic-native-host',
    'captured-generic-batch-host', 'captured-generic-real-headers',
    'initializer-bridge-host', 'initializer-local-contracts',
    'current-native-local-cycle-host', 'current-native-source-only',
}
artifacts = preflight / 'github'
artifacts.mkdir()
assert not snapshot.exists() and not snapshot.is_symlink()
def fetch(suffix, name):
    url = api + '/' + suffix
    raw = subprocess.check_output(['curl','-fSs','--max-time','25','-H','Cache-Control: no-cache',url])
    row = json.loads(raw)
    (artifacts / name).write_bytes(raw)
    return row

data = fetch(f'actions/runs?head_sha={expected}&per_page=100','workflow-runs.json')
all_runs = data['workflow_runs']
chosen = [run for run in all_runs if run['path'] in {f'.github/workflows/r03-ir-{n}.yml' for n in workflow_names}]
assert len(chosen)==len(workflow_names) and all(run['head_sha']==expected for run in chosen)
def get_job_lists(run):
    rid = run['id']
    latest = fetch(f'actions/runs/{rid}/jobs?filter=latest&per_page=100',f'run-{rid}-jobs.json')
    attempt = fetch(f'actions/runs/{rid}/attempts/{run["run_attempt"]}/jobs?per_page=100',f'run-{rid}-attempt-jobs.json')
    return rid, latest, attempt

with ThreadPoolExecutor(max_workers=6) as pool:
    tuples = list(pool.map(get_job_lists,chosen))
latest_jobs = {str(rid): latest for rid,latest,_ in tuples}
with snapshot.open('x') as stream:
    json.dump({'runs':chosen,'jobs':latest_jobs,
               'ancillary':[x for x in all_runs if x not in chosen]},stream,indent=2)
    stream.write('\n')
def status(row):
    return (row.get('head_sha'),row.get('status'),row.get('conclusion'))
def join(args):
    rid, j, a = args
    jid = j['id']
    direct = fetch(f'actions/jobs/{jid}',f'job-{jid}.json')
    check = fetch(f'check-runs/{jid}',f'check-{jid}.json')
    return {'runId':rid,'jobId':jid,'jobName':j['name'],
            'latest':status(j),'attempt':status(a),'direct':status(direct),'check':status(check),
            'identityVerified':direct['id']==a['id']==check['id']==jid and direct['run_id']==a['run_id']==j['run_id']==rid}

tasks=[]
for rid, latest, attempt in tuples:
    assert len(latest['jobs'])==len(attempt['jobs'])==2
    assert {j['id'] for j in latest['jobs']}=={j['id'] for j in attempt['jobs']}
    for j in latest['jobs']:
        [a] = [x for x in attempt['jobs'] if x['id']==j['id']]
        tasks.append((rid,j,a))
with ThreadPoolExecutor(max_workers=6) as pool:
    joins=list(pool.map(join,tasks))
result = all(j['identityVerified'] and all(j[k]==(expected,'completed','success') for k in ['latest','attempt','direct','check']) for j in joins)
receipt = {'checkedAtUtc':datetime.now(timezone.utc).isoformat(),
           'sourceCommit':expected,'sourcePath':str(snapshot),
           'sourceSha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),
           'allExactJobAndCheckRunRecordsAgree':result,'joins':joins}
(preflight/'CI_DIRECT_JOINS.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('CI direct, attempt, and check run joins',result,len(joins))
if not result:
    for j in joins:
        if not j['identityVerified'] or any(j[k]!=(expected,'completed','success') for k in ['latest','attempt','direct','check']):
            print(j)
