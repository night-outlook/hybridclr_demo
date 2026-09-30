import datetime,hashlib,json,pathlib,shutil,subprocess
D=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo')
R=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930B-lifetime')
P=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20260930B-lifetime')
C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20260930-batch-b-return-required'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
meta=json.loads((P/'fixture-metadata.json').read_text());malformed=[]
for f in meta['files']:
 for ref in f['references']:
  if ref['hasPublicKey'] and not ref['keyOrTokenHex']:malformed.append({'path':f['path'],'sha256':f['sha256'],'assemblyReference':ref})
assert len(malformed)==4
logs=[]
for p in sorted((R/'builds').glob('*/Editor.log'))+[R/'editor-tests.log']:
 lines=p.read_text().splitlines();errors=[{'line':i+1,'text':x} for i,x in enumerate(lines) if 'CS0009' in x];shared=[{'line':i+1,'text':x} for i,x in enumerate(lines) if 'csc.dll' in x and '/shared' in x]
 assert errors and shared;logs.append({'path':str(p),'sha256':sha(p),'errors':errors,'sharedCompilerInvocations':shared})
(P/'DIAGNOSTIC_FINDINGS.json').write_text(json.dumps({'kind':'ReadOnlyArtifactDiagnosis','recordedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Existing artifacts only; no compilation, fixture execution, source repair, batch retry or original receipt edit','metadataOperation':'pwsh -NoProfile -File '+str(P/'inspect-fixture-metadata.ps1'),'metadataOutputSha256':sha(P/'fixture-metadata.json'),'malformedAssemblyReferences':malformed,'compilerLogs':logs,'interpretation':'Observed empty full-public-key AssemblyRefs explain Unity Roslyn Invalid public key; persistent Unity compiler service is the likely dotnet survivor role, not proven from the comm-only roster.'},indent=2)+'\n')
C.mkdir(exist_ok=False)
idx=json.loads((R/'evidence-index.json').read_text())
for name in [f['path'] for f in idx['files']]+['LOCAL_BATCH_RESULT.json','evidence-index.json','evidence.tar.gz','seal-receipt.json']:
 dest=C/'batch'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,dest)
shutil.copytree(P,C/'preflight')
sourcepaths=['Tools/AssemblyShadow/R03/run_local.py','Tools/AssemblyShadow/R03/command_lifetime.py','Tools/AssemblyShadow/R03/batch_evidence.py','Tools/AssemblyShadow/R03/Fixtures/EvolutionFixtureCorpus.cs','Tools/AssemblyShadow/R03/PlayerFixtures/Program.cs','Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs','Tools/AssemblyShadow/R03/batch_contract.py','Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md']
for n in sourcepaths:
 dest=C/'source-snapshot'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/n,dest)
