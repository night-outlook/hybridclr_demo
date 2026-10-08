"""Final independent read-only custody/filesystem checks after blocked admission."""
from pathlib import Path
import json,hashlib,datetime,subprocess,plistlib,concurrent.futures,time,sys,os
P=Path(__file__).resolve().parent;BASE=P.parent;W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';CHECK=BASE/'StorageCheck-R03LocalBatch-20261007S-lr-recovery';R=BASE/'R03LocalBatch-20261007R-lq-storage';PY='/Library/Frameworks/Python.framework/Versions/3.14/bin/python3';sys.path[:0]=[str(D/'Tools/AssemblyShadow/R03Completion'),str(D/'Tools/AssemblyShadow/R03Storage')];import retained_transaction as retained;import storage_guard as storage

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(n,value):
 with (P/n).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def cmd(label,argv):
 folder=P/'operations'/label;folder.mkdir();beg=utc();r=subprocess.run(argv,capture_output=True);(folder/'stdout.log').write_bytes(r.stdout);(folder/'stderr.log').write_bytes(r.stderr);save_path=folder/'receipt.json';save_path.write_text(json.dumps({'argv':argv,'startUtc':beg,'endUtc':utc(),'exitCode':r.returncode,'state':'Captured' if r.returncode==0 else 'Unavailable','stdoutSha256':sha(folder/'stdout.log'),'stderrSha256':sha(folder/'stderr.log')},indent=2)+'\n');return r
start=utc();r=cmd('resolved-df',['/bin/df','-k',str(P),str(W),'/private/tmp',str(CHECK)]);assert r.returncode==0;devices=sorted({line.split()[0] for line in r.stdout.decode().splitlines()[1:]});infos={}
for i,device in enumerate(devices):
 r=cmd('resolved-device-'+str(i),['/usr/sbin/diskutil','info','-plist',device]);infos[device]=plistlib.loads(r.stdout) if r.returncode==0 else {'state':'Unavailable'}
r=cmd('resolved-apfs',['/usr/sbin/diskutil','apfs','list','-plist']);apfs=plistlib.loads(r.stdout) if r.returncode==0 else None;r=cmd('resolved-quota',['/usr/bin/quota','-v']);quota={'exitCode':r.returncode,'stdout':r.stdout.decode(),'stderr':r.stderr.decode()};matches=[]
if apfs:
 for c in apfs.get('Containers',[]):
  for v in c.get('Volumes',[]):
   if '/dev/'+v.get('DeviceIdentifier','') in devices:matches.append({'containerReference':c['ContainerReference'],'containerUUID':c.get('APFSContainerUUID'),'containerFree':c['CapacityFree'],'volume':v})
def clean(value):
 if isinstance(value,dict):return {k:clean(v) for k,v in value.items()}
 if isinstance(value,list):return [clean(v) for v in value]
 if isinstance(value,bytes):return {'hex':value.hex()}
 if isinstance(value,datetime.datetime):return value.isoformat()
 return value
