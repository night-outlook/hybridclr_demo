# R03 B2 — End-of-collection class-fact recheck (Primary implementation and source review)

**Date:** 2026-11-12 UTC. **Scope:** R03 B2 only; inactive source, no Player caller and no real Unity rebuild. **Branch:** codex/assembly-shadow-r01b-h1. **Native change:** night-outlook/il2cpp_plus@04d979fe55cea6b2dee7f5bfc49a71f2f1fb6386. **Unchanged:** night-outlook/hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55 and night-outlook/hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de. **Demo source-audit anchor:** night-outlook/hybridclr_demo@74891c675ebcb449b0a65721266d7e1559b12a03; read current pushed HEAD after doc updates. All four pinned to this branch. Original 5,222-byte enabled V1 GetExecutionDiagnosticsJson, original B1 and live R02 paths UNMODIFIED.

## Problem confirmed from actual source

Previous TryCaptureBoundedDefinitionExecutionLive copied each authenticated class's original V1 cctor_started/cctor_finished_or_no_cctor/initializationExceptionGCHandle and static_fields address. It checked (1) first physical class callback, (2) start of the second callback and (3) end of that same callback after TypeKey formatting. A late mutation to class A **during TypeKey formatting of a subsequent class B** could occur after A's last check but before the bounded record was accepted. Existing registry/image/R02 checks cannot observe a change to those class fields unless they also affect those independent sources. A successful two-pass receipt therefore did NOT guarantee that all class rows remained equal even at the end of the second traversal.

This is a genuine intra-collection *observational* hole, not a claim that the original V1 getter itself was atomic or that an all-VM epoch has become attainable.

## Decision and implementation

Add one additional **bounded end-of-collection physical class enumeration** while original g_MetadataLock and initial metadata Reader are still held, immediately after collecting all owned TypeKey/class rows and before image registry rereads or frozen record publication. Retain the first pass's 2048-slot ClassFacts value array (at most 16 bytes each); after successfully copying each row in pass two, replace that slot's first-pass value with its final primitive values. The third pass uses the existing second-pass physical::Scratch binding, plus a new bounded **2,048-byte** per-slot visited array and the existing 65,536-callback limit:

- Every third-pass registered class identity is checked as an opaque address against the already authenticated second-pass identity/registration; unknown non-registered VM classes remain ignored as in original physical enumeration.
- Read class fields **only after** that match and only inside the callback/metadata lock; compare against the latest per-class owned-row value. Error ObservedClassFactsChanged on an observed difference.
- Reject BadPhysicalEnumeration on null, duplicate registered callback, or callback budget exhaustion; reject UnmatchedClass when any previously observed class is absent from the third pass.
- Publish observedClassFactsEndPassMatched and observedClassFactsEndPassStable only after the entire source and counter/registry/first-error fences succeeded; Reject clears both new and earlier positive receipts, rows and record.
- Reuse previous stack storage rather than retaining any raw Il2CppClass* after the callback, and do not invoke an allocating original getter.

The old observedClassFactsTwoPassStable field remains scoped to its earlier checks. The new third-pass receipt names the additional observation, **not** a coherent VM/GC/cctor source epoch. This adds one full physical class enumeration and ~2KiB of callback-local visited stack storage; the existing 32KiB class-fact array remains. Real Unity stack safety/latency/RSS have not been measured. The VM iterator may allocate; no global no-allocation claim follows.

## Changes and exact test evidence

Native changes at 04d979fe55ce:

- libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl — update per-slot primitive after owned row succeeds; third matched end-pass, typed failures and final receipt.
- libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLive.h — new end-pass matched/stable receipt, poison/reset in Reject.
- NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp — five new negative scenarios: mutation of cctor at end pass, mutation of static storage at end pass, mutation of class A during later class B TypeKey, missing end-pass class, duplicate end-pass class. All rejected; existing positive rows require three physical passes and full end-pass match.
- .github/workflows/r03-native-b2-definition-live-source-host.yml — raised minimum to **81** source-mock scenarios.

Demo changed only read-only source admission and documentation. The 63-native/eight-demo candidate source manifest remains **exact** (four native Git blobs updated), new source/receipt/mode tokens and numeric limits enforced, no Local authority. Source gate tests reject false native three-pass/epoch claims and insufficient case/assertion budgets.

**Native CI:** [run 43199686419](https://github.com/night-outlook/il2cpp_plus/actions/runs/43199686419), real checked-in inactive .inl compiled with **mocked** VM; Ubuntu 24.04 × C++11/C++17 passed with Release/Debug strict and ASan/UBSan host profiles, 81 cases and 2,126 assertions per host process. The two macOS-15 C++11/17 jobs were queued at the initial review checkpoint; check final workflow result before claiming 4/4. **Exact four-fork source gate:** [demo run 43200124015](https://github.com/night-outlook/hybridclr_demo/actions/runs/43200124015) **2/2 PASS** (macOS/Ubuntu) at demo@74891c675ebcb449b0a65721266d7e1559b12a03. A subsequent doc/status update will change demo HEAD and may trigger a separate run; do not transfer an older CI verdict without checking its exact SHA.

An independent Human Review Gate and new Local Validation are NOT completed or authorized by this mock/source evidence. An unrelated legacy R02 final-source verification workflow can fail on its older frozen integration blobs; it is not the B2 host test, and must not be silently promoted to R02 acceptance.

## Source review findings

- **B2-END-01 / bounded source PASS:** source now detects the concrete previously uncovered case where a later class TypeKey changes a previously captured class's cctor value. It compares all previously admitted class facts at one later observation and rejects missing/duplicate third-pass membership.
- **B2-END-02 / observational boundary OPEN:** all three passes are serial *observations*, not a whole-VM linearization. Concurrent cctor activity could change an earlier row AFTER the end pass; ABA and mutable class/GC metadata can escape. g_MetadataLock protects the bounded metadata traversal but not necessarily every cctor/GC state mutation. No claim of terminal lifetime, thread quiescence or exact original V1 class parity.
- **B2-END-03 / class-shape completeness OPEN:** admitted source is still a registered **physical AOT TypeDef subset** with bounded composite/primitive/Unicode TypeKeys. Arbitrary interpreter/open-generic/VAR/MVAR and metadata lifetime are not covered; the original getter's full registry may be broader. No attempt to replace missing unsupported rows with zero or a placeholder.
- **B2-END-04 / performance and correctness to validate:** third il2cpp_class_for_each pass, 2KiB extra callback-local stack and existing 32KiB fact array must be compiled and profiled in actual Unity native TUs; the host mock cannot establish GC safety, pointer identity stability, native ABI compatibility, shutdown behavior or cost.
- **B2-END-05 / terminal V2 OPEN:** original complete field14/finalDiagnostics and field15/finalExecutionDiagnostics cannot yet be frozen under a proven common source epoch. Descriptor-relative native V2 binary, artifact/envelope, identity-bound receipt and independently verified recovery are not implemented. Previous full-stage R03 FAIL/High findings remain.

**Next bounded Primary-owned step:** design and prove complete original nonempty V1 execution-registry and class-shape admission (including interpreter/open generic cases) with explicit live class/GC/metadata lifetime decision and race model, then integrate both terminal-safe fields. Do not begin H2/M08A/X02/SNAP-01, reuse consumed B1 oneuse-12, or self-approve Human Review Gate.

**Final flags:** readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; PureInterpreter disabled. Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md stays **CLOSED / NO EXECUTION**.
