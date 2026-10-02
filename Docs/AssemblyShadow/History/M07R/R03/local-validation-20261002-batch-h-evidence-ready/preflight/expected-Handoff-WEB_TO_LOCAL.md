# Primary Implementation → Local Validation: R03 batch H, rejected-stage observation

## Objective and preserved result

Run exactly one fresh **37-cell batch H** against the rejected-stage identity/observation repair. Preserve all evidence and return to Primary. Do not retry A–G, reuse their apps, alter historical evidence, enable PureInterpreter expansion or enter H2.

Authoritative Local publication: `0d8a19830ce454d22335c854978816a830997187`. G remains **ReturnRequired: 32 Passed / 5 Failed / 0 Blocked; seal Passed**. Its four builds, 754 Editor cases, six strict isolated warm witnesses and full positive C07 passed. All four controls identified the ArrayPool Gen2-finalizer producer; their diagnostic results passed while contaminated unisolated warm certificates remained Failed. Five rejection cases failed after probe reads changed the terminal observation from error16 to error15. The excluded M01 test remains NoCoverage.

## Read first

Paths are relative to `Docs/AssemblyShadow/`:
1. `README.md` and `Plan/CURRENT_STATUS.md`.
2. `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` for unchanged G facts, not old commands.
3. `History/M07R/R03/I_REJECTION_OBSERVATION.md`, `I_HOST_EVIDENCE.json`, `I_VALIDATION_MATRIX.md`.
4. `History/M07R/R03/H_PRODUCER_ISOLATION.md` for the unchanged diagnostic lease/control contract and `Plan/stages/R03-evolution-semantics.md` for full-stage obligations.
5. This live handoff for the only new authorized execution.

## Exact source authority

All repositories use `codex/assembly-shadow-r01b-h1`.

| Repository | Exact owning checkout | Revision |
| --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Final docs-only transport SHA in Primary's prompt, resolved and checked below |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `120bb01be680cec0375002a0823552d66d34b84c` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` |

New tested executable/CI anchor: **`9d70494c97e4efc9597a3e071f63c1489c6ac396`**. Only Docs/AssemblyShadow documentation/evidence may differ after it. Do not use G's older IL2CPP revision. HybridCLR/package, reference cores/package, four build roles, all case identities, fixture DLLs, counter/lease/ownership guards and command deadlines remain unchanged.

Resolve the final demo transport from the latest commit touching this WEB_TO_LOCAL.md; require it to equal local HEAD, current remote HEAD and Primary's exact prompt. A commit cannot embed its own SHA. Never execute an arbitrary later tip, old anchor, smoke commit or preserved app. The runner independently verifies all four authorities at entry and completion.

## Repair and required observation

Layout definition identities are copied while staged ownership is valid, then rendered from owned bytes rather than resolving rejected private handles. This does not widen visibility, restore terminal errors, initialize baseline business state or relax rejection expectations. Fresh overall Player raw and available runtimeProbe schemas are **3**. `rejectionProbe` is a JSON string with schema1 / R03RejectedProbeNonMutationV1. Do not upgrade historical raw data.

C02/C08/C09/C10/D01 must still reach Validate16/state8/unpublished with no post-failure business work. They now capture terminal diagnostics/recovery before probe retrieval, after a fixed 16-byte capacity control returning **-2**, after one complete read, and after a second complete read. Both full receipts must succeed with exact byte counts, retained Captured layout identities and identical layout rows. The original terminal transaction and entire recovery must remain unchanged through every capture and the final raw diagnostics. Error15, -3, missing/changed identities, exceptions, omitted rows or restored errors are failures. A retained prior row is not necessarily the failing type; do not fabricate that attribution.

The original positive checks remain mandatory: six strict warm certificates with zero all-thread exact-loop proof/layout work, the finite drained producer lease, 10,000 allocations and unchanged preparation, real method/old-AOT guard/graph behavior, C07 positive physical proof, and four independent unisolated producer controls. Contaminated controls retain Failed unisolated warm certificates; at least one control must identify the actual producer. No global finalizer suppression, lease extension or threshold relaxation is authorized.

Primary completed 183 Python contracts, host/native regression and artifact authentication, complete-helper/package compilation and 35 pinned-SDK native syntax checks. These are not integrated rejection-path Player acceptance; that remains H's purpose.

## Pinned environment and unused root

