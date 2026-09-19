# R01B H1 — Current Primary Implementation

## Status

Latest Local return:

`7a627afc7d3615430772cd1f5e6978d5106f34c7`

Current candidate build-input source anchor:

`99ef65db13341f54cf610e18453dddf197ee86e4`

H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

## Local findings

The `4fff4df...` Local cycle re-established current source/build/M07 authority and passed startup11, M07 14/14 and the broad independent capacity/parser/index/native matrix.

Three independent Primary-owned blockers remained.

### A. Failure/publication transaction was still too late

All three early Baseline admission capsules passed in the same Player PIDs.

Normal host startup then legitimately touched candidate baseline assemblies.

The later managed `R01FailureProbe` attempted a new Shadow transaction and received `BaselineAlreadyUsed` in every mode.

This is architectural: a transaction that is meant to prove first-use behavior cannot start after normal host continuation.

### B. Lazy-v2 command inventory was off by one field

The deterministic-v2 generator records:

`[mono, generator.exe, fixtureId, output.dll]`

for each generation run.

The lazy verifier incorrectly required three fields, so it rejected the fresh valid v2 manifest before Player launch.

### C. Protected profile-1 M07 used historical coordinator policy

The profile-1 installation itself verified exactly.

Its historical M07 wrapper then called its own historical full source verifier after `ValidateCompilerInputs` had intentionally rewritten baseline-bound tracked files, so it failed before producing the profile-1 graph.

## Repair A — earliest callback owns the complete failure transaction

The dedicated failure/publication matrix now maps:

- `R01-Failure-P03-Control` → early `Control`;
- `R01-Failure-Q04-Metadata` → early `MetadataFailureContinue`;
- `R01-Failure-InitializerThrow` → early `InitializerFailureContinue`.

The new continued modes run the same strict `R01EarlyStartup.RunFailureTransaction` logic as the terminal startup tests.

The difference is only the gateway result:

- historical `MetadataFailure` / `InitializerFailure`: `PassedExpectedFailure`, callback return 1, native process terminates before host continuation;
- dedicated `MetadataFailureContinue` / `InitializerFailureContinue`: `PassedExpectedFailureContinued`, callback return 0, allowing the dedicated late verification probe to run.

The generic startup suite refuses the continuation-only modes; only the failure/publication launcher can request them.

### Late probe is now read-only

`R01FailureProbe` no longer mutates Assembly Shadow state.

It:

1. re-verifies the current M07/failure/Q04 input graph and profile-2 budget contract;
2. binds the exact early capsule and early receipt to the current PID;
3. requires the early receipt file to equal `R01EarlyStartup.LastReceiptJson`;
4. proves early mode/patch/baseline/runtime/closure and staged DLL/PDB bytes exactly match the selected failure case;
5. queries post-host diagnostics, capacity and recovery only;
6. requires the transaction state to persist across host continuation:
   - Control → `Committed`;
   - Metadata → `Failed`;
   - Initializer → `FailedAfterCommit`.

The strict Python verifier treats the early receipt as authoritative transaction evidence and the schema-2 late result as persistence/provenance evidence.

Launch/verification schema is now v3 with `transactionOwnership=EarliestStartup`.

## Repair B — lazy-v2 generator command binding

The lazy v2 verifier now requires exactly four generation commands in this exact semantic order:

1. fixture 1 / run 1;
2. fixture 1 / run 2;
3. fixture 2 / run 1;
4. fixture 2 / run 2.

Each command must be:

`[pinned mono, absolute generator exe, exact fixture id, exact Ixxxx-runN.dll output]`

All previously added generator/tool/hash/shape/parser/historical-v1-separation checks remain unchanged.

## Repair C — current coordinator drives protected reference M07

The current candidate outer M07 wrapper is project-parameterized.

The core now always invokes:

`$PSScriptRoot/verify-installed-runtime.py`

from the **current coordinator checkout**, even when `-ProjectPath` points to the protected historical project.

The current verifier already has the tested H1 dispatch:

- before workflow mutation: full runtime + demo-source verification;
- after baseline-bound mutation: full installed runtime/package/native verification with demo source skipped internally, plus `h1_m07_workflow_authority.py` against the authenticated originals and requested baseline.

The outer wrapper still owns exact backup/restoration of the three mutable tracked paths.

The protected project contributes only its exact pinned profile-1 source/runtime and Unity producer methods. Its historical `Invoke-M07Build.ps1` and historical verifier are not used to define current H1 coordinator policy.

`verify-h1-protected-reference.py` now authenticates the actual reference-side producers (`M07Build.cs`, `M07StructuralResources.cs`, `R00ControlledBuild.cs`, profile-1 reservation source), not the obsolete wrapper.

## Primary testing

The last authority-consistent run before the final producer-list cleanup, workflow `35411171891`, passed:

- bounded Primary: **320/320**;
- committed handoff: **11/11**;
- early capsule: **7/7**;
- early results: **19/19**;
- failure pipeline: **16/16**;
- lazy contract: **9/9**.

Artifact `10573647440`, ZIP SHA-256 `6b6cc55adf33447829af1b680c738970e81d2f06db6a50ec0fd8f65540a72e11`.

A final authority-consistent run including the protected producer-list cleanup is required before handoff completion.

## Preserved Local evidence

Checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260918-authority4fff/`

remains historical evidence for source anchor `4fff4df...`.

Its Passed/Failed/NoCoverage/NotRun states must not be relabelled.

## Next Local cycle

After final Primary CI:

1. fresh V00-V03/current M07;
2. startup11 + M07 14/14;
3. early-owned failure/publication matrix + late persistence verifier;
4. current capacity/parser/index retained cells;
5. fresh dense-v2 + diagnostic Player + lazy-v2 Player;
6. authenticate protected profile-1 family;
7. invoke **current candidate** `Invoke-M07Build.ps1` with `-ProjectPath <protected-demo>`;
8. verify the fresh profile-1 M07 graph and exact outer restoration;
9. run old-Player rejection;
10. produce controlled Development ON/OFF builds on both sides;
11. freeze A/B build map;
12. bind the preregistered performance protocol/schedule;
13. execute pilots/formal performance if comparability passes;
14. checkpoint before cleanup;
15. V05 + independent M08 only if mandatory evidence is complete.

Do not begin R02.
