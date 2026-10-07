# Primary Implementation → Local Validation: R03 completion batch Q

## Objective and preserved state

Run **exactly one fresh batch Q** to validate R03-LP-001 and R03-LP-002 together with all retained completion requirements. No non-trivial implementation is assigned to Local. Do not retry or reclassify P.

P remains ReturnRequired: **90 cells, 71 Passed / 18 Failed / 1 Blocked**; six builds and 18+754+755 Editor cases Passed with zero skips/inconclusive; all 59 Players executed, 42 verification Passed / 17 Failed. Its live-policy/restored-baseline subproofs and seal/custody Passed. Preserve P, O, N and all earlier evidence/result states unchanged.

## Read first

1. `Docs/AssemblyShadow/README.md`
2. `Docs/AssemblyShadow/Plan/CURRENT_STATUS.md`
3. Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`
4. `History/M07R/R03/LP_Repair_2026-10-06/PRIMARY_REVIEW.md`
5. `History/M07R/R03/LP_Repair_2026-10-06/EVIDENCE.json`
6. This complete assignment.

## Source and transport authority

All branches are `codex/assembly-shadow-r01b-h1`.

| Repository | Required Local checkout | Source/commit authority |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | Product/consumer anchor `b42cbe1134a56e675b8a98e275a45ae5a012e17d`; CI workspace/temp-path anchor `0a0974c95ad4eab2cfdaf9b9ff7e0609be67abf5`; execute the final Docs-only transport containing this handoff, whose exact 40-character SHA is supplied in Primary's final prompt |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` |

Both `Tools/AssemblyShadow/{R03,R03Completion}/source-pins.json` remain unchanged. Package/native/IL2CPP revisions, C# helpers, platform/profile, native build pins and original reference-build sources remain exactly those enforced by the runner. No package or installed native substitution is allowed. Changes between the product anchor and `0a0974c9...` are confined to the standalone LP CI workspace and canonical test-temp-path configuration; every later difference must be under `Docs/AssemblyShadow/**`.

Smoke branches `codex/connector-smoke-20261006-primary-r03` (prior four-repository smoke) and `codex/connector-smoke-20261006-lp-a21f` (new demo Git-data smoke) are disposable transport evidence, never product sources or merge targets. Connector branch deletion is unavailable.

## Implemented repairs and required fresh checks

**LP-001:** `resource-input-binding` now runs before `production-entry-integration`, and integration depends explicitly on that cell. A graph/layout failure blocks integration even if the failed action left a partial `resource_context`. The existing integration consumer and live-policy baseline-hash check are unchanged. Verify the actual ledger dependency/order, current ON snapshot binding, P01–P05 eligibility/generation, all three wrong-domain filtered-reference diagnostics, policy byte stability and fresh restored-baseline zero roots/closure. An integration failure must not block otherwise independent resource/measurement/startup checks whose own prerequisites passed.

**LP-002:** the existing `R02/type_resolution_schema.current_m07_schema` is scoped around all three Completion M07 entry points: per-resource case, aggregate suite and positive early-startup case. The bridge validates the exact current 33-field R02 extension, typed UInt64 range, version/profile/coverage and unchanged legacy semantics before in-memory projection. It restores the legacy callback on both success and error. Codec owner/project authority still passes explicitly. Neither the default legacy checker nor the bridge implementation changed.

Retain `typeInfoBridge` receipts: each of the 13 ON resource and four positive-startup checks must actually verify current type information (the current fixture has 17 objects each); aggregate M07 must recheck the 14 modes (221 ON objects in the current fixture). OFF must use the unchanged disabled contract with zero bridged objects. Six expected-rejection startup cases must not execute business resource verification and retain `typeInfoBridge=null`. Keep every original raw file/string/hash; do not edit JSON, remove `r02`, accept arbitrary unknown fields, or infer success from the bridge alone. New tests exercise every entry point and all these rejection/custody boundaries; historical P replay remains explicitly non-acceptance evidence.

## Environment, limits and unused root

