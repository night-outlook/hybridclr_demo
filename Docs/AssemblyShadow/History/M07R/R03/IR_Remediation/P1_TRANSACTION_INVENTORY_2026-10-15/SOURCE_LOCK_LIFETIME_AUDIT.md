# P1 source and lock audit — bounded transaction inventory (R03)

**Owner:** Primary Implementation. **Date:** 2026-10-15 UTC. **Scope:** real transaction-owned data capture only; not complete VM diagnostic acquisition, Unity scheduler safe-point, Player validation or Human Review Gate.

## 1. Source identities and exact diffs

- Canonical branch: codex/assembly-shadow-r01b-h1. Native authority: night-outlook/il2cpp_plus at 51c28cf535dc0dcd3294ec49bc6877064d22c75a, based on 10a6bece70ec4990dc795daa11b3f4a7629b7a61.
- New product source: libil2cpp/vm/AssemblyShadowBoundedTransactionInventory.h; additive declaration in AssemblyShadow.h; additive AssemblyShadow::TryCaptureBoundedTransactionInventory in AssemblyShadow.cpp.
- GitHub Connector independently compared the entire original GetDiagnosticsJson, GetExecutionDiagnosticsJson and TryCaptureBoundedTransactionStatus method bodies before and after: ALL THREE ARE BYTE-FOR-BYTE UNCHANGED. No original diagnostic getter, C#/Player, terminal guard, V1 writer, V2 file transaction or semantic verifier now calls the new method.

## 2. Exactly what one transaction mutex protects

The new method calls Current() and takes the existing std::lock_guard on transaction.mutex once. Inside that scope, it synchronously copies these fields into preallocated, owned storage:

| Source | Fields copied | Source capacity or caveat |
| --- | --- | --- |
| Transaction + s_state + first-error flags | State/error/detail/IDs/generation/closure expected and StagedCount/retained bytes | Embedded prior status component: detail 32768 bytes, baseline ID 8192, patch ID 8192 |
| Published StableAotConfiguration | Every stableNames string in order | At most 4096; source overage fails |
| Transaction.closure | All candidate names; staged MVID, skeleton, runtime-metadata, published, initializer attempted/ran flags in order | At most 4096; null candidate rejected; unstaged member preserves empty MVID/false flags |
| Transaction.commitOrder | Every committed name, original order | At most 4096; no clipping |
| Transaction.events | Sequence, kind, name, generation and stagedCount for every source event | At most 4096; the original Event() implementation already bounds its source vector, so it does NOT prove all attempted events were retained |
| Combined variable inventory text | Raw source bytes deep-copied synchronously | 1048576 bytes total; overflow fails closed |

The old getter collects the same transaction-owned fields but uses heap std::vector/std::string snapshots. The new inventory directly consumes const source references into a fixed text arena and fixed typed tables. It performs no dynamic container expansion or arbitrary formatter in this method. The output is inaccessible until the entire inventory and status have successfully sealed.

**Critical boundary:** the mutex protects transaction container structure and its strings. It does not prove all independently atomic staged initializer flags, external CandidateRegistry identities, class metadata, usage records, R02 counters or Unity engine callbacks refer to one global instant. Staged flags still use the same atomic loads as the original getter, potentially independently changing. Original candidate and staged-object retention must be proven separately in the real engine lifecycle.

## 3. Post-lock failure precedence and source instability

First-error inputs (s_typeFailure immutable first pointer, s_state, s_active, s_configuration, s_unexpectedFailure, s_lateBaselineUse) are sampled before and after the transaction portion. Under the mutex, unexpected failure overrides late baseline use, which overrides transaction.lastError/detail. After unlock, the stable first TypeFailure overrides the copied transaction status and selects Failed versus FailedAfterCommit using the native active snapshot. A witnessed change to checked source pointers/state/generation/flags causes SourceChanged and invalidates the complete inventory. No retry, synthetic epoch, accepted prefix or semantic PASS follows.

Equal atomic reads are **not a global generation protocol**. ABA transitions, unsampled class/usage/cache changes and independent staged initializer updates are not ruled out. This is one transaction mutex-consistent subset plus postlock first-failure precedence, not a complete R03 diagnostic snapshot.

## 4. Lock ordering, memory, failure and owner