C.joinpath('.gitattributes').write_text('*.dll binary\n*.tar.gz binary\n')
C.joinpath('README.md').write_text('''# R03 Local batch B — immutable failed-run checkpoint

**ReturnRequired: 12 Passed, 5 Failed, 19 Blocked; focused seal Passed.** One fresh invocation only, 2026-09-30 18:06:26.933831–18:07:40.190805 UTC, exit 1. Executed demo `a261bdf0db3f1432226a6b6b69f6f56fbbc47d34`; source/CI anchor `7e2852fcd6c5bd9ebc82f2b3f97516742b772dc2`. The later Local documentation commit does not replace this execution provenance.

Read [LOCAL_VALIDATION.md](../../../../Handoff/LOCAL_VALIDATION.md) for status and [RETURN_TO_WEB.md](../../../../Handoff/RETURN_TO_WEB.md) for two actionable Primary issues. This checkpoint does not establish Unity/IL2CPP/native or runtime acceptance. R03Accepted=false; H2Passed=false; PureInterpreter expansion disabled.

- [LOCAL_BATCH_RESULT.json](batch/LOCAL_BATCH_RESULT.json), [BATCH_EXECUTION.json](batch/BATCH_EXECUTION.json) and all 36 individual cells preserve actual classifications.
- [evidence-index.json](batch/evidence-index.json), [evidence.tar.gz](batch/evidence.tar.gz), [seal-receipt.json](batch/seal-receipt.json) are unchanged runner outputs: 407 indexed files / 408 authenticated archive members. Final result and seal receipt are written after sealing and additionally bound by this checkpoint manifest.
- All 17 command receipts/streams, five pre-cleanup process rosters, host results/fixture DLLs, build configs and actual Editor compiler logs are retained in `batch/` with unchanged hashes.
- [POSTRUN_AUTHENTICATION.json](preflight/POSTRUN_AUTHENTICATION.json) authenticates live files, archive members, ledger/cells, command streams, fixture inventory, exact final source authority and 90 previous custody bindings. This read-only audit is separate from the original seal.
- [DIAGNOSTIC_FINDINGS.json](preflight/DIAGNOSTIC_FINDINGS.json) and [fixture-metadata.json](preflight/fixture-metadata.json) bind metadata-only inspection. A.dll refers to B with AssemblyRef flags=1 (PublicKey), zero key bytes; four generated fixtures have this defect. No DLL was changed.
- [RETAINED_LIVE_ROOTS.json](preflight/RETAINED_LIVE_ROOTS.json) inventories 108 excluded compiled/intermediate files, three clean detached reference worktrees and four isolated project roots. Original `Library` caches and all live roots remain available. Retained compiler response files are read-only diagnostic copies; no build outputs or test XML were manufactured.
- `source-snapshot/` retains the relevant executed-source files. `preflight/` includes command/environment/time/exit receipts and bounded postrun diagnosis. [MANIFEST.sha256](MANIFEST.sha256) binds every checkpoint file except itself.

Live root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930B-lifetime`. Preflight root: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20260930B-lifetime`. These are retained, not disposable or reusable batch roots. Batch A and earlier R02/H1 evidence remain unchanged.

Exactly four build cells and the EditMode invocation failed Unity compilation with CS0009; build methods, IL2CPP/native compilation, Editor test assertions and all nineteen Players did not run. All five Unity receipts additionally capture one surviving `dotnet` member; the original `remainingProcessGroup=true` and immediate cleanup flags remain unchanged. A later read-only ps observation found no members of those groups. No source repair, retry, pin change, full-stage review or acceptance promotion occurred. Local Validation → Primary Implementation; stop.
''')
# Preserve old report content and archive previous heading as historical.
heads={
'LOCAL_VALIDATION.md':'''## Current run — 2026-09-30, R03 batch B returned after Unity compilation

**Local Validation → Primary Implementation: `ReturnRequired`; 36 cells: 12 Passed, 5 Failed, 19 Blocked; focused seal Passed; runner exit 1.** Exactly one fresh invocation ran 11:06:26–11:07:40 America/Los_Angeles (18:06:26–18:07:40 UTC) in `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930B-lifetime`. No retry or source/timeout/expectation change occurred. This is the factual focused result, not full R03 acceptance.

### Executed authority, pins and environment

All owning checkouts were clean, exact paths and origin identities verified independently, and current remote branch tips matched before and after execution. Demo fast-forwarded from the published A return `2a9fdec813592fd79db511d5db96a6dcf1dea620`; the other pins were already current. All four use branch `codex/assembly-shadow-r01b-h1` and `git@github.com:night-outlook/<repository>.git`.

| Repository / absolute owning path | Exact executed commit |
| --- | --- |
| hybridclr_demo — `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `a261bdf0db3f1432226a6b6b69f6f56fbbc47d34` |
| hybridclr — `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `041c0cbb42d3e64e54fe605673d99799b5d63893` |
| hybridclr_unity — `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `120bb01be680cec0375002a0823552d66d34b84c` |
| il2cpp_plus — `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `1abb6bcaa85226f08c67f9da65edb3c58e8cb399` |

Demo source/CI anchor `7e2852fcd6c5bd9ebc82f2b3f97516742b772dc2`; delta to execution HEAD verified documentation-only. Reference sources remained detached, clean and retained at `<live root>/reference-worktrees/`: native `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, IL2CPP `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`, graph-test package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`. All four isolated projects use the candidate package file reference, recorded source-inputs/install pins and role build configs; no other worktree Library, Builds or HybridCLRData was used. No build receipt/GUID exists because Unity compilation failed before the build entry method.

Environment: macOS 26.5 arm64; Python 3.14.6; .NET SDK 8.0.318/runtime 8.0.21; PowerShell 7.6.3; Apple clang 21.0.0; macOS SDK 26.5. Exact Unity `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, target StandaloneOSX/arm64. SDK path `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk` was used only for managed builds; that Unity 6000 Editor was not run. The invocation used the handoff's Python and run_local.py with `--workspace /Users/ah/GitHub/hybridclr/assembly_shadow_h1r --output /Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930B-lifetime --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity --demo-commit a261bdf0db3f1432226a6b6b69f6f56fbbc47d34`. Full command, cwd, PID 92199, scoped environment, start/end and exit are in checkpoint `preflight/runner-exit.json`. Each actual operation has its command receipt with start/end epoch timestamps and stream hashes.

### Fresh results and limits

| Validation | Status | Evidence / factual boundary |
| --- | --- | --- |
| Entry/final authority, reference sources | Passed | Four owning source/remote checks and three detached reference worktrees. |
| Verifier/lifetime contracts | Passed | 43 tests: original 29 plus 14 repair contracts, command 0001. |
| Baseline / candidate graph | Passed | Actual 9/9 in each, commands 0005–0008; native observations remain NotRun. |
| Admission and method contracts | Passed | Actual 35/35, commands 0009–0010. |
| Player fixture generation | Passed | Actual 15 DLL inventory, commands 0011–0012; dnlib inventory success is not compiler/runtime validity. |
| Four isolated preparations | Passed | Configs, source/package/native pins, per-project fixture hashes retained. |
| Candidate Release, reference Release, candidate Debug, candidate OFF build cells | Failed | Four actual Unity launches (0013–0016) fail compilation: CS0009 Invalid public key in Assets/Fixtures/A.dll. Build entry methods, conversion/native compilation and Player builds NotRun. |
| EditMode cell | Failed | Actual Unity -runTests invocation 0017 fails the same compiler prerequisite; Editor assertions NotRun; XML unavailable because execution never reached Test Runner. |
| Nineteen Player cells | Blocked/NotRun | C01–C10, R01–R05, D01–D03, O01 never launched; no native MethodInfo, runtime or warm-certificate acceptance evidence. |
| Focused seal / postrun custody | Passed | 407 live indexed files, 408 archive members, all 36 aggregate/individual cells and command streams authenticated; 90 prior custody bindings unchanged. |

The repaired direct .NET build/run chain completed with exit 0 and no survivors for commands 0005–0012. All five Unity commands exited 1 with `remainingProcessGroup=true`; each preserved `process-group-before-cleanup.json` contains one `dotnet`, PPID 1, state S. Parent PGIDs 92325/92495/92666/92847/93004; child PIDs 92465/92655/92831/92984/93034. Receipts remain schemaVersion 2, lifetimePolicy R03OwnedCommandV1, timeout=false, cleanupErrors=[] and immediate postCleanupGroupExists=true. Later read-only ps found no members of those groups; it does not rewrite or excuse the original failures. Original A survivor identity remains unknown.

Read-only DLL inspection found baseline A.dll SHA-256 `43518538821b13ac2271e2322aa47fb8ed076e755fd2cee6bd7fda85ae8f7281`: its B AssemblyRef has flags=1 / HasPublicKey=true / empty key bytes. Reversal B.dll and both true-cycle DLLs have the same malformed full-public-key reference pattern. The shared corpus uses AssemblyRefUser(name, version) without explicit unsigned-token normalization; fixture inventory and host graph analysis reopen through dnlib without testing pinned Unity Roslyn reference consumption. This explains the CS0009 prerequisite failure; correcting construction and adding consumer-validity coverage is Primary work. Unity logs separately show its bundled compiler launched with /shared; this is the likely surviving dotnet service, with exact role uncertain because captured comm lacks arguments. See RETURN_TO_WEB.md for actionable issues R03-LB-001/002.

### Evidence custody and exit

Immutable [batch-B checkpoint](../History/M07R/R03/local-validation-20260930-batch-b-return-required/README.md) contains unchanged runner outputs, all included files/receipts/DLLs/logs, executed-source snapshots and separate preflight/audit/metadata diagnostics. Live root and all bin/obj/reference-worktrees/project caches remain retained; `preflight/RETAINED_LIVE_ROOTS.json` binds 108 excluded compiled/intermediate files and root identities. No failed output was replaced or reused.

| Artifact | SHA-256 |
| --- | --- |
| LOCAL_BATCH_RESULT.json | `3c8646fa68556b987469467c473e7bff6b529abbd8df3b1693a0a49a20738870` |
| BATCH_EXECUTION.json | `b07bbd2b005881cd34c73fe708aaa8d3adbe6bb9e480aa9354cdff547498a2a8` |
| evidence-index.json | `ec1feae707274098acfbce3f83696a0ce1d2aa734318254bb84d54878cb63887` |
| evidence.tar.gz | `a09d5480508a6d40bf619f925b76144693faf5ed637dbf7ac1c7fed5cec86ebd` |
| seal-receipt.json | `662df37c5904f58df11310e351017a98ed7490c8762682e2993fe61442c31286` |

Bounded Local fixes: none. Only Local-owned reports/new checkpoint change in this return; native/package/control pins and Primary handoff are untouched. Batch A checkpoint/raw outputs and R02 I result/index/archive reauthenticated unchanged; earlier A–I/H1 classifications remain preserved. Full legacy regressions, broader generic/delegate/interface/stack-trace coverage, startup/capacity/performance/memory, PureInterpreter qualification, independent full R03 stage review and H2 remain NotRun/outside this focused batch. `R03Accepted=false`; `H2Passed=false`; `pureInterpreterExpansionEnabled=false`; `fullLegacyRegressionAcceptance=false`. **Exit: Local Validation → Primary Implementation; stop.** Publication adds only docs/evidence; the final pushed Local commit is the demo HEAD in the outgoing prompt, not a new executed source. Any future validation needs a new committed/pushed Primary handoff and unused output root.

''',
'RETURN_TO_WEB.md':'''## Current return — R03 batch B: invalid fixture key and Unity command lifetime

**ReturnRequired: 12 Passed, 5 Failed, 19 Blocked; focused seal Passed; exit 1.** One invocation, 2026-09-30 18:06:26–18:07:40 UTC. Exact tuple/environment/operation status are in [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md). Read the immutable [batch-B checkpoint](../History/M07R/R03/local-validation-20260930-batch-b-return-required/README.md), particularly `preflight/DIAGNOSTIC_FINDINGS.json`, `fixture-metadata.json` and `POSTRUN_AUTHENTICATION.json`. Live root below means `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930B-lifetime`; source root is `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`.

The a261bdf0db3f1432226a6b6b69f6f56fbbc47d34 repair passed its actual direct managed chain: baseline/candidate graph 9/9 each, admission 35/35, fifteen fixture DLLs, and no surviving process groups in commands 0005–0012. This does not close Unity-owned lifetime or native/runtime validation. No Local source repair was made.

### R03-LB-001 — generated AssemblyRef encodes an empty full public key

**Symptom/reproduction.** The authorized once-only command was `python3 -B <source root>/hybridclr_demo/Tools/AssemblyShadow/R03/run_local.py --workspace <source root> --output <live root> --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity --demo-commit a261bdf0db3f1432226a6b6b69f6f56fbbc47d34`, using SDK 8.0.318 and the exact four commits recorded in LOCAL_VALIDATION.md. Do not reproduce in B. Following successful preparation, each isolated project's Unity compilation failed before R03Build.Build. The subsequent independent EditMode invocation failed before assertions. All19 Players blocked.

**Evidence.** `<live root>/builds/{candidate-release,reference-release,candidate-debug,candidate-off}/Editor.log:869` and `<live root>/editor-tests.log:694` contain `error CS0009: Metadata file '<isolated project>/Assets/Fixtures/A.dll' could not be opened -- Invalid public key.` Exact committed copies are in checkpoint `batch/`. Actual command receipts 0013–0017 contain full paths/times/flags/exit1; no timeout. `preflight/fixture-metadata.json`, generated by the retained metadata-only PowerShell script, observes baseline A.dll SHA-256 `43518538821b13ac2271e2322aa47fb8ed076e755fd2cee6bd7fda85ae8f7281`: AssemblyDef unsigned, but B AssemblyRef flags1/HasPublicKey=true/empty key. Reversal B.dll SHA-256 `230ff8067ffd065da3b8020aef7dfaa8a4dedd1e575fb69b58fa49b19ce4d6b9` and true-cycle A/B have the same pattern. No fixture was executed or rewritten during diagnosis.

**Root cause / gap.** `Tools/AssemblyShadow/R03/Fixtures/EvolutionFixtureCorpus.cs:33` creates `AssemblyRefUser(provider, new Version(1,0,0,0))`; emitted provider references have the full-public-key bit without any full key bytes. `PlayerFixtures/Program.cs` StaticReference roundtrips those references into AOT Player DLLs. Its inventory and graph-only layout checks use dnlib, which accepts the malformed bytes, so host PASS did not cover Unity Roslyn consumption. The exact observed malformed metadata is a concrete explanation for Invalid public key, rather than a runtime semantics failure.

**Impact/direction.** Audit the shared real-DLL corpus and all referencing fixture builders for explicit valid unsigned reference construction (empty public-key token with PublicKey flag clear) or a coherent valid signed identity. Preserve graph edges, static witness layout, logical identities and conservative admission expectations. Add a regression that consumes generated DLLs as references using the pinned Unity compiler/toolchain, covering baseline A/B, reversal and true-cycle, alongside assertions on AssemblyRef flags/key lengths. Do not drop A.dll from inputs, fake signed identities, change expectations or patch the sealed batch. This spans fixture construction and consumer-validity coverage and is returned to Primary.

**Uncertainty / remaining validation.** Metadata-only inspection did not run an unsigned repaired compiler experiment; after fixing this first prerequisite, additional compile, IL2CPP, native or runtime failures may appear. All four complete isolated builds, actual mandatory EditMode IDs and nineteen fresh-process Player cases still require a fresh source-bound batch. Existing host checks and seal do not substitute for them.

### R03-LB-002 — Unity invocations leave an owned dotnet process after exit

**Symptom/reproduction.** The same five Unity invocations in B each exited1 at compilation and also violated the production no-survivor guard. Original direct .NET build failures from A are repaired in the tested direct path; Unity's internal compiler invocation is a separate ownership boundary. Do not retry or globally shut down processes to manufacture a pass.

**Evidence.** `<live root>/commands/{0013,0014,0015,0016,0017}/command.json` and each `process-group-before-cleanup.json` preserve schemaVersion2, lifetimePolicy R03OwnedCommandV1, remainingProcessGroup=true, timeout=false, cleanupErrors=[] and one captured member with executable dotnet, PPID1, stateS. Parent PGIDs: 92325/92495/92666/92847/93004; child PIDs: 92465/92655/92831/92984/93034. All immediate postCleanupGroupExists flags are true. Compiler lines at build logs872 and Editor log697 use Unity2022's own NetCoreRuntime/dotnet with DotNetSdkRoslyn/csc.dll and `/shared`. Later read-only ps in POSTRUN_AUTHENTICATION found no remaining members; raw failure flags remain unchanged.

**Most likely root cause / impact.** The repaired direct `dotnet build` arguments and child environment do not control Unity Bee's `/shared` Roslyn command. The likely survivor is Unity's persistent compiler service; roster comm proves dotnet but does not prove exact command line/role or connect it to the unknown A survivor. Even after correcting the metadata defect, Unity-owned background work may still violate the strict command-lifetime contract. Current evidence proves the failure-exit path, not successful-build survival.

**Primary direction.** Investigate and configure the pinned Unity compiler lifecycle within each isolated invocation, keeping the no-survivor guard and owned-group cleanup. Use bounded, ownership-scoped executable/argument diagnostics if necessary to identify the service. Add same-wrapper Unity lifecycle coverage for both compiler-failure and successful-build paths. Do not whitelist dotnet, accept exit0 with survivors, kill unrelated named processes or relax timeouts. Whether pinned Unity supports disabling the service cleanly or needs an explicit scoped lifecycle arrangement remains to be determined by Primary.

**Required revalidation / exit.** Both issues need committed/pushed Primary changes and a new exact handoff with an unused root. Preserve B and A as sealed failed attempts. The next authorized 36-cell integrated batch must still include four completed isolated builds, actual Editor assertions and nineteen fresh processes, final authority and strict seal. Full R03 acceptance, resource/performance work, PureInterpreter qualification and H2 are not waived. `R03Accepted=false`; `H2Passed=false`; expansion disabled. **Local Validation → Primary Implementation; stop.**

'''}
oldreports={}
for name,section in heads.items():
 p=D/'Docs/AssemblyShadow/Handoff'/name;old=p.read_text();title,tail=old.split('\n',1)
 originalheading='## Current run — 2026-09-30, R03 batch A returned at managed process lifetime' if name=='LOCAL_VALIDATION.md' else '## Current return — R03 batch A: managed command lifetime blocks native validation'
 assert tail.count(originalheading)==1
 newtail=tail.replace(originalheading,originalheading.replace('Current','Historical',1),1)
 p.write_text(title+'\n\n'+section+newtail.lstrip('\n'))
 oldreports[name]={'originalSha256':hashlib.sha256(old.encode()).hexdigest(),'preservation':'Prior body unchanged except Current-to-Historical batch-A heading; new B section prepended','newSha256':sha(p)}
C.joinpath('REPORT_HISTORY_PRESERVATION.json').write_text(json.dumps(oldreports,indent=2)+'\n')
files=sorted(p for p in C.rglob('*') if p.is_file());C.joinpath('MANIFEST.sha256').write_text(''.join(sha(p)+'  '+str(p.relative_to(C))+'\n' for p in files))
print('checkpoint',C,'files',len(files)+1,'bytes',sum(p.stat().st_size for p in files))
