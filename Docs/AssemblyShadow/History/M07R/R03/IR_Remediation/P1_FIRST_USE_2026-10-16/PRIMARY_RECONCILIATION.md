# P1 first-use source capture — Primary reconciliation

**Owner:** Primary Implementation. **Date:** 2026-10-16 UTC. **Disposition:** Actual bounded first-use native source entry point, **PassedWithinHostScope** only. **P1 still Incomplete; Local Validation PAUSED.**

## 1. Source and branch authority

All repositories remain on branch codex/assembly-shadow-r01b-h1.

| Repository | Exact code/source authority |
| --- | --- |
| night-outlook/il2cpp_plus | **1d66565855e729bedeaf93ed24078e9a6dbc83ed** — new bounded first-use C++ header, additive native source entry point and host source-bound tests/CI |
| night-outlook/hybridclr_demo | Primary reconciliation/docs publication only; latest remote documentation HEAD must not be substituted for an executed test pin |
| night-outlook/hybridclr | **4b2774b066cfc6afd77a8c8aded6bda7ea574f55**, unchanged |
| night-outlook/hybridclr_unity | **948c0e3b4f8891481301770115e8ba4945eea6de**, unchanged |

Previous native implementation base: 339a49b5f1eb18c7cef9390c73ee6b64b0e6a36d. Connector comparisons independently verified the **entire existing GetDiagnosticsJson, GetExecutionDiagnosticsJson, TryCaptureBoundedTransactionStatus and TryCaptureBoundedTransactionInventory functions are unchanged**. The native changes are additive: a new header, declaration and TryCaptureBoundedFirstUses body, source-bound tests/runner and CI.

The **last actually Local-host-executed** source tuple remains demo 7b9d1d4e37d1731f9f00042eb04892a8afaf7e80 and native 74dbdbea80d83923863303bd2b2c0a87f36541b1, with the unchanged HybridCLR/package SHAs. Demo Tools/AssemblyShadow/R03/source-pins.json intentionally retains that executed tuple. The new native head is NOT a real installed Unity SDK/Player validated pin, and previous Local host PASS and prior FAIL are immutable.

## 2. Implementation completed

**libil2cpp/vm/AssemblyShadowBoundedFirstUseCapture.h** introduces a noncopyable, fixed-capacity, one-use owned capture with **4096 candidate slots, 1048576 bytes of owned text, and bounded 160-byte first-use detail**. The original BaselineUseKind, name, first-use detail + exact FirstUseSequence decimal suffix, class-free empty type string, thread and timestamp are preserved for complete rows, including sequence 0 and UINT64_MAX. Candidate names use the full source string bytes; original detail is treated as the legacy terminated C-string with bounded validation. Every limit violation, missing terminator, wrong stage/order, source generation mismatch and unsafe class name leaves the result incomplete.

**New native AssemblyShadow::TryCaptureBoundedFirstUses**, additive to AssemblyShadow.cpp/.h, reads the actual process-published CandidateRegistry. It copies all bounded raw UseRecord fields while holding the original short UsageLock, and reads the original non-atomic s_usageGeneration **under that same lock**. After releasing it, the method copies stable candidate names and composes owned detail/sequence bytes without constructing a heap snapshot. It enters UsageLock once more only to verify the generation; a changed generation or registry pointer fails closed. It does not acquire g_MetadataLock, call VM class/type resolution or execute managed/Player code.

**Critical safe boundary:** UseRecord.klass is copied as an **opaque token only**; the live source method never dereferences it. If any present first-use observation requires physical class namespace/name, the live method refuses to Seal with UnverifiedClassMetadata. This avoids the original getter's unproven post-UsageLock Il2CppClass dereference without silently omitting the required type field. The standalone component has a token-matching physical-name resolver interface for **future metadata-owner integration**, but the current production source method deliberately never calls it. Test-only fake type resolution cannot establish real metadata class lifetime or semantic truth.

No original hot-path first-use writer, guard/scheduler business rejection, class observation, V1 verifier, V2 Player transport, C#/managed code or execution reporting count was changed. The new native source entry point has no existing Player caller.

## 3. Strict source-bound CI and independent artifact verification

