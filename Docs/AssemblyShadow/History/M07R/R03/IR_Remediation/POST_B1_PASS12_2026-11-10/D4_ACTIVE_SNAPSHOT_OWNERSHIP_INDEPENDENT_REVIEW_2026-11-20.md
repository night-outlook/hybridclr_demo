# R03 B2 D4 — Independent source/evidence review of process-owned ActiveSnapshot and P5/P6

**Decision: `PassD4ForNextGate` — BOUNDED TO D4 SOURCE/HOST.** Date: **2026-11-20 UTC**. This independent review covers only D4, including the recovery of the cancelled macOS CI job. It is not Primary self-approval, real Unity/IL2CPP Player acceptance, Local Validation authority, R03 acceptance, H2, or the Human Review Gate. The D4 checkpoint may advance to **planning/authorization of the next gate only**; do not start D5 Local execution without a separately approved handoff.

## 1. Exact source authority and independent evidence

All four repositories: `codex/assembly-shadow-r01b-h1`. Verified remote HEADs before publication:

| Repository | Source authority | D4 modifications |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | verified pre-report HEAD `5de8e3c9f9e4154b80770854ed1eab8992a3fec2`; **CI-tested code `c3307abacaaaec9db2a0f866b726e2ae5df1108b`** | D4 source-host tests/workflow; later documentation-only commits |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Unchanged D3 Runtime/Codec |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | Unchanged |
| `night-outlook/il2cpp_plus` | `3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699` | Three native paths detailed below |

D3→D4 GitHub compare `il2cpp_plus@40d9a16a6e357f0b3ad1cc93362a93cc41768258...3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699` reports **four commits, exactly three paths**, without touching D2 `Assembly.cpp`/`MetadataCache.cpp`, HybridCLR Runtime/Codec, source roster, Unity package, or the old V1/B1/R02 ABI:

- `libil2cpp/vm/AssemblyShadow.cpp`: blob `d1493c2d04b71a5ab99da94f21c13052a6cef2b1`.
- `libil2cpp/vm/AssemblyShadowProcessSnapshotOwner.h`: new blob `ccd10ea0a1d273f5fe31f52d346d090b0a5af79c`.
- `libil2cpp/vm/AssemblyShadowPublicationPhaseReceipt.h`: comment-only blob `e465434511b5896973db2a04c23bd8a11ef3cd4b`; phase values/logic unchanged.

I independently inspected the actual production source, D1 receipt and first-error/terminal policy, nested D2 publisher bodies, D3 observer-to-Codec chain, D4 test extractor and its 20 mutation cases, both host programs, the workflow, GitHub run metadata, job steps and all four raw final-attempt job logs. Reference documents were used for intent, not as substitutes for source: [D4 Primary design](D4_ACTIVE_SNAPSHOT_OWNERSHIP_PRIMARY_DESIGN_2026-11-19.md), [D4 Primary review](D4_ACTIVE_SNAPSHOT_OWNERSHIP_PRIMARY_REVIEW_2026-11-19.md), [D4 review request](D4_ACTIVE_SNAPSHOT_OWNERSHIP_INDEPENDENT_REVIEW_REQUEST_2026-11-19.md), [independent D3 pass](D3_INDEPENDENT_REREVIEW_2026-11-19.md) and [Approach A](B2_NATIVE_PUBLICATION_REMEDIATION_PREAPPROVAL_DESIGN_2026-11-18.md). The reviewer **did not** run a real Unity Player, native platform SDK, or full production translation-unit build.

## 2. Independent conclusions at the actual native boundaries

### D4-IR-01 — PASS/source: ownership precedes public pointer (critical D4 defect addressed)

`AssemblyShadow.cpp` declares `Transaction::activeOwner` as `ProcessSnapshotOwner<ActiveSnapshot>`. The existing `Current()` returns an intentionally never-deleted `static Transaction* transaction = new Transaction()`. The local `snapshot` remains `unique_ptr`-owned and unpublished during prevalidation and real Codec/Runtime P3/P4. `Publication` borrows both the raw pointer and the address of this pending `unique_ptr`; `PublishActive` validates these agree before transfer.

The actual `ProcessSnapshotOwner::TryPublish` in the new native header checks for null pending/already retained/already public. Only on success does it perform `retained_ = std::move(pending)`, then `published.store(retained_.get(), std::memory_order_release)`. The move of a default-deleter `std::unique_ptr`, `get()` and atomic pointer store have no allocating/throwing work between ownership and publication. The former unsafe `snapshot.release()` in the outer `CommitTransaction` was eliminated. A throw after the public store therefore cannot destroy that snapshot via the local `unique_ptr`.

