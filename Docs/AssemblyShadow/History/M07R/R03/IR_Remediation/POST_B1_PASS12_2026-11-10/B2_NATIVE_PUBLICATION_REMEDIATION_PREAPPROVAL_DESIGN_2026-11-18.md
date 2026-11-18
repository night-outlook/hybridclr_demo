# R03 B2 — Native publication remediation: pre-approval design and gated plan

**Status:** PROPOSED, NOT APPROVED. **Date:** 2026-11-18 UTC. This document defines a candidate correction for the proven host-level exception gaps, without authorizing production changes or Local Validation.

**Inputs:** exact-source [native visibility review](B2_NATIVE_PUBLICATION_VISIBILITY_BOUNDARY_REVIEW_2026-11-18.md), [pinned native-body exception host](B2_EXTRACTED_NATIVE_EXCEPTION_HOST_REVIEW_2026-11-18.md), and [actual Runtime/Codec post-group fault host](B2_NATIVE_ACTUAL_RUNTIME_POST_GROUP_FAULT_REVIEW_2026-11-18.md). The current production pins remain il2cpp_plus@cecf4b859d50b128e5c0fc6c90cd89e3a452b96a, hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55 and hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de.

## 1. Problem statement and invariant

The native callback chain currently holds:

transaction.mutex → g_MetadataLock → s_assemblyLock → manually acquired UsageLock → InterpreterMetadataIndexRuntime reservationMutex → Codec mutex.

Normal callback return handles registry rollback and unlock. Exceptional return is not covered by the manually transferred UsageLock or by the registry false-return branches. An actual Runtime group can be published **before** the native active snapshot is visible. Returning to Validated or retrying from that point is not a proven reversible operation.

**Required invariant:** after the earliest irreversible Codec Lifecycle::Published store, no failure path may assert that the publication was rolled back or retryable without an independently proven reverse transition. When the outcome of a Codec invocation is unknown, the failure is **terminal for this process**; only a new process may attempt clean initialization. This must not be confused with an automatic application restart.

Secondary invariants:
- preserve exactly once source ownership and published TypeDef identities;
- no executable baseline fallback after a terminal publication failure;
- unwind UsageLock in correct nested lock order on all supported exceptional exits;
- do not publish s_active until snapshot ownership is permanently retained;
- preserve the first failure and recovery reason without requiring allocation or managed execution while sensitive locks are held;
- keep V1/B1/R02, source/registration roster, feature flag and B2 capacity unchanged.

## 2. Phase model and safe/unsafe transitions

A prototype phase receipt **must be attached to the *actual* publication call chain**, not inferred from the final boolean return:

| Phase | Observed entry point | Permitted failure classification |
| --- | --- | --- |
| P0 Prepared | CommitTransaction snapshot and registry reservations, no mutation | Validated may be preserved if full cleanup proven |
| P1 Usage admitted | TryBeginPublication true, UsageLock acquired | Precodec error only if both registries and usage lease have been properly unwound |
| P2 Registries appended | Both physical and CLI entries inserted under their respective locks | Precodec cleanup only if no codec attempt and complete rollback proved |
| P3 Codec attempted | Immediately before calling real Codec::PublishBatch | Unknown/exception outcome ⇒ TerminalRestartRequired |
| P4 Codec/group published | Runtime publication-group.active release-store completed | Any failure ⇒ TerminalRestartRequired, never claim original private state |
| P5 Native active snapshot published | s_active release-store completed | Any failure ⇒ terminal post-commit state; snapshot must remain owned |
| P6 Initializers running | CommitTransaction drops transaction lock after publication | Existing FailedAfterCommit/first-error behavior must remain monotonic |

This is a **design state machine**, not a claim that the production code currently records these phases. A phase receipt must be updated before each potentially irreversible action using storage prepared before acquiring the transaction/metadata/assembly locks. A returned error from Codec without explicit attempt/rollback evidence must not be silently interpreted as untouched state.

## 3. Candidate approaches

**A. Phase-aware terminal fail-closed (recommended candidate; requires approval).** Add a bounded publication receipt, distinguish proved precodec rejection from unknown-after-codec-attempt outcome, ensure native callback exceptional cleanup and UsageLock custody, and mark any uncertain or postpublication error terminal with restart required. No aggressive rollback claim after P3. This is the simplest candidate aligned with current monotonic metadata design.

**B. All-or-nothing rollback after Codec publication (not recommended without new proof).** Would require reversing Codec Lifecycle::Published, publication-group identities and all exposed/deferred metadata references and ensuring no concurrent readers saw the state. Current stable, monotonic Codec/VM design and source-host results **do not provide such a proof**. Reject as a scope expansion unless independent architectural evidence supports it.

**C. Global no-throw enforcement without recovery handling (insufficient alone).** Preallocate all vectors, move all allocations out of critical sections and audit every caller and native lock primitive. This may reduce exception probability but does not prove impossibility, and it fails to provide an explicit terminal response to out-of-contract exceptions. Apply as a supporting invariant, not as a substitute for A.

**Proposed choice:** A, subject to Human Review approval specifically for cross-repository native publication semantics. No production implementation is performed by this document.

## 4. Native exception ownership sketch — review required

A TryBeginPublication-local RAII variable is **incorrect**: it would release UsageLock when the callback returns true, before the publication completes. Similarly, an outer CommitTransaction scope-only destructor can release UsageLock *after* inner metadata/assembly locks have unwound, which may violate intended release order.

