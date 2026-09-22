# Local Validation report

## Current run — 2026-09-22 authority `91ac4db3`

### Exit

**Local Validation → Primary Implementation: RETURN REQUIRED after 14/40 formal pairs**

Fresh V00 authenticated candidate checkout `bb2bf106c172c985e9330de9cc0e2f58b24f096b` and exact source/tool anchor `91ac4db31cec704551c7db05bd918c8d5695ce83`. Candidate authority returned `SourceTargetVerifiedNotBuildAccepted`; reproduction tooling, the protected profile-1 family, and both installed runtimes passed. The candidate installed-runtime receipt was refreshed through the sanctioned `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability` path, then passed strict demo-source and Shadow-ON verification.

Fresh bounded Primary validation passed 364/364. Requested focused Python and PowerShell suites passed. Full Python discovery completed 1,049 leaves: 1,021 Passed, 28 explicit environment-bound Skipped, zero failures, and zero errors. The exact reviewed source audits passed: `24a0d3af... → 91ac4db...` contains the required 9 non-metadata paths and `69130bbb... → 91ac4db...` contains the required 22 paths, with no forbidden runtime or producer delta. Historical Unity 1,076/1,076 and retained-ON evidence remain only `ReusedAuditedFromD18`, not fresh current-source execution.

The retained V04 manifest, Player-artifact manifest, latest blocked-checkpoint manifest, protocol, schedule, build map, pilot index, five pilot attempts, four selected pilots, and eight selected launch receipts reauthenticated. Independent hashing verified 33,792 bound files totaling 1,606,993,133 bytes with zero content mismatches.

A new `H1GraphReuseBridge` passed as `AuthenticatedToolOnlySuccessor` with SHA-256 `b207fe8a91c15650d00670dd593207b00fed9a0e05cf618d13982b18402437a2`. It binds the exact retained runner SHA-256 `afc0b649579ebd497be493be9fd39fcfe19e3ba3074d6d6679e009975d21a07c` and current runner SHA-256 `a8de4dc1052306923f7aef529442d4c2012cc959c5dea58da6f15785caacd280`.

The new retained-pilot admission preflight passed with five retained attempts, four selected pilots, exact historical runner bindings, and no deep reconstruction. Its SHA-256 is `111c897d2925f0fb85a2b33d941e2a342a7984ba630c5b00ec1ed3f702608898`.

The new strict pilot seal passed with `deepLaunchVerificationCount=8`, 33,792 sealed files, and SHA-256 `25a768a7fd05e7d103aab31d42d2fcbc121423afbeeae73ffb180a7281d794cc`.

A new formal series started only from the retained pilot index. The first batch invocation hit a pre-launch output-name collision with preserved historical side output; Local retained that failed invocation and used the allowed absolute-output-path adjustment to run pair 1 directly. Pair 1 proved protected A had no formal authority, candidate B used the current runner and a valid `H1FormalSideLaunchAuthority`, the child consumed it, launched the Player, and emitted an R00 receipt echoing the same authority, bridge, seal, and map.

Formal pairs 1–14 passed: all 10 `R00-OFF-NoPatch` pairs and the first four `R00-ON-NoPatch` pairs. Pair 15 did not produce an output directory or sample index before its supervising terminal was interrupted; therefore it never became a protocol attempt and remains attempt 1.

On fail-closed resume from the authenticated pair-14 sample index, cached seal admission stopped before pair 15:

`Pilot verification cache invalidated by changed file identity: .../NativeOff.app/Contents/Frameworks/GameAssembly.dylib`

The sealed and current SHA-256 are both `ae75b36f20a8adf323a821ee2f2f585ae0bfc664e8e81063f8b3cc0ec4023b8d`. Size, inode, mode, mtime, and ctime are identical. Only `st_dev` changed from `16777229` to `16777230`. The seal correctly failed under its current contract. Local did not weaken the guard, rewrite the seal, relabel the existing formal series under a new seal, modify source/tool contracts, edit `WEB_TO_LOCAL.md`, run final analysis, enter V05/M08, or begin R02.

### Results

| Cell | Result | Evidence / disposition |
| --- | --- | --- |
| V00 candidate authority | `Passed` | Checkout `bb2bf106...`; exact `SourceTargetVerifiedNotBuildAccepted` for `91ac4db3...` |
| V00 reproduction/protected refs | `Passed` | Reproduction tooling `ba8fee33...`; protected profile-1 family exact |
| V00 installed runtimes | `PassedAfterCandidateReceiptRefresh` | Candidate receipt `570e2996...`; protected receipt `54bfe84c...` |
| V01 bounded Primary | `Passed` | 364/364 |
| V01 Python inventory | `CompletedWithExplainedEnvironmentSkips` | 1,049 total; 1,021 Passed; 28 environment Skipped; 0 failures/errors |
| V01 Unity EditMode | `ReusedAuditedFromD18` | Historical 1,076/1,076 only after exact source audit; not fresh execution |
| V01A source audits | `PassedExactSets` | Exact 9-path and 22-path non-metadata sets |
| V02 retained evidence | `PassedRetainedEvidenceReauthentication` | 33,792 files / 1,606,993,133 bytes / zero mismatches |
| V04 graph bridge | `Passed` | New bridge SHA `b207fe8a...`; retained runner SHA `afc0b649...` exact |
| V04 retained-pilot admission | `Passed` | 5 attempts; 4 selected; exact historical runner; no deep reconstruction |
| V04 strict pilot seal | `PassedThenFilesystemIdentityInvalidated` | Initially 8/8 deep sides; later `st_dev` changed while bytes and all other recorded guard fields remained identical |
| V04 formal pair 1 authority | `Passed` | Historical runner only in pilot provenance; current runner/current B authority; real Player launch |
| V04 formal series | `PartialPassedThenBlocked` | 14/40 Passed; pair 15 not started as a protocol attempt; 26 pairs remain |
| V04 final analysis | `NotRun` | Complete 40-pair index absent and seal cache invalid |
| V05 / independent M08 | `Ineligible / NotRun` | Mandatory V04 formal inventory and final analysis incomplete |

### Root cause and required Primary decision

The seal’s stat guard includes filesystem device identity. A host/filesystem remount can change `st_dev` while the file path, content hash, size, inode, permissions, mtime, and ctime remain unchanged. That makes a valid long-running formal series non-resumable under the current contract. This is fail-closed behavior, but it is also an operational portability problem for multi-hour/multi-day sealed runs.

Primary must decide whether device identity is intentionally acceptance-critical. If yes, Local must create a completely new bridge/seal and restart the formal series from the retained pilot index after establishing a stable mount; the 14 passed formal pairs remain historical and cannot be chained. If no, Primary must make and test a narrow source/tool correction defining a stable cross-remount identity guard while retaining SHA-256 and the other immutable fields. Local must not make that semantic change.

### Retention checkpoint

The authenticated blocked checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260922-authority91ac-formal-seal-invalidated/`. It contains current authority/tests/audits, retained evidence authentication, the new bridge/admission/seal, every completed formal sample index and side receipt, both pre-attempt interruption records, the seal-invalidation receipt, prior checkpoint manifest links, handoff snapshots, raw evidence, and a SHA-256 manifest. No retained evidence cleanup was performed.

H1 remains `InProgress`; the last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.
