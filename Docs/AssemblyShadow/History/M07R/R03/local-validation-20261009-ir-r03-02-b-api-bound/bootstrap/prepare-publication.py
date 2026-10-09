from pathlib import Path
import json,hashlib,subprocess,datetime,shutil,os,concurrent.futures
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';BASE=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');P=BASE/'Preflight-R03IRLocal-20261009B-api-bound';BOOT=BASE/'IR-R03-02-bootstrap-20261009B-api-bound';CHECK=BASE/'StorageCheck-R03IRLocal-20261009B-api-bound';B=BASE/'R03IRLocal-20261009B-api-bound';STORAGE=BASE/'Storage-R03IRLocal-20261009B-api-bound';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-b-api-bound';branch='codex/assembly-shadow-r01b-h1'
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
 r=json.loads((P/f'HISTORICAL_CUSTODY_{phase}.json').read_text());assert r['state']=='Passed' and r['files']==416515 and not r['errors']
ad=json.loads((CHECK/'admission.json').read_text());assert ad['state']=='Blocked' and not ad['batchStarted'];ci=json.loads((P/'CI_EQUIVALENCE_VERIFICATION.json').read_text());assert ci['state']=='Passed'
flags={'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'ReadyForHumanReviewGate':False,'fullLegacyRegressionAcceptance':False,'pureInterpreterExpansionEnabled':False}
result={'kind':'R03IRLocalPrerequisiteResult','recordedUtc':now(),'result':'CapacityBlocked','exitState':'Local Validation -> Primary Implementation','batch':'NotRun','plannedCells':14,'executedCells':0,'builds':{'planned':3,'executed':0,'state':'NotRun'},'players':{'planned':4,'executed':0,'state':'NotRun'},'unityExecution':'NotRun','editMode':'NotRun','il2cppNativeBuild':'NotRun','irTargetGeneration':'NotRun','activeMethodSideEffects':'NotRun','sourceAuthority':'Passed','originalSInputs':{'state':'Passed','fixtures':15,'classification':'ReusedAudited immutable Git inputs'},'hostPythonTests':{'state':'Passed','count':64},'nativePolicyChecks':{'state':'Passed','count':69,'runtimeAcceptance':False},'custody':{'before':'Passed','after':'Passed','uniqueFiles':416515},'currentPlayerApiCoverage':'Passed','sourceBoundCIPreflight':'Passed','diagnosticWrapperExit':2,'storageAdmission':'Blocked','storageSession':'NotAdmitted','executionWrapperInvocations':0,'coreResult':'Unavailable','ledger':'Unavailable','coreIndexArchiveSeal':'Unavailable','capacity':{'firstObservedAvailableBytes':67720581120,'requiredBytes':68719476736,'deficitBytes':998895616,'formula':'max(64GiB,2*Q+20GiB)','QPlanningBytes':14164955136,'operatingFloorBytes':21474836480,'capacityReserved':False},'sources':rows,'evidenceRoots':{'bootstrap':str(BOOT),'preflight':str(P),'diagnostic':str(CHECK),'absentBatch':str(B),'absentExecutingStorage':str(STORAGE)},'historicalReclassification':False,'boundedFixes':[],'independentFullStageReview':'FAIL',**flags}
save(P/'LOCAL_PREFLIGHT_RESULT.json',result)
footprint=sum(f.stat().st_size for root in [P,BOOT,CHECK] for f in root.rglob('*') if f.is_file());v=os.statvfs(D);available=v.f_bavail*v.f_frsize;required=2*footprint+20*1024**3;assert available>=required
save(P/'PUBLICATION_CAPACITY.json',{'recordedUtc':now(),'state':'Passed','purpose':'Small prerequisite checkpoint publication only; never runtime storage admission','payloadBytesBeforeThisReceipt':footprint,'requiredBytes':required,'availableBytes':available,'formula':'2*prerequisitePayload+20GiB','capacityReserved':False,'runtimeAdmissionStillBlocked':True})
preservation=[]
for name in ['LOCAL_VALIDATION.md','RETURN_TO_WEB.md']:
 f=D/'Docs/AssemblyShadow/Handoff'/name;raw=f.read_bytes();obj=subprocess.check_output(['git','-C',str(D),'show',pins['hybridclr_demo']+':'+str(f.relative_to(D))]);assert raw==obj;save(P/(name+'.PRESERVATION.json'),{'path':str(f),'previousSha256':sha(f),'previousCommit':pins['hybridclr_demo'],'strategy':'Prepend current report; relabel only prior first Current heading Historical; preserve every other prior byte'})
C.mkdir();bindings=[];transport=[]
for label,root in [('preflight',P),('bootstrap',BOOT),('storage-diagnostic',CHECK)]:
 for f in sorted(root.rglob('*')):
  assert not f.is_symlink()
  if not f.is_file():continue
  rel=Path(label)/f.relative_to(root);h=sha(f);size=f.stat().st_size
  if size>32*1024**2:
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
(C/'README.md').write_text('''# IR-R03-02 B Local prerequisite checkpoint — 2026-10-09

**CapacityBlocked; batch NotRun.** This additive prerequisite checkpoint is not a sealed runtime batch. Diagnostic wrapper exit2, admission Blocked, session NotAdmitted, batchStarted=false; zero execution-wrapper invocations and zero Unity launches. All14 cells/3 builds/4 Players are NotRun; core result/ledger/index/archive/seal are Unavailable.

Read preflight/LOCAL_PREFLIGHT_RESULT.json, preflight/CI_CURRENT_SOURCE.json, preflight/CI_EQUIVALENCE_VERIFICATION.json, both custody receipts, and storage-diagnostic/admission.json. All22 current compiler inputs matched the actual successful CI37903041633 at ba47, with0 errors/13 warnings. This is net8/CSharp9 real-package compilation using Unity API stubs, not official Unity managed compilation or runtime execution. Local passed64 Python tests and69 standalone native policy checks,15 original S fixture admissions, and416,515-file custody before/after. Prior native/API/fixture logs were reused-audited with unchanged relevant source bytes; no new CI execution is inferred.

Storage observed67,720,581,120bytes available against68,719,476,736 required, deficit998,895,616bytes. Unchanged max(64GiB,2*Q+20GiB) and20GiB floor; allocation probes NotRun; no cleanup, threshold change or reservation. A and S/R/Q/P/O/N are preserved; retained R remains staged. A's original CapacityBlocked/NoCoverage is unchanged. B's current-body compile coverage Passed is a separate successor observation.

COPY_BINDINGS maps exact original live paths and SHA256. FILE_TRANSPORT lists byte chunks for the large protected map; concatenate in listed order outside the checkpoint and verify the original SHA256. MANIFEST.sha256 authenticates all checkpoint files except itself. Raw captures retain bytes; the separately decoded connector job log has a normalized final newline. The durable compiler-build.log is losslessly decoded and matches the published original hash. CI binaries/ZIP/binlog were not downloaded by Local; Primary artifact verification remains attributed, with expiry noted in its EVIDENCE.json.

No product fix or phase/admission retry. Distinct IR target generation and active-method side-effect proof are NotRun. Independent full-stage review remains FAIL, separate re-review NotRun, all acceptance flags false, PureInterpreter expansion disabled. Next owner: Primary Implementation; stop after B.
''')
link='../History/M07R/R03/'+C.name
table='\n'.join('| `'+str(W/n)+'` | `'+branch+'` | `'+h+'` |' for n,h in pins.items())
receipt=json.loads((P/'commands/storage-diagnostic/receipt.json').read_text());host=json.loads((P/'LOCAL_HOST_PREFLIGHT.json').read_text());sourceEnv=json.loads((P/'SOURCE_ENVIRONMENT.json').read_text());before=json.loads((P/'HISTORICAL_CUSTODY_BEFORE.json').read_text());after=json.loads((P/'HISTORICAL_CUSTODY_AFTER.json').read_text())
local=f'''## Current run — IR-R03-02 B API-bound prerequisites, 2026-10-09 PDT / UTC

**CapacityBlocked; focused batch NotRun. Current-source supplementary CSharp API prerequisite Passed. Exit: Local Validation → Primary Implementation.** One B diagnostic ran without --execute and exited2; no executing invocation or Unity launch. All14 cells, three IL2CPP native build roles and four fresh Players are NotRun; core result/ledger/index/archive/seal Unavailable. [Factual result]({link}/preflight/LOCAL_PREFLIGHT_RESULT.json), [immutable B checkpoint]({link}/README.md). The prior A failure and historical NoCoverage remain unchanged.

| Actual owning repository | Branch | Exact B prerequisite commit |
| --- | --- | --- |
{table}

Each clean checkout independently passed top/branch/HEAD/status/canonical origin/worktree/submodule and fresh remote-tip checks. Demo safely fast-forwarded from A publicationd576 to exact434 transport; no reset/stash/clean/unrelated worktree changes. Compiled source `ba47b41674b83a6f694ac4f8ac1bc8f83a9da24b` is an ancestor; final delta is Docs-only. Product/native/package/fixture/runner/storage policy remain unchanged. [Initial and sync receipts]({link}/bootstrap/SYNC_AUTHORITY.json), [final exact authority]({link}/preflight/FINAL_PREFLIGHT_SOURCE_AUTHORITY.json), [source Git blobs/hashes]({link}/SOURCE_BINDINGS.json).

### Fresh B prerequisite states

| Validation | Factual result |
| --- | --- |
| Current-source API receipt/input/full-log authentication | Passed;22 tracked inputs,19 explicit CSharp inputs, actual job output receipts match published records |
| Fresh prescribed Python host suite | Passed,64 tests, zero skips/errors/failures |
| Fresh standalone C++ terminal policy compile/run | Passed,69 checks; not AssemblyShadow.cpp or Unity Player execution |
| Original S immutable DLL admission | Passed,15 original Git blobs; ReusedAudited inputs, no regeneration or runtime replay |
| Protected custody before and after | Passed,416,515 files, zero differences/symlinks; includes authenticated416,161-file prior map plus A checkpoint/live roots |
| Diagnostic storage | Exit2, admission Blocked, session NotAdmitted, batchStarted=false; allocation probes NotRun |
| Executing storage/Unity/Editor/IL2CPP build/Players | NotRun; zero --execute invocations and Unity launches |
| Distinct IR target generation / active-method side effects | NotRun; no fresh binary or post-poison field proof |
| Core result, ledger, index/archive/seal | Unavailable; no synthetic runtime cells or seal |

[Current-source receipt]({link}/preflight/CI_CURRENT_SOURCE.json) follows the prescribed procedure exactly. [Independent live-job/receipt/source verification]({link}/preflight/CI_EQUIVALENCE_VERIFICATION.json) records clocks, hashes and all22 input Git/blob/byte bindings, actual CI37903041633/job113729828150 atba47, package948, full compiler log SHA256 `a2805d2bf18a7004f5cb1b2197b8fba3f9f1edb4fac6f4ec2fc0d27dc820ae72`, current Player SHA256 `22c3e0be7cebc041706b1412c5fc317c806c49a0980be143d5517dc4cc59a7bd`,0 errors/13 warnings and current source inclusion. **CI used SDK10.0.401 targeting net8.0/CSharp9/UNITY_EDITOR with checked-in Unity API stubs.** It is not official Unity managed compilation, fresh Local managed compilation, Unity or runtime acceptance. Durable compiler log is exact lossless decoded bytes; connector job-log copy has a normalized final newline. CI binaries/ZIP/binlog were not downloaded by Local; Primary's artifact verification and11 synthetic receipt tests remain attributed, not new Local results. Previous native/API/fixture actual logs remain ReusedAudited with unchanged relevant sources; old API37874183375 remains historical NoCoverage.

[Host command receipts]({link}/preflight/LOCAL_HOST_PREFLIGHT.json) preserve exact argv/start/end/exits/source/header/binary/stream SHA256; host tests ran `{host['commands'][-3]['startUtc']}` through `{host['commands'][-1]['endUtc']}`. Unity2022.3.62f2 executable `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity` was verified present and never launched; planned StandaloneOSX arm64 target NotRun. Local SDK8.0.318 uses SDK-only `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`; Unity6000 never launched. Python3.14.6, macOS26.5.2 build25F84, Apple clang21.0.0 and active CommandLineTools/MacOSX SDK were recorded in [environment]({link}/preflight/SOURCE_ENVIRONMENT.json). Temp stays/private/tmp; no developer-directory, credential/protocol or SDK substitution. Shared ordinary-owner Git common metadata locations are not validation project roots.

[Original fixture receipt]({link}/preflight/ir-original-s-fixture-authority.json) SHA256 `53a8766bc18d5067396331af13ad10dd050e0853aee4c0eaa11c39751375494d` binds S publication `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`, inventory Git blob `0688bd2dad054bd59fcdd1564a050a398cfa14e7`, and all15 literal DLLs. Expected separate IR target SHA256 `8d0b28cbca4d889801883ad436c51c215b913f1645055590980f902f1e80fffd`, MVID `597eb18e-e0e7-6f8b-7e4a-6cdaabf9d1ff`,2048bytes/zero timestamp remains an expectation; generation belongs to an admitted batch and was NotRun here. Historical regeneration Failed/NotIdentical is preserved.

### Exact storage failure, custody and publication

Diagnostic start `{receipt['startUtc']}`, end `{receipt['endUtc']}`, actual wrapper exit2. [Exact command/streams]({link}/preflight/commands/storage-diagnostic/receipt.json) uses run_terminal_storage_checked.py, workspaceW, demo434, exact Unity, retained Q and the B output/diagnostic sidecar **without --execute**. First failure: `batch: available 67720581120 < required 68719476736 bytes`; observed63.070GiB versus64GiB, deficit998,895,616bytes (0.930GiB). Unchanged Q planning14,164,955,136bytes and max(64GiB,2*Q+20GiB); floor20GiB, no reservation. [Admission]({link}/storage-diagnostic/admission.json) SHA256 `757fef8cea467d0f61dd7f8845bc9754b79146c9212e15607c25f59e39a3dda5`; [capacity samples]({link}/storage-diagnostic/capacity.jsonl), [session]({link}/storage-diagnostic/session.json) SHA256 `4a302d1af6b6e5c6542e0ca86d32e9ddf055356f95246d45ca646ee04d12fe92`, and [dispatch]({link}/storage-diagnostic/dispatch.json) retain separate states and timestamps. Directory diskutil-info queries remain Unavailable; df/APFS-list observations captured. No cleanup, deletion, relocation, threshold/temp/quota change, retry or future-capacity claim.

All B candidate paths were initially absent, nonsymlinked and nonaliasing. Live preflight `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261009B-api-bound`; diagnostic `/Users/ah/GitHub/hybridclr/r03-local-validation/StorageCheck-R03IRLocal-20261009B-api-bound`; bootstrap `/Users/ah/GitHub/hybridclr/r03-local-validation/IR-R03-02-bootstrap-20261009B-api-bound`. Requested batch `/Users/ah/GitHub/hybridclr/r03-local-validation/R03IRLocal-20261009B-api-bound` and executing storage `/Users/ah/GitHub/hybridclr/r03-local-validation/Storage-R03IRLocal-20261009B-api-bound` remain absent. No prior Library/build/cache/app or ordinary primary/control project was used for execution.

[Before custody]({link}/preflight/HISTORICAL_CUSTODY_BEFORE.json) ran `{before['startUtc']}`→`{before['endUtc']}`; [after custody]({link}/preflight/HISTORICAL_CUSTODY_AFTER.json) ran `{after['startUtc']}`→`{after['endUtc']}`. Both verify416,515 files against the authenticated original A map reconstructed from immutable Git chunks and additive A copied/live bindings, without missing-file rebaselining. Postpublication external administrative files are current custody snapshots only. R stays staged/Failed; S90Passed and independent review FAIL remain distinct; Q/P/O/N/A and Failed unisolated warm certificates are unchanged.

[Copy bindings]({link}/COPY_BINDINGS.json), [ordered large-map transport]({link}/FILE_TRANSPORT.json), source snapshots and MANIFEST.sha256 preserve this additive checkpoint. Small publication capacity check covers only the prerequisite payload plus20GiB and does not pass runtime admission. Only Local-owned reports and the specified new checkpoint changed; no bounded product fix. Publication manifest/staged-byte/JSON/link/diff/scope verification and final pushed heads are recorded externally at `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261009B-api-bound/PUBLICATION_VALIDATION.json` and `PUBLICATION_RECEIPT.json`, separate from prerequisite source434.

R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; PureInterpreter expansion disabled. Independent full-stage review remains FAIL, separate re-review NotRun; genuine captured-generic/initializer cases and IR-R03-01 remain Primary work. No H2/X02/M08A; Local returns to Primary and stops after this one B result.

'''
ret=f'''## Current return — IR-R03-02 B API-bound prerequisites, 2026-10-09

**CapacityBlocked; focused batch NotRun.** [Local report](LOCAL_VALIDATION.md), [immutable B checkpoint]({link}/README.md), [factual result]({link}/preflight/LOCAL_PREFLIGHT_RESULT.json). Current-source API evidence Passed:22 compiler inputs matched CI37903041633/ba47,0 errors/13 warnings, using Unity API stubs. This closes B's supplementary compile-evidence prerequisite only; A's historical NoCoverage and capacity failure remain unchanged. Fresh64Python/69native checks,15 original S fixtures and416,515-file before/after custody Passed.

No new non-trivial product-source defect is established and no defect entry is manufactured. The sole remaining B admission blocker is environmental capacity. Diagnostic2026-10-09T08:39:49.098014+00:00→08:40:09.889885+00:00 exited2: available67,720,581,120bytes versus required68,719,476,736bytes, deficit998,895,616bytes (0.930GiB). [Original admission]({link}/storage-diagnostic/admission.json), [exact argv/logs]({link}/preflight/commands/storage-diagnostic/receipt.json), capacity/session/dispatch preserve the failure. BatchStarted=false, allocation probes NotRun; no --execute invocation, Unity, build or Player. All14/3/4 runtime scope NotRun; no core result/seal.

Required Primary/operator action: establish measured adequate headroom through separately authorized unrelated-data management without touching protected A/S/R/Q/P/O/N, changing thresholds/temp paths or retrying B. Then publish a distinct authorized diagnostic root and exact four-source tuple. Merely freeing the historical deficit is not a sustained-capacity guarantee; fresh full admission and probes remain mandatory. Original failed B diagnostic must stay immutable.

Validation still required: one newly authorized fully admitted focused batch14cells/three native builds/four fresh Players, real same-method pre-poison controls and readable counter2 after rejected reflection/delegate calls, unchanged AOT canary/first failure/state/generation/diagnostics, OFF control, source/build/request/PID bindings and seal. Stub compilation is not official Unity/Player execution. Genuine captured-generic/initializer coverage, IR-R03-01, independent full-stage re-review and broader approval remain separate unresolved work.

R remains staged; S90Passed/full-stage reviewFAIL remain distinct. A and all earlier evidence are preserved. All acceptance flags remain false; PureInterpreter expansion disabled. No Local implementation expansion or H2/X02/M08A. **Local Validation → Primary Implementation; stop after B.**

'''
for name,section,title in [('LOCAL_VALIDATION.md',local,'# Local Validation report'),('RETURN_TO_WEB.md',ret,'# Local Validation → Primary Implementation')]:
 f=D/'Docs/AssemblyShadow/Handoff'/name;old=f.read_text();prefix=title+'\n\n';assert old.startswith(prefix);body=old[len(prefix):].replace('## Current ','## Historical ',1);f.write_text(prefix+section+body)
for f in C.rglob('*.json'):json.loads(f.read_text())
manifest=''.join(sha(f)+'  '+str(f.relative_to(C))+'\n' for f in sorted(C.rglob('*')) if f.is_file());(C/'MANIFEST.sha256').write_text(manifest)
for line in manifest.splitlines():h,name=line.split('  ',1);assert sha(C/name)==h
save(P/'PUBLICATION_PREPARATION.json',{'recordedUtc':now(),'state':'Passed','checkpoint':str(C),'manifestSha256':sha(C/'MANIFEST.sha256'),'files':len(manifest.splitlines()),'copies':len(bindings),'runtimeExecution':False,'coreSeal':'Unavailable','sourceChanged':False})
print(json.dumps({'checkpoint':str(C),'files':len(manifest.splitlines()),'manifestSha256':sha(C/'MANIFEST.sha256'),'state':'Prepared'}))
