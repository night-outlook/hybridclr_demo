# R01B H1 — Current Primary Implementation

## Status

Latest Local return:

`f829db516b3e5d0a9fef4d5539ec097dfb9867b3`

Candidate build-input source anchor:

`925e84d7b653bc7434482e6f4fbde39a4d9fcd0e`

H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

## What Local closed at source `99ef65db...`

The previous cycle established substantially more H1 evidence:

- V00-V03 source/provenance builds passed;
- controlled + normal M07 passed;
- startup11 and M07 14/14 passed;
- ordinary 8192/8193 and exact mixed 512 MiB capacity passed;
- dense-v2 generation and parser/native boundary coverage passed;
- generic/index/cache/capability/attribute/native retained coverage passed;
- the protected profile-1 runtime and fresh M07 graph passed under the current candidate coordinator;
- old-Player rejection passed;
- all four controlled Development Players passed provenance/configuration checks;
- build-map comparability and preregistration binding passed.

Only three independent V04 contracts remained incomplete.

## Repair 1 — Q04 post-terminal first-use history

### Observed failure

The Q04 transaction itself had already failed in the earliest callback and sealed native state as `Failed`.

Normal host continuation then recorded candidate baseline first-use entries.

The strict late verifier reused the eligible-transaction rule and rejected any selected-closure use, even though the transaction was already terminal and could no longer become eligible.

### Corrected rule

`verify_first_use_history` now has an explicit `allow_selected_closure` option, default `false`.

It is enabled only for the dedicated post-host Q04 persistence check.

Therefore:

- eligible transactions still reject selected-closure baseline use;
- Control and initializer published worlds still require exact no-late-baseline-use equality;
- the Q04 early receipt/history remains immutable;
- only candidate identities may appear after Q04 terminal failure;
- unknown/non-candidate identities remain invalid;
- registry order, complete first-use sequence, timestamps and previous-record immutability remain verified.

This changes the observation rule after terminal failure; it does not weaken transaction eligibility.

## Repair 2 — dense-v2 runtime identity

The deterministic generator source defines:

- namespace: `AssemblyShadow.Dense`;
- type: `DenseType_{fixtureId:D4}_{row:D4}_MetadataBoundary_0123456789abcdef0123456789abcdef`;
- method result: `fixtureId * 10000 + row`.

The Player probe incorrectly used namespace `AssemblyShadow.Workload` and expected only `fixtureId`.

The probe now derives both the generated type name and return value through dedicated helpers shared by the two 4095/4096 checks.

Expected boundary results are:

- fixture 1: 14095 / 14096;
- fixture 2: 24095 / 24096.

The existing manifest/generator/hash/parser/size/table-width checks are unchanged.

## Repair 3 — graph-bound controlled performance

### Observed failure

The previous freezer authenticated four controlled Development Players and their build-time comparability, but accepted fixture/replay graphs produced under different normal-M07 baseline IDs.

Pilot 1 independently reconstructed R00 inputs and failed before either Player launched.

### Strict build-map correction

Each side now has to prove before `ComparabilityPassed`:

- fixture manifest schema/milestone;
- fixture `baselineBuildId` equals both controlled ON/OFF receipts;
- fixture `runtimeAbiHash` equals both controlled ON/OFF receipts;
- Unity/target/architecture equality;
- fixture's exact `playerBuildReceiptPath/Sha256` is the controlled NativeOn receipt;
- replay binds the same fixture, NativeOn receipt, baseline, runtime ABI, build GUID, native library and platform.

`run-h1-paired-performance.py` now invokes this strict validator before launching a Player.

A normal-M07 graph paired with a separately rebuilt controlled Player can no longer reach sampling.

### Graph-bound producer

`Invoke-M07Build.ps1` now exposes:

`-ControlledPerformanceBuilds`

In this mode the existing workflow:

1. validates compiler inputs;
2. builds the baseline resource set;
3. builds NativeOn through `R00ControlledBuild.BuildPlayer` under the requested baseline;
4. builds NativeOff through the same controlled producer and baseline;
5. retains both controlled-evidence receipts;
6. runs structural Prepare/Compile/Restore;
7. finalizes fixtures/replay after the controlled NativeOn world exists;
8. publishes one M07 workflow receipt containing the graph and controlled evidence;
9. retains the existing outer exact-byte restoration contract.

Controlled-performance mode is mutually exclusive with the deliberate controlled-failure mode.

This path is usable both for the current profile-2 candidate and the protected profile-1 project via `-ProjectPath`.

## Broad-test drift closed

Local also identified two stale expectations unrelated to runtime behavior:

- `test_r01_early_launch` assumed `DEFAULT_MODES == MODES[:-1]`; it now derives the default inventory by excluding Baseline and dedicated continuation-only modes;
- `M07BuildTests.WorkflowRestoresExactProjectSettingsBytesAcrossFreshEditors` read only the outer wrapper while asserting core-owned strings; it now checks the outer and core files independently.

Primary CI directly executes the early-launch suite, and bounded M07 tests pin the Unity test's ownership model.

## Evidence preservation

The prior checkpoint remains immutable:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260919-authority99ef/`

Its failure states are not relabelled:

- Q04 strict verification: `Failed`;
- lazy Player: `FailedRuntimeNoDenseCoverage`;
- pilot 1: `FailedBeforePlayerLaunch`;
- formal performance: `Blocked / NotRun`.

The new source requires fresh evidence.

## Next Local cycle

1. fresh V00/V01 and broad Python/EditMode confirmation;
2. fresh current candidate provenance + M07;
3. startup/M07 matrix and Q04/Control/initializer strict verification;
4. fresh dense-v2 diagnostic Player and 4 boundary method calls;
5. fresh protected profile-1 verification;
6. graph-bound controlled-performance M07 workflow on profile 1;
7. graph-bound controlled-performance M07 workflow on profile 2;
8. strict freeze of those two matching graphs;
9. preregistration binding;
10. all pilot pairs;
11. formal paired performance only if pilots pass;
12. old-Player current-anchor check where required;
13. checkpoint before cleanup;
14. V05 + genuinely independent M08 only after mandatory V04 completion.

Do not begin R02.
