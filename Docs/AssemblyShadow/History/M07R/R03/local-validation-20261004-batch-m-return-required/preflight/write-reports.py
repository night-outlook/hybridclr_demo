"""Local-owned factual reports and immutable checkpoint; preserve historical bodies."""
import pathlib,json,hashlib,subprocess,datetime,zoneinfo
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261004M-policy';R=P.parent/'R03LocalBatch-20261004M-policy';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261004-batch-m-return-required';rel='../History/M07R/R03/'+C.name
load=lambda p:json.loads(pathlib.Path(p).read_text());sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r=load(R/'LOCAL_BATCH_RESULT.json');a=load(P/'POSTRUN_AUTHENTICATION.json');run=load(P/'runner-exit.json');cp=load(P/'COMPILER_POLICY_AUDIT.json');nb=load(P/'NATIVE_LAYOUT_DIAGNOSIS.json');rb=load(P/'RESOURCE_BUILD_RECOVERY_AUDIT.json');li=load(P/'LI_CONTRACT_AUDIT.json');fixed=load(P/'FIXED_IMAGE_AUDIT.json');issues=load(P/'PRIMARY_ISSUES.json');obs=load(P/'INTEGRATED_OBSERVATIONS.json');env=load(P/'environment.json');history={}
assert a['counts']=={'Passed':48,'Failed':1,'Blocked':41} and cp['state']=='Passed' and rb['state']=='Passed'
cmd=' '.join(run['command']);tz=zoneinfo.ZoneInfo('America/Los_Angeles');times=' → '.join(datetime.datetime.fromisoformat(run[k]).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S %Z') for k in ['startedUtc','endedUtc'])
def save(name,title,body):
 q=D/'Docs/AssemblyShadow/Handoff'/name;old=subprocess.check_output(['git','-C',str(D),'show','HEAD:Docs/AssemblyShadow/Handoff/'+name],text=True);assert q.read_text()==old;tail=old.split('\n',1)[1].lstrip('\n').replace('## Current','## Historical',1);q.write_text(title+'\n\n'+body.strip()+'\n\n'+tail);history[name]={'originalSha256':hashlib.sha256(old.encode()).hexdigest(),'historicalBodySha256':hashlib.sha256(tail.encode()).hexdigest(),'newSha256':sha(q),'preservation':'Previous full report body unchanged except first Current heading changed to Historical'}
repos='\n'.join('| `'+str(W/n)+'` | `'+r['repositories'][n]+'` |' for n in ['hybridclr_demo','hybridclr','hybridclr_unity','il2cpp_plus'])
hashes='\n'.join('| `'+n+'` | `'+h+'` |' for n,h in a['topLevelHashes'].items());cells='\n'.join('| `'+c['id']+'` | '+c['result']+' |' for c in r['cells']);builds='\n'.join('| '+b['role']+' | `'+b['receiptSha256']+'` | `'+b['binding']['sourcePinsSha256']+'` | '+str(b['binding']['verifiedNativeFiles'])+' |' for b in obs['builds']);resbuilds='\n'.join('| '+b['role']+' | `'+b['playerReceiptSha256']+'` | `'+b['buildGuid']+'` | `'+b['nativeLibrarySha256']+'` |' for b in rb['builds']);xml='\n'.join('| '+e['folder']+' | '+str(e['count'])+'/'+str(e['count'])+'; zero skips | `'+e['xmlSha256']+'` |' for e in li['fullEditors'])
local=f'''## Current run — R03 completion batch M, 2026-10-04 PDT: compiler-policy/linked repairs Passed; P05 layout comparison returns to Primary

**ReturnRequired; 90 cells: 48 Passed / 1 Failed / 41 Blocked; sealStatus=Passed; runner exit 1. Exit A: Local Validation → Primary Implementation.** Exactly one fresh invocation PID {run['pid']}, {times}; UTC {run['startedUtc']} → {run['endedUtc']}. No retry, source fix, pin/scope/expectation/timeout/cleanup/lease changes or earlier app reuse.

The fresh original compiler gate Passed with current captured 25-site proof and all 16 guard controls. Both resource Player builds and their subsequent linked 25-site proofs Passed. All six build roles, 23 focused fresh Players, early 18-method Editor preflight and complete 754/755 Editor rosters Passed with zero skips/inconclusive. P05 later failed `NativeLayoutIncompatible` when comparing linked baseline against compiler target; fixture finalization and the 36 resource/measurement/early-startup processes were Blocked. Scoped settings restoration independently verified exact original bytes. New defect R03-LM-001 requires Primary; passing compile/link evidence does not establish complete R03 acceptance.

### Source authority and environment

Each repository independently matched expected path, branch `codex/assembly-shadow-r01b-h1`, clean status, canonical `git@github.com:night-outlook/<repo>.git` identity and exact remote tip before/after execution. Demo safely fast-forwarded from `4df1ef8de7ffb4a585e1d3ddfd1b16c024e1bc60`; three siblings were unchanged. Executable/CI anchor `bb4bb31132ab1aaafa0a6c38cd3b5120142ff6b7` is an ancestor and the final delta is documentation-only. Mandatory Git checks, worktree/submodule/package/native/generated-file pins and operations are retained in [preflight]({rel}/preflight). All 34561 earlier custody bindings authenticated before/after M; L and earlier bytes/states remain unchanged.

| Actual repository path | Exact executed source commit |
| --- | --- |
{repos}

Unity 2022.3.62f2 / StandaloneOSX arm64 at `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`; macOS 26.5.2 (25F84) arm64; SDK 8.0.318/runtime 8.0.21; Python 3.14.6; PowerShell 7.6.3; Apple clang 21/macOS SDK 26.5. SDK-only root `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`; no Unity6000 Editor launched. Pinned mscorlib SHA-256 `d89d5124cafb873b34c2eac68d2ece41d14fec10999baf0e4620276dff54ab83`. Exact versions/argv/environment/start/end/PID/exit/output/hash records are in environment.json, runner receipts and each command.json. No existing Editor at entry; gate helper Off; effective host model unexposed, no guessed identity or independent full-stage gate claim. Ordinary primary/control checkouts unused and unchanged.

```text
{cmd}
```

### Validation states and limits

| Scope | Factual result |
| --- | --- |
| Host contracts | Passed 172 completion Python, 183 retained verifier, 32 qualification, 12 constructor, 20 capability and 10 fixed-image host cases; graphs 9+9/admission 35 |
| Q22 | Passed two byte-identical complete reports from the same four prepared DLLs; unchanged before/after hashes. [Current audit]({rel}/preflight/COMPILER_POLICY_AUDIT.json) binds input/report hashes; qualificationApproved=false |
| Fixture/compiler lifecycle/API prerequisites | Passed 33 fixture/33 pinned compiler-consumer checks, valid/invalid actual Editor probes, full helper/API compilation; expected negative exits remain distinct |
| Focused builds and Players | Passed four isolated native roles and 23 unique fresh Player PIDs (19 cases + four producer diagnostics) |
| Warm/C07/rejection | Passed six unchanged strict warm witnesses, positive C07 physical proof and five non-mutating rejected-stage observations preserving terminal error 16 |
| Producer controls | Passing diagnostic attribution observes actual ArrayPool Gen2 admissions in four controls; every contaminated unisolatedWarmCertificate=Failed remains Failed |
| Original resource prerequisites | Passed preparation, ten actual source-pin controls, native install, ten actual capability controls/five declaration decisions, fixed-image authentication/materialization/ten actual image controls |
| Current compiler policy | Passed original full gate, current 25-site captured/recomputed proof, 16 exact controls and unchanged eight immutable inputs; compile-only linkedProofExecuted/runtimeAcceptance/expansion flags false |
| Original linked builds | Passed both feature-ON/OFF roles; actual current linked raw proofs each 25 sites independently verified with snapshot/reflection/native metadata and installed inventory |
| P05 public compiler | Emitted successful p05-compile-receipt/snapshot; Available. Whole resource-p05-compile cell Failed later during NativeLayoutAdmissionSnapshot / atomic fixture construction |
| P05 recovery | Passed exact original settings byte restoration after recorded mutation; original/reserialized bytes and production/wrapper receipts retained |
| P05 finalization/full fixture graph/production integration | Blocked; no successful atomic P05 manifest, full graph or runtime receipt inferred |
| 36 completion Players / performance / early-startup | Blocked; zero resource/R00/early processes launched; no performance SLA, capacity/startup or broad M06 runtime acceptance |
| Seal/custody and audits | Passed 10259 indexed files / 10260 unique archive members; all original states preserved. Read-only completion aggregate separately records four Passed/three NotRun; independent linked/recovery audit Passed |

| Actual Editor roster | Result | XML SHA-256 |
| --- | --- | --- |
{xml}

Focused M01 exclusion remains NoCoverage in that roster. Resource 755 roster includes original M01 asset/GUID coverage; Editor success is not bundle/Player acceptance. Command receipts 0001–0106 retain clocks/streams and cleanup: expected negative exits at 0058 (invalid-key consumer), 0060 (invalid-key Editor), 0065 (old-helper CS0266); actual product failure at 0104. No timeout or survivor on the failing command. Recorded Unity inner exits and cleanup actions are unchanged; no historical A/B survivor identity inferred.

### Fresh build and input provenance

Focused receipts `{R}/builds/<role>/build-receipt.json` bind project/output/native roots, before/after installed source, schema-2 nativeBinding and linked DLL/Player hashes. Build GUID is unavailable for these four receipts; no GUID equivalence claim.

| Focused role | Receipt SHA-256 | Source-pin SHA-256 | Verified native files |
| --- | --- | --- | --- |
{builds}

Candidate source/native pins are the four owning commits above. Reference Release deliberately uses verified historical native `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` / IL2CPP `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`; current overlay/package is separately bound. Exact detached reference source worktrees and all live roots are retained in [RETAINED_LIVE_ROOTS.json]({rel}/preflight/RETAINED_LIVE_ROOTS.json). This is source reuse, not historical build/runtime-result reuse.

| Original resource role | Player receipt SHA-256 | Build GUID | Native library SHA-256 |
| --- | --- | --- | --- |
{resbuilds}

[RESOURCE_BUILD_RECOVERY_AUDIT.json]({rel}/preflight/RESOURCE_BUILD_RECOVERY_AUDIT.json) records exact paths, input snapshot/native metadata hashes, actual ON/OFF arguments, linked proof hashes, installed native binding and restoration. Resource builds use no R03 probe/producer lease. Settings final SHA-256 `{rb['restoration']['finalSettingsSha256']}` equals the backed-up original; preserved Unity serialization SHA-256 `{rb['restoration']['unityReserializedBytesSha256']}` is separately bound. Original defines/state/production/wrapper receipt hashes remain distinct.

### Compiler-policy repair and new failure

All six policy configurations are immutable and recorded in resource-project.json/compilerPolicyInputs. Original raw file SHA-256 `0958d5c98ee7cdfa3662f9942687926343de95523398451c423ee5de38aa5a4c` and exact dependency SHA-256 `f0f0b9fe51afaaaa5879bf5cb70f8f7116f5d60ee2164c8e3f3cb5be5af3d36d` were preserved through phases. Compiler contract `{cp['contract']['path']}` SHA-256 `{cp['contract']['sha256']}`; current snapshot `{cp['compilerSnapshot']['path']}` SHA-256 `{cp['compilerSnapshot']['sha256']}`; captured compiled proof `{cp['capturedCompiledProof']['sha256']}`. All 213 compiler modules, mode/proof and 16 control mutations/outcomes authenticate. Subsequent actual linked proofs were verified independently; this is fresh M evidence, not Primary's historical L-byte replay or reclassification of L.

Frozen M00 image `{fixed['frozenImageSha256']}` (4608 bytes) is reused-audited input authenticated against its pinned original archive/member and materialized before resource Unity. Provider/MVID/mode/configuration/semantic hashes are unchanged. [FIXED_IMAGE_AUDIT.json]({rel}/preflight/FIXED_IMAGE_AUDIT.json) distinguishes host encoder semantics from actual pinned-Unity semantics. No new M00 compilation or historical runtime-result reuse is claimed.

R03-LM-001: conservative admission compares linked baseline DLL `{nb['linkedBaselineDll']['sha256']}` against compiler target `{nb['targetDll']['sha256']}`. Read-only CLI metadata shows all 43 differing bases keep the same qualified names but change scope mscorlib → netstandard; 18 analogous declared field-scope differences are retained. Examples: InternalEntry System.Object parent, M06InternalNode.Changed System.Action, m07InlineValues List<T>. EvolutionSignature/TypeKey use raw assembly qualifiers without a verified cross-input forwarding context. This is the most likely cause of the widespread ParentChanged/signature errors. The audit does not prove forwarding equivalence, all type compatibility or native allocation/offset safety. No guard bypass or Local source fix. [RETURN_TO_WEB.md](RETURN_TO_WEB.md) provides reproduction, source chain, exact evidence and Primary repair direction.

### Custody, publication and exit

Live root `{R}` and preflight `{P}` remain retained, including projects/Library/HybridCLRData/reference sources and all evidence-referenced inputs. [Immutable M checkpoint]({rel}/README.md) contains exact indexed bytes, source snapshots, policy/Q22/linked/recovery/diagnosis audits and additional authenticated baseline PlayerInputs needed for the failure. These added custody copies are not new compilation or test execution. All earlier 34561 bindings and full report histories are preserved.

| Original artifact | SHA-256 |
| --- | --- |
{hashes}

The original {int((R/'evidence.tar.gz').stat().st_size)}-byte archive is unchanged, transported in exact ordered byte parts and reconstructed at a new external path. Manifest/JSON/links/staged bytes/source provenance and whitespace checks precede commit. Only the two Local reports/new M checkpoint are owned changes. The source pin is the executed commit, distinct from the later Local publication HEAD. Final clean status/remote tips/latest pushed heads for all four repos are externally verified in `{P}/PUBLICATION_RECEIPT.json` and the final short handoff, avoiding self-referential commit hashes.

**R03Accepted=false; H2Passed=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; PureInterpreter expansion disabled. No SLA or Human Review Gate readiness.** Independent meaningful checks completed; Failed/Blocked/NotRun/Unavailable/NoCoverage/reused-audited states remain distinct. **Exit A: Local Validation → Primary Implementation. Stop; no further batch or non-trivial Local implementation.**

### All 90 original cells

Receipts `{R}/cells/<id>.json`, mirrored in checkpoint batch/cells, bind operation/dependencies/command clock/output/hashes via BATCH_EXECUTION.json.

| Cell | Original state |
| --- | --- |
{cells}
'''
issue=issues['issues'][0];ev=issue['evidence'];returnbody=f'''## Current return — R03 batch M: LL repair Passed; P05 framework identity comparison requires Primary

**ReturnRequired; 48 Passed / 1 Failed / 41 Blocked; 90 cells; seal Passed.** One invocation PID{run['pid']}, {times}. Six fresh build roles, 23 focused Players, early 18-method Editor preflight and full 754/755 zero-skip rosters Passed. Current compiler 25-site proof/16 controls and both subsequent linked proofs Passed. P05 failed native-layout admission; scoped settings recovery Passed. The 36 downstream Players did not execute. Preserve all L/earlier states unchanged.

Read [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md), [M checkpoint]({rel}/README.md), [PRIMARY_ISSUES.json]({rel}/preflight/PRIMARY_ISSUES.json), [NATIVE_LAYOUT_DIAGNOSIS.json]({rel}/preflight/NATIVE_LAYOUT_DIAGNOSIS.json), [compiler audit]({rel}/preflight/COMPILER_POLICY_AUDIT.json) and [linked/recovery audit]({rel}/preflight/RESOURCE_BUILD_RECOVERY_AUDIT.json).

### R03-LM-001 — linked baseline/compiler target framework scopes trigger NativeLayoutIncompatible

**Exact reproduction already performed.** Use the four executed source heads/paths/branch in LOCAL_VALIDATION.md with Unity 2022.3.62f2 / SDK 8.0.318. The single invocation below is complete; do not retry M or change its root. Inspect resource-p05-compile and command0104:

```text
{cmd}
```

**Symptom and evidence.** {issue['symptom']} Log `{ev['log']}`, SHA-256 `{ev['logSha256']}`, line {ev['line']}: `{ev['excerpt']}`. Command `{ev['command']}`, SHA-256 `{ev['commandSha256']}`; exit1/no timeout/no surviving group. Public p05-compile-receipt.json and snapshot are Available; the later atomic P05 fixture receipt/manifest is Unavailable.

The call chain is R03CompletionBuild.StructuralCompile → M07StructuralResources.Compile → M07Build.BuildFixtureFromSnapshot → ShadowPatchManifestBuilder.BuildCore → NativeLayoutAdmissionSnapshot.AnalyzeAndRequire → NativeLayoutAdmissionValidator.Compare. Baseline manifest and full linked PlayerInputs are copied without changes in checkpoint preflight/layout-inputs; target/state snapshots and 28 Git-authenticated sources are preserved. Exact original source/live paths/hashes and input provenance are in NATIVE_LAYOUT_DIAGNOSIS.json / PRIMARY_ISSUES.json.

Linked baseline `{nb['linkedBaselineDll']['path']}`, SHA-256 `{nb['linkedBaselineDll']['sha256']}`; target `{nb['targetDll']['path']}`, SHA-256 `{nb['targetDll']['sha256']}`. The 43 observed differing base references preserve qualified type names with mscorlib/netstandard scope differences. Eighteen declared field-scope differences include Action, generic List<T> and async framework types. These metadata observations are not a forwarding/native safety certificate.

**Most likely root cause / design boundary.** {issue['mostLikelyRootCause']}

**Affected scope.** {issue['affectedScope']}

**Concrete Primary direction.** {issue['recommendedImplementationDirection']}

**Remaining uncertainty.** {issue['remainingUncertainty']}

**Validation required after repair.** {issue['validationRequiredAfterFix']}

Settings restoration after failure is independently Passed with exact backed-up original bytes and retained Unity serialization; full P05 transaction/finalization and resource graph remain Blocked. No Local source fix, additional Unity launch or failure reclassification occurred. R03Accepted=false; H2Passed=false; qualificationApproved=false; PureInterpreter expansion disabled. **Exit A: Local Validation → Primary Implementation.**
'''
save('LOCAL_VALIDATION.md','# Local Validation report',local);save('RETURN_TO_WEB.md','# Local Validation → Primary Implementation',returnbody);(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps(history,indent=2)+'\n')
(C/'README.md').write_text(f'''# Immutable R03 Local completion batch M checkpoint

**ReturnRequired:48 Passed/1 Failed/41 Blocked;90 cells;seal Passed.** Exactly one invocation at demo `301493290706e81437db1ac6a31977e9930d9fc6`, {times}, pinned Unity2022.3.62f2/SDK8.0.318. Six fresh build roles,23 Players,early18/full754/755 zero-skip Editor rosters Passed. Fresh compiler25-site proof/16 controls and both linked proofs Passed. P05 native-layout screen Failed;36 downstream Players Blocked. Exact settings recovery Passed. R03-LM-001 requires Primary; no source fix/retry.

Read [Local report](../../../../Handoff/LOCAL_VALIDATION.md), [Primary return](../../../../Handoff/RETURN_TO_WEB.md), [result](batch/LOCAL_BATCH_RESULT.json), [ledger](batch/BATCH_EXECUTION.json), [index](batch/evidence-index.json), [seal](batch/seal-receipt.json), [issues](preflight/PRIMARY_ISSUES.json), [layout diagnosis](preflight/NATIVE_LAYOUT_DIAGNOSIS.json), [compiler audit](preflight/COMPILER_POLICY_AUDIT.json), [linked/recovery audit](preflight/RESOURCE_BUILD_RECOVERY_AUDIT.json), [custody](preflight/POSTRUN_AUTHENTICATION.json), [manifest](MANIFEST.sha256), [archive transport](ARCHIVE_TRANSPORT.json) and [reconstruction](ARCHIVE_RECONSTRUCTION_AUDIT.json).

All 10259 indexed files, command streams, host/Editor/build/Player and current policy/snapshot/Q22 evidence are preserved byte-for-byte. Additional baseline PlayerInputs copies authenticate the exact linked DLLs used by the failed screen; these are custody copies, not new execution. Live root `{R}` / preflight `{P}` and receipt-referenced Library/HybridCLRData/apps/reference roots remain retained. All34561 earlier bindings/report bodies unchanged. The original archive SHA-256 `{a['topLevelHashes']['evidence.tar.gz']}` reconstructs from ordered byte parts with unchanged seal.

Frozen historical M00 is reused-audited input, not new compilation/runtime-result reuse. Current linked proof is fresh; blocked graph/runtime states remain Blocked. Contaminated unisolated certificates remain Failed. R03Accepted=false;H2Passed=false;qualificationApproved=false;fullLegacyRegressionAcceptance=false;PureInterpreter expansion disabled. **Local Validation → Primary Implementation.** Final publication head differs from executed source and is verified externally after push.
''')
print('Two Local reports/new M README written; full historical bodies preserved')
