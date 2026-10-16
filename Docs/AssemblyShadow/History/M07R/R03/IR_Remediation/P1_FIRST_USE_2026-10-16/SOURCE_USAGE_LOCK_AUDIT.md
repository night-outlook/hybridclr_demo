# P1 bounded first-use capture — source and lock/lifetime audit

**Owner:** Primary Implementation. **Review date:** 2026-10-16 UTC (2026-10-15 Pacific). **Status:** Additive native source method, PassedWithinHostScope only. **Not** complete P1, Unity SDK/Player validation or R03 acceptance.

## 1. Exact source and unchanged production behavior

Working branch: codex/assembly-shadow-r01b-h1. Native implementation and qualifying CI source commit: **night-outlook/il2cpp_plus@1d66565855e729bedeaf93ed24078e9a6dbc83ed**. Previous native base: **339a49b5f1eb18c7cef9390c73ee6b64b0e6a36d**.

New files:
- libil2cpp/vm/AssemblyShadowBoundedFirstUseCapture.h — preallocated, noncopyable staged capture of first-use records.
- tools/r03/diagnostic_stream/bounded_first_use_fixture.cpp — host fixture with explicit CandidateRegistry and UsageLock models.
- tools/r03/diagnostic_stream/run_bounded_first_use.py — extracts and compiles the exact real native method; records provenance and raw commands.
- .github/workflows/r03-p1-bounded-first-use.yml — macOS Apple Clang and Linux Clang/GCC matrix, strict and ASan/UBSan.

Two existing native files receive additive changes: enabled AssemblyShadow.h declares TryCaptureBoundedFirstUses; enabled AssemblyShadow.cpp defines it. By direct GitHub Connector readback, the complete original GetDiagnosticsJson, GetExecutionDiagnosticsJson, TryCaptureBoundedTransactionStatus and TryCaptureBoundedTransactionInventory C++ method bodies are **byte-for-byte unchanged** from the previous native base. No original getters, Player native/C# emitter, report policy, semantic verifier or native engine lifecycle adapter invokes this new method.

## 2. Existing producer data and lifetime facts

The actual source has CandidateRegistry entries, each with Candidate.name and a single UseRecord firstUse. Each UseRecord contains present, kind, char detail[160], const Il2CppClass* klass, thread, timestamp and sequence. RecordBaselineUse, AssertMethodIsActive and CapturedArgumentVisitor publish the first first-use observation under the existing UsageLock and increment the plain s_usageGeneration counter under that lock. Subsequent first-use attempts do not overwrite a present first-use record.

CandidateRegistry is process-retained and published through s_candidates after configuration/initialization, using release/acquire pointer publication. The current source does not show a registry free/replacement on successful runtime execution, but **future VM shutdown and native metadata lifetime are not proven** merely by retained registry ownership. Immutable Candidate.name can be copied after releasing UsageLock while the exact registry pointer remains unchanged, with the existing process-retention contract.

Original GetDiagnosticsJson allocates a std::vector of UseRecord copies under UsageLock and, after unlocking, builds strings from Candidate.name, the original detail, sequence and potentially dereferences use.klass to obtain namespace/name. That last dereference needs an independent Il2CppClass metadata lifetime guarantee and is **not adopted** by the new capture.

## 3. New lock and ownership boundary

1. The caller must construct the roughly 2MiB bounded capture while healthy and own it on one thread. Exact caps: **4096 candidate slots, 1048576 bytes of copied name/detail/type text, and 160 bytes per raw detail**. These are fail-closed source caps, NOT authorization to truncate, cap engine reporting or exclude original candidate rows.
2. The native method loads the published CandidateRegistry and calls Begin with the exact entry count. Under a **single existing UsageLock**, it copies raw UseRecord fields and all 160 detail bytes for every candidate into fixed source-owned capture slots; it reads s_usageGeneration under the same lock. No allocation, type resolution, metadata lock or Il2CppClass dereference occurs under this spinlock.
3. The method **releases UsageLock before** it copies immutable Candidate.name data and creates the exact original C-string detail plus literal FirstUseSequence numeric suffix in owned storage. Decimal uint64 conversion is fixed-buffer and locale-independent, including 0 and UINT64_MAX. Candidate slots with present=false remain absent, not synthetic baselineUses rows.
4. It enters UsageLock a **second, short time** solely to sample the plain s_usageGeneration. The Capture seals only if this matches the generation copied in phase 1 and the registry identity remains unchanged. A witnessed first-use publication or registry change invalidates the entire capture. These checks do not prove a global VM epoch, exclude a theoretical sequence ABA/wrap, or guarantee the safety of metadata from independent threads.
5. All variable string data is copied immediately. A malformed char detail[160] without a terminator, invalid/overlapping input, changed source generation, wrong stage/order or any capacity breach poisons the capture. The public owned row accessor refuses all calls until a complete successful Seal. It exposes rows in exact candidate source order, omitting only genuinely absent first-use entries.

**Class lifetime gate (critical):** The source copies UseRecord.klass **only as an opaque identity token**, without reading namespace/name/type, even under UsageLock. The live native method NEVER invokes ResolvePhysicalClass and therefore **rejects sealing any class-bearing record** with UnverifiedClassMetadata. It does not substitute an empty type, fabricate a type key, dereference a freed class, or turn an incomplete record into a PASS. The standalone component exposes PendingOpaqueClass/ResolvePhysicalClass for a future **separately approved and source/lifetime-proven** metadata resolver. The token comparison does not independently authenticate the supplied type bytes; the existing live adapter is deliberately not wired to that optional API.

