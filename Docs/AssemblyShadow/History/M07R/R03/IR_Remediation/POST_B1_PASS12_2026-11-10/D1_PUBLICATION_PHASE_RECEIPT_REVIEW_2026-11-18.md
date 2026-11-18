# R03 B2 / D1 — Atomic publication-phase receipt: design → implementation → host evidence review

**Evidence date:** 2026-11-18 UTC. **Stage:** D1 only (preallocated/nonallocating phase-receipt contract). **Branch:** codex/assembly-shadow-r01b-h1 across all four repositories.

## D0 approval and scope

The human explicitly approved **Approach A: phase-aware terminal fail-closed** and authorized the D1–D4 implementation sequence **subject to intermediate review checkpoints** in the conversation immediately preceding this D1 cycle. This is **not** approval of R03, the final Human Review Gate, a Local Validation run, or automatic advancement beyond the current D1 checkpoint.

The source design is [B2_NATIVE_PUBLICATION_REMEDIATION_PREAPPROVAL_DESIGN_2026-11-18.md](B2_NATIVE_PUBLICATION_REMEDIATION_PREAPPROVAL_DESIGN_2026-11-18.md). Its historical heading "pre-approval" is retained for provenance; this D1 note records the subsequent human approval. D1 implements an **inert** C++ contract in the native fork and test-only hosts in the demo. D2 (native lock/registry custody), D3 (real Runtime bridge), D4 (snapshot lifetime) are not started.

### Pinned four-repository state

| Repository | Exact tested source |
| --- | --- |
| night-outlook/hybridclr_demo | CI/test code commit **6d0452b0538f85adbd2d851ff29a93a3d23d652e** (final docs-only HEAD must be verified separately) |
| night-outlook/hybridclr | **4b2774b066cfc6afd77a8c8aded6bda7ea574f55** — unchanged |
| night-outlook/hybridclr_unity | **948c0e3b4f8891481301770115e8ba4945eea6de** — unchanged |
| night-outlook/il2cpp_plus | **c9a772a52d4757281eba63296376c7875a01ae34** — new inert header |

Exact added/changed tested blobs:
- il2cpp_plus/libil2cpp/vm/AssemblyShadowPublicationPhaseReceipt.h: **acd360895ec619749ea5c184f1949d64fd0123e4**
- hybridclr_demo/Tools/AssemblyShadow/R03IR/TypeDefCensus/PublicationPhaseReceiptHost.cpp: **263ee93bf970d94d06b8342e093259e05e3be782**
- hybridclr_demo/Tools/AssemblyShadow/R03IR/TypeDefCensus/PublicationPhaseReceiptFaultHost.cpp: **b4583a84597925120a2f01e73ff86c0c21902d83**
- hybridclr_demo/.github/workflows/r03-b2-d1-publication-phase-receipt.yml: **2fe3bb29af9a7b01229bc29ecfabf6d768e00dcb**

The new header is **not referenced** by AssemblyShadow.cpp, the C++/Unity production compilation roster, the HybridCLR Codec/Runtime or a managed API. It changes no current program behavior, ABI enum, Unity build settings, B2 capacity, V1/B1/R02 behavior, resolver or PureInterpreter activation. Header inclusion, live phase writes and terminal state consumption belong to future separately reviewed slices.

## D1 design and implementation

The receipt is an embedded, constructor-initialized **single std::atomic<uint32_t>** whose acquire-read returns a coherent phase/outcome/first-reason snapshot. It owns no heap, strings, metadata pointer, mutex or callback. Its constructor and public methods are noexcept; host compilation checks that the receipt occupies at most 16 bytes (not an installed 32-bit ABI proof). There is **one writer per transaction**, with concurrent readers permitted; racing writers are invalid and cause terminal classification on conflicting transition.

The sequential phases are P0 Prepared, P1 UsageAdmitted, P2 RegistriesAppended, P3 CodecAttempted, P4 RuntimeGroupPublished, P5 ActiveSnapshotPublished, P6 InitializersRunning. D3 must mark **CodecAttempted before entering the real Codec**, not retroactively from its return status.

Outcomes are InProgress, RejectedBeforeCodec, TerminalRestartRequired and Complete. Reasons are small bounded enum codes including MissingCleanupProof, InvalidPhaseTransition, CodecOutcomeUnknown, NativePublicationFailure, SnapshotOwnershipUnverified and InitializerFailure. A first terminal reason is monotonic and cannot be overwritten. Complete and RejectedBeforeCodec are absorbing; attempts to advance them fail without changing them.

