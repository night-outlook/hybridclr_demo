from pathlib import Path
import json,hashlib,subprocess,concurrent.futures,tarfile,datetime,sys
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261009D-custody-scoped');C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-c-custody-blocked';BASE=P.parent;S=BASE/'R03LocalBatch-20261007S-lr-recovery'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
start=now();names=[]
for l in (C/'MANIFEST.sha256').read_text().splitlines():
 h,n=l.split('  ',1);assert sha(C/n)==h;nbytes=(C/n).read_bytes();raw=subprocess.check_output(['git','-C',str(D),'show','36b9828d62bb81d98e81d055871a9540fe116276:'+str((C/n).relative_to(D))]);assert raw==nbytes;names.append(n)
assert {str(f.relative_to(C)) for f in C.rglob('*') if f.is_file()}==set(names)|{'MANIFEST.sha256'}
raw=subprocess.check_output(['git','-C',str(D),'show','36b9828d62bb81d98e81d055871a9540fe116276:'+str((C/'MANIFEST.sha256').relative_to(D))]);assert raw==(C/'MANIFEST.sha256').read_bytes()
a=json.loads((C/'preflight/CUSTODY_FAILURE_ANALYSIS.json').read_text());actual={n:sha(S/n) for n in a['sealedS']['topArtifactHashes']};assert actual==a['sealedS']['topArtifactHashes']
index=json.loads((S/'evidence-index.json').read_text());assert len(index['files'])==15712
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 vals=list(pool.map(lambda r:sha(S/r['path'])==r['sha256'], index['files']))
assert all(vals)
with tarfile.open(S/'evidence.tar.gz','r:gz') as t:
 members=t.getmembers();archiveNames={r.name for r in members};assert len(members)==15713;assert all(r['path'] in archiveNames for r in index['files'])
assert (S/'evidence.tar.gz').stat().st_size==587907380
record={'state':'Passed byte/index/Git authentication only','startUtc':start,'endUtc':now(),'originalCPublication':'36b9828d62bb81d98e81d055871a9540fe116276','cManifestSha256':sha(C/'MANIFEST.sha256'),'cManifestFiles':len(names),'allCCheckpointFilesMatchOriginalGit':True,'sTopArtifactHashes':actual,'indexedFilesVerified':15712,'archiveBytes':587907380,'archiveMembers':len(members),'archiveCoversAllIndexedPaths':True,'strictHistoricalCustody':'Blocked','runtimeAcceptance':False,'unityLaunched':False}
(P/'SEALED_S_AND_C_AUTHENTICATION.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
