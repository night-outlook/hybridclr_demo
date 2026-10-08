"""Read-only independent seal/ledger/receipt/custody authentication after S exits."""
from pathlib import Path
import json,hashlib,datetime,collections,tarfile,concurrent.futures,sys,subprocess,os
P=Path(__file__).resolve().parent;BASE=P.parent;B=BASE/'R03LocalBatch-20261007S-lr-recovery';W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';S=BASE/'Storage-R03LocalBatch-20261007S-lr-recovery-2'
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def load(path):return json.loads(Path(path).read_text())
def save(name,value):
 with (P/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
start=utc();errors=[];record={'kind':'ReadOnlySPostrunAuthentication','startUtc':start,'state':'Unavailable','runtimeAcceptance':False}
try:
 assert (P/'operations/storage-executing/receipt.json').exists(),'Outer invocation must finish first'
 result=load(B/'LOCAL_BATCH_RESULT.json');ledger=load(B/'BATCH_EXECUTION.json');idx=load(B/'evidence-index.json');seal=load(B/'seal-receipt.json');cells=result['cells'];assert cells==ledger['cells'] and len(cells)==len({x['id'] for x in cells})==90;assert sha(B/'BATCH_EXECUTION.json')==result['executionLedgerSha256'];assert seal==result['seal'] and sha(B/'evidence-index.json')==seal['indexSha256'] and sha(B/'evidence.tar.gz')==seal['archiveSha256']
 for c in cells:assert load(B/'cells'/(c['id']+'.json'))==c
 for flag in ['R03Accepted','H2Passed','qualificationApproved','pureInterpreterExpansionEnabled','fullLegacyRegressionAcceptance']:assert result[flag] is False
 expected={}
 for row in idx['files']:
  path=B/row['path'];assert path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(B);assert path.stat().st_size==row['size'] and sha(path)==row['sha256'];expected[row['path']]=row
 assert len(expected)==len(idx['files']);expected['evidence-index.json']={'size':(B/'evidence-index.json').stat().st_size,'sha256':sha(B/'evidence-index.json')}
 with tarfile.open(B/'evidence.tar.gz','r:gz') as archive:
  seen=set()
  for member in archive:
   assert member.name not in seen and member.name in expected and member.isfile();seen.add(member.name);row=expected[member.name];assert member.size==row['size'];stream=archive.extractfile(member);digest=hashlib.sha256()
   for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
   assert digest.hexdigest()==row['sha256'],member.name
  assert seen==set(expected)
 command_rows=[]
 for file in sorted((B/'commands').glob('*/command.json')):
  c=load(file);assert sha(file.parent/'stdout.log')==c['stdoutSha256'] and sha(file.parent/'stderr.log')==c['stderrSha256'];command_rows.append({'id':file.parent.name,'exitCode':c['exitCode'],'pid':c['pid'],'pgid':c['pgid'],'remainingProcessGroup':c.get('remainingProcessGroup'),'postCleanupGroupExists':c.get('postCleanupGroupExists'),'commandReceiptSha256':sha(file)})
  if c.get('remainingProcessGroup'):assert (file.parent/'process-group-before-cleanup.json').exists()
 editors=[]
 import xml.etree.ElementTree as ET
 for label in ['focused-editor','resource-editor']:
  folder=B/label
  if (folder/'verification.json').exists():
   v=load(folder/'verification.json');row={'path':str(folder),'verification':v,'verificationSha256':sha(folder/'verification.json'),'classification':'Fresh actual execution if XML exists'}
   if (folder/'results.xml').exists():
    tree=ET.parse(folder/'results.xml').getroot();row['xmlSha256']=sha(folder/'results.xml');row['xmlAttributes']=tree.attrib
    if v['result']=='Passed':
     assert v['xmlSha256']==row['xmlSha256'] and v['scopeSha256']==sha(folder/'scope.json');assert tree.get('failed')=='0' and tree.get('skipped')=='0' and tree.get('inconclusive')=='0'
   editors.append(row)
 players=[]
 paths=list((B/'players').glob('*/verification.json'))+list((B/'resource-players').glob('*/verification.json'))+list((B/'measurements').glob('*/*/verification.json'))+list((B/'early').glob('*/verification.json'))
 for file in sorted(paths):
  v=load(file);row={'path':str(file),'result':v['result'],'sha256':sha(file),'launchPid':v.get('launchPid'),'rawPath':v.get('rawPath'),'rawSha256':v.get('rawSha256')}
  if v.get('rawPath') and v.get('rawSha256'):assert sha(v['rawPath'])==v['rawSha256']
  if v.get('commandReceipt') and v.get('commandSha256'):assert sha(v['commandReceipt'])==v['commandSha256']
  if v.get('rawSha256') and (file.parent/'raw.json').exists():assert sha(file.parent/'raw.json')==v['rawSha256']
  players.append(row)
 recovery=load(B/'transaction-recovery/verification.json') if (B/'transaction-recovery/verification.json').exists() else {'state':'Unavailable'}
 if recovery.get('stage')=='Complete' and recovery.get('cleanupResult')=='ExactOriginalBytesRestored':
  config=load(B/'resource-project.json');project=Path(config['projectPath']);run=Path(config['runPath']);state=load(run/'p05-define-state.json');assert sha(project/'ProjectSettings/ProjectSettings.asset')==sha(run/'p05-project-settings.original')==state['originalSettingsSha256']==recovery['originalSettingsSha256']==recovery['afterSettingsSha256'];assert sha(B/'transaction-recovery/settings-before.bytes')==recovery['beforeSettingsSha256'];assert (run/'p05-restored.json').exists() and (run/'p05-settings-restored.json').exists() and (run/'p05-unity-restored.bytes').exists()
 current=load(P/'prior-evidence-custody.json');custody_errors=[]
 def verify(row):
  path,h=row
  try:
   actual=sha(path);return None if actual==h else {'path':path,'expectedSha256':h,'actualSha256':actual}
  except Exception as e:return {'path':path,'expectedSha256':h,'error':str(e)}
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for error in pool.map(verify,current.items(),buffersize=48):
   if error:custody_errors.append(error)
 save('HISTORICAL_CUSTODY_AFTER.json',{'kind':'ReadOnlySContinuationAfterCustody','recordedUtc':utc(),'state':'Passed' if not custody_errors else 'Failed','uniqueFiles':len(current),'expectedMapSha256':sha(P/'prior-evidence-custody.json'),'errors':custody_errors,'historicalClassificationChanged':False});assert not custody_errors,'Historical custody changed'
 sys.path.insert(0,str(D/'Tools/AssemblyShadow/R03Completion'));import retained_transaction
 rr=retained_transaction.verify(BASE/'R03LocalBatch-20261007R-lq-storage',retained_transaction.inputs());save('RETAINED_R_AFTER.json',dict(rr,recordedUtc=utc(),initialOutputUnmodified=True))
 session=load(S/'session.json');dispatch=load(S/'dispatch.json');outer=load(P/'operations/storage-executing/receipt.json');assert dispatch['batchStarted'] is True and dispatch['coreResultSha256']==sha(B/'LOCAL_BATCH_RESULT.json') and dispatch['storageSessionSha256']==sha(S/'session.json');counts=dict(collections.Counter(c['result'] for c in cells))
 if counts.get('Passed')==90:
  assert len(players)==59 and all(x['result']=='Passed' for x in players),'All 59 fresh Player records required'
  assert len(editors)==2 and all(x['verification']['result']=='Passed' for x in editors),'Both real Editor rosters required'
  assert recovery.get('cleanupResult')=='ExactOriginalBytesRestored' and recovery.get('remoteAuthority')=='Passed' and recovery.get('stage')=='Complete','Complete cleanup plus fresh remote acceptance required'
 record.update(state='Passed',endUtc=utc(),coreResult=result['result'],sealStatus=result['sealStatus'],cells=90,counts=counts,failedCells=[c for c in cells if c['result']=='Failed'],blockedCells=[c['id'] for c in cells if c['result']=='Blocked'],indexedLiveFiles=len(idx['files']),archiveMembers=len(expected),commandReceipts=command_rows,editorEvidence=editors,playerVerificationRecords=players,playerVerificationCount=len(players),transactionRecovery=recovery,storageSessionState=session['state'],storageProblem=session.get('latchedProblem'),outerExitCode=outer['exitCode'],custodyFiles=len(current),retainedR=rr,topLevelHashes={n:sha(B/n) for n in ['LOCAL_BATCH_RESULT.json','BATCH_EXECUTION.json','evidence-index.json','evidence.tar.gz','seal-receipt.json']},publicationIsNotRuntimeAcceptance=True)
except Exception as e:record.update(state='Failed',endUtc=utc(),error={'type':type(e).__name__,'message':str(e)})
save('POSTRUN_AUTHENTICATION.json',record);print(json.dumps({k:record[k] for k in ['state','coreResult','counts','indexedLiveFiles','archiveMembers','playerVerificationCount','outerExitCode','error'] if k in record}),flush=True)
if record['state']!='Passed':raise SystemExit(1)
