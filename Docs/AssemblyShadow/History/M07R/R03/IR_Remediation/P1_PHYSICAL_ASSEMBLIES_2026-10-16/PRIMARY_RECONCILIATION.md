# P1 physical assembly source capture — Primary Implementation reconciliation

**Owner:** Primary Implementation. **Date:** 2026-10-16 UTC. **Disposition:** Inactive additive native source, PassedWithinHostScope only. P1 still Incomplete; no Local Validation authorized.

## 1. Source commits and provenance

All four repositories use branch codex/assembly-shadow-r01b-h1. Native source increment: **night-outlook/il2cpp_plus@fba5b62148076943ba689b40333894f0edd3c7df**, based on prior first-use native **1d66565855e729bedeaf93ed24078e9a6dbc83ed**. Unchanged HybridCLR and package pins are **4b2774b066cfc6afd77a8c8aded6bda7ea574f55** and **948c0e3b4f8891481301770115e8ba4945eea6de**. The final demo source of this review is a documentation publication only and must be verified separately from the remote branch HEAD.

The last **actual Local host-executed source tuple** is demo **7b9d1d4e37d1731f9f00042eb04892a8afaf7e80** and native **74dbdbea80d83923863303bd2b2c0a87f36541b1**, plus unchanged HybridCLR/package pins. Demo Tools/AssemblyShadow/R03/source-pins.json intentionally retains those execution SHAs; this newly written CI-only native code has NOT run in the installed Unity environment. Previous Local host successor PASS and older FAIL remain distinct consumed historical evidence.

GitHub Connector compared native code changes: only new bounded physical assembly header, additive Assembly.h declaration, additive Assembly.cpp source reader, test fixture/runner and CI. The **complete original Assembly::CaptureShadowEnumeration** method body is byte-for-byte unchanged; the existing AssemblyShadow::GetDiagnosticsJson, GetExecutionDiagnosticsJson, first-use, transaction-status and inventory producers are not modified in this increment. No Player/C# or semantic validator calls the new source method.

## 2. Implemented code and owned contract

- **libil2cpp/vm/AssemblyShadowBoundedPhysicalAssemblies.h:** fixed, one-use, nonmovable Capture with **4096 physical assembly slots** and **1,048,576 owned name bytes**. It stores exact name bytes/length, physical interpreter bool and the separately sampled physical enumeration generation. No borrowed source pointer survives in a complete result; Get requires successful Seal.
- **Assembly::TryCaptureBoundedPhysicalAssemblies:** a new inactive source reader under the original **s_assemblyLock**. It walks the original s_Assemblies registry and uses exactly the existing CopyValidAssemblies token!=0 inclusion rule, preserving the physical registration order and duplicate physical names/identities without logical name resolution. It derives isInterpreter from the existing IsInterpreterImage predicate already used by GetLoadedAssemblyPhysical under the same registry lock, then synchronously copies the name into owned storage.
- The method samples AssemblyShadow::ActiveGeneration before and after traversal under the same s_assemblyLock; any witnessed change invalidates the entire capture. This is **only an observed-change guard and the original independent physical enumeration generation**, not proof of one cross-transaction/metadata/usage/R02 epoch.
- Null/corrupt assembly/image/name, too many entries, overlong strings, input aliasing, illegal phase/reuse or changed source generation fail closed. Neither a short prefix nor count can be treated as complete. This does not reduce the original record counts or impose report caps.
- The source reader does not create AssemblyVector copies, allocate containers, dereference Il2CppClass, invoke VM type formatting, call a metadata/cache lock, perform file I/O or call managed code within the short source path. However, up to 1MiB of copied names under s_assemblyLock may still cause significant contention; actual lock latency/GC/RSS have NOT been measured.

**Important lifecycle limitation:** MetadataCache::Clear can release physical image/assembly tables and MetadataAllocCleanup deletes metadata pools during Runtime::Shutdown, while no source-backed owner/quiescence barrier between cleanup and this reader has been established. An s_assemblyLock reader is not automatically safe against metadata pool cleanup. This component remains **inactive** until native engine-owner/teardown contracts are established. Read [SOURCE_LIFETIME_AUDIT.md](SOURCE_LIFETIME_AUDIT.md) for exact source and lock/cleanup evidence.

## 3. Host test and artifact evidence

