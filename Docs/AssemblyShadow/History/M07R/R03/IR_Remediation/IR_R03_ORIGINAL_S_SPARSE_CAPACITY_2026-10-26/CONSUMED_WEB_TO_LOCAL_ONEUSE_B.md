# Primary Implementation -> Local Validation — ACTIVE one-use R03 oneuse-B (retained original S)

**Authorization: ONE NEW coordinator invocation after fresh, read-only environment admission.** Earlier oneuse-A remains BLOCKED / CapacityBlocked_CoordinatorNotRun, coordinator 0, all ten stages NotRun, no Unity/Player/SDK execution. Its original output root/name is consumed. This handoff authorizes read-only reuse of the retained clean fc55 worktree after re-verification, not a second worktree creation. It does not authorize H2/M08A/X02/SNAP-01, a Human Review Gate, R03 acceptance or production release.

## 1. Four authoritative GitHub repositories and Local roots

Branch for all four: codex/assembly-shadow-r01b-h1. The **latest pushed full demo HEAD is specified in the final short Primary-to-Local prompt** after this document is committed; that exact remote HEAD is the authoritative DEMO_COMMIT (a Git document cannot embed its own eventual commit SHA). Other three fixed SHAs:

| Repo | Source pin | Prior Local checkout |
| --- | --- | --- |
| night-outlook/hybridclr_demo | full newest pushed SHA from final handoff | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo |
| night-outlook/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr |
| night-outlook/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity |
| night-outlook/il2cpp_plus | e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus |

WORKSPACE previously /Users/ah/GitHub/hybridclr/assembly_shadow_h1r. ORIGINAL_S: **retain** /Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse (clean, registered, detached fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b). No recreation, pruning, resetting, repacking, moving or deletion. The old native 74dbdbea80d83923863303bd2b2c0a87f36541b1 in R03/source-pins.json and original S native 1cf87f8209790f9fb2ebec97487dc1990ccd56c5 remain separate history. Verify all actual paths, ownership, canonical origin, branch, clean tracked and untracked status, and live GitHub remote HEAD; previous paths are factual Local observations, not newly inspected by this web agent.

## 2. Read first and required Primary design

Read:
1. Docs/AssemblyShadow/README.md and THIS WEB_TO_LOCAL.md.
2. Local-owned Handoff/LOCAL_VALIDATION.md, RETURN_TO_WEB.md, latest oneuse-A checkpoint at Docs/AssemblyShadow/History/M07R/R03/local-validation-current-native-original-s-20261026-oneuse-a, including FINDING.json, LOCAL_RESULT.json, STAGE_STATES.json, capacity, original-worktree, TOOLCHAIN and preservation receipts.
3. Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_R03_CURRENT_NATIVE_CAPACITY_READMISSION_2026-10-26/{DESIGN.md,PLAN.md,PRIMARY_RECONCILIATION.md,EVIDENCE.json}; archived previous oneuse-A WEB_TO_LOCAL for historical reading ONLY.
4. Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_R03_CURRENT_NATIVE_LOCAL_CYCLE_2026-10-26/{DESIGN.md,PLAN.md,PRIMARY_SOURCE_REVIEW.md}, canonical R03 stage, Human Review Gates and current status.
5. The October 8 independent R03 full-stage FAIL and erratum, IR-R03-01/02, RC1–RC6 and D1=A/D2=A owner disposition.

Confirmed prior oneuse-A: before-worktree free 55,757,221,888 bytes (51.93 GiB), immediate after-worktree 21,074,190,336 bytes (19.63 GiB), which violated fixed minimum 21,474,836,480 (20 GiB). Later passive 21,783,199,744 bytes (20.29 GiB) was NOT readmission. dotnet --list-sdks was missing on PATH; R03 PlayerFixtures.csproj targets net8.0. Unity 2022.3.62f2 arm64 was discovered, but no Player launched. Do not relabel any blocked/historical evidence.

## 3. Required newly verified Local prerequisites BEFORE coordinator

1. Re-authenticate exact four latest pushed clean source HEADs, canonical remotes/branch/submodules, ten current candidate blobs and 42 VM Git blobs. Check no unrelated modifications or conflicting active Unity/IL2CPP/Player processes in the isolated workspace.
2. Re-authenticate the **existing** original-S fc55 path as singly registered detached clean worktree through Git. Do not run a second git worktree add. Original S full archive will be checked by the later separate read-only original-S audit stage.
3. Unity executable previously discovered at /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity is valid only if independently rechecked (Hub/Info.plist, lipo arm64, hash). Require actual python3, clang++, lipo and git.
4. Resolve the prior missing .NET prerequisite: a trusted actual dotnet command on PATH, SDK >=8 **plus Microsoft.NETCore.App 8.x runtime**, to compile and run pinned net8.0 PlayerFixtures. Local may discover and enable an **already installed** suitable toolchain with process-only PATH changes, recording its binary, hash/version/RID and actual list-sdks/list-runtimes. If absent, return ToolchainPrerequisiteBlocked BEFORE coordinator. No automatic new system installation, persistent PATH change, source/SDK semantic modification or skipped net8 checks.
5. Select a **new physically canonical absent output root** outside all source/worktree/history roots. Preferred output parent: independent high-capacity volume with comfortable free headroom (**30 GiB+ advisory, not a verified consumption bound**). The actual coordinator hard minimum remains **20 GiB**, unchanged. A single borderline 20.29 GiB historical sample is not evidence of durable build capacity. If source volume remains marginal, choose and independently verify another mount and its permissions/free bytes; never clean historical archives, Git/Unity caches or old roots to create room automatically. Record fresh available bytes/mount/unique root before launching. Suggested new label if absent: /Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-CurrentNativeOriginalS-20261026-oneuse-B, or use a distinct new root on a verified larger volume. **Never oneuse-A**, even if physically absent.

