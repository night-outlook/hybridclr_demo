from pathlib import Path
import json,subprocess,hashlib,datetime,platform,os,plistlib
P=Path(__file__).resolve().parent;E=json.loads((P/'EXPECTED.json').read_text());W=Path(E['workspace']);D=W/'hybridclr_demo';U=Path(E['unity']);C=U.parent.parent;O=Path(E['output']);S=Path(E['scratch'])
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def save(n,x):(P/n).write_text(json.dumps(x,indent=2)+'\n')
info=plistlib.loads((C/'Info.plist').read_bytes());assert info.get('CFBundleVersion')=='2022.3.62f2' or info.get('CFBundleShortVersionString')=='2022.3.62f2'
roots=[C/'il2cpp/libil2cpp',C/'il2cpp/external',C/'Managed',C/'NetCoreRuntime',C/'DotNetSdkRoslyn',C/'NetStandard'];paths=set([U,C/'Info.plist'])
for root in roots:
 assert root.is_dir();paths.update(p for p in root.rglob('*') if p.is_file())
files=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p),symlink=os.readlink(p) if p.is_symlink() else None) for p in sorted(paths)]
save('SDK_BEFORE.json',dict(time=now(),unityVersion='2022.3.62f2',unityNeverLaunched=True,anchor=str(U),roots=list(map(str,roots)),files=files))
for name,a in [('python',['python3','--version']),('clang',['clang++','--version']),('os',['sw_vers']),('kernel',['uname','-a']),('sdkpath',['xcrun','--show-sdk-path']),('space',['df','-k',str(P)])]:
 r=subprocess.run(a,capture_output=True,text=True);save(name+'.json',dict(argv=a,exit=r.returncode,stdout=r.stdout,stderr=r.stderr,time=now()))
inputs=[]
for n,paths in {'hybridclr_demo':['Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowOwnedPhysicalNamesSyntax.cpp','Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowPhysicalMembershipSyntax.cpp','Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowOpaqueInventorySyntax.cpp','Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowExecutionEmptyLiveSyntax.cpp','Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowExecutionComposeSyntax.cpp','Tools/AssemblyShadow/R03IR/run_p1_command_failure_tests.py','Tools/AssemblyShadow/R03IR/test_p1_command_failures.py','Tools/AssemblyShadow/R03IR/test_p1_metadata_preflight.py','Tools/AssemblyShadow/R03IR/test_p1_managed_receipt.py','Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowGeneralComposeSyntax.cpp','Tools/AssemblyShadow/R03/source-pins.json','Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py','Tools/AssemblyShadow/R03IR/run_primary_host_preflight.py','Tools/AssemblyShadow/R03/native_validation.py','Tools/AssemblyShadow/R03/build_api.py','Tools/AssemblyShadow/R03/input_validation.py','Packages/manifest.json','Packages/packages-lock.json','ProjectSettings/ProjectVersion.txt'],'il2cpp_plus':['libil2cpp/vm/AssemblyShadowOwnedPhysicalNames.h','libil2cpp/vm/AssemblyShadowOwnedPhysicalNamesSource.inl','libil2cpp/vm/AssemblyShadowPhysicalMembership.h','libil2cpp/vm/AssemblyShadowPhysicalMembershipSource.inl','tools/r03/diagnostic_stream/run_owned_physical_names.py','tools/r03/diagnostic_stream/owned_physical_names_fixture.cpp','tools/r03/diagnostic_stream/run_physical_membership.py','tools/r03/diagnostic_stream/physical_membership_fixture.cpp','libil2cpp/vm/AssemblyShadowExecutionRegistryPublisher.h','libil2cpp/vm/AssemblyShadowExecutionRegistrationWitness.h','libil2cpp/vm/AssemblyShadowExecutionRegistryRevision.h','libil2cpp/vm/AssemblyShadowOpaqueExecutionInventory.h','libil2cpp/vm/AssemblyShadowOpaqueExecutionInventorySource.inl','tools/r03/diagnostic_stream/run_opaque_execution_inventory.py','tools/r03/diagnostic_stream/opaque_inventory_fixture.cpp','tools/r03/diagnostic_stream/test_bounded_execution_empty_live_receipts.py','libil2cpp/vm/AssemblyShadowBoundedExecutionEmptyLive.h','libil2cpp/vm/AssemblyShadowBoundedExecutionEmptyLiveSource.inl','tools/r03/diagnostic_stream/run_bounded_execution_empty_live.py','tools/r03/diagnostic_stream/empty_live_fixture/MockRuntime.h','tools/r03/diagnostic_stream/empty_live_fixture/AssemblyShadowFrozenExecutionRecord.h','tools/r03/diagnostic_stream/empty_live_fixture/AssemblyShadowMetadataLifetime.h','tools/r03/diagnostic_stream/empty_live_fixture/fixture.cpp','libil2cpp/vm/AssemblyShadowFrozenExecutionRecord.h','libil2cpp/vm/AssemblyShadowR02Snapshot.h','libil2cpp/vm/AssemblyShadowFrozenR02Serializer.h','tools/r03/diagnostic_stream/run_frozen_execution.py','tools/r03/diagnostic_stream/frozen_execution_fixture.cpp','tools/r03/diagnostic_stream/frozen_execution_allocations.cpp','tools/r03/diagnostic_stream/reference/AssemblyShadowExecutionSerializer.h','tools/r03/diagnostic_stream/reference/AssemblyShadowR02Diagnostics.h','tools/r03/diagnostic_stream/test_frozen_execution_include_path.py','tools/r03/diagnostic_stream/test_bounded_general_live_command.py','libil2cpp/vm/AssemblyShadowBoundedGeneralLive.h','libil2cpp/vm/AssemblyShadowBoundedGeneralLiveSource.inl','libil2cpp/vm/AssemblyShadow.h','tools/r03/diagnostic_stream/run_bounded_general_live.py','tools/r03/diagnostic_stream/bounded_general_live_fixture.cpp','libil2cpp/vm/AssemblyShadowBoundedGeneralComposer.h','libil2cpp/vm/AssemblyShadowFrozenGeneralCapture.h','tools/r03/diagnostic_stream/run_bounded_general_composer.py','tools/r03/diagnostic_stream/bounded_general_composer_fixture.cpp','libil2cpp/vm/AssemblyShadow.cpp','libil2cpp/vm/AssemblyShadowBoundedFirstUseCapture.h','tools/r03/diagnostic_stream/run_bounded_first_use.py','tools/r03/diagnostic_stream/bounded_first_use_fixture.cpp','libil2cpp/vm/AssemblyShadowMetadataLifetime.h','libil2cpp/vm/Runtime.cpp','libil2cpp/vm/Assembly.cpp','libil2cpp/vm/AssemblyShadowVisibility.cpp','tools/r03/diagnostic_stream/run_metadata_lifetime_gate.py']}.items():
 for rel in paths:
  p=W/n/rel;blob=subprocess.check_output(['git','-C',str(W/n),'rev-parse',E['pins'][n]+':'+rel],text=True).strip();assert p.read_bytes()==subprocess.check_output(['git','-C',str(W/n),'cat-file','blob',blob]);inputs.append(dict(path=str(p),repository=n,commit=E['pins'][n],gitBlob=blob,bytes=p.stat().st_size,sha256=sha(p)))
