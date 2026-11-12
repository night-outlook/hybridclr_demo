# R03 B2 — bounded existing primitive-default TypeKeys, source review

Date: 2026-11-12 UTC. Owner: Primary Implementation. Stage: **inactive native class-source implementation, source/host evidence only; NOT full V2 or real Unity Player acceptance.**

## 1. Provenance and scope

| Canonical GitHub repository | Branch | Reviewed source revision |
| --- | --- | --- |
| night-outlook/il2cpp_plus | codex/assembly-shadow-r01b-h1 | f6530b221f0ef98ff38436ca8cd2692304d63265 |
| night-outlook/hybridclr | same | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | same | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/hybridclr_demo | same | Read latest pushed branch HEAD at use time |

The exact machine source manifest is Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json, now **41 native source/ABI/test/CI Git blobs and four demo pure source mirrors**. Legacy B1 oneuse-12 was already executed at demo 2d690bb2f7234ddcbee339f9da7125d687f5ed45 and native 8aa8d09319a89b55b2496bcc2c69ccc69cb57be9: focused 19/19 real macOS Unity/IL2CPP Player PASS, immutable and consumed, not a new B2 result.

The previous canonical composite TypeKeys and original Unicode assembly-fold source remain unchanged. Original V1 GetExecutionDiagnosticsJson, B1 first-error producer, original AssemblyShadowTypeKey::FormatMetadataOnly, R02 source/formatter and all runtime operation entry points remain unmodified.

## 2. Original primitive source semantics and bounded design

The actual original Class.cpp implementation of Class::FromIl2CppTypeEnum(Il2CppTypeEnum) uses a switch over IL2CPP_TYPE codes returning the existing preinitialized il2cpp_defaults class pointers. The direct primitive default branch does not allocate a class, populate a metadata cache, call Class::Init, create a generic class, allocate arrays or resolve a fresh constructed type. This is **source-limited** knowledge: the full official Unity Class.cpp translation unit has not been compiled by these host tests. The original AssemblyShadowTypeKey.cpp::FormatType default branch obtains that class, then calls AssemblyShadowTypeKey::Make(primitive), whose canonical name uses the existing class declaration, assembly Unicode folding and generic arity.

New **inactive only** AssemblyShadowBoundedDefinitionExecutionLiveSource.inl default case:
1. Invokes the original Class::FromIl2CppTypeEnum(value->type) exclusively during healthy-time initial metadata Reader and g_MetadataLock scope, with original before/after registry, R02 and B1 source checks.
2. Refuses null class, null image/assembly, null physical TypeDef handle, rank/constructed generic, nonnull class genericContainerHandle or declaringType. A type without an existing initialized default class is rejected; no fallback class creation or guessed system type names.
3. Resolves the class's opaque TypeDef handle against the original unfiltered registered physical AOT assembly table via the already authenticated AOT owner scanner before any metadata TypeDef dereference. The resolved image must be exactly the original default class image; missing/ambiguous/unregistered/staged/type-owner mismatch fails closed.
4. Uses the already implemented bounded canonical physical TypeDef formatter and original Unicode folding only for a successfully proven owner. Requires metadata generic arity zero and compares original class namespace/name against the physically resolved metadata declaration, and rejects any mismatched class/metadata ancestry. This establishes canonical **definition-key spelling for the admitted subset** without inferring full V1 field15 parity.
5. The existing recursive GENERICINST/PTR/SZARRAY/ARRAY and qualifier composer can consume the admitted primitive's owned key; no VM pointers survive into owned rows/frozen record. It records positive-only usedExistingPrimitiveDefault and admittedPrimitiveArguments, cleared on every later source/record rejection.

This is *strictly narrower* than the entire original primitive fallback. Some real preinitialized default classes may not carry a physical AOT definition handle or pass the new registered assembly index; they will be **rejected**, not misrepresented as supported. All original VAR/MVAR remain rejected by the original metadata-images path and the new bounded source. No general primitive or arbitrary execution-class completeness is claimed.

