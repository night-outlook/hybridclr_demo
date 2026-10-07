from pathlib import Path
import datetime,hashlib,json,subprocess,shutil,os,plistlib
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';BASE=Path('/Users/ah/GitHub/hybridclr/r03-local-validation')
P=BASE/'Preflight-R03LocalBatch-20261007R-lq-storage';CHECK=BASE/'StorageCheck-R03LocalBatch-20261007R-lq-storage';B=BASE/'R03LocalBatch-20261007R-lq-storage';STORAGE=BASE/'Storage-R03LocalBatch-20261007R-lq-storage'
C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-r-capacity-blocked';rel=str(C.relative_to(D));SOURCE='cbf80474ebdee125e1d162d9c32a1734ee541720';BRANCH='codex/assembly-shadow-r01b-h1'
PINS={'hybridclr_demo':SOURCE,'hybridclr':'4b2774b066cfc6afd77a8c8aded6bda7ea574f55','hybridclr_unity':'948c0e3b4f8891481301770115e8ba4945eea6de','il2cpp_plus':'1cf87f8209790f9fb2ebec97487dc1990ccd56c5'}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,a):
 with p.open('x') as f:json.dump(a,f,indent=2);f.write('\n')
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args]).decode().strip()
start=utc();assert not C.exists() and not B.exists() and not STORAGE.exists()
pre=[]
for name,pin in PINS.items():
 r=W/name;assert git(r,'rev-parse','--show-toplevel')==str(r);assert git(r,'rev-parse','HEAD')==pin;assert git(r,'branch','--show-current')==BRANCH;assert not git(r,'status','--short');assert git(r,'remote','get-url','origin')=='git@github.com:night-outlook/'+name+'.git'
 pre.append({'path':str(r),'branch':BRANCH,'head':pin,'statusShort':'','origin':git(r,'remote','get-url','origin'),'worktrees':git(r,'worktree','list','--porcelain'),'submodules':git(r,'submodule','status','--recursive')})
a=json.loads((CHECK/'admission.json').read_text());s=json.loads((CHECK/'session.json').read_text());dispatch=json.loads((CHECK/'dispatch.json').read_text());audit=json.loads((P/'PRESERVED_EVIDENCE_AUDIT.json').read_text());env=json.loads((P/'ENVIRONMENT.json').read_text());rc=json.loads((P/'RETAINED_CONTRACT_RESULTS.json').read_text())
assert a['state']=='Blocked' and s['state']=='Failed' and not dispatch['batchStarted'] and dispatch['coreResultPath'] is None and audit['state']=='Passed'
for name,digest in audit['sidecarHashes'].items():assert sha(CHECK/name)==digest
sourcefiles=[('.github/workflows/r03-storage.yml'),*[str(p.relative_to(D)) for p in sorted((D/'Tools/AssemblyShadow/R03Storage').glob('*.py'))],'Tools/AssemblyShadow/R03Completion/run_completion.py','Tools/AssemblyShadow/R03Completion/resource_pipeline.py','Tools/AssemblyShadow/R03/run_local.py','Tools/AssemblyShadow/R03/source-pins.json','Tools/AssemblyShadow/R03Completion/source-pins.json','Packages/manifest.json','Packages/packages-lock.json','ProjectSettings/ProjectVersion.txt']
sourcebytes=sum((D/n).stat().st_size for n in sourcefiles);prebytes=sum(p.stat().st_size for p in P.rglob('*') if p.is_file());checkbytes=sum(p.stat().st_size for p in CHECK.rglob('*') if p.is_file());planned=prebytes+checkbytes+sourcebytes+1024*1024 # conservative small report/manifest allowance
common=Path(git(D,'rev-parse','--path-format=absolute','--git-common-dir'));locations={}
for name,path in {'publicationCheckout':D,'gitCommon':common,'sidecar':CHECK,'preflight':P}.items():
 st=os.statvfs(path);locations[name]={'path':str(path),'device':path.stat().st_dev,'availableBytes':st.f_bavail*st.f_frsize}
