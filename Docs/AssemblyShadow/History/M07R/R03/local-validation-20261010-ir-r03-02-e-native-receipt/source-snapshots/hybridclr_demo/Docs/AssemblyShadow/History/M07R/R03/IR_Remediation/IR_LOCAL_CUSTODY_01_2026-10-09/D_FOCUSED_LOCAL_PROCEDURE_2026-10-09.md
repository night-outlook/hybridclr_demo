# IR-R03-02 D — focused fresh Local procedure (2026-10-09)

**Run only under exact final Primary four-SHA handoff.** This D attempt is new; never retry C, relabel its `CustodyBlocked` result, modify S caches, repair R, run H2/X02/M08A or weaken storage/source gates. The [Primary disposition](README.md) accepts only an explicitly measured *unchanged* historic custody loss for one **new independent** terminal Player witness, **not** a strict historical-custody PASS or original S native provenance recovery.

## Sources and read order

First read `Docs/AssemblyShadow/README.md`, `Plan/CURRENT_STATUS.md`, `Handoff/WEB_TO_LOCAL.md`, Local-owned `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md`. Then this procedure, its [custody decision](README.md), the exact [C checkpoint](../../local-validation-20261009-ir-r03-02-c-custody-blocked/README.md), [B source-bound C# procedure](../IR_R03_02_FOCUSED_LOCAL_PROCEDURE_2026-10-09.md), S fixture policy, R03 design, independent FAIL/C04 erratum and HUMAN_REVIEW_GATES.

All owning worktrees are `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/<repo>`, branch `codex/assembly-shadow-r01b-h1`. Final demo SHA comes **only** from final Primary prompt and must be a Docs-only descendant of `ba47b41674b83a6f694ac4f8ac1bc8f83a9da24b` (compiled current Player). Non-demo SHAs: HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`; hybridclr_unity `948c0e3b4f8891481301770115e8ba4945eea6de`; il2cpp_plus `9ce1c1bfec9a21b92ea300acda5f27a3815b2c37`. Inspect each checkout separately: real location, clean status, HEAD, branch, canonical origin, worktree, submodules and fresh `git ls-remote`. No switch/reset/stash/clean of unrelated local state.

## Fresh D external roots

Under `/Users/ah/GitHub/hybridclr/r03-local-validation`, verify these **four exact candidates** are absent, nonsymlinked and nonoverlapping with every source, historic or peer root **before** creating only preflight. Otherwise stop and return to Primary for a different explicitly authorized set. No reuse of A/B/C.

- `Preflight-R03IRLocal-20261009D-custody-scoped` — new preflight receipts
- `R03IRLocal-20261009D-custody-scoped` — new sealed batch; keep absent until admitted execution
- `StorageCheck-R03IRLocal-20261009D-custody-scoped` — diagnostic-only session
- `Storage-R03IRLocal-20261009D-custody-scoped` — separate one-shot execution session

Immutable C checkpoint: `$W/hybridclr_demo/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-c-custody-blocked`. Retained read-only Q: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261006Q-lp-repair`. Unity: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`; target StandaloneOSX arm64; Python 3.14; never launch Unity 6000.

## Prerequisite and execution sequence

1. Confirm all four exact pushed remote pins/source manifest, **Docs-only delta** since compiled ba47, unused roots, no historical modifications. Record commands and their source/exit/provenance. Only then create the fresh preflight directory.
2. Authenticate the original S five top artifacts/15,712 indexed members and the literal original 15 S DLL Git blobs. Use the committed existing fixture tool, never regenerate S input bytes or use old native S installation as new build source. IR target generation remains NotRun until actual new scheduler work.
3. Reverify current-body C# API CI [37903041633](https://github.com/night-outlook/hybridclr_demo/actions/runs/37903041633), job113729828150, **all 22 actual input hashes/blobs**, package/source equivalence, output/log receipts using the exact command in B procedure, with **D preflight destination** rather than B. It compiled with 0 errors/13 warnings against pinned package and checked-in Unity API stubs, not real Unity Player.
4. Run fresh 64 Python `Tools/AssemblyShadow/R03IR/test_*.py` tests, native 69 checks compiled with C++17 and the exact flags below, and ten additional synthetic [scoped-custody tests](test_scoped_custody.py). Persist raw stdout/stderr, commands, hashes and exits. A current runtime source difference invalidates inherited compiler evidence.
5. **Before any Unity invocation**, run [verify_scoped_custody.py](verify_scoped_custody.py) against **the immutable original C checkpoint and its exact four-part prior map**. It reads and SHA-verifies all 416,844 map entries, 77,477 C missing/error identities and current live bytes. Require exit0 and `ScopedHistoricalLossStable`, `presentVerified=339367`, `historicalStillMissing=77477`, `originalStrictCustody=Blocked`, zero problems and complete scan. It never rebaselines the original map. Any new missing, changed content, symlink, restored item, tampered checkpoint or incomplete scan => **Blocked**, no runtime. Keep original C reports and four historical installedNativeRoot states Missing.
6. Run **one diagnostic-only** `run_terminal_storage_checked.py` on the new D batch and `StorageCheck` roots, **without** `--execute`. Require fresh exit0 / Admitted and `batchStarted=false`, the original Q binding and full-size accounting, `max(64GiB,2*Q+20GiB)` admission, 64 GiB requirement, 20 GiB live floor and probes. C's earlier 77.912 GiB cannot be reused; no threshold/temp/quota/snapshot/cleanup change.
7. **Only if every prerequisite above passed**, run the same storage wrapper **once** with new D `Storage` sidecar and `--execute`. It independently repeats admission before launching the unchanged **14 cells / three native builds / four Players**. Otherwise return Blocked/NotRun with zero launches and no synthetic ledger/seal. If an execution begins and fails, preserve actual failure; no cell retry, resume, alternate path or manual fix.
8. Re-run full scoped custody **after** whichever diagnostic/execution actually took place, using a new receipt. A fresh post-execution loss independently forces `ReturnRequired`; it cannot be hidden by a green runtime cell. Keep missing history Missing/Blocked in both reports.
9. Publish Local-owned `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` plus additive checkpoint `Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-d-custody-scoped/` with authenticated raw receipts/manifest, then commit/push/verify remote. Stop and return to Primary.

The following commands are an **ordered conditional template**, NOT a command batch to run blindly:

~~~bash
export PYTHONDONTWRITEBYTECODE=1
PY=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BASE=/Users/ah/GitHub/hybridclr/r03-local-validation
P="$BASE/Preflight-R03IRLocal-20261009D-custody-scoped"
D="$BASE/R03IRLocal-20261009D-custody-scoped"
CHECK="$BASE/StorageCheck-R03IRLocal-20261009D-custody-scoped"
EXEC="$BASE/Storage-R03IRLocal-20261009D-custody-scoped"
C="$W/hybridclr_demo/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-c-custody-blocked"
DOC="$W/hybridclr_demo/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09"
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
Q="$BASE/R03LocalBatch-20261006Q-lp-repair"
EXPECTED_DEMO_COMMIT=REPLACE_WITH_EXACT_FINAL_PRIMARY_HANDOFF_SHA
# Do ALL source/remote/unused-root checks first; then create only P:
mkdir "$P"
"$PY" -B -m unittest discover -s "$DOC" -p 'test_scoped_custody.py' -v
"$PY" -B -m unittest discover -s "$W/hybridclr_demo/Tools/AssemblyShadow/R03IR" -p 'test_*.py' -v
c++ -std=c++17 -Wall -Wextra -Werror -pedantic -pthread \
  -I"$W/il2cpp_plus/libil2cpp" "$W/il2cpp_plus/tools/r03/terminal_execution_tests.cpp" \
  -o "$P/terminal-policy"
"$P/terminal-policy"
"$PY" -B "$DOC/verify_scoped_custody.py" \
  --checkpoint "$C" --phase before --receipt "$P/scoped-custody-before.json"
# Only after exact source/API/fixture/scope checks are passed:
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_terminal_storage_checked.py" \
  --workspace "$W" --output "$D" --unity "$UNITY" \
  --demo-commit "$EXPECTED_DEMO_COMMIT" --retained-q "$Q" --storage-evidence "$CHECK"
# Only after the above diagnostic is Admitted / exit0 and every gate Passed:
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_terminal_storage_checked.py" \
  --workspace "$W" --output "$D" --unity "$UNITY" \
  --demo-commit "$EXPECTED_DEMO_COMMIT" --retained-q "$Q" --storage-evidence "$EXEC" --execute
# Independently perform after-custody even when execution is not admitted:
"$PY" -B "$DOC/verify_scoped_custody.py" \
  --checkpoint "$C" --phase after --receipt "$P/scoped-custody-after.json"
~~~

ON Players must execute their true same-active-method reflection and delegate pre-poison (42/42), real instance private counter `stable` reaches 2, then a caught genuine baseline-owner or test-driven type-resolution terminal failure. After poison, attempt reflection/delegate and ordinary reflected AOT canary: none may run/modify the active counter or AOT canary, and the pre-resolved private field must remain **readable** at 2. First-failure recovery/state/fixed diagnostics stable. OFF control ordinary canary executes twice without a Shadow transaction. Retain 14 individual cell states, three actual native builds, four raw Player results/logs, original fixture and new IR target hashes/MVID, request/PID/nonce/build/source joins and full result/index/archive/seal plus separate storage and both custody receipts. Failure of a proof is Failed/Blocked/NotRun as appropriate, not Passed.

Original full historical custody remains `CustodyBlocked` and S native installation provenance incomplete. This scoped D result does not prove genuine captured generic/initializer paths, close IR-R03-01, the independent R03 FAIL, or full legacy acceptance. `R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled.
