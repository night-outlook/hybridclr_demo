from pathlib import Path
import json,hashlib,subprocess,datetime,shutil,os,concurrent.futures
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';BASE=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');P=BASE/'Preflight-R03IRLocal-20261009C-capacity-retry';BOOT=BASE/'IR-R03-02-bootstrap-20261009C-capacity-retry';CHECK=BASE/'StorageCheck-R03IRLocal-20261009C-capacity-retry';B=BASE/'R03IRLocal-20261009C-capacity-retry';STORAGE=BASE/'Storage-R03IRLocal-20261009C-capacity-retry';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-c-custody-blocked';branch='codex/assembly-shadow-r01b-h1'
pins=json.loads((P/'SOURCE_ENVIRONMENT.json').read_text())['pins']
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],timeout=180).decode().strip()
def authority(item):
 name,pin=item;repo=W/name;start=now();commands=[]
 for args in [('rev-parse','--show-toplevel'),('branch','--show-current'),('rev-parse','HEAD'),('status','--short'),('remote','-v'),('worktree','list','--porcelain'),('submodule','status','--recursive'),('ls-remote','origin','refs/heads/'+branch)]:
  a=now();out=git(repo,*args);commands.append({'argv':['git','-C',str(repo),*args],'startUtc':a,'endUtc':now(),'exitCode':0,'stdout':out})
 assert commands[0]['stdout']==str(repo) and commands[1]['stdout']==branch and commands[2]['stdout']==pin and not commands[3]['stdout'];assert commands[-1]['stdout'].split()[0]==pin;assert git(repo,'remote','get-url','origin')=='git@github.com:night-outlook/'+name+'.git'
 return {'path':str(repo),'branch':branch,'commit':pin,'startUtc':start,'endUtc':now(),'state':'Passed','commands':commands}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(authority,pins.items()))
save(P/'FINAL_PREFLIGHT_SOURCE_AUTHORITY.json',{'repositories':rows,'state':'Passed'})
assert not B.exists() and not STORAGE.exists() and not C.exists()
for phase in ['BEFORE','AFTER']:
 r=json.loads((P/f'HISTORICAL_CUSTODY_{phase}.json').read_text());assert r['state']=='Blocked' and r['files']==416844 and len(r['errors'])==77477
