from pathlib import Path
import subprocess,json,hashlib,datetime,plistlib,concurrent.futures,os,time
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo'
BASE=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');P=BASE/'Preflight-R03LocalBatch-20261007R-lq-storage';CHECK=BASE/'StorageCheck-R03LocalBatch-20261007R-lq-storage';Q=BASE/'R03LocalBatch-20261006Q-lp-repair'
QC=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261006-batch-q-return-required';SOURCE='cbf80474ebdee125e1d162d9c32a1734ee541720'
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,a):
 with p.open('x') as f:json.dump(a,f,indent=2);f.write('\n')
def cmd(label,argv):
 p=P/'commands'/label;p.mkdir();start=utc();r=subprocess.run(argv,cwd=D,capture_output=True)
 (p/'stdout.log').write_bytes(r.stdout);(p/'stderr.log').write_bytes(r.stderr)
 a={'command':argv,'cwd':str(D),'startUtc':start,'endUtc':utc(),'exitCode':r.returncode,'state':'Captured' if r.returncode==0 else 'Unavailable','stdoutSha256':digest(p/'stdout.log'),'stderrSha256':digest(p/'stderr.log')};write(p/'receipt.json',a);return r,a
start=utc();r,df=cmd('supplemental-df',['/bin/df','-k',str(BASE),str(W),'/private/tmp',str(D)])
assert r.returncode==0
lines=r.stdout.decode().splitlines()[1:];devices=sorted({line.split()[0] for line in lines});infos=[]
for i,device in enumerate(devices):
 r,a=cmd(f'supplemental-device-{i}', ['/usr/sbin/diskutil','info','-plist',device]);infos.append({'device':device,'receipt':a,'info':plistlib.loads(r.stdout) if r.returncode==0 else None})
r,a=cmd('supplemental-apfs',['/usr/sbin/diskutil','apfs','list','-plist']);apfs=plistlib.loads(r.stdout) if r.returncode==0 else None
r,q=cmd('supplemental-quota',['/usr/bin/quota','-v'])
volumes=[]
if apfs:
 for container in apfs.get('Containers',[]):
  matching=[v for v in container.get('Volumes',[]) if '/dev/'+v.get('DeviceIdentifier','') in devices]
  if matching:volumes.append({'container':container,'matchingDeviceIdentifiers':[v['DeviceIdentifier'] for v in matching]})
# Plists retained verbatim in command streams; convert plist types only in the derivative report.
def clean(v):
 if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
 if isinstance(v,list):return [clean(x) for x in v]
 if isinstance(v,bytes):return {'hex':v.hex()}
 if isinstance(v,datetime.datetime):return v.isoformat()
 return v
write(P/'FILESYSTEM_SUPPLEMENT.json',clean({'kind':'ReadOnlyResolvedDeviceSupplement','startUtc':start,'endUtc':utc(),'devicesFromDf':devices,'deviceInfos':infos,'matchingApfsContainers':volumes,'quotaReceipt':q,'originalDirectoryDiagnosticsUnchanged':True,'capacityRemediationPerformed':False,'interpretation':'Supplemental current observations; no reconstruction of Q allocation failure or reservation. Original ordinary-directory diskutil errors remain Unavailable.'}))
print('Resolved-device diagnostics captured',flush=True)
start=utc();mf=QC/'MANIFEST.sha256';rel=str(mf.relative_to(D));blob=subprocess.check_output(['git','-C',str(D),'show',SOURCE+':'+rel]);assert mf.read_bytes()==blob
expected={};groups={}
def bind(path,sha,group):
 path=str(path);assert len(sha)==64
 if path in expected:assert expected[path]==sha,(path,'Conflicting expected bindings')
 expected[path]=sha;groups.setdefault(group,set()).add(path)
for line in blob.decode().splitlines():
 sha,name=line.split('  ',1);p=QC/name;assert p.resolve().is_relative_to(QC.resolve());bind(p,sha,'qCheckpointManifest')
priorpath=QC/'preflight/prior-evidence-custody.json';prior=json.loads(priorpath.read_text())
for p,sha in prior.items():bind(p,sha,'priorCustody')
post=json.loads((QC/'preflight/POSTRUN_AUTHENTICATION.json').read_text())
for name,sha in post['topLevelHashes'].items():bind(Q/name,sha,'qTopLevel')
index=json.loads((Q/'evidence-index.json').read_text())
for row in index['files']:
 p=Q/row['path'];assert p.resolve().is_relative_to(Q.resolve());assert p.stat().st_size==row['size'];bind(p,row['sha256'],'qLiveIndex')
errors=[];done=0;last=time.monotonic()
def verify(item):
 p,want=item
 try:
  actual=digest(p);return None if actual==want else {'path':p,'expectedSha256':want,'actualSha256':actual}
 except Exception as e:return {'path':p,'expectedSha256':want,'error':repr(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for error in pool.map(verify,expected.items(),buffersize=48):
  done+=1
  if error:errors.append(error)
  if time.monotonic()-last>20:print('Custody verified',done,'of',len(expected),flush=True);last=time.monotonic()
result={'kind':'SourceAuthenticatedHistoricalEvidenceCustody','startUtc':start,'endUtc':utc(),'sourceCommit':SOURCE,'qCheckpointPath':str(QC),'qManifestPath':str(mf),'qManifestSha256':digest(mf),'qManifestMatchesSourceGitBlob':True,'priorBindingMapPath':str(priorpath),'priorBindingMapSha256':digest(priorpath),'counts':{g:len(v) for g,v in groups.items()},'uniquePathsVerified':len(expected),'errors':errors,'state':'Passed' if not errors else 'Failed','historicalEvidenceReclassified':False,'retainedQPlanningScanIsNotCustodyProof':True,'qOriginalCounts':post['counts'],'qOriginalCellCount':post['cells'],'topLevelQHashes':post['topLevelHashes'],'rRootExists':(BASE/'R03LocalBatch-20261007R-lq-storage').exists(),'executingStorageRootExists':(BASE/'Storage-R03LocalBatch-20261007R-lq-storage').exists(),'sidecarHashes':{str(p.relative_to(CHECK)):digest(p) for p in sorted(CHECK.rglob('*')) if p.is_file()}}
write(P/'PRESERVED_EVIDENCE_AUDIT.json',result);assert not errors,errors[:10];assert not result['rRootExists'] and not result['executingStorageRootExists'];print(json.dumps({k:result[k] for k in ['state','counts','uniquePathsVerified','endUtc']}),flush=True)
