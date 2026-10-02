import datetime,hashlib,json,pathlib,shutil,subprocess
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261002G-producer');R=P.parent/'R03LocalBatch-20261002G-producer';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261002-batch-g-return-required';rel='../History/M07R/R03/'+C.name
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((P/'POSTRUN_AUTHENTICATION.json').read_text());rej=json.loads((P/'REJECTION_OBSERVATION_ANALYSIS.json').read_text())
cmd='/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -B '+str(D)+'/Tools/AssemblyShadow/R03/run_local.py --workspace '+str(W)+' --output '+str(R)+' --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity --demo-commit 78767ea4d7ea064115daffcdbb2ce9435569814c'
pins={'hybridclr_demo':'78767ea4d7ea064115daffcdbb2ce9435569814c','hybridclr':'4b2774b066cfc6afd77a8c8aded6bda7ea574f55','hybridclr_unity':'120bb01be680cec0375002a0823552d66d34b84c','il2cpp_plus':'9ab7a0000f02251e280901c6e23f6a7772344ca6'}
pinrows='\n'.join('| `'+str(W/n)+'` | `'+h+'` |' for n,h in pins.items())
hashes='\n'.join('| `'+n+'` | `'+h+'` |' for n,h in a['topLevelHashes'].items())
failrows='\n'.join('| `'+r['id']+'` | '+str(r['pid'])+' | `'+r['commandId']+'` | `'+r['rawSha256']+'` | `'+r['verificationSha256']+'` |' for r in rej['rows'])
local=f'''## Current run — R03 batch G, 2026-10-02: producer attribution and six warm witnesses pass; five rejection observations fail

**Local Validation → Primary Implementation. Result=ReturnRequired; 37 cells: 32 Passed, 5 Failed, 0 Blocked; sealStatus=Passed; runner exit 1.** Exactly one invocation, runner PID 45229, UTC 2026-10-02T10:38:14.388652+00:00–2026-10-02T10:44:38.180250+00:00 (03:38:14–03:44:38 PDT). Four fresh native build roles and 754 selected EditMode cases with zero skips Passed. All 23 fresh-process Players executed: 14 of the original 19 main cases Passed, five Failed; four added controls diagnostic Passed with four unisolated warm certificates Failed. The producer-controls aggregate Passed with four identified loop admissions. All six strict isolated warm witnesses and the complete C07 positive physical-proof cell Passed. Five expected-negative cases fail because runtime-probe observation throws and replaces their terminal diagnostics. No Local source fix, retry, app reuse, counter relaxation, forced GC, extra warm-up, timeout/lifetime/lease change or acceptance promotion occurred.

### Executed repository authority, pins and environment

Each owning checkout independently matched its absolute top-level path, branch `codex/assembly-shadow-r01b-h1`, clean status, canonical origin `git@github.com:night-outlook/<repository>.git`, exact source HEAD and remote tip. Safe fast-forward synchronization preserved unrelated worktrees. Demo synchronized from F Local publication `7f27633d9fc761faa93733b07e1787831babe73e`. Executable source anchor `53e6e559165344cb98405a7261a988871157a864` is an ancestor and its delta to executed demo is documentation-only. Source/package/native/build/configuration pins and source-manifest hashes were authenticated before execution and again for all four isolated projects.

| Repository path | Exact executed commit |
| --- | --- |
{pinrows}

Fresh clean detached reference worktrees remain beneath `{R}`: native `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, IL2CPP `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`, graph-test package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`. Exact retained paths are in [RETAINED_LIVE_ROOTS.json]({rel}/preflight/RETAINED_LIVE_ROOTS.json). No other checkout, Library, HybridCLRData, Builds, prior batch app or control sibling was used or changed. Four role-specific source/config/install-root/nativeBinding receipts and complete app inventories remain bound to G. Build GUID is explicitly Unavailable where the receipt reports it; no GUID was inferred.

macOS 26.5 arm64; Python 3.14.6; .NET SDK 8.0.318/runtime 8.0.21; PowerShell 7.6.3; Apple clang 21.0.0/macOS SDK 26.5. Exact Unity executable `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, StandaloneOSX/arm64. SDK-only root `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`; Unity APIs/BCL remain pinned to 2022.3.62f2. Pinned mscorlib SHA-256 `d89d5124cafb873b34c2eac68d2ece41d14fec10999baf0e4620276dff54ab83`. Scoped DOTNET_ROOT/DOTNET_ROOT_ARM64, DOTNET_MULTILEVEL_LOOKUP=0, PYTHONDONTWRITEBYTECODE=1 and TMPDIR=/private/tmp are recorded in runner-invocation.json. Gate helper reports Off; no independent full-stage review claimed.

```text
{cmd}
```

### Fresh results and preserved evidence states

| Validation | State | Evidence / scope |
| --- | --- | --- |
| Exact authority, source/pins/configuration and fresh roots | Passed | preflight, source-inputs/config/nativeBinding receipts |
| Host runner regressions, admission and graph checks | Passed | 163 Python cases, 35 admission cases, 9/9 graph cases on each package pin; original cells/commands retained |
| Real DLL inputs and Unity compiler consumers | Passed | 15 DLL fixtures, 33 fixture audits and 33 consumer cases |
| Unity lifecycle probes / complete helper APIs | Passed | valid/invalid Editor probes; package/helper compile with 425 inputs and 115 defines |
| Expected-negative compiler controls | Passed contract / compiler exit 1 | Only commands 0048/0050/0055 exit 1; old C helper reproduces its two CS0266 errors; distinct from product builds |
| Four isolated native/IL2CPP Player builds | Passed | schema-2 receipts bind installation root, source pins and app inventory |
| Selected actual EditMode suite | Passed | 754 cases, zero skips; XML/editor-scope/editor-verification retained |
| Main Player cases | 14 Passed / 5 Failed | all original 19 fresh processes ran; no downstream cell suppressed |
| Six strict warm witnesses | Passed | C03/C04/C05/C07/D02/D03; all exact-loop cold/layout/workspace deltas zero and hits/baseline checks at least 10000 |
| Four unisolated producer controls | Diagnostic Passed / warm certificate Failed | PC-C03/PC-C04/PC-C05/PC-C07; natural contamination observed in each |
| Producer-controls aggregate | Passed | four identified loop admissions; producer-controls.json and source-bound raw/verification receipts |
| Full C07 cell / physical readiness on both paired apps | Passed | positive proof, Commit, reflection/delegate 41, 10000 allocations; details below |
| Five expected-negative observations | Failed | C02/C08/C09/C10/D01; runtimeProbe Unavailable; exact production rejection verifier fails |
| Batch sealing and custody audit | Passed | 1901 indexed files, 1902 safe unique archive members; all 37 cells agree; 6989 earlier custody files unchanged |
| Process lifetime | Passed | all 83 command receipts clean, no timeout/survivor/cleanup error; seven birth-authenticated Unity completion receipts retained |
| Excluded M01 asset test | NoCoverage | unavailable fixture; excluded case is not a skip or pass |
| Full R03 legacy/resource/generalized runtime/performance/memory review and H2 | NotRun in focused G / remains open | focused batch is not full-stage acceptance |

No reused or historical evidence was promoted to fresh G coverage. All 23 Player command exits are 0; verification states above remain authoritative. 80 of 83 commands exit 0; the three named expected-negative compiler exits retain their original code. Raw streams, response files, emitted DLLs, Editor logs/XML, all original verification receipts and pre-cleanup/lifetime evidence are included. Completed prerequisites permitted all Players; the failed observations do not justify rerunning or changing downstream expectations.

### Actual producer and bounded isolation observations

All four natural controls record one admission in the exact phase-2 loop: admissionCacheMisses +1, allocationProofChecks +1, cacheEntries +1, cacheBytes +80; hits/baseline checks +10000. Four cold events identify the same full nested generic type, `System.Runtime.CompilerServices.ConditionalWeakTable<byte[][], object>.Enumerator`, on probe thread 2 rather than loop owner 1, site Object::NewAllocSpecific, generation 1/domain 1/context 0x0. Actual producer context identifies finalizer `mscorlib/System.Gen2GcCallback`, delegate method `Gen2GcCallbackFunc`, token 100672638, closed declaring type `System.Buffers.TlsOverPerCoreLockedStacksArrayPool<byte>` and producerRecognizedArrayPool=true. Exact full type keys, samples, events, native runtime thread identifiers and counters are retained in [PRODUCER_RUNTIME_AUDIT.json]({rel}/preflight/PRODUCER_RUNTIME_AUDIT.json) and each raw.runtimeProbe. This confirms the producer in G; it does not retroactively identify the historical F actor.

| Case | Fresh PID | Native runtime producer thread identifier | Lease elapsed µs / admitted-completed / deferred-drained |
| --- | --- | --- | --- |
| PC-C03 | 50795 | 6163410944 | no lease / 2-2 / 0-0 |
| PC-C04 | 50797 | 6164606976 | no lease / 2-2 / 0-0 |
| PC-C05 | 50799 | 6108393472 | no lease / 2-2 / 0-0 |
| PC-C07 | 50801 | 6129790976 | no lease / 2-2 / 0-0 |
| C03 | retained receipt | process-local owner | 12502 / 2-2 / 1-1 |
| C04 | retained receipt | process-local owner | 12586 / 2-2 / 1-1 |
| C05 | retained receipt | process-local owner | 12760 / 2-2 / 1-1 |
| C07 | retained receipt | process-local owner | 13757 / 2-2 / 1-1 |
| D02 | retained receipt | process-local owner | 249991 / 1-1 / 0-0 |
| D03 | retained receipt | process-local owner | 249522 / 1-1 / 0-0 |

All six main leases use R03ArrayPoolFinalizerFenceV1, leaseMs=5000, acquired/released/drained=true and expired/invalid=false; all main cold events are zero. Four controls have requested/acquired/released/drained=false, leaseMs=0. Ten raw/verifier cases and all 50 native spans reconcile. Distinct PID/run nonce/source/config/fixture hashes bind each pair; no pointer or thread number is treated as a cross-process identity. Isolation is diagnostic-only, may delay queued finalizers, and is not production GC or performance qualification.

Both C07 main and PC-C07 retain sourceSize=24/targetSize=32, source offset [16]/target offsets [16,24], target storage [4,8], baselineReady/targetReady/targetDefinitionReady/physicalProof=true, error=0, pending/truncated=false. sourceSizeInited/targetSizeInited=false are preserved: readiness comes from finalized staged definition. Proof-time business/vtable flags are false and cctor states 0; baseline flags remain false at final read. Main baseline/target pointers `0x11fe15cd0`/`0x11fe15fa0`; PC baseline/target `0x11f195c20`/`0x11f195ef0`; both node keys `type(11:r03contract/3:R03/4:Node@0)`. Main C07 full cell Passed; PC diagnostic Passed with unisolatedWarmCertificate=Failed. Historical F's physical-proof Passed/full-cell Failed remains unchanged.

### New non-trivial issue and preserved uncertainty

R03-LG-001: five expected-negative cases return Validate code 16/state 8 while unpublished, then probe read returns -3 with `RuntimeProbeFailure: System.InvalidOperationException: Runtime probe receipt failed: -3`. Subsequent terminal diagnostics/recovery show code 15, `ShadowAllocationDuringMetadataResolution Object::NewAllocSpecific`, RestartRequired. runtimeProbe is empty/Unavailable in these cases. The strict verifier reports `Exact production rejection code` and Failed. See [RETURN_TO_WEB.md](RETURN_TO_WEB.md) for the actionable source chain and limits and [REJECTION_OBSERVATION_ANALYSIS.json]({rel}/preflight/REJECTION_OBSERVATION_ANALYSIS.json) for exact source/raw/command/verification bindings. Likely new full type-key rendering re-enters private metadata after validation scope ends and managed exception allocation changes terminal state; exact first failing layout row and inner native exception stack remain Unavailable. No Local source change was authorized or made.

### Immutable checkpoint and exit

Live root `{R}` is retained intact with all referenced build/project/reference/app roots. Immutable [G checkpoint]({rel}/README.md) contains all indexed bytes plus batch result/index/seal and exact three-part archive transport. Archive size 163817752 bytes; reassembly uses a new destination and authenticates the original whole hash. [MANIFEST.sha256]({rel}/MANIFEST.sha256), [ARCHIVE_TRANSPORT.json]({rel}/ARCHIVE_TRANSPORT.json) and [ARCHIVE_RECONSTRUCTION_AUDIT.json]({rel}/ARCHIVE_RECONSTRUCTION_AUDIT.json) cover transport; publication checks authenticate every staged byte and local link. Captured generated/native whitespace is preserved byte-for-byte, with attributes restricted to raw batch files and authenticated source snapshots. No acceptance flags or earlier receipts were rewritten.

| Original artifact | SHA-256 |
| --- | --- |
{hashes}

Publication owns only this report, RETURN_TO_WEB.md and the new G checkpoint. The final demo publication HEAD is distinct from executed source and is recorded after non-force push in `{P}/PUBLICATION_RECEIPT.json` and the final handoff, with all four clean canonical remote heads verified. Native/package/IL2CPP publication heads remain the executed commits above. The publication commit does not claim fresh executable validation. R03Accepted=false; H2Passed=false; PureInterpreter expansion disabled; full legacy acceptance false. Exit exactly **Local Validation → Primary Implementation** to repair LG-001; no next milestone or further Local batch begins.
'''
ret=f'''## Current return — R03 batch G: rejected-stage type-key observation replaces terminal diagnostics

**ReturnRequired: 37 cells, 32 Passed / 5 Failed / 0 Blocked; seal Passed; runner exit 1.** Four fresh builds, 754 selected actual EditMode cases with zero skips, six strict warm witnesses, producer-controls aggregate and complete C07 cell Passed. All 23 fresh Player processes ran. Four controls confirmed the actual ArrayPool Gen2 finalizer/delegate producer; their diagnostic results Passed and all unisolated warm certificates remain Failed. Five expected-negative cells fail during probe observation. Read [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md) for authority, environment, states and hashes; [G checkpoint]({rel}/README.md) for preserved bytes. No Local source fix or retry. R03Accepted=false; H2Passed=false; M01 NoCoverage; PureInterpreter expansion disabled. Return to Primary.

### R03-LG-001 — full type-key observation of rejected staged classes allocates and changes the original failure

**Symptom and exact reproduction already performed.** Execute the prescribed single runner at the four source commits recorded in LOCAL_VALIDATION.md, branch codex/assembly-shadow-r01b-h1, Unity 2022.3.62f2 and SDK 8.0.318. Actual interval UTC 2026-10-02T10:38:14.388652+00:00–2026-10-02T10:44:38.180250+00:00, runner PID 45229:

```text
{cmd}
```

Do not retry G or relaunch its apps. In C02-private-reference, C08-interface-change, C09-reference-to-value-kind, C10-field-removal and D01-private-reference: Configure/Begin/Reserve/Stage succeed; Validate returns code 16/state 8, phase Validate, published=false. In managed finally, R03_ReadRuntimeProbe returns -3. The raw receipt records:

```text
RuntimeProbeFailure: System.InvalidOperationException: Runtime probe receipt failed: -3
at AssemblyShadow.R03.Player.R03Player.Start ()
lastError=15
terminalFailureCode=15
ShadowAllocationDuringMetadataResolution Object::NewAllocSpecific
state=Failed; disposition=RestartRequired; abortAllowed=false; published=false
verification.error=Exact production rejection code; verification.result=Failed
```

runtimeProbe is empty/Unavailable. Original steps retain code 16, but later diagnostics/recovery contain 15. No Commit, business work or warm witness occurred in these five cases. All five Player command exits are 0, which is not verifier success. C06 true-cycle fails before retained layouts and Passed its expected-negative contract; reference/off cases are unaffected. These five cases were Passed in F; F evidence is not rewritten.

**Exact evidence.** Live `{R}/players/<case>/raw.json`, request.json, verification.json and Player logs; corresponding `{R}/commands/<command-id>/` receipts/streams. Exact immutable copies are [batch/players]({rel}/batch/players) and [batch/commands]({rel}/batch/commands). [REJECTION_OBSERVATION_ANALYSIS.json]({rel}/preflight/REJECTION_OBSERVATION_ANALYSIS.json) contains complete run nonces, source bindings, build-receipt/request/log hashes, steps and excerpts. The source-bound Failed verification receipts agree with cell and ledger status.

| Case | PID | Command | raw.json SHA-256 | verification.json SHA-256 |
| --- | --- | --- | --- | --- |
{failrows}

**Most likely root cause and why observation permits the mutation.** Read-only source tracing is retained in [diagnostic-source-snapshot]({rel}/preflight/diagnostic-source-snapshot) and [probe-format-f-to-g.diff]({rel}/preflight/probe-format-f-to-g.diff). New G `PlayerProject/AssemblyShadowR03Probe.cpp` ProbeType (lines 193–194) calls `AssemblyShadowTypeKey::Format(&klass->byval_arg)` for every retained baseline/target layout. Serialization occurs after Validate returns and its private owner/resolver scope ends for rejected unpublished layouts. Format enters AssemblyShadowTypeMetadataScope (AssemblyShadowTypeKey.cpp 218–221); FormatType/RawDefinition resolve class/valuetype via MetadataCache::GetTypeInfoFromHandle (1190) → GlobalMetadata::GetTypeInfoFromHandle (792) → interpreter MetadataModule image/token decode. MetadataModule.h private-image lookup precedes published lookup; InterpreterMetadataIndexRuntime.cpp CurrentOwner (161–174) depends on construction/private/public owner context; Decode (196–205) rejects an absent owner. MetadataUtil.cpp codec error helpers (19–48) raise a managed ExecutionEngineException. Inside Format's metadata scope, managed exception allocation enters ResolveAllocation (AssemblyShadowTypeResolver.cpp 884–892) and trips the physical-metadata allocation guard, recording code 15. Probe catch-all returns -3 and discards partial JSON; R03Player.cs finally (166–184) reads terminal diagnostics after probe retrieval. Thus diagnostic collection can overwrite the authoritative validation failure it is intended to report.

Runtime proves the original code16 → failed probe → code15 sequence in five fresh processes; the private-owner/codec path is the most likely static explanation. The exact first failing layout row and inner native stack are Unavailable, so an OwnerRequired return is not claimed as directly observed. This is not evidence that retained memory was freed. The source snapshot and diff are historical read-only source evidence, not extra runtime coverage.

**Impact boundary.** Rejected unpublished staged layouts, full nested/generic type-key formatting, metadata ownership/lifetime and native probe receipt generation; five negative acceptance cells lose both a usable probe and original terminal diagnostics. Positive warm/counter checks and all four controls passed unchanged. Cross-module ownership and formatting semantics make this a non-trivial Primary issue, beyond a bounded Local patch.

**Concrete implementation direction.** Capture immutable full type keys/layout identity while valid owner context exists, or implement genuinely metadata-only formatting over authenticated owned physical metadata. Preserve nested/generic identity and explicit unavailable/error states. Diagnostic retrieval must not resolve/lazily initialize classes, publish staged metadata or allocate a managed exception; it must preserve original error16/recovery. Keep private visibility and allocation guards intact. Do not accept error15, ignore a probe exception, loosen exact rejection verification, extend a lease or broaden Local implementation. Record original diagnostics before and after native receipt retrieval in a focused rejected-layout regression to prove observation is non-mutating. Instrument the formatter/codec path if needed to establish the first failing row without changing semantics.

**Validation after the fix.** Primary host/native negative-path regressions plus a newly authorized fresh pinned Local batch. Require all five exact-negative cells retain original error16 and safe bounded probe evidence, all 37 cells, four fresh builds, 754 selected cases/zero skips and 23 fresh Players. Preserve all six strict warm witnesses, positive C07 proof, actual producer attribution and four control certificates' Failed state when contaminated. No reinterpretation of G/F or production GC acceptance. Wider R03 legacy/resource/generic/delegate/interface/stack/performance/memory and independent review/H2 remain open.
'''
preserve={}
for name,body in [('LOCAL_VALIDATION.md',local),('RETURN_TO_WEB.md',ret)]:
 q=D/'Docs/AssemblyShadow/Handoff'/name;old=q.read_bytes();heading,tail=old.decode().split('\n',1);tail=tail.lstrip('\n').replace('## Current','## Historical',1);q.write_text(heading+'\n\n'+body+'\n'+tail)
 preserve[name]={'originalCommit':pins['hybridclr_demo'],'originalSha256':hashlib.sha256(old).hexdigest(),'newSha256':sha(q),'policy':'Prepend G; only previous Current F heading becomes Historical; previous report body otherwise unchanged'}
