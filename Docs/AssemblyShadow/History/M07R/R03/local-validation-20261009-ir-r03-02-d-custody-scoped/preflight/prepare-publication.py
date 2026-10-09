from pathlib import Path
import json,hashlib,subprocess,datetime,shutil,os,concurrent.futures
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';BASE=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');P=BASE/'Preflight-R03IRLocal-20261009D-custody-scoped';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-d-custody-scoped';branch='codex/assembly-shadow-r01b-h1';pins=json.loads((P/'SOURCE_ENVIRONMENT.json').read_text())['pins'];source=pins['hybridclr_demo']
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(f):
 with Path(f).open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def save(f,v):
 with Path(f).open('x') as s:json.dump(v,s,indent=2);s.write('\n')
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],timeout=180).decode().strip()
def authority(n):
 r=W/n;start=now();commands=[]
 for a in [('rev-parse','--show-toplevel'),('branch','--show-current'),('rev-parse','HEAD'),('status','--short'),('remote','-v'),('worktree','list','--porcelain'),('submodule','status','--recursive'),('ls-remote','origin','refs/heads/'+branch)]:
  t=now();out=git(r,*a);commands.append({'argv':['git','-C',str(r),*a],'startUtc':t,'endUtc':now(),'exitCode':0,'stdout':out})
 assert commands[0]['stdout']==str(r) and commands[1]['stdout']==branch and commands[2]['stdout']==pins[n] and not commands[3]['stdout'];assert commands[-1]['stdout'].split()[0]==pins[n];assert git(r,'remote','get-url','origin')=='git@github.com:night-outlook/'+n+'.git'
 return {'path':str(r),'branch':branch,'commit':pins[n],'startUtc':start,'endUtc':now(),'state':'Passed','commands':commands}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(authority,pins))
