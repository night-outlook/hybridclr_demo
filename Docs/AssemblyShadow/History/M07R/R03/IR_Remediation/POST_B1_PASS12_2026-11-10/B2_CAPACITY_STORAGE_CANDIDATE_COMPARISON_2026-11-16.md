# R03 B2 — isolated capacity storage candidates (no integration)

**Date:** 2026-11-16 UTC. **Stage:** Primary Implementation, test-only R03 B2 storage feasibility. **Branch:** `codex/assembly-shadow-r01b-h1`. **Forks pinned on entry:** demo `fac1b38e43a94778fbbfa8965d854d3ce5bcfbd0`; hybridclr `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`; hybridclr_unity `948c0e3b4f8891481301770115e8ba4945eea6de`; il2cpp_plus `cecf4b859d50b128e5c0fc6c90cd89e3a452b96a`.

## Existing source-derived problem

The current **inactive** native B2 collector samples up to **1,024 observed execution-class identities** while the root+nonroot TypeDef owner/content audit stores at most **128 distinct handles** in a <=24,576-byte stack object. It owns exactly copied namespace/simple-name data limited to 64 bytes **each**, declaring/generic indices, arity, root/non-root role bits, and independently verified first owner. A first-pass root-only preflight now rejects >=129 distinct root handles early but **does not** count additional nested/generic/primitive TypeDef leaves. The full set can therefore exceed 128 after a 128-root preflight succeeds. Other limits (65,536 indexed metadata lookups; class/GC/VM lifetime/epoch) are independent.

An actual high-water source census, 32/64-bit ABI measurements and real Unity metadata-lock/worker-stack profiling are **not available**. The following candidates are prototypes, **not proposals to raise live B2 limits without human review**.

## Deliverables

- `Tools/AssemblyShadow/R03IR/CapacityCandidates/TypeDefStorageCandidates.h`: pure C++11 candidate A (fixed slab), candidate B (compact metadata + exact-string arena), and a shared no-allocation `Census<Storage>` collector.
- `Tools/AssemblyShadow/R03IR/CapacityCandidates/TypeDefStorageCandidateHost.cpp`: deterministic synthetic 128/129/1,024 owner/TypeDef cases, duplicate root+nonroot role merge, owner conflict, declaration byte drift, 64-byte name boundary, prepared storage capacity, packed-arena exhaustion, fail-first-error and release/reuse cases.
- `.github/workflows/r03-b2-capacity-candidate-host.yml`: separate macOS/Ubuntu C++11/C++17 strict + address/undefined-sanitized host matrix; checks machine-readable output flags. It does **not** invoke Unity or attach to the existing B2 source gate.

### Candidate A — fixed-slab storage

`SlabStorage` preallocates `capacity` exact `Entry` records, each with two 64-byte name fields plus the authenticated-handle/owner-value metadata. Reserving for 1,024 records removes the **128-pair storage ceiling in this isolated model**, while keeping exact copied bytes and explicit root/non-root role flags. Capacity and object size are deterministic; unused short-name bytes still consume memory.

### Candidate B — metadata + exact-byte arena

`ArenaStorage` preallocates `capacity` compact metadata entries and an independent bounded byte arena. Offsets and byte lengths point **inside the owned arena only**; no caller strings are retained. Reusing the same TypeDef handle merges role flags without copying names again. Actual reserved memory is the entry array plus the explicitly chosen arena budget; capacity may fail because either limit is reached. An arena sized for typical short names **does not** automatically accommodate 1,024 maximum-length declarations.

### Shared constraints / hypotheses

The prototypes never dereference opaque handle/owner values and do not perform owner authentication. The caller must independently establish physical image and original V1 first-owner provenance **before** `Add`. Only `Prepare` allocates; it must be invoked **outside** `g_MetadataLock` and metadata Readers in any future integration. `Add`, `Seal`, and failure scrubbing use already reserved storage. A recorded error scrubs all owned bytes, never emits a positive receipt, and preserves the first error. `Receipt` reports paired-count/root/nonroot-count, actual name bytes and reserved bytes; all runtime, Unity and VM epoch flags are always false.

Both candidates currently use a **linear pair lookup** in `Add` (O(n²) total worst-case) to keep initial semantics independently checkable. This is **not** a performance-accepted implementation. A proven preallocated hash/index or another deterministic lookup bound would be necessary before integrating a larger-capacity version under metadata locks.

## Verification and selection criteria

The new workflow should demonstrate all of the following without touching native B2:

1. 1,024 distinct synthetic TypeDef handles admitted when *both* preallocated budgets suffice; explicit 129-record cases succeed within the candidates, unlike the currently reviewed 128-pair live B2 subset.
2. Exact namespace/simple-name bytes, declaration indices, owner values, and merged root/nonroot role bits survive copying. Conflicting owner or changed content rejects with owned bytes scrubbed.
3. Overcapacity, arena overflow, name longer than 64 bytes, missing opaque handle, invalid stage and invalid prepare reject. A released object can be prepared anew without retaining a published positive state.
4. All runtime-acceptance, real-Unity and coherent-epoch flags stay false. Reserve-size comparisons are **host ABI results**, not actual Unity/IL2CPP worker-stack or RSS measurements.