save('SOURCE_BINDINGS.json',inputs)
old=[]
for name in ['local-validation-host-only-20261015-fc0d3565','local-validation-host-only-20261015-74dbdbea-a1']:
 cp=D/'Docs/AssemblyShadow/History/M07R/R03'/name/'MANIFEST.sha256';old.append(dict(path=str(cp),sha256=sha(cp)))
for name in ['R03-PRIMARY-HOST-ONLY-20261015-fc0d3565','R03-PRIMARY-HOST-ONLY-20261015-74dbdbea-a1']:
 p=O.parent/name/'MANIFEST.json';old.append(dict(path=str(p),sha256=sha(p)))

consumed=O.parent/'R03-P1-METADATA-SOURCE-20261016-0a0b'
for rel,h in {'RESULT.json':'13e256649c9c6355b4ed7eb4c5190a0f62acacaf42ad0195a27a21718d3ba565','MANIFEST.json':'b0f6c0597a7311ce2ec8647d807da8dcfbef34ee41140a104ef79dc84a10a13f','managed-sdk/build-api/results.json':'43f38be35063559bcb156c31968f6b80d8707982692aef55fd6ab05285ea916e'}.items():
 p=consumed/rel;assert sha(p)==h;old.append(dict(path=str(p),sha256=h))
cp=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-metadata-source-20261016-0a0b/MANIFEST.sha256';old.append(dict(path=str(cp),sha256=sha(cp)))
for row in json.loads((consumed/'MANIFEST.json').read_text())['files']:
 p=consumed/row['path'];assert p.stat().st_size==row['size'] and sha(p)==row['sha256']
old_native=json.loads((consumed/'native-sdk/native-sdk-inputs.json').read_text())['files'];prior_scratch=O.parent/'Scratch-R03-P1-METADATA-20261016-0a0b'
for row in old_native:assert sha(prior_scratch/row['path'])==row['sha256']
save('CONSUMED_BEFORE.json',dict(result='Preserved',regularFilesVerified=len(json.loads((consumed/'MANIFEST.json').read_text())['files']),nativeScratchInputsVerified=len(old_native),priorAggregateResult='FailedOrIncomplete',originalRawAndScratchReused=False,consumedRoot=str(consumed),scratchRoot=str(prior_scratch)))


passed=O.parent/'R03-P1-MANAGED-RECEIPT-20261016-0620';pcp=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-managed-receipt-20261016-0620'
pa=json.loads((pcp/'preflight/EVIDENCE_AUDIT.json').read_text())
for rel,h in {'RESULT.json':pa['rawResultSha256'],'MANIFEST.json':pa['rawManifestSha256'],'managed-sdk/build-api/results.json':pa['managed']['actualResultSha256']}.items():
 p=passed/rel;assert sha(p)==h;old.append(dict(path=str(p),sha256=h))
old.append(dict(path=str(pcp/'MANIFEST.sha256'),sha256=sha(pcp/'MANIFEST.sha256')))
for row in json.loads((passed/'MANIFEST.json').read_text())['files']:
 p=passed/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
ps=O.parent/'Scratch-R03-P1-MANAGED-RECEIPT-20261016-0620';pi=json.loads((passed/'native-sdk/native-sdk-inputs.json').read_text())['files']
for row in pi:assert sha(ps/row['path'])==row['sha256']
save('CONSUMED_PASS_BEFORE.json',dict(result='Preserved',rawRoot=str(passed),scratchRoot=str(ps),regularFilesVerified=len(json.loads((passed/'MANIFEST.json').read_text())['files']),scratchInputsVerified=len(pi),priorOutcome='PassedSourceHostAndSDKOnly',noPriorConsumerOrRuntimeRerun=True))


