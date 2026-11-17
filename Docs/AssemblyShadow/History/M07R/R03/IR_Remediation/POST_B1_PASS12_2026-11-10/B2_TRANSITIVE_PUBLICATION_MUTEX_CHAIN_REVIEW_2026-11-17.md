# R03 B2 — Cross-repository transitive publication mutex chain: source review

**Date:** 2026-11-17 UTC. **Role:** Primary Implementation; independent source-check checkpoint. **Branch:** `codex/assembly-shadow-r01b-h1`. **Tested code anchor:** `night-outlook/hybridclr_demo@3b7d20addb3b34bd3a9d62001e8aa16a16c93d06`. **Read-only source pins:** `night-outlook/il2cpp_plus@cecf4b859d50b128e5c0fc6c90cd89e3a452b96a`, `night-outlook/hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`. The unchanged `hybridclr_unity` branch HEAD is `948c0e3b4f8891481301770115e8ba4945eea6de`.

**Scope boundary:** Source-only checks, not runtime compilation, Player, actual lock acquisition trace, complete deadlock/call-graph proof, source/GC lifetime receipt, capacity decision, or Local Validation authorization. Inactive B2 and all production native sources are unchanged.

## 1. New concrete source finding

The preceding [native lock/lifetime graph review](B2_NATIVE_LOCK_LIFETIME_GRAPH_REVIEW_2026-11-17.md) established a direct `transaction.mutex → g_MetadataLock → s_assemblyLock → UsageLock` path on shadow publication, but left `InterpreterAssembly::PublishStagedImagesBatch` as a transitive call requiring investigation. The actual **separate `hybridclr` repository** supplies that implementation and reveals **two more nested locks**:

| Ordered call segment | Concrete source, under exact pin | Lock / action |
|---|---|---|
| `AssemblyShadow::CommitTransaction` | `il2cpp_plus/libil2cpp/vm/AssemblyShadow.cpp` | Owns `transaction.mutex` through native publication; drops before module initializers |
| `MetadataCache::PublishInterpreterAssembliesBatch` | `il2cpp_plus/libil2cpp/vm/MetadataCache.cpp` | Acquires `g_MetadataLock`, then invokes physical batch publisher |
| `Assembly::PublishShadowBatch` | `il2cpp_plus/libil2cpp/vm/Assembly.cpp` | Acquires `s_assemblyLock`, appends the batch and invokes `tryBegin`/`publish` callbacks |
| `TryBeginPublication` → `PublishActive` | `il2cpp_plus/libil2cpp/vm/AssemblyShadow.cpp` | Manually acquires `UsageLock`; keeps it held through staged-image batch publishing and active snapshot release-store |
| `Assembly::PublishStagedImagesBatch` | `hybridclr/hybridclr/metadata/StagedAssembly.cpp` | Delegates to `InterpreterImage::RegisterImagesBatch` |
| `InterpreterImage::RegisterImagesBatch` | `hybridclr/hybridclr/metadata/InterpreterImage.cpp` | Delegates to `InterpreterMetadataIndexRuntime::PublishBatch` |
| `InterpreterMetadataIndexRuntime::PublishBatch` | `hybridclr/hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp` | Acquires **`reservationMutex`**, then invokes `current->codec.PublishBatch` |
| `InterpreterMetadataIndexCodec::PublishBatch` | `hybridclr/hybridclr/metadata/InterpreterMetadataIndexCodec.h` | Acquires **`codec.mutex_`** while validating reservations and publishing lifecycle states |

The resulting **observed six-lock nesting** is:

`transaction.mutex → g_MetadataLock → s_assemblyLock → UsageLock → reservationMutex → codec.mutex_`.

The ordinary interpreter placeholder path differs: `hybridclr/metadata/Assembly.cpp::Assembly::Create` enters `g_MetadataLock`, calls native `Assembly::PublishInterpreterPlaceholder` under `s_assemblyLock`, then `PublishPlaceholderImage` → `InterpreterImage::RegisterImage` → `InterpreterMetadataIndexRuntime::Publish` → `PublishBatch` (same **`reservationMutex → codec.mutex_`**). The placeholder success path does not itself take shadow `transaction.mutex` or `UsageLock`; its callbacks perform physical assembly image/backlink assignment and rollback on an explicitly failed publish.

`InterpreterMetadataIndexCodec::PublishBatch` uses preallocated codec storage and release-stores to lifecycle entries; `Runtime::PublishBatch` release-stores the publication group after the codec batch succeeds. This is **source-level evidence of the implementation sequence**, not proof of all exceptions, allocation behavior, progress, atomic VM snapshot or all transitive callee locks.

## 2. Exact pinned files

| Repository | File | Verified Git blob |
|---|---|---|
| `il2cpp_plus` | `libil2cpp/vm/AssemblyShadow.cpp` | `dc941907884b9a7f44ade6085d05f2e4a1a96d9e` |
| `il2cpp_plus` | `libil2cpp/vm/MetadataCache.cpp` | `b9a9881c6e6a551c19069446a9be61c21f4c8584` |
| `il2cpp_plus` | `libil2cpp/vm/Assembly.cpp` | `df1acbfdaf054067720d2e7c1545e49100ad93ec` |
| `hybridclr` | `hybridclr/metadata/Assembly.cpp` | `b77eb08bda9fe8c34f9b64473ffe8426d7b5fff7` |
| `hybridclr` | `hybridclr/metadata/StagedAssembly.cpp` | `8b9e9da261365326b327051c43c52acc3b2052ce` |
| `hybridclr` | `hybridclr/metadata/InterpreterImage.cpp` | `afe4b3b9e29fa4023c6025e0b35e13d53a6ff15b` |
| `hybridclr` | `hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp` | `509e357359a8912c05adac3434a7e71b3fc3f83c` |
| `hybridclr` | `hybridclr/metadata/InterpreterMetadataIndexCodec.h` | `2020d4e2da6dea8601525203e7ab307d21c40a73` |

