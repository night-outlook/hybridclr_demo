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
r=load(O/'RESULT.json');assert r['result']=='PassedSourceHostAndSDKOnly' and r['sourcePreserved'] and len(r['commands'])==18 and r['expectedNativeSyntaxUnits']==100 and r['postflightError'] is None and all(c['status']=='Passed' for c in r['commands']) and r['officialUnitySdkCompileAttempted'] is True and r['officialUnitySdkCompilePassed'] is True
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
native=load(O/'native-sdk/results.json');assert native['result']=='Passed' and native['candidateNativeSha']==E['pins']['il2cpp_plus'] and native['plannedTranslationUnitCount']==100 and len(native['translationUnits'])==100
cmds={}
for p in (O/'native-sdk/commands').glob('*/command.json'):
 c=load(p);assert c['exitCode']==0 and not c['remainingProcessGroup'] and not c['postCleanupGroupExists'] and not c['timeout'];cmds[sha(p)]=c
pairs=set()
for t in native['translationUnits']:
 src=Path(t['source']);assert sha(src)==t['sha256'];c=cmds[t['commandReceipt']];assert '-fsyntax-only' in c['command'] and '-std=c++17' in c['command'] and c['command'][c['command'].index('-arch')+1]=='arm64' and c['command'][-1]==str(src);pairs.add((t['profile'],src.name))
assert len(pairs)==100 and len({x[1] for x in pairs})==20 and len({x[0] for x in pairs})==5
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
save('OWNED_GENERAL_VERIFICATION.json',dict(result='PassedWithinOwnedHostAndSDKSyntaxScope',profiles=owned['profiles'],fourCompileRunReceiptsVerified=True,sourceContract=owned['sourceContract'],sourceInputs=owned['sourceBefore'],actualHeadersAndLegacySerializerCompiled=True,sourcePreserved=True,frozenGeneralCapacity=3932160,globalVmEpochProven=False,runtimeAcceptance=False,standaloneSdkProbe='AssemblyShadowGeneralComposeSyntax.cpp',all100NativeConfigurationsVerified=True))

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

assert r['kind']=='R03P1FailureAwareSourceSDKPreflight' and r['schemaVersion']==2 and r['componentCount']==r['attemptedComponentCount']==18 and r['stoppedAfter'] is None and r['commandLifetimeUnverified'] is False and r['descendantQuiescenceProven'] is False
assert [c['name'] for c in r['commands']]==['command-failures','legacy-host','metadata-gate','bounded-class','bounded-physical','bounded-first-use','owned-general','live-general','owned-execution','empty-live','opaque-inventory','physical-membership','owned-physical-names','bounded-status','bounded-inventory','frozen-v2','managed-sdk','native-sdk']
for c in r['commands']:
 assert c['commandInvoked'] is True and c['exit']==0 and c['stopBatchReason'] is None and c['commandLifetimeUnverified'] is False and c['descendantQuiescenceProven'] is False and c['timedOut'] is False and c['interrupted'] is False and c['outputCompleteness']=='CompleteDirectChildStreams'
 for stream in ['stdout','stderr']:
  p=O/'commands'/c['name']/(stream+'.bin');assert c[stream+'Available'] is True and c[stream+'CapturedBytes']==p.stat().st_size
 p=Path(c['innerResultPath']);assert p.is_file() and not p.is_symlink() and p.resolve()==p and sha(p)==c['innerResultSha256'] and load(p)['result']==c['innerResult']==c['expectedInnerResult']
assert load(O/'MANIFEST.json')['inventoryScope']=='CompletedBatchFiles' and load(O/'MANIFEST.json')['commandLifetimeUnverified'] is False
cf=load(O/'command-failures/RESULT.json');assert cf['kind']=='R03P1CommandFailureContracts' and cf['schemaVersion']==1 and cf['result']=='PassedWithinHostScope' and cf['expectedTestCount']==cf['testsRun']==len(cf['testIds'])==len(set(cf['testIds']))==85
assert all(cf[k]==0 for k in ['failures','errors','skipped','expectedFailures','unexpectedSuccesses']) and cf['sourcePreserved'] and cf['sourceBefore']==cf['sourceAfter'] and cf['commandLifetimeUnverified'] is False
assert [m['expectedTests'] for m in cf['modules']]==[5,14,44,10,12] and sum(len(m['testIds']) for m in cf['modules'])==85
for path,row in cf['sourceBefore'].items():
 q=Path(path);data=q.read_bytes();assert len(data)==row['bytes'] and sha(q)==row['sha256'] and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['gitBlob']
assert len(cf['sourceBefore'])==13 and cf['realPythonChildTests'] is True and cf['gitSdkVmChildrenMocked'] is True and all(cf[k] is False for k in ['nativeCompilerExecuted','officialUnitySdkCompiled','UnityPlayerExecuted','runtimeAcceptance'])
log=O/'command-failures/unittest.log';assert sha(log)==cf['log']['sha256'] and log.stat().st_size==cf['log']['bytes'];text=log.read_text();assert 'Ran 85 tests' in text and text.rstrip().endswith('OK')
assert len([line for line in text.splitlines() if line.endswith(' ... ok')])==85
save('COMMAND_FAILURE_VERIFICATION.json',dict(result='PassedWithinHostToolingScope',uniqueTests=85,modules=cf['modules'],failures=0,errors=0,skipped=0,sourceInputs=cf['sourceBefore'],sourcePreserved=True,fullUnittestLogSha256=sha(log),realControlledPythonChildren=True,gitSdkVmChildrenMocked=True,currentBatch18CompleteDirectChildren=True,noUnsafeStopWitnessed=True,descendantQuiescenceProven=False,timeoutInterruptAndNotRunSemanticsCheckedByContracts=True,productionRuntimeOrProcessTreeSupervisionProven=False))
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
save('OWNED_EXECUTION_VERIFICATION.json',dict(result='PassedWithinOwnedExecutionHostAndOfficialSDKSyntaxScope',profiles=profiles,caseGroups=list(catalog),hostGroupsExecuted=210,successfulCompilerVersionCompileRunReceipts=13,sourceIdentity=identity,sourceHashes=execution['sourceSha256Before'],sourcePreserved=True,referenceSha256=execution['referenceSha256'],referenceAdapters=execution['referenceAdapters'],hostR02CounterSourceCases=True,classRowsAreHostFixtures=True,coherentVmEpochProven=False,classPointerOriginProven=False,originalLiveGettersReplaced=False,runtimeAcceptance=False,SDKProbe='AssemblyShadowExecutionComposeSyntax.cpp',probeCompiledUnderAllFiveOfficialSdkProfiles=True,SDKConfigurations=100,watchedOperatorNewAfterPrewarm=0,processGcRssMeasured=False,realVmShutdownSafetyProven=False,legacyMacCIFailureUnchanged=True))

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
cpp=(N/'libil2cpp/vm/AssemblyShadow.cpp').read_bytes()
assert cpp.count(b'#include "AssemblyShadowBoundedExecutionEmptyLiveSource.inl"')==1 and cpp.count(b'TryCaptureBoundedEmptyExecutionLive(')==0
for rel in ['libil2cpp/vm/AssemblyShadowBoundedExecutionEmptyLive.h','libil2cpp/vm/AssemblyShadowBoundedExecutionEmptyLiveSource.inl']:
 old=subprocess.check_output(['git','-C',str(N),'show','48ee6468065a6b559f53719dc310d901d8181ab8:'+rel]);assert old==(N/rel).read_bytes()
