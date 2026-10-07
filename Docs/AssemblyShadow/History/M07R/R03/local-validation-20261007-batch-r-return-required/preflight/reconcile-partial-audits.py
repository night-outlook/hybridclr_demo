"""Read-only partial-batch audit; preserve initial auditor failures and original verdicts."""
from pathlib import Path
import hashlib,json,datetime,sys,types,subprocess,collections,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent;B=P.parent/'R03LocalBatch-20261007R-lq-storage';W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';S=P.parent/'Storage-R03LocalBatch-20261007R-lq-storage'
sys.path[:0]=[str(D/'Tools/AssemblyShadow/R03Completion'),str(D/'Tools/AssemblyShadow/R03')]
from fixture_contracts import roster,verify_editor
from source_pin_contract import CODES,validate_document,INPUTS
from fixture_authority import verify_native_inventory
from resource_capabilities import CODES as CAP_CODES
from fixture_project import source_catalog

def load(p):return json.loads(Path(p).read_text())
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(n,o):
 with (P/n).open('x') as f:json.dump(o,f,indent=2);f.write('\n')
start=utc();result=load(B/'LOCAL_BATCH_RESULT.json');cells={c['id']:c for c in result['cells']};cfg=load(B/'resource-project.json');project=Path(cfg['projectPath']);run=Path(cfg['runPath']);receipts=Path(cfg['receiptRoot']);batch=types.SimpleNamespace(root=B,workspace=W,pins=result['repositories']);checks=[]
state=load(run/'p05-define-state.json');settings=project/'ProjectSettings/ProjectSettings.asset';original=run/'p05-project-settings.original';assert sha(original)==state['originalSettingsSha256'];text=settings.read_text();assert 'ASSEMBLY_SHADOW_P05' in text and sha(settings)!=sha(original)
missing=[str(p) for p in [run/'p05-restored.json',run/'p05-settings-restored.json',run/'p05-unity-restored.bytes',receipts/'restore.json',B/'resource-logs/restore.log'] if not p.exists()];assert len(missing)==5
assert cells['resource-p05-compile']['result']=='Passed' and cells['resource-p05-restore']['error']=='Git command failed: ls-remote origin'
restore={'cell':'resource-p05-restore','originalResult':'Failed','failureUtc':'2026-10-07T15:19:22.695541+00:00','error':cells['resource-p05-restore']['error'],'failureReceipt':str(S/'failure-000689.json'),'failureReceiptSha256':sha(S/'failure-000689.json'),'originalSettingsPath':str(original),'originalSettingsSha256':sha(original),'currentStagedSettingsPath':str(settings),'currentStagedSettingsSha256':sha(settings),'stagedDefines':state['stagedDefines'],'originalDefines':state['originalDefines'],'missingRestorationEvidence':missing,'liveRootRetainedUnmodified':True,'restoreCoverage':'Unavailable','originalGitStderrExitRepositoryAndArgv':'Unavailable: helper discarded details','cause':'Remote-authority subprocess returned nonzero before StructuralRestore launch; exact transport cause cannot be recovered','recommendation':'Preserve strict exact remote pins while recording bounded Git command path/argv/exit/stdout/stderr/timestamps. Separate safe local transaction recovery from fresh remote acceptance; preserve this staged project before any recovery. Require a fresh authorized batch/root, no retry here.'}
save('P05_RESTORE_FAILURE_ANALYSIS.json',{'startUtc':start,'endUtc':utc(),**restore})
# Constructor and production source-pin consumer: actual early XML, ten controls, immutable original source settings.
host=load(B/'fixture-constructor-host/results.json');assert host['result']=='Passed' and len(host['cases'])==12 and host['failures']==0
early=B/'fixture-constructor-editor';fresh=verify_editor(ET.parse(early/'results.xml').getroot(),roster());v=load(early/'verification.json');assert all(v[k]==x for k,x in fresh.items());assert load(early/'scope.json')['names']==roster() and v['xmlSha256']==sha(early/'results.xml')
report=load(receipts/'source-pin-contract.json');assert report['result']=='Passed' and report['before']==report['after'] and len(report['cases'])==10 and {c['id'] for c in report['cases']}==set(CODES);validate_document(load(project/INPUTS[0]),batch,project)
for c in report['cases']:assert c['result']=='Passed' and c['observedCode']==c['expectedCode']==CODES[c['id']] and sha(c['path'])==c['sha256']
sourceSettings=[]
for row in report['before']:
 rel=row['path'];blob=subprocess.check_output(['git','-C',str(D),'show',result['repositories']['hybridclr_demo']+':'+rel]) if rel in ['ProjectSettings/ProjectSettings.asset','ProjectSettings/AssemblyShadowSettings.asset'] else (project/rel).read_bytes();assert hashlib.sha256(blob).hexdigest()==row['sha256'];sourceSettings.append({'path':rel,'originalPreflightSha256':row['sha256'],'currentSha256':sha(project/rel),'laterConfiguredOrStaged':sha(project/rel)!=row['sha256']})