The runner tools/r03/diagnostic_stream/run_bounded_first_use.py extracts and compiles the exact current native TryCaptureBoundedFirstUses body under explicit C++ CandidateRegistry/UsageLock mocks and records source before/after Git blobs, method SHA-256 and all compiler/run stderr/stdout receipts. [Final native CI 38839990454](https://github.com/night-outlook/il2cpp_plus/actions/runs/38839990454) completed **SUCCESS**, all three jobs Apple Clang/macOS15, Clang/Linux and GCC/Linux. Strict C++17 and ASan/UBSan profiles Passed on each job. Actual method SHA-256: **c3626338497a16466c3f358f3771eb663fc211b94d6bd5ee6223364763bf4a2b**.

Tests covered: ordered presence/absence of candidate first-use rows; exact class-free detail/sequence/kind/name/thread/timestamp; complete 4096-slot acceptance and 4097 rejection; source registry/generation changes; all candidate/detail/text limits; malformed unterminated detail; null registry member; self-alias and immediately adjacent valid source; wrong stage/reuse; and explicit denial of class-bearing live source until a proven name. A synthetic test-only resolver with matching opaque identity checked the original namespace + "." + class name format, without exercising real Il2CppClass lifetime. Current product AssemblyShadowDiagnostics::Serialize and the inactive frozen general builder matched **all 980 bytes** of complete synthetic general JSON assembled from actual-method **first-use** rows plus **mocked** transaction/assembly/class fields.

[Existing general serializer/V2 interop CI 38839990408](https://github.com/night-outlook/il2cpp_plus/actions/runs/38839990408) also completed SUCCESS, 3/3 jobs at the same final native head. This is separate source-bound host coverage, NOT a full project/official SDK/Player acceptance.

Three original CI ZIP artifacts were independently downloaded from GitHub Connector. **All 57 manifest-declared regular files** matched original archive bytes and SHA-256, with no missing, mismatched or unlisted files. All 3 RESULT.json files report PassedWithinHostScope, sourcePreserved=true, strict/sanitized success, and the identical native method hash. [EVIDENCE.json](EVIDENCE.json) includes all artifact IDs/ZIP SHA-256/source binds and the limitations of this audit.

## 4. Source lifetime, lock and missing coverage

Read [SOURCE_USAGE_LOCK_AUDIT.md](SOURCE_USAGE_LOCK_AUDIT.md) for the actual first-use writers, process-retained CandidateRegistry, short UsageLock protocol, original unsafe class read and no-epoch limitation.

**This is NOT the complete P1 live diagnostic producer.** It fails closed on a class-bearing first-use, which real game execution may commonly produce. Class metadata lifetime, post-UsageLock safe owner, bounded class physical name production, all physical assembly/class enumeration and type keys remain unproved. The method returns only the first-use subset and is not yet wired into the field14 builder. Captured raw bytes (~4096 × bounded UseRecord) must be copied under UsageLock; worst-case spinlock hold time, real contention, peak native RSS and terminal callback liveness remain unmeasured. The source-generation check is not a universal global epoch. The current independent transaction inventory/R02/execution frozen components are also not integrated into the actual Player.

**Earliest unfinished Primary work:** obtain a source-backed metadata-lifetime ticket and bounded physical first-use class name under the correct lock order (**never** take metadata lock while holding UsageLock). Then implement bounded physical assembly/class enumeration, immutable physical metadata type owner lookup and exact bounded FormatMetadataOnly, preserve separate source generations, capture/GC/RSS peaks, and integrate general/execution/R02 complete outputs only when source data are valid. P2 authenticated native/C# V2 transaction and every unchanged original semantic predicate are still NotIntegrated; E0/E1 supported native engine safe point/GC/finalizer/maintenance/restart Blocked; P3 official managed/55-native SDK compilation/Player NotRun.

## 5. Immutable evidence, acceptance and handoff stop

The previous Local host successor PASS remains consumed at its original exact pins; the earlier Local host FAIL and its raw evidence remain immutable. SNAP-01 remains **FAIL/ReturnRequired**: 18 cases, **14 Passed/4 Failed**, first observed ON slot14 prefix262145 above the original V1 text limit262144 (actual complete bytes Unavailable), engine **51213 uncapped reports / 500ms, exit71**. Historical N/M/K/I/E FAIL, strict original S custody Blocked (416844 originals,339367 survivors,77477 missing; four native source roots missing), and independent R03 full-stage review FAIL/re-review NotRun are unchanged. Other old R02 and terminal-policy CI textual source assertions remain independently unqualified; passing the new host tests does not assert repository-wide CI health.

**R03Accepted=false, H2Passed=false, qualificationApproved=false, ReadyForHumanReviewGate=false, fullLegacyRegressionAcceptance=false, PureInterpreter disabled. WEB_TO_LOCAL PAUSED.** No new Local Validation, Unity/Player build/run, Human Review Gate or H2/X02/M08A authorized by this increment.
