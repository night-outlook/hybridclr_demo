from pathlib import Path
import json,hashlib,collections,concurrent.futures,datetime,tarfile,os
BASE=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');P=BASE/'Preflight-R03IRLocal-20261009C-capacity-retry';S=BASE/'R03LocalBatch-20261007S-lr-recovery';D=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');SC=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready';start=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(f):
 with Path(f).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
failure=json.loads((P/'HISTORICAL_CUSTODY_BEFORE.json').read_text());missing={r['path']:r for r in failure['errors']};assert len(missing)==77477 and all('No such file or directory' in r.get('error','') for r in missing.values());groups=collections.Counter();other=[]
for path in missing:
 f=Path(path);assert f.is_relative_to(S/'projects');rel=f.relative_to(S);parts=rel.parts;assert parts[0]=='projects' and parts[2] in ['Library','HybridCLRData'];groups['/'.join(parts[:3])]+=1
top=json.loads((SC/'preflight/POSTRUN_AUTHENTICATION.json').read_text())['topLevelHashes'];actual={n:sha(S/n) for n in top};assert actual==top
index=json.loads((S/'evidence-index.json').read_text());assert len(index['files'])==15712;intersection=[r['path'] for r in index['files'] if str(S/r['path']) in missing];assert not intersection
def check(row):
 f=S/row['path']
 try:return None if sha(f)==row['sha256'] else {'path':str(f),'expected':row['sha256'],'actual':sha(f)}
 except Exception as e:return {'path':str(f),'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:indexErrors=[r for r in pool.map(check,index['files'],buffersize=48) if r]
assert not indexErrors
with tarfile.open(S/'evidence.tar.gz','r:gz') as tar:
 members=tar.getmembers();names={m.name for m in members};archivedMissing=[str(Path(p).relative_to(S)) for p in missing if str(Path(p).relative_to(S)) in names];assert not archivedMissing
builds=[]
for f in sorted((S/'builds').glob('*/build-receipt.json')):
 data=json.loads(f.read_text());bindings=data.get('nativeBinding',{});sdk=bindings.get('installedSdkRoot');builds.append({'path':str(f),'sha256':sha(f),'installedSdkRoot':sdk,'installedSdkRootExists':os.path.exists(sdk) if sdk else None,'historicalReceiptRewritten':False})
report={'state':'CustodyBlocked','startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'expectedFiles':failure['files'],'missingFiles':len(missing),'changedFiles':0,'presentFilesVerified':failure['files']-len(missing),'missingByScope':dict(groups),'missingWitnessSamples':list(missing.values())[:12],'custodyFailureSha256':sha(P/'HISTORICAL_CUSTODY_BEFORE.json'),'mapSha256':failure['mapSha256'],'missingFileClassification':'S unindexed retained Library/HybridCLRData custody snapshots; not indexed sealed core evidence','indexAndArchiveMissingIntersection':0,'sealedS':{'topArtifactHashes':actual,'indexedFiles':15712,'indexedErrors':indexErrors,'archiveBytes':(S/'evidence.tar.gz').stat().st_size,'archiveMembers':len(members),'missingFilesPresentInSealedArchive':0,'state':'Passed read-only byte/index authentication only'},'retainedR':failure['retainedR'],'buildReceiptBindings':builds,'deletionActorAndExactTime':'Unavailable','rootCause':'Previously authenticated protected files are now absent; runtime source/expectation changes are not established','automaticRestorationPerformed':False,'missingFilesRebaselined':False,'historicalS90PassedReclassified':False,'runtimeBatch':'NotRun','unityLaunches':0,'runtimeAcceptance':False}
with (P/'CUSTODY_FAILURE_ANALYSIS.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({'state':report['state'],'missingFiles':len(missing),'sealedS':report['sealedS']['state'],'indexedFiles':15712,'archiveMembers':len(members),'absentCacheScopes':len(groups)}),flush=True)
