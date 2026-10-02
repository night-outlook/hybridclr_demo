"""Publish factual reports only after completed, authenticated focused H success."""
import datetime,hashlib,json,pathlib,shutil,subprocess
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261002H-rejection';R=P.parent/'R03LocalBatch-20261002H-rejection';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261002-batch-h-evidence-ready';rel='../History/M07R/R03/'+C.name
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();result=load(R/'LOCAL_BATCH_RESULT.json');auth=load(P/'POSTRUN_AUTHENTICATION.json');integrated=load(P/'INTEGRATED_OBSERVATIONS.json');rej=load(P/'REJECTION_RUNTIME_AUDIT.json');prod=load(P/'PRODUCER_RUNTIME_AUDIT.json');inv=load(P/'runner-exit.json')
assert result['result']=='EvidenceReadyForPrimaryReview' and result['sealStatus']=='Passed' and inv['exitCode']==0 and auth['status']==rej['status']=='Passed' and len(result['cells'])==37 and all(c['result']=='Passed' for c in result['cells'])
assert all(x['status']=='Passed' for row in prod['rows'] for x in row['checks'].values())
command=' '.join(inv['command']);pins=result['repositories'];pinrows='\n'.join('| `'+str(W/n)+'` | `'+pins[n]+'` |' for n in ['hybridclr_demo','hybridclr','hybridclr_unity','il2cpp_plus']);cellrows='\n'.join('| `'+c['id']+'` | '+c['result']+' |' for c in result['cells']);hashrows='\n'.join('| `'+n+'` | `'+h+'` |' for n,h in auth['topLevelHashes'].items());rejectionrows=[]
for row in rej['rows']:
 f=row['fullReadBindings'];layouts=f[0]['layouts'];identities=', '.join(v['target']['typeKey'] for v in layouts)
 rejectionrows.append('| `'+row['case']+'` | '+str(row['pid'])+' | -2 | '+str(f[0]['nativeReturn'])+' / '+str(f[1]['nativeReturn'])+' | '+str(len(layouts))+' | `'+row['rawSha256']+'` | `'+row['verificationSha256']+'` |')
rejectiontable='\n'.join(rejectionrows)
warmrows=[];controlrows=[]
for row in prod['rows']:
 f=row['producerFence'];label=row['case'];window=row['checks']['completeWindowAndReconciliation']['evidence'];delta=window['exactLoopDelta']
 if row['kind']=='StrictIsolatedMain':warmrows.append('| `'+label+'` | '+str(row['pid'])+' | '+str(f['elapsedMicros'])+' | '+str(f['admitted'])+'/'+str(f['completed'])+' | '+str(f['deferred'])+'/'+str(f['deferredCompleted'])+' | zero |')
 else:
  ev=row['checks']['naturalProducerDiagnostic']['evidence'];controlrows.append('| `'+label+'` | '+str(row['pid'])+' | '+ev['unisolatedWarmCertificate']+' | '+str(ev['identifiedLoopAdmissions'])+' | '+str(delta['admissionCacheMisses'])+'/'+str(delta['admissionProofAttempts'])+'/'+str(delta['admissionEntries'])+'/'+str(delta['admissionRetainedBytes'])+' |')
