"""Update only the two Local reports after authenticated S and checkpoint copying."""
from pathlib import Path
import json,hashlib,subprocess,datetime
P=Path(__file__).resolve().parent;BASE=P.parent;B=BASE/'R03LocalBatch-20261007S-lr-recovery';D=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');C=Path(json.loads((P/'CHECKPOINT_LOCATION.json').read_text())['path']);a=json.loads((P/'POSTRUN_AUTHENTICATION.json').read_text());result=json.loads((B/'LOCAL_BATCH_RESULT.json').read_text());auth=json.loads((P/'SOURCE_AUTHORITY.json').read_text());pin=auth['repositories']['hybridclr_demo'];outer=json.loads((P/'operations/storage-executing/receipt.json').read_text());env=json.loads((P/'READ_ONLY_READINESS.json').read_text());ready=a['state']=='Passed' and result['result']=='EvidenceReadyForPrimaryReview' and result['sealStatus']=='Passed' and a['storageSessionState']=='Passed' and a['outerExitCode']==0;cp='../History/M07R/R03/'+C.name;cells={r['id']:r for r in result['cells']}
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,value):
 with Path(path).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
rows='\n'.join('| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/'+name+'` | `codex/assembly-shadow-r01b-h1` | `'+commit+'` |' for name,commit in auth['repositories'].items());hashes='\n'.join('| `'+name+'` | `'+h+'` |' for name,h in a['topLevelHashes'].items());counts=' / '.join(str(n)+' '+status for status,n in a['counts'].items());failed='; '.join(c['id']+': '+c['error'] for c in a['failedCells']) or 'None';player_states={};
for row in a['playerVerificationRecords']:player_states[row['result']]=player_states.get(row['result'],0)+1
recovery=a['transactionRecovery'];body=f'''## Current run — fresh R03 batch S after storage remediation, 2026-10-07 PDT / 2026-10-08 UTC

**Core result: {result['result']}; {counts}. Seal {result['sealStatus']}; executing storage/session {a['storageSessionState']}; wrapper exit {a['outerExitCode']}; independent read-only byte authentication {a['state']}. Exit: Local Validation → Primary Implementation.** This is exactly one fresh S execution. Original S capacity-blocked prerequisite evidence remains immutable; its batch-NotRun fact was not rewritten. User continuation explicitly resolved the exact execution SHA to pushed Local documentation descendant `{pin}` of Primary source `e8fda852684f584295fe37830340ab3c9f3fcc4f`; their 389-file delta contains only Local reports/blocker checkpoint. Executable source remains identical to anchor 9f27feb647bbf2d2bc82483700fe4f78e5ea60be. [Authorization and unused-path binding]({cp}/preflight/EXECUTION_AUTHORIZATION.json).

### Source and environment

| Actual owning repository | Branch | Exact execution commit |
| --- | --- | --- |
{rows}

Unity 2022.3.62f2 at `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`; StandaloneOSX arm64. SDK 8.0.318 at SDK-only `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`; Unity 6000 was never launched. Python `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3` 3.14.6; macOS 26.5.2 build 25F84; active CommandLineTools MacOSX SDK 26.5 and Apple clang 21.0.0. Full-Xcode version remains Unavailable, separate from the actual native build results. No source/package/native/build pin, credential/protocol, scope, expectation, timeout, warm-up, fence, GC or acceptance flag was changed. No bounded product fix was made. Shared Git common metadata locations are recorded; no ordinary primary/control project or prior app was used for validation. [Source authority]({cp}/preflight/SOURCE_AUTHORITY.json), [environment]({cp}/preflight/READ_ONLY_READINESS.json), [exact snapshots]({cp}/SOURCE_BINDINGS.json).

### Prerequisites, build and runtime

| Required validation | Factual state |
| --- | --- |
| Retained R read-only six-file audit | Passed before and after; original restore Failed; settings still staged; restorationPerformed=false; original Git cause Unavailable |
| Four-owner transport / LR / storage prerequisites | TransportReady, all 4 Passed; 45 LR and 48 storage tests Passed, zero skips/errors/failures |
| Full historical custody | Passed before/after for 291,006 unique files, including 290,082 original published-map paths plus prior S checkpoint/preflight; no missing-file rebaselining or historical reclassification |
| Fresh diagnostic / executing admission | Admitted, all allocation probes Passed; respective sessions Passed. Fresh outputs use `-2` sidecars; original blocked sidecar untouched |
| Ninety-cell core ledger | {counts}; exact 90 unique cells retained |
| Four focused native builds | {', '.join(role+': '+cells['build-'+role]['result'] for role in ['candidate-release','reference-release','candidate-debug','candidate-off'])} |
| Two original-resource native builds | ON {cells['resource-player-on']['result']}; OFF {cells['resource-player-off']['result']} |
| Early 18-method Editor / 754 focused / 755 original-resource scopes | Early {cells['completion-tool-contracts']['result']}; focused {cells['editor-tests']['result']}; original-resource {cells['resource-editor']['result']}; actual XML/scope/verdict records retained |
| Fresh Player verification records | {a['playerVerificationCount']} records: {player_states}; full requirement 23 focused + 14 resource + 12 observations + 10 early = 59 |
| P05 prepare / compile / restore / finalize | {', '.join(label+': '+cells['resource-p05-'+label]['result'] for label in ['prepare','compile','restore','finalize'])} |
| Cleanup and fresh remote acceptance | cleanupResult={recovery.get('cleanupResult','Unavailable')}; remoteAuthority={recovery.get('remoteAuthority','Unavailable')}; stage={recovery.get('stage','Unavailable')} |
| Resource binding / production integration / aggregate / measurement summary / final authority | {', '.join(label+': '+cells[label]['result'] for label in ['resource-input-binding','production-entry-integration','resource-contracts','measurement-summary','final-authority'])} |
| Core index/archive/seal and exact copied transport | {result['sealStatus']}; original sealed bytes/hashes retained without resealing |

[Read-only postrun authentication]({cp}/preflight/POSTRUN_AUTHENTICATION.json) records each command/stream hash, actual exits/process groups, both Editor XML verdicts, Player bindings, recovery and all five top-level hashes. Command expected-negative compiler controls stay distinct from successful product builds. [Integrated detailed observations]({cp}/preflight/INTEGRATED_DETAILS.json) records build GUIDs/native bindings, six strict warm witnesses, C07 physical readiness, rejection preservation, producer attribution, Editor counts, integration roots/closure and restoration hashes. Contaminated producer controls retain Failed unisolated warm certificates alongside Passed diagnostic results; the producer lease is diagnostic-only. Prior M01 NoCoverage/results/certificates are unchanged; current 755-roster M01 execution is separate. Frozen M00/compiler input reuse is ReusedAudited input, not fresh M00 compilation or historical runtime acceptance. Original90 sealed rows are never rewritten for supplemental observations.

### Command, time, custody and evidence

Execution cwd `{D}`; start `{outer['startUtc']}`, end `{outer['endUtc']}` UTC (October7 PDT). Exact command/streams/clocks are in [outer receipt]({cp}/preflight/operations/storage-executing/receipt.json):

```text
{' '.join(outer['argv'])}
```

Live batch `{B}`; retained isolated project/SDK/cache/reference roots remain where their receipts bind them. [Retained roots]({cp}/preflight/RETAINED_LIVE_ROOTS.json). Fresh preflight `{P}`; diagnostic `{BASE}/StorageCheck-R03LocalBatch-20261007S-lr-recovery-2`; executing storage `{BASE}/Storage-R03LocalBatch-20261007S-lr-recovery-2`; retained-R audit and transport use corresponding `-2` roots. Allocation probes are point-in-time, not capacity reservation. Sampling/tracebacks and [publication footprint plus 20 GiB check]({cp}/preflight/storage-publication-check.json) preserve observed capacity/constraints. No capacity reclamation, arbitrary deletion or relocation was performed by Local.

Retained R `{BASE}/R03LocalBatch-20261007R-lq-storage` remains untouched and staged; its 90-cell 47 Passed / 1 Failed / 42 Blocked result is not reclassified. Q/P/O/N/all earlier and original blocked R/S evidence retain exact hashes. [Before custody]({cp}/preflight/HISTORICAL_CUSTODY_BEFORE.json), [after custody]({cp}/preflight/HISTORICAL_CUSTODY_AFTER.json), original expected map and six-file before/after audit remain separate. Unindexed old R caches are current custody snapshots, not historical acceptance evidence.

| Immutable core artifact | SHA-256 |
| --- | --- |
{hashes}

Failures: {failed}. Blocked cells: {len(a['blockedCells'])}. No phase/batch retry or product-source change. All still-meaningful assigned cells were executed or truthfully blocked by the unchanged scheduler.

### Publication and exit boundary

Only these two Local reports and new `{C.name}` are owned changes. Exact copy/source/JSON/hash/link/manifest/whitespace/staged-byte checks accompany publication. Archive ordered parts reconstruct the original sealed byte stream; [transport manifest]({cp}/FILE_TRANSPORT.json) and helper preserve live originals. Latest pushed four-repository HEADs and clean/remote verification are recorded externally at `{P}/PUBLICATION_RECEIPT.json` and in the final handoff, separate from the execution source `{pin}`.

R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; PureInterpreter expansion disabled. Independent full-stage review, Primary reconciliation and owner/human approval remain pending. Observations do not approve a production performance SLA, deferred R02 CPU/H1 RSS risks or unfenced warm acceptance. Prior ancillary effective-main-model observation remains unresolved and distinct; no gate PASS/Off or independent-review claim. Local returns to Primary and stops.

'''
return_body=f'''## Current return — fresh R03 batch S, 2026-10-07 PDT

Core `{result['result']}`; {counts}; seal {result['sealStatus']}; storage {a['storageSessionState']}; wrapper exit {a['outerExitCode']}. Execution demo `{pin}`; native/package/IL2CPP pins unchanged. [Full factual Local report](LOCAL_VALIDATION.md), [immutable checkpoint]({cp}/README.md), [postrun authentication]({cp}/preflight/POSTRUN_AUTHENTICATION.json).

{('No new non-trivial product-source defect was observed in this assigned batch. No Primary Implementation defect entry is manufactured.' if ready else 'Observed failures requiring Primary triage: '+failed)} P05 cleanup `{recovery.get('cleanupResult','Unavailable')}` and fresh remote authority `{recovery.get('remoteAuthority','Unavailable')}` are separate preserved facts. Original R remains staged, Failed at restoration, with original transport cause Unavailable. Historical Q/P/O/N, blocked prerequisites and contaminated Failed unisolated certificates are unchanged.

Required Primary action: reconcile this source-bound complete/partial matrix and preserved raw evidence, then perform the independent full-stage review and explicit owner decisions. Do not infer R03/H2 acceptance, qualification approval, PureInterpreter expansion, performance SLA or a new milestone from a Local batch result. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; PureInterpreter expansion disabled. Local stops; no retry or implementation expansion is authorized.

'''
preservation=[]
for name,prefix in [('LOCAL_VALIDATION.md',body),('RETURN_TO_WEB.md',return_body)]:
 path=D/'Docs/AssemblyShadow/Handoff'/name;old=path.read_bytes();blob=subprocess.check_output(['git','-C',str(D),'show',pin+':Docs/AssemblyShadow/Handoff/'+name]);assert old==blob;title,oldbody=old.decode().split('\n\n',1);historical=oldbody.replace('## Current','## Historical',1);new=title+'\n\n'+prefix+historical;path.write_text(new);assert path.read_text().endswith(historical);preservation.append({'path':str(path),'sourceCommit':pin,'beforeSha256':hashlib.sha256(old).hexdigest(),'afterSha256':sha(path),'historicalBodyPreserved':True,'soleOldBodyEdit':'First Current heading becomes Historical'})