## 4. Exact V1 field behavior and source limitations

For a class-free first use, the owned Row reproduces the original name, BaselineUseKind, detail with **space + FirstUseSequence= + full decimal sequence**, type="" and thread/timestamp. C-style detail stops at its first embedded NUL as the original std::string(use.detail) does; candidate name uses the complete std::string bytes, including embedded NUL, as the original producer did. A future verified physical type resolver must emit the original namespace + "." + name exactly, including the dot when namespace is empty, without metadata cache side effects or class instantiation.

Capture correctness is limited to **one UsageLock-protected first-use subset**. The native method does NOT correlate these fields atomically with transaction closure, physical assembly generations, ordinary class listing, execution type keys, R02 counters, GC/finalizer or scheduler callbacks. Source data may change between lock scopes; the generation/pointer checks conservatively detect observed changes without a universal snapshot protocol. Worst-case UsageLock hold time for up to 4096 raw copies, spin contention, effect on user code and exact VM peak RSS/GC are unmeasured.

The class-bearing refusal means this is **not a complete real general diagnostics producer** for the likely game workload; class metadata lifetime/owner remains an explicit P1 prerequisite, not a delegated Local implementation task.

## 5. CI/source evidence and limitations

The host runner mechanically extracts the exact current production TryCaptureBoundedFirstUses body, pins its expected short-lock/generation/no-class-dereference structure and compiles it against explicit C++ CandidateRegistry, UseRecord, UsageLock and atomic mocks. The same build links the real current AssemblyShadowDiagnostics.cpp and checks full synthetic general V1 JSON composed from the actual captured first-use rows plus **mocked other VM fields**.

[Final source-bound CI 38839990454](https://github.com/night-outlook/il2cpp_plus/actions/runs/38839990454) is SUCCESS across Apple Clang/macOS15 and Clang/GCC Linux24.04, each with strict C++17 and ASan/UBSan. Test cases cover 4096 exactly accepted, 4097 rejected, no-class source deep-copy after mutation, exact max sequence value, absent candidates, first-use generation/registry change, malformed non-NUL detail, nullptr Candidate, text overflow, premature Seal/order, capture self-alias, valid immediately adjacent input, class-bearing live source refusal, mismatch opaque token, and standalone **synthetic-only** future metadata resolution. Synthetic complete general V1 parity is **980 bytes** for class-free records.

Production first-use method SHA-256: **c3626338497a16466c3f358f3771eb663fc211b94d6bd5ee6223364763bf4a2b**. Three original GitHub Actions ZIP artifacts were downloaded and independently checked: **57/57 manifest-declared regular files matched SHA-256 and byte length, with no missing/mismatched/unlisted entries**. [EVIDENCE.json](EVIDENCE.json) records archive hashes, source pins, commands and limitations. Existing [general serializer/V2 interop CI 38839990408](https://github.com/night-outlook/il2cpp_plus/actions/runs/38839990408) separately PASSed 3/3 jobs at the same native source pin.

Host source mocks do not constitute an official installed Unity2022.3.62f2 StandaloneOSX compiler, Player, actual metadata/class lifetime, terminal native scheduler owner/GC/finalizer servicing, memory/RSS bound, V2 file transaction or R03 acceptance. Mac LeakSanitizer coverage remains unavailable. Other historical R02/terminal-policy CI source assertions are not reclassified by this work.

## 6. Next substantive Primary implementation gate

- Obtain and review source-supported Il2CppClass/Il2CppImage metadata lifetime and approved g_MetadataLock ownership before implementing a real physical first-use class-name resolver. Never acquire g_MetadataLock **inside** UsageLock (would violate original transaction→metadata→assembly→usage/cache rank), and never dereference class handles outside a proved lifetime ticket.
- Extend bounded, separately versioned physical assembly and ordinary class enumeration without allocating/retaining unproved Il2CppClass pointers after metadata-lock release; preserve every source field and honest count/dropped coverage.
- Implement bounded, exact physical metadata-owner mapping and FormatMetadataOnly replacement covering nested/generic/array/qualifiers and original UTF16 assembly-name folding; reject capacity/type-owner mismatch instead of changing keys.
- Integrate only then the existing transaction inventory, first-use, general/execution/R02 owned captures into authentic complete field14/15 transport. P2 native/C# V2 semantic verifier remains NotIntegrated; E0/E1 real supported Unity engine owner/finalizer/restart remains Blocked; P3 official managed+55-native SDK compile/Player remains NotRun.

**Stop/acceptance:** WEB_TO_LOCAL remains PAUSED; last Local host PASS remains consumed at DEMO 7b9d1d4e37d1731f9f00042eb04892a8afaf7e80 and NATIVE 74dbdbea80d83923863303bd2b2c0a87f36541b1. Original SNAP-01 FAIL/ReturnRequired 14Passed/4Failed with ON slot14 scanned prefix262145 above V1 limit262144 (full actual size Unavailable); engine51213 uncapped reports in500ms exit71; N/M/K/I/E FAIL and historical S custody Blocked. R03Accepted, H2Passed, qualificationApproved, ReadyForHumanReviewGate and fullLegacyRegressionAcceptance remain false; PureInterpreter expansion disabled; no H2/X02/M08A.
