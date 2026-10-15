# P1 bounded native transaction inventory — Primary reconciliation

**Owner:** Primary Implementation. **Date:** 2026-10-15 UTC. **Result:** PassedWithinHostScope, additive native transaction-subset capture; **P1 Incomplete**. Local Validation PAUSED; no Unity/Player or new milestone authorized.

## 1. Exact source authority

Canonical four repositories and branch codex/assembly-shadow-r01b-h1:

| Repository | Source authority |
| --- | --- |
| night-outlook/il2cpp_plus | **51c28cf535dc0dcd3294ec49bc6877064d22c75a** — additive real VM transaction inventory method plus fixed capture, source-bound tests and CI |
| night-outlook/hybridclr_demo | Primary documentation publication only; final remote HEAD is a review pin, NOT a new execution |
| night-outlook/hybridclr | **4b2774b066cfc6afd77a8c8aded6bda7ea574f55**, unchanged |
| night-outlook/hybridclr_unity | **948c0e3b4f8891481301770115e8ba4945eea6de**, unchanged |

The **last executed Local host PASS** remains bound to demo 7b9d1d4e37d1731f9f00042eb04892a8afaf7e80 and native 74dbdbea80d83923863303bd2b2c0a87f36541b1, with the same HybridCLR/package pins. Demo Tools/AssemblyShadow/R03/source-pins.json retains this tested tuple; it is intentionally NOT changed to the new uninstalled native CI source. Earlier Local FAIL is independently immutable. Both Local host roots are consumed.

## 2. Implemented Primary-owned code

**New owned source component:** libil2cpp/vm/AssemblyShadowBoundedTransactionInventory.h.

- One no-move/no-copy Capture owns a fixed **1,048,576-byte text arena**, typed arrays of **4096** stable names, **4096** closure/assembly rows, **4096** commit names and **4096** event rows, plus the prior bounded status component (32KiB detail, 8KiB baseline build ID, 8KiB patch ID). A static object-size upper-bound guard is enforced. The absolute capacities are conservative source limits, not permission to truncate or drop input.
- A strict stage machine copies every supplied source field in order. The typed fields preserve candidate names, MVID, skeletonBuilt, runtimeMetadataInitialized, published, moduleInitializerAttempted/Ran, event sequence/kind/name/generation/stagedCount, and all status scalars. Null/overlapping text, invalid member, count overflow, text overflow and stage violation fail closed. No incomplete array, status or prefix can be returned from the sealed accessors.
- A successful capture owns every copied name/MVID/event string and retains **no borrowed source pointer**. A given source span must remain valid only during its synchronous method call. The object must be preallocated while healthy and remain single-owner through capture and reads.

**New actual VM source entry point:** additive AssemblyShadow::TryCaptureBoundedTransactionInventory in libil2cpp/vm/AssemblyShadow.cpp, declared in AssemblyShadow.h.

- Under **one existing transaction.mutex** the entry point copies the prior status fields and transaction-sourced stableAotNames, closure/assembly rows, commitOrder and events directly into the fixed owned Capture. It uses the same candidate/staged data and staged initializer flag atomic loads as original GetDiagnosticsJson, without constructing a new vector or string.
- After unlocking, it uses the original first-failure precedence: immutable TypeFailure error/detail overrides transaction status, and the active snapshot determines Failed or FailedAfterCommit. The adapter compares first-error, state, active and published configuration pointer/generation before/after and rejects a witnessed source change without retry. These guards **do not** prove a global VM epoch or the coherence of independently changing staged flags.
- This method has no caller in the original GetDiagnosticsJson/GetExecutionDiagnosticsJson or Player and is **inactive**. Connector readback independently confirmed those complete original getters AND TryCaptureBoundedTransactionStatus remained **byte-for-byte unchanged** from native base 10a6bece70ec4990dc795daa11b3f4a7629b7a61 to final native source.

**Source bound and test code:** tools/r03/diagnostic_stream/bounded_transaction_inventory_fixture.cpp, run_bounded_transaction_inventory.py and .github/workflows/r03-p1-transaction-inventory.yml. The runner extracts and compiles the **actual production method body** against explicit fixture VM source models, saves per-command raw streams and SHA-256, records full source Git blobs before/after and emits RESULT/MANIFEST for each fresh CI run.

## 3. Verified CI and independent artifact audit

