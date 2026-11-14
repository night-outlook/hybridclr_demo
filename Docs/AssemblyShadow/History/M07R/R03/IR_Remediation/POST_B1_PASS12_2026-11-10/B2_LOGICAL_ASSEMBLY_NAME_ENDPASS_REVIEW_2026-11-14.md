# R03 B2 — observed logicalAssembly exact name end-pass fence

**Date:** 2026-11-14 UTC. **Stage:** Primary Implementation of INACTIVE R03 B2 only. **Branch:** `codex/assembly-shadow-r01b-h1`. **Native commit:** `night-outlook/il2cpp_plus@dce8c095b53fa28e6ed6a2b825a0c36fe3da5c5a`.

## Source-derived correctness gap

The original, frozen V1 `GetExecutionDiagnosticsJson` assigns `row.logicalAssembly = Quoted(owner->aname.name)` for each observed class. Inactive B2 copies that exact string to its owned row during the second physical class pass. Its existing third class pass checked pointer/tag and cctor/static facts but did not compare the source name *bytes*. An in-place name change at the same address, or a different string at a replacement address, could therefore escape the final observation while the owned row retained old text. This is a demonstrable source-mock consistency gap; not proof of a real Unity race.

## Focused solution and memory/performance bound

- `libil2cpp/vm/AssemblyShadowOwnedExecutionRows.h`: reuse the existing 2,048-slot occupied map as a **one-based uint16 insertion-index map**. It grows by **2,048 bytes** within the existing `sizeof(Rows)<=320KiB` bound. `Rows::SameCollectingLogicalAssembly(slot, ByteView)` uses the map for O(1) exact byte comparison, fails closed for missing slot, different bytes or wrong state, and is inaccessible after `Seal` sorts entries. Existing fail/scrub and row order invariants remain.
- `libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl`: the *existing* third physically matched class callback reads `image->assembly->aname.name` under the initial metadata Reader and `g_MetadataLock`, bounds length to 4,096 bytes and compares against the second-pass owned `logicalAssembly` for the same authenticated registry slot. Any missing, oversized or changed text fails with the existing `SourceChanged` first-error and revokes rows/receipts. No fourth class traversal or per-name heap allocation is added.
- The pure owned-row header is mirrored in hybridclr_demo under `Tools/AssemblyShadow/R03IR/NativeDiagnostics/BoundedOwnedExecutionRows.h` (only include filenames differ). The exact source gate pins the native header, mirror, native implementation, test code, and all repository source identities.

## Source-host regression

Three new checked-in scenarios in the actual inactive `.inl` synthetic VM: (1) change the name bytes at the same pointer after row collection, expect `SourceChanged`; (2) change name to different bytes at a new pointer, expect `SourceChanged`; (3) move to different pointer with *identical* bytes, expect success. Existing success/error tests continue to check complete row/receipt revocation and first error. **Native [CI 43550349351](https://github.com/night-outlook/il2cpp_plus/actions/runs/43550349351): 4/4 PASS** macOS/Ubuntu × C++11/C++17, Release/Debug strict/sanitized, **142 scenarios / 7,007 assertions per execution**. The separate pure Rows host suite is [workflow 43550349327](https://github.com/night-outlook/il2cpp_plus/actions/runs/43550349327). Four-repository source CI at the new demo SHA must be independently verified.

## Explicit limits / next Primary work

The comparison covers only the **observed execution-class logicalAssembly field**. It does not prove every physical image's name, generic argument TypeKey-owner assembly name bytes, source changes that revert between observations, assembly-object identity, class/GC/metadata lifetime, or a coherent whole-VM epoch. The 2 KiB Rows size increase may affect actual caller stack/RSS depending on storage placement; no official Unity native TU, GameAssembly, Player or lock latency/stack measurement has run at this source revision. The combined <=128 TypeDef capacity, <=64-byte TypeDef names and other B2 caps are unchanged. This is not original V1 full field14/15 parity, a terminal-safe immutable source, native descriptor-relative V2 writer/envelope/independent receipt, or authenticated first recovery.

**Acceptance unchanged:** `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven`; PureInterpreter disabled; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`. The historical B1 oneuse-12 focused real Player receipt cannot be reused as B2 evidence. Human Review Gate not approved; no H2/M08A/X02/SNAP-01.
