# R03 B2 — exact root Il2CppType bitfield source fence

**Date:** 2026-11-13 UTC. **Scope:** Primary Implementation, inactive R03 B2 source only, four repositories on `codex/assembly-shadow-r01b-h1`.

**Native change:** `night-outlook/il2cpp_plus@f6584984c2f175f42e1b071cc99007e1d3eef185` (`libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl`, `NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp`). The candidate manifest records the exact two Git blob SHAs; hybridclr and hybridclr_unity source pins remain unchanged.

## Source-derived defect

The previous `ClassFacts::Read` copied root image, metadata TypeDef handle, byval data pointer, generic-class pointer, and the 8-bit `Il2CppType::type` tag, plus cctor/static facts. The initial row admission rejected nonzero `attrs`, `num_mods`, `byref` and `pinned`, but the third class traversal only compared `type` and the pointer. A post-row change of a previously checked qualifier could therefore evade `SameRoot` while the immutable TypeKey still represented the earlier value. `valuetype` was also omitted. This is a bounded observation gap, not proof of an actual concurrent Unity metadata mutation.

The original `libil2cpp/il2cpp-runtime-metadata.h` declares **exactly 32 bits** of six `Il2CppType` members: `attrs:16`, `type:8`, `num_mods:5`, `byref:1`, `pinned:1`, `valuetype:1`. These bitfields are read individually and combined by unsigned shifts (16, 24, 29, 30, 31), not via aliasing compiler-dependent bitfield storage. The pre-existing `uint32_t typeCode` member becomes `uint32_t typeBits`. `SameRoot` compares the complete packed value.

## Regression and limits

Five new synthetic-VM end-pass cases mutate separately `attrs`, `num_mods`, `byref`, `pinned`, or `valuetype`, without modifying class/image/TypeDef/payload pointer identities. Every case must return `ObservedClassRootChanged`, revoke owned rows and all positive source receipts, and preserve existing first error. Combined with the existing cases, the exact native source-host [CI 43429814337](https://github.com/night-outlook/il2cpp_plus/actions/runs/43429814337) completed **4/4 PASS** Mac/Linux C++11/17 with 139 scenarios and 6873 assertions for each Release/Debug strict/sanitized host execution. Tests compile the checked-in inactive .inl with a SYNTHETIC VM, not Unity's native translation unit.

No extra `ClassFacts` member, stack, heap, physical class pass, source access after terminal, native V1 getter, B1, R02, active resolver or native V2 writer was added. Existing `static_assert(sizeof(ClassFacts)<=48)` and packed-facts <=53,264 B remain unchanged. The demo source gate requires the six exact bitfield declarations, all pack shifts and five regression modes. It must pass at the new demo exact HEAD before declaring cross-repository source qualification.

**Remaining:** 128 combined TypeDef pair cap; 64-byte names; source-derived real-game census; stable class/GC/metadata ownership, generic-context and assembly-name contents; a coherent whole-VM epoch; complete original V1 finalDiagnostics field14 and finalExecutionDiagnostics field15; terminal-safe immutable source; descriptor-relative native V2 artifact/envelope, independent receipt/readback and first recovery; real Unity native TU and Player validation. Repeated observations do NOT prove post-sample stability or class/GC lifetime.

**Product flags:** `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven`; PureInterpreter remains disabled; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`. No H2/M08A/X02/SNAP-01 or Human Review Gate approval. The ancillary R02 historical source-pin CI failure is unrelated and remains open.

## Verified four-fork source CI

[**Demo CI 43430276852**](https://github.com/night-outlook/hybridclr_demo/actions/runs/43430276852): **2/2 completed/success**, Ubuntu-24.04 and macOS-15 at `night-outlook/hybridclr_demo@a6360bd9d629cb0b9597f666a25d158472990dd6` and `il2cpp_plus@f6584984c2f175f42e1b071cc99007e1d3eef185`, with unchanged hybridclr/hybridclr_unity pins. The exact source gate ran after pinning the native two-file change, validating 64 native/eight demo blobs, original V1 getter provenance and fail-closed product flags. Independent Primary static inspection matched six original Il2CppType bitfield widths and all five negative `ObservedClassRootChanged` cases. **This is source/host only**; it does not prove original live Unity metadata/GC lifetime, full fields14/15, class/VM epoch, native V2 or runtime acceptance.

[**Native ancillary R02 CI 43429814377**](https://github.com/night-outlook/il2cpp_plus/actions/runs/43429814377) remains failed from pre-existing historical R02 source-byte pins of files not changed here; do not claim full native CI green. The subsequent documentation-only commit must have an independently verified exact-HEAD source gate.
