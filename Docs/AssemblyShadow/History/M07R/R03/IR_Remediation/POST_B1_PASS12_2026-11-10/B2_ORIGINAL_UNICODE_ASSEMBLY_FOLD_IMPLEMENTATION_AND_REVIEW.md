# R03 B2 — original Unicode assembly folding, implementation and source review

Date: 2026-11-11 UTC. Owner: Primary Implementation. **Inactive native source only; no complete V2 or Unity runtime acceptance.**

## Exact source and intent

All four repositories use codex/assembly-shadow-r01b-h1. Reviewed native revision: night-outlook/il2cpp_plus@db5354a9befd5cfd02f907d3169c8106e0a29305; unchanged interpreter: night-outlook/hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55; unchanged Unity package: night-outlook/hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de. Read latest GitHub remote HEAD for hybridclr_demo. [Exact candidate manifest](../../../../../../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) pins **38 native source/ABI/test/CI blobs plus four independent demo source mirrors**.

The original AssemblyShadowTypeKey.cpp::CanonicalAssembly calls AssemblyShadowName::ViewName, the original NameHash, and NextFolded -> VmStringUtils::Utf16ToLower, then converts folded UTF-16 code units to UTF-8. ASCII-only normalization is insufficient for accented, Greek, Cyrillic and supplementary Unicode assembly names. A locale-dependent substitute would change original canonical TypeKey bytes.

The chosen path reuses the **original VM NextFolded** callback rather than duplicating a Unicode table.

## Implementation and verified source boundary

Native changes:
- libil2cpp/vm/AssemblyShadowOwnedDefinitionTypeKey.h: new C++11 BeginCanonicalFolded over a pre-normalized original ViewName slice and original folding callback. Checks valid UTF-16 pair/surrogate, source advancement, bounded UTF-8 conversion, postfold UTF-8 byte length prefix, one-way failure and 4096-byte key budget. No heap allocation or retained VM input.
- libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl: calls **original** ViewName, NameHash and NextFolded under the existing original g_MetadataLock, initial-session Reader and registered AOT TypeDef-handle ownership proof. Legacy V1 and native B1 remain unchanged.
- libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLive.h: positive-only usedUnicodeAssemblyFold receipt and fail-closed revocation on rejection.
- NativeHostTests/AssemblyShadowFoldedNameMock.h and updated NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp: actual inactive .inl with synthetic VM metadata and intentionally partial fake Unicode fold map; 55 source-mock scenarios/process, including Unicode positive/path/version/supplementary and invalid UTF-8 source.
- NativeHostTests/AssemblyShadowOwnedFoldedDefinitionHost.cpp: pure encoder tests including invalid callbacks, invalid surrogate pairs, aliases, reuse, capacity and guarded allocation exclusion.
- NativeHostTests/AssemblyShadowNameReferenceParityHost.cpp and ShadowNameParityShim/il2cpp-config.h: standalone host includes actual original AssemblyShadowName.h and exact original char-conversions.cpp Unicode data, plus original pinned VmStringUtils.cpp lower-table lookup logic in an isolated test-only ABI shim. Reference NameHash/NameEquals vs bounded key byte output are tested for Latin, Greek, Cyrillic and supplementary Unicode.
- New strict/sanitized Mac/Linux C++11/C++17 CI workflows for folded pure host and original source/table parity; NativeHostTests/README.md records scope.
- GitHub source gate and candidate manifest pin the original Name.h, VmStringUtils.cpp/h, StringUtils.cpp, char-conversions.cpp/h, all new test drivers and CI workflows. Demo pure type-key header is source-identical to the native header.

The original Unicode parity host deliberately does **not** compile all of VmStringUtils.cpp or AssemblyShadowTypeKey.cpp, link Unity native runtime, or prove arbitrary live metadata lifetime. Original StringUtils UTF-16 to UTF-8 and legacy TypeKey grammar are pinned as reference, but the host sample cases alone are not universal runtime equivalence.

### Evidence at source checkpoint

