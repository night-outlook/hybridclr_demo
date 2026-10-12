# L consolidated Local Validation — terminal rejection and actual Bee factory

**ONE fresh L attempt.** Complete the entire ordered source/host/custody/compiler/admission chain before at most one runtime invocation. K is consumed; do not retry it. L is an attempt identifier, not H1/H2 or a Human Review Gate. No nontrivial implementation is assigned to Local.

## 1. Read and verify exact owning sources

Read `Docs/AssemblyShadow/README.md`, `Plan/CURRENT_STATUS.md`, current `Handoff/WEB_TO_LOCAL.md`, factual Local-owned `LOCAL_VALIDATION.md` / `RETURN_TO_WEB.md`, [Primary reconciliation](PRIMARY_RECONCILIATION.md), [audit](COMPLETION_AUDIT.json), original K checkpoint and original C scoped-loss policy. Retain the original R03 design/plan and independent FAIL/Human Review Gates.

All four canonical `night-outlook` repositories use `codex/assembly-shadow-r01b-h1` in `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/<repo>`. Independently verify actual top/path, branch/HEAD, clean status, origin, worktrees/submodules, fresh `git ls-remote` and `Tools/AssemblyShadow/R03/source-pins.json`. Reject truncated/divergent/dirty state; no reset, stash, clean or alternative worktree. The final full demo SHA is in the final Primary prompt and must be a Docs-only descendant of executable/test anchor `04a3cd93663f9a4e877a5524d9c22ee5a3fe0131`. Exact other pins:

- HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`
- package `948c0e3b4f8891481301770115e8ba4945eea6de`
- native **`c1a6876a3801a8343123977a0e230558904fd94d`**, not old K native0fa7.

Verify actual current executable bytes; ancestry alone is insufficient. Official CI38243672034 covers the current C#/native source; its old demo4f7 input must be compared byte-for-byte. The three newer Python receipt changes are covered by CI38262556820 at04a3. Both are attributed existing evidence, not fresh Local compilation or runtime.

## 2. Seven fresh external candidates

Base `/Users/ah/GitHub/hybridclr/r03-local-validation`. Prove all seven absent, canonical, nonsymlinked, mutually nonoverlapping, and disjoint from every source, installed Editor and retained S/R/Q/P/O/N/A/B/C/D/E/F/G/H/I/J/K or earlier reserved root. If occupied, stop; never delete/reuse/rename or invent a replacement. Create only preflight after source/location admission.

- `Preflight-R03L-after-K-52d9`
- `ManagedAPI-R03L-after-K-52d9`
- `NativeSDK-R03L-after-K-52d9`
- `Scratch-R03L-after-K-52d9`
- `R03IRLocal-L-after-K-52d9`
- `StorageCheck-R03IRLocal-L-after-K-52d9`
- `Storage-R03IRLocal-L-after-K-52d9`

Installed Unity exactly `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, macOS StandaloneOSX arm64, existing Python3.14/SDK-only .NET8.0.318/Apple clang as recorded. No installation/upgrade, Unity6000 process, global PATH/TMPDIR change or previous copied SDK/app reuse. Retain the established per-command environment, including the child TMPDIR policy. Record actual environment and versions.

## 3. Mandatory shared prerequisites

Authenticate original K/earlier Local report and raw evidence identities, original C/E/F/G/H/I/J manifests and source bindings, original sealed S15,712 indexed files/nine archive parts and **all15 immutable original S fixture DLLs**, retained R's original failed restoration and read-only Q `R03LocalBatch-20261006Q-lp-repair`. No regenerated original S fixture or missing historical native root. Preserve source and installed SDK/tool/managed-reference snapshots; label unindexed current-only inventories as such.

Run **203 R03 tool/process tests** once (this includes the20 scratch cases), **91 R03IR tests** once (includes17 factory assertions within one test and12 new receipt controls),25 C custody tests,nine retained-E controls,14 J collector tests; also the separately sanitized native snapshot test. Run current native rejection/reporting strict+ASan/UBSan, actual Object.h access, engine observer strict+ASan/UBSan and69 policy checks. Retain complete argv/cwd/environment/source/PID/time/exit/stream hashes. No skips or expected-outcome changes; report actual counts and stop on mismatch. CI cannot substitute for fresh host execution.

