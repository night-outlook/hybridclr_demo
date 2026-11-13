# R03 B2 — Original V1 root first-owner end-pass recheck

**Stage:** Primary Implementation, inactive R03 B2 source/host only. **Date:** 2026-11-13 UTC. **Working branch:** codex/assembly-shadow-r01b-h1 in all four repos. **Native source:** night-outlook/il2cpp_plus@2ded6fa7deac7a52890aee917516fe9cdb42b128; **demo source gate anchor:** hybridclr_demo@2fff0e1c76ac4150889aa138036c11400fd7cb88; read the final pushed demo HEAD after this report. Unchanged native/package forks: hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55 and hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de. Original enabled V1 getter remains its byte-pinned 5,222-byte source, native B1 unchanged.

## Source diagnosis

The actual enabled V1 execution diagnostics creates MetadataTypeImages from token-valid PHYSICAL CopyValidAssemblies order (interpreter images included) with an unordered_map::emplace first-owner rule. The inactive B2 bounded field15 source already checked the original first owner of each admitted TypeKey component during owner-checked key construction. It also double-sampled original physical image address, typeCount and image/assembly tokens; and checked class root pointer/tag and cctor/static facts across three physically matched iterator callbacks.

Those checks did NOT repeat the original first-owner lookup for the class root after the owned row was copied. A metadata indexed handle could be removed from its image, or another earlier physical image could begin returning the same handle, while every class pointer, original image identity and token/count remained unchanged. In that case the previously recorded original first-owner receipt would be stale even at the final class observation.

The actual original enabled getter is not a globally coherent snapshot either. This source change detects two specific **observed** late changes, not an atomic metadata map.

## Implementation

Without adding a new physical class traversal or heap buffer, extend the existing end-of-collection third matched class pass while holding the original g_MetadataLock and the initial metadata-lifetime Reader. For each previously registered and physically matched class, first verify the unchanged packed root facts and cctor/static state. Then re-evaluate original first-emplace metadata owner for that class's root TypeDef handle using the earlier authenticated token-valid physical original-V1 image inventory and the existing pure assembly_shadow_original_v1_owner_join::CheckFirstOwner. Read metadata indexed handles only through MetadataCache::GetAssemblyTypeHandle; do NOT directly dereference unowned TypeDef handles.

A **separate bounded total** of 65,536 indexed metadata-handle lookups covers all third-pass roots; a budget excess fails closed. Missing indexed owner returns OriginalV1OwnerMissing, earlier different owner returns OriginalV1FirstOwnerConflict, budget exhaustion returns OriginalV1LookupBudget, and other unavailable owner source rejects with OriginalV1ImageSourceUnavailable. No optional silent downgrade to an empty or partial class record is allowed. The third callback records exact owner recheck count/lookup work in the scoped receipt.

The new receipt fields originalV1RootOwnerEndPassMatched, originalV1RootOwnerEndPassLookups, and originalV1RootOwnerEndPassStable are zero/false on Reject. Positive originalV1FirstEmplaceOwnerMatched now requires a complete, successful root-owner end pass and the existing second original image identity/token/count observation. Source failure continues to revoke every owned row and frozen record. No original V1 getter, runtime resolver, B1 source, assembly table or Player transport entrypoint changed.

**Performance boundary:** no extra physical iterator pass or large owned scratch, but up to 65,536 *additional* indexed metadata reads while holding the metadata lock. This is a hard fail-closed budget, not a demonstrated latency bound or throughput result in Unity.

## Raw evidence and regression chronology

[Final native source host CI 43351671250](https://github.com/night-outlook/il2cpp_plus/actions/runs/43351671250) at il2cpp_plus@2ded6fa7deac7a52890aee917516fe9cdb42b128: **4/4 PASS**, macOS-15 and Ubuntu-24.04 × C++11/C++17, with Release/Debug strict/ASan-UBSan host profiles. Each process reports **115 scenarios and 4,656 assertions**. Four new negative scenarios exercise:

1. A physically admitted AOT root handle disappears from its indexed metadata image at the third pass without changing the class root pointer.
2. An earlier interpreter physical image starts advertising the same AOT root handle after the original class row was copied, changing the first owner.
3. A plain interpreter-only root loses its indexed metadata handle at the third pass, with no registered AOT TypeDefs required.
4. An earlier class loses indexed root ownership during a later class's TypeKey construction; the complete end pass detects the stale earlier row.

All reject, scrub positive root-owner receipts and owned rows, and preserve the earlier root/ctor/static tests. The initial host CI [43351492096](https://github.com/night-outlook/il2cpp_plus/actions/runs/43351492096) failed a new test because the competing-owner fixture prepared an interpreter image but had not enabled the mutation flag. The fixture was corrected in the final native commit; production source was unchanged by that correction. Neither run used actual Unity metadata or Player.

[Four-repository code-anchor source audit 43352312987](https://github.com/night-outlook/hybridclr_demo/actions/runs/43352312987) at demo@2fff0e1c76ac4150889aa138036c11400fd7cb88 **2/2 PASS** (macOS-15, Ubuntu-24.04), verifying 64 native/eight demo independent pinned Git blobs, the exact 5,222-byte original getter, source root owner recheck tokens, receipt poison and negative coverage. The final docs SHA requires its own CI verification; do not transplant an earlier run result.

## Scoped source review and blocking findings

- **ROOT-OWNER-END-01 / host and source PASS:** the observed original physical first-owner of each admitted root is rechecked at the end of the existing third class enumeration; fixed synthetic VM mutations of the indexed owner map are detected despite stable class root pointers and image tokens.
- **ROOT-OWNER-END-02 / incomplete metadata table:** this protects **root TypeDef handles only**, not the full original V1 MetadataTypeImages table or every nested/generic argument handle used earlier in TypeKey construction. TypeDef name bytes, generic-context contents, metadata index relocation within the same owner, ABA, and changes after the final observation remain unchecked.
- **ROOT-OWNER-END-03 / lifetime and epoch not proved:** initial metadata Reader plus g_MetadataLock and three observed class passes do not establish class/GC lifetime or a coherent whole-VM source epoch; the original allocating getter is not terminal-safe. No real Unity2022 official native full TU, GameAssembly, Player, thread-stack or metadata mutation experiment has run at these SHAs.
- **ROOT-OWNER-END-04 / budget risk:** the additional 65,536-work budget can cause a capture formerly admitted by the restricted B2 source to reject on large class/image sets; that is fail-closed by design. CPU/lock hold time needs real Unity profiling before future activation.
- **ROOT-OWNER-END-05 / full field14/15 and V2 blocked:** complete original V1 class-shape and metadata contents, preterminal immutable field14/finalDiagnostics and field15/finalExecutionDiagnostics, descriptor-relative native V2 artifact/envelope, identity-bound external receipt/readback and authenticated first recovery remain unimplemented. Historical B1 oneuse-12 focused real Player 19/19 PASS is consumed and not current B2 acceptance. Original independent R03 full-stage FAIL/High findings remain.

**Next Primary-owned step:** develop a complete original execution-class shape and metadata-handle/content source admission and a defensible class/GC/metadata lifetime boundary, then full terminal-safe fields and authenticated native V2. No H2/M08A/X02/SNAP-01 or self-approved Human Review Gate.

**Flags:** readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; PureInterpreter disabled. WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION.