save('FILESYSTEM_SUPPLEMENT.json',clean({'kind':'ReadOnlyResolvedDeviceSupplement','startUtc':start,'endUtc':utc(),'devices':devices,'deviceInfo':infos,'matchingApfsVolumes':matches,'quota':quota,'samePoolNotSummed':True,'noCapacityRemediationPerformed':True,'originalDirectoryDiagnosticsPreserved':True}))
# Exact sidecar and launch absence authentication.
ad=json.loads((CHECK/'admission.json').read_text());session=json.loads((CHECK/'session.json').read_text());dispatch=json.loads((CHECK/'dispatch.json').read_text());samples=[json.loads(x) for x in (CHECK/'capacity.jsonl').read_text().splitlines()];assert ad['state']=='Blocked' and not ad['batchStarted'] and session['state']=='NotAdmitted' and not session['batchStarted'];assert session['telemetrySha256']==sha(CHECK/'capacity.jsonl');assert dispatch['storageSessionSha256']==sha(CHECK/'session.json') and dispatch['coreResultPath'] is None;assert ad['requiredAvailableBytesEachLocation']==max(64*1024**3,2*ad['retainedQSize']['planningBytes']+20*1024**3);minimum=min(v['availableBytes'] for v in samples[0]['volumes']);assert minimum<ad['requiredAvailableBytesEachLocation'];assert not(BASE/'R03LocalBatch-20261007S-lr-recovery').exists() and not(BASE/'Storage-R03LocalBatch-20261007S-lr-recovery').exists()
local={'kind':'LocalStoragePrerequisiteResult','result':'CapacityBlocked','batchResult':'NotRun','sourceDemoCommit':'e8fda852684f584295fe37830340ab3c9f3fcc4f','batchStarted':False,'unityOrPlayerLaunches':0,'admissionState':ad['state'],'diagnosticSessionState':session['state'],'diagnosticExitCode':2,'requiredBytes':ad['requiredAvailableBytesEachLocation'],'availableAdmissionBytes':minimum,'deficitBytes':ad['requiredAvailableBytesEachLocation']-minimum,'allocationProbes':'NotRun: capacity prerequisite failed before probes','all90CellsSixBuilds59Players18_754_755Editor':'NotRun: no batch constructed','coreResultLedgerSeal':'Unavailable: no core batch constructed','sidecarHashes':{f.name:sha(f) for f in CHECK.iterdir() if f.is_file()},'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'ReadyForHumanReviewGate':False,'pureInterpreterExpansionEnabled':False,'noRemediationOrThresholdChanges':True};save('LOCAL_STORAGE_RESULT.json',local)
# Re-read six witnesses in memory; no CLI output/root reuse or restoration.
six=retained.verify(R,retained.inputs());six.update({'recordedUtc':utc(),'initialReportUnmodified':True,'inputManifestSha256':sha(D/'Tools/AssemblyShadow/R03Completion/lr-retained.json')});save('RETAINED_R_AFTER.json',six)
expected=json.loads((P/'prior-evidence-custody.json').read_text());assert sha(P/'prior-evidence-custody.json')==json.loads((P/'HISTORICAL_CUSTODY_BEFORE.json').read_text())['expectedMapSha256'];errors=[];done=0;last=time.monotonic();beg=utc()
def verify(row):
 path,h=row
 try:
  actual=sha(path);return None if actual==h else {'path':path,'expectedSha256':h,'actualSha256':actual}
 except Exception as e:return {'path':path,'expectedSha256':h,'error':repr(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for error in pool.map(verify,expected.items(),buffersize=48):
  done+=1
  if error:errors.append(error)
  if time.monotonic()-last>20:print('Final custody checked',done,'/',len(expected),flush=True);last=time.monotonic()
links=json.loads((P/'RETAINED_R_SYMLINKS.json').read_text());assert all(Path(path).is_symlink() and os.readlink(path)==target for path,target in links.items());save('HISTORICAL_CUSTODY_AFTER.json',{'kind':'SFinalReadOnlyHistoricalCustody','startUtc':beg,'endUtc':utc(),'state':'Passed' if not errors else 'Failed','uniqueFiles':len(expected),'errors':errors,'expectedMapSha256':sha(P/'prior-evidence-custody.json'),'retainedRStillStaged':True,'historicalResultsReclassified':False,'initialRReadOnlyAuditUnmodified':True});assert not errors,errors[:5]
# No live S footprint exists. Budget only the factual prerequisite publication payload, not a fabricated batch.
inputs=[P,BASE/'RetainedR-R03LocalBatch-20261007S-lr-recovery',BASE/'Transport-R03LocalBatch-20261007S-lr-recovery',CHECK];size=sum(f.stat().st_size for root in inputs for f in root.rglob('*') if f.is_file());common=Path(subprocess.check_output(['git','-C',str(D),'rev-parse','--path-format=absolute','--git-common-dir'],text=True).strip());observation=storage.sample({'publicationCheckout':D,'preflight':P,'gitCommon':common});required=max(storage.FLOOR,size+storage.MARGIN);storage.capacity_ok(observation,required);save('storage-publication-check.json',{'kind':'PrerequisiteBlockerPublicationCapacity','recordedUtc':utc(),'state':'Passed','requiredBytes':required,'ownedPayloadBytes':size,'observation':observation,'noSBatchFootprintExists':True,'corePublicationFootprintCheck':'NotRun: core never constructed','onlySmallFactualPrerequisiteCheckpoint':True})
print('Final custody and retained-R authentication Passed; S CapacityBlocked/NotRun',flush=True)
