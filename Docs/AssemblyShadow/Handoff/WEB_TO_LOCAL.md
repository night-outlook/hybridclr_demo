# Primary Implementation → Local Validation — ONE 16-component P1 opaque-execution source/SDK cycle

**This exact Docs-only handoff authorizes one new source/host + official installed Unity2022.3.62f2 SDK SYNTAX-ONLY Local Validation cycle.** Objective: verify the new **inactive nonempty opaque execution-observation inventory** source method and its fail-closed typed receipt, while retaining every previous source/host and compiler control. This does NOT authorize Unity Editor, Test Runner, Player, native linked runtime, seven-root SNAP-01 replay, engine-owner/scheduler exploration, Human Review Gate, later milestone, or implementation changes by Local.

## Consumed historical evidence — do not rerun

Latest Local-owned 20261019-48ee is PASS / PassedSourceHostAndSDKOnly, 15/15 components, 70 distinct Python command-failure tests, five official managed compiler products with exact OriginalUnsignedCounts expected-negative, 85/85 native SDK C++17 arm64 syntax commands. This run and its raw/scratch/audit/checkpoint are **consumed**, as are all previous P1 source/SDK results. Original d16d SourceConfirmed_NotFaultInjected finding is corrected within later controlled host scope, not altered at its original source tuple. Existing SNAP-01/N/M/K/I/E and historical immutable R02 whole-file fingerprint FAIL, original strict S custody Blocked, independent R03 full-stage FAIL/re-review NotRun remain exactly as recorded in LOCAL_VALIDATION.md. Never reclassify a prior result based on current CI, mock tests or SDK syntax.

## Mandatory read order before any execution

1. Docs/AssemblyShadow/README.md and Plan/CURRENT_STATUS.md at the exact demo pinned HEAD.
2. Local-owned Handoff/LOCAL_VALIDATION.md **first**, then Handoff/RETURN_TO_WEB.md; read the full consumed 20261019-48ee checkpoint and all original historical limitations.
3. [New P1 source design](../History/M07R/R03/IR_Remediation/P1_OPAQUE_EXECUTION_INVENTORY_2026-10-19/DESIGN.md), [Primary review](../History/M07R/R03/IR_Remediation/P1_OPAQUE_EXECUTION_INVENTORY_2026-10-19/PRIMARY_REVIEW.md), [machine evidence](../History/M07R/R03/IR_Remediation/P1_OPAQUE_EXECUTION_INVENTORY_2026-10-19/EVIDENCE.json).
4. This full handoff and [remaining implementation plan](../History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md). No authority may be inferred from chat or a previous WEB_TO_LOCAL.md invocation.

## Exact four canonical repositories and branch

All four must be separate, clean canonical Git working trees on branch **codex/assembly-shadow-r01b-h1**, with valid night-outlook/<repo> origins, local and remote HEADs exactly equal and no unrelated files or submodule/worktree drift. Parent /Users/ah/GitHub/hybridclr/assembly_shadow_h1r is NOT a Git repository. Fast-forward only clean ancestor branches; never reset, clean, force-push, merge unrelated states or overwrite dirty files.

| Repository | Existing Local checkout path | Required pushed source |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | **Final handoff-containing Docs-only commit**, exactly equal to live remote branch HEAD, local HEAD and the accompanying Primary final prompt's full 40-character SHA. The tested source/host anchor is **224f4db367c9bae557c32c2351b8dd36b64cb2fe**; every commit after this anchor MUST change only Docs/**. |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | **4b2774b066cfc6afd77a8c8aded6bda7ea574f55** |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | **948c0e3b4f8891481301770115e8ba4945eea6de** |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | **5e2326a45bd6070aa25830ca8c0236e1915bde13** |

Demo HEAD must be exactly the commit which last modified Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md; compare with git log -1 --format=%H -- that path. Verify both local clean branch HEAD and git ls-remote for this exact branch before any work. Check that no non-Docs source changes occurred after the source anchor. A later branch update, even a Docs-only commit, invalidates this authorization until Primary publishes another handoff. Historical Tools/AssemblyShadow/R03/source-pins.json records earlier original native source and **must never be rewritten**; explicit --candidate-native-sha selects the current native source without reclassifying historical evidence.

## Primary-owned implementation, not delegated to Local

