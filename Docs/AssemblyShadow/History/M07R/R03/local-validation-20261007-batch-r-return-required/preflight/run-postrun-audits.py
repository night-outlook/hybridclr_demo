"""Run only read-only evidence auditors after the single wrapper has finished."""
from pathlib import Path
import subprocess,json,os,datetime,hashlib
P=Path(__file__).resolve().parent;B=P.parent/'R03LocalBatch-20261007R-lq-storage';D=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');PY='/Library/Frameworks/Python.framework/Versions/3.14/bin/python3'
assert (P/'runner-exit.json').is_file() and (B/'seal-receipt.json').is_file();env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','GIT_SSH_COMMAND':json.loads((P/'SOURCE_AUTHORITY.json').read_text())['sshCommand']}
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
start=datetime.datetime.now(datetime.timezone.utc).isoformat();before={r['path']:r['sha256'] for r in json.loads((B/'evidence-index.json').read_text())['files']};before.update({n:sha(B/n) for n in ['LOCAL_BATCH_RESULT.json','BATCH_EXECUTION.json','evidence-index.json','evidence.tar.gz','seal-receipt.json']});result=json.loads((B/'LOCAL_BATCH_RESULT.json').read_text());cells={c['id']:c for c in result['cells']}
scripts=['authenticate-focused-batch.py','audit-li-contracts.py','audit-ln-repairs.py','audit-producer-runtime.py','audit-rejection-observation.py','audit-resource-builds-restoration.py','audit-capabilities.py','audit-fixed-image.py','audit-compiler-policy.py','audit-layout-identity.py','audit-completion.py','audit-lo-repairs.py','audit-lp-repairs.py'];rows=[]
for script in scripts:
 label=script.removesuffix('.py');folder=P/'audit-operations'/label;folder.mkdir(parents=True);beg=datetime.datetime.now(datetime.timezone.utc).isoformat()
 # Focused full authentication expects completed focused builds/fixtures; absent prerequisites are NotRun, not invented failures.
 prerequisites=['player-fixtures','prepare-candidate-release','build-candidate-release','build-reference-release','build-candidate-debug','build-candidate-off','producer-controls'] if script=='authenticate-focused-batch.py' else []
 blocked=[name for name in prerequisites if cells[name]['result']!='Passed']
 if blocked:
  row={'script':script,'result':'NotRun','reason':'Focused auditor full-input prerequisite is absent','prerequisites':{n:cells[n]['result'] for n in blocked},'startUtc':beg,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 else:
  with (folder/'stdout.log').open('xb') as out,(folder/'stderr.log').open('xb') as err:r=subprocess.run([PY,'-B',str(P/script)],cwd=D,env=env,stdout=out,stderr=err)
  row={'script':script,'result':'Passed' if r.returncode==0 else 'Failed','exitCode':r.returncode,'argv':[PY,'-B',str(P/script)],'cwd':str(D),'startUtc':beg,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stdoutSha256':sha(folder/'stdout.log'),'stderrSha256':sha(folder/'stderr.log')}
 (folder/'receipt.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row);print(script,row['result'],flush=True)
changed=[]
for rel,h in before.items():
 if not (B/rel).is_file() or sha(B/rel)!=h:changed.append(rel)
record={'kind':'ReadOnlyPostrunAuditDispatch','startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scripts':rows,'indexedAndTopLevelRawFilesUnchanged':not changed,'changedRawFiles':changed,'originalBatchResult':result['result'],'originalCellsReclassified':False,'productReexecution':False};(P/'POSTRUN_AUDIT_DISPATCH.json').write_text(json.dumps(record,indent=2)+'\n');assert not changed
