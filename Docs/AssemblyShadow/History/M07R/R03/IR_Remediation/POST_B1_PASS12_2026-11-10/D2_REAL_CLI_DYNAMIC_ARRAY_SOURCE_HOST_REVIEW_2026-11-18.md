# R03 B2 D2 — real CLI dynamic_array rollback source/host review

**Date:** 2026-11-18 UTC. **Scope:** bounded D2 Primary Implementation follow-up, no D3/D4 integration, no real Unity/IL2CPP Player. **Branch:** codex/assembly-shadow-r01b-h1 across all four repositories. The D2 independent checkpoint remains PENDING; the user only waived the earlier D1 interim review.

## Purpose and exact source

The existing D2 test host compiled **actual native publication function bodies** but replaced the production CLI registry's il2cpp::utils::dynamic_array with a std::vector-backed test class. Because the D2 source calls s_cliAssemblies.resize_uninitialized(previousSize) in a noexcept destructor, the actual template's shrink contract and capacity behavior matter.

This follow-up reads and compiles the *real Git-pinned* native header:

- il2cpp_plus/libil2cpp/utils/dynamic_array.h @ original native D2 commit **b86a97e1dcca18163df5ac2d5f268bf6de18bbdf**, Git blob **0e6653e6e7efe93f023f63893c1a3b94f347a1d0**.
- Native publisher uses the unchanged five-file D2 source tuple (Assembly.cpp/.h, MetadataCache.cpp/.h, AssemblyShadow.cpp), all pinned by extract_d2_native_custody.py. The unchanged generated function-body source SHA-256 is **b1c5b63fde4d359ea835304218434a2989ef0230ed5cd2b2341adc4673e457b8**.
- hybridclr and hybridclr_unity remain at **4b2774b066cfc6afd77a8c8aded6bda7ea574f55** and **948c0e3b4f8891481301770115e8ba4945eea6de**, respectively. No production native file was modified this cycle.

## Source-derived findings

In dynamic_array.h the actual resize_uninitialized(size_t size, bool double_on_resize=false) writes m_size=size, then **returns immediately when m_size <= capacity()**. It only invokes reserve(size) when growing outside capacity. The D2 metadata publisher reserves s_cliAssemblies.size()+assemblies.size() **before** invoking the native assembly batch; all appends run inside that reserved capacity under g_MetadataLock and s_assemblyLock. On an ordinary false return or C++ stack unwinding, the D2 ScopedCliRollback shrinks the array to the pre-publication size, which was within the prior reserved capacity. The real source therefore supports a **non-growing shrink** at that rollback site.

Important caveats:
- The template's push_back() first increments m_size and calls reserve only on overflow. This follow-up checks the expected pre-reservation path. It is not an exhaustive test of allocation failure, corrupted capacity, UB or all OS allocator behavior.
- The exact dynamic_array.h template source is copied unchanged into a temporary host include. Its Memory.h dependencies are replaced with a test-owned aligned allocator shim; this is **not** the real il2cpp::utils::Memory allocator, FastAutoLock, GC, VM or Player.
- The shim counts real template realloc calls, asserting **one pre-publication capacity allocation and no additional allocation on shrink**, in the isolated host process. This is not a native memory allocation benchmark.
- A second mock-only profile still injects an exception during a CLI append; the actual pointer-only dynamic_array profile cannot be asked to throw at that point when pre-reserved. It instead covers pre-use denial, normal false/success, usage-acquired throw, staged throw, hypothetical post-stage throw, and prior-first-error preservation.
- The D2 exceptional terminal latch does not prove Codecs' lifecycle can be rolled back. That remains a D3-critical classification gap; D4 still owns the raw ActiveSnapshot lifetime question.

## Test code and CI method

Test-only changes, all in hybridclr_demo:
- Tools/AssemblyShadow/R03IR/TypeDefCensus/D2NativeCustodyHost.cpp: conditional compilation with D2_REAL_CLI to use exact il2cpp::utils::dynamic_array<T> in place of the original std::vector stand-in; assert retained capacity and a single allocator-shim realloc across both normal and exceptional rollback.
- .github/workflows/r03-b2-d2-native-custody-host.yml: checkout original D2 native commit and exact dynamic_array.h blob; copy the authenticated bytes to the runner temp include dir; add a small temporary Memory.h host-only shim; compile strict (-O2), ASan+UBSan and no-exceptions profiles on Ubuntu 24.04/macOS 15 × C++11/C++17. Original mock CLI tests and all 18 pinned-source mutation cases remain executed unchanged.

A **first follow-up run** (GitHub Actions 44278777181) passed initial real-template scenarios, then failed a CI assertion threshold: the prior-first-error test reports **13 checks**, not the generic >=15 threshold. No source/production fix was implied. The corrected exact test/workflow commit is **hybridclr_demo@6362aa3469abd3baa15b97b8e5cb169f602c27d1**, with [GitHub Actions 44278898831](https://github.com/night-outlook/hybridclr_demo/actions/runs/44278898831) as its authoritative run. **Final verified run: 4/4 completed/success** (Ubuntu 24.04 and macOS 15 × C++11/C++17). All four job logs were independently read back. Each completed job ran **18/18 exact-source mutation tests**, then **19 original mock-CLI host receipts plus 17 real dynamic_array host receipts**, all passing (36 receipts and **568 assertions per job**). The combined run therefore has **144 passing host receipts / 2,272 checks**; the actual dynamic_array subset contributes **68 receipts / 1,124 checks**. Strict, ASan/UBSan and -fno-exceptions C++ profiles were exercised; no compiler warnings, sanitizer faults or assertion failures were observed in the four completed job logs. The original failed parser-threshold run remains a failure, not a pass.

The host JSON explicitly marks realCliDynamicArraySource=true only in the real-template profiles, nativeRuntimeCodecActual=false, unityPlayerExecuted=false, postCodecRollbackProven=false, and all R03/H2/HumanReview acceptance flags false.

## Primary review disposition

**D2-CLI-01 — PASS, narrow source/host:** exact production dynamic_array.h has a capacity-preserving shrink path; the enhanced source-host exercises that template in the pinned D2 publisher with the test allocator. Real OS/Unity allocator integration remains NotRun.

**D2-CLI-02 — OPEN, high:** D2 pre-reservation and lock guards are necessary but do not prove concurrent VM/GC/class metadata lifetime, OS/memory allocator exceptional behavior, or that all native Player compiler/ABI targets support the exact destructor cleanup semantics.

**D2-CLI-03 — OPEN, critical:** native normal bool-false publisher path still resets Validated without a real D1 CodecAttempted receipt. Publishing the metadata index cannot be undone by shrinking registry vectors. D3 must resolve this only **after** the pending D2 review checkpoint is passed or separately waived.

**D2-CLI-04 — OPEN, critical:** D4 ActiveSnapshot ownership and post-active failure behavior are not addressed here.

**Current authority:** D2 Primary follow-up and pre-review evidence only. D2IndependentReview=Pending; D3/D4=NotStarted. WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false. No H2/M08A/X02/SNAP-01, Local Validation or project Human Review Gate authorization. B2 native limits 128 combined TypeDefs/64-byte names/65,536 owner lookups and V1/B1/R02/source roster/PureInterpreter remain unchanged.
