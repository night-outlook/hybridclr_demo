# IR-R03-02 focused Local Validation procedure — 2026-10-09 UTC

**Procedure prepared by Primary Implementation. Execute only if the current `WEB_TO_LOCAL.md` explicitly authorizes this exact source tuple.** This document by itself is **not a launch instruction**. It does not reopen historical S/R/Q/P/O/N, H2 or X02. The original independent R03 full-stage verdict remains FAIL.

## Objective and scope

Validate the **new** native terminal-execution guard with three fresh Unity 2022.3.62f2 macOS arm64 IL2CPP Player builds and four fresh isolated Player processes, and return actual first-failure/side-effect evidence. This is proportionate **focused** runtime evidence, not a rerun of S's 90 cells and not complete R03 acceptance.

The four *new* cases are:
1. `IR-R03-02-release-baseline` — ON Release, real physical AOT baseline-owner method guard caught, valid active reflection/delegate then rejected after poison.
2. `IR-R03-02-debug-baseline` — ON Debug, same real caught baseline-owner control.
3. `IR-R03-02-release-type` — ON Release, test-driven real `FailTypeResolution` boundary, then valid method rejection.
4. `IR-R03-02-off` — OFF Release, two ordinary reflected AOT canary invocations, no Shadow transaction.

Real captured-generic failure and real post-publication initializer-failure are **NotRun** in this subset. No claim about uninstrumented arbitrary direct AOT-to-AOT invocation, X02 expansion or production performance follows. The reference/S original matrices remain untouched.

## Exact repository inputs

All branches are `codex/assembly-shadow-r01b-h1`; the **final immutable four-head tuple must be read from the final Primary handoff** and verified against `git ls-remote` before any command.

| Repository | Owning checkout | Essential source authority |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Final pushed handoff SHA; `R03/source-pins.json` + `R03IR` |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `9ce1c1bfec9a21b92ea300acda5f27a3815b2c37` |

**Historical immutable witness:** S publication `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`, fifteen committed original S fixture Git objects at `Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/batch/host/player-fixtures`, inventory Git blob `0688bd2dad054bd59fcdd1564a050a398cfa14e7`. The special `--ir-target` Methods binary is separately deterministic, SHA-256 `8d0b28cbca4d889801883ad436c51c215b913f1645055590980f902f1e80fffd`, MVID `597eb18e-e0e7-6f8b-7e4a-6cdaabf9d1ff`. No regenerated 15-DLL set is permitted in this validation.

This new IR target was compiled by dnlib with a fixed PE timestamp and is separately named/receipted. Do not mistake it for S's `virtual-slot/Methods.dll`. Historical regeneration comparison failures remain Failed and immutable; they concern regenerated *new* bytes, not the byte identity of files copied directly from the original S commit.

## Required prerequisites and host checks

Mac: Unity `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, exact target StandaloneOSX arm64; dotnet SDK with net8 support and Python 3.14 at `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`. Do **not** launch Unity 6000.

Use the workspace `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`. For each nested repo independently verify owning path, clean tree (`git status --porcelain`), named branch, exact `git rev-parse HEAD`, canonical origin, and fresh `git ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1`. No reset/stash/clean/pull of an occupied dirty checkout. Local source discrepancy is a **preflight block**.

Before the expensive Player sequence, run read-only source-bound host checks in an external receipt folder (avoid `__pycache__`):
```bash
export PYTHONDONTWRITEBYTECODE=1
PY=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
"$PY" -B -m unittest discover -s "$W/hybridclr_demo/Tools/AssemblyShadow/R03IR" -p 'test_*.py' -v
```
Then run the exact checked-in native terminal policy test with `c++ -std=c++17 -Wall -Wextra -Werror -pedantic -pthread -I"$W/il2cpp_plus/libil2cpp" "$W/il2cpp_plus/tools/r03/terminal_execution_tests.cpp" -o <UNUSED_EXTERNAL_PATH>/terminal-policy`, execute it and retain JSON/command/log/source SHA. These host tests do not replace Unity native builds or Players.

**Source-bound CI prerequisite:** verify [native terminal policy Linux/macOS](https://github.com/night-outlook/il2cpp_plus/actions/runs/37872834945), [original-S input authority and deterministic new target](https://github.com/night-outlook/hybridclr_demo/actions/runs/37894308627), [IR host contracts](https://github.com/night-outlook/hybridclr_demo/actions/runs/37894308586), [Player C# API](https://github.com/night-outlook/hybridclr_demo/actions/runs/37874183375) and [official Unity native API compilation](https://github.com/night-outlook/hybridclr_demo/actions/runs/37893353097), each with actual job logs, exact executing commit and relevant file-source equivalence. A green earlier run is not automatically evidence for later different bytes; inspect the source diff.

## Retained evidence and conditional storage admission

Never modify or reclaim historical evidence. In particular retained R remains **staged** and Failed, Q's cause retains its historical status, S retains 90 Passed but no acceptance flags, and four contaminated unisolated warm certificates remain Failed.

All required paths must be unused and outside every owning repo and historical root. Fixed candidate paths (if still unused; otherwise **return to Primary for a new named root**, never overwrite):

- New IR sealed root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03IRLocal-20261009A-terminal`.
- Diagnostic-only capacity sidecar: `/Users/ah/GitHub/hybridclr/r03-local-validation/StorageCheck-R03IRLocal-20261009A-terminal`.
- Distinct execution capacity sidecar: `/Users/ah/GitHub/hybridclr/r03-local-validation/Storage-R03IRLocal-20261009A-terminal`.
- Preserved Q root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261006Q-lp-repair`.

The new `run_terminal_storage_checked.py` uses the **unchanged** `R03StorageAdmissionV1` policy, including exact preserved Q failure cell SHA, whole-root metadata sizing, `max(64GiB, 2*Q + 20GiB)` available-space policy, 1MiB allocation/fdatasync/readback probes, and 20GiB sampled operating floor. It checks all external temp, Git common metadata, batch, fixtures, workspace, and sidecar paths. No snapshots/quota/cache cleanup, no threshold change, no reservation claim. A capacity failure produces **CapacityBlocked/NotRun**, not an authorized Unity launch.

Diagnostic-only command, **no Unity launch**:
```bash
EXPECTED_DEMO_COMMIT="${EXPECTED_DEMO_COMMIT:?Set exact 40-character demo SHA from Primary handoff}"
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_terminal_storage_checked.py" \
  --workspace "$W" \
  --output /Users/ah/GitHub/hybridclr/r03-local-validation/R03IRLocal-20261009A-terminal \
  --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity \
  --demo-commit "$EXPECTED_DEMO_COMMIT" \
  --retained-q /Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261006Q-lp-repair \
  --storage-evidence /Users/ah/GitHub/hybridclr/r03-local-validation/StorageCheck-R03IRLocal-20261009A-terminal
