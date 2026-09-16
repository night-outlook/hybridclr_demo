# Local Validation report

## Current run — 2026-09-16 handoff 534b03e

### Exit

**Local Validation → Primary Implementation**

The candidate branch was explicitly fast-forwarded to handoff `534b03eb49140eb7f9d9fbdb64217e113a317626`; candidate source anchor `1b1cc9fe192b88be2a20fad31ea030b1e30be669` and all protected runtime/reproduction/performance pins match. A separate checkout was created for `codex/assembly-shadow-h1-count-repro-tooling` at exact `0c9c2508d94a097dff50028212a01695c8e29c60`. Both V00 authority checks pass.

V01 candidate checks pass: H1 Python 472/472, bounded Bee Primary 294/294, Unity 2022.3.62f2 compilation with zero errors, and focused NUnit 4/4 plus 10/10. The exact reproduction-tooling checkout fails Unity compilation at `Assets/AssemblyShadowDemo/Tests/Editor/H1ManagedSourceProvenanceTests.cs(13,43)` with CS0426 because its historical test still references `H1ManagedSourceProvenance.Capture`, a nested type removed by the current schema-3 bridge.

The current bridge blob is correctly authenticated and the post-failure tooling preflight still passes. The stale test blob is inherited unchanged from protected reproduction; the candidate source anchor deletes this path. Removing or updating it would expand the reviewed nine-path tooling delta/allowlist, which Local is explicitly forbidden to change. Tooling NUnit and V02–V05 are therefore `Blocked / NotRun`. Independent M08 was not commissioned; last M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`; R02 was not started.

### Validated source state

| Role | Branch | Exact observed HEAD | Result |
| --- | --- | --- | --- |
| Candidate handoff | `codex/assembly-shadow-r01b-h1` | `534b03eb49140eb7f9d9fbdb64217e113a317626` | `Pass` |
| Candidate source anchor | same branch | `1b1cc9fe192b88be2a20fad31ea030b1e30be669` | `Pass` in source target and pin |
| Candidate native | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` | `Pass`, clean |
| Shared package | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` | `Pass`, clean |
| Shared IL2CPP | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` | `Pass`, clean |
| Protected reproduction | `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` | `Pass`, unchanged and clean |
| Reproduction tooling | `codex/assembly-shadow-h1-count-repro-tooling` | `0c9c2508d94a097dff50028212a01695c8e29c60` | V00 `Pass`; Unity compile `Fail` |
| Reproduction native | `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` | `Pass`, unchanged and clean |
| Performance reference | `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` | `Pass`, unchanged and clean |

Pre-existing untracked historical `v7`–`v11` and all earlier checkpoints were preserved unchanged. No reset, clean, stash, protected branch movement, runtime pin change, or local allowlist expansion was performed.

### Validation results

| Step | Result | Empirical result |
| --- | --- | --- |
| V00 candidate authority | `Pass` | `SourceTargetVerifiedNotBuildAccepted`; handoff/source/pins and false gate flags exact. |
| V00 reproduction tooling authority | `Pass` | `BehaviorAndToolingSourcesVerifiedNotBuildAccepted`; behavior/protected/tooling ancestry, 11 tool files, 9 overrides, working bytes, pins, and false gate flags exact. |
| V01 H1 Python | `Pass` | 472/472 exact leaf inventory. |
| V01 Bee Primary | `Pass` | 294/294, zero nonpasses. |
| V01 candidate Unity | `Pass` | Fresh compile, zero errors; focused NUnit 4/4 and 10/10. |
| V01 reproduction-tooling Unity | `Fail` | CS0426: historical managed-source test expects removed nested `Capture` type. |
| V01 reproduction-tooling NUnit | `Blocked / NotRun` | Project cannot compile. |
| V02 candidate normal-cache proof | `Blocked / NotRun` | Handoff requires return on an additional tooling dependency; historical V02/V03 evidence remains historical. |
| V03 fresh six-build set | `Blocked / NotRun` | Reproduction tooling source state cannot compile, so no valid six-build set or tooling binding can be produced. |
| V04 runtime/count/startup/performance | `Blocked / NotRun` | No valid current six-build set. |
| V05 successor and independent M08 | `Blocked / NotRun` | Acceptance inputs incomplete; last independent M08 remains `FAIL`. |

The first candidate-preflight shell wrapper used the zsh-reserved variable `status` after the preflight process returned. That recording error is preserved as an unavailable exit-code attempt; the corrected fresh invocation exited 0 and is the accepted V00 observation.