# Scope is the expressly permitted small factual blocker publication, not batch admission/publication.
assert min(v['availableBytes'] for v in locations.values())>4*planned+64*1024*1024
save(P/'SMALL_BLOCKER_PUBLICATION_CHECK.json',{'kind':'SmallFactualBlockerPublicationObservation','startUtc':start,'endUtc':utc(),'preflightBytes':prebytes,'sidecarBytes':checkbytes,'sourceSnapshotBytes':sourcebytes,'plannedCopyUpperBoundBytes':planned,'locations':locations,'fullBatchPublicationCheck':'NotRun: no batch root was constructed; no full batch copy or archive','batchAdmissionUnchanged':'Blocked','runtimeAuthorityGranted':False,'scope':'Only Local-owned small factual blocker reports/checkpoint; no historical evidence moved or packed'})
save(P/'PRE_EDIT_STATUS.json',{'startUtc':start,'endUtc':utc(),'existingModifications':[],'repositories':pre,'ownedPaths':[rel,'Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md','Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md'],'productFilesOwned':[]})
C.mkdir();shutil.copytree(P,C/'preflight');shutil.copytree(CHECK,C/'storage-check')
bind=[]
for name in sourcefiles:
 raw=subprocess.check_output(['git','-C',str(D),'show',SOURCE+':'+name]);assert raw==(D/name).read_bytes();dest=C/'source-snapshot/hybridclr_demo'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);bind.append({'repository':str(D),'branch':BRANCH,'commit':SOURCE,'path':name,'sha256':sha(dest)})
