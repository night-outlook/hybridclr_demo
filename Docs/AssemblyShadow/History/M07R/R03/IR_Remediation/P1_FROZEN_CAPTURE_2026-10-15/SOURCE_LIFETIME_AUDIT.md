# P1 current VM diagnostic source and lifetime audit (source-bound, not a runtime pass)

**Owner:** Primary Implementation. **Review anchor:** il2cpp_plus codex/assembly-shadow-r01b-h1 prior live source commit 74dbdbea80d83923863303bd2b2c0a87f36541b1. The new P1 frozen capture code is inactive and does not alter these reviewed original VM entry points. Do not infer Unity Player or SDK verification from this audit.

## General diagnostics — AssemblyShadow::GetDiagnosticsJson

Source: il2cpp_plus/libil2cpp/vm/AssemblyShadow.cpp (active enabled section, lines approximately 1295–1394 at the reviewed commit).

1. The function constructs ShadowDiagnosticSnapshot with std::string and std::vector fields and copies startup candidates. It does not use preallocated fixed bounded storage.
2. A transaction mutex protects the status/closure/event portion while copying owned vectors, strings, staged assembly metadata and module-initializer flags. It is released before most remaining diagnostic acquisition.
3. The immutable TypeFailure pointer can supersede snapshot state/detail after the transaction copy. This is a separate atomic read and not necessarily one epoch with the transaction lock.
4. A separate UsageLock only protects copying first-use UseRecord values. The later conversion of use.klass->namespaze/name to dynamic strings occurs outside that lock and any demonstrated type-metadata lifetime ticket. A pointer's use after release cannot be called safe solely because an earlier first-use record was copied.
5. Assembly::CaptureShadowEnumeration independently captures a generation and a dynamic AssemblyVector. ShadowVisibility::CollectOrdinaryClasses separately takes g_MetadataLock to collect pointer values and a class generation. The later class-name, interpreter and staged-metadata reads occur after this function releases its metadata lock; source-backed lifetime/coherence proof across these operations is still required.
6. AssemblyShadowDiagnostics::Serialize uses std::ostringstream and returns an owned std::string. SerializeTo is bounded in output bytes but receives the same already heap-backed ShadowDiagnosticSnapshot and does not bound its capture or GC/RSS peak.
7. The resulting diagnostic state, assembly enumeration and class enumeration may legitimately have different capture generations. Their existing schema must not be silently rewritten to claim a single global epoch.

## Execution diagnostics — AssemblyShadow::GetExecutionDiagnosticsJson

Source: il2cpp_plus/libil2cpp/vm/AssemblyShadow.cpp (active enabled section, lines approximately 1460–1555). Relevant native structs: AssemblyShadowTypeKey.h/.cpp, AssemblyShadowR02Diagnostics.h, AssemblyShadowObservationCounters.h.

1. A fixed std::array of 1024 observed Il2CppClass* is populated under ExecutionObservationLock, copied from a process-lifetime 2048-entry hashed table. The writer has kMaximumExecutionClasses=1024; a new observation above that count increments s_droppedClassObservations. The class pointer inventory is bounded, but this does NOT bound subsequent allocations.
2. The execution observation lock is released before class owner, metadata or initialization flags are inspected. The generic/class metadata owner lookup is based on a separately acquired Assembly::CaptureShadowEnumeration. Its MetadataTypeImages is an allocating std::unordered_map built by traversing each image's typeCount.
3. AssemblyShadowTypeKey::FormatMetadataOnly recursively constructs multiple std::strings, vectors, declaration keys and folded assembly UTF-16/UTF-8 intermediate state, with recursion/declaration depth checks. It has no output-sized allocation bound and no reviewed lifetime ticket for all handles across the released locks. It must be replaced or separately captured/reviewed before claiming a bounded terminal producer.
4. g_MetadataLock protects just the brief static_fields pointer read per class. The cctor/exception flags are read via relaxed atomics afterward. These may not represent a simultaneous state across all classes.
5. Header counters are read by a sequence of atomic operations. The subset-first acquire reads constrain specific subtotal ordering but do not constitute an all-counter epoch. R02 AppendDiagnostics reads many counters while serializing; it still has dynamic observation coverage, saturation, dropped-thread and allocator-overhead limitations.
6. The existing legacy method still writes std::ostringstream and returns std::string; debug address formatting also uses ostringstream. The pure shared execution formatter does not bound metadata acquisition or prove a post-terminal safe point.
7. The new FrozenExecutionCapture deep-copies caller-provided finished type-key/class text and header values. It does NOT validate the source object's generation/lifetime or produce a type key; its ownership guarantee begins only after its checked Add/Freeze have succeeded. No VM calls occur in its SerializeTo.