warmtable='\n'.join(warmrows);controltable='\n'.join(controlrows);size=(R/'evidence.tar.gz').stat().st_size;archivehash=auth['topLevelHashes']['evidence.tar.gz']
start=datetime.datetime.fromisoformat(inv['startedUtc']);end=datetime.datetime.fromisoformat(inv['endedUtc']);from zoneinfo import ZoneInfo
localtimes=start.astimezone(ZoneInfo('America/Los_Angeles')).strftime('%Y-%m-%d %H:%M:%S')+'–'+end.astimezone(ZoneInfo('America/Los_Angeles')).strftime('%H:%M:%S %Z')
body=f'''## Current run — R03 batch H, 2026-10-02: focused rejected-stage preservation Passed; return for Primary reconciliation

**Result=EvidenceReadyForPrimaryReview; 37 cells: 37 Passed / 0 Failed / 0 Blocked; sealStatus=Passed; runner exit 0. Exit: Local Validation → Primary Implementation.** Exactly one fresh invocation, PID {inv['pid']}, {localtimes}; UTC {inv['startedUtc']}–{inv['endedUtc']}. All four fresh native build roles, 754 selected actual Editor cases with zero skips, and all 23 fresh-process Players passed their defined contracts. The five strict negative cases retain error 16 through the 16-byte/-2 capacity control, two complete bounded native reads and final raw capture. All six strict main warm certificates, full positive C07 and producer-controls aggregate Passed. Contaminated natural controls' unisolated warm certificates remain Failed. No Local source fix, terminal restoration, counter/scope/pin/ownership/lease/warm-up/deadline change, retry or prior-app reuse occurred.

### Executed authority and environment

All owning repositories independently matched their absolute top-level paths, branch `codex/assembly-shadow-r01b-h1`, clean status, canonical origins `git@github.com:night-outlook/<repository>.git`, exact local HEAD and remote tip before and after execution. Demo safely fast-forwarded from G Local publication `0d8a19830ce454d22335c854978816a830997187`; IL2CPP advanced coherently to the H source pin. Source anchor `9d70494c97e4efc9597a3e071f63c1489c6ac396` is an ancestor and its delta to the executed demo is documentation-only. Original source pins, package file reference, fixture IDs, build roles, Editor filter and Player expectations are authenticated in [preflight]({rel}/preflight) and each isolated source/config receipt. Earlier owning/linked worktrees are preserved.

| Owning repository path | Exact executed commit |
| --- | --- |
{pinrows}

Fresh detached reference worktrees beneath `{R}/reference-worktrees` remain clean at native `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, IL2CPP `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`, graph-test package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`. The four role-specific `projects/` and `builds/` roots retain their own Library/HybridCLRData/install SDK/app outputs; no ordinary primary checkout, old app, prior cache or control sibling is mixed in. [RETAINED_LIVE_ROOTS.json]({rel}/preflight/RETAINED_LIVE_ROOTS.json) records exact retained paths. Schema-2 build receipts and nativeBinding bind each installed root, non-generated core and full app inventory to source/config hashes. Build GUID remains explicitly Unavailable where the receipt reports it; no matching GUID is inferred.

Environment: macOS 26.5 arm64; Python 3.14.6; SDK 8.0.318/runtime 8.0.21; PowerShell 7.6.3; Apple clang 21.0.0/macOS SDK 26.5. Unity executable `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, StandaloneOSX/arm64. SDK-only root `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`; no Unity 6000 Editor execution. Pinned Unity 2022.3.62f2 `MonoBleedingEdge/lib/mono/unityaot-macos/mscorlib.dll` SHA-256 `d89d5124cafb873b34c2eac68d2ece41d14fec10999baf0e4620276dff54ab83`. Scoped SDK PATH/DOTNET_ROOT/DOTNET_ROOT_ARM64, DOTNET_MULTILEVEL_LOOKUP=0, PYTHONDONTWRITEBYTECODE=1 and TMPDIR=/private/tmp are recorded in runner-invocation.json. No Unity Editor was running at preflight. Gate helper Off; no independent stage-review or Human Review Gate verdict claimed.

```text
{command}
```

### Every required cell and supporting contracts

All statuses below are fresh G-independent H results. Expected-negative compiler exit1 and expected Validate16 rejection are successful contracts, not successful product operations.

| Cell | Original sealed state |
| --- | --- |
{cellrows}

Supporting Passed checks: 183 verifier Python tests, both 9-case graph suites, 35 admission contracts, 15 real DLL fixtures, 33 unsigned-reference audits, 33 pinned-Unity consumers, valid/invalid Editor lifecycle probes, full package/helper API compilation (425 inputs/115 defines), four fresh IL2CPP/native arm64 builds and 754 selected Editor XML cases with zero skips. The 83 command receipts retain authenticated streams and clean process-group completion; 80 exit0, only named 0048/0050/0055 expected-negative controls exit1. The old C helper produces exactly two CS0266 errors, while current helper/product builds succeed. Seven birth-authenticated Unity completion receipts retain the original inner exits and bounded owned VBCSCompiler retirement; no global compiler kill or hidden survivor was used. Local did not separately rerun Primary's 90 native header processes or 35 syntax checks; their source-bound CI records are historical/host evidence, not extra Local Player coverage.

All original 19 main Players and four PC controls executed with distinct PID/run nonce and bound request/raw/build-receipt hashes. All 23 Player command exits0 and source-defined semantic/diagnostic verifications Passed. Reference/off unavailable native probe states remain explicit; they do not acquire fabricated snapshot coverage. M01 remains **NoCoverage**, excluded because its frozen fixture is unavailable, not counted as an Editor skip/pass. Full-stage legacy/resource, broader generic/interface/delegate/stack-trace, startup/capacity/performance/memory, gated qualification and independent full R03 review are **NotRun in this focused batch and remain open**.

### Five negative paths: non-mutating observation witnessed

[REJECTION_RUNTIME_AUDIT.json]({rel}/preflight/REJECTION_RUNTIME_AUDIT.json) reconciles every original source-bound `verification.rejectionObservation` subcheck with the raw observation. Overall raw/runtimeProbe schemas3 and string-encoded `rejectionProbe` schema1/policy R03RejectedProbeNonMutationV1 are preserved. Each one-transaction process reaches Configure/Begin/Reserve/Stage success then Validate16/state 8/unpublished. Four captures (`before`, `afterSmall`, `afterFirst`, `afterSecond`) plus final ordinary raw diagnostics retain exact immutable transaction projection and the entire recovery document: lastError/terminalFailureCode16, failed state 8, generation0, no Commit/publication/module/business initialization, RestartRequired. No probe exception or error 15 occurs. Whole diagnostic strings remain retained; independent ordinary-class enumeration is not asserted invariant.

| Case | Fresh PID | Capacity return | Full-read return bytes (first/second) | Retained rows | raw.json SHA-256 | verification.json SHA-256 |
| --- | --- | --- | --- | --- | --- | --- |
{rejectiontable}

Both native full reads return exactly their UTF-8 payload length below131072. C02/D01 retain two layout rows (`layout/<Module>` and `layout/R03.Node`); C08/C09 retain one prior `R03Contract/<Module>` row; C10 retains `R03Contract/<Module>` and `R03Contract/R03.Node`. Layout rows remain exactly equal across reads, identities have R03OwnedLayoutIdentityV1 and Captured baseline/target statuses with distinct opaque physical values and complete type keys. Each explicit captured transaction projection and entire recovery compare equal at all five boundaries. The second complete native JSON, complete diagnostics/recovery strings, their byte hashes and statuses are retained. An earlier retained row is not assumed to identify the actual failing type; failingRowIdentified=false remains explicit. These fresh H observations satisfy the focused LG-001 repair verification; G's five Failed cells and missing probes remain historical Failed/Unavailable without schema upgrade or retroactive closure.

### Six strict main warm witnesses and four natural controls

[PRODUCER_RUNTIME_AUDIT.json]({rel}/preflight/PRODUCER_RUNTIME_AUDIT.json) retains all ten raw probes, 50 adjacent native spans, exact counter/event reconciliation and source/DLL/build bindings. Each main exact loop has zero all-thread cold admission/proof/layout/workspace work and at least 10000 hits/baseline checks, unchanged eight preparation allocations and 10000 business allocations. Leases remain R03ArrayPoolFinalizerFenceV1/5000ms, acquired/released/drained=true, expired/invalid=false. All deferred matching callbacks complete.

| Main witness | Fresh PID | Lease elapsed µs | Admitted/completed | Deferred/completed | Exact-loop cold work |
| --- | --- | --- | --- | --- | --- |
{warmtable}

| Natural control | Fresh PID | Unisolated warm certificate | Identified admissions | Miss/proof/entry/byte delta |
| --- | --- | --- | --- | --- |
{controltable}

Producer-controls aggregate Passed, with {integrated['producerControls']['identifiedLoopAdmissions']} identified in-loop admissions. All four controls observe an exact-loop Object::NewAllocSpecific admission on probe thread2 rather than owner1, type `System.Runtime.CompilerServices.ConditionalWeakTable<byte[][], object>.Enumerator`. Actual context identifies `mscorlib/System.Gen2GcCallback`, delegate `Gen2GcCallbackFunc`, token100672638, closed declaring type `System.Buffers.TlsOverPerCoreLockedStacksArrayPool<byte>`, recognizedArrayPool=true. Complete full keys, numeric native runtime thread identifiers and all four cold events per control remain in raw/audit evidence; no cross-process thread or pointer identity is inferred. Diagnostic success does not promote a contaminated control's Failed warm certificate. Pairing uses DLL/source/config/build hashes and distinct PID/run IDs, never pointer/thread equality across processes. Lease isolation remains diagnostic-only and may delay queued finalizers; it is not production GC/performance qualification. No H attribution is retroactively assigned to older E/F evidence.

Full C07 main and the paired control retain sourceSize24/targetSize32, source offset[16]/target offsets[16,24], target storage[4,8], source/target attrs1, native sizes-1. baselineReady/targetReady/targetDefinitionReady/physicalProof=true, error0, pending/truncated=false; sourceSizeInited/targetSizeInited=false are preserved. Proof-time baseline/target business/vtable flags are false with cctor0; baseline flags remain false at final read. Both source-bound physical subchecks Passed, followed by main publication/reflection/delegate result41 and 10000 allocations. Their owned identity statuses are Captured; readiness comes from finalized staged definitions. Exact per-process physical values remain in the audit. The control's contaminated unisolated certificate remains Failed. Historical F positive physical subcheck/full-cell Failed and G full-cell Passed remain as originally sealed.

### Custody, publication and exact exit state

[POSTRUN_AUTHENTICATION.json]({rel}/preflight/POSTRUN_AUTHENTICATION.json) authenticates {auth['indexedLiveFiles']} indexed live files and {auth['archiveMembers']} exact safe unique archive members; result/ledger/37 individual cells agree. All {auth['priorCustodyFilesUnchanged']} earlier custody files are unchanged. No reused evidence is promoted to fresh H acceptance. Every important observation is preserved in raw receipts/reports; transient Unity Console is not the sole record.

Live `{R}` and all receipt-referenced project/install/build/app/reference roots remain intact. Immutable [H checkpoint]({rel}/README.md) copies every indexed byte plus top-level result/index/seal and exact ordered archive parts. Original archive size {size} bytes, SHA-256 `{archivehash}`; [ARCHIVE_TRANSPORT.json]({rel}/ARCHIVE_TRANSPORT.json) and [ARCHIVE_RECONSTRUCTION_AUDIT.json]({rel}/ARCHIVE_RECONSTRUCTION_AUDIT.json) authenticate fresh separate reassembly without recompression. [MANIFEST.sha256]({rel}/MANIFEST.sha256) and publication checks bind checkpoint/staged bytes, JSON and local links. Exact captured generated/native whitespace is preserved with narrow raw/snapshot attributes; prior reports change only by prepending H and marking the previous G heading historical.

| Original sealed artifact | SHA-256 |
| --- | --- |
{hashrows}

Only LOCAL_VALIDATION.md, RETURN_TO_WEB.md and the new H checkpoint are Local-owned publication changes; no runtime/source/pin change or local fix. Final pushed demo publication HEAD is distinct from executed source and is recorded after non-force push in `{P}/PUBLICATION_RECEIPT.json` and the final copyable handoff; all four clean canonical remote heads are verified. Native/package/IL2CPP heads remain the executed commits above. Focused outcome EvidenceReadyForPrimaryReview does not satisfy full-stage Human Review Gate requirements. **R03Accepted=false; H2Passed=false; pureInterpreterExpansionEnabled=false; fullLegacyRegressionAcceptance=false.** Exit exactly **Local Validation → Primary Implementation** for source/evidence reconciliation and remaining Primary-owned stage work; do not begin another batch, H2, implementation or qualification autonomously.
'''
ret=f'''## Current return — R03 batch H: focused rejection preservation Passed; no new non-trivial defect

**EvidenceReadyForPrimaryReview; 37 Passed / 0 Failed / 0 Blocked; seal Passed; runner exit0.** Exactly one fresh batch, PID{inv['pid']}, {localtimes} (UTC {inv['startedUtc']}–{inv['endedUtc']}). Four fresh builds, 754 selected actual Editor cases/zero skips and 23 fresh-process Player contracts Passed. All five negative-path rejectionObservation subchecks confirm error 16/state 8 unchanged through -2 capacity failure and two complete native reads; captured identities and repeated layout rows remain complete and equal. Six strict isolated warm witnesses, actual producer-controls aggregate and full C07 Passed. Contaminated natural controls retain Failed unisolated warm certificates. No Local source fix, terminal restoration, retry or expectation/pin/ownership/lease/warm-up/deadline change.

No new non-trivial implementation issue was reproduced, so no new actionable defect entry is added. Fresh H evidence satisfies the focused runtime regression for historical R03-LG-001; its original G Failed/Unavailable evidence and uncertainty remain immutable below. Read [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md), immutable [H checkpoint]({rel}/README.md), [REJECTION_RUNTIME_AUDIT.json]({rel}/preflight/REJECTION_RUNTIME_AUDIT.json), [PRODUCER_RUNTIME_AUDIT.json]({rel}/preflight/PRODUCER_RUNTIME_AUDIT.json) and the original per-case request/raw/verification receipts. Full raw schema3/rejectionProbe schema1 before/after captures and repeated receipt are retained; no failing row identity is inferred.

Primary must reconcile this source-bound focused result with its repair/design record, preserve all historical states, and own remaining full-stage work. M01 remains NoCoverage. Full legacy/resource, broader runtime/generic/interface/delegate/stack-trace, startup/capacity/performance/memory, gated qualification and independent full R03 review remain open; this is not Ready for Human Review Gate. R03Accepted=false; H2Passed=false; PureInterpreter expansion disabled; fullLegacyRegressionAcceptance=false. Exit **Local Validation → Primary Implementation**; no further Local execution or implementation is authorized by this completed batch.
'''
preservation={}
for name,newbody in [('LOCAL_VALIDATION.md',body),('RETURN_TO_WEB.md',ret)]:
 q=D/'Docs/AssemblyShadow/Handoff'/name;old=q.read_bytes();heading,tail=old.decode().split('\n',1);tail=tail.lstrip('\n').replace('## Current','## Historical',1);q.write_text(heading+'\n\n'+newbody+'\n'+tail);preservation[name]={'originalCommit':pins['hybridclr_demo'],'originalSha256':hashlib.sha256(old).hexdigest(),'newSha256':sha(q),'policy':'Prepend H; previous Current G heading becomes Historical; prior report body otherwise unchanged'}
