import pathlib,json,hashlib,datetime,zoneinfo,shutil
D=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');R=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001E-provenance');P=R.parent/'Preflight-R03LocalBatch-20261001E-provenance';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261001-batch-e-return-required'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
audit=load(P/'POSTRUN_AUTHENTICATION.json');obs=load(P/'INTEGRATED_OBSERVATIONS.json');run=load(P/'runner-exit.json');result=load(R/'LOCAL_BATCH_RESULT.json');diagnosis=load(P/'DIAGNOSTIC_FINDINGS.json');live=str(R);checkpoint='../History/M07R/R03/'+C.name+'/README.md';hashes=audit['topLevelHashes'];start=datetime.datetime.fromisoformat(run['startedUtc']);end=datetime.datetime.fromisoformat(run['endedUtc']);tz=zoneinfo.ZoneInfo('America/Los_Angeles');localtime=start.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')+'–'+end.astimezone(tz).strftime('%H:%M:%S')+' PDT';utctime=run['startedUtc']+'–'+run['endedUtc'];assert result['result']=='ReturnRequired' and audit['counts']=={'Passed':32,'Failed':4}
command=' '.join(run['command']);version=load(P/'environment.json')['versions']
local=f'''## Current run — R03 batch E, 2026-10-01: provenance/scope repairs pass; four runtime cells fail

**Local Validation → Primary Implementation. Result=ReturnRequired; 36 cells: 32 Passed, 4 Failed, 0 Blocked; sealStatus=Passed; runner exit 1.** Exactly one invocation, {localtime} (UTC {utctime}), runner PID {run['pid']}. Four fresh native build roles and the scoped Editor run passed. All 19 fresh-process Players ran: 15 Passed, 4 Failed. No Local source fix, retry, pin/scope/expectation/deadline/cleanup change, or acceptance promotion occurred.

### Executed authority and environment

All four owning checkouts independently matched absolute top-level path, branch, clean status, canonical origin and exact current remote tips before and after execution. All branches are `codex/assembly-shadow-r01b-h1`; origins are `git@github.com:night-outlook/<repository>.git`. The candidate demo fast-forwarded cleanly from published D return `33d7b1fce2f3b8463dc4ac78061250ecc7df925d`. Tested source anchor `979abd80b673e690c5f82819ed194200f8d2e536` is an ancestor and its delta to the executed transport is documentation/evidence-only. Latest WEB_TO_LOCAL.md-touching commit equaled prompt/local/remote HEAD.

| Repository path | Exact executed commit |
| --- | --- |
'''
for name,h in result['repositories'].items():
 if name in ['hybridclr_demo','hybridclr','hybridclr_unity','il2cpp_plus']:local+=f'| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/{name}` | `{h}` |\n'