firstuse=O.parent/'R03-P1-FIRSTUSE-CLASS-20261016-f598';fcp=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-firstuse-class-20261016-f598';fa=json.loads((fcp/'preflight/EVIDENCE_AUDIT.json').read_text())
for rel,h in {'RESULT.json':fa['rawResultSha256'],'MANIFEST.json':fa['rawManifestSha256'],'managed-sdk/build-api/results.json':fa['managed']['actualResultSha256']}.items():
 p=firstuse/rel;assert sha(p)==h;old.append(dict(path=str(p),sha256=h))
old.append(dict(path=str(fcp/'MANIFEST.sha256'),sha256=sha(fcp/'MANIFEST.sha256')))
for row in json.loads((firstuse/'MANIFEST.json').read_text())['files']:
 p=firstuse/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
fs=O.parent/'Scratch-R03-P1-FIRSTUSE-CLASS-20261016-f598';fi=json.loads((firstuse/'native-sdk/native-sdk-inputs.json').read_text())['files']
for row in fi:assert sha(fs/row['path'])==row['sha256']
save('CONSUMED_FIRSTUSE_BEFORE.json',dict(result='Preserved',rawRoot=str(firstuse),scratchRoot=str(fs),regularFilesVerified=len(json.loads((firstuse/'MANIFEST.json').read_text())['files']),scratchInputsVerified=len(fi),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))


owned=O.parent/'R03-P1-OWNED-GENERAL-20261016-3dc9';ocp=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-owned-general-20261016-3dc9';oa=json.loads((ocp/'preflight/EVIDENCE_AUDIT.json').read_text())
for rel,h in {'RESULT.json':oa['rawResultSha256'],'MANIFEST.json':oa['rawManifestSha256'],'managed-sdk/build-api/results.json':oa['managed']['actualResultSha256']}.items():
 p=owned/rel;assert sha(p)==h;old.append(dict(path=str(p),sha256=h))
old.append(dict(path=str(ocp/'MANIFEST.sha256'),sha256=sha(ocp/'MANIFEST.sha256')))
for row in json.loads((owned/'MANIFEST.json').read_text())['files']:
 p=owned/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
oscratch=O.parent/'Scratch-R03-P1-OWNED-GENERAL-20261016-3dc9';oi=json.loads((owned/'native-sdk/native-sdk-inputs.json').read_text())['files']
for row in oi:assert sha(oscratch/row['path'])==row['sha256']
save('CONSUMED_OWNED_BEFORE.json',dict(result='Preserved',rawRoot=str(owned),scratchRoot=str(oscratch),regularFilesVerified=len(json.loads((owned/'MANIFEST.json').read_text())['files']),scratchInputsVerified=len(oi),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))
for n in ['R03-PRIMARY-HOST-ONLY-20261015-fc0d3565','R03-PRIMARY-HOST-ONLY-20261015-74dbdbea-a1']:
 root=O.parent/n
 for row in json.loads((root/'MANIFEST.json').read_text())['files']:
  q=root/row['path']
  if row.get('kind')=='Symlink':assert q.is_symlink() and os.readlink(q)==row['target']
  else:assert sha(q)==row['sha256'] and q.stat().st_size==row['size']
save('HISTORICAL_HOST_BEFORE.json',dict(result='Preserved',allOriginalManifestEntriesVerified=True))
space=os.statvfs(O.parent);assert space.f_bavail*space.f_frsize>8*1024**3
save('SPACE_ADMISSION.json',dict(availableBytes=space.f_bavail*space.f_frsize,minimumLocalWorkingMarginBytes=8*1024**3,scope='Small source/SDK-only batch, no runtime storage threshold altered',time=now()))


lprior=O.parent/'R03-P1-LIVE-GENERAL-20261018-5667';lcp=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-live-general-20261018-5667';la=json.loads((lcp/'preflight/EVIDENCE_AUDIT.json').read_text())
for rel,h in {'RESULT.json':la['rawResultSha256'],'MANIFEST.json':la['rawManifestSha256'],'managed-sdk/build-api/results.json':la['managed']['actualResultSha256']}.items():
 p=lprior/rel;assert sha(p)==h;old.append(dict(path=str(p),sha256=h))
old.append(dict(path=str(lcp/'MANIFEST.sha256'),sha256=sha(lcp/'MANIFEST.sha256')))
for row in json.loads((lprior/'MANIFEST.json').read_text())['files']:
 p=lprior/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
lscratch=O.parent/'Scratch-R03-P1-LIVE-GENERAL-20261018-5667';li=json.loads((lprior/'native-sdk/native-sdk-inputs.json').read_text())['files']
for row in li:assert sha(lscratch/row['path'])==row['sha256']
save('CONSUMED_LIVE_BEFORE.json',dict(result='Preserved',rawRoot=str(lprior),scratchRoot=str(lscratch),regularFilesVerified=len(json.loads((lprior/'MANIFEST.json').read_text())['files']),scratchInputsVerified=len(li),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))

cmdprior=O.parent/'R03-P1-COMMAND-FAILURES-20261019-cmdfail-e29a';ccp=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-command-failures-20261019-cmdfail-e29a';ca=json.loads((ccp/'preflight/EVIDENCE_AUDIT.json').read_text())
for rel,h in {'RESULT.json':ca['rawResultSha256'],'MANIFEST.json':ca['rawManifestSha256'],'managed-sdk/build-api/results.json':ca['managed']['actualResultSha256']}.items():
 p=cmdprior/rel;assert sha(p)==h;old.append(dict(path=str(p),sha256=h))
