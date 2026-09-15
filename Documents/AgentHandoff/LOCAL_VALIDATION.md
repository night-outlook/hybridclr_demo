# Local Validation report

## Current run — 2026-09-15

### Exit

**Local Validation → Primary Implementation**

The required authoritative preflight fails at published handoff HEAD `c0d3070e15682567bb1b2d693d7c7a4f9ea802fb` before source validation:

```text
Blocked: Incomplete handoff sections
```

Candidate/reproduction/runtime/performance heads and pin files were independently observed at the requested identities, but that does not replace the committed preflight. V01–V05 were therefore `Blocked / NotRun`. No Unity, installation, Player, runtime, performance, successor, or M08 command was started for this anchor. Human Review Gate remains not ready and R02 was not started.

### Source state observed before preflight

| Role | Branch | Exact observed HEAD | Result |
| --- | --- | --- | --- |
| Candidate demo | `codex/assembly-shadow-r01b-h1` | `c0d3070e15682567bb1b2d693d7c7a4f9ea802fb` | `Pass` |
| Candidate code anchor | same branch | `463ec3fab5d5e3bdbd09fe1970c21bf90f26ada9` | `Pass` in both source-target and pin files |
| Candidate native | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` | `Pass` |
| Shared package | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` | `Pass` |
| Shared IL2CPP | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` | `Pass` |
| Reproduction demo | `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` | `Pass`, unchanged |
| Reproduction native | `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` | `Pass`, unchanged |
| Performance reference | `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` | `Pass`, unchanged with its older profile |

The candidate demo and all three candidate runtime branches were explicitly pulled with `--ff-only`. Remote reproduction and performance heads were checked without moving their worktrees. Candidate native/package/IL2CPP, reproduction demo/native, and performance reference were clean. Candidate retained only the pre-existing untracked historical v7–v11 directories; they were not staged or modified.

### V00 preflight

Command from the candidate root:

```sh
python3 Tools/AssemblyShadow/h1_handoff_preflight.py --project /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo --role candidate --output /Users/ah/GitHub/hybridclr/h1-local-validation-20260915-c0d3070/v00/candidate-handoff-attempt2.json
```

- Exit code: `1`
- stdout: empty
- stderr: `Blocked: Incomplete handoff sections`
- Output JSON: `Unavailable`; verification failed before report creation
- Repeated invocation: same result
- `WEB_TO_LOCAL.md` SHA-256: `b89c4c156ae9687adaf81cc03f156cc601e58d89f8eb1ecd442ba03f8626cc68`
- `source-targets.json` SHA-256: `9645753dfb0ba422d2a7e7553dd2a53ed971d058ffe6287147848ce985ec53a4`
- source-pins SHA-256: `fbf3f556a75f5ed2555f111d111d4f5f178077cbf88e26a7edcb80419d765f30`
- preflight script SHA-256: `994e6e48c05aa15b2c66207a256ca76dcebdc8075bb9c1350d35e1d6f55263b1`

The script requires these exact heading substrings:

```text
## Objective
## Source targets
## Implementation
## Local validation
## Failure evidence
## Alternatives
## Risks
## Local correction boundary
## Human review gate
```

The published handoff omits four required substrings: `## Implementation`, `## Alternatives`, `## Risks`, and `## Human review gate`. Its `## Failure evidence to return` heading satisfies the script's substring check for `## Failure evidence`.

### Validation status

| Step | Result | Reason |
| --- | --- | --- |
| Preflight / V00 prerequisite | `Failed` | Published handoff is incompatible with its committed preflight contract |
| V01 source/tool/Unity regressions | `Blocked / NotRun` | Required preflight did not pass |
| V02 Apple-domain and failure-retention checks | `Blocked / NotRun` | Required preflight did not pass |
| V03 install, smoke, and remaining builds | `Blocked / NotRun` | Required preflight did not pass |
| V04 runtime/count/startup/performance | `Blocked / NotRun` | No accepted source preflight or fresh builds |
| V05 successor and independent M08 | `Blocked / NotRun` | Acceptance chain has no valid inputs |

No bounded local fix was made because `WEB_TO_LOCAL.md` is Primary-owned and changing the preflight contract would change source/acceptance semantics. Evidence is committed under [local-validation-20260915-c0d3070](local-validation-20260915-c0d3070/README.md). The actionable issue is at the top of [RETURN_TO_WEB.md](RETURN_TO_WEB.md).

---

## Historical run — 2026-09-14

Validation date: 2026-09-14 (America/Los_Angeles)

## Exit

