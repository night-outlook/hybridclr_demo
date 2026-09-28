# HybridCLR Assembly Shadow

This is the canonical documentation root.

- `Plan/`: design, roadmap, stage specifications and review gates.
- `Handoff/`: live Primary Implementation and Local Validation contract.
- `Architecture/`: durable design decisions.
- `History/`: historical evidence and current R02 implementation records.
- `Evidence/`: evidence catalogs and protected pins.

H1 remains `PassedWithExplicitDeferredRisk` after D1=A and D2=A. Historical evidence retains its original status.

Primary incorporated Local batch E return `1d7dc134003206ada8a92b50763ca2da7dc9530d`. Current source anchor: `d4cfbe5da29482a3b307fbec3333821615288129`; matched H1-runtime control: `5a931fe86795e8cc192d3df262cdee824b105963`. Candidate authority `69f75b78a0696be8b7da69c1725f07c6e1708c48` passed R02 CI 36330847917 (Linux/macOS), scoped legacy CI 36330847766 and fixed-input provenance CI 36330847788.

Read `Plan/CURRENT_STATUS.md`, `Handoff/WEB_TO_LOCAL.md` and `History/M07R/R02/E_M00_REPAIR.md`, `LOCAL_VALIDATION_TASKS.md`, `PRIMARY_VALIDATION.md`. The next Local batch has **34 cells**, including read-only E DLL forensics and independent historical fixed-input materialization in both workspaces. Fresh M07 validation is still required. R02 is not accepted; do not begin R03.
