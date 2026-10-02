# Current Status — R03 batch-D blockers repaired; awaiting batch E

## State and authority

R02 remains **PassedWithExplicitDeferredRisk** under its separate owner decision. R03 is in progress; no full stage or H2 acceptance is claimed.

- R02Accepted=true; mayEnterR03=true; R03Started=true.
- Latest Local publication: `33d7b1fce2f3b8463dc4ac78061250ecc7df925d`.
- Latest executed focused batch: D from demo `faa351d6854e71982ca047b994fb8579475f542a`.
- D remains ReturnRequired: **12 Passed / 5 Failed / 19 Blocked**, seal Passed.
- R03-LD-001: explicit installation-root binding implemented and host-validated; integrated revalidation required.
- R03-LD-002: isolated Editor scope defined and host-validated; actual filtered execution required. Frozen M01 resource fixture remains NoCoverage.
- Next Local cycle: **batch E requested; NotRun**.
- R03Accepted=false; H2Passed=false; PureInterpreter expansion disabled; fullLegacyRegressionAcceptance=false.

Read F_PROVENANCE_SCOPE_REPAIR.md, F_HOST_EVIDENCE.json and F_VALIDATION_MATRIX.md under `History/M07R/R03/`, then `Handoff/WEB_TO_LOCAL.md`. Local-owned reports and D/A/B/C/R02/H1 history remain unchanged; earlier handoffs are not execution authority.

## Preserved D evidence

Four successful native artifact receipts/ARM64 apps are not passed build cells: the strict recursive receipt lookup failed all four. Actual Editor recorded 754 Passed/one Ignored, not a passed aggregate. All nineteen Players were Blocked. Local authenticated 1,736 indexed files / 1,737 archive members; Primary has not accessed the retained macOS live root.

D result/index/archive hashes remain `1d24e6ccfce7cd9f8e77cd51ca0afc1d5eb3ce5a8f8af5fba60cfccf9e6d1844`, `b7bbe6d66c3c398db0fb504679cf560226aad4e044fe8a3ef04ccff3fc01e08b`, `989d7211e1772efc2b20f13b5354e533bc4760adf93fa4a45b1d5176ed17ff53`. Preserve the original live archive and ordered published parts without re-compression.

## New exact source tuple

Branch for all repositories: `codex/assembly-shadow-r01b-h1`.

| Repository | Source authority |
| --- | --- |
| night-outlook/hybridclr_demo | Tested anchor `979abd80b673e690c5f82819ed194200f8d2e536`; execute only the final docs-only transport HEAD identified by the live handoff and final Primary prompt |
| night-outlook/hybridclr | `041c0cbb42d3e64e54fe605673d99799b5d63893` |
| night-outlook/hybridclr_unity | `120bb01be680cec0375002a0823552d66d34b84c` |
| night-outlook/il2cpp_plus | `1abb6bcaa85226f08c67f9da65edb3c58e8cb399` |

Implementation commit `1b89581a802a660057fd507f4deb65f060b29669` introduces receipt schema 2 and strict isolated Editor scope. Anchor `979abd80...` corrects a new host-audit assumption about reference inventory counts; the production verifier had no fixed count. Only Docs/AssemblyShadow documentation/evidence may differ after the tested anchor. Do not infer the final transport SHA from an earlier record; resolve the latest commit touching WEB_TO_LOCAL.md and require local/remote/prompt equality.

## Completed Primary checks

Host workflow **36926248759** passed Linux x86_64 and macOS arm64 with SDK 8.0.318: **116 Python contracts**, both 9-case graph suites, 35 admission/method cases, 15 Player inputs, 33 fixture audits/consumers, Runtime API compilation, shared compiler lifecycle, and recorded-D provenance/scope audit. Each platform retained 49 positive and two expected-negative commands, all clean. The exact 754-name catalog is verified; that is not fresh Editor execution.

Pinned-API workflow **36926248750** compiled the entire updated helper and actual package dependencies using Unity 2022.3.62f2 compiler/API bytes. The helper had zero errors/warnings; the unchanged original C helper still produced exactly its two CS0266 errors. All five commands completed without survivors. Primary authenticated the three downloaded final archives: host 629 indexed / 630 ZIP files each, API 28 / 29. See F_HOST_EVIDENCE.json for hashes, IDs and scope limits.

## Next Local action

Run once in prescribed unused root `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001E-provenance` using the exact tuple/environment in WEB_TO_LOCAL.md. Never retry A/B/C/D or reuse an existing root. Keep all 36 cells, four new native builds and nineteen fresh-process Players. The 754 selected Editor cases must all pass with no skips; the single unavailable M01 asset test remains explicitly excluded/NoCoverage. No Local source, schema, filter, expectation, timeout or cleanup changes are authorized.

Success means EvidenceReadyForPrimaryReview with all 36 cells and the focused seal Passed, not R03/H2 acceptance. Otherwise return ReturnRequired with factual evidence. Local updates/pushes its reports and a new immutable E checkpoint, then stops for Primary reconciliation.

## Remaining stage obligations

Actual frozen-M01 and broader old-resource regressions, broader method/generic/delegate/interface/stack-trace coverage, startup/capacity/performance/memory, gated PureInterpreter qualification and independent full R03 review remain Primary-owned. R02 deferred CPU residuals and original H1 RSS risk remain visible through H2. This focused scope correction does not authorize release or waive full-stage resource coverage.
