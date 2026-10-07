"""Read-only LI repair evidence authentication after the single sealed O run."""
import pathlib,json,hashlib,datetime,sys,types,xml.etree.ElementTree as ET
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261007R-lq-storage-2';R=P.parent/'R03LocalBatch-20261007R-lq-storage';sys.path[:0]=[str(D/'Tools/AssemblyShadow/R03Completion'),str(D/'Tools/AssemblyShadow/R03')]
import os
os.environ['GIT_SSH_COMMAND']=json.loads((P/'SSH_TRANSPORT.json').read_text())['command']
from fixture_contracts import roster,verify_editor
from source_pin_contract import CODES,INPUTS,validate_document
from fixture_authority import verify_installation
load=lambda p:json.loads(pathlib.Path(p).read_text())
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
start=datetime.datetime.now(datetime.timezone.utc).isoformat();result=load(R/'LOCAL_BATCH_RESULT.json');cells={c['id']:c for c in result['cells']};config=load(R/'resource-project.json');project=pathlib.Path(config['projectPath']);batch=types.SimpleNamespace(workspace=W,root=R,pins=result['repositories'],resource_config=config)
host=load(R/'fixture-constructor-host/results.json');assert host['result']=='Passed' and len(host['cases'])==12 and host['failures']==0 and host['originalFourArgumentException']=='TargetParameterCountException';assert all(host[k] is False for k in ['unityEditorRun','acquisitionPolicyAssertionsExecuted','qualificationAuthorized','expansionAuthorized'])
early=R/'fixture-constructor-editor';v=load(early/'verification.json');scope=load(early/'scope.json');fresh=verify_editor(ET.parse(early/'results.xml').getroot(),roster());assert all(v[k]==x for k,x in fresh.items()) and scope['names']==roster() and scope['packageRevision']==result['repositories']['hybridclr_unity'] and v['scopeSha256']==sha(early/'scope.json') and v['xmlSha256']==sha(early/'results.xml')
cmd=v['command'];assert sha(cmd['outerReceipt'])==cmd['outerSha256'] and sha(cmd['completion'])==cmd['completionSha256'] and load(cmd['completion'])['commandExitCode']==0 and cmd['clean'] is True
reportPath=pathlib.Path(config['receiptRoot'])/'source-pin-contract.json';report=load(reportPath);verification=load(R/'source-pin-contract-verification.json');assert report['result']=='Passed' and verification['sha256']==sha(reportPath) and report['consumer']=='HybridCLR.Editor.AssemblyShadow.ShadowSourcePins.Read' and report['serialization']=='UnityEngine.JsonUtility' and report['unityEditorRun'] is True and report['nativeInstallationRun'] is False and report['before']==report['after'];assert len(report['cases'])==10 and {c['id'] for c in report['cases']}==set(CODES);validate_document(load(project/INPUTS[0]),batch,project)
for case in report['cases']:
 assert case['result']=='Passed' and case['observedCode']==case['expectedCode']==CODES[case['id']] and sha(case['path'])==case['sha256']
 assert pathlib.Path(case['path'])==project/INPUTS[0] if case['id']=='generated' else pathlib.Path(case['path']).parent==reportPath.parent/'source-pin-contract-inputs'
initial={x['path'].split('/hybridclr_demo/',1)[1]:x for x in load(P/'pre-install-source-settings.json')['files'] if x['path'].split('/hybridclr_demo/',1)[1] in ['ProjectSettings/ProjectSettings.asset','ProjectSettings/AssemblyShadowSettings.asset']};bound=[]
for item in report['before']:
 path=item['path'];current=project/path
 original=pathlib.Path(initial[path]['copy']) if path in initial else current
 assert sha(original)==item['sha256']
 bound.append({'path':path,'preflightBeforeAfterSha256':item['sha256'],'originalBytesBinding':str(original),'currentPostInstallSha256':sha(current),'changedLaterByAuthorizedConfigure':sha(current)!=item['sha256'],'limitation':'Later configured bytes do not retroactively change preflight input hashes'})
proof=verification['command'];assert sha(proof['outerReceipt'])==proof['outerSha256'] and sha(proof['completion'])==proof['completionSha256'] and load(proof['completion'])['commandExitCode']==0 and proof['clean'] is True
native=verify_installation(batch,config);assert cells['resource-install']['result']=='Passed';editors=[]
for folder,count in [('focused-editor',754),('resource-editor',755)]:
 if not(R/folder/'results.xml').exists():
  cell=cells['editor-tests' if folder=='focused-editor' else 'resource-editor'];assert cell['result']=='Failed' and cell['error']=='Review any additional package change before selecting Editor tests' and not(R/folder).exists()
  editors.append({'folder':folder,'expectedCount':count,'count':0,'state':'Failed','execution':'NotRun','xmlState':'Unavailable','error':cell['error']});continue
 tree=ET.parse(R/folder/'results.xml').getroot();xmlcases=list(tree.iter('test-case'));assert len(xmlcases)==count and tree.get('passed')==str(count) and all(tree.get(k)=='0' for k in ['failed','skipped','inconclusive']);assert all(c.get('result')=='Passed' for c in xmlcases) and set(roster())<=set(c.get('fullname') for c in xmlcases);editors.append({'folder':folder,'count':count,'allEighteenAffectedMethodsPassed':True,'xmlSha256':sha(R/folder/'results.xml')})
record={'kind':'ReadOnlyQLIContractAudit','startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'Passed','hostConstructorCases':12,'earlyActualEditorCases':18,'hostResultSha256':sha(R/'fixture-constructor-host/results.json'),'earlyXmlSha256':sha(early/'results.xml'),'earlyVerificationSha256':sha(early/'verification.json'),'actualConsumerCases':10,'consumerReportPath':str(reportPath),'consumerReportSha256':sha(reportPath),'consumerCodes':CODES,'unchangedPreflightInputs':bound,'installedResourceNativeBinding':native,'fullEditors':editors,'interpretation':'Fresh Q constructor/source-pin regression; downstream states recorded separately. Native installation is not a Player build.','R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'pureInterpreterExpansionEnabled':False}
(P/'LI_CONTRACT_AUDIT.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k not in ['installedResourceNativeBinding','consumerCodes','unchangedPreflightInputs']},indent=2))