save(P/'FINAL_PREFLIGHT_SOURCE_AUTHORITY.json',{'state':'Passed','repositories':rows})
absent=[BASE/n for n in ['R03IRLocal-20261009D-custody-scoped','StorageCheck-R03IRLocal-20261009D-custody-scoped','Storage-R03IRLocal-20261009D-custody-scoped']]
assert all(not os.path.lexists(f) for f in absent) and not C.exists()
before=json.loads((P/'scoped-custody-before.json').read_text());after=json.loads((P/'scoped-custody-after.json').read_text());diag=json.loads((P/'VERIFIER_BINDING_DIAGNOSIS.json').read_text());bad=[r for r in diag['cReceiptBindings'] if not r['matchesVerifierLiteral']];assert len(bad)==1 and bad[0]['literalLength']==53 and bad[0]['matchesOriginalGit'];assert before['result']==after['result']=='Blocked' and before['error']==after['error'];assert json.loads((P/'CI_EQUIVALENCE_VERIFICATION.json').read_text())['state']=='Passed'
flags={'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'ReadyForHumanReviewGate':False,'fullLegacyRegressionAcceptance':False,'pureInterpreterExpansionEnabled':False}
roles=['candidate-release','candidate-debug','candidate-off'];ids=['entry-authority','real-dll-fixtures','ir-generator-build','ir-side-effect-fixture']+[x+'-'+r for r in roles for x in ['prepare','build']]+['IR-R03-02-release-baseline','IR-R03-02-debug-baseline','IR-R03-02-release-type','IR-R03-02-off'];assert len(ids)==14
save(P/'PLANNED_RUNTIME_STATES.json',{'kind':'R03IRPrerequisiteNotRunScope','sourceCommit':source,'sourcePath':str(D/'Tools/AssemblyShadow/R03IR/run_terminal_local.py'),'sourceSha256':sha(D/'Tools/AssemblyShadow/R03IR/run_terminal_local.py'),'schedulerConstructed':False,'notExecutionLedger':True,'reason':'Published scoped verifier rejected immutable native receipt binding before full scan','cells':[{'id':n,'state':'NotRun'} for n in ids],'builds':[{'role':n,'state':'NotRun'} for n in roles],'players':[{'id':n,'state':'NotRun'} for n in ids[-4:]],'coreLedger':'Unavailable'})
result={'kind':'R03IRLocalPrerequisiteResult','recordedUtc':now(),'result':'ScopedCustodyPreflightBlocked','exitState':'Local Validation -> Primary Implementation','batch':'NotRun','sources':rows,'plannedCells':14,'executedCells':0,'builds':{'planned':3,'executed':0,'state':'NotRun'},'players':{'planned':4,'executed':0,'state':'NotRun'},'unityLaunches':0,'editMode':'NotRun','il2cppNativeBuild':'NotRun','irTargetGeneration':'NotRun','activeMethodSideEffects':'NotRun','sourceAuthority':'Passed','sourceBoundCIPreflight':'Passed','currentCompilerInputs':22,'hostPythonTests':{'state':'Passed','count':64},'nativePolicyChecks':{'state':'Passed','count':69,'runtimeAcceptance':False},'scopedVerifierSyntheticTests':{'state':'Passed','count':10},'originalSInputs':{'state':'Passed','fixtures':15,'classification':'ReusedAudited original Git inputs'},'sealedSByteIndexAuthentication':'Passed','immutableCCheckpointGitAuthentication':'Passed','retainedR':'Passed read-only, original restore Failed/still staged','scopedCustody':{'before':'Blocked','after':'Blocked','fullLiveMapScan':'NotRun','freshPresentVerified':'Unavailable','freshHistoricalStillMissing':'Unavailable','historicalOriginalExpectedFiles':416844,'historicalOriginalPresentVerified':339367,'historicalOriginalMissing':77477,'originalStrictCustody':'Blocked','strictFullHistoricalCustodyAccepted':False,'sourceBuildProcessProvenanceRestored':False,'missingInventoryRebased':False,'blockingReason':before['error']},'storageDiagnostic':'NotRun','storageAdmission':'NotRun','executingStorage':'NotRun','diagnosticWrapperInvocations':0,'executionWrapperInvocations':0,'capacity':'Unavailable; no fresh D admission executed','coreResult':'Unavailable','ledger':'Unavailable','coreIndexArchiveSeal':'Unavailable','evidenceRoot':str(P),'absentRoots':[str(f) for f in absent],'boundedFixes':[],'historicalReclassification':False,'independentFullStageReview':'FAIL',**flags}
save(P/'LOCAL_PREFLIGHT_RESULT.json',result)
footprint=sum(f.stat().st_size for f in P.rglob('*') if f.is_file());v=os.statvfs(D);available=v.f_bavail*v.f_frsize;required=2*footprint+20*1024**3;assert available>=required
save(P/'PUBLICATION_CAPACITY.json',{'recordedUtc':now(),'state':'Passed','purpose':'Small documentation/evidence publication only; not runtime admission','payloadBytesBeforeReceipt':footprint,'availableBytes':available,'requiredBytes':required,'formula':'2*prerequisitePayload+20GiB','capacityReserved':False,'runtimeBlockedByScopedVerifier':True})
for n in ['LOCAL_VALIDATION.md','RETURN_TO_WEB.md']:
 f=D/'Docs/AssemblyShadow/Handoff'/n;assert f.read_bytes()==subprocess.check_output(['git','-C',str(D),'show',source+':'+str(f.relative_to(D))]);save(P/(n+'.PRESERVATION.json'),{'path':str(f),'previousSha256':sha(f),'previousCommit':source,'strategy':'Prepend D; relabel only previous first Current heading Historical; preserve every other prior byte'})
C.mkdir();bindings=[]
for f in sorted(P.rglob('*')):
 assert not f.is_symlink()
 if f.is_file():
  rel=Path('preflight')/f.relative_to(P);dest=C/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest);h=sha(f);assert sha(dest)==h;assert f.stat().st_size<50*1024**2;bindings.append({'originalPath':str(f),'checkpointPath':str(rel),'sha256':h,'bytes':f.stat().st_size,'transport':'exactCopy'})
