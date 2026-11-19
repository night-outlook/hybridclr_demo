# R03 B2 D4 — Process-owned ActiveSnapshot and P5/P6 completion

**Primary Implementation design record; D4 NOT independently approved.** 2026-11-19 UTC. Working branch: `codex/assembly-shadow-r01b-h1`. Only D4 scope is authorized by [independent `PassD3ForD4`](D3_INDEPENDENT_REREVIEW_2026-11-19.md). No D5, Local Validation, H2, M08A, X02, SNAP-01, R03 acceptance, Unity/IL2CPP Player or Human Review Gate execution is authorized.

## 1. Problem and required invariant

Before D4, `AssemblyShadow::PublishActive` release-stored a raw `ActiveSnapshot*` into `s_active` while `CommitTransaction` still owned it via local `std::unique_ptr`. That pointer could dangle if native unwinding destroyed the local owner before the later `snapshot.release()`. A post-active exception during diagnostics or initializers also lacked a single guard spanning P5 through completion. D1 phase P5/P6 and `Complete` had not been integrated into the real production chain.

**Invariant A — ownership-before-publication:** A published `s_active` pointer is retained in an owning object with lifetime at least as long as all process-global native readers, **before** the public release-store. There must be **no throwing operation** between ownership acquisition and the store. A pre-ownership rejection must not publish an active pointer. If a fault occurs after publication, the retained owner must remain live and the process must become terminal, not retryable.

**Invariant B — phase fidelity:** P5 may be recorded only after the actual `s_active` release-store. P6 is recorded at the boundary immediately before dropping the transaction lock and entering the initializer loop. `Complete` may be set only after all initializers, terminal guard checks, state transition to `Committed`, and success diagnostics return. Earlier P3/P4 Runtime and Codec witnesses remain unchanged.

**Invariant C — terminal monotonicity and old contracts:** Any unexpected exit after P5 must preserve the first error, seal D1 receipt to `TerminalRestartRequired`, set a durable terminal flag and `FailedAfterCommit`, and **never free** the published snapshot. Explicit initializer/guard failures retain their original error semantics; an unexpected native exit must not overwrite a previously frozen first error. Keep D2 physical/CLI rollback and D3 pre-UsageUnlock sealing, P0 used-closure retry, source roster, ABI and B2 capacities unchanged. D4 does not implement a reverse Codec/group transition or auto-restart.

## 2. Ownership approach and why it is suitable

**Selected:** a no-throw, one-time `ProcessSnapshotOwner<ActiveSnapshot>` field inside the existing `Transaction` returned by `Current()`. `Current()` constructs `static Transaction* transaction = new Transaction()` and never deletes it; this explicit process-lifetime allocation already exists. The `ProcessSnapshotOwner` holds a `std::unique_ptr<ActiveSnapshot>` and publishes its owned `get()` to an `std::atomic<const ActiveSnapshot*>` after move assignment. It performs no allocation, managed call, lock acquisition, VM operation or user callback.

The prebuilt, privately held `std::unique_ptr` remains local in `CommitTransaction` until `PublishActive` has witnessed real Codec/Runtime P4 success. The synchronous publication context borrows `&snapshot`, and verifies that its owner and expected raw pointer agree. Then:

1. Reject if the pending owner is null, a snapshot is already retained, or `s_active` is already public; do **not** move ownership on refusal.
2. Move `snapshot` into the process-lived `Transaction::activeOwner` using nonthrowing `std::unique_ptr` default-deleter move assignment.
3. Release-store `activeOwner.get()` into `s_active`, with **no intervening throwing operation**.
4. Advance the actual attempt receipt to P5. If it unexpectedly refuses, seal the process terminal **before** releasing UsageLock; the already published snapshot remains owned.
5. Mark the existing `ActivePublished` normal-success lease exit, then release UsageLock. D2 physical/CLI publisher returns normally.

**Rejected alternatives:**
- Publish raw pointer first then call `snapshot.release()`: existing dangling-pointer defect.
- `snapshot.release()` before store without a retained owner: no dangling pointer but an unmanaged leak with no explicit owner/retention witness; inferior for auditing and shutdown tests.
- Copy/move an existing native `ActiveSnapshot` value after publication: breaks immutable pointer identity and may allocate/throw or invalidate its published maps.
- Attempt a reversible Codec/group transition on failure: violates the D0–D3 approved fail-closed design.

The `Transaction` lifetime assumption is a source contract, not proof that a third-party embedder never manually unloads the entire native module. Exact Unity/Player shutdown and 32-bit memory/atomic semantics remain Local Validation tasks.

## 3. Post-active phases, exceptions and handled failures

