# HybridCLR Assembly Shadow — isolated Primary staging branch

## STAGING ONLY — execution scalar header source

This `codex/p1-execution-scalars-20261018` demo branch documents the *next* P1 native execution scalar header implementation **without modifying the active 12-component Local Validation source tuple**. It is **not** a Local handoff, Unity SDK/Player acceptance or new milestone. Current staging validation is host CI only.

- Native staging branch `night-outlook/il2cpp_plus@codex/p1-execution-scalars-20261018`, based on exact active native source `5667e3712f49e4b38c7dd7359e57f81e344626da`, host-tested commit `39d4637b868726c92f50d1db92a5c269ff0bafe5`.
- The code introduces a new inactive `TryCaptureBoundedExecutionHeader` source method that captures only execution diagnostic scalar header values, rejects observed concurrent change/invalid coverage, and formats using the existing V1 execution header serializer.
- [Primary staging design/code review](History/M07R/R03/IR_Remediation/P1_EXECUTION_SCALARS_2026-10-18/PRIMARY_STAGING_REVIEW.md) · [Machine CI source/custody evidence](History/M07R/R03/IR_Remediation/P1_EXECUTION_SCALARS_2026-10-18/EVIDENCE.json).
- [CI 39095475904](https://github.com/night-outlook/il2cpp_plus/actions/runs/39095475904) passed 3/3 macOS/Linux compiler jobs, two strict/sanitized profiles, 13 groups/profile; 57/57 output files verified. **No Unity SDK/Player compile or run on this staging source.**

## ACTIVE Local Validation remains separately authorized

The canonical active branch is `codex/assembly-shadow-r01b-h1`, with exact committed/pushed demo SHA `25d5986c5919ab70119364ce36e8b670329ad5b0`, native SHA `5667e3712f49e4b38c7dd7359e57f81e344626da`, HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` and package `948c0e3b4f8891481301770115e8ba4945eea6de`. [Authoritative active WEB_TO_LOCAL.md](https://github.com/night-outlook/hybridclr_demo/blob/25d5986c5919ab70119364ce36e8b670329ad5b0/Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md) authorizes **one 12-component/75-native-syntax source+SDK-only batch** at THOSE commits, not the staging branch. No returned Local result is yet published for that active assignment.

**[This staging branch's WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md) contains NO executable Local assignment.** Do not use any staged source SHA for the active Local run; do not overwrite consumed evidence.

## Remaining engineering gates

P1 complete coherent live general/execution/R02 VM capture, true class pointer lifetime, global epoch, type-key/class allocation/GC/RSS, shutdown/lock safety, original getter integration remain Incomplete. P2 authenticated native/C# V2 semantic transport NotIntegrated. E0 supported Unity engine owner capability Blocked/Unavailable; E1 native maintenance/drain/restart BlockedByE0. P3 linking and runtime evidence incomplete. Historical SNAP-01/N/M/K/I/E FAIL, R02 fingerprint FAIL, strict S custody Blocked, independent R03 review FAIL/rereview NotRun and earlier source/SDK Local PASS/FAIL are unchanged.

`R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`; no Human Review Gate or milestone advancement.
