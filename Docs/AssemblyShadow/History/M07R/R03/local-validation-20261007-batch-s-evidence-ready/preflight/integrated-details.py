"""Read-only factual substate summary; no producer receipt or acceptance rewriting."""
from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).resolve().parent;B=P.parent/'R03LocalBatch-20261007S-lr-recovery';load=lambda p:json.loads(Path(p).read_text())
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
result=load(B/'LOCAL_BATCH_RESULT.json');cells={r['id']:r for r in result['cells']};builds=[]
for role in ['candidate-release','reference-release','candidate-debug','candidate-off']:
 file=B/'builds'/role/'build-receipt.json'
 if file.exists():
  r=load(file);cell=cells['build-'+role];builds.append({'role':role,'result':cell['result'],'receipt':str(file),'sha256':sha(file),'schemaVersion':r['schemaVersion'],'architecture':r['architecture'],'errors':r['errors'],'installedNativeRoot':r['installedNativeRoot'],'nativeBinding':cell.get('evidence',{}).get('nativeBinding'),'playerInventoryEntries':len(r['playerFiles']),'buildGuidState':'Unavailable','buildGuidReason':'Original focused producer receipt does not emit a GUID; exact Player inventory/receipt and installed-native bindings are preserved instead.'})
for role in ['on','off']:
 c=cells['resource-player-'+role]
 if c['result']=='Passed':
  phase=load(c['evidence']['phaseReceipt']);file=Path(phase['playerReceipt']);r=load(file);assert sha(file)==phase['playerReceiptSha256'];assert sha(r['nativeLibraryPath'])==r['nativeLibrarySha256'];builds.append({'role':'resource-'+role,'result':c['result'],'receipt':str(file),'sha256':sha(file),'buildGuid':r['buildGuid'],'buildGuidState':'Available','architecture':r['architecture'],'nativeLibrarySha256':r['nativeLibrarySha256'],'nativeMetadataSha256':r['nativeMetadataSha256'],'inputSnapshotHash':r['inputSnapshotHash'],'runtimeAbiHash':r['runtimeAbiHash']})
warm=[];controls=[];rejections=[]
for file in sorted((B/'players').glob('*/verification.json')):
 v=load(file);w=v.get('warmWindow',{});name=file.parent.name
 if w.get('policy')=='R03ExactAllocationWindowV1':warm.append({'case':name,'result':v['result'],'warmWindow':w,'verificationSha256':sha(file)})
 if 'unisolatedWarmCertificate' in w:controls.append({'case':name,'diagnosticResult':v['result'],'unisolatedWarmCertificate':w['unisolatedWarmCertificate'],'identifiedLoopAdmissions':w['identifiedLoopAdmissions'],'verificationSha256':sha(file)})
 if 'rejectionObservation' in v:rejections.append({'case':name,'rejectionObservation':v['rejectionObservation'],'verificationSha256':sha(file)})
c07=load(B/'players/C07-private-primitive-append/verification.json') if (B/'players/C07-private-primitive-append/verification.json').exists() else None
editors=[]
for name in ['focused-editor','resource-editor']:
 f=B/name/'verification.json'
 if f.exists():editors.append({'role':name,'verification':load(f),'sha256':sha(f)})
integration=cells['production-entry-integration'];integration_record=None
if integration['result']=='Passed':
 integration_record=load(integration['evidence']['path']);assert integration_record['returnChangedRoots']==[] and integration_record['returnClosure']==[]
record={'kind':'SIntegratedReadOnlyObservations','recordedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'builds':builds,'focusedGuidAbsenceIsExplicitNotInvented':True,'earlyEditor18':cells['completion-tool-contracts'].get('evidence',{}).get('earlyEditorFixtures'),'editors':editors,'strictWarmWitnesses':warm,'producerControls':controls,'producerAggregate':load(B/'producer-controls.json') if (B/'producer-controls.json').exists() else None,'positiveC07':{'result':c07['result'],'layout':c07.get('prepublicationLayout')} if c07 else None,'rejectionObservations':rejections,'transactionRecovery':load(B/'transaction-recovery/verification.json') if (B/'transaction-recovery/verification.json').exists() else None,'productionIntegration':integration_record,'resourceAggregate':load(B/'resource-contracts.json') if (B/'resource-contracts.json').exists() else None,'measurementSummary':load(B/'measurements.json') if (B/'measurements.json').exists() else None,'acceptanceFlagsUnchanged':True,'historicalResultsUnchanged':True}
if result['result']=='EvidenceReadyForPrimaryReview':
 assert len(builds)==6 and len(warm)==6 and len(controls)==4;assert all(w['unisolatedWarmCertificate']=='Failed' for w in controls);assert c07['prepublicationLayout']['physicalProof'] and c07['prepublicationLayout']['baselineReady'] and c07['prepublicationLayout']['targetReady'];assert len(editors)==2 and editors[0]['verification']['cases']==754 and editors[1]['verification']['cases']==755
with (P/'INTEGRATED_DETAILS.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print('Detailed observations preserved',len(builds),'builds',len(warm),'strict witnesses',len(controls),'contaminated controls',flush=True)