Portable evidence is under [local-validation-20260916-534b03e](../../Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260916-534b03e/README.md). No product or validation-policy code was changed. The actionable nontrivial issue is at the top of [RETURN_TO_WEB.md](RETURN_TO_WEB.md).

---

## Historical run — 2026-09-16 handoff 9568ea3

### Exit

**Local Validation → Primary Implementation**

The candidate branch was explicitly pulled to requested handoff `9568ea386822b4e8e48ff73e793d4a2cd09092dc`. Candidate source anchor `5f561abdfbe020d1d480594a2130c5ec846c0e6a` and all protected pins match. V00 and V01 pass. V02 provides the first fresh real-Unity schema-3 proof: both required managed assemblies are uniquely bound to the fresh Player through `BeeCacheHitBoundToFreshPlayerInput`, each action's two-file recursive response closure is exact and unchanged, and `freshCompilerExecutionClaim=false`.

All four candidate V03 modes pass strict native compiler/PCH/store provenance, schema-3 managed provenance, exact fresh Player input binding, and restoration. The fresh reproduction ON/Debug Player then succeeds, but the protected reproduction checkout's project-local pre-domain `h1_native_capture.py` rejects its 446-action Apple graph with `Translation units disagree on effective diagnostic macros (link flags are not compile evidence)`. No compiler-provenance output or build receipt is published.

A diagnostic-only replay using the candidate source anchor's current tool passes on the exact failed reproduction request and graph, including Apple macro/PCH probes and independent retained-store verification. It explicitly reports `DiagnosticReplayVerifiedNotBuildAccepted` and cannot repair the failed build. The discrepancy is therefore a tooling-chain/version mismatch, not authority to accept the unreceipted Player locally.

Reproduction ON/Release, V04, and V05 are `Blocked / NotRun`. Independent whole-chain M08 was not commissioned. Human Review Gate is not ready, `humanGatePassed=false`, `mayEnterR02=false`, and R02 was not started.

### Validated source state

