# P1 owned ordinary class capture — Primary reconciliation

**Owner:** Primary Implementation. **Date:** 2026-10-16 UTC. **Disposition:** additive bounded class-row reader, verified **PassedWithinHostScope**, NOT complete P1 or runtime acceptance. **Local Validation remains PAUSED.**

## 1. Exact source and previous authority

All four repositories use codex/assembly-shadow-r01b-h1.

| Repository | Authority |
| --- | --- |
| night-outlook/il2cpp_plus | **2db707eb3021516c2cef962b3d294b4d047e4ef9** — final bounded ordinary-class source, corrected legacy interpreter-image predicate, private-image publication guard, tests/CI |
| night-outlook/hybridclr_demo | New Primary documentation only; final pushed demo HEAD must be verified separately from the CI source SHA |
| night-outlook/hybridclr | **4b2774b066cfc6afd77a8c8aded6bda7ea574f55**, unchanged |
| night-outlook/hybridclr_unity | **948c0e3b4f8891481301770115e8ba4945eea6de**, unchanged |

Base native source was fba5b62148076943ba689b40333894f0edd3c7df. GitHub Connector verified the new changes are limited to AssemblyShadowBoundedOrdinaryClasses.h, an additive AssemblyShadowVisibility.h declaration, additive AssemblyShadowVisibility.cpp callback/method, source-bound test/runner and workflow. The original AssemblyShadowVisibility::CollectOrdinaryClasses body remains **byte-for-byte unchanged**. GetDiagnosticsJson, GetExecutionDiagnosticsJson, the terminal behavior, Player/C#, V1 original semantic verifier and other previously published P1 collectors are unchanged.

The **last actual Local-host-executed** pair remains demo 7b9d1d4e37d1731f9f00042eb04892a8afaf7e80 and native 74dbdbea80d83923863303bd2b2c0a87f36541b1, plus unchanged HybridCLR/package commits. Demo Tools/AssemblyShadow/R03/source-pins.json intentionally remains bound to those execution sources; it MUST NOT be promoted to this new CI-only native source. The original Local host PASS and earlier FAIL are separately immutable and consumed.

## 2. Implemented native source

**New libil2cpp/vm/AssemblyShadowBoundedOrdinaryClasses.h:** a caller-preallocated, one-shot, noncopyable owned capture, with **8192 complete class rows** and **2,097,152 copied assembly/type-name bytes**. Each row retains only offsets, lengths and the three original boolean fields: isInterpreter, isConstructedGeneric and usesStagedMetadata. It immediately composes namespace + '.' + class name for a nonempty namespace (no leading dot when absent). No Il2CppClass, Il2CppImage or borrowed name pointer survives in a complete record. An invalid stage, source null/overlap, source overflow or observed generation/visibility change poisons the result without a truncated PASS or accepted prefix.

**New AssemblyShadowVisibility::TryCaptureBoundedOrdinaryClasses:** an **inactive** parallel native path that takes the existing g_MetadataLock, samples ActiveGeneration and the private-image list head, calls the same il2cpp_class_for_each traversal as CollectOrdinaryClasses and copies all original V1 fields synchronously through CaptureOwnedOrdinaryClass, before releasing the lock. It rejects a witnessed active-generation or visibility-head publication change. It neither creates a class-pointer vector nor retains class handles. The original collector remains intact and is still used by the real getter.

**Critical correctness fix during implementation:** the original getter derives class isInterpreter from Interpreter(klass->image->assembly), i.e. the physical **assembly's image**, not necessarily klass->image. The initial new callback used the class image; Primary corrected it to klass->image->assembly->image and added explicit invalid physical-image rejection. The host fixture now deliberately disagrees the two image flags and asserts the original predicate. No test or field was weakened to hide the discrepancy.

The new callback also calls original ClassUsesStagedMetadata while holding the metadata lock. Source validation cannot assert its recursive traversal has a bounded call stack or lock hold duration. The upstream il2cpp_class_for_each delegates to MemoryInformation::ReportIL2CppClasses; that traversal can use allocating assembly snapshots and multiple metadata registries. The new fixed row writer **does not make upstream class enumeration allocation-free**, even if the output writer itself avoids heap expansion.

## 3. CI and raw artifact verification