[CI 38842846530](https://github.com/night-outlook/il2cpp_plus/actions/runs/38842846530) **completed SUCCESS at native fba5b62148076943ba689b40333894f0edd3c7df, all 3 jobs**: macOS15 Apple Clang, Linux Clang and Linux GCC, each strict C++17 and ASan/UBSan. The host runner compiles the **exact current production Assembly::TryCaptureBoundedPhysicalAssemblies body** under explicit physical registry/mutex/generation mocks, not a substitute rewritten formatter.

Tests covered 0/4/4096/4097 physical rows, exact token filtering/order/duplicate physical names/interpreter flag, source string mutation after capture, seen generation change, all null/overlimit/stage/alias negatives and separate adjacent name acceptance. Prepared-path operator-new accounting observed no dynamic allocation from the capture and source method; this excludes actual IL2CPP metadata, native malloc, RSS, OS locks and GC. The 4096-name sample contains more than the legacy V1 individual text limit, but is synthetic input.

The fixture additionally compiled the independently pinned **immutable original general V1 serializer** at Git blob **226b01273d3e30d190422c4c4c740c49a8d957f0**, linked the actual current product serializer and composed the captured physical rows into the inactive frozen general builder. It requires complete **three-way identical 411,154-byte JSON**. All non-physical VM domains in that sample are explicitly MOCKED. This shows formatting/ordering compatibility only; it is not an actual SNAP-01 slot14 payload or type/class owner proof.

Three original GitHub Actions artifact ZIPs were downloaded through the GitHub Connector and audited independently. **81 of 81 manifest-declared regular files** matched byte lengths and SHA-256, no missing/mismatched/unlisted; strict/sanitized runs and all six compiler/execute receipts per platform Passed, source files were unchanged. Actual native reader method SHA-256 **fc88097a67c3a93a00b0f0150b09531074c11f77f5f9e6bd4aa5af1ba274a3da**; old physical reader SHA-256 **bec8878dda2755b5f48c49f16dd87de27cff8b3a189689679a3c6dbdb3afa540**. [EVIDENCE.json](EVIDENCE.json) includes exact artifact ZIP hashes, ids and limits.

This evidence is **host-source-with-mocks**, not official Unity2022.3.62f2 StandaloneOSX native/managed SDK compilation, actual VM/Player, terminal safe point, original semantic verifier or R03 acceptance.

## 4. Earliest unfinished Primary work and stopping conditions

**P1 still Incomplete.** The new physical assembly sub-snapshot does not address the unsafe original GetDiagnosticsJson class pointer vector or first-use Il2CppClass token, dynamic execution MetadataTypeImages, recursive FormatMetadataOnly, R02 atomic epoch, or comprehensive complete diagnostic field14/15 capture. Source shutdown cleanup is not coordinated with this reader.

Next Primary work in dependency order:
1. Find/prove the real Unity/IL2CPP metadata lifecycle and native shutdown admission/owner synchronization, class/image name lifetime, and acceptable lock hold budgets. The source review identifies MetadataAllocCleanup/MetadataCache::Clear as concrete missing ownership proof; do NOT infer a lifetime ticket solely from g_MetadataLock or Runtime::IsShuttingDown.
2. Implement actual bounded ordinary-class source enumeration and class-bearing first-use name resolution **only under the proven owner/lifetime protocol**, no metadata dereference after unlock and no g_MetadataLock inside UsageLock.
3. Complete fixed-budget physical metadata owner mapping and exact recursive type-key production with original byte parity. Measure full P1 lock/GC/RSS/allocator peaks and coherent or explicitly independent snapshot generations.
4. Only then P2: complete authenticated native/C# V2 field14/15 + every unchanged semantic predicate, preserving historical V1. E0/E1 supported engine owner, native finalizer/GC/service continuation and restart remain Blocked/NotProven. P3 official installed managed/55-native SDK compilation and real Player remain NotRun.

**Stop/custody:** SNAP-01 remains FAIL/ReturnRequired, 18 cells 14Passed/4Failed; real ON field14 scanned prefix262145 exceeds V1 262144 and exact complete source lengths are Unavailable; engine 51213 uncapped reports in 500ms, exit71. Historical N/M/K/I/E FAIL, strict original S custody Blocked (416844 expected/339367 survivors/77477 missing, four missing native roots), independent R03 full-stage FAIL/re-review NotRun. No code truncation, output cap, native-report coalescing, early exit, GC/finalizer suppression or semantic predicate relaxation.

R03Accepted=false, H2Passed=false, qualificationApproved=false, ReadyForHumanReviewGate=false, fullLegacyRegressionAcceptance=false; PureInterpreter expansion disabled. **WEB_TO_LOCAL PAUSED, no new Local Validation command, no Unity/Player SDK run or Human Review Gate, and no H2/X02/M08A.**
