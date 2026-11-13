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
