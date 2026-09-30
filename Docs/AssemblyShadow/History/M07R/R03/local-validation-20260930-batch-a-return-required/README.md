# R03 Local batch A — sealed ReturnRequired

One source-bound batch ran on 2026-09-30, 07:47:06–07:47:47 America/Los_Angeles (14:47:06–14:47:47 UTC). Runner exit: **1**. The complete 36-cell ledger records **4 Passed, 3 Failed, 29 Blocked**. The focused seal Passed; this is not runtime acceptance or a full R02 seal.

Read [the batch result](batch/LOCAL_BATCH_RESULT.json), [the execution ledger](batch/BATCH_EXECUTION.json), [the postrun authentication](preflight/POSTRUN_AUTHENTICATION.json), and the current `Handoff/RETURN_TO_WEB.md` first. All copied raw files retain their original bytes. No batch was resumed or retried.

## Execution authority

All four owning repositories used branch `codex/assembly-shadow-r01b-h1` and exact clean local/remote identities at entry and final authority:

| Repository | Owning path | Executed commit |
| --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `25a7c5ada06c97574bf218e74cf38c811445d13c` |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `041c0cbb42d3e64e54fe605673d99799b5d63893` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `120bb01be680cec0375002a0823552d66d34b84c` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `1abb6bcaa85226f08c67f9da65edb3c58e8cb399` |

The demo delta from host-CI anchor `f5f5712459fdf67e2b748ddeab8e6540bffd3d95` contains eight documentation paths and no executable/tool changes. Publication of this checkpoint is a later documentation commit, not a replacement execution identity.

The exact runner command, PID, environment and start/end times are in [runner-exit.json](preflight/runner-exit.json). Workspace: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`; live root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930A-a898f`; separate preflight root: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20260930A-a898f`.

## Factual result

- Passed: entry authority, 29 synthetic Python verifier/filesystem contracts, three exact detached reference source worktrees, final authority.
- Failed: `host-baseline-graph`, `host-candidate-graph`, `host-admission`. Commands 0005/0006/0007 compiled successfully with exitCode=0, zero errors/warnings, timeout=false, but remainingProcessGroup=true. The runner killed each surviving owned group and rejected the command before invoking the compiled assertion program.
- Blocked/NotRun: Player fixture generation; all four project prepare/build pairs; actual Unity EditMode tests; all nineteen Player cases. No host assertion results, generated Player fixture inventory, isolated project/build, Editor XML/log, Player request/raw/verdict or new runtime acceptance exists.

The probable cause is the mismatch between default shared .NET compilation/server lifetime and the runner's immediate empty-process-group requirement. `source/run_local.py` retains the exact failing build and cleanup implementation. [The prior R02 managed command policy](source/r02-managed-reference.py) disables servers per invocation; the R03 command omits that policy. The installed SDK's copied target defaults `UseSharedCompilation` to true. The original receipts do not identify descendant PIDs or command lines, so the precise survivor executable remains unproven. No product logic assertion failed because none of the three compiled host programs ran.

## Environment and preserved roots

macOS 26.5 arm64; Python 3.14.6; .NET SDK 8.0.318/runtime 8.0.21; PowerShell 7.6.3; Apple clang 21.0.0; macOS SDK 26.5. The exact Unity 2022.3.62f2 executable and version were verified present, but Unity was not launched after the prerequisite failures. The intended target was StandaloneOSX/arm64. The .NET SDK binary was resolved from the existing Unity 6000.5.3f1 installation's `Contents/Resources/Scripting/DotNetSdk`; that Editor was not launched or substituted for Unity 2022.3.62f2. See [environment.json](preflight/environment.json).

The batch archive excludes `bin/`, `obj/`, reference worktrees and specified Unity caches by design. [RETAINED_LIVE_ROOTS.json](preflight/RETAINED_LIVE_ROOTS.json) records retained compiled outputs/intermediates and exact clean reference-worktree identities. The three compiled binaries are compilation artifacts, not passed host assertion evidence. Live roots were neither removed nor reused.

## Integrity and limits

| File | SHA-256 |
| --- | --- |
| LOCAL_BATCH_RESULT.json | `a03a2b2cc2f493ca92f782eed0a2b03d040c45a826333581818c96200c4a9173` |
| BATCH_EXECUTION.json | `0598bf960dbf9b4474b9075ab7cb24e3b1acb12941c86f8fd26dbf39bec314c5` |
| evidence-index.json | `a14717414c030ac734fc2e9543118b507df4465b55cbbeb4a9af0bf5a0756181` |
| evidence.tar.gz | `13cf7407447d7952aae6429bbf8e5aae3fc11a030ae139651a09142324450c6c` |
| seal-receipt.json | `d92fde6945465e0df8ac109d6430da59b9c3be3694f382cc2f55d7bd6df4e84d` |

Read-only postrun authentication checked every one of the 58 indexed live files and 59 archive members, exact aggregate/individual 36-cell equality, execution-ledger binding, command log hashes, and unchanged prior I result/index/archive hashes. This authentication is a custody check of the failed batch, not a second execution or an independent full R03 review. `MANIFEST.sha256` authenticates this bounded committed checkpoint.

No bounded Local source fix, expectation/timeout change, extra host assertion invocation, Unity run, Player launch, performance run or pin change was made after the single execution. Earlier A–I/H1 evidence retains its original classification. R02 acceptance is established separately by its committed owner decision; historical I execution-time false flags remain unmodified. `R03Accepted=false`, `H2Passed=false`, `pureInterpreterExpansionEnabled=false`, `fullLegacyRegressionAcceptance=false`.

Exit: **Local Validation → Primary Implementation**. Primary must repair the managed command lifetime contract and test it without weakening no-survivor enforcement, then supply a new exact source handoff and unused root. Full R03 legacy, broader method/generic/delegate/interface/stack-trace, startup/capacity/performance/memory, PureInterpreter qualification, independent full-stage review and H2 remain uncompleted.
