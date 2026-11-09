from pathlib import Path
import datetime
import hashlib
import json
import subprocess

base = Path('/Users/ah/GitHub/hybridclr/r03-local-validation')
preflight = base / 'Preflight-CapturedGeneric08'
demo = base.parent / 'assembly_shadow_h1r/hybridclr_demo'
handoff = demo / 'Docs/AssemblyShadow/Handoff'
root = base / 'R03IR-CapturedGeneric-20261109-oneuse-08'
host = root.with_name(root.name+'-native-host-raw')
checkpoint = demo / 'Docs/AssemblyShadow/History/M07R/R03/local-validation-captured-generic-20261109-oneuse-08-prerequisite-blocked'
publication = base / 'captured-generic-08-prerequisite-blocked-PUBLICATION_RECEIPT.json'
source = '26843412eda7034cd91c0754bdcde16d5517d814'

def load(path):
    return json.loads(path.read_text())

def save(path, data):
    with path.open('x') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')

def sha(data):
    return hashlib.sha256(data).hexdigest()

for path in (root,host,checkpoint,publication):
    assert not path.exists() and not path.is_symlink(), path
assert not (preflight/'runner-INVOCATION.json').exists()
assert subprocess.check_output(['git','-C',str(demo),'status','--porcelain']) == b''
ci = load(preflight/'CI.json')
direct = load(preflight/'CI_DECISION_RECHECK.json')
assert direct['exactDemo']==source
assert direct['nonpassingJobRecords']==[[42551093381,128946622207,'in_progress','success']]
assert direct['directRecheck']['status']=='in_progress'
job_rows = []
for run in ci['runs']:
    assert (run['head_sha'],run['status'],run['conclusion'])==(source,'completed','success')
    jobs = load(preflight/f'RUN_{run["id"]}_JOBS.json')['jobs']
    assert len(jobs)==2 and all(j['head_sha']==source and j['run_id']==run['id'] for j in jobs)
    for os in ('macos-15','ubuntu-24.04'):
        [job] = [j for j in jobs if os in j['name']]
        job_rows.append({'run':run['id'],'workflow':run['path'],'job':job['id'],'os':os,
                         'status':job['status'],'conclusion':job['conclusion'],'sha':job['head_sha'],
                         'mandatory':run['id']!=42551093404})
assert sum(j['mandatory'] for j in job_rows)==14
assert sum(j['mandatory'] and (j['status'],j['conclusion'])==('completed','success') for j in job_rows)==13
caps = [load(preflight/f'CAPACITY_{i}.json') for i in (1,2)]
delta = (datetime.datetime.fromisoformat(caps[1]['timeUtc'])-datetime.datetime.fromisoformat(caps[0]['timeUtc'])).total_seconds()
assert delta>=60 and caps[0]['device']==caps[1]['device']==base.stat().st_dev
assert all(c['capacity']['freeBytes']>=26843545600 and c['bothFreshRootsAbsent'] for c in caps)
admission = load(preflight/'ADMISSION.json')
preserve = load(preflight/'PRESERVATION_BEFORE.json')
custody = load(preflight/'SCOPED_C_BEFORE.json')
assert admission['result']=='PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun'
assert preserve['result']=='PassedRemainingProtectedInputs_Exact17RetiredRemainUnavailable'
assert custody['result']=='ScopedHistoricalLossStable' and custody['completeScan']
assert (custody['presentVerified'],custody['historicalStillMissing'],custody['originalStrictCustody'])==(339367,77477,'Blocked')
pins = preserve['sourcePins']
assert pins['hybridclr_demo']==source
checkpoint.mkdir()
(checkpoint/'preflight').mkdir()
bindings = []
for path in sorted(preflight.iterdir()):
    if not path.is_file() or path.suffix not in {'.json','.log','.py'}:
        continue
    data = path.read_bytes()
    text = data.decode('utf-8')
    encoding = 'ExactBytes'
    target = checkpoint/'preflight'/path.name
    if '\r' in text or text.endswith('\n\n') or any(x.endswith((' ','\t')) for x in text.splitlines()):
        target = target.with_name(target.name+'.utf8.json')
        save(target,{'kind':'ExactUtf8TextEvidenceEncoding','source':str(path),'sha256':sha(data),'text':text})
        encoding = 'Utf8TextField'
    else:
        target.write_bytes(data)
    bindings.append({'source':str(path),'path':str(target.relative_to(checkpoint)),
                     'sha256':sha(data),'bytes':len(data),'encoding':encoding})
