from pathlib import Path
import json,hashlib,os,subprocess,concurrent.futures,datetime,collections
P=Path(__file__).resolve().parent;E=json.loads((P/'EXPECTED.json').read_text());W=Path(E['workspace']);D=W/'hybridclr_demo';O=Path(E['output']);S=Path(E['scratch'])
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def load(p):
 def pairs(items):
  d={}
  for k,v in items:
   if k in d:raise ValueError('Duplicate key '+k+' in '+str(p))
   d[k]=v
  return d
 def constant(v):raise ValueError('Nonfinite '+v+' in '+str(p))
 return json.loads(p.read_text(),object_pairs_hook=pairs,parse_constant=constant)
def save(n,x):(P/n).write_text(json.dumps(x,indent=2)+'\n')
r=load(O/'RESULT.json');assert r['result']=='PassedSourceHostAndSDKOnly' and r['sourcePreserved'] and len(r['commands'])==15 and r['expectedNativeSyntaxUnits']==85 and r['postflightError'] is None and all(c['status']=='Passed' for c in r['commands']) and r['officialUnitySdkCompileAttempted'] is True and r['officialUnitySdkCompilePassed'] is True
manifest=load(O/'MANIFEST.json')['files']
for row in manifest:
 p=O/row['path'];assert '..' not in Path(row['path']).parts and p.is_file() and not p.is_symlink() and p.stat().st_size==row['size'] and sha(p)==row['sha256']
assert {str(p.relative_to(O)) for p in O.rglob('*') if p.is_file() and not p.is_symlink()}=={x['path'] for x in manifest}|{'MANIFEST.json'}
links=[dict(path=str(p.relative_to(O)),target=os.readlink(p)) for p in O.rglob('*') if p.is_symlink()];legacy=O/'legacy-host';lm=load(legacy/'MANIFEST.json')['files'];ls=[dict(path='legacy-host/'+x['path'],target=x['target']) for x in lm if x.get('kind')=='Symlink'];assert sorted(links,key=str)==sorted(ls,key=str)
for c in r['commands']:
 assert load(O/'commands'/(c['name']+'.json'))==c
 for stream in ['stdout','stderr']:assert sha(O/'commands'/c['name']/(stream+'.bin'))==c[stream+'.binSha256']
for path,h in r['sourceSha256'].items():assert sha(Path(path))==h
stream_receipts=0
for p in O.rglob('*.json'):
 if p.name!='command.json' and not p.name.endswith('.command.json'):continue
 c=load(p)
 if 'stdoutSha256' not in c:continue
 for stream in ['stdout','stderr']:
  if p.name=='command.json':candidates=[p.parent/(stream+s) for s in ['.bin','.log','']]
  else:prefix=p.name[:-len('command.json')];candidates=[p.parent/(prefix+stream+s) for s in ['.bin','']]
  matched=[q for q in candidates if q.is_file() and not q.is_symlink() and sha(q)==c[stream+'Sha256']];assert matched,(str(p),stream)
 stream_receipts+=1
summaries={}
for name in ['metadata-gate','bounded-class','bounded-physical','bounded-first-use','bounded-status','bounded-inventory','frozen-v2','owned-general','live-general']:
 c=load(O/name/'RESULT.json');assert c['result'] in ['PassedWithinHostScope','PassedWithinInactiveHostScope','PassedWithinOwnedHostScope','PassedWithinInactiveSourceHostScope'];summaries[name]={k:c[k] for k in ['result','profilesCompleted','completedProfiles','profiles','sourcePreserved','sourceUnchanged','firstError','firstFailure','sourceContract'] if k in c};summaries[name]['commandCount']=len(c['commands'])
lr=load(legacy/'RESULT.json');assert lr['result']=='PassedHostOnly' and lr['sourcePreserved'] and len(lr['commands'])==8 and all(x['status']=='Passed' for x in lr['commands'])
general=load(legacy/'native-general-stream/evidence/RESULT.json');assert general['result']=='PassedWithinHostScope' and general['oldExecutionProducer']==general['currentExecutionProducer']=='Passed' and all(x['tests']==25 and not(x['failures'] or x['errors'] or x['skipped']) for x in general['profiles'])
pr=legacy/'native-general-stream/evidence/current-execution-parity';parity=load(pr/'RESULT.json');assert len(parity['cases'])==6 and len(parity['commands'])==24 and parity['result']=='PassedHostOnly'
for c in parity['cases']:
 a=pr/(c['profile']+'-'+c['variant']+'-frozen.json');b=pr/(c['profile']+'-'+c['variant']+'-current.json');assert a.read_bytes()==b.read_bytes() and sha(a)==sha(b)==c['sha256'] and a.stat().st_size==c['bytes']
managed=load(O/'managed-sdk/build-api/results.json');mc=next(x for x in r['commands'] if x['name']=='managed-sdk');assert managed['result']=='Passed' and mc['exit']==0 and mc['status']=='Passed' and mc['innerResult']=='Passed' and mc['returnedBindingVerified'] is True and mc['innerResultPath']==str(O/'managed-sdk/build-api/results.json') and mc['innerResultSha256']==sha(O/'managed-sdk/build-api/results.json') and not (O/'managed-sdk/results.json').exists()
stdout=load(O/'commands/managed-sdk/stdout.bin');assert stdout['result']==str(O/'managed-sdk/build-api/results.json') and stdout['sha256']==sha(O/'managed-sdk/build-api/results.json') and set(stdout)=={'result','sha256'}
assert managed['kind']=='R03CompleteBuildHelperCompile' and type(managed['schemaVersion']) is int and managed['schemaVersion']==1 and managed['unityVersion']=='2022.3.62f2' and all(managed[k] is False for k in ['unityEditorRun','nativeExecution','runtimeAcceptance'])
mp=O/'managed-sdk/build-api/results.json';assert mp.resolve()==mp and not mp.is_symlink()
def binding(b):p=Path(b['path']);assert p.is_file() and sha(p)==b['sha256'];assert p.stat().st_size==b.get('size',p.stat().st_size)
for b in managed['inputs']:binding(b)
products=[x['output'] for x in managed['packageAssemblies']]+[managed['completeHelper'],managed['terminalPlayerApi']['output']];assert len(products)==5
for b in products:binding(b)
expected=[]
for c in managed['commands']:
 binding(c['receipt']);binding(c['response']);p=Path(c['receipt']['path']);cr=load(p);assert cr['exitCode']==c['expectedExit'] and not cr['remainingProcessGroup'] and not cr['postCleanupGroupExists'] and not cr['timeout']
 if c['expectedExit']:
  text=(p.parent/'stdout.log').read_text()+(p.parent/'stderr.log').read_text();assert text.count('error CS0266:')==2;assert not (O/'managed-sdk/build-api/OriginalUnsignedCounts/OriginalUnsignedCounts.dll').exists();expected.append(dict(id=c['id'],exit=cr['exitCode'],CS0266Errors=2))
