# R03 B2 — deterministic indexed TypeDef storage candidates

**Date:** 2026-11-16 UTC. **Scope:** Primary Implementation of isolated **test-only** storage alternatives. **Branch:** `codex/assembly-shadow-r01b-h1`. **Exact tested demo commit:** `fdbad90d8bed6ba72e4d6329988ff6d255e06745`. Native `il2cpp_plus` remains `cecf4b859d50b128e5c0fc6c90cd89e3a452b96a` and **is not modified or integrated**.

## Source-derived problem and design choice

Previously, both candidate `Census<Storage>::Add` methods performed a linear search of all existing TypeDef handles. With N=1,024 records this imposed O(N²) total comparisons during ingestion, unacceptable as evidence for a future time-bounded metadata-lock source. The earlier candidate report [B2 capacity storage comparison](B2_CAPACITY_STORAGE_CANDIDATE_COMPARISON_2026-11-16.md) explicitly left indexing unresolved. A hash table would be fast for ordinary distributions but could degrade to an O(N) lookup on adversarial or heavily colliding handle values; the acceptance budget needed a more explicit **worst-case index-path bound**.

**Implemented in test-only source:** `BoundedHandlePatriciaIndex`, a compressed MSB-first binary Patricia trie keyed by **opaque `uintptr_t` handle identity only**. No VM class, type handle, image, owner or metadata pointer is ever dereferenced by the index.

- The tree maintains at most **one leaf per distinct handle** and at most one additional branch per distinct handle. For a caller-selected capacity C <=1,024, `Prepare(C)` allocates **2*C nodes** (including unused index 0) once before any future metadata lock. One-based 16-bit indices cannot overflow at C<=1,024. No insert, lookup, role merge, Seal or failure scrub allocates storage.
- Branches test a monotonically increasing **bit position** along each root-to-leaf path. At most `8*sizeof(uintptr_t)+1` node visits are needed to reach a leaf. Source-level bounds: **65 lookup visits / 130 insertion node visits** on 64-bit; the 32-bit theoretical bounds are 33/66, **not** yet tested by a 32-bit native build. Insertion also finds the first differing bit in at most pointer-width bit tests. Therefore index operations have **O(pointer-width)** deterministic path lengths independent of the number or order of enrolled handles, instead of quadratic scanning. This is not a proof of end-to-end capture latency.
- The `Census` retains the existing exact second-stage semantics: `owner` equality, complete metadata indices/arity, byte-exact namespace/simple-name copy, and root/nonroot role merge. On an index insertion or invariant failure the first error is `IndexInvariant`; the candidate clears index and owned storage, rejects further additions, and publishes no positive receipt. `Seal` now checks index count and traversal invariants *before* marking the result complete.
- Both fixed-slab and compact-arena models use the **same preallocated index**. `Release` clears the key nodes (including pointer values) and frees all candidate buffers. Reuse requires a new explicit `Prepare`.
- This index authenticates **no** original V1 first owner. Such proof remains a separate, mandatory step before any hypothetical native integration.

## Exact source and tests

| Test-only path | Git blob SHA at code commit |
|---|---|
| `Tools/AssemblyShadow/R03IR/CapacityCandidates/BoundedHandlePatriciaIndex.h` | `928d5986cb077864322b6755178d8e3a42241257` |
| `Tools/AssemblyShadow/R03IR/CapacityCandidates/TypeDefStorageCandidates.h` | `08e5a8f970b825867696d3d1a83abf788860ceee` |
| `Tools/AssemblyShadow/R03IR/CapacityCandidates/TypeDefStorageCandidateHost.cpp` | `f195b037513c4721d101aa7a548d2488a197f3d8` |
| `.github/workflows/r03-b2-capacity-candidate-host.yml` | `00318d934205f98382dddddaeafdb65e292d1cf8` |

