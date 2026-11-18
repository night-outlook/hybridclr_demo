# R03 B2 — Native publication visibility and exceptional-exit envelope (Primary Implementation)

**Evidence UTC date:** 2026-11-18. **Branch:** codex/assembly-shadow-r01b-h1. **Scope:** exactly one pre-integration, read-only production source-contract review and regression suite in hybridclr_demo. This is **not** a production correction, full compiler CFG proof, authorization of Local Validation, R03 acceptance, or Human Review Gate approval.

## 1. Objective and fixed source

After the actual Codec host tests and actual Runtime-with-mock-Bridge host tests passed, the next uncovered correctness boundary was the *real* native assembly/metadata registry publisher and real VM active-snapshot visibility predicate. Prior reviews identified the irreversible codec store and manual UsageLock; this cycle checks the complete native callback-to-Bridge chain with exact source pins and repeatable negative tests.

Fixed production commits (no production edits):
- **night-outlook/il2cpp_plus@cecf4b859d50b128e5c0fc6c90cd89e3a452b96a**
- **night-outlook/hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55**
- **night-outlook/hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de**

The seven source files, authenticated both against Git HEAD tree object and exact on-disk blob, are:

| File (repository) | Source blob |
| --- | --- |
| libil2cpp/vm/AssemblyShadow.cpp (il2cpp_plus) | dc941907884b9a7f44ade6085d05f2e4a1a96d9e |
| libil2cpp/vm/Assembly.cpp (il2cpp_plus) | df1acbfdaf054067720d2e7c1545e49100ad93ec |
| libil2cpp/vm/MetadataCache.cpp (il2cpp_plus) | b9a9881c6e6a551c19069446a9be61c21f4c8584 |
| hybridclr/metadata/StagedAssembly.cpp (hybridclr) | 8b9e9da261365326b327051c43c52acc3b2052ce |
| hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp (hybridclr) | 509e357359a8912c05adac3434a7e71b3fc3f83c |
| hybridclr/metadata/InterpreterMetadataIndexCodec.h (hybridclr) | 2020d4e2da6dea8601525203e7ab307d21c40a73 |
| hybridclr/metadata/AssemblyShadowBridge.cpp (hybridclr) | d756308613e4a8e64f67b5295b1ec1787c3901fc |

## 2. Source-derived publication design and failure classification

**Pre-publication reservations:** AssemblyShadow::CommitTransaction (AssemblyShadow.cpp:1208–1254) allocates the local ActiveSnapshot and builds maps before setting Committing and invoking MetadataCache::PublishInterpreterAssembliesBatch. MetadataCache.cpp:1137–1147 holds g_MetadataLock and reserves the CLI registry vector before calling Assembly::PublishShadowBatch. Assembly.cpp:269–290 takes s_assemblyLock, reserves the physical vector, then invokes tryBegin. This is a source-order witness only.

**Cross-callback UsageLock:** TryBeginPublication (AssemblyShadow.cpp:703–711) manually acquires LockUsage, checks UsedClosureMember and returns true *without releasing it*. The lock remains held through nested registry writes and PublishActive; PublishActive releases it on normal false or success. The local UsageLock RAII class at lines 351–355 is **not** instantiated in these two callbacks. Neither callback declares an exception boundary, and no native catch around the entire cross-callback publication was observed in the reviewed source.

**Normal bool-false registry rollback:** Assembly::PublishShadowBatch appends to s_Assemblies after tryBegin; if publish returns false it shrinks the vector to originalSize. MetadataCache::PublishShadowRegistries appends to s_cliAssemblies and shrinks that vector on a false publishActive result. These two rollback paths are **inside if (!publish(...))**, so a thrown C++ exception is not demonstrated to execute them. This proves the explicit false-return source shape; it does NOT prove exception rollback or concurrent reader correctness.

**Irreversible codec and publication-group phase:** StagedAssembly.cpp:538–542 forwards to InterpreterImage::RegisterImagesBatch, which delegates to the actual Runtime::PublishBatch. Runtime.cpp:226–251 first validates image associations, calls codec.PublishBatch and returns its error if non-None. Only after success does Runtime store each group identity, release-store group.active=1 and return None. The pinned codec's PublishBatch (Codec.h:549–583) validates the complete input and then release-stores Lifecycle::Published for each record. The first lifecycle release-store is the **point of no return** for that codec state. It is not a general transactional rollback primitive.

**Real native VM visibility:** AssemblyShadowBridge::IsPublicImage (AssemblyShadowBridge.cpp:39–44) requires a non-null image, exact image-index match, Il2CppImage and assembly pointer, then calls il2cpp::vm::AssemblyShadow::IsActiveShadow. That native method (AssemblyShadow.cpp:1944–1948) loads s_active with acquire semantics and checks active->shadowToBaseline membership. Runtime's Public helper (Runtime.cpp:51–65) separately requires active publication-group membership before applying this Shadow gate. This rules out a source-level *intent* that codec lifecycle stores alone grant public Shadow image lookup. No cross-thread Unity execution has been measured.

**Snapshot ownership hazard on unknown exceptional exit:** PublishActive (AssemblyShadow.cpp:714–728) sets staged->published, then s_active.store(snapshot, release), then UnlockUsage. CommitTransaction releases its local unique_ptr<ActiveSnapshot> **only after** the nested publication callback returns. There are no source-observed explicit throw statements between the s_active store and the local release, but a future new exception path in this interval could leave a dangling active pointer if the unique_ptr unwinds. More immediately, an exception between manual LockUsage and the normal UnlockUsage exits could strand UsageLock and bypass both vector rollbacks. Neither event is claimed to have occurred.