assert len(managed['commands'])==6 and len(expected)==1
native=load(O/'native-sdk/results.json');assert native['result']=='Passed' and native['candidateNativeSha']==E['pins']['il2cpp_plus'] and native['plannedTranslationUnitCount']==85 and len(native['translationUnits'])==85
cmds={}
for p in (O/'native-sdk/commands').glob('*/command.json'):
 c=load(p);assert c['exitCode']==0 and not c['remainingProcessGroup'] and not c['postCleanupGroupExists'] and not c['timeout'];cmds[sha(p)]=c
pairs=set()
for t in native['translationUnits']:
 src=Path(t['source']);assert sha(src)==t['sha256'];c=cmds[t['commandReceipt']];assert '-fsyntax-only' in c['command'] and '-std=c++17' in c['command'] and c['command'][c['command'].index('-arch')+1]=='arm64' and c['command'][-1]==str(src);pairs.add((t['profile'],src.name))
assert len(pairs)==85 and len({x[1] for x in pairs})==17 and len({x[0] for x in pairs})==5
sdk_inputs=load(O/'native-sdk/native-sdk-inputs.json')['files']
for b in sdk_inputs:assert sha(S/b['path'])==b['sha256']
for b in native['sources']:assert sha(W/b['path'])==b['sha256']
war={}
for sub in ['managed-sdk','native-sdk']:
 rows=[]
 for p in (O/sub/'commands').glob('*/*.log'):
  data=p.read_text(errors='replace');lines=[l for l in data.splitlines() if 'warning:' in l or 'warning CS' in l or ': error:' in l or 'error CS' in l]
  if lines:rows.append(dict(path=str(p),sha256=sha(p),warningCount=sum('warning:' in l or 'warning CS' in l for l in lines),errorCount=sum(': error:' in l or 'error CS' in l for l in lines),excerpts=lines))
 war[sub]=dict(warnings=sum(x['warningCount'] for x in rows),errors=sum(x['errorCount'] for x in rows),streams=rows)
save('COMPILER_DIAGNOSTICS.json',war)
before=load(P/'SDK_BEFORE.json');actual=set([before['anchor'],str(Path(before['anchor']).parent.parent/'Info.plist')])
for root in before['roots']:actual.update(str(p) for p in Path(root).rglob('*') if p.is_file())
assert actual=={b['path'] for b in before['files']}
for b in before['files']:
 p=Path(b['path']);assert p.stat().st_size==b['bytes'] and sha(p)==b['sha256'] and (os.readlink(p) if p.is_symlink() else None)==b['symlink']
save('SDK_AFTER.json',dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),result='Preserved',beforeReceiptSha256=sha(P/'SDK_BEFORE.json'),verifiedFiles=len(before['files']),verifiedBytes=sum(b['bytes'] for b in before['files']),noMissingExtraOrModifiedInputs=True,unityNeverLaunched=True))
for b in load(P/'SOURCE_BINDINGS.json'):assert sha(Path(b['path']))==b['sha256']
prior=load(P/'PRIOR_EVIDENCE_BEFORE.json')
for b in prior:assert sha(Path(b['path']))==b['sha256']
save('PRIOR_EVIDENCE_AFTER.json',dict(result='PreservedManifestIdentities',bindings=prior,previousHostFailAndPassUnchanged=True,fullHistoricalCustodyOrRuntimeRevalidation='NotRun'))

consumed=O.parent/'R03-P1-METADATA-SOURCE-20261016-0a0b'
for row in load(consumed/'MANIFEST.json')['files']:
 p=consumed/row['path'];assert p.stat().st_size==row['size'] and sha(p)==row['sha256']
old_native=load(consumed/'native-sdk/native-sdk-inputs.json')['files'];prior_scratch=O.parent/'Scratch-R03-P1-METADATA-20261016-0a0b'
for row in old_native:assert sha(prior_scratch/row['path'])==row['sha256']
assert load(consumed/'RESULT.json')['result']=='FailedOrIncomplete' and load(consumed/'RESULT.json')['officialUnitySdkCompilePassed'] is False
save('CONSUMED_AFTER.json',dict(result='Preserved',regularFilesVerified=len(load(consumed/'MANIFEST.json')['files']),nativeScratchInputsVerified=len(old_native),priorAggregateResult='FailedOrIncomplete',priorSdkAggregateFlag=False,originalRawAndScratchReused=False,consumedRoot=str(consumed),scratchRoot=str(prior_scratch)))


passed=O.parent/'R03-P1-MANAGED-RECEIPT-20261016-0620';pi=load(passed/'native-sdk/native-sdk-inputs.json')['files'];ps=O.parent/'Scratch-R03-P1-MANAGED-RECEIPT-20261016-0620'
for row in load(passed/'MANIFEST.json')['files']:
 q=passed/row['path'];assert q.stat().st_size==row['size'] and sha(q)==row['sha256']
for row in pi:assert sha(ps/row['path'])==row['sha256']
assert load(passed/'RESULT.json')['result']=='PassedSourceHostAndSDKOnly'
save('CONSUMED_PASS_AFTER.json',dict(result='Preserved',rawRoot=str(passed),scratchRoot=str(ps),regularFilesVerified=len(load(passed/'MANIFEST.json')['files']),scratchInputsVerified=len(pi),priorOutcome='PassedSourceHostAndSDKOnly',noPriorConsumerOrRuntimeRerun=True))
first=load(O/'bounded-first-use/RESULT.json');assert first['result']=='PassedWithinHostScope' and first['methodSha256']=='67fcd9f6660c67c8a60ed610cdc9b3c3cfc06adb01f9805a581e6dd97dd42be2'
first_expected=['classless-ownership','existing-fail-closed','existing-capacity-phase','existing-token-contract','classless-general-parity','class-ownership','null-absent-names','cstring-budget','cstring-alias','owner-unavailable','usage-after-metadata','shutdown-drain','dense-general-parity','unresolved-refusal','parallel-captures']
for profile in ['strict','sanitized']:
 labels=[line[5:] for line in (O/'bounded-first-use'/(profile+'-run.stdout')).read_text().splitlines() if line.startswith('PASS ')];assert labels==first['caseGroups'][profile]==first_expected and len(set(labels))==15
