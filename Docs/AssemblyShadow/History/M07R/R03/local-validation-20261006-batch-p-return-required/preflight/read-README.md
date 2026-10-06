# HybridCLR Assembly Shadow

Canonical documentation: Plan for design/stages/gates, Handoff for current assignments, Architecture for decisions and History for immutable evidence.

**R03 completion batch O remains ReturnRequired. Primary Implementation has published repairs for R03-LO-001–004 plus an integrated live source-versus-linked policy-domain guard. The next owner is Local Validation for exactly one fresh completion batch after reading `Handoff/WEB_TO_LOCAL.md`. Full R03 acceptance and the Human Review Gate remain open.**

Batch O was published at demo `7025f1026fd61f101a81fbafafb999095aa8604e`: 90 cells, 58 Passed / 30 Failed / 2 Blocked; six fresh builds Passed; the 18-method preflight and full 754/755 Editor rosters Passed with zero skips/inconclusive; all 59 Players executed with 30 verifications Passed and 29 Failed; seal and final custody Passed. Preserve O, N and every earlier result/evidence state unchanged.

Primary repair sequence on `codex/assembly-shadow-r01b-h1`:

- `ed615c91303ebee0078da00e01208c02b255cb61`: separates source/compiler and linked-Player policy domains; restores codec context; canonicalizes linked-DLL lookup; restores the methods/image-record consumer contract.
- `7b148aa8cace4af4cb1d7a4219c4f79fe0182394`: corrects the LO-001 regression fixture so authenticated reported source edges are not inferred from emitted DLL `AssemblyRef` metadata.
- `9c4b76a540e74c045cabaf9e700051512a75cead`: adds fresh integrated Unity source-policy validation plus the guarded linked-policy negative control and binds that evidence into production-entry integration.
- `8db761455dfd73ef01eac7d48eb39c69ca253cf8`: CI-only change raising the pinned-API job budget from 60 to 120 minutes after a source-matched run exhausted the old budget during the unchanged N reference replay.

Other source pins are unchanged: HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`; HybridCLR Unity package `948c0e3b4f8891481301770115e8ba4945eea6de`; IL2CPP+ `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`.

Primary pre-handoff checks: the bounded selected Python suite passed 102 tests with zero failures/errors/skips; the published `7b148aa…` host and pinned-API workflows Passed; source-matched `9c4b76a…`/`8db76145…` workflow evidence is recorded in `History/M07R/R03/LO_Continuation_2026-10-06/PRIMARY_REVIEW.md`. The mandatory GitHub Connector write/readback smoke test Passed in all four repositories. Connector branch deletion is unavailable, so the disposable smoke branch `codex/connector-smoke-20261006-primary-r03` remains recorded rather than silently treated as cleaned up.

Read `Plan/CURRENT_STATUS.md`, `Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md`, `History/M07R/R03/LO_Continuation_2026-10-06/PRIMARY_REVIEW.md`, then the new assignment in `Handoff/WEB_TO_LOCAL.md`.

`R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; PureInterpreter expansion remains disabled. A green next Local batch is evidence for Primary review, not automatic stage or Human Review Gate approval.
