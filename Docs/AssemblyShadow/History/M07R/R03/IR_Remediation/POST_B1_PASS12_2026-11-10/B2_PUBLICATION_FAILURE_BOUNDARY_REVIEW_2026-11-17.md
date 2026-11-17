# R03 B2 — Publication irreversibility and exception disposition: Primary source-host review

**Date:** 2026-11-17 UTC. **Branch:** `codex/assembly-shadow-r01b-h1`. **Scope:** exactly one source-only publication-failure boundary and one isolated, fail-closed C++11 policy experiment. **Tested code commit:** `night-outlook/hybridclr_demo@c9b927c651960e67704bff23e170cb21f2376006`. Read-only source pins: `night-outlook/il2cpp_plus@cecf4b859d50b128e5c0fc6c90cd89e3a452b96a`, `night-outlook/hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`. Unchanged `night-outlook/hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`.

This report is **not** a full Human Review Gate, Unity/Player proof, native patch approval, source lifetime/GC epoch certificate, or Local Validation handoff. Runtime B2 remains inactive.

## 1. Source-derived point of no return

The prior [transitive mutex chain](B2_TRANSITIVE_PUBLICATION_MUTEX_CHAIN_REVIEW_2026-11-17.md) and [usage lease candidate review](B2_RUNTIME_CODEC_MUTEX_USAGE_LEASE_REVIEW_2026-11-17.md) established the lock ordering but not exception-safe failure classification. This cycle checks the actual publication sequence, **not** an unpinned synthetic approximation:

| Scope / owner | Source fact at fixed Git blob | Consequence |
|---|---|---|
| `il2cpp_plus/AssemblyShadow.cpp` (`dc941907884b9a7f44ade6085d05f2e4a1a96d9e`) | `TryBeginPublication` manually acquires `UsageLock`. `PublishActive` calls the staged-image batch, sets `member.staged->published`, then release-stores `s_active`. Normal success and false-return paths call `UnlockUsage`. | The lock is held **across callbacks**; normal returns do not establish C++ unwinding safety. |
| Same native source | `CommitTransaction` sets `Committing`, calls `MetadataCache::PublishInterpreterAssembliesBatch`, and on a **normal false return** sets `Validated`. | This return-path classification must not be used for an unknown exceptional escape or partially published lifecycle. |
| `hybridclr/StagedAssembly.cpp` (`8b9e9da261365326b327051c43c52acc3b2052ce`) and `InterpreterImage.cpp` (`afe4b3b9e29fa4023c6025e0b35e13d53a6ff15b`) | Staged batch delegates to `InterpreterImage::RegisterImagesBatch` and then `InterpreterMetadataIndexRuntime::PublishBatch`. | A source-visible synchronous bridge connects native publish to codec. |
| `InterpreterMetadataIndexRuntime.cpp` (`509e357359a8912c05adac3434a7e71b3fc3f83c`) | Validates under `reservationMutex`; calls the codec; on success release-stores each image's `publicationGroup`, then `groups[group].active`, and advances the group index. | Group visibility occurs **after** the codec publication succeeds. |
| `InterpreterMetadataIndexCodec.h` (`2020d4e2da6dea8601525203e7ab307d21c40a73`) | Validates all reservations under `codec.mutex_`; a later loop release-stores each record's `Lifecycle::Published`. The pinned function has no normal error-return branch after these stores. | The first lifecycle store is the **irreversible publication boundary** for conservative error classification. No source evidence of an inverse state transition was obtained. |

There are **five exact source Git blobs** in this scoped verification, including the full native commit method and its separate `FeatureDisabled` stub. The source verifier strips comments and quoted literals, extracts lexical function bodies, checks normal-return operation ordering, rejects altered lifecycle/group/active stores and unexpected normal error returns after lifecycle publication, and reports `PinnedNormalReturnIrreversibilityBoundaryOnly`. It is **not a compiler CFG, transitive no-throw guarantee, concurrency proof, or actual atomic metadata snapshot**.

## 2. Candidate error-state policy, **not implemented in native VM**

The new test-only `PublicationFailureBoundaryCandidate.h` separates **known pre-attempt rejection** from **unknown outcome at/after the codec attempt**. Its receipt is monotonic and carries no metadata pointers. It owns the existing isolated `PublicationUsageLeaseCandidate.h` lease; that lease is never compiled into `libil2cpp`.

| Event in the synthetic policy | Result | Retry or rollback claim |
|---|---|---|
| Explicitly verified rejection while the usage lease is held **before** any codec call | `RejectedBeforeAttempt` | Eligible for *test-only* `knownRecoverablePrecommitOnly`; real rollback/abort remains separately unproven |
| Begin opaque codec call; any throw, unknown result, absent completion, or return requiring unverified rollback | `TerminalRestartRequired` | **No** retry or rollback |
| Codec normal success, then failure before group activation | `TerminalRestartRequired` | Already past the possible lifecycle transition |
| Group visible, then failure before the active snapshot store | `TerminalRestartRequired` | Never claim the active mapping is safely recoverable |
| Active snapshot stored, then exception or missing final commit receipt | `TerminalRestartRequired` | An already-active mapping cannot be treated as a precommit failure |
| All stages succeed in order and release the usage lease | `Complete` (synthetic only) | Still **no** native runtime acceptance |
| Wrong-stage call, abandoned scope, invalid retry, or post-completion misuse | Terminal, fail-closed | Cannot revive a terminal or invalidated receipt |