assert len(first['commands'])==4 and all(c['exit']==0 for c in first['commands']) and first['sourcePreserved'] and first['metadataAdmissionAndNonNestedLocksCheckedUnderMocks'] and first['classBearingSourceContractPassedUnderMocks'] and first['realPlayerRun'] is False
for path,row in first['sourceBefore'].items():
 q=Path(path);data=q.read_bytes();assert len(data)==row['bytes'] and sha(q)==row['sha256'] and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['gitBlob']
save('FIRST_USE_VERIFICATION.json',dict(result='PassedWithinFirstUseHostScope',methodSha256=first['methodSha256'],profiles=first['profilesCompleted'],caseGroups=first['caseGroups'],fourCompileRunReceiptsVerified=True,realClassMetadataProven=False,contract='Physical namespace-dot-name including .Class; copied ownership;4096 row limit; nonnested usage/metadata locks; initial epoch only; generation/mutation/overflow/null/alias controls under explicit mocks',sourceInputs=first['sourceBefore'],sourcePreserved=True))


firstuse=O.parent/'R03-P1-FIRSTUSE-CLASS-20261016-f598';fi=load(firstuse/'native-sdk/native-sdk-inputs.json')['files'];fs=O.parent/'Scratch-R03-P1-FIRSTUSE-CLASS-20261016-f598'
for row in load(firstuse/'MANIFEST.json')['files']:
 q=firstuse/row['path'];assert q.stat().st_size==row['size'] and sha(q)==row['sha256']
for row in fi:assert sha(fs/row['path'])==row['sha256']
assert load(firstuse/'RESULT.json')['result']=='PassedSourceHostAndSDKOnly'
save('CONSUMED_FIRSTUSE_AFTER.json',dict(result='Preserved',rawRoot=str(firstuse),scratchRoot=str(fs),regularFilesVerified=len(load(firstuse/'MANIFEST.json')['files']),scratchInputsVerified=len(fi),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))
owned=load(O/'owned-general/RESULT.json');assert owned['result']=='PassedWithinOwnedHostScope' and owned['sourcePreserved'] and owned['firstError'] is None and owned['actualProductionHeadersCompiled'] and owned['legacySerializerSameSourceCompiled']
composer_groups=['byte-exact-general-owned-parity','composition-no-new-allocation','missing-source-fail-closed','incomplete-source-fail-closed','cross-reader-generation-mismatch','startup-source-bounds','invalid-borrowed-startup-refusal','complete-output-budget-refusal','invalid-utf8-refusal','single-owner-single-freeze','no-coherent-vm-epoch-or-player-claim']
for profile in ['strict','sanitized']:
 text=(O/'owned-general'/(profile+'-run.stdout.bin')).read_text();labels=[line[len('GROUP:'):] for line in text.splitlines() if line.startswith('GROUP:')]
 assert labels==owned['profiles'][profile]['cases']==composer_groups and len(set(labels))==11
 assert [x for x in text.splitlines() if x.startswith('ALLOCATIONS_AFTER_PREWARM:')]==['ALLOCATIONS_AFTER_PREWARM:0'] and owned['profiles'][profile]['allocationsAfterPrewarm']==0 and text.rstrip().endswith('P1 BOUNDED GENERAL COMPOSER HOST PASS')
assert len(owned['commands'])==4 and all(c['exit']==0 for c in owned['commands']) and owned['sourceContract']['globalVmEpochProven'] is False and owned['allVmEpochProven'] is False and owned['runtimeAcceptance'] is False and owned['originalLiveGettersReplaced'] is False
for rel,row in owned['sourceBefore'].items():
 q=W/'il2cpp_plus'/rel;data=q.read_bytes();assert len(data)==row['bytes'] and sha(q)==row['sha256'] and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['gitBlob']
assert 'AssemblyShadowGeneralComposeSyntax.cpp' in {p[1] for p in pairs}
save('OWNED_GENERAL_VERIFICATION.json',dict(result='PassedWithinOwnedHostAndSDKSyntaxScope',profiles=owned['profiles'],fourCompileRunReceiptsVerified=True,sourceContract=owned['sourceContract'],sourceInputs=owned['sourceBefore'],actualHeadersAndLegacySerializerCompiled=True,sourcePreserved=True,frozenGeneralCapacity=3932160,globalVmEpochProven=False,runtimeAcceptance=False,standaloneSdkProbe='AssemblyShadowGeneralComposeSyntax.cpp',all85NativeConfigurationsVerified=True))

owned_prior=O.parent/'R03-P1-OWNED-GENERAL-20261016-3dc9';oi=load(owned_prior/'native-sdk/native-sdk-inputs.json')['files'];oscratch=O.parent/'Scratch-R03-P1-OWNED-GENERAL-20261016-3dc9'
for row in load(owned_prior/'MANIFEST.json')['files']:
 q=owned_prior/row['path'];assert q.stat().st_size==row['size'] and sha(q)==row['sha256']
for row in oi:assert sha(oscratch/row['path'])==row['sha256']
assert load(owned_prior/'RESULT.json')['result']=='PassedSourceHostAndSDKOnly'
save('CONSUMED_OWNED_AFTER.json',dict(result='Preserved',rawRoot=str(owned_prior),scratchRoot=str(oscratch),regularFilesVerified=len(load(owned_prior/'MANIFEST.json')['files']),scratchInputsVerified=len(oi),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))
for n in ['R03-PRIMARY-HOST-ONLY-20261015-fc0d3565','R03-PRIMARY-HOST-ONLY-20261015-74dbdbea-a1']:
 root=O.parent/n
 for row in load(root/'MANIFEST.json')['files']:
  q=root/row['path']
  if row.get('kind')=='Symlink':assert q.is_symlink() and os.readlink(q)==row['target']
  else:assert sha(q)==row['sha256'] and q.stat().st_size==row['size']
