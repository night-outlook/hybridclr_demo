# Local Validation report

## Current run — 2026-09-15 handoff 8f5bcaa

### Exit

**Local Validation → Primary Implementation**

Fresh V00 and V01 pass. V02 proves that both the retained real Apple replay and the new store contract cross the former 267,613,743-byte failure point: all 448 declared paths are available, 315,422,684 nominal bytes become 318,212,421 logical unique retained bytes and 72,612,459 physical stored bytes, and `h1_verify_capture_store.py` passes. Planning, exact PCH replay, all six compiler probe contexts, 446-action domain classification, and 444-object linkage also complete.

The prioritized fresh V03 candidate ON/Debug Player builds and passes strict native provenance plus independent store verification. The required managed-source verifier then fails with `Blocked: Missing or ambiguous managed action chain for AssemblyShadow.R01BDiagnostics`. The exact Player managed actions exist in an unchanged pre-existing Bee DAG and their DLL outputs existed before the build; the current capture admits only new/changed DAGs and therefore retains zero managed compilation rows. Changing graph freshness or reuse equivalence is a provenance-semantic change, so no local allowlist or policy adjustment was made.

The remaining five builds and V04–V05 are `Blocked / NotRun`. Independent whole-chain M08 was not commissioned. Human Review Gate is not ready, `humanGatePassed=false`, `mayEnterR02=false`, and R02 was not started.

### Validated source state

