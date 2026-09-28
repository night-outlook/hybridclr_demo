# HybridCLR Assembly Shadow

This is the canonical documentation root.

- `Plan/`: design, roadmap, stages and review gates.
- `Handoff/`: live Primary Implementation and Local Validation contract.
- `Architecture/`: durable design decisions.
- `History/`: historical evidence and current R02 implementation records.
- `Evidence/`: evidence catalogs and protected pins.

H1 remains `PassedWithExplicitDeferredRisk` after explicit D1=A/D2=A. Historical results keep their original classifications.

Primary has incorporated Local return `4c4f50adfd3a44073d14b107227f399c53ea605c`. The batch-G host include repair is frozen at source `af9ba49127a7e852fed504a55c733c5f6ec5e54e`, paired with control `2e8ae9f5e5fa30325a4b6225b34a602477d7aa0e`. Runtime/package pins are unchanged; both roles use package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.

Authority `5c7b9babca7257edb61976f50e3b8a51fc18abd6` passed R02 CI 36393519340, actual macOS writer/parser CI 36393519338, legacy CI 36393519418 and fixed-origin CI 36393519352. These are host/source checks, not Unity Player acceptance.

Read `Plan/CURRENT_STATUS.md`, `Handoff/WEB_TO_LOCAL.md`, and `History/M07R/R02/G_INCLUDE_REPAIR.md`, `LOCAL_VALIDATION_TASKS.md`, `PRIMARY_VALIDATION.md` and `source-targets.json`. The earlier F integration and Editor-coverage repairs remain included. The next batch remains 34 cells. Use the final verified transport HEAD in Primary's prompt rather than the earlier source/CI commit.

R02 is unaccepted until complete Local evidence and independent stage review succeed. D1/D2 require measured disposition before H2. Do not begin R03.