- Unity `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`; StandaloneOSX/arm64.
- Python `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`.
- Managed SDK `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`, version **8.0.318**, SDK only. Do not launch Unity 6000.
- BCL `Contents/MonoBleedingEdge/lib/mono/unityaot-macos/mscorlib.dll`, SHA-256 `d89d5124cafb873b34c2eac68d2ece41d14fec10999baf0e4620276dff54ab83`.
- New root `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261002H-rejection`.

Verify all recorded paths/versions and that the root does not exist. Missing/mismatched tooling is Blocked, not permission to substitute or delete a root. Preserve all A–G/R02/H1 live evidence, original archives and ordered exact-byte publication parts.

## Execute once

Verify canonical remotes and clean owning checkouts first. Fast-forward only: no reset, stash, forced checkout, unrelated merge or source edits.

```bash
set -euo pipefail
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
DEMO="$WORKSPACE/hybridclr_demo"
BATCH=/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261002H-rejection
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
PYTHON=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
BCL=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MonoBleedingEdge/lib/mono/unityaot-macos/mscorlib.dll
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
git -C "$DEMO" merge-base --is-ancestor 9d70494c97e4efc9597a3e071f63c1489c6ac396 "$DEMO_COMMIT"
git -C "$DEMO" diff --exit-code 9d70494c97e4efc9597a3e071f63c1489c6ac396 "$DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
test "$(git -C "$WORKSPACE/hybridclr" rev-parse HEAD)" = 4b2774b066cfc6afd77a8c8aded6bda7ea574f55
test "$(git -C "$WORKSPACE/hybridclr_unity" rev-parse HEAD)" = 120bb01be680cec0375002a0823552d66d34b84c
test "$(git -C "$WORKSPACE/il2cpp_plus" rev-parse HEAD)" = 1cf87f8209790f9fb2ebec97487dc1990ccd56c5
test "$(dotnet --version)" = 8.0.318
test -f "$UNITY"
printf '%s  %s\n' d89d5124cafb873b34c2eac68d2ece41d14fec10999baf0e4620276dff54ab83 "$BCL" | shasum -a 256 -c
test ! -e "$BATCH"
"$PYTHON" -B "$DEMO/Tools/AssemblyShadow/R03/run_local.py" \
  --workspace "$WORKSPACE" --output "$BATCH" \
  --unity "$UNITY" --demo-commit "$DEMO_COMMIT"
```

Before invocation compare DEMO_COMMIT with the final Primary prompt. Capture actual argv/environment/PID/timestamps/exit without modifying runner outputs. Invoke once; independent checks are already scheduled. A failed preflight is Blocked, not fabricated batch execution. Never manually launch blocked cases or repeat a transaction/control until it passes.

## Evidence, publication and stop

Retain all **37 cells / four fresh builds / 754 selected Editor cases with zero skips / 23 fresh Players**. The verifier cell runs 183 Python tests. Preserve result/ledger/index/archive/seal, every command stream/completion, fixture/compiler and source/config bindings, nativeBinding/apps, Editor scope/XML/verdict, all Player requests/raw/Passed-or-Failed verification records and producer-controls.json.

Additionally preserve all four captures and return codes in rejectionProbe, the second complete native receipt, captured layout identity/status fields and each rejectionObservation verifier subcheck. Full raw diagnostic strings remain evidence; only the explicit immutable transaction projection is required invariant, not ordinary-class enumeration. Keep missing M01 coverage and contaminated control warm certificates distinct from passes.

All 37 cells and the focused seal must pass for EvidenceReadyForPrimaryReview; otherwise return ReturnRequired. Even on focused success keep R03Accepted=false, H2Passed=false, pureInterpreterExpansionEnabled=false and fullLegacyRegressionAcceptance=false.

Update Handoff/LOCAL_VALIDATION.md and Handoff/RETURN_TO_WEB.md factually, preserving G as historical. Add an immutable History/M07R/R03/local-validation-<date>-batch-h-<result>/ checkpoint. Commit/push only Local-owned demo reports/evidence, verify final repository/branch/HEAD, and stop for Primary reconciliation. Oversized archives use unchanged live originals plus ordered exact-byte parts and independent reconstruction; never recompress or rewrite the original seal.

No non-trivial implementation is delegated. Any source, identity-capture policy, schema, counter/lease/ownership rule, scope/filter, fixture, pin, warm-up, iteration-count, deadline or cleanup change returns to Primary. Full M01/legacy/resource, broader runtime, startup/capacity/performance/memory, gated qualification and independent stage review remain Primary-owned before H2.
