# Local Validation report

## Current run — 2026-09-23/24, repaired analysis-source handoff

### Exit

**Local Validation → Primary Implementation: FAIL at complete Python discovery.**

The final pushed Primary handoff was checked out cleanly at `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`, branch `codex/assembly-shadow-r01b-h1`, HEAD `dd3c8988e9136e0c3a8ca965f82067d6b7c83acd`. Its build-input/tool anchor remains `7aa6f61994da354b04464e38ddfc8552cc5c3055`. The other validation worktrees and matching pushed commits are `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` at `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` at `0ea633a2c5b936b5af69d944593c55bd2783fca9`, and `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` at `6be7f38bec2fa4677d24efc1a4a1294240789933`. All use the expected branch. Native/package/IL2CPP pins and the Unity package file reference resolve to this validation workspace. Exact repository inventories are in the new checkpoint's `V00/v00r-source-authority.json`.

V00.R passed: all nine restored `.agents`/`.codex` files are byte-identical to their `7aa6f619` Git blobs; the complete 7aa→HEAD non-metadata delta is empty. The 27df→HEAD non-metadata delta is exactly the fixed five analysis-only paths, and the retained 6913→7aa delta is exactly the 24-path allowlist. The committed V00 preflight returned `SourceTargetVerifiedNotBuildAccepted`. This authenticates source identity, not a new Player build or acceptance gate.

Bounded Primary regression passed 376/376. Complete Python discovery then executed 1,061 leaves: 1,032 `Passed`, 28 explicit `Skipped`, and one `Failed`. The failure is `test_h1_paired_performance.H1PairedPerformanceTests.test_analyze_sample_index_complete_positive`. Its synthetic `raw()` fixture stores build GUID, baseline ID, and runtime ABI only inside `playerBuildReceipt`; the corrected analyzer requires those three values at raw-result top level and rejects all 44 synthetic pilot/formal attempts with `R00 raw top-level build field differs: buildGuid`. The focused committed test reproduced this. Adding those top-level fields from the expected receipt **in memory only** made the focused test return `ComparabilityPassed`; no repository test or production source was edited. The bounded suite does not contain this failing positive test.

Changing the test file in this checkout would create a sixth non-metadata path after the fixed `7aa6f619` anchor and invalidate both current source preflight and the exact five-path historical compatibility rule. This is therefore a Primary source-authority decision, even though the test fixture defect itself is narrow. `RETURN_TO_WEB.md` gives the reproduction and corrective direction.

### Results

| Cell | State | Evidence and limit |
| --- | --- | --- |
| Four-repository Git/native/package preflight | `Passed` | `V00/v00r-source-authority.json`; exact pushed commits and clean checkouts before report edits |
| V00.R repaired source-authority audit | `Passed` | Nine restored bytes exact; 7aa→HEAD zero non-metadata; 27df→HEAD exact five; 6913→7aa exact 24 |
| V00 committed handoff/source preflight | `Passed` | `V00/handoff-preflight.json`; `SourceTargetVerifiedNotBuildAccepted` |
| V01 bounded Primary | `Passed` | 376/376, full inventory and log in `V01/bounded-primary/` |
| V01 complete Python discovery | `Failed` | 1,032 Passed / 28 Skipped / 1 Failed; `V01/python-inventory.json` and `python-tests.log` |
| V01 focused fixture diagnosis | `FailedAsCommitted`; `PassedWithInMemoryDiagnosticCorrection` | 44 invalid synthetic attempts as committed; no file edit or authoritative PASS claim |
| V02 historical checkpoint and four fixed live hashes | `PassedHistoricalIntegrityOnly` | 92/92 manifest entries and four SHA-256 matches; full live graph not reauthenticated this cycle |
| V04 historical compatibility preflight and corrected analysis | `Blocked / NotRun` | Complete Python prerequisite has one failure |
| Analysis-only closure checkpoint / V05 / independent M08 | `Blocked / NotRun` | V04 remains incomplete |
| Unity, IL2CPP, native builds, Players, profiler | `NotRun` | Current handoff is analysis-only; no new build GUID or execution evidence |

