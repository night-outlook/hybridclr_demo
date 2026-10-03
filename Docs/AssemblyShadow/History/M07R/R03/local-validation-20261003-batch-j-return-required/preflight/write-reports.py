import pathlib,json,hashlib,subprocess,datetime,zoneinfo,collections,shutil
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261003J-contracts';R=P.parent/'R03LocalBatch-20261003J-contracts';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261003-batch-j-return-required';load=lambda p:json.loads(pathlib.Path(p).read_text());sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();result=load(R/'LOCAL_BATCH_RESULT.json');auth=load(P/'POSTRUN_AUTHENTICATION.json');li=load(P/'LI_CONTRACT_AUDIT.json');issues=load(P/'PRIMARY_ISSUES.json');env=load(P/'environment.json');inv=load(P/'runner-exit.json');assert auth['status']==li['status']=='Passed' and auth['counts']=={'Passed':43,'Failed':1,'Blocked':46};assert inv['batchInvocations']==1 and inv['pid']==89851 and inv['exitCode']==1
rel='../History/M07R/R03/'+C.name;start=datetime.datetime.fromisoformat(inv['startedUtc']);end=datetime.datetime.fromisoformat(inv['endedUtc']);tz=zoneinfo.ZoneInfo('America/Los_Angeles');interval=start.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')+'–'+end.astimezone(tz).strftime('%H:%M:%S %Z');command=' '.join(inv['command']);repoRows='\n'.join('| `'+str(W/n)+'` | `'+result['repositories'][n]+'` |' for n in ['hybridclr_demo','hybridclr','hybridclr_unity','il2cpp_plus']);hashRows='\n'.join('| `'+n+'` | `'+h+'` |' for n,h in auth['topLevelHashes'].items());cellRows=[]
for c in result['cells']:
 detail=c.get('error','') if c['result']=='Failed' else ('Prerequisite did not pass: '+', '.join(c['dependencies']) if c['result']=='Blocked' else '')
 cellRows.append('| `'+c['id']+'` | '+c['result']+' | '+detail.replace('|','\\|')+' |')
