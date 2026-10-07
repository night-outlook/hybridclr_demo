"""Publish only checked Local docs/checkpoint; no force push, source changes or cleanup."""
from pathlib import Path
import subprocess,json,os,datetime,hashlib,collections
P=Path(__file__).resolve().parent;W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';B=P.parent/'R03LocalBatch-20261007R-lq-storage';S=P.parent/'Storage-R03LocalBatch-20261007R-lq-storage';C=Path(json.loads((P/'CHECKPOINT_LOCATION.json').read_text())['path']);source=json.loads((P/'SOURCE_AUTHORITY.json').read_text());branch=source['branch'];env={**os.environ,'GIT_SSH_COMMAND':source['sshCommand'],'GIT_TERMINAL_PROMPT':'0'}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
seq=0
def git(repo,*args,timeout=90):
 global seq
 seq+=1;folder=P/'git-publication'/str(seq).zfill(3);folder.mkdir(parents=True);start=utc();argv=['git','-C',str(repo),*args]
 try:r=subprocess.run(argv,env=env,capture_output=True,timeout=timeout)
 except subprocess.TimeoutExpired as e:
  (folder/'stdout.log').write_bytes(e.stdout or b'');(folder/'stderr.log').write_bytes(e.stderr or b'');(folder/'receipt.json').write_text(json.dumps({'argv':argv,'startUtc':start,'endUtc':utc(),'state':'Unavailable','timeout':True},indent=2)+'\n');raise
 (folder/'stdout.log').write_bytes(r.stdout);(folder/'stderr.log').write_bytes(r.stderr);(folder/'receipt.json').write_text(json.dumps({'argv':argv,'startUtc':start,'endUtc':utc(),'exitCode':r.returncode,'stdoutSha256':sha(folder/'stdout.log'),'stderrSha256':sha(folder/'stderr.log')},indent=2)+'\n');assert r.returncode==0,(argv,r.returncode,r.stderr.decode(errors='replace')[:2000]);return r.stdout.decode().strip()
assert json.loads((P/'STAGING_RECEIPT.json').read_text())['state']=='Passed';start=utc();rel=str(C.relative_to(D));owned=['Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md','Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md'];staged=git(D,'diff','--cached','--name-only').splitlines();assert staged and all(n in owned or n.startswith(rel+'/') for n in staged);assert not git(D,'diff','--name-only');assert not git(D,'ls-files','--others','--exclude-standard');git(D,'diff','--check');git(D,'diff','--cached','--check')
for name,pin in source['repositories'].items():
 repo=W/name;assert git(repo,'rev-parse','--show-toplevel')==str(repo);assert git(repo,'branch','--show-current')==branch and git(repo,'rev-parse','HEAD')==pin;assert git(repo,'remote','get-url','origin')=='git@github.com:night-outlook/'+name+'.git';assert git(repo,'ls-remote','origin','refs/heads/'+branch).split()[0]==pin
 if name!='hybridclr_demo':assert not git(repo,'status','--short')
git(D,'commit','-m','Record R03 batch R partial validation and P05 authority failure',timeout=300);commit=git(D,'rev-parse','HEAD');assert len(commit)==40;changes=git(D,'diff-tree','--no-commit-id','--name-only','-r','HEAD').splitlines();assert set(changes)==set(staged);assert not git(D,'status','--short');git(D,'push','origin','HEAD:refs/heads/'+branch,timeout=300)
repos=[]
for name,pin in source['repositories'].items():
 repo=W/name;expected=commit if name=='hybridclr_demo' else pin;head=git(repo,'rev-parse','HEAD');remote=git(repo,'ls-remote','origin','refs/heads/'+branch);status=git(repo,'status','--short');assert head==expected==remote.split()[0] and not status and git(repo,'branch','--show-current')==branch
 repos.append({'repository':'night-outlook/'+name,'path':str(repo),'branch':branch,'commit':head,'sourceCommit':pin,'remoteHead':remote,'remote':'verified','status':status,'toplevel':git(repo,'rev-parse','--show-toplevel'),'remotes':git(repo,'remote','-v'),'worktrees':git(repo,'worktree','list','--porcelain')})
result=json.loads((B/'LOCAL_BATCH_RESULT.json').read_text());receipt={'kind':'R03LocalImmutableCheckpointPublication','startUtc':start,'endUtc':utc(),'state':'Passed','executedSource':source['repositories'],'repositoriesLatestPushed':repos,'demoPublicationCommit':commit,'checkpointPath':str(C),'checkpointManifestSha256':sha(C/'MANIFEST.sha256'),'stagedFiles':len(staged),'result':result['result'],'counts':dict(collections.Counter(c['result'] for c in result['cells'])),'sealStatus':result['sealStatus'],'storageSession':json.loads((S/'session.json').read_text())['state'],'topLevelOriginalHashes':{n:sha(B/n) for n in ['LOCAL_BATCH_RESULT.json','BATCH_EXECUTION.json','evidence-index.json','evidence.tar.gz','seal-receipt.json']},'storageHashes':{n:sha(S/n) for n in ['session.json','dispatch.json','capacity.jsonl','admission.json','launch-intent.json','source-authority.json']},'modificationScope':owned+[rel],'sourceAndExpectationsUnchanged':True,'historicalResultsUnchanged':True,'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'pureInterpreterExpansionEnabled':False,'nextState':'Primary Implementation'}
with (P/'PUBLICATION_RECEIPT.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print('Published',commit,'all four remote heads verified clean',flush=True)
