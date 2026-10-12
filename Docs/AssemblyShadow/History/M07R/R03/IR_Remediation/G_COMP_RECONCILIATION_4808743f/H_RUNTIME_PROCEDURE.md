# H runtime procedure — one fresh post-G-COMP terminal-reporting batch

**Primary authorization is conditional on the final exact four-repository handoff and every prerequisite below.** H is an attempt identifier, not the H1/H2 Human Review Gate. It replaces neither G's compile-only record nor any prior runtime record. No previous attempt or designated F/G root is resumed.

## 1. Goal and allowed scope

Execute the **unchanged** `Tools/AssemblyShadow/R03IR/run_terminal_storage_checked.py` once diagnostically and, only after fresh admission, once with `--execute`. Its core runner schedules **14 cells**, three fresh native builds (`candidate-release`, `candidate-debug`, `candidate-off`) and four fresh Players:

| Case | Native role | Stimulus |
| --- | --- | --- |
| IR-R03-02-release-baseline | candidate-release | baseline-owner |
| IR-R03-02-debug-baseline | candidate-debug | baseline-owner |
| IR-R03-02-release-type | candidate-release | type-resolution |
| IR-R03-02-off | candidate-off | off |

No fifth Player, additional stimulus, unhandled-exception experiment, old app reuse, manual rerun, source correction or guard relaxation is authorized. The native observer compiled by G is not wired into these four Players as a genuine engine-originated experiment. Its coverage remains NotRun in actual Unity. H cannot by itself close IR-LOCAL-RUNTIME-01, captured-generic/initializer coverage, IR-R03-01, broader legacy/performance acceptance or the independent full-stage review.

## 2. Read order and source identity

Read canonical README.md, Plan/CURRENT_STATUS.md, Handoff/WEB_TO_LOCAL.md, this procedure, [Primary reconciliation](PRIMARY_RECONCILIATION.md), [raw audit](PRIMARY_G_AUDIT.json), Local-owned LOCAL_VALIDATION.md/RETURN_TO_WEB.md at G publication, and Plan/HUMAN_REVIEW_GATES.md. Preserve all recorded historical outcomes.

All four actual owning checkouts are under `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/`, branch `codex/assembly-shadow-r01b-h1`. The exact **final latest-pushed demo transport SHA** comes from the final Primary prompt; do not execute an audit/smoke branch or substitute the source anchor. Other pins are HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package `948c0e3b4f8891481301770115e8ba4945eea6de`, native `c386cdd1e8942561f1d1e1fada52d21ca524f174`. Verify all are full 40-character hexadecimal strings; no abbreviated/truncated pins.

For each repo independently record actual top, path, branch, HEAD, clean status, remote URL, submodules/worktrees and fresh `git ls-remote`. Verify demo source-pins.json equals those three non-demo HEADs. Check final demo executable bytes match G compilation source `d7f46bfd090313b41b38175ce1196f14484a3d1e` and publication `4808743fcbbc2075b9be305140bdf5ffa8583b0f`; all intervening changes must be only the documented Primary/Local Docs changes. Do not use a dirty tree, force/reset/stash/clean or overwrite another agent's work.

Key unchanged Git blobs: current Player `bbced69dee847a7f6b5b721fd55635976acf42a4`; core runner `386d47c041cf18a46ce741a269cd1ed1fd959d95`; storage wrapper `064795791687b50033fd247f28d6ae2ab25a8909`; native overlay `a23f927e28714ae6d4eb62c76e6127f96c9f709f`; C scoped verifier `ccc6af25d5d424b3bffe629ebd609ec5e5beed0a`; E-preservation verifier `52d1c177ba216bb0164099c082b1f3e9a2e6b40d`. Confirm these against actual Git objects, source snapshots, compiled input hashes and current source. Any mismatch blocks H and returns to Primary; do not quietly recompile an altered candidate under this handoff.

## 3. Fresh single-use roots and toolchain

Base is `/Users/ah/GitHub/hybridclr/r03-local-validation`. Before creating anything, verify these four candidates are absent, canonical/nonsymlinked and disjoint from source, installed Editor, retained Q, every S/R/Q/P/O/N/A/B/C/D/E root, F/G compile output, and all reserved older F runtime roots:

