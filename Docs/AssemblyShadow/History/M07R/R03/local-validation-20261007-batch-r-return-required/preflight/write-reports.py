"""Reconcile factual completed Local results; preserve all historical report bodies."""
from pathlib import Path
import json,hashlib,subprocess,collections,datetime
P=Path(__file__).resolve().parent;BASE=P.parent;W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';B=BASE/'R03LocalBatch-20261007R-lq-storage';PIN='ba57a3391da9627e694ee33f8bfe3cb993e6c56a'
def load(p):return json.loads(Path(p).read_text())
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
result=load(B/'LOCAL_BATCH_RESULT.json');cells=result['cells'];counts=dict(collections.Counter(c['result'] for c in cells));run=load(P/'runner-exit.json');S=BASE/'Storage-R03LocalBatch-20261007R-lq-storage';session=load(S/'session.json');dispatch=load(S/'dispatch.json');C=Path(load(P/'CHECKPOINT_LOCATION.json')['path']);links='../History/M07R/R03/'+C.name;authority=load(P/'SOURCE_AUTHORITY.json');audits=load(P/'POSTRUN_AUDIT_DISPATCH.json');ready=result['result']=='EvidenceReadyForPrimaryReview' and session['state']=='Passed' and run['exitCode']==0;env=load(P/'ENVIRONMENT.json');matrix='\n'.join('| '+c['id']+' | '+c['result']+' | '+','.join(c.get('dependencies',[]))+' | batch/cells/'+c['id']+'.json |' for c in cells);(C/'VALIDATION_MATRIX.md').write_text('# Original 90-cell validation matrix\n\nVerdicts are copied without reclassification from the sealed result.\n\n| Cell | State | Prerequisites | Evidence relative to checkpoint |\n| --- | --- | --- | --- |\n'+matrix+'\n')
rows='\n'.join(f'| `{W/name}` | `{authority["branch"]}` | `{pin}` |' for name,pin in authority['repositories'].items());top={n:sha(B/n) for n in ['LOCAL_BATCH_RESULT.json','BATCH_EXECUTION.json','evidence-index.json','evidence.tar.gz','seal-receipt.json']};hashrows='\n'.join(f'| `{n}` | `{h}` |' for n,h in top.items());auditrows='\n'.join(f'| {r["script"]} | {r["result"]} |' for r in audits['scripts']);failures=[{'id':c['id'],'state':c['result'],'error':c.get('error'),'evidencePath':str(B/'cells'/(c['id']+'.json')),'sha256':sha(B/'cells'/(c['id']+'.json'))} for c in cells if c['result']!='Passed'];(C/'ORIGINAL_FAILURES.json').write_text(json.dumps({'sourceCommit':PIN,'failures':failures,'noReclassification':True},indent=2)+'\n')
for flag in ['R03Accepted','H2Passed','qualificationApproved','pureInterpreterExpansionEnabled']:assert result[flag] is False
oldhashes=[]
head=f'''## Current run — R03 completion batch R, 2026-10-07 PDT

**{result['result']}; original cells={counts}; sealStatus={result.get('sealStatus',result.get('seal',{}).get('result','Unavailable'))}; executing storage session={session['state']}; wrapper exit={run['exitCode']}. Exit: Local Validation → Primary Implementation.** One executing invocation, PID{run['pid']}, `{run['startedUtc']}` → `{run['endedUtc']}` UTC. The original blocked prerequisite at source cbf80474 remains unchanged; it was NotRun, not a failed runtime attempt. This execution uses the newly authorized source `{PIN}`. No batch/phase retry, old-app reuse, product fix, scope/expectation/pin substitution, threshold/timeout/warm-up/lease change or historical promotion occurred.

### Authority, environment and source exception

User explicitly authorized `{PIN}` and the exact nine agent-configuration-file exception to WEB_TO_LOCAL's Docs-only post-anchor rule. All four clean owning checkouts matched independently verified canonical origins/remote heads; only demo safely fast-forwarded from95982f2 to the authorized commit. Product, storage/core runner, C#, fixture/package/native/IL2CPP sources and both source-pin manifests remain unchanged. [Authorization]({links}/preflight/USER_SOURCE_AUTHORIZATION.json), [source preflight]({links}/preflight/SOURCE_AUTHORITY.json), [synchronization]({links}/preflight/SYNCHRONIZATION.json), [environment]({links}/preflight/ENVIRONMENT.json) and commands/*/receipt.json record exact paths/heads/branches/status/remotes/worktrees/submodules/operations/clocks. No ordinary primary/control checkout was used for validation. Source snapshots match exact Git blobs; final Local transport HEAD is separate from runtime source.

| Actual repository | Branch | Executed source commit |
| --- | --- | --- |
{rows}

Unity2022.3.62f2 /StandaloneOSX arm64 at `{env['unityPath']}`; SDK8.0.318 from SDK-only `{env['sdkRoot']}`, no Unity6000 launch. Python path `{env['pythonPath']}`. Actual macOS/architecture/Xcode/clang/platform SDK versions and command clocks/stream hashes are retained in preflight/commands. EXPECTED_DEMO_COMMIT exact; DOTNET_ROOT/ARM64 pinned, MULTILEVEL_LOOKUP=0, TMPDIR=/private/tmp, bytecode disabled. Both source manifests, package manifest/lock and ProjectVersion match source Git blobs. No exact-project Editor was open at entry.

Ancillary gate helper returned InvalidMainAgentModel because exact effective main-model identity is unavailable from authoritative host metadata. Original exit1/stderr is preserved in [gate observation]({links}/preflight/ADMIN_PREFLIGHT_GATE_OBSERVATION.json); no model guess, retry with a guess, Off/PASS inference or gate-setting change occurred. It stopped only Local administrative preparation before storage tests/admission/Unity; continuation completed the remaining preflight under the explicit user-authorized runtime scope. Independent full-stage review remains pending, outside this batch.

### Invocation and storage

Prescribed executing wrapper, cwd `{D}`; exact environment/start/end/PID/exit/stream hashes are in [runner receipt]({links}/preflight/runner-exit.json):

```text
{' '.join(run['argv'])}
```

48 fresh storage host tests Passed with zero failures/errors/skips. New diagnostic `{BASE/'StorageCheck-R03LocalBatch-20261007R-lq-storage-2'}` admission=Admitted/session=Passed; all10 allocation/fsync/readback/cleanup probes Passed. The executing wrapper independently obtained its own fresh admission and immediately rechecked full capacity before construction. No diagnostic pass alone was treated as launch authority. The original blocked diagnostic and immutable checkpoint remain byte-identical.

Executing sidecar `{S}` and byte-identical checkpoint copy [executing-storage]({links}/executing-storage) retain source authority, sizing/admission, all capacity samples, launch-intent, integration-allocation-probe, any failures, original session/dispatch. Original admission budget is `max(64GiB,2*B+20GiB)`; operating floor20GiB unchanged. All validation locations use the same APFS Data-container pool; sibling free space is not summed. Sampled minimum is not instantaneous high-water; space was not reserved. Current preflight resolved-device/APFS/quota observations and original ordinary-directory diagnostic Unavailable states remain distinct. Operator storage changes were not performed by Local; custody checks verified preserved evidence before execution.

Final storage state={session['state']}; samples={session['samples']}; minima bytes={session['minimumSampledAvailableBytes']}; latched problem={session.get('latchedProblem')}. [Publication-capacity receipt]({links}/preflight/storage-publication-check.json) separately verifies the unchanged prescribed batch-footprint-plus20GiB budget at checkout, retained root and actual Git common directory before copying. It does not rewrite the core or session verdict.

### Original validation and independent evidence checks

Original90-cell counts={counts}; see [complete matrix]({links}/VALIDATION_MATRIX.md) and original sealed ledger/result. The required scope remains six fresh native builds,18-method early Editor preflight, exact754/755 full Editor rosters with zero skips/inconclusive, and59 fresh Players. Actual statuses, exact build/nativeBinding/installation/source pins/GUIDs, XML/scope/verdict hashes, launch/request/raw/verification IDs, process lifetimes and native observations are retained in original cells and the independent audit reports below. Expected-negative compiler/Player exits are separate from failed product builds. Any Failed/Blocked/NotRun/Unavailable/NoCoverage/reused-audited evidence retains its original state.

| Read-only postrun audit | Dispatch state |
| --- | --- |
{auditrows}

Postrun/COMPLETION_RUNTIME/LO/LP/LI/LN/resource-restoration/layout/producer/rejection/capability/fixed-image/compiler-policy audits record concrete subproofs, counts and hashes independently of dispatch success. Binding-before-integration, live source/linked policy guards, all five current sidecars/P05 finalization and exact restoration, restored-baseline zero changed roots/zero closure, strict R02 bridge/221-object aggregate, codec contexts and measurement/startup original contracts are rechecked where original prerequisites Passed. Frozen M00/historical compiler-input reuse remains audited input reuse, not a new M00 compilation or old Player-result reuse. Natural producer controls retain Failed unisolated warm certificates even when their diagnostic contract Passed; isolation is diagnostic and does not approve a production performance SLA. Focused M01 NoCoverage and separate original-resource coverage remain distinct.

All indexed raw files and top-level artifacts remained unchanged through postrun audits. Historical custody is independently rechecked against the expanded authenticated map, including Q/P/O/N and the original blocked R checkpoint/sidecar. Retained fresh live Libraries/HybridCLRData/native roots and build/reference identities are bound by RETAINED_LIVE_ROOTS.json and original receipts; they are not mixed with previous apps or caches. No source changes were made by Local.

| Live original artifact | SHA-256 |
| --- | --- |
{hashrows}

Live batch: `{B}`. Exact checkpoint [README]({links}/README.md), FILE_TRANSPORT.json and reconstruction helper preserve the sealed archive and oversized raw copies as ordered64MiB parts without rewriting/resealing. Source bindings, all original cells/commands/host/Editor/build/Player/resource/measurement/early-startup receipts and full storage/preflight are included. LOCAL_BATCH_RESULT.json remains the original factual result; no storage/gate state is substituted into its cells.

### Publication and exit

Only Local-owned LOCAL_VALIDATION.md, RETURN_TO_WEB.md and this new immutable checkpoint are modified. Historical report bodies are preserved with only the prior Current heading changed to Historical. Manifest/JSON/hash/local-link/source/whitespace/staged-byte checks and remote/cleanliness verification accompany publication; final pushed four-repository commits are recorded externally at `{P}/PUBLICATION_RECEIPT.json` and in the final handoff. Publication HEAD is transport authority only, not executed source.

{'No new product-source blocker was found by this batch; Primary must reconcile the fresh evidence and perform independent full-stage review.' if ready and not failures else 'Return the factual original failures/limits to Primary; do not expand Local implementation or retry. Read ORIGINAL_FAILURES.json and RETURN_TO_WEB.md.'} R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; PureInterpreter expansion disabled. Full-stage acceptance, independent review, human approval and production performance SLA remain pending; R02 CPU/H1 RSS risks and contaminated Failed warm certificates are not promoted. **Local Validation → Primary Implementation. Stop.**

'''
ret=f'''## Current return — R03 completion batch R, 2026-10-07 PDT

**{result['result']}; original90-cell counts={counts}; storage session={session['state']}; wrapper exit={run['exitCode']}. Local Validation → Primary Implementation.** Read [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md), [immutable R checkpoint]({links}/README.md), [matrix]({links}/VALIDATION_MATRIX.md), original sealed result/ledger and [original failures]({links}/ORIGINAL_FAILURES.json). Source `{PIN}` was explicitly authorized, including its nine agent-configuration-file exception. Prior Q/P/O/N and original blocked R evidence remain unchanged.

{'No new non-trivial product-source issue was found in this Local batch. The prior storage deficit is superseded only by separately recorded fresh admission/execution; the original CapacityBlocked/NotRun record remains historical and unchanged. Primary should reconcile this evidence and perform independent full-stage review before any acceptance decision.' if ready and not failures else 'Original failures and blockers require Primary reconciliation. Exact cell errors and source-bound evidence paths/hashes are in ORIGINAL_FAILURES.json; no phase retry, product-source fix or expectation change was made.'}

Fresh scope and every original state are detailed in LOCAL_VALIDATION.md and the complete matrix. Core result/ledger/index/archive/seal, all build/Editor/Player/resource/measurement/startup receipts and separate storage telemetry are preserved; any reused-audited inputs remain distinguished from fresh runtime results. Independent read-only audits record actual subproof verdicts rather than promoting a focused pass or dispatch exit to full-stage acceptance. Four contaminated unisolated warm certificates retain Failed.

The ancillary gate helper's InvalidMainAgentModel exit1 is retained as an unresolved exact-host-identity observation, not a runtime test failure or gate PASS/Off. No model was guessed or gate/source configuration changed. Independent full-stage review remains pending under the handoff scope.

Remaining validation/decision: Primary reconciliation, independent full R03 stage review, explicit acceptance/human gate and production performance/SLA decisions. R02 CPU/H1 RSS risks remain visible. No new Local development, next milestone, structural/PureInterpreter expansion or historical reclassification is authorized. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; PureInterpreter expansion disabled. **Local Validation → Primary Implementation. Stop.**

'''
for name,new,prefix in [('LOCAL_VALIDATION.md',head,'## Current run'),('RETURN_TO_WEB.md',ret,'## Current return')]:
 path=D/'Docs/AssemblyShadow/Handoff'/name;old=path.read_bytes();assert old==subprocess.check_output(['git','-C',str(D),'show',PIN+':'+str(path.relative_to(D))]);title,body=old.decode().split('\n',1);historical=body.replace(prefix,prefix.replace('Current','Historical'),1).lstrip('\n');assert prefix in body;path.write_text(title+'\n\n'+new+historical);oldhashes.append({'file':str(path.relative_to(D)),'priorGitCommit':PIN,'priorFileSha256':hashlib.sha256(old).hexdigest(),'historicalBodySha256':hashlib.sha256(historical.encode()).hexdigest(),'currentFileSha256':sha(path),'onlyHistoricalEdit':'First Current heading changes to Historical; all prior evidence bodies retained'})
