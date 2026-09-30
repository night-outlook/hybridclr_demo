# R03 C — batch-B validation matrix after managed lifetime repair

Date: 2026-09-30. Status: **prepared for Local Validation; batch B NotRun**.

This is the batch-B supplement to the immutable `A_VALIDATION_MATRIX.md`. It changes the source anchor and process-lifetime coverage, not the 36-cell ledger, four build roles, nineteen Player cases, product expectations or R03 exit conditions. `C_LIFETIME_REPAIR.md` and `C_HOST_EVIDENCE.json` record Primary's repair and host evidence. `Handoff/WEB_TO_LOCAL.md` supplies the exact new Local execution instructions.

## Authority

All repositories use `codex/assembly-shadow-r01b-h1`. The demo's new tested executable/CI source anchor is **`7e2852fcd6c5bd9ebc82f2b3f97516742b772dc2`**. The actual Local execution must use its final documentation-only transport descendant identified by the current handoff and Primary's exact prompt, with local/remote HEAD equality. The old `f5f571...` anchor and batch-A handoff are historical, not authority for a new run.

External pins remain:
- HybridCLR `041c0cbb42d3e64e54fe605673d99799b5d63893`.
- Managed package `120bb01be680cec0375002a0823552d66d34b84c`.
- IL2CPP `1abb6bcaa85226f08c67f9da65edb3c58e8cb399`.

Reference graph package remains `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`; reference Player native cores remain HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` and IL2CPP `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`. Reference Players use the same current harness/package as the candidate, not the historical accepted binary.

Local environment: macOS arm64, .NET SDK 8.0.318, Unity **2022.3.62f2**, StandaloneOSX/arm64. Paths and version checks are in the live handoff. New unused root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930B-lifetime`. Never reuse or retry batch A.

## Same thirty-six required cells

| Group | Count | Batch-B requirement |
| --- | ---: | --- |
| Entry authority | 1 | Four canonical clean owning checkouts, exact source pins/branch and remote-head equality. |
| Verifier contracts | 1 | Existing 29 verifier/filesystem contracts plus 14 new lifetime/policy tests: 43 tests, within the existing cell. |
| Reference sources | 1 | Three detached published reference worktrees, preserved and verified. |
| Host baseline graph | 1 | Successful owned build followed by actual reference graph assertion execution: 9 cases. |
| Host candidate graph | 1 | Successful owned build followed by actual candidate graph assertion execution: 9 cases. |
| Host admission | 1 | Successful owned build followed by all 35 real-DLL admission/method assertions. |
| Player fixtures | 1 | Successful owned build/run and exact 15-DLL inventory authentication. |
| Isolated project preparation and native builds | 8 | Prepare/build pairs for candidate-release, reference-release, candidate-debug and candidate-off. |
| Editor tests | 1 | Actual EditMode execution, all mandatory R03 IDs and target-cycle regression, unchanged result checks. |
| Player cases | 19 | Unchanged `player-cases.json`: C01–C10, R01–R05, D01–D03 and O01, each in a fresh process. |
| Final authority | 1 | Recheck all four source/branch/remote identities and clean owning checkouts. |
| **Total** | **36** | Original dependency rules remain; independent cells continue and dependent cells become Blocked on failure. |

The Player coverage remains baseline/no-patch, reference observations, private-reference rejection, supported private-primitive proof, physical slot movement/logical remapping, old-AOT execution rejection, legal direction reversal, actual target-cycle rejection, interface/kind/field-removal rejection, Debug and feature-OFF paths. No input, expected value, warm-certificate assertion or failure-phase expectation is relaxed.

## R03-LA-001 specific evidence

For the three previously blocked host build/assertion paths and fixture generation, verify that the recorded managed build commands contain `--disable-build-servers`, `-p:UseSharedCompilation=false`, and `-nodeReuse:false`. The child policy must contain the server/node-reuse controls in `command_lifetime.py`; changing the agent's global environment or shutting down unrelated servers is not an alternative.

A positive command receipt must show `schemaVersion=2`, `lifetimePolicy=R03OwnedCommandV1`, exit 0, no timeout, `remainingProcessGroup=false`, no start or cleanup errors, and bound stdout/stderr hashes. Actual assertion results must follow successful builds: compilation alone cannot pass a host cell. The same production wrapper is used by Local and the new host CI driver.

On a surviving group, preserve the original true observation, the bounded `process-group-before-cleanup.json` roster (or its explicit unavailability), PID/PGID, cleanup errors and the separate post-cleanup observation. Successful cleanup cannot turn a command or cell into PASS. There is no grace-to-PASS, process-name whitelist, global server shutdown, semantic retry or output-root reuse.

The 14 new tests include real clean/nonzero/timeout/startup-failure commands, an exit-0 parent with a surviving child, an unrelated sentinel left alive, unavailable diagnostics, disappearing-group behavior, bounded roster parsing, inherited environment override and immutable output roots. These synthetic negatives test tooling enforcement; they are not evidence of a native product failure or successful Player execution.

## Result, seal and return

All 36 cells and the focused seal must pass for `EvidenceReadyForPrimaryReview`. Otherwise retain `ReturnRequired` and all failed/blocked/NotRun classifications. Keep `R03Accepted=false`, `H2Passed=false`, `pureInterpreterExpansionEnabled=false`, and `fullLegacyRegressionAcceptance=false`.

Retain the original ledger, final result, index/archive/seal receipts, command and process diagnostics, host/fixture outputs, native build receipts, Editor XML/logs, all Player request/raw/verifier chains and inventoried excluded live roots. Record the factual outcome in the Local-owned reports and a new immutable batch-B checkpoint, commit/push those Local deliverables, then return to Primary.

Batch A remains 4 Passed / 3 Failed / 29 Blocked with its passed custody seal. Primary host CI on Linux and macOS arm64 passed 43 Python tests, both 9-case graph suites, 35 admission/method cases, fixture generation, Runtime API compilation and twelve clean owned commands per platform. Those results justify issuing this new Local handoff; they do not retroactively execute A, prove Local's macOS 26.5/Unity environment, or complete R03/H2. Broader legacy/resource, generic/delegate/interface, startup/capacity/performance/memory, PureInterpreter qualification and independent stage review remain Primary-owned.
