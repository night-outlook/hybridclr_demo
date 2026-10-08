# Primary Implementation → Local environment: REVIEW ONLY after S

## Current assignment

**No new Local runtime batch is authorized.** The earlier S executing assignment has been consumed. S passed all 90 cells and is reconciled by Primary as passing its prescribed Local contracts. Its original status remains EvidenceReadyForPrimaryReview. The next work is a separate independent full-stage R03 review **under owner-approved D1=A / D2=A scope**, not a rerun, retained-R repair or advancement to M08A. The owner's choices are recorded; they are not reviewer or H2 approval.

Current owner remains **Primary Implementation** for review integration, scope documents and substantive fixes. An independent reviewer must work read-only and return findings, not implement them. This handoff does not claim an independent reviewer has already run.

## Read first

All following paths are under `Docs/AssemblyShadow/`:

1. `README.md` and `Plan/CURRENT_STATUS.md`.
2. Unchanged Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`.
3. `History/M07R/R03/S_Reconciliation/PRIMARY_RECONCILIATION.md` and `FULL_STAGE_PRIMARY_REVIEW.md`.
4. `History/M07R/R03/S_Reconciliation/EVIDENCE.json`, original `OWNER_DECISIONS.md`, recorded `OWNER_DISPOSITION_2026-10-08.md`, `BOUNDED_R03_EXIT_MATRIX.md`, `INDEPENDENT_REVIEW_REQUEST.md` **and** `INDEPENDENT_REVIEW_SCOPE_ADDENDUM.md`.
5. Original R03 design/stage/remaining-completion requirements and HUMAN_REVIEW_GATES; the new assessment does not replace them.

## Exact sources

All branches: `codex/assembly-shadow-r01b-h1`.

| Repository | Owning Local checkout | Required review authority |
|---|---|---|
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | S publication `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`; actual execution `29bb3d4a39bf8a2f23be404f77535aaba3485bfc`; exact final Docs-only assessment transport supplied in Primary's final prompt |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` |

Use the exact final prompt SHA, not an inferred latest tip. Confirm fc55 is its ancestor and that all subsequent changes are confined to Docs/AssemblyShadow. No source/pin/fixture/agent configuration changes are included in this assignment. Use read-only Connector access or safe isolated read-only review views; preserve unrelated/dirty working trees. Do not reset, stash, clean or switch an occupied project to make review convenient.

## Independent review route

Follow INDEPENDENT_REVIEW_REQUEST.md in an actually separate isolated read-only reviewer session. The pinned `.agents/config/config.json` disables automatic reviewer invocation; do not change it or invent a helper result/model identity. An explicitly requested independent stage review remains required despite that setting. Choose a permitted available review route according to the live host schema and the existing agent-collaboration contract. Main-agent self-review or byte-check scripts must not be relabeled as independent.

If no separate independent reviewer can be invoked, report `ReviewBlocked` and `independentReview=NotRun`, with the actual unavailable capability. Do not fabricate a PASS, ninety new Blocked runtime cells or an Off result. No Unity/build/Player execution is a fallback for an unavailable reviewer.

The reviewer must inspect actual pinned design, plan, cross-repository implementation, test semantics and raw evidence; the Primary matrix is a starting point, not authority for its own approval. In particular address RC1 qualification/expansion scope, RC3 supported versus rejected generic/old-handle claims, RC4 installed-baseline versus target graph, RC5 observational versus production performance claims, cleanup versus fresh remote acceptance, and archive/source provenance. The owner **has responded D1=A / D2=A**. Review the amended R03 Design/stage, ADR-0002 and deferred X02 plan against exact code/evidence; keep unrelated RC2–RC4 obligations intact. Do not misclassify the owner scope decision as a stage-review PASS or H2 authorization.

Return an independent report with exact reviewed pins, transport, actual reviewer context, method/exclusions, requirement matrix, findings and PASS/FAIL/BLOCKED verdict. Keep the reviewer read-only. Return its output to Primary for publication and any authorized remediation; do not implement non-trivial changes or overwrite prior review/evidence.

## Evidence and preservation boundary

S live root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery`.
S publication receipt: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261007S-lr-recovery-2/PUBLICATION_RECEIPT.json`.
Committed evidence: `History/M07R/R03/local-validation-20261007-batch-s-evidence-ready`.

Preserve all S/R/Q/P/O/N and prerequisite-only evidence and their original result states. R remains staged and must not be opened in Unity, restored, finalized, moved or deleted. Its historical Git cause remains Unavailable. Four contaminated unisolated warm certificates remain Failed. Local's clean-tree, storage and historical custody observations remain recorded evidence, not an indefinite environmental guarantee.

Do not call run_completion.py, run_storage_checked.py --execute, StructuralRestore or a historical batch command under this assignment. Do not alter source pins, schemas, credentials, protocols, storage thresholds, timeouts, warm-up, leases or gate settings. A finding requiring fresh execution returns to Primary for an impact-specific new handoff.

## Stop and approval boundary

This cycle creates no new Local validation result. Return the independent review or the truthful review blocker to Primary and stop. All substantive design/code/test fixes stay Primary-owned. Owner D1=A/D2=A decisions are now separately recorded and the bounded R03 exit contract amended. An actually separate reviewer must verify that the new contract preserves all non-deferred safety and evidence obligations.

`R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. A reviewer PASS alone does not grant H2. The human-defined H2 remains separately initiated after R03 scope/findings closure. No later milestone or production-performance approval is authorized.