save(C/'COPY_BINDINGS.json',bindings);save(C/'FILE_TRANSPORT.json',{'format':'Exact files; immutable prior C map remains in original authenticated Git checkpoint, not rebaselined','files':[]})
sourcePaths=[]
ci=json.loads((P/'CI_EQUIVALENCE_VERIFICATION.json').read_text())
sourcePaths.extend(W/x['repository'].split('/')[1]/x['path'] for x in ci['inputs'])
DOC=D/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09';sourcePaths.extend(f for f in DOC.rglob('*') if f.is_file())
for rel in ['Docs/AssemblyShadow/README.md','Docs/AssemblyShadow/Plan/CURRENT_STATUS.md','Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md','Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_R03_02_FOCUSED_LOCAL_PROCEDURE_2026-10-09.md','Tools/AssemblyShadow/R03IR/run_terminal_local.py','Tools/AssemblyShadow/R03IR/run_terminal_storage_checked.py','Tools/AssemblyShadow/R03IR/ir_original_fixtures.py','Tools/AssemblyShadow/R03/source-pins.json']:
 sourcePaths.append(D/rel)
E=D/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_LOCAL_API_01_2026-10-09';sourcePaths.extend(E/f for f in ['README.md','EVIDENCE.json','compile-inputs.json','compile-result.json','build.log.gz.b64','PRIMARY_SYNTHETIC_CHECKS.json']);sourcePaths.extend([W/'il2cpp_plus/tools/r03/terminal_execution_tests.cpp',W/'il2cpp_plus/libil2cpp/vm/AssemblyShadowTerminalExecution.h'])
sourceBindings=[]
for f in dict.fromkeys(sourcePaths):
 repo=next(W/n for n in pins if f.is_relative_to(W/n));rel=f.relative_to(repo);raw=subprocess.check_output(['git','-C',str(repo),'show',pins[repo.name]+':'+str(rel)]);assert raw==f.read_bytes();dest=C/'source-snapshots'/repo.name/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);sourceBindings.append({'repository':str(repo),'commit':pins[repo.name],'path':str(rel),'gitBlob':git(repo,'rev-parse',pins[repo.name]+':'+str(rel)),'sha256':sha(f),'snapshot':str(dest.relative_to(C))})
