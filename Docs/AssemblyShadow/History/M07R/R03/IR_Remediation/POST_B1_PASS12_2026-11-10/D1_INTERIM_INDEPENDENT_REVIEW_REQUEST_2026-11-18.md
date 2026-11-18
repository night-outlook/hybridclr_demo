# R03 B2 D1 — interim independent review request (not a completed review)

**Purpose:** Obtain an independently performed D1 review decision **before D2 native lock/registry custody changes**. The user's earlier approval authorizes Approach A and D1–D4 with intermediate review checkpoints; it is NOT a blanket Human Review Gate acceptance. D1 was authored and self-audited by Primary Implementation. This file is a review request, not the decision.

**Branch:** codex/assembly-shadow-r01b-h1, all repositories.

## Exact tested-code pins

| Repository | Commit |
| --- | --- |
| night-outlook/hybridclr_demo | 4522010bbe7657d050f5b90c50dd36ee9055d2f2 — revised D1 tests and CI, documentation HEAD verified separately |
| night-outlook/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 — unchanged |
| night-outlook/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de — unchanged |
| night-outlook/il2cpp_plus | ff0b7f81f6e66ff47a51edb8b348c9d25d2237e3 — inert reviewed D1 header only |

Native header: libil2cpp/vm/AssemblyShadowPublicationPhaseReceipt.h, Git blob a7edf954bfefeafa1c46ccc9a0ab411b5077cb22. Demo review host: Tools/AssemblyShadow/R03IR/TypeDefCensus/PublicationPhaseReceiptReviewHost.cpp, Git blob 8ab2eb8691d2e1baf7bfa70520b169891e4971b0. Demo CI workflow: .github/workflows/r03-b2-d1-publication-phase-receipt.yml, Git blob 516eaf4464dbb16174b074b75394e77ca969bc85.

## Required reading order

1. Docs/AssemblyShadow/README.md; Docs/AssemblyShadow/Plan/CURRENT_STATUS.md; Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md.
2. D1_PUBLICATION_PHASE_RECEIPT_REVIEW_2026-11-18.md (earlier PI evidence).
3. D1_ADVERSARIAL_STATIC_REVIEW_2026-11-18.md (new adversarial PI findings; explicitly NOT independent).
4. The native header and all three D1 source-host tests at the exact pinned commits.
5. [Corrected new CI run 44251246947](https://github.com/night-outlook/hybridclr_demo/actions/runs/44251246947), its four job conclusions and raw receipts. Old CI 44247202018 remains failed; 44247307904 tested the earlier header.

## Independent reviewer acceptance questions

- Does one receipt represent exactly one attempted publication, and can a proved pre-codec rejection return Validated only after the coordinator has independently authenticated complete cleanup? How is a new attempt distinguished from the old one?
- Is it safe that Complete and RejectedBeforeCodec are absorbing, while process-global postcommit terminal failures are handled outside the attempt receipt?
- Are publication phase transitions and first-terminal-reason rules compatible with the intended callback/lock ordering, including when real Codec is attempted but fails or throws?
- Do atomic accesses, record lifetime, lack of copy/move, lock-free target admission and reader teardown meet the actual native integration needs?
- Are the new host checks strong enough for D1 **only**, and do all real Runtime/Unity/GC/Player and D2–D4 gaps remain distinctly marked NotRun?
- Are any D1 findings that require a native API change still open before D2 can safely start?

**Permitted decision:** PassD1ForD2 / ReturnRequired / Blocked. The reviewer should cite exact files and commit SHAs, and record actionable findings. A pass permits proceeding to **D2 only**, not automatically D3/D4, Local Validation or the R03 Human Review Gate. Any finding that changes the phase ABI or retry/terminal semantics returns to Primary Implementation before D2.

**Current outcome:** AwaitingIndependentReview; no reviewer decision exists. WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION, R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false; PureInterpreter disabled. No Unity/SDK/IL2CPP/Player execution or Local Validation handoff is authorized by this request.