(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps(preserve,indent=2)+'\n')
(C/'README.md').write_text(f'''# Immutable R03 batch G Local evidence checkpoint

Result **ReturnRequired**, 37 cells: **32 Passed / 5 Failed**, seal **Passed**. Exactly one fresh batch, UTC 2026-10-02T10:38:14.388652+00:00–2026-10-02T10:44:38.180250+00:00, runner PID45229. Four builds, 754 selected EditMode cases/zero skips, six strict warm witnesses, actual producer aggregate and full C07 Passed. Five expected-negative cases fail when probe observation changes terminal error16 to15. Four controls diagnostic Passed with contaminated unisolated warm certificates Failed. R03Accepted=false; H2Passed=false; excluded M01 NoCoverage. No source fix, retry or acceptance promotion.

Read the current [Local report](../../../../Handoff/LOCAL_VALIDATION.md) and [Primary return](../../../../Handoff/RETURN_TO_WEB.md). This directory preserves the immutable G evidence; later reports may advance, these raw receipts may not.

Executed demo `78767ea4d7ea064115daffcdbb2ce9435569814c`, native `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package `120bb01be680cec0375002a0823552d66d34b84c`, IL2CPP `9ab7a0000f02251e280901c6e23f6a7772344ca6`. All owning repositories beneath `{W}`, branch codex/assembly-shadow-r01b-h1. Unity2022.3.62f2/StandaloneOSXarm64; SDK8.0.318.

Original live root `{R}` and all receipt-referenced roots remain retained. [batch/LOCAL_BATCH_RESULT.json](batch/LOCAL_BATCH_RESULT.json), [batch/BATCH_EXECUTION.json](batch/BATCH_EXECUTION.json), [batch/evidence-index.json](batch/evidence-index.json), [batch/seal-receipt.json](batch/seal-receipt.json), all indexed command/host/fixture/compiler/build/Editor/Player bytes are copied exactly. [producer-controls.json](batch/producer-controls.json) preserves aggregate state. Authentication: [POSTRUN_AUTHENTICATION.json](preflight/POSTRUN_AUTHENTICATION.json), [PRODUCER_RUNTIME_AUDIT.json](preflight/PRODUCER_RUNTIME_AUDIT.json), [REJECTION_OBSERVATION_ANALYSIS.json](preflight/REJECTION_OBSERVATION_ANALYSIS.json), [RETAINED_LIVE_ROOTS.json](preflight/RETAINED_LIVE_ROOTS.json); prior6989 custody files unchanged.

[ARCHIVE_TRANSPORT.json](ARCHIVE_TRANSPORT.json) describes three exact archive parts. Use [REASSEMBLE_EVIDENCE.py](REASSEMBLE_EVIDENCE.py) with an absolute unused destination; reconstructed archive must be 163817752 bytes with SHA-256 `2a3e90a49eb9b13d035a3749b8012f1e96d4410343d76b7f11a00617d17aaf23`. [ARCHIVE_RECONSTRUCTION_AUDIT.json](ARCHIVE_RECONSTRUCTION_AUDIT.json) authenticates a separate fresh reconstruction. [MANIFEST.sha256](MANIFEST.sha256) binds all checkpoint bytes except itself; [REPORT_HISTORY_PRESERVATION.json](REPORT_HISTORY_PRESERVATION.json) binds prior report bodies. Source snapshots retain exact executed bytes, do not constitute additional tests. Publication commit is distinct from executed source; final pushed HEAD is verified in external `{P}/PUBLICATION_RECEIPT.json` and final handoff to avoid a self-referential commit hash.
''')
shutil.copy2(__file__,C/'preflight/write-reports.py')
print('Wrote only owned reports and checkpoint documentation')