| Role | Branch | Exact observed HEAD | Result |
| --- | --- | --- | --- |
| Candidate handoff checkout | `codex/assembly-shadow-r01b-h1` | `8f5bcaa687e33e8666eacc942b5e414a83b737fc` | `Pass` |
| Candidate source/implementation anchor | same branch | `91ebef56eaa7034ed49a80bced422ea4c067d2fe` | `Pass` in source target and pin file |
| Candidate native | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` | `Pass`, clean |
| Shared package | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` | `Pass`, clean |
| Shared IL2CPP | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` | `Pass`, clean |
| Reproduction demo | `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` | `Pass`, unchanged |
| Reproduction native | `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` | `Pass`, unchanged |
| Performance reference | `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` | `Pass`, unchanged |

The candidate was explicitly pulled with `git pull --ff-only origin codex/assembly-shadow-r01b-h1`. Candidate retained only the pre-existing untracked historical `v7`–`v11` directories in addition to this new checkpoint. Reproduction and performance-reference worktrees remained clean and were not repointed or reinstalled.

### Environment

- macOS 26.5.2 (25F84), arm64
- Unity 2022.3.62f2, StandaloneOSX arm64
- Apple clang 21.0.0 (`clang-2100.1.1.101`)
- Python 3.14.6
- PowerShell 7.6.3
- Git 2.50.1 (Apple Git-155)

### Validation results

| Step | Result | Empirical result |
| --- | --- | --- |
| V00 authoritative preflight | `Pass` | Exit 0; `SourceTargetVerifiedNotBuildAccepted`; checkout `8f5bcaa…`; code source `91ebef56…`; native installation false; both gate flags false. |
| V01 Bee Primary | `Pass` | Fresh exact bounded suite 256/256. The initial pre-existing-output invocation failure is retained. |
| V01 H1 Python | `Pass` | Fresh leaf inventory 451/451. |
| V01 strict provenance / normal M02 owner | `Pass` | 4/4 and 15/15. |
| V01 candidate Unity | `Pass` | Fresh compile; corrected focused NUnit 4/4 and 10/10; full demo Editor regression 351/351; package Editor regression 720/720. Initial zero-test filter attempts are retained as failures. |
| V01 reproduction Unity | `CompletedWithNonPass` | Fresh compile and focused NUnit 14/14 passed. Optional full demo sweep completed 330/342 with the same 12 historical missing managed-source/baseline/linked-input failures. |
| V02 retained Apple replay | `Pass` for diagnostics | `DiagnosticReplayVerifiedNotBuildAccepted`; 446 compiler actions, 444 linked objects, domains 430 runtime / 2 BDWGC / 14 zlib, two PCH producers, six probe contexts, all reached processes exit 0. |
| V02 real retention volume | `Pass` for store integrity | 448/448 declared paths; 315,422,684 nominal bytes; 451 observations/content/blobs; 318,212,421 logical bytes; 72,612,459 stored bytes; 444 `zlib-v1`, 7 `raw-v1`. |
| V02 independent store verifier | `Pass` | Exit 0; `StoreVerifiedNotAcceptance`; raw/stored identities and accounting authenticate. |
| V02 fail-closed controls | `Pass` | 6/6: old-boundary volume, compressed tamper, corrupt finalization, incompressible raw fallback, logical limit and stored limit. |
| V03 pinned install / runtime verification | `Pass` | Install passed. Correct verifier invocation reports 955 source files, 957 installed files, demo source verified, mode `on`, receipt SHA-256 `9644959a1832d14992a5b1dedd959b4922d24d3c79aebccca9d92c6788bd7c94`. The initial duplicate-operation invocation exited 2 and is retained. |
| V03 candidate ON/Debug native smoke | `Pass` through native provenance | Player build, native strict verifier, fresh store verifier, Apple domains/PCH/probes, and exact restoration pass. |
| V03 managed-source provenance | `Fail` | Managed capture records one new native graph and zero managed compilation rows. Required C# actions exist only in unchanged cached Bee graphs and outputs. |
| V03 remaining five builds | `Blocked / NotRun` | A valid candidate ON/Debug smoke receipt is required. |
| V04 runtime/count/startup/performance | `Blocked / NotRun` | No six-build fresh provenance set exists. |
| V05 successor and independent M08 | `Blocked / NotRun` | Successor inputs are incomplete; M08 was not commissioned. |

### Fresh smoke identity

- Build ID: `H1Count-On-Debug`
- Build GUID: `540065befa904f7f880ab13416c0f852`
- Input snapshot SHA-256: `7ddd2f21c4718469ec06998ce3f19e2ff0100cc28eda2c4b5a2431a6eab753d5`
- Fresh Bee DAG SHA-256: `3115788e4cdae9f9a4021dc8f5f27f4d5efd9ac5c819bcc30fb5298072832c95`
- `GameAssembly.dylib` SHA-256: `9acf78528cda4587f0cf97b4a2e565767e57962c863da19f30479276f91c4ba0`
- Build receipt SHA-256: `3043f69397cb8cc0dc4a798cbfe851f02f65031a6d8a23f2b31f09dec1ce1a92`
- Compiler provenance SHA-256: `13a2fe9f1ce20a8db3d120b38e18e93040117edf94ea8fb8127cd4acbd998109`
- Retention inventory SHA-256: `089060a3ca2ea4e9eb162c4f9bf9b90a77819b455bed7faa8119ed6ab45629dc`
- Restoration: `ExactRestorationVerified`

Portable evidence is under [local-validation-20260915-8f5bcaa](../../Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260915-8f5bcaa/README.md). The full unpacked roots remain at `/Users/ah/GitHub/hybridclr/h1-local-validation-20260915-8f5bcaa` and `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/H1CountBuild-e347902b06224cbc8af39ec58902fafa`.

---

## Current run — 2026-09-15 handoff 22eda8b

### Exit

**Local Validation → Primary Implementation**

The repaired authoritative V00 preflight passed, and fresh V01 candidate validation passed. V02 and the prioritized fresh V03 candidate ON/Debug smoke then independently reached the same new provenance blocker: `h1_capture_attempt.Attempt` exhausts its fixed 256 MiB aggregate retention budget while copying the real Apple Bee graph's declared native inputs. Both attempts stop before planning, PCH replay, or macro probes. The fresh Player build completes, but no compiler-provenance receipt or accepted build receipt exists.

The remaining five builds, V04, V05 successor packaging, and independent whole-chain M08 are therefore `Blocked / NotRun`. Human Review Gate is not ready, `humanGatePassed=false`, `mayEnterR02=false`, and R02 was not started.

### Validated source state

| Role | Branch | Exact observed HEAD | Result |
| --- | --- | --- | --- |
| Candidate handoff checkout | `codex/assembly-shadow-r01b-h1` | `22eda8b9d27c2494cdf66749aefebcbbc8701371` | `Pass` |
| Candidate source anchor | same branch | `b6db7c2fb2fce364d49458b7dfc78886fd430004` | `Pass` in source target and pin file |
| Candidate implementation anchor | same branch | `463ec3fab5d5e3bdbd09fe1970c21bf90f26ada9` | `Pass` |
| Candidate native | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` | `Pass`, clean |
| Shared package | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` | `Pass`, clean |
| Shared IL2CPP | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` | `Pass`, clean |
| Reproduction demo | `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` | `Pass`, unchanged |
| Reproduction native | `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` | `Pass`, unchanged |
| Performance reference | `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` | `Pass`, unchanged |

The candidate was explicitly pulled with `git pull --ff-only origin codex/assembly-shadow-r01b-h1` and reached the requested handoff. Candidate retained only the pre-existing untracked historical `v7`–`v11` directories. Reproduction and performance-reference worktrees remained clean and were not repointed or reinstalled.

