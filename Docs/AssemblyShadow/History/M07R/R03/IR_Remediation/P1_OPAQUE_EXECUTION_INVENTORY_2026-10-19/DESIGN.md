# P1 — inactive bounded opaque execution-observation inventory

## Objective
The consumed Local 20261019-48ee PASS established 15/15 source/SDK-only components, 70 command-failure tests and 85/85 installed native syntax checks. The existing inactive empty-live source rejects nonempty observed class inventories because physical class origin, metadata lifetime and type-key formatting cannot yet be proven. This increment introduces a narrower real VM **opaque inventory census** for zero AND nonzero observed classes, without claiming a complete execution record or enabling original getters.

## Production implementation
- New AssemblyShadowOpaqueExecutionInventory.h defines one-use preallocated Scratch, two fixed 2,048-slot snapshots, maximum 1,024 observed nonnull classes, an explicit size <=33,000 bytes, typed errors and an acceptance-false Receipt.
- New AssemblyShadowOpaqueExecutionInventorySource.inl is included exactly once in AssemblyShadow.cpp and declared only behind the existing feature switch in AssemblyShadow.h. It has **no** original getter, managed, Player or V2 file-transport caller.
- Under a single initial-runtime MetadataLifetimeGate.Reader, copy the complete fixed existing execution-observation pointer table twice, holding ExecutionObservationLock for each bounded copy. No class pointer is dereferenced, classified, formatted, returned or placed in a public record; no g_MetadataLock, UsageLock, transaction mutex or heap/managed/file call is nested.
- Validate exact count, 1,024 bound and uniqueness after release of the lock. Compare the two complete slot arrays exactly, together with observed active identity, generation and state. Reject duplicate entries, count mismatch, source changes, closed admission, reuse and any missing observation. Clear both scratch snapshots before return.
- A success records only observed count/generation and stable-source-samples booleans. PhysicalClassPointerOriginProven, coherentVmEpochProven, executionJsonComplete, playerExecution and runtimeAcceptance always remain FALSE. Clearing is semantic invalidation, not guaranteed cryptographic zeroization.

## Scope and cost
Only two 2,048-slot copies execute inside the existing short observation lock. The exact duplicate and equality checks run after unlocking, in fixed storage without heap allocation. Uniqueness checking has a bounded worst-case quadratic comparison cost; no production latency/GC/RSS, all-VM epoch, ABA-free source, shutdown deadlock or pointer lifetime guarantee follows. The method is INACTIVE and its opaque values must never be reused for metadata dereference without a separate provenance/lifetime design and Human Review Gate.

## Verification
The native runner compiles the actual production header and method against explicit VM mocks, and authenticates the original AssemblyShadow.cpp/AssemblyShadow.h Git blobs after removing only the additive declarations/includes. Two C++17 host profiles (strict and ASan/UBSan) run 18 distinct groups each, including 0/1/3/1024 nonempty inventories, duplicate pointer, malformed counts, same-count pointer replacement, relocation, state/active changes, closed admission and scratch reuse. GitHub CI tests Mac Clang, Linux Clang/GCC; host scope ONLY.

Demo adds opaque-inventory as the sixteenth independent Local source child and a standalone native SDK signature probe as translation unit 18; candidate native SDK syntax total becomes **90 = 18 × five profiles**, alongside the unchanged five positive managed products and expected-negative control. The 70 Python command-failure tests remain; aggregate regression mock cases now include a failed opaque-inventory child.

One new source/SDK-only Local cycle may be separately authorized after exact four-repository pinning; no Unity Editor/Player, E0/E1 engine tests, runtime seven-root suite, historical result changes or automatic Human Review Gate.
