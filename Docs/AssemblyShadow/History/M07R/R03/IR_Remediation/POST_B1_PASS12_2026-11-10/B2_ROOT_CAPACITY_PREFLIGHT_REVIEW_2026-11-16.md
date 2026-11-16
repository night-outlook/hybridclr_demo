# R03 B2 — first-pass bounded root TypeDef capacity preflight

**Date:** 2026-11-16 UTC. **Stage:** Primary Implementation, **inactive R03 B2 only**. All repositories use branch `codex/assembly-shadow-r01b-h1`. **Native source:** `night-outlook/il2cpp_plus@cecf4b859d50b128e5c0fc6c90cd89e3a452b96a`.

## Problem and scope

The existing B2 physical-membership system admits up to 1,024 observed class identities. The combined root-plus-nonroot TypeDef owner/content audit has **128 distinct handle+owner pairs** (and two exact <=64-byte name fields per record). Thus even an otherwise valid set of 129 different class-root TypeDefs cannot fit, but previously B2 spent work on metadata owner scans, TypeKey construction, or class-row copying before recognizing the root-only impossibility. This is an **existing explicit fail-closed subset**, not a regression demonstrated in a real Player. This change does **not** enlarge or solve its capacity.

## Implementation

1. In native `AssemblyShadowPackedClassFacts.h`, a pure C++11 `CountDistinctKeysCapped<Limit>` operates on already copied dense primitive facts. A temporary linear-probing hash table of `2*Limit+1` `uintptr_t` buckets holds only opaque key values; `Limit=128` implies **257 buckets / <=2,056 bytes on 64-bit**. Its RAII destructor zeroes all entries on every return, including overflow. Nothing is allocated on the heap, no TypeDef/image address is dereferenced by this helper, and no new physical class enumeration is performed. The count is exact through 128 distinct nonzero keys and **capped at 129** after the first necessary overflow. The remaining facts are still inspected for missing keys without adding new entries, preserving the existing admission-error path for null root handles.
2. In the actual inactive B2 `AssemblyShadowBoundedDefinitionExecutionLiveSource.inl`, after a complete *first physically matched class pass*, project `ClassFacts::definition` (copied from observed, membership-matched classes) into the pure census. If `overLimit && !missingKey`, reject with existing `SourceOutsideBudget` **before** entering the second class pass or owner/TypeKey indexed lookup loops. Otherwise continue unchanged. The pure preflight proves neither physical metadata ownership nor a VM/class/GC epoch.
3. `AssemblyShadowBoundedDefinitionExecutionLive.h` adds diagnostic-only `Receipt::originalV1RootDistinctPreflightCapped`. It can be **129 on a rejected attempt**; `Reject` still revokes every positive coverage/completion flag, owned row, and frozen record. A nonzero count is NOT product-acceptance evidence. The count on a successful restricted run is an observed root-only count, not a census of nested/generic/primitive argument handles.
4. The combined audited TypeDef capacity remains 128, per-name maximum 64 bytes, audit stack <=24,576 B, total indexed metadata lookup budget <=65,536, packed class-facts capacity 1,024/2,048 slots and record size <=53,264 B. The **additional transient local stack** is bounded at <=2,056 B on 64-bit; real Unity worker-stack/lock-time cost remains unmeasured.

**Changes in native fork:** `libil2cpp/vm/AssemblyShadowPackedClassFacts.h`, `libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLive.h`, `libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl`, `NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp`. No enabled original V1 getter, B1, R02, active resolver or future native V2 was changed.

## Source-host regression and exact evidence

The source-mock harness compiles the **actual inactive .inl** against a synthetic VM. It now provides:
- **128 distinct root TypeDefs** across 128 observed classes: eligible, with 128 authenticated root declaration receipts and preflight count 128.
- **129 distinct root TypeDefs:** `SourceOutsideBudget` after the FIRST class pass (not the second), retained diagnostic count 129, no indexed TypeKey owner work and no positive/frozen source output.
- **129 observed classes sharing ONE root TypeDef:** eligible, with one exact root audit pair, proving the limit concerns distinct handles rather than class identities.
- **Four additional pure packed-facts tests:** repeated key in a 1,024-row scratch, 128 distinct adversarial hash-colliding keys, 129 distinct colliding keys, and an invalid/missing key without early error substitution.

