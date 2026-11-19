# R03 B2 D3 — IR-D3-01 pre-unlock terminal custody remediation (Primary)

**Date:** 2026-11-19 UTC. **Role:** Primary Implementation, not independent review. **Status:** native correction and focused test sources pushed; **new CI queued / no successful execution receipt yet**. Do not regard the repair as independent D3 acceptance or authorize D4 or Local Validation.

## Authority and defect

The [independent D3 report](D3_INDEPENDENT_REVIEW_2026-11-19.md) returned **ReturnRequired** for critical **IR-D3-01**: after a failed real Codec publication, `PublishActive` previously released UsageLock while the transaction remained `Committing`, before `CommitTransaction` stored `s_unexpectedFailure` and terminal state. The genuine `TerminalMethodDenied` predicate treats Committing without a durable failure as nonterminal, so a concurrent baseline method could pass the entry gate during that interval. The report established a **source-derived permissible schedule**, not a Unity Player observation. Preserve its exact classification until an independent re-review passes.

All four repositories use branch `codex/assembly-shadow-r01b-h1`. Source pins for this fix:

| Repository | Revision | Changes |
| --- | --- | --- |
| `night-outlook/il2cpp_plus` | `40d9a16a6e357f0b3ad1cc93362a93cc41768258` | **One production path:** `libil2cpp/vm/AssemblyShadow.cpp` |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Unchanged from D3 |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | Unchanged |
| `night-outlook/hybridclr_demo` | `426c4082e7f59e69f894fe6dd82595f9a0edd6ec` | Focused test/workflow source checkpoint, later documentation HEAD separately verified |

The native `AssemblyShadow.cpp` Git blob for the fix is `5e5fb4b094ae8111e5f674dfc534d411bf597690`. The D2 physical/CLI registry files and HybridCLR Runtime/Codec were **not** modified.

## Implemented correction

1. A per-attempt `PublicationLeaseExit` has three explicit states: `Unknown` (default), `UsedBeforeAppend` (the source-witnessed safe P0 refusal), and `ActivePublished` (the existing successful native active snapshot release-store). It is only accessed within the existing synchronous native publication lock chain.
2. The new `SealFailedPublicationBeforeUsageUnlock(Publication&)` is **noexcept, fixed-storage and allocation-free**: it marks the existing D1 attempt terminal without reversing Codec, uses the existing `FirstErrorV2::TryFreeze` without overwriting an earlier failure, and release-stores `s_unexpectedFailure` and the Failed/FailedAfterCommit state. The first-error origin distinguishes normal false from unexpected C++ unwind.
3. The idempotent `ReleasePublicationUsage` calls that seal on every `Unknown` lease exit **while still holding UsageLock**, then sets `usageHeld=false` and clears the usage atomic flag. A competing method guard acquiring the usage lease afterward synchronizes with the release and observes terminal intent before it can pass its final terminal gate.
4. The precise used-closure refusal marks `UsedBeforeAppend` **before** its release, maintaining the already reviewed P0-only retryable path; successful native `s_active` publication marks `ActivePublished` before release and remains nonterminal. All normal false-return paths mark `normalFailure` before releasing; an unexpected exception leaves the default Unknown and is sealed from the existing D2 physical rollback abandonment callback.
5. Existing outer `CommitTransaction` normal/exception reporting and D3 `ClassifyFailedNativeBatch` stay in place. Their repeated `TryFreeze`/terminal stores cannot unfreeze, overwrite, or undo the earlier seal. No new managed enum, activation flag, source roster, B2 budget or Runtime/Codec ABI change was introduced.

**Caveats:** native `FirstErrorV2` and phase receipt atomics execute under the existing nested transaction/metadata/assembly/usage locks, but use inline storage and no locks or VM calls in their implementations; actual 32-bit/Unity native lock-free behavior and complete VM/GC lifetime remain unverified. A thread already executing business code before the new terminal store cannot be retroactively stopped; the corrected guarantee is that a candidate method acquiring UsageLock after the failed publisher releases it cannot newly pass the terminal guard. Post-active `unique_ptr<ActiveSnapshot>` lifetime is still **D4 critical/open**.

## Focused test implementation and exact scope

New `hybridclr_demo` source files:
- `Tools/AssemblyShadow/R03IR/TypeDefCensus/extract_d3_usage_gate.py`: Git HEAD/blob-pinned body extractor, 21 literal production/native wrappers and exact real `dynamic_array.h` source; crosschecks phase/first-error state before usage unlock, D2 physical/CLI unwind, and true native terminal entry predicate.
- `Tools/AssemblyShadow/R03IR/TypeDefCensus/test_extract_d3_usage_gate.py`: 19 exact-source and fail-closed mutation tests; changes to early seal, origin, lock order, safe P0/success, D2 rollback and Runtime Codec/group boundaries are negative controls.
- `Tools/AssemblyShadow/R03IR/TypeDefCensus/D3UsageGateRaceHost.cpp`: compiles exact native D2 physical and CLI scope bodies, exact D3 callbacks and classifier, actual `FirstErrorV2`, `TerminalMethodDenied`, actual HybridCLR Runtime.cpp/Codec.h and the two literal staged/image wrapper functions. The Unity lock implementation/VM objects/allocator and stage-fault producer are **test-owned stand-ins**. A two-thread barrier pauses T1 in the fake assembly-lock destructor **after native UsageLock release but before the old outer terminal-classifier site**, while T2 acquires UsageLock and checks the actual terminal method predicate. Cases: source-witnessed safe P0, normal success, Runtime precheck, actual Codec validation error, group-published callback refusal, C++ exception before Codec, C++ exception after real group, and preexisting FirstError preservation.
- `.github/workflows/r03-b2-d3-usage-gate-race.yml`: macOS 15 + Ubuntu 24.04 × C++11/C++17, strict/ASan+UBSan host and an expected-failing **test-only negative control** that suppresses the early failure-seal call while preserving the source function. No `Unity` or `IL2CPP Player` invocation.

**CI evidence status at report creation:**
- [Latest source-exact matrix 44495063272](https://github.com/night-outlook/hybridclr_demo/actions/runs/44495063272) is **Queued**, not Passed, at demo tested code `426c4082e7f59e69f894fe6dd82595f9a0edd6ec`. Four jobs have not started. No host execution/sanitizer/negative-control acceptance receipt may be claimed.
- Earlier attempts [44494149474](https://github.com/night-outlook/hybridclr_demo/actions/runs/44494149474) and [44494610249](https://github.com/night-outlook/hybridclr_demo/actions/runs/44494610249) were also Queued when last checked; superseded code SHA, not acceptance evidence.
- The original D3 [CI 44487046888](https://github.com/night-outlook/hybridclr_demo/actions/runs/44487046888) remains 4/4 PASS at **prior** native source. It does **not** establish closure of IR-D3-01.

## Required completion / stop

**Primary correction status: Implemented and pushed, but validation pending.** Once GitHub runners actually execute the new exact-source matrix, independently verify each job's result, raw 19 mutation cases, eight strict/sanitized host scenarios, test negative-control rejection and absence of sanitizer faults; repair any focused failures without changing the documented product scope. Then issue a **new independent D3 re-review request** referencing exact new remote heads and source+CI evidence. The independent reviewer, not Primary, decides PassD3ForD4 / ReturnRequired / Blocked.

**Current gate:** `D3IndependentReview=ReturnRequired` (prior decision preserved), `IR-D3-01Correction=ImplementedValidationPending`, `D4=NotStarted`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`. Do not begin D4, D5, H2/M08A/X02/SNAP-01 or local Unity/IL2CPP builds.