### Environment

- macOS 26.5.2 (25F84), arm64
- Unity 2022.3.62f2, StandaloneOSX arm64
- Apple clang 21.0.0 (`clang-2100.1.1.101`)
- Python 3.14.6
- PowerShell 7.6.3
- Git 2.50.1 (Apple Git-155)

### Validation results

| Step | Result | Empirical result |
| --- | --- | --- |
| V00 authoritative preflight | `Pass` | Exit 0; `SourceTargetVerifiedNotBuildAccepted`; checkout `22eda8b…`; code source `b6db7c2…`; native installation false; both gate flags false. |
| V01 Bee Primary | `Pass` | Fresh exact bounded suite 250/250. |
| V01 H1 Python | `Pass` | Fresh leaf inventory 445/445. |
| V01 strict provenance / normal M02 owner | `Pass` | 4/4 and 15/15. |
| V01 candidate Unity | `Pass` | Fresh batch compile; focused NUnit 4/4 and 10/10; full Editor regression 351/351. |
| V01 reproduction Unity | `CompletedWithNonPass` | Fresh compile and focused NUnit 14/14 passed. An additional full sweep completed 330/342 with 12 preserved failures: six managed-source setup failures on the reproduction nested asmdef, one missing M01 baseline, and five missing M05 linked inputs. |
| V02 authenticated graph census | `Pass` for inventory only | Historical failure archive and graph hashes authenticated; 446 compiler actions observed. This inventory does not approve domains or acceptance. |
| V02 real retained replay | `Fail` | Retained 337 observations / 267,613,743 unique bytes, then exceeded the 256 MiB total bound on `UnityEngine.UIElementsModule__7.cpp`. Stage `declared-input-retention`; planning/PCH replay/macro probes `NotRun`. |
| V02 bounded negative planning | `Pass` | Synthetic 16/430 split retained request/graph/config, failed at `planning`, and recorded PCH replay/macro probes `NotRun`. |
| V03 pinned install | `Pass` | Candidate `PinnedSourceInstaller.Install` exited 0. |
| V03 installed-runtime verification | `Pass` | 955 source files, 957 installed files, `demoSourceVerified=true`, Shadow mode `on`, receipt `3e332c26e8cbcbaf803d82707d7f4937262ddb2dd66d6af1673823184e98da19`. |
| V03 candidate ON/Debug smoke | `Fail` | Player build completed; mandatory provenance capture failed at the same retention boundary. No provenance or build receipt. Exact restoration verified. |
| V03 remaining five builds | `Blocked / NotRun` | A valid candidate ON/Debug smoke receipt is required. |
| V04 runtime/count/startup/performance | `Blocked / NotRun` | No fresh provenance-bound Player set exists. |
| V05 successor and independent M08 | `Blocked / NotRun` | Successor inputs are incomplete; M08 was not commissioned. |

The first installed-runtime command incorrectly supplied the wrapper's implicit `verify` operation and exited 2; its raw output is preserved. The corrected invocation passed. No production source or acceptance policy was changed locally.

### Fresh smoke failure identity

- Build ID: `H1Count-On-Debug`
- Build GUID: `9638639b2bfe41b793b8bb629f1801ff`
- Input snapshot: `fdcb5eb0bef2eb34567f242de74db10a3b132cfd0d7d9712bca4e1e12cc24d17`
- Fresh Bee DAG: 2,766,362 bytes, SHA-256 `a1a3eede51e061b4e9da2b9d5a5f4e119b9535434e896db3a55609a7c249ae37`
- `GameAssembly.dylib`: 101,101,430 bytes, SHA-256 `f731d42f4ff9a91a240afa80310e126458232bacb5859fecb4efba02823155db`
- Attempt inventory: SHA-256 `f01a19f6b49ee2df1ae1c94699903ea47bba6b0eabce79918acbc7660c2b85ac`
- Failure: `Capture input exceeds retention byte bound: .../UnityEngine.UIElementsModule__7.cpp`
- Restoration: `ExactRestorationVerified`

Portable evidence is under [local-validation-20260915-22eda8b](../../Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260915-22eda8b/README.md). The unpacked raw roots remain at `/Users/ah/GitHub/hybridclr/h1-local-validation-20260915-22eda8b/v02/retained-apple-replay` and `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/H1CountBuild-fa63d77e368c42d0b558979fecb5fc1b`.

---

## Historical run — 2026-09-15 c0d3070 handoff

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
