from h_common import *
import shutil
C=hist/'local-validation-m-after-l-73bc';R=B/'R03IRLocal-M-after-L-73bc';M=B/'ManagedAPI-R03M-after-L-73bc';N=B/'NativeSDK-R03M-after-L-73bc';S=B/'Scratch-R03M-after-L-73bc';source=pins['hybridclr_demo'];branch='codex/assembly-shadow-r01b-h1'
assert not C.exists();clean_sources();no_unity()
for n in ['HOST_RESULT.json','MANAGED_VERIFICATION.json','NATIVE_VERIFICATION.json','SOURCE_PRESERVATION_BEFORE.json','SOURCE_PRESERVATION_AFTER.json','FINAL_SOURCE_AUTHORITY.json']:assert load(P/n)['state']=='Passed'
for phase in ['before','after']:
 c=load(P/('scoped-custody-'+phase+'.json'));assert c['result']=='ScopedHistoricalLossStable' and c['completeScan'] and c['presentVerified']==339367 and c['historicalStillMissing']==77477 and not c['problems'];assert load(P/('retained-e-'+phase+'.json'))['result']=='PassedPreservationOnly';assert load(P/('FG_SDK_PRESERVATION_'+phase.upper()+'.json'))['state']=='PassedPreservationOnly'
a=load(P/'FINAL_EVIDENCE_AUDIT.json');core=load(R/'LOCAL_BATCH_RESULT.json');diag=load(P/'FAILURE_DIAGNOSIS.json');bee=load(P/'BEE_OBSERVATION_AUDIT.json');assert len(a['cells'])==18 and core['sealStatus']=='Passed';counts=a['cellCounts'];ok=counts=={'Passed':18};verdict='FocusedEvidenceReadyForPrimaryReview' if ok else 'FAIL / ReturnRequired'
result={'kind':'R03IRMCurrentLocalResult','recordedUtc':now(),'result':verdict,'exitState':'Local Validation -> Primary Implementation','pins':pins,'branch':branch,'executableAnchor':'04a3cd93663f9a4e877a5524d9c22ee5a3fe0131','sourceAuthority':'Passed exact four-owner remote tuple; only approved test/Docs/CI delta','hostSuites':load(P/'HOST_RESULT.json')['suites'],'correctedInventoryTests':29,'nativePolicyChecks':69,'nativeHostChecks':'Passed strict/sanitized rejection/reporting/observer, actual Object.h access, separately sanitized snapshot; mocked dependencies are not runtime','managedCompile':load(P/'MANAGED_VERIFICATION.json')['state'],'managedCompilerInvocations':1,'managedProducts':5,'expectedNegativeControls':1,'managedWarnings':load(P/'MANAGED_VERIFICATION.json')['warningCount'],'nativeCompile':load(P/'NATIVE_VERIFICATION.json')['state'],'nativeCompilerInvocations':1,'nativeConfigurations':55,'nativeWarnings':load(P/'COMPILER_WARNING_AUDIT.json')['occurrences'],'runtime':{'invocations':1,'plannedCells':18,'actualCellCounts':counts,'builds':a['builds'],'players':a['players']},'storage':a['storage'],'sealStatus':a['sealStatus'],'boundedArtifacts':a['topArtifacts'],'indexedFiles':a['indexedFiles'],'archiveMembers':a['archiveMembers'],'bee':bee['roles'],'issues':diag['issues'],'custody':{'before':'ScopedHistoricalLossStable','after':'ScopedHistoricalLossStable','expected':416844,'surviving':339367,'unchangedMissing':77477,'problems':0,'strictHistoricalCustody':'Blocked'},'preservation':'Before and after Passed E/F/G/H/I/J/K/L/SDK, current source, original S inputs and R/Q; unindexed snapshot not original build provenance','historicalStates':{'E':'FAIL','I':'FAIL','K':'FAIL','F':'PrerequisiteBlocked','H':'PrerequisiteBlocked','L':'PrerequisiteBlocked','G':'Passed compile-only','J':'Passed scoped compile/read-only'},'sourceChanges':[],'retries':0,'extraStimuli':0,'cacheCleanup':False,'TMPDIRChanged':False,'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'ReadyForHumanReviewGate':False,'fullLegacyRegressionAcceptance':False,'pureInterpreterExpansionEnabled':False,'independentFullStageReview':'FAIL','independentReReview':'NotRun'}
save(P/'LOCAL_M_RESULT.json',result)
for name in ['LOCAL_VALIDATION.md','RETURN_TO_WEB.md']:
 f=D/'Docs/AssemblyShadow/Handoff'/name;assert f.read_bytes()==subprocess.check_output(['git','-C',str(D),'show',source+':'+str(f.relative_to(D))]);save(P/(name+'.PRESERVATION.json'),{'path':str(f),'previousCommit':source,'previousSha256':sha(f),'strategy':'Prepend current M; only prior first Current heading relabeled Historical'})
C.mkdir();copies=[];excluded=[]
def copy(f,rel):
 dest=C/rel;dest.parent.mkdir(parents=True,exist_ok=True);assert f.is_file() and not f.is_symlink()
 if f.stat().st_size<=48*1024**2:
  shutil.copyfile(f,dest);copies.append({'originalPath':str(f),'checkpointPath':str(rel),'sha256':sha(f),'bytes':f.stat().st_size,'transport':'exactCopy'})
 else:
  parts=[]
  with f.open('rb') as stream:
   i=0
   while data:=stream.read(32*1024**2):
    part=Path(str(rel)+'.part-%03d'%i);target=C/part;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);parts.append({'path':str(part),'bytes':len(data),'sha256':sha(target)});i+=1
  copies.append({'originalPath':str(f),'checkpointPath':str(rel),'sha256':sha(f),'bytes':f.stat().st_size,'transport':'ordered32MiBParts','parts':parts})