| Role | Branch | Exact observed HEAD | Result |
| --- | --- | --- | --- |
| Candidate handoff checkout | `codex/assembly-shadow-r01b-h1` | `9568ea386822b4e8e48ff73e793d4a2cd09092dc` | `Pass` |
| Candidate source anchor | same branch | `5f561abdfbe020d1d480594a2130c5ec846c0e6a` | `Pass` in source target and pin |
| Candidate native | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` | `Pass`, clean |
| Shared package | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` | `Pass`, clean |
| Shared IL2CPP | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` | `Pass`, clean |
| Reproduction demo | `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` | `Pass`, unchanged and clean |
| Reproduction native | `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` | `Pass`, unchanged and clean |
| Performance reference | `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` | `Pass`, unchanged and clean |

Pre-existing untracked historical `v7`–`v11` evidence was preserved and excluded. No reset, clean, stash, branch move, or protected-pin change was performed.

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
| V00 authoritative preflight | `Pass` | Exit 0; `SourceTargetVerifiedNotBuildAccepted`; requested checkout, source anchor, pins, and false gate flags. |
| V01 Bee Primary | `Pass` | Corrected fresh invocation 283/283. Initial pre-created-output failure is retained. |
| V01 H1 Python / focused owners | `Pass` | H1 inventory 461/461; managed cache 10/10; managed provenance 17/17; strict provenance 4/4; M02 owner 15/15. |
| V01 candidate Unity | `Pass` | Compile; focused NUnit 4/4 and 10/10; full demo 351/351; package 720/720. |
| V01 reproduction Unity | `Pass` for required scope | Compile and focused NUnit 4/4 and 10/10. |
| V02 pinned install/runtime | `Pass` | 955 source files, 957 installed files, demo source verified, mode `on`, receipt SHA-256 `8b6d04c1e54c57174bae04476814166ff78d52ab5d1af1d048695c4462087f68`. |
| V02 fresh candidate ON/Debug | `Pass` | Native strict verifier, schema-3 managed verifier, and exact restoration pass. Both required rows are cache hits bound to exact fresh Player inputs. |
| V02 action-local responses | `Pass` | Two recursive responses per selected action; `responseSources`/retained membership exact; all owned responses unchanged. This run observed zero audit-only response changes. |
| V02 native store | `Pass` for integrity | `StoreVerifiedNotAcceptance`; 451 objects, 318,212,421 logical bytes, 72,612,459 stored bytes. |
| V03 candidate ON/OFF × Debug/Release | `Pass` | Four modes pass strict native and schema-3 managed provenance; each mode has two unique cache-hit rows and exact restoration. |
| V03 reproduction ON/Debug | `Fail` | Player succeeds, then old project-local capture rejects the Apple macro split. No provenance/receipt. Restoration is exact. |
| V03 candidate-tool replay | `Pass` for diagnosis only | Exact request/graph passes current macro/PCH diagnostics and store verification; no fresh-build or receipt claim. |
| V03 reproduction ON/Release | `Blocked / NotRun` | Serial strict batch stops at the required ON/Debug failure. |
| V04 runtime/count/startup/performance | `Blocked / NotRun` | Required six-build provenance set is incomplete. |
| V05 successor and independent M08 | `Blocked / NotRun` | Acceptance inputs are incomplete; last independent M08 remains `FAIL`. |

The two mistaken runtime-verifier invocations used a duplicate operation argument. One raw failure is retained; the first log was overwritten before checkpointing and is recorded as `Unavailable`. The corrected verifier result is the only accepted runtime-install observation.

### Key evidence

V02 candidate ON/Debug uses build GUID `1d8b8152db7348839de41dbe0206aa2f`, input snapshot `498a47bdffd70f650b51bfd1057a51e6bb2be0e914ba8196dad67ed1c576c2f1`, and native SHA-256 `c5fcf8c9e78632a5d9a1df8319ce7a5cc346526c745823ab72df8ded27d901c0`. The normal Bee cache remained intact; neither cache cleaning nor `--reuse-proof` was used.

The failed reproduction ON/Debug build uses build GUID `44882bc8dac74f538be9e951991d790e`, input snapshot `7d1349c55854ce6f121eafef0312eb04da6698a7e245cc33b2ece52fa2654073`, native SHA-256 `4ad497816822932021d89879e5f5d7c7f490a4b0ae5fda4994498281a278fae5`, request SHA-256 `d0264e40f116445884696ebbd56564622722c2b20ba78835b7e5a741439095e1`, and selected graph SHA-256 `aaaedafc0c9d1a5e5410090d396d906ac1aced72b79965f3fe14d072ee22879d`. The candidate diagnostic replay proof is `a4425ebca605487b7c57fa851e6ac5f03f22d0e766da642934b4191b0cd5fc5d` and remains non-acceptance evidence.

Portable evidence is under [local-validation-20260916-9568ea3](../../Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260916-9568ea3/README.md). No product code or local policy change was made. The actionable issue is at the top of [RETURN_TO_WEB.md](RETURN_TO_WEB.md).

---


## Historical run — 2026-09-16 handoff 2ca4720

### Exit

**Local Validation → Primary Implementation**

The candidate branch was explicitly fast-forwarded to requested handoff `2ca4720508dc114e9c55756fcb2a068678dff90c`. Candidate source anchor `5f561abdfbe020d1d480594a2130c5ec846c0e6a` and every protected native/package/IL2CPP/reproduction/performance identity match the published handoff.

The authoritative V00 preflight fails immediately with `Blocked: Incomplete handoff sections`. The committed preflight requires nine literal, case-sensitive heading substrings. Published `WEB_TO_LOCAL.md` provides only `## Objective`, `## Failure evidence`, and `## Local correction boundary`; it lacks `## Source targets`, `## Implementation`, `## Local validation`, `## Alternatives`, `## Risks`, and `## Human review gate`.

The handoff requires V00 PASS before V01–V05 and forbids Local Validation from rewriting `WEB_TO_LOCAL.md`. V01–V05 are `Blocked / NotRun`. No Unity, Bee-cache, installation, Player, runtime, performance, successor, or M08 command was started for source anchor `5f561ab`. Human Review Gate is not ready, `humanGatePassed=false`, `mayEnterR02=false`, and R02 was not started.

### Validated source state

