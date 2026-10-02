# Primary Implementation → Local Validation: R03 batch E, provenance and Editor scope

## Objective and preserved return

Run exactly one new **36-cell batch E** after R03-LD-001/002. Do not retry A/B/C/D, change their evidence, redesign R03, enable PureInterpreter expansion or enter H2.

Authoritative Local return: `33d7b1fce2f3b8463dc4ac78061250ecc7df925d`. D remains **ReturnRequired: 12 Passed / 5 Failed / 19 Blocked**, focused seal Passed. It produced four successful native artifact receipts and ARM64 apps, but all four build cells failed provenance verification. Actual Editor execution had 754 Passed and one Ignored; the frozen M01 resource case remains NoCoverage. All nineteen Players were Blocked. Primary does not retroactively promote any of these cells.

## Read first

All relative documentation paths below are under `Docs/AssemblyShadow/`:
1. `README.md` and `Plan/CURRENT_STATUS.md`.
2. `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` for preserved D facts, not old execution commands.
3. `History/M07R/R03/F_PROVENANCE_SCOPE_REPAIR.md`, `F_HOST_EVIDENCE.json`, `F_VALIDATION_MATRIX.md`.
4. `History/M07R/R03/A_PRIMARY_IMPLEMENTATION.md` and `Plan/stages/R03-evolution-semantics.md` for unchanged product scope and full-stage exits.
5. This live handoff for the only authorized next execution.

## Exact source authority

All four repositories use `codex/assembly-shadow-r01b-h1`.

| Repository | Exact owning checkout | Revision |
| --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Final docs-only transport SHA supplied in Primary's prompt, resolved and checked below |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `041c0cbb42d3e64e54fe605673d99799b5d63893` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `120bb01be680cec0375002a0823552d66d34b84c` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `1abb6bcaa85226f08c67f9da65edb3c58e8cb399` |

New tested source anchor: **`979abd80b673e690c5f82819ed194200f8d2e536`**. Only `Docs/AssemblyShadow/` documentation/evidence may differ after it. Earlier anchors and historical A–E preparation records do not authorize this run. Execute exactly the final pushed transport SHA in Primary's prompt, not the anchor, a smoke commit, an old executed commit or arbitrary later HEAD. A receiver without chat context resolves the latest commit touching this `WEB_TO_LOCAL.md` and requires it to equal local and current remote HEAD; the runner rechecks all four authorities at entry and completion.

Native/package sources, reference-core/package pins, nineteen Player expectations, four build roles, count/error guards, lifetime enforcement, command deadlines and top-level dependencies are unchanged.

## Implemented correction and acceptance boundary

`R03Build.cs` emits build receipt schema **2** and the exact `installedNativeRoot` used by the producer. `build_provenance.py` independently checks the pinned OSXEditor root profile inside the selected batch/role, canonical nonlinked paths, install receipt/hash, exact native inventory, four-source tuple, unchanged non-generated sources and additive diagnostic probe. It does not search recursively, select a first matching hash or delete generation copies. Old v1 receipts are not upgraded or reused.

`editor_scope.py` defines the isolated-project scope before launching tests. It excludes exactly the unavailable frozen M01 asset test via an anchored negative full-name filter, retains all **754** other cases, and requires every selected case and aggregate to be Passed with zero skips. Exact 35 R03 IDs and the true-cycle test remain mandatory. The D XML is a hash-pinned name catalog only, never fresh evidence. `editor-scope.json` and `editor-verification.json` explicitly retain the excluded case as **NoCoverage** and `fullLegacyRegressionAcceptance=false`. No broad skipped-result allowance or category-wide exclusion exists.

Primary's host and pinned-API results are in F_HOST_EVIDENCE.json. They are not new integrated Unity, native-installation or Player acceptance. The next run must produce actual v2 receipts and the actual filtered Editor result.

## Environment and unused root

- Unity `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`; StandaloneOSX, arm64.
- Python `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`.
- Direct managed SDK `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`, version **8.0.318**, used as SDK only. Do not launch Unity 6000.
- New prescribed root `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001E-provenance`.

Verify recorded tools and versions. Missing/mismatched tooling is Blocked, not permission to substitute versions. Verify the new root does not exist; do not delete/reuse a root to bypass that guard. Preserve all D/A/B/C and R02/H1 evidence, including D's original live archive and published byte parts.

## Run once

First verify all canonical origins and clean owning checkouts. Fast-forward only; no reset, stash, forced checkout, unrelated merge or source changes.

```bash
set -euo pipefail
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
DEMO="$WORKSPACE/hybridclr_demo"
BATCH=/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001E-provenance
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
git -C "$DEMO" merge-base --is-ancestor 979abd80b673e690c5f82819ed194200f8d2e536 "$DEMO_COMMIT"
git -C "$DEMO" diff --exit-code 979abd80b673e690c5f82819ed194200f8d2e536 "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
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

Before invocation, also require DEMO_COMMIT to match Primary's final prompt. Capture the actual command, environment, PID, timestamps and exit without altering the runner's outputs. Invoke once; independent cells are already scheduled. A failed preflight is Blocked, not a fabricated 36-cell execution. Never manually launch blocked cases or retry the batch.

## Required evidence and return

Retain all **36 cells / four new build roles / nineteen fresh-process Player cases**, plus all existing fixture, compiler, lifecycle and complete-helper prerequisites. The verifier cell now runs 116 tests. Actual Editor execution must include exactly the 754 selected identities with zero skips. The missing M01 asset case remains excluded/NoCoverage and is not counted as Passed.

Preserve the result, ledger, index, archive, seal, all command streams, host/fixture/compiler outputs, supervised completion receipts, build configs/receipts/apps, Editor XML and Player evidence. Additionally preserve `editor-scope.json`, `editor-verification.json` and build cells' `nativeBinding` records; each new build receipt must contain `schemaVersion=2` and `installedNativeRoot`. Canonical SDK directories and copied generation receipts remain intact. Do not rewrite pre-cleanup observations or infer runtime success from artifact existence.

All 36 cells and the focused seal must pass for `EvidenceReadyForPrimaryReview`; otherwise return `ReturnRequired`. `R03Accepted=false`, `H2Passed=false`, `pureInterpreterExpansionEnabled=false` and `fullLegacyRegressionAcceptance=false` remain mandatory even on a successful focused batch.

Local updates `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` factually, preserves D as historical, and creates an immutable `History/M07R/R03/local-validation-<date>-batch-e-<result>/` checkpoint. Commit/push only Local-owned demo reports/evidence and stop. For large archives, reuse D's exact-byte transport convention: preserve the live original, bind ordered parts to its original hash, authenticate reconstruction and keep transport metadata separate from the runner seal. No re-compression or replacement of raw evidence.

No non-trivial implementation is delegated. Changes to source, installation-root profile, schema, test catalog/filter, expectations, fixture assets, pins, deadlines or lifecycle policy require Primary. Do not waive skipped or missing tests, globally kill compiler servers or alter failed receipts. Actual M01 resource coverage, full R03 regressions, broader method/generic/stack-trace work, performance/memory/capacity and PureInterpreter qualification remain Primary-owned before full stage review and H2.
