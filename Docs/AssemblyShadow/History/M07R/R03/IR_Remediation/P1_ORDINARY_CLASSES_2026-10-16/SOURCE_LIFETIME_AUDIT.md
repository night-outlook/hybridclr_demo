# R03 P1 — ordinary physical class capture: source, lock and lifetime audit

**Owner:** Primary Implementation. **Review date:** 2026-10-16 UTC. **Scope:** bounded, owned ordinary class diagnostic rows using existing IL2CPP source. NOT a source-proven terminal metadata lifetime ticket, Unity/Player validation or completed P1.

## 1. Authoritative source

Canonical native source: night-outlook/il2cpp_plus at 2db707eb3021516c2cef962b3d294b4d047e4ef9 on codex/assembly-shadow-r01b-h1, based on fba5b62148076943ba689b40333894f0edd3c7df.

Reviewed actual implementation: libil2cpp/vm/AssemblyShadowVisibility.cpp and .h; libil2cpp/vm/AssemblyShadow.cpp, MemoryInformation.cpp, Runtime.cpp, MetadataCache.cpp, MetadataAlloc.cpp and .h, Class.cpp, GenericClass.cpp, MetadataLock.h; libil2cpp/il2cpp-api.cpp and both current/frozen/historical general serializers.

New production sources: libil2cpp/vm/AssemblyShadowBoundedOrdinaryClasses.h and an additive AssemblyShadowVisibility::TryCaptureBoundedOrdinaryClasses with a synchronous CaptureOwnedOrdinaryClass callback. GitHub Connector compared the complete original CollectOrdinaryClasses body before/after: byte-for-byte unchanged (284 bytes). Existing getters, native Player writers, semantic policies and prior source collectors were not modified.

## 2. Exact source semantics preserved

Original CollectOrdinaryClasses locks g_MetadataLock, captures AssemblyShadow::ActiveGeneration and invokes il2cpp_class_for_each with CollectClass, which pushes raw Il2CppClass pointers into a dynamic vector. Original GetDiagnosticsJson dereferences those pointers later, after the enumeration lock: physical assembly name, namespace and class name, interpreter flag, generic-instance flag, and staged-metadata flag.

The new parallel, inactive collector holds the same g_MetadataLock, enumerates through the same il2cpp_class_for_each API and copies each V1 field into fixed owned byte storage *within* the synchronous callback. No class, image or source-name pointer survives in a completed record.

The original V1 typeName adds namespace + "." only when namespace is non-null and nonempty. The new component preserves empty/null namespace without a dot. It retains the exact original boolean names and field ordering through AssemblyShadowFrozenGeneralCapture.

**Important correctness finding repaired:** the old getter obtains isInterpreter using Interpreter(klass->image->assembly), which queries the *physical assembly's image*. The first new version queried klass->image directly. The final source uses the original klass->image->assembly->image and rejects missing physical-image pointers. The host fixture deliberately supplies differing class/assembly image flags and verifies the assembly-image result; the initial green CI runs before that correction do not qualify the final source.

Visibility is independently published through the s_privateImages linked-list head. The new method reads both ActiveGeneration and the private-image head before/after traversal and rejects any observed change in either. This is an observed-change detector; equal readings do NOT establish a global VM epoch or exclude all source mutations.

## 3. Lock scope, allocations and omissions

g_MetadataLock is the baselib::ReentrantLock used by the original collector. The new callback performs bounded text copying, scalar reads and the original ClassUsesStagedMetadata traversal. The capture has 8192 class rows and a 2097152-byte owned text budget, is preallocated, one-shot, noncopyable and fails closed on malformed input, overrun, wrong stage or changed source. A partially filled array cannot be returned as a completed result.

**End-to-end enumeration is NOT proven allocation-free.** The public il2cpp_class_for_each delegates to MemoryInformation::ReportIL2CppClasses, which walks physical/logical assembly, array, SZ-array, generic and pointer metadata registries. Assembly::GetAllAssemblies may generate a new heap-backed snapshot after invalidation. ClassUsesStagedMetadata recursively traverses class/type/generic relationships with cycle-path detection; it is now called while g_MetadataLock is held, unlike the older getter's postlock flag formatting. Worst-case recursion depth, duration under the metadata lock, and runtime metadata allocation/instantiation behavior remain unqualified. When the bounded callback has failed, the public iterator may continue visiting classes; it cannot be treated as an interruptible bounded producer.

The per-component 2MiB name budget does not supersede V1 per-text 262144 or V2 frame65536, artifact3932160, envelope262144 and combined encoded4194304 limits. Final complete fields, frame overhead and provenance must be verified by the future authenticated Player path. No count is silently capped, and the source does not invent omitted class records.