[CI 38778487071](https://github.com/night-outlook/il2cpp_plus/actions/runs/38778487071) completed **SUCCESS, 3/3 jobs** at native HEAD 51c28cf535dc0dcd3294ec49bc6877064d22c75a: macOS 15 Apple Clang, Ubuntu 24.04 Clang and Ubuntu 24.04 GCC. Each ran strict C++17 and ASan/UBSan, with the actual method body and fixed inventory source.

Checks included: all stable/closure/commit/event array order and typed values; empty unstaged MVID and booleans; first TypeFailure precedence with active/nonactive state; mutation after freeze with no borrowed pointers retained; detected TypeFailure, state, active generation, late error, unexpected failure and configuration flips; exact count overflow of each array; 1MiB text overflow, invalid candidate/status detail, illegal stages and deliberate self-overlap; acceptance of a separately allocated adjacent text buffer; and zero observed operator-new calls in the preprepared host-only capture path.

The host fixture also fed the **actual captured transaction subset** plus explicitly **mocked other VM fields** through the existing inactive FrozenGeneralCapture to construct full general JSON, comparing all **1,705 bytes** against current native AssemblyShadowDiagnostics::Serialize. This validates the P1 component interface/field ordering for that synthetic input; it does not prove that the real general getter, physical assembly/class metadata/first-use data or R02 are captured coherently in production.

The three original GitHub CI ZIPs were retrieved and independently verified: **all 57 manifest-declared regular files** matched their byte lengths and SHA-256, no missing/mismatched/unlisted; all three RESULT.json files report PassedWithinHostScope, both profiles Passed, sourcePreserved=true and identical compiled production method SHA-256 **aecef83b206047463c24a355487222a41117c9ba97eb4f0afb38615c2faad3d9**. [EVIDENCE.json](EVIDENCE.json) records artifacts 11994083467/11993329617/11995115862, ZIP hashes and exact case limits.

**This was NOT** official Unity2022.3.62f2 StandaloneOSX native/managed SDK compilation, actual VM execution, Player test, memory/GC/RSS qualification, metadata lifecycle inspection or semantic acceptance.

## 3A. Existing serializer source-gate maintenance — independently retested

The new additive native entry points changed the **whole AssemblyShadow.cpp file blob** but left its original GetExecutionDiagnosticsJson C++ function exactly unchanged. Two existing production-aware CI workflows consequently failed their obsolete entire-file source gate inside tools/r03/diagnostic_stream/current_execution_producer.py. The original immutable historical N implementation and the current complete execution function still have their original independently pinned SHA-256 identities, and no output byte mismatch or product regression was demonstrated by those failures.

Primary updated **only the host test harness** at native HEAD **339a49b5f1eb18c7cef9390c73ee6b64b0e6a36d**: pin the exact original historical source/fixture Git blobs, execution serializer and writer headers, and the complete current GetExecutionDiagnosticsJson **function SHA-256 4829a3ae7b9b0df57d054738f99d940b4ad7644a364df0502c9976469819d372**; record the complete new AssemblyShadow.cpp Git blob and SHA-256 in the new result's source receipt, rather than rejecting unrelated additive source. This preserves fail-closed detection of a modified execution function, and all existing old/current complete-byte parity tests. No product methods were changed in the maintenance commit.

**Both re-run source-bound workflows passed all 3 jobs** at 339a49b5f1eb18c7cef9390c73ee6b64b0e6a36d: [current/frozen producer CI 38780274071](https://github.com/night-outlook/il2cpp_plus/actions/runs/38780274071), including six complete fixture parity pairs, unchanged 25 general-stream cases/profile and altered-frozen-source negative refusal; and [general serializer/V2 interop CI 38780274017](https://github.com/night-outlook/il2cpp_plus/actions/runs/38780274017), with strict/sanitized host checks across macOS Clang and Linux Clang/GCC. Their CI PASS is scoped host evidence only. Earlier red CI attempts remain failed records, not retroactively recategorized.

**Do not conflate other historical workflows:** R02 Primary fixed whole-file integration verification and the R03 terminal business-entry textual source assertion also had independently failed checks earlier on this evolving branch. Those are not claimed corrected or Accepted by this P1 inventory/harness increment. No Human Review Gate or entire repository-wide CI PASS is asserted.

## 4. Source lock/lifetime audit and remaining work

Read [SOURCE_LOCK_LIFETIME_AUDIT.md](SOURCE_LOCK_LIFETIME_AUDIT.md) for the exact source lock scope, STM fields, source cap/error behavior, Current() lazy allocation and proof gaps.

The transaction mutex protects the transaction container/strings, NOT an all-VM instant. Staged initializer booleans are independently atomic. The old Event() source itself caps events at 4096; the new capture neither drops new records nor proves source attempt completeness. The fixed component may copy ~1MiB while holding transaction.mutex: worst-case lock hold time, possible contention/deadlock in terminal paths, prior Current() prewarm and process lifetime of Candidate/StagedAssembly are still unproven. A host mock does not establish the Unity engine owner safe point E0 or native maintenance/finalizer life cycle.

**Earliest unfinished Primary work:** bounded source-level first-use capture under UsageLock, independently reviewed metadata lifetime before dereferencing klass; bounded physical assembly/class enumeration and byte-exact metadata type-key acquisition; full general/execution/R02 coherent or explicitly versioned sub-snapshots, source-level overflow and peak-memory qualification. Only after P1 proofs can P2 real native/C# V2 transaction and **every unchanged original semantic predicate**, E0/E1 legitimate Unity native safe point, and P3 official managed/55-native compiler/Player cycle be authorized. Nontrivial implementation remains Primary-owned, not delegated to Local.

## 5. Historical outcomes and stop

SNAP-01 remains **FAIL/ReturnRequired**: 18 cells (14 Passed / 4 Failed), three ON slot14 scanned prefix262145 over original V1 262144 limit, exact full producer lengths Unavailable; engine 51213 uncapped reports per500ms, exit71. Historical N/M/K/I/E FAIL; original strict S custody Blocked (416844 expected,339367 survivors,77477 missing, four original roots unavailable); independent full-stage R03 review FAIL/re-review NotRun. V2 frame65536, artifact3932160, envelope262144 and combined encoded4194304 unchanged; no truncation, report caps/coalescing, no-op method/default dispatch, sleep/early-exit or finalizer suppression.

R03Accepted=false, H2Passed=false, qualificationApproved=false, ReadyForHumanReviewGate=false, fullLegacyRegressionAcceptance=false; PureInterpreter disabled. **WEB_TO_LOCAL remains PAUSED, no new Local assignment, no official SDK/Player execution or Human Review Gate, no H2/X02/M08A.**
