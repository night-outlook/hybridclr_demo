# Primary Implementation → Local Validation: R03 completion batch O

## Objective

Run **exactly one fresh batch O** to validate LN-001–LN-004 and the complete remaining R03 integration. No non-trivial implementation is assigned to Local.

N remains ReturnRequired: **90 cells, 48 Passed / 4 Failed / 38 Blocked; seal Passed**. Preserve N and all earlier results. Do not retry N or reuse its apps/root.

## Read first

1. `Docs/AssemblyShadow/README.md`
2. `Docs/AssemblyShadow/Plan/CURRENT_STATUS.md`
3. `Docs/AssemblyShadow/History/M07R/R03/Q_INTEGRATION_REPAIR.md`
4. `Docs/AssemblyShadow/History/M07R/R03/Q_HOST_EVIDENCE.json`
5. `Docs/AssemblyShadow/History/M07R/R03/Q_VALIDATION_MATRIX.md`
6. Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` for N's factual state.

## Exact source

All branches: `codex/assembly-shadow-r01b-h1`.

| Repository | Path | Exact source |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | Final documentation-only transport containing this file; exact SHA supplied in Primary's final prompt |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | 1cf87f8209790f9fb2ebec97487dc1990ccd56c5 |

Executable/CI anchor: `fefe846b1209d18a96c432ed0ca2222f16cda976`. Every later demo change must be under `Docs/AssemblyShadow/**`.

## Prepared repairs

- LN-001: exact 13-file package-delta scope with unchanged 754/755 catalogs and fail-closed extra-file detection.
- LN-002: reference metadata revalidation in a separate equivalent captured closed domain; source/disk/semantic mutation guards retained.
- LN-003: explicit authenticated native-codec source context, threaded through resource and early-success verification; no ambient-cwd or fallback checkout.
- LN-004: consistent canonical simple-name lookup while preserving original load-order binding, full identities, duplicate/order/hash guards.

Primary host/compiler CI passed at the executable anchor. These checks do not replace fresh Unity/Player validation.

## Environment and new root

- Unity: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`
- Python: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`
- SDK-only DOTNET_ROOT: `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`, version 8.0.318. Do not launch Unity 6000.
- New root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261005O-ln-closure`

Existing output, dirty/wrong checkout, missing tools, wrong versions or source mismatch are blockers. Do not delete evidence or substitute versions.

## Execute once

Fast-forward only. No reset/stash/forced checkout/unrelated merge or source edit. Require demo HEAD and remote branch head to equal Primary's exact final prompt SHA.

```bash
set -euo pipefail
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
DEMO="$WORKSPACE/hybridclr_demo"
BATCH=/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261005O-ln-closure
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
PYTHON=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
export DOTNET_ROOT=/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk
export PATH="$DOTNET_ROOT:$PATH"
export DOTNET_MULTILEVEL_LOOKUP=0
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
git -C "$DEMO" merge-base --is-ancestor fefe846b1209d18a96c432ed0ca2222f16cda976 "$DEMO_COMMIT"
git -C "$DEMO" diff --exit-code fefe846b1209d18a96c432ed0ca2222f16cda976 "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
test "$(git -C "$WORKSPACE/hybridclr" rev-parse HEAD)" = 4b2774b066cfc6afd77a8c8aded6bda7ea574f55
test "$(git -C "$WORKSPACE/hybridclr_unity" rev-parse HEAD)" = 948c0e3b4f8891481301770115e8ba4945eea6de
test "$(git -C "$WORKSPACE/il2cpp_plus" rev-parse HEAD)" = 1cf87f8209790f9fb2ebec97487dc1990ccd56c5
test "$(dotnet --version)" = 8.0.318
test -x "$UNITY" && test -x "$PYTHON" && test ! -e "$BATCH"
"$PYTHON" -B "$DEMO/Tools/AssemblyShadow/R03Completion/run_completion.py"   --workspace "$WORKSPACE" --output "$BATCH" --unity "$UNITY" --demo-commit "$DEMO_COMMIT"
```

Invoke once. Independent cells continue under the runner; dependents remain Blocked. Do not manually retry a phase.

## Required scope and evidence

Retain **90 cells, six fresh builds, 59 fresh Players, early 18 Editor preflight and both 754/755 zero-skip rosters**.

In addition to all existing completion evidence, retain:
- editor-source-scope with actual 13-file delta and both catalogs;
- reference-binding inputs, all 15 fresh case receipts and reference-context diagnosis;
- qualification reports for baseline and P01–P05;
- codec authority/context receipts including repository top-level, commit and codec hash;
- all five fresh schema-2 native-layout sidecars and complete layout-identity-verification;
- P05 finalization/restoration, production integration, resource contracts, measurement and early-startup evidence;
- complete ledger/result/index/archive/seal and final authority.

All existing guards remain. Preserve four contaminated producer controls' Failed unisolated certificates. Missing/unemitted evidence remains Unavailable/NotRun, never empty success.

## Verdict and return

All 90 cells and the seal must Pass for `EvidenceReadyForPrimaryReview`; any Failed/Blocked cell returns `ReturnRequired`.

Even on green O: `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, PureInterpreter expansion disabled. No performance SLA or Human Review Gate approval follows automatically.

After exactly one invocation, update Local-owned reports factually, create an immutable batch-O checkpoint, commit/push only Local-owned evidence/docs, verify remote HEAD, then stop. No non-trivial Local source changes, guard weakening, scope reduction, hash rebinding, package substitution, old-app reuse or historical reclassification.
