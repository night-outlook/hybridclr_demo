# Primary Implementation → Local Validation: R03 conservative candidate, focused native evidence

## Objective

Run exactly one source-bound R03 focused Local Validation batch against the conservative candidate, preserve all raw evidence, and return the factual result to Primary. **Do not redesign R03, enable PureInterpreter structural expansion, relax expectations, or enter H2.**

Read first:
- `Docs/AssemblyShadow/README.md`
- `Docs/AssemblyShadow/Plan/CURRENT_STATUS.md`
- `Docs/AssemblyShadow/Plan/stages/R03-evolution-semantics.md`
- `Docs/AssemblyShadow/History/M07R/R03/A_PRIMARY_IMPLEMENTATION.md`
- `Docs/AssemblyShadow/History/M07R/R03/A_VALIDATION_MATRIX.md`
- `Docs/AssemblyShadow/History/M07R/R03/B_PRIMARY_HANDOFF.md`

## Canonical local paths

- workspace: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`
- demo: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`
- HybridCLR: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr`
- managed package: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity`
- IL2CPP: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus`
- unused batch root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930A-a898f`
- Unity: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`

The batch root must not already exist. Do not delete or reuse an existing root to make the run proceed.

## Repository/source authority

Branch in all four repositories: `codex/assembly-shadow-r01b-h1`.

Exact non-demo pins:
- `night-outlook/hybridclr` = `041c0cbb42d3e64e54fe605673d99799b5d63893`
- `night-outlook/hybridclr_unity` = `120bb01be680cec0375002a0823552d66d34b84c`
- `night-outlook/il2cpp_plus` = `1abb6bcaa85226f08c67f9da65edb3c58e8cb399`

Demo host-CI execution anchor: `f5f5712459fdf67e2b748ddeab8e6540bffd3d95`.
Pre-handoff documentation parent: `a898fbf7f65792f1edabef836c6706b2f27d7f1f`.

The authoritative demo validation commit is the **current pushed remote HEAD that contains this file**. A commit cannot contain its own SHA, so do not infer or hardcode a stale demo SHA from an earlier document. Resolve `refs/heads/codex/assembly-shadow-r01b-h1` immediately before execution; it must match the exact demo SHA in the final Primary handoff prompt. The runner repeats the remote-head check.

Before execution, verify the delta from `f5f5712459fdf67e2b748ddeab8e6540bffd3d95` to that final demo HEAD is documentation/coordination only. Any non-document/source/tool delta after the host-CI anchor is a blocker and must return to Primary.

## Implementation under validation

Primary implemented:
- target-only load ordering separated from safety/historical closure while retaining genuine target-cycle rejection;
- conservative `NativeLayoutAdmissionV1` in Editor and metadata-only native prepublication validation;
- physical linked-Player baseline binding for layout admission;
- logical method identity separated from token/slot/optimization metadata, with independent compatibility checks;
- old-AOT execution guard retained;
- ordinary hot-update role promotion rejection;
- real-DLL host fixtures, isolated Unity/IL2CPP project generation, native MethodInfo observer, strict evidence/verifier contracts and one 36-cell runner.

No private-reference structural expansion is enabled. Unknown/unsupported physical layout remains rejected or `NeedsNativeProof`.

## Required execution

Fast-forward only; do not merge unrelated work or modify source to make the batch pass.

Run this exact shell sequence:

```bash
set -euo pipefail

WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
DEMO="$WORKSPACE/hybridclr_demo"
BATCH=/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930A-a898f
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity

for REPO in hybridclr_demo hybridclr hybridclr_unity il2cpp_plus; do
  git -C "$WORKSPACE/$REPO" fetch origin "$BRANCH"
  git -C "$WORKSPACE/$REPO" checkout "$BRANCH"
  git -C "$WORKSPACE/$REPO" merge --ff-only "origin/$BRANCH"
done