**Local Validation → Primary Implementation**

V00 and V01 passed. V02 reproduced the Apple Bee/PCH provenance blocker. In V03, both pinned runtimes installed and verified, and the fresh candidate ON/Debug Player build completed, but the mandatory native-provenance capture failed on the same macro-scope disagreement. No provenance-bound smoke receipt exists, so the other five builds and V04–V05 acceptance chain are blocked. Independent whole-chain M08 was not run, Human Review Gate is not ready, and R02 was not started.

## Validated source state

| Role | Working copy | Branch | Validated checkout HEAD | Code anchor |
| --- | --- | --- | --- | --- |
| Candidate demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | `bec2bd1936171313663a425d63bd3b0249b171c5` | `54259ef467e3937fe1879161aa552e42eb7e5854` |
| Reproduction demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r_repro/hybridclr_demo` | `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` | `4e3d2035991ab5629265ac663e61bcb2ca62828b` |
| Candidate native | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` | same |
| Reproduction native | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r_repro/hybridclr` | `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` | same |
| Shared package | candidate/reproduction sibling checkouts | candidate branch / detached exact pin | `0ea633a2c5b936b5af69d944593c55bd2783fca9` | same |
| Shared IL2CPP | candidate/reproduction sibling checkouts | candidate branch / detached exact pin | `6be7f38bec2fa4677d24efc1a4a1294240789933` | same |
| Performance reference | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r_reference/hybridclr_demo` | `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` | same |

All named branches were explicitly pulled with `git pull --ff-only`. Candidate and reproduction runtime repositories matched `source-targets.json`. The performance reference retained its own older profile and was not reinstalled. The original dirty `main` checkout was not used or changed. Candidate's pre-existing untracked historical `v7`–`v11` directories were preserved and excluded from this publication.

## Environment

- macOS 26.5.2 (25F84), arm64
- Unity 2022.3.62f2, StandaloneOSX arm64
- Apple clang 21.0.0 (`clang-2100.1.1.101`)
- Python 3.14.6
- PowerShell 7.6.3
- Git 2.50.1 (Apple Git-155)
- Free disk before build: 42 GiB

## Validation results

| Step | Result | Empirical result |
| --- | --- | --- |
| V00 handoff preflight | `Pass` | Candidate and reproduction each returned `SourceTargetVerifiedNotBuildAccepted`; handoff, branches, anchors, pins, and source-pin bytes matched. |
| V01 Python | `Pass` | Candidate 345/345 and reproduction 99/99 leaf tests passed. Exact IDs are in the committed inventories. The reproduction checkout lacked the inventory wrapper (`Unavailable`); its present test tree was run through the byte-identical candidate read-only wrapper. |
| V01 Unity compile | `Pass` | Candidate and reproduction batch compiles exited 0 on Unity 2022.3.62f2. |
| V01 NUnit | `Pass` | In each checkout, `H1PchEvidenceProcessTests` passed 4/4 and `H1EvidenceProcessTests` passed 10/10. Commands used `-runTests` without `-quit`; exact case IDs and XML are retained. |
| V02 old PCH diagnostic | `Fail` | Exact old request, DAG, and PCH bytes were available when executed. `h1_pch_diagnose.py` exited 1: `Translation units disagree on effective diagnostic macros (link flags are not compile evidence)`. The old request and derived 446-action diagnostic are retained; the raw old DAG is `Unavailable` after the fresh build replaced the mutable Bee graph. |
| V03 pinned install | `Pass` | Candidate and reproduction `PinnedSourceInstaller.Install` exited 0. |
| V03 installed runtime verification | `Pass` | Both reported Unity 2022.3.62f2, 955 source files, 957 installed files, demo source verified, mode `on`. Candidate receipt SHA-256 `3fcd683717f642c6175bc0b41ad719277ba73525500e792ba70f8f16ec8a9f81`; reproduction `9bc67b11d27ebf2e6bcb35f42051e31ced95f6ab68ba4c139220447b4fb6678b`. |
| V03 smoke dry plan | `Pass` | Planned only candidate / on / Debug with `humanGatePassed=false`, `mayEnterR02=false`. |
| V03 fresh smoke | `Fail` | Player build succeeded, then mandatory `h1_native_capture.py` failed on macro consistency. Source restoration was exactly verified. No build receipt was produced. |
| V03 remaining five builds | `Blocked` / `NotRun` | The verified candidate ON/Debug smoke receipt is a dependency. |
| V04 runtime/count/startup/repro/performance chain | `Blocked` / `NotRun` | No fresh provenance-bound Player set exists. Historical results were not promoted. |
| V05 successor and independent M08 | `Blocked` / `NotRun` | Successor inputs are incomplete; no independent whole-chain M08 was commissioned. |

