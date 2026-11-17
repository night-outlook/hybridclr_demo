# R03 B2 — Pinned native Reader/publication/shutdown lock-graph review

**Date:** 2026-11-17 UTC. **Role:** Primary Implementation. **Scope:** one source-only, non-activating audit of native B2 lock/lifetime assumptions. **Exact code commit:** `night-outlook/hybridclr_demo@71d9d5e7576965a0c954cbf667f049d12fa474ae`, branch `codex/assembly-shadow-r01b-h1`. Native baseline: `il2cpp_plus@cecf4b859d50b128e5c0fc6c90cd89e3a452b96a`; unchanged `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`. **This is not a lock-cycle proof, real Unity run, runtime census, Local Validation authorization, or Human Review Gate approval.**

## 1. Reviewed exact source, not synthetic lock-name assumptions

The verifier binds **nine native Git blobs** by exact commit, tree membership and file bytes. These are inspected in their relevant lexical function scopes (C++ comments and quoted strings are excluded), not by an unscoped `grep`:

| Native source | SHA-1 Git blob | Evidence boundary |
|---|---|---|
| `libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl` | `f988e8a3ebaefe13dde80fa2cb784a673326f395` | Reader/metadata protection, physical visits, in-scope scrubbing |
| `libil2cpp/vm/Assembly.cpp` | `df1acbfdaf054067720d2e7c1545e49100ad93ec` | physical visitor, assembly lock, batch/placeholder callback scopes |
| `libil2cpp/vm/MetadataCache.cpp` | `b9a9881c6e6a551c19069446a9be61c21f4c8584` | batch publication acquires metadata lock then calls assembly publisher |
| `libil2cpp/vm/Runtime.cpp` | `1b176ee5fd3e2127a0237877e5c9c32bc53058b3` | Init gate-open and final Shutdown drain under `s_InitLock` |
| `libil2cpp/vm/AssemblyShadowMetadataLifetime.h` | `d2fe09dd51debbbbc71d67b21347f5d971a3cafd` | initial Reader epoch and unbounded `CloseAndDrain` loop |
| `libil2cpp/vm/AssemblyShadowOriginalV1ImageScan.h` | `41cdb90776f1f68f3fc7cbff85045965e29b99b0` | token-valid physical image source and parent backlink |
| `libil2cpp/vm/AssemblyShadow.cpp` | `dc941907884b9a7f44ade6085d05f2e4a1a96d9e` | transaction mutex, `TryBeginPublication`, `UsageLock`, `PublishActive` |
| `libil2cpp/vm/GlobalMetadata.cpp` | `90a9da38496b316becc3c771be0cd29f8bbf7e7b` | initialized cached class lookup versus `InitOnce` construction |
| `libil2cpp/vm/MemoryInformation.cpp` | `f5bf451d3115d02880f8b54cb932c20c4eda60f6` | public initialized/logical class population is not physical TypeDef census |

## 2. Confirmed source-local ordering; **not** an end-to-end lock proof

| Source path | Ordering observed at exact native source | Remaining unverified work |
|---|---|---|
| Inactive B2 capture | initial `MetadataLifetime::Gate::Reader` → `g_MetadataLock` → `Assembly::TryVisitOriginalV1ExecutionImages` → internal `s_assemblyLock`; two original-V1 image visits, three public class passes, borrowed owner/fact scrub inside metadata-lock scope | source pointer/class generation; independent physical collection completeness; callbacks and other native lock paths |
| Interpreter shadow-batch publication | `MetadataCache::PublishInterpreterAssembliesBatch` takes `g_MetadataLock` → `Assembly::PublishShadowBatch` takes `s_assemblyLock`, executes `tryBegin`/`publish` callbacks in that scope | callback transitive calls, allocator behavior, lock inversion and stalled publication under contention |
| Transaction commit/active publish | `AssemblyShadow::CommitTransaction` holds `transaction.mutex` through the batch call; `TryBeginPublication` acquires `UsageLock`; `PublishActive` calls `InterpreterAssembly::PublishStagedImagesBatch`, release-stores `s_active`, then releases `UsageLock`; failure branch also releases | therefore there is a concrete **`transaction.mutex → g_MetadataLock → s_assemblyLock → UsageLock`** sequence; transitive locks/allocations inside staged-image publication remain unaudited |
| Placeholder publication | `Assembly::PublishInterpreterPlaceholder` holds `s_assemblyLock` while invoking `commit`, `publish` and potentially `rollback` callbacks | callback lock/call graph is not proven by this scan |
| Runtime lifetime | `Runtime::Init` under `s_InitLock` opens the gate after metadata initialization. Final `Runtime::Shutdown` under `s_InitLock` calls `FireProcessExitEvent` **before** `CloseAndDrain`, then aborts threads and later calls `MetadataAllocCleanup` | `FireProcessExitEvent` may invoke managed code; drain spins with no finite timeout; whether every admitted reader can always finish without waiting for a lock held by shutdown is **not proven** |

