# P1 bounded live transaction status — Primary Implementation reconciliation

**Owner:** Primary Implementation. **Date:** 2026-10-15. **Disposition:** source-backed native status acquisition implemented, **PassedWithinHostScope** under production-method mocks. Complete P1 remains Incomplete; runtime/Unity/Player acceptance unproved. The WEB_TO_LOCAL handoff remains PAUSED.

## 1. Exact four-repository authority

- night-outlook/il2cpp_plus: **10a6bece70ec4990dc795daa11b3f4a7629b7a61**; new additive native status method plus owned capture header, actual-source host runner/tests and CI, branch codex/assembly-shadow-r01b-h1.
- night-outlook/hybridclr_demo: this reconciliation and status-only docs are published on the same branch; resolve the latest demo SHA from remote, not from the tested old Local execution.
- night-outlook/hybridclr: **4b2774b066cfc6afd77a8c8aded6bda7ea574f55**, unchanged.
- night-outlook/hybridclr_unity: **948c0e3b4f8891481301770115e8ba4945eea6de**, unchanged.

The last actually **Local-host-validated** code tuple is DEMO 7b9d1d4e37d1731f9f00042eb04892a8afaf7e80 and NATIVE 74dbdbea80d83923863303bd2b2c0a87f36541b1, with the unchanged HybridCLR/package SHAs. Tools/AssemblyShadow/R03/source-pins.json intentionally retains that older execution tuple and is **not** changed to the new uninstalled native source. Older Local host PASS and previous FAIL remain separately immutable.

## 2. Substantive new source work

**Native libil2cpp/vm/AssemblyShadowBoundedTransactionStatus.h** is a noncopyable, caller-preallocated, one-shot owned status descriptor with hard capacities: 32,768 bytes for detail and 8,192 bytes each for baselineBuildId and patchId. It retains original AssemblyShadowState, AssemblyShadowError, generation, closure expected/staged count and retainedBytes. All bytes (including embedded NUL/control) are copied immediately from borrowed source strings, and no borrowed pointer survives into the completed result.

**Native AssemblyShadow::TryCaptureBoundedTransactionStatus** was added to existing AssemblyShadow.h/.cpp inside the enabled feature. This **actual native source method** reads the status scalars/strings inside the original transaction mutex and uses the original non-allocating StagedCount; afterward it samples the process-lifetime first TypeFailure pointer and applies its original late precedence, choosing Failed or FailedAfterCommit based on the physical active snapshot. A witnessed flip of first-failure pointer, s_state, active pointer/generation or the two first-error flags causes a terminal SourceChanged failure with no reattempt. Capture refuses duplicate use, missing precedence sampling, oversized input and invalid views. It intentionally has **no caller** from current GetDiagnosticsJson, GetExecutionDiagnosticsJson or Player.

Connector readback independently compared the complete original GetDiagnosticsJson and GetExecutionDiagnosticsJson method bodies at native commit 37972fe7b0eabc6332a87422c70fd9c21bedb235 and final native 10a6bece70ec4990dc795daa11b3f4a7629b7a61: **both original diagnostic getters are byte-identical**. No old record field, semantic predicate, V1 length limit or native runtime failure policy changed. The new method and capture header are additive.

**Important bug resolved during CI:** an early alias guard incorrectly used the maximal capture object size (which includes non-owned bookkeeping bytes) rather than the true owned character arena; it rejected valid separately allocated strings next to the object. Final source uses the end of patch_ as the exact arena boundary, and a deterministic adjacent sibling-buffer regression passes on all platforms. Earlier failed exploratory test runs remain failed.

## 3. Source-bound test/CI evidence

The new tools/r03/diagnostic_stream/run_bounded_transaction_status.py mechanically extracts and compiles the **actual current production method body**, retaining source SHA-256 **5f56ff8cc96ac63bc0c81bd2c2abce1ca74b01ccc9953a832984153be4dc34bf**, against explicit mock Transaction/mutex, active snapshot, TypeFailure and native atomics from bounded_transaction_source_fixture.cpp. It does **not** rewrite the actual source method or simulate a real Unity engine/scheduler.

