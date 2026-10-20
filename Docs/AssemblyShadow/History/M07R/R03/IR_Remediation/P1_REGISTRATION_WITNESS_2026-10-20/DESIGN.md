# R03 P1 — inactive execution registration-source witness

## Evidence basis and scope

The latest consumed Local Validation 20261020-f09e is PASS / PassedSourceHostAndSDKOnly: 16/16 components, 75 command-failure tests, five positive managed compiler products plus original expected-negative, and 90/90 native Apple arm64 SDK C++17 syntax at demo d9748b7b4c24dd567c31e59aa4885761b1d8c685, native f09edc0499fa8baf964b80256a71ce9f4d2bd522 and unchanged other two repositories. This source/host/SDK-only result is immutable and NOT Player/runtime or overall R03 acceptance.

The preceding opaque inventory compares two complete 2,048-slot snapshots and a registry-only revision but does not authenticate how an observed pointer value was registered. This increment adds a bounded, write-once registration-path witness; it does NOT prove that any Il2CppClass pointer remains live or is safe to dereference.

## Production implementation

- New native AssemblyShadowExecutionRegistrationWitness.h is a fixed 2,048-slot side table. Each write-once entry stores an opaque pointer identity and a source-kind enum: Candidate or ActiveShadow. Empty slots require None. Register rejects invalid, null and occupied entries; Matches requires exact slot identity/source without class dereference. Object storage is statically bounded to 40,960 bytes, without dynamic allocation.
- AssemblyShadow.cpp ObserveExecutionClass retains the original candidate/active-shadow physical assembly membership and candidate-first precedence. While holding the original ExecutionObservationLock, it records the corresponding source witness BEFORE publishing a new registry pointer; if witness recording fails the pointer/count/revision are unchanged and the existing dropped-observation counter advances. Duplicates and rejected sources cannot create a new witness. No additional metadata dereference, lock or initialization occurs.
- AssemblyShadowOpaqueExecutionInventory.h requires the matching witness for every sampled slot. It rejects unregistered, wrong-identity, phantom-empty and malformed source entries. Each Snapshot tracks only bounded candidate/active witness counts, not per-slot witness tags outside the lock. The existing one-shot Scratch remains within its 33,000-byte static limit; two samples still compare all slots/count, witness counts, active state/generation and the registry revision.
- AssemblyShadowOpaqueExecutionInventorySource.inl samples the table and witnesses under the original short registry lock and initial-session metadata admission, emits only numeric witnessed counts and registrationWitnessesObserved=true on complete success, and scrubs opaque pointer scratch. An incomplete source or observed change fails closed. No pointer, type key, class row or full execution JSON escapes.

These witnesses authenticate only that a pointer value was admitted by this registration path as candidate or active-shadow at observation time. They DO NOT prove physical VM allocator ownership, type-key validity, metadata lifetime, source epoch after restart, all-VM coherence, general ABA freedom, GC/RSS, Shutdown safety or Player acceptance. The original general/execution getters, C# APIs, native transport and V1/V2 business predicates remain unchanged.

## Source/host/official SDK checks

The native fixture compiles the checked-in production witness header and exact inactive collector source against explicit VM mocks. It retains 21 original cases and adds unwitnessed-pointer-refused, mismatched-witness-pointer-refused, phantom-witness-empty-slot-refused, and active-shadow-witness-admitted. Total: 25 distinct cases per strict/ASan+UBSan profile and five direct version/compile/run receipts. It records source bytes before/after. The native source runner authenticates exact original getter/guard CPP blob after stripping only enumerated approved source additions, including the real witness insertion path. Native CI covers macOS Clang, Linux Clang/GCC.

Demo preflight adds the new witness header to source and SDK custody, mock test inputs and the existing AssemblyShadowOpaqueInventorySyntax.cpp. The SDK probe checks witness-slot alignment, the 40,960-byte bound and fail-closed default receipt. The outer matrix remains 16 components, 75 Python command-failure controls, and 90 actual Apple arm64 native C++17 syntax configurations (18 translation units x five profiles), plus the original five managed positive products and expected-negative compiler control.

## Safety, performance and stopping point

The side table adds bounded static storage, one registration write only after a new class is admitted, and an extra fixed-cost per-slot check inside the current short lock during inactive capture. No process latency, GC/RSS, resource lifecycle or native Shutdown proof is claimed. Keep the feature INACTIVE; do not use the witness as permission to dereference classes. One new exact-four-SHA source/host/official SDK syntax-only Local cycle may be authorized, with new unused evidence roots, no Unity Editor/Player, no retries and no historical reclassification.

P1 stays Incomplete for true physical pointer lifetime/origin, nonempty type keys/JSON, VM-global epoch, getter integration, allocation/GC/RSS and Shutdown. P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete. Historical SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, strict S custody Blocked and independent full-stage R03 FAIL/re-review NotRun remain unchanged. All acceptance flags false; PureInterpreter disabled.