ad=json.loads((CHECK/'admission.json').read_text());assert ad['state']=='Admitted' and not ad['batchStarted'];ci=json.loads((P/'CI_EQUIVALENCE_VERIFICATION.json').read_text());assert ci['state']=='Passed'
flags={'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'ReadyForHumanReviewGate':False,'fullLegacyRegressionAcceptance':False,'pureInterpreterExpansionEnabled':False}
result={'kind':'R03IRLocalPrerequisiteResult','recordedUtc':now(),'result':'CustodyBlocked','exitState':'Local Validation -> Primary Implementation','batch':'NotRun','plannedCells':14,'executedCells':0,'builds':{'planned':3,'executed':0,'state':'NotRun'},'players':{'planned':4,'executed':0,'state':'NotRun'},'unityExecution':'NotRun','editMode':'NotRun','il2cppNativeBuild':'NotRun','irTargetGeneration':'NotRun','activeMethodSideEffects':'NotRun','sourceAuthority':'Passed','originalSInputs':{'state':'Passed','fixtures':15,'classification':'ReusedAudited immutable Git inputs'},'hostPythonTests':{'state':'Passed','count':64},'nativePolicyChecks':{'state':'Passed','count':69,'runtimeAcceptance':False},'custody':{'before':'Blocked','after':'Blocked','uniqueFiles':416844,'missingFiles':77477,'presentFilesVerified':339367,'missingInventoryRebased':False},'currentPlayerApiCoverage':'Passed','sourceBoundCIPreflight':'Passed','diagnosticWrapperExit':0,'storageAdmission':'Admitted','storageSession':'Passed','executionWrapperInvocations':0,'coreResult':'Unavailable','ledger':'Unavailable','coreIndexArchiveSeal':'Unavailable','capacity':{'firstObservedAvailableBytes':83657576448,'requiredBytes':68719476736,'deficitBytes':0,'headroomAbovePolicyBytes':14938099712,'formula':'max(64GiB,2*Q+20GiB)','QPlanningBytes':14164955136,'operatingFloorBytes':21474836480,'capacityReserved':False},'sources':rows,'evidenceRoots':{'bootstrap':str(BOOT),'preflight':str(P),'diagnostic':str(CHECK),'absentBatch':str(B),'absentExecutingStorage':str(STORAGE)},'historicalReclassification':False,'boundedFixes':[],'independentFullStageReview':'FAIL',**flags}
save(P/'LOCAL_PREFLIGHT_RESULT.json',result)
footprint=sum(f.stat().st_size for root in [P,BOOT,CHECK] for f in root.rglob('*') if f.is_file());v=os.statvfs(D);available=v.f_bavail*v.f_frsize;required=2*footprint+20*1024**3;assert available>=required
save(P/'PUBLICATION_CAPACITY.json',{'recordedUtc':now(),'state':'Passed','purpose':'Small prerequisite checkpoint publication only; never runtime storage admission','payloadBytesBeforeThisReceipt':footprint,'requiredBytes':required,'availableBytes':available,'formula':'2*prerequisitePayload+20GiB','capacityReserved':False,'runtimeExecutionBlockedByCustody':True})
preservation=[]
for name in ['LOCAL_VALIDATION.md','RETURN_TO_WEB.md']:
 f=D/'Docs/AssemblyShadow/Handoff'/name;raw=f.read_bytes();obj=subprocess.check_output(['git','-C',str(D),'show',pins['hybridclr_demo']+':'+str(f.relative_to(D))]);assert raw==obj;save(P/(name+'.PRESERVATION.json'),{'path':str(f),'previousSha256':sha(f),'previousCommit':pins['hybridclr_demo'],'strategy':'Prepend current report; relabel only prior first Current heading Historical; preserve every other prior byte'})
C.mkdir();bindings=[];transport=[]
for label,root in [('preflight',P),('bootstrap',BOOT),('storage-diagnostic',CHECK)]:
 for f in sorted(root.rglob('*')):
  assert not f.is_symlink()
  if not f.is_file():continue
  rel=Path(label)/f.relative_to(root);h=sha(f);size=f.stat().st_size
  if size>48*1024**2:
   parts=[]
   with f.open('rb') as stream:
    i=0
    while chunk:=stream.read(32*1024**2):
     part=Path(str(rel)+f'.part{i:03d}');dest=C/part;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(chunk);parts.append({'path':str(part),'bytes':len(chunk),'sha256':sha(dest)});i+=1
   total=hashlib.sha256()
   for part in parts:total.update((C/part['path']).read_bytes())
   assert total.hexdigest()==h
   transport.append({'originalPath':str(f),'logicalCheckpointPath':str(rel),'bytes':size,'sha256':h,'parts':parts});bindings.append({'originalPath':str(f),'sha256':h,'bytes':size,'transport':'orderedParts','parts':parts})
  else:
   dest=C/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest);assert sha(dest)==h;bindings.append({'originalPath':str(f),'checkpointPath':str(rel),'sha256':h,'bytes':size,'transport':'exactCopy'})