## 4. No-write readmission, then exactly ONE new ten-stage execution

Set WORKSPACE, ORIGINAL_S, UNITY_EXE, DEMO_COMMIT (the final full pushed demo SHA in the closing short prompt), and RUN_ROOT as independently verified above. Never create RUN_ROOT manually. The following new read-only preflight may be repeated ONLY to verify a bounded environment prerequisite repair; it does NOT create a batch/worktree or execute Unity:

    PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/current_native_environment_admission.py" --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"

Require exit 0 and result PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun, plus independent Local source, toolchain and fresh capacity checks. Save stdout/stderr, exact CLI/toolchain/volume snapshots and timestamps OUTSIDE the still absent RUN_ROOT and all consumed/protected roots. A source/toolchain/disk failure is PrerequisiteBlocked, coordinator zero; do not run a partial stage as a workaround.

ONLY after successful fresh readmission invoke this command **once and once only**:

    PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_current_native_validation_cycle.py" --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"

Coordinator independently repeats branch/remote/source/Unity and >=20 GiB checks and creates a NEW root if eligible. Never run old R03/source-pins, oneuse-A, S/b7e3/c42a/f51d, original native commands or manually retry this root. Any failed/incomplete new root is consumed; preserve it and return to Primary.

## 5. Required ten stages and results — scope unchanged

1. source-contracts: 20 current source/pin host tests.
2. oracle-contracts: 27 actual-verifier synthetic host tests (not Player).
3. vm-delta-contracts: 12 actual 42-file native VM source host tests.
4. original-s-host-contracts: 30 historical provenance host tests.
5. installed-source-host-contracts: 15 source/install synthetic host tests.
6. original-s-audit: read-only nine-part authentic archive (587,907,380 bytes, SHA256 23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6), 15,713 members, immutable 90-cell original S ledger.
7. original-s-process-joins: 59 original archived Player/command/request/PID/build-identity joins, no historical runtime replay.
8. native-host-diagnostics: diagnostic stream/codec/transaction/legacy sink and strict/sanitized native host tests if compiler available.
9. current-native-players: exactly three e1e5 Release/Debug/OFF fresh builds and five actual Unity 2022.3.62f2 macOS arm64 Players (release/debug baseline poison, release type poison, OFF healthy control, engine unhandled). Require actual post-poison reflection/delegate/AOT canary attempts, no body-field/canary increment, original first-failure/recovery stability, native report, process/nonce/build/installed source and binary identity.
10. native-installed-source-audit: 42 current native VM files matched byte-for-byte in three role-specific physical installed native trees = 126 pairs. Installed byte parity is NOT a proof of full transitive C++ source inclusion or binary linkage.

Do not promote historical outcomes from original S 90/90, b7e3/c42a overall Local FAIL, f51d historical audit-only PASS, D1=A conservative V1/X02 deferred or D2=A observational-only performance. No early success of a subset can erase another Failed/Blocked/NotRun. At most FocusedEvidenceReadyForIndependentReview, not product/runtime acceptance.

## 6. Local deliverables, boundaries and stop

Publish an additive Local checkpoint (never overwrite oneuse-A): raw read-only preflight with retained fc55 registration, fresh capacity/device/timestamps, dotnet/clang/Unity provenance, four clean source/remote pins; coordinator ADMISSION.json, RESULT.json, COORDINATOR_MANIFEST.json; all ten stage INVOCATION/RESULT/stdout/stderr/PID/exit/timeout/hashes; original-S archive and 90-cell/59-process receipts, host diagnostics, 3 build receipts and installed source/binaries/generated C++ materials, all five Player requests/launch/raw/log/verifiers, 126 physical source pairs if reached, after-preservation and child sealing. Distinguish Failed, Blocked, NotRun, Unavailable and scoped Passed accurately. Capture full first error; preserve consumed prior roots.

Local may perform bounded verified environment corrections such as a temporary PATH to an already installed SDK, NOT nontrivial source/native/architecture changes, threshold weakening, unapproved new software installation, evidence reinterpretation or multiple batch roots. For a missing toolchain/space prerequisite stop before coordinator and report. For coordinator failure retain the fresh root and report ReturnRequired; no automatic retry. Update **Local-owned** Handoff/LOCAL_VALIDATION.md and RETURN_TO_WEB.md, commit/push factual evidence and verify remote, then STOP and return to Primary.

## 7. Unchanged independent review / Human Review Gate

The October 8 independent R03 full-stage **FAIL** and High IR-R03-01/02 remain open. Captured generic/module initializer/virtual/interface paths and full compiled/linked binary closure still require independent consideration beyond five focused Players. P1 incomplete, P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 incomplete. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, qualificationApproved=false, runtimeAcceptance=false; PureInterpreter disabled. D1=A/D2=A and contaminated Failed performance certificates unchanged. No Human Review Gate, H2, X02, M08A, SNAP-01 or further milestone until separate explicit human initiation and actual stage exit conditions.
