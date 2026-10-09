from pathlib import Path
import json,hashlib,subprocess,datetime,shutil,os,concurrent.futures
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';BASE=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');P=BASE/'Preflight-R03IRLocal-20261009A-terminal';BOOT=BASE/'IR-R03-02-bootstrap-20261009A';CHECK=BASE/'StorageCheck-R03IRLocal-20261009A-terminal';B=BASE/'R03IRLocal-20261009A-terminal';STORAGE=BASE/'Storage-R03IRLocal-20261009A-terminal';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-preflight-blocked';branch='codex/assembly-shadow-r01b-h1'
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
rows=json.loads((P/'FINAL_PREFLIGHT_SOURCE_AUTHORITY.json').read_text())['repositories']
ci=json.loads((P/'CI_SOURCE_EQUIVALENCE.json').read_text())
bindings=json.loads((C/'COPY_BINDINGS.json').read_text())
assert not (C/'SOURCE_BINDINGS.json').exists()
sourceBindings=[]
sourcePaths=[Path(x['path']) for x in json.loads((CHECK/'source-authority.json').read_text())['sourceFiles']]
sourcePaths.extend([D/'Docs/AssemblyShadow/README.md',D/'Docs/AssemblyShadow/Plan/CURRENT_STATUS.md',D/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_R03_02_FOCUSED_LOCAL_PROCEDURE_2026-10-09.md',D/'.github/workflows/r03-ir-player-api.yml',D/'Tools/AssemblyShadow/R03/PlayerApiCompile/PlayerApiCompile.csproj',W/'il2cpp_plus/tools/r03/terminal_execution_tests.cpp',W/'il2cpp_plus/libil2cpp/vm/AssemblyShadowTerminalExecution.h'])
for f in dict.fromkeys(sourcePaths):
 repo=next(W/n for n in pins if f.is_relative_to(W/n));name=repo.name;rel=f.relative_to(repo);raw=subprocess.check_output(['git','-C',str(repo),'show',pins[name]+':'+str(rel)]);assert raw==f.read_bytes();dest=C/'source-snapshots'/name/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);sourceBindings.append({'repository':str(repo),'commit':pins[name],'path':str(rel),'gitBlob':git(repo,'rev-parse',pins[name]+':'+str(rel)),'sha256':sha(f),'snapshot':str(dest.relative_to(C))})
save(C/'SOURCE_BINDINGS.json',sourceBindings)
(C/'.gitattributes').write_text('bootstrap/** -whitespace\npreflight/** -whitespace\nstorage-diagnostic/** -whitespace\nsource-snapshots/** -whitespace\n')
(C/'README.md').write_text('''# IR-R03-02 Local prerequisite checkpoint — 2026-10-09

**CapacityBlocked; focused batch NotRun.** No Unity, IL2CPP Player build or Player was launched; zero execution-wrapper invocations. This is an immutable prerequisite checkpoint, not a sealed runtime batch. The original diagnostic wrapper exited 2. The separate administrative driver exited 0 after recording that exit; it is not admission success.

Read `preflight/LOCAL_PREFLIGHT_RESULT.json`, `preflight/CI_SOURCE_EQUIVALENCE.json`, `storage-diagnostic/admission.json`, both custody receipts and `SOURCE_BINDINGS.json`. Local passed 64 Python tests, 69 native policy checks, exact four-owner source/remote checks, literal 15 original S fixture admission, and before/after custody for 416,161 files. Current CSharp Player API coverage is NoCoverage because the supplied successful job compiled an earlier body. The original actual logs and source delta remain preserved.

Storage observed 68,289,347,584 bytes available, required 68,719,476,736; deficit 430,129,152 bytes. Unchanged max(64GiB,2*Q+20GiB) policy; no cleanup, relocation or threshold change. All 14 planned cells, three builds and four Players remain NotRun; no core result, ledger, index, archive or seal exists. The distinct deterministic IR target was not generated locally. Fifteen staged S inputs are ReusedAudited immutable bytes, not replayed runtime results.

Live roots are retained exactly where COPY_BINDINGS records them. Large maps use FILE_TRANSPORT ordered byte chunks; concatenate parts outside this checkpoint and compare the listed original SHA256. MANIFEST.sha256 authenticates all checkpoint files except itself. Raw captures retain bytes and whitespace; decoded connector CI logs have a normalized trailing newline and are not remote ZIP byte-identity claims.

S/R/Q/P/O/N remain unchanged; R remains staged. Independent full-stage review remains FAIL. True captured-generic and post-poison initializer cases remain NotRun. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; PureInterpreter expansion disabled. No bounded product fix. Next owner: Primary Implementation. Fresh current-source CSharp API evidence and a separately authorized unused storage diagnostic root are required before any future focused execution.
''')
link='../History/M07R/R03/'+C.name
table='\n'.join('| `'+str(W/n)+'` | `'+branch+'` | `'+shaValue+'` |' for n,shaValue in pins.items())
local=f'''## Current run — IR-R03-02 focused prerequisites, 2026-10-09 PDT / UTC

**CapacityBlocked; focused batch NotRun. Source-bound CI preflight also Blocked: current Player CSharp API coverage NoCoverage. Exit: Local Validation → Primary Implementation.** No `--execute` invocation, Unity, IL2CPP Player build, Editor test or Player was launched. All 14 cells, three builds and four fresh Players are NotRun; no core ledger/result/index/archive/seal is manufactured. [Factual result]({link}/preflight/LOCAL_PREFLIGHT_RESULT.json), [immutable prerequisite checkpoint]({link}/README.md).

### Exact preflight source and environment

| Actual owning repository | Branch | Exact prerequisite commit |
| --- | --- | --- |
{table}

All four clean owning checkouts independently passed top/branch/HEAD/status/origin/worktree/submodule and fresh exact remote-tip checks. Safe fast-forwards preceded validation; source freeze `3eb309a1f82a9c7d4199a8499b95144a78cbdd24` is an ancestor with Docs-only delta. [Git receipts]({link}/bootstrap/SYNC_AUTHORITY.json), [final preflight authority]({link}/preflight/FINAL_PREFLIGHT_SOURCE_AUTHORITY.json), [source snapshots/hashes]({link}/SOURCE_BINDINGS.json). Unity 2022.3.62f2 executable is present at `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`; planned target StandaloneOSX arm64 is NotRun. SDK-only dotnet 8.0.318 uses `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`; Unity 6000 was never launched. Python 3.14.6, macOS 26.5.2 build25F84, Apple clang21.0.0, active `/Library/Developer/CommandLineTools` and its MacOSX SDK were recorded. [Environment]({link}/preflight/SOURCE_ENVIRONMENT.json). Shared ordinary-owner Git metadata paths are not validation project paths. No primary/control project, Library, build, cache or prior app was used for execution.

### Completed and unavailable validation

| Check | Factual result |
| --- | --- |
| Fresh prescribed Local Python tests | Passed, 64 tests, zero skips/errors/failures |
| Native terminal policy header compilation/execution | Passed, 69 checks; does not execute product AssemblyShadow.cpp or a Unity Player |
| Named CI actual job logs | Successful executing commits retained; relevant source comparisons qualified per file |
| Current CSharp Player API coverage | NoCoverage; required source-equivalence preflight Blocked |
| Literal original S input authority | Passed, 15 authenticated immutable Git DLLs; ReusedAudited input, no runtime-result reuse |
| Local deterministic IR target generation | NotRun; expected target hash is not fresh binary evidence |
| Historical custody before and after | Passed, 416,161 unique files, zero differences; R still staged |
| Diagnostic-only storage wrapper | Exit2; admission Blocked, session NotAdmitted; allocation probes NotRun |
| Executing storage / runtime batch / side-effect proof | NotRun; 0 of14 cells, 0 of3 builds, 0 of4 Players |
| Core result, ledger, index, archive and seal | Unavailable because no batch was started |

[Host argv/clocks/exit/source/binary/stream hashes]({link}/preflight/LOCAL_HOST_PREFLIGHT.json) bind the prescribed unittest invocation and `c++ -std=c++17 -Wall -Wextra -Werror -pedantic -pthread` policy test. Host execution spanned `2026-10-09T07:14:39.149135+00:00` through `2026-10-09T07:14:42.636099+00:00`. All required CI metadata and decoded logs are retained in bootstrap/ci; [CI source equivalence]({link}/preflight/CI_SOURCE_EQUIVALENCE.json) preserves actual executing SHAs/file hashes and limits. The source-freeze host run37895355423 and fresh Local tests cover current host contracts. API run37874183375 at `0e8c9ae457e77c595e119e9f2c089f759d6d1b16` passed its old source with 0 errors; the new pre/post-poison field assertions differ. Official native API compilation does not compile this Player body. No current CSharp acceptance is inferred.

Original S fixture authority [receipt]({link}/preflight/ir-original-s-fixture-authority.json) SHA256 `a6cc7b001cd6b9424fa968ebae3a7b370db28c63c957ddd5e9615564cf6fe7f8` binds original S publication `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b` and inventory Git blob `0688bd2dad054bd59fcdd1564a050a398cfa14e7`. External direct input-probe preparation first omitted a sibling Python module path and stopped before staging; [administrative observation]({link}/preflight/ADMINISTRATIVE_INPUT_PROBE.json) preserves that failure and Unavailable original timing. Only the external helper import path was corrected; production runner already has the correct path. No source fix or batch/phase retry. Subsequent production staging helper authenticated actual original bytes; new IR target generation remains NotRun.

### Storage, evidence custody and exit

The diagnostic-only wrapper command and actual exit2 are preserved in [receipt]({link}/preflight/commands/storage-diagnostic/receipt.json); start `2026-10-09T07:16:33.595206+00:00`, end `2026-10-09T07:16:55.669398+00:00`. Exact argv uses `run_terminal_storage_checked.py`, workspace `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`, demo-commit `fca2fdb035512fc739693641a5fa2126e4254258`, requested output `/Users/ah/GitHub/hybridclr/r03-local-validation/R03IRLocal-20261009A-terminal`, exact Unity path, retained Q, and diagnostic storage sidecar, **without --execute**.

First failure: `batch: available 68289347584 < required 68719476736 bytes`; observed63.599GiB versus64GiB, deficit430,129,152bytes (0.401GiB). Q planning14,164,955,136bytes; unchanged formula max(64GiB,2*Q+20GiB), operating floor20GiB. [Admission]({link}/storage-diagnostic/admission.json), [capacity samples]({link}/storage-diagnostic/capacity.jsonl), [session]({link}/storage-diagnostic/session.json), [dispatch]({link}/storage-diagnostic/dispatch.json) preserve separate initial and later sampled capacity, no reservation claim and batchStarted=false. Session SHA256 `a8ca3231f0eba3e31dbcb3525d5fc9e8c7b5a9b42c59c89ca78df9057444e70f`. This is one shared APFS pool; diskutil info on directory arguments was Unavailable while df/APFS-list observations succeeded. No reclamation, threshold change, source/pin/configuration change or cleanup occurred.

Live preflight `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261009A-terminal`; bootstrap `/Users/ah/GitHub/hybridclr/r03-local-validation/IR-R03-02-bootstrap-20261009A`; diagnostic `/Users/ah/GitHub/hybridclr/r03-local-validation/StorageCheck-R03IRLocal-20261009A-terminal`. Requested batch and distinct executing-storage `/Users/ah/GitHub/hybridclr/r03-local-validation/Storage-R03IRLocal-20261009A-terminal` remain absent. [Copy bindings]({link}/COPY_BINDINGS.json), [ordered large-map transport]({link}/FILE_TRANSPORT.json) and MANIFEST.sha256 authenticate this additive checkpoint. Publication capacity check covers only the small prerequisite payload plus20GiB, and cannot pass the blocked64GiB runtime policy.

[Before custody]({link}/preflight/HISTORICAL_CUSTODY_BEFORE.json) and [after custody]({link}/preflight/HISTORICAL_CUSTODY_AFTER.json) verify every416,161 bound file without missing-file rebaselining. S indexed evidence and published map/manifest are authenticated from original immutable Git objects; unindexed cache additions are current custody snapshots only. S remains90Passed with independent full-stage review FAIL; R remains staged/Failed, Q/P/O/N unchanged. Contaminated controls retain Failed unisolated warm certificates. No historical result is rewritten.

Stale Primary README/CURRENT_STATUS STOP summaries were retained; the latest specific WEB_TO_LOCAL and explicit user handoff authorize conditional focused execution only. Failed prerequisites prevented it. Only Local reports and the additive prerequisite checkpoint are owned changes; no bounded product fix. Final pushed heads/clean remote verification are recorded externally at `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261009A-terminal/PUBLICATION_RECEIPT.json` and in the final handoff, separate from the preflight source SHA.

R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; PureInterpreter expansion disabled. Independent full-stage verdict remains FAIL. True captured-generic and initializer post-poison cases remain NotRun, outside this subset; IR-R03-01 and separate re-review remain Primary work. Local returns to Primary and stops.

'''
api=ci['playerApiMismatch'];ret=f'''## Current return — IR-R03-02 focused prerequisites, 2026-10-09

**CapacityBlocked; focused batch NotRun.** [Local report](LOCAL_VALIDATION.md), [immutable checkpoint]({link}/README.md), [factual prerequisite result]({link}/preflight/LOCAL_PREFLIGHT_RESULT.json). Host64Python/69native checks, exact source/remote authority,15 original S inputs and416,161-file before/after custody Passed. No new runtime result or native defect is established; no Unity/build/Player or executing-wrapper invocation occurred.

### IR-LOCAL-API-01 — required Player API CI is not bound to the current side-effect assertions

**Symptom:** source-bound CI prerequisite Blocked; current Player CSharp API coverage NoCoverage. The required successful API run37874183375/job113638829514 compiled demo `0e8c9ae457e77c595e119e9f2c089f759d6d1b16`; current authorized source is `fca2fdb035512fc739693641a5fa2126e4254258`. It does not prove compilation of the current field-side-effect witness.

**Exact reproduction (read-only, already performed):** in `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`, compare `git diff 0e8c9ae457e77c595e119e9f2c089f759d6d1b16 fca2fdb035512fc739693641a5fa2126e4254258 -- Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs`; authenticate both Git objects and inspect the saved actual API job log's compilation inputs, Build succeeded/0 errors and checkout SHA. No workflow rerun is required to reproduce this source mismatch. [Source delta]({link}/preflight/PLAYER_API_SOURCE_DELTA.patch), [comparison and log hashes]({link}/preflight/CI_SOURCE_EQUIVALENCE.json), [actual log]({link}/bootstrap/ci/job-113638829514.log).

| Player source | Git blob | SHA256 |
| --- | --- | --- |
| Old compiled body | `{api['executingBlob']}` | `{api['executingSha256']}` |
| Current required body | `{api['currentBlob']}` | `{api['currentSha256']}` |

**Relevant differences:** new private primitive `stable` FieldInfo resolution/read, actual counter0→2 positive controls, readable post-poison field and unchanged2 assertion. **Most likely cause:** a green earlier supplementary workflow URL was carried into the source-bound prerequisite after Player bytes changed. **Affected scope:** compile-evidence admission for this exact focused Player and its active-method side-effect proof. Current source-freeze host CI and native API syntax tests do not compile this CSharp body.

**Recommended Primary direction:** publish successful existing `r03-ir-player-api.yml` compilation at the current executable source (or a demonstrably byte-identical descendant) using exact package `948c0e3b4f8891481301770115e8ba4945eea6de`, with actual logs, checkout SHA and relevant file bindings; update the source-bound prerequisite reference. Preserve the field controls and native guards. No architecture or Local source alteration is needed to close this evidence gap.

**Remaining uncertainty:** this mismatch does not establish a compile error or runtime defect. The discovered CI list was bounded and is not an exhaustive claim that no other matching run exists. **Validation after Primary action:** inspect current-source actual CSharp compile logs; repeat all fresh admission checks only under a new authorized unused diagnostic root; then exactly one focused14-cell/3-build/4-Player execution if all prerequisites pass. Verify actual readable field2 after poison, first-failure/recovery unchanged and seal. True captured-generic/initializer coverage and independent full-stage review remain separate unresolved work.

### Environmental prerequisite — capacity below unchanged admission

Diagnostic2026-10-09T07:16:33.595206+00:00→07:16:55.669398+00:00 returned2: available68,289,347,584bytes < required68,719,476,736bytes, deficit430,129,152bytes. [Exact original admission]({link}/storage-diagnostic/admission.json) and command/streams/session are retained; batchStarted=false and allocation probes NotRun. No product-source fix is requested for capacity. Primary/operator must establish measured safe headroom and publish a distinct unused diagnostic root, without deleting or relocating preserved S/R/Q/P/O/N, weakening thresholds or retrying the existing sidecar. Existing failed admission remains immutable even if capacity changes later.

R remains staged; S90Passed and full-stage review FAIL remain distinct. All acceptance flags remain false; PureInterpreter expansion disabled. Local stops and returns to Primary; no substantive Local changes or runtime closure claim.

'''
for name,section,title in [('LOCAL_VALIDATION.md',local,'# Local Validation report'),('RETURN_TO_WEB.md',ret,'# Local Validation → Primary Implementation')]:
 f=D/'Docs/AssemblyShadow/Handoff'/name;old=f.read_text();prefix=title+'\n\n';assert old.startswith(prefix);body=old[len(prefix):].replace('## Current ','## Historical ',1);f.write_text(prefix+section+body)
for f in C.rglob('*.json'):
 if '.part' not in f.name:json.loads(f.read_text())
manifest=''.join(sha(f)+'  '+str(f.relative_to(C))+'\n' for f in sorted(C.rglob('*')) if f.is_file());(C/'MANIFEST.sha256').write_text(manifest)
for line in manifest.splitlines():h,name=line.split('  ',1);assert sha(C/name)==h
save(P/'PUBLICATION_PREPARATION.json',{'recordedUtc':now(),'state':'Passed','checkpoint':str(C),'manifestSha256':sha(C/'MANIFEST.sha256'),'files':len(manifest.splitlines()),'copies':len(bindings),'runtimeExecution':False,'coreSeal':'Unavailable','sourceChanged':False})
print(json.dumps({'checkpoint':str(C),'files':len(manifest.splitlines()),'manifestSha256':sha(C/'MANIFEST.sha256'),'state':'Prepared'}))
