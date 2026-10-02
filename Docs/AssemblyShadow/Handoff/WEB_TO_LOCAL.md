# Primary Implementation → Local Validation: R03 batch F, runtime attribution and physical readiness

## Objective and immutable prior result

Run exactly one new **36-cell batch F** against the published runtime repair tuple. Preserve all evidence and return to Primary. Do not retry A–E, reuse their apps, modify their evidence, enable PureInterpreter expansion or enter H2.

Authoritative Local return: `b97375d4b12357d0f987cf7738eaa422d4615081`. E remains **ReturnRequired: 32 Passed / 4 Failed / 0 Blocked; seal Passed**. Its four native builds and 754 selected Editor cases passed; all nineteen Players ran with fifteen Passed and four Failed. C03/C04/C05 Release warm intervals gained an unattributed proof; C07 failed prepublication physical readiness. No source review or new measurement contract retroactively promotes those cells. The excluded M01 resource test remains NoCoverage.

## Read first

All relative documentation paths are under `Docs/AssemblyShadow/`:
1. `README.md` and `Plan/CURRENT_STATUS.md`.
2. `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` for unchanged E evidence, not old commands.
3. `History/M07R/R03/G_RUNTIME_PROOF_REPAIR.md`, `G_HOST_EVIDENCE.json`, `G_VALIDATION_MATRIX.md`.
4. `Plan/stages/R03-evolution-semantics.md` and `History/M07R/R03/A_PRIMARY_IMPLEMENTATION.md` for full-stage obligations.
5. This live handoff for the only authorized next execution.

## Exact source authority

All four repositories use `codex/assembly-shadow-r01b-h1`.

| Repository | Exact owning checkout | Revision |
| --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Final docs-only transport SHA in Primary's prompt, resolved and checked below |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `120bb01be680cec0375002a0823552d66d34b84c` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `aae0ebb55b8761a7a905b410349d006d76fa748b` |

New tested executable/CI anchor: **`67e8c1df18f84dda4ec70edd45b1ed717bcea4e8`**. Only `Docs/AssemblyShadow/` documentation/evidence may differ after it. The native pins changed; do not reuse E's earlier native source tuple. The managed package, reference native cores/package, four build roles, nineteen case identities, deadlines and top-level dependencies remain unchanged.

A commit cannot embed its own SHA. Resolve the final demo transport as the latest commit touching this WEB_TO_LOCAL.md, then require it to equal local HEAD, current remote HEAD and Primary's exact final prompt. The runner independently repeats all four authority checks before and after execution. Do not execute the anchor itself, a smoke commit, an old transport or an arbitrary later branch tip.

## Implemented correction and explicit contract

LE-001: bounded native cold-event attribution and six exact observer/loop boundaries replace the assumption that the entire managed-observer interval is a pure business-allocation interval. Raw broad counters remain visible and must match their native snapshots. Every cold delta must reconcile to full physical key, logical type, generation/domain/context, site and process-local native thread identity. The exact 10,000-allocation loop must still have zero new admission proof/layout/field/interface work and retain at least 10,000 hits and baseline-state checks. Broad cold work is allowed only outside the exact loop with complete non-target attribution, not an unexplained +1 allowance. Historical E's extra class/site/thread remains unknown.

LE-002: staged initialization now exposes an authenticated finalized-definition layout capability only after complete metadata initialization. It avoids forcing Class::Init, baseline object allocation or business initializers, while retaining the original baseline readiness and physical CheckLayout guards. C07 remains a required positive case. It must prove private Int64 tail geometry and successful prepublication readiness before Commit, without baseline business initialization. Unready or incompatible layouts retain fail-closed terminal behavior; Local must not change this success expectation to a rejection.

The isolated native test profile enables the bounded runtime probe; its ordinary-build default is off. Raw Player observations now use schema 2 with runtimeProbe. Old-core reference controls do not claim unavailable probe coverage. This is diagnostic validation, not a production performance acceptance run.

Primary has completed source review, 144 Python contracts, retained host/fixture/lifecycle/provenance tests, native header regressions and 25 pinned-SDK syntax compilations. The complete updated helper/package compilation also passed. Those results are not actual new integrated Player proof; that is the purpose of F.

## Environment and new unused root

