# Primary Implementation → Local Validation: R03 completion batch L

## Objective and preserved history

Run **exactly one fresh batch L** to verify authoritative fixed-image provisioning before reflection-enabled resource compilation, retaining the complete remaining-R03 validation scope. No non-trivial implementation is assigned to Local.

K remains ReturnRequired: 43 Passed / 1 Failed / 46 Blocked; seal Passed. Its four builds, 23 focused Players, 18-method preflight, full 754/755 zero-skip Editor rosters and all source-pin/target-inventory controls Passed. Its resource compiler failed; two resource builds and 36 downstream Players were Blocked. Preserve these states and every prior checkpoint. Do not retry K or reuse its root/apps. M01 source-asset/GUID Editor Passed is distinct from unavailable bundle/runtime acceptance.

## Read first

Paths relative to `Docs/AssemblyShadow/`:
1. `README.md` and `Plan/CURRENT_STATUS.md`.
2. `History/M07R/R03/N_FIXED_IMAGE_REPAIR.md`, `N_HOST_EVIDENCE.json`, `N_VALIDATION_MATRIX.md`.
3. Unchanged `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` for K's actual evidence and uncertainty.
4. `History/M07R/R03/K_MEASUREMENT_PROTOCOL.md` and `Architecture/ADR/ADR-0002-pure-interpreter-qualification-boundary.md` for unchanged qualification/measurement limits.
5. This file for the only newly authorized execution.

## Exact source and owning paths

Branch in all repositories: `codex/assembly-shadow-r01b-h1`.

| Repository | Owning path | Exact source |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | Final documentation-only transport containing this file; must equal Primary's final prompt and local/remote HEAD |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | `c86cbf665f5fcb2137e5adf2960541ce492467a4` |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` |

Executable/CI anchor: `78ce9f81968a330b2801a93d4a426ffab7565b5f`. Every subsequent demo change must be under `Docs/AssemblyShadow/**`. Do not run an arbitrary newer tip. A commit cannot embed its own hash; Primary supplies the exact final transport SHA in the copyable prompt and Local verifies it before execution. Package/native pins and the original runtime test expectations are unchanged.

## Implementation prepared

The resource fixture now requires the existing R02 frozen-image source blobs and authenticates their exact original archive/member before provisioning. It materializes the exact 4,608-byte image, SHA-256 `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`, through the existing exclusive receipt-bound materializer before any resource-project Unity invocation. It never copies the ignored owning image or selects a cache/ancestor/earlier app. Both fixed-image sites and the full six-site configuration are unchanged.

An actual Unity preflight invokes production project-image validation and ten guard controls before resource compilation. It requires unchanged input hashes, exact provider/MVID, both original mode selections, pinned semantic identity and false authorization flags. Current target-provider semantics and successful reflection ILPP remain required by the original subsequent compiler snapshot; the preflight cannot replace them.

Matching host/compiler CI Passed, including original-archive authentication, 148/183 Python suites, ten image controls and pinned Unity Mono semantic verification. These are not new Unity Editor or Player execution. N_FIXED_IMAGE_REPAIR contains the full changed-file inventory and rollback boundary.

## Pinned environment and unused root

