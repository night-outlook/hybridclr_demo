# Local Validation report

## Current run — 2026-09-21 authority `24a0d3af`

### Exit

**Local Validation → Primary Implementation: RETURN REQUIRED at retained pilot seal admission**

Fresh V00 authenticated candidate checkout `0733534d8112a7a0b1e05bb5d904e945b6ed24cc` and exact source/tool anchor `24a0d3af7d5b5b664d063a75d85deb4f11aa2915`. Candidate authority returned `SourceTargetVerifiedNotBuildAccepted`; reproduction tooling, the exact protected profile-1 family, and both installed runtimes passed. The candidate installed-runtime receipt was refreshed once through `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability`, then passed strict Shadow-ON verification with complete demo-source authentication.

Both reviewed source audits passed exactly. The non-metadata delta `a964f79d... → 24a0d3af...` is the required 11 paths, and `69130bbb... → 24a0d3af...` is the required 20 paths. No runtime, Unity asset, native, protocol, schedule, measurement, graph/build-map producer, preregistration producer, or Player binary source changed. Accordingly, the prior Unity 1076/1076 result and the prior three-mode retained-ON preflight are classified only as `ReusedAuditedFromD18`, not fresh current-source execution.

Fresh bounded Primary validation passed 359/359. All requested focused regressions passed, including the real formal child-command harness, exact graph-reuse transition, paired driver, formal batch, retained-early scope, R01 failure ownership, lazy-dense behavior, and both PowerShell recovery contracts. Full Python discovery completed 1,044 leaves: 1,016 Passed, 28 explicit environment-bound Skipped, zero failures, and zero errors. The skips remain non-Passed evidence.

The retained V04 manifest, Player-artifact manifest, and latest `authoritya964-formal-launch-blocked` checkpoint manifest all authenticated. Live protocol, schedule, build map, preregistration controls, pilot history, and all eight selected launch receipts remained bound. An independent complete rehash verified 33,792 retained files totaling 1,606,993,133 bytes with zero mismatches.

A new side-B-only `H1GraphReuseBridge` passed with status `AuthenticatedToolOnlySuccessor` and SHA-256 `3962cdd9fbd2d81de2d1f2918bc802c9e6e10151f8ae41ec01d40d388ae76004`. It binds the exact 20-path transition, current installed runtime, frozen build map, current formal-authority module, and current `run-r00-players.py`.

The mandatory new strict pilot seal then failed before deep verification:

`Prior A diagnostic runner binding mismatch`

This is a current Primary tool-contract defect. The authoritative retained pilot index records `run-r00-players.py` SHA-256 `afc0b649579ebd497be493be9fd39fcfe19e3ba3074d6d6679e009975d21a07c`, which exactly matches the runner at both retained graph anchor `69130bbb...` and previous source `a964f79d...`. The current formal-subprocess repair intentionally changed that runner to SHA-256 `a8de4dc1052306923f7aef529442d4c2012cc959c5dea58da6f15785caacd280`.

`seal-h1-pilot-verification.py` invokes `_load_prior(... phase="pilot" ...)` before authenticating the supplied graph bridge. `_load_prior` unconditionally requires every historical pilot side diagnostic `runner` binding to equal `runner_binding()` for the current file. It therefore rejects the immutable, correctly authenticated retained pilot provenance before bridge-aware strict reconstruction can begin. No `H1PilotVerificationReceipt` was created and `deepLaunchVerificationCount=0`.

Local did not modify source/tool contracts, weaken verification, edit `WEB_TO_LOCAL.md`, move protected pins, rewrite retained evidence, reuse the a964 bridge/seal, admit either historical failed formal index, start a new formal series, or begin R02.

### Results

| Cell | Result | Evidence / disposition |
| --- | --- | --- |
| V00 candidate authority | `Passed` | Checkout `0733534d...`; exact `SourceTargetVerifiedNotBuildAccepted` for `24a0d3af...` |
| V00 reproduction/protected refs | `Passed` | Reproduction tooling `ba8fee33...`; protected profile-1 family exact |
| V00 installed runtimes | `PassedAfterCandidateReceiptRefresh` | Candidate receipt `2a40ef6a...`; protected receipt `54bfe84c...`; both Shadow ON and demo source verified |
| V01 bounded Primary | `Passed` | 359/359 |
| V01 focused formal/graph/paired/batch/retained | `Passed` | 5/5, 12/12, 12/12, 2/2, 2/2 |
| V01 R01/failure/lazy | `Passed` | Capsule 7/7; launch 20/20; results 20/20; failure 16/16; lazy 10/10 |
| V01 PowerShell recovery | `Passed` | Generated-input labels and mutable-input success/failure restoration passed |
| V01 Python inventory | `CompletedWithExplainedEnvironmentSkips` | 1,044 total; 1,016 passed; 28 explicit environment skips; 0 failures/errors |
| V01 Unity EditMode | `ReusedAuditedFromD18` | Historical 1,076/1,076 retained only after exact 11-path audit; not fresh current-source execution |
| V01A source audits | `PassedExactSets` | Exact 11-path and 20-path non-metadata sets |
| V02 retained evidence | `PassedArtifactReauthentication` | Three manifests, controls, pilot history, 8 selected launches, and 1.607 GB bound files authenticate |
| V04 retained ON preflight | `ReusedAuditedFromD18` | Historical 3/3 result; no affected verifier path in 11-path delta |
| V04 graph bridge | `Passed` | New side-B `AuthenticatedToolOnlySuccessor`; SHA `3962cdd9...` |
| V04 strict pilot seal | `FailedBeforeDeepVerification` | Retained pilot runner `afc0b649...` rejected against current runner `a8de4dc1...`; no seal created |
| V04 new formal series | `Blocked / NotRun` | Mandatory new 8-side seal absent; historical failed indices not used |
| V04 final analysis | `NotRun` | Complete formal index absent |
| V05 / independent M08 | `Ineligible / NotRun` | Mandatory seal, formal, and analysis evidence absent |

### Root cause and required Primary correction

The loader conflates two different identities:

1. immutable provenance of the historical runner that produced retained pilot diagnostics; and
2. the current runner implementation that the new seal/formal chain must authenticate for current execution.

Primary must add a fail-closed bridge-aware retained-pilot admission path. It should accept the historical pilot runner only when its path/hash is authenticated as the exact runner at retained graph anchor `69130bbb...` and the same bridge proves the reviewed transition to the current runner. It must continue to require the current runner for new formal attempts, preserve default/direct current-pairing behavior, preserve protected side-A isolation, and reject arbitrary historical runner substitution. Add a real regression that feeds the actual retained-style pilot runner binding through `seal-h1-pilot-verification.py` with a valid current bridge and proves eight deep sides can start, plus negative tests for unbridged or tampered historical runner hashes.

After Primary publishes the correction, Local must restart at fresh V00, re-audit the source delta, create a new bridge and strict seal, and start a new formal series from the retained pilot index. The a964 bridge/seal and its two failed formal attempts remain historical only.

### Retention checkpoint

The authenticated blocked checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority24a0-pilot-seal-blocked/`. It contains fresh V00/V01/V01A/V02 evidence, reuse classifications, the new bridge, the production seal failure receipt, prior checkpoint manifest links, raw evidence, and a SHA-256 manifest. No retained graph or pilot cleanup was performed.

H1 remains `InProgress`; the last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.