## 4. Teardown is NOT synchronized by this lock

Runtime::Shutdown in Runtime.cpp invokes ProcessExit, transitions its plain shutting_down flag, handles native threads/finalizers, calls MetadataCache::Clear under IL2CPP_ENABLE_RELOAD, then calls MetadataAllocCleanup unconditionally. MetadataCache::Clear can free physical image and assembly tables; MetadataAllocCleanup deletes metadata pools used by Class.cpp and GenericClass.cpp for Il2CppClass and related structures.

The examined cleanup paths are not source-proven to participate in g_MetadataLock as a reader/writer lifetime barrier. A metadata lock protecting a reader does not itself preclude another shutdown path from releasing its memory. Runtime::IsShuttingDown returns a plain bool, not an atomic lifetime lease. The Unity2022.3.62f2 StandaloneOSX engine-owner safe point, callback drain, GC/finalizer/service continuation and restart remain E0/E1 Blocked.

**Consequently the new collector is inactive** and must not be called from terminal callbacks until a real read-admission/teardown-drain protocol and bounded enumeration semantics are implemented and approved. Likewise, UseRecord.klass remains an opaque token. The new class inventory does NOT authorize resolving that pointer without separate lifetime ownership and without avoiding g_MetadataLock-inside-UsageLock inversion.

## 5. Host source-bound verification

[Final CI run 38845581521](https://github.com/night-outlook/il2cpp_plus/actions/runs/38845581521) completed SUCCESS on macOS15 Apple Clang, Linux Clang and Linux GCC, in strict and ASan/UBSan. The runner mechanically extracts and compiles the complete actual bounded source method AND its real callback against explicit host class/image/enumerator/metadata-lock mocks.

The test covers empty, small, 8192 and 8193 class cases; correct UTF-8 and control bytes; exact namespace-dot-type formatting; class assembly-image predicate disagreement; all generic/staged/interpreter flags; copy-before-source-mutation; excluded invisible/uninitialized mock types; null class/image/assembly/physical image/name; wrong stage, alias and valid adjacent buffer; generation and private-image-head publication changes; overlong class inventory.

The captured 8192-class rows were combined with explicitly MOCKED other VM domains, then complete immutable original V1, current product V1 and staged frozen V1 JSON output matched all **1403463 bytes**. This is a synthetic specimen, NOT the actual unknown complete SNAP-01 finalDiagnostics payload.

Three original CI ZIP artifacts were downloaded through the GitHub Connector. Primary independently checked **84/84 manifest-declared regular files** against archive byte length and SHA-256, found no missing/mismatched/unlisted files, and verified all 18 compiler/run commands and each strict/sanitized success. [EVIDENCE.json](EVIDENCE.json) contains source hashes and original ZIP hashes. Exploratory runs with stale test expectations remain failures; only final run 38845581521 qualifies the final native source.

This result is source-bound host-mock evidence, NOT installed Unity SDK compilation, actual VM class metadata lifetime, allocator/lock/GC/RSS measurements, Player behavior, or R03 acceptance.

## 6. Next Primary gates and stop

1. Source-review a non-fabricated metadata read-admission and shutdown-drain protocol coordinated with Runtime::Shutdown, metadata pools, and GC/finalizer/engine-owner lifecycle. Prove destructor/cleanup races, reentrancy and lock order; no guessed Unity ABI or modeled ready flag.
2. Prove complete public class iterator semantics without unwanted allocations/metadata creation, with bounded recursion/hold time under g_MetadataLock and source-backed coverage/dropped accounting.
3. Only under a proven owner, resolve class-bearing first-use tokens without holding UsageLock while acquiring metadata lock; then build bounded physical type-owner and exact recursive type-key generation, including generics and nested types.
4. After complete P1 capture/peak memory proofs, integrate authenticated V2 native/C# field14 and field15 with every unchanged semantic verifier predicate. E0/E1 and official P3 managed/55-native SDK compilation remain open; no fresh Local cycle authorized.

Historical SNAP-01 remains FAIL/ReturnRequired: 18 cells, 14 Passed/4 Failed; ON slot14 observed prefix 262145 above V1 262144, full true payload length Unavailable; engine 51213 uncapped reports/500ms/exit71. N/M/K/I/E FAIL, original strict S custody Blocked (416844 originals, 339367 survivors, 77477 missing and four roots unavailable), full-stage R03 independent review FAIL / re-review NotRun. All R03/H2/qualification/Human Review Gate acceptance flags are false. PureInterpreter expansion disabled. Local Validation PAUSED; no H2/X02/M08A.