The likely ownership boundary is the nested publication coordinator:
- make a publication lifetime/lease record part of an already constructed context; eliminate unowned transfer;
- perform cleanup on exceptional exit **while the matching s_assemblyLock and g_MetadataLock scopes still exist**, releasing the usage lease before those outer scopes unwind;
- preserve the existing acquisition order and cover false-return, throw, nested throw and abandoned-session paths;
- scope native CLI and physical vector rollback to the **provably precodec** phase. After an attempted Codec publish, structural cleanup may still be needed for safety, but it must never imply the Runtime/Codec was restored or a retry is permitted. Decide whether vectors stay appended or are hidden under terminal state only after auditing all readers;
- do not call allocating diagnostics, managed exception creation, or callbacks which reacquire transaction/metadata locks while UsageLock is held.

**Important unresolved choice:** a terminal state with a *null* s_active after P3 needs a clearly specified visible failure signal. The existing FailedAfterCommit state is currently often selected based on s_active being non-null, not on Codec progress. Reusing it without validating the ABI and resolution semantics risks misleading downstream readers. Prefer an additional monotonic terminal-restart flag/receipt where feasible; evaluate enum/managed ABI compatibility explicitly.

## 5. ActiveSnapshot lifetime

Currently PublishActive writes the raw pointer into s_active; CommitTransaction releases ownership from its local unique_ptr only after nested callbacks return. A new exception between those operations could leave an invalid process-global pointer.

Candidate contract:
- prebuild all maps and reserve storage before publication;
- at the final native active publication boundary, arrange process-lifetime ownership **before** making the pointer public, with no intervening throwing operation;
- on precodec rejection, reclaim unpublished snapshot normally;
- after any attempted Codec publication, ensure either the snapshot is owned and published consistently or the process becomes terminal, without deleting a pointer that may be visible;
- exercise unexpected exits before and after the store. A leak during terminal shutdown is preferable to a dangling pointer, but leak policy must be reviewed.

This is **not** a ready-to-apply code recipe; ownership and memory ordering need independent review against native readers, GC and shutdown.

## 6. Gated implementation plan — stop points

| Slice | Primary Implementation deliverable | Closure evidence / stop |
| --- | --- | --- |
| D0 — Decision gate | Human/independent approval of phase model, terminal semantics, lock ownership, snapshot lifetime | **Currently OPEN; no native code until approved** |
| D1 — Receipt contract | Minimal C++ phase receipt and stub fault-path tests, preallocated and nonallocating | Static and strict/sanitizer host evidence; explicit review |
| D2 — Native custody | Bounded RAII/exception cleanup of UsageLock and physical/CLI registry scopes, no unrelated changes | Fault injection at precodec/after-append points; lock-order review |
| D3 — Runtime bridge | Propagate actual CodecAttempted/GroupPublished outcome across HybridCLR Runtime, staged publisher and native Publication context | Exact source tests proving precodec error vs postcodec terminal classification |
| D4 — Active ownership | Transfer process-lifetime ActiveSnapshot ownership safely, durable terminal and first-error receipt | Fault matrix at all publication phases; static/host review |
| D5 — Local Validation | Publish new four-repo pinned WEB_TO_LOCAL with fresh roots and exact Unity/IL2CPP Player/GC/ABI tests, if explicitly authorized | Local empirical evidence + independent full-stage review |
| D6 — Human Review Gate | Review design → implementation → Local evidence for R03 B2 | Human decision required, not agent approval |

Do not combine all slices in one automated instruction. Each has a specific validation command/receipt and stops for review where the project requires it. Preserve previous failed and successful receipts independently; do not relabel them.

## 7. Minimum fault-injection matrix

Before approving D5, the next code must support deterministic evidence for all of these distinct cases:

- Input/closure rejection before usage acquisition (no registry/codec changes).
- Usage admitted, then precodec failure before registry append.
- Both registry appends completed, then provable precodec false return.
- Actual Codec validation returns an error with an independently verified untouched lifecycle.
- Exception or unknown outcome **inside Codec attempt**, including after first Lifecycle::Published store.
- Runtime group activation succeeded, then exception **before** s_active release-store (demonstrated by current *host adapter*, not Unity).
- Exception after native s_active store but before ownership transfer (must be structurally impossible or safely handled).
- Exception during/after module initializer, preserving existing first-error and postcommit terminal rules.
- Concurrent reader visibility and shutdown/CloseAndDrain behavior under bounded time/resource budgets.
- Full V1 fields14/15 parity and V2 receipt/readback/first recovery; source roster and ABI unchanged.

Each outcome must record exact commit, source SHA, lifecycle/VM phase, registry sizes, lock release, terminal reason, first error, whether a Player was actually executed and whether the evidence was synthetic, source-only or empirical. Never promote a mock-host success to product or Human Review acceptance.

## 8. Decisions requested at the production gate

1. **Adopt A (phase-aware terminal fail-closed) rather than retryable post-codec rollback?** Recommended: yes.
2. **Allow a native terminal-restart receipt/flag even when s_active remains null?** Recommended: yes, but determine managed ABI and old V1/B1 compatibility before choosing enum or flag.
3. **Authorize D1–D4 production changes only after independent review of this plan?** Current state: not approved. The ongoing instruction to continue Primary Implementation permits test-only analysis in current scope but does not itself satisfy the explicit production review gate documented in this project.

**Invariant status:** WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false. PureInterpreter disabled. No H2/M08A/X02/SNAP-01, no consumed Local rerun and no self-approved Human Review Gate.
