# R03 B2 — Physical versus public IL2CPP enumeration: source/lifetime design and review

**Date:** 2026-11-17 UTC. **Scope:** Primary Implementation, **source-grounded and read-only**. This checkpoint does **not** attach a native TypeDef census, alter `il2cpp_plus`, build a Unity Player, reopen Local Validation or approve a Human Review Gate. All repositories remain on `codex/assembly-shadow-r01b-h1`.

| Repository | Exact read-only source pin |
|---|---|
| `night-outlook/hybridclr_demo` | Code anchor: `09fcb539620702b25274999102d2329377ee096f` |
| `night-outlook/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `cecf4b859d50b128e5c0fc6c90cd89e3a452b96a` |

## 1. Source-confirmed discovery: two materially different populations

The existing inactive B2 source (`libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl`) calls `il2cpp_class_for_each` **three** times and `Assembly::TryVisitOriginalV1ExecutionImages` **twice** while an initial metadata-lifetime Reader and `g_MetadataLock` are held. Their inputs are **not equivalent**.

### A. Public class-reporting population

`libil2cpp/il2cpp-api.cpp::il2cpp_class_for_each` forwards to `vm::MemoryInformation::ReportIL2CppClasses`. With Assembly Shadow enabled, that function:

1. Obtains `Assembly::GetAllAssemblies()` and a visibility generation. In `Assembly.cpp`, the getter can rebuild a **logical** assembly snapshot via `CopyLogicalAssemblies`, which calls `AssemblyShadow::ResolveAssembly(physical)` and deduplicates by logical name. **Nuance:** the initial snapshot points at `s_Assemblies` until an assembly-version change; do not claim the getter always returns a freshly logical-remapped vector. Neither state gives a closed-world physical proof.
2. Calls `GlobalMetadata::GetInitializedTypeInfoFromAssembly` for each image TypeDef index. For AOT this reads the existing `s_TypeInfoDefinitionTable`; for interpreter images it consults `GetCachedTypeInfoFromTypeDefinitionRawIndex`. The method returns a class **only if the cached class is initialized**. It is a nonconstructing observer, **not** a complete list of metadata TypeDefs.
3. Wraps callbacks in `ReportVisibleClass`, which checks `AssemblyShadowVisibility::IsClassVisible` against the captured visibility generation.
4. Additionally walks four separately maintained constructed-class caches: multidimensional array, SZArray, generic classes and pointer types. The generic walker uses `s_GenericClassMutex`; the array/pointer walkers use `g_MetadataLock`. These caches represent materialized runtime classes and are not the full physical metadata definition table.

B2 matches registered execution classes **within this public callback population**. The success of three repeated class passes is not an independent proof that every physical definition, every rejected TypeKey path, or even every hidden physical class was visited. It must not be described as a universal physical-class enumeration.

### B. Original-V1 physical-definition population

`Assembly::TryVisitOriginalV1ExecutionImages` visits the raw `s_Assemblies` table using `assembly_shadow_original_v1_image_scan::Scan`, under `s_assemblyLock`. It uses the original `CopyValidAssemblies` **nonzero assembly-token** eligibility rule in physical registration order. Interpreter and zero-TypeDef images are **not** excluded. This is the correct source order for original V1 `MetadataTypeImages` *first-emplace* owner semantics. A borrowed image still needs the initial metadata Reader, `g_MetadataLock`, token and assembly-image backlink checks, and a bounded index traversal before any metadata dereference. The image inventory is **not** an enumeration of every initialized, generic or constructed `Il2CppClass`.

**Consequence:** `TypeDefSourceCoverageReplay` validates only **caller-declared** use obligations; two equal caller-planned passes can omit the same real path. The original-V1 physical registration inventory is independently enumerable in source, but source inspection alone cannot establish a coherent whole-VM/class/GC epoch or high-water capacity.

## 2. New implementation: pinned-source population boundary verifier

The following files are added only to `hybridclr_demo`:

- `Tools/AssemblyShadow/R03IR/TypeDefCensus/verify_native_enumerator_population.py`: read-only verification of **11 exact Git blobs**, commit, Git-tree membership, native code scopes and source expressions. Reports `PinnedSourcePopulationMismatchOnly` with **all runtime/production/epoch/capacity acceptance flags false**. It does not read VM process memory or invoke Unity/IL2CPP.
- `Tools/AssemblyShadow/R03IR/TypeDefCensus/test_verify_native_enumerator_population.py`: 23 narrow test cases, including source-mutation negatives for logical remapping, initialized-only class lookup, cache walkers, physical image eligibility, metadata Reader and the 3:2 B2 source-pass distinction. The true pinned-source test runs only where its exact native checkout is present; it is mandatory **without skips** in CI.
- `.github/workflows/r03-b2-native-enumerator-population.yml`: two independent macOS/Ubuntu source-only jobs, each checking out exact native commit `cecf4b859d50b128e5c0fc6c90cd89e3a452b96a` in a detached, sparse, read-only working tree, running the mutation suite and emitting a bounded JSON report. No compiler, Unity Player, source regeneration or runtime action is invoked.

Eleven source-pin files: `il2cpp-api.cpp`, `MemoryInformation.cpp`, `Assembly.cpp`, `AssemblyShadowOriginalV1ImageScan.h`, `GlobalMetadata.cpp`, `GenericMetadata.cpp`, `ArrayMetadata.cpp`, `MetadataCache.cpp`, `Runtime.cpp`, `AssemblyShadowMetadataLifetime.h`, and `AssemblyShadowBoundedDefinitionExecutionLiveSource.inl`. The script and workflow explicitly fail on stale Git commits, source-file blob drift, missing C++ expressions or skipped native-checkout tests. It is a **lexical source contract**, not an AST or compiler-verified CFG. An unmodeled native path may still exist.

**Evidence:** [exact-code GitHub Actions run 44000649670](https://github.com/night-outlook/hybridclr_demo/actions/runs/44000649670): **2/2 completed/success**, macOS-15 and Ubuntu-24.04, with **23/23 tests passed and no skips on each host**, including a real pinned-native-checkout test. The JSON contract reported `PinnedSourcePopulationMismatchOnly`, verified all 11 native Git blobs, and kept every runtime, epoch, Player, product and Human Review flag false. The separately executed local Primary sandbox suite had **22 passed and one skipped** (no network access to the native checkout); it is not Local Validation. No Unity Editor, IL2CPP compiler or Player was run.

## 3. Source-lifetime contract: what is and is not proved

- `Runtime::Init` opens `g_MetadataLifetimeGate` near the fully initialized tail. `Runtime::Shutdown` holds `s_InitLock`, invokes `CloseAndDrain` after process-exit notification and before thread abort and metadata cleanup. A Reader's initial epoch (1) can prevent teardown while that Reader is admitted. **It does not independently identify the allocation epoch of each borrowed class/type/image, prevent source mutation, freeze the class GC lifetime, guarantee no ABA reuse, or establish a VM-wide atomic snapshot.**
- B2's outer `g_MetadataLock` protects several metadata maps and cached-class lookups. Physical assembly visitation takes `s_assemblyLock`. The generic constructed-class walker separately takes `s_GenericClassMutex`; these source locks are **not** proof of an atomic observation across all caches. Do not introduce new nested lock orders until deadlock and thread-shutdown behavior are reviewed.
- Repeated physical-image, class and registry observations can detect **observed** change only. Equal source handles/generations are neither a GC provenance certificate nor a coherent VM epoch. Never retain raw class, metadata or physical-image pointers past the protected synchronous callback.

## 4. Proposed production design, NOT yet authorized

### Lane P — conservative physical TypeDef-slot upper bound

Under a previously admitted Reader, acquire the existing metadata protection and use original-V1 **token-valid physical image order**. For each valid image, synchronously count `image->typeCount`, classify interpreter/zero-TypeDef images and perform checked 64-bit additions. Count only scalar metadata facts in preallocated storage; avoid `Class::From*`, `GetTypeInfoFromTypeDefinitionIndex`, managed code, name formatting, file IO and per-image allocations. A finite `sum(image->typeCount)` is an **upper bound on distinct handles whose first owner appears in this inventory**, not an exact used-TypeDef high water. Duplicate handles and unused physical types make it conservative; handles outside this token-valid inventory cannot be assumed admitted. Any invalid image, excess image count or aggregate overflow must return **Incomplete**, not a successful count. This lane does not enumerate runtime class shapes or generic instantiations.

### Lane U — observed execution-use inventory (separate measurement)

Begin with an independently witnessed **registered execution-class** population and its source lifetime. Recursively traverse every relevant `ClassRoot`, declaring ancestor, generic definition, argument, composite leaf and existing primitive default, including **pre-owner rejected** paths. Each use is either explicitly resolved through original-V1 first-owner membership or recorded as unsupported/uncovered. Do not derive the expected site plan only from successful `resolveOwner` events; do not take the current 128-handle B2 audit, 129-root preflight or public logical class iteration as an exhaustive planner. A bounded recorder may produce an **IncompleteLowerBound** on overflow or missing callbacks, never a fake final count. The existing host `TypeDefSourceCoverageReplay` remains a tool for checking **planned** visits, not for discovering the entire native graph.

### Cross-lane evidence and acceptance fences

- Bind the two lane inventories to **one declared observation scope**, but do not label the scope an atomic VM epoch until a separately proven synchronization/generation contract exists.
- Preallocate recorder memory before acquiring metadata/assembly locks. Budget worst-case original image scans, owner lookup count, stack, GC/RSS and metadata-lock hold time; do not assume the 1,024-handle/4,096-event synthetic prototype capacities or 65,536 B2 owner scans are adequate.
- Keep first-error and incomplete receipts separate from success. After releasing source locks, export only owned scalar data with no borrowed addresses, and require independently authenticated build/source/trace hashes and first-recovery readback before any product acceptance.
- Preserve original V1 field14/15 semantic and byte parity; do not select fixed-slab vs compact-arena storage or raise native B2's **128 combined TypeDef**, **64-byte name** or **65,536 lookup** limits on synthetic estimates.

## 5. Entry conditions for a future native change and Human Review Gate

1. **Define the population target:** Is the acceptance objective the conservative physical declaration upper bound, the observed registered execution-use graph, the original V1 visible class rows, or separate reported metrics for all three? The recommended plan separates them; no single counter substitutes for another.
2. **Approve source and lifetime:** identify the exact source callbacks, class/metadata allocation provenance and isolation needed for physically hidden and generic classes; review lock order, shutdown and concurrent assembly publication. An initial Reader + `g_MetadataLock` is **necessary but insufficient** for an all-VM snapshot claim.
3. **Review coverage and limits:** enumerate unsupported/rejected paths before choosing a recorder capacity. Define overflow semantics, lock/stack limits, 32/64-bit ABI and platform tests. Validate the new source outside the synthetic host before any runtime activation.
4. **Only then** authorize a dedicated Local Validation batch, its exact four-repository pinned handoff, evidence custody, independent source receipt and Human Review Gate. No consumed B1 oneuse batch can be reused as B2 proof.

**Current source-only disposition:** `PinnedSourcePopulationMismatchOnly`. The native `il2cpp_plus` implementation and 64-native/eight-demo exact source roster are unmodified. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `readyForNativeV2FieldCapture=false`; `nativeV2TransportImplemented=false`; `runtimeAcceptance=false`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or Human Review Gate self-approval.
