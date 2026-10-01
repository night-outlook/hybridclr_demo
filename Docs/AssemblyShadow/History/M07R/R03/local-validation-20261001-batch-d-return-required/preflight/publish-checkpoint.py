import hashlib,json,pathlib,shutil,subprocess
D=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');R=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001D-build-api');P=R.parent/'Preflight-R03LocalBatch-20261001D-build-api';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261001-batch-d-return-required'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
assert subprocess.check_output(['git','-C',str(D),'status','--short'],text=True)=='';C.mkdir(exist_ok=False)
idx=json.loads((R/'evidence-index.json').read_text());hashes=json.loads((P/'POSTRUN_AUTHENTICATION.json').read_text())['topLevelHashes']
for name in [f['path'] for f in idx['files']]+['LOCAL_BATCH_RESULT.json','evidence-index.json','seal-receipt.json']:
 dest=C/'batch'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,dest)
parts=C/'batch/evidence.tar.gz.parts';parts.mkdir();partRecords=[]
with (R/'evidence.tar.gz').open('rb') as f:
 number=0
 while data:=f.read(64*1024*1024):
  p=parts/('part-%03d'%number);p.write_bytes(data);partRecords.append({'path':str(p.relative_to(C)),'size':len(data),'sha256':sha(p)});number+=1
combined=hashlib.sha256()
for part in partRecords:
 with (C/part['path']).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):combined.update(b)
assert combined.hexdigest()==hashes['evidence.tar.gz']
(C/'ARCHIVE_TRANSPORT.json').write_text(json.dumps({'kind':'BytePreservingArchiveTransport','reason':'Original 163272284-byte archive exceeds GitHub single-blob limit; sealed bytes are split for Git publication only','originalLivePath':str(R/'evidence.tar.gz'),'originalSha256':hashes['evidence.tar.gz'],'originalSize':(R/'evidence.tar.gz').stat().st_size,'partSizeLimit':64*1024*1024,'parts':partRecords,'concatenationSha256Verified':True,'originalSealUnchanged':True},indent=2)+'\n')
(C/'REASSEMBLE_EVIDENCE.py').write_text('''"""Reconstruct the exact sealed archive at a new, caller-specified path."""
import hashlib,json,pathlib,sys
root=pathlib.Path(__file__).resolve().parent
manifest=json.loads((root/'ARCHIVE_TRANSPORT.json').read_text())
if len(sys.argv)!=2:raise SystemExit('Usage: python3 REASSEMBLE_EVIDENCE.py /absolute/unused/evidence.tar.gz')
target=pathlib.Path(sys.argv[1]);assert target.is_absolute() and not target.exists()
whole=hashlib.sha256();size=0
with target.open('xb') as output:
 for part in manifest['parts']:
  h=hashlib.sha256();n=0
  with (root/part['path']).open('rb') as source:
   for block in iter(lambda:source.read(1048576),b''):
    h.update(block);whole.update(block);output.write(block);n+=len(block)
  assert h.hexdigest()==part['sha256'] and n==part['size'];size+=n
assert whole.hexdigest()==manifest['originalSha256'] and size==manifest['originalSize']
print('Authenticated archive:',target,whole.hexdigest(),size)
''')
shutil.copytree(P,C/'preflight')
for name in ['Tools/AssemblyShadow/R03/run_local.py','Tools/AssemblyShadow/R03/build_api.py','Tools/AssemblyShadow/R03/input_validation.py','Tools/AssemblyShadow/R03/unity_command.py','Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs','Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md']:
 dest=C/'source-snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/name,dest)
