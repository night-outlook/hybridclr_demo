"""Authenticate P's four repaired boundaries from existing evidence only."""
import pathlib,json,hashlib,datetime,sys
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261007R-lq-storage-2';R=P.parent/'R03LocalBatch-20261007R-lq-storage'
sys.path[:0]=[str(D/'Tools/AssemblyShadow/R03Completion'),str(D/'Tools/AssemblyShadow/R03'),str(D/'Tools/AssemblyShadow')]
import reference_binding,editor_contract
from native_codec_source import read_codec,CodecSourceContext
load=lambda p:json.loads(pathlib.Path(p).read_text())
def sha(p):
 with pathlib.Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
start=datetime.datetime.now(datetime.timezone.utc).isoformat();result=load(R/'LOCAL_BATCH_RESULT.json');cells={c['id']:c for c in result['cells']};index={f['path']:f for f in load(R/'evidence-index.json')['files']}
def bound(p):
 p=pathlib.Path(p);assert p.is_relative_to(R);entry=index[str(p.relative_to(R))];assert p.is_file() and not p.is_symlink() and p.stat().st_size==entry['size'] and sha(p)==entry['sha256'];return {'path':str(p),'sha256':entry['sha256'],'size':entry['size'],'indexed':True}
record={'kind':'ReadOnlyQBoundaryRepairAudit','startUtc':start,'checks':[],'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'expansionAuthorized':False,'newUnityCompilerPlayerExecution':False}
root=R/'editor-source-scope'
if root.exists():
 for f in sorted(root.rglob('*.json')):bound(f)
 scopeReport=load(root/'results.json');assert scopeReport['result']=='Passed' and scopeReport['packageRevision']==result['repositories']['hybridclr_unity'] and scopeReport['counts']==[754,755] and scopeReport['editorExecution']=='NotRun' and scopeReport['catalogUse']=='NamesOnly';assert len(scopeReport['reviewedPackageDelta'])==13 and set(scopeReport['reviewedPackageDelta'])==editor_contract.REVIEWED_PACKAGE_FILES
 for label,full,count in [('focused',False,754),('resource',True,755)]:
  actual=load(root/(label+'-scope.json'));fresh=editor_contract.source_scope(D,W/'hybridclr_unity',result['repositories']['hybridclr_unity'],scopeReport['requiredIds'],resource_complete=full);assert actual==fresh and len(actual['expectedNames'])==count
 bound(root/'name-catalog.xml');record['checks'].append({'id':'LN-001-source-scope','state':'Passed','files':[bound(f) for f in sorted(root.rglob('*.json'))],'reviewedPackageFiles':13,'expectedCatalogs':[754,755],'sourceGuardRecheck':'Actual pinned Git delta and exact catalog bindings','fullTestRunnerExecution':'See LI_CONTRACT_AUDIT and COMPLETION_RUNTIME_AUDIT; source-scope verdict is not an XML test verdict'})
else:record['checks'].append({'id':'LN-001-source-scope','state':'Unavailable','originalCell':cells['completion-tool-contracts']['result']})
path=R/'reference-binding/results.json'
if path.exists():
 inputs=load(R/'reference-binding-inputs.json');v=load(path);bound(path);bound(R/'reference-binding-inputs.json')
 if v['result']=='Passed':
  verdict=reference_binding.verify_results(R/'reference-binding',inputs);cases=[]
  for row in v['caseReceipts']:
   f=R/'reference-binding'/row['path'];d=load(f);assert d['selection']==row['id'] and d['result']=='Passed';casepath=f.parent/'case-result.json';assert load(casepath)==d['cases'][0];cases.append({'id':row['id'],'receipt':bound(f),'caseResult':bound(casepath),'elapsedMilliseconds':d['cases'][0]['elapsedMilliseconds']})
  diagnosis=load(R/'reference-binding/reference-context-diagnosis.json');record['checks'].append({'id':'LN-002-reference-controls','state':'Passed','cases':cases,'freshSupervisedCases':15,'verdict':verdict,'diagnosis':bound(R/'reference-binding/reference-context-diagnosis.json'),'semanticDifferences':diagnosis['differences'],'historicalInputBasis':inputs['basis'],'historicalNQualification':'Failed unchanged','freshProductionQualificationCell':cells['production-entry-integration']['result']})
 else:record['checks'].append({'id':'LN-002-reference-controls','state':'Failed','result':v,'resultReceipt':bound(path)})
else:record['checks'].append({'id':'LN-002-reference-controls','state':'Unavailable','originalCell':cells['completion-tool-contracts']['result']})
path=R/'native-codec-source-verification.json'
if path.exists():
 cfg=load(R/'resource-project.json');project=pathlib.Path(cfg['projectPath']);finalize=load(pathlib.Path(cfg['receiptRoot'])/'finalize.json');manifest=load(finalize['fixtureManifest']);baseline=load(manifest['baselineManifestPath']);profile=baseline['metadataEncodingProfile2'];context=CodecSourceContext(project,W/'hybridclr',result['repositories']['hybridclr']);content,fresh=read_codec(baseline['sourcePins']['hybridclr'],profile['nativeSourceRevision'],profile['nativeCodecHeaderSha256'],context);assert fresh==load(path) and hashlib.sha256(content).hexdigest()==profile['nativeCodecHeaderSha256'];record['checks'].append({'id':'LN-003-codec-source-context','state':'Passed','receipt':bound(path),'verifiedContext':fresh,'originalResourceBindingCell':cells['resource-input-binding']['result'],'scope':'Authenticated source blob only; no graph/native/runtime success inferred'})
else:record['checks'].append({'id':'LN-003-codec-source-context','state':'Unavailable','originalCell':cells['resource-input-binding']['result']})
path=R/'layout-identity-verification.json'
record['checks'].append({'id':'LN-004-current-sidecar-verdict','state':load(path)['result'] if path.exists() else 'Unavailable','receipt':bound(path) if path.exists() else None,'independentFullRecheck':'LAYOUT_IDENTITY_AUDIT.json','runtimeAcceptance':False})
contextFailures=[{'id':c['id'],'state':c['result'],'error':c['error']} for c in result['cells'] if c['result']=='Failed' and 'Relative codec pin requires explicit authenticated project/owner context' in c.get('error','')]
record['checks'].append({'id':'LN-003-codec-context-error-check','state':'Failed' if contextFailures else 'Passed','originalFailedCells':contextFailures,'originalFullCaseStates':{c['id']:c['result'] for c in result['cells'] if c['id'].startswith('resource-T07-') or c['id'] in ['early-Control-P03','early-Control-P01','early-OrdinaryFirst','early-OrdinaryAfterReserve']},'scope':'No codec-context error in the executed consumers; full resource/positive startup cases still Failed at the later known R02 schema boundary. This is a partial stage check, not end-to-end runtime acceptance.'})
record['endUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();record['scope']='Existing sealed bytes and source-authority reads only; actual full Editor/production/runtime coverage is recorded separately.'
(P/'LN_REPAIR_AUDIT.json').write_text(json.dumps(record,indent=2)+'\n');print([(r['id'],r['state']) for r in record['checks']])
