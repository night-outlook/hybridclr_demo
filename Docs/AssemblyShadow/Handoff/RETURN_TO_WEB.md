# Local Validation → Primary Implementation

## Blocker: failure/publication Player contract omits required early capsules

### Symptom

Fresh authority `8b1298d...`, controlled/normal M07, startup11, and the capsule-backed 14-mode M07 Player matrix pass. The next separate failure/publication gate launches all three cases, but the advanced Player refuses before host continuation:

```text
[AssemblyShadowStartup] Failed: Bootstrap explicitly refused startup
[AssemblyShadowStartup] Terminating process before host continuation (exit=1)
```

The strict verifier result is:

```text
R01-Failure-P03-Control.exitCode: expected 0, got 1
```

Evidence:

- launch receipt: `_temp/AssemblyShadow/R01FailurePlayers-Authority8b-20260918A/r01-failure-launches.json`, SHA `b28d88e6f3614d27709be569e39c90220117649e2fb3ab094e0706f9b5f8cd28`;
- strict result: `_temp/local-validation-20260917-authority8b/v04-failure-results.json`, SHA `ebeb4def22376d037d39b28fe7fe79bb4c964b211ff5341bad65810387e2d8a2`;
- per-mode Unity and console logs are beside the launch receipt;
- authenticated portable copy: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260918-authority8b/raw-evidence.tar.gz`.

### Exact reproduction

Run `Tools/AssemblyShadow/run-r01-failure-players.py` with the fresh normal-M07 fixture, ON/OFF receipts, replay receipt, failure-fixtures receipt, Q04 negative-input receipt, and a new direct child of `_temp/AssemblyShadow` as the output root. Then invoke `r01_failure_results.main()` on the resulting `r01-failure-launches.json`.

The recorded `processLaunches[*].command` and `r01_failure_results.command_for()` contain `-shadowR01FailureMode`, fixture/build/failure/negative paths, result path, and log path, but do not contain `-shadowEarlyCapsule`, `-shadowEarlyCapsuleSha256`, or `-shadowEarlyResult`.

### Root cause and affected scope

The advanced source-authority Player enforces authenticated earliest-startup acquisition before host continuation. `run-m07-players.py` already supports this through `--early-capsule-root`, and the corrected M07 run passed 14/14. The separate failure launcher predates or bypasses that contract and does not materialize/authenticate a mode-bound capsule. The verifier encodes the same obsolete command, so a manual extra argument would fail exact-command verification and cannot be used as an acceptance workaround.

This blocks the failure/publication prerequisite and therefore the remaining capacity 8192/8193, lazy/dense/generic/array/reflection/FieldRVA/old-Player, retained M03–M07, performance, V05, and M08 chain in this Local run.

A secondary harness defect exists: `Tools/AssemblyShadow/r01_failure_results.py` defines `main()` but has no `if __name__ == "__main__"` entrypoint, so direct script execution exits 0 without producing an output. Local invoked the unchanged `main()` through Python import to obtain the strict failed result.

### Recommended implementation direction

Update the failure launcher and strict verifier as one contract change:

1. Materialize the authenticated early capsule(s) before the immutable-input snapshot, using the same current source-pinned capsule machinery as startup11.
2. Add capsule and early-result files to the complete input inventory and launch receipt.
3. Add exact `-shadowEarlyCapsule`, `-shadowEarlyCapsuleSha256`, and `-shadowEarlyResult` arguments to each failure command.
4. Extend `r01_failure_results.command_for()` and verification to bind the capsule bytes, early result, process identity, and expected early outcome before accepting the failure/publication result.
5. Add the missing module entrypoint and focused positive/negative tests that prove the verifier rejects missing, stale, substituted, or mode-mismatched capsules.

Do not weaken startup refusal, bypass exact-command comparison, reuse a startup11 result as the failure result, or relabel the current failed launches.

### Validation still required

After the fix, rerun the three-case failure/publication launcher and strict gate from the retained fresh M07 chain or from a newly regenerated equivalent chain if any bound input changes. Only after it passes should Local continue the remaining V04 chain, retention update, V05 successor package, and genuinely independent whole-chain M08 review.

H1 remains `InProgress`; M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. Do not begin R02.
