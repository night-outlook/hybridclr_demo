"""Read-only LP repair authentication against completed R; never launches products."""
import pathlib,json,datetime,hashlib,sys,types
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=pathlib.Path(__file__).resolve().parent;R=P.parent/'R03LocalBatch-20261007R-lq-storage'
sys.path[:0]=[str(D/'Tools/AssemblyShadow/R03Completion'),str(D/'Tools/AssemblyShadow/R03'),str(D/'Tools/AssemblyShadow/R02'),str(D/'Tools/AssemblyShadow')]
import fixture_authority,m07_results as m07,r01_early_results as early
from fixture_authority import verify_graph
from type_resolution_schema import current_m07_schema,legacy_projection,loads
from legacy_runtime import EARLY_CASES
load=lambda p:json.loads(pathlib.Path(p).read_text())
def sha(p):
 with pathlib.Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
result=load(R/'LOCAL_BATCH_RESULT.json');cells={c['id']:c for c in result['cells']};index={f['path']:f for f in load(R/'evidence-index.json')['files']}
def bound(p):
 p=pathlib.Path(p);item=index[str(p.relative_to(R))];assert sha(p)==item['sha256'] and p.stat().st_size==item['size'];return {'path':str(p),'sha256':item['sha256']}
def unchanged(path,value):assert pathlib.Path(path)==R/'native-codec-source-verification.json' and load(path)==value
fixture_authority.write=unchanged
record={'kind':'ReadOnlyRLPRepairAudit','startedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':[],'productReexecution':False,'rawEvidenceModified':False,'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'expansionAuthorized':False}
def check(name,fn,deps=()):
 blocked=[c for c in deps if cells[c]['result']!='Passed']
 if blocked:record['checks'].append({'id':name,'state':'NotRun','originalPrerequisites':{c:cells[c]['result'] for c in blocked}});return
 try:value=fn()
 except Exception as e:record['checks'].append({'id':name,'state':'Failed','error':str(e)})
 else:record['checks'].append({'id':name,'state':'Passed','evidence':value})
ids=[c['id'] for c in result['cells']]
def order():
 plan=load(R/'completion-plan.json');assert plan['cells']==ids and len(ids)==90
 a=ids.index('resource-input-binding');b=ids.index('production-entry-integration');assert a<b and cells['production-entry-integration']['dependencies']==['resource-input-binding']
 return {'bindingPosition':a,'integrationPosition':b,'dependencies':cells['production-entry-integration']['dependencies'],'binding':bound(R/'cells/resource-input-binding.json'),'integration':bound(R/'cells/production-entry-integration.json'),'bindingOriginalState':cells['resource-input-binding']['result'],'integrationOriginalState':cells['production-entry-integration']['result']}
check('LP-001-actual-ledger-order-and-dependency',order)
if cells['resource-input-binding']['result']=='Passed':
 cfg=load(R/'resource-project.json');root=pathlib.Path(cfg['receiptRoot']);phase=lambda n:load(root/(n+'.json'));fin=phase('finalize');batch=types.SimpleNamespace(root=R,workspace=W,pins=result['repositories'],resource_config=cfg)
 full=verify_graph(batch,cfg,pathlib.Path(fin['fixtureManifest']),pathlib.Path(phase('player-on')['playerReceipt']),pathlib.Path(phase('player-off')['playerReceipt']),pathlib.Path(fin['replayReceipt']));context=full['context']
 def strict_check(rawpath,fn,expected):
  before=sha(rawpath);raw=loads(pathlib.Path(rawpath).read_text());rows=raw['typeResolutions'];assert len(rows)==expected
  for i,row in enumerate(rows):legacy_projection(loads(row['rawJson']),str(rawpath)+'.typeResolutions['+str(i)+']')
  callback=m07.verify_type_resolutions
  try:
   with current_m07_schema() as bridge:value=fn()
  finally:assert m07.verify_type_resolutions is callback
  assert sha(rawpath)==before and bridge=={'kind':'R02StrictM07TypeInfoBridge','schemaVersion':1,'profile':2,'verifiedTypeInfoObjects':expected,'rawEvidenceModified':False}
  binding=bound(rawpath);binding.update(rawSha256BeforeReadOnlyVerification=before,rawSha256AfterReadOnlyVerification=sha(rawpath),comparisonScope='Postrun strict semantic recheck; original sealed hashes remain independent')
  return value,bridge,binding
 for mode in sorted(m07.MODES):
  def case(mode=mode):
   v=load(R/'resource-players'/mode/'verification.json');raw=pathlib.Path(v['rawPath']);patch=m07.MODE_PATCH[mode];count=17 if patch else 0
   if patch:value,bridge,binding=strict_check(raw,lambda:m07.verify_case(raw,context['manifest'],context['baseline'],context['fixtures'],full['baselineResources'],context['on'],context['off'],source_context=full['codecContext']),count)
   else:
    before=sha(raw);callback=m07.verify_type_resolutions
    with current_m07_schema() as bridge:value=m07.verify_case(raw,context['manifest'],context['baseline'],context['fixtures'],full['baselineResources'],context['on'],context['off'],source_context=full['codecContext'])
    assert m07.verify_type_resolutions is callback and sha(raw)==before;binding=bound(raw);binding.update(rawSha256BeforeReadOnlyVerification=before,rawSha256AfterReadOnlyVerification=sha(raw))
   assert value==v['originalContract'] and bridge==v['typeInfoBridge'] and bridge['verifiedTypeInfoObjects']==count and bridge['rawEvidenceModified'] is False
   return {'raw':binding,'bridge':bridge,'originalVerification':bound(R/'resource-players'/mode/'verification.json'),'callbackRestored':True,'fullOriginalContractRechecked':True}
  check('LP-002-resource-'+mode,case,['resource-'+mode])
 for label,mode,patch in EARLY_CASES:
  def startup(label=label,mode=mode,patch=patch):
   folder=R/'early'/label;v=load(folder/'verification.json')
   if mode in early.POSITIVE_MODES:
    m07mode='T07-01-Prefab-P01' if patch=='P01' else early.DEFAULT_M07_MODE;raw=folder/('m07-'+m07mode+'.json');_,bridge,binding=strict_check(raw,lambda:m07.verify_case(raw,context['manifest'],context['baseline'],context['fixtures'],full['baselineResources'],context['on'],context['off'],source_context=full['codecContext']),17);assert bridge==v['typeInfoBridge'];return {'raw':binding,'bridge':bridge,'callbackRestored':True,'businessResourceContractRechecked':True}
   assert v['typeInfoBridge'] is None and not list(folder.glob('m07-*.json')) and v['expectedRejection'] is True and v['originalExit']==1
   return {'verification':bound(folder/'verification.json'),'typeInfoBridge':None,'businessResourceExecution':False,'expectedRejection':True}
  check('LP-002-startup-'+label,startup,['early-'+label])
 def aggregate():
  path=R/'resource-contracts.json';v=load(path);callback=m07.verify_type_resolutions;rawPaths=[R/'m07-results'/('m07-'+mode+'.json') for mode in m07.MODES];diagnosticPaths=[R/'m07-results'/('m07-'+mode+'-diagnostics.json') for mode in m07.MODES];assert len(rawPaths)==len(diagnosticPaths)==14 and set((R/'m07-results').glob('*.json'))==set(rawPaths+diagnosticPaths);raws={p:sha(p) for p in rawPaths+diagnosticPaths};assert all(bound(p)['sha256']==h for p,h in raws.items())
  with current_m07_schema() as bridge:value=m07.verify_suite(pathlib.Path(fin['fixtureManifest']),R/'m07-results',pathlib.Path(phase('player-on')['playerReceipt']),pathlib.Path(phase('player-off')['playerReceipt']),allow_incomplete=False,replay_receipt=pathlib.Path(fin['replayReceipt']),source_context=full['codecContext'])
  assert m07.verify_type_resolutions is callback and all(sha(p)==h for p,h in raws.items()) and bridge==v['typeInfoBridge'] and bridge['verifiedTypeInfoObjects']==221 and bridge['rawEvidenceModified'] is False and value==v['originalVerifierOutput'] and value['resultPassed'] is True and len(value['modes'])==14
  return {'originalReceipt':bound(path),'bridge':bridge,'modes':14,'rawFilesUnchanged':len(raws),'resultFiles':len(rawPaths),'diagnosticFiles':len(diagnosticPaths),'rawHashesBeforeAndAfterReadOnlyVerification':[{'path':str(p),'before':h,'after':sha(p)} for p,h in raws.items()],'callbackRestored':True,'fullOriginalSuiteRechecked':True}
 check('LP-002-complete-resource-aggregate',aggregate,['resource-contracts'])
record['endedUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();record['originalBatchResult']=result['result'];(P/'LP_REPAIR_AUDIT.json').write_text(json.dumps(record,indent=2)+'\n');print([(x['id'],x['state']) for x in record['checks']])
