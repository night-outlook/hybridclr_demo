# Primary Implementation → Local Validation: R03 completion batch P

## Objective

Run **exactly one fresh batch P** to validate the four batch-O returns together on the published repair candidate, including the new live source-versus-linked policy-domain evidence. Do not retry or reclassify batch O. No non-trivial implementation is assigned to Local Validation.

Batch O remains authoritative historical evidence: **90 cells, 58 Passed / 30 Failed / 2 Blocked; seal Passed**. Preserve O, N and all earlier results/custody unchanged.

## Read first

1. `Docs/AssemblyShadow/README.md`
2. `Docs/AssemblyShadow/Plan/CURRENT_STATUS.md`
3. `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md`
4. `Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md`
5. `Docs/AssemblyShadow/History/M07R/R03/local-validation-20261005-batch-o-return-required/README.md`
6. `Docs/AssemblyShadow/History/M07R/R03/LO_Continuation_2026-10-06/PRIMARY_REVIEW.md`

## Exact source

All branches: `codex/assembly-shadow-r01b-h1`.

| Repository | Path | Required source |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | executable source `9c4b76a540e74c045cabaf9e700051512a75cead`; CI-only timeout commit `8db761455dfd73ef01eac7d48eb39c69ca253cf8`; latest pushed handoff transport SHA is supplied in Primary's final prompt |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` |

For the demo repository, require the final prompt SHA to equal both local HEAD after fast-forward and remote branch HEAD. Require `9c4b76a…` to be an ancestor and require no non-documentation diff after it:

```bash
git -C "$DEMO" merge-base --is-ancestor 9c4b76a540e74c045cabaf9e700051512a75cead "$DEMO_COMMIT"
git -C "$DEMO" diff --exit-code 9c4b76a540e74c045cabaf9e700051512a75cead "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow' ':!.github/workflows/r03-completion-api.yml'
git -C "$DEMO" diff --exit-code 8db761455dfd73ef01eac7d48eb39c69ca253cf8 "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
```

The only non-Docs change after executable anchor `9c4b76a…` is `.github/workflows/r03-completion-api.yml`, changing the CI timeout from 60 to 120 minutes; it does not alter the Unity/Player implementation.

The disposable Connector smoke branch is not product source and must never be merged: `codex/connector-smoke-20261006-primary-r03`.

## Repairs under validation

### R03-LO-001 — policy-domain separation

The production integration keeps the original source/compiler policy immutable, derives a separate linked-Player policy, and uses the source policy for restored-baseline compilation. Before that compile, the fresh Unity project now emits `compiler-policy-domains.json` plus source/linked policy bytes. Required facts:

- the real live Unity source inventory validates with the source policy;
- the linked-Player policy is rejected against that source inventory;
- the three original guards remain present for `Unity.Burst.Unsafe`, `Unity.RenderPipelines.Universal.2D.Internal`, and `Unity.RenderPipelines.Universal.Config.Runtime`;
- source and linked policy inputs remain byte-stable during validation;
- P01–P05 analysis still succeeds;
- restored-baseline compilation completes and final comparison has zero changed roots and zero closure.

### R03-LO-002 — codec context

All resource and positive early-startup consumers must retain the authenticated owner/project context used to resolve the relative codec pin. No ambient working-directory or fallback checkout is acceptable. Revalidate all 13 ON resource cases and all four positive early-startup cases, retaining the existing negative controls.

### R03-LO-003 — linked-DLL identity lookup

ON/OFF NoPatch measurement cells must locate linked images by canonical simple assembly name while retaining original load order and independently checking physical DLL metadata, identity, hash/MVID, duplicates and order.

### R03-LO-004 — image-record consumer contract

P01/P03 measurement cells must pass the complete image record to the methods/PDB consumer. Revalidate all measurement method, symbol, business, exception and aggregate outputs; do not substitute a synthetic methods list.

## Environment and fresh root

