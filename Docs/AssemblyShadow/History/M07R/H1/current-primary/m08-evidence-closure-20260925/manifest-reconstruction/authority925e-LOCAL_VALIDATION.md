# Local Validation report

## Current run — 2026-09-19 authority `925e84d7`

### Exit

**Local Validation → Primary Implementation: RETURN REQUIRED after V04**

Fresh V00 authenticated candidate checkout `2bd1a86904f8cfeeadf55693641bc27f014538e9` and exact source anchor `925e84d7b653bc7434482e6f4fbde39a4d9fcd0e`. Candidate authority returned `SourceTargetVerifiedNotBuildAccepted`; reproduction tooling, the exact protected family, and both installed runtimes passed. No prior attempt was reused or relabelled.

V00–V03, normal M07, startup11, M07 14/14, strict failure/publication, deterministic dense-v2 real Player execution, ordinary and mixed capacity, and the retained parser/native matrix passed. The two requested graph-bound controlled-performance workflows both failed before their first controlled Player build at the same current-code parameter validation defect. The build map, preregistration, pilots, formal samples, analysis, V05, and M08 therefore did not run.

### Results

| Cell | Result | Evidence / disposition |
| --- | --- | --- |
| V00 candidate authority | `Passed` | `SourceTargetVerifiedNotBuildAccepted`; checkout `2bd1a869...`, source `925e84d7...` |
| V00 reproduction/protected refs | `Passed` | Reproduction-tooling authority and the exact protected four-repository family verified; candidate and protected installed runtimes matched source with Shadow ON |
| V01 complete Python inventory | `PassedWithExplicitSkips` | 1,015 discovered: 987 passed, 28 explicit skips, no failures |
| V01 bounded Primary | `Passed` | 323/323 |
| V01 broad Unity EditMode | `Passed` | 1,076/1,076, no failures or skips |
| V02/V03 provenance builds | `Passed` | Six fresh candidate/reproduction debug/release/ON/OFF cells, both strict compiler verifiers, and exact restoration passed |
| V04 normal M07 | `Passed` | `M07-Baseline-H1-925e-Normal-20260919A`; fresh fixture, ON/OFF, replay, link-input restoration, and outer restoration receipts |
| V04 startup11 | `PassedBoundedProfile` | 11 fresh PIDs; strict result passed |
| V04 M07 Player matrix | `PassedGate3B14Of14` | All 14 modes passed; no missing modes |
| V04 failure/publication | `Passed` | Schema v3; `transactionOwnership=EarliestStartup`; Control `Committed`, Q04 `Failed`, initializer `FailedAfterCommit`; bindings/capsules/early/late/raw/log hashes retained |
| V04 dense-v2 producer/parser | `Passed` | Two deterministic fixtures; dense native parser and bounded-reader sanitizer matrix passed |
| V04 dense-v2 diagnostic Player | `Passed` | 62 checks, `denseFixtures=2`, `denseBoundaryChecks=4`; ReturnIds 14095, 14096, 24095, 24096; capacity monotonic and inputs unchanged |
| V04 retained native matrix | `Passed` | M03–M06, budget, contention, recovery, startup, gateway, transaction, attribute, constraint, index-range/runtime, live capability, type cache, and codec kernel passed |
| V04 ordinary capacity | `Passed` | 8,192 assemblies / 536,870,912 bytes; 8,193rd refusal; real Player 516.1 s; strict verification passed |
| V04 exact mixed capacity | `Passed` | 536,733,184 ordinary + 137,728 Shadow = 536,870,912 bytes; five Shadow images, three retained failed reservations; real Player 537.4 s; strict verification passed |
| V04 protected profile-1 authentication | `Passed` | Protected commits and source anchor authenticated; runtime matched source before and after the failed workflow; worktree restored exactly |
| V04 controlled performance — profile 1 | `FailedBeforeControlledPlayerBuild` | Compiler authority and resource baseline passed, then `native-on-controlled` was rejected by the helper's `Label` `ValidateSet`; no controlled Player or workflow receipt produced |
| V04 controlled performance — profile 2 | `FailedBeforeControlledPlayerBuild` | Same exact current-code failure after authority and resource baseline; no controlled Player or workflow receipt produced; exact outer restoration and runtime re-verification passed |
| V04 old-Player current-anchor check | `Blocked / NotRun` | Required fresh profile-1 and profile-2 graphs do not exist |
| V04 frozen build map | `Blocked / NotRun` | Four controlled receipt/evidence pairs do not exist; `ComparabilityPassed` was not claimed |
| V04 preregistration / pilots / formal / analysis | `Blocked / NotRun` | Build-map prerequisite absent; no performance process or sample was launched |
| V05 / M08 | `Blocked / NotRun` | Mandatory V04 performance evidence is incomplete |

### Failure analysis

The direct failure is in `Tools/AssemblyShadow/Invoke-M07Build.Core.ps1`: `Invoke-M07PlayerMethodWithGeneratedInputRecovery` declares `Label` with `ValidateSet('native-on', 'native-off')`, while the `-ControlledPerformanceBuilds` branch calls it with `native-on-controlled` and `native-off-controlled`. PowerShell rejects the first value before `R00ControlledBuild.BuildPlayer` starts. The protected and candidate executions reproduced the same defect independently.

The design allowed the defect because broad and focused source tests validated workflow intent and graph binding without executing PowerShell's runtime parameter binder for this branch. The durable repair is to make the recovery helper's accepted stage vocabulary consistent with every real caller and add a direct PowerShell integration test that enters both controlled labels before Unity work, while retaining the existing exact-byte recovery contract.

Both failures occurred after source/runtime authority and resource baseline creation. The outer recovery receipts prove exact restoration; post-failure installed-runtime verification passed in both projects. They are functional workflow failures, not authority, provenance, shared-input corruption, or environmental unavailability.

### Retention checkpoint

The authenticated pre-cleanup checkpoint is [local-validation-20260919-authority925e](../History/M07R/H1/local-validation-20260919-authority925e/README.md). `MANIFEST.sha256` binds the report, summary, artifact index, and raw-evidence archive. Large payloads remain live and receipt-bound. No cleanup was performed.

H1 remains `InProgress`; the last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. `WEB_TO_LOCAL.md`, source/preflight verification, protected pins, and R02 were not modified.
