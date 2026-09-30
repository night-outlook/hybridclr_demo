# Primary Implementation → Local Validation: R03 batch B, managed lifetime repair

## Objective and preserved result

Run one fresh **36-cell R03 batch B** using the repaired managed command lifetime policy. Do not retry batch A, redesign the feature, enable PureInterpreter expansion, or enter H2.

Batch A remains `ReturnRequired`: **4 Passed, 3 Failed, 29 Blocked**, with a passed focused seal. Its three builds compiled but failed the process-group lifetime check before host assertions. Its Unity builds, EditMode tests and all nineteen Player cases remain Blocked/NotRun. The authoritative Local return is `2a9fdec813592fd79db511d5db96a6dcf1dea620`; neither Local-owned report nor its immutable checkpoint has been rewritten by Primary.

## Read order

1. `Docs/AssemblyShadow/README.md` and `Plan/CURRENT_STATUS.md`.
2. `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` (batch-A facts, not batch-B execution instructions).
3. `History/M07R/R03/C_LIFETIME_REPAIR.md`, `C_HOST_EVIDENCE.json`, and `C_VALIDATION_MATRIX.md`.
4. `History/M07R/R03/A_PRIMARY_IMPLEMENTATION.md` and `Plan/stages/R03-evolution-semantics.md` for unchanged product scope.
5. This document for the new execution command. Historical A/B handoff documents must not override it.

All relative paths above are under `Docs/AssemblyShadow/`.

## Source authority

Branch in all four repositories: `codex/assembly-shadow-r01b-h1`.

| Repository | Exact owning checkout | Source revision |
| --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Final documentation transport HEAD containing this handoff; resolve and verify as below |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `041c0cbb42d3e64e54fe605673d99799b5d63893` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `120bb01be680cec0375002a0823552d66d34b84c` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `1abb6bcaa85226f08c67f9da65edb3c58e8cb399` |

**New executable/CI source anchor: `7e2852fcd6c5bd9ebc82f2b3f97516742b772dc2`.** This supersedes the old `f5f571...` anchor for new runs. `94f2612a6c64c341ac38efcaf01952cb594f47d8` implements the repair; `7e2852...` fixes complete CI artifact retention. Only documentation/evidence may differ after the new anchor.

The exact demo execution commit is the final pushed transport SHA supplied in Primary's prompt. A standalone agent can resolve it as the latest commit touching this `WEB_TO_LOCAL.md`, but must require that commit to equal local HEAD and the current remote branch HEAD. Do not substitute an arbitrary later HEAD, the source anchor, a smoke commit, or the batch-A execution commit. The runner rechecks the four exact authorities before and after execution.

Native/package pins, Player cases, fixture generators, admission expectations, Unity build timeouts and the 36-cell ledger are unchanged. Reference graph tests use package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`. Reference Players still use the accepted R02 native cores (`1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` / `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`) with the current harness/package, not the historical accepted binary.

## Repair and changed modules

`Tools/AssemblyShadow/R03/command_lifetime.py` provides child-scoped build-server opt-outs, bounded process diagnostics, owned-group cleanup and immutable command receipts. `run_local.py` delegates `Batch.command` to that helper and supplies `--disable-build-servers`, `-p:UseSharedCompilation=false`, and `-nodeReuse:false` for managed builds. An observed surviving group remains failure even after cleanup. No global build-server shutdown or process-name-based killing is allowed.

`test_command_lifetime.py` adds 14 policy/real-process tests. `run_host_lifetime.py` and `.github/workflows/r03-primary.yml` exercise the actual `Batch.command`/`Batch.managed` call chain on .NET 8.0.318 on Linux and macOS, rather than using unrelated direct shell builds. The original 29 contracts remain; discovery now runs 43 tests.

## Exact environment and unused root

- Unity: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`.
- Target: `StandaloneOSX`, `arm64`.
- Python: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3` (batch-A environment).
- Existing SDK: `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`, SDK **8.0.318**. This is only the SDK location; do not launch that Unity 6000 Editor.
- New batch root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930B-lifetime`.

These executable paths are taken from the committed batch-A environment receipt. Verify they still exist and report the same versions. Missing/mismatched tooling is Blocked, not permission to install or substitute another Unity version. The batch root must not already exist; never delete or reuse A or B to bypass this check.

## Execution

First verify all four canonical origins and clean owning checkouts. Preserve all A and prior R02/H1 roots. Fast-forward only; no resets, stash, forced checkout, unrelated merge or source edits.

