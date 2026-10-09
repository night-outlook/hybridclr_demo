# HybridCLR Assembly Shadow

Plan contains normative design/stages/gates; Handoff contains current assignments; History preserves Local evidence and separate Primary/reviewer assessments.

## Current state

**The independent full-stage R03 review returned FAIL. Primary remediation is in progress; no new Local runtime batch is authorized.** IR-R03-01 has a successful original-S byte audit and a published withdrawal of mismatched Primary provenance claims, but is not independently closed. **IR-R03-02 now has a Primary native terminal-state implementation and separately authored focused Player regression sources**, not yet a passing fresh Unity/Player validation or independent re-review. New Local execution remains gated on pinned compile and contract checks.

Read in order:

1. [Current status](Plan/CURRENT_STATUS.md) and [current handoff boundary](Handoff/WEB_TO_LOCAL.md).
2. Unchanged Local-owned [Local validation](Handoff/LOCAL_VALIDATION.md) and [return to Primary](Handoff/RETURN_TO_WEB.md).
3. [Independent FAIL review](History/M07R/R03/S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md) **and** its [C04 evidence erratum](History/M07R/R03/S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_EVIDENCE_ERRATUM_2026-10-08.md).
4. [Primary remediation checkpoint](History/M07R/R03/IR_Remediation/PRIMARY_REMEDIATION_2026-10-08.md) and [corrective provenance index](History/M07R/R03/IR_Remediation/ORIGINAL_S_PROVENANCE_CORRECTION_2026-10-08.json). Read the [new IR-R03-02 native design](History/M07R/R03/IR_Remediation/IR_R03_02_NATIVE_DESIGN_2026-10-08.md) for source/tests and explicit unproved branches.
5. Original Design/R03 requirements and HUMAN_REVIEW_GATES, plus the [recorded D1=A/D2=A disposition](History/M07R/R03/S_Reconciliation/OWNER_DISPOSITION_2026-10-08.md), [bounded exit matrix](History/M07R/R03/S_Reconciliation/BOUNDED_R03_EXIT_MATRIX.md) and [deferred X02 plan](Plan/stages/X02-pure-interpreter-structural-expansion.md).

## S evidence and correction

S's original Local result remains **EvidenceReadyForPrimaryReview**. Local reported 90 Passed cells, six builds, 59 fresh Players and 18/754/755 Editor scopes with zero skips/inconclusive. That historical outcome is not R03/H2 acceptance and is not a new execution by Primary.

The immutable S evidence publication is `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`; actual S runtime demo source is `29bb3d4a39bf8a2f23be404f77535aaba3485bfc`. Other runtime pins remain HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package `948c0e3b4f8891481301770115e8ba4945eea6de`, and IL2CPP+ `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`. All feature branches remain `codex/assembly-shadow-r01b-h1`.

The original archive is **587,907,380 bytes, nine parts, 15,712 indexed files / 15,713 members**, SHA-256 `23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6`. The earlier Primary five-part/18,160-member attribution is **withdrawn**, not reconciled by an invented transformation. The earlier `S_Reconciliation/EVIDENCE.json` and associated assessments remain historical records, not current authority for the disputed original-archive or unjoined quantitative claims. Use the corrective index above.

Auditor/tests/workflow at `38575b165d798defe545f2501f1fc307ccac44a3` completed [run 37845000985](https://github.com/night-outlook/hybridclr_demo/actions/runs/37845000985): 30 host tests Passed and bounded original-byte/ledger/cell authentication Passed. This is neither a Unity/Player run nor independent reviewer approval. Complete role-specific source/build/process semantic joins and material capture-omission review remain incomplete.

## Current Primary native candidate (not yet Player-validated)

The present candidate feature source is `night-outlook/il2cpp_plus@9ce1c1bfec9a21b92ea300acda5f27a3815b2c37` with the lock-free terminal policy, native entry denial, preserved first-failure diagnostic construction and Linux/macOS **header/contract** CI [37872834945](https://github.com/night-outlook/il2cpp_plus/actions/runs/37872834945) Passed. The new supplementary Player runner is under `Tools/AssemblyShadow/R03IR/`, and the focused R03 source manifest pins that candidate. This does **not** supersede S's historical native pin or prove the full native translation-unit build / a fresh Player. The supplemental C# Player API compiled against the pinned package in [CI 37874183375](https://github.com/night-outlook/hybridclr_demo/actions/runs/37874183375) (0 errors, 13 warnings). The later Linux/macOS IR-host run [37873722486](https://github.com/night-outlook/hybridclr_demo/actions/runs/37873722486) passed **43 tests per platform**, including strict receipt negative controls. Full **official Unity 2022 SDK native translation-unit** compilation and four-process macOS Player validation remain separate and unproved. These source and host checks do not prove a fresh Player.  Independent FAIL remains in force; genuine captured generic and initializer-failure post-poison cases are still outside the present four-process witness.

## Approval and preservation boundary

D1=A retains conservative NativeLayoutAdmissionV1 for R03 and defers V1-external PureInterpreter expansion to X02, without authorizing it. D2=A leaves S performance observational only. The owner decisions do not waive independent findings or grant H2. Automatic reviewer settings remain unchanged.

Preserve all S/R/Q/P/O/N and prerequisite-only evidence. Retained R stays staged and untouched; four contaminated unisolated warm certificates remain Failed. Deferred R02 CPU/H1 RSS risks are not accepted here.

`R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. **Current owner: Primary Implementation.** Native remediation and remaining evidence coverage precede any exact-source Local Validation handoff; independent re-review and the separately initiated Human Review Gate remain required.
