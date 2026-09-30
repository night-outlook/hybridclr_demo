# R03 A — focused Local Validation matrix

Date: 2026-09-30. Authority: Primary Implementation. Status: **ready for first Local execution; not R03 acceptance**.

This file is the explicit matrix referenced by `A_PRIMARY_IMPLEMENTATION.md`. It binds the first empirical R03 run to the production candidate and to `Tools/AssemblyShadow/R03/run_local.py`. It does not reduce the broader R03 exit conditions in `Plan/stages/R03-evolution-semantics.md`.

## Source and platform pins

- branch for all four repositories: `codex/assembly-shadow-r01b-h1`
- demo host-CI execution anchor: `f5f5712459fdf67e2b748ddeab8e6540bffd3d95`
- HybridCLR candidate: `041c0cbb42d3e64e54fe605673d99799b5d63893`
- managed package candidate: `120bb01be680cec0375002a0823552d66d34b84c`
- IL2CPP candidate: `1abb6bcaa85226f08c67f9da65edb3c58e8cb399`
- reference HybridCLR core: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`
- reference IL2CPP core: `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`
- reference managed package: `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`
- Unity: `2022.3.62f2`
- target: `StandaloneOSX`
- architecture: `arm64`

The exact demo transport commit is the pushed feature-branch HEAD containing the live handoff. The batch receives that exact SHA through `--demo-commit` and independently validates it against local and remote Git state.

## Thirty-six required cells

The runner must produce exactly 36 unique cells:

1. `entry-authority`: four canonical repositories, exact branch/HEAD, clean owning checkouts and remote-head equality.
2. `verifier-contracts`: Python verifier/filesystem contract suite.
3. `reference-sources`: detached reference-core worktrees at the published R02 source pins.
4. `host-baseline-graph`: production graph contract against reference package behavior.
5. `host-candidate-graph`: production graph contract against the candidate package.
6. `host-admission`: 35 real-DLL layout/method identity contracts.
7. `player-fixtures`: exact 15-DLL native fixture inventory.
8–15. Four isolated role preparation/build pairs: `candidate-release`, `reference-release`, `candidate-debug`, `candidate-off`.
16. `editor-tests`: actual Unity EditMode execution with all required R03 contract IDs and the real target-cycle regression.
17–35. Nineteen fresh-process Player cases listed below.
36. `final-authority`: repeat exact clean repository/remote authority after all execution.

Independent cells continue after unrelated failures; dependent cells become `Blocked`. There is no semantic retry, expectation relaxation, source repair or acceptance promotion inside this batch.

## Nineteen fresh-process Player cases

| ID | Role | Expected observation |
| --- | --- | --- |
| C01-baseline | candidate-release | baseline/no-patch path |
| C02-private-reference | candidate-release | admission reject before unsupported layout can publish |
| C03-moved-slot | candidate-release | logical method maps despite physical slot movement; result 42; warm certificate |
| C04-old-AOT-guard | candidate-release | mapped active method succeeds; old AOT execution remains guarded |
| C05-direction-reversal | candidate-release | baseline A→B / target B→A accepted; result 41 |
| C06-actual-target-cycle | candidate-release | genuine target AssemblyRef cycle rejected |
| C07-private-primitive-append | candidate-release | native proof admits supported physical layout; result 41; warm certificate |
| C08-interface-change | candidate-release | admission reject |
| C09-reference-to-value-kind | candidate-release | admission reject |
| C10-field-removal | candidate-release | admission reject |
| R01-baseline | reference-release | reference baseline |
| R02-original-late-layout | reference-release | retained legacy late-layout behavior |
| R03-original-slot-lookup | reference-release | retained legacy physical-slot observation |
| R04-direction-reversal | reference-release | reference reversal succeeds; result 41 |
| R05-actual-target-cycle | reference-release | genuine target cycle rejected |
| D01-private-reference | candidate-debug | debug admission reject |
| D02-moved-slot | candidate-debug | debug logical remap succeeds; result 42 |
| D03-old-AOT-guard | candidate-debug | debug old-AOT guard retained |
| O01-feature-OFF-baseline | candidate-off | feature-OFF baseline behavior |

Each Player case has a unique run ID and process, exact request/raw/verifier receipts, actual PID, DLL hashes and bound build receipt. The native MethodInfo observer reads real baseline physical rows and actual active metadata; it is test-only and separately hashed in the build receipt.

## Pass boundary

A focused batch is successful only when all of the following are true:

- all 36 cells are `Passed`;
- `LOCAL_BATCH_RESULT.json.result == "EvidenceReadyForPrimaryReview"`;
- `sealStatus == "Passed"`;
- the execution ledger and seal authenticate successfully;
- `R03Accepted == false`;
- `H2Passed == false`;
- `pureInterpreterExpansionEnabled == false`;
- `fullLegacyRegressionAcceptance == false`.

Expected top-level evidence includes:
- `BATCH_EXECUTION.json`
- `LOCAL_BATCH_RESULT.json`
- `evidence-index.json`
- `evidence.tar.gz`
- `seal-receipt.json`
- `cells/*.json`
- `commands/*/command.json` plus stdout/stderr
- `host/**/results.json` and Player fixture inventory
- `builds/*/build-receipt.json`
- `editor-results.xml` and `editor-tests.log`
- `players/*/{request.json,raw.json,verification.json,Player.log}`

Rebuildable caches, detached reference worktrees and other explicitly excluded live roots are retained and inventoried but are not falsely represented as archive members.

## Failure boundary

Any failed prerequisite, build, Editor test, Player case, authority check or seal produces `ReturnRequired` or a nonzero runner exit. Preserve the unused-root evidence exactly. Do not rerun in the same root, edit expected values, widen timeouts as a semantic workaround, enable unsupported structure changes, or locally redesign the implementation.

Local may make only a trivial correction that is independently closed-loop verifiable and does not change design intent or blast radius. Any non-trivial issue returns to Primary with exact receipts and source pins.

## Scope limit

This batch is deliberately focused. Passing it does **not** complete:
- full P01/P02/P03 and old-resource P04/P05 regression acceptance;
- broader stack-trace/interface/delegate/generic/negative-method coverage;
- startup/capacity/performance and memory acceptance;
- PureInterpreter eligibility or structural expansion;
- complete R03 independent stage review;
- H2 or release approval.
