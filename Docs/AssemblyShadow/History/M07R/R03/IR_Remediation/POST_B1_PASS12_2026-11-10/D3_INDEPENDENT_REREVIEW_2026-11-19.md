# R03 B2 D3 — Independent re-review of IR-D3-01 remediation

**Decision: `PassD3ForD4` (D3 source/host checkpoint only).** Date: 2026-11-19 UTC. Reviewer: independent source/evidence reviewer; **not** the Primary Implementation report and **not** the Human Review Gate. This supersedes the **decision** `ReturnRequired` from the original [independent D3 report](D3_INDEPENDENT_REVIEW_2026-11-19.md), while preserving that report, its exact rejected source pins, and all prior CI dispositions as historical evidence.

**Authorization limit:** The decision permits a *separately assigned Primary Implementation D4* only. D4 itself is **not started or accepted**. No Unity/IL2CPP/Player run, Local Validation, H2, M08A, X02, SNAP-01, R03 acceptance, or Human Review Gate is authorized. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`.

## 1. Independent scope, sources and exact commit authority

Reviewed the original [IR-D3-01 failure report](D3_INDEPENDENT_REVIEW_2026-11-19.md), [Approach A design](B2_NATIVE_PUBLICATION_REMEDIATION_PREAPPROVAL_DESIGN_2026-11-18.md), [D2 independent source review](D2_INDEPENDENT_REVIEW_2026-11-18.md), [Primary remediation report](D3_IR_D3_01_PRIMARY_REMEDIATION_2026-11-19.md), [independent re-review request](D3_IR_D3_01_INDEPENDENT_REREVIEW_REQUEST_2026-11-19.md), and current canonical README/handoff. **Independently reopened** source definitions in both native and HybridCLR production trees, exact test harness/extractor/workflow, the actual GitHub workflow run and **all four raw job logs**. This was a remote source/evidence review; the reviewer did not run a Unity Player, local Unity Editor, or compile complete production native translation units.

Four source pins on branch `codex/assembly-shadow-r01b-h1`, checked against remote branch HEAD immediately before publication:

| Repository | Source commit/verified pre-report HEAD | Changes in focused remediation |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | pre-report docs HEAD `d99c07fcb1fb94ba45eddb9d1b907f52e7d40f02`; **tested code at `b2e39532718d8bb80ce3089b7374015befbdab37`** | New exact source-host tests/workflow and later documentation |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Unchanged since original D3 |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | Unchanged |
| `night-outlook/il2cpp_plus` | `40d9a16a6e357f0b3ad1cc93362a93cc41768258` | Exactly one production path: `libil2cpp/vm/AssemblyShadow.cpp` |

The native before/after compare `e31d73968e1895e46c0d790132f1b10b23f78842...40d9a16a6e357f0b3ad1cc93362a93cc41768258` is **one commit, one file, 69 changed lines**. The corrected native blob is `5e5fb4b094ae8111e5f674dfc534d411bf597690`. All exact native D2 rollback, phase receipt, first-error, ABI, terminal predicate and `dynamic_array.h` blobs were independently reread and match the test's pinned source-inventory. The `hybridclr_demo` test commit is ancestral to the current docs HEAD; the compare shows **documentation-only** changes between the tested source revision and pre-review HEAD.

## 2. IR-D3-01 — **CLOSED for the defined D3 source-level failure schedule**

The original defect permitted a concurrent candidate method to acquire UsageLock **after** the publisher had released it, but **before** the outer `CommitTransaction` branch marked the process terminal. At that point `s_state=Committing`, `s_unexpectedFailure=false`, and `s_active=null`, so `TerminalMethodDenied` could return false.

The repaired native `AssemblyShadow.cpp` defines a per-attempt `PublicationLeaseExit` with `Unknown` (default), `UsedBeforeAppend` and `ActivePublished`. These are ordinary same-thread fields within the existing native call chain, not shared per-thread locks or a new managed ABI.

**Authoritative order on an unknown normal failure or exceptional exit:**

1. `ReleasePublicationUsage` (~774–783) confirms `usageHeld=true` and `leaseExit=Unknown`; it calls `SealFailedPublicationBeforeUsageUnlock` **while still holding UsageLock**.
2. The seal (~740–771) marks the D1 phase receipt `TerminalRestartRequired` with `CodecOutcomeUnknown` after P3 or `MissingCleanupProof` before P3. No metadata lifecycle reversal is claimed.
3. It calls the real process-lifetime `FirstErrorV2::TryFreeze` with origin `TransactionTerminal` for normal false or `UnexpectedFailure` for native unwinding. The actual class preserves an existing record using Empty→Writing atomic CAS, has inline bounded storage, and performs no allocation/VM call.
4. It release-stores `s_unexpectedFailure=true`, then release-stores `s_state=Failed` (or `FailedAfterCommit` if an active snapshot already exists).
5. **Only then** does `ReleasePublicationUsage` set `usageHeld=false` and `UnlockUsage` execute `atomic_flag.clear(release)`.

A candidate method that later acquires UsageLock through `test_and_set(acquire)` observes the earlier terminal state; the actual terminal predicate (`AssemblyShadow.cpp:316–328`, `AssemblyShadowTerminalExecution.h`) rejects methods when the durable failure is present. The full `AssertMethodIsActive` source has an initial terminal check and a **second check before successful admission** (~2175–2257). A thread that made its initial check while the publisher still owned UsageLock cannot use the now-released lock to pass the final check. This closes the **specific source-derived two-thread schedule** from IR-D3-01; it does not purport to retroactively stop a method that genuinely entered before the failure became terminal.

**Safe branches preserved:**

- `TryBeginPublication` marks `UsedBeforeAppend` only after an actual `UsedClosureMember` returns a baseline-used candidate while holding UsageLock and before either registry append. The subsequent release does not seal terminal; the outer `ClassifyFailedNativeBatch` still requires P0/InProgress and full cleanup proof before permitting `Validated`.
- `PublishActive` marks `ActivePublished` only **after** the native `s_active.store(...,release)` and before releasing UsageLock. That success release does not falsely poison the process. The separate **D4 ownership-before-publication defect remains OPEN**.

**D2 and exception compatibility:** The unchanged `MetadataCache::PublishInterpreterAssembliesBatch` and `Assembly::PublishShadowBatch` retain lock order transaction→metadata→physical assembly→usage→Runtime reservation→Codec. Their CLI and physical rollback guards unwind inside their respective locks; the physical `onAbandon` callback invokes `ReleasePublicationUsage` **before** the physical lock unwinds. In C++ exceptional exits where `PublishActive` does not return, this idempotent callback seals terminal first and releases usage; the existing outer `ScopedUnexpectedPublicationExit` cannot replace the earlier first error or restore a healthy state. A later duplicate onAbandon is a no-op because `usageHeld=false`. The new seal only uses fixed-storage D1/FirstError and atomics, with no allocating diagnostics or new lock acquisition in the inspected source.

**Fail-closed result:** All non-P0 ordinary false returns remain terminal, even when Runtime rejects before the real Codec call; this intentionally conservative recovery policy was already accepted at the sequential D3 source/host checkpoint. Actual `Codec::PublishBatch`/Runtime group activation callbacks remain at their previously verified P3/P4 boundaries and no rollback after Codec attempt is claimed.

## 3. Independent CI audit, including negative control

[**GitHub Actions 44496297788**](https://github.com/night-outlook/hybridclr_demo/actions/runs/44496297788) is independently verified **completed/success on the first run attempt, 4/4 jobs**, head SHA `b2e39532718d8bb80ce3089b7374015befbdab37`, push event. All four job logs were fetched and parsed separately.

| Job | Python source tests | Actual-source host receipts / assertions | Old-behavior negative control |
| --- | --- | --- | --- |
| Ubuntu 24.04 / C++11 | 19/19, OK | 16 / 422, PASS | Expected failure observed |
| Ubuntu 24.04 / C++17 | 19/19, OK | 16 / 422, PASS | Expected failure observed |
| macOS 15 / C++11 | 19/19, OK | 16 / 422, PASS | Expected failure observed |
| macOS 15 / C++17 | 19/19, OK | 16 / 422, PASS | Expected failure observed |
| **Total** | **76 passing tests** | **64 receipts / 1,688 assertions** | **4 expected failures** |

The 19 Python cases per job include two positive identity/body tests and 17 deliberate source mutation/inventory rejection tests. Eight named host cases run twice per job (strict `-O2` and ASan+UBSan): P0 used-denial, normal success, Runtime precheck rejection, actual Codec validation rejection, real Runtime group publication followed by a synthetic callback rejection, exception before Codec, exception after group, and preexisting FirstError preservation. **Five race cases per profile** acquire UsageLock on a competing thread while the publisher is paused in a **host-owned** native assembly-lock destructor after usage release and **before** the original outer terminal-classification site: **40 deterministic race host receipts total**. All readbacks show denied method admission, no wrong-success/rollback claim, no host assertion failure or sanitizer fault.

The **negative control** modifies the extracted test-only native source to suppress early failure sealing on an Unknown exit (while preserving a callable seal function for warning-clean compilation). It then runs the same `codec-validation-race` case. Each job verifies a **nonzero process exit** and a stderr `IR-D3-01 HOST FAIL` assertion before emitting `ExpectedBrokenLeaseRaceRejected`. This demonstrates the regression catches the original class of incorrect ordering; it is **not** a run of the historical old production commit or a real Player fault.

The host executes the **exact pinned bodies** of D2 physical/CLI publication+rollback and the D3 native UsageLock/phase/first-error/terminal helper, with the real pinned `libil2cpp/utils/dynamic_array.h` template and actual HybridCLR `InterpreterMetadataIndexRuntime.cpp`/`InterpreterMetadataIndexCodec.h`. The two literal staged/image forwarding bodies are compiled; VM lock, image, allocator and fault-producer objects are **stand-ins**. The complete original `CommitTransaction` and `AssertMethodIsActive` native translation units are **not** compiled/linked in the host: their relevant call sites were separately inspected as source. The native C++ exception host uses native exceptions; there is no new full Runtime/VM `-fno-exceptions` acceptance claim.

Earlier original D3 CI `44487046888` passes the *rejected prior source* only and is not reused as proof of this fix. Queued and YAML-corrected interim runs likewise do not replace this exact final successful evidence.

## 4. Findings, boundaries and remaining work

| ID | Severity | Independent disposition / follow-up |
| --- | --- | --- |
| **IR-D3-01** | **Critical in old D3** | **CLOSED for this source-host checkpoint**: fail-closed state and FirstError are published before UsageLock release; real two-thread negative/success paths and a broken-order negative control pass |
| IR-D3R-02 | Pass | P0 witnessed used-closure refusal and post-active success are differentiated, preventing false terminal state |
| IR-D3R-03 | Pass | D2 CLI/physical cleanup and UsageLock idempotence remain source-consistent under normal false and C++ unwind |
| IR-D3R-04 | Pass / bounded | FirstError prior-record preservation, normal-vs-exception origin, P3/P4 actual Runtime/Codec phase order verified |
| IR-D3R-05 | **High / evidence boundary** | Real Unity/IL2CPP native TUs, VM/GC concurrency, native baselib/FastAutoLock, 32-bit atomic/ABI and whole Player test remain **NotRun**. Host synthetic fault producer and OS/VM stand-ins must not be promoted to empirical Player acceptance |
| IR-D3R-06 | **Critical / D4 (deferred)** | `s_active` still stores a raw `ActiveSnapshot*` before `CommitTransaction` relinquishes its `unique_ptr`. D4 must solve ownership, P5/P6, post-store exception/shutdown and lifetime |
| IR-D3R-07 | Minor / documentation | Older D1 receipt/CommitTransaction comments still describe the receipt as inert or only late unexpected-exit sealing; update when editing in D4, without altering source behavior under this independent review |

**Reviewer judgment:** No new D3-blocking source defect was found in the fixed lease-release ordering, and the verified exact-source regression plus negative control directly covers the original IR-D3-01 schedule. The remaining high-severity integration/whole-VM uncertainties are **explicitly reserved for later Local Validation**; the existing ActiveSnapshot issue is the **designated D4 critical task**, not a reason to invent a D3 pass over D4.

**Final D3 disposition:** `D1IndependentReview=WaivedByUser` (not Passed); `D2IndependentReview=PassD2ForD3`; `D3IndependentReview=PassD3ForD4`; `D4=NotStarted`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. Do not self-approve the Human Review Gate or begin D4 in the independent review session.
