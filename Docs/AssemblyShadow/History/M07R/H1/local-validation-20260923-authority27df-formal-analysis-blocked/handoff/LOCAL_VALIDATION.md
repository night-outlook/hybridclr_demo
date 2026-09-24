# Local Validation report

## Current run — 2026-09-23 authority `27df1a3d`

### Exit

**Local Validation → Primary Implementation: RETURN REQUIRED after 40/40 formal pairs**

Fresh V00 authenticated candidate checkout `f5e34235641c212c715aef3405925ddd4cf28ee6` and exact source/tool anchor `27df1a3d60811dc121f296ab561ae313a382b363`. Candidate authority returned `SourceTargetVerifiedNotBuildAccepted`; reproduction tooling, the protected profile-1 family, and both installed runtimes passed. The candidate installed-runtime receipt was refreshed through the sanctioned `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability` path, then passed strict verification.

Fresh bounded Primary validation passed 368/368. The focused suite passed 126/126, both requested PowerShell recovery suites passed, and full Python discovery completed 1,053 leaves: 1,025 Passed, 28 explicit environment-bound Skipped, zero failures, and zero errors. The exact source audits passed: `91ac4db3... → 27df1a3d...` contains the required 3 non-metadata paths and `69130bbb... → 27df1a3d...` contains the required 22 paths, with no forbidden runtime or producer delta. Historical Unity 1,076/1,076 remains only `ReusedAuditedFromD18`, not fresh current-source execution.

The retained V04 manifests, build map, protocol, schedule, pilot index, five pilot attempts, four selected pilots, and eight selected launch receipts reauthenticated. Independent hashing verified 33,792 bound files totaling 1,606,993,133 bytes with zero content mismatches.

A new `H1GraphReuseBridge` passed as `AuthenticatedToolOnlySuccessor` with SHA-256 `c03665dbdba797f5024fa8f376e6ac6aa6edf165c76387ddbf01ee6d3611826c`. It binds the exact retained runner SHA-256 `afc0b649579ebd497be493be9fd39fcfe19e3ba3074d6d6679e009975d21a07c` and current runner SHA-256 `a8de4dc1052306923f7aef529442d4c2012cc959c5dea58da6f15785caacd280`.

The retained-pilot admission preflight passed with five retained attempts, four selected pilots, exact historical runner bindings, and no deep reconstruction. Its SHA-256 is `cbfc6faf8512a214ff97fa939bc6335b05a36362d66b539ff22e954c61529ed1`.

The new guard-v2 strict seal passed with `guardKind=CrossRemountStableStatGuard`, `guardVersion=2`, guard fields exactly `[inode, mode, size, mtimeNs, ctimeNs]`, no device field, `deepLaunchVerificationCount=8`, and 33,792 sealed files. Its SHA-256 is `bdc4062acfc6d208a9be50a142b897a07e7359e5df14ad3d3d8f2805c5179631`.

A wholly new formal series started from the retained pilot index, without chaining either historical failed series. The batch runner automatically used path-hash namespace suffix `7cafb9c53434`, so pair 1 did not collide with preserved project-local outputs. Pair 1 proved protected A had no formal launch authority, while candidate B received and consumed a valid current `H1FormalSideLaunchAuthority`, passed retained graph preparation, launched the Player, and emitted an R00 receipt echoing the same authority, bridge, seal, and build map.

All 40 formal pairs passed on their first protocol attempt: 10/10 OFF-NoPatch, 10/10 ON-NoPatch, 10/10 ON-P01, and 10/10 ON-P03. No whole-pair retry was required. The batch receipt is `PassedAllFormalPairs`, SHA-256 `97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667`; the final cumulative index SHA-256 is `a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021`.

The bridge-aware strict analyzer completed after reconstructing the cumulative chain, but returned `Incomplete` / `ComparabilityIncomplete`. Build-map comparability and chronology passed. Of 45 cumulative attempts, 44 were rejected by the same receipt-shape check:

`R00 raw build field differs: baselineBuildId`

