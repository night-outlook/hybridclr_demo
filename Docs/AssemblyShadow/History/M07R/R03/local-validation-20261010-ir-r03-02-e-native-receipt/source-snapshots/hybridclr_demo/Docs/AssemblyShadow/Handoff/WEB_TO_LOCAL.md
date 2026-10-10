# Primary Implementation → Local Validation — IR-R03-02 E, repaired immutable C receipt

**ONE fresh E preflight is conditionally authorized. At most one E 14-cell/three-build/four-Player execution is authorized ONLY if all source, real receipt, full custody, fixture and storage checks pass.** The previous D result is `ScopedCustodyPreflightBlocked`, not a completed Player test, and must not be retried, altered or reclassified. The original R03 independent full-stage review remains FAIL.

## Read order

1. `Docs/AssemblyShadow/README.md`, `Plan/CURRENT_STATUS.md`, then this E `Handoff/WEB_TO_LOCAL.md`.
2. Local-owned `Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md`; historical [D checkpoint](../History/M07R/R03/local-validation-20261009-ir-r03-02-d-custody-scoped/README.md) and [C checkpoint](../History/M07R/R03/local-validation-20261009-ir-r03-02-c-custody-blocked/README.md), both unchanged.
3. [IR-LOCAL-CUSTODY-02 Primary source correction](../History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_02_2026-10-10/README.md), [machine-readable CI evidence](../History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_02_2026-10-10/EVIDENCE.json) and **[E exact validation procedure](../History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_02_2026-10-10/E_FOCUSED_LOCAL_PROCEDURE_2026-10-10.md)**.
4. [Original C scoped-loss disposition](../History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09/README.md), original S fixture policy, current-body C# API evidence, native design.
5. Original R03 design/plans, independent FAIL/C04 erratum, D1=A/D2=A decisions and HUMAN_REVIEW_GATES. Do not use historical D/B procedures as an execution authorization.

## Four exact owning source repositories

All four branches `codex/assembly-shadow-r01b-h1`. **Use the final pushed 40-character SHA tuple in the final Primary message**—not a provisional pre-documentation commit or the isolated CI branch. The actual Local checkout workspace is `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`.

| Repo | Actual owning path | Authority |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Exact final Primary pushed HEAD; Docs-only descendant of compiled API/Player anchor `ba47b41674b83a6f694ac4f8ac1bc8f83a9da24b` |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `9ce1c1bfec9a21b92ea300acda5f27a3815b2c37` |

All canonical remotes `https://github.com/night-outlook/<repo>.git` (matching SSH acceptable). Independently check each checkout top, branch, clean worktree, remote identity, `git rev-parse HEAD`, `git ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1`, submodules, and current `Tools/AssemblyShadow/R03/source-pins.json` non-demo pins. Never reset, stash, clean, force-push or use unrelated owner/control trees; mismatches block.

## Defect correction and independently compiled/tested source

D executed demo `7313c768a2658ae77357e3fb1a83e9542585c99c`, final D Local checkpoint publication `4d728038f562ddbf7e35564409e9d3b436c6772c`. The original `verify_scoped_custody.py` contained 53-character `NATIVE_LIVE_CUSTODY_LIMIT.json` SHA, while immutable C's true SHA-256 is **`5cf6365c3e84e5390868984b52a2f11cc8f52b40534de0fa53b92499d0359f9d`**, original Git blob `cca29fae8e0bbe7431d44b1f3f0eff96727c5756`. Before/after exit2 both occurred **before the full 416,844-file live scan**; D storage and Unity were NotRun.

Primary repaired `IR_LOCAL_CUSTODY_01_2026-10-09/verify_scoped_custody.py` and its adjacent regression tests in **Docs only**. The exact current Git blob IDs must be verified: verifier `ccc6af25d5d424b3bffe629ebd609ec5e5beed0a`; test `594b36b505721e246ffbcdbbfcb3037071626aad`. Every one of five original C JSON receipts now authenticates against its original SHA-256 **and** Git blob ID; pinned SHA/Git/map-part lengths are fail-closed. Five new tests read actual original C objects and parse its complete original 127MB/four-part map; ten original synthetic tests remain.