- Unity: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, StandaloneOSX arm64.
- Python: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`.
- SDK-only DOTNET_ROOT: `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`, SDK `8.0.318`. Do not launch Unity 6000.
- New batch root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261006Q-lp-repair`.
- Separate publication/preflight root: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261006Q-lp-repair`.

Wrong/dirty checkout, mismatched origin/head/pin/tool, unavailable prerequisites or an existing output root are blockers. Do not remove evidence, reset/stash unrelated work, reuse apps or alter timeouts, warm-up, leases, cleanup semantics or evidence guards. The Primary host environment did not inspect these Mac working trees; Local must perform and retain its own clean-tree/source checks.

## Execute once

Set `EXPECTED_DEMO_COMMIT` to the **exact final published demo SHA in Primary's handoff prompt**, not the product anchor, a smoke commit or an inferred latest HEAD. Verify canonical origins without logging embedded credentials. Fast-forward only. The following block does not retry any phase:

```bash
set -euo pipefail
: "${EXPECTED_DEMO_COMMIT:?Set the exact 40-character demo transport SHA from the Primary handoff}"
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
DEMO="$WORKSPACE/hybridclr_demo"
BATCH=/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261006Q-lp-repair
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
PYTHON=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
export DOTNET_ROOT=/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk
export PATH="$DOTNET_ROOT:$PATH"
export DOTNET_MULTILEVEL_LOOKUP=0 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp
[[ "$EXPECTED_DEMO_COMMIT" =~ ^[0-9a-f]{40}$ ]]
for REPO in hybridclr_demo hybridclr hybridclr_unity il2cpp_plus; do
  DIR="$WORKSPACE/$REPO"
  test -z "$(git -C "$DIR" status --porcelain=v1 --untracked-files=all)"
  test "$(git -C "$DIR" branch --show-current)" = "$BRANCH"
  ORIGIN="$(git -C "$DIR" remote get-url origin)"
  case "$ORIGIN" in
    "https://github.com/night-outlook/$REPO"|"https://github.com/night-outlook/$REPO.git"|"git@github.com:night-outlook/$REPO.git"|"ssh://git@github.com/night-outlook/$REPO.git") ;;
    *) echo "Unexpected origin for $REPO" >&2; exit 1 ;;
  esac
  case "$REPO" in
    hybridclr_demo) EXPECTED="$EXPECTED_DEMO_COMMIT" ;;
    hybridclr) EXPECTED=4b2774b066cfc6afd77a8c8aded6bda7ea574f55 ;;
    hybridclr_unity) EXPECTED=948c0e3b4f8891481301770115e8ba4945eea6de ;;
    il2cpp_plus) EXPECTED=1cf87f8209790f9fb2ebec97487dc1990ccd56c5 ;;
  esac
  test "$(git -C "$DIR" ls-remote origin "refs/heads/$BRANCH" | awk '{print $1}')" = "$EXPECTED"
  git -C "$DIR" fetch origin "$BRANCH"
  test "$(git -C "$DIR" rev-parse FETCH_HEAD)" = "$EXPECTED"
  git -C "$DIR" merge --ff-only FETCH_HEAD
  test "$(git -C "$DIR" rev-parse HEAD)" = "$EXPECTED"
  test -z "$(git -C "$DIR" status --porcelain=v1 --untracked-files=all)"
done
git -C "$DEMO" merge-base --is-ancestor 0a0974c95ad4eab2cfdaf9b9ff7e0609be67abf5 "$EXPECTED_DEMO_COMMIT"
git -C "$DEMO" diff --exit-code 0a0974c95ad4eab2cfdaf9b9ff7e0609be67abf5 "$EXPECTED_DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
test "$(dotnet --version)" = 8.0.318
test -x "$UNITY" && test -x "$PYTHON" && test ! -e "$BATCH"
"$PYTHON" -B "$DEMO/Tools/AssemblyShadow/R03Completion/run_completion.py" \
  --workspace "$WORKSPACE" --output "$BATCH" --unity "$UNITY" --demo-commit "$EXPECTED_DEMO_COMMIT"
```

## Evidence, verdict and stopping point

Retain **all 90 cells, six fresh builds, 59 fresh Players, the 18-method Editor preflight and both 754/755 exact zero-skip/inconclusive rosters**. Only binding/integration order and its explicit dependency changed; no coverage was removed. Retain all prior measurement, producer, rejection, resource, startup and current-source checks and the complete ledger/result/index/archive/seal/final-authority records. The four contaminated unisolated warm certificates remain Failed and are not repaired by attribution. Missing evidence remains Unavailable/NotRun; blocked prerequisites remain Blocked.

In addition retain the binding and integration cell receipts, original policy reports/bytes/three guards, restored compile and zero-root/closure receipt, each `typeInfoBridge`, raw JSON hashes before/after verification, codec authority and full resource aggregate output. On failure include exact Python traceback, failed cell/dependencies, raw/result/command paths and hashes, tool argv/exit/PID and all independently passing subproofs without promoting the cell verdict.

Only mechanically obvious local environment/harness corrections with independent verification and no source/design/pin/guard/scope/acceptance change are permitted. Do not repair non-trivial issues, edit the schema bridge, manually retry phases, reduce scope or rebind evidence. Return them to Primary.

All 90 cells and the seal must Pass for `EvidenceReadyForPrimaryReview`; otherwise return `ReturnRequired`. Even when green, `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, PureInterpreter expansion disabled and full independent stage review pending. No performance SLA, deferred R02 CPU or H1 RSS acceptance is granted.

After the one invocation, update only Local-owned `LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md` and an immutable `History/M07R/R03/local-validation-20261006-batch-q-...` checkpoint with factual provenance. Commit/push, verify all final heads and cleanliness, then return to Primary and stop. Do not enter the next milestone or declare human approval.
