# R02 Local Validation task sheet — after batch G

Protocol: `R02LocalBatch-v1`. Execute only the exact final pushed tuple in Primary's prompt and current `source-targets.json`. Read the live `Handoff/WEB_TO_LOCAL.md`, `G_INCLUDE_REPAIR.md`, and retained F integration/Editor-coverage designs first. No non-trivial source changes are assigned to Local.

## Entry and invocation

Candidate owning root: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`.
Control owning root: `/Users/ah/GitHub/hybridclr/assembly_shadow_r02_control/hybridclr_demo`.
Control branch/head: `codex/r02-h1-runtime-control@2e8ae9f5e5fa30325a4b6225b34a602477d7aa0e`.
Common source: `af9ba49127a7e852fed504a55c733c5f6ec5e54e`.

Resolve Unity 2022.3.62f2, Python 3.10+, PowerShell, .NET SDK supporting net8.0 and host C++ compiler on macOS arm64. Close both Unity editors. Set `TMPDIR=/private/tmp` and `PYTHONDONTWRITEBYTECODE=1`. Preserve all prior worktrees/evidence. Confirm all eight owning repositories and remote tips against the final prompt and source targets; no uncommitted source changes are allowed.

Set `CANDIDATE` and `CONTROL` to the owning roots above, `CANDIDATE_HEAD` to the exact final prompt transport HEAD, `CONTROL_HEAD` to `2e8ae9f5e5fa30325a4b6225b34a602477d7aa0e`, `UNITY`/`PWSH` to resolved absolute executable paths and `OUTPUT` to a new unused direct child of candidate `_temp/AssemblyShadow/`. The minimum entry free-space check is 30 GiB, not a guarantee of full evidence capacity.

```sh
export TMPDIR=/private/tmp
export PYTHONDONTWRITEBYTECODE=1
python3 "$CANDIDATE/Tools/AssemblyShadow/R02/run_local.py" \
  --candidate "$CANDIDATE" --candidate-head "$CANDIDATE_HEAD" \
  --control "$CONTROL" --control-head "$CONTROL_HEAD" \
  --unity "$UNITY" --pwsh "$PWSH" --output "$OUTPUT"
```

Inspect that dry plan, then add `--execute` for one new execution. Do not substitute the source anchor for the final transport HEAD. If a remote moves again, stop before execution and report the mismatch; do not rewrite pins or update to an unreviewed tip.

## Required batch coverage

All 34 existing cells remain required. First pass the full host Primary cell, including actual native writer/parser execution at diagnostics levels 0/1/2. Require twelve native fixtures, one legacy fixture and the unchanged complete assertions. Preserve compiler-version/include-policy/platform evidence and every compile/emit/managed receipt. The new macOS CI proves that path in its host environment, not the user's Local tools or Unity environment.

Then run independent E raw forensics, separate fixed-M00 materializations and fresh candidate/control ON/OFF graphs, eight functional sidecars, four pilot plus forty formal A/B pairs (88 fresh timing processes), Editor/native/generated-transaction/M07/startup11/failure/count132/diagnostic/lazy-dense/ordinary-mixed-capacity, final authorities and complete sealing.

All five exact Editor full names must appear once with Passed status in a Passed NUnit run:

- `AssemblyShadowDemo.Tests.R02ProbeContractTests.FormulaMatchesIndependentLoop`
- `AssemblyShadowDemo.Tests.R02ProbeContractTests.JsonPreservesNestedRawDiagnosticsAndLargeIntegers`
- `AssemblyShadowDemo.EditorTests.R02TypeResolutionSchemaTests.EveryR02LinkedFieldIsRequiredByActualRuntimeProof`
- `AssemblyShadowDemo.EditorTests.R02TypeResolutionSchemaTests.MatchingButNarrowedInputsCannotRedefineTheR02WireSchema`
- `AssemblyShadowDemo.EditorTests.R02TypeResolutionSchemaTests.UnitySerializationDoesNotManufactureMissingOrZeroR02Coverage`

`editor-tests.json` must bind the original XML and all five requiredCases. Host XML tests do not replace these real Editor cases. Inspect M07 early capsules/receipts separately from later parser/semantic results. Both count families use their own unchanged auditors before the 132-cell Player matrix. Generated transaction inputs depend on a valid current candidate graph.

## Failure, restoration and retention

Independent valid cells may continue; failed prerequisites block consumers. No semantic retry, timeout increase, native include flag workaround, hash/pin change, weaker verifier or smaller case set is allowed. Return non-trivial errors with the first failing command and complete stdout/stderr.

Use only the committed linker restoration policy. Retain original/generated/restored bytes and reject unfamiliar changes. Preserve forensic snapshots and their exact Git/index/archive provenance; never recreate an old path or silently omit missing evidence. Keep the frozen M00 hash and original materialization contract.

Retain every current build/input/launch/raw/verifier chain, type-resolution JSON, command completion snapshot, performance analysis, failure, seal/index/archive and indexed external root. `SEAL_FAILED.json` or an inventory alone cannot replace a complete seal. Preserve A/B/C/D/E/F/G and H1 evidence regardless of the new result.

Report D1/D2 CPU/memory effects and remaining uncertainty; a passing host or functional test is not performance/RAM acceptance. Keep historical R01 and current H1-runtime-control comparisons distinct.

Update and push `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` with actual classifications and exact source/evidence identities. Obtain a genuinely independent R02 stage review only when the full evidence is eligible. Stop and return to Primary. H1 remains PassedWithExplicitDeferredRisk; R02Accepted=false; mayEnterR03=false.