save(C/'SOURCE_BINDINGS.json',{'sourceCommit':SOURCE,'sourceAnchor':'357a9024865561362cd2c42fa8f793f56aac1763','postAnchorDocsOnly':True,'files':bind,'otherRepositoryPins':PINS,'productSourcesUnchanged':True})
command=json.loads((P/'commands/storage-diagnostic/receipt.json').read_text());capacity=[json.loads(line) for line in (CHECK/'capacity.jsonl').read_text().splitlines()];first=capacity[0];available=int(a['error']['message'].split('available ')[1].split()[0]);required=a['requiredAvailableBytesEachLocation'];minimum=min(s['minimumSampledAvailableBytes'].values());deficit=required-available
flags={'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'ReadyForHumanReviewGate':False,'pureInterpreterExpansionEnabled':False}
result={'kind':'R03LocalStoragePrerequisiteResultV1','sourceRepositories':pre,'sourceCommit':SOURCE,'startUtc':command['startUtc'],'endUtc':command['endUtc'],'result':'CapacityBlocked','batchState':'NotRun','storageAdmission':'Blocked','storageSession':'Failed','diagnosticExitCode':2,'diagnosticInvocations':1,'executingWrapperInvocations':0,'batchStarted':False,'unityLaunches':0,'freshBuilds':0,'freshPlayers':0,'freshEditorTests':0,'plannedBatch':{'cells':90,'builds':6,'players':59,'editorRosters':[18,754,755],'state':'NotRun'},'actualBatchCells':None,'coreResult':None,'coreLedger':None,'coreSeal':'NotRun','realAllocationProbes':'NotRun: failed capacity check precedes probes','requiredAvailableBytes':required,'admissionAvailableBytes':available,'admissionDeficitBytes':deficit,'minimumSampledAvailableBytes':minimum,'qFootprint':a['retainedQSize'],'capacityReserved':False,'historicalEvidence':{'state':'Passed','counts':audit['counts'],'uniquePathsVerified':audit['uniquePathsVerified'],'auditSha256':sha(P/'PRESERVED_EVIDENCE_AUDIT.json'),'reclassified':False},'hostSuites':[{'name':'storage','tests':48,'state':'Passed','receipt':str(P/'commands/storage-tests/receipt.json')},* [{'name':v['suite'],'tests':v['expectedTests'],'state':v['result'],'receipt':str(P/'commands'/v['suite']/'receipt.json')} for v in rc['suites']]],'sidecarPath':str(CHECK),'sidecarHashes':audit['sidecarHashes'],'batchPath':str(B),'executingStoragePath':str(STORAGE),'batchAndExecutingStorageRootsAbsent':True,'boundedProductFixes':[],'externalPrerequisite':'Operator-approved storage capacity/headroom; no safe approved deletion/relocation is assigned','exitState':'Local Validation -> Primary Implementation',**flags}
save(C/'LOCAL_STORAGE_RESULT.json',result)
body=f'''# Batch R storage prerequisite checkpoint

**CapacityBlocked; batch NotRun.** Source `{SOURCE}`. Diagnostic admission=Blocked, original session=Failed, diagnostic exit2, `batchStarted=false`. There was one diagnostic invocation and zero executing invocations. No Unity, IL2CPP, native compilation, build, Player, Editor Test Runner, core ledger/result/archive or seal was produced for R.

[LOCAL_STORAGE_RESULT.json](LOCAL_STORAGE_RESULT.json) is a prerequisite report, not a runtime batch verdict. [storage-check](storage-check) preserves the complete original diagnostic sidecar byte for byte. [preflight](preflight) records synchronization, read-first documents, environment, commands, supplemental filesystem observations and historical evidence custody. [SOURCE_BINDINGS.json](SOURCE_BINDINGS.json) authenticates the source snapshot. [MANIFEST.sha256](MANIFEST.sha256) covers checkpoint files except itself.

Policy required64GiB at each location; admission observed `{available}` bytes (10.22GiB), deficit `{deficit}` bytes (53.78GiB). The 20GiB operating-floor observation also latched Failed. Actual allocation probes were NotRun. All ten locations share one APFS Data-volume pool. The policy is conservative headroom, not a measured Unity peak, reserved storage or permission to delete evidence.

48 storage +5 orchestration +9 strict-schema host tests Passed. They provide no fresh Unity/Player acceptance. Historical Q manifest16183, prior custody143563, Q live index15046 and five top-level Q artifacts were reauthenticated; unique paths verified174796. All historical states remain unchanged, including Q's Failed integration and contaminated Failed unisolated warm certificates.

Live paths: `{P}`, `{CHECK}`. `{B}` and `{STORAGE}` remain absent. Folder date20261007 is the handoff identifier; diagnostic ran2026-10-07UTC /2026-10-06PDT. Read [Local report](../../../../Handoff/LOCAL_VALIDATION.md) and [Primary return](../../../../Handoff/RETURN_TO_WEB.md).

No Local product-source fix, capacity remediation, retry, threshold/scope change or new runtime acceptance. All acceptance flags false; PureInterpreter expansion disabled. Independent full-stage review pending. Latest pushed publication HEAD will be recorded externally at `{P}/PUBLICATION_RECEIPT.json` and in the final handoff; it is transport authority, not executed source.
'''
(C/'README.md').write_text(body)
links='../History/M07R/R03/'+C.name
rows='\n'.join(f'| `{W/name}` | `{BRANCH}` | `{pin}` |' for name,pin in PINS.items())
hashes='\n'.join(f'| `{name}` | `{value}` |' for name,value in audit['sidecarHashes'].items())
local=f'''## Current run — R03 batch R storage prerequisite, 2026-10-06 PDT / 2026-10-07 UTC

**CapacityBlocked; batch NotRun; admission Blocked; original storage session Failed; diagnostic exit2. Exit: Local Validation → Primary Implementation.** One diagnostic invocation `{command['startUtc']}` → `{command['endUtc']}` (2026-10-06 20:29:26 →20:29:46 PDT). Zero executing-wrapper/core invocations, Unity launches, builds, Editor executions or Players. The handoff's20261007 folder identifier is preserved; it does not change actual event clocks. Batch and executing sidecar roots remain absent. No90-cell result, core ledger/archive/index/seal or runtime acceptance is manufactured.

### Source authority and environment

All four owning checkouts were independently clean, matched their exact paths/branches/remote identities, and were safely fast-forwarded to the exact pushed handoff commits before diagnostics. Demo moved from Q publication `69af19f63ec20b900d28b3fab27c646d47264736` to `{SOURCE}`; other owning pins were already exact. Storage executable/CI anchor `357a9024865561362cd2c42fa8f793f56aac1763` is authenticated; its later delta is Docs-only. Q-to-source changes are only the four storage files, storage workflow and Primary docs. Existing Completion/R03/R02 product code, C#, package/native/IL2CPP pins and both source manifests are unchanged. No ordinary primary/control checkout, old app or Library was used for execution. Git top-level/branch/HEAD/status/remotes/worktrees/submodules and fetch/FF clocks are in [synchronization]({links}/preflight/synchronization.json) and [source authority]({links}/preflight/SOURCE_AUTHORITY.json).

| Actual owning repository | Branch | Diagnostic source commit |
| --- | --- | --- |
{rows}

Pinned Unity executable exists at `{env['unityPath']}`; authenticated CFBundleVersion=`2022.3.62f2`, Info.plist SHA `b7e25851c739c92d14f1441929c7b74d8b6e5b7d09b2b0f857e03a9b3b47710e`. Unity was not launched. Planned platform StandaloneOSX arm64; observed host macOS26.5.2(25F84), arm64; Python3.14.6. SDK-only `{env['sdkRoot']}` returned8.0.318; no Unity6000 launch. EXPECTED_DEMO_COMMIT=`{SOURCE}`, DOTNET_ROOT/ARM64 exact SDK path, MULTILEVEL_LOOKUP=0, TMPDIR=/private/tmp, PYTHONDONTWRITEBYTECODE=1. Both source-pin manifests, package manifest/lock and ProjectVersion match current Git blobs; exact bytes/hashes are in [environment]({links}/preflight/ENVIRONMENT.json) and [source bindings]({links}/SOURCE_BINDINGS.json). Gate helper Off; authoritative exact effective model unavailable, no inference or independent review claim. Source pins are separate from the final Local publication transport commit.

### Operations, states and storage evidence

The prescribed command was diagnostic only, without `--execute`, cwd `{D}`:

```text
{' '.join(command['command'])}
```

[Command receipt]({links}/preflight/commands/storage-diagnostic/receipt.json) records start/end/argv/cwd/exit and original stream hashes. All additional command operations/clocks are retained in preflight/COMMANDS.json, preflight/RETAINED_CONTRACT_RESULTS.json and commands/*/receipt.json; supplemental filesystem and custody operation clocks are in their individual reports. The executing command was never reached; no Unity operation or acceptance flag was changed.

| Operation | Actual state | Evidence/limit |
| --- | --- | --- |
| Source/remote/pin preflight | Passed | Four exact clean owning checkouts, pinned source blobs |
| Storage host tests | Passed | 48 cases,0 errors/failures/skips;03:29:26.248108→03:29:26.742996 UTC |
| LP orchestration host tests | Passed | 5 cases,0 skips;03:31:27.252531→03:31:27.411347 UTC |
| Strict schema host tests | Passed | 9 cases,0 skips;03:31:27.411578→03:31:27.507398 UTC |
| Real storage admission | Blocked |64GiB policy not met at any of10 roles |
| Real allocation/fsync/readback probes | NotRun |Capacity rejection precedes probes; mocked host tests do not establish actual probes |
| Diagnostic storage session | Failed |Second sample below20GiB operating floor; original latch preserved |
| Executing wrapper/core/90 cells | NotRun |No launch-intent; `batchStarted=false`, null exit/result; R root absent |
| Unity/IL2CPP/native compilation/six builds | NotRun |Dependent on admitted storage |
|18/754/755 Editor rosters/59 fresh Players | NotRun |No XML/runtime receipts produced for R |
| Restored-baseline, policy/bridge/resource/runtime proofs | NotRun |No fresh R product evidence; Q unchanged |
| Full-batch publication size/archive/seal | NotRun |No batch exists; only expressly permitted small factual blocker publication |
| Historical evidence custody | Passed |16183 checkpoint +143563 prior +15046 Q indexed +5 Q top-level bindings;174796 unique paths |

Q retained sizing:107514 files,9832 directories, logical `{a['retainedQSize']['logicalBytesPerPath']}` bytes, allocated unique-inode/planning `{a['retainedQSize']['planningBytes']}` bytes (13.19GiB), scan2.468s; includes live caches, physical APFS sharing unknown. `max(64GiB,2*B+20GiB)`=`{required}` bytes; formula term49,804,746,752 bytes, so64GiB floor dominates. At admission all10 roles had `{available}` bytes (10.223GiB), exact deficit `{deficit}` bytes (53.777GiB). Two capacity samples at03:29:46.447082 and03:29:46.717912 UTC; sampled minimum `{minimum}` bytes. Session latched `available {minimum} < required 21474836480`. This is a policy StorageBlocked exception with preserved dynamic trace, errno/filename null; it is not a fresh ENOSPC reproduction or a measured build high-water. No reservation or periodic executing monitor started.

Roles batch/restoredCapture observed `{BASE}` because planned roots were absent; workspace `{W}`; childTemp/pythonTemp `/private/tmp`; sidecar `{CHECK}`; Git common directories `/Users/ah/GitHub/hybridclr/{{hybridclr_demo,hybridclr,hybridclr_unity,il2cpp_plus}}/.git`. All device/fsid16777230, `df` maps to `/dev/disk3s1` mounted `/System/Volumes/Data`, same APFS containerdisk3. Free bytes from sibling volumes must not be summed. [Supplemental filesystem report]({links}/preflight/FILESYSTEM_SUPPLEMENT.json) binds fresh resolved-device diagnostics: APFS container capacity494,384,795,648, free10,964,729,856 bytes, Data usage457,173,430,272; configured quota/reserve values0 for its volumes, userquota output`none`. These are point observations, not guarantees of future allocations or reconstruction of Q's failure instant. Original `diskutil info -plist <ordinary directory>` calls (eight per admission/session diagnostic capture) remain Unavailable/exit1; supplemental `/dev/disk3s1` lookup Captured without changing the raw failures or product source.

Complete diagnostic files are retained live at `{CHECK}` and byte-identically in [storage-check]({links}/storage-check). Original hashes:

| Sidecar file | SHA-256 |
| --- | --- |
{hashes}

`{B}` and `{STORAGE}` were not created. No older batch/root/app was reused or rerun; Q/P/O/N and all earlier raw outcomes remain unchanged. [Custody audit]({links}/preflight/PRESERVED_EVIDENCE_AUDIT.json) authenticates Q manifest bytes against `{SOURCE}` Git blob, its16183 published files, all143563 inherited absolute-path bindings, all15046 Q live-index files and five Q top-level artifacts. No historical verdict is promoted; Q restored-baseline proof remains Unavailable, Q integration Failed, four contaminated unisolated certificates Failed, and older NoCoverage/Blocked/reused-audited states retain their original meanings.

### Local administrative correction, publication and exit

An initial Local admin-only version assertion read the descriptive CFBundleShortVersionString (`Unity version 2022.3.62f2`) as a bare version and stopped before commands/tests/diagnosis. The admin assertion was corrected to authoritative CFBundleVersion. [Correction receipt]({links}/preflight/PREFLIGHT_VERSION_FIELD_CORRECTION.json) retains exact before/after scripts/hashes and diagnosticInvocationsBeforeCorrection=0. No product-source change, substituted Unity, retry or second diagnostic resulted; exact48+5+9 host suites then Passed. No bounded product fix was made.

No capacity remedy is assigned or safely authorized: no deletion/relocation of evidence, caches, Libraries, Git history or user data; no external mount/path substitution, quota change, threshold weakening, source/expectation/deadline change or runtime invocation. [Small publication observation]({links}/preflight/SMALL_BLOCKER_PUBLICATION_CHECK.json) records measured remaining space and the limited checkpoint/report copy budget, separate from failed batch admission. Only these two Local-owned reports and [immutable checkpoint]({links}/README.md) are modified; all original diagnostic bytes are preserved. Manifest/JSON/local links/Git diff/source/custody checks and final four pushed heads are recorded in checkpoint/publication receipts. Latest pushed Local transport commit is recorded at `{P}/PUBLICATION_RECEIPT.json` and final handoff, not represented as executed source.

New Primary environmental prerequisite R03-LR-001 is detailed in [RETURN_TO_WEB.md](RETURN_TO_WEB.md). All dependent integrated R work remains NotRun. Operator-approved headroom and a new explicit source-bound handoff are required before future admission/execution; no product-source defect is established by this blocked prerequisite. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; PureInterpreter expansion disabled. Independent full-stage review and human approval pending. **Local Validation → Primary Implementation. Stop.**

'''
ret=f'''## Current return — R03 batch R storage admission, 2026-10-06 PDT / 2026-10-07 UTC

**CapacityBlocked; batch NotRun. Admission Blocked; original diagnostic session Failed; diagnostic exit2. Local Validation → Primary Implementation.** No Unity, IL2CPP, build, Editor or Player was launched for R. Read [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md), [R prerequisite checkpoint]({links}/README.md) and [LOCAL_STORAGE_RESULT.json]({links}/LOCAL_STORAGE_RESULT.json). All prior Q/P/O/N outcomes and evidence remain unchanged. No product-source repair is inferred.

### R03-LR-001 — Actual validation storage falls53.78GiB below required admission

**Symptom.** The exact source-bound diagnostic returned exit2 and `storageAdmission=Blocked`, `batchStarted=false`. Batch R and executing-storage roots are absent. Current Data pool has about10.22GiB available while admission requires64GiB at each validation role. The session independently latched Failed below20GiB. No90-cell runtime result or seal exists for R.

**Exact reproduction already performed once.** Use four source pins/paths in LOCAL_VALIDATION.md, demo `{SOURCE}`, branch `{BRANCH}`, EXPECTED_DEMO_COMMIT exact, Python3.14.6, SDK8.0.318 and verified Unity2022.3.62f2 path. The command below ran only diagnostics; do not execute it again into the existing CHECK root or call the core directly:

```text
{' '.join(command['command'])}
```

Cwd `{D}`; start `{command['startUtc']}`, end `{command['endUtc']}`, original exit2. Read admission and both capacity rows, then session and dispatch. No `--execute` invocation occurred.48 storage +5 orchestration +9 strict-schema independent host cases Passed; these do not remedy capacity or imply fresh product validation.

**Raw evidence and exact excerpts.** Live sidecar `{CHECK}`; identical copy `{C}/storage-check`. Command receipts and resolved-device/APFS/quota observations `{P}`; corresponding immutable preflight copy inside checkpoint. Each raw sidecar hash appears below; [custody audit]({links}/preflight/PRESERVED_EVIDENCE_AUDIT.json) preserves prior evidence. [Source bindings]({links}/SOURCE_BINDINGS.json) binds guard/entry/test/core/pin inputs; all four exact source repositories are in LOCAL_VALIDATION.md.

| Raw file | SHA-256 |
| --- | --- |
{hashes}

```text
storage_guard.admit:275 -> capacity_ok:147 -> require:35
StorageBlocked: batch: available {available} < required {required} bytes
admission.state=Blocked; capacityReserved=false; probes not reached
session.state=Failed; samples=2
StorageBlocked: batch: available {minimum} < required 21474836480 bytes
dispatch.batchStarted=false; batchExitCode=null; coreResultPath=null
```

Q sizing B=`{a['retainedQSize']['planningBytes']}` bytes (allocated unique inode; live caches retained);2B+20GiB=49,804,746,752;64GiBfloor governs. Admission deficit `{deficit}` bytes=53.777GiB. All10 roles use device/fsid16777230, `/dev/disk3s1` `/System/Volumes/Data`, containerdisk3. Supplemental actual-device/APFS commands Captured; container free10,964,729,856/494,384,795,648 bytes, volume quota/reserve values0, userquota`none`. Original ordinary-directory diskutil calls remain Unavailable/exit1, eight per diagnostic capture. No current OS ENOSPC was triggered: errno/filename null, observed failure is the explicit policy comparison.

**Most likely root cause / why permitted.** Actual shared APFS pool lacks the unchanged conservative admission headroom. The new guard correctly blocked before allocation probes, batch construction or Unity. The policy is not a proven peak/reservation; diagnostic mocked tests and prior source/compiler CI cannot create storage or establish future allocation availability. No product-source defect is established. No safe approved data/history deletion, evidence relocation or new mount/path is supplied.

**Affected scope.** All fresh R90 cells/six builds/59 Players/18+754+755 Editor cases/restored-baseline proof/strict bridge/resource/runtime/qualification/seal remain NotRun. They are not90 fabricated Blocked verdicts. Q still has89 Passed/1 Failed and sealPassed; Q's zero-root/zero-closure proof remains Unavailable. Earlier historical states and all contaminated Failed unisolated warm certificates are unchanged. Small factual blocker publication is separate from nonexistent full-batch packing.

**Recommended Primary direction.** Reconcile this environmental prerequisite and coordinate an operator-approved capacity/retention plan with genuine sufficient headroom at every required location. Preserve all original evidence/caches/Git history; no threshold reduction, arbitrary deletion, source fix or path substitution is justified. Once remediation is specifically authorized, issue a fresh explicit source-bound Local handoff using unused numbered diagnostic and execution locations. Re-measure Q, actual locations/quotas, run real allocation probes and require fresh admission. Only then use the storage-checked executing wrapper once; do not bypass admission or retry Q/P/O/N. R never started, but its current diagnostic root is immutable and cannot be reused.

**Remaining uncertainty / diagnostic limit.** Future competing writers, metadata limits and actual build high-water are unknown; no reservation was taken. Point-in-time quota/reserve0 observations do not retrospectively identify Q's allocation boundary. Eight ordinary-directory `diskutil info` errors per capture were resolved with a separate read-only device lookup; raw failures remain Unavailable. Any future harness improvement to resolve mount/device arguments belongs to Primary and should preserve unsupported states; no Local implementation change is assigned. Complete storage admission and integrated runtime acceptance remain unvalidated.

**Validation after capacity remediation.** In a separately authorized unused source-bound run require admissionAdmitted with all real probes, storageSessionPassed, unchanged complete90-cell matrix, six fresh builds,59 fresh Players, exact18/754/755 zero-skip/inconclusive Editor scopes, binding-before-integration, live policy/three guards, five source-bound sidecars/P05 restoration, restored-baseline zero roots/closure, strict bridge/resource aggregate/codec proofs, raw custody/seal and final authority. Preserve Q/P/O/N unchanged; a green focused completion still requires Primary reconciliation/independent full-stage review and explicit acceptance.

No Local product-source change, capacity remediation, retry or new acceptance. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; PureInterpreter expansion disabled. **Local Validation → Primary Implementation. Stop.**

'''
history=[]
for name,new,oldprefix,newprefix in [('LOCAL_VALIDATION.md',local,'## Current run','## Historical run'),('RETURN_TO_WEB.md',ret,'## Current return','## Historical return')]:
 path=D/'Docs/AssemblyShadow/Handoff'/name;old=path.read_text();assert old.encode()==subprocess.check_output(['git','-C',str(D),'show',SOURCE+':'+str(path.relative_to(D))]);heading,tail=old.split('\n',1);assert oldprefix in tail;preserved=tail.replace(oldprefix,newprefix,1);path.write_text(heading+'\n\n'+new+preserved.lstrip('\n'))
 history.append({'file':str(path.relative_to(D)),'oldSha256':hashlib.sha256(old.encode()).hexdigest(),'historicalBodySha256':hashlib.sha256(preserved.lstrip('\n').encode()).hexdigest(),'onlyHistoricalEdit':'First current heading becomes historical; all prior evidence/verdict body preserved','currentSha256':sha(path)})
save(C/'REPORT_HISTORY_PRESERVATION.json',{'sourceCommit':SOURCE,'reports':history})
# Exempt exact captured streams/source only when their pre-existing whitespace would fail diff --check.
exempt=[]
for p in sorted(C.rglob('*')):
 if p.is_file() and p.suffix in ['.log','.py','.txt','.json','.yml','.md'] and (p.is_relative_to(C/'preflight') or p.is_relative_to(C/'source-snapshot')):
  r=subprocess.run(['git','diff','--no-index','--check','/dev/null',str(p)],capture_output=True)
  if r.returncode!=0:
   assert r.returncode==2 or r.returncode==1,(p,r.stderr)
   exempt.append({'path':str(p.relative_to(C)),'sha256':sha(p),'diagnostic':r.stdout.decode(errors='replace')})
if exempt:
 (C/'.gitattributes').write_text('# Preserve authenticated original source/stream whitespace. Owned prose remains checked.\n'+''.join('"'+r['path']+'" -whitespace -text\n' for r in exempt))
save(C/'RAW_WHITESPACE_PRESERVATION.json',{'exemptedCapturedFiles':exempt,'normalOwnedProseChecksRequired':True})
for p in C.rglob('*.json'):json.loads(p.read_text())
manifest=[]
for p in sorted(C.rglob('*')):
 if p.is_file():manifest.append(sha(p)+'  '+str(p.relative_to(C)))
(C/'MANIFEST.sha256').write_text('\n'.join(manifest)+'\n')
for name,value in audit['sidecarHashes'].items():assert sha(CHECK/name)==sha(C/'storage-check'/name)==value
assert not B.exists() and not STORAGE.exists()
print(json.dumps({'checkpoint':str(C),'files':len(manifest)+1,'bytes':sum(p.stat().st_size for p in C.rglob('*') if p.is_file()),'result':result['result'],'batchState':result['batchState'],'admissionDeficitBytes':deficit,'sidecarFiles':len(audit['sidecarHashes'])}),flush=True)
