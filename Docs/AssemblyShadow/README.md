# HybridCLR Assembly Shadow

This is the canonical documentation root.

- `Plan/`: design, roadmap, stage specifications and review gates.
- `Handoff/`: live Primary Implementation and Local Validation contract.
- `Architecture/`: durable design decisions.
- `History/`: historical evidence and current R02 implementation records.
- `Evidence/`: evidence catalogs and protected pins.

H1 remains `PassedWithExplicitDeferredRisk` after explicit D1=A and D2=A. Historical evidence keeps its original status.

Primary has incorporated Local return `39dd8213f0a93a2ebde4bdbe982ead4214e9b2eb`. Batch-D repair source: `57a9470bf299af60f88112998c8326c4c013204a`; matched H1-runtime control: `a379f0b809a5d8af967df06fc83271d90fd84f4c`. Final authority `96ec97221439ab1ca8964acaf5bf2b5b16e2dcda` passed R02 CI 36323257884 (Linux and macOS) and scoped legacy CI 36323257953.

Read `Plan/CURRENT_STATUS.md`, `Handoff/WEB_TO_LOCAL.md`, `History/M07R/R02/D_COMPLETION_REPAIR.md`, `LOCAL_VALIDATION_TASKS.md` and `PRIMARY_VALIDATION.md` in that R02 directory. The next Local batch has 33 required cells. R02 remains unaccepted until real Local evidence and independent stage review complete. Do not begin R03.