```bash
set -euo pipefail
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
DEMO="$WORKSPACE/hybridclr_demo"
BATCH=/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930B-lifetime
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
PYTHON=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
export DOTNET_ROOT=/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk
export PATH="$DOTNET_ROOT:$PATH"
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR=/private/tmp

for REPO in hybridclr_demo hybridclr hybridclr_unity il2cpp_plus; do
  test -z "$(git -C "$WORKSPACE/$REPO" status --porcelain=v1 --untracked-files=all)"
  test "$(git -C "$WORKSPACE/$REPO" branch --show-current)" = "$BRANCH"
  git -C "$WORKSPACE/$REPO" fetch origin "$BRANCH"
  git -C "$WORKSPACE/$REPO" merge --ff-only FETCH_HEAD
done

DEMO_COMMIT="$(git -C "$DEMO" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
test "$(git -C "$DEMO" rev-parse HEAD)" = "$DEMO_COMMIT"
test "$(git -C "$DEMO" ls-remote origin "refs/heads/$BRANCH" | awk '{print $1}')" = "$DEMO_COMMIT"
git -C "$DEMO" merge-base --is-ancestor 7e2852fcd6c5bd9ebc82f2b3f97516742b772dc2 "$DEMO_COMMIT"
git -C "$DEMO" diff --exit-code 7e2852fcd6c5bd9ebc82f2b3f97516742b772dc2 "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
test "$(git -C "$WORKSPACE/hybridclr" rev-parse HEAD)" = 041c0cbb42d3e64e54fe605673d99799b5d63893
test "$(git -C "$WORKSPACE/hybridclr_unity" rev-parse HEAD)" = 120bb01be680cec0375002a0823552d66d34b84c
test "$(git -C "$WORKSPACE/il2cpp_plus" rev-parse HEAD)" = 1abb6bcaa85226f08c67f9da65edb3c58e8cb399
test "$(dotnet --version)" = 8.0.318
test ! -e "$BATCH"

"$PYTHON" -B "$DEMO/Tools/AssemblyShadow/R03/run_local.py" \
  --workspace "$WORKSPACE" --output "$BATCH" \
  --unity "$UNITY" --demo-commit "$DEMO_COMMIT"
```

Also compare `DEMO_COMMIT` with the exact SHA in Primary's final prompt. Capture the preflight environment, actual command, start/end times, PID and exit code without altering runner outputs. The script is invoked once. On failure, inspect receipts and continue only the independent cells already scheduled by the runner; do not rerun the batch or invoke blocked cells manually.

## Required checks and evidence

The ledger stays **36 cells / four isolated builds / nineteen fresh-process Player cases**. Both baseline/candidate graph assertions, all 35 admission/method assertions, 15-DLL generation, complete EditMode execution with mandatory IDs, Debug/Release/OFF roles and unchanged Player expectations remain required. The expanded Python suite runs within the existing verifier-contracts cell.

Success requires all 36 cells Passed, `EvidenceReadyForPrimaryReview`, and a passed focused seal. Failed or blocked work remains `ReturnRequired`. `R03Accepted=false`, `H2Passed=false`, `pureInterpreterExpansionEnabled=false`, and `fullLegacyRegressionAcceptance=false` must remain unchanged.

Preserve `LOCAL_BATCH_RESULT.json`, `BATCH_EXECUTION.json`, `evidence-index.json`, `evidence.tar.gz`, `seal-receipt.json`, all cells/commands/host/builds/players outputs, Editor XML/logs, and the excluded live roots inventoried by receipts. New command receipts have `schemaVersion=2` and `lifetimePolicy=R03OwnedCommandV1`. Record all child policy values and, on survivors, `process-group-before-cleanup.json`, PID/PGID/member roster, and cleanup errors. Never replace `remainingProcessGroup=true` with the post-cleanup observation or whitelist a compiler executable.

## Local-owned return and boundaries

Update `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` factually, preserving A as historical. Create a new immutable `History/M07R/R03/local-validation-<date>-batch-b-<result>/` checkpoint with the exact executed tuple, counts, command/error evidence, archive/index hashes and custody audit. Commit/push those Local-owned demo reports/evidence and stop. Do not edit this Primary-owned handoff or external repositories.

No non-trivial implementation is delegated. Only independently verifiable, non-semantic trivial corrections may be proposed; do not change source, flags, timeouts, expectations, pins or cleanup rules to force this batch through. Return any such issue to Primary.

The original survivor executable remains unknown. Host lifecycle evidence is not Unity/native acceptance, not full R03 completion, and not H2. Full-stage legacy/resource, broader method/generic, startup/capacity/performance/memory work and gated PureInterpreter qualification remain Primary-owned after this return.