save(checkpoint/'COPY_BINDINGS.json',{'copies':bindings})
save(checkpoint/'LOCAL_RESULT.json',{
    'result':'PrerequisiteBlocked','runtime':'NotRun','executionCandidate':pins,
    'runnerInvocations':0,'unityBuilds':0,'players':0,'plannedCells':19,'executedCells':0,
    'plannedCellsStatus':'NotRun','productLedgerCreated':False,
    'batchRoot':str(root),'hostRawRoot':str(host),'bothRootsAbsent':True,
    'ciJobs':job_rows,'ciBlocker':'IR-LOCAL-R03-CAPTURED-GENERIC-08-CI-STATUS-01',
    'ciRecheck':direct,'capacitySamples':caps,'capacitySecondsApart':delta,
    'macAdmission':admission['result'],'historicalStrictCustody':'Blocked',
    'frozenCPresent':custody['presentVerified'],'frozenCHistoricalMissing':custody['historicalStillMissing'],
    'preservedPublishedCheckpoints':len(preserve['history']),'retiredRootsUnavailable':17,'retiredDuplicatePathsUnavailable':40,
    'runtimeAcceptance':False,'R03Accepted':False,'H2Passed':False,'ReadyForHumanReviewGate':False,
    'qualificationApproved':False,'fullLegacyRegressionAcceptance':False,
    'publicationReceipt':str(publication),'nextState':'Primary Implementation',
})
summary = f'''**PrerequisiteBlocked / NotRun.** The oneuse-08 candidate was `{source}`. The runner, Unity build and Player counts are all zero. All 19 planned cells are NotRun. Both reserved runtime roots are absent.

**IR-LOCAL-R03-CAPTURED-GENERIC-08-CI-STATUS-01.** Thirteen of fourteen mandatory OS jobs at the exact source SHA report completed/success. Ubuntu source-audit job [128946622207](https://github.com/night-outlook/hybridclr_demo/actions/runs/42551093381/job/128946622207) in run 42551093381, attempt 1, reports `status=in_progress`, `conclusion=success` and `completed_at=2026-11-09T02:28:13Z`. The run is completed/success, each step is completed/success, and the job log records seven tests passing. The direct job, attempt job list and check-run records agree on the inconsistent job status. The fresh direct job recheck at {direct["checkedAtUtc"]} returned the same status. WEB_TO_LOCAL requires completed/success at the job level. The CI gate is blocked. The source audit covers the public fork declarations and implementations.

The current-native source-only jobs both passed. The exact-source workflow and job receipts also preserve the ancillary failed and cancelled outcomes. The read-only Mac/Unity/SDK admission, four pinned Git sources, clean registered Original S and remaining custody checks passed. Fresh capacity samples were **{caps[0]["capacity"]["freeGiB"]:.6f} GiB** and **{caps[1]["capacity"]["freeGiB"]:.6f} GiB**, {delta:.3f} seconds apart on device {caps[0]["device"]}. The frozen-C rescan verified 339,367 surviving bindings and 77,477 recorded historical absences. Strict historical custody is Blocked. The 17 owner-retired roots and 40 duplicate paths are Unavailable.

Primary should reconcile the exact-commit Ubuntu job record so the mandatory completed/success predicate can be verified, then provide a fresh handoff. The reserved oneuse-08 runtime root and separate host root remain unconsumed. This prerequisite checkpoint is separate from a runtime evidence checkpoint. All acceptance flags are false.'''
(checkpoint/'README.md').write_text('# Captured-generic oneuse-08 — PrerequisiteBlocked\n\n'+summary+'\n\n[Result and evidence inventory](LOCAL_RESULT.json)\n')
relative = '../History/M07R/R03/'+checkpoint.name
owned = []
for name in ('LOCAL_VALIDATION.md','RETURN_TO_WEB.md'):
    path = handoff/name
    prior = path.read_text()
    title, sep, body = prior.partition('\n\n')
    assert sep
    rel = str(path.relative_to(demo))
    assert prior==subprocess.check_output(['git','-C',str(demo),'show',source+':'+rel],text=True)
    path.write_text(title+'\n\n## Captured-generic oneuse-08 — PrerequisiteBlocked\n\n'+summary+
                    f'\n\n[Authenticated prerequisite evidence]({relative}/README.md).\n\n---\n\n'+body)
    owned.append(rel)
files = sorted(x for x in checkpoint.rglob('*') if x.is_file())
manifest = checkpoint/'MANIFEST.sha256'
manifest.write_text(''.join(f'{sha(f.read_bytes())}  {f.relative_to(checkpoint)}\n' for f in files))
save(preflight/'PUBLICATION_PLAN.json',{'result':'PrerequisiteBlocked','executionPins':pins,
     'checkpoint':str(checkpoint),'checkpointManifestSha256':sha(manifest.read_bytes()),
     'ownedReports':owned,'checkpointFiles':len(files)+1})
print('Prepared BLOCKED checkpoint',len(files)+1,'files')