- `Preflight-R03IRLocal-H-post-GCOMP-7d42` — H source/host/custody/command records
- `R03IRLocal-H-post-GCOMP-7d42` — new sealed runtime batch, absent until executable admission
- `StorageCheck-R03IRLocal-H-post-GCOMP-7d42` — diagnostic storage session only
- `Storage-R03IRLocal-H-post-GCOMP-7d42` — separately admitted execution session

If any exists or aliases protected state, stop as Blocked; do not delete, rename, resume or invent another root. Root names are stable identifiers, not claims about wall-clock dates. Preserve actual command timestamps.

Use Unity `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, StandaloneOSX arm64, Python 3.14. Record actual `dotnet --info` and C++ compiler identity; the unchanged fixture generator requires the existing compatible .NET SDK. SDK-only use of an already installed toolchain may follow the documented E environment, but **no Unity 6000 Editor launch, installer, toolchain upgrade, global PATH/TMPDIR change or undocumented substitution**. Record per-command environment. Preserve the existing wrapper child-environment policy, including `/private/tmp`; do not change it to evade admission.

Retained Q is `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261006Q-lp-repair`. Never use G's copied SDK as a Player installation or use E's old app/native output. Build fresh isolated projects from the pinned source.

## 4. Required preflight, all before storage or Unity

1. Complete exact-source/remote/toolchain/root checks. Create only the new H preflight root. Authenticate G's original manifest (Git blob `4dc786b14983cc099e87cbd58189c9816f890de9`, SHA-256 `eda067e3a425fab00a1754d1f8dfbc3b444b409e70c7832940bec2609cd37fec`), all 544 listed files, actual managed response/source bindings and the complete 55-unit/profile result. Record G as **ReusedAuditedCompilation**, never as a new H compiler pass. No repeat of G's compile scripts is required while all compiled inputs are identical. Its original five targets and separate expected-negative control remain distinct.
2. Authenticate original C/E/F/G checkpoint objects/manifests, original S sealed/indexed evidence and all 15 original S DLL fixtures against their original Git authority. Never regenerate those 15 fixtures. The distinct deterministic IR-only target may be generated only by the existing core runner. Preserve R's retained failure/restoration state and Q's source/capacity identity.
3. Run fresh **20 scratch tests; all 65 current R03IR host tests; 15 original C-scoped verifier tests; nine retained-E tests; native reporting normal/sanitized, actual Object.h access, native observer normal/sanitized, and 69 standalone C++17 policy checks**. Require actual successful exits and no skips; save every raw stream. The expected subprocess failures inside negative tests remain expected controls, not Player evidence. These host tests do not replace actual builds/Players.
4. Complete a full original-C `verify_scoped_custody.py --phase before` using a new H receipt: `completeScan=true`, 416,844 original entries, exactly 339,367 surviving hashes, exactly 77,477 original missing path/hash identities, zero problems, `result=ScopedHistoricalLossStable`, `originalStrictCustody=Blocked`. Any new loss, restoration, byte change, symlink or incomplete scan blocks H. Never reduce the original map or expand the scoped exception.
5. Run existing `verify_retained_e.py --phase before` with a new H receipt: authenticate original E published index/top artifacts and three original installed-native inventories, then capture its additional current before/after snapshot. Require `PassedPreservationOnly`. This does not make E Passed or turn unindexed current snapshots into historical build proof. A missing/changed E artifact is a blocker, not permission to reconstruct it.
6. Record read-only preservation of G's installed-SDK inventory/tool inputs and its retained four compile-only roots, plus F's retained preflight. Use original G digest records for bytes covered by those records; current-only unindexed snapshots must be explicitly labeled current preservation, not retroactive provenance. Store any new inventories solely in H preflight. Recheck them after activity; do not write into old roots. G's source-owned files that intentionally change only through this documented Docs handoff must be distinguished from installed SDK/vendor inputs. No source, SDK or historical output cleanup.

The full C before audit and all above requirements are **mandatory**, not optional. Stop on the first failed prerequisite before storage/Unity. Complete independent after-preservation checks when feasible even if preflight stops; a missing before admission is never fabricated or inferred from an after pass.

## 5. Two separate storage sessions; one execution maximum

After all nonstorage prerequisites pass, invoke the unchanged storage wrapper **without `--execute`** using H batch and H StorageCheck roots. Require fresh `Admitted`, exit 0, `batchStarted=false`, complete device/Q bindings and allocation/fsync/readback probes. Retain original threshold `max(64 GiB, 2*Q + 20 GiB)` at each required location and the 20 GiB running floor. G's 84,323,880,960-byte observation is historical, not current capacity or a reservation. No protected cleanup, alternate temp path or threshold reduction.

Only after the diagnostic gate passes may ONE independently admitted invocation use H Storage with `--execute`. Recheck exact source and continued root absence before it. The wrapper remeasures capacity; do not bypass it to call the core runner directly. Preserve the core scheduler's dependency behavior: it may finish independent cells after another runtime cell fails, but no cell/process/build may be manually retried and no second `--execute` is authorized.

The permitted fresh work is exactly the existing 14 cells / three builds / four Players, including the distinct IR fixture generator. A partial batch, native fatal fallback, signal, timeout or missing raw JSON remains factual Failed/NotRun/Unavailable. Do not repair source, disable guards, substitute a build, relax a counter or reclassify the failed cell while H is in progress.

## 6. Commands (execute conditionally, never as an unconditional script)

Record argv, CWD, source identity, start/end, exit code, environment and full stdout/stderr hashes for each command. This skeleton assumes the exact final Primary SHA has already been checked against clean HEAD and remote; assigning DEMO_SHA below is not permission to accept an arbitrary branch tip.

```bash
export PYTHONDONTWRITEBYTECODE=1
PY=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BASE=/Users/ah/GitHub/hybridclr/r03-local-validation
P="$BASE/Preflight-R03IRLocal-H-post-GCOMP-7d42"
H="$BASE/R03IRLocal-H-post-GCOMP-7d42"
CHECK="$BASE/StorageCheck-R03IRLocal-H-post-GCOMP-7d42"
EXEC="$BASE/Storage-R03IRLocal-H-post-GCOMP-7d42"
Q="$BASE/R03LocalBatch-20261006Q-lp-repair"
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
C="$W/hybridclr_demo/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-c-custody-blocked"
C_DOC="$W/hybridclr_demo/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09"
E_DOC="$W/hybridclr_demo/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_RUNTIME_01_2026-10-10"
DEMO_SHA="$(git -C "$W/hybridclr_demo" rev-parse HEAD)"