save(C/'COPY_BINDINGS.json',bindings);save(C/'FILE_TRANSPORT.json',{'format':'Ordered byte chunks; concatenate in listed order without decoding; verify original SHA256','files':transport})
sourceBindings=[]
sourcePaths=[Path(x['path']) for x in json.loads((CHECK/'source-authority.json').read_text())['sourceFiles']]
E=D/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_LOCAL_API_01_2026-10-09'
sourcePaths.extend(E/f for f in ['README.md','EVIDENCE.json','compile-inputs.json','compile-result.json','build.log.gz.b64','PRIMARY_SYNTHETIC_CHECKS.json'])
sourcePaths.extend(W/x['repository'].split('/')[1]/x['path'] for x in ci['inputs'])
sourcePaths.extend([D/'Docs/AssemblyShadow/README.md',D/'Docs/AssemblyShadow/Plan/CURRENT_STATUS.md',D/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_R03_02_FOCUSED_LOCAL_PROCEDURE_2026-10-09.md',W/'il2cpp_plus/tools/r03/terminal_execution_tests.cpp',W/'il2cpp_plus/libil2cpp/vm/AssemblyShadowTerminalExecution.h'])
for f in dict.fromkeys(sourcePaths):
 repo=next(W/n for n in pins if f.is_relative_to(W/n));name=repo.name;rel=f.relative_to(repo);raw=subprocess.check_output(['git','-C',str(repo),'show',pins[name]+':'+str(rel)]);assert raw==f.read_bytes();dest=C/'source-snapshots'/name/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);sourceBindings.append({'repository':str(repo),'commit':pins[name],'path':str(rel),'gitBlob':git(repo,'rev-parse',pins[name]+':'+str(rel)),'sha256':sha(f),'snapshot':str(dest.relative_to(C))})
save(C/'SOURCE_BINDINGS.json',sourceBindings)
(C/'.gitattributes').write_text('bootstrap/** -whitespace\npreflight/** -whitespace\nstorage-diagnostic/** -whitespace\nsource-snapshots/** -whitespace\n')
(C/'README.md').write_text('''# IR-R03-02 C Local prerequisite checkpoint — 2026-10-09

**CustodyBlocked; runtime batch NotRun. Storage diagnostic Admitted.** The human request "disk space freed, retry local validation" authorized a fresh C attempt from the pushed B documentation publication, preserving all source and custody guards. CONTINUATION_AUTHORIZATION.json records the request and unused roots. This is additive prerequisite evidence, not a sealed runtime batch.

Fresh exact four-owner authority, 64 Python tests, 69 native policy checks, 15 immutable S fixture admissions and all 22 current CSharp CI input bindings Passed. Diagnostic wrapper exit 0, admission Admitted, session Passed and all 11 allocation/sync/readback probes Passed. Capacity was 83,657,576,448 bytes (77.912 GiB) versus 68,719,476,736 required. Capacity was not reserved and no executing invocation was permitted.

Both custody audits are Blocked: 416,844 expected files, 339,367 present verified, 77,477 Missing and 0 changed. All Missing paths are retained S unindexed Library/HybridCLRData snapshots; before/after error rows match exactly. Four historical focused installed-native roots are absent. S's five top artifacts, all 15,712 indexed files and original sealed archive still authenticate. The missing paths are absent from that archive, so it cannot restore them. The deletion actor and exact time are Unavailable. No missing-file rebaselining, historical regeneration, automatic recovery or product change occurred.

Read preflight/LOCAL_PREFLIGHT_RESULT.json, HISTORICAL_CUSTODY_BEFORE.json, HISTORICAL_CUSTODY_AFTER.json, CUSTODY_FAILURE_ANALYSIS.json, NATIVE_LIVE_CUSTODY_LIMIT.json, CI_EQUIVALENCE_VERIFICATION.json and storage-diagnostic/admission.json. Raw historicalRootsModified=false describes audit write behavior, not intact custody. The initial analysis's null installedSdkRoot fields are supplemented by NATIVE_LIVE_CUSTODY_LIMIT.json reading each actual installedNativeRoot receipt. All 14 runtime cells, three builds and four Players are NotRun; core result/ledger/index/archive/seal Unavailable; zero Unity launches.

COPY_BINDINGS authenticates exact live originals. FILE_TRANSPORT preserves the large prior custody map as ordered byte chunks; concatenate without decoding and verify its original SHA256. Both complete failure JSON files are exact copies. MANIFEST.sha256 covers every checkpoint file except itself. API CI used Unity stubs, not official managed assemblies or runtime. Prior native/API/fixture CI remains ReusedAudited; distinct IR target generation and post-poison side-effect proof remain NotRun.

A/B failures and S/R/Q/P/O/N historical results are not rewritten. R remains staged; S historical 90 Passed, current missing retained caches and independent full-stage review FAIL remain distinct. All acceptance flags false; PureInterpreter expansion disabled. Primary must resolve custody recovery or an explicit scoped disposition before a fresh authorized runtime handoff. Next owner: Primary Implementation; stop after C.
''')
link='../History/M07R/R03/'+C.name
table='\n'.join('| `'+str(W/n)+'` | `'+branch+'` | `'+h+'` |' for n,h in pins.items())
receipt=json.loads((P/'commands/storage-diagnostic/receipt.json').read_text());host=json.loads((P/'LOCAL_HOST_PREFLIGHT.json').read_text());before=json.loads((P/'HISTORICAL_CUSTODY_BEFORE.json').read_text());after=json.loads((P/'HISTORICAL_CUSTODY_AFTER.json').read_text());analysis=json.loads((P/'CUSTODY_FAILURE_ANALYSIS.json').read_text())
assert before['errors']==after['errors'];assert analysis['missingFiles']==77477 and analysis['changedFiles']==0 and analysis['sealedS']['indexedErrors']==[]
scopes='\n'.join('| `'+n+'` | '+str(count)+' |' for n,count in analysis['missingByScope'].items())
local=f'''## Current run — IR-R03-02 C capacity retry prerequisites, 2026-10-09 PDT / UTC

**CustodyBlocked; focused runtime batch NotRun. Storage diagnostic Admitted. Exit: Local Validation → Primary Implementation.** The human's direct request “disk space freed, retry local validation” authorized one fresh C attempt using new sibling roots and the latest pushed B documentation commit. It did not authorize removing protected data, rebasing custody or bypassing failed prerequisites. [Authorization and roots]({link}/bootstrap/CONTINUATION_AUTHORIZATION.json), [factual result]({link}/preflight/LOCAL_PREFLIGHT_RESULT.json), [additive C checkpoint]({link}/README.md).

No --execute invocation or Unity launch occurred. All 14 cells, three IL2CPP/native build roles and four fresh Players are NotRun; target generation, Editor/runtime side-effect checks and seal are NotRun or Unavailable. Capacity passed independently; custody prevented dispatch. This is a new prerequisite observation, not a successful runtime validation or a retry of A/B.

| Actual owning repository | Branch | Exact C prerequisite source commit |
| --- | --- | --- |
{table}

Every clean checkout independently passed top/branch/HEAD/status/canonical SSH origin/worktree/submodule and fresh remote-tip checks. Demo source `e6f918bf6c756251982eef47f255eaa71b11e1d4` is the verified pushed B Local evidence publication, a Docs-only descendant of Primary `434ed7ff92951881fcdc7ebbb046c900e6a1d7d2` and compiled anchor `ba47b41674b83a6f694ac4f8ac1bc8f83a9da24b`. Product/native/package/fixture/runner/storage inputs are unchanged. No switch/reset/stash/clean, credential or protocol change. [Sync authority]({link}/bootstrap/SYNC_AUTHORITY.json), [final source authority]({link}/preflight/FINAL_PREFLIGHT_SOURCE_AUTHORITY.json), [Git blobs/source snapshots]({link}/SOURCE_BINDINGS.json). Validation source and final documentation publication are distinct; the final pushed heads are in the external publication receipt.

### Prerequisite and dependent execution states

| Validation | Actual state and coverage |
| --- | --- |
| Source, remote and compiler-input authentication | Passed, all four owners and 22 compiler inputs / 19 explicit CSharp inputs |
| Prescribed fresh Python host tests | Passed, 64 tests, no skips/errors/failures |
| Fresh standalone native policy compile/run | Passed, 69 checks; not product AssemblyShadow.cpp or Unity Player execution |
| Original S immutable fixture DLLs | Passed, 15 authenticated original Git inputs, ReusedAudited; no regeneration |
| Protected custody before and after | Blocked, 416,844 expected / 339,367 present verified / 77,477 Missing / 0 changed |
| Diagnostic storage without --execute | Exit 0, Admitted, session Passed, 11 allocation/sync/readback probes Passed, batchStarted=false |
| Executing storage / Unity / Editor / IL2CPP builds / Players | NotRun, zero --execute invocations and Unity launches |
| IR target generation / active-method side-effect checks | NotRun |
| Runtime result / ledger / index / archive / seal | Unavailable; no synthetic runtime cells or seal |

[Host command receipts]({link}/preflight/LOCAL_HOST_PREFLIGHT.json) include exact argv/cwd, start/end, exits, source/header/binary and stream hashes. Host suite/native checks ran `{host['commands'][-3]['startUtc']}` through `{host['commands'][-1]['endUtc']}`. [Environment]({link}/preflight/SOURCE_ENVIRONMENT.json) records macOS 26.5.2 build 25F84, Python 3.14.6, Apple clang 21.0.0, CommandLineTools and MacOSX SDK. Exact Unity 2022.3.62f2 `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity` was verified present, never launched; planned StandaloneOSX arm64 NotRun. SDK 8.0.318 is used only from `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`; Unity 6000 never launched. Temp remains `/private/tmp`; shared APFS paths are not additional capacity.

[Current-source API receipt]({link}/preflight/CI_CURRENT_SOURCE.json) and [independent live-job/input verification]({link}/preflight/CI_EQUIVALENCE_VERIFICATION.json) matched CI 37903041633/job 113729828150 at compiled anchor ba47: 0 errors/13 warnings; all 22 current tracked input hashes/Git blobs match. Current Player SHA256 `22c3e0be7cebc041706b1412c5fc317c806c49a0980be143d5517dc4cc59a7bd`, exact lossless full compiler log SHA256 `a2805d2bf18a7004f5cb1b2197b8fba3f9f1edb4fac6f4ec2fc0d27dc820ae72`. **CI used SDK 10.0.401, net8.0/CSharp9/UNITY_EDITOR and Unity API stubs.** It is not official Unity managed compilation or runtime acceptance. Actual decoded connector job-log copy has a normalized final newline; durable compiler log matches original bytes. CI binaries/ZIP/binlog were not downloaded by Local; Primary's artifact authentication and 11 synthetic receipt tests remain attributed. Previous native/API/fixture logs remain ReusedAudited with unchanged relevant source bytes; old API 37874183375 remains historical NoCoverage.

[Original fixture authentication]({link}/preflight/ir-original-s-fixture-authority.json) SHA256 `1371afaeafa220934eb6b3ddc05c9acbc09a3270dc08f93405ffa0fe58a410b6` binds all 15 original DLLs, S publication `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b` and inventory Git blob `0688bd2dad054bd59fcdd1564a050a398cfa14e7`. Admission ran 2026-10-09T10:36:06.917033+00:00→10:36:07.517993+00:00. Expected distinct IR target SHA256 `8d0b28cbca4d889801883ad436c51c215b913f1645055590980f902f1e80fffd`, MVID `597eb18e-e0e7-6f8b-7e4a-6cdaabf9d1ff`, 2048 bytes/zero PE timestamp remains expectation only; fresh generation NotRun. Historical Failed/NotIdentical regeneration is unchanged.

### Custody blocker and preserved sealed evidence

[Before custody]({link}/preflight/HISTORICAL_CUSTODY_BEFORE.json) ran `{before['startUtc']}`→`{before['endUtc']}`, SHA256 `b44e3c3ae6abc0e79d222c459c5463a6fd0fa186996f1dd2b7ac85a8963df2fe`. [After custody]({link}/preflight/HISTORICAL_CUSTODY_AFTER.json) ran `{after['startUtc']}`→`{after['endUtc']}`, SHA256 `86a5e926841b50e3edb337c4a0a22bd3a6a6dd1484ad40d2f926c0c72161603b`. Both complete raw reports retain the same 77,477 Missing rows; no differences among the 339,367 present files. The original B map is authenticated from immutable Git objects and additive copied/live bindings; C did not rebaseline missing files. [Map binding]({link}/preflight/CUSTODY_MAP_BINDING.json) and [failure analysis]({link}/preflight/CUSTODY_FAILURE_ANALYSIS.json) preserve expected hashes and full scope.

All missing paths are under `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery`:

| S-relative retained scope | Missing files |
| --- | --- |
{scopes}

Example exact missing path: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery/projects/reference-release/Library/SourceAssetDB-lock`, expected SHA256 `edf459865e56bd3bc68b0db5dcf4630ea85928a07216e8a93f32df6dfe559fda`. Historical stripped native file `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery/projects/reference-release/HybridCLRData/StrippedAOTDllsTempProj/StandaloneOSX/Il2CppOutputProject/IL2CPP/libil2cpp/vm/AssemblyShadow.cpp` is Missing, expected SHA256 `facdfa76e7b90b88e94cb060b6072c0d73d66f8f9b740b3644f5224085fe93f2`.

[NATIVE_LIVE_CUSTODY_LIMIT]({link}/preflight/NATIVE_LIVE_CUSTODY_LIMIT.json) confirms candidate-debug/candidate-off/candidate-release/reference-release schema-2 receipts retain exact original hashes but all four receipt-bound `projects/<role>/HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp` roots are now Missing. This supplements the initial analysis's null generic installedSdkRoot fields with each actual installedNativeRoot field; no historical receipt was rewritten. Current native owner is correct at 9ce1, while S executed against historical IL2CPP `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`; installing current bytes cannot restore historical provenance.

**S sealed evidence byte/index audit Passed separately:** all five top-level artifact hashes match, all 15,712 indexed files verify, archive 587,907,380 bytes / 15,713 members, SHA256 `23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6`. Every indexed path is present in the archive. Missing-path intersection with index/archive is zero; these unindexed retained caches cannot be recovered from that archive. Historical S 90 Passed is unchanged, not current custody or full-stage acceptance. R's six-file read-only audit Passed and remains staged with its original Failed restore; no repair. A/B/Q/P/O/N present protected evidence matches. Deletion actor and exact time are Unavailable; only the interval after B's Passed audit and before C's Blocked audit is established.

Raw historicalRootsModified=false means the audit made no writes, **not** that custody is intact. The first custody terminal output was large; [administrative output bounding]({link}/preflight/ADMINISTRATIVE_OUTPUT_BOUNDING.json) records external helper-only compact stdout for the after check, preserving all raw JSON rows and the original helper. No source/expectation/cleanup/timeout rule changed, no failed audit rerun, no automatic cache regeneration, recovery, relocation or missing-map reduction. No new product-source defect is established.

### Fresh storage diagnostic and publication

Diagnostic `{receipt['startUtc']}`→`{receipt['endUtc']}` exited 0; [exact wrapper command/streams]({link}/preflight/commands/storage-diagnostic/receipt.json) used source e6, exact workspace/Unity, retained Q and unused C output roots **without --execute**. It ran independently to measure capacity despite custody failure. [Admission]({link}/storage-diagnostic/admission.json) SHA256 `29fb9b1923d63c47736f502680b8f3e3d580614341cc40b87695fc3e5b6b8d2a`: available 83,657,576,448 bytes (77.912 GiB), required 68,719,476,736 bytes (64 GiB), headroom 14,938,099,712 bytes (13.912 GiB). Unchanged formula max(64GiB,2*Q+20GiB), Q planning 14,164,955,136 bytes, operating floor 20 GiB. All 11 owned allocation/sync/readback probes Passed and owned probe cleanup Passed. No historical cleanup, threshold change or reservation; diagnostic success alone cannot dispatch through custody failure.

[Capacity samples]({link}/storage-diagnostic/capacity.jsonl), [session]({link}/storage-diagnostic/session.json) SHA256 `d776da3cfb36140a2dd5f296602caa8273f982352fe0e7c3eea6b261de5a578f` and [dispatch]({link}/storage-diagnostic/dispatch.json) SHA256 `e993ddaa8df05a63a4dd40524a973c7d4742aa0b1565061ca74cfc114231a16f` retain Passed/Admitted versus batchStarted=false and coreResult=null. Directory diskutil-info queries remain Unavailable; df/APFS-list observations captured.

Live C evidence: preflight `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261009C-capacity-retry`, diagnostic `/Users/ah/GitHub/hybridclr/r03-local-validation/StorageCheck-R03IRLocal-20261009C-capacity-retry`, bootstrap `/Users/ah/GitHub/hybridclr/r03-local-validation/IR-R03-02-bootstrap-20261009C-capacity-retry`. All C candidate roots were initially absent/nonaliasing. Requested batch `/Users/ah/GitHub/hybridclr/r03-local-validation/R03IRLocal-20261009C-capacity-retry` and executing-storage `/Users/ah/GitHub/hybridclr/r03-local-validation/Storage-R03IRLocal-20261009C-capacity-retry` remain absent. No ordinary primary/control checkout or historical app/Library/native state was used for execution.

[Exact copy bindings]({link}/COPY_BINDINGS.json), [ordered large-map transport]({link}/FILE_TRANSPORT.json), source snapshots and MANIFEST.sha256 preserve the additive C checkpoint; both complete 46 MB failure reports are exact copies. Small publication capacity verification covers checkpoint bytes only, not runtime reservation. Only Local-owned reports/checkpoint changed; no bounded product fix. Manifest/JSON/hash/link/diff/staged-byte/scope checks and final pushed heads are recorded externally at `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261009C-capacity-retry/PUBLICATION_VALIDATION.json` and `PUBLICATION_RECEIPT.json`. Historical report bodies are preserved apart from first Current heading relabeling.

R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; PureInterpreter expansion disabled. Independent full-stage review remains FAIL, separate re-review NotRun; genuine captured-generic/initializer cases and IR-R03-01 remain Primary work. No H2/X02/M08A. Primary must resolve the custody issue below; Local stops after C.

'''
ret=f'''## Current return — IR-R03-02 C, 2026-10-09

**CustodyBlocked; focused runtime batch NotRun. Storage admission Passed.** [Local report](LOCAL_VALIDATION.md), [additive C checkpoint]({link}/README.md), [factual result]({link}/preflight/LOCAL_PREFLIGHT_RESULT.json). Source/remote and 22 current API inputs, fresh 64 Python tests / 69 native checks and 15 immutable S fixture DLLs Passed. Diagnostic exit 0, Admitted, 11 probes Passed. No --execute or Unity launch; all 14 cells / three builds / four Players NotRun, core result/seal Unavailable. No new product-source failure is established.

### IR-LOCAL-CUSTODY-01 — missing protected S retained cache/native roots

**Symptom and impact:** both fresh custody audits found exactly 77,477 Missing of 416,844 protected files; 339,367 present verify and 0 changed. Missing data spans 12 retained S Library/HybridCLRData groups, including all four focused receipt-bound installedNativeRoot paths. This violates the prerequisite requiring protected evidence preservation and blocks new execution, even though capacity now passes.

**Reproduction:** authenticate prior B custody map/chunks against immutable demo `e6f918bf6c756251982eef47f255eaa71b11e1d4`; use C COPY_BINDINGS/FILE_TRANSPORT to reconstruct prior-evidence-custody.json, verify SHA256 `133cba8a9b54b74a9909c6da6948838f8f604afea47bc61bdee88f45c22df0e8`; inspect the complete before/after Missing rows and compare their expected path/hash with current filesystem existence. Example `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery/projects/reference-release/Library/SourceAssetDB-lock` is absent, expected SHA256 `edf459865e56bd3bc68b0db5dcf4630ea85928a07216e8a93f32df6dfe559fda`. Also absent: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery/projects/reference-release/HybridCLRData/StrippedAOTDllsTempProj/StandaloneOSX/Il2CppOutputProject/IL2CPP/libil2cpp/vm/AssemblyShadow.cpp`, expected SHA256 `facdfa76e7b90b88e94cb060b6072c0d73d66f8f9b740b3644f5224085fe93f2`.

**Evidence:** [before report]({link}/preflight/HISTORICAL_CUSTODY_BEFORE.json), SHA256 `b44e3c3ae6abc0e79d222c459c5463a6fd0fa186996f1dd2b7ac85a8963df2fe`, 2026-10-09T10:36:05.400602+00:00→10:36:42.984168+00:00; [after report]({link}/preflight/HISTORICAL_CUSTODY_AFTER.json), SHA256 `86a5e926841b50e3edb337c4a0a22bd3a6a6dd1484ad40d2f926c0c72161603b`, 10:42:46.085930+00:00→10:43:22.502599+00:00. Exact excerpt: state=Blocked, files=416844, errors=77477; before/after error rows equal. [Scope/sealed audit]({link}/preflight/CUSTODY_FAILURE_ANALYSIS.json) and [actual native-root receipts]({link}/preflight/NATIVE_LIVE_CUSTODY_LIMIT.json) enumerate paths and original build receipt hashes.

**Likely cause and uncertainty:** retained data was removed outside C's read-only audit between B's successful custody observation and C's failed observation. Actor, precise time, cleanup command and existence of a recoverable copy are Unavailable. This is an evidence-custody issue, not proof of a product runtime defect. No Local restoration, regeneration or map rebaselining occurred. Raw historicalRootsModified=false only describes no audit writes.

**Affected scope and intact evidence:** all missing files are unindexed S retained caches. S's five top artifacts and all 15,712 indexed files authenticate; its original 587,907,380-byte sealed archive remains SHA256 `23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6`, all indexed paths covered, zero missing-path intersection. It does not contain the missing caches. Four schema-2 build receipts remain intact but reference absent `projects/<candidate-debug|candidate-off|candidate-release|reference-release>/HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp` roots. S historical runtime source was demo `29bb3d4a39bf8a2f23be404f77535aaba3485bfc`, native IL2CPP `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`; current native 9ce1 is different. A/B/Q/P/O/N present files verify; R remains staged and unchanged, original restore Failed. S historical 90 Passed is preserved separately from today's custody failure and full-stage review FAIL.

**Recommended Primary direction:** locate and authenticate a byte-identical recovery under the original S source/native/build pins, or obtain an explicit scoped custody disposition/exception that retains the complete Missing report and records loss of live installed-SDK provenance. Assess that limit in independent review. Do not reconstruct historical roots with current native sources, regenerate S caches, silently shrink/rebase the protected inventory or claim full custody Passed. Only after this is resolved may Primary issue a distinct fresh source-bound handoff/root; do not retry C.

**Validation remaining:** after recovery, verify every restored expected byte and all protected hashes; after an explicitly approved disposition, retain Missing states and document its exact scope. A new authorized attempt must freshly pass source/host/API/fixture/custody and storage prerequisites before one 14-cell / three-build / four-Player batch, including active same-method pre-poison controls, readable counter2 after rejected reflection/delegate calls, unchanged AOT canary, first failure/state/generation/diagnostics, OFF control, source/build/request/PID bindings and seal. API stub compilation is not Unity or runtime acceptance. Genuine captured-generic/initializer coverage, IR-R03-01 and independent full-stage review remain separately unclosed.

All acceptance flags remain false; PureInterpreter expansion disabled. No Local product change or H2/X02/M08A. **Local Validation → Primary Implementation; stop after C.**

'''
for name,section,title in [('LOCAL_VALIDATION.md',local,'# Local Validation report'),('RETURN_TO_WEB.md',ret,'# Local Validation → Primary Implementation')]:
 f=D/'Docs/AssemblyShadow/Handoff'/name;old=f.read_text();prefix=title+'\n\n';assert old.startswith(prefix);body=old[len(prefix):].replace('## Current ','## Historical ',1);f.write_text(prefix+section+body)
for f in C.rglob('*.json'):json.loads(f.read_text())
manifest=''.join(sha(f)+'  '+str(f.relative_to(C))+'\n' for f in sorted(C.rglob('*')) if f.is_file());(C/'MANIFEST.sha256').write_text(manifest)
for line in manifest.splitlines():h,name=line.split('  ',1);assert sha(C/name)==h
save(P/'PUBLICATION_PREPARATION.json',{'recordedUtc':now(),'state':'Passed','checkpoint':str(C),'manifestSha256':sha(C/'MANIFEST.sha256'),'files':len(manifest.splitlines()),'copies':len(bindings),'runtimeExecution':False,'coreSeal':'Unavailable','sourceChanged':False})
print(json.dumps({'checkpoint':str(C),'files':len(manifest.splitlines()),'manifestSha256':sha(C/'MANIFEST.sha256'),'state':'Prepared'}))
