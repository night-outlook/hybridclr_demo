import datetime,hashlib,json,pathlib,shutil
from zoneinfo import ZoneInfo
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261003I-completion';R=P.parent/'R03LocalBatch-20261003I-completion';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261003-batch-i-return-required';rel='../History/M07R/R03/'+C.name
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();result=load(R/'LOCAL_BATCH_RESULT.json');auth=load(P/'POSTRUN_AUTHENTICATION.json');inv=load(P/'runner-exit.json');issues=load(P/'PRIMARY_ISSUES.json');integrated=load(P/'INTEGRATED_OBSERVATIONS.json');prod=load(P/'PRODUCER_RUNTIME_AUDIT.json');rej=load(P/'REJECTION_RUNTIME_AUDIT.json');complete=load(P/'COMPLETION_RUNTIME_AUDIT.json');pins=result['repositories']
assert result['result']=='ReturnRequired' and result['sealStatus']=='Passed' and inv['exitCode']==1 and auth['status']=='Passed' and auth['counts']=={'Passed':40,'Failed':2,'Blocked':48} and rej['status']=='Passed'
start=datetime.datetime.fromisoformat(inv['startedUtc']);end=datetime.datetime.fromisoformat(inv['endedUtc']);localtime=start.astimezone(ZoneInfo('America/Los_Angeles')).strftime('%Y-%m-%d %H:%M:%S')+'–'+end.astimezone(ZoneInfo('America/Los_Angeles')).strftime('%H:%M:%S %Z');command=' '.join(inv['command'])
pinrows='\n'.join('| `'+str(W/n)+'` | `'+pins[n]+'` |' for n in ['hybridclr_demo','hybridclr','hybridclr_unity','il2cpp_plus']);cellrows='\n'.join('| `'+c['id']+'` | '+c['result']+' | '+(', '.join(c.get('blockedBy',[])) if c['result']=='Blocked' else c.get('error',''))+' |' for c in result['cells']);hashrows='\n'.join('| `'+n+'` | `'+h+'` |' for n,h in auth['topLevelHashes'].items());artifactrows='\n'.join('| `'+v['path'].replace(str(R)+'/','')+'` | `'+v['sha256']+'` |' for v in issues['evidence']);size=(R/'evidence.tar.gz').stat().st_size
warmtable='\n'.join('| `'+v['case']+'` | '+str(v['pid'])+' | '+str(v['producerFence']['elapsedMicros'])+' | '+str(v['producerFence']['deferred'])+'/'+str(v['producerFence']['deferredCompleted'])+' | Passed |' for v in prod['rows'] if v['kind']=='StrictIsolatedMain');failureNames='\n'.join('- `'+v['fullname']+'`' for v in issues['issues'][0]['failedCases']);ctorxml=next(v['sha256'] for v in issues['evidence'] if v['path'].endswith('/results.xml'));installhash=next(v['sha256'] for v in issues['evidence'] if v['path'].endswith('/resource-logs/install.log'));issuepin=issues['issues'][1]['sourcePinsSha256'];settingshash=issues['issues'][1]['settingsSha256'];qualification=next(v['evidence'] for v in complete['checks'] if v['id']=='static-qualification');exitCounts={str(k):sum(c['exitCode']==k for c in auth['commands']) for k in [0,1]}
local=f'''## Current run — R03 completion batch I (2026-10-02 PDT / 2026-10-03 UTC): two independent prerequisite defects

**Local Validation → Primary Implementation. Result=ReturnRequired; 90 cells: 40 Passed / 2 Failed / 48 Blocked; sealStatus=Passed; runner exit1.** Exactly one invocation, PID {inv['pid']}, {localtime}; UTC {inv['startedUtc']}–{inv['endedUtc']}. Four of six planned native builds Passed; both resource builds Blocked. The focused Editor roster ran all754 cases: 736 Passed, 18 Failed, zero skipped/inconclusive. The 755-case resource-complete Editor run was Blocked. All23 focused fresh-process Player contracts Passed; the remaining36 resource/R00/early Players were Blocked and never launched. Source-bound qualification/tooling checks Passed without authorizing expansion. No Local source fix, retry, manual blocked-stage execution, old-app reuse, expectation/counter/scope/pin/lease/deadline change, terminal restoration or acceptance promotion occurred.

### Executed authority, pins, platform and operations

All four owning checkouts independently matched absolute top-level paths, branch `codex/assembly-shadow-r01b-h1`, clean status, canonical origins `git@github.com:night-outlook/<repository>.git`, exact local HEAD and remote tip at preflight and completion. Demo safely fast-forwarded from H Local publication `3a9d51a9bb42b12bf29dfd6e0d7d12956ae04a68`; the managed package advanced to the qualification source below. Executable/CI anchor `55d43dd828d96647298b91ed6d8da122523f8a87` is an ancestor with documentation-only delta to executed demo. Source/package/native pins, submodule state, manifests, config hashes and worktree registration were recorded individually. Ordinary primary checkout/control siblings were not used or changed.

| Owning repository path | Exact executed commit |
| --- | --- |
{pinrows}

Fresh detached reference worktrees beneath `{R}/reference-worktrees` are clean at native `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, IL2CPP `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`, reference graph package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`. Four focused projects/builds and the new resource-complete copied project retain separate source/config/cache/install/output paths. [RETAINED_LIVE_ROOTS.json]({rel}/preflight/RETAINED_LIVE_ROOTS.json) records exact roots. Four schema-2 build/nativeBinding receipts and complete arm64 app inventories authenticate successful focused builds; their build GUID is Unavailable where the receipt provides none. No resource app/build GUID/native installation is inferred after failed installation.

Environment: macOS26.5 arm64; Python3.14.6; .NET SDK8.0.318/runtime8.0.21; PowerShell7.6.3; Apple clang21.0.0/macOS SDK26.5. Exact Unity `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, StandaloneOSX/arm64. SDK-only root `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`; no Unity6000 Editor execution. Pinned mscorlib SHA-256 `d89d5124cafb873b34c2eac68d2ece41d14fec10999baf0e4620276dff54ab83`. Scoped SDK PATH/DOTNET_ROOT/DOTNET_ROOT_ARM64, DOTNET_MULTILEVEL_LOOKUP=0, PYTHONDONTWRITEBYTECODE=1, TMPDIR=/private/tmp and actual argv/PID/timestamps/exit are preserved in runner receipts. No existing Unity Editor at preflight; gate helper Off; no independent full-stage review claimed. The batch's 20261003 name is its source-bound logical identity; actual local execution date above is October2 PDT.

```text
{command}
```

### Required scope and factual coverage

| Validation | State and exact boundary |
| --- | --- |
| Entry/final authority and source/pin binding | Passed; exact tuple remained clean/pushed |
| Completion tooling / retained verifier tests | Passed;49 /183 source-defined Python tests, not Player coverage |
| Qualification | Passed;32 real-DLL static cases, byte-bound inventory {qualification['inventoryFiles']} files; runtimeProofExecuted/expansionAuthorized=false |
| Host baseline/candidate graphs and admission | Passed;9+9 graph cases and35 admission cases |
| Real fixtures / unsigned-reference audit / Unity consumers | Passed;15 DLLs,33 audits,33 consumers |
| Lifecycle probes / complete-helper compilation | Passed contracts; valid/invalid probes and exact old-helper two-CS0266 negative control retained |
| Focused four native/IL2CPP builds | Passed; fresh candidate/reference/debug/feature-OFF roles |
| Focused Editor | Failed;754 cases,736 Passed/18 Failed/0 skipped/0 inconclusive; all failures occur in reflective fixture construction |
| Focused main Players | Passed;19 distinct fresh processes |
| Four natural producer controls | Diagnostic Passed; all contaminated unisolated warm certificates remain Failed |
| Six strict main warm witnesses / full positive C07 | Passed; unchanged zero all-thread exact-loop proof/layout work and positive physical-layout/business checks |
| Five rejected-stage observations | Passed; error16 unchanged across capacity -2, two full reads and final raw state |
| Original-resource copied project | Passed preparation;525 selected files/6 frozen M01 files verified; copying is not M01 runtime acceptance |
| Resource install | Failed; generated pins omit architecture, rejected by production SourcePinTarget before installation |
| Resource compiler/bundles/ON/OFF builds/P05 prepare/compile/finalize | Blocked; no manual continuation |
| P05 restore cell | Passed cleanup only: NoRecordedMutation / restorationCoverage=NotApplicable; no P05 transaction or byte-restoration proof |
| 755-case resource Editor/M01 | Blocked / NoCoverage; no XML or new M01 acceptance evidence |
| Production entry P01–P05/input binding/14 resource Players | Blocked; no apps/manifests/bundle/runtime acceptance |
| 12 unfenced R00 observations/M06 supplements/measurement summary | Blocked; measurements.json/statistics/memory observations Unavailable, not zero-valued |
| 10 early-startup Players | Blocked; no fresh startup results |
| Evidence sealing/custody | Passed integrity; does not turn Failed/Blocked validation into acceptance |

All90 predetermined cells are retained, including independent successes and dependent Blocked states:

| Cell | Original sealed state | Error / blockers when recorded |
| --- | --- | --- |
{cellrows}

{len(auth['commands'])} command receipts retain authenticated streams, original exits and clean process-group completion; {exitCounts['0']} exit0 and {exitCounts['1']} exit1. Only0051/0053/0058 are expected-negative compiler controls. Failed Editor0063 has actual Unity exit2 normalized by its existing supervisor to outer1; resource-install0087 has Unity/outer1. Eight Unity completion receipts preserve bounded birth-authenticated compiler retirement, clean=true, no survivors/timeouts/cleanup errors. No global compiler kill or reclassification of failed commands occurred. All23 launched Player PID/run IDs are distinct and source/request/raw/build receipt bound. Primary's host/compiler CI is retained as historical/static evidence, not substituted for missing Local stages.

### Preserved focused runtime witnesses

[REJECTION_RUNTIME_AUDIT.json]({rel}/preflight/REJECTION_RUNTIME_AUDIT.json) confirms the five one-transaction cases C02/C08/C09/C10/D01 retain original failed state8/error16/unpublished/RestartRequired through four before/after captures plus final raw. The16-byte capacity call returns-2; both full returns match exact UTF-8 payload lengths (C02/D01=2697, C08/C09=1664, C10=2730). Captured baseline/target identities and rows remain equal under R03OwnedLayoutIdentityV1; full transaction projection and entire recovery are unchanged. No error15/-3/probe exception or terminal restoration. Retained prior rows do not identify the failing type. H/G historical data is unchanged.

[PRODUCER_RUNTIME_AUDIT.json]({rel}/preflight/PRODUCER_RUNTIME_AUDIT.json) reconciles all10 probes and50 native spans. Six main leases remain finite R03ArrayPoolFinalizerFenceV1/5000ms, acquired/released/drained=true, expired/invalid=false; exact-loop cold work zero and cache hits/baseline checks at least10000.

| Main witness | PID | Lease elapsed µs | Deferred/completed | Strict certificate |
| --- | --- | --- | --- | --- |
{warmtable}

All four natural controls identify an exact-loop Object::NewAllocSpecific admission on probe thread2 rather than owner1, nested `ConditionalWeakTable<byte[][],object>.Enumerator`, actual `System.Gen2GcCallback` / `Gen2GcCallbackFunc` token100672638 / closed `TlsOverPerCoreLockedStacksArrayPool<byte>`, recognizedArrayPool=true. Each has miss/proof/entry +1 and bytes+80, all four cold events retained; aggregate identifiedLoopAdmissions=4. These diagnostic contracts Passed while each unisolatedWarmCertificate=Failed. Pairing uses source/DLL/build hashes and distinct process/run identities, never cross-process pointer/thread equality. Diagnostic lease isolation may delay queued finalizers; it is not production GC/performance acceptance.

Full C07 and paired physical subchecks Passed: source24/target32 bytes, source offset16 retained, target private8-byte tail offset24/storage[4,8]; baselineReady/targetReady/targetDefinitionReady/physicalProof=true, error0, pending/truncated=false. Captured statuses complete; source/targetSizeInited=false preserved, finalized definition provides readiness. Baseline business/vtable/cctor flags remain false/false/0. Main publication/reflection/delegate41 and10000 allocations Passed. These focused results do not fill blocked resource, broader runtime or observation coverage.

### Two Primary-owned problems and retained limitations

[R03-LI-001 and R03-LI-002 in RETURN_TO_WEB.md](RETURN_TO_WEB.md) provide exact reproduction, excerpts, root causes, impact, concrete repair directions and post-fix validation. [PRIMARY_ISSUES.json]({rel}/preflight/PRIMARY_ISSUES.json) retains all18 failure names/stacks, generated pin bytes, configured arm64 settings, source snapshots and hashes. The first is an internal constructor/test-fixture contract mismatch; the second is a generator/production source-pin schema mismatch. No Local implementation was made: successful closure requires updating the authoritative source/test contracts and a newly authorized fresh integration batch. Small textual changes do not justify reusing I or claiming post-fix acceptance.

M01 remains NoCoverage for I because the required resource Editor was Blocked; H's prior exclusion stays historical NoCoverage. P05 structural restoration is NotApplicable cleanup, not successful restoration coverage. No broader M06 supplement, production graph/generation, current-source timing/memory or early-startup coverage was obtained. Unknown downstream failures remain unknown. No unsupported support scope, performance SLA, R03/H2 acceptance or independent qualification approval is inferred from static qualification or focused success.

### Immutable evidence publication and exact exit

[POSTRUN_AUTHENTICATION.json]({rel}/preflight/POSTRUN_AUTHENTICATION.json) authenticates {auth['indexedLiveFiles']} indexed files and {auth['archiveMembers']} exact safe unique archive members, result/ledger/90 individual cells and all command streams. All {auth['priorCustodyFilesUnchanged']} earlier evidence bindings remain unchanged. [COMPLETION_RUNTIME_AUDIT.json]({rel}/preflight/COMPLETION_RUNTIME_AUDIT.json) records23 actual Player commands, zero resource/R00/early processes, qualified static success and NotRun read-only replay stages for blocked prerequisites. Audit integrity Passed is distinct from original ReturnRequired.

Live `{R}` and all referenced roots remain retained. Immutable [I checkpoint]({rel}/README.md) contains every indexed byte, top result/index/seal and exact ordered archive parts. Archive {size} bytes; [ARCHIVE_TRANSPORT.json]({rel}/ARCHIVE_TRANSPORT.json), [ARCHIVE_RECONSTRUCTION_AUDIT.json]({rel}/ARCHIVE_RECONSTRUCTION_AUDIT.json), [MANIFEST.sha256]({rel}/MANIFEST.sha256) and publication checks authenticate independent fresh reassembly, committed bytes, JSON and links. No recompression, omission, raw/flag/schema rewrite or old evidence promotion. Exact source/generated whitespace is retained through narrow authenticated snapshot attributes.

| Original artifact | SHA-256 |
| --- | --- |
{hashrows}

Only the two Local reports and new I checkpoint are publication changes; no bounded fix or affected source repository change. Final pushed demo publication HEAD is distinct from executed c579e75eadef58ca484b35ffee03e435a925d781, recorded after non-force push in `{P}/PUBLICATION_RECEIPT.json` and final handoff with all four clean canonical remote heads. **R03Accepted=false; H2Passed=false; qualificationApproved=false; pureInterpreterExpansionEnabled=false; fullLegacyRegressionAcceptance=false; no release performance SLA approved.** Exit exactly **Local Validation → Primary Implementation** for the two defects and remaining stage work. Stop; no batch retry, new milestone, qualification expansion or H2 is authorized.
'''
ret=f'''## Current return — R03 batch I: Editor fixture constructor and copied source-pin schema defects

**ReturnRequired;90 cells:40 Passed/2 Failed/48 Blocked;seal Passed;runner exit1.** Exactly one source-bound invocation PID{inv['pid']}, {localtime} (UTC {inv['startedUtc']}–{inv['endedUtc']}). Four focused builds and23 focused Player contracts Passed; qualification32 static cases Passed without expansion authority. Focused Editor754 cases yielded736 Passed/18 Failed/zero skips. Resource installation failed before native install; two resource builds,755-case Editor and36 resource/measurement/early Players remain Blocked. No retry, source fix, scope change or blocked-stage execution. Read [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md), [I checkpoint]({rel}/README.md) and [PRIMARY_ISSUES.json]({rel}/preflight/PRIMARY_ISSUES.json).

### Exact reproduction performed for both entries

Use only the executed four-repository source tuple and branch codex/assembly-shadow-r01b-h1 in LOCAL_VALIDATION.md, Unity2022.3.62f2/SDK8.0.318. The following command was invoked once; **do not repeat I or reuse its apps/root**:

```text
{command}
```

### R03-LI-001 — reflected CompiledAssemblySet fixture construction uses obsolete four-argument contract

**Symptom.** Focused EditMode selected all754 exact identities;18 fail before policy assertions with `System.Reflection.TargetParameterCountException : Number of parameters specified does not match the expected number.` There are17 ManagedAcquisitionPolicyTests failures and one PolicyTests failure. XML is `{R}/focused-editor/results.xml`, SHA-256 `{ctorxml}`. Editor log/scope/verdict and command0063/unity-completion are sealed. Actual Unity exit2, outer supervisor1, clean completion; no lifetime failure. Raw first witness stack includes `ManagedAcquisitionPolicyTests+Fixture.CreateSet ... ManagedAcquisitionPolicyTests.cs:393`; the Policy witness points to `PolicyTests.cs:285`.

**Root cause.** At package11a20efadd8f1ebc494d02ac80135e224dabd3e5, `Editor/AssemblyShadow/Metadata/CompiledAssemblySet.cs:28–29` has a five-parameter internal constructor: assemblies,modules,resolver,deferredFacadeReferences,`IEnumerable<CompiledAssemblySource> sources`. `Tests/Editor/AssemblyShadow/ManagedAcquisitionPolicyTests.cs:392–393` and `PolicyTests.cs:284–285` still select the single non-public constructor and invoke four objects. Reflection bypasses compile-time arity checking. Host/tool qualification and full-helper compilation did not execute these Editor fixtures, so their green results did not detect the stale contract. Exact source blobs/copies/hashes are in PRIMARY_ISSUES.json and [issue-source-snapshot]({rel}/preflight/issue-source-snapshot).

**Impact/direction.** Current Editor acquisition/policy regression assertions are unverified because fixtures fail during construction; this does not establish a native layout/admission regression. Repair test construction against the current contract, preferably through one checked fixture helper rather than duplicated implicit `GetConstructors().Single()` assumptions. Supply semantically correct byte/source records where needed, or an explicit synthetic-fixture boundary; do not fake qualification provenance, add null blindly, loosen production source binding or drop the failed tests. Audit other constructor consumers. Whether any deeper assertion fails after construction remains unknown. Run the affected tests and unchanged full754/755 rosters under pinned Unity in a newly authorized source/root; preserve I's failures.

Exact failed identities:

{failureNames}

### R03-LI-002 — completion fixture generates source pins without required architecture

**Symptom.** Independent resource-install command0087 (Unity/outer exit1, clean completion) throws:

```text
ShadowBuildException: SourcePinTarget: Source pins do not match exact Unity version, target and architecture.
ShadowSourcePins.Read ... ShadowSourcePins.cs:34
M07Build.Configure ... M07Build.cs:51
R03CompletionBuild.<Install> ... R03CompletionBuild.cs:108
```

Live log `{R}/resource-logs/install.log` line10599 onward, SHA-256 `{installhash}`. Generated `{R}/projects/resource-complete/ProjectSettings/AssemblyShadowSourcePins.json`, SHA-256 `{issuepin}`, has schemaVersion1/unityVersion2022.3.62f2/targetStandaloneOSX and exact repository pins but **no architecture key**. Configured AssemblyShadowSettings.asset explicitly records `architecture: arm64`, SHA-256 `{settingshash}`. Exact copies are [issue-resource-snapshot]({rel}/preflight/issue-resource-snapshot); full stack/source evidence and copies/hashes are in PRIMARY_ISSUES.json.

**Root cause and scope.** `Tools/AssemblyShadow/R03Completion/fixture_project.py:85–91` builds the pin object with schemaVersion,unityVersion,target and repository records, omitting architecture. Production `ShadowSourcePins.Read:29–35` requires `pins.architecture == architecture`; omitted JsonUtility field is null versus configured arm64. `M02Build.Configure:40` sets the architecture before `M07Build.Configure:51` consumes pins. The Python copied-project verifier compares against the same incomplete generator and never proves the production C# serialized contract. Static compilation cannot detect the missing runtime JSON field. Installation aborts before the pinned native root exists; no resource compiler/bundles/ON-OFF builds/P01–P05 finalization,755-case M01 Editor,14 resource Players,12 observation/M06 processes or10 early cases execute. All48 dependent cells remain Blocked.

**Concrete direction/uncertainty.** Generate and bind the full source-pin platform schema, including the pinned arm64 field, and add a generator-to-production-consumer contract prerequisite. Keep SourcePinTarget and exact revision/target guards intact; no fallback architecture or hand-edit of I's generated JSON. Prove the copied project matches production serialization/validation before expensive phases. Revalidate install, all six builds, resource scopes/bundles/production entries/restoration and59 Players in a newly authorized complete batch. Downstream issues remain unknown. The P05 restore cell only reports `NoRecordedMutation / NotApplicable` because no transaction state was recorded; M02 configuration wrote permitted settings before failing, so this is not a claim that no project file changed, nor successful P05 byte-restoration coverage.

### Preserved exit and evidence states

The six strict warm witnesses, five non-mutating rejection observations, actual producer controls and full C07 all Passed freshly in I; four contaminated control warm certificates remain Failed. These independent successes do not replace missing completion coverage. M01 remains NoCoverage; measurements/statistics/runtime supplements/early evidence are Unavailable because their cells are Blocked. No Local fix can be closed-loop verified within the authorized single source-bound batch without another tuple/root; both contract repairs return to Primary. All historical A–H evidence remains unchanged. R03Accepted=false;H2Passed=false;qualificationApproved=false;PureInterpreter expansion disabled;no release performance SLA. Exit **Local Validation → Primary Implementation**.

Key exact evidence hashes (immutable copies beneath checkpoint/batch):

| Evidence path relative to live I root | SHA-256 |
| --- | --- |
{artifactrows}
'''
for a,b in [('macOS26.5','macOS 26.5'),('Python3.14.6','Python 3.14.6'),('SDK8.0.318','SDK 8.0.318'),('runtime8.0.21','runtime 8.0.21'),('PowerShell7.6.3','PowerShell 7.6.3'),('clang21.0.0','clang 21.0.0'),('SDK26.5','SDK 26.5'),('Unity6000','Unity 6000'),('Unity2022.3.62f2','Unity 2022.3.62f2'),('all754','all 754'),('all90','all 90'),('All90','All 90'),('All23','All 23'),('all10','all 10'),('and50','and 50'),('and35','and 35'),('and23','and 23'),('remaining36','remaining 36'),('all48','all 48'),('All48','All 48'),('least10000','least 10000')]:local=local.replace(a,b);ret=ret.replace(a,b)
preservation={}
for name,body in [('LOCAL_VALIDATION.md',local),('RETURN_TO_WEB.md',ret)]:
 q=D/'Docs/AssemblyShadow/Handoff'/name;old=q.read_bytes();heading,tail=old.decode().split('\n',1);tail=tail.lstrip('\n').replace('## Current','## Historical',1);q.write_text(heading+'\n\n'+body+'\n'+tail);preservation[name]={'originalCommit':pins['hybridclr_demo'],'originalSha256':hashlib.sha256(old).hexdigest(),'newSha256':sha(q),'policy':'Prepend I; only previous Current H heading becomes Historical; previous body otherwise unchanged'}
