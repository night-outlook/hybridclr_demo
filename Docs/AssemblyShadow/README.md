# HybridCLR Assembly Shadow

This is the canonical documentation root.

- `Plan/`: design, roadmap, stages and normative review gates.
- `Handoff/`: live Primary Implementation / Local Validation coordination.
- `Architecture/`: durable decisions.
- `History/`: immutable evidence, implementation and review records.
- `Evidence/`: protected fixture and artifact catalogs.

**R02 is accepted as `PassedWithExplicitDeferredRisk`.** Batch I completed 34/34 required cells, independent stage review returned PASS with zero findings, and the owner explicitly selected `R02-D1=A, R02-D2=A`.

**R03 is now in progress.** Primary implemented the conservative layout-admission, logical-method-identity and baseline/target graph candidate plus a source-bound 36-cell Local Validation batch. No Unity/IL2CPP Player execution of this R03 candidate has been accepted yet, PureInterpreter structural expansion remains disabled, R03 is not accepted, and H2 has not passed.

Read, in order:
- `Plan/CURRENT_STATUS.md`
- `Plan/stages/R03-evolution-semantics.md`
- `History/M07R/R03/A_PRIMARY_IMPLEMENTATION.md`
- `History/M07R/R03/A_VALIDATION_MATRIX.md`
- `History/M07R/R03/B_PRIMARY_HANDOFF.md`
- `Handoff/WEB_TO_LOCAL.md`

The R03 host-CI execution anchor is demo `f5f5712459fdf67e2b748ddeab8e6540bffd3d95` with external source pins:
- HybridCLR `041c0cbb42d3e64e54fe605673d99799b5d63893`
- managed package `120bb01be680cec0375002a0823552d66d34b84c`
- IL2CPP `1abb6bcaa85226f08c67f9da65edb3c58e8cb399`

The later demo commits through this handoff are documentation/coordination transport only. Local Validation must execute the exact current remote HEAD of `codex/assembly-shadow-r01b-h1` and must verify that the post-anchor delta is documentation-only before running.

R02-D1 CPU residuals and the original H1 +18–19 MiB RSS risk remain visible through H2. Neither R02 acceptance nor this focused R03 batch is a production SLA, RAM-budget approval, release acceptance, or H2 approval.
