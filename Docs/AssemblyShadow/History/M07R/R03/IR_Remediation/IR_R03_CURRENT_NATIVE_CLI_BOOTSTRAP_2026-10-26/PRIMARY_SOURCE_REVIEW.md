# Primary source review and Local oneuse-C reconciliation — R03 current-native CLI bootstrap (2026-10-26)

**Author:** Primary Implementation, NOT an independent full-stage R03 reviewer or Human Review Gate. **Basis:** exact night-outlook/hybridclr_demo@fdf73ca907ace8d9470c888a02d0c3bedc25379b Local-owned handoff/current oneuse-C checkpoint, raw stderr and coordinator/projection results; source read through GitHub Connector at immutable refs, then new Primary code and raw Mac/Linux CI logs.

## 1. Original reported outcomes preserved

The returned Local **FAIL / ReturnRequired** is a genuine oneuse-C combined coordinator outcome. The single sparse source-projection PASS authenticated the same detached clean fc55 original S and all 16,978 protected file bytes, measured actual available space rising to 46.334 GiB. Read-only Local source/remote/Unity2022/net8 admission then Passed. Exactly one 10-stage coordinator ran: eight scoped Passed, current-native-players Failed and native-installed-source-audit Blocked. The eight Passes authenticate 104 source-host tests, original nine-part S archive 587,907,380 bytes SHA256 23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6, 15,713 members, original 90 recorded cells, 59 historic process joins and eight native source-host diagnostic components. No current-native batch/Player/Unity compiled input or installed 126 physical pairs exists.

The actual failed child exited 1 with:
    ModuleNotFoundError: No module named 'run_local'
before argument parsing and before CurrentNativeBatch construction, in Tools/AssemblyShadow/R03IR/run_terminal_current.py at the original first top-level import. The owning file Tools/AssemblyShadow/R03/run_local.py is a parallel sibling, and the later imported focused runner's path bootstrap cannot help. Parent coordinator sys.path state does not survive subprocess creation. Original source-bound stderr, command/process receipt and finding provide direct independent evidence of this diagnosis. This is a CLI wrapper defect, not a terminal-method behavior test.

The original oneuse-C coordinator/projection roots are immutable/consumed; source history previous oneuse-A/B remain their own BLOCKED states. Historical original S bounded 90/90, b7e3/c42a overall FAIL and f51d historical-only PASS remain separate.

## 2. Implemented correction and exact preservation scope

Changed wrapper: Tools/AssemblyShadow/R03IR/run_terminal_current.py now imports sys and adds the physically adjacent owning R03 directory to sys.path before importing OriginalBatch/require. Existing wrapper command flags, early verify_source_roots actual 10-file admission before Batch/root creation, candidate_pins in-memory native e1e5 overlay, 3-build/5-Player execution injection and old native 74db historical manifest remain intact.

Changed no-write prereq: current_native_environment_admission.py now launches this very CLI's real --help in a fresh Python subprocess from external output parent with PYTHONPATH/PYTHONHOME/PYTHONSTARTUP removed. It requires CLI exit0, expected --workspace/--output/--demo-commit flags, empty stderr, returns typed no-Unity/Player receipt and actual stdout/stderr SHA-256. A failed import refuses the new expensive combined coordinator BEFORE creating its one-use root. The previous environment toolchain, exact source pins, original-S registration, 20 GiB hard disk floor and actual Unity executable checks remain unchanged.

Additional tests: 23 explicit actual fresh-subprocess current-native CLI contracts, including external cwd, no PYTHONPATH, fake cwd/PYTHONPATH run_local poisoning, required argument/malformed SHA/relative workspace/output/nonowning absolute workspace rejection before root creation, actual fresh module import, unchanged legacy runner/fixture/source pin Git blobs, no fake dry-run/SDK/Unity. Two new existing admission negative/positive tests make 27 for that suite. Historical source runner, Player fixtures, original S files, current native VM source, interpreter/package and current combined coordinator code Git blobs were not altered.

## 3. Mac/Linux CI — examined actual jobs, not inferred