(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps(preservation,indent=2)+'\n');(C/'README.md').write_text(f'''# Immutable R03 completion batch I Local evidence

**ReturnRequired;90 cells:40 Passed/2 Failed/48 Blocked;seal Passed;runner exit1.** One invocation PID{inv['pid']}, UTC {inv['startedUtc']}–{inv['endedUtc']} ({localtime}). Four focused builds/23 focused Player contracts Passed. Focused Editor736/754 Passed,18 Failed,zero skips; resource-install fails before installation. Two resource builds,755-case Editor and36 additional Players Blocked. Static qualification Passed without expansion authority; six warm witnesses/rejection preservation/full C07 Passed; contaminated controls retain Failed unisolated certificates. R03/H2/qualification approval remain false.

Read [Local report](../../../../Handoff/LOCAL_VALIDATION.md), [Primary return](../../../../Handoff/RETURN_TO_WEB.md), [PRIMARY_ISSUES.json](preflight/PRIMARY_ISSUES.json). LI-001 is obsolete reflected fixture constructor arity; LI-002 is missing architecture in generated pins. No source fix or retry. Later reports may advance; I raw bytes stay immutable.

[batch/LOCAL_BATCH_RESULT.json](batch/LOCAL_BATCH_RESULT.json), [batch/BATCH_EXECUTION.json](batch/BATCH_EXECUTION.json), [batch/completion-plan.json](batch/completion-plan.json), [batch/evidence-index.json](batch/evidence-index.json), [batch/seal-receipt.json](batch/seal-receipt.json) and every indexed command/source/config/fixture/build/Editor/Player byte are copied exactly. [POSTRUN_AUTHENTICATION.json](preflight/POSTRUN_AUTHENTICATION.json) covers {auth['indexedLiveFiles']} indexed files/{auth['archiveMembers']} exact archive members and {auth['priorCustodyFilesUnchanged']} older custody bindings unchanged. [COMPLETION_RUNTIME_AUDIT.json](preflight/COMPLETION_RUNTIME_AUDIT.json), [REJECTION_RUNTIME_AUDIT.json](preflight/REJECTION_RUNTIME_AUDIT.json), [PRODUCER_RUNTIME_AUDIT.json](preflight/PRODUCER_RUNTIME_AUDIT.json) preserve distinctions and source-bound observations. [RETAINED_LIVE_ROOTS.json](preflight/RETAINED_LIVE_ROOTS.json) lists retained caches/projects/reference roots; resource apps/measurements were not produced.

Executed source tuple is in result/preflight, exact owning paths beneath `{W}`, branch codex/assembly-shadow-r01b-h1. Unity2022.3.62f2/StandaloneOSXarm64 and SDK8.0.318. Live root `{R}` remains intact. [ARCHIVE_TRANSPORT.json](ARCHIVE_TRANSPORT.json) describes exact ordered parts; [REASSEMBLE_EVIDENCE.py](REASSEMBLE_EVIDENCE.py) authenticates a new absolute unused destination, expected {size} bytes/SHA-256 `{auth['topLevelHashes']['evidence.tar.gz']}`. [ARCHIVE_RECONSTRUCTION_AUDIT.json](ARCHIVE_RECONSTRUCTION_AUDIT.json) binds separate reconstruction; original live archive/seal unchanged. [MANIFEST.sha256](MANIFEST.sha256) covers checkpoint except itself; [REPORT_HISTORY_PRESERVATION.json](REPORT_HISTORY_PRESERVATION.json) binds previous report bodies. Source/runtime settings snapshots are raw evidence, not additional execution. Final pushed publication identity is externally verified in `{P}/PUBLICATION_RECEIPT.json` and final handoff, distinct from executed source. Exit exactly Local Validation → Primary Implementation.
''');shutil.copy2(__file__,C/'preflight/write-reports.py');print('Wrote two owned I reports and checkpoint README')