Complete **full original-C before custody** before official compilation/runtime:416,844 original identities,339,367 hash-verified survivors,77,477 exact unchanged missing path/hash identities,zero problems,completeScan=true,ScopedHistoricalLossStable,originalStrictCustody=Blocked. Any new missing/restored/changed/aliased path blocks. Authenticate retained-E before and F/G/H/I/J/K plus installed SDK before preservation. No current snapshot or after-only audit replaces an absent before. Four original S native roots remain Missing.

Any failed shared source/host/custody/preservation gate stops compilers, storage and Unity. Distinct read-only after checks may still be made safely, preserving NotRun rather than inventing admission.

## 4. Fresh current-source managed and native compiler gates

Run each compiler at most once in its separate new output. The two compile outcomes are independent while shared gates remain valid, but **both must Pass before runtime**. No edits, adjusted flags, warning suppression or repeated partial output. Preserve failures and remaining NotRun matrix rows.

```bash
export PYTHONDONTWRITEBYTECODE=1
PY=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
B=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
DOC="$W/hybridclr_demo/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation"
# The following commands run conditionally, never blindly after an earlier failure.
"$PY" -B -m unittest discover -s "$W/hybridclr_demo/Tools/AssemblyShadow/R03" -p 'test_*.py' -v
"$PY" -B -m unittest discover -s "$W/hybridclr_demo/Tools/AssemblyShadow/R03IR" -p 'test_*.py' -v
R03_SANITIZERS=1 "$PY" -B -m unittest discover -s "$W/hybridclr_demo/Tools/AssemblyShadow/R03IR" -p test_native_snapshot.py -v
"$PY" -B -m unittest discover -s "$DOC/IR_LOCAL_CUSTODY_01_2026-10-09" -p test_scoped_custody.py -v
"$PY" -B -m unittest discover -s "$DOC/IR_RUNTIME_01_2026-10-10" -p test_retained_e.py -v
"$PY" -B -m unittest discover -s "$DOC/IR_I_RESPONSE_RESERVE_6f02" -p test_debug_collection.py -v
"$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_terminal_rejection.py"
R03_SANITIZERS=1 "$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_terminal_rejection.py"
"$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_reporting.py"
R03_SANITIZERS=1 "$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_reporting.py"
"$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_object_access.py"
"$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_engine_observer.py"
R03_SANITIZERS=1 "$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_engine_observer.py"
c++ -std=c++17 -Wall -Wextra -Werror -pedantic -pthread \
 -I"$W/il2cpp_plus/libil2cpp" "$W/il2cpp_plus/tools/r03/terminal_execution_tests.cpp" \
 -o "$B/Preflight-R03L-after-K-52d9/policy"
"$B/Preflight-R03L-after-K-52d9/policy"
# Now complete the separate full before-custody and preservation gates in section3.
# Only after ALL shared gates passed:
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03/build_api.py" \
 --workspace "$W" --unity "$UNITY" --output "$B/ManagedAPI-R03L-after-K-52d9"
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03/native_validation.py" \
 --workspace "$W" --unity "$UNITY" --output "$B/NativeSDK-R03L-after-K-52d9" \
 --sdk-scratch "$B/Scratch-R03L-after-K-52d9"
```

Require five managed product/helper/Player outputs plus separate expected-negative twoCS0266/noDLL control, and **55 native C++17/arm64/fsyntax-only configurations** (11units x candidate/debug/probe-off/diagnostics-off/feature-off), including new rejection reserve through Runtime/AssemblyShadow and current test overlay. Bind actual source/SDK/copy hashes and complete commands/streams. J/K old native compilation does not coverc1. The installed SDK is read-only, scratch external and new. Compilation is not linking/Unity execution. Retain all warnings, including616 repeated Baselib occurrences when produced; do not require exactly the same warning count across hosts as a substitute for checking actual errors.

## 5. Two storage admissions, one 18-cell runtime execution

Only after all shared and both compiler gates pass, invoke the unchanged storage wrapper **once without --execute** using StorageCheck. Require fresh Admitted/exit0/batchStarted=false, correct device/Q/probe allocation/fsync/readback, unchanged max(64GiB,2xQ+20GiB) admission and20GiB sampled operating floor. Historical free space is not a reservation.

Only then invoke once with **--execute** under the distinct Storage root. It independently re-admits capacity. Do not run the core directly, retry a cell/Player or use an earlier app.

