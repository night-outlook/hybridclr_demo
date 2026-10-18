# R03 P1 — bounded execution-header scalar capture (isolated Primary staging)

**Status: implemented and host-source-tested on an ISOLATED staging branch. NOT MERGED to the active Assembly Shadow feature branch. NOT authorized for Local Validation or Unity/Player execution.**

## Branch/source authority

- Staging native: `night-outlook/il2cpp_plus`, branch `codex/p1-execution-scalars-20261018`, base exact active SHA `5667e3712f49e4b38c7dd7359e57f81e344626da`. Host-tested source commit `39d4637b868726c92f50d1db92a5c269ff0bafe5`.
- Staging documentation: `night-outlook/hybridclr_demo`, same staging branch, based on active demo `25d5986c5919ab70119364ce36e8b670329ad5b0`.
- `night-outlook/hybridclr` remains `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, and `night-outlook/hybridclr_unity` remains `948c0e3b4f8891481301770115e8ba4945eea6de`.
- **The canonical active branch `codex/assembly-shadow-r01b-h1` remains unchanged** and continues to authorize exactly the already published *12-component / 75-native-syntax* inactive general-source Local Validation at those original active SHAs. This staging branch does NOT replace, extend, retry or cancel that assignment.

## Focused design

The currently active `AssemblyShadow::GetExecutionDiagnosticsJson` first samples the native execution header counters, then builds a metadata type-key map, formats class rows and appends R02 details, with allocating `std::vector`/`std::ostringstream` operations. The staged next increment extracts **only the immutable execution diagnostic scalar header** into a dedicated, caller-preallocated, fail-closed Capture. It does not attempt class/type-key enumeration, complete execution JSON, R02 detailed metrics or Player integration.

Changes isolated to the native staging branch:

1. `libil2cpp/vm/AssemblyShadowBoundedExecutionHeader.h`: captures the exact existing `assembly_shadow_execution_diagnostic::Header` scalar fields (`stateCode`, `state`, `generation`, method checks, rejected and shadow checks, class-cctor counters, interpreter transformations and dropped-class observations). Rejects invalid state, impossible subset > total, missing counter thread coverage, saturated counters, multiple uses, and a **witnessed** before/after difference. Uses a statically mapped enum state name on output rather than retaining the caller's string pointer. The complete object is statically bounded to 256 bytes.
2. `libil2cpp/vm/AssemblyShadowBoundedExecutionHeaderSource.inl`: a native method `AssemblyShadow::TryCaptureBoundedExecutionHeader` that holds one initial-epoch MetadataLifetimeGate reader while sampling the same atomic R02-backed scalar sources in the same acquire/relaxed order as the original getter. It collects two copies, checks both live dropped-thread/saturation flags, and compares ActiveSnapshot pointers/state **outside** the field-read windows too, to reject a state/active publication occurring during the second sample. No metadata class or type pointer is dereferenced apart from the admitted retained ActiveSnapshot generation.
3. `AssemblyShadow.h` declares the inactive method under the existing feature enablement, and `AssemblyShadow.cpp` includes it in its owning native TU. No old getter, public C# API, engine-owner adapter or native V2 wire path changes.
4. `tools/r03/diagnostic_stream/bounded_execution_header_fixture.cpp` and `run_bounded_execution_header.py`: host tests compile the **exact production .inl bytes** with real bounded Capture / original serializer and explicitly modeled VM atomic/metadata-source controls, including a deterministic state flip within the second scalar read (the window that a simple pairwise-header comparison could miss).
5. `.github/workflows/r03-p1-bounded-execution-header-staging.yml` executes strict and ASan/UBSan host suites under macOS Clang and Linux Clang/GCC **on this staging branch only**, without running Unity/Player or changing the active feature branch's workflow.

## Exact host checks, limits and evidence

[Staging native CI run 39095475904](https://github.com/night-outlook/il2cpp_plus/actions/runs/39095475904) **PASSED 3/3 jobs**, each **13 strict + 13 ASan/UBSan groups**, **78 passing group executions and 12 compilation/test subprocesses with exit0**. The exact production method's SHA256 was `3faac86c05fff40eaab190d1621eb8eb68b450785bd9a399ab458568cf96024a` in all three outputs. The three original ZIP digest identities match GitHub's artifact records, and all **57/57 manifest-declared files** were independently checked for bytes and SHA256.

Coverage includes: original `AssemblyShadowExecutionSerializer::Begin` header-byte parity (classless prefix only), zero watched new-allocations after locale prewarm, invalid/missing state, impossible subset/total ratios, denied saturated/dropped-thread metric coverage, counter change, state change *during* the second sample, active snapshot pointer replacement with the same generation, single-use fail-closed capture, no retained mutable state pointer and closed metadata admission. The fixture substitutes only VM state/counter writers; it does **not** establish real source synchronization.

The first CI attempt [39095444605](https://github.com/night-outlook/il2cpp_plus/actions/runs/39095444605) FAILED: a source-contract test incorrectly expected one read of `ObservationCounters::DroppedThreads` and `Saturated` when the implementation correctly requires two. Primary corrected the test's expected count to two and re-ran on the staging branch; the original failed CI record is preserved. The correction did not change the execution reader's production behavior.

**NotRun / not proven**: actual installed Unity2022.3.62f2 SDK native compilation for these staged changes; full live `AssemblyShadow.cpp` link; `GetExecutionDiagnosticsJson` replacement; class/type-key recursion/cctor/static storage capture; R02 detailed metric set; global VM epoch, ABA exclusion, GC/RSS, native metadata teardown/lock deadlock freedom; Engine E0/E1 owner scheduling and Player semantics. The metric snapshots are two independently sampled aggregates from per-thread atomics, not a coherent all-VM timepoint. Early/prewarm Data() initialization and process RSS have not been qualified by host `operator new` checks.

## Merge and Local Validation gates

1. **Do not merge or cherry-pick staging into the active branch before the active 12/75 `WEB_TO_LOCAL.md` attempt returns a factual result**, or before Primary explicitly consumes/reconciles that one-shot authorization. The current active Local test is source-pinned and must not be invalidated.
2. After the active Local report, Primary must independently review the returned evidence, preserve PASS/FAIL distinctly, verify the four actual remote SHAs, and review this isolated branch relative to its native active-base SHA. Resolve any conflict against actual source changes, not by replacing previous evidence.
3. When merged, add the scalar-header source to a **separately reviewed, new source+SDK-only candidate validation**; update the active demo aggregate with a new `execution-header` child and exact native hash/source bindings. Local must then compile the real updated `AssemblyShadow.cpp` under the official SDK matrix and report factual results. **No current executable Local command or fresh output root is authorized by this staging design.**
4. Engine owner capability, real Reader lifetime, original getter wiring and P2 remain independent Primary engineering gates; do not promote the host suite to runtime safety.

## Historical states preserved

Earlier Local `20261016-3dc9` PASS 11/11, `20261016-f598` PASS 10/10, `20261016-0620` PASS 10/10 and `20261016-0a0b` FAIL 9/10 are all separately consumed, not reclassified. SNAP-01 FAIL/ReturnRequired (14/18), N/M/K/I/E FAIL, the historical R02 whole-file fingerprint FAIL, original strict S custody Blocked, and independent full-stage R03 review FAIL/rereview NotRun remain unchanged.

**P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete**. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. No Human Review Gate, Player or new milestone is authorized.