DEMO_COMMIT="$(git -C "$DEMO" ls-remote origin "refs/heads/$BRANCH" | awk '{print $1}')"
test -n "$DEMO_COMMIT"
test "$(git -C "$DEMO" rev-parse HEAD)" = "$DEMO_COMMIT"
test "$(git -C "$WORKSPACE/hybridclr" rev-parse HEAD)" = 041c0cbb42d3e64e54fe605673d99799b5d63893
test "$(git -C "$WORKSPACE/hybridclr_unity" rev-parse HEAD)" = 120bb01be680cec0375002a0823552d66d34b84c
test "$(git -C "$WORKSPACE/il2cpp_plus" rev-parse HEAD)" = 1abb6bcaa85226f08c67f9da65edb3c58e8cb399

python3 -B "$DEMO/Tools/AssemblyShadow/R03/run_local.py" \
  --workspace "$WORKSPACE" \
  --output "$BATCH" \
  --unity "$UNITY" \
  --demo-commit "$DEMO_COMMIT"
```

Do not rerun in the same output root. A nonzero exit, failed cell, blocked prerequisite or failed seal is evidence and must be preserved.

## Required validations

The runner must execute exactly 36 cells, including:
- entry/final four-repository authority;
- Python verifier/filesystem contracts;
- reference-source worktrees;
- baseline and candidate real-DLL graph contracts;
- 35-case layout/method host suite;
- exact 15-DLL Player fixture inventory;
- four isolated prepare/build roles: candidate Release, reference Release, candidate Debug, candidate feature-OFF;
- real Unity EditMode tests with exact R03 case matching;
- nineteen fresh-process Player cases covering baseline, private-reference rejection, private-primitive native proof, physical slot movement, old-AOT execution guard, direction reversal, genuine target cycle, interface/kind/removal rejection, reference-core observations, Debug and feature-OFF behavior.

The detailed case identities and expected outcomes are normative for this batch in `A_VALIDATION_MATRIX.md` and `Tools/AssemblyShadow/R03/player-cases.json`.

## Expected result and evidence

Success requires:
- all 36 cells `Passed`;
- `LOCAL_BATCH_RESULT.json.result == "EvidenceReadyForPrimaryReview"`;
- `sealStatus == "Passed"`;
- `R03Accepted == false`;
- `H2Passed == false`;
- PureInterpreter structural expansion still disabled.

Preserve at least:
- `BATCH_EXECUTION.json`
- `LOCAL_BATCH_RESULT.json`
- `evidence-index.json`
- `evidence.tar.gz`
- `seal-receipt.json`
- all `cells/`, `commands/`, `host/`, `builds/`, `players/`, Editor XML/logs and retained live roots referenced by receipts.

A failed run must remain `ReturnRequired`; do not relabel completed launches or host checks as stage acceptance.

## Local-owned return

After the single run:

1. Write the factual current result at the top of `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md`.
2. Update `Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md` with the concise Primary return, including exact four-repository executed SHAs, result counts, seal/index/archive hashes, failing/blocked cells and evidence root.
3. Create an immutable checkpoint under `Docs/AssemblyShadow/History/M07R/R03/local-validation-<date>-<result>/` containing the bounded review/evidence receipts and manifest appropriate to the result.
4. Commit and push those Local-owned documentation/evidence changes to the demo branch only. Do not rewrite `WEB_TO_LOCAL.md`, product source, external repo pins or prior R02 evidence.
5. Stop and return control to Primary. Do not begin remaining R03 implementation or H2.

If the exact Unity executable or any required local SDK/tool is unavailable, record `Blocked` with the factual environment evidence rather than substituting a different Unity version.

## Known limits

Primary host CI passed, but this candidate has not yet produced accepted Unity/IL2CPP Player evidence. The focused batch is not full R03 acceptance. Full legacy regressions, broader generic/delegate/interface/stack-trace cases, startup/capacity/performance/memory work, PureInterpreter qualification/experiments and independent full R03 stage review remain after this return. H2 remains closed.
