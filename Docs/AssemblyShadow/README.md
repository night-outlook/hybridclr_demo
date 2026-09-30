# HybridCLR Assembly Shadow

This is the canonical documentation root.

- `Plan/`: design, roadmap, stages and normative review gates.
- `Handoff/`: live Primary Implementation / Local Validation coordination.
- `Architecture/`: durable decisions.
- `History/`: immutable evidence, implementation and review records.
- `Evidence/`: protected fixture and artifact catalogs.

**R02 is accepted as `PassedWithExplicitDeferredRisk`.** Batch I completed 34/34 required cells, independent stage review returned PASS with zero findings, and the owner explicitly selected `R02-D1=A, R02-D2=A`.

Read `Plan/CURRENT_STATUS.md`, `History/M07R/R02/I_R02_ACCEPTANCE_DECISION.md`, `History/M07R/R02/I_PRIMARY_REVIEW.md`, and `Handoff/WEB_TO_LOCAL.md`.

The accepted execution remains candidate `19b0adcf0a1f376f16eaebf16558d0dcdfdafe6f`, source `a81bb0d7b886fe941ba4b132296a30dcf4a319cc`, control `21c689732cd8087f8ee8fdce4e52a8f2a655f722`, candidate IL2CPP `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`, control IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933`, and package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.

R02-D1 retains measured CPU residuals through H2. R02-D2 preserves the original H1 RSS risk and future production RAM-budget work. Neither decision is a production SLA, release acceptance, or proof that historical memory cost disappeared.

`R02Accepted=true` and `mayEnterR03=true`, but **R03 has not started**. The next explicitly initiated Primary cycle follows `Plan/stages/R03-evolution-semantics.md`. Normative H2 remains after R03; do not treat this R02 decision as H2 approval.
