# R03 B2 — Original V1 interpreter-only physical TypeDef admission

**Stage:** Primary Implementation, source/host only. **Date:** 2026-11-12 UTC. **Native source:** night-outlook/il2cpp_plus@f8bf89b42cfb20ab716b7d55a7ce91d20f1875b3, branch codex/assembly-shadow-r01b-h1. Other native/package forks unchanged at hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55 and hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de. Demo anchor before final documentation commit: hybridclr_demo@818d2a9375f0a357c7839e1dc1a83d346059460a. Use the latest pushed demo remote HEAD as final provenance.

## Source diagnosis

The actual original V1 GetExecutionDiagnosticsJson reads the token-valid physical assembly table with CaptureShadowEnumeration, then builds a first-emplace MetadataTypeImages map from all images, including interpreter images, without requiring any AOT TypeDefs. The recently added inactive B2 simple-interpreter path correctly admitted a physically matched, nonnested/non-generic interpreter CLASS or VALUETYPE only from that original map. However, an unrelated global guard required registeredAotImages.Count() != 0 **before the original-V1 image visitor**. Thus, an interpreter-only physical source (nonempty V1 metadata map, no registered AOT TypeDefs) was rejected even though its supported interpreter row could have its TypeDef owner independently authenticated.

This was a source admission defect, not a demonstrated Unity runtime failure; there is no real Player result at these SHAs.

## Design and exact implementation

Only remove the **global nonempty registered-AOT TypeDef inventory requirement**, preserving its healthy-state check. Retain every individual AOT class/argument owner requirement: discovery still uses d.registry->Contains(img) for AOT; generic argument resolution still scans registered AOT images and rejects an unknown AOT or interpreter generic argument. Plain interpreter roots still require the independently observed original V1 token-valid physical image membership, handle equality and original first-emplace owner join. A registered-only interpreter root without an original image must fail closed.

The initial metadata Reader, g_MetadataLock, triple physical class-fact observations and R02/registry/B1 fences remain unchanged. An empty registered AOT source is **allowed**, not automatically considered a complete V1 capture. Neither an all-VM epoch nor GC/class pointer lifetime is established by this change.

Files changed in il2cpp_plus:
- libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl — replace the global AOT-count admission with a health-only requirement and scope comments.
- NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp — add six tests for interpreter-only physical source, including no-AOT positives and ownership/unsupported-type negatives.
- .github/workflows/r03-native-b2-definition-live-source-host.yml — require at least 94 native source scenarios.

Demo source manifest pins the three changed native Git blobs, preserves the fixed original enabled V1 getter, exact source inventory and the 63-native/eight-demo source gate, and adds explicit interpreter-only scope flags and structural negative regression tests.

## Tests, provenance and independent Primary source review

[Native host CI 43208481081](https://github.com/night-outlook/il2cpp_plus/actions/runs/43208481081) at native@f8bf89b42cfb20ab716b7d55a7ce91d20f1875b3 ran the ACTUAL inactive .inl against a synthetic VM on Ubuntu C++11/C++17 Release/Debug strict and ASan/UBSan: **both Ubuntu jobs Passed**, 94 cases and 2553 assertions per host process. Two new positives are interpreter-only plain CLASS and VALUETYPE with zero registered AOT TypeDef images; four negatives cover missing TypeDef handle, generic definition, constructed generic and absent original V1 physical image. Every rejected source revokes the owned record and all positive receipts. Both macOS-15 jobs were queued at this review checkpoint; do not claim a complete native 4/4 PASS unless they finish.

The demo four-fork CI at the final demo commit must be checked after publication. Static source gate verifies the original registered AOT per-definition check and the physical interpreter first-owner check are still present, and rejects reintroduction of the unrelated global AOT nonempty requirement. New Python regression tests mutate those source predicates and the explicit false acceptance flags.

**Finding B2-ONLY-01 / source+host scoped PASS:** an interpreter-only registry with a supported TypeDef no longer fails because no unrelated AOT TypeDef exists. The six new host cases exercised the actual native .inl with synthetic types and counters; this does not attest to real Unity/HybridCLR runtime metadata.

**Finding B2-ONLY-02 / ownership preserved in source:** AOT discovery and leaves continue to require independent registered-AOT metadata owners. Interpreter roots still require original token-valid physical first-owner; no unrestricted interpreter generic-composite or VAR/MVAR support was introduced.

**Finding B2-ONLY-03 / runtime NOT PROVEN:** official Unity 2022.3 native full translation units, real GameAssembly, class allocation origin, GC/metadata lifetime, true interpreter metadata and original V1 byte parity in Player remain NotRun. Mixed-assembly metadata ownership could still expose unsupported row kinds.

**Finding B2-ONLY-04 / lifetime and native V2 BLOCKED:** the three physical iterator passes are independent observations, not an atomic whole-VM epoch. Complete original general field14 and execution field15, correct postterminal source lifetime, one-owner descriptor-relative native V2 artifact/envelope, independent identity-bound receipt/recovery and R03 acceptance remain outstanding. Earlier native B1 oneuse-12 focused real Player 19/19 PASS is consumed and is not B2 validation. Original independent R03 full-stage FAIL/High findings remain.

**Next Primary:** systematically categorize original registered class shapes and define the class/GC/metadata source epoch necessary for complete field14+15; do not replace unsupported classes with partial or empty rows, and do not begin H2/M08A/X02/SNAP-01 without the required review.

**Flags:** readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; PureInterpreter disabled. Handoff remains CLOSED / NO EXECUTION.