## Lock order and requirements before integrating P1 into a live producer

Original transaction/metadata/assembly/usage/cache lock order is documented as a bootstrap contract in AssemblyShadow.h, but reading current diagnostics under multiple independent scopes is not an automatic global atomic snapshot. **Do not** simply hold the transaction mutex and g_MetadataLock across recursive FormatMetadataOnly, arbitrary string formatting, native I/O or C# callbacks: that might block initialization, invert internal lock order or create a terminal deadlock. A reviewed source-backed acquisition boundary must:

- Define one allowed producer thread and exactly which locks are held across each coherent part (or explicitly define independently versioned sub-snapshots), including lock ranks and completion guarantees under Failed/FailedAfterCommit.
- Prove all Il2CppClass*, Il2CppType*, Il2CppImage* and metadata type handles remain valid while every referenced field is copied, including class initialization and finalizers. Prove no business logic or managed method is reached during capture.
- Preallocate bounded metadata/identity and row storage *while healthy*. Count/witness exact bytes and hard capacity before a terminal failure; treat unavailable/overflow counts as failures without prefix acceptance.
- Preserve the original complete JSON field order/escaping/state/counters. Count dropped classes, saturation and truncated coverage honestly; do not cap reporting, disable finalizers or change semantic predicates to manufacture success.
- Keep V2 file transaction and any external/managed output outside VM metadata/transaction lock scopes. A physical engine-owner safe-point is not established by this audit or any mocked native coordinator.

**Status:** P1 live acquisition/lock/lifetime/memory guarantees are **Incomplete / NotRun**. The next Primary-owned task is a reviewed VM capture API and bounded type-key/metadata policy; Local is not authorized to invent or implement it.

## Memory budgets and distinctions

The new header fixes 1024 owned rows and a 2,097,152-byte owned text arena, and static_assert limits sizeof the capture object to at most 3MiB. It must be allocated while healthy; post-terminal construction is not demonstrated. These bounds cover only owned execution *input* text and row state, not metadata index/build, C++ allocator overhead, process RSS, managed GC, or production lock duration.

The host V2 experiment simultaneously allocates a separate <=3,932,160-byte unencoded field storage, <=3,932,160-byte encoded memory sink and a 65,536-byte scratch buffer. The sum can exceed the previously defined 4MiB **encoded transport** allowance. For future runtime, stream encoded bytes into the descriptor-authenticated file transaction rather than treating the host's redundant in-memory wire sink as the production allocation plan. The full expected peak-memory policy must be reviewed separately and measured on the installed target.

The 331078-byte execution N fixture and 300032-byte general host fixture are **synthetic**, not actual SNAP-01 producer byte counts. The original real slot14 scanned prefix262145 only; full actual byte count is Unavailable. A complete failure remains a failure, not an invitation to widen V1 text bounds.

## Unchanged evidence and restrictions

SNAP-01 18 cells 14 Passed / 4 Failed, three ON zero raw/exit2 at original field14 >262144, uncapped engine51213 reports/500ms/exit71, N/M/K/I/E FAIL, strict S historical custody Blocked, full R03 review FAIL/review NotRun and all acceptance flags false. No official Unity2022.3.62f2 StandaloneOSX native/managed compiler, no Player, no genuine engine-owner safe point or restart evidence is furnished by P1 host tests.
