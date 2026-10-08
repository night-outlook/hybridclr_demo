from pathlib import Path
import json,subprocess,datetime,hashlib
P=Path(__file__).resolve().parent;W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';C=Path(json.loads((P/'CHECKPOINT_LOCATION.json').read_text())['path']);a=json.loads((P/'SOURCE_AUTHORITY.json').read_text());commit=json.loads((P/'LOCAL_COMMIT_RECEIPT.json').read_text())['commit'];branch=a['branch']
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(f):
 with Path(f).open('rb') as src:return hashlib.file_digest(src,'sha256').hexdigest()
start=utc();stdout=P/'push.stdout.log';stderr=P/'push.stderr.log'
with stdout.open('xb') as out,stderr.open('xb') as err:
 r=subprocess.run(['git','-C',str(D),'push','origin','HEAD:refs/heads/'+branch],stdout=out,stderr=err,timeout=900)
with (P/'PUSH_RECEIPT.json').open('x') as f:json.dump({'startUtc':start,'endUtc':utc(),'argv':['git','-C',str(D),'push','origin','HEAD:refs/heads/'+branch],'exitCode':r.returncode,'stdoutPath':str(stdout),'stdoutSha256':sha(stdout),'stderrPath':str(stderr),'stderrSha256':sha(stderr),'forcePush':False},f,indent=2);f.write('\n')
assert r.returncode==0,'Push failed; retain local commit and raw push receipts, no authoritative handoff'
rows=[]
for name,source in a['repositories'].items():
 path=W/name;pin=commit if name=='hybridclr_demo' else source;ops=[]
 for args in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--short'],['remote','-v'],['ls-remote','origin','refs/heads/'+branch]]:
  t=utc();r=subprocess.run(['git','-C',str(path),*args],capture_output=True,text=True,timeout=120);ops.append({'argv':['git','-C',str(path),*args],'startUtc':t,'endUtc':utc(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0
 assert ops[0]['stdout'].strip()==str(path) and ops[1]['stdout'].strip()==branch and ops[2]['stdout'].strip()==pin and not ops[3]['stdout'].strip() and ops[5]['stdout'].split()[0]==pin;assert 'git@github.com:night-outlook/'+name+'.git' in ops[4]['stdout'];rows.append({'repository':'night-outlook/'+name,'path':str(path),'branch':branch,'commit':pin,'remote':'verified','clean':True,'operations':ops})
changed=subprocess.check_output(['git','-C',str(D),'diff','--name-only',a['repositories']['hybridclr_demo'],commit],text=True).splitlines();root=str(C.relative_to(D));assert all(p in ['Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md','Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md'] or p.startswith(root+'/') for p in changed)
for line in (C/'MANIFEST.sha256').read_text().splitlines():h,n=line.split('  ',1);assert sha(C/n)==h
result=json.loads((P/'POSTRUN_AUTHENTICATION.json').read_text());record={'kind':'LocalValidationPublishedAuthority','recordedUtc':utc(),'state':'Passed','executedDemoCommit':a['repositories']['hybridclr_demo'],'publicationCommit':commit,'repositories':rows,'checkpoint':str(C),'checkpointManifestSha256':sha(C/'MANIFEST.sha256'),'coreResult':result['coreResult'],'counts':result['counts'],'sealStatus':result['sealStatus'],'coreHashes':result['topLevelHashes'],'storageSessionState':result['storageSessionState'],'outerExitCode':result['outerExitCode'],'historicalCustodyVerifiedFiles':result['custodyFiles'],'onlyOwnedDocumentationEvidenceChanged':True,'acceptanceFlagsRemainFalse':True,'nextState':'Primary Implementation'}
with (P/'PUBLICATION_RECEIPT.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print('Push and all four latest heads verified',commit,'checkpoint',C,flush=True)