- Unity: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`; target StandaloneOSX/arm64.
- Python: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`.
- Direct managed SDK: `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`, version **8.0.318**, used as SDK only. Do not launch Unity 6000.
- New root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261002F-runtime`.

Verify the recorded tools and versions. Missing/mismatched tooling is Blocked, not permission to substitute versions. The root must not exist. Never delete/reuse an output root to bypass the guard. Preserve all A–E/R02/H1 live evidence, original archives and exact-byte publication parts.

## Execute once

First verify canonical origins and clean owning checkouts. Fast-forward only: no reset, stash, forced checkout, unrelated merge or source edits.

```bash
set -euo pipefail
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
DEMO="$WORKSPACE/hybridclr_demo"
BATCH=/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261002F-runtime
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
git -C "$DEMO" merge-base --is-ancestor 67e8c1df18f84dda4ec70edd45b1ed717bcea4e8 "$DEMO_COMMIT"
git -C "$DEMO" diff --exit-code 67e8c1df18f84dda4ec70edd45b1ed717bcea4e8 "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
test "$(git -C "$WORKSPACE/hybridclr" rev-parse HEAD)" = 4b2774b066cfc6afd77a8c8aded6bda7ea574f55
test "$(git -C "$WORKSPACE/hybridclr_unity" rev-parse HEAD)" = 120bb01be680cec0375002a0823552d66d34b84c
test "$(git -C "$WORKSPACE/il2cpp_plus" rev-parse HEAD)" = aae0ebb55b8761a7a905b410349d006d76fa748b
test "$(dotnet --version)" = 8.0.318
test -f "$UNITY"
test ! -e "$BATCH"
"$PYTHON" -B "$DEMO/Tools/AssemblyShadow/R03/run_local.py" \
  --workspace "$WORKSPACE" --output "$BATCH" \
  --unity "$UNITY" --demo-commit "$DEMO_COMMIT"
```

Before the runner invocation, compare DEMO_COMMIT with Primary's exact prompt. Capture actual argv/environment/PID/timestamps/exit without changing runner output. Invoke once. A failed preflight is Blocked, not a fabricated 36-cell execution. Independent cells are already scheduled; do not manually launch blocked cases or retry any batch.

## Required new evidence

Retain all **36 cells / four fresh native build roles / 754 selected Editor cases with zero skips / nineteen fresh-process Players**. The verifier cell runs 144 Python tests. Preserve the existing actual fixture consumers, compiler/lifecycle controls, complete-helper check, schema-2 native build provenance and excluded M01 NoCoverage.

Six candidate warm witnesses remain mandatory: C03/C04/C05/C07 and D02/D03. For each, retain native sample labels `[0,10,1,2,11,3]`, the original broad before/after snapshots, all cold events and exact-loop deltas. Report observed class/physical-key/site/thread/span attribution when present; otherwise report the unresolved mismatch. No new attribution is assigned retrospectively to E.

C07 additionally requires exactly one successful prepublication R03Contract/R03.Node layout row: both sides ready, target definition readiness true, no pending layout, physicalProof true/error0, unchanged baseline initialization/vtable/cctor state, one retained field plus private eight-byte tail storage, and successful publication/invocation/allocation. Preserve the full row even when it fails; do not warm or initialize baseline business state to bypass the guard.

Keep result/ledger/index/archive/seal, all command streams and Unity completion receipts, host/fixture/compiler outputs, configs/source manifests, nativeBinding, build receipts/apps, editor-scope.json, editor-verification.json and actual XML. Every launched Player retains request.json, raw.json including runtimeProbe, Player.log and the launch receipt. Semantic verification now writes a source-bound Passed or Failed verification.json; a Failed receipt is not an acceptance result. Missing outputs after an earlier launch failure remain missing, not fabricated.

## Local-owned return and stop

All 36 cells and the focused seal must pass for EvidenceReadyForPrimaryReview. Otherwise return ReturnRequired with the original Failed/Blocked/NotRun/NoCoverage distinctions. A successful focused batch still has R03Accepted=false, H2Passed=false, pureInterpreterExpansionEnabled=false and fullLegacyRegressionAcceptance=false.

Update `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` factually; retain E as historical. Add an immutable `History/M07R/R03/local-validation-<date>-batch-f-<result>/` checkpoint. Commit/push Local-owned demo evidence/docs and stop for Primary reconciliation. For large archives, preserve the live original and use the existing ordered exact-byte parts plus independent reconstruction audit, without re-compression or seal changes.

No non-trivial implementation is delegated. Source, native readiness policy, probe/schema, scope/filter, expectations, warm-up/iteration count, pins, deadlines and lifecycle changes require Primary. Do not reuse old apps, globally kill named compiler processes, relax attribution, flip C07 to an expected rejection or rewrite failed raw values. Full legacy/resource/M01 coverage, broader generic/interface/delegate/stack-trace work, startup/capacity/performance/memory, PureInterpreter qualification and independent full-stage review remain Primary-owned before H2.
