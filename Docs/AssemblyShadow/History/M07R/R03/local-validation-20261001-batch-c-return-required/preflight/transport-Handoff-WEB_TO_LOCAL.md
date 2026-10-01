# Primary Implementation → Local Validation: R03 batch C, fixture references and Unity lifecycle

## Objective and preserved return

Run one fresh **36-cell R03 batch C** after the R03-LB-001 fixture-reference and R03-LB-002 Unity compiler-lifetime repairs. Do not retry A or B, redesign R03, enable PureInterpreter expansion, or enter H2.

The authoritative Local return is `ec463b6dfbd91603ec0c539378af6dbbe6b9e651`. Batch B remains **ReturnRequired: 12 Passed / 5 Failed / 19 Blocked**, focused seal Passed. Its managed host tests passed; Unity compilation failed; Editor assertions, native/IL2CPP builds and nineteen Players did not run. A remains historical. Neither Local-owned report nor any A/B checkpoint was rewritten by this repair.

## Read order

All paths below are under `Docs/AssemblyShadow/`:
1. `README.md` and `Plan/CURRENT_STATUS.md`.
2. `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` for preserved B facts, not old execution instructions.
3. `History/M07R/R03/D_INPUT_REPAIR.md`, `D_HOST_EVIDENCE.json`, and `D_VALIDATION_MATRIX.md`.
4. `History/M07R/R03/A_PRIMARY_IMPLEMENTATION.md` and `Plan/stages/R03-evolution-semantics.md` for unchanged product scope.
5. This live handoff for the new command and source authority. Earlier A/B/C preparation records are historical.

## Exact source authority

Branch in all four repositories: `codex/assembly-shadow-r01b-h1`.

| Repository | Exact owning path | Revision |
| --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Final docs-only transport SHA supplied in Primary's prompt; resolve using this handoff's latest touching commit and require local/remote HEAD equality as below |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `041c0cbb42d3e64e54fe605673d99799b5d63893` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `120bb01be680cec0375002a0823552d66d34b84c` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `1abb6bcaa85226f08c67f9da65edb3c58e8cb399` |

**New tested executable/CI anchor: `5c2932d5340728b16302b7cea8f20b64fcc9e7ce`.** It supersedes the earlier `7e2852...` and `f5f571...` anchors for new runs. Implementation is `c72893c0df9452aa46a45a1f723b71f62512a0e6`; `5c2932...` fixes the new consumer's static/instance call shape without changing fixture semantics. Only documentation/evidence may differ after the new anchor.

Execute exactly the final pushed transport SHA, not the source anchor, a smoke commit, an arbitrary later HEAD or a previous batch's executed commit. A context-free agent resolves it as the latest commit touching this WEB_TO_LOCAL.md, then requires it to equal local HEAD and the current remote branch HEAD. The value must also equal Primary's final prompt. The runner independently verifies all four authorities before and after execution.

Native/package pins, nineteen Player cases, four build roles, normal runtime expectations, original command deadlines and the top-level 36-cell ledger remain unchanged. Reference package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192` is used for baseline graph tests; reference Players use the accepted R02 native cores `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` / `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c` with the current package/harness, not a historical binary.

## Implemented correction and selection

The common fixture generator explicitly emits unsigned A/B provider references (empty PublicKeyToken, PublicKey flag clear). A new audit verifies all fifteen Player plus eighteen shared-corpus DLLs, including exact provider identity and unchanged graph/static-field witnesses. Real compiler consumers check every input; a separate malformed control must produce the exact invalid-public-key diagnostic.

R03's Unity build and EditMode calls now use the existing, unchanged birth-authenticated R02OwnedUnityRoslyn-v2 supervisor through `unity_command.py`. It retires only the selected invocation's exact compiler children before the unchanged outer R03OwnedCommandV1 boundary. Unknown/new/changed descendants fail closed. Direct .NET worker prevention remains in place. There is no global compiler shutdown or dotnet-name exception. Original command exit codes remain intact.

Changed files: `Fixtures/EvolutionFixtureCorpus.cs`; new `FixtureAudit/FixtureAudit.csproj` and `Program.cs`; `input_validation.py`, `unity_command.py`, `test_input_validation.py`, `run_host_inputs.py`; integration in `run_local.py`/`run_host_lifetime.py`; and `.github/workflows/r03-primary.yml`, all under `Tools/AssemblyShadow/R03/` unless fully qualified. The reused R02 supervisor/identity/evidence files, native/package sources, outer lifetime helper and Player expectations are unchanged.

Selection: use the existing authenticated supervisor for Unity's recorded `/shared` lifecycle rather than an unverified Unity compiler switch or broad process cleanup. No runtime candidate or cleanup fallback may be selected locally to turn a failure into success.

## Environment and new root

- Unity: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`.
- Target: `StandaloneOSX`, `arm64`.
- Python: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`.
- Existing direct managed SDK: `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`, SDK **8.0.318**. This is an SDK location only; do not launch that Unity 6000 Editor.
- New prescribed root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001C-inputs`.

