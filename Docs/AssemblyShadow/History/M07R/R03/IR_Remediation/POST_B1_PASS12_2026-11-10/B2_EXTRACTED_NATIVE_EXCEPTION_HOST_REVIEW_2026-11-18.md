# R03 B2 — Exact native registry publisher host: injected exceptional-exit evidence

**Date:** 2026-11-18 UTC  
**Branch:** codex/assembly-shadow-r01b-h1 across all four repositories  
**Checkpoint:** bounded Primary Implementation, pre-integration only; NOT native/Unity production acceptance, and NOT Human Review Gate approval.

## 1. Objective and authoritative inputs

Previous R03 B2 source work authenticated the normal-false registry rollback and real Codec/Runtime/Bridge publication ordering, but had not **executed** the native registry and cross-callback UsageLock bodies on an exceptional path. This checkpoint reproduces one *synthetically injected* throw while compiling the **literal C++ bodies** from the exact pinned native fork, without changing the fork. The goal is to distinguish exception unwind of RAII mutex guards from cleanup of the two registry vectors and manually acquired UsageLock.

The fixed production tuple remains:

| Repository | Pinned commit |
| --- | --- |
| night-outlook/hybridclr_demo | new tested code = fd60c453781ddf79a5087d7e4db150a1ae690d7b |
| night-outlook/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | cecf4b859d50b128e5c0fc6c90cd89e3a452b96a |

The test checks **three native Git blobs** from il2cpp_plus, both by actual checkout HEAD and by tree/on-disk blob identity:

| Native file | Git blob |
| --- | --- |
| libil2cpp/vm/Assembly.cpp | df1acbfdaf054067720d2e7c1545e49100ad93ec |
| libil2cpp/vm/MetadataCache.cpp | b9a9881c6e6a551c19069446a9be61c21f4c8584 |
| libil2cpp/vm/AssemblyShadow.cpp | dc941907884b9a7f44ade6085d05f2e4a1a96d9e |

The generator extracts **eleven unchanged C++ definitions**: the native assembly batch publisher, metadata context and callbacks, metadata batch publisher, native LockUsage/UnlockUsage and UsedClosureMember, native Publication record, and TryBeginPublication/PublishActive. Generated source SHA-256 in all four CI jobs was **9c6a27315f0fecefb52b7c80c838ef4d870dbf7e1184be8e0d21402c26aa5b8c**.

The generator does not parse production source with compiler fidelity and its brace matching is intentionally narrow, but it does authenticate exact original Git objects and copies body bytes *without modifying any expression*. Only surrounding namespace wrappers and a host scaffold are introduced. Any future source change requires re-review and explicit pin updates.

## 2. Bounded design and implementation plan

1. Add NativeRegistryExceptionalHost.cpp outside Unity/native build rosters. Define minimal host-only stand-ins for Il2CppAssembly, CLI dynamic array, mutex guards, Candidate/Transaction and InterpreterAssembly batch callback. Do not construct actual Il2Cpp VM objects or call the real Codec/Runtime.
2. Add extract_native_registry_publication.py to verify the three exact blobs, select eleven uniquely anchored original definitions and generate a temporary NativeRegistryExactBodies.inc, plus machine-readable source receipt. The original function bodies are left unchanged.
3. Add test_extract_native_registry_publication.py with ten required real-checkout tests: source inventory, literal-body shape, duplicate/missing anchors and malformed extract inputs. No synthetic passing fallback or skipped production-source checks.
4. Add a CI matrix for Ubuntu 24.04 + macOS 15 × C++11/C++17, each executing optimized strict compilation and an ASan/UBSan profile. Check both generated-source receipt and host outcome JSON.
5. Inspect complete job logs before publication. Publish evidence and a separate production correction plan; preserve Local Validation closure and stop before touching native runtime.

Files delivered in hybridclr_demo:

- Tools/AssemblyShadow/R03IR/TypeDefCensus/NativeRegistryExceptionalHost.cpp
- Tools/AssemblyShadow/R03IR/TypeDefCensus/extract_native_registry_publication.py
- Tools/AssemblyShadow/R03IR/TypeDefCensus/test_extract_native_registry_publication.py
- .github/workflows/r03-b2-native-registry-exception-host.yml

No source file in hybridclr, hybridclr_unity or il2cpp_plus was changed.

## 3. Directly executed scenario matrix

Each compiled host profile runs **4 scenarios / 44 checks**:

| Scenario | Actual pinned native result within mock host |
| --- | --- |
| Used closure detected by TryBeginPublication | Returns false before registry append; native UsageLock released; both registries unchanged |
| InterpreterAssembly::PublishStagedImagesBatch returns false | PublishActive returns false and releases UsageLock; both registry rollback branches execute; s_active remains null |
| Staged publication returns success | Physical and CLI registries contain two members; s_active points to test-owned snapshot; native UsageLock released |
| **Injected C++ exception** inside mocked PublishStagedImagesBatch | **C++ exception escapes PublishActive; both registry vectors retain appended members, UsageLock stays held; RAII metadata/assembly mutexes unwind; s_active remains null** |