The scanner rejects an unexpected repository HEAD, absent/symlinked file, unbounded file, changed on-disk Git blob, changed Git tree entry, missing call boundary, changed source order or missing mutex. It parses lexical C++ scopes after removing comments/literals; it deliberately distinguishes enabled and feature-disabled `CommitTransaction` bodies. No public source is copied into `hybridclr_demo` as a new production source.

## 3. Implementation and validation

New files, all **only** in `night-outlook/hybridclr_demo`:

- `Tools/AssemblyShadow/R03IR/TypeDefCensus/verify_native_publication_mutex_chain.py`: read-only exact two-repo pin and call-order validator, structured JSON report `PinnedTransitivePublicationLocksOnly`, six-lock shadow chain and four-lock placeholder chain. All product/epoch/acceptance flags **always false**.
- `Tools/AssemblyShadow/R03IR/TypeDefCensus/test_verify_native_publication_mutex_chain.py`: source-shaped positive and fail-closed mutation suite for lock deletion/reordering, missed callback call, missing error/success `UnlockUsage`, changed placeholder rollback, removed codec mutex/lifecycle publication, module initializer moved under transaction lock, altered compile-disabled stub, C++ comments/string decoys and pin completeness.
- `.github/workflows/r03-b2-transitive-publication-mutex-chain.yml`: **two** independent macOS-15 and Ubuntu-24.04 jobs, sparse read-only checkout of the **exact** three `il2cpp_plus` and five `hybridclr` Git blobs; the native-checkout test is mandatory with zero skips, followed by a fresh CLI proof/JSON gate.

**Primary sandbox:** `python3 -m unittest discover -s Tools/AssemblyShadow/R03IR/TypeDefCensus -p 'test_verify_native_publication_mutex_chain.py' -v`: **22 tests / 21 PASS, 1 intentionally skipped** because the source-only sandbox cannot connect to GitHub. This is not real-source proof; the CI source test is mandatory.

**GitHub Actions exact-code CI:** [run 44036353650](https://github.com/night-outlook/hybridclr_demo/actions/runs/44036353650) at **`hybridclr_demo@3b7d20addb3b34bd3a9d62001e8aa16a16c93d06`**: **2/2 completed/success**, macOS-15 and Ubuntu-24.04, **22/22 tests with no skips per host**. Both also executed the CLI directly against the two pinned source repositories and checked structured output and every false acceptance flag.

## 4. Findings, disposition and stopping rule

- **TPUB-01 — PASS / exact static source scope.** The shadow batch and ordinary placeholder both reach the codec publisher through the pinned call edges, and the two previously omitted mutex layers are established. The source gate rejects direct mutation of these operations.
- **TPUB-02 — OPEN / HIGH, end-to-end lock proof.** Neither this lexical source inspection nor the prior lock-graph audit establishes all unrelated callers of `reservationMutex`/codec locks, every reverse-edge candidate, blocking time, thread scheduling, or actual deadlock freedom. **Do not assert a six-lock chain is safe merely because it is source-consistent.**
- **TPUB-03 — OPEN / HIGH, exception safety.** `TryBeginPublication` manually acquires a spin-based `UsageLock` and carries it across calls into **another repository**. `PublishActive` explicitly unlocks on success and normal failure, but there is no independently verified C++ exception-unwind/RAII guarantee for all transitively invoked code and mutex errors. The potential for an exceptional escape while holding `UsageLock` must be resolved before runtime acceptance; this is a design risk, **not an observed runtime failure**.
- **TPUB-04 — OPEN / HIGH, source/GC lifetime and shutdown.** `MetadataLifetime::Gate::Reader`, `g_MetadataLock`, `s_assemblyLock` and current physical image observations do not establish a coherent class/GC metadata allocation epoch or prove `CloseAndDrain` makes finite progress under actual concurrent publication. The complete physical metadata source and Lane U registered execution-use/rejection graph remain separate gaps.
- **TPUB-05 — OPEN.** No real Unity 2022.3 Player, native IL2CPP TU, GC/lock latency/stack/RSS test, complete original V1 fields14/15, native V2 artifact/receipt/readback/first recovery, Human Review Gate approval, or R03 acceptance was performed. Native B2 stays **inactive** with the original combined **128 TypeDef** limit, **64-byte** declaration fields and **65,536** indexed owner lookup cap.

**Next Primary boundary:** Source-review other callers of `reservationMutex`/codec mutex and the user-defined publication callbacks, then design a bounded exception-safe `UsageLock` publication scope if required. Any native modification, real capture, or Local Validation run requires a separately reviewed design and explicit authorization; keep physical Lane P and execution-use Lane U separate.

**Disposition:** `PinnedTransitivePublicationLocksOnly`. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or Human Review Gate approval. Other three repositories and the exact 64-native/eight-demo source manifest remain unchanged.
