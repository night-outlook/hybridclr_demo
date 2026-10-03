# Primary Implementation → Local Validation: R03 completion batch J

## Objective and history

Run **exactly one fresh batch J** to validate LI-001's fixture-constructor repair and LI-002's complete platform/source-pin contract, while retaining the full remaining-completion scope. Preserve evidence and return to Primary. No non-trivial source implementation is assigned to Local.

Batch I remains ReturnRequired: 40 Passed / 2 Failed / 48 Blocked; seal Passed. Do not retry I, reuse its root/apps, or change its reports/checkpoint. M01 remains NoCoverage in the historical isolated runs. R03, H2 and structural expansion remain unapproved.

## Read first

Paths relative to `Docs/AssemblyShadow/`:

1. `README.md`, `Plan/CURRENT_STATUS.md`.
2. `History/M07R/R03/L_CONTRACT_REPAIR.md`, `L_HOST_EVIDENCE.json`, `L_VALIDATION_MATRIX.md`.
3. Unchanged `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` for I's original failure evidence.
4. `History/M07R/R03/K_MEASUREMENT_PROTOCOL.md` and `Architecture/ADR/ADR-0002-pure-interpreter-qualification-boundary.md` for unchanged measurement/qualification limits.
5. This file for the only newly authorized Local execution.

## Exact source authority

Branch in all four repositories: `codex/assembly-shadow-r01b-h1`. Owning workspace: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`; repository directories have the names below.

| Repository | Exact source |
| --- | --- |
| night-outlook/hybridclr_demo | Final documentation-only transport containing this file, exactly matching Primary's final prompt and local/remote HEAD |
| night-outlook/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | `c86cbf665f5fcb2137e5adf2960541ce492467a4` |
| night-outlook/il2cpp_plus | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` |

Executable/CI anchor: `8d5297c375201687d17b91843ea0250ed90c0095`. Any delta from this anchor to the final demo handoff must be limited to `Docs/AssemblyShadow/**`. Do not run an arbitrary newer tip. The exact final SHA comes from the Primary prompt; a commit cannot literally embed its own hash.

## Implementation prepared

The package's two policy fixtures use one exact five-argument constructor helper. Its empty source collection is explicitly synthetic, not qualifying evidence. Production byte/metadata and ownership guards are unchanged. Twelve actual-helper host contracts and an additional early 18-method Unity regression are integrated.

The copied resource project now generates `architecture=arm64` alongside the exact Unity/target/repository tuple. Independent Python checks precede writing. A separate Unity preflight invokes actual `ShadowSourcePins.Read`/JsonUtility on the generated file and ten positive/negative controls before Configure/Install. Its before/after pin/settings/authority hashes must agree. Native runtime pins, counters, full Editor rosters, fixture DLLs and Player expectations are unchanged.

Primary host/compiler checks passed at the anchor; they do not claim actual Unity Editor or Player execution. The early Editor and real deserialization preflights are part of this Local run.

## Pinned environment and unused root

- Unity: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`.
- Python: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`.
- SDK-only root: `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`, version 8.0.318. Do not launch Unity 6000.
- New root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261003J-contracts`.

The root must not exist. Missing tools/platform versions or an existing root are blockers, not permission to substitute versions or delete evidence.

## Execute once

Fast-forward only; no reset/stash/forced checkout/unrelated merge or source edit. Verify the final prompt SHA before invocation.

```bash
set -euo pipefail
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
DEMO="$WORKSPACE/hybridclr_demo"
BATCH=/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261003J-contracts
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
git -C "$DEMO" merge-base --is-ancestor 8d5297c375201687d17b91843ea0250ed90c0095 "$DEMO_COMMIT"
git -C "$DEMO" diff --exit-code 8d5297c375201687d17b91843ea0250ed90c0095 "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
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

Immediately before running, require DEMO_COMMIT to equal Primary's final prompt SHA. Preserve the outer argv/environment/PID/timestamps/exit without editing runner outputs. Execute once; no retry in the same root.

## Required scope and evidence

Retain **all 90 cells, six fresh builds, 59 fresh Players, both 754/755 zero-skip Editor runs**. Added prerequisites are the 12 host constructor contracts, additional 18-method actual Editor preflight, and ten actual production source-pin consumer checks. They do not reduce the original scope.

Preserve all original ledger/result/index/archive/seal, nativeBinding/build, qualification, resource/P01–P05/production-entry/restoration, measurement/M06/early-startup, command and Player evidence. Also preserve:

- `fixture-constructor-host/results.json`, binary/source/command evidence;
- `fixture-constructor-editor/{scope.json,results.xml,Editor.log,verification.json}`;
- `resource-logs/source-pin-preflight.log` and `source-pin-contract-verification.json`;
- `<resource receiptRoot>/source-pin-contract.json`, all control JSON files and captured input hashes;
- actual owned Unity/supervisor completion receipts for both new preflights.

Keep compiler negative controls and expected runtime rejections distinct from successful build/publication. Preserve the four contaminated controls' Failed unisolated warm certificates. Do not broaden M01 coverage unless its real full-resource tests run and pass.

## Verdict, ownership and stop

All 90 cells and the seal must Pass for EvidenceReadyForPrimaryReview; any Failed/Blocked cell returns ReturnRequired. R03Accepted=false, H2Passed=false, qualificationApproved=false and PureInterpreter expansion disabled throughout. Full-stage reconciliation and independent review remain Primary-owned.

After the single run, factually update `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md`, add a new immutable `History/M07R/R03/local-validation-<date>-batch-j-<result>/` checkpoint, commit/push Local-owned demo evidence/docs, verify remote authority, and stop. Preserve every earlier checkpoint and custody state. Do not change source, expectations, timeouts, counter/lease policy, ownership/provenance checks or rosters to make it pass. Non-trivial defects return to Primary. No H2 or later milestone is authorized.
