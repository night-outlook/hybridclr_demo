# Primary Implementation → Local Validation: R03 completion batch M

## Objective and preserved history

Run **exactly one fresh batch M** for LL-001/LL-002: immutable compiler-policy inputs and the exact supplemental bootstrap entry, retaining full remaining-R03 scope. No non-trivial implementation is assigned to Local.

L remains ReturnRequired:43 Passed/1 Failed/46 Blocked,seal Passed. Four builds,23 focused Players,early18/full754/755 Editor rosters and source-pin/capability/fixed-image checks Passed. Compiler artifacts are Available but final policy Failed; two resource builds and36 downstream Players were Blocked. Preserve all history. Do not retry L or reuse its apps/root. M01 source-asset/GUID Editor Passed is not bundle/runtime acceptance.

## Read first

Relative to Docs/AssemblyShadow:
1. README.md and Plan/CURRENT_STATUS.md.
2. History/M07R/R03/O_COMPILER_POLICY_REPAIR.md,O_HOST_EVIDENCE.json,O_VALIDATION_MATRIX.md.
3. Unchanged Handoff/LOCAL_VALIDATION.md and RETURN_TO_WEB.md for L's empirical evidence.
4. History/M07R/R03/K_MEASUREMENT_PROTOCOL.md and Architecture/ADR/ADR-0002-pure-interpreter-qualification-boundary.md.
5. This file for the sole new execution assignment.

## Exact source and paths

All branches: `codex/assembly-shadow-r01b-h1`.

| Repository | Owning path | Exact source |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | Final docs-only transport containing this file, exactly matching Primary prompt/local/remote HEAD |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | c86cbf665f5fcb2137e5adf2960541ce492467a4 |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | 1cf87f8209790f9fb2ebec97487dc1990ccd56c5 |

Executable/CI anchor: `bb4bb31132ab1aaafa0a6c38cd3b5120142ff6b7`. All later demo changes must be under Docs/AssemblyShadow/**. Do not execute an arbitrary newer tip. A commit cannot embed its own hash; Primary supplies the exact transport SHA in the final prompt, independently checked before invocation.

## Prepared implementation

The fixture accounts for the entire tracked compiler-policy JSON input set and copies the original25-site raw-admission configuration unchanged. A single exact OnQuit/M06 entry is added; every other dependency declaration is unchanged. The original M07 compiler gate must succeed before the returned new snapshot is checked for captured25-site proof and16 actual positive/negative controls. No older snapshot fallback, synthetic success report or weakened production guard is allowed.

Pinned-Mono replay uses L's authenticated emitted DLLs as read-only inputs. It is not an upgrade of L's Failed policy, a new compiler snapshot or Editor/Player execution. Q22 now compares independently loaded analyses of the same prepared byte inputs, retaining exact report equality. Matching host/compiler evidence and limitations are in O_HOST_EVIDENCE.json.

## Environment and unused output

- Unity: /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity.
- Python: /Library/Frameworks/Python.framework/Versions/3.14/bin/python3.
- SDK-only DOTNET_ROOT: /Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk, version8.0.318. Do not launch Unity6000.
- New root: /Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261004M-policy.

Existing output, missing tools/input, wrong versions or dirty/wrong checkouts are blockers, not permission to substitute or delete evidence.

## Execute once

Fast-forward only. No reset/stash/forced checkout/unrelated merge, source edit, hash rebinding or policy adjustment. Confirm Primary's exact prompt SHA immediately before invocation.

```bash
set -euo pipefail
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
DEMO="$WORKSPACE/hybridclr_demo"
BATCH=/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261004M-policy
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
git -C "$DEMO" merge-base --is-ancestor bb4bb31132ab1aaafa0a6c38cd3b5120142ff6b7 "$DEMO_COMMIT"
git -C "$DEMO" diff --exit-code bb4bb31132ab1aaafa0a6c38cd3b5120142ff6b7 "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
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

Require DEMO_COMMIT to equal Primary's exact prompt SHA. Record outer argv/environment/PID/start/end/exit separately. Invoke once; do not bypass failures or manually retry phases. Independent cells continue under the runner; dependents remain Blocked.

## Scope and evidence

Retain **90 cells,six fresh builds,59 fresh Players,early18 Editor preflight and both754/755 zero-skip rosters**. Preserve all existing constructor/source-pin/capability/fixed-image/qualification/graph/runtime/rejection/warm/producer/C07/resource/P01–P05/restoration/measurement/M06/early-startup contracts. New LL checks run inside existing cells, not instead of old coverage.

Preserve the complete ledger/result/index/archive/seal, build/nativeBinding, Editor/Player, source/provenance, command/supervisor and final-authority evidence. Also retain:
- compilerPolicyInputs in resource-project.json and project authority;
- original raw admission/dependency/whitelist/reflection/resource configuration bytes;
- resource receiptRoot/compiler-policy-contract.json and compiler-policy-controls/R01–R08,B01–B08 JSON plus observation.json;
- batch-root compiler-policy-verification.json;
- exact new compiler snapshot, mode receipt, RawTypeAdmissions/configuration.json and compiled-evidence.json, all DLL/PDB/source hashes;
- qualification/Q22-deterministic-source-binding/determinism-first.json,determinism-second.json,determinism-inputs.json.

Require all25 current operation identities, successful original gate, captured proof,16 exact controls/codes and unchanged immutable inputs. Compile-only linkedProofExecuted/runtimeAcceptance/expansionAuthorized/R03Accepted/H2Passed remain false. Original later builds still require actual linked raw proof. Missing or unemitted records remain Unavailable, not empty success. Never select older evidence or manufacture a Passed report. Preserve contaminated controls' Failed unisolated certificates.

## Verdict and return

All90 cells and seal must Pass for EvidenceReadyForPrimaryReview; any Failed/Blocked cell returns ReturnRequired. R03Accepted=false;H2Passed=false;qualificationApproved=false;PureInterpreter expansion disabled. No performance SLA or gate approval follows.

After one invocation, factually update LOCAL_VALIDATION.md and RETURN_TO_WEB.md; add immutable History/M07R/R03/local-validation-<date>-batch-m-<result>/ evidence; preserve every earlier custody/result; commit/push only Local-owned demo reports/evidence and verify remote branch/HEAD; then stop. Do not change source, scope, raw hashes/modes, reflection entrypoints, guards, counters, lease/deadlines, package pins or earlier apps to force success. Primary owns non-trivial defects, full-stage reconciliation and independent review.
