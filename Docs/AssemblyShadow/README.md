# HybridCLR Assembly Shadow

Plan contains normative design/stages/gates; Handoff contains current assignments; History preserves Local evidence and separate Primary/reviewer assessments.

## Current state

**The independent full-stage R03 review returned FAIL. Primary remediation is in progress; no new Local runtime batch is authorized.** IR-R03-01 has a successful original-S byte audit and a published withdrawal of mismatched Primary provenance claims, but is not independently closed. IR-R03-02 remains open: the native terminal-execution correction and its new runtime regression are not implemented in this checkpoint.

Read in order:

1. [Current status](Plan/CURRENT_STATUS.md) and [current handoff boundary](Handoff/WEB_TO_LOCAL.md).
2. Unchanged Local-owned [Local validation](Handoff/LOCAL_VALIDATION.md) and [return to Primary](Handoff/RETURN_TO_WEB.md).
3. [Independent FAIL review](History/M07R/R03/S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md) **and** its [C04 evidence erratum](History/M07R/R03/S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_EVIDENCE_ERRATUM_2026-10-08.md).
4. [Primary remediation checkpoint](History/M07R/R03/IR_Remediation/PRIMARY_REMEDIATION_2026-10-08.md) and [corrective provenance index](History/M07R/R03/IR_Remediation/ORIGINAL_S_PROVENANCE_CORRECTION_2026-10-08.json).
5. Original Design/R03 requirements and HUMAN_REVIEW_GATES, plus the [recorded D1=A/D2=A disposition](History/M07R/R03/S_Reconciliation/OWNER_DISPOSITION_2026-10-08.md), [bounded exit matrix](History/M07R/R03/S_Reconciliation/BOUNDED_R03_EXIT_MATRIX.md) and [deferred X02 plan](Plan/stages/X02-pure-interpreter-structural-expansion.md).

## S evidence and correction

S's original Local result remains **EvidenceReadyForPrimaryReview**. Local reported 90 Passed cells, six builds, 59 fresh Players and 18/754/755 Editor scopes with zero skips/inconclusive. That historical outcome is not R03/H2 acceptance and is not a new execution by Primary.

The immutable S evidence publication is `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`; actual S runtime demo source is `29bb3d4a39bf8a2f23be404f77535aaba3485bfc`. Other runtime pins remain HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package `948c0e3b4f8891481301770115e8ba4945eea6de`, and IL2CPP+ `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`. All feature branches remain `codex/assembly-shadow-r01b-h1`.

The original archive is **587,907,380 bytes, nine parts, 15,712 indexed files / 15,713 members**, SHA-256 `23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6`. The earlier Primary five-part/18,160-member attribution is **withdrawn**, not reconciled by an invented transformation. The earlier `S_Reconciliation/EVIDENCE.json` and associated assessments remain historical records, not current authority for the disputed original-archive or unjoined quantitative claims. Use the corrective index above.

Auditor/tests/workflow at `38575b165d798defe545f2501f1fc307ccac44a3` completed [run 37845000985](https://github.com/night-outlook/hybridclr_demo/actions/runs/37845000985): 30 host tests Passed and bounded original-byte/ledger/cell authentication Passed. This is neither a Unity/Player run nor independent reviewer approval. Complete role-specific source/build/process semantic joins and material capture-omission review remain incomplete.

## Approval and preservation boundary

D1=A retains conservative NativeLayoutAdmissionV1 for R03 and defers V1-external PureInterpreter expansion to X02, without authorizing it. D2=A leaves S performance observational only. The owner decisions do not waive independent findings or grant H2. Automatic reviewer settings remain unchanged.

Preserve all S/R/Q/P/O/N and prerequisite-only evidence. Retained R stays staged and untouched; four contaminated unisolated warm certificates remain Failed. Deferred R02 CPU/H1 RSS risks are not accepted here.

`R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. **Current owner: Primary Implementation.** Native remediation and remaining evidence coverage precede any exact-source Local Validation handoff; independent re-review and the separately initiated Human Review Gate remain required.
