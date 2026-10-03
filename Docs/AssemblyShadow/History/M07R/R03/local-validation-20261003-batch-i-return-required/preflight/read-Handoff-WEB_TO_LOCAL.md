# Primary Implementation → Local Validation: R03 batch I, remaining-completion integration

## Objective

Run exactly one fresh source-bound **R03 batch I** that combines the retained conservative H regressions with static qualification, original-resource M01/P01–P05 coverage, available broader runtime witnesses, production graph/generation integration, current-source observations and early-startup regressions. Preserve all evidence and return to Primary.

This is not R03/H2 acceptance and does not authorize PureInterpreter structural expansion.

## Read first

Paths are relative to `Docs/AssemblyShadow/`:

1. `README.md` and `Plan/CURRENT_STATUS.md`.
2. `Architecture/ADR/ADR-0002-pure-interpreter-qualification-boundary.md`.
3. `History/M07R/R03/K_COMPLETION_PREP.md`, `K_VALIDATION_MATRIX.md`, `K_MEASUREMENT_PROTOCOL.md`, `K_HOST_EVIDENCE.json`.
4. `History/M07R/R03/J_H_FOCUSED_RECONCILIATION.md` for the immutable earlier focused result.
5. `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` for historical Local facts; do not execute their retired commands.
6. This file for the only newly authorized execution.

## Exact source authority

All repositories use branch `codex/assembly-shadow-r01b-h1` and owning paths beneath `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`.

| Repository | Exact validation authority |
| --- | --- |
| `night-outlook/hybridclr_demo` | final pushed docs-only transport commit containing this file; must equal the exact SHA in Primary's prompt and local/remote HEAD |
| `night-outlook/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `11a20efadd8f1ebc494d02ac80135e224dabd3e5` |
| `night-outlook/il2cpp_plus` | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` |

Executable/tool source anchor: `55d43dd828d96647298b91ed6d8da122523f8a87`. The final demo handoff may differ from this anchor only under `Docs/AssemblyShadow/**`. Verify that delta before execution. Never run an arbitrary later tip.

The completion source's `source-pins.json` binds the three non-demo revisions above and retains `runtimeAcceptance=false` / `expansionAuthorized=false`. The runner replaces only the demo transport identity with the exact final published SHA.

## What Primary implemented

- byte-bound, non-authorizing `R03PureInterpreterEligibilityV1`; V1 physical admission remains authoritative and structural expansion stays disabled;
- exact copied original-resource project using the tracked M01 prefab/data/scene/meta identities and original production M07/P05 paths;
- separate 754-case focused and 755-case resource-complete Editor scopes, both requiring zero skips;
- source-bound P01–P05 production changed-root/closure/load/generation checks and return-to-installation-baseline comparison;
- supplementary existing M06 static/delegate/exception observations in the same fresh R00 processes, outside the original timing interval;
- unfenced current-source R00 observation protocol and existing early-startup/capability checks;
- deterministic 90-cell orchestration, exact-source/provenance checking, process-lifetime rules, restoration logic and evidence seal.

Primary host/compiler checks passed on exact anchor `55d43dd...`; see `K_HOST_EVIDENCE.json`. They are not Unity/Player acceptance.

## Pinned environment and unused output

- workspace: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`
- Unity: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`
- Python: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`
- SDK-only root: `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`, version **8.0.318**; do not launch Unity 6000
- new batch root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261003I-completion`

The output root must not exist. Do not delete/reuse a previous root to make the batch proceed.

## Execute once

Fast-forward only. No reset/stash/forced checkout/unrelated merge or source edit.

```bash
set -euo pipefail
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
DEMO="$WORKSPACE/hybridclr_demo"
BATCH=/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261003I-completion
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
git -C "$DEMO" merge-base --is-ancestor 55d43dd828d96647298b91ed6d8da122523f8a87 "$DEMO_COMMIT"
git -C "$DEMO" diff --exit-code 55d43dd828d96647298b91ed6d8da122523f8a87 "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
test "$(git -C "$WORKSPACE/hybridclr" rev-parse HEAD)" = 4b2774b066cfc6afd77a8c8aded6bda7ea574f55
test "$(git -C "$WORKSPACE/hybridclr_unity" rev-parse HEAD)" = 11a20efadd8f1ebc494d02ac80135e224dabd3e5
test "$(git -C "$WORKSPACE/il2cpp_plus" rev-parse HEAD)" = 1cf87f8209790f9fb2ebec97487dc1990ccd56c5
test "$(dotnet --version)" = 8.0.318
test -x "$UNITY"
test ! -e "$BATCH"

"$PYTHON" -B "$DEMO/Tools/AssemblyShadow/R03Completion/run_completion.py" \
  --workspace "$WORKSPACE" --output "$BATCH" \
  --unity "$UNITY" --demo-commit "$DEMO_COMMIT"
```

Immediately before invocation require `DEMO_COMMIT` to equal the exact demo SHA in Primary's final prompt. Capture the outer argv/environment/PID/timestamps/exit without altering runner outputs. Invoke once.

## Required batch-I evidence

The predetermined ledger is exactly **90 unique cells**. Retain all raw evidence for:

- six fresh native builds and their installed/native binding receipts;
- 754-case focused Editor XML and 755-case resource-complete Editor XML, both zero-skip;
- **59 fresh Player processes**: 23 focused, 14 original M07 resource, 12 R00 observation, 10 early-startup;
- qualification/results.json and exact byte/reference/resource/closure bindings;
- original M01/P01–P05 source/resource/bundle/manifest receipts and structural restoration evidence;
- production-entry integration and return-to-baseline results;
- M06 supplement receipts and selected physical DLL/PDB identities;
- R00 raw observations and `measurements.json` without inventing a release threshold;
- all command receipts/streams, cell receipts, result/ledger/index/archive/seal and final authority.

`K_VALIDATION_MATRIX.md` and the runner are the normative batch-I scope. Independent cells continue after unrelated failures; dependent cells become Blocked.

## Pass/failure interpretation

All 90 cells plus the evidence seal must pass for `EvidenceReadyForPrimaryReview`. Even then:

- `R03Accepted=false`;
- `H2Passed=false`;
- `qualificationApproved=false`;
- `pureInterpreterExpansionEnabled=false`;
- no release performance SLA is approved;
- historical H M01 NoCoverage and all A–H historical outcomes remain unchanged.

Any Failed/Blocked cell returns `ReturnRequired`. Do not retry in the same root, reuse A–H apps, loosen scope/counters/rosters, change timing criteria, authorize structural expansion, or make a non-trivial source fix locally.

## Local return and stop

After the one run:

1. factually update `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`;
2. add an immutable `History/M07R/R03/local-validation-<date>-batch-i-<result>/` checkpoint with source/environment/result/seal and bounded evidence transport;
3. preserve all historical reports/evidence exactly;
4. commit/push only Local-owned demo reports/evidence and verify final repository/branch/HEAD;
5. stop and return control to Primary.

No later milestone or Human Review Gate is authorized by this batch. Primary will reconcile I, close any remaining R03 exit-matrix items, conduct the independent R03 stage review, and only then may stop for user-initiated H2.
