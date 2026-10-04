"""Single-use factual K publication; preserve the complete prior report body."""
import pathlib,json,hashlib,subprocess,datetime,zoneinfo,collections,shutil
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261003K-capabilities';R=P.parent/'R03LocalBatch-20261003K-capabilities';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261003-batch-k-return-required'
load=lambda p:json.loads(pathlib.Path(p).read_text());sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();result=load(R/'LOCAL_BATCH_RESULT.json');auth=load(P/'POSTRUN_AUTHENTICATION.json');cap=load(P/'CAPABILITY_CONTRACT_AUDIT.json');li=load(P/'LI_CONTRACT_AUDIT.json');issues=load(P/'PRIMARY_ISSUES.json');env=load(P/'environment.json');inv=load(P/'runner-exit.json');assert auth['status']==cap['status']==li['status']=='Passed' and auth['counts']=={'Passed':43,'Failed':1,'Blocked':46};assert inv['batchInvocations']==1 and inv['exitCode']==1 and len(issues['issues'])==1
rel='../History/M07R/R03/'+C.name;tz=zoneinfo.ZoneInfo('America/Los_Angeles');start=datetime.datetime.fromisoformat(inv['startedUtc']);end=datetime.datetime.fromisoformat(inv['endedUtc']);interval=start.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')+'–'+end.astimezone(tz).strftime('%H:%M:%S %Z');command=' '.join(inv['command']);repoRows='\n'.join('| `'+str(W/n)+'` | `'+result['repositories'][n]+'` |' for n in ['hybridclr_demo','hybridclr','hybridclr_unity','il2cpp_plus']);hashRows='\n'.join('| `'+n+'` | `'+h+'` |' for n,h in auth['topLevelHashes'].items());cellRows=[]
for c in result['cells']:
 detail=c.get('error','') if c['result']=='Failed' else ('Prerequisite did not pass: '+', '.join(c['dependencies']) if c['result']=='Blocked' else '')
 cellRows.append('| `'+c['id']+'` | '+c['result']+' | '+detail.replace('|','\\|')+' |')
