# R03 B2 — Actual Runtime/Codec plus pinned native publication: post-group fault checkpoint

**Date:** 2026-11-18 UTC  
**Branch:** codex/assembly-shadow-r01b-h1  
**Scope:** Primary Implementation, source-host integration and failure analysis only. No production native modifications, Local Validation authority, Unity Player or Human Review Gate approval.

## 1. Purpose and provenance

The previous compiled native-body host injected a C++ exception *before* the real HybridCLR Codec/Runtime. It proved that the literal native functions do not release a manually held UsageLock or roll back either assembly registry vector when a mocked deep callback throws. It did **not** prove which HybridCLR metadata lifecycle state would remain if the Runtime had already published its group.

This checkpoint compiles the **same exact literal native function bodies** together with the **actual pinned HybridCLR InterpreterMetadataIndexRuntime.cpp and Codec.h**. The only substituted components are the native VM/Unity structures and locks, the staged assembly-to-Runtime delegate, a minimal il2cpp-config.h, and the AssemblyShadowBridge private/public predicates. Each scenario runs in a **new process**. The test does not reset an inconsistent global state in order to claim a successful retry.

| Repository | Exact commit used |
| --- | --- |
| night-outlook/hybridclr_demo (tested code and CI) | 65bb926c5ef48499c389448b67a395c439dc60fe |
| night-outlook/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | cecf4b859d50b128e5c0fc6c90cd89e3a452b96a |

Test file:
Tools/AssemblyShadow/R03IR/TypeDefCensus/NativeRegistryActualRuntimePostGroupHost.cpp
(Git blob dd611232ab1d4d719ad5bfc9bdf0904135c1660e).

Workflow:
.github/workflows/r03-b2-native-actual-runtime-post-group.yml
(Git blob 75955e7ea6689fdb3487cd61ff92b2dfd5c7063c).

The native extraction uses the previously verified, unchanged source pinning tool. Its generated native-body source SHA-256 is fixed at
9c6a27315f0fecefb52b7c80c838ef4d870dbf7e1184be8e0d21402c26aa5b8c.

**Three native source blobs (literal definitions):**
- libil2cpp/vm/Assembly.cpp — df1acbfdaf054067720d2e7c1545e49100ad93ec
- libil2cpp/vm/MetadataCache.cpp — b9a9881c6e6a551c19069446a9be61c21f4c8584
- libil2cpp/vm/AssemblyShadow.cpp — dc941907884b9a7f44ade6085d05f2e4a1a96d9e

**Four pinned actual Runtime/Codec source blobs:**
- hybridclr/metadata/InterpreterMetadataIndexCodec.h — 2020d4e2da6dea8601525203e7ab307d21c40a73
- hybridclr/metadata/InterpreterMetadataIndexRuntime.h — c39ac0f5a0c1ea93c55d51e04d25d31a71775260
- hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp — 509e357359a8912c05adac3434a7e71b3fc3f83c
- hybridclr/metadata/AssemblyShadowBridge.h — 5340c0bf9e4c4c211b4379929f3f79133661505a

All Git commit, tree-blob and checked-out-file SHA checks are performed by CI. Only hybridclr_demo is written.

## 2. One-cycle design, implementation and validation

1. Reuse the exact-source native extraction, without modifying the extracted native functions.
2. Link the actual HybridCLR InterpreterMetadataIndexRuntime.cpp/Codec.h into a standalone host executable. Real Runtime::ReserveImages, ScopedConstruction, Encode, Finalize, PublishBatch, Decode, GetPublishedImage and Abort are executed.
3. Define a minimal staging adapter that calls **actual** Runtime::PublishBatch; it may deliberately throw **after a successful return** but before the unchanged native PublishActive can store s_active. Native StagedAssembly.cpp is **not** compiled, and that callback's ability to throw in a Unity build is **not** established.
4. Preserve a mock native s_active pointer whose release-store is performed by the exact native PublishActive body. A mock AssemblyShadowBridge::IsPublicImage gates Runtime public visibility against that pointer; this is **not** the real IsActiveShadow map or whole-VM epoch.
5. Execute each independent scenario in its own process. Do not reset native/Runtime process globals or call the publication path again in a post-group fault process.
6. Run both C++11 and C++17 on Ubuntu 24.04 and macOS 15, strict and ASan/UBSan profiles, with exact receipt assertion and a separate initial pinned-native extraction suite.
7. Review the exact CI output and stop before production mutation.

## 3. Five separate-process scenarios