# Only after exact source, G evidence, toolchain and four-root checks:
mkdir "$P"
"$PY" -B -m unittest discover -s "$W/hybridclr_demo/Tools/AssemblyShadow/R03" -p 'test_native_validation_scratch.py' -v
"$PY" -B -m unittest discover -s "$W/hybridclr_demo/Tools/AssemblyShadow/R03IR" -p 'test_*.py' -v
"$PY" -B -m unittest discover -s "$C_DOC" -p 'test_scoped_custody.py' -v
"$PY" -B -m unittest discover -s "$E_DOC" -p 'test_retained_e.py' -v
"$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_reporting.py"
R03_SANITIZERS=1 "$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_reporting.py"
"$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_object_access.py"
"$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_engine_observer.py"
R03_SANITIZERS=1 "$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_engine_observer.py"
c++ -std=c++17 -Wall -Wextra -Werror -pedantic -pthread \
  -I"$W/il2cpp_plus/libil2cpp" "$W/il2cpp_plus/tools/r03/terminal_execution_tests.cpp" -o "$P/policy"
"$P/policy"

# Only if all host, fixture, original-source and retained-data checks passed:
"$PY" -B "$C_DOC/verify_scoped_custody.py" --checkpoint "$C" \
  --phase before --receipt "$P/scoped-custody-before.json"
"$PY" -B "$E_DOC/verify_retained_e.py" --demo "$W/hybridclr_demo" \
  --phase before --receipt "$P/retained-e-before.json"