save('HISTORICAL_HOST_AFTER.json',dict(result='Preserved',allOriginalManifestEntriesVerified=True))
live=load(O/'live-general/RESULT.json');assert live['result']=='PassedWithinInactiveSourceHostScope' and live['sourcePreserved'] and live['firstError'] is None and live['compiledExactProductionSource'] and live['compiledActualBoundedSourcesAndSerializer']
lgroups=['actual-method-legacy-v1-parity','actual-method-zero-new-after-prewarm','missing-owned-source-denied','transaction-source-failure','first-use-source-failure','physical-assembly-source-failure','ordinary-class-source-failure','usage-generation-changed-during-read','usage-generation-changed-during-compose','terminal-state-changed-during-read','bounded-startup-scan-refusal','single-owner-one-shot-output','closed-metadata-admission-refusal']
assert live['sourceMethodSha256']=='232bd739bc6a54e8047118fbba8eb301a58f67e869ca8ce974902c8c382244a8'
assert sha(O/'live-general/actual-source.inl')==live['sourceMethodSha256']==sha(W/'il2cpp_plus/libil2cpp/vm/AssemblyShadowBoundedGeneralLiveSource.inl')
for profile in ['strict','sanitized']:
 text=(O/'live-general'/(profile+'-run.stdout.bin')).read_text();labels=[line[len('GROUP:'):] for line in text.splitlines() if line.startswith('GROUP:')]
 assert labels==live['caseGroups'][profile]['caseGroups']==lgroups and len(set(labels))==13 and text.rstrip().endswith('P1 REAL GENERAL LIVE SOURCE METHOD HOST PASS')
assert len(live['commands'])==4 and all(c['exit']==0 for c in live['commands'])
assert live['postflightError'] is None and live['observedSourceHashesEqual'] is True and live['sourceBefore']==live['sourceAfter'] and live['commandLifetimeUnverified'] is False and live['descendantQuiescenceProven'] is False
for c in live['commands']:
 assert c['commandLifetimeUnverified'] is False and c['descendantQuiescenceProven'] is False and c['timedOut'] is False and c['interrupted'] is False and c['outputCompleteness']=='CompleteDirectChildStreams'
 for stream in ['stdout','stderr']:
  q=O/'live-general'/(c['name']+'.'+stream+'.bin');assert c[stream+'Available'] is True and c[stream+'CapturedBytes']==q.stat().st_size and sha(q)==c[stream+'Sha256']
for flag in ['coherentVmEpochProven','nativeClassPointerOriginProven','realShutdownDeadlockFreedomProven','originalLiveGettersReplaced','runtimeAcceptance','realEngineMetadataGate','fullRuntimeAllocationGcRssProven','officialUnitySdkCompiled','playerExecuted']:assert live[flag] is False
for rel,row in live['sourceBefore'].items():
 q=W/'il2cpp_plus'/rel;data=q.read_bytes();assert len(data)==row['bytes'] and sha(q)==row['sha256'] and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['gitBlob']
fixture=(W/'il2cpp_plus/tools/r03/diagnostic_stream/bounded_general_live_fixture.cpp').read_text()
assert 'assert(ok && allocated==0 && f.output->Complete());' in fixture and 'newCalls=0;watch=true;' in fixture and 'const size_t allocated=newCalls;' in fixture and '(void)std::locale();' in fixture
production=(W/'il2cpp_plus/libil2cpp/vm/AssemblyShadow.cpp').read_text();assert production.count('#include "AssemblyShadowBoundedGeneralLiveSource.inl"')==1
for profile in {x[0] for x in pairs}:assert (profile,'AssemblyShadow.cpp') in pairs
save('LIVE_GENERAL_VERIFICATION.json',dict(result='PassedWithinInactiveSourceHostAndOfficialSDKSyntaxScope',sourceMethodSha256=live['sourceMethodSha256'],caseGroups=live['caseGroups'],fourCompileRunReceiptsVerified=True,sourceInputs=live['sourceBefore'],actualProductionMethodBytesCompiled=True,actualOwnedCapturesAndLegacySerializer=True,sourcePreserved=True,watchedNewAllocationsAfterPrewarm=0,allocationEvidence='Passing exact production method fixture assertion; no separately emitted numeric counter receipt',productionAssemblyShadowCppIncludedInAllFiveOfficialSdkProfiles=True,coherentVmEpochProven=False,nativeClassPointerOriginProven=False,realShutdownDeadlockFreedomProven=False,originalLiveGettersReplaced=False,runtimeAcceptance=False))

assert r['kind']=='R03P1FailureAwareSourceSDKPreflight' and r['schemaVersion']==2 and r['componentCount']==r['attemptedComponentCount']==15 and r['stoppedAfter'] is None and r['commandLifetimeUnverified'] is False and r['descendantQuiescenceProven'] is False
assert [c['name'] for c in r['commands']]==['command-failures','legacy-host','metadata-gate','bounded-class','bounded-physical','bounded-first-use','owned-general','live-general','owned-execution','empty-live','bounded-status','bounded-inventory','frozen-v2','managed-sdk','native-sdk']
for c in r['commands']:
 assert c['commandInvoked'] is True and c['exit']==0 and c['stopBatchReason'] is None and c['commandLifetimeUnverified'] is False and c['descendantQuiescenceProven'] is False and c['timedOut'] is False and c['interrupted'] is False and c['outputCompleteness']=='CompleteDirectChildStreams'
 for stream in ['stdout','stderr']:
  p=O/'commands'/c['name']/(stream+'.bin');assert c[stream+'Available'] is True and c[stream+'CapturedBytes']==p.stat().st_size
 p=Path(c['innerResultPath']);assert p.is_file() and not p.is_symlink() and p.resolve()==p and sha(p)==c['innerResultSha256'] and load(p)['result']==c['innerResult']==c['expectedInnerResult']
assert load(O/'MANIFEST.json')['inventoryScope']=='CompletedBatchFiles' and load(O/'MANIFEST.json')['commandLifetimeUnverified'] is False
cf=load(O/'command-failures/RESULT.json');assert cf['kind']=='R03P1CommandFailureContracts' and cf['schemaVersion']==1 and cf['result']=='PassedWithinHostScope' and cf['expectedTestCount']==cf['testsRun']==len(cf['testIds'])==len(set(cf['testIds']))==70
assert all(cf[k]==0 for k in ['failures','errors','skipped','expectedFailures','unexpectedSuccesses']) and cf['sourcePreserved'] and cf['sourceBefore']==cf['sourceAfter'] and cf['commandLifetimeUnverified'] is False
assert [m['expectedTests'] for m in cf['modules']]==[5,14,29,10,12] and sum(len(m['testIds']) for m in cf['modules'])==70
for path,row in cf['sourceBefore'].items():
 q=Path(path);data=q.read_bytes();assert len(data)==row['bytes'] and sha(q)==row['sha256'] and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['gitBlob']