mac='; '.join(env['versions']['macOS'].splitlines());runtime=f'''Fresh focused evidence: four isolated native/IL2CPP builds and all 19 main plus four diagnostic-control Player contracts Passed. Six strict warm witnesses, full positive C07 physical-layout/publication/business checks and five non-mutating rejected-stage observations Passed. [PRODUCER_RUNTIME_AUDIT.json]({rel}/preflight/PRODUCER_RUNTIME_AUDIT.json) reconciles ten probes/fifty spans; actual natural-control producer attribution is Observed with four identified loop admissions. Each contaminated control retains **unisolatedWarmCertificate=Failed**. The diagnostic finalizer lease remains bounded and is not production GC/performance acceptance. [REJECTION_RUNTIME_AUDIT.json]({rel}/preflight/REJECTION_RUNTIME_AUDIT.json) confirms original error16/state8/unpublished/RestartRequired survives capacity -2, two complete owned-byte reads and final raw projection/recovery. No terminal restoration, counter relaxation, extra warm-up or ownership change.
'''
local=f'''## Current run — R03 completion batch J, 2026-10-03: contract repairs Passed; resource policy mismatch returns to Primary

**Result=ReturnRequired; 90 cells:43 Passed /1 Failed /46 Blocked; sealStatus=Passed; runner exit1. Exit Local Validation → Primary Implementation.** Exactly one fresh invocation PID89851, {interval}; UTC {inv['startedUtc']}–{inv['endedUtc']}. No retry, blocked-stage manual continuation, source fix, expectation/scope/pin/deadline/lease change or historical app reuse.

The new 12 host constructor checks and 18-method actual Editor preflight Passed. Both complete actual Editor rosters Passed:754/754 focused and755/755 resource, zero skips/inconclusive. All 23 focused fresh Player contracts Passed;36 resource/measurement/early Players never launched. Four of six planned builds Passed; two resource builds Blocked. Ten real production source-pin consumer cases Passed with identical before/after input hashes; pinned native installation Passed. The following resource compiler prerequisite failed **UnknownPrecompiledCapability: Unity.Collections.LowLevel.ILSupport** before creating a compiler snapshot. Its46 dependent cells remain Blocked. Evidence integrity does not promote these states to acceptance.

### Actual authority, pins and environment

All owning paths independently matched branch `codex/assembly-shadow-r01b-h1`, exact clean HEADs, canonical `git@github.com:night-outlook/<repo>.git` origins and remote tips before/after execution. Clean demo/package checkouts advanced by fast-forward only; native/IL2CPP heads stayed unchanged. Anchor `8d5297c375201687d17b91843ea0250ed90c0095` is an ancestor with documentation-only delta. Package delta from I is only its four synthetic test fixture files; production/native guards are unchanged. Original Local I reports and earlier checkpoint bytes were authenticated before execution. Git/submodule/worktree, source/package/build pins, manifests and generated-file bindings are retained in [preflight]({rel}/preflight) and original receipts.

| Owning repository path | Exact executed source |
| --- | --- |
{repoRows}

Environment: {mac}; arm64; Python3.14.6; SDK8.0.318/runtime8.0.21; PowerShell7.6.3; Apple clang21/macOS SDK26.5. Exact Unity2022.3.62f2/StandaloneOSXarm64 at `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`. SDK-only root `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`; no Unity6000 Editor ran. Pinned mscorlib SHA-256 `d89d5124cafb873b34c2eac68d2ece41d14fec10999baf0e4620276dff54ab83`. Scoped environment/argv/PID/start/end/exit are captured; no pre-existing Editor at entry; gate helper Off and no independent full-stage gate verdict claimed. No ordinary primary/control checkout was used or changed.

```text
{command}
```

Live root `{R}`; external capture `{P}`. [RETAINED_LIVE_ROOTS.json]({rel}/preflight/RETAINED_LIVE_ROOTS.json) records separate projects/SDKs/caches and clean detached reference worktrees at native1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad, IL2CPP a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c and graph-package b936a495ade1691ebb6f3bab8fdff3ef34f6f192. Focused schema2 receipts/nativeBinding authenticate four app inventories and arm64 binaries; GUID Unavailable where not provided. The resource SDK installation has a separately authenticated native inventory; **installation is not a fifth Player build**. No resource app/build GUID/bundle/manifest is inferred.

### Exact validation states and new coverage

| Validation | Factual state |
| --- | --- |
| Entry/final authority, pins, isolated source copies | Passed |
| Completion Python/retained R03 verifier contracts | Passed;73/183 source-defined host tests |
| Constructor helper host | Passed;12 checks, including original four-argument exception control; synthetic sources remain non-qualifying |
| Early real Editor regression | Passed;18 exact I-failing identities; replaces neither full roster |
| Static qualification/graphs/admission | Passed;32/9+9/35; no runtime/expansion authority |
| Real fixtures/audit/compiler consumers/lifecycle/API helper | Passed;15 DLLs,33 audits,33 consumers, valid/invalid lifetime probes and old-count two-CS0266 negative control |
| Focused four native builds and23 Players | Passed; fresh independent receipts |
| Full Editor | Passed;754 and755 exact cases, zero skips/inconclusive |
| J M01 original source-asset/GUID contract | Passed in the actual755-case resource Editor; historical H/I NoCoverage unchanged |
| Source-pin consumer | Passed;10 actual ShadowSourcePins.Read/JsonUtility cases, exact negative codes and unchanged four inputs |
| Resource original source preparation/native installation | Passed;527 source files/six frozen M01 files; installed inventory authenticated |
| Resource compiler policy/snapshot | Failed;declared IL support capability is absent from actual target inventory; no target snapshot emitted |
| Resource bundles/two builds/P05 prepare/compile/finalize | Blocked |
| P05 restore cell | Passed cleanup only:NoRecordedMutation/restorationCoverage=NotApplicable; no structural byte-restoration coverage |
| Production P01–P05 integration/input binding/14 resource Players | Blocked; M01/resource runtime and bundle acceptance remain NoCoverage |
| 12 unfenced R00/M06 observation processes and summary | Blocked; measurements.json/timing distributions/memory observations Unavailable, not zero |
| 10 early-startup Players | Blocked |
| Seal/post-run custody authentication | Passed integrity only |

[LI_CONTRACT_AUDIT.json]({rel}/preflight/LI_CONTRACT_AUDIT.json) replays the actual constructor/Editor and consumer contracts. All18 affected methods also Passed within both full rosters; there were1527 test executions over three Editor runs, not1527 unique identities. Before/after consumer inputs agree and bind exact original settings snapshots/pins/authority. Later authorized M02/M07 configuration changed settings and bootstrap scene; this does not rewrite preflight hashes or claim successful P05 restoration. LI-001/LI-002's fresh J regression Passed; I remains40 Passed/2 Failed/48 Blocked with its original18 Editor failures and seal intact.

{runtime}

93 owned command receipts:89 exit0/four exit1. Expected-negative compiler commands0054/0056/0061 Passed their contracts; product compiler0092 failed with Unity/outer exit1. All groups completed cleanly, no surviving group, timeout or cleanup error. Twelve Unity completion receipts retain birth-authenticated supervision; nine record one owned compiler retirement and three record zero. Zero actions is not missing cleanup when no owned compiler remained; raw flags/actions are preserved. Exact per-command start/end times, source bindings, stream hashes and exits remain in batch/commands; cell absence of execution is explicit Blocked/Unavailable.

All90 predetermined identities retain their original states:

| Cell | Original sealed state | Failure/dependency |
| --- | --- | --- |
{chr(10).join(cellRows)}

### Primary issue, limits and custody

[RETURN_TO_WEB.md](RETURN_TO_WEB.md) records **R03-LJ-001** with exact reproduction/log/source/policy/dependency hashes, scope and repair direction. [PRIMARY_ISSUES.json]({rel}/preflight/PRIMARY_ISSUES.json) preserves16 exact source blobs and six live resource snapshots. The filtered resource dependency profile and inherited five-plugin M02 declarations do not agree. Missing VisualScripting Antlr is a further source-supported risk, not a separately reproduced failure. A serialized complete Unity target inventory and compiler.json are Unavailable: the guard threw before compilation/success receipt emission. Command/log/cell remain preserved. No local source fix was made; profile/consumer contract closure needs Primary and a newly authorized tuple/root.

[POSTRUN_AUTHENTICATION.json]({rel}/preflight/POSTRUN_AUTHENTICATION.json) authenticates2753 indexed files/2754 exact safe archive members,90 individual cells and all original streams; all16523 older custody bindings are unchanged. [COMPLETION_RUNTIME_AUDIT.json]({rel}/preflight/COMPLETION_RUNTIME_AUDIT.json) records23 actual direct Players, zero resource/R00/early processes, four Passed read-only groups/three NotRun groups. Read-only audit network lookups initially timed out; same configured SSH identity/unchanged canonical origins recovered and exact tips were reverified. Audit attempts are retained separately from product results; no product deadlines changed.

Immutable [J checkpoint]({rel}/README.md) contains every indexed byte, top result/index/seal, exact ordered archive parts, [MANIFEST.sha256]({rel}/MANIFEST.sha256) and [ARCHIVE_RECONSTRUCTION_AUDIT.json]({rel}/ARCHIVE_RECONSTRUCTION_AUDIT.json). Original live archive and roots remain intact. No recompression, omitted indexed evidence or state/schema rewrite. Exact raw source/settings whitespace is preserved via narrowly authenticated snapshot attributes; owned prose is checked. Prior report body remains unchanged except its Current→Historical I heading.

| Original artifact | SHA-256 |
| --- | --- |
{hashRows}

Only the two Local reports/new J checkpoint are committed/pushed; no executable fix or other repository change. Final pushed publication identity is distinct from executed cebed900e6456433ac65db531262b60fd26766ee and is verified after push in `{P}/PUBLICATION_RECEIPT.json` and the final handoff, avoiding a commit self-hash cycle. R03Accepted=false;H2Passed=false;qualificationApproved=false;pureInterpreterExpansionEnabled=false;fullLegacyRegressionAcceptance=false;no production performance SLA or Human Review Gate approval. Exit exactly **Local Validation → Primary Implementation**, then stop.
'''
issue=issues['issues'][0];evidenceRows='\n'.join('| `'+x['path'].replace(str(R)+'/','')+'` | `'+x['sha256']+'` |' for x in issues['evidence']);returnText=f'''## Current return — R03 batch J: contract repairs Passed; resource capability profile requires Primary

**ReturnRequired;43 Passed/1 Failed/46 Blocked;seal Passed;one invocation PID89851, {interval}.** Four focused builds/23 Player contracts,18-method preflight, both754/755 Editor rosters with zero skips, ten actual source-pin consumer cases and native installation Passed. The resource compiler prerequisite failed before producing a target snapshot. Two resource builds and36 downstream Players were Blocked. Read [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md), [J checkpoint]({rel}/README.md), [LI_CONTRACT_AUDIT.json]({rel}/preflight/LI_CONTRACT_AUDIT.json) and [PRIMARY_ISSUES.json]({rel}/preflight/PRIMARY_ISSUES.json).

LI-001/LI-002 have fresh passing J regressions, including all18 affected methods in all three Editor runs and production consumer/installation success. Their original I failure/custody states remain unchanged. The J M01 source-asset/GUID test actually ran and Passed; M01 resource/bundle/Player acceptance remains NoCoverage.

### R03-LJ-001 — isolated resource dependency profile contradicts inherited precompiled capability declarations

**Exact reproduction already performed.** Use only the four executed commits/branch/paths recorded in LOCAL_VALIDATION.md, Unity2022.3.62f2 and SDK8.0.318. Invoke the prescribed command once in unused J; it has completed and must not be repeated:

```text
{command}
```

After preparation, actual source-pin consumer0090 and native Install0091 succeed. Command0092 runs `AssemblyShadowDemo.Editor.R03CompletionBuild.CompilerPreflight` against `{project if (project:=pathlib.Path(load(R/'resource-project.json')['projectPath'])) else ''}`. Its actual Unity/outer exits are1; completion is clean, zero compiler retirement actions, no survivor or timeout. Sealed `{R}/resource-logs/compiler.log`, line450:

```text
ShadowBuildException: UnknownPrecompiledCapability: Precompiled declaration is not a target compiler input: Unity.Collections.LowLevel.ILSupport
AssemblyShadowSettingsUtil.DeclareCapability ... AssemblyShadowSettingsUtil.cs:220
AssemblyShadowSettingsUtil.BuildCapabilities ... AssemblyShadowSettingsUtil.cs:206,134
AssemblyShadowSettingsUtil.CreatePolicyConfiguration ... AssemblyShadowSettingsUtil.cs:23
M07Build.ValidateCompilerInputs ... M07Build.cs:99
R03CompletionBuild.CompilerPreflight ... R03CompletionBuild.cs:109
```

**Root cause and why preparation missed it.** `fixture_project.dependencies:75–86` produces a narrowed package manifest (Unity modules/URP/test/UGUI plus JSON and pinned HybridCLR). Actual isolated manifest/resolved lock have neither `com.unity.collections` nor `com.unity.visualscripting`. `M07Build.Configure` inherits `M02Build.Configure`; M02 lines31–39 unconditionally declare Newtonsoft.Json, Unity.Burst.Unsafe, Unity.Collections.LowLevel.ILSupport, nunit.framework and Unity.VisualScripting.Antlr3.Runtime. Production `AssemblyShadowSettingsUtil.BuildCompilerInventory:124–174` derives its dictionary from actual active-target Player/PlayerWithoutTestAssemblies and references; DeclareCapability correctly rejects the missing declared plugin at220. This happens before `AssemblySnapshot.CompileWithOptions` (M07Build100), so it is a configuration/target-inventory mismatch rather than a demonstrated C# syntax/native compilation failure. Host/API compilation and the platform-pin consumer do not execute this policy/inventory contract.

Source/policy/manifest/lock snapshots are [issue-source-snapshot]({rel}/preflight/issue-source-snapshot) and [issue-resource-snapshot]({rel}/preflight/issue-resource-snapshot), with exact Git/live hashes in PRIMARY_ISSUES.json. No matching ILSupport or Antlr3 file was found in the retained isolated Assets/PackageCache. The guard directly proves the first name is absent from its actual Unity-derived dictionary. A full serialized CompilationPipeline inventory is Unavailable; do not treat the ScriptAssemblies listing as that inventory. Collections is not an explicit owning manifest dependency either; no historical provider/version is invented. VisualScripting1.9.4 is an explicit owning dependency excluded by the resource filter. Antlr3 is a further likely mismatch, not a second observed runtime failure.

**Affected scope and uncertainty.** Resource compiler snapshot, seven-bundle baseline, ON/OFF native builds, P05 mutation/structural compile/finalization, production P01–P05 graph/input binding and36 M07/R00/early processes remain unverified. Independent755-case Editor including M01 source-asset contract Passed; it cannot replace those stages. P05 restore only reports NoRecordedMutation/NotApplicable. M02/M07 configuration did modify allowed settings/bootstrap scene before the guard; no blanket no-mutation claim. No compiler.json was emitted before the exception; preserve Unavailable alongside original Failed command/log/cell. Downstream failures remain unknown.

**Concrete Primary direction.** Reconcile the reviewed resource dependency scope and complete precompiled capability profile with actual active-target compiler inventory. Choose coherent pinned dependencies or an explicit complete scope-specific configuration; retain UnknownPrecompiledCapability, classification, ordinary hot-update/plugin, closure and source/ownership guards. Audit every inherited declaration, including Antlr3, and capture the actual target inventory/positive-negative policy consumer contract before expensive phases. Do not simply delete the first failing name, make missing plugins optional, bypass classification or edit J's settings/expectations. Impact crosses resource provisioning and original production configuration; it cannot be closed locally inside the finished source-bound batch.

**Validation still required.** Primary source/host/compiler regression followed by a newly authorized fresh tuple/root: unchanged constructor/source-pin preflights, successful actual policy/target compiler snapshot, all90 cells/six builds,754/755 Editor/zero skips,59 Players, native bindings, P01–P05/structural byte restoration/production-entry integration, unfenced observations/M06/early and complete evidence seal. Preserve all six strict warm witnesses, five error16 rejection observations, positive C07, actual producer attribution and contaminated controls' Failed unisolated certificates. Do not rerun J or reuse its apps.

Key evidence paths relative to retained J root:

| Evidence | SHA-256 |
| --- | --- |
{evidenceRows}

All16523 prior custody bindings remain unchanged; J2753 indexed files/2754 archive members authenticate. No Local fix or further validation is authorized by this completed run. R03Accepted=false;H2Passed=false;qualificationApproved=false;PureInterpreter expansion disabled;no performance SLA;full-stage independent review remains open. Exit **Local Validation → Primary Implementation**.
'''
preservation={}
for name,heading,body in [('LOCAL_VALIDATION.md','# Local Validation report',local),('RETURN_TO_WEB.md','# Local Validation → Primary Implementation',returnText)]:
 q=D/'Docs/AssemblyShadow/Handoff'/name;old=q.read_text();blob=subprocess.check_output(['git','-C',str(D),'show','HEAD:Docs/AssemblyShadow/Handoff/'+name]);assert old.encode()==blob;first,tail=old.split('\n',1);tail=tail.lstrip('\n');history=tail.replace('## Current','## Historical',1);new=heading+'\n\n'+body+'\n'+history;assert new.endswith(history);preservation[name]={'priorSha256':hashlib.sha256(blob).hexdigest(),'priorCommit':'cebed900e6456433ac65db531262b60fd26766ee','historyTransformation':'Only first Current-to-Historical I heading; complete previous body preserved','newSha256':hashlib.sha256(new.encode()).hexdigest()};q.write_text(new)
