# R03 B2 — restricted same-image GENERICINST TypeKey source increment

**Date:** 2026-11-11 UTC. **Primary Implementation scope:** B2 nonterminal **inactive** physical source increment only. **No Unity Editor, actual IL2CPP GameAssembly, real Player or Native V2 file transport was built or executed.** The original oneuse-12 B1 19/19 focused Player PASS remains historical and unmodified.

## 1. Exact commits, design and changed files

| Repository | Source pin |
| --- | --- |
| `night-outlook/il2cpp_plus` | `20a57e58098e3476dad5459f04f9fc730c3848c1` |
| `night-outlook/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/hybridclr_demo` | Current feature-branch HEAD; exact source file roster and native pin in [`b2_definition_native_candidate.json`](../../../../../../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json). The demo SHA is verified at final handoff, never self-referenced inside its own manifest. |

The native change from pre-increment `il2cpp_plus@4c900ab22735768f517d81daccfed31a3d9aeb1e` is limited to: `libil2cpp/vm/AssemblyShadowOwnedConstructedTypeKey.h` (new), `AssemblyShadowOwnedExecutionRows.h` (typed source acceptance), `AssemblyShadowBoundedDefinitionExecutionLiveSource.inl` (restricted physical GENERICINST adapter), `NativeHostTests/AssemblyShadowOwnedConstructedTypeKeyHost.cpp` and `AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp`, the two matching CI workflows and `NativeHostTests/README.md`. No old `GetExecutionDiagnosticsJson`, `GetDiagnosticsJson`, B1 first-error producer, PureInterpreter logic, managed icall, transaction owner or historical evidence was modified.

The authoritative original canonical grammar is in **unchanged** `il2cpp_plus/libil2cpp/vm/AssemblyShadowTypeKey.cpp` blob `6b23b4bad66e9a8f36c68717ef82626351018624`:

`generic(` + canonical concrete generic **definition** key + each `,` + UTF-8 byte-length-prefixed canonical concrete argument key + `)`.

The original type ABI comes from pinned `libil2cpp/il2cpp-runtime-metadata.h` blob `f7f235848209ee331adfd1c2b214b46cc753392e` (actual `Il2CppGenericClass`, `Il2CppGenericInst`, `Il2CppGenericContext`, and `Il2CppType`). Both source blobs are now explicit admission inputs, not inferred from the mock.

### Chosen source policy (conservative by design)

The inactive `AssemblyShadow::TryCaptureBoundedDefinitionExecutionLive` continues to require the original **initial-session** metadata Reader, an observed registration witness, a physical first-match callback under `g_MetadataLock`, same-image verified AOT metadata TypeDef ownership, and a bounded source-fence/revision check. It now admits `IL2CPP_TYPE_GENERICINST` only if the observed class and type share exactly the verified physical generic class, the class-instantiation is present and has no method-instantiation context, the unqualified base definition belongs to the observed physical AOT image, and **each** unqualified concrete `CLASS/VALUETYPE` argument is independently verified against that same image. The concrete argument count must equal the verified leaf definition's arity, and be between **1 and 16**.

The new `r03_b2_owned_constructed_type_key::Capture` has a fixed **4,096-byte** owned output, one-way Fresh/Arguments/Complete/Failed state, no heap or persistent borrowed source. `Rows::Add` statically accepts only this canonical constructed-key capture or the original canonical metadata-definition capture. Invalid count, unsealed key, unsupported shape or overflow invalidates the entire key/row, never truncates or substitutes a display name. The existing original native frozen execution/R02 record is used unchanged downstream.

**Excluded from this bounded scope:** a generic TypeDef or argument in another physical image, generic arguments that are themselves instantiated generics, arrays, pointers, open `VAR/MVAR`, qualifiers, non-ASCII physical assembly-name folding, any state after native B1 terminal publication, metadata epochs other than the initial session, global VM class/GC epoch, and complete general or execution V2 field14/15. A nested **definition** ancestry and generic-definition arity are supported; nested **constructed** type graphs are not.

## 2. Tests and independent source review