Verify the recorded tools and versions still exist. Missing or mismatched tooling is Blocked, not permission to substitute Unity/SDK versions. The root must not already exist; never delete or reuse A, B or C to bypass the unused-root guard.

## Execution

Verify canonical origins and clean owning checkouts before synchronizing. Fast-forward only. No reset, stash, forced checkout, unrelated merge or source edits. Preserve all A/B/R02/H1 roots and live evidence.

```bash
set -euo pipefail
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
DEMO="$WORKSPACE/hybridclr_demo"
BATCH=/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001C-inputs
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
git -C "$DEMO" merge-base --is-ancestor 5c2932d5340728b16302b7cea8f20b64fcc9e7ce "$DEMO_COMMIT"
git -C "$DEMO" diff --exit-code 5c2932d5340728b16302b7cea8f20b64fcc9e7ce "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
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

Compare DEMO_COMMIT with Primary's exact final prompt before running. Capture preflight environment, actual command, timestamps, process ID and runner exit without changing its output files. Invoke once. A failed preflight is recorded as Blocked; do not manufacture a 36-cell execution that never occurred.

## Required checks and evidence

The original **36 cells / four native build roles / nineteen fresh-process Player cases** remain required. The existing verifier cell now runs **57** tests. The player-fixtures cell additionally audits 33 DLLs, compiles 33 consumers with the pinned Unity compiler, verifies one explicit invalid-key consumer control, and runs separate valid/invalid isolated Editor compiler/lifecycle probes. These two additional Editor probes do not replace native builds or EditMode assertions.

Normal commands still require successful exit and semantic assertions. Only the explicitly named invalid-key controls expect exit 1, with CS0009 and Invalid public key, no consumer/marker output and clean supervised completion. Their original command failures remain visible. Arbitrary compilation errors, timeouts, missing receipts or lingering processes cannot satisfy a negative test.

Collect the unchanged result/ledger/index/archive/seal files and all cells/commands/host/builds/players/Editor evidence. Also preserve:
- `fixture-audit/results.json`, generated consumer sources, shared corpus and malformed control;
- `consumer-unity-2022.3.62f2/results.json`, emitted consumer DLLs and compiler/runtime/reference bindings;
- `unity-lifecycle/results.json`, both logs and the valid marker;
- both `projects/compiler-probe-*` source/input directories;
- `commands/*/unity-completion.json` with original inner command/exit, compiler binding, birth-identity/PGID observations and retirement actions;
- the corresponding outer schema-v2 command receipts and any process-group-before-cleanup diagnostics.

For Unity calls the outer command PID is the supervisor PID, not the inner Unity PID. Native Player launch PIDs/run IDs remain direct and unchanged. Do not rewrite pre-cleanup observations using post-cleanup state. Preserve excluded live worktrees/SDK/cache roots according to the original focused seal policy.

All 36 cells and the focused seal must pass for EvidenceReadyForPrimaryReview. Any failed or blocked work remains ReturnRequired. R03Accepted=false, H2Passed=false, pureInterpreterExpansionEnabled=false and fullLegacyRegressionAcceptance=false remain mandatory.

## Local-owned return and limits

Update `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` factually, preserving B as historical. Create a new immutable `History/M07R/R03/local-validation-<date>-batch-c-<result>/` checkpoint with the executed tuple, counts, command/error details, all new subcheck evidence, seal/index/archive hashes and custody audit. Commit/push Local-owned demo reports/evidence, then stop for Primary reconciliation. Do not edit this handoff or external repositories.

No non-trivial implementation is delegated. Environment/path verification and reporting are permitted; changes to source, fixture flags, consumers, expectations, pins, timeouts, cleanup rules or negative-test classification require Primary. Do not manually run blocked cases, rerun this batch, globally kill compiler servers or repair sealed A/B bytes.

Host .NET compiler and supervisor checks passed on Linux and macOS arm64; actual Unity compiler/Editor/IL2CPP checks remain the purpose of C. B's exact survivor identity is still uncertain. Full R03 legacy/resource regressions, broader method/generic/interface/delegate/stack-trace coverage, startup/capacity/performance/memory, PureInterpreter qualification and independent full stage review remain Primary-owned. This batch cannot approve R03, H2 or release.