def permitted(f):return not any(x.endswith('.app') for x in f.parts) and f.suffix.lower() not in ['.dll','.dylib','.a','.o','.so','.exe','.pdb','.mdb'] and f.name!='policy'
def transfer(root,prefix,files):
 for f in files:
  assert not f.is_symlink()
  if not f.is_file():continue
  if permitted(f) and f.name!='evidence.tar.gz':copy(f,Path(prefix)/f.relative_to(root))
  else:excluded.append({'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f),'reason':'Exact binary/archive retained locally; published original hashes/receipts, no archive rewrite'})
for root,prefix in [(P,'preflight'),(M,'managed'),(N,'native')]:transfer(root,prefix,sorted(root.rglob('*')))
sys.path.insert(0,str(D/'Tools/AssemblyShadow/R03'));from batch_evidence import selected_files
transfer(R,'batch',selected_files(R))
for name,prefix in [('StorageCheck-R03IRLocal-M-after-L-73bc','storage-diagnostic'),('Storage-R03IRLocal-M-after-L-73bc','storage-execution')]:
 root=B/name;transfer(root,prefix,sorted(root.rglob('*')))
save(C/'COPY_BINDINGS.json',copies);save(C/'FILE_TRANSPORT.json',{'format':'Exact permitted copies; large metadata in ordered32MiB parts','excludedOriginalBinaryAndArchiveFiles':excluded,'coreArchive':next(x for x in a['topArtifacts'] if Path(x['path']).name=='evidence.tar.gz'),'coreArchiveContentUploaded':False,'coreArchiveModified':False,'externalSDK':str(S),'vendorSDKCompilerTreesUploaded':False,'redactions':[],'runtimeRetries':0,'sealClassification':'Original complete bounded local seal; checkpoint metadata is not a replacement archive'})
save(C/'RETAINED_LIVE_ROOTS.json',{'roots':list(map(str,[P,M,N,S,R,B/'StorageCheck-R03IRLocal-M-after-L-73bc',B/'Storage-R03IRLocal-M-after-L-73bc'])),'coreIndexExclusions':a['excludedLiveRoots'],'nativeInventories':[{'role':x['role'],'root':x.get('installedNativeRoot'),'files':x.get('nativeFilesVerified')} for x in a['builds']],'allRetained':True,'excludedContent':'Official vendor SDK, standalone compiler/fixture binaries, complete core archive/apps and all original Library/cache roots remain locally at recorded paths'})
paths=[D/'Docs/AssemblyShadow/README.md',D/'Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md',D/'Docs/AssemblyShadow/Plan/CURRENT_STATUS.md',D/'Tools/AssemblyShadow/R03/source-pins.json']
paths.extend(D/'Tools/AssemblyShadow/R03'/n for n in ['test_batch_contract.py','build_provenance.py','build_api.py','native_validation.py','command_lifetime.py','PlayerProject/R03Build.cs','PlayerProject/AssemblyShadowR03Probe.cpp'])
paths.extend(D/'Tools/AssemblyShadow/R03IR'/n for n in ['run_terminal_local.py','run_terminal_storage_checked.py','bee_observation.py','PlayerProject/R03TerminalPlayer.cs','ir_original_fixtures.py'])
paths.extend(f for f in (hist/'IR_Remediation/IR_LOCAL_INVENTORY_01_2026-10-13').iterdir() if f.is_file())
paths.extend(W/'il2cpp_plus/libil2cpp'/n for n in ['vm/Runtime.cpp','vm/Exception.cpp','vm/Object.cpp','vm/AssemblyShadow.cpp','vm/AssemblyShadow.h','vm/AssemblyShadowFixedBoolean.h','vm/AssemblyShadowTerminalRejection.h','vm/AssemblyShadowTerminalReporting.h','vm/AssemblyShadowEngineReportingProbe.cpp','gc/GarbageCollector.cpp'])
sources=[]
for f in dict.fromkeys(paths):
 repo=next(W/n for n in pins if f.is_relative_to(W/n));rel=f.relative_to(repo);raw=subprocess.check_output(['git','-C',str(repo),'show',pins[repo.name]+':'+str(rel)]);assert raw==f.read_bytes();dest=C/'source-snapshots'/repo.name/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);sources.append({'repository':str(repo),'commit':pins[repo.name],'path':str(rel),'gitBlob':subprocess.check_output(['git','-C',str(repo),'rev-parse',pins[repo.name]+':'+str(rel)],text=True).strip(),'sha256':sha(f),'snapshot':str(dest.relative_to(C))})
save(C/'SOURCE_BINDINGS.json',sources);(C/'.gitattributes').write_text('** -whitespace\n')
link='../History/M07R/R03/'+C.name;table='\n'.join('| `'+str(W/n)+'` | `'+branch+'` | `'+h+'` |' for n,h in pins.items());pcases='\n'.join('| '+x['caseId']+' | '+str(x.get('pid','NotRun'))+' | '+str(x.get('exitCode','NotRun'))+' | '+x['state']+' | '+x['raw']+' / '+x['verification']+' |' for x in a['players']);ex=load(P/'commands/storage-execute/receipt.json');bef=load(P/'scoped-custody-before.json');aft=load(P/'scoped-custody-after.json');av=next(x for x in a['topArtifacts'] if Path(x['path']).name=='evidence.tar.gz')
local=f'''## Current run — M-after-L-73bc focused validation

**{verdict}. Exit: Local Validation → Primary Implementation.** All shared prerequisites, fresh official compilers and two separate storage admissions Passed. One runtime invocation produced {counts}, out of 18 cells; three build roles and five Player cases were retained. Actual outcomes appear below and in [factual result]({link}/preflight/LOCAL_M_RESULT.json), [ledger]({link}/batch/BATCH_EXECUTION.json), [core result]({link}/batch/LOCAL_BATCH_RESULT.json) and [independent evidence audit]({link}/preflight/FINAL_EVIDENCE_AUDIT.json). No retry, source change, cache cleanup, TMPDIR workaround, guard relaxation or extra stimulus. L remains PrerequisiteBlocked.

| Owning repository | Branch | Exact M execution source |
| --- | --- | --- |
{table}

[Source authority]({link}/preflight/SOURCE_AUTHORITY.json) binds independent canonical tops/branches/clean HEADs/origins/worktrees/submodules and exact remote tips. Demo safely fast-forwarded from L publication329040; all seven M roots were absent, canonical and nonaliasing before creation. Actual production bytes equal anchor04a3cd93663f9a4e877a5524d9c22ee5a3fe0131; only approved inventory test/Docs/CI changed. [Test/guard bindings]({link}/preflight/M_INVENTORY_CORRECTION.json): corrected test blobdc58b0ab95e1f3f5b595abfbbd04e100a41047e1; unchanged production guard blob4a9ba7240ded6ad81bcc29ada489ed26cbc2ae50. [Source before]({link}/preflight/SOURCE_PRESERVATION_BEFORE.json)/[after]({link}/preflight/SOURCE_PRESERVATION_AFTER.json) authenticate2,187 pinned source files unchanged during M. [Final source authority]({link}/preflight/FINAL_SOURCE_AUTHORITY.json) is clean and remote-verified before Docs publication. Final pushed Docs HEAD differs from this execution source; external PUBLICATION_RECEIPT.json independently records all four latest pushed heads.

### Fresh host, compiler and preservation gates

[Host receipts]({link}/preflight/HOST_RESULT.json):203 R03 (including29 corrected inventory contracts and20 scratch tests),91 R03IR,25 C custody,9 retained-E,14 collector and one separate sanitized snapshot Passed with zero failures/errors/skips, in prescribed order. Strict/sanitized native rejection, reporting and observer; actual Object.h access;69 policy checks Passed. These host mock/compiler checks do not prove Unity runtime semantics. [Original authentication]({link}/preflight/G_EQUIVALENCE.json) binds C/E/F/G/H/I/J/K/L manifests and immutable Git objects as historical. [S input receipt]({link}/preflight/ORIGINAL_INPUT_PREFLIGHT.json) authenticates15 original DLLs,15,712 index files/15,713 archive members and original top hashes, with no regeneration. R restoration remains Failed; Q retained at its exact root.

[Official managed compile]({link}/preflight/MANAGED_VERIFICATION.json):five product/helper/Player targets Passed; separate expected-negative control exits1 with exactly two CS0266 errors and no DLL.428 input/reference/source hashes and five emitted DLL hashes verified;{result['managedWarnings']} warnings retained. [Official native compile]({link}/preflight/NATIVE_VERIFICATION.json):55/55 C++17 arm64 syntax configurations Passed (11 units × five profiles), no failed/NotRun;1,889 copied SDK/overlay files authenticated;{result['nativeWarnings']} repeated vendor Baselib warnings retained unsuppressed in [warning audit]({link}/preflight/COMPILER_WARNING_AUDIT.json). One invocation per helper; neither syntax compilation establishes native linking/runtime. Vendor SDK/compiler/standalone binaries remain local.

[Environment]({link}/preflight/SOURCE_ENVIRONMENT.json):Unity2022.3.62f2/StandaloneOSX arm64,Python3.14.6,macOS26.5.2 build25F84,Apple clang21.0.0/MacOSX26.5,.NET SDK-only8.0.318. [Inherited environment]({link}/preflight/INHERITED_ENVIRONMENT.json) records unchanged global TMPDIR; only established per-command SDK environment used. Unity6000 was never launched. Every command receipt preserves absolute argv/cwd,pins,PID/PGID,start/end UTC,exit and stream hashes.

Full original C-before `{bef['startedUtc']}`→`{bef['completedUtc']}` and after `{aft['startedUtc']}`→`{aft['completedUtc']}`:416,844 expected files,339,367 physically SHA-verified survivors,77,477 identical original missing identities,zero problems,completeScan=true,ScopedHistoricalLossStable. [Before]({link}/preflight/scoped-custody-before.json)/[after]({link}/preflight/scoped-custody-after.json). Original strict custody remains Blocked; four original S native roots remain Missing. Both E audits and F/G/H/I/J/K/L/SDK preservation Passed; installed SDK2,113 files/109,847,001 bytes unchanged,428 current compiler inputs unchanged. [Preservation after]({link}/preflight/FG_SDK_PRESERVATION_AFTER.json), [E after]({link}/preflight/retained-e-after.json), [original bindings after]({link}/preflight/ORIGINAL_BINDINGS_AFTER.json). Unindexed snapshot is a current comparison, not retroactive build provenance; L after-only census never becomes L before admission.

### One storage-gated runtime execution

One diagnostic-only session Admitted/Passed with batchStarted=false, then one separate executing session freshly Admitted. Original threshold max(64GiB,2×Q+20GiB) and20GiB running floor retained; capacities are observations, not reservations. [Diagnostic]({link}/storage-diagnostic/admission.json), [execute session]({link}/storage-execution/session.json), [dispatch]({link}/storage-execution/dispatch.json). Execute ran once `{ex['startUtc']}`→`{ex['endUtc']}`, exit{ex['exitCode']}. Strict BuildReport error requirements and native/source/app hash checks remain independent of observations.

| Player | PID | Exit | Cell | Raw / verifier |
| --- | --- | --- | --- | --- |
{pcases}

[Runtime diagnosis]({link}/preflight/FAILURE_DIAGNOSIS.json) records actual first-cause/phase/recovery and semantic witness fields, keeping unavailable defaults distinct from proven state. [Bee observations]({link}/preflight/BEE_OBSERVATION_AUDIT.json) retain actual original-factory/driver identities, counts, assembly digests, node outputs and restoration results without suppressing product errors. [Crash evidence]({link}/preflight/CRASH_DIAGNOSIS.json) joins any retained crash by PID/time/request/three Mach-O UUIDs; no extra launch/debug stimulus. Historical I shared-cache emitter remains Unavailable unless direct captured output proves it; a fresh successful Debug build cannot reclassify I.

{diag['summary']}

### Seal, publication and exit

Original bounded seal {a['sealStatus']}: {a['indexedFiles']} indexed files/{a['archiveMembers']} archive members. Archive{av['bytes']} bytes,SHA256 `{av['sha256']}`, retained unchanged at `{av['path']}`. Ledger SHA256 `{sha(R/'BATCH_EXECUTION.json')}`. [Seal]({link}/batch/seal-receipt.json), [live roots]({link}/RETAINED_LIVE_ROOTS.json), [copy/source bindings]({link}/COPY_BINDINGS.json), [source snapshots]({link}/SOURCE_BINDINGS.json), [transport]({link}/FILE_TRANSPORT.json). The full sealed archive/apps, official SDK/vendor/compiler and protected caches stay outside Git; permitted raw logs, receipts, original index/seal and complete binary hashes are published. No replacement or edited archive is fabricated. Seal proves bounded byte custody, not semantics or acceptance.

Only these two Local reports and additive M checkpoint change; historical bodies preserved except first Current→Historical heading. Manifest/JSON/copy/source hashes/links/staged bytes/scope/diff checks precede commit/push. External `{P}/PUBLICATION_VALIDATION.json` and PUBLICATION_RECEIPT.json avoid self-reference and verify final all-four remote publication. **Return to Primary and stop after one M outcome.** E/I/K remain FAIL;F/H/L PrerequisiteBlocked;G/J original scoped Passed;strict S custody Blocked;independent full-stage FAIL/rereview NotRun. All acceptance flags false;PureInterpreter disabled. Captured-generic/initializer,IR-R03-01,normal finalizer/shutdown,full legacy/performance and independent rereview remain outside M. No H2/X02/M08A/Human Review Gate advancement.

'''
ret=f'''## Current return — M-after-L-73bc {verdict}

**Local Validation → Primary Implementation.** [Local report](LOCAL_VALIDATION.md), [checkpoint]({link}/README.md), [factual result]({link}/preflight/LOCAL_M_RESULT.json), [diagnosis]({link}/preflight/FAILURE_DIAGNOSIS.json). Fresh host, full before-custody/preservation, official managed/55-native compiler and separate storage gates Passed. One18-cell/3-build/5-Player attempt; actual cell counts{counts}. Independent after-custody/preservation and original seal passed. No retries/source changes/extra stimulus.

**Common exact reproduction:** four canonical owner paths and source tuple in LOCAL_VALIDATION; demo{source},native{pins['il2cpp_plus']},branch{branch};Unity2022.3.62f2/macOS26.5.2 arm64/.NET8.0.318/Apple clang21. Follow pinned M procedure in order, then exact diagnostic/execute argv and UTC/PID receipts under [execute]({link}/preflight/commands/storage-execute/receipt.json). Runtime root `{R}`. This consumed attempt must not be retried; any new validation needs fresh Primary source/root authority.

'''
if not diag['issues']:ret+='No new nontrivial implementation issue was observed within this focused scope. Primary must reconcile factual M evidence and outstanding full-stage coverage before requesting independent rereview.\n\n'
for issue in diag['issues']:
 ret+='### '+issue['id']+'\n\n'
 for key,label in [('symptom','Symptom'),('evidence','Evidence and relevant excerpts'),('mostLikelyRootCause','Most likely root cause'),('scope','Affected scope'),('direction','Recommended Primary direction'),('uncertainty','Remaining uncertainty'),('validation','Validation after correction')]:ret+='**'+label+':** '+issue[key]+'\n\n'
ret+=f'''Read the exact [diagnosis]({link}/preflight/FAILURE_DIAGNOSIS.json), actual batch players/builds/commands and before/after audits; retain Passed/Failed/Unavailable independently. Historical E/I/K FAIL,F/H/L Blocked,G/J scoped Passed and original strict S custody Blocked remain unchanged. All acceptance flags false;independent full-stage review FAIL/rereview NotRun. Return to Primary and stop;no H2/X02/M08A/expansion/gate approval.\n\n'''
for name,section in [('LOCAL_VALIDATION.md',local),('RETURN_TO_WEB.md',ret)]:
 f=D/'Docs/AssemblyShadow/Handoff'/name;title,body=f.read_text().split('\n\n',1);f.write_text(title+'\n\n'+section+body.replace('## Current ','## Historical ',1))
(C/'README.md').write_text('# M focused Local checkpoint\n\n**'+verdict+'**; one18-cell/three-build/five-Player attempt. Read preflight/LOCAL_M_RESULT.json,FAILURE_DIAGNOSIS.json,FINAL_EVIDENCE_AUDIT.json and before/after/host/compiler receipts. Full raw logs, requests, verifiers, phase/factory evidence, exact source snapshots and SHA inventories retained. FILE_TRANSPORT describes binary/archive content retained outside Git; original full bounded seal is unchanged, not replaced by this metadata checkpoint. PUBLICATION_VALIDATION/PUBLICATION_RECEIPT remain external in the current Preflight root to avoid self-reference. All acceptance flags remain false; historical states unchanged; return Primary.\n')
(C/'MANIFEST.sha256').write_text(''.join(sha(f)+'  '+str(f.relative_to(C))+'\n' for f in sorted(C.rglob('*')) if f.is_file()));print(json.dumps({'state':'Prepared','manifestFiles':len((C/'MANIFEST.sha256').read_text().splitlines()),'manifestSha256':sha(C/'MANIFEST.sha256'),'copiedFiles':len(copies),'binaryArchiveExclusions':len(excluded)}),flush=True)