The mock supports extended indexed handles in a dedicated optional table, not by increasing the size of every mocked `Il2CppImage`. [**Native source CI 43792802567**](https://github.com/night-outlook/il2cpp_plus/actions/runs/43792802567) **4/4 PASS**, macOS-15/Ubuntu-24.04 × C++11/C++17, Release/Debug strict and sanitizer profiles, **158 scenarios and 8,711 assertions per execution**. Results explicitly state `realUnity=false`, `R03Accepted=false` and `nativeV2TransportImplemented=false`. The demo exact source-gate requires a separate code SHA and final docs-HEAD check.

## Capacity redesign decisions still required

This is **necessary, not sufficient**: 128 roots may still combine with nested/generic/primitive TypeDef leaves to exceed the 128-pair limit; any such overflow still fails later. The capped 129 diagnostic is a lower bound on the needed root capacity, NOT the full needed allocation. The existing 65,536-lookup owner budgets may also fail independently even if larger owner storage is introduced.

Two future Primary candidates worth considering after a defensible source census are: (A) a bounded, caller-preallocated heap slab with at least the actual root-plus-leaf high-water count, allocated **before** entering metadata locks; or (B) a compact separately bounded key/index plus exact-string arena to reduce allocation size while preserving byte-exact owner and declaration checks. Neither candidate is approved or implemented here. Both need validated lifetime, allocation-failure, metadata lock/latency, 32/64-bit stack/heap and GC/VM-source epoch behavior. Simply raising the 128 constant on the current stack-allocated array would violate the reviewed 24,576-byte bound.

**Outstanding:** full original V1 execution field15 / general field14, terminal-safe immutable snapshots, descriptor-relative authenticated native V2 artifact/envelope/independent receipt/readback/first recovery, real Unity 2022.3 native TU/Player, GC/class lifetime, coherent VM-wide epoch, and independent R03 historical FAIL/High findings. The old R02 source-verification workflow has an unrelated historical byte-pin mismatch in `AssemblyShadowTypeResolver.cpp` and `AssemblyShadow.cpp`; do not describe all native CI as green.

**State:** `readyForNativeV2FieldCapture=false`; `nativeV2TransportImplemented=false`; `runtimeAcceptance=false`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; `wholeVmEpoch=NotProven`; PureInterpreter disabled. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`. No Human Review Gate self-approval, oneuse re-run, or H2/M08A/X02/SNAP-01 work.

## Verified exact-source code-anchor CI

[**Demo 43793630092**](https://github.com/night-outlook/hybridclr_demo/actions/runs/43793630092): **2/2 completed/success**, macOS-15 and Ubuntu-24.04 at demo code `46229153cc1b690bebed875a180c1e72fbba131a`, native `cecf4b859d50b128e5c0fc6c90cd89e3a452b96a`, hybridclr `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, and hybridclr_unity `948c0e3b4f8891481301770115e8ba4945eea6de`. The exact four-repository gate verified **64 native/eight demo Git blobs**, 47 Python source-admission unit tests **per OS**, the unmodified original V1 getter and false product/VM/V2 flags. Reported status `PassedInactiveSourceOnly_NotFullV2`, `handoffAuthority=CLOSED_NO_LOCAL_EXECUTION`. This is source/host only; the subsequent evidence-only documentation commit requires its **own** exact-HEAD CI verdict.

The ancillary R02 source verification at [native run 43792802559](https://github.com/night-outlook/il2cpp_plus/actions/runs/43792802559) remains **Failed** on historical `AssemblyShadowTypeResolver.cpp` and `AssemblyShadow.cpp` byte pins, neither changed by this preflight. Targeted native B2 4/4 and demo 2/2 PASS do not make full repository CI green.
