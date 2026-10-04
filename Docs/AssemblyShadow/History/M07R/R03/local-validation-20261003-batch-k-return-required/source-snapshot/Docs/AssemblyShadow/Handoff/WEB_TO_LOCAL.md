# Primary Implementation → Local Validation: R03 completion batch K

## Objective and preserved history

Run **exactly one fresh batch K** for the complete resource dependency/capability reconciliation and actual target-inventory contract, retaining the full remaining-completion scope. Preserve all evidence and return to Primary. No non-trivial source implementation is assigned to Local.

J remains ReturnRequired: 43 Passed/1 Failed/46 Blocked, seal Passed. LI-001/LI-002 and J's M01 source-asset/GUID Editor contract Passed; resource/bundle/runtime evidence remains unavailable. Do not retry J, reuse its apps/root, relabel native installation as a build, or rewrite any historical evidence.

## Read first

Paths relative to `Docs/AssemblyShadow/`:
1. `README.md` and `Plan/CURRENT_STATUS.md`.
2. `History/M07R/R03/M_CAPABILITY_REPAIR.md`, `M_HOST_EVIDENCE.json`, `M_VALIDATION_MATRIX.md`.
3. Unchanged `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` for J's empirical return.
4. `History/M07R/R03/K_MEASUREMENT_PROTOCOL.md` and `Architecture/ADR/ADR-0002-pure-interpreter-qualification-boundary.md` for unchanged measurement and qualification limits.
5. This file for the only newly authorized execution.

## Exact source authority

Branch in all four repositories: `codex/assembly-shadow-r01b-h1`. Owning workspace: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`; owning repository directories use the names below.

| Repository | Exact source |
| --- | --- |
| night-outlook/hybridclr_demo | Final docs-only transport containing this file, matching Primary's exact final prompt and local/remote HEAD |
| night-outlook/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | `c86cbf665f5fcb2137e5adf2960541ce492467a4` |
| night-outlook/il2cpp_plus | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` |

Executable/CI anchor: `f00626dca8591496f2676b629104fd688bf06dce`. Every subsequent demo change must be under `Docs/AssemblyShadow/**`. Do not run an arbitrary newer tip. A commit cannot embed its own hash; the exact final transport SHA is supplied by Primary's prompt and independently checked against the pushed branch.

## Primary implementation under validation

The named resource profile audits all five inherited declarations, retaining exactly Newtonsoft.Json, Unity.Burst.Unsafe and nunit.framework as required fixed runtime plugins. Collections.ILSupport and VisualScripting.Antlr3 are explicitly out of this resource scope; unexpected presence is a failure. This is not dynamic filtering or an optional missing-plugin rule. Original M02/M07 behavior outside the owned synchronous scope and package/native guards remain unchanged.

The manifest pins the complete reviewed package closure, including J's observed XR subsystems1.0.0 module. Before the resource compiler snapshot, a supervised actual Unity invocation records both CompilationPipeline arrays, reference-byte hashes, complete production-derived inventory, full policy, all five dispositions, configured-input hashes and ten production-core controls. Independent verification reconstructs the inventory and checks exact guard codes. Configuration is explicit; the control phase must not mutate configured inputs. Compilation/host success does not substitute for this actual consumer run.

## Pinned environment and unused root

- Unity: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`.
- Python: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`.
- SDK-only root: `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`, version 8.0.318. Do not launch Unity6000.
- New root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261003K-capabilities`.

The root must not exist. Missing tools, wrong versions, dirty/wrong checkouts or an existing output are blockers, not permission to substitute or delete anything.

## Execute once

Fast-forward only. No reset, stash, forced checkout, unrelated merge, source edit or package-policy adjustment. Verify the exact Primary prompt SHA immediately before invocation.

```bash
set -euo pipefail
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
DEMO="$WORKSPACE/hybridclr_demo"
BATCH=/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261003K-capabilities
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
git -C "$DEMO" merge-base --is-ancestor f00626dca8591496f2676b629104fd688bf06dce "$DEMO_COMMIT"
git -C "$DEMO" diff --exit-code f00626dca8591496f2676b629104fd688bf06dce "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
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

Require DEMO_COMMIT to equal Primary's final prompt SHA. Record actual outer argv/environment/PID/start/end/exit separately without editing runner outputs. Invoke once. All 90 cells are predetermined; independent cells continue after unrelated failures and dependent cells remain Blocked.

## Required scope and evidence

Retain **90 cells, six fresh builds, 59 fresh Players, 18-method Editor preflight, both 754/755 full Editor rosters with zero skips**, original constructor/source-pin checks and all original runtime expectations. K adds the 20 actual-helper host profile tests and 10 actual policy/inventory controls inside existing prerequisites; they do not reduce any scope.

Preserve all existing ledger/result/index/archive/seal, source/qualification, nativeBinding/build, Editor, P01–P05/resource/production-entry/restoration, measurement/M06/early-startup, Player, command and final-authority evidence. Additionally retain:
- `capability-profile-host/results.json` and its binaries/source/command evidence;
- `resource-logs/capability-preflight.log` and the actual Unity/supervisor receipt;
- `<resource receiptRoot>/capability-contract.json` and all `capability-inputs/*.json` control files;
- `capability-contract-verification.json`;
- actual manifest/lock, both actual compiler arrays, all referenced DLL identities/hashes, derived inventory, full policy, five dispositions and configured-input/source hashes.

Require exactly the ten controls/codes in M_VALIDATION_MATRIX. Capture actual available Failed receipts and exceptions if a prerequisite fails; an unemitted array/snapshot is Unavailable, not an empty successful inventory. Do not fix the next missing name locally. Preserve contaminated controls' Failed unisolated warm certificates. M01's source-asset pass is not resource-runtime acceptance.

## Verdict, return and stop

All 90 cells and seal must Pass for EvidenceReadyForPrimaryReview. Any Failed/Blocked cell returns ReturnRequired. R03Accepted=false, H2Passed=false, qualificationApproved=false and PureInterpreter expansion disabled throughout. No production performance SLA is created.

After the one invocation, factually update LOCAL_VALIDATION.md and RETURN_TO_WEB.md; create an immutable `History/M07R/R03/local-validation-<date>-batch-k-<result>/` checkpoint; preserve all prior evidence/custody; commit/push only Local-owned demo reports/evidence and verify its remote branch/HEAD; then stop and return to Primary. No non-trivial source change, expectation/timeout/counter/lease adjustment, classification/ownership bypass, package substitution, scope change, old-app reuse, H2 or later milestone is authorized. Primary owns non-trivial findings, remaining stage obligations, reconciliation and independent full-stage review.
