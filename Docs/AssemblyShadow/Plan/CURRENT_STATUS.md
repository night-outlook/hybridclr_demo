# Current Status

- Candidate build-input/tool source anchor: `a964f79d6ceba866c5956741a4a32e38ff8a6b5f`.
- Latest Local return: `21caaecc315623ec10c779af04d563ed7badeac2`.
- Latest authenticated Local checkpoint: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6dd9-formal-blocked/`.
- Reusable V04 graph/pilot checkpoint: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/`.
- Gate: `H1 / InProgress / AwaitingNestedEarlyAuthorityEmpiricalClosureAndFormalSampling`.
- Last independent M08: `FAIL` (historical; not rerun).
- Human gate passed: `false`.
- May enter R02: `false`.

## Latest Local result

Local freshly validated source/tool anchor `6dd964c0...` and completed:

- candidate/protected authority and installed-runtime verification;
- exact 14-path retained-graph source audit;
- retained checkpoint/Player/control/pilot reauthentication;
- complete Python inventory with 1005 passed, 28 explicit environment skips, zero failures/errors;
- fresh broad Unity EditMode 1076/1076;
- a real side-B `H1GraphReuseBridge` whose SHA-256 is `088a338632a9d2a9970c0bc61aaa9b218b4ca93e080a1734539b68317fa1a89e`.

The real bridge itself passed. The subsequent strict pilot seal failed after about 1104.2 seconds with:

`R00 baseline: source pins differ from baseline provenance`

No pilot seal or formal Player was created.

Focused Local diagnosis proved:

1. outer `r00_results.verify_suite(... pairing_authority=...)` retained-graph verification passed;
2. strict modern `R01EarlyStartup` then called `r01_early_results._prepare`;
3. `_prepare` re-entered default current-pairing `verify_inputs`;
4. the authenticated bridge authority was therefore dropped only at nested early-capsule reconstruction.

This is a fail-closed Primary authority-propagation defect, not bridge corruption, artifact drift, timeout acceptance, or performance failure.

## Current Primary repair

Source anchor `a964f79d6ceba866c5956741a4a32e38ff8a6b5f` closes that exact nested boundary.

### Authority propagation

- `r01_early_results._prepare` accepts an optional **keyword-only** `pairing_authority`.
- No authority: it preserves the original current-pairing `verify_inputs` path.
- Authority present: it uses `verify_inputs_with_reuse`.
- `r00_results.verify_suite` passes the exact same authenticated authority into both nested early-preparation call sites.
- Direct `r01_early_results.verify_suite` remains current-pairing-only; no historical-pairing CLI or public verifier argument was added.
- Retained authority is accepted by nested early preparation only when requested early modes are a subset of `Baseline` / `Control`.
- Ordinary, failure, and guard early modes reject retained authority before nested verification.

`r00_player_inputs.require_current_pairing` remains unchanged.

### Bridge invalidation

`r01_early_results.py` is now:

- part of the exact retained-graph non-metadata allowlist;
- part of the graph bridge's verifier bindings.

Any later early-verifier change therefore invalidates the bridge and requires a new bridge.

The retained `69130bbb... → current` non-metadata delta is now exactly **17 paths**. It still contains no Assets/Packages/Unity C#/asmdef/native runtime/measurement/protocol/schedule/map producer change.

### Fast retained-ON preflight

New:

`Tools/AssemblyShadow/verify-h1-retained-early-reuse.py`

Before the full 8-side seal it:

- full-reauthenticates the bridge;
- selects candidate side B;
- strict-verifies:
  - `R00-ON-NoPatch`;
  - `R00-ON-P01`;
  - `R00-ON-P03`;
- uses the same authenticated authority;
- therefore exercises both nested early `Baseline` and `Control` capsule reconstruction.

It is read-only diagnostic evidence and does not replace the full pilot seal.

### Regression coverage

Primary now covers:

- real `69130bbb... → current` Git/source transition;
- actual nested `r01_early_results._prepare` with bridge-style authority and `Baseline`;
- assertion that default `verify_inputs` is not called in that retained path;
- `r00_results` authority propagation into nested preparation;
- direct early verifier remains current-pairing-only;
- nonperformance modes reject retained authority;
- retained-ON preflight verifies exactly the three candidate ON modes with one authority;
- existing bridge/seal/formal/final-analysis and formal-batch regressions.

Primary workflow `35614424960` at authority successor `76577900...` passed **353/353** bounded tests, live handoff **11/11**, R01 early capsule **7/7**, early launch **20/20**, early results **20/20**, failure pipeline **16/16**, both M07 PowerShell recovery regressions, and lazy **10/10**.

## Required next action

Local must restart from fresh V00, refresh candidate installed-runtime receipt for the new source pin if required, run current Python/Unity/source audits, and create a **new** bridge.

Do not reuse the valid `6dd964c0...` bridge because it binds old current-source/verifier hashes.

Then run the new 3-mode retained-ON preflight. Only if that passes, run a new full 8-side strict pilot seal. If the seal passes, proceed immediately through the 40-pair formal batch and bridge-aware final analysis.

The prior failed seal remains historical evidence and must not be relabelled.

Only after V04 completion, V05, and genuine independent M08 PASS may H1 become Ready for Human Review Gate.

Do not begin R02.
