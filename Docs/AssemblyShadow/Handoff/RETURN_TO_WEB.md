# Local Validation → Primary Implementation

## Blocker: complete Python discovery fails on a stale positive R00 fixture

### Symptom and reproduction

At the repaired pushed demo handoff HEAD `dd3c8988e9136e0c3a8ca965f82067d6b7c83acd`, source anchor `7aa6f61994da354b04464e38ddfc8552cc5c3055`, V00.R and committed V00 preflight pass. Bounded Primary passes 376/376. Full discovery then runs 1,061 leaves: 1,032 Passed, 28 Skipped, one Failed.

From `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`, run:

```text
python3 Tools/AssemblyShadow/h1_test_inventory.py python --tests /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Tools/AssemblyShadow/tests --pattern 'test*.py' --log <new-log> --output <new-inventory>
```

The failing leaf is:

```text
test_h1_paired_performance.H1PairedPerformanceTests.test_analyze_sample_index_complete_positive
AssertionError: 'ComparabilityIncomplete' != 'ComparabilityPassed'
```

The focused committed test reproduces this result. Its analyzer output has 44 invalid synthetic attempts, each side first reporting `R00 raw top-level build field differs: buildGuid`. All four formal-pair counts and selected pilot counts consequently remain zero. Chronology and interval checks are otherwise true.

### Root cause and affected scope

`Tools/AssemblyShadow/tests/test_h1_paired_performance.py` builds synthetic R00 results in `H1PairedPerformanceTests.raw()`. It places `buildGuid`, `baselineBuildId`, and `runtimeAbiHash` inside `playerBuildReceipt`, but does not place them at raw-result top level. The corrected production analyzer in `Tools/AssemblyShadow/h1_paired_performance.py::_check_build_binding` intentionally requires all three top-level fields and treats nested baseline/runtime values as optional duplicates. The synthetic positive fixture still models the pre-repair shape. An in-memory diagnostic that added the three top-level fields from the expected build receipt made this same focused test pass with `ComparabilityPassed`; no repository file was edited.

The bounded Primary suite does not include this positive test, so its 376/376 result did not detect the full-discovery failure. Because the full Python suite is a prerequisite to historical compatibility, Local did not run historical compatibility, corrected performance analysis, V05, or M08. This failure is in the synthetic test fixture; it is not evidence that any of the immutable 40/40 real formal pairs failed.

### Evidence

Authenticated return checkpoint: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority7aa6-python-fixture-blocked/`.

- `V00/v00r-source-authority.json`: all four correct Git worktrees, exact restored agent bytes, zero 7aa→HEAD non-metadata delta, exact 27df→HEAD five-path delta, and exact retained-graph 24-path audit.
- `V00/handoff-preflight.json`: `SourceTargetVerifiedNotBuildAccepted` at the repaired checkout.
- `V01/bounded-primary/`: passed 376/376 inventory and raw log.
- `V01/python-inventory.json` and `python-tests.log`: full 1,061-leaf result, failed test identity, assertion, and 28 explicit skips.
- `V01/paired-performance-focused-diagnosis-v2.json`: deterministic committed-test failure and first per-side analyzer errors.
- `V01/paired-performance-focused-diagnosis.json`: in-memory fixture correction passed; diagnostic only.
- `V02/historical-integrity.json`: independent 92/92 prior checkpoint manifest verification and matching fixed live bridge/seal/batch/final-index hashes. This does not establish current historical compatibility.

### Required Primary action and remaining uncertainty

Update the synthetic `raw()` fixture to emit the authenticated top-level `buildGuid`, `baselineBuildId`, and `runtimeAbiHash`, while retaining its nested receipt path/SHA/build-GUID binding. Rerun the positive test, analyzer negative tests, and complete Python discovery. Include the positive test in the required bounded regression so a passing bounded run cannot miss this contract drift again.

A committed change to this test file is non-metadata after `7aa6f619` and would violate both the current source pin and the fixed five-path `H1HistoricalPerformanceReanalysis-v1` compatibility boundary. Primary must review and publish a coherent source-authority and historical-analysis policy successor before returning to Local. Keep the fail-closed raw-result identity checks and immutable source-27df evidence; do not mark this test file metadata or silently broaden the historical allowlist. The exact authority revision needed for a test-only successor remains a Primary decision.

After the new pushed handoff, Local must rerun V00.R/V00, full Python discovery, complete live historical evidence authentication, compatibility preflight, corrected analysis, checkpoint, V05, and genuinely independent M08. H1 remains `InProgress`; historical M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. Do not begin R02.