- Native **TryCaptureOpaqueExecutionInventory(Scratch&, Receipt&)** in AssemblyShadowOpaqueExecutionInventorySource.inl is included ONCE by AssemblyShadow.cpp and exposed only under the Assembly Shadow feature switch in AssemblyShadow.h. It is **inactive**, without any original getter/Player/native execution path caller.
- It holds initial-session metadata-lifetime admission across two bounded readings of the 2,048-slot process execution-observation registry. Only the original short ExecutionObservationLock protects each pointer-value copy; no Il2CppClass dereference, type key, static field read, metadata/transaction/usage nested locks, callbacks, heap allocations or file writes. It checks nonnull count <=1,024, duplicate identities and exact same slot identities before discarding raw pointers and returning a count/generation/observed-stability receipt.
- **This is NOT complete execution/class serialization.** The sampled values are opaque, unauthenticated physical pointers; no pointer origin, lifetime, VM-wide coherent epoch/ABA, type-key correctness, real class-row execution details, GC/RSS, Shutdown deadlock freedom, Player or runtime acceptance is proven. The existing original general/execution getters, C# APIs, terminal guards and V1/V2 semantic/report predicates are unmodified.
- Native source-bound runner run_opaque_execution_inventory.py compiles the actual production header/method (not a transcription) against explicit VM mocks and requires original AssemblyShadow.cpp/.h getter blobs unchanged except the narrow additive includes/declaration. **18 distinct native host cases per strict/ASan+UBSan profile**, five direct compiler-version/compile/run receipts, no pointer-valued output, no acceptance flag promotion, exact source hash custody.
- Demo one-shot run_p1_metadata_local_preflight.py schedules **16 independently receipted components**. The newly added opaque-inventory child expects PassedWithinInactiveOpaqueHostScope; its source hashing includes the new native .h/.inl, runner, fixture, and new SDK syntax probe. The original **70** command-failure regressions and all other existing 15 components remain. Native candidate official SDK syntax is now **90 C++17 arm64 -fsyntax-only commands** = 18 unique translation units × five unchanged candidate/debug/probe-off/diagnostics-off/feature-off profiles. AssemblyShadow.cpp itself compiles the exact .inl; the 18th translation unit AssemblyShadowOpaqueInventorySyntax.cpp checks method signature and bounded scratch. The existing five managed positive compilation products and separate expected-negative OriginalUnsignedCounts exit1, exactly two CS0266 and no DLL are unchanged.
- Native [CI 39244090056](https://github.com/night-outlook/il2cpp_plus/actions/runs/39244090056) Passed Mac Clang/Linux Clang/GCC 3/3. Demo [managed/aggregate CI 39244400344](https://github.com/night-outlook/hybridclr_demo/actions/runs/39244400344), [focused command-failure CI 39244400346](https://github.com/night-outlook/hybridclr_demo/actions/runs/39244400346) and [integrated 70-test CI 39244400525](https://github.com/night-outlook/hybridclr_demo/actions/runs/39244400525) Passed. These are HOST/mocked execution, not a fresh official installed Unity SDK run or a linked Player.

## Exactly ONE fresh and unused evidence set

Before execution independently verify four exact source/remote pins, original consumed evidence and SDK before hashes, canonical roots absent/disjoint and sufficient approved external storage. All FOUR paths must be absent and never reused, outside SDK/checkouts/previous raw/scratch/audit and each other:

- New raw batch: /Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-OPAQUE-INVENTORY-20261019-5e23
- New SDK copy scratch: /Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-OPAQUE-INVENTORY-20261019-5e23
- New independent Local audit/authority root: /Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-OPAQUE-INVENTORY-20261019-5e23
- New additive checked-in checkpoint: Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-opaque-inventory-20261019-5e23/

Read-only installed official Unity 2022.3.62f2 Apple arm64 SDK anchor (DO NOT LAUNCH):
/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity

Inherited TMPDIR and original compiler subprocess/private/tmp policy remain unchanged. No Unity SDK/vendor/product binaries may be committed to Git. Local may only create independent audit/checkpoint after admission.

## ONE executable command, after all independent checks

    set -euo pipefail
    W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
    D="$W/hybridclr_demo"
    B=/Users/ah/GitHub/hybridclr/r03-local-validation
    UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
    SOURCE=224f4db367c9bae557c32c2351b8dd36b64cb2fe
    NATIVE=5e2326a45bd6070aa25830ca8c0236e1915bde13
    DEMO_SHA="$(git -C "$D" rev-parse HEAD)"
    test "$(git -C "$D" branch --show-current)" = codex/assembly-shadow-r01b-h1
    test "$DEMO_SHA" = "$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
    test "$DEMO_SHA" = "$(git -C "$D" ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1 | awk '{print $1}')"
    git -C "$D" diff --exit-code "$SOURCE" "$DEMO_SHA" -- . ':(exclude)Docs/**'
    python3 -B "$D/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
      --workspace "$W" --unity "$UNITY" \
      --expected-demo "$DEMO_SHA" --expected-native "$NATIVE" \
      --output "$B/R03-P1-OPAQUE-INVENTORY-20261019-5e23" \
      --sdk-scratch "$B/Scratch-R03-P1-OPAQUE-INVENTORY-20261019-5e23"

This attempt is consumed on PASS, FAIL, timeout, interruption or Blocked. **No retries, resumed child, alternate root/renamed suffix, vendor/compiler workaround or new runtime command**. Unknown command or descendant lifetime must stop later subprocesses; later scheduled components are NotRun without creating roots, and postflight Git/source subprocesses are prohibited until lifetime is established. Never convert an observed incomplete/failure receipt into success.

## Independent actual Local verification

Check all **16** cells, not the aggregate alone: command-failures, legacy-host, metadata-gate, bounded-class, bounded-physical, bounded-first-use, owned-general, live-general, owned-execution, empty-live, **opaque-inventory**, bounded-status, bounded-inventory, frozen-v2, managed-sdk and native-sdk.

A fresh PASS / PassedSourceHostAndSDKOnly requires 16/16 exact Passed outer cells, sourcePreserved=true, postflightError=null, stoppedAfter=null, all true expected SDK attempted/passed flags, exact four clean local and remote pins, original consumed evidence preservation, no historical reclassification and correct, authentic per-child RESULT/manifest/binary stdout+stderr receipts.

For opaque-inventory require PassedWithinInactiveOpaqueHostScope, exactly **two execution profiles × 18 unique test groups each** (strict, ASan/UBSan), five successful compiler-version/compile/run receipts with exit0, sourceMethodSha256 574ed4a99e7664686f2093cbf27a6c95df06e35440aef1c3331229aac2542152, exact original getter/API blob verification, stable input hashes, no partial output. It must actually test one, scattered and max-capacity **nonempty opaque identities**, duplicate/mismatched table refusal and same-count pointer replacement/relocation; no class field is dereferenced or serialized. Verify receipt explicitly states physicalClassPointerOriginProven=false, coherentVmEpochProven=false, completeExecutionSource=false, officialUnitySdkCompiled=false, UnityPlayerExecuted=false and runtimeAcceptance=false. This is NOT a complete class-type/source proof.

Retain all other component criteria: 70 distinct source-bound command-failure tests (5+14+29+10+12, no errors/skips), existing live-general 13 host cases per profile, owned-general 11, first-use 15, owned-execution 35 cases × 6 profiles, empty-live 20 × 2 plus original exact lifetime summary controls, original general/frozen-V2 negative cases and legacy exact byte parity. Managed compiler must independently produce five original DLLs and exact separate negative exit1/two CS0266/no DLL, with original canonical nested managed build-api/results.json binding. Native official SDK must independently compile **90/90 actual arm64 C++17 syntax configurations** = 18 distinct units × the five original profiles, including real full AssemblyShadow.cpp and the new opaque syntax probe. This is syntax only, not linked Player evidence. Preserve warnings and errors as actual observations, not copied expected totals.

Preserve original installed SDK and every consumed P1 raw result/manifest, scratch inputs, independent authority receipts, negative-control symlinks and historical source SHA binds before/after; verify evidence hashes and copies. No vendor binaries, no forged V1 raw or synthetic Player data. Local may update ONLY factual Handoff/LOCAL_VALIDATION.md, Handoff/RETURN_TO_WEB.md and the ONE additive checkpoint, with bounded environment-only diagnosis. Publish factual evidence and all four verified HEADs, without modifying native code/tests/compiler/tooling or old evidence.

## Stop / ownership / acceptance limits

**STOP** after this ONE scoped batch and return to Primary Implementation. Even a full PASS is NOT P1 global acceptance or a Human Review Gate. P1 physical class origin/lifetime, full nonempty execution rows/type keys, global VM atomic epoch/ABA, original getter integration, low-allocation/GC/RSS and Shutdown/lock safety remain Incomplete. P2 actual native+C# authenticated V2 transaction NotIntegrated; E0 vendor-supported StandaloneOSX engine owner-safe point Blocked/Unavailable; E1 callback drain/maintenance/restart BlockedByE0; full P3 linked Player/runtime Incomplete. Original SNAP-01/N/M/K/I/E and historic R02 fingerprint FAIL, strict S custody Blocked, full-stage R03 FAIL/re-review NotRun, report 500ms/1–64 uncapped original predicates and all V1/V2 budgets remain unchanged.

R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; PureInterpreter expansion disabled.
