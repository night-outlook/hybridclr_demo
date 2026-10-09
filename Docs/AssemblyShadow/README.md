# HybridCLR Assembly Shadow

Plan contains normative design/stages/gates; Handoff contains current assignments; History preserves Local evidence and separate Primary/reviewer assessments.

## Current state

**The current Player C# compilation prerequisite is repaired and published. Local storage remains unresolved.** One fresh B preflight/diagnostic is authorized by [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md); runtime execution is conditional on all source, custody, host, compile-equivalence and fresh storage checks passing. Primary has not reclaimed, reserved or measured local disk capacity. The original independent full-stage R03 review remains **FAIL**, with independent re-review **NotRun**.

Read in order:

1. [Current status](Plan/CURRENT_STATUS.md) and [current handoff](Handoff/WEB_TO_LOCAL.md).
2. Unchanged Local-owned [validation result](Handoff/LOCAL_VALIDATION.md) and [return to Primary](Handoff/RETURN_TO_WEB.md). The immutable A preflight-blocked checkpoint is `History/M07R/R03/local-validation-20261009-ir-r03-02-preflight-blocked/` at demo `d576ae49261a35565bca9fc0701e835d8d9a87fa`.
3. [Current source-matched API correction](History/M07R/R03/IR_Remediation/IR_LOCAL_API_01_2026-10-09/README.md), [machine-readable evidence](History/M07R/R03/IR_Remediation/IR_LOCAL_API_01_2026-10-09/EVIDENCE.json) and [B focused procedure](History/M07R/R03/IR_Remediation/IR_R03_02_FOCUSED_LOCAL_PROCEDURE_2026-10-09.md).
4. [Native design](History/M07R/R03/IR_Remediation/IR_R03_02_NATIVE_DESIGN_2026-10-08.md), [immutable fixture policy](History/M07R/R03/IR_Remediation/IR_R03_02_FIXTURE_PROVENANCE_2026-10-09.md), [independent FAIL review](History/M07R/R03/S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md) and [C04 citation erratum](History/M07R/R03/S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_EVIDENCE_ERRATUM_2026-10-08.md).
5. Original R03 Design/Plan and HUMAN_REVIEW_GATES, [D1=A/D2=A disposition](History/M07R/R03/S_Reconciliation/OWNER_DISPOSITION_2026-10-08.md), [bounded exit matrix](History/M07R/R03/S_Reconciliation/BOUNDED_R03_EXIT_MATRIX.md), [original-S correction](History/M07R/R03/IR_Remediation/ORIGINAL_S_PROVENANCE_CORRECTION_2026-10-08.json) and [deferred X02](Plan/stages/X02-pure-interpreter-structural-expansion.md).

## Current evidence versus runtime acceptance

A Local preflight passed 64 Python tests, 69 native policy checks, authentication of 15 original S fixtures and before/after custody of 416,161 files. It correctly stopped with **zero Unity launches; all 14 cells / 3 builds / 4 Players NotRun**. Its available space was 68,289,347,584 versus required 68,719,476,736 bytes. That historical capacity rejection and earlier-Player API **NoCoverage** finding remain unchanged in Local's records.

Fresh [C# API run 37903041633](https://github.com/night-outlook/hybridclr_demo/actions/runs/37903041633) passed at demo `ba47b41674b83a6f694ac4f8ac1bc8f83a9da24b`: **0 errors, 13 warnings**, actual current Player input and real pinned HybridCLR package. The workflow now records input Git blobs/hashes, exact compiler invocation and result/output hashes. Primary verified the downloaded artifact; exact input/result receipts and a lossless full compiler log are published in the correction directory. Eleven separate synthetic receipt tests passed.

This was **net8.0/C#9 compilation with Unity API stubs**, not compilation against official Unity managed assemblies, Unity execution, a Player build, or independent approval. The native candidate remains IL2CPP+ `9ce1c1bfec9a21b92ea300acda5f27a3815b2c37`, HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package `948c0e3b4f8891481301770115e8ba4945eea6de`. All feature branches remain `codex/assembly-shadow-r01b-h1`; final demo transport must be a Docs-only descendant of ba47. Runtime sources, fixtures and storage thresholds were not changed in this correction.

B uses new, locally verified-unused paths and the unchanged `max(64GiB, 2*Q+20GiB)` storage policy with 20GiB operating floor. No protected cleanup, threshold reduction, stale-capacity reuse or same-root retry is authorized. Genuine captured-generic and initializer-failure witnesses, remaining IR-R03-01 semantic/capture work, broader regression acceptance and separate independent re-review remain incomplete.

## Historical authority and preservation

S remains EvidenceReadyForPrimaryReview: 90 Passed cells, six builds, 59 fresh Players, 18/754/755 Editor scopes. S runtime demo is `29bb3d4a39bf8a2f23be404f77535aaba3485bfc`, evidence publication `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`, historical native `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`; those are not the new candidate's execution evidence.

The original S archive is **587,907,380 bytes, nine parts, 15,712 indexed files / 15,713 members**, SHA-256 `23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6`. The earlier five-part/18,160 attribution and unjoined quantitative claims remain withdrawn, not retrospectively reconciled. The corrective provenance index is current authority. Failed S regeneration comparisons remain Failed/NotIdentical; B copies the 15 original Git inputs and uses a separately authenticated IR-only target.

Preserve S/R/Q/P/O/N and A, all prerequisite and failed-attempt evidence, staged retained R, four Failed contaminated warm certificates and unaccepted deferred R02 CPU/H1 RSS risks. D1=A bounds NativeLayoutAdmissionV1 and defers X02 without authorizing it; D2=A keeps performance observational. Automatic reviewer settings remain unchanged.

`R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. **Stop after the one B Local result and return to Primary Implementation.** No H2, X02 or M08A is begun; the Human Review Gate remains separately human-initiated.
