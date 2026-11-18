# R03 B2 D1 — adversarial Primary static review and contract hardening

**Evidence date:** 2026-11-18 UTC. **Role:** Primary Implementation, separate adversarial pass over the already committed D1 artifact. **Not an independent external reviewer and not a Human Review Gate approval.** Scope is D1 receipt semantics and tests only; D2–D4 production publisher work is intentionally untouched.

## 1. Exact reviewed baseline and scope

All four repositories are on branch codex/assembly-shadow-r01b-h1.

| Repository | Baseline at start of review | Test-relevant result |
| --- | --- | --- |
| night-outlook/hybridclr_demo | b0122d6f8d13e1e2e6d97c87923ae4fb4c2a4397 | Revised workflow code at 4522010bbe7657d050f5b90c50dd36ee9055d2f2; documentation HEAD separately verified |
| night-outlook/il2cpp_plus | c9a772a52d4757281eba63296376c7875a01ae34 | Header-only correction ff0b7f81f6e66ff47a51edb8b348c9d25d2237e3; reviewed new Git blob a7edf954bfefeafa1c46ccc9a0ab411b5077cb22 |
| night-outlook/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 | unchanged |
| night-outlook/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de | unchanged |

The previous [D1 contract implementation review](D1_PUBLICATION_PHASE_RECEIPT_REVIEW_2026-11-18.md) and approved [Approach A / D1–D4 plan](B2_NATIVE_PUBLICATION_REMEDIATION_PREAPPROVAL_DESIGN_2026-11-18.md) are inputs. The corrected prior CI 44247307904 established the initial 4/4 host pass. The current pass independently re-reads the actual header, both existing D1 host files, the workflow, and their original raw CI receipts rather than relying on the previous review prose.

## 2. Findings and dispositions

### D1-IR-01 — HIGH integration ambiguity: receipt lifetime versus Validated retry — HARDENED

The initial header said one writer owned a transaction, and its test allowed RejectedBeforeCodec → MayReturnValidated=true. However RejectedBeforeCodec is absorbing: the same receipt cannot Advance and has no Reset. A caller who keeps one receipt per transaction and tries to reuse it after a permitted precodec rejection would be unable to record a second publication attempt. Resetting this record silently would also erase per-attempt first failure provenance.

**Resolution:** explicitly state ONE receipt per publication ATTEMPT, never per reusable transaction; a later permitted attempt constructs a fresh receipt. No Reset API was added. The new adversarial host verifies that an old rejected attempt remains unchanged while a fresh, distinct receipt can enter the phase sequence. This is a necessary shape contract, **not permission to retry**: D2/D3 must still verify that the transaction and all registries, UsageLock, Codec and VM state truly permit another attempt. Source change is limited to header comments/API guidance, not actual publisher wiring.

### D1-IR-02 — HIGH integration boundary: receipt Complete does not represent late failures — DOCUMENTED AND TESTED

On the current header, Complete is absorbing, and MarkTerminal after Complete is deliberately a no-op. Therefore a post-commit baseline guard, initializer follow-up or other later terminal event cannot rely on this per-attempt receipt alone to change Complete to TerminalRestartRequired. Existing process-global AssemblyShadow terminal/first-failure protections must remain independent and monotonic.

**Resolution:** clarify this in the receipt comments and demonstrate it with an exact-header review-host scenario. D3/D4 must specify the handoff from per-attempt receipt to durable postcommit terminal/first-error state and prove that the latter cannot be lost. No new production postcommit state has been invented in D1.

### D1-IR-03 — MEDIUM: noexcept atomic access is not a lock-freedom guarantee — API/TEST ADDED

The D1 header uses a single atomic uint32_t and declares its APIs noexcept. That proves neither lock-free implementation nor an acceptable latency bound on every Player ABI. A source-host passing on a 64-bit desktop compiler is not a 32-bit Android or iOS demonstration.

**Resolution:** expose a simple noexcept IsLockFreeOnThisTarget() query. The new host asserts lock-freedom on the actually tested macOS/Ubuntu CI runners. This is a platform admission input, not proof about all target devices or all source/compiler combinations. D2/D3 must decide how a non-lock-free target is rejected or measured; do not silently classify the property as globally proven.

### D1-IR-04 — HIGH, OPEN for D2/D3: booleans are an assertion, not rollback evidence

A caller can supply all four true fields of PreCodecCleanupProof without a VM-authenticated proof that Codec was never entered and that both registries and UsageLock were actually restored. The D1 receipt only verifies the consistency of the *reported* phase and proof; it cannot observe the actual native side effects.

**Required D2/D3 proof:** capture no-codec-attempt markers before entering Codec, verify native physical and CLI rollback under their actual locks, prove UsageLock was released, and ensure the return-to-Validated path is **never used** after P3 CodecAttempted. No D1 product integration or false acceptance occurs.