| Evidence | Scope | Result |
| --- | --- | --- |
| [Pure constructed-key host CI 42978349307](https://github.com/night-outlook/il2cpp_plus/actions/runs/42978349307) | Mac/Linux × C++11/17, strict+ASan/UBSan, **8 real host executions**; fixed byte grammar, two concrete arguments, invalid count, missing/unsealed key, duplicate/reuse, capacity, output revocation and immutable row copying | **4/4 jobs PASS**, **78 assertions/process, 624 in total**, zero protected allocations |
| [Native physical-source mock CI 42979860514](https://github.com/night-outlook/il2cpp_plus/actions/runs/42979860514) | Exact new `.inl` compiled with a **mock** `Il2CppClass` and metadata ABI, Mac/Linux × C++11/17 × Release/`IL2CPP_DEBUG` × strict/ASan-UBSan, **16 host processes**; 31 typed cases | **4/4 jobs PASS**, **31 scenarios/process (496 total), 243 assertions/process (3,888 total)**, no reported sanitizer errors |
| [Exact source admission 42980498037](https://github.com/night-outlook/hybridclr_demo/actions/runs/42980498037) | Mac/Linux, 15 native blob IDs, three demo pure-source counterparts, real `Il2CppGenericClass` ABI, original `AssemblyShadowTypeKey.cpp` grammar, four branch HEAD pins, false acceptance flags and explicit CLOSED handoff | **2/2 jobs PASS**, `PassedInactiveSourceOnly_NotFullV2` |

Native positive cases include simple and nested physical TypeDefs, generic-definition arity, two observed classes in reversed physical callback order, a same-image two-argument `GENERICINST`, and nested TypeDef arguments. Negative cases include missing/foreign argument owners, wrong/over-limit arity, qualified/constructed generic arguments, absent class or method contexts, wrong generic base, staged metadata indices, malformed/cyclic ancestry, invalid physical source, and B1 first-error publication during capture. All negative tests require invalidation of the record and owned rows.

**Source-review finding closed in this increment:** a generic key may be structurally valid without being a physical execution TypeKey. The adapter therefore does not accept caller-supplied generic text; it authenticates each underlying TypeDef through the real image's handle enumeration before dereference, then feeds only completed immutable typed captures into `Rows`. The unchanged legacy type formatter is pinned to guard against accidental grammar changes. This is a **conservative subset source policy**, not an independent guarantee of arbitrary metadata origin, class pointer lifetime, or all-VM snapshot coherence.

**Additional open risks:** Mock generic-class objects match a pinned source layout but are not a real IL2CPP compiler or runtime proof. The actual `klass->typeMetadataHandle` / `generic->type->data.typeHandle` relationship for constructed Player classes, allocator behavior of the physical enumerator, snapshot ordering versus concurrent cctor/storage changes, complete source enumeration of all relevant images, and real V1 byte-for-byte parity for nonempty generic classes remain **NotRun/NotProven**. The 16-argument/4-KiB caps deliberately reject some valid application shapes. No independent real source-to-Player/GC/shutdown coverage exists.

## 3. Rollback, remaining Primary work, and Local gate

Rollback this increment by reverting only the native files and the demo pure-source/CI/manifest updates introduced after pre-increment native `4c900ab...`. Do not re-open or modify the consumed oneuse-12 local roots, original S, existing B1 source receipt or previous R03 review findings. The original class/first-error functions were not changed.

Next Primary-owned source work: canonical cross-image generic definition/argument ownership and complete composite TypeKey grammar (arrays, modifiers, qualifiers, Unicode folds and variable-shape policy), followed by real original V1 execution-field parity, terminal-safe full `finalDiagnostics`/field14 source, complete `finalExecutionDiagnostics`/field15 source, authenticated bounded V2 file transaction and independent receipt. B3 whole-VM epoch and other R03 acceptance gaps remain outside this increment.

**No new Local Validation execution authority.** `WEB_TO_LOCAL.md` must remain **CLOSED / NO EXECUTION**. `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; wholeVmEpoch=NotProven; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false`. PureInterpreter stays disabled; no H2/M08A/X02/SNAP-01 and no self-approved Human Review Gate.
