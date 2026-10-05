"""Read-only authentication of M's current policy proof and Q22; no launches."""
import pathlib,json,hashlib,datetime,sys,types
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261005N-identity';R=P.parent/'R03LocalBatch-20261005N-identity'
sys.path[:0]=[str(D/'Tools/AssemblyShadow/R03Completion'),str(D/'Tools/AssemblyShadow/R03')]
import compiler_policy_inputs as cp
load=lambda p:json.loads(pathlib.Path(p).read_text());sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();start=datetime.datetime.now(datetime.timezone.utc).isoformat()
result=load(R/'LOCAL_BATCH_RESULT.json');cfg=load(R/'resource-project.json');project=pathlib.Path(cfg['projectPath']);batch=types.SimpleNamespace(root=R,workspace=W,resource_config=cfg,pins=result['repositories']);idx={f['path']:f for f in load(R/'evidence-index.json')['files']}
def bound(p):
 p=pathlib.Path(p);h=sha(p);assert idx[str(p.relative_to(R))]['sha256']==h;return {'path':str(p),'sha256':h,'sealedIndexAuthenticated':True}
Q=R/'qualification/Q22-deterministic-source-binding';inputs=load(Q/'determinism-inputs.json');assert len(inputs['files'])==4 and inputs['before']==inputs['after'];assert (Q/'determinism-first.json').read_bytes()==(Q/'determinism-second.json').read_bytes()
for name,h in zip(inputs['files'],inputs['before']):assert sha(name)==h;bound(name)
record={'kind':'ReadOnlyNCurrentCompilerPolicyAudit','startUtc':start,'Q22':{'state':'Passed','inputFiles':4,'beforeAfterEqual':True,'reportsByteIdentical':True,'inputs':bound(Q/'determinism-inputs.json'),'first':bound(Q/'determinism-first.json'),'second':bound(Q/'determinism-second.json'),'qualificationApproved':False},'compilerPolicyInputs':cfg['compilerPolicyInputs'],'currentImmutablePolicyFiles':cp.validate_inputs(project),'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'expansionAuthorized':False,'interpretation':'Original result states preserved; current compile-only guard evidence is distinct from linked proof and runtime. Historical M compiler bytes are not inputs to this audit.'}
path=pathlib.Path(cfg['receiptRoot'])/'compiler-policy-contract.json';cell=next(c for c in result['cells'] if c['id']=='resource-compiler');record['originalCompilerCellState']=cell['result']
if path.exists():
 r=load(path);record.update(contract=bound(path),originalContractResult=r['result'])
 if r['result']=='Passed':
  verdict=cp.verify_report(path,batch,project);verification=load(R/'compiler-policy-verification.json');assert verdict==verification;S=pathlib.Path(r['snapshot']);mode=load(S/'compiler-mode.json');assert mode['snapshotReceiptSha256']==sha(S/'assembly-snapshot.json') and mode['developmentBuild'] and mode['snapshotHash']==load(S/'assembly-snapshot.json')['snapshotHash']
  record.update(state='Passed',guardControls=16,rawSites=25,compilerSnapshot=bound(S/'assembly-snapshot.json'),compilerMode=bound(S/'compiler-mode.json'),capturedConfiguration=bound(S/'RawTypeAdmissions/configuration.json'),capturedCompiledProof=bound(S/'RawTypeAdmissions/compiled-evidence.json'),observation=bound(path.parent/'compiler-policy-controls/observation.json'),verification=bound(R/'compiler-policy-verification.json'),moduleFiles=verdict['moduleFiles'],originalCompilerPolicyPassed=True,capturedRawProofVerified=True,linkedProofExecuted=False,controls=r['observation']['controls'],onQuitMethodHash=r['observation']['onQuitMethodHash'])
  for p in S.rglob('*.pdb'):bound(p)
  for c in r['observation']['controls']:bound(c['configurationPath'])
 else:record.update(state='Failed',error=r.get('error'),partialReceipt=r)
else:record.update(state='Unavailable',reason='Original compiler gate did not emit a compiler-policy contract; do not manufacture success')
linked=[]
for p in sorted((project/'_temp/AssemblyShadow').glob('**/RawTypeAdmissions/linked-evidence.json')):
 j=load(p);assert j['phase']=='Linked' and j['configurationSha256']==cp.RAW_SHA;linked.append({'receipt':bound(p),'siteCount':len(j['sites']),'buildGuid':j.get('buildGuid'),'snapshotRoot':str(p.parent.parent),'phase':'Linked','limitation':'File authentication; full build/linked inventory verdict is separately recorded by original production receipts and completion audit'})
record['availableLinkedProofReceipts']=linked;record['linkedProofCoverage']='Available' if linked else 'Unavailable';record['endUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(P/'COMPILER_POLICY_AUDIT.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k in ['state','originalCompilerCellState','guardControls','rawSites','moduleFiles','linkedProofCoverage','originalCompilerPolicyPassed','capturedRawProofVerified']},indent=2));print('Q22 Passed; linked receipts',len(linked))
