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
for n,paths in {'hybridclr_demo':['Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowExecutionEmptyLiveSyntax.cpp','Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowExecutionComposeSyntax.cpp','Tools/AssemblyShadow/R03IR/run_p1_command_failure_tests.py','Tools/AssemblyShadow/R03IR/test_p1_command_failures.py','Tools/AssemblyShadow/R03IR/test_p1_metadata_preflight.py','Tools/AssemblyShadow/R03IR/test_p1_managed_receipt.py','Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowGeneralComposeSyntax.cpp','Tools/AssemblyShadow/R03/source-pins.json','Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py','Tools/AssemblyShadow/R03IR/run_primary_host_preflight.py','Tools/AssemblyShadow/R03/native_validation.py','Tools/AssemblyShadow/R03/build_api.py','Tools/AssemblyShadow/R03/input_validation.py','Packages/manifest.json','Packages/packages-lock.json','ProjectSettings/ProjectVersion.txt'],'il2cpp_plus':['tools/r03/diagnostic_stream/test_bounded_execution_empty_live_receipts.py','libil2cpp/vm/AssemblyShadowBoundedExecutionEmptyLive.h','libil2cpp/vm/AssemblyShadowBoundedExecutionEmptyLiveSource.inl','tools/r03/diagnostic_stream/run_bounded_execution_empty_live.py','tools/r03/diagnostic_stream/empty_live_fixture/MockRuntime.h','tools/r03/diagnostic_stream/empty_live_fixture/AssemblyShadowFrozenExecutionRecord.h','tools/r03/diagnostic_stream/empty_live_fixture/AssemblyShadowMetadataLifetime.h','tools/r03/diagnostic_stream/empty_live_fixture/fixture.cpp','libil2cpp/vm/AssemblyShadowFrozenExecutionRecord.h','libil2cpp/vm/AssemblyShadowR02Snapshot.h','libil2cpp/vm/AssemblyShadowFrozenR02Serializer.h','tools/r03/diagnostic_stream/run_frozen_execution.py','tools/r03/diagnostic_stream/frozen_execution_fixture.cpp','tools/r03/diagnostic_stream/frozen_execution_allocations.cpp','tools/r03/diagnostic_stream/reference/AssemblyShadowExecutionSerializer.h','tools/r03/diagnostic_stream/reference/AssemblyShadowR02Diagnostics.h','tools/r03/diagnostic_stream/test_frozen_execution_include_path.py','tools/r03/diagnostic_stream/test_bounded_general_live_command.py','libil2cpp/vm/AssemblyShadowBoundedGeneralLive.h','libil2cpp/vm/AssemblyShadowBoundedGeneralLiveSource.inl','libil2cpp/vm/AssemblyShadow.h','tools/r03/diagnostic_stream/run_bounded_general_live.py','tools/r03/diagnostic_stream/bounded_general_live_fixture.cpp','libil2cpp/vm/AssemblyShadowBoundedGeneralComposer.h','libil2cpp/vm/AssemblyShadowFrozenGeneralCapture.h','tools/r03/diagnostic_stream/run_bounded_general_composer.py','tools/r03/diagnostic_stream/bounded_general_composer_fixture.cpp','libil2cpp/vm/AssemblyShadow.cpp','libil2cpp/vm/AssemblyShadowBoundedFirstUseCapture.h','tools/r03/diagnostic_stream/run_bounded_first_use.py','tools/r03/diagnostic_stream/bounded_first_use_fixture.cpp','libil2cpp/vm/AssemblyShadowMetadataLifetime.h','libil2cpp/vm/Runtime.cpp','libil2cpp/vm/Assembly.cpp','libil2cpp/vm/AssemblyShadowVisibility.cpp','tools/r03/diagnostic_stream/run_metadata_lifetime_gate.py']}.items():
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
N=W/'il2cpp_plus';old_cpp=subprocess.check_output(['git','-C',str(N),'show','f0c5afe43fe256ac09fabacd5d40f82956988fe2:libil2cpp/vm/AssemblyShadow.cpp']);new_cpp=(N/'libil2cpp/vm/AssemblyShadow.cpp').read_bytes()
insert1=b'#include "AssemblyShadowBoundedExecutionEmptyLive.h"\n';insert2=b'// P1 inactive execution R02 source; exact bounded zero-class subset only.\n#include "AssemblyShadowBoundedExecutionEmptyLiveSource.inl"\n'
assert new_cpp.count(insert1)==new_cpp.count(insert2)==1 and new_cpp.replace(insert1,b'',1).replace(insert2,b'',1)==old_cpp
save('EMPTY_SOURCE_BINDING_BEFORE.json',dict(result='OriginalCppAndGettersBytePreservedExceptThreeAdditiveLines',baseline='f0c5afe43fe256ac09fabacd5d40f82956988fe2',candidate=E['pins']['il2cpp_plus'],baselineCppSha256=hashlib.sha256(old_cpp).hexdigest(),candidateCppSha256=hashlib.sha256(new_cpp).hexdigest(),originalGettersUnchanged=True,sourceMethodSha256=sha(N/'libil2cpp/vm/AssemblyShadowBoundedExecutionEmptyLiveSource.inl'),headerSha256=sha(N/'libil2cpp/vm/AssemblyShadowBoundedExecutionEmptyLive.h'),removingOnlyNewHeaderIncludeCommentAndMethodIncludeReconstructsEveryOriginalCppByte=True))


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
for repo,args in [('il2cpp_plus',['diff','--exit-code','d16d2f7eee4c0f2333f31c4ec6e40422956d8fd1',E['pins']['il2cpp_plus'],'--','libil2cpp']),('hybridclr_demo',['diff','--exit-code','8514c03cce722c0b036267552ba026ecb548edaa',E['pins']['hybridclr_demo'],'--','Tools/AssemblyShadow/R03/build_api.py','Tools/AssemblyShadow/R03/native_validation.py','Tools/AssemblyShadow/R03/source-pins.json'])]:
 argv=['git','-C',str(W/repo),*args];start=now();r=subprocess.run(argv,capture_output=True,text=True);assert r.returncode==0 and not r.stdout;correction.append(dict(argv=argv,start=start,end=now(),exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
save('CORRECTION_SCOPE_BEFORE.json',dict(result='ProductionNativeAndCompilerPoliciesByteUnchanged',checks=correction,newNativePython=sha(W/'il2cpp_plus/tools/r03/diagnostic_stream/run_bounded_execution_empty_live.py'),newOuterPython=sha(D/'Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py'),newNativeTests=sha(W/'il2cpp_plus/tools/r03/diagnostic_stream/test_bounded_execution_empty_live_receipts.py')))

# Four deliberate symlink controls in each consumed P1 manifest remain separate from regular inventory.
prior_links=[]
for root in [consumed,passed,firstuse,owned,lprior,cmdprior,fprior,eprior]:
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