```
**Do not execute the following while the current WEB_TO_LOCAL remains STOP.** Only after an affirmative Primary handoff and all checks pass, use **a fresh** capacity session (not the diagnostic sidecar) for one execution:
```bash
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_terminal_storage_checked.py" \
  --workspace "$W" \
  --output /Users/ah/GitHub/hybridclr/r03-local-validation/R03IRLocal-20261009A-terminal \
  --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity \
  --demo-commit "$EXPECTED_DEMO_COMMIT" \
  --retained-q /Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261006Q-lp-repair \
  --storage-evidence /Users/ah/GitHub/hybridclr/r03-local-validation/Storage-R03IRLocal-20261009A-terminal \
  --execute
```
The placeholders are **not** authority to run. Replace only from the final published Primary handoff SHA and preserve the executed shell/argv and receipts. The wrapper rechecks admission from scratch, observes capacity every five seconds, does not interrupt an in-flight command, retains the real fourteen-cell scheduler and core seal, and writes separate audit/capacity/dispatch receipts. If admission fails, do not create a Player; if a begun batch fails, do not retry its phases or alter results.

## Required validation evidence and final reporting

Exactly **14** cells, **3** fresh native builds and **4** fresh Players are planned. Do not treat a merely prepared or blocked cell as a completed build or Player.

The two original-S and IR-target preflight rows must prove the literal 15 original blob SHA-256 values, the distinct deterministic IR target SHA/MVID and the hard-coded request/run PID/nonce/source/build receipts. Every ON Player must show: state 6 and active `Keep` actually executes **twice** before failure; real caught terminal failure; state 9; post-failure **attempts** via reflection and delegate both rejected, no successful invocation; AOT canary count unchanged; `R03.Node.stable` still exactly 2 through a readable pre-resolved field; original recovery reason/first failure unchanged; native fixed diagnostics available and correctly bound. OFF must execute the ordinary canary twice with no shadow transaction. The ON type-resolution stimulus is test-driven; do not claim organically malformed generic/type metadata evidence. Verify original Q/S/R custody before and after independently; historical S is not re-executed.

Retain raw Player JSON/logs, request SHA, PID/command ownership, native install receipts and source inventory, all build receipts, test target/fixture authority, storage admission/samples/session, core ledger, index/archive/seal and explicit `ReturnRequired` or `FocusedEvidenceReadyForPrimaryReview`. The separate wrapper exit and capacity state must be consistent with these facts. Report to Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`; publish additive immutable checkpoint under `Docs/AssemblyShadow/History/M07R/R03/`. Verify remote before return. No unreviewed Local substantive native refactor.

**Stop after the focused evidence.** Next owner returns to Primary for unresolved true captured-generic and module-initializer regressions, IR-R03-01 semantic/capture work and separate independent re-review. Do not mark R03Accepted/H2Passed/qualification/readiness/PureInterpreter expansion true; never begin H2, X02 or M08A.
