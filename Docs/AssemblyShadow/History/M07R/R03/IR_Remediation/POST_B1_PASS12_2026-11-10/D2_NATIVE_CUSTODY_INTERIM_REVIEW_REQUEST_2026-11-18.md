## D2 additional exact native CLI container evidence (2026-11-18 UTC)

**New input for the independent reviewer:** [real native dynamic_array source-host review](D2_REAL_CLI_DYNAMIC_ARRAY_SOURCE_HOST_REVIEW_2026-11-18.md). The D2 actual native production source pin remains **il2cpp_plus@b86a97e1dcca18163df5ac2d5f268bf6de18bbdf**, now with the exact unmodified libil2cpp/utils/dynamic_array.h Git blob **0e6653e6e7efe93f023f63893c1a3b94f347a1d0** compiled in a separate host profile. Tested demo code **6362aa3469abd3baa15b97b8e5cb169f602c27d1**. [CI 44278898831](https://github.com/night-outlook/hybridclr_demo/actions/runs/44278898831) **4/4 PASS** macOS/Ubuntu C++11/C++17: each job 18 source mutation tests, 19 mock-CLI receipts plus 17 actual-template receipts, **36 scenarios / 568 checks per job**. The first enhanced run 44278777181 had a CI assertion-count mismatch (the prior-first-error host case has 13 checks), corrected without native production edits. The template itself is exact, but allocator/VM/locks remain host stand-ins.

The new evidence supports non-growing CLI registry shrink inside pre-reserved capacity; it does **not** establish full Unity allocator/GC behavior, a complete native Player build, post-codec rollback, or an independently approved D2 checkpoint. The D2 independent review decision is still **Pending**, so D3 remains unstarted.

---

# R03 B2 D2 — interim independent review request (not completed)

**Checkpoint:** D2 native registry and UsageLock exceptional custody. The source and host tests are complete; no independent reviewer decision has occurred. Working branch codex/assembly-shadow-r01b-h1.

The user expressly waived the **previous D1 interim independent review only**. [D1 waiver](D1_INTERIM_REVIEW_USER_WAIVER_2026-11-18.md) is not an independent D1 pass and does not waive this D2 checkpoint.

## Exact tested source tuple

- hybridclr_demo **150f4a685dda170880089dbe1a930028f562056a** (D2 test/CI; documentation HEAD separately verified)
- hybridclr **4b2774b066cfc6afd77a8c8aded6bda7ea574f55** (unchanged)
- hybridclr_unity **948c0e3b4f8891481301770115e8ba4945eea6de** (unchanged)
- il2cpp_plus **b86a97e1dcca18163df5ac2d5f268bf6de18bbdf** (actual D2 source)

Read [D2 Primary review/evidence](D2_NATIVE_PUBLICATION_CUSTODY_IMPLEMENTATION_REVIEW_2026-11-18.md) and the [Approach A plan](B2_NATIVE_PUBLICATION_REMEDIATION_PREAPPROVAL_DESIGN_2026-11-18.md). Independently inspect these five native files: libil2cpp/vm/Assembly.h, Assembly.cpp, MetadataCache.h, MetadataCache.cpp, AssemblyShadow.cpp. Also inspect the unchanged D1 phase receipt and the D2 host/extraction tests under hybridclr_demo/Tools/AssemblyShadow/R03IR/TypeDefCensus.

[GitHub Actions 44255064703](https://github.com/night-outlook/hybridclr_demo/actions/runs/44255064703): **4/4 completed success**, 18 pinned-source/mutation tests per job, 76 total C++ scenario receipts across macOS/Ubuntu × C++11/C++17 strict, sanitizer and no-exceptions. Failed intermediate runs 44254631939 and 44254693065 retain FAIL; 44254818775 was a pass for the earlier seven-scenario set.

## Reviewer questions

1. Prove or refute destructor order: CLI rollback → idempotent usage release → physical rollback → s_assemblyLock unwind → g_MetadataLock unwind, on false returns and C++ exceptional exits.
2. Check callback ABI, scope object construction/destruction and real native allocator/Unity lock semantics. Standalone std::vector/std::mutex mocks are not Player proof.
3. Verify no double-unlock of another usage owner, reverse lock acquisition, or potential allocation/throw in a cleanup destructor.
4. Confirm the unexpected exit latch preserves the existing first-error record and rejects terminal business execution even with s_active=null.
5. Treat D3 **normal bool-false → Validated** without actual CodecAttempted proof as a critical open issue; do not count D2 registry cleanup as Codec rollback.
6. Treat D4 ActiveSnapshot ownership after s_active store as a critical open issue; no Product/GC/whole-VM epoch has been proved.
7. Identify remaining real Unity/IL2CPP build/Player/32-bit ABI, C++ no-exceptions and shutdown validation needs.

**Decision:** PassD2ForD3 / ReturnRequired / Blocked. A pass permits D3 only, not a Local Validation run or final Human Review Gate. A new user waiver of D2 must be separately explicit; D1 waiver does not suffice.

**Status:** AwaitingIndependentReview. WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false, PureInterpreter disabled, B2 inactive. No H2/M08A/X02/SNAP-01 or Human Review Gate self-approval.