The same source documents the process-lifetime assumption, and the host explicitly checks duplicate publish, null pending, already public pointer, persistent ownership after post-store failure, and no-exceptions header compilation. A host compiler test is **not** proof of native module unloading or VM/GC shutdown lifetime; these are reserved for Local Validation.

### D4-IR-02 — PASS/source: actual P5, P6 and Complete order

The unchanged HybridCLR Runtime still calls `beforeCodec` immediately before `Codec::PublishBatch` and `afterRuntimeGroup` only after `groups[group].active.store(1, release)`, so D3 P3/P4 receipts remain source-correct.

In the actual native `PublishActive`, `activeOwner.TryPublish` completes the *real* `s_active` release-store **before** `phaseReceipt->Advance(ActiveSnapshotPublished)` (P5). A failed P5 phase transition after the pointer store takes the existing D3 terminal-before-UsageUnlock path, without deleting the retained owner or claiming Codec rollback. A successful P5 marks `leaseExit=ActivePublished` and releases the usage lease.

The outer `CommitTransaction` constructs `ScopedPostActiveExit` before its first post-active `Event`, validates P5/InProgress and pointer/owner identity, then advances `InitializersRunning` (P6) immediately before the existing transaction lock release and initializer loop. After all explicit initializer successes, the normal state CAS to `Committed`, success `Event`, and `Result(Success)`, the actual `PublicationPhaseReceipt::Complete()` can seal the local attempt. It is not published as a process-global recoverable receipt or claimed proof of unrelated concurrent business method scheduling.

### D4-IR-03 — PASS/source with host support: explicit and unexpected postactive failure

`ScopedPostActiveExit` is a nonallocating/noexcept scope guard whose destructor is armed across postactive diagnostics and initializers. On unexpected exit it marks D1 terminal, attempts one-time `FirstErrorV2::TryFreeze` (without replacing an earlier event), release-stores `s_unexpectedFailure=true` and `FailedAfterCommit`, and **never** resets the active pointer or owner. It acquires no VM/metadata/transaction lock.

Explicit initializer errors and raced terminal guards retain the original `Result` and terminal error identity: their paths mark D1 terminal and only disarm the unexpected-exit guard **after** the normal `Result` completes; diagnostic throws on that path therefore still fail closed. The earlier D2/D3 `ScopedUnexpectedPublicationExit` covers a C++ exceptional unwind *inside the nested native publisher*, including the synthetic host `post-active-store-throw` scenario where the snapshot is already process-owned. No unexpected C++ exit was found that could delete a pointer already published to `s_active`.

### D4-IR-04 — PASS/bounded: D2/D3 old contracts and ABI unchanged

The D2 physical/CLI publisher and `dynamic_array.h` are unchanged, with D2 rollback/abandon callback still executed before outer assembly/metadata locks unwind. D3 usage lease seals terminal *before* release on Unknown failure, and the exact P0 `UsedBeforeAppend` remains the only retryable preappend branch. The new owner and guard do not introduce a new public managed method, change existing enum values or permit post-Codec rollback/retry. D4 retains the inactive B2 cap/roster/PureInterpreter and does **not** authorize H2 or new assemblies.

## 3. CI cancellation, exact rerun and raw evidence

