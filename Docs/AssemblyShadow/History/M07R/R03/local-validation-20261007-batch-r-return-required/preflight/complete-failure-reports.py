"""Add exact current-run results and actionable Primary return; preserve historical report bodies."""
from pathlib import Path
import json,hashlib,shutil
P=Path(__file__).resolve().parent;C=Path(json.loads((P/'CHECKPOINT_LOCATION.json').read_text())['path']);D=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');B=P.parent/'R03LocalBatch-20261007R-lq-storage';S=P.parent/'Storage-R03LocalBatch-20261007R-lq-storage';cfg=json.loads((B/'resource-project.json').read_text());a=json.loads((P/'P05_RESTORE_FAILURE_ANALYSIS.json').read_text());link='../History/M07R/R03/'+C.name
issue=f'''### R03-LR-002 — remote-authority failure stranded the P05 transaction

**Symptom:** `resource-p05-restore=Failed`, error `Git command failed: ls-remote origin`; 42 dependent cells Blocked. P05 preparation and compilation Passed, but no StructuralRestore process launched. The isolated project remains staged with `ASSEMBLY_SHADOW_P05`; original define string was empty. No restoration, finalization, full-resource Editor or integrated resource/measurement/startup acceptance is established. No failed product Unity command was observed.

**Reproduction:** At the four exact source commits in LOCAL_VALIDATION.md, with Unity2022.3.62f2 /StandaloneOSX arm64 and SDK8.0.318, follow the single storage-checked invocation in [runner receipt]({link}/preflight/runner-exit.json). After command0122 StructuralCompile exited0, `resource-p05-restore` calls `resources.restore` → `authenticate_copy` → `run_local.git(root, 'ls-remote', 'origin', 'refs/heads/codex/assembly-shadow-r01b-h1')`. The captured original event occurred2026-10-07T15:19:22.695541Z (08:19:22 PDT). Do not reexecute R or a phase to reproduce; this original event and retained state are sufficient to identify the failure boundary. The transport failure itself is not reliably reproducible from captured data.

**Evidence:** [original failed cell]({link}/batch/cells/resource-p05-restore.json), [original storage exception/stack]({link}/executing-storage/failure-000689.json), [read-only analysis]({link}/preflight/P05_RESTORE_FAILURE_ANALYSIS.json), [original compile command]({link}/batch/commands/0122/command.json) and unity-completion.json; immutable backups/live paths below. Relevant stack excerpt: `resource_pipeline.py:133 authenticate_copy(batch, config)` → `fixture_authority.py:49 git(root, 'ls-remote', 'origin', ...)` → `run_local.py:31 require(result.returncode == 0, 'Git command failed: ls-remote origin')`.

| Evidence | Exact live path | SHA-256 |
| --- | --- | --- |
| Failed restore cell | `{B}/cells/resource-p05-restore.json` | `{hashlib.sha256((B/'cells/resource-p05-restore.json').read_bytes()).hexdigest()}` |
| Original exception | `{S}/failure-000689.json` | `{a['failureReceiptSha256']}` |
| Original settings backup | `{a['originalSettingsPath']}` | `{a['originalSettingsSha256']}` |
| Retained staged settings | `{a['currentStagedSettingsPath']}` | `{a['currentStagedSettingsSha256']}` |

`p05-restored.json`, `p05-settings-restored.json`, `p05-unity-restored.bytes`, `R03CompletionArtifacts/restore.json` and resource-logs/restore.log are absent. The original state/compile receipts and retained project root are preserved; Local did not restore or otherwise alter the sealed/live state.

**Most likely cause and uncertainty:** A remote Git subprocess returned nonzero while checking exact authority, before transaction recovery. Network/SSH/server failure is plausible, but its original stderr, numeric exit, full argv and failing repository were discarded by `run_local.git`; no specific transport cause or remote-head change can be inferred. All four clean owning HEADs and canonical remote tips matched in the later read-only postrun audit. That later observation does not retroactively pass the original check. This is not evidence of a product runtime defect or storage exhaustion.

**Affected scope:** P05 exact restoration/finalization, the755-case resource Editor roster, resource graph binding, production integration/live policy/restored-baseline zero-root/zero-closure proofs, and36 resource/measurement/early Players. Six builds, the18-method early and754-case focused Editor rosters, and23 focused Players completed independently. Earlier Q/P/O/N and original blocked R results are unchanged.

**Recommended Primary direction:** Add source-bound Git command failure receipts containing repository, complete argv, numeric exit, bounded stdout/stderr, start/end and source authority; retain strict canonical origins/exact commit checks and fail-closed acceptance. Review transaction cleanup ownership so loss of fresh remote connectivity cannot silently leave recovery unobserved; authenticate captured transaction/original bytes and record recovery separately from runtime acceptance. Any such design/recovery change belongs to Primary. Preserve this staged project before any recovery; do not repair it or retry inside R. Establish transport readiness and publish an explicit new source/root handoff after reconciliation.

**Required validation after Primary action:** Closed-loop failure-diagnostic and transaction-ownership controls without weakening authority; then a fresh authorized batch/root with exact P05 byte restoration/finalization,755 resource cases,36 additional Players, graph-before-integration, live source/linked-policy and zero-root/zero-closure proofs, strict bridge/resource aggregate/codec evidence, complete90-cell ledger and seal. Full-stage independent review/acceptance decisions remain pending.

'''
actual=f'''### Actual completion and audit limits

| Required validation | Actual R state |
| --- | --- |
| Storage tests/admission/runtime | 48 host tests Passed; two separate fresh admissions Admitted with10 probes each; executing session Passed,720 samples, minimum59.624 GiB; production integration allocation probe NotRun |
| Core matrix | 90 original cells:47 Passed,1 Failed,42 Blocked; result ReturnRequired; seal Passed |
| Native builds | All six fresh build cells Passed; four focused roles plus resource ON/OFF; separate exact native/source inventories authenticated |
| Early constructor Editor preflight | 18 methods Passed;12 host constructor controls and10 actual source-pin consumer controls Passed |
| Focused Editor | 754 cases Passed; zero Failed/skipped/inconclusive |
| Resource Editor | 755 planned; NotRun because restoration Failed; original cell Blocked; no XML |
| Players | 23 fresh focused processes Passed;36 planned resource/measurement/startup cases NotRun/Blocked; total required59 remains incomplete |
| Warm/physical proofs | Six strict focused warm witnesses and positive C07 proof Passed; four producer controls diagnostic Passed while each unisolated warm certificate remains Failed |
| Qualification | Fresh static qualification cell Passed, non-authorizing; qualificationApproved=false |
| P05 restore/finalize and production integration | Restore Failed; downstream Blocked; live policy/restored-baseline zero-root/zero-closure/strict bridge/resource aggregate not established in R |
| Evidence custody | 10,784 indexed files,10,785 archive members authenticated;174,915 prior-custody paths unchanged; no owned process-group survivors observed postrun |

Initial postrun audit dispatch failures are preserved. LI's administrative adapter referenced an absent old-template settings file; the separate [partial reconciliation]({link}/preflight/PARTIAL_BATCH_RECONCILIATION.json) binds actual preflight settings directly to exact source Git blobs and verifies18/10 controls. Resource restoration audit lacks genuine restore receipts; its coverage is Unavailable. Capability audit's full-current-input check fails on retained staged settings after the original restore failure; the actual10-case preflight Passed and original execution verification remain distinct from postrun revalidation Unavailable. Completion auditor's Q-specific failure-reproduction assertion cannot reproduce an uncaptured Git transport error offline; its7 semantic observations remain2 Passed/5 NotRun and original dispatch Failed. No original verdict was rewritten and no product was reexecuted.

The [storage runtime audit]({link}/preflight/STORAGE_RUNTIME_AUDIT.json) authenticates720 sequential samples, both10-probe admissions, source/dispatch/result/telemetry bindings and no latched capacity fault. Three failure-* diagnostics are expected-negative compiler/fixture controls (cell Passed); the fourth is the actual Git restore failure. Ordinary-path diskutil diagnostics retain Unavailable separately from resolved-device APFS observations.

'''
for name,extra,marker in [('LOCAL_VALIDATION.md',actual+'See current R03-LR-002 in [RETURN_TO_WEB.md](RETURN_TO_WEB.md) for actionable reproduction, hashes, cause limits and required Primary work.\n\n','### Publication and exit'),('RETURN_TO_WEB.md',issue,'Remaining validation/decision:')]:
 path=D/'Docs/AssemblyShadow/Handoff'/name;text=path.read_text();pos=text.index(marker);text=text[:pos]+extra+text[pos:];text=text.replace('launch-intent, integration-allocation-probe, any failures, original session/dispatch','launch-intent, any failures, original session/dispatch; integration-allocation-probe is NotRun because production integration was Blocked');path.write_text(text)
history=json.loads((C/'REPORT_HISTORY_PRESERVATION.json').read_text())
for row in history['reports']:
 row['currentFileSha256']=hashlib.sha256((D/row['file']).read_bytes()).hexdigest()
(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps(history,indent=2)+'\n')
(C/'README.md').write_text((C/'README.md').read_text()+'\nActual completed scope: six build cells,18+754 Editor cases and23 focused Players Passed. Restore Failed;42 dependent cells Blocked including755 Editor cases and36 Players NotRun. R03-LR-002 is documented in RETURN_TO_WEB.md. Storage session Passed independently. PARTIAL_BATCH_RECONCILIATION.json and STORAGE_RUNTIME_AUDIT.json preserve initial auditor failures and coverage limits. No phase/source/settings retry or restoration was performed.\n')
for src in P.rglob('*'):
 if src.is_file() and src.name!='PUBLICATION_RECEIPT.json':
  dest=C/'preflight'/src.relative_to(P);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
print('Exact failed-boundary report and actual scope recorded; historical bodies retained')