- Unity: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`.
- Python: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`.
- SDK-only root: `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`, version 8.0.318. Do not launch Unity6000.
- New root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261004L-fixed-image`.

The root must not exist. Missing archive, fixture, tools, wrong versions, dirty/wrong checkout or an existing root is a blocker, not permission to substitute inputs or delete evidence. Historical archive authentication may read only its one pinned source; no cache search is authorized.

## Execute once

Fast-forward only. No reset/stash/forced checkout/unrelated merge, source edit or hash rebinding. Confirm the exact prompt SHA before invocation.

```bash
set -euo pipefail
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
DEMO="$WORKSPACE/hybridclr_demo"
BATCH=/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261004L-fixed-image
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
git -C "$DEMO" merge-base --is-ancestor 78ce9f81968a330b2801a93d4a426ffab7565b5f "$DEMO_COMMIT"
git -C "$DEMO" diff --exit-code 78ce9f81968a330b2801a93d4a426ffab7565b5f "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
test "$(git -C "$WORKSPACE/hybridclr" rev-parse HEAD)" = 4b2774b066cfc6afd77a8c8aded6bda7ea574f55
test "$(git -C "$WORKSPACE/hybridclr_unity" rev-parse HEAD)" = c86cbf665f5fcb2137e5adf2960541ce492467a4
test "$(git -C "$WORKSPACE/il2cpp_plus" rev-parse HEAD)" = 1cf87f8209790f9fb2ebec97487dc1990ccd56c5
test "$(dotnet --version)" = 8.0.318
test -x "$UNITY"
test -x "$PYTHON"
test ! -e "$BATCH"

"$PYTHON" -B "$DEMO/Tools/AssemblyShadow/R03Completion/run_completion.py" \
  --workspace "$WORKSPACE" --output "$BATCH" \
  --unity "$UNITY" --demo-commit "$DEMO_COMMIT"
```

Immediately before invocation require DEMO_COMMIT to equal Primary's exact final prompt SHA. Preserve actual outer argv/environment/PID/start/end/exit separately. Invoke once. Do not bypass a failed preflight or retry any phase by hand; independent cells continue under the runner and dependent cells remain Blocked.

## Required scope and evidence

Retain **all 90 cells, six fresh builds, 59 fresh Players, early 18-method Editor preflight and both 754/755 zero-skip rosters**. Retain all constructor, source-pin, capability, qualification, runtime, graph, resource, P01–P05, restoration, measurement/M06 and early-startup expectations. Added origin/materialization and ten actual fixed-image controls run within existing cells, not in place of any old coverage.

In addition to the full original ledger/result/index/archive/seal, build/nativeBinding, source/Editor/Player and command evidence, preserve:
- `fixed-image-origin/search.json` and extracted `frozen-m00.dll`;
- `fixed-image-host/results.json`, semantic diagnostics, control configs/images and source/binary/command evidence;
- resource `_temp/AssemblyShadow/R03CompletionFixedImage/preparation.json` and `materialized.dll.bytes`;
- exact provisioned M00 image, compact fixture/origin and six-site reflection configuration;
- `resource-logs/fixed-image-preflight.log` and actual owned Unity/supervisor receipt;
- `<resource receiptRoot>/fixed-image-contract.json` and all `fixed-image-controls/` files;
- `fixed-image-contract-verification.json`;
- actual compiler/snapshot and ReflectionBindings image/provider-mode evidence, or exact Failed/Unavailable records when not emitted.

No input materialization is a new compiler build or historical Player-result reuse. Do not promote preflight Passed to snapshot/resource runtime acceptance. Preserve the four contaminated controls' Failed unisolated warm certificates. Do not claim missing snapshot data is an empty successful inventory.

## Verdict, ownership and stop

All 90 cells and seal must Pass for EvidenceReadyForPrimaryReview; any Failed/Blocked cell returns ReturnRequired. R03Accepted=false; H2Passed=false; qualificationApproved=false; PureInterpreter expansion disabled. No production performance SLA or Human Review Gate approval follows.

After one invocation, update LOCAL_VALIDATION.md and RETURN_TO_WEB.md factually; add an immutable `History/M07R/R03/local-validation-<date>-batch-l-<result>/` checkpoint; preserve every earlier evidence/custody state; commit/push only Local-owned demo reports/evidence and verify repository/branch/HEAD; then stop. No non-trivial Local source changes, pinned-hash edits, reflection-site removal, ILPP disabling, expectation/counter/lease/deadline relaxation, package substitution, old-app reuse or later-milestone work is authorized. Primary owns any remaining defect, full-stage reconciliation and independent review.
