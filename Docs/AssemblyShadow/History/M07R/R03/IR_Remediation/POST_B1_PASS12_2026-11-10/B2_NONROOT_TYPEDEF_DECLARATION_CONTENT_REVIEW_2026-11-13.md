# R03 B2 — Bounded non-root TypeDef declaration-content consistency

**Primary Implementation; inactive source/host only.** UTC date: 2026-11-13. Branch: `codex/assembly-shadow-r01b-h1`. Native: `night-outlook/il2cpp_plus@bf9b17175b56090ad5ac05f699864b79358204a2`; demo source-audit anchor: `night-outlook/hybridclr_demo@d47afd16a7d3e58a4170630bf06b461edab190e9`. Other forks unchanged: `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`. The original enabled 5,222-byte V1 getter and B1 path remain unchanged.

## Problem and source semantics

The authentic enabled V1 builds a first-emplace TypeDef metadata owner map from token-valid **physical** assemblies, including interpreter images. The prior inactive B2 source rechecked class-root and <=128 admitted non-root TypeDef owner pairs, but **same handle and same first physical owner do not imply the same metadata contents**. TypeDef namespace/name bytes, declaring/generic-container indices, or generic arity could differ by the final metadata sample even if class/image pointers and tokens did not.

This is a bounded *observational* source consistency gap; the synthetic host mutations do not demonstrate that genuine Unity TypeDef metadata can legally change concurrently.

## Implemented source boundary

Extend the existing `NonRootOwnerAudit` pairs in `AssemblyShadowBoundedDefinitionExecutionLiveSource.inl` with **byte-exact copied** UTF-8 namespace and simple-name data (each at most 64 bytes), `declaringTypeIndex`, `genericContainerIndex`, and the generic container's observed arity. The owner must already have passed the original V1 physical first-owner check. Repeated use of the same handle must agree with the saved declaration. No borrowed `char*`, class pointer, heap buffer, or unbounded string hash is retained.

After the third physically matched class pass, second original physical image pass, and each non-root original-owner recheck, read the same authenticated TypeDef declaration again **under the initial metadata-lifetime Reader and `g_MetadataLock`**. Compare the copied bytes, indices and arity exactly. Changes return `OriginalV1TypeDefContentChanged`; names beyond the 64-byte field limit return `SourceOutsideBudget`. Such rejects revoke every owned row/frozen record and positive receipt. The new receipt fields are `originalV1NonRootTypeDefContentMatched` and `originalV1NonRootTypeDefContentEndPassStable`; both are reset on failure. The preexisting first-owner positive receipt now depends on the new scoped content recheck.

A separate discovered **first-error propagation bug** was corrected: if the second class/TypeKey pass rejects, the collector now invokes the existing rejection path *immediately*, instead of continuing into a partial end-pass audit capable of obscuring the original error. The 65-byte name fixture establishes the intended budget error survives unchanged.

Resource bounds: <=128 non-root handles, <=64 bytes for each of two names per entry, and a compile-time audit scratch cap **24,576 bytes** (previous owner-only audit cap <=2,064 bytes; at most **22,512 additional bytes** by these static bounds). No extra physical class traversal or changed enabled getter. Original metadata-owner root and non-root lookup limits each remain independently bounded (<=65,536 indexed reads for each bounded phase); genuine Unity lock duration/worker stack remains unmeasured.

## Tests and evidence

[Native source/host CI 43361925344](https://github.com/night-outlook/il2cpp_plus/actions/runs/43361925344) at exact native SHA bf9b17175b56090ad5ac05f699864b79358204a2: **4/4 PASS** on macOS-15/Ubuntu-24.04 × C++11/C++17, Release/Debug strict and ASan/UBSan test variants. Each host execution reports **126 scenarios and 5,637 assertions**, with six new negatives: mutation of simple-name bytes behind an unchanged pointer; namespace change; declaring index change; primitive TypeDef generic-container index change; generic arity change; and a 65-byte non-root name rejected for `SourceOutsideBudget` without later masking.

During development, focused CI exposed (1) a primitive-default fixture that failed to construct the generic source row and (2) first-error masking after a failed second pass. Both were corrected and the temporary diagnostics removed before the exact final host run. These are **synthetic VM** results, not real Unity native translation-unit or Player validation.

[Exact four-repository code-anchor source audit 43362278126](https://github.com/night-outlook/hybridclr_demo/actions/runs/43362278126) at demo code SHA d47afd16a7d3e58a4170630bf06b461edab190e9 checks the unchanged original getter, the 64-native/eight-demo Git blob roster, source-consistency and error-order predicates, typed receipt revocation and explicit *false* acceptance flags. Final documentation HEAD must receive an independent CI result rather than inheriting that code-anchor outcome.

## Independent Primary source findings and remaining decisions

- **DECL-01 / scoped source PASS:** Previously admitted non-root TypeDefs now have exact bounded declaration-name and structural-index/arity checks; mutable metadata names at identical addresses are detected in host tests.
- **DECL-02 / scoped first-error PASS:** a second-pass source failure exits before non-root audits can overwrite the root-cause error; oversized names fail closed without truncation.
- **DECL-03 / incomplete source OPEN:** this covers only <=128 previously admitted **non-root** handles with two <=64-byte name fields. Registered **root** TypeDef name/structural contents, more complex interpreter/generic/open VAR/MVAR shapes and the complete original V1 TypeDef table are not authenticated. AOT/metadata name buffers beyond the byte cap reject instead of pretending complete coverage.
- **DECL-04 / runtime epoch OPEN:** g_MetadataLock + Reader and repeated class/image/metadata observations do **not** provide class allocation provenance, GC lifetime, ABA exclusion, immutable VM epoch, or original getter-to-Player byte parity. Additional stack and metadata calls need official Unity 2022.3 IL2CPP compilation, Player and performance validation in a future **authorized** Local batch.
- **DECL-05 / R03 acceptance BLOCKED:** complete terminal-safe original general field14 and execution field15, native one-owner descriptor-relative V2 artifact/envelope, independent identity-bound receipt/readback and authenticated first recovery remain unimplemented. Existing independent full-stage R03 FAIL/High findings remain. Historical B1 oneuse-12 focused 19/19 Player PASS is consumed and cannot be promoted as new B2 validation.

**Next Primary:** authenticate bounded root declaration contents or establish a coherent immutable metadata/class lifetime source before attempting complete field14/15 and native V2. Do not start H2/M08A/X02/SNAP-01 or self-approve Human Review Gate.

**Flags:** `readyForNativeV2FieldCapture=false`; `nativeV2TransportImplemented=false`; `runtimeAcceptance=false`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; `wholeVmEpoch=NotProven`; PureInterpreter disabled. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`.