Immediately after `PublishInterpreterAssembliesBatch` reports success, `CommitTransaction` constructs an allocation-free, `noexcept` `ScopedPostActiveExit` guard, before any `Event()` or module-initializer preparation can throw. It checks that the receipt is P5/InProgress and that the process-owned pointer matches `s_active`. Failure seals terminal with `SnapshotOwnershipUnverified`, not `Validated`.

The real `Event("active-published")` occurs while P5 remains current. `Advance(InitializersRunning)` records P6 immediately before the existing `lock.unlock()`. The guard remains armed across all initializer calls and records/commit-order/diagnostic work. On unexpected normal early return or C++ unwind, its destructor marks D1 terminal (`NativePublicationFailure` if before P6, `InitializerFailure` if after), attempts to freeze `FirstErrorV2` with `UnexpectedFailure` origin **without overwriting an earlier event**, then release-stores `s_unexpectedFailure=true` and `s_state=FailedAfterCommit`. It never deletes or releases the process-owned snapshot and acquires no metadata/transaction locks.

Explicit initializer and late-guard failures retain the existing `Result()` return codes and their first-error/recovery producers. They mark the D1 receipt terminal, and disarm the post-active exceptional guard **only after** `Result()` returns (thus an exception from diagnostics is still terminal). On the successful path, `Committed` is recorded by the original compare/exchange, followed by `Event("transaction-committed")`, `Result(Success)`, and finally D1 `Complete()`; only then is the guard disarmed and success returned. Invalid P6/`Complete` progression is terminal. No new managed-visible enums, V1 fields or public APIs were introduced.

The `ScopedUnexpectedPublicationExit` guard spanning D2/D3 publication also marks D1 terminal on native unwinding, including a hypothetical exception after P5 and before the outer return; the snapshot is already process-owned.

## 4. Source and test surface

Production changes restricted to `night-outlook/il2cpp_plus`:
- `libil2cpp/vm/AssemblyShadowProcessSnapshotOwner.h`: reusable C++11 no-throw template, no VM dependency.
- `libil2cpp/vm/AssemblyShadow.cpp`: process-lived owner field, borrowed pending-owner pointer, real owner-before-store handoff, P5/P6 and successful `Complete`, post-active terminal guard, direct normal/exception branch handling and accurate phase documentation.
- `libil2cpp/vm/AssemblyShadowPublicationPhaseReceipt.h`: documentation-only correction of historical D1 comments. The state-machine implementation remains unchanged.

`hybridclr`, `hybridclr_unity` and the D2 native assembly/metadata registry files remain unchanged.

New `hybridclr_demo` validation-only source:
- `extract_d4_snapshot_ownership.py`: exact Git HEAD/blobs, source contract checks, 22 literal native/HybridCLR function/type bodies; real CLI `dynamic_array.h` pinned by Git blob.
- `test_extract_d4_snapshot_ownership.py`: 20 positive/source mutation tests covering ownership order, duplicate/adversarial owner, P5/P6, `Complete`, first-error/terminal guard and D2/D3 path retention.
- `D4SnapshotOwnershipHost.cpp`: actual pinned Runtime.cpp/Codec.h, exact D2 physical/CLI publishers, D3 native callbacks/first-error/phase and D4 exact owner and post-active guard, with host stand-ins for Unity locks, VM/image objects and synthetic faults.
- `D4SnapshotOwnerNoExceptionsHost.cpp`: exact owner and D1 headers under strict/sanitized/`-fno-exceptions -fno-rtti`, including static `noexcept` API checks, duplicate-publish/invalid-owner and P5/P6 terminal/success paths.
- `.github/workflows/r03-b2-d4-snapshot-ownership.yml`: Ubuntu 24.04/macOS 15 × C++11/C++17. Includes a test-only negative control suppressing the owner's move before publication. No Unity, IL2CPP Player, Android/iOS or SDK commands.

## 5. D4 exit criteria and acceptance limits

Before issuing an independent D4 review request, Primary must inspect *completed*, source-pinned GitHub Actions job metadata and raw logs, report each scenario/condition separately (including negative-control expected failure), fix test/production defects found, and publish exact four-repository source pins. A passing source-host matrix is **necessary but not sufficient** for real Player/VM acceptance.

Required D4 host scenarios include safe P0 rejection, ordinary committed snapshot, a real Codec validation error, real group publication with callback refusal, null/mismatched pending snapshot after actual group commit, C++ unwind before Codec and after group, exceptional unwind after `s_active` publication, post-active diagnostic/initializer exceptions, explicit handled initializer failure, first-error preservation, P6/`Complete` success, and a non-allocating no-exceptions owner-header profile. D3 two-thread ordering regressions remain covered.

**After D4 host completion:** Stop for an **independent D4 review**. Do not start D5 or publish a new Local Validation handoff until authorized by the independent gate and all project-defined prerequisites. At this design checkpoint, `D4Implementation=InProgress`, `D4IndependentReview=NotStarted`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`.
