# Independent D4 decision — PassD4ForNextGate, bounded source-host (2026-11-20 UTC)

[**Independent D4 review published**](D4_ACTIVE_SNAPSHOT_OWNERSHIP_INDEPENDENT_REVIEW_2026-11-20.md): **`D4IndependentReview=PassD4ForNextGate`**, D4 source-host only. This supersedes the earlier request's "Awaiting CI/independent decision" as **current** authority; the historical request remains below unchanged for audit. [CI 44517874612](https://github.com/night-outlook/hybridclr_demo/actions/runs/44517874612) **attempt 2** is completed/success, 4/4 jobs; 80 Python tests, 176 source-host receipts / 3,580 assertions, and four expected-failing no-owner controls. Attempt 1 remains failure with cancelled macOS C++17 (no job steps). Source pins: demo tested `c3307abacaaaec9db2a0f866b726e2ae5df1108b`, hybridclr `c3c232023724cbad565b85e9b2c3beea8ce2789a`, hybridclr_unity `948c0e3b4f8891481301770115e8ba4945eea6de`, il2cpp_plus `3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699`. This does **not** authorize Local Validation, Unity/IL2CPP/Player, D5 execution, R03 acceptance, H2, or Human Review Gate; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`. Remaining high-risk real VM/GC, 32-bit ABI, shutdown and P5/P6 cross-thread method-entry behavior are explicitly deferred to a separately authorized Local gate.

---

# D4 review request: complete exact CI now available (2026-11-20 UTC)

