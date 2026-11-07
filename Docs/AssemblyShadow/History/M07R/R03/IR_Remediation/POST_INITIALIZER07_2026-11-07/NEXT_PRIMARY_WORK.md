# R03 remaining Primary Implementation plan — after oneuse-07

Stage: Primary Implementation only. This document is NOT authority for a Local build or Player run. It preserves the 15/15 initializer oneuse-07 focused PASS, original evidence and independent R03 FAIL.

> **Current progress (2026-11-07): A1 completed, A2 earliest incomplete.** The actual independent-owner CLR host, strict source/fixture/receipt checks and dual-OS CI passed at demo source `353617ca0461a5df34f57e44784adae0525b7277` (run `42363760691`). See [A1 review](CAPTURED_GENERIC_A1_OWNER_HOST.md). No native/IL2CPP `method_inst`, captured-baseline terminal error15, prepublication-safe physical type acquisition, or complete V2/whole-VM evidence has run. Continue only A2 Primary source work; this plan does **not** authorize Local Validation. The 15/15 initializer oneuse07 result remains focused PASS, while full independent R03 remains FAIL.


## A. Captured-baseline generic failure (IR-R03-02)

Objective: a real physically captured generic argument whose *generic method's AOT owner is not Methods*, with original baseline Methods.R03.Node as a closed generic argument, prewarmed before Shadow, producing genuine terminal error15 rather than relabeled error13/21.

1. Source-review the pinned native `AssemblyShadow.cpp` captured-argument visitor and owner/instantiation checks, `TerminalProducerFixtures.cs`, current managed Player and `remaining_witness_contracts.py`. Preserve existing original S/initializer fixture SHA roles; do not replace historical Method.dlls.
2. Primary implements a new isolated test-only fixture and managed/native witnesses. Prove actual generic definition owner, physical baseline argument type/image indices, exact invocation path and preterminal positive body side effect; then perform one deliberate postpublication terminal attempted entry and preserved first failure.
3. Provide typed native receipt of real state9/error15/guard reason `CapturedBaselineType`, unchanged pre-bound physical field/canary, fixed native diagnostics and precise method-entry provenance. No host-synthetic status can substitute.
4. Add adversarial negative tests: swapped generic owner/argument image, same owner, missing inflation/attempt/side-effect, error13/21 confusion, forged build/PID/fixture, boolean-as-int, absent first-error detail, invalid original baseline metadata, duplicate/overwritten output.
5. Compile source-only native/C# and strict coordinator tests via dual-OS GitHub Actions before proposing a new Local Player.

## B. Complete native diagnostic V2 (IR-R03-02; separate engineering scope)

The existing `R03IR/NativeDiagnostics/`, `R03IR/bounded_v2/` and `remaining_witness_contracts.py` are host-stage building blocks, not proof that a Unity Player has a full `NativePreopenedSnapshotV2` producer.

1. Define the exact final native producer, epoch and first-error freeze lifecycle; keep the original first VM recovery reason before postterminal managed formatting or allocation. Preserve distinction among actual callback, exception, method-entry, VM-wide publication and shutdown.
2. Implement a bounded, descriptor-relative, exclusive sink with source/fixture/build/PID/nonce and physical snapshot hash joins; no symlink escape, truncation, silently accepted partial report, duplicate writer or invented empty first error.
3. Add host proofs of positive and failure paths, early failure, capacity overflow, short write/fsync, no-fallback allocation, concurrent reader/reentrancy and immutable first failure. Keep raw V1 and V2 explicitly distinct.
4. Only after A and B are reviewed, combine a *single fresh, fixed-size* Local suite where feasible: captured-generic, real initializer control/failure, necessary OFF/reference control(s), exact source/build native V2 joins and historical custody checks. Preserve one-use roots, capacity gates, no retries, and distinct Player processes.

## C. Original S provenance and remaining stage evidence (IR-R03-01)

- Complete every provable original-S nine-part/90-cell/59-process source-to-generated-source/object/link/Player join, including exact generated compiler inputs and archival omissions. Distinguish direct fresh proof, authenticated archived proof, and unavailable owner-retired evidence.
- The 17 deleted roots/40 duplicate paths must remain Unavailable, not recreated or silently waived. Any impossible strict historical custody stays Blocked.
- Complete outstanding RC1–RC6 coverage and bounded D1=A/D2=A claims only with independent authentic source and empirical evidence. Whole-VM epoch, managed shutdown, GC/RSS, captured-generic and native complete general diagnostics still require independent analysis.

## Gate and responsibility

Primary owns all source/design/refactoring/test/diagnostic changes and performs a source-level review before handoff. Local Validation owns real Unity/IL2CPP/compiler/SDK/device execution, empirical receipts, diagnosis and bounded local fixes. Do not leave core architecture implementation to Local.

The current `Handoff/WEB_TO_LOCAL.md` is CLOSED. Only Primary may reopen it by publishing an entirely new one-use, exact-commit, four-repository, fully tested execution contract with fresh absent output roots, host/OS/SDK and capacity gates, fixed scenarios, concrete commands, expected results, acceptance boundaries, evidence, preserved historic data and stop conditions. An independent **user-initiated** full R03 re-review is required before a separate Human Review Gate; neither automation nor Primary self-review may approve that gate.