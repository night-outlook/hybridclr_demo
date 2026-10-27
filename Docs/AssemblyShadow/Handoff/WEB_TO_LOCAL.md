# Primary Implementation -> Local Validation — ACTIVE R03 oneuse-C source-preserving capacity remediation

**ONE bounded source-projection attempt plus, conditionally, ONE new combined coordinator invocation.** This supersedes and consumes all execution authority in earlier oneuse-A and oneuse-B handoffs. Their factual Local BLOCKED checkpoints remain immutable: coordinator 0 and all ten R03 stages NotRun. No standalone Unity build, original-S replay, H2/M08A/X02, Human Review Gate or product acceptance is authorized.

## 1. Exact four pushed source repositories

Branch codex/assembly-shadow-r01b-h1. Verify clean owning checkout paths, full GitHub remote identity, submodules, live branch HEAD and absence of unrelated changes. The **full final pushed demo commit** is specified in the closing Primary-to-Local handoff prompt after this document is committed; that exact SHA is DEMO_COMMIT, not the older f2aa/e6e/f1b2 source anchors or original S fc55. Current Git file cannot embed its own eventual commit SHA.

| Repository | Pin | Previously observed path |
| --- | --- | --- |
| night-outlook/hybridclr_demo | latest pushed demo full SHA from final Primary handoff | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo |
| night-outlook/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr |
| night-outlook/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity |
| night-outlook/il2cpp_plus | e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus |

Read first:
1. Docs/AssemblyShadow/README.md and THIS WEB_TO_LOCAL.md.
2. Local-owned Handoff/LOCAL_VALIDATION.md and RETURN_TO_WEB.md, especially oneuse-B (capacity BLOCKED, dotnet resolved), oneuse-A and their immutable checkpoint/raw evidence.
3. Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_R03_ORIGINAL_S_SPARSE_CAPACITY_2026-10-26/{DESIGN.md,PLAN.md,PRIMARY_SOURCE_AUDIT.md,EVIDENCE.json}, and archived consumed oneuse-B handoff.
4. Earlier Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_R03_CURRENT_NATIVE_LOCAL_CYCLE_2026-10-26 source/evidence design, canonical R03 stage/Human Review Gates, Oct 8 independent R03 FAIL/erratum and owner D1=A/D2=A.

## 2. Exact retained fc55 auxiliary worktree and permitted change

ORIGINAL_S is the already-retained canonical path:
    /Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse

It MUST remain a singly registered, clean detached Git worktree at original S source commit fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b with canonical night-outlook/hybridclr_demo remote. Do not recreate, move, delete, force/prune, reset or repack this worktree; do not modify committed Git objects or external historical Local output roots. The historic S actual execution source demo29bb/native1cf87f, old R03 native74db and current e1e5 remain separate.

The **ONLY permitted source-environment mutation** is a one-time controlled Git sparse-checkout projection of this retained *auxiliary* clean fc55 worktree. It intentionally de-materializes unrelated clean TRACKED files outside the exact protected original-S checkpoint subtree from this worktree, while preserving original fc55 Git objects/history and the complete protected checkpoint byte-for-byte. Its lossless reversal would need sufficient future disk space and is NOT automatically authorized. No other history/cache/output deletion, Time Machine snapshot thinning, git gc, Git worktree removal, new full fc55 checkout, CLI installer, permanent PATH or resource/root purge is permitted.

Protected subtree:
    Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready

Source Git tree SHA2acdcc0ec3c0f15dea11f99bc9c5d6d0f431de79: exactly 16,978 regular Git files, 3,882,340,952 bytes of logical committed content. This is not a promised physical reclaim. The script verifies every physical protected file against Git before AND after conversion. A prior whole-worktree free-space decrease (~32 GiB) is a measurement, not wholly attributed to the worktree.

## 3. Phase A — bounded Git checkout projection (not a coordinator run)

Set WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r (or independently verified canonical actual source parent), ORIGINAL_S to retained fc55, DEMO_COMMIT to final closing handoff SHA. Verify no other agent/process is using or modifying the auxiliary original-S worktree. Confirm full Git registration/source pin and that it is currently a clean full checkout (not already sparse).

First run STRICTLY READ-ONLY inspect (no output path and no files written):

    PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/original_s_sparse_projection.py" --inspect --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --demo-commit "$DEMO_COMMIT"

Require exit0, result PassedReadOnlyInspect_NotAnExecution, exact 16,978/3,882,340,952 and pinned tree SHA, originalWorktreeSparseEnabled=false and all four current sources verified. A failure is SourceProjectionPrerequisiteBlocked; no sparse conversion or Unity invocation. Retain actual stdout/error externally as raw Local environmental evidence.

Select a NEW, absent, canonical external REMEDIATION_ROOT distinct from coordinator RUN_ROOT, current sources, original S and older evidence:
    /Users/ah/GitHub/hybridclr/r03-local-validation/R03OriginalS-SparseProjection-20261026-oneuse-C

Use it ONLY if currently absent and verified. If the intended path exists, STOP for Primary authorization; do not overwrite or pick retries. Then run EXACTLY ONCE:

    PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/original_s_sparse_projection.py" --apply --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --demo-commit "$DEMO_COMMIT" --evidence "$REMEDIATION_ROOT"