## Commands and bounded invocation corrections

The authoritative preflight ran `h1_handoff_preflight.py --role candidate|reproduction` with new output files. Candidate and reproduction Python inventories used `h1_test_inventory.py`; Unity compile and NUnit used the repository PowerShell ownership/Unity runners. Raw commands, XML, stdout/stderr, and exit records are in `local-validation-20260914-bec2bd1/validation-raw-results.tar.gz`.

The PCH replay command was:

```sh
python3 Tools/AssemblyShadow/h1_pch_diagnose.py --request /ABS/OLD_REQUEST.json --graph /ABS/OLD_GRAPH.json --output /Users/ah/GitHub/hybridclr/h1-local-validation-20260914-bec2bd1/v02/pch-diagnostic
```

The fresh smoke command was:

```sh
python3 Tools/AssemblyShadow/h1_count_build_batch.py --candidate /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo --reproduction /Users/ah/GitHub/hybridclr/assembly_shadow_h1r_repro/hybridclr_demo --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity --pwsh /usr/local/bin/pwsh --scope smoke --output /Users/ah/GitHub/hybridclr/h1-local-validation-20260914-bec2bd1/v03/smoke-execute-2 --execute
```

Two local invocation errors were retained and corrected without source changes: the runtime verifier wrapper already inserts its `verify` operation, and the build batch requires an absent output directory. Both corrected invocations reached their intended checks. These are not product failures.

## Fresh smoke identity and restoration

- Build ID: `H1Count-On-Debug`
- Build GUID: `4ca877a4f3bf4c708d43089f6016f9fb`
- Input snapshot: `3cbdc85d75bf7b185936b9dff450dfdd43f60a91d46875ed8be112069b3b8418`
- `GameAssembly.dylib`: 101,101,414 bytes, SHA-256 `d26b47e1f83781ff0bf14baa178e8ace3184ff52552177e53109e21abff981c6`
- Selected fresh DAG: SHA-256 `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181`
- Candidate source-pin bytes: SHA-256 `d0d160d18cfdc281947c0d2b0b68de60a93d96f91cc93addcc74f1123c55c846`
- Build process: exit 1 after Unity reported `Build Finished, Result: Success` and the provenance adapter threw.
- Restore process: exit 0. The four diagnostic scene fields and known settings serialization were the only changes; recorded before bytes were restored and `ExactRestorationVerified` was written.

The fresh DAG has 446 native compile actions. All carry `HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1` and `HYBRIDCLR_H1_COUNT_DIAGNOSTICS=1`, but the current parser derives two assertion/debug groups: 16 C actions with `IL2CPP_DEBUG=0, NDEBUG=0, IL2CPP_DEVELOPMENT=0`, and 430 actions including both PCH producers with `IL2CPP_DEBUG=1, NDEBUG=0, IL2CPP_DEVELOPMENT=0`.

## Evidence

Portable checkpoint: [local-validation-20260914-bec2bd1](local-validation-20260914-bec2bd1/README.md).

- `candidate-python-inventory.json` and `reproduction-python-inventory.json` contain every Python test ID and result.
- Four committed NUnit inventories contain every case ID and result; raw XML and Unity logs are in `validation-raw-results.tar.gz`.
- V02's original request and full derived action inventory are committed. Its raw old DAG was not copied before the fresh build replaced `Library/Bee`, so that one input is honestly `Unavailable` for portable old-attempt replay. The V03 fresh failure independently reproduces the same split and retains its complete raw DAG.
- `fresh-smoke-failure-inputs.tar.gz` is the portable failure bundle. It contains the raw DAG, both original PCHs, raw module-file-info, all 833 referenced header/config bytes, SDK settings, managed begin capture, raw Unity failure log, exact macro-action inventory, and restoration files.
- The exact compiler and selected native library are identified by path, size, and SHA-256 in the failure manifest. The 290,664,032-byte compiler and 101,101,414-byte native binary remain in the immutable local failure root and were not duplicated into Git. The selected graph has no libtool action.
- Full local raw root: `/Users/ah/GitHub/hybridclr/h1-local-validation-20260914-bec2bd1`.
- Failed preparation root: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/H1CountBuild-4546fb1a522d4b658a271e93c55d0b3e`.

No executable source was changed. The actionable nontrivial issue is in [RETURN_TO_WEB.md](RETURN_TO_WEB.md).