### D1-IR-05 — OPEN for D2/D3: publication race, object lifetime and global failure state

The receipt is a **single-writer per-attempt** atomic snapshot. The review host exercises multiple concurrent readers during one terminal transition; it does not authorize racing writers, protect a destroyed attempt object from a late reader, or certify process-wide monotonic terminal status. D2/D3 must define the object owner, its lifetime through callbacks, its transfer to durable process state before teardown, and ordering under transaction/metadata/assembly/usage/Codec locks. No current test proves Native Concurrent Reader/GC epoch, Unity Player or shutdown drain progress.

### D1-IR-06 — ACCEPTED D1 scope only: ABI and Unity still not verified

The header is inert and does not alter the current player/native TU roster. Strict C++11/C++17, ASan/UBSan, and -fno-exceptions/-fno-rtti host compiles establish only the exercised environments. Full 32-bit target ABI, true lock-free implementation on Android/iOS, Class/GC lifetime and V1/B1/R02 compatibility remain Local Validation work, not R03 acceptance.

## 3. Implemented hardening and scope

Changes:
- il2cpp_plus/libil2cpp/vm/AssemblyShadowPublicationPhaseReceipt.h — explicit per-attempt/no-reset and separate post-Complete terminal guard contract; noexcept target lock-free query. New blob a7edf954bfefeafa1c46ccc9a0ab411b5077cb22.
- hybridclr_demo/Tools/AssemblyShadow/R03IR/TypeDefCensus/PublicationPhaseReceiptReviewHost.cpp — adversarial six-scenario executable, independently testing per-attempt reuse prohibition, absorbing completion/rejection, terminal retry refusal, coherent concurrent terminal reads, and host lock-free observation. New blob 8ab2eb8691d2e1baf7bfa70520b169891e4971b0.
- hybridclr_demo/.github/workflows/r03-b2-d1-publication-phase-receipt.yml — updated exact native commit/blob and added review executable to strict/sanitized/no-exceptions profiles. Git blob 516eaf4464dbb16174b074b75394e77ca969bc85.

The original D1 phase and fault test files remain untouched. No change to actual AssemblyShadow::CommitTransaction, Codec/Runtime, callbacks, native publication locks, active snapshot or Unity source roster. This deliberately does not begin D2.

## 4. Fresh exact-source verification evidence

[**GitHub CI 44251246947**](https://github.com/night-outlook/hybridclr_demo/actions/runs/44251246947) ran at hybridclr_demo code commit 4522010bbe7657d050f5b90c50dd36ee9055d2f2 and native header commit ff0b7f81f6e66ff47a51edb8b348c9d25d2237e3.

**4/4 completed/success**, macOS 15 and Ubuntu 24.04, C++11/C++17; four exact remote job readbacks showed:
- Original D1 phase host: **17 scenarios / 396 assertions**, strict, sanitizer and no-exceptions profiles per job (12 completed host executions).
- New adversarial review host: **6 scenarios / 51 assertions**, strict, sanitizer and no-exceptions per job (12 executions); each host reported target lock-free on the two tested CI OSes.
- Original D1 simulated fault host: nine separate-process cases, two profiles per job (**72 receipts**), no Unity/acceptance flags promoted.
- No compile failures, sanitizer errors or failed host assertions in the four completed job logs.
- Earlier workflow [44247202018](https://github.com/night-outlook/hybridclr_demo/actions/runs/44247202018) remains FAILED at a shallow-checkout diff-tree assumption. Intermediate success [44247307904](https://github.com/night-outlook/hybridclr_demo/actions/runs/44247307904) remains a valid pass of the original header, **not** of the new reviewed header.

This is D1 receipt proof under test-owned simulated callbacks and actual C++ header compilation only; it does not exercise live Unity, real HybridCLR Codec invocation or native D2 custody.

## 5. Reviewer disposition and next checkpoint

**D1 primary adversarial source audit: COMPLETED; D1 review findings IR-01/02/03 addressed in the contract/host; remaining IR-04/05/06 are explicit D2–D4/Local prerequisites.**

**Independent external/human interim review: PENDING.** The author is the same Primary Implementation Owner who produced the earlier code, so this report does **not** meet an independently performed second-agent review and cannot self-approve an interim Human Review Gate. Before D2 production source edits, an authorized independent reviewer should inspect both commits, the final D1 API contract, CI receipts, and the unresolved D2/D3 integration properties, then record a clear pass/return/blocked decision. Do not infer this review occurred merely because CI passed.

D2, D3, D4 = NotStarted. WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; PureInterpreter disabled. Native B2 128 combined TypeDefs / 64-byte names / 65,536 owner lookups, original V1/B1/R02/resolver/manifest unchanged. No H2/M08A/X02/SNAP-01, consumed Local replay or self-approved Human Review Gate.