local+=f'''
Reference worktrees are fresh, clean and detached under `{live}/reference-worktrees/`: HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`; IL2CPP `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`; graph-test package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`. Native reference roles use that reference core and the current package/test harness; they do not substitute an old accepted Player. Role source manifests and install pins bind executed demo, package, native/IL2CPP sources and baseline fixture inventory. Historical owning-project H1 pin files remain unchanged and were not used to build the owning Unity project; the runner emitted isolated role configurations. No primary-checkout Library/HybridCLRData/Builds or previous batch app was used.

Environment: macOS 26.5 arm64; Python 3.14.6; SDK 8.0.318/runtime 8.0.21; PowerShell 7.6.3; Apple clang 21.0.0; macOS SDK 26.5. Exact Unity executable `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, target StandaloneOSX/arm64. SDK `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk` was used as SDK only; Unity 6000 Editor was not launched. Recorded tool versions, command timestamps/status/worktree/ref checks, scope/config hashes and the one invocation are in checkpoint `preflight/`. An auxiliary broad process substring assertion matched pre-existing Unity Hub; the exact executable observation and unused isolated-project roots are retained in scope-and-config-pins.json. No process was terminated for that observation and no batch retry occurred.

Actual command, from the owning demo checkout:

```text
{command}
```

`preflight/runner-exit.json` binds start/end, PID, cwd, environment, exit and batchInvocations=1. All 79 command receipts record per-operation timestamps, argv/PID/process group, stream paths/hashes, original exits and lifetime flags. Outer Unity command PIDs identify supervisors; direct Player PIDs bind request/run IDs and raw observations. Build GUIDs and native/managed/app inventories remain in each schema-2 build receipt and corresponding Editor.log.

### Fresh validation and coverage states

| Validation | State | Evidence and limit |
| --- | --- | --- |
| Entry/final Git authority and reference worktrees | Passed | Exact clean four-repository tuple and retained fresh detached references. |
| Verifier/input/API/lifetime/provenance/scope contracts | Passed | 116 Python tests, command 0001. Synthetic contracts do not replace actual native/runtime evidence. |
| Graph suites and admission | Passed | Reference 9/9, candidate 9/9 and admission 35/35. |
| Player fixtures and input prerequisites | Passed | 15 DLLs, 33 metadata audits, 33 actual pinned Unity compiler consumers, invalid-key negative control, two actual Editor compiler-lifetime probes. |
| Complete helper/package API prerequisite | Passed | Real package Runtime/CodeGen/Editor assemblies and full helper; 425 input bindings, 115 defines, five commands 0051–0055. Old C helper still yields exactly two expected CS0266 errors and no DLL. |
| Four preparations and fresh native build cells | Passed | Candidate Release, reference Release, candidate Debug and feature-OFF; real installer/generation/IL2CPP/C++/link. Schema 2, exact installedNativeRoot, app inventory and ARM64 verified; nativeBinding emitted. |
| Actual selected EditMode execution | Passed | Command 0060; exact 754 selected identities all Passed, zero failures/skips/inconclusive cases; all 35 mandatory R03 IDs and cycle case included. |
| Excluded frozen M01 resource asset test | NoCoverage | Exact single excluded identity/reason/assets in editor-scope.json and editor-verification.json. Not counted as Passed; fullLegacyRegressionAcceptance=false. |
| Fresh-process Players | 15 Passed / 4 Failed | All 19 unique PID/run-ID requests executed once; raw, logs, command receipts and original cell states preserved. |
| Focused seal and separate custody audit | Passed | 1,867 indexed files / 1,868 exact archive members; cell/ledger equality and stream/tool/input bindings; 3,081 prior custody hashes unchanged. |

All 79 command groups completed with no survivor, timeout or cleanup error. 76 command exits were 0; only 0048 (invalid compiler consumer), 0050 (invalid actual Editor probe), and 0055 (preserved C helper) were the named expected-negative exit-1 controls. Those are distinct from successful builds. Seven birth-authenticated Unity completions preserved inner exits and retired their owned compiler children cleanly. Player recording exit 0 is not semantic acceptance: four runtime cells failed their unchanged verifier.

R03-LD-001 is verified repaired in E's executed scope: every producer-selected SDK root matches its schema-2 nativeBinding, exact source tuple and installedAfter inventory despite preserved generation receipt copies. Candidate installed counts are 965→966; reference counts 964→965; no fixed shared inventory count is imposed. R03-LD-002 is verified repaired for the focused scope: actual filtered XML matches all 754 catalog identities with zero skips. The actual frozen M01 fixture/resource obligation remains NoCoverage. D's Failed cells and ignored XML remain historical, not promoted.

### Runtime failures and observations

| Failed cell | Unchanged verifier error | Actual observation |
| --- | --- | --- |
| C03-moved-slot | Repeated warm proof work: admissionCacheMisses | Completed/published, reflection+delegate 42, 10,000 allocations; warm misses/proofs/entries +1, retained bytes +80; hits/baseline checks +10,000. |
| C04-old-AOT-guard | Repeated warm proof work: admissionCacheMisses | Same warm delta; reflection+delegate 42; raw native probe observes active guard 1, baseline guard 0, final state 9 / restart code 21. |
| C05-direction-reversal | Repeated warm proof work: admissionCacheMisses | Complete successful publication/reversed graph, reflection+delegate 41, 10,000 allocations; same extra cold proof delta. |
| C07-private-primitive-append | Complete successful publication API chain | Validate returns 16/state 8 before Commit; NativeLayoutNeedsNativeProof / ChangedLayoutUnavailableBeforePublication; no invocation or warm loop. |

Release C03/C04/C05 each also show +5 genericContextChecks. No field/interface workspace build or layoutCheckCalls increases during the warm interval; resolver remap/miss counters do not increase. Debug D02/D03 pass with 10,000 hits/baseline checks and zero new admission miss/proof. The process-wide admission counters cover every allocation class/thread after publication, so the single additional completed cache entry cannot be attributed to the business Node from current evidence. Most likely boundary: one cold allocation/cache construction in the broad measured/observer/harness interval; its exact class/site/thread and timing are unavailable. This does not prove a cache regression, justify waiving +1, or establish the failed Release warm certificate.

C07's private Int64 append is Editor-screened as NeedsNativeProof, not guaranteed native compatibility. Native CheckStagedPair rejects changed fields if the physical baseline or target readiness predicate is false, before CheckLayout and publication. Raw diagnostics prove that readiness rejection, not an offset incompatibility; which side/readiness subcondition failed is unavailable. Return entries R03-LE-001/002 include exact reproduction, hashes, source excerpts, uncertainty, implementation direction and required new validation.

The 15 Passed Player cells are C01/C02/C06/C08/C09/C10, R01–R05, D01–D03 and O01. This includes baseline controls, targeted conservative rejections, actual target-cycle rejection, original reference late-layout/slot behaviors, Debug MethodInfo remapping/old-AOT guard and feature-OFF baseline. C03/C04 raw real MethodInfo mappings show moved slots and stable identities, but these observations do not promote their Failed warm-certificate cells. All 19 raw observations are retained. Only the 15 passed cases have successful verification.json outputs; the four failed cases have Failed cell receipts and original raw evidence, with successful-verdict files Unavailable by design after the throw.

### Evidence custody, publication and exit

Immutable [batch-E checkpoint]({checkpoint}) stores all 1,867 indexed files individually, including four complete apps, command streams, original result/ledger/index/seal, fixture/compiler/lifecycle evidence, schema-2 receipts/nativeBinding, actual XML/scope/verdict, all Player requests/raw/logs/available verifications, executed source snapshots and separate read-only authentication/diagnosis. Live root `{live}` and preflight `{P}` remain intact. Excluded Library/HybridCLRData/native/generated roots, six isolated projects, three references and compiled/intermediate files are inventoried in RETAINED_LIVE_ROOTS.json. No earlier raw or sealed bytes were edited.

| Original artifact | SHA-256 |
| --- | --- |
'''
for name,h in hashes.items():local+=f'| {name} | `{h}` |\n'
local+=f'''
Original live evidence.tar.gz is {(R/'evidence.tar.gz').stat().st_size:,} bytes and exceeds GitHub's single-blob limit. ARCHIVE_TRANSPORT.json binds three ordered exact byte parts; their concatenation reconstructs the unchanged original archive hash. The reconstruction audit verifies every part, size and whole hash at a new external destination. This publication representation is separate from the focused seal and does not replace/re-compress the live archive or omit an indexed member. MANIFEST.sha256 binds checkpoint publication bytes. All prior A–D checkpoints/live evidence and R02 I result/index/archive custody bindings are unchanged.

Only two Local reports and this new checkpoint change; no bounded source fix is made. Full R03 legacy/resource, broader generic/delegate/interface/stack-trace, startup/capacity/performance/memory, PureInterpreter qualification and independent full-stage review remain outside this focused batch and uncompleted. R03Accepted=false; H2Passed=false; pureInterpreterExpansionEnabled=false; fullLegacyRegressionAcceptance=false. **Exit: Local Validation → Primary Implementation; stop.** Final clean latest pushed heads and remote verification are recorded in the outgoing prompt and external PUBLICATION_RECEIPT.json; the later publication commit does not replace executed-source provenance. Any future validation requires a new exact pushed Primary handoff and unused root.

'''
ret=f'''## Current return — R03 batch E: two runtime issues require Primary Implementation

**ReturnRequired: 32 Passed, 4 Failed, 0 Blocked; focused seal Passed; runner exit 1.** Exactly one batch, {localtime}. All four fresh schema-2 build cells and all 754 selected Editor cases passed. All 19 fresh-process Players executed: 15 Passed, 4 Failed. No Local source change, retry, expectation/deadline/provenance/lifetime waiver occurred. Read [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md) and the immutable [E checkpoint]({checkpoint}) for the full tuple and evidence states.

R03-LD-001/002 repairs passed integrated validation in E; historical D results remain unchanged. The missing frozen M01 resource test remains NoCoverage. The following two new entries are the non-trivial implementation/measurement-contract issues returned to Primary.

### R03-LE-001 — Release warm interval gains one unattributed admission proof

**Symptom and exact reproduction performed.** Run the prescribed batch once from `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` with the exact SDK 8.0.318/Unity 2022.3.62f2 and four-source tuple in LOCAL_VALIDATION.md:

```text
{command}
```

Do not repeat E or relaunch its Players. Candidate Release C03-moved-slot, C04-old-AOT-guard and C05-direction-reversal each completes successful publication, reflection/delegate work and 10,000 allocations, but fails `Repeated warm proof work: admissionCacheMisses`. Independent Debug D02/D03 passes unchanged warm expectations.

**Exact evidence and excerpts.** Live root `{live}`; original `players/{{C03-moved-slot,C04-old-AOT-guard,C05-direction-reversal}}/{{request.json,raw.json,Player.log}}`, commands 0063/0064/0065, corresponding Failed cells and full build candidate-release receipt/apps. Before→after for C03/C04: admissionCacheMisses 17→18, admissionProofAttempts 17→18, admissionCacheHits 22→10022, baselineStateChecks 9→10009. C05 has the same values. Each adds admissionEntries 1 / admissionRetainedBytes 80 and genericContextChecks 5. No warm field/interface workspace or layout-check increase is observed. Debug D02/D03 retains misses/proofs 17→17 and the same +10,000 required hits/checks. Exact full snapshots, raw/request hashes, PID/run IDs, source lines and method/guard observations are bound in checkpoint `preflight/DIAGNOSTIC_FINDINGS.json`; original raw is also sealed/committed. Successful-verdict files are absent for failed cases; absence is not a Passed result.

**Likely root cause and why the design permits this failure.** `AssemblyShadowTypeResolver.cpp:849–922` uses a post-publication physical-class cache for every ResolveAllocation class, including unrelated BCL allocations. `AssemblyShadowAllocationProof.h:118/131` increments global miss/build counters; `AssemblyShadowObservationCounters.h:129–147` sums all thread slots. The verifier at `batch_contract.py` compares those broad process counters across two returned managed JSON observations as though zero cold work for the measured business class implied zero work for every class/thread. GetTypeResolutionInfo's native snapshot is taken before RuntimeApi converts it to a managed String, and the interval also includes harness work after the allocation loop. The extra completed entry with unchanged shadow-layout work most likely belongs to a cold allocation/proof in that broader interval. Exact class/site/thread attribution is not available. Do not claim the cause is proven marshalling, a specific BCL type, a race, or business-cache invalidation.

**Affected scope and implementation direction.** Release warm-certificate acceptance for method-slot, old-AOT guard and graph reversal is blocked; observed publication/business/method/guard semantics are retained separately. Primary should add a bounded, source-reviewed allocation-key/class/site/thread trace or equivalent attribution around exact snapshot boundaries, determine the extra entry, and implement a deliberate observer/witness boundary or cache correction accordingly. Retain mandatory per-allocation baseline checks and zero repeated target proof/layout/interface/field work. Do not blindly tolerate +1, extend warm-up until it passes, hide global counter deltas, or promote E after diagnosis. If the accepted measurement contract needs refinement, publish the design/expectation change explicitly in a new authoritative handoff.

**Remaining uncertainty and validation after repair.** No per-key proof event trace or later rerun exists; all three Release cases show the same +1, while both independent Debug witnesses show zero. A new unused source-bound batch must execute the Release and Debug witnesses, prove the diagnosed attribution/boundary with raw counter bindings, preserve active mapping/old-AOT guard and all original runtime semantics, and keep cold/unrelated work visible where applicable. E remains Failed for these cells.

### R03-LE-002 — private primitive append lacks physical proof before publication

**Symptom/reproduction.** The same single batch E's C07-private-primitive-append stages `primitive/R03Contract.dll` against the fresh AOT baseline and reaches Validate. The required success case returns code 16/state 8, does not Commit or invoke business code, and fails `Complete successful publication API chain`. No later business/warm operation was executed after that prerequisite failure.

**Evidence/excerpt.** `{live}/players/C07-private-primitive-append/{{request.json,raw.json,Player.log}}`, command 0067, cell `cells/C07-private-primitive-append.json`, exact baseline/target inventory hashes and schema-2 candidate-release receipt are preserved. Raw `steps` ends `{{"phase":"Validate","code":16,"state":8}}`; published=false; invocation/delegate/warm counts 0. Diagnostic/recovery detail: `R03Contract: NativeLayoutAdmissionV1: NativeLayoutNeedsNativeProof type(11:r03contract/3:R03/4:Node@0) ChangedLayoutUnavailableBeforePublication`; disposition RestartRequired, abortAllowed=false. Hash-bound excerpts and full raw/source bindings are in `preflight/DIAGNOSTIC_FINDINGS.json`.

**Root cause and affected boundary.** `AssemblyShadowTypeResolver.cpp:588–621` checks staged field shapes. If fields changed and either BaselineLayoutReady(PhysicalLayout(baseline)) or target->size_inited is false, it rejects at line 614 before CheckLayout's physical offset/size/private-storage comparison. The fixture generated from `R03EvolutionContractCases.cs` L03 appends a private Int64; the Editor result intentionally says NeedsNativeProof and never claims physical proof was executed. `player-cases.json` nevertheless expects successful publication/allocation at untouched startup. Current execution demonstrates that prepublication readiness contract is not met; it does not demonstrate incompatible physical offsets. Which side/readiness subcondition is unavailable in the raw schema. Type enumeration alone does not establish the required ready layout.

**Primary implementation direction.** Reconcile the staged physical-readiness path with the intended conservative R03 positive candidate. If private primitive append is supported in this bootstrap profile, establish and verify the necessary physical size/offset proof before Commit without old business initialization, baseline object allocation, or a weakened readiness guard. Add bounded readiness observations and real pinned native regression coverage. If that proof is intentionally unavailable in the conservative profile, resolve the design/supported-scope/fixture expectation explicitly in a new Primary source/handoff; do not silently relabel this existing success case as an expected rejection. Preserve code-16 fail-closed terminal behavior until positive proof exists.

**Uncertainty and required validation.** No live flag/offset probe was added and no new Player launched. A new source-bound batch must bind exact DLL bytes, expose the intended physical proof/readiness, preserve no old baseline business initialization, and verify the selected admission/Commit/allocation semantics. Related reference/value/interface/removal rejection guards, old-AOT guard and full required matrix must still execute. Full resource/deployment compatibility is outside this focused native safety witness.

### Custody and stop

Separate read-only audit authenticated 1,867 indexed live files / 1,868 exact archive members, all 36 cell/ledger identities, 79 clean command streams, 19 unique direct Player PIDs/run IDs and 3,081 unchanged prior custody bindings. The immutable E checkpoint retains every indexed file and the unchanged original seal. Live archive {(R/'evidence.tar.gz').stat().st_size:,} bytes is preserved; three exact committed byte parts and reconstruction audit retain its SHA-256 `{hashes['evidence.tar.gz']}`. No Local source fix, retry, pin/scope/expectation/cleanup change or failed-cell promotion occurred.

R03Accepted=false; H2Passed=false; PureInterpreter expansion disabled; fullLegacyRegressionAcceptance=false. Frozen M01 resource coverage remains NoCoverage; broader full-stage work is not waived. **Local Validation → Primary Implementation; stop.** A new exact pushed Primary handoff and unused root are required before further validation.

'''
preservation={}
for name,section in [('LOCAL_VALIDATION.md',local),('RETURN_TO_WEB.md',ret)]:
 p=D/'Docs/AssemblyShadow/Handoff'/name;old=p.read_text();first,tail=old.split('\n',1);tail=tail.lstrip('\n');assert tail.startswith('## Current');tail=tail.replace('## Current','## Historical',1);p.write_text(first+'\n\n'+section+tail);preservation[name]={'originalSha256':hashlib.sha256(old.encode()).hexdigest(),'newSha256':sha(p),'preservation':'Previous report body retained except D Current-to-Historical heading; E prepended'}