old.append(dict(path=str(ccp/'MANIFEST.sha256'),sha256=sha(ccp/'MANIFEST.sha256')))
for row in json.loads((cmdprior/'MANIFEST.json').read_text())['files']:
 p=cmdprior/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
cscratch=O.parent/'Scratch-R03-P1-COMMAND-FAILURES-20261019-cmdfail-e29a';ci=json.loads((cmdprior/'native-sdk/native-sdk-inputs.json').read_text())['files']
for row in ci:assert sha(cscratch/row['path'])==row['sha256']
save('CONSUMED_COMMAND_BEFORE.json',dict(result='Preserved',rawRoot=str(cmdprior),scratchRoot=str(cscratch),regularFilesVerified=len(json.loads((cmdprior/'MANIFEST.json').read_text())['files']),scratchInputsVerified=len(ci),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))
refs=[]
for name,h in {'AssemblyShadowExecutionSerializer.h':'30c78cf0ac30f7f1e59f573b950f594ac2379afaa372f544b9fdcaa26cc608ef','AssemblyShadowR02Diagnostics.h':'b42e61cbd65dc26f2f9c207c318697b46d0c909e7d83f1e2b8b4b4e109ce56ba'}.items():
 p=W/'il2cpp_plus/tools/r03/diagnostic_stream/reference'/name
 raw=subprocess.check_output(['git','-C',str(W/'il2cpp_plus'),'show','5667e3712f49e4b38c7dd7359e57f81e344626da:libil2cpp/vm/'+name])
 assert p.read_bytes()==raw and sha(p)==h
 refs.append(dict(path=str(p),sha256=h,originalCommit='5667e3712f49e4b38c7dd7359e57f81e344626da',originalPath='libil2cpp/vm/'+name))
save('EXECUTION_REFERENCE_BEFORE.json',dict(result='AuthenticatedOriginalGitBytes',references=refs))
runner=(W/'il2cpp_plus/tools/r03/diagnostic_stream/run_frozen_execution.py').read_text();assert "'-iquote', str(native/'libil2cpp/vm')" in runner


fprior=O.parent/'R03-P1-OWNED-EXECUTION-20261019-f0c5';fcp=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-owned-execution-20261019-f0c5';f_a=json.loads((fcp/'preflight/EVIDENCE_AUDIT.json').read_text())
for rel,h in {'RESULT.json':f_a['rawResultSha256'],'MANIFEST.json':f_a['rawManifestSha256'],'managed-sdk/build-api/results.json':f_a['managed']['actualResultSha256']}.items():
 p=fprior/rel;assert sha(p)==h;old.append(dict(path=str(p),sha256=h))
old.append(dict(path=str(fcp/'MANIFEST.sha256'),sha256=sha(fcp/'MANIFEST.sha256')))
for row in json.loads((fprior/'MANIFEST.json').read_text())['files']:
 p=fprior/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
fscratch=O.parent/'Scratch-R03-P1-OWNED-EXECUTION-20261019-f0c5';f_i=json.loads((fprior/'native-sdk/native-sdk-inputs.json').read_text())['files']
for row in f_i:assert sha(fscratch/row['path'])==row['sha256']
save('CONSUMED_EXECUTION_BEFORE.json',dict(result='Preserved',rawRoot=str(fprior),scratchRoot=str(fscratch),regularFilesVerified=len(json.loads((fprior/'MANIFEST.json').read_text())['files']),scratchInputsVerified=len(f_i),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))
N=W/'il2cpp_plus'
cpp=(N/'libil2cpp/vm/AssemblyShadow.cpp').read_text();api=(N/'libil2cpp/vm/AssemblyShadow.h').read_text()
inc='#include "AssemblyShadowOpaqueExecutionInventorySource.inl"';header='#include "AssemblyShadowOpaqueExecutionInventory.h"'
assert cpp.count(inc)==cpp.count(header)==1 and cpp.count('TryCaptureOpaqueExecutionInventory(')==0
import ast
runner_path=N/'tools/r03/diagnostic_stream/run_opaque_execution_inventory.py';tree=ast.parse(runner_path.read_text());gate=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='verify');literals={}
for node in gate.body:
 if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
  try:literals[node.targets[0].id]=ast.literal_eval(node.value)
  except (ValueError,TypeError):pass