assert len(cf['sourceBefore'])==11 and cf['realPythonChildTests'] is True and cf['gitSdkVmChildrenMocked'] is True and all(cf[k] is False for k in ['nativeCompilerExecuted','officialUnitySdkCompiled','UnityPlayerExecuted','runtimeAcceptance'])
log=O/'command-failures/unittest.log';assert sha(log)==cf['log']['sha256'] and log.stat().st_size==cf['log']['bytes'];text=log.read_text();assert 'Ran 70 tests' in text and text.rstrip().endswith('OK')
assert len([line for line in text.splitlines() if line.endswith(' ... ok')])==70
save('COMMAND_FAILURE_VERIFICATION.json',dict(result='PassedWithinHostToolingScope',uniqueTests=70,modules=cf['modules'],failures=0,errors=0,skipped=0,sourceInputs=cf['sourceBefore'],sourcePreserved=True,fullUnittestLogSha256=sha(log),realControlledPythonChildren=True,gitSdkVmChildrenMocked=True,currentBatch15CompleteDirectChildren=True,noUnsafeStopWitnessed=True,descendantQuiescenceProven=False,timeoutInterruptAndNotRunSemanticsCheckedByContracts=True,productionRuntimeOrProcessTreeSupervisionProven=False))
lprior=O.parent/'R03-P1-LIVE-GENERAL-20261018-5667';li=load(lprior/'native-sdk/native-sdk-inputs.json')['files'];lscratch=O.parent/'Scratch-R03-P1-LIVE-GENERAL-20261018-5667'
for row in load(lprior/'MANIFEST.json')['files']:
 q=lprior/row['path'];assert q.stat().st_size==row['size'] and sha(q)==row['sha256']
for row in li:assert sha(lscratch/row['path'])==row['sha256']
assert load(lprior/'RESULT.json')['result']=='PassedSourceHostAndSDKOnly'
save('CONSUMED_LIVE_AFTER.json',dict(result='Preserved',rawRoot=str(lprior),scratchRoot=str(lscratch),regularFilesVerified=len(load(lprior/'MANIFEST.json')['files']),scratchInputsVerified=len(li),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))
pl=load(P/'HISTORICAL_SYMLINKS_BEFORE.json')
for row in pl['bindings']:
 q=Path(row['path']);assert q.is_symlink() and os.readlink(q)==row['target']
save('HISTORICAL_SYMLINKS_AFTER.json',pl)

retained={}
for name in ['metadata-gate','bounded-class','bounded-physical','bounded-status','bounded-inventory','frozen-v2']:
 child=load(O/name/'RESULT.json');assert child.get('sourcePreserved',child.get('sourceUnchanged')) is True and child.get('firstError',child.get('firstFailure')) is None
 for c in child['commands']:assert c['exit']==c.get('expectedExit',0) and c.get('timedOut',False) is False
 profiles=child.get('profilesCompleted',child.get('completedProfiles'))
 if name=='frozen-v2':
  profiles=[x['profile'] for x in child['profiles']]
  for row in child['profiles']:assert row['strictWireReferenceByteParity'] and row['originalSemanticStatus']=='Failed' and row['overflowRejected'] and row['partialSinkRejected'] and row['invalidUtf8Rejected'] and row['combinedArtifactOverflowRejected']
 assert profiles==['strict','sanitized']
 inp=child.get('sourceBefore',child.get('sources'))
 for rel,b in inp.items():
  q=Path(rel)
  if not q.is_absolute():q=W/'il2cpp_plus'/rel
  data=q.read_bytes();assert sha(q)==b['sha256'] and len(data)==b.get('bytes',len(data)) and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==b['gitBlob']
 assert child['runtimeAcceptance'] is False
 retained[name]=dict(result=child['result'],sourcePreserved=True,profiles=profiles,commandsVerified=len(child['commands']),expectedNegativeCommands=[c for c in child['commands'] if c.get('expectedExit',0)!=0],runtimeAcceptance=False)
save('RETAINED_HOST_VERIFICATION.json',retained)

cmdprior=O.parent/'R03-P1-COMMAND-FAILURES-20261019-cmdfail-e29a';ci=load(cmdprior/'native-sdk/native-sdk-inputs.json')['files'];cscratch=O.parent/'Scratch-R03-P1-COMMAND-FAILURES-20261019-cmdfail-e29a'
for row in load(cmdprior/'MANIFEST.json')['files']:
 q=cmdprior/row['path'];assert q.stat().st_size==row['size'] and sha(q)==row['sha256']
for row in ci:assert sha(cscratch/row['path'])==row['sha256']
assert load(cmdprior/'RESULT.json')['result']=='PassedSourceHostAndSDKOnly' and len(load(cmdprior/'RESULT.json')['commands'])==13
save('CONSUMED_COMMAND_AFTER.json',dict(result='Preserved',rawRoot=str(cmdprior),scratchRoot=str(cscratch),regularFilesVerified=len(load(cmdprior/'MANIFEST.json')['files']),scratchInputsVerified=len(ci),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))
import ast,re
execution=load(O/'owned-execution/RESULT.json');assert execution['kind']=='R03P1FrozenExecutionHost' and execution['schemaVersion']==1 and execution['result']=='PassedWithinOwnedExecutionHostScope'
assert execution['sourcePreserved'] is True and execution['sourceSha256Before']==execution['sourceSha256After'] and execution['sourceIdentity']==execution['sourceIdentityAfter'] and execution['testGroupsExecuted']==210
identity=execution['sourceIdentity'];assert identity['mode']=='GitCheckout' and identity['gitHead']==E['pins']['il2cpp_plus'] and identity['gitBranch']=='codex/assembly-shadow-r01b-h1' and identity['gitClean'] is True
assert execution['actualR02CounterSourceExercised'] is True and execution['classRowsAreHostFixtures'] is True and execution['legacyReferenceCommit']=='5667e3712f49e4b38c7dd7359e57f81e344626da'
for flag in ['coherentVmEpochProven','classPointerOriginProven','originalLiveGettersReplaced','officialSdkCompile','unityEditorRun','UnityPlayerExecuted','runtimeAcceptance']:assert execution[flag] is False
for rel,h in execution['sourceSha256Before'].items():assert sha(W/'il2cpp_plus'/rel)==h
assert len(execution['sourceSha256Before'])==14
refs=load(P/'EXECUTION_REFERENCE_BEFORE.json')['references'];assert execution['referenceSha256']=={Path(x['path']).name:x['sha256'] for x in refs}
prefix=b'// Independent legacy reference; original bytes follow unchanged.\n'
for name,row in execution['referenceAdapters'].items():
 q=O/'owned-execution'/row['path'];original=(W/'il2cpp_plus/tools/r03/diagnostic_stream/reference'/name).read_bytes();assert row['onlyAddedCommentPrefix'] is True and q.read_bytes()==prefix+original and sha(q)==row['sha256'] and hashlib.sha256(original).hexdigest()==row['originalSha256']==execution['referenceSha256'][name]