assert 'AssemblyShadowExecutionEmptyLiveSyntax.cpp' in {p[1] for p in pairs}
for profile in {x[0] for x in pairs}:assert (profile,'AssemblyShadowExecutionEmptyLiveSyntax.cpp') in pairs and (profile,'AssemblyShadow.cpp') in pairs
save('EMPTY_LIVE_VERIFICATION.json',dict(result='PassedWithinInactiveZeroClassHostAndOfficialSDKSyntaxScope',sourceMethodSha256=empty['originalProductionMethodSha256'],profiles=empty['profiles'],directVersionCompileRunReceipts=5,successfulCompilersActuallyVerified=2,groupsPerProfile=20,sourceInputs=empty['sourceBefore'],sourcePreserved=True,actualHeaderAndMethodBytes=True,VMAndCounterAndRecordInputsExplicitMocks=True,zeroClassSubsetOnly=True,completeExecutionSource=False,coherentVmEpochProven=False,classPointerOriginProven=False,runtimeAcceptance=False,originalGettersUnchanged=True,SDKConfigurations=100,SDKUnits=20,SDKProbe='AssemblyShadowExecutionEmptyLiveSyntax.cpp',newProbeAndRealAssemblyShadowCppAllFiveSyntaxProfiles=True,nativeReceiptFailurePathsControlledBy12Tests=True,currentEmpiricalBatchFaultObserved=False,priorSourceFindingPreserved=True))
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
for path,key in [(W/'il2cpp_plus/tools/r03/diagnostic_stream/run_opaque_execution_inventory.py','newNativePython'),(D/'Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py','newOuterPython')]:assert sha(path)==co[key]
save('CORRECTION_SCOPE_AFTER.json',dict(result='Preserved',beforeReceiptSha256=sha(P/'CORRECTION_SCOPE_BEFORE.json'),managedCompilerAndHistoricalPinsByteUnchanged=True))
native_tests=next(m['testIds'] for m in cf['modules'] if Path(m['path']).name=='test_bounded_execution_empty_live_receipts.py');assert len(native_tests)==12
outer_tests=next(m['testIds'] for m in cf['modules'] if Path(m['path']).name=='test_p1_command_failures.py');assert len(outer_tests)==44
save('RECEIPT_FIX_VERIFICATION.json',dict(result='PassedWithinHostReceiptAndSDKSyntaxScope',nativeRevision=E['pins']['il2cpp_plus'],demoRevision=E['pins']['hybridclr_demo'],retainedPrimaryFindingId='P1-OPAQUE-LIFETIME-01',historicalEmptyLiveFindingStatusUnchanged=pf['originalStatus'],currentFaultObserved=False,combinedHostMethods=85,nativeReceiptContractMethods=native_tests,outerFailureContractMethods=outer_tests,sourceBeforePreserved=cf['sourceBefore']==cf['sourceAfter'],normalEmptyLive=dict(commandLifetimeUnverified=empty['commandLifetimeUnverified'],successfulSourceCompileProfiles=empty['successfulSourceCompileProfiles'],actualProductionHeaderAndMethodCompiled=empty['actualProductionHeaderAndMethodCompiled'],postflightError=empty['postflightError'],sourcePreserved=empty['sourcePreserved'],manifestInventoryScope=em['inventoryScope']),newFailurePathsVerifiedByControlledHostTests=True,actualOfficialSdkTimeoutOrSurvivorObserved=False,descendantQuiescenceProven=False,runtimeAcceptance=False))

# Opaque inventory is a fixed opaque-identity census, not a class metadata reader.
opaque=load(O/'opaque-inventory/RESULT.json');assert opaque['kind']=='R03P1InactiveOpaqueExecutionInventoryHost' and opaque['schemaVersion']==1 and opaque['result']=='PassedWithinInactiveOpaqueHostScope'
assert opaque['sourceMethodSha256']==load(P/'OPAQUE_SOURCE_BINDING_BEFORE.json')['opaqueMethodSha256'] and opaque['sourceBefore']==opaque['sourceAfter'] and opaque['sourcePreserved'] is True and opaque['firstError'] is None and opaque['postflightError'] is None and opaque['commandLifetimeUnverified'] is False
assert opaque['actualNativeOpaqueMethodCompiled'] is True and opaque['opaqueNonemptySourceExercised'] is True and opaque['classPointersNeverDereferenced'] is True
for flag in ['physicalClassPointerOriginProven','coherentVmEpochProven','completeExecutionSource','officialUnitySdkCompiled','UnityPlayerExecuted','runtimeAcceptance']:assert opaque[flag] is False
assert len(opaque['sourceBefore'])==9
for rel,b in opaque['sourceBefore'].items():
 q=N/rel;data=q.read_bytes();assert len(data)==b['bytes'] and sha(q)==b['sha256'] and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==b['gitBlob']
