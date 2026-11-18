# R03 B2 D2 — native registry and UsageLock exception custody

**Date:** 2026-11-18 UTC. **Branch:** codex/assembly-shadow-r01b-h1. **Scope:** Primary Implementation, D2 only; not Unity/IL2CPP Player acceptance or an independent Human Review Gate.

## Authorization and exact pins

The user previously approved Approach A and D1–D4, then explicitly **waived the interim D1 independent review** and requested continuing development. That waiver is recorded in [D1_INTERIM_REVIEW_USER_WAIVER_2026-11-18.md](D1_INTERIM_REVIEW_USER_WAIVER_2026-11-18.md); it is *WaivedByUser*, not a fictitious independent PASS and not a waiver of D2/D3/D4/final review or Local Validation restrictions.

- night-outlook/il2cpp_plus **b86a97e1dcca18163df5ac2d5f268bf6de18bbdf** — D2 native source
- night-outlook/hybridclr_demo **150f4a685dda170880089dbe1a930028f562056a** — exact final D2 test/workflow source
- night-outlook/hybridclr **4b2774b066cfc6afd77a8c8aded6bda7ea574f55** — unchanged
- night-outlook/hybridclr_unity **948c0e3b4f8891481301770115e8ba4945eea6de** — unchanged

## Native implementation — five files

| il2cpp_plus native file | Git blob | Change |
| --- | --- | --- |
| libil2cpp/vm/Assembly.h | 934de0826582339878dc7a70c53f966327c6ef69 | Require idempotent no-throw abandonment callback |
| libil2cpp/vm/MetadataCache.h | 1f99a863e80a692053e57781648dba1bcc50f80c | Propagate callback through native publisher |
| libil2cpp/vm/Assembly.cpp | e46ece727d5f03a914a4a6ba147cc69bc4e0a427 | Scope-owned physical assembly vector cleanup and usage release before lock unwind |
| libil2cpp/vm/MetadataCache.cpp | f0f8124ee979d563fdd170fc13c8d90ea29bf702 | Scope-owned CLI vector cleanup on false or exception |
| libil2cpp/vm/AssemblyShadow.cpp | a03111cd93e02ea9d89cd2a3dba8e764e922ba46 | usageHeld ownership flag, idempotent ReleasePublicationUsage, unexpected publication-exit terminal marker |

**Order:** CommitTransaction transaction.mutex → g_MetadataLock → s_assemblyLock → UsageLock → Runtime reservationMutex → Codec mutex remains unchanged. The CLI rollback guard destroys first; the physical rollback guard then calls the idempotent usage callback and truncates physical entries **before s_assemblyLock unwinds**, while g_MetadataLock is still held. On normal success, each scope disarms and registry version increments as before.

**UsageLock custody:** TryBeginPublication marks usageHeld after LockUsage; both normal PublishActive exits release through ReleasePublicationUsage. The outer physical rollback guard invokes the same callback on normal failure and C++ exceptional exits. The flag prevents a second release. This is single-publication-transaction ownership, not arbitrary multiwriter access.

**Terminal unexpected exit:** CommitTransaction creates a local, no-throw ScopedUnexpectedPublicationExit around MetadataCache::PublishInterpreterAssembliesBatch. On C++ exceptional exit, after native inner cleanup, it calls the existing nonallocating FirstErrorV2::TryFreeze with UnexpectedFailure, sets s_unexpectedFailure and marks Failed or FailedAfterCommit. This is NOT the complete D1 phase receipt or a complete exception boundary for other CommitTransaction phases. The change uses scope destructors rather than native try/catch, preserving a no-exceptions compile path. A platform that does not unwind C++ exceptions is not granted a recovery contract.

**Critical limitation:** A physical/CLI vector shrink does NOT restore a published HybridCLR Codec lifecycle or Runtime publication group. The D2 scope does not claim or implement post-codec rollback.

## Test-only implementation and evidence

New hybridclr_demo files:
- Tools/AssemblyShadow/R03IR/TypeDefCensus/extract_d2_native_custody.py
- Tools/AssemblyShadow/R03IR/TypeDefCensus/test_extract_d2_native_custody.py
- Tools/AssemblyShadow/R03IR/TypeDefCensus/D2NativeCustodyHost.cpp
- .github/workflows/r03-b2-d2-native-custody-host.yml

