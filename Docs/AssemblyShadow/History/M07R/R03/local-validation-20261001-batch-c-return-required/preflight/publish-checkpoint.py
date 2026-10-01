import hashlib,json,pathlib,shutil,subprocess
D=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');R=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001C-inputs');P=R.parent/'Preflight-R03LocalBatch-20261001C-inputs';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261001-batch-c-return-required'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['git','-C',str(D),'status','--short'],text=True)==''
C.mkdir(exist_ok=False);idx=json.loads((R/'evidence-index.json').read_text());audit=json.loads((P/'POSTRUN_AUTHENTICATION.json').read_text());hashes=audit['topLevelHashes']
for name in [f['path'] for f in idx['files']]+['LOCAL_BATCH_RESULT.json','evidence-index.json','evidence.tar.gz','seal-receipt.json']:
 dest=C/'batch'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,dest)
shutil.copytree(P,C/'preflight')
sourcepaths=['Tools/AssemblyShadow/R03/run_local.py','Tools/AssemblyShadow/R03/input_validation.py','Tools/AssemblyShadow/R03/unity_command.py','Tools/AssemblyShadow/R03/command_lifetime.py','Tools/AssemblyShadow/R03/batch_evidence.py','Tools/AssemblyShadow/R03/Fixtures/EvolutionFixtureCorpus.cs','Tools/AssemblyShadow/R03/FixtureAudit/Program.cs','Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs','Tools/AssemblyShadow/R02/unity_session.py','Tools/AssemblyShadow/R02/process_identity.py','Tools/AssemblyShadow/R02/evidence.py','Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md']
for name in sourcepaths:
 dest=C/'source-snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/name,dest)
