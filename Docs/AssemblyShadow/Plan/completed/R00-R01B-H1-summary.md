# R00–R01B and H1 Status

R00 and R01 established the reviewed baseline and capacity/failure contract. R01B implemented the metadata-index expansion and subsequent H1 remediation.

H1 remains **InProgress**. The latest Local cycle closed V04 historical compatibility/reanalysis at source d61 with complete source/test validation and source-27df live evidence reauthentication; no Player was rerun.

Current Primary defines `H1AnalysisOnlySuccessorEvidence-v1` for V05. It preserves source-27df execution as `ReusedAuthenticatedFromSource27df`, current source/test checks as `FreshCurrentSourceValidation`, and historical performance as `ReanalyzedImmutableHistoricalExecution`. V05 success only makes the package eligible for a genuine independent M08 review.

The historical independent M08 result remains **FAIL** until a new independent review is actually executed. A new M08 PASS may change the state only to `ReadyForHumanReviewGate`; it does not set `humanGatePassed=true` and does not permit R02. Explicit human H1 approval remains mandatory.

Current live status and exact repository/source pins are authoritative in `../CURRENT_STATUS.md` and `../../Handoff/source-targets.json`. Historical R01B/H1 material remains immutable under `History/M07R/`.