```bash
DEMO_SHA=REPLACE_FROM_FINAL_PRIMARY_FULL_40_SHA_PROMPT
Q="$B/R03LocalBatch-20261006Q-lp-repair"
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_terminal_storage_checked.py" \
 --workspace "$W" --unity "$UNITY" --demo-commit "$DEMO_SHA" --retained-q "$Q" \
 --output "$B/R03IRLocal-L-after-K-52d9" --storage-evidence "$B/StorageCheck-R03IRLocal-L-after-K-52d9"
# Only after this diagnostic admission and every earlier gate passed:
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_terminal_storage_checked.py" \
 --workspace "$W" --unity "$UNITY" --demo-commit "$DEMO_SHA" --retained-q "$Q" \
 --output "$B/R03IRLocal-L-after-K-52d9" --storage-evidence "$B/Storage-R03IRLocal-L-after-K-52d9" --execute
```

The scheduler stays **18 cells /3 builds /5 fresh Players**: release-baseline,debug-baseline,release-type,OFF,release-engine-unhandled plus three independent actual Bee observations. Original cell/request IDs remain unchanged; L freshness is established by source/build/app/PID/run/nonce/new paths. No sixth Player or additional stimulus. Independent observation cells may report failure even when their product builds Pass. A failed build never authorizes its Player.

## 6. Required new runtime evidence

**Semantic bridge:** retain healthy Boolean and rejection reserve preparation, real GC mask31,42/42,stable0->2 and canary1. Native baseline-owner/type rejection must reach the expected caught wrapper/receipt return1, not early phase170 catch/-1. All original post-poison reflection/delegate/reflected-AOT attempted entries must fail without side effects; stable must remain readable2, canary unchanged, first/native recovery code21 or13 and fixed diagnostics stable, physical reporter mask15. OFF remains canary1->2/mask0. Raw result Failed stays Failed even with process exit0; default state zeroes after early failure are not a reset claim.

**Finalizer/engine:** retain original uncaught run-bound sentinel, healthy logger1 and GC31, actual native reporter completion1..64, logger1->1, state6->9/code13, recovery and full500ms record. Exact guard-owned unhandled rejection may be reported natively; arbitrary exceptions must not be newly admitted or swallowed. Record any native unhandled-rejection messages/counts and absence/presence honestly. Do not force another finalizer case if none occurred. Sentinel alone, an empty file, SIGABRT/SEGV, timeout or native fatal is not a valid engine result. This bounded case does not qualify every finalizer, resource cleanup, shared-exception mutation or normal shutdown.

**Bee factory/driver:** authenticate original module/processor type and actual assembly hashes against the installed SDK, original forwarded factory calls, captured count/selected sequence, unique initially-empty driver, bounded actual nodes/logs, and **factoryRestored=true**. No second-factory identity waiver. Keep strict errors==0 and original exceptions/ref-out/return semantics. Unrestored/concurrently changed slot, unsupported Unity Mono proxy, missing driver or incomplete identity is failed evidence; do not fix it locally. An observation is not a build acceptance override or proof of I's historical emitter.

Capture full first-failure/rejection/phase/native snapshot logs, raw JSON and strict verifier outputs, source/request/nonce/PID/app UUID/build joins, all actual exit/signal/timeouts, original compiler/BuildReport warnings and errors. Failed native reporting or missing semantic fields cannot be replaced by inference from unchanged counters.

## 7. After checks, publication and stop

After any attempted work, independently run full original-C after custody, retained-E after, and F/G/H/I/J/K/SDK/source/fixture preservation against valid fresh before records, wherever feasible. New protected mutation itself requires ReturnRequired. After-only does not repair missing before. No restoration/rebaseline of77,477 missing S identities or four native roots.

Publish **one additive** `Docs/AssemblyShadow/History/M07R/R03/local-validation-l-after-k-52d9/` checkpoint and update only Local-owned `Handoff/LOCAL_VALIDATION.md` / `RETURN_TO_WEB.md`, preserving all prior bodies and states. Include exact source, fresh host/compiler/preservation, two storage sessions, actual18cell ledger/3builds/5Players/Bee identities, genuine raw failures and bounded archive/seal only if constructed. Vendor SDK/compiler/app binaries stay local; preserve permitted logs/hash inventories. Commit/push/read back all four remote HEADs, then STOP and return to Primary.

No retry, source change, guard/threshold relaxation, cache cleanup, new root substitution, forced GC suppression or broad acceptance. K/I/E remainFAIL;F/HBlocked;G/J historicalscopePassed;strictS custodyBlocked;allacceptanceflagsfalse;independentfullstageFAIL/re-reviewNotRun;PureInterpreterdisabled. Captured-generic/initializer,IR-R03-01 and legacy/performance/Human Review remain separate. NoH2/X02/M08A.
