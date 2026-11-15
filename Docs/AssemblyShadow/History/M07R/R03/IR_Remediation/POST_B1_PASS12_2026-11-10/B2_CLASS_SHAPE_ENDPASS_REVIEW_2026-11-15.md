# R03 B2 — final-pass restricted class-shape admission fence

**Date:** 2026-11-15 UTC. **Scope:** Primary Implementation of inactive R03 B2, not Local Validation, acceptance, H2/M08A/X02/SNAP-01, or Human Review Gate. **Branch:** `codex/assembly-shadow-r01b-h1` on all four forks.

**Native source commit:** `night-outlook/il2cpp_plus@0d97e9d1f37863dd89323d3dc8a9aa19bd94d78f`. Changed exactly:
- `libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl`
- `NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp`

## Source-derived defect

During B2's second physically matched class pass, the restricted source admits only `klass->rank == 0`. For the original token-valid *plain interpreter* TypeDef subset, it additionally requires null `klass->genericContainerHandle` and `klass->declaringType`, and rejects constructed generic or other unsupported interpreter shapes. The third class pass previously compared packed root tag/data/pointers plus cctor/static facts and the owned `logicalAssembly` name, **but not those admission-only class-shape fields**. A late change could leave an owned row while the class no longer met the exact subset originally admitted.

This is a source-observation correctness gap only. It is not evidence that a real Unity runtime mutates such fields, nor does it confer a coherent metadata/class/GC lifetime epoch.

## Focused implementation

After `ClassFacts::SameRoot` and `SameClassState` succeed inside the existing third `il2cpp_class_for_each` callback, the code checks:

1. Every admitted class still has `rank == 0`.
2. For the *current original physical interpreter image* only, `genericContainerHandle == nullptr` and `declaringType == nullptr`.

Any violated predicate produces `ObservedClassRootChanged`, which takes the existing fail-closed `Reject` path and revokes all owned rows, positive source receipts and frozen bytes. No fourth class enumeration, heap allocation, new native snapshot, TypeDef record, or additional stack scratch. AOT class shapes are **not** subjected to the interpreter-only null restriction. The original enabled V1 getter, B1, R02 and active resolver were not modified.

This check covers only post-admission shape changes witnessed during the final pass. It cannot prove earlier unobserved mutations, ABA, generic-instance internals, class/GC metadata provenance, whole-VM epoch or post-sampling stability.

## Host regression and independent static review

The checked-in **actual inactive .inl** is compiled against a synthetic VM. Three new negative modes change only one field just before the third callback: `RootRankChangedAtEnd`, `InterpreterDeclaringChangedAtEnd`, `InterpreterContainerChangedAtEnd`. Each requires `ObservedClassRootChanged` with full source/receipt revocation. One positive synthetic `AotExistingClassShape` retains nonnull AOT declaring/container fields and must remain admitted, proving the fix does not extend the interpreter-only restriction to AOT.

[**Native CI 43701442617**](https://github.com/night-outlook/il2cpp_plus/actions/runs/43701442617) **4/4 PASS** (macOS-15, Ubuntu-24.04 × C++11/C++17), 146 cases and 7,178 assertions per Release/Debug strict/sanitized source-mock execution. This is not a real Unity C++ translation unit, GameAssembly or Player.

**Source gate:** `hybridclr_demo/Tools/AssemblyShadow/R03IR/b2_definition_source_gate.py` explicitly requires the new third-pass guards, test modes, and source/host-only capability flags. `test_b2_definition_source_gate.py` includes scope/negative manifest mutations. The four-repository exact native+demo blob roster remains 64 native/eight demo and must pass at the final exact demo SHA.

## Remaining blockers

- Combined maximum 128 distinct used TypeDef handles; 64-byte exact TypeDef name fields; real-game census not obtained.
- Class/GC/metadata lifetime, unchanged generic-instance internals, stable physical assembly provenance and true whole-VM epoch remain **NotProven**.
- Complete original execution/general V1 final field15/14, terminal-safe immutable source, descriptor-relative authenticated native V2 artifact/envelope, externally authenticated receipt and first recovery remain incomplete.
- Official Unity 2022.3 native translation unit, GameAssembly and Player, worker-thread stack/RSS, metadata-lock latency and GC profile not run for these commits.
- The ancillary historical R02 source-verify workflow may still reject old source-byte pins; its outcome must be recorded separately from targeted B2 PASS.

**State:** `readyForNativeV2FieldCapture=false`; `nativeV2TransportImplemented=false`; `runtimeAcceptance=false`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; `wholeVmEpoch=NotProven`; PureInterpreter disabled; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`. No one-use Local batch or milestone transition is authorized.
