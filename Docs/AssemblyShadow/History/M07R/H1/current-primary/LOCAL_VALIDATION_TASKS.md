# Local Validation Tasks — Formal Sampling Closure after `fa23a0dd...`

Candidate build-input/tool source anchor:

`1a87a393e7a0ee312f39647532d80bfc603c7b23`

Latest Local return:

`fa23a0ddcf45eabc870e7e7742d2d18a78a52d49`

Retained authenticated V04 checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/`

H1 remains `InProgress`. Do not begin R02.

## Goal

Validate the sealed pilot-admission optimization, reuse the already-passed controlled graphs/map/preregistration/pilots only when the source/hash audit permits it, then complete all forty formal pairs and final analysis in one Local cycle if no new failure occurs.

## V00 — fresh current authority

1. Pull the final pushed `codex/assembly-shadow-r01b-h1` checkout and require clean tracked state.
2. Record checkout HEAD separately from source anchor `1a87a393e7a0ee312f39647532d80bfc603c7b23`.
3. Run candidate handoff/source preflight and require `SourceTargetVerifiedNotBuildAccepted` for the exact source anchor.
4. Reauthenticate reproduction tooling and protected profile-1 pins.
5. Verify candidate and protected installed runtimes.

Hard-stop on source/runtime/protected-ref mismatch.

## V01 — current tool regression

Run:

- bounded Primary suite;
- committed live-handoff preflight;
- direct paired-driver regression;
- existing R01/lazy/PowerShell recovery suites.

The paired-driver regression must prove:

- strict seal: exactly 8 deep pilot-side verifications;
- 40 formal admissions: zero deep pilot rescans;
- fail-closed mutation handling for pilot receipt, bound artifact, protocol, schedule, build map, and verifier.

Also rerun the complete Python inventory once the retained policy-pinned M00 fixed input is present. The prior 20 nonpasses were generated-prerequisite failures, not accepted skips.

Run broad Unity EditMode after required clean-owner generated prerequisites are present. Do not promote prior generated-prerequisite failures to Passed without a fresh rerun.

## V01A — source-scope reuse audit

Compare executable/tool source from:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3`

to:

`1a87a393e7a0ee312f39647532d80bfc603c7b23`

Expected executable/tool/test/CI delta:

- `Tools/AssemblyShadow/run-h1-paired-performance.py`;
- `Tools/AssemblyShadow/seal-h1-pilot-verification.py`;
- `Tools/AssemblyShadow/tests/test_h1_paired_driver.py`;
- `Tools/AssemblyShadow/h1_bee_primary_tests.py`;
- `.github/workflows/h1-bee-primary.yml`.

Require **no change** to:

- Player/runtime/Bootstrap C#;
- HybridCLR native;
- HybridCLR Unity;
- IL2CPP;
- `run-r00-players.py`;
- `r00_results.py`;
- `r00_player_inputs.py`;
- M07 graph/build receipts;
- performance protocol JSON;
- bound schedule JSON;
- build-map freezer;
- preregistration binder;
- timing/statistics logic;
- final paired analyzer.

Docs/source-pin/history commits after the source anchor are metadata-only.

If the expected scope does not hold, do not reuse V04 artifacts.

## V02 — retained V04 artifact reauthentication

Before reuse, verify:

- checkpoint `MANIFEST.sha256`;
- `PLAYER_ARTIFACTS.sha256`;
- reference/current controlled graph receipts and controlled evidence;
- old-Player rejection receipt;
- frozen build map + freeze receipt;
- preregistration binding;
- bound protocol/schedule;
- cumulative pilot index and all pilot launch receipt bindings.

Require all hashes to match the retained checkpoint and live bound files.

If any graph/map/protocol/schedule/pilot binding changed, stop and rebuild the affected evidence instead of resealing it.

## V04.J — seal the completed pilot set exactly once

Choose a new output path under the current evidence root and run:

~~~text
python3 Tools/AssemblyShadow/seal-h1-pilot-verification.py \
  --protocol <bound-protocol> \
  --schedule <bound-schedule> \
  --build-map <frozen-build-map> \
  --pilot-index <retained-pilot-sample-index> \
  --output <new-pilot-verification.json>
