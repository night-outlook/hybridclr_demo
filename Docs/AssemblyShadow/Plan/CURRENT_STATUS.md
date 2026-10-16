# Current status — managed receipt correction; new Local successor pending

## Latest factual Local outcome

The source/SDK cycle `20261016-0a0b`, published at demo `1abf5df96c61e8f5bd870d6b03a93e33f44182f5`, is **consumed: FAIL / FailedOrIncomplete, 9 Passed / 1 Failed**. Its managed child exited 0 and wrote a valid Passed receipt under `managed-sdk/build-api/results.json`; the wrapper instead looked for `managed-sdk/results.json`. The original outer cell, aggregate, and `officialUnitySdkCompilePassed=false` are unchanged.

Local's actual five managed products plus expected-negative control, all **70 native syntax configurations**, and nine passing outer components remain factual scoped evidence. SDK/source/prior evidence preservation was reported Passed. The retained warnings (68 managed, 742 native occurrences) were not suppressed. Primary read the returned records and audit, not a fresh execution of those SDK commands or a complete rescan of Local's external evidence.

[LOCAL_VALIDATION](../Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB](../Handoff/RETURN_TO_WEB.md) are Local-owned. [Original checkpoint](../History/M07R/R03/local-validation-p1-metadata-source-20261016-0a0b/README.md).

## Primary correction and verification

**Finding `IR-LOCAL-P1-MANAGED-RECEIPT-01`: fixed in source; fresh Local verification pending.** Demo source/CI anchor: `06209426b765a805da2cc2f810ba5da390787099` on `codex/assembly-shadow-r01b-h1`. The exact nested path, returned SHA-256, managed receipt kind/schema/scope and actual verdict are now joined by the consumer; child exit 0 alone cannot pass. Missing, altered or malformed data and failed child/inner results remain failures.

The actual aggregate success regression fails against the original source and passes against the correction. Thirteen new consumer/orchestration tests Passed in Primary. [CI 38859685370](https://github.com/night-outlook/hybridclr_demo/actions/runs/38859685370) Passed **2/2 jobs, 18 tests each** on Linux/macOS (five existing plus thirteen new). Both artifact ZIP hashes and all ten declared files were verified. Tests mock Git, SDKs and child commands; actual producer receipt expressions are source-derived. No fresh SDK or Unity run follows from CI.

[Correction design/review](../History/M07R/R03/IR_Remediation/P1_MANAGED_RECEIPT_2026-10-16/PRIMARY_RECONCILIATION.md), [machine evidence](../History/M07R/R03/IR_Remediation/P1_MANAGED_RECEIPT_2026-10-16/EVIDENCE.json), [raw host test logs](../History/M07R/R03/IR_Remediation/P1_MANAGED_RECEIPT_2026-10-16/HOST_TEST_LOGS.txt).

## Work ownership and gates

| Area | Current disposition |
| --- | --- |
| Managed receipt consumer | Source corrected and host-tested; separately authorized Local successor NotRun |
| Native/managed official SDK compilation | Passed within the consumed Local syntax/API scope; aggregate remains Failed; new successor results pending |
| P1 coherent bounded live VM capture | Incomplete; original getter integration, global epoch, allocation/GC/RSS, lock/shutdown safety remain Primary-owned |
| P2 authenticated native/C# V2 semantic integration | NotIntegrated |
| E0 Unity2022.3.62f2 StandaloneOSX engine-owner capability | Blocked/Unavailable |
| E1 native scheduler, maintenance, drain and restart | BlockedByE0 |
| Full P3 integrated runtime preparation | Incomplete; 70-unit syntax is not linking or runtime evidence |
| Player execution / independent full-stage re-review | NotRun for this correction; historical R03 full-stage review remains FAIL |

The current [WEB_TO_LOCAL](../Handoff/WEB_TO_LOCAL.md) authorizes **one new ten-component host/SDK-only cycle** using unused roots. No previous root may be retried, renamed or promoted. Nontrivial changes remain Primary-owned. After the new cycle, Local must publish factual evidence and return to Primary; it may not enter another milestone or approve a Human Review Gate.

Native code and compiler procedures are unchanged by this correction: native `0a0b70156e75d450d75d0bcfd9132843b8abbbb0`, HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package `948c0e3b4f8891481301770115e8ba4945eea6de`. Historical source-pins.json stays unchanged. Final demo transport HEAD may contain only Docs publication after the source anchor; the handoff resolves and verifies that exact HEAD.

## Immutable history and acceptance

SNAP-01 remains FAIL/ReturnRequired (14/18 cells Passed; three ON files empty after original slot14 limit 262144 was exceeded, scanned prefix262145 only; exact real full length Unavailable). The engine witness still failed with 51213 uncapped reports/500ms and exit71. N/M/K/I/E remain FAIL; strict original S custody remains Blocked; independent full-stage R03 FAIL/re-review NotRun is unchanged.

V1 text limit262144; V2 frame65536, artifact3932160, envelope262144 and combined encoded4194304 are unchanged. No truncation, count cap/coalescing, sleeps, finalizer suppression or altered semantic predicate is permitted.

`R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. No Unity Editor/Player runtime, H2/X02/M08A or Human Review Gate.

The [previous full status snapshot](https://github.com/night-outlook/hybridclr_demo/blob/1abf5df96c61e8f5bd870d6b03a93e33f44182f5/Docs/AssemblyShadow/Plan/CURRENT_STATUS.md) preserves older detailed P1 progress. Its old permission/status paragraphs are historical. The [remaining Primary implementation plan](../History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md) remains the engineering roadmap.