The actual `Gate::Reader` default admits only source epoch **1**, and its destructor releases the admitted reader. None of these facts authenticates `Il2CppImage*`, `Il2CppClass*`, TypeDef pointer allocation origin, GC lifetime, or an ABA-safe coherent VM epoch. `GlobalMetadata::GetInitializedTypeInfoFromAssembly` reads only existing initialized class caches; the separate `GetTypeInfoFromTypeDefinitionIndex` can materialize a class through `InitOnce` under `g_MetadataLock`. Neither is an independent physical source-lifetime attestation.

**Critical distinction:** an observed shared lock order on two direct paths does not eliminate **all** reverse edges through callbacks, class/GC creation, runtime shutdown or future callers. This audit deliberately reports `deadlockFreedomProven=false`, `transitivePublicationCallbackLocksAudited=false`, `shutdownDrainHasProvenFiniteTimeout=false`, and `classGcVmEpochProven=false`.

## 3. Implementation and evidence

Added to `hybridclr_demo` only:

1. `Tools/AssemblyShadow/R03IR/TypeDefCensus/verify_native_lock_lifetime_graph.py`: exact 9-file commit/tree/blob verification; source-scoped checks of the B2, physical scanner, publisher/callback and shutdown ordering. It recognizes **both** the enabled `CommitTransaction` and separately compiled `FeatureDisabled` stub instead of silently selecting one. It always emits `PinnedLockOrderObservationsOnly`, with no product acceptance, runtime or epoch success flags.
2. `Tools/AssemblyShadow/R03IR/TypeDefCensus/test_verify_native_lock_lifetime_graph.py`: actual-source-pin check plus fixture-based mutation negatives for misplaced/missing locks, token and parent backlink drift, callback ordering, missing `UsageLock` release, misplaced shutdown drain, unsupported compile-conditional ambiguity, class-cache source drift and comment/quoted-string false positives.
3. `.github/workflows/r03-b2-native-lock-lifetime-graph.yml`: exact native checkout on macOS-15 and Ubuntu-24.04, source-only Python unit tests, no skipped native checkout tests, checked JSON contract. No Unity, SDK, C++ production translation unit or Player invocation.

**Verification:** Local Primary source-fixture suite: **21 passed, 1 skipped** (native checkout unavailable in sandbox). The first exact-source CI at `7c9ace3a2581a572953c9403ebbc4d3770faf58d`, [run 44008725371](https://github.com/night-outlook/hybridclr_demo/actions/runs/44008725371), **FAILED**, revealing two compile-time `CommitTransaction` definitions. This was corrected (not waived) in source code commits `31bb9ba89393243b34cd49c0a81ff93649e60fec` and `71d9d5e7576965a0c954cbf667f049d12fa474ae`, with a new regression. [**Corrected exact-code CI 44009016536**](https://github.com/night-outlook/hybridclr_demo/actions/runs/44009016536) **2/2 completed/success**; macOS and Ubuntu **22/22 passed, no skips**. The job parsed the checked-in JSON and confirmed all runtime/acceptance booleans false. The initial failed CI is retained as a diagnosis, never counted as a pass.

## 4. Primary findings and required follow-up gate

- **LOCK-01 — PASS / source-only:** B2's confirmed direct Reader/metadata/assembly path, two physical visits, first-owner source and in-scope identity scrubbing are pinned. No code or native roster was modified.
- **LOCK-02 — PASS / source-only, risk still OPEN:** Shadow publication has a concrete nested **transaction → metadata → assembly → usage** lock sequence; both success/failure usage-lock release are checked. `InterpreterAssembly::PublishStagedImagesBatch` and placeholder callback transitive lock dependencies remain **OPEN / HIGH**. A new native collector must not acquire `UsageLock` under the source locks without a complete reversal audit.
- **LOCK-03 — OPEN / HIGH:** Final Runtime Shutdown holds `s_InitLock` while `Gate.CloseAndDrain` waits with no timeout, after `FireProcessExitEvent`. Cross-thread wait-for cycles, stalled callbacks and source reader completion under shutdown are **not proved safe**. Do not add synchronous dispatch, managed work or blocking IO inside admitted source visitors.
- **LOCK-04 — OPEN / HIGH:** Exact metadata/class allocation provenance and ABA/GC/VM-wide linearization are unproven; two identical physical image scans alone can miss the same source or observe reused metadata. The earlier Lane P synthetic physical-slot bound remains separate from Lane U actual registered execution-use/rejected-path measurement.
- **LOCK-05 — OPEN:** No real Unity Player, metadata-lock hold-time/stack/RSS profile, 32-bit ABI, original terminal V1 fields14/15, native V2 artifact/readback/first recovery, or independent R03 full-stage acceptance. Existing native B2 combined **128 distinct TypeDefs**, **64-byte name** and **65,536 indexed owner lookups** remain unchanged.

**Next review boundary:** Independently inspect and test *all* transitive `PublishStagedImagesBatch` and placeholder callbacks, exact compiler/runtime lock acquisition and metadata allocation/GC lifetime; produce a deadlock/teardown test matrix before designing a live Lane P source attachment. A static text gate is a useful source drift detector, not a proof of safe production integration. Any runtime capture requires a **separately authorized** Local Validation batch and explicit Human Review Gate process. No consumed B1 oneuse-12 evidence can be reused.

**Disposition:** `PinnedLockOrderObservationsOnly`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or Human Review Gate self-approval.