save(C/'SOURCE_BINDINGS.json',sourceBindings)
(C/'.gitattributes').write_text('preflight/** -whitespace\nsource-snapshots/** -whitespace\n')
(C/'README.md').write_text('''# IR-R03-02 D scoped-custody prerequisite checkpoint — 2026-10-09

**ScopedCustodyPreflightBlocked; runtime batch NotRun.** Source/API and fresh 64 Python / 69 native / ten verifier tests Passed; original 15 S fixture DLLs authenticated; C checkpoint matches original Git and S five artifacts/15,712 indexed files/15,713 archive members verify. Both actual published verifier invocations exit 2 on its 53-character native-limit SHA literal. The original C file remains unchanged with a valid 64-character SHA. No full live-map scan completed. Historical 339,367 surviving / 77,477 Missing are frozen C facts, not a fresh D census.

Read preflight/LOCAL_PREFLIGHT_RESULT.json, VERIFIER_BINDING_DIAGNOSIS.json and both scoped-custody receipts/command streams. All 14 planned cells / three builds / four Players NotRun; PLANNED_RUNTIME_STATES is a prerequisite scope declaration, not an execution ledger. Zero diagnostic/execute wrapper invocations and zero Unity launches. All three batch/storage roots remain absent; no fresh storage admission or runtime seal. No source change or retry.

COPY_BINDINGS and MANIFEST.sha256 authenticate exact additive evidence; original C maps/failure receipts remain in the prior immutable Git checkpoint, with no duplicate/rebaseline required. SOURCE_BINDINGS snapshots the actual Primary verifier, disposition and runtime/compiler pins. Both Local reports preserve earlier factual returns. Final validation/publication receipts stay external in the D preflight root to avoid self-referential publication hashes.

Strict original custody stays Blocked; ScopedHistoricalLossStable was not achieved; S live-native provenance remains incomplete. C/S/R/Q/P/O/N/A/B histories are not reclassified. All acceptance flags remain false, full-stage independent review FAIL/re-review NotRun, PureInterpreter expansion disabled. Primary must correct/authenticate its pinned input and publish a fresh unused attempt; Local stops after D.
''')
link='../History/M07R/R03/'+C.name
table='\n'.join('| `'+str(W/n)+'` | `'+branch+'` | `'+h+'` |' for n,h in pins.items())
commandBefore=json.loads((P/'commands/scoped-custody-before/receipt.json').read_text());commandAfter=json.loads((P/'commands/scoped-custody-after/receipt.json').read_text());host=json.loads((P/'LOCAL_HOST_PREFLIGHT.json').read_text())
local=f'''## Current run — IR-R03-02 D scoped-custody prerequisites, 2026-10-09 PDT / UTC

**ScopedCustodyPreflightBlocked; runtime batch NotRun. Exit: Local Validation → Primary Implementation.** The exact-loss disposition authorized one fresh independent D attempt with strict historical custody preserved as Blocked. The published verifier exited 2 in both before/after phases while authenticating a C receipt, before reconstructing/scanning the full live map. No diagnostic storage wrapper, --execute, Unity, build or Player ran. [Result]({link}/preflight/LOCAL_PREFLIGHT_RESULT.json), [checkpoint]({link}/README.md), [individual planned NotRun states]({link}/preflight/PLANNED_RUNTIME_STATES.json).

| Actual owning repository | Branch | Exact D prerequisite source commit |
| --- | --- | --- |
{table}

The clean demo safely fast-forwarded from C publication `36b9828d62bb81d98e81d055871a9540fe116276` to authorized `7313c768a2658ae77357e3fb1a83e9542585c99c`. Each repository independently passed path/top/branch/HEAD/status/canonical SSH origin/worktree/submodules/fresh remote tip. No reset/stash/clean, credential/protocol change or unrelated checkout use. Source manifest binds the exact three non-demo pins. Demo remains Docs-only since compiled API anchor `ba47b41674b83a6f694ac4f8ac1bc8f83a9da24b`; runtime/native/package/fixtures/runner/storage guards unchanged. [Sync authority]({link}/preflight/SYNC_AUTHORITY.json), [final authority]({link}/preflight/FINAL_PREFLIGHT_SOURCE_AUTHORITY.json), [Git/source snapshots]({link}/SOURCE_BINDINGS.json). Final pushed documentation heads are separate from this execution-source tuple, recorded in the external publication receipt.

### Fresh checks and coverage

| Validation | Actual D result |
| --- | --- |
| Source/remote/environment | Passed, all four exact clean owners |
| Current managed API CI/source/receipt equivalence | Passed, all 22 inputs / 19 explicit CSharp inputs; Unity API stubs only |
| Fresh prescribed Python tests | Passed, 64 tests, no skips/errors/failures |
| Standalone native policy compilation/run | Passed, 69 checks; not product AssemblyShadow.cpp or Unity runtime |
| Fresh scoped-custody synthetic tests | Passed, ten; they did not detect the real C constant mismatch |
| Original S fixture authentication | Passed, 15 original immutable Git DLLs; ReusedAudited inputs, no regeneration |
| C immutable checkpoint / S byte-index authentication | Passed, all 195 C manifest files match original Git; S five top artifacts and all 15,712 indexed files verify |
| Retained R read-only audit | Passed, six files; remains staged, original restore Failed |
| Scoped before / after verifier | Blocked / Blocked, exit 2 / 2; immutable receipt hash mismatch |
| Fresh 416,844-file live census | NotRun; verifier failed loading original inputs; fresh surviving/missing counts Unavailable |
| D diagnostic / executing storage admission | NotRun, zero wrapper invocations; capacity Unavailable for D |
| All 14 scheduler cells / three native builds / four Players | NotRun; no scheduler constructed and zero Unity launches |
| IR target generation / active-method side effects | NotRun |
| Core result / ledger / index / archive / seal | Unavailable; no synthetic runtime result or seal |

[Host commands]({link}/preflight/LOCAL_HOST_PREFLIGHT.json) preserve exact argv/cwd/start/end/exits, binary/source/header and stdout/stderr hashes; ten/64/69 checks all Passed. [Environment]({link}/preflight/SOURCE_ENVIRONMENT.json): macOS 26.5.2 build 25F84, Python 3.14.6, Apple clang 21.0.0 and CommandLineTools/MacOSX SDK. Exact Unity `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity` verified present, never launched; StandaloneOSX arm64 planned, NotRun. Local SDK 8.0.318 uses SDK-only `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`; Unity 6000 never launched. Temp `/private/tmp` unchanged.

[Current source/API receipt]({link}/preflight/CI_CURRENT_SOURCE.json) and [fresh remote job/source/receipt comparison]({link}/preflight/CI_EQUIVALENCE_VERIFICATION.json) authenticate CI 37903041633/job 113729828150 at ba47, 0 errors/13 warnings, exact full compiler log SHA256 `a2805d2bf18a7004f5cb1b2197b8fba3f9f1edb4fac6f4ec2fc0d27dc820ae72` and current Player SHA256 `22c3e0be7cebc041706b1412c5fc317c806c49a0980be143d5517dc4cc59a7bd`. **CI used SDK 10.0.401 targeting net8.0/CSharp9/UNITY_EDITOR with checked-in Unity API stubs, not official Unity managed assemblies or Player execution.** Original compiler log decoded losslessly; decoded connector job text has a normalized final newline. Binary/ZIP/binlog not downloaded by Local; Primary artifact verification and 11 receipt tests remain attributed. Earlier native/API/fixture logs reused-audited with unchanged bytes; old API 37874183375 remains historical NoCoverage.

[Fixture receipt]({link}/preflight/ir-original-s-fixture-authority.json), SHA256 `b0f2949c22fe91963bcf6b3900aaeee8d4b8636090c003bcfd2b3930d3727f08`, binds 15 original DLLs to S publication `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`, inventory blob `0688bd2dad054bd59fcdd1564a050a398cfa14e7`. Fresh staging ran 2026-10-09T13:48:29.442098+00:00→13:48:29.926667+00:00. Separate IR target expected SHA256 `8d0b28cbca4d889801883ad436c51c215b913f1645055590980f902f1e80fffd`, MVID `597eb18e-e0e7-6f8b-7e4a-6cdaabf9d1ff`, 2048 bytes/zero PE timestamp remains expected-only; generation NotRun.

### Actual verifier failure and historical states

Before [command receipt]({link}/preflight/commands/scoped-custody-before/receipt.json) ran `{commandBefore['startUtc']}`→`{commandBefore['endUtc']}`, exit 2, raw [before result]({link}/preflight/scoped-custody-before.json) SHA256 `760c7670ceced1dbc66f10136e997854c2c30ade2c89e18302523973dc185b61`. Separate required after [command receipt]({link}/preflight/commands/scoped-custody-after/receipt.json) ran `{commandAfter['startUtc']}`→`{commandAfter['endUtc']}`, exit 2, [after result]({link}/preflight/scoped-custody-after.json) SHA256 `a5d988da9a35f1e19c30e563bfc3c677a6945b76be9cc139cf6894834a0ad8f3`. Both report `Immutable C file SHA mismatch` for the exact original C `preflight/NATIVE_LIVE_CUSTODY_LIMIT.json`. The after phase is separate required post-prerequisite evidence, not a retry of before; no execution occurred.

[Binding diagnosis]({link}/preflight/VERIFIER_BINDING_DIAGNOSIS.json) establishes that the published verifier has literal `5cf6365c3e84e5390868984b52b40534de0fa53b92499d0359f9d` (53 characters) while the unchanged original receipt SHA256 is `5cf6365c3e84e5390868984b52a2f11cc8f52b40534de0fa53b92499d0359f9d` (64). Original Git blob `cca29fae8e0bbe7431d44b1f3f0eff96727c5756` at C publication 36b9828d matches current file and C manifest. All other four C_BLOBS values and four original map parts match; the full C map remains SHA256 `133cba8a9b54b74a9909c6da6948838f8f604afea47bc61bdee88f45c22df0e8`. Published verifier source SHA256 `f70fa56b4c730684a91cd6b329bcc63573c2b2027814d65e09ae2e87ac6504c9`. No verifier source or expected binding was edited locally.

**D did not establish ScopedHistoricalLossStable or fresh 339,367/77,477 counts.** Those counts and the 12 missing groups/four absent installed-native roots remain original C facts, with strict historical CustodyBlocked; no restoration or rebaselining. The failure is in Primary's new prerequisite input binding, not evidence of changed historical bytes or a product runtime defect. Stop-on-failed-prerequisite instructions prevent Local correcting the expected hash and rerunning this consumed attempt.

[Read-only C/S audit]({link}/preflight/SEALED_S_AND_C_AUTHENTICATION.json) ran 2026-10-09T13:49:15.115879+00:00→13:49:21.325527+00:00: every C checkpoint manifest file is original-Git-identical; S five top artifact hashes and 15,712 indexed files match; original archive 587,907,380 bytes / 15,713 members, SHA256 `23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6`, all indexed paths covered. These are byte/index facts, not original live SDK provenance recovery or full custody PASS. [Retained R]({link}/preflight/RETAINED_R_READ_ONLY.json) remains staged/Failed original restore. No historical native installation, Library, HybridCLRData or app was consumed or modified; no Q/P/O/N/A/B/C result was reclassified. A new full protected census is Unavailable because the authorized helper stopped before it.

### Roots, preservation and publication

Preflight `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261009D-custody-scoped` was created only after exact-source/remote/absence/nonaliasing checks. All three remaining roots `/Users/ah/GitHub/hybridclr/r03-local-validation/R03IRLocal-20261009D-custody-scoped`, `/Users/ah/GitHub/hybridclr/r03-local-validation/StorageCheck-R03IRLocal-20261009D-custody-scoped`, `/Users/ah/GitHub/hybridclr/r03-local-validation/Storage-R03IRLocal-20261009D-custody-scoped` remain absent. Retained Q stays `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261006Q-lp-repair`; its new admission/full-size proof was NotRun. C capacity is historical and is not reused. No disk cleanup, threshold/quota/temp/snapshot change, source/runtime fix, failed-phase retry or scope reduction.

[Exact copy bindings]({link}/COPY_BINDINGS.json), [source snapshots]({link}/SOURCE_BINDINGS.json) and MANIFEST.sha256 authenticate the additive D checkpoint. Earlier report bodies remain intact except prior first Current→Historical heading. Only Local-owned reports and new checkpoint changed. Small publication-capacity check permits documentation payload only, not runtime admission. Manifest/JSON/links/hash/staged bytes/scope/diff checks and final pushed heads are in external `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261009D-custody-scoped/PUBLICATION_VALIDATION.json` and `PUBLICATION_RECEIPT.json`, avoiding self-referential checkpoint hashes.

All acceptance flags false: R03Accepted, H2Passed, qualificationApproved, ReadyForHumanReviewGate, fullLegacyRegressionAcceptance; PureInterpreter expansion disabled. Independent full-stage review FAIL, re-review NotRun. Genuine captured-generic/initializer witnesses, IR-R03-01 and historical native-root risk remain unclosed. No H2/X02/M08A. Local returns to Primary and stops after D.

'''
ret=f'''## Current return — IR-R03-02 D scoped-custody prerequisite, 2026-10-09

**ScopedCustodyPreflightBlocked; runtime batch NotRun.** [Local report](LOCAL_VALIDATION.md), [D checkpoint]({link}/README.md), [factual result]({link}/preflight/LOCAL_PREFLIGHT_RESULT.json). Fresh source/API, 64 Python / 69 native / ten synthetic custody tests, 15 immutable S fixtures and S sealed byte/index authentication Passed. Both actual scoped verifier invocations exited 2 before any live map scan. No storage wrapper, Unity or runtime execution; all 14 cells / three builds / four Players NotRun, seal Unavailable.

### IR-LOCAL-CUSTODY-02 — published native-limit receipt hash truncated

**Symptom:** before/after fail with `Immutable C file SHA mismatch` for `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-c-custody-blocked/preflight/NATIVE_LIVE_CUSTODY_LIMIT.json`. D cannot satisfy its scoped preflight despite immutable C evidence matching Git. This is a Primary-owned prerequisite correction; the one-attempt stop rule disallows a Local expectation edit/retry.

**Exact reproduction:** use clean demo `7313c768a2658ae77357e3fb1a83e9542585c99c`; invoke Python 3.14 `-B` with `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09/verify_scoped_custody.py --checkpoint <absolute original C checkpoint> --phase before --receipt <fresh external receipt>`. Actual D command is preserved in [before command]({link}/preflight/commands/scoped-custody-before/receipt.json), 2026-10-09T13:50:20.783340+00:00→13:50:21.041053+00:00, exit 2; [after command]({link}/preflight/commands/scoped-custody-after/receipt.json), 13:50:59.101263+00:00→13:50:59.301628+00:00, exit 2. Do not rerun D.

**Evidence and root cause:** [binding diagnosis]({link}/preflight/VERIFIER_BINDING_DIAGNOSIS.json) independently authenticates all five original C receipts against publication `36b9828d62bb81d98e81d055871a9540fe116276`. The source `C_BLOBS['NATIVE_LIVE_CUSTODY_LIMIT.json']` literal is `5cf6365c3e84e5390868984b52b40534de0fa53b92499d0359f9d` (53 characters). Original Git/current receipt hash is `5cf6365c3e84e5390868984b52a2f11cc8f52b40534de0fa53b92499d0359f9d` (64), blob `cca29fae8e0bbe7431d44b1f3f0eff96727c5756`. Both [before]({link}/preflight/scoped-custody-before.json) and [after]({link}/preflight/scoped-custody-after.json) stopped in load_frozen_c/authenticated_json. Verifier source SHA256 `f70fa56b4c730684a91cd6b329bcc63573c2b2027814d65e09ae2e87ac6504c9`. All other receipt constants and four map-part size/hash bindings match. The ten synthetic tests passed but do not authenticate these hardcoded real receipt constants.

**Affected scope:** new Docs-owned custody verifier cannot load the immutable native-limit receipt; therefore full 416,844-file scan, fresh surviving/missing counts, ScopedHistoricalLossStable and every dependent storage/runtime stage are NotRun/Unavailable. No product runtime defect is established, runtime pins remain unchanged. Full C checkpoint and S indexed/sealed authentication Passed independently; strict historical custody remains Blocked and four native roots remain historically Missing, not recovered or reclassified.

**Recommended Primary correction:** derive the exact native-limit SHA from the authenticated original C Git object and correct the frozen literal; validate all pinned SHA literals as 64 hexadecimal characters and add a real immutable-receipt/source-binding regression so synthetic stable-loss tests cannot miss truncation. Keep the frozen map, original loss identities, guards and disposition unchanged. Publish correction and fresh unused attempt roots; never silently bypass receipt authentication or retry D.

**Remaining uncertainty/validation:** no fresh full census completed, so stable missing set, unexpected restoration/new loss and all 339,367 survivor bytes remain unverified for D. A successor must freshly authenticate the corrected original receipts/map, run all host/API/fixture/sealed checks and full before/after 416,844-entry audits, independently pass both diagnostic and execution storage gates, then run the one 14-cell/three-build/four-Player batch with real pre/post-poison side-effect proof and a source-bound seal. Missing historical S live native provenance remains unaccepted for full-stage review. Captured-generic/initializer and IR-R03-01 work remain separate.

All acceptance flags remain false, PureInterpreter expansion disabled; independent full-stage FAIL/re-review NotRun unchanged. **Local Validation → Primary Implementation; stop after D.**

'''
for n,section,title in [('LOCAL_VALIDATION.md',local,'# Local Validation report'),('RETURN_TO_WEB.md',ret,'# Local Validation → Primary Implementation')]:
 f=D/'Docs/AssemblyShadow/Handoff'/n;old=f.read_text();prefix=title+'\n\n';assert old.startswith(prefix);body=old[len(prefix):].replace('## Current ','## Historical ',1);f.write_text(prefix+section+body)
for f in C.rglob('*.json'):json.loads(f.read_text())
manifest=''.join(sha(f)+'  '+str(f.relative_to(C))+'\n' for f in sorted(C.rglob('*')) if f.is_file());(C/'MANIFEST.sha256').write_text(manifest)
save(P/'PUBLICATION_PREPARATION.json',{'state':'Passed','recordedUtc':now(),'checkpoint':str(C),'manifestSha256':sha(C/'MANIFEST.sha256'),'files':len(manifest.splitlines()),'copies':len(bindings),'runtimeExecution':False,'coreSeal':'Unavailable','sourceChanged':False})
print(json.dumps({'state':'Prepared','checkpoint':str(C),'files':len(manifest.splitlines()),'manifestSha256':sha(C/'MANIFEST.sha256')}))