| Case | Real Runtime invoked? | Outcome |
| --- | --- | --- |
| used-rejection | No | Native TryBeginPublication rejects used candidate before registry append; both registries empty and metadata image remains private |
| precodec-false | No | Mock staging delegate returns false; native false-return rollback clears both vectors and UsageLock; metadata image remains private |
| codec-unfinalized | Yes | Actual Runtime/Codec rejects unfinalized image; native false-return cleanup succeeds, image remains private |
| runtime-success | Yes | Actual Runtime/Codec group publication succeeds, native s_active is set by the literal native callback, mock Bridge grants public visibility; Abort and duplicate publication reject |
| **post-group-throw** | **Yes** | Actual Runtime/Codec group returns None, then TEST-only staging adapter throws before native s_active store; registries remain appended, UsageLock remains held, native s_active=null; Runtime public resolver remains gated while **Abort and republish both reject** |

The last scenario contains the decisive distinction: metadata publication cannot be undone by merely shrinking either native registry vector. The actual Runtime returns InvalidState on Abort and repeated Publish; the implementation has already recorded publication-group membership. This is a **source-host, mocked-VM partial-commit demonstration**, not empirical Unity recovery evidence.

## 4. CI and scope of successful evidence

[GitHub Actions run 44231606845](https://github.com/night-outlook/hybridclr_demo/actions/runs/44231606845), tested at demo code 65bb926c5ef48499c389448b67a395c439dc60fe:

- **4/4 completed/success jobs**: Ubuntu 24.04 and macOS 15 × C++11 and C++17.
- Each job: **10/10 original native extraction tests**, exact source SHA verification, two compile/run profiles (optimized strict and ASan/UBSan).
- Each profile runs **five isolated process invocations**, with assertions of scenario name and all evidence/acceptance restrictions. **40 machine-readable scenario receipts total** across the four jobs.
- Per profile, check counts: used-rejection 18; precodec-false 18; codec-unfinalized 18; runtime-success 20; post-group-throw 20. This is **94 checks per profile**, **752 checks across 8 profiles**. These counts represent host assertions, not Unity product or runtime acceptance.
- GCC produces a **visible nonfatal -Wmaybe-uninitialized warning** for the pinned Runtime.cpp FootprintStats::sealed (previously documented); only this warning category is downgraded, not hidden or repaired.
- All receipts retain nativeVmMocked=true, bridgeMocked=true and nativeProductionModified=false; safeRecoveryProven=false, exceptionSafePublicationProven=false, realUnity=false, R03Accepted=false, H2Passed=false and ReadyForHumanReviewGate=false. No skip is promoted into a pass.

No known failed run of this specific workflow was published before run 44231606845. Historical failed attempts in other R03 B2 workflows remain separate.

## 5. Primary code/evidence review

**POSTGROUP-01 — HOST-PASS, HIGH finding:** Compiled native bodies + actual Runtime/Codec confirm that after the real group has committed, an injected exceptional exit may leave the two native registries populated, the manual UsageLock held, and native s_active absent. The Runtime group is not restored to private state; Abort and repeat Publish are rejected.

**POSTGROUP-02 — HOST-PASS, scope restriction:** The real Runtime Public helper is guarded by a mock VM active predicate, so public resolution and Decode return private-owner rejection while native s_active remains null. The test proves only the *mock gate plus actual Runtime* behavior, not the real Bridge→VM map or concurrent readers.

**POSTGROUP-03 — OPEN / CRITICAL:** A successful Runtime::PublishBatch is a point of irreversible metadata publication, yet the native CommitTransaction bool-false handling can label failure as Validated. The host failure throws rather than returns false and therefore does **not** exercise the actual CommitTransaction false-return reset, because the full native CommitTransaction body is not compiled. The production failure-policy implementation remains unverified; do not infer a safe retry.

**POSTGROUP-04 — OPEN / HIGH:** Because the test injects a throw in a mock staging callback immediately after real Runtime success, it does not show an actual HybridCLR runtime callback throws in that interval. Native s_active ownership, ActiveSnapshot lifetime, complete Unity code-generation and ABI semantics, reentrant locking, GC/class metadata epoch, concurrency and real Player behavior remain untested.

**POSTGROUP-05 — OPEN / HIGH:** Even if an RAII lease fixed UsageLock unwind and both vector scopes were corrected, the already committed Runtime group would still be irreversible. A production correction must be phase-aware and terminal on any unknown post-codec result. A test-only cleanup is not a rollback.

## 6. Next design boundary

See the separate *pre-approval remediation proposal* in this checkpoint directory. It must be reviewed before native code changes; it is **not** a self-issued approval. Work may continue on independent diagnostics/test infrastructure without changing the pinned production semantics.

Native B2 remains inactive at **128 combined TypeDefs / 64-byte declaration fields / 65,536 indexed owner lookups**. Original V1/B1/R02/resolver, source rosters and PureInterpreter remain unchanged. WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false. No H2/M08A/X02/SNAP-01, consumed Local replay or Human Review Gate self-approval.
