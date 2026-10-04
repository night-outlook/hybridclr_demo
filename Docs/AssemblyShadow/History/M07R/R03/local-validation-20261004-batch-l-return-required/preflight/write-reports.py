"""Publish factual Local batch L conclusions while preserving previous report bodies."""
import pathlib,json,hashlib,subprocess,datetime
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261004L-fixed-image';R=P.parent/'R03LocalBatch-20261004L-fixed-image';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261004-batch-l-return-required';rel='../History/M07R/R03/'+C.name
load=lambda p:json.loads(pathlib.Path(p).read_text());sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
res=load(R/'LOCAL_BATCH_RESULT.json');auth=load(P/'POSTRUN_AUTHENTICATION.json');run=load(P/'runner-exit.json');issues=load(P/'PRIMARY_ISSUES.json');diag=load(P/'COMPILER_POLICY_AUDIT.json');fixed=load(P/'FIXED_IMAGE_AUDIT.json');li=load(P/'LI_CONTRACT_AUDIT.json');ret=load(P/'RETAINED_LIVE_ROOTS.json');obs=load(P/'INTEGRATED_OBSERVATIONS.json')
assert res['result']=='ReturnRequired' and auth['counts']=={'Passed':43,'Failed':1,'Blocked':46}
cmd=' '.join(run['command']);branch=res['repositories']['branch'];history={}
def preserve(name,body,title):
 q=D/'Docs/AssemblyShadow/Handoff'/name;old=subprocess.check_output(['git','-C',str(D),'show','HEAD:Docs/AssemblyShadow/Handoff/'+name],text=True);tail=old.split('\n',1)[1].lstrip('\n').replace('## Current','## Historical',1);assert q.read_text()==old
 q.write_text(title+'\n\n'+body.strip()+'\n\n'+tail);history[name]={'originalSha256':hashlib.sha256(old.encode()).hexdigest(),'historicalBodySha256':hashlib.sha256(tail.encode()).hexdigest(),'newSha256':sha(q),'preservation':'Previous complete report body retained; first Current heading changed to Historical only'}