(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps(preservation,indent=2)+'\n')
readme=f'''# R03 Local batch E — immutable ReturnRequired checkpoint

**32 Passed / 4 Failed / 0 Blocked; focused seal Passed; one invocation, exit 1.** {localtime}; UTC {utctime}. Executed demo `d51483dc1a11007fe1db2ee456a8b0444061389c`, tested source anchor `979abd80b673e690c5f82819ed194200f8d2e536`. The later publication commit does not replace executed-source provenance.

Read [LOCAL_VALIDATION.md](../../../../Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB.md](../../../../Handoff/RETURN_TO_WEB.md). R03Accepted=false; H2Passed=false; PureInterpreter expansion disabled; fullLegacyRegressionAcceptance=false. Exit: Local Validation → Primary Implementation; stop.

- [LOCAL_BATCH_RESULT.json](batch/LOCAL_BATCH_RESULT.json), [BATCH_EXECUTION.json](batch/BATCH_EXECUTION.json), all 36 cells, [evidence-index.json](batch/evidence-index.json) and [seal-receipt.json](batch/seal-receipt.json) preserve original states/bytes. All 1,867 indexed files are committed individually; all 1,868 archive members independently authenticated.
- [ARCHIVE_TRANSPORT.json](ARCHIVE_TRANSPORT.json) binds three ordered exact byte parts for the unchanged {(R/'evidence.tar.gz').stat().st_size:,}-byte sealed archive, SHA-256 `{hashes['evidence.tar.gz']}`. Original `evidence.tar.gz` stays at the live root. [REASSEMBLE_EVIDENCE.py](REASSEMBLE_EVIDENCE.py) reconstructs only into a new caller-specified absolute destination and verifies each part/whole. Transport is separate from the runner seal; no re-compression or member omission.
- Four new native-role apps, all schema-2 build receipts, actual installed-root `nativeBinding` records, native/config/source inventories and build logs are preserved in `batch/builds/` and build cell receipts. Candidate installedAfter count 966, reference 965; physical source tuple/app inventories/ARM64 checks Passed. Live generated receipt copies are not deleted or treated as authoritative installed roots.
- [editor-scope.json](batch/editor-scope.json), [editor-verification.json](batch/editor-verification.json) and [editor-results.xml](batch/editor-results.xml) bind 754 selected exact cases, all Passed with zero skips. The single frozen M01 asset test is excluded/NoCoverage, not Passed. Full legacy/resource acceptance remains false.
- All 19 fresh-process Player requests/raw/logs and 15 successful verification receipts are in `batch/players/`. Three Release cases fail warm-counter expectations; one private primitive append fails the expected successful publication chain. Four failed successful-verdict files are unavailable after the unchanged verifier throw. Original recording exit 0 does not imply a Passed cell.
- [INTEGRATED_OBSERVATIONS.json](preflight/INTEGRATED_OBSERVATIONS.json) and [DIAGNOSTIC_FINDINGS.json](preflight/DIAGNOSTIC_FINDINGS.json) bind exact fresh schema-2/native/Editor/Player observations, selected counter deltas, identities/hashes, two actionable Primary issues and explicit uncertainty. Native method and old-AOT guard observations in Failed cells do not promote them.
- [POSTRUN_AUTHENTICATION.json](preflight/POSTRUN_AUTHENTICATION.json) binds all sealed/live evidence, 79 command streams, seven authenticated Unity completions, compiler/fixture/API inputs and 3,081 prior custody files unchanged. Only named controls 0048/0050/0055 preserve expected nonzero compiler exits. Every original lifetime flag is retained.
- [RETAINED_LIVE_ROOTS.json](preflight/RETAINED_LIVE_ROOTS.json) retains six isolated project/cache roots, three detached references and compiled/intermediate file hashes. Excluded Library/HybridCLRData/native/generated roots stay live. Source snapshots and diagnostic excerpts bind the executed code. [MANIFEST.sha256](MANIFEST.sha256) authenticates checkpoint files except itself. Batch-only whitespace attributes preserve immutable generated/output bytes.

Live root `{live}`; preflight `{P}`. No previous root/app was reused. No Local implementation, source/pin/scope/expectation/deadline/lifetime change, raw-evidence rewrite or retry occurred. Earlier A–D/R02/H1 evidence remains unchanged. Full-stage obligations and missing M01 coverage remain open.
'''
(C/'README.md').write_text(readme);shutil.copy2(P/'write-reports.py',C/'preflight/write-reports.py')
print('Updated two Local reports, preserved D and earlier bodies, and wrote E checkpoint README')
