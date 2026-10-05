# Primary Implementation → Local Validation: R03 completion batch N

## Objective and preserved history

Run **exactly one fresh batch N** for R03-LM-001: authenticated linked-baseline/compiler-target type identity, retaining full remaining-R03 scope. No non-trivial implementation is assigned to Local.

M remains ReturnRequired:48 Passed/1 Failed/41 Blocked,90 cells,seal Passed. Six builds,23 focused Players,early18/full754/755 Editor rosters,current25-site compiler proof/16 controls and both linked proofs Passed. P05 atomic fixture construction Failed;36 downstream Players did not run. Exact scoped settings restoration Passed. Preserve all history. Do not retry M or reuse its root/apps. M01 source-asset/GUID Editor Passed is not complete bundle/runtime acceptance.

## Read first

Relative to Docs/AssemblyShadow:
1. README.md and Plan/CURRENT_STATUS.md.
2. History/M07R/R03/P_LAYOUT_IDENTITY_REPAIR.md,P_HOST_EVIDENCE.json,P_VALIDATION_MATRIX.md.
3. Unchanged Handoff/LOCAL_VALIDATION.md and RETURN_TO_WEB.md for M's empirical return.
4. History/M07R/R03/K_MEASUREMENT_PROTOCOL.md and Architecture/ADR/ADR-0002-pure-interpreter-qualification-boundary.md.
5. This file for the sole new execution assignment.

## Exact source and paths

All branches: `codex/assembly-shadow-r01b-h1`.

| Repository | Owning path | Exact source |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | Final docs-only transport containing this file, exactly matching Primary's final prompt and local/remote HEAD |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | ef6c70f30248c4b7c41e9e85d81e08f5709dc4ba |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | 1cf87f8209790f9fb2ebec97487dc1990ccd56c5 |

Executable/CI anchor: `7e1060ff5723efe365c60bc052bbbcb117d62dfa`. All later demo changes must be under Docs/AssemblyShadow/**. The managed package pin changes for this batch; both R03/source-pins.json and R03Completion/source-pins.json agree. Do not execute an arbitrary newer tip. Primary supplies the final transport SHA in the prompt because a commit cannot embed its own hash.

## Prepared implementation

The production native-layout screen constructs private metadata identity domains from reread/reverified complete linked and compiler inventories. Actual captured runtime forwarders plus verified target-framework bytes resolve the reference boundary without qualifier stripping, ambient resolution or same-name aliases. Conservative parent/interface/field/layout checks and native allocation/offset revalidation remain required. Schema-2 sidecars record exact source hashes, image identities/MVIDs and declaration-to-definition paths.

The 33 host identity cases include actual authenticated M input replay and adversarial real-DLL controls. Historical replay is not a new compiler snapshot or runtime result. After new fixture finalization, the existing resource-input-binding cell verifies all five fresh P01-P05 sidecars and nonzero P05 forwarding coverage. No cell, build, Player or existing expectation is removed. Matching host and pinned-Unity compiler/Mono checks Passed; actual N integration remains pending.

## Environment and unused output

- Unity: /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity.
- Python: /Library/Frameworks/Python.framework/Versions/3.14/bin/python3.
- SDK-only DOTNET_ROOT: /Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk, version8.0.318. Do not launch Unity6000.
- New root: /Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261005N-identity.

Existing output, missing tool/input, wrong versions or dirty/wrong checkouts are blockers, not permission to substitute or delete evidence. The committed replay may read only its exact pinned historical M input paths; no earlier app, cache or arbitrary snapshot selection is permitted.

## Execute once

Fast-forward only. No reset/stash/forced checkout/unrelated merge, source edit, hash rebinding, facade substitution or guard adjustment. Confirm Primary's exact prompt SHA immediately before invocation.

```bash
set -euo pipefail
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
DEMO="$WORKSPACE/hybridclr_demo"
BATCH=/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261005N-identity
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
git -C "$DEMO" merge-base --is-ancestor 7e1060ff5723efe365c60bc052bbbcb117d62dfa "$DEMO_COMMIT"
git -C "$DEMO" diff --exit-code 7e1060ff5723efe365c60bc052bbbcb117d62dfa "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
test "$(git -C "$WORKSPACE/hybridclr" rev-parse HEAD)" = 4b2774b066cfc6afd77a8c8aded6bda7ea574f55
test "$(git -C "$WORKSPACE/hybridclr_unity" rev-parse HEAD)" = ef6c70f30248c4b7c41e9e85d81e08f5709dc4ba
test "$(git -C "$WORKSPACE/il2cpp_plus" rev-parse HEAD)" = 1cf87f8209790f9fb2ebec97487dc1990ccd56c5
test "$(dotnet --version)" = 8.0.318
test -x "$UNITY"
test -x "$PYTHON"
test ! -e "$BATCH"
"$PYTHON" -B "$DEMO/Tools/AssemblyShadow/R03Completion/run_completion.py" \
  --workspace "$WORKSPACE" --output "$BATCH" \
  --unity "$UNITY" --demo-commit "$DEMO_COMMIT"
```

Require DEMO_COMMIT to equal Primary's exact final prompt SHA. Record outer argv/environment/PID/start/end/exit separately. Invoke once; do not bypass failures or manually retry phases. Independent cells continue under the runner; dependent cells remain Blocked.

## Scope and evidence

Retain **90 cells,six fresh builds,59 fresh Players,early18 Editor preflight and both754/755 zero-skip rosters**. Preserve all constructor/source-pin/capability/fixed-image/qualification/graph/compiler-policy/linked/runtime/rejection/warm/producer/C07/resource/P01-P05/restoration/measurement/M06/early-startup contracts.

Preserve the complete ledger/result/index/archive/seal, build/nativeBinding, Editor/Player, immutable source/provenance, command/supervisor and final-authority evidence. Also retain:
- layout-identity-inputs.json and layout-identity/results.json/comparison.json, plus synthetic DLL hashes and exact historical input bindings;
- actual current baseline/target snapshot receipts, complete linked/compiler inventories and captured retargeting proof/runtime facade;
- all five current P01-P05 native-layout-admission-v1.json files (schema2), with identityEvidence;
- layout-identity-verification.json, exact fixture graph/load orders, successful current P05 manifest/finalization and independent settings-restoration receipts.

Require complete identities/hashes/MVIDs, exact proof and framework provenance, actual forwarding paths and nonzero P05 mapping coverage. nativeProofExecuted=false,runtimeMustRevalidate=true,allocationProofStillRequired=true and expansion disabled remain mandatory in nominal reports. Linked/native offset and allocation proof must still execute through the original later paths. Missing/unemitted reports remain Unavailable; never fabricate a Passed sidecar or select older evidence. Preserve all four contaminated producer controls' Failed unisolated warm certificates.

## Verdict and return

All90 cells and seal must Pass for EvidenceReadyForPrimaryReview; any Failed/Blocked cell returns ReturnRequired. R03Accepted=false;H2Passed=false;qualificationApproved=false;PureInterpreter expansion disabled. No production performance SLA or Human Review Gate approval follows.

After one invocation, factually update LOCAL_VALIDATION.md and RETURN_TO_WEB.md; add immutable History/M07R/R03/local-validation-<date>-batch-n-<result>/ evidence; preserve every earlier custody/result; commit/push only Local-owned demo reports/evidence and verify remote repository/branch/HEAD; then stop. No non-trivial Local source change, forwarding/qualifier relaxation, same-name alias, guard bypass, counter/lease/deadline adjustment, package substitution or old-app reuse is authorized. Primary owns remaining defects, full-stage reconciliation and independent review.