The run used Python 3.14.6 on macOS arm64; command receipts in the checkpoint record UTC start/end, exact commands, logs, paths, and exit codes. The handoff specifies Unity 2022.3.62f2 / StandaloneOSX / arm64; Unity was not invoked. The authenticated return checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority7aa6-python-fixture-blocked/`, containing all fresh V00/V01 and independent integrity evidence plus `MANIFEST.sha256`. The immutable source-27df execution checkpoint and 40/40 formal series remain historical; no Player was rerun and no historical receipt was changed. Earlier runtime evidence remains `ReusedAuditedFromFF3D`, earlier Unity EditMode 1,076/1,076 remains `ReusedAuditedFromD18`, and source-27df formal execution remains historical. None is relabelled as fresh current-source execution.

Primary must publish a coherent test-fixture correction and source/compatibility handoff. After it is pushed, Local must restart V00.R/V00, rerun the full Python suite, then perform complete live historical reauthentication, historical compatibility preflight, corrected analysis, checkpoint authentication, V05, and genuinely independent M08 in order. H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. R02 is closed.

## Historical run — 2026-09-23/24, source-pin mismatch

### Exit

**Local Validation → Primary Implementation: FAIL at V00 source authority.**

The latest pushed handoff was read at demo checkout HEAD `d7854b16c09b02d4494d28c2b0ea015ba83f58a3`, branch `codex/assembly-shadow-r01b-h1`, path `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`. Its declared analysis source/tool anchor is `7aa6f61994da354b04464e38ddfc8552cc5c3055`. All four validation worktrees are on the handoff branch, clean, and match the pushed remote heads. Their exact paths, commits, remotes, worktree registrations, package references, source pins, submodule inventories, and host versions are in the new checkpoint's `V00/repository-preflight.json`.

| Repository | Validation checkout | Pushed commit |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `d7854b16c09b02d4494d28c2b0ea015ba83f58a3` before this report commit |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |

Native, package, and IL2CPP pins equal those three repository commits. `Packages/manifest.json` resolves the HybridCLR Unity package to this validation workspace. No new build GUID or Player artifact was generated. The completed formal evidence remains bound to execution source `27df1a3d60811dc121f296ab561ae313a382b363` and retained graph source `69130bbb3a6df516916dddb5ad263799a7c6e5e3`; its four fixed live evidence hashes are recorded in `V02/historical-live-four-hashes.json`.

The current `h1_handoff_preflight.py --project <candidate> --role candidate --output <new V00 output>` returned exit 1: `Blocked: Demo HEAD contains build-input changes after the source pin`. The exact nine non-metadata changes from `7aa6f619` to `d7854b1` are the three `.agents/skills/agent-collaboration` files and six `.codex/agents` profiles. The source verifier compares the complete non-metadata Git tree at the pin to HEAD, so the migration commit `d7854b1` invalidated the pinned checkout. The source-to-source five-path analysis delta and 24-path retained-graph delta remain exact, but they do not authenticate this later HEAD.

### Results

| Cell | State | Evidence and limit |
| --- | --- | --- |
| V00 repository/branch/remote/native/package pins | `Passed` | `V00/repository-preflight.json`; clean worktrees and exact remote heads before report commit |
| V00 current committed handoff/source preflight | `Failed` | `V00/preflight.json`; source pin rejected before output receipt |
| V01 exact source-to-source audits | `PassedForAnchorsOnly` | `V01A/source-audits.json`: 27df→7aa exact five; 6913→7aa exact 24; 7aa→HEAD has nine non-metadata files |
| V02 historical checkpoint manifest | `PassedHistoricalIntegrityOnly` | 92/92 manifest entries verified in `V02/historical-checkpoint-manifest.log` |
| V02 four fixed live evidence hashes | `PassedHistoricalIntegrityOnly` | Bridge, seal, batch, and final sample hash-identical at original live paths; no full live graph reauthentication this cycle |
| V00 bounded Primary / complete Python discovery | `Blocked / NotRun` | Source preflight prerequisite failed |
| V04 historical compatibility and corrected analysis | `Blocked / NotRun` | Source-authority prerequisite failed; no analysis result claimed |
| V04 new checkpoint / V05 / independent M08 | `Blocked / NotRun` | No authenticated current analysis checkout |
| Unity, IL2CPP, native builds, Players, profiler | `NotRun` | Current handoff specifies analysis-only validation; no new execution evidence |

The fresh run used Python 3.14.6, PowerShell 7.6.3, and Git 2.50.1 on macOS arm64. The handoff specifies Unity 2022.3.62f2 / StandaloneOSX / arm64; Unity was not invoked. The preflight command, UTC start/end, exit code, stdout/stderr, Git inventories, full path lists, hashes, and manifest log are in `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority7aa6-source-pin-blocked/`. That checkpoint is the evidence for this return and references the immutable 27df execution checkpoint. Historical runtime, EditMode, pilot, and formal results remain historical and are not promoted to current-source PASS.

Primary must restore a coherent pushed handoff source identity while preserving the completed 40/40 formal series and the source verifier's fail-closed guarantee. `RETURN_TO_WEB.md` gives the reproduction and implementation boundary. After a new pushed handoff, Local must restart V00 and run V01, historical compatibility, corrected analysis, checkpoint, V05, and independent M08 in order. H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. R02 is closed.

## Historical run — 2026-09-23 authority `27df1a3d`

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
