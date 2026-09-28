# HybridCLR Assembly Shadow

This is the canonical documentation root.

- `Plan/`: design, roadmap, stage specifications and review gates.
- `Handoff/`: live Primary Implementation and Local Validation contract.
- `Architecture/`: durable decisions.
- `History/`: immutable historical evidence and current R02 implementation records.
- `Evidence/`: protected fixture and artifact catalogs.

H1 remains PassedWithExplicitDeferredRisk after D1=A/D2=A. Historical results keep their original classification.

Primary incorporated Local return `d33792957303488e03529c945ac01ce0eedd660b`. Batch-H common source is `a81bb0d7b886fe941ba4b132296a30dcf4a319cc`; matched H1-runtime control is `21c689732cd8087f8ee8fdce4e52a8f2a655f722`. **Candidate IL2CPP now uses `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`; control keeps H1 IL2CPP.** Both roles retain package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.

Authority `c5278a1a6fe024f1b00f8807d4e162e8e6f17d4d` passed R02/Linux/macOS CI 36431496003, actual macOS writer/parser CI 36431496157, legacy CI 36431495940 and M00 origin CI 36431495954. Read `Plan/CURRENT_STATUS.md`, `Handoff/WEB_TO_LOCAL.md`, and `History/M07R/R02/H_RUNTIME_REPAIR.md`, `LOCAL_VALIDATION_TASKS.md`, `PRIMARY_VALIDATION.md` and `source-targets.json`.

Use the final verified candidate transport HEAD from Primary's prompt, not the earlier source/CI commit. Run one fresh 34-cell Local batch with newly source-bound builds. Host/source CI is not Unity Player acceptance; R02 remains unaccepted and D1/D2 require measured disposition before H2. Do not begin R03.
