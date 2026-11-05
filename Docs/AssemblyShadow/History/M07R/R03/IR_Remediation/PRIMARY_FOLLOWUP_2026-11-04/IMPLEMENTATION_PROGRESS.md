# R03 Primary Implementation continuation — 2026-11-04

Status: **Primary Implementation in progress**. This is a source/CI continuation record, not a Human Review Gate or Local Validation acceptance report.

## Source authority

Working branch: `codex/assembly-shadow-r01b-h1`.

| Repository | Pinned revision for this continuation |
| --- | --- |
| `night-outlook/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `41764ae1eeefb33b05966e7f7676e52aae39c340` |
| `night-outlook/hybridclr_demo` | Track the actual feature-branch HEAD and this record's publishing commit; do not substitute an old consumed K pin |

The Connector disposable-branch smoke test passed on `night-outlook/hybridclr_demo`:
`codex/r03-connector-smoke-20261104-1814-5d3a`, commit
`844b9e70d3dab49250d8b183321f1200c8e37eaa`.
The branch was not removed because no branch-delete Connector action was available.
It is not a product or handoff branch.

## Committed source corrections

- `96cb83ba6455820216b02f9b8df07221b62d433f`: the existing V1
  `verify_ir` now admits **only** `off`, `baseline-owner`, and
  `type-resolution`. New generic or initializer labels cannot fall through
  to the type-resolution case. Added `test_terminal_stimulus_scope.py`;
  58 synthetic host regression cases passed locally, including four independent
  negative mutation classes in the prepared source package. This is *not*
  Player evidence.
- `6e3510dad54afc1ad5b624425dbbb415c518acd7`: make the three
  `MemberRefUser` method operands explicit `IMethod` arguments in
  `TerminalProducerFixtures.cs`. Previously CI failed with exactly three
  `CS0121` ambiguous `Emit` overload errors.
- `cc6e391aa2a757601f42680e686752efcb7f966e`: re-pin the **current**
  source-only oracle to reviewed blob
  `489e4bb13309c175545a042e15660f5d5c3aa83c` and add a relabelled
  unsupported-stimulus negative test. Historical S/K raw records are untouched.
- `5c5a9aff8b1a9691174ac0d9779c460e4a3100b1` and
  `24fccd9692ce371534be594cc41d894bd008eaa3`: update the
  **current-source candidate** gate and manifest to the same exact reviewed V1
  blob. This corrects the fail-closed CI source-identity failure; it is not
  an authorization to reuse a consumed Local run.
- `ceab491411934f92f1d2c80487fd32456d4e3a3d`: bind the
  current net8.0 fixture source admission to the actual reviewed project
  Git blob `249c47c1b453fc0cd3520173122599ca03cbe78c`.
  Earlier `REQUIRED_CSPROJ_BLOB` was stale and failed readmission.

## Observed CI evidence, without runtime promotion

- At `96cb83ba...`, the source-only terminal host matrix **passed**
  on macOS 14 and Ubuntu 24.04: GitHub Actions run
  [41954584869](https://github.com/night-outlook/hybridclr_demo/actions/runs/41954584869).
- The initially failing oracle run
  [41954584690](https://github.com/night-outlook/hybridclr_demo/actions/runs/41954584690)
  had `Existing oracle source changed; review test assumptions`. Its rerun
  on commit `cc6e391...` **passed**:
  [41955808472](https://github.com/night-outlook/hybridclr_demo/actions/runs/41955808472).
- Fixture generation CI originally failed three C# `CS0121` errors:
  [41954584795](https://github.com/night-outlook/hybridclr_demo/actions/runs/41954584795).
  The corrected `6e3510d...` source then passed the separate
  **non-acceptance** fixture reproducibility workflow:
  [41955783586](https://github.com/night-outlook/hybridclr_demo/actions/runs/41955783586).
- The current-native coherent source gate **passed** at
  `24fccd9...`:
  [41955843234](https://github.com/night-outlook/hybridclr_demo/actions/runs/41955843234).
- The subsequent Local-cycle host-contract run
  [41955843160](https://github.com/night-outlook/hybridclr_demo/actions/runs/41955843160)
  failed on an unrelated stale net8.0 `.csproj` Git blob expected by
  `current_native_environment_admission.py`, not a Unity Player run.
  The expectation was corrected at `ceab491...` and requires fresh CI
  observation before it can be called passed.

For any changed commit, recheck the exact run status before recording a final
outcome. Jobs not yet completed are **NotYetVerified**, never Passed.

## Open High findings and boundaries

1. **IR-R03-02:** deterministic host fixtures for `captured-generic`,
   `initializer-failure`, and `initializer-control` exist, but the
   corresponding genuine Player producers, independently preserved
   per-attempt side-effect evidence, strict case-specific raw verifier, and
   fresh isolated Player observations **do not exist**.
   Their CLR-only generator checks cannot establish R03 terminal behavior.
2. **IR-R03-01:** the generated-source identity crosswalk is not a semantic
   source → generated C++ → build receipt → original S Player execution proof.
   The original S inputs and historical published evidence remain immutable.
3. **Local Validation:** K was consumed; `WEB_TO_LOCAL.md` remains closed.
   Do not launch/replay K, edit its raw output, silently move its pins,
   or issue a new handoff before all planned source, host test, provenance,
   and scoped reviewer prerequisites are complete.

All gates remain `R03Accepted=false`, `H2Passed=false`,
`qualificationApproved=false`,
`pureInterpreterExpansionEnabled=false`.
Do not treat source CI, synthetic host tests, or original 15 fixture
regeneration as runtime qualification.

## Follow-up: all diagnosed current-source host gates restored

- `149db30e164ae04109bfe99ab1e3bef6d298a4ba`: update
  `current_native_cli_contracts.py` to the exact reviewed V1 verifier
  blob, without changing any consumed historical evidence.
- The complete current-native host workflow **passed** on macOS 15 and
  Ubuntu 24.04 at that source commit:
  [41956813877](https://github.com/night-outlook/hybridclr_demo/actions/runs/41956813877).
  This run includes source admission, real fresh Python CLI bootstrap,
  capacity/net8 preflight checks, and strict host-only contracts. It
  does not launch a Unity Player.
- Four additional K/L/source host workflows also **passed** at
  `149db30e...`:
  [41956813592](https://github.com/night-outlook/hybridclr_demo/actions/runs/41956813592),
  [41956813417](https://github.com/night-outlook/hybridclr_demo/actions/runs/41956813417),
  [41956813478](https://github.com/night-outlook/hybridclr_demo/actions/runs/41956813478),
  [41956813559](https://github.com/night-outlook/hybridclr_demo/actions/runs/41956813559).
- Before that, the source-only fixture and compatibility workflow
  [41956481142](https://github.com/night-outlook/hybridclr_demo/actions/runs/41956481142)
  passed at `ceab491...`.

This resolves the **identified host CI failures** for the newly reviewed
source. It does not close either High R03 finding or authorize Local execution.
