# Primary Implementation → Local Validation — CLOSED (oneuse-07 consumed)

Date: 2026-11-07 UTC. **No Local Validation build, Player, runner, repair, cleanup or retry is presently authorized.**

The previous `R03IR-Initializer-20261107-oneuse-07` single-use 15-cell batch ran exactly once, with execution demo `6e1dc7b4349a386dc35c5ed46fca4225db273b18`. The Local publication demo commit is `66a0218ffb17e363531b7f7bc0f4114787ae0b76`. The verified result is **focused initializer PASS (15/15 cells)**, not R03 acceptance. The previous `WEB_TO_LOCAL.md` was consumed; do not copy its old invocation or reuse its output roots.

## Required read order (for review, not execution)

1. `Docs/AssemblyShadow/README.md` and `Plan/CURRENT_STATUS.md`.
2. `History/M07R/R03/local-validation-initializer-20261107-oneuse-07/{README.md,LOCAL_RESULT.json,local-evidence/FINAL_INDEPENDENT_AUDIT.json}` and original raw Player records.
3. Local-owned `Handoff/RETURN_TO_WEB.md`, oneuse-07 section. The Local-owned `Handoff/LOCAL_VALIDATION.md` is **empty** in the published repository; use actual checkpoint/RETURN_TO_WEB facts, and do not invent a Local record.
4. `History/M07R/R03/IR_Remediation/POST_INITIALIZER07_2026-11-07/{PRIMARY_RECONCILIATION.md,NEXT_PRIMARY_WORK.md}`.

The original oneuse-07 **historical** instructions are retrievable at
`night-outlook/hybridclr_demo` commit
`6e1dc7b4349a386dc35c5ed46fca4225db273b18`,
`Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`. They are not a live authorization.
The historical oneuse-06 file referenced there as `RUNTIME_FINDINGS.json` was
incorrectly named: the published finding is
`History/M07R/R03/local-validation-initializer-20261107-oneuse-06/local-evidence/FINDING.md`,
with `BRIDGE_FINDING.json`. Neither error changes previous evidence.

## Source authority (fixed four-repository branch)

All on `codex/assembly-shadow-r01b-h1`:
- `night-outlook/hybridclr_demo`: current pushed Primary `HEAD` must be verified against GitHub Connector; current *runtime execution source*, not a new HEAD assertion, was `6e1dc7b4349a386dc35c5ed46fca4225db273b18`.
- `night-outlook/hybridclr`: `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`.
- `night-outlook/hybridclr_unity`: `948c0e3b4f8891481301770115e8ba4945eea6de`.
- `night-outlook/il2cpp_plus`: `41764ae1eeefb33b05966e7f7676e52aae39c340`.

The oneuse-07 record proves a real linked Bi4 phase103=1 and native
299/300 callback once per Player, field3/mask15, control0/6 and the
postprepared failure19/9 sentinel in distinct successful Players.
It does not identify the postterminal AOT denial mechanism,
implement native snapshot V2, or prove physical captured generic error15.

## Next responsibility and explicit stop

**Primary Implementation retains ownership.** Further design, implementation,
native V2 instrumentation, captured-generic real test stimulus, host tests,
documentation, and source-bound CI belong to Primary.
Local Validation may read/inspect the published checkpoint but
must not execute another build or Player until a separately reviewed,
fully prepared, committed/pushed, exact-source new `WEB_TO_LOCAL.md`
explicitly authorizes a new single-use cycle with fresh roots and machine,
Git, SDK, history/custody and capacity gates.

The 17 user-authorized retired runtime roots and 40 duplicate paths
remain `Unavailable/PermanentlyDeleted`. Historical strict custody
remains `Blocked` and historical verdicts are not overwritten.
The independent R03 review remains **FAIL** with High `IR-R03-01/02`
open. `R03Accepted=false`; `H2Passed=false`;
`ReadyForHumanReviewGate=false`; `runtimeAcceptance=false`;
`qualificationApproved=false`; `fullLegacyRegressionAcceptance=false`;
PureInterpreter disabled. No Human Review Gate/H2/M08A/X02/SNAP-01.