save(C/'REPORT_HISTORY_PRESERVATION.json',{'kind':'PreservedLocalReportHistory','reports':preservation})
(C/'README.md').write_text(f'''# Immutable Local R03 batch S checkpoint

Execution source `{pin}`; {result['result']}; {counts}; seal {result['sealStatus']}; storage {a['storageSessionState']}; wrapper exit {a['outerExitCode']}. Original S blocked prerequisites and retained R are unchanged. This checkpoint contains exact selected sealed evidence, source snapshots, admitted diagnostic/executing sidecars and read-only custody/publication checks. Excluded live roots remain retained at their original receipt paths; see preflight/RETAINED_LIVE_ROOTS.json. It is not an all-cache archive or product acceptance.

Read the Local report and preflight/POSTRUN_AUTHENTICATION.json, INTEGRATED_DETAILS.json and SOURCE_AUTHORITY.json; batch/LOCAL_BATCH_RESULT.json and BATCH_EXECUTION.json preserve all 90 original rows. COPY_BINDINGS.json and SOURCE_BINDINGS.json authenticate original copies. FILE_TRANSPORT.json gives ordered exact parts for evidence.tar.gz/large originals. REASSEMBLE_EVIDENCE.py reconstructs into an absolute unused directory only; no resealing or historical reclassification. MANIFEST.sha256 binds checkpoint files.

Final pushed commits/publication receipt are external at `{P}/PUBLICATION_RECEIPT.json`, avoiding a recursive commit self-hash; final handoff supplies all four exact latest pushed heads. R03Accepted=false; H2Passed=false; qualificationApproved=false; PureInterpreter expansion disabled. Next owner: Primary Implementation for reconciliation and independent full-stage review, not autonomous next-milestone work.
''')
print('Updated only Local reports and checkpoint README; historical bodies preserved',flush=True)
