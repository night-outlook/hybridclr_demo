"""Read-only actual target/profile evidence authentication; never invokes Unity."""
import pathlib,json,hashlib,datetime,sys,types,collections
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261006Q-lp-repair';R=P.parent/'R03LocalBatch-20261006Q-lp-repair'
sys.path[:0]=[str(D/'Tools/AssemblyShadow/R03Completion'),str(D/'Tools/AssemblyShadow/R03')]
from resource_capabilities import verify_report,CODES,INCLUDED,EXCLUDED
load=lambda p:json.loads(pathlib.Path(p).read_text());sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
started=datetime.datetime.now(datetime.timezone.utc).isoformat();result=load(R/'LOCAL_BATCH_RESULT.json');cfg=load(R/'resource-project.json');project=pathlib.Path(cfg['projectPath']);batch=types.SimpleNamespace(root=R,resource_config=cfg,workspace=W,pins=result['repositories'],unity='/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity')
host=load(R/'capability-profile-host/results.json');assert host['result']=='Passed' and len(host['cases'])==20 and all(c['result']=='Passed' for c in host['cases']) and host['unityEditorRun'] is False and host['runtimeAcceptance'] is False
path=pathlib.Path(cfg['receiptRoot'])/'capability-contract.json';record={'kind':'ReadOnlyQCapabilityContractAudit','startUtc':started,'hostCases':20,'hostSha256':sha(R/'capability-profile-host/results.json'),'scope':'Actual target preflight only; compiler/build/Player states separate','R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'pureInterpreterExpansionEnabled':False}
if path.exists():
 report=load(path);record.update(reportPath=str(path),reportSha256=sha(path),originalReceiptResult=report['result'])
 if report['result']=='Passed':
  verdict=verify_report(path,batch,project);verification=load(R/'capability-contract-verification.json');assert verification['sha256']==sha(path) and all(verification[k]==v for k,v in verdict.items());proof=verification['command'];assert sha(proof['outerReceipt'])==proof['outerSha256'] and sha(proof['completion'])==proof['completionSha256'];assert load(proof['outerReceipt'])['exitCode']==0 and load(proof['completion'])['completion']['clean'] is True
  record.update(status='Passed',inventoryRows=len(report['inventory']),referenceFiles=len(report['referenceFiles']),compilerAssembliesByMode=dict(collections.Counter(r['mode'] for r in report['compilerAssemblies'])),declarations=report['declarations'],cases=report['cases'],unchangedConfiguredInputs=report['before']==report['after'],policySha256=hashlib.sha256(report['policyJson'].encode()).hexdigest(),verificationSha256=sha(R/'capability-contract-verification.json'),verdict=verdict)
 else:record.update(status='Failed',availableReceipt=report,independentReplay='NotRun: original actual policy prerequisite Failed')
else:record.update(status='Unavailable',reason='Actual target report was not emitted; not an empty passing inventory')
record['endUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(P/'CAPABILITY_CONTRACT_AUDIT.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k not in ['availableReceipt','cases','verdict','declarations']},indent=2))
