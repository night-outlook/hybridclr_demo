# HybridCLR Assembly Shadow

## Current — P1 managed receipt correction; separate Local successor pending

The `20261016-0a0b` source/SDK cycle is consumed and remains **FAIL / FailedOrIncomplete: 9 Passed, 1 Failed**. Actual managed compilation (five products plus the expected-negative control) and all 70 native syntax configurations Passed; the outer managed cell failed because Primary's wrapper checked the wrong receipt path. The [Local report](Handoff/LOCAL_VALIDATION.md) and [return](Handoff/RETURN_TO_WEB.md) remain authoritative factual records, unchanged by Primary.

Primary corrected `IR-LOCAL-P1-MANAGED-RECEIPT-01` at demo source/CI commit **`06209426b765a805da2cc2f810ba5da390787099`**. The wrapper now binds the producer's exact `managed-sdk/build-api/results.json` path, returned SHA-256, receipt identity and inner verdict. No root-level fallback or exit-only success is accepted. Native code, both SDK compiler procedures and historical source pins are unchanged.

[CI 38859685370](https://github.com/night-outlook/hybridclr_demo/actions/runs/38859685370) Passed on macOS/Linux: **18 host tests each**, including the five original CLI checks and thirteen new consumer/orchestration regressions. Original artifact ZIP hashes and all ten manifest-declared files were independently verified. The tests use mocked Git/SDK/child processes; they are not new Unity or SDK execution.

## Read order

1. [Current plan and status](Plan/CURRENT_STATUS.md).
2. [LOCAL_VALIDATION](Handoff/LOCAL_VALIDATION.md), then [RETURN_TO_WEB](Handoff/RETURN_TO_WEB.md).
3. [Primary correction and review](History/M07R/R03/IR_Remediation/P1_MANAGED_RECEIPT_2026-10-16/PRIMARY_RECONCILIATION.md), [machine evidence](History/M07R/R03/IR_Remediation/P1_MANAGED_RECEIPT_2026-10-16/EVIDENCE.json), and [raw test logs](History/M07R/R03/IR_Remediation/P1_MANAGED_RECEIPT_2026-10-16/HOST_TEST_LOGS.txt).
4. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md), the sole current execution authorization. It defines a **new one-shot source/SDK-only successor**, exact source identity checks, unused roots and stop conditions. Do not repeat the consumed cycle or execute an old command from history.

## Remaining engineering gates

P1 complete coherent bounded live VM capture, allocation/GC/RSS and shutdown/lock safety are unfinished. P2 V2 native/C# semantic integration is NotIntegrated. E0/E1 Unity engine-owner lifecycle remains unresolved. SDK syntax success is not linking, Player execution, deadlock freedom or R03 acceptance. Primary owns all nontrivial implementation; Local owns only factual validation and bounded environmental diagnosis.

**No Unity Editor/Player launch, runtime seven-root batch, Human Review Gate or H2/X02/M08A is authorized.** `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. All historical SNAP-01 and other FAIL/Blocked states are preserved.

## History and source authority

All four canonical `night-outlook` repositories use `codex/assembly-shadow-r01b-h1`. The native source stays `0a0b70156e75d450d75d0bcfd9132843b8abbbb0`; HybridCLR stays `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`; the Unity package stays `948c0e3b4f8891481301770115e8ba4945eea6de`. Final demo handoff HEAD includes documentation-only publication after the tested source anchor; WEB_TO_LOCAL verifies that distinction without an unknown SHA placeholder.

The [previous complete index at the returned Local revision](https://github.com/night-outlook/hybridclr_demo/blob/1abf5df96c61e8f5bd870d6b03a93e33f44182f5/Docs/AssemblyShadow/README.md) retains the detailed earlier P1 increments and immutable evidence links. Those old status/authorization paragraphs are historical, not instructions to run another batch. The [remaining P1/P2/E0/E1/P3 implementation plan](History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md) and [engine-owner capability assessment](History/M07R/R03/IR_Remediation/SNAP01_EXECUTION_FORMATTER_2026-10-15/ENGINE_OWNER_CAPABILITY_ASSESSMENT.md) remain in force.
