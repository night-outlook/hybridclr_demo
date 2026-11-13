# R03 B2 — explicit root/non-root TypeDef-use roles

**Date:** 2026-11-13 UTC. **Stage:** Primary Implementation self-review, inactive B2 only. **Branch:** `codex/assembly-shadow-r01b-h1`. **Native source:** `night-outlook/il2cpp_plus@94e5312b8ee167384820f8ab58ee9661dfc7bfb3`. **Demo code/source gate:** exact new HEAD in GitHub.

## Defect and correction

Previously, `resolveOwner` tagged a TypeDef as root using `handle==klass->typeMetadataHandle`, ignoring its *use site*. A shared TypeDef that was also a generic argument of the same class therefore failed to acquire the non-root role; the deduplicated owner and exact content audit still ran, but scoped non-root receipt counters underreported its coverage.

The class's initial `buildDefinition` call now passes `classRootDefinition=true`; all composer leaves, constructed generic bases and primitive-default definitions pass `false`. Only depth zero of the initial class definition is root: `classRootUse=classRootDefinition && depth==0`. Declaring-type ancestors and argument leaves are non-root even when their handles equal the current class-root handle. The existing `NonRootOwnerAudit::Note` continues to merge both roles on **one authenticated TypeDef handle+image pair** and preserves exact copied content. No new allocation, class pass, or owner capacity was added.

The new `GenericRootAlsoArgument` synthetic-VM test uses one root handle as an argument plus a second distinct argument, requiring **two distinct pairs / one root role / two non-root roles**, correct constructed TypeKey and unchanged fail-closed receipts. It tests role accounting; the synthetic constructed type is not proof of a legal arbitrary C# generic instantiation or real Unity behavior. Exact source-gate requirements reject reverting to inferred root role.

## Bounded validation and current evidence

Native files: `libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl` and `NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp`. The two new Git blobs and native commit are pinned in `Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json`. Connector remote write/readback succeeded. **New exact native/demo CI still requires independent check**; the prior 133-case native CI 43373757923 must not be promoted to this commit. No official Unity C++ TU, GameAssembly, Player, metadata/GC lifetime, or native V2 evidence is claimed.

## Open conditions and stop point

The combined **128-distinct TypeDef** and <=64-byte name-field bounds, <=24,576-byte audit object and <=65,536 metadata lookup budget remain. A defensible real-source TypeDef census, class/GC/metadata lifetime/VM epoch design, full terminal original V1 fields14/15, and descriptor-relative native V2 writer/envelope/receipt/first-recovery are outstanding. Historical independent R03 FAIL/High findings remain. `readyForNativeV2FieldCapture=false`, `nativeV2TransportImplemented=false`, `runtimeAcceptance=false`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `wholeVmEpoch=NotProven`; PureInterpreter disabled. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; no Local batch or later milestone is authorized.

## CI checkpoint after workflow pin reconciliation

- **Native exact SHA `94e5312b8ee167384820f8ab58ee9661dfc7bfb3`:** [workflow 43396033155](https://github.com/night-outlook/il2cpp_plus/actions/runs/43396033155) 4/4 completed/success, Mac/Linux C++11/17; Release/Debug strict/sanitized; 134 scenarios and 6688 assertions per host execution.
- **Demo initial source gate 43396487900:** 2/2 failed *before source audit* because `.github/workflows/r03-ir-b2-definition-four-pin-source.yml` still checked out and required stale native `f89b9e9323df1234bf1bc59ca7f418533c958246`. No new source check was exercised. The workflow now pins `94e5312b8ee167384820f8ab58ee9661dfc7bfb3` at all four places; rerun via the workflow-file commit. Do not count the original failing gate as source evidence.
- **Unrelated native R02 workflow 43396030879:** failed its historical `tools/r02/finalize_sources.py --verify` byte-pins for `AssemblyShadowTypeResolver.cpp` and `AssemblyShadow.cpp`, neither changed in this B2 cycle. The targeted B2 source matrix is separately green; do not claim all native CI is green.

The demo source-audit CI at the final doc HEAD must still be inspected. Scope and acceptance flags above are unchanged.

## Exact four-repository source-gate result

[**Demo CI 43396819207**](https://github.com/night-outlook/hybridclr_demo/actions/runs/43396819207): 2/2 completed/success on macOS-15/Ubuntu-24.04 at demo `ad03a03f5e73f66db42b7c86cf68e07ab5b47ce1` and native `94e5312b8ee167384820f8ab58ee9661dfc7bfb3`, with frozen hybridclr/hybridclr_unity branches. Each OS passed 43 source-gate Python tests; verified 64 native and eight demo Git blobs and original V1 getter provenance. Both results report `PassedInactiveSourceOnly_NotFullV2` and keep `handoffAuthority=CLOSED_NO_LOCAL_EXECUTION`. This does not verify the later documentation commit without its own exact-HEAD result.

Primary code review: no new class visitation, native heap allocation, extra audit pair, changed 128/64-byte limits, original enabled getter modification, or premature positive product/VM predicate was introduced. The mock scenario is synthetic and cannot supply GC/type lifetime evidence. This is a scoped Primary review, **not** an independent Human Review Gate.