for key in ['publisherCall','previousWriter','publisherHeader','witnessHeader','witnessDecl','witnessInsert','witnessClassify','oldAdmission','revisionHeader','revisionDecl','revisionInsert']:assert key in literals
assert cpp.count(literals['publisherCall'])==1 and cpp.count(literals['publisherHeader'])==1
assert 'ExecutionObservationLock lock;' in literals['publisherCall'] and 'assembly_shadow_execution_publisher::Insert(' in literals['publisherCall'] and 'klass,witnessedSource);' in literals['publisherCall']
oldcpp=cpp.replace(literals['publisherHeader']+'\n','').replace(literals['publisherCall'],literals['previousWriter'])
for key in ['physicalHeader','physicalApi','physicalInclude','nameHeader','nameInline']:assert oldcpp.count(literals[key])==1,key
oldcpp=oldcpp.replace(literals['physicalHeader']+'\n','').replace(literals['physicalApi']+'\n','').replace(literals['physicalInclude'],'').replace(literals['nameHeader']+'\n','').replace(literals['nameInline'],'')
api=api.replace(literals['physicalNamespace'],'').replace(literals['physicalDecl'],'').replace(literals['nameNamespace'],'').replace(literals['nameDeclaration'],'')
for key in ['witnessHeader','witnessDecl','witnessInsert','witnessClassify','revisionHeader','revisionDecl','revisionInsert']:assert oldcpp.count(literals[key])==1,key
oldcpp=oldcpp.replace(literals['witnessHeader']+'\n','').replace(literals['witnessDecl'],'').replace(literals['witnessInsert'],'').replace(literals['witnessClassify'],literals['oldAdmission'])
oldcpp=oldcpp.replace(literals['revisionHeader']+'\n','').replace(literals['revisionDecl'],'').replace(literals['revisionInsert'],'')
oldcpp=oldcpp.replace(header+'\n','').replace('// P1 inactive opaque execution observation inventory. No class dereference.\n'+inc+'\n','')
oldapi=api.replace('namespace assembly_shadow_opaque_execution { class Scratch; struct Receipt; }\n','').replace('    // P1 INACTIVE: observable opaque class identities without metadata dereference.\n    // Never returns pointers, type keys, JSON, or a VM-coherence claim.\n    static bool TryCaptureOpaqueExecutionInventory(\n        assembly_shadow_opaque_execution::Scratch& scratch,\n        assembly_shadow_opaque_execution::Receipt& receipt);\n','')
originals=[]
for rel,data,blob in [('libil2cpp/vm/AssemblyShadow.cpp',oldcpp.encode(),'53aecc2d113b20b6ff825d0aa4ca0f4372a7cce2'),('libil2cpp/vm/AssemblyShadow.h',oldapi.encode(),'32956c2c4084951131b497c1201712a0d4fe11b3')]:
 original=subprocess.check_output(['git','-C',str(N),'cat-file','blob',blob]);assert data==original
 assert subprocess.check_output(['git','-C',str(N),'rev-parse','48ee6468065a6b559f53719dc310d901d8181ab8:'+rel],text=True).strip()==blob
 originals.append(dict(path=rel,baseline='48ee6468065a6b559f53719dc310d901d8181ab8',originalBlob=blob,originalSha256=hashlib.sha256(original).hexdigest(),candidateSha256=sha(N/rel)))
save('OPAQUE_SOURCE_BINDING_BEFORE.json',dict(result='OriginalCppAndApiBytesPreservedExceptExactOpaqueAdditions',originals=originals,opaqueMethodSha256=sha(N/'libil2cpp/vm/AssemblyShadowOpaqueExecutionInventorySource.inl'),opaqueHeaderSha256=sha(N/'libil2cpp/vm/AssemblyShadowOpaqueExecutionInventory.h'),noDirectProductionCppCaller=True,revisionHeaderSha256=sha(N/'libil2cpp/vm/AssemblyShadowExecutionRegistryRevision.h'),removedOnlyExactOpaqueWitnessRevisionAndPublisherAdditions=True,publisherHeaderSha256=sha(N/'libil2cpp/vm/AssemblyShadowExecutionRegistryPublisher.h'),witnessHeaderSha256=sha(N/'libil2cpp/vm/AssemblyShadowExecutionRegistrationWitness.h'),productionPublisherCall=literals['publisherCall'],sourceGateSha256=sha(runner_path)))


eprior=O.parent/'R03-P1-EMPTY-LIVE-20261019-d16d';ecp=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-empty-live-20261019-d16d';ea=json.loads((ecp/'preflight/EVIDENCE_AUDIT.json').read_text())
for rel,h in {'RESULT.json':ea['rawResultSha256'],'MANIFEST.json':ea['rawManifestSha256'],'managed-sdk/build-api/results.json':ea['managed']['actualResultSha256']}.items():
 p=eprior/rel;assert sha(p)==h;old.append(dict(path=str(p),sha256=h))
old.append(dict(path=str(ecp/'MANIFEST.sha256'),sha256=sha(ecp/'MANIFEST.sha256')))
for row in json.loads((eprior/'MANIFEST.json').read_text())['files']:
 p=eprior/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
escratch=O.parent/'Scratch-R03-P1-EMPTY-LIVE-20261019-d16d';ei=json.loads((eprior/'native-sdk/native-sdk-inputs.json').read_text())['files']
for row in ei:assert sha(escratch/row['path'])==row['sha256']
save('CONSUMED_EMPTY_BEFORE.json',dict(result='Preserved',rawRoot=str(eprior),scratchRoot=str(escratch),regularFilesVerified=len(json.loads((eprior/'MANIFEST.json').read_text())['files']),scratchInputsVerified=len(ei),priorOutcome='PassedSourceHostAndSDKOnly',priorSourceFindingState='SourceConfirmed_NotFaultInjected',historicalValidationRerun=False))
prior_finding=ecp/'FINDING.json';pf=json.loads(prior_finding.read_text());assert pf['id']=='IR-LOCAL-P1-EMPTY-LIVE-RECEIPT-01' and pf['status']=='SourceConfirmed_NotFaultInjected' and pf['observedCurrentBatchFault'] is False
old.append(dict(path=str(prior_finding),sha256=sha(prior_finding)))
old_source_bindings=[]
for row in pf['sourceEvidence']:
 q=Path(row['path']);relative=q.relative_to(W);repo=relative.parts[0];rel=str(Path(*relative.parts[1:]));raw=subprocess.check_output(['git','-C',str(W/repo),'show',pf['executionPins'][repo]+':'+rel]);assert hashlib.sha256(raw).hexdigest()==row['sha256'];old_source_bindings.append(dict(repo=repo,path=rel,commit=pf['executionPins'][repo],sha256=row['sha256']))
