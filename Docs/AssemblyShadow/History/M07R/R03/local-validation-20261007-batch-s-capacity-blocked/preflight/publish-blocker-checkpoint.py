"""Copy and validate only Local prerequisite-blocker evidence and reports."""
from pathlib import Path
import json,hashlib,shutil,subprocess,datetime,re
P=Path(__file__).resolve().parent;BASE=P.parent;W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';PIN='e8fda852684f584295fe37830340ab3c9f3fcc4f';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-capacity-blocked';CHECK=BASE/'StorageCheck-R03LocalBatch-20261007S-lr-recovery';AUDIT=BASE/'RetainedR-R03LocalBatch-20261007S-lr-recovery';TRANSPORT=BASE/'Transport-R03LocalBatch-20261007S-lr-recovery'
def load(p):return json.loads(Path(p).read_text())
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(*args):return subprocess.check_output(['git','-C',str(D),*args])
assert git('rev-parse','HEAD').decode().strip()==PIN and not git('status','--short');assert load(P/'HISTORICAL_CUSTODY_AFTER.json')['state']=='Passed';assert load(P/'storage-publication-check.json')['state']=='Passed';s=load(P/'LOCAL_STORAGE_RESULT.json');assert s['result']=='CapacityBlocked' and not s['batchStarted'];assert not C.exists();C.mkdir();beg=utc();copies=[]
for root,label in [(P,'preflight'),(AUDIT,'retained-r-audit'),(TRANSPORT,'transport'),(CHECK,'storage-diagnostic')]:
 for src in sorted(root.rglob('*')):
  if src.is_file():
   dest=C/label/src.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest);assert sha(src)==sha(dest);copies.append({'source':str(src),'copy':str(dest.relative_to(C)),'size':dest.stat().st_size,'sha256':sha(dest)})
(C/'COPY_BINDINGS.json').write_text(json.dumps({'kind':'ExactPrerequisiteEvidenceCopies','startUtc':beg,'endUtc':utc(),'files':copies,'rawBytesUnchanged':True},indent=2)+'\n');(C/'LOCAL_STORAGE_RESULT.json').write_bytes((P/'LOCAL_STORAGE_RESULT.json').read_bytes())
sourcePaths=['Tools/AssemblyShadow/R03/git_diagnostics.py','Tools/AssemblyShadow/R03/run_local.py','Tools/AssemblyShadow/R03/source-pins.json','Tools/AssemblyShadow/R03Completion/source-pins.json','Tools/AssemblyShadow/R03Completion/fixture_authority.py','Tools/AssemblyShadow/R03Completion/resource_pipeline.py','Tools/AssemblyShadow/R03Completion/retained_transaction.py','Tools/AssemblyShadow/R03Completion/lr-retained.json','Tools/AssemblyShadow/R03Completion/transport_preflight.py','Tools/AssemblyShadow/R03Completion/test_lr_git.py','Tools/AssemblyShadow/R03Completion/test_lr_recovery.py','Tools/AssemblyShadow/R03Completion/test_lr_retained.py','Tools/AssemblyShadow/R03Storage/storage_guard.py','Tools/AssemblyShadow/R03Storage/run_storage_checked.py','Tools/AssemblyShadow/R03Storage/test_storage_guard.py','Tools/AssemblyShadow/R03Storage/test_storage_dispatch.py','.github/workflows/r03-lr-contracts.yml']
bindings=[]
for rel in sourcePaths:
 raw=git('show',PIN+':'+rel);assert raw==(D/rel).read_bytes();dest=C/'source-snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);bindings.append({'path':rel,'sha256':sha(dest),'gitCommit':PIN,'snapshot':str(dest.relative_to(C))})
