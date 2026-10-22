# R03 P1 — Root manifest lifetime consistency for Git-only postflight timeouts

## Authority and factual source states

The authoritative last Local-owned **`20261021-7c2c`** [validation](../../../../../Handoff/LOCAL_VALIDATION.md) and [return](../../../../../Handoff/RETURN_TO_WEB.md) record **`PASS / PassedSourceHostAndSDKOnly`**, source tuple demo `c5dde8493504cf69781fb0ab52123f525010a3aa`, native `82ddcef9417e3d662fdd39916a92124b5c835094`, hybridclr `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, hybridclr_unity `948c0e3b4f8891481301770115e8ba4945eea6de`. **24/24** independent children Passed; **85** original distinct command-failure test IDs; **seven** strict/sanitized source case inventories (28/21/12/15/16/16/16); five actual managed positive products and a distinct exact `OriginalUnsignedCounts` expected-negative; **100/100** official installed Unity2022.3.62f2 Apple arm64 C++17 syntax-only configurations; **20/20** actual final Git postflight direct commands exit0 and four verified final repo heads. Independent preservation audit Passed. One batch only; no retry/Unity Editor/Test Runner/Player/native product linking, GC/RSS, real Shutdown, canonical execution identity or R03 product acceptance.

Latest Local finding [`IR-LOCAL-P1-GIT-MANIFEST-LIFETIME-01`](../../local-validation-p1-git-postflight-20261021-7c2c/FINDING.json) is **`SourceConfirmed_NotFaultInjected`**: a source-only inconsistency in the **unexercised Git-only timeout** branch. The successful Local batch had no timeout; therefore its `PASS` is unaffected. The prior `20261021-82dd` raw aggregate is still **`FAIL / FailedOrIncomplete`** after a real 120-second hybridclr `ls-remote` timeout, even though all 24 children Passed and later independent source/SDK audits preserved source. Its `sourcePreserved=false` and `fourRepositoriesAfter=[]` remain immutable, and its missing postflight process evidence cannot be reconstructed or rewritten.

## Defect and minimal correction

Existing real finalizer computes:
- `unknown_lifetime = stopped is not None or git_probe.unknown_lifetime`
- Outer `RESULT.json.commandLifetimeUnverified = unknown_lifetime`
- `MANIFEST.json.inventoryScope = UnsealedObservedFiles` when `unknown_lifetime`
- **Incorrect** `MANIFEST.json.commandLifetimeUnverified = stopped is not None`

A Git-only timeout has `stopped=None`, `git_probe.unknown_lifetime=True`. The original manifest thus incorrectly said `false` even while its inventory scope and aggregate lifetime said `true`. This is a **root evidence-schema inconsistency**, not a demonstrated product-code defect, nor a successful live timeout in `7c2c`.

Change **one expression** in `Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py`:

```python
"commandLifetimeUnverified":unknown_lifetime
```

Leave everything else unchanged: all original 24 child scheduling and verdict semantics, the **120-second** Git authority timeout, five Git operations per four repositories, strict origin/branch/HEAD/clean/source before-after equality, direct command bounded stream/sha/elapsed receipts, unknown-descendant nonclaim, no retry/alternative transport, source-pins.json immutability and original SDK compiler contracts. Do not change `GitPostflightProbe` behavior, native/HybridCLR source or Unity SDK.

## Synthetic end-to-end fault coverage, in existing 85 tests

Extend **one existing** `test_p1_command_failures.py` discovery leaf (`test_postflight_failure_cannot_turn_green`) instead of adding test IDs. Its `exercise('postflight-git-timeout')` invokes the real `run_p1_metadata_local_preflight.main()` under controlled child/Git mocks, with **all 24** synthetic child receipts Passed and only second final Git repository's `ls-remote` fault-injected `subprocess.TimeoutExpired` with captured stdout/stderr prefixes. It **serializes real temporary batch `RESULT.json` and `MANIFEST.json`**, then parses/compares them separately, asserting:
- Exit1/aggregate `FailedOrIncomplete`; `sourcePreserved=false`; `postflightError` includes `TimeoutExpired`; only one fully verified final repo; one actual mock final Git timeout; `stoppedAfter=None` because all 24 components passed.
- Both **aggregate** and **manifest** generic `commandLifetimeUnverified=true`, exactly equal; `postflightGitDiagnostics.commandLifetimeUnverified=true`, `inventoryScope=UnsealedObservedFiles`; original official SDK mock results cannot promote aggregate acceptance; `descendantQuiescenceProven=false`.
- Existing successful-batch (`false`/`false`/CompletedBatchFiles) and already stopped-component (`true`/`true`/UnsealedObservedFiles) equality checks added inside existing leaves, with no new top-level tests, case-roster/count/threshold change or real external Git/SDK access.

**Red→green evidence:** First push **test-only** `hybridclr_demo@b29b6385b428e1cb3fbc5684306f6a754d1f7664` and observed [integrated 85-run CI 39710461380](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710461380) FAIL: exact `test_postflight_failure_cannot_turn_green` assertion `manifest['commandLifetimeUnverified'] is True` failed (was `False`), while all 85 tests executed. Then one-line source fix `hybridclr_demo@789655f19bd54c8abdcda67946a1f8195193176c`: corrected [integrated CI 39710581913](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710581913) PASS 2/2 Mac/Linux, [focused CI 39710581915](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710581915) PASS 2/2, [managed aggregate CI 39710581907](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710581907) PASS 2/2. These are **real Python tests of checked-in source with deliberately mocked Git/SDK/VM children**, not actual installed SDK syntax nor actual SSH timeout.

## Acceptance and Local boundary

One fresh, separately source-pinned **24-component source/host/official installed Unity SDK syntax-only** Local batch may verify this corrected root-manifest contract under a newly admitted unused root set, after independent preservation admission of all prior P1 raw/scratch/audit/checkpoints including `7c2c PASS` and `82dd FAIL`. Local must not retry old roots, alter Git/SSH or timeout, patch source/SDK, launch Editor/Test Runner/Player or promote product acceptance.

**P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete.** Original SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, strict S custody Blocked, independent full-stage R03 FAIL/re-review NotRun; all canonical TypeKey, pointer lifetime, VM-wide epoch/ABA, execution V1, 500ms/1..64, memory/GC/RSS/Shutdown and Player acceptance remain unproved. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