save('PRIOR_FINDING_BEFORE.json',dict(result='HistoricalFindingAndSourceGitObjectsAuthenticated',findingId=pf['id'],originalStatus=pf['status'],path=str(prior_finding),sha256=sha(prior_finding),sourceBindings=old_source_bindings,originalSuccessfulBatchStillPass=True))
correction=[]
for repo,args in [('hybridclr_demo',['diff','--exit-code','465c14e660b576836f544da2b410dcb8b9e6c05f',E['pins']['hybridclr_demo'],'--','Tools/AssemblyShadow/R03/build_api.py','Tools/AssemblyShadow/R03/source-pins.json'])]:
 argv=['git','-C',str(W/repo),*args];start=now();r=subprocess.run(argv,capture_output=True,text=True);assert r.returncode==0 and not r.stdout;correction.append(dict(argv=argv,start=start,end=now(),exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
save('CORRECTION_SCOPE_BEFORE.json',dict(result='ManagedCompilerAndHistoricalPinsByteUnchanged',checks=correction,newNativePython=sha(W/'il2cpp_plus/tools/r03/diagnostic_stream/run_opaque_execution_inventory.py'),newOuterPython=sha(D/'Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py')))

receiptprior=O.parent/'R03-P1-EMPTY-LIVE-RECEIPT-20261019-48ee';receiptcp=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-empty-live-receipt-20261019-48ee';ra=json.loads((receiptcp/'preflight/EVIDENCE_AUDIT.json').read_text())
for rel,h in {'RESULT.json':ra['rawResultSha256'],'MANIFEST.json':ra['rawManifestSha256'],'managed-sdk/build-api/results.json':ra['managed']['actualResultSha256']}.items():
 p=receiptprior/rel;assert sha(p)==h;old.append(dict(path=str(p),sha256=h))
old.append(dict(path=str(receiptcp/'MANIFEST.sha256'),sha256=sha(receiptcp/'MANIFEST.sha256')))
for row in json.loads((receiptprior/'MANIFEST.json').read_text())['files']:
 p=receiptprior/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
rscratch=O.parent/'Scratch-R03-P1-EMPTY-LIVE-RECEIPT-20261019-48ee';ri=json.loads((receiptprior/'native-sdk/native-sdk-inputs.json').read_text())['files']
for row in ri:assert sha(rscratch/row['path'])==row['sha256']
save('CONSUMED_RECEIPT_BEFORE.json',dict(result='Preserved',rawRoot=str(receiptprior),scratchRoot=str(rscratch),regularFilesVerified=len(json.loads((receiptprior/'MANIFEST.json').read_text())['files']),scratchInputsVerified=len(ri),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))

def inventory(root):
 if not root.exists() and not root.is_symlink():return dict(path=str(root),exists=False,interpretation='AbsentOnly_NoInferredExecutionOutcome')
 rows=[]
 for q in [root,*sorted(root.rglob('*'))]:
  if q.is_symlink():rows.append(dict(path=str(q),kind='Symlink',target=os.readlink(q)))
  elif q.is_file():rows.append(dict(path=str(q),kind='Regular',bytes=q.stat().st_size,sha256=sha(q)))
 return dict(path=str(root),exists=True,files=rows)
superseded=[O.parent/n for n in ['R03-P1-OPAQUE-INVENTORY-20261019-5e23','Scratch-R03-P1-OPAQUE-INVENTORY-20261019-5e23','Preflight-R03-P1-OPAQUE-INVENTORY-20261019-5e23']]+[D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-opaque-inventory-20261019-5e23']
save('SUPERSEDED_ROOTS_BEFORE.json',dict(supersededUnconsumedHandoff='d4daea59682ffd14a8ff8b282c280733bcecb3d8',roots=[inventory(root) for root in superseded],noHistoricalResultInferred=True))
commits=subprocess.check_output(['git','-C',str(D),'rev-list','b2d6345f66fdf76456b5fab943f0737da4c62974..'+E['pins']['hybridclr_demo']],text=True).splitlines();percommit=[]
for commit in commits:
 names=subprocess.check_output(['git','-C',str(D),'diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines();assert all(x.startswith('Docs/') for x in names);percommit.append(dict(commit=commit,paths=names))
save('DOCS_ONLY_COMMITS.json',dict(anchor='b2d6345f66fdf76456b5fab943f0737da4c62974',commits=percommit))

opaqueprior=O.parent/'R03-P1-OPAQUE-LIFETIME-20261019-d548';opaquecp=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-opaque-lifetime-20261019-d548';oa=json.loads((opaquecp/'preflight/EVIDENCE_AUDIT.json').read_text())
for rel,h in {'RESULT.json':oa['rawResultSha256'],'MANIFEST.json':oa['rawManifestSha256'],'managed-sdk/build-api/results.json':oa['managed']['actualResultSha256']}.items():
 p=opaqueprior/rel;assert sha(p)==h;old.append(dict(path=str(p),sha256=h))
old.append(dict(path=str(opaquecp/'MANIFEST.sha256'),sha256=sha(opaquecp/'MANIFEST.sha256')))
for row in json.loads((opaqueprior/'MANIFEST.json').read_text())['files']:
 p=opaqueprior/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
opscratch=O.parent/'Scratch-R03-P1-OPAQUE-LIFETIME-20261019-d548';opi=json.loads((opaqueprior/'native-sdk/native-sdk-inputs.json').read_text())['files']
for row in opi:assert sha(opscratch/row['path'])==row['sha256']
save('CONSUMED_OPAQUE_BEFORE.json',dict(result='Preserved',rawRoot=str(opaqueprior),scratchRoot=str(opscratch),regularFilesVerified=len(json.loads((opaqueprior/'MANIFEST.json').read_text())['files']),scratchInputsVerified=len(opi),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))

revisionprior=O.parent/'R03-P1-REGISTRY-REVISION-20261020-f09e';revisioncp=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-registry-revision-20261020-f09e';rva=json.loads((revisioncp/'preflight/EVIDENCE_AUDIT.json').read_text())
for rel,h in {'RESULT.json':rva['rawResultSha256'],'MANIFEST.json':rva['rawManifestSha256'],'managed-sdk/build-api/results.json':rva['managed']['actualResultSha256']}.items():
 p=revisionprior/rel;assert sha(p)==h;old.append(dict(path=str(p),sha256=h))
old.append(dict(path=str(revisioncp/'MANIFEST.sha256'),sha256=sha(revisioncp/'MANIFEST.sha256')))
for row in json.loads((revisionprior/'MANIFEST.json').read_text())['files']:
 p=revisionprior/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
rvscratch=O.parent/'Scratch-R03-P1-REGISTRY-REVISION-20261020-f09e';rvi=json.loads((revisionprior/'native-sdk/native-sdk-inputs.json').read_text())['files']
for row in rvi:assert sha(rvscratch/row['path'])==row['sha256']
save('CONSUMED_REVISION_BEFORE.json',dict(result='Preserved',rawRoot=str(revisionprior),scratchRoot=str(rvscratch),regularFilesVerified=len(json.loads((revisionprior/'MANIFEST.json').read_text())['files']),scratchInputsVerified=len(rvi),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))
witness_roots=[O.parent/n for n in ['R03-P1-REGISTRATION-WITNESS-20261020-f0cb','Scratch-R03-P1-REGISTRATION-WITNESS-20261020-f0cb','Preflight-R03-P1-REGISTRATION-WITNESS-20261020-f0cb']]+[D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-registration-witness-20261020-f0cb']
save('SUPERSEDED_WITNESS_BEFORE.json',dict(supersededHandoff='04875be02778c024549730c6e2ef9b05a94fca44',roots=[inventory(root) for root in witness_roots],noHistoricalExecutionResultInferred=True))

publisherprior=O.parent/'R03-P1-REGISTRY-PUBLISHER-20261020-699d';publishercp=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-registry-publisher-20261020-699d';pua=json.loads((publishercp/'preflight/EVIDENCE_AUDIT.json').read_text())
for rel,h in {'RESULT.json':pua['rawResultSha256'],'MANIFEST.json':pua['rawManifestSha256'],'managed-sdk/build-api/results.json':pua['managed']['actualResultSha256']}.items():
 p=publisherprior/rel;assert sha(p)==h;old.append(dict(path=str(p),sha256=h))
old.append(dict(path=str(publishercp/'MANIFEST.sha256'),sha256=sha(publishercp/'MANIFEST.sha256')))
for row in json.loads((publisherprior/'MANIFEST.json').read_text())['files']:
 p=publisherprior/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
puscratch=O.parent/'Scratch-R03-P1-REGISTRY-PUBLISHER-20261020-699d';pui=json.loads((publisherprior/'native-sdk/native-sdk-inputs.json').read_text())['files']
for row in pui:assert sha(puscratch/row['path'])==row['sha256']
save('CONSUMED_PUBLISHER_BEFORE.json',dict(result='Preserved',rawRoot=str(publisherprior),scratchRoot=str(puscratch),regularFilesVerified=len(json.loads((publisherprior/'MANIFEST.json').read_text())['files']),scratchInputsVerified=len(pui),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))
physical_roots=[O.parent/n for n in ['R03-P1-PHYSICAL-MEMBERSHIP-20261020-52d0','Scratch-R03-P1-PHYSICAL-MEMBERSHIP-20261020-52d0','Preflight-R03-P1-PHYSICAL-MEMBERSHIP-20261020-52d0']]+[D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-physical-membership-20261020-52d0']
save('SUPERSEDED_PHYSICAL_BEFORE.json',dict(supersededHandoff='d0bde05d2eb55da52c4ab35f4504d00897f951c5',roots=[inventory(root) for root in physical_roots],noHistoricalExecutionResultInferred=True))
owned_runner=N/'tools/r03/diagnostic_stream/run_owned_physical_names.py';owned_tree=ast.parse(owned_runner.read_text());owned_gate=next(n for n in owned_tree.body if isinstance(n,ast.FunctionDef) and n.name=='verify');ol={}
for node in owned_gate.body:
 if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
  try:ol[node.targets[0].id]=ast.literal_eval(node.value)
  except (ValueError,TypeError):pass
actualcpp=(N/'libil2cpp/vm/AssemblyShadow.cpp').read_text();actualapi=(N/'libil2cpp/vm/AssemblyShadow.h').read_text();ph=(N/'libil2cpp/vm/AssemblyShadowPhysicalMembership.h').read_text()
for value in [ol['include'],ol['inline_block']]:assert actualcpp.count(value)==1
assert actualcpp.count('TryCaptureOwnedObservedPhysicalNames(')==0
restoredcpp=actualcpp.replace(ol['include']+'\n','').replace(ol['inline_block'],'');restoredapi=actualapi.replace(ol['forward'],'').replace(ol['declaration'],'')
binding=next(ast.literal_eval(n.value) for n in owned_tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REGISTRATION_BINDING_BLOCK' for t in n.targets));assert ph.count(binding)==1
restoredph=ph.replace(binding,'').replace(ol['enumAdded'],'').replace(ol['newEnumeration'],ol['oldEnumeration'])
owned_originals=[]
for rel,raw,blob in [('libil2cpp/vm/AssemblyShadow.cpp',restoredcpp.encode(),'46240c58f83f1ce1a048266ed3bf421af4197567'),('libil2cpp/vm/AssemblyShadow.h',restoredapi.encode(),'55b1be3a134b41652fd88e24d8d548e5ca98126e'),('libil2cpp/vm/AssemblyShadowPhysicalMembership.h',restoredph.encode(),'375d9225bfbb7be693b15ffc7fc7203b48e45d92')]:
 original=subprocess.check_output(['git','-C',str(N),'cat-file','blob',blob]);assert raw==original;owned_originals.append(dict(path=rel,originalBlob=blob,originalSha256=hashlib.sha256(raw).hexdigest(),candidateSha256=sha(N/rel)))
save('OWNED_SOURCE_BINDING_BEFORE.json',dict(result='ExactReviewedAdditionsAndFirstMatchChangeAuthenticated',originals=owned_originals,methodSha256=sha(N/'libil2cpp/vm/AssemblyShadowOwnedPhysicalNamesSource.inl'),headerSha256=sha(N/'libil2cpp/vm/AssemblyShadowOwnedPhysicalNames.h'),noNormalCppCaller=True))

namesprior=O.parent/'R03-P1-OWNED-PHYSICAL-NAMES-20261020-e6a3';namescp=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-owned-physical-names-20261020-e6a3';na=json.loads((namescp/'preflight/EVIDENCE_AUDIT.json').read_text())
for rel,h in {'RESULT.json':na['rawResultSha256'],'MANIFEST.json':na['rawManifestSha256'],'managed-sdk/build-api/results.json':na['managed']['actualResultSha256']}.items():
 q=namesprior/rel;assert sha(q)==h;old.append(dict(path=str(q),sha256=h))
old.append(dict(path=str(namescp/'MANIFEST.sha256'),sha256=sha(namescp/'MANIFEST.sha256')))
for row in json.loads((namesprior/'MANIFEST.json').read_text())['files']:
 q=namesprior/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['size']
nss=O.parent/'Scratch-R03-P1-OWNED-PHYSICAL-NAMES-20261020-e6a3';nsi=json.loads((namesprior/'native-sdk/native-sdk-inputs.json').read_text())['files']
for row in nsi:assert sha(nss/row['path'])==row['sha256']
save('CONSUMED_NAMES_BEFORE.json',dict(result='Preserved',rawRoot=str(namesprior),scratchRoot=str(nss),regularFilesVerified=len(json.loads((namesprior/'MANIFEST.json').read_text())['files']),scratchInputsVerified=len(nsi),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))
checkpoints=[]
for row in old:
 q=Path(row['path'])
 if q.name!='MANIFEST.sha256':continue
  # Authenticate every bounded checkpoint text copy, including Local historical reports.
 entries=[]
 for line in q.read_text().splitlines():
  h,rel=line.split('  ',1);f=q.parent/rel;assert sha(f)==h;entries.append(dict(path=rel,sha256=h,bytes=f.stat().st_size))
 checkpoints.append(dict(root=str(q.parent),manifestSha256=sha(q),files=entries))
assert len(checkpoints)==15
save('CHECKPOINTS_BEFORE.json',dict(result='Preserved',count=len(checkpoints),checkpoints=checkpoints))

# Four deliberate symlink controls in each consumed P1 manifest remain separate from regular inventory.
prior_links=[]
for root in [consumed,passed,firstuse,owned,lprior,cmdprior,fprior,eprior,receiptprior,opaqueprior,revisionprior,publisherprior,namesprior]:
 for row in json.loads((root/'legacy-host/MANIFEST.json').read_text())['files']:
  if row.get('kind')=='Symlink':
   q=root/'legacy-host'/row['path'];assert q.is_symlink() and os.readlink(q)==row['target'];prior_links.append(dict(path=str(q),target=row['target']))
save('HISTORICAL_SYMLINKS_BEFORE.json',dict(result='Preserved',bindings=prior_links))

save('PRIOR_EVIDENCE_BEFORE.json',old)
for root in [O,S]:assert not root.exists() and not root.is_symlink() and root.resolve()==root
argv=['python3','-B',str(D/'Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py'),'--workspace',str(W),'--unity',str(U),'--expected-demo',E['pins']['hybridclr_demo'],'--expected-native',E['pins']['il2cpp_plus'],'--output',str(O),'--sdk-scratch',str(S)]
rec=dict(argv=argv,cwd=str(D),start=now(),platform=platform.platform(),TMPDIR=os.environ.get('TMPDIR'),CXX=os.environ.get('CXX'),outputAndScratchInitiallyAbsent=True,unityAnchorOnly=True);save('INVOCATION.json',rec)
with (P/'stdout.bin').open('xb') as out,(P/'stderr.bin').open('xb') as err:
 proc=subprocess.Popen(argv,cwd=D,stdout=out,stderr=err,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});rec['pid']=proc.pid;rec['exit']=proc.wait()
rec.update(end=now(),stdoutSha256=sha(P/'stdout.bin'),stderrSha256=sha(P/'stderr.bin'));save('RECEIPT.json',rec);print(json.dumps(rec,indent=2));print((P/'stdout.bin').read_text());print((P/'stderr.bin').read_text())
