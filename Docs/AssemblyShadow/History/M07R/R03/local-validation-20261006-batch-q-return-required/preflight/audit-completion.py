"""Read-only replay of original contracts against sealed batch Q; no launches."""
import collections,datetime,hashlib,json,pathlib,statistics,subprocess,sys,types,xml.etree.ElementTree as ET
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261006Q-lp-repair';R=P.parent/'R03LocalBatch-20261006Q-lp-repair';sys.path[:0]=[str(D/'Tools/AssemblyShadow/R03Completion'),str(D/'Tools/AssemblyShadow/R03'),str(D/'Tools/AssemblyShadow')]
import os
os.environ['GIT_SSH_COMMAND']=json.loads((P/'SSH_TRANSPORT.json').read_text())['command']
import fixture_authority
from fixture_authority import verify_graph,verify_installation,authenticate_copy
from fixture_project import verify_sources
from editor_contract import verify as verify_editor
from execution_contract import verify as verify_execution
from run_completion import cell_plan
import m07_results as m07,r00_results as r00,r01_early_results as early
from legacy_runtime import EARLY_CASES
from type_resolution_schema import current_m07_schema
def verify_current_m07_case(*args,**kwargs):
    with current_m07_schema() as bridge:
        value=m07.verify_case(*args,**kwargs)
    return value
load=lambda p:json.loads(pathlib.Path(p).read_text())
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
# Keep production receipt emission read-only: authenticate identical existing JSON.
def authenticate_existing_receipt(path,value):
 path=pathlib.Path(path);assert path==R/'native-codec-source-verification.json' and path.is_file()
 assert load(path)==value;return None
fixture_authority.write=authenticate_existing_receipt
started=datetime.datetime.now(datetime.timezone.utc).isoformat();result=load(R/'LOCAL_BATCH_RESULT.json');cells={c['id']:c for c in result['cells']};plan=load(R/'completion-plan.json');assert list(cells)==plan['cells']==cell_plan(load(D/'Tools/AssemblyShadow/R03/player-cases.json')) and len(cells)==90
for k in ['R03Accepted','H2Passed','pureInterpreterExpansionEnabled','qualificationApproved','fullLegacyRegressionAcceptance']:assert result[k] is False
checks=[];players=[];builds=[]
def check(name,fn,deps=()):
 blocked=[c for c in deps if cells[c]['result']!='Passed']
 if blocked:checks.append({'id':name,'state':'NotRun','reason':'Original prerequisite not Passed','dependencies':blocked});return None
 try:evidence=fn()
 except Exception as exc:checks.append({'id':name,'state':'Failed','error':str(exc)});return None
 checks.append({'id':name,'state':'Passed','evidence':evidence});return evidence

def qualification():
 data=load(R/'qualification/results.json');assert data['kind']=='R03QualificationContracts' and data['result']=='Passed' and len(data['cases'])==32 and data['failures']==0 and data['runtimeProofExecuted'] is False and data['expansionAuthorized'] is False
 for item in data['inventory']:
  f=R/'qualification'/item['path'];assert sha(f)==item['sha256'] and f.stat().st_size==item['size']
 return {'path':str(R/'qualification/results.json'),'sha256':sha(R/'qualification/results.json'),'cases':32,'inventoryFiles':len(data['inventory']),'runtimeProofExecuted':False,'expansionAuthorized':False,'classification':'Static real-DLL qualification input, not runtime/expansion authority'}
