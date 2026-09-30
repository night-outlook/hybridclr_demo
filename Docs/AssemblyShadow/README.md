# HybridCLR Assembly Shadow

This is the canonical documentation root.

- `Plan/`: design, roadmap, stages and normative review gates.
- `Handoff/`: live Primary Implementation / Local Validation coordination.
- `Architecture/`: durable decisions.
- `History/`: immutable evidence, implementation and review records.
- `Evidence/`: protected fixture and artifact catalogs.

**R02 batch I is complete: 34/34 cells Passed and independent stage review PASS, zero findings.** Local return is `7a88cfc867d37360a1dc6a06892b3811ec025adf`. Primary reconciled the committed checkpoint and measured performance data. The remaining step is explicit R02 acceptance and D1/D2 risk disposition, not another automatic repair/build cycle.

Read `Plan/CURRENT_STATUS.md`, `Handoff/WEB_TO_LOCAL.md`, and `History/M07R/R02/I_PRIMARY_REVIEW.md`, `I_PRIMARY_AUDIT.json` and `I_NEXT_VALIDATION_PLAN.md`. The original I checkpoint and Local-owned handoff records are preserved unchanged. Prior `PRIMARY_VALIDATION.md` remains the exact host/source CI record.

Common source remains `a81bb0d7b886fe941ba4b132296a30dcf4a319cc`; control remains `21c689732cd8087f8ee8fdce4e52a8f2a655f722`. Candidate native is `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`; control native remains `6be7f38bec2fa4677d24efc1a4a1294240789933`. Both roles use package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.

H1 remains `PassedWithExplicitDeferredRisk`. `R02Accepted=false` and `mayEnterR03=false` pending the explicit choices in the Primary review. Normative H2 still follows R03; I's readiness is not H2 approval. Local should synchronize documentation and preserve evidence only. Do not rerun I or start R03 from this update.