The raw R00 top-level `baselineBuildId` and `runtimeAbiHash` are correct and match the frozen build. The nested raw `playerBuildReceipt` correctly binds its path, SHA-256, and build GUID, but omits `baselineBuildId` and `runtimeAbiHash`. The final analyzer requires those fields inside the nested receipt. The omission is identical across protected/candidate and the 44 otherwise analyzable pilot/formal attempts. The remaining cumulative attempt is the already-preserved historical `R00-ON-NoPatch-pilot-01` failure: its A-side runner process group could not be proven gone, so B was skipped. Local reproduced the receipt-shape failure through the analyzer's isolated build-binding check and retained a machine-readable diagnosis. This is a source/tool contract failure, not a formal pair failure; retrying current formal pairs would reproduce the same immutable receipt shape.

Local did not modify the producer, analyzer, `WEB_TO_LOCAL.md`, or any source/tool contract; did not relabel the formal evidence; did not enter V05/M08; and did not begin R02.

### Results

| Cell | Result | Evidence / disposition |
| --- | --- | --- |
| V00 candidate authority | `Passed` | Checkout `f5e34235...`; exact `SourceTargetVerifiedNotBuildAccepted` for `27df1a3d...` |
| V00 reproduction/protected refs | `Passed` | Reproduction tooling on its actual branch worktree; protected profile-1 family exact |
| V00 installed runtimes | `PassedAfterCandidateReceiptRefresh` | Candidate receipt SHA `4d8afaea...`; protected receipt SHA `54bfe84c...` |
| V01 bounded Primary | `Passed` | 368/368 |
| V01 focused validation | `Passed` | 126/126 plus both PowerShell recovery suites |
| V01 Python inventory | `CompletedWithExplainedEnvironmentSkips` | 1,053 total; 1,025 Passed; 28 environment Skipped; 0 failures/errors |
| V01 Unity EditMode | `ReusedAuditedFromD18` | Historical 1,076/1,076 only after exact source audit; not fresh execution |
| V01A source audits | `PassedExactSets` | Exact 3-path and 22-path non-metadata sets |
| V02 retained evidence | `PassedRetainedEvidenceReauthentication` | 33,792 files / 1,606,993,133 bytes / zero mismatches |
| V04 graph bridge | `Passed` | New bridge SHA `c03665db...`; retained runner SHA `afc0b649...` exact |
| V04 retained-pilot admission | `Passed` | 5 attempts; 4 selected; exact historical runner; no deep reconstruction |
| V04 guard-v2 pilot seal | `Passed` | Stable stat guard exact; no device; 8/8 deep sides; SHA `bdc4062a...` |
| V04 formal pair 1 authority | `Passed` | A has no authority; current B authority consumed; real Player launch; receipt echo exact |
| V04 formal series | `PassedAllFormalPairs` | 40/40 first-attempt passes; 10 per mode; zero retries |
| V04 final analysis | `Incomplete` | `ComparabilityIncomplete`; 0 valid / 45 invalid: 44 nested-receipt schema mismatches plus 1 preserved historical pilot process-cleanup failure |
| V05 / independent M08 | `Ineligible / NotRun` | Mandatory V04 final analysis did not pass |

### Root cause and required Primary correction

The Player-side R00 producer and strict final analyzer disagree about the nested raw build-receipt schema. The producer places `baselineBuildId` and `runtimeAbiHash` at R00 top level but not inside `playerBuildReceipt`; the analyzer requires the same values inside `playerBuildReceipt`. The design allowed the mismatch because launch-time and cached-admission verification authenticated path/hash/build-GUID and top-level authority, while the final analyzer applied a stricter nested-field contract only after the complete series.

Primary must reconcile this contract and add fail-closed coverage. The durable choices are to make the producer echo both fields into the nested receipt, or to deliberately revise the analyzer to bind the authenticated top-level fields instead. Primary must also decide, based on the corrected contract and immutability rules, whether these 40/40 raw attempts may be reanalyzed or whether a new formal series is required. Local must not make that semantic decision.

### Retention checkpoint

The authenticated checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260923-authority27df-formal-analysis-blocked/`. It contains current authority/tests/audits, retained evidence authentication, the new bridge/admission/guard-v2 seal, all 40 cumulative sample indexes, the batch receipt, strict analyzer output and logs, the contract-failure diagnosis, prior checkpoint manifest links, handoff snapshots, raw evidence, all referenced formal side evidence, and a SHA-256 manifest. The large side-evidence archive is split into ordered parts for Git transport; concatenating the parts reconstructs aggregate SHA-256 `fda8226ee124ecc7d6687e2bbbab30d2166c838fd5fc7225b9972d949982f75f`.

H1 remains `InProgress`; the last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.