(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps(preservation,indent=2)+'\n')
(C/'README.md').write_text(f'''# Immutable R03 batch H Local evidence checkpoint

**EvidenceReadyForPrimaryReview; 37 cells Passed, seal Passed, runner exit0.** Exactly one invocation PID{inv['pid']}, UTC {inv['startedUtc']}–{inv['endedUtc']}. Four builds/754 Editor cases zero skips/23 fresh Player contracts Passed. Five negative observations preserve error 16 through capacity -2 and two complete bounded reads; six warm witnesses/producer aggregate/full C07 Passed. Contaminated controls retain Failed unisolated warm certificates. M01=NoCoverage; R03Accepted=false; H2Passed=false. No Local fix, retry or acceptance promotion; return to Primary, not full-stage Human Review Gate.

Read [Local report](../../../../Handoff/LOCAL_VALIDATION.md) and [Primary return](../../../../Handoff/RETURN_TO_WEB.md). Later reports may advance; raw H bytes remain immutable. Executed four source commits are recorded in [batch/LOCAL_BATCH_RESULT.json](batch/LOCAL_BATCH_RESULT.json), branch codex/assembly-shadow-r01b-h1, owning paths beneath `{W}`. Unity 2022.3.62f2/StandaloneOSXarm64; SDK8.0.318.

Live root `{R}` and all referenced projects/install roots/apps/reference worktrees remain retained. Every indexed byte and [batch/BATCH_EXECUTION.json](batch/BATCH_EXECUTION.json), [batch/evidence-index.json](batch/evidence-index.json), [batch/seal-receipt.json](batch/seal-receipt.json), [batch/producer-controls.json](batch/producer-controls.json) are preserved. [POSTRUN_AUTHENTICATION.json](preflight/POSTRUN_AUTHENTICATION.json) covers {auth['indexedLiveFiles']} indexed files/{auth['archiveMembers']} safe archive members and {auth['priorCustodyFilesUnchanged']} earlier custody bindings unchanged. [REJECTION_RUNTIME_AUDIT.json](preflight/REJECTION_RUNTIME_AUDIT.json) preserves raw before/after states, byte-count bindings, captured identity rows and repeated probes; [PRODUCER_RUNTIME_AUDIT.json](preflight/PRODUCER_RUNTIME_AUDIT.json) reconciles warm/control evidence; [RETAINED_LIVE_ROOTS.json](preflight/RETAINED_LIVE_ROOTS.json) lists exact retained paths.

[ARCHIVE_TRANSPORT.json](ARCHIVE_TRANSPORT.json) describes exact ordered archive parts. [REASSEMBLE_EVIDENCE.py](REASSEMBLE_EVIDENCE.py) writes only to an absolute unused destination; expect {size} bytes and SHA-256 `{archivehash}`. Independent [ARCHIVE_RECONSTRUCTION_AUDIT.json](ARCHIVE_RECONSTRUCTION_AUDIT.json) authenticates separate reconstruction without changing the live original or seal. [MANIFEST.sha256](MANIFEST.sha256) binds every checkpoint file except itself. [REPORT_HISTORY_PRESERVATION.json](REPORT_HISTORY_PRESERVATION.json) binds prior report bodies. Source snapshots are exact read-only source evidence, not extra runtime execution. Final pushed publication identity is verified externally in `{P}/PUBLICATION_RECEIPT.json` and final handoff to avoid self-referential commit hashing; it is distinct from tested executable source.
''')
shutil.copy2(__file__,C/'preflight/write-success-reports.py');print('Wrote authenticated H success reports and checkpoint README')
