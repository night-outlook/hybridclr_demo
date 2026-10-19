# HybridCLR Assembly Shadow

## Current — P1 failure-aware source/SDK handoff published; one Local cycle authorized

**Primary Implementation has published the command-failure receipt/fail-stop tooling and one new 13-component Local Validation assignment on `codex/assembly-shadow-r01b-h1`.** Do not use the old consumed 12-component command. The latest factual Local return, [`20261018-5667`](Handoff/LOCAL_VALIDATION.md), was **PASS / PassedSourceHostAndSDKOnly (12/12, 75/75 native SDK syntax)** and is consumed, not a Player/runtime acceptance result.

### Current primary source and evidence

- Native tooling and source-only command tests: `night-outlook/il2cpp_plus@e29a38f66331ccabe5822a9f83401cd4a2b20c5a`. This is based on an additional independent inactive native frozen-execution/R02 owned-record commit `d8a1df3007e93aeb65dd9fe97ab96b4771de8f17`; the new feature remains separately unqualified by this batch.
- Demo source/test/CI and preserved Primary findings: `night-outlook/hybridclr_demo@d67846e9a28add70046198da9a4fba7e27f0764b`. The final Docs-only handoff-containing commit is the current verified remote branch HEAD, to be matched with the Primary prompt.
- Unchanged `night-outlook/hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55` and `night-outlook/hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`.
- [Primary design](History/M07R/R03/IR_Remediation/P1_COMMAND_FAILURES_2026-10-19/DESIGN.md), [source review](History/M07R/R03/IR_Remediation/P1_COMMAND_FAILURES_2026-10-19/PRIMARY_REVIEW.md), [host evidence](History/M07R/R03/IR_Remediation/P1_COMMAND_FAILURES_2026-10-19/EVIDENCE.json), [publication reconciliation](History/M07R/R03/IR_Remediation/P1_COMMAND_FAILURES_2026-10-19/PUBLICATION.md).

Primary reproduced loss of timeout output and continued outer batch work after timeout in the original source. The published Python tooling retains failed/partial/unavailable stream receipts, refuses duplicate-key/nonfinite/symlink-redirected component JSON, stops later components when command lifetime is unverified, labels them `NotRun`, and reports SDK compilation only on real successful compiler receipts. It does **not** provide a descendant-process quiescence proof. Native and managed production runtime/getter/guard/serializer/compiler helpers remain unchanged by this increment.

Fresh Primary **host-only** regression execution: **53/53 unique tests PASS**, 0 skips/errors/failures, plus 3 admission refusals; actual controlled Python subprocesses and mocked compiler/Git/VM fixtures. The new focused [demo command-failure CI](https://github.com/night-outlook/hybridclr_demo/actions/runs/39208716350) and [native command-failure CI](https://github.com/night-outlook/il2cpp_plus/actions/runs/39208403729) both passed. An independent [inactive owned-execution CI](https://github.com/night-outlook/il2cpp_plus/actions/runs/39208403669) has a macOS Clang failure; it is outside this batch and remains a Primary-owned follow-up. Official installed Unity2022.3.62f2 SDK syntax validation of these new Python tooling changes is delegated only as described in [WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md). No Player, Editor, linked execution, shutdown, GC/RSS, or Human Review Gate acceptance is claimed.

### Mandatory read order

1. [Plan/CURRENT_STATUS.md](Plan/CURRENT_STATUS.md), then Local-owned [LOCAL_VALIDATION.md](Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB.md](Handoff/RETURN_TO_WEB.md).
2. The [Primary review](History/M07R/R03/IR_Remediation/P1_COMMAND_FAILURES_2026-10-19/PRIMARY_REVIEW.md) and its [publication note](History/M07R/R03/IR_Remediation/P1_COMMAND_FAILURES_2026-10-19/PUBLICATION.md).
3. [WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md) for exact pinned source, one-shot validation command, evidence and stop boundary.
4. The [remaining production implementation plan](History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md).

### Original failures and remaining gates unchanged

The existing native `TryCaptureBoundedGeneralLive` remains **inactive**, original getters unchanged. A stable observed fence is not a coherent all-VM epoch; provenance, ABA, full execution/R02 capture, allocation/GC/RSS, metadata Shutdown/lock safety remain P1 incomplete. P2 native/C# authenticated V2 integration remains NotIntegrated. E0 supported StandaloneOSX owner-safe point is Blocked/Unavailable, E1 BlockedByE0; full P3 linked Player/runtime acceptance incomplete. Original SNAP-01/N/M/K/I/E FAIL, historical R02 immutable-fingerprint FAIL, strict original S custody Blocked and independent R03 full-stage FAIL/re-review NotRun are preserved. Earlier P1 `20261016-3dc9`, `20261016-f598`, `20261016-0620` source/SDK PASS and `20261016-0a0b` FAIL remain consumed.

`R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. No new runtime cycle, Human Review Gate or later milestone is authorized.