The source's existing limits remain: 1024 registered AOT images, 64 matched observed source images, 8192 TypeDefs per image, 65536 aggregate metadata-owner lookups, 16 generic arguments per node, eight composite levels, max 4096 bytes per owned TypeKey, 1024 rows/256 KiB owned row text. Rejection scrubs source, all primitive/Unicode/composite flags and the frozen record.

## 3. Implemented files

Native:
- libil2cpp/vm/AssemblyShadow.cpp — include original vm/Class.h only for inactive diagnostic source.
- libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl — original direct default lookup, registered physical TypeDef owner proof and class-declaration parity; no change to existing V1 getters.
- libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLive.h — two primitive-only receipt fields and irrevocable fail-close scrubbing.
- NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp — exact real inactive .inl compiled using a **fake** VM metadata/Class::FromIl2CppTypeEnum lookup. Positive preexisting Int32-style default in an unobserved registered AOT image, qualified primitive and negative missing/unregistered, wrong handle/image, ambiguous owner, unrecognized type code, nonzero generic arity, class name/declaringType and class genericContainerHandle. The duplicate-owner mock fixture was corrected without weakening the separate explicit ambiguity rejection.
- .github/workflows/r03-native-b2-definition-live-source-host.yml — exact Class.cpp/Class.h source checks, both OS/C++11/C++17 Release/Debug strict/ASan-UBSan host matrix and 67-case/1186-assertion minimum, no Unity.
- NativeHostTests/README.md — source, limits and warnings.

Demo:
- Tools/AssemblyShadow/R03IR/b2_definition_source_gate.py structurally inspects the original pinned Class.cpp default switch body to reject cache construction/Class::Init/array-instantiation paths and original Class.h; also verifies exact source sites, mock positives/negatives and false product flags.
- Tools/AssemblyShadow/R03IR/test_b2_definition_source_gate.py adds adversarial manifest admission tests, forbidden product-acceptance promotions and exact source roster checks.
- Exact candidate manifest includes original libil2cpp/il2cpp-class-internals.h metadata ABI and native Class.cpp/Class.h; 41 native blobs in total.
- .github/workflows/r03-ir-b2-definition-four-pin-source.yml binds four remote branch heads and source files through a zero-run-time negative gate.

## 4. Source and test evidence

