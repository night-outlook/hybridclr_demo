"""Read-only authentication of N identity evidence; no launches or sealed writes."""
import pathlib,json,hashlib,datetime,sys
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261005O-ln-closure';R=P.parent/'R03LocalBatch-20261005O-ln-closure'
sys.path[:0]=[str(D/'Tools/AssemblyShadow/R03Completion'),str(D/'Tools/AssemblyShadow/R03')]
import layout_identity as li,layout_evidence as le
load=lambda p:json.loads(pathlib.Path(p).read_text())
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def bound(p):return {'path':str(p),'sha256':sha(p),'size':pathlib.Path(p).stat().st_size}
start=datetime.datetime.now(datetime.timezone.utc).isoformat();result=load(R/'LOCAL_BATCH_RESULT.json');cells={c['id']:c for c in result['cells']};inputs=load(R/'layout-identity-inputs.json');host=li.verify_results(R/'layout-identity',inputs);comparison=load(R/'layout-identity/comparison.json')
record={'kind':'ReadOnlyOLayoutIdentityAudit','startUtc':start,'host':host,'inputReceipt':bound(R/'layout-identity-inputs.json'),'comparisonReceipt':bound(R/'layout-identity/comparison.json'),'historicalReplay':{'basis':inputs['basis'],'linkedImages':len(inputs['linked']),'compilerImages':len(inputs['compiler']),'rawParentChangedRows':sum('ParentChanged' in r['reasons'] for r in comparison['declared']['types']),'resolvedRows':len(comparison['resolved']['types']),'rejectedRows':sum(r['decision']=='Rejected' for r in comparison['resolved']['types']),'mappedDeclarations':sum(r['runtimeFacadeUsed'] for r in comparison['compilerResolutions']),'nativeProofExecuted':False,'runtimeAcceptance':False},'freshReports':[],'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'expansionAuthorized':False}
config=load(R/'resource-project.json');project=pathlib.Path(config['projectPath']);phase=pathlib.Path(config['receiptRoot'])/'finalize.json';verification=R/'layout-identity-verification.json'
if not phase.exists():
 record['freshFiveReportAuditState']='NotRun';record['freshFiveReportReason']='Original resource-p05-finalize '+cells['resource-p05-finalize']['result'];record['productionVerificationState']='Unavailable' if not verification.exists() else load(verification)['result']
else:
 manifestPath=pathlib.Path(load(phase)['fixtureManifest']);manifest=load(manifestPath);baseRoot=pathlib.Path(manifest['baselineInputSnapshot']);assert manifestPath.is_relative_to(project) and baseRoot.is_relative_to(project)
 baseline,linked=li.snapshot(baseRoot,True);proofPath=li.child(baseRoot,li.PROOF);proof=load(proofPath);facade=li.child(baseRoot,li.FACADE)
 assert [r['patchId'] for r in manifest['fixtures']]==['P01','P02','P03','P04','P05'];v=load(verification) if verification.exists() else None
 for row in manifest['fixtures']:
  root=pathlib.Path(row['compileSnapshot']);patch=pathlib.Path(row['patchDirectory']);assert root.is_relative_to(project) and patch.is_relative_to(project)
  target,compiler=li.snapshot(root,False);sidecar=li.child(patch,li.REPORT);value=load(sidecar)
  try:checks=le.verify_value(value,baseline,target,linked,compiler,proof,sha(proofPath),sha(facade),row['closureLoadOrder']);fullState='Passed';fullError=None
  except Exception as error:
   fullState='Failed';fullError=type(error).__name__+': '+str(error);checks={'assemblies':len(value['assemblies']),'linkedImages':len(linked),'compilerImages':len(compiler),'mappedDeclarations':sum(x['runtimeFacadeUsed'] for x in value['identityEvidence']['compilerResolutions']),'nativeProofExecuted':False,'runtimeMustRevalidate':True,'expansionAuthorized':False,'basis':'Captured counts only; complete verifier failed'}
  assert target['snapshotHash']==row['compileSnapshotHash'] and baseline['snapshotHash']==manifest['baselineInputSnapshotHash'];record['freshReports'].append({'patchId':row['patchId'],'sidecar':bound(sidecar),'baselineReceipt':bound(baseRoot/'assembly-snapshot.json'),'targetReceipt':bound(root/'assembly-snapshot.json'),'linkedProof':bound(proofPath),'runtimeFacade':bound(facade),'checks':checks,'fullVerifierState':fullState,'fullVerifierError':fullError,'rejectedTypes':sum(t['decision']=='Rejected' for a in value['assemblies'] for t in a['types'])})
 assert record['freshReports'][-1]['checks']['mappedDeclarations']>0
 if v:
  assert v['kind']=='R03FreshLayoutIdentityVerification'
  if v['result']=='Passed':
   assert len(v['fixtures'])==5 and all(row['fullVerifierState']=='Passed' for row in record['freshReports'])
   for original,recheck in zip(v['fixtures'],record['freshReports']):assert original['patchId']==recheck['patchId'] and original['path']==recheck['sidecar']['path'] and original['sha256']==recheck['sidecar']['sha256'] and original['checks']==recheck['checks']
   assert cells['resource-input-binding']['evidence']['layoutIdentity']==v
  else:
   assert cells['resource-input-binding']['result']=='Failed' and v['error']==record['freshReports'][0]['fullVerifierError'] and v['fixtures']==[]
 record['freshFiveReportAuditState']='Passed' if all(row['fullVerifierState']=='Passed' for row in record['freshReports']) else 'Failed';record['productionVerificationState']=v['result'] if v else 'Unavailable';record['verificationReceipt']=bound(verification) if v else None
record['endUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();record['status']='Passed';record['interpretation']='Authentication audit only; original cell states preserved. Historical replay is reused-audited input. Nominal sidecars are not native offset/allocation or runtime authority.'
(P/'LAYOUT_IDENTITY_AUDIT.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k not in ['freshReports']},indent=2));print('Fresh reports',[(r['patchId'],r['checks']) for r in record['freshReports']])