The host explicitly observes the retained entries, metadata/physical mutex depth returning to zero, the manual atomic flag still held, absence of active snapshot and absence of staged->published transition. It performs **test-owned reset** of those structures after the throw to avoid polluting the host process; this reset is **not a native rollback, permission to retry, or evidence of recoverability**.

The synthetic injection occurs at a single, deliberately modeled runtime callback. No real Unity heap, metadata parser, Codec/Runtime transaction, IL2CPP Player, GC synchronization or actual exception producer was invoked. Real native lock identity and ownership are replaced by std::mutex and scoped guards that match the source call pattern. The output proves the behavior of the extracted bodies under these stand-ins and **does not prove that this exception can occur in an installed Unity runtime**.

## 4. Exact CI and provenance

[Exact-code GitHub Actions run 44230604848](https://github.com/night-outlook/hybridclr_demo/actions/runs/44230604848) was read back through the GitHub Connector. **4/4 jobs completed/success**:

- Ubuntu 24.04, C++11 — 10 Python extraction tests passed; strict and sanitizer C++ host passed, 4 scenarios/44 assertions each
- Ubuntu 24.04, C++17 — same results
- macOS 15, C++11 — same results
- macOS 15, C++17 — same results

Each job emitted two host JSON receipts, **8 host receipts total**, all with actualNativeSourceBodiesCompiled=true, mockNativeDependencies=true, injectedCallbackException=true and all Unity, real Codec, safeRecovery, nativeProductionChanged, R03Accepted, H2Passed and ReadyForHumanReviewGate flags false.

This was a **first-try successful run**; no intermediate failed version of this particular workflow is being promoted or concealed.

## 5. Primary review findings

**NRX-01 — HOST-REPRODUCED, high importance.** Native bodies execute normal bool-false rollback correctly in the mock but do **not** execute physical/CLI vector rollback when PublishStagedImagesBatch throws. Both source callbacks implement rollback only in their bool-false branches. This is now compiled fault-path evidence at pinned source (with mocks), not only lexical inference.

**NRX-02 — HOST-REPRODUCED, high importance.** Native TryBeginPublication keeps UsageLock held across callback return. When a mocked deep callback throws, the extracted native code does not call UnlockUsage. The test-owned atomic flag remains held while both RAII mutex guards unwind. This is the precise exceptional-exit custody gap; whether a production runtime can throw there is still NotRun.

**NRX-03 — NOT PROVEN, critical design dependency.** The host faults *before* actual Codec PublishBatch execution. It does not test or establish recoverability when a Codec Lifecycle::Published store, Runtime group active store, or native s_active store may already have occurred. Any **unknown** outcome after codec attempt must be classified Terminal/Restart Required rather than treated as retryable precommit rejection without separate proof.

**NRX-04 — NOT PROVEN, high importance.** ActiveSnapshot lifetime still crosses a two-stage ownership boundary: native s_active release-store occurs inside PublishActive while CommitTransaction's unique_ptr releases ownership only after the nested call returns. There was no injected throw between those two actual production operations in this host. No proof of dangling pointer or safe exit is claimed.

**NRX-05 — NOT RUN.** Source/compiler fidelity of the complete Unity TUs, true metadata mutex/VM lock graph, concurrent readers, GC/class allocation epoch, shutdown CloseAndDrain progress, native V2/readback/recovery, complete original V1 fields 14/15, 32-bit ABI, memory/resource budgets, three Players, original R03 full-stage evidence and independent Human Review.

## 6. Next bounded Primary step and decision gate

A *separately reviewed* native remediation design should use a phase-aware failure protocol, not a blanket catch-and-retry:

1. **Before codec attempt:** only a formally proved untouched/rollback-complete path may return an ordinary precommit rejection (possibly still Validated).
2. **Codec attempted / outcome unknown:** emit terminal/restart status, preserve first-error and monotonic irreversible state. Do not repeat a half-committed publication.
3. **Registry cleanup and UsageLock:** use exception-safe ownership of the transferred usage flag and both vector append scopes; registry shrinking on exception must never be misrepresented as Codec/VM rollback. Preserve the observed lock order.
4. **ActiveSnapshot:** transfer ownership to a process-lifetime holder before publishing a pointer, with no throwing operation between visibility and ownership transfer, and verify safe terminal behavior after attempted publication.
5. **Evidence:** stage-specific fault injections (before codec, after lifecycle, after group active, after native active), negative/positive host/Unity tests, exact source manifests, separate Local Validation authorization and independent review prior to acceptance.

**Explicit approval remains required before changing production native publication semantics.** This checkpoint is a host-only Primary result, not that approval.

B2 remains inactive with **128 combined TypeDefs / 64-byte declaration names / 65,536 indexed owner lookups**. Original V1/B1/R02, active resolver, source rosters and PureInterpreter activation remain unchanged. WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false. No H2/M08A/X02/SNAP-01, consumed Local replay or self-approved Human Review Gate.