check('static-qualification',qualification,['qualification'])
for folder,count,cell in [('focused-editor',754,'editor-tests'),('resource-editor',755,'resource-editor')]:
 def editor(folder=folder,count=count,cell=cell):
  root=R/folder;scope=load(root/'scope.json');v=load(root/'verification.json');fresh=verify_editor(ET.parse(root/'results.xml').getroot(),scope);assert fresh['result']==v['result']=='Passed' and fresh['cases']==count and fresh['skipped']==0
  assert all(v[k]==x for k,x in fresh.items()) and sha(root/'results.xml')==v['xmlSha256'] and sha(root/'scope.json')==v['scopeSha256'] and cells[cell]['evidence']==v
  return {'scope':str(root/'scope.json'),'scopeSha256':sha(root/'scope.json'),'xml':str(root/'results.xml'),'xmlSha256':sha(root/'results.xml'),'verificationSha256':sha(root/'verification.json'),'freshReadOnlyContract':fresh}
 check(folder,editor,[cell])
config=load(R/'resource-project.json') if (R/'resource-project.json').exists() else None
batch=types.SimpleNamespace(workspace=W,root=R,pins=result['repositories'],resource_config=config)
context=None
if config:
 def phase_receipts():
  project,pins=authenticate_copy(batch,config);sources=verify_sources(project,config,configured=True);records=[]
  for phase in ['install','compiler','resources','player-on','player-off','prepare','compile','restore','finalize']:
   p=pathlib.Path(config['receiptRoot'])/(phase+'.json')
   if not p.exists():records.append({'phase':phase,'state':'Unavailable','expectedCellState':cells['resource-'+{'install':'install','compiler':'compiler','resources':'bundles','player-on':'player-on','player-off':'player-off','prepare':'p05-prepare','compile':'p05-compile','restore':'p05-restore','finalize':'p05-finalize'}[phase]]['result']});continue
   d=load(p);assert d['kind']=='R03OriginalResourceBuildAdapter' and d['phase']==phase and d['projectPath']==str(project) and d['baselineId']==config['baselineId'] and d['unityVersion']=='2022.3.62f2' and d['target']=='StandaloneOSX'
   assert all(d[k] is False for k in ['expansionAuthorized','R03Accepted','H2Passed']) and d['sourcePinsSha256']==sha(project/'ProjectSettings/AssemblyShadowSourcePins.json');records.append({'phase':phase,'path':str(p),'sha256':sha(p),'receipt':d})
  return {'project':str(project),'sourceVerification':sources,'receipts':records}
 check('copied-resource-source-and-phase-bindings',phase_receipts,['resource-install','resource-p05-restore'])
 def restoration():
  project=pathlib.Path(config['projectPath']);run=pathlib.Path(config['runPath']);state=load(run/'p05-define-state.json');original=run/'p05-project-settings.original';production=load(run/'p05-restored.json');wrapper=load(run/'p05-settings-restored.json');unitybytes=run/'p05-unity-restored.bytes';settings=project/'ProjectSettings/ProjectSettings.asset'
  assert sha(original)==sha(settings)==state['originalSettingsSha256']==production['originalSettingsSha256']==wrapper['originalSettingsSha256']
  assert sha(unitybytes)==production['restoredSettingsSha256']==wrapper['restoredSettingsSha256'] and sha(run/'p05-define-state.json')==production['stateSha256']==wrapper['stateSha256'] and production['originalDefines']==state['originalDefines']
  return {'status':'ExactOriginalBytesRestored','originalSha256':sha(original),'finalProjectSettingsSha256':sha(settings),'preservedUnityReserializedBytesSha256':sha(unitybytes),'productionReceiptSha256':sha(run/'p05-restored.json'),'wrapperReceiptSha256':sha(run/'p05-settings-restored.json'),'stateSha256':sha(run/'p05-define-state.json'),'originalDefines':state['originalDefines'],'noReceiptRewrite':True}
 check('original-P05-restoration',restoration,['resource-p05-restore','resource-p05-compile'])
 def integration():
  p=pathlib.Path(config['receiptRoot'])/'integration.json';v=load(p);assert v['kind']=='R03ProductionEntryIntegration' and [r['patchId'] for r in v['patches']]==['P01','P02','P03','P04','P05'] and v['returnChangedRoots']==v['returnClosure']==[] and all(v[k] is False for k in ['runtimeProofExecuted','expansionAuthorized','R03Accepted','H2Passed'])
  for row in v['patches']:
   for k,h in [('patchManifest','patchManifestSha256'),('eligibilityPath','eligibilitySha256')]:assert sha(row[k])==row[h]
   q=load(row['eligibilityPath']);assert q['kind']=='R03PureInterpreterEligibilityV1' and all(q[k] is False for k in ['expansionAuthorized','runtimeProofExecuted','qualificationApproved']) and q['closure']==row['closure'] and q['targetLoadOrder']==row['loadOrder']
  return {'path':str(p),'sha256':sha(p),'patches':v['patches'],'returnChangedRoots':[],'returnClosure':[],'runtimeProofExecuted':False,'expansionAuthorized':False}
 check('production-P01-P05-entry-qualification-agreement',integration,['production-entry-integration'])
 if cells['resource-input-binding']['result']=='Passed':
  phase=lambda n:load(pathlib.Path(config['receiptRoot'])/(n+'.json'))
  try:
   batch.resource_on=pathlib.Path(phase('player-on')['playerReceipt']);batch.resource_off=pathlib.Path(phase('player-off')['playerReceipt']);finalize=phase('finalize');batch.resource_manifest=pathlib.Path(finalize['fixtureManifest']);batch.resource_replay=pathlib.Path(finalize['replayReceipt']);full=verify_graph(batch,config,batch.resource_manifest,batch.resource_on,batch.resource_off,batch.resource_replay);context=full['context'];batch.resource_context=full
   assert context['installed']==cells['resource-input-binding']['evidence']['installed']
   for key in ['on','off']:
    b=context[key];builds.append({'role':'resource-'+key,'receipt':str(b['path']),'receiptSha256':sha(b['path']),'buildGuid':b['player']['buildGuid'],'nativeLibrarySha256':b['player']['nativeLibrarySha256'],'inputSnapshotHash':b['player']['inputSnapshotHash'],'output':str(b['output']),'nativeArguments':b['player']['nativeArguments'],'installedBinding':context['installed'],'fresh':True})
   checks.append({'id':'resource-original-graph-and-six-resource-build-bindings','state':'Passed','evidence':{'profile':full['profile'],'builds':builds,'fixtureManifestSha256':sha(batch.resource_manifest),'editorReplaySha256':sha(batch.resource_replay),'noProbeOrLease':True}})
  except Exception as exc:checks.append({'id':'resource-original-graph-and-six-resource-build-bindings','state':'Failed','error':str(exc)})
 else:checks.append({'id':'resource-original-graph-and-six-resource-build-bindings','state':'NotRun','reason':'Original resource-input-binding not Passed'})