(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps({'reports':oldhashes},indent=2)+'\n')
(C/'README.md').write_text(f'''# R03 completion batch R Local evidence

**{result['result']}; original counts={counts}; storage session={session['state']}; wrapper exit={run['exitCode']}.** Executed source `{PIN}`. One executing invocation; no retry or product fix. All acceptance flags remain false; independent full-stage review pending.

[Matrix](VALIDATION_MATRIX.md), [transport bindings](FILE_TRANSPORT.json), [source bindings](SOURCE_BINDINGS.json), [Local report](../../../../Handoff/LOCAL_VALIDATION.md), [Primary return](../../../../Handoff/RETURN_TO_WEB.md). Preflight and all three separate storage records are included; the original blocked diagnostic remains unchanged. Live root `{B}` and retained isolated Libraries/HybridCLRData/reference roots remain at their receipt-bound paths.

Transported files are exact ordered64MiB parts, not new result/ledger/seal bytes. REASSEMBLE_EVIDENCE.py reconstructs them into a new absolute unused directory and verifies sizes/hashes; original live bytes remain unchanged. MANIFEST.sha256 covers all checkpoint files except itself.

Latest pushed four-repository commits will be recorded externally at `{P}/PUBLICATION_RECEIPT.json` and final handoff; publication HEAD is transport authority, not executed source. Local Validation → Primary Implementation. Stop.
''')
print('Updated Local reports; historical bodies preserved')
