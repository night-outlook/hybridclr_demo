# R03 current-native CLI startup repair — Design (2026-10-26)

**Owner:** Primary Implementation. **Scope:** IR-LOCAL-CURRENT-NATIVE-CLI-IMPORT-01 only. Not a new milestone, independent R03 review, runtime acceptance or H2.

## Observed Local failure — exact provenance

Source: night-outlook/hybridclr_demo@fdf73ca907ace8d9470c888a02d0c3bedc25379b, Docs/AssemblyShadow/Handoff/{LOCAL_VALIDATION.md,RETURN_TO_WEB.md}, and History/M07R/R03/local-validation-current-native-original-s-20261026-oneuse-c/{FINDING.json,LOCAL_RESULT.json,batch/RESULT.json,batch/steps/current-native-players/stderr.log}.

oneuse-C successfully sparse-projected the retained original-S fc55 auxiliary worktree; verified 16,978 original checkpoint files before and after; measured 19.844 to 46.334 GiB available. A fresh actual Local read-only admission passed with Unity2022.3.62f2 arm64, SDK8.0.318/runtime8.0.21 via process-only PATH. Exactly one combined coordinator then returned **ReturnRequired: 8 Passed, 1 Failed, 1 Blocked**. The eight scoped Passes include 104 host tests, full original-S nine-part archive/15,713 members/90 historical cells, 59 archived process joins and native host diagnostics. They do not establish current-native Player correctness or independent original-S semantic source/build/Player review.

The first Failed current-native-players child was a fresh Python interpreter launched from the external oneuse-C coordinator root. Before any Batch creation or Unity/build execution it raised:
    run_terminal_current.py line14 -> from run_local import Batch as OriginalBatch, require
    ModuleNotFoundError: No module named 'run_local'

The real module resides in adjacent Tools/AssemblyShadow/R03/run_local.py, not R03IR. The unchanged focused run_terminal_local.py inserts that adjacent directory, but is imported too late. The coordinator inserts R03 into the parent Python sys.path, which is not inherited by the child. Child exit1, no current-native batch/seal, 0/3 builds, 0/5 Players, 0/126 physical installed source pairs. Installed-source stage Blocked. This is a source-script import/launch defect, NOT native runtime evidence.

## Bounded source fix

Modify only Tools/AssemblyShadow/R03IR/run_terminal_current.py: import sys and, **before its first historical R03 import**, derive HERE from Path(__file__).resolve().parent, derive R03 as HERE.parent / "R03", then call sys.path.insert(0, str(R03)). This points only to the physically adjacent owning checkout source, matching the existing old focused runner's import contract. Keep all early current candidate ten-blob/source-remote checks, CurrentNativeBatch behavior, legacy 74db historical native pin, in-memory candidate e1e5 pin overlay, actual Player fixture, source build-v2 installer and strict negative oracle unchanged. Do not change historical run_local.py, run_terminal_local.py, the native/interpreter/package repositories or original S evidence.

## True fresh-process and negative tests

Add Tools/AssemblyShadow/R03IR/current_native_cli_contracts.py; explicit filename avoids broad historical test_*.py discovery. Launch subprocess.run([sys.executable, "-B", absolute wrapper, "--help"]) from an unrelated temporary working directory, with PYTHONPATH, PYTHONHOME and PYTHONSTARTUP omitted, PYTHONNOUSERSITE and PYTHONDONTWRITEBYTECODE set. Require exit0, expected --workspace/--output/--demo-commit flags, empty stderr and no evidence/Unity creation. Cover fake run_local.py in foreign cwd and poisoned PYTHONPATH, malformed/relative CLI arguments, invalid source checkout rejection, actual fresh module import, immutable legacy source/fixture Git blob IDs, and no dry-run bypass. These are real independent interpreter executions, not a same-process import substitute.

Extend current_native_environment_admission.py with verify_standalone_current_cli: run that actual --help subprocess without PYTHONPATH from the proposed output parent *before* the combined coordinator root can be created. Include argv/cwd/exit and stdout/stderr SHA-256 in its read-only prerequisite receipt, reject nonzero/stderr or missing expected options. It does not execute Unity/IL2CPP, compile .NET, produce Local batch roots or claim runtime acceptance. Extend existing admission hostile tests to reject a forged import failure before any output.

## Host-only verification and boundaries

Source-only Mac/Linux CI exercises 205 tests per platform: 20 coordinator, 15 installed-source synthetic, 27 retained worktree/capacity/net8/CLI admission, **23 actual standalone Python subprocess contracts**, 31 sparse checkout contracts, 20 current source pins, 27 Player-verifier synthetic oracles, 12 changed VM source tests and 30 original-S host contracts. Also check related current-native source and R03 historical K/L workflows. The code-only CLI startup Pass does NOT prove a native installed SDK, three fresh builds, five Players, generic/initializer support, source linker/compiled closure or product acceptance.

## New oneuse-D evidence plan and stop

oneuse-C coordinator and sparse projection are consumed: **never rerun either**. Retain the same clean detached sparse fc55 worktree and its complete protected checkpoint; do not re-sparsify or recreate. A fresh oneuse-D root needs an independently source-pinned four-repo live remote SHA, read-only toolchain/capacity/source/standalone CLI admission, a unique absent external output root, the original unchanged 20-GiB hard floor and advisory >=40 GiB headroom. Historical oneuse-C 46.33 GiB is an observation, not guaranteed current free space.

If admission passes, invoke the unchanged ten-stage combined coordinator **once**, requiring actual three current-native builds, five real Unity2022.3 arm64 Player cases and 126 physical installed VM source pairs, plus all original S read-only process/archive and native host stages. Another original S archived read-only check does not rerun historical S Players. Failure stops and returns raw first error to Primary; Local never modifies substantive source, expectations or used roots.

The October 8 independent full-stage R03 **FAIL**, High IR-R03-01/02, original S bounded 90/90, b7e3/c42a overall FAIL, f51d historical audit-only PASS, D1=A conservative NativeLayoutAdmissionV1/X02 deferral, D2=A observational performance/four contaminated Failed certificates all remain unchanged. P1 incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 incomplete. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, qualificationApproved=false, runtimeAcceptance=false, PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or automatic Human Review Gate.