Additional focused cases exercise:
- 1,024 distinct handles with identical low-bit patterns that would collide in a naive `(key>>3)%N` hash; reverse-order duplicate additions merge the nonroot role without duplicating names;
- handles with the same top bit and long common prefixes, including first/last leaves after multiple Patricia splits and owner-conflict first-error cleanup;
- direct Find/Insert of all 1,024 keys in both directions, absent key rejection, zero-key rejection, duplicate capacity handling, Clear and Release/reprepare;
- the existing 129, 1,024, owner conflict, exact declaration drift, 64-byte field limit, arena exhaustion, failed prepare and fail-first-error tests.

## Verified source-host CI and measured reservation

[**Dedicated candidate run 43798253582**](https://github.com/night-outlook/hybridclr_demo/actions/runs/43798253582): **4/4 PASS** on macOS-15 and Ubuntu-24.04 × C++11/C++17. Each matrix job completed both `-O2 -Wall -Wextra -Werror -pedantic` and ASan/UBSan profiles. **26 cases / 14,151 assertions per process**. The exact recorded status is `PassedSyntheticStorageOnly`; `realUnity=false`, `realMetadata=false`, `integratedInB2=false`, `runtimeAcceptance=false`, `R03Accepted=false`, `ReadyForHumanReviewGate=false`.

| Host-ABI reserved storage for 1,024 records | Fixed slab A | Compact arena B, 32-KiB text budget |
|---|---:|---:|
| Original candidate allocation, no index | 163,840 B | 73,728 B |
| Preallocated Patricia index, **2,048 nodes** | 32,768 B | 32,768 B |
| **Total counted reserved buffers** | **196,608 B** | **106,496 B** |

Measured shared index: 32,768 bytes on the tested 64-bit hosts; worst-case lookup bound 65 visits, insertion bound 130. Compact remains 90,112 bytes smaller for short synthetic names, **but not** for all valid name lengths. At 1,024 records × (64-byte namespace + 64-byte simple name), the compact arena would need 131,072 bytes of text plus metadata and index; its reservation would exceed the slab. A fixed 32-KiB text budget rejects such inputs. These totals omit heap allocator metadata, fragmentation, real Unity thread stacks, VM/GC and independent source lifetime storage.

## Review findings, limitations and stopping point

**INDEX-01 — source-host PASS:** Both prototypes use deterministic, bounded key indexing without per-Add allocation. Existing exact byte/owner/role semantics and fail-closed error handling pass tested boundaries.

**INDEX-02 — OPEN (actual census):** No real-game root-plus-nonroot TypeDef high-water measurement, namespace/simple-name distributions, original first-owner overlap or generic/nested/primitive reference census. A capacity of 1,024 is a synthetic comparison, **not** a chosen production bound.

**INDEX-03 — OPEN (runtime proof):** Only 64-bit macOS/Linux host ABI was measured. No official Unity 2022.3 C++ translation-unit/GameAssembly or Player verification, 32-bit target ABI, metadata-lock latency, worker-stack/RSS/GC profiling, immutable class/metadata owner lifetime, coherent VM epoch or original full V1 field14/15 parity.

**INDEX-04 — NOT IN SCOPE:** Indexing does not change the native B2 **combined 128-handle** limit or <=64-byte declaration field caps, 65,536 metadata lookup budget, native V2 transport/receipt/first recovery, or the historical independent R03 FAIL/High findings. Earlier B1 oneuse-12 Player results cannot be reused as B2 evidence. The ancillary historical R02 source-pin CI failure remains open.

**Disposition:** Keep both candidates isolated; **no design is selected or integrated**. The next substantive Primary step is a source-derived root+nonroot census strategy and explicit owner/metadata-lifetime contract, followed by latency/allocator bounds and a separate Human Review Gate before any production capacity redesign. The exact 64-native/eight-demo four-repository source manifest and all four native branch pins remain unchanged.

**State:** `readyForNativeV2FieldCapture=false`, `nativeV2TransportImplemented=false`, `runtimeAcceptance=false`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `wholeVmEpoch=NotProven`; PureInterpreter disabled; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`. No Local execution batch or new milestone is authorized.
