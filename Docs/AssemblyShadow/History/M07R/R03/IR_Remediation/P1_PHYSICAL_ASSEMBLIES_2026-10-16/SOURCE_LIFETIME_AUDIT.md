# P1 physical assembly source: lock, lifetime and enumeration audit

**Owner:** Primary Implementation. **Review date:** 2026-10-16 UTC. **Status:** additive bounded physical assembly capture source, verified only under isolated host mocks. P1 is NOT complete; Local Validation remains PAUSED.

## 1. Exact source, scope and invariants

Canonical branch codex/assembly-shadow-r01b-h1, native source night-outlook/il2cpp_plus at **fba5b62148076943ba689b40333894f0edd3c7df**, based on **1d66565855e729bedeaf93ed24078e9a6dbc83ed**. Changes: a new AssemblyShadowBoundedPhysicalAssemblies.h, additive Assembly::TryCaptureBoundedPhysicalAssemblies declaration/definition in Assembly.h/Assembly.cpp, and host-only test/runner/CI. GitHub Connector confirmed the original Assembly::CaptureShadowEnumeration body is **byte-for-byte unchanged**. The original diagnostic getters and other P1 source methods are not modified.

The existing physical enumeration in Assembly.cpp holds s_assemblyLock, calls CopyValidAssemblies on s_Assemblies, and returns AssemblyShadow::ActiveGeneration while still holding that lock. CopyValidAssemblies retains every physical assembly whose token is nonzero, preserving registry insertion order and repeated physical identities/names. It does **not** use the logical assembly mapping or deduplication used by GetAllAssemblies.

The new additive reader uses exactly the same s_assemblyLock and physical s_Assemblies list, skips token==0 records, and copies each admitted physical name plus the physical interpreter-image bit to caller-owned bounded storage while the lock is held. This avoids the original source getter's allocating AssemblyVector and post-lock name dereferences in the **new** source path. Existing GetLoadedAssemblyPhysical already calls hybridclr::metadata::IsInterpreterImage under this same lock, so the new non-allocating classification follows a known existing native lock usage. A null physical entry/image/name now fails closed rather than being silently omitted.

The generation is sampled before and after traversal under s_assemblyLock; an observed active-generation flip is rejected. The retained generation is the **separate original assembly-enumeration generation**, not an all-VM epoch. No status, class, first-use or R02 generation correlation is newly established.

## 2. Owned storage and failure boundaries

- AssemblyShadowBoundedPhysicalAssemblies::Capture is preallocated, noncopyable/nonmovable, single-owner. Caps: 4096 physical entries and 1,048,576 total name bytes; fixed Entry rows retain offset/length/interpreter flag only. It stores no Il2CppAssembly/Il2CppImage/name pointers in a successful record.
- Each source name must be valid as a zero-terminated native string during the synchronous registry-locked copy. The bounded C-string scan refuses a name longer than the remaining storage. It preserves exact original UTF-8 bytes, insertion order, duplicate names and original interpreter classification; no sorting/normalization/de-duplication is introduced. An empty name is preserved if present.
- Capacity overflow, unexpected null/corrupt source, self-alias, illegal phase/reuse and witnessed generation change poison the capture. Neither count nor Get rows is available as a complete result after failure. An input buffer immediately adjacent to the Capture but outside its memory range is not spuriously classified as alias.
- The source reader does not allocate source arrays, call metadata type resolution, execute managed code, open files or call an external sink while s_assemblyLock is held. Up to 1MiB of copied text and 4096 records under the registry lock still imply potentially significant lock duration; actual lock time, contention, queue starvation, RSS, GC and retained memory must be separately measured.
- This is field14 ordinaryAssemblies **only**; it is NOT a replacement for GetDiagnosticsJson or a complete SNAP-01 report. 1MiB is only a per-component text budget, not a license to spend the whole V2 artifact on this field. The authentic complete finalDiagnostics and finalExecutionDiagnostics and frame overhead must fit the unchanged V2 aggregate limits.

## 3. Runtime shutdown and metadata lifetime: explicit limitation

The source lifecycle prevents claiming general safety from the assembly lock alone:

- Runtime.cpp Runtime::Shutdown holds s_InitLock, transitions shutting_down and eventually invokes MetadataCache::Clear when IL2CPP_ENABLE_RELOAD and MetadataAllocCleanup unconditionally. MetadataAlloc.cpp explicitly deletes its s_MetadataMemoryPool / generic metadata pools; Class.cpp and GenericClass.cpp allocate numerous Il2CppClass/metadata objects through MetadataCalloc. MetadataCache::Clear frees physical image/assembly tables.
- This cleanup path is **not source-proven to take s_assemblyLock or g_MetadataLock as a quiescent reader barrier** around all freed class/image/name storage. Runtime::IsShuttingDown alone is not a lock/refcount ticket and the recorded shutting_down variable is a plain bool. A true "not shutting down" observation does not protect a concurrent metadata pool reclamation.
- MemoryInformation::ReportIL2CppClasses / il2cpp_class_for_each crosses regular assembly lists and array/generic/pointer metadata registries; even though AssemblyShadowVisibility::CollectOrdinaryClasses holds g_MetadataLock, this does not prove the separate teardown synchronizes through that lock or that the enumerator has bounded, allocation-free metadata ownership. Do NOT reuse that enumerator from a terminal callback as an implied safe class resolver.
- The **actual supported Unity2022.3.62f2 StandaloneOSX engine-owner callback drain/maintenance/restart protocol is still unavailable** (E0/E1 Blocked). The new assembly capture is therefore an additive, inactive healthy-time-capable source component with **no terminal-time lifetime authorization**. A reliable future caller must prove metadata pool/image and registry lifetime and external shutdown quiescence before invoking it.

The first-use UseRecord.klass stays an **opaque token**. This new source does not resolve that pointer. A physical class-name resolver still needs a separately supported metadata lifetime/owner ticket; it must never acquire g_MetadataLock inside the short UsageLock and never treat raw pointer address equality as full type provenance.

## 4. Source-bound testing

[CI run 38842846530](https://github.com/night-outlook/il2cpp_plus/actions/runs/38842846530) completed SUCCESS at native fba5b62148076943ba689b40333894f0edd3c7df, all 3 jobs: macOS 15 Apple Clang, Ubuntu 24.04 Clang, Ubuntu 24.04 GCC. Each compiled the **exact current Assembly::TryCaptureBoundedPhysicalAssemblies method body** under an explicit std::mutex-backed assembly registry mock and strict C++17 plus ASan/UBSan.

Coverage: zero, 4, 4096 and 4097 physical registry entries; token==0 exclusion, physical order, repeated names and interpreter flag; owned name source mutation, broken registry rows, 1MiB name budget, invalid stage/alias and valid adjacent buffer, observed active generation flip and zero operator-new allocations in the **prepared host method path**. Test-only full general JSON comparison required exact equality among the immutable original V1 serializer, current production V1 serializer and the new staged general builder for a synthetic **411154-byte** physical enumeration. Every other VM domain in that fixture is **MOCKED**.

[Machine evidence](EVIDENCE.json) binds the exact source/method hashes and the three CI artifacts. Primary downloaded the original artifact ZIPs and independently verified **81/81 manifest-declared regular files** by SHA-256 and byte length; no missing/mismatched/unlisted files. This is stronger provenance for host tests, NOT real Player semantics or an official Unity native build.

## 5. Next Primary steps and stop

1. Review and implement a real metadata lifecycle read/owner ticket that is coordinated with Runtime::Shutdown / metadata-pool cleanup and preserves required GC/finalizer servicing. No unsupported source-level hook or guessed Unity ABI.
2. Under that proven owner, implement **bounded physical class** enumeration without borrowed pointers after metadata lock, and source-reviewed names for class-bearing first-use. Fail closed if the source does not expose a supported complete class inventory without allocation/instantiation.
3. Complete bounded physical metadata-owner index + recursive type-key formatter with byte-for-byte original FormatMetadataOnly parity, including generic/array/nested/UTF16 folding; qualify full limits and peak RSS.
4. Integrate transaction inventory, first-use, physical assemblies/classes, execution and R02 into complete authenticated V2 native/C# Player field14/15 + every **unchanged** semantic verifier predicate (P2). Source-backed E0/E1 lifecycle and official P3 managed/55-native SDK compile remain prerequisites.

Historical SNAP-01 remains FAIL/ReturnRequired (14Passed/4Failed, three ON slot14 scanned prefix262145 over V1 bound262144, true complete lengths Unavailable; engine51213 uncapped reports in500ms exit71). N/M/K/I/E FAIL, original strict S custody Blocked, R03 full-stage FAIL/re-review NotRun. R03Accepted=false, H2Passed=false, qualificationApproved=false, ReadyForHumanReviewGate=false, fullLegacyRegressionAcceptance=false; PureInterpreter disabled. **Local Validation remains PAUSED; no new Player root or H2/X02/M08A.**