for x in refs:assert sha(Path(x['path']))==x['sha256']
save('EXECUTION_REFERENCE_AFTER.json',dict(result='AuthenticatedOriginalGitBytesPreserved',beforeReceiptSha256=sha(P/'EXECUTION_REFERENCE_BEFORE.json'),references=refs,generatedAdaptersOnlyAddAuthenticatedCommentPrefix=True))
runner=W/'il2cpp_plus/tools/r03/diagnostic_stream/run_frozen_execution.py';tree=ast.parse(runner.read_text());catalog=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='TESTS' for t in n.targets));assert len(catalog)==len(set(catalog))==35
labels=[f'level{level}-{mode}' for level in [0,1,2] for mode in ['strict','sanitized']];assert [x['name'] for x in execution['profiles']]==labels and execution['actualR02CounterSourceProfiles']==labels
cmds_execution={c['label']:c for c in execution['commands']};assert list(cmds_execution)==['compiler-version']+[x+suffix for x in labels for suffix in ['-compile','-run']] and len(cmds_execution)==13
for label,c in cmds_execution.items():
 assert c['status']=='Passed' and c['exit']==0 and load(O/'owned-execution'/(label+'.json'))==c
 for stream in ['stdout.bin','stderr.bin']:
  b=c[stream];q=O/'owned-execution'/b['path'];assert q.name==label+'.'+stream and sha(q)==b['sha256'] and q.stat().st_size==b['bytes']
stream_receipts+=13
profiles=[]
for row in execution['profiles']:
 label=row['name'];level=row['diagnosticsLevel'];san=row['sanitized'];assert row['result']=='Passed' and row['tests']==list(catalog)
 text=(O/'owned-execution'/(label+'-run.stdout.bin')).read_text();assert re.findall(r'^PASS (.+)$',text,re.M)==list(catalog)
 assert re.findall(r'^SUMMARY tests=(\d+) diagnosticsLevel=(\d+) runtimeAcceptance=false$',text,re.M)==[('35',str(level))]
 alloc=re.findall(r'^OBSERVATION watchedOperatorNew=(\d+) snapshotBytes=(\d+) recordBytes=(\d+)$',text,re.M);assert len(alloc)==1 and [list(x) for x in alloc]==row['allocation'] and alloc[0][0]=='0' and int(alloc[0][1])<=512 and int(alloc[0][2])<=3932160+768
 c=cmds_execution[label+'-compile'];argv=c['argv'];assert '-std=c++17' in argv and argv[argv.index('-iquote')+1]==str(W/'il2cpp_plus/libil2cpp/vm') and '-I'+str(W/'il2cpp_plus/libil2cpp/vm') not in argv and '-DHYBRIDCLR_ASSEMBLY_SHADOW_DIAGNOSTICS_LEVEL='+str(level) in argv
 assert ('-fsanitize=address,undefined' in argv)==san and cmds_execution[label+'-run']['argv']==[str(O/'owned-execution'/label)]
 profiles.append(dict(name=label,diagnosticsLevel=level,sanitized=san,groups=35,watchedOperatorNew=0,snapshotObjectBytes=int(alloc[0][1]),recordObjectBytes=int(alloc[0][2])))
assert execution['leakSanitizer']=='UnavailableOnAppleHost' and execution['sanitizerEnvironment']=={'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'}
assert 'AssemblyShadowExecutionComposeSyntax.cpp' in {p[1] for p in pairs}
for profile in {x[0] for x in pairs}:assert (profile,'AssemblyShadowExecutionComposeSyntax.cpp') in pairs
save('OWNED_EXECUTION_VERIFICATION.json',dict(result='PassedWithinOwnedExecutionHostAndOfficialSDKSyntaxScope',profiles=profiles,caseGroups=list(catalog),hostGroupsExecuted=210,successfulCompilerVersionCompileRunReceipts=13,sourceIdentity=identity,sourceHashes=execution['sourceSha256Before'],sourcePreserved=True,referenceSha256=execution['referenceSha256'],referenceAdapters=execution['referenceAdapters'],hostR02CounterSourceCases=True,classRowsAreHostFixtures=True,coherentVmEpochProven=False,classPointerOriginProven=False,originalLiveGettersReplaced=False,runtimeAcceptance=False,SDKProbe='AssemblyShadowExecutionComposeSyntax.cpp',probeCompiledUnderAllFiveOfficialSdkProfiles=True,SDKConfigurations=85,watchedOperatorNewAfterPrewarm=0,processGcRssMeasured=False,realVmShutdownSafetyProven=False,legacyMacCIFailureUnchanged=True))

fprior=O.parent/'R03-P1-OWNED-EXECUTION-20261019-f0c5';f_i=load(fprior/'native-sdk/native-sdk-inputs.json')['files'];fscratch=O.parent/'Scratch-R03-P1-OWNED-EXECUTION-20261019-f0c5'
for row in load(fprior/'MANIFEST.json')['files']:
 q=fprior/row['path'];assert q.stat().st_size==row['size'] and sha(q)==row['sha256']
for row in f_i:assert sha(fscratch/row['path'])==row['sha256']
assert load(fprior/'RESULT.json')['result']=='PassedSourceHostAndSDKOnly' and len(load(fprior/'RESULT.json')['commands'])==14
save('CONSUMED_EXECUTION_AFTER.json',dict(result='Preserved',rawRoot=str(fprior),scratchRoot=str(fscratch),regularFilesVerified=len(load(fprior/'MANIFEST.json')['files']),scratchInputsVerified=len(f_i),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))
empty=load(O/'empty-live/RESULT.json');assert empty['commandLifetimeUnverified'] is False and empty['descendantQuiescenceProven'] is False and empty['postflightError'] is None and empty['successfulSourceCompileProfiles']==['strict-compile','sanitized-compile'];em=load(O/'empty-live/MANIFEST.json');assert em['inventoryScope']=='CompletedHostFiles' and em['commandLifetimeUnverified'] is False
assert empty['kind']=='R03P1EmptyExecutionLiveSourceHost' and empty['schemaVersion']==1 and empty['result']=='PassedWithinInactiveZeroClassHostScope'
assert empty['sourcePreserved'] is True and empty['sourceBefore']==empty['sourceAfter'] and empty['firstError'] is None and empty['actualProductionHeaderAndMethodCompiled'] is True and empty['nativeVmInputsExplicitlyMocked'] is True
assert empty['zeroClassSubsetOnly'] is True and all(empty[k] is False for k in ['completeExecutionSource','coherentVmEpochProven','classPointerOriginProven','officialUnitySdkCompiled','UnityPlayerExecuted','runtimeAcceptance'])
assert len(empty['sourceBefore'])==12 and empty['originalProductionMethodSha256']=='14b422a81986960c0de25ad0fe4214241cc9f7ea4e6ad9a724330dbd9230de4d'
N=W/'il2cpp_plus';h=N/'libil2cpp/vm/AssemblyShadowBoundedExecutionEmptyLive.h';inl=N/'libil2cpp/vm/AssemblyShadowBoundedExecutionEmptyLiveSource.inl';assert sha(inl)==empty['originalProductionMethodSha256'] and sha(h)=='d4f4d495fc0636fcdd41f1121a1aa71404e838e1dfedfc7a7a3d10d70777e734'
for rel,b in empty['sourceBefore'].items():
 q=N/rel;data=q.read_bytes();assert len(data)==b['bytes'] and sha(q)==b['sha256'] and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==b['gitBlob']
