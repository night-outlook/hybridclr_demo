# Current Status — R03 LI contracts repaired; batch J prepared

## Authoritative state

- R02 remains PassedWithExplicitDeferredRisk; focused H remains reconciled Passed.
- Latest Local publication: demo `c16f39ec204876e3fd569f75c7b2e7dabc8c3913`.
- Latest executed completion batch: I, from demo `c579e75eadef58ca484b35ffee03e435a925d781`.
- I remains ReturnRequired: **40 Passed / 2 Failed / 48 Blocked**, seal Passed. Focused Editor remains 736 Passed / 18 Failed / zero skips; all 23 executed focused Players Passed. Resource builds/Editor and 36 downstream Players were Blocked.
- LI-001 and LI-002 source repairs are implemented and host/compiler checked. Their integrated closure awaits J.
- R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; qualificationApproved=false.
- PureInterpreter expansion disabled; fullLegacyRegressionAcceptance=false. Historical M01 NoCoverage is not upgraded.
- **Next owner: Local Validation only for the new exact batch J in WEB_TO_LOCAL.md.**

## Read and source authority

Read `History/M07R/R03/L_CONTRACT_REPAIR.md`, `L_HOST_EVIDENCE.json`, `L_VALIDATION_MATRIX.md`, then `Handoff/WEB_TO_LOCAL.md`. The original Local return and all A–I checkpoints are unchanged. K's measurement protocol and ADR-0002 qualification boundary still apply.

Branch in all four repositories: `codex/assembly-shadow-r01b-h1`.

| Repository | Repair implementation/source pin |
| --- | --- |
| hybridclr_demo | Executable/CI anchor `8d5297c375201687d17b91843ea0250ed90c0095`; final documentation-only handoff must match Primary's prompt and local/remote HEAD |
| hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` — unchanged |
| hybridclr_unity | `c86cbf665f5fcb2137e5adf2960541ce492467a4` |
| il2cpp_plus | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` — unchanged |

Package changes are restricted to synthetic policy fixture construction; production source/qualification/ownership/native guards are unchanged. Demo fixes source-pin generation, adds constructor and actual-consumer preflights, strengthens tests and binds the new package revision.

## Completed Primary checks

At the exact anchor, workflow **37116804583** Passed on Linux and macOS: 73 completion-tool Python tests, 183 retained verifier tests, 12 actual-helper constructor contracts, 32 qualification, 9+9 graph and 35 admission contracts per host. All 12 owned commands per host completed cleanly.

Workflow **37116804600** Passed: complete resource helper/dependencies including the new source-pin consumer compiled against Unity2022.3.62f2 APIs, **16 assemblies / 650 sources / 16 clean successful compiler commands**. The 907 warnings, including 17 new serialized/default-field CS0649 warnings, are retained; no all-source warning-free claim is made. Pinned Core RP compiler-source metadata is not claimed byte-equivalent to Local UPM packages.

All three final archives were independently authenticated: each host 447 indexed files / 448 ZIP files; API 118 indexed / 119 ZIP files. All indexed bytes, unique membership, sources, command streams and verdicts match. Fourteen uploaded demo source files and three corrected package fixture files match the compiler artifact; the remaining metadata/workflow blobs were checked through Connector.

These are host/compiler checks. **Actual early Editor and production JsonUtility execution have not run in Primary.**

## Batch J

The new root is `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261003J-contracts`. Require the original **90 cells / six fresh builds / 59 fresh Players**, full zero-skip 754/755 Editor selections, plus an additional early 18-method Editor subset and ten actual source-pin consumer checks in existing prerequisite cells. Neither preflight replaces downstream coverage. Native counters, producer lease, expected rejections, C07 success and measurement rules are unchanged.

Any Failed/Blocked cell or failed seal returns ReturnRequired. All 90 Passed with a Passed seal returns EvidenceReadyForPrimaryReview, not stage/gate approval. No I rerun or historical app reuse is authorized.

After Local returns, Primary reconciles the result, fixes substantive findings and completes the full R03 exit matrix and independent design→plan→implementation→evidence review. Unrepresented generic/interface/old-handle/qualification/production-risk obligations remain open. Only after the documented exit conditions may the project become Ready for the separately user-initiated H2. Do not enter M08A automatically; retain R02 deferred CPU and H1 RSS risks.
