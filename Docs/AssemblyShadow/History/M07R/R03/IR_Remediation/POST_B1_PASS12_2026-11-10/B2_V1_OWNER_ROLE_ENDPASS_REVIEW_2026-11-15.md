# R03 B2 — exact original V1 owner-derived execution flags re-observed

**Date:** 2026-11-15 UTC. **Stage:** Primary Implementation, **INACTIVE R03 B2 only**. **Branch:** `codex/assembly-shadow-r01b-h1`. **Native revision:** `night-outlook/il2cpp_plus@41f92438bc2c1e76613ddc7e0aa70a5e33f46c29`. No Local Validation authority, H2/M08A/X02/SNAP-01, or Human Review Gate approval.

## Defect, proven from the existing native source

The exact original V1 `GetExecutionDiagnosticsJson` computes `interpreterShadow=(baseline||shadow)`, `physicalInterpreter=Interpreter(owner)`, and `isActive=!baseline` from the class's physical owning assembly and the `ActiveSnapshot` membership. The inactive bounded B2 second pass copied those three boolean values into `Rows`; the third physically matched class pass then rechecked root TypeDef shape, class cctor/static, and byte-exact `logicalAssembly`, **but did not compare those three stored owner-derived values**. It also did not explicitly recheck `image->assembly->image==image` before reading the owner's name. Observable changes in source values, without changing the image pointer or assembly name, could leave previously copied flags in the frozen class row.

The V1 JSON serializer's real field names are `executionModeCode`, `executionMode`, `physicalImageKind`, and `isActive` (not the private `interpreterShadow` and `physicalInterpreter` struct field names). The original serializer was not changed.

## Scoped implementation

- `libil2cpp/vm/AssemblyShadowOwnedExecutionRows.h` adds `SameCollectingV1OwnerFlags(slot, interpreterShadow, physicalInterpreter, isActive)`. It uses the existing one-based `uint16_t[2048]` insertion-slot map, and compares exactly the copied three `Flags` members. Reject absent slots, stale index or stages after `Seal`. No new stored fields, heap, class pass, or buffer.
- `libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl` carries the already borrowed immutable active-snapshot pointer in `EndPassFacts`. Inside the **existing third class callback**, and still under the initial metadata Reader/`g_MetadataLock`, it checks the physical `owner->image` backlink, unchanged byte-exact class `logicalAssembly`, and recomputes `baseline||shadow`, `Interpreter(owner)`, `!baseline` for comparison against the owned row. Any observed mismatch reports existing `SourceChanged` and revokes the entire source and positive receipts.
- `NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp` adds four negative synthetic-VM cases (owner physical-interpreter flag drift with unchanged image token, baseline membership removed, shadow membership added, assembly-image backlink changed) plus one positive stable ActiveShadow row with the exact legacy JSON `executionModeCode=1`, `executionMode="InterpreterShadow"`, `physicalImageKind="Aot"`, and `isActive=true`.
- Demo's `BoundedOwnedExecutionRows.h` pure header is updated to match native byte-for-byte except three local include spellings. The 64-native/eight-demo exact source manifest, admission rules, negative capability tests, and four-pin CI workflow pin the revised sources.

## Evidence and test correction

The initial native code commit `51c7b121626d2e5b38dd3f0c339330dc48b3963f` failed its new positive host assertion because the test expected private `Flags` names in serialized JSON. Direct inspection of `AssemblyShadowExecutionSerializer.h` showed the actual original V1 public field names above. Only the regression test assertion was corrected; the production bounded source logic remained unchanged.

[**Native actual inactive .inl CI 43727437923**](https://github.com/night-outlook/il2cpp_plus/actions/runs/43727437923): **4/4 PASS** macOS-15/Ubuntu-24.04 × C++11/C++17. Each Release/Debug strict/sanitized host execution reports **151 cases and 7,390 assertions**, `realUnity=false`, `R03Accepted=false`, and `nativeV2TransportImplemented=false`. This compiles the checked-in .inl with a synthetic VM only, **not** Unity's real native C++ TU or Player. Demo four-fork CI at the new exact demo SHA must be checked separately.

## Limitations and remaining Primary work

The re-observation detects observed changes between the earlier copied row and third callback only, not ABA or changes after the final callback. The initial `ActiveSnapshot` pointer is re-read for membership; neither its lifetime nor concurrent mutation safety is proven by the synthetic cases, and an inconsistent whole-VM epoch is **not** established. It does not establish all generic argument/type owner assembly-name contents, complete original V1 execution field15/general field14, or terminal-safe native V2. It neither increases nor solves the combined 128 distinct TypeDef audit cap, 64-byte declaration names, 24,576-byte audit scratch, or real Unity worker-stack/metadata-lock/GC performance concerns.

Historical independent R03 FAIL/High findings remain open. Native R02 historical source-pin CI has been failing on unrelated preexisting `AssemblyShadow.cpp` and `AssemblyShadowTypeResolver.cpp` pins; do not claim all native workflows green from the targeted source-host PASS. The prior B1 oneuse-12 focused Player result cannot substitute for B2 Player evidence.

**Product flags:** `readyForNativeV2FieldCapture=false`; `nativeV2TransportImplemented=false`; `runtimeAcceptance=false`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; `wholeVmEpoch=NotProven`. PureInterpreter disabled. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`. No Local batch or later milestone is authorized.
