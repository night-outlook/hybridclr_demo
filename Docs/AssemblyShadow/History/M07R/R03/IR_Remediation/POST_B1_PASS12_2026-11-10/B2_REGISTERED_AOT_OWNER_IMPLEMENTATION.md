# R03 B2 — registered physical AOT image ownership for unobserved generic arguments

## Final source correction — valid AOT assembly with zero TypeDefs (2026-11-11 UTC)

**Latest reviewed native commit: `night-outlook/il2cpp_plus@8627a93f4f307c8d2c99e7edada54573a93cc312`.** The preceding `f08cb329...` source has been superseded **only** for current B2 candidate selection; its original tests and commits remain in history.

**Finding / correction:** The original physical assembly registry (`s_Assemblies`) can contain a valid registered AOT assembly with `image->typeCount==0`. Such an assembly cannot own a metadata TypeDef; rejecting it would unnecessarily invalidate unrelated valid class diagnostics in fine-grained module projects. `AssemblyShadowRegisteredAotImageScan::Scan` now **skips** these empty AOT images after checking assembly token/image backreference and interpreter status. It continues to fail closed on invalid registered assembly source, over-capacity nonempty inventory, missing or ambiguous TypeDef owner, first-error publication and observed-class/registry changes. The actual unmodified source and R02 output schema remain intact.

