# Primary Implementation → Local Validation: R03 batch D, complete build-helper API correction

## Objective and preserved result

Run one fresh **36-cell R03 batch D** after R03-LC-001. Do not retry A/B/C, modify their evidence, redesign R03, enable PureInterpreter expansion, or enter H2.

Authoritative Local return: `ed9afef29d17c64f15b281ea8b2176cb17d637b3`. C remains **ReturnRequired: 12 Passed / 5 Failed / 19 Blocked**, focused seal Passed. It verified fixture consumers and supervised compiler lifetime in the executed scope, but four build invocations and EditMode failed at the common helper's int-to-uint assignments. Native builds, Editor assertions and all nineteen Players did not run. Primary has not rewritten Local-owned reports or C's checkpoint.

## Read first

All relative paths here are under `Docs/AssemblyShadow/`:
1. `README.md` and `Plan/CURRENT_STATUS.md`.
2. `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` for unchanged C facts, not old execution commands.
3. `History/M07R/R03/E_BUILD_API_REPAIR.md`, `E_HOST_EVIDENCE.json`, and `E_VALIDATION_MATRIX.md`.
4. `History/M07R/R03/A_PRIMARY_IMPLEMENTATION.md` and `Plan/stages/R03-evolution-semantics.md` for unchanged product scope/full-stage exits.
5. This live handoff for the only new batch command. Earlier A/B/C/D preparation records are historical.

## Exact authority

All four repositories use `codex/assembly-shadow-r01b-h1`:

| Repository | Owning path | Revision |
| --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Final docs-only transport SHA in Primary's prompt, resolved and checked below |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `041c0cbb42d3e64e54fe605673d99799b5d63893` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `120bb01be680cec0375002a0823552d66d34b84c` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `1abb6bcaa85226f08c67f9da65edb3c58e8cb399` |

**New tested source anchor: `5931ada3c70958a7c6132219e059a42ee3cecbd0`.** Implementation `24a5a25972afc2a91afb26e68f97984c6dd8af2b` fixes the two count fields and adds full compilation coverage; `5931ada...` corrects `/noconfig` placement. Only Docs/AssemblyShadow evidence/documentation may differ after the new anchor. Previous source anchors do not authorize this run.

Execute the final pushed transport SHA supplied by Primary, not the source anchor, old executed commit, smoke branch or arbitrary later HEAD. A context-free receiver resolves the latest commit touching this WEB_TO_LOCAL.md and requires it to equal local HEAD and current remote HEAD. Also compare it with Primary's exact prompt before execution. The runner verifies all four sources at entry/final authority.

The three external pins, reference-core/package pins, 19 Player cases, four build roles, count/error acceptance rules, command deadlines and top-level ledger remain unchanged.

## Completed Primary repair

`PlayerProject/R03Build.cs` now declares both receipt counts as int, matching the actual Unity BuildSummary getters; no casts or JSON field/schema changes. Build success still requires a successful report and zero totalErrors.

`build_api.py` compiles the three actual package assemblies and complete helper using the pinned Unity compiler and actual API DLLs. It separately recompiles the preserved C helper and requires only its original two CS0266 errors. The CoreModule hash must match C's `e22a829a8022d30c6b2b11fe764d12a2383cf882b63a954641e3cd41ea56af6e`. All input bytes, command receipts, response files and output DLLs are bound. No API/package stubs are used. This same check is integrated in the existing player-fixtures cell before native preparation; the additional ten Python contracts bring the suite to 67.

Primary's new CI extracts the exact official Unity 2022.3.62f2 ARM64 installer and executes its compiler without installing or launching the Editor. Actual full-helper and package compilation, the precise old-helper negative control, and retained host regressions are recorded in E_HOST_EVIDENCE.json. This is compiler evidence, not Unity import/generation/IL2CPP/native acceptance. D must execute the integrated path.

## Pinned environment and unused root

- Unity `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`; StandaloneOSX, arm64.
- Python `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`.
- Direct managed SDK `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`, version **8.0.318**, used only as SDK. Do not launch Unity 6000.
- New root `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001D-build-api`.

Verify these recorded tools/versions. Missing or mismatched tooling is Blocked, not permission to substitute versions. The new root must not exist; never delete/reuse a root to bypass the guard. Preserve all A/B/C and R02/H1 evidence.