for name,src in [('AssemblyShadowBoundedExecutionEmptyLive.h',h),('AssemblyShadowBoundedExecutionEmptyLiveSource.inl',inl),('AssemblyShadowFrozenExecutionRecord.h',N/'tools/r03/diagnostic_stream/empty_live_fixture/AssemblyShadowFrozenExecutionRecord.h'),('AssemblyShadowMetadataLifetime.h',N/'tools/r03/diagnostic_stream/empty_live_fixture/AssemblyShadowMetadataLifetime.h')]:assert (O/'empty-live/host-only-includes'/name).read_bytes()==src.read_bytes()
groups=['level2-zero-class','level1-zero-class','level0-zero-class','reused-frozen-output','metadata-closed','nonempty-class-inventory','inconsistent-class-inventory','counter-first-failure','counter-second-failure','dropped-threads-refused','saturated-refused','dropped-class-rows-refused','state-changed-mid-source','class-added-mid-source','state-changed-during-format','counter-changed-during-format','generation-changed-during-format','class-added-during-format','begin-refusal','freeze-refusal']
assert list(empty['profiles'])==['sanitized','strict'] or list(empty['profiles'])==['strict','sanitized']
for profile in ['strict','sanitized']:
 text=(O/'empty-live'/(profile+'-run.stdout.bin')).read_text();assert re.findall(r'^PASS (.+)$',text,re.M)==groups==empty['profiles'][profile]['caseGroups'] and len(set(groups))==20 and text.rstrip().endswith('P1 EMPTY LIVE EXECUTION SOURCE HOST PASS')
assert len(empty['commands'])==5 and [c['name'] for c in empty['commands']]==['compiler-version','strict-compile','strict-run','sanitized-compile','sanitized-run']
for c in empty['commands']:
 assert c['status']=='Passed' and c['exit']==0 and c['outputCompleteness']=='CompleteDirectChildStreams' and c['commandLifetimeUnverified'] is False and c['timedOut'] is False and c['interrupted'] is False and load(O/'empty-live'/(c['name']+'.json'))==c
 for stream in ['stdout','stderr']:
  q=O/'empty-live'/(c['name']+'.'+stream+'.bin');assert c[stream+'Available'] is True and c[stream+'CapturedBytes']==q.stat().st_size and sha(q)==c[stream+'Sha256']
stream_receipts+=5
cpp=(N/'libil2cpp/vm/AssemblyShadow.cpp').read_bytes();bb=load(P/'EMPTY_SOURCE_BINDING_BEFORE.json');assert sha(N/'libil2cpp/vm/AssemblyShadow.cpp')==bb['candidateCppSha256'] and sha(inl)==bb['sourceMethodSha256'] and sha(h)==bb['headerSha256']
assert cpp.count(b'#include "AssemblyShadowBoundedExecutionEmptyLiveSource.inl"')==1 and cpp.count(b'TryCaptureBoundedEmptyExecutionLive(')==0
save('EMPTY_SOURCE_BINDING_AFTER.json',dict(result='Preserved',beforeReceiptSha256=sha(P/'EMPTY_SOURCE_BINDING_BEFORE.json'),originalGettersUnchanged=True,additiveNativeMethodHasNoDirectCppCaller=True,candidateCppSha256=sha(N/'libil2cpp/vm/AssemblyShadow.cpp')))
assert 'AssemblyShadowExecutionEmptyLiveSyntax.cpp' in {p[1] for p in pairs}
for profile in {x[0] for x in pairs}:assert (profile,'AssemblyShadowExecutionEmptyLiveSyntax.cpp') in pairs and (profile,'AssemblyShadow.cpp') in pairs
save('EMPTY_LIVE_VERIFICATION.json',dict(result='PassedWithinInactiveZeroClassHostAndOfficialSDKSyntaxScope',sourceMethodSha256=empty['originalProductionMethodSha256'],profiles=empty['profiles'],directVersionCompileRunReceipts=5,successfulCompilersActuallyVerified=2,groupsPerProfile=20,sourceInputs=empty['sourceBefore'],sourcePreserved=True,actualHeaderAndMethodBytes=True,VMAndCounterAndRecordInputsExplicitMocks=True,zeroClassSubsetOnly=True,completeExecutionSource=False,coherentVmEpochProven=False,classPointerOriginProven=False,runtimeAcceptance=False,originalGettersUnchanged=True,SDKConfigurations=85,SDKUnits=17,SDKProbe='AssemblyShadowExecutionEmptyLiveSyntax.cpp',newProbeAndRealAssemblyShadowCppAllFiveSyntaxProfiles=True,nativeReceiptFailurePathsControlledBy12Tests=True,currentEmpiricalBatchFaultObserved=False,priorSourceFindingPreserved=True))
# Rehash consumed predecessor without applying new semantics to its original evidence.
eprior=O.parent/'R03-P1-EMPTY-LIVE-20261019-d16d';escratch=O.parent/'Scratch-R03-P1-EMPTY-LIVE-20261019-d16d'
for row in load(eprior/'MANIFEST.json')['files']:
 q=eprior/row['path'];assert q.stat().st_size==row['size'] and sha(q)==row['sha256']