**The only MayReturnValidated=true condition** is a successful RejectBeforeCodec called during P0–P2, with all four evidence flags true: CodecNotAttempted, physical registry restored, CLI registry restored, usage lock released. Missing any flag triggers terminal/restart-required; calling RejectBeforeCodec in P3 or later triggers terminal CodecOutcomeUnknown **even if all booleans are true**. The caller is responsible for actually authenticating these properties: the receipt stores the supplied evidence and enforces stage consistency but **does not independently prove** native rollback or VM lifetime.

Complete requires P6. Invalid phase jumps, premature completion, an unknown result and failed cleanup proof cannot become a retry permit. No implicit retry/reset API is included. An actual post-Complete business failure still requires integration with the existing postcommit first-error/terminal path in D3/D4; the D1 receipt is not a substitute.

## Test and CI evidence

[**Corrected exact-code CI 44247307904**](https://github.com/night-outlook/hybridclr_demo/actions/runs/44247307904) completed **4/4 success** on macOS 15 and Ubuntu 24.04 × C++11/C++17. The workflow authenticates the exact native header commit, Git-tree blob and checked-out-file blob. Each job:
- builds and executes PublicationPhaseReceiptHost under **strict -O2, ASan+UBSan and -fno-exceptions/-fno-rtti**: **17 scenarios / 396 assertions per process**, three executions per job = 12 receipt-host executions total;
- builds and executes PublicationPhaseReceiptFaultHost under strict and ASan+UBSan, with **nine isolated processes per profile**: preflight-clean, usage-clean, registries-clean, registry-cleanup-unverified, codec-unknown-throw, post-group-throw, post-active-throw, initializer-throw, completed — **72 fault-host JSON receipts** total;
- rejects missing/incorrect output, incorrect terminal/Validated classification, skipped scenarios and true product/Unity/Human Review flags.

The source host checks in-progress/complete/terminal states, first-error preservation, illegal jumps, missing evidence, postcodec retry refusal, and single-word concurrent-read consistency. The fault host uses **simulated** registry/usage/Codec state, not the actual native callbacks. It intentionally injects C++ exceptions and validates terminal classification. Both suites retain nativeIntegration=false, actualCodecAttempted=false, realUnity=false, R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false.

[**Initial run 44247202018**](https://github.com/night-outlook/hybridclr_demo/actions/runs/44247202018) **FAILED** during a Git source-admission shell check: diff-tree HEAD expected a parent in a shallow detached checkout. The source pin and actual new header commit were valid; the corrected workflow uses exact commit and tree/on-disk blob checks without parent-dependent diff-tree. The failed run is preserved, not upgraded to PASS.

This is **not** D2 lock custody validation, a native Runtime/Codec execution, Unity/IL2CPP Player validation or a proof that caller-supplied cleanup evidence is truthful.

## Independent-style Primary source review findings

- **D1-01 PASS / bounded:** the receipt contains no dynamic allocation, logging, managed call, native lock or new production callback. It encodes phase/outcome/first-reason in one atomic value and uses C++11-compatible noexcept methods. Both clang and GCC strict/sanitized/no-exceptions compiles pass in CI.
- **D1-02 PASS / modeled policy:** explicit P0–P2 positive cleanup proofs can yield RejectedBeforeCodec; missing proof or any P3+ attempted-codec outcome cannot yield MayReturnValidated. Terminal reason is absorbing and first-wins in tested scenarios.
- **D1-03 OPEN / HIGH:** all proof booleans are supplied by the caller. D2/D3 must independently establish registry/usage cleanup and codec invocation provenance at exact native boundaries; do not trust the booleans without that evidence.
- **D1-04 OPEN / HIGH:** ownership of UsageLock across callbacks, reverse mutex edges, physical+CLI vector exceptional cleanup, and snapshot lifetime are unchanged in production. The actual callback host previously demonstrated an inconsistent partial state.
- **D1-05 OPEN:** the receipt is not connected to a real D3 CodecAttempted marker or durable first-error/terminal guard. Native VM readers, shutdown, GC/class/metadata epoch, real Unity Player/32-bit ABI, V1 field 14/15 and native V2 remain uncovered. Atomic operations being noexcept does not prove lock-free or bounded duration on every target.
- **D1-06 REVIEW CHECKPOINT:** this D1 source/test review is an agent-authored evidence assessment, **not human approval to enter D2**, and not the project Human Review Gate. Preserve the user's D0 authorization while obtaining/recording the intermediate D1 review decision before implementing native registry/lock custody.

**Disposition:** D1 Implementation = Complete within inert source/host scope. D1 independent/human checkpoint = Awaiting Review; D2/D3/D4 = NotStarted. Local Validation stays **CLOSED_NO_LOCAL_EXECUTION**; no Unity/SDK/IL2CPP execution authorized and no handoff is issued. R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or self-approval.
