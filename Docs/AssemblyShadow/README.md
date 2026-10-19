# HybridCLR Assembly Shadow

## Current — P1 inactive owned execution/R02 source published; one new Local source/SDK-only cycle

**Most recent Local Validation** was `20261019-cmdfail-e29a`: **PASS / PassedSourceHostAndSDKOnly**, 13/13 components, 53 command-failure tests, 75/75 official Unity2022.3.62f2 arm64 native SDK syntax configurations and managed positive/expected-negative compiler receipts. It is consumed, was not a Unity Editor/Player launch and did not close P1/P2/E0/E1/full P3.

**New Primary source:** native `il2cpp_plus@f0c5afe43fe256ac09fabacd5d40f82956988fe2` fixes only the host `-I vm`/macOS libc++ `string.h` collision for the inactive owned execution/R02 runner and adds a regression. Its owned execution host [CI 39212760872](https://github.com/night-outlook/il2cpp_plus/actions/runs/39212760872) PASSED 3/3 Mac/Linux Clang/GCC after original [CI 39208403669](https://github.com/night-outlook/il2cpp_plus/actions/runs/39208403669) macOS FAIL, which remains immutable. The underlying P1 owned execution/R02 feature is still inactive and not Player-qualified.

**New demo source anchor:** `hybridclr_demo@35c5a02e90f32be4f6da8307d0a539bdf696a10f` extends candidate preflight to **14 independent components** including `owned-execution`, plus **80 C++17 arm64 native SDK syntax configurations** (16 units × five profiles). [Managed/aggregate CI 39213798210](https://github.com/night-outlook/hybridclr_demo/actions/runs/39213798210) PASSED, [command-failure CI 39213581041](https://github.com/night-outlook/hybridclr_demo/actions/runs/39213581041) PASSED, [host header syntax CI 39213944245](https://github.com/night-outlook/hybridclr_demo/actions/runs/39213944245) PASSED 2/2 Mac/Linux. No official installed SDK has yet compiled this **new** 80-unit candidate at the new source tuple.

**The next Local task is exactly ONE fresh source/host/installed SDK syntax-only cycle** governed by the final current [WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md) and four pinned remote HEADs; do not rerun the old 13-component batch or start Unity Editor/Player, runtime seven-root tests, Human Review Gate, H2/X02/M08A or other milestones.

### Required reading order
1. [Plan/CURRENT_STATUS.md](Plan/CURRENT_STATUS.md), then Local-owned [LOCAL_VALIDATION.md](Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB.md](Handoff/RETURN_TO_WEB.md).
2. [New bounded P1 design](History/M07R/R03/IR_Remediation/P1_OWNED_EXECUTION_SOURCE_2026-10-19/DESIGN.md), [Primary evidence review](History/M07R/R03/IR_Remediation/P1_OWNED_EXECUTION_SOURCE_2026-10-19/PRIMARY_REVIEW.md), and [machine evidence](History/M07R/R03/IR_Remediation/P1_OWNED_EXECUTION_SOURCE_2026-10-19/EVIDENCE.json).
3. [WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md) for exact new authorized batch and stop conditions.
4. [Remaining P1/P2/E0/E1/P3 plan](History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md).

### Explicit non-acceptance
Live general and execution getters are unchanged and allocating; a stable publication/counter fence does not prove atomic VM epoch/ABA freedom, source pointer origin, allocation/GC/RSS or Shutdown safety. P1 Incomplete, P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 Incomplete. Original SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, strict S custody Blocked, independent R03 full-stage FAIL/re-review NotRun remain factual. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
