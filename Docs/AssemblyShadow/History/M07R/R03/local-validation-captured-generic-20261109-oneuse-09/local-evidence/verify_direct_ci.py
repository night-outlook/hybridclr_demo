from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
import hashlib
import json
import re
import subprocess

base = Path('/Users/ah/GitHub/hybridclr/r03-local-validation')
preflight = base / 'Preflight-CapturedGeneric09'
snapshot = base / 'captured-generic-09-prerequisite-CI.json'
expected = 'bb5fce9c15450e68c6341d88270fbc30dd7b9738'
artifacts = preflight / 'github'
def load(path):
    return json.loads(path.read_text())
source = load(snapshot)
checks = load(artifacts/'commit-check-runs.json')['check_runs']

def verify(item):
    run, job, attempt = item
    rid, jid = run['id'], job['id']
    [check] = [c for c in checks if c['id']==jid]
    assert job['run_id']==attempt['run_id']==rid and attempt['id']==jid
    for row in (job,attempt,check):
        assert (row['head_sha'],row['status'],row['conclusion'])==(expected,'completed','success'), row
    assert check['name']==attempt['name']==job['name']
    direct = artifacts/f'job-{jid}.json'
    evidence = {'mode':'DirectJobREST','url':job['url']}
    if direct.is_file():
        row = load(direct)
        assert row['id']==jid and row['run_id']==rid and row['name']==job['name']
        assert (row['head_sha'],row['status'],row['conclusion'])==(expected,'completed','success'), row
        evidence.update(sha256=hashlib.sha256(direct.read_bytes()).hexdigest(), file=str(direct))
    else:
        url = f'https://github.com/night-outlook/hybridclr_demo/actions/runs/{rid}/job/{jid}'
        assert check['details_url']==url and job['html_url']==url
        page = artifacts/f'job-{jid}-page.html'
        if not page.is_file():
            page.write_bytes(subprocess.check_output(['curl','-fSs','--max-time','25',url]))
        raw = page.read_bytes()
        html = raw.decode('utf-8')
        [status] = re.findall(r'<check-steps\b[^>]*\bdata-job-status="([^"]+)"',html)
        [header] = re.findall(r'data-url="/night-outlook/hybridclr_demo/runs/'+str(jid)+r'/header">\s*([a-z]+)\s*<relative-time',html)
        [name] = re.findall(r'id="check-step-header-title">\s*<span[^>]*>([^<]+)</span>',html)
        log_paths = re.findall(r'data-log-url="(/night-outlook/hybridclr_demo/commit/[^"]+)"',html)
        assert status=='completed' and header=='succeeded' and unescape(name)==job['name']
        assert log_paths and all(x.startswith(f'/night-outlook/hybridclr_demo/commit/{expected}/checks/{jid}/logs/') for x in log_paths)
        assert f'"selectedJobId":{jid},' in html and f'/actions/runs/{rid}/job/{jid}' in html
        evidence={'mode':'DirectActionsJobPage','url':url,'file':str(page),
                  'sha256':hashlib.sha256(raw).hexdigest(),'dataJobStatus':status,
                  'jobHeaderConclusion':header,'jobHeaderName':unescape(name),
                  'shaBoundStepLogUrls':log_paths}
    existing_check = artifacts/f'check-{jid}.json'
    if existing_check.is_file():
        c=load(existing_check)
        assert (c['head_sha'],c['status'],c['conclusion'])==(expected,'completed','success')
    return {'jobId':jid,'runId':rid,'name':job['name'],'headSha':expected,
            'status':'completed','conclusion':'success','directJobEvidence':evidence}

tasks=[]
for run in source['runs']:
    rid=run['id']
    jobs=source['jobs'][str(rid)]['jobs']
    attempt=load(artifacts/f'run-{rid}-attempt-jobs.json')['jobs']
    assert len(jobs)==len(attempt)==2 and {j['id'] for j in jobs}=={j['id'] for j in attempt}
    for j in jobs:
        [a]=[x for x in attempt if x['id']==j['id']]
        tasks.append((run,j,a))
with ThreadPoolExecutor(max_workers=4) as pool:
    joins=list(pool.map(verify,tasks))
receipt={'checkedAtUtc':datetime.now(timezone.utc).isoformat(),
         'sourceCommit':expected,'sourcePath':str(snapshot),
         'sourceSha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),
         'allExactJobAndCheckRunRecordsAgree':True,'joins':joins}
with (preflight/'CI_DIRECT_JOINS.json').open('x') as f:
    json.dump(receipt,f,indent=2);f.write('\n')
print('Verified job/attempt/check-run joins',len(joins),'including',
      sum(j['directJobEvidence']['mode']=='DirectActionsJobPage' for j in joins),'direct Actions job pages')