repoRows='\n'.join('| `'+str(W/n)+'` | `'+res['repositories'][n]+'` |' for n in ['hybridclr_demo','hybridclr','hybridclr_unity','il2cpp_plus'])
buildRows='\n'.join('| '+b['role']+' | Passed | `'+b['receiptSha256']+'` | `'+b['binding']['sourcePinsSha256']+'` | '+str(b['binding']['verifiedNativeFiles'])+' |' for b in obs['builds'])
cellRows='\n'.join('| `'+c['id']+'` | '+c['result']+' |' for c in res['cells'])
hashRows='\n'.join('| `'+n+'` | `'+h+'` |' for n,h in auth['topLevelHashes'].items())
refRows='\n'.join('- `'+x['path']+'` detached at `'+x['commit']+'`, clean.' for x in ret['referenceWorktrees'])
local=f'''## Current run — R03 completion batch L, 2026-10-04 PDT: fixed-image preflight Passed; compiler-policy integration returns to Primary

**Result=ReturnRequired; 90 cells: 43 Passed / 1 Failed / 46 Blocked; sealStatus=Passed; runner exit 1. Exit Local Validation → Primary Implementation.** Exactly one fresh invocation, PID {run['pid']}, UTC {run['startedUtc']} → {run['endedUtc']} (06:07:50–06:17:15 PDT). No retry, manual blocked-stage continuation, source fix, source/pin/expectation/scope/deadline/lease change or historical app reuse.

Actual fixed-image authentication/materialization and all ten guarded Unity consumer controls Passed. Actual source-pin and capability preflights Passed. Current compiler execution emitted 24 assemblies, 189 references, symbols, Development mode and reflection-image evidence, then final policy validation Failed with 25 UnboundedManagedAcquisition plus 26 BootstrapReflection diagnostics. The isolated project omitted the owning 25-site raw-type configuration (R03-LL-001); a separate new OnQuit reflection consumer lacks an exact bootstrap entrypoint declaration (R03-LL-002). Four focused native builds and 23 fresh Players Passed; two resource builds and 36 downstream Players were Blocked. Both complete Editor rosters Passed, 754/754 and 755/755, zero skips/inconclusive. Integrity, preflights and emitted artifacts do not establish full runtime acceptance.

### Authority, paths, pins and environment

All four owning checkouts independently matched their expected paths, branch `{branch}`, clean repository-specific HEAD and exact canonical `git@github.com:night-outlook/<repo>.git` remote tip before/after execution. Mandatory top-level/branch/HEAD/status/remotes/worktrees/submodules and source/package/generated/build pins are retained in [preflight]({rel}/preflight). Only demo safely fast-forwarded from `4abd44f1fc6f81a75c76ae4975c28dd06a80b9f8`; siblings were unchanged. Executable/CI anchor `78ce9f81968a330b2801a93d4a426ffab7565b5f` is an ancestor with a documentation-only final delta. All 27981 previous evidence/custody bindings authenticated before/after L. K and earlier states and bytes are unchanged.

| Actual owning path | Exact executed source commit |
| --- | --- |
{repoRows}

Unity 2022.3.62f2 / StandaloneOSX arm64 at `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`; macOS 26.5.2 (25F84) arm64; .NET SDK 8.0.318 / runtime 8.0.21; Python 3.14.6; PowerShell 7.6.3; Apple clang 21 / macOS SDK 26.5. SDK-only root `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`; no Unity 6000 Editor launched. Pinned mscorlib SHA-256 `d89d5124cafb873b34c2eac68d2ece41d14fec10999baf0e4620276dff54ab83`. Exact argv/environment, start/end times, process IDs and exit/cleanup receipts accompany each command. No pre-existing Editor at entry; gate helper Off and host model unexposed. No ordinary primary or control checkout was used/changed. Canonical origins and configured SSH identity were preserved.

```text
{cmd}
```

### Fresh validation and evidence states

| Validation | Factual status and evidence |
| --- | --- |
| Completion host contracts and qualification | Passed host checks (148 completion Python cases, 32 static qualification cases); qualificationApproved=false, no interpreter expansion |
| Retained verifier / graphs / admission | Passed 183 verifier cases, baseline/candidate graphs 9/9, admission 35; host evidence only |
| Constructor and early real Editor | Passed 12 host cases and 18 actual Editor cases; [LI audit]({rel}/preflight/LI_CONTRACT_AUDIT.json) |
| Fixture, compiler consumers and lifecycle | Passed 33 fixture + 33 pinned compiler-consumer checks and valid/invalid actual Editor probes; invalid exits remain expected negatives |
| Complete helper/API compile | Passed full helper and dependencies; unchanged old-helper CS0266 reproduction is an expected-negative control |
| Four focused IL2CPP/native builds | Passed; schema-2 installed roots, native/source pins and output hashes retained below |
| Focused Editor | Passed 754/754, zero skips; original excluded M01 case remains NoCoverage within this focused scope |
| Resource Editor, independent of failed compiler stage | Passed 755/755, including original resource M01 fixture; does not promote full M01 Player acceptance |
| Focused Players | Passed 19 source-bound cases + four fresh producer diagnostics, 23 unique process IDs; six strict warm witnesses and positive C07 layout proof preserved |
| Producer diagnostics | Passed aggregate attribution, actual ArrayPool Gen2 producer observed in four controls; each unisolatedWarmCertificate=Failed remains Failed |
| Negative staging observation | Passed five cases with terminal error 16 unchanged through capacity control and repeated complete reads |
| Resource preparation and source-pin/install preflight | Passed, 537 verified copied files and six original M01 resources; ten actual source-pin controls and installed native binding retained |
| Actual target capability preflight | Passed all ten controls/five declaration decisions, 214 inventory rows/192 reference hashes; [capability audit]({rel}/preflight/CAPABILITY_CONTRACT_AUDIT.json) |
| Fixed image | Passed origin, materialization, ten host controls and ten actual Unity controls; [fixed-image audit]({rel}/preflight/FIXED_IMAGE_AUDIT.json) |
| Original resource compiler | Failed command 0099 in final policy validation; artifacts available, adapter compiler.json Unavailable; [policy audit]({rel}/preflight/COMPILER_POLICY_AUDIT.json) |
| Additional resource builds, bundles, production P01–P05 and 36 completion Players | Blocked; no resource runtime, performance, capacity or early-acquisition acceptance inferred |
| P05 cleanup cell | Passed NoRecordedMutation / restorationCoverage=NotApplicable; transaction restoration coverage NotRun |
| Seal, final authority and read-only evidence audits | Passed; original 90 cell states remain unchanged; read-only completion audit separately preserves four Passed / three NotRun checks |

Command receipts 0001–0100 retain all streams and clocks: 96 exit 0; expected-negative exits 1 at 0058 (invalid-key consumer), 0060 (invalid-key Editor), 0065 (old helper); product/compiler failure exit 1 at 0099. All owned groups were empty at completion and subsequent observation. Supervised Unity completion receipts retain original inner exits; no survivor identity is inferred retroactively for A/B. Exact XML SHA-256 focused `a4f6dec4aa4dfe00a663974b9368ef57f7886c056a5fad4678f7c7613237b4f2`, resource `3771fdbb5a174f421a24f57773104ddde56fc4482549f045c0614dd068f0cd43`.

### Build/native provenance

Receipts at `{R}/builds/<role>/build-receipt.json`; logs, config, installed before/after files, nativeBinding and linked Player hashes remain under those roles and isolated projects. Build GUID is unavailable in these receipts; no GUID-based equivalence claim. Role provenance and fresh process binding were audited independently.

| Role | Result | Receipt SHA-256 | Installed source-pin SHA-256 | Verified native files |
| --- | --- | --- | --- | --- |
{buildRows}

Candidate native/package/IL2CPP pins are the owning source commits above. The reference native build deliberately uses pinned historical native `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` and IL2CPP `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`; its receipt binds the current source-bound test overlay/package separately. Historical reference sources are not historical build/runtime-result reuse. Retained reference worktrees:

{refRows}

### Fixed-image and compiler-policy findings

Authoritative frozen input `{D}/Tools/AssemblyShadow/R02/fixtures/m00-frozen.dll.zlib.base64.txt` was authenticated against origin and the immutable historical archive, then materialized before first resource Unity command 0095. Image SHA-256 `{fixed['frozenImageSha256']}`, 4608 bytes; provider `{fixed['actualProvider']}`, MVID `{fixed['actualMvid']}`. Historical archive SHA-256 `{fixed['archiveSha256']}`. Reflection configuration stays `26837a5f710abae42a69a85ea2edf66939eff9afa6f6e8ce5b8e2cafc44f564a`; two fixed-image sites/provider-mode requirements unchanged. This is reused-audited input, no new M00 C# compilation and no historical Player-result reuse. Actual Development semantic hash `{fixed['actualPinnedSemanticHash']}`; host encoder observation `{fixed['hostEncoderSemanticObservation']}` makes no pinned-Mono semantic claim. No semantic/config/image hash rebinding occurred.

Actual fixed-image receipt SHA-256 `{fixed['actualReceiptSha256']}`, verification `{fixed['verificationSha256']}`. Preflight selects declared Development/Release modes; that alone is not current-provider proof. Subsequent current compiler/ILPP emitted snapshot `{diag['compilerArtifacts']['snapshot']['path']}` (SHA-256 `{diag['compilerArtifacts']['snapshot']['sha256']}`), snapshotHash `{diag['compilerArtifacts']['snapshotHash']}`, current provider DLL `{diag['compilerArtifacts']['currentProvider']['sha256']}` and exact reflection image. All 213 DLLs and 89 PDB files authenticate against snapshot records and the sealed index. Final compiled policy remains Failed, playerBuildSucceeded=false; raw-type proof directory and adapter compiler.json are Unavailable. Emitted artifacts are preserved as Available, not a standalone Passed provider/build verdict.

R03-LL-001: all 25 diagnostic Development operation positions/method hashes/signatures match owning `ProjectSettings/AssemblyShadowRawTypeAdmissions.json`; its isolated counterpart is Missing and fixture selection omits it. R03-LL-002: the literal `R03CompletionExecution::OnQuit` Type.GetType acquisition has no exact dependency declaration; five same-target declarations name other call sites. Both need Primary integration work. [RETURN_TO_WEB.md](RETURN_TO_WEB.md) includes actionable reproductions, evidence hashes, impact, repair direction and remaining uncertainty. No bounded Local fix was made.

### Custody, publication and exit

Live root `{R}` is retained with projects/Library/HybridCLRData/apps/reference worktrees referenced by receipts; no cross-root cache/app reuse. Portable raw copy, command streams, host/build/Editor/Player evidence, origin/materialization, source snapshots and read-only audits are in [immutable L checkpoint]({rel}/README.md). Live preflight `{P}`. Ledger/index/archive/seal authenticated, 3195 indexed files and 3196 unique archive members. Original 174423350-byte archive is retained and transported as three exact ordered byte parts with original SHA/seal unchanged; reconstruction is audited at a new external path. Checkpoint manifest binds copied bytes, not a new validation batch. Earlier 27981 bindings remain untouched. Exact allowed resource mutations are isolated settings/bootstrap-scene configuration; no P05 transaction ran.

| Original top-level artifact | SHA-256 |
| --- | --- |
{hashRows}

Only Local-owned `LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md` and this new checkpoint are publication scope. Publication checks authenticate JSON, manifests, links, source blobs, staged bytes and whitespace. The executed demo commit above is the source pin, not the later documentation/evidence publication head. Final pushed heads/status/remote tips for all four repositories are verified after publication in `{P}/PUBLICATION_RECEIPT.json` and the final short handoff; this avoids a self-referential commit hash in the checkpoint.

**R03Accepted=false; H2Passed=false; qualificationApproved=false; PureInterpreter expansion disabled; fullLegacyRegressionAcceptance=false.** No production performance SLA, independent full-stage acceptance or Human Review Gate readiness is established. Missing downstream coverage remains Blocked/NotRun/Unavailable as recorded. Meaningful independent checks are complete; no source fix or further batch is authorized. **Exit A: Local Validation → Primary Implementation.**

### All 90 original cell states

Exact receipts are `{R}/cells/<id>.json`, mirrored in the checkpoint batch/cells; command operations, UTC start/end, output and hashes are bound by each receipt and BATCH_EXECUTION.json.

| Cell | Original state |
| --- | --- |
{cellRows}
'''
retbody=f'''## Current return — R03 batch L: fixed-image controls Passed; two compiler-policy integration defects require Primary

**ReturnRequired; 90 cells: 43 Passed / 1 Failed / 46 Blocked; seal Passed; one invocation PID24279, 2026-10-04 06:07:50–06:17:15 PDT.** Four focused native builds, 23 fresh Players, early 18 Editor cases and full 754/755 Editor rosters (zero skips) Passed. Frozen-image authentication/materialization and all ten actual guarded consumer controls Passed. Final resource compiler policy Failed; two resource builds and 36 downstream Players Blocked. No Local source fix or retry. Read [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md), [L checkpoint]({rel}/README.md), [PRIMARY_ISSUES.json]({rel}/preflight/PRIMARY_ISSUES.json) and [COMPILER_POLICY_AUDIT.json]({rel}/preflight/COMPILER_POLICY_AUDIT.json). K and earlier evidence states remain unchanged.

### Exact reproduction already performed

Use the four repository paths/branches/source commits in LOCAL_VALIDATION.md with Unity 2022.3.62f2 and SDK 8.0.318. The prescribed invocation below is complete. Inspect command 0099 / resource-compiler cell; do not rerun L or mutate its retained root. A Primary repair needs a newly authorized source-bound batch.

```text
{cmd}
```

Failure log `{R}/resource-logs/compiler.log`, SHA-256 `{diag['compilerLog']['sha256']}`; command receipt `{diag['compilerCommand']['path']}`, SHA-256 `{diag['compilerCommand']['sha256']}`. Snapshot and reflection artifacts are Available with exact hashes in the policy audit, but final compiled policy Failed. Adapter compiler.json is Unavailable; no resource app was built. The strict guards correctly exposed these input/consumer integration defects.
'''
for i in issues['issues']:
 e=i['evidence'];retbody+=f'''
### {i['id']} — {i['symptom']}

**Evidence.** {e['excerpt']}

Exact diagnostic line(s): `{e.get('diagnosticLines',e.get('diagnosticLine'))}` in the log above. The policy audit records all 51 diagnostics, missing-file checks, exact method/operation matches, copied dependencies, captured compiler mode and 302 DLL/PDB hashes. Git-authenticated source snapshots are retained at [issue-source-snapshot]({rel}/preflight/issue-source-snapshot); owning source pins are explicit in each snapshot record.

**Most likely root cause / why the integration allowed it.** {i['mostLikelyRootCause']}

**Affected scope.** {i['affectedScope']}

**Concrete Primary direction.** {i['recommendedImplementationDirection']}

**Remaining uncertainty.** {i['remainingUncertainty']}

**Required validation after repair.** {i['validationRequiredAfterFix']}
'''
retbody+='''
R03-LL-001 call chain: fixture_project.SETTINGS/select → absent configuration → ShadowRawTypeAdmissionEvidence.CompilationDefines/Capture/ReadAndVerify → no verified raw admissions → ShadowAssemblyPolicyValidator.ValidateReflection. R03-LL-002 call chain: R03CompletionExecution.OnQuit literal Type.GetType → compiler reference → BootstrapIsolationRule.IsApprovedReflection exact call-site check. Both fail in M07Build.ValidateCompilerInputs line 106 after compiler snapshot emission. Repair input/consumer closure; preserve existing finite policy and strict guards. Do not hide errors by removing preserved consumers, weakening policy, copying caches or treating declarations as acceptance.

Frozen image reuse is authenticated input only. Current-provider ILPP emitted files; final policy success, resource bundles/Players, production P01–P05, M06 measurements and supplemental runtime behavior remain unestablished. Cleanup Passed means NoRecordedMutation / restoration NotApplicable; transaction restoration remains NotRun. Contaminated producer certificates remain Failed despite passing diagnostic attribution. Qualification and acceptance remain false.

Only the two Local reports/new immutable checkpoint are committed/pushed. Exact later publication heads are recorded in the final four-repository handoff/external publication receipt; no validation is attributed to that documentation commit. **Exit A: Local Validation → Primary Implementation. R03Accepted=false; H2Passed=false; qualificationApproved=false; PureInterpreter expansion disabled. Stop; no further Local batch.**
'''
preserve('LOCAL_VALIDATION.md',local,'# Local Validation report');preserve('RETURN_TO_WEB.md',retbody,'# Local Validation → Primary Implementation');(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps(history,indent=2)+'\n')
(C/'README.md').write_text(f'''# Immutable R03 Local batch L checkpoint

Executed once at demo source `96eaa341d8eea476aec72506bac1a2d0456e24d7`, Unity 2022.3.62f2 / SDK 8.0.318, 2026-10-04 06:07:50–06:17:15 PDT. **ReturnRequired: 43 Passed / 1 Failed / 46 Blocked; 90 cells; seal Passed.** Four focused builds and 23 Players Passed; 754/755 full Editor rosters zero skips. Fixed-image controls Passed. Final resource compiler policy Failed; two resource builds/36 downstream Players Blocked. R03-LL-001 omitted raw-type configuration and R03-LL-002 undeclared OnQuit call site require Primary. No source fix/retry.

Read [Local report](../../../../Handoff/LOCAL_VALIDATION.md), [Primary return](../../../../Handoff/RETURN_TO_WEB.md), [result](batch/LOCAL_BATCH_RESULT.json), [ledger](batch/BATCH_EXECUTION.json), [index](batch/evidence-index.json), [seal](batch/seal-receipt.json), [issues](preflight/PRIMARY_ISSUES.json), [policy diagnosis](preflight/COMPILER_POLICY_AUDIT.json), [fixed image audit](preflight/FIXED_IMAGE_AUDIT.json), [custody audit](preflight/POSTRUN_AUTHENTICATION.json), [manifest](MANIFEST.sha256) and [archive transport](ARCHIVE_TRANSPORT.json). Full batch/commands/builds/host/Editor/Player and compiler snapshot artifacts are copied byte-for-byte. Reconstruction at an unused external path is checked in [archive audit](ARCHIVE_RECONSTRUCTION_AUDIT.json).

Live batch `{R}` and preflight `{P}` remain retained; source-bound apps/projects/reference worktrees/Library/HybridCLRData are listed in [retained roots](preflight/RETAINED_LIVE_ROOTS.json). Frozen historical M00 bytes are reused-audited input, no new M00 compilation or historical runtime reuse. Compiler DLLs/snapshot/reflection image are Available, final policy Failed; adapter compiler receipt Unavailable. Source snapshots and read-only audit tools are custody material, not extra validation execution.

All earlier 27981 evidence bindings and complete previous report bodies are preserved. The three ordered archive parts reconstruct the original 174423350 bytes/SHA-256 `{auth['topLevelHashes']['evidence.tar.gz']}` with unchanged seal. R03Accepted=false; H2Passed=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; PureInterpreter expansion disabled. **Local Validation → Primary Implementation.** Source commits differ from the later Local publication commit, whose final pushed head is externally verified after publication.
''')
print('Updated two Local reports preserving historical bodies; checkpoint README/history receipt written')