~~~

This step is expected to perform the expensive strict reconstruction once.

Require:

- `kind=H1PilotVerificationReceipt`;
- `status=PassedStrictReconstructionAndStatGuardSealed`;
- `deepLaunchVerificationCount=8`;
- exactly four selected pilot modes;
- verifier bindings match current tools;
- protocol/schedule/map bindings match retained artifacts;
- pilot attempt digest includes retained failed/retry attempts;
- file inventory and guard digests are present;
- no file identity changed during sealing.

Record wall-clock duration and file count/bytes from the receipt.

Do not regenerate the seal after observing formal timings unless a bound identity actually changes and the invalidation is retained as evidence.

## V04.K — run all forty formal pairs with the same seal

For formal pair 1 use the retained pilot index:

~~~text
python3 Tools/AssemblyShadow/run-h1-paired-performance.py \
  --protocol <bound-protocol> \
  --schedule <bound-schedule> \
  --build-map <frozen-build-map> \
  --pilot-verification-receipt <new-pilot-verification.json> \
  --prior-index <retained-pilot-sample-index> \
  --output-root <new-formal-pair-root> \
  --phase formal \
  --attempt 1
~~~

For every subsequent pair, use the previous successful/retained `sample-index.json` as `--prior-index`. Omit `--pair-id` for a new scheduled pair so the driver selects the next unattempted formal row.

Require every generated formal index to carry the exact same `pilotVerification` path/hash binding.

If a pair fails for a protocol-permitted reason:

1. retain the failed whole-pair attempt;
2. diagnose and confirm no owned process remains;
3. rerun the **same pair** with `--pair-id <id>` and incremented `--attempt`;
4. chain the failed index as the next prior index;
5. never selectively rerun only A or B.

No latency-based deletion, schedule edit, threshold edit, build-map edit, or seal replacement is permitted.

### Cached admission performance evidence

For at least the first formal invocation record:

- time from driver start to first side runner launch;
- absence of repeated `r00_results.verify_suite` pilot reconstruction;
- cache receipt binding;
- any stat-guard verification diagnostic.

The previous 47:39 pre-launch behavior must not recur on an unchanged sealed graph.

## V04.L — final paired analysis

After all 40 formal pair IDs have a selected valid attempt, run the unchanged analyzer:

~~~text
python3 Tools/AssemblyShadow/analyze-h1-paired-performance.py \
  --sample-index <final-sample-index.json> \
  --output <new-performance-analysis.json>
~~~

The analyzer remains fully strict and may take substantial time because it independently reconstructs selected evidence. Do not substitute the pilot seal for final analysis.

Retain the full analysis even if comparability or measured results are unfavorable.

## V04.M — complete current-anchor inventory closure

Before V05 eligibility, require fresh closure of the two prior generated-prerequisite inventory gaps:

- complete Python inventory;
- broad Unity EditMode inventory.

If prerequisites are still absent, record exact missing generated artifacts and generate/recover them only through the existing authoritative build/setup path; do not weaken tests or convert failures to skips.

## Retention checkpoint

Before cleanup, authenticate a new checkpoint containing/hash-binding at minimum:

- fresh V00/V01 and source-scope audit;
- retained-V04 reuse authentication;
- strict pilot verification receipt;
- every formal attempt and cumulative sample index;
- cached-admission timing/diagnostic evidence;
- final analysis;
- fresh Python/EditMode closure;
- explicit links/hashes back to the prior V04 boundary checkpoint.

Preserve failed/retried attempts.

## V05 / independent M08

Proceed only if:

1. source-scope reuse is independently justified;
2. the pilot seal passes;
3. all 40 formal pairs complete under the preregistered contract;
4. final analysis completes;
5. complete Python/EditMode inventories no longer contain unexplained nonpasses;
6. no fresh evidence contradicts retained V04 evidence.

Then prepare V05 successor evidence and commission a genuinely independent whole-chain M08 review.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**.

Stop for explicit human approval. Do not begin R02.