[Final CI run 38750613093](https://github.com/night-outlook/il2cpp_plus/actions/runs/38750613093) at native commit 10a6bece70ec4990dc795daa11b3f4a7629b7a61 completed **SUCCESS** on all three jobs (macOS Apple Clang, Linux Clang and Linux GCC), each strict C++17 and ASan/UBSan. Source-bound cases cover owned immutable text and numerical status, precedence between transaction/late baseline/unexpected/first TypeFailure, active/nonactive terminal state, deterministic source changes after lock sampling, first-input size limits, poison/no-retry, adjacent input, and prepared-path operator-new accounting.

The three passing GitHub CI ZIPs were downloaded and independently audited: **57 manifest-declared regular files** SHA-256 checked against original ZIP bytes, no missing, mismatched or unlisted files; 12 strict/sanitized compile+process receipts and all three identical production method hashes. [EVIDENCE.json](EVIDENCE.json) contains exact ZIP SHA-256, artifact IDs, source pins and test-scope negatives.

This is not official Unity2022.3.62f2 StandaloneOSX native or managed compilation, and not a real VM scheduling/locking test. The source capture object must be preallocated while healthy; Current() itself may lazily allocate if never initialized, and attempting a terminal mutex acquisition may block. A pair of stable atomic reads is not a global epoch. These limitations are explicitly reviewed in [SOURCE_LIFETIME_REVIEW.md](SOURCE_LIFETIME_REVIEW.md).

## 4. Remaining Primary work, earliest first

1. **P1 full native source acquisition still Incomplete.** Extend source-backed, bounded and lifetime-proven status capture to startup candidates, transaction closure/events/stable names, usage registry first-use records, separate physical assembly/class enumerations, bounded metadata-owner lookup and byte-equivalent FormatMetadataOnly type keys. Preserve original late TypeFailure precedence and distinct source generations. Prove no lock inversion, no dangling Il2CppClass/Il2CppImage/Il2CppType reference, bounded transaction hold time, complete class/error coverage and actual VM peak allocation/GC/RSS.
2. Only after reviewing the above source-lifetime/lock owner, connect the already inactive owned general JSON, frozen execution rows and frozen R02 components into a **real complete** field14/15 sink. A completed captured record still needs authentic V2 multi-field aggregate/identity validation; accepting a per-field prefix or capped result is prohibited.
3. **P2 NotIntegrated:** authenticated native/C# V2 file transaction and reader dispatch into every unchanged original semantic predicate. Historical V1 verifier and all prior evidence remain untouched.
4. **E0/E1 Blocked:** supported Unity2022.3.62f2 StandaloneOSX native engine scheduler-owner safe point, in-flight callback drain and GC/finalizer/service/restart source contract. No guessed ABI, simulated acknowledgement, no-op dispatch, sleep, cap/coalescing or finalizer disable.
5. **P3 NotRun:** source-bound official managed and 55-native SDK compilation, real Unity runtime, bounded failure/rollback/normal shutdown audit, separate exact-source new Local assignment and later Human Review Gate. No new Local task or seven Player roots are authorized now.

## 5. Immutable acceptance state

Current WEB_TO_LOCAL remains **PAUSED**; no Local task has been assigned in this P1 increment, and the earlier host-only PASS remains consumed at its original execution pins. SNAP-01 stays **FAIL/ReturnRequired**: 18 cells (14 Passed/4 Failed), three ON raw files zero bytes/exit2 after original V1 field14 prefix262145 exceeded its262144 bound, full producer lengths Unavailable, engine **51213 uncapped reports in 500ms, exit71**. Historical N/M/K/I/E FAIL, strict original S custody Blocked (416844 original identities,339367 survivors,77477 missing, four roots absent), independent R03 full-stage review FAIL and re-review NotRun. V2 frame65536, artifact3932160, envelope262144 and combined encoded4194304 limits unchanged.

R03Accepted=false, H2Passed=false, qualificationApproved=false, ReadyForHumanReviewGate=false, fullLegacyRegressionAcceptance=false, PureInterpreter disabled. No H2/X02/M08A or automatic Human Review Gate.
