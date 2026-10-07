from pathlib import Path
import hashlib,json,subprocess,re,datetime,os
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';BASE=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');P=BASE/'Preflight-R03LocalBatch-20261007R-lq-storage';CHECK=BASE/'StorageCheck-R03LocalBatch-20261007R-lq-storage';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-r-capacity-blocked';SOURCE='cbf80474ebdee125e1d162d9c32a1734ee541720';rel=str(C.relative_to(D));docs=['Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md','Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md'];owned=[*docs,rel]
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def git(*args):return subprocess.run(['git','-C',str(D),*args],capture_output=True,check=True).stdout
start=utc();assert git('rev-parse','HEAD').decode().strip()==SOURCE;assert all(n in docs or n.startswith(rel+'/') for n in git('diff','--cached','--name-only').decode().splitlines());assert all(n in docs or n.startswith(rel+'/') for n in git('diff','--name-only').decode().splitlines())
status=git('status','--short','--untracked-files=all').decode();assert all(line[3:] in docs or line[3:].startswith(rel+'/') for line in status.splitlines())
manifest=C/'MANIFEST.sha256';rows=manifest.read_text().splitlines()
for line in rows:
 h,name=line.split('  ',1);p=C/name;assert p.resolve().is_relative_to(C.resolve());assert sha(p)==h
jcount=0
for p in C.rglob('*.json'):json.loads(p.read_text());jcount+=1
for p in C.rglob('*'):
 if p.is_file():assert p.stat().st_size<100*1024*1024
for row in json.loads((C/'SOURCE_BINDINGS.json').read_text())['files']:
 assert hashlib.sha256(git('show',SOURCE+':'+row['path'])).hexdigest()==row['sha256'];assert sha(D/row['path'])==row['sha256']
a=json.loads((P/'PRESERVED_EVIDENCE_AUDIT.json').read_text())
for name,h in a['sidecarHashes'].items():assert sha(CHECK/name)==sha(C/'storage-check'/name)==h
for row in json.loads((C/'REPORT_HISTORY_PRESERVATION.json').read_text())['reports']:
 p=D/row['file'];assert sha(p)==row['currentSha256'];old=git('show',SOURCE+':'+row['file']).decode();assert hashlib.sha256(old.encode()).hexdigest()==row['oldSha256'];prefix='## Current run' if p.name=='LOCAL_VALIDATION.md' else '## Current return';hist=old.split('\n',1)[1].replace(prefix,prefix.replace('Current','Historical'),1).lstrip('\n');assert p.read_text().endswith(hist);assert hashlib.sha256(hist.encode()).hexdigest()==row['historicalBodySha256']
linkchecks=[]
for p in [*[D/n for n in docs],C/'README.md']:
 text=p.read_text();text=text.split('## Historical ',1)[0] if p.name!='README.md' else text
 for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
  if '://' in target or target.startswith('#'):continue
  target=target.strip('<>').split('#')[0];resolved=p.parent/target;assert resolved.exists(),(p,target);linkchecks.append({'file':str(p),'target':target})
for label,count in [('storage-tests',48),('orchestration',5),('schema',9)]:
 p=P/'commands'/label;receipt=json.loads((p/'receipt.json').read_text());assert receipt['exitCode']==0
 log=(p/'stderr.log').read_text();assert re.search(r'Ran '+str(count)+r' tests? in ',log) and re.search(r'\nOK\s*$',log);assert 'skipped=' not in log
 assert sha(p/'stdout.log')==receipt.get('stdoutSha256',receipt.get('streams',{}).get('stdout.log')) if 'stdoutSha256' in receipt else True
for name in ['R03LocalBatch-20261007R-lq-storage','Storage-R03LocalBatch-20261007R-lq-storage']:assert not (BASE/name).exists()
for name,pin in json.loads((P/'SOURCE_AUTHORITY.json').read_text())['repositories'].items():
 r=W/name
 if name!='hybridclr_demo':
  assert subprocess.check_output(['git','-C',str(r),'rev-parse','HEAD']).decode().strip()==pin;assert not subprocess.check_output(['git','-C',str(r),'status','--short'])
check={'kind':'SmallBlockerPublicationVerification','startUtc':start,'endUtc':utc(),'sourceCommit':SOURCE,'existingChangesClassified':'Only the two Local reports and the new R prerequisite checkpoint; all source/native/package repositories otherwise clean','checkpointFilesVerifiedBeforeReceipt':len(rows),'jsonFilesParsed':jcount,'ownedLocalLinksChecked':linkchecks,'sourceBlobsMatch':True,'sidecarByteIdentical':True,'historicalReportBodiesPreserved':True,'hostTests':{'Passed':62,'Failed':0,'Skipped':0},'rBatchAndExecutingStorageAbsent':True,'sourcePinsUnchanged':True,'productChanges':[],'reportHashes':{n:sha(D/n) for n in docs},'manifestCoverage':'All checkpoint files except MANIFEST.sha256; regenerated once after this verification receipt','state':'Passed'}
(C/'PUBLICATION_CHECKS.json').write_text(json.dumps(check,indent=2)+'\n')
manifest.write_text('\n'.join(sha(p)+'  '+str(p.relative_to(C)) for p in sorted(C.rglob('*')) if p.is_file() and p!=manifest)+'\n')
git('diff','--check');git('add','--',*owned);git('add','-f','--',*[str(p.relative_to(D)) for p in C.rglob('*.log')]);git('diff','--cached','--check')
staged=git('diff','--cached','--name-only').decode().splitlines();assert set(staged)==set(docs+[str(p.relative_to(D)) for p in C.rglob('*') if p.is_file()])
for n in staged:assert git('show',':'+n)==(D/n).read_bytes(),n
(P/'STAGING_RECEIPT.json').write_text(json.dumps({'startUtc':start,'endUtc':utc(),'state':'Passed','ownedPaths':owned,'stagedFiles':len(staged),'stagedBytesMatchWorkingTree':True,'gitDiffCheck':'Passed','cachedDiffCheck':'Passed','checkpointManifestSha256':sha(manifest),'checkpointFiles':len(manifest.read_text().splitlines())+1,'reportHashes':check['reportHashes']},indent=2)+'\n')
print(json.dumps({'state':'Passed','stagedFiles':len(staged),'checkpointFiles':len(manifest.read_text().splitlines())+1,'hostTests':62,'links':len(linkchecks)}),flush=True)
