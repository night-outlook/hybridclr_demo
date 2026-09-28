# Current Status — batch-F repair finalized; awaiting Local Validation

- Input Local return: `6415fdf3cc384c0fb8fa7073d8b1ee3631702e0f`.
- H1: `PassedWithExplicitDeferredRisk`; D1=A and D2=A remain development-stage risk deferrals.
- Current executable/tool source: `1642392278a97bc9348195e35ec5d1b7fb6fa530`.
- CI-tested candidate authority: `4a6a8d604e27aa5e3175149c4df0170b8ec09b05`.
- Candidate branch: `codex/assembly-shadow-r01b-h1`.
- Matched control: `codex/r02-h1-runtime-control@028ad68fa25a531be07f11f1fdcc417842f98ab4`.
- HybridCLR, both roles: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`.
- Managed package, both roles: `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.
- Candidate/control IL2CPP: `3981da12f2cd3ee878a04dda6f573d0ad3faeda5` / `6be7f38bec2fa4677d24efc1a4a1294240789933`.
- R02Accepted=false; mayEnterR03=false.

## Implemented disposition

All five batch-F integration repairs are published: strict optional R02 native/managed diagnostics schema and linked proof, M07 early capsules, count-family-specific auditors, scoped linker restoration, and stable forensic snapshots with exact archive recovery. The new package is required in both workspaces; prior F graphs cannot be reused as new-package builds.

The resumed audit found one additional acceptance gap: the batch enforced only two existing Editor tests although three new schema tests were required. The final runner now requires exactly one Passed record for every one of the five exact full names, a Passed overall NUnit run, and no failed/inconclusive cases. Missing, skipped, duplicated or misnamed required tests reject the cell. `editor-tests.json` includes `requiredCases` and binds the full XML. Seven added host tests exercise this behavior. The batch remains 34 cells.

The control has the current source as explicit ancestry and differs from that source tree only in the source-pin file. Candidate post-source commits change only permitted metadata. No source allowlist, semantic expectation, production runtime, timeout or performance schedule was relaxed.

## Selected final Primary evidence

All selected workflows tested authority `4a6a8d604e27aa5e3175149c4df0170b8ec09b05`:

- R02 workflow 36387357718: Linux and macOS Passed; Python 210/210; macOS repeated subset 79/79; native-writer/package-parser 1,310 checks; native matrices 70/70 each; managed Baseline/P01/P03 102/111/111 assertions with clean process groups.
- Legacy workflow 36387357712: 384/384 current reusable/rejection tests, 6/6 fixed-H1 positives, remaining R01/M07/R01B workflow steps Passed.
- Origin workflow 36387357717: immutable M00 archive/member/compact-fixture provenance Passed.
- Four downloaded artifact sizes/digests/CRCs, 3,278 source files and 137 unique nested bindings authenticated. Both final changed executable blobs match the tested export.

`PRIMARY_VALIDATION.md` and `F_COVERAGE_VALIDATION.json` record exact artifacts, results and limits. The earlier `F_PRIMARY_VALIDATION.json` remains evidence for its earlier authority, not this final coverage change.

## Next Local cycle

Run one new unused 34-cell `R02LocalBatch-v1` from the final verified candidate transport and fixed control above. Cover all fresh builds, eight sidecars, four pilot plus forty formal A/B pairs, five required Editor contracts, affected regressions, D1/D2 measurements, final source checks and complete sealing. Independent stage review is eligible only after the required evidence succeeds.

No new Unity/Player execution or actual Editor-test execution occurred in Primary. The old F result remains 22 Passed, 8 Failed and 4 Blocked followed by failed sealing; its preservation inventory is not a complete seal. Preserve A/B/C/D/E/F and H1 evidence. Return non-trivial failures to Primary without local source changes. Stop before R03.
