# HybridCLR Assembly Shadow

This is the canonical documentation root.

- `Plan/`: design, roadmap, stage specifications and review gates.
- `Handoff/`: live Primary Implementation and Local Validation contract.
- `Architecture/`: durable design decisions.
- `History/`: historical evidence and current R02 implementation records.
- `Evidence/`: evidence catalogs and protected pins.

H1 remains `PassedWithExplicitDeferredRisk` after explicit user acceptance of D1=A and D2=A. Historical evidence keeps its original status.

R02 Primary Implementation has incorporated Local return `621216751ade64aa39f28ed44a5acdc15c38c6cc` and published the build-boundary repair. Repaired source anchor: `82d64ce415c062729f0082e81c1808eaac9602e4`; matched H1-runtime control: `6c950eaa98f995084750fe1ea8f80cfe4c59c61b`. Final R02 Primary CI run `36318653155` passed, and final scoped legacy-H1 CI run `36318659885` passed.

R02 itself is **not accepted** until the new Local Validation batch and independent R02 stage review complete. Read `Plan/CURRENT_STATUS.md`, `Handoff/WEB_TO_LOCAL.md`, `History/M07R/R02/LOCAL_VALIDATION_TASKS.md`, and `History/M07R/R02/PRIMARY_VALIDATION.md`. Do not begin R03.
