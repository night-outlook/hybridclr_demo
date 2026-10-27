# R03 retained original-S source projection — Primary source review (2026-10-26)

**Scope:** Primary code review and Mac/Linux host-only evidence for an environment capacity remediation. No actual original-S sparse projection on the user's Mac, no Unity/IL2CPP build, nine-part archive audit, R03 current-native Player, independent R03 reviewer or Human Review Gate.

## 1. Evidence authority and source pins

- Local oneuse-B was BLOCKED / PrerequisiteBlocked_Capacity and oneuse-A was BLOCKED / CapacityBlocked_CoordinatorNotRun. Both had zero coordinator invocations, all ten empirical stages NotRun and no Player/build. oneuse-B before/after capacity ~19.858/19.840 GiB on shared APFS container disk3; /Volumes/Data was not independent extra capacity.
- oneuse-B Local discovered usable .NET SDK8.0.318/Microsoft.NETCore.App8.0.21 osx-arm64 under installed Unity6000.5.3f1 DotNetSdk with process-only PATH. This is real read-only CLI evidence, not a build.
- Original retained fc55 path /Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse, commit fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b. GitHub original checkpoint tree SHA2acdcc0ec3c0f15dea11f99bc9c5d6d0f431de79 contains exactly 16,978 regular blobs (16,958 mode100644, 20 mode100755), 3,882,340,952 logical bytes.
- Development branch codex/assembly-shadow-r01b-h1, external pins hybridclr4b2774b066cfc6afd77a8c8aded6bda7ea574f55, hybridclr_unity948c0e3b4f8891481301770115e8ba4945eea6de, il2cpp_plus e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb. Demo must always be the final pushed handoff HEAD.
- Original R03 older native74db and historical S native1cf87f remain separate. No source pins/runtime modification.

## 2. Reviewed source and failure boundary

New original_s_sparse_projection.py pins the exact retained fc55 path, checkpoint subtree, committed tree SHA, file count and byte roster. It will not apply unless original is clean/detached/singly registered, four current sources/remote heads match and 16,978 checkpoint physical files are regular/nonaliased with original committed Git object bytes. It refuses dirty/untracked changes, submodules, symlinks, altered sources, existing evidence directory and repeat sparse execution. Its --inspect mode is strictly no-write.

The only permitted mutating command is Git sparse-checkout set --cone --no-sparse-index for the full pinned checkpoint subtree. Unrelated clean tracked materialization outside that subtree may be removed from this auxiliary worktree; original Git objects/history and protected checkpoint bytes are verified before and after. Reversing to full checkout is not automatic and may require the same large disk headroom. This physical de-materialization is an explicit bounded change, not a claim that the auxiliary worktree remains a full checkout.

INTENT.json is written under a previously absent external evidence root before the command. One command stdout/stderr/exit/timeout is preserved, without prune/reset/clean/gc or any retry. After it, the tool checks exact original HEAD, worktree registration/cleanliness, sparse projection, all four live remote/source identities and all protected physical file blobs. A failure preserves the partial receipt and stops. It never launches Unity, Player or an original-S archive audit, and never claims runtime acceptance. Actual APFS space reclaimed is measured rather than inferred.

Original-S audit_s_provenance.py and audit_s_process_joins.py remain unchanged and consume the committed original checkpoint subtree and new external audit output. Primary inspected the source call path and found no known read-only audit dependency outside that checkpoint, but genuine sparse checkout and complete archive/semantic validation remain Local tasks.

## 3. Host CI and prior test correction

The first CI attempt for the new 31 temporary-Git host tests FAILED on both macOS/Linux: Git ls-tree -l pads file-size fields, but the initial parser used literal-space splitting. Primary corrected it to whitespace tokenization while keeping source mode/blob/size/path/count requirements. Preserve the initial CI test FAIL; it was not product/runtime failure.

Corrected [GitHub CI 40442802143](https://github.com/night-outlook/hybridclr_demo/actions/runs/40442802143) completed SUCCESS on macos-15 (job121986872486) and ubuntu-24.04 (job121986872320), each **180 host-only tests** with no failures: 31 new sparse Git custody, 20 coordinator, 15 installed-native source synthetic, 25 retained-fc55/net8/capacity, 20 candidate-source, 27 verifier synthetic, 12 VM-delta source and 30 original-S host. Both raw CI job logs were examined separately. Tests use tiny temporary Git repositories to exercise real sparse materialization, Git-object preservation and rejection cases; they do not touch the actual fc55 checkout or prove APFS reclamation.

## 4. Limits and next phase

- Actual retained fc55 has NOT been sparsified. Physical space recovery, APFS snapshots/clones, capacity admission and ability to complete three Unity builds remain unknown. The Git checkpoint's 3.62 GiB is logical content, not a physical disk-use guarantee.
- Ten empirical R03 stages, current exact-native builds/Players, original nine-part archive/59 process crosswalk and physical 126 installed source pairs remain NotRun. CI is host-only and does not prove full compiled/linked native source.
- Existing 20-GiB minimum is unchanged. A 40-GiB advisory post-projection headroom is a risk buffer, not a measured build lower bound.
- b7e3/c42a overall Local FAIL, f51d historical-only PASS, S historical 90/90, D1=A conservative V1/X02 deferral, D2=A observational performance and contaminated Failed performance certificates remain fixed. Oct 8 independent full-stage R03 FAIL and High IR-R03-01/02 remain. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, runtimeAcceptance=false, qualificationApproved=false, PureInterpreter disabled; no H2/M08A/X02/SNAP-01.

Next source-frozen oneuse-C handoff authorizes one controlled checkout projection only, followed by new source/capacity/toolchain admission. Only a genuinely passing admission can permit the unchanged ten-stage coordinator to run once in a fresh oneuse-C output root.