(C/'SOURCE_BINDINGS.json').write_text(json.dumps({'sourceCommit':PIN,'sourceAnchor':'9f27feb647bbf2d2bc82483700fe4f78e5ea60be','files':bindings,'repositories':load(P/'SOURCE_AUTHORITY.json')['repositories'],'postAnchorDocsOnly':True},indent=2)+'\n');auth=load(P/'SOURCE_AUTHORITY.json');before=load(P/'HISTORICAL_CUSTODY_BEFORE.json');after=load(P/'HISTORICAL_CUSTODY_AFTER.json');link='../History/M07R/R03/'+C.name;environment=load(P/'ENVIRONMENT.json');ops=load(P/'PREREQUISITE_SEQUENCE_FINAL.json')['operations'];storageOp=next(o for o in ops if o['label']=='storage-diagnostic');rowtext='\n'.join(f'| `{W/n}` | `{auth["branch"]}` | `{h}` |' for n,h in auth['repositories'].items());hashtext='\n'.join(f'| `{n}` | `{h}` |' for n,h in s['sidecarHashes'].items());available=s['availableAdmissionBytes']/1024**3;deficit=s['deficitBytes']/1024**3
local=f'''## Current run — R03 batch S prerequisites, 2026-10-07 PDT / 2026-10-08 UTC

**CapacityBlocked; batch NotRun. Admission Blocked; diagnostic session NotAdmitted; diagnostic exit2. Exit: Local Validation → Primary Implementation.** No S core was constructed, executing wrapper invoked, Unity/IL2CPP/native build/Editor/Player launched, or runtime result/ledger/seal produced. All90 cells, six builds,59 Players and18/754/755 Editor scopes are NotRun, without fabricated runtime cells. [Factual Local prerequisite result]({link}/LOCAL_STORAGE_RESULT.json), [checkpoint]({link}/README.md), [final prerequisite sequence]({link}/preflight/PREREQUISITE_SEQUENCE_FINAL.json).

### Exact source and environment authority

All four owning checkouts independently passed top/branch/HEAD/status/origin/worktree/submodule verification and exact fresh remote-tip checks, then safe fast-forward. Only demo changed: R publication1fb504b2 → authorized `{PIN}`. Source anchor9f27feb647bbf2d2bc82483700fe4f78e5ea60be is an ancestor; final delta after it is Docs-only. [Source authority]({link}/preflight/SOURCE_AUTHORITY.json), bootstrap command receipts and [exact source snapshots]({link}/SOURCE_BINDINGS.json) bind paths/operations/clocks/streams. Credentials/protocol/SSH policy, native/package pins, runtime expectations, source manifests, deadlines, warm-up, leases and storage thresholds were not changed. No primary/control checkout was used for validation; shared Git common metadata paths remain explicit.

| Owning repository | Branch | Prerequisite source commit |
| --- | --- | --- |
{rowtext}

Unity2022.3.62f2 executable `{environment['unityPath']}` was present with exact CFBundleVersion; it was not launched. Planned target StandaloneOSX arm64. SDK8.0.318 at SDK-only `{environment['sdkRoot']}` verified; Unity6000 was not launched. Python3.14.6, macOS26.5.2 build25F84, Apple clang21.0.0 and active CommandLineTools MacOSX SDK26.5 were observed. Full-Xcode version is Unavailable because xcodebuild requires a full Xcode installation; this is distinct from available active SDK/compiler and NotRun native compilation. [Environment and source-setting hashes]({link}/preflight/ENVIRONMENT.json), operations/* receipts retain exact paths, clocks, exit and stream SHA-256. No developer-directory or SDK substitution occurred.

Administrative observation: the initial metadata logger incorrectly asserted the optional Xcode-version query must succeed and stopped before any mandated retained audit/transport/tests/admission. Original script/exit/log/initial sequence remain preserved. Continuation reused those version receipts, retained Xcode-version Unavailable, verified active SDK/clang, and then ran each required prerequisite once. [Administrative observation]({link}/preflight/ADMIN_PREPARATION_OBSERVATION.json). No product source fix or validation-phase retry. Prior ancillary effective-main-model identity observation remains unresolved; no model guess, gate PASS/Off or independent-review claim.

### Completed prerequisites and factual missing scope

| Validation | State and evidence |
| --- | --- |
| Retained R six-file audit | Passed; original restore cell Failed; settings remain staged; restorationPerformed=false; original Git cause Unavailable; five restore outputs remain absent. [Initial report]({link}/retained-r-audit/verification.json), [final independent re-read]({link}/preflight/RETAINED_R_AFTER.json) |
| Four-owner transport | TransportReady; all4 rows Passed; point-in-time only. [Report and bounded Git observations]({link}/transport/verification.json) |
| Local LR host selection | 45 tests Passed, zero failures/errors/skips; host controls do not establish Unity restoration. operations/lr-tests receipts/streams |
| Local storage suite | 48 tests Passed, zero failures/errors/skips. operations/storage-tests receipts/streams |
| Full historical custody | Passed before and after; {after['uniqueFiles']:,} unique files; unchanged historical Q/P/O/N, original blocked R, published R and indexed live evidence. Current unindexed retained-R caches are separately captured before/after, not promoted to historical runtime acceptance. [Before]({link}/preflight/HISTORICAL_CUSTODY_BEFORE.json), [after]({link}/preflight/HISTORICAL_CUSTODY_AFTER.json), authenticated full map and authority |
| Fresh diagnostic admission | Blocked; session NotAdmitted; exit2; batchStarted=false; probes NotRun before allocation |
| Executing admission / core S / builds / Editors / Players | NotRun; core and executing-sidecar paths absent |
| S P05 cleanup/fresh remote acceptance/finalization/integration/bridge/resource/measurement proofs | NotRun; no recovery or runtime receipt is claimed |
| Core ledger/result/index/archive/seal | Unavailable because no core batch exists; prerequisite artifacts remain separate |

### Capacity evidence and command

Diagnostic start `{storageOp['startUtc']}`, end `{storageOp['endUtc']}` UTC (October7 PDT); exact command cwd `{D}` and source/environment/stream bindings are retained:

```text
{' '.join(storageOp['argv'])}
```

Measured retained-Q planning size14,164,955,136 bytes (107,514 files;9,832 directories), unchanged source-bound input. Formula `max(64GiB,2*B+20GiB)` requires **{s['requiredBytes']:,} bytes (64GiB)** at each relevant location. Initial observation at2026-10-08T02:15:43.925246Z /2026-10-07 19:15:43 PDT showed **{s['availableAdmissionBytes']:,} bytes ({available:.3f}GiB)**. Deficit **{s['deficitBytes']:,} bytes ({deficit:.3f}GiB)**. Exact original error: `batch: available 62512148480 < required 68719476736 bytes`. Two capacity samples are retained; final minimum62,512,091,136 bytes is a separate later sample. The20GiB operating floor remained satisfied and no operating fault was latched; admission still failed its higher budget. No reservation/high-water/future-readiness claim.

All10 roles reported device/fsid16777230 on the same Data/APFS pool. Resolved `/dev/disk3s1` /containerdisk3 observations showed volume quota/reserve0 and user quota none; original ordinary-directory diskutil errors remain Unavailable. [Supplement]({link}/preflight/FILESYSTEM_SUPPLEMENT.json), [original sizing/traceback]({link}/storage-diagnostic/admission.json), capacity.jsonl, session.json and dispatch.json. APFS sibling capacity is not summed. No history/cache/data deletion, relocation, credential repair, capacity reclamation, mount substitution or threshold change was performed.

| Original diagnostic artifact | SHA-256 |
| --- | --- |
{hashtext}

No live S footprint exists, so the core footprint-plus20GiB publication check is NotRun. A separately labeled prerequisite-publication budget measured the actual factual evidence payload plus20GiB at checkout/preflight/actual Git common directory and Passed before copying. [Receipt]({link}/preflight/storage-publication-check.json); it does not grant batch admission.

### Publication and exit

Only Local-owned LOCAL_VALIDATION.md, RETURN_TO_WEB.md and new immutable `{C.name}` are changed. Exact copy/source/JSON/hash/link/manifest/whitespace/staged-byte checks accompany publication. All historical report bodies are preserved; only the first Current heading becomes Historical. Latest pushed four-repository commits and final remote/cleanliness verification are recorded externally at `{P}/PUBLICATION_RECEIPT.json` and in the final handoff; publication HEAD is separate from prerequisite source `{PIN}`. No runtime result is manufactured for synchronization or blocked admission.

Primary must reconcile the environmental prerequisite with the operator: establish measured headroom safely at every relevant shared-pool location while preserving history, then supply a separate authorized fresh source/root handoff. Do not retry this diagnostic, reuse its outputs, launch S, or infer runtime repair acceptance from host/transport tests. No new product-source defect is established. R remains ReturnRequired47/1/42, staged and immutable; all contaminated unisolated warm certificates remain Failed. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; PureInterpreter expansion disabled. Independent full-stage review/human approval, R02 CPU/H1 RSS and production-performance decisions remain pending. **Local Validation → Primary Implementation. Stop.**

'''
ret=f'''## Current return — R03 batch S prerequisites, 2026-10-07 PDT / 2026-10-08 UTC

**CapacityBlocked; batch NotRun.** Read [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md), [immutable checkpoint]({link}/README.md), [Local prerequisite result]({link}/LOCAL_STORAGE_RESULT.json) and [original admission]({link}/storage-diagnostic/admission.json). No new non-trivial product-source issue is established; this is an unmet environmental prerequisite, not a fresh Unity/Player result or proof of the LR repair.

Exact source `{PIN}` and unchanged other3 pins are listed in LOCAL_VALIDATION.md. Retained R read-only audit Passed, all4 transport rows Passed,45 LR and48 storage tests Passed with zero skips/errors/failures. Full before/after custody Passed for{after['uniqueFiles']:,} files, including retained R's still-staged settings and absent restoration outputs. Original R's Git cause remains Unavailable. No R recovery or historical reclassification occurred.

At2026-10-07 19:15:43 PDT /2026-10-08T02:15:43.925246Z, fresh storage admission Failed its prerequisite: available **{s['availableAdmissionBytes']:,} bytes ({available:.3f}GiB)** versus required **{s['requiredBytes']:,} bytes (64GiB)**; deficit **{s['deficitBytes']:,} bytes ({deficit:.3f}GiB)**. Formula is unchanged `max(64GiB,2*14,164,955,136+20GiB)`. Original admission state Blocked, diagnostic session NotAdmitted, diagnostic exit2, batchStarted=false; allocation probes NotRun. Same shared APFS pool, volume quota/reserve0 and user quota none; no reservation or future capacity guarantee.

**Required Primary/operator action:** Establish adequate measured headroom safely without deleting/moving preserved history or changing thresholds, credentials, protocol or source pins. Then publish a separately authorized handoff with unused prerequisite/execution roots and fresh transport/storage checks. Local did not reclaim capacity or launch an executing wrapper. The current diagnostic and all old evidence remain immutable.

**Validation still required:** Actual new-source Unity/P05 exact restoration followed by fresh remote success, finalization,755 resource roster, all90 cells/six builds/59 Players and18/754/755 Editor scopes, graph-before-integration, zero roots/closure, live policy, strict bridge/resource aggregate/codec/measurement proofs and seal. All of this is NotRun for S; earlier R/Q/P evidence cannot substitute. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; PureInterpreter expansion disabled. Independent full-stage review/human approval and prior performance risks remain pending. **Local Validation → Primary Implementation. Stop.**

'''
history=[]
for name,new,prefix in [('LOCAL_VALIDATION.md',local,'## Current run'),('RETURN_TO_WEB.md',ret,'## Current return')]:
 f=D/'Docs/AssemblyShadow/Handoff'/name;raw=f.read_bytes();assert raw==git('show',PIN+':'+str(f.relative_to(D)));title,body=raw.decode().split('\n',1);old=body.replace(prefix,prefix.replace('Current','Historical'),1).lstrip('\n');assert prefix in body;f.write_text(title+'\n\n'+new+old);history.append({'file':str(f.relative_to(D)),'priorGitCommit':PIN,'priorFileSha256':hashlib.sha256(raw).hexdigest(),'historicalBodySha256':hashlib.sha256(old.encode()).hexdigest(),'onlyHistoricalEdit':'First Current heading changes to Historical','currentFileSha256':sha(f)})
