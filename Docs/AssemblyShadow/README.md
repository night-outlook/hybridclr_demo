# HybridCLR Assembly Shadow

This is the canonical documentation root.

- `Plan/`: design, roadmap, stages and normative review gates.
- `Handoff/`: live Primary Implementation / Local Validation coordination.
- `Architecture/`: durable decisions.
- `History/`: immutable evidence, implementation and review records.
- `Evidence/`: protected fixture and artifact catalogs.

**R02 remains accepted as `PassedWithExplicitDeferredRisk`. R03 is in progress; H2 has not passed.**

## Current cycle: managed lifetime repair → R03 Local batch B

Local batch A returned **4 Passed / 3 Failed / 29 Blocked**, with its focused evidence seal Passed. Three managed builds exited 0 but left surviving process groups, so the runner stopped before host assertions. Unity, EditMode and all nineteen Player cases remain Blocked/NotRun for A. Its exact Local return is `2a9fdec813592fd79db511d5db96a6dcf1dea620`; the original reports and checkpoint remain unchanged.

Primary repaired the per-invocation managed build lifetime policy without weakening survivor rejection. The new same-wrapper host regression passed on Linux x86_64 and macOS arm64 with .NET SDK 8.0.318; its final artifacts were downloaded and authenticated. This permits a fresh focused Local batch B, not acceptance of A, R03, Unity/native behavior or H2.

Read in this order:
- `Plan/CURRENT_STATUS.md`
- `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` for preserved A facts
- `History/M07R/R03/C_LIFETIME_REPAIR.md`
- `History/M07R/R03/C_HOST_EVIDENCE.json`
- `History/M07R/R03/C_VALIDATION_MATRIX.md`
- `Handoff/WEB_TO_LOCAL.md` for the new exact execution handoff

The product design remains in `Plan/DESIGN.md`, `Plan/stages/R03-evolution-semantics.md`, and `History/M07R/R03/A_PRIMARY_IMPLEMENTATION.md`. Earlier `A_VALIDATION_MATRIX.md` and `B_PRIMARY_HANDOFF.*` remain historical records; their old source anchor/output root must not override the current handoff.

New demo executable/CI source anchor: **`7e2852fcd6c5bd9ebc82f2b3f97516742b772dc2`**. The final demo handoff is its documentation-only transport descendant, identified by Primary's exact prompt and the current `WEB_TO_LOCAL.md`. All four repositories use branch `codex/assembly-shadow-r01b-h1`.

Unchanged external pins: HybridCLR `041c0cbb42d3e64e54fe605673d99799b5d63893`, managed package `120bb01be680cec0375002a0823552d66d34b84c`, and IL2CPP `1abb6bcaa85226f08c67f9da65edb3c58e8cb399`.

Batch B keeps the original **36 cells / four isolated builds / nineteen fresh-process Player cases**; the existing Python verifier cell now includes the additional lifetime regressions. Use only the unused B root prescribed in `WEB_TO_LOCAL.md`. Never retry A or repair failed evidence in place.

`R03Accepted=false`; `H2Passed=false`; PureInterpreter structural expansion remains disabled. R02-D1 CPU residuals and the original H1 +18–19 MiB RSS risk remain visible through H2. Broader R03 regressions, measurement, PureInterpreter qualification and independent stage review remain Primary-owned; this focused handoff does not waive them.
