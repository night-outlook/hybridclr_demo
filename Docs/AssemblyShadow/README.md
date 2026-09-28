# HybridCLR Assembly Shadow

This is the canonical documentation root.

- `Plan/`: design, roadmap, stage specifications and review gates.
- `Handoff/`: live Primary Implementation and Local Validation contract.
- `Architecture/`: durable design decisions.
- `History/`: historical evidence and current R02 implementation records.
- `Evidence/`: evidence catalogs and protected pins.

H1 remains `PassedWithExplicitDeferredRisk` after explicit D1=A and D2=A. Historical evidence keeps its original classification.

Primary has incorporated Local return `6415fdf3cc384c0fb8fa7073d8b1ee3631702e0f`. Final batch-F repair source is `995dbf1003c306a69586f882ff02599db7a9780e`; matched H1-runtime control is `95b85617c92f8ce806f4652d88077936c76c3b8a`. **Both roles now use managed package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.** Authority commit `a01ac8169ccdbaacc3eec8ce81009f38eb100d64` passed R02/Linux/macOS CI 36372371088, legacy CI 36372371077 and fixed-origin CI 36372371129.

Read `Plan/CURRENT_STATUS.md`, `Handoff/WEB_TO_LOCAL.md`, and `History/M07R/R02/F_INTEGRATION_REPAIR.md`, `LOCAL_VALIDATION_TASKS.md` and `PRIMARY_VALIDATION.md` in that R02 directory. The next Local batch remains 34 required cells. Use the final verified transport HEAD in Primary's prompt, not the earlier source/CI commit. Fresh builds with the new package are required.

Primary CI is host/source validation, not Unity Player acceptance. R02 remains unaccepted until the required Local evidence and independent stage review are complete. D1/D2 require measured disposition before H2. Do not begin R03.
