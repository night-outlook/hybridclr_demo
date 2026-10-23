from pathlib import Path
import json,hashlib,subprocess,datetime,ast,os,plistlib,concurrent.futures,difflib
P=Path(__file__).resolve().parent;E=json.loads((P/'EXPECTED.json').read_text());W=Path(E['workspace']);D=W/'hybridclr_demo';N=W/'il2cpp_plus';O=Path(E['output']);S=Path(E['scratch'])
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def save(name,v):(P/name).write_text(json.dumps(v,indent=2)+'\n')
def load(p):return json.loads(p.read_text())
started=now();assert not (P/'INVOCATION.json').exists() and not (P/'RECEIPT.json').exists() and not O.exists() and not O.is_symlink() and not S.exists() and not S.is_symlink()
# Read-only structural diagnosis; never re-execute the failed provenance helper.
tree=ast.parse((N/'tools/r03/diagnostic_stream/run_opaque_execution_inventory.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='verify');lit={}
for n in fn.body:
 if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
  try:lit[n.targets[0].id]=ast.literal_eval(n.value)
  except (ValueError,TypeError):pass
cpp=(N/'libil2cpp/vm/AssemblyShadow.cpp').read_text();api=(N/'libil2cpp/vm/AssemblyShadow.h').read_text()
removed=[]
for path,key,current in [('libil2cpp/vm/AssemblyShadow.cpp','admitted_include',cpp),('libil2cpp/vm/AssemblyShadow.h','admitted_decl',api)]:
 original=subprocess.check_output(['git','-C',str(N),'show','82ddcef9417e3d662fdd39916a92124b5c835094:'+path])
 assert current.count(lit[key])==1 and current.replace(lit[key],'').encode()==original
 removed.append(dict(path=path,currentSha256=sha(N/path),prior82ddSha256=hashlib.sha256(original).hexdigest(),exactNewAdditiveBytes=lit[key],removingOnlyPublishedAdditionRestoresPrior82ddBytes=True))
# Reconstruct the same old fingerprint in data only, exposing the omitted new emissions.
c=cpp;a=api
for k in ['integrated_json_header','integrated_json_include','shape_header','shape_source','live_header','live_source']:c=c.replace(lit[k],'')
for k in ['integrated_json_forward','integrated_json_decl','shape_forward','shape_declaration','live_forward','live_declaration']:a=a.replace(lit[k],'')
c=c.replace(lit['publisherHeader']+'\n','').replace(lit['publisherCall'],lit['previousWriter'])
for k,suffix in [('physicalHeader','\n'),('physicalApi','\n'),('physicalInclude',''),('nameHeader','\n'),('nameInline','')]:c=c.replace(lit[k]+suffix,'')
for k in ['physicalNamespace','physicalDecl','nameNamespace','nameDeclaration']:a=a.replace(lit[k],'')
for k,suffix in [('witnessHeader','\n'),('witnessDecl',''),('witnessInsert','')]:c=c.replace(lit[k]+suffix,'')
c=c.replace(lit['witnessClassify'],lit['oldAdmission'])
for k,suffix in [('revisionHeader','\n'),('revisionDecl',''),('revisionInsert','')]:c=c.replace(lit[k]+suffix,'')
c=c.replace('#include "AssemblyShadowOpaqueExecutionInventory.h"\n','').replace('// P1 inactive opaque execution observation inventory. No class dereference.\n#include "AssemblyShadowOpaqueExecutionInventorySource.inl"\n','')
a=a.replace('namespace assembly_shadow_opaque_execution { class Scratch; struct Receipt; }\n','').replace('    // P1 INACTIVE: observable opaque class identities without metadata dereference.\n    // Never returns pointers, type keys, JSON, or a VM-coherence claim.\n    static bool TryCaptureOpaqueExecutionInventory(\n        assembly_shadow_opaque_execution::Scratch& scratch,\n        assembly_shadow_opaque_execution::Receipt& receipt);\n','')
repro=[]
for path,reconstructed,blob,key in [('libil2cpp/vm/AssemblyShadow.cpp',c,'53aecc2d113b20b6ff825d0aa4ca0f4372a7cce2','admitted_include'),('libil2cpp/vm/AssemblyShadow.h',a,'32956c2c4084951131b497c1201712a0d4fe11b3','admitted_decl')]:
 old=subprocess.check_output(['git','-C',str(N),'cat-file','blob',blob]);assert reconstructed.encode()!=old and reconstructed.replace(lit[key],'').encode()==old
 repro.append(dict(path=path,originalGitBlob=blob,originalSha256=hashlib.sha256(old).hexdigest(),unstrippedReconstructionSha256=hashlib.sha256(reconstructed.encode()).hexdigest(),omittedOnlyNewLiteral=lit[key],readOnlyResidualComparisonExactlyRestoresOriginal=True))
 save(Path(path).name+'.FROZEN_COMPARISON.json',dict(kind='ReadOnlyFrozenByteComparison',originalGitBlob=blob,originalSha256=hashlib.sha256(old).hexdigest(),diff=''.join(difflib.unified_diff(old.decode().splitlines(True),reconstructed.splitlines(True),fromfile='immutable Git blob '+blob,tofile='failed Local helper reconstruction')),sourceUnmodified=True))
failure=dict(id='IR-LOCAL-P1-ADMITTED-PREFLIGHT-01',status='LocalCollectorPrerequisiteBlocked',ownership='Local-owned independent preflight helper; no product-source defect established',sourcePin=E['pins'],failedCommand=['python3','-B',str(P/'run-once.py')],commandExit=1,failedLine=150,tracebackPath=str(P/'run-once.log'),tracebackSha256=sha(P/'run-once.log'),helperPath=str(P/'run-once.py'),helperSha256=sha(P/'run-once.py'),symptom='Frozen original CPP reconstruction retains new published admitted include and fails exact Git-blob assertion before core launch.',rootCause='Independent Local helper adapted later owned-name reconstruction but missed earlier opaque CPP/API reconstruction. Native published source gate already strips exact admitted_include/admitted_decl.',firstFailureObserved='AssemblyShadow.cpp comparison against Git blob 53aecc2d113b20b6ff825d0aa4ca0f4372a7cce2',apiComparison='Not reached by failed helper; independently compared read-only in this diagnosis',reproduction=repro,currentSourceExactlyMatchesExpectedAdditiveDelta=removed,coreInvocationCreated=False,coreProcessLaunched=False,compilerLaunchesByThisCycle=0,actualTwentyGitBatchPostflightCommands='NotRun',coreBatchResult='NotRun',rootDisposition='Consumed/stopped after prerequisite failure; no retry or new suffix',wrapperProcessStartAndPid='Unavailable_NotRecordedBeforeInvocationStage',earliestRecordedPreflightTime=load(P/'SDK_BEFORE.json')['time'],failureLogMtimeUtc=datetime.datetime.fromtimestamp((P/'run-once.log').stat().st_mtime,datetime.timezone.utc).isoformat(),recommendedDirection='Review this Local collector omission; ensure every frozen CPP/API comparison strips only source-authenticated exact additive wrapper bytes without rebaselining fingerprints. A new Primary handoff and unused roots are required before another core attempt.',runtimeAcceptance=False)
save('PRE_CORE_FAILURE.json',failure)
# Full after-preservation against independent pre-root admission.
sdk=load(P/'SDK_BEFORE.json')
for row in sdk['files']:
 q=Path(row['path']);assert q.stat().st_size==row['bytes'] and sha(q)==row['sha256'] and (os.readlink(q) if q.is_symlink() else None)==row['symlink']
paths={Path(sdk['anchor']),Path(sdk['anchor']).parent.parent/'Info.plist'}
for root in sdk['roots']:paths.update(q for q in Path(root).rglob('*') if q.is_file())
assert paths=={Path(row['path']) for row in sdk['files']}
save('SDK_AFTER.json',dict(result='Preserved',time=now(),verifiedFiles=len(sdk['files']),verifiedBytes=sum(x['bytes'] for x in sdk['files']),newCompilation='NotRun',unityNeverLaunched=True,beforeReceiptSha256=sha(P/'SDK_BEFORE.json')))
for row in load(P/'SOURCE_BINDINGS.json'):assert sha(Path(row['path']))==row['sha256'] and Path(row['path']).stat().st_size==row['bytes']
ret=load(P/'ADMISSION_RETAINED_BEFORE.json');links=0
for item in ret['consumed']:
 raw=Path(item['rawRoot']);scratch=Path(item['scratchRoot']);assert sha(raw/'MANIFEST.json')==item['manifestSha256'];m=load(raw/'MANIFEST.json')
 for row in m['files']:
  q=raw/row['path'];assert q.stat().st_size==row['size'] and sha(q)==row['sha256']
 for row in load(raw/'native-sdk/native-sdk-inputs.json')['files']:assert sha(scratch/row['path'])==row['sha256']
 for row in load(raw/'legacy-host/MANIFEST.json')['files']:
  if row.get('kind')=='Symlink':
   q=raw/'legacy-host'/row['path'];assert q.is_symlink() and os.readlink(q)==row['target'];links+=1
 audit=Path(item['auditRoot']);assert {str(q) for q in audit.rglob('*') if q.is_file() and not q.is_symlink()}=={row['path'] for row in item['auditFiles']}
 for row in item['auditFiles']:q=Path(row['path']);assert q.stat().st_size==row['bytes'] and sha(q)==row['sha256']
save('ADMISSION_RETAINED_AFTER.json',dict(result='Preserved',time=now(),consumedSets=len(ret['consumed']),historicalNegativeSymlinks=links,beforeReceiptSha256=sha(P/'ADMISSION_RETAINED_BEFORE.json'),sourceBindingsPreserved=True,allHistoricalOutcomesUnchanged=True))
cps=load(P/'ADMISSION_CHECKPOINTS_BEFORE.json')
for item in cps['checkpoints']:
 root=Path(item['root']);assert sha(root/'MANIFEST.sha256')==item['manifestSha256']
 assert {str(q.relative_to(root)) for q in root.rglob('*') if q.is_file()}=={row['path'] for row in item['files']}|{'MANIFEST.sha256'}
 for row in item['files']:q=root/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['bytes']
save('ADMISSION_CHECKPOINTS_AFTER.json',dict(result='Preserved',count=len(cps['checkpoints']),beforeReceiptSha256=sha(P/'ADMISSION_CHECKPOINTS_BEFORE.json'),allCheckpointBytesPreserved=True))
def authority(n):
 rows=[];path=W/n
 for args in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--short'],['remote','-v'],['worktree','list','--porcelain'],['submodule','status','--recursive'],['ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1']]:
  cmd=['git','-C',str(path),*args];t=now();r=subprocess.run(cmd,capture_output=True,text=True,timeout=90);rows.append(dict(argv=cmd,start=t,end=now(),exit=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0
 assert rows[0]['stdout'].strip()==str(path) and rows[1]['stdout'].strip()=='codex/assembly-shadow-r01b-h1' and rows[2]['stdout'].strip()==E['pins'][n] and not rows[3]['stdout'] and rows[-1]['stdout'].split()[0]==E['pins'][n]
 return n,rows
save('GIT_AFTER.json',dict(concurrent.futures.ThreadPoolExecutor(4).map(authority,E['pins'])))
names=['command-failures','legacy-host','metadata-gate','bounded-class','bounded-physical','bounded-first-use','owned-general','live-general','owned-execution','empty-live','opaque-inventory','physical-membership','owned-physical-names','owned-physical-json','live-owned-physical-json','observed-type-shape','live-type-shape-census','observed-type-shape-json','vm-shape-json','admitted-execution','bounded-status','bounded-inventory','frozen-v2','managed-sdk','native-sdk']
result=dict(kind='IndependentLocalPrerequisiteOutcome_NotCoreBatchResult',result='PrerequisiteBlocked',batchResult='NotRun',findingId=failure['id'],sourcePins=E['pins'],workspace=str(W),rawOutput=str(O),sdkScratch=str(S),start=started,end=now(),rootAdmission='Passed',independentSourcePreservation='Passed',installedSdkPreservation='Passed',historicalEvidencePreservation='Passed',consumedP1Sets=len(ret['consumed']),priorCheckpointSets=len(cps['checkpoints']),historicalNegativeSymlinks=links,components=[dict(name=n,status='NotRun',invoked=False,reason='Independent Local provenance prerequisite failed before core invocation') for n in names],componentCount=25,attemptedComponentCount=0,original85FailureTests='NotRun',newNineCaseProfiles='NotRun',managedFivePlusNegative='NotRun',native100Configurations='NotRun',allEightInventoryFlags='NotRun',twentyActualBatchGitPostflightCommands='NotRun',aggregateManifestConsistency='NotRun_NoCoreManifestConstructed',coreRootAbsent=True,sdkScratchAbsent=True,independentGitAfter='PassedFourExactCleanHeads',coreInvocationRecordAbsent=True,coreProcessPid='Unavailable_NotLaunched',noCoreRetry=True,unityEditorAndPlayer='NotRun',warnings='Unavailable_NoFreshCompilerRun',R03Accepted=False,H2Passed=False,qualificationApproved=False,ReadyForHumanReviewGate=False,fullLegacyRegressionAcceptance=False,runtimeAcceptance=False,nextState='Primary Implementation')
save('LOCAL_RESULT.json',result);print(json.dumps(result,indent=2))
