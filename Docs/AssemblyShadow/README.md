# HybridCLR Assembly Shadow

Canonical documentation: Plan for design/stages/gates, Handoff for current assignments, Architecture for decisions and History for immutable evidence.

**Batch P remains ReturnRequired. R03-LP-001 and R03-LP-002 have published source repairs and regression coverage. The next assignment is exactly one fresh batch Q in [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md). R03 acceptance and the Human Review Gate remain open.**

P was published at demo `d9ef449e8e8aef885539e4b981243a868f8d0ba6` after execution from `d8884646659f7b6ae0f6ceda746fd271c96c8d61`: 90 cells, 71 Passed / 18 Failed / 1 Blocked; six builds and 18+754+755 Editor cases Passed with zero skips/inconclusive. All 59 Players executed: 42 verification Passed / 17 Failed. Live-policy and restored-baseline zero-root/zero-closure subproofs, seal and final custody Passed. These subproofs do not change P's failed cell or aggregate verdicts. Preserve P, O, N and all earlier evidence unchanged.

Read [CURRENT_STATUS](Plan/CURRENT_STATUS.md), Local-owned [LOCAL_VALIDATION](Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB](Handoff/RETURN_TO_WEB.md), then [LP Primary review](History/M07R/R03/LP_Repair_2026-10-06/PRIMARY_REVIEW.md), its [evidence index](History/M07R/R03/LP_Repair_2026-10-06/EVIDENCE.json), and the new handoff.

The repair commit is `b42cbe1134a56e675b8a98e275a45ae5a012e17d`. It puts authenticated resource binding before integration with an explicit dependency and uses the existing strict R02 schema bridge at all Completion M07 verification entries. Raw evidence, codec context, legacy semantics, OFF behavior and all coverage remain guarded. Real-constructor scheduling tests, strict entry-point controls and a bounded immutable P replay cover both reported defects. The replay verifies 18 original resource-observation witnesses and 289 current type-info objects; it is not new Player or full-stage acceptance.

Complete-checkout CI run **37518987943 Passed on Linux and macOS**, with **360 tests Passed per platform and zero failures/errors/skips**, plus the bounded P replay. Artifact and source hashes are authenticated in the evidence index; this is not fresh Unity/Player acceptance.

The complete source/CI anchor is `0a0974c95ad4eab2cfdaf9b9ff7e0609be67abf5`; the two CI-only commits after the repair add the required pinned package checkout and canonical test temp path. Final transport is a Docs-only descendant supplied in Primary's final prompt. All branches remain `codex/assembly-shadow-r01b-h1`. Other pins are unchanged: HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`; package `948c0e3b4f8891481301770115e8ba4945eea6de`; IL2CPP+ `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`.

Q retains 90 cells, six fresh builds, 59 fresh Players, the 18-method preflight and both 754/755 exact Editor rosters. A green Q returns `EvidenceReadyForPrimaryReview` only. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`; PureInterpreter expansion disabled. Independent full-stage review, deferred R02 CPU and H1 RSS risks, and failed unisolated warm certificates remain visible. Smoke branches remain disposable transport records, not product sources.
