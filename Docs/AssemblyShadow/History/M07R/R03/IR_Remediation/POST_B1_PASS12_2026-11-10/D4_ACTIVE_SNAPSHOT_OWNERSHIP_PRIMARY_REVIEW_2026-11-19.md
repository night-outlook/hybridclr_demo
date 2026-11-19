# R03 B2 D4 — Primary Implementation review: process-owned snapshot and P5/P6

**Status at initial publication: D4 production implementation complete; current exact-code source-host CI 2/4 PASS, macOS jobs queued. Independent D4 review NOT performed.** Date 2026-11-19 UTC. Only D4 was authorized by the [independent D3 PassD3ForD4](D3_INDEPENDENT_REREVIEW_2026-11-19.md). This is a **Primary** report, not independent approval, Local Validation or Human Review Gate.

## 1. Source authority, branch and change inventory

All four repositories on `codex/assembly-shadow-r01b-h1`.

| Repository | Exact tested source revision | D4 change scope |
| --- | --- | --- |
| `night-outlook/il2cpp_plus` | `3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699` | `libil2cpp/vm/AssemblyShadow.cpp`, new `AssemblyShadowProcessSnapshotOwner.h`, D1 receipt comment-only update |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Unchanged since D3 |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | Unchanged |
| `night-outlook/hybridclr_demo` | **test/workflow code `c3307abacaaaec9db2a0f866b726e2ae5df1108b`** (documentation commits separate) | 2 C++ host tests, 1 Python extractor, 1 mutation suite, 1 GitHub Actions workflow, design/review docs |

The native compare from approved D3 source `40d9a16a6e357f0b3ad1cc93362a93cc41768258` to D4 `3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699` shows **4 commits/3 native paths only** (no D2 assembly/metadata registry code, no Codec/Runtime, no Unity package, no source roster). D4 blob pins: `AssemblyShadow.cpp=d1493c2d04b71a5ab99da94f21c13052a6cef2b1`, `AssemblyShadowProcessSnapshotOwner.h=ccd10ea0a1d273f5fe31f52d346d090b0a5af79c`, `AssemblyShadowPublicationPhaseReceipt.h=e465434511b5896973db2a04c23bd8a11ef3cd4b`.

## 2. Primary code review against approved approach A

Detailed design: [D4_ACTIVE_SNAPSHOT_OWNERSHIP_PRIMARY_DESIGN_2026-11-19.md](D4_ACTIVE_SNAPSHOT_OWNERSHIP_PRIMARY_DESIGN_2026-11-19.md).

**D4-PI-01 (source pass):** The existing `Current()` implementation allocates `static Transaction* transaction = new Transaction()` and never destroys it. `Transaction` now contains `ProcessSnapshotOwner<ActiveSnapshot>`, which owns a `std::unique_ptr<ActiveSnapshot>`. The pending local `snapshot` remains the only owner before P4; immediately before native active release-publication, `TryPublish` validates the pending pointer, moves its ownership into `Transaction::activeOwner` and then release-stores `activeOwner.get()` into `s_active` with **no throwing operation between move and store**. `snapshot.release()` has been eliminated from the outer CommitTransaction. This prevents the documented dangling pointer when a throw occurs after the store but before the former local release.

**D4-PI-02 (source pass):** After real Runtime/Codec group P4 and owner/publication succeeds, the native callback advances to P5/ActiveSnapshotPublished. A phase error after publication is terminal before UsageLock releases, and the snapshot remains transaction-owned. `ScopedPostActiveExit` is constructed before any potentially allocating diagnostic Event; it first verifies `s_active` matches process ownership and P5/InProgress, then records P6 before the existing lock-unlock/init boundary. Only after actual initializer completion, state CAS to Committed and success diagnostics does `PublicationPhaseReceipt::Complete` succeed.

**D4-PI-03 (source pass with empirical limits):** If a post-active diagnostic or initializer path unexpectedly returns/throws without explicitly disarming the guard, the guard marks the receipt terminal, attempts to freeze `FirstErrorV2` without replacing an existing first cause, sets `s_unexpectedFailure=true`, then `s_state=FailedAfterCommit`. No process-owned snapshot is destroyed or rolled back. On deliberately handled initializer/guard failures, the original `Result` and error origin are retained; the guard disarms only after `Result` returns, so a diagnostic throw is still terminal. On exceptional exit from the nested native publisher after active publication, its existing D2/D3 outer guard marks receipt and terminal state; the already transferred snapshot remains owned.