[Final source-bound CI 38845581521](https://github.com/night-outlook/il2cpp_plus/actions/runs/38845581521) is **SUCCESS, all three jobs** at final native source 2db707eb3021516c2cef962b3d294b4d047e4ef9: macOS15 Apple Clang, Ubuntu24.04 Clang and Ubuntu24.04 GCC; each executed strict C++17 and ASan/UBSan with -Wall/-Wextra/-Werror/-pedantic.

The runner compiles the **actual new production C++ callback AND method bodies**, extracted without rewriting, against explicit native class/image/metadata-lock/visible-class mocks. It independently compiles the frozen original general serializer at Git blob **226b01273d3e30d190422c4c4c740c49a8d957f0**, links current production general serialization, and constructs a staged frozen general JSON from those actual source-callback rows. All three outputs must match complete bytes.

Tested: 0, 6, 8192 and 8193 class enumerations; identical physical order; namespace formatting with null/empty/Unicode; embedded control characters; generic/staged flags; interpreter kind from the correct physical assembly image even when the class image disagrees; exclusion of invisible/uninitialized **fixture** types; name mutation after ownership transfer; missing native class/image/assembly/physical-image/name; too-large buffer; invalid stage, alias and adjacent input; active-generation and private-image head changes. The 8192-class host specimen matched all **1,403,463 bytes** across immutable original/current/frozen general JSON. Other VM fields in that specimen are **MOCKED**. It does not indicate the true real ON Player slot14 length.

Primary downloaded the three original qualifying CI ZIPs using GitHub Connector and independently verified all **84/84 manifest-declared regular files**, their actual byte lengths, SHA-256 hashes, source preservation and all 18 compile/execute stderr/stdout receipts; no missing, mismatched or unlisted files. Complete method SHA-256 **0b5ba5bdd6d77d751c3cb90bf5aad8d301c2b4502a630072fd1912a51a518a24**, callback SHA-256 **0c908fd16e253a6cd597a2cf0edd9ae64750ef70ac94773225e65707ec77f8a7**. [EVIDENCE.json](EVIDENCE.json) retains archive IDs/hashes and negative capability.

Exploratory runs with stale source-bound checks or the initial incorrect class-image predicate remain failed historical runs. **Only CI 38845581521 qualifies the final native code.** This is not a repository-wide CI claim; older unrelated R02 and terminal-policy CI gates are still not qualified by this increment.

## 4. Exact lifetime limitation

[SOURCE_LIFETIME_AUDIT.md](SOURCE_LIFETIME_AUDIT.md) independently examines Runtime.cpp, MetadataCache.cpp, MetadataAlloc.cpp, MemoryInformation.cpp and visibility recursion. Runtime::Shutdown may reclaim image/assembly metadata and unconditionally deletes metadata pools. The source does **not** establish that g_MetadataLock is acquired by all shutdown cleanup paths, so a held metadata lock is NOT a sufficient lifetime lease against metadata reclamation. The true supported Unity2022.3.62f2 StandaloneOSX engine owner, callback drain, GC/finalizer continuation and restart protocol remain E0/E1 Blocked.

Therefore this is **inactive additive code, not terminal-time safe capture**. The real GetDiagnosticsJson still has its old dynamic class pointer vector and no new Player integration. The first-use UseRecord.klass stays opaque and cannot be resolved using this new reader without independent metadata-lifetime proof. No actual native SDK compile, real shutdown concurrency test, lock duration/RSS/GC measurement or real Unity Player run was performed.

## 5. Next Primary work and stop

The earliest substantive Primary prerequisite is a **source-backed metadata lifetime reader-admission / teardown quiescence contract** that coordinates with Runtime::Shutdown, its native metadata pools and the actual engine owner. An arbitrary flag check, mock admission receipt or unmanaged terminal callback is not sufficient. After that, qualify complete no-allocation class enumeration, recursive visibility/lock hold bounds, safe first-use class-name resolution outside UsageLock, exact physical metadata owner/type-key formatting and coherent/versioned complete field14/15 source acquisition. Only then wire authenticated native/C# V2 Player transport and unchanged original semantic predicates (P2), with E0/E1 lifecycle and P3 official SDK/Player validation prerequisites.

**Immutable status:** SNAP-01 stays FAIL/ReturnRequired: 18 cells, 14 Passed/4 Failed; original slot14 observed prefix262145 exceeded original V1 262144 bound, actual complete length Unavailable; engine 51213 uncapped reports/500ms and exit71. Historical N/M/K/I/E remain FAIL, original S custody Blocked (416844 expected/339367 survivors/77477 missing, four native roots missing), and independent full-stage R03 review FAIL/re-review NotRun. All R03Accepted, H2Passed, qualificationApproved, ReadyForHumanReviewGate, fullLegacyRegressionAcceptance flags false; PureInterpreter disabled.

**WEB_TO_LOCAL PAUSED:** no new Local host/Unity native SDK/Player run, no new Player root, no H2/X02/M08A or automatic Human Review Gate is authorized.