local=f'''## Current run — R03 completion batch K, 2026-10-03 PDT: capability repair Passed; missing fixed-image input returns to Primary

**Result=ReturnRequired; 90 cells:43 Passed /1 Failed /46 Blocked; sealStatus=Passed; runner exit1. Exit Local Validation → Primary Implementation.** Exactly one fresh invocation PID{inv['pid']}, {interval}; UTC {inv['startedUtc']}–{inv['endedUtc']}. No retry, blocked-stage manual continuation, source fix, expectation/scope/pin/deadline/lease change or historical app reuse.

The actual Unity capability consumer Passed all ten policy controls and five declaration decisions. It captured22 Player and21 PlayerWithoutTestAssemblies rows,214 derived inventory rows and192 reference-file hashes, exact manifest/lock closure and full guarded policy. Resource compilation then failed in ReflectionBindingsILPostProcessor because the isolated source copy lacked the pinned M00 fixed image. Four focused native builds and23 fresh Players Passed; the two resource builds and36 resource/measurement/early processes were Blocked. Both complete Editor rosters Passed:754/754 focused and755/755 resource, zero skips/inconclusive. Integrity and passing inventory evidence do not promote blocked runtime states.

### Actual authority, pins and environment

Each owning repository independently matched the expected path, branch `codex/assembly-shadow-r01b-h1`, clean HEAD, canonical `git@github.com:night-outlook/<repo>.git` origin and exact remote tip before and after execution. Only the demo advanced by safe fast-forward from71bddefd86a3b718d9d36b3edc2d88cd21db1e92; all three sibling heads were unchanged. Executable/CI anchor `f00626dca8591496f2676b629104fd688bf06dce` is an ancestor and its final transport delta is documentation-only. Git status/submodule/worktree/source/package/build pins and commands are recorded in [preflight]({rel}/preflight). All22181 prior evidence/custody bindings authenticated before and after K; J and all earlier checkpoints remain unchanged.

| Owning repository path | Exact executed source |
| --- | --- |
{repoRows}

Environment: macOS26.5.2 (25F84) arm64; Python3.14.6; SDK8.0.318/runtime8.0.21; PowerShell7.6.3; Apple clang21/macOS SDK26.5. Unity2022.3.62f2/StandaloneOSXarm64 at `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`. SDK-only root `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`; no Unity6000 Editor ran. Pinned mscorlib SHA-256 `d89d5124cafb873b34c2eac68d2ece41d14fec10999baf0e4620276dff54ab83`. Scoped argv/environment/PID/start/end/exit retained. No pre-existing Editor at entry; gate helper Off; effective host model unexposed and no guessed model or full-stage gate verdict. No ordinary primary or control checkout used or changed. Canonical origins/configured SSH identity preserved; bounded network transport did not change product timeouts.

```text
{command}
```

Live root `{R}`; external capture `{P}`. [RETAINED_LIVE_ROOTS.json]({rel}/preflight/RETAINED_LIVE_ROOTS.json) records isolated projects, Library/HybridCLRData/caches and separate clean detached reference worktrees at native1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad, IL2CPP a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c and graph-package b936a495ade1691ebb6f3bab8fdff3ef34f6f192. Four schema2/nativeBinding receipts authenticate exact app files/arm64 binaries and installed SDK roots. Resource native installation Passed separately; it is not a fifth build. Unprovided focused build GUIDs remain Unavailable; no resource app/GUID/bundle/manifest is inferred.

### Exact validation states and evidence boundaries

| Validation | Factual result |
| --- | --- |
| Entry/final authority, pins, isolated copies | Passed |
| Completion Python/retained R03 verifier contracts | Passed;107/183 host cases |
| New actual-helper capability profile host | Passed;20 checks; host evidence, not Unity inventory |
| Constructor host/early actual Editor | Passed;12 host/18 exact affected methods |
| Static qualification/graphs/admission | Passed;32/9+9/35; no runtime/expansion authority |
| DLL fixtures/audit/pinned consumers/lifecycle/full API helper | Passed;15 fixtures/33 audits/33 consumers, valid and expected-invalid probes; unchanged old-helper two-CS0266 control |
| Four focused builds/23 Players | Passed; all fresh, source-bound |
| Full Editor rosters | Passed;754+755 cases, zero skips/inconclusive |
| M01 original source-asset/GUID Editor contract | Passed in755-case resource run; resource/bundle/runtime acceptance NoCoverage |
| Actual production source-pin consumer | Passed;ten exact cases and identical four before/after inputs |
| Resource preparation/native installation | Passed;531 copied source files/six frozen M01 files; installed inventory authenticated |
| Actual target capability/policy preflight | Passed;ten controls, five decisions,43 compiler array rows/214 derived inventory/192 reference hashes; complete guarded policy |
| Resource compiler snapshot | Failed;ILPP cannot read pinned M00 fixed image; no successful compiler/snapshot receipt |
| Bundles/two resource native builds/P05 prepare/compile/finalize | Blocked |
| P05 restore cell | Passed cleanup only:NoRecordedMutation/restorationCoverage=NotApplicable; no byte-restoration proof |
| Production P01–P05 integration/binding/14 resource Players | Blocked; original runtime coverage NoCoverage |
|12 unfenced R00/M06 observation processes/summary | Blocked; timings/memory/measurements.json Unavailable, not zero |
|10 early-startup Players | Blocked |
| Seal/post-run custody authentication | Passed integrity only |

[CAPABILITY_CONTRACT_AUDIT.json]({rel}/preflight/CAPABILITY_CONTRACT_AUDIT.json) independently reconstructs the full inventory from both actual Unity arrays, authenticates all referenced DLL bytes and control inputs, checks the production-derived policy and verifies unchanged configured inputs. Newtonsoft.Json, Unity.Burst.Unsafe and nunit.framework are present fixed Runtime/non-shadow/non-bootstrap plugins; Collections.ILSupport and VisualScripting.Antlr3 are absent as explicitly excluded providers. The exact package closure is11 non-module packages,32 built-in modules and the pinned HybridCLR package. Actual command0094 supervised Unity Passed; configured-input hashes before/after match. LJ-001 has fresh K passing repair evidence; J retains its original failure and unavailable target snapshot. This preflight explicitly did not compile a snapshot or prove resource/runtime acceptance.

[LI_CONTRACT_AUDIT.json]({rel}/preflight/LI_CONTRACT_AUDIT.json) authenticates12 constructor-host and18 early actual Editor methods plus ten actual ShadowSourcePins.Read/JsonUtility controls/native installation. All18 methods also Passed within both full rosters:1527 test executions across three runs, not1527 unique identities. Original settings snapshots bind pre-install before/after hashes; later authorized M02/M07 configuration changed ShadowSettings/bootstrap scene without retroactively changing those preflight hashes. No P05 transaction ran. I/J and all earlier evidence retain their original states.

[PRODUCER_RUNTIME_AUDIT.json]({rel}/preflight/PRODUCER_RUNTIME_AUDIT.json) confirms six strict isolated warm witnesses, ten probes/fifty spans, positive C07 physical/publication/business proof and actual natural producer attribution with four identified admissions. Each of the four natural controls retains **unisolatedWarmCertificate=Failed** while diagnostic verification Passed. The bounded lease is diagnostic, not production GC/performance acceptance. [REJECTION_RUNTIME_AUDIT.json]({rel}/preflight/REJECTION_RUNTIME_AUDIT.json) confirms five non-mutating negative-stage observations: terminal error16/state8/unpublished/RestartRequired unchanged through capacity-2, two full owned-byte reads, raw projection and recovery. No counter relaxation, warm-up/GC/lease extension or terminal restoration.

96 command receipts:92 exit0/four exit1. Expected-negative compiler commands0056/0058/0063 Passed their contracts; actual product command0095 failed with Unity/outer exit1. All groups completed cleanly, no survivors, timeout or cleanup error. Thirteen supervised Unity completion receipts retain nine single owned-compiler retirements and four zero-action completions; no action is required when no authenticated compiler remains. Exact command start/end, native/source bindings, streams and exits are retained in batch/commands. Absence of dependent execution remains Blocked/Unavailable.

All90 predetermined cells retain sealed states:

| Cell | Original sealed state | Failure/dependency |
| --- | --- | --- |
{chr(10).join(cellRows)}

### Non-trivial return, custody and publication

[RETURN_TO_WEB.md](RETURN_TO_WEB.md) records R03-LK-001 with exact reproduction, log excerpts, pins, file hashes, source chain, missing generated input and concrete Primary direction. [PRIMARY_ISSUES.json]({rel}/preflight/PRIMARY_ISSUES.json) preserves22 exact Git source snapshots/six live resource snapshots. A historical ignored owning M00 image is separately snapshotted for diagnosis only:4608 bytes/hash9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27. It was never copied into or used by K, and its generation provenance is Unavailable from this Git handoff. Matching bytes do not permit historical artifact reuse. No Local code fix; provisioning and generated-input authority require Primary. Failed compiler output is not a valid snapshot; compiler.json and snapshot.json remain Unavailable.

[POSTRUN_AUTHENTICATION.json]({rel}/preflight/POSTRUN_AUTHENTICATION.json) authenticates2817 indexed files/2818 exact archive members,90 cells/all command streams and22181 unchanged prior custody bindings. [COMPLETION_RUNTIME_AUDIT.json]({rel}/preflight/COMPLETION_RUNTIME_AUDIT.json) records23 actual direct Players, zero resource/R00/early processes, four Passed read-only groups and three NotRun groups. Read-only replay never launches additional validation.

Immutable [K checkpoint]({rel}/README.md) preserves every indexed byte, original result/index/seal and exact ordered archive parts, [MANIFEST.sha256]({rel}/MANIFEST.sha256), [ARCHIVE_TRANSPORT.json]({rel}/ARCHIVE_TRANSPORT.json) and [ARCHIVE_RECONSTRUCTION_AUDIT.json]({rel}/ARCHIVE_RECONSTRUCTION_AUDIT.json). All original live roots/archive remain intact. No recompression or state/schema rewrite. Raw whitespace is byte-preserved through exact authenticated snapshot attributes; owned prose retains whitespace checks. Previous report bodies remain unchanged except their first Current→Historical J headings.

| Original artifact | SHA-256 |
| --- | --- |
{hashRows}

Only the two Local reports and new K checkpoint are committed/pushed. No executable/native/package/pin fix. The final publication commit is verified after push in `{P}/PUBLICATION_RECEIPT.json` and final handoff, distinct from executed1704c0393dd0c7717502e336232a0d951422e767; this avoids a self-hash commit cycle. R03Accepted=false;H2Passed=false;qualificationApproved=false;pureInterpreterExpansionEnabled=false;fullLegacyRegressionAcceptance=false;no performance SLA/Human Review Gate approval. Exit exactly **Local Validation → Primary Implementation**, then stop.
'''
issue=issues['issues'][0];ev='\n'.join('| `'+r['path'].replace(str(R)+'/','')+'` | `'+r['sha256']+'` |' for r in issues['evidence']);returnText=f'''## Current return — R03 batch K: LJ capability repair Passed; fixed-image provisioning needs Primary

**ReturnRequired;43 Passed/1 Failed/46 Blocked;seal Passed;one invocation PID{inv['pid']}, {interval}.** Four focused builds/23 Players,18-method early and754/755 full Editor rosters with zero skips,12 constructor/20 actual-helper host checks, ten production source-pin controls and ten actual target policy controls Passed. The two resource builds and36 downstream Players were Blocked after the actual resource compiler failed. Read [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md), [K checkpoint]({rel}/README.md), [PRIMARY_ISSUES.json]({rel}/preflight/PRIMARY_ISSUES.json) and [CAPABILITY_CONTRACT_AUDIT.json]({rel}/preflight/CAPABILITY_CONTRACT_AUDIT.json). J's original failure/custody remain unchanged; LJ-001 has fresh passing K preflight evidence.

### R03-LK-001 — Git-only fresh fixture omits pinned M00 image required by reflection ILPP

**Exact reproduction already performed.** Use the four executed commits/branch/paths recorded in LOCAL_VALIDATION.md, Unity2022.3.62f2/SDK8.0.318. The prescribed one invocation below is complete; do not retry K or reuse its root/apps:

```text
{command}
```

Actual source-pin consumer0092, native Install0093 and capability consumer0094 Passed. Command0095 invokes `AssemblyShadowDemo.Editor.R03CompletionBuild.CompilerPreflight` against `{project if (project:=pathlib.Path(load(R/'resource-project.json')['projectPath'])) else ''}`. Actual Unity/outer exits1; supervised completion clean; no survivor/timeout. Raw `{R}/resource-logs/compiler.log`, first ILPP error line724 and terminal line1523:

```text
ReflectionBindingsILPostProcessor: error AssemblyShadow reflection binding failed:
System.IO.DirectoryNotFoundException: Could not find a part of the path
.../projects/resource-complete/Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes
System.IO.File.ReadAllBytes
ReflectionBindingsILPostProcessor.ProcessAssembly
ShadowBuildException: CompileFailed: No Player assemblies emitted.
AssemblySnapshot.CompileCore ... AssemblySnapshot.cs:246
M07Build.ValidateCompilerInputs ... M07Build.cs:101
R03CompletionBuild.CompilerPreflight ... R03CompletionBuild.cs:115
```

**Direct cause, root cause and why preflights missed it.** `fixture_project.py` names M00 in ROOTS, but source_catalog copies only Git HEAD ls-tree entries. The candidate HEAD has zero tracked M00 entries; `.gitignore:104` excludes `/Assets/StreamingAssets/AssemblyShadow/`. The required image does exist as an ignored4608-byte owning artifact with SHA-256 `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`; it is absent in the fresh isolated project and was not used by K. Merely selecting a directory does not validate its required generated-input closure.

The unchanged six-site `ProjectSettings/AssemblyShadowReflectionBindings.json` has two FixedAssemblyBytes sites (`m00-normal-hot-update-image` and `h1-count-ordinary-witness-image`) pointing to that same pinned image/hash/provider/Development+Release semantic contracts. `AssemblySnapshot.CompileCore:239–246` adds the raw-config hash define then calls actual CompilePlayerScripts. `ReflectionBindingsILPostProcessor.ProcessAssembly:58–60` reads every fixed-image site for each targeted assembly before ValidateImageEvidence; absent input causes the observed DirectoryNotFoundException and ILPP error. Unity emits no successful Player assembly set, so the production snapshot guard reports CompileFailed. Editor compilation skips this Player-only ILPP path; successful Editor/API/inventory checks do not exercise its ancillary image bytes. `BaselineBuild.Build:89–98` normally produces/copies the M00 hot DLL after PrebuildCommand.GenerateAll; the completion fixture has no corresponding authenticated prerequisite before CompilerPreflight. That historical full Player producer is not permission for Local to run an extra batch/build.

**Available evidence and impact.** Actual capability receipt/control verification Passed:22+21 compiler array rows,214 reconstructed inventory rows,192 DLL reference hashes, full guarded policy/all five dispositions/ten exact controls with unchanged configured inputs. The compiler failure is a separate generated-input problem. Resource bundles, two native builds, P05 mutation/compile/restoration/finalization, production P01–P05/input graph and36 resource/R00/early processes remain unverified. Independent755-case resource Editor including M01 source-asset/GUID Passed; resource/runtime remains NoCoverage. P05 restore is cleanup-only NoRecordedMutation/NotApplicable. No successful compiler.json or snapshot.json was emitted; partial compile output is not promoted. Settings/bootstrap configuration changed only within authorized isolated scope.

[PRIMARY_ISSUES.json]({rel}/preflight/PRIMARY_ISSUES.json) authenticates22 source/six resource snapshots plus the raw exception/command/cell. [issue-source-snapshot]({rel}/preflight/issue-source-snapshot) and [issue-resource-snapshot]({rel}/preflight/issue-resource-snapshot) retain exact bytes. [Ignored historical input snapshot]({rel}/preflight/ignored-historical-input/AssemblyShadowBaseline.HotUpdate.dll.bytes) is diagnostic only, with no authoritative producer/source/build receipt and never used in K. Preserve this provenance limitation; no parent/worktree/cache search is an execution fallback.

**Concrete Primary direction.** Add an explicit source/build-bound immutable fixed-image provision or generation prerequisite before reflection-enabled compilation. Audit every FixedAssemblyBytes site and referenced generated artifact; require exact configured hash, provider identity and compiler-mode semantic proof. Use a reviewed reproducible producer or committed/published authoritative fixture with complete provenance. Do not blindly copy ignored historical cache bytes, remove reflection sites, disable ILPP/binding controls, change pinned hashes to accept arbitrary bytes or make image inputs optional. Add actual absent/mutated/provider/mode controls and successful Unity compiler consumption. This crosses fixture provisioning and generated-input authority; no non-trivial Local repair is authorized.

**Remaining uncertainty/required validation.** Fresh reproducibility of the pinned4608-byte image is unknown; subsequent reflection/graph/native/runtime defects remain untested. After Primary repair and host/compiler checks, authorize a new exact tuple/root: all90 cells/six builds/59 Players,754+755 zero-skip rosters, unchanged constructor/source-pin/capability controls and runtime warm/producer/C07/rejection expectations, M01/P01–P05 structural byte restoration/production-entry integration/unfenced observations/M06/early and complete seal. Preserve K/J/all earlier evidence and all contaminated controls' Failed unisolated certificates.

| Evidence relative to live K root where applicable | SHA-256 |
| --- | --- |
{ev}

All22181 prior custody bindings and2817 indexed K files authenticate. No Local fix or further validation authorized by this finished run. R03Accepted=false;H2Passed=false;qualificationApproved=false;PureInterpreter expansion disabled;full-stage independent review remains open;no performance SLA. Exit **Local Validation → Primary Implementation**.
'''
preservation={}
for name,heading,body in [('LOCAL_VALIDATION.md','# Local Validation report',local),('RETURN_TO_WEB.md','# Local Validation → Primary Implementation',returnText)]:
 q=D/'Docs/AssemblyShadow/Handoff'/name;blob=subprocess.check_output(['git','-C',str(D),'show','HEAD:Docs/AssemblyShadow/Handoff/'+name]);assert q.read_bytes()==blob;first,tail=blob.decode().split('\n',1);history=tail.lstrip('\n').replace('## Current','## Historical',1);new=heading+'\n\n'+body+'\n'+history;assert new.endswith(history);q.write_text(new);preservation[name]={'priorSha256':hashlib.sha256(blob).hexdigest(),'priorCommit':'1704c0393dd0c7717502e336232a0d951422e767','historyTransformation':'Only first Current-to-Historical J heading; entire prior body preserved','newSha256':sha(q)}
