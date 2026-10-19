# P1 opaque-inventory lifetime receipt parity — focused correction

## Problem and source evidence

The previously published inactive opaque inventory runner writes `commandLifetimeUnverified` into its component summary on a timeout, interruption or unknown command execution outcome. However, the shared outer aggregate in demo source before `d548799cc026b2ca78b40b7289fed404a3e8ec96` required that typed marker only from `empty-live`, not `opaque-inventory`. `read_component_result()` otherwise defaults a missing marker to false; `execute_component()` formerly treated a missing/malformed opaque summary as an ordinary known failed component and could continue later Git/compiler subprocess work without proving native descendant quiescence. This is a controlled source-path finding, **not** a witnessed timeout in the consumed 20261019-48ee Local PASS.

## Narrow behavioral change

- For the newly added native `opaque-inventory` component, require a present **boolean** `commandLifetimeUnverified` key on every completed result, just as for `empty-live`.
- If a completed native live child has a missing result, absent marker, malformed type, or invalid JSON, classify the outer command lifetime as **Unverified** and assign a distinct `NativeLiveReceiptUnavailableOrInvalid` stop reason. Preserve captured child exit/streams and receipt error; do not call postflight Git or start later scheduled components.
- If the inner result explicitly says `commandLifetimeUnverified=true`, retain `ChildReportedUnverifiedCommandLifetime` stop behavior even if the inner success status appears successful. Explicit `false` with completed exit!=0 is **Failed**, not unknown lifetime, and permits independent subsequent checks; full aggregate cannot PASS.
- Other historical components keep their existing schema/optional marker behavior. No native C++, original getter, compiler source, runtime flags, SDK matrices, build-helper or source-pins.json change.

## Focused regressions

Extend actual outer orchestration/mocked child cases by five: nested opaque uncertainty, missing marker, string marker, null marker and missing opaque result. Require `FailedOrIncomplete` aggregate, explicit `NotRun` receipts for later cells, absent unlaunched component roots, no postflight Git verification and unsealed observed inventory. Keep existing completed nonzero opaque regression and all 70 original methods.

Total contracts = **75 unique methods (5,14,34,10,12)**. Two CI runners (macOS and Ubuntu) execute focused, integrated 75 and managed/aggregate paths. Source/test CI scope does **not** prove actual detached compiler descendant quiescence.

## Local boundary

Source anchor demo `d548799cc026b2ca78b40b7289fed404a3e8ec96` and native `5e2326a45bd6070aa25830ca8c0236e1915bde13`. A new exact-four-remote-SHA, Docs-only WEB_TO_LOCAL authorizes one source/host/official installed SDK **syntax-only** batch: 16 components and 90 candidate native syntax configurations. No prior evidence root is recycled; no Unity Editor/Player, VM runtime, engine-owner experiment, acceptance promotion or Human Review Gate.
