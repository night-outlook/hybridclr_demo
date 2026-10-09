# Primary Implementation → Local Validation — IR-R03-02 D, exact-loss scoped custody

**Scope: one new D preflight, followed by at most one new D 14-cell/3-build/4-Player batch only if ALL current gates pass.** Prior C returned `CustodyBlocked` with 77,477 retained S files Missing, 0 Unity launches and all runtime cells NotRun. **This is an explicit Primary-only scoped exception for new independent IR evidence, NOT recovery, not strict historical custody PASS, not S reacceptance, not Human Review Gate approval.** Do not retry C.

## Read order

1. `Docs/AssemblyShadow/README.md`; `Plan/CURRENT_STATUS.md`; this current handoff.
2. Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` (original C findings and exact receipts preserved).
3. [IR-LOCAL-CUSTODY-01 Primary disposition](../History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09/README.md) and [D full procedure](../History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09/D_FOCUSED_LOCAL_PROCEDURE_2026-10-09.md), including checked-in verifier and ten negative controls.
4. [C immutable checkpoint](../History/M07R/R03/local-validation-20261009-ir-r03-02-c-custody-blocked/README.md); [current-source C# API correction](../History/M07R/R03/IR_Remediation/IR_LOCAL_API_01_2026-10-09/README.md); [original S fixture authority](../History/M07R/R03/IR_Remediation/IR_R03_02_FIXTURE_PROVENANCE_2026-10-09.md).
5. Original R03 design/plan, independent full-stage FAIL/C04 erratum, D1=A/D2=A decision and HUMAN_REVIEW_GATES. Do not infer permissions from old B/C procedures or conversation history.

## Exact authority and owning checkouts

All branches: `codex/assembly-shadow-r01b-h1`. **Use the latest pushed four-SHA tuple in the final Primary handoff**, verifying the exact file/authenticated source hashes and remote tip again before work. Demo is a Docs-only descendant of compiled current-Player source `ba47b41674b83a6f694ac4f8ac1bc8f83a9da24b`. Other three HEADs and `Tools/AssemblyShadow/R03/source-pins.json` remain:

| GitHub repository | Actual owning path | Fixed commit |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Final handoff SHA only; Docs-only descendants since ba47 |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `9ce1c1bfec9a21b92ea300acda5f27a3815b2c37` |

Origin identities are `night-outlook/<repo>` (HTTPS or same SSH). Verify path, branch, clean worktree, submodules, HEAD, source manifest, fresh `git ls-remote`. Never reset/stash/clean unrelated state or force-advance a mismatched checkout. Canonical GitHub Connector has verified remote writes.

## Prior Local facts, Primary disposition and provenance limit

C Local execution source `e6f918bf6c756251982eef47f255eaa71b11e1d4`, immutable report publication `36b9828d62bb81d98e81d055871a9540fe116276`. Source/API, 64 Python tests, 69 native-policy checks and 15 original S fixture blobs Passed. Fresh diagnostic storage Admitted at 83,657,576,448 bytes versus 68,719,476,736 required, eleven probes Passed, but no execution. **Strict C custody Blocked**: 416,844 expected / 339,367 present verified / **77,477 Missing**, 0 changed; four historical S installedNativeRoot trees absent.

Original S sealed evidence remains authenticated (587,907,380 byte archive, SHA-256 `23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6`; 15,712 indexed files). Missing S caches and historical native roots are *outside* the archive and cannot be restored from it. S built with historical IL2CPP+ `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`, not current `9ce1`. **Original source/build/process semantic provenance is NOT fully reauthenticated**. Do not fabricate native recovery by using new IL2CPP+ bytes. Original S90Passed, retained R staged/Failed restoration, all A/B/C reports and Q/P/O/N remain factual and unchanged.

Primary decides **only** that an unchanged historical missing set may be carried forward as explicitly *ScopedHistoricalLossStable* during fresh independent IR-R03-02 testing, subject to independent hashing of **all 416,844 frozen C map entries** before/after execution. The helper must return exactly **339,367 present byte-verified and 77,477 missing**, with unchanged 12-group missing path/hash identities, zero new/changed/symlink/partial scan and original C reports/map/native root limits authenticated. Require `originalStrictCustody=Blocked`; **NEVER mark strict custody Passed or rebaseline the missing files**. A changed/partially restored previously missing item also blocks until new Primary disposition; no automatic exception widening. Fresh executable must neither consume nor modify S Library/HybridCLRData.

## New D root candidates, conditional execution

Use macOS arm64, Unity 2022.3.62f2, Python3.14 and exact current source. Under `/Users/ah/GitHub/hybridclr/r03-local-validation`, verify each of these is **unused, not a symlink, not aliasing/nested**; otherwise Blocked/NotRun, return to Primary for distinct roots.

- `Preflight-R03IRLocal-20261009D-custody-scoped`
- `R03IRLocal-20261009D-custody-scoped`
- `StorageCheck-R03IRLocal-20261009D-custody-scoped`
- `Storage-R03IRLocal-20261009D-custody-scoped`

Retained read-only Q: `R03LocalBatch-20261006Q-lp-repair` in the same parent. C and all old roots MUST be preserved. First run current CI source equivalence against pinned C# compilation [CI 37903041633](https://github.com/night-outlook/hybridclr_demo/actions/runs/37903041633), original S five top artifacts/index, 15 Git S inputs, 64 host Python/69 native tests and the ten additional verifier negative tests. The C# compilation used net8/C#9 with real pinned package but Unity API **stubs**, not official Unity Player. A green status alone is insufficient.

Use the exact new D [procedure](../History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09/D_FOCUSED_LOCAL_PROCEDURE_2026-10-09.md). The Primary-owned Docs-only `verify_scoped_custody.py` checks entire immutable C checkpoint/map and independently SHA-256-hashes every original present file. Require complete pre-scan `ScopedHistoricalLossStable`/exit0 with explicit historical strict Blocked; separately record normal full-historical custody remains Blocked.

Only after ALL non-storage prerequisites qualify, run `run_terminal_storage_checked.py` **without** `--execute` for the fresh D diagnostics-only sidecar. Enforce original `R03StorageAdmissionV1`, bound Q, `max(64GiB,2*Q+20GiB)`, 20GiB running floor, owned probes/cleanup, no threshold/quota/temp/snapshot changes. Previous C available space is not current proof. Only after current diagnosis Admitted/exit0 and `batchStarted=false` may **one** independent `--execute` wrapper with the new D execution sidecar initiate exactly 14 scheduler cells / 3 builds / 4 fresh Players. Recheck admission afresh; failure or capacity rejection stops, no phase retry/resume. Run independent full-scope **after** census and preserve separate post-run custody failures, even if Players passed.

## Exact Player evidence, Local publication and stopping rules

ON Players: same active `Methods.R03.Node.Keep` reflection and delegate return 42 twice with real `stable` instance counter 0→2 before failure; actual caught baseline-owner or test-driven native type-resolution poison; state FailedAfterCommit; post-poison attempts of same reflection/delegate and ordinary reflected AOT canary rejected, no active or AOT counter increment; **readable private field still 2** and unchanged first failure/recovery/native fixed diagnostics. OFF must run normal AOT reflective canary twice without a Shadow transaction. Genuine captured-generic and initializer-failure scenarios remain outside this subset.

Publish full source/CI/fixture, separate strict historical custody versus scoped D before/after receipts, Q/R/S archive/authentication, capacity/session/dispatch, 14 cells and actual three builds/four Player raw results if run, PID/nonce/request/argv/build/source joins and index/archive/seal. If no runtime was launched, report zero launches and all runtime rows NotRun; never manufacture a seal. Update only Local-owned `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` and additive `Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-d-custody-scoped/`. Commit/push/verify remote; **stop and return to Primary**. Small local command fixes only; any meaningful design/provenance risk returns to Primary.

**Acceptance flags remain false:** R03Accepted=false, H2Passed=false, qualificationApproved=false, ReadyForHumanReviewGate=false, fullLegacyRegressionAcceptance=false, PureInterpreter expansion disabled. Independent full-stage review remains **FAIL**, rereview NotRun; missing historical S native-root custody is an unresolved full-review risk. No H2/X02/M08A/release or performance SLA approval.