if context:
 def binding(folder,cell_id,expected_exit=0):
  v=load(folder/'verification.json');cmd=load(v['commandReceipt']);assert cells[cell_id]['result']==v['result'] and cells[cell_id].get('evidence')==v and cmd['pid']==v['launchPid'] and cmd['exitCode']==expected_exit
  assert sha(v['commandReceipt'])==v['commandSha256'] and sha(v['console'])==v['consoleSha256'] and pathlib.Path(v['console']).read_bytes()==pathlib.Path(v['commandReceipt']).parent.joinpath('stdout.log').read_bytes()+pathlib.Path(v['commandReceipt']).parent.joinpath('stderr.log').read_bytes()
  for name,h in v['sourceInputHashes'].items():assert sha(name)==h
  return v,cmd
 for mode in sorted(m07.MODES):
  def m07_case(mode=mode):
   folder=R/'resource-players'/mode;v,cmd=binding(folder,'resource-'+mode);p=pathlib.Path(v['rawPath']);assert sha(p)==v['rawSha256'];raw=load(p);assert raw['processId']==cmd['pid'];fresh=verify_current_m07_case(p,context['manifest'],context['baseline'],context['fixtures'],full['baselineResources'],context['on'],context['off'],source_context=full['codecContext']);assert fresh==v['originalContract'];players.append({'group':'M07','case':mode,'pid':cmd['pid'],'raw':str(p),'rawSha256':sha(p),'verificationSha256':sha(folder/'verification.json'),'buildGuid':raw.get('buildGuid'),'state':'Passed'})
   return {'pid':cmd['pid'],'rawSha256':sha(p),'verificationSha256':sha(folder/'verification.json'),'originalContract':fresh}
  check('M07-'+mode,m07_case,['resource-'+mode])
 for mode in r00.MODES:
  for rep in range(3):
   def measurement(mode=mode,rep=rep):
    folder=R/'measurements'/mode/str(rep);v,cmd=binding(folder,'measure-'+mode+'-'+str(rep));raw=load(v['rawPath']);assert sha(v['rawPath'])==v['rawSha256'] and raw['processId']==cmd['pid'];off=mode==r00.OFF_MODE;launch={'resultPath':v['rawPath'],'earlyCapsulePath':'' if off else str(folder/'early.capsule'),'earlyCapsuleSha256':'' if off else sha(folder/'early.capsule'),'earlyResultPath':'' if off else str(folder/'early.json'),'earlyResultSha256':'' if off else sha(folder/'early.json')};fresh=r00.verify_result(raw,mode,context,launch,'R01EarlyStartup',True);assert fresh==v['originalContract'];request=load(folder/'request.json');extra=load(folder/'execution.json');supp=verify_execution(request,extra,raw,sha(folder/'request.json'),sha(v['rawPath']),cmd['pid'],context);assert supp==v['executionSupplement'] and sha(folder/'execution.json')==v['supplementSha256'];players.append({'group':'R00','case':mode+'/'+str(rep),'pid':cmd['pid'],'raw':v['rawPath'],'rawSha256':sha(v['rawPath']),'verificationSha256':sha(folder/'verification.json'),'buildGuid':raw.get('buildGuid'),'state':'Passed','memory':{k:x for k,x in raw.items() if 'memory' in k.lower() or 'bytes' in k.lower()},'operations':fresh['operations'],'supplement':supp})
    return {'pid':cmd['pid'],'rawSha256':sha(v['rawPath']),'supplement':supp,'originalContract':fresh,'measurementIntervalIncludesSupplement':False}
   check('R00-'+mode+'-'+str(rep),measurement,['measure-'+mode+'-'+str(rep)])
 for label,mode,patch in EARLY_CASES:
  def early_case(label=label,mode=mode,patch=patch):
   folder=R/'early'/label;expected_exit=0 if mode in early.POSITIVE_MODES else 1;v,cmd=binding(folder,'early-'+label,expected_exit);assert sha(folder/'early.json')==v['rawSha256'] and sha(folder/'early.capsule')==v['capsuleSha256'];observed=early.verify_early_receipt(folder/'early.json',folder/'early.capsule',mode,cmd['pid'],full['profile']);assert observed['diagnosticProfileComplete'];early.verify_startup_logs(mode,folder/'Player.log',pathlib.Path(v['console']))
   if mode in early.POSITIVE_MODES:
    m07mode='T07-01-Prefab-P01' if patch=='P01' else early.DEFAULT_M07_MODE;rawpath=folder/('m07-'+m07mode+'.json');raw=load(rawpath);assert raw['processId']==cmd['pid'];early.verify_imported_snapshots(observed,raw);verify_current_m07_case(rawpath,context['manifest'],context['baseline'],context['fixtures'],full['baselineResources'],context['on'],context['off'],source_context=full['codecContext'])
   else:assert not list(folder.glob('m07-*.json'))
   players.append({'group':'Early','case':label,'pid':cmd['pid'],'raw':str(folder/'early.json'),'rawSha256':sha(folder/'early.json'),'verificationSha256':sha(folder/'verification.json'),'state':'Passed','expectedExit':expected_exit,'expectedRejection':expected_exit==1});return {'pid':cmd['pid'],'expectedExit':expected_exit,'observed':observed}
  check('Early-'+label,early_case,['early-'+label])
 def measurements():
  original=load(R/'measurements.json');assert original['result']=='Passed' and original['processes']==12 and all(original[k] is False for k in ['noiseOrOverheadThresholdClaimed','releasePerformanceAcceptance','R02DeferredCpuRiskAcceptedHere','H1RssRiskAcceptedHere','R03Accepted','H2Passed'])
  recalculated=[]
  for mode in r00.MODES:
   selected=[load(R/'measurements'/mode/str(rep)/'verification.json') for rep in range(3)]
   for operation in r00.OPERATIONS:
    for phase,_,_ in r00.PHASES:
     values=[v['nanosecondsPerIteration'] for r in selected for v in r['originalContract']['operations'] if v['operation']==operation and v['phase']==phase];assert len(values)==3;recalculated.append({'mode':mode,'operation':operation,'phase':phase,'samples':values,'min':min(values),'median':statistics.median(values),'max':max(values)})
  assert recalculated==original['statistics'];return {'path':str(R/'measurements.json'),'sha256':sha(R/'measurements.json'),'processes':12,'statistics':recalculated,'profile':original['profile'],'releasePerformanceAcceptance':False,'memoryEvidence':original['memoryEvidence']}
 check('unfenced-measurement-distributions',measurements,['measurement-summary'])
