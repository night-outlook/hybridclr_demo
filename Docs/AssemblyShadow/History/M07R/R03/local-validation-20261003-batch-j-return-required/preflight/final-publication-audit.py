import concurrent.futures,datetime,hashlib,json,pathlib,subprocess
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261003J-contracts');R=P.parent/'R03LocalBatch-20261003J-contracts';C=D/('Docs/AssemblyShadow/History/M07R/R03/local-validation-20261003-batch-j-'+('evidence-ready' if json.loads((R/'LOCAL_BATCH_RESULT.json').read_text())['result']=='EvidenceReadyForPrimaryReview' else 'return-required'));branch='codex/assembly-shadow-r01b-h1'
def git(path,*args):return subprocess.check_output(['git','-C',str(path),*args],text=True).strip()
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def verify(name):
 p=W/name;head=git(p,'rev-parse','HEAD');remote=git(p,'ls-remote','origin','refs/heads/'+branch);status=git(p,'status','--short');origin=git(p,'remote','get-url','origin');actualbranch=git(p,'branch','--show-current');top=git(p,'rev-parse','--show-toplevel')
 assert head==remote.split()[0] and status=='' and actualbranch==branch and top==str(p) and origin=='git@github.com:night-outlook/'+name+'.git'
 return {'repository':'night-outlook/'+name,'path':str(p),'branch':actualbranch,'commit':head,'remote':origin,'remoteHead':remote.split()[0],'status':status,'remoteVerified':True,'worktrees':git(p,'worktree','list','--porcelain')}
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:rows=list(executor.map(verify,['hybridclr_demo','hybridclr','hybridclr_unity','il2cpp_plus']))
expected={'hybridclr':'4b2774b066cfc6afd77a8c8aded6bda7ea574f55','hybridclr_unity':'c86cbf665f5fcb2137e5adf2960541ce492467a4','il2cpp_plus':'1cf87f8209790f9fb2ebec97487dc1990ccd56c5'}
for row in rows[1:]:assert row['commit']==expected[row['repository'].split('/')[1]]
changed=git(D,'diff','--name-only','cebed900e6456433ac65db531262b60fd26766ee','HEAD').splitlines();assert len(changed)>100 and all(n in ['Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md','Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md'] or n.startswith(str(C.relative_to(D))+'/') for n in changed)
manifest=(C/'MANIFEST.sha256').read_text().splitlines()
for line in manifest:
 h,n=line.split('  ',1);p=C/n;assert sha(p)==h
 b=subprocess.check_output(['git','-C',str(D),'show','HEAD:'+str(p.relative_to(D))]);assert hashlib.sha256(b).hexdigest()==h
for f in json.loads((R/'evidence-index.json').read_text())['files']:assert sha(R/f['path'])==f['sha256'] and sha(C/'batch'/f['path'])==f['sha256']
for n,h in json.loads((P/'POSTRUN_AUTHENTICATION.json').read_text())['topLevelHashes'].items():
 assert sha(R/n)==h
 if n!='evidence.tar.gz':assert sha(C/'batch'/n)==h
transport=json.loads((C/'ARCHIVE_TRANSPORT.json').read_text());combined=hashlib.sha256();size=0
for part in transport['parts']:
 p=C/part['path'];assert sha(p)==part['sha256'] and p.stat().st_size==part['size'];size+=part['size']
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):combined.update(b)
assert combined.hexdigest()==transport['originalSha256']==sha(R/'evidence.tar.gz') and size==transport['originalSize']
for p,h in json.loads((P/'prior-evidence-custody.json').read_text()).items():assert sha(p)==h
result={'kind':'LocalPublicationReceipt','startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'Passed','repositories':rows,'changedFiles':len(changed),'checkpointManifestFilesAuthenticated':len(manifest),'originalBatchFilesAndPreviousCustodyUnchanged':True,'executedDemoCommit':'cebed900e6456433ac65db531262b60fd26766ee','publishedDemoCommit':rows[0]['commit'],'batchInvocations':1,'exitState':'Local Validation -> Primary Implementation','R03Accepted':False,'H2Passed':False}
(P/'PUBLICATION_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='repositories'},indent=2))
for row in rows:print(row['repository'],row['commit'],'remote=verified clean')