| Evidence | Final run and observed outcome | Correct scope |
| --- | --- | --- |
| Actual .inl synthetic VM host | [43139433481](https://github.com/night-outlook/il2cpp_plus/actions/runs/43139433481): **4/4 completed/success** at native f6530b...; 16 host processes (Mac/Linux × C++11/17 × Release/Debug × strict/sanitized), 67 typed scenarios and **1195 assertions per process**; ASan/UBSan enabled in sanitized profiles | Actual inactive .inl with fake Class/metadata. **Not** Unity native ABI or actual il2cpp_defaults pointer safety |
| Exact four-fork structural source audit | [43139844512](https://github.com/night-outlook/hybridclr_demo/actions/runs/43139844512): **2/2 completed/success** Ubuntu/macOS, 21 Python negative tests per OS, **41 native source/ABI + four demo source** Git blobs, branch HEADs and false acceptance statuses | Source identity, structural Class.cpp lookup, negative admission. **Not** full Class.cpp compile, real Player or field15 parity |
| Historical previous Unicode and composite host suites | Prior verified run receipts in B2_ORIGINAL_UNICODE_ASSEMBLY_FOLD_IMPLEMENTATION_AND_REVIEW.md and B2_COMPOSITE_TYPEKEY_IMPLEMENTATION_AND_REVIEW.md; original source snapshots unchanged except additive B2 | Preserve their exact original scope and RED/fix attempts |

A first source-mock candidate was RED from ambiguous ownership in a synthetic fixture, then from incorrect mock assertions about qualified type flags and generic base TypeKey. Primary repaired the fixture and assertions, retaining the separate deliberately ambiguous source test. One further negative proves that a default class with nonnull genericContainerHandle must not be formatted as a nongeneric class. Historical REDs remain in GitHub CI history and are not product evidence. The final native 67-case matrix is GREEN on both OS and standards. Do not infer runtime success from this.

## 5. Independent review findings and unresolved decisions

- **B2-PRIM-01 — noncreating default lookup:** the pinned original Class.cpp direct primitive switch returns existing il2cpp_defaults pointers; the exact switch fragment has no Class::Init, metadata allocation, cache or pointer/array class constructors. The test-only fake Class implements a representative return. **Passed source structural check only; official Unity compilation NotRun.**
- **B2-PRIM-02 — class vs TypeDef identity:** returned default must pass registered physical AOT TypeDef owner discovery, resolved image equality, nonnested/nonconstructed/nongeneric class shape, metadata declaration name/namespace and zero arity. Mock negative cases fail closed. **Passed fake-VM source contract; real initialized corelib defaults NotProven.**
- **B2-PRIM-03 — class/metadata lifetime:** original metadata lock and first-session Reader fence the synchronous source callback, but even an unchanged inventory revision and R02 snapshot do not freeze cctor/static fields or prove postterminal class/GC metadata lifetime. **Primary-owned blocker.**
- **B2-PRIM-04 — original field15 byte semantics:** the formatter retains the original physical TypeKey spelling for this restricted subset, but no complete real original V1 nonempty execution JSON parity, unknown class shapes or full collector/serialization coverage has been measured. **Primary-owned blocker; nativeV2 field15 still false.**
- **B2-PRIM-05 — native V2 transport:** canonical fields14 and15 are original *full* finalDiagnostics and finalExecutionDiagnostics, not summaries/partial rows. Complete terminal-safe snapshots, one-writer descriptor transaction, external receipt authentication and initial-session source custody are not implemented. **Primary-owned blocker; no executable Local batch.**
- **B2-PRIM-06 — native host isolation:** all fake Class/metadata code remains under NativeHostTests, with no fake headers or test global new/delete linked to production GameAssembly. The original Class.cpp/ABI source is pinned rather than transplanted. **Source-scope only, future Unity link audit required.**

## 6. Next Primary implementation and single-batch Local design

The earliest remaining Primary work is source-accurate **original full execution field15 class-row byte/semantic parity** across healthy, nonempty, generic, primitive and Unicode case families with a valid source/metadata lifetime model. If some original full type shapes cannot be captured under a no-allocation terminal contract, retain field15 blocked; do not silently substitute partial source. Then complete full general field14 terminal source, native V2 binary/envelope/receipt writer, independent readback and adversarial host CI; B3 coherent whole-VM epoch stays separate unless proven.

Only after those Primary gates pass may a fresh **one-use Local Validation** batch start. One real Unity2022.3.62f2 macOS ARM64 IL2CPP Release source-installed build and three independent Players should simultaneously measure: exact four clean Git SHA pins and manifests, source/SDK/Bee/bridge/link symbols and allocator exclusion, Empty/initializer19/guard15 controls, physical primitive and Unicode canonical TypeKeys against original V1, complete terminal field14/15/V2 first receipt, typed negative owner/lifetime/GC/race/duplicate/symlink failures, and independent raw/product custody, GC/RSS/first-call costs. The previous oneuse-12 remains consumed and may never be replayed. Keep one verified source tuple and separate raw host/product roots; Local makes bounded fixes only and returns nontrivial issues through RETURN_TO_WEB.md.

**Current product flags:** readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; handoffAuthority=CLOSED_NO_LOCAL_EXECUTION. PureInterpreter disabled; independent R03 full-stage FAIL and High IR-R03-01/02 remain open. No H2/M08A/X02/SNAP-01 or Human Review Gate self-approval.