# Complete additional G/installed-SDK/F preservation checks before proceeding.
# One diagnostic invocation, no --execute:
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_terminal_storage_checked.py" \
  --workspace "$W" --output "$H" --unity "$UNITY" --demo-commit "$DEMO_SHA" \
  --retained-q "$Q" --storage-evidence "$CHECK"

# Only if every prerequisite and the fresh diagnostic admission passed:
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_terminal_storage_checked.py" \
  --workspace "$W" --output "$H" --unity "$UNITY" --demo-commit "$DEMO_SHA" \
  --retained-q "$Q" --storage-evidence "$EXEC" --execute

# Distinct after checks, also after a failed attempt where feasible:
"$PY" -B "$C_DOC/verify_scoped_custody.py" --checkpoint "$C" \
  --phase after --receipt "$P/scoped-custody-after.json"
"$PY" -B "$E_DOC/verify_retained_e.py" --demo "$W/hybridclr_demo" \
  --phase after --before "$P/retained-e-before.json" --receipt "$P/retained-e-after.json"
# Independently compare the retained G/F/installed-SDK inventories as well.
```

If before-E or before-C did not complete, record that fact and do not manufacture an after/before join. Any new historical mutation independently requires ReturnRequired even if all Player cases passed.

## 7. Runtime assertions and diagnostics

Every ON Player must establish **actual same active MethodInfo/delegate** positive controls (42/42), private primitive field `stable` from 0 to 2, first authentic baseline-owner code 21 or prescribed native type-resolution code 13, poisoned/final state 9 and RestartRequired recovery. After poison, active reflection, active delegate and reflected AOT canary must be attempted and rejected without executing bodies. Field must remain **readable at 2**, canary unchanged at 1, first recovery equal final recovery, fixed diagnostics readable. ON reporting probe mask **15**, OFF mask **0**. OFF state remains Disabled and ordinary canary advances 1→2. Preserve unchanged machine verifiers; no source/test expectation edits.

Retain native `[AssemblyShadowFirstFailure]`, `[AssemblyShadowPhase]`, `[AssemblyShadowTerminalReport]`, raw stderr and Player.log. Phases locate progress but do not prove semantic success. Capture actual new first failure if recurrence occurs; never attribute it retrospectively to E without evidence. A native fatal fallback is a failed Player. Preserve actual PID/run/request/build joins, process-group cleanup, exit/signal/timeout and missing-file states. Authenticate any macOS crash reports by process identity, timestamps and app/GameAssembly/UnityPlayer UUIDs; no debugger rerun or substitute crash log.

## 8. Publication and stop

Local owns its factual reports. Publish only the additive checkpoint `Docs/AssemblyShadow/History/M07R/R03/local-validation-h-post-gcomp-7d42/`, update LOCAL_VALIDATION.md and RETURN_TO_WEB.md while retaining historical bodies, and preserve full raw commands, all 14 cell states, three build receipts, four Player records when produced, request/source/fixture identities, exact storage admission/session/dispatch, and complete before/after custody/preservation. Index/archive/seal exist only for an actually constructed batch; zero launches must not receive a fabricated runtime seal. A seal proves bounded evidence integrity, not runtime or historical full-stage acceptance.

Retain vendor SDK, installed files and binaries locally; upload only permitted project evidence, hashes, logs and inventories. Commit/push, verify all four remote heads and record a publication receipt outside the sealed root. STOP after one H outcome and return to Primary. No Local nontrivial correction or retry; no automatic next milestone.

H can yield `FocusedEvidenceReadyForPrimaryReview` only if all required original runtime checks, seal, source and preservation checks pass. This is not full R03 acceptance. Engine-originated reporting, captured-generic/initializer, IR-R03-01, warning/runtime risks and independent full-stage review remain separate. E remains FAIL, F-COMP remains Blocked, G-COMP remains Passed within compile-only scope, and original strict S custody remains Blocked. All acceptance flags remain false and PureInterpreter expansion disabled. No H2/X02/M08A or Human Review Gate advancement.