commands=[load(p) for p in sorted((R/'commands').glob('*/command.json'))];direct=[c for c in commands if '.app/Contents/MacOS/' in c['command'][0] and not c['command'][0].endswith('/Unity')];assert len({c['pid'] for c in direct})==len(direct)
focused=[load(p) for p in (R/'players').glob('*/verification.json')];pids=[v['launchPid'] for v in focused if 'launchPid' in v]+[v['pid'] for v in players];assert len(pids)==len(set(pids)) and set(pids)<=set(c['pid'] for c in direct)
record={'kind':'ReadOnlyQCompletionSemanticAudit','startUtc':started,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'originalBatchResult':result['result'],'originalCellCounts':dict(collections.Counter(c['result'] for c in cells.values())),'checks':checks,'resourceBuilds':builds,'resourceMeasurementEarlyPlayers':players,'actualDirectPlayerCommands':len(direct),'actualDirectPlayerPids':[c['pid'] for c in direct],'focusedVerificationReceipts':len(focused),'replayedResourceMeasurementEarlyPlayers':len(players),'readOnlyAuditStates':dict(collections.Counter(c['state'] for c in checks)),'allPlannedPlayerEvidenceCovered':len(pids)==len(direct)==59,'limits':'Existing source-bound sealed data only; no Editor/Player launch, source change, restored terminal state, qualification approval, performance SLA or historical state promotion. Failed/Blocked prerequisites remain original states.','R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'pureInterpreterExpansionEnabled':False}
(P/'COMPLETION_RUNTIME_AUDIT.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k not in ['checks','resourceBuilds','resourceMeasurementEarlyPlayers','actualDirectPlayerPids']},indent=2));print('Audit failures',[(c['id'],c.get('error')) for c in checks if c['state']=='Failed'])

# Reproduce original Failed offline contracts without launches or guard changes.
import traceback
reproduced=[]
def failed_call(cell_id,rawpath,fn,precheck=None):
 c=cells[cell_id];assert c['result']=='Failed';raw=load(rawpath);matches=[(p,load(p)) for p in sorted((R/'commands').glob('*/command.json')) if str(rawpath) in load(p)['command']];assert len(matches)==1
 cp,cmd=matches[0];assert raw['processId']==cmd['pid'] and not cmd['remainingProcessGroup'] and not cmd['postCleanupGroupExists']
 rec={'cell':cell_id,'originalState':'Failed','rawPath':str(rawpath),'rawSha256':sha(rawpath),'rawReportedResult':raw.get('result'),'pid':cmd['pid'],'commandReceipt':str(cp),'commandReceiptSha256':sha(cp),'commandExitCode':cmd['exitCode'],'noProductReexecution':True}
 if precheck:rec['independentPrerequisiteContract']=precheck(cmd)
 try:fn(cmd)
 except Exception as exc:
  assert str(exc)==c['error'],(cell_id,str(exc),c['error']);rec.update(offlineReproduction='MatchedOriginalFailure',error=str(exc),traceback=traceback.format_exc())
 else:raise AssertionError(('Original failure unexpectedly did not reproduce',cell_id))
 reproduced.append(rec)
if context:
 for mode in sorted(m07.MODES):
  cell_id='resource-'+mode
  if cells[cell_id]['result']=='Failed':
   rawpath=R/'m07-results'/('m07-'+mode+'.json')
   failed_call(cell_id,rawpath,lambda cmd,p=rawpath:verify_current_m07_case(p,context['manifest'],context['baseline'],context['fixtures'],full['baselineResources'],context['on'],context['off'],source_context=full['codecContext']))
 for mode in r00.MODES:
  for rep in range(3):
   cell_id='measure-'+mode+'-'+str(rep)
   if cells[cell_id]['result']=='Failed':
    folder=R/'measurements'/mode/str(rep);rawpath=folder/(mode+'.json');raw=load(rawpath);off=mode==r00.OFF_MODE
    launch={'resultPath':str(rawpath),'earlyCapsulePath':'' if off else str(folder/'early.capsule'),'earlyCapsuleSha256':'' if off else sha(folder/'early.capsule'),'earlyResultPath':'' if off else str(folder/'early.json'),'earlyResultSha256':'' if off else sha(folder/'early.json')}
    def precheck(cmd,raw=raw,mode=mode,launch=launch):
     value=r00.verify_result(raw,mode,context,launch,'R01EarlyStartup',True);return {'originalR00Contract':'Passed','operationCount':len(value['operations']),'aggregateMeasurementState':'Blocked','supplementAndOverallCellRemain':'Failed','releasePerformanceAcceptance':False}
    failed_call(cell_id,rawpath,lambda cmd,f=folder,p=rawpath,v=raw:verify_execution(load(f/'request.json'),load(f/'execution.json'),v,sha(f/'request.json'),sha(p),cmd['pid'],context),precheck)
 for label,mode,patch in EARLY_CASES:
  cell_id='early-'+label
  if cells[cell_id]['result']=='Failed':
   folder=R/'early'/label;m07mode='T07-01-Prefab-P01' if patch=='P01' else early.DEFAULT_M07_MODE;rawpath=folder/('m07-'+m07mode+'.json')
   def precheck(cmd,folder=folder,mode=mode):
    value=early.verify_early_receipt(folder/'early.json',folder/'early.capsule',mode,cmd['pid'],full['profile']);return {'originalEarlyReceipt':'Passed','diagnosticProfileComplete':value['diagnosticProfileComplete'],'overallCellRemains':'Failed'}
   failed_call(cell_id,rawpath,lambda cmd,p=rawpath:verify_current_m07_case(p,context['manifest'],context['baseline'],context['fixtures'],full['baselineResources'],context['on'],context['off'],source_context=full['codecContext']),precheck)
expected={c['id'] for c in cells.values() if c['result']=='Failed' and c['id']!='production-entry-integration'};assert {v['cell'] for v in reproduced}==expected
(P/'FAILED_CONTRACT_REPRODUCTION.json').write_text(json.dumps({'kind':'ReadOnlyQFailedContractReproduction','cases':reproduced,'allRuntimeFailedCellsCovered':sorted(expected),'noLaunchesOrSourceChanges':True,'sealedReceiptsUnchanged':True,'originalBatchResult':result['result'],'productionFailure':'Original actual Unity exception only; no retry','R03Accepted':False,'H2Passed':False},indent=2)+'\n')
print('Original runtime failures reproduced offline:',len(reproduced))