Use measurements from **the exact CI SHA**, not assumed `sizeof` results. Candidate B may be more memory-efficient on short names, but choosing a final arena budget requires a defensible real-source high-water census, including all nested/generic/primitive handles and namespace/name lengths. Candidate A's fixed-record allocation is easier to budget at the cost of reserved unused name bytes. Neither resolves 65,536-lookup limits, metadata/class lifetime, synchronization or full original V1 field14/15 parity.

## Hard stopping point

**No production integration, cap adjustment or Local Validation handoff is authorized by these prototype results.** Existing `il2cpp_plus` source, the 64-native/eight-demo B2 source manifest, and its original getter/B1/active resolver remain unchanged. The independent R03 full-stage review still has historical FAIL/High items. Full native V2 artifact/envelope/independent receipt/first recovery, real Unity native translation unit/Player, and genuine metadata/GC/VM epoch are not proven.

Acceptance remains `readyForNativeV2FieldCapture=false`, `nativeV2TransportImplemented=false`, `runtimeAcceptance=false`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `wholeVmEpoch=NotProven`. PureInterpreter stays disabled. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`. Future selection and product integration require fresh source/host evidence, an exact capacity/latency budget, and the existing Human Review Gate process.

## Verified source-host result and review (candidate code anchor)

[**Capacity candidate CI 43796253756**](https://github.com/night-outlook/hybridclr_demo/actions/runs/43796253756) completed **4/4 PASS** at demo commit `9aa5dd9e031930ab804f16d37ef0e1ffe6c32650`: macOS-15 and Ubuntu-24.04 × C++11/C++17. Every matrix cell ran both `-O2 -Wall -Wextra -Werror -pedantic` and ASan/UBSan builds; **21 synthetic cases and 4,735 assertions per process**. The recorded result was `PassedSyntheticStorageOnly`, `realUnity=false`, `realMetadata=false`, `integratedInB2=false`, `R03Accepted=false`, and `ReadyForHumanReviewGate=false`.

Exact tested source Git blobs: `TypeDefStorageCandidates.h@e48d83272d9207e7d688a59ce44909645f6084e7`; `TypeDefStorageCandidateHost.cpp@75d8017e09a3080cb393373f3d19b329f6deb816`. The workflow checkout was later narrowed to these files at `9aa5dd9e031930ab804f16d37ef0e1ffe6c32650`; the model code was **not changed** by that CI-only optimization.

| 1,024-record host comparison | Fixed slab A | Compact arena B (32 KiB text budget) |
|---|---:|---:|
| Preallocated candidate **reserved bytes** | **163,840** | **73,728** |
| Exact synthetic text consumed (4+4 bytes per distinct pair) | 8,192 | 8,192 |
| Runtime integrated into native B2? | No | No |
| Original native B2 combined cap | 128 | 128 |

For these short synthetic names, B reserves **90,112 fewer bytes (~55%)** than A. This is the **candidate's explicitly accounted buffers**, not complete process RSS, allocator overhead, native Unity ABI measurement, or a measured C++ memory high-water mark. The arena B allocation comprises 40,960 bytes of records plus a 32,768-byte name budget.

**Important contrary case:** 1,024 declarations each with both 64-byte fields at the limit require at least **131,072 bytes of exact-name arena**, before record storage; at the observed metadata record size, B would then reserve **172,032 bytes**, which is **8,192 bytes more** than A's 163,840-byte fixed slab (allocator overhead excluded). A fixed 32 KiB arena **fails closed**, rather than magically supporting that worst case. A real-name distribution and expansion headroom are required to choose B.

### Primary static review of the prototype

- `SlabStorage::Prepare` and `ArenaStorage::Prepare` own their allocations and must precede any future metadata lock. The `Add`/role merge path itself contains no explicit allocation; `Release` and error transitions zero owned fields. The synthetic host did **not** instrument global allocator hooks or quantify real lock latency.
- Both candidates check exact `handle`, `owner`, namespace/simple-name byte length and content, indices, arity and root/nonroot roles. They do **not** perform independently authenticated physical first-owner proof. Every caller's handles are synthetic values. The candidates cannot be plugged into the live source without an explicit owner/metadata-lifetime design and a new separate review.
- Both use a **linear existing-handle search**. At 1,024 distinct pairs, this is O(1,024²) total comparisons in the worst case, not a bounded production-latency acceptance proof. A preallocated index, caller-side source census, and measured performance remain necessary.
- The header is not referenced by `il2cpp_plus` or the existing native B2 source manifest. The actual native 128-cap collector and its prior exact four-repository source audit remain untouched. No test-only result promotes the current 128-pair live cap.

**Disposition:** **Two candidate implementations and reproducible host evidence available; no production storage design selected.** Next Primary work is a sourced root+nonroot TypeDef population/name-length census (including generic/nested/primitive references) and owner-lookup/metadata-lock latency budget, then a scoped design selection. Stop at the existing Human Review Gate before any production capacity architecture changes.
