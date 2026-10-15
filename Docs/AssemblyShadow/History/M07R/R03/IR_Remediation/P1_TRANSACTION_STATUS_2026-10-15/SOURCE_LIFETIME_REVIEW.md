# P1 bounded native transaction-status source and lifetime review

**Owner:** Primary Implementation. **Source anchor:** il2cpp_plus 10a6bece70ec4990dc795daa11b3f4a7629b7a61, branch codex/assembly-shadow-r01b-h1. **Disposition:** additive real native source entry point, verified with exact-method host mocks; **NOT** complete P1, installed Unity compilation, Player or R03 acceptance.

## Exact source scope

- Additive native API: AssemblyShadow::TryCaptureBoundedTransactionStatus, declared in libil2cpp/vm/AssemblyShadow.h under the enabled feature and defined in AssemblyShadow.cpp. Output: preconstructed, single-owner AssemblyShadowBoundedTransactionStatus.h Capture.
- Existing code: transaction.status/error/detail/IDs/closure state within Transaction and its std::mutex, immutable process-lifetime TypeFailure pointer and s_active/s_state/first-failure atomics.
- Independent GitHub Connector comparison found **GetDiagnosticsJson and GetExecutionDiagnosticsJson each byte-for-byte unchanged** from native 37972fe7b0eabc6332a87422c70fd9c21bedb235 to native 10a6bece70ec4990dc795daa11b3f4a7629b7a61. No original runtime output, semantic policy or V1 verifier has been replaced.

## Source-lifetime boundary

The actual new native method enters the existing transaction mutex and synchronously copies status state, lastError, error detail, baselineBuildId, patchId, generation, closure size, StagedCount and retainedBytes. The capture owns all copied text: detail capacity 32768 bytes; build ID and patch ID capacity 8192 bytes each. Capacity overrun, null source or prohibited overlap **fails closed** without output and without truncation.

Transaction strings are protected during the bounded memcpy. StagedCount is the original non-allocating loop. No recursive type-key construction, managed callback, file emission, metadata cache call or new metadata lock is made under this mutex. However, lock hold time is not instrumented, and a terminal VM callback may be blocked behind the owner. Current() lazily allocates its process-lifetime Transaction on first use. Future use after terminal failure requires independent healthy-time preinitialization and a reviewed owner safe point; constructing Capture while healthy alone does not address Current() initialization.

Original status precedence is respected within the sampled native values: unexpected failure overrides late baseline use, which overrides transaction lastError/detail. After releasing the mutex the first immutable s_typeFailure, if present and unchanged between admission and final sample, overrides state/code/detail; Failed versus FailedAfterCommit derives from the active snapshot. A source change witnessed in s_state, active pointer/generation, first failure pointer or the two first-error flags produces SourceChanged. No retry or fabricated consistent snapshot is permitted.

This **does not prove one atomic VM epoch**. The guard reads independently published variables, cannot prove all class/assembly/usage/R02 state, and is not a universal ABA or scheduler barrier. GetDiagnosticsJson retains its own original weaker multi-lock snapshot semantics. Status Capture includes NO startup candidates, closure/event rows, first-use metadata, assembly/class inventories or R02 counters; it is a source-backed P1 status building block only.

## Host test verification and discovered bug

[CI 38750613093](https://github.com/night-outlook/il2cpp_plus/actions/runs/38750613093) completed **SUCCESS** on Apple Clang/macOS15, Linux Clang and Linux GCC. Strict C++17 and ASan/UBSan tests compile the **exact extracted current production method body** against explicit VM/transaction/atomic mocks. Tested full owned text (including embedded NUL), transaction scalar values, late/early failure precedence, first TypeFailure override, active/nonactive terminal state, deterministic first-failure/state/active/flag changes, no retry, double use, malformed phase, overlimit detail/build/patch and zero observed operator-new calls in the prepared synchronous mock path. Actual source method SHA-256: 5f56ff8cc96ac63bc0c81bd2c2abce1ca74b01ccc9953a832984153be4dc34bf.

The initial exploratory CI exposed a real alias-guard bug in the new Capture header. It compared borrowed pointers against kMaxObjectBytes, which includes bookkeeping padding, so a legitimate separate allocation directly adjacent to Capture could be rejected as overlapping. The final implementation checks the **actual owned text arena**, from detail_ to the end of patch_. A deterministic adjacent-sibling-buffer fixture now passes. Earlier exploratory CI failures remain historical failures and are not reclassified.

Three original passing CI artifact ZIPs were downloaded and independently audited. Each declares its own complete source hashes and four compiler/process receipts (strict/sanitized build+run). All 57 manifest-declared regular files were independently SHA-256 matched to their ZIP payloads with no missing, mismatched or unlisted files. ZIP digests and artifact IDs are recorded in EVIDENCE.json. This is actual-source-method **mock compilation**, NOT full official native SDK compile.

## Remaining lock and lifetime proof

1. Establish healthy-time transaction preinitialization, permitted read/caller thread and maximum lock hold time in the official Unity2022.3.62f2 StandaloneOSX native runtime.
2. Capture complete transaction closure/events/stable names and first-use registry under explicit lock ranking without holding a spinlock through arbitrary VM metadata reads. Preserve original error/detail precedence and independently sampled generations.
3. Prove class/image/type identity lifetime; replace allocating physical metadata owner index and recursive FormatMetadataOnly type-key construction with fixed-budget, byte-identical, fail-closed acquisition. Then integrate owned general/execution/R02 components with actual source sampling.
4. Preserve both V1 historical verification and all original V2 and semantic bounds; integrate real native/C# file transaction only after acquisition and E0 scheduler ownership source contracts are reviewed.
5. Complete official SDK managed/55-native compiler matrix, static terminal-path review and separate Human Review Gate before a new Local runtime authorization.

**No Local assignment.** WEB_TO_LOCAL stays PAUSED and previously consumed host runs/roots cannot be reused. SNAP-01 remains FAIL/ReturnRequired (14Passed/4Failed, three ON slot14 prefix262145 over262144, full size Unavailable, engine51213 uncapped reports/500ms exit71). N/M/K/I/E FAIL; strict S original custody Blocked (416844 original,339367 surviving,77477 missing); R03 full-stage FAIL/re-review NotRun. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; PureInterpreter expansion disabled. No H2/X02/M08A.