**D4-PI-04 (no observed D3 regression in inspected paths):** Verified old D2 `ScopedCliRollback` and `ScopedPhysicalRollback` implementation and UsageLock release ordering untouched. Used-closure P0 retry remains nonterminal; Runtime/Codec phase P3/P4 placement and D3 early terminal sealing are unchanged. New snapshot owner has no ABI-visible state, no new managed method/enum, no automatic restart and no Codec rollback claim. The B2 inactive feature and existing capacity limits remain unchanged.

## 3. Source-host tests and provenance

[Current exact-source D4 CI 44517874612](https://github.com/night-outlook/hybridclr_demo/actions/runs/44517874612) tests demo source `c3307abacaaaec9db2a0f866b726e2ae5df1108b`, pinned native and HybridCLR revisions above. At this report's initial publication, **Ubuntu 24.04 C++11/C++17 jobs passed, macOS 15 C++11/C++17 jobs remained queued**. Each completed Ubuntu job was independently read back as:
- **20/20 Python source and negative mutation tests** (exact source HEADs and blob hashes; 22 native/HybridCLR extracted bodies and precise D2/D3/D4 sequencing).
- **32 passing integrated host scenarios / 724 assertions** under strict `-O2` + ASan/UBSan. Real pinned HybridCLR Runtime.cpp/Codec.h, exact D2 physical/CLI source bodies and real `dynamic_array.h`, D3 callbacks and D4 owner/guards compiled with **test-owned VM/OS locks/allocator**. Distinct scenarios: safe P0, native normal success, Runtime precheck and real Codec rejection, synthetic real-group refusal, pre/post-group exceptions, prior first-error, **post-active native throw**, null/mismatched pending owner after real group store, post-active event/initializer exceptions, existing first-error preservation, explicit handled initializer error and P6 Completed success. Five D3 race cases still exercise the forced two-thread barrier.
- **12 passing no-exceptions owner/header executions / 171 assertions** under strict, ASan/UBSan and `-fno-exceptions -fno-rtti` (four cases/profile). These compile the exact D4 `ProcessSnapshotOwner` and D1 phase receipt, **not** complete native Runtime or Unity production TUs.
- **One expected failing test-only control** omits the owner move and verifies the regression host rejects the resulting non-owned public state; no production source was changed by the control.

**Interim verified total: 40 Python tests, 64 integrated host receipts / 1,448 assertions, 24 owner-header receipts / 342 assertions, and two expected-failing old-owner controls**. No ASan/UBSan error in the two completed Ubuntu job logs. **This is not yet a 4/4 CI pass**; superseded failed attempts are preserved with their original GitHub status. The first D4 CI attempt had a Python test syntax error, and the next failed the source receipt's outdated body-count threshold. Neither was a passing run.

Do not promote mock-host evidence to Unity/IL2CPP Player, real baselib/FastAutoLock, GC/whole-VM epoch, native 32-bit atomics/ABI, shutdown/finalizers, V1 field14/15 parity or actual first-recovery empirical acceptance. Those remain **NotRun** and require a separately authorized Local Validation cycle.

## 4. Primary findings, review gate and status

| ID | Severity | Disposition |
| --- | --- | --- |
| D4-PI-01 — owner acquired after Codec group but before public pointer | Pass / source; source-host evidence partial | Confirm all 4 jobs and external native lifetimes at authorized Local stage |
| D4-PI-02 — P5/P6 and Complete strictly ordered | Pass / source; source-host evidence partial | Verify exact phase and exception paths in final logs |
| D4-PI-03 — unexpected post-active exit terminal; first error retained | Pass / source; source-host evidence partial | Exact current host tests and independent review required |
| D4-PI-04 — original D2/D3 behavior retained | Pass / source | Real native/ABI validation deferred |
| D4-PI-05 — real Unity/IL2CPP Player, actual OS locks/GC/VM and 32-bit | **High / NotRun** | Only later explicitly authorized Local Validation |
| D4-PI-06 — manual/human milestone gate | NotAuthorized | No D5, H2, M08A, X02, SNAP-01 or Human Review self-approval |

**Initial disposition:** `D4PrimaryImplementation=SourceCompleteCIPartial`, `D4IndependentReview=Pending`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`. Once all four final-source jobs genuinely pass, independently audit their logs and append a clearly labeled complete-evidence update, then request **independent D4 review**. Do not begin D5 automatically.