**Commit failure classification:** CommitTransaction's *bool false* branch restores s_state=Validated and labels runtimePublisher=false as an InternalError or used-closure denial as BaselineAlreadyUsed. Source pinning supports only normal returns. For an exception escaping after s_state=Committing, the current source does not establish a terminal/restart receipt; an unknown post-codec outcome cannot safely be mapped onto this normal-return Validated reset. RAII lock release alone would not recover the codec lifecycle or registry consistency.

## 3. Bounded Primary implementation plan and executed work

1. Read exact production source and lock/visibility boundary. Do not change any native repository.
2. Implement a **new** fail-closed, exact-Git-blob source verifier in Tools/AssemblyShadow/R03IR/TypeDefCensus/verify_native_publication_visibility_boundary.py, scoped to the seven files. It records normal-return and acquire/release ordering, metadata/assembly rollback, usage-lock transfer, Runtime/Codec group activation and actual Bridge→VM active membership. It emits explicitly false exception-safety, native/runtime and acceptance flags.
3. Implement test_verify_native_publication_visibility_boundary.py: 26 source/negative-mutation cases running against the **real pinned Git checkouts**, with no synthetic passing fixture, covering removed locks/preallocation/normal rollback, missing begin guard, missing unlock, invalid release/acquire semantics, bypassed bridge membership, post-publication errors, changed terminal classification and unreviewed catch insertion.
4. Add .github/workflows/r03-b2-native-publication-visibility-boundary.yml with detached sparse checkouts of exactly the two pinned source repos, macOS 15 / Ubuntu 24.04, no-skips unit tests and a machine-readable source-boundary receipt.
5. Inspect and preserve failed CI attempts; repair only the verifier/test harness, not production source. Stop without native integration or new Local handoff.

**New tested code commit:** night-outlook/hybridclr_demo@7d23259daf8b61481117d33b52a8be21a201d450. Latest documentation-only HEAD must be verified separately. No hybridclr, hybridclr_unity or il2cpp_plus source changed.

## 4. Exact CI results and review

- [Initial workflow run 44228197602](https://github.com/night-outlook/hybridclr_demo/actions/runs/44228197602): **FAILED 2/2**; one positive verifier test incorrectly assumed the two UnlockUsage tokens in PublishActive were unique; three mutation tests used nonunique anchors in a large native translation unit. These are test/verifier defects, not observed production failures.
- [Intermediate run 44228336783](https://github.com/night-outlook/hybridclr_demo/actions/runs/44228336783): **FAILED 2/2** while the source verifier/test mutations were being corrected. Do not promote to success.
- **Final [exact-code run 44228362237](https://github.com/night-outlook/hybridclr_demo/actions/runs/44228362237): PASSED 2/2**, Ubuntu 24.04 and macOS 15 both completed/success on tested code 7d23259daf8b61481117d33b52a8be21a201d450. Each OS ran **26 tests, all passed**, no skips, against authenticated seven production source files, then emitted the source-contract JSON and validated every restricted flag. No compiler/Unity Player was invoked in this workflow.

**Finding PUBVIS-01 — PASS / narrow source scope:** both normal-false registry rollback paths, the actual Runtime group gate and the real Bridge→VM active-membership path are present at the pinned sources. This is a source order/branch shape check plus mutation coverage, **not** a compiler CFG, native callback execution or concurrent visibility test.

**Finding PUBVIS-02 — OPEN / HIGH:** cross-callback manual UsageLock ownership lacks a reviewed exception-unwind guarantee. The two registry rollback branches are reached on false returns only. A failed/throwing native continuation can violate lock/registry custody; the actual invocation of such a path has not been demonstrated.

**Finding PUBVIS-03 — OPEN / CRITICAL DESIGN DEPENDENCY:** the first Codec Lifecycle::Published store is irreversible absent a separately proven rollback protocol. No native terminal-on-unknown receipt, reliable exception boundary, or safe retry after unknown state exists in the reviewed integration. The earlier test-only terminal candidate does not constitute native adoption.

**Finding PUBVIS-04 — OPEN / HIGH:** the shared ActiveSnapshot pointer has a two-step lifetime transfer (s_active store inside callback, unique_ptr.release after callback returns). The exact source has no explicit throw statement in this final interval; nevertheless any future exceptional exit must preserve pointer ownership and process-lifetime object validity. No empirical dangling pointer failure is claimed.

**Finding PUBVIS-05 — NOT COVERED:** live VM visibility epoch, GC/Class lifetime, concurrent readers, reverse lock edges, shutdown CloseAndDrain progress, 32-bit ABI, product-native activation, real Unity/IL2CPP Player, V1 fields 14/15, native V2/receipt/readback/first recovery and historical independent full-stage acceptance.

## 5. Required decision before native production modification

The next *separate* production change should only proceed after explicit architecture/human review of:
1. The exact pre-codec vs codec-attempted vs post-group vs post-active failure classification, with terminal/restart state on any unknown outcome.
2. A scope-owned native UsageLock lease that survives exceptions without altering lock ordering, and symmetric cleanup for registry writes, **without** treating successful lease release as a rollback.
3. The ActiveSnapshot lifetime transfer and process-lifetime ownership when the callback succeeds, fails normally, or exits exceptionally; a method to prove the terminal state and first-error receipt remain durable.
4. Negative fault injection at each phase and a fresh authorized Local Validation build/Player evidence matrix, with unchanged original V1/B1 and rollback admission restrictions.

**The present task is a source-only verification checkpoint, not authorization to implement those changes.** B2 remains inactive: combined 128 TypeDefs, 64-byte declaration names, 65,536 indexed owner lookups; original V1/B1/R02, active resolver, exact source roster and PureInterpreter switch unchanged. WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false. No H2/M08A/X02/SNAP-01, consumed Local replay, or self-approved Human Review Gate.