The native source-exact mock now includes a dedicated **`RegisteredEmptyAotAssembly` positive case** and strict 42-case CI threshold, plus the prior 41 source scenarios. [Native final CI 42988174617](https://github.com/night-outlook/il2cpp_plus/actions/runs/42988174617) **4/4 PASS**, macOS/Ubuntu C++11/17 × Release/Debug × strict/ASan-UBSan: **16 host executions, 672 case executions, 7,776 assertions**, with no reported sanitizer errors. [Final 23-native/3-demo exact-source audit 42988434479](https://github.com/night-outlook/hybridclr_demo/actions/runs/42988434479) **2/2 PASS** with the unchanged four-fork historical pins, updated native scanner/mock/workflow source blobs, 16 fail-closed source-admission tests per OS and explicit `PassedInactiveSourceOnly_NotFullV2` receipt. Neither run compiled the real `Assembly.cpp` in Unity/IL2CPP or executed a Player.

**Disposition unchanged:** no full canonical execution TypeKey grammar, real V1 field15 parity, terminal-safe metadata snapshot, full field14/15 V2 transport or whole-VM epoch. `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false`. Original oneuse-12 B1 real-Player 19/19 focused PASS remains immutable; `WEB_TO_LOCAL` remains **CLOSED / NO EXECUTION**.

---

Date: 2026-11-11 UTC. Owner: **Primary Implementation**. Source branch: `codex/assembly-shadow-r01b-h1`.

**Outcome:** the previously inactive, bounded VM execution source can now construct a canonical concrete TypeDef argument key even when its owning physical AOT image has **no observed class**, provided the image comes from the original registered physical assembly table. This is a limited **healthy-time / initial-session source subset**, not a complete V1 execution snapshot, V2 field15, coherent VM epoch or runtime acceptance.

## 1. Exact native source and design decision

| Repository | Reviewed SHA |
| --- | --- |
| `night-outlook/il2cpp_plus` | `f08cb329fb19eaa47eaa8075e62dbc3f2d42cf8a` |
| `night-outlook/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/hybridclr_demo` | Latest branch HEAD, remote-verified at final publication; [source tuple and exact Git blobs](../../../../../../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) exclude a self-referential demo commit. |

This source increment touches `libil2cpp/vm/Assembly.h` and `Assembly.cpp`, adds `AssemblyShadowRegisteredAotImageScan.h`, and extends `AssemblyShadowObservedPhysicalImages.h`, `AssemblyShadowBoundedDefinitionExecutionLive.h` and the inactive `AssemblyShadowBoundedDefinitionExecutionLiveSource.inl`. The source-exact mock and native CI are updated. **The original `AssemblyShadow::GetDiagnosticsJson/GetExecutionDiagnosticsJson`, first-error B1 producer, `AssemblyShadowTypeKey.cpp` grammar, V1 serializer and frozen R02 serializer were not modified.**

The earlier physically matched class enumerator is **not** an all-metadata owner list: pinned `MemoryInformation::ReportIL2CppClasses` visits initialized, visible classes and specific runtime caches. The original `Assembly::GetAllAssemblies` is a logical/visibility snapshot, likewise unsuitable for proving ownership of an unobserved AOT image. The physical `Assembly.cpp` registry instead holds raw `s_Assemblies` under the existing `s_assemblyLock`. Its existing `GetAllPhysicalAssemblies`, `GetLoadedAssemblyPhysical` and `TryCaptureBoundedPhysicalAssemblies` already use that registry and the assembly token/interpreter-image selection policy. Primary added a **callback-only source** over this original table, not a new loaded-assembly table or managed reflection path.

## 2. New source behavior and custody

1. The existing inactive capture admits the original **initial-session** `MetadataLifetimeGate::Reader`, copies the execution registry/witnesses with `ExecutionObservationLock`, and enters `g_MetadataLock`.
2. The new `Assembly::TryVisitRegisteredAotImages` takes `s_assemblyLock` and synchronously walks **raw** `s_Assemblies`, not `GetAllAssemblies`. The pure `AssemblyShadowRegisteredAotImageScan::Scan` applies the original nonzero token policy, rejects malformed image-to-assembly backreferences, excludes interpreter images through the existing HybridCLR predicate and never materializes a heap vector or retains an assembly pointer. An AOT image may be admitted even if **zero of its classes** were physically enumerated.
3. The pre-existing two physical class-enumerator passes still prove actual source-class/registration witness matching. The source checks that each matched source-class image is in the new registered AOT inventory. It permits at most **64 matched-class images** and **1,024 distinct registered AOT images**; total metadata ownership comparisons remain bounded to **65,536**, and each inspected image to **8,192 TypeDefs**.
4. For a supported `GENERICINST`, each concrete `CLASS/VALUETYPE` argument TypeDef handle is compared against **only** admitted registered physical AOT image TypeDef handles before dereference. The resulting original-format canonical key uses that actual owner's assembly name. `usedUnobservedAotArgumentImage` differentiates a registered but unobserved argument image from an observed one; it is a source provenance marker, **not** a full-source completion marker. Unsupported/ambiguous/unregistered/interpreter owners fail closed.
5. After the physical class passes and **before releasing `g_MetadataLock`**, the source revisits the raw registered AOT table under `s_assemblyLock`, comparing bounded distinct ordered image identities. If different, it invalidates the output. The inventory scrubs borrowed image pointers while the metadata lock remains held. The original R02, observed-class registry and first-error fences are still checked; the record is frozen only for the admitted subset.

**Contract limits:** Two raw assembly registry visits and two class enumerations are not one atomic VM point; equal sets do not prove ABA immunity, cctor/static-field consistency, absence of concurrent assembly mutation between visits, or complete class/GC ownership. This source is still **not terminal-safe**. Original registered assemblies can include token-invalid and interpreter entries, which are excluded. Missing/unregistered physical images, constructed generic argument graphs, arrays, pointers, qualifiers, open generic variables and non-ASCII assembly folding are not admitted. The 1,024-image and 65,536-lookup bounds can conservatively reject otherwise valid large applications. There is no new Player caller.

## 3. Evidence and red-to-green

| Gate | Exact run and scope | Result |
| --- | --- | --- |
| [Final native source-exact mock CI](https://github.com/night-outlook/il2cpp_plus/actions/runs/42986790417) | `il2cpp_plus@f08cb329...`, macOS 15 + Ubuntu 24.04 × C++11 + C++17; each job builds Release/Debug × strict/ASan-UBSan; **16 actual host binaries**, **41 scenarios per binary** | **4/4 PASS, 656 scenario executions, 7,408 assertions, 0 reported sanitizer errors** |
| [Final exact four-repo source gate](https://github.com/night-outlook/hybridclr_demo/actions/runs/42987239404) | macOS + Ubuntu; **23 native file blobs / 3 demo pure header blobs**, original generic ABI and TypeKey grammar, physical registry implementation, pure scanner, original iterator/lock sources, all fork branch HEAD pins, explicit false product flags and closed WEB_TO_LOCAL | **2/2 PASS**, 15 negative/admission test functions per OS, result `PassedInactiveSourceOnly_NotFullV2` |

The positive source-mock cases now include **a registered support AOT image with no observed class**, but whose concrete TypeDef is used by an observed `GENERICINST`. A byte assertion compares the canonical key with the original grammar using the correct `support` assembly prefix, while the receipt separately reports one observed image and two registered AOT images. Negative cases reject a support image absent from `s_Assemblies`, invalid assembly/image backreference, mutation of the registered image set between visits, more than 1,024 registered images, missing/ambiguous/interpreter owners, second-pass class loss, the original B1 first-error race, metadata index mutations, unsupported generic shapes and the previous budget/epoch cases.

**Preserved intermediate RED:** [Initial native CI 42986475295](https://github.com/night-outlook/il2cpp_plus/actions/runs/42986475295) failed C++11/17 at a local `AotRegistrySink` initialization after adding an error field. Primary corrected the C++11 initialization and reran the **changed exact source**, which passed at 42986790417. Previous green evidence from `il2cpp_plus@cfb33d...` is not used to certify this candidate.

Neither test compiles the entire **real** `Assembly.cpp`/Unity-provided IL2CPP translation units, links GameAssembly, executes a Unity Player, validates Runtime teardown or proves first-recovery native V2 file transport. The real native `.inl` and pure scanner are compiled in a synthetic/mock VM environment. These distinctions remain in machine receipts.

## 4. Independent Primary review and residual findings

**Accepted within source-only scope:** the raw physical-assembly visitor uses existing assembly lock and token/filter semantics; the bounded source separates original class membership from generic-argument image origin; it rejects missing/ambiguous registered owners before reading TypeDef metadata, enforces capacities, retains only owned class-row/TypeKey bytes outside the metadata lock, and makes a second observational registry comparison. Existing active getters and B1 behavior are untouched.

**Open, blocking full B2:** original V1 full `finalExecutionDiagnostics` equality for arbitrary real observed classes, genuine official Unity native compilation/linked object custody, complete TypeKey grammar (non-AOT, nested constructed generics, arrays/qualifiers/open variables/non-ASCII folding), source lifetime during GC/Runtime shutdown and first-terminal capture, complete full `finalDiagnostics` (field14), native descriptor-relative V2 writer/envelope/independent receipt, and R03's original S and whole-VM epoch/GC/RSS/RC/P/E requirements. The original independent R03 full-stage **FAIL** and High `IR-R03-01/IR-R03-02` remain open.

**Next Primary-owned stage:** full original V1 *execution class row semantics* and canonical source coverage/byte parity under approved metadata lifetime, then terminal-safe general and execution V2 fields; do not install a reduced schema as full V2 without a distinct version and review. A real Unity SDK/Player build remains a later, fresh, one-use **Local Validation** candidate only once these source gates are complete.

**Authority:** `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven`. PureInterpreter disabled, no H2/M08A/X02/SNAP-01 and no self-approved Human Review Gate. **`WEB_TO_LOCAL.md` stays CLOSED / NO EXECUTION.** Oneuse-12 B1 19/19 focused real-Player PASS and its immutable evidence are unchanged.