(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps({'reports':history},indent=2)+'\n');(C/'README.md').write_text(f'''# Batch S prerequisite blocker checkpoint

**CapacityBlocked; batch NotRun.** No executing wrapper, Unity, native build, Editor or Player launch; no core result/ledger/seal. Prerequisite source `{PIN}`. Retained R remains staged and unchanged.

[Local result](LOCAL_STORAGE_RESULT.json), [storage admission](storage-diagnostic/admission.json), [transport](transport/verification.json), [retained R](retained-r-audit/verification.json), [full custody](preflight/HISTORICAL_CUSTODY_AFTER.json), [source bindings](SOURCE_BINDINGS.json), [copy hashes](COPY_BINDINGS.json), [Local report](../../../../Handoff/LOCAL_VALIDATION.md), [Primary return](../../../../Handoff/RETURN_TO_WEB.md).

45 LR and48 storage tests Passed; all4 transport rows Passed; full custody290,082 files Passed. Admission requires64GiB, observed{available:.3f}GiB, deficit{deficit:.3f}GiB. Original session NotAdmitted/probes NotRun. MANIFEST.sha256 covers all files except itself. Publication authority is recorded at `{P}/PUBLICATION_RECEIPT.json`, separately from prerequisite source. All acceptance flags remain false. Local Validation → Primary Implementation. Stop.
''')
(P/'CHECKPOINT_LOCATION.json').write_text(json.dumps({'path':str(C),'sourceCommit':PIN,'result':'CapacityBlocked','batchResult':'NotRun'},indent=2)+'\n');print('Owned factual prerequisite checkpoint and reports written',str(C),flush=True)