src=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity/Tests/Editor/AssemblyShadow/ResourceAbiTests.cs');dest=C/'source-snapshot/hybridclr_unity/Tests/Editor/AssemblyShadow/ResourceAbiTests.cs';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
(C/'.gitattributes').write_text('''# Preserve binary evidence, archive parts and immutable original Unity output.
*.dll binary
*.dylib binary
*.tar.gz binary
batch/evidence.tar.gz.parts/* binary
batch/**/*.log whitespace=-blank-at-eol,-blank-at-eof
batch/**/*.meta whitespace=-blank-at-eol,-blank-at-eof
batch/**/*.asset whitespace=-blank-at-eol,-blank-at-eof
''')
(C/'README.md').write_text('''# R03 Local batch D — immutable ReturnRequired checkpoint

**12 Passed / 5 Failed / 19 Blocked; focused seal Passed; runner exit1.** Exactly one invocation, 2026-10-01 16:47:28.470800–16:53:21.060233 UTC (09:47:28–09:53:21 America/Los_Angeles). Executed demo `faa351d6854e71982ca047b994fb8579475f542a`, tested source anchor `5931ada3c70958a7c6132219e059a42ee3cecbd0`. The later Local publication HEAD does not replace executed-source provenance.

Read [LOCAL_VALIDATION.md](../../../../Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB.md](../../../../Handoff/RETURN_TO_WEB.md). R03Accepted=false; H2Passed=false; PureInterpreter expansion disabled; fullLegacyRegressionAcceptance=false. No independent full-stage review or acceptance is claimed.

- [LOCAL_BATCH_RESULT.json](batch/LOCAL_BATCH_RESULT.json), [BATCH_EXECUTION.json](batch/BATCH_EXECUTION.json) and all36 cells retain original classifications. [evidence-index.json](batch/evidence-index.json) and [seal-receipt.json](batch/seal-receipt.json) remain unchanged. Custody authenticated1736 indexed files/1737 exact archive members.
- Original live `evidence.tar.gz` is preserved unchanged. Its163272284 bytes exceed GitHub's single-blob limit, so the committed [ARCHIVE_TRANSPORT.json](ARCHIVE_TRANSPORT.json) binds three byte-preserving parts in `batch/evidence.tar.gz.parts/`. Their ordered concatenation is exactly SHA-256 `989d7211e1772efc2b20f13b5354e533bc4760adf93fa4a45b1d5176ed17ff53`. [REASSEMBLE_EVIDENCE.py](REASSEMBLE_EVIDENCE.py) reconstructs only at a new caller-specified absolute path and verifies every part/whole hash. This transport does not modify the runner seal or omit any archived member. All indexed files, including four complete Player apps, are also committed individually.
- [build-api/inputs.json](batch/build-api/inputs.json) and [build-api/results.json](batch/build-api/results.json) retain425 input bindings/115 defines, five compiler responses, three actual package DLLs and the whole helper DLL. Four positive compiles passed; the byte-bound complete C helper returned the exact two expected CS0266 errors with no output. Commands0051–0055 preserve original exits.
- All earlier fixture/audit/consumer/lifecycle checks remain, including33 audited inputs/consumers and valid-invalid actual Editor probes. All60 command receipts/streams and seven unity-completion receipts are retained. Only0048/0050/0055 are explicit expected-negative commands; normal builds and EditMode returned exit0 with clean outer lifetime.
- All four build receipts report Passed, nonGeneratedCorePreserved=true, errors0 and actual retained ARM64 apps. Their runner cells remain Failed because two hash-matching install receipts exist: canonical SDK and stripped-AOT generated copy. Read-only diagnosis authenticated Player inventories and found the canonical SDK matches installedAfter, while the generated copy differs in one generated file. It does not override the original failed provenance gate.
- [editor-results.xml](batch/editor-results.xml) records755 cases:754 Passed, zero Failed, one Ignored. All35 mandatory R03 contracts and target-cycle regression Passed. The frozen M01 demo-resource asset test remains Skipped/NoCoverage; aggregate root Skipped:Ignored failed the strict runner cell. All19 Players remain Blocked/NotRun.
- [POSTRUN_AUTHENTICATION.json](preflight/POSTRUN_AUTHENTICATION.json) authenticates sealed/live bytes,36-cell equality,60 command streams, toolchain/consumer/API bindings, lifetime completion and1280 prior custody files unchanged. [DIAGNOSTIC_FINDINGS.json](preflight/DIAGNOSTIC_FINDINGS.json) binds detailed native receipt copies/inventory differences, read-only lipo observations, exact XML/skip reason and mandatory-ID audit.
- [RETAINED_LIVE_ROOTS.json](preflight/RETAINED_LIVE_ROOTS.json) retains135 compiled/intermediate bindings, six isolated project/cache roots and three clean detached reference worktrees. Excluded Library/HybridCLRData native/generated roots remain live. `source-snapshot/` retains executed verifier/build code, Primary handoff and skipped-test source. [MANIFEST.sha256](MANIFEST.sha256) binds every checkpoint file except itself. Scoped whitespace attributes preserve captured Unity output bytes.

Live root `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001D-build-api`; preflight `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261001D-build-api`. A/B/C and earlier R02/H1 evidence remain unchanged. No root may be reused to bypass provenance. No Local source fix, retry, blocked Player launch, acceptance/expectation/timeout/cleanup change occurred. Local Validation → Primary Implementation; stop.
''')
local='''## Current run — R03 batch D, 2026-10-01: native artifacts produced; provenance and Editor scope gates fail

**Local Validation → Primary Implementation: ReturnRequired;36 cells:12 Passed,5 Failed,19 Blocked; focused seal Passed; runner exit1.** Exactly one fresh invocation,2026-10-01 16:47:28.470800–16:53:21.060233 UTC (09:47:28–09:53:21 America/Los_Angeles), runner PID6095. No Local fix, retry, manual blocked-case execution or expectation/timeout/cleanup relaxation occurred.

### Executed authority, tooling and operations

Four clean owning checkouts independently matched top-level path, branch, exact HEAD and current remote tips before/after execution. All use `codex/assembly-shadow-r01b-h1` and `git@github.com:night-outlook/<repository>.git`. Demo fast-forwarded from published C return `ed9afef29d17c64f15b281ea8b2176cb17d637b3`; three external pins unchanged. Tested source anchor `5931ada3c70958a7c6132219e059a42ee3cecbd0` is an ancestor; delta to execution HEAD is documentation/evidence-only. Latest handoff-touching commit matched local/remote HEAD at execution.

| Exact owning path | Executed commit |
| --- | --- |
| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `faa351d6854e71982ca047b994fb8579475f542a` |
| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `041c0cbb42d3e64e54fe605673d99799b5d63893` |
| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `120bb01be680cec0375002a0823552d66d34b84c` |
| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `1abb6bcaa85226f08c67f9da65edb3c58e8cb399` |

Detached reference worktrees under `<live root>/reference-worktrees/` retained clean: native `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, IL2CPP `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`, graph-test package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`. Four native-role source/install manifests bind exact candidate/reference cores, current package and executed demo; actual install receipts and native inventories are preserved in separate diagnosis. No source or cache from the ordinary checkout was used. Each role has its own project, configs, generated native root, app and logs; stripped-AOT generation copies are distinct from installed SDKs.

Environment:macOS26.5 arm64; Python3.14.6; SDK8.0.318/runtime8.0.21; PowerShell7.6.3; Apple clang21.0.0; macOS SDK26.5. Exact actual Unity `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`; target StandaloneOSX/arm64. Direct SDK path `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk` used as SDK only; Unity6000 Editor not launched. Full preflight tool/version/status/ref/worktree operations are in checkpoint `preflight/environment.json`, `preflight-before-sync.json`, `preflight-commands.json`.

Exact command: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -B /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Tools/AssemblyShadow/R03/run_local.py --workspace /Users/ah/GitHub/hybridclr/assembly_shadow_h1r --output /Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001D-build-api --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity --demo-commit faa351d6854e71982ca047b994fb8579475f542a`. `preflight/runner-exit.json` retains cwd, scoped environment, exact start/end/exit and invocation count1. Each of60 command receipts has operation/timestamps/streams/hash bindings. Outer Unity PIDs identify supervisors; they are not relabeled as direct Player or inner Unity PIDs. Build logs retain conversion/compiler/linker/build events and build GUIDs at their original per-role paths.

### Fresh results and evidence states

| Validation | State | Result and boundary |
| --- | --- | --- |
| Entry/final authority and detached reference sources | Passed | Exact clean sources/remotes and three retained reference worktrees. |
| Verifier/input/API/lifetime Python contracts | Passed | All67 tests, command0001. |
| Reference/candidate graph and admission | Passed | Actual9/9 each plus35/35, commands0005–0010. |
| Player fixtures and extended subchecks | Passed | Fifteen DLLs,33 audits,33 actual Unity consumers, exact invalid-key control, two actual Editor probes and complete build-helper API checks. |
| Full helper/package compilation | Passed subcheck | Three real package assemblies (15/14/173 sources), whole helper,425 input bindings/115 defines; commands0051–0054 exit0. Preserved C helper command0055 expected exit1/two CS0266/no output; not a product-build success. |
| Four preparations | Passed | Bound source/config/package/native/fixture inputs; four isolated roots. |
| Four native build validation cells | Failed | Commands0056–0059 exit0 and build-receipt.json reports Passed/errors0/nonGeneratedCorePreserved=true with fresh ARM64 apps. Strict runner gate rejects two matching install receipts rather than one. Artifact build success is retained separately from failed provenance validation. |
| Actual EditMode cell | Failed | Command0060 exit0; XML755 cases,754 Passed,0 Failed,1 Ignored; aggregate Skipped:Ignored rejected. All35 mandatory R03 IDs and target-cycle Passed in read-only XML audit. Frozen M01 resource asset test is Skipped/NoCoverage. |
| Nineteen Players | Blocked/NotRun | C01–C10,R01–R05,D01–D03,O01 not launched. No runtime/native MethodInfo/warm certificate acceptance evidence. |
| Focused seal and separate custody audit | Passed | 1736 indexed live files/1737 exact archive members;36 ledger/individual cell matches;60 streams;1280 previous custody bindings unchanged. |

All60 outer command groups completed cleanly. Seven supervised Unity completions0049/0050/0056–0060 preserved inner exits and exact compiler binding/birth identities; each retired one authenticated VBCSCompiler child, with clean completion. Only0048 (invalid consumer),0050 (invalid Editor probe) and0055 (old complete helper) retain expected nonzero exits. Other57 commands exited0. No survivor/timeout/cleanup exception or negative-control override masked these failed cells. Fixture/lifetime/count/API repair observations passed in executed scope; C/A/B failure bytes and uncertainty remain historical.

Native artifact outcomes are genuine fresh installer/generation/conversion/C++/link/build observations, but runner build cells remain Failed. Each role's receipt contains22 Player files,965 installedBefore and966 installedAfter entries,44 linked DLLs,errors0/warnings1 and feature/diagnostic/CPP configuration. Canonical SDK roots under `HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp` exactly match installedAfter. A second equal-hash receipt under `HybridCLRData/StrippedAOTDllsTempProj/StandaloneOSX/Il2CppOutputProject/IL2CPP/libil2cpp` was copied by generation; its native inventory differs in one generated file. `verify_build` searches all HybridCLRData recursively and requires one hash match, so legitimate copied receipts fail the locator guard. Player/app inventories and ARM64 architecture were read-only authenticated without launching Players. Exact paths/hashes/pin tuples/differences are in `preflight/DIAGNOSTIC_FINDINGS.json` and `preflight/native-receipts/`.

The isolated project omits frozen M01 prefab/scene/data assets. Actual `ResourceAbiTests.FrozenDemoResourcesUseActualScriptGuidsAndOnlyAffectedBundles` therefore calls Assert.Ignore with reason `The frozen M01 demo assets are not present in this project.` The XML root becomes Skipped:Ignored; `editor_tests` demands Passed before checking mandatory IDs, producing `Nonzero real Editor test execution required` despite actual execution. No ignored result is relabeled Passed; this asset coverage remains NoCoverage. Returned issues R03-LD-001/002 require Primary-owned locator/test-scope correction under the current prohibition on Local source changes.

### Custody, publication and exit

Live root `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001D-build-api`; preflight `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261001D-build-api`. Immutable [batch-D checkpoint](../History/M07R/R03/local-validation-20261001-batch-d-return-required/README.md) retains all indexed evidence individually, including four full apps, XML, API inputs/results/compiler responses/package/helper DLLs, all60 commands/streams, seven completion receipts, source snapshots, detailed diagnosis and separate authentication. Excluded Library/HybridCLRData and all live roots remain intact;135 bin/obj files, six projects and three detached references are inventoried. No test XML, Player receipt or coverage was fabricated.

| Artifact | SHA-256 |
| --- | --- |
'''
for n,h in hashes.items():local+='| '+n+' | `'+h+'` |\n'
local+='''
The original163272284-byte live evidence.tar.gz is unchanged. To fit GitHub's single-file limit, checkpoint `ARCHIVE_TRANSPORT.json` binds three exact ordered64MiB-or-smaller parts; concatenation equals the original archive hash. The reconstruction helper writes only a new absolute destination and validates all hashes. Publication changes storage representation only, not any seal/index/member/result bytes. All1736 original indexed files are also individually committed. Checkpoint manifest binds the complete published transport and evidence.

No Local fix or source/pin/timeout/expectation/cleanup change. Only Local-owned reports/new checkpoint change; A/B/C checkpoint/raw files and R02 I result/index/archive reauthenticated unchanged, preserving earlier R02/H1 states. Full R03 legacy/resource, broader generic/delegate/interface/stack-trace, startup/capacity/performance/memory, PureInterpreter qualification and independent full-stage review remain NotRun/outside this focused result. `R03Accepted=false`; `H2Passed=false`; `pureInterpreterExpansionEnabled=false`; `fullLegacyRegressionAcceptance=false`. **Exit: Local Validation → Primary Implementation; stop.** Latest pushed Local docs/evidence HEAD is recorded in the outgoing prompt; executed demo remains faa351d. New committed/pushed Primary handoff and unused root required before another batch.

'''
ret='''## Current return — R03 batch D: native locator and Editor scope integration failures

**ReturnRequired:12 Passed,5 Failed,19 Blocked; focused seal Passed; exit1.** One batch,2026-10-01 16:47:28–16:53:21 UTC (09:47:28–09:53:21 America/Los_Angeles). Exact tuple/environment/commands and states are in [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md); immutable [D checkpoint](../History/M07R/R03/local-validation-20261001-batch-d-return-required/README.md). Complete package/helper count/API repair passed its five compile checks and all four actual native pipelines. No Local implementation or retry occurred.

### R03-LD-001 — recursively unique install-receipt lookup rejects legitimate generation copies

**Symptom / exact reproduction performed.** From `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`, invoke `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -B /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Tools/AssemblyShadow/R03/run_local.py --workspace /Users/ah/GitHub/hybridclr/assembly_shadow_h1r --output /Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001D-build-api --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity --demo-commit faa351d6854e71982ca047b994fb8579475f542a`, with SDK8.0.318 and exact external tuple from LOCAL_VALIDATION.md. Do not repeat D. Four roles produce real ARM64 apps with successful build receipts, then all four cells fail `Exact native installation receipt is required`. All19 dependent Players block.

**Evidence.** Live root means `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001D-build-api`. `builds/{candidate-release,reference-release,candidate-debug,candidate-off}/build-receipt.json` reports Passed,errors0,nonGeneratedCorePreserved=true; commands0056–0059 retain original exit0/clean supervised completion. Their cell receipts remain Failed. Each project's HybridCLRData contains two receipts matching installReceiptSha256: `LocalIl2CppData-OSXEditor/il2cpp/libil2cpp/assembly-shadow-install.json` and `StrippedAOTDllsTempProj/StandaloneOSX/Il2CppOutputProject/IL2CPP/libil2cpp/assembly-shadow-install.json`. Exact per-role paths/hashes/tuples, copied receipt bytes and native inventory comparisons are in checkpoint `preflight/DIAGNOSTIC_FINDINGS.json`/`native-receipts/`. Raw Player bytes/inventories, logs and complete build receipts are committed under `batch/`; no artifact-only pass overrides the failed provenance cell.

**Root cause / boundary.** `Tools/AssemblyShadow/R03/run_local.py:211–216` recursively searches all HybridCLRData by receipt hash and requires exactly one match. `PrebuildCommand.GenerateAll` legitimately produces a stripped-AOT output project that copies the installed receipt. Equal receipt hashes identify copied content, not a unique installed directory. Read-only diagnosis finds the canonical installed SDK matches all966 installedAfter entries; the stripped-AOT copy differs in one generated file. The installation source tuple is correct in both receipts. No native compilation or pin mismatch is demonstrated by this failure; locator identity is the broken integration contract.

**Primary direction.** Record the explicit actual installed native root from SettingsUtil.LocalIl2CppDir in the build receipt, then authenticate its project/batch containment, expected installation receipt hash and exact native inventories. Distinguish generated copies from the installed SDK without deleting evidence. Add a regression with an equal-hash stripped-AOT receipt and differing generated snapshot. Do not choose the first recursive match, weaken content/containment checks or remove the copy to force uniqueness. Correct the producer/verifier contract coherently; Local changes are forbidden by this handoff.

**Uncertainty / revalidation.** Native artifacts and installed inventories are authenticated, but runtime cases never launched. After a committed/pushed locator repair, a fresh source-bound batch must pass the four original build cells and all19 fresh-process Players; do not manually launch blocked D cases or promote D's cells after diagnosis. Native runtime/layout/method/guard/warm-certificate outcomes remain unknown.

### R03-LD-002 — entire-package Editor run includes an unavailable M01 asset contract

**Symptom / reproduction.** The same authorized D batch's independent EditMode command0060 runs the whole package suite in candidate-release after preparation. Unity exits0 with clean supervised completion, but `editor-tests` fails `Nonzero real Editor test execution required` because XML aggregate root is Skipped:Ignored. The tests did execute:755 cases,754 Passed,zero Failed,one Ignored. All35 mandatory R03 IDs and GraphAndInputTests.CyclesReportClosedPath are unique Passed results in read-only XML audit.

**Evidence/excerpt.** `<live root>/editor-results.xml` and `editor-tests.log`, command0060 plus unity-completion.json are unchanged checkpoint `batch/` files. XML ignored case: `HybridCLR.Editor.AssemblyShadow.Tests.ResourceAbiTests.FrozenDemoResourcesUseActualScriptGuidsAndOnlyAffectedBundles`; category UnityAssetDatabase; reason `The frozen M01 demo assets are not present in this project.` Detailed root attributes,755-case counts,skip reason and all35 exact required names are in `preflight/DIAGNOSTIC_FINDINGS.json`. That M01 asset test is Skipped/NoCoverage, not Passed.

**Root cause / boundary.** `prepare_project` creates the focused baseline DLL/build harness project, omitting `Assets/AssemblyShadowDemo/ResourcesSource/VersionedPrefab.prefab`, `Assets/AssemblyShadowDemo/Scenes/Business.unity` and `Assets/AssemblyShadowDemo/ResourcesSource/VersionedData.asset`. The test at pinned package `Tests/Editor/AssemblyShadow/ResourceAbiTests.cs:519–525` explicitly Assert.Ignore's when they are absent. `editor_tests` launches the unfiltered package suite and requires aggregate Passed before validating R03 IDs, making the chosen suite incompatible with the isolated project's fixture scope. This is not a failed R03 assertion; it is not full M01 resource coverage either.

**Primary direction.** Define the focused Editor scope explicitly: select the required R03 contracts and target-cycle regression, or provide all frozen M01 assets/dependencies if the complete package suite is intentionally required. Preserve the full-stage legacy/resource gate. Continue requiring exact unique mandatory IDs, actual XML, no required skips/failures and clean original command completion. Do not blindly accept every Skipped aggregate or relabel the missing asset coverage Passed. Add a scope/fixture regression so isolated projects and selected tests agree.

**Uncertainty / validation after repair.** All required R03 Editor assertions already pass in D; that does not override the original Failed cell. Scope selection or fixture provisioning is Primary-owned. Next authorized batch must execute the agreed scope, preserve ignored/unavailable coverage explicitly, and satisfy its original strict mandatory-ID semantics alongside native/runtime validation. Full R03 resource/regression acceptance remains outside this focused run.

### Custody and stop

Count/API and earlier fixture/lifetime repairs passed in executed scope. All60 outer command groups clean; only named controls0048/0050/0055 preserve expected exit1; seven actual Unity completions preserve original inner exits. No source fix, pin change, retry, Player launch, flag rewrite, timeout/cleanup relaxation or acceptance promotion occurred.

Custody Passed for1736 indexed files/1737 archive members and1280 prior bindings unchanged. Original live163272284-byte archive remains intact; committed ARCHIVE_TRANSPORT.json binds three exact parts that reconstruct its unchanged SHA-256, and all indexed files are also committed individually. R03Accepted=false; H2Passed=false; PureInterpreter expansion disabled. Remaining full-stage work is not waived. **Local Validation → Primary Implementation; stop.** A new exact pushed Primary handoff and unused root are required.

'''
sections={'LOCAL_VALIDATION.md':local,'RETURN_TO_WEB.md':ret};preservation={}
for name,section in sections.items():
 p=D/'Docs/AssemblyShadow/Handoff'/name;old=p.read_text();first,tail=old.split('\n',1);tail=tail.lstrip('\n');assert tail.startswith('## Current');tail=tail.replace('## Current','## Historical',1);p.write_text(first+'\n\n'+section+tail);preservation[name]={'originalSha256':hashlib.sha256(old.encode()).hexdigest(),'newSha256':sha(p),'preservation':'Previous report body retained except C Current-to-Historical heading; D prepended'}
(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps(preservation,indent=2)+'\n');files=sorted(p for p in C.rglob('*') if p.is_file());(C/'MANIFEST.sha256').write_text(''.join(sha(p)+'  '+str(p.relative_to(C))+'\n' for p in files));print('Checkpoint created',len(files)+1,'files',sum(p.stat().st_size for p in files),'bytes; largest blob',max(p.stat().st_size for p in files))