## Run once

Verify canonical origins, clean owning checkouts and branches before syncing. Fast-forward only; no reset, stash, forced checkout, unrelated merge or source edits.

```bash
set -euo pipefail
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
DEMO="$WORKSPACE/hybridclr_demo"
BATCH=/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001D-build-api
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
git -C "$DEMO" merge-base --is-ancestor 5931ada3c70958a7c6132219e059a42ee3cecbd0 "$DEMO_COMMIT"
git -C "$DEMO" diff --exit-code 5931ada3c70958a7c6132219e059a42ee3cecbd0 "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
test "$(git -C "$WORKSPACE/hybridclr" rev-parse HEAD)" = 041c0cbb42d3e64e54fe605673d99799b5d63893
test "$(git -C "$WORKSPACE/hybridclr_unity" rev-parse HEAD)" = 120bb01be680cec0375002a0823552d66d34b84c
test "$(git -C "$WORKSPACE/il2cpp_plus" rev-parse HEAD)" = 1abb6bcaa85226f08c67f9da65edb3c58e8cb399
test "$(dotnet --version)" = 8.0.318
test -f "$UNITY"
test ! -e "$BATCH"

"$PYTHON" -B "$DEMO/Tools/AssemblyShadow/R03/run_local.py" \
  --workspace "$WORKSPACE" --output "$BATCH" \
  --unity "$UNITY" --demo-commit "$DEMO_COMMIT"
```

Before running compare DEMO_COMMIT with Primary's final prompt. Capture preflight/environment, exact command, timestamps/PID and exit without changing runner outputs. Invoke once. A failed preflight is Blocked, not a fictional completed batch. Never run blocked cells manually or retry a failed batch.

## Required scope and evidence

Keep **36 cells / four native build roles / nineteen fresh-process Player cases**. The verifier cell runs 67 contracts. The player-fixtures cell keeps all original 15-DLL/33-audit/33-Unity-consumer/invalid-key and valid-invalid Editor probes and adds the complete helper compilation from E_VALIDATION_MATRIX.md.

All normal compiles/builds require exit 0 and the corresponding semantic/output proof. The existing named invalid-key controls may expect their exact CS0009, and the new preserved-old-helper control may expect exactly two CS0266 errors with no output. Each must still have clean lifetime. Nonzero product build exits cannot be reclassified as negative-control success.

Preserve all original result/ledger/index/archive/seal, cells/commands/host/fixtures/consumers/lifecycle/build/Editor/Player files, supervision receipts and excluded live roots. In addition retain `build-api/inputs.json`, `build-api/results.json`, each `build-api/*/compiler.rsp`, the compiled package/helper DLLs, and all five additional command receipts/streams. The new directory is part of the existing focused seal. Do not edit the preserved C helper: the check reads its byte-bound repository snapshot only.

For supervised Unity calls the outer PID identifies the supervisor; direct Player PID/run-ID binding remains unchanged. No global compiler shutdown, survivor exception, timeout extension, hash relaxation or rewritten raw flag is authorized.

All 36 cells and the focused seal must pass for EvidenceReadyForPrimaryReview. Otherwise retain ReturnRequired and exact Failed/Blocked/NotRun classifications. R03Accepted=false, H2Passed=false, pureInterpreterExpansionEnabled=false and fullLegacyRegressionAcceptance=false remain mandatory.

## Local-owned return and stop

Write factual results to `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`, preserving C as historical. Add a new immutable `History/M07R/R03/local-validation-<date>-batch-d-<result>/` checkpoint with executed tuples, counts, command/error details, added compile evidence, hashes and custody audit. Commit/push these Local-owned demo reports/evidence, then stop for Primary. Do not edit this Primary handoff or external repositories.

No non-trivial implementation is delegated. Source, compiler flags, count types, expectations, pins, timeouts, cleanup rules or new failing cases return to Primary; do not force a pass locally. The known compiler blocker is fixed and compile-verified, but installer/generation/IL2CPP/native/runtime failures may still surface. Full-stage regressions, measurement, PureInterpreter qualification and independent review remain Primary-owned; this focused D cannot approve R03, H2 or release.