**Intentional conservatism:** beginning the opaque codec call places the candidate in `CodecAttempted` *before* invoking another module. Even an exception before the first actual store is reported terminal, because the caller lacks independently authenticated evidence of nonpublication. A future native design may classify a **proved normal no-side-effect error** as precommit, but must not derive that from a `catch(...)` or an RAII unlock alone.

**Important subtlety:** releasing an RAII usage lease does **not** restore codec lifecycle state, publication group visibility, the active snapshot or transaction status. A real cross-callback lease must also be reviewed for destructor order relative to the actual `g_MetadataLock`, `s_assemblyLock`, native transaction lock and exception unwinding. The host model cannot prove the production callbacks' release order or shutdown progress.

## 3. Implementation and repeatable tests

New files only in `hybridclr_demo`:

- `Tools/AssemblyShadow/R03IR/TypeDefCensus/verify_publication_failure_boundary.py` — read-only exact native/HybridCLR commit, tree and Git blob verifier; five function/phase ordering contracts; always-false production, rollback, VM epoch and acceptance evidence flags.
- `Tools/AssemblyShadow/R03IR/TypeDefCensus/test_verify_publication_failure_boundary.py` — 26 mutation/source tests including lifecycle/active/group reordering, new postcommit error, removed normal unlock, disabled stub drift, comments as decoys, and the mandatory true pinned checkout.
- `Tools/AssemblyShadow/R03IR/TypeDefCensus/PublicationFailureBoundaryCandidate.h` — C++11 source-host-only monotonic error and phase model, reusing the existing pinned synthetic UsageLease header without modifying it.
- `Tools/AssemblyShadow/R03IR/TypeDefCensus/PublicationFailureBoundaryCandidateHost.cpp` — 20 fail-closed scenarios / 114 assertions per run, including injected exceptions at every publication phase and attempted invalid recovery after a prior terminal or complete receipt.
- `.github/workflows/r03-b2-publication-failure-boundary-host.yml` — exact pin checkouts and source-mutation suite with zero skips, plus macOS/Ubuntu × C++11/C++17 strict+ASan/UBSan tests. **No Unity Editor, IL2CPP Player, native SDK or real metadata is executed.**

**Primary local source-only evidence:** 25/26 Python tests passed with one intentionally skipped, because the external exact checkout is unavailable here. GCC and Clang × C++11/C++17 × strict and ASan+UBSan: **8/8 host executions passed**, 20 cases / 114 checks each. This is not Local Validation. The existing test-only UsageLease header was reproduced byte-for-byte (Git blob `6283d78beba5da0f9c0dd02d25307df869e40d80`), not republished or changed.

**GitHub exact-code evidence:** [GitHub Actions run 44112641871](https://github.com/night-outlook/hybridclr_demo/actions/runs/44112641871). **At initial review preparation: 3/4 matrix jobs passed; macOS C++11 pending. This is NOT a four-job PASS until confirmed separately.**

## 4. Primary review findings and stopping point

- **PBND-01 — source-order:** Only the pinned normal-return lifecycle, group, and active-snapshot ordering is checked. Exact source drift fails closed. Any future compiler-verified call/exception boundary still needs separate review.
- **PBND-02 — test-only policy:** The monotonic terminal model rejects attempted recovery after an opaque codec call. The RAII lease releases the *test-owned* usage lock on simulated exceptions. It cannot prove native atomicity or build/GC source lifetime.
- **PBND-03 — OPEN / HIGH:** No native exception-custody implementation or independently verified no-throw contract exists for all transitive publication calls, and the actual native `CommitTransaction` false-return path still resets `Validated`. A real exceptional escape may be **unknown**, not equivalent to a normal precommit error.
- **PBND-04 — OPEN / HIGH:** Real transactional visibility, process-lifetime irreversible metadata, active snapshot ownership, GC/class/VM source epoch, reverse lock edges, teardown progress and actual Unity Player evidence remain unproven.
- **PBND-05 — OPEN:** Full original V1 fields14/15 byte parity, native V2 terminal artifact/receipt/readback/first recovery, real TypeDef-use high-water, 32/64-bit ABI and native stack/lock/RSS profiling, and historical R03 independent-review findings are still outstanding.

**Recommendation for a separately human-reviewed future native change:** first define a bounded, explicit phase/failure receipt for `CommitTransaction` and the codec publisher; require the terminal/restart transition to occur for all **unknown after-attempt outcomes**; then design a narrowly scoped RAII usage-lock owner whose lifetime ends under the correct lock-unwind order. Only with independent proof of rollback/no-change can an error return legitimately remain `Validated`. This is a review recommendation **not an authorization or a production patch**.

**Disposition:** `PinnedNormalReturnIrreversibilityBoundaryOnly` + `PassedSyntheticPublicationFailurePolicyOnly` if and only if the exact-code workflow passes. All product acceptance flags stay false. Production native forks and the original 64-native/eight-demo source manifest are unchanged; the actual B2 128 combined TypeDef, 64-byte declaration and 65,536 indexed owner lookup limits remain fixed. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; PureInterpreter disabled. No H2/M08A/X02/SNAP-01, consumed B1 oneuse replay or Human Review Gate self-approval.