- Native actual .inl source mock: [CI 43011988073](https://github.com/night-outlook/il2cpp_plus/actions/runs/43011988073). Ubuntu C++11/17 jobs completed/success at the first review: 55 typed cases and 924 assertions per process, Release/Debug strict/sanitized. macOS jobs were still queued at that observation; recheck before claiming 4/4.
- Pure Unicode encoding: [CI 43011964681](https://github.com/night-outlook/il2cpp_plus/actions/runs/43011964681). Ubuntu C++11/17 completed/success; Mac queued at the first review.
- Original VM name + Unicode table host: [CI 43012431935](https://github.com/night-outlook/il2cpp_plus/actions/runs/43012431935). Ubuntu C++11/17 completed/success; Mac queued at the first review. Later workflow revision 94c7d67... added exact original TypeKey.cpp grammar check without skip; recheck latest CI and compile attribution.
- Exact 38-native/four-demo four-pin source audit: read the GitHub Actions run at final hybridclr_demo commit; its result is source-only and must not be promoted to Unity build/Player.
- Previous [bounded composite implementation review](B2_COMPOSITE_TYPEKEY_IMPLEMENTATION_AND_REVIEW.md) and B1 oneuse-12 real macOS IL2CPP Player focused 19/19 PASS remain historical and separately source-pinned; oneuse-12 is consumed and not new B2 validation.

## Independent review findings

**B2-UNICODE-01 (bounded name parity):** Original Unicode folding callback is used in actual source; the encoder computes the folded UTF-8 byte length and scrubs on malformed source. Known unicode examples are tested with original name header and Unicode table. Full original V1 nonempty class JSON byte parity and actual Unity ABI remain **NotProven**.

**B2-UNICODE-02 (source trust and lifetime):** The pure callback is caller-provided; production source is explicitly pinned to original NextFolded. Physical AOT TypeDef ownership proof and initial metadata Reader are retained. Two assemblies/class observation passes, registry/R02 fences and class cctor/static values are **not a coherent VM epoch** or postterminal proof. Remains Primary-owned.

**B2-UNICODE-03 (type-shape coverage):** Original FormatMetadataOnly rejects VAR/MVAR when an image map is supplied. Primitive/default enum types use an original Class::FromIl2CppTypeEnum path, currently not proven safe to access as a no-allocation/no-initialization bounded source. These still fail closed; do not delegate nontrivial implementation to Local or invent a surrogate TypeKey.

**B2-UNICODE-04 (V2 producer/transport):** Original V2 slot14 finalDiagnostics and slot15 finalExecutionDiagnostics mean complete native diagnostics, not a B1 first-error or subset. Terminal-safe full field source/metadata/GC lifetime, authenticated descriptor-relative native V2 artifact and externally bound receipt are not implemented. Keep readyForNativeV2FieldCapture=false and nativeV2TransportImplemented=false.

**B2-UNICODE-05 (host contamination):** Both standalone host drivers override global new/delete and must remain exclusively under NativeHostTests, outside Unity Bee/production libil2cpp. The test-only fake ABI shim must not be copied into GameAssembly. Real linked symbol and official native TU checks remain unexecuted.

## Next Primary and conditional single-batch Local scope

Primary should complete authenticated primitive field15 TypeKey sourcing (if it can avoid introducing new class/cache creation), exact original nonempty V1 byte parity, terminal-safe full general/execution fields14/15 and a correct class/GC/metadata lifetime contract. Then integrate the already host-tested bounded V2 codec and descriptor transaction with one-writer identity, independently authenticated receipt and adversarial tests. Only after independent source review and a new explicitly authorized WEB_TO_LOCAL may Local perform a single exact-four-SHA, fresh one-use batch: original-S/capacity/SDK/working-tree admission, one Unity2022.3.62f2 IL2CPP build, three separate Players (Empty, initializer19, captured generic15), V1/B1/full V2 comparisons, GC/RSS/stability and independent artifact/receipt custody. Local fixes remain limited; substantive changes return to Primary.

**Current acceptance:** readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; handoffAuthority=CLOSED_NO_LOCAL_EXECUTION. Original full R03 FAIL, High IR-R03-01/02, PureInterpreter disabled, no H2/M08A/X02/SNAP-01 or human self-approval.