ei=load(eprior/'native-sdk/native-sdk-inputs.json')['files']
for row in ei:assert sha(escratch/row['path'])==row['sha256']
assert load(eprior/'RESULT.json')['result']=='PassedSourceHostAndSDKOnly'
save('CONSUMED_EMPTY_AFTER.json',dict(result='Preserved',rawRoot=str(eprior),scratchRoot=str(escratch),regularFilesVerified=len(load(eprior/'MANIFEST.json')['files']),scratchInputsVerified=len(ei),priorOutcome='PassedSourceHostAndSDKOnly',priorSourceFindingState='SourceConfirmed_NotFaultInjected',historicalValidationRerun=False))
pf=load(P/'PRIOR_FINDING_BEFORE.json');assert sha(Path(pf['path']))==pf['sha256']
for row in pf['sourceBindings']:
 data=subprocess.check_output(['git','-C',str(W/row['repo']),'show',row['commit']+':'+row['path']]);assert hashlib.sha256(data).hexdigest()==row['sha256']
save('PRIOR_FINDING_AFTER.json',dict(result='HistoricalFindingUnchanged',beforeReceiptSha256=sha(P/'PRIOR_FINDING_BEFORE.json'),findingId=pf['findingId'],originalStatus=pf['originalStatus'],path=pf['path'],sha256=pf['sha256'],originalSuccessfulBatchStillPass=True))
co=load(P/'CORRECTION_SCOPE_BEFORE.json')
for check in co['checks']:
 v=subprocess.run(check['argv'],capture_output=True,text=True);assert v.returncode==0 and not v.stdout
for path,key in [(W/'il2cpp_plus/tools/r03/diagnostic_stream/run_bounded_execution_empty_live.py','newNativePython'),(D/'Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py','newOuterPython'),(W/'il2cpp_plus/tools/r03/diagnostic_stream/test_bounded_execution_empty_live_receipts.py','newNativeTests')]:assert sha(path)==co[key]
save('CORRECTION_SCOPE_AFTER.json',dict(result='Preserved',beforeReceiptSha256=sha(P/'CORRECTION_SCOPE_BEFORE.json'),productionNativeAndCompilerPoliciesByteUnchanged=True))
native_tests=next(m['testIds'] for m in cf['modules'] if Path(m['path']).name=='test_bounded_execution_empty_live_receipts.py');assert len(native_tests)==12
outer_tests=next(m['testIds'] for m in cf['modules'] if Path(m['path']).name=='test_p1_command_failures.py');assert len(outer_tests)==29
save('RECEIPT_FIX_VERIFICATION.json',dict(result='PassedWithinHostReceiptAndSDKSyntaxScope',nativeRevision=E['pins']['il2cpp_plus'],demoRevision=E['pins']['hybridclr_demo'],historicalFindingId=pf['findingId'],historicalFindingStatusUnchanged=pf['originalStatus'],currentFaultObserved=False,combinedHostMethods=70,nativeReceiptContractMethods=native_tests,outerFailureContractMethods=outer_tests,sourceBeforePreserved=cf['sourceBefore']==cf['sourceAfter'],normalEmptyLive=dict(commandLifetimeUnverified=empty['commandLifetimeUnverified'],successfulSourceCompileProfiles=empty['successfulSourceCompileProfiles'],actualProductionHeaderAndMethodCompiled=empty['actualProductionHeaderAndMethodCompiled'],postflightError=empty['postflightError'],sourcePreserved=empty['sourcePreserved'],manifestInventoryScope=em['inventoryScope']),newFailurePathsVerifiedByControlledHostTests=True,actualOfficialSdkTimeoutOrSurvivorObserved=False,descendantQuiescenceProven=False,runtimeAcceptance=False))

def authority(n):
 path=W/n;rows=[]
 for args in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--short'],['remote','-v'],['worktree','list','--porcelain'],['submodule','status','--recursive'],['ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1']]:
  cmd=['git','-C',str(path),*args];start=datetime.datetime.now(datetime.timezone.utc).isoformat();v=subprocess.run(cmd,capture_output=True,text=True,timeout=90);rows.append(dict(argv=cmd,start=start,end=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit=v.returncode,stdout=v.stdout,stderr=v.stderr));assert v.returncode==0
 assert rows[0]['stdout'].strip()==str(path) and rows[1]['stdout'].strip()=='codex/assembly-shadow-r01b-h1' and rows[2]['stdout'].strip()==E['pins'][n] and not rows[3]['stdout'] and rows[-1]['stdout'].split()[0]==E['pins'][n];return n,rows
save('GIT_AFTER.json',dict(concurrent.futures.ThreadPoolExecutor(4).map(authority,E['pins'])))
audit=dict(result='PassedFactualEvidenceAudit',batchResult=r['result'],outerStates=dict(collections.Counter(c['status'] for c in r['commands'])),rawResultSha256=sha(O/'RESULT.json'),rawManifestSha256=sha(O/'MANIFEST.json'),regularInventoryEntries=len(manifest),symlinksOmittedByOuterManifestButAuthenticatedByLegacyManifest=links,localizedCommandStreamReceiptsVerified=stream_receipts,sourcePreserved=True,installedSdkPreserved=True,managed=dict(actualResult=managed['result'],aggregateState=mc['status'],exit=mc['exit'],obsoleteRootReceiptAbsent=True,innerResultPath=mc['innerResultPath'],innerResultSha256=mc['innerResultSha256'],returnedBindingVerified=mc['returnedBindingVerified'],actualResultPath=str(O/'managed-sdk/build-api/results.json'),actualResultSha256=sha(O/'managed-sdk/build-api/results.json'),productCount=5,inputCount=len(managed['inputs']),expectedNegative=expected,warnings=war['managed-sdk']['warnings']),native=dict(actualResult=native['result'],passedConfigurations=85,failedConfigurations=0,notRunConfigurations=0,distinctTranslationUnits=17,profiles=sorted({x[0] for x in pairs}),copiedSdkInputsVerified=len(sdk_inputs),candidateNativeSha=E['pins']['il2cpp_plus'],warnings=war['native-sdk']['warnings']),hostSummaries=summaries,legacyGeneralProfiles=general['profiles'],legacyParityCases=parity['cases'],noNewCompilerErrors=True,aggregateVerdictPreserved=True,realUnityOrPlayerRun=False,runtimeAcceptance=False,newNontrivialFindings=[],priorFindingId='IR-LOCAL-P1-EMPTY-LIVE-RECEIPT-01',priorFindingStatusUnchanged='SourceConfirmed_NotFaultInjected',successorFixValidation='PassedWithinHostReceiptAndSDKSyntaxScope')
save('EVIDENCE_AUDIT.json',audit);print(json.dumps({k:v for k,v in audit.items() if k not in ['hostSummaries','legacyParityCases']},indent=2))
