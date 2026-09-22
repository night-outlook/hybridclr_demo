# Current Status

- Candidate build-input/tool source anchor: `f1266a4d7f39a49523186b3dc63f9add9cc0e64c`.
- Latest Local return: `d18a1fb15c43f918c9d3bba1ed641e87a58b32b0`.
- Latest authenticated Local checkpoint: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authoritya964-formal-launch-blocked/`.
- Reusable graph/pilot checkpoint: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/`.
- Gate: `H1 / InProgress / AwaitingFormalSubprocessAuthorityEmpiricalClosure`.
- Last independent M08: `FAIL` (historical; not rerun).
- Human gate passed: `false`.
- May enter R02: `false`.

## Latest Local result

At source `a964f79d...`, Local completed all admission work through a passing strict pilot seal:

- current/protected authority and installed runtimes passed;
- exact 9-path and 17-path source audits passed;
- Python inventory: 1010 passed / 28 explicit environment skips / 0 failures-errors;
- Unity EditMode: 1076/1076;
- retained evidence and 33,792 bound files reauthenticated;
- new graph bridge passed;
- retained-ON early preflight passed all 3 modes;
- strict pilot seal passed 8/8 with stable guards;
- cached formal admission reached first side launch in about 14.746 seconds.

Formal pair 1 then found the next boundary.

Protected side A passed. Candidate side B failed before Player launch because the child `run-r00-players.py` process still called default current-pairing `verify_inputs`. A protocol-valid whole-pair attempt 2 reproduced the exact same side-B failure.

The failure is not bridge/seal drift, nested early reconstruction, timeout, cleanup, or a measured Player failure.

## Current Primary repair

Source anchor `f1266a4d7f39a49523186b3dc63f9add9cc0e64c` adds a formal side-B subprocess authority boundary.

### H1FormalSideLaunchAuthority

For every bridge-bound **formal candidate side B** attempt, the paired driver creates a new `H1FormalSideLaunchAuthority`.

It binds:

- pairId, attempt, mode, AB/BA order;
- exact candidate project;
- exact per-side R00 output root;
- protocol and schedule;
- frozen build map;
- graph-reuse bridge;
- pilot verification seal;
- fixture manifest;
- Native ON and Native OFF receipts;
- Editor replay;
- current authority/paired-driver/R00-runner/R00-verifier/early-verifier tool hashes.

The output-root binding prevents replaying one authority into another formal runner output.

### Child runner

`run-r00-players.py` exposes only the H1-specific:

`--h1-formal-launch-authority <receipt>`

It does **not** accept a raw historical revision or generic source-pin override.

When that receipt is present, the child:

1. verifies the exact pair/input/map/bridge/seal/tool/output binding;
2. reconstructs authority through the same graph bridge;
3. uses `verify_inputs_with_reuse` for retained candidate side B;
4. passes the same authority into Baseline/Control early preparation for ON modes.

Without the receipt, behavior remains current-pairing-only.

Protected side A never receives the authority.

### Parent and retry evidence

The R00 runner writes the exact authority binding into its launch receipt.

The parent only marks a real runner receipt Passed when that echo equals the parent-issued authority.

Formal attempt diagnostics retain `formalLaunchAuthority`.

A failed candidate side B that exits before producing an R00 launch receipt still retains its authority receipt and original runner diagnostic; no synthetic launch evidence is fabricated.

Resumed bridge-bound formal chains require a hash-valid side-B authority on every non-skipped formal attempt.

### Final analysis

Before statistics, final analysis now:

- full-verifies the graph bridge;
- verifies every formal candidate side-B authority against pairId/attempt/inputs/output-root/bridge/seal/tool hashes;
- requires protected side A to have no retained authority;
- validates authority evidence even for failed pre-launch attempts;
- requires successful runner receipts to echo the exact same authority;
- then performs the existing strict launch/raw/result verification.

## Source scope

Previous Primary source `a964f79d... → f1266a4d...` is exactly **11 non-metadata paths**.

Retained graph `69130bbb... → f1266a4d...` is exactly **20 non-metadata paths**.

No Unity Assets/Packages/C#/asmdef, native runtime, measurement source, protocol, schedule, graph producer, or Player binary source changed.

The new paths relative to the previous retained allowlist are:

- `Tools/AssemblyShadow/h1_formal_launch_authority.py`;
- `Tools/AssemblyShadow/run-r00-players.py`;
- `Tools/AssemblyShadow/tests/test_h1_formal_launch_authority.py`.

## Primary validation

The final pre-pin source run executed **357/357 functional bounded tests** successfully. Its only nonpass was the intentionally stale source-pin live-handoff preflight; authority-updated CI is the next gate.

## Next action

Local must restart from fresh V00, create a **new** bridge and a **new** strict seal because source/tool/verifier hashes changed.

The previous a964 bridge/seal/preflight are historical/audited evidence and cannot be reused as current authorities.

A separate 3-mode retained-ON preflight is not mandatory this cycle because the new 11-path delta does not touch R00 results, early results, or that preflight tool, and the fresh 8-side seal re-verifies those paths under the new bridge.

Start a **new formal series from the retained pilot index**, not from either failed a964 formal attempt.

The first new pair must empirically prove:

- parent creates side-B `H1FormalSideLaunchAuthority`;
- child accepts it;
- candidate side B gets past graph preparation and actually launches the Player;
- R00 launch receipt echoes the same authority;
- protected side A remains authority-free.

If pair 1 passes, continue the formal batch through all 40 pairs and final analysis.

Do not begin R02.