(C/'.gitattributes').write_text('''# Preserve immutable DLL/archive bytes without text conversion.
*.dll binary
*.tar.gz binary
# Preserve native Unity output whitespace under sealed hashes.
batch/**/*.log whitespace=-blank-at-eol,-blank-at-eof
batch/**/ProjectSettings/*.asset whitespace=-blank-at-eol,-blank-at-eof
''')
(C/'README.md').write_text('''# R03 Local batch C — immutable failed-run checkpoint

**ReturnRequired: 12 Passed, 5 Failed, 19 Blocked; focused seal Passed; exit 1.** Exactly one fresh invocation, 2026-10-01 02:53:29.052545–02:55:02.642508 UTC (2026-09-30 19:53:29–19:55:02 America/Los_Angeles). Executed demo `fdefb4f7133812f3b0593ae2257057c1bc57195e`; tested source/CI anchor `5c2932d5340728b16302b7cea8f20b64fcc9e7ce`. The later Local documentation HEAD is publication authority, not replacement execution provenance.

Read [LOCAL_VALIDATION.md](../../../../Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB.md](../../../../Handoff/RETURN_TO_WEB.md). R03Accepted=false; H2Passed=false; PureInterpreter expansion disabled; fullLegacyRegressionAcceptance=false. No full-stage acceptance or independent stage review is claimed.

- [LOCAL_BATCH_RESULT.json](batch/LOCAL_BATCH_RESULT.json), [BATCH_EXECUTION.json](batch/BATCH_EXECUTION.json) and all 36 cell receipts retain exact classifications.
- [evidence-index.json](batch/evidence-index.json), [evidence.tar.gz](batch/evidence.tar.gz) and [seal-receipt.json](batch/seal-receipt.json) are unchanged runner outputs: 677 indexed files / 678 authenticated members. The result and seal receipt are written after the seal and bound separately by this checkpoint manifest.
- [fixture-audit/results.json](batch/fixture-audit/results.json) records 33 metadata checks, consumer sources/peer bindings and the separate malformed control. [consumer-unity-2022.3.62f2/results.json](batch/consumer-unity-2022.3.62f2/results.json) records 33 actual compiled consumers and the distinct expected-CS0009 command. All input/output bytes and toolchain binding hashes are retained.
- [unity-lifecycle/results.json](batch/unity-lifecycle/results.json) records actual valid/invalid Editor probes. Valid marker is retained; invalid marker is absent by expectation. Their original inner exits are 0/1, with both supervised completion checks clean. Neither probe replaces native builds or EditMode assertions.
- All 55 command receipts/streams, seven unity-completion.json receipts, build configs, Editor logs, six isolated projects' included source/input/settings files and actual host/fixture outputs are retained unchanged in `batch/`. Commands 0048 and 0050 are separately asserted invalid-key controls, not product build successes. Commands 0051–0055 are genuine product compiler failures.
- [POSTRUN_AUTHENTICATION.json](preflight/POSTRUN_AUTHENTICATION.json) authenticates sealed bytes, ledger/cells, all streams, subchecks, toolchain/consumer bindings, supervised completion and 542 unchanged prior custody files. No outer command retained a surviving process group.
- [DIAGNOSTIC_FINDINGS.json](preflight/DIAGNOSTIC_FINDINGS.json), [unity-api-metadata.json](preflight/unity-api-metadata.json) and the metadata-reader script bind the exact CS0266 cause. Both BuildSummary count getters are System.Int32, while R03Build.cs lines50–51 declare uint fields and line109 assigns them implicitly. The initial metadata-reader path lookup failure is recorded separately; no validation rerun occurred.
- [RETAINED_LIVE_ROOTS.json](preflight/RETAINED_LIVE_ROOTS.json) binds 135 excluded compiled/intermediate files, three clean detached reference worktrees and six isolated project roots/cache locations. All retained live roots remain intact.
- `source-snapshot/` retains executed code/handoff and reused supervisor files. Checkpoint-local whitespace attributes retain raw Unity log/settings bytes. [MANIFEST.sha256](MANIFEST.sha256) binds all checkpoint files except itself.

Live root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001C-inputs`. Preflight: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261001C-inputs`. A/B and earlier R02/H1 evidence remain unchanged. Do not reuse these roots.

Both B repairs passed the new focused observations. All four native-role Unity invocations and the independent EditMode invocation then failed CS0266 in the common Editor build source. Build entry methods, conversion/native compilation, Editor assertions and all nineteen Players did not run; XML and native receipts are unavailable due to the prerequisite failure. No Local source fix, retry, pin/expectation/timeout change or acceptance promotion occurred. Local Validation → Primary Implementation; stop.
''')
local='''## Current run — R03 batch C, 2026-10-01 UTC: repaired inputs/lifetime pass; Editor build source fails

**Local Validation → Primary Implementation: ReturnRequired; 36 cells: 12 Passed, 5 Failed, 19 Blocked; focused seal Passed; runner exit 1.** Exactly one fresh invocation ran 2026-10-01 02:53:29.052545–02:55:02.642508 UTC (2026-09-30 19:53:29–19:55:02 America/Los_Angeles), runner PID 97655. No source fix, retry, blocked-cell invocation, expectation/timeout/cleanup change or acceptance promotion occurred.

### Exact executed authority and environment

All four canonical owning paths were clean, on `codex/assembly-shadow-r01b-h1`, with independent top-level/branch/HEAD/status/origin/worktree/submodule inspection and exact remote tips before and after execution. Demo fast-forwarded from Local return `ec463b6dfbd91603ec0c539378af6dbbe6b9e651`; external repositories were already pinned. Origins are `git@github.com:night-outlook/<repository>.git`. The tested source anchor `5c2932d5340728b16302b7cea8f20b64fcc9e7ce` is an ancestor, and delta to execution HEAD is Docs/AssemblyShadow-only. The latest commit touching the live handoff matched HEAD and remote at execution.

| Owning repository path | Exact executed commit |
| --- | --- |
| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `fdefb4f7133812f3b0593ae2257057c1bc57195e` |
| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `041c0cbb42d3e64e54fe605673d99799b5d63893` |
| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `120bb01be680cec0375002a0823552d66d34b84c` |
| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `1abb6bcaa85226f08c67f9da65edb3c58e8cb399` |

Reference detached worktrees under `<live root>/reference-worktrees/` remain clean at native `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, IL2CPP `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`, graph-test package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`. Four native-role isolated project manifests bind current package `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` and exact candidate/reference install/source pins and fixture hashes. Two additional compiler probes have independent project roots and empty package dependency manifests. No ordinary checkout or other batch Library/HybridCLRData/Builds was used. No native build receipt or build GUID exists because compilation failed before the build method ran.

Environment: macOS 26.5 arm64; Python 3.14.6; .NET SDK 8.0.318/runtime8.0.21; PowerShell7.6.3; Apple clang21.0.0; macOS SDK26.5. Actual Unity `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`; target StandaloneOSX/arm64. Direct managed SDK `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk` was used as SDK only; that Unity6000 Editor was not launched. Scoped environment/tool checks and timestamped Git operations are in checkpoint `preflight/environment.json`, `preflight-commands.json` and `preflight-before-sync.json`.

Exact invocation: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -B /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Tools/AssemblyShadow/R03/run_local.py --workspace /Users/ah/GitHub/hybridclr/assembly_shadow_h1r --output /Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001C-inputs --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity --demo-commit fdefb4f7133812f3b0593ae2257057c1bc57195e`. Full cwd/environment/PID/start/end/exit are in `preflight/runner-exit.json`; all 55 commands preserve their own start/end epochs, streams and hashes. For supervised Unity commands, outer PID is the supervisor PID, not an asserted inner Unity PID.

### Fresh results and classification

| Validation | Status | Factual evidence boundary |
| --- | --- | --- |
| Entry/final authority and detached reference sources | Passed | Four exact owning source/remote tuples; three retained reference worktrees. |
| Python verifier/lifetime/input contracts | Passed | All 57 tests in command0001. |
| Baseline and candidate graph | Passed | Actual9/9 each, commands0005–0008; native observations NotRun. |
| Admission/method suite | Passed | Actual35/35, commands0009–0010. |
| Player-fixtures cell | Passed | Fifteen generated DLLs,33 audited inputs,33 actual pinned-Unity compiler consumers, one exact invalid-key compiler control and two actual independent Editor probes. |
| Four native-role preparations | Passed | candidate Release/reference Release/candidate Debug/candidate OFF source/config/package/native bindings preserved. |
| Four native build cells | Failed | Actual supervised Unity commands0051–0054 compile common Editor source and fail CS0266 at R03Build.cs:109. Build method/IL2CPP conversion/native compilation/Player builds NotRun. |
| EditMode cell | Failed | Actual -runTests command0055 hits the same compiler prerequisite. Editor assertions NotRun; test XML unavailable because Test Runner was never reached. |
| Nineteen Player cells | Blocked/NotRun | C01–C10,R01–R05,D01–D03,O01 did not launch; no native MethodInfo/runtime/warm certificate evidence. |
| Focused seal and separate read-only custody audit | Passed | 677 live indexed files,678 exact archive members,36 aggregate/individual cell matches,55 command stream bindings and542 prior custody bindings unchanged. |

`fixture-audit/results.json` passed33/33 (fifteen Player + eighteen shared corpus inputs). All provider references now have PublicKey flag clear and empty token; mscorlib has its eight-byte token. `consumer-unity-2022.3.62f2/results.json` passed33/33 actual consumers with bound runtime/compiler/reference files and emitted DLL hashes. Command0048 separately returned exit1 with CS0009/Invalid public key and no emitted consumer; it is an expected-negative assertion, not a successful normal build.

`unity-lifecycle/results.json` passed both actual Editor probes. Command0049 compiled/invoked the valid marker and exited0. Command0050 retained exit1 and exact invalid-key diagnostic, with no marker. Both completed cleanly under the supervisor. All seven Unity completions0049–0055 preserved original inner exits, authenticated one owned VBCSCompiler child each by kernel birth identity and retired it using SIGTERM; all outer receipts remainingProcessGroup=false/postCleanupGroupExists=false, timeout=false, no cleanup errors. All55 command groups completed cleanly. Seven original exit1 commands remain visible: two expected-negative controls0048/0050 plus five genuine failed product invocations0051–0055. B's original survivor identity is not retroactively inferred.

R03-LB-001 fixture-reference repair and R03-LB-002 supervised compiler lifecycle are verified in the executed focused scope, including actual pinned compiler/Editor success and failure. This does not establish successful native-build/runtime lifecycle or full-stage acceptance. Next blocker: R03Build.cs fields errors/warnings are uint (lines50–51), but pinned Unity BuildSummary totalErrors/totalWarnings getters return System.Int32; assignments line109 fail CS0266. Read-only metadata inspection binds UnityEditor.CoreModule.dll SHA-256 `e22a829a8022d30c6b2b11fe764d12a2383cf882b63a954641e3cd41ea56af6e`. Compiler/API/source evidence and Primary direction are in RETURN_TO_WEB.md and checkpoint `preflight/DIAGNOSTIC_FINDINGS.json`/`unity-api-metadata.json`. The current handoff explicitly reserves source corrections for Primary; no bounded Local fix was made.

### Custody and exit

Live root `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001C-inputs`; preflight `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261001C-inputs`. Immutable [batch-C checkpoint](../History/M07R/R03/local-validation-20261001-batch-c-return-required/README.md) contains unchanged result/ledger/index/archive/seal, all included cells/host/audit/consumer/build/Editor/project inputs, all55 receipts/streams and seven unity-completion receipts, source snapshots and separate audit/metadata diagnostics. Excluded live roots remain retained; `preflight/RETAINED_LIVE_ROOTS.json` inventories135 compiled/intermediate files, six isolated projects and three detached references. No missing Editor XML or Player/build receipt was manufactured.

| Artifact | SHA-256 |
| --- | --- |
'''
for n,h in hashes.items():local+='| '+n+' | `'+h+'` |\n'
local+='''
No Local source fix or external repository change. A/B checkpoints/raw output and prior R02 I result/index/archive were reauthenticated unchanged; earlier R02/H1 evidence and execution-time flags remain preserved. Only Local-owned reports and this new checkpoint change. Full R03 legacy/resource regressions, broader generic/delegate/interface/stack-trace coverage, startup/capacity/performance/memory, PureInterpreter qualification and independent full-stage review remain NotRun/outside this focused batch. `R03Accepted=false`; `H2Passed=false`; `pureInterpreterExpansionEnabled=false`; `fullLegacyRegressionAcceptance=false`. **Exit: Local Validation → Primary Implementation; stop.** The outgoing prompt records the latest pushed Local docs/evidence HEAD; execution provenance remains fdefb4f. A new exact committed/pushed Primary handoff and unused root are required for another batch.

'''
ret='''## Current return — R03 batch C: pinned Unity build-summary API compile failure

**ReturnRequired:12 Passed,5 Failed,19 Blocked; focused seal Passed; exit1.** One batch only,2026-10-01 02:53:29–02:55:02 UTC. Exact tuples/tooling/times and all statuses are in [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md); immutable [C checkpoint](../History/M07R/R03/local-validation-20261001-batch-c-return-required/README.md). No Local source fix or retry occurred.

### R03-LC-001 — R03Build receipt fields mismatch pinned Unity count getter types

**Symptom.** All four native-role build invocations and the actual EditMode invocation fail C# compilation with two CS0266 errors at Assets/Editor/R03Build.cs(109,34)/(109,81). No build method, IL2CPP/native compilation, Editor assertion or Player executes. This is a Primary-owned source blocker: the current WEB_TO_LOCAL.md explicitly prohibits Local source changes even for this bounded API correction.

**Exact reproduction already performed.** From `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`, with SDK8.0.318 and Unity2022.3.62f2, invoke `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -B /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Tools/AssemblyShadow/R03/run_local.py --workspace /Users/ah/GitHub/hybridclr/assembly_shadow_h1r --output /Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001C-inputs --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity --demo-commit fdefb4f7133812f3b0593ae2257057c1bc57195e`. Exact three external pins are in LOCAL_VALIDATION.md. Do not reproduce in C or any prior root. After input subchecks pass, the prepared projects copy the same R03Build.cs to Assets/Editor; Unity compiles it before either build or Test Runner entry.

**Raw evidence/excerpts.** Live root `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001C-inputs`. Its `builds/{candidate-release,reference-release,candidate-debug,candidate-off}/Editor.log:951–952` and `editor-tests.log:614–615` report `error CS0266: Cannot implicitly convert type 'int' to 'uint'. An explicit conversion exists (are you missing a cast?)`. Commands0051–0055 retain original exit1 and clean supervised completion; exact commands/times/source bindings are in `commands/*/command.json` and `unity-completion.json`. Their unchanged committed copies are checkpoint `batch/`. All log hashes/excerpts and source SHA are in `preflight/DIAGNOSTIC_FINDINGS.json`; no timeout or owned-group survivor caused this failure.

**Root cause and missing coverage.** Executed `Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs:50–51` declares uint errors/warnings; line109 assigns report.summary.totalErrors/totalWarnings. Read-only inspection of `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/Managed/UnityEngine/UnityEditor.CoreModule.dll` confirms both getters return System.Int32; assembly SHA-256 `e22a829a8022d30c6b2b11fe764d12a2383cf882b63a954641e3cd41ea56af6e`. C# does not implicitly convert this int value to uint. Earlier fixture errors prevented this source from compiling; host and separate compiler/lifecycle checks did not validate the complete build Editor source against the pinned API. The real runtime API check covers a different source boundary.

**Affected scope / concrete Primary direction.** Correct the count representation coherently with the pinned API and unchanged JSON verifier contract. Prefer int fields matching the actual getters; if an unsigned receipt representation is intentional, use explicit checked nonnegative conversion. Avoid silent unchecked wraparound or changes to error-count acceptance. Add a focused compile check for the complete R03Build.cs against actual Unity2022.3.62f2 Editor references, so build-helper API errors are caught before expensive integrated runs. This same file blocks every native role and EditMode; native/package pins and runtime expectations need no change for the demonstrated cause.

**Remaining uncertainty and required validation.** The direct cause is proven by source, five compiler logs and pinned API metadata. No repaired source compilation experiment was performed because Local source changes/retries are prohibited. Subsequent installer/generation/IL2CPP/native/runtime failures remain unknown. Primary must commit/push its correction, verify the focused Editor compile, then issue a new exact-source handoff and unused root. The next authorized36-cell batch must still complete all four isolated native builds, actual mandatory EditMode IDs and19 fresh-process Player cases, final authority and strict seal. Do not alter C evidence or reinterpret a negative control as product success.

### Repair observations retained, not new open issues

R03-LB-001 passed33 audited fixtures and33 actual pinned-Unity compiler consumers, plus the separate exact-CS0009 negative consumer. R03-LB-002 passed actual valid/invalid Editor probes and supervised compiler retirement on all seven Unity commands. All55 outer command groups were clean. Original exits1 for commands0048/0050 remain failed commands within passed expected-negative assertions; five product exits1 remain genuine compilation failures. B's survivor identity remains historically uncertain, and successful native-build/runtime lifecycle is still unvalidated.

Custody audit Passed:677 indexed files/678 archive members, all36 cells and542 prior custody files unchanged. Source snapshots, metadata diagnostics, consumer DLLs/markers and all completion receipts are bound by the checkpoint manifest. No additional implementation is delegated locally. R03Accepted=false; H2Passed=false; PureInterpreter expansion disabled. Full R03 completion and independent stage review remain Primary-owned. **Local Validation → Primary Implementation; stop.**

'''
sections={'LOCAL_VALIDATION.md':local,'RETURN_TO_WEB.md':ret};preservation={}
for name,section in sections.items():
 p=D/'Docs/AssemblyShadow/Handoff'/name;old=p.read_text();first,tail=old.split('\n',1);tail=tail.lstrip('\n');assert tail.startswith('## Current');tail=tail.replace('## Current','## Historical',1);p.write_text(first+'\n\n'+section+tail);preservation[name]={'originalSha256':hashlib.sha256(old.encode()).hexdigest(),'newSha256':sha(p),'preservation':'Previous report body retained byte-for-byte except batch-B Current-to-Historical heading; C prepended'}
(C/'REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps(preservation,indent=2)+'\n')
files=sorted(p for p in C.rglob('*') if p.is_file());(C/'MANIFEST.sha256').write_text(''.join(sha(p)+'  '+str(p.relative_to(C))+'\n' for p in files));print('Checkpoint created',len(files)+1,'files',sum(p.stat().st_size for p in files),'bytes')
