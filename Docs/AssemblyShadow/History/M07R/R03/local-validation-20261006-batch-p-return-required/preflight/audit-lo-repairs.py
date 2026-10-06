"""Read-only authentication of fresh batch-P LO repair evidence, no product launches."""
import pathlib,json,hashlib,datetime,sys,types
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo'
P=pathlib.Path(__file__).resolve().parent;R=P.parent/'R03LocalBatch-20261006P-lo-repair'
sys.path[:0]=[str(D/'Tools/AssemblyShadow/R03Completion'),str(D/'Tools/AssemblyShadow/R03'),str(D/'Tools/AssemblyShadow')]
import policy_domains,fixture_authority,execution_contract
from fixture_authority import verify_graph
load=lambda p:json.loads(pathlib.Path(p).read_text())
def sha(p):
 with pathlib.Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
result=load(R/'LOCAL_BATCH_RESULT.json');cells={c['id']:c for c in result['cells']}
index={f['path']:f for f in load(R/'evidence-index.json')['files']}
def bound(p):
 p=pathlib.Path(p);e=index[str(p.relative_to(R))];assert p.stat().st_size==e['size'] and sha(p)==e['sha256'];return {'path':str(p),'sha256':e['sha256'],'size':e['size']}
def existing(path,value):
 assert pathlib.Path(path)==R/'native-codec-source-verification.json' and load(path)==value
fixture_authority.write=existing
record={'kind':'ReadOnlyPLORepairAudit','startedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':[],'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'expansionAuthorized':False,'productReexecution':False}
cfg=load(R/'resource-project.json');root=pathlib.Path(cfg['receiptRoot']);project=pathlib.Path(cfg['projectPath'])
batch=types.SimpleNamespace(root=R,workspace=W,pins=result['repositories'],resource_config=cfg)
if cells['resource-input-binding']['result']=='Passed':
 phase=lambda n:load(root/(n+'.json'))
 final=phase('finalize');full=verify_graph(batch,cfg,pathlib.Path(final['fixtureManifest']),pathlib.Path(phase('player-on')['playerReceipt']),pathlib.Path(phase('player-off')['playerReceipt']),pathlib.Path(final['replayReceipt']));context=full['context']
 def check(name,fn,original):
  try:value=fn()
  except Exception as e:record['checks'].append({'id':name,'subproofState':'Failed','error':str(e),'originalCells':{n:cells[n]['result'] for n in original}})
  else:record['checks'].append({'id':name,'subproofState':'Passed','evidence':value,'originalCells':{n:cells[n]['result'] for n in original}})
 def domains():
  f=root/'compiler-policy-domains.json';value=policy_domains.verify_live(f,project,root,context['on']['snapshot']['snapshotHash']);report=load(f)
  return {'originalVerifier':value,'report':bound(f),'sourcePolicy':bound(report['sourcePolicyPath']),'linkedPolicy':bound(report['linkedPolicyPath']),'linkedPolicyDiagnostics':report['linkedPolicyDiagnostics'],'sourceDiagnostics':report['sourceDiagnostics'],'guardProviders':report['guardProviders'],'project':str(project),'baselineSnapshotHash':report['baselineSnapshotHash']}
 check('LO-001-live-policy-domains',domains,['production-entry-integration'])
 def integrated():
  p=root/'integration.json';v=load(p);assert v['kind']=='R03ProductionEntryIntegration' and v['returnChangedRoots']==v['returnClosure']==[] and [r['patchId'] for r in v['patches']]==['P01','P02','P03','P04','P05']
  assert sha(v['policyDomainsPath'])==v['policyDomainsSha256'];rows=[]
  for row in v['patches']:
   q=load(row['eligibilityPath']);assert q['closure']==row['closure'] and q['targetLoadOrder']==row['loadOrder'] and not any(q[k] for k in ['expansionAuthorized','qualificationApproved','runtimeProofExecuted'])
   assert sha(row['patchManifest'])==row['patchManifestSha256'] and sha(row['eligibilityPath'])==row['eligibilitySha256'];rows.append({'patchId':row['patchId'],'manifest':bound(row['patchManifest']),'qualification':bound(row['eligibilityPath'])})
  return {'integration':bound(p),'patches':rows,'returnChangedRoots':[],'returnClosure':[],'subproofDoesNotPromoteFailedOrchestration':True}
 check('LO-001-restored-baseline-integration',integrated,['production-entry-integration'])
 affected=[n for n in cells if n.startswith('resource-T07-') and n!='resource-T07-14-OFF']+[n for n in cells if n.startswith('early-') and load(R/'cells'/(n+'.json')).get('evidence',{}).get('mode') in ('Control','ShadowPreload','PatchPreload')]
 # Positive startup modes are authoritative from the unchanged original case table.
 from legacy_runtime import EARLY_CASES
 import r01_early_results as early
 affected=[n for n in cells if n.startswith('resource-T07-') and 'OFF' not in n]+['early-'+label for label,mode,patch in EARLY_CASES if mode in early.POSITIVE_MODES]
 record['checks'].append({'id':'LO-002-end-to-end-codec-consumers','subproofState':'Passed' if len(affected)==17 and all(cells[n]['result']=='Passed' for n in affected) else 'Failed','originalCells':{n:cells[n]['result'] for n in affected},'authenticatedCodecContext':bound(R/'native-codec-source-verification.json'),'context':load(R/'native-codec-source-verification.json'),'independentOriginalVerifiers':'COMPLETION_RUNTIME_AUDIT.json'})
 for group,modes in [('LO-003-linked-baseline-lookup',['R00-ON-NoPatch','R00-OFF-NoPatch']),('LO-004-image-record-consumer',['R00-ON-P01','R00-ON-P03'])]:
  def images(modes=modes):
   rows=[]
   for mode in modes:
    image=execution_contract.selected_image(context,mode);assert isinstance(image,dict) and isinstance(image['methods'],list) and image['identity']['name']=='AssemblyA.Implementation.Internal';rows.append({'mode':mode,'physicalIdentity':image['identity'],'methodCount':len(image['methods']),'pdbAvailable':image['pdbAvailable'],'consumerSchema':'Complete image record'})
   for mode in modes:
    for rep in range(3):
     p=R/'measurements'/mode/str(rep)/'verification.json';v=load(p);assert v['result']=='Passed' and v['executionSupplement']['result']=='Passed';bound(p)
   return {'images':rows,'actualMeasurementCells':6,'originalConsumerRules':'Unchanged original M06 business/exception/PDB rules','independentOriginalVerifiers':'COMPLETION_RUNTIME_AUDIT.json'}
  check(group,images,['measure-'+mode+'-'+str(rep) for mode in modes for rep in range(3)])
else:record['checks'].append({'id':'LO-repair-evidence','subproofState':'NotRun','reason':'Original resource-input-binding not Passed'})
record['endedUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();record['originalProductionCell']=cells['production-entry-integration'];(P/'LO_REPAIR_AUDIT.json').write_text(json.dumps(record,indent=2)+'\n');print([(r['id'],r['subproofState']) for r in record['checks']])