(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps(preservation,indent=2)+'\n')
(C/'README.md').write_text(f'''# Immutable R03 completion batch K Local evidence

**ReturnRequired:43 Passed/1 Failed/46 Blocked;seal Passed;one invocation PID{inv['pid']}, {interval}.** Executed demo1704c0393dd0c7717502e336232a0d951422e767; exact sibling sources/paths in [Local report](../../../../Handoff/LOCAL_VALIDATION.md). Four builds/23 Players,18 early and754/755 full Editor cases with zero skips,12 constructor/20 actual-helper host checks, ten source-pin and ten actual capability controls Passed. Resource CompilerPreflight failed when reflection ILPP read the absent pinned M00 image; two builds/36 Players Blocked. M01 source-asset Editor Passed; runtime NoCoverage. No retry or Local fix.

Read [Primary return](../../../../Handoff/RETURN_TO_WEB.md), [PRIMARY_ISSUES.json](preflight/PRIMARY_ISSUES.json), [CAPABILITY_CONTRACT_AUDIT.json](preflight/CAPABILITY_CONTRACT_AUDIT.json) and [LI_CONTRACT_AUDIT.json](preflight/LI_CONTRACT_AUDIT.json). Preserve every earlier checkpoint and natural controls' Failed unisolated warm certificates. R03/H2/qualification approval and expansion remain false.

[batch/LOCAL_BATCH_RESULT.json](batch/LOCAL_BATCH_RESULT.json), [batch/BATCH_EXECUTION.json](batch/BATCH_EXECUTION.json), [batch/completion-plan.json](batch/completion-plan.json), [batch/evidence-index.json](batch/evidence-index.json) and [batch/seal-receipt.json](batch/seal-receipt.json) retain original states/receipts/streams/source/config/qualification/fixture/build/Editor/Player evidence. [POSTRUN_AUTHENTICATION.json](preflight/POSTRUN_AUTHENTICATION.json) authenticates2817 indexed files/2818 archive members and22181 unchanged prior custody bindings. [COMPLETION_RUNTIME_AUDIT.json](preflight/COMPLETION_RUNTIME_AUDIT.json), [PRODUCER_RUNTIME_AUDIT.json](preflight/PRODUCER_RUNTIME_AUDIT.json) and [REJECTION_RUNTIME_AUDIT.json](preflight/REJECTION_RUNTIME_AUDIT.json) are read-only source-bound replays.

Live root `{R}` and all roots in [RETAINED_LIVE_ROOTS.json](preflight/RETAINED_LIVE_ROOTS.json) remain intact. [ARCHIVE_TRANSPORT.json](ARCHIVE_TRANSPORT.json)/[REASSEMBLE_EVIDENCE.py](REASSEMBLE_EVIDENCE.py) reconstruct exact ordered parts at a new absolute unused destination: {(R/'evidence.tar.gz').stat().st_size}bytes, SHA-256 `{auth['topLevelHashes']['evidence.tar.gz']}`. [ARCHIVE_RECONSTRUCTION_AUDIT.json](ARCHIVE_RECONSTRUCTION_AUDIT.json), [MANIFEST.sha256](MANIFEST.sha256) and [REPORT_HISTORY_PRESERVATION.json](REPORT_HISTORY_PRESERVATION.json) authenticate publication. Ignored M00 diagnostic bytes were never used as build input and have no authoritative generation provenance. Raw source snapshots are evidence only. Later canonical reports may advance; these K bytes remain immutable.

Final pushed publication identity is verified externally in `{P}/PUBLICATION_RECEIPT.json` and final handoff, distinct from executed source. Exit exactly Local Validation → Primary Implementation.
''')
shutil.copy2(P/'write-reports.py',C/'preflight/write-reports.py');print('Wrote factual K reports and checkpoint README; preserved complete J history')