| Role | Branch | Exact observed HEAD | Result |
| --- | --- | --- | --- |
| Candidate handoff checkout | `codex/assembly-shadow-r01b-h1` | `2ca4720508dc114e9c55756fcb2a068678dff90c` | `Pass` |
| Candidate source/implementation anchor | same branch | `5f561abdfbe020d1d480594a2130c5ec846c0e6a` | `Pass` in source target and source pin |
| Candidate native | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` | `Pass`, clean |
| Shared package | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` | `Pass`, clean |
| Shared IL2CPP | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` | `Pass`, clean |
| Reproduction demo | `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` | `Pass`, unchanged |
| Reproduction native | `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` | `Pass`, unchanged |
| Performance reference | `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` | `Pass`, unchanged |

The candidate retained the pre-existing untracked historical `v7`–`v11` directories plus this new checkpoint. Protected worktrees remained clean and were not moved or reinstalled.

### Validation results

| Step | Result | Empirical result |
| --- | --- | --- |
| V00 repository/pin observation | `Pass` | Checkout, source anchor, all protected pins, tool versions, and dirty-state boundaries match. |
| V00 authoritative preflight | `Fail` | Exit 1; `Blocked: Incomplete handoff sections`; no output JSON created. |
| V01 affected regressions | `Blocked / NotRun` | Required V00 preflight did not pass. |
| V02 schema-3 real Bee proof | `Blocked / NotRun` | Required V00 preflight did not pass; normal Bee cache was untouched. |
| V03 fresh build set | `Blocked / NotRun` | Required V00 preflight did not pass. |
| V04 runtime/count/startup/performance | `Blocked / NotRun` | No accepted fresh build inputs. |
| V05 successor and independent M08 | `Blocked / NotRun` | Acceptance chain has no valid new inputs; M08 was not commissioned. |

Portable evidence is under [local-validation-20260916-2ca4720](../../Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260916-2ca4720/README.md). No bounded local fix was made because the authority document and executable handoff contract are Primary-owned.

---

## Historical run — 2026-09-15 handoff 3695905

### Exit

**Local Validation → Primary Implementation**

Fresh V00 and V01 pass. The prioritized candidate ON/Debug Player build completes and passes strict native compiler/PCH/domain/store verification. The required managed cache verifier then fails closed on `Library/Bee/artifacts/StandaloneOSX_CodeGen/Unity.Burst.CodeGen.rsp` before it can emit either `BeeCacheHitBoundToFreshPlayerInput` row.

The normal Bee cache was preserved and `--reuse-proof` was not used. Both required compiler actions are unique in the retained Player DAG. Their assembly-local response files, 201 dependencies per assembly, compiler outputs, reachable downstream DLLs, and exact fresh Player input path/hash/size bindings are unchanged. Seven unrelated graph-wide CodeGen response files legitimately gained the two diagnostic defines staged for the Player build. The implementation retains and checks all 92 DAG response files before selecting an assembly, so the unrelated changes reject both otherwise-complete candidate chains.

Response-file scope and managed acceptance semantics are Primary-owned. No local parser, allowlist, cache, limit, or provenance change was made. The remaining five builds and V04–V05 are `Blocked / NotRun`; independent whole-chain M08 was not commissioned. Human Review Gate is not ready, `humanGatePassed=false`, `mayEnterR02=false`, and R02 was not started.

### Validated source state

| Role | Branch | Exact observed HEAD | Result |
| --- | --- | --- | --- |
| Candidate handoff checkout | `codex/assembly-shadow-r01b-h1` | `3695905b1981a5cecbd444e27114c34cbc3bf255` | `Pass` |
| Candidate source/implementation anchor | same branch | `0387feb4344bbe95fd7db524d6e0bae759adc203` | `Pass` in source target and source pin |
| Candidate native | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` | `Pass`, clean |
| Shared package | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` | `Pass`, clean |
| Shared IL2CPP | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` | `Pass`, clean |
| Reproduction demo | `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` | `Pass`, unchanged |
| Reproduction native | `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` | `Pass`, unchanged |
| Performance reference | `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` | `Pass`, unchanged |