otree=ast.parse((N/'tools/r03/diagnostic_stream/run_opaque_execution_inventory.py').read_text());ogroups=next(ast.literal_eval(n.value) for n in otree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GROUPS' for t in n.targets));assert len(ogroups)==len(set(ogroups))==34
for profile in ['strict','sanitized']:
 text=(O/'opaque-inventory'/(profile+'-run.stdout.bin')).read_text();assert tuple(re.findall(r'^PASS (.+)$',text,re.M))==ogroups and opaque['profiles'][profile]['caseGroups']==list(ogroups) and text.rstrip().endswith('P1 OPAQUE EXECUTION INVENTORY SOURCE HOST PASS')
assert len(opaque['commands'])==5 and [c['name'] for c in opaque['commands']]==['compiler-version','strict-compile','strict-run','sanitized-compile','sanitized-run']
for c in opaque['commands']:
 assert c['status']=='Passed' and c['exit']==0 and c['commandLifetimeUnverified'] is False and not c.get('timedOut',False) and not c.get('interrupted',False) and c['outputCompleteness']=='CompleteDirectChildStreams' and load(O/'opaque-inventory'/(c['name']+'.json'))==c
 for stream in ['stdout','stderr']:
  q=O/'opaque-inventory'/(c['name']+'.'+stream+'.bin');assert c[stream+'Available'] is True and c[stream+'CapturedBytes']==q.stat().st_size and sha(q)==c[stream+'Sha256']
stream_receipts+=5
om=load(O/'opaque-inventory/MANIFEST.json');assert om['inventoryScope']=='CompletedHostFiles' and om['commandLifetimeUnverified'] is False
for b in om['files']:q=O/'opaque-inventory'/b['path'];assert q.stat().st_size==b['bytes'] and sha(q)==b['sha256']
assert sha(N/'libil2cpp/vm/AssemblyShadowOpaqueExecutionInventorySource.inl')==opaque['sourceMethodSha256']
for profile in {x[0] for x in pairs}:assert (profile,'AssemblyShadowOpaqueInventorySyntax.cpp') in pairs and (profile,'AssemblyShadow.cpp') in pairs
bb=load(P/'OPAQUE_SOURCE_BINDING_BEFORE.json')
for row in bb['originals']:
 assert sha(N/row['path'])==row['candidateSha256']
 data=subprocess.check_output(['git','-C',str(N),'cat-file','blob',row['originalBlob']]);assert hashlib.sha256(data).hexdigest()==row['originalSha256']
assert cpp.count(b'TryCaptureOpaqueExecutionInventory(')==0 and cpp.count(b'#include "AssemblyShadowOpaqueExecutionInventorySource.inl"')==1
save('OPAQUE_SOURCE_BINDING_AFTER.json',dict(result='Preserved',beforeReceiptSha256=sha(P/'OPAQUE_SOURCE_BINDING_BEFORE.json'),originalCppAndApiBytesPreservedExceptExactOpaqueAdditions=True,noDirectProductionCppCaller=True))
opaque_tests=[t for t in outer_tests if '.test_' in t and 'opaque' in t];assert len(opaque_tests)==5
save('OPAQUE_INVENTORY_VERIFICATION.json',dict(result='PassedWithinInactiveOpaqueHostAndOfficialSDKSyntaxScope',sourceMethodSha256=opaque['sourceMethodSha256'],sourceInputs=opaque['sourceBefore'],profiles=opaque['profiles'],caseGroups=list(ogroups),groupsPerProfile=34,directCommandReceiptPairs=5,allSuccessfulCompilerClaimsBackedByBothCompileReceipts=True,summaryLifetime=False,manifestScope=om['inventoryScope'],outer85ContractsVerified=True,fiveOpaqueFailureContractIds=opaque_tests,SDKConfigurations=100,SDKUnits=20,probe='AssemblyShadowOpaqueInventorySyntax.cpp',allFiveProfilesCompileActualProductionCppAndProbe=True,sourcePreserved=True,slotCount=2048,maximumOpaqueValues=1024,scratchStaticAssertBytes=33000,classPointersNeverDereferenced=True,physicalClassPointerOriginProven=False,coherentVmEpochProven=False,completeExecutionSource=False,descendantQuiescenceProven=False,runtimeAcceptance=False))
receiptprior=O.parent/'R03-P1-EMPTY-LIVE-RECEIPT-20261019-48ee';rscratch=O.parent/'Scratch-R03-P1-EMPTY-LIVE-RECEIPT-20261019-48ee';ri=load(receiptprior/'native-sdk/native-sdk-inputs.json')['files']
for row in load(receiptprior/'MANIFEST.json')['files']:
 q=receiptprior/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['size']
for row in ri:assert sha(rscratch/row['path'])==row['sha256']
assert load(receiptprior/'RESULT.json')['result']=='PassedSourceHostAndSDKOnly'
save('CONSUMED_RECEIPT_AFTER.json',dict(result='Preserved',rawRoot=str(receiptprior),scratchRoot=str(rscratch),regularFilesVerified=len(load(receiptprior/'MANIFEST.json')['files']),scratchInputsVerified=len(ri),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))
sup=load(P/'SUPERSEDED_ROOTS_BEFORE.json')
for root in sup['roots']:
 p=Path(root['path']);assert (p.exists() or p.is_symlink())==root['exists']
 if root['exists']:
  seen=set()
  for q in [p,*sorted(p.rglob('*'))]:
   if q.is_symlink() or q.is_file():seen.add(str(q))
  assert seen=={b['path'] for b in root['files']}
  for b in root['files']:
   q=Path(b['path'])
   if b['kind']=='Symlink':assert q.is_symlink() and os.readlink(q)==b['target']
   else:assert q.stat().st_size==b['bytes'] and sha(q)==b['sha256']
save('SUPERSEDED_ROOTS_AFTER.json',dict(result='PreservedWithoutInferredExecutionVerdict',beforeReceiptSha256=sha(P/'SUPERSEDED_ROOTS_BEFORE.json'),roots=sup['roots']))

# Registry-only revision: source-bound fixture assertions, no fabricated numeric sample receipt.
fixture_path=N/'tools/r03/diagnostic_stream/opaque_inventory_fixture.cpp';fixture=fixture_path.read_text();header=N/'libil2cpp/vm/AssemblyShadowExecutionRegistryRevision.h';registry=header.read_text();opheader=(N/'libil2cpp/vm/AssemblyShadowOpaqueExecutionInventory.h').read_text();method=(N/'libil2cpp/vm/AssemblyShadowOpaqueExecutionInventorySource.inl').read_text();production=(N/'libil2cpp/vm/AssemblyShadow.cpp').read_text()
new_groups=['same-slots-new-registry-revision','stable-nonzero-registry-revision','saturated-registry-revision-refused'];assert all(g in ogroups for g in new_groups)
assert 'receipt.registryRevisionFenceStable&&' in fixture and 'receipt.registryRevisionBefore==receipt.registryRevisionAfter&&' in fixture and 'receipt.registryRevisionAfter==s_executionRegistryRevision.Current()' in fixture
assert 'test("same-slots-new-registry-revision",opaque::Error::SourceChanged' in fixture and 'test("stable-nonzero-registry-revision",opaque::Error::None' in fixture and 'test("saturated-registry-revision-refused",opaque::Error::InvalidRegistry' in fixture
assert 'Revision{8}' in fixture and 'Revision{9}' in fixture and 'require(!s_executionRegistryRevision.Advance(),"revision overflow accepted")' in fixture
assert 'if(value_==std::numeric_limits<uint64_t>::max())return false;' in registry and '++value_;' in registry
assert method.count('s_executionRegistryRevision.Current()')==1 and method.index('ExecutionObservationLock lock;')<method.index('s_executionRegistryRevision.Current()')
assert 'receipt.registryRevisionBefore=scratch.Before().RegistryRevision();' in method and 'receipt.registryRevisionAfter=scratch.After().RegistryRevision();' in method and 'receipt.registryRevisionFenceStable=true;' in method
assert 'registryRevision_' in opheader and 'std::numeric_limits<uint64_t>::max()' in opheader and 'registryRevision_!=b.registryRevision_' in opheader
assert production.count('assembly_shadow_execution_publisher::Insert(')==1
start=production.index('    void ObserveExecutionClass(');end=production.index('    void RecordFirstGuardFailure(',start);observed=production[start:end]
assert observed.index('ExecutionObservationLock lock;')<observed.index('assembly_shadow_execution_publisher::Insert(')<observed.index('ObservationMemo::Remember(klass);',observed.index('assembly_shadow_execution_publisher::Insert('))<observed.index('s_droppedClassObservations.fetch_add')
assert sha(header)==bb['revisionHeaderSha256']
excerpts=[]
for path,tokens in [(fixture_path,['receipt.registryRevisionFenceStable&&','same-slots-new-registry-revision','stable-nonzero-registry-revision','saturated-registry-revision-refused']),(header,['bool Advance()','max())return false;']),(N/'libil2cpp/vm/AssemblyShadow.cpp',['void ObserveExecutionClass(','assembly_shadow_execution_publisher::Insert('])]:
 lines=path.read_text().splitlines()
 for token in tokens:
  indexes=[i for i,line in enumerate(lines) if token in line];assert len(indexes)==1
  i=indexes[0];lo=max(0,i-2);hi=min(len(lines),i+7);excerpts.append(dict(path=str(path),sha256=sha(path),startLine=lo+1,endLine=hi,excerpt='\n'.join(lines[lo:hi])))
save('REGISTRY_REVISION_VERIFICATION.json',dict(result='PassedWithinRegistryScopedSourceHostAndOfficialSDKSyntax',sourceMethodSha256=opaque['sourceMethodSha256'],revisionHeaderSha256=sha(header),sourceInputs=opaque['sourceBefore'],profiles=opaque['profiles'],groupsPerProfile=34,newGroupCases=new_groups,versionCompileRunReceipts=5,saturatingRevisionUnderOriginalObservationLockSourceChecked=True,successfulFixtureAssertsEqualBeforeAfterAndFenceTrue=True,stablePositiveFixtureInitialRevision=9,changedSlotsUnchangedFixtureInitialRevision=8,positiveFixtureNumericValuesIndependentlyEmitted=False,numericEvidence='Source-authenticated runtime require assertions and PASS groups; no separately emitted numeric revision JSON/log fields',mockVmInputs=True,sourceExcerpts=excerpts,originalGetterBlobPreservedAfterExactApprovedAdditions=True,registryOnlyFence=True,VMWideCoherenceProven=False,generalABAFreedomProven=False,classPointerProvenance=False,descendantQuiescenceProven=False,runtimeAcceptance=False,SDKConfigurations=100,SDKUnits=20))
opaqueprior=O.parent/'R03-P1-OPAQUE-LIFETIME-20261019-d548';opscratch=O.parent/'Scratch-R03-P1-OPAQUE-LIFETIME-20261019-d548';opi=load(opaqueprior/'native-sdk/native-sdk-inputs.json')['files']
for row in load(opaqueprior/'MANIFEST.json')['files']:
 q=opaqueprior/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['size']
for row in opi:assert sha(opscratch/row['path'])==row['sha256']
assert load(opaqueprior/'RESULT.json')['result']=='PassedSourceHostAndSDKOnly'
save('CONSUMED_OPAQUE_AFTER.json',dict(result='Preserved',rawRoot=str(opaqueprior),scratchRoot=str(opscratch),regularFilesVerified=len(load(opaqueprior/'MANIFEST.json')['files']),scratchInputsVerified=len(opi),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))
ad=load(P/'ADMISSION_RETAINED_BEFORE.json')
for old in ad['consumed']:
 assert sha(Path(old['rawRoot'])/'MANIFEST.json')==old['manifestSha256']
 actual={str(q) for q in Path(old['auditRoot']).rglob('*') if q.is_file() and not q.is_symlink()};assert actual=={b['path'] for b in old['auditFiles']}
 for b in old['auditFiles']:
  q=Path(b['path']);assert q.stat().st_size==b['bytes'] and sha(q)==b['sha256']
save('ADMISSION_RETAINED_AFTER.json',dict(result='Preserved',beforeReceiptSha256=sha(P/'ADMISSION_RETAINED_BEFORE.json'),consumedP1Batches=len(ad['consumed']),allPriorAuditFilesAndManifestHashesUnchanged=True,historicalResultsReclassified=False))

publisher=N/'libil2cpp/vm/AssemblyShadowExecutionRegistryPublisher.h';witness=N/'libil2cpp/vm/AssemblyShadowExecutionRegistrationWitness.h';pub=publisher.read_text();wit=witness.read_text();assert sha(publisher)==bb['publisherHeaderSha256'] and sha(witness)==bb['witnessHeaderSha256']
assert pub.count('inline Result Insert(')==1 and pub.index('if(entry==identity)return Result::Existing;')<pub.index('if(count==maximum)return Result::Full;')<pub.index('if(revision.Current()==std::numeric_limits<uint64_t>::max())')<pub.index('if(!witnesses.Register(slot,identity,source))')<pub.index('entry=identity;')<pub.index('++count;')<pub.index('revision.Advance();')
assert 'enum class Result : uint8_t { Inserted, Existing, Full, WitnessRejected, RevisionExhausted, InvalidInput };' in pub
assert production.count(bb['productionPublisherCall'])==1 and 'knownCandidate' in observed and observed.index('? assembly_shadow_execution_witness::Source::Candidate')<observed.index(': assembly_shadow_execution_witness::Source::ActiveShadow')
assert fixture.count('#include "AssemblyShadowExecutionRegistryPublisher.h"')==1 and 'return publisher::Insert(s_executionClasses,s_executionClassCount,maximum,' in fixture
writer_groups=['publisher-candidate','publisher-active-shadow','publisher-duplicate','publisher-capacity','publisher-existing-at-capacity','publisher-conflicting-witness','publisher-saturated-revision','publisher-invalid-input','publisher-collision-probe'];assert all(g in ogroups for g in writer_groups) and [g for g in ogroups if g.startswith('publisher-')]==writer_groups
assert 'publisher::Result::RevisionExhausted' in fixture and 'saturated revision left a phantom witness' in fixture and 'failed publication changed pointer/count/revision' in fixture and 'duplicate changed registry count/revision' in fixture and 'full registry was mutated' in fixture and 'invalid insertion had side effects' in fixture
assert 'receipt.candidateWitnessesBefore==1&&receipt.activeWitnessesBefore==0' in fixture and 'receipt.activeWitnessesBefore==1&&receipt.candidateWitnessesBefore==0' in fixture and 'receipt.candidateWitnessesBefore==1&&receipt.activeWitnessesBefore==1' in fixture and 's_executionClassCount==2&&s_executionRegistryRevision.Current()==2' in fixture
assert 'receipt.registrationWitnessesObserved' in fixture and 'receipt.candidateWitnessesBefore+receipt.activeWitnessesBefore==' in fixture
src=N/'libil2cpp/vm/AssemblyShadowOpaqueExecutionInventorySource.inl';source=src.read_text();assert 'receipt.registrationWitnessesObserved=true;' in source
# Independently reconstruct the reviewed original Git blob using only the bound source gate's literal replacement snippets.
rtree=ast.parse((N/'tools/r03/diagnostic_stream/run_opaque_execution_inventory.py').read_text());gate=next(n for n in rtree.body if isinstance(n,ast.FunctionDef) and n.name=='verify');lit={}
for node in gate.body:
 if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
  try:lit[node.targets[0].id]=ast.literal_eval(node.value)
  except (ValueError,TypeError):pass
assert lit['publisherCall']==bb['productionPublisherCall'];restore=production.replace(lit['publisherHeader']+'\n','').replace(lit['publisherCall'],lit['previousWriter'])
for key in ['witnessHeader','witnessDecl','witnessInsert','witnessClassify','revisionHeader','revisionDecl','revisionInsert']:assert restore.count(lit[key])==1
restore=restore.replace(lit['physicalHeader']+'\n','').replace(lit['physicalApi']+'\n','').replace(lit['physicalInclude'],'').replace(lit['nameHeader']+'\n','').replace(lit['nameInline'],'')
restore=restore.replace(lit['witnessHeader']+'\n','').replace(lit['witnessDecl'],'').replace(lit['witnessInsert'],'').replace(lit['witnessClassify'],lit['oldAdmission'])
restore=restore.replace(lit['revisionHeader']+'\n','').replace(lit['revisionDecl'],'').replace(lit['revisionInsert'],'').replace(lit['header']+'\n','').replace('// P1 inactive opaque execution observation inventory. No class dereference.\n'+lit['include']+'\n','')
assert restore.encode()==subprocess.check_output(['git','-C',str(N),'cat-file','blob','53aecc2d113b20b6ff825d0aa4ca0f4372a7cce2'])
for profile in {x[0] for x in pairs}:assert (profile,'AssemblyShadow.cpp') in pairs and (profile,'AssemblyShadowOpaqueInventorySyntax.cpp') in pairs
binds=[]
for q in [publisher,witness,fixture_path,N/'libil2cpp/vm/AssemblyShadow.cpp',src]:
 rel=str(q.relative_to(N));blob=subprocess.check_output(['git','-C',str(N),'rev-parse',E['pins']['il2cpp_plus']+':'+rel],text=True).strip();assert q.read_bytes()==subprocess.check_output(['git','-C',str(N),'cat-file','blob',blob]);binds.append(dict(path=str(q),commit=E['pins']['il2cpp_plus'],gitBlob=blob,sha256=sha(q)))
save('REGISTRY_PUBLISHER_VERIFICATION.json',dict(result='PassedWithinSharedPublisherSourceHostAndOfficialSDKSyntax',sourceBindings=binds,profiles=opaque['profiles'],totalGroupsPerProfile=34,writerGroups=writer_groups,additionalWitnessGroups=['unwitnessed-pointer-refused','mismatched-witness-pointer-refused','phantom-witness-empty-slot-refused','active-shadow-witness-admitted'],directCompilerVersionCompileRunReceipts=5,sourceInputsPreserved=opaque['sourceBefore'],productionCall=bb['productionPublisherCall'],productionAndFixtureUseSameExactHeader=True,callerUsesExistingObservationLock=True,candidatePrecedencePreserved=True,insertedOrExistingMemoizedOnceAndRejectedDroppedOnceSourceChecked=True,saturatedRevisionRejectedBeforeWitnessSlotCountPublication=True,writerAndCollectorCandidateActiveCountsCheckedByActualFixtureAssertions=True,independentlyEmittedNumericReceipts=False,originalGetterGuardBlobRestored='53aecc2d113b20b6ff825d0aa4ca0f4372a7cce2',SDKConfigurations=100,SDKUnits=20,allFiveSyntaxProfilesCompileActualProductionCallerAndProbe=True,registrationPathProvenanceOnly=True,physicalClassPointerOriginProven=False,coherentVmEpochProven=False,generalABAFreedomProven=False,descendantQuiescenceProven=False,runtimeAcceptance=False))
revisionprior=O.parent/'R03-P1-REGISTRY-REVISION-20261020-f09e';rvscratch=O.parent/'Scratch-R03-P1-REGISTRY-REVISION-20261020-f09e';rvi=load(revisionprior/'native-sdk/native-sdk-inputs.json')['files']
for row in load(revisionprior/'MANIFEST.json')['files']:
 q=revisionprior/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['size']
for row in rvi:assert sha(rvscratch/row['path'])==row['sha256']
assert load(revisionprior/'RESULT.json')['result']=='PassedSourceHostAndSDKOnly'
save('CONSUMED_REVISION_AFTER.json',dict(result='Preserved',rawRoot=str(revisionprior),scratchRoot=str(rvscratch),regularFilesVerified=len(load(revisionprior/'MANIFEST.json')['files']),scratchInputsVerified=len(rvi),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))
wx=load(P/'SUPERSEDED_WITNESS_BEFORE.json')
for root in wx['roots']:
 q=Path(root['path']);assert (q.exists() or q.is_symlink())==root['exists']
 if root['exists']:
  actual={str(p) for p in [q,*q.rglob('*')] if p.is_file() or p.is_symlink()};assert actual=={b['path'] for b in root['files']}
  for b in root['files']:
   f=Path(b['path'])
   if b['kind']=='Symlink':assert f.is_symlink() and os.readlink(f)==b['target']
   else:assert sha(f)==b['sha256'] and f.stat().st_size==b['bytes']
save('SUPERSEDED_WITNESS_AFTER.json',dict(result='PreservedWithoutInferredExecutionOutcome',beforeReceiptSha256=sha(P/'SUPERSEDED_WITNESS_BEFORE.json'),roots=wx['roots']))

# Fresh actual-source physical-membership and owned-name host children.
for name,runner_name,kind,verdict,count,method_key,end_marker,source_count in [
 ('physical-membership','run_physical_membership.py','R03P1InactivePhysicalEnumeratorMembershipSourceHost','PassedWithinInactivePhysicalEnumerationHostScope',21,'sourceMethodSha256','P1 PHYSICAL ENUMERATION MEMBERSHIP SOURCE HOST PASS',10),
 ('owned-physical-names','run_owned_physical_names.py','R03P1InactiveOwnedObservedPhysicalNamesSourceHost','PassedWithinInactiveOwnedPhysicalNamesHostScope',28,'actualProductionMethodSha256','P1 OWNED PHYSICAL NAMES SOURCE HOST PASS',8)]:
 child=load(O/name/'RESULT.json');assert child['kind']==kind and child['schemaVersion']==1 and child['result']==verdict and child['sourcePreserved'] is True and child['sourceBefore']==child['sourceAfter'] and child['firstError'] is None and child['postflightError'] is None and child['commandLifetimeUnverified'] is False
 assert len(child['sourceBefore'])==source_count
 for rel,row in child['sourceBefore'].items():
  q=N/rel;data=q.read_bytes();assert len(data)==row['bytes'] and sha(q)==row['sha256'] and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['gitBlob']
 for flag in ['physicalClassPointerOriginProven','metadataPointerLifetimeProven','coherentVmEpochProven','officialUnitySdkCompiled','UnityPlayerExecuted','runtimeAcceptance']:assert child[flag] is False
 assert child['actualSourceCompiled' if name=='owned-physical-names' else 'actualProductionHeaderAndMethodCompiled'] is True
 tree=ast.parse((N/'tools/r03/diagnostic_stream'/runner_name).read_text());groups=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GROUPS' for t in n.targets));assert len(groups)==len(set(groups))==count
 assert len(child['commands'])==5 and [c['name'] for c in child['commands']]==['compiler-version','strict-compile','strict-run','sanitized-compile','sanitized-run']
 for c in child['commands']:
  assert c['status']=='Passed' and c['exit']==0 and c['commandLifetimeUnverified'] is False and not c.get('timedOut',False) and not c.get('interrupted',False) and c['outputCompleteness']=='CompleteDirectChildStreams' and load(O/name/(c['name']+'.json'))==c
  for stream in ['stdout','stderr']:
   q=O/name/(c['name']+'.'+stream+'.bin');assert c[stream+'Available'] is True and c[stream+'CapturedBytes']==q.stat().st_size and sha(q)==c[stream+'Sha256']
 stream_receipts+=5
 for profile in ['strict','sanitized']:
  text=(O/name/(profile+'-run.stdout.bin')).read_text();assert tuple(re.findall(r'^PASS (.+)$',text,re.M))==groups and child['profiles'][profile]['caseGroups']==list(groups) and text.rstrip().endswith(end_marker)
 cm=load(O/name/'MANIFEST.json');assert cm['inventoryScope']=='CompletedHostFiles' and cm['commandLifetimeUnverified'] is False
 for b in cm['files']:q=O/name/b['path'];assert q.stat().st_size==b['bytes'] and sha(q)==b['sha256']
 if name=='owned-physical-names':names_child=child;names_groups=groups
 else:membership_child=child;membership_groups=groups
owned_inl=N/'libil2cpp/vm/AssemblyShadowOwnedPhysicalNamesSource.inl';owned_header=N/'libil2cpp/vm/AssemblyShadowOwnedPhysicalNames.h';physical_header=N/'libil2cpp/vm/AssemblyShadowPhysicalMembership.h';owned_fixture=N/'tools/r03/diagnostic_stream/owned_physical_names_fixture.cpp';method=owned_inl.read_text();text=owned_fixture.read_text();head=owned_header.read_text();ph=physical_header.read_text()
assert names_child['actualProductionMethodSha256']==sha(owned_inl) and names_child['ownedPhysicalNamesOnly'] is True and names_child['metadataAndIteratorInputsMocked'] is True and names_child['completeExecutionTypeKeys'] is False
assert membership_child['sourceMethodSha256']==sha(N/'libil2cpp/vm/AssemblyShadowPhysicalMembershipSource.inl') and membership_child['completeExecutionSource'] is False and membership_child['membershipDoesNotAuthorizeDereference'] is True
assert method.count('ObserveEnumeratedOwned(klass)')==1 and method.index('if(event!=physical::ObservationEvent::FirstMatch')<method.index('if(!klass->image')<method.index('context.names->Add(')
assert method.count('ExecutionObservationLock lock;')==2 and method.count('os::FastAutoLock metadataLock(&g_MetadataLock);')==1 and method.index('ExecutionObservationLock lock;')<method.index('os::FastAutoLock metadataLock(&g_MetadataLock);')<method.rindex('ExecutionObservationLock lock;')
assert 'names.Revoke();' in method and 'membershipScratch.Scrub();' in method and 'names.Seal(membershipScratch.Observed())' in method and 'receipt.namesCopiedFromMatchedEnumeratorCallbacks=true;' in method
assert 'throw std::runtime_error("observation nested with metadata")' in text and 'throw std::runtime_error("nested metadata lock")' in text and 'require(!readers&&!observationLockDepth&&!metadataLockDepth' in text
assert 'value(row.physicalAssemblyName)=="PhysicalAssembly"' in text and 'value(row.nameSpace)=="Namespace"&&value(row.simpleName)=="Class"' in text and 'std::strcpy(mutableName,"ChangedLater")' in text and 'value(row.physicalAssemblyName)=="MutableBefore"' in text
assert 'kMaximumRows=1024' in head and 'kMaximumTextBytes=256u*1024u' in head and 'kMaximumFieldBytes=4096' in head and 'sizeof(Capture)<=512u*1024u' in head and 'std::array<char,kMaximumTextBytes> text_' in head and 'text_.fill(0);' in head
assert '(void)ObserveEnumeratedOwned(address);' in ph
ob=load(P/'OWNED_SOURCE_BINDING_BEFORE.json');assert ob['methodSha256']==sha(owned_inl) and ob['headerSha256']==sha(owned_header)
for row in ob['originals']:
 assert sha(N/row['path'])==row['candidateSha256'];data=subprocess.check_output(['git','-C',str(N),'cat-file','blob',row['originalBlob']]);assert hashlib.sha256(data).hexdigest()==row['originalSha256']
# Independently restore reviewed physical match-event change and additive declarations/includes.
otree=ast.parse((N/'tools/r03/diagnostic_stream/run_owned_physical_names.py').read_text());ofn=next(n for n in otree.body if isinstance(n,ast.FunctionDef) and n.name=='verify');ol={}
for node in ofn.body:
 if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
  try:ol[node.targets[0].id]=ast.literal_eval(node.value)
  except (ValueError,TypeError):pass
for value in [ol['include'],ol['inline_block']]:assert production.count(value)==1
assert production.count('TryCaptureOwnedObservedPhysicalNames(')==0
restored_cpp=production.replace(ol['include']+'\n','').replace(ol['inline_block'],'');api=(N/'libil2cpp/vm/AssemblyShadow.h').read_text();restored_api=api.replace(ol['forward'],'').replace(ol['declaration'],'')
binding=next(ast.literal_eval(n.value) for n in otree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REGISTRATION_BINDING_BLOCK' for t in n.targets));assert ph.count(binding)==1
restored_ph=ph.replace(binding,'').replace(ol['enumAdded'],'').replace(ol['newEnumeration'],ol['oldEnumeration'])
for value,blob in [(restored_cpp,'46240c58f83f1ce1a048266ed3bf421af4197567'),(restored_api,'55b1be3a134b41652fd88e24d8d548e5ca98126e'),(restored_ph,'375d9225bfbb7be693b15ffc7fc7203b48e45d92')]:assert value.encode()==subprocess.check_output(['git','-C',str(N),'cat-file','blob',blob])
new_receipt_tests=[x for x in outer_tests if ('physical_membership' in x or 'owned_physical_names' in x or 'owned_names' in x)];assert len(new_receipt_tests)==10
for profile in {x[0] for x in pairs}:assert (profile,'AssemblyShadowOwnedPhysicalNamesSyntax.cpp') in pairs and (profile,'AssemblyShadowPhysicalMembershipSyntax.cpp') in pairs and (profile,'AssemblyShadow.cpp') in pairs
save('OWNED_SOURCE_BINDING_AFTER.json',dict(result='Preserved',beforeReceiptSha256=sha(P/'OWNED_SOURCE_BINDING_BEFORE.json'),originalCppApiAndPhysicalHeaderBlobsVerified=True,noNormalCppCaller=True))
save('PHYSICAL_MEMBERSHIP_VERIFICATION.json',dict(result='PassedWithinInactivePhysicalMembershipHostAndOfficialSDKSyntax',profiles=membership_child['profiles'],groupsPerProfile=21,sourceInputs=membership_child['sourceBefore'],methodSha256=membership_child['sourceMethodSha256'],fiveVersionCompileRunReceiptsVerified=True,membershipDoesNotAuthorizeDereference=True,metadataAndIteratorInputsMocked=True,metadataPointerLifetimeProven=False,coherentVmEpochProven=False,runtimeAcceptance=False,SDKConfigurations=100,SDKUnits=20))
save('OWNED_PHYSICAL_NAMES_VERIFICATION.json',dict(result='PassedWithinInactiveOwnedPhysicalNamesHostAndOfficialSDKSyntax',profiles=names_child['profiles'],groupsPerProfile=28,sourceInputs=names_child['sourceBefore'],methodSha256=sha(owned_inl),headerSha256=sha(owned_header),fiveVersionCompileRunReceiptsVerified=True,firstMatchOnlyBeforeMetadataRead=True,sourceStringMutationImmutabilityFixtureAsserted=True,nonnestedLocksAssertedUnderMocks=True,rowsMaximum=1024,textBytesMaximum=262144,fieldBytesMaximum=4096,captureObjectBytesMaximum=524288,originalCppApiAndPhysicalHeaderBlobsVerified=True,voidPhysicalEnumeratorApiPreserved=True,newPhysicalAndOwnedNamesFailStopContractIds=new_receipt_tests,numericNameBytesIndependentlyEmitted=False,rawEvidence='Source-authenticated fixture assertions and complete PASS groups; no separately emitted per-case name JSON',metadataAndIteratorInputsMocked=True,ownedPhysicalNamesOnly=True,physicalClassPointerOriginProven=False,metadataPointerLifetimeProven=False,completeExecutionTypeKeys=False,coherentVmEpochProven=False,descendantQuiescenceProven=False,runtimeAcceptance=False,SDKConfigurations=100,SDKUnits=20))
publisherprior=O.parent/'R03-P1-REGISTRY-PUBLISHER-20261020-699d';puscratch=O.parent/'Scratch-R03-P1-REGISTRY-PUBLISHER-20261020-699d';pui=load(publisherprior/'native-sdk/native-sdk-inputs.json')['files']
for row in load(publisherprior/'MANIFEST.json')['files']:
 q=publisherprior/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['size']
for row in pui:assert sha(puscratch/row['path'])==row['sha256']
assert load(publisherprior/'RESULT.json')['result']=='PassedSourceHostAndSDKOnly'
save('CONSUMED_PUBLISHER_AFTER.json',dict(result='Preserved',rawRoot=str(publisherprior),scratchRoot=str(puscratch),regularFilesVerified=len(load(publisherprior/'MANIFEST.json')['files']),scratchInputsVerified=len(pui),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))
sup=load(P/'SUPERSEDED_PHYSICAL_BEFORE.json')
for root in sup['roots']:
 q=Path(root['path']);assert (q.exists() or q.is_symlink())==root['exists']
 if root['exists']:
  actual={str(p) for p in [q,*q.rglob('*')] if p.is_file() or p.is_symlink()};assert actual=={b['path'] for b in root['files']}
  for b in root['files']:
   f=Path(b['path'])
   if b['kind']=='Symlink':assert f.is_symlink() and os.readlink(f)==b['target']
   else:assert sha(f)==b['sha256'] and f.stat().st_size==b['bytes']
save('SUPERSEDED_PHYSICAL_AFTER.json',dict(result='PreservedWithoutInferredExecutionOutcome',beforeReceiptSha256=sha(P/'SUPERSEDED_PHYSICAL_BEFORE.json'),roots=sup['roots']))

# Independently join producer group order, aggregate schema/scope and actual slot/source assertions.
outer_source=D/'Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py';outer_tree=ast.parse(outer_source.read_text())
expected_groups=next(ast.literal_eval(n.value) for n in outer_tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='EXPECTED_OWNED_BINDING_GROUPS' for t in n.targets))
assert tuple(names_groups)==expected_groups and len(set(expected_groups))==28
owned_outer=next(c for c in r['commands'] if c['name']=='owned-physical-names')
assert owned_outer['ownedBindingCaseInventoryVerified'] is True and r['expectedOwnedBindingCaseGroupsPerProfile']==28
assert type(names_child['schemaVersion']) is int and names_child['schemaVersion']==1
for profile in ['strict','sanitized']:
 assert names_child['profiles'][profile]['result']=='PassedWithinExplicitVmMocks' and names_child['profiles'][profile]['caseGroups']==list(expected_groups)
assert type(membership_child['schemaVersion']) is int
assert method.index('if(event!=physical::ObservationEvent::FirstMatch')<method.index('TryObservedRegistrationBinding(')<method.index('context.names->Add(')
assert 'context.names->Add(registeredSlot,registeredSource,' in method and 'receipt.boundRegistrationRows=names.Count();' in method and 'receipt.allRowsBoundToObservedRegistry=true;' in method and 'receipt.allRowsBoundToObservedRegistry=false;' in method and 'return reject(names.FirstError());' in method
for token in ['size_t registrySlot=kRegistrationSlots;','registrationSource=row.registrationSource;','out.registrySlot=row.registrySlot;','usedRegistrationSlots_[registrationSlot]','DuplicateRegistrationBinding','InvalidRegistrationBinding']:
 assert token in head,token
failure=head[head.index('bool Fail(Error error)'):head.index('bool Append(')]
for token in ['text_.fill(0);','rows_.fill(Row{});','usedRegistrationSlots_.fill(0);','used_=count_=0;']:assert token in failure
for token in ['if(!captured_||badEnumeration_||!address)return false;','if(!seen_[slot])return false;','slotOut=kSlots;','sourceOut=assembly_shadow_execution_witness::Source::None;']:assert token in binding
fixture_tokens=['receipt.allRowsBoundToObservedRegistry &&','receipt.boundRegistrationRows==names.Count()', 's_executionRegistrationWitnesses.Matches(row.registrySlot,','observed==row.registrationSource','a.registrySlot==slot(&classes[1])','b.registrySlot==slot(&classes[0])','a.registrySlot!=b.registrySlot','slot(&classes[0])==slot(&classes[2048])','a.registrySlot==(slot(&classes[0])+1)%physical::kSlots','!scratch.TryObservedRegistrationBinding(&classes[0],index,role)','!scratch.TryObservedRegistrationBinding(&classes[1],index,role)','n.FirstError()==owned::Error::InvalidRegistrationBinding','n.FirstError()==owned::Error::DuplicateRegistrationBinding','!n.Get(0,v)']
for token in fixture_tokens:assert token in text,token
native_tree=ast.parse((N/'tools/r03/diagnostic_stream/run_owned_physical_names.py').read_text());oldtree=ast.parse(subprocess.check_output(['git','-C',str(N),'show','e6a350eb684a388b0c7a598f7ad0d1bae9b4f4e5:tools/r03/diagnostic_stream/run_owned_physical_names.py'],text=True));old_groups=next(ast.literal_eval(n.value) for n in oldtree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GROUPS' for t in n.targets));assert tuple(g for g in names_groups if g in old_groups)==old_groups
new_groups=[g for g in names_groups if g not in old_groups];assert len(new_groups)==8
# Current physical header adds precisely one query to the prior e6a3 first-match implementation.
ph_prior=subprocess.check_output(['git','-C',str(N),'show','e6a350eb684a388b0c7a598f7ad0d1bae9b4f4e5:libil2cpp/vm/AssemblyShadowPhysicalMembership.h']);assert ph.replace(binding,'').encode()==ph_prior
for rel in ['libil2cpp/vm/AssemblyShadow.cpp','libil2cpp/vm/AssemblyShadow.h']:
 assert (N/rel).read_bytes()==subprocess.check_output(['git','-C',str(N),'show','e6a350eb684a388b0c7a598f7ad0d1bae9b4f4e5:'+rel])
consumer_fixture=(D/'Tools/AssemblyShadow/R03IR/test_p1_command_failures.py').read_text();consumer_node=next(n for n in ast.walk(ast.parse(consumer_fixture)) if isinstance(n,ast.FunctionDef) and n.name=='verify_exact_host_binding_inventory_and_fail_closed_mutations');consumer_helper=ast.get_source_segment(consumer_fixture,consumer_node)
assert 'OwnedBindingInventoryContract().verify_exact_host_binding_inventory_and_fail_closed_mutations()' in consumer_fixture
# Full helper executes inside the existing successful frozen leaf; no extra tests are run by this audit.
assert 'test_all_eighteen_components_have_independent_success' in '\n'.join(cf['testIds'])
bound=dict(result='PassedWithinInactiveRegistryBoundOwnedNamesSourceHostAndOfficialSDKSyntax',groupsPerProfile=28,old20GroupRelativeOrderPreserved=True,newBindingGroups=new_groups,producerOrderedInventory=list(names_groups),outerOrderedInventoryVerified=True,ownedBindingCaseInventoryVerified=True,outerReceiptPath=str(O/'commands/owned-physical-names.json'),outerReceiptSha256=sha(O/'commands/owned-physical-names.json'),producerResultSha256=sha(O/'owned-physical-names/RESULT.json'),sourceMethodSha256=sha(owned_inl),physicalQuerySha256=hashlib.sha256(binding.encode()).hexdigest(),boundSlotRange=[0,2047],allowedSources=['Candidate','ActiveShadow'],firstMatchOnlyLookup=True,sourceMutationOwnedTextIndependenceAsserted=True,matchedRowSlotAndWitnessAssertionsVerified=True,reverseEnumerationAndCollisionsAsserted=True,internalFailureTextRowsSlotBitmapScrubSourceVerified=True,firstTypedErrorPropagationVerified=True,originalCppAndApiByteUnchanged=True,originalPhysicalMembershipExceptExactQueryByteUnchanged=True,consumerRegressionHelperSha256=hashlib.sha256(consumer_helper.encode()).hexdigest(),consumerTestsRunWithinOriginal85Leaves=True,numericRowsSeparatelyEmitted=False,physicalClassPointerOriginProven=False,metadataPointerLifetimeProven=False,completeExecutionTypeKeys=False,coherentVmEpochProven=False,descendantQuiescenceProven=False,runtimeAcceptance=False)
save('BOUND_REGISTRY_VERIFICATION.json',bound)
# Newest consumed immutable raw/scratch joins, plus every prior checkpoint manifest and copied file.
namesprior=O.parent/'R03-P1-OWNED-PHYSICAL-NAMES-20261020-e6a3';nss=O.parent/'Scratch-R03-P1-OWNED-PHYSICAL-NAMES-20261020-e6a3';nsi=load(namesprior/'native-sdk/native-sdk-inputs.json')['files']
for row in load(namesprior/'MANIFEST.json')['files']:
 q=namesprior/row['path'];assert sha(q)==row['sha256'] and q.stat().st_size==row['size']
for row in nsi:assert sha(nss/row['path'])==row['sha256']
assert load(namesprior/'RESULT.json')['result']=='PassedSourceHostAndSDKOnly'
save('CONSUMED_NAMES_AFTER.json',dict(result='Preserved',rawRoot=str(namesprior),scratchRoot=str(nss),regularFilesVerified=len(load(namesprior/'MANIFEST.json')['files']),scratchInputsVerified=len(nsi),priorOutcome='PassedSourceHostAndSDKOnly',historicalValidationRerun=False))
cp_before=load(P/'CHECKPOINTS_BEFORE.json');assert cp_before['count']==15
for cp in cp_before['checkpoints']:
 root=Path(cp['root']);assert sha(root/'MANIFEST.sha256')==cp['manifestSha256']
 assert {str(q.relative_to(root)) for q in root.rglob('*') if q.is_file()}=={b['path'] for b in cp['files']}|{'MANIFEST.sha256'}
 for b in cp['files']:q=root/b['path'];assert sha(q)==b['sha256'] and q.stat().st_size==b['bytes']
save('CHECKPOINTS_AFTER.json',dict(result='Preserved',count=15,beforeReceiptSha256=sha(P/'CHECKPOINTS_BEFORE.json'),filesVerified=sum(len(cp['files']) for cp in cp_before['checkpoints'])))

origins=collections.Counter();unexpected=[]
installed=Path(E['unity']).parent.parent
for row in managed['inputs']:
 q=Path(row['path']);canon=q.resolve(strict=True)
 if canon.is_relative_to(installed):origin='officialUnity2022.3.62f2'
 elif canon.is_relative_to(D):origin='pinnedDemoCheckout';repo=D
 elif canon.is_relative_to(W/'hybridclr_unity'):origin='pinnedPackageCheckout';repo=W/'hybridclr_unity'
 else:unexpected.append(str(q));continue
 if origin!='officialUnity2022.3.62f2':
  rel=str(canon.relative_to(repo));data=subprocess.check_output(['git','-C',str(repo),'show',E['pins'][repo.name]+':'+rel]);assert hashlib.sha256(data).hexdigest()==row['sha256']
 origins[origin]+=1
assert not unexpected and sum(origins.values())==len(managed['inputs'])==428
pm=D/'Packages/manifest.json';reference=load(pm)['dependencies']['com.code-philosophy.hybridclr'];assert reference=='file:../../hybridclr_unity';assert (pm.parent/reference[len('file:'):]).resolve()==W/'hybridclr_unity'
overlays=[]
for name in ['AssemblyShadowExecutionRegistryRevision.h','AssemblyShadowExecutionRegistrationWitness.h','AssemblyShadowExecutionRegistryPublisher.h','AssemblyShadowPhysicalMembership.h','AssemblyShadowPhysicalMembershipSource.inl','AssemblyShadowOwnedPhysicalNames.h','AssemblyShadowOwnedPhysicalNamesSource.inl']:
 q=N/'libil2cpp/vm'/name;t=S/'libil2cpp/vm'/name;assert sha(q)==sha(t);overlays.append(dict(source=str(q),sha256=sha(q),scratchPath=str(t)))
save('COMPILER_INPUT_ORIGINS.json',dict(result='VerifiedPinnedSourceAndOfficialSdkInputs',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),managedResultPath=str(O/'managed-sdk/build-api/results.json'),managedResultSha256=sha(O/'managed-sdk/build-api/results.json'),managedInputOrigins=dict(origins),unexpectedInputOrigins=unexpected,packageManifest=str(pm),packageManifestSha256=sha(pm),packageReference=reference,canonicalPackagePath=str(W/'hybridclr_unity'),nativeHeadersAndMethods=overlays,runtimeAcceptance=False))

def authority(n):
 path=W/n;rows=[]
 for args in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--short'],['remote','-v'],['worktree','list','--porcelain'],['submodule','status','--recursive'],['ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1']]:
  cmd=['git','-C',str(path),*args];start=datetime.datetime.now(datetime.timezone.utc).isoformat();v=subprocess.run(cmd,capture_output=True,text=True,timeout=90);rows.append(dict(argv=cmd,start=start,end=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit=v.returncode,stdout=v.stdout,stderr=v.stderr));assert v.returncode==0
 assert rows[0]['stdout'].strip()==str(path) and rows[1]['stdout'].strip()=='codex/assembly-shadow-r01b-h1' and rows[2]['stdout'].strip()==E['pins'][n] and not rows[3]['stdout'] and rows[-1]['stdout'].split()[0]==E['pins'][n];return n,rows
save('GIT_AFTER.json',dict(concurrent.futures.ThreadPoolExecutor(4).map(authority,E['pins'])))
audit=dict(result='PassedFactualEvidenceAudit',batchResult=r['result'],outerStates=dict(collections.Counter(c['status'] for c in r['commands'])),rawResultSha256=sha(O/'RESULT.json'),rawManifestSha256=sha(O/'MANIFEST.json'),regularInventoryEntries=len(manifest),symlinksOmittedByOuterManifestButAuthenticatedByLegacyManifest=links,localizedCommandStreamReceiptsVerified=stream_receipts,sourcePreserved=True,installedSdkPreserved=True,managed=dict(actualResult=managed['result'],aggregateState=mc['status'],exit=mc['exit'],obsoleteRootReceiptAbsent=True,innerResultPath=mc['innerResultPath'],innerResultSha256=mc['innerResultSha256'],returnedBindingVerified=mc['returnedBindingVerified'],actualResultPath=str(O/'managed-sdk/build-api/results.json'),actualResultSha256=sha(O/'managed-sdk/build-api/results.json'),productCount=5,inputCount=len(managed['inputs']),expectedNegative=expected,warnings=war['managed-sdk']['warnings']),native=dict(actualResult=native['result'],passedConfigurations=100,failedConfigurations=0,notRunConfigurations=0,distinctTranslationUnits=20,profiles=sorted({x[0] for x in pairs}),copiedSdkInputsVerified=len(sdk_inputs),candidateNativeSha=E['pins']['il2cpp_plus'],warnings=war['native-sdk']['warnings']),hostSummaries=summaries,legacyGeneralProfiles=general['profiles'],legacyParityCases=parity['cases'],noNewCompilerErrors=True,aggregateVerdictPreserved=True,realUnityOrPlayerRun=False,runtimeAcceptance=False,newNontrivialFindings=[],priorFindingId='IR-LOCAL-P1-EMPTY-LIVE-RECEIPT-01',priorFindingStatusUnchanged='SourceConfirmed_NotFaultInjected',successorFixValidation='PassedWithinRegistryBoundOwnedNamesHostReceiptAndSDKSyntaxScope',opaqueVerification='OPAQUE_INVENTORY_VERIFICATION.json',registryRevisionVerification='REGISTRY_REVISION_VERIFICATION.json',publisherVerification='REGISTRY_PUBLISHER_VERIFICATION.json',ownedPhysicalNamesVerification='OWNED_PHYSICAL_NAMES_VERIFICATION.json',physicalMembershipVerification='PHYSICAL_MEMBERSHIP_VERIFICATION.json',boundRegistryVerification='BOUND_REGISTRY_VERIFICATION.json')
save('EVIDENCE_AUDIT.json',audit);print(json.dumps({k:v for k,v in audit.items() if k not in ['hostSummaries','legacyParityCases']},indent=2))