This command hashes all protected Git blobs (3.62 GiB logical data) before altering the checkout; writes INTENT; runs a single Git sparse-checkout set --cone --no-sparse-index for the one protected subtree; verifies all protected files again after; checks original fc55 registration, clean HEAD, exact sparse path and physical before/after free bytes. It produces REMEDIATION_ROOT/{INTENT.json,GIT_COMMAND.json,RESULT.json} with complete failure/raw status. Never manually repeat sparse conversion. If output indicates Failed/Incomplete, protected mismatch, remaining dirty Git state or incomplete receipt, STOP and return Primary with raw evidence. Do not automatically restore full checkout on a nearly full APFS container or launch the coordinator.

On success require result PassedBoundedSourceProjection_RequiresFreshCapacityAdmission, all 16,978 physical Git identities verified and original worktree clean/registered. Record the actual APFS/container/mount free bytes and projection policy as new environment evidence. A successful source projection does NOT itself give R03 acceptance or authorize Player execution.

## 4. Phase B — fresh storage and toolchain admission

The prior oneuse-B read-only admission failed on 19.858/19.840 GiB < fixed 20 GiB. Its alternative /Volumes/Data shares APFS container disk3 and is NOT extra space. Previous trusted .NET SDK is now discovered at:
    /Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk/dotnet
Source was SDK8.0.318, runtime8.0.21, osx-arm64; actually verify all three again and enable only this installed DotNetSdk directory on a process/session-local PATH for new toolchain commands. Unity Player itself must remain:
    /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
Verify genuine Unity 2022.3.62f2, lipo arm64, executable binary hash, clang++/lipo/python3/git and current source/pins. Do not install another .NET SDK or substitute the Unity6000 Editor/Player.

Choose ONE fresh nonexistent oneuse-C output root disjoint from all previous A/B/source/projection/evidence roots. Suggested:
    /Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-CurrentNativeOriginalS-20261026-oneuse-C
or a new independently mounted volume with actual separate free capacity. Do not create RUN_ROOT manually. Keep hard coordinator minimum MIN_FREE_GIB=20 unchanged. Due to three builds and five Players, **40 GiB post-projection is preferred as advisory** (not empirically proven consumption); if less than 40 GiB is free, do not autonomously begin expensive Player work on a marginal sample—publish fresh evidence and ask Primary for explicit go/no-go. Never infer that 20.01 GiB is sustainable.

Run the existing unchanged **READ-ONLY** admission, may be rechecked after safe environment preparation:

    PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/current_native_environment_admission.py" --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"

Requires exit0 and PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun with actual 20-GiB minimum, source/remote/physical fc55 Git, dotnet SDK8/runtime8 and Unity2022.3 checks. Record source/volume/APFS snapshots before and after. Preflight does not produce or modify RUN_ROOT. If anything fails, STOP and return PrerequisiteBlocked (coordinator0, all ten NotRun); do not use old A/B roots or manually run partial source/Player stages.

## 5. Phase C — ONE unchanged R03 ten-stage coordinator

ONLY if Phase A passed complete checkpoint preservation and Phase B passed source/toolchain/capacity admission with adequate headroom for the combined test, launch exactly ONCE:

    PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_current_native_validation_cycle.py" --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"

This is the exact original combined ten-stage validation (no retuned acceptance, no additional old roots): 20 source tests, 27 synthetic verifier tests, 12 changed-VM tests, 30 original-S host tests, 15 installed-native synthetic, original-S nine-part byte/90-cell historical archive, 59 archived process joins, native-host diagnostics, three new current-native e1e5 build roles and five fresh Unity arm64 Player cases, 126 changed VM installed-source byte pairs. Require actual post-poison managed entry attempts, no business method body side effect, stable terminal cause/recovery, healthy OFF control, native engine sentinel, request/nonce/PID/build and installation/Player binary provenance.

Never run oneuse-A/B, old S, b7e3/c42a/f51d, old R03 runner or any other source/Player batch. A used/partial C root is immediately consumed and cannot be retried. On failure preserve first error and all raw evidence. Even complete R03 focused evidence is at most FocusedEvidenceReadyForIndependentReview, NOT R03Accepted, runtimeAcceptance or an independent R03 PASS.

## 6. Required Local return and stop

Publish new additive receipts for the exact one-use sparse conversion, including full INTENT/GIT_COMMAND/RESULT and after-projection 16,978-file physical preservation; APFS bytes/mount state before/after and source/remote reauthentication; exact SDK8 CLI and Unity2022 binary; fresh read-only coordinator admission raw. If coordinator runs, preserve ADMISSION/RESULT/COORDINATOR_MANIFEST, ten stages and raw stdout/stderr/exit/PIDs/child cleanup, actual original S audit/90 cells/59 archived processes, native host diagnostics, three native builds, five Player raw/verifiers and 126 installed source byte pairs, generated/link evidence and all signed/sealed custody. Distinguish Passed/Failed/Blocked/NotRun/Unavailable and material gaps.

Update Local-owned Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md and RETURN_TO_WEB.md, add a new provenance-bound checkpoint under Docs/AssemblyShadow/History/M07R/R03, commit/push and independently verify all four final remote heads. Preserve oneuse-A/B, original S Git object history, b7e3/c42a/f51d/S historical evidence. No Local nontrivial production-source changes or arbitrary cleanup. STOP after factual publication and return to Primary.

Original Oct 8 independent full-stage R03 FAIL and High IR-R03-01/02 remain; D1=A conservative NativeLayoutAdmissionV1 / X02 deferred, D2=A observational performance and four contaminated Failed certificates unchanged. P1 incomplete; P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 incomplete; R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, qualificationApproved=false, runtimeAcceptance=false, PureInterpreter disabled. No H2/M08A/X02/SNAP-01/Human Review Gate without separate human initiation.