Published Primary code-only commit 43fa6108ca092f5583ea3f807266d5827d5f10c8. Source-host [GitHub run 40459012594](https://github.com/night-outlook/hybridclr_demo/actions/runs/40459012594) completed **SUCCESS** on ubuntu-24.04 (job 122038940850) and macos-15 (job 122038941217). Raw job logs separately fetched and read, with exactly these test counts and no failure/error on **each** platform:

| Suite | Tests |
| --- | ---: |
| Original combined coordinator host contracts | 20 |
| Installed-native parity synthetic | 15 |
| Retained original-S/capacity/net8/new no-write CLI gate | 27 |
| **Actual standalone fresh Python interpreter CLI tests** | **23** |
| Original-S tiny Git sparse projection custody | 31 |
| Current source candidate / historic native pins | 20 |
| Strict Player verifier synthetic inputs | 27 |
| Full changed native VM source bytes | 12 |
| Original-S archive auditor host contracts (no full archive executed in CI) | 30 |
| **TOTAL per OS** | **205** |

The job logs include real test_02_actual_fresh_interpreter_help_from_external_cwd, test_20_real_readonly_admission_runs_same_fresh_cli and test_23_readonly_probe_strips_assisting_pythonpath PASS per host. Independently existing R03 current-native coherent source workflow run 40459012688 and R03 K source 40459012560, K terminal 40459012784 and L factory 40459012623 have completed SUCCESS at this same code commit; the distinct independent-review terminal host workflow is source-only and does not replace the October 8 review verdict.

All CI is source/host-only, not actual Unity/IL2CPP compiler, current-native linked Player, full real original-S archive reconstruction or independent full R03 reviewer acceptance. No Local file, SDK, original-S evidence or native production code was modified by the web agent.

### Related R03 independent-review host workflow: fixed CI checkout scope, not a reviewer verdict

The same code commit 43fa triggered independent-review terminal **host-test** CI run 40459012648. Its macos-14 job failed before tests: actions/checkout attempted the entire historical demo working tree (~195k files), exhausted the GitHub-hosted runner volume and reported No space left on device. Its ubuntu-24.04 job passed. This is a real CI-infrastructure FAIL, not an IR terminal method or Player runtime failure.

Primary restricted that workflow's checkout to Tools/AssemblyShadow/R03, R03IR and the required parallel R03Storage infrastructure. The intermediate macos host test run 40460171308 then revealed that the first sparse roster omitted R03Storage/storage_guard.py, producing an actual source-test ImportError while 149 other tests ran; this was a real incomplete CI-input finding, not rewritten into a green result. Primary added the missing dependency directory without modifying any historical test assertions or product source.

Final corrected GitHub Actions [run 40460340694](https://github.com/night-outlook/hybridclr_demo/actions/runs/40460340694), source-only CI commit 99f79a65a953aec47403128013135d1645beb19b, **SUCCESS** on macos-14 (job122043162893, 156/156 actual host Python tests, OK) and ubuntu-24.04 (job122043163193, 156/156, OK). Both raw job logs inspected. This adds no real Unity/Player evidence or independent human reviewer verdict and does not change oneuse-C outcomes.

## 4. Remaining gaps and exact next action

- **Current-native empirical IR-R03-02:** actual e1e5 source-matched real Unity2022.3.62f2 macOS arm64 3 native builds, five real Players and 126 physical installed changed-native-VM source pairs are still NotRun. CLI startup success is a prerequisite; downstream build/runtime behavior is unknown. Captured generic, post-publication initializer, virtual/interface/AOT crossing beyond fixed five cases and compiled/linker inclusion need independent claim-specific review.
- **Original-S IR-R03-01:** oneuse-C authentic byte/index/90-cell and historical 59-process joins Passed within the new historical read-only scope. Original full source/build/Unity Player/process semantic pairing and two omitted material generated method-pointer/invoker source outputs still require a separate independent review. No original S Player was replayed, original Oct 8 FAIL not overturned.
- The retained original-S fc55 is now legitimately **sparse**; do not rerun a sparse projection or create another worktree. Its original checkpoint physically preserved by oneuse-C. This historical observation must be reverified read-only as part of new oneuse-D.
- New Local requires a fresh unused external oneuse-D root and new exact demo remote source commit, available disk >=20 GiB (40 GiB advisory), installed Unity2022.3 arm64, existing net8 SDK/runtime only through process-local PATH and new genuine unassisted CLI startup admission. Run existing combined coordinator once; return first errors, no Local nontrivial source changes.

Stage state remains: Oct 8 full independent R03 **FAIL**, High IR-R03-01/02 OPEN, D1=A conservative NativeLayoutAdmissionV1/X02 deferral, D2=A observational performance and four contaminated Failed certificates retained. P1 incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 incomplete; R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, qualificationApproved=false, runtimeAcceptance=false, PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or Human Review Gate automatically.