[**GitHub Actions D4 run 44517874612**](https://github.com/night-outlook/hybridclr_demo/actions/runs/44517874612) at `hybridclr_demo@c3307abacaaaec9db2a0f866b726e2ae5df1108b`:

- **Attempt 1:** completed/**failure**; Ubuntu C++11/17 and macOS C++11 PASS; macOS C++17 **cancelled with no recorded job steps**. Its missing log is not reclassified as a failed native assertion; neither can that cancelled job count as executed.
- **Action:** GitHub Connector explicitly reran **only the cancelled macOS C++17 job**, preserving the original tested code SHA and other source pins, without committing or modifying production.
- **Attempt 2:** **completed/success, 4/4 job conclusions=success**. Verified new macOS C++17 job **`136149124210`** plus retained successful Ubuntu C++11 **`136149125866`**, Ubuntu C++17 **`136149172538`** and macOS C++11 **`136149126760`**. All four current-attempt job logs were read.

| Environment | Source tests | D2/D3/D4 + real Runtime/Codec host | No-exceptions owner/header host | No-owner negative control |
| --- | --- | --- | --- | --- |
| Ubuntu 24.04 C++11 | 20/20 PASS | 32 receipts, 724 assertions | 12 receipts, 171 assertions | Expected test failure observed |
| Ubuntu 24.04 C++17 | 20/20 PASS | 32 receipts, 724 assertions | 12 receipts, 171 assertions | Expected test failure observed |
| macOS 15 C++11 | 20/20 PASS | 32 receipts, 724 assertions | 12 receipts, 171 assertions | Expected test failure observed |
| macOS 15 C++17 | 20/20 PASS | 32 receipts, 724 assertions | 12 receipts, 171 assertions | Expected test failure observed |
| **Totals** | **80 tests** | **128 receipts / 2,896 assertions** | **48 receipts / 684 assertions** | **4 expected failures** |

Thus **176 passing host receipts / 3,580 assertions**. No unexpected host assertion, ASan, or UBSan failure in any successful job. The integrated 16 named cases/profile include P0 used closure, normal publish, Runtime precheck/actual Codec failure, post-group synthetic rejection, two D3 race/exception classes, prior first-error, post-active native throw, null/mismatched pending owner, postactive event/initializer faults, preservation of first error, handled initializer failure, and P6/Complete success. The owner-only host covers strict, ASan/UBSan, and `-fno-exceptions -fno-rtti` (four scenarios/profile). The expected-failing test-only owner-removal control is checked for a **nonzero result plus the intended host failure assertion** before recording the negative receipt.

**Provenance limits:** The integrated host compiles **22 extracted literal production bodies**, actual HybridCLR `InterpreterMetadataIndexRuntime.cpp` and Codec header, and real native CLI dynamic_array template with test-owned locks, VM/image types, allocation shims and synthetic fault producers. The entire native `CommitTransaction`, real IL2CPP/Unity VM translation units, live GC or platform Player were *not linked*. `-fno-exceptions` covers the reusable owner and D1 receipt, **not** the full native commit path. The Source receipt and mutation tests authenticate bodies/source order but do not turn mocks into Player proof.

## 4. Findings and exit decision

| Finding | Severity/status | Required next action |
| --- | --- | --- |
| **IR-D4-01 — raw public pointer before ownership** | **Critical original defect: CLOSED for D4 source-host** | Preserve immutable owner/process-lifetime in D5 native/Player tests |
| IR-D4-02 — P5/P6 and Complete order | **PASS/source-host bounded** | Validate real module initializer and concurrency path under authorized Local |
| IR-D4-03 — postactive unexpected exit, first error, terminal | **PASS/source-host bounded** | Verify real native exceptions/VM policy and recovery visibility during D5 |
| IR-D4-04 — D2/D3 regression and physical/CLI/Codec semantics | **PASS/source-host bounded** | Preserve exact tuple, avoid post-Codec rollback inference |
| IR-D4-05 — real Unity/IL2CPP/GC/native locks/32-bit ABI/shutdown | **HIGH / NotRun** | Mandatory separately authorized Local Validation; no product acceptance claim |
| IR-D4-06 — cross-thread Shadow method admission around P5/P6 | **HIGH / not established** | The owned pointer is publicly visible at P5; the host does not prove an external business method cannot race before P6. Preserve this explicit concurrent-reader risk for D5 rather than claiming whole-VM epoch coherence |
| IR-D4-07 — test ownership and source limitations | **Bounded** | Real full native translation-unit link, Unity platform memory model and first-recovery evidence still required |

**Independent judgment:** D4's authorization boundary is safe **ownership-before-publication**, P5/P6 source witness, and fail-closed local postactive paths. Source inspection and all four authenticated host jobs meet that limited checkpoint. IR-D4-06 is recorded as an **unproven real-VM concurrency boundary**, not a proved regression introduced by the ownership repair; it must be explicitly tested before product acceptance. This conclusion is **not** a blanket authorization for new shadow business execution before initializers or for release.

**Disposition: `D4IndependentReview=PassD4ForNextGate`**; `D1IndependentReview=WaivedByUser` (not Passed); `D2IndependentReview=PassD2ForD3`; `D3IndependentReview=PassD3ForD4`; `D4PrimaryImplementation=CompleteSourceHost`. D4 is closed for its **limited source-host milestone only**. **`D5LocalValidation=NotAuthorized`**, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`. A separate decision must authorize D5 planning and Local execution. No H2/M08A/X02/SNAP-01 or Human Review Gate self-approval.
