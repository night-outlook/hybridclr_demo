"""Local-owned N reports, preserving all prior report bodies and evidence states."""
import pathlib,json,hashlib,subprocess,datetime,zoneinfo,collections
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261005N-identity';R=P.parent/'R03LocalBatch-20261005N-identity'
load=lambda p:json.loads(pathlib.Path(p).read_text());sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r=load(R/'LOCAL_BATCH_RESULT.json');a=load(P/'POSTRUN_AUTHENTICATION.json');run=load(P/'runner-exit.json');identity=load(P/'LAYOUT_IDENTITY_AUDIT.json');issues=load(P/'PRIMARY_ISSUES.json');obs=load(P/'INTEGRATED_OBSERVATIONS.json');completion=load(P/'COMPLETION_RUNTIME_AUDIT.json');rb=load(P/'RESOURCE_BUILD_RECOVERY_AUDIT.json');li=load(P/'LI_CONTRACT_AUDIT.json');cp=load(P/'COMPILER_POLICY_AUDIT.json');env=load(P/'environment.json');diag=load(P/'EDITOR_SCOPE_DIAGNOSIS.json')
C=D/('Docs/AssemblyShadow/History/M07R/R03/local-validation-20261005-batch-n-'+('evidence-ready' if r['result']=='EvidenceReadyForPrimaryReview' else 'return-required'));rel='../History/M07R/R03/'+C.name;history={};cells={c['id']:c for c in r['cells']};counts=dict(collections.Counter(c['result'] for c in r['cells']));assert counts==a['counts'] and len(cells)==90 and a['status']=='Passed';assert set(issues['allFailedCellsCovered'])=={c['id'] for c in r['cells'] if c['result']=='Failed'}
tz=zoneinfo.ZoneInfo('America/Los_Angeles');times=' → '.join(datetime.datetime.fromisoformat(run[k]).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S %Z') for k in ['startedUtc','endedUtc']);command=' '.join(run['command']);statusline=', '.join(str(counts.get(state,0))+' '+state for state in ['Passed','Failed','Blocked']);direct=completion['actualDirectPlayerCommands'];failed='; '.join(c['id']+': '+c['error'] for c in r['cells'] if c['result']=='Failed')
def save(name,title,body):
 q=D/'Docs/AssemblyShadow/Handoff'/name;old=subprocess.check_output(['git','-C',str(D),'show','HEAD:Docs/AssemblyShadow/Handoff/'+name],text=True);assert q.read_text()==old
 tail=old.split('\n',1)[1].lstrip('\n').replace('## Current','## Historical',1);q.write_text(title+'\n\n'+body.strip()+'\n\n'+tail);history[name]={'originalSha256':hashlib.sha256(old.encode()).hexdigest(),'historicalBodySha256':hashlib.sha256(tail.encode()).hexdigest(),'newSha256':sha(q),'preservation':'Previous full report body unchanged except first Current heading changed to Historical'}
repos='\n'.join('| `'+str(W/n)+'` | `codex/assembly-shadow-r01b-h1` | `'+r['repositories'][n]+'` |' for n in ['hybridclr_demo','hybridclr','hybridclr_unity','il2cpp_plus']);hashes='\n'.join('| `'+n+'` | `'+h+'` |' for n,h in a['topLevelHashes'].items());celltable='\n'.join('| `'+c['id']+'` | '+c['result']+' |' for c in r['cells']);focusedbuilds='\n'.join('| '+b['role']+' | `'+b['receiptSha256']+'` | `'+b['binding']['sourcePinsSha256']+'` | '+str(b['binding']['verifiedNativeFiles'])+' |' for b in obs['builds']);resourcebuilds='\n'.join('| '+b['role']+' | `'+b['playerReceiptSha256']+'` | `'+b['buildGuid']+'` | `'+b['nativeLibrarySha256']+'` |' for b in rb['builds']);reports='\n'.join('| '+row['patchId']+' | `'+row['sidecar']['sha256']+'` | '+str(row['checks']['linkedImages'])+' / '+str(row['checks']['compilerImages'])+' | '+str(row['checks']['mappedDeclarations'])+' |' for row in identity['freshReports']);editors='\n'.join('| '+e['folder']+' | '+str(e.get('expectedCount',e.get('count')))+' | '+e.get('state','Passed')+' | '+e.get('execution','Executed')+' | '+e.get('xmlState',e.get('xmlSha256','Unavailable'))+' |' for e in li['fullEditors']);additional='\n'.join('- `'+n+'`' for n in diag['additionalFiles']);resourcesExecuted=completion['replayedResourceMeasurementEarlyPlayers'];runtimeStates=str(completion['readOnlyAuditStates'])
local=f'''## Current run — R03 completion batch N, 2026-10-05 PDT: factual return to Primary

**{r['result']}; 90 cells: {statusline}; sealStatus={r['sealStatus']}; runner exit {run['exitCode']}. Exit A: Local Validation → Primary Implementation.** One fresh invocation PID {run['pid']}, {times}; UTC {run['startedUtc']} → {run['endedUtc']}. No retry, earlier app/root reuse, source fix, pin/scope/expectation/timeout/cleanup/lease changes.

Fresh P05 compile={cells['resource-p05-compile']['result']}, restoration={cells['resource-p05-restore']['result']}, finalization={cells['resource-p05-finalize']['result']}, production entry={cells['production-entry-integration']['result']}, resource-input-binding={cells['resource-input-binding']['result']}. Identity audit: five fresh reports={identity['freshFiveReportAuditState']}; production verification={identity['productionVerificationState']}. All six fresh build roles and 23 focused Players Passed. Actual direct Player processes={direct}; independently replayed resource/measurement/early results={resourcesExecuted}. Full Editor cells Failed before scope/XML creation or Test Runner launch, because the package-delta review omitted five new production files; the separate early 18-method Editor preflight Passed. Full-roster tests are NotRun with XML Unavailable, not failing NUnit cases. R03-LN-001/002/003 require Primary; independently observed LN-004 also requires repair. Thirty-six planned resource/measurement/early Players remain Blocked and were not launched.

### Exact authority, environment and invocation

All four owning checkouts were independently clean at the exact handoff paths/branches/commits with canonical origins and matching remote heads. Only demo and package safely fast-forwarded; native/IL2CPP unchanged. Anchor `7e1060ff5723efe365c60bc052bbbcb117d62dfa` is an ancestor; final transport delta is Docs-only. Both R03 pin files agree. Git top-level/branch/HEAD/status/remotes/worktrees/submodule checks, package/native/source pins and before/after operations are retained in [preflight]({rel}/preflight). Ordinary primary/control checkouts were unused. All {a['priorCustodyFilesUnchanged']} earlier custody bindings authenticated before/after N; M and earlier bytes/results remain unchanged.

| Actual repository path | Branch | Exact executed source commit |
| --- | --- | --- |
{repos}

Unity 2022.3.62f2 / StandaloneOSX arm64 at `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`; macOS26.5.2 (25F84), Python3.14.6, PowerShell7.6.3, Apple clang21/macOS SDK26.5; .NET SDK8.0.318/runtime8.0.21. SDK-only root `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`; no Unity6000 Editor was launched. Pinned mscorlib SHA `d89d5124cafb873b34c2eac68d2ece41d14fec10999baf0e4620276dff54ab83`. Exact versions, argv/environment/PID/start/end/exit and per-command hashes/outputs are in environment.json, runner receipts and commands/*/command.json. No existing Editor at entry; gate helper Off; effective model unavailable from host, no guess or independent full-stage gate claim.

```text
{command}
```

### Factual validation states

| Scope | Factual result and limit |
| --- | --- |
| Host prerequisites | Passed 229 completion Python,183 retained verifier,33 identity,32 qualification,12 constructor,20 capability,10 fixed-image cases; baseline/candidate graph9+9 and admission35 |
| Identity historical replay | Passed on exact immutable M inputs:56 linked/214 compiler images,43 raw ParentChanged rows,53 resolved NeedsNativeProof rows,18 mapped declarations. Basis remains ReusedAuditedLocalMLayoutInputs; no historical runtime result promoted |
| Q22 | Passed two byte-identical reports from same four prepared DLLs; before/after input hashes unchanged. qualificationApproved=false |
| Fixture/lifetime/API | Passed33 fixture/33 pinned consumer checks, actual valid/invalid Editor probes and complete helper/API compiler prerequisite. Expected-negative compiler exits remain separate |
| Focused builds/Players | Four native roles and23 fresh unique PIDs Passed;6 strict warm witnesses,C07 positive physical proof and5 non-mutating rejection observations retaining terminal16 Passed |
| Natural producer controls | Diagnostic attribution Passed,4 actual identified ArrayPool Gen2 admissions. All4 contaminated unisolatedWarmCertificate=Failed retained; no counter subtraction/acceptance promotion |
| Resource compiler/policy/linked | Original full gate,25 current raw sites/16 controls,immutable inputs,2 linked25-site proofs and exact native inventory Passed |
| P05 compile/restore/finalize | {cells['resource-p05-compile']['result']} / {cells['resource-p05-restore']['result']} / {cells['resource-p05-finalize']['result']}; exact settings byte recovery independently authenticated |
| Five current schema-2 sidecars | {identity['freshFiveReportAuditState']} in independent complete verification (assembly-name casing); raw reports Available, production verification Unavailable after earlier codec-path failure; nativeProofExecuted=false,runtimeMustRevalidate=true,allocationProofStillRequired=true,expansion disabled |
| Production/resource graph | production-entry={cells['production-entry-integration']['result']}; input-binding={cells['resource-input-binding']['result']}; full resource-contracts={cells['resource-contracts']['result']} |
| Resource/measurement/early | {resourcesExecuted} original processes reverified; read-only semantic states={runtimeStates}; measurement-summary={cells['measurement-summary']['result']}. Protocol observations do not approve a performance SLA |
| Full Editor754/755 | Failed source-scope prerequisites;0 full-roster tests executed; XML/scope/log Unavailable. Early18 actual methods Passed independently |
| Seal/custody | {r['sealStatus']}; {a['indexedLiveFiles']} indexed files/{a['archiveMembers']} unique archive members authenticated. External early audit attempts needing the final ledger were Unavailable until post-run; no compiler/Editor/Player launched by those attempts |

| Actual full Editor scope | Expected cases | Original cell | Execution | XML |
| --- | --- | --- | --- | --- |
{editors}

Focused M01 planned exclusion remains NoCoverage. The resource full755 roster did not execute its M01 asset/GUID Editor case; any source/resource/Player coverage is separately recorded. Expected name catalog bytes are authenticated, never reused as test results. No missing XML becomes an empty or successful test suite.

### Fresh build/source provenance

Focused receipts `{R}/builds/<role>/build-receipt.json` bind source manifests/installed native roots/output inventories. Build GUID unavailable in these4 receipts; no GUID equivalence claim. Reference Release deliberately uses authenticated historical native `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` / IL2CPP `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c` with separately bound current overlay/package. Reference source reuse is distinct from earlier app/runtime reuse. [RETAINED_LIVE_ROOTS.json]({rel}/preflight/RETAINED_LIVE_ROOTS.json) records exact detached sources and cache/build roots.

| Focused role | Receipt SHA-256 | Source-pin SHA-256 | Verified native files |
| --- | --- | --- | --- |
{focusedbuilds}

| Resource role | Receipt SHA-256 | Build GUID | Native library SHA-256 |
| --- | --- | --- | --- |
{resourcebuilds}

[RESOURCE_BUILD_RECOVERY_AUDIT.json]({rel}/preflight/RESOURCE_BUILD_RECOVERY_AUDIT.json) independently verifies both linked snapshots/reflection/raw25-site proofs/native metadata/source inventory. Original settings SHA `{rb['restoration']['originalSha256']}` = final SHA `{rb['restoration']['finalSettingsSha256']}`; separately retained Unity-reserialized bytes SHA `{rb['restoration']['unityReserializedBytesSha256']}`. Production/wrapper/state receipts remain distinct; restoration is not inferred from a build status.

### Fresh identity proof and limits

[LAYOUT_IDENTITY_AUDIT.json]({rel}/preflight/LAYOUT_IDENTITY_AUDIT.json) authenticates replay inputs/results/comparison/synthetic DLLs separately from current schema-2 reports. Five current sidecar files and their indexed hashes are Available. Independent unchanged full verification fails on assembly-name casing for each report; the original graph did not reach this verifier after the codec-path failure. The table below lists authenticated captured counts only, not successful complete verification. Complete nominal binding/native/linked runtime acceptance cannot be inferred from report presence or factory editorAccepted=true. No qualifier stripping or same-name alias was used. Nominal identity proof does not certify native offsets/allocation; original native/runtime witnesses remain required.

| Current fixture | Sidecar SHA-256 | Linked/compiler images | Mapped declarations |
| --- | --- | --- | --- |
{reports}

[COMPILER_POLICY_AUDIT.json]({rel}/preflight/COMPILER_POLICY_AUDIT.json), [FIXED_IMAGE_AUDIT.json]({rel}/preflight/FIXED_IMAGE_AUDIT.json) and [CAPABILITY_CONTRACT_AUDIT.json]({rel}/preflight/CAPABILITY_CONTRACT_AUDIT.json) authenticate unchanged policy closure, actual current25-site/16-control proof,10 image/10 actual capability controls and all immutable configuration. Frozen M00 image reuse remains reused-audited input; not a new M00 compilation or historical Player-result reuse. [COMPLETION_RUNTIME_AUDIT.json]({rel}/preflight/COMPLETION_RUNTIME_AUDIT.json) records 23 direct Players and zero resource/measurement/early result replays, plus exact restoration and original Blocked/NotRun states. Those 36 downstream Players produced no fresh requests/raw results or measurements. Observations do not establish releasePerformanceAcceptance or waive R02 CPU/H1 RSS risks.

### New Primary issues and custody

R03-LN-001: actual package delta has13 files but the reviewed scope set has8; the additional5 are the intended identity repair. The guard refuses before full Test Runner invocation. Host scope tests mock Git diff from the same reviewed set and therefore miss this real-pin mismatch. [RETURN_TO_WEB.md](RETURN_TO_WEB.md) and [PRIMARY_ISSUES.json]({rel}/preflight/PRIMARY_ISSUES.json) contain exact reproduction/source chain/excerpts/hashes, impact, recommended direction, uncertainty and required fresh validation. No Local source/scope fix. LN-002: production qualification rejects unityengine.animationmodule despite all six disk inputs matching captured hashes; differing resolver/semantic contexts are the leading unproven cause. LN-003: native-codec verification consumes a project-relative source pin under demo cwd; exact owning codec bytes match the manifest. LN-004: independent complete verification of all five fresh sidecars fails the asymmetric assembly-name comparison; production verification remains Unavailable. Diagnosis receipts and source snapshots preserve these distinctions.

Live `{R}` and external preflight `{P}` remain retained, including projects/Library/HybridCLRData/reference sources and all receipt-referenced inputs. [Immutable N checkpoint]({rel}/README.md) includes exact indexed evidence, source snapshots and independent authentication/diagnosis receipts. Original archive bytes/seal remain unchanged, transported as exact ordered parts and reconstructed at a new path. Prior reports are preserved in full except their first Current heading becomes Historical.

| Original artifact | SHA-256 |
| --- | --- |
{hashes}

Only the two Local reports/new checkpoint are owned publication changes. Manifest/JSON/links/raw whitespace/staged Git bytes checked before commit; final exact clean repository/branch/remote heads/latest pushed commits and earlier custody verified externally in `{P}/PUBLICATION_RECEIPT.json` and the final short handoff. Executed source15f6c2c... remains distinct from the later publication HEAD.

**R03Accepted=false; H2Passed=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; PureInterpreter expansion disabled. No performance SLA or Human Review Gate readiness. Exit A: Local Validation → Primary Implementation. Stop; no further batch or non-trivial Local implementation.**

### All90 original cells

Per-cell receipts `{R}/cells/<id>.json` and BATCH_EXECUTION.json bind operation/dependencies/command clocks/outputs/hashes. Failed,Blocked,NotRun,Unavailable,NoCoverage and reused-audited evidence remain distinct.

| Cell | Original state |
| --- | --- |
{celltable}
'''
save('LOCAL_VALIDATION.md','# Local Validation report',local)
issue=issues['issues'][0];ev='\n'.join('- `'+e['path']+'`, SHA-256 `'+e['sha256']+'`; execution='+e['testExecution']+', XML='+e['xmlState'] for e in issue['evidence'])
ret=f'''## Current return — R03 batch N: four actionable Primary issues

**{r['result']};90 cells:{statusline};seal {r['sealStatus']};one invocation PID{run['pid']},{times}.** Six fresh build roles/23 focused Players Passed. Fresh P05 compile/restore/finalize and five schema-2 report results are recorded in LOCAL_VALIDATION.md. Actual direct Player processes={direct}; full754/755 rosters did not execute because source-scope admission Failed; early18 actual methods Passed. Preserve M and all earlier states unchanged.

Read [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md), [N checkpoint]({rel}/README.md), [PRIMARY_ISSUES.json]({rel}/preflight/PRIMARY_ISSUES.json), [EDITOR_SCOPE_DIAGNOSIS.json]({rel}/preflight/EDITOR_SCOPE_DIAGNOSIS.json) and [LAYOUT_IDENTITY_AUDIT.json]({rel}/preflight/LAYOUT_IDENTITY_AUDIT.json).

### R03-LN-001 — package-delta guard omits five identity production files

**Symptom.** {issue['symptom']}

**Exact reproduction already performed.** Use the four executed source heads/paths in LOCAL_VALIDATION.md, pinned Unity2022.3.62f2/SDK8.0.318. The single prescribed invocation is complete; inspect the two failing cells below and the Git-authenticated source snapshots in the diagnosis. Do not retry N or mutate its retained root. `CompletionBatch.execute → resource_pipeline.editor:175–188 → editor_contract.source_scope:28–31` rejects before scope-folder creation or `unity_command`.

```text
{command}
```

**Evidence/excerpt.** `editor_contract.py:30–31` computes the actual diff from package120bb01be680cec0375002a0823552d66d34b84c toef6c70f30248c4b7c41e9e85d81e08f5709dc4ba and requires equality with REVIEWED_PACKAGE_FILES. It raises exactly `Review any additional package change before selecting Editor tests`. Actual13 versus reviewed8;0 missing reviewed files. Additional files:

{additional}

{ev}

Diagnosis SHA-256 `{sha(P/'EDITOR_SCOPE_DIAGNOSIS.json')}`. No full-roster scope/XML/Editor log or associated Test Runner command exists; only the separate early18-method Test Runner invocation executed. Current expected names come from the authenticated catalog, not reused XML results.

**Direct cause/root cause/why permitted.** {issue['rootCause']} {issue['whyDesignAllowedIt']}

**Impact.** Both full Editor cells Failed;1509 intended cases are NotRun, with XML Unavailable. The separate18 methods and independently completed N build/identity/native/Player checks retain their recorded states. Full-stage coverage remains incomplete; no acceptance or Human Gate inference. Focused M01 NoCoverage and resource M01 Editor non-execution remain distinct from any actual resource runtime evidence.

**Concrete Primary direction.** {issue['recommendedDirection']}

**Remaining uncertainty.** {issue['remainingUncertainty']}

**Validation after repair.** {issue['validationAfterRepair']}

No Local source/scope change or runtime retry. All4 contaminated unisolated warm certificates remain Failed despite passing diagnostic attribution. R03Accepted=false;H2Passed=false;qualificationApproved=false;PureInterpreter expansion disabled. Source/runtime evidence belongs to executed15f6c2c9a5e070e631fdcda9a2bb022f4b61a733; later publication HEAD is listed only as transport authority in the final handoff/external receipt. **Exit A: Local Validation → Primary Implementation.**
'''
extra=[]
for item in issues['issues'][1:]:
 steps='\n'.join(str(i+1)+'. '+step for i,step in enumerate(item['reproduction']))
 evidence='\n'.join('- `'+e['path']+'`, SHA-256 `'+e['sha256']+'`' for e in item['evidence'])
 impact=json.dumps(item['affectedScope'],indent=2)
 extra.append(f"""### {item['id']} — {item['title']}

**Symptom.** {item['symptom']}

**Exact reproduction already performed.**

{steps}

**Evidence and excerpt.**

{evidence}

{item['relevantExcerpt']}

**Most likely root cause.** {item['rootCause']}

**Why the design allowed it.** {item['whyDesignAllowedIt']}

**Affected scope.**

```json
{impact}
```

**Recommended Primary direction.** {item['recommendedDirection']}

**Remaining uncertainty.** {item['remainingUncertainty']}

**Validation after repair.** {item['validationAfterRepair']}

**Local changes.** {item['localSourceFix']}
""")
ret=ret.replace('No Local source/scope change or runtime retry.', '\n\n'.join(extra)+'\n\nNo Local source/scope change or runtime retry.')
save('RETURN_TO_WEB.md','# Local Validation → Primary Implementation',ret)
(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps(history,indent=2)+'\n')
(C/'README.md').write_text(f'''# Immutable R03 completion batch N checkpoint

{r['result']};90 cells:{statusline};seal {r['sealStatus']};one invocation,{times}. Six fresh builds,actual direct Players={direct};full Editor roster source-scope failures retained. Executed demo15f6c2c9a5e070e631fdcda9a2bb022f4b61a733/packageef6c70f30248c4b7c41e9e85d81e08f5709dc4ba; native/IL2CPP source pins and all source/command hashes in receipts.

Read [LOCAL_VALIDATION](../../../.. /Handoff/LOCAL_VALIDATION.md), [RETURN_TO_WEB](../../../.. /Handoff/RETURN_TO_WEB.md), [batch result](batch/LOCAL_BATCH_RESULT.json), [ledger](batch/BATCH_EXECUTION.json), [index](batch/evidence-index.json), [seal](batch/seal-receipt.json), [identity audit](preflight/LAYOUT_IDENTITY_AUDIT.json), [runtime audit](preflight/COMPLETION_RUNTIME_AUDIT.json), [scope diagnosis](preflight/EDITOR_SCOPE_DIAGNOSIS.json), [Primary issues](preflight/PRIMARY_ISSUES.json), [archive transport](ARCHIVE_TRANSPORT.json), [manifest](MANIFEST.sha256).

Live root:{R};preflight:{P}. Exact byte parts reconstruct with REASSEMBLE_EVIDENCE.py at a new absolute unused path; original archive/index/seal remain unchanged. Earlier report bodies and {a['priorCustodyFilesUnchanged']} custody bindings preserved. No Local code fix; full Editor tests NotRun/XML Unavailable remain distinct from failed source admission. Nominal/reused-input evidence does not grant native/runtime/stage authority. Acceptance and expansion false; Exit A to Primary.
'''.replace('../../../.. /','../../../../'))
print('N reports written; complete historical bodies preserved',counts)