(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps(preservation,indent=2)+'\n');size=(R/'evidence.tar.gz').stat().st_size
(C/'README.md').write_text(f'''# Immutable R03 completion batch J Local evidence

**ReturnRequired:43 Passed/1 Failed/46 Blocked;seal Passed;one invocation89851, {interval}.** Executed demo cebed900e6456433ac65db531262b60fd26766ee; exact other sources/branch/paths in [Local report](../../../../Handoff/LOCAL_VALIDATION.md). Four builds/23 focused Players,18 early and754/755 full Editor cases with zero skips,12 constructor and ten real source-pin checks Passed. Native installation Passed; resource CompilerPreflight fails UnknownPrecompiledCapability for the missing declared IL support plugin. Two resource builds/36 downstream Players Blocked. M01 source-asset Editor contract Passed; resource runtime remains NoCoverage. No retry or Local source fix.

Read [Primary return](../../../../Handoff/RETURN_TO_WEB.md), [PRIMARY_ISSUES.json](preflight/PRIMARY_ISSUES.json), [LI_CONTRACT_AUDIT.json](preflight/LI_CONTRACT_AUDIT.json). Preserve I/A–H and contaminated natural-control Failed warm certificates exactly. R03/H2/qualification approval and structural expansion remain false.

[batch/LOCAL_BATCH_RESULT.json](batch/LOCAL_BATCH_RESULT.json), [batch/BATCH_EXECUTION.json](batch/BATCH_EXECUTION.json), [batch/completion-plan.json](batch/completion-plan.json), [batch/evidence-index.json](batch/evidence-index.json) and [batch/seal-receipt.json](batch/seal-receipt.json) retain all original cells/receipts/streams/source/config/qualification/fixture/build/Editor/Player bytes. [POSTRUN_AUTHENTICATION.json](preflight/POSTRUN_AUTHENTICATION.json) authenticates2753 indexed files/2754 exact archive members and16523 unchanged prior custody bindings. [COMPLETION_RUNTIME_AUDIT.json](preflight/COMPLETION_RUNTIME_AUDIT.json), [PRODUCER_RUNTIME_AUDIT.json](preflight/PRODUCER_RUNTIME_AUDIT.json) and [REJECTION_RUNTIME_AUDIT.json](preflight/REJECTION_RUNTIME_AUDIT.json) preserve source-bound states and limits.

Live root `{R}` and roots in [RETAINED_LIVE_ROOTS.json](preflight/RETAINED_LIVE_ROOTS.json) remain intact. [ARCHIVE_TRANSPORT.json](ARCHIVE_TRANSPORT.json) and [REASSEMBLE_EVIDENCE.py](REASSEMBLE_EVIDENCE.py) reconstruct exact ordered parts at a new absolute unused destination: {size} bytes/SHA-256 `{auth['topLevelHashes']['evidence.tar.gz']}`. [ARCHIVE_RECONSTRUCTION_AUDIT.json](ARCHIVE_RECONSTRUCTION_AUDIT.json), [MANIFEST.sha256](MANIFEST.sha256) and [REPORT_HISTORY_PRESERVATION.json](REPORT_HISTORY_PRESERVATION.json) bind the publication without changing sealed bytes. Raw snapshots are read-only evidence, not extra execution. Later canonical reports may advance; these J bytes stay immutable.

Final pushed publication identity is externally verified in `{P}/PUBLICATION_RECEIPT.json` and final handoff, distinct from executed source. Exit exactly Local Validation → Primary Implementation.
''');shutil.copy2(P/'write-reports.py',C/'preflight/write-reports.py');print('Wrote factual current J reports, unchanged I history and immutable checkpoint README')