The candidate was explicitly pulled with `git pull --ff-only origin codex/assembly-shadow-r01b-h1`. Candidate retained the pre-existing untracked historical `v7`–`v11` directories in addition to this new checkpoint. Reproduction and performance-reference worktrees remained clean and were not repointed or reinstalled.

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
| V00 authoritative preflight | `Pass` | Exit 0; `SourceTargetVerifiedNotBuildAccepted`; checkout `3695905…`; code source `0387feb…`; native installation false; both gate flags false. |
| V01 Bee Primary | `Pass` | Fresh exact bounded suite 281/281. |
| V01 H1 Python | `Pass` | Fresh exact H1 inventory 459/459. Additional broad inventory: 955 passed / 1 skipped platform-path fixture; this is not Unity or Player acceptance. |
| V01 strict provenance / normal M02 owner / cache controls | `Pass` | 4/4, 15/15, and 8/8. |
| V01 candidate Unity | `Pass` | Fresh compile; focused NUnit 4/4 and 10/10; full demo Editor regression 351/351; package Editor regression 720/720. |
| V01 reproduction Unity | `CompletedWithNonPass` | Fresh compile and focused NUnit 14/14 passed. Additional full demo sweep completed 330/342 with the same 12 historical missing managed-source/baseline/linked-input failures. |
| V02 real Bee cache proof | `Fail` | One unchanged Player DAG, two unique required compiler actions, exact fresh Player inputs, and unchanged assembly-local chains exist. Seven unrelated graph-wide CodeGen responses changed, so no cache-hit acceptance row was emitted. |
| V03 pinned install / runtime verification | `Pass` | Install passed; 955 source files, 957 installed files, demo source verified, mode `on`, receipt SHA-256 `5d229b965e1b3d67212b5c029555c4d94327318179cb735adcdee4df957271f7`. |
| V03 candidate ON/Debug Player/native evidence | `Pass` before managed verification | Player build, strict native verifier, independent store verifier, Apple domains/PCH/probes, and exact restoration pass. |
| V03 managed-source provenance | `Fail` | `Cached managed response changed or was unavailable: .../StandaloneOSX_CodeGen/Unity.Burst.CodeGen.rsp`. |
| V03 remaining five builds | `Blocked / NotRun` | A valid candidate ON/Debug smoke receipt is required. |
| V04 runtime/count/startup/performance | `Blocked / NotRun` | No six-build fresh provenance set exists. |
| V05 successor and independent M08 | `Blocked / NotRun` | Successor inputs are incomplete; M08 was not commissioned. |

### Real cache and fresh build identity

- Cached Player DAG: 9,281,264 bytes, SHA-256 `46997e81b065cdd57c5d93913e076192fdc79e809d6757e9045e1bafef5080af`.
- Cache observations: 302 total, 295 `Unchanged`, 7 `Changed`.
- Bootstrap cached action SHA-256: `147ff4fdd7fb75e65bf9ac1e541096a0a7a72b82bfe1e32ddafab91101cef6a7`; fresh Player input SHA-256 `863743cc1aba2835c5491e01277d9a054e9cf590923059627a4c42667aaa8c39`.
- Diagnostics cached action SHA-256: `67df1baf137e19ff95e6d36cf579e4065b5c57281ec80b1ed2ee17734ca560cc`; fresh Player input SHA-256 `d8c6a81f7c0f489d8de76c60454e8ebd06c5448d60c9ee67e7940c60cc10dd04`.
- Build GUID: `f6aa5298e2284385a9d458bb58f08e68`; input snapshot SHA-256 `ea5f83c1c1de80ce83bc9d121e4138843de8fb6234681e11a38c090d1ed55713`.
- Native Bee graph SHA-256: `d0e34c181592adc10abedf1139104b951ac75bf2e356f352e04888edc297cf57`.
- `GameAssembly.dylib` SHA-256: `117e733567a7b6d52742c93281a3842773af2820301dee602264887fdf4b2e85`.
- Native build receipt SHA-256: `ab2cf18d908b302e9de775c35b06bbd824df260dc5d3725fb6d6336e887cd0ae`.
- Compiler provenance SHA-256: `47bed29c77133de6f001b984a65c45371bac75ffc5ab5484bb9dbf72339a2b18`.
- Managed capture SHA-256: `a081924a5a08a6d13666e26df43144074db240d9c3940fd5446978faa3d4502e`.
- Store verification: `StoreVerifiedNotAcceptance`; 451 observations/content/blobs, 318,212,421 logical bytes, 72,612,459 stored bytes; inventory SHA-256 `a66bc38bdf402c5130b95b42ab6b535716236dabbceb9b369da0d9cbf28956c7`.
- Restoration: `ExactRestorationVerified`.

Portable evidence is under [local-validation-20260915-3695905](../../Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260915-3695905/README.md). Full unpacked roots remain at `/Users/ah/GitHub/hybridclr/h1-local-validation-20260915-3695905/v03/smoke` and `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/H1CountBuild-27d8ff137d4b40258d6b42dbd83dd99a`.

---

## Historical run — 2026-09-15 handoff 8f5bcaa

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