checks.append({'id':'LI-constructor-source-pin-preflights','state':'Passed','hostCases':12,'actualEarlyEditorCases':18,'actualSourcePinConsumerCases':10,'inputs':sourceSettings,'xmlSha256':sha(early/'results.xml')})
# Exact native source binding of BOTH completed resource builds, independent of current staged settings.
pins=load(project/'ProjectSettings/AssemblyShadowSourcePins.json');paths={k:W/n for k,n in zip(('demo','hybridclr','hybridclrUnity','il2cppPlus'),('hybridclr_demo','hybridclr','hybridclr_unity','il2cpp_plus'))};native=verify_native_inventory(project/'HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp',pins,paths);builds=[]
for phase in ['player-on','player-off']:
 r=load(receipts/(phase+'.json'));path=Path(r['playerReceipt']);assert sha(path)==r['playerReceiptSha256'];player=load(path);cmd=load(B/'cells'/('resource-'+phase+'.json'));assert cmd['result']=='Passed';builds.append({'role':phase,'receiptPath':str(path),'sha256':sha(path),'buildGuid':player.get('buildGuid'),'result':'Passed','originalCellSha256':sha(B/'cells'/('resource-'+phase+'.json'))})
checks.append({'id':'Resource-ON-OFF-native-source-binding','state':'Passed','builds':builds,'installedNativeBinding':native})
# Capability consumer actual proof: current project was intentionally staged after preflight.
cap=load(receipts/'capability-contract.json');cv=load(B/'capability-contract-verification.json');assert cap['result']=='Passed' and cv['sha256']==sha(receipts/'capability-contract.json');assert len(cap['cases'])==10
for c in cap['cases']:assert c['result']=='Passed' and sha(c['path'])==c['sha256']
checks.append({'id':'Capability-consumer-execution','state':'Passed','cases':10,'originalReportSha256':sha(receipts/'capability-contract.json'),'originalVerificationSha256':sha(B/'capability-contract-verification.json'),'postrunFullCurrentInputRevalidation':'Unavailable: exact restoration prerequisite failed; initial auditor Policy consumer changed input retained, not relabeled'})
checks.append({'id':'Resource-full-755-Editor','state':'NotRun','originalCellResult':cells['resource-editor']['result'],'reason':'resource-p05-restore Failed; no XML exists'});assert not(B/'resource-editor/results.xml').exists()
checks.append({'id':'P05-exact-restore-finalization','state':'Unavailable','originalRestoreResult':'Failed','originalFinalizeResult':cells['resource-p05-finalize']['result'],'analysis':restore})
checks.append({'id':'Resource-live-policy-restored-baseline-bridge-Player-integration','state':'NotRun','reason':'Original input-binding/integration and 36 resource/measurement/startup Player cells Blocked'})
checks.append({'id':'Original-failure-offline-reproduction','state':'Unavailable','reason':'No original Git stderr, exit code, complete argv or failed repository captured; online reexecution cannot establish original cause','noGitPhaseRetry':True})
save('PARTIAL_BATCH_RECONCILIATION.json',{'kind':'ReadOnlyPartialBatchReconciliation','startUtc':start,'endUtc':utc(),'originalResult':result['result'],'originalCounts':dict(collections.Counter(c['result'] for c in cells.values())),'checks':checks,'initialAuditorErrorsPreserved':True,'productReexecution':False,'sourceOrRetainedSettingsModified':False,'acceptanceFlagsChanged':False})
print('Partial reconciliation complete',len(checks),'checks; original failure remains Failed')
