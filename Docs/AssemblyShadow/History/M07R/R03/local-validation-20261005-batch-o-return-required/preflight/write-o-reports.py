"""Write only Local-owned factual reports after sealed O evidence authentication."""
import pathlib,json,hashlib,datetime,zoneinfo,subprocess,collections
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261005O-ln-closure';R=P.parent/'R03LocalBatch-20261005O-ln-closure'
load=lambda p:json.loads(pathlib.Path(p).read_text());sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r=load(R/'LOCAL_BATCH_RESULT.json');a=load(P/'POSTRUN_AUTHENTICATION.json');run=load(P/'runner-exit.json');env=load(P/'environment.json');issues=load(P/'PRIMARY_ISSUES.json');obs=load(P/'INTEGRATED_OBSERVATIONS.json');identity=load(P/'LAYOUT_IDENTITY_AUDIT.json');completion=load(P/'COMPLETION_RUNTIME_AUDIT.json');ln=load(P/'LN_REPAIR_AUDIT.json');li=load(P/'LI_CONTRACT_AUDIT.json');rb=load(P/'RESOURCE_BUILD_RECOVERY_AUDIT.json')
counts=dict(collections.Counter(c['result'] for c in r['cells']));assert a['status']=='Passed' and counts==a['counts'];cells={c['id']:c for c in r['cells']};assert len(cells)==90
assert set(issues['allFailedCellsCovered'])=={c['id'] for c in r['cells'] if c['result']=='Failed'}
C=D/('Docs/AssemblyShadow/History/M07R/R03/local-validation-20261005-batch-o-'+('evidence-ready' if r['result']=='EvidenceReadyForPrimaryReview' else 'return-required'));assert C.exists();rel='../History/M07R/R03/'+C.name
status=', '.join(str(counts.get(s,0))+' '+s for s in ['Passed','Failed','Blocked']);tz=zoneinfo.ZoneInfo('America/Los_Angeles');times=' → '.join(datetime.datetime.fromisoformat(run[k]).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S %Z') for k in ['startedUtc','endedUtc']);command=' '.join(run['command']);history={}
def save(name,title,body):
 q=D/'Docs/AssemblyShadow/Handoff'/name;old=subprocess.check_output(['git','-C',str(D),'show','HEAD:Docs/AssemblyShadow/Handoff/'+name],text=True);assert q.read_text()==old;tail=old.split('\n',1)[1].lstrip('\n').replace('## Current','## Historical',1);q.write_text(title+'\n\n'+body.strip()+'\n\n'+tail);history[name]={'originalSha256':hashlib.sha256(old.encode()).hexdigest(),'historicalBodySha256':hashlib.sha256(tail.encode()).hexdigest(),'newSha256':sha(q),'preservation':'Full previous body retained except first Current heading changed to Historical'}
repos='\n'.join('| `'+str(W/n)+'` | `codex/assembly-shadow-r01b-h1` | `'+r['repositories'][n]+'` |' for n in ['hybridclr_demo','hybridclr','hybridclr_unity','il2cpp_plus']);celltable='\n'.join('| `'+c['id']+'` | '+c['result']+' |' for c in r['cells']);hashes='\n'.join('| `'+n+'` | `'+h+'` |' for n,h in a['topLevelHashes'].items());focused='\n'.join('| '+b['role']+' | `'+b['receiptSha256']+'` | `'+b['binding']['sourcePinsSha256']+'` | '+str(b['binding']['verifiedNativeFiles'])+' |' for b in obs['builds']);resources='\n'.join('| '+b['role']+' | `'+b['playerReceiptSha256']+'` | `'+b['buildGuid']+'` | `'+b['nativeLibrarySha256']+'` |' for b in rb['builds']);sidecars='\n'.join('| '+v['patchId']+' | '+v['fullVerifierState']+' | `'+v['sidecar']['sha256']+'` | '+str(v['checks']['linkedImages'])+'/'+str(v['checks']['compilerImages'])+' | '+str(v['checks']['mappedDeclarations'])+' |' for v in identity['freshReports']);repair='\n'.join('| '+v['id']+' | '+v['state']+' |' for v in ln['checks']);editor='\n'.join('| '+v['folder']+' | '+str(v.get('expectedCount',v['count']))+' | '+v.get('state','Passed')+' | '+v.get('execution','Executed')+' | '+v.get('xmlSha256',v.get('xmlState','Unavailable'))+' |' for v in li['fullEditors']);new='; '.join(i['id']+': '+i['symptom'] for i in issues['issues']) or 'No new non-trivial defect recorded; Primary reconciliation and independent full-stage review remain required.'
local=f'''## Current run — R03 completion batch O, 2026-10-05 PDT

**{r['result']}; 90 cells: {status}; sealStatus={r['sealStatus']}; runner exit {run['exitCode']}. Exit: Local Validation → Primary Implementation.** One prescribed invocation, PID {run['pid']}, {times}; UTC {run['startedUtc']} → {run['endedUtc']}. No retry, old-app/root reuse, source fix, scope reduction, hash rebinding, pin/package substitution or timeout/cleanup/warm-up/lease adjustment.

Actual direct Player processes={completion['actualDirectPlayerCommands']}; focused verification receipts={completion['focusedVerificationReceipts']}; independent resource/measurement/early result rechecks={completion['replayedResourceMeasurementEarlyPlayers']}. Full Editor states, fresh production integration and all original cell verdicts appear below. New Primary issues: {new}

### Authority and environment

Every owning checkout was independently clean at the exact handoff path/branch/commit, canonical origin and matching remote head. Demo/package safely fast-forwarded; native/IL2CPP unchanged. Executable/CI anchor `fefe846b1209d18a96c432ed0ca2222f16cda976` is an ancestor; all later transport changes are Docs-only. Both R03 pin manifests agree. Absolute paths, top-level/branch/HEAD/status/remotes/worktrees/submodules, fetch/FF operations and command clocks are retained in [preflight]({rel}/preflight). Ordinary primary/control checkouts were unused. All {a['priorCustodyFilesUnchanged']} prior custody bindings authenticated; N and every earlier original result/evidence state remain unchanged.

| Repository path | Branch | Executed source commit |
| --- | --- | --- |
{repos}

Unity 2022.3.62f2 / StandaloneOSX arm64 at `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`; .NET SDK8.0.318/runtime8.0.21 from SDK-only `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`. No Unity6000 Editor launched. macOS26.5.2(25F84), Python3.14.6, PowerShell7.6.3, Apple clang21/macOS SDK26.5. Exact versions/argv/environment/start/end/PID/exit are in environment.json, runner receipts and commands/*/command.json. Unity mscorlib SHA `d89d5124cafb873b34c2eac68d2ece41d14fec10999baf0e4620276dff54ab83`. No existing Editor at entry; gate helper Off; exact effective model unavailable from authoritative host, no inferred model or independent full-stage review claim.

```text
{command}
```

### LN repairs and actual Editor scope

The actual host unit suites are recorded with test counts and command/stream hashes in POSTRUN_AUTHENTICATION.json. Static qualification32, baseline/candidate graph9+9, admission35, fixture33/pinned consumer33 and complete helper/API compiler checks retain their individual original receipts.

[LN_REPAIR_AUDIT.json]({rel}/preflight/LN_REPAIR_AUDIT.json) independently authenticates the real 13-file package delta/unchanged catalogs, 15 fresh supervised reference-binding cases and context diagnosis, explicit pinned native-codec authority, and original fresh sidecar verification. Historical compiler replay retains ReusedAuditedLocalNCompilerInputs; it does not reclassify N or grant new runtime/qualification authority. Fresh production qualification cell={cells['production-entry-integration']['result']}; source binding cell={cells['resource-input-binding']['result']}.

| Repaired boundary | Factual audit state |
| --- | --- |
{repair}

| Full Editor roster | Required cases | Original state | Execution | XML SHA/state |
| --- | --- | --- | --- | --- |
{editor}

The early 18-method Test Runner preflight is independently authenticated in [LI_CONTRACT_AUDIT.json]({rel}/preflight/LI_CONTRACT_AUDIT.json), with constructor12/source-pin10 controls and unchanged inputs. Full rosters require exact names and zero skips/inconclusive; names-only source catalog is not a reused test verdict. Focused M01 exclusion remains NoCoverage, while the separate resource roster's asset/GUID test and actual resource Player behavior retain their own evidence. Missing XML/results remain Unavailable/NotRun.

### Builds, runtime and restoration

[POSTRUN_AUTHENTICATION.json]({rel}/preflight/POSTRUN_AUTHENTICATION.json) authenticates the seal/ledger/index/archive, command streams, process supervision, fixture/consumer/API inputs, four focused schema-2 builds and 23 focused Player receipts. Expected-negative compiler exits are distinct from successful product builds. Natural producer diagnostics retain all four contaminated unisolatedWarmCertificate=Failed; diagnostic attribution does not promote them. Six strict warm witnesses, C07 positive physical proof and five rejection observations retain their actual source-bound verdicts in [producer audit]({rel}/preflight/PRODUCER_RUNTIME_AUDIT.json) and [rejection audit]({rel}/preflight/REJECTION_RUNTIME_AUDIT.json).

| Focused role | Receipt SHA-256 | Source-pin SHA-256 | Verified native files |
| --- | --- | --- | --- |
{focused}

Focused build GUID is unavailable in those four receipts; no GUID equivalence inferred. Reference Release uses the explicitly bound historical native `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` / IL2CPP `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c` with current source overlay/package. Historical source reuse is separate from old-app/runtime reuse. [RETAINED_LIVE_ROOTS.json]({rel}/preflight/RETAINED_LIVE_ROOTS.json) records exact detached roots, isolated projects, Libraries and HybridCLRData.

| Fresh original-resource role | Receipt SHA-256 | Build GUID | Native library SHA-256 |
| --- | --- | --- | --- |
{resources}

[RESOURCE_BUILD_RECOVERY_AUDIT.json]({rel}/preflight/RESOURCE_BUILD_RECOVERY_AUDIT.json) independently binds both current linked snapshots/reflection/native inventory/25-site proofs and P05 restoration. P05 compile={cells['resource-p05-compile']['result']}, restore={cells['resource-p05-restore']['result']}, finalize={cells['resource-p05-finalize']['result']}. Original settings SHA `{rb['restoration']['originalSha256']}` = final SHA `{rb['restoration']['finalSettingsSha256']}`; separately retained Unity-reserialized bytes SHA `{rb['restoration']['unityReserializedBytesSha256']}`. Production/wrapper/state receipts remain distinct.

### Fresh layout and remaining completion evidence

[LAYOUT_IDENTITY_AUDIT.json]({rel}/preflight/LAYOUT_IDENTITY_AUDIT.json) distinguishes historical M input replay from all five current schema-2 report rechecks. Fresh aggregate={identity['freshFiveReportAuditState']}; production verification={identity['productionVerificationState']}. Full identities, hashes/MVIDs, captured inventories/facades/forwarding paths and original load order remain guarded. Nominal reports preserve nativeProofExecuted=false, runtimeMustRevalidate=true, allocationProofStillRequired=true and disabled expansion; they alone do not establish physical/native/runtime acceptance. Counts in any Failed verifier row are captured observations only.

| Current fixture | Full verifier | Sidecar SHA-256 | Linked/compiler images | Mapped declarations |
| --- | --- | --- | --- | --- |
{sidecars}

[COMPILER_POLICY_AUDIT.json]({rel}/preflight/COMPILER_POLICY_AUDIT.json), [FIXED_IMAGE_AUDIT.json]({rel}/preflight/FIXED_IMAGE_AUDIT.json) and [CAPABILITY_CONTRACT_AUDIT.json]({rel}/preflight/CAPABILITY_CONTRACT_AUDIT.json) preserve Q22's two byte-identical reports/four unchanged input hashes, immutable compiler inputs/current25-site16-control proof, frozen M00 input materialization and actual inventory/capability guards. Frozen input is reused-audited, not a new M00 compilation or old runtime result.

[COMPLETION_RUNTIME_AUDIT.json]({rel}/preflight/COMPLETION_RUNTIME_AUDIT.json) records the original Failed production integration and rechecks independently meaningful resource graph, OFF resource and negative startup contracts. Failed prerequisites retain NotRun audit states. [FAILED_CONTRACT_REPRODUCTION.json]({rel}/preflight/FAILED_CONTRACT_REPRODUCTION.json) reproduces all 29 original runtime failures offline with exact errors and tracebacks, actual PID/command/raw hashes and no new launches or guard changes. All 12 original R00 raw contracts separately Passed their read-only recheck; supplements and overall measurement cells remain Failed. All 59 fresh Player commands and indexed raw files are present; 30 final Player verifications Passed and 29 Failed. The completion audit coverage flag is false because complete successful semantic coverage was not achieved, not because custody evidence is missing. Audit states={completion['readOnlyAuditStates']}. Actual fresh process counts and raw/request/receipt/build GUID/source hashes remain recorded individually; expected negative exits remain separate. Measurement-summary={cells['measurement-summary']['result']}. Protocol observations do not approve a production performance SLA, noise/overhead threshold, R02 deferred CPU risk or H1 RSS risk.

### Custody and publication

Live `{R}` and external preflight `{P}` remain retained, including every receipt-referenced live project/cache/source/build root. [Immutable O checkpoint]({rel}/README.md) preserves {a['indexedLiveFiles']} indexed files/{a['archiveMembers']} unique archive members, source snapshots and independent audits. Original archive/index/seal bytes are unchanged; exact ordered parts reconstruct at a new path. Previous report bodies are fully retained except their first Current heading becomes Historical.

| Original artifact | SHA-256 |
| --- | --- |
{hashes}

Only two Local reports and the new O checkpoint are owned publication changes. Manifests, JSON, local links, raw whitespace provenance and staged Git bytes are checked before commit. Final clean paths/branches/latest pushed heads and remote identities are recorded in `{P}/PUBLICATION_RECEIPT.json` and the short handoff; executed source `25a9dbce977247d83ef1b1c0411a663d8dda4456` remains distinct from the later publication commit.

**R03Accepted=false; H2Passed=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; PureInterpreter expansion disabled. No performance SLA or Human Review Gate readiness. Return to Primary for reconciliation/independent full-stage review and any recorded defects, then stop.**

### All 90 original cells

| Cell | Original state |
| --- | --- |
{celltable}
'''
save('LOCAL_VALIDATION.md','# Local Validation report',local)
entries=[]
for issue in issues['issues']:
 steps='\n'.join(str(i+1)+'. '+s for i,s in enumerate(issue['reproduction']));ev='\n'.join('- `'+e['path']+'`, SHA-256 `'+e['sha256']+'`' for e in issue['evidence']);entries.append(f"""### {issue['id']} — {issue['title']}

**Symptom.** {issue['symptom']}

**Exact reproduction already performed.**

{steps}

**Evidence and excerpts.**

{ev}

{issue['relevantExcerpt']}

**Most likely root cause.** {issue['rootCause']}

**Why permitted / affected scope.** {issue['whyDesignAllowedIt']} {issue['affectedScope']}

**Recommended Primary direction.** {issue['recommendedDirection']}

**Remaining uncertainty.** {issue['remainingUncertainty']}

**Validation after repair.** {issue['validationAfterRepair']}

No Local source fix or phase/batch retry.
""")
ret=f'''## Current return — R03 completion batch O

**{r['result']}; 90 cells: {status}; seal {r['sealStatus']}; one invocation PID {run['pid']}, {times}.** Read [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md), [O checkpoint]({rel}/README.md), [PRIMARY_ISSUES.json]({rel}/preflight/PRIMARY_ISSUES.json), [LN repairs]({rel}/preflight/LN_REPAIR_AUDIT.json) and [completion audit]({rel}/preflight/COMPLETION_RUNTIME_AUDIT.json). Preserve N and all earlier evidence/results unchanged.

Exact source paths/commits/tools and command are recorded in LOCAL_VALIDATION.md. Actual direct Players={completion['actualDirectPlayerCommands']}; full Editor and production/runtime verdicts retain their own states. No historical replay or focused test is full-stage acceptance. No new non-trivial defect is manufactured merely to acknowledge synchronization or a passing focused result.

{chr(10).join(entries) if entries else 'No new non-trivial Primary defect was discovered in this assigned batch. Primary must reconcile the fresh evidence and complete independent full-stage review; no approval is inferred.'}

R03Accepted=false; H2Passed=false; qualificationApproved=false; PureInterpreter expansion disabled. Four contaminated unisolated warm certificates remain Failed. Executed source `25a9dbce977247d83ef1b1c0411a663d8dda4456`; publication HEAD is transport authority only and is recorded externally/in the final handoff. **Local Validation → Primary Implementation. Stop.**
'''
save('RETURN_TO_WEB.md','# Local Validation → Primary Implementation',ret)
(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps(history,indent=2)+'\n')
(C/'README.md').write_text(f'''# Immutable R03 completion batch O checkpoint

{r['result']}; 90 cells: {status}; seal {r['sealStatus']}; one invocation, {times}. Executed demo `25a9dbce977247d83ef1b1c0411a663d8dda4456`; actual source tuple and evidence states are preserved in receipts.

Read [LOCAL_VALIDATION](../../../../Handoff/LOCAL_VALIDATION.md), [RETURN_TO_WEB](../../../../Handoff/RETURN_TO_WEB.md), [result](batch/LOCAL_BATCH_RESULT.json), [ledger](batch/BATCH_EXECUTION.json), [index](batch/evidence-index.json), [seal](batch/seal-receipt.json), [LN repairs](preflight/LN_REPAIR_AUDIT.json), [completion audit](preflight/COMPLETION_RUNTIME_AUDIT.json), [Primary issues](preflight/PRIMARY_ISSUES.json), [archive transport](ARCHIVE_TRANSPORT.json) and [manifest](MANIFEST.sha256).

Live root `{R}` and preflight `{P}` remain retained. REASSEMBLE_EVIDENCE.py reconstructs exact original archive bytes at a new absolute unused path. Source/generated/build/native/fixture/result provenance remains distinct. No acceptance/qualification/expansion/Human Gate approval. Return to Primary and stop.
''')
print('O Local reports written; previous bodies preserved',counts)