- Unity: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`
- Python: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`
- SDK-only `DOTNET_ROOT`: `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`, expected SDK `8.0.318`; do not launch Unity 6000.
- New root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261006P-lo-repair`

An existing output root, dirty/wrong checkout, unexpected branch/head, missing tool, wrong version, or source mismatch is a blocker. Do not delete prior evidence or substitute versions.

## Execute once

Fast-forward only. Do not reset, stash, force-checkout, merge unrelated work, edit source, weaken guards, substitute packages, rebind hashes, or reuse old apps/results.

```bash
set -euo pipefail
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
DEMO="$WORKSPACE/hybridclr_demo"
BATCH=/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261006P-lo-repair
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

DEMO_COMMIT="$(git -C "$DEMO" rev-parse HEAD)"
test "$DEMO_COMMIT" = "$(git -C "$DEMO" ls-remote origin "refs/heads/$BRANCH" | awk '{print $1}')"
git -C "$DEMO" merge-base --is-ancestor 9c4b76a540e74c045cabaf9e700051512a75cead "$DEMO_COMMIT"
git -C "$DEMO" diff --exit-code 9c4b76a540e74c045cabaf9e700051512a75cead "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow' ':!.github/workflows/r03-completion-api.yml'
git -C "$DEMO" diff --exit-code 8db761455dfd73ef01eac7d48eb39c69ca253cf8 "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
test "$(git -C "$WORKSPACE/hybridclr" rev-parse HEAD)" = 4b2774b066cfc6afd77a8c8aded6bda7ea574f55
test "$(git -C "$WORKSPACE/hybridclr_unity" rev-parse HEAD)" = 948c0e3b4f8891481301770115e8ba4945eea6de
test "$(git -C "$WORKSPACE/il2cpp_plus" rev-parse HEAD)" = 1cf87f8209790f9fb2ebec97487dc1990ccd56c5
test "$(dotnet --version)" = 8.0.318
test -x "$UNITY" && test -x "$PYTHON" && test ! -e "$BATCH"

"$PYTHON" -B "$DEMO/Tools/AssemblyShadow/R03Completion/run_completion.py" \
  --workspace "$WORKSPACE" --output "$BATCH" --unity "$UNITY" --demo-commit "$DEMO_COMMIT"
```

Invoke once. Independent cells continue under the runner when permitted; dependent cells remain Blocked after a failed prerequisite. Do not manually retry a phase.

## Required complete scope

Retain the existing completion matrix unchanged:

- 90 cells;
- six fresh builds;
- 59 fresh Player processes;
- early 18-method Editor preflight;
- full 754 and 755 Editor rosters with exact names and zero skips/inconclusive;
- production-entry integration and restored-baseline compilation;
- all resource, measurement, startup, producer/rejection and custody evidence;
- complete ledger/result/index/archive/seal and final authority.

Additionally retain and authenticate:

- `compiler-policy-domains.json`;
- its bound `compiler-policy-domains/source-policy.json` and `linked-policy.json` files;
- baseline snapshot hash, project path, Unity version and target;
- live source-policy and linked-policy diagnostics;
- all three filtered-reference guard messages;
- P01–P05 eligibility/generation reports and restored-baseline zero-root/zero-closure receipt;
- codec owner/project/source bindings through every affected resource/startup call;
- linked DLL canonical lookup plus physical identity/hash/MVID evidence;
- complete image-record, methods and PDB evidence for measurement consumers.

Missing or unemitted evidence is `Unavailable`/`NotRun`, never inferred success.

## Permitted Local fixes

Only trivial, mechanically obvious environment or harness corrections that do not change architecture, acceptance semantics, guards, matrix scope, source pins or production behavior. Any non-trivial issue returns to Primary Implementation without source repair.

## Verdict and return

All 90 cells **and** the seal must Pass for `EvidenceReadyForPrimaryReview`. Any Failed or Blocked cell returns `ReturnRequired` with exact evidence and a concise `RETURN_TO_WEB.md` issue report.

Even if batch P is green:

- `R03Accepted=false`;
- `H2Passed=false`;
- `qualificationApproved=false`;
- `ReadyForHumanReviewGate=false`;
- PureInterpreter expansion remains disabled.

A green batch P returns to Primary for reconciliation and the required independent full-stage design → plan → implementation → evidence review. Do not start a later milestone or declare Human Review Gate approval.

After the single invocation, update Local-owned `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` factually, create an immutable batch-P checkpoint, commit/push only Local-owned evidence/docs, verify remote HEAD, and stop.
