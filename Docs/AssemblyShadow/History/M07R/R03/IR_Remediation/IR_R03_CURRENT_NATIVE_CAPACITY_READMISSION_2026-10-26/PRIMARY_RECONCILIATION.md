# Primary reconciliation — oneuse-A capacity BLOCKED and oneuse-B preparation (2026-10-26)

**Author:** Primary Implementation; not independent reviewer, Local operator or Human Review Gate. **Source basis:** verified published oneuse-A Local-owned RETURN_TO_WEB.md and LOCAL_VALIDATION.md, immutable checkpoint README.md, FINDING.json, LOCAL_RESULT.json, STAGE_STATES.json and raw worktree/capacity/toolchain receipts at night-outlook/hybridclr_demo@542078a801463b29d234d4221800e6ec7fab27d4. Four current remote HEAD identities confirmed against that return prior to editing. Original source/IR player/native tools are unchanged.

## Reconciliation findings

1. IR-LOCAL-CURRENT-NATIVE-ORIGINAL-S-CAPACITY-01 is a **true environment admission BLOCKED**, not a failing Unity native implementation test. The after-worktree free sample was 21,074,190,336 bytes (19.63 GiB) against 21,474,836,480 bytes (20 GiB) hard threshold. The later 21,783,199,744 bytes (20.29 GiB) observation was passive and not a new admission. Exclusive storage-causality is unproven; the approx 32 GiB drop cannot be claimed entirely as steady-state worktree cost. Primary does not alter the hard threshold.
2. oneuse-A execution was **never dispatched**: coordinator invocations 0, all 10 stages NotRun, 0 Unity/SDK/build/Player launches, 0/126 physical VM comparisons, all coordinator and child final receipts Unavailable_NotProduced. Do not publish any fabricated Failed/Passed downstream result. Prior Source/remote pins, preserved SDK/history hashes and Unity arm64 discovery stay separately Passed within Local preflight scope.
3. An actual secondary readiness issue is independently recorded: executable dotnet missing on PATH. Primary inspected the exact R03 PlayerFixtures.csproj and verified TargetFramework=net8.0, fixed Git blob 6bd02a765a53d9fc1830d1026f2b02710172a092. The next Local stage cannot assume net8 SDK or runtime just because clang/Unity are available. No software installation or toolchain repair has occurred in Primary or original oneuse-A Local.
4. The **existing retained** detached worktree /Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse at fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b is permitted **only** as read-only historical input after a fresh independent check of registration, HEAD, clean status, origin, 15-part fixture identities where applicable and exact original archive authority. This does not change original S executed/native tuple. No new fc55 worktree creation or cleanup is authorized.
5. The old oneuse-A output root/name and active WEB_TO_LOCAL have been consumed by this preflight BLOCKED; the new operation requires a **distinct oneuse-B** root and new pushed four-source tuple. Only a fresh no-write prerequisite check may precede its unique coordinator invocation.

## Primary implementation and test scope

- Added source-only current_native_environment_admission.py: requires a singly registered clean retained fc55 worktree, unchanged exact source/remote tests and actual arm64 Unity 20-GiB gate, unique new output; validates net8 fixture Git blob, dotnet SDK >=8, Microsoft.NETCore.App 8.x runtime, CXX and lipo. Does not create/write a worktree, project, batch or result. Reports read-only prerequisites, not build/runtime success. A reported RID is observation, not native source proof.
- Added current_native_environment_contracts.py (25 explicit host-only adversarial tests) and updated the existing R03 Mac/Linux source-only CI to execute them alongside the previous 124 host-only tests. No change to original coordinator stages, product/native C++, Player fixture, S archive, previous source-pin or negative/verifier semantics.
- Existing native coordinator MIN_FREE_GIB remains **20**. Advisory >=30 GiB after worktree is a conservative buffer recommendation, not a demonstrated required capacity nor an unconditional reason for a PASS. An alternate output volume is preferred if sustainably available. No automatic deletion, cache pruning or root overwrite is supported.

## Provenance and acceptance boundaries

New read-only environment CI:
- commit source: 1d79ef9cfb52a45a8c7465aa39b0c50b8cfb707f (demo only, before final handoff documentation);
- GitHub Actions run 40438909487, completed success on macos-15 and ubuntu-24.04;
- 149 tests per platform: 20 coordinator, 15 VM physical parity synthetic, 25 retained-worktree/SDK/capacity, 20 exact native candidate source, 27 verifier synthetic, 12 changed VM source and 30 original S provenance-host;
- **no actual Local retained-worktree recheck, .NET installation, original S archive reconstruction, Unity 2022.3.62f2 compile or current-native Player execution**. This source CI is not acceptance.

The original October 8 independent R03 full-stage review remains FAIL, High IR-R03-01/IR-R03-02 still open. Original S historical Local 90/90, b7e3/c42a overall Local FAIL, f51d historical evidence-only PASS, D1=A conservative V1 / X02 deferred, D2=A observational-only performance and contaminated failed warm certificates remain fixed. P1 incomplete, P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 incomplete. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, qualificationApproved=false, runtimeAcceptance=false; PureInterpreter disabled.

**Next state:** conditional read-only re-admission of the retained fc55 with disk/toolchain on actual Local host, then exactly one new explicitly pinned oneuse-B batch only if all prerequisites pass. A prerequisite Blocked result does **not** authorize trying the old A command/root or redefining failed history. Local writes its own factual returns; Primary owns any nontrivial source corrections; independent full-stage review and Human Review Gate require separate human initiation.