[Source-bound CI 38031146338](https://github.com/night-outlook/hybridclr_demo/actions/runs/38031146338), job `114152170509`, is **success** at verification-branch SHA `675930d9125b7ca11f183d857210e2934ae72ff7`: Python AST Passed; **15/15 real/synthetic tests Passed**; actual C native-limit SHA computed identically; full original map authenticated. The CI branch was created from corrected feature commit `81502a93b472e52f189969fb74bdf358b352cb07` and adds **only** its isolated workflow, so it cannot be used as an E source or execution commit. CI covered historical committed data, not Local surviving files/Unity/Player.

Current C# Player body remains source anchor ba47 and `R03TerminalPlayer.cs` Git blob `adc798c6c299594d496393c6729c4c6087111b31`, SHA256 `22c3e0be7cebc041706b1412c5fc317c806c49a0980be143d5517dc4cc59a7bd`. [Managed CI 37903041633](https://github.com/night-outlook/hybridclr_demo/actions/runs/37903041633) passed 0 errors/13 warnings on 22 tracked input hashes, package at exact pin, **using Unity API stubs**, not real Unity managed/Player execution. Do not infer that the new Docs-only CI qualifies as actual Unity native compile.

## Historical custody exception and all non-negotiable prerequisites

C strict protected custody **Blocked**, as preserved by Local: **416,844 expected; 339,367 present+hash-verified at C; 77,477 Missing; zero changed**. D never executed the fresh census. Twelve S Library/HybridCLRData groups and four receipt-bound installed-native roots are missing. Original S sealed archive of 587,907,380 bytes, SHA-256 `23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6`, and all 15,712 indexed files match, but do **not** contain the missing roots. Original S ran historical IL2CPP+ `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`, not current `9ce1`. Do not regenerate, replace, relocate or delete historical S native/cache bytes; do not call full custody or original installed-native provenance Passed.

The earlier **bounded Primary engineering exception remains limited to a new, independent IR-focused test only**. Run corrected verifier against the **exact original C** four map parts/two full reports/native-limit and **every still-present file**, before and after. The only scoped success is `ScopedHistoricalLossStable` with `originalStrictCustody=Blocked`, `presentVerified=339367`, `historicalStillMissing=77477`, same exact 77,477 original path+expected-SHA pairs, zero new/changed/symlink/partially scanned/restored; historical strict custody remains Blocked. An unexpected restoration, any byte change, new loss or incomplete scan must return Blocked and await Primary. New E project/native inputs must come solely from currently pinned source, not lost original S native installations.

## One fresh E session — four unused external candidates

Under `/Users/ah/GitHub/hybridclr/r03-local-validation/`, independently confirm all four are absent/nonsymlinked/nonaliasing and disjoint from protected or prior A/B/C/D roots. If any path exists, do not reuse, rename or invent an alternative—return Blocked for a new Primary designation.

1. `Preflight-R03IRLocal-20261010E-native-receipt` (new source/custody/host/CI receipts)
2. `R03IRLocal-20261010E-native-receipt` (new sealed 14-cell batch, absent until execution)
3. `StorageCheck-R03IRLocal-20261010E-native-receipt` (diagnostic only)
4. `Storage-R03IRLocal-20261010E-native-receipt` (independent execution session)

Read-only retained Q: `R03LocalBatch-20261006Q-lp-repair`. Unity `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, StandaloneOSX arm64, Python 3.14; Unity 6000 must not be launched.

Perform the **ordered exact commands** and receipt requirements in the [E procedure](../History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_02_2026-10-10/E_FOCUSED_LOCAL_PROCEDURE_2026-10-10.md):

- Verify all source/remote/pins, original S seal/fixtures and R/Q custody; authenticate 22 C# CI inputs and current Player.
- Fresh **15** custody tests (including real original-C receipt/map authentication), **64** R03IR host Python tests, native terminal policy **69** checks with exact C++17 flags.
- Before full 416,844-file C-frozen live custody scan **must** exit0 `ScopedHistoricalLossStable`; original strict remains Blocked; any other status forbids storage/Unity.
- Fresh diagnostic-only `run_terminal_storage_checked.py` **without** `--execute`, original `R03StorageAdmissionV1`, exact 64GiB admission `max(64GiB,2*Q+20GiB)`, 20GiB sampled floor, allocation/sync/readback probes and source/Q guard. Earlier C disk measurement is not current capacity.
- Only after all prerequisites pass, **one** new invoking session on distinct E `Storage` sidecar **with** `--execute` may launch exactly **14 cells/3 native builds/4 fresh Players**. Admission is remeasured. Do not retry or resume failure/blocked phases.
- Independently perform a full separate **after** scoped custody verification, regardless of runtime outcome where feasible; any new loss independently requires ReturnRequired even with successful Players. Preserve all raw errors/logs and do not rewrite D.

## Expected runtime witness and publication

In ON Players the same already-resolved active `Methods.R03.Node.Keep` reflection/delegate must actually execute twice pre-poison (42/42), instance primitive `stable` counter must read 0→2; then real caught baseline-owner or test-driven native type-resolution failure. All subsequent attempts (same active reflection, same delegate, ordinary reflected AOT canary) must be rejected without side effects, `stable` must remain **readable at 2**, AOT count unchanged, first-failure/recovery/state/generation/fixed diagnostics stable. OFF control executes ordinary reflected AOT canary twice with no transaction. Genuine captured-generic/initializer failures are NOT covered by these four Players.

Local owns `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`, plus one additive E checkpoint `Docs/AssemblyShadow/History/M07R/R03/local-validation-20261010-ir-r03-02-e-native-receipt/`, with exact 4-head Git identity, CI/current source bindings, all before/after custody, original S fixture+seal, storage/session/dispatch, 14 cell ledger, three build receipts, four real Player JSONs/logs, PID/nonce/request/build identities and index/archive/seal **only if executed**. Zero launches => all runtime cells/builds/Players NotRun, no invented seal. Local may fix isolated syntax/path issues only if source equivalence fully reestablished; otherwise return nontrivial changes to Primary. Publish all evidence in Git, verify remote heads, **stop after one E result and return to Primary**.

Historical S/R/Q/P/O/N and A/B/C/D reports unchanged; R staged/restore Failed, four contaminated warm certificates Failed, R02 CPU/RSS risks unaccepted. Independent R03 FAIL/re-review NotRun; captured-generic/initializer, IR-R03-01 and broad legacy acceptance remain pending. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`, PureInterpreter expansion disabled. Do not enter H2/X02/M08A or claim separate human approval.