The source extractor requires exact native HEAD and authenticates Git-tree and checked-out blobs of the five modified native files. It copies **14 C++ bodies/type definitions** into a standalone host, preserving expression bodies. A local CommitTransaction struct with an attached variable is normalized to a standalone host type declaration (host-only semicolon), **not** the full CommitTransaction function. Generated source SHA-256 on all CI jobs: **b1c5b63fde4d359ea835304218434a2989ef0230ed5cd2b2341adc4673e457b8**. Eighteen mutation/source tests per job protect the cleanup sites, callback order, idempotence and source hashes.

The host executes these cases as independent processes with mock native locks, CLI container, candidate registry, active snapshot and staging callback:
1. already-used closure denial;
2. ordinary false-return rollback;
3. successful normal publication;
4. C++ exception on second CLI append, after first succeeded;
5. exception immediately after acquiring UsageLock;
6. exception from staged publisher;
7. hypothetical exception after staged group completion;
8. **preservation of a pre-existing first-error reason** on a later exception.

Each exception case checks physical/CLI vectors restored, usage flag released **before** the assembly lock destructor, lock depth zero, unchanged version/active snapshot, and terminal/first-error receipt. The hypothetical post-group case uses a mock delegate — NOT a real Codec lifecycle; no retry safety is inferred.

[**Final exact-code CI 44255064703**](https://github.com/night-outlook/hybridclr_demo/actions/runs/44255064703): **4/4 completed success** (Ubuntu 24.04, macOS 15 × C++11, C++17). Each job passed **18/18 Python mutation tests**, strict and ASan/UBSan host executions of all eight scenarios, plus a -fno-exceptions/-fno-rtti host build and three normal cases. **19 host receipts / 287 checks per job, 76 receipts / 1,148 checks total.** All four job logs were independently read back: no native host assertion failures, ASan/UBSan errors or compile warnings.

Prior D2 runs are retained with their true conclusions:
- [44254631939](https://github.com/night-outlook/hybridclr_demo/actions/runs/44254631939): FAIL — Python test function-name typo, before C++ compile.
- [44254693065](https://github.com/night-outlook/hybridclr_demo/actions/runs/44254693065): FAIL — the host extractor initially required a plain struct terminator for a local declaration, before C++ compile.
- [44254818775](https://github.com/night-outlook/hybridclr_demo/actions/runs/44254818775): PASS 4/4 for the earlier seven-scenario set.
- [44255064703](https://github.com/night-outlook/hybridclr_demo/actions/runs/44255064703): PASS 4/4 for the final eight-scenario set.

## Primary review findings / blockers

**D2-01 PASS (bounded host):** Actual modified native source bodies compile and demonstrate physical/CLI registry cleanup and usage-release ordering under mock exception and normal-return conditions. First-error freeze preserves a prior record. -fno-exceptions compilation passes for normal paths.

**D2-02 OPEN / CRITICAL (D3):** The normal bool-false path in CommitTransaction **still restores s_state=Validated** for a Runtime failure. D2 fixes exceptional custody only. D3 must wire the actual D1 receipt before the real Codec call, independently authenticate untouched-versus-attempted state, and reject any unproved retry after CodecAttempted. The D2 vector shrink MUST NOT be reported as metadata/Codec rollback.

**D2-03 OPEN / CRITICAL (D4):** ActiveSnapshot raw pointer is published before unique_ptr release from CommitTransaction. D2 does not close the ownership gap after a late exceptional exit. A true process-wide terminal decision and memory lifetime review remain required.

**D2-04 OPEN / HIGH:** Full production native TU compilation, real libil2cpp::utils::dynamic_array shrink noexcept guarantees on all targets, native thread/GC/metadata/VM epoch, real first-error JSON, Unity/IL2CPP Player and 32-bit ABI are **NOT RUN**. Source-host type/lock stand-ins do not establish them.

**D2-05 REVIEW:** This is a Primary Implementation source and CI review, not independently issued D2 approval. The user waived *D1* interim review only. D3/D4 have not started, and all later review gates remain in force until explicitly waived or passed.

**Disposition:** D2 native source committed, host evidence PASS with mocks, product validation PENDING; WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false; PureInterpreter disabled. Inactive B2 limits (128 combined TypeDefs/64-byte names/65,536 owner lookups), original V1/B1/R02/resolver and exact source roster unchanged. No H2/M08A/X02/SNAP-01 or Human Review Gate self-approval.
