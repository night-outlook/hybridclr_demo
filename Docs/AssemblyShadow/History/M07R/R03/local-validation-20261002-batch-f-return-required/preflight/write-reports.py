import datetime,hashlib,json,pathlib,subprocess
D=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');P=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261002F-runtime');R=P.parent/'R03LocalBatch-20261002F-runtime';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261002-batch-f-return-required'
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result=load(R/'LOCAL_BATCH_RESULT.json');audit=load(P/'POSTRUN_AUTHENTICATION.json');obs=load(P/'INTEGRATED_OBSERVATIONS.json');diagnosis=load(P/'DIAGNOSTIC_FINDINGS.json');physical=load(P/'PHYSICAL_PROOF_AUDIT.json');invocation=load(P/'runner-exit.json')
assert result['result']=='ReturnRequired' and result['sealStatus']=='Passed' and audit['counts']=={'Passed':32,'Failed':4}
repoTable='\n'.join('| `'+r['path']+'` | `'+r['commit']+'` |' for r in audit['repositories'])
cmd=' '.join(invocation['command']);hashTable='\n'.join('| '+n+' | `'+h+'` |' for n,h in audit['topLevelHashes'].items())
failed=[p for p in obs['players'] if p['state']=='Failed'];rows='\n'.join('| '+p['id']+' | '+str(p['pid'])+' | `'+p['rawSha256']+'` | `'+p['verificationSha256']+'` |' for p in failed)
physicalKeys='\n'.join('| '+r['case']+' | `'+r['runtimeProbe']['events'][0]['type']['physical']+'` | '+str(r['value'])+' | '+str(r['state'])+' |' for r in diagnosis['runtime'] if r['cellState']=='Failed')
local=f'''## Current run — R03 batch F, 2026-10-02: attribution and positive staged proof observed; four exact-loop cells fail

**Local Validation → Primary Implementation. Result=ReturnRequired; 36 cells: 32 Passed, 4 Failed, 0 Blocked; sealStatus=Passed; runner exit 1.** Exactly one invocation, 2026-10-02 01:26:18–01:32:39 PDT (UTC {invocation['startedUtc']}–{invocation['endedUtc']}), runner PID {invocation['pid']}. All four fresh native build roles and all 754 selected Editor cases passed. All 19 fresh-process Players ran: 15 Passed, 4 Failed. Six warm witnesses produced complete native probes; both Debug witnesses Passed, four Release witnesses Failed. No Local source fix, retry, pin/scope/expectation/warm-up/deadline/lifetime change or acceptance promotion occurred.

### Executed authority, environment and operations

Each owning checkout independently matched its exact absolute top-level path, branch, clean status, canonical origin and remote tip before and after execution. All branches are `codex/assembly-shadow-r01b-h1`; origins are `git@github.com:night-outlook/<repository>.git`. Demo safely fast-forwarded from published E return `b97375d4b12357d0f987cf7738eaa422d4615081`. Tested executable source anchor `67e8c1df18f84dda4ec70edd45b1ed717bcea4e8` is an ancestor; its delta to the executed demo is documentation-only. The latest WEB_TO_LOCAL.md-touching commit matched prompt/local/remote HEAD. Pre-existing state was classified before synchronization and all checkouts remained clean throughout execution; unrelated worktrees were preserved.

| Repository path | Exact executed commit |
| --- | --- |
{repoTable}

Fresh detached, clean reference worktrees are retained under `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261002F-runtime/reference-worktrees/`: HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, IL2CPP `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`, graph-test package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`. The native reference build uses its frozen core with the current package/harness. Four role source manifests, configs, isolated package references and installed pins bind exact cores, package, executed demo and fixture DLL inventories. Historical owning-project H1 pin files remain unchanged; the owning Unity project was not built. No primary-checkout or previous batch Library/HybridCLRData/Builds/app was used.

Environment: macOS 26.5 arm64, Python 3.14.6, .NET SDK 8.0.318/runtime 8.0.21, PowerShell 7.6.3, Apple clang 21.0.0 and macOS SDK 26.5. Actual Unity is `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`; target StandaloneOSX/arm64. The .NET SDK at `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk` supplies managed compilation only; Unity 6000 Editor was not launched. Exact tool/version, Git/worktree/submodule, source/package/config hashes, retained process observations and scoped environment are in checkpoint `preflight/`.

Command from the owning candidate demo:

```text
{cmd}
```

`preflight/runner-exit.json` binds absolute cwd, start/end, PID, environment, exit and batchInvocations=1. All 79 command receipts retain per-operation times/argv/PID/process group and stream paths/hashes. Outer Unity PIDs identify supervisors; direct Player PIDs bind exact requests/run IDs/raw evidence. Schema-2 build receipts bind installedNativeRoot/nativeBinding and complete native/managed/app inventories. Explicit Unity build GUID is Unavailable in these receipts; no GUID is inferred. Four distinct fresh role roots, source/config hashes, complete app inventories and 19 direct launch/run-ID bindings provide the recorded provenance.

### Fresh validation and evidence states

| Validation | State | Evidence and boundary |
| --- | --- | --- |
| Entry/final source authority and reference worktrees | Passed | Exact clean four-repository source tuple, origins/remotes and detached references. |
| Verifier/input/API/lifetime/provenance/scope/probe contracts | Passed | 144 Python tests, command 0001; these do not substitute for real runtime coverage. |
| Managed graph suites and admission | Passed | Reference 9/9, candidate 9/9, admission 35/35. |
| Player fixtures / compiler input prerequisites | Passed | 15 DLLs, 33 metadata audits, 33 actual pinned Unity compiler consumers, invalid-key negative control and valid/invalid actual Editor probes. |
| Complete helper/package API prerequisite | Passed | Real Runtime/CodeGen/Editor assemblies and helper, 425 input bindings/115 defines, commands 0051–0055. Old C helper negative control has exactly two CS0266 errors and no DLL. |
| Four preparations and fresh native build cells | Passed | Candidate Release, reference Release, candidate Debug, feature-OFF; real installation/generation/IL2CPP/C++/link. All app inventories/ARM64/source/native bindings authenticated. |
| Actual selected EditMode execution | Passed | Command 0060, exact 754 catalog identities, all Passed, zero skips/failures/inconclusive; all 35 mandatory R03 IDs and cycle case present. |
| Excluded frozen M01 resource asset test | NoCoverage | Exact identity/missing assets/reason in editor-scope.json and editor-verification.json; fullLegacyRegressionAcceptance=false. |
| Fresh-process Players | 15 Passed / 4 Failed | All 19 unique PID/run-ID requests ran once; each has source-bound Passed/Failed verification.json, original raw and cell state. |
| Six warm probes: shape/boundary/cold-event reconciliation | Passed observation audit | Six complete probes, labels 0/10/1/2/11/3, no overflow/saturation/dropped threads; all 30 native spans reconcile. This does not waive exact-loop failures. |
| Required warm certificates | 2 Passed / 4 Failed | Debug D02/D03 Passed; Release C03/C04/C05/C07 Failed for admissionCacheMisses during labels 1→2. |
| C07 positive physical-layout subcheck | Passed subcheck; full cell Failed | Original raw.runtimeProbe passes the unchanged verify_primitive_layout function in a separate read-only audit. No Player rerun. |
| Focused seal / separate custody authentication | Passed | 1,871 indexed files, 1,872 exact archive members, 36 cell/ledger matches, 5,027 earlier custody bindings unchanged. |

All 79 outer command groups completed without survivor, timeout or cleanup error. Only 0048 (invalid compiler consumer), 0050 (invalid actual Editor probe), and 0055 (preserved C helper) retain expected exit 1; other 76 exits are 0. These negative controls are distinct from product build results. Seven birth-authenticated Unity completions preserved inner exits and clean owned compiler retirement. Exit 0 from each Player records its observation; it does not promote the four semantic failures.

### Exact-loop attribution and remaining failure

All four Release cells fail the unchanged `Repeated exact-loop proof work: admissionCacheMisses`. Each publishes, invokes reflection/delegate business work and executes 10,000 allocations. All six probes have ownerThread=1. Every Release extra entry is attributed to probe thread=2, site=`Object::NewAllocSpecific`, generation=1, domain=1, context=`0x0`, logical type assembly=`mscorlib`, namespace=`""`, name=`Enumerator`. These are process-local probe identities, not OS thread IDs. Full physical keys and results are:

| Failed cell | Cold physical key | Reflection/delegate value | Final state |
| --- | --- | --- | --- |
{physicalKeys}

Only exact-loop span label 1→2 contains events: admissionCacheMisses +1, admissionProofAttempts +1, admissionEntries +1, admissionRetainedBytes +80, all phase 2 with the same complete key/site/thread. Hits and mandatory baseline checks each increase 10,000; genericContextChecks increases 5; field/interface workspace and layoutCheckCalls do not increase. All other native spans have no counter/event delta. Debug D02/D03 has the same required 10,000 hits/checks with zero cold events. F therefore establishes a different-thread BCL cold admission *inside* the exact loop, not in an observer-return span. The recorded cold key differs from each measured Node key. This does not establish which managed caller/subsystem or generic declaring owner allocated Enumerator, nor why Release and Debug scheduling differs.

Source confirms global counters sum all thread slots and active probe Count accepts every thread. Mark authenticates its owner and phase boundary but does not constrain concurrent allocations. The unchanged verifier applies zero cold work to all-thread counters over labels 1→2. Thus unrelated observed BCL work invalidates this all-thread witness even while target hit/check deltas are present. No repeated target proof is evidenced by the retained cold events, but that cannot promote an all-thread Failed certificate. R03-LF-001 in RETURN_TO_WEB.md records this implementation/measurement-contract boundary and remaining actor uncertainty. E's class/site/thread/timing remains historically unknown; F identities are not assigned retroactively to E.

### C07 staged physical readiness and business observations

The unique R03Contract/R03.Node layout row binds baseline physical `0x120755b00` and target `0x120755dd0`: baselineReady=true, targetReady=true, targetDefinitionReady=true, physicalProof=true, error=0, truncated=false. Source/target pending flags are false. Both business initialized/vtable flags are false and cctor counts are zero at prepublication proof; baseline remains uninitialized/no vtable/cctor=0 at final read. sourceSizeInited=false/targetSizeInited=false are preserved, not rewritten; the finalized staged-layout readiness predicates and positive proof are the observed authority.

Source size 24, target size 32; native sizes -1/-1. One retained field offset 16/attribute 1 is unchanged. Target has offsets [16,24], attributes [1,1], storage [4,8]; the private Int64 occupies proved tail storage 24–32. The additional `<Module>` row is retained separately and is not the required Node witness. Original C07 completes successful publication/state 6, reflection/delegate 41 and 10,000 allocations. `preflight/PHYSICAL_PROOF_AUDIT.json` records the strict unchanged primitive-layout verifier Passed independently because the full runner throws first on warm work. R03-LE-002's physical-readiness symptom is repaired in this F scope; C07's full cell remains Failed under R03-LF-001. E's original rejection/result is unchanged.

C03/C04 raw MethodInfo identity/moved-slot and active/baseline guard observations remain sealed; C04 final state 9 follows the expected old-AOT guard. Those successful partial observations do not change Failed cells. The 15 Passed Players are C01/C02/C06/C08/C09/C10, R01–R05, D01–D03 and O01. They cover original reference late-layout/slot behavior, target-cycle and conservative rejection controls, Debug remapping/guard and feature-OFF baseline in the prescribed scope.

### Evidence custody, publication and exit

Immutable [batch-F checkpoint](../History/M07R/R03/local-validation-20261002-batch-f-return-required/README.md) contains all 1,871 indexed files individually, four complete apps, command streams, original result/ledger/index/seal, compiler/fixture/lifecycle/API evidence, exact Editor XML/scope/verdict, all 19 Player requests/raw/logs and Passed/Failed verification receipts, raw.runtimeProbe samples/events/layouts, source snapshots and separate read-only audits. Live root `{R}` and preflight `{P}` remain intact. RETAINED_LIVE_ROOTS.json inventories six isolated projects, three reference worktrees and excluded caches/native/generated/intermediate files. No previous raw/sealed bytes were modified.

| Original artifact | SHA-256 |
| --- | --- |
{hashTable}

Original live archive is 163,690,329 bytes. Three ordered exact byte parts in ARCHIVE_TRANSPORT.json reconstruct the unchanged archive; independent reconstruction verifies part/whole hashes at a new external path. This representation is separate from the focused seal: no recompression, member omission or raw rewrite. MANIFEST.sha256 binds checkpoint publication bytes. All prior A–E checkpoint/live custody and R02 I bindings are unchanged.

Only these two Local reports and the new F checkpoint change; no bounded source fix. Full R03 legacy/resource, broader generic/delegate/interface/stack-trace, startup/capacity/performance/memory, PureInterpreter qualification and independent full-stage review are NotRun in this focused batch. Gate-review mode is Off; no independent stage acceptance is claimed. R03Accepted=false; H2Passed=false; pureInterpreterExpansionEnabled=false; fullLegacyRegressionAcceptance=false. **Exit: Local Validation → Primary Implementation; stop.** Final clean latest pushed heads/remote verification belong to the outgoing prompt and external PUBLICATION_RECEIPT.json. The later documentation/evidence publication commit does not replace executed-source provenance. Future execution requires a new exact pushed Primary handoff and unused root.
'''
returned=f'''## Current return — R03 batch F: attributed concurrent cold admission blocks four Release witnesses

**ReturnRequired: 32 Passed, 4 Failed, 0 Blocked; focused seal Passed; runner exit 1.** Exactly one batch, 2026-10-02 01:26:18–01:32:39 PDT. Four fresh native build cells and all 754 selected Editor cases passed. All 19 fresh-process Players executed: 15 Passed, 4 Failed. Both Debug warm witnesses Passed; all four Release warm witnesses Failed. No Local source change or retry. Read [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md) for exact paths/branches/commits/tooling/operations and the immutable [F checkpoint](../History/M07R/R03/local-validation-20261002-batch-f-return-required/README.md). Frozen M01 coverage remains NoCoverage.

### R03-LF-001 — another probe thread admits a cold mscorlib Enumerator inside the exact Release loop

**Symptom and exact reproduction performed.** From `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`, with .NET SDK 8.0.318 and Unity 2022.3.62f2, execute the prescribed runner once at demo `8f86dda1aa0582a5b2d55aa650ea321f710cb49a`, native `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package `120bb01be680cec0375002a0823552d66d34b84c`, IL2CPP `aae0ebb55b8761a7a905b410349d006d76fa748b`; all exact candidate paths and branch `codex/assembly-shadow-r01b-h1` are in LOCAL_VALIDATION.md.

```text
{cmd}
```

Do not repeat F or relaunch its apps. Candidate Release C03-moved-slot/C04-old-AOT-guard/C05-direction-reversal/C07-private-primitive-append completes publication/business work and 10,000 allocations, then fails `Repeated exact-loop proof work: admissionCacheMisses`. All four have source-bound Failed verification.json matching their Failed cells. Debug D02/D03 passes with zero cold events.

**Evidence and relevant excerpts.** Live root `{R}`; commands 0063/0064/0065/0067 and their direct Player requests/logs/raw/cells are sealed and committed. Exact raw and verification hashes:

| Failed case | Direct PID | raw.json SHA-256 | verification.json SHA-256 |
| --- | --- | --- | --- |
{rows}

Each original `raw.json.runtimeProbe` has six sample labels [0,10,1,2,11,3], ownerThread=1, complete/unsaturated counter coverage, no dropped threads/overflow. Exactly four cold events fall between labels 1 and 2, phase=2, thread=2, generation=1, domain=1, context=`0x0`, site=`Object::NewAllocSpecific`, assembly=`mscorlib`, namespace=`""`, name=`Enumerator`. All four events use the same process-local physical key (listed in LOCAL_VALIDATION.md). Excerpt: `{{"metric":"admissionCacheMisses","amount":1,"phase":2,"thread":2,"generation":1,"domain":1,"context":"0x0","site":"Object::NewAllocSpecific"}}`; subsequent events are proofAttempts +1, entries +1, retainedBytes +80. Exact-loop hits/baselineChecks each +10,000; genericContextChecks +5; zero new field/interface/layout work. All other spans have no deltas/events. Independent cold-event reconciliation Passed for all 30 spans; the original all-thread zero-cold-work assertion remains Failed.

Checkpoint `preflight/DIAGNOSTIC_FINDINGS.json`, `COLD_ATTRIBUTION_AUDIT.json`, `INTEGRATED_OBSERVATIONS.json` and source snapshots bind all event/type/sample rows, target keys, run IDs/PIDs, original deltas/errors and code. These are read-only audits of existing observations; no new Player was launched. The type/thread IDs are not OS thread IDs or stable identities across processes/batches.

**Direct cause, likely root boundary and why the design permits it.** The failing delta is positively attributed to a non-target BCL physical type on a different native probe thread during the exact warm loop. `Object.cpp:310` routes allocation through ResolveAllocationClass at Object::NewAllocSpecific. `AssemblyShadowTypeResolver.cpp:884–922` applies admission caching to post-publication allocation classes and creates SiteScope. `AssemblyShadowAllocationProof.h:119/132/165–166` emits the miss/proof/entry/bytes events. `AssemblyShadowRuntimeProbe.h:81–84` creates process-local thread IDs; Snapshot sums ObservationCounters; Count at lines 137–150 records all active threads under the boundary lock. `AssemblyShadowObservationCounters.h:129–147` sums every claimed thread slot. Mark authenticates the owner and phase but does not stop another thread allocating in phase 2. `runtime_contract.py:85–91` requires zero cold work from those all-thread counters inside labels 1→2. Thus an unrelated cold admission on thread 2 causes the observed failure. Temporal attribution is now established; the prior broad observer-return hypothesis does not explain these F events.

**Impact and concrete Primary direction.** Release warm acceptance for slot movement, old-AOT guard, reversed graph and primitive append remains blocked. Target hits/checks and positive physical proof are retained separately. Primary should trace the managed caller/declaring generic owner or known concurrent subsystem associated with this full key/site on the non-owner thread, then reconcile the deliberately all-thread exact-loop contract with the real concurrent workload. Prefer a documented, source-reviewed isolation/control of the diagnosed producer if the all-thread contract is retained; otherwise any refined measurement semantics requires explicit design/expectation review and a new authoritative handoff. Preserve complete broad attribution, zero repeated target proof/layout/interface/field work, per-allocation baseline/poison guards and counter/event reconciliation. Do not simply ignore non-owner events, tolerate +1, increase warm-up, initialize baseline business state, change C07 into a rejection or relabel F. This is a cross-native/harness/contract issue with an unresolved producer; no local implementation is authorized.

**Remaining uncertainty and validation after repair.** The retained trace gives native key/site/probe-thread/phase and simple logical type identity, but not the managed stack, nested generic declaring owner, OS-thread mapping or exact engine subsystem. Release/Debug scheduling difference is not explained. No business-target cold proof event is retained, but that alone cannot establish a valid all-thread warm certificate. E's exact actor/timing remains unknown; F must not rewrite it. After Primary repair, issue a new exact pushed handoff and unused root. Re-execute all 36 cells/four fresh builds/754 exact Editor identities/19 fresh Players; all six warm witnesses must satisfy the explicitly reviewed contract and show complete raw reconciled evidence. Retain real MethodInfo/old-AOT guard/graph controls and C07 positive prepublication physical proof without old business initialization.

### Physical-readiness repair observed; original full C07 cell remains Failed

R03-LE-002's native readiness symptom is repaired in F's scope: C07 publishes, returns reflection/delegate 41/state 6 and runs the warm loop. Its unique R03Contract/R03.Node row proves both baselineReady and targetReady plus targetDefinitionReady/physicalProof=true/error0/truncated=false. Baseline/target are separate physical classes; source24/target32, retained offset16 unchanged, private 8-byte field appended at offset24. Baseline and target initialized/vtable/cctor flags remain false/false/0 at proof; baseline remains uninitialized at final read. Source/target size_inited flags are retained false, distinct from the finalized staged-layout readiness authority. The strict unchanged layout subcheck Passed independently in `preflight/PHYSICAL_PROOF_AUDIT.json`; overall C07 remains Failed under R03-LF-001. This positive observation does not rewrite E's original rejection or issue evidence.

### Custody and stop

Read-only audit authenticated all 1,871 indexed files/1,872 exact archive members, all 36 cell/ledger identities, 79 clean command streams/seven supervised Unity completions, all 19 Passed/Failed verifier receipts and 5,027 unchanged prior custody bindings. Original 163,690,329-byte archive SHA-256 `{audit['topLevelHashes']['evidence.tar.gz']}` is retained live and in three exact transport parts; reconstruction does not rewrite the seal. All four complete fresh apps and retained live roots/source snapshots remain bound. Named expected-negative controls remain distinct from successful builds.

R03Accepted=false; H2Passed=false; PureInterpreter expansion disabled; fullLegacyRegressionAcceptance=false. Full-stage resource/legacy/performance/memory/generalized coverage and independent review remain uncompleted. **Local Validation → Primary Implementation; stop.** No further Local execution until a new exact pushed Primary handoff.
'''
checkpoint=f'''# R03 Local batch F — immutable ReturnRequired checkpoint

**32 Passed / 4 Failed / 0 Blocked; focused seal Passed; one invocation, exit 1.** 2026-10-02 01:26:18–01:32:39 PDT; UTC {invocation['startedUtc']}–{invocation['endedUtc']}. Executed demo `8f86dda1aa0582a5b2d55aa650ea321f710cb49a`; tested source anchor `67e8c1df18f84dda4ec70edd45b1ed717bcea4e8`. Later publication HEAD does not replace executed-source provenance.

Read [LOCAL_VALIDATION.md](../../../../Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB.md](../../../../Handoff/RETURN_TO_WEB.md). R03Accepted=false; H2Passed=false; PureInterpreter expansion disabled; fullLegacyRegressionAcceptance=false. Exit: Local Validation → Primary Implementation; stop.

- [LOCAL_BATCH_RESULT.json](batch/LOCAL_BATCH_RESULT.json), [BATCH_EXECUTION.json](batch/BATCH_EXECUTION.json), all 36 cells, [evidence-index.json](batch/evidence-index.json), [seal-receipt.json](batch/seal-receipt.json) preserve original bytes/states. All 1,871 indexed files are committed individually; all 1,872 archive members authenticated independently.
- [ARCHIVE_TRANSPORT.json](ARCHIVE_TRANSPORT.json) binds three ordered exact byte parts of the unchanged 163,690,329-byte sealed archive, SHA-256 `{audit['topLevelHashes']['evidence.tar.gz']}`. Original archive remains live; [REASSEMBLE_EVIDENCE.py](REASSEMBLE_EVIDENCE.py) verifies/reconstructs only at a new caller-specified absolute path. No recompression or omitted members. [ARCHIVE_RECONSTRUCTION_AUDIT.json](ARCHIVE_RECONSTRUCTION_AUDIT.json) binds the independently reconstructed bytes.
- Four fresh full apps, schema-2 receipts/nativeBinding, exact source/config/native inventories and build logs are in `batch/builds/` and cell receipts. Candidate installedAfter=967, reference=965; all source/binding/app/ARM64 checks Passed. Explicit Unity build GUID is not emitted by these receipts; none is inferred.
- [editor-scope.json](batch/editor-scope.json), [editor-verification.json](batch/editor-verification.json), [editor-results.xml](batch/editor-results.xml) bind all 754 selected exact identities Passed with zero skips. The single unavailable frozen M01 asset test remains excluded/NoCoverage.
- All 19 fresh-process requests/raw/logs and source-bound Passed/Failed verification receipts are in `batch/players/`. Four Release C03/C04/C05/C07 cells fail exact-loop cold-work assertions; both Debug warm witnesses Passed. Recording exit0 does not establish acceptance.
- [DIAGNOSTIC_FINDINGS.json](preflight/DIAGNOSTIC_FINDINGS.json) and [COLD_ATTRIBUTION_AUDIT.json](preflight/COLD_ATTRIBUTION_AUDIT.json) preserve complete raw.runtimeProbe samples/events/layout rows and independently reconcile all 30 spans. Four Release cases record the non-target mscorlib Enumerator on probe thread2 during exact loop phase2, distinct from owner1; original strict cells remain Failed.
- [PHYSICAL_PROOF_AUDIT.json](preflight/PHYSICAL_PROOF_AUDIT.json) applies the unchanged primitive-layout verifier to sealed C07 raw: Passed subcheck, both physical sides ready, source24/target32, offsets16→[16,24], privateInt64 tail and no baseline business initialization. C07 full cell remains Failed. [INTEGRATED_OBSERVATIONS.json](preflight/INTEGRATED_OBSERVATIONS.json) binds actual schema-2/native/Editor/Player observations and exact verification hashes.
- [POSTRUN_AUTHENTICATION.json](preflight/POSTRUN_AUTHENTICATION.json) binds index/archive/ledger/cells/79 streams/seven authenticated Unity completions/fixture/API/lifetime inputs and 5,027 prior custody bindings unchanged. Only named controls0048/0050/0055 preserve expected nonzero exits.
- [RETAINED_LIVE_ROOTS.json](preflight/RETAINED_LIVE_ROOTS.json) inventories six isolated projects, three detached references and excluded caches/native/generated/intermediates. Source snapshots bind executed native/managed code. [MANIFEST.sha256](MANIFEST.sha256) authenticates publication files except itself; batch-only attributes preserve immutable generated whitespace.

Live root `{R}`; preflight `{P}`. No earlier app/root/source pin was reused for execution. No Local source fix/retry/expectation/warm-up/deadline/lifetime change occurred. A–E/R02 evidence remains unchanged; E attribution stays unknown. Broader full-stage obligations are not completed or waived.
'''
preservation={}
for name,section in [('LOCAL_VALIDATION.md',local),('RETURN_TO_WEB.md',returned)]:
 q=D/'Docs/AssemblyShadow/Handoff'/name;original=q.read_bytes();text=original.decode();first,tail=text.split('\n',1);tail=tail.lstrip('\n').replace('## Current','## Historical',1)
 q.write_text(first+'\n\n'+section+'\n'+tail)
 preservation[name]={'priorExecutedHead':'8f86dda1aa0582a5b2d55aa650ea321f710cb49a','priorSha256':hashlib.sha256(original).hexdigest(),'newSha256':sha(q),'historyPolicy':'Previous report body preserved byte-for-byte except first Current-to-Historical E heading'}
(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps(preservation,indent=2)+'\n');(C/'README.md').write_text(checkpoint)
print('Wrote F Local reports and immutable checkpoint README; previous bodies preserved')