**`ReadyForIndependentD4Review`**, not independent approval. [GitHub Actions run 44517874612](https://github.com/night-outlook/hybridclr_demo/actions/runs/44517874612) **attempt 2 completed/success, 4/4 jobs** at exact demo code `c3307abacaaaec9db2a0f866b726e2ae5df1108b`; original cancelled macOS C++17 in attempt 1 remains historical failure. Actual rerun macOS C++17 job `136149124210` succeeded. Four current job logs have been fetched and checked: **80 Python tests, 176 host receipts / 3,580 assertions, four expected-failing no-owner controls**, no unexpected native assertion/sanitizer reports. Use the [updated Primary evidence](D4_ACTIVE_SNAPSHOT_OWNERSHIP_PRIMARY_REVIEW_2026-11-19.md), then independently read actual pinned native/HybridCLR source and host logs; do not merely endorse Primary's report.

**Source tuple:** `hybridclr_demo@c3307abacaaaec9db2a0f866b726e2ae5df1108b` **tested code** (later docs-only branch HEAD separate); `hybridclr@c3c232023724cbad565b85e9b2c3beea8ce2789a`; `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`; `il2cpp_plus@3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699`. D1 waived (not Passed), D2 passed, D3 independent `PassD3ForD4`. **Only choose `PassD4ForNextGate`, `ReturnRequired`, or `Blocked` after independent source/host review.** No D5/Local/Player/H2/Human Review authorization, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`.

**Original pre-CI-completion request retained below for provenance.**

---

# R03 B2 D4 — independent review request: process-owned snapshot/P5/P6

**Status: PreparedAwaitingFullSourceHostCI; no independent D4 decision yet.** Date 2026-11-19 UTC. Review only D4. Do not start D5, Local Validation, H2, M08A, X02, SNAP-01 or the Human Review Gate.

## 1. Authority and exact source tuple

All four repositories branch `codex/assembly-shadow-r01b-h1`:

| Repo | Fixed source commit | Key evidence |
| --- | --- | --- |
| `night-outlook/il2cpp_plus` | `3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699` | `libil2cpp/vm/AssemblyShadow.cpp` (blob `d1493c2d04b71a5ab99da94f21c13052a6cef2b1`), `AssemblyShadowProcessSnapshotOwner.h` (blob `ccd10ea0a1d273f5fe31f52d346d090b0a5af79c`), D1 receipt comment-only blob `e465434511b5896973db2a04c23bd8a11ef3cd4b` |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Unchanged real Runtime/Codec P3/P4 |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | Unchanged |
| `night-outlook/hybridclr_demo` | **D4 tested code `c3307abacaaaec9db2a0f866b726e2ae5df1108b`**, documentation HEAD tracked separately | 20 source tests; integrated D2–D4/Runtime host, no-exceptions owner host, CI |

Source design and Primary evidence:
- [D4 Primary design](D4_ACTIVE_SNAPSHOT_OWNERSHIP_PRIMARY_DESIGN_2026-11-19.md)
- [D4 Primary implementation/evidence review](D4_ACTIVE_SNAPSHOT_OWNERSHIP_PRIMARY_REVIEW_2026-11-19.md)
- [D3 independent `PassD3ForD4`](D3_INDEPENDENT_REREVIEW_2026-11-19.md)
- [Approach A](B2_NATIVE_PUBLICATION_REMEDIATION_PREAPPROVAL_DESIGN_2026-11-18.md)

Compare native D3→D4 `40d9a16a6e357f0b3ad1cc93362a93cc41768258...3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699`: exactly **four commits/three native paths**, with no new HybridCLR or il2cpp_plus D2 registry changes. Source roster, managed ABI, inactive B2 limits and PureInterpreter startup behavior remain unchanged.

## 2. CI entry and acceptance condition

[**D4 CI 44517874612**](https://github.com/night-outlook/hybridclr_demo/actions/runs/44517874612) must be independently verified as **completed/success for all four jobs** (Ubuntu24.04/macOS15 × C++11/C++17), not merely because the Primary report says it passed. At document creation, **Ubuntu C++11 and C++17 had passed**, while both macOS jobs were queued. Do not approve this re-review until the final source-pinned CI matrix is complete and all four raw job logs have been read.

The workflow `.github/workflows/r03-b2-d4-snapshot-ownership.yml` checks exact Git HEADs, file blob hashes, 22 extracted native/HybridCLR production bodies, the original `dynamic_array.h` template, two compiled C++ source-hosts and a synthetic **expected-failing no-owner negative control**. Per fully passing job, expect **20/20 Python source mutation tests**, **32 integrated host executions / 724 checks** under strict/ASan+UBSan, **12 no-exceptions owner-header executions / 171 checks** under strict/ASan+UBSan/`-fno-exceptions -fno-rtti`, plus a verified negative-control failure. If 4/4 passes, expected total **80 source tests, 176 host executions / 3,580 checks, four expected-failing test-only controls**. These are **expected counts**, not recorded as completed evidence until logs are authenticated.

## 3. Independent questions and exact source scope

1. **Ownership-before-store:** Inspect the actual `Current()` process-lifetime `static Transaction*`, new `Transaction::activeOwner` owner type, pending `unique_ptr`, `PublishActive` validation and `ProcessSnapshotOwner::TryPublish`. Prove the move into process-lifetime `unique_ptr` happens **before** `s_active.store(release)` with no throwing operation between. Confirm pre-publication rejection never leaves a dangling `s_active` pointer, and post-publication exception cannot free a publicly visible snapshot. Audit whether shutdown/embedded-module lifecycle invalidates any lifetime assumption.
2. **Phase fidelity:** Verify original D3 P3/P4 remain authentic Runtime/Codec boundaries; native P5 `Advance` happens after actual published pointer; P6 happens only at initializer execution boundary; `Complete` only after state Committed and successful initializer/diagnostic path. Confirm a failed phase witness cannot return a false success or retryable state.
3. **Normal/error/exception matrix:** Inspect null/mismatched pending owner after actual Runtime group, P5 rejection, precodec failures, exception *after* native active store but before outer CommitTransaction return, post-active Event throw, initializer throw, handled initializer error, final commit recording failure and success. Check D2 physical/CLI rollback and D3 terminal-before-UsageUnlock on all relevant exits; never claim Codec lifecycle reversal.
4. **First-error and terminal policy:** Confirm FirstErrorV2 CAS protects the earliest event and no new allocating diagnostic runs under metadata/usage locks; `s_unexpectedFailure`/FailedAfterCommit gate business execution when postactive diagnostics or initializers throw. Handled initializer failures must preserve the original `Result` return cause instead of being mislabeled unexpected failures.
5. **C++ ABI and lock correctness:** Inspect D2→D4 diff for unintended changes; default-delete `unique_ptr` move noexcept property, atomic release/acquire and target-dependent lock-free behavior, concurrent readers, VM metadata lifetime, real baselib/FastAutoLock and 32-bit/OS shutdown. Clearly mark Unity/Player/GC integration **NotRun**, not PASS.
6. **Test independence:** Read `extract_d4_snapshot_ownership.py`, `test_extract_d4_snapshot_ownership.py`, `D4SnapshotOwnershipHost.cpp`, `D4SnapshotOwnerNoExceptionsHost.cpp`, the workflow and *all final job logs*. Distinguish 22 literal production bodies and real Runtime.cpp/Codec from host-owned VM objects, fake locks, synthetic exceptions, and the no-exceptions header-only profile. Confirm the test-only negative control actually fails on a missing owner move, not merely compiles.
7. **Gate boundaries:** Do not conflate a D4 source-host pass with D5/Local authorization, final R03 acceptance, H2 or Human Review Gate. Preserve D1 waived/D2 pass/D3 pass, inactive B2 capacities and the exact source pins, V1/B1/R02 obligations and remaining Local work.

## 4. Required reviewer disposition

Only after complete evidence independently verified, choose **`PassD4ForNextGate`**, **`ReturnRequired`**, or **`Blocked`**, with exact scope, findings, and open Local/production evidence. A D4 pass is **not** itself authority to run Local Validation unless a separately approved D5 handoff is issued under the project's gates.

**Current authority:** `D1IndependentReview=WaivedByUser` (not Passed), `D2IndependentReview=PassD2ForD3`, `D3IndependentReview=PassD3ForD4`; `D4Implementation=InProgress`, `D4IndependentReview=Pending`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`.