- Existing bootstrap lock order: transaction → metadata → assembly → usage/cache. This method acquires ONLY the transaction mutex, and no metadata, assembly or usage spinlocks, VM type formatter, external file sink or managed callback under that mutex. No new source lock inversion is introduced in the method itself. However, worst-case hold time, writer starvation, reentrancy and terminal callback ownership are NOT measured/approved.
- Current() lazily creates the transaction singleton with a heap allocation on its first call. The caller must prove healthy-time initialization of Current() and preallocate the 1.4–1.6MiB Capture before using the method in a terminal callback. Host source-unit tests do not establish this.
- Memory includes a 1MiB text arena, 4096 stable spans, 4096 closure typed rows, 4096 commit spans, 4096 event typed rows and ~50KiB embedded status. The compile-time object-size budget is 1MiB + 600000 bytes. Production RSS/GC/heap plus the preexisting 3.9MiB general, 2MiB execution, type index and V2 transport budgets remain unmeasured and unapproved.
- A null candidate, invalid source, string overlap, missing field, array count overrun or text limit fails closed. The first error is retained. No truncation, count cap in reporting, or fallback to a partial valid record. The source's existing 4096-event retention limitation remains unchanged rather than being claimed as full event coverage.
- All read-only getters return owned spans/scalars only after Seal; pointers remain valid only for the lifetime of the Capture.

## 5. Verification and limits

Host runner mechanically extracts the **exact current production TryCaptureBoundedTransactionInventory C++ body** and compiles it under explicit mocks of Transaction, StagedAssembly, Candidate, StableAotConfiguration and native atomics. Strict and ASan/UBSan cover original field order, staged flags and empty rows, status/TypeFailure priority, source-string mutation after capture, invalid stage, copy overlap, valid adjacent input, source flips, and all row/text count limits. A synthetic 1705-byte complete general V1 record combines the captured actual-method transaction subset with MOCKED other VM fields, then matches current product AssemblyShadowDiagnostics::Serialize in full bytes. It does not exercise a Unity class table.

[Final CI run 38778487071](https://github.com/night-outlook/il2cpp_plus/actions/runs/38778487071): SUCCESS at native 51c28cf535dc0dcd3294ec49bc6877064d22c75a, all three jobs Apple Clang/macOS15, Clang/Linux and GCC/Linux, each strict and ASan/UBSan. The downloaded three original CI ZIPs were independently verified: all 57 manifest-declared regular files matched their sizes and SHA-256, no missing/mismatch/unlisted. Source-method SHA-256: aecef83b206047463c24a355487222a41117c9ba97eb4f0afb38615c2faad3d9. Exact ZIP hashes and artifact identities: EVIDENCE.json.

This CI is product-method source extraction under mocks, NOT installed Unity2022.3.62f2 StandaloneOSX native/managed compiler, real VM owner/metadata/GC/RSS evidence, native V2 Player integration or runtime acceptance. No full SNAP-01 slot14 length or new engine 500ms result exists.

## 6. Remaining P1 and next Primary gates

1. Prove healthy-time transaction initialization, permitted capture owner and a bounded transaction mutex hold time, plus candidate/staged process-lifetime retention during failure/finalization.
2. Build a bounded first-use capture under short UsageLock WITHOUT dereferencing Il2CppClass pointers outside independently proven metadata lifetime; preserve exact FirstUseSequence/detail.
3. Add bounded physical assembly and ordinary class enumeration with independent generation/owner evidence, full source completeness and honest overflow/dropped accounting.
4. Replace allocating MetadataTypeImages index and recursive FormatMetadataOnly with a fixed-budget, byte-equivalent and lifetime-reviewed type-key producer.
5. Only then integrate full general/execution/R02 into authenticated V2 native/C# Player and every UNCHANGED original semantic predicate (P2). E0/E1 Unity engine owner/GC/finalizer/restart remains source/vendor dependent and Blocked. P3 official installed managed/55-native SDK and Player remains NotRun.

**Stop:** Local Validation PAUSED. SNAP-01 FAIL/ReturnRequired (18 cells 14 Passed/4 Failed; ON slot14 scanned prefix262145 over original limit262144, actual complete lengths Unavailable; engine51213 uncapped reports/500ms exit71); N/M/K/I/E FAIL and original strict S custody Blocked (416844 expected/339367 survivors/77477 missing/four native roots absent); independent full-stage R03 FAIL/re-review NotRun. R03Accepted/H2Passed/qualificationApproved/ReadyForHumanReviewGate/fullLegacyRegressionAcceptance all false. PureInterpreter disabled; no H2/X02/M08A.
